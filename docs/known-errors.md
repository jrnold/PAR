# Known errors

Found by comparing the files to each other and to the catalog, and by the checks in
`src/par/schemas/`. Nothing here has been compared to the original published sources, so values that
look wrong are reported, not changed, unless this page says otherwise.

## Fixed by the build

  | Where                | Problem                                                                               | What the build does                |
  | -------------------- | ------------------------------------------------------------------------------------- | ---------------------------------- |
  | `VOEVODSK` Civil War | Dates stored as 1961 to 1965, because the spreadsheet couldn't hold dates before 1900 | Subtracts 100 years                |
  | `LIVRMORE`           | Dates stored as 1961 to 1965, for the same reason                                     | Subtracts 100 years                |
  | `DODGE`              | 128 rows with ditto marks in the name and date columns                                | Fills them from the row above      |
  | `DODGE`              | 3 rows with no day in the date                                                        | `*_min` and `*_max` span the month |
  | `BODASHIP`           | Misspelled headers                                                                    | Corrects the names                 |
  | `KRIVO`              | Quattro Pro macro keystrokes such as `{END}{LEFT}` in the header rows                 | Removes them from the citation     |
  | `LMI`                | Missing numbers coded -99, according to the catalog                                   | Reads them as null                 |
  | Spreadsheets         | Stored errors, which `sqz` writes as `ERR`                                            | Reads them as null and logs them   |

## Placeholders

`--`, `?`, `??`, and `..` are null in every column, including text columns. The documentation supports
this only in part:

- CEC's notes define `?` as unknown. The other sheets don't define these marks.
- The catalog warns that dashes are ambiguous: they could mean zero, unknown, not applicable, or not
  reported. So a null from `--` doesn't always mean the value was unknown. The COMP tables show why:
  their `total` columns add `--` cells as zero.
- For MOTTELAY, the catalog says its dashes follow the source, where it's unclear whether they mean
  zero or "data not available".

Other codes keep their documented meanings in text columns, because they aren't placeholders: `N/A` in
CEC (not applicable), `NR` and `U` in ORALFORE (not recorded, unknown), `NA` in SP128 loss types (not
identified as to type), and `UNSP` in AHART. A `U` in CEC's terrain means urban. In numeric columns
they are null.

## Error cells

`results/validation/error_cells.csv` lists every cell read as null because it held a stored error.
`sqz` writes both ERR and NA as `ERR`, so the file can't tell them apart.

  | Table              | Cells | Likely cause                                                                                                    |
  | ------------------ | ----- | --------------------------------------------------------------------------------------------------------------- |
  | `bwshall`          | 1,845 | 1,843 in `winner_b` and `loser_b`, where a battle has no second force, so likely NA. The other 2 are in row 445 |
  | `rmc`              | 523   | Attrition columns. The sheet doesn't explain it                                                                 |
  | `krivo`            | 29    | Formulas that depend on values the source gives as `--`                                                         |
  | `berndt`           | 18    | Formulas that depend on values the source gives as `??`                                                         |
  | `westwall`         | 9     | Unknown; the 2013 export showed `#N/A`                                                                          |
  | `parmisc`          | 2     | `end_month` and `end_day` in row 22                                                                             |
  | `voevodsk_vietnam` | 2     | Division by zero                                                                                                |
  | `ade`              | 1     | `ln` of a value that isn't positive                                                                             |

## Differences from the 2013 exports

The tables were built from the exports through version 1.0.0. Compared by key, every table has the
same rows, and no value became null. These changed:

  | Table                                                                   | Change                                                                                                                                      |
  | ----------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
  | `crete`, `iwojima`, `berndt`, `krivo`                                   | 195 null formula cells now hold the sheet's stored result (77, 72, 29, and 17). These are not independently checked                         |
  | `parmisc`                                                               | 3 `attacker_losses` values (seq 12, 13, 21) that were blanked by hand are restored                                                          |
  | `dodge`                                                                 | Hand-cleaning errors fixed: seq 77 had Hohenfriedberg's date on a Soor row, and seq 120 and 121 were named San Giorgio instead of Neresheim |
  | `sp128`, `sp190`                                                        | `attacker_won` (1 or 0) is now `wina` (+1 or -1), the sheets' own coding. 78 values differ                                                  |
  | `livrmore`                                                              | New column `attack_id_code`, which the hand cleaning dropped                                                                                |
  | `bwshall`, `dodge`, `livrmore`, `mottelay`, `parmisc`, `sp128`, `sp190` | `source_row` is now the row in the sheet, not in the cleaned export. Citations and notes come from the sheet                                |

## Values that fail a check, not changed

  | Table      | Row    | Problem                                                                                               |
  | ---------- | ------ | ----------------------------------------------------------------------------------------------------- |
  | `ade`      | 145    | 8th ID on Dec 29: Allied bloody casualties of 90 exceed total battle casualties of 46                 |
  | `bwshall`  | 103    | Parkany: loser losses of 90,000 exceed loser strength of 16,000                                       |
  | `bwshall`  | 489    | Uckerath: loser losses of 30,000 exceed loser strength of 24,000                                      |
  | `bwshall`  | 933    | Inkerman: winner dead plus wounded is 5,700, but bloody losses are 7,000                              |
  | `bwshall`  | 941    | Solferino: winner bloody plus missing is 13,100, but total losses are 17,400                          |
  | `bwshall`  | 959    | Perryville: winner losses of 3,400 exceed winner strength of 1,600                                    |
  | `cec`      | 9 rows | KIA + WIA + CMIA doesn't equal total battle casualties; the difference is often other dead or injured |
  | `comp28id` | 87, 88 | Both rows carry sequence number 73                                                                    |
  | `mottelay` | 49     | Ball's Bluff: Federal killed plus wounded is 449, but the total is 455                                |
  | `parmisc`  | 46     | Navarino: defender losses of 4,000 exceed defender strength of 1,962                                  |
  | `parmisc`  | 181    | Wounded Knee Creek: defender losses of 145 exceed defender strength of 120                            |

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
  | Diskette README, PARMISC               | Dates through 1945                       | 1965 (source row 104)                                        |
  | Diskette README, REISTERK              | Division data through 14 July 1953       | 27 July 1953 (source row 40)                                 |
  | Catalog, AHART                         | 3,594 records                            | The files hold 3,595                                         |
  | Previous README                        | "Helbold"                                | Helmbold                                                     |

## Citation details

The `sources` table holds each citation as fields. Text is as written apart from a closing period,
so `classification` is `U` for ORALFORE and `UNCLASSIFIED (formerly SECRET)` for KRIVO, and PARMISC
says `See Notes`. A few cases to know about:

- `LIVRMORE`: the sheet calls its dataset `LIVERMORE-1993`. The table keeps the sheet's spelling.
- `ORALFORE`: the revision date is a date number in row 11, read as 25 December 1989. That is earlier
  than the 1993 and 1994 dates on the other sheets, and it may only reflect the computer's clock.
- `AHART`, `LMI`: these have prose citations, so their fields were entered by hand from those.
  `BODASHIP`'s are parsed from a citation typed into its schema. `metadata_from` marks all three.
- `ADE` names no author, and `POGOGORO` no organization. Both are null.

## Gaps

- `BODASHIP.WQ!` is listed in the diskette README but isn't in this repository. `BODASHIP.csv` was
  added in the first commit and can't be traced to an original file. It is the only table not read
  from the diskette.
- `BERNDT` has four naval battles below its table, with no header of their own. They are in
  `berndt_naval`, and their columns are named after the land-battle headers above them.
