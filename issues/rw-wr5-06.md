TITLE: [Warehouse] [Finding] Real-world WR5-06 · Record expired and rejected food disposal and the FSSAI quarterly data
LABELS: task,warehouse,gap-real-world,phase-p4,warehouse-india
issue: 747
---
Part of #8 · Module **`warehouse-india`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **minor** · Finding type **MISSING-TASK** · Related: #42, #641, #32 · Source: real-world gap check 2026-11-03, lane WR5

> **Statutory content.** Sources are cited under Evidence; anything marked UNVERIFIED there, and every figure, must be confirmed against the law in force at build time.

## Why this task exists

Food installs only. FSSAI requires rejected, expired, recalled and returned food to be segregated and marked, disposal recorded (quantity destroyed, auctioned or redirected, and the agency), no relabelling as cattle feed, and quarterly data on FoSCoS. Without it the FBO rebuilds the return from scrap vouchers.

## Scope

A disposal route (DESTROYED / AUCTIONED / ANIMAL_FEED_AUTHORISED / RETURNED_TO_SUPPLIER) and agency on the scrap or disposal movement of food items. A quarterly report: rejected (with QC reference), expired and returned quantities, action taken, frozen when submitted. Hidden unless the food profile is on.

## Acceptance

- Scrapping an expired food lot requires a route and an agency
- The quarterly report rebuilt after submission is identical
- With the setting off, nothing appears

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

[FSSAI advisory RCD-02005/12/2024, 16-12-2024](https://fssai.gov.in/upload/advisories/2024/12/6773d3d6a50f3Advisory-expired-rejected%20food.pdf). Grep `FoSCoS` = 0.

## Global setting

`WAREHOUSE_FOOD_COMPLIANCE_ENABLED` default=false alternatives=true

The default is the recommendation; the alternatives are selectable per install through the settings page.
