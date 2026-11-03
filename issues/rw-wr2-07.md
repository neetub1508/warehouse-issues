TITLE: [Warehouse] [Finding] Real-world WR2-07 · Record storage temperature readings and hold stock on excursion
LABELS: task,warehouse,gap-real-world,phase-p5
issue: 734
---
Part of #10 · Module **`warehouse`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **major** · Finding type **MISSING-TASK** · Related: #29, #126, #42 · Source: real-world gap check 2026-11-03, lane WR2 · Merges WR5-07

> **Statutory content.** Sources are cited under Evidence; anything marked UNVERIFIED there, and every figure, must be confirmed against the law in force at build time.

## Why this task exists

A cold room or ambient pharma/food store must keep temperature records and act on an excursion (quarantine, QA disposition) before the goods are sold. The plan admits this is deferred "v2" and that item temperature limits without anything measuring against them are "a requirement with no enforcement", but no task exists, so the deferral is invisible. An FSSAI or drug inspector asking for temperature logs for the batch on the shelf gets nothing from the system.

## Scope

Temperature/humidity readings bound to zone or location (manual entry from a logger round, CSV import, or device push through the port); limit bands from the zone and item; excursion event with duration; automatic hold (P2-03) on positions in the zone for items whose limits were breached; QA disposition (release / reject / concession) closes the hold; reading report per zone and per lot for the lot's residence period.

## Acceptance

- A reading outside the zone band for longer than the configured grace opens one excursion and places holds on affected positions.
- Release requires the QA permission and a reason; holds remain on rejected lots.
- Per-lot report lists every reading of the zones the lot sat in during its residence.
- Manual readings require recorder, time and instrument.

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

FSSAI Sch.4 5.3.1.1 time/temperature control (P): https://www.taxclue.in/blog/schedule-4-part-2-fssai-licensing-regulations-food-operations-and-controls/ ; FSSAI storage audit checklist "records of temperature monitoring are maintained": https://infotrain.fssai.gov.in/AMS/doc/RDC_Draft_Storage_01_11_2017.pdf . docs/WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md deferral row B ("readings, excursions and auto-quarantine are v2"); issue_titles.txt has no title with cold/temperature/sensor/excursion; issues/00-EPIC-master.md:286 lists cold chain as a segment v1 "cannot serve at all".

## Global setting

`WAREHOUSE_TEMP_EXCURSION_GRACE_MINUTES` default=30 alternatives=0..240

The default is the recommendation; the alternatives are selectable per install through the settings page.

## Depends on

#29

## Merged finding WR5-07 · Log cold-room temperatures and hold stock on an excursion

Cold-chain stores (food, chemicals, 3PL cold storage) must prove temperature control. An excursion has to put the affected stock on hold for QA disposition, and clients and insurers ask for the log in a claim.

**Scope:** A temperature range per location or zone. Readings, manual or imported from a logger file. An out-of-range reading opens an excursion with start and end, and places a hold on the lots in that zone during the window. A log report per zone and period.

**Acceptance:**
- A reading of 9 °C in a 2-8 °C zone opens an excursion and holds the lots in that zone
- Closing the excursion records a disposition per lot
- The period log exports with min / max per day

**Evidence:** FSSAI Sch. 4 summary: 5 °C or below for high-risk food, -18 °C or below for frozen ([TaxClue](https://www.taxclue.in/blog/schedule-4-part-2-fssai-licensing-regulations-food-operations-and-controls/), practitioner). The design set has only an attribute key "cold-chain excursion" (p0-05 row 13).

**Global setting:** `WAREHOUSE_TEMP_EXCURSION_AUTO_HOLD` default=true alternatives=false
