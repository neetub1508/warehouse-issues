# Functional Contract — Order amendment and versioning (purchase orders and sales orders)

> **What this is.** The functional truth for changing an approved PO or SO in `warehouse-trade`: one
> amendment document per change, its approval, the version snapshot, the push to core, the reprint and
> the version compare. Both sides share this engine on mirrored tables (`wht_po_amendments` /
> `wht_so_amendments`); a row names the side only where they differ. Rate-contract amendments are
> [trade-rate-contract](trade-rate-contract.contract.md) `TRC-T1-05`.
>
> **Status.** Derived 2026-10-22 (v0). No code exists yet.

---

## 0. Identity

| | |
|---|---|
| **Workflow** | Draft amendment (manual, from supplier acknowledgement with changes, from customer schedule revision) → submit → approve → apply: version + 1, snapshot, port push, reprint, ack reset; or reject / withdraw / cancel |
| **Module** | `warehouse-trade`; `p8-01` / `p8-02` ports |
| **Domain baseline** | FRD-TRADE FR-553, FR-590…FR-593, FR-611, `TRD-04`, `OD-36` · R28 §4 A5 |
| **Owning task body** | `issues/p9-11.md` |
| **Primary tables** | `wht_po_amendments`, `wht_po_amendment_changes`, `wht_purchase_order_versions`, `wht_purchase_order_line_versions`, `wht_po_schedule_line_versions`; sales mirror `wht_so_amendments`, `wht_so_amendment_changes`, `wht_sales_order_versions`, `wht_sales_order_line_versions`, `wht_so_schedule_line_versions` (`V550100`) |
| **Permission resources** | `wht_po_amendments:view/create/edit/export/submit/approve/cancel` · `wht_so_amendments:` same |
| **Routes** | WS-296 `/warehouse/trade/purchase/amendments`, WS-307 `/warehouse/trade/sales/amendments`; version tabs on WS-293 / WS-304 · mobile: none |
| **Contract status / version** | `derived` · `v0 — 2026-10-22` |

**Fields.** Amendment: `amendment_number` (`<order_number>-A<nn>`, at submit), `order_id`,
`base_version_no`, `reason_code`, `origin` (`MANUAL`/`ACK_CHANGES`/`CUSTOMER_SCHEDULE`), `status`,
`value_before`, `value_after`, `value_delta`, `approval_request_id`, `applied_at`. Change row:
`change_type` (`LINE_QTY`, `LINE_RATE`, `LINE_DISCOUNT`, `LINE_ADD`, `LINE_CANCEL`, `SCHEDULE_ADD`,
`SCHEDULE_QTY`, `SCHEDULE_DATE`, `SCHEDULE_CANCEL`, `VALIDITY_TO`, `CEILING`, `TERMS`, `DELIVER_TO`,
`TOLERANCE`), `line_id`, `schedule_line_id`, `field_name`, `old_value`, `new_value` (TEXT, typed by
`change_type`), `in_firm_zone`. Version snapshot: every header / line / schedule column of the order at
`version_no`, `snapshot_at`, `amendment_id`.

### Acceptance checks

| # | Expects | Delivered by |
|---|---|---|
| A1 | Quantity never below committed (`WH-SC-541`) | `TOA-GRD-02` |
| A2 | Rate change on un-received qty; version 2; port push; amendment print; ack reset (`WH-SC-542`) | `TOA-T4-01`…`-04` |
| A3 | One open amendment; releases refused meanwhile (`WH-SC-543`) | `TOA-GRD-01`, `-04` |
| A4 | Approval on new total and delta (`WH-SC-544`) | `TOA-T1-02` |
| A5 | Compare and reprint any version (`WH-SC-545`) | `TOA-T4-05` |
| A6 | Counterparty, type, currency, company not amendable (`WH-SC-546`) | `TOA-GRD-03` |

## 1. T1 — State machine

| Status | Reachable via | Exits via | Kind |
|---|---|---|---|
| `DRAFT` | `-01`, return | `-02`, `-05` | initial |
| `SUBMITTED` | `-02` | `TAM` | active |
| `APPLIED` | `-03` | none | terminal |
| `REJECTED` | `TAM` | none (a new amendment may be drafted) | terminal |
| `CANCELLED` | `-05` | none | terminal |

| ID | From | Action | To | Guard | Actor | Side effects | Comment | UI |
|---|---|---|---|---|---|---|---|---|
| TOA-T1-01 | — | Draft (manual / from ack / from schedule import) | `DRAFT` | `TOA-GRD-01` | `:create` + order `:amend` | change rows computed against the current version | reason code | order row action *Amend* |
| TOA-T1-02 | `DRAFT` | Submit | `SUBMITTED` | `TOA-GRD-02`, `-03`, `-05` | `:submit` | number; `TAM-T1-03` doc `PO_AMENDMENT`/`SO_AMENDMENT` evaluated **twice** — on `value_after` and on `value_delta` — the request takes the union of levels of both matches (stricter applies); conditions `manual_rate`, `below_floor_price` re-evaluated on changed lines | no | Submit |
| TOA-T1-03 | `SUBMITTED` | Approved | `APPLIED` | `TOA-GRD-06` (re-check at apply) | approver | `TOA-T4-01`…`-04` in one transaction | — | WS-285 |
| TOA-T1-04 | `SUBMITTED` | Rejected / returned | `REJECTED` / `DRAFT` | `TAM` | approver | ack-with-changes origin → follow-up logged | yes | WS-285 |
| TOA-T1-05 | `DRAFT` | Cancel | `CANCELLED` | — | maker | — | no | row action |

### 1.3 Guards

| ID | Predicate | Refusal |
|---|---|---|
| TOA-GRD-01 | Order status ∈ {`APPROVED`, `ISSUED`, `ACKNOWLEDGED`}; no other amendment `DRAFT`/`SUBMITTED` for the order (partial unique index) | `409 TRADE_AMENDMENT_OPEN` |
| TOA-GRD-02 | Per line: new qty ≥ received (PO) / shipped (SO) + in-flight (open gate entry, unposted GRN, released-not-received — PO; picked-not-shipped, released-not-picked — SO) read from core; schedule qty ≥ released on that schedule line; BLANKET Σ schedule = new line qty | `422 TRADE_AMEND_BELOW_COMMITTED {received, inFlight}` |
| TOA-GRD-03 | Not amendable: `po_type`/`so_type`, counterparty, company, currency, item of an existing line (cancel + add instead) | `422 TRADE_FIELD_NOT_AMENDABLE` |
| TOA-GRD-04 | While an amendment is open, releases on its lines and short-close of the order are refused | `409 TRADE_AMENDMENT_OPEN` |
| TOA-GRD-05 | Rate change applies to un-received / unshipped quantity only (`OD-36`): the change row records `effective_quantity`; a rate change on a fully received line is refused | `422 TRADE_RATE_CHANGE_NOTHING_OPEN` |
| TOA-GRD-06 | At apply: base version still current and committed quantities still satisfy `TOA-GRD-02` (a receipt may have landed since submit) | `409 TRADE_AMENDMENT_STALE` — amendment returned to `DRAFT` with recomputed figures |
| TOA-GRD-07 | Counterparty not blocked when the amendment increases quantity or adds a line | `422 TRADE_SUPPLIER_BLOCKED` / `TRADE_CUSTOMER_BLOCKED` |
| TOA-GRD-08 | Validity extension keeps rate-contract validity (contract still approved on the new dates) or the line is re-priced manually (`manual_rate`) | field `422` |

### 1.4 Unreachable

| ID | Forbidden | Why |
|---|---|---|
| TOA-UNR-01 | Editing an order outside an amendment after approval | no edit path (`TAM-UNR-03`, `TPO-UNR-03`) |
| TOA-UNR-02 | Overwriting or deleting a version snapshot | append-only; trigger refuses UPDATE/DELETE |
| TOA-UNR-03 | Applying an amendment without the port push succeeding | same transaction (`TOA-T4-02`) |

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from |
|---|---|---|---|
| TOA-T2-01 | Draft / edit / cancel | `:create` / `:edit` / maker | `DRAFT` |
| TOA-T2-02 | Submit | `:submit` | `DRAFT` |
| TOA-T2-03 | Approve | `:approve` (`TAM`) | `SUBMITTED` |
| TOA-T2-04 | Compare versions / reprint version | order `:view` | ≥ 1 version |
| TOA-T2-05 | Export | `:export` | — |

## 3. T3 — Time-driven rules

None of its own; pending approval escalation is `TAM-T3-01`.

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in |
|---|---|---|---|
| TOA-T4-01 | Applied | changes written to the order; `version_no` + 1; snapshot rows for the new version (version 1 was written at approval) | `OrderAmendmentService.apply` |
| TOA-T4-02 | Applied | PO: `WhPurchaseOrderPort.amendOrder` (`POS-T1-07`, `amendmentReason`, idempotency `WHT_PO_AMENDMENT:<id>`) on the trade PO's one core PO — line qty / date / rate, added lines, schedule lines (`FIRM` and `FORECAST`), `cancelScheduleLine` for removed unreceived lines; SO: `WhDemandOrderPort.amendDemand` / `cancelLine` (`POS-T1-12`) on the SO's one core demand order — firm and `FORECAST` schedule kept equal to the trade schedule. Core's `POS-GRD-09` (never below received / allocated + picked + shipped) is the backstop of `TOA-GRD-02` | same transaction; refusal rolls back (`TPO-T4-03` pattern) |
| TOA-T4-03 | Applied | ack status → `PENDING` (PO: supplier must re-acknowledge; SO: a new acknowledgement print is due); rate-contract consumption adjusted (`TRC-T4-01`); PR allocations adjusted for cancelled lines (`TPR-T1-07`) | same |
| TOA-T4-04 | Applied | print `PURCHASE_ORDER` / `SALES_ORDER_ACK` with banner *Amendment No. n dated d — supersedes version n−1* and a change summary | renderer |
| TOA-T4-05 | Compare | backend diff of any two snapshots (header, lines, schedule), field by field | `OrderVersionService` |
| TOA-T4-06 | SO amendment of origin `CUSTOMER_SCHEDULE` | changes with `in_firm_zone = true` counted for `SCHEDULE_VOLATILITY` (`TCE-T4-03`) | evaluation run reads change rows |

## 5. T5 — Screen contract

WS-296 / WS-307 (reference **Service Vehicle**): grids `wht_po_amendments` / `wht_so_amendments`,
scopes `WAREHOUSE_TRADE_PO_AMENDMENT` / `WAREHOUSE_TRADE_SO_AMENDMENT`. Tiles: draft, submitted,
applied (period), rejected (period), firm-zone changes (SO). Columns: `amendmentNumber`, `orderNumber`,
`counterpartyName`, `baseVersionNo`, `origin`, `reason`, `valueBefore`, `valueAfter`, `valueDelta`,
`status`, `appliedAt`, audit. Filters: `counterpartyId`, `status`, `origin`, `reasonCode`,
`appliedFrom`/`To`. Actions: View (change rows, old → new) · Edit · Submit · Cancel · Print.
**Versions tab** on the order: list of versions, *Compare* (two pickers), *Reprint*.

## 6. Out of scope

| Item | Decision |
|---|---|
| Retrospective rate change on received quantity | `OD-36` — accounting |
| Amending a closed / short-closed / cancelled order | not offered; a new order is raised |

## 7. Amendments

| Date | Rows | Change | Found by |
|---|---|---|---|
| 2026-10-22 | all | v0 derived | TRADE author |

## 8. Invariants and scenarios

`WH-SC-537`, `WH-SC-541`…`WH-SC-546`, `WH-SC-560`.

## 9. Open rows

`OD-36`.
