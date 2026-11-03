"""Tests for the table parser, the schemas, and the source files they describe."""

import datetime as dt
import re
from pathlib import Path
from typing import Any

import pytest
import yaml

from par import tables
from par.zenodo import metadata


def spec(columns: list[Any], **table: object) -> dict[str, Any]:
    """Return a one-table source spec."""
    return {
        "source": "X",
        "tables": [{"name": "x", "rows": [1, 2], "keys": ["a"], "columns": columns, **table}],
    }


def parse(columns: list[Any], cells: list[list[str]], **table: object) -> tables.Table:
    """Parse rows with a one-table spec."""
    source = spec(columns, **table)
    return tables.parse_table(source, source["tables"][0], cells, {})


def test_error_cells_become_null_and_are_logged() -> None:
    out = parse([[0, "a", "integer", "A"]], [["1"], ["#VALUE!"]], keys=["source_row"])
    assert out.arrow["a"].to_pylist() == [1, None]
    assert out.error_cells == [{"table": "x", "source_row": 2, "column": "a", "value": "#VALUE!"}]


@pytest.mark.parametrize("placeholder", ["", "--", "?", "??", ".."])
def test_placeholders_are_null_in_text_columns(placeholder: str) -> None:
    out = parse([[0, "a", "string", "A"]], [["x"], [placeholder]], keys=["source_row"])
    assert out.arrow["a"].to_pylist() == ["x", None]


def test_table_missing_codes_stay_as_text_in_text_columns() -> None:
    out = parse(
        [[0, "a", "string", "A"], [1, "b", "number", "B"]],
        [["N/A", "1"], ["x", "N/A"]],
        keys=["source_row"],
        missing=["N/A"],
    )
    assert out.arrow["a"].to_pylist() == ["N/A", "x"]
    assert out.arrow["b"].to_pylist() == [1, None]


def test_all_null_number_column_stays_number() -> None:
    out = parse([[0, "a", "number", "A"]], [[""], ["--"]], keys=["source_row"])
    assert [c["type"] for c in out.columns] == ["number"]


def test_unexpected_value_stops_the_build() -> None:
    with pytest.raises(ValueError, match="row 2 column a"):
        parse([[0, "a", "number", "A"]], [["1"], ["oops"]])


def test_integer_column_rejects_fractions() -> None:
    with pytest.raises(ValueError, match="non-integer"):
        parse([[0, "a", "integer", "A"]], [["1"], ["0.5"]])


def test_ditto_copies_the_row_above() -> None:
    column = {"col": 0, "name": "d", "type": "date", "description": "D", "ditto": '"-"-"'}
    out = parse([column], [["1807-6-10"], ['"-"-"']], keys=["source_row"])
    assert out.arrow["d"].to_pylist() == [dt.date(1807, 6, 10)] * 2


def test_year_offset_moves_civil_war_dates() -> None:
    out = parse(
        [[0, "d", "date", "D"]],
        [["07/01/1961"], ["03/01/1965"]],
        keys=["source_row"],
        date_year_offset=-100,
    )
    assert out.arrow["d"].to_pylist() == [dt.date(1861, 7, 1), dt.date(1865, 3, 1)]


def test_summary_rows_reconcile_and_are_removed() -> None:
    out = parse(
        [[0, "a", "integer", "A"], [1, "b", "string", "B"]],
        [["2", "x"], ["2", "TOTAL"], ["3", "y"], ["9", "TOTAL"]],
        keys=["source_row"],
        rows=[1, 4],
        summary_rows={"match": {1: ["TOTAL"]}, "columns": {0: "a"}},
    )
    assert out.arrow["a"].to_pylist() == [2, 3]
    assert [(c["reported"], c["computed"]) for c in out.controls] == [(2, 2), (9, 3)]


def test_correction_must_match_the_source() -> None:
    source = spec([[0, "a", "integer", "A"]])
    fixes = {("x", 1, "a"): {"old": "5", "new": "6"}}
    with pytest.raises(ValueError, match="correction expects"):
        tables.parse_table(source, source["tables"][0], [["1"], ["2"]], fixes)


def test_macro_keystrokes_are_removed_from_text() -> None:
    cells = ["Address: Moscow.", "", "{END}{RIGHT 2}", "{RIGHT 4}~{DOWN}."]
    assert tables.clean_text(cells) == "Address: Moscow."


def test_number_column_with_only_whole_values_becomes_integer() -> None:
    out = parse(
        [[0, "a", "number", "A"], [1, "b", "number", "B"]],
        [["2", "0.5"], ["3", "1"]],
        keys=["source_row"],
    )
    assert out.arrow["a"].to_pylist() == [2, 3]
    assert [c["type"] for c in out.columns] == ["integer", "number"]


def test_fixed_width_split() -> None:
    columns = [{"width": 2}, {"width": 3}]
    assert tables.split_fixed("ab123", columns) == ["ab", "123"]


@pytest.mark.parametrize("path", sorted(tables.SCHEMA_DIR.glob("*.yaml")), ids=lambda p: p.stem)
def test_schema_column_names_are_unique_snake_case(path: Path) -> None:
    for table in yaml.safe_load(path.read_text())["tables"]:
        names = [
            tables.normalize_column(c, "width" in str(c))["name"] if isinstance(c, dict) else c[1]
            for c in table["columns"]
        ]
        assert len(names) == len(set(names)), table["name"]
        assert all(re.fullmatch(r"[a-z][a-z0-9_]*", name) for name in names), table["name"]
        assert "source_row" not in names


# Row counts from the diskette README, except where it miscounts: COMP tables lose total rows, and
# INCHON has 24 days (0 to 23), ORALFORE 361 rows including one unnumbered row, not 23 and 360.
EXPECTED_ROWS = {
    "ade": 393, "berndt": 78, "bob18": 18, "bodaship": 120, "bwshall": 1087, "cec": 81,
    "comp6ad": 508, "comp7ad": 934, "crete": 14, "dodge": 261, "inchon": 24, "iwojima": 37,
    "kelley_korea": 315, "kelley_vietnam": 138, "krivo": 180, "livrmore": 63, "mottelay": 120,
    "oralfore": 361, "parmisc": 209, "pogogoro": 9, "reisterk_division": 43,
    "reisterk_regiment": 52, "rmc": 250, "sp128": 92, "sp190": 83, "voevodsk_vietnam": 24,
    "voevodsk_korea": 16, "voevodsk_wwii": 8, "voevodsk_wwi_us": 9, "voevodsk_wwi_mixed": 22,
    "voevodsk_civil_war": 19, "westwall": 12,
}  # fmt: skip


def spreadsheet_tables() -> dict[str, tables.Table]:
    """Parse every table whose source is in git."""
    corrections = tables.load_corrections()
    out = {}
    for path in sorted(tables.SCHEMA_DIR.glob("*.yaml")):
        source = yaml.safe_load(path.read_text())
        if "fixed_width" in source:
            continue
        rows = tables.read_rows(source)
        for table in source["tables"]:
            parsed = tables.parse_table(source, table, rows, corrections)
            tables.check_keys(parsed)
            out[parsed.name] = parsed
    return out


def test_row_counts_match_the_documentation() -> None:
    tables = spreadsheet_tables()
    for name, expected in EXPECTED_ROWS.items():
        assert tables[name].arrow.num_rows == expected, name


def test_control_totals_reconcile() -> None:
    bad = [
        control
        for table in spreadsheet_tables().values()
        for control in table.controls
        if abs(control["reported"] - control["computed"]) > 0.51
    ]
    assert bad == []


def test_civil_war_dates_are_in_the_civil_war() -> None:
    dates = spreadsheet_tables()["voevodsk_civil_war"].arrow["date"].to_pylist()
    assert min(dates).year == 1861
    assert max(dates).year == 1865


def test_zenodo_metadata_has_required_fields() -> None:
    record = metadata(dt.date(2026, 1, 2))
    assert record["publication_date"] == "2026-01-02"
    for key in ("title", "upload_type", "description", "creators"):
        assert record[key]
