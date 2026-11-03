TITLE: [Warehouse] [Finding] Real-world WR3-14 · Track repairable spares by condition through repair
LABELS: task,warehouse,gap-real-world,phase-p8
issue: 737
---
Part of #546 · Module **`warehouse`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **minor** · Finding type **MISSING-TASK** · Related: #662 · Source: real-world gap check 2026-11-03, lane WR3

> **Statutory content.** Sources are cited under Evidence; anything marked UNVERIFIED there, and every figure, must be confirmed against the law in force at build time.

## Why this task exists

Maintenance stores issue a new motor or bearing housing against the old one and send the old one out for rewinding or repair. It comes back as a refurbished spare at repair cost. If the old part is never booked back, the plant loses track of costly spares at repairers and values a refurbished spare as new.

## Scope

An item flag `is_repairable`. Issuing one requires returning the old unit into status `DEFECTIVE` (no allocation, low value). An RGP for repair moves it to the repairer location. The repair receipt changes the status to `REFURBISHED`, valued at defective value + repair charge. Add a register of spares at repairers with ageing.

## Acceptance

- Issuing a repairable spare without an old-part return is refused or warned (setting).
- An old part sent on RGP shows in "at repairer" ageing.
- The repaired receipt is valued as old value + repair cost and is allocatable as REFURBISHED.

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

SAP repairable spares, valued by condition (New / Refurbished / Defective) and refurbished through an order: https://help.sap.com/saphelp_46c/helpdata/en/5b/ae3be44b8611d182ba0000e829fbfe/content.htm. Plan: grep `repairable|unserviceable|refurbish` in issues → none in scope. FR-512 RGP "never moves stock".

## Global setting

`WAREHOUSE_REPAIRABLE_OLD_PART_RETURN` default=REQUIRE alternatives=WARN,OFF

The default is the recommendation; the alternatives are selectable per install through the settings page.

## Depends on

none
---
Counts: catalogue 46 steps (31 covered, 4 planned-wrong, 11 gap). 14 findings (4 PLANNED-WRONG, 10 MISSING-TASK; 0 blocker, 10 major, 4 minor).
Statutory: 16 claims (14 confirmed, 1 changed: intra-state job-work e-way bill is state-specific). Unverified items: the ITC-04 notification number, Schedule M status after 31-Dec-2025, and the CRA-form 2025 amendment.
