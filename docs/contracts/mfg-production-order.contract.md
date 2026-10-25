# Functional Contract — Production order lifecycle (create, release, hold, complete, reopen, close hand-off)

> **What this is.** The functional truth for the `whm_production_orders` document: creation with the
> BOM snapshot (manual, from a demand-order line, from an MRP proposal, from QC rework, as a parent's
> sub-assembly), numbering, release with the shortage list, component reservations and optional
> approval, hold / resume, unrelease, cancel, completion (manual or by a final receipt), reopen, the
> close hand-off to settlement, the MTO demand link, the traveller print and the append-only event
> history; plus the two report screens WS-336 (capacity load) and WS-337 (registers).
>
> **What this is not.** Material staging, request-materials and the cost-object resolver are
> [`mfg-material-staging-issue.contract.md`](mfg-material-staging-issue.contract.md) (`MSI-*`); receipts,
> backflush and receipt reversal are [`mfg-production-receipt.contract.md`](mfg-production-receipt.contract.md)
> (`PRC-*`); BOM selection is [`mfg-bom.contract.md`](mfg-bom.contract.md) (`BOM-*`); settlement
> arithmetic is `mfg-costing-close.contract.md`; MRP conversion is `mfg-mrp.contract.md`; QC rework is
> `mfg-qc-rework.contract.md`; subcontract dispatch is `mfg-subcontracting.contract.md`. Reservations go
> through `WhbReservationService`; no ledger row is written by this document itself.
>
> **Status.** Derived 2026-10-22 (v0), **not ratified**. Authority `docs/frd/FRD-MFG.md` FR-632…FR-637,
> FR-656 (close entry), FR-668, §7, §8, §12. *Proposed* codes are fixed by `p10-05` / `p10-13`.

---

## 0. Identity

| | |
|---|---|
| **Workflow** | Order `PLANNED → RELEASED → IN_PROGRESS → COMPLETED → CLOSED`; `CANCELLED`; unrelease; reopen; hold flag; MTO link; traveller; events; capacity load and registers |
| **Module** | `warehouse-manufacturing` (`whm_`); calls `WhbReservationService` (create/release/`releaseByHolder`), `WhbDocumentNumberIssuer.resolveSiteSeries` (`PRD-`), `WhDemandOrderPort` read (`p8-02`), `WarehousePrintDataProvider` (`PRODUCTION_ORDER_TRAVELLER`) |
| **Domain baseline** | FRD-MFG §3.1 registries, §4 order tables, §5 ladder, `MD-02`, `MD-12`, `MD-38` (MFG ships in v1.1 with the P8 seams); `DECISIONS.md` `L-6` (allocatable), `L-10` (reservation holder quad), `L-14` (non-own never valued); `RJ-005` (one verb per transition) |
| **Owning task bodies** | `p10-05` (`V560030` · `V561030`) · `p10-13` (`V561110` report grids). Depends on `p10-02`, `p10-03`, `p8-02` |
| **Primary tables** | `whm_production_orders`, `whm_production_order_components`, `_outputs`, `_operations`, `_events` |
| **Status columns** | `whm_production_orders.status` (`PLANNED`/`APPROVED`/`RELEASED`/`IN_PROGRESS`/`COMPLETED`/`CLOSED`/`SHORT_CLOSED`/`CANCELLED`; R32 `APPROVED`, `SHORT_CLOSED`) + flag `is_on_hold`; component `line_status`, operation `status` derived on write — **no `CHECK`** (`D-10`) |
| **Permission resources** | `whm_production_orders:{view,create,edit,export,submit,approve,release,approve_release,approve_shortage_release,unrelease,hold,complete,reopen,cancel,substitute,request_materials,close}` (R32 `submit`, `approve`, `approve_shortage_release`) (`substitute`, `request_materials` → `MSI`) · `whm_reports:{view,export}` (WS-336, WS-337). Hold and Resume share `:hold`. AUDITOR `:view` only |
| **Routes** | `/warehouse/manufacturing/production-orders` (WS-323), `/[id]` (WS-324), `/capacity-load` (WS-336), `/registers` (WS-337) · mobile: none |
| **Requirement source** | `docs/frd/FRD-MFG.md` 2026-10-22 |
| **Contract status** | `derived 2026-10-22 (v0), not ratified` |
| **Contract version** | `v0 — 2026-10-22` |

### Acceptance checks

| # | The requester expects… | Delivered by |
|---|---|---|
| A1 | Creation freezes the BOM: scaled, scrap applied, fixed unscaled, phantoms exploded; later BOM versions never alter it (`WH-SC-609`, `WH-SC-612`) | `PRO-T1-01`, `PRO-T4-01`, `PRO-UNR-02` |
| A2 | Release returns a shortage list, honours `BLOCK`/`WARN`/`ALLOW`, makes HARD reservations with the order holder quad (`WH-SC-610`, `WH-SC-611`) | `PRO-T1-08`, `PRO-GRD-08`, `PRO-T4-02` |
| A3 | Cancel only while nothing is posted, staged or issued against a requisition (open MRQs are cancelled through the port, R29 F4); after the first posting the exit is unstage/return → complete short → close, never cancel (MD-15); the number stays issued (`WH-SC-613`, `WH-SC-614`) | `PRO-T1-20`, `PRO-GRD-10` |
| A4 | Hold refuses every posting with `409 ORDER_ON_HOLD` (`WH-SC-615`) | `PRO-T1-13`, `PRO-GRD-11` |
| A5 | MTO link freezes the SO reference; a cancelled demand line raises `DEMAND_CANCELLED` and never cancels the order (`WH-SC-616`, `WH-SC-617`) | `PRO-T1-02`, `PRO-T4-07`, `PRO-UNR-05` |
| A6 | Reopen `COMPLETED → IN_PROGRESS` with a reason until a settlement exists (`WH-SC-644`) | `PRO-T1-18`, `PRO-GRD-14` |
| A7 | Close hands off to settlement; `CLOSED` refuses any further issue (`WH-SC-641`, `WH-SC-642`, `WH-SC-643`) | `PRO-T1-21`, `PRO-T1-22`, `PRO-GRD-15` |
| A8 | Capacity load is infinite and visible, flags overload, reschedules nothing (`WH-SC-659`) | §5.3, `PRO-UNR-08` |

---

## 1. T1 — State machine

### 1.1 Status inventory

| Entity | Status | Represented by | Reachable via | Exits via | Kind |
|---|---|---|---|---|---|
| Order | `PLANNED` | `status` | `PRO-T1-01`…`-05`, `-12`, `-46`, `-47` | `-08`, `-09`, `-20`, `-40` | initial, editable |
| Order | *order approval pending* (derived, R32) | `PLANNED` with an engine request of type `WHM_PRODUCTION_ORDER` `PENDING` | `PRO-T1-40` (Submit) | `-40a` (final approval), `-47` (reject / withdraw) | active; edits refused `409 APPROVAL_PENDING` |
| Order | `APPROVED` (R32) | `status`; `approved_by/at` | `PRO-T1-40a` | `-08`, `-09`, `-20`, `-46` | active; edit only as an amendment (`PRO-T1-46`) |
| Order | *release pending approval* (derived) | `PLANNED` / `APPROVED` with `release_requested_by/at` set, `released_at` null and one engine request of type `WHM_SHORTAGE_RELEASE` `PENDING` (R31 `PRO-OPEN-02`; R32 one pending track per order) | `PRO-T1-09` | `-10`, `-11`, `-11a` | active |
| Order | `RELEASED` | `status`; `released_by/at`, stamped at the actual release (+ `release_approved_by/at`) | `PRO-T1-08`, `-10` | `-12`, `-15`, `-20` | active |
| Order | `IN_PROGRESS` | `status`; `actual_start_at` | `PRO-T1-15`, `-18`, `-19` | `-16`, `-17` | active |
| Order | `COMPLETED` | `status`; `completed_by/at`, `actual_end_at` | `PRO-T1-16`, `-17` | `-18`, `-19`, `-21` | active |
| Order | `CLOSED` | `status`; `closed_at`, `settlement_id` | `PRO-T1-22` (effect) | none | **terminal** |
| Order | `SHORT_CLOSED` (R32) | `status`; `closed_at`, `settlement_id`, `close_short_reason_code_id` | `PRO-T1-41` (effect of the settlement post) | none | **terminal** |
| Order | `CANCELLED` | `status`; `cancel_reason_code_id`, `cancel_note` | `PRO-T1-20` | none | **terminal** |
| Order flag | *on hold* | `is_on_hold = true`; `hold_reason_code_id`, `hold_note`, `held_by/at` | `PRO-T1-13` | `PRO-T1-14` | orthogonal to `RELEASED`/`IN_PROGRESS` |
| Component line | `OPEN`/`PARTIAL`/`COMPLETE`/`CLOSED` | `line_status`, derived from required vs consumed on every write | effects (`MSI`, `PRC`) | `CLOSED` at order close/cancel | derived |
| Operation | `OPEN`/`STARTED`/`CONFIRMED` | `whm_production_order_operations.status` | `mfg-qc-rework` confirmations | — | derived |

### 1.2 Transitions

Every transition appends one `whm_production_order_events` row (`event_type`, `from_status`,
`to_status`, reason, note, actor, `occurred_at`) in the same transaction (`PRO-T4-09`).

| ID | From | Event / action | To | Guard (service, first) | Actor (permission) | Side effects | Comment/reason required | UI entry point | Source |
|---|---|---|---|---|---|---|---|---|---|
| PRO-T1-01 | — | **Create (manual)**: type, item, planned qty + UoM, priority, planned start/end, receipt / line-side locations, work centre, consumption policy, tolerances, planned lot, optional explicit BOM | `PLANNED`, `demand_source_type = MANUAL` | `PRO-GRD-01`…`-06`, `-17`, `-18`, `-20` | `whm_production_orders:create` | `PRD-` number issued at create (gapless per site, `PRO-T4-08`); snapshot (`PRO-T4-01`); policy / tolerances default from settings when null | no | WS-323 toolbar **Add** | FR-632, FR-633 |
| PRO-T1-02 | — | **Create from demand line** (MTO) | `PLANNED`, `demand_source_type = DEMAND_ORDER` | `PRO-T1-01` guards + `PRO-GRD-19` | `whm_production_orders:create` | `demand_source_id/line_id` stored; `demand_source_ref` frozen (SO no./line, customer); `reserve_output_for_demand` as chosen | no | WS-323 **Add** → *From demand line* picker | FR-632, FR-637 |
| PRO-T1-03 | — | *(effect)* MRP `MAKE` proposal converted | `PLANNED`, `demand_source_type = MRP`, `mrp_proposal_id`; `order_type = SUBCONTRACT` when the proposal's BOM has usage `SUBCONTRACT` (R31 F-MF-014) | `PRO-T1-01` guards | `whm_mrp_proposals:convert` | sub-assembly proposals → child orders with `parent_order_id`, `demand_source_type = PARENT_ORDER` (`PRO-T1-05`) | — | none here — WS-334 **Convert** (`mfg-mrp`) | FR-666 |
| PRO-T1-04 | — | *(effect)* QC `REWORK` disposition `onDisposition` | `PLANNED`, `order_type = REWORK`, `demand_source_type = QC_REWORK`, `rework_of_inspection_id` | `PRO-GRD-01` (rework BOM optional — `bom_id` may be null), `-02` | system (QC disposition by `wh_quality_inspections:disposition`) | first component = rejected item/lot, `supply_stock_status_code = REJECTED`, `BACKFLUSH`, **no reservation** (core admits none on a non-allocatable status; MD-26, MD-30); output = same item; lot kept per `rework_keeps_lot` | — | none — WS-080 disposition (`mfg-qc-rework`) | FR-653 |
| PRO-T1-05 | — | Create a sub-assembly child order from a parent | `PLANNED`, `parent_order_id` | `PRO-T1-01` guards | `whm_production_orders:create` | child's main output = parent component item; child need date = parent component `required_date` | no | WS-324 Components tab **Make sub-assembly** | FR-633 |
| PRO-T1-06 | `PLANNED` (any field) · `RELEASED`/`IN_PROGRESS` (priority, planned dates, notes, work centre only) | Edit | unchanged | `PRO-GRD-05`, `-06`, `-20`, `-23`; quantity / BOM / item edits only in `PLANNED` (`PRO-GRD-12`) | `whm_production_orders:edit` | quantity change in `PLANNED` re-scales the snapshot (`PRO-T1-07`) | no | WS-323/WS-324 **Edit** | FR-633, FR-634 |
| PRO-T1-07 | `PLANNED` | **Re-explode** (re-select BOM and rebuild components / outputs / operations) | unchanged | `PRO-GRD-01`, `-23`; nothing issued (`PRO-GRD-10`) | `whm_production_orders:edit` | snapshot replaced; `bom_id` updated; event `RE_EXPLODED` | no | WS-324 **Re-explode** (shown only in `PLANNED`, `WH-SC-612`) | FR-633, FR-634 |
| PRO-T1-08 | `PLANNED` · `APPROVED` (only `APPROVED` when `order_approval_mode` applies, `PRO-GRD-40`), `release_requires_approval = false` and no shortage under `APPROVE` | **Release** | `RELEASED` | `PRO-GRD-07`, `-08`, `-11`, `-21`, `-40` | `whm_production_orders:release` | reservations (`PRO-T4-02`); `planned_cost` rolled (`PRO-T4-03`); `released_by/at`; traveller printable | shortage acknowledgement under `WARN` (`PRO-GRD-08`) | WS-323 row **Release** modal (shows shortage list) | FR-635 |
| PRO-T1-09 | `PLANNED` · `APPROVED` (`PRO-GRD-40`), `release_requires_approval = true` **or** a shortage under `release_with_shortage = APPROVE` | **Release (request)** | *release pending approval* | `PRO-GRD-07`, `-08`, `-40` | `whm_production_orders:release` | `release_requested_by/at` stamped (`released_*` stays null); **one** engine request of type `WHM_SHORTAGE_RELEASE` (`p8-30`; approve verb `:approve_release`, snapshot condition `has_shortage` with the shortage list; default policy `DOCUMENT_DEFINED`: one level, held by `:approve_shortage_release` when `has_shortage`, else `:approve_release`); no reservation yet; approvers notified by the engine alert (`PRO-T3-03`) | as `PRO-T1-08` | WS-323 row **Release** | FR-635 |
| PRO-T1-10 | *release pending approval* | *(effect)* the engine's **final** approval of the `WHM_SHORTAGE_RELEASE` request | `RELEASED` | `PRO-GRD-09`; `PRO-GRD-07`, `-08` re-run (stock may have moved — a new shortage under `APPROVE` fails the post-approval effect `409 SHORTAGE_RELEASE_NEEDS_APPROVAL` and the order stays pending-free `PLANNED`/`APPROVED`) | engine level (`:approve_release` / `:approve_shortage_release`) | `released_by/at` and `release_approved_by/at` stamped now; `PRO-T4-02`, `-03` | no | WS-323 row **Approve release** | FR-635 |
| PRO-T1-11 | *release pending approval* | Reject release (engine reject at any level) | the status it was requested from (pending cleared) | `PRO-GRD-09` | engine level | `release_requested_by/at` cleared; event `RELEASE_REJECTED` | **yes** — `APPROVAL_REJECT` reason | WS-323 row **Reject release** (opens the engine action) | FR-635, FR-825 |
| PRO-T1-11a | *release pending approval* | **Withdraw** release request (engine `withdraw`) | the status it was requested from | requester only | `whm_production_orders:release` | `release_requested_by/at` cleared; event `RELEASE_WITHDRAWN` | no | WS-323 row **Withdraw** | FR-635, FR-825 |
| PRO-T1-12 | `RELEASED` | **Unrelease** | `PLANNED` | `PRO-GRD-10`, `-11` | `whm_production_orders:unrelease` | reservations released and open MRQs cancelled through the port (`PRO-T4-04`); batches and their unstarted job cards `CANCELLED`, `PLANNED` units `CANCELLED` with serial values voided (`SFL-T1-10c`, `PUR-T1-08`); an `APPROVED` order returns to `PLANNED` and needs re-approval; `release_requested_*`, `released_*`, `release_approved_*` cleared; `planned_cost` kept | no | WS-323 row **Unrelease** | FR-634, FR-635 |
| PRO-T1-13 | `RELEASED` · `IN_PROGRESS`, not on hold | **Hold** | flag set | `PRO-GRD-16` (reason in `PRODUCTION_HOLD`) | `whm_production_orders:hold` | reservations **kept**; every posting refused while set (`PRO-GRD-11`) | **yes** — reason + note | WS-323 row **Hold** modal | FR-634 |
| PRO-T1-14 | on hold | **Resume** | flag cleared | — | `whm_production_orders:hold` | `hold_*` cleared (history in events) | no | WS-323 row **Resume** | FR-634 |
| PRO-T1-15 | `RELEASED` | *(effect)* first posting of any kind for the order — `PRODUCTION_STAGE` (`MSI-T1-04`), `PRODUCTION_STAGE_CONSUMPTION` (`SFL-T4-02`, R32), store issue (`MSI-T1-09`), receipt (`PRC-T1-04`), subcontract dispatch | `IN_PROGRESS` | never set directly | the poster | `actual_start_at` = the posting's `occurred_at` | — | none (effect) | FR-634 |
| PRO-T1-16 | `IN_PROGRESS` | **Complete** (manual) | `COMPLETED` | `PRO-GRD-11`, `-13` | `whm_production_orders:complete` | `completed_by/at`, `actual_end_at`; remaining open reservations **kept** until close — `COMPLETED` still accepts late store issues and returns through the resolver until `CLOSED` (MD-14); open operations left as is | `PRODUCTION_CLOSE_SHORT` reason when received good < planned × (1 − under %) | WS-323 row **Complete** modal | FR-634 |
| PRO-T1-17 | `IN_PROGRESS` | *(effect)* receipt posted with `is_final = true` (`PRC-T1-04`/`-06`) | `COMPLETED` | `PRC-GRD-06` (close-short reason on the receipt) | `whm_production_receipts:post` / `:approve` | as `PRO-T1-16` | on the receipt | none (effect) | FR-634, FR-647 |
| PRO-T1-18 | `COMPLETED`, no live settlement | **Reopen** | `IN_PROGRESS` | `PRO-GRD-14` | `whm_production_orders:reopen` | `completed_*` cleared; event keeps them | **yes** — `PRODUCTION_REOPEN` reason | WS-323 row **Reopen** modal | FR-634 |
| PRO-T1-19 | `COMPLETED` | *(effect)* a receipt reversal posted (`PRC-T1-13`) | `IN_PROGRESS` | `PRC-GRD-24` | `whm_production_receipt_reversals:post` | rollups regress | — | none (effect) | FR-634, FR-649 |
| PRO-T1-20 | `PLANNED` · `APPROVED` · `RELEASED` (incl. either pending approval — the open engine request is withdrawn) | **Cancel** | `CANCELLED` | `PRO-GRD-10`, `-16` (`PRODUCTION_CANCEL`) | `whm_production_orders:cancel` | reservations released and open MRQs cancelled through the port (`PRO-T4-04`); batches, unstarted job cards and `PLANNED` units cancelled as `PRO-T1-12`; component lines `CLOSED`; MRP proposal link kept; number stays issued | **yes** | WS-323 row **Cancel** modal | FR-634 |
| PRO-T1-21 | `COMPLETED` | **Close** — computes the residual and creates the settlement | `COMPLETED` (settlement `DRAFT`, or posted at once → `PRO-T1-22`) | `PRO-GRD-15` | `whm_production_orders:close` | settlement per `mfg-costing-close` (residual, `close_variance_approval_percent`); when under threshold it posts in the same transaction | no | WS-323 row **Close** modal (shows residual, split, approval need; R32: planned vs actual quantity, material and time variance, rejection %, cost per unit — read from the WS-337 registers, `CST-T5-10`) | FR-656 |
| PRO-T1-22 | `COMPLETED` | *(effect)* settlement `POSTED` | `CLOSED` | settlement guards (`mfg-costing-close`) | `whm_production_settlements:post` / `:approve` | `PRO-T4-05`: reservations released, MRQ closed through `WhMaterialRequisitionPort.close`, component lines `CLOSED`, `closed_at`, `settlement_id` | — | none (effect); WS-329 | FR-656 |
| PRO-T1-23 | any but `CANCELLED` | **Print traveller** | unchanged | — | `whm_production_orders:view` | `PRODUCTION_ORDER_TRAVELLER`: header, barcode, demand ref, components (required / issued / supply method), operations with QC checkpoints, output lots | no | WS-324 toolbar **Print traveller** | FR-636 |

### 1.3 Guards

| ID | Predicate (must hold to proceed) | Refusal: HTTP · code · field | Message shape | DB backstop | Source |
|---|---|---|---|---|---|
| PRO-GRD-01 | A BOM resolves by `BOM-T1-13` on `planned_start_date` (MD-19; re-checked at release by `PRO-GRD-07`) for usage `PRODUCTION` (`STANDARD`/`REWORK`) or `SUBCONTRACT` (`SUBCONTRACT`); an explicit BOM's usage matches the type; `REWORK` may have none | `422 BOM_NOT_FOUND` · `bomId`; `422 BOM_USAGE_MISMATCH` *(proposed)* · `bomId` | item, site, date, usage | FK `bom_id` | FR-626, FR-633, FR-658 |
| PRO-GRD-02 | `planned_quantity > 0`; UoM convertible to item base (factor frozen into `conversion_factor_used`) | `422 UOM_NOT_CONVERTIBLE` · `uomCode`; `422` · `plannedQuantity` | — | CHECK | FR-632, `FR-143` |
| PRO-GRD-03 | The item is not a phantom (`BOM-GRD-12`'s predicate) and is stock-holding | `422 PHANTOM_ITEM_NOT_PRODUCIBLE` *(proposed)* · `itemId` | — | — | FR-627 |
| PRO-GRD-04 | `order_type` active in `WHM_ORDER_TYPE`; `SUBCONTRACT` carries `subcontractor_counterparty_id` and a `subcontract_location_id` of type `JOB_WORKER` at the site; non-subcontract types carry neither | `422 SUBCONTRACTOR_REQUIRED` *(proposed)* · `subcontractorCounterpartyId`; `422 SUBCONTRACT_LOCATION_INVALID` *(proposed)* · `subcontractLocationId` — the codes of `SUB-GRD-02`, `-03`, one code per predicate (R31 F-MF-019) | — | composite FK | FR-658 |
| PRO-GRD-05 | `planned_end_date ≥ planned_start_date` | `422 PLANNED_END_BEFORE_START` *(proposed)* · `plannedEndDate` | — | — | FR-632 |
| PRO-GRD-06 | `receipt_location_id` is physical stock-holding at the order's site; `line_side_location_id` of type `LINE_SIDE` at the site; work centre active at the site; tolerances ≥ 0 | `422 RECEIPT_LOCATION_INVALID` · `receiptLocationId`; `422 LINE_SIDE_LOCATION_INVALID` · `lineSideLocationId` *(proposed)* | names type found | FK | FR-632 |
| PRO-GRD-07 | Release: frozen BOM `APPROVED` and current on `planned_start_date` (`REWORK` without BOM exempt); `receipt_location_id` set; ≥ 1 component or a `REWORK` order | `409 BOM_NOT_EFFECTIVE` *(proposed)* · `bomId`; `422 RECEIPT_LOCATION_REQUIRED` · `receiptLocationId` | names BOM range and start | — | FR-635 |
| PRO-GRD-08 | Shortage per component = required base − allocatable free stock at the site (`L-6`, house owner only); for a line with `supply_stock_status_code` set (a rework order's `REJECTED` line) = required base − on-hand **in that status** at its supply location less open reservations (MD-30, R29 F2). `BLOCK`: any shortage refuses; `WARN`: request carries `acknowledgeShortage = true`; `ALLOW`: proceeds | `409 RELEASE_SHORTAGE` · `components` listing item, required, available, short; `422 SHORTAGE_ACK_REQUIRED` *(proposed)* · `acknowledgeShortage` | `IMPELLER-02 short 40` | — | FR-635, `WH-SC-610`, `-611` |
| PRO-GRD-09 | Approve/reject release: the engine's `DAP-GRD-03` — actor ≠ `release_requested_by`, ≠ the order's creator, has acted on no other level of the request; `ADMIN` refused too (R32, `D-21` item 6) | kept code `403 RELEASE_SELF_APPROVAL` *(MD-21)* · banner | names the requester | — | FR-635, `MD-12` |
| PRO-GRD-10 | Cancel / Unrelease / Re-explode: no posted `PRODUCTION_STAGE`, `PRODUCTION_STAGE_CONSUMPTION` (R32), store issue, receipt or dispatch for the order; **no job card ever started** (`STARTED`/`PAUSED`/`HELD_QC`/`COMPLETED`, R32 — `PLANNED` units do not block: they are cancelled and their serial values voided, `PUR-T1-08`); no staging list beyond `DRAFT`/`CANCELLED`; **no MRQ of the order with Σ issued > 0** (read by `WhMaterialRequisitionPort.getRequisitionPosition`, `MRQ-T1-23`) — an MRQ that is `DRAFT`/`SUBMITTED`/`APPROVED` with nothing issued, or `REJECTED`/`CLOSED`/`CANCELLED`, never blocks: the transition cancels it through the port's `cancel`, a no-op on a terminal one (`MRQ-T1-21`; R29 F4) | `409 ORDER_HAS_POSTINGS` · banner naming each document (`STG-000031`, `MRQ-…`) | an order with a posting is `IN_PROGRESS` and never cancels: the banner offers *Unstage* / store return, then *Complete* (close-short reason) and *Close* (MD-15) | — | FR-634, `WH-SC-614` |
| PRO-GRD-11 | No posting, release, stage, request or receipt while `is_on_hold`; the resolver refuses the same (`MSI-GRD-07`) | `409 ORDER_ON_HOLD` · banner | names hold reason | — | FR-634, `WH-SC-615` |
| PRO-GRD-12 | The transition's `From` matches the current status (table above); item / BOM / quantity edits only in `PLANNED` — an `APPROVED` order is edited only through *Amend* (`PRO-T1-46`, R32) and an order with a `PENDING` engine request not at all (`409 APPROVAL_PENDING`) | `409 ORDER_TRANSITION_INVALID` *(proposed)* · banner | names current and requested | `@Version` | FR-634 |
| PRO-GRD-13 | Complete: no receipt `DRAFT`/`PENDING_APPROVAL`; under-receipt below planned × (1 − `under_receipt_percent`, order → setting) needs `PRODUCTION_CLOSE_SHORT` | `409 ORDER_HAS_OPEN_RECEIPT` *(proposed)* · banner; `422 CLOSE_SHORT_REASON_REQUIRED` · `closeShortReasonCodeId` | received vs threshold | — | FR-647, `WH-SC-629` |
| PRO-GRD-14 | Reopen: no settlement in `DRAFT`/`APPROVED`/`POSTED` for the order (`REJECTED` does not count); reason in `PRODUCTION_REOPEN` | `409 ORDER_SETTLEMENT_EXISTS` *(proposed)* · banner | names `PST-` number | partial unique index `settlement.order_id WHERE status <> 'REJECTED'` (MD-22) | FR-634, `WH-SC-644` |
| PRO-GRD-15 | Close: **the close guard is `mfg-costing-close`'s** and is cited, never restated (R31 F-MF-006) — `CST-GRD-07` (status `COMPLETED`), `CST-GRD-02` (no line-side balance of the order whatever the staging-list status, no live staging list), `-03` (no open receipt or reversal), `-04` (no open subcontract balance or `DRAFT` dispatch), `-05` (no live settlement), `-08` (MRQ closable) | the `CST-GRD-*` codes: `409 ORDER_NOT_COMPLETED`, `ORDER_HAS_OPEN_STAGING`, `ORDER_HAS_OPEN_RECEIPT`, `SUBCONTRACT_BALANCE_OPEN`, `SUBCONTRACT_DISPATCH_DRAFT_OPEN`, `SETTLEMENT_EXISTS`, `ORDER_REQUISITION_OPEN` · `orderId` | lists each blocker | — | FR-656, FR-661, `WH-SC-648` |
| PRO-GRD-16 | Reason codes belong to the transition's context (`PRODUCTION_HOLD`, `PRODUCTION_CANCEL`, `PRODUCTION_REOPEN`, `PRODUCTION_CLOSE_SHORT`) and are active | `422 REASON_CODE_INVALID` · `reasonCodeId` | — | FK `whb_reason_codes` | FR-634 |
| PRO-GRD-17 | Owner = house owner of the site's operator company (non-own refused in v1, `OD-42`) | `422 OWNER_NOT_HOUSE` *(proposed)* · `ownerId` | — | FK | FR-632, `L-14` |
| PRO-GRD-18 | Same company: item, BOM, locations, counterparty belong to the order's company | `422 COMPANY_MISMATCH` · the field | — | — | FR-632, `MPR-GRD-08` (same rule) |
| PRO-GRD-19 | Demand line: exists via `WhDemandOrderPort`, open (not cancelled/fulfilled), same site, same item; Σ live orders' planned for that line ≤ its open quantity (warn above) | `422 DEMAND_LINE_INVALID` *(proposed)* · `demandSourceLineId` | names SO/line state | — | FR-637 |
| PRO-GRD-20 | `priority ∈ 1..5` | `422` · `priority` | — | CHECK | FR-632 |
| PRO-GRD-21 | Concurrency: release / unrelease / cancel / complete / close lock the order row (`FOR UPDATE`) and check `version` | `409 CONCURRENT_MODIFICATION` · banner | — | `@Version` | FR-620 (concurrency clause, R30 `CP-FR-009`) |
| PRO-GRD-22 | Record scope: the order's site is in the user's allowed warehouses | `404` | — | `WHERE` in every query | FR-669, `D-14` |
| PRO-GRD-23 | Edit / Re-explode while the release is pending approval (`PLANNED`, `release_requested_at` set, `released_at` null) is refused — the approver must approve the request as made; reject it first (R29 F22) | `409 RELEASE_PENDING_APPROVAL` *(proposed)* · banner | names the requester and `release_requested_at` | — | FR-634, FR-635 |

### 1.4 Transitions that must be unreachable

| ID | Forbidden | What makes it unreachable | Source |
|---|---|---|---|
| PRO-UNR-01 | `CLOSED` / `CANCELLED` → anything; deleting an order | terminal; no delete endpoint; `PRD-` numbers stay issued | FR-634, FR-636 |
| PRO-UNR-02 | A BOM change altering an order's components after create (other than *Re-explode* in `PLANNED`) | snapshot; `BOM-UNR-04` | FR-633 |
| PRO-UNR-03 | Setting `IN_PROGRESS`, `COMPLETED` (by receipt) or `CLOSED` directly | effects only (`PRO-T1-15`, `-17`, `-22`) | FR-634 |
| PRO-UNR-04 | Cancel of an order with any posting; `COMPLETED`/`IN_PROGRESS` → `CANCELLED` | `PRO-GRD-10`; not offered | FR-634 |
| PRO-UNR-05 | Automatic cancel or quantity change on demand-line cancel/reduction | `PRO-T4-07` raises an exception only | FR-637, R-11 |
| PRO-UNR-06 | Reopen after a settlement exists | `PRO-GRD-14` | FR-634 |
| PRO-UNR-07 | Hold on `PLANNED`/`COMPLETED`/terminal orders | not offered; `PRO-GRD-12` | FR-634 |
| PRO-UNR-08 | Automatic rescheduling from the capacity load | WS-336 is read-only (R-01) | FR-668 |
| PRO-UNR-09 | Widening `wh_work_orders` for production | separate document (`MD-02`) | FR-620, `RN-033` |

---

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from | Extra condition | Source |
|---|---|---|---|---|---|
| PRO-T2-01 | Add / from demand line / sub-assembly | `whm_production_orders:create` | — | planner | FR-632 |
| PRO-T2-02 | Edit | `whm_production_orders:edit` | `PLANNED` (all); `RELEASED`·`IN_PROGRESS` (priority, dates, notes, work centre) | not while a release is pending approval (`PRO-GRD-23`) | FR-634 |
| PRO-T2-03 | Re-explode | `whm_production_orders:edit` | `PLANNED` | nothing issued; release not pending | FR-634 |
| PRO-T2-04 | Release | `whm_production_orders:release` | `PLANNED` (no pending request) | — | FR-635 |
| PRO-T2-05 | Approve / Reject release | `whm_production_orders:approve_release` | *release pending approval* | actor ≠ requester | FR-635 |
| PRO-T2-06 | Unrelease | `whm_production_orders:unrelease` | `RELEASED` | nothing posted/staged/issued (`PRO-GRD-10`) | FR-634 |
| PRO-T2-07 | Hold · Resume | `whm_production_orders:hold` | `RELEASED`·`IN_PROGRESS` not held · held | supervisor | FR-634 |
| PRO-T2-08 | Complete | `whm_production_orders:complete` | `IN_PROGRESS` | not held | FR-634 |
| PRO-T2-09 | Reopen | `whm_production_orders:reopen` | `COMPLETED` | no live settlement | FR-634 |
| PRO-T2-10 | Cancel | `whm_production_orders:cancel` | `PLANNED`·`RELEASED` | nothing posted/staged/issued (`PRO-GRD-10`) | FR-634 |
| PRO-T2-11 | Close | `whm_production_orders:close` | `COMPLETED` | `PRO-GRD-15` | FR-656 |
| PRO-T2-12 | View · traveller | `whm_production_orders:view` | any (traveller not `CANCELLED`) | cost accountant, auditor | FR-636 |
| PRO-T2-13 | Export | `whm_production_orders:export` | any | not AUDITOR | FR-669 |
| PRO-T2-14 | Capacity load / registers view · export | `whm_reports:view` · `:export` | — | export not AUDITOR | FR-668 |

---

## 3. T3 — Time-driven rules & notifications

| ID | Rule | Trigger | What it changes | Who is notified | Channel | Job class | Notify-once? | Source |
|---|---|---|---|---|---|---|---|---|
| PRO-T3-01 | **Late order**: `planned_end_date < today` (site TZ) and status `PLANNED`/`RELEASED`/`IN_PROGRESS` | daily scheduler (own actor, never ADMIN) | nothing stored — `lateOnly` filter + tile computed on read | planner (order `created_by`) and supervisors of the work centre | in-app | `WhmLateOrderAlertJob` (`whb_job_runs`) | once per order per day of lateness change | FR-634 |
| PRO-T3-02 | **Late start**: `planned_start_date < today` and still `PLANNED`/`RELEASED` | same job | none | planner | in-app | same job | once | FR-634 |
| PRO-T3-03 | Release pending approval escalation after `warehouse.approval.pending_alert_hours` | elapsed since `released_at` | nothing — never auto-approves | holders of `:approve_release` | core pending-approval alert (`p2-23`) | core job | one per episode | FR-635 |
| PRO-T3-04 | `RELEASED` order on hold longer than `staging_stale_days` | daily | none | production manager | in-app | `WhmLateOrderAlertJob` | once per hold episode | FR-634 |

---

## 4. T4 — Cross-entity effects

| ID | When this happens | Then this other record must change | Enforced in | Source |
|---|---|---|---|---|
| PRO-T4-01 | Create / Re-explode | components = BOM lines × (planned base ÷ BOM base) ÷ (1 − BOM `process_loss_percent` ÷ 100) × (1 + scrap%), fixed lines unscaled (process loss raises the inputs so the planned output survives it; `MRP-N-04` and `BOM-T1-14` apply the same factor — R29 F29), phantoms exploded with `phantom_path`; line effectivity filtered on `planned_start_date`; `required_date = planned_start + lead_time_offset_days`; outputs (sequence 1 = MAIN + BOM outputs scaled); operations copied with planned setup + run × qty; `supply_location_id` from line default → work centre line-side (stage) → site default | order service, one transaction (`WH-SC-609`: `CASING-01` 105, `BOLT-M8` 802) | FR-633 |
| PRO-T4-02 | Release (approved) with `component_reservation = SOFT`/`HARD` | one `whb_reservations` row per component line and location for min(required, allocatable), holder `(WAREHOUSE_MANUFACTURING, PRODUCTION_ORDER, orderId, componentLineNo)`; `NONE` creates none; `SOFT` carries `expires_at` = end of `planned_end_date` + `staging_stale_days` (site zone), re-dated when planned dates are edited (MD-23): a later date by `WhbReservationService.extend`, an **earlier** one by `release` + `create` in the same transaction, because `extend` moves later only (`WhbReservationService.java:212`; the re-created hold may be smaller — the shortage list shows it; R29 F18); a line with `supply_stock_status_code` set gets none (MD-30); reservations are made **only here, at release** — never at create (R29 F2); shortage is a computed field, not stored. These are the **only** reservations for the components: the order's MRQ reserves nothing and the store issue consumes them via `reservationsFor` (MD-16) | `WhbReservationService.create`, same transaction (`L-10`, `WH-SC-610`) | FR-635 |
| PRO-T4-03 | Release | `planned_cost` = Σ component required × current unit cost (`BOM-T4-05` method); missing cost → 0 and flagged in events | order service | FR-635 |
| PRO-T4-04 | Unrelease / Cancel | `releaseByHolder(WAREHOUSE_MANUFACTURING, PRODUCTION_ORDER, orderId)` with reason context `RESERVATION_RELEASE`; every MRQ of the order `WhMaterialRequisitionPort.cancel(CancelRequisitionCommand)` (envelope key `PRODUCTION_ORDER:<orderId>:MRQ_CANCEL:<mrqId>`, reason = the order's cancel reason) — a no-op success on a terminal MRQ with nothing issued (`MRQ-T1-21`) | reservation service, MRQ port, one transaction | FR-634 |
| PRO-T4-05 | Settlement posted (close) | remaining reservations released; open MRQ closed via `WhMaterialRequisitionPort.close` (open-to-issue → `closed_quantity`, `MRQ-T1-09`); component lines `CLOSED`; `closed_at`, `settlement_id` | settlement service → order service, one transaction | FR-656 |
| PRO-T4-06 | MSI / PRC postings | `issued_/returned_/staged_/unstaged_/consumed_quantity`, `received_/scrapped_/rejected_quantity`, `line_status` roll up (cited: `MSI-T4-*`, `PRC-T4-*`) | posting transaction | FR-638, FR-644 |
| PRO-T4-07 | Demand line cancelled or reduced below Σ live orders (read through `WhDemandOrderPort` on demand-order event) | a `DEMAND_CANCELLED` event on the order (banner on WS-324) and an `whm_mrp_exceptions` row at the next run; **order unchanged** | demand-order event listener (`WH-SC-617`) | FR-637 |
| PRO-T4-08 | Create | `PRD-` number from `whb_number_series` (gapless, per operator company + site, yearly) logged in `whb_number_series_issued`; survives cancel; a site created after `V560001` has no series → `409 NUMBER_SERIES_NOT_CONFIGURED` naming series and site (the issuer throws, `WhbDocumentNumberIssuer.java:159-162`); the admin adds it on the base number-series screen (R29 F32) | `WhbDocumentNumberIssuer.resolveSiteSeries` | FR-636 |
| PRO-T4-09 | Every transition | `whm_production_order_events` row (append-only) + audit log `PRODUCTION_ORDER_<EVENT>`; `@CacheEvict statistics.whmProductionOrder` | order service | FR-634 |
| PRO-T4-10 | MRP convert | proposal `CONVERTED`, `converted_document_type = PRODUCTION_ORDER`, id, ref | `mfg-mrp` | FR-666 |

---

## 5. T5 — Screen contract (web only)

### 5.1 `/warehouse/manufacturing/production-orders` — WS-323 Production Orders

| | |
|---|---|
| **Type** | list + transition modals (reference: **Service Vehicle**) |
| **Grid identifier** | `whm_production_orders` · filter scope `WAREHOUSE_MFG_PRODUCTION_ORDER` |
| **Default sort** | `e.planned_start_date ASC, e.priority ASC` |
| **Statistics tiles** | `PLANNED` · `RELEASED` · `IN_PROGRESS` · `COMPLETED` · late (`PRO-T3-01`) |
| **Columns** | `orderNumber`, `orderType`, `itemCode`, `itemName`, `bomCode`, `plannedQuantity`, `receivedQuantity`, `scrappedQuantity`, `rejectedQuantity`, `uomCode`, `priority`, `plannedStartDate` (date-only `formatDateSync`), `plannedEndDate` (date-only), `status`, `isOnHold` (badge), `shortageCount`, `demandSourceType`, `demandSourceRef`, `parentOrderNumber`, `workCentreName`, `warehouseName`, `releasedAt`, `completedAt` (timestamps, `formatDateWithTimezoneSync`), audit |
| **Filters** | `warehouseId` → `workCentreId` (enum, cascading); `status` (enum); `orderType` (enum); `itemId` typeahead; `priority` (enum); `isOnHold` (boolean); `demandSourceType` (enum); `plannedStartFrom`/`To` (`date`, dateOnly); `plannedEndFrom`/`To` (`date`, dateOnly); `lateOnly` (boolean); `orderNumber`, `demandSourceRef` (text) |
| **Row actions** | View → WS-324 · Edit → `PRO-T2-02` · Release → `-04` · Approve/Reject release → `-05` · Unrelease → `-06` · Hold/Resume (warning/success) → `-07` · Complete → `-08` · Reopen → `-09` · Cancel → `-10` · Close → `-11` |
| **Toolbar** | Add (manual / from demand line) → `PRO-T2-01` · Export |
| **Modals** | Add/Edit `Modal size="lg" minWidth={500} resizable` (tabs Header · Locations & tolerances · Demand); Release `lg` (shortage grid, acknowledge checkbox under `WARN`); Hold / Cancel / Reopen / Reject release `md` (reason + note); Complete `md` (close-short reason when under tolerance); Close `lg` (residual, split preview, approval note). Refusal inside the modal via `AlertBox`; Save gated only on client validation + loading |
| **Export columns** | grid columns + `createdByName`, `updatedByName` |

### 5.2 `/warehouse/manufacturing/production-orders/[id]` — WS-324 detail

| | |
|---|---|
| **Header** | number, status ladder, hold banner, `DEMAND_CANCELLED` banner, demand ref, BOM code, planned vs received, actions as WS-323 + **Print traveller** + **Re-explode** (`PLANNED`) |
| **Tabs** | **Components** (`lineNo`, item, `phantomPath`, `requiredQuantity`, `issuedQuantity`, `returnedQuantity`, `stagedQuantity`, `consumedQuantity`, `supplyMethod`, `supplyLocationCode`, `requiredDate`, `lineStatus`, `isUnplanned`, substitute-of, shortage) · **Outputs** · **Operations** · **Materials** (`MSI` §5.2) · **Receipts** (`PRC` §5.1 filtered) · **Quality** · **Cost** (planned vs actual, pool, absorbed, residual) · **Genealogy** (`WhbGenealogyQueryService.trace`) · **History** (`whm_production_order_events`: `occurredAt`, `eventType`, `fromStatus`, `toStatus`, reason, note, actor) |
| **Print** | `PRODUCTION_ORDER_TRAVELLER` (`PRO-T1-23`) |

### 5.3 `/warehouse/manufacturing/capacity-load` — WS-336 Capacity Load

| | |
|---|---|
| **Type** | report, read-only (grid + bar per day) |
| **Grid identifier** | `whm_capacity_load` · `WAREHOUSE_MFG_CAPACITY_LOAD` |
| **Columns** | as `mfg-mrp` WS-336: `workCentreCode`, `workCentreName`, `loadDate` (date-only), `availableMinutes`, `loadMinutes`, `loadPercent`, `isOverload`, `orderMinutes`, `proposalMinutes` |
| **Filters** | `warehouseId` → `workCentreId` (enum); `dateFrom`/`dateTo` (`date`, dateOnly, required, ≤ 92 days); `includeProposals` (boolean); `overloadOnly` (boolean) |
| **Rule** | **one rule, owned by `p10-13`: [`mfg-mrp.contract.md`](mfg-mrp.contract.md) §5.1** (MD-39, R29 F25) — open operations of `PLANNED`/`RELEASED`/`IN_PROGRESS` orders spread over the working days of `[planned_start_date, planned_end_date]`; `MAKE` proposals when included; `WH-SC-659`: 610 ÷ (480 × 0.9) = 141 % |
| **Actions** | Run · drill to orders · Export (`whm_reports:export`) |

### 5.4 `/warehouse/manufacturing/registers` — WS-337 Manufacturing Registers

| | |
|---|---|
| **Type** | report, tabbed; grid `whm_register_*` · scope `WAREHOUSE_MFG_REGISTER` |
| **Tabs · columns** | *Production register* (`receiptNumber`, `postingDate`, `orderNumber`, `itemCode`, `outputType`, `lotCode`, `goodQuantity`, `rejectedQuantity`, `scrappedQuantity`, `unitCost`, `extendedValue`) · *WIP by order* (`orderNumber`, `status`, `issuedValue`, `backflushedValue`, `returnedValue`, `absorbedValue`, `wipValue`) · *Scrap register* (`receiptNumber`, `itemCode`, `quantity`, `reasonCode`, `isAbnormal`, `value`) · *Yield* (`orderNumber`, `plannedQuantity`, `goodQuantity`, `yieldPercent`) · *Consumption variance* (`orderNumber`, `componentItemCode`, `requiredQuantity`, `consumedQuantity`, `varianceQuantity`, `deviationReason`) |
| **Filters** | `warehouseId`; `dateFrom`/`dateTo` (`date`, dateOnly, on `posting_date`); `itemId` typeahead; `orderId`; `status` (enum, WIP tab); `isAbnormal` (boolean, scrap tab) |
| **Export** | the active tab's columns (`whm_reports:export`); no `createdByName` (report, no audit columns — grid↔export parity) |

---

## 6. Out of scope (explicit decisions)

| Baseline item | Decision | Reason | Revisit |
|---|---|---|---|
| Automatic order from SO | not built | R-11 | convert on WS-334 |
| Finite scheduling / APS | not built | R-01 | — |
| Non-own owner (job work in) | refused in MFG v1.1 | `OD-42` | v1.2 |
| Disassembly order type | not built | R-07 | code-list row |
| Settlement arithmetic, cost sheet | `mfg-costing-close.contract.md` | cited | — |
| Staging / issue / receipt | `MSI`, `PRC` contracts | cited | — |
| Mobile | none | R-13 | — |

---

## 7. Amendments

| Date | Row IDs affected | Change | Found by |
|---|---|---|---|
| 2026-10-22 | all | v0 derived from `FRD-MFG.md`, code evidence and research catalogue; unratified | contract derivation (P10 design) |
| 2026-10-22 | `PRO-T1-04`, `-06`, `-07`, `-12`, `-20`, `PRO-GRD-08`, `-10`, `-23`, `PRO-T4-01`, `-02`, `-04`, `-08`, §5.3, `PRO-OPEN-06` | R29: rework line unreserved (F2, MD-30); cancel/unrelease block only on issued MRQs and cancel the rest through the port (F4); SOFT re-dated earlier by release + create (F18); no edit while release pending (F22); one capacity-load rule (F25, MD-39); confirmation never sets `IN_PROGRESS` (F28); process loss (F29); unconfigured series (F32) | `R29-functional-review-mfg.md` |
| 2026-10-23 | `PRO-T1-03`, `-09`…`-12`, `PRO-GRD-04`, `-09`, `-15`, `-23`, §1.1, Source column on T1–T4, `PRO-OPEN-02` | R31: `release_requested_by/at` (`PRO-OPEN-02` DECIDE); close guard owned by CST and cited (F-MF-006); one code per predicate with SUB (F-MF-019); MRP converts a `SUBCONTRACT` order (F-MF-014); Source FR on every rule row (F-MF-018) | `R31-functional-review-mfg.md`, `R31-decisions.md` |
| 2026-10-22 | T1, T4, §9 | Consistency pass: `COMPLETED` not settled (MD-14), no cancel after posting (MD-15), single reservation owner (MD-16), selection on planned start (MD-19), `403` (MD-21), SOFT expiry (MD-23), rework supply status (MD-26), `MACHINE_DOWN` seeded | FRD-MFG §9 |
| 2026-10-25 | R32 (`D-20`): §12 — order approval mode and `SHORT_CLOSED`, shortage release modes (default `APPROVE`), shortage list with PO ETA and capacity, multi-demand orders, optional auto-create, routing / batch snapshot at release, ECN re-explode, R32 register tabs (FR-823…FR-826) |
| 2026-10-25 | §12 `PRO-T1-50`, `PRO-GRD-50` | R32 fix wave (mfg-eng): the `SAMPLE` order type with its trial-version release exception, `SAMPLE`-status receipt and own cost pool; the sample gate on create / release / reservation / auto-create (F-R32ME-008, -001, -002) | `R32-functional-review-mfg-eng.md` |
| 2026-10-25 | §0, §1.1, `PRO-T1-08`…`-12`, `-15`, `-20`, `-21`, `PRO-GRD-09`, `-10`, `-12`, §12 `PRO-T1-40`, `-40a`, `-41`, `-42`, `-46`, `-47` | R32-fix: `APPROVED` / `SHORT_CLOSED` merged into the ladder, release and cancel from `APPROVED` (F-R32MS-005); unrelease / cancel cancel batches, cards and units and are refused once a card started, `PRODUCTION_STAGE_CONSUMPTION` counts (F-R32MS-006); order approval and release approval through the engine (`WHM_PRODUCTION_ORDER`, `WHM_SHORTAGE_RELEASE`), amendment after approval (F-R32MS-008, `D-21` item 6); one pending release track with reject / withdraw (F-R32MS-017); close modal figures (F-R32MS-026) | `R32-functional-review-mfg-shop.md` |

---

## 8. Invariants and scenarios this workflow must not break

| Invariant | Rows that carry it | Scenarios that prove it |
|---|---|---|
| Snapshot isolation | `PRO-T4-01`, `PRO-UNR-02` | `WH-SC-609`, `WH-SC-612` |
| `L-6` / `L-10` reservations | `PRO-GRD-08`, `PRO-T4-02`, `-04` | `WH-SC-610`, `WH-SC-611`, `WH-SC-613` |
| No cancel after posting | `PRO-GRD-10` | `WH-SC-614` |
| Hold blocks postings | `PRO-GRD-11` | `WH-SC-615` |
| MTO never auto-cancelled | `PRO-T4-07`, `PRO-UNR-05` | `WH-SC-616`, `WH-SC-617` |
| Reopen only before settlement | `PRO-GRD-14` | `WH-SC-644` |
| `CLOSED` refuses issues | `PRO-T1-22`, `MSI-GRD-07` | `WH-SC-641`, `WH-SC-642`, `WH-SC-643` |
| `L-14` house owner only | `PRO-GRD-17` | `WH-SC-652` |
| Infinite capacity | `PRO-UNR-08` | `WH-SC-659` |

---

## 9. Open rows

| ID | Contradiction / hole | Proposed resolution | Authority | Status |
|---|---|---|---|---|
| PRO-OPEN-01 *(resolved — MD-15)* | `WH-SC-614` refuses cancel of an order with a posted staging and offers "unstage first" — but FR-634 makes the first posting set `IN_PROGRESS`, from which Cancel is not allowed and which unstage never regresses; "unstage first" cannot make cancel possible | the refusal offers *Unstage* + *Complete short* (manual complete with close-short reason) + *Close*; never cancel | FR-634 vs `WH-SC-614` | resolved |
| PRO-OPEN-02 *(resolved — R31-decisions DECIDE: the alternative taken)* | `release_requires_approval` has no status and no `release_requested_*` columns — only `released_by/at` and `release_approved_by/at` | **adopted:** `release_requested_by/at` added (FRD §4); pending = `PLANNED` + `release_requested_at` set + `released_at` null; `released_*` is stamped only at actual release (`PRO-T1-09`…`-12`, `PRO-GRD-09`, `-23`) | FR-635, §4 | resolved |
| PRO-OPEN-03 *(resolved — MD-14; STORES `FR-533` amended)* | FR-640 / `MSI-GRD-07` refuse a store issue to an order not `RELEASED`/`IN_PROGRESS`, but FR-656 and `WH-SC-641` require a **late issue after the final receipt** on a `COMPLETED` order, and returns after final receipt | resolver admits `COMPLETED` for issues/returns (consumption policy still applies); `CLOSED` refused (`WH-SC-643`) | FR-640 vs FR-656 | resolved |
| PRO-OPEN-04 *(resolved — FRD §3.1 now seeds the four values)* | Reason context `PRODUCTION_HOLD` lists no values; `WH-SC-615` uses `MACHINE_DOWN` | seed `MACHINE_DOWN`, `MATERIAL_SHORTAGE`, `QUALITY_ISSUE`, `PLANNER_HOLD` in `V560001` | FRD §3.1 | resolved |
| PRO-OPEN-05 *(resolved — MD-23)* | `component_reservation = SOFT` but `whb_reservations` requires `expires_at` for `SOFT` (`V500033:416-417`); FRD sets no expiry | SOFT expiry = `planned_end_date` + `staging_stale_days` | evidence §5 | resolved |
| PRO-OPEN-06 *(resolved — R29 F28)* | Whether an operation confirmation (no movement) counts as the "first posting" that sets `IN_PROGRESS` | **no** — movements only; a confirmation stamps `actual_start_at` only (`QRW-T1-01`) | FR-634, FR-651 | resolved |

## 12. R32 rules (PRD 2026-10-24, `D-20`)

Owning task: `issues/p10-05.md` `## R32 additions (PRD 2026-10-24)` (FR-824…FR-826); registers `issues/p10-13.md` (FR-823).

| ID | Rule | Refusal / effect | Source |
|---|---|---|---|
| PRO-T1-40 | *Submit for approval* (`whm_production_orders:submit`) of a `PLANNED` order the `order_approval_mode` applies to (`MTS_ONLY`: no demand link; `ALL`) opens one engine request of type `WHM_PRODUCTION_ORDER` (`p8-30`; approve verb `whm_production_orders:approve`, default policy `SINGLE_LEVEL`, `excludedActorIds` frozen = creator + submitter) — the order is *order approval pending* | `409 APPROVAL_PENDING` on a second submit; `422` when the mode does not apply | FR-824 |
| PRO-T1-40a | The engine's final approval sets `APPROVED` (`approved_by/at` = the last approver); value bands, levels and upward escalation are the engine's | kept code `403 ORDER_SELF_APPROVAL` for `DAP-GRD-03` (maker / submitter / prior level; `ADMIN` refused too) | FR-824 |
| PRO-T1-46 | *Amend* an `APPROVED` order (`whm_production_orders:edit`, reason from `DOCUMENT_AMENDMENT`): the order returns to `PLANNED` with `document_revision` + 1 and the edit applied; release then needs a new approval of the new revision | `409 DOCUMENT_APPROVED_LOCKED` on an in-place edit of an `APPROVED` order | FR-824 |
| PRO-T1-47 | Engine reject (reason `APPROVAL_REJECT`) or requester withdraw of a `WHM_PRODUCTION_ORDER` request: the order stays `PLANNED`, editable and resubmittable | — | FR-824 |
| PRO-GRD-40 | Release of an order the mode applies to needs `APPROVED` | `409 ORDER_NOT_APPROVED` | FR-824 |
| PRO-T1-41 | *Close* of a `COMPLETED` order completed with a `PRODUCTION_CLOSE_SHORT` reason ends `SHORT_CLOSED` (terminal, in the §1.1 inventory; same settlement guards as `CLOSED`, `CST-GRD-02`…`-08`; the settlement post sets it in place of `PRO-T1-22`'s `CLOSED`) | status distinguishes short-closed orders | FR-824 |
| PRO-T1-42 | Release with shortage under `APPROVE` (default) is the `PRO-T1-09` request — **one pending state per order** (the *release pending approval* track, engine type `WHM_SHORTAGE_RELEASE` with `has_shortage = true`; `shortage_release_requested_by/at` stamped with `release_requested_by/at`); approve → `PRO-T1-10`, reject → `PRO-T1-11`, withdraw → `PRO-T1-11a`; `shortage_release_approved_by/at` = the final approver; `BLOCK` refuses; `WARN` releases with the list; `ALLOW` reads as `WARN` | `409 SHORTAGE_RELEASE_NEEDS_APPROVAL` (a direct release attempt while a shortage needs approval); kept code `403 RELEASE_SELF_APPROVAL` for `DAP-GRD-03` (DAP §0.1); `409 RELEASE_SHORTAGE` | FR-825 |
| PRO-T5-10 | The release dialog's shortage list shows per short component the open PO quantity and earliest ETA (core PO schedule lines) and the routing work centres' load over the order's dates (`mfg-mrp` §5.1 rule) | display | FR-825 |
| PRO-GRD-41 | `whm_production_order_demands`: same item and site; Σ quantities ≤ planned; each demand line on one live order at a time | `422 DEMAND_EXCEEDS_ORDER`; `409 DEMAND_LINE_ON_OTHER_ORDER` | FR-826 |
| PRO-T4-20 | Output reservations of a multi-demand order split by demand line in `seq` order at receipt / QC release (FR-637 rule per line) | — | FR-826 |
| PRO-T1-43 | With `create_order_from_demand_line` = `true`, a new demand line of a MAKE item creates a `PLANNED` order (demand link set, never released automatically) | idempotent per demand line | FR-826 |
| PRO-T1-44 | Release of a job-card item snapshots the routing (`SFL-GRD-05`) and creates batches and job cards (`SFL-T1-10`, `-11`) in the release transaction | `409 ROUTING_NOT_EFFECTIVE` | FR-633 |
| PRO-T1-45 | ECN implement may re-explode a `RELEASED` order with nothing posted (decision `RE_EXPLODE_UNSTARTED`): reservations released and re-made on the new snapshot | `409 ORDER_HAS_POSTINGS` when something posted meanwhile | FR-633 |
| PRO-T5-11 | WS-337 R32 tabs: time variance, operator output, first-pass yield by routing stage, PDI pass %, SPC, batch variance, full unit cost, sample cost — backend registers, exportable, AUDITOR read-only | display | FR-823 |
| PRO-T1-50 | **`SAMPLE` order type** (`WHM_ORDER_TYPE` + `SAMPLE`, FR-799): created only from a sample request iteration (`ECH-T1-22`, `-27`) by `whm_sample_requests:create_order`, `sample_request_id` / `sample_iteration_id` set; may freeze a **trial** BOM / routing (`DRAFT` / `SUBMITTED`, `is_trial`) — at release `PRO-GRD-07` and `SFL-GRD-05` accept the trial version for this type only; the drawing revision ≥ `RELEASED_FOR_SAMPLE`; never covers a demand line (FR-826), never auto-created, never under the sample gate; output received into stock status `SAMPLE` at the *Sample store* location when `p8-22` names one (`PRC` receipt rule, `p10-07`), its pool reported as sample cost (`CST-T4-30`) | `422 TRIAL_BOM_ONLY_ON_SAMPLE_ORDER` (trial version on any other type); `409 SAMPLE_DRAWING_NOT_RELEASED` | FR-799 |
| PRO-GRD-50 | **Sample gate** on `STANDARD` orders: create, release and output reservation for a demand line marked *sample approval required* refused while `ECH-GRD-10` is closed; `create_order_from_demand_line` (`PRO-T1-43`) creates nothing for such a line and alerts the planner (`ECH-T4-10`) | `409 SAMPLE_APPROVAL_PENDING` naming line and request | FR-801, FR-826 |
