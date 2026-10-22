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
| **Permission resources** | `wht_rfqs:view/create/edit/export/issue/cancel` · `wht_vendor_quotations:view/create/edit/export` · `wht_comparative_statements:view/create/edit/export/submit/approve/award` |
| **Routes** | WS-288 `/warehouse/trade/purchase/rfqs`, WS-289 `/vendor-quotations`, WS-290 `/comparative-statements` (+ `/[id]`) · mobile: none |
| **Contract status / version** | `derived` · `v0 — 2026-10-22` |

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
(`VALUE`/`QUANTITY`). CS: `cs_number` (at submit), `rfq_id`, `status`, `prepared_by`; award rows:
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

## 1. T1 — State machine

### 1.1 Status inventory

| Entity | Status | Reachable via | Exits via | Kind |
|---|---|---|---|---|
| RFQ | `DRAFT` | `-01` | `-03`, `-04` | initial |
| RFQ | `ISSUED` | `-03` | `-05`, `-04` | active |
| RFQ | `BIDS_CLOSED` | `-05` (manual, or due date passed — `TRA-T3-02`) | `-10` | active |
| RFQ | `EVALUATION` | CS submitted | award outcome | active |
| RFQ | `AWARDED` / `PARTIALLY_AWARDED` | `TRA-T4-04` | `-12` | active |
| RFQ | `NOT_AWARDED` | CS approved awarding nothing | none | terminal |
| RFQ | `CLOSED` | `-12` | none | terminal |
| RFQ | `CANCELLED` | `-04` | none | terminal |
| Invitee | `INVITED` → `RESPONDED` / `DECLINED` / `NO_RESPONSE` | `-05`, `-06`, `-08` | — | — |
| VQ | `DRAFT` → `SUBMITTED`; `REVISED` (superseded), `WITHDRAWN`, `EXPIRED`, `AWARDED`, `PARTIALLY_AWARDED`, `NOT_AWARDED` | `-07`, `-08`, `-09`, T3, T4 | — | — |
| CS | `DRAFT` → `SUBMITTED` → `APPROVED` / `REJECTED`; `DRAFT` on return | `-10`, `-11`, `TAM` | — | — |

### 1.2 Transitions

| ID | From | Action | To | Guard | Actor | Side effects | Comment | UI |
|---|---|---|---|---|---|---|---|---|
| TRA-T1-01 | — | Create RFQ (manual or from WS-287) | `DRAFT` | — | `wht_rfqs:create` | PR allocations (`TPR-T1-06`) | no | WS-288 Add |
| TRA-T1-02 | `DRAFT` | Add / remove invitee | invitee rows | `TRA-GRD-02` | `:edit` | AVL warning stored if WARN | no | RFQ modal tab *Suppliers* |
| TRA-T1-03 | `DRAFT` | Issue | `ISSUED` | `TRA-GRD-01`, `-02`, `-03` | `wht_rfqs:issue` | number; one print job per invitee (`RFQ` template, own name only); `sent_at` | no | Issue |
| TRA-T1-04 | `DRAFT`, `ISSUED` | Cancel | `CANCELLED` | no CS submitted | `:cancel` | PR allocations released (`TPR-T1-07`); invitees notified (print *RFQ cancelled*) | **yes** | row action |
| TRA-T1-05 | `ISSUED` | Close bids | `BIDS_CLOSED` | — | `:issue` | invitees still `INVITED` → `NO_RESPONSE` | no | row action |
| TRA-T1-06 | invitee `INVITED` | Record decline | `DECLINED` | — | `:edit` | — | reason code | Suppliers tab |
| TRA-T1-07 | — | Capture quotation (against RFQ or unsolicited) | VQ `DRAFT` → `SUBMITTED` | `TRA-GRD-04`, `-05` | `wht_vendor_quotations:create` | number; invitee `RESPONDED` | no | WS-289 Add / RFQ *Capture response* |
| TRA-T1-08 | VQ `SUBMITTED` | Revise | new version `SUBMITTED`; old `REVISED` | RFQ not `CLOSED`/`CANCELLED`; not after award approved for that line | `:edit` | `supersedes_id` | no | *Revise* |
| TRA-T1-09 | VQ `SUBMITTED` | Withdraw | `WITHDRAWN` | not awarded | `:edit` | removed from CS | yes | row action |
| TRA-T1-10 | RFQ `BIDS_CLOSED` (or `ISSUED` when all invitees answered) | Prepare CS | CS `DRAFT` | `TRA-GRD-06` | `wht_comparative_statements:create` | matrix computed (`TRA-T4-01`) | no | WS-290 *Prepare* |
| TRA-T1-11 | CS `DRAFT` | Recommend + submit | `SUBMITTED`; RFQ `EVALUATION` | `TRA-GRD-07`, `-08`, `-09` | `:submit` | `TAM-T1-03` value Σ awarded × landed price, conditions `non_l1_award` when any | reason on non-L1 | WS-290 detail |
| TRA-T1-12 | RFQ `AWARDED`/`PARTIALLY_AWARDED` | Every award target past `DRAFT` or deleted | `CLOSED` | — | system | — | — | — |

### 1.3 Guards

| ID | Predicate | Refusal |
|---|---|---|
| TRA-GRD-01 | invitees ≥ `warehouse.trade.rfq.min_suppliers` ∨ limited-source reason + note; `response_due_date ≥ issue_date`; ≥ 1 line | field `422` |
| TRA-GRD-02 | Invitee has a supplier profile, not purchase-blocked; for each RFQ item with any AVL row: status `APPROVED`/`PROVISIONAL` on the date, else REFUSE (or WARN per setting); `SUSPENDED`/`DISQUALIFIED` always refused | `422 TRADE_SUPPLIER_BLOCKED` / `TRADE_SUPPLIER_NOT_ON_AVL` |
| TRA-GRD-03 | Print templates exist for kind `RFQ` | `422 TRADE_TEMPLATE_MISSING` |
| TRA-GRD-04 | `valid_until ≥ quote_date`; price ≥ 0; price = 0 only with free-of-charge reason; discount ∈ [0,100); offered UoM convertible to RFQ UoM | field `422` |
| TRA-GRD-05 | A line with an item ≠ RFQ line item is `is_alternative = true` | `422` on `isAlternative` |
| TRA-GRD-06 | Sealed mode on ⇒ RFQ `BIDS_CLOSED` or due date passed; prices hidden in reads for everyone but the capturer until then | `409 TRADE_RFQ_SEALED` |
| TRA-GRD-07 | Σ awarded per RFQ line ≤ RFQ line qty; awarded ≤ offered qty; awarded ≥ MOQ unless note | `422 TRADE_AWARD_EXCEEDS_RFQ_QTY` |
| TRA-GRD-08 | Award to a rank ≠ 1 ⇒ `award_reason_code` + note; alternative-item award ⇒ reason | field `422` |
| TRA-GRD-09 | At approval: each awarded quotation `valid_until ≥ today`; supplier still not blocked; AVL still valid | `422 TRADE_QUOTATION_EXPIRED` / blocked |

### 1.4 Unreachable

| ID | Forbidden | Why |
|---|---|---|
| TRA-UNR-01 | An RFQ print showing another supplier's name or price | per-invitee render; template data contains one invitee |
| TRA-UNR-02 | Ranking across currencies | `OD-34`: foreign-currency quotations shown unranked |
| TRA-UNR-03 | Editing a `SUBMITTED` quotation in place | revise creates a version |
| TRA-UNR-04 | An award target created without CS approval | targets are drafted only in the `onApproved` callback |

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from |
|---|---|---|---|
| TRA-T2-01 | Edit RFQ / invitees | `wht_rfqs:edit` | `DRAFT` |
| TRA-T2-02 | Issue / close bids | `wht_rfqs:issue` | `DRAFT` / `ISSUED` |
| TRA-T2-03 | Cancel | `wht_rfqs:cancel` | `DRAFT`, `ISSUED` |
| TRA-T2-04 | Capture / revise / withdraw quotation | `wht_vendor_quotations:create`/`edit` | RFQ `ISSUED`/`BIDS_CLOSED` (revise up to award) |
| TRA-T2-05 | Prepare / edit / submit CS | `wht_comparative_statements:create`/`edit`/`submit` | per T1 |
| TRA-T2-06 | Approve award | `wht_comparative_statements:approve` via `TAM` | CS `SUBMITTED` |
| TRA-T2-07 | Print RFQ, CS | `:view` | issued / submitted |

## 3. T3 — Time-driven rules

| ID | Rule | Trigger | Changes | Notified | Job |
|---|---|---|---|---|---|
| TRA-T3-01 | Response reminder | `response_due_date − warehouse.trade.rfq.reminder_days` (default 2), invitees `INVITED` | none | buyer | `TradeRfqJob` daily |
| TRA-T3-02 | Due date passed | `response_due_date < today` (site tz) | RFQ stays `ISSUED`; *sealed* lifts; CS may be prepared | buyer | same |
| TRA-T3-03 | Quotation expiry | `valid_until < today` | VQ `EXPIRED` unless awarded | buyer | same |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in |
|---|---|---|---|
| TRA-T4-01 | CS prepared / refreshed | matrix: per RFQ line × latest submitted quotation version — net = price × (1 − disc); landed = net + charges allocated by basis; rank by landed within currency; plus lead time, payment days, MOQ, vendor grade (`TCE`), last PO rate, contract rate (`TRC-T4-02`) | `ComparativeStatementService` (backend) |
| TRA-T4-02 | Quotation revised after CS `DRAFT` | CS flagged *stale*; submit refused until refreshed (`409 TRADE_CS_STALE`) | same |
| TRA-T4-03 | Award approved | per awarded supplier × target type, one draft target document prefilled (lines, price `price_source = QUOTATION`, terms); `target_document_id` stored | `AwardService.onApproved` |
| TRA-T4-04 | Award approved | PR allocations move RFQ line → target line for the awarded qty; unawarded qty released to PR (`TPR-T1-07`); RATE_CONTRACT targets release all (no quantity); VQ statuses set; RFQ `AWARDED`/`PARTIALLY_AWARDED`/`NOT_AWARDED` | same transaction |

## 5. T5 — Screen contract

### 5.1 WS-288 RFQs (reference **Service Vehicle**)
Grid `wht_rfqs`, scope `WAREHOUSE_TRADE_RFQ`, sort `e.created_at DESC`. Tiles: draft, issued, due ≤ 2
days, bids closed, awarded. Columns: `rfqNumber`, `warehouseName`, `buyerName`, `issueDate`,
`responseDueDate`, `lineCount`, `invitedCount`, `respondedCount`, `status`, audit. Filters: `warehouseId`,
`status`, `buyerId`, `supplierId` (invitee), `itemId`, `dueFrom`/`dueTo`. Row actions: View · Edit · Issue
· Capture response · Close bids · Prepare CS · Cancel · Print. Modal tabs: Header · Lines · Suppliers.

### 5.2 WS-289 Vendor Quotations
Grid `wht_vendor_quotations`, scope `WAREHOUSE_TRADE_VENDOR_QUOTATION`. Columns: `vqNumber`,
`versionNo`, `rfqNumber`, `supplierName`, `supplierQuoteRef`, `quoteDate`, `validUntil`, `currencyCode`,
`totalValue` (masked when sealed), `status`, audit. Filters: `supplierId`, `rfqId`, `status`,
`validFrom`/`validTo`, `expiringOnly`. Row actions: View · Revise · Withdraw · Versions.

### 5.3 WS-290 Comparative Statements + detail
Grid `wht_comparative_statements`, scope `WAREHOUSE_TRADE_COMPARATIVE_STATEMENT`. Detail is a matrix
(rows = RFQ lines, column groups = suppliers) rendered from the backend payload; L1 cell highlighted;
per line an award editor (supplier, qty, target type, reason). Print `COMPARATIVE_STATEMENT`.

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

## 8. Invariants and scenarios

`WH-SC-485`, `WH-SC-505`…`WH-SC-514`.

## 9. Open rows

| ID | Question | Status |
|---|---|---|
| TRA-OPEN-01 | E-mail dispatch of RFQ prints | **Proposed:** print + download only in v1; channel recorded manually. DEFERRED-TO-p9-05 |
