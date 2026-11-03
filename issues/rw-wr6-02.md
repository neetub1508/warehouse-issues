TITLE: [Warehouse] [Finding] Real-world WR6-02 · Refuse receipt of client stock at a premises the client has not registered
LABELS: task,warehouse,gap-real-world,phase-p4,warehouse-3pl
issue: 752
---
Part of #8 · Module **`warehouse-3pl`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **major** · Finding type **MISSING-TASK** · Related: #68, #17, #684 · Source: real-world gap check 2026-11-03, lane WR6

> **Statutory content.** Sources are cited under Evidence; anything marked UNVERIFIED there, and every figure, must be confirmed against the law in force at build time.

## Why this task exists

Goods held at an undeclared place of business are exposed to detention and confiscation, and the client cannot legally supply from there. The plan records the registration and alarms on it, but lets stock be received anyway. The RFP point (FR-301) is then never enforced.

## Scope

Add an inbound-receipt and ASN guard, via a base pre-receipt SPI implemented by warehouse-3pl, that checks for an active client registration covering the site's state and warehouse. Apply the same check on stock-transfer arrival into a site for a client owner. Add a dashboard tile for live stock at uncovered sites.

## Acceptance

- In BLOCK mode, a GRN for client X at site S with no covering registration is refused with a field-level error naming X and the state.
- In WARN mode, the receipt posts and records an alert row with a recipient.
- The report lists client stock currently held at sites with no covering registration.

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

CBIC letter 25-09-2025 (row 3). In p4-10.md the acceptance is register + alarm only. grep `APOB` in p5-0*.md returns nothing; no receipt gate.

## Global setting

`WAREHOUSE_3PL_UNREGISTERED_PREMISES_POLICY` default=BLOCK alternatives=WARN, OFF

The default is the recommendation; the alternatives are selectable per install through the settings page.

## Depends on

#68
