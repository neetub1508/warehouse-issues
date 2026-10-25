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
`schedule_line_id` (null for an OPEN call-off or a replacement), qty, `unit_price`, `core_schedule_line_id`,
`lost_sale_quantity` (an OPEN call-off has no schedule line, so its capture accumulates here — `TSO-T4-13`, default 0).

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
| TSO-T1-12 | release `RELEASED` | Every core schedule line carrying its `releaseRef` is shipped or cancelled (`demand_order.shipped`, `getFulfilmentPosition`) — a whole-firmed BLANKET line carries it because `firmScheduleLine(…, releaseRef)` re-stamps it at firm (`TSO-T4-02`, R31 F-TR-003) | `CLOSED` | — | system | — | — | — | FR-608 |
| TSO-T1-13 | line `OPEN` / header non-terminal | Short-close line or header | request `SO_SHORT_CLOSE` (seeded zero-level) | `TSO-GRD-13`, `-14` | `:short_close` | — | **yes**, reason code | row action / line action | FR-609 |
| TSO-T1-13a | `SO_SHORT_CLOSE` request approved | Short-close takes effect | line `SHORT_CLOSED`; header `SHORT_CLOSED` when header action | `TSO-GRD-13` re-checked | approver / `SYSTEM` | **`cancelScheduleLine`** for every open schedule line of the line with nothing picked (`FORECAST`, and `FIRM` with nothing picked — core releases its allocation); **`closeScheduleLineShort`** for a `FIRM` line already partly picked or shipped, which closes its unpicked remainder (R31 F-TR-005); header: then **`closeDemand`** (`TSO-T4-06`); open releases closed; RC consumption reduced | — | WS-285 | FR-609 |
| TSO-T1-14 | any active | Log commitment follow-up | follow-up row; `customer_revised_date` | — | `wht_so_commitment_followups:create` | — | no | WS-306, detail | FR-610 |
| TSO-T1-15 | BLANKET non-terminal | Import / enter revised customer schedule | SO amendment `DRAFT` (`TOA-T1-01`, origin `CUSTOMER_SCHEDULE`); a `DRAFT` amendment of the same origin is `CANCELLED` and replaced | `TSO-GRD-19`; no `SUBMITTED` amendment open | `:amend` | changes inside the sales firm zone flagged (`in_firm_zone = true`, counted for `TCE`). Twin: `TPO-T1-11` *Accept changes* drafts the purchase amendment | no | WS-304 *Revise schedule* (CSV dry-run → apply) | FR-611 |
| TSO-T1-16 | SRA `RECEIVED` / `PARTIALLY_RECEIVED` with intent `REPLACE` (the SO is open: `TSR-GRD-03` refuses `REPLACE` on a closed SO, and `TSO-T3-03` waits for the SRA) | Replacement release drafted | release `DRAFT`, `is_replacement`, `source_sra_id` | `TSO-GRD-06` (replacement bound; exempt from the type, validity and schedule gates — any SO type, after `valid_to` too, R31 F-TR-002) | system (`TSR-T4-02`); the planner submits it | lines for the received qty at the original net price, no schedule line. Twin: `TPO-T4-07` reinstates through an amendment (§5 M26) | no | WS-313 | FR-612 |

### 1.3 Guards

| ID | Predicate | Refusal | Source |
|---|---|---|---|
| TSO-GRD-01 | Customer profile exists, not sales-blocked; dispatch site in user scope and allows dispatch | `422 TRADE_CUSTOMER_BLOCKED` | FR-543 |
| TSO-GRD-02 | Type rules as `TPO-GRD-02`: FIXED — qty > 0, Σ schedule = qty; OPEN — qty null, validity, unit price > 0; BLANKET — qty > 0, validity | field `422` | FR-605 |
| TSO-GRD-03 | Every line priced (0 only free-of-charge + reason, never on OPEN); currency = contract / price list currency | field `422` | FR-604 |
| TSO-GRD-04 | BLANKET: Σ schedule = line qty, dates ∈ validity; FIXED: schedule dates ≥ order date | `422 TRADE_SCHEDULE_TOTAL_MISMATCH` / `TRADE_OUTSIDE_VALIDITY` | FR-605 |
| TSO-GRD-05 | Item active and sellable; UoM convertible (`whb_item_uom_conversions`, factor frozen); dispatch site in the user's scope (twin of `TPO-GRD-05`) | field `422` / `TRADE_UOM_NOT_CONVERTIBLE` | FR-605 |
| TSO-GRD-06 | Release: dates ∈ validity; FIXED lines never released; qty ≤ schedule open (qty − released − pending) for BLANKET; OPEN: Σ released + pending ≤ line ceiling and ≤ header ceiling value. A **replacement** release (`is_replacement`) is exempt from **every** one of these — validity, the FIXED-line rule, schedule and ceiling bounds (FRD-TRADE TS-F16, R31 F-TR-002) — and bounded instead by the SRA's received quantity − already replaced; it goes to core as a `FIRM` `releaseSchedule` entry on the SO's line whatever the SO type (`TSO-T4-02`) | `422 TRADE_RELEASE_EXCEEDS_SCHEDULE` / `TRADE_CEILING_EXCEEDED` / `TRADE_OUTSIDE_VALIDITY` / `TRADE_NOT_RELEASABLE` / `TRADE_REPLACEMENT_EXCEEDS_RECEIVED` | FR-607 |
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
| TSO-UNR-03 | Changing an approved SO except by amendment; a credit check blocking release | no edit after approval (`TOA`); credit refused (FRD §11 R1) — no such guard exists · **R32 (`D-20` item 3): the credit half is superseded by `TSO-GRD-25` / `-26` — the credit check is now enforced through the accounting credit service** | FR-553 |
| TSO-UNR-04 | Auto-release of a BLANKET schedule line; an SO invoice | releases are planner acts (twin of `TRD-11`); invoice refused (R2) · **R32 (`D-20` item 4): the invoice stays accounting's, now created from trade's dispatch hand-off (`TSO-T4-16`)** | FR-605 |
| TSO-UNR-05 | Storing shipped quantity in `wht_`; a release blocked by ATP shortfall | `TRD-03`; FR-607: shown, never blocked | FR-607, FR-608 |
| TSO-UNR-06 | Changing `so_type` after submit | not editable | FR-605 |
| TSO-UNR-07 | A trade SO `CLOSED` while its core demand order can still take releases | auto-close and header short-close call `closeDemand` in the same transaction | FR-609 |
| TSO-UNR-08 | A lost sale captured at release, or twice for one cancel / short-close request | a release is never refused for ATP (`TSO-UNR-05`), so nothing is lost there; `TSO-T4-13` runs once in the approving transaction, keyed `<scheduleLineId>:<approvalRequestId>` (OPEN: `<releaseLineId>:<approvalRequestId>`); a dispatch-release cancel captures nothing | FR-681 |

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from | Source |
|---|---|---|---|---|
| TSO-T2-01 | Add / edit | `:create` / `:edit` | `DRAFT`, `REJECTED` | FR-605 |
| TSO-T2-02 | Submit / withdraw | `:submit` | `DRAFT`, `REJECTED` / `SUBMITTED` | FR-551 |
| TSO-T2-03 | Approve | `:approve` (`TAM`) + `warehouse:orders:port` | `SUBMITTED`; `SO_CANCEL` / `SO_SHORT_CLOSE` requests | FR-605 |
| TSO-T2-04 | Send acknowledgement / print | `:issue` / `:view` | `APPROVED`+ | FR-606 |
| TSO-T2-05 | Re-send acknowledgement | `:issue` | `ISSUED` with ack `PENDING` | FR-606 |
| TSO-T2-06 | Dispatch release — create / submit / approve / cancel | `wht_so_dispatch_releases:create` / `:submit` / `:approve` / `:cancel` (+ `warehouse:orders:port` as `TPO-T2-06`) | SO `APPROVED`, `ISSUED`; release per T1 — a replacement release (`TSO-T1-16`) is allowed on any open SO, after validity and on a FIXED SO (`TSO-GRD-06`) | FR-607 |
| TSO-T2-07 | Amend / revise schedule | `:amend` (`TOA`) | `APPROVED`, `ISSUED` | FR-590, FR-611 |
| TSO-T2-08 | Short-close | `:short_close` | non-terminal | FR-609 |
| TSO-T2-09 | Cancel | `:cancel` | non-terminal, `TSO-GRD-09` | FR-609 |
| TSO-T2-10 | Commitment follow-up | `wht_so_commitment_followups:create` | non-terminal | FR-610 |
| TSO-T2-11 | Export | `:export`; `wht_so_dispatch_releases:export`; `wht_so_commitment_followups:export` (auditor: none) | — | FR-616 |
| TSO-T2-12 | Every action in this table, and the auditor | `wht_<table>:<verb>` per FRD-TRADE FR-617 (`view`, `create`, `edit`, `export` + the workflow verbs above); `permission_dependencies` seeded; the auditor bundle holds `:view` only; record scope follows core's company / site grants; a bundle whose action calls a core port is also granted `warehouse:orders:port` in the trade seed | — | FR-617 |

## 3. T3 — Time-driven rules

| ID | Rule | Trigger | Changes | Notified (FRD-TRADE §12b) | Job | Source |
|---|---|---|---|---|---|---|
| TSO-T3-01 | Dispatch due (twin of the release proposal) | open BLANKET / OPEN schedule line with `committed_date − warehouse.trade.sales.dispatch_horizon_days` (default 7) ≤ today | shown on WS-305 (computed) | dispatch planners of the dispatch site, digest `TRADE_DISPATCH_DUE` | `TradeDispatchJob` daily | FR-607 |
| TSO-T3-02 | At risk (twin of expediting) | open line due within `warehouse.trade.sales.at_risk_days` (default 5) and unreleased, or released with ATP short (`TSO-T4-12`) | computed `atRisk` | sales exec + planners, `TRADE_COMMITMENT_AT_RISK` | same | FR-610 |
| TSO-T3-03 | Auto-close | every line `SHORT_CLOSED` or fulfilment `COMPLETE` (shipped ≥ qty × (1 − under tolerance)), no release open, **no SRA of the SO open**; OPEN/BLANKET also when validity ended and nothing open | `CLOSED`; a tolerated `FIRM` remainder is closed by `closeScheduleLineShort` first, then `closeDemand` (`TSO-T4-10`) | sales exec, `TRADE_ORDER_CLOSED` | nightly `TradeSoCloseJob`, calling as trade's **service principal** (`TRD-13`, FRD-STORES R.1 — never as the SO's sales executive; R31 F-TR-012) | FR-609 |
| TSO-T3-04 | Ack not sent (twin of ack overdue) | ack `PENDING` `warehouse.trade.sales.ack_send_alert_days` (default 1) after approval or after the amendment that reset it | none | sales exec, `TRADE_SO_ACK_NOT_SENT` | `TradeDispatchJob` | FR-606 |
| TSO-T3-05 | Validity ending | OPEN/BLANKET `valid_to − 30` | none | sales exec, `TRADE_SO_VALIDITY_ENDING` | `TradeContractJob` | FR-605 |
| TSO-T3-06 | Dispatch overdue (twin of release overdue) | BLANKET / OPEN schedule line unreleased with `committed_date < today` | computed `dispatchOverdue` on WS-305 / WS-306; counted against our own `DELIVERY_OTIF` (`TCE`) | sales exec + planners (in the at-risk digest) | `TradeDispatchJob` | FR-610 |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in | Source |
|---|---|---|---|---|
| TSO-T4-01 | Approved (every type) | `WhDemandOrderPort.createDemand(CreateDemandCommand{ envelope(sourceModule 'warehouse-trade', idempotencyKey 'WHT_SALES_ORDER:<id>:DEMAND_CREATE:1', actingUserId = last approver), sourceDocumentType 'WHT_SALES_ORDER', sourceDocumentId, sourceDocumentRef <so_number>, demandType 'SALES', customerCounterpartyId, warehouseId = dispatch site, ownerId, salesOrderRef <so_number>, customerPoRef, customerPoDate, fulfilmentPolicy, shipToAddressId = `ship_to_address_id`, lines[ lineRef <line_no>, itemId, uomCode, orderedQuantity (ignored for a schedule-driven line; OPEN: null with no schedule, which core makes schedule-driven — `CN-4`), unitPrice, requiredDate, schedule[ kind FIXED→FIRM · BLANKET→FORECAST (OPEN: none), requestedDate = committed date, quantity, releaseRef (FIXED: the SO number; BLANKET: `<so_number>-S<schedule no>`) ] ] })` → one core demand order, schedule-driven, its header following `OD-45` (A) (`POS-T1-12b`); ids stored. Ship-to reaches core on the create, snapshotted into `ship_to_*` (`POS-GRD-16`; FRD-TRADE §12c `CN-3`, resolved) | approval transaction | FR-605 |
| TSO-T4-02 | Dispatch release approved | a whole BLANKET schedule line → `firmScheduleLine(DemandScheduleLineCommand{ scheduleLineId, releaseRef <release no> })` — the optional `releaseRef` re-stamps the firmed core line from `<so_number>-S<n>` to the release number, so `TSO-T1-12` closes the release by it (FRD-STORES R.2, R31 F-TR-003) (key `…:DEMAND_FIRM:<release no>-<schedule no>`); an OPEN call-off, a split BLANKET line or a replacement → `releaseSchedule(ReleaseDemandScheduleCommand{ demandOrderId, releaseRef <release no>, entries[ demandLineId, FIRM, requestedDate = planned dispatch date, quantity ] })` (key `…:DEMAND_RELEASE:<release no>`) — for a split BLANKET line the `FORECAST` line is reduced to the remainder by `amendDemand` (key `…:DEMAND_AMEND:<release no>`); the core `FIRM` line ids stored. Core `FORECAST` lines stay equal to the unreleased schedule, which MRP reads and which never reserve (`POS-UNR-03`, closes `OD-32`) | release approval transaction | FR-607 |
| TSO-T4-03 | Any port call refused | trade transaction rolls back; core error relayed (twin of `TPO-T4-03`) | port adapter | FR-618 |
| TSO-T4-04 | Detail / grid read | allocated, picked, shipped, delivered, backordered quantities per line and schedule line (`getFulfilmentPosition`, `POS-T4-07`), shipments, outward gate passes (`p8-03`), challans / e-way bills (india, when installed — read through core references only) by `core_demand_order_id`; fulfilment `COMPLETE` when every line shipped ≥ qty × (1 − under tolerance) or short-closed | `SalesOrderQueryService` | FR-608 |
| TSO-T4-05 | Ack sent / re-sent | trade only — the acknowledgement is our print; nothing goes to core (twin of `TPO-T4-05`) | ack transaction | FR-606 |
| TSO-T4-06 | Short-close / cancel approved | `cancelScheduleLine(DemandScheduleLineCommand{ scheduleLineId, reasonCodeId })` per open schedule line with nothing picked; `closeScheduleLineShort(scheduleLineId, reasonCodeId)` per `FIRM` line partly picked or shipped — core closes the unpicked remainder, releases its reservation and writes `cancelled_quantity` (FRD-STORES R.2, R31 F-TR-005); `reasonCodeId` is a `TRADE_ORDER_CLOSE`-context `whb_reason_codes` id (FR-546, R31 F-TR-007); header: `closeDemand(CloseDemandCommand)`; cancel: `cancelDemand(CancelDemandCommand)`; keys `WHT_SALES_ORDER:<soId>:<op>:<request id>-<n>`; RC consumption reduced | same transaction | FR-609 |
| TSO-T4-07 | SRA received with intent `REPLACE` | `TSO-T1-16` drafts the replacement release; the SO stays open (`TSO-T3-03`); on a `SHORT_CLOSED` / `CANCELLED` SO nothing is drafted and the SRA asks for a declined reason (`TSR-T1-05`) — twin of `TPO-T4-07` | SRA service | FR-612 |
| TSO-T4-08 | Any write | `whb_audit_events` | services | FR-540 |
| TSO-T4-09 | Dispatch release cancelled after approval | `unfirmScheduleLine` (key `…:DEMAND_UNFIRM:<release no>-X<n>`) or `cancelScheduleLine` (key `…:DEMAND_CANCEL_SCHEDULE:<release no>-X<n>`) + `amendDemand` restoring a split `FORECAST` (key `…:DEMAND_AMEND:<release no>-X`) | release cancel transaction | FR-607 |
| TSO-T4-10 | Auto-close | each tolerated `FIRM` remainder (shipped within under-tolerance, e.g. 97 of 100) → `closeScheduleLineShort(scheduleLineId, reasonCodeId = AUTO_CLOSE)` (key `…:DEMAND_CLOSE_SCHEDULE_SHORT:AUTO-<schedule no>`), so no allocatable or backordered remainder stays in core (R31 F-TR-006); then `closeDemand(CloseDemandCommand{ demandOrderId, reasonCodeId = AUTO_CLOSE })`, key `…:DEMAND_CLOSE:AUTO`, in the same transaction, as trade's service principal (`TRD-13`) — `AUTO_CLOSE` is the `TRADE_ORDER_CLOSE` reason trade seeds (FR-546) — the core order then follows its ordinary ladder (`POS-T1-12a`); nothing unshipped ⇒ `SHIPPED` at once | close job transaction | FR-609 |
| TSO-T4-11 | Core events for this SO (`demand_order.shipped` per `release_ref`, `demand_order.amended`, `demand_order.cancelled`) | release close (`TSO-T1-12`), commitments refresh; a core-side cancel the trade SO did not cause is logged for the sales executive | outbox subscriber | FR-608 |
| TSO-T4-12 | WS-305 / at-risk read | `WhAvailableToPromiseQuery.atp(AtpQuery{ warehouseId = dispatch site, ownerId, itemIds, horizonEnd })` → `availableNow`, open reservations, firm scheduled receipts by date; shortfall = due open − (`availableNow` + receipts before the date), computed in the backend, never a reservation (`POS-T4-08`) | `DispatchPlanningQueryService` | FR-607 |
| TSO-T4-13 | `SO_CANCEL` (`TSO-T1-05a`) or `SO_SHORT_CLOSE` (`TSO-T1-13a`) approved with a reason in `warehouse.trade.sales.lost_sale_reason_codes` — **not** a dispatch-release cancel (`TSO-T1-10c`), whose quantity returns to the schedule and is not lost (R31 F-TR-008) | per schedule line losing quantity — for an OPEN line, per released call-off **release line** losing its unshipped quantity (an OPEN line has no schedule line): core **`WhLostSalePort.captureLostSale`**`(envelope(key 'WHT_SALES_ORDER:<soId>:LOST_SALE_CAPTURE:<line id>-<approvalRequestId>', actingUserId = the `TRD-13` principal — the last approver, or the submitter when the seeded zero-level rule approved it as `SYSTEM`), CaptureLostSaleCommand{ warehouseId = dispatch site, itemId, ownerId = house owner, requestedQuantity = the cancelled / short-closed base quantity, lostSaleReasonCodeId = `TRADE_STOCK_NOT_AVAILABLE`, sourceDocumentType `TRADE_SO_SCHEDULE_LINE` (OPEN: `TRADE_SO_RELEASE_LINE`), sourceDocumentId = the schedule line id (OPEN: the release line id), sourceDocumentRef `<so_number>` })` (`POS-T1-40`: core records source type / id from these and the source system from the envelope) after the short-close's `cancelScheduleLine` / `closeScheduleLineShort`, or after the cancel's `cancelDemand` (`TSO-T4-06`); `lost_sale_quantity` += that quantity on the schedule line (OPEN: on the release line). The *short for ATP* case is this row: the planner releases what ATP allows (`TSO-T4-12`) and short-closes the rest with `NO_STOCK`. A core refusal rolls the approval back (`TSO-T4-03`) | same transaction | FR-681 |

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

## R32 additions (PRD 2026-10-24, `D-20`)

Rows added by the R32 fold (FRD-TRADE §4.15). Numbers continue each kind's sequence; where a number exists on one side of the purchase / sales mirror only, the asymmetry is stated in FRD-TRADE §5 rows M35…M40.

| ID | Kind | Rule | Refusal / effect | Source |
|---|---|---|---|---|
| TSO-GRD-20 | guard | `warehouse.trade.sales.so_requires_won_quotation` = true (default): SO only from a won quotation line or a sales rate contract | `422 TRADE_SO_NEEDS_WON_QUOTATION` | FR-752 |
| TSO-GRD-21 | guard | Line from a quotation keeps `source_quotation_line_id`, `quoted_unit_price`; a different price / discount sets `price_differs_from_quotation`; customer PO copy (`WHT_SALES_ORDER`, `CUSTOMER_PO`) required when the profile's `customer_po_required`; ATP shown at submit and approval, never blocking | `422 TRADE_CUSTOMER_PO_COPY_REQUIRED` | FR-752 |
| TSO-GRD-22 | guard | `bill_to_address_id` (role `BILL_TO`) required; `dispatch_mode_code` (`trade_dispatch_mode`); `CUSTOM` line `drawing_no` + `drawing_revision` frozen at approval | field `422` | FR-753 |
| TSO-T4-14 | effect | `warehouse.trade.sales.reservation_timing` = `AT_APPROVAL` (default): approval / release asks core to allocate every `FIRM` line now (`allocateImmediately` on `createDemand`, `releaseSchedule` and `firmScheduleLine` — a whole-line BLANKET release included; `CN-20`, carrier `P8-26`); shortfall shown; `FORECAST` never reserves | — | FR-754 |
| TSO-GRD-23 | guard | Dispatch release with mode `TRANSPORTER`: **transporter** and planned date required at approval; **vehicle no and LR no / date** required before gate-out, through trade's answer to core's gate-out guard (`CN-21`), which also carries details entered after release to the core shipment; details known at release go on the release command (`CN-20`, every command incl. `firmScheduleLine`); `SO_RELEASE` rule per `warehouse.trade.sales.dispatch_release_approval` (`ONE_LEVEL` → role `trade_dispatch_incharge`) | `422 TRADE_DISPATCH_TRANSPORT_REQUIRED {field}` (at approval for the transporter; at gate-out for vehicle / LR) | FR-755 |
| TSO-GRD-24 | guard | With `warehouse.trade.sales.dispatch_checklist_required` (true): every required checklist item of the covering release line done (`wht_so_dispatch_release_checks`) before core confirms the shipment — trade's answer to core's **pre-ship guard** `WhPreShipGuard.check` (`CN-22`, carrier `P8-26`) at pack confirmation / shipment posting; `DISPATCH_LOADING_LIST` print with core-picked serials | `422 TRADE_DISPATCH_CHECKLIST_INCOMPLETE {releaseLineId, item}` (returned by the guard; core refuses the ship step) | FR-756 |
| TSO-T4-15 | effect | SO line tax rows (`wht_so_line_taxes`, typed heads incl. `UTGST`) from `WhTaxPreviewProvider` (`CN-16`, `P8-26`; accounting's tax determination through the adapter, `D-21` item 1) with bill-to + ship-to states (IGST Act s.10(1)(b) decided by the provider), supply kind `DOMESTIC` / `EXPORT` / `SEZ` (zero-rated per the provider), effective document date; an OPEN line on its unit price, recomputed per release; frozen at approval; printed on the SO acknowledgement; no provider → *Taxes extra as applicable* | `422 TRADE_TAX_CLASSIFICATION_MISSING {lineNo}`; `422 TRADE_PLACE_OF_SUPPLY_UNRESOLVED` | FR-761, FR-762 |
| TSO-T1-17 | transition | *Share* the SO acknowledgement by e-mail / WhatsApp; sets `ISSUED`, `ack_status = SENT` as print does | `422 TRADE_SHARE_DOCUMENT_NOT_APPROVED` | FR-763 |
| TSO-GRD-25 | guard | Credit check through the one core SPI `WhbCustomerCreditProvider.check(company, customer, candidate, excludeDocumentRef)` (`CN-17`, carrier `P8-26`; check-only accounting entry point, `D-21` item 4) at `SO_SUBMIT` (shown), `SO_APPROVAL` and `DISPATCH_RELEASE` (per `warehouse.trade.sales.credit_check_points`, enforced before any port call). Non-overlapping buckets (receivables, accounting drafts, accounting open orders, trade open orders, shipped-not-yet-drafted by shipment id, minus advances); `excludeDocumentRef` takes the document out of the trade buckets. **Candidate:** SO approval — FIXED all lines, BLANKET `FIRM` lines, OPEN 0, an amendment its increase; release — the release value, excluded from the trade open-order bucket; gross with tax on, else net. A release of an `is_replacement` line is never checked. **Mode mapping:** `OFF` → `PASS`; `WARN` → `WARN`; `BLOCK` / credit hold → `BLOCK`; `APPROVE` → `NEEDS_OVERRIDE` (answered only by `TSO-T1-18`). Result row in `wht_credit_check_results` written in its own committed transaction, uk(SO, version, release, point, attempt), so a refusal keeps its row. **Supersedes `TSO-UNR-03`'s credit half** | `422 TRADE_CREDIT_LIMIT_EXCEEDED {limit, exposure, candidate}`; `503 TRADE_CREDIT_CHECK_UNAVAILABLE` when `warehouse.trade.sales.credit_check_unavailable` = `BLOCK` | FR-765 |
| TSO-T1-18 | transition | `SO_CREDIT_OVERRIDE` request from a blocked SO / release with reason (`trade_credit_override_reason` + note); approval covers that SO version or release up to its amount; audited `TRADE_CREDIT_OVERRIDDEN` | `422 TRADE_OVERRIDE_REASON_REQUIRED` | FR-766 |
| TSO-GRD-26 | guard | Overdue (accounting's ageing in the `CN-17` answer) beyond `warehouse.trade.sales.overdue_grace_days` (0) raises the decision to accounting's mode refusal at SO approval (`OFF` → no check; trade owns no credit policy); advance terms (`advance_required_pct` / `_amount`) vs the SO-referenced advances in the answer (or recorded fields without accounting) block dispatch release approval (not for an `is_replacement` release); both overridable by `TSO-T1-18` | `422 TRADE_OVERDUE_OUTSTANDING {amount, days}`; `422 TRADE_ADVANCE_NOT_RECEIVED {required, received}` | FR-767 |
| TSO-T4-16 | effect | Core is the one producer (`D-21` item 2): it emits one shipment-level `INVOICE_REQUEST` per shipment id (every despatch of a BLANKET / OPEN SO included, whatever the demand header status) and asks trade's `WhAccountingEnvelopeEnricher` (`CN-18`, `P8-26`): SO price, discount, typed tax-head rows, HSN, customer PO, e-way ref, shipped unit serials and bound part serials (`UnitRegistryPort.findByUnitSerial`); recorded as a `SALES_INVOICE` enrichment row, uk(company, kind, `source_event_id`) — a repeat returns the stored answer; trade emits no invoice kind. A shipment of an `is_replacement` release → `NOT_INVOICEABLE {REPLACEMENT}`, core requests no invoice. **Supersedes `TSO-UNR-04`'s invoice half: the invoice is accounting's, created from core's request** | `REJECTED` acknowledgement shows accounting's reason; core re-hands, the enricher answers the same | FR-773 |
| TSO-T4-17 | effect | Core `INVOICE_ACKNOWLEDGED` (shipment → invoice no / date, per-line quantity, serial list; `D-21` item 3) → `wht_so_line_billings`, uk(proposal, SO line, accounting document no) — a re-sent acknowledgement writes nothing; line `billing_status` derived from billed vs shipped with replacement shipments excluded on both sides; `warehouse.trade.sales.close_rule` = `SHIPPED_AND_INVOICED` adds billed = shipped to auto-close (`TSO-T3-03`). The same event marks MFG units `SOLD` (MFG's consumer; trade sends nothing) | — | FR-774 |
| TSO-T4-18 | effect | Display status `APPROVED` → `IN_PRODUCTION` → `PARTLY_DISPATCHED` → `FULLY_DISPATCHED` → `INVOICED` → `CLOSED`, derived from core production progress (`CN-19`, declared by `P8-26`, MFG implements), shipments and billings; ordered basis FIXED line qty / BLANKET `FIRM` qty / OPEN released qty; replacement shipments are not counted as invoiceable; stored status unchanged; WS-315 order-book row per line | — | FR-776 |
| TSO-GRD-27 | guard | One dispatch authorisation for every SO type: with `warehouse.trade.sales.fixed_so_dispatch_release_required` (true) a FIXED SO (lines `FIRM` at approval) ships only through `DISPATCH_ONLY` releases (no core command; `TSO-GRD-23`, `-24`, `-25`, `-26` and the `SO_RELEASE` approval apply as to any release); trade's answer to core's pre-ship guard (`CN-22`, `P8-26`) refuses a shipment of a FIXED trade line beyond the quantity of its `APPROVED` releases | `409 TRADE_DISPATCH_NOT_AUTHORISED {demandLineId}` | FR-755 |
| TSO-GRD-28 | guard | Gate-out on invoice (CGST Act s.31(1)(a); `D-21` item 3): with an accounting handover target configured, trade's answer to core's gate-out guard (`CN-21`, `P8-26`) refuses gate-out of an invoiceable trade shipment until `INVOICE_ACKNOWLEDGED` for its shipment id has arrived; without a target, and for a replacement shipment, the gate pass is printed on a delivery-challan basis | `409 TRADE_INVOICE_NOT_ACKNOWLEDGED {shipmentId}` | FR-773 |

## 6. Out of scope

| Item | Decision |
|---|---|
| Pick / pack / ship / outward gate pass / challan / e-way bill | core / `warehouse-india` |
| Issuing the invoice or credit note, numbering it, posting receivables; credit limits and exposure | accounting — trade checks credit through `WhbCustomerCreditProvider` (`TSO-GRD-25`, superseding FRD §11 R1) and enriches core's `INVOICE_REQUEST` / `CREDIT_NOTE_PROPOSAL` (`TSO-T4-16`, `TSR-T4-06`, superseding R2 / R3 in part); it never issues either document (R32 F-R32TR-033) |
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
| 2026-10-23 | §0 fields, `TSO-T1-12`, `-13a`, `-16`, `-GRD-06`, `-T2-06`, `-T3-03`, `-T4-02`, `-T4-06`, `-T4-10`, `-T4-13`, `-UNR-08`, every T2 row | R31: replacement exempt from type / validity / schedule gates (F-TR-002); `firmScheduleLine(…, releaseRef)` (F-TR-003, `CN-9`); `closeScheduleLineShort` for partly picked lines and tolerated remainders (F-TR-005, F-TR-006, `CN-10`); port reasons `whb_reason_codes` (F-TR-007); lost-sale trigger, OPEN release line, principal (F-TR-008); `WhLostSalePort` (F-TR-011, `CN-11`); service principal (F-TR-012); T2 Source FRs (F-TR-019) | R31 |
| 2026-10-24 | every row citing a core event | P8 decision record `EV-1` (DECISIONS `D-19`): every outbox event code renamed to the dotted `whb_event_types` vocabulary of registry R.4 (PC-42) — e.g. `purchase_order.amended`, `demand_order.shipped`, `rma.matched`, `supplier_return.dispatched`; no behaviour change | decision record P8 wave 1/2 |
| 2026-10-25 | `TSO-GRD-20`, `TSO-GRD-21`, `TSO-GRD-22`, `TSO-T4-14`, `TSO-GRD-23`, `TSO-GRD-24`, `TSO-T4-15`, `TSO-T1-17`, `TSO-GRD-25`, `TSO-T1-18`, `TSO-GRD-26`, `TSO-T4-16`, `TSO-T4-17`, `TSO-T4-18` (new, *R32 additions*) | R32 fold of the client PRD (`D-20`): acceptance checks, bill-to / dispatch mode / frozen drawing revision, reservation at approval, dispatch transport + approval + checklist, GST, share, credit / overdue / advance checks and override, invoice hand-off, billing status + close on invoice, display status (`TSO-UNR-03`, `-04` superseded in part) | R32 / `D-20` |
| 2026-10-25 | `TSO-T4-14`, `TSO-GRD-23`…`-26`, `TSO-T4-15`…`-18`, `TSO-GRD-27`, `TSO-GRD-28` (new), §6 | R32-fix (`D-21` items 1–5): tax from accounting's tax determination via `CN-16` with bill-to / ship-to and supply kind; one credit SPI `WhbCustomerCreditProvider` with non-overlapping buckets, incremental candidate, mode mapping, committed result rows; FIXED SOs dispatched through `DISPATCH_ONLY` releases; checklist and FIXED veto via core's pre-ship guard (`CN-22`); transporter at approval, vehicle / LR at gate-out (`CN-21`); `allocateImmediately` + transport on `firmScheduleLine`; core `INVOICE_REQUEST` per shipment enriched by trade, replacements excluded, `INVOICE_ACKNOWLEDGED` billing with an idempotency key, gate-out on invoice; stale §6 row amended. All carriers core `P8-26` | R32 review F-R32TR-002, -007…-012, -021…-023, -025, -026, -028, -029, -033, -034 |

## 8. Invariants and scenarios

`WH-SC-555`…`WH-SC-561`, `WH-SC-580`, `WH-SC-584`, `WH-SC-586`…`WH-SC-589`, `WH-SC-591`, `WH-SC-593`,
`WH-SC-594`, `WH-SC-596`, `WH-SC-599` (lost sale; core `WH-SC-283`).

## 9. Open rows

| ID | Question | Status |
|---|---|---|
| TSO-OPEN-01 | Port signatures vs `p8-02` | **Settled (R29):** aligned to FRD-STORES *Port & seam registry*; FRD-TRADE §12c `CN-3`, `CN-4`, `CN-7` resolved by STORES 2026-10-22 (registry R.1, R.2; `STO-D20`); nothing owed |
| TSO-OPEN-02 | Does `getFulfilmentPosition` expose picked-not-shipped per schedule line (needed by `TSO-GRD-09`, `-13`)? | **Settled by STORES:** yes, `POS-T4-07` |
