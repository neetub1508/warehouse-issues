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
| **Workflow** | Draft amendment (manual, from supplier acknowledgement with changes, from customer schedule revision, from a supplier return with intent `REPLACE`) → submit → approve → apply: version + 1, snapshot, port push, reprint, ack reset; or reject (edit and resubmit) / withdraw / cancel |
| **Module** | `warehouse-trade`; `p8-01` / `p8-02` ports |
| **Domain baseline** | FRD-TRADE FR-553, FR-590…FR-593, FR-611, `TRD-04`, `OD-36` · R28 §4 A5 |
| **Owning task body** | `issues/p9-11.md` |
| **Primary tables** | `wht_po_amendments`, `wht_po_amendment_changes`, `wht_purchase_order_versions`, `wht_purchase_order_line_versions`, `wht_po_schedule_line_versions`; sales mirror `wht_so_amendments`, `wht_so_amendment_changes`, `wht_sales_order_versions`, `wht_sales_order_line_versions`, `wht_so_schedule_line_versions` (`V550100`) |
| **Permission resources** | `wht_po_amendments:view/create/edit/export/submit/approve/cancel` · `wht_so_amendments:` same. The approver bundles hold core `warehouse:orders:port` (`TRD-13`); a zero-level (`SYSTEM`) apply calls the port as the submitter, who needs it too |
| **Routes** | WS-296 `/warehouse/trade/purchase/amendments`, WS-307 `/warehouse/trade/sales/amendments`; version tabs on WS-293 / WS-304 · mobile: none |
| **Contract status / version** | `derived` · `v1 — 2026-10-22` (R29 folded) |

**Fields.** Amendment: `amendment_number` (`<order_number>-A<nn>`, per-order counter, at submit — no number
series, FR-547), `order_id`, `base_version_no`, `reason_code`, `origin` (`MANUAL`/`ACK_CHANGES`/
`CUSTOMER_SCHEDULE` (SO)/`SUPPLIER_RETURN` (PO)), `source_supplier_return_id` (origin `SUPPLIER_RETURN`),
`status`, `value_before`, `value_after`, `value_delta`, `approval_request_id`, `applied_at`. Change row:
`change_type` (`LINE_QTY`, `LINE_RATE`, `LINE_DISCOUNT`, `LINE_ADD`, `LINE_CANCEL`, `SCHEDULE_ADD`,
`SCHEDULE_QTY`, `SCHEDULE_DATE`, `SCHEDULE_CANCEL`, `VALIDITY_TO`, `RECEIPT_CUTOFF` (PO), `CEILING`, `TERMS`,
`DELIVER_TO` (PO: receiving location **inside the same site**), `SHIP_TO` (SO: another address of the same
customer), `TOLERANCE`), `line_id`, `schedule_line_id`, `field_name`, `old_value`, `new_value` (TEXT, typed by
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
| A6 | Counterparty, type, currency, company, site not amendable (`WH-SC-546`) | `TOA-GRD-03` |
| A7 | An open amendment blocks only the schedule lines it changes; a newer customer import replaces a draft (`WH-SC-543`, `-589`) | `TOA-GRD-04`, `-10` |
| A8 | A supplier-return replacement goes through the version engine (`WH-SC-564`) | `TOA-T1-01`, `TOA-GRD-09` |

## 1. T1 — State machine

| Status | Reachable via | Exits via | Kind |
|---|---|---|---|
| `DRAFT` | `-01`, return | `-02`, `-05` | initial |
| `SUBMITTED` | `-02` | `TAM` | active |
| `APPLIED` | `-03` | none | terminal |
| `REJECTED` | `TAM` | edit → `DRAFT`, `-05` (as every trade document, FR-551) | active |
| `CANCELLED` | `-05`, `TOA-GRD-10` | none | terminal |

| ID | From | Action | To | Guard | Actor | Side effects | Comment | UI |
|---|---|---|---|---|---|---|---|---|
| TOA-T1-01 | — | Draft — manual; from ack (`TPO-T1-11`, maker = the buyer who chose *Accept changes*); from a customer schedule import (`TSO-T1-15`); from a supplier return (`TPO-T4-07`, system-drafted, maker = the buyer who submits it) | `DRAFT` | `TOA-GRD-01`, `-09`, `-10` | `:create` + order `:amend` (system for `SUPPLIER_RETURN`) | change rows computed against the current version | reason code | order row action *Amend* |
| TOA-T1-02 | `DRAFT`, `REJECTED` | Submit | `SUBMITTED` | `TOA-GRD-02`, `-03`, `-05` | `:submit` | number at first submit; `TAM-T1-03` doc `PO_AMENDMENT`/`SO_AMENDMENT`, matched on `value_after` and on the absolute `value_delta` (`TAM-GRD-09`: the match with more levels is used, a tie takes `value_after`); conditions `manual_rate`, `below_floor_price` re-evaluated on changed lines; origin `SUPPLIER_RETURN` carries only `supplier_return_replacement` (seeded zero-level `EXACT` rule) | no | Submit |
| TOA-T1-02a | `SUBMITTED` | Withdraw (`TAM-T1-09`) | `DRAFT` | no step acted | maker | — | no | *Withdraw* |
| TOA-T1-03 | `SUBMITTED` | Approved | `APPLIED` | `TOA-GRD-06` (re-check at apply) | approver / `SYSTEM` | `TOA-T4-01`…`-04` in one transaction | — | WS-285 |
| TOA-T1-04 | `SUBMITTED` | Rejected / returned | `REJECTED` / `DRAFT` | `TAM` | approver | ack-with-changes origin → follow-up logged | yes | WS-285 |
| TOA-T1-05 | `DRAFT`, `REJECTED` | Cancel | `CANCELLED` | — | maker | origin `SUPPLIER_RETURN`: the quantity returns to the PO line's `replacement_pending_quantity` and the buyer is told | no | row action |

### 1.3 Guards

| ID | Predicate | Refusal |
|---|---|---|
| TOA-GRD-01 | Order status ∈ PO {`APPROVED`, `ISSUED`, `ACKNOWLEDGED`} / SO {`APPROVED`, `ISSUED`}; no other amendment `DRAFT`/`SUBMITTED`/`REJECTED` for the order (partial unique index) — except `-10` | `409 TRADE_AMENDMENT_OPEN` |
| TOA-GRD-02 | Per line: new qty ≥ received (PO) / shipped (SO) + in-flight (open gate entry, unposted GRN, released-not-received — PO; picked-not-shipped, released-not-picked — SO) read from core; schedule qty ≥ released on that schedule line; BLANKET Σ schedule = new line qty | `422 TRADE_AMEND_BELOW_COMMITTED {received, inFlight}` |
| TOA-GRD-03 | Not amendable: `po_type`/`so_type`, counterparty, company, currency, **site** (deliver-to / dispatch site — `STO-D15`; another site is cancel + new order), item of an existing line (cancel + add instead); `DELIVER_TO` must name a receiving location inside the order's site; `SHIP_TO` an active address of the same customer | `422 TRADE_FIELD_NOT_AMENDABLE` |
| TOA-GRD-04 | While an amendment is open: a release, release cancel or line short-close on a **schedule line the amendment changes** (or on any schedule line of a line it adds, cancels or re-prices) is refused; a header short-close or cancel of the order is refused. Releases of untouched schedule lines proceed (`TPO-GRD-14`, `TSO-GRD-14`) | `409 TRADE_AMENDMENT_OPEN` |
| TOA-GRD-05 | Rate change applies to un-received / unshipped quantity only (`OD-36`): the change row records `effective_quantity`; a rate change on a fully received line is refused | `422 TRADE_RATE_CHANGE_NOTHING_OPEN` |
| TOA-GRD-06 | At apply: base version still current and committed quantities still satisfy `TOA-GRD-02` (a receipt may have landed since submit) | `409 TRADE_AMENDMENT_STALE` — amendment returned to `DRAFT` with recomputed figures |
| TOA-GRD-07 | Counterparty not blocked when the amendment increases quantity or adds a line | `422 TRADE_SUPPLIER_BLOCKED` / `TRADE_CUSTOMER_BLOCKED` |
| TOA-GRD-08 | Validity extension keeps rate-contract validity (contract still approved on the new dates) or the line is re-priced manually (`manual_rate`) | field `422` |
| TOA-GRD-09 | Origin `SUPPLIER_RETURN`: only `SCHEDULE_ADD` (and, on a FIXED line, the matching `LINE_QTY`) of the returned quantity on the original line, at its rate; no other change type | `422 TRADE_FIELD_NOT_AMENDABLE` |
| TOA-GRD-10 | A new origin-`CUSTOMER_SCHEDULE` amendment while one of the same origin is `DRAFT`: the draft is `CANCELLED` and replaced in the same transaction; while it is `SUBMITTED` the import is refused | `409 TRADE_AMENDMENT_OPEN` |

### 1.4 Unreachable

| ID | Forbidden | Why |
|---|---|---|
| TOA-UNR-01 | Editing an order outside an amendment after approval | no edit path (`TAM-UNR-03`, `TPO-UNR-03`) |
| TOA-UNR-02 | Overwriting or deleting a version snapshot | append-only; trigger refuses UPDATE/DELETE |
| TOA-UNR-03 | Applying an amendment without the port push succeeding | same transaction (`TOA-T4-02`) |

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from |
|---|---|---|---|
| TOA-T2-01 | Draft / edit / cancel | `:create` / `:edit` / maker | `DRAFT`, `REJECTED` |
| TOA-T2-02 | Submit / withdraw | `:submit` | `DRAFT`, `REJECTED` / `SUBMITTED` |
| TOA-T2-03 | Approve | `:approve` (`TAM`) | `SUBMITTED` |
| TOA-T2-04 | Compare versions / reprint version | order `:view` | ≥ 1 version |
| TOA-T2-05 | Export | `:export` | — |

## 3. T3 — Time-driven rules

None of its own; pending approval escalation is `TAM-T3-01`.

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in |
|---|---|---|---|
| TOA-T4-01 | Applied | changes written to the order; `version_no` + 1; snapshot rows for the new version (version 1 was written at approval) | `OrderAmendmentService.apply` |
| TOA-T4-02 | Applied | **PO:** `WhPurchaseOrderPort.amendOrder(AmendPurchaseOrderCommand{ envelope(key 'WHT_PURCHASE_ORDER:<poId>:PO_AMEND:<amendment no>'), poId, expectedRevisionNo, amendmentReason, lineChanges[poLineId, orderedQuantity?, unitPrice?, expectedDeliveryDate?, receivingLocationId?], scheduleChanges[scheduleLineId, quantity?, scheduledDate?, unitPrice?], newScheduleLines[poLineId, kind, scheduledDate, quantity, unitPrice?, releaseRef], newLines[], validTo?, receiptCutoffDate? })` (`POS-T1-07`) on the PO's one core PO — every `SCHEDULE_ADD` goes as `newScheduleLines` in the same command, so a FIXED line's `LINE_QTY` increase and its added schedule line are checked together (`POS-GRD-02`; FRD-TRADE §12c `CN-2`, resolved), and a `DELIVER_TO` change goes as `lineChanges.receivingLocationId` (`POS-GRD-15`); `cancelScheduleLine` for removed unreceived schedule lines (`…:PO_CANCEL_SCHEDULE:<amendment no>-<n>`). **SO:** `WhDemandOrderPort.amendDemand` (`…:DEMAND_AMEND:<amendment no>`; a `SHIP_TO` change as `shipToAddressId`, re-snapshotted by core — `POS-GRD-16`, FRD-TRADE §12c `CN-3`, resolved), `cancelLine` (`LINE_CANCEL`), `cancelScheduleLine` (`SCHEDULE_CANCEL`), `releaseSchedule` with `FORECAST` entries for added schedule lines (`POS-T1-11`, `-11c`, `-12`) on the SO's one core demand order — firm and `FORECAST` schedule kept equal to the trade schedule. Core's `POS-GRD-09` (never below received / allocated + cancelled + backordered; site immutable) is the backstop of `TOA-GRD-02`, `-03` | same transaction; refusal rolls back (`TPO-T4-03` pattern) |
| TOA-T4-03 | Applied | ack status → `PENDING` (PO: supplier must re-acknowledge, `TPO-T3-04` restarts; SO: *Re-send acknowledgement* is due, `TSO-T1-11`, `TSO-T3-04`); rate-contract consumption adjusted (`TRC-T4-01`); PR allocations adjusted for cancelled lines (`TPR-T1-07`); origin `SUPPLIER_RETURN`: `replacement_pending_quantity` cleared and the line shows *replacement due* | same |
| TOA-T4-04 | Applied | print `PURCHASE_ORDER` / `SALES_ORDER_ACK` with banner *Amendment No. n dated d — supersedes version n−1* and a change summary | renderer |
| TOA-T4-05 | Compare | backend diff of any two snapshots (header, lines, schedule), field by field | `OrderVersionService` |
| TOA-T4-06 | SO amendment of origin `CUSTOMER_SCHEDULE` | changes inside `warehouse.trade.sales.firm_zone_days` (default 14) of the schedule date set `in_firm_zone = true` and are counted for `SCHEDULE_VOLATILITY` (`TCE-T4-03`); a replaced `DRAFT` (`TOA-GRD-10`) is not counted | evaluation run reads change rows of `APPLIED` amendments |

## 5. T5 — Screen contract

WS-296 / WS-307 (reference **Service Vehicle**): grids `wht_po_amendments` / `wht_so_amendments`,
scopes `WAREHOUSE_TRADE_PO_AMENDMENT` / `WAREHOUSE_TRADE_SO_AMENDMENT`. Tiles: draft, submitted,
applied (period), rejected (period), firm-zone changes (SO). Columns: `amendmentNumber`, `orderNumber`,
`counterpartyName`, `baseVersionNo`, `origin`, `reason`, `valueBefore`, `valueAfter`, `valueDelta`,
`status`, `appliedAt`, audit. Filters: `counterpartyId`, `status`, `origin`, `reasonCode`,
`appliedFrom`/`To`. Origin values: `MANUAL`, `ACK_CHANGES`, `SUPPLIER_RETURN` (WS-296) / `MANUAL`,
`CUSTOMER_SCHEDULE` (WS-307). Value columns are in the order's currency; no tile sums money. Actions: View
(change rows, old → new) · Edit · Submit · Withdraw · Cancel · Print. Export ⊇ grid. Empty state: *No
amendments.* **Versions tab** on the order: list of versions, *Compare* (two pickers), *Reprint*.

## 6. Out of scope

| Item | Decision |
|---|---|
| Retrospective rate change on received quantity | `OD-36` — accounting |
| Amending a closed / short-closed / cancelled order | not offered; a new order is raised |

## 7. Amendments

| Date | Rows | Change | Found by |
|---|---|---|---|
| 2026-10-22 | all | v0 derived | TRADE author |
| 2026-10-22 | §0 fields, §1, `TOA-T1-01`…`-05`, `TOA-GRD-01`, `-03`, `-04`, `-09`, `-10`, T2, `TOA-T4-02`, `-03`, `-06`, §5 | R29 TP-F17, F23, F24, TS-F10, F19, F29 and contract quality: registry-exact port commands and keys, origin `SUPPLIER_RETURN`, site immutable / deliver-to inside the site / ship-to, lock only on changed schedule lines, newer import replaces a draft, withdraw row, `REJECTED` editable like every trade document, deterministic dual-band match, sales firm-zone setting named | R29 |
| 2026-10-22 | `TOA-T4-02` | Aligned to the updated core registry: `SCHEDULE_ADD` as `amendOrder` `newScheduleLines` (`CN-2`); `DELIVER_TO` as `lineChanges.receivingLocationId`; `SHIP_TO` as `amendDemand` `shipToAddressId` (`CN-3`) | TRADE author |

## 8. Invariants and scenarios

`WH-SC-537`, `WH-SC-541`…`WH-SC-546`, `WH-SC-560`, `WH-SC-564`, `WH-SC-584`, `WH-SC-589`.

## 9. Open rows

`OD-36`.
