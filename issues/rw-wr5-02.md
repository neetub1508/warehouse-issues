TITLE: [Warehouse] [Finding] Real-world WR5-02 · Enforce DG class segregation, licensed store quantity and SDS on file
LABELS: task,warehouse,gap-real-world,phase-p1,warehouse-base
issue: 744
---
Part of #4 · Module **`warehouse-base`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **major** · Finding type **MISSING-TASK** · Related: #126, #88, #33 · Source: real-world gap check 2026-11-03, lane WR5 · Merges WR2-08, WR2-09

> **Statutory content.** Sources are cited under Evidence; anything marked UNVERIFIED there, and every figure, must be confirmed against the law in force at build time.

## Why this task exists

FR-711 only checks that a location permits the item's class. Real storage rules also forbid incompatible classes in one store (oxidiser beside flammable liquid), cap the quantity a licensed store may hold (PESO licence quantity; MSIHC isolated-storage thresholds trigger duties), and require a safety data sheet available to workers. A warehouse that over-stocks a licensed shed breaches the licence even if each putaway was "allowed".

## Scope

(1) A class × class compatibility code list (ALLOWED / SEPARATE / FORBIDDEN), checked at putaway, transfer and load. (2) A maximum quantity per DG location or zone and class (in the class's UOM: litres or kg), optionally linked to a WR5-01 licence; the check uses the post-move on-hand. (3) An SDS document with revision and date on the item, required before the first receipt of a DG item, printable from the location. (4) A site report of quantity on hand per chemical against a configured threshold.

## Acceptance

- Putting class 5.1 into a store holding class 3, when the pair is FORBIDDEN, is refused with both classes named
- A putaway taking a store above its licensed litres is refused, with the remaining capacity stated
- Receipt of a DG item with no current SDS follows the setting
- The threshold report lists every chemical whose on-hand is at or above its threshold

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

Petroleum Rules 2002: Class A over 30 L needs a licence ([PESO FAQ](https://peso.gov.in/sites/default/files/2024-08/Revised%20FAQs%20on%20PR%202002%20PDF.pdf)). MSIHC r.2 / Sch. 2 thresholds and Sch. 5 SDS ([PPCB copy](https://ppcb.punjab.gov.in/media/documents/The_Manufacture_Storage__Import_of_Hazardous_Chemical_Rules_1989.pdf)). Grep: `\bSDS\b|MSDS|safety data` in issues = 0. Per-zone ceilings existed only in fenced #88.

## Global setting

`WAREHOUSE_DG_SDS_REQUIRED_AT_RECEIPT` default=BLOCK alternatives=WARN|OFF; `WAREHOUSE_DG_QUANTITY_CEILING_ACTION` default=BLOCK alternatives=WARN

The default is the recommendation; the alternatives are selectable per install through the settings page.

## Depends on

#126

## Merged finding WR2-08 · Enforce dangerous-goods segregation between incompatible classes

P1-15 checks that a location is a DG store permitting the item's class, but a store permitting both class 3 (flammable liquids) and 5.1 (oxidisers) will accept them in the same bin or next to each other. Chemical-warehousing practice is a segregation table (none / segregate / keep apart / isolate) between classes; putting incompatibles together is the classic fire and toxic-gas cause, and the factory inspector or insurer surveyor will call it out.

**Scope:** DG compatibility matrix as data (class x class → ALLOWED / SEPARATE_LOCATION / SEPARATE_ZONE / SEPARATE_STORE); putaway suggestion and confirmation, transfer and LPN move refuse a placement that violates the matrix against stock already in the same location / zone; seeded default matrix from a recognised table, editable by the safety officer with audit.

**Acceptance:**
- With class 3 stock in bin B, putting class 5.1 stock into B is refused naming both classes; into another bin of the same zone it is refused only if the matrix says SEPARATE_ZONE.
- Matrix edits are audited and require a distinct permission.
- With the setting off, today's behaviour holds.

**Evidence:** HSE HSG71 Chemical warehousing (segregation of incompatible substances, paras 60-73): https://www.hse.gov.uk/pubns/books/hsg71.htm , https://www.hse.gov.uk/Comah/sragtech/techmeassegregat.htm ; Queensland managing incompatible goods: https://www.worksafe.qld.gov.au/safety-and-prevention/hazards/hazardous-chemicals/managing-hazchem-risks/managing-incompatible-goods . issues/p1-15.md:161-163 (FR-710/711) checks location-permits-class only; no compatibility matrix (grep "segregation table|incompatib" in p1-15 = 0).

**Global setting:** `WAREHOUSE_DG_COMPATIBILITY_ENFORCED` default=true alternatives=false

## Merged finding WR2-09 · Stop on-hand exceeding a premises' licensed storage quantity

Petroleum, explosives, pesticide and fertiliser storage licences are issued for a premises and a maximum quantity (e.g. PESO: Class B above 2,500 L needs a licence, district authority up to 25,000 L). Receiving one more tanker or pallet than the licence allows is an offence and voids fire insurance cover, yet the plan only caps despatch per period for narcotics and some pesticides. Storekeepers today watch it on a whiteboard.

**Scope:** On `whin_entity_licences`, licensed storage capacity per class/category and UoM for the licensed site (and optionally location/zone); receipt, putaway, transfer-in and production receipt check projected on-hand of licensed categories against capacity; warn at a threshold, refuse above capacity unless the licence is amended; expired own licence blocks receipts of that category.

**Acceptance:**
- Site licence 20,000 L Class B, on-hand 18,500 L: a GRN of 2,000 L is refused with remaining capacity 1,500 L.
- At >= warn threshold the receipt succeeds with an alert to the licence holder.
- An expired own licence refuses receipt of its categories at that site.

**Evidence:** PESO SOP and FAQ thresholds and licensing authorities: https://peso.gov.in/sites/default/files/2025-01/Petroleum%20Rules%202002%20-%20SOP.pdf ; https://peso.gov.in/sites/default/files/2024-08/Revised%20FAQs%20on%20PR%202002%20PDF.pdf . issues/p4-13.md:52-54 `whin_licence_quantity_ceilings` "cap quantity per period" for despatch; p4-13.md:78,123 despatch guard only; no receipt/putaway capacity check.

**Global setting:** `WAREHOUSE_LICENSED_CAPACITY_WARN_PCT` default=90 alternatives=50..100
