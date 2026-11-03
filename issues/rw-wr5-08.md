TITLE: [Warehouse] [Finding] Real-world WR5-08 · Run and record mock recall drills against the trace report
LABELS: task,warehouse,gap-real-world,phase-p5
issue: 748
---
Part of #10 · Module **`warehouse`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **minor** · Finding type **MISSING-TASK** · Related: #76, #141 · Source: real-world gap check 2026-11-03, lane WR5

> **Statutory content.** Sources are cited under Evidence; anything marked UNVERIFIED there, and every figure, must be confirmed against the law in force at build time.

## Why this task exists

FSSAI recall plans, and the customer and certification audits that test them, expect a periodic mock recall: pick a lot, trace one-up / one-down, and show what percentage of quantity was accounted for in how long. The plan names "mock recall" but no task builds it. A drill run as a live recall would quarantine real stock and notify real customers.

## Scope

A MOCK recall kind on #76 that runs trace forward and back, places no hold and sends no notification. It records start and finish time, quantity produced or received, quantity located (on hand, despatched by consignee, consumed, scrapped), % accounted for, and findings. Register with last-drill date per site.

## Acceptance

- A mock recall places no hold and sends nothing
- It shows the % accounted for and the elapsed time
- The site register shows the next drill due date

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

INDIA-LOCALISATION-PACK.md:1063 and R5 S-040 list mock recall. FSS (Food Recall Procedure) Regs 2017 ([APEDA copy](https://agriexchange.apeda.gov.in/ImportRegulations/FSSAIPublishesFinalRegulationsFoodRecallProceduresNew%20DelhiIndia232017.pdf)). Grep `mock` in issues gives only test mocks.

## Global setting

`WAREHOUSE_MOCK_RECALL_INTERVAL_MONTHS` default=12 alternatives=6|3

The default is the recommendation; the alternatives are selectable per install through the settings page.

## Depends on

#76
