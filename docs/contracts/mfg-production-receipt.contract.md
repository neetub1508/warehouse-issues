# Functional Contract — Production receipt (backflush, outputs, scrap, genealogy) and receipt reversal

> **What this is.** The functional truth for the production receipt (`FGR-`): its ladder including
> `PENDING_APPROVAL`; the backflush proposal, its edit and the whole-post shortage refusal; the
> composition of the **one** `PRODUCTION_RECEIPT` movement; main, co- and by-product outputs with lots,
> manufacture and expiry dates, serials and dispositions; scrap and rejection; over/under tolerances;
> `is_final` → order `COMPLETED`; the genealogy row; the receipt reversal (`PRV-`) request → approve →
> post with its guards; and the FG receipt note. Screens WS-326, WS-327.
>
> **What this is not.** Ledger guards are [`movement-post-reverse.contract.md`](movement-post-reverse.contract.md)
> (`MPR-*`), cited not restated. Cost arithmetic (pool, absorption, co-product split, abnormal scrap
> share) is owned by `mfg-costing-close.contract.md` (FR-654, FR-655) and cited at `PRC-T4-03`. Final QC
> dispositions are core `p8-06` / `mfg-qc-rework.contract.md`. Subcontract receipts add rules in
> `mfg-subcontracting.contract.md` (backflush from the job-worker location, `registerReturn`).
>
> **Status.** Derived 2026-10-22 (v0), **not ratified**. Authority `docs/frd/FRD-MFG.md` FR-644…FR-650,
> FR-673 (output of bonded inputs stays in bond, R31 F-MF-010), FR-678 (india Legal Metrology declaration on the
> FG receipt note, R31 F-MF-017), FR-654 (cited), §5 one-movement rule, §8 settings, §12 `WH-SC-625`…`-635`. *Proposed* codes fixed by
> `p10-07`.

---

## 0. Identity

| | |
|---|---|
| **Workflow** | Receipt `DRAFT → (PENDING_APPROVAL →) POSTED → REVERSED`, `PENDING_APPROVAL → DRAFT` (return, MD-22), `DRAFT → CANCELLED`; reversal `REQUESTED → APPROVED → POSTED`, `REQUESTED/APPROVED → REJECTED`; backflush; outputs; scrap/rejection; genealogy; FG receipt note |
| **Module** | `warehouse-manufacturing`; calls `WhbStockLedgerWriter.post/reverse`, `WhbTransformationRecorder.record` (`Propagation.MANDATORY`), `WhbReservationService`, `WhbDocumentNumberIssuer` (`FGR-`, `PRV-`), `WarehousePrintDataProvider` (`FG_RECEIPT_NOTE`); implements `QualityInspectionSourceResolver` type `PRODUCTION_RECEIPT` (`p8-06`) |
| **Domain baseline** | FRD §3.1 (`PRODUCTION_RECEIPT` + `_REVERSAL`, `VIRT-PRODUCTION`, `VIRT-SCRAP`, `PRODUCTION_SCRAP`, `PRODUCTION_DEVIATION`, `PRODUCTION_REVERSAL`, `PRODUCTION_CLOSE_SHORT`), §5, `MD-03`, `MD-10`, `MD-11`; `L-1`, `L-3`, `L-8`, `L-12`, `L-13`, `L-14`, `I-1` |
| **Owning task bodies** | `p10-07` (`V560050` · `V561050`), **including the per-receipt absorption and split** of `mfg-costing-close` §1.5 / `CST-T4-01`…`-04` (MD-37, R29 F23). Depends on `p10-05`, `p10-06`, `p8-06` |
| **Primary tables** | `whm_production_receipts`, `whm_production_receipt_outputs`, `whm_production_receipt_output_serials`, `whm_production_receipt_consumptions`, `whm_production_receipt_reversals`; base `whb_transformations` (+ inputs/outputs) |
| **Status columns** | receipt `status` and reversal `status` — **no `CHECK`** (`D-10`); a deferred constraint trigger refuses `POSTED` with null `movement_id` (the `trg_wh_work_orders_assert_completed_movement` shape) |
| **Permission resources** | `whm_production_receipts:{view,create,edit,export,post,approve,cancel}` · `whm_production_receipt_reversals:{view,create,export,approve,post}` (Reject runs under `:approve`). AUDITOR `:view` only |
| **Routes** | `/warehouse/manufacturing/production-receipts` (WS-326), `/warehouse/manufacturing/receipt-reversals` (WS-327); WS-324 *Receipts* tab · mobile: none |
| **Contract status** | `derived 2026-10-22 (v0), not ratified` |
| **Contract version** | `v0 — 2026-10-22` |

### Acceptance checks

| # | The requester expects… | Delivered by |
|---|---|---|
| A1 | Posting writes **one** `PRODUCTION_RECEIPT` movement with backflush, outputs and scrap; output into `QC_HOLD` when final inspection is required; order `IN_PROGRESS` and received rolled up (`WH-SC-625`) | `PRC-T1-04`, `PRC-T4-01`, `-02` |
| A2 | A backflush shortage refuses the whole post naming item, location, shortfall; nothing posts (`WH-SC-626`) | `PRC-GRD-12`, `PRC-UNR-02` |
| A3 | Several receipts, one movement each; `is_final` completes the order (`WH-SC-627`) | `PRC-T1-04`, `PRC-T4-06` |
| A4 | Over-receipt beyond tolerance refused naming the level; final below under-tolerance needs a close-short reason (`WH-SC-628`, `WH-SC-629`) | `PRC-GRD-05`, `-06` |
| A5 | Scrap to `VIRT-SCRAP` with reason, rejected into `REJECTED`; abnormal share kept off good units (`WH-SC-630`) | `PRC-GRD-07`, `PRC-T4-01`, `-03` |
| A6 | Scrap value above threshold waits `PENDING_APPROVAL`; the poster cannot approve (`WH-SC-631`) | `PRC-T1-05`, `-06`, `PRC-GRD-15` |
| A7 | Output expiry capped by an input lot that *limits output expiry* (`WH-SC-632`) | `PRC-GRD-08`, `PRC-T4-04` |
| A8 | Genealogy traces both ways through the receipt's transformation (`WH-SC-633`) | `PRC-T4-05` |
| A9 | Reversal request → approve (other user) → post: one reversing movement, rollups regress, transformation kept (`WH-SC-634`); refused when output moved on (`WH-SC-635`) | `PRC-T1-10`…`-13`, `PRC-GRD-21`…`-27` |
| A10 | `WARN` deviation needs a `PRODUCTION_DEVIATION` reason (`WH-SC-624`); in-process rejection pre-fills (`WH-SC-637`) | `PRC-GRD-11`, `PRC-T1-01` |
| A11 | Output of an order that consumed licensed (bonded) stock is received in that duty status; a mixed or late regime is refused (`WH-SC-682`) | `PRC-GRD-28`, `PRC-T4-14` |
| A12 | With india on, the FG receipt note and the FG / pack label carry the Legal Metrology declaration read from the lot, the packaging level and the MRP in force | `PRC-T4-15`, `PRC-UNR-09` |

---

## 1. T1 — State machine

### 1.1 Status inventory

| Entity | Status | Represented by | Reachable via | Exits via | Kind |
|---|---|---|---|---|---|
| Receipt | `DRAFT` | `whm_production_receipts.status` | `PRC-T1-01`, `-07` | `-04`, `-05`, `-08` | initial, editable |
| Receipt | `PENDING_APPROVAL` | `status`; nothing posted | `PRC-T1-05` | `-06`, `-07` | active, read-only |
| Receipt | `POSTED` | `status`; `movement_id`, `transformation_id`, `posted_by/at` (+ `approved_by/at`) | `PRC-T1-04`, `-06` | `-09` | active |
| Receipt | `REVERSED` | `status` | `PRC-T1-09` (effect) | none | **terminal** |
| Receipt | `CANCELLED` | `status`; `cancel_note` | `PRC-T1-08` | none | **terminal** |
| Reversal | `REQUESTED` | `whm_production_receipt_reversals.status`; `requested_by/at` | `PRC-T1-10` | `-11`, `-12` | initial |
| Reversal | `APPROVED` | `status`; `approved_by/at` | `PRC-T1-11` | `-13`, `-12` | active |
| Reversal | `POSTED` · `REJECTED` | `status`; `reversal_movement_id` on `POSTED` | `PRC-T1-13`, `-12` | none | **terminal** |
| Output line | `GOOD` / `REJECTED` / `SCRAPPED` | `disposition` | entry | — | not a status — a classification |

### 1.2 Transitions

| ID | From | Event / action | To | Guard (service, first) | Actor (permission) | Side effects | Comment/reason required | UI entry point | Source |
|---|---|---|---|---|---|---|---|---|---|
| PRC-T1-01 | — | **Create receipt** for an order: `occurred_at`, `posting_date`, `is_final`; outputs pre-filled from order outputs (open planned qty), scrap pre-filled from confirmed operation scrap and rejection from in-process QC since the last receipt (FR-651, `WH-SC-637`) | `DRAFT` | `PRC-GRD-01` | `whm_production_receipts:create` | `FGR-` number at create (gapless per site); consumption proposal computed (`PRC-T1-03`) | no | WS-324 *Receipts* **Receive**; WS-326 **Add** (order picker) | FR-644, FR-651 |
| PRC-T1-02 | `DRAFT` | Edit outputs: qty, UoM, location, lot code, manufacture date, expiry override, serials, disposition (`GOOD`/`REJECTED`/`SCRAPPED`), scrap reason | unchanged | `PRC-GRD-02`…`-04`, `-07`…`-10`, `-16`, `-17` | `whm_production_receipts:edit` | proposal recomputed on any main-output qty change (edited consumption lines kept, flagged) | scrap reason on `SCRAPPED` | WS-326 **Edit** modal, *Outputs* tab | FR-644 |
| PRC-T1-03 | `DRAFT` | **Backflush proposal / edit consumption**: for each `STAGE_BACKFLUSH`/`BACKFLUSH` component, proposed base = required per unit × (good + rejected + scrapped main output of this receipt); lots FEFO/FIFO from line side, then supply location; supervisor may edit qty, lot, location, add component scrap | unchanged | `PRC-GRD-11`, `-13` | `whm_production_receipts:edit` | `proposed_base_quantity` kept beside `base_quantity` | `PRODUCTION_DEVIATION` reason under `WARN` beyond tolerance | WS-326 modal *Consumption* tab | FR-645 |
| PRC-T1-04 | `DRAFT`, scrap value ≤ `scrap_value_approval_threshold` (or null) | **Post** | `POSTED` | `PRC-GRD-01`…`-14`, `-16`…`-20` re-run under the order row lock; then every `MPR-T1-01` guard (`MPR-GRD-01`, `-05`, `-07`, `-08`, `-09`/`-10`, `-15`, `-16`, `-21`, `-26`) | `whm_production_receipts:post` | `PRC-T4-01`…`-08` and `-14` in **one transaction**; order → `IN_PROGRESS` (if `RELEASED`) and, when `is_final`, → `COMPLETED` (`PRO-T1-17`) | close-short reason when final under tolerance | WS-326 row **Post** | FR-644, FR-645 |
| PRC-T1-05 | `DRAFT`, scrap value > threshold | **Post** (submits) | `PENDING_APPROVAL` | `PRC-GRD-01`…`-14`, `-16`…`-20` (validated, nothing written to the ledger) | `whm_production_receipts:post` | `scrap_value` stored; approvers notified (`PRC-T3-01`) | as `PRC-T1-04` | WS-326 row **Post** (modal says *needs approval*) | FR-646 |
| PRC-T1-06 | `PENDING_APPROVAL` | **Approve** | `POSTED` | `PRC-GRD-15`; **all post guards re-run** (stock may have moved: `PRC-GRD-12` can now refuse) | `whm_production_receipts:approve` | `approved_by/at`; as `PRC-T1-04`, `posted_by` = submitter, actor recorded as approver | no | WS-326 row **Approve** | FR-646 |
| PRC-T1-07 | `PENDING_APPROVAL` | **Return to draft** (MD-22) | `DRAFT` | `PRC-GRD-15` | `whm_production_receipts:approve` | — | **yes** — note | WS-326 row **Return** | FR-646 |
| PRC-T1-08 | `DRAFT` | **Cancel** | `CANCELLED` | — | `whm_production_receipts:cancel` | number stays issued; nothing posted | **yes** — `cancel_note` | WS-326 row **Cancel** | FR-644 |
| PRC-T1-09 | `POSTED` | *(effect of `PRC-T1-13`)* | `REVERSED` | never set directly | `whm_production_receipt_reversals:post` | — | — | none — WS-326 **Reverse** routes to WS-327 | FR-649 |
| PRC-T1-10 | receipt `POSTED` | **Request reversal** — whole receipt | reversal `REQUESTED` | `PRC-GRD-21`…`-24`, `-27` | `whm_production_receipt_reversals:create` | `PRV-` number (gapless per site) | **yes** — `PRODUCTION_REVERSAL` reason + note | WS-327 **Request**; WS-326 **Reverse** | FR-649 |
| PRC-T1-11 | `REQUESTED` | **Approve** | `APPROVED` | `PRC-GRD-26`; `-22`, `-23` re-checked | `whm_production_receipt_reversals:approve` | `approved_by/at` | no | WS-327 row **Approve** | FR-649 |
| PRC-T1-12 | `REQUESTED` · `APPROVED` | **Reject** (incl. an approved reversal whose post is refused) | `REJECTED` | — | `whm_production_receipt_reversals:approve` | uk on `receipt_id` frees (a new request is possible) | **yes** | WS-327 row **Reject** | FR-649 |
| PRC-T1-13 | `APPROVED` | **Post reversal** | `POSTED`; receipt `REVERSED` | `PRC-GRD-22`…`-25` re-run under lock; then `MPR-T1-08` guards (`MPR-GRD-09`, `-11`…`-14`, `-29`, `-30`, `-35`) — current-dated, no soft-close override | `whm_production_receipt_reversals:post` — **not** `:approve` (`RJ-005`) | `PRC-T4-09`…`-12` in one transaction; order `COMPLETED → IN_PROGRESS` (`PRO-T1-19`) | the request's reason travels to the reversal movement (`MPR-GRD-11`) | WS-327 row **Post** | FR-649 |
| PRC-T1-14 | `POSTED` · `REVERSED` | **Print FG receipt note** | unchanged | — | `whm_production_receipts:view` | `FG_RECEIPT_NOTE`: receipt + order numbers, outputs with lots, expiry, status, location; scrap / rejection with reasons; consumed components; QC reference; *REVERSED* watermark when reversed | no | WS-326 row **Print** | FR-650 |

### 1.3 Guards

| ID | Predicate (must hold to proceed) | Refusal: HTTP · code · field | Message shape | DB backstop | Source |
|---|---|---|---|---|---|
| PRC-GRD-01 | Order `RELEASED`/`IN_PROGRESS` (a `COMPLETED` order takes no receipt — reopen first, MD-14), not on hold, same company; no other receipt of the order in `PENDING_APPROVAL` when this one is `is_final` | `409 ORDER_NOT_OPEN` · `orderId`; `409 ORDER_ON_HOLD` · `orderId`; `409 ORDER_HAS_OPEN_RECEIPT` *(proposed)* · `orderId` (the field `CST-GRD-03` uses — one code, one field; R31 F-MF-019) | names status / hold | — | FR-634, FR-644 |
| PRC-GRD-02 | ≥ 1 output line with `quantity > 0`; a `MAIN` line present unless the receipt is scrap-only (`is_final` with all `SCRAPPED`) | `422 RECEIPT_HAS_NO_OUTPUTS` *(proposed)* · `outputs` | — | CHECK `quantity > 0` | FR-644 |
| PRC-GRD-03 | Each output's item is an order output (`order_output_id` set) — main, co- or by-product | `422 OUTPUT_NOT_ON_ORDER` · `outputs[n].itemId` | names item and order | FK `order_output_id` | FR-644, `WH-SC-649` |
| PRC-GRD-04 | UoM convertible to item base; `conversion_factor_used` frozen on the line; base qty ≠ 0 for non-zero entry (`MPR-GRD-26`) | `422 UOM_NOT_CONVERTIBLE` · `outputs[n].uomCode` | — | `MPR-GRD-26` | FR-644, `L-7` |
| PRC-GRD-05 | Cumulative **good** main base (posted receipts + this) ≤ planned × (1 + `over_receipt_percent`), resolved order → setting (default 0; explicit 0 blocks; null inherits) | `422 OVER_RECEIPT_TOLERANCE_EXCEEDED` · `outputs[n].quantity` | *"received 101 exceeds planned 100 by 1.00 %, tolerance 0.00 % (setting warehouse.manufacturing.over_receipt_percent)"* | — | FR-647, `WH-SC-628` |
| PRC-GRD-06 | `is_final` with cumulative good main < planned × (1 − `under_receipt_percent`) carries a `PRODUCTION_CLOSE_SHORT` reason (stored on the order `close_short_reason_code_id`) | `422 CLOSE_SHORT_REASON_REQUIRED` · `closeShortReasonCodeId` | received, threshold, level | — | FR-647, `WH-SC-629` |
| PRC-GRD-07 | `SCRAPPED` output carries an active `PRODUCTION_SCRAP` reason; `REJECTED` may carry one; component scrap on a consumption line carries one | `422 SCRAP_REASON_REQUIRED` *(proposed)* · `outputs[n].scrapReasonCodeId` | — | FK | FR-646 |
| PRC-GRD-08 | Lot / dates: lot code required by the item lot policy (from `planned_lot_code` → policy); `manufacture_date ≤ posting_date`; `expiry_date` = manufacture + shelf life capped at the earliest consumed lot with *limits output expiry*; an override may shorten, never lengthen past the cap | `422 LOT_REQUIRED` · `outputs[n].lotCode`; `422 EXPIRY_EXCEEDS_INPUT_LOT` *(proposed)* · `outputs[n].expiryDate` | names capping lot and date | — | FR-644, `WH-SC-632` |
| PRC-GRD-09 | Serialised output: serial count = base qty; unique per `(owner, item, serial)` | `422 SERIAL_REQUIRED` · `outputs[n].serials`; `409 SERIAL_ALREADY_ISSUED` · `outputs[n].serials[m]` | — | uk | FR-644, `FR-106` |
| PRC-GRD-10 | Stock status resolved: `GOOD` → `QC_HOLD` when item × site requires final inspection, else item × site receipt default → movement-type default → refuse (never a literal `AVAILABLE`); `REJECTED` → `REJECTED` | `422 RECEIVED_STATUS_UNRESOLVED` · `outputs[n].stockStatusCode` | names item, site, what to configure | — | FR-644, FR-646 (the `RQP-GRD-07` rule) |
| PRC-GRD-11 | Consumption vs proposal per policy (order → BOM → setting): beyond `consumption_tolerance_percent` `STRICT` refuses, `WARN` needs `PRODUCTION_DEVIATION`, `FLEXIBLE` free; unplanned consumption item under `STRICT` refused | `422 CONSUMPTION_TOLERANCE_EXCEEDED` · `consumptions[n].baseQuantity`; `422 DEVIATION_REASON_REQUIRED` · `consumptions[n].deviationReasonCodeId`; `422 ITEM_NOT_ON_ORDER` · `consumptions[n].itemId` | names proposed, entered, tolerance | — | FR-643, FR-645, `WH-SC-624` |
| PRC-GRD-12 | **Backflush availability**: every consumption line's qty is on hand at its location / lot / status, counting the order's own reservations as available to it, within the item × site negative-stock policy (`MPR-GRD-16`); otherwise the **whole post** is refused | `422 BACKFLUSH_SHORTAGE` · `consumptions[n]` listing item, location, lot, shortfall | *"BOLT-M8 at PLT1-RM-A01 short 120"* | ledger `MPR-GRD-15`/`-16` | FR-645, `WH-SC-626`, `MD-10` |
| PRC-GRD-13 | Consumption lot status allocatable — **or, for a component line with `supply_stock_status_code` set, exactly that status** (a rework order's `REJECTED` line, MD-30; R29 F2) — lot not expired / on hold; location is the component's line side or supply location (or another stock-holding location of the site when edited) | `422 CONSUMPTION_SOURCE_INVALID` *(proposed)* · `consumptions[n].fromLocationId` | — | ledger | FR-645 |
| PRC-GRD-14 | **= `QRW-GRD-09`** (one gate, one code, R29 F27): `block_receipt_on_open_inprocess_qc = true` ⇒ no `RECORDED` confirmation of the order with `inspection_required = true` lacks a *completed* in-process inspection (not yet started counts as open) | `409 INPROCESS_INSPECTION_OPEN` · `orderId` | lists `OPC-` numbers and inspection numbers | — | FR-652 |
| PRC-GRD-15 | Approve / return a `PENDING_APPROVAL` receipt: actor ≠ the submitter (`posted_by` candidate / `updated_by` at submit) | `403 RECEIPT_SELF_APPROVAL` *(MD-21)* · banner | names submitter | — | FR-646, `WH-SC-631` |
| PRC-GRD-16 | Output location physical, stock-holding, at the order's site (default `receipt_location_id`); not a phantom item (`BOM-GRD-12`) | `422 RECEIPT_LOCATION_INVALID` · `outputs[n].toLocationId`; `422 PHANTOM_ITEM_NOT_STOCKABLE` | — | validator | FR-644, FR-627 |
| PRC-GRD-17 | `posting_date` period `OPEN` (or soft-close override held) and `occurred_at ≤ now` | per `MPR-GRD-05`, `-09`, `-10` | as cited | ledger | FR-644, `L-8`, `L-13` |
| PRC-GRD-18 | Rollups and tolerance read under `SELECT … FOR UPDATE` on the order row; two concurrent receipts serialise | `409 CONCURRENT_MODIFICATION` · banner | — | `@Version` | FR-620 (concurrency clause, R30 `CP-FR-009`) |
| PRC-GRD-19 | One movement per receipt: idempotency key `PRODUCTION_RECEIPT:<receiptId>`; a replay returns the same movement | per `MPR-GRD-03`/`-04` | — | uk `(source_system, idempotency_key)` | FR-645, §5, `I-1` |
| PRC-GRD-20 | Non-own order is never valued (unit costs 0, `L-14`); v1 refuses non-own at create (`PRO-GRD-17`) | — (predicate asserted by test) | — | — | FR-654 |
| PRC-GRD-21 | Reversal: receipt `POSTED`; no reversal of it in `REQUESTED`/`APPROVED`/`POSTED` | `409 RECEIPT_REVERSAL_EXISTS` *(proposed)* · `receiptId` | names `PRV-` | uk `receipt_id` while not `REJECTED` | FR-649 |
| PRC-GRD-22 | **Output not moved on**: every output line's quantity still stands at its location, lot, serial and status — no later movement (pick, putaway, status change, issue, consumption by a parent order, shipment) touched it | `409 RECEIPT_OUTPUT_MOVED` · `receiptId` naming the movement / document and quantity | *"10 PUMP-100 lot P-2610-01 shipped on SHP-…"* | `MPR-GRD-13`/`-14` mirror | FR-649, `WH-SC-635`, `L-3` |
| PRC-GRD-23 | No open inspection (`PRODUCTION_RECEIPT` source) on the receipt's output; no pending QC scrap movement | `409 RECEIPT_INSPECTION_OPEN` · `receiptId` | names inspection | — | FR-649 |
| PRC-GRD-24 | Order not `CLOSED`; no live settlement (`DRAFT`/`APPROVED`) for the order — reject it first (MD-18) | `409 ORDER_NOT_OPEN` · `orderId`; `409 ORDER_SETTLEMENT_PENDING` · `orderId` (names the `PST-` number) | — | — | FR-649 |
| PRC-GRD-25 | Reversal into a closed period refused; current-dated, no soft-close override | `MPR-GRD-09` (`CLOSED` admits nothing); `403 PERIOD_OVERRIDE_FORBIDDEN` · `posting_date` | as cited | ledger | FR-649, `L-8` |
| PRC-GRD-26 | Approver ≠ requester; approver holds `whm_production_receipt_reversals:approve` (MD-20) | `403 REVERSAL_SELF_APPROVAL` *(MD-21)* · banner | — | — | FR-649 |
| PRC-GRD-27 | Reason in context `PRODUCTION_REVERSAL`, active | `422 REASON_CODE_INVALID` · `reasonCodeId` | — | FK | FR-649, `MPR-GRD-11` |
| PRC-GRD-28 | **Bonded regime at backflush** (R31 F-MF-010): the receipt's consumption lines carry at most one licensed duty status, equal to the order's `bonded_duty_status` when it is frozen; the first licensed backflush freezes it — and is refused on an order that has already posted output outside that regime (`BND-GRD-04`, MD-43) | `409 BONDED_REGIME_MIXED` / `409 BONDED_REGIME_AFTER_OUTPUT` *(proposed)* · `consumptions[n].dutyStatus` | names the frozen and the offered status | — | FR-673 |

### 1.4 Transitions that must be unreachable

| ID | Forbidden | What makes it unreachable | Source |
|---|---|---|---|
| PRC-UNR-01 | Editing a `POSTED` / `PENDING_APPROVAL` / `REVERSED` receipt | state check; no edit modal; ledger `MPR-UNR-01` | FR-649, `L-2`, `L-3` |
| PRC-UNR-02 | A partial post (some lines posted) or a failed-backflush queue | one movement, all or nothing (`MPR-T1-01`); `PRC-GRD-12` | FR-645, R-06, `MD-10` |
| PRC-UNR-03 | More than one movement per receipt, or a receipt `POSTED` with null `movement_id` | `PRC-GRD-19`; deferred constraint trigger | FR-645, §5 |
| PRC-UNR-04 | Partial reversal | whole-movement mirror (`MPR-GRD-14`) | FR-649 |
| PRC-UNR-05 | Deleting or updating a `whb_transformations` row on reversal | append-only sealed trigger; a reversing row is recorded instead | FR-649, `L-12` |
| PRC-UNR-06 | `CANCELLED`/`REVERSED` receipt, `POSTED`/`REJECTED` reversal → anything | terminal | FR-644, FR-649 |
| PRC-UNR-07 | Reversal posted by the approver's verb | `RJ-005` — `:post` ≠ `:approve` | FR-649, `RJ-005` |
| PRC-UNR-08 | Setting order `COMPLETED` from a non-final receipt | only `is_final` or manual Complete | FR-647 |
| PRC-UNR-09 | Output of bonded inputs received as `DOMESTIC`; a `whin_mrp_revisions` row updated or deleted; MRP, net quantity or month of manufacture copied onto a declaration | output duty status set from `bonded_duty_status` (`PRC-T4-14`); append-only trigger on the revisions; the declaration is read from the lot and packaging level at print (`PRC-T4-15`) | FR-673, FR-678 |

---

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from | Extra condition | Source |
|---|---|---|---|---|---|
| PRC-T2-01 | Create receipt | `whm_production_receipts:create` | order `RELEASED`/`IN_PROGRESS`, not held | supervisor | FR-644 |
| PRC-T2-02 | Edit outputs / consumption | `whm_production_receipts:edit` | `DRAFT` | — | FR-644 |
| PRC-T2-03 | Post | `whm_production_receipts:post` | `DRAFT` | — | FR-644 |
| PRC-T2-04 | Approve · Return | `whm_production_receipts:approve` | `PENDING_APPROVAL` | actor ≠ submitter; production manager | FR-646 |
| PRC-T2-05 | Cancel | `whm_production_receipts:cancel` | `DRAFT` | — | FR-644 |
| PRC-T2-06 | Print FG receipt note | `whm_production_receipts:view` | `POSTED`·`REVERSED` | — | FR-650 |
| PRC-T2-07 | Request reversal | `whm_production_receipt_reversals:create` | receipt `POSTED` | no live reversal | FR-649 |
| PRC-T2-08 | Approve · Reject reversal | `whm_production_receipt_reversals:approve` | `REQUESTED` · `REQUESTED`/`APPROVED` | actor ≠ requester | FR-649 |
| PRC-T2-09 | Post reversal | `whm_production_receipt_reversals:post` | `APPROVED` | — | FR-649 |
| PRC-T2-10 | Export | `:export` on either resource | any | not AUDITOR | FR-669 |

---

## 3. T3 — Time-driven rules & notifications

| ID | Rule | Trigger | What it changes | Who is notified | Channel | Job class | Notify-once? | Source |
|---|---|---|---|---|---|---|---|---|
| PRC-T3-01 | Pending approval (receipt `PENDING_APPROVAL`, reversal `REQUESTED`) escalation after `warehouse.approval.pending_alert_hours` | elapsed since submit / request | nothing — never auto-approves | holders of the approve verb | core pending-approval alert (`p2-23`) | core job | one per episode | FR-646, FR-649 |
| PRC-T3-02 | `DRAFT` receipt older than `staging_stale_days` | daily | nothing (`staleOnly` filter) | supervisor | in-app | `WhmStaleStagingAlertJob` | once | FR-644 |
| PRC-T3-03 | Output expiry | `expiry_date` | core shelf-life rules (`p2-05`) | — | — | core | — | FR-644 |

---

## 4. T4 — Cross-entity effects

| ID | When this happens | Then this other record must change | Enforced in | Source |
|---|---|---|---|---|
| PRC-T4-01 | Receipt post | **one `PRODUCTION_RECEIPT` movement** (INTERNAL, `source_document_type = PRODUCTION_RECEIPT`, key `PRODUCTION_RECEIPT:<id>`), lines: (a) each consumption −qty at line side / supply location, +qty at `VIRT-PRODUCTION-<site>`; (b) component scrap −qty at source, +qty at `VIRT-SCRAP-<site>`; (c) each `GOOD`/`REJECTED` output −qty at `VIRT-PRODUCTION`, +qty at its location in the resolved status, with lot, serials, frozen factor; (d) each `SCRAPPED` output −qty at `VIRT-PRODUCTION`, +qty at `VIRT-SCRAP`; balances per `(owner, item, lot, serial, duty)` (`MPR-GRD-01`, `I-1`); `movement_id`, `movement_line_id`s stored; the order's holds on the consumed positions — found by holder quad, never stored (MD-36) — passed as `consumedReservationIds` and closed `CONSUMED` by the receipt service (`WhbReservationStore.consume` — the id alone only exempts a hold from the availability check, `WhbStockPositionWriter.java:231`), their remainders re-created in the same transaction (R31 F-MF-002) | receipt posting service → `WhbStockLedgerWriter.post` (`WH-SC-625`, `-630`) | FR-645 |
| PRC-T4-02 | Receipt post | order `received_/scrapped_/rejected_quantity` (main, base); order output `received_quantity`; component `consumed_quantity`, `line_status`; `actual_start_at` when first | same transaction | FR-644 |
| PRC-T4-03 | Receipt post | **`extendedCost` per real output line, `costBasis` null** (the type default; the VAS shape `WhWorkOrderPostingService.java:78-93` — R29 F19, MD-34); counter lines carry no cost: absorbed value = own backflush + share of the unabsorbed issued pool; by-product credit first; abnormal scrap share leaves the pool as the MFG-side record `scrap_value` (no ledger value, R29 F20); MAIN + CO split by largest remainder; a same-item output whose grain nets to zero states the engine's figure and leaves the extras to settlement (MD-33) — arithmetic in `mfg-costing-close` §1.5, **built in this task** (MD-37); a post with no absorption result is refused, never posted at the engine's fallback value | costing service in `p10-07` (`WH-SC-639`, `-640`) | FR-654, FR-655 |
| PRC-T4-04 | Receipt post | output lots created/resolved with `manufacture_date`, `expiry_date`; serials written | lot service | FR-644 |
| PRC-T4-05 | Receipt post | one `whb_transformations` row (`transformation_type = PRODUCTION`, `work_order_ref_type = PRODUCTION_RECEIPT`, id, `movement_id`) via `WhbTransformationRecorder.record`: inputs = lots/serials backflushed by this receipt + **every** lot issued to the order up to this post (net of returns), whatever earlier receipt also listed it — the issued pool is absorbed across all receipts (R29 F14, MD-41); outputs = output lots | same transaction (`WH-SC-633`, `L-12`) | FR-648 |
| PRC-T4-06 | Post with `is_final` | order → `COMPLETED` (`PRO-T1-17`); remaining reservations kept until close | order service | FR-647 |
| PRC-T4-07 | Post, `GOOD` output in `QC_HOLD` | output lines exposed to `QualityInspectionSourceResolver` type `PRODUCTION_RECEIPT`; dispositions are core's (`mfg-qc-rework`) | resolver | FR-652 |
| PRC-T4-08 | Post, order `reserve_output_for_demand`, good main output landing in an **allocatable** status | a reservation of that output for the demand line (holder = the core demand order line); output landing in `QC_HOLD` (or any non-allocatable status) is **not** reserved here — `QRW-T4-10` reserves it at QC release (R29 F15) | reservation service (`WH-SC-616`) | FR-637 |
| PRC-T4-09 | Reversal post | one reversing movement through `WhbStockLedgerWriter.reverse` mirroring line for line (`MPR-T1-08`, `MPR-GRD-14`); `reversal_movement_id` | reversal service | FR-649 |
| PRC-T4-10 | Reversal post | rollups regress (received / scrapped / rejected / consumed); absorbed value returns to the pool; MTO output reservation released; order `COMPLETED → IN_PROGRESS` (`PRO-T1-19`) | same transaction | FR-649 |
| PRC-T4-11 | Reversal post | a reversing `whb_transformations` row (`transformation_type = PRODUCTION_REVERSAL`, ref `PRODUCTION_RECEIPT_REVERSAL`) with the original's inputs and outputs as positive quantities — the original stays; until base's trace reads it as a cancel marker (**SEAM-M6**, owner `p0`, carried in `P10-07`) the trace includes both, over-inclusion being the safe direction (R31 `PRC-OPEN-05`) | `WhbTransformationRecorder` | FR-649 |
| PRC-T4-12 | Reversal post | reservations the receipt consumed are **not** re-created automatically; the planner re-stages / re-releases if needed | by design | FR-649 |
| PRC-T4-14 | Receipt post on an order whose `bonded_duty_status` is set, or frozen by this receipt's backflush | every `GOOD` / `REJECTED` main, co- and by-product line is posted in that duty status, never `DOMESTIC`; india writes the `MANUFACTURE_ISSUE` / `MANUFACTURE_OUTPUT` register rows and, for scrap of licensed components, a bonded loss (`mfg-bonded-issue` `BND-T4-01`, `-03`, `-04`; R31 F-MF-010) | receipt post service; india recorder | FR-673, FR-674 |
| PRC-T4-15 | Print of the FG receipt note or the FG / pack label, india on | `p8-12`'s `declaration` block filled by india's `WarehouseDeclarationDataProvider` from `whin_packaged_commodity_declarations` (consumer care, manufacturer, packer, unit-sale-price basis), the MRP in force on the lot's pack date (`whin_mrp_revisions`), net quantity from the packaging level and month / year of manufacture from the lot; india absent → the block renders nothing (R31 F-MF-017) | print provider (`p8-12`); india bean | FR-678 |
| PRC-T4-13 | Every write | audit `PRODUCTION_RECEIPT_*`, `RECEIPT_REVERSAL_*`; `@CacheEvict statistics.whmProductionReceipt`, `statistics.whmReceiptReversal`; outbox `stock.movement.posted` (`MPR-T4-07`); accounting handover envelope (`MPR-T4-08`, FR-657) | services | FR-657 |

---

## 5. T5 — Screen contract (web only)

### 5.1 `/warehouse/manufacturing/production-receipts` — WS-326 Production Receipts

| | |
|---|---|
| **Type** | list + transition modals (reference: **Service Vehicle**) |
| **Grid identifier** | `whm_production_receipts` · filter scope `WAREHOUSE_MFG_PRODUCTION_RECEIPT` |
| **Default sort** | `e.occurred_at DESC` |
| **Statistics tiles** | `DRAFT` · `PENDING_APPROVAL` · `POSTED` · `REVERSED` · scrap value (period) |
| **Columns** | `receiptNumber`, `orderNumber`, `itemCode`, `goodQuantity`, `rejectedQuantity`, `scrappedQuantity`, `uomCode`, `lotCodes`, `isFinal`, `scrapValue`, `status`, `postingDate` (date-only `formatDateSync`), `occurredAt`, `postedAt`, `approvedAt` (timestamps), `postedByName`, `approvedByName`, `warehouseName`, audit |
| **Filters** | `warehouseId`; `status` (enum); `orderId` typeahead; `itemId` typeahead; `isFinal` (boolean); `hasScrap` (boolean); `postingDateFrom`/`To` (`date`, dateOnly); `lotCode`, `receiptNumber` (text) |
| **Row actions** | View · Edit (`DRAFT`) · Post · Approve / Return (`PENDING_APPROVAL`) · Cancel (`DRAFT`) · Reverse → WS-327 · Print FG receipt note |
| **Toolbar** | Add · Export |
| **Modals** | Add/Edit `Modal size="lg" minWidth={500} resizable`, tabs **Outputs · Consumption · Scrap & rejection · Genealogy preview**; Post confirm `md` (shows threshold outcome, close-short reason when needed); Return / Cancel `md` (note); refusals (incl. `BACKFLUSH_SHORTAGE` list) inside the modal `AlertBox`, modal stays open; Save gated on client validation + loading only |
| **Export columns** | grid + outputs sheet + consumptions sheet + `createdByName`, `updatedByName` |
| **Print** | `FG_RECEIPT_NOTE` (`PRC-T1-14`) |

### 5.2 `/warehouse/manufacturing/receipt-reversals` — WS-327 Receipt Reversals

| | |
|---|---|
| **Type** | list + transition modals (reference: **Service Vehicle**) |
| **Grid identifier** | `whm_production_receipt_reversals` · filter scope `WAREHOUSE_MFG_RECEIPT_REVERSAL` |
| **Default sort** | `e.requested_at DESC` |
| **Statistics tiles** | `REQUESTED` · `APPROVED` · `POSTED` · `REJECTED` |
| **Columns** | `reversalNumber`, `receiptNumber`, `orderNumber`, `itemCode`, `quantity`, `reasonCode`, `note`, `status`, `requestedByName`, `requestedAt`, `approvedByName`, `approvedAt`, `postedAt` (timestamps), `warehouseName`, audit |
| **Filters** | `warehouseId`; `status` (enum); `orderId` typeahead; `reasonCodeId` (enum); `requestedFrom`/`To` (`date`); `reversalNumber` (text) |
| **Row actions** | View · Approve · Reject · Post |
| **Toolbar** | Request (receipt picker, `POSTED` only) · Export |
| **Modals** | Request `md` (reason + note; shows moved-on check result); Approve / Reject `md`; Post confirm `md`; refusal in-modal |
| **Export columns** | grid + `createdByName`, `updatedByName` |

WS-324 *Receipts* tab lists the order's receipts with the same columns and actions.

---

## 6. Out of scope (explicit decisions)

| Baseline item | Decision | Reason | Revisit |
|---|---|---|---|
| Failed-backflush queue (COGI) | not built | R-06, `MD-10` | — |
| Partial receipt reversal | not supported | whole-movement mirror | adjustment |
| Unbuild / disassembly | not built | R-07 | code-list row |
| Cost arithmetic and settlement | `mfg-costing-close.contract.md` | cited | — |
| QC dispositions / rework orders | `mfg-qc-rework.contract.md`, core `p8-06` | cited | — |
| Subcontract receipt specifics | `mfg-subcontracting.contract.md` | cited | — |
| Mobile receipt | none | R-13 | — |

---

## 7. Amendments

| Date | Row IDs affected | Change | Found by |
|---|---|---|---|
| 2026-10-22 | all | v0 derived from `FRD-MFG.md`, code evidence and research catalogue; unratified | contract derivation (P10 design) |
| 2026-10-22 | `PRC-GRD-13`, `-14`, `PRC-T4-01`, `-03`, `-05`, `-08`, §0 | R29: named supply status consumable (F2, MD-30); cumulative genealogy (F14, MD-41); MTO reservation only into an allocatable status (F15); `extendedCost`, type-default basis (F19, MD-34); abnormal scrap MFG-side (F20); absorption built here (F23, MD-37); one in-process gate `INPROCESS_INSPECTION_OPEN` (F27); holds found by holder (MD-36) | `R29-functional-review-mfg.md` |
| 2026-10-23 | §0, `PRC-GRD-01`, `-28`, `PRC-UNR-09`, `PRC-T4-01`, `-11`, `-14`, `-15`, Source column, `PRC-OPEN-05`, `-06` | R31: holds closed explicitly (F-MF-002); bonded output rows (F-MF-010); Legal Metrology declaration rows for FR-678 (F-MF-017); Source FR filled on every rule row (F-MF-018); `ORDER_HAS_OPEN_RECEIPT` one field (F-MF-019); reversal transformation additive, SEAM-M6 (F-MF-021); DECIDE rows applied | `R31-functional-review-mfg.md`, `R31-decisions.md` |
| 2026-10-22 | T1, §9 | Consistency pass: no receipt on `COMPLETED` (MD-14), reversal refused while a settlement is live (MD-18), `:approve` on reversals (MD-20), `403` (MD-21), `PENDING_APPROVAL → DRAFT` (MD-22), `gate_entry_id` (MD-26) | FRD-MFG §9 |
| 2026-10-25 | R32 (`D-20` items 3, 13a, 20): §12 — batch and unit-serial receipts, PDI-passed units only for PDI items, no negative backflush of lot / serial items, conversion absorbed per receipt (FR-828) |

---

## 8. Invariants and scenarios this workflow must not break

| Invariant | Rows that carry it | Scenarios that prove it |
|---|---|---|
| `L-1` / `I-1` one balanced movement per receipt | `PRC-T4-01`, `PRC-GRD-19`, `PRC-UNR-03` | `WH-SC-625`, `WH-SC-627`, `WH-SC-630` |
| All-or-nothing backflush | `PRC-GRD-12`, `PRC-UNR-02` | `WH-SC-626` |
| Tolerances | `PRC-GRD-05`, `-06` | `WH-SC-628`, `WH-SC-629` |
| Maker–checker on scrap / reversal | `PRC-GRD-15`, `-26` | `WH-SC-631`, `WH-SC-634` |
| Expiry carried to FG | `PRC-GRD-08` | `WH-SC-632` |
| `L-12` genealogy | `PRC-T4-05`, `-11`, `PRC-UNR-05` | `WH-SC-633` |
| `L-3` correction is reversal | `PRC-T1-10`…`-13`, `PRC-GRD-22` | `WH-SC-634`, `WH-SC-635` |
| `L-8` period-bound | `PRC-GRD-17`, `-25` | — (`WH-SC-021` core) |
| Consumption policy | `PRC-GRD-11` | `WH-SC-624` |

---

## 9. Open rows

| ID | Contradiction / hole | Proposed resolution | Authority | Status |
|---|---|---|---|---|
| PRC-OPEN-01 *(resolved — MD-22)* | The ladder gives `PENDING_APPROVAL` no exit except `POSTED`; an approver who disagrees, or a post refused at approval (`PRC-GRD-12` after stock moved), has nowhere to go | add `PENDING_APPROVAL → DRAFT` (Return, note) — `PRC-T1-07` | FRD §5 | resolved |
| PRC-OPEN-02 *(resolved — MD-18)* | FR-649 returns a `COMPLETED` order to `IN_PROGRESS` on reversal, but a `DRAFT`/`APPROVED` settlement may already exist (`WH-SC-642` keeps the order `COMPLETED` with a pending settlement); reopen is refused in that state (FR-634) | refuse reversal while a live settlement exists (`PRC-GRD-24`) | FR-649 vs FR-634 | resolved |
| PRC-OPEN-03 *(resolved — MD-20)* | Persona table (§2) names `whm_production_receipts:approve_reversal`; §7 permissions have `whm_production_receipt_reversals:approve` and no `approve_reversal` verb | use §7 (`whm_production_receipt_reversals:approve`) | FRD §2 vs §7 | resolved |
| PRC-OPEN-04 *(resolved — MD-21: `403`)* | Self-approval codes return `409` here; the house uses `403` (`MPR-GRD-19`, `MRQ-GRD-05`) | ratify family-wide | — | resolved |
| PRC-OPEN-05 *(resolved — R31-decisions DECIDE: default stands; F-MF-021)* | "A reversing transformation is recorded" — `whb_transformations` has no reversal semantics and requires `base_quantity > 0` | a `PRODUCTION_REVERSAL` row linked to the original, same inputs/outputs as positive quantities — **no schema change** (`V500035` has no `CHECK` on `transformation_type`, `:24`); the trace reading it as a cancel marker is **SEAM-M6**, owned by `p0` and carried in `P10-07`; until then the trace over-includes (safe for a recall) — `PRC-T4-11`, FRD §3.2 | FR-649, evidence §3 | resolved |
| PRC-OPEN-06 *(resolved — R31-decisions DECIDE: default stands)* | Whether a scrap-only final receipt (no good output) is legal | allowed (`PRC-GRD-02`; SAP scrap-only confirmation) | derived | resolved |

## 12. R32 rules (PRD 2026-10-24, `D-20`)

Owning task: `issues/p10-07.md` `## R32 additions (PRD 2026-10-24)` (FR-828); the PDI half is `mfg-pdi-unit-registry` (`p10-22`).

| ID | Rule | Refusal / effect | Source |
|---|---|---|---|
| PRC-GRD-30 | A receipt of a batch-produced order names its batch; lot code = `batch_no`; unit-serial outputs are the batch's assigned serials that completed the last stage (never typed) and, for a `pdi_required` item, hold a signed `PASS` certificate | `422 BATCH_REQUIRED`; `422 SERIAL_NOT_OF_BATCH`; `422 PDI_NOT_PASSED` | FR-828 |
| PRC-GRD-31 | Backflush (receipt or stage) of a lot- or serial-controlled item never goes negative whatever `negative_stock_mode` (`D-20` item 13a) | `422 BACKFLUSH_SHORTAGE` | FR-828 |
| PRC-T4-20 | Posting a unit-serial receipt creates / updates the unit registry rows (`PUR-T1-20`) and turns the `PLANNED` serials into stock in the receipt status | registry `IN_STOCK` | FR-828 |
| PRC-T4-21 | The receipt's absorbed value includes the order's unabsorbed conversion pool share (`CST-T4-20`) by the FR-654 proportion; the handover envelope carries the conversion breakdown | — | FR-828 |
| PRC-T4-22 | Batch rollups (received, consumed vs required) update in the post transaction; WS-337 batch variance reads them | — | FR-828 |
