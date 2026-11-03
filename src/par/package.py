"""Build the Frictionless data package and the zip files archived on Zenodo."""

import json
import shutil
import zipfile
from pathlib import Path
from typing import Any

import duckdb
from frictionless import Package

from par.ocr import MARKDOWN_DIR, PDFS
from par.tables import RAW_DIR, Table

PARQUET_DIR = Path("data/processed/parquet")
PACKAGE_DIR = Path("data/processed/datapackage")
PACKAGE_ZIP = Path("data/processed/par-datapackage.zip")
DISKETTE_ZIP = Path("data/processed/par-diskette.zip")
VERSION = "2.0.0"
# Keep zip files byte-identical between builds, so downstream DVC stages don't rerun.
FIXED_TIME = (1994, 5, 31, 0, 0, 0)

SOURCES = [
    {
        "title": "PAR Datadisk (Personnel Attrition Rates in Historical Land Combat Operations)"
        " (Revised) Version 2.1 (Computer Diskette), May 31, 1994, DTIC ADM000368",
    },
    {
        "title": "Helmbold, Robert L. Personnel Attrition Rates in Historical Land Combat"
        " Operations: A Catalog of Attrition and Casualty Data Bases on Diskettes Usable with"
        " Personal Computers. US Army Concepts Analysis Agency, CAA-RP-93-4, September 1993,"
        " DTIC ADA279069",
    },
]
DESCRIPTION = (
    "Tidy tables from the Personnel Attrition Rates (PAR) data diskettes compiled by Robert L."
    " Helmbold at the US Army Concepts Analysis Agency: personnel strengths, casualties, and"
    " related data for historical battles and operations. Each table lists its original source"
    " in its description; the catalog (ADA279069) describes each source and its limitations."
)


def resource(table: Table) -> dict[str, Any]:
    """Return a data package resource for one table."""
    description = "\n\n".join(
        filter(None, [table.spec.get("description", ""), table.citation, table.notes])
    )
    fields = [
        {"name": c["name"], "type": c["type"], "description": c["description"]}
        for c in table.columns
    ]
    if "source_row" in table.arrow.column_names:
        fields.insert(
            0,
            {
                "name": "source_row",
                "type": "integer",
                "description": f"Row in the source file ({table.source})",
            },
        )
    return {
        "name": table.name,
        "title": table.spec["title"],
        "description": description,
        "path": f"data/{table.name}.csv",
        "format": "csv",
        "mediatype": "text/csv",
        "encoding": "utf-8",
        "schema": {
            "fields": fields,
            "primaryKey": table.spec.get("keys", ["source_row"]),
        },
    }


def add_to_zip(archive: zipfile.ZipFile, path: Path, name: str) -> None:
    """Add a file to a zip with a fixed timestamp."""
    info = zipfile.ZipInfo(name, date_time=FIXED_TIME)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    archive.writestr(info, path.read_bytes())


def zip_dir(root: Path, out: Path) -> None:
    """Zip a directory, with sorted entries so the result is reproducible."""
    with zipfile.ZipFile(out, "w") as archive:
        for path in sorted(p for p in root.rglob("*") if p.is_file()):
            add_to_zip(archive, path, path.relative_to(root).as_posix())


def build_package(tables: list[Table]) -> None:
    """Write the data package directory, validate it, and zip it with the raw diskette."""
    shutil.rmtree(PACKAGE_DIR, ignore_errors=True)
    (PACKAGE_DIR / "data").mkdir(parents=True)
    (PACKAGE_DIR / "docs").mkdir()
    for table in tables:
        order = "source" if table.name == "sources" else "source_row"
        duckdb.sql(
            f"copy (select * from '{PARQUET_DIR / table.name}.parquet' order by {order}) "
            f"to '{PACKAGE_DIR / 'data' / table.name}.csv' (header)"
        )
    resources = sorted((resource(table) for table in tables), key=lambda r: r["name"])
    for pdf in PDFS:
        for doc in (pdf, MARKDOWN_DIR / f"{pdf.stem}.md"):
            shutil.copy(doc, PACKAGE_DIR / "docs" / doc.name)
    descriptor = {
        "name": "personnel-attrition-rates",
        "title": "Personnel Attrition Rates in Historical Land Combat Operations",
        "version": VERSION,
        "description": DESCRIPTION,
        "licenses": [
            {
                "name": "PDDL-1.0",
                "title": "Open Data Commons Public Domain Dedication and License 1.0",
                "path": "https://opendatacommons.org/licenses/pddl/1-0/",
            }
        ],
        "sources": SOURCES,
        "contributors": [
            {"title": "Jeffrey B. Arnold", "role": "wrangler"},
            {"title": "Robert L. Helmbold", "role": "author"},
        ],
        "resources": resources,
    }
    with (PACKAGE_DIR / "datapackage.json").open("w", encoding="utf-8") as f:
        json.dump(descriptor, f, indent=2)
        f.write("\n")
    report = Package(PACKAGE_DIR / "datapackage.json").validate()
    if not report.valid:
        raise ValueError(report.to_summary())
    zip_dir(PACKAGE_DIR, PACKAGE_ZIP)
    zip_dir(RAW_DIR, DISKETTE_ZIP)
