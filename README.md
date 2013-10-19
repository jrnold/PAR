Personnel Attrition Rates in Historical Land Combat Operations
===============================================================

This repository contains the data from:

     "PAR Datadisk (Personnel Attrition Rates in Historical Land
     Combat Operations) (Revised) Version 2.1 (Computer Diskette).",
     May 31, 1994, DTIC ADM000368. http://oai.dtic.mil/oai/oai?verb=getRecord&metadataPrefix=html&identifier=ADM000368

*PAR Datadisk (Personnel
Attrition Rates in Historical Land Combat Operations) (Revised)
Version 2.1 (on CD-ROM).*, May 31, 1994, AD-M000368,
http://oai.dtic.mil/oai/oai?verb=getRecord&metadataPrefix=html&identifier=ADM000368

    **Abstract:** This study provides a catalog of computerized data bases on
    personnel casualties and attrition that will be of great value to
    all who use personnel casualty and attrition data in studies and
    analyses, weapons evaluation, wargames and simulation, model
    validation, assessing the utility of protective measures, and so
    forth. The scope of the study is limited to a selected class of
    databases. The criteria for inclusion is as follows: The databases
    must be in the public domain; in database form; contain
    information on military operations in and/or outcomes of battles
    or wars; must be available on disk; and will be useful to military
    operations analysts, developers, users, accessors, and military
    historians.

The documentation for this data are contained in

  Helbold, Robert L. "Personnel Attrition Rates in Historical Land
  Combat Operations: A Catalog of Attrition and Casualty Data Bases on
  Diskettes Usable with Personal Computers", Sep 1993, DTIC ADA279069.
  http://oai.dtic.mil/oai/oai?verb=getRecord&metadataPrefix=html&identifier=ADA279069

The original data were in an obsolete file format, ``WQ!`` which
requires DOS + Quattro Pro (< 4.0) because it was compressed using
[SQZ!](http://en.wikipedia.org/wiki/Synex_Systems_Corporation#SQZ.21).
I liberated the files from this format and converted them to something usable.

Files
---------------

The original files are contained in ``orig/``, while the new converted data are contained in ``data/``.

- *ADE.DB4*: It contains 393 rows recording selected division-level
engagements that took place during the World War II Ardennes Campaign
with dates of 16 December 1944 through 16 January 1945.  The columns
include an arbitrary row or sequence number, the number of days
elapsed (counting 16 December as day 1), the calendar date for that
day, the side ([A]merican, [G]erman, or [B]ritish) and identification
of the Base Unit used, the estimated German and Allied initial
strength when that base unit is used to define unit matchups, German
and Allied TBC, German and Allied bloody casualties, German and Allied
other changes in personnel strength on that day, and the distance
opposed advance by the Allies (negative if the Allies were driven
back).

- *AHART.txt*: A fixed-format ASCII file format is given below and explained more
fully in the companion document in Appendix B under AHART-1993.

   Field Name    Field Width in Characters
   ----------   --------------------------
   Source           20
   Battle           12
   Unit             12
   Size             8
   Date             8
   ArtyUnit         12
   TubeType         11
   TubeCat          7
   TubeQuant        12
   TypeRd           6
   RdPerDay         10
   RoundQuant       8
   DaysQuant        3
   Operation        9
   RoundWt          5
   RdWtDay          10
   TotalWt          12
   RdTubeDay        6
   RoundCost        4
   RdCostDay        10
   TotalCost        12
   Notes            10
   RedUnit          12
   RSize            8
   RedOpn           10
   RTypeTube        12
   RTubeQuant       10
   RTypeRd          6
   RRdPerDay        10
   RRdQuant         12
   Misc             57
   ----------   --------------------------
   Total            344



- *BERNDT.DB4*:  It contains 78 rows recording selected battles with
dates ranging from 1741 through 1877.  The columns include an
arbitrary row or sequence number; the battle name; starting year,
month, and day; victor and loser ID; initial victor and loser
strengths; victor and loser bloody losses, CMIA losses, and total
losses; and battle duration in hours.

- *BOB18.DB4*: It contains 18 rows recording Battle of Britain air
combat events for the dates 13 August 1940 through 06 September 1940.
The columns include an arbitrary row or sequence number; calendar
date; number of Luftwaffe attack sorties; number of Fighter Command
defense sorties; Luftwaffe and Fighter Command losses; and duration in
days (all of which are equal to 1 in this file).

- *BODASHIP.DB4*: It contains 120 rows recording selected naval
engagements with dates ranging from 1638 through 1905.  The columns
include an arbitrary row or sequence number; page from which the data
were taken; item number on the page from which the data were taken;
type of battle as given by the source; battle name; starting and
ending year, month, and day; duration in days; winner's and loser's
ID-A and ID-B; winner's and loser's initial number of personnel, main
ships, other ships, cannon, dead, wounded, bloody losses, MIA/POW,
total personnel losses, main ships lost, other ships lost, and cannon
lost.

- *BWSHALL.DB4*: It contains 1,087 rows recording selected land
battles with dates ranging from 1619 through 1905.  The columns
include an arbitrary row or sequence number; page from which the data
were taken; item number on the page from which the data were taken;
type of battle as given by the source; battle name; starting and
ending year, month, and day; duration in days; winner's and loser's
ID-A, ID-B, initial strength, dead, wounded, bloody losses, MIA/POW,
and total losses.

- *CEC.DB4*: It contains 81 rows recording selected contingency
operations with dates ranging from 1946 through 1982.  The columns
include an arbitrary row or sequence number; code number used by the
source; name of the operation; starting and ending dates; duration in
days; description; attacker advance in km; side 1 and side 2 IDs,
participants, and force; codes for the insertion method, unit type,
posture, terrain, weather, air superiority, and surprise achieved;
surpriser side; codes for surprise level, strength and casualties for
each side; personnel strength, KIA, WIA, CMIA, other dead, other
injured, DNBI, total battle casualties, and notes.

- *COMP28ID.DB4*: It contains 1,795 rows recording US 28th Infantry
Division events for the dates 2 November 1944 through 13 November
1944.  The columns include an arbitrary row or sequence number;
division name; date; ID of sub-unit level 1 (first echelon below
division); ID of sub-unit level 2 (second echelon below division); ID
of sub-unit level 3 (third echelon below division); the KIA, WIA, MIA,
non-battle injured, and total losses for the identified sub-unit.

- *COMP6AD.DB4*: It contains 508 rows recording US 6th Armored
Division events for the dates 31 December 1944 through 3 January 1945.
The columns include the same kinds of items as in the COMP28ID.DB4
spreadsheet.

- *COMP7AD.DB4*: It contains 934 rows recording US 7th Armored
Division events for the dates 17 December 1944 through 23 December
1944.  The columns include the same kinds of items as in the
``COMP28ID.DB4`` spreadsheet.

- *CRETE.DB4*: It contains 14 rows recording events surrounding the
battle for Crete during World War II.  The columns include the day
number; notes; D-Day + day number; German personnel landed, lost on
that day, cumulative losses, and survivors; and British personnel
ashore, landed, lost on that day, cumulative losses, and survivors
remaining on the island.

- *DODGE.DB4*: It  contains 261 rows recording losses in selected
battles with dates ranging from 1631 through 1815.  The columns
include an arbitrary row or sequence number; page from which the data
were taken; battle name; starting and ending year, month, and day;
nationality; number engaged and casualties; casualty type (KIA or
bloody); and notes.

- *INCHON.DB4*:  It contains 23 rows recording events for the dates
14 September 1950 through 7 October 1950.  The columns include the day
(D-Day + day); date; US Marine strength at 2400 on that day; North
Korean reinforcements and strength on that day; UN forces landed and
total ashore on that day; USMC KIA, DOW, MIA, WIA, and TBC on that
day; enemy POWs taken; enemy estimated casualties, TBC, strength at
2400, and reinforcements on that day.

- *IWOJIMA.DB4*:   It contains 37 rows recording events for the dates
19 February 1945 through 27 March 1945.  The columns include the day
number; notes; calendar date; Day (D-Day + day); USMC landed, lost,
cumulative losses, and survivors on the island on that day; Japanese
survivors ashore on that day; and the estimated US and Japanese
surviving strength on the island on that day.

- *KELLEY.DB4*:   It contains 315 rows recording selected air combat
engagements during the Korean war with dates ranging from 19 August
1957 through 22 July 1953 and 138 rows recording selected air combat
engagements during the Vietnam War.  The columns for the Korean War
include an arbitrary row or sequence number; date; number of US and
North Korean (NK) aircraft engaged; and number of US and NK aircraft
lost in the engagement.  The columns for the Vietnam War include an
arbitrary row or sequence number; ID of US and North Vietnamese (NVN)
aircraft types engaged; number of US and NVN aircraft engaged; number
of US and NVN aircraft lost.

- *KRIVO.DB4*: It contains 180 rows recording selected Soviet
operations on the Eastern Front during World War II with dates ranging
from 22 June 1941 through 9 August 1945.  The columns include an
arbitrary row or sequence number; page from which the data were taken;
the operation type indicated in the source; ID of the operation;
starting and ending dates; ID of major units involved on the Soviet
side, together with their initial strengths, permanent losses, medical
losses, total losses, average total losses per day, average total
losses per 1,000 men per day, ratio of medical to permanent losses;
and an index numbering the separate operations for which data are
recorded.

- *LIVRMORE.DB4*:   It contains 63 rows recording selected US Civil War
battles with dates ranging from July 1961 through April 1865. The
columns include an arbitrary row or sequence number; battle name;
starting and ending dates; attacker ID (Federal or Confederate);
attacker's ID code; attacker's and defender's personnel strengths,
KIA, WIA, bloody casualties, and MIA and POW; and ID of the winning
side.

- *LMI.txt* A fixed-format ASCII file, whose format is given below and explained more
fully in the companion document in Appendix B under LMI-1989.

    Field   Field Name  Type        Width   Example
    -----   ----------  ----        -----   -------
    1       DATE        Date        8       19441220
    2       UNIT        Character   5       INF D
    3       DIV         Numeric     3       99
    4       CORP        Numeric     2       5
    5       ARMY        Numeric     2       1
    6       AGP         Numeric     2       12
    7       KIA         Numeric     5       15
    8       WIA         Numeric     5       65
    9       CMIA        Numeric     5       303
    10      AUTH        Numeric     6       14184
    11      ASSD        Numeric     6       10734
    12      VERSION     Character   2
    -----   ----------  ----        -----   -------
                        Total       51

- *MOTTELAY.DB4*: It contains 120 rows recording selected engagements
of the US Civil War with dates ranging from June 1961 through April
1965. The columns include an arbitrary row or sequence number; page
from which the data were taken; calendar date; engagement type as
described by the source, location, and duration in hours; the Federal
and Confederate force sizes, KIA, WIA, bloody losses, POW, MIA, and
TBC; and ID of which side won (Federal or Confederate).

- *ORALFORE.DB4*:   It contains 360 rows recording selected events from
World War II with dates ranging from 10 May 1940 through 7 December
1944.  The columns include an arbitrary row or sequence number; ID of
the operation or phase involved; route, locale, sector, or other
location information; calendar date; distance in kilometers; codes for
the prevailing weather (both as it affected armor and, separately, as
it affected air), terrain, road net, obstacles, opposition intensity;
attacker's and defender's coded force condition and missions;
attacker's and defender's percent casualties; and comments.

- *PARMISC.DB4*:   It contains 209 rows recording selected battles
having dates ranging from 1741 through 1945.  The columns include an
arbitrary row or sequence number; number of the reference or source
used; volume and page number of the source; battle name; starting and
ending calendar dates; duration in days; attacker's and defender's
ID-A, ID-B, initial strength, dead, wounded, bloody losses, MIA/POW,
and total losses; ID of the victorious side; and notes.

- *POGOGORO.DB4*:   It contains 9 rows recording events from the Soviet
Pogoroloye-Gorodische operation for dates 4 August 1942 through 12
August 1942.  The columns include an arbitrary row or sequence number;
calendar date; Soviet and German strengths and losses on that day; and
notes.

- *REISTERK.DB4*:   It contains selected events from the Korean War: 43
rows for US division-level operations with dates ranging from 4 July
1950 through 14 July 1953, and 52 rows for US regimental-level
operations.  The columns used for the division-level operations
include an arbitrary row or sequence number; page from which the data
were taken; operation type as given by the source; operation name or
ID; starting and ending calendar dates; type unit involved; number of
units; number of unit-days; mean unit strength; KIA; WIA-CRO; and
WIA-Admitted.  The columns used for the regimental-level operations
include an arbitrary row or sequence number; page from which the data
were taken; operation type as given by the source; tactical action;
type unit; number of unit-days; mean unit strength; KIA; WIA-CRO;
WIA-Admitted; and the WIA/KIA ratio.

- *RMC.DB4*: This is a spreadsheet file readable by Quattro Pro
Version 3.0.  It contains 150 rows recording selected events from the
World War II Ardennes Offensive (Battle of the Bulge) with dates
ranging from 16 December 1944 through 2 January 1945, and 100 rows
recording selected events from the World War II Lorraine Offensive
with dates ranging from 8 September 1944 through 27 November 1944. The
columns include an arbitrary row or sequence number; ID of the
operation involved (Ardennes or Lorraine); ID code; calendar date;
codes for the attack type and description; codes for the posture,
attacker/defender ID, US and German artillery activity, environment
along the line, environment for a penetration, number of US and German
infantry platoons, US and German armor and anti-armor strength, US and
German degree of mechanization, US and German tank attrition, US and
German personnel attrition; advance distance in km; and frontage in
km.

- *SP128.DB4*: This is a spreadsheet file readable by Quattro Pro
Version 3.0.  It contains 92 rows recording selected battles with
dates ranging from 1741 through 1945.  The columns include an
arbitrary row or sequence number; battle name; ID of the source of the
information; year; ID of the attacker and defender; attacker and
defender initial strength, losses, and loss type code; duration in
days; and ID of the winning side (coded for attacker or defender).

- *SP190.DB4*: This is a spreadsheet file readable by Quattro Pro
Version 3.0.  It contains 83 rows recording selected battles with
dates ranging from 280BC through 1944 AD.  The columns include an
arbitrary row or sequence number; battle name; ID of the war,
campaign, or article; ID of the source of information; ID of the
attacker and defender; attacker and defender initial strength, losses,
and loss type code; duration in days; and ID of the winning side
(coded for attacker or defender).

- *VOEVODSK.DB4*:   It records selected items from various wars, mainly
the personnel strengths of the forces committed by one side and the
battle losses it suffered as the war progressed. Contains 24 rows of
US data from the Vietnam War; 16 rows of US data from the Korean War;
8 rows of US data from World War II; 9 rows of US data from World War
I; 22 rows of mixed British, French, and German data from World War I;
and 19 rows of mixed Federal and Confederate data from the US Civil
War.  Each part's columns include an arbitrary row or sequence number;
ID of the war; and calendar date.  The Vietnam part's columns include
US Army and DOD strength in theater, battle casualties, battle deaths,
and casualty/battle death ratio.  The Korean War part's columns
include US Army strength in theater, battle casualties, battle deaths,
and casualty/death ratio.  The US World War II part's columns include
total US Army strength, battle casualties, battle deaths, and
casualty/death ratio.  The US World War I part's columns include US
Army strength in theater and battle deaths.  The mixed British,
French, and German part's columns include British strength in theater,
bloody losses, and KIA; German bloody losses; French and British
battle losses; German battle losses in fighting the French; and German
battle losses in fighting the British.  The US Civil War part's
columns include Union and Confederate strength, battle casualties,
battle deaths, and casualty/death ratio.

- *WESTWALL.DB4*:  It contains 12 rows recording phases of the combat
between US and German forces in a sector of the Westwall for the dates
2 October 1944 through 7 October 1944.  The columns include an
arbitrary row or sequence number; calendar date and time of the
beginning and end of each phase; duration of each phase in hours;
beginning and ending time of the phase in hours relative to the start
of the battle; coded indication of whether the phase was active or
relatively quiet; for each phase, the US and German starting
strengths, losses during the phase, total reinforcements and/or
replacements during the phase, average rate of reinforcement and/or
replacement during the phase, and estimated strengths at the start of
each phase.

**Abbreviations** At various places in the following we have used
the following abbreviations or conventions:

-   KIA = killed in action.
-   WIA = missing in action.
-   MIA = missing in action.
-   POW = prisoner of war.
-   CMIA = captured or missing in action.
-   DNBI = diseased and non-battle injured.
-   Bloody casualties = KIA + WIA.
-   TBC = total battle casualties (sum of KIA, WIA, and CMIA).
-   ID = identification (a name or other identification).
-   ID-A = ID of the principal force component.
-   ID-B = ID of the secondary force component.
-   CRO = carded for record only.
-   Admitted = admitted to hospital for at least one over-night stay.
-   DTIC = Defense Technical Information Center.

