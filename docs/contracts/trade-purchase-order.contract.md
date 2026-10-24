# Functional Contract — Purchase order (FIXED / OPEN / BLANKET), schedules, releases, acknowledgement, expediting, short-close and the hand-off to stores

> **What this is.** The functional truth for the commercial purchase order in `warehouse-trade`: its
> three types, the delivery schedule, releases and their hand-off to the core PO through the `p8-01`
> port, the supplier acknowledgement, expediting and short-close. What happens at the gate, the GRN and
> QC is core's ([receipt-qc-putaway](receipt-qc-putaway.contract.md) and the STORES contracts); this
> contract only **reads** it. Approval cites `TAM-*`; amendment is
> [trade-order-amendment](trade-order-amendment.contract.md); pricing is `TRC-T4-02`.
>
> **Sales twin.** [trade-sales-order](trade-sales-order.contract.md), **row for row**: every `TPO-*` id has a
> `TSO-*` row with the same number — the same behaviour, a stated difference, or a written refusal
> (FRD-TRADE §5 M16–M25).
>
> **Port names.** Every port method, command field, operation key, event and refusal code below is
> FRD-STORES *"Port & seam registry (authoritative)"*'s; trade's keys, principal and grants are FRD-TRADE §12a.
>
> **Status.** Derived 2026-10-22 (v0), R29 folded (v1). No code exists yet.

---

## 0. Identity

| | |
|---|---|
| **Workflow** | Draft (manual, from PR workbench, from award) → submit → approve (core PO via port, every type) → issue to supplier → acknowledgement → releases (OPEN call-offs, BLANKET schedule releases; FIXED needs none, `TRD-12`) → execution in core (gate entry, GRN + bill, QC, MRN) → complete / short-close → closed (core PO closed with it); cancel before execution; expediting throughout |
| **Module** | `warehouse-trade`; core `warehouse` through `WhPurchaseOrderPort` (`ai.warehouse.port.purchase`; [po-schedule-port](po-schedule-port.contract.md) `POS-*`) and read-only queries |
| **Domain baseline** | FRD-TRADE FR-575…FR-589, FR-682…FR-689 (subcontract service PO, `D-18` item 3, §1.5), FR-542 (MSME), FR-544 (AVL), FR-585, `TRD-01`, `TRD-02` (separate tables per side, same shape — the SO twin is `trade-sales-order`), `TRD-03`, `TRD-11`…`-13`, `OD-30`, `OD-38`, `OD-39` · R27 `RM-003`…`RM-010` · `FR-123` layered truth |
| **Owning task bodies** | `issues/p9-07.md` (types, schedule, releases, port, cancel) · `issues/p9-10.md` (acknowledgement, expediting, short-close, auto-close) |
| **Primary tables** | `wht_purchase_orders`, `wht_purchase_order_lines`, `wht_po_schedule_lines`, `wht_po_releases`, `wht_po_release_lines`, `wht_po_charges` (`V550060`); `wht_po_acknowledgements`, `wht_po_ack_lines`, `wht_po_followups` (`V550090`) |
| **Permission resources** | `wht_purchase_orders:view/create/edit/export/submit/approve/cancel/issue/acknowledge/short_close/amend` · `wht_po_releases:view/create/submit/approve/cancel/export` · `wht_po_followups:view/create/export`. The buyer and purchase-approver bundles also hold core **`warehouse:orders:port`** (`TRD-13`, seeded in `V551070`) |
| **Routes** | WS-292 `/warehouse/trade/purchase/orders`, WS-293 `/[id]`, WS-294 `/releases`, WS-295 `/expediting` · mobile: none |
| **Contract status / version** | `derived` · `v1 — 2026-10-22` |

**Fields.** Header: `po_number` (trade series `PO` / `PA`, issued at submit; printed to the supplier and stored on the
core PO as `source_document_ref`, `OD-30`), `po_type` (`FIXED`/`OPEN`/`BLANKET`), `version_no` (1 at approval), company,
`supplier_counterparty_id`, `buyer_id`, `order_date`, `warehouse_id` (deliver-to site), `deliver_to_location_id`,
`currency_code`, `payment_terms_code` + `payment_terms_days`, `delivery_terms_code`, `freight_terms_code`,
`rate_contract_id`, `comparative_statement_id`, `valid_from`/`valid_to` (OPEN/BLANKET), `receipt_cutoff_date`
(OPEN/BLANKET, optional, ≥ `valid_to`), `ceiling_value` (OPEN; null ⇒ `open_unbounded`), `price_basis`
(`AGREEMENT`/`AT_RELEASE`), `terms_template_version_id`, `msme_acknowledged` + by/at, `status`, `core_po_id` ↓
`wh_purchase_orders` (one core PO per trade PO, every type), `issued_at`, `ack_status`, `closed_at`,
`short_close_reason_code`, `po_purpose` (`STOCK` / `SUBCONTRACT`, FR-682). Line: `line_no`, `line_kind` (`STOCK` / `SUBCONTRACT_SERVICE`), `subcontract_order_id` (bare UUID of `whm_production_orders.id`, no FK) + `subcontract_order_ref`, item, `supplier_part_number`, description, `uom_code`,
`conversion_factor_used`, `quantity` (FIXED/BLANKET > 0; OPEN null), `ceiling_quantity` (OPEN line, optional),
`unit_price`, `discount_percent`, `net_price` (computed in backend), `price_source`, `rate_contract_line_id`,
`over_tolerance_pct`, `under_tolerance_pct`, `tax_classification_code` (recorded), `is_free_of_charge` (FIXED /
BLANKET only), `line_status` (`OPEN`/`SHORT_CLOSED`/`CANCELLED`), `replacement_pending_quantity`, `core_po_line_id`.
Schedule line: `line_id`, `schedule_no`, `delivery_date`, `quantity`, `zone` (`FIRM`/`TENTATIVE`, derived from
`warehouse.trade.firm_zone_days` at read, frozen when released), `released_quantity`, `pending_release_quantity`
(in submitted releases), `release_status` (`PLANNED`/`PROPOSED`/`PARTIALLY_RELEASED`/`RELEASED`/`CANCELLED`; a FIXED
schedule line is `RELEASED` at approval), `core_schedule_line_id`, `supplier_confirmed_date`,
`supplier_confirmed_quantity`, `supplier_promised_date` (expediting). Release: `release_number` (`<po_number>-Rnn`,
per-order counter, at submit), `release_date`, `status`, `approval_request_id`, `cancel_reason_code`; release
line: `po_line_id`, `schedule_line_id` (BLANKET) or null (OPEN call-off), qty, delivery date, `unit_price` (by
`price_basis`), `core_schedule_line_id` (the core `FIRM` line, `releaseRef` = release number).

### Acceptance checks

| # | Expects | Delivered by |
|---|---|---|
| A1 | Approval of every type creates one core PO in the approval transaction; a port refusal rolls back (`WH-SC-524`, `-525`, `-568`) | `TPO-T1-04`, `TPO-T4-01`, `-03` |
| A2 | Idempotent approval (`WH-SC-526`) | `TPO-GRD-12` |
| A3 | OPEN call-offs within ceiling (pending included) and validity; receipt after validity until the cut-off (`WH-SC-527`, `-528`, `-567`, `-572`) | `TPO-T1-08`, `TPO-GRD-06`, `-07`, `-16` |
| A4 | BLANKET schedule sums and validity; proposals never auto-release; partial release (`WH-SC-529`…`-531`) | `TPO-GRD-04`, `TPO-T3-01`, `TPO-T1-09` |
| A5 | Receipts, bills, QC read from core; fulfilment derived (`WH-SC-532`) | `TPO-T4-04` |
| A6 | Tolerance suggests short-close; short-close via port (`WH-SC-533`, `-539`) | `TPO-T1-13`, `TPO-T4-06` |
| A7 | Cancel only before execution and through `PO_CANCEL`; core cannot edit trade POs (`WH-SC-534`, `-535`, `-576`) | `TPO-T1-05`, `TPO-GRD-09`, `TPO-UNR-02` |
| A8 | Supplier blocked: no new releases (`WH-SC-536`) | `TPO-GRD-08` |
| A9 | Acknowledgement with changes drafts an amendment; agreed date unchanged (`WH-SC-537`) | `TPO-T1-11` |
| A10 | Expediting due/overdue in site timezone, FIXED lines included, promised date separate (`WH-SC-538`, `-579`) | `TPO-T3-02`, `-06` |
| A11 | Auto-close closes the core PO too, and waits for QC holds and supplier returns (`WH-SC-540`, `-577`) | `TPO-T3-03`, `TPO-T4-10` |
| A12 | A release can be cancelled, a rejected one gives its quantity back, and a release closes by its own core lines (`WH-SC-567`) | `TPO-T1-10a`…`-10c`, `-12` |
| A13 | `AT_RELEASE` prices reach core per release (`WH-SC-517`, `-571`) | `TPO-T4-02`, `TRC-T4-03` |
| A14 | A subcontract service PO links one MFG subcontract order per line through core, creates no core PO, and lands its processing charge on the processed item by service confirmation (`D-18` item 3; `WH-SC-700`…`707`, range `WH-SC-700`…`719` allocated in `DECISIONS.md` §6) | §1.5, `TPO-T4-13`, `-14` |

## 1. T1 — State machine

### 1.1 Status inventory

| Entity | Status | Reachable via | Exits via | Kind |
|---|---|---|---|---|
| PO | `DRAFT` | `-01`, award, PR workbench, return | `-02`, `-05` | initial |
| PO | `SUBMITTED` | `-02` | `TAM`, `-03` | active |
| PO | `REJECTED` | `TAM` | edit → `DRAFT` | active |
| PO | `APPROVED` | `-04` | `-06`, `-05`, `-08`/`-09`, `-13` | active |
| PO | `ISSUED` | `-06` | `-11`, releases, `-13`, `-05` | active |
| PO | `ACKNOWLEDGED` | `-11` (`ACCEPTED`) | releases, `-13`, `-05` | active |
| PO | `CLOSED` | `TPO-T3-03` | none | terminal |
| PO | `SHORT_CLOSED` | `-13a` header | none | terminal |
| PO | `CANCELLED` | `-05`, `-05a` | none | terminal |
| PO | *fulfilment* `NOT_STARTED` / `PARTIAL` / `COMPLETE`; *validity* `EXPIRED` (OPEN/BLANKET) | **derived on read** (`TPO-T4-04`) | — | derived |
| Release | `DRAFT` | `-08`, `-09`, return | `-08`/`-09` submit, `-10b` | initial |
| Release | `SUBMITTED` | `-08`, `-09` | `-10`, `-10a`, `-10b` (withdraw) | active |
| Release | `RELEASED` | `-10` | `-10c`, `-12` | active |
| Release | `REJECTED` | `-10a` | edit → `DRAFT`, `-10b` | active |
| Release | `CANCELLED` | `-10b`, `-10c` | none | terminal |
| Release | `CLOSED` | `-12` | none | terminal |
| Ack | `PENDING` → `ACCEPTED` / `ACCEPTED_WITH_CHANGES` / `REJECTED`; reset to `PENDING` by an approved amendment | `-06`, `-11`, `TOA-T4-03` | — | — |

### 1.2 Transitions

| ID | From | Action | To | Guard | Actor | Side effects | Comment | UI | Source |
|---|---|---|---|---|---|---|---|---|---|
| TPO-T1-01 | — | Create (manual / from PR lines / from award) | `DRAFT` | — | `:create` (award target: maker = the statement's preparer, `TRA-T4-03`) | prices resolved (`TRC-T4-02`); PR allocations | no | WS-292 Add (type picker first) | FR-575, FR-576 |
| TPO-T1-02 | `DRAFT`, `REJECTED` | Submit | `SUBMITTED` | `TPO-GRD-01`…`-05`, `-08`, `-10` | `:submit` | number (series `PO` for FIXED / OPEN, `PA` for BLANKET — `OD-30`); `TAM-T1-03` doc `PO`, value Σ net × qty (FIXED/BLANKET) or the header ceiling value (OPEN; when null, Σ line ceiling qty × price, or 0, with condition **`open_unbounded`**), conditions `manual_rate`, `non_l1_award` inherited | no | Submit | FR-575 |
| TPO-T1-03 | `SUBMITTED` | Withdraw | `DRAFT` | `TAM-T1-09` | maker | — | no | Withdraw | FR-551 |
| TPO-T1-04 | `SUBMITTED` | Approved (last level) | `APPROVED` | `TPO-GRD-11`, `-12` | approver (holds `warehouse:orders:port`) | **`WhPurchaseOrderPort.createOrder`** (`POS-T1-05`) in the same transaction (`TPO-T4-01`) — every type; `version_no = 1` snapshot (`TOA-T4-01`); RC consumption (`TRC-T4-01`) for FIXED and BLANKET lines; FIXED schedule lines → `RELEASED` | — | WS-285 | FR-577 |
| TPO-T1-04a | `SUBMITTED` | Rejected / returned | `REJECTED` / `DRAFT` | `TAM` | approver | maker notified | **yes** | WS-285 | FR-551 |
| TPO-T1-05 | `DRAFT`; `SUBMITTED` (withdraw first); `APPROVED`, `ISSUED`, `ACKNOWLEDGED` | Cancel | `DRAFT`/`SUBMITTED`: `CANCELLED` at once; after approval: request `PO_CANCEL` opened (seeded zero-level, an install may add levels) | `TPO-GRD-09`, `-14` (header) | `:cancel` | after approval → `-05a` on approval | **yes**, reason code | row action | FR-583 |
| TPO-T1-05a | `PO_CANCEL` request approved | Cancel takes effect | `CANCELLED` | `TPO-GRD-09` re-checked | approver / `SYSTEM` | **`cancelOrder`** (`TPO-T4-06`); PR allocations released; RC consumption reversed; open releases `CANCELLED` | — | WS-285 | FR-583 |
| TPO-T1-06 | `APPROVED` | Issue to supplier | `ISSUED` | template exists | `:issue` | print job `PURCHASE_ORDER` (version, T&C); `issued_at`; ack `PENDING` | no | Issue / Print | FR-576, FR-615 |
| TPO-T1-07 | any non-terminal | Reprint | — | — | `:view` | reprint flagged | no | Print | FR-615 |
| TPO-T1-08 | OPEN, `APPROVED`/`ISSUED`/`ACKNOWLEDGED` | Create and submit a call-off release | release `DRAFT` → `SUBMITTED` | `TPO-GRD-06`, `-07`, `-08`, `-14` | `wht_po_releases:create` / `:submit` | number `<po>-Rnn`; price by `price_basis` (`TRC-T4-03`); `TAM` doc `PO_RELEASE` (seeded zero-level `EXACT` rule; `open_unbounded` / `release_price_manual` need an install rule), value Σ qty × price; `pending_release_quantity` += qty | no | WS-293 Releases tab, WS-294 *New call-off* | FR-578, FR-580 |
| TPO-T1-09 | BLANKET, same states | Release schedule line(s) — whole or split | release `SUBMITTED` | `TPO-GRD-06`…`-08`, `-14`; release qty ≤ schedule open (qty − released − pending) | `wht_po_releases:create` / `:submit` | as `-08`; schedule `pending_release_quantity` | no | WS-294 (proposals + manual *Release*) | FR-579, FR-580 |
| TPO-T1-10 | release `SUBMITTED` | Approved | `RELEASED` | `TPO-GRD-15` (all release guards re-checked under a lock on the PO header), `-12` | approver / `SYSTEM` (submitter is the port's `actingUserId`) | **`releaseSchedule`** (`POS-T1-06`) in the same transaction (`TPO-T4-02`); pending → `released_quantity`; RC consumption (OPEN); print `SCHEDULE_RELEASE` available | — | — | FR-580 |
| TPO-T1-10a | release `SUBMITTED` | Rejected / returned | `REJECTED` / `DRAFT` | `TAM` | approver | `pending_release_quantity` −= qty — the schedule quantity is open again; the release lines' PR allocations (`target_type PO_RELEASE_LINE`) are released (`TPR-T4-03`, R31 F-TR-014) | **yes** | WS-285 | FR-580, FR-561 |
| TPO-T1-10b | release `DRAFT`, `REJECTED`; `SUBMITTED` after withdraw (`TAM-T1-09`) | Cancel | `CANCELLED` | — | `wht_po_releases:cancel` | pending quantity reverted; the release lines' PR allocations released (`TPR-T4-03`); nothing sent to core | **yes**, reason code | WS-294 / WS-293 | FR-580, FR-561 |
| TPO-T1-10c | release `RELEASED`, some of it unreceived | Cancel the unreceived part | `CANCELLED` (nothing received) or `CLOSED` (part received) | `TPO-GRD-09` per release line (no open gate entry or unposted GRN on its core lines); `TPO-GRD-14` | `wht_po_releases:cancel` | per release line, as `TPO-T4-09`: nothing received → `unfirmScheduleLine` (whole-firmed BLANKET line) or `cancelScheduleLine` (added `FIRM` line); **partly received → the core `FIRM` line is reduced to its received quantity by `amendOrder` `scheduleChanges.quantity`** (core's floor is the received quantity, FRD-STORES R.2; R31 F-TR-004 — `unfirm` and `cancel` both need 0 received); the unreceived BLANKET quantity returns to the trade schedule as unreleased and to core as `FORECAST` through the same `amendOrder` (`newScheduleLines` `FORECAST`, or `scheduleChanges` on the reduced `FORECAST` line); the unreceived quantity's PR allocation released (`TPR-T4-03`, R31 F-TR-014); RC consumption reduced | **yes**, reason code | WS-294 / WS-293 | FR-580, FR-583 |
| TPO-T1-11 | `ISSUED`, `ACKNOWLEDGED` with ack `PENDING` | Record acknowledgement | ack `ACCEPTED` → PO `ACKNOWLEDGED`; `ACCEPTED_WITH_CHANGES` → buyer decides: *Accept changes* drafts an amendment (`TOA-T1-01`, origin `ACK_CHANGES`, maker = that buyer) / *Dispute* logs a follow-up; `REJECTED` → follow-up + buyer decides cancel | — | `:acknowledge` | `wht_po_acknowledgements` row + per schedule line confirmed date/qty; **trade only** (`TPO-T4-05`) | supplier ref | WS-293 Acknowledgement tab | FR-586 |
| TPO-T1-12 | release `RELEASED` | Every core schedule line carrying its `releaseRef` is received, closed or cancelled (`purchase_order.schedule_line.received`, `getReceiptPosition`) | `CLOSED` | — | system | — | — | — | FR-580 |
| TPO-T1-13 | line `OPEN` / header non-terminal | Short-close line or header | request `PO_SHORT_CLOSE` (seeded zero-level) | `TPO-GRD-13`, `-14` | `:short_close` | — | **yes**, reason code | row action / line action | FR-588 |
| TPO-T1-13a | `PO_SHORT_CLOSE` request approved | Short-close takes effect | line `SHORT_CLOSED`; header `SHORT_CLOSED` when header action | `TPO-GRD-13` re-checked | approver / `SYSTEM` | **`closeLine`** for firm open qty, **`cancelScheduleLine`** for unreceived `FORECAST` lines, header: **`closeOrder`** (`TPO-T4-06`); unreleased schedule lines `CANCELLED`; open releases closed; PR allocations for unordered qty released; RC consumption reduced | — | WS-285 | FR-588 |
| TPO-T1-14 | any active | Log follow-up | follow-up row | — | `wht_po_followups:create` | `supplier_promised_date` on the schedule line; `next_followup_date` | no | WS-295, detail | FR-587 |

### 1.3 Guards

| ID | Predicate | Refusal | Source |
|---|---|---|---|
| TPO-GRD-01 | Supplier profile exists, not purchase-blocked; AVL per FR-544 for every line item; MICRO/SMALL with terms > 45 days ⇒ `msme_acknowledged = true` | `422` `TRADE_SUPPLIER_BLOCKED` / `TRADE_SUPPLIER_NOT_ON_AVL` / field `msmeAcknowledged` | FR-542, FR-544 |
| TPO-GRD-02 | Type rules: FIXED — every line qty > 0 and Σ schedule = qty (one schedule line defaulted from required date); OPEN — line qty null, `valid_from ≤ valid_to`, unit price > 0; BLANKET — qty > 0, validity set | field `422` | FR-575 |
| TPO-GRD-03 | Every line priced (`unit_price` set; 0 only with `is_free_of_charge` + reason, and **never on an OPEN line** — core refuses it, `STO-D14`); currency = rate contract currency when `rate_contract_line_id` set | field `422` `isFreeOfCharge` | FR-576 |
| TPO-GRD-04 | BLANKET: Σ schedule qty = line qty; every `delivery_date` ∈ validity; FIXED: schedule dates ≥ order date | `422 TRADE_SCHEDULE_TOTAL_MISMATCH` / `TRADE_OUTSIDE_VALIDITY` | FR-579 |
| TPO-GRD-05 | Item active and purchasable; UoM convertible; deliver-to site in the user's site scope; deliver-to location inside that site | field `422` | FR-576 |
| TPO-GRD-06 | Release date and delivery dates ∈ validity (`valid_to` is the last release date, `POS-GRD-05`); PO not *expired*, not terminal; FIXED lines are never released (`TRD-12`) | `422 TRADE_OUTSIDE_VALIDITY` / `TRADE_NOT_RELEASABLE` | FR-580 |
| TPO-GRD-07 | OPEN: Σ released + Σ pending qty (line) ≤ line ceiling; Σ released + pending value ≤ header ceiling value; RC ceiling via `TRC-T4-01` | `422 TRADE_CEILING_EXCEEDED {open}` | FR-578, FR-580 |
| TPO-GRD-08 | Supplier not blocked at release / qty-increasing amendment | `422 TRADE_SUPPLIER_BLOCKED` | FR-585 |
| TPO-GRD-09 | Cancel (order, or a released part): no core receipt on the lines concerned, no core gate entry open (`p8-03`), no posted or draft GRN — asked of core through `getReceiptPosition` | `409 TRADE_EXECUTION_STARTED {blocker}` | FR-583 |
| TPO-GRD-10 | Edit refused while an approval request or an amendment is open | `409 TRADE_APPROVAL_PENDING` / `TRADE_AMENDMENT_OPEN` | FR-553 |
| TPO-GRD-11 | At approval: re-resolve contract prices; if a rate contract used at draft has expired, ended or changed, refuse | `409 TRADE_PRICE_CHANGED_SINCE_SUBMIT` | FR-573 |
| TPO-GRD-12 | Idempotency: every port write carries the FRD-TRADE §12a key (`WHT_PURCHASE_ORDER:<id>:<operation>:<sequence>`); a repeated call returns the recorded result (`replayed = true`); no second core PO | `409 PORT_IDEMPOTENCY_CONFLICT` (relayed) | FR-618 |
| TPO-GRD-13 | Short-close: line has open qty (agreed or released − received − in-flight per core); in-flight (open gate entry, unposted GRN) blocks closing that part | `409 TRADE_IN_FLIGHT {gateEntryNo}` | FR-588 |
| TPO-GRD-14 | Amendment lock (`TOA-GRD-04`): a release, release cancel or line short-close touching a schedule line an open amendment changes is refused; a header short-close or cancel is refused while any amendment is open | `409 TRADE_AMENDMENT_OPEN` | FR-591 |
| TPO-GRD-15 | At release approval, under `SELECT … FOR UPDATE` on the PO header: `-06`, `-07` (with this release's own pending quantity counted once), `-08`, AVL (`-01`), price (`-11`) and `-14` re-checked | as each guard | FR-580, FR-618 |
| TPO-GRD-16 | `receipt_cutoff_date` null or ≥ `valid_to` | field `422` | FR-576 |

### 1.4 Unreachable

| ID | Forbidden | Why | Source |
|---|---|---|---|
| TPO-UNR-01 | Trade writing `wh_purchase_orders` / lines directly | port only (`RN-053`, `ArchitectureInvariantsTest` asserts no trade repository on `wh_` write) | FR-577 |
| TPO-UNR-02 | Core screens editing, approving, cancelling or closing a trade-created core PO | trade's `PurchaseOrderChangeGuard` bean (`POS-GRD-08`) refuses every change kind with `409 PO_OWNED_BY_SOURCE_MODULE` (`OD-39`) | FR-577 |
| TPO-UNR-03 | Changing an approved PO except by amendment | no edit modal after approval; `TOA` | FR-553 |
| TPO-UNR-04 | Auto-release of a BLANKET schedule line | `TRD-11`; the job writes `PROPOSED` only | FR-579 |
| TPO-UNR-05 | Storing received / accepted quantity in `wht_` | `TRD-03` | FR-581 |
| TPO-UNR-06 | Changing `po_type` after submit | not editable; API refuses | FR-575 |
| TPO-UNR-07 | A trade PO `CLOSED` while its core PO stays open | auto-close and header short-close call `closeOrder` in the same transaction | FR-589 |

### 1.5 Subcontract service PO (FR-682…FR-689, `D-18` item 3)

A `FIXED` PO with `po_purpose = SUBCONTRACT`; every line a `SUBCONTRACT_SERVICE` line linked to one MFG
subcontract order. It follows the PO ladder of §1.2 for draft, submit, approval, issue, acknowledgement,
expediting, cancel, short-close and auto-close, except as these rows say. **No sales twin** (FRD-TRADE §5 M34):
we do not sell processing.

| ID | From | Action | To | Guard | Actor | Side effects | Comment | UI | Source |
|---|---|---|---|---|---|---|---|---|---|
| TPO-T1-17 | `SUBMITTED` | Approved (last level) — subcontract PO | `APPROVED` | `TPO-GRD-11`, `-17`…`-19` re-checked | approver | **no port call**: no core PO is created (`TPO-UNR-08`); `version_no = 1` snapshot; service lines `OPEN` | — | WS-285 | FR-684 |
| TPO-T1-18 | `APPROVED`, `ISSUED`, `ACKNOWLEDGED`; line `OPEN` | Record service confirmation | confirmation `POSTED`; line confirmed += qty | `TPO-GRD-20` | `wht_purchase_orders:confirm_service` | number `<po_number>-Cnn`; job worker's bill no / date recorded; the charge posted by core in the same transaction (`TPO-T4-14`) | bill ref | WS-293 *Service confirmations* | FR-686 |
| TPO-T1-19 | confirmation `POSTED` | Reverse confirmation | `REVERSED` | not already reversed; core refuses the reverse `409 LANDED_COST_LAYER_CONSUMED` once any loaded layer was issued after apply (`CVL-GRD-09a`, correct by revaluation) and the trade reversal rolls back (P8 decision `G21`) | `wht_purchase_orders:confirm_service` | core reverses its landed-cost posting in the same transaction (`TPO-T4-14`); the quantity is confirmable again | **yes**, reason (`TRADE_ORDER_CLOSE`) | WS-293 | FR-687 |
| TPO-T1-20 | subcontract PO non-terminal | Cancel / short-close / auto-close | as `-05`/`-05a`, `-13`/`-13a`, `TPO-T3-03` | cancel: no `POSTED` confirmation; short-close closes the unconfirmed remainder; auto-close when every line confirmed ≥ qty × (1 − under tolerance) or short-closed | as those rows | **no port call** (no core PO) | as those rows | as those rows | FR-688 |

| ID | Predicate | Refusal | Source |
|---|---|---|---|
| TPO-GRD-17 | Purpose rules: a `SUBCONTRACT` PO is `FIXED`, in the company currency, and holds only `SUBCONTRACT_SERVICE` lines; a `STOCK` PO holds none; `po_purpose` immutable after submit | `422 TRADE_SUBCONTRACT_TYPE` / `TRADE_SUBCONTRACT_CURRENCY` / `TRADE_PO_PURPOSE_MIXED` | FR-684 |
| TPO-GRD-18 | Every service line has `subcontract_order_id`; at most one non-cancelled service line per subcontract order (partial unique index); a service line without a link is refused (R8 stands) | `422 TRADE_SERVICE_LINE_NEEDS_SUBCONTRACT_ORDER` / `409 TRADE_SUBCONTRACT_ORDER_ALREADY_ORDERED` | FR-682, FR-689 |
| TPO-GRD-19 | At save, submit and approval: `CostObjectResolver('PRODUCTION_ORDER').resolve(subcontract_order_id, companyId)` succeeds, the order is of kind `SUBCONTRACT` and its job worker is the PO's supplier; the line's item is the resolved order's processed item (FRD-TRADE §12c `CN-14` (a)) | `422 TRADE_SUBCONTRACT_ORDER_INVALID` | FR-683 |
| TPO-GRD-20 | Service confirmation: quantity > 0 and ≤ processed (core read, `TPO-T4-13`) − Σ `POSTED` confirmations of the line; line not `SHORT_CLOSED` / `CANCELLED` | `422 TRADE_CONFIRMATION_EXCEEDS_PROCESSED {open}` | FR-685, FR-686 |

| ID | Forbidden | Why | Source |
|---|---|---|---|
| TPO-UNR-08 | A core PO, release, gate entry or GRN for a subcontract PO; trade reading or writing a `whm_` row | the processed item comes back by MFG's subcontract receipt; the link is a bare id resolved through core (`TRD-09`, `ArchitectureInvariantsTest` (d)) | FR-684, FR-682 |
| TPO-UNR-09 | A service line on a `STOCK` PO, or a general service / capex PO | R8 stays refused (FRD-TRADE §11) | FR-689 |
| TPO-UNR-10 | Editing or deleting a posted service confirmation | corrected only by reversal (`TPO-T1-19`) | FR-687 |

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from | Source |
|---|---|---|---|---|
| TPO-T2-01 | Add / edit | `:create` / `:edit` | `DRAFT`, `REJECTED` | FR-575 |
| TPO-T2-02 | Submit / withdraw | `:submit` | `DRAFT`, `REJECTED` / `SUBMITTED` | FR-551 |
| TPO-T2-03 | Approve | `:approve` (`TAM`) + `warehouse:orders:port` | `SUBMITTED`; `PO_CANCEL` / `PO_SHORT_CLOSE` requests | FR-577 |
| TPO-T2-04 | Issue / print | `:issue` / `:view` | `APPROVED`+ | FR-576, FR-615 |
| TPO-T2-05 | Acknowledge | `:acknowledge` | `ISSUED`, `ACKNOWLEDGED` with ack `PENDING` | FR-586 |
| TPO-T2-06 | Release (OPEN/BLANKET) — create / submit / approve / cancel | `wht_po_releases:create` / `:submit` / `:approve` / `:cancel` (+ `warehouse:orders:port` for submit of a zero-level release, approve and cancel) | PO `APPROVED`, `ISSUED`, `ACKNOWLEDGED`; release per T1 | FR-580 |
| TPO-T2-07 | Amend | `:amend` (`TOA`) | `APPROVED`, `ISSUED`, `ACKNOWLEDGED` | FR-590 |
| TPO-T2-08 | Short-close | `:short_close` | non-terminal | FR-588 |
| TPO-T2-09 | Cancel | `:cancel` | non-terminal, `TPO-GRD-09` | FR-583 |
| TPO-T2-10 | Follow-up | `wht_po_followups:create` | non-terminal | FR-587 |
| TPO-T2-11 | Export | `:export` (auditor: none) | — | FR-616 |
| TPO-T2-13 | Confirm / reverse a subcontract service | `wht_purchase_orders:confirm_service` (+ the core authority `CN-14` (c) names) | subcontract PO `APPROVED`, `ISSUED`, `ACKNOWLEDGED` | FR-686, FR-687 |
| TPO-T2-12 | Every action in this table, and the auditor | `wht_<table>:<verb>` per FRD-TRADE FR-617 (`view`, `create`, `edit`, `export` + the workflow verbs above); `permission_dependencies` seeded; the auditor bundle holds `:view` only; record scope follows core's company / site grants; a bundle whose action calls a core port is also granted `warehouse:orders:port` in the trade seed | — | FR-617 |

## 3. T3 — Time-driven rules

| ID | Rule | Trigger | Changes | Notified (FRD-TRADE §12b) | Job | Source |
|---|---|---|---|---|---|---|
| TPO-T3-01 | Release proposal | BLANKET schedule line `PLANNED` with `delivery_date − lead_time_days(item, supplier) − warehouse.trade.release_horizon_days ≤ today` | `release_status = PROPOSED` | buyer, `TRADE_RELEASE_PROPOSED` | `TradeReleaseProposalJob` daily; once per line | FR-579 |
| TPO-T3-02 | Expediting due / overdue | open quantity on a FIXED schedule line or on a released OPEN / BLANKET quantity, with `delivery_date − warehouse.trade.expedite.days_before ≤ today` (site tz, `FR-439`); overdue when `delivery_date < today`; also `next_followup_date = today` | none (computed filters `dueSoon`, `overdue`) | buyer digest, `TRADE_EXPEDITE_DIGEST` | `TradeExpediteJob` daily | FR-587 |
| TPO-T3-03 | Auto-close | every line `SHORT_CLOSED` or fulfilment `COMPLETE`, no release open, **no GRN line of the PO under QC hold and no supplier return of it not yet dispatched / cancelled** (core reads), no `replacement_pending_quantity`; OPEN/BLANKET also when validity ended and nothing open | `CLOSED`; `closeOrder` (`TPO-T4-10`) | buyer, `TRADE_ORDER_CLOSED` | nightly `TradePoCloseJob`, calling as trade's **service principal** (`TRD-13`, FRD-STORES R.1 — never as the PO's buyer; R31 F-TR-012) | FR-589 |
| TPO-T3-04 | Ack overdue | ack `PENDING` `warehouse.trade.ack.alert_days` (default 3) after `issued_at` or after the amendment that reset it | none | buyer, `TRADE_PO_ACK_OVERDUE` | `TradeExpediteJob` | FR-586 |
| TPO-T3-05 | Validity ending | OPEN/BLANKET `valid_to − 30` | none | buyer, `TRADE_VALIDITY_ENDING` | `TradeContractJob` | FR-576 |
| TPO-T3-06 | Release overdue | BLANKET schedule line `PLANNED`/`PROPOSED` with open quantity and `delivery_date − lead_time_days ≤ today` (it can no longer arrive on time) | computed `releaseOverdue` on WS-294; the line is excluded from the supplier's `DELIVERY_OTIF` (`TCE`) | buyer, `TRADE_RELEASE_OVERDUE`, once per line | `TradeReleaseProposalJob` | FR-580 |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in | Source |
|---|---|---|---|---|
| TPO-T4-01 | Approved (every type) | `WhPurchaseOrderPort.createOrder(CreatePurchaseOrderCommand{ envelope(sourceModule 'warehouse-trade', idempotencyKey 'WHT_PURCHASE_ORDER:<id>:PO_CREATE:1', actingUserId = last approver), sourceDocumentType 'WHT_PURCHASE_ORDER', sourceDocumentId, sourceDocumentRef <po_number>, poType FIXED→FIXED · OPEN→OPEN · BLANKET→BLANKET_RELEASE, supplierCounterpartyId, warehouseId, ownerId, currencyCode, validFrom, validTo, receiptCutoffDate, agreementRef (BLANKET: the agreement number), initialStatus 'APPROVED', approvedByUserId = last approver, lines[ lineRef <line_no>, itemId, uomCode, orderedQuantity (FIXED: qty; OPEN, BLANKET: null — `POS-GRD-02`), unitPrice (net), rateSource / rateSourceRef, agreementLineRef (BLANKET), expectedDeliveryDate, overTolerancePct = `over_tolerance_pct`, underTolerancePct = `under_tolerance_pct`, receivingLocationId = the PO's `deliver_to_location_id`, schedule[ kind FIXED→FIRM · BLANKET→FORECAST, scheduledDate, quantity, unitPrice?, releaseRef (FIXED: the PO number) ] ] })` → core PO `APPROVED` with `approval_source = SOURCE_MODULE` (core's maker–checker not re-run, `POS-T1-05`); `core_po_id`, `core_po_line_id`, `core_schedule_line_id` stored. Tolerances and the receiving location reach core on the create, so core's over/short-receipt guard and GRN default read them (`POS-GRD-15`; FRD-TRADE §12c `CN-1`, resolved) | approval transaction | FR-577, FR-582 |
| TPO-T4-02 | Release approved | `releaseSchedule(ReleaseScheduleCommand{ envelope(key 'WHT_PURCHASE_ORDER:<poId>:PO_RELEASE:<release no>'), poId = core_po_id, releaseRef <release no>, entries[] })`: a whole BLANKET schedule line → `firm(scheduleLineId, unitPrice?)`, `unitPrice` = the release price when `AT_RELEASE`, else omitted (`STO-D19`; FRD-TRADE §12c `CN-6`, resolved); an OPEN call-off or a split BLANKET line → `add(poLineId, FIRM, deliveryDate, qty, unitPrice)` — and for BLANKET the `FORECAST` line is reduced to the remainder by `amendOrder` `scheduleChanges` (key `…:PO_AMEND:<release no>`) or ended by `cancelScheduleLine` (key `…:PO_CANCEL_SCHEDULE:<release no>-<schedule no>`) when nothing remains; the core `FIRM` line ids are stored on the release lines | release approval transaction | FR-578 |
| TPO-T4-03 | Any port call refused | trade transaction rolls back; the core error code and field (e.g. `403 PORT_AUTHORITY_REQUIRED`, `422 PO_LINE_QUANTITY_RULE`, `409 PORT_IDEMPOTENCY_CONFLICT`) are relayed in the trade envelope | port adapter | FR-577, FR-618 |
| TPO-T4-04 | Detail / grid read | received, accepted, rejected, in-flight, billed quantities, gate entries, GRNs (bill no/date), QC results and holds, MRNs, supplier returns, claims read from core by `core_po_id` (FK down; `getReceiptPosition` for quantities per line and schedule line); fulfilment `COMPLETE` when every line received ≥ qty × (1 − under tolerance) or short-closed | `PurchaseOrderQueryService` (read-only joins / core query beans) | FR-581 |
| TPO-T4-05 | Ack recorded | trade only — the port has no acknowledge operation; core `acknowledged_at` stays null for trade POs (`TPO-OPEN-03`) | ack transaction | FR-586 |
| TPO-T4-06 | Short-close / cancel approved | `closeLine(ClosePurchaseOrderLineCommand)` / `cancelScheduleLine` / `closeOrder` / `cancelOrder` with `reasonCodeId` (a `TRADE_ORDER_CLOSE`-context `whb_reason_codes` id — the request's reason, FR-546, R31 F-TR-007) and `note`, keys `WHT_PURCHASE_ORDER:<poId>:<op>:<request id>-<line / schedule no>`; PR allocation release (`TPR-T1-07`); RC consumption reduced | same transaction | FR-583, FR-588 |
| TPO-T4-07 | `supplier_return.dispatched` with intent `REPLACE` for this PO (`source_document_id`) | PO `APPROVED`/`ISSUED`/`ACKNOWLEDGED`: a system amendment `DRAFT` (origin `SUPPLIER_RETURN`, change `SCHEDULE_ADD` of the returned qty on the original line, condition `supplier_return_replacement`) is drafted for the buyer to submit; while another amendment is open the quantity waits in `replacement_pending_quantity` and is drafted when it ends. PO `CLOSED` cannot happen meanwhile (`TPO-T3-03`); PO `SHORT_CLOSED` / `CANCELLED`: nothing reinstated, buyer notified `TRADE_REPLACEMENT_NEEDS_NEW_PO`, shown on the Returns tab | outbox subscriber (`OD-33`, `TOA-T1-01`) | FR-613 |
| TPO-T4-08 | Any write | `whb_audit_events` | services | FR-540 |
| TPO-T4-09 | Release cancelled after approval | a whole-firmed BLANKET line with nothing received → `unfirmScheduleLine(UnfirmScheduleLineCommand{ scheduleLineId, reasonCodeId, note })` (key `…:PO_UNFIRM_SCHEDULE:<release no>-X<n>`), back to `FORECAST` keeping its schedule number and release reference (`STO-D19`; FRD-TRADE §12c `CN-6`, resolved); each added unreceived `FIRM` line → `cancelScheduleLine(CancelScheduleLineCommand{ scheduleLineId, reasonCodeId, note })` (key `…:PO_CANCEL_SCHEDULE:<release no>-X<n>`), and a split BLANKET remainder is restored by `amendOrder` (`scheduleChanges` on the reduced `FORECAST` line, or `newScheduleLines` when it was ended; key `…:PO_AMEND:<release no>-X`), so the core forecast equals the unreleased schedule. A **partly received** line (`TPO-T1-10c`) is neither un-firmed nor cancelled: `amendOrder` (key `…:PO_AMEND:<release no>-X`) sets its `scheduleChanges.quantity` to the received quantity and, in the same command, restores the unreceived BLANKET quantity as `FORECAST` (R31 F-TR-004). Every `reasonCodeId` is a `TRADE_ORDER_CLOSE` reason (FR-546) | release cancel transaction | FR-580 |
| TPO-T4-10 | Auto-close | `closeOrder(ClosePurchaseOrderCommand{ poId, reasonCodeId = AUTO_CLOSE, note })` as trade's service principal (`TRD-13`), key `…:PO_CLOSE:AUTO` — `AUTO_CLOSE` is the `TRADE_ORDER_CLOSE` reason trade seeds (FR-546); idempotent on a `CLOSED` core PO (`POS-T1-08`) | close job transaction | FR-589 |
| TPO-T4-11 | Core events for this PO (`purchase_order.schedule_line.received`, `purchase_order.line.received`, `purchase_order.amended`, `purchase_order.closed`, `purchase_order.cancelled`) | release close (`TPO-T1-12`), expediting refresh; a core-side close or cancel the trade PO did not cause is logged for the buyer (it cannot happen through the guarded screens) | outbox subscriber | FR-580, FR-589 |
| TPO-T4-13 | Subcontract service line read (WS-292 / WS-293, `TPO-GRD-20`) | processed quantity = the processed item's base quantity received by the linked order's receipts, from core's received-output read for cost object `PRODUCTION_ORDER` × item (FRD-TRADE §12c `CN-14` (b)); never stored; fulfilment derived as `TPO-T4-04` | `PurchaseOrderQueryService` | FR-685 |
| TPO-T4-14 | Service confirmation posted / reversed | core's landed-cost apply (`CN-14` (c); `WhCostObjectChargePort.applyOutputCharge` / `reverseOutputCharge`, FRD-STORES registry R.2) with `PortEnvelope(key 'WHT_PURCHASE_ORDER:<poId>:SUBCONTRACT_CHARGE_APPLY:<confirmation no>', actingUserId = the confirming buyer)`, source `WHT_PURCHASE_ORDER` / the confirmation, cost object `PRODUCTION_ORDER` = `subcontract_order_id`, item = the processed item, value = confirmed qty × line net price in the company currency → one value-only `LANDED_COST_APPLY` onto the order's receiving lots (`CVL-T4-07` sends a consumed share on); its reference stored as `core_landed_cost_ref`. Reversal: the same port's reverse (`…:SUBCONTRACT_CHARGE_REVERSE:<confirmation no>`). A refusal rolls back (`TPO-T4-03`). **P8 decision `G21`:** all output lots at one site, owner and company, else `422 COST_OBJECT_OUTPUT_MULTIPLE_SITES` before any number or posting (no splitting); `reverseOutputCharge` follows `CVL-GRD-09a` — refused `409 LANDED_COST_LAYER_CONSUMED` once any loaded layer was issued after apply (correct by revaluation), and the trade reversal rolls back; a port-created charge is reversed only through the port. Closes MFG `SUB-OPEN-06` | confirmation transaction | FR-686, FR-687 |
| TPO-T4-12 | — (mirror of `TSO-T4-12` ATP) | **refused**: supplier capacity is not known to us (§5 M19) | — | FR-575 (§5 M19) |

## 5. T5 — Screen contract

### 5.1 WS-292 Purchase Orders (reference **Service Vehicle**)
Grid `wht_purchase_orders`, scope `WAREHOUSE_TRADE_PURCHASE_ORDER`, sort `e.order_date DESC`. Tiles:
awaiting approval, approved / not issued, ack pending, overdue schedule lines, open value (company currency,
plus *+n in other currencies*, FR-616). Columns: `poNumber`, `poType`, `versionNo`, `supplierName`,
`supplierGrade` (latest published, FR-597), `warehouseName`, `buyerName`, `orderDate` (date-only), `validTo`,
`currencyCode`, `orderValue`, `releasedValue`, `fulfilment` (derived), `ackStatus`, `status`, `msmeCategory`,
audit. Filters: `warehouseId`; `poType`; `status`; `supplierId` typeahead; `buyerId`; `itemId`; `currencyCode`;
`orderFrom`/`orderTo`; `overdueOnly`; `ackPendingOnly`. Row actions: View · Edit · Submit · Withdraw · Issue ·
Print · Acknowledge · Release · Amend · Short-close · Cancel. Toolbar: Add (type picker first; *Subcontract PO* = `FIXED`, `po_purpose = SUBCONTRACT`, FR-689) · Export (⊇ grid, money per row in
its own currency). Column and filter `poPurpose` (FR-689). Add/Edit modal tabs: Header · Lines · Schedule · Charges & terms (≤ 6 groups each).

### 5.2 WS-293 Detail — tabs per FRD-TRADE §6.

### 5.3 WS-294 Schedule Releases
Grid `wht_po_releases`, scope `WAREHOUSE_TRADE_PO_RELEASE`, sort `e.release_date DESC`, plus a *Proposals* view
(schedule lines `PROPOSED` and *release overdue*). Tiles: proposals, release overdue, submitted, released
(period), cancelled (period) — counts. Columns: `releaseNumber`, `poNumber`, `poType`, `supplierName`,
`releaseDate`, `lineCount`, `releaseValue`, `currencyCode`, `status`, `corePoNumber`, audit. Filters:
`supplierId`, `warehouseId`, `poId`, `status`, `proposalsOnly`, `releaseOverdueOnly`, `dueFrom`/`dueTo`.
Actions: *Release* (manual: pick a BLANKET PO's schedule lines, or *New call-off* on an OPEN PO) · Release
selected proposals (multi-select, one release per PO) · View · Submit · Withdraw · Cancel (`TPO-T1-10b`,
`-10c`) · Print. Export ⊇ grid. Empty state: *No releases — releases are raised from OPEN and BLANKET
orders.*

### 5.4 WS-295 Purchase Expediting
Grid `wht_po_expediting` (open FIXED schedule lines and open released quantities), scope
`WAREHOUSE_TRADE_PO_EXPEDITING`, sort `e.delivery_date ASC`. Tiles: due ≤ `days_before`, overdue, follow-up
due today, ack pending, promised later than agreed — counts. Columns: `poNumber`, `releaseNumber` (blank for
FIXED), `supplierName`, `itemCode`, `deliveryDate` (agreed), `supplierConfirmedDate`, `supplierPromisedDate`,
`openQuantity`, `daysLate` (backend), `lastFollowupAt`, `nextFollowupDate`. Filters: `supplierId`, `buyerId`,
`warehouseId`, `poType`, `dueSoon`, `overdue`, `followupDueToday`. Actions: Log follow-up · Open PO. Export
⊇ grid (`wht_po_followups:export`). Empty state: *Nothing to expedite.*

## 6. Out of scope

| Item | Decision |
|---|---|
| Gate entry, GRN, bill capture, short/excess handling, QC, MRN | core `p8-03`…`p8-08`; read-only here |
| Debit note on short / reject | refused (FRD §11 R3) |
| Invoice match | refused (R2) |
| Supplier-managed schedule via portal / EDI | refused (R6, R7) |

## 7. Amendments

| Date | Rows | Change | Found by |
|---|---|---|---|
| 2026-10-22 | all | v0 derived | TRADE author |
| 2026-10-22 | all | R29 TP-F1, F4, F6, F7, F14, F15, F17, F19, F21–F23, F26–F28, TS-F7, MA-02, MA-05, MA-10 and contract quality: registry-exact port commands and keys; release ladder (reject-revert, cancel, close by `releaseRef`); `PO_CANCEL`; auto-close → `closeOrder` with QC / return holds; reinstatement as a system amendment; pending releases reserved; approval-time re-check; amendment lock on changed lines; `open_unbounded`; free-of-charge refused on OPEN; receipt cut-off; FIXED in expediting; release overdue; screens completed; ack drift fixed (`TPO-T1-11` = `T4-05`); numbering aligned row for row with `TSO` | R29 |
| 2026-10-22 | `TPO-T4-01`, `-02`, `-09`, `TPO-OPEN-01` | Aligned to the updated core registry: create carries tolerances and receiving location (`CN-1`); whole-line BLANKET release uses `firm(…, unitPrice)`; release cancel uses `unfirmScheduleLine` and `amendOrder` (`newScheduleLines`) instead of cancel + re-add (`CN-6` → `STO-D19`); `CN-1`…`CN-7` resolved | TRADE author |
| 2026-10-23 | every T1, guard, unreachable, T3 and T4 row | `Source` column added, filled from FRD-TRADE §4, so every rule traces to the FR it proves | R30 `CP-FR-008` |
| 2026-10-23 | `TPO-T1-10a`…`-10c`, `-T3-03`, `-T4-06`, `-T4-09`, `-T4-10`, `-T4-12`, §1.5 (new), `TPO-T2-13`, A14, §5.1, `TPO-OPEN-02`, every T2 row | R31: partly received release reduced by `amendOrder` (F-TR-004, `CN-12`); release reject / cancel releases PR allocations (F-TR-014); auto-close as the service principal (F-TR-012); port reasons are `whb_reason_codes` (F-TR-007); T2 Source FRs (F-TR-019); subcontract service PO rows for FR-682…FR-689 (`D-18` item 3); `TPO-OPEN-02` settled | R31 |
| 2026-10-24 | every row citing a core event | P8 decision record `EV-1` (DECISIONS `D-19`): every outbox event code renamed to the dotted `whb_event_types` vocabulary of registry R.4 (PC-42) — e.g. `purchase_order.amended`, `demand_order.shipped`, `rma.matched`, `supplier_return.dispatched`; no behaviour change | decision record P8 wave 1/2 |
| 2026-10-24 | `TPO-T1-19`, `TPO-T4-14` | P8 decision `G21` (DECISIONS `D-19`): output lots at one site, owner and company, else `422 COST_OBJECT_OUTPUT_MULTIPLE_SITES`; reverse follows `CVL-GRD-09a` (`409 LANDED_COST_LAYER_CONSUMED`) and the trade reversal rolls back | decision record P8 wave 1/2 |

## 8. Invariants and scenarios

`FR-123` layered truth · `L-1` untouched (trade posts nothing) · `WH-SC-524`…`WH-SC-540`, `WH-SC-483`,
`WH-SC-536`, `WH-SC-567`, `WH-SC-568`, `WH-SC-571`, `WH-SC-572`, `WH-SC-576`…`WH-SC-579`.

## 9. Open rows

| ID | Question | Status |
|---|---|---|
| TPO-OPEN-01 | Port signatures above vs `p8-01` | **Settled (R29):** aligned to FRD-STORES *Port & seam registry*; FRD-TRADE §12c `CN-1`, `CN-2`, `CN-5`, `CN-6`, `CN-7` resolved by STORES 2026-10-22 (registry R.1, R.2; `STO-D19`, `STO-D20`); nothing owed |
| TPO-OPEN-02 | `OD-30` PO pickers match `source_document_ref` | **Settled (R31 decisions):** pickers match `po_number` **or** `source_document_ref` and show both; owed by `p8-03` / `p8-04` |
| TPO-OPEN-03 | Should the port gain `acknowledge` so core WS-072 shows the supplier acknowledgement? | **Settled: no** — WS-293 owns it (`TPO-T4-05`) |
