TITLE: [Warehouse] [Finding] Real-world WR2-04 · Confirm and reconcile own stock held by third parties
LABELS: task,warehouse,gap-real-world,phase-p5
issue: 732
---
Part of #10 · Module **`warehouse`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **major** · Finding type **MISSING-TASK** · Related: #37, #48, #690, #24 · Source: real-world gap check 2026-11-03, lane WR2

> **Statutory content.** Sources are cited under Evidence; anything marked UNVERIFIED there, and every figure, must be confirmed against the law in force at build time.

## Why this task exists

Stock lying with job workers, C&F agents, consignment agents and hired third-party godowns is part of inventory but not countable by the company's own counters. At year end the auditor needs a confirmation from each custodian (or an inspection) and asks why goods have sat there longer than normal. Without a confirmation request/response record and a reconciliation of confirmed vs book quantity per lot, the finance team chases letters by e-mail and cannot show the auditor that differences were adjusted.

## Scope

Confirmation run per as-at date per external custodian (job worker, consignee, external godown counterparty/location): generate a statement of book quantity per item/lot from the as-at engine (WS-224), send (print/e-mail), record the custodian's confirmed quantity, compute differences, propose an adjustment through the existing count/adjustment approval path; ageing of stock at each custodian beyond a threshold.

## Acceptance

- A confirmation for custodian C at 31-Mar lists the as-at book quantity per item/lot even if movements were posted after 31-Mar.
- Entering a confirmed quantity lower than book creates a proposed adjustment that posts only after approval (approver != preparer).
- Unanswered confirmations older than N days appear on a pending list.
- Stock at a custodian older than the threshold shows on an ageing tile.

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

Third-party custody: auditor verifies management's procedures, third-party confirmations or inspections, and long-held stock (P): https://bcajonline.org/journal/caro-2020-series-new-clauses-and-modifications-inventories-and-other-current-assets/ ; equivalent ISA 501 para on third-party custody: https://www.charteredaccountants.ie/chariotindex/text/apb_isa_501_2010/12.html . grep -ril "stock confirmation|balance confirmation|third-party confirmation" design set = 0. #48 builds the *3PL's* custody report to its clients, the opposite direction; JOB_WORKER virtual location (p1-05.md:143) holds the balance but has no confirmation workflow.

## Global setting

`WAREHOUSE_THIRD_PARTY_STOCK_AGE_ALERT_DAYS` default=180 alternatives=any positive integer (a business alert, not a statutory figure)

The default is the recommendation; the alternatives are selectable per install through the settings page.

## Depends on

#136
