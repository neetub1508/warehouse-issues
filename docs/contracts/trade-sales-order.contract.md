# Functional Contract — Sales order (FIXED / OPEN / BLANKET), customer delivery schedule, dispatch planning and releases, acknowledgement, commitment tracking, short-close

> **What this is.** The functional truth for the commercial sales order in `warehouse-trade`: its three
> types, the customer delivery schedule, dispatch planning from the FG store and the hand-off of each
> dispatch release to the SO's one core demand order through the `p8-02` port, the order acknowledgement,
> delivery commitment tracking and short-close. Picking, packing, shipping, the outward gate pass and the
> challan / e-way bill are core's and `warehouse-india`'s; this contract only **reads** them.
>
> **Purchase twin.** [trade-purchase-order](trade-purchase-order.contract.md), **row for row**: every `TSO-*`
> id below has the `TPO-*` row of the same number as its twin; a row says *same as*, states the difference, or
> writes the refusal. Both sides keep **one core execution document per trade order** and release by firming
> its schedule (FRD-TRADE §5 M18); the demand header follows STORES `OD-45` option (A).
>
> **Port names.** Every port method, command field, operation key, event and refusal code below is
> FRD-STORES *"Port & seam registry (authoritative)"*'s; trade's keys, principal and grants are FRD-TRADE §12a.
>
> **Status.** Derived 2026-10-22 (v0), R29 folded (v1). No code exists yet.

---

## 0. Identity

| | |
|---|---|
| **Workflow** | Draft (manual / from won quotation / from sales RC) → submit → approve (core demand order via port) → acknowledge to customer → dispatch planning → dispatch releases (OPEN customer call-offs, BLANKET schedule lines; FIXED needs none, `TRD-12`) → core pick / pack / ship → complete / short-close → closed (`closeDemand`); cancel before execution; customer schedule revisions; commitment tracking |
| **Module** | `warehouse-trade`; core `warehouse` through `WhDemandOrderPort` and `WhAvailableToPromiseQuery` (`ai.warehouse.port.demand`; [po-schedule-port](po-schedule-port.contract.md) `POS-T1-10`…`-12b`, `POS-T4-05`…`-08`) and read-only queries |
| **Domain baseline** | FRD-TRADE FR-605…FR-611, FR-681 (lost sale, `D-17` item 4; core `FR-257`), FR-543, FR-545, `TRD-01`, `TRD-02` (twin of `trade-purchase-order`), `TRD-03`, `TRD-12`, `TRD-13`, `OD-32`, `OD-39`, STORES `OD-45` · R28 §4 D1–D3 |
| **Owning task bodies** | `issues/p9-09.md` (types, schedule, dispatch planning, releases, port, cancel, schedule import) · `issues/p9-10.md` (acknowledgement, commitments, short-close, auto-close) |
| **Primary tables** | `wht_sales_orders`, `wht_sales_order_lines`, `wht_so_schedule_lines`, `wht_so_dispatch_releases`, `wht_so_dispatch_release_lines`, `wht_so_charges` (`V550080`); `wht_so_acknowledgements`, `wht_so_commitment_followups` (`V550090`) |
| **Permission resources** | `wht_sales_orders:view/create/edit/export/submit/approve/cancel/issue/short_close/amend` · `wht_so_dispatch_releases:view/create/submit/approve/cancel/export` · `wht_so_commitment_followups:view/create/export`. The sales-executive, sales-approver and dispatch-planner bundles also hold core **`warehouse:orders:port`** (`TRD-13`, seeded in `V551090`) |
| **Routes** | WS-303 `/warehouse/trade/sales/orders`, WS-304 `/[id]`, WS-313 `/dispatch-releases`, WS-306 `/commitments`, WS-305 `/dispatch-planning` · mobile: none |
| **Contract status / version** | `derived` · `v1 — 2026-10-22` |

**Fields** (twin of `TPO` §0). Header: `so_number` (series `SO`, at submit; stored on the core demand order as
`sales_order_ref` and `source_document_ref`), `so_type`, `version_no`, company, customer, `customer_po_number`,
`customer_po_date`, `sales_exec_id`, `order_date`, `dispatch_warehouse_id`, `ship_to_address_id`, currency,
terms, `quotation_id`, `rate_contract_id`, `price_list_id`, `valid_from`/`valid_to` (OPEN/BLANKET),
`ceiling_value` (OPEN; null ⇒ `open_unbounded`), `price_basis` (`AGREEMENT`/`AT_RELEASE`),
`terms_template_version_id`, `status`, `core_demand_order_id` ↓ `wh_demand_orders`, `issued_at`, `ack_status`
(`PENDING`/`SENT`), `closed_at`, `short_close_reason_code`. Line: `line_no`, item, `customer_part_number`,
`customer_item_ref_id`, `uom_code`, `quantity` (FIXED/BLANKET > 0; OPEN null), `ceiling_quantity` (OPEN),
`unit_price`, `discount_percent`, `net_price`, `price_source`, `rate_contract_line_id`, `floor_price_at_order`,
`over_tolerance_pct`, `under_tolerance_pct`, `is_free_of_charge` (FIXED / BLANKET only), `line_status`,
`core_demand_line_id`. Schedule line: `delivery_date` (requested), `committed_date` (our acknowledged date,
defaults to the requested one), `customer_revised_date`, `quantity`, `zone` (from
`warehouse.trade.sales.firm_zone_days`), `released_quantity`, `pending_release_quantity`, `release_status`
(FIXED: `RELEASED` at approval), `core_schedule_line_id`, `lost_sale_quantity` (captured by `TSO-T4-13`, default 0). Dispatch release: `release_number` (`<so_number>-Dnn`,
per-order counter, at submit), `release_date`, `planned_dispatch_date`, `status`, `approval_request_id`,
`is_replacement`, `source_sra_id`, `customer_calloff_ref`, `cancel_reason_code`; release line: `so_line_id`,
`schedule_line_id` (null for an OPEN call-off or a replacement), qty, `unit_price`, `core_schedule_line_id`.

### Acceptance checks

| # | Expects | Delivered by |
|---|---|---|
| A1 | Approval of every type creates one core demand order in the approval transaction; a refusal rolls back (`WH-SC-555`, `-593`) | `TSO-T1-04`, `TSO-T4-01`, `-03` |
| A2 | Idempotent approval and release | `TSO-GRD-12` |
| A3 | OPEN call-offs within ceiling (pending included) and validity; RC ceiling (`WH-SC-588`) | `TSO-T1-08`, `TSO-GRD-06`, `-07` |
| A4 | BLANKET dispatch planning shows ATP; shortfall shown not blocked; over-release refused; FIXED not released (`WH-SC-557`, `-558`, `-596`) | `TSO-T1-09`, `TSO-GRD-06`, `TSO-T4-12` |
| A5 | Shipments read from core; fulfilment derived (`WH-SC-559`) | `TSO-T4-04` |
| A6 | Short-close via port; tolerance (`TSO-T1-13`) | `TSO-T1-13`, `TSO-T4-06` |
| A7 | Cancel only before execution and through `SO_CANCEL`; core cannot edit trade demand orders | `TSO-T1-05`, `TSO-GRD-09`, `TSO-UNR-02` |
| A8 | Customer blocked: no new releases | `TSO-GRD-08` |
| A9 | Acknowledgement printed with committed dates, re-sent after amendment (`WH-SC-556`, `-584`) | `TSO-T1-06`, `-11` |
| A10 | At-risk commitments with a revised date apart from committed (`WH-SC-561`) | `TSO-T3-02` |
| A11 | Auto-close calls `closeDemand`; the core order stays open across releases until then (`WH-SC-580`) | `TSO-T3-03`, `TSO-T4-10` |
| A12 | A dispatch release can be cancelled, a rejected one gives its quantity back, and a release closes by its own core lines (`WH-SC-586`) | `TSO-T1-10a`…`-10c`, `-12` |
| A13 | Customer schedule revision through amendment, firm-zone flagged; a newer import replaces a draft (`WH-SC-560`, `-589`) | `TSO-T1-15` |
| A14 | Replacement release from a return (`WH-SC-587`) | `TSO-T1-16`, `TSO-GRD-06` |
| A15 | Quantity cancelled or short-closed **for stock** (incl. the unreleased rest of a release planned short on ATP) records one core lost sale per schedule line and request; other reasons record none (`WH-SC-599`) | `TSO-T4-13`, `TSO-UNR-08` |

## 1. T1 — State machine

### 1.1 Status inventory

| Entity | Status | Reachable via | Exits via | Kind |
|---|---|---|---|---|
| SO | `DRAFT` | `-01`, win, return | `-02`, `-05` | initial |
| SO | `SUBMITTED` | `-02` | `TAM`, `-03` | active |
| SO | `REJECTED` | `TAM` | edit → `DRAFT` | active |
| SO | `APPROVED` | `-04` | `-06`, `-05`, `-08`/`-09`, `-13` | active |
| SO | `ISSUED` | `-06` (acknowledgement sent) | releases, `-11`, `-13`, `-05` | active |
| SO | — (twin of `ACKNOWLEDGED`) | **refused**: we issue the acknowledgement, the customer does not return one (§5 M22); `ISSUED` is the acknowledged state | — | — |
| SO | `CLOSED` | `TSO-T3-03` | none | terminal |
| SO | `SHORT_CLOSED` | `-13a` header | none | terminal |
| SO | `CANCELLED` | `-05`, `-05a` | none | terminal |
| SO | *fulfilment* `NOT_STARTED` / `PARTIAL` / `COMPLETE`; *validity* `EXPIRED` (OPEN/BLANKET) | **derived on read** (`TSO-T4-04`) | — | derived |
| Dispatch release | `DRAFT` | `-08`, `-09`, `-16`, return | submit, `-10b` | initial |
| Dispatch release | `SUBMITTED` | `-08`, `-09`, `-16` | `-10`, `-10a`, `-10b` (withdraw) | active |
| Dispatch release | `RELEASED` | `-10` | `-10c`, `-12` | active |
| Dispatch release | `REJECTED` | `-10a` | edit → `DRAFT`, `-10b` | active |
| Dispatch release | `CANCELLED` | `-10b`, `-10c` | none | terminal |
| Dispatch release | `CLOSED` | `-12` | none | terminal |
| Ack | `PENDING` (approved, not yet sent; or reset by an approved amendment) → `SENT` | `-04`, `-06`, `-11`, `TOA-T4-03` | — | — |

### 1.2 Transitions

| ID | From | Action | To | Guard | Actor | Side effects | Comment | UI | Source |
|---|---|---|---|---|---|---|---|---|---|
| TSO-T1-01 | — | Create (manual / from won quotation / from sales RC) | `DRAFT` | — | `:create` (win target: maker = the user who marked the win) | prices `TRC-T4-04`; quotation charges carried to `wht_so_charges` | no | WS-303 Add (type picker first) | FR-605 |
| TSO-T1-02 | `DRAFT`, `REJECTED` | Submit | `SUBMITTED` | `TSO-GRD-01`…`-05`, `-08`, `-10`, `-17`, `-18` | `:submit` | number; `TAM-T1-03` doc `SO`, value as `TPO-T1-02` (OPEN without ceiling value: `open_unbounded`), conditions `below_floor_price`, `discount_over_pct`, `manual_rate` | no | Submit | FR-605 |
| TSO-T1-03 | `SUBMITTED` | Withdraw | `DRAFT` | `TAM-T1-09` | maker | — | no | Withdraw | FR-551 |
| TSO-T1-04 | `SUBMITTED` | Approved (last level) | `APPROVED` | `TSO-GRD-11`, `-12` | approver (holds `warehouse:orders:port`) | **`WhDemandOrderPort.createDemand`** (`POS-T1-10`) in the same transaction (`TSO-T4-01`) — every type; `version_no = 1` snapshot; RC consumption for FIXED and BLANKET lines; FIXED schedule lines → `RELEASED`; ack `PENDING` | — | WS-285 | FR-606 |
| TSO-T1-04a | `SUBMITTED` | Rejected / returned | `REJECTED` / `DRAFT` | `TAM` | approver | maker notified | **yes** | WS-285 | FR-551 |
| TSO-T1-05 | `DRAFT`; `SUBMITTED` (withdraw first); `APPROVED`, `ISSUED` | Cancel | `DRAFT`/`SUBMITTED`: `CANCELLED` at once; after approval: request `SO_CANCEL` (seeded zero-level) | `TSO-GRD-09`, `-14` (header) | `:cancel` | after approval → `-05a` | **yes**, reason code | row action | FR-609 |
| TSO-T1-05a | `SO_CANCEL` request approved | Cancel takes effect | `CANCELLED` | `TSO-GRD-09` re-checked | approver / `SYSTEM` | **`cancelDemand`** (`TSO-T4-06`); RC consumption reversed; open releases `CANCELLED` | — | WS-285 | FR-609 |
| TSO-T1-06 | `APPROVED` | Send acknowledgement | `ISSUED`; ack `SENT` | template exists | `:issue` | print `SALES_ORDER_ACK` with committed dates; `wht_so_acknowledgements` row for the version | no | *Acknowledge* | FR-606 |
| TSO-T1-07 | any non-terminal | Reprint | — | — | `:view` | reprint flagged | no | Print | FR-615 |
| TSO-T1-08 | OPEN, `APPROVED`/`ISSUED` | Record and submit a customer call-off release | release `DRAFT` → `SUBMITTED` | `TSO-GRD-06`, `-07`, `-08`, `-14` | `wht_so_dispatch_releases:create` / `:submit` | number `<so>-Dnn`; price by `price_basis`; `TAM` doc `SO_RELEASE` (seeded zero-level `EXACT`; `open_unbounded` / `release_price_manual` need an install rule), value Σ qty × price; `pending_release_quantity` += qty | customer call-off ref | WS-304 Releases tab, WS-313 *New call-off* | FR-605 |
| TSO-T1-09 | BLANKET, same states | Plan dispatch — release due schedule line(s), whole or part (multi-select; one release per SO × planned dispatch date) | release `SUBMITTED` | `TSO-GRD-06`…`-08`, `-14`; FIXED lines not offered (`TRD-12`) | same | as `-08`; ATP shown (`TSO-T4-12`) | no | WS-305 *Release* | FR-607 |
| TSO-T1-10 | release `SUBMITTED` | Approved | `RELEASED` | `TSO-GRD-15`, `-12` | approver / `SYSTEM` (submitter is the port's `actingUserId`) | **`firmScheduleLine`** / **`releaseSchedule`** (`POS-T1-11`, `-11a`) in the same transaction (`TSO-T4-02`); pending → `released_quantity`; RC consumption (OPEN) | — | — | FR-607 |
| TSO-T1-10a | release `SUBMITTED` | Rejected / returned | `REJECTED` / `DRAFT` | `TAM` | approver | pending quantity reverted | **yes** | WS-285 | FR-551 |
| TSO-T1-10b | release `DRAFT`, `REJECTED`; `SUBMITTED` after withdraw | Cancel | `CANCELLED` | — | `wht_so_dispatch_releases:cancel` | pending reverted; nothing sent to core | **yes**, reason code | WS-313 / WS-304 | FR-609 |
| TSO-T1-10c | release `RELEASED`, nothing of it picked | Cancel | `CANCELLED` | `TSO-GRD-09` per release line (picked = 0 on its core schedule lines, `getFulfilmentPosition`); `TSO-GRD-14` | `wht_so_dispatch_releases:cancel` | **`unfirmScheduleLine`** for whole-firmed BLANKET lines (allocated 0; else core refuses `409 DEMAND_SCHEDULE_ALLOCATED` and the planner releases the allocation first), **`cancelScheduleLine`** for added `FIRM` lines (call-off, split, replacement) with a split `FORECAST` restored by `amendDemand` (`TSO-T4-09`); schedule qty open again; RC consumption reduced | **yes**, reason code | WS-313 / WS-304 | FR-609 |
| TSO-T1-11 | `ISSUED` with ack `PENDING` (after an approved amendment) | Re-send acknowledgement | ack `SENT` | template exists | `:issue` | print `SALES_ORDER_ACK` of the new version with the amendment banner; new `wht_so_acknowledgements` row. Twin of `TPO-T1-11` (we issue, they record — §5 M22) | no | *Re-send acknowledgement* | FR-606 |
| TSO-T1-12 | release `RELEASED` | Every core schedule line carrying its `releaseRef` is shipped or cancelled (`WH_DEMAND_SHIPPED`, `getFulfilmentPosition`) | `CLOSED` | — | system | — | — | — | FR-608 |
| TSO-T1-13 | line `OPEN` / header non-terminal | Short-close line or header | request `SO_SHORT_CLOSE` (seeded zero-level) | `TSO-GRD-13`, `-14` | `:short_close` | — | **yes**, reason code | row action / line action | FR-609 |
| TSO-T1-13a | `SO_SHORT_CLOSE` request approved | Short-close takes effect | line `SHORT_CLOSED`; header `SHORT_CLOSED` when header action | `TSO-GRD-13` re-checked | approver / `SYSTEM` | **`cancelScheduleLine`** for every open unpicked schedule line of the line (`FORECAST`, and `FIRM` with nothing picked — core releases its allocation); header: then **`closeDemand`** (`TSO-T4-06`); open releases closed; RC consumption reduced | — | WS-285 | FR-609 |
| TSO-T1-14 | any active | Log commitment follow-up | follow-up row; `customer_revised_date` | — | `wht_so_commitment_followups:create` | — | no | WS-306, detail | FR-610 |
| TSO-T1-15 | BLANKET non-terminal | Import / enter revised customer schedule | SO amendment `DRAFT` (`TOA-T1-01`, origin `CUSTOMER_SCHEDULE`); a `DRAFT` amendment of the same origin is `CANCELLED` and replaced | `TSO-GRD-19`; no `SUBMITTED` amendment open | `:amend` | changes inside the sales firm zone flagged (`in_firm_zone = true`, counted for `TCE`). Twin: `TPO-T1-11` *Accept changes* drafts the purchase amendment | no | WS-304 *Revise schedule* (CSV dry-run → apply) | FR-611 |
| TSO-T1-16 | SRA `RECEIVED` / `PARTIALLY_RECEIVED` with intent `REPLACE` | Replacement release drafted | release `DRAFT`, `is_replacement`, `source_sra_id` | `TSO-GRD-06` (replacement bound) | system (`TSR-T4-02`); the planner submits it | lines for the received qty at the original net price, no schedule line. Twin: `TPO-T4-07` reinstates through an amendment (§5 M26) | no | WS-313 | FR-612 |

### 1.3 Guards

| ID | Predicate | Refusal | Source |
|---|---|---|---|
| TSO-GRD-01 | Customer profile exists, not sales-blocked; dispatch site in user scope and allows dispatch | `422 TRADE_CUSTOMER_BLOCKED` | FR-543 |
| TSO-GRD-02 | Type rules as `TPO-GRD-02`: FIXED — qty > 0, Σ schedule = qty; OPEN — qty null, validity, unit price > 0; BLANKET — qty > 0, validity | field `422` | FR-605 |
| TSO-GRD-03 | Every line priced (0 only free-of-charge + reason, never on OPEN); currency = contract / price list currency | field `422` | FR-604 |
| TSO-GRD-04 | BLANKET: Σ schedule = line qty, dates ∈ validity; FIXED: schedule dates ≥ order date | `422 TRADE_SCHEDULE_TOTAL_MISMATCH` / `TRADE_OUTSIDE_VALIDITY` | FR-605 |
| TSO-GRD-05 | Item active and sellable; UoM convertible (`whb_item_uom_conversions`, factor frozen); dispatch site in the user's scope (twin of `TPO-GRD-05`) | field `422` / `TRADE_UOM_NOT_CONVERTIBLE` | FR-605 |
| TSO-GRD-06 | Release: dates ∈ validity; FIXED lines never released; qty ≤ schedule open (qty − released − pending) for BLANKET; OPEN: Σ released + pending ≤ line ceiling and ≤ header ceiling value; a **replacement** release (`is_replacement`) is exempt from schedule and ceiling bounds and bounded instead by the SRA's received quantity − already replaced | `422 TRADE_RELEASE_EXCEEDS_SCHEDULE` / `TRADE_CEILING_EXCEEDED` / `TRADE_OUTSIDE_VALIDITY` / `TRADE_NOT_RELEASABLE` / `TRADE_REPLACEMENT_EXCEEDS_RECEIVED` | FR-607 |
| TSO-GRD-07 | RC ceiling consumed on release (`TRC-T4-01`) | `422 TRADE_CEILING_EXCEEDED` | FR-603 |
| TSO-GRD-08 | Customer not sales-blocked at release / qty-increasing amendment (a replacement release is allowed) | `422 TRADE_CUSTOMER_BLOCKED` | FR-543 |
| TSO-GRD-09 | Cancel (order, or a released part): nothing picked or shipped on the core schedule lines concerned (`getFulfilmentPosition`, `POS-T4-07`) | `409 TRADE_EXECUTION_STARTED` | FR-609 |
| TSO-GRD-10 | Edit refused while an approval request or an amendment is open (twin of `TPO-GRD-10`) | `409 TRADE_APPROVAL_PENDING` / `TRADE_AMENDMENT_OPEN` | FR-553 |
| TSO-GRD-11 | At approval: re-resolve contract / price-list prices; refuse if the source expired, ended or changed (twin of `TPO-GRD-11`) | `409 TRADE_PRICE_CHANGED_SINCE_SUBMIT` | FR-604 |
| TSO-GRD-12 | Idempotency: FRD-TRADE §12a keys (`WHT_SALES_ORDER:<id>:<operation>:<sequence>`); a repeat returns the recorded result | `409 PORT_IDEMPOTENCY_CONFLICT` (relayed) | FR-618 |
| TSO-GRD-13 | Short-close: open qty > 0; picked-not-shipped (`getFulfilmentPosition`) blocks that part | `409 TRADE_IN_FLIGHT` | FR-609 |
| TSO-GRD-14 | Amendment lock (`TOA-GRD-04`): a release, release cancel or line short-close touching a schedule line an open amendment changes is refused; a header short-close or cancel is refused while any amendment is open | `409 TRADE_AMENDMENT_OPEN` | FR-591 |
| TSO-GRD-15 | At release approval, under a lock on the SO header: `-06`, `-07`, `-08`, part approval (`-18`), price (`-11`) and `-14` re-checked | as each guard | FR-607, FR-618 |
| TSO-GRD-16 | — (twin of `TPO-GRD-16` receipt cut-off) | **refused**: shipping firm released quantity after validity is our own act; core has no despatch cut-off and needs none | FR-605 |
| TSO-GRD-17 | `customer_po_required` ⇒ customer PO no + date; (customer, customer PO no) unique among non-cancelled SOs | field `422` / `409 TRADE_DUPLICATE_CUSTOMER_PO` | FR-605 |
| TSO-GRD-18 | Part approval (FR-545) | `422 TRADE_CUSTOMER_PART_NOT_APPROVED` | FR-545 |
| TSO-GRD-19 | Revised schedule lines ≥ released per line; dates ∈ validity (or validity extension in the same amendment) | `422 TRADE_AMEND_BELOW_COMMITTED` | FR-611 |

### 1.4 Unreachable

| ID | Forbidden | Why | Source |
|---|---|---|---|
| TSO-UNR-01 | Trade writing `wh_demand_orders` | port only | FR-605, FR-608 |
| TSO-UNR-02 | Core screens editing, releasing, cancelling or closing a trade-created demand order | trade's `DemandOrderChangeGuard` bean (`POS-GRD-14`) refuses `EDIT`, `RELEASE`, `CANCEL`, `CLOSE` with `409 DEMAND_OWNED_BY_SOURCE_MODULE`; `ALLOCATE` is allowed (`OD-39`) | FR-608 |
| TSO-UNR-03 | Changing an approved SO except by amendment; a credit check blocking release | no edit after approval (`TOA`); credit refused (FRD §11 R1) — no such guard exists | FR-553 |
| TSO-UNR-04 | Auto-release of a BLANKET schedule line; an SO invoice | releases are planner acts (twin of `TRD-11`); invoice refused (R2) | FR-605 |
| TSO-UNR-05 | Storing shipped quantity in `wht_`; a release blocked by ATP shortfall | `TRD-03`; FR-607: shown, never blocked | FR-607, FR-608 |
| TSO-UNR-06 | Changing `so_type` after submit | not editable | FR-605 |
| TSO-UNR-07 | A trade SO `CLOSED` while its core demand order can still take releases | auto-close and header short-close call `closeDemand` in the same transaction | FR-609 |
| TSO-UNR-08 | A lost sale captured at release, or twice for one cancel / short-close request | a release is never refused for ATP (`TSO-UNR-05`), so nothing is lost there; `TSO-T4-13` runs once in the approving transaction, keyed `<scheduleLineId>:<approvalRequestId>` | FR-681 |

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from |
|---|---|---|---|
| TSO-T2-01 | Add / edit | `:create` / `:edit` | `DRAFT`, `REJECTED` |
| TSO-T2-02 | Submit / withdraw | `:submit` | `DRAFT`, `REJECTED` / `SUBMITTED` |
| TSO-T2-03 | Approve | `:approve` (`TAM`) + `warehouse:orders:port` | `SUBMITTED`; `SO_CANCEL` / `SO_SHORT_CLOSE` requests |
| TSO-T2-04 | Send acknowledgement / print | `:issue` / `:view` | `APPROVED`+ |
| TSO-T2-05 | Re-send acknowledgement | `:issue` | `ISSUED` with ack `PENDING` |
| TSO-T2-06 | Dispatch release — create / submit / approve / cancel | `wht_so_dispatch_releases:create` / `:submit` / `:approve` / `:cancel` (+ `warehouse:orders:port` as `TPO-T2-06`) | SO `APPROVED`, `ISSUED`; release per T1 |
| TSO-T2-07 | Amend / revise schedule | `:amend` (`TOA`) | `APPROVED`, `ISSUED` |
| TSO-T2-08 | Short-close | `:short_close` | non-terminal |
| TSO-T2-09 | Cancel | `:cancel` | non-terminal, `TSO-GRD-09` |
| TSO-T2-10 | Commitment follow-up | `wht_so_commitment_followups:create` | non-terminal |
| TSO-T2-11 | Export | `:export`; `wht_so_dispatch_releases:export`; `wht_so_commitment_followups:export` (auditor: none) | — |

## 3. T3 — Time-driven rules

| ID | Rule | Trigger | Changes | Notified (FRD-TRADE §12b) | Job | Source |
|---|---|---|---|---|---|---|
| TSO-T3-01 | Dispatch due (twin of the release proposal) | open BLANKET / OPEN schedule line with `committed_date − warehouse.trade.sales.dispatch_horizon_days` (default 7) ≤ today | shown on WS-305 (computed) | dispatch planners of the dispatch site, digest `TRADE_DISPATCH_DUE` | `TradeDispatchJob` daily | FR-607 |
| TSO-T3-02 | At risk (twin of expediting) | open line due within `warehouse.trade.sales.at_risk_days` (default 5) and unreleased, or released with ATP short (`TSO-T4-12`) | computed `atRisk` | sales exec + planners, `TRADE_COMMITMENT_AT_RISK` | same | FR-610 |
| TSO-T3-03 | Auto-close | every line `SHORT_CLOSED` or fulfilment `COMPLETE` (shipped ≥ qty × (1 − under tolerance)), no release open, **no SRA of the SO open**; OPEN/BLANKET also when validity ended and nothing open | `CLOSED`; `closeDemand` (`TSO-T4-10`) | sales exec, `TRADE_ORDER_CLOSED` | nightly `TradeSoCloseJob` (acts as the SO's sales executive) | FR-609 |
| TSO-T3-04 | Ack not sent (twin of ack overdue) | ack `PENDING` `warehouse.trade.sales.ack_send_alert_days` (default 1) after approval or after the amendment that reset it | none | sales exec, `TRADE_SO_ACK_NOT_SENT` | `TradeDispatchJob` | FR-606 |
| TSO-T3-05 | Validity ending | OPEN/BLANKET `valid_to − 30` | none | sales exec, `TRADE_SO_VALIDITY_ENDING` | `TradeContractJob` | FR-605 |
| TSO-T3-06 | Dispatch overdue (twin of release overdue) | BLANKET / OPEN schedule line unreleased with `committed_date < today` | computed `dispatchOverdue` on WS-305 / WS-306; counted against our own `DELIVERY_OTIF` (`TCE`) | sales exec + planners (in the at-risk digest) | `TradeDispatchJob` | FR-610 |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in | Source |
|---|---|---|---|---|
| TSO-T4-01 | Approved (every type) | `WhDemandOrderPort.createDemand(CreateDemandCommand{ envelope(sourceModule 'warehouse-trade', idempotencyKey 'WHT_SALES_ORDER:<id>:DEMAND_CREATE:1', actingUserId = last approver), sourceDocumentType 'WHT_SALES_ORDER', sourceDocumentId, sourceDocumentRef <so_number>, demandType 'SALES', customerCounterpartyId, warehouseId = dispatch site, ownerId, salesOrderRef <so_number>, customerPoRef, customerPoDate, fulfilmentPolicy, shipToAddressId = `ship_to_address_id`, lines[ lineRef <line_no>, itemId, uomCode, orderedQuantity (ignored for a schedule-driven line; OPEN: null with no schedule, which core makes schedule-driven — `CN-4`), unitPrice, requiredDate, schedule[ kind FIXED→FIRM · BLANKET→FORECAST (OPEN: none), requestedDate = committed date, quantity, releaseRef (FIXED: the SO number; BLANKET: `<so_number>-S<schedule no>`) ] ] })` → one core demand order, schedule-driven, its header following `OD-45` (A) (`POS-T1-12b`); ids stored. Ship-to reaches core on the create, snapshotted into `ship_to_*` (`POS-GRD-16`; FRD-TRADE §12c `CN-3`, resolved) | approval transaction | FR-605 |
| TSO-T4-02 | Dispatch release approved | a whole BLANKET schedule line → `firmScheduleLine(DemandScheduleLineCommand{ scheduleLineId })` (key `…:DEMAND_FIRM:<release no>-<schedule no>`); an OPEN call-off, a split BLANKET line or a replacement → `releaseSchedule(ReleaseDemandScheduleCommand{ demandOrderId, releaseRef <release no>, entries[ demandLineId, FIRM, requestedDate = planned dispatch date, quantity ] })` (key `…:DEMAND_RELEASE:<release no>`) — for a split BLANKET line the `FORECAST` line is reduced to the remainder by `amendDemand` (key `…:DEMAND_AMEND:<release no>`); the core `FIRM` line ids stored. Core `FORECAST` lines stay equal to the unreleased schedule, which MRP reads and which never reserve (`POS-UNR-03`, closes `OD-32`) | release approval transaction | FR-607 |
| TSO-T4-03 | Any port call refused | trade transaction rolls back; core error relayed (twin of `TPO-T4-03`) | port adapter | FR-618 |
| TSO-T4-04 | Detail / grid read | allocated, picked, shipped, delivered, backordered quantities per line and schedule line (`getFulfilmentPosition`, `POS-T4-07`), shipments, outward gate passes (`p8-03`), challans / e-way bills (india, when installed — read through core references only) by `core_demand_order_id`; fulfilment `COMPLETE` when every line shipped ≥ qty × (1 − under tolerance) or short-closed | `SalesOrderQueryService` | FR-608 |
| TSO-T4-05 | Ack sent / re-sent | trade only — the acknowledgement is our print; nothing goes to core (twin of `TPO-T4-05`) | ack transaction | FR-606 |
| TSO-T4-06 | Short-close / cancel approved | `cancelScheduleLine(DemandScheduleLineCommand{ scheduleLineId, reasonCodeId })` per open unpicked schedule line, header: `closeDemand(CloseDemandCommand)`; cancel: `cancelDemand(CancelDemandCommand)`; keys `WHT_SALES_ORDER:<soId>:<op>:<request id>-<n>`; RC consumption reduced | same transaction | FR-609 |
| TSO-T4-07 | SRA received with intent `REPLACE` | `TSO-T1-16` drafts the replacement release; the SO stays open (`TSO-T3-03`); on a `SHORT_CLOSED` / `CANCELLED` SO nothing is drafted and the SRA asks for a declined reason (`TSR-T1-05`) — twin of `TPO-T4-07` | SRA service | FR-612 |
| TSO-T4-08 | Any write | `whb_audit_events` | services | FR-540 |
| TSO-T4-09 | Dispatch release cancelled after approval | `unfirmScheduleLine` (key `…:DEMAND_UNFIRM:<release no>-X<n>`) or `cancelScheduleLine` (key `…:DEMAND_CANCEL_SCHEDULE:<release no>-X<n>`) + `amendDemand` restoring a split `FORECAST` (key `…:DEMAND_AMEND:<release no>-X`) | release cancel transaction | FR-607 |
| TSO-T4-10 | Auto-close | `closeDemand(CloseDemandCommand{ demandOrderId, reasonCodeId = AUTO_CLOSE })`, key `…:DEMAND_CLOSE:AUTO` — the core order then follows its ordinary ladder (`POS-T1-12a`); nothing unshipped ⇒ `SHIPPED` at once | close job transaction | FR-609 |
| TSO-T4-11 | Core events for this SO (`WH_DEMAND_SHIPPED` per `release_ref`, `WH_DEMAND_AMENDED`, `WH_DEMAND_CANCELLED`) | release close (`TSO-T1-12`), commitments refresh; a core-side cancel the trade SO did not cause is logged for the sales executive | outbox subscriber | FR-608 |
| TSO-T4-12 | WS-305 / at-risk read | `WhAvailableToPromiseQuery.atp(AtpQuery{ warehouseId = dispatch site, ownerId, itemIds, horizonEnd })` → `availableNow`, open reservations, firm scheduled receipts by date; shortfall = due open − (`availableNow` + receipts before the date), computed in the backend, never a reservation (`POS-T4-08`) | `DispatchPlanningQueryService` | FR-607 |
| TSO-T4-13 | `SO_CANCEL` (`TSO-T1-05a`, `-10c`) or `SO_SHORT_CLOSE` (`TSO-T1-13a`) approved with a reason in `warehouse.trade.sales.lost_sale_reason_codes` | per schedule line losing quantity: core `captureLostSale(WhLostSaleRequest{ warehouseId = dispatch site, itemId, ownerId = house owner, requestedQuantity = the cancelled / short-closed base quantity, lostSaleReasonCodeId = `TRADE_STOCK_NOT_AVAILABLE`, sourceSystem `WAREHOUSE_TRADE`, sourceType `TRADE_SO_SCHEDULE_LINE`, sourceId `<scheduleLineId>:<approvalRequestId>` }, actor = the last approver, `TRD-13`)` after the port's `cancelScheduleLine` (`TSO-T4-06`); `lost_sale_quantity` += that quantity. The *short for ATP* case is this row: the planner releases what ATP allows (`TSO-T4-12`) and short-closes the rest with `NO_STOCK`. A core refusal rolls the approval back (`TSO-T4-03`) | same transaction | FR-681 |

## 5. T5 — Screen contract

### 5.1 WS-303 Sales Orders (reference **Service Vehicle**)
Grid `wht_sales_orders`, scope `WAREHOUSE_TRADE_SALES_ORDER`, sort `e.order_date DESC`. Tiles: awaiting
approval, approved / ack not sent, at risk, overdue dispatch, open value (company currency, plus *+n in other
currencies*, FR-616). Columns: `soNumber`, `soType`, `versionNo`, `customerName`, `customerGrade`,
`customerPoNumber`, `customerPoDate`, `dispatchWarehouseName`, `salesExecName`, `orderDate`, `validTo`,
`currencyCode`, `orderValue`, `releasedValue`, `shippedValue`, `fulfilment` (derived), `ackStatus`, `status`,
audit. Filters: `dispatchWarehouseId`; `soType`; `status`; `customerId` typeahead; `salesExecId`; `itemId`;
`currencyCode`; `orderFrom`/`orderTo`; `atRiskOnly`; `ackPendingOnly`. Row actions: View · Edit · Submit ·
Withdraw · Acknowledge · Re-send acknowledgement · Print · Release · Amend · Short-close · Cancel. Toolbar: Add ·
Export (⊇ grid). Add/Edit modal tabs: Header · Lines · Schedule · Charges & terms.

### 5.2 WS-304 Detail — tabs per FRD-TRADE §6.

### 5.3 WS-313 Dispatch Releases (twin of WS-294)
Grid `wht_so_dispatch_releases`, scope `WAREHOUSE_TRADE_SO_DISPATCH_RELEASE`, sort `e.release_date DESC`.
Tiles: due (from WS-305), dispatch overdue, submitted, released (period), replacements pending — counts.
Columns: `releaseNumber`, `soNumber`, `soType`, `customerName`, `releaseDate`, `plannedDispatchDate`,
`lineCount`, `releaseValue`, `currencyCode`, `isReplacement`, `status`, `coreDemandOrderNumber`, audit.
Filters: `customerId`, `dispatchWarehouseId`, `soId`, `status`, `replacementOnly`, `dueFrom`/`dueTo`. Actions:
View · Submit · Withdraw · Cancel (`TSO-T1-10b`, `-10c`) · Open demand order (core, read). Export ⊇ grid
(`wht_so_dispatch_releases:export`). Empty state: *No dispatch releases — plan them on Dispatch Planning.*
Print: none (§5 M32 refusal).

### 5.4 WS-306 Delivery Commitments (twin of WS-295)
Grid `wht_so_commitments` (open schedule lines due within `at_risk_days` or overdue), scope
`WAREHOUSE_TRADE_SO_COMMITMENT`, sort `e.committed_date ASC`. Tiles: at risk, dispatch overdue, follow-up due
today, ack not sent, customer-revised later than committed — counts. Columns: `soNumber`, `releaseNumber`,
`customerName`, `itemCode`, `customerPartNumber`, `committedDate`, `customerRevisedDate`, `openQuantity`,
`atpQuantity`, `daysLate`, `lastFollowupAt`, `nextFollowupDate`. Filters: `customerId`, `salesExecId`,
`dispatchWarehouseId`, `soType`, `atRiskOnly`, `overdue`, `followupDueToday`. Actions: Log follow-up · Open
SO. Export ⊇ grid (`wht_so_commitment_followups:export`). Empty state: *No commitments at risk.*

### 5.5 WS-305 Dispatch Planning (sales only; purchase counterpart is the WS-294 *Proposals* view)
Grid `wht_so_dispatch_plan` (open schedule lines of every type in the horizon), scope
`WAREHOUSE_TRADE_SO_DISPATCH_PLAN`, sort `e.committed_date ASC`; `grid_preferences` default filters
`dispatchWarehouseId`, `horizonDays`. Tiles: due in horizon, ATP short, dispatch overdue, FIXED (no release
needed), released not shipped — counts. Columns: `soNumber`, `soType`, `customerName`, `itemCode`,
`customerPartNumber`, `committedDate`, `customerRevisedDate`, `openQuantity`, `atpQuantity`, `shortfall`,
`zone`. Filters: `dispatchWarehouseId` (required), `customerId`, `soType`, `horizonDays`, `atRiskOnly`.
Multi-select *Release* with per-line qty (BLANKET / OPEN rows only; FIXED rows show ATP only, `TRD-12`).
Export ⊇ grid. Empty state: *Nothing due in the horizon.*

## 6. Out of scope

| Item | Decision |
|---|---|
| Pick / pack / ship / outward gate pass / challan / e-way bill | core / `warehouse-india` |
| Credit limit, invoice, credit note | refused (FRD §11 R1–R3) |
| Make-to-order production trigger | MFG reads `FORECAST` and `FIRM` demand schedule from core (`OD-32`) |
| EDI schedules | refused (R7); CSV import is v1 |
| A dispatch-release print | refused (§5 M32) |

## 7. Amendments

| Date | Rows | Change | Found by |
|---|---|---|---|
| 2026-10-22 | all | v0 derived | TRADE author |
| 2026-10-22 | all | R29 TS-F1, F2, F6, F7, F10, F11, F12, F14…F20, F24, F25, MA-01…MA-10, MA-14, MA-15, MA-17 and contract quality: rewritten row for row against `TPO` (same ids); registry-exact port commands and keys; `OD-45` (A) with `closeDemand`; `ISSUED` + `ack_status` + re-send; `SO_RELEASE` approval, ceiling consumption, reject-revert, cancel (`unfirmScheduleLine` / `cancelScheduleLine`), close by `releaseRef`; FIXED not released; replacement releases; guard twins; tolerances and `COMPLETE`; `SO_CANCEL`; amendment lock on changed lines; WS-313 and full screen contracts; `TSO-OPEN-02` closed by `POS-T4-07` | R29 |
| 2026-10-22 | `TSO-T4-01`, `TSO-OPEN-01` | Aligned to the updated core registry: create carries `shipToAddressId` (`CN-3`); an OPEN line goes with no schedule and a null quantity (`CN-4`); `CN-1`…`CN-7` resolved | TRADE author |
| 2026-10-23 | every T1, guard, unreachable, T3 and T4 row | `Source` column added, filled from FRD-TRADE §4, so every rule traces to the FR it proves | R30 `CP-FR-008` |
| 2026-10-23 | §0, A15, `TSO-UNR-08`, `TSO-T4-13`, §8 | Lost sale from the sales order: a cancel or short-close for stock calls core `captureLostSale` once per schedule line and request (`D-17` item 4, FR-681) | R30 `CP-GA-003` |
| 2026-10-23 | `TSO-T3-03`, A6 | SO mirror of FRD-TRADE `CN-8`: an SO `TOLERANCE` amendment pushes nothing to core (a core demand line holds no tolerance; `CreateDemandCommand` carries none); auto-close reads trade's amended `under_tolerance_pct` (`TOA-T4-02`). The PO side goes to core as `amendOrder` `lineChanges.overTolerancePct` / `underTolerancePct` (`STO-D25`) | R30 `CP-GB-002` |

## 8. Invariants and scenarios

`WH-SC-555`…`WH-SC-561`, `WH-SC-580`, `WH-SC-584`, `WH-SC-586`…`WH-SC-589`, `WH-SC-591`, `WH-SC-593`,
`WH-SC-594`, `WH-SC-596`, `WH-SC-599` (lost sale; core `WH-SC-283`).

## 9. Open rows

| ID | Question | Status |
|---|---|---|
| TSO-OPEN-01 | Port signatures vs `p8-02` | **Settled (R29):** aligned to FRD-STORES *Port & seam registry*; FRD-TRADE §12c `CN-3`, `CN-4`, `CN-7` resolved by STORES 2026-10-22 (registry R.1, R.2; `STO-D20`); nothing owed |
| TSO-OPEN-02 | Does `getFulfilmentPosition` expose picked-not-shipped per schedule line (needed by `TSO-GRD-09`, `-13`)? | **Settled by STORES:** yes, `POS-T4-07` |
