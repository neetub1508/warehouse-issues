TITLE: [Warehouse] [Finding] Real-world WR6-07 · Produce client-attended count sheets and a year-end stock confirmation
LABELS: task,warehouse,gap-real-world,phase-p5,warehouse-3pl
issue: 757
---
Part of #10 · Module **`warehouse-3pl`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **minor** · Finding type **MISSING-TASK** · Related: #48, #684 · Source: real-world gap check 2026-11-03, lane WR6

> **Statutory content.** Sources are cited under Evidence; anything marked UNVERIFIED there, and every figure, must be confirmed against the law in force at build time.

## Why this task exists

Clients' auditors ask the 3PL to confirm quantities held at year end, and many contracts require a periodic joint count. Today the 3PL types this up by hand from the custody report.

## Scope

Add an as-at confirmation letter per client (qty by item/lot/status, at a chosen date, from WS-224's as-at grain) with operator signatory and document storage. Add a "client-attended" flag + attendee on count sessions.

## Acceptance

- A confirmation for 31-Mar shows the same quantities as WS-227 for that date.
- The confirmation lists only that client's stock.

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

SA 501 third-party inventory confirmation: UNVERIFIED (not fetched). Plan: WS-227 custody report gives as-at quantities. grep `stock confirmation|balance confirmation|SA 50[15]` returns nothing.
