"""Write the parsed tables, and what the parser and checks found, as parquet."""

from pathlib import Path

import duckdb
import pyarrow as pa
import pyarrow.parquet as pq

from par.tables import Table, load_tables

PARQUET_DIR = Path("data/processed/parquet")
INTERIM_DIR = Path("data/interim")

ERROR_SCHEMA = pa.schema(
    [
        ("table", pa.string()),
        ("source_row", pa.int64()),
        ("column", pa.string()),
        ("value", pa.string()),
    ]
)
CONTROL_SCHEMA = pa.schema(
    [
        ("table", pa.string()),
        ("source_row", pa.int64()),
        ("column", pa.string()),
        ("reported", pa.float64()),
        ("computed", pa.float64()),
    ]
)
CHECK_SCHEMA = pa.schema(
    [
        ("table", pa.string()),
        ("check", pa.string()),
        ("expression", pa.string()),
        ("source_row", pa.int64()),
    ]
)


def write_parquet(table: pa.Table, path: Path) -> None:
    """Write a parquet file with zstd compression (baseline rule F3)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(table, path, compression="zstd")


def failing_rows(table: Table) -> list[dict[str, object]]:
    """Run a table's SQL checks. A row fails when an expression is false, not when it is null."""
    failures: list[dict[str, object]] = []
    con = duckdb.connect()
    con.register("t", table.arrow)
    for check in table.spec.get("checks", []):
        query = f"select source_row from t where ({check['expr']}) = false order by 1"
        failures.extend(
            {
                "table": table.name,
                "check": check["name"],
                "expression": check["expr"],
                "source_row": row[0],
            }
            for row in con.sql(query).fetchall()
        )
    con.close()
    return failures


def build_tables() -> None:
    """Parse all tables and write them with their issue logs."""
    tables = load_tables()
    errors: list[dict[str, object]] = []
    controls: list[dict[str, object]] = []
    checks: list[dict[str, object]] = []
    for table in tables:
        write_parquet(table.arrow, PARQUET_DIR / f"{table.name}.parquet")
        errors.extend(table.error_cells)
        controls.extend(table.controls)
        checks.extend(failing_rows(table))
    write_parquet(pa.Table.from_pylist(errors, ERROR_SCHEMA), INTERIM_DIR / "error_cells.parquet")
    write_parquet(
        pa.Table.from_pylist(controls, CONTROL_SCHEMA), INTERIM_DIR / "control_totals.parquet"
    )
    write_parquet(
        pa.Table.from_pylist(checks, CHECK_SCHEMA), INTERIM_DIR / "check_failures.parquet"
    )


def write_validation(out: Path = Path("results/validation")) -> None:
    """Write the issue logs as small CSV tables for git."""
    out.mkdir(parents=True, exist_ok=True)
    interim = INTERIM_DIR.as_posix()
    queries = {
        "error_cells": f"select * from '{interim}/error_cells.parquet' order by 1, 2, 3",
        "control_total_mismatches": f"""
            select *, round(reported - computed, 3) as difference
            from '{interim}/control_totals.parquet'
            where abs(reported - computed) > 0.51 order by 1, 2, 3""",
        "check_failures": f"select * from '{interim}/check_failures.parquet' order by 1, 2, 4",
        "summary": f"""
            select 'error_cells' as issue, "table", count(*) as n
            from '{interim}/error_cells.parquet' group by 2
            union all
            select 'check:' || "check", "table", count(*)
            from '{interim}/check_failures.parquet' group by 1, 2
            union all
            select 'control_total_mismatch', "table", count(*)
            from '{interim}/control_totals.parquet'
            where abs(reported - computed) > 0.51 group by 2
            order by 2, 1""",
    }
    for name, query in queries.items():
        duckdb.sql(f"copy ({query}) to '{out / name}.csv' (header)")
