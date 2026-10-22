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
| **Permission resources** | `wht_supplier_profiles:view/create/edit/export/block` · `wht_customer_profiles:` same · `wht_approved_vendor_items:view/create/edit/export/approve` · `wht_customer_item_refs:view/create/edit/export` · `wht_terms_templates:view/create/edit` · `wht_evaluation_schemes:view/create/edit` · `wht_evaluation_runs:view/create/publish/export` |
| **Routes** | WS-280, WS-281, WS-282, WS-283, WS-311, WS-310, WS-297, WS-309 · mobile: none |
| **Contract status / version** | `derived` · `v0 — 2026-10-22` |

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
(`PENDING`/`APPROVED`). Customer item ref: company, customer, item, `customer_part_number`,
`drawing_number`, `drawing_revision`, `approval_status_code`, `valid_from`, `valid_to`, document link.
Scheme: company, `side` (`PURCHASE`/`SALES`), `period_type`, `is_active`; criteria: `metric_code` (fixed
catalogue below), `weight` `DECIMAL(9,6)`; bands: `grade_code`, `min_score`. Run: scheme, `period_from`,
`period_to`, `status` (`DRAFT`/`PUBLISHED`/`SUPERSEDED`), `supersedes_run_id`; evaluation: run,
counterparty, `score`, `grade_code`, `sample_size`; score: metric, `raw_value`, `normalised_score`
(0–100), `numerator`, `denominator`.

**Metric catalogue** (fixed in code; scheme picks and weights them):

| Side | Metric | Formula (period, per counterparty) | Source |
|---|---|---|---|
| P | `DELIVERY_OTIF` | released schedule lines received **on or before** `delivery_date` (site tz) **and** ≥ qty × (1 − under tolerance) ÷ released schedule lines due in period × 100 | trade schedule + core GRN `occurred_at`, qty (`p6-05` facts) |
| P | `QUALITY_ACCEPTANCE` | accepted ÷ inspected qty × 100 (lines without inspection count as accepted only when the item's inspection policy is *none*) | core QC (`p8-06`) |
| P | `PRICE_VARIANCE` | 100 − clamp(|PO net price − contract price| ÷ contract price × 100, 0, 100), quantity-weighted; lines without a contract excluded | trade |
| P | `RFQ_RESPONSE` | invitations `RESPONDED` ÷ invitations closed × 100 | trade |
| P | `ACK_TIMELINESS` | POs acknowledged within `warehouse.trade.ack.alert_days` ÷ POs issued × 100 | trade |
| S | `DELIVERY_OTIF` | schedule lines shipped on or before `committed_date` and in full ÷ due × 100 | trade schedule + core shipment |
| S | `RETURN_RATE` | 100 − (authorised return qty ÷ shipped qty × 100) | trade SRA + core |
| S | `SCHEDULE_VOLATILITY` | 100 − (firm-zone schedule changes ÷ schedule lines due × 100), floored at 0 | `TOA-T4-06` |
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

## 1. T1 — State machine

| ID | From | Action | To | Guard | Actor | Side effects | Comment | UI |
|---|---|---|---|---|---|---|---|---|
| TCE-T1-01 | — | Create / edit profile | profile active | `TCE-GRD-01`, `-02` | `:create`/`:edit` | — | no | WS-280 / WS-281 |
| TCE-T1-02 | not blocked | Request block | `BLOCK_PENDING` | — | `:block` | `TAM` doc `PROFILE_BLOCK` | **yes**, reason code | row action |
| TCE-T1-03 | `BLOCK_PENDING` / blocked | Approved / request unblock → approved | blocked / unblocked | `TAM` | approver | `blocked_at/by`; audit | yes | WS-285 |
| TCE-T1-04 | — | AVL entry / status change | `approval_state PENDING` → `APPROVED` | `TCE-GRD-03` | `wht_approved_vendor_items:create`/`edit` → `:approve` | effective on approval | reason | WS-282 |
| TCE-T1-05 | — | Customer item ref create / status change | row | uk (company, customer, item, revision) | `wht_customer_item_refs:*` | — | no | WS-283 |
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
| TCE-T2-01 | Profiles add / edit / block request | `wht_*_profiles:create`/`edit`/`block` |
| TCE-T2-02 | AVL maintain / approve | `wht_approved_vendor_items:create`/`edit`/`approve` |
| TCE-T2-03 | Customer item refs | `wht_customer_item_refs:*` |
| TCE-T2-04 | Schemes | `wht_evaluation_schemes:*` |
| TCE-T2-05 | Run / publish / export | `wht_evaluation_runs:create`/`publish`/`export` |

## 3. T3 — Time-driven rules

| ID | Rule | Trigger | Changes | Notified | Job |
|---|---|---|---|---|---|
| TCE-T3-01 | Period-end run proposal | first day after period end | a `DRAFT` run per active scheme (computation only; publish stays manual) | trade administrator | `TradeEvaluationJob` monthly |
| TCE-T3-02 | AVL expiry alert | `valid_to − 30` | none | trade administrator | `TradeContractJob` |
| TCE-T3-03 | Udyam re-classification reminder | `msme_classified_on` older than 1 year (classification limits change — April 2025 revision) | none | trade administrator | yearly |
| TCE-T3-04 | Part approval expiry | customer item ref `valid_to − 30` | none | sales exec | `TradeContractJob` |

## 4. T4 — Cross-entity effects

| ID | When | Then |
|---|---|---|
| TCE-T4-01 | PO submit for a MICRO/SMALL supplier with terms > 45 days | `TPO-GRD-01` requires `msme_acknowledged` |
| TCE-T4-02 | RFQ invite / award / PO / release / rate contract line | AVL check per FR-544 (`TRA-GRD-02`, `TPO-GRD-01`, `TRC-GRD-04`) |
| TCE-T4-03 | Run computed | metrics per catalogue from core facts (read-only, FK down) and trade documents; stored numerator / denominator so every score is reproducible |
| TCE-T4-04 | Quotation / SO line | part approval per FR-545 (`TSQ-GRD-02`, `TSO-GRD-04`) |
| TCE-T4-05 | Publish with grade ≤ `warehouse.trade.evaluation.review_grade` | a `whb_tasks` row of task type `TRADE_AVL_REVIEW` (seeded by trade) for the trade administrator, linked to the supplier / customer |
| TCE-T4-06 | Published grade | shown on CS (`TRA-T4-01`), PO header, AVL, customer profile, SO header |

## 5. T5 — Screen contract

WS-280 / WS-281 (reference **Customer**): grids `wht_supplier_profiles` / `wht_customer_profiles`,
scopes `WAREHOUSE_TRADE_SUPPLIER_PROFILE` / `WAREHOUSE_TRADE_CUSTOMER_PROFILE`; columns
`counterpartyCode`, `counterpartyName`, `msmeCategory` / `customerCategory`, `udyamRegistrationNo`,
`paymentTermsDays`, `leadTimeDays`, `isBlocked`, `latestGrade`, `status`, audit; filters category,
blocked, grade; tiles active, blocked, pending block requests, MSME (supplier) / part-approval required
(customer), grade D. WS-282 AVL grid `wht_approved_vendor_items` (item/category, supplier, status,
validity, sole source, approval state, grade). WS-283 customer item refs grid. WS-310 schemes (Customer
shape, criteria + bands tabs). WS-297 / WS-309 evaluations: run list + per-counterparty score grid
(`score`, `grade`, each metric's `normalisedScore` with numerator / denominator on hover, `excludedMetrics`).
WS-311 T&C templates (Department shape, version list).

## 6. Out of scope

| Item | Decision |
|---|---|
| Supplier self-assessment / audits (ISO, IATF checklists) | not built; re-entry: a supplier-audit document feeding a new metric |
| Payment behaviour metric | refused (R4) |

## 7. Amendments

| Date | Rows | Change | Found by |
|---|---|---|---|
| 2026-10-22 | all | v0 derived | TRADE author |

## 8. Invariants and scenarios

`WH-SC-482`…`WH-SC-487`, `WH-SC-547`…`WH-SC-549`.

## 9. Open rows

| ID | Question | Status |
|---|---|---|
| TCE-OPEN-01 | Does base let a sibling seed a `whb_task_types` row (`TRADE_AVL_REVIEW`)? | **Proposed: yes**, under the owning-module guard like code lists. DEFERRED-TO-p9-12 |
