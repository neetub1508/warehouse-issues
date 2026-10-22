TITLE: [Warehouse] EPIC: P10 — Manufacturing (warehouse-manufacturing)
LABELS: epic,warehouse,phase-p10
issue: TBD
---
Part of __MASTER__ · Module `warehouse-manufacturing` (`ai.warehousemanufacturing`, band **V560000–V569999**, prefix **`whm_`**) · Migrations — **24 blocks in band + one `warehouse-india` block, enumerated below** · Depends on **`P7`** (removal first) and **`P8`** (`p8-01`, `p8-02`, `p8-03`, `p8-06`, `p8-09`, `p8-10`, `p8-11` hard; `p8-16` for SEAM-M3) and **`P9`** (`p9-04`, `p9-07`, optional at runtime) · Runs in parallel with **`P9`** until p10-12 — the module **may ship before trade**: with trade off, MRP BUY output becomes a draft core PO (`OD-41` fallback)

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
- **Maker ≠ checker** on BOM approval, receipt reversal, over-threshold scrap and over-threshold settlement.
- **House-owned supply only** in MRP and valuation; non-own stock never valued (`L-14`).
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
| `V560060` · `V561060` | operation confirmations · permissions, leaf | p10-08 |
| `V560070` · `V561070` | settlements + lines · permissions, leaf | p10-09 |
| `V560080` · `V561080` | subcontract dispatches + lines, reconciliations · permissions, leaf | p10-10 |
| **`V540190`** (`warehouse-india`) | job-work processed-form return + scrap on dispatch lines (SEAM-M5) | p10-10 |
| `V560090` · `V561090` | item planning parameters, demand plans + lines · permissions, leaves | p10-11 |
| `V560100` · `V561100` | MRP runs, proposals, pegging, exceptions · permissions, leaves | p10-12 |
| `V561110` | report grids (capacity load, registers) — no table · permissions, leaves | p10-13 |

**Collision check (2026-10-22):** no `V56xxxx` file exists in `classic/warehouse*/backend` and no other
`issues/*.md` claims a version in `V560000–V569999`. The FRD-MFG migration map names **`V540150`** for the
india seam, but `V540150__Create_whin_approval_dispatches_and_approval_clocks.sql` already exists (`p4-06`,
`WIN-18`); this phase uses **`V540190`** (free in code and in every issue) — SPINE to correct FRD-MFG §3
row `V560080` and SEAM-M5.

## Tasks

| Task | Title | Depends on |
|---|---|---|
| [`p10-01`](p10-01.md) | Module bootstrap — scaffold, flag, menu tree, settings, the 22 applicable platform touchpoints | `p8-01`, `p8-02`, `p8-03`, `p8-06`, `p8-09`, `p8-10`, `p8-11`, `p8-16` |
| [`p10-02`](p10-02.md) | Manufacturing registries under the `RL-003` guard | p10-01 |
| [`p10-03`](p10-03.md) | BOM — versions, alternates, phantoms, co-/by-products, maker–checker, explosion, where-used, roll-up | p10-02 |
| [`p10-04`](p10-04.md) | Work centres and BOM operations | p10-03 |
| [`p10-05`](p10-05.md) | Production order — snapshot, lifecycle, release, reservations, MTO link, traveller | p10-04, `p8-02`, `p8-09` |
| [`p10-06`](p10-06.md) | Staging, issue through core, return, substitution, consumption policy | p10-05, `p8-09`, `p8-10`, `p8-11` |
| [`p10-07`](p10-07.md) | Production receipt — backflush, scrap, tolerances, genealogy, reversal, FG note | p10-06 |
| [`p10-08`](p10-08.md) | Operation confirmations, final / in-process QC, rework | p10-07, `p8-06` |
| [`p10-09`](p10-09.md) | Costing, co-product split, settlement, close, cost sheet | p10-07, p10-08 |
| [`p10-10`](p10-10.md) | Subcontracting / job work + india `V540190` seam (SEAM-M5) | p10-07, p10-09, `p8-03`, `p9-07` (ref only) |
| [`p10-11`](p10-11.md) | Planning masters — item planning parameters, demand plans | p10-03 |
| [`p10-12`](p10-12.md) | MRP — run, netting, lot sizing, proposals, pegging, conversion, exceptions | p10-05, p10-11, `p8-01`, `p8-02`, `p8-16`, `p9-04` (runtime) |
| [`p10-13`](p10-13.md) | Capacity load and manufacturing registers | p10-04, p10-09, p10-12 |

Parallel lanes after p10-04: {p10-05 → p10-06 → p10-07 → {p10-08 → p10-09 → p10-10}}, {p10-11}; p10-12
joins after p10-05 and p10-11; p10-13 last. Shared-registry edits (`filterUtils.ts`,
`CacheConfiguration.java`, `WarehouseManufacturingSafeTranslation.tsx`, i18n) serialize at the barrier.

## Dependencies outside the phase

| Task | What P10 needs from it |
|---|---|
| `p8-01` | PO schedule lines + open quantity — MRP supply (FR-664) |
| `p8-02` | `WhDemandOrderPort` + `FORECAST` schedule lines — MTO link (FR-637) and MRP independent demand (`OD-32` confirmed) |
| `p8-03` | Returnable gate pass for the generic subcontract dispatch (FR-659); gate entry on the return (FR-661) |
| `p8-06` | Polymorphic QC source, `onDisposition`, **SEAM-M4** non-stock-bearing sources (FR-652) |
| `p8-09` | `WhMaterialRequisitionPort`, `CostObjectResolver` + **SEAM-M1** counter purpose + **SEAM-M2** hooks (FR-640, FR-641, FR-643) |
| `p8-10` | Store issue with cost object `PRODUCTION_ORDER` landing in `VIRT-PRODUCTION` (FR-640) |
| `p8-11` | Store return from the same counter purpose (FR-641) |
| `p8-16` | **SEAM-M3** external replenishment-suggestion port, origin `MRP` (FR-666, `OD-31`/`OD-41`/`OD-44`) |
| `p9-04` | Trade turns an `MRP` suggestion into a PR (FR-557) — runtime only, no compile dependency |
| `p9-07` | Service PO reference frozen on a subcontract order (FR-658) and suggestion reference on the PO line (`OD-44`) — runtime only |

## Seams owed by other areas (MFG cannot ship them; each is a dependency, not a workaround — FRD-MFG §3.2)

| Seam | Owner | Needed change | Blocks |
|---|---|---|---|
| **SEAM-M1** | `p8-09` / `p8-10` (`p8-11` returns) | `ResolvedCostObject.counterLocationPurpose` (default `CONSUMED`; `PRODUCTION_ORDER` → `PRODUCTION`) used by the store-issue post | p10-06, p10-09 |
| **SEAM-M2** | `p8-09` / `p8-10` / `p8-11` | `CostObjectResolver` hooks `onIssuePosted`, `onIssueReversed`, `onReturnPosted`, `assertIssuable` in the posting transaction | p10-06 |
| **SEAM-M3** | `p8-16` (FRD-MFG §3.2 still says "new `p8-15` or `p8-14`" — `p8-15` is the RMA port) | `WhReplenishmentSuggestionPort.publishExternal/withdrawExternal`, `origin` + `origin_document_type/id` on `wh_replenishment_suggestions` | p10-12 |
| **SEAM-M4** | `p8-06` | `InspectableSource.stockBearing`; record-only ACCEPT/REJECT/REWORK when `false` | p10-08, p10-07 |
| **SEAM-M5** | core `ai.warehouse.port.jobwork.JobWorkDispatchPort` + `warehouse-india` bean — **owned inside p10-10** as a cross-module change (india migration `V540190`) | `registerDispatch`, `registerReturn(returnedAsItemId, consumedInputQty, scrapQty, scrapRetained)` | p10-10 |

## Admin settings seeded by P10 (all in `V561000`, FRD-MFG §8)

`release_requires_approval` (false) · `release_with_shortage` (WARN) · `component_reservation` (HARD) ·
`consumption_policy_default` (WARN) · `consumption_tolerance_percent` (0) · `over_receipt_percent` (0) ·
`under_receipt_percent` (0) · `scrap_value_approval_threshold` (null) · `close_variance_approval_percent`
(5) · `rework_keeps_lot` (true) · `block_receipt_on_open_inprocess_qc` (false) · `staging_stale_days` (7) ·
`mrp.horizon_days` (90) · `mrp.suggestion_cover_days` (30) — all prefixed `warehouse.manufacturing.`;
`admin_settings.description` ≤ 255 characters.

## Open decisions this phase carries

`OD-40` actual costing with settlement (default adopted) · `OD-41` trade off → core draft PO from an MRP
suggestion · `OD-42` job work **in** — v1.1, non-own owner never valued · `OD-43` labour/overhead recorded,
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
- [ ] The exit criterion's ten steps pass in order on a clean database (and steps 8–9 again with india and trade on)
- [ ] FRD-MFG §13 traceability: every FR-620…FR-669 closed by a merged task; every WH-SC-600…659 cited in a test name
- [ ] The eight `mfg-*` contracts exist and every row is implemented or refused
- [ ] `OD-40`…`OD-44` resolved or their defaults ratified in `DECISIONS.md` by SPINE; the `V540150` → `V540190` correction made in FRD-MFG
- [ ] No mobile; no accounting posting
