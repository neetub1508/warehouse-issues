TITLE: [Warehouse] [Finding] Real-world WR6-06 · Run client exit as a handover: final joint count, stock-out, hold-over, data return
LABELS: task,warehouse,gap-real-world,phase-p5,warehouse-3pl
issue: 756
---
Part of #10 · Module **`warehouse-3pl`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **major** · Finding type **MISSING-TASK** · Related: #258, #17, #684 · Source: real-world gap check 2026-11-03, lane WR6

> **Statutory content.** Sources are cited under Evidence; anything marked UNVERIFIED there, and every figure, must be confirmed against the law in force at build time.

## Why this task exists

At exit the client and 3PL must agree a closing quantity, move or hand over every unit, and settle the final bill. Goods left after contract end go on hold-over rates and, after notice, an uncollected-goods procedure. The client must also remove the APOB. W64/GDN-R32 enforce only a cutoff and access closure, so the closing stock dispute and the stranded stock have no process.

## Scope

Add an offboarding template (reusing onboarding task sets) with blocking tasks. Final client-attended count, with a signed variance sheet feeding WR6-05 (#755). Bulk outward/transfer of remaining stock. Hold-over storage charge code effective after contract end. A notice ladder for uncollected stock (N days → reminder → final notice → disposal under contract) with documents. A data return export (stock, movement history, bills). A reminder to the client to delete the APOB. OFFBOARDED is reachable only with zero stock or a documented disposal.

## Acceptance

- OFFBOARD is refused while the client has non-zero stock and no disposal record.
- Stock left after contract end bills at the hold-over rate from the day after end date.
- The final count variance sheet is stored as a document and linked to the final run.
- The data export contains every movement for the client and nothing for another owner.

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

Client stock movement out is the client's own supply/stock transfer, needing invoice/challan + EWB (CBIC letter 25-09-2025, row 3). Plan: finding-w64.md scope "offboarding end date, COD/AR sinks…" only. grep `joint (count|verification)` returns nothing, `abandon` returns only reservation contexts, `hold.?over` returns only p2-03/p4-09 (not 3PL).

## Global setting

`WAREHOUSE_3PL_UNCOLLECTED_NOTICE_DAYS` default=30 alternatives=15, 60

The default is the recommendation; the alternatives are selectable per install through the settings page.

## Depends on

#258
