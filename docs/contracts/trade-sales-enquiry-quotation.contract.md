# Functional Contract — Sales enquiry → customer quotation (versions) → won / lost / regretted

> **What this is.** The functional truth for pre-sales in `warehouse-trade`: recording a customer's
> enquiry (their RFQ to us), preparing and approving our quotation, revising it, and recording the
> outcome, which drafts the sales order or sales rate contract. Pricing is `TRC-T4-04`; approval is `TAM-*`.
>
> **Purchase twin.** PR + RFQ + vendor quotation + comparative statement + award
> ([trade-purchase-requisition](trade-purchase-requisition.contract.md), [trade-rfq-award](trade-rfq-award.contract.md));
> FRD-TRADE §5 M3, M5–M12. Refused twins: consolidation (M5), sealed mode (M9), competitor comparison (M10).
>
> **Status.** Derived 2026-10-22 (v0). No code exists yet.

---

## 0. Identity

| | |
|---|---|
| **Workflow** | Enquiry recorded → (regret) or quotation drafted → submit (approval when conditions) → approved → sent → revised (new version) → won → SO / sales RC drafted; or lost / expired / cancelled |
| **Module** | `warehouse-trade` |
| **Domain baseline** | FRD-TRADE FR-598…FR-601, FR-545 (customer part approval), FR-604, `TRD-10` |
| **Owning task body** | `issues/p9-08.md` |
| **Primary tables** | `wht_sales_enquiries`, `wht_sales_enquiry_lines`, `wht_customer_quotations`, `wht_customer_quotation_lines`, `wht_customer_quotation_charges` (`V550070`) |
| **Permission resources** | `wht_sales_enquiries:view/create/edit/export/cancel` · `wht_customer_quotations:view/create/edit/export/submit/approve/issue/cancel` |
| **Routes** | WS-298 `/warehouse/trade/sales/enquiries`, WS-299 `/quotations`, WS-300 `/win-loss` · mobile: none |
| **Contract status / version** | `derived` · `v0 — 2026-10-22` |

**Fields.** Enquiry: `enquiry_number` (at save, series `ENQ`), company, customer, `customer_enquiry_ref`,
`customer_enquiry_date`, `source_code`, `quote_by_date`, `sales_exec_id`, `dispatch_warehouse_id`,
`status`, `regret_reason_code`, `outcome_at`. Line: item (nullable with `new_item_description` when the
plant has no item yet — such a line can be regretted or quoted only after an item exists), customer part
no (FR-545), qty, UoM, required date, `target_price`, spec note, `line_outcome`. Quotation:
`quotation_number` (series `SQ`, at submit; shared by all versions), `version_no`, `supersedes_id`,
`enquiry_id` (nullable), customer, `quote_date`, `valid_until`, currency, payment / delivery / freight
terms, `terms_template_version_id`, `status`, `won_target_type` + `won_target_id`, `loss_reason_code`,
`competitor_name`, `competitor_price`, `sent_at`. Line: `enquiry_line_id`, item, customer part no, qty,
UoM, `unit_price`, `discount_percent`, `net_price`, `price_source`, `floor_price_at_quote`,
`lead_time_days`, `promised_date`, `is_free_of_charge`.

### Acceptance checks

| # | Expects | Delivered by |
|---|---|---|
| A1 | Enquiry → quotation v1 sent (`WH-SC-550`) | `TSQ-T1-01`, `-04`…`-07` |
| A2 | Revision supersedes; only the latest sent version is winnable (`WH-SC-551`) | `TSQ-T1-08`, `TSQ-GRD-05` |
| A3 | Regret with reason and letter (`WH-SC-552`) | `TSQ-T1-03` |
| A4 | Lost with reason, competitor, price; analysis (`WH-SC-553`) | `TSQ-T1-10`, §5.3 |
| A5 | Won drafts the order (`WH-SC-554`) | `TSQ-T4-02` |
| A6 | Below floor / big discount needs approval; unapproved part refused (`WH-SC-521`, `-486`) | `TSQ-GRD-02`, `-03` |

## 1. T1 — State machine

### 1.1 Status inventory

| Entity | Status | Reachable via | Exits via | Kind |
|---|---|---|---|---|
| Enquiry | `OPEN` | `-01` | `-02`, `-03`, `-11` | initial |
| Enquiry | `QUOTED` | first version `SENT` | outcome | active |
| Enquiry | `WON` / `PARTIALLY_WON` / `LOST` / `REGRETTED` / `CANCELLED` | `TSQ-T4-01`, `-03`, `-11` | none | terminal |
| Quotation version | `DRAFT` → `SUBMITTED` → `APPROVED` → `SENT`; `REJECTED`; `REVISED`; `WON`; `LOST`; `EXPIRED`; `CANCELLED` | below | — | — |

### 1.2 Transitions

| ID | From | Action | To | Guard | Actor | Side effects | Comment | UI |
|---|---|---|---|---|---|---|---|---|
| TSQ-T1-01 | — | Record enquiry | `OPEN` | `TSQ-GRD-01` | `wht_sales_enquiries:create` | number | no | WS-298 Add |
| TSQ-T1-02 | `OPEN` | Prepare quotation | quotation v1 `DRAFT` | — | `wht_customer_quotations:create` | lines copied; prices resolved `TRC-T4-04` | no | *Quote* |
| TSQ-T1-03 | `OPEN` | Regret | `REGRETTED` | — | `wht_sales_enquiries:edit` | print `REGRET_LETTER` | **yes**, reason code | *Regret* |
| TSQ-T1-04 | `DRAFT`, `REJECTED` | Submit | `SUBMITTED` (or `APPROVED` directly when no condition and the seeded `SQ` rule is zero-level) | `TSQ-GRD-02`…`-04` | `:submit` | number at first submit; `TAM-T1-03` doc `SQ` with conditions `below_floor_price`, `discount_over_pct` | no | Submit |
| TSQ-T1-05 | `SUBMITTED` | Approved / rejected / returned | `APPROVED` / `REJECTED` / `DRAFT` | `TAM` | approver | — | on reject/return | WS-285 |
| TSQ-T1-06 | `APPROVED` | Send / print | `SENT` | template exists | `:issue` | print `CUSTOMER_QUOTATION`; `sent_at`; enquiry `QUOTED` | no | Send |
| TSQ-T1-07 | `SENT` | Reprint | — | — | `:view` | reprint flagged | no | Print |
| TSQ-T1-08 | `SENT`, `EXPIRED` | Revise | new version `DRAFT`; old `REVISED` on the new one's send | latest version only | `:edit` | `supersedes_id` | no | *Revise* |
| TSQ-T1-09 | `SENT` (latest) | Mark won (whole or per line) | `WON` | `TSQ-GRD-05`, `-06` | `:edit` | `TSQ-T4-02` | no | *Won* (target picker: FIXED / OPEN / BLANKET SO / sales RC) |
| TSQ-T1-10 | `SENT` (latest) | Mark lost | `LOST` | — | `:edit` | enquiry outcome | **yes**: loss reason; competitor + price optional | *Lost* |
| TSQ-T1-11 | `OPEN`, quotation `DRAFT` | Cancel | `CANCELLED` | — | `:cancel` | — | yes | row action |

### 1.3 Guards

| ID | Predicate | Refusal |
|---|---|---|
| TSQ-GRD-01 | Customer profile exists, not sales-blocked; ≥ 1 line | `422 TRADE_CUSTOMER_BLOCKED` |
| TSQ-GRD-02 | `requires_part_approval` ⇒ every line has a current `APPROVED` customer item reference | `422 TRADE_CUSTOMER_PART_NOT_APPROVED` |
| TSQ-GRD-03 | `valid_until ≥ quote_date` (default + `warehouse.trade.quotation.validity_days`); price ≥ 0 (0 only free-of-charge + reason); discount ∈ [0,100) | field `422` |
| TSQ-GRD-04 | Every line has an `item_id` (a new-item line must be resolved to an item first) | `422 TRADE_ITEM_REQUIRED` |
| TSQ-GRD-05 | Only the latest version, status `SENT`, `valid_until ≥ today` — or the customer's PO date ≤ `valid_until` recorded on the win | `409 TRADE_QUOTATION_NOT_WINNABLE` |
| TSQ-GRD-06 | Customer not sales-blocked at win | `422 TRADE_CUSTOMER_BLOCKED` |

### 1.4 Unreachable

| ID | Forbidden | Why |
|---|---|---|
| TSQ-UNR-01 | Editing a `SENT` version | revise creates a version |
| TSQ-UNR-02 | Winning a superseded version | `TSQ-GRD-05` |
| TSQ-UNR-03 | An SO drafted from a quotation without a win | the SO draft is created only in `TSQ-T4-02` (or manually, unlinked) |

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from |
|---|---|---|---|
| TSQ-T2-01 | Enquiry add / edit / regret | `wht_sales_enquiries:create`/`edit` | `OPEN` |
| TSQ-T2-02 | Quotation add / edit | `wht_customer_quotations:create`/`edit` | `DRAFT`, `REJECTED` |
| TSQ-T2-03 | Submit / approve | `:submit` / `:approve` | per T1 |
| TSQ-T2-04 | Send / print | `:issue` / `:view` | `APPROVED` / `SENT` |
| TSQ-T2-05 | Revise / won / lost | `:edit` | `SENT` (latest) |
| TSQ-T2-06 | Compare versions | `:view` | ≥ 2 versions |
| TSQ-T2-07 | Export | `:export` | — |

## 3. T3 — Time-driven rules

| ID | Rule | Trigger | Changes | Notified | Job |
|---|---|---|---|---|---|
| TSQ-T3-01 | Quote-by reminder | enquiry `OPEN` and `quote_by_date − 1` | none | sales exec | `TradeSalesJob` daily |
| TSQ-T3-02 | Quotation expiry | `SENT` and `valid_until < today` | `EXPIRED` | sales exec | same |
| TSQ-T3-03 | Follow-up nudge | `SENT` for `warehouse.trade.quotation.followup_days` (default 7) with no outcome | none | sales exec | same |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in |
|---|---|---|---|
| TSQ-T4-01 | Version won / lost | enquiry lines' outcome; enquiry `WON` / `PARTIALLY_WON` / `LOST` when every line has an outcome | `QuotationService` |
| TSQ-T4-02 | Won | draft SO of the chosen type (or sales rate contract) prefilled — lines, price (`price_source = QUOTATION`), terms, customer PO no captured on the win modal | same transaction |
| TSQ-T4-03 | Enquiry regretted | open quotation drafts cancelled | same |
| TSQ-T4-04 | Version compare | backend diff of header + lines between any two versions | `QuotationVersionService` |

## 5. T5 — Screen contract

### 5.1 WS-298 Sales Enquiries (reference **Service Vehicle**)
Grid `wht_sales_enquiries`, scope `WAREHOUSE_TRADE_SALES_ENQUIRY`. Tiles: open, quote due ≤ 2 days,
quoted, won (period), lost (period). Columns: `enquiryNumber`, `customerName`, `customerEnquiryRef`,
`customerEnquiryDate`, `source`, `quoteByDate`, `salesExecName`, `lineCount`, `status`, audit. Filters:
`customerId`, `salesExecId`, `status`, `source`, `quoteByFrom`/`To`. Actions: View · Edit · Quote ·
Regret · Cancel.

### 5.2 WS-299 Customer Quotations
Grid `wht_customer_quotations` (latest version per number by default; *All versions* toggle). Columns:
`quotationNumber`, `versionNo`, `customerName`, `enquiryNumber`, `quoteDate`, `validUntil`,
`currencyCode`, `quotationValue`, `belowFloor` flag, `status`, audit. Filters: `customerId`,
`salesExecId`, `status`, `validFrom`/`To`, `expiringOnly`. Actions: View · Edit · Submit · Send · Print ·
Revise · Compare versions · Won · Lost · Cancel.

### 5.3 WS-300 Quotation Win/Loss (reference **Department**, read-only report grid)
Backend aggregates by period × customer × item × executive × loss reason: quoted count / value, won
count / value, hit rate %, lost value. Filters: period (`DateRangePicker`), `customerId`, `salesExecId`,
`lossReasonCode`. Export allowed.

## 6. Out of scope

| Item | Decision |
|---|---|
| Lead / opportunity pipeline | refused (FRD §11 R11) |
| Cost-plus quotation build-up from BOM / routing | MFG; trade takes a typed price (re-entry: MFG publishes a standard cost the quotation shows as reference) |
| Competitor bid comparison | refused (R10) |

## 7. Amendments

| Date | Rows | Change | Found by |
|---|---|---|---|
| 2026-10-22 | all | v0 derived | TRADE author |

## 8. Invariants and scenarios

`WH-SC-486`, `WH-SC-520`, `WH-SC-521`, `WH-SC-550`…`WH-SC-554`.

## 9. Open rows

None beyond FRD-TRADE §10.
