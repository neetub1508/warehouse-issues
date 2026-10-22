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
| **Primary tables** | Purchase: `wht_purchase_rate_contracts`, `_lines`, `_prices`, `_slabs`. Sales: `wht_sales_rate_contracts`, `_lines`, `_prices`, `_slabs`; `wht_price_lists`, `wht_price_list_prices`, `wht_price_list_slabs` (`V550050`) |
| **Permission resources** | `wht_purchase_rate_contracts:*` + `:submit` `:approve` `:amend` `:cancel` · `wht_sales_rate_contracts:*` (same verbs) · `wht_price_lists:*` (same verbs) |
| **Routes** | WS-291 `/warehouse/trade/purchase/rate-contracts`, WS-302 `/warehouse/trade/sales/rate-contracts`, WS-301 `/warehouse/trade/sales/price-lists` · mobile: none |
| **Contract status / version** | `derived` · `v0 — 2026-10-22` |

**Fields.** Header: `contract_number` (series `PRC` / `SRC` / `PL`, at submit), company, counterparty
(supplier or customer; none for a price list), `applicability` (price list: `ALL` or customer category
codes, junction `wht_price_list_categories`), `valid_from`, `valid_to` (DATE), `currency_code`,
payment / delivery / freight terms (recorded), `terms_template_version_id`, `status`, `terminated_at`,
`termination_reason_code`. Line: item, `uom_code`, `ceiling_quantity` (nullable), `consumed_quantity`
(maintained), `floor_price` (sales only), notes. Price row: `line_id`, `effective_from`, `effective_to`
(DATE, half-open), `base_rate` `DECIMAL(19,6)`, `amendment_id`; **`EXCLUDE USING gist (company_id WITH =,
counterparty_id WITH =, item_id WITH =, uom_code WITH =, daterange(effective_from, effective_to,'[)') WITH
&&) WHERE (status_active)`** across the contract's approved price rows — the migration declares
`btree_gist` and fails loudly if absent. Slab: `price_id`, `from_quantity`, `rate` (per order line qty,
`OD-35`).

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

## 1. T1 — State machine

### 1.1 Status inventory

| Status | Represented by | Reachable via | Exits via | Kind |
|---|---|---|---|---|
| `DRAFT` | `status` | `-01`, award target (`TRA-T4-03`), win target, return | `-02`, `-08` | initial |
| `SUBMITTED` | status | `-02` | `TAM` | active |
| `APPROVED` | status; `valid_from > today` reads as *Scheduled* | `TAM` | `-06`, `-07` | active |
| *Active* | **derived**: `APPROVED` ∧ today ∈ validity | — | — | derived |
| *Expired* | **derived**: `APPROVED` ∧ today > `valid_to` | — | `-05` (extension by amendment) | derived |
| `TERMINATED` | status | `-07` | none | terminal |
| `SUPERSEDED` | status | `-09` | none | terminal |
| `REJECTED` | status | `TAM` | edit → `DRAFT` | active |
| `CANCELLED` | status | `-08` | none | terminal |

### 1.2 Transitions

| ID | From | Action | To | Guard | Actor | Side effects | Comment | UI |
|---|---|---|---|---|---|---|---|---|
| TRC-T1-01 | — | Create | `DRAFT` | — | `:create` | — | no | Add |
| TRC-T1-02 | `DRAFT`/`REJECTED` | Submit | `SUBMITTED` | `TRC-GRD-01`, `-02` (pre-check) | `:submit` | number; `TAM-T1-03` doc type `PRC`/`SRC`/`PRICE_LIST`, value = Σ ceiling × rate if ceilings else quantity-free rule | no | Submit |
| TRC-T1-03 | `SUBMITTED` | Approved | `APPROVED` | `TRC-GRD-02` (DB `EXCLUDE` is the final word) | approver | price rows become effective | — | WS-285 |
| TRC-T1-04 | `SUBMITTED` | Rejected / returned | `REJECTED` / `DRAFT` | `TAM` | approver | — | yes | WS-285 |
| TRC-T1-05 | `APPROVED` | Amend (price revision, validity extension, add line, ceiling change, terms) | amendment `DRAFT` → approved | `TRC-GRD-03` | `:amend` | on approval: new price row from `effective_from`, previous row's `effective_to` set to it; header fields updated; `contract_version` + 1 | reason code | row action *Amend* |
| TRC-T1-06 | — | (alias) price revision = `-05` with only a price change | — | — | — | — | — | — |
| TRC-T1-07 | `APPROVED` | Terminate | `TERMINATED` | `termination_date ≥ today`; approval `PRC`/`SRC` termination condition | `:cancel` | price rows end at termination date; open OPEN/BLANKET orders priced from it keep their agreement rate | **yes** | row action |
| TRC-T1-08 | `DRAFT` | Cancel | `CANCELLED` | — | `:cancel` | — | no | row action |
| TRC-T1-09 | `APPROVED` | A new contract for the same counterparty marked *supersedes* is approved | `SUPERSEDED` | new `valid_from` = old's end + 1 day or later | system | — | — | — |

### 1.3 Guards

| ID | Predicate | Refusal |
|---|---|---|
| TRC-GRD-01 | `valid_from ≤ valid_to`; ≥ 1 line; rate ≥ 0; slabs strictly increasing `from_quantity`, first slab from 0 or the line has a base rate; counterparty profile exists and is not blocked; currency set; price list applicability set | field `422` |
| TRC-GRD-02 | No approved price row of another contract overlaps for (company, counterparty, item, UoM) — service pre-check names the clashing contract; the `EXCLUDE` is the last word | `422 TRADE_RATE_OVERLAP {contractNumber}` |
| TRC-GRD-03 | Revision `effective_from ≥ today` (no retro price, `OD-36`); extension keeps `EXCLUDE`; ceiling ≥ consumed | field `422` |
| TRC-GRD-04 | Purchase only: line item on AVL (FR-544) when the item has AVL rows | `TRADE_SUPPLIER_NOT_ON_AVL` |

### 1.4 Unreachable

| ID | Forbidden | Why |
|---|---|---|
| TRC-UNR-01 | Updating a price row's rate in place | rows are append-only by amendment |
| TRC-UNR-02 | A price column on `whb_item_supplier_sources` | `RN-030`, `FR-119` |
| TRC-UNR-03 | Pricing a line from an expired, terminated, unapproved or other-currency contract | `TRC-T4-02` filters |

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from |
|---|---|---|---|
| TRC-T2-01 | Add / edit | `:create` / `:edit` | `DRAFT`, `REJECTED` |
| TRC-T2-02 | Submit | `:submit` | `DRAFT`, `REJECTED` |
| TRC-T2-03 | Approve | `:approve` | `SUBMITTED` |
| TRC-T2-04 | Amend / terminate | `:amend` / `:cancel` | `APPROVED` |
| TRC-T2-05 | Import price rows (CSV, dry-run then apply; only into a `DRAFT` or an amendment) | `:edit` | `DRAFT`, amendment `DRAFT` |
| TRC-T2-06 | Export | `:export` | — |

## 3. T3 — Time-driven rules

| ID | Rule | Trigger | Changes | Notified | Job |
|---|---|---|---|---|---|
| TRC-T3-01 | Expiry alert | `valid_to − warehouse.trade.contract.expiry_alert_days` (default 30) | `expiry_alert_sent_at` | contract owner (buyer / sales exec) | `TradeContractJob` daily, notify once |
| TRC-T3-02 | Expiry | `valid_to < today` | none — *Expired* is derived | — | — |
| TRC-T3-03 | Ceiling alert | consumed ≥ 90 % of ceiling | none | owner | same job, once per threshold |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in |
|---|---|---|---|
| TRC-T4-01 | A PO / SO line (or release) is **approved** pricing from a contract line | `consumed_quantity` += line qty (release qty for OPEN/BLANKET); on cancel / short-close / amendment decrease it is reduced. Refused if it would exceed the ceiling (`422 TRADE_CEILING_EXCEEDED`) | `RateContractConsumptionService`, row lock on the contract line |
| TRC-T4-02 | **Purchase resolution** `resolve(company, supplier, item, uom, qty, date, currency)` | 1 approved active contract price row on `date` (same currency; UoM via `whb_uom_conversions`, factor frozen on the order line; no conversion → contract skipped with reason) → slab for `qty` → `price_source = RATE_CONTRACT`; else 2 latest awarded valid quotation of that supplier → `QUOTATION`; else 3 none → caller requires manual entry → `MANUAL` + `manual_rate` condition. Returns last approved PO rate as a separate reference field | `PurchasePriceResolutionService` |
| TRC-T4-03 | Revision approved | approved orders untouched; OPEN/BLANKET with `price_basis = AT_RELEASE` price each new release on its release date; `AGREEMENT` keeps the order rate | release service calls resolution with the release date |
| TRC-T4-04 | **Sales resolution** `resolve(company, customer, item, uom, qty, date, currency)` | customer contract → price list whose applicability includes the customer's category → general (`ALL`) price list → manual; `below_floor_price` when net < floor (from the contract line, else the price list) | `SalesPriceResolutionService` |

## 5. T5 — Screen contract

WS-291 / WS-302 / WS-301 (reference **Service Vehicle**). Grids `wht_purchase_rate_contracts`,
`wht_sales_rate_contracts`, `wht_price_lists`; scopes `WAREHOUSE_TRADE_PURCHASE_RATE_CONTRACT`,
`WAREHOUSE_TRADE_SALES_RATE_CONTRACT`, `WAREHOUSE_TRADE_PRICE_LIST`. Tiles: draft, submitted, active,
expiring ≤ 30 days, expired. Columns: `contractNumber`, `counterpartyName` (none on price list;
`applicability` instead), `validFrom`, `validTo` (date-only), `currencyCode`, `lineCount`,
`ceilingConsumedPct`, `status` (with derived *Active / Expired / Scheduled*), audit. Filters:
counterparty typeahead, `itemId`, `status`, `activeOn` (`DatePicker`), `expiringOnly`. Row actions: View ·
Edit · Submit · Amend · Terminate · Price history · Import prices · Print. Detail tabs: Lines · Price
history (dated rows, never edited) · Consumption (orders that used it) · Amendments · Approvals.

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

## 8. Invariants and scenarios

`WH-SC-515`…`WH-SC-523`.

## 9. Open rows

`OD-35`, `OD-36` (FRD-TRADE §10).
