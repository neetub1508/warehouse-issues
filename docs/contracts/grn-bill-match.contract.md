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
| **Primary tables** | `wh_goods_receipt_bills` (new, `V510403`); `wh_goods_receipt_lines` ALTER: `billed_quantity`, `excess_accepted_quantity`, `excess_refused_quantity`, `excess_refused_reason_code_id`, `excess_approved_by`, `excess_approved_at` (`V510403`); `wh_goods_receipts` ALTER: `gate_entry_id` (`V510403`); code-list rows `RECON_CASE_TYPE.EXCESS_OVER_BILL`, `RECON_RESOLUTION.RECORD_SUPPLEMENTARY_BILL`, `.ACCEPT_FREE_OF_CHARGE`, `SUPPLIER_DOCUMENT_TYPE.*`; reason context `EXCESS_REFUSAL` |
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
| GRN line excess | *none* | `excess_quantity` = 0 | — | — | fact |
| GRN line excess | *undecided* | received > billed (or > open PO/schedule qty) and `excess_accepted + excess_refused < excess` | `GBM-T1-02` | `-04`, `-05`, `-06` | blocks post |
| GRN line excess | *decided* | `excess_accepted + excess_refused = excess` | `-04`…`-06` | edit in `DRAFT` re-opens | — |
| Bill | primary / supplementary | `wh_goods_receipt_bills.is_primary`, `is_supplementary` | `-01`, `-08` | none after post (append-only) | — |
| Excess case | `OPEN` → `RESOLVED` | `wh_reconciliation_cases` (`V510019` ladder) | `GBM-T4-03` | `GBM-T1-08`, `-09` | — |

### 1.2 Transitions

| ID | From | Event | To | Guard | Actor | Side effects | Reason? | UI |
|---|---|---|---|---|---|---|---|---|
| GBM-T1-01 | GRN `DRAFT` | Set primary bill (copied from gate entry at create, editable) | unchanged | `GBM-GRD-01`, `-02`, `-03` | `wh_goods_receipts:edit` | one `is_primary` bill row (partial uk one primary per GRN) | no | WS-077 *Bill* panel |
| GBM-T1-02 | `DRAFT` | Receive line with **billed quantity** (defaults to the ASN line qty, else the open PO/schedule qty, else null for blind) | unchanged | `billed_quantity ≥ 0` | `wh_goods_receipts:edit` | `short_quantity`, `excess_quantity` computed in the response, not stored | no | WS-076 **Receive line** |
| GBM-T1-03 | `DRAFT` | Post | `POSTED` (`RQP-T1-09`) | `RQP` guards + `GBM-GRD-04`, `-05`, `-08` | `wh_goods_receipts:post` | `GBM-T4-01`…`-04` | no | WS-076 **Post** |
| GBM-T1-04 | line excess *undecided* | Accept excess **inside tolerance** | *decided* | excess ≤ tolerance headroom (`GBM-GRD-06`) | `wh_goods_receipts:edit` | `excess_accepted_quantity` = excess | no | automatic at **Receive line** when inside tolerance |
| GBM-T1-05 | line excess *undecided* | **Approve** excess above tolerance | *decided* | approver ≠ the line's last editor and ≠ the GRN creator (`FR-408`) | `wh_goods_receipts:approve_excess` | `excess_accepted_quantity`, `excess_approved_by/at` | **yes** | WS-077 line action **Approve excess** |
| GBM-T1-06 | line excess *undecided* | **Refuse** excess | *decided* | — | `wh_goods_receipts:edit` | `received_quantity` stays the physical count; `excess_refused_quantity` is set and **only `received − excess_refused` is posted** to stock (`GBM-T4-01`) | **yes** (reason context `EXCESS_REFUSAL`) | WS-077 line action **Refuse excess** |
| GBM-T1-07 | *decided* | Edit the line (qty or billed) in `DRAFT` | *undecided* if the excess changed | — | `:edit` | decision columns cleared; approval stamp cleared | no | — |
| GBM-T1-08 | GRN `POSTED` | Add **supplementary bill** (type, no, date, amount, lines: GRN line + billed qty) | unchanged | `GBM-GRD-01`…`-03`; Σ billed per line ≤ posted received | `wh_goods_receipts:add_supplementary_bill` | bill row `is_supplementary`; line `billed_quantity` += (a recorded fact, the GRN stock is untouched); open `EXCESS_OVER_BILL` case resolved `RECORD_SUPPLEMENTARY_BILL` when the line's excess-over-bill reaches 0 | no | WS-077 **Add supplementary bill** |
| GBM-T1-09 | excess case `OPEN` | Resolve `ACCEPT_FREE_OF_CHARGE` | `RESOLVED` | resolver holds `wh_reconciliation_cases:resolve`; ≠ GRN poster | case permission | resulting document = the GRN; **no** GRN change | **yes** | reconciliation case screen |

### 1.3 Guards

| ID | Predicate | Refusal | Backstop | Source |
|---|---|---|---|---|
| GBM-GRD-01 | normalised bill no (trim, upper, spaces removed) is not on a bill of a `POSTED`/`REVERSED`-free GRN of the same supplier in the same financial year (`whb_companies` FY start) | `409 SUPPLIER_BILL_DUPLICATE` · `bills[i].billNumber`, naming the first GRN | unique index on `(supplier_counterparty_id, fiscal_year, bill_number_normalised) WHERE is_live` maintained by the service on post | FR-516 |
| GBM-GRD-02 | bill date ≤ GRN receipt date and ≤ today | `422 SUPPLIER_BILL_DATE_AFTER_RECEIPT` · `bills[i].billDate` | — | FR-516 |
| GBM-GRD-03 | bill type is an active `SUPPLIER_DOCUMENT_TYPE` row | `422 SUPPLIER_DOCUMENT_TYPE_INVALID` | composite FK | FR-516 |
| GBM-GRD-04 | `bill_required_for_po_receipt = true` and any line has `po_line_id` ⇒ a primary bill exists | `409 SUPPLIER_BILL_REQUIRED` · `bills` | — | FR-516 |
| GBM-GRD-05 | every line's excess is *decided* | `409 EXCESS_APPROVAL_REQUIRED` · `lines[i].excessQuantity` naming each line | — | FR-520 |
| GBM-GRD-06 | tolerance headroom = (ordered or firm schedule open qty) × (1 + resolved pct) − already received; resolution PO line → header → item → warehouse → setting (`WhPurchaseOrderLineStatusService.java:111-126`, unchanged) | inside → auto-accept; above → needs `-05` or `-06` | — | FR-520 |
| GBM-GRD-07 | an approved excess still respects `received − refused ≥ 0` and `accepted + rejected ≤ received − refused` | `422 GRN_LINE_QUANTITIES_INCONSISTENT` | CHECK `excess_accepted_quantity + excess_refused_quantity <= received_quantity` and `accepted_quantity + rejected_quantity <= received_quantity - excess_refused_quantity` (replaces `V510014:318`) | FR-517 |
| GBM-GRD-08 | the posting tolerance refusal `OVER_RECEIPT_TOLERANCE_EXCEEDED` (`WhGoodsReceiptPostingService.java:133`) now evaluates `received − excess_refused` and is raised only when an **approved** excess is missing — it never fires on a decided line | `422 OVER_RECEIPT_TOLERANCE_EXCEEDED` | — | FR-520 |

### 1.4 Unreachable

| ID | Must never happen |
|---|---|
| GBM-UNR-01 | a debit note, credit note or journal written by any transition |
| GBM-UNR-02 | refused excess posted to stock |
| GBM-UNR-03 | a posted GRN line's received/accepted/rejected quantity changed by a supplementary bill or a case resolution (`RQP-UNR-01`) |
| GBM-UNR-04 | `billedQuantity()` returning `receivedQuantity` |

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from | Extra |
|---|---|---|---|---|
| GBM-T2-01 | Edit bill / billed qty | `wh_goods_receipts:edit` | `DRAFT` | — |
| GBM-T2-02 | Approve excess | `wh_goods_receipts:approve_excess` | `DRAFT`, line *undecided* above tolerance | ≠ maker |
| GBM-T2-03 | Refuse excess | `wh_goods_receipts:edit` | `DRAFT`, line *undecided* | reason |
| GBM-T2-04 | Add supplementary bill | `wh_goods_receipts:add_supplementary_bill` | `POSTED` | — |
| GBM-T2-05 | Open the short claim | `wh_supplier_claims:edit` / `:submit` | claim `DRAFT` | `P5-23` ladder |
| GBM-T2-06 | Print GRN | `wh_print_jobs:create` | `POSTED` (also `DRAFT` as *provisional*) | `SYS-GRN` gains bill block |

## 3. T3 — Time-driven rules

| ID | Rule | Trigger | Changes | Notified | Job | Once? |
|---|---|---|---|---|---|---|
| GBM-T3-01 | Excess-over-bill case ageing | case `OPEN` > `warehouse.receiving.supplementary_bill_alert_days` (default 15) | nothing | case owner | `p2-23` pending-approval job family | once per case |
| GBM-T3-02 | Short claim left in `DRAFT` | > `warehouse.receiving.short_claim_draft_alert_days` (default 3) | nothing | GRN poster | same | once per claim |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in |
|---|---|---|---|
| GBM-T4-01 | GRN post | the receipt movement posts `received − excess_refused` per line (the `RQP-T4-01` writer call with the reduced quantity); PO line roll-up and schedule allocation (`POS-T4-02`) use the same quantity | GRN posting service |
| GBM-T4-02 | GRN post with any line `billed − received > 0` | one `SHORT_SHIPMENT` claim in `DRAFT` (`wh_supplier_claims`, `source_document_type = GOODS_RECEIPT`), lines from `WhSupplierClaimQueryService.getPrefill` (`:311`, `suggestedQuantity` `:239`) restricted to short lines, `unit_value` = PO line `unit_price`, `claim_date` = receipt date; `created_by` = the poster. A blind receipt (no billed qty) opens none | GRN post, **same transaction** |
| GBM-T4-03 | GRN post with any line `received − excess_refused − billed > 0` | one `EXCESS_OVER_BILL` case per GRN (`subject_type = GOODS_RECEIPT`), severity `MEDIUM` | `WhReconciliationCaseRecorder.open` |
| GBM-T4-04 | GRN post | outbox `WH_GRN_POSTED` gains `bills[]` and per-line `billed/received/accepted/rejected/excessRefused` (accounting handover, FRD §8) | outbox writer |
| GBM-T4-05 | receipt reversal post (`RQP-T1-32`) | the short claim, if still `DRAFT`, is `WITHDRAWN` with note *receipt reversed*; if submitted, a `QUANTITY` case opens naming it — the claim is never silently changed | reversal service |
| GBM-T4-06 | refused excess | listed on the gate entry's gate-out view (`GTE-T4-06`) | read model |

## 5. T5 — Screen contract

### 5.1 WS-076 Goods Receipts (changes) · WS-077 detail

| | |
|---|---|
| **New grid columns** | `supplierPoNumber` (`source_document_ref` of the PO, TRADE `OD-30`), `billNumber` (primary), `billDate` (`formatDateSync`), `billType`, `gateEntryNumber`, `billedQuantity` (Σ), `shortQuantity` (Σ), `excessRefusedQuantity` (Σ), `hasOpenExcessCase` |
| **New filters** | `poNumber` (text) now matches `po_number` **or** `source_document_ref`; `billNumber` (text), `billDateFrom/To` (date), `gateEntryNumber` (text), `shortOnly`, `excessOnly` (boolean) — add to `COMMON_FILTER_CONFIGS.WAREHOUSE_GOODS_RECEIPT` |
| **New tiles** | *Short* · *Excess awaiting decision* (DRAFT) · *Excess over bill open* |
| **PO picker** | *Receive line* / blind-receipt PO search matches `po_number` or `source_document_ref`; labels show both |
| **Detail (WS-077)** | *Bill* panel (primary + supplementary list); line grid columns `billed`, `received`, `excessAccepted`, `excessRefused`, `accepted`, `rejected`, `short` side by side; line actions **Approve excess**, **Refuse excess**; header **Print**, **Add supplementary bill**; links to the short claim and the excess case |
| **Export** | grid columns + `createdByName`, `updatedByName`; line export includes all six quantities |

## 6. Out of scope

Debit/credit notes; bill booking; price variance (`P5-10`); landed cost (`P2-17`); mobile.

## 7. Amendments

| Date | Change |
|---|---|
| 2026-10-22 | v0 derived |

## 8. Invariants and scenarios

`L-1` (only `received − refused` enters stock); `RQP-UNR-01`; `FR-408`. Scenarios `WH-SC-437`…`-441`, `-477`.

## 9. Open rows

| ID | Question | Default |
|---|---|---|
| GBM-OPEN-01 | OD-28 — free-of-charge excess | case resolution only |
| GBM-OPEN-02 | Short against the PO **and** against the bill on the same line: one claim or two records? | claim for short-vs-bill; `QUANTITY` case for short-vs-PO (today) — both may exist |
