# Functional Contract — Returns: the return receipt, the optional RMA, grading, disposition, return to vendor, recall and the supplier claim register

> **What this is.** The functional truth for the core returns stream: **the return receipt is the primary
> object and the RMA is optional**, matched to it later; returns land in a dedicated status, are graded at
> receipt, and leave through a disposition registry that posts a specified movement. It also owns return to
> vendor as an ordinary outbound, recall (quarantine in place, list every consignee, release every
> reservation) and **one supplier claim register**. The trade side — the sales return authorisation a
> customer asks for — is [`trade-sales-return-authorisation`](trade-sales-return-authorisation.contract.md)
> and reaches this contract through the RMA-creation port ([`po-schedule-port`](po-schedule-port.contract.md)
> §8a); it is not restated here.
>
> **Status.** Derived 2026-10-23 (v0) from `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` §6.16 (`FR-269`…`FR-275`,
> `FR-280`) and `FR-459`, read with `D-16` (`RN-016`, `RN-024`, `RN-051`: RTO, marketplace returns and the
> `OBSOLESCENCE` claim type are removed) and `D-16` item 6 (warehouse never generates a debit or credit
> note), and verified against the built code in `classic`. Not ratified. Written for R30 `CP-FR-007`
> row 15 / `D-17` item 1.

---

## 0. Identity

| | |
|---|---|
| **Workflow** | Return receipt `RECEIVED` → Post (stock in, returns status) → match an RMA (optional, any time) → grade lines → disposition (one movement per line) → `DISPOSITIONED` · Reverse. RMA `OPEN` → `APPROVED` → `MATCHED` / `EXPIRED` / `CANCELLED`. Supplier return (WS-084) through a `VENDOR_RETURN` demand order. Recall `OPEN` → notify → responses → `CLOSED`. Supplier claim `DRAFT` → `SUBMITTED` → `ACKNOWLEDGED` → decided → `SETTLED` / `WITHDRAWN` |
| **Module** | `warehouse-base` (`RETURN_TYPE` code list, `whb_dispositions`, `whb_condition_codes`) + `warehouse` (`WhReturnReceiptService`, `WhReturnReceiptPostingService`, `WhRmaService`, `WhRmaExpiryJob`, `WhReturnGradingService`, `WhSupplierReturnService`, `WhRecallService`, `WhRecallPostGuard`, `WhSupplierClaimService`) |
| **Domain baseline** | `D-16` items 2, 3, 6 · `L-10`, `L-12`, `L-14` · `RJ-003`, `RJ-010` · [`costing-valuation`](costing-valuation.contract.md) `CVL-T4-03` (return cost rule) · [`movement-post-reverse`](movement-post-reverse.contract.md) |
| **Owning tasks** | `issues/p0-05.md` (`RETURN_TYPE`, status change as a movement) · `issues/p2-12.md` (return receipt, RMA, disposition v1 — PARTIALLY VOID) · `issues/p2-13.md` (supplier return) · `issues/p5-13.md` (grading — PARTIALLY VOID) · `issues/p5-14.md` (recall) · `issues/p5-23.md` (supplier claim register — PARTIALLY VOID) |
| **Primary tables** | `wh_return_receipts`, `wh_return_receipt_lines`, `wh_rmas`, `wh_rma_lines` (`V510050`), `wh_return_gradings`, `wh_supplier_returns` (`V510020`), `wh_recalls`, `wh_recall_lines`, `wh_supplier_claims`, `wh_supplier_claim_lines` |
| **Status columns** | return receipt `RECEIVED`/`POSTED`/`DISPOSITIONED`/`REVERSED` · RMA `OPEN`/`APPROVED`/`MATCHED`/`EXPIRED`/`CANCELLED` · supplier return `DRAFT`/`APPROVED`/`PICKED`/`DISPATCHED`/`CLOSED`/`CANCELLED` · recall `OPEN`/`CLOSED` (line response `PENDING`/`NOTIFIED`/`ACKNOWLEDGED`/`STOCK_RETURNED`/`NO_RESPONSE`) · supplier claim `DRAFT`/`SUBMITTED`/`ACKNOWLEDGED`/`APPROVED`/`PART_APPROVED`/`REJECTED`/`SETTLED`/`WITHDRAWN` |
| **Permission resources** | `wh_return_receipts:{view,create,edit,post,match_rma,disposition,approve,reverse,export}` · `wh_rmas:{view,create,edit,approve,match,expire,cancel,export}` · `wh_return_gradings:{view,grade,export}` · `wh_recalls:{view,create,notify,respond,close,export}` · `wh_supplier_claims:{view,create,edit,submit,acknowledge,decide,settle,withdraw,export}` · `wh_supplier_returns:*` |
| **Routes** | WS-135 `/warehouse/inbound/returns` · WS-136 `/warehouse/inbound/rmas` · WS-137 `/warehouse/inbound/return-gradings` · WS-012 `/warehouse/catalogues/dispositions` · WS-084 `/warehouse/inbound/supplier-returns` · WS-139 `/warehouse/inventory/recalls` · WS-248 / WS-249 `/warehouse/inbound/supplier-claims` · WS-250 `/warehouse/reports/supplier-claim-ageing` · mobile: none (`D-16` item 7) |
| **Contract version** | `v0 — 2026-10-23` |

### Acceptance checks

| # | Expects | Delivered by |
|---|---|---|
| A1 | A blind return is representable; an RMA is matched later, never by re-receiving (`WH-SC-057`) | `RMR-T1-01`, `-04`, `RMR-UNR-01` |
| A2 | Return type is a day-one column read by disposition (`WH-SC-057`) | `RMR-GRD-01`, `-08` |
| A3 | Returns never land in available (`WH-SC-057`) | `RMR-GRD-03` |
| A4 | Grading at receipt (`WH-SC-341`) | `RMR-T1-06`, `RMR-GRD-06` |
| A5 | Disposition registry; scrap / donate explicit and approved; no refund anywhere (`WH-SC-057`) | `RMR-T1-07`, `-08`, `RMR-UNR-02`, `-03` |
| A6 | Return to vendor is an ordinary outbound relieving its GRN's layer (`WH-SC-072`) | `RMR-T4-03` |
| A7 | Recall in one transaction (`WH-SC-137`) | `RMR-T1-14`, `RMR-T4-04` |
| A8 | One supplier claim register with ageing (`WH-SC-365`) | `RMR-T1-17`…`-22`, `RMR-T5-07` |

---

## 1. T1 — State machine

### 1.1 Status inventory

| Entity | Status | Reachable via | Exits via | Kind |
|---|---|---|---|---|
| Return receipt | `RECEIVED` | `RMR-T1-01` | `-02` | initial |
| Return receipt | `POSTED` | `RMR-T1-02` | `-07`, `-09` | active (lines graded / dispositioned) |
| Return receipt | `DISPOSITIONED` | `RMR-T1-07` (last line decided) | none | **terminal** |
| Return receipt | `REVERSED` | `RMR-T1-09` | none | **terminal** |
| RMA | `OPEN` → `APPROVED` → `MATCHED` / `EXPIRED` / `CANCELLED` | `RMR-T1-10`…`-13` | — | ladder |
| Recall | `OPEN` → `CLOSED` | `RMR-T1-14`, `-16` | — | ladder |
| Supplier claim | `DRAFT` → `SUBMITTED` → `ACKNOWLEDGED` → `APPROVED`/`PART_APPROVED`/`REJECTED` → `SETTLED`; `WITHDRAWN` | `RMR-T1-17`…`-22` | — | ladder |

### 1.2 Transitions

| ID | From | Event | To | Guard | Actor | Side effects | Reason? | Source |
|---|---|---|---|---|---|---|---|---|
| RMR-T1-01 | — | Create a return receipt **with or without an RMA**: site, owner, `return_type`, customer, original shipment / demand order (optional), reason, lines (item, UoM, lot, serial, received status, condition) | `RECEIVED` | `RMR-GRD-01`…`-04` | `wh_return_receipts:create` / `:edit` | number `RR…` | no | FR-269, FR-270 |
| RMR-T1-02 | `RECEIVED` | **Post** | `POSTED` | `RMR-GRD-01`…`-04` re-checked | `:post` | `RMR-T4-01` | no | FR-269, FR-271 |
| RMR-T1-04 | `RECEIVED` · `POSTED` | **Match an RMA** (a screen action, never a re-receipt) | unchanged; RMA → `MATCHED` | `RMR-GRD-05` | `:match_rma` (receipt) / `wh_rmas:match` (RMA) | `rma_id`, `rma_matched_at` | no | FR-269 |
| RMR-T1-06 | `POSTED` | **Grade** a line: condition grade, note, photo, serial and lot verified, measured weight + verdict, packaging intact, disposition | unchanged | `RMR-GRD-06` | `wh_return_gradings:grade` | a `wh_return_gradings` row | no | FR-272 |
| RMR-T1-07 | `POSTED` | **Disposition** lines (restock, quarantine, scrap in v1; refurbish, repack, return to vendor, return to client, hold for client, donate in v2) | `DISPOSITIONED` when every line is decided | `RMR-GRD-07`, `-08` | `:disposition` | `RMR-T4-02` | per registry | FR-273 |
| RMR-T1-08 | line disposition `SCRAP` / `DONATE` pending | Approve / reject the value-destroying disposition | posted / refused | approver ≠ the user who chose the disposition, else `403 SCRAP_SELF_APPROVAL`; `SCRAP_NOT_PENDING` | `:approve` | the scrap movement posts on approval | **yes** | FR-273 |
| RMR-T1-09 | `POSTED` (no disposition yet) | Reverse | `REVERSED` | `RETURN_HAS_DISPOSITION` once any line is decided | `:reverse` | a reversal movement | **yes** | FR-269 |
| RMR-T1-10 | — | Create an RMA: customer, original order, reason, expected condition, lines, expiry date | `OPEN` | expiry ≥ RMA date, else `422 RMA_EXPIRY_BEFORE_DATE` | `wh_rmas:create` / `:edit` | — | no | FR-269 |
| RMR-T1-11 | `OPEN` | Approve | `APPROVED` | `OPEN` only (`RMA_NOT_OPEN`) | `wh_rmas:approve` | — | no | FR-269 |
| RMR-T1-12 | `OPEN` · `APPROVED` | Expire (manual, or `RMR-T3-01`) | `EXPIRED` | live only (`RMA_NOT_LIVE`) | `wh_rmas:expire` / job | — | no | FR-269 |
| RMR-T1-13 | `OPEN` · `APPROVED` | Cancel | `CANCELLED` | live only | `wh_rmas:cancel` | — | **yes** | FR-269 |
| RMR-T1-14 | — | **Initiate recall**: item, lot(s), class | `OPEN` | `RMR-GRD-09` | `wh_recalls:create` | `RMR-T4-04` in **one** transaction | **yes** | FR-280 |
| RMR-T1-15 | `OPEN` | Notify consignees; record each line's response | `OPEN` | `RECALL_NOTHING_TO_NOTIFY`, `RECALL_LINE_NOT_NOTIFIED` | `:notify` / `:respond` | WhatsApp where the order / shipment carries a phone, else manual | no | FR-280 |
| RMR-T1-16 | `OPEN` | Close | `CLOSED` | no pending lines (`RECALL_LINES_PENDING`) | `:close` | — | no | FR-280 |
| RMR-T1-17 | — | Create a supplier claim: supplier, type, source document, lines referencing the receipt line or movement that evidences them, claimed value, currency | `DRAFT` | `RMR-GRD-10` | `wh_supplier_claims:create` / `:edit` | number `CLM…` | no | FR-459 |
| RMR-T1-18 | `DRAFT` | Submit | `SUBMITTED` | `RMR-GRD-11` | `:submit` | ageing clock starts | no | FR-459 |
| RMR-T1-19 | `SUBMITTED` | Acknowledge (supplier accepted receipt of the claim) | `ACKNOWLEDGED` | `RMR-GRD-11` | `:acknowledge` | — | no | FR-459 |
| RMR-T1-20 | `ACKNOWLEDGED` | Decide | `APPROVED` / `PART_APPROVED` / `REJECTED` | decision complete and ≤ claimed (`SUPPLIER_CLAIM_DECISION_INCOMPLETE` / `_OVER_CLAIM`); a rejection reason (`_REJECTION_REASON_REQUIRED`) | `:decide` | — | rejection: **yes** | FR-459 |
| RMR-T1-21 | decided | Settle: settlement mode, reference, date, settled amount; any balance explicitly written off | `SETTLED` | `SUPPLIER_CLAIM_SETTLEMENT_MODE_INVALID` / `_REF_REQUIRED` / `_DATE_INVALID` / `_BALANCE_NOT_WRITTEN_OFF` | `:settle` | the claim leaves the ageing report on its settlement date with `ageing_bucket_at_close` | no | FR-459 |
| RMR-T1-22 | `DRAFT` · `SUBMITTED` · `ACKNOWLEDGED` | Withdraw | `WITHDRAWN` | note required (`SUPPLIER_CLAIM_WITHDRAW_NOTE_REQUIRED`) | `:withdraw` | — | **yes** | FR-459 |
| RMR-T1-23 | — | Create a supplier return (vendor, origin GRN / lot, lines) | `DRAFT` | `RMR-GRD-12` | `wh_supplier_returns:create` / `:edit` (`DRAFT` only, `SUPPLIER_RETURN_NOT_DRAFT`) | — | no | FR-275 |
| RMR-T1-24 | `DRAFT` | Approve | `APPROVED` | `RMR-GRD-13` | `wh_supplier_returns:approve` | `RMR-T4-03` (the `VENDOR_RETURN` demand order raised and allocated) | no | FR-275 |
| RMR-T1-25 | `APPROVED` → `PICKED` → `DISPATCHED` | Pick and despatch of its demand order | as named | the ordinary outbound guards (`outbound-despatch`) | system (effects of the demand order) | `RMR-T4-03` | no | FR-275 |
| RMR-T1-26 | `DISPATCHED` | **Close** — the supplier has the goods | `CLOSED` | only from `DISPATCHED`, else `SUPPLIER_RETURN_NOT_DISPATCHED` | `wh_supplier_returns:close` (`WhSupplierReturnController.java:256-257`) | `RMR-T4-06` | no | FR-275 |
| RMR-T1-27 | `DRAFT` · `APPROVED` · `PICKED` | Cancel | `CANCELLED` | cancellable only from those three (`WhSupplierReturn.java:183-184`), else `SUPPLIER_RETURN_NOT_CANCELLABLE`; a reason, else `SUPPLIER_RETURN_CANCEL_REASON_REQUIRED` | `wh_supplier_returns:cancel` | — | **yes** | FR-275 |

### 1.3 Guards

| ID | Predicate | Refusal | Backstop | Source |
|---|---|---|---|---|
| RMR-GRD-01 | `return_type` is an active `RETURN_TYPE` code: customer return, refused delivery, cancelled in transit, vendor return, recall, client withdrawal, warranty, exchange (`D-16`: the retail values are not seeded) | `422 RETURN_TYPE_INVALID` · `returnType` | composite FK to the code list | FR-270 — **see §10 row 1** |
| RMR-GRD-02 | Reason valid (note when required); at least one line; each line resolves (item, UoM, lot, serial; serial quantity 1); the original shipment, when named, is `DISPATCHED`/`DELIVERED` | `422 RETURN_REASON_INVALID` / `_REASON_NOTE_REQUIRED` / `RETURN_NO_LINES` / `RETURN_LINE_UNRESOLVED` / `RETURN_LINE_SERIAL_QUANTITY` / `RETURN_LINE_SHIPMENT_INVALID` | — | FR-269 |
| RMR-GRD-03 | A line's received status is `RETURNED` or `PENDING_RESOLUTION` — on hand and **not allocatable**; never `AVAILABLE` | `422 RETURN_LINE_STATUS_INVALID` · `lines[i].stockStatusCode` | `whb_stock_statuses.is_allocatable` | FR-271 |
| RMR-GRD-04 | A line's condition is an active `whb_condition_codes` row | `422 RETURN_LINE_CONDITION_INVALID` | FK | FR-272 |
| RMR-GRD-05 | Match: the RMA is live (`OPEN`/`APPROVED`), not expired, not already matched; the receipt has no RMA yet | `422 RETURN_RMA_INVALID` / `RETURN_RMA_EXPIRED` / `RETURN_RMA_ALREADY_MATCHED` / `RETURN_RMA_REQUIRED` | — | FR-269 |
| RMR-GRD-06 | Grade: the line resolves and is not yet dispositioned; a condition is chosen; a weight check has a verdict; the chosen disposition is offered for the return type; a recalled lot is never graded to a restock | `422 GRADING_LINE_UNRESOLVED` / `GRADING_LINE_DISPOSITIONED` / `GRADING_CONDITION_REQUIRED` / `GRADING_WEIGHT_VERDICT_REQUIRED` / `GRADING_DISPOSITION_NOT_OFFERED` / `GRADING_LOT_RECALLED` | — | FR-272 |
| RMR-GRD-07 | Disposition: a line is decided once; the disposition is offered (v1: `RESTOCK_SELLABLE`, `QUARANTINE`, `SCRAP`); its registry movement type is supported | `422 DISPOSITION_NO_LINES` / `DISPOSITION_LINE_UNRESOLVED` / `409 DISPOSITION_ALREADY_DECIDED` / `422 DISPOSITION_NOT_OFFERED` / `DISPOSITION_MOVEMENT_TYPE_UNSUPPORTED` | `whb_dispositions.movement_type_code`, `target_stock_status_code` | FR-273 |
| RMR-GRD-08 | A recalled lot is never restocked under any disposition | `422 DISPOSITION_LOT_RECALLED` | `WhRecallPostGuard` (`RECALLED_LOT_NOT_ALLOCATABLE`) | FR-270, FR-280 |
| RMR-GRD-09 | Recall: lot exists and is the item's; no open recall for the lot; caller is neither owner-scoped nor (for Initiate) site-scoped; no period override pending; no staged picks of the lot | `422 LOT_NOT_FOUND` / `LOT_ITEM_MISMATCH` / `409 RECALL_ALREADY_OPEN` / `403 RECALL_OWNER_SCOPE_REQUIRED` / `RECALL_WAREHOUSE_SCOPE_REQUIRED` / `409 RECALL_PERIOD_OVERRIDE_PENDING` / `RECALL_STAGED_ORDERS` | one transaction | FR-280 |
| RMR-GRD-10 | Claim: type valid (short shipment, damage in transit, quality reject, price; expiry and breakage per the FRD); date not future; source valid and unchanged; each line cites a **posted** receipt line of the same supplier, once, not already claimed, within the evidenced quantity and unit cost, in the claim currency | `422 SUPPLIER_CLAIM_TYPE_INVALID` / `_DATE_FUTURE` / `_SOURCE_INVALID` / `_LINE_NO_RECEIPT` / `_LINE_RECEIPT_NOT_POSTED` / `_LINE_OTHER_SUPPLIER` / `_LINE_DUPLICATE` / `_LINE_ALREADY_CLAIMED` / `_LINE_OVER_EVIDENCE` / `_LINE_OVER_UNIT_COST` / `_LINE_CURRENCY_MISMATCH` · `409 _SOURCE_CHANGED` / `_SITE_CHANGED` | — | FR-459 — **see §10 rows 2, 3** |
| RMR-GRD-11 | A claim moves only along its ladder | `409 SUPPLIER_CLAIM_TRANSITION_REFUSED` naming from, to and verb | `WhSupplierClaimValidationService.requireFrom` | FR-459 |
| RMR-GRD-12 | A supplier return names a valid origin (GRN / lot of the vendor) and its site never changes after create | `SUPPLIER_RETURN_ORIGIN_INVALID`; `SUPPLIER_RETURN_WAREHOUSE_IMMUTABLE` | — | FR-275 |
| RMR-GRD-13 | Approval is maker ≠ checker | `403 SUPPLIER_RETURN_SELF_APPROVAL` (`WhSupplierReturnValidationService.java:147`) | — | FR-275 |

### 1.4 Unreachable

| ID | Must never happen | Why it cannot | Source |
|---|---|---|---|
| RMR-UNR-01 | A return that cannot be received without an RMA, or an RMA matched by receiving the goods again | `RMR-T1-01` takes no RMA; `RMR-T1-04` links an existing receipt | FR-269 |
| RMR-UNR-02 | A refund screen, a refund amount or a payment path in any warehouse module | `wh_return_receipts` / `wh_rmas` carry no amount or payment column (`V510050` header); warehouse emits the disposition only | FR-274 |
| RMR-UNR-03 | A disposition that silently discards stock | scrap and donate post an explicit value-destroying movement with a reason and an approver (`RMR-T1-08`) | FR-273 |
| RMR-UNR-04 | Return to vendor as a special ledger case | it is a `VENDOR_RETURN` demand order through the ordinary outbound (`RMR-T4-03`) | FR-275 |
| RMR-UNR-05 | Warehouse generating a debit note or credit note for a return to vendor or a claim | `D-16` item 6; `wh_supplier_returns.debit_note_ref` is a reference typed in, never a generated document | FR-275 |
| RMR-UNR-06 | A recall that half-applies (some positions quarantined, reservations kept) | Initiate is one transaction; any refusal rolls all of it back | FR-280 |

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from | Source |
|---|---|---|---|---|
| RMR-T2-01 | Receive / post / reverse a return | `wh_return_receipts:create` / `:post` / `:reverse` | — / `RECEIVED` / `POSTED` | FR-269 |
| RMR-T2-02 | Match an RMA | `wh_return_receipts:match_rma` · `wh_rmas:match` | live RMA | FR-269 |
| RMR-T2-03 | Grade / disposition / approve scrap | `wh_return_gradings:grade` / `wh_return_receipts:disposition` / `:approve` | `POSTED` | FR-272, FR-273 |
| RMR-T2-04 | Recall create / notify / respond / close | `wh_recalls:*` | see §1.2 | FR-280 |
| RMR-T2-05 | Supplier claim verbs | `wh_supplier_claims:{submit,acknowledge,decide,settle,withdraw}` | see §1.2 | FR-459 |
| RMR-T2-06 | Supplier return create / edit / approve / close / cancel | `wh_supplier_returns:{create,edit,approve,close,cancel}` (`WhSupplierReturnController.java:48`) | `DRAFT` / `DRAFT` / `DRAFT` / `DISPATCHED` / `DRAFT` · `APPROVED` · `PICKED` | FR-275 |

## 3. T3 — Time-driven rules

| ID | Rule | Trigger | Changes | Source |
|---|---|---|---|---|
| RMR-T3-01 | RMA expiry | `warehouse.rmas.expiry.cron` (`WhRmaExpiryJob`): a live RMA past its expiry date | `EXPIRED` | FR-269 |
| RMR-T3-02 | Supplier claim ageing: age from submission to the as-of date, bucketed; a settled claim keeps the bucket it closed in | on read (WS-250) | — | FR-459 |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in | Source |
|---|---|---|---|---|
| RMR-T4-01 | Return receipt posts | one `RETURN_RECEIPT` movement into the returns status; cost by `CVL-T4-03` (matched reversal, else `RETURN_UNMATCHED`) | `WhReturnReceiptPostingService` → writer | FR-269, FR-271 |
| RMR-T4-02 | A line is dispositioned | the registry row's movement type posts to its target status (status change in place for restock / quarantine; `SCRAP` / `ISSUE` for value-destroying ones) | same | FR-273 |
| RMR-T4-03 | A supplier return is approved | a `VENDOR_RETURN` demand order (one line per return line, same lot) is raised and allocated; picking and despatch are its effects (`PICKED`, `DISPATCHED`); an `origin_grn_id` relieves that receipt's layer | `WhSupplierReturnService`, `WhSupplierReturnDemandEffects` | FR-275 (`RJ-003`, `RJ-010`) |
| RMR-T4-04 | A recall is initiated | every allocatable position of the lot (and its splits, and every kit lot built from it) is **quarantined in place** by a status-change movement; every reservation at that grain is released with the recall reason; every shipment that carried the lot is listed with consignee and tracking; the affected-customer list exports | `WhRecallService` → writer | FR-280 |
| RMR-T4-05 | A disposition is decided | the warehouse emits it (an event per dispositioned line); nothing computes a refund | `WhReturnLineDispositionedEvents` | FR-274 |
| RMR-T4-06 | A supplier return is closed | its `VENDOR_RETURN` demand order, if still `SHIPPED`, is confirmed `DELIVERED` in the same transaction (`WhSupplierReturnService.java:281-295`) | `WhSupplierReturnService.close` | FR-275 |

## 5. T5 — Screen contract

| ID | Screen · grid · scope | Contract | Source |
|---|---|---|---|
| RMR-T5-01 | WS-135 Return Receipts · `wh_return_receipts` · `WAREHOUSE_RETURN_RECEIPT` | `returnNumber`, `returnType`, customer, RMA (blank when blind), status; actions Post · Match RMA · Disposition · Reverse by state; filter `returnType` | FR-269, FR-270 |
| RMR-T5-02 | WS-136 RMAs · `wh_rmas` · `WAREHOUSE_RMA` | `rmaNumber`, `customerName`, `originalOrderNumber`, reason, expected condition, expiry, status; `/matchable-receipts` lists blind receipts to match | FR-269 |
| RMR-T5-03 | WS-137 Return Gradings · `wh_return_gradings` · `WAREHOUSE_RETURN_GRADING` | `returnNumber`, `lineNo`, `conditionCode`, `gradeNote`, verifications, weight, packaging intact, photo, graded by / at | FR-272 |
| RMR-T5-04 | WS-012 Dispositions · `whb_dispositions` · `WAREHOUSE_DISPOSITION` | registry: `movement_type_code`, `target_stock_status_code`, approval flag | FR-273 |
| RMR-T5-05 | WS-084 Supplier Returns · `wh_supplier_returns` · `WAREHOUSE_SUPPLIER_RETURN` | vendor, origin GRN / lot, status ladder, demand order link | FR-275 |
| RMR-T5-06 | WS-139 Recalls · `wh_recalls` · `WAREHOUSE_RECALL` | lines = consignees with response; line export = affected-customer list | FR-280 |
| RMR-T5-07 | WS-248 / WS-249 Supplier Claims, WS-250 Supplier Claim Ageing | one register for every claim type; detail with lines and evidence; ageing buckets with export | FR-459 |

## 6. Out of scope

The customer-facing sales return authorisation (`trade-sales-return-authorisation`); RTO consignments,
marketplace claims and obsolescence returns (removed, `D-16`); per-client inspection checklists (v2 by
`FR-272`, no owner); refunds, credit notes and debit notes (`FR-274`, `D-16` item 6).

## 7. Amendments

| Date | Change |
|---|---|
| 2026-10-23 | v0 derived (R30 `CP-FR-007` row 15) |
| 2026-10-23 | R31: `F-CB-008` (supplier-return `RMR-T1-23`…`-27`, `RMR-GRD-12`, `-13`, `RMR-T2-06`, `RMR-T4-06`); `F-CB-022` (§10 row 1, WS-135); `RMR-OPEN-01`, `-02` decided |

## 8. Invariants and scenarios

`L-10`, `L-12`, `L-14`; `WH-SC-057`, `WH-SC-072`, `WH-SC-137`, `WH-SC-341`, `WH-SC-365`.

## 9. Open rows

| ID | Question | Default |
|---|---|---|
| RMR-OPEN-01 | `FR-275` says the emitted debit-note proposal is v2; `D-16` item 6 says warehouse never generates a debit or credit note. Is the v2 proposal withdrawn? | **DECIDED R31 (2026-10-23): default stands** — withdrawn (`D-16` item 6, `RMR-UNR-05`) |
| RMR-OPEN-02 | `FR-272` per-client inspection checklists (v2) — no live task owns them | **DECIDED R31 (2026-10-23): not withdrawn** — the checklist half stays v2, deferred against PARTIALLY VOID `P5-13`; a new task is needed when it is scheduled |

## 10. Code divergences

The FRD rule is kept; the code is what differs.

| # | File:line | FR | Difference |
|---|---|---|---|
| 1 | `warehouse-base/backend/src/main/resources/db/migration/V500010__Create_whb_code_lists_task_types_dispositions_attribute_keys.sql:155`, `:161` | FR-270 | the two retail return types the FRD removes (`RTO`, `MARKETPLACE`) are still seeded (removal pending in `P7`); BUILD-SPEC WS-135's `returnType` list carried them too and was amended (R31 `F-CB-022`) |
| 2 | `warehouse/…/entity/WhSupplierClaim.java:72` | FR-459 | the `OBSOLESCENCE` claim type and its source are still in the vocabulary (`D-16` `RN-051` removes them) |
| 3 | `warehouse/…/entity/WhSupplierClaim.java:69-77` | FR-459 | types are short shipment, damage in transit, quality reject, price; the FRD's expiry claim has no type |
