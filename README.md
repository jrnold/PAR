# Personnel Attrition Rates in Historical Land Combat Operations

Tidy tables from the Personnel Attrition Rates (PAR) data diskettes, compiled by Robert L. Helmbold
at the US Army Concepts Analysis Agency in 1993 and 1994. They cover personnel strengths and
casualties in battles and operations from 280 BC to 1982, in 36 tables from 28 source files.

The finished data is a [Frictionless data package](https://datapackage.org/), archived on Zenodo with
the original diskette files and both reports:
[doi:10.5281/zenodo.23927050](https://doi.org/10.5281/zenodo.23927050). `dvc repro` builds it as
`data/processed/par-datapackage.zip`, and `src/par/zenodo.py` uploads it.

## Get the data

```bash
uv sync
uv run dvc pull    # needs read access to gs://jrnold-dvc/PAR
uv run dvc repro
```

Rebuilding doesn't call LlamaParse. The OCR stage is frozen because it costs money.

## Know the limits of the data

The catalog warns that historical data bases can be expected to hold errors of at least 5 to 30
percent. Read it before using a table for analysis.

This repository doesn't correct values against the original sources. The build checks each table
for internal consistency and reports what it finds:

- [`docs/known-errors.md`](docs/known-errors.md) lists errors found so far, and how each was handled.
- `results/validation/` lists every failed check and spreadsheet error cell.

## Where the data comes from

The diskettes are:

> PAR Datadisk (Personnel Attrition Rates in Historical Land Combat Operations) (Revised) Version 2.1
> (Computer Diskette). May 31, 1994. DTIC ADM000368.

Two reports document them, and both are in this repository, with OCR text from LlamaParse:

  | Report                                                                                                                                                         | PDF                               | OCR text                          |
  | -------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------- | --------------------------------- |
  | Helmbold, Robert L. *A Catalog of Attrition and Casualty Data Bases on Diskettes Usable with Personal Computers.* CAA-RP-93-4, September 1993. DTIC ADA279069. | [PDF](docs/sources/ADA279069.pdf) | [Markdown](docs/ocr/ADA279069.md) |
  | *Addenda to the Annotated Bibliography.* CAA-RP-95-2. DTIC ADA294527.                                                                                          | [PDF](docs/sources/ADA294527.pdf) | [Markdown](docs/ocr/ADA294527.md) |

The spreadsheets on the diskettes are `.WQ!` files, Quattro Pro worksheets compressed with
[SQZ!](https://en.wikipedia.org/wiki/Synex_Systems_Corporation). In 2013 they were converted by
hand, through DOS Quattro Pro and LibreOffice, to the CSV files in `data/manual/exports/`. Those
exports are the source for those tables. The pipeline doesn't read the `.WQ!` files, which are kept
unchanged in `data/raw/`. Spreadsheet errors in the exports are null in the tables.

## How it's built

  | Stage          | Input                                                                  | Output                                                                   |
  | -------------- | ---------------------------------------------------------------------- | ------------------------------------------------------------------------ |
  | `ocr` (frozen) | `docs/sources/*.pdf`                                                   | `data/interim/ocr/`                                                      |
  | `ocr-markdown` | OCR results                                                            | `docs/ocr/*.md`                                                          |
  | `tables`       | `data/manual/exports/`, `data/raw/dtic-adm000368/`, `src/par/schemas/` | `data/processed/parquet/`, issue logs                                    |
  | `validate`     | issue logs                                                             | `results/validation/*.csv`                                               |
  | `package`      | tables, reports                                                        | `data/processed/datapackage/`, `par-datapackage.zip`, `par-diskette.zip` |

`src/par/schemas/` holds one file per source, saying where each table's rows are and what each
column means. See [`docs/datasets.md`](docs/datasets.md) for a description of each dataset, and
[`data/README.md`](data/README.md) for the tables.

## Abbreviations

- KIA: killed in action.
- WIA: wounded in action.
- MIA: missing in action.
- POW: prisoner of war.
- CMIA: captured or missing in action.
- DNBI: diseased and non-battle injured.
- Bloody casualties: KIA + WIA.
- TBC: total battle casualties (KIA + WIA + CMIA).
- CRO: carded for record only.
- Admitted: admitted to hospital for at least one overnight stay.

## License

- Diskette files and reports: public domain, as US government works.
- Derived tables: [ODC PDDL 1.0](https://opendatacommons.org/licenses/pddl/1-0/).
- Code: [MIT](LICENSE).
