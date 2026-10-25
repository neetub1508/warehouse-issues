# Functional Contract — Operation confirmations, in-process & final QC, rework (`warehouse-manufacturing`)

> **What this is.** The functional truth for shop-floor operation confirmations (WS-328), the two QC
> sources MFG registers with the core polymorphic inspection (`p8-06`) — `IN_PROCESS` (non-stock-bearing,
> SEAM-M4) and `PRODUCTION_RECEIPT` (final QC of `QC_HOLD` output) — the MFG-owned `REWORK` disposition,
> the rework order its `onDisposition` creates, and the `block_receipt_on_open_inprocess_qc` gate.
>
> **What this is not.** It does not restate the inspection lifecycle, sampling or the core dispositions:
> those are [`receipt-qc-putaway.contract.md`](receipt-qc-putaway.contract.md) (`RQP-*`) and
> [`incoming-inspection-sampling.contract.md`](incoming-inspection-sampling.contract.md) (`IIS-*`). It does
> not restate ledger guards: every posting cites [`movement-post-reverse.contract.md`](movement-post-reverse.contract.md)
> (`MPR-*`). The order ladder is `mfg-production-order.contract.md`; the receipt post is
> `mfg-production-receipt.contract.md` (both cited by name; not yet written).
>
> **Status.** Derived 2026-10-22 (v0), **not ratified**. No code exists. Authority: `docs/frd/FRD-MFG.md`.

---

## 0. Identity

| | |
|---|---|
| **Workflow** | Record / cancel an operation confirmation → (QC checkpoint) in-process inspection, outcome recorded, nothing moves → production receipt into `QC_HOLD` → final inspection → release / reject / scrap / **rework** → rework order `PLANNED` |
| **Module** | `warehouse-manufacturing` (`ai.warehousemanufacturing`, `whm_`, band V560000–V569999). Implements core `QualityInspectionSourceResolver` for `PRODUCTION_RECEIPT` and `IN_PROCESS` (`p8-06`, seeded by core `V501231`, not re-seeded — FR-621). **No mobile** (R-13) |
| **Domain baseline** | FRD-MFG FR-651, FR-652, FR-653, FR-634, FR-644, FR-649, §3.1 (`REWORK` disposition), §3.2 SEAM-M4, §8 settings · `DECISIONS.md` `L-1`, `L-3`, `L-6`, `L-10`, `L-12` · `RQP-T1-16`…`-23`, `RQP-T1-36` · `IIS-GRD-07`, `IIS-GRD-07a`, `IIS-T1-07`, `IIS-T4-05` |
| **Owning task bodies** | `p10-08` (FRD §13; task body not yet written). Depends on `p10-05` (order), `p10-07` (receipt), `p8-06` (polymorphic QC + SEAM-M4), `p10-02` (`REWORK` disposition, `OPC-` series) |
| **Primary tables** | `whm_operation_confirmations` (`V560060`); reads/writes `whm_production_order_operations` rollups; creates `whm_production_orders` (+ `_components`, `_outputs`, `_events`) for rework; core `wh_quality_inspections` (+ lines, results) are core's |
| **Status columns** | `whm_operation_confirmations.status` (`RECORDED`/`CANCELLED`) and `whm_production_order_operations.status` (`OPEN`/`STARTED`/`CONFIRMED`) — **no DB `CHECK`** (`D-10`); the service enforces |
| **Permission resources** | `whm_operation_confirmations:{view,create,export,cancel}` · core `wh_quality_inspections:{view,create,edit,disposition,approve,export}` · `whm_production_orders:view` (Quality tab). Every verb depends on `:view` |
| **Routes** | `/warehouse/manufacturing/operation-confirmations` (WS-328) · `/warehouse/manufacturing/production-orders/[id]` Operations + Quality tabs (WS-324) · core `/warehouse/inbound/quality-inspections` (WS-080) with source types `PRODUCTION_RECEIPT`/`IN_PROCESS` · **mobile: none** |
| **Requirement source** | `docs/frd/FRD-MFG.md` as of 2026-10-22 |
| **Contract status** | `derived 2026-10-22 (v0), not ratified` |
| **Contract version** | `v0 — 2026-10-22` |

### Acceptance checks

| # | The requester expects… | Delivered by |
|---|---|---|
| A1 | A confirmation records good/scrap/rework quantity, minutes, operator, start/finish and final flag, posts **no movement**, and is cancelled, never edited (`WH-SC-637`) | `QRW-T1-01`, `QRW-T1-02`, `QRW-UNR-01`, `QRW-UNR-02` |
| A2 | A milestone confirmation confirms the earlier open operations; confirmed scrap pre-fills the next receipt's scrap | `QRW-T1-01`, `QRW-T4-02`, `QRW-T4-03` |
| A3 | A confirmation at a QC-checkpoint operation is inspectable as a **non-stock-bearing** source; accept / reject / rework are recorded and nothing moves; a reject pre-fills the next receipt's rejected quantity (`WH-SC-637`) | `QRW-T1-04`, `QRW-T1-05`, `QRW-GRD-07`, `QRW-T4-04` |
| A4 | With `block_receipt_on_open_inprocess_qc = true` a receipt of the order cannot post while an in-process inspection of the order is open | `QRW-GRD-09`, `QRW-T4-05` |
| A5 | Final QC inspects the receipt's `QC_HOLD` output: release → `AVAILABLE` + putaway, reject → `REJECTED`, scrap → pending approval — all by core (`WH-SC-625`, `WH-SC-636`) | `QRW-T1-06`, `QRW-T1-07`, `QRW-T1-08` |
| A6 | `REWORK` moves the stock to `REJECTED` and, in the same transaction, creates a `PLANNED` rework order whose first component is the rejected item/lot and whose output is the same item, lot kept per `rework_keeps_lot` (`WH-SC-636`, `WH-SC-638`) | `QRW-T1-09`, `QRW-T4-06`…`-08` |
| A7 | A receipt whose output is under an open final inspection cannot be reversed | `QRW-T4-09` (cites FR-649) |
| A8 | The rework order's cost is the carried value of the reworked units plus extras (`WH-SC-638`) | `QRW-T4-08`; arithmetic in `mfg-costing-close.contract.md` `CST-T4-01` |

---

## 1. T1 — State machine

### 1.1 Status inventory

| Entity | Status | Represented by | Reachable via | Exits via | Kind |
|---|---|---|---|---|---|
| Confirmation | `RECORDED` | `whm_operation_confirmations.status` | `QRW-T1-01` | `QRW-T1-02` | initial, active |
| Confirmation | `CANCELLED` | `status`; `cancel` event on the order history | `QRW-T1-02` | none | **terminal** |
| Order operation | `OPEN` | `whm_production_order_operations.status` | order create (snapshot, FR-633) | `QRW-T1-01` | initial |
| Order operation | `STARTED` | `status` — at least one `RECORDED` confirmation, none final | `QRW-T1-01`, `QRW-T1-02` (regress) | `QRW-T1-01` (final), `-02` | active (derived on write) |
| Order operation | `CONFIRMED` | `status` — a `RECORDED` final confirmation of it or of a later milestone | `QRW-T1-01` | `QRW-T1-02` (regress) | active (derived on write) |
| In-process inspection | *in progress* / *completed* (derived) | core `started_at`/`completed_at` (`RQP` §1.1); source `IN_PROCESS`, `stock_bearing = false` | `QRW-T1-04` | `QRW-T1-05` | core |
| Final-QC stock | `QC_HOLD` → `AVAILABLE` · `REJECTED` · scrap *pending* | stock status of the receipt output position | receipt post (FR-644) | `QRW-T1-06`…`-09` | ledger state |
| Rework order | `PLANNED` (then the ordinary order ladder) | `whm_production_orders.status`, `order_type = REWORK`, `demand_source_type = QC_REWORK` | `QRW-T1-09` (effect) | `mfg-production-order` ladder | initial |

Not statuses: `inspection_required` on the confirmation is a fact set at record time; the in-process
outcome (`ACCEPT`/`REJECT`/`REWORK`, `INSPECTION_OUTCOME`) is a verdict on the core inspection line.

### 1.2 Transitions

| ID | From | Event / action | To | Guard (service, first) | Actor (permission) | Side effects | Comment/reason required | UI entry point | Source |
|---|---|---|---|---|---|---|---|---|---|
| QRW-T1-01 | — | **Record confirmation** for one order operation: good / scrap / rework quantity, setup + run minutes, operator, `started_at`, `finished_at`, `is_final` | `RECORDED` | `QRW-GRD-01`…`-06` | `whm_operation_confirmations:create` | `OPC-` number (gapless, site, yearly); operation rollups `confirmed_good/scrap/rework_quantity`, `actual_minutes` += ; operation `STARTED`, or `CONFIRMED` when `is_final`; when the operation `is_milestone`, every earlier `OPEN`/`STARTED` operation becomes `CONFIRMED` with its good quantity raised to the milestone's where lower (`QRW-T4-02`); `inspection_required = operation.is_qc_checkpoint`; order `actual_start_at` stamped when null; **no movement, no order status change** (`QRW-OPEN-03`) | scrap reason when scrap > 0 | WS-328 toolbar **Add**; WS-324 Operations tab **Confirm** | FR-651 |
| QRW-T1-02 | `RECORDED` | **Cancel confirmation** | `CANCELLED` | `QRW-GRD-07`, `QRW-GRD-08`, `QRW-GRD-15` | `whm_operation_confirmations:cancel` — not `:create` (`RJ-005`) | rollups recomputed from the remaining `RECORDED` rows (incl. milestone-implied confirmations); operation status re-derived; next-receipt pre-fill recomputed; history event | **yes** — an `OPERATION_CONFIRMATION_CANCEL` reason (seeded in `V560001` beside `MRP_DISMISS`, R31 `QRW-OPEN-04`) + note | WS-328 row **Cancel** | FR-651 |
| QRW-T1-03 | `RECORDED` | Edit a confirmation | refused | — | any | none — correction is cancel + re-record | — | none (`QRW-UNR-01`) | FR-651 |
| QRW-T1-04 | — | **Start in-process inspection** (`IIS-T1-07`, `source_type = IN_PROCESS`, source = the confirmation) | *in progress* | `IIS-GRD-07`, `QRW-GRD-10` | `wh_quality_inspections:create` | core header + one line (`item_id` = order item, proposed quantity = `good_quantity`, `stock_bearing = false`, no location/status) | no | WS-080 **Start** (source picker lists confirmations with `inspection_required` and no completed inspection); WS-324 Quality tab **Inspect** | FR-652 |
| QRW-T1-05 | *in progress* | **Complete** with outcomes per line `ACCEPT` / `REJECT` / `REWORK` (quantities sum to the inspected quantity) | *completed* | `RQP-GRD-15`, `RQP-GRD-17`, `IIS-GRD-07a` | `wh_quality_inspections:edit` | core records outcomes; MFG `onDisposition` (`QRW-T4-04`): **nothing moves**; `REJECT` qty adds to the order's next-receipt rejected pre-fill; `REWORK` qty adds to the operation's `confirmed_rework_quantity`; **no rework order** (no stock exists, `QRW-OPEN-05`) | no | WS-080 **Complete** | FR-652 |
| QRW-T1-06 | `QC_HOLD` output of a `POSTED` receipt, final inspection *completed* | **Disposition → release** (`RESTOCK_SELLABLE`) | `AVAILABLE` | `RQP-GRD-18`, `RQP-GRD-29`, `QRW-GRD-11` | `wh_quality_inspections:disposition` | `RQP-T1-20` (`STATUS_CHANGE` via `MPR-T1-10`, putaway task); MFG `onDisposition`: MTO output reservation for the demand line when `reserve_output_for_demand` (`QRW-T4-10`) | **yes** | WS-080 **Disposition** | FR-652 |
| QRW-T1-07 | as `-06` | **Disposition → reject** (`REJECT`) / `RTV` refused | `REJECTED` | as `-06`; `RTV` → `QRW-GRD-12` | `wh_quality_inspections:disposition` | `RQP-T1-21`; MFG `onDisposition`: order `rejected_quantity` += (`QRW-T4-11`) | **yes** | WS-080 **Disposition** | FR-652 |
| QRW-T1-08 | as `-06` | **Disposition → scrap** (`SCRAP`) → approve / reject / withdraw | *pending* → scrapped | as `-06` | `:disposition`; approve `wh_quality_inspections:approve` | `RQP-T1-22`, `-23`, `-36` (`MPR-T1-04`…`-07`, `MPR-GRD-27`); MFG `onDisposition` on approval: order `scrapped_quantity` +=; **the order's cost pool is not touched** — the units leave at carried cost | **yes** | WS-080 **Disposition**, **Approve scrap** | FR-652 |
| QRW-T1-09 | as `-06` | **Disposition → `REWORK`** (MFG-registered; target status `REJECTED`) | `REJECTED` + rework order `PLANNED` | `RQP-GRD-18`, `RQP-GRD-29`, `QRW-GRD-11`, `QRW-GRD-13`, `QRW-GRD-14` | `wh_quality_inspections:disposition` (the rework order is a system effect; **no** `whm_production_orders:create` needed, `QRW-OPEN-06`) | `STATUS_CHANGE` `QC_HOLD → REJECTED` via `MPR-T1-10`; **same transaction**: `onDisposition` creates the rework order (`QRW-T4-06`, `-07`); no putaway task (`RJ-017`) | **yes** | WS-080 **Disposition** | FR-653 |
| QRW-T1-10 | `REJECTED` stock of an MFG receipt | Rework order released, issued/backflushed, received | ordinary order ladder | `mfg-production-order` / `mfg-production-receipt` | as there | the rework receipt's output may go to `QC_HOLD` again and be inspected again (rework of rework allowed) | — | WS-323 / WS-326 | FR-653 |

### 1.3 Guards — the predicate, the refusal, and where it lands

House envelope `{ "error", "details": { "errors": { "<field>": "<msg>" } } }`. `422` invalid input, `409`
state conflict. MFG tables carry no trigger for these guards; the service is the only enforcement.

| ID | Predicate (must hold to proceed) | Refusal: HTTP · code · field | Message shape | DB backstop | Source |
|---|---|---|---|---|---|
| QRW-GRD-01 | Order `RELEASED` or `IN_PROGRESS`, `is_on_hold = false`, on the caller's allowed sites | `409 ORDER_NOT_OPEN` · `orderId`; `409 ORDER_ON_HOLD` · `orderId` | names order, status / hold reason | — | FR-634, FR-651 |
| QRW-GRD-02 | The operation belongs to the order and is not `CONFIRMED` by a final confirmation | `422 OPERATION_NOT_ON_ORDER` · `operationId`; `409 OPERATION_ALREADY_CONFIRMED` · `operationId` | names operation seq and the final `OPC-` | FK `operation_id` | FR-651 |
| QRW-GRD-03 | good, scrap, rework ≥ 0 and good + scrap + rework > 0; minutes ≥ 0 | `422 CONFIRMATION_QUANTITY_INVALID` · `goodQuantity` | — | `CHECK (≥ 0)` | FR-651 |
| QRW-GRD-04 | scrap > 0 ⇒ `scrap_reason_code_id` of context `PRODUCTION_SCRAP` | `422 SCRAP_REASON_REQUIRED` · `scrapReasonCodeId` | — | FK to reason code | FR-646, FR-651 |
| QRW-GRD-05 | `finished_at` ≥ `started_at`; both ≤ server now (site TZ display) | `422 CONFIRMATION_TIME_INVALID` · `finishedAt` | — | — | FR-651, `L-13` spirit |
| QRW-GRD-06 | `operator_user_id` is an active user of the company (display via the platform user helper) | `422 OPERATOR_INVALID` · `operatorUserId` | — | FK users | FR-651 |
| QRW-GRD-07 | No core inspection (in progress **or** completed) has this confirmation as source | `409 CONFIRMATION_INSPECTED` · `id` | names the inspection number | — | FR-651, FR-652 |
| QRW-GRD-08 | Order not `CLOSED`/`CANCELLED` | `409 ORDER_NOT_OPEN` · `orderId` | — | — | FR-634 |
| QRW-GRD-09 | **Receipt post gate** (`block_receipt_on_open_inprocess_qc = true` only): no `RECORDED` confirmation of the order with `inspection_required = true` lacks a *completed* in-process inspection (not-yet-started counts as open, `QRW-OPEN-02`). Evaluated by the receipt post (DRAFT→POSTED and PENDING_APPROVAL→POSTED) | `409 INPROCESS_INSPECTION_OPEN` · `orderId` | lists `OPC-` numbers and inspection numbers | — | FR-652, §8 |
| QRW-GRD-10 | `IN_PROCESS` resolver: confirmation `RECORDED`, `inspection_required = true`, order not `CANCELLED`/`CLOSED`, no other inspection of it *in progress* | `422 QC_SOURCE_NOT_INSPECTABLE` · `sourceId`; `409 INSPECTION_IN_PROGRESS` · `sourceId` | — | — | FR-652, `IIS-GRD-08` |
| QRW-GRD-11 | `PRODUCTION_RECEIPT` resolver: receipt `POSTED` (not `REVERSED`), output line in `QC_HOLD` with held quantity > dispositioned; no `REQUESTED`/`APPROVED` reversal of the receipt | `422 QC_SOURCE_NOT_INSPECTABLE` · `sourceId`; `409 RECEIPT_REVERSAL_PENDING` · `sourceId` | names the `PRV-` | — | FR-649, FR-652 |
| QRW-GRD-12 | `RTV` is not offered for a `PRODUCTION_RECEIPT` source (no supplier) | `422 DISPOSITION_NOT_SUPPORTED_FOR_SOURCE` · `lines[n].dispositionCode` | — | — | FR-652 |
| QRW-GRD-13 | `REWORK` only for a source whose resolver implements rework (`PRODUCTION_RECEIPT`); refused for `GOODS_RECEIPT`, store return, stock and `IN_PROCESS` (the latter uses outcome `REWORK`, `QRW-T1-05`) | `422 DISPOSITION_NOT_SUPPORTED_FOR_SOURCE` · `lines[n].dispositionCode` | names the source type | — | FR-653, SEAM-M4 |
| QRW-GRD-15 | Cancel reason present, active, of context `OPERATION_CONFIRMATION_CANCEL` (R31 `QRW-OPEN-04`) | `422 REASON_REQUIRED` · `reasonCodeId` | — | FK to reason code | FR-651 |
| QRW-GRD-14 | Rework order creatable: output item active; owner house (`L-14`; non-own is `OD-42` v1.2); a rework BOM, when one resolves, is `APPROVED` and effective today; idempotency key `QRW:<inspectionLineId>:<dispositionSeq>` not yet used | `422 REWORK_ORDER_NOT_CREATABLE` · `lines[n]` (whole disposition refused) | names the failing condition | partial uk on `(rework_of_inspection_id, demand_source_line_id)` | FR-653 |

### 1.4 Transitions that must be unreachable

| ID | Forbidden | What makes it unreachable | Source |
|---|---|---|---|
| QRW-UNR-01 | Editing a confirmation | no edit endpoint or modal; cancel + re-record only | FR-651 |
| QRW-UNR-02 | A confirmation posting a movement or changing stock | the confirmation service holds no `WhbStockLedgerWriter` dependency (proved by grep) | FR-651 |
| QRW-UNR-03 | An in-process inspection moving stock or offering a disposition | `IIS-GRD-07a` (`409 INSPECTION_SOURCE_NOT_STOCK_BEARING`) | FR-652, SEAM-M4 |
| QRW-UNR-04 | `REWORK` creating a second rework order on replay | idempotency key in `QRW-GRD-14` | FR-653 |
| QRW-UNR-05 | A `CANCELLED` confirmation returning to `RECORDED` | terminal | FR-651 |
| QRW-UNR-06 | The rework order cancelling or reverting the disposition | the disposition is a posted `STATUS_CHANGE`; cancelling the rework order leaves the stock `REJECTED` (a further disposition is a stock-source inspection, core) | FR-653, `L-3` |

---

## 2. T2 — Action × role × state

Every query and action is limited to the caller's allowed warehouses; AUDITOR reads, never exports.

| ID | Action | Permission | Allowed from | Extra condition | Source |
|---|---|---|---|---|---|
| QRW-T2-01 | Record confirmation | `whm_operation_confirmations:create` | order `RELEASED`/`IN_PROGRESS`, not on hold; operation not final-confirmed | supervisor persona | FR-651 |
| QRW-T2-02 | Cancel confirmation | `whm_operation_confirmations:cancel` | `RECORDED`, not inspected | note required | FR-651 |
| QRW-T2-03 | View / export confirmations | `:view` / `:export` | any | export excludes AUDITOR | FR-651 |
| QRW-T2-04 | Start in-process inspection | `wh_quality_inspections:create` | confirmation `RECORDED`, `inspection_required` | QC inspector | FR-652 |
| QRW-T2-05 | Record results / complete | `wh_quality_inspections:edit` | *in progress* | outcomes only, no disposition | FR-652 |
| QRW-T2-06 | Start final inspection | `wh_quality_inspections:create` | receipt `POSTED`, `QC_HOLD` output held | `QRW-GRD-11` | FR-652 |
| QRW-T2-07 | Disposition release / reject / scrap / rework | `wh_quality_inspections:disposition` | final inspection *completed* | `RTV` hidden for this source | FR-652, FR-653 |
| QRW-T2-08 | Approve / reject QC scrap | `wh_quality_inspections:approve` | scrap *pending* | approver ≠ dispositioner (`MPR-GRD-27`) | FR-652 |
| QRW-T2-09 | Open the rework order | `whm_production_orders:view` | rework order exists | link on WS-080 line and WS-324 Quality tab | FR-653 |

---

## 3. T3 — Time-driven rules & notifications

| ID | Rule | Trigger | What it changes | Who is notified | Channel | Job class | Notify-once? | Source |
|---|---|---|---|---|---|---|---|---|
| QRW-T3-01 | Inspection awaited at a QC checkpoint | `QRW-T1-01` with `inspection_required` | nothing | users holding `wh_quality_inspections:create` at the site | in-app — `TBD` DEFERRED-TO-p10-08 | event, no job | once per confirmation | FR-652 |
| QRW-T3-02 | Rework order created | `QRW-T1-09` | nothing | users holding `whm_production_orders:release` at the site | in-app — `TBD` DEFERRED-TO-p10-08 | event | once | FR-653 |
| QRW-T3-03 | Pending QC scrap escalation | `RQP-T3-03` (cited) | nothing | as `RQP-T3-03` | as there | `p2-23` job | as there | FR-652 |
| QRW-T3-04 | None auto-completes an inspection, auto-dispositions or auto-releases a rework order | — | — | — | — | — | — | FR-652 |

---

## 4. T4 — Cross-entity effects

| ID | When this happens | Then this other record must change | Enforced in | Source |
|---|---|---|---|---|
| QRW-T4-01 | Confirmation recorded / cancelled | `whm_production_order_operations` rollups and `status` re-derived from `RECORDED` rows, same transaction | `WhmOperationConfirmationService` | FR-651 |
| QRW-T4-02 | Milestone confirmation recorded | earlier non-final operations `CONFIRMED`, good raised to the milestone's; a cancel of the milestone regresses them | same | FR-651 |
| QRW-T4-03 | Confirmed scrap at the order's operations since the last posted receipt | the next receipt DRAFT pre-fills main-output `SCRAPPED` quantity with that scrap and its reason (editable, FR-651) | receipt create (`mfg-production-receipt`) | FR-651 |
| QRW-T4-04 | In-process inspection completed | `REJECT` qty → next-receipt `REJECTED` pre-fill; `REWORK` qty → operation `confirmed_rework_quantity`; history event on the order | `IN_PROCESS` resolver `onDisposition` | FR-652 |
| QRW-T4-05 | Receipt post with the setting on | `QRW-GRD-09` evaluated before `MPR-T1-01` | receipt post service | FR-652 |
| QRW-T4-06 | `REWORK` disposition | rework order created: `order_type = REWORK`, item = output item, `planned_quantity` = dispositioned base qty (base UoM), `owner_id` = stock owner, `demand_source_type = QC_REWORK`, `demand_source_id` = inspection, `demand_source_line_id` = inspection line, `rework_of_inspection_id`, `parent_order_id` = the inspected receipt's order, `priority` 3, `planned_start_date` = disposition date (site TZ), `planned_end_date` = start + `manufacturing_lead_time_days` (0 when none), `receipt_location_id` = the rejected stock's location, `planned_lot_code` = the rejected lot when `rework_keeps_lot` else null, `PRD-` number at create, event `CREATED_FROM_QC` | `PRODUCTION_RECEIPT` resolver `onDisposition` | FR-653 |
| QRW-T4-07 | same | component line 1 = rejected item/lot, qty = dispositioned qty, `supply_method = BACKFLUSH`, `supply_location_id` = the rejected location, `supply_stock_status_code = REJECTED` (MD-26) and **no reservation** — `WhbReservationService.create` refuses a non-allocatable status (ATP 0, `WhbStockPositionWriter.java:356-366`) and only a `VENDOR_RETURN` demand may name one (`WhbAllocationService.java:205-230`); the allocator never offers `REJECTED` stock, so nothing is lost (MD-30, R29 F2); extras from a rework BOM — `is_rework_alternative = true` (MD-26) or added ad hoc in `PLANNED` (FR-653); output 1 = MAIN, same item | same | FR-653 |
| QRW-T4-08 | Rework order receipts | pool = carried value of the backflushed rejected lot + extras. When the output grain (same item, owner, site, duty) nets to zero against the rejected input, the costing engine posts the output at the grain's current average whatever is stated (`WhbCostingEngine.java:278-289`): the receipt states that figure and absorbs only it, the extras' value stays in the pool, and the **close settlement** capitalises it onto the output lot still on hand (or `COST_OF_SALES`) through the landed-cost path (`CST-T4-06`; MD-33, R29 F7). A grain that does not net to zero (scrap, partial rework) is absorbed by `CST-T4-01` as usual; same lot code when `rework_keeps_lot` (`WH-SC-638`) | `mfg-production-receipt` (receipt), `mfg-costing-close` (settlement) | FR-653, FR-654 |
| QRW-T4-09 | Receipt reversal requested while an output line has a final inspection *in progress* or a pending QC scrap | refused (FR-649) `409 RECEIPT_INSPECTION_OPEN` / `RECEIPT_SCRAP_PENDING` (`RQP-GRD-30` vocabulary) | `mfg-production-receipt` | FR-649 |
| QRW-T4-10 | Release of `QC_HOLD` output of an MTO order with `reserve_output_for_demand` | the demand-line reservation is created for the **released** quantity at release, not at receipt (QC_HOLD is not allocatable, `L-6`; `QRW-OPEN-08`) | resolver `onDisposition` | FR-637 |
| QRW-T4-11 | Final-QC reject / rework / approved scrap | order `rejected_quantity` / `scrapped_quantity` rollups +=; `received_quantity` unchanged; over-receipt tolerance is **not** freed (`QRW-OPEN-09`) | resolver `onDisposition` | FR-647, FR-652 |
| QRW-T4-12 | Rework order cancelled | stock stays `REJECTED`; inspection line keeps the link; MRP stops counting it as supply | `mfg-production-order` | FR-653 |

---

## 5. T5 — Screen contract (web only)

### 5.1 `/warehouse/manufacturing/operation-confirmations` — WS-328 Operation Confirmations

| | |
|---|---|
| **Type** | list + Add/View modals (reference: **Customer**) |
| **Grid identifier** | `whm_operation_confirmations` · filter scope `WAREHOUSE_MFG_OPERATION_CONFIRMATION` |
| **Default sort** | `e.finished_at DESC` |
| **Statistics tiles** | `RECORDED` · `CANCELLED` · awaiting inspection · scrap quantity (period) — filter-aware |
| **Columns** | `confirmationNumber`, `orderNumber` (GridLink → WS-324), `itemName`, `operationSeq`, `workCentreName`, `goodQuantity`, `scrapQuantity`, `reworkQuantity`, `scrapReasonName`, `setupMinutes`, `runMinutes`, `operatorName` (platform user-display helper), `startedAt`, `finishedAt` (timestamps: `formatDateWithTimezoneSync`), `isFinal`, `inspectionRequired`, `inspectionStatus` (derived: none / awaited / in progress / completed), `status`, `createdByName`, `updatedByName` |
| **Filters** | `warehouseId` → `workCentreId` → `orderId` (typeahead) → `operationId`; `status` (enum); `isFinal` (boolean); `inspectionRequired` (boolean); `operatorUserId` (user typeahead); `finishedFrom`/`finishedTo` (`date`, timestamp range). All in `COMMON_FILTER_CONFIGS.WAREHOUSE_MFG_OPERATION_CONFIRMATION` |
| **Row actions** | View → `QRW-T2-03` · Cancel → `QRW-T2-02` (warning variant, `RECORDED` and not inspected) · Inspect → WS-080 (when awaited, `QRW-T2-04`) |
| **Toolbar** | **Add** (Record confirmation modal `size="lg"`, `minWidth={500}`, resizable; order → operation cascade; `DatePicker mode="datetime"` for start/finish, `maxDate = now`) → `QRW-T2-01` · Export |
| **Export columns** | every grid column + `createdByName`, `updatedByName` |
| **Print** | none |
| **Mobile counterpart** | none (R-13) |

### 5.2 WS-324 Production Order detail — Operations and Quality tabs (MFG part)

| Tab | Shows | Actions |
|---|---|---|
| Operations | per operation: seq, work centre, planned vs confirmed good/scrap/rework, minutes planned vs actual, QC checkpoint, status | **Confirm** (`QRW-T2-01`) |
| Quality | in-process and final inspections of the order (number, source, status, outcomes/dispositions), rework orders created (GridLink) | **Inspect** → WS-080 |

### 5.3 Core WS-080 Quality Inspections (MFG-relevant behaviour only)

Source picker gains `PRODUCTION_RECEIPT` (lists `QC_HOLD` receipt output lines) and `IN_PROCESS`
(lists awaited confirmations). For `IN_PROCESS` the Disposition action is hidden and the line shows an
outcome select (`ACCEPT`/`REJECT`/`REWORK`). For `PRODUCTION_RECEIPT` the disposition select offers
`RESTOCK_SELLABLE`, `REJECT`, `SCRAP`, `REWORK`; `RTV` is hidden. A dispositioned `REWORK` line shows the
rework order number as a GridLink.

---

## 6. Out of scope (explicit decisions)

| Not built | Where it lives / why |
|---|---|
| Mobile shop-floor confirmation | R-13 (no warehouse mobile) |
| Labour T&A, OEE, machine/IoT capture | R-02; an integration principal may post confirmations through the API |
| Use-with-deviation disposition, CoA, eBMR | R-10; not in FRD-MFG |
| Sampling plans, AQL bands | core `IIS-*` |
| Auto-start of an inspection on a confirmation or receipt | none — the inspector starts it (`QRW-T3-04`) |
| Rework of non-MFG stock (GRN, store return) | `QRW-GRD-13`; supplier stock goes `REJECT`/`RTV` |
| Ledger post / reverse mechanics | `movement-post-reverse.contract.md`, cited by `MPR-*` |

## 7. Amendments

| Date | Row IDs affected | Change | Found by |
|---|---|---|---|
| 2026-10-22 | all | v0 derived from `docs/frd/FRD-MFG.md`; not ratified | contract derivation (design set) |
| 2026-10-22 | `QRW-T4-07`, `-08`, `QRW-OPEN-01`, `-02`, `-03`, `-08` | R29: rework component unreserved (F2, MD-30); same-item extras via settlement (F7, MD-33); MTO reservation at release (F15); one in-process gate (F27); confirmation never sets `IN_PROGRESS` (F28); P8 seed renumbered (`V501231`) | `R29-functional-review-mfg.md` |
| 2026-10-23 | `QRW-T1-02`, `QRW-GRD-15`, Source column, `QRW-OPEN-04`…`-06`, `-09` | R31: cancel reason context (`QRW-OPEN-04` DECIDE); Source FR on every rule row (F-MF-018); DECIDE rows applied | `R31-functional-review-mfg.md`, `R31-decisions.md` |
| 2026-10-22 | §9 | Consistency pass: no `SCRAP` stock status (MD-25), `supply_stock_status_code` and `is_rework_alternative` (MD-26) | FRD-MFG §9 |
| 2026-10-25 | R32 (`D-20` item 11): §12 — PQC per routing stage with first-piece / patrol / full sampling, next-stage hold by default, pass under deviation, in-order rework loop with a cycle limit, producer segregation and NCR feed through the core fold (FR-808…FR-810) |

## 8. Invariants and scenarios this workflow must not break

| Invariant | Rows that carry it | Scenarios that prove it |
|---|---|---|
| Confirmations post nothing | `QRW-UNR-02`, `QRW-T1-01` | `WH-SC-637` |
| Non-stock-bearing source moves nothing (SEAM-M4) | `QRW-T1-05`, `QRW-UNR-03` | `WH-SC-637` |
| `L-1` / `L-3` — dispositions are balanced status changes; corrections are reversals | `QRW-T1-06`…`-09` (`MPR-T1-10`) | `WH-SC-636` |
| `L-6` — QC-held stock is not allocatable | `QRW-T4-10` | `WH-SC-625`, `WH-SC-636` |
| Rework order created atomically with the disposition, once | `QRW-T1-09`, `QRW-GRD-14`, `QRW-UNR-04` | `WH-SC-636`, `WH-SC-638` |
| `L-12` — rework output keeps traceability to the reworked lot | `QRW-T4-07`, `QRW-T4-08` | `WH-SC-638` |

## 9. Open rows — contradictions and holes

| ID | Contradiction / hole | Recommendation | Authority | Status |
|---|---|---|---|---|
| QRW-OPEN-01 *(resolved — MD-26: `supply_stock_status_code` adopted)* | FR-653 says the rework order's first component is supplied "from status `REJECTED`", but `whm_production_order_components` has no supply-status column and core store issue issues allocatable stock | add `supply_stock_status_code` to `_components` (default null = allocatable); rework line 1 = `REJECTED`, `BACKFLUSH` from that position; **no reservation** (R29 F2 replaced the HARD-hold clause — MD-30) | FRD §4 owns schema | resolved |
| QRW-OPEN-02 *(resolved — R29 F27)* | FR-652 "release of a downstream receipt is refused while an in-process inspection … is open": "release" vs post, and whether an awaited-but-unstarted inspection is "open" | read as **receipt post**; awaited counts as open; `PRC-GRD-14` now uses `QRW-GRD-09`'s predicate and `409 INPROCESS_INSPECTION_OPEN` | FR-652, §8 | resolved |
| QRW-OPEN-03 *(resolved — R29 F28, `PRO-OPEN-06`)* | FR-634 sets `IN_PROGRESS` "by the first posting of any kind"; a confirmation posts nothing | a confirmation does not move the order to `IN_PROGRESS`; it stamps `actual_start_at` only (`p10-08` corrected) | FR-634, FR-651 | resolved |
| QRW-OPEN-04 *(resolved — R31-decisions DECIDE)* | No reason context for cancelling a confirmation (§3.1) | **adopted:** `OPERATION_CONFIRMATION_CANCEL` context in `V560001`, matching `MRP_DISMISS` in the same migration (FRD §3.1; `QRW-T1-02`, `QRW-GRD-15`) | §3.1 | resolved |
| QRW-OPEN-05 *(resolved — R31-decisions DECIDE: default stands)* | In-process outcome `REWORK`: FR-653's `onDisposition` creates a rework order, but nothing is stock in-process | no rework order for `IN_PROCESS`; rework quantity recorded on the operation only (`QRW-T1-05`) | SEAM-M4, FR-653 | resolved |
| QRW-OPEN-06 *(resolved — R31-decisions DECIDE: default stands)* | The rework order is created under the inspector's identity, who may lack `whm_production_orders:create` | system effect of `:disposition`; `created_by` = inspector, event actor = inspector (`QRW-T1-09`) | FR-653, `RJ-005` | resolved |
| QRW-OPEN-07 *(resolved — MD-26: `is_rework_alternative BOOLEAN NOT NULL DEFAULT false`)* | FR-653 "rework BOM (`usage = PRODUCTION`, alternative flagged rework)" — `whm_boms` has no rework flag column | add `is_rework_alternative BOOLEAN` to `whm_boms`, or a `WHM_BOM_USAGE` value `REWORK` | FRD §4 | resolved |
| QRW-OPEN-08 *(resolved — R29 F15)* | FR-637 reserves MTO output at each good receipt, but FR-644 receives into `QC_HOLD` when final inspection is required — QC-held stock is not allocatable (`L-6`) | reserve at release (`QRW-T4-10`); receipts into an allocatable status reserve at receipt (`PRC-T4-08`, FR-637 amended) | FR-637, FR-644, `L-6` | resolved |
| QRW-OPEN-09 *(resolved — R31-decisions DECIDE: default stands)* | Does a final-QC reject/rework free over-receipt tolerance (FR-647)? Not stated | no — tolerance counts receipt good quantity; replacement is the rework order or a new order (`QRW-T4-11`) | FR-647 | resolved |

## 12. R32 rules (PRD 2026-10-24, `D-20`)

Owning task: `issues/p10-08.md` `## R32 additions (PRD 2026-10-24)` (FR-808…FR-810). Job cards are `mfg-shop-floor`; PDI is `mfg-pdi-unit-registry`.

| ID | Rule | Refusal / effect | Source |
|---|---|---|---|
| QRW-T1-20 | A booking on a checkpoint operation with `pqc_blocks_next_stage` = `true` (default) opens an `IN_PROCESS` inspection on the booking and sets the job card `HELD_QC`; its output does not transfer until the inspection completes | job card `HELD_QC` | FR-809 |
| QRW-T1-21 | Inspection completes: `ACCEPT` → transfer; `REJECT` → booked rejected (reason), no transfer; `ACCEPT_UNDER_DEVIATION` → transfer only with a deviation consumed through `WhQualityDeviationPort` (`p8-18`, usage `PRODUCTION_CONSUMPTION`); with `false` the inspection is record-only (FR-652) | `409 DEVIATION_REQUIRED` | FR-809 |
| QRW-T1-22 | `REWORK` (PQC or PDI) on job-card units creates a rework job card on the same batch at the originating (or a named earlier) operation, `rework_cycle` + 1; its good output re-enters PQC / PDI at that stage | rework counts per batch and unit serial | FR-810 |
| QRW-GRD-20 | A unit / batch at `max_rework_cycles` takes no further rework | `409 REWORK_LIMIT_REACHED` | FR-810 |
| QRW-GRD-21 | PQC plan precedence: routing operation plan → operation master plan → item plan; sampling `FIRST_PIECE` (first unit of each batch before the rest transfer), `PATROL` (every `patrol_interval_units`), `FULL` (per-unit result rows by unit serial) | `422 PQC_PLAN_MISSING` when a checkpoint has none | FR-808 |
| QRW-GRD-22 | The `IN_PROCESS` resolver's `producedByUserIds` returns the booking's crew and poster; core refuses an inspector among them unless `inspector_may_be_producer` (`p8-19`); result approval follows `p8-19`'s mode | `403 INSPECTOR_IS_PRODUCER` (core) | FR-808 |
| QRW-T4-20 | A PQC reject attributed to a purchased component (reason flagged supplier-caused) raises a core NCR (`p8-17`) naming the component item, lot and supplier, so line rejections feed vendor rejection ppm (`p8-21`) | NCR id recorded on the inspection | FR-808 |
| QRW-UNR-20 | Final-QC `REWORK` of **received** stock creating a rework job card | it still creates a rework order (FR-653, `D-20` item 11) | FR-810 |
