TITLE: [Warehouse] EPIC: P10 — Manufacturing (warehouse-manufacturing)
LABELS: epic,warehouse,phase-p10
issue: 548
---
Part of __MASTER__ · Module `warehouse-manufacturing` (`ai.warehousemanufacturing`, band **V560000–V569999**, prefix **`whm_`**) · Migrations — **61 blocks in band (25 + 36 added by R32) + six `warehouse-india` blocks (`V540190`…`V540193`, `V541160`, `V541161`), enumerated below** · Depends on **`P7`** (removal first) and **`P8`** (`p8-01`, `p8-02`, `p8-03`, `p8-06`, `p8-09`, `p8-10`, `p8-11` hard; `p8-16` for SEAM-M3) and **`P9`** (`p9-04`, `p9-07`, optional at runtime) · Ships in **v1.1** with the P8 seams it consumes (MD-38, R29 F24) · Runs in parallel with **`P9`** until p10-12 — the module **may ship before trade**: with trade off, MRP BUY output becomes a draft core PO (`OD-41` fallback)

## Overview

**Production through the warehouse, owning no ledger.** R28 group C found the build has kits and a
single-movement VAS work order and nothing a manufacturer runs on (`RN-030`…`RN-036`); `p6-12` had refused
multi-level BOMs. `D-16` / `RN-053` reverses that refusal (`RN-032`) in one switchable sibling:

```
BOM (multi-level, versioned, alternates, phantoms, co-/by-products) ── maker–checker ── explosion / where-used / roll-up
  → MRP (regenerative per site: demand orders + FORECAST lines + demand plan + MRQs, house-owned supply)
      → MAKE proposal → PLANNED production order (BOM snapshot)        → BUY proposal → core suggestion (origin MRP)
  → release (shortage list, reservations)                                  → trade PR (p9-04) | core draft PO (trade off)
  → request materials → core MRQ (p8-09) → core store issue (p8-10) into VIRT-PRODUCTION
  → staging list → LINE_SIDE (PRODUCTION_STAGE) · operation confirmations · in-process QC (non-stock)
  → production receipt: backflush + outputs + scrap in ONE movement · genealogy · final QC (p8-06) · rework order
  → subcontract: dispatch to job worker (gate pass p8-03 | india challan, SEAM-M5) → processed-item receipt → reconciliation
  → close = settlement (one value-only movement) · cost sheet · registers · capacity load (infinite)
```

Requirements, data model, state machines, screens, settings, decisions, open decisions, refusals and
scenarios: **[`docs/frd/FRD-MFG.md`](../docs/frd/FRD-MFG.md)**. Contracts (one per workflow, owed by MFG,
cited by each task): `mfg-bom`, `mfg-production-order`, `mfg-material-staging-issue`,
`mfg-production-receipt`, `mfg-qc-rework`, `mfg-costing-close`, `mfg-subcontracting`, `mfg-mrp`
(`docs/contracts/`).

**What P10 deliberately does not do** (FRD-MFG §10, fourteen refusals): no finite scheduling / APS, no
labour or OEE, no net-change or multi-site MRP, no standard costing, no failed-backflush queue, no unbuild,
no ECO workflow, no configurable BOMs, no process-manufacturing eBMR, no automatic MTO order creation, no
tool life, **no mobile**, and **no GL posting, debit or credit note** (accounting deferred, `RN-054`).

## Exit criterion — a Mode-D-plus install: platform + `warehouse-base` + `warehouse` + `warehouse-manufacturing` (then + `warehouse-trade`, + `warehouse-india`)

**Exit criterion: a discrete pump (`PUMP-100`, FRD-MFG §12 cast) and a batch resin (`RESIN-A` + co-product
`RESIN-B` + by-product `SOLVENT-REC`) each run end to end — BOM → MRP → order → material → receipt → QC →
close.** Run in order on a clean database:
1. Manufacturing **off** — no `whm_` object, no menu, core unchanged (p10-01 acceptance).
2. Manufacturing on — `V560000` asserts the core contract; registries guarded (`RL-003`).
3. **`WH-SC-600` → `WH-SC-602` → `WH-SC-604` → `WH-SC-606` → `WH-SC-609`** — BOM approval, effectivity, recursion refusal, explosion, scrap + fixed quantity.
4. **`WH-SC-610` → `WH-SC-616` → `WH-SC-618` → `WH-SC-620` → `WH-SC-623`** — release with shortage, MTO link, staging, MRQ → store issue into WIP, substitution.
5. **`WH-SC-625` → `WH-SC-626` → `WH-SC-627` → `WH-SC-630` → `WH-SC-633` → `WH-SC-634`** — receipt, backflush shortage refuses, completion, scrap, genealogy, reversal.
6. **`WH-SC-636` → `WH-SC-638`** — final QC with `REWORK`, rework order.
7. **`WH-SC-639` → `WH-SC-640` → `WH-SC-641`** — absorption, exact co-product split, settlement at close (`WH-SC-632` + `WH-SC-640` are the resin batch: expiry capped by the consumed lot, Σ split exact).
8. **`WH-SC-645` → `WH-SC-647` → `WH-SC-648`** — subcontract dispatch, processed-item receipt, reconciliation (`WH-SC-646`/`647` again with india on).
9. **`WH-SC-650` → `WH-SC-654` → `WH-SC-655` → `WH-SC-656` → `WH-SC-658`** — MRP run, MAKE conversion, BUY with trade on and off, concurrency.
10. **`WH-SC-659`** — capacity load; and an AUDITOR reads every MFG screen and exports nothing.
11. India on: **`WH-SC-680` → `WH-SC-682` → `WH-SC-683` → `WH-SC-686` → `WH-SC-687`** — MOOWR stock issued to the order, output received in bond with scrap as a bonded loss, bonded job work under permission, the MOOWR return, and a non-production exit still refused (`p10-14`, `D-17` item 3).

## The invariants and properties this phase establishes

- **MFG writes no position directly** — every stock effect is `WhbStockLedgerWriter.post` or a core
  document (store issue / store return); MFG owns no ledger (FRD-MFG §1).
- **One posting document, one movement** (MD-03, §5): staging action, receipt, settlement, dispatch each
  post exactly one movement with key `<DOCTYPE>:<id>`, balanced per `(owner, item, lot, serial, duty status)`
  (`I-1`); a `POSTED` row with a null `movement_id` is refused by a deferred trigger. Correction is
  reversal (`L-3`), never edit. The VAS work order is **not** widened (`RN-033`).
- **FKs point down only** (`FR-620`) and **no sibling imports** — india and trade reached only through
  core-defined ports with optional beans; proved by `ArchitectureInvariantsTest`.
- **Every vocabulary is a code list; no status `CHECK`** (`D-10`); every MFG seed carries the `RL-003`
  owning-module guard.
- **A BOM change never alters an existing order** (FR-633); **an approved BOM is immutable** (FR-625).
- **Maker ≠ checker** on BOM approval, release (when configured), receipt reversal, over-threshold scrap,
  over-threshold settlement and subcontract write-off; self-approval is `403 <DOC>_SELF_APPROVAL` (MD-21).
- **`COMPLETED` is not settled** (MD-14): late store issues and returns flow until `CLOSED`; an order with a
  posting is never cancelled (MD-15); the order alone owns its component reservations (MD-16).
- **House-owned supply only** in MRP and valuation; non-own stock never valued (`L-14`).
- **WIP is MFG's record** (MD-32, MD-34): virtual lines carry no cost layer, so the order's pool — issues, backflush,
  subcontract dispatches — lives on MFG rows; every output states its `extendedCost`; the settlement restates layers on
  the landed-cost path. No warehouse-base change.
- **MFG movement types post only from their MFG document** — MFG's `WhbMovementPostGuard` (MD-35).
- **Accounting is a handover, never a posting** (FR-657).

## Migration blocks

```bash
# from the warehouse-issues repo root
grep -h '^Part of __P10__' issues/p10-*.md | sed 's/.*Migrations \*\*//; s/ · Screens.*//'
```

That command is the authority; re-run it after any header change.

| Block | Content | Task |
|---|---|---|
| `V560000` | bootstrap — core-contract assertion, no table | p10-01 |
| `V561000` | L1 *Manufacturing*, three L2 sections, settings registry (§8), source system | p10-01 |
| `V560001` | registries: movement / document / location types, code lists, reasons, `REWORK`, print kinds, series | p10-02 |
| `V560010` · `V561010` | BOM headers, lines, alternates, outputs + grid · permissions, leaves | p10-03 |
| `V560020` · `V561020` | work centres, BOM operations · permissions, leaf | p10-04 |
| `V560030` · `V561030` | production orders, components, outputs, operations, events · permissions, leaf | p10-05 |
| `V560040` · `V561040` | staging lists + lines, component substitutions · permissions, leaf | p10-06 |
| `V560050` · `V561050` | production receipts, outputs (+ serials), consumptions, reversals · permissions, leaves | p10-07 |
| **`V540193`** · **`V541161`** (`warehouse-india`) | Legal Metrology declarations, MRP revisions + grids · permissions, leaf (R30 `CP-GA-006`) | p10-07 |
| `V560060` · `V561060` | operation confirmations · permissions, leaf | p10-08 |
| `V560070` · `V561070` | settlements + lines · permissions, leaf | p10-09 |
| `V560080` · `V561080` | subcontract dispatches + lines, reconciliations, reconciliation actions (recall / write-off) · permissions, leaf | p10-10 |
| **`V540190`** (`warehouse-india`) | job-work processed-form return, scrap, return reversal and loss on job-work lines (SEAM-M5, MD-25) | p10-10 |
| `V560090` · `V561090` | item planning parameters, demand plans + lines · permissions, leaves | p10-11 |
| `V560100` · `V561100` | MRP runs, proposals, pegging, exceptions · permissions, leaves | p10-12 |
| `V561110` | report grids (capacity load, registers) — no table · permissions, leaves | p10-13 |
| `V560120` | `whm_production_orders.bonded_duty_status`, `whm_subcontract_dispatches.bond_permission_ref` | p10-14 |
| **`V540191`** · **`V540192`** · **`V541160`** (`warehouse-india`) | bond rules registry + bond register of operations + grid · MOOWR returns + lines, SEZ movements · permissions, leaves, compliance rule (`D-17` item 3) | p10-14 |
| `V562001` | R32 registries (FR-835) | p10-02 |
| `V563000` | R32 L2 sections *Engineering*, *Shop Floor*, *Quality & Units*; R32 settings; personas (FR-834) | p10-01 |
| `V562005` · `V563005` | machines + work-centre rate columns · permissions | p10-04 |
| `V562010` · `V563010` | operations, routings, routing operations + grids · permissions, leaves | p10-16 |
| `V562020` · `V563020` | shifts, operators, authorisations, work-centre shifts + grids · permissions, leaves | p10-15 |
| `V562030` · `V563030` | ECNs + lines + dispositions · permissions, leaf | p10-17 |
| `V562040` · `V563040` | drawings, revisions, issue log · permissions, leaf | p10-18 |
| `V562050` · `V563050` | sample requests, iterations · permissions, leaf | p10-19 |
| `V562060` · `V563060` | production batches, job cards, events, confirmation operators + confirmation columns · permissions, leaves | p10-20 |
| `V562070` · `V563070` | unit serial series, unit serials, part bindings · permissions, leaf | p10-21 |
| `V562080` · `V563080` | PDI order points, records, certificates · permissions, leaf, print template | p10-22 |
| `V562090` · `V563090` | unit registry, part replacements, type approvals · permissions, leaves, `FORM_22` | p10-23 |
| `V562100` · `V563100` | daily plans + lines · board grid, permissions, leaves | p10-24 |
| `V562110` · `V563110` | cost estimates · permissions, leaf | p10-25 |
| `V562120` · `V563120` | tools, routing-operation tools, tool life, maintenance plans + orders, `whm_operation_confirmations.tool_id` · permissions, leaves | p10-26 |
| `V562200` · `V563200` | product variants, variant applicability + BOM columns · import / compare permissions | p10-03 |
| `V562220` · `V563220` | production-order demands + order / operation columns · approve permissions | p10-05 |
| `V562240` | receipt batch / unit-serial columns — no table | p10-07 |
| `V562260` | order conversion costs | p10-09 |
| `V562280` | production-parameter columns — no table | p10-11 |
| `V563290` | R32 register report grids — no table | p10-13 |

**Collision check (2026-10-22):** no `V56xxxx` file exists in `classic/warehouse*/backend` and no other
`issues/*.md` claims a version in `V560000–V569999`. The india seam is **`V540190`** (free in code and in
every issue; `V540150` is `p4-06`'s approval dispatches) — FRD-MFG §3 and SEAM-M5 carry it (MD-28).
**Re-checked 2026-10-23** for `p10-14`: `V540191`, `V540192`, `V541160` and `V560120` are in no file in `classic`
and claimed by no other issue (the last india files are `V540184` and `V541159`). Same check for `p10-07`'s `V540193` and `V541161`: free.

## Tasks

__TASKS__

| Task | Title | Depends on |
|---|---|---|
| [`p10-01`](p10-01.md) | Module bootstrap — scaffold, flag, menu tree, settings, the 22 applicable platform touchpoints | `p8-01`, `p8-02`, `p8-03`, `p8-06`, `p8-09`, `p8-10`, `p8-11`, `p8-16` |
| [`p10-02`](p10-02.md) | Manufacturing registries under the `RL-003` guard | p10-01 |
| [`p10-03`](p10-03.md) | BOM — versions, alternates, phantoms, co-/by-products, maker–checker, explosion, where-used, roll-up | p10-02 |
| [`p10-04`](p10-04.md) | Work centres and BOM operations | p10-03 |
| [`p10-05`](p10-05.md) | Production order — snapshot, lifecycle, release, reservations, MTO link, traveller | p10-04, `p8-02`, `p8-09` |
| [`p10-06`](p10-06.md) | Staging, issue through core, return, substitution, consumption policy | p10-05, `p8-09`, `p8-10`, `p8-11` |
| [`p10-07`](p10-07.md) | Production receipt — backflush, scrap, tolerances, genealogy, reversal, FG note, **per-receipt absorption and exact split** (MD-37) | p10-06 |
| [`p10-08`](p10-08.md) | Operation confirmations, final / in-process QC, rework | p10-07, `p8-06` |
| [`p10-09`](p10-09.md) | Settlement (landed-cost restatement path), close, cost sheet | p10-07, p10-08 |
| [`p10-10`](p10-10.md) | Subcontracting / job work + india `V540190` seam (SEAM-M5) | p10-07, p10-09, `p8-03`, `p9-07` (the trade subcontract PO, D-18 item 3) |
| [`p10-11`](p10-11.md) | Planning masters — item planning parameters, demand plans | p10-03 |
| [`p10-12`](p10-12.md) | MRP — run, netting, lot sizing, proposals, pegging, conversion, exceptions | p10-05, p10-11, `p8-01`, `p8-02`, `p8-16`, `p9-04` (runtime) |
| [`p10-13`](p10-13.md) | Capacity load and manufacturing registers | p10-04, p10-09, p10-12 |
| [`p10-14`](p10-14.md) | Bonded / MOOWR stock to production and to a job worker — bond rules, bond register, output in bond, MOOWR return, SEZ lines (`D-17` item 3) | p10-06, p10-07, p10-10, india `p4-07` |
| [`p10-15`](p10-15.md) | Operators, skills and shifts (R32) | p10-04, p10-16 |
| [`p10-16`](p10-16.md) | Operation master and routing master (R32, `D-20` item 17) | p10-03, p10-04, `p8-30` |
| [`p10-17`](p10-17.md) | Engineering change notice (R32, `D-20` item 1) | p10-16, p10-05, `p8-30` |
| [`p10-18`](p10-18.md) | Drawings — revisions, port, controlled copies, issue log (R32) | p10-02, `p8-30` |
| [`p10-19`](p10-19.md) | Samples — requests, SAMPLE orders, iterations, approval (R32) | p10-05, p10-18, `p8-22` |
| [`p10-20`](p10-20.md) | Production batches and job cards (R32) | p10-06, p10-10, p10-15, p10-16 |
| [`p10-21`](p10-21.md) | Unit serials and as-built binding (R32) | p10-11, p10-20 |
| [`p10-22`](p10-22.md) | PDI gate per vehicle (R32) | p10-07, p10-08, p10-21, `p8-06`, `p8-19` |
| [`p10-23`](p10-23.md) | Manufacturer unit registry, traceability, Form 22 / VAHAN (R32, `D-20` item 4) | p10-22 |
| [`p10-24`](p10-24.md) | Production board and daily plans (R32) | p10-20 |
| [`p10-25`](p10-25.md) | Pre-sale cost estimate service (R32) | p10-09, p10-16 |
| [`p10-26`](p10-26.md) | Tooling / die master and preventive maintenance (R32) | p10-20 |

Parallel lanes after p10-04: {p10-05 → p10-06 → p10-07 → {p10-08 → p10-09 → p10-10}}, {p10-11}; p10-12
joins after p10-05 and p10-11; p10-13 last; p10-14 after p10-10 (parallel with p10-11…p10-13). Shared-registry edits (`filterUtils.ts`,
`CacheConfiguration.java`, `WarehouseManufacturingSafeTranslation.tsx`, i18n) serialize at the barrier.

**R32 build order (`D-20`):** p10-04 (`V562005`) → p10-16 (`V562010`) → p10-15 (`V562020`) → {p10-17, p10-18 → p10-19}; p10-20 after p10-15 / p10-16 / p10-06 / p10-10 → p10-21 → p10-22 → p10-23; p10-24, p10-26 after p10-20; p10-25 after p10-09 and p10-16. The R32 amendment sections of p10-01…p10-13 ride with their task (or, when that task is closed, its own follow-up).

## Dependencies outside the phase

| Task | What P10 needs from it |
|---|---|
| `p8-01` | PO schedule lines + open quantity — MRP supply (FR-664) |
| `p8-02` | `WhDemandOrderPort` + `FORECAST` schedule lines — MTO link (FR-637) and MRP independent demand (`OD-32` confirmed) |
| `p8-03` | Returnable gate pass for the generic subcontract dispatch (FR-659); gate entry on the return (FR-661) |
| `p8-06` | Polymorphic QC source, `onDisposition`, **SEAM-M4** non-stock-bearing sources (FR-652) |
| `p8-09` | `WhMaterialRequisitionPort` (`FRD-STORES` `FR-531`), `CostObjectResolver` + **SEAM-M1** counter purpose + **SEAM-M2** hooks + `reservationsFor`; the resolver admits `COMPLETED` orders (`FR-533`, amended for MD-14/MD-16) (FR-640, FR-641, FR-643) |
| `p8-10` | Store issue with cost object `PRODUCTION_ORDER` landing in `VIRT-PRODUCTION` (FR-640) |
| `p8-11` | Store return from the same counter purpose (FR-641) |
| `p8-16` | **SEAM-M3** external replenishment-suggestion port, origin `MRP` (FR-666, `OD-31`/`OD-41`/`OD-44`) |
| `p9-04` | Trade turns an `MRP` suggestion into a PR (FR-557) — runtime only, no compile dependency |
| `p9-07` | The warehouse-trade subcontract PO (FRD-TRADE FR-682…689, **SEAM-M7**: R9 lifted for a service line linked to a subcontract order; it lands the processing charge — D-18 item 3) and suggestion reference on the PO line (`OD-44`) — runtime only |

## Seams owed by other areas (MFG cannot ship them; each is a dependency, not a workaround — FRD-MFG §3.2)

| Seam | Owner | Needed change | Blocks |
|---|---|---|---|
| **SEAM-M1** | `p8-09` / `p8-10` (`p8-11` returns) | `ResolvedCostObject.counterLocationPurpose` (default `CONSUMED`; `PRODUCTION_ORDER` → `PRODUCTION`) used by the store-issue post | p10-06, p10-09 |
| **SEAM-M2** | `p8-09` / `p8-10` / `p8-11` | `CostObjectResolver` hooks `assertIssuable`, `onIssuePosted`, `onReturnPosted` in the posting transaction + `reservationsFor` (MD-16); **no `onIssueReversed`** — rejected by STORES `STO-D13`, a mis-issue is a store return (MD-17) | p10-06 |
| **SEAM-M3** | `p8-16` (MD-28) | `WhReplenishmentSuggestionPort.publishExternal/withdrawExternal`, `origin` + `origin_document_type/id` on `wh_replenishment_suggestions` | p10-12 |
| **SEAM-M4** | `p8-06` | `QualityInspectionSourceResolver.stockBearing()` (FRD-STORES registry R.3); record-only ACCEPT/REJECT/REWORK when `false` | p10-08, p10-07 |
| **SEAM-M5** | core `ai.warehouse.port.jobwork.JobWorkDispatchPort` + `warehouse-india` bean — **owned inside p10-10** as a cross-module change (india migration `V540190`) | `registerDispatch`, `registerReturn(returnedAsItemId, consumedInputQty, scrapQty, scrapRetained)` (a recall is a return of the input), `reverseReturn`, `registerLoss` (MD-25) | p10-10 |
| **SEAM-M6** | `p0` base genealogy, carried in `p10-07` | `WhbGenealogyQueryService.trace` reads a `PRODUCTION_REVERSAL` transformation row as a cancel marker; no schema change (R31 F-MF-021) | p10-07 |
| **SEAM-M7** | `p9-07` (warehouse-trade) | the subcontract service-line PO (FRD-TRADE FR-682…689): trade owns the link `subcontract_order_id`, validated through MFG's `PRODUCTION_ORDER` resolver (`order_type`, `subcontractor_counterparty_id`), and lands the charge as a value-only `LANDED_COST_APPLY` (D-18 item 3, R31 F-MF-005) | p10-10 |

## Admin settings seeded by P10 (all in `V561000`, FRD-MFG §8)

`release_requires_approval` (false) · `release_with_shortage` (~~WARN~~ **APPROVE**, R32) · `component_reservation` (HARD) ·
`consumption_policy_default` (WARN) · `consumption_tolerance_percent` (0) · `over_receipt_percent` (0) ·
`under_receipt_percent` (0) · `scrap_value_approval_threshold` (null) · `close_variance_approval_percent`
(5) · `rework_keeps_lot` (true) · `block_receipt_on_open_inprocess_qc` (false) · `staging_stale_days` (7) ·
`mrp.horizon_days` (90) · `mrp.suggestion_cover_days` (30) — all prefixed `warehouse.manufacturing.`;
`admin_settings.description` ≤ 255 characters.

**R32 settings (in `V563000`, FRD-MFG §8 rows marked *R32*):** `bom.approval_levels` (2) · `bom.single_released_alternative` (false) · `ecn_required_for_released_change` (true) · `ecn.approval_levels` (2) · `drawing.revision_scheme` (ALPHA) · `drawing.uncontrolled_watermark_text` · `sample.dispatch_approval_required` (true) · `order_approval_mode` (MTS_ONLY) · `create_order_from_demand_line` (false) · `pqc_blocks_next_stage_default` (true) · `patrol_interval_units` (10) · `max_rework_cycles` (3) · `unit_serial.assign_at` (FIRST_STAGE) · `pdi_revalidate_days` (30) · `warranty_starts_at` (SALE) · `vahan_export_layout` · `costing.absorb_conversion` (true) · `costing.overhead_basis` (PER_HOUR) · `costing.overhead_percent` (0) · `adhoc_substitution_requires_deviation` (true) · `maintenance.overdue_mode` (WARN). **`release_with_shortage` default changes WARN → APPROVE** (`ALLOW` read as `WARN`, `D-20` item 12; the row is updated in `V563000`); `release_requires_approval` is superseded by `order_approval_mode`.

## Open decisions this phase carries

`OD-40` actual costing with settlement (default adopted) · `OD-41` trade off → core draft PO from an MRP
suggestion · `OD-42` job work **in** — v1.2, non-own owner never valued · `OD-43` labour/overhead recorded,
not absorbed · `OD-44` published MRP suggestion counts as supply for `suggestion_cover_days` (trade to
confirm the PO-line reference). Each has an adopted default (FRD-MFG §11). Also confirms TRADE `OD-31`
(MD-07) and `OD-32` (MD-08).

## Traps this phase must not walk into

- **Widening the VAS work order.** `wh_work_orders` keeps its one-terminal-movement trigger; the
  production order is a separate document (MD-02).
- **A second issue document.** Manual issue and return are core's (`p8-10`/`p8-11`); MFG never adds an
  issue slip (MD-04, `RM-022`).
- **Issue into `VIRT-CONSUMED`.** Without SEAM-M1 the order's WIP is expensed and the cost pool reads
  zero; p10-06 cannot ship before it.
- **Partial backflush.** A shortage refuses the whole post; there is no COGI queue (MD-10).
- **Sibling cross-imports.** MFG never imports `ai.warehouseindia` or `ai.warehousetrade`; it calls core
  ports whose beans may be absent.
- **Counting 3PL stock as supply** (`L-14`) or **valuing a non-own order**.
- **Accounting creep.** No debit/credit note, no GL account, no job-work charge invoice (R-14).
- **Mobile.** None — user rule 2026-09-11.
- **Docker only** for build and test; never a local `mvn` / `npm`.

## Definition of done

Per __MASTER__, with these phase-specific additions:

- [ ] Every task merged with reviewer + functional-reviewer clean against its contract rows
- [ ] The exit criterion's eleven steps pass in order on a clean database (and steps 8–9 again with india and trade on)
- [ ] FRD-MFG §13 traceability: every FR-620…FR-677 closed by a merged task; every WH-SC-600…659 and WH-SC-680…699 cited in a test name
- [ ] The nine `mfg-*` contracts (with `mfg-bonded-issue`) exist and every row is implemented or refused
- [ ] `OD-40`…`OD-44` resolved or their defaults ratified in `DECISIONS.md` by SPINE; MD-14…MD-43 (FRD-MFG §9) honoured by every task
- [ ] Every port call matches the FRD-STORES "Port & seam registry (authoritative)"; FRD-MFG "R29 dispositions" rows all closed
- [ ] No mobile; no accounting posting
