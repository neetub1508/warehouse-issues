TITLE: [Warehouse] [Finding] Real-world WR6-08 · Add a Rule 58 warehouse register and a GST inspection pack per owner
LABELS: task,warehouse,gap-real-world,phase-p4,warehouse-india
issue: 758
---
Part of #8 · Module **`warehouse-india`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **minor** · Finding type **MISSING-TASK** · Related: #136, #48 · Source: real-world gap check 2026-11-03, lane WR6

> **Statutory content.** Sources are cited under Evidence; anything marked UNVERIFIED there, and every figure, must be confirmed against the law in force at build time.

## Why this task exists

On a GST officer's visit the operator must show goods identified owner-wise and item-wise, and books of the period each lot stayed, with receipt, dispatch, movement and disposal. WS-210 defaults to OWN stock and has no storage period column.

## Scope

Add a report labelled for Rule 58. Per owner, lot, item: inward date and document, outward date and document, days held, consignor/consignee, current bin. Add a one-click as-at owner-wise stock print for inspection.

## Acceptance

- The register for client X lists every receipt and dispatch with days held, and nothing for other owners.
- The inspection print at time T matches stock on hand by owner at T.

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

Rule 58(4),(5) under s.35(2): https://cbic-gst.gov.in/accnt-record-rules.html ; https://www.gstzen.in/a/records-to-be-maintained-by-owner-or-operator-of-godown-or-warehouse-and-transporters-cgst-rule-58.html. Plan: grep `Rule 58|35\(2\)` returns nothing; p2-20.md:70 "WS-210 defaults to OWN".
