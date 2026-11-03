TITLE: [Warehouse] [Finding] Real-world WR4-05 · Declare each dispatch under the transit-insurance open policy
LABELS: task,warehouse,gap-real-world,phase-p5
issue: 742
---
Part of #10 · Module **`warehouse`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **minor** · Finding type **MISSING-TASK** · Related: #73, #46 · Source: real-world gap check 2026-11-03, lane WR4

> **Statutory content.** Sources are cited under Evidence; anything marked UNVERIFIED there, and every figure, must be confirmed against the law in force at build time.

## Why this task exists

Manufacturers insure outward goods under an open marine/transit policy. Each dispatch is declared, and a claim is accepted only for a declared consignment. With no declaration register, the insurer can reject a transit-damage claim, and the monthly declaration is rebuilt by hand from invoices.

## Scope

A policy master (insurer, policy no., validity, per-consignment limit, applicable incoterms/freight terms). Each shipment where the company bears transit risk gets a declaration row (policy, value, date, route). A monthly declaration export. Outward transit claims link to the declaration (see WR4-06).

## Acceptance

- A shipment on FOR-destination terms gets a declaration row; an ex-works shipment does not
- A consignment over the per-consignment limit is flagged before dispatch
- The monthly declaration export totals match shipped value under the policy

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

Industry practice for open-cover policies. **UNVERIFIED: no primary source fetched.** Grep `transit insurance|marine insurance|insurance declaration` = 0 in warehouse-issues.

## Global setting

`WAREHOUSE_TRANSIT_INSURANCE_DECLARATION` default=OFF alternatives=ON

The default is the recommendation; the alternatives are selectable per install through the settings page.

## Depends on

#73
