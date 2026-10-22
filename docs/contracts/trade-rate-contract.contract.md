# Functional Contract — Rate contracts and price lists (purchase and sales), and price resolution

> **What this is.** The functional truth for agreed prices on both sides of `warehouse-trade`: the
> purchase rate contract per supplier, the sales rate contract per customer, the sales price list, their
> dated revisions, slabs, ceilings and expiry, and the two price-resolution services every order line
> uses. Both sides share one state machine; each row names the side when they differ.
>
> **Mirror.** FRD-TRADE §5 M13–M15. The generic purchase price list has no twin (M14, refusal R14).
>
> **Status.** Derived 2026-10-22 (v0). No code exists yet.

---

## 0. Identity

| | |
|---|---|
| **Workflow** | Draft → submit → approve → (active by date) → revise price by amendment (dated rows) → expire / terminate / supersede; resolution on every PO / SO / quotation / PR line |
| **Module** | `warehouse-trade` |
| **Domain baseline** | FRD-TRADE FR-570…FR-574, FR-602…FR-604, `TRD-10`, `OD-35`, `OD-36` · R27 `RM-006` · R28 `RN-030` (agreed rates live here, never on `whb_item_supplier_sources`) |
| **Owning task body** | `issues/p9-06.md` |
| **Primary tables** | Purchase: `wht_purchase_rate_contracts`, `_lines`, `_prices`, `_slabs`. Sales: `wht_sales_rate_contracts`, `_lines`, `_prices`, `_slabs`; `wht_price_lists`, `wht_price_list_categories`, `wht_price_list_prices`, `wht_price_list_slabs`. Shared amendment engine: `wht_rate_contract_amendments` (`contract_kind` `PRC`/`SRC`/`PL`), `wht_rate_contract_amendment_changes` (`V550050`) |
| **Permission resources** | `wht_purchase_rate_contracts:*` + `:submit` `:approve` `:amend` `:cancel` · `wht_sales_rate_contracts:*` (same verbs) · `wht_price_lists:*` (same verbs). An amendment (incl. termination) is drafted with `:amend`, submitted with `:submit` and approved with `:approve` through `TAM`; `:cancel` cancels only a `DRAFT` contract |
| **Routes** | WS-291 `/warehouse/trade/purchase/rate-contracts`, WS-302 `/warehouse/trade/sales/rate-contracts`, WS-301 `/warehouse/trade/sales/price-lists` · mobile: none |
| **Contract status / version** | `derived` · `v1 — 2026-10-22` (R29 folded) |

**Fields.** Header: `contract_number` (series `PRC` / `SRC` / `PL`, at submit), company, counterparty
(supplier or customer; none for a price list), `applicability` (price list: `ALL` or customer category
codes, junction `wht_price_list_categories`), `priority` (price list only, integer ≥ 1, 1 = first),
`valid_from`, `valid_to` (DATE, **inclusive**), `currency_code`, payment / delivery / freight terms
(recorded), `terms_template_version_id`, `status`, `terminates_on` (DATE) + `termination_reason_code`,
`superseded_on` + `superseded_by_id`, `supersedes_id`. Line: item, `uom_code`, `ceiling_quantity`
(nullable), `consumed_quantity` (maintained), `floor_price` (sales only), notes. Price row: `line_id`,
`effective_from`, `effective_to` (DATE, **exclusive**: the last valid day + 1 — so a contract valid to
2027-03-31 writes `effective_to = 2027-04-01`, and a termination on d writes `effective_to = d`),
`base_rate` `DECIMAL(19,6)`, `amendment_id`, and — set by trigger from the header and line so the constraint
can be declared — denormalised `company_id`, `counterparty_id` (price list: the applicability key), `item_id`,
`uom_code`, plus `is_effective` (true once the contract or the amendment that wrote the row is approved).
**`EXCLUDE USING gist (company_id WITH =, counterparty_id WITH =, item_id WITH =, uom_code WITH =,
daterange(effective_from, effective_to,'[)') WITH &&) WHERE (is_effective)`** on the purchase and sales
contract price rows; `btree_gist` is asserted (`V550000`). Slab: `price_id`, `from_quantity`, `rate` (per
order line qty, `OD-35`). Amendment: `amendment_number` (`<contract number>-Ann`), `contract_kind`,
`contract_id`, `reason_code`, `status` (`DRAFT`/`SUBMITTED`/`APPLIED`/`REJECTED`/`CANCELLED`),
`approval_request_id`; change rows `change_type` (`PRICE`, `VALIDITY_TO`, `ADD_LINE`, `CEILING`, `TERMS`,
`TERMINATE`), line, `effective_from`, `old_value`, `new_value`, `termination_date`.

### Acceptance checks

| # | Expects | Delivered by |
|---|---|---|
| A1 | Slab price, ceiling consumption (`WH-SC-515`) | `TRC-T4-01`, `-02` |
| A2 | No overlapping approved rate per supplier × item × UoM (`WH-SC-516`) | `TRC-GRD-02` |
| A3 | Revision is dated; approved orders keep their rate (`WH-SC-517`) | `TRC-T1-06`, `TRC-T4-03` |
| A4 | Manual override flagged for approval (`WH-SC-518`) | `TRC-T4-02` |
| A5 | Expiry alert; expired prices nothing (`WH-SC-519`) | `TRC-T3-01`, `-02` |
| A6 | Sales precedence customer RC → category PL → general PL → manual; floor (`WH-SC-520`, `-521`) | `TRC-T4-04` |
| A7 | UoM and currency mismatches (`WH-SC-522`, `-523`) | `TRC-T4-02` |
| A8 | Termination and supersession take effect on their date, through an approved amendment (`WH-SC-575`, `-571`) | `TRC-T1-07`, `-09`, `TRC-T3-04` |
| A9 | Price-list precedence is defined; equal-priority overlaps are refused (`WH-SC-590`) | `TRC-GRD-05`, `TRC-T4-04` |

## 1. T1 — State machine

### 1.1 Status inventory

| Status | Represented by | Reachable via | Exits via | Kind |
|---|---|---|---|---|
| `DRAFT` | `status` | `-01`, award target (`TRA-T4-03`), win target, return | `-02`, `-08` | initial |
| `SUBMITTED` | status | `-02` | `TAM` | active |
| `APPROVED` | status; `valid_from > today` reads as *Scheduled*; `terminates_on` / `superseded_on` set reads as *Ending on d* | `TAM` | `-05`, `-07`, `-09`, `TRC-T3-04` | active |
| *Active* | **derived**: `APPROVED` ∧ today ∈ validity ∧ today < `terminates_on` / `superseded_on` when set | — | — | derived |
| *Expired* | **derived**: `APPROVED` ∧ today > `valid_to` | — | `-05` (extension by amendment) | derived |
| `TERMINATED` | status, set **on** `terminates_on` | `TRC-T3-04` | none | terminal |
| `SUPERSEDED` | status, set **on** `superseded_on` | `TRC-T3-04` | none | terminal |
| Amendment | `DRAFT` → `SUBMITTED` → `APPLIED`; `REJECTED` (editable → `DRAFT`); `CANCELLED` | `-05`, `TAM` | — | — |
| `REJECTED` | status | `TAM` | edit → `DRAFT` | active |
| `CANCELLED` | status | `-08` | none | terminal |

### 1.2 Transitions

| ID | From | Action | To | Guard | Actor | Side effects | Comment | UI |
|---|---|---|---|---|---|---|---|---|
| TRC-T1-01 | — | Create | `DRAFT` | — | `:create` | — | no | Add |
| TRC-T1-02 | `DRAFT`/`REJECTED` | Submit | `SUBMITTED` | `TRC-GRD-01`, `-02` (pre-check) | `:submit` | number; `TAM-T1-03` doc type `PRC`/`SRC`/`PRICE_LIST`, value = Σ ceiling × rate if ceilings else quantity-free rule | no | Submit |
| TRC-T1-03 | `SUBMITTED` | Approved | `APPROVED` | `TRC-GRD-02` (DB `EXCLUDE` is the final word) | approver | price rows become effective | — | WS-285 |
| TRC-T1-04 | `SUBMITTED` | Rejected / returned | `REJECTED` / `DRAFT` | `TAM` | approver | — | yes | WS-285 |
| TRC-T1-05 | contract `APPROVED`, no other amendment open | Draft amendment (price revision, validity extension, add line, ceiling change, terms, termination) → submit | amendment `DRAFT` → `SUBMITTED` | `TRC-GRD-03` | `:amend`, then `:submit` | number at submit; `TAM-T1-03` doc `PRC_AMENDMENT` / `SRC_AMENDMENT` / `PRICE_LIST_AMENDMENT` (condition `termination` when it terminates; value = Σ ceiling × new rate, `TAM-GRD-09`) | reason code | row action *Amend* / *Terminate* |
| TRC-T1-05a | amendment `SUBMITTED` | Approved | `APPLIED` | `TRC-GRD-02`, `-03` re-checked; DB `EXCLUDE` | approver | new price row from `effective_from`, previous row's `effective_to` set to it; header fields updated; `contract_version` + 1 | — | WS-285 |
| TRC-T1-05b | amendment `SUBMITTED` | Rejected / returned | `REJECTED` / `DRAFT` | `TAM` | approver | nothing applied | yes | WS-285 |
| TRC-T1-06 | — | (alias) price revision = `-05` with only a `PRICE` change | — | — | — | — | — | — |
| TRC-T1-07 | amendment with `TERMINATE` `APPLIED` | Termination recorded | contract stays `APPROVED`, *Ending on d*; `terminates_on = d` | `termination_date ≥ today` | approver (via `-05a`) | every price row's `effective_to` = `min(effective_to, d)`; `TRC-T3-04` sets `TERMINATED` on d; orders with `price_basis = AGREEMENT` keep their rate; `AT_RELEASE` releases from d resolve no contract price (`TRC-T4-03`) | **yes** | — |
| TRC-T1-08 | `DRAFT` | Cancel | `CANCELLED` | — | `:cancel` | — | no | row action |
| TRC-T1-09 | `APPROVED` | A new contract for the same counterparty marked *supersedes* is approved | stays `APPROVED`, `superseded_on` = successor's `valid_from` | new `valid_from` ≥ today and ≤ old's `valid_to` + 1 day | system (in the successor's approval) | old price rows end on `superseded_on`; `TRC-T3-04` sets `SUPERSEDED` on that date | — | — |

### 1.3 Guards

| ID | Predicate | Refusal |
|---|---|---|
| TRC-GRD-01 | `valid_from ≤ valid_to`; ≥ 1 line; rate ≥ 0; slabs strictly increasing `from_quantity`, first slab from 0 or the line has a base rate; counterparty profile exists and is not blocked; currency set; price list applicability set | field `422` |
| TRC-GRD-02 | No approved price row of another contract overlaps for (company, counterparty, item, UoM) — service pre-check names the clashing contract; the `EXCLUDE` is the last word | `422 TRADE_RATE_OVERLAP {contractNumber}` |
| TRC-GRD-03 | Revision `effective_from ≥ today` (no retro price, `OD-36`); extension keeps `EXCLUDE`; ceiling ≥ consumed; one open amendment per contract; termination date ≥ today and ≤ `valid_to` | field `422` / `409 TRADE_AMENDMENT_OPEN` |
| TRC-GRD-04 | Purchase only: line item on AVL (FR-544) when the item has AVL rows | `TRADE_SUPPLIER_NOT_ON_AVL` |
| TRC-GRD-05 | Price list: no other effective price list of the same company, currency and **priority** whose applicability intersects (`ALL` intersects everything; categories intersect when they share one) prices the same item × UoM on an overlapping date range — service check at approval, under a lock on the company's price-list set | `422 TRADE_PRICE_LIST_OVERLAP {listCode}` |

### 1.4 Unreachable

| ID | Forbidden | Why |
|---|---|---|
| TRC-UNR-01 | Updating a price row's rate in place | rows are append-only by amendment |
| TRC-UNR-02 | A price column on `whb_item_supplier_sources` | `RN-030`, `FR-119` |
| TRC-UNR-03 | Pricing a line from an expired, terminated (on or after `terminates_on`), superseded, unapproved or other-currency contract | `TRC-T4-02` filters on the price row's date range |
| TRC-UNR-04 | A termination or supersession taking prices away before its date | price rows end on the date; the status flips only on the date (`TRD-15`) |

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from |
|---|---|---|---|
| TRC-T2-01 | Add / edit | `:create` / `:edit` | `DRAFT`, `REJECTED` |
| TRC-T2-02 | Submit | `:submit` | `DRAFT`, `REJECTED` |
| TRC-T2-03 | Approve | `:approve` | `SUBMITTED` |
| TRC-T2-04 | Draft amendment / termination; approve it | `:amend` + `:submit` / `:approve` (`TAM`) | contract `APPROVED` |
| TRC-T2-05 | Import price rows (CSV, dry-run then apply; only into a `DRAFT` or an amendment) | `:edit` | `DRAFT`, amendment `DRAFT` |
| TRC-T2-06 | Export | `:export` | — |

## 3. T3 — Time-driven rules

| ID | Rule | Trigger | Changes | Notified | Job |
|---|---|---|---|---|---|
| TRC-T3-01 | Expiry alert | `valid_to − warehouse.trade.contract.expiry_alert_days` (default 30) | `expiry_alert_sent_at` | contract owner (buyer / sales exec), `TRADE_CONTRACT_EXPIRING` | `TradeContractJob` daily, notify once |
| TRC-T3-02 | Expiry | `valid_to < today` | none — *Expired* is derived | — | — |
| TRC-T3-03 | Ceiling alert | consumed ≥ 90 % of ceiling | none | owner, `TRADE_CONTRACT_CEILING` | same job, once per threshold |
| TRC-T3-04 | Dated end | today ≥ `terminates_on` / `superseded_on` | status `TERMINATED` / `SUPERSEDED` | owner, `TRADE_CONTRACT_ENDED` | same job, once |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in |
|---|---|---|---|
| TRC-T4-01 | A FIXED / BLANKET PO or SO line, or an OPEN release / dispatch release, is **approved** pricing from a contract line | `consumed_quantity` += line qty (release qty for OPEN; the agreed line qty for BLANKET at order approval); on cancel, release cancel or reject-revert, short-close or amendment decrease it is reduced. Refused if it would exceed the ceiling (`422 TRADE_CEILING_EXCEEDED`) | `RateContractConsumptionService`, row lock on the contract line |
| TRC-T4-02 | **Purchase resolution** `resolve(company, supplier, item, uom, qty, date, currency)` | 1 the approved contract price row with `is_effective` and `effective_from ≤ date < effective_to` (same currency; UoM via `whb_uom_conversions`, factor frozen on the order line; no conversion → contract skipped with reason) → slab for `qty` → `price_source = RATE_CONTRACT`; else 2 latest awarded valid quotation of that supplier → `QUOTATION`; else 3 none → caller requires manual entry → `MANUAL` + `manual_rate` condition. Returns last approved PO rate as a separate reference field | `PurchasePriceResolutionService` |
| TRC-T4-03 | Revision approved, or a release priced `AT_RELEASE` | approved orders untouched; OPEN/BLANKET with `price_basis = AT_RELEASE` price each new release on its release date (that price travels to core on the release's schedule line, `TPO-T4-02`); `AGREEMENT` keeps the order rate; when no contract price resolves on the release date (expired, terminated, superseded), the release needs a manual price and carries `release_price_manual` | release service calls resolution with the release date |
| TRC-T4-04 | **Sales resolution** `resolve(company, customer, item, uom, qty, date, currency)` | customer contract → price lists whose applicability includes the customer's category, lowest `priority` first → general (`ALL`) price lists, lowest `priority` first → manual; `below_floor_price` when net < floor (from the contract line, else the price list that priced it) | `SalesPriceResolutionService` |

## 5. T5 — Screen contract

WS-291 / WS-302 / WS-301 (reference **Service Vehicle**). Grids `wht_purchase_rate_contracts`,
`wht_sales_rate_contracts`, `wht_price_lists`; scopes `WAREHOUSE_TRADE_PURCHASE_RATE_CONTRACT`,
`WAREHOUSE_TRADE_SALES_RATE_CONTRACT`, `WAREHOUSE_TRADE_PRICE_LIST`. Tiles: draft, submitted, active,
expiring ≤ 30 days, expired. Columns: `contractNumber`, `counterpartyName` (none on price list;
`applicability` instead), `validFrom`, `validTo` (date-only), `currencyCode`, `lineCount`,
`ceilingConsumedPct`, `status` (with derived *Active / Expired / Scheduled*), audit. Filters:
counterparty typeahead, `itemId`, `status`, `currencyCode`, `activeOn` (`DatePicker`), `expiringOnly`.
Price lists add `priority` and `applicability` columns and filters. Row actions: View · Edit · Submit · Amend
· Terminate (opens an amendment with `TERMINATE`) · Withdraw · Price history · Import prices · Print. Detail
tabs: Lines · Price history (dated rows, never edited) · Consumption (orders that used it) · Amendments ·
Approvals. Empty state: *No contracts yet.* Export ⊇ grid incl. `createdByName` / `updatedByName`.

## 6. Out of scope

| Item | Decision |
|---|---|
| Cumulative / retroactive slabs, rebates | `OD-35`; accounting |
| Value contracts (target value without lines) | not built v1: every contract is item-lined; re-entry as a header `ceiling_value` |
| Price escalation formulas (index-linked, e.g. steel price index) | not built v1; revision by amendment is the mechanism |

## 7. Amendments

| Date | Rows | Change | Found by |
|---|---|---|---|
| 2026-10-22 | all | v0 derived | TRADE author |
| 2026-10-22 | §0 fields, §1.1, `TRC-T1-05`…`-09`, `TRC-GRD-03`, `-05`, `TRC-UNR-03`, `-04`, T2-04, `TRC-T3-04`, `TRC-T4-01`…`-04`, §5 | R29 TP-F14, F20, TS-F17, F22, F23 and contract quality: amendment and termination ladder with approval doc types, dated termination and supersession, `AT_RELEASE` after the end, SO release consumption, price-list priority, inclusive validity vs exclusive price-row end, the task's `is_effective` form | R29 |

## 8. Invariants and scenarios

`WH-SC-515`…`WH-SC-523`, `WH-SC-571`, `WH-SC-575`, `WH-SC-588`, `WH-SC-590`.

## 9. Open rows

`OD-35`, `OD-36` (FRD-TRADE §10).
