# PAR

Tidy tables and a Frictionless data package from the 1994 PAR data diskettes. See `README.md`.

- The `sheets` stage decodes the `.WQ!` files to `data/interim/sqz-csv/` with `sqz` (`cargo install quattro-sqz --locked`), and those CSVs are the source for the spreadsheet tables. `BODASHIP.WQ!` is lost, so that table alone reads `data/manual/exports/BODASHIP.csv`. Spreadsheet errors (`ERR`) and the placeholders `--`, `?`, `??`, and `..` are null.
- Column meanings and row ranges live in `src/par/schemas/`. Change them there, not in generated files.
- Parsing is strict. If a new value stops the build, add it to the column's `missing` list only if it really means missing.
- Don't change a data value to make a check pass. Record a real correction in `data/manual/corrections.csv` (`table,source_row,column,old,new,reason`) and in `docs/known-errors.md`.
- Publishing to Zenodo can't be undone. Only run `par-zenodo-upload --publish` when asked.

## Data (DVC)

This project follows the data baseline; read it with `git show main:data-baseline/README.md`. Its
project type is corpus. This directory is its own DVC project, so run `dvc` from here.

- Default remote: `gs://jrnold-dvc/PAR`. On an auth error, ask the user to run
  `! gcloud auth application-default login`.
- After changing data: `dvc repro` or `dvc add`, `dvc push`, `git commit`, `git push`.
- Never run `dvc gc`, and never `git add` a DVC-tracked path.

Exceptions to the baseline, one line each, in the form `Exception to P1: reason`. `data-audit` reads
these lines and reports the rule as accepted. There are none yet.
