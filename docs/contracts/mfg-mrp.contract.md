# Functional Contract — Planning masters, MRP runs, proposals, exceptions, capacity load (`warehouse-manufacturing`)

> **What this is.** The functional truth for item planning parameters (WS-331) and demand plans (WS-332),
> the regenerative per-site MRP run and its locking (WS-333), the netting rules, lot sizing, offsets and
> time fence, the proposal ladder with pegging and conversion — `MAKE` → `PLANNED` production order;
> `BUY` → core replenishment suggestion origin `MRP` (SEAM-M3, `OD-31`), which trade turns into a PR or,
> with trade off, core turns into a draft PO (`OD-41`); the `OD-44` cover rule (WS-334) — exception
> messages (WS-335) and the read-only capacity load (WS-336).
>
> **What this is not.** It does not restate the order ladder (`mfg-production-order.contract.md`), the PR
> conversion ([`trade-purchase-requisition.contract.md`](trade-purchase-requisition.contract.md), `TPR-*`),
> core replenishment (`V510070`) or the demand-order port (`p8-02`). MRP posts **no movement**.
>
> **Status.** Derived 2026-10-22 (v0), **not ratified**. No code exists. Authority: `docs/frd/FRD-MFG.md`.

---

## 0. Identity

| | |
|---|---|
| **Workflow** | Maintain planning params + demand plan → run MRP (site) → proposals + pegging + exceptions → planner firms / dismisses / converts → orders and suggestions become supply for the next run; capacity load read alongside |
| **Module** | `warehouse-manufacturing`. Reads core `p8-02` demand orders (incl. `FORECAST` schedule lines, `OD-32` **confirmed**), `p8-01` PO schedule lines, `p8-09` MRQs, base positions/reservations; writes core suggestions only through SEAM-M3 (`publishExternal`/`withdrawExternal`). No dependency on `warehouse-trade` (MD-07, MD-08) |
| **Domain baseline** | FRD-MFG FR-637, FR-662…FR-668, §8 (`mrp.horizon_days` 90, `mrp.suggestion_cover_days` 30), MD-07…MD-09, `OD-31`, `OD-32`, `OD-41`, `OD-44`, R-01, R-03, R-04, R-11 · `DECISIONS.md` `L-6`, `L-10`, `L-14` · `TPR-T1-02` |
| **Owning task bodies** | `p10-11` (planning masters), `p10-12` (MRP), `p10-13` (capacity load) — FRD §13; bodies not yet written. Needs SEAM-M3 (core replenishment) |
| **Primary tables** | `whm_item_planning_params`, `whm_demand_plans`, `_lines` (`V560090`); `whm_mrp_runs`, `whm_mrp_proposals`, `whm_mrp_pegging`, `whm_mrp_exceptions` (`V560100`); run via `whb_job_runs` |
| **Status columns** | demand plan `DRAFT`/`ACTIVE`/`ARCHIVED`; run `QUEUED`/`RUNNING`/`COMPLETED`/`FAILED`/`SUPERSEDED`; proposal `OPEN`/`FIRMED`/`CONVERTED`/`DISMISSED`/`SUPERSEDED` — no `CHECK` (`D-10`) |
| **Permission resources** | `whm_item_planning_params:{view,create,edit,delete,export}` · `whm_demand_plans:{view,create,edit,delete,export,activate}` · `whm_mrp_runs:{view,run,export}` · `whm_mrp_proposals:{view,firm,convert,dismiss,export}` · `whm_mrp_exceptions:{view,acknowledge,export}` · `whm_reports:{view,export}` (capacity load) |
| **Routes** | `/warehouse/manufacturing/planning-parameters` (WS-331), `/demand-plans` (WS-332), `/mrp-runs` (WS-333), `/mrp-proposals` (WS-334), `/mrp-exceptions` (WS-335), `/capacity-load` (WS-336) · **mobile: none** |
| **Contract status / version** | `derived 2026-10-22 (v0), not ratified` · `v0 — 2026-10-22` |

### Acceptance checks

| # | The requester expects… | Delivered by |
|---|---|---|
| A1 | LFL netting with lead-time offset, dependent demand exploded, BUY net of stock and PO lines, pegging to the SO (`WH-SC-650`) | `MRP-N-01`…`-10`, `MRP-T4-01` |
| A2 | `FIXED` lot 1,000 for a net need of 320 (`WH-SC-651`) | `MRP-N-11` |
| A3 | Non-own stock is never supply (`WH-SC-652`, `L-14`) | `MRP-N-06` |
| A4 | Demand plan `MAX` mode: 200, not 250 (`WH-SC-653`) | `MRP-N-03` |
| A5 | MAKE convert → `PLANNED` order with snapshot; child MAKE → linked child order (`WH-SC-654`) | `MRP-T1-13`, `MRP-T4-03` |
| A6 | BUY convert → core suggestion origin `MRP`; trade raises the PR; trade off → core draft PO, suggestion consumed, next run counts the PO (`WH-SC-655`, `WH-SC-656`) | `MRP-T1-14`, `MRP-T4-04`, `MRP-N-08` |
| A7 | Exceptions name document, current and suggested dates; never auto-applied (`WH-SC-657`, `WH-SC-617`) | `MRP-T1-17`, `MRP-X-*` |
| A8 | One run per site at a time; a completed run supersedes `OPEN` proposals (never published), `FIRMED` and `CONVERTED` stay; a converted BUY's unordered suggestion is supply for `suggestion_cover_days`, then withdrawn (MD-24, `WH-SC-658`) | `MRP-GRD-07`, `MRP-T1-08` |
| A9 | Capacity load buckets minutes per work centre per day vs capacity and flags overload, rescheduling nothing (`WH-SC-659`) | §5.1, `MRP-UNR-05` |

---

## 1. T1 — State machine

### 1.1 Status inventory

| Entity | Status | Represented by | Reachable via | Exits via | Kind |
|---|---|---|---|---|---|
| Demand plan | `DRAFT` | `whm_demand_plans.status` | `MRP-T1-03` | `-04`, `-06` | initial |
| Demand plan | `ACTIVE` | `status` (one per site) | `MRP-T1-04` | `-05` | active |
| Demand plan | `ARCHIVED` | `status` | `MRP-T1-05` | none | **terminal** |
| Run | `QUEUED` → `RUNNING` | `whm_mrp_runs.status`, `job_run_id` | `MRP-T1-07` | `-08`, `-09` | active |
| Run | `COMPLETED` | `status`; counts, `finished_at` | `MRP-T1-08` | `-10` | active (current run) |
| Run | `FAILED` | `status`; `error_message` | `MRP-T1-09` | `-10` | active |
| Run | `SUPERSEDED` | `status` | `MRP-T1-10` | none | **terminal** |
| Proposal | `OPEN` | `whm_mrp_proposals.status` | `MRP-T1-08` | `-11`, `-13`/`-14`, `-15`, `-16` | initial |
| Proposal | `FIRMED` | `status`; `firmed_by/at` | `MRP-T1-11` | `-13`/`-14`, `-15` | active (counted as supply) |
| Proposal | `CONVERTED` · `DISMISSED` · `SUPERSEDED` | `status`; `converted_document_*` / `dismiss_reason_code_id` | `-13`/`-14` · `-15` · `-16` | none | **terminal** |
| Exception | *new* / *acknowledged* (derived) | `acknowledged_by/at` | `MRP-T1-08` / `-17` | none | — |

### 1.2 Transitions

| ID | From | Event / action | To | Guard (service, first) | Actor (permission) | Side effects | Comment/reason required | UI entry point |
|---|---|---|---|---|---|---|---|---|
| MRP-T1-01 | — | Create / edit item × site planning params | row | `MRP-GRD-01`…`-04` | `whm_item_planning_params:create` / `:edit` | — | no | WS-331 **Add** / **Edit** |
| MRP-T1-02 | row | Delete / deactivate params | deleted / `is_active = false` | — | `:delete` / `:edit` | item drops out of MRP (method treated `NONE`) | no | WS-331 row action |
| MRP-T1-03 | — | Create demand plan (+ lines, bucket editor or **Import**) | `DRAFT` | `MRP-GRD-05`, `-06` | `whm_demand_plans:create` | — | no | WS-332 **Add**; **Import** (ImportButton, Service Vehicle pattern) |
| MRP-T1-04 | `DRAFT` | **Activate** | `ACTIVE` | `MRP-GRD-08` | `whm_demand_plans:activate` | becomes the default plan of the site's next run | no | WS-332 row **Activate** |
| MRP-T1-05 | `ACTIVE` | **Archive** | `ARCHIVED` | — | `whm_demand_plans:activate` (`MRP-OPEN-06`) | next run uses no plan unless another is activated | no | WS-332 row **Archive** |
| MRP-T1-06 | `DRAFT` | Delete | deleted | never referenced by a run | `whm_demand_plans:delete` | — | no | WS-332 row **Delete** |
| MRP-T1-07 | — | **Run MRP** for a site (planner, or the Scheduler principal) | `QUEUED` | `MRP-GRD-07` | `whm_mrp_runs:run` | `MRP-` number (not gapless); typed snapshot `planning_date` (site today), `horizon_days` (setting), `demand_plan_id` (ACTIVE), `include_forecast_schedule_lines` (default true), `include_qc_hold_supply` (default false); `whb_job_runs` row | no | WS-333 **Run** modal |
| MRP-T1-08 | `QUEUED` | Job executes under the site advisory lock: netting §1.5 | `RUNNING` → `COMPLETED` | — | Scheduler (own actor, never ADMIN) | proposals `OPEN` + pegging + exceptions written; counts; **the previous `COMPLETED`/`FAILED` run → `SUPERSEDED` and its `OPEN` proposals → `SUPERSEDED`** (`MRP-T1-16`); `FIRMED`/`CONVERTED` untouched | — | none (job) |
| MRP-T1-09 | `RUNNING` | Job fails | `FAILED` | — | Scheduler | transaction rolled back: no proposal of this run survives; previous run untouched; `error_message` | — | none |
| MRP-T1-10 | `COMPLETED`/`FAILED` | A later run completes | `SUPERSEDED` | — | effect | — | — | none |
| MRP-T1-11 | `OPEN` | **Firm** (multi-select) | `FIRMED` | `MRP-GRD-09`, `-10` | `whm_mrp_proposals:firm` | counted as supply by later runs; never superseded | no | WS-334 **Firm** |
| MRP-T1-12 | `OPEN`/`FIRMED` | Edit a proposal's quantity / date | refused | — | any | change after conversion, on the order or PR | — | none (`MRP-UNR-02`) |
| MRP-T1-13 | `OPEN`/`FIRMED`, type `MAKE` | **Convert** → `PLANNED` production order (an `OPEN` proposal is firmed and converted in one transaction, `MRP-OPEN-04`) | `CONVERTED` | `MRP-GRD-09`…`-12` + order-create guards (`BOM_NOT_FOUND`) | `whm_mrp_proposals:convert` | `MRP-T4-03`; idempotency key `MRP:<proposalId>` | no | WS-334 **Convert** |
| MRP-T1-14 | `OPEN`/`FIRMED`, type `BUY` | **Convert** → core replenishment suggestion (SEAM-M3 `publishExternal(origin = MRP, runId, proposalId, item, site, qty, needDate)`) | `CONVERTED` | `MRP-GRD-09`, `-10`, `-13` | `whm_mrp_proposals:convert` | `MRP-T4-04`; `converted_document_type = REPLENISHMENT_SUGGESTION` | no | WS-334 **Convert** |
| MRP-T1-15 | `OPEN`/`FIRMED` | **Dismiss** | `DISMISSED` | `MRP-GRD-09`, `-14` | `whm_mrp_proposals:dismiss` | not supply; may re-appear in the next run | **yes** — reason | WS-334 **Dismiss** |
| MRP-T1-16 | `OPEN` | *(effect of `MRP-T1-08`)* | `SUPERSEDED` | never set directly | effect | none — an `OPEN` proposal has no suggestion | — | none |
| MRP-T1-17 | *new* exception | **Acknowledge** (multi-select) | *acknowledged* | exception of the current run | `whm_mrp_exceptions:acknowledge` | `acknowledged_by/at`; **nothing is applied** | no | WS-335 **Acknowledge** |

### 1.3 Guards

| ID | Predicate (must hold to proceed) | Refusal: HTTP · code · field | Message shape | DB backstop | Source |
|---|---|---|---|---|---|
| MRP-GRD-01 | One params row per `(item_id, warehouse_id)` | `409 PLANNING_PARAMS_DUPLICATE` · `itemId` | — | uk | FR-662 |
| MRP-GRD-02 | Lot sizing coherent: `FIXED` ⇒ `fixed_lot_quantity > 0`; `MIN_MAX` ⇒ `0 ≤ min ≤ max`, `max > 0`; `min_lot ≤ max_lot` when both; `rounding_multiple > 0` when set | `422 LOT_SIZING_INVALID` · the field | names rule and values | `CHECK (> 0)` | FR-662, FR-665 |
| MRP-GRD-03 | Lead times, fence, safety stock ≥ 0 | `422 PLANNING_VALUE_NEGATIVE` · the field | — | `CHECK (≥ 0)` | FR-662 |
| MRP-GRD-04 | `procurement_type = MAKE` with no `APPROVED` `PRODUCTION` BOM → saved with a warning (MRP raises `NO_BOM`) | — (warning in the modal) | — | — | FR-667 |
| MRP-GRD-05 | Demand line `period_start` aligned to the bucket (ISO Monday / 1st of month) and inside `[valid_from, valid_to]`; quantity ≥ 0; uk `(plan, item, period_start)` | `422 PERIOD_START_NOT_BUCKET_ALIGNED` · `lines[n].periodStart`; `422 PERIOD_OUTSIDE_PLAN_VALIDITY`; `409 DEMAND_LINE_DUPLICATE` | names the date | uk | FR-663 |
| MRP-GRD-06 | Import: every row resolves item (code) and passes `-05`; the import is all-or-nothing with a per-row error report | `422 IMPORT_ROWS_INVALID` · `rows[n]` | row number + reason | — | FR-663 |
| MRP-GRD-07 | No run of the site is `QUEUED`/`RUNNING` (advisory lock key = site) | `409 MRP_RUN_IN_PROGRESS` · `warehouseId` | names the running `MRP-` | advisory lock | FR-664, `WH-SC-658` |
| MRP-GRD-08 | No other `ACTIVE` plan for the site; plan has ≥ 1 line | `409 DEMAND_PLAN_ACTIVE_EXISTS` · `warehouseId`; `422 DEMAND_PLAN_EMPTY` | names the active plan | partial uk `(warehouse_id) WHERE status = 'ACTIVE'` | FR-663 |
| MRP-GRD-09 | Proposal belongs to the site's current (latest `COMPLETED`) run and is `OPEN`/`FIRMED` | `409 MRP_PROPOSAL_STALE` · `proposalIds[n]` | names the superseding run | — | FR-666 |
| MRP-GRD-10 | No run of the site is `QUEUED`/`RUNNING` (a run reading a snapshot would double-count the conversion) | `409 MRP_RUN_IN_PROGRESS` · `warehouseId` | — | — | FR-664 |
| MRP-GRD-11 | MAKE: BOM resolvable per FR-626 at `start_date`; item active | `422 BOM_NOT_FOUND` · `proposalIds[n]` | item, site, date, usage | — | FR-626 |
| MRP-GRD-12 | MAKE with child proposals: children pegged by `parent_proposal_id` in the same run are `OPEN`/`FIRMED` → converted together; a child already converted/dismissed is skipped and named | — (partial, reported per row) | lists skipped children | — | FR-666, `WH-SC-654` |
| MRP-GRD-13 | BUY: SEAM-M3 port bean present and accepts | `409 REPLENISHMENT_PORT_UNAVAILABLE` · `proposalIds[n]` | — | — | SEAM-M3 |
| MRP-GRD-14 | Dismiss reason present | `422 REASON_REQUIRED` · `dismissReasonCodeId` (`MRP-OPEN-05`) | — | — | FR-666 |
| MRP-GRD-15 | Multi-select actions: each proposal in its own transaction; the response lists per-row success / refusal | — | per-row | — | FR-666 |

### 1.4 Transitions that must be unreachable

| ID | Forbidden | What makes it unreachable | Source |
|---|---|---|---|
| MRP-UNR-01 | MRP posting a movement, creating an order or a suggestion without a planner action | the run service has no writer, order or SEAM-M3 dependency (grep); R-11 | FR-666, R-11 |
| MRP-UNR-02 | Editing a proposal | no edit endpoint | FR-666 |
| MRP-UNR-03 | Auto-applying an exception (reschedule, cancel) | exceptions are rows only | FR-667 |
| MRP-UNR-04 | Net-change or multi-site netting, `TRANSFER` proposals | regenerative per site only | R-03, R-04 |
| MRP-UNR-05 | Capacity load rescheduling or moving dates | read-only report | FR-668, R-01 |
| MRP-UNR-06 | MFG calling `warehouse-trade` or creating a PO | BUY ends at the core suggestion | MD-07 |

### 1.5 Netting rules (per site, per item in low-level-code order, daily buckets, base UoM)

| ID | Rule |
|---|---|
| MRP-N-01 | **Scope.** Items with active params `planning_method = MRP`; `REORDER_POINT`/`NONE`/no row ⇒ not planned (left to core replenishment). Horizon = `planning_date` … `+ horizon_days`. |
| MRP-N-02 | **Low-level code** = deepest position of the item over approved `PRODUCTION` BOMs effective in the horizon; phantoms are exploded through (never planned); a cycle found here ⇒ `RECURSIVE_BOM` exception, the subtree is skipped, the run continues. |
| MRP-N-03 | **Independent demand.** (a) open core demand-order lines: open qty from `WhDemandOrderPort.getFulfilmentPosition`, dated at the line's required date; **`FORECAST` schedule lines** included when `include_forecast_schedule_lines` (`OD-32`); (b) the run's demand plan per bucket after consumption: `MAX_OF_FORECAST_AND_ORDERS` ⇒ bucket demand = max(forecast, Σ orders in bucket) (orders consume forecast; `WH-SC-653` = 200); `FORECAST_PLUS_ORDERS` ⇒ forecast + orders; forecast dated at `period_start`; (c) approved-not-issued `p8-09` MRQ lines **except** those with cost object `PRODUCTION_ORDER` (already dependent demand, MD-16); (d) safety stock as a requirement on `planning_date`. |
| MRP-N-04 | **Dependent demand.** Open orders (`PLANNED`/`RELEASED`/`IN_PROGRESS`, incl. `SUBCONTRACT`/`REWORK`): per component required − consumed − staged-not-consumed, dated at `required_date`; MAKE proposals of this run: BOM explosion × quantity, dated at proposal `start_date` + line `lead_time_offset_days`; alternates used only by `usage_percent` split when set. |
| MRP-N-05 | **On-hand supply.** Allocatable on-hand (`L-6`) at the site's stock-holding locations, excluding `LINE_SIDE` and `JOB_WORKER` locations; `QC_HOLD` counted at `planning_date + qc_lead_time_days` only when `include_qc_hold_supply`; lots whose expiry is before the requirement date are not counted for it (`MRP-OPEN-07`). |
| MRP-N-06 | **Owner OWN only.** Only positions of the house owner (`owner_type = OWN`) count; client/consignment stock is never supply (`L-14`, `WH-SC-652`). |
| MRP-N-07 | **Reservations.** Open reservations are subtracted from on-hand **unless** their holder is itself a counted demand (a demand-order line, a counted order component) — that demand is already in the gross requirement (FR-664). |
| MRP-N-08 | **Scheduled receipts.** Open `p8-01` PO schedule-line quantity at its due date; open production orders' remaining main output (planned − received good) at `planned_end_date`; `FIRMED` proposals at `need_date`; **published-but-unordered MRP suggestions** (proposal `CONVERTED` BUY whose suggestion is not referenced by a PO schedule line and is younger than `mrp.suggestion_cover_days`, `OD-44`) at their need date; a suggestion consumed into a core draft PO counts via that PO (`WH-SC-656`). |
| MRP-N-09 | **Net.** Projected available per day = on-hand + receipts − requirements; a day below safety stock (outside the fence) creates a net requirement to restore safety stock. |
| MRP-N-10 | **Offsets.** `start_date = need_date − (manufacturing_lead_time_days` for MAKE \| purchase lead time for BUY: params → priority-1 `whb_item_supplier_sources.lead_time_days` → `whb_item_site_settings.lead_time_days`\| `) − safety_lead_time_days`; calendar days. No lead time resolvable ⇒ 0 + `NO_LEAD_TIME`. |
| MRP-N-11 | **Lot sizing**, applied in order: rule (`LOT_FOR_LOT` = net; `FIXED` = ⌈net ÷ fixed⌉ × fixed, `WH-SC-651` 320 → 1,000; `MIN_MAX` = up to max when projected < min; `PERIOD_WEEKLY`/`MONTHLY` = Σ net of the ISO week / month at its first need date) → raise to `min_lot` → split into proposals ≤ `max_lot` → round up to `rounding_multiple`. |
| MRP-N-12 | **Time fence.** A requirement whose `start_date` falls before `planning_date + planning_time_fence_days` gets **no new proposal**: `RESCHEDULE_IN` on a later existing supply when one exists, else `START_IN_PAST` (`MRP-OPEN-03`). Outside the fence a proposal whose start is before `planning_date` is created with `START_IN_PAST`. |
| MRP-N-13 | **Pegging.** Each proposal writes `whm_mrp_pegging` rows (`demand_type` `DEMAND_ORDER`/`FORECAST`/`DEMAND_PLAN`/`MRQ`/`SAFETY_STOCK`/`PROPOSAL`/`PRODUCTION_ORDER`, id, line, frozen ref, qty); dependent proposals peg to `parent_proposal_id`. |
| MRP-N-14 | **Procurement.** MAKE item without a BOM ⇒ no proposal, `NO_BOM`; BUY ⇒ `proposal_type = BUY`; UoM = item base UoM. |

### 1.6 Exception catalogue (`WHM_MRP_EXCEPTION`)

| ID | Code | Raised when | Names |
|---|---|---|---|
| MRP-X-01 | `RESCHEDULE_IN` | existing supply due after the date it is needed | document, current due, suggested date |
| MRP-X-02 | `RESCHEDULE_OUT` | existing supply due earlier than needed (`WH-SC-657`) | same |
| MRP-X-03 | `CANCEL` / `EXCESS_SUPPLY` | supply not needed in the horizon / beyond requirement + safety | document, qty |
| MRP-X-04 | `START_IN_PAST` / `DUE_IN_PAST` | proposal start < planning date / open supply due < planning date | document or proposal, dates |
| MRP-X-05 | `BELOW_SAFETY_STOCK` | projected below safety inside the fence | item, date, qty |
| MRP-X-06 | `NO_BOM` · `NO_LEAD_TIME` · `RECURSIVE_BOM` | `MRP-N-14`, `-10`, `-02` | item (and path for recursive) |
| MRP-X-07 | `DEMAND_CANCELLED` | an open production order pegged to a cancelled / reduced demand line (FR-637, `WH-SC-617`) | order, demand ref, qty |

---

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from | Extra condition |
|---|---|---|---|---|
| MRP-T2-01 | Maintain planning params | `whm_item_planning_params:create/edit/delete` | any | planner |
| MRP-T2-02 | Maintain / import demand plan | `whm_demand_plans:create/edit` | `DRAFT`; `ACTIVE` lines editable (`:edit`) | — |
| MRP-T2-03 | Activate / archive plan | `whm_demand_plans:activate` | `DRAFT` / `ACTIVE` | `MRP-GRD-08` |
| MRP-T2-04 | Run MRP | `whm_mrp_runs:run` | no run in progress | site in caller's scope |
| MRP-T2-05 | Firm / convert / dismiss | `whm_mrp_proposals:firm` / `:convert` / `:dismiss` | `OPEN`/`FIRMED` of the current run | no run in progress |
| MRP-T2-06 | Acknowledge exception | `whm_mrp_exceptions:acknowledge` | current run | — |
| MRP-T2-07 | View capacity load | `whm_reports:view` (export `:export`) | — | AUDITOR no export |

## 3. T3 — Time-driven rules & notifications

| ID | Rule | Trigger | What it changes | Who is notified | Channel | Job class | Notify-once? |
|---|---|---|---|---|---|---|---|
| MRP-T3-01 | Scheduled nightly run per site | `whb_job_runs` schedule — **no schedule setting in FRD §8** (`MRP-OPEN-08`) | `MRP-T1-07` as Scheduler | — | — | MRP run job | — |
| MRP-T3-02 | Run completed / failed | `MRP-T1-08`/`-09` | nothing | the requesting planner (Scheduler runs: holders of `whm_mrp_runs:run`) | in-app — `TBD` DEFERRED-TO-p10-12 | event | once per run |
| MRP-T3-03 | Stuck run | `RUNNING` beyond the job framework's timeout | → `FAILED`, lock released | as `-02` | as `-02` | `whb_job_runs` watchdog | once |
| MRP-T3-04 | `OD-44` cover expiry | suggestion older than `mrp.suggestion_cover_days`, still unordered | the next run stops counting it and calls `withdrawExternal` before re-proposing (MD-24) | — | — | MRP run job | — |

## 4. T4 — Cross-entity effects

| ID | When this happens | Then this other record must change | Enforced in |
|---|---|---|---|
| MRP-T4-01 | Run completes | proposals, pegging, exceptions; previous run + its `OPEN` proposals `SUPERSEDED` | run job, one transaction |
| MRP-T4-02 | Firm | the proposal is supply in later runs | netting `MRP-N-08` |
| MRP-T4-03 | MAKE convert | `PLANNED` order: `order_type = STANDARD`, item, `bom_id` per FR-626, `planned_quantity`, `planned_start_date = start_date`, `planned_end_date = need_date`, `demand_source_type = MRP`, `demand_source_id` = proposal, `mrp_proposal_id`, `demand_source_ref` = first pegged demand ref; when pegged to a demand-order line: MTO link (FR-637, `reserve_output_for_demand` false by default); child MAKE proposals → child orders with `parent_order_id`; BOM snapshot (FR-633); `converted_document_*` set | proposal service → order service |
| MRP-T4-04 | BUY convert | core `wh_replenishment_suggestions` row, `origin = MRP`, `origin_document_type/id` = run/proposal, `suggested_source = PURCHASE` (SEAM-M3); **trade on** ⇒ trade raises the PR (`TPR-T1-02`, `p9-04`, FR-557); **trade off** ⇒ core replenishment *Create PO* → draft core PO, suggestion consumed (`OD-41`) | SEAM-M3 |
| MRP-T4-05 | Converted order cancelled / suggestion dismissed in core | the proposal stays `CONVERTED`; the next run re-plans from actual supply | — |
| MRP-T4-06 | Demand-order line cancelled / reduced | `DEMAND_CANCELLED` on the pegged order in the next run; the order is never cancelled (FR-637) | netting |

## 5. T5 — Screen contract (web only)

All grids ship `grid_column_definitions` + `filter_definitions` + `grid_preferences` (default filters
and columns) in their table migration, register their `COMMON_FILTER_CONFIGS` scope, and export a superset
of the visible columns incl. `createdByName`/`updatedByName` where shown. Modals `size="lg"`
`minWidth={500}` resizable; date fields are `DatePicker` (`dateOnly` filters for SQL `DATE`).

| WS · route | Grid · scope · reference | Columns | Filters | Actions |
|---|---|---|---|---|
| WS-331 `planning-parameters` | `whm_item_planning_params` · `WAREHOUSE_MFG_PLANNING_PARAM` · Customer | `itemCode`, `itemName`, `warehouseName`, `planningMethod`, `procurementType`, `lotSizingRule`, `fixedLotQuantity`, `minLotQuantity`, `maxLotQuantity`, `roundingMultiple`, `safetyStockQuantity`, `safetyLeadTimeDays`, `manufacturingLeadTimeDays`, `purchaseLeadTimeDays` (+ resolved), `planningTimeFenceDays`, `qcLeadTimeDays`, `defaultBomAlternativeNo`, `isActive`, audit | `warehouseId` → `itemId`; `planningMethod`, `procurementType`, `lotSizingRule` (enum); `isActive` (boolean) | Add · Edit · View · Activate/Deactivate · Delete · Export |
| WS-332 `demand-plans` | `whm_demand_plans` · `WAREHOUSE_MFG_DEMAND_PLAN` · Customer (bucket grid editor + import) | `planCode`, `name`, `warehouseName`, `bucket`, `consumptionMode`, `validFrom`, `validTo` (date-only `formatDateSync`), `lineCount`, `totalQuantity`, `status`, audit | `warehouseId`; `status`, `bucket` (enum); `validFrom`/`validTo` (**dateOnly**) | Add · Edit · Import · Activate · Archive · Delete (`DRAFT`) · Export |
| WS-333 `mrp-runs` | `whm_mrp_runs` · `WAREHOUSE_MFG_MRP_RUN` · Service Vehicle | `runNumber`, `warehouseName`, `planningDate` (date-only), `horizonDays`, `demandPlanCode`, `includeForecastScheduleLines`, `includeQcHoldSupply`, `status`, `startedAt`, `finishedAt`, `itemCount`, `proposalCount`, `exceptionCount`, `errorMessage`, `createdByName` | `warehouseId`; `status` (enum); `planningDateFrom`/`To` (**dateOnly**) | **Run** (modal) · View · Open proposals / exceptions · Export |
| WS-334 `mrp-proposals` | `whm_mrp_proposals` · `WAREHOUSE_MFG_MRP_PROPOSAL` · Customer (multi-select) | `_select`, `runNumber`, `itemCode`, `itemName`, `proposalType`, `quantity`, `uomCode`, `startDate`, `needDate` (date-only), `lowLevelCode`, `bomCode`, `peggedDemandRefs`, `status`, `firmedByName`, `convertedDocumentRef` (GridLink), `dismissReasonName` | `warehouseId` → `runId` (default current); `proposalType`, `status` (enum); `itemId`; `needDateFrom`/`To` (**dateOnly**); `startInPastOnly` (boolean) | Firm · Convert · Dismiss (reason modal) — bulk; View pegging · Export |
| WS-335 `mrp-exceptions` | `whm_mrp_exceptions` · `WAREHOUSE_MFG_MRP_EXCEPTION` · Department | `runNumber`, `exceptionCode` (registry label), `itemName`, `documentType`, `documentRef` (GridLink), `currentDueDate`, `suggestedDueDate` (date-only; columns `current_due_date`, `suggested_due_date` — MD-27), `quantity`, `message`, `acknowledgedByName`, `acknowledgedAt` | `warehouseId` → `runId`; `exceptionCode` (enum); `itemId`; `acknowledged` (boolean) | Acknowledge (bulk) · Export |
| WS-336 `capacity-load` | `whm_capacity_load` · `WAREHOUSE_MFG_CAPACITY_LOAD` · report | `workCentreCode`, `workCentreName`, `loadDate` (date-only), `availableMinutes` (= minutes/day × efficiency % × parallel units on a working day of the mask, else 0), `loadMinutes`, `loadPercent`, `isOverload` (> 100 %), `orderMinutes`, `proposalMinutes` | `warehouseId` → `workCentreId`; `dateFrom`/`dateTo` (**dateOnly**, default today + 30); `includeProposals` (boolean); `overloadOnly` (boolean) | Export only (no write) |

### 5.1 Capacity load computation (WS-336, read-only)

Load per work centre per day = open operations (`OPEN`/`STARTED`) of `PLANNED`/`RELEASED`/`IN_PROGRESS`
orders: setup (if not `STARTED`) + run minutes × (1 − confirmed good ÷ planned), spread evenly over the
working days of `[planned_start_date, planned_end_date]` (`MRP-OPEN-09`); plus, when
`includeProposals`, current-run `OPEN`/`FIRMED` MAKE proposals with BOM operations (setup + run per unit ×
qty over `[start_date, need_date]`). `WH-SC-659`: 480 × 90 % × 1 = 432; 610 ÷ 432 = **141 %**, overload,
nothing rescheduled.

## 6. Out of scope

| Not built | Why |
|---|---|
| Net-change MRP; multi-site / `TRANSFER` proposals | R-03, R-04 |
| Finite scheduling, APS, auto-reschedule | R-01 |
| Automatic order / PR creation without a planner | R-11, `TPR` §6 |
| Working-day calendars in lead-time offsets | calendar days in v1 |
| Mobile | R-13 |

## 7. Amendments

| Date | Row IDs affected | Change | Found by |
|---|---|---|---|
| 2026-10-22 | all | v0 derived from `docs/frd/FRD-MFG.md`; not ratified | contract derivation (design set) |
| 2026-10-22 | T3, §9 | Consistency pass: suggestion publish/cover/withdraw (MD-24), `PRODUCTION_ORDER` MRQs excluded (MD-16), `current_due_date` (MD-27), SEAM-M3 = `p8-16` (MD-28) | FRD-MFG §9 |

## 8. Invariants and scenarios this workflow must not break

| Invariant | Rows | Scenarios |
|---|---|---|
| `L-14` — non-own never supply | `MRP-N-06` | `WH-SC-652` |
| `L-6`/`L-10` — no double subtraction of reservations | `MRP-N-07` | `WH-SC-650` |
| One run per site | `MRP-GRD-07`, `-10` | `WH-SC-658` |
| No sibling-to-sibling dependency (MD-07) | `MRP-UNR-06`, `MRP-T4-04` | `WH-SC-655`, `WH-SC-656` |
| Nothing auto-applied | `MRP-UNR-01`, `-03`, `-05` | `WH-SC-617`, `WH-SC-657`, `WH-SC-659` |

## 9. Open rows — contradictions and holes

| ID | Contradiction / hole | Recommendation | Authority | Status |
|---|---|---|---|---|
| MRP-OPEN-01 *(resolved — MD-24)* | FR-666: "a new run supersedes `OPEN` proposals and withdraws their unconverted suggestions" — an `OPEN` proposal has no suggestion (BUY publishes only at convert), and `OD-44` keeps published-unordered suggestions as supply | a run never withdraws a suggestion of a `CONVERTED` proposal inside the cover window; after `suggestion_cover_days` the run withdraws it and re-proposes (`MRP-T3-04`) | FR-666 vs `OD-44`, FR-664 | resolved |
| MRP-OPEN-02 *(resolved — MD-16)* | FR-664 counts approved-not-issued MRQs as independent demand **and** open orders' components as dependent demand — an order's own MRQ (`Request materials`) is counted twice | exclude MRQ lines with cost object `PRODUCTION_ORDER` (`MRP-N-03`) | FR-640, FR-664 | resolved |
| MRP-OPEN-03 | FR-665 inside-fence behaviour names only `RESCHEDULE_IN` / `START_IN_PAST`; an uncovered need inside the fence with no later supply and a start not in the past has no exception | raise `START_IN_PAST` (start would fall inside the frozen zone) — or add `INSIDE_TIME_FENCE` to `WHM_MRP_EXCEPTION` | FR-665, §3.1 | open |
| MRP-OPEN-04 | §5 ladder is `OPEN → FIRMED → CONVERTED`; FR-666 / `WH-SC-655` convert without an explicit firm | convert from `OPEN` firms and converts in one transaction (`firmed_by` = converter) | §5, FR-666 | open |
| MRP-OPEN-05 | `dismiss_reason_code_id` exists but §3.1 seeds no MRP reason context | add `MRP_DISMISS` context (`NOT_NEEDED`, `DUPLICATE`, `MANUAL_PLAN`) in `V560001` | §3.1 | open |
| MRP-OPEN-06 | `whm_demand_plans` has `activate` but no archive verb | archive under `:activate` | §7 | open |
| MRP-OPEN-07 | Research §11 "lot expiring before FG release": FR-664 counts on-hand without expiry | exclude lots expiring before the requirement date (`MRP-N-05`) | FR-664 | open |
| MRP-OPEN-08 | FR-664 is async and §2 names a Scheduler for the MRP run, but §8 has no schedule setting | add `warehouse.manufacturing.mrp.schedule_cron` (null = manual only) | §8 | open |
| MRP-OPEN-09 | FR-668 does not say how an order's minutes are placed on days (`WH-SC-659` is a single day) | spread over working days between planned start and end | FR-668 | open |
| MRP-OPEN-10 | Core replenishment (`V510070`) plans by reorder point regardless of MFG's `planning_method`; an `MRP` item with core reorder settings is proposed twice | core replenishment skips items whose MFG params say `MRP` (SEAM-M3 read) | FR-662, SEAM-M3 | open |
| MRP-OPEN-11 *(resolved — MD-27)* | `whm_mrp_exceptions.current_date` is a PostgreSQL **reserved word** | rename to `current_due_date` (and `suggested_date` → `suggested_due_date` for symmetry) | FRD §4, PostgreSQL | resolved |
| MRP-OPEN-12 *(resolved — SEAM-M3 is `p8-16`, MD-28)* | FRD SEAM-M3 says "new `p8-15`, or folded into `p8-14`"; `issues/p8-15.md` already exists as the RMA-creation port | fold SEAM-M3 into `p8-14` or take the next free STORES id | FRD §3.2 | resolved |
