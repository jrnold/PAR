"""Tests for the table parser, the schemas, and the source files they describe."""

import datetime as dt
import re
from pathlib import Path
from typing import Any

import pytest
import yaml

from par import tables, zenodo
from par.package import VERSION
from par.sources import load_sources, parse_citation
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
    out = parse([[0, "a", "integer", "A"]], [["1"], ["ERR"]], keys=["source_row"])
    assert out.arrow["a"].to_pylist() == [1, None]
    assert out.error_cells == [{"table": "x", "source_row": 2, "column": "a", "value": "ERR"}]


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
        [["22463"], ["23802"]],
        keys=["source_row"],
        date_year_offset=-100,
    )
    assert out.arrow["d"].to_pylist() == [dt.date(1861, 7, 1), dt.date(1865, 3, 1)]


def test_date_numbers_use_the_spreadsheet_epoch() -> None:
    out = parse([[0, "d", "date", "D"]], [["14836"], ["16437"]], keys=["source_row"])
    assert out.arrow["d"].to_pylist() == [dt.date(1940, 8, 13), dt.date(1944, 12, 31)]


def test_time_fractions_become_times() -> None:
    out = parse([[0, "t", "time", "T"]], [["0.4583333333333333"], ["0"]], keys=["source_row"])
    assert out.arrow["t"].to_pylist() == [dt.time(11), dt.time(0)]


def test_time_outside_a_day_stops_the_build() -> None:
    with pytest.raises(ValueError, match="fraction of a day"):
        parse([[0, "t", "time", "T"]], [["0.5"], ["1.5"]])


def test_date_parts_are_joined() -> None:
    column = {"parts": [0, 1, 2], "name": "d", "type": "date", "description": "D"}
    out = parse([column], [["1619", "6", "10"], ["1620", "11", "8"]], keys=["source_row"])
    assert out.arrow["d"].to_pylist() == [dt.date(1619, 6, 10), dt.date(1620, 11, 8)]


@pytest.mark.parametrize("day", ["?", "ERR"])
def test_unknown_day_gives_the_range_of_the_month(day: str) -> None:
    columns = [
        {"parts": [0, 1, 2], "partial": bound, "name": name, "type": "date", "description": "D"}
        for bound, name in (("first", "low"), ("last", "high"))
    ]
    out = parse(columns, [["1702", "7", day], ["1704", "2", day]], keys=["source_row"])
    assert out.arrow["low"].to_pylist() == [dt.date(1702, 7, 1), dt.date(1704, 2, 1)]
    assert out.arrow["high"].to_pylist() == [dt.date(1702, 7, 31), dt.date(1704, 2, 29)]


def test_split_date_ditto_copies_the_row_above() -> None:
    column = {"parts": [0, 1, 2], "name": "d", "type": "date", "description": "D", "ditto": '"-"-"'}
    out = parse([column], [["1674", "6", "16"], ['"', '"', '"']], keys=["source_row"])
    assert out.arrow["d"].to_pylist() == [dt.date(1674, 6, 16)] * 2


def test_text_missing_nulls_a_code_in_text_columns() -> None:
    out = parse(
        [[0, "a", "string", "A"]], [["NA"], ["x"]], keys=["source_row"], text_missing=["NA"]
    )
    assert out.arrow["a"].to_pylist() == [None, "x"]


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
    """Parse every spreadsheet table. Needs the `sheets` stage's output (`dvc pull`)."""
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


def test_every_sheet_but_bodaship_comes_from_the_diskette() -> None:
    sources = [yaml.safe_load(p.read_text()) for p in sorted(tables.SCHEMA_DIR.glob("*.yaml"))]
    exports = {s["source"] for s in sources if "export" in s}
    assert exports == {"BODASHIP"}


def test_sheet_values_the_exports_lost_are_recovered() -> None:
    parsed = spreadsheet_tables()
    # The sheets leave these cells empty in a table's first or last rows, so they aren't all filled.
    for table, column, filled in [
        ("crete", "allied_cum_losses", 13),
        ("crete", "german_survivors", 13),
        ("iwojima", "usmc_cum_losses", 36),
        ("iwojima", "usmc_survivors", 36),
    ]:
        values = [v for v in parsed[table].arrow[column].to_pylist() if v is not None]
        assert len(values) >= filled, (table, column)
    for table, column in [("crete", "allied_cum_losses"), ("iwojima", "usmc_cum_losses")]:
        values = [v for v in parsed[table].arrow[column].to_pylist() if v is not None]
        assert values == sorted(values), (table, column)


def test_dodge_keeps_the_sheet_where_the_export_was_wrong() -> None:
    rows = {r["seq_no"]: r for r in spreadsheet_tables()["dodge"].arrow.to_pylist()}
    assert rows[77]["battle_name"] == "Soor"
    assert rows[77]["start_date_min"] == dt.date(1745, 9, 30)
    assert rows[120]["battle_name"] == "Neresheim"
    assert (rows[9]["start_date_min"], rows[9]["start_date_max"]) == (
        dt.date(1702, 7, 1),
        dt.date(1702, 7, 31),
    )


def test_civil_war_sheets_are_moved_back_a_century() -> None:
    dates = spreadsheet_tables()["livrmore"].arrow["start_date"].to_pylist()
    assert dates[0] == dt.date(1861, 7, 21)


@pytest.mark.parametrize("table", ["sp128", "sp190", "livrmore"])
def test_wina_keeps_the_sheet_coding(table: str) -> None:
    assert set(spreadsheet_tables()[table].arrow["wina"].to_pylist()) == {-1, 1}


def test_hand_cleaned_sheets_take_their_citation_from_the_sheet() -> None:
    parsed = spreadsheet_tables()
    for table in ("bwshall", "dodge", "livrmore", "mottelay", "parmisc", "sp128", "sp190"):
        assert "Prepared By: Dr. Robert L. Helmbold" in parsed[table].citation, table


def test_citation_fields_join_wrapped_lines_but_not_colons_in_titles() -> None:
    fields = parse_citation(
        "Data From (Title): Historical Data and Lanchester's Theory of\n"
        "Combat: Part II.\n"
        "Author: Helmbold, Robert L.\n"
        "Organization:\n"
        "Spreadsheet last revised: 30 October 1993"
    )
    assert fields == {
        "title": "Historical Data and Lanchester's Theory of Combat: Part II",
        "author": "Helmbold, Robert L.",
        "organization": None,
        "last_revised": "30 October 1993",
    }


def test_citation_must_start_with_a_label() -> None:
    with pytest.raises(ValueError, match="start with a label"):
        parse_citation("Dougherty, Francis L., and so on")


def source_rows() -> dict[str, dict[str, Any]]:
    """Return the `sources` table by source."""
    return {row["source"]: row for row in load_sources().arrow.to_pylist()}


def test_sources_has_one_row_per_schema() -> None:
    assert set(source_rows()) == {p.stem for p in tables.SCHEMA_DIR.glob("*.yaml")}


def test_every_source_has_core_fields() -> None:
    for name, row in source_rows().items():
        for field in ("dataset", "title", "publication_date", "publication_year", "classification"):
            assert row[field] is not None, (name, field)


def test_every_table_is_listed_under_one_source() -> None:
    listed = [t for row in source_rows().values() for t in row["tables"].split(", ")]
    assert sorted(listed) == sorted(spreadsheet_tables() | {"ahart": 0, "lmi": 0})


def test_datasets_match_the_schemas_except_the_livermore_spelling() -> None:
    for path in tables.SCHEMA_DIR.glob("*.yaml"):
        expected = yaml.safe_load(path.read_text())["dataset"]
        found = source_rows()[path.stem]["dataset"]
        assert found == expected or (path.stem, found) == ("LIVRMORE", "LIVERMORE-1993")


def test_only_hand_typed_citations_are_marked_schema() -> None:
    by_hand = {n for n, row in source_rows().items() if row["metadata_from"] == "schema"}
    assert by_hand == {"AHART", "BODASHIP", "LMI"}


def test_revision_dates_are_parsed() -> None:
    rows = source_rows()
    assert rows["DODGE"]["last_revised"] == dt.date(1994, 1, 11)
    missing = {n for n, row in rows.items() if row["last_revised"] is None}
    assert missing == {"AHART", "LMI"}


def test_oralfore_revision_date_matches_the_number_in_the_sheet() -> None:
    source = yaml.safe_load((tables.SCHEMA_DIR / "ORALFORE.yaml").read_text())
    number = float(tables.clean_text(tables.read_rows(source)[10]).split()[-1])
    expected = tables.DATE_EPOCH + dt.timedelta(days=int(number))
    assert source_rows()["ORALFORE"]["last_revised"] == expected


def test_zenodo_metadata_has_required_fields() -> None:
    record = metadata(dt.date(2026, 1, 2))
    assert record["publication_date"] == "2026-01-02"
    for key in ("title", "upload_type", "description", "creators"):
        assert record[key]
    assert record["version"] == VERSION


def test_zenodo_upload_needs_a_target_so_it_cant_create_a_separate_record(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("sys.argv", ["par-zenodo-upload"])
    monkeypatch.setattr(zenodo, "request", lambda *_a, **_k: pytest.fail("called the API"))
    with pytest.raises(SystemExit):
        zenodo.main()


def test_zenodo_publish_needs_a_draft(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.argv", ["par-zenodo-upload", "--new-version-of", "1", "--publish"])
    monkeypatch.setattr(zenodo, "request", lambda *_a, **_k: pytest.fail("called the API"))
    with pytest.raises(SystemExit):
        zenodo.main()


def test_zenodo_new_version_returns_the_new_draft(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, str]] = []

    def fake(url: str, _token: str, method: str = "GET") -> dict[str, Any]:
        calls.append((method, url))
        return {"id": 2, "links": {"latest_draft": "draft-url"}}

    monkeypatch.setattr(zenodo, "request", fake)
    assert zenodo.new_version_draft(1, "token")["id"] == 2
    assert calls == [("POST", f"{zenodo.API}/1/actions/newversion"), ("GET", "draft-url")]
