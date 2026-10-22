# Functional Contract — Purchase order (FIXED / OPEN / BLANKET), schedules, releases, acknowledgement, expediting, short-close and the hand-off to stores

> **What this is.** The functional truth for the commercial purchase order in `warehouse-trade`: its
> three types, the delivery schedule, releases and their hand-off to the core PO through the `p8-01`
> port, the supplier acknowledgement, expediting and short-close. What happens at the gate, the GRN and
> QC is core's ([receipt-qc-putaway](receipt-qc-putaway.contract.md) and the STORES contracts); this
> contract only **reads** it. Approval cites `TAM-*`; amendment is
> [trade-order-amendment](trade-order-amendment.contract.md); pricing is `TRC-T4-02`.
>
> **Sales twin.** [trade-sales-order](trade-sales-order.contract.md), row for row (FRD-TRADE §5 M16–M25).
>
> **Status.** Derived 2026-10-22 (v0). No code exists yet. Port signatures are what trade **requires**
> from `p8-01`; STORES owns the port (`FRD-TRADE §12`).

---

## 0. Identity

| | |
|---|---|
| **Workflow** | Draft (manual, from PR workbench, from award) → submit → approve (FIXED/OPEN: core PO via port) → issue to supplier → acknowledgement → releases (OPEN call-offs, BLANKET schedule releases) → execution in core (gate entry, GRN + bill, QC, MRN) → complete / short-close → closed; cancel before execution; expediting throughout |
| **Module** | `warehouse-trade`; core `warehouse` through the `p8-01` port (`WhPurchaseOrderPort`, `ai.warehouse.port.purchase`; [po-schedule-port](po-schedule-port.contract.md) `POS-*`) and read-only queries |
| **Domain baseline** | FRD-TRADE FR-575…FR-589, FR-542 (MSME), FR-544 (AVL), FR-585, `TRD-01`, `TRD-03`, `TRD-11`, `OD-30`, `OD-38`, `OD-39` · R27 `RM-003`…`RM-010` · `FR-123` layered truth |
| **Owning task bodies** | `issues/p9-07.md` (types, schedule, releases, port, cancel) · `issues/p9-10.md` (acknowledgement, expediting, short-close, auto-close) |
| **Primary tables** | `wht_purchase_orders`, `wht_purchase_order_lines`, `wht_po_schedule_lines`, `wht_po_releases`, `wht_po_release_lines`, `wht_po_charges` (`V550060`); `wht_po_acknowledgements`, `wht_po_ack_lines`, `wht_po_followups` (`V550090`) |
| **Permission resources** | `wht_purchase_orders:view/create/edit/export/submit/approve/cancel/issue/acknowledge/short_close/amend` · `wht_po_releases:view/create/submit/approve/cancel/export` · `wht_po_followups:view/create/export` |
| **Routes** | WS-292 `/warehouse/trade/purchase/orders`, WS-293 `/[id]`, WS-294 `/releases`, WS-295 `/expediting` · mobile: none |
| **Contract status / version** | `derived` · `v0 — 2026-10-22` |

**Fields.** Header: `po_number` (trade series `PO` / `PA`, issued at submit; printed to the supplier and stored on the
core PO as `source_document_ref`, `OD-30`), `po_type` (`FIXED`/`OPEN`/`BLANKET`), `version_no` (1 at approval), company,
`supplier_counterparty_id`, `buyer_id`, `order_date`, `warehouse_id` (deliver-to site),
`deliver_to_location_id`, `currency_code`, `payment_terms_code` + `payment_terms_days`,
`delivery_terms_code`, `freight_terms_code`, `rate_contract_id`, `comparative_statement_id`,
`valid_from`/`valid_to` (OPEN/BLANKET), `ceiling_quantity`/`ceiling_value` (OPEN), `price_basis`
(`AGREEMENT`/`AT_RELEASE`), `terms_template_version_id`, `msme_acknowledged` + by/at, `status`,
`core_po_id` ↓ `wh_purchase_orders` (one core PO per trade PO, every type), `issued_at`, `ack_status`, `closed_at`,
`short_close_reason_code`. Line: `line_no`, item, `supplier_part_number`, description, `uom_code`,
`conversion_factor_used`, `quantity` (FIXED/BLANKET > 0; OPEN null), `ceiling_quantity` (OPEN line,
optional), `unit_price`, `discount_percent`, `net_price` (computed in backend), `price_source`,
`rate_contract_line_id`, `over_tolerance_pct`, `under_tolerance_pct`, `tax_classification_code`
(recorded), `is_free_of_charge`, `line_status` (`OPEN`/`SHORT_CLOSED`/`CANCELLED`), `core_po_line_id`.
Schedule line: `line_id`, `schedule_no`, `delivery_date`, `quantity`, `zone` (`FIRM`/`TENTATIVE`,
derived from `warehouse.trade.firm_zone_days` at read, frozen when released), `released_quantity`,
`release_status` (`PLANNED`/`PROPOSED`/`PARTIALLY_RELEASED`/`RELEASED`/`CANCELLED`),
`supplier_confirmed_date`, `supplier_confirmed_quantity`, `supplier_promised_date` (expediting).
Release: `release_number` (`<po_number>-Rnn`), `release_date`, `status`, `core_schedule_line_ids` (the `FIRM`
lines added / firmed on the core PO, `release_ref` = release number); release line: `po_line_id`, `schedule_line_id`
(BLANKET) or null (OPEN call-off), qty, delivery date, `unit_price` (by `price_basis`).

### Acceptance checks

| # | Expects | Delivered by |
|---|---|---|
| A1 | FIXED approval creates one core PO in the approval transaction; a port refusal rolls back (`WH-SC-524`, `-525`) | `TPO-T1-04`, `TPO-T4-01` |
| A2 | Idempotent approval (`WH-SC-526`) | `TPO-GRD-12` |
| A3 | OPEN call-offs within ceiling and validity (`WH-SC-527`, `-528`) | `TPO-T1-08`, `TPO-GRD-06`, `-07` |
| A4 | BLANKET schedule sums and validity; proposals never auto-release; partial release (`WH-SC-529`…`-531`) | `TPO-GRD-04`, `TPO-T3-01`, `TPO-T1-09` |
| A5 | Receipts, bills, QC read from core; fulfilment derived (`WH-SC-532`) | `TPO-T4-04` |
| A6 | Tolerance suggests short-close; short-close via port (`WH-SC-533`, `-539`) | `TPO-T1-13`, `TPO-T4-06` |
| A7 | Cancel only before execution; core cannot edit trade POs (`WH-SC-534`, `-535`) | `TPO-GRD-09`, `TPO-UNR-02` |
| A8 | Supplier blocked: no new releases (`WH-SC-536`) | `TPO-GRD-08` |
| A9 | Acknowledgement with changes drafts an amendment; agreed date unchanged (`WH-SC-537`) | `TPO-T1-11` |
| A10 | Expediting due/overdue in site timezone, promised date separate (`WH-SC-538`) | `TPO-T3-02` |
| A11 | Auto-close (`WH-SC-540`) | `TPO-T3-03` |

## 1. T1 — State machine

### 1.1 Status inventory

| Entity | Status | Reachable via | Exits via | Kind |
|---|---|---|---|---|
| PO | `DRAFT` | `-01`, award, PR workbench, return | `-02`, `-05` | initial |
| PO | `SUBMITTED` | `-02` | `TAM` | active |
| PO | `REJECTED` | `TAM` | edit → `DRAFT` | active |
| PO | `APPROVED` | `-04` | `-06`, `-05`, `-08`/`-09`, `-13` | active |
| PO | `ISSUED` | `-06` | `-10`, `-11`, releases, `-13` | active |
| PO | `ACKNOWLEDGED` | `-11` (`ACCEPTED`) | releases, `-13` | active |
| PO | `CLOSED` | `TPO-T3-03` | none | terminal |
| PO | `SHORT_CLOSED` | `-13` header | none | terminal |
| PO | `CANCELLED` | `-05` | none | terminal |
| PO | *fulfilment* `NOT_STARTED` / `PARTIAL` / `COMPLETE`; *validity* `EXPIRED` (OPEN/BLANKET) | **derived on read** (`TPO-T4-04`) | — | derived |
| Release | `DRAFT` → `SUBMITTED` → `RELEASED`; `REJECTED`; `CANCELLED`; `CLOSED` (core PO closed) | `-08`, `-09`, `TAM`, `-12` | — | — |
| Ack | `PENDING` → `ACCEPTED` / `ACCEPTED_WITH_CHANGES` / `REJECTED`; reset to `PENDING` by an approved amendment | `-11`, `TOA-T4-03` | — | — |

### 1.2 Transitions

| ID | From | Action | To | Guard | Actor | Side effects | Comment | UI |
|---|---|---|---|---|---|---|---|---|
| TPO-T1-01 | — | Create (manual / from PR lines / from award) | `DRAFT` | — | `:create` | prices resolved (`TRC-T4-02`); PR allocations | no | WS-292 Add (type picker first) |
| TPO-T1-02 | `DRAFT`, `REJECTED` | Submit | `SUBMITTED` | `TPO-GRD-01`…`-05`, `-08`, `-10` | `:submit` | number (BLANKET); `TAM-T1-03` doc `PO`, value Σ net × qty (FIXED/BLANKET) or ceiling value (OPEN; quantity-band rule when no ceiling value), conditions `manual_rate`, `non_l1_award` inherited | no | Submit |
| TPO-T1-03 | `SUBMITTED` | Withdraw | `DRAFT` | `TAM-T1-09` | maker | — | no | Withdraw |
| TPO-T1-04 | `SUBMITTED` | Approved (last level) | `APPROVED` | `TPO-GRD-11`, `-12` | approver | **`WhPurchaseOrderPort.createOrder`** (`POS-T1-05`) in the same transaction (`TPO-T4-01`) — every type; `version_no = 1` snapshot (`TOA-T4-02`); RC consumption (`TRC-T4-01`) FIXED only | — | WS-285 |
| TPO-T1-05 | `DRAFT`, `SUBMITTED`, `APPROVED`, `ISSUED`, `ACKNOWLEDGED` | Cancel | `CANCELLED` | `TPO-GRD-09` | `:cancel` | **`WhPurchaseOrderPort.cancelOrder`** when a core PO exists; PR allocations released; RC consumption reversed | **yes**, reason code | row action |
| TPO-T1-06 | `APPROVED` | Issue to supplier | `ISSUED` | template exists | `:issue` | print job `PURCHASE_ORDER` (version, T&C); `issued_at`; ack `PENDING` | no | Issue / Print |
| TPO-T1-07 | any non-terminal | Reprint | — | — | `:view` | reprint flagged | no | Print |
| TPO-T1-08 | OPEN, `APPROVED`/`ISSUED`/`ACKNOWLEDGED` | Create call-off release | release `DRAFT` → `SUBMITTED` | `TPO-GRD-06`, `-07`, `-08`, `TOA-GRD-04` | `wht_po_releases:create` | `TAM` doc `PO_RELEASE` (seeded zero-level within agreement) | no | WS-293 Releases tab, WS-294 |
| TPO-T1-09 | BLANKET, same states | Release schedule line(s) — whole or split | release `SUBMITTED` | `TPO-GRD-06`…`-08`; release qty ≤ schedule open | `wht_po_releases:create` | as `-08`; schedule `released_quantity` | no | WS-294 (proposals + manual) |
| TPO-T1-10 | release `SUBMITTED` | Approved | `RELEASED` | `TPO-GRD-12` | approver / `SYSTEM` | **`WhPurchaseOrderPort.releaseSchedule`** (`POS-T1-06`; OPEN: add `FIRM` dated schedule lines; BLANKET: firm the `FORECAST` lines, splitting where partial) in the same transaction; RC consumption; print `SCHEDULE_RELEASE` available | — | — |
| TPO-T1-11 | `ISSUED`, `ACKNOWLEDGED` (ack `PENDING`) | Record acknowledgement | ack `ACCEPTED` → PO `ACKNOWLEDGED`; `ACCEPTED_WITH_CHANGES` → buyer decides: *Accept changes* drafts an amendment (`TOA-T1-01`) / *Dispute* logs a follow-up; `REJECTED` → follow-up + buyer decides cancel | — | `:acknowledge` | `wht_po_acknowledgements` row + per schedule line confirmed date/qty; core `acknowledged_at` set via port (`TPO-T4-05`) | supplier ref | WS-293 Acknowledgement tab |
| TPO-T1-12 | release `RELEASED` | Core release PO closed / short-closed | release `CLOSED` | — | system (read) | — | — | — |
| TPO-T1-13 | line `OPEN` / header non-terminal with execution started | Short-close line or header | line `SHORT_CLOSED`; header `SHORT_CLOSED` when header action | `TPO-GRD-13` | `:short_close` | `TAM` doc `PO_SHORT_CLOSE` (seeded zero-level); **`WhPurchaseOrderPort.closeLine` / `closeOrder`** for firm open qty and **`cancelScheduleLine`** for unreceived `FORECAST` lines; unreleased schedule lines `CANCELLED`; PR allocations for unordered qty released; RC consumption reduced | **yes**, reason code | row action / line action |
| TPO-T1-14 | any active | Log follow-up | follow-up row | — | `wht_po_followups:create` | `supplier_promised_date` on the schedule line; `next_followup_date` | no | WS-295, detail |

### 1.3 Guards

| ID | Predicate | Refusal |
|---|---|---|
| TPO-GRD-01 | Supplier profile exists, not purchase-blocked; AVL per FR-544 for every line item; MICRO/SMALL with terms > 45 days ⇒ `msme_acknowledged = true` | `422` `TRADE_SUPPLIER_BLOCKED` / `TRADE_SUPPLIER_NOT_ON_AVL` / field `msmeAcknowledged` |
| TPO-GRD-02 | Type rules: FIXED — every line qty > 0 and Σ schedule = qty (one schedule line defaulted from required date); OPEN — line qty null, `valid_from ≤ valid_to`, unit price set; BLANKET — qty > 0, validity set | field `422` |
| TPO-GRD-03 | Every line priced (`unit_price` set; 0 only with `is_free_of_charge` + reason); currency = rate contract currency when `rate_contract_line_id` set | field `422` |
| TPO-GRD-04 | BLANKET: Σ schedule qty = line qty; every `delivery_date` ∈ validity; FIXED: schedule dates ≥ order date | `422 TRADE_SCHEDULE_TOTAL_MISMATCH` / `TRADE_OUTSIDE_VALIDITY` |
| TPO-GRD-05 | Item active and purchasable; UoM convertible; deliver-to site in the user's site scope | field `422` |
| TPO-GRD-06 | Release date and delivery dates ∈ validity; PO not *expired*, not terminal | `422 TRADE_OUTSIDE_VALIDITY` |
| TPO-GRD-07 | OPEN: Σ released qty (line) ≤ line ceiling; Σ released value ≤ header ceiling value; RC ceiling via `TRC-T4-01` | `422 TRADE_CEILING_EXCEEDED {open}` |
| TPO-GRD-08 | Supplier not blocked at release / qty-increasing amendment | `422 TRADE_SUPPLIER_BLOCKED` |
| TPO-GRD-09 | Cancel: no release `RELEASED` with core receipt, no core gate entry open (`p8-03`), no posted GRN on the core PO — asked of core through `WhPurchaseOrderPort.getReceiptPosition` | `409 TRADE_EXECUTION_STARTED {blocker}` |
| TPO-GRD-10 | Edit refused while an approval request or an amendment is open | `409 TRADE_APPROVAL_PENDING` / `TRADE_AMENDMENT_OPEN` |
| TPO-GRD-11 | At approval: re-resolve contract prices; if a rate contract used at draft has expired or changed, refuse | `409 TRADE_PRICE_CHANGED_SINCE_SUBMIT` |
| TPO-GRD-12 | Idempotency key `(WHT_PURCHASE_ORDER, id, version_no)` / `(WHT_PO_RELEASE, id)`: a repeated call returns the first result; no second core PO | — |
| TPO-GRD-13 | Short-close: line has open qty (agreed or released − received − in-flight per core); in-flight (open gate entry, unposted GRN) blocks closing that part | `409 TRADE_IN_FLIGHT {gateEntryNo}` |

### 1.4 Unreachable

| ID | Forbidden | Why |
|---|---|---|
| TPO-UNR-01 | Trade writing `wh_purchase_orders` / lines directly | port only (`RN-053`, `ArchitectureInvariantsTest` asserts no trade repository on `wh_` write) |
| TPO-UNR-02 | Core screens editing, approving, cancelling or closing a trade-created core PO | trade's `PurchaseOrderChangeGuard` bean (`POS-GRD-08`) refuses with `409 PO_OWNED_BY_SOURCE_MODULE` |
| TPO-UNR-03 | Changing an approved PO except by amendment | no edit modal after approval; `TOA` |
| TPO-UNR-04 | Auto-release of a BLANKET schedule line | `TRD-11`; the job writes `PROPOSED` only |
| TPO-UNR-05 | Storing received / accepted quantity in `wht_` | `TRD-03` |
| TPO-UNR-06 | Changing `po_type` after submit | not editable; API refuses |

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from |
|---|---|---|---|
| TPO-T2-01 | Add / edit | `:create` / `:edit` | `DRAFT`, `REJECTED` |
| TPO-T2-02 | Submit / withdraw | `:submit` | `DRAFT`, `REJECTED` / `SUBMITTED` |
| TPO-T2-03 | Approve | `:approve` (`TAM`) | `SUBMITTED` |
| TPO-T2-04 | Issue / print | `:issue` / `:view` | `APPROVED`+ |
| TPO-T2-05 | Acknowledge | `:acknowledge` | `ISSUED`, `ACKNOWLEDGED` |
| TPO-T2-06 | Release (OPEN/BLANKET) | `wht_po_releases:create` | `APPROVED`, `ISSUED`, `ACKNOWLEDGED` |
| TPO-T2-07 | Amend | `:amend` (`TOA`) | `APPROVED`, `ISSUED`, `ACKNOWLEDGED` |
| TPO-T2-08 | Short-close | `:short_close` | non-terminal |
| TPO-T2-09 | Cancel | `:cancel` | non-terminal, `TPO-GRD-09` |
| TPO-T2-10 | Follow-up | `wht_po_followups:create` | non-terminal |
| TPO-T2-11 | Export | `:export` | — |

## 3. T3 — Time-driven rules

| ID | Rule | Trigger | Changes | Notified | Job |
|---|---|---|---|---|---|
| TPO-T3-01 | Release proposal | BLANKET schedule line `PLANNED` with `delivery_date − lead_time_days(item, supplier) − warehouse.trade.release_horizon_days ≤ today` | `release_status = PROPOSED` | buyer | `TradeReleaseProposalJob` daily; once per line |
| TPO-T3-02 | Expediting due / overdue | open released schedule qty with `delivery_date − warehouse.trade.expedite.days_before ≤ today` (site tz, `FR-439`); overdue when `delivery_date < today`; also `next_followup_date = today` | none (computed filters `dueSoon`, `overdue`) | buyer digest | `TradeExpediteJob` daily |
| TPO-T3-03 | Auto-close | every line `SHORT_CLOSED` or fulfilment `COMPLETE` and no release open; OPEN/BLANKET also when validity ended and nothing open | `CLOSED` | buyer | nightly `TradePoCloseJob` |
| TPO-T3-04 | Ack overdue | ack `PENDING` `warehouse.trade.ack.alert_days` (default 3) after `issued_at` | none | buyer | `TradeExpediteJob` |
| TPO-T3-05 | Validity ending | OPEN/BLANKET `valid_to − 30` | none | buyer | `TradeContractJob` |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in |
|---|---|---|---|
| TPO-T4-01 | Approved (every type) | `WhPurchaseOrderPort.createOrder({sourceModule:'warehouse-trade', idempotencyKey:'WHT_PURCHASE_ORDER:<id>:v<version>', actingUserId, initialStatus:'APPROVED', approvedByUserId, sourceDocumentType:'WHT_PURCHASE_ORDER', sourceDocumentId, sourceDocumentRef:<po_number>, poType: FIXED→FIXED · OPEN→OPEN · BLANKET→BLANKET_RELEASE, agreementRef (BLANKET), validFrom/validTo, company, warehouse, supplier, currency, lines[item, uom, qty|null, unitPrice(net), rateSource/rateSourceRef, tolerances, taxClassificationCode, agreementLineRef], scheduleLines[lineNo, date, qty, kind: FIXED→FIRM · BLANKET→FORECAST]})` → core PO `APPROVED` with `approval_source = SOURCE_MODULE` (core's maker–checker not re-run, `POS-T1-05`); `core_po_id`, `core_po_line_id` stored | approval transaction |
| TPO-T4-02 | Release approved | `WhPurchaseOrderPort.releaseSchedule({corePoId, releaseRef, scheduleLines[lineRef, date, qty, kind:'FIRM']})` with idempotency key `WHT_PO_RELEASE:<id>` | release approval transaction |
| TPO-T4-03 | Any port call refused | trade transaction rolls back; the core error code and field are relayed in the trade envelope | port adapter |
| TPO-T4-04 | Detail / grid read | received, accepted, rejected, in-flight, billed quantities, gate entries, GRNs (bill no/date), QC results, MRNs, supplier returns, claims read from core by `core_po_id` (FK down); fulfilment `COMPLETE` when every line received ≥ qty × (1 − under tolerance) or short-closed | `PurchaseOrderQueryService` (read-only joins / core query beans) |
| TPO-T4-05 | Ack recorded | trade only — the port has no acknowledge operation; core `acknowledged_at` stays null for trade POs (`TPO-OPEN-03`) | ack transaction |
| TPO-T4-06 | Short-close / cancel | `WhPurchaseOrderPort.closeLine` / `closeOrder` / `cancelScheduleLine` / `cancelOrder` with reason; PR allocation release (`TPR-T1-07`); RC consumption reduced | same transaction |
| TPO-T4-07 | Core supplier return with intent `REPLACE` dispatched | open qty reinstated on the PO line through the port, shown on the Returns tab (`OD-33`, `TSR`) | event handler |
| TPO-T4-08 | Any write | `whb_audit_events` | services |

## 5. T5 — Screen contract

### 5.1 WS-292 Purchase Orders (reference **Service Vehicle**)
Grid `wht_purchase_orders`, scope `WAREHOUSE_TRADE_PURCHASE_ORDER`, sort `e.order_date DESC`. Tiles:
awaiting approval, approved / not issued, ack pending, overdue schedule lines, open value. Columns:
`poNumber`, `poType`, `versionNo`, `supplierName`, `warehouseName`, `buyerName`, `orderDate`
(date-only), `validTo`, `currencyCode`, `orderValue`, `releasedValue`, `fulfilment` (derived), `ackStatus`,
`status`, `msmeCategory`, audit. Filters: `warehouseId`; `poType`; `status`; `supplierId` typeahead;
`buyerId`; `itemId`; `orderFrom`/`orderTo`; `overdueOnly`; `ackPendingOnly`. Row actions: View · Edit ·
Submit · Withdraw · Issue · Print · Acknowledge · Release · Amend · Short-close · Cancel. Toolbar: Add ·
Export. Add/Edit modal tabs: Header · Lines · Schedule · Charges & terms (≤ 6 groups each).

### 5.2 WS-293 Detail — tabs per FRD-TRADE §6.

### 5.3 WS-294 Schedule Releases
Grid `wht_po_releases` plus a *Proposals* filter (schedule lines `PROPOSED`). Columns: `releaseNumber`,
`poNumber`, `supplierName`, `releaseDate`, `lineCount`, `releaseValue`, `status`, `corePoNumber`, audit.
Filters: `supplierId`, `warehouseId`, `status`, `proposalsOnly`, `dueFrom`/`dueTo`. Actions: Release
selected proposals (multi-select, one release per PO) · View · Cancel (before receipt) · Print.

### 5.4 WS-295 Purchase Expediting
Grid of open released schedule lines `wht_po_expediting`. Columns: `poNumber`, `releaseNumber`,
`supplierName`, `itemCode`, `deliveryDate` (agreed), `supplierConfirmedDate`, `supplierPromisedDate`,
`openQuantity`, `daysLate` (backend), `lastFollowupAt`, `nextFollowupDate`. Filters: `supplierId`,
`buyerId`, `warehouseId`, `dueSoon`, `overdue`, `followupDueToday`. Actions: Log follow-up · Open PO.

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

## 8. Invariants and scenarios

`FR-123` layered truth · `L-1` untouched (trade posts nothing) · `WH-SC-524`…`WH-SC-540`, `WH-SC-483`,
`WH-SC-536`.

## 9. Open rows

| ID | Question | Status |
|---|---|---|
| TPO-OPEN-01 | Port signatures above vs `p8-01` as written by STORES | reconcile when `p8-01` lands; this contract changes, not the port, unless a field is missing |
| TPO-OPEN-02 | `OD-30` PO pickers match `source_document_ref` | owed by `p8-03` / `p8-04` |
| TPO-OPEN-03 | Should the port gain `acknowledge` so core WS-072 shows the supplier acknowledgement? | **Proposed: no** — WS-293 owns it; revisit if stores asks. DEFERRED-TO-p9-10 |
