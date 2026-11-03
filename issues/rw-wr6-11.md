TITLE: [Warehouse] [Finding] Real-world WR6-11 · Add dock-to-stock, inventory accuracy and order accuracy SLA metrics
LABELS: task,warehouse,gap-real-world,phase-p5,warehouse-3pl
issue: 761
---
Part of #10 · Module **`warehouse-3pl`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **minor** · Finding type **MISSING-TASK** · Related: #44, #122 · Source: real-world gap check 2026-11-03, lane WR6

> **Statutory content.** Sources are cited under Evidence; anything marked UNVERIFIED there, and every figure, must be confirmed against the law in force at build time.

## Why this task exists

Indian 3PL contracts commonly measure inbound turnaround and inventory record accuracy alongside dispatch timeliness. With only order-level metrics, the monthly KPI pack is built in a spreadsheet.

## Scope

Add three measurable metrics, each storing numerator and denominator with drill-through:
- DOCK_TO_STOCK (receipt → putaway complete within N hours, per receipt)
- INVENTORY_RECORD_ACCURACY (count lines without variance / counted lines)
- ORDER_ACCURACY (shipped orders without a client-raised claim or return for wrong item / shipped)

## Acceptance

- Each metric measures a month for a client with drill-through to failing receipts, count lines or orders.
- Each is owner-scoped (negative test).

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

R4 F-076 inventory accuracy metric (`docs/reviews/R4-fulfilment-3pl-audit.md:299, :1898`). Code: `Wh3plSlaDefinition.MEASURABLE_METRICS = List.of(ON_TIME_SHIP, ORDER_CYCLE_TIME)`. Market KPI lists: UNVERIFIED (no vendor page fetched).

## Depends on

#44
