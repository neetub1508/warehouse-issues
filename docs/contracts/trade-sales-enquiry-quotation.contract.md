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
| **Workflow** | Enquiry recorded → (regret, whole or per line) or quotation drafted → submit (approval) → approved → sent → revised (new version, also after expiry) → won / lost **per line** → SO / sales RC drafted for won lines; remaining enquiry lines quoted, regretted or closed lost; cancelled |
| **Module** | `warehouse-trade` |
| **Domain baseline** | FRD-TRADE FR-598…FR-601, FR-545 (customer part approval), FR-604, `TRD-10` |
| **Owning task body** | `issues/p9-08.md` |
| **Primary tables** | `wht_sales_enquiries`, `wht_sales_enquiry_lines`, `wht_customer_quotations`, `wht_customer_quotation_lines`, `wht_customer_quotation_charges` (`V550070`) |
| **Permission resources** | `wht_sales_enquiries:view/create/edit/export/cancel` · `wht_customer_quotations:view/create/edit/export/submit/approve/issue/cancel` |
| **Routes** | WS-298 `/warehouse/trade/sales/enquiries`, WS-299 `/quotations`, WS-300 `/win-loss` · mobile: none |
| **Contract status / version** | `derived` · `v1 — 2026-10-22` (R29 folded) |

**Fields.** Enquiry: `enquiry_number` (at save, series `ENQ`), company, customer, `customer_enquiry_ref`,
`customer_enquiry_date`, `source_code`, `quote_by_date`, `sales_exec_id`, `dispatch_warehouse_id`,
`status`, `regret_reason_code`, `outcome_at`. Line: item (nullable with `new_item_description` when the
plant has no item yet — such a line can be regretted or quoted only after an item exists), customer part
no (FR-545), qty, UoM, required date, `target_price`, spec note, `line_outcome` (`OPEN`, `QUOTED`, `WON`,
`LOST`, `REGRETTED`), `regret_reason_code`. Quotation:
`quotation_number` (series `SQ`, at submit; shared by all versions), `version_no`, `supersedes_id`,
`enquiry_id` (nullable), customer, `quote_date`, `valid_until`, currency, payment / delivery / freight
terms, `terms_template_version_id`, `status`, `won_target_type` + `won_target_id`, `loss_reason_code`,
`competitor_name`, `competitor_price`, `sent_at`. Line: `enquiry_line_id`, item, customer part no, qty,
UoM, `unit_price`, `discount_percent`, `net_price`, `price_source`, `floor_price_at_quote`,
`lead_time_days`, `promised_date`, `is_free_of_charge`, `line_outcome` (`WON`/`LOST`, set at the outcome),
`loss_reason_code`, `competitor_name`, `competitor_price`. Charges (`wht_customer_quotation_charges`, the
vendor-quotation shape): `charge_type_code` (code list `trade_charge_type`), `amount`, `allocation_basis`
(`VALUE`/`QUANTITY`), `note`; no tax; carried to `wht_so_charges` of the won SO.

### Acceptance checks

| # | Expects | Delivered by |
|---|---|---|
| A1 | Enquiry → quotation v1 sent (`WH-SC-550`) | `TSQ-T1-01`, `-04`…`-07` |
| A2 | Revision supersedes; only the latest sent version is winnable (`WH-SC-551`) | `TSQ-T1-08`, `TSQ-GRD-05` |
| A3 | Regret with reason and letter (`WH-SC-552`) | `TSQ-T1-03` |
| A4 | Lost with reason, competitor, price; analysis (`WH-SC-553`) | `TSQ-T1-10`, §5.3 |
| A5 | Won drafts the order (`WH-SC-554`) | `TSQ-T4-02` |
| A6 | Below floor / big discount needs approval — the zero-level default never approves it; unapproved part refused (`WH-SC-521`, `-486`, `-585`) | `TSQ-GRD-02`, `-03`, `TAM-GRD-01` |
| A7 | An expired quotation can still be won (PO-date evidence) or lost (`WH-SC-582`) | `TSQ-T1-09`, `-10`, `TSQ-GRD-05` |
| A8 | Partly quoted / partly won enquiries resolve every line (`WH-SC-583`) | `TSQ-T1-02`, `-03`, `-12`, `TSQ-T4-01` |

## 1. T1 — State machine

### 1.1 Status inventory

| Entity | Status | Reachable via | Exits via | Kind |
|---|---|---|---|---|
| Enquiry | `OPEN` | `-01` | `-02`, `-03`, `-11` | initial |
| Enquiry | `QUOTED` | first version `SENT` | `-02` (open lines), `-03` (lines), `-12`, outcome (`TSQ-T4-01`) | active |
| Enquiry | `WON` / `PARTIALLY_WON` / `LOST` / `REGRETTED` / `CANCELLED` | `TSQ-T4-01`, `-03`, `-11`, `-12` | none | terminal |
| Enquiry line | `OPEN` → `QUOTED` → `WON` / `LOST`; `REGRETTED` | `line_outcome` | `-02`, `-03`, `-09`, `-10`, `-12` | — |
| Quotation version | `DRAFT` → `SUBMITTED` → `APPROVED` → `SENT`; `REJECTED`; `REVISED`; `WON`; `LOST`; `EXPIRED` (→ revise / won / lost); `CANCELLED` | below | — | — |

### 1.2 Transitions

| ID | From | Action | To | Guard | Actor | Side effects | Comment | UI |
|---|---|---|---|---|---|---|---|---|
| TSQ-T1-01 | — | Record enquiry | `OPEN` | `TSQ-GRD-01` | `wht_sales_enquiries:create` | number | no | WS-298 Add |
| TSQ-T1-02 | `OPEN`; `QUOTED` with lines still `OPEN` | Prepare quotation (for the open lines) | quotation v1 `DRAFT` | the lines are `OPEN` (not already on a live quotation) | `wht_customer_quotations:create` | lines copied; prices resolved `TRC-T4-04` | no | *Quote* / *Quote remaining* |
| TSQ-T1-03 | `OPEN` (whole), or `OPEN` / `QUOTED` (selected open lines) | Regret | enquiry `REGRETTED` (whole) / lines `REGRETTED` | — | `wht_sales_enquiries:edit` | print `REGRET_LETTER` (the lines regretted); `TSQ-T4-01` re-evaluates the header | **yes**, reason code | *Regret* / *Regret lines* |
| TSQ-T1-04 | `DRAFT`, `REJECTED` | Submit | `SUBMITTED`; approved at once by `SYSTEM` only when the seeded zero-level `EXACT` `SQ` rule matches — i.e. the quotation carries **no** condition (`TAM-GRD-01`) | `TSQ-GRD-02`…`-04` | `:submit` | number at first submit; `TAM-T1-03` doc `SQ` with conditions `below_floor_price`, `discount_over_pct`, `manual_rate` | no | Submit |
| TSQ-T1-05 | `SUBMITTED` | Approved / rejected / returned | `APPROVED` / `REJECTED` / `DRAFT` | `TAM` | approver | maker notified | on reject/return | WS-285 |
| TSQ-T1-05a | `SUBMITTED` | Withdraw (`TAM-T1-09`) | `DRAFT` | no step acted | maker | — | no | *Withdraw* |
| TSQ-T1-06 | `APPROVED` | Send / print | `SENT` | template exists | `:issue` | print `CUSTOMER_QUOTATION`; `sent_at`; enquiry `QUOTED` | no | Send |
| TSQ-T1-07 | `SENT` | Reprint | — | — | `:view` | reprint flagged | no | Print |
| TSQ-T1-08 | `SENT`, `EXPIRED` (latest) | Revise | new version `DRAFT`; old `REVISED` on the new one's send | latest version only | `:edit` | `supersedes_id` | no | *Revise* |
| TSQ-T1-09 | `SENT`, `EXPIRED` (latest) | Record outcome — at least one line won | `WON`; each line `WON` or `LOST` | `TSQ-GRD-05`, `-06`, `-07` | `:edit` | `TSQ-T4-01`, `-02` (won lines only) | loss reason on each lost line; customer PO date when `EXPIRED` | *Won* (per-line outcome; target picker: FIXED / OPEN / BLANKET SO / sales RC) |
| TSQ-T1-10 | `SENT`, `EXPIRED` (latest) | Mark lost (every line) | `LOST` | — | `:edit` | `TSQ-T4-01` | **yes**: loss reason; competitor + price optional | *Lost* |
| TSQ-T1-11 | `OPEN`, quotation `DRAFT` | Cancel | `CANCELLED` | — | `:cancel` | — | yes | row action |
| TSQ-T1-12 | Enquiry `QUOTED` | Close as lost (customer silent) | every line still `OPEN` / `QUOTED` → `LOST` (reason required); the latest live quotation `LOST`; header per `TSQ-T4-01` | no quotation `SUBMITTED` / `APPROVED` | `wht_sales_enquiries:edit` | — | **yes**, loss reason | *Close as lost* |

### 1.3 Guards

| ID | Predicate | Refusal |
|---|---|---|
| TSQ-GRD-01 | Customer profile exists, not sales-blocked; ≥ 1 line | `422 TRADE_CUSTOMER_BLOCKED` |
| TSQ-GRD-02 | `requires_part_approval` ⇒ every line has a current `APPROVED` customer item reference | `422 TRADE_CUSTOMER_PART_NOT_APPROVED` |
| TSQ-GRD-03 | `valid_until ≥ quote_date` (default + `warehouse.trade.quotation.validity_days`); price ≥ 0 (0 only free-of-charge + reason); discount ∈ [0,100) | field `422` |
| TSQ-GRD-04 | Every line has an `item_id` (a new-item line must be resolved to an item first) | `422 TRADE_ITEM_REQUIRED` |
| TSQ-GRD-05 | Only the latest version, status `SENT` or `EXPIRED`; `valid_until ≥ today`, or the customer's PO date ≤ `valid_until` recorded on the win (always required from `EXPIRED`) | `409 TRADE_QUOTATION_NOT_WINNABLE` |
| TSQ-GRD-06 | Customer not sales-blocked at win | `422 TRADE_CUSTOMER_BLOCKED` |
| TSQ-GRD-07 | The outcome records `WON` or `LOST` (+ reason) for **every** quotation line | field `422` per line |

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
| TSQ-T2-03 | Submit / withdraw / approve | `:submit` / `:submit` (maker) / `:approve` | per T1 |
| TSQ-T2-04 | Send / print | `:issue` / `:view` | `APPROVED` / `SENT` |
| TSQ-T2-05 | Revise / won / lost | `:edit` | `SENT`, `EXPIRED` (latest) |
| TSQ-T2-08 | Quote remaining / regret lines / close as lost | `wht_customer_quotations:create` / `wht_sales_enquiries:edit` | enquiry `QUOTED` |
| TSQ-T2-06 | Compare versions | `:view` | ≥ 2 versions |
| TSQ-T2-07 | Export | `:export` | — |

## 3. T3 — Time-driven rules

| ID | Rule | Trigger | Changes | Notified | Job |
|---|---|---|---|---|---|
| TSQ-T3-01 | Quote-by reminder | enquiry `OPEN` (or `QUOTED` with open lines) and `quote_by_date − 1` | none | sales exec, `TRADE_QUOTE_BY` | `TradeSalesJob` daily |
| TSQ-T3-02 | Quotation expiry | `SENT` and `valid_until < today` | `EXPIRED` (still revisable, winnable with PO-date evidence, losable) | sales exec, `TRADE_QUOTATION_EXPIRED` | same |
| TSQ-T3-03 | Follow-up nudge | `SENT` / `EXPIRED` for `warehouse.trade.quotation.followup_days` (default 7) with no outcome | none | sales exec, `TRADE_QUOTATION_FOLLOWUP` | same |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in |
|---|---|---|---|
| TSQ-T4-01 | Line outcome recorded (won / lost / regretted / closed lost) | the enquiry line takes the quotation line's outcome; the header is `WON` when every line is `WON`, `PARTIALLY_WON` when every line has an outcome and at least one is `WON`, `LOST` / `REGRETTED` when every line is lost / regretted (`LOST` when mixed), else stays `QUOTED` | `QuotationService` |
| TSQ-T4-02 | Won | draft SO of the chosen type (or sales rate contract) prefilled with the **won lines only** — price (`price_source = QUOTATION`), terms, charges, customer PO no and date captured on the win modal; maker = the user who recorded the win | same transaction |
| TSQ-T4-03 | Enquiry regretted | open quotation drafts cancelled | same |
| TSQ-T4-04 | Version compare | backend diff of header + lines between any two versions | `QuotationVersionService` |

## 5. T5 — Screen contract

### 5.1 WS-298 Sales Enquiries (reference **Service Vehicle**)
Grid `wht_sales_enquiries`, scope `WAREHOUSE_TRADE_SALES_ENQUIRY`. Tiles: open, quote due ≤ 2 days,
quoted, won (period), lost (period) — counts. Columns: `enquiryNumber`, `customerName`, `customerEnquiryRef`,
`customerEnquiryDate`, `source`, `quoteByDate`, `salesExecName`, `lineCount`, `openLineCount`, `status`,
audit. Filters: `customerId`, `salesExecId`, `status`, `source`, `quoteByFrom`/`To`. Actions: View · Edit ·
Quote · Quote remaining · Regret · Regret lines · Close as lost · Cancel. Export ⊇ grid. Empty state: *No
enquiries.*

### 5.2 WS-299 Customer Quotations
Grid `wht_customer_quotations` (latest version per number by default; *All versions* toggle). Columns:
`quotationNumber`, `versionNo`, `customerName`, `enquiryNumber`, `quoteDate`, `validUntil`,
`currencyCode`, `quotationValue`, `belowFloor` flag, `status`, audit. Filters: `customerId`,
`salesExecId`, `status`, `currencyCode`, `validFrom`/`To`, `expiringOnly`. Tiles: draft, awaiting approval,
sent, expired, quoted value (company currency + *+n in other currencies*, FR-616). Actions: View · Edit ·
Submit · Withdraw · Send · Print · Revise · Compare versions · Won · Lost · Cancel. Modal tabs: Header · Lines
· Charges · Terms. Export ⊇ grid. Empty state: *No quotations.*

### 5.3 WS-300 Quotation Win/Loss (reference **Department**, read-only report grid)
Backend aggregates by period × customer × item × executive × loss reason **× currency**: quoted count / value,
won count / value, hit rate % (counts, currency-free), lost value; values are never added across currencies.
Filters: period (`DateRangePicker`), `customerId`, `salesExecId`, `lossReasonCode`, `currencyCode`. Export
allowed (grouped by currency).

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
| 2026-10-22 | §0, §1.1, `TSQ-T1-02`…`-05a`, `-08`…`-12`, `TSQ-GRD-05`, `-07`, T2, T3, T4, §5 | R29 TS-F4, F5, F8, F12, F24, F26, MA-15, MA-16, MA-18: won / lost / revise from `EXPIRED`, per-line outcomes, quote / regret remaining lines, close as lost, withdraw, exact zero-level rule, charges specified, currency-split values | R29 |

## 8. Invariants and scenarios

`WH-SC-486`, `WH-SC-520`, `WH-SC-521`, `WH-SC-550`…`WH-SC-554`, `WH-SC-582`, `WH-SC-583`, `WH-SC-585`.

## 9. Open rows

None beyond FRD-TRADE §10.
