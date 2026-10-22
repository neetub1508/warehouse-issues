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
| **Domain baseline** | FRD-MFG §3.1 registries, §4 order tables, §5 ladder, `MD-02`, `MD-12`; `DECISIONS.md` `L-6` (allocatable), `L-10` (reservation holder quad), `L-14` (non-own never valued); `RJ-005` (one verb per transition) |
| **Owning task bodies** | `p10-05` (`V560030` · `V561030`) · `p10-13` (`V561110` report grids). Depends on `p10-02`, `p10-03`, `p8-02` |
| **Primary tables** | `whm_production_orders`, `whm_production_order_components`, `_outputs`, `_operations`, `_events` |
| **Status columns** | `whm_production_orders.status` (`PLANNED`/`RELEASED`/`IN_PROGRESS`/`COMPLETED`/`CLOSED`/`CANCELLED`) + flag `is_on_hold`; component `line_status`, operation `status` derived on write — **no `CHECK`** (`D-10`) |
| **Permission resources** | `whm_production_orders:{view,create,edit,export,release,approve_release,unrelease,hold,complete,reopen,cancel,substitute,request_materials,close}` (`substitute`, `request_materials` → `MSI`) · `whm_reports:{view,export}` (WS-336, WS-337). Hold and Resume share `:hold`. AUDITOR `:view` only |
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
| Order | `PLANNED` | `status` | `PRO-T1-01`…`-05`, `-12` | `-08`, `-10`, `-20` | initial, editable |
| Order | *release pending approval* (derived) | `PLANNED` with `released_by/at` set and `release_approved_by` null (`PRO-OPEN-02`) | `PRO-T1-09` | `-10`, `-11` | active |
| Order | `RELEASED` | `status`; `released_by/at` (+ `release_approved_by/at`) | `PRO-T1-08`, `-10` | `-12`, `-15`, `-20` | active |
| Order | `IN_PROGRESS` | `status`; `actual_start_at` | `PRO-T1-15`, `-18`, `-19` | `-16`, `-17` | active |
| Order | `COMPLETED` | `status`; `completed_by/at`, `actual_end_at` | `PRO-T1-16`, `-17` | `-18`, `-19`, `-21` | active |
| Order | `CLOSED` | `status`; `closed_at`, `settlement_id` | `PRO-T1-22` (effect) | none | **terminal** |
| Order | `CANCELLED` | `status`; `cancel_reason_code_id`, `cancel_note` | `PRO-T1-20` | none | **terminal** |
| Order flag | *on hold* | `is_on_hold = true`; `hold_reason_code_id`, `hold_note`, `held_by/at` | `PRO-T1-13` | `PRO-T1-14` | orthogonal to `RELEASED`/`IN_PROGRESS` |
| Component line | `OPEN`/`PARTIAL`/`COMPLETE`/`CLOSED` | `line_status`, derived from required vs consumed on every write | effects (`MSI`, `PRC`) | `CLOSED` at order close/cancel | derived |
| Operation | `OPEN`/`STARTED`/`CONFIRMED` | `whm_production_order_operations.status` | `mfg-qc-rework` confirmations | — | derived |

### 1.2 Transitions

Every transition appends one `whm_production_order_events` row (`event_type`, `from_status`,
`to_status`, reason, note, actor, `occurred_at`) in the same transaction (`PRO-T4-09`).

| ID | From | Event / action | To | Guard (service, first) | Actor (permission) | Side effects | Comment/reason required | UI entry point |
|---|---|---|---|---|---|---|---|---|
| PRO-T1-01 | — | **Create (manual)**: type, item, planned qty + UoM, priority, planned start/end, receipt / line-side locations, work centre, consumption policy, tolerances, planned lot, optional explicit BOM | `PLANNED`, `demand_source_type = MANUAL` | `PRO-GRD-01`…`-06`, `-17`, `-18`, `-20` | `whm_production_orders:create` | `PRD-` number issued at create (gapless per site, `PRO-T4-08`); snapshot (`PRO-T4-01`); policy / tolerances default from settings when null | no | WS-323 toolbar **Add** |
| PRO-T1-02 | — | **Create from demand line** (MTO) | `PLANNED`, `demand_source_type = DEMAND_ORDER` | `PRO-T1-01` guards + `PRO-GRD-19` | `whm_production_orders:create` | `demand_source_id/line_id` stored; `demand_source_ref` frozen (SO no./line, customer); `reserve_output_for_demand` as chosen | no | WS-323 **Add** → *From demand line* picker |
| PRO-T1-03 | — | *(effect)* MRP `MAKE` proposal converted | `PLANNED`, `demand_source_type = MRP`, `mrp_proposal_id` | `PRO-T1-01` guards | `whm_mrp_proposals:convert` | sub-assembly proposals → child orders with `parent_order_id`, `demand_source_type = PARENT_ORDER` (`PRO-T1-05`) | — | none here — WS-334 **Convert** (`mfg-mrp`) |
| PRO-T1-04 | — | *(effect)* QC `REWORK` disposition `onDisposition` | `PLANNED`, `order_type = REWORK`, `demand_source_type = QC_REWORK`, `rework_of_inspection_id` | `PRO-GRD-01` (rework BOM optional — `bom_id` may be null), `-02` | system (QC disposition by `wh_quality_inspections:disposition`) | first component = rejected item/lot, `supply_stock_status_code = REJECTED`, `BACKFLUSH`, **no reservation** (core admits none on a non-allocatable status; MD-26, MD-30); output = same item; lot kept per `rework_keeps_lot` | — | none — WS-080 disposition (`mfg-qc-rework`) |
| PRO-T1-05 | — | Create a sub-assembly child order from a parent | `PLANNED`, `parent_order_id` | `PRO-T1-01` guards | `whm_production_orders:create` | child's main output = parent component item; child need date = parent component `required_date` | no | WS-324 Components tab **Make sub-assembly** |
| PRO-T1-06 | `PLANNED` (any field) · `RELEASED`/`IN_PROGRESS` (priority, planned dates, notes, work centre only) | Edit | unchanged | `PRO-GRD-05`, `-06`, `-20`, `-23`; quantity / BOM / item edits only in `PLANNED` (`PRO-GRD-12`) | `whm_production_orders:edit` | quantity change in `PLANNED` re-scales the snapshot (`PRO-T1-07`) | no | WS-323/WS-324 **Edit** |
| PRO-T1-07 | `PLANNED` | **Re-explode** (re-select BOM and rebuild components / outputs / operations) | unchanged | `PRO-GRD-01`, `-23`; nothing issued (`PRO-GRD-10`) | `whm_production_orders:edit` | snapshot replaced; `bom_id` updated; event `RE_EXPLODED` | no | WS-324 **Re-explode** (shown only in `PLANNED`, `WH-SC-612`) |
| PRO-T1-08 | `PLANNED`, `release_requires_approval = false` | **Release** | `RELEASED` | `PRO-GRD-07`, `-08`, `-11`, `-21` | `whm_production_orders:release` | reservations (`PRO-T4-02`); `planned_cost` rolled (`PRO-T4-03`); `released_by/at`; traveller printable | shortage acknowledgement under `WARN` (`PRO-GRD-08`) | WS-323 row **Release** modal (shows shortage list) |
| PRO-T1-09 | `PLANNED`, `release_requires_approval = true` | **Release (request)** | *release pending approval* | `PRO-GRD-07`, `-08` | `whm_production_orders:release` | `released_by/at` stamped; no reservation yet; approvers notified (`PRO-T3-03`) | as `PRO-T1-08` | WS-323 row **Release** |
| PRO-T1-10 | *release pending approval* | **Approve release** | `RELEASED` | `PRO-GRD-09`; `PRO-GRD-07`, `-08` re-run (stock may have moved) | `whm_production_orders:approve_release` | `release_approved_by/at`; `PRO-T4-02`, `-03` | no | WS-323 row **Approve release** |
| PRO-T1-11 | *release pending approval* | Reject release | `PLANNED` (pending cleared) | `PRO-GRD-09` | `whm_production_orders:approve_release` | `released_by/at` cleared; event `RELEASE_REJECTED` | **yes** | WS-323 row **Reject release** |
| PRO-T1-12 | `RELEASED` | **Unrelease** | `PLANNED` | `PRO-GRD-10`, `-11` | `whm_production_orders:unrelease` | reservations released and open MRQs cancelled through the port (`PRO-T4-04`); `released_*`, `release_approved_*` cleared; `planned_cost` kept | no | WS-323 row **Unrelease** |
| PRO-T1-13 | `RELEASED` · `IN_PROGRESS`, not on hold | **Hold** | flag set | `PRO-GRD-16` (reason in `PRODUCTION_HOLD`) | `whm_production_orders:hold` | reservations **kept**; every posting refused while set (`PRO-GRD-11`) | **yes** — reason + note | WS-323 row **Hold** modal |
| PRO-T1-14 | on hold | **Resume** | flag cleared | — | `whm_production_orders:hold` | `hold_*` cleared (history in events) | no | WS-323 row **Resume** |
| PRO-T1-15 | `RELEASED` | *(effect)* first posting of any kind for the order — `PRODUCTION_STAGE` (`MSI-T1-04`), store issue (`MSI-T1-09`), receipt (`PRC-T1-04`), subcontract dispatch | `IN_PROGRESS` | never set directly | the poster | `actual_start_at` = the posting's `occurred_at` | — | none (effect) |
| PRO-T1-16 | `IN_PROGRESS` | **Complete** (manual) | `COMPLETED` | `PRO-GRD-11`, `-13` | `whm_production_orders:complete` | `completed_by/at`, `actual_end_at`; remaining open reservations **kept** until close — `COMPLETED` still accepts late store issues and returns through the resolver until `CLOSED` (MD-14); open operations left as is | `PRODUCTION_CLOSE_SHORT` reason when received good < planned × (1 − under %) | WS-323 row **Complete** modal |
| PRO-T1-17 | `IN_PROGRESS` | *(effect)* receipt posted with `is_final = true` (`PRC-T1-04`/`-06`) | `COMPLETED` | `PRC-GRD-06` (close-short reason on the receipt) | `whm_production_receipts:post` / `:approve` | as `PRO-T1-16` | on the receipt | none (effect) |
| PRO-T1-18 | `COMPLETED`, no live settlement | **Reopen** | `IN_PROGRESS` | `PRO-GRD-14` | `whm_production_orders:reopen` | `completed_*` cleared; event keeps them | **yes** — `PRODUCTION_REOPEN` reason | WS-323 row **Reopen** modal |
| PRO-T1-19 | `COMPLETED` | *(effect)* a receipt reversal posted (`PRC-T1-13`) | `IN_PROGRESS` | `PRC-GRD-24` | `whm_production_receipt_reversals:post` | rollups regress | — | none (effect) |
| PRO-T1-20 | `PLANNED` · `RELEASED` (incl. pending approval) | **Cancel** | `CANCELLED` | `PRO-GRD-10`, `-16` (`PRODUCTION_CANCEL`) | `whm_production_orders:cancel` | reservations released and open MRQs cancelled through the port (`PRO-T4-04`); component lines `CLOSED`; MRP proposal link kept; number stays issued | **yes** | WS-323 row **Cancel** modal |
| PRO-T1-21 | `COMPLETED` | **Close** — computes the residual and creates the settlement | `COMPLETED` (settlement `DRAFT`, or posted at once → `PRO-T1-22`) | `PRO-GRD-15` | `whm_production_orders:close` | settlement per `mfg-costing-close` (residual, `close_variance_approval_percent`); when under threshold it posts in the same transaction | no | WS-323 row **Close** modal (shows residual, split, approval need) |
| PRO-T1-22 | `COMPLETED` | *(effect)* settlement `POSTED` | `CLOSED` | settlement guards (`mfg-costing-close`) | `whm_production_settlements:post` / `:approve` | `PRO-T4-05`: reservations released, MRQ closed through `WhMaterialRequisitionPort.close`, component lines `CLOSED`, `closed_at`, `settlement_id` | — | none (effect); WS-329 |
| PRO-T1-23 | any but `CANCELLED` | **Print traveller** | unchanged | — | `whm_production_orders:view` | `PRODUCTION_ORDER_TRAVELLER`: header, barcode, demand ref, components (required / issued / supply method), operations with QC checkpoints, output lots | no | WS-324 toolbar **Print traveller** |

### 1.3 Guards

| ID | Predicate (must hold to proceed) | Refusal: HTTP · code · field | Message shape | DB backstop | Source |
|---|---|---|---|---|---|
| PRO-GRD-01 | A BOM resolves by `BOM-T1-13` on `planned_start_date` (MD-19; re-checked at release by `PRO-GRD-07`) for usage `PRODUCTION` (`STANDARD`/`REWORK`) or `SUBCONTRACT` (`SUBCONTRACT`); an explicit BOM's usage matches the type; `REWORK` may have none | `422 BOM_NOT_FOUND` · `bomId`; `422 BOM_USAGE_MISMATCH` *(proposed)* · `bomId` | item, site, date, usage | FK `bom_id` | FR-626, FR-633, FR-658 |
| PRO-GRD-02 | `planned_quantity > 0`; UoM convertible to item base (factor frozen into `conversion_factor_used`) | `422 UOM_NOT_CONVERTIBLE` · `uomCode`; `422` · `plannedQuantity` | — | CHECK | FR-632, `FR-143` |
| PRO-GRD-03 | The item is not a phantom (`BOM-GRD-12`'s predicate) and is stock-holding | `422 PHANTOM_ITEM_NOT_PRODUCIBLE` *(proposed)* · `itemId` | — | — | FR-627 |
| PRO-GRD-04 | `order_type` active in `WHM_ORDER_TYPE`; `SUBCONTRACT` carries `subcontractor_counterparty_id` and a `subcontract_location_id` of type `JOB_WORKER` at the site; non-subcontract types carry neither | `422 SUBCONTRACTOR_REQUIRED` *(proposed)* · `subcontractorCounterpartyId` / `subcontractLocationId` | — | composite FK | FR-658 |
| PRO-GRD-05 | `planned_end_date ≥ planned_start_date` | `422 PLANNED_END_BEFORE_START` *(proposed)* · `plannedEndDate` | — | — | FR-632 |
| PRO-GRD-06 | `receipt_location_id` is physical stock-holding at the order's site; `line_side_location_id` of type `LINE_SIDE` at the site; work centre active at the site; tolerances ≥ 0 | `422 RECEIPT_LOCATION_INVALID` · `receiptLocationId`; `422 LINE_SIDE_LOCATION_INVALID` · `lineSideLocationId` *(proposed)* | names type found | FK | FR-632 |
| PRO-GRD-07 | Release: frozen BOM `APPROVED` and current on `planned_start_date` (`REWORK` without BOM exempt); `receipt_location_id` set; ≥ 1 component or a `REWORK` order | `409 BOM_NOT_EFFECTIVE` *(proposed)* · `bomId`; `422 RECEIPT_LOCATION_REQUIRED` · `receiptLocationId` | names BOM range and start | — | FR-635 |
| PRO-GRD-08 | Shortage per component = required base − allocatable free stock at the site (`L-6`, house owner only); for a line with `supply_stock_status_code` set (a rework order's `REJECTED` line) = required base − on-hand **in that status** at its supply location less open reservations (MD-30, R29 F2). `BLOCK`: any shortage refuses; `WARN`: request carries `acknowledgeShortage = true`; `ALLOW`: proceeds | `409 RELEASE_SHORTAGE` · `components` listing item, required, available, short; `422 SHORTAGE_ACK_REQUIRED` *(proposed)* · `acknowledgeShortage` | `IMPELLER-02 short 40` | — | FR-635, `WH-SC-610`, `-611` |
| PRO-GRD-09 | Approve/reject release: actor ≠ `released_by` | `403 RELEASE_SELF_APPROVAL` *(MD-21)* · banner | names the requester | — | FR-635, `MD-12` |
| PRO-GRD-10 | Cancel / Unrelease / Re-explode: no posted `PRODUCTION_STAGE`, store issue, receipt or dispatch for the order; no staging list beyond `DRAFT`/`CANCELLED`; **no MRQ of the order with Σ issued > 0** (read by `WhMaterialRequisitionPort.getRequisitionPosition`, `MRQ-T1-23`) — an MRQ that is `DRAFT`/`SUBMITTED`/`APPROVED` with nothing issued, or `REJECTED`/`CLOSED`/`CANCELLED`, never blocks: the transition cancels it through the port's `cancel`, a no-op on a terminal one (`MRQ-T1-21`; R29 F4) | `409 ORDER_HAS_POSTINGS` · banner naming each document (`STG-000031`, `MRQ-…`) | an order with a posting is `IN_PROGRESS` and never cancels: the banner offers *Unstage* / store return, then *Complete* (close-short reason) and *Close* (MD-15) | — | FR-634, `WH-SC-614` |
| PRO-GRD-11 | No posting, release, stage, request or receipt while `is_on_hold`; the resolver refuses the same (`MSI-GRD-07`) | `409 ORDER_ON_HOLD` · banner | names hold reason | — | FR-634, `WH-SC-615` |
| PRO-GRD-12 | The transition's `From` matches the current status (table above); item / BOM / quantity edits only in `PLANNED` | `409 ORDER_TRANSITION_INVALID` *(proposed)* · banner | names current and requested | `@Version` | FR-634 |
| PRO-GRD-13 | Complete: no receipt `DRAFT`/`PENDING_APPROVAL`; under-receipt below planned × (1 − `under_receipt_percent`, order → setting) needs `PRODUCTION_CLOSE_SHORT` | `409 ORDER_HAS_OPEN_RECEIPT` *(proposed)* · banner; `422 CLOSE_SHORT_REASON_REQUIRED` · `closeShortReasonCodeId` | received vs threshold | — | FR-647, `WH-SC-629` |
| PRO-GRD-14 | Reopen: no settlement in `DRAFT`/`APPROVED`/`POSTED` for the order (`REJECTED` does not count); reason in `PRODUCTION_REOPEN` | `409 ORDER_SETTLEMENT_EXISTS` *(proposed)* · banner | names `PST-` number | partial unique index `settlement.order_id WHERE status <> 'REJECTED'` (MD-22) | FR-634, `WH-SC-644` |
| PRO-GRD-15 | Close: status `COMPLETED`; no staging list `RELEASED`/`PARTIALLY_STAGED`; no receipt `DRAFT`/`PENDING_APPROVAL`; no subcontract balance open (`mfg-subcontracting`); no live settlement already | `409 ORDER_CLOSE_BLOCKED` *(proposed)* · banner listing blockers; `409 SUBCONTRACT_BALANCE_OPEN` (subcontract) | lists each blocker | — | FR-656, FR-661, `WH-SC-648` |
| PRO-GRD-16 | Reason codes belong to the transition's context (`PRODUCTION_HOLD`, `PRODUCTION_CANCEL`, `PRODUCTION_REOPEN`, `PRODUCTION_CLOSE_SHORT`) and are active | `422 REASON_CODE_INVALID` · `reasonCodeId` | — | FK `whb_reason_codes` | FR-634 |
| PRO-GRD-17 | Owner = house owner of the site's operator company (non-own refused in v1, `OD-42`) | `422 OWNER_NOT_HOUSE` *(proposed)* · `ownerId` | — | FK | FR-632, `L-14` |
| PRO-GRD-18 | Same company: item, BOM, locations, counterparty belong to the order's company | `422 COMPANY_MISMATCH` · the field | — | — | `MPR-GRD-08` (same rule) |
| PRO-GRD-19 | Demand line: exists via `WhDemandOrderPort`, open (not cancelled/fulfilled), same site, same item; Σ live orders' planned for that line ≤ its open quantity (warn above) | `422 DEMAND_LINE_INVALID` *(proposed)* · `demandSourceLineId` | names SO/line state | — | FR-637 |
| PRO-GRD-20 | `priority ∈ 1..5` | `422` · `priority` | — | CHECK | FR-632 |
| PRO-GRD-21 | Concurrency: release / unrelease / cancel / complete / close lock the order row (`FOR UPDATE`) and check `version` | `409 CONCURRENT_MODIFICATION` · banner | — | `@Version` | — |
| PRO-GRD-22 | Record scope: the order's site is in the user's allowed warehouses | `404` | — | `WHERE` in every query | `D-14` |
| PRO-GRD-23 | Edit / Re-explode while the release is pending approval (`PLANNED`, `released_at` set, `release_approved_at` null) is refused — the approver must approve the request as made; reject it first (R29 F22) | `409 RELEASE_PENDING_APPROVAL` *(proposed)* · banner | names the requester and `released_at` | — | FR-634, FR-635 |

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
| PRO-UNR-09 | Widening `wh_work_orders` for production | separate document (`MD-02`) | `RN-033` |

---

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from | Extra condition |
|---|---|---|---|---|
| PRO-T2-01 | Add / from demand line / sub-assembly | `whm_production_orders:create` | — | planner |
| PRO-T2-02 | Edit | `whm_production_orders:edit` | `PLANNED` (all); `RELEASED`·`IN_PROGRESS` (priority, dates, notes, work centre) | not while a release is pending approval (`PRO-GRD-23`) |
| PRO-T2-03 | Re-explode | `whm_production_orders:edit` | `PLANNED` | nothing issued; release not pending |
| PRO-T2-04 | Release | `whm_production_orders:release` | `PLANNED` (no pending request) | — |
| PRO-T2-05 | Approve / Reject release | `whm_production_orders:approve_release` | *release pending approval* | actor ≠ requester |
| PRO-T2-06 | Unrelease | `whm_production_orders:unrelease` | `RELEASED` | nothing posted/staged/issued (`PRO-GRD-10`) |
| PRO-T2-07 | Hold · Resume | `whm_production_orders:hold` | `RELEASED`·`IN_PROGRESS` not held · held | supervisor |
| PRO-T2-08 | Complete | `whm_production_orders:complete` | `IN_PROGRESS` | not held |
| PRO-T2-09 | Reopen | `whm_production_orders:reopen` | `COMPLETED` | no live settlement |
| PRO-T2-10 | Cancel | `whm_production_orders:cancel` | `PLANNED`·`RELEASED` | nothing posted/staged/issued (`PRO-GRD-10`) |
| PRO-T2-11 | Close | `whm_production_orders:close` | `COMPLETED` | `PRO-GRD-15` |
| PRO-T2-12 | View · traveller | `whm_production_orders:view` | any (traveller not `CANCELLED`) | cost accountant, auditor |
| PRO-T2-13 | Export | `whm_production_orders:export` | any | not AUDITOR |
| PRO-T2-14 | Capacity load / registers view · export | `whm_reports:view` · `:export` | — | export not AUDITOR |

---

## 3. T3 — Time-driven rules & notifications

| ID | Rule | Trigger | What it changes | Who is notified | Channel | Job class | Notify-once? |
|---|---|---|---|---|---|---|---|
| PRO-T3-01 | **Late order**: `planned_end_date < today` (site TZ) and status `PLANNED`/`RELEASED`/`IN_PROGRESS` | daily scheduler (own actor, never ADMIN) | nothing stored — `lateOnly` filter + tile computed on read | planner (order `created_by`) and supervisors of the work centre | in-app | `WhmLateOrderAlertJob` (`whb_job_runs`) | once per order per day of lateness change |
| PRO-T3-02 | **Late start**: `planned_start_date < today` and still `PLANNED`/`RELEASED` | same job | none | planner | in-app | same job | once |
| PRO-T3-03 | Release pending approval escalation after `warehouse.approval.pending_alert_hours` | elapsed since `released_at` | nothing — never auto-approves | holders of `:approve_release` | core pending-approval alert (`p2-23`) | core job | one per episode |
| PRO-T3-04 | `RELEASED` order on hold longer than `staging_stale_days` | daily | none | production manager | in-app | `WhmLateOrderAlertJob` | once per hold episode |

---

## 4. T4 — Cross-entity effects

| ID | When this happens | Then this other record must change | Enforced in |
|---|---|---|---|
| PRO-T4-01 | Create / Re-explode | components = BOM lines × (planned base ÷ BOM base) ÷ (1 − BOM `process_loss_percent` ÷ 100) × (1 + scrap%), fixed lines unscaled (process loss raises the inputs so the planned output survives it; `MRP-N-04` and `BOM-T1-14` apply the same factor — R29 F29), phantoms exploded with `phantom_path`; line effectivity filtered on `planned_start_date`; `required_date = planned_start + lead_time_offset_days`; outputs (sequence 1 = MAIN + BOM outputs scaled); operations copied with planned setup + run × qty; `supply_location_id` from line default → work centre line-side (stage) → site default | order service, one transaction (`WH-SC-609`: `CASING-01` 105, `BOLT-M8` 802) |
| PRO-T4-02 | Release (approved) with `component_reservation = SOFT`/`HARD` | one `whb_reservations` row per component line and location for min(required, allocatable), holder `(WAREHOUSE_MANUFACTURING, PRODUCTION_ORDER, orderId, componentLineNo)`; `NONE` creates none; `SOFT` carries `expires_at` = end of `planned_end_date` + `staging_stale_days` (site zone), re-dated when planned dates are edited (MD-23): a later date by `WhbReservationService.extend`, an **earlier** one by `release` + `create` in the same transaction, because `extend` moves later only (`WhbReservationService.java:212`; the re-created hold may be smaller — the shortage list shows it; R29 F18); a line with `supply_stock_status_code` set gets none (MD-30); reservations are made **only here, at release** — never at create (R29 F2); shortage is a computed field, not stored. These are the **only** reservations for the components: the order's MRQ reserves nothing and the store issue consumes them via `reservationsFor` (MD-16) | `WhbReservationService.create`, same transaction (`L-10`, `WH-SC-610`) |
| PRO-T4-03 | Release | `planned_cost` = Σ component required × current unit cost (`BOM-T4-05` method); missing cost → 0 and flagged in events | order service |
| PRO-T4-04 | Unrelease / Cancel | `releaseByHolder(WAREHOUSE_MANUFACTURING, PRODUCTION_ORDER, orderId)` with reason context `RESERVATION_RELEASE`; every MRQ of the order `WhMaterialRequisitionPort.cancel(CancelRequisitionCommand)` (envelope key `PRODUCTION_ORDER:<orderId>:MRQ_CANCEL:<mrqId>`, reason = the order's cancel reason) — a no-op success on a terminal MRQ with nothing issued (`MRQ-T1-21`) | reservation service, MRQ port, one transaction |
| PRO-T4-05 | Settlement posted (close) | remaining reservations released; open MRQ closed via `WhMaterialRequisitionPort.close` (open-to-issue → `closed_quantity`, `MRQ-T1-09`); component lines `CLOSED`; `closed_at`, `settlement_id` | settlement service → order service, one transaction |
| PRO-T4-06 | MSI / PRC postings | `issued_/returned_/staged_/unstaged_/consumed_quantity`, `received_/scrapped_/rejected_quantity`, `line_status` roll up (cited: `MSI-T4-*`, `PRC-T4-*`) | posting transaction |
| PRO-T4-07 | Demand line cancelled or reduced below Σ live orders (read through `WhDemandOrderPort` on demand-order event) | a `DEMAND_CANCELLED` event on the order (banner on WS-324) and an `whm_mrp_exceptions` row at the next run; **order unchanged** | demand-order event listener (`WH-SC-617`) |
| PRO-T4-08 | Create | `PRD-` number from `whb_number_series` (gapless, per operator company + site, yearly) logged in `whb_number_series_issued`; survives cancel; a site created after `V560001` has no series → `409 NUMBER_SERIES_NOT_CONFIGURED` naming series and site (the issuer throws, `WhbDocumentNumberIssuer.java:159-162`); the admin adds it on the base number-series screen (R29 F32) | `WhbDocumentNumberIssuer.resolveSiteSeries` |
| PRO-T4-09 | Every transition | `whm_production_order_events` row (append-only) + audit log `PRODUCTION_ORDER_<EVENT>`; `@CacheEvict statistics.whmProductionOrder` | order service |
| PRO-T4-10 | MRP convert | proposal `CONVERTED`, `converted_document_type = PRODUCTION_ORDER`, id, ref | `mfg-mrp` |

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
| 2026-10-22 | T1, T4, §9 | Consistency pass: `COMPLETED` not settled (MD-14), no cancel after posting (MD-15), single reservation owner (MD-16), selection on planned start (MD-19), `403` (MD-21), SOFT expiry (MD-23), rework supply status (MD-26), `MACHINE_DOWN` seeded | FRD-MFG §9 |

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
| PRO-OPEN-02 | `release_requires_approval` has no status and no `release_requested_*` columns — only `released_by/at` and `release_approved_by/at` | represent "pending" as `PLANNED` + `released_at` set + `release_approved_at` null (`PRO-T1-09`); or add `release_requested_by/at` | FR-635, §4 | OPEN |
| PRO-OPEN-03 *(resolved — MD-14; STORES `FR-533` amended)* | FR-640 / `MSI-GRD-07` refuse a store issue to an order not `RELEASED`/`IN_PROGRESS`, but FR-656 and `WH-SC-641` require a **late issue after the final receipt** on a `COMPLETED` order, and returns after final receipt | resolver admits `COMPLETED` for issues/returns (consumption policy still applies); `CLOSED` refused (`WH-SC-643`) | FR-640 vs FR-656 | resolved |
| PRO-OPEN-04 *(resolved — FRD §3.1 now seeds the four values)* | Reason context `PRODUCTION_HOLD` lists no values; `WH-SC-615` uses `MACHINE_DOWN` | seed `MACHINE_DOWN`, `MATERIAL_SHORTAGE`, `QUALITY_ISSUE`, `PLANNER_HOLD` in `V560001` | FRD §3.1 | resolved |
| PRO-OPEN-05 *(resolved — MD-23)* | `component_reservation = SOFT` but `whb_reservations` requires `expires_at` for `SOFT` (`V500033:416-417`); FRD sets no expiry | SOFT expiry = `planned_end_date` + `staging_stale_days` | evidence §5 | resolved |
| PRO-OPEN-06 *(resolved — R29 F28)* | Whether an operation confirmation (no movement) counts as the "first posting" that sets `IN_PROGRESS` | **no** — movements only; a confirmation stamps `actual_start_at` only (`QRW-T1-01`) | FR-634, FR-651 | resolved |
