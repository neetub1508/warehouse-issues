# Functional Contract — RFQ → vendor quotation → comparative statement → award

> **What this is.** The functional truth for sourcing in `warehouse-trade`: issuing an RFQ to several
> suppliers, capturing their quotations (versioned), preparing the comparative statement with L1 ranking,
> recommending and approving the award, and drafting the award target (FIXED PO, OPEN PO, BLANKET
> agreement or rate contract). Approval cites `TAM-*`.
>
> **Sales twin.** Customer quotation + win/loss ([trade-sales-enquiry-quotation](trade-sales-enquiry-quotation.contract.md));
> FRD-TRADE §5 M7–M12. Sealed mode has no twin (M9).
>
> **Status.** Derived 2026-10-22 (v0). No code exists yet.

---

## 0. Identity

| | |
|---|---|
| **Workflow** | RFQ draft → issue (per-supplier prints) → responses / declines → close bids → vendor quotations (versions) → comparative statement → recommendation (split, reasons) → award approval → award targets drafted → RFQ closed |
| **Module** | `warehouse-trade` |
| **Domain baseline** | FRD-TRADE FR-562…FR-569, FR-544 (AVL), FR-597 (grade), `OD-34`, `OD-37` · R27 `RM-002` |
| **Owning task body** | `issues/p9-05.md` |
| **Primary tables** | `wht_rfqs`, `wht_rfq_lines`, `wht_rfq_suppliers`, `wht_vendor_quotations`, `wht_vendor_quotation_lines`, `wht_vendor_quotation_charges`, `wht_comparative_statements`, `wht_comparative_statement_awards` (`V550040`) |
| **Permission resources** | `wht_rfqs:view/create/edit/export/issue/cancel` · `wht_vendor_quotations:view/create/edit/export` · `wht_comparative_statements:view/create/edit/export/submit/approve` (the award is approved by `:approve`; no separate `:award` verb) |
| **Routes** | WS-288 `/warehouse/trade/purchase/rfqs`, WS-289 `/vendor-quotations`, WS-290 `/comparative-statements` (+ `/[id]`) · mobile: none |
| **Contract status / version** | `derived` · `v1 — 2026-10-22` (R29 folded) |

**Fields.** RFQ: `rfq_number` (at issue, series `RFQ`), company, `warehouse_id` (deliver-to), `buyer_id`,
`issue_date`, `response_due_date`, `currency_code` (requested), `terms_template_version_id`,
`limited_source_reason_code` + `limited_source_note`, `status`. RFQ line: item, qty, UoM, required date,
specification note. RFQ supplier: `supplier_counterparty_id`, `sent_at`, `channel_code`,
`response_status`, `decline_reason_code`, `avl_warning` (stored when enforcement = WARN). Vendor
quotation: `vq_number` (at capture, series `VQ`), `rfq_id` (nullable = unsolicited), supplier,
`supplier_quote_ref`, `quote_date`, `valid_until`, `currency_code`, payment/delivery/freight terms,
`version_no`, `supersedes_id`, `status`. Line: `rfq_line_id` (nullable), item, `is_alternative`,
`offered_quantity`, `unit_price`, `discount_percent` [0,100), `moq`, `lead_time_days`,
`is_free_of_charge` + reason, remarks. Charges: `charge_type_code`, amount, allocation basis
(`VALUE`/`QUANTITY`). CS: `cs_number` (at submit), `rfq_id`, `currency_code` (one statement per RFQ × currency,
partial uk among statements not `REJECTED`), `status`, `prepared_by`, `is_stale`; award rows:
`rfq_line_id`, `vendor_quotation_line_id`, `rank` (computed), `awarded_quantity`, `award_target_type`
(`FIXED_PO`/`OPEN_PO`/`BLANKET`/`RATE_CONTRACT`), `award_reason_code` + note, `target_document_id`.

### Acceptance checks

| # | Expects | Delivered by |
|---|---|---|
| A1 | Minimum invitees or a limited-source reason; AVL / block checks on invite (`WH-SC-485`, `-505`) | `TRA-GRD-01`, `-02` |
| A2 | Per-supplier RFQ prints; response tracking (`WH-SC-505`, `-506`) | `TRA-T1-03`, `-05` |
| A3 | Quotation versions; alternatives never ranked as the asked item (`WH-SC-507`, `-508`) | `TRA-T1-07`, `TRA-GRD-05` |
| A4 | Sealed mode hides prices until due (`WH-SC-509`) | `TRA-GRD-06` |
| A5 | Backend L1 on landed price ex-tax (`WH-SC-510`) | `TRA-T4-01` |
| A6 | Non-L1 needs reason; split ≤ RFQ qty; expired quote not awardable (`WH-SC-511`, `-512`, `-514`) | `TRA-GRD-07`…`-09` |
| A7 | Award drafts targets and moves PR allocations (`WH-SC-513`) | `TRA-T4-03`, `-04` |
| A8 | A rejected statement or a stalled RFQ always has an exit (`WH-SC-566`) | `TRA-T1-04`, `-13`, `-14` |
| A9 | A statement awards in one currency only (`WH-SC-573`) | `TRA-GRD-10` |
| A10 | An expired quotation can be extended and the pending award refreshed (`WH-SC-514`) | `TRA-T1-08`, `TAM-T1-08a` |

## 1. T1 — State machine

### 1.1 Status inventory

| Entity | Status | Reachable via | Exits via | Kind |
|---|---|---|---|---|
| RFQ | `DRAFT` | `-01` | `-03`, `-04` | initial |
| RFQ | `ISSUED` | `-03` | `-05`, `-04` | active |
| RFQ | `BIDS_CLOSED` | `-05` (the buyer's act only: the due date never closes bids, `TRA-T3-02` only notifies; `NO_RESPONSE` is set at `-05`, R31 F-TR-023), `-13`, `-14` | `-10`, `-04` | active |
| RFQ | `EVALUATION` | CS submitted | award outcome, `-13`, `-14`, `-04` (no CS `SUBMITTED`) | active |
| RFQ | `AWARDED` / `PARTIALLY_AWARDED` | `TRA-T4-04` | `-12` | active |
| RFQ | `NOT_AWARDED` | CS approved awarding nothing | none | terminal |
| RFQ | `CLOSED` | `-12` | none | terminal |
| RFQ | `CANCELLED` | `-04` | none | terminal |
| Invitee | `INVITED` → `RESPONDED` / `DECLINED` / `NO_RESPONSE` | `-05`, `-06`, `-08` | — | — |
| VQ | `DRAFT` → `SUBMITTED`; `REVISED` (superseded), `WITHDRAWN`, `EXPIRED` (revisable, `-08`), `AWARDED`, `PARTIALLY_AWARDED`, `NOT_AWARDED` | `-07`, `-08`, `-09`, T3, T4 | — | — |
| CS | `DRAFT` → `SUBMITTED` → `APPROVED`; `REJECTED` (terminal, `-13`); `DRAFT` on return (`-14`) or input change (`TAM-T1-08a`) | `-10`, `-11`, `TAM` | — | — |

### 1.2 Transitions

| ID | From | Action | To | Guard | Actor | Side effects | Comment | UI | Source |
|---|---|---|---|---|---|---|---|---|---|
| TRA-T1-01 | — | Create RFQ (manual or from WS-287) | `DRAFT` | — | `wht_rfqs:create` | PR allocations (`TPR-T1-06`) | no | WS-288 Add | FR-559, FR-562 |
| TRA-T1-02 | `DRAFT` | Add / remove invitee | invitee rows | `TRA-GRD-02` | `:edit` | AVL warning stored if WARN | no | RFQ modal tab *Suppliers* | FR-562 |
| TRA-T1-03 | `DRAFT` | Issue | `ISSUED` | `TRA-GRD-01`, `-02`, `-03` | `wht_rfqs:issue` | number; one print job per invitee (`RFQ` template, own name only); `sent_at` | no | Issue | FR-562, FR-563 |
| TRA-T1-04 | `DRAFT`, `ISSUED`, `BIDS_CLOSED`, `EVALUATION` | Cancel | `CANCELLED` | no CS `SUBMITTED` (withdraw it first, `TAM-T1-09`); `DRAFT` statements are cancelled with it | `:cancel` | PR allocations released (`TPR-T1-07`); invitees notified (print *RFQ cancelled*) | **yes**, reason code | row action | FR-562 |
| TRA-T1-05 | `ISSUED` | Close bids | `BIDS_CLOSED` | — | `:issue` | invitees still `INVITED` → `NO_RESPONSE` | no | row action | FR-563 |
| TRA-T1-06 | invitee `INVITED` | Record decline | `DECLINED` | — | `:edit` | — | reason code | Suppliers tab | FR-563 |
| TRA-T1-07 | — | Capture quotation (against RFQ or unsolicited) | VQ `DRAFT` → `SUBMITTED` | `TRA-GRD-04`, `-05` | `wht_vendor_quotations:create` | number; invitee `RESPONDED` | no | WS-289 Add / RFQ *Capture response* | FR-564 |
| TRA-T1-08 | VQ `SUBMITTED`, `EXPIRED` | Revise (incl. a validity extension) | new version `SUBMITTED`; old `REVISED` | RFQ not `CLOSED`/`CANCELLED`; not after award approved for that line | `:edit` | `supersedes_id`; a `DRAFT` statement using it is flagged stale (`TRA-T4-02`); a `SUBMITTED` one has its request returned by `TAM-T1-08a` and goes back to `DRAFT`, stale | no | *Revise* | FR-564, FR-569 |
| TRA-T1-09 | VQ `SUBMITTED` | Withdraw | `WITHDRAWN` | not awarded | `:edit` | removed from CS | yes | row action | FR-564 |
| TRA-T1-10 | RFQ `BIDS_CLOSED` (or `ISSUED` when all invitees answered, or `EVALUATION` for another currency) | Prepare CS for a currency | CS `DRAFT` | `TRA-GRD-06`; no other non-rejected CS for the RFQ × currency | `wht_comparative_statements:create` | matrix computed (`TRA-T4-01`); preparer recorded as `prepared_by` | no | WS-290 *Prepare* (currency picker) | FR-566 |
| TRA-T1-11 | CS `DRAFT` | Recommend + submit | `SUBMITTED`; RFQ `EVALUATION` | `TRA-GRD-07`…`-10`; not stale (`TRA-T4-02`) | `:submit` | `TAM-T1-03` value Σ awarded × landed price in the statement's currency, conditions `non_l1_award` when any | reason on non-L1 | WS-290 detail | FR-567 |
| TRA-T1-12 | RFQ `AWARDED`/`PARTIALLY_AWARDED` | Every award target past `DRAFT` or deleted | `CLOSED` | — | system | — | — | — | FR-568 |
| TRA-T1-13 | CS `SUBMITTED` | Rejected (`TAM-T1-07`) | CS `REJECTED`; RFQ → `BIDS_CLOSED` when no other statement of it is `SUBMITTED`/`APPROVED` | — | approver | award rows void; a new statement for the currency may be prepared (`-10`) | **yes** | WS-285 | FR-551 |
| TRA-T1-14 | CS `SUBMITTED` | Returned (`TAM-T1-08`, `-08a`) | CS `DRAFT`; RFQ → `BIDS_CLOSED` under the same rule | — | approver / system | award rows kept for editing | **yes** | WS-285 | FR-551, FR-569 |

### 1.3 Guards

| ID | Predicate | Refusal | Source |
|---|---|---|---|
| TRA-GRD-01 | invitees ≥ `warehouse.trade.rfq.min_suppliers` ∨ limited-source reason + note; `response_due_date ≥ issue_date`; ≥ 1 line | field `422` | FR-562 |
| TRA-GRD-02 | Invitee has a supplier profile, not purchase-blocked; for each RFQ item with any AVL row: status `APPROVED`/`PROVISIONAL` on the date, else REFUSE (or WARN per setting); `SUSPENDED`/`DISQUALIFIED` always refused | `422 TRADE_SUPPLIER_BLOCKED` / `TRADE_SUPPLIER_NOT_ON_AVL` | FR-544 |
| TRA-GRD-03 | Print templates exist for kind `RFQ` | `422 TRADE_TEMPLATE_MISSING` | FR-563, FR-615 |
| TRA-GRD-04 | `valid_until ≥ quote_date`; price ≥ 0; price = 0 only with free-of-charge reason; discount ∈ [0,100); offered UoM convertible to RFQ UoM | field `422` | FR-564 |
| TRA-GRD-05 | A line with an item ≠ RFQ line item is `is_alternative = true` | `422` on `isAlternative` | FR-564 |
| TRA-GRD-06 | Sealed mode on ⇒ RFQ `BIDS_CLOSED` or due date passed; prices hidden in reads for everyone but the capturer until then | `409 TRADE_RFQ_SEALED` | FR-565 |
| TRA-GRD-07 | Σ awarded per RFQ line over **every** non-rejected statement of the RFQ ≤ RFQ line qty; awarded ≤ offered qty; awarded ≥ MOQ unless note | `422 TRADE_AWARD_EXCEEDS_RFQ_QTY` | FR-567 |
| TRA-GRD-08 | Award to a rank ≠ 1 ⇒ `award_reason_code` + note; alternative-item award ⇒ reason | field `422` | FR-567 |
| TRA-GRD-09 | At approval: each awarded quotation `valid_until ≥ today`; supplier still not blocked; AVL still valid | `422 TRADE_QUOTATION_EXPIRED` / blocked | FR-569 |
| TRA-GRD-10 | Every awarded quotation line is in the statement's currency (other-currency quotations are shown unranked and awardable only on their own currency's statement) | `422 TRADE_CS_MIXED_CURRENCY` | FR-566 |
| TRA-GRD-11 | **Concurrency**: every edit, submit, transition and approval of a `wht_` document checks its optimistic `version`; a stale write changes nothing | `409 CONCURRENT_MODIFICATION` stale write (`TPR-OPEN-03`) | FR-618 |

### 1.4 Unreachable

| ID | Forbidden | Why | Source |
|---|---|---|---|
| TRA-UNR-01 | An RFQ print showing another supplier's name or price | per-invitee render; template data contains one invitee | FR-563 |
| TRA-UNR-02 | Ranking across currencies | `OD-34`: foreign-currency quotations shown unranked | FR-566 |
| TRA-UNR-03 | Editing a `SUBMITTED` quotation in place | revise creates a version | FR-564 |
| TRA-UNR-04 | An award target created without CS approval | targets are drafted only in the `onApproved` callback | FR-568 |

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from | Source |
|---|---|---|---|---|
| TRA-T2-01 | Edit RFQ / invitees | `wht_rfqs:edit` | `DRAFT` | FR-562 |
| TRA-T2-02 | Issue / close bids | `wht_rfqs:issue` | `DRAFT` / `ISSUED` | FR-562, FR-563 |
| TRA-T2-03 | Cancel | `wht_rfqs:cancel` | `DRAFT`, `ISSUED`, `BIDS_CLOSED`, `EVALUATION` (no CS `SUBMITTED`, as `TRA-T1-04`; R31 F-TR-018) | FR-562 |
| TRA-T2-04 | Capture / revise / withdraw quotation | `wht_vendor_quotations:create`/`edit` | RFQ `ISSUED`/`BIDS_CLOSED` (revise up to award) | FR-564 |
| TRA-T2-05 | Prepare / edit / submit CS | `wht_comparative_statements:create`/`edit`/`submit` | per T1 | FR-566 |
| TRA-T2-06 | Approve award | `wht_comparative_statements:approve` via `TAM` | CS `SUBMITTED` | FR-567 |
| TRA-T2-07 | Print RFQ, CS | `:view` | issued / submitted | FR-615 |
| TRA-T2-08 | Every action in this table, and the auditor | `wht_<table>:<verb>` per FRD-TRADE FR-617 (`view`, `create`, `edit`, `export` + the workflow verbs above); `permission_dependencies` seeded; the auditor bundle holds `:view` only; record scope follows core's company / site grants; a bundle whose action calls a core port is also granted `warehouse:orders:port` in the trade seed | — | FR-617 |

## 3. T3 — Time-driven rules

| ID | Rule | Trigger | Changes | Notified | Job | Source |
|---|---|---|---|---|---|---|
| TRA-T3-01 | Response reminder | `response_due_date − warehouse.trade.rfq.reminder_days` (default 2), invitees `INVITED` | none | the RFQ's buyer, `TRADE_RFQ_REMINDER` | `TradeRfqJob` daily | FR-563 |
| TRA-T3-02 | Due date passed | `response_due_date < today` (site tz) | RFQ stays `ISSUED` (bids close only by `TRA-T1-05`); *sealed* lifts; the buyer is told to close bids | the RFQ's buyer, `TRADE_RFQ_DUE` | same | FR-563 |
| TRA-T3-03 | Quotation expiry | `valid_until < today` | VQ `EXPIRED` unless awarded (still revisable, `-08`) | the RFQ's buyer, `TRADE_VQ_EXPIRED` | same | FR-569 |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in | Source |
|---|---|---|---|---|
| TRA-T4-01 | CS prepared / refreshed | matrix: per RFQ line × latest submitted quotation version — net = price × (1 − disc); landed = net + charges allocated by basis; rank by landed within currency; plus lead time, payment days, MOQ, vendor grade (`TCE`), last PO rate, contract rate (`TRC-T4-02`) | `ComparativeStatementService` (backend) | FR-566 |
| TRA-T4-02 | Quotation revised while a CS using it is `DRAFT` (or returned to `DRAFT` by `TAM-T1-08a`) | CS flagged *stale*; submit refused until refreshed (`409 TRADE_CS_STALE`) | same | FR-569 |
| TRA-T4-03 | Award approved | per awarded supplier × target type, one draft target document prefilled (lines, price `price_source = QUOTATION`, terms, charges); `target_document_id` stored; **maker (`created_by`) = the statement's `prepared_by`**, never the approver (FR-549), so the approver may approve the target | `AwardService.onApproved` | FR-568 |
| TRA-T4-04 | Award approved | PR allocations move RFQ line → target line for the awarded qty on FIXED_PO / BLANKET targets; **RATE_CONTRACT and OPEN_PO targets release all** (they hold no quantity; the buyer later allocates to releases, `TPR-T1-06` *Add to release*); unawarded qty released to PR (`TPR-T1-07`); VQ statuses set; RFQ `AWARDED`/`PARTIALLY_AWARDED`/`NOT_AWARDED` once no statement is pending | same transaction | FR-560, FR-568 |

## 5. T5 — Screen contract

### 5.1 WS-288 RFQs (reference **Service Vehicle**)
Grid `wht_rfqs`, scope `WAREHOUSE_TRADE_RFQ`, sort `e.created_at DESC`. Tiles: draft, issued, due ≤ 2
days, bids closed, awarded. Columns: `rfqNumber`, `warehouseName`, `buyerName`, `issueDate`,
`responseDueDate`, `lineCount`, `invitedCount`, `respondedCount`, `status`, audit. Filters: `warehouseId`,
`status`, `buyerId`, `supplierId` (invitee), `itemId`, `dueFrom`/`dueTo`. Row actions: View · Edit · Issue
· Capture response · Close bids · Prepare CS · Cancel · Print. Modal tabs: Header · Lines · Suppliers.

### 5.2 WS-289 Vendor Quotations
Grid `wht_vendor_quotations`, scope `WAREHOUSE_TRADE_VENDOR_QUOTATION`, sort `e.quote_date DESC`; latest
version per number by default (*All versions* toggle). Tiles: submitted (current), expiring ≤ 7 days,
expired, awarded (period), unsolicited — counts. Columns: `vqNumber`, `versionNo`, `rfqNumber`,
`supplierName`, `supplierQuoteRef`, `quoteDate`, `validUntil` (date-only), `currencyCode`, `totalValue`
(masked when sealed), `status`, audit. Filters: `supplierId`, `rfqId`, `status`, `currencyCode`,
`validFrom`/`validTo`, `expiringOnly`. Row actions: View · Revise (`SUBMITTED`, `EXPIRED`) · Withdraw ·
Versions. Export ⊇ grid (prices masked while sealed). Empty state: *No quotations captured.*

### 5.3 WS-290 Comparative Statements + detail
Grid `wht_comparative_statements`, scope `WAREHOUSE_TRADE_COMPARATIVE_STATEMENT`, sort `e.created_at DESC`.
Columns: `csNumber`, `rfqNumber`, `currencyCode`, `buyerName`, `preparedByName`, `lineCount`,
`supplierCount`, `awardedValue` (statement currency), `nonL1Count`, `isStale`, `status`, audit. Filters:
`rfqId`, `status`, `currencyCode`, `buyerId`, `preparedFrom`/`To`, `nonL1Only`, `staleOnly`. Tiles: draft,
stale, submitted, approved (period), rejected (period) — counts. Row actions: View · Edit (`DRAFT`) · Refresh
(stale) · Submit · Withdraw · Print. Export ⊇ grid. Empty state: *No comparative statements — prepare one from
an RFQ.* Detail is a matrix (rows = RFQ lines, column groups = suppliers) rendered from the backend payload;
L1 cell highlighted; other-currency quotations in a separate unranked band; per line an award editor
(supplier, qty, target type, reason). Print `COMPARATIVE_STATEMENT`.

## R32 additions (PRD 2026-10-24, `D-20`)

Rows added by the R32 fold (FRD-TRADE §4.15). Numbers continue each kind's sequence; where a number exists on one side of the purchase / sales mirror only, the asymmetry is stated in FRD-TRADE §5 rows M35…M40.

| ID | Kind | Rule | Refusal / effect | Source |
|---|---|---|---|---|
| TRA-T4-05 | effect | Vendor quotation lines get tax rows from `WhTaxPreviewProvider` (`CN-16`) at the supplier's state vs the receiving site; a vendor-stated rate that differs is shown, the computed one is used | no provider → no tax rows | FR-761 |
| TRA-T4-06 | effect | CS shows landed price **excluding recoverable GST** and **gross incl. GST**; rank (L1) on `warehouse.trade.cs.rank_basis` (default `LANDED_NET_OF_ITC`, else `GROSS`), still only within one currency (`OD-34`) | — | FR-762 |
| TRA-T1-15 | transition | *Share* an `ISSUED` RFQ to each invited supplier by e-mail / WhatsApp (`wht_document_shares`); supersedes `TRA-OPEN-01` | `422 TRADE_SHARE_DOCUMENT_NOT_APPROVED`; `503 TRADE_SHARE_CHANNEL_UNAVAILABLE` | FR-763 |

## 6. Out of scope

| Item | Decision |
|---|---|
| Supplier portal / e-auction | refused FRD §11 R6 |
| Technical vs commercial two-envelope evaluation | not built in v1; sealed mode is the single-envelope form. Re-entry: a `technical_status` per quotation |
| Tax in landed price | refused `TRD-06` |

## 7. Amendments

| Date | Rows | Change | Found by |
|---|---|---|---|
| 2026-10-22 | all | v0 derived | TRADE author |
| 2026-10-22 | §0, §1.1, `TRA-T1-04`, `-08`, `-10`, `-11`, `-13`, `-14`, `TRA-GRD-07`, `-10`, T3, `TRA-T4-02`…`-04`, §5.2, §5.3 | R29 TP-F2, F3, F16, F25, F26, F28 and *in code, not in contract*: rejected/returned statement exits, cancel from `BIDS_CLOSED`/`EVALUATION`, revise from `EXPIRED`, one statement per currency, OPEN-PO targets release allocations, target maker, `:award` dropped, screen contracts | R29 |
| 2026-10-23 | every T1, guard, unreachable, T3 and T4 row | `Source` column added, filled from FRD-TRADE §4, so every rule traces to the FR it proves | R30 `CP-FR-008` |
| 2026-10-23 | §1.1 `BIDS_CLOSED`, `TRA-T3-02`, `-T2-03`, `-GRD-11`, `TRA-OPEN-01`, every T2 row | R31: the due date never closes bids (F-TR-023); cancel states aligned with `TRA-T1-04` (F-TR-018); `TRA-OPEN-01` settled; stale-write code (`TPR-OPEN-03`); T2 Source FRs (F-TR-019) | R31 |
| 2026-10-25 | `TRA-T4-05`, `TRA-T4-06`, `TRA-T1-15` (new, *R32 additions*) | R32 fold of the client PRD (`D-20`): GST on vendor quotations and the CS (rank net of ITC), RFQ share by e-mail / WhatsApp (`TRA-OPEN-01` superseded) | R32 / `D-20` |

## 8. Invariants and scenarios

`WH-SC-485`, `WH-SC-505`…`WH-SC-514`, `WH-SC-566`, `WH-SC-573`.

## 9. Open rows

| ID | Question | Status |
|---|---|---|
| TRA-OPEN-01 | E-mail dispatch of RFQ prints | **Settled (R31 decisions):** default stands — print + download only in v1; channel recorded manually (`p9-05`) · **Superseded 2026-10-25 by `D-20` item 7 (R32): e-mail / WhatsApp share, `TRA-T1-15`, FR-763 (`p9-16`)** |
