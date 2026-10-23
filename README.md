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

## Research and readiness reports

[Warehouse documents imported from Downloads](docs/reference/downloads-2026-10-01/README.md) — dated audit packs, comparisons and supporting evidence. Current implementation scope remains governed by the task sources and adopted decisions.

## What is being built

A **standalone-capable, country-neutral warehouse and inventory-management product for manufacturing
plant stores and storage** (`DECISIONS.md` `D-16`, 2026-10-22): raw material, consumables and spares
received against purchase, issued to departments and production, finished goods received from
production and despatched against sales, and storage sold to third parties. It is built on one
immutable, double-sided, append-only stock ledger at full grain, the application layers that write to
it, and a generic inbound movement port so that any number of future consumers — a logistics/TMS
module, a supply-chain module, or any vertical in the suite — can move stock **without
`warehouse-base` ever depending on them**.

It has nothing to do with the `dealer` module and is a different product from it. **Dealer and
retail/e-commerce features are removed from warehouse, not extracted** (`RN-050`, `RN-051`): no
dealer-parts or services-job-parts adapter, no channels, marketplaces, AWB pools, NDR, COD or RTO.
Generic shipping — carriers, labels, manifests, consignments, tracking events, RMAs — stays in core.

It is the first real stock ledger in this suite.

```
platform                                V0      – V999      (exists)
 └── warehouse-base                     V500000 – V509999   v1
     │   the stock ledger and its masters
     │   items · variants · UoM & conversions · barcodes
     │   sites · zones · locations · lots · serials · LPNs
     │   owners · counterparties · the open catalogues
     │   movements · positions · reservations · cost layers
     │   the generic inbound movement port · the outbox
     │
     ├── warehouse                      V510000 – V519999   v1 · v1.1 · v2
     │   the application on top of the ledger
     │   inbound: ASN · receiving · QC · putaway · cross-dock
     │   outbound: allocation · waves · pick · pack · ship
     │   transfers · adjustments · counts · replenishment
     │   valuation & costing · returns · printing · kitting
     │   stores (P8): gate entry · GRN with bill fields
     │   sampling QC · MRN · material requisition
     │   store issue to a cost object · store return
     │   the PO and sales demand-order creation ports
     │
     ├── warehouse-adapter-<vertical>   V520000 – V529999
     │   dealer    V520000 – V520999   REMOVED 2026-09-21, band reserved
     │   services  V521000 – V521999   REMOVED 2026-09-21, band reserved
     │   field-service V522000 · assets V523000   not scheduled
     │   example   V525000 – V525999   CI-only fixture
     │
     ├── warehouse-3pl                  V530000 – V539999   v2
     │   owner-of-goods billing · rate cards · the billable-event
     │   meter · storage algorithms · the client portal
     │
     ├── warehouse-india                V540000 – V549999   v1 + v2
     │   wave 1 — the documents goods cannot legally move without
     │   wave 2 — the statutory registers and filings · job work
     │
     ├── warehouse-trade                V550000 – V559999   NEW   P9   ai.warehousetrade · wht_
     │   purchase and sales, mirrored row for row, one toggle
     │   PR / enquiry → RFQ / quotation → award → rate contract
     │   fixed · open · blanket orders with delivery schedules
     │   releases · amendments · approval matrix
     │
     └── warehouse-manufacturing        V560000 – V569999   NEW   P10  ai.warehousemanufacturing · whm_
         multi-level BOM · production order · issue to WIP
         backflush · FG + co-product receipt · in-process and
         final QC · subcontracting · MRP · costing and close
```

`warehouse-base` depends on **platform only**. It has zero compile-time dependency on any vertical and
never reads another module's tables. `warehouse-trade` and `warehouse-manufacturing` reach core stock
only through the `P8` ports. Every foreign key between the modules points *downward* — proven, table
by table, in [`docs/DATA-MODEL.md`](docs/DATA-MODEL.md) §3. Accounting is **deferred** (`RN-054`): no
phase generates a debit or credit note. No phase has a mobile screen.

## The decisions that shape everything

The full set is [`docs/DECISIONS.md`](docs/DECISIONS.md) — `D-1`…`D-16`. The six a reader will
otherwise re-litigate:

| | |
|---|---|
| **D-1** | **Five modules, not four.** The brief's four carry a *vertical* axis and no *jurisdiction* axis, so `warehouse-india` exists — the same call accounting took. `D-16` adds `warehouse-trade` and `warehouse-manufacturing` beside them |
| **D-2** | **Flyway bands are V500000–V569999, not V900000+.** The bands originally proposed are already occupied by **1,061 existing `.sql` files** (dealer OEM seed and platform per-client migrations), and a collision there does not fail loudly — it silently deletes a history row. The removed dealer and services adapter bands `V520000`–`V521999` stay reserved and are never reused |
| **D-5** | **`owner_id` is `NOT NULL` in v1, in every install.** `warehouse-3pl` ships in v2; the column cannot. No rule recovers whose a unit was, so it is free now and unbackfillable later — without it, 3PL is not a module, it is a rewrite |
| **D-6** | **Whichever system is authoritative for quantity is authoritative for cost.** Warehouse owns the movement, the position and the costing engine; accounting always owns the ledger and does not re-cost what it is handed |
| **D-12** | **v1 is a cut line, not the scope limit.** Every capability found by any lens is placed in a version and carried in a task **now** — v1, v1.1, v2 and v3 are all defined |
| **D-16** | **Re-targeted to manufacturing + storage; dealer and retail code are removed.** It overrides every earlier document where they assume a dealer or retail target. Removed features are deleted, mixed migrations rewritten, and the dev database rebuilt **once** — no drop migrations, no shims (`RN-052`). Dual-use items are renamed: `VOR` → line-stop / machine-down, `WORKSHOP` → production store, `OEM_PART_NUMBER` → manufacturer part no. Purchase and sales go to `warehouse-trade`, production to `warehouse-manufacturing` (`RN-053`) |

## The versions, all defined now

| | Phases | What it is |
|---|---|---|
| **v1** | P0 · P1 · P2 · P2-IN | The stock ledger and inventory control, end to end, on a standalone install — plus returns, printing and the India movement documents |
| **v1.1** | P3 | The warehouse floor: RF/handheld flows, tasks, waves, packing, the print server, dock, van stock |
| **v2** | P4 · P5 | India statutory filing, and 3PL: owner-of-goods billing, carrier integration, full reverse logistics |
| **v3** | P6 | Optimisation, planning, GS1/EPCIS, automation — and the `logistics` module, whose acceptance is **zero commits to `warehouse-base`** |
| **D-16** | P7 → P8 → {P9 ∥ P10} | **P7** removes the dealer and retail code, applies the renames and rebuilds the dev database once · **P8** the manufacturing stores additions in core `warehouse` · **P9** `warehouse-trade` · **P10** `warehouse-manufacturing`. P7 is a hard barrier before P8; P9 and P10 may run in parallel ([`IMPLEMENTATION-PLAN.md`](docs/IMPLEMENTATION-PLAN.md) §1.9) |

Seven P0–P6 tasks whose whole scope was dealer or retail are **VOID** (`P2-24`, `P2-25`, `P2-26`,
`P3-19`, `P5-12`, `P5-15`, `P6-09`); five more are partly void.

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

Later rounds, each with its own register:

| Round | Reviews | What it did |
|---|---|---|
| 2 | `R8`…`R15` | 62 findings — [`GAP-REGISTER-R2.md`](docs/GAP-REGISTER-R2.md) |
| 3 | `R16`…`R21` | 52 findings — [`GAP-REGISTER-R3.md`](docs/GAP-REGISTER-R3.md) |
| 4 | `R22`…`R26` | 83 findings — [`GAP-REGISTER-R4.md`](docs/GAP-REGISTER-R4.md), including `D-14`'s branch↔warehouse junction |
| **R27** | [client purchase-to-stores gap](docs/reviews/R27-client-p2p-stores-gap.md) | a client's manufacturing purchase-to-stores flow checked step by step against the built code — 36 `RM-` rows |
| **R28** | [manufacturing + storage re-target impact](docs/reviews/R28-manufacturing-storage-retarget-impact.md) | the dealer and retail footprint, the capability matrix and the decisions `RN-050`…`RN-054` (§8b, authoritative) behind `D-16`, plus the program plan (§8c) — 38 `RN-` rows |
| **R29** | dual-engine functional review (Claude + GPT) of the re-target areas: [rem](docs/reviews/R29-functional-review-rem.md) · [stores](docs/reviews/R29-functional-review-stores.md) · [trade-purchase](docs/reviews/R29-functional-review-trade-purchase.md) · [trade-sales](docs/reviews/R29-functional-review-trade-sales.md) · [mfg](docs/reviews/R29-functional-review-mfg.md) | **145 findings**, every one fixed and dispositioned in its area FRD and folded into the task that carries it |

Reviews R1–R26, the gap registers and `docs/competitive/` predate `D-16` and are historical where they
assume a dealer or retail target. Where the re-target stands is
[`docs/reviews/RETARGET-PROGRAM-STATUS.md`](docs/reviews/RETARGET-PROGRAM-STATUS.md).

## Status

| | |
|---|---|
| Requirements | **661** — **471** `FR-001`…`FR-471` in the main FRD (24 of them **WITHDRAWN by `D-16`**, kept for the record), plus **190** `FR-480`…`FR-669` in the area files [`docs/frd/`](docs/frd/): `FRD-REM` 20 · `FRD-STORES` 40 · `FRD-TRADE` 80 · `FRD-MFG` 50. Each carries its module, version, phase and the findings it closes |
| Data model | **486 tables** — `whb_` 132 · `wh_` 147 · `wht_` 75 · `whin_` 66 · `whm_` 34 · `wh3_` 26 · adapters 6 (the `whad_`/`whas_` tables are removed) — with the split proof and the migration allocation ([`DATA-MODEL.md`](docs/DATA-MODEL.md) §8.1) |
| Scenarios | **668** `WH-SC-nnn` — 411 in the catalogue and 257 in the area files — the acceptance criteria, in Given/When/Then |
| Screens | **327** build blocks — 255 in the build spec and 72 in the area files — each naming its canonical reference page, gridIdentifier, filter scope, caches and permissions |
| Contracts | **28** workflow contracts in [`docs/contracts/`](docs/contracts/) — 3 core, 7 stores, 10 trade, 8 manufacturing |
| Backlog | **200 tasks** in 12 phases — 144 in P0–P6 (7 VOID by `D-16`) and 56 in P7–P10 (P7 13 · P8 16 · P9 14 · P10 13) — plus 12 phase epics and a master epic. All filed; the re-target is EPICs **#545–#548** and tasks **#549–#604** ([`issues/CREATED.md`](issues/CREATED.md)) |
| Integrity | `tools/check-design-set.py` — 13 checks, run in CI, **0 violations** |
| Prior art | earlier warehouse/supply-chain design exists in `neetub1508/classic-issues`. It is **input, not gospel** — every premise was re-verified and eleven were found false. See [`docs/reviews/R6-prior-art-triage.md`](docs/reviews/R6-prior-art-triage.md). That repository is not modified by this one |
| Code | none here; the build runs in `classic` |

> **The `.md` files in this repository are authoritative.** GitHub issue bodies are a mirror, kept in
> sync mechanically by `issues/create-issues.sh --sync`; `--check` fails CI on drift. Never edit an
> issue body in the GitHub UI.
