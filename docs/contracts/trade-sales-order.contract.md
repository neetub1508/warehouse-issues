# Functional Contract — Sales order (FIXED / OPEN / BLANKET), customer delivery schedule, dispatch planning and releases, acknowledgement, commitment tracking, short-close

> **What this is.** The functional truth for the commercial sales order in `warehouse-trade`: its three
> types, the customer delivery schedule, dispatch planning from the FG store and the hand-off of each
> dispatch release to a core demand order through the `p8-02` port, the order acknowledgement, delivery
> commitment tracking and short-close. Picking, packing, shipping, the outward gate pass and the
> challan / e-way bill are core's and `warehouse-india`'s; this contract only **reads** them.
>
> **Purchase twin.** [trade-purchase-order](trade-purchase-order.contract.md), row for row. Both sides
> keep **one core execution document per trade order** and release by firming its schedule (FRD-TRADE §5 M18).
>
> **Status.** Derived 2026-10-22 (v0). No code exists yet. Port signatures are what trade requires from `p8-02`.

---

## 0. Identity

| | |
|---|---|
| **Workflow** | Draft (manual / from won quotation) → submit → approve → acknowledge to customer → dispatch planning → dispatch releases (FIXED schedule lines, OPEN customer call-offs, BLANKET schedule lines) → core demand order → pick / pack / ship (core) → complete / short-close → closed; cancel before release; customer schedule revisions; commitment tracking |
| **Module** | `warehouse-trade`; core `warehouse` through `WhDemandOrderPort` (`p8-02`, `ai.warehouse.port.demand`; [po-schedule-port](po-schedule-port.contract.md) `POS-T1-10`…`-12`) and read-only queries |
| **Domain baseline** | FRD-TRADE FR-605…FR-611, FR-543, FR-545, `TRD-01`, `TRD-03`, `OD-32`, `OD-39` · R28 §4 D1–D3 |
| **Owning task bodies** | `issues/p9-09.md` (types, schedule, dispatch planning, releases, port, cancel, schedule import) · `issues/p9-10.md` (acknowledgement, commitments, short-close, auto-close) |
| **Primary tables** | `wht_sales_orders`, `wht_sales_order_lines`, `wht_so_schedule_lines`, `wht_so_dispatch_releases`, `wht_so_dispatch_release_lines`, `wht_so_charges` (`V550080`); `wht_so_acknowledgements`, `wht_so_commitment_followups` (`V550090`) |
| **Permission resources** | `wht_sales_orders:view/create/edit/export/submit/approve/cancel/issue/short_close/amend` · `wht_so_dispatch_releases:view/create/cancel/export` · `wht_so_commitment_followups:view/create` |
| **Routes** | WS-303 `/warehouse/trade/sales/orders`, WS-304 `/[id]`, WS-305 `/dispatch-planning`, WS-306 `/commitments` · mobile: none |
| **Contract status / version** | `derived` · `v0 — 2026-10-22` |

**Fields** mirror `trade-purchase-order` §0 with: `so_number` (series `SO`, at submit; stored on the core
demand order as `sales_order_ref` and `source_document_ref`), `so_type`, customer, `customer_po_number`,
`customer_po_date`, `sales_exec_id`, `ship_to_address_id`, `dispatch_warehouse_id`, `quotation_id`,
`rate_contract_id`, `price_list_id`; lines add `customer_part_number`, `customer_item_ref_id`,
`floor_price_at_order`; schedule lines carry `committed_date` (our acknowledged date, defaults to the
requested `delivery_date`), `customer_revised_date`, `zone`, `released_quantity`, `release_status`;
dispatch release: `release_number` (`<so_number>-Dnn`), `release_date`, `planned_dispatch_date`,
`status`, `core_schedule_line_ids` (firmed on the SO's one core demand order); header `core_demand_order_id`; release line: `so_line_id`, `schedule_line_id` (null for OPEN call-off),
qty, `unit_price`.

### Acceptance checks

| # | Expects | Delivered by |
|---|---|---|
| A1 | Duplicate customer PO refused (`WH-SC-555`) | `TSO-GRD-02` |
| A2 | Acknowledgement printed with committed dates (`WH-SC-556`) | `TSO-T1-06` |
| A3 | Dispatch planning shows ATP; shortfall shown not blocked; over-release refused (`WH-SC-557`, `-558`) | `TSO-T1-09`, `TSO-GRD-06` |
| A4 | Shipments read from core; fulfilment derived (`WH-SC-559`) | `TSO-T4-04` |
| A5 | Customer schedule revision through amendment, firm-zone flagged (`WH-SC-560`) | `TSO-T1-12` |
| A6 | At-risk commitments with a revised date apart from committed (`WH-SC-561`) | `TSO-T3-02` |

## 1. T1 — State machine

### 1.1 Status inventory

Header ladder is **identical** to `TPO` §1.1 (`DRAFT`, `SUBMITTED`, `REJECTED`, `APPROVED`, `ISSUED` =
acknowledgement sent, `CLOSED`, `SHORT_CLOSED`, `CANCELLED`; derived fulfilment `NOT_STARTED` / `PARTIAL`
/ `COMPLETE` and validity `EXPIRED`). There is **no `ACKNOWLEDGED` from the customer**: our
acknowledgement *is* `ISSUED` (M22). Dispatch release: `DRAFT` → `RELEASED` → `CLOSED` (core demand
order shipped / closed); `CANCELLED`.

### 1.2 Transitions

| ID | From | Action | To | Guard | Actor | Side effects | Comment | UI |
|---|---|---|---|---|---|---|---|---|
| TSO-T1-01 | — | Create (manual / from won quotation / from sales RC) | `DRAFT` | — | `:create` | prices `TRC-T4-04` | no | WS-303 Add |
| TSO-T1-02 | `DRAFT`, `REJECTED` | Submit | `SUBMITTED` | `TSO-GRD-01`…`-05` | `:submit` | number; `TAM` doc `SO`, conditions `below_floor_price`, `discount_over_pct`, `manual_rate` | no | Submit |
| TSO-T1-03 | `SUBMITTED` | Withdraw | `DRAFT` | `TAM-T1-09` | maker | — | no | — |
| TSO-T1-04 | `SUBMITTED` | Approved | `APPROVED` | `TSO-GRD-10` | approver | `version_no = 1` snapshot; RC consumption for FIXED; **`WhDemandOrderPort.createDemand`** (`TSO-T4-01`) — FIXED schedule `FIRM`, BLANKET schedule `FORECAST`, OPEN none | — | WS-285 |
| TSO-T1-05 | non-terminal | Cancel | `CANCELLED` | `TSO-GRD-08` | `:cancel` | planned demand withdrawn; RC consumption reversed | **yes** | row action |
| TSO-T1-06 | `APPROVED` | Send acknowledgement | `ISSUED` | template exists | `:issue` | print `SALES_ORDER_ACK` with committed dates; `wht_so_acknowledgements` row | no | *Acknowledge* |
| TSO-T1-07 | `APPROVED`, `ISSUED` | Record OPEN call-off (customer's) | release `DRAFT` | `TSO-GRD-06`, `-07` | `wht_so_dispatch_releases:create` | — | customer call-off ref | WS-304 |
| TSO-T1-08 | release `DRAFT` | Release | `RELEASED` | `TSO-GRD-06`, `-07`, `-09` | same | **`WhDemandOrderPort.releaseSchedule`** (`TSO-T4-02`) in the same transaction; schedule `released_quantity` | no | WS-305 *Release* |
| TSO-T1-09 | due schedule lines | Plan dispatch (multi-select, whole / part) | one release per SO × planned dispatch date | as `-08` | same | ATP shown (`TSO-T4-03`) | no | WS-305 |
| TSO-T1-10 | release `RELEASED` | Cancel release | `CANCELLED` | core demand order not yet picked — asked via `WhDemandOrderPort.getFulfilmentPosition` | `wht_so_dispatch_releases:cancel` | `WhDemandOrderPort.amendDemand` returns the firmed lines to `FORECAST` (BLANKET) or `cancelLine` (OPEN call-off); schedule qty back to open | **yes** | WS-305 / detail |
| TSO-T1-11 | line / header non-terminal | Short-close | `SHORT_CLOSED` | `TSO-GRD-11` | `:short_close` | `TAM` `SO_SHORT_CLOSE`; unreleased schedule cancelled; open demand cancelled through the port; planned demand withdrawn | **yes** | row action |
| TSO-T1-12 | BLANKET non-terminal | Import / enter revised customer schedule | SO amendment `DRAFT` (`TOA-T1-01`) | `TSO-GRD-12` | `:amend` | firm-zone changes flagged (`schedule_change_in_firm_zone = true`, counted for `TCE`) | no | WS-304 *Revise schedule* (CSV dry-run → apply) |
| TSO-T1-13 | any active | Log commitment follow-up | follow-up row; `customer_revised_date` | — | `wht_so_commitment_followups:create` | — | no | WS-306 |

### 1.3 Guards

| ID | Predicate | Refusal |
|---|---|---|
| TSO-GRD-01 | Customer profile exists, not sales-blocked; dispatch site in user scope and allows dispatch | `422 TRADE_CUSTOMER_BLOCKED` |
| TSO-GRD-02 | `customer_po_required` ⇒ customer PO no + date; (customer, customer PO no) unique among non-cancelled SOs | field `422` / `409 TRADE_DUPLICATE_CUSTOMER_PO` |
| TSO-GRD-03 | Type rules as `TPO-GRD-02`; BLANKET Σ schedule = qty, dates ∈ validity (`TPO-GRD-04` mirror) | as TPO |
| TSO-GRD-04 | Part approval (FR-545) | `422 TRADE_CUSTOMER_PART_NOT_APPROVED` |
| TSO-GRD-05 | Every line priced; currency = contract / price list currency | field `422` |
| TSO-GRD-06 | Release qty ≤ schedule open qty (BLANKET/FIXED) or ≤ ceiling open (OPEN); dates ∈ validity | `422 TRADE_RELEASE_EXCEEDS_SCHEDULE` / `TRADE_CEILING_EXCEEDED` / `TRADE_OUTSIDE_VALIDITY` |
| TSO-GRD-07 | No open SO amendment on the lines | `409 TRADE_AMENDMENT_OPEN` |
| TSO-GRD-08 | Cancel: no release `RELEASED` whose demand order has been picked or shipped | `409 TRADE_EXECUTION_STARTED` |
| TSO-GRD-09 | Customer not sales-blocked at release | `422 TRADE_CUSTOMER_BLOCKED` |
| TSO-GRD-10 | Idempotency `(WHT_SALES_ORDER, id, version)` / `(WHT_SO_DISPATCH_RELEASE, id)` | — |
| TSO-GRD-11 | Short-close: open qty > 0; in-flight (picked not shipped) blocks that part | `409 TRADE_IN_FLIGHT` |
| TSO-GRD-12 | Revised schedule lines ≥ already released per line; dates ∈ validity (or validity extension in the same amendment) | `422 TRADE_AMEND_BELOW_COMMITTED` |

### 1.4 Unreachable

| ID | Forbidden | Why |
|---|---|---|
| TSO-UNR-01 | Trade writing `wh_demand_orders` | port only |
| TSO-UNR-02 | Core screens editing / cancelling a trade-created demand order's commercial fields | trade's `DemandOrderChangeGuard` bean (`p8-02`) refuses with `409 PO_OWNED_BY_SOURCE_MODULE` |
| TSO-UNR-03 | A credit check blocking release | refused (FRD §11 R1) — no such guard exists |
| TSO-UNR-04 | An SO invoice | refused (R2) |
| TSO-UNR-05 | Release blocked by ATP shortfall | FR-607: shown, never blocked; core's fulfilment policy decides backorder |

## 2. T2 — Action × role × state

Mirror of `TPO` §2 with *Acknowledge* = send (`:issue`), *Release* = `wht_so_dispatch_releases:create`
(dispatch planner), *Revise schedule* = `:amend`.

## 3. T3 — Time-driven rules

| ID | Rule | Trigger | Changes | Notified | Job |
|---|---|---|---|---|---|
| TSO-T3-01 | Dispatch due | schedule line open with `committed_date − warehouse.trade.sales.dispatch_horizon_days` (default 7) ≤ today | shown on WS-305 (computed) | dispatch planner digest | `TradeDispatchJob` daily |
| TSO-T3-02 | At risk | open line due within `warehouse.trade.sales.at_risk_days` (default 5) and unreleased, or released with ATP short | computed `atRisk` | sales exec + planner | same |
| TSO-T3-03 | Auto-close | mirror `TPO-T3-03` | `CLOSED` | sales exec | nightly |
| TSO-T3-04 | Validity ending | mirror `TPO-T3-05` | none | sales exec | `TradeContractJob` |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in |
|---|---|---|---|
| TSO-T4-01 | Approved | `WhDemandOrderPort.createDemand({sourceModule:'warehouse-trade', idempotencyKey:'WHT_SALES_ORDER:<id>:v<version>', actingUserId, sourceDocumentType:'WHT_SALES_ORDER', sourceDocumentId, sourceDocumentRef:<so_number>, salesOrderRef:<so_number>, customerPoRef, customerPoDate, demandType:'SALES', company, warehouse: dispatch site, customer, shipTo, lines[item, uom, qty], scheduleLines[lineNo, requestedDate: committed date, qty, kind]})` → one core demand order; id stored | approval transaction |
| TSO-T4-02 | Dispatch release / schedule amendment | `WhDemandOrderPort.releaseSchedule({coreDemandOrderId, releaseRef, scheduleLines[lineRef, requestedDate: planned dispatch date, qty, kind:'FIRM']})` (OPEN call-off adds `FIRM` lines); `amendDemand` on amendment keeps the core `FORECAST` lines equal to the unreleased schedule, which MRP reads and which never reserve (`POS-UNR-03`, closes `OD-32`) | same transaction |
| TSO-T4-03 | WS-305 read | ATP per item × dispatch site from core positions minus reservations (core query bean), computed in the backend | `DispatchPlanningQueryService` |
| TSO-T4-04 | Detail / grid read | picked, shipped, delivered quantities, shipments, outward gate passes (`p8-03`), challans / e-way bills (india, when installed — read through core references only) from core by `core_demand_order_id` | `SalesOrderQueryService` |
| TSO-T4-05 | SRA approved / RMA received | Returns tab; `REPLACE` drafts a replacement release (`TSR-T4-02`) | SRA service |

## 5. T5 — Screen contract

WS-303 grid `wht_sales_orders`, scope `WAREHOUSE_TRADE_SALES_ORDER` — columns mirror WS-292 with
`customerName`, `customerPoNumber`, `customerPoDate`, `salesExecName`, `dispatchWarehouseName`,
`shippedValue`. Tiles: awaiting approval, approved / ack not sent, at risk, overdue dispatch, open value.
WS-304 tabs per FRD-TRADE §6. WS-305 *Dispatch Planning*: grid of open schedule lines
`wht_so_dispatch_plan` — `soNumber`, `customerName`, `itemCode`, `customerPartNumber`, `committedDate`,
`customerRevisedDate`, `openQuantity`, `atpQuantity`, `shortfall`, `zone`; filters `dispatchWarehouseId`
(required), `customerId`, `horizonDays`, `atRiskOnly`; multi-select *Release* with per-line qty. WS-306
*Delivery Commitments*: at-risk / overdue lines with follow-ups (mirror WS-295).

## 6. Out of scope

| Item | Decision |
|---|---|
| Pick / pack / ship / outward gate pass / challan / e-way bill | core / `warehouse-india` |
| Credit limit, invoice, credit note | refused (FRD §11 R1–R3) |
| Make-to-order production trigger | MFG reads `FORECAST` and `FIRM` demand schedule from core (`OD-32`) |
| EDI schedules | refused (R7); CSV import is v1 |

## 7. Amendments

| Date | Rows | Change | Found by |
|---|---|---|---|
| 2026-10-22 | all | v0 derived | TRADE author |

## 8. Invariants and scenarios

`WH-SC-555`…`WH-SC-561`.

## 9. Open rows

| ID | Question | Status |
|---|---|---|
| TSO-OPEN-01 | Port signatures vs `p8-02` | reconcile when `p8-02` lands |
| TSO-OPEN-02 | Does `getFulfilmentPosition` expose picked-not-shipped per schedule line (needed by `TSO-GRD-08`, `-11`)? | confirm with `p8-02` |
