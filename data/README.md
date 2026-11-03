# Data

## Sources

  | Directory            | Source                                                                                                                                                            | Retrieved                                      | Version          | License                           | How to fetch                                                        |
  | -------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------- | ---------------- | --------------------------------- | ------------------------------------------------------------------- |
  | `raw/dtic-adm000368` | DTIC ADM000368, PAR Datadisk diskettes                                                                                                                            | Before 2013; the retrieval date isn't recorded | 2.1, 31 May 1994 | Public domain, US government work | `dvc pull`. Three diskettes' worth of files, without `BODASHIP.WQ!` |
  | `manual/exports`     | CSV exports of the `.WQ!` spreadsheets, made through DOS Quattro Pro and LibreOffice in 2013, with eight later cleaned by hand. Only `BODASHIP.csv` is still read | Git history since 2013                         | None             | ODC PDDL 1.0                      | In git                                                              |

## Tables

One table per `.parquet` file in `processed/parquet/`, and one CSV per table in the data package.
Every table but `sources` has `source_row`, the row in its source file.

  | Table                | One row per                                                                 | Key           | Source   |
  | -------------------- | --------------------------------------------------------------------------- | ------------- | -------- |
  | `ade`                | Ardennes Campaign division-level engagements, 16 Dec 1944 to 16 Jan 1945    | `seq_no`      | ADE      |
  | `ahart`              | Artillery expenditures by selected US units, World War II to Vietnam        | `source_row`  | AHART    |
  | `berndt`             | Selected land battles, 1741 to 1877                                         | `seq_no`      | BERNDT   |
  | `berndt_naval`       | Four naval battles listed below the BERNDT table                            | `battle_name` | BERNDT   |
  | `bob18`              | Battle of Britain air combat, 13 Aug to 6 Sep 1940                          | `seq_no`      | BOB18    |
  | `bodaship`           | Naval engagements, 1638 to 1905                                             | `seq_no`      | BODASHIP |
  | `bwshall`            | Land battles, 1619 to 1905                                                  | `seq_no`      | BWSHALL  |
  | `cec`                | Contingency operations, 1946 to 1982                                        | `seq_no`      | CEC      |
  | `comp28id`           | US 28th Infantry Division casualties by sub-unit and day                    | `source_row`  | COMP28ID |
  | `comp6ad`            | US 6th Armored Division casualties by sub-unit and day                      | `seq_no`      | COMP6AD  |
  | `comp7ad`            | US 7th Armored Division casualties by sub-unit and day                      | `seq_no`      | COMP7AD  |
  | `crete`              | Battle of Crete daily strengths and losses                                  | `day_number`  | CRETE    |
  | `dodge`              | Losses in selected battles, 1631 to 1815                                    | `seq_no`      | DODGE    |
  | `inchon`             | Inchon-Seoul daily strengths and casualties, 14 Sep to 7 Oct 1950           | `day`         | INCHON   |
  | `iwojima`            | Iwo Jima daily strengths and losses, 19 Feb to 27 Mar 1945                  | `day_number`  | IWOJIMA  |
  | `kelley_korea`       | Korean War air combat engagements, 1951 to 1953                             | `seq_no`      | KELLEY   |
  | `kelley_vietnam`     | Vietnam War air combat engagements                                          | `seq_no`      | KELLEY   |
  | `krivo`              | Soviet strategic operations on the Eastern Front, 1941 to 1945              | `seq_no`      | KRIVO    |
  | `livrmore`           | US Civil War battles, 1861 to 1865                                          | `seq_no`      | LIVRMORE |
  | `lmi`                | US strengths and casualties in Northwest Europe, 15 Jun 1944 to 30 Apr 1945 | `source_row`  | LMI      |
  | `mottelay`           | US Civil War engagements, 1861 to 1865                                      | `seq_no`      | MOTTELAY |
  | `oralfore`           | Opposed rates of advance of large forces in Europe, 1940 to 1944            | `source_row`  | ORALFORE |
  | `parmisc`            | Battles from miscellaneous sources, 1741 to 1965                            | `seq_no`      | PARMISC  |
  | `pogogoro`           | Pogoreloye-Gorodische operation, 4 to 12 Aug 1942                           | `seq_no`      | POGOGORO |
  | `reisterk_division`  | Korean War US division-level operations                                     | `seq_no`      | REISTERK |
  | `reisterk_regiment`  | Korean War US regimental-level operations                                   | `seq_no`      | REISTERK |
  | `rmc`                | Ardennes and Lorraine battle days, 1944 to 1945                             | `seq_no`      | RMC      |
  | `sources`            | Source of each table: its citation as fields, with dates parsed             | `source`      | All      |
  | `sp128`              | Battles from CORG-SP-128, 1741 to 1945                                      | `seq_no`      | SP128    |
  | `sp190`              | Battles from CORG-SP-190, 280 BC to 1944                                    | `seq_no`      | SP190    |
  | `voevodsk_vietnam`   | US strength and cumulative battle losses, Vietnam War                       | `seq_no`      | VOEVODSK |
  | `voevodsk_korea`     | US strength and cumulative battle losses, Korean War                        | `seq_no`      | VOEVODSK |
  | `voevodsk_wwii`      | US strength and cumulative battle losses, World War II                      | `seq_no`      | VOEVODSK |
  | `voevodsk_wwi_us`    | US strength and cumulative battle deaths, World War I                       | `seq_no`      | VOEVODSK |
  | `voevodsk_wwi_mixed` | British, French, and German cumulative losses, World War I                  | `seq_no`      | VOEVODSK |
  | `voevodsk_civil_war` | Union and Confederate strength and cumulative losses, US Civil War          | `seq_no`      | VOEVODSK |
  | `westwall`           | Westwall combat phases, 2 to 7 Oct 1944                                     | `seq_no`      | WESTWALL |
