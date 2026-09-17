# warehouse-issues

For Claude task execution, follow [CLAUDE.md](CLAUDE.md). It preserves the existing task conventions and limits implementation to the assigned scope.


**Adopted solutions:** [Global settings and resolved behaviour](docs/GLOBAL-SETTINGS-DECISIONS.md) · [First-day setup](INSTALL.md). Existing historical questions are resolved by this contract where named.


Design, requirements and delivery backlog for the Classic **Warehouse and Inventory Management**
product.

This repository holds the pre-implementation design set. **No production code lives here** — the code
will be built in [`neetub1508/classic`](https://github.com/neetub1508/classic).

Start with **[`docs/README.md`](docs/README.md)** — it gives the read order and says who each document
is for. If you are about to write the first migration, start instead with
**[`docs/IRREVERSIBLE.md`](docs/IRREVERSIBLE.md)**.

---

## What is being built

A **standalone-capable, country-neutral warehouse and inventory-management product**: one immutable,
double-sided, append-only stock ledger at full grain, the application layers that write to it, and a
generic inbound movement port so that any number of future consumers — a logistics/TMS module, a
supply-chain module, a POS, an eCommerce channel, or any vertical in the suite — can move stock
**without `warehouse-base` ever depending on them**.

It is the first real stock ledger in this suite. `services`, `field-service` and `assets` have no stock
capability at all today, and a workshop's parts issue is stored as free text.

```
platform                                V0      – V999      (exists)
 └── warehouse-base                     V500000 – V509999   NEW   v1
     │   the stock ledger and its masters
     │   items · variants · UoM & conversions · barcodes
     │   sites · zones · locations · lots · serials · LPNs
     │   owners · counterparties · the fourteen open catalogues
     │   movements · positions · reservations · cost layers
     │   the generic inbound movement port · the outbox
     │
     ├── warehouse                      V510000 – V519999   NEW   v1
     │   the application on top of the ledger
     │   inbound: ASN · receiving · QC · putaway · cross-dock
     │   outbound: allocation · waves · pick · pack · ship
     │   transfers · adjustments · counts · replenishment
     │   valuation & costing · returns · printing · kitting
     │   execution: tasks · RF flows · dock · van stock
     │
     ├── warehouse-adapter-<vertical>   V520000 – V529999   NEW   v1 → v2
     │   dealer parts · services job parts · field-service van
     │   stock · assets spares · the logistics seam
     │
     ├── warehouse-3pl                  V530000 – V539999   NEW   v2
     │   owner-of-goods billing · rate cards · the billable-event
     │   meter · storage algorithms · the client portal
     │
     └── warehouse-india                V540000 – V549999   NEW   v1 + v2
         wave 1 — the documents goods cannot legally move without
         wave 2 — the statutory registers and filings
```

`warehouse-base` depends on **platform only**. It has zero compile-time dependency on any vertical and
never reads another module's tables. Every foreign key between the modules points *downward* — proven,
table by table, in [`docs/DATA-MODEL.md`](docs/DATA-MODEL.md) §3.

## The decisions that shape everything

The full set is [`docs/DECISIONS.md`](docs/DECISIONS.md) — `D-1`…`D-13`. The five a reader will
otherwise re-litigate:

| | |
|---|---|
| **D-1** | **Five modules, not four.** The brief's four carry a *vertical* axis and no *jurisdiction* axis, so `warehouse-india` exists — the same call accounting took |
| **D-2** | **Flyway bands are V500000–V549999, not V900000+.** The bands originally proposed are already occupied by **1,061 existing `.sql` files** (dealer OEM seed and platform per-client migrations), and a collision there does not fail loudly — it silently deletes a history row |
| **D-5** | **`owner_id` is `NOT NULL` in v1, in every install.** `warehouse-3pl` ships in v2; the column cannot. No rule recovers whose a unit was, so it is free now and unbackfillable later — without it, 3PL is not a module, it is a rewrite |
| **D-6** | **Whichever system is authoritative for quantity is authoritative for cost.** Warehouse owns the movement, the position and the costing engine; accounting always owns the ledger and does not re-cost what it is handed |
| **D-12** | **v1 is a cut line, not the scope limit.** Every capability found by any lens is placed in a version and carried in a task **now** — v1, v1.1, v2 and v3 are all defined |

## The versions, all defined now

| | Phases | What it is |
|---|---|---|
| **v1** | P0 · P1 · P2 · P2-IN | The stock ledger and inventory control, end to end, on a standalone install — plus returns, printing, the India movement documents, and the dealer-parts and services adapters |
| **v1.1** | P3 | The warehouse floor: RF/handheld flows, tasks, waves, packing, the print server, dock, van stock |
| **v2** | P4 · P5 | India statutory filing, and 3PL: owner-of-goods billing, channels, full reverse logistics |
| **v3** | P6 | Optimisation, planning, GS1/EPCIS, automation — and the `logistics` module, whose acceptance is **zero commits to `warehouse-base`** |

## How this design set was produced

Seven independent `functional-reviewer` passes, run 2026-09-01/02 against the live `classic` checkout,
the in-flight `accounting` design set, and 28,928 lines of prior warehouse/supply-chain/TMS design art
found in `neetub1508/classic-issues`:

| Lens | Scope | Findings |
|---|---|---|
| **R1** codebase reality | What does the actual codebase require of a new module, and what already exists? | `C-001`…`C-050` |
| **R2** tier-1 WMS | Manhattan · Blue Yonder · SAP EWM · Oracle WMS Cloud · Körber · Infor · Softeon · Tecsys | `T-001`…`T-097` |
| **R3** ERP & mid-market | NetSuite · D365 · SAP B1 · Odoo · ERPNext · Zoho · Cin7 · Tally · Busy · Marg · and the DMS-parts column | `E-001`…`E-090` |
| **R4** fulfilment & 3PL | Extensiv · Logiwa · ShipHero · ShipBob · Increff · Unicommerce · 25 products | `F-001`…`F-093` |
| **R5** standards & statute | GS1/EPCIS · GST · e-way bill · pharma · food · hazmat · customs · Ind AS 2 · the ops surface | `S-001`…`S-098` |
| **R6** prior-art triage | 28,928 lines of earlier design, 80 tables of DDL, triaged KEEP/ADAPT/CONTRADICTED/OBSOLETE | `P-001`…`P-060` |
| **R7** logistics seam | The warehouse↔logistics↔supply-chain boundary, the adapter contract, the open registries | `G-001`…`G-086` |

**575 findings.** Their disposition — every one traced to a task, a decision, or an honest
`NEEDS-TASK` row — is [`docs/GAP-REGISTER.md`](docs/GAP-REGISTER.md).

## Status

| | |
|---|---|
| Requirements | **459** `FR-001`…`FR-459`, each carrying its module, version, phase and the findings it closes |
| Data model | **317 tables** across five modules, with the split proof and the migration allocation |
| Scenarios | **300** `WH-SC-nnn` — the acceptance criteria, in Given/When/Then |
| Screens | **237** build blocks, each naming its canonical reference page, gridIdentifier, filter scope, caches and permissions |
| Backlog | **143 tasks** in 8 phases, plus 8 phase epics and a master epic |
| Integrity | `tools/check-design-set.py` — 13 checks, run in CI |
| Prior art | earlier warehouse/supply-chain design exists in `neetub1508/classic-issues`. It is **input, not gospel** — every premise was re-verified and eleven were found false. See [`docs/reviews/R6-prior-art-triage.md`](docs/reviews/R6-prior-art-triage.md). That repository is not modified by this one |
| Code | none |

> **The `.md` files in this repository are authoritative.** GitHub issue bodies are a mirror, kept in
> sync mechanically by `issues/create-issues.sh --sync`; `--check` fails CI on drift. Never edit an
> issue body in the GitHub UI.
