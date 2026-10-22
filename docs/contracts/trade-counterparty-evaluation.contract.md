# Functional Contract — Trade profiles, approved vendor list, customer part approval, and counterparty evaluation (vendor rating, customer rating / OTIF)

> **What this is.** The functional truth for the commercial layer `warehouse-trade` adds over the
> base counterparty: supplier and customer trade profiles (block / unblock, MSME, terms), the approved
> vendor list, the customer item reference with part approval, and the periodic evaluation of suppliers
> and customers on one engine. Approval cites `TAM-*`.
>
> **Mirror.** FRD-TRADE §5 M1, M2, M27, M28.
>
> **Status.** Derived 2026-10-22 (v0). No code exists yet.

---

## 0. Identity

| | |
|---|---|
| **Workflow** | Profile create / edit; block → approve → blocked; unblock → approve; AVL entry → approve → status changes → expiry; customer item ref → approval status; evaluation scheme → run (draft) → publish → supersede; grade-triggered review task |
| **Module** | `warehouse-trade`; reads `whb_counterparties` + roles, core receipts / QC (`p6-05`, `p8-06`), core shipments / RMAs |
| **Domain baseline** | FRD-TRADE FR-541…FR-546, FR-594…FR-597, FR-614, `TRD-05` · `p1-08` (thin identity), `p6-05` (`FR-142`) |
| **Owning task bodies** | `issues/p9-02.md` (profiles, AVL, customer item refs, T&C templates, vocabularies) · `issues/p9-12.md` (evaluation) |
| **Primary tables** | `wht_supplier_profiles`, `wht_customer_profiles`, `wht_approved_vendor_items`, `wht_customer_item_refs`, `wht_terms_templates`, `wht_terms_template_versions` (`V550010`); `wht_evaluation_schemes`, `wht_evaluation_criteria`, `wht_evaluation_grade_bands`, `wht_evaluation_runs`, `wht_counterparty_evaluations`, `wht_counterparty_evaluation_scores` (`V550110`) |
| **Permission resources** | `wht_supplier_profiles:view/create/edit/export/block/approve` · `wht_customer_profiles:` same · `wht_approved_vendor_items:view/create/edit/export/approve` · `wht_customer_item_refs:view/create/edit/export` · `wht_terms_templates:view/create/edit/export` · `wht_evaluation_schemes:view/create/edit/export` · `wht_evaluation_runs:view/create/publish/export`. `:approve` on a profile acts on `PROFILE_BLOCK` requests of that side, on the AVL on `AVL` requests (`TAM` §0.1); each depends on `:view` |
| **Routes** | WS-280, WS-281, WS-282, WS-283, WS-311, WS-310, WS-297, WS-309 · mobile: none |
| **Contract status / version** | `derived` · `v1 — 2026-10-22` (R29 folded) |

**Fields.** Supplier profile: `counterparty_id` (uk with company), `company_id`, `is_purchase_blocked`,
`block_reason_code`, `blocked_at`, `blocked_by`, `block_request_status` (`NONE`/`BLOCK_PENDING`/
`UNBLOCK_PENDING`), `msme_category_code`, `udyam_registration_no` (VARCHAR(19), pattern
`^UDYAM-[A-Z]{2}-[0-9]{2}-[0-9]{7}$`), `msme_classified_on` (DATE), `default_lead_time_days`,
`min_order_value`, `default_currency_code`, `payment_terms_code`, `payment_terms_days`,
`delivery_terms_code`, `freight_terms_code`, `latest_grade_code` (written by publish), notes, `status`.
Customer profile mirrors it without MSME, plus `customer_category_code`, `default_ship_to_address_id` ↓
`whb_counterparty_addresses`, `default_dispatch_warehouse_id`, `customer_po_required`,
`requires_part_approval`. AVL: company, `item_id` xor `item_category_id`, supplier, `avl_status_code`,
`valid_from`, `valid_to`, `is_sole_source`, `approved_by`, `approved_at`, `reason`, `approval_state`
(`PENDING`/`APPROVED`/`REJECTED`), `approval_request_id`, `pending_change` (the requested status / dates of a
change awaiting approval; the effective values stay until it is approved). Customer item ref: company,
customer, item, `customer_part_number`, `drawing_number`, `drawing_revision`, `approval_status_code`,
`valid_from`, `valid_to`, document link (required for `APPROVED`).
Scheme: company, `side` (`PURCHASE`/`SALES`), `period_type`, `is_active`; criteria: `metric_code` (fixed
catalogue below), `weight` `DECIMAL(9,6)`; bands: `grade_code`, `min_score`. Run: scheme, `period_from`,
`period_to`, `status` (`DRAFT`/`PUBLISHED`/`SUPERSEDED`), `supersedes_run_id`; evaluation: run,
counterparty, `score`, `grade_code`, `sample_size`; score: metric, `raw_value`, `normalised_score`
(0–100), `numerator`, `denominator`.

**Metric catalogue** (fixed in code; scheme picks and weights them):

| Side | Metric | Formula (period, per counterparty) | Source |
|---|---|---|---|
| P | `DELIVERY_OTIF` | committed schedule lines — FIXED schedule lines and released OPEN / BLANKET quantities — received **on or before** `delivery_date` (site tz) **and** ≥ qty × (1 − under tolerance) ÷ committed schedule lines due in period × 100; a BLANKET line left unreleased past its date (`TPO-T3-06`) is our fault and is excluded | trade schedule + core GRN `occurred_at`, qty (`p6-05` facts) |
| P | `QUALITY_ACCEPTANCE` | accepted ÷ inspected qty × 100 (lines without inspection count as accepted only when the item's inspection policy is *none*) | core QC (`p8-06`) |
| P | `PRICE_VARIANCE` | 100 − clamp(|PO net price − contract price| ÷ contract price × 100, 0, 100), quantity-weighted; lines without a contract excluded | trade |
| P | `RFQ_RESPONSE` | invitations `RESPONDED` ÷ invitations closed × 100 | trade |
| P | `ACK_TIMELINESS` | POs acknowledged within `warehouse.trade.ack.alert_days` ÷ POs issued × 100 | trade |
| S | `DELIVERY_OTIF` | schedule lines shipped on or before `committed_date` and ≥ qty × (1 − under tolerance) ÷ schedule lines due × 100 — unreleased lines count (the release is ours to make, `TSO-T3-06`) | trade schedule + core shipment (`getFulfilmentPosition`) |
| S | `RETURN_RATE` | 100 − (authorised return qty ÷ shipped qty × 100) | trade SRA + core |
| S | `SCHEDULE_VOLATILITY` | 100 − (firm-zone schedule changes ÷ schedule lines due × 100), floored at 0; firm zone = `warehouse.trade.sales.firm_zone_days` | `TOA-T4-06` |
| S | `ENQUIRY_CONVERSION` | enquiries `WON`/`PARTIALLY_WON` ÷ enquiries with an outcome × 100 | trade |

A metric with denominator 0 is **excluded** and the remaining weights are re-normalised for that
counterparty; the evaluation stores `excluded_metrics`. A counterparty with no metric is not scored.

### Acceptance checks

| # | Expects | Delivered by |
|---|---|---|
| A1 | Profile requires the role link (`WH-SC-482`) | `TCE-GRD-01` |
| A2 | MSME warning + acknowledgement (`WH-SC-483`) | `TCE-T4-01` |
| A3 | Block / unblock maker–checker (`WH-SC-484`) | `TCE-T1-02`, `-03` |
| A4 | AVL enforcement (`WH-SC-485`) | `TCE-T4-02` |
| A5 | Part approval gate (`WH-SC-486`) | `TCE-T4-04` |
| A6 | Weighted score and grade; immutable publish (`WH-SC-547`, `-548`) | `TCE-T1-07`, `TCE-GRD-04` |
| A7 | Grade raises a review task, never suspends (`WH-SC-549`) | `TCE-T4-05` |
| A8 | AVL entries are maker–checker through the engine, with a reject path (`WH-SC-570`) | `TCE-T1-04`, `-04a` |
| A9 | Block / unblock can be approved by a holder of the side's `:approve` (`WH-SC-595`) | `TCE-T1-03` |
| A10 | Customer rating and sales self-approval (`WH-SC-592`, `-593`) | metric catalogue S, `TAM-GRD-03` |

## 1. T1 — State machine

| ID | From | Action | To | Guard | Actor | Side effects | Comment | UI |
|---|---|---|---|---|---|---|---|---|
| TCE-T1-01 | — | Create / edit profile | profile active | `TCE-GRD-01`, `-02` | `:create`/`:edit` | — | no | WS-280 / WS-281 |
| TCE-T1-02 | not blocked / blocked | Request block / request unblock | `BLOCK_PENDING` / `UNBLOCK_PENDING` | no request already pending | `:block` | `TAM` doc `PROFILE_BLOCK` (side recorded) | **yes**, reason code | row action |
| TCE-T1-03 | `BLOCK_PENDING` / `UNBLOCK_PENDING` | Approved / rejected | blocked / unblocked; on reject back to the previous state | `TAM` (`TAM-GRD-03`: the requester cannot approve) | `wht_supplier_profiles:approve` / `wht_customer_profiles:approve` | `blocked_at/by`; audit | yes | WS-285 |
| TCE-T1-04 | — | AVL entry / status or date change (maker) | `approval_state PENDING`; request `AVL` opened | `TCE-GRD-03` | `wht_approved_vendor_items:create`/`edit` | the change is held in `pending_change`; nothing is effective until approval | reason | WS-282 |
| TCE-T1-04a | `PENDING` | Approved / rejected / returned (`TAM`) | `APPROVED` (change effective, `approved_by/at`) / `REJECTED` (no effect; a new entry needs a new request) / back to editable | `TAM-GRD-03` → `403 TRADE_APPROVAL_SELF` for the maker | `wht_approved_vendor_items:approve` | audit | on reject / return | WS-285 |
| TCE-T1-05 | — | Customer item ref create / status change | row | uk (company, customer, item, revision); `TCE-GRD-06` | `wht_customer_item_refs:*` | — | no | WS-283 |
| TCE-T1-06 | — | Run evaluation for scheme × period | run `DRAFT` | `TCE-GRD-04`, `-05` | `wht_evaluation_runs:create` | scores computed (`TCE-T4-03`) | no | WS-297 / WS-309 *Run* |
| TCE-T1-07 | `DRAFT` | Publish | `PUBLISHED`; prior published run for the same scheme × period `SUPERSEDED` | — | `:publish` (≠ creator: maker–checker) | `latest_grade_code` on profiles; `TCE-T4-05` | no | *Publish* |
| TCE-T1-08 | `DRAFT` | Discard | deleted | — | creator | — | no | — |

### 1.3 Guards

| ID | Predicate | Refusal |
|---|---|---|
| TCE-GRD-01 | Counterparty has role `SUPPLIER` (supplier profile) / `CUSTOMER` (customer profile); one profile per counterparty × company × side | `422 TRADE_COUNTERPARTY_ROLE_MISSING` / `409` duplicate |
| TCE-GRD-02 | Udyam number matches the pattern when MSME category is `MICRO`/`SMALL`/`MEDIUM`; payment terms days ≥ 0 | field `422` |
| TCE-GRD-03 | AVL: `item_id` xor `item_category_id`; `valid_from ≤ valid_to`; no overlapping row for the same company × item/category × supplier (`EXCLUDE`) | field `422` / `TRADE_AVL_OVERLAP` |
| TCE-GRD-04 | Scheme active; Σ weights = 100 (checked at scheme save too); ≥ 2 grade bands, strictly decreasing `min_score` | `422 TRADE_WEIGHTS_NOT_100` |
| TCE-GRD-05 | Period ended (`period_to < today`); no `DRAFT` run open for the same scheme × period | `422` / `409` |
| TCE-GRD-06 | Customer item ref `APPROVED` only with the customer's approval document attached; the status records the customer's decision, so no internal approval request (FR-545, §5 M2) | `422` on `document` |

### 1.4 Unreachable

| ID | Forbidden | Why |
|---|---|---|
| TCE-UNR-01 | Automatic AVL suspension or supplier block from a grade | `FR-596`; advisory task only |
| TCE-UNR-02 | Editing a published evaluation | immutable; re-run supersedes |
| TCE-UNR-03 | Credit limit, bank details, payment history on a profile | FRD §11 R1, R4 |
| TCE-UNR-04 | A second supplier / customer master | `FR-541` |

## 2. T2 — Action × role × state

| ID | Action | Permission |
|---|---|---|
| TCE-T2-01 | Profiles add / edit / block or unblock request / approve request | `wht_*_profiles:create`/`edit`/`block`/`approve` |
| TCE-T2-02 | AVL maintain / approve (`TAM`) | `wht_approved_vendor_items:create`/`edit`/`approve` |
| TCE-T2-03 | Customer item refs | `wht_customer_item_refs:*` |
| TCE-T2-04 | Schemes | `wht_evaluation_schemes:*` |
| TCE-T2-05 | Run / publish / export | `wht_evaluation_runs:create`/`publish`/`export` |

## 3. T3 — Time-driven rules

| ID | Rule | Trigger | Changes | Notified | Job |
|---|---|---|---|---|---|
| TCE-T3-01 | Period-end run proposal | first day after period end | a `DRAFT` run per active scheme (computation only; publish stays manual) | trade administrator, `TRADE_EVALUATION_DRAFTED` | `TradeEvaluationJob` monthly |
| TCE-T3-02 | AVL expiry alert | `valid_to − 30` | none | trade administrator, `TRADE_AVL_EXPIRING` | `TradeContractJob` |
| TCE-T3-03 | Udyam re-classification reminder | `msme_classified_on` older than 1 year (classification limits change — April 2025 revision) | none | trade administrator, `TRADE_UDYAM_REVIEW` | `TradeEvaluationJob`, yearly pass |
| TCE-T3-04 | Part approval expiry | customer item ref `valid_to − 30` | none | the customer's sales executives, `TRADE_PART_APPROVAL_EXPIRING` | `TradeContractJob` |

## 4. T4 — Cross-entity effects

| ID | When | Then |
|---|---|---|
| TCE-T4-01 | PO submit for a MICRO/SMALL supplier with terms > 45 days | `TPO-GRD-01` requires `msme_acknowledged` |
| TCE-T4-02 | RFQ invite / award / PO / release / rate contract line | AVL check per FR-544 (`TRA-GRD-02`, `TPO-GRD-01`, `TRC-GRD-04`) |
| TCE-T4-03 | Run computed | metrics per catalogue from core facts (read-only, FK down) and trade documents; stored numerator / denominator so every score is reproducible |
| TCE-T4-04 | Quotation / SO line | part approval per FR-545 (`TSQ-GRD-02`, `TSO-GRD-18`) |
| TCE-T4-05 | Publish with grade ≤ `warehouse.trade.evaluation.review_grade` | a `whb_tasks` row of task type `TRADE_AVL_REVIEW` (seeded by trade) for the trade administrator, linked to the supplier / customer |
| TCE-T4-06 | Published grade | shown on CS (`TRA-T4-01`), PO header, AVL, customer profile, SO header |

## 5. T5 — Screen contract

Every grid: `DynamicDataTable`, `grid_column_definitions` + `filter_definitions` + `grid_preferences` (both
default arrays), its own `filterUtils.ts` scope, export ⊇ grid incl. `createdByName` / `updatedByName`
(auditor: none), an empty-state message.

**WS-280 / WS-281** (reference **Customer**): grids `wht_supplier_profiles` / `wht_customer_profiles`,
scopes `WAREHOUSE_TRADE_SUPPLIER_PROFILE` / `WAREHOUSE_TRADE_CUSTOMER_PROFILE`; columns `counterpartyCode`,
`counterpartyName`, `msmeCategory` / `customerCategory`, `udyamRegistrationNo` (supplier), `paymentTermsDays`,
`leadTimeDays` (supplier) / `defaultDispatchWarehouseName` (customer), `isBlocked`, `blockRequestStatus`,
`latestGrade`, `status`, audit; filters category, `isBlocked`, `blockRequestStatus`, grade; tiles active,
blocked, pending block / unblock requests, MSME (supplier) / part-approval required (customer), grade D; row
actions View · Edit · Request block / unblock.

**WS-282 Approved Vendor List**: grid `wht_approved_vendor_items`, scope `WAREHOUSE_TRADE_APPROVED_VENDOR`;
columns `itemCode` / `itemCategoryName`, `supplierName`, `avlStatus`, `validFrom`, `validTo` (date-only),
`isSoleSource`, `approvalState`, `pendingChange`, `supplierGrade`, `approvedByName`, `approvedAt`, audit;
filters `itemId`, `itemCategoryId`, `supplierId`, `avlStatus`, `approvalState`, `activeOn`, `expiringOnly`;
tiles approved, provisional, suspended / disqualified, pending approval, expiring ≤ 30 days; row actions View ·
Add · Change status · Withdraw request. Empty state: *No AVL rows — enforcement applies only to items that
have one.*

**WS-283 Customer Item References**: grid `wht_customer_item_refs`, scope `WAREHOUSE_TRADE_CUSTOMER_ITEM_REF`;
columns `customerName`, `itemCode`, `customerPartNumber`, `drawingNumber`, `drawingRevision`,
`approvalStatus`, `validFrom`, `validTo`, `hasDocument`, audit; filters `customerId`, `itemId`,
`approvalStatus`, `expiringOnly`; tiles approved, pending, rejected, expiring ≤ 30 days, approved without a
current revision; row actions View · Edit · Attach document.

**WS-310 Evaluation Schemes** (Customer shape): grid `wht_evaluation_schemes`, scope
`WAREHOUSE_TRADE_EVALUATION_SCHEME`; columns `side`, `periodType`, `criteriaCount`, `bandCount`, `isActive`,
audit; filters `side`, `isActive`; tiles active purchase, active sales, inactive, last run (purchase), last
run (sales); modal tabs Criteria · Grade bands.

**WS-297 / WS-309 Vendor Evaluations / Customer Ratings** (mirrored): run grid `wht_evaluation_runs` filtered
by side, scopes `WAREHOUSE_TRADE_VENDOR_EVALUATION` / `WAREHOUSE_TRADE_CUSTOMER_RATING`; columns `schemeName`,
`periodFrom`, `periodTo`, `status`, `counterpartyCount`, `gradeACount`…`gradeDCount`, `publishedByName`,
`publishedAt`; filters `periodFrom`/`To`, `status`; tiles draft runs, published (period), superseded,
counterparties graded D, counterparties not scored; actions Run · Publish (≠ creator) · Discard · View scores.
Per-run score grid: `counterpartyName`, `score`, `grade`, each metric's `normalisedScore` (numerator /
denominator on hover), `sampleSize`, `excludedMetrics`.

**WS-311 T&C Templates** (Department shape): grid `wht_terms_templates`, scope `WAREHOUSE_TRADE_TERMS_TEMPLATE`;
columns `documentTypeCode`, `name`, `currentVersionNo`, `effectiveFrom`, `isActive`, audit; filters
`documentTypeCode`, `isActive`; tiles active, per document type count (PO, SO, RFQ, quotation), inactive; row
actions View · Edit · New version · Versions.

## 6. Out of scope

| Item | Decision |
|---|---|
| Supplier self-assessment / audits (ISO, IATF checklists) | not built; re-entry: a supplier-audit document feeding a new metric |
| Payment behaviour metric | refused (R4) |

## 7. Amendments

| Date | Rows | Change | Found by |
|---|---|---|---|
| 2026-10-22 | all | v0 derived | TRADE author |
| 2026-10-22 | §0, metric catalogue, `TCE-T1-02`…`-05`, `TCE-GRD-06`, T2, T3, §5 | R29 TP-F10, F11, F26, F27, F28, TS-F29, MA-12: AVL through the engine with reject, profile `:approve`, part-approval refusal recorded, OTIF over FIXED and released lines, sales firm zone named, notifications, every screen specified | R29 |

## 8. Invariants and scenarios

`WH-SC-482`…`WH-SC-487`, `WH-SC-547`…`WH-SC-549`, `WH-SC-570`, `WH-SC-592`, `WH-SC-595`.

## 9. Open rows

| ID | Question | Status |
|---|---|---|
| TCE-OPEN-01 | Does base let a sibling seed a `whb_task_types` row (`TRADE_AVL_REVIEW`)? | **Proposed: yes**, under the owning-module guard like code lists. DEFERRED-TO-p9-12 |
