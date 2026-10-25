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
| **Domain baseline** | FRD-TRADE FR-598…FR-601, FR-545 (customer part approval), FR-604, FR-680 (lost sale, `D-17` item 4), `TRD-10` · core `FR-257` (through `WhLostSalePort.captureLostSale`, `POS-T1-40`, over `WhInsufficientStockLogService`) |
| **Owning task body** | `issues/p9-08.md` |
| **Primary tables** | `wht_sales_enquiries`, `wht_sales_enquiry_lines`, `wht_customer_quotations`, `wht_customer_quotation_lines`, `wht_customer_quotation_charges` (`V550070`) |
| **Permission resources** | `wht_sales_enquiries:view/create/edit/export/cancel` · `wht_customer_quotations:view/create/edit/export/submit/approve/issue/cancel` |
| **Routes** | WS-298 `/warehouse/trade/sales/enquiries`, WS-299 `/quotations`, WS-300 `/win-loss` · mobile: none |
| **Contract status / version** | `derived` · `v1 — 2026-10-22` (R29 folded) |

**Fields.** Enquiry: `enquiry_number` (at save, series `ENQ`), company, customer, `customer_enquiry_ref`,
`customer_enquiry_date`, `source_code`, `quote_by_date`, `sales_exec_id`, `dispatch_warehouse_id`,
`status`, `regret_reason_code`, `outcome_at`. Line: item (nullable with `new_item_description` when the
plant has no item yet — such a line can be **regretted** at once (the *not catalogued* lost sale of `TSQ-T4-05`), and **quoted** only after an item exists, `TSQ-GRD-04`; R31 F-TR-010), customer part
no (FR-545), qty, UoM, required date, `target_price`, spec note, `line_outcome` (`OPEN`, `QUOTED`, `WON`,
`LOST`, `REGRETTED`), `regret_reason_code`, `lost_sale_log_id` (↓ `wh_insufficient_stock_log`, set once by `TSQ-T4-05`). Quotation:
`quotation_number` (series `SQ`, at submit; shared by all versions), `version_no`, `supersedes_id`,
`enquiry_id` (nullable), customer, `dispatch_warehouse_id` (NOT NULL; defaulted from the enquiry, else from `wht_customer_profiles.default_dispatch_warehouse_id`, editable while `DRAFT` — R31 F-TR-009; the site `TSQ-T4-05` records a lost sale against and the won SO's dispatch site), `quote_date`, `valid_until`, currency, payment / delivery / freight
terms, `terms_template_version_id`, `status`, `won_target_type` + `won_target_id`, `loss_reason_code`,
`competitor_name`, `competitor_price`, `sent_at`. Line: `enquiry_line_id`, item, customer part no, qty,
UoM, `unit_price`, `discount_percent`, `net_price`, `price_source`, `floor_price_at_quote`,
`lead_time_days`, `promised_date`, `is_free_of_charge`, `line_outcome` (`WON`/`LOST`, set at the outcome),
`loss_reason_code`, `competitor_name`, `competitor_price`, `lost_sale_log_id`. Charges (`wht_customer_quotation_charges`, the
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
| A9 | A line lost or regretted **for stock** records one core lost sale; any other reason records none (`WH-SC-597`, `-598`) | `TSQ-T4-05`, `TSQ-UNR-04` |

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

| ID | From | Action | To | Guard | Actor | Side effects | Comment | UI | Source |
|---|---|---|---|---|---|---|---|---|---|
| TSQ-T1-01 | — | Record enquiry | `OPEN` | `TSQ-GRD-01` | `wht_sales_enquiries:create` | number | no | WS-298 Add | FR-598 |
| TSQ-T1-02 | `OPEN`; `QUOTED` with lines still `OPEN` | Prepare quotation (for the open lines) | quotation v1 `DRAFT` | the lines are `OPEN` (not already on a live quotation) | `wht_customer_quotations:create` | lines copied; prices resolved `TRC-T4-04` | no | *Quote* / *Quote remaining* | FR-599 |
| TSQ-T1-03 | `OPEN` (whole), or `OPEN` / `QUOTED` (selected open lines) | Regret | enquiry `REGRETTED` (whole) / lines `REGRETTED` | — | `wht_sales_enquiries:edit` | print `REGRET_LETTER` (the lines regretted); `TSQ-T4-01` re-evaluates the header | **yes**, reason code | *Regret* / *Regret lines* | FR-598, FR-615 |
| TSQ-T1-04 | `DRAFT`, `REJECTED` | Submit | `SUBMITTED`; approved at once by `SYSTEM` only when the seeded zero-level `EXACT` `SQ` rule matches — i.e. the quotation carries **no** condition (`TAM-GRD-01`) | `TSQ-GRD-02`…`-04` | `:submit` | number at first submit; `TAM-T1-03` doc `SQ` with conditions `below_floor_price`, `discount_over_pct`, `manual_rate` | no | Submit | FR-599 |
| TSQ-T1-05 | `SUBMITTED` | Approved / rejected / returned | `APPROVED` / `REJECTED` / `DRAFT` | `TAM` | approver | maker notified | on reject/return | WS-285 | FR-551 |
| TSQ-T1-05a | `SUBMITTED` | Withdraw (`TAM-T1-09`) | `DRAFT` | no step acted | maker | — | no | *Withdraw* | FR-551 |
| TSQ-T1-06 | `APPROVED` | Send / print | `SENT` | template exists | `:issue` | print `CUSTOMER_QUOTATION`; `sent_at`; enquiry `QUOTED` | no | Send | FR-600, FR-615 |
| TSQ-T1-07 | `SENT` | Reprint | — | — | `:view` | reprint flagged | no | Print | FR-600 |
| TSQ-T1-08 | `SENT`, `EXPIRED` (latest) | Revise | new version `DRAFT`; old `REVISED` on the new one's send | latest version only | `:edit` | `supersedes_id` | no | *Revise* | FR-600 |
| TSQ-T1-09 | `SENT`, `EXPIRED` (latest) | Record outcome — at least one line won | `WON`; each line `WON` or `LOST` | `TSQ-GRD-05`, `-06`, `-07` | `:edit` | `TSQ-T4-01`, `-02` (won lines only) | loss reason on each lost line; customer PO date when `EXPIRED` | *Won* (per-line outcome; target picker: FIXED / OPEN / BLANKET SO / sales RC) | FR-601 |
| TSQ-T1-10 | `SENT`, `EXPIRED` (latest) | Mark lost (every line) | `LOST` | — | `:edit` | `TSQ-T4-01` | **yes**: loss reason; competitor + price optional | *Lost* | FR-601 |
| TSQ-T1-11 | `OPEN`, quotation `DRAFT` | Cancel | `CANCELLED` | — | `:cancel` | — | yes | row action | FR-598 |
| TSQ-T1-12 | Enquiry `QUOTED` | Close as lost (customer silent) | every line still `OPEN` / `QUOTED` → `LOST` (reason required); the latest live quotation `LOST`; header per `TSQ-T4-01` | no quotation `SUBMITTED` / `APPROVED` | `wht_sales_enquiries:edit` | — | **yes**, loss reason | *Close as lost* | FR-601 |

### 1.3 Guards

| ID | Predicate | Refusal | Source |
|---|---|---|---|
| TSQ-GRD-01 | Customer profile exists, not sales-blocked; ≥ 1 line | `422 TRADE_CUSTOMER_BLOCKED` | FR-543 |
| TSQ-GRD-02 | `requires_part_approval` ⇒ every line has a current `APPROVED` customer item reference | `422 TRADE_CUSTOMER_PART_NOT_APPROVED` | FR-545 |
| TSQ-GRD-03 | `valid_until ≥ quote_date` (default + `warehouse.trade.quotation.validity_days`); price ≥ 0 (0 only free-of-charge + reason); discount ∈ [0,100) | field `422` | FR-599 |
| TSQ-GRD-04 | Every **quotation** line has an `item_id` (a new-item enquiry line must be resolved to an item before it is quoted); regretting a new-item enquiry line (`TSQ-T1-03`) is not guarded by it (R31 F-TR-010) | `422 TRADE_ITEM_REQUIRED` | FR-598 |
| TSQ-GRD-05 | Only the latest version, status `SENT` or `EXPIRED`; `valid_until ≥ today`, or the customer's PO date ≤ `valid_until` recorded on the win (always required from `EXPIRED`) | `409 TRADE_QUOTATION_NOT_WINNABLE` | FR-600 |
| TSQ-GRD-06 | Customer not sales-blocked at win | `422 TRADE_CUSTOMER_BLOCKED` | FR-543 |
| TSQ-GRD-07 | The outcome records `WON` or `LOST` (+ reason) for **every** quotation line | field `422` per line | FR-601 |
| TSQ-GRD-08 | **Concurrency**: every edit, submit, transition and approval of a `wht_` document checks its optimistic `version`; a stale write changes nothing | `409 CONCURRENT_MODIFICATION` stale write (`TPR-OPEN-03`) | FR-618 |

### 1.4 Unreachable

| ID | Forbidden | Why | Source |
|---|---|---|---|
| TSQ-UNR-01 | Editing a `SENT` version | revise creates a version | FR-600 |
| TSQ-UNR-02 | Winning a superseded version | `TSQ-GRD-05` | FR-600 |
| TSQ-UNR-03 | An SO drafted from a quotation without a win | the SO draft is created only in `TSQ-T4-02` (or manually, unlinked) | FR-601 |
| TSQ-UNR-04 | A second lost sale for one line, or a lost sale for a non-stock reason | `TSQ-T4-05` runs only when `lost_sale_log_id` is null and the reason is in `warehouse.trade.sales.lost_sale_reason_codes`; the outcome is terminal per line | FR-680 |

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from | Source |
|---|---|---|---|---|
| TSQ-T2-01 | Enquiry add / edit / regret | `wht_sales_enquiries:create`/`edit` | `OPEN` | FR-598 |
| TSQ-T2-02 | Quotation add / edit | `wht_customer_quotations:create`/`edit` | `DRAFT`, `REJECTED` | FR-599 |
| TSQ-T2-03 | Submit / withdraw / approve | `:submit` / `:submit` (maker) / `:approve` | per T1 | FR-551 |
| TSQ-T2-04 | Send / print | `:issue` / `:view` | `APPROVED` / `SENT` | FR-615 |
| TSQ-T2-05 | Revise / won / lost | `:edit` | `SENT`, `EXPIRED` (latest) | FR-600, FR-601 |
| TSQ-T2-08 | Quote remaining / regret lines / close as lost | `wht_customer_quotations:create` / `wht_sales_enquiries:edit` | enquiry `QUOTED` | FR-598 |
| TSQ-T2-06 | Compare versions | `:view` | ≥ 2 versions | FR-600 |
| TSQ-T2-07 | Export | `:export` | — | FR-616 |
| TSQ-T2-09 | Every action in this table, and the auditor | `wht_<table>:<verb>` per FRD-TRADE FR-617 (`view`, `create`, `edit`, `export` + the workflow verbs above); `permission_dependencies` seeded; the auditor bundle holds `:view` only; record scope follows core's company / site grants; a bundle whose action calls a core port is also granted `warehouse:orders:port` in the trade seed | — | FR-617 |

## 3. T3 — Time-driven rules

| ID | Rule | Trigger | Changes | Notified | Job | Source |
|---|---|---|---|---|---|---|
| TSQ-T3-01 | Quote-by reminder | enquiry `OPEN` (or `QUOTED` with open lines) and `quote_by_date − 1` | none | sales exec, `TRADE_QUOTE_BY` | `TradeSalesJob` daily | FR-598 |
| TSQ-T3-02 | Quotation expiry | `SENT` and `valid_until < today` | `EXPIRED` (still revisable, winnable with PO-date evidence, losable) | sales exec, `TRADE_QUOTATION_EXPIRED` | same | FR-600 |
| TSQ-T3-03 | Follow-up nudge | `SENT` / `EXPIRED` for `warehouse.trade.quotation.followup_days` (default 7) with no outcome | none | sales exec, `TRADE_QUOTATION_FOLLOWUP` | same | FR-599 |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in | Source |
|---|---|---|---|---|
| TSQ-T4-01 | Line outcome recorded (won / lost / regretted / closed lost) | the enquiry line takes the quotation line's outcome; the header is `WON` when every line is `WON`, `PARTIALLY_WON` when every line has an outcome and at least one is `WON`, `LOST` / `REGRETTED` when every line is lost / regretted (`LOST` when mixed), else stays `QUOTED` | `QuotationService` | FR-601 |
| TSQ-T4-02 | Won | draft SO of the chosen type (or sales rate contract) prefilled with the **won lines only** — price (`price_source = QUOTATION`), terms, charges, customer PO no and date captured on the win modal; maker = the user who recorded the win | same transaction | FR-601 |
| TSQ-T4-03 | Enquiry regretted | open quotation drafts cancelled | same | FR-598 |
| TSQ-T4-04 | Version compare | backend diff of header + lines between any two versions | `QuotationVersionService` | FR-599 |
| TSQ-T4-05 | A line regretted (`TSQ-T1-03`) or recorded `LOST` (`TSQ-T1-09`, `-10`, `-12`) with a reason in `warehouse.trade.sales.lost_sale_reason_codes` (default `NO_STOCK`, `LEAD_TIME_NOT_MET`) | core **`WhLostSalePort.captureLostSale`**`(envelope(sourceModule 'warehouse-trade', idempotencyKey 'WHT_SALES_ENQUIRY:<enquiryId>:LOST_SALE_CAPTURE:<lineId>' / 'WHT_CUSTOMER_QUOTATION:<quotationId>:LOST_SALE_CAPTURE:<lineId>', actingUserId = the user recording the outcome), CaptureLostSaleCommand{ warehouseId = the enquiry's / quotation's `dispatch_warehouse_id`, itemId (null ⇒ itemDescription = new_item_description, *not catalogued*), ownerId = the house owner, requestedQuantity = the line qty in base UoM, lostSaleReasonCodeId = core reason `TRADE_STOCK_NOT_AVAILABLE` (context `SHORT_PICK`), sourceDocumentType `TRADE_ENQUIRY_LINE` / `TRADE_QUOTATION_LINE`, sourceDocumentId = line id, sourceDocumentRef = the enquiry / quotation number })` — the registered port of FRD-STORES R.2 (`POS-T1-40`, op `LOST_SALE_CAPTURE`; core records source type / id from these and the source system from the envelope; R31 F-TR-011), never the core service directly; the returned id is stored as `lost_sale_log_id` on the line (and on its enquiry line, so the two never capture twice). Core reads the available quantity itself and sets `is_lost_sale`, `captured_manually`, `policy_applied = BLOCK`. A core refusal (`403` site scope, `422 LOST_SALE_*`) rolls the outcome back and is relayed on the line (`TPO-T4-03` pattern) | same transaction | FR-680 |

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

## R32 additions (PRD 2026-10-24, `D-20`)

Rows added by the R32 fold (FRD-TRADE §4.15). Numbers continue each kind's sequence; where a number exists on one side of the purchase / sales mirror only, the asymmetry is stated in FRD-TRADE §5 rows M35…M40.

| ID | Kind | Rule | Refusal / effect | Source |
|---|---|---|---|---|
| TSQ-GRD-09 | guard | Enquiry has `customer_id` **or** prospect fields (`prospect_name` + mobile or e-mail, `prospect_state_code`); `lead_id` is a bare `leads-base` id, `lead_ref` frozen; no `dealer` / `leads` / `services` read | field `422` | FR-750 |
| TSQ-T1-13 | transition | Win of a prospect quotation: counterparty (`CUSTOMER`) + address + GSTIN + trade profile created through base's counterparty service, `customer_id` set on enquiry and quotation, then the SO draft (FR-601) | SO on a prospect `422 TRADE_PROSPECT_NEEDS_CUSTOMER` | FR-750 |
| TSQ-GRD-10 | guard | Enquiry line: `product_nature` (`STANDARD`/`CUSTOM`) required; `sample_needed`; model + variant axis values resolve to one SKU of the style × variant matrix or the line stays not-catalogued; attachments `WHT_SALES_ENQUIRY(_LINE)` | `422 TRADE_VARIANT_UNRESOLVED` | FR-751 |
| TSQ-GRD-11 | guard | Quotation submit: every `CUSTOM` line (all lines when `warehouse.trade.feasibility.required_for` = `ALL`) has an `APPROVED` feasibility review | `422 TRADE_FEASIBILITY_NOT_APPROVED {enquiryLineId}` | FR-771 |
| TSQ-T1-14 | transition | Feasibility review `DRAFT` → `SUBMITTED` → `APPROVED` / `REJECTED` (`FEASIBILITY`, `TAM-GRD-12`); an approved `NOT_FEASIBLE` offers *Regret* reason `NOT_FEASIBLE`; WS-314 lists lines without an approved review | — | FR-771 |
| TSQ-T4-06 | effect | *Request costing*: cost sheet lines from `WhPreSaleCostingProvider.estimate` (`CN-19`) or by hand; margin and suggested price computed in the backend; quotation line keeps `cost_sheet_id` | MFG absent → manual lines only | FR-772 |
| TSQ-GRD-12 | guard | Margin < `warehouse.trade.quotation.target_margin_pct` (15) sets `below_target_margin`; cost sheets need `wht_quotation_cost_sheets:view` | — | FR-772 |
| TSQ-GRD-13 | guard | With `warehouse.trade.sales.sample_approval_before_order` = true, a `sample_needed` line is won only once its MFG sample (`WhSampleRequestPort.status`) is customer-approved | `422 TRADE_SAMPLE_NOT_APPROVED` | FR-772 |
| TSQ-T4-07 | effect | Quotation line tax rows (`wht_customer_quotation_line_taxes`) at the ship-to state; frozen at approval; printed | `422 TRADE_TAX_CLASSIFICATION_MISSING {lineNo}` | FR-761, FR-762 |
| TSQ-T2-10 | action | Print `CUSTOMER_QUOTATION` with watermark: `DRAFT` / `SUPERSEDED` text on unapproved / superseded versions, the company watermark on approved ones | — | FR-760 |
| TSQ-T1-15 | transition | *Share* an approved / sent quotation or a regret letter by e-mail / WhatsApp (marks `SENT` as print does) | `422 TRADE_SHARE_DOCUMENT_NOT_APPROVED` | FR-763 |

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
| 2026-10-23 | every T1, guard, unreachable, T3 and T4 row | `Source` column added, filled from FRD-TRADE §4, so every rule traces to the FR it proves | R30 `CP-FR-008` |
| 2026-10-23 | §0, A9, `TSQ-UNR-04`, `TSQ-T4-05`, §8 | Lost sale from pre-sales: a line lost or regretted for stock calls core `captureLostSale` once (`D-17` item 4, FR-680) | R30 `CP-GA-003` |
| 2026-10-23 | §0 fields, `TSQ-GRD-04`, `-GRD-08`, `-T4-05`, every T2 row | R31: quotation `dispatch_warehouse_id` (F-TR-009); a not-catalogued line can be regretted (F-TR-010); lost sale through `WhLostSalePort.captureLostSale` with an envelope (F-TR-011, `CN-11`); stale-write code (`TPR-OPEN-03`); T2 Source FRs (F-TR-019) | R31 |
| 2026-10-25 | `TSQ-GRD-09`, `TSQ-T1-13`, `TSQ-GRD-10`, `TSQ-GRD-11`, `TSQ-T1-14`, `TSQ-T4-06`, `TSQ-GRD-12`, `TSQ-GRD-13`, `TSQ-T4-07`, `TSQ-T2-10`, `TSQ-T1-15` (new, *R32 additions*) | R32 fold of the client PRD (`D-20`): lead / prospect enquiry and conversion at win, model / variant / nature / sample flags, feasibility, pre-sale costing, sample gate, GST lines, watermark, share | R32 / `D-20` |

## 8. Invariants and scenarios

`WH-SC-486`, `WH-SC-520`, `WH-SC-521`, `WH-SC-550`…`WH-SC-554`, `WH-SC-582`, `WH-SC-583`, `WH-SC-585`, `WH-SC-597`, `WH-SC-598`. Core `WH-SC-283` (lost sales are demand) is reached through `TSQ-T4-05`.

## 9. Open rows

None beyond FRD-TRADE §10.
