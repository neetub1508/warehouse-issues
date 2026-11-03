TITLE: [Warehouse] [Finding] Real-world WR6-10 · Alert when an approved period is not invoiced within the statutory window
LABELS: task,warehouse,gap-real-world,phase-p5,warehouse-3pl
issue: 760
---
Part of #10 · Module **`warehouse-3pl`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **minor** · Finding type **MISSING-TASK** · Related: #35, #242 · Source: real-world gap check 2026-11-03, lane WR6

> **Statutory content.** Sources are cited under Evidence; anything marked UNVERIFIED there, and every figure, must be confirmed against the law in force at build time.

## Why this task exists

A run left in review or approved-not-invoiced past 30 days from the end of supply means a late invoice under Rule 47, or past the contract due date under s.31(5). Tax and interest then fall due from the earlier date.

## Scope

Add a scheduled check on runs whose period ended more than N days ago and are not INVOICED, with a recipient (WS-064 job row), on the billing dashboard.

## Acceptance

- A run for a period ended 26 days ago, still APPROVED, raises an alert to the billing manager.
- An INVOICED run raises none.

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

Rule 47: https://gstzen.in/a/time-limit-for-issuing-tax-invoice-cgst-rule-47.html ; s.31(5): https://taxguru.in/goods-and-service-tax/continuous-supply-services-gst-determining-time-supply-practical-examples.html. Plan: FR-292 has the run ladder with no ageing alarm.

## Global setting

`WAREHOUSE_3PL_INVOICE_LAG_ALERT_DAYS` default=25 alternatives=15, 28

The default is the recommendation; the alternatives are selectable per install through the settings page.
