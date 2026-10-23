# Functional Contract — GRN against the supplier bill: billed vs received vs accepted, short and excess

> **What this is.** The functional truth for the bill on a goods receipt: the primary and supplementary
> bills, the per-line billed quantity, the duplicate-bill guard, the short receipt that opens a supplier
> claim, and the excess that is accepted inside tolerance, accepted with approval, or refused. It
> **extends** [`receipt-qc-putaway.contract.md`](receipt-qc-putaway.contract.md) (`RQP-*`) — the GRN ladder
> `DRAFT → POSTED → REVERSED`/`CANCELLED` is unchanged and cited, not restated.
>
> **What this is not.** Not a three-way match (`P5-10`, `wh_three_way_matches`), not a debit or credit
> note (`RN-054`). Valuation is untouched.
>
> **Status.** Derived 2026-10-22 (v0) from [`frd/FRD-STORES.md`](../frd/FRD-STORES.md) §6.4. Not ratified.

---

## 0. Identity

| | |
|---|---|
| **Workflow** | GRN create (bill copied from gate entry) → receive lines with billed qty → excess decision per line → post → short claim / excess case → supplementary bill (after post) |
| **Module** | `warehouse` |
| **Domain baseline** | `FR-122`, `FR-123`, `FR-516`…`FR-520`, `STO-D5` · `RQP-T1-07`…`-12`, `RQP-GRD-06` (tolerance) · `P5-23` claims (`V510216`) · `V510019` reconciliation cases · `GLOBAL-SETTINGS-DECISIONS.md` `warehouse.receiving.over_receipt_percent` |
| **Owning task** | `issues/p8-04.md`; depends on `p8-03` (gate entry), `p8-01` (schedule allocation), `p5-23`, `p2-13` |
| **Primary tables** | `wh_goods_receipt_bills` (new, `V511313`, with `bill_group_key`); `wh_goods_receipt_lines` ALTER: **`supplier_billed_quantity`** (a new column with its own accessor `supplierBilledQuantity()` — the existing `billedQuantity()` and the two helpers that read it are left alone, R29 F5), `excess_over_po_quantity`, `excess_accepted_quantity`, `excess_approved_quantity`, `excess_refused_quantity`, `excess_refused_reason_code_id`, `excess_approved_by`, `excess_approved_at` (`V511313`); `wh_goods_receipts` ALTER: `gate_entry_id` (`V511313`); code-list rows `RECON_CASE_TYPE.EXCESS_OVER_BILL`, `RECON_RESOLUTION.RECORD_SUPPLEMENTARY_BILL`, `.ACCEPT_FREE_OF_CHARGE`, `.RECEIPT_REVERSED`, `SUPPLIER_DOCUMENT_TYPE.*`; reason context `EXCESS_REFUSAL` |
| **Permission resources** | existing `wh_goods_receipts:*`; new verbs `wh_goods_receipts:approve_excess`, `wh_goods_receipts:add_supplementary_bill` (`V511403`) |
| **Routes** | `/warehouse/inbound/goods-receipts` (WS-076) + `/[id]` (WS-077); `/warehouse/inbound/reconciliation-cases`; `/warehouse/inbound/supplier-claims` |
| **Contract version** | `v0 — 2026-10-22` |

### Acceptance checks

| # | Expects | Delivered by |
|---|---|---|
| A1 | Bill no/date on the GRN, duplicates refused (`WH-SC-437`, `-477`) | `GBM-GRD-01`…`-03` |
| A2 | Billed, received, accepted shown side by side and stored (`FR-517`, `FR-518`) | `GBM-T1-02`, §5 |
| A3 | Bill 100, received 92 → short claim, no debit note (`WH-SC-438`) | `GBM-T4-02` |
| A4 | Excess inside tolerance accepted; above it approved by a second person or refused and sent back (`WH-SC-439`…`-441`) | `GBM-T1-04`…`-06`, `GBM-GRD-05`…`-07` |
| A5 | Excess over the bill is a case awaiting a supplementary bill (`WH-SC-440`) | `GBM-T4-03`, `GBM-T1-08` |

---

## 1. T1 — State machine

The GRN header ladder is `RQP`'s. This contract adds **line-level facts** and two child documents' effects.

### 1.1 Status inventory (additions)

| Entity | Status | Represented by | Reachable via | Exits via | Kind |
|---|---|---|---|---|---|
| GRN line excess | *none* | `excess` = 0 (§1.5) | — | — | fact |
| GRN line excess | *undecided* | `decision_quantity` (§1.5) > `excess_approved + excess_refused` | `GBM-T1-02` | `-05`, `-06` | blocks post |
| GRN line excess | *decided* | `decision_quantity = excess_approved + excess_refused` (the auto-accepted part needs no decision) | `-04`…`-06` | edit in `DRAFT` re-opens | — |
| Bill | primary / supplementary | `wh_goods_receipt_bills.is_primary`, `is_supplementary` | `-01`, `-08` | none after post (append-only) | — |
| Excess case | `OPEN` → `RESOLVED` | `wh_reconciliation_cases` (`V510019` ladder) | `GBM-T4-03` | `GBM-T1-08`, `-09` | — |

### 1.2 Transitions

| ID | From | Event | To | Guard | Actor | Side effects | Reason? | UI | Source |
|---|---|---|---|---|---|---|---|---|---|
| GBM-T1-01 | GRN `DRAFT` | Set primary bill (copied from gate entry at create, editable) | unchanged | `GBM-GRD-01`, `-02`, `-03` | `wh_goods_receipts:edit` | one `is_primary` bill row (partial uk one primary per GRN) | no | WS-077 *Bill* panel | — |
| GBM-T1-02 | `DRAFT` | Receive line with **supplier billed quantity** (defaults to the ASN line qty, else the open PO/schedule qty, else null for blind) | unchanged | `supplier_billed_quantity ≥ 0` | `wh_goods_receipts:edit` | §1.5 figures computed in the response; the auto-accepted part is stored at once (`-04`) | no | WS-076 **Receive line** | FR-518 |
| GBM-T1-03 | `DRAFT` | Post | `POSTED` (`RQP-T1-09`) | `RQP` guards + `GBM-GRD-04`, `-05`, `-08` | `wh_goods_receipts:post` | `GBM-T4-01`…`-04` | no | WS-076 **Post** | — |
| GBM-T1-04 | any line with `excess > 0` | Accept the **auto part** (`excess − decision_quantity`, §1.5) | unchanged | — | system at **Receive line** | `excess_accepted_quantity` = the auto part | no | automatic | — |
| GBM-T1-05 | line excess *undecided* | **Approve** the decision quantity (all of it or part; the rest must be refused) | *decided* when approved + refused = decision quantity | approver ≠ the line's last editor and ≠ the GRN creator (`FR-408`), else `403 GRN_EXCESS_SELF_APPROVAL` (R29 F26) | `wh_goods_receipts:approve_excess` | `excess_approved_quantity`, `excess_accepted_quantity` += it, `excess_approved_by/at` | **yes** | WS-077 line action **Approve excess** | — |
| GBM-T1-06 | line excess *undecided* | **Refuse** the decision quantity (or the part not approved) | *decided* | — | `wh_goods_receipts:edit` | `received_quantity` stays the physical count; `excess_refused_quantity` is set and **only `received + free − excess_refused` is posted** to stock (`GBM-T4-01`) | **yes** (reason context `EXCESS_REFUSAL`) | WS-077 line action **Refuse excess** | — |
| GBM-T1-07 | *decided* | Edit the line (qty or billed) in `DRAFT` | *undecided* if the excess changed | — | `:edit` | decision columns cleared; approval stamp cleared | no | — | — |
| GBM-T1-08 | GRN `POSTED` | Add **supplementary bill** (type, no, date, amount, lines: GRN line + billed qty) | unchanged | `GBM-GRD-01`…`-03`; Σ billed per line ≤ posted received | `wh_goods_receipts:add_supplementary_bill` | bill row `is_supplementary`; line `supplier_billed_quantity` += (a recorded fact, the GRN stock is untouched); open `EXCESS_OVER_BILL` case resolved `RECORD_SUPPLEMENTARY_BILL` when the line's excess-over-bill reaches 0 | no | WS-077 **Add supplementary bill** | — |
| GBM-T1-09 | excess case `OPEN` | Resolve `ACCEPT_FREE_OF_CHARGE` | `RESOLVED` | resolver holds `wh_reconciliation_cases:resolve`; ≠ GRN poster, else `403 EXCESS_CASE_SELF_RESOLUTION` (R29 F26) | case permission | resulting document = the GRN; **no** GRN change | **yes** | reconciliation case screen | — |

### 1.3 Guards

| ID | Predicate | Refusal | Backstop | Source |
|---|---|---|---|---|
| GBM-GRD-01 | normalised bill no (trim, upper, spaces removed) is not on a **live** bill (GRN `POSTED`, not reversed) of the same supplier in the same financial year (`whb_companies` FY start) **belonging to another bill group**. `bill_group_key` = the GRN's `gate_entry_id`, else the GRN id: every GRN of one gate entry carries the entry's one bill and is one group, so several GRNs (several POs on one entry, `V510014:128` `session_id` not unique) never trip the guard on their shared bill (R29 F24) | `409 SUPPLIER_BILL_DUPLICATE` · `bills[i].billNumber`, naming the first GRN | `EXCLUDE USING gist (supplier_counterparty_id WITH =, fiscal_year WITH =, bill_number_normalised WITH =, bill_group_key WITH <>) WHERE (is_live)` (`btree_gist`, `V500012`) | FR-516 |
| GBM-GRD-02 | **primary** bill: bill date ≤ GRN receipt date and ≤ today. **Supplementary** bill (`GBM-T1-08`, appended after post — the supplier invoices the excess later): bill date ≥ the primary bill's date (the GRN receipt date when there is none) and ≤ today (site TZ); the receipt-date ceiling does not apply to it (R31 F-SR-007) | `422 SUPPLIER_BILL_DATE_AFTER_RECEIPT` · `bills[i].billDate` (primary) / `422 SUPPLEMENTARY_BILL_DATE_INVALID` · `billDate` (supplementary) | — | FR-516 |
| GBM-GRD-03 | bill type is an active `SUPPLIER_DOCUMENT_TYPE` row | `422 SUPPLIER_DOCUMENT_TYPE_INVALID` | composite FK | FR-516 |
| GBM-GRD-04 | `bill_required_for_po_receipt = true` (default **true**, seeded by `P8-04`; R31 F-SR-014) and any line has `po_line_id` ⇒ a primary bill exists | `409 SUPPLIER_BILL_REQUIRED` · `bills` | — | FR-516 |
| GBM-GRD-05 | every line's excess is *decided* | `409 EXCESS_APPROVAL_REQUIRED` · `lines[i].decisionQuantity` naming each line | — | FR-520 |
| GBM-GRD-06 | the §1.5 arithmetic: headroom `H` = effective open quantity (`effectiveOrderedQuantity()` or the firm open schedule quantity, `POS-T1-14`) − received on other posted GRNs; tolerance `T` = effective quantity × resolved pct, resolution PO line → header → item → warehouse → setting (`WhPurchaseOrderLineStatusService.java:111-126`, unchanged); free quantity is excluded from every comparison, as today (`WhGoodsReceiptLine.java:42-44`) | auto part accepted; the decision part needs `-05` or `-06` | — | FR-520 |
| GBM-GRD-07 | an approved excess still respects `received − refused ≥ 0` and `accepted + rejected ≤ received − refused`. **`rejected_quantity` is the existing dock rejection** (landed in `REJECTED` at post, `WhGoodsReceiptPostingService.java:305-311`), not a QC reject — a QC reject is an inspection disposition (R29 F5) | `422 GRN_LINE_QUANTITIES_INCONSISTENT` | CHECK `excess_accepted_quantity + excess_refused_quantity <= received_quantity`, `supplier_billed_quantity IS NULL OR supplier_billed_quantity >= 0`, and `accepted_quantity + rejected_quantity <= received_quantity - excess_refused_quantity` (replaces `V510014:318`) | FR-517, FR-122 |
| GBM-GRD-08 | the posting tolerance refusal `OVER_RECEIPT_TOLERANCE_EXCEEDED` (`WhGoodsReceiptPostingService.java:133`) now evaluates `received − excess_refused` (free excluded) against `H + T + excess_approved` — it never fires on a decided line, and a receipt over the PO but not over the bill **is** decidable (R29 F8) | `422 OVER_RECEIPT_TOLERANCE_EXCEEDED` | — | FR-520 |

### 1.4 Unreachable

| ID | Must never happen |
|---|---|
| GBM-UNR-01 | a debit note, credit note or journal written by any transition |
| GBM-UNR-02 | refused excess posted to stock |
| GBM-UNR-03 | a posted GRN line's received/accepted/rejected quantity changed by a supplementary bill or a case resolution (`RQP-UNR-01`) |
| GBM-UNR-04 | `supplierBilledQuantity()` returning `receivedQuantity`, or a change to what the existing `billedQuantity()` / `overReceivedQuantity()` / `shortQuantity()` return (`WhGoodsReceiptLine.java:207-228`; they keep comparing received to *expected*) |

### 1.5 Excess arithmetic and frozen worked examples (R29 F5, F8)

Per GRN line, free quantity excluded everywhere: `R` received, `B` supplier billed (null for blind), `H`
headroom and `T` tolerance (`GBM-GRD-06`).

- `excess_over_bill` = max(`R − B`, 0) (0 when `B` is null) · `excess_over_po` = max(`R − H`, 0) (stored `excess_over_po_quantity`)
- `excess` = max(`excess_over_bill`, `excess_over_po`)
- **`decision_quantity`** = max(`R − (H + T)`, 0) — the only part that needs **Approve** or **Refuse**
- auto part = `excess − decision_quantity` (accepted at Receive line, `GBM-T1-04`)
- `excess_over_bill_accepted` = max(`R − excess_refused − B`, 0) — opens the `EXCESS_OVER_BILL` case (`GBM-T4-03`)

| # | PO (`H`) | Tol. | Bill `B` | Received `R` | excess / decision | Outcome |
|---|---|---|---|---|---|---|
| E1 (`WH-SC-439`) | 100 | 2% (`T` 2) | 100 | 104 | 4 / **2** | 2 auto-accepted; post refused `409 EXCESS_APPROVAL_REQUIRED` until the 2 are approved or refused |
| E2 (`WH-SC-440`) | 100 | 2% | 100 | 104 | 4 / 2 approved | 104 posted; `EXCESS_OVER_BILL` case for 4 |
| E3 (`WH-SC-441`) | 100 | 2% | 100 | 104 | 4 / 2 refused | 102 posted; refused 2 leave with the vehicle; case for 2 |
| E4 (R29 F8) | 100 | 2% | 110 | 110 | 10 / **8** | over the PO, not over the bill: 2 auto, 8 to approve or refuse; no excess-over-bill case |
| E5 | 100 | 5% (`T` 5) | 100 | 103 | 3 / 0 | all 3 auto-accepted; case for 3 |
| E6 | 100 | 2% | — (blind) | 101 | 1 / 0 | auto-accepted; no case (no bill) |

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from | Extra | Source |
|---|---|---|---|---|---|
| GBM-T2-01 | Edit bill / billed qty | `wh_goods_receipts:edit` | `DRAFT` | — | — |
| GBM-T2-02 | Approve excess | `wh_goods_receipts:approve_excess` | `DRAFT`, line *undecided* above tolerance | ≠ maker | — |
| GBM-T2-03 | Refuse excess | `wh_goods_receipts:edit` | `DRAFT`, line *undecided* | reason | — |
| GBM-T2-04 | Add supplementary bill | `wh_goods_receipts:add_supplementary_bill` | `POSTED` | — | — |
| GBM-T2-05 | Open the short claim | `wh_supplier_claims:edit` / `:submit` | claim `DRAFT` | `P5-23` ladder | — |
| GBM-T2-06 | Print GRN | `wh_print_jobs:create` | `POSTED` (also `DRAFT` as *provisional*) | `SYS-GRN` gains bill block | FR-538, FR-518 |

## 3. T3 — Time-driven rules

| ID | Rule | Trigger | Changes | Notified | Job | Once? |
|---|---|---|---|---|---|---|
| GBM-T3-01 | Excess-over-bill case ageing | case `OPEN` > `warehouse.receiving.supplementary_bill_alert_days` (default 15) | nothing | case owner | `p2-23` pending-approval job family | once per case |
| GBM-T3-02 | Short claim left in `DRAFT` | > `warehouse.receiving.short_claim_draft_alert_days` (default 3) | nothing | GRN poster | same | once per claim |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in | Source |
|---|---|---|---|---|
| GBM-T4-01 | GRN post | the receipt posts **`received + free − excess_refused`** per line: `received + free − rejected − excess_refused` into the resolved received status and `rejected` into `REJECTED` (today's split, `WhGoodsReceiptPostingService.java:305-311`, with the refused excess taken off); PO line roll-up and schedule allocation (`POS-T4-02`) use `received − excess_refused` (free excluded, as today) | GRN posting service | — |
| GBM-T4-02 | GRN post with any line `supplier_billed − received > 0` | one `SHORT_SHIPMENT` claim in `DRAFT` (`wh_supplier_claims`, `source_document_type = GOODS_RECEIPT`), lines from `WhSupplierClaimQueryService.getPrefill` (`:311`) restricted to short lines; **for `SHORT_SHIPMENT` the prefill's suggested quantity and the validation ceiling (`WhSupplierClaimValidationService.java:216-229`, query `:335`) read `supplier_billed − received` when the GRN line has a supplier billed quantity, and keep `expected − received` otherwise** (R29 F19); `unit_value` = PO line `unit_price` (or the allocated schedule price, `POS-GRD-12`), `claim_date` = receipt date; `created_by` = the poster. A blind receipt (no billed qty) opens none | GRN post, **same transaction** | FR-519 |
| GBM-T4-03 | GRN post with any line `excess_over_bill_accepted` > 0 (§1.5) | one `EXCESS_OVER_BILL` case per GRN (`subject_type = GOODS_RECEIPT`), severity `MEDIUM` | `WhReconciliationCaseRecorder.open` | — |
| GBM-T4-04 | GRN post | outbox `WH_GRN_POSTED` gains `bills[]` and per-line `billed/received/accepted/rejected/excessRefused` (accounting handover, FRD §8) | outbox writer | — |
| GBM-T4-05 | receipt reversal post (`RQP-T1-32`) | the short claim, if still `DRAFT`, is `WITHDRAWN` with note *receipt reversed*; if submitted, a `QUANTITY` case opens naming it — the claim is never silently changed. An open `EXCESS_OVER_BILL` case of the GRN and an open weighment `QUANTITY` case (`GTE-T4-03`) are resolved `RECEIPT_REVERSED` (new `RECON_RESOLUTION` row; resulting document = the reversal) in the same transaction (R29 F29) | reversal service | — |
| GBM-T4-06 | refused excess | listed on the gate entry's gate-out view (`GTE-T4-06`) | read model | — |

## 5. T5 — Screen contract

### 5.1 WS-076 Goods Receipts (changes) · WS-077 detail

| | |
|---|---|
| **New grid columns** | `supplierPoNumber` (`source_document_ref` of the PO, TRADE `OD-30`), `billNumber` (primary), `billDate` (`formatDateSync`), `billType`, `gateEntryNumber`, `supplierBilledQuantity` (Σ), `billShortQuantity` (Σ), `excessRefusedQuantity` (Σ), `hasOpenExcessCase` |
| **New filters** | `poNumber` (text) now matches `po_number` **or** `source_document_ref`; `billNumber` (text), `billDateFrom/To` (date), `gateEntryNumber` (text), `shortOnly`, `excessOnly` (boolean) — add to `COMMON_FILTER_CONFIGS.WAREHOUSE_GOODS_RECEIPT` |
| **New tiles** | *Short* · *Excess awaiting decision* (DRAFT) · *Excess over bill open* |
| **PO picker** | *Receive line* / blind-receipt PO search matches `po_number` or `source_document_ref`; labels show both |
| **Detail (WS-077)** | *Bill* panel (primary + supplementary list); line grid columns `supplierBilled`, `free`, `received`, `dockRejected`, `excessAccepted`, `excessRefused`, `accepted`, `rejected`, `short` side by side; line actions **Approve excess**, **Refuse excess**; header **Print**, **Add supplementary bill**; links to the short claim and the excess case |
| **Export** | grid columns + `createdByName`, `updatedByName`; line export includes all six quantities |

## 6. Out of scope

Debit/credit notes; bill booking; price variance (`P5-10`); landed cost (`P2-17`); mobile.

## 7. Amendments

| Date | Change |
|---|---|
| 2026-10-22 | v0 derived |
| 2026-10-22 | R29 dispositions: `supplier_billed_quantity` beside the untouched helpers; free and dock-rejected quantity in the posting rule; §1.5 excess arithmetic with frozen examples; duplicate-bill guard per bill group; short-claim ceiling on billed − received; reversal resolves the cases; self-approval codes |
| 2026-10-23 | R31: supplementary bill dated after the receipt accepted, ≥ the primary bill's date (`GBM-GRD-02`, F-SR-007); `bill_required_for_po_receipt` default stated (`GBM-GRD-04`, F-SR-014); `GBM-OPEN-01`/`-02` resolved (`R31-decisions`) |

## 8. Invariants and scenarios

`L-1` (only `received − refused` enters stock); `RQP-UNR-01`; `FR-408`. Scenarios `WH-SC-437`…`-441`, `-477`.

## 9. Open rows

| ID | Question | Default |
|---|---|---|
| GBM-OPEN-01 | OD-28 — free-of-charge excess | case resolution only. **RESOLVED (DEFAULT), 2026-10-23** (`R31-decisions`): wait for the bill; a manager may resolve `ACCEPT_FREE_OF_CHARGE` on the case only; the posted GRN line is never edited |
| GBM-OPEN-02 | Short against the PO **and** against the bill on the same line: one claim or two records? | claim for short-vs-bill; `QUANTITY` case for short-vs-PO (today) — both may exist. **RESOLVED (DEFAULT), 2026-10-23** (`R31-decisions`): two records, both linked to the source line, no double recovery |
