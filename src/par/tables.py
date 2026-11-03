"""Turn the diskette's spreadsheet exports and fixed-width files into typed tables.

Each file in `schemas/` says where a table's rows are in its source and what each column means.
Parsing is strict: a value that doesn't fit its column type stops the build unless the schema lists
it as missing. Spreadsheet error strings become null and are logged, so nothing is dropped silently.
"""

import csv
import datetime as dt
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pyarrow as pa
import yaml

SCHEMA_DIR = Path(__file__).parent / "schemas"
EXPORT_DIR = Path("data/manual/exports")
RAW_DIR = Path("data/raw/dtic-adm000368")
CORRECTIONS = Path("data/manual/corrections.csv")

ERROR_TOKENS = {"#VALUE!", "#N/A", "#DIV/0!", "#REF!", "#NAME?", "Err:511", "Err:522"}
# Placeholders for an unknown or empty value, null in every column. Other codes, such as CEC's N/A
# or ORALFORE's NR, keep their documented meaning in coded columns; see each schema's `missing`.
PLACEHOLDERS = {"", "--", "?", "??", ".."}
ARROW_TYPES = {
    "integer": pa.int64(),
    "number": pa.float64(),
    "string": pa.string(),
    "date": pa.date32(),
    "time": pa.time32("s"),
}
DATE_FORMATS = ("%m/%d/%Y", "%Y-%m-%d")


@dataclass
class Table:
    """A parsed table with its schema, plus what the parser found along the way."""

    name: str
    source: str
    spec: dict[str, Any]
    columns: list[dict[str, Any]]
    arrow: pa.Table
    citation: str
    notes: str
    error_cells: list[dict[str, Any]] = field(default_factory=list)
    controls: list[dict[str, Any]] = field(default_factory=list)


def normalize_column(raw: list[Any] | dict[str, Any], fixed: bool) -> dict[str, Any]:
    """Expand a `[position, name, type, description]` shorthand into a column dict."""
    if isinstance(raw, dict):
        return raw
    position, name, kind, description = raw
    return {
        "width" if fixed else "col": position,
        "name": name,
        "type": kind,
        "description": description,
    }


def parse_date(value: str, column: dict[str, Any]) -> dt.date:
    """Parse a date using the column's format options, or the sheet's usual formats."""
    if "day_of" in column:
        return dt.date.fromisoformat(f"{column['day_of']}-{int(value):02d}")
    if "year_by_month" in column:
        parsed = dt.datetime.strptime(f"{value}2000", column["format"] + "%Y")
        return parsed.replace(year=column["year_by_month"][value[:3]]).date()
    if "format" in column:
        return dt.datetime.strptime(value, column["format"]).date()
    for fmt in DATE_FORMATS:
        try:
            return dt.datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    match = re.fullmatch(r"(\d{3,4})-(\d{1,2})-(\d{1,2})", value)
    if match:
        return dt.date(*map(int, match.groups()))
    raise ValueError(f"unrecognized date {value!r}")


def shift_year(value: dt.date, years: int) -> dt.date:
    """Shift a date by whole years."""
    return value.replace(year=value.year + years)


def parse_value(value: str, column: dict[str, Any], offset: int) -> Any:
    """Convert a non-missing cell to the column's type, raising ValueError if it doesn't fit."""
    kind = column["type"]
    if kind == "string":
        return value
    if kind == "integer":
        number = float(value)
        if number != int(number):
            raise ValueError(f"non-integer {value!r}")
        return int(number)
    if kind == "number":
        return float(value)
    if kind == "date":
        parsed = parse_date(value, column)
        return shift_year(parsed, offset) if offset else parsed
    if kind == "time":
        return dt.datetime.strptime(value, "%I:%M:%S %p").time()
    raise ValueError(f"unknown column type {kind}")


def load_corrections(path: Path = CORRECTIONS) -> dict[tuple[str, int, str], dict[str, str]]:
    """Read cell corrections, keyed by table, source row, and column name."""
    if not path.exists():
        return {}
    with path.open(newline="", encoding="utf-8") as f:
        return {(r["table"], int(r["source_row"]), r["column"]): r for r in csv.DictReader(f)}


def clean_text(cells: list[str]) -> str:
    """Join a sheet row into a line of text, dropping cells of Quattro Pro macro keystrokes."""
    parts = [cell.strip() for cell in cells if not cell.strip().startswith("{")]
    return " ".join(part for part in parts if part)


def read_rows(spec: dict[str, Any]) -> list[list[str]]:
    """Read a source's rows as text cells, one row per record."""
    if "fixed_width" in spec:
        lines: list[str] = []
        for name in spec["fixed_width"]["files"]:
            text = (RAW_DIR / name).read_bytes().decode("ascii").replace("\x1a", "")
            lines.extend(text.splitlines())
        return [[line] for line in lines]
    with (EXPORT_DIR / spec["export"]).open(newline="", encoding="latin-1") as f:
        return [list(map(str, row)) for row in csv.reader(f)]


def text_block(rows: list[list[str]], span: list[int] | None) -> str:
    """Return a 1-based inclusive range of rows as lines of text."""
    if span is None:
        return ""
    lines = (clean_text(row) for row in rows[span[0] - 1 : span[1]])
    return "\n".join(line for line in lines if line)


def split_fixed(line: str, columns: list[dict[str, Any]]) -> list[str]:
    """Cut a fixed-width record into its fields."""
    cells: list[str] = []
    start = 0
    for column in columns:
        cells.append(line[start : start + column["width"]])
        start += column["width"]
    return cells


def is_summary(cells: list[str], match: dict[int, list[str]]) -> bool:
    """Return whether a row is a total row according to the schema's `summary_rows.match`."""
    return any(cells[col].strip() in values for col, values in match.items())


def number_or_zero(cell: str) -> float:
    """Read a total-row or detail cell for reconciliation, treating non-numbers as zero."""
    try:
        return float(cell)
    except ValueError:
        return 0.0


def settle_type(column: dict[str, Any], values: list[Any]) -> dict[str, Any]:
    """Make a `number` column an integer when it has values and all of them are whole."""
    known = [v for v in values if v is not None]
    if column["type"] == "number" and known and all(float(v).is_integer() for v in known):
        values[:] = [None if v is None else int(v) for v in values]
        return column | {"type": "integer"}
    return column


def convert_cell(
    cell: str, column: dict[str, Any], missing: set[str], offset: int, previous: list[Any]
) -> Any:
    """Convert one cell, returning None for a missing value and the row above for a ditto mark."""
    if cell == column.get("ditto"):
        return previous[-1]
    if cell in PLACEHOLDERS or (
        column["type"] != "string" and (cell in missing or cell in column.get("missing", []))
    ):
        return None
    return parse_value(cell, column, offset)


def parse_table(
    spec: dict[str, Any],
    table: dict[str, Any],
    rows: list[list[str]],
    corrections: dict[tuple[str, int, str], dict[str, str]],
) -> Table:
    """Parse one table from its source rows."""
    fixed = "fixed_width" in spec
    columns = [normalize_column(c, fixed) for c in table["columns"]]
    first, last = table.get("rows", [1, len(rows)])
    missing = set(table.get("missing", []))
    offset = table.get("date_year_offset", 0)
    summary = table.get("summary_rows")
    data: dict[str, list[Any]] = {"source_row": []} | {c["name"]: [] for c in columns}
    errors: list[dict[str, Any]] = []
    controls: list[dict[str, Any]] = []
    segment = dict.fromkeys((summary or {}).get("columns", {}), 0.0)

    for row_no in range(first, last + 1):
        raw = rows[row_no - 1]
        cells = split_fixed(raw[0], columns) if fixed else raw
        if summary and is_summary(cells, summary["match"]):
            for col, name in summary["columns"].items():
                controls.append(
                    {
                        "table": table["name"],
                        "source_row": row_no,
                        "column": name,
                        "reported": number_or_zero(cells[col]),
                        "computed": segment[col],
                    }
                )
            segment = dict.fromkeys(segment, 0.0)
            continue
        if summary:
            for col in segment:
                segment[col] += number_or_zero(cells[col])
        data["source_row"].append(row_no)
        for index, column in enumerate(columns):
            name = column["name"]
            cell = (cells[index] if fixed else cells[column["col"]]).strip()
            fix = corrections.get((table["name"], row_no, name))
            if fix is not None:
                if cell != fix["old"]:
                    raise ValueError(
                        f"{table['name']} row {row_no} {name}: correction expects "
                        f"{fix['old']!r}, found {cell!r}"
                    )
                cell = fix["new"]
            if cell in ERROR_TOKENS or cell in column.get("error", []):
                errors.append(
                    {"table": table["name"], "source_row": row_no, "column": name, "value": cell}
                )
                data[name].append(None)
                continue
            try:
                data[name].append(convert_cell(cell, column, missing, offset, data[name]))
            except ValueError as error:
                raise ValueError(f"{table['name']} row {row_no} column {name}: {error}") from error

    columns = [settle_type(column, data[column["name"]]) for column in columns]
    arrow = pa.table(
        {
            "source_row": pa.array(data["source_row"], pa.int64()),
            **{c["name"]: pa.array(data[c["name"]], ARROW_TYPES[c["type"]]) for c in columns},
        }
    )
    for control in table.get("controls", []):
        cells = rows[control["row"] - 1]
        for col, name in control["columns"].items():
            values = arrow[name].to_pylist()
            controls.append(
                {
                    "table": table["name"],
                    "source_row": control["row"],
                    "column": name,
                    "reported": number_or_zero(cells[col]),
                    "computed": sum(v for v in values if v is not None),
                }
            )
    notes = "\n".join(
        filter(
            None,
            [
                spec.get("notes", "").strip(),
                text_block(rows, spec.get("notes_rows")),
                text_block(rows, spec.get("extra_notes_rows")),
            ],
        )
    )
    citation = spec.get("citation", "").strip() or text_block(rows, spec.get("citation_rows"))
    return Table(
        name=table["name"],
        source=spec["source"],
        spec=table,
        columns=columns,
        arrow=arrow,
        citation=citation,
        notes=notes,
        error_cells=errors,
        controls=controls,
    )


def check_keys(table: Table) -> None:
    """Fail unless the table's key columns are unique and non-missing (baseline rule P5)."""
    keys = table.spec.get("keys", ["source_row"])
    seen = set()
    for values in zip(*(table.arrow[k].to_pylist() for k in keys), strict=True):
        if None in values or values in seen:
            raise ValueError(f"{table.name}: bad key {values} for {keys}")
        seen.add(values)


def load_tables(schema_dir: Path = SCHEMA_DIR) -> list[Table]:
    """Parse every table in every schema file."""
    corrections = load_corrections()
    tables = []
    for path in sorted(schema_dir.glob("*.yaml")):
        spec = yaml.safe_load(path.read_text(encoding="utf-8"))
        rows = read_rows(spec)
        for table_spec in spec["tables"]:
            table = parse_table(spec, table_spec, rows, corrections)
            check_keys(table)
            tables.append(table)
    return tables
