"""Turn each source's citation block into one row of structured metadata."""

import datetime as dt
import re
from typing import Any

import pyarrow as pa
import yaml

from par.tables import ARROW_TYPES, SCHEMA_DIR, Table, read_rows, text_block

# Every label the citation blocks use. A line starting with anything else continues the field above,
# so a wrapped title such as "Combat: Part II." stays in the title.
LABELS = {
    "dataset": "dataset",
    "data from": "title",
    "data from (title)": "title",
    "author": "author",
    "organization": "organization",
    "address": "address",
    "publication date": "publication_date",
    "classification": "classification",
    "source available from": "available_from",
    "sources available from": "available_from",
    "prepared by": "prepared_by",
    "spreadsheet prepared by": "prepared_by",
    "last revised": "last_revised",
    "spreadsheet last revised": "last_revised",
    "note": "note",
}
# A final period in these fields can belong to an abbreviation, such as "Robert L." or "Inc."
ABBREVIATED_FIELDS = {"author", "organization"}
ABBREVIATION_LENGTH = 3
COLUMNS: list[dict[str, Any]] = [
    {"name": "source", "type": "string", "description": "Source file name, as in `source_row`"},
    {"name": "tables", "type": "string", "description": "Tables from this source, comma-separated"},
    {"name": "dataset", "type": "string", "description": "Dataset name in the citation"},
    {"name": "title", "type": "string", "description": "Title of the original publication"},
    {"name": "author", "type": "string", "description": "Author of the original publication"},
    {"name": "organization", "type": "string", "description": "Publisher or organization"},
    {"name": "address", "type": "string", "description": "Address of the organization"},
    {"name": "publication_date", "type": "string", "description": "Publication date, as written"},
    {"name": "publication_year", "type": "integer", "description": "First year in the date"},
    {"name": "classification", "type": "string", "description": "Classification, as written"},
    {"name": "available_from", "type": "string", "description": "Where the source can be found"},
    {"name": "prepared_by", "type": "string", "description": "Who prepared the spreadsheet"},
    {
        "name": "last_revised",
        "type": "date",
        "description": "Date the sheet was last revised",
    },
    {"name": "note", "type": "string", "description": "Other note in the citation"},
    {
        "name": "metadata_from",
        "type": "string",
        "description": "sheet if parsed from the diskette file, schema if entered by hand",
    },
]


def clean_field(field: str, value: str) -> str | None:
    """Collapse a field's whitespace and drop a closing period that isn't an abbreviation's."""
    text = " ".join(value.split())
    if text.endswith(".") and not (
        field in ABBREVIATED_FIELDS and len(text.split()[-1]) - 1 <= ABBREVIATION_LENGTH
    ):
        text = text[:-1]
    return text or None


def parse_citation(text: str) -> dict[str, str | None]:
    """Split a citation block into fields, raising ValueError if it doesn't start with a label."""
    fields: dict[str, list[str]] = {}
    current = None
    for line in text.splitlines():
        label, colon, rest = line.partition(":")
        field = LABELS.get(label.strip().lower()) if colon else None
        if field is not None:
            current = field
            fields[current] = [rest]
        elif current is None:
            raise ValueError(f"citation doesn't start with a label: {line!r}")
        else:
            fields[current].append(line)
    return {field: clean_field(field, " ".join(parts)) for field, parts in fields.items()}


def parse_revision_date(value: str | None) -> dt.date | None:
    """Read a revision date such as `30 October 1993`."""
    return None if value is None else dt.datetime.strptime(value, "%d %B %Y").date()


def parse_year(value: str | None) -> int | None:
    """Return the first year in a publication date."""
    match = re.search(r"\b\d{4}\b", value or "")
    return int(match[0]) if match else None


def source_fields(spec: dict[str, Any]) -> dict[str, Any]:
    """Return one source's metadata. A schema's `metadata` adds to or replaces the citation's."""
    if "citation_rows" in spec:
        fields = parse_citation(text_block(read_rows(spec), spec["citation_rows"]))
    elif "metadata" in spec:  # AHART and LMI have prose citations, with nothing to parse.
        fields = {}
    else:
        fields = parse_citation(spec["citation"])
    fields |= spec.get("metadata", {})
    return fields | {
        "source": spec["source"],
        "tables": ", ".join(table["name"] for table in spec["tables"]),
        "dataset": fields.get("dataset", spec["dataset"]),
        "publication_year": parse_year(fields.get("publication_date")),
        "last_revised": parse_revision_date(fields.get("last_revised")),
        "metadata_from": "sheet" if "citation_rows" in spec else "schema",
    }


def load_sources() -> Table:
    """Build the `sources` table, with one row per source file."""
    specs = (yaml.safe_load(p.read_text("utf-8")) for p in sorted(SCHEMA_DIR.glob("*.yaml")))
    rows = [source_fields(spec) for spec in specs]
    arrow = pa.table(
        {
            c["name"]: pa.array([row.get(c["name"]) for row in rows], ARROW_TYPES[c["type"]])
            for c in COLUMNS
        }
    )
    spec = {
        "name": "sources",
        "title": "Source of each table: the citation in its diskette file, as fields",
        "keys": ["source"],
    }
    return Table("sources", "diskette", spec, COLUMNS, arrow, citation="", notes="")
