# Known errors

Found by comparing the files to each other and to the catalog, and by the checks in
`src/par/schemas/`. Nothing here has been compared to the original published sources, so values that
look wrong are reported, not changed, unless this page says otherwise.

## Fixed by the build

  | Where                | Problem                                                                               | What the build does              |
  | -------------------- | ------------------------------------------------------------------------------------- | -------------------------------- |
  | `VOEVODSK` Civil War | Dates stored as 1961 to 1965, because the spreadsheet couldn't hold dates before 1900 | Subtracts 100 years              |
  | `BWSHALL`            | Duration column headed `Sequence No."` in the 2013 CSV                                | Names it `duration_days`         |
  | `DODGE`              | Duplicate `start_date_min` and `end_date_min` headers                                 | Names the second of each `*_max` |
  | `DODGE`              | 36 rows with ditto marks in the four date columns                                     | Fills them from the row above    |
  | `SP128`              | Five rows of legend text at the end of the data                                       | Moves them to the table notes    |
  | `BODASHIP`, `SP190`  | Misspelled headers                                                                    | Corrects the names               |
  | `KRIVO`              | Quattro Pro macro keystrokes such as `{END}{LEFT}` in the header rows                 | Removes them from the citation   |
  | `LMI`                | Missing numbers coded -99, according to the catalog                                   | Reads them as null               |
  | Spreadsheet exports  | Error strings such as `#VALUE!`                                                       | Reads them as null and logs them |

## Placeholders

`--`, `?`, `??`, and `..` are null in every column, including text columns. The documentation supports
this only in part:

- CEC's notes define `?` as unknown. The other sheets don't define these marks.
- The catalog warns that dashes are ambiguous: they could mean zero, unknown, not applicable, or not
  reported. So a null from `--` doesn't always mean the value was unknown. The COMP tables show why:
  their `total` columns add `--` cells as zero.
- For MOTTELAY, the catalog says its dashes follow the source, where it's unclear whether they mean
  zero or "data not available". The 2013 CSV has blanks instead, which are also null.

Other codes keep their documented meanings in text columns, because they aren't placeholders: `N/A` in
CEC (not applicable), `NR` and `U` in ORALFORE (not recorded, unknown), `NA` in SP128 loss types (not
identified as to type), and `UNSP` in AHART. A `U` in CEC's terrain means urban. In numeric columns
they are null.

## Error cells

`results/validation/error_cells.csv` lists every cell read as null because it held an error string.
The CSV exports are the source for these tables, so these values are not recovered from the `.WQ!`
files or recomputed.

  | Table              | Cells | Likely cause                                                              |
  | ------------------ | ----- | ------------------------------------------------------------------------- |
  | `rmc`              | 523   | `-INF` in the attrition columns. The sheet doesn't explain it             |
  | `crete`            | 77    | Iterative formulas that LibreOffice couldn't evaluate in 2013 (`Err:522`) |
  | `iwojima`          | 72    | Cumulative formulas that failed in 2013 (`#VALUE!`)                       |
  | `berndt`           | 47    | Formulas that depend on values the source gives as `??`                   |
  | `krivo`            | 46    | Formulas that depend on values the source gives as `--`                   |
  | `westwall`         | 9     | `#N/A`                                                                    |
  | `voevodsk_vietnam` | 2     | Division by zero                                                          |
  | `ade`              | 1     | `ln` of a value that isn't positive                                       |

## Values that fail a check, not changed

  | Table      | Row    | Problem                                                                                               |
  | ---------- | ------ | ----------------------------------------------------------------------------------------------------- |
  | `ade`      | 145    | 8th ID on Dec 29: Allied bloody casualties of 90 exceed total battle casualties of 46                 |
  | `bwshall`  | 89     | Parkany: loser losses of 90,000 exceed loser strength of 16,000                                       |
  | `bwshall`  | 475    | Uckerath: loser losses of 30,000 exceed loser strength of 24,000                                      |
  | `bwshall`  | 919    | Inkerman: winner dead plus wounded is 5,700, but bloody losses are 7,000                              |
  | `bwshall`  | 927    | Solferino: winner bloody plus missing is 13,100, but total losses are 17,400                          |
  | `bwshall`  | 945    | Perryville: winner losses of 3,400 exceed winner strength of 1,600                                    |
  | `cec`      | 9 rows | KIA + WIA + CMIA doesn't equal total battle casualties; the difference is often other dead or injured |
  | `comp28id` | 87, 88 | Both rows carry sequence number 73                                                                    |
  | `mottelay` | 34     | Ball's Bluff: Federal killed plus wounded is 449, but the total is 455                                |
  | `parmisc`  | 32     | Navarino: defender losses of 4,000 exceed defender strength of 1,962                                  |
  | `parmisc`  | 167    | Wounded Knee Creek: defender losses of 145 exceed defender strength of 120                            |

Two other values look wrong but aren't caught by a check:

- `ahart`: 5 rows dated 1904 carry the WWII battle names SAAR and DIADEM (source rows 2765 and 3400 to 3403).
- `ahart`: 3 rows dated 1976 have the battle name NONE (source rows 2610 to 2612).

## Errors in the documentation

Corrected in this repository's documentation. The files in `data/raw/` are unchanged.

  | Where                                  | Says                                     | Should say                                                   |
  | -------------------------------------- | ---------------------------------------- | ------------------------------------------------------------ |
  | Diskette README                        | WIA = missing in action                  | Wounded in action                                            |
  | Diskette README, KELLEY                | Dates from 19 August 1957                | 1951, as in the data                                         |
  | Diskette README, LIVRMORE and MOTTELAY | Dates from 1961 to 1965                  | 1861 to 1865                                                 |
  | Diskette README, LMI                   | KIA, WIA, and CMIA are 5 characters wide | 6, which is what the 54-character records hold               |
  | Diskette README, AHART                 | Records of 344 characters                | 342 plus CRLF, which the catalog confirms; `misc` is 55 wide |
  | Diskette README, INCHON                | 23 rows                                  | 24 (days 0 to 23)                                            |
  | Diskette README, ORALFORE              | 360 rows                                 | 361, including one unnumbered row                            |
  | Diskette README, PARMISC               | Dates through 1945                       | 1965 (source row 90)                                         |
  | Diskette README, REISTERK              | Division data through 14 July 1953       | 27 July 1953 (source row 40)                                 |
  | Catalog, AHART                         | 3,594 records                            | The files hold 3,595                                         |
  | Previous README                        | "Helbold"                                | Helmbold                                                     |

## Gaps

- `BODASHIP.WQ!` is listed in the diskette README but isn't in this repository. `BODASHIP.csv` was
  added in the first commit and can't be traced to an original file.
- `BERNDT` has four naval battles below its table, with no header of their own. They are in
  `berndt_naval`, and their columns are named after the land-battle headers above them.
