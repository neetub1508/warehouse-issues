TITLE: [Warehouse] [Finding] Real-world WR2-05 · Parse all GS1 date and content AIs at scan, mapping 15 to best-before
LABELS: task,warehouse,gap-real-world,phase-p3,warehouse-base
issue: 733
---
Part of #7 · Module **`warehouse-base`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **major** · Finding type **PLANNED-WRONG** · Related: #20, #74, #42, #121, #712 · Source: real-world gap check 2026-11-03, lane WR2

> **Statutory content.** Sources are cited under Evidence; anything marked UNVERIFIED there, and every figure, must be confirmed against the law in force at build time.

## Why this task exists

Supplier cartons and pharma/food DataMatrix codes routinely carry production date (11), best-before (15) or pack date (13) alongside GTIN, lot and expiry. The scan service refuses the whole string when it meets an AI it does not know, so the receiver at the dock, the putaway operator and the counter all fall back to typing lot and dates by hand on a real supplier label, which defeats scanning and invites wrong-date entry on FEFO stock. The design separately insists best-before and use-by are different dates, but the scanner can only read use-by (17).

## Scope

Add fixed-length AIs 02, 11, 12, 13, 15, 16 and variable AIs 37, 240, 30, 400, 7003 (at least read-and-carry, not refuse); map 15 to the lot's best-before, 11 to manufacture date, 17 to expiry; when 02+37 appear, resolve the pack level from the content GTIN and quantity; unknown-but-well-formed AIs from the GS1 table are skipped with a warning instead of refusing the scan. Optionally parse GS1 Digital Link URIs (`https://<domain>/01/<gtin>/10/<lot>?17=<date>`) into the same composite (the part of #121 that is not SSCC allocation).

## Acceptance

- `(01)08901234567894(11)260101(17)271231(10)L1` resolves item, lot L1, mfg 2026-01-01, expiry 2027-12-31.
- `(01)...(15)270630(10)L2` sets best-before 2027-06-30 and leaves expiry empty.
- A string with a well-formed AI not in the supported list resolves the supported parts and returns a warning, not 422.
- A Digital Link URI with 01/10/17 resolves the same composite as the equivalent element string.

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

GS1 AI table: 02 CONTENT N2+N14, 11 PROD DATE, 13 PACK DATE, 15 BEST BEFORE, 16 SELL BY, 17 USE BY or EXPIRY (all N2+N6): https://ref.gs1.org/ai/GS1_Application_Identifiers.jsonld . Code: `classic/warehouse-base/backend/src/main/java/ai/warehousebase/service/scan/WhbGs1ElementStringParser.java:75-90` defines only AI 00, 01, 10, 17, 21, 310n (FIXED_LENGTHS = 00,01,17; VARIABLE_AIS = 10,21) and throws GS1_ELEMENT_UNPARSEABLE when an announced GS1 string "cannot be read whole". Design pack line 1064 requires best-before and use-by as two columns.

## Depends on

#20
