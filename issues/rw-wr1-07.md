TITLE: [Warehouse] [Finding] Real-world WR1-07 · Add IS 2500 switching rules and the 2026 skip-lot to AQL sampling
LABELS: task,warehouse,gap-real-world,phase-p8
issue: 727
---
Part of #546 · Module **`warehouse`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **minor** · Finding type **MISSING-TASK** · Related: #566, #640 · Source: real-world gap check 2026-11-03, lane WR1

> **Statutory content.** Sources are cited under Evidence; anything marked UNVERIFIED there, and every figure, must be confirmed against the law in force at build time.

## Why this task exists

An AQL plan in IS 2500 / ISO 2859-1 relies on switching between normal, tightened and reduced inspection to give the buyer the protection the AQL promises. Customers and auditors of auto and engineering suppliers expect it. The plan uses single normal plans only and has deferred switching with no task to re-enter it. ISO's January 2026 edition also adds skip-lot procedures.

## Scope

Per item × supplier inspection state (NORMAL / TIGHTENED / REDUCED / DISCONTINUED), updated by completed inspections under the standard's rules. Plan resolution picks the table for that state. Skip-lot per the 2026 edition. A history screen. An override with a reason.

## Acceptance

- Two lots rejected out of five consecutive lots move the pair to TIGHTENED, and the next inspection uses the tightened table. (The exact 2-of-5 rule needs checking against the standard text; it is UNVERIFIED.)
- Five consecutive accepted lots under TIGHTENED return the pair to NORMAL.
- The state and its history are visible per supplier-item.

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

Switching rules protect the consumer by moving to tightened inspection or stopping sampling when quality slips ([BIS IS 2500-1 preview](https://services.bis.gov.in/tmp/SR2500_1.pdf)). ISO 2859-1:2026 3rd ed. adds skip-lot ([ISO](https://www.iso.org/standard/85464.html)). Plan: FRD-STORES.md §12 row 4 "not building … switching rules" with re-entry path "an `inspection_level_history` table", but no issue exists.

## Global setting

`WAREHOUSE_QC_SWITCHING_RULES_ENABLED` default=false alternatives=true

The default is the recommendation; the alternatives are selectable per install through the settings page.

## Depends on

#566
