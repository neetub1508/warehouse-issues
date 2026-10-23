# Functional Contract — Subcontracting / job work out (`warehouse-manufacturing`)

> **What this is.** The functional truth for a subcontract order (a production order of type
> `SUBCONTRACT`), the subcontract dispatch (`SCD-`, `DRAFT → DISPATCHED` / `CANCELLED`) on the **generic
> path** (core returnable gate pass, `p8-03`) or the **India path** (core `JobWorkDispatchPort`, india bean,
> SEAM-M5, `V540190`), the subcontract receipt (backflush from the job-worker location, a different item
> back, scrap retained or returned), the reconciliation (recall / write-off) and the close guard (WS-330).
>
> **What this is not.** It does not restate the order ladder (`mfg-production-order.contract.md`), the
> receipt post (`mfg-production-receipt.contract.md`), costing (`mfg-costing-close.contract.md`, `CST-*`),
> ledger guards ([`movement-post-reverse.contract.md`](movement-post-reverse.contract.md), `MPR-*`), the
> gate pass (`p8-03`) or india's challan / registration / ITC-04 (`issues/p4-02.md`). MFG writes no `whin_`
> table and has no compile dependency on `warehouse-india` (FR-620, MD-13).
>
> **Status.** Derived 2026-10-22 (v0), **not ratified**. No code exists. Statutory values **RE-VERIFY**.

---

## 0. Identity

| | |
|---|---|
| **Workflow** | Create `SUBCONTRACT` order (BOM usage `SUBCONTRACT`, job worker, `JOB_WORKER` location) → release → dispatch(es) → stock at job-worker location → subcontract receipt(s) → reconcile open balance (recall / write-off) → close |
| **Module** | `warehouse-manufacturing`; calls core `ai.warehouse.port.jobwork.JobWorkDispatchPort` when the india bean exists (SEAM-M5), else core gate pass (`p8-03`). The port is **not** a STORES port (FRD-STORES defines none): `p10-10` declares it in core and ships the india bean; `V540190` (processed-form return, scrap, return reversal, loss on job-work lines) ships in `warehouse-india`, owned by `p10-10` (MD-25, MD-28) |
| **Domain baseline** | FRD-MFG FR-632, FR-658…FR-661, FR-670…FR-675 (bonded job work, `mfg-bonded-issue`, `D-17` item 3), §3.1 (`SUBCONTRACT_DISPATCH`, `SUBCONTRACT_RECALL`, `SUBCONTRACT_WRITE_OFF`), §3.2 SEAM-M5, MD-13 · `DECISIONS.md` `L-1`, `L-10`, `L-11`, `L-14` · `MPR-T1-01`, `-04`, `-05`, `MPR-GRD-15`, `-16`, `-19`, `-35` · `issues/p4-02.md`, `issues/p8-03.md` |
| **Owning task bodies** | `p10-10` (FRD §13; body not yet written). Depends on `p10-05`, `p10-07`, `p8-03`, `p4-02`; SEAM-M5 is a cross-module change inside `p10-10` |
| **Primary tables** | `whm_subcontract_dispatches` (+ `bond_permission_ref`, `V560120`), `_lines`, `whm_subcontract_reconciliations` (`V560080`); subcontract fields on `whm_production_orders` (`subcontractor_counterparty_id`, `subcontract_location_id`, `service_po_line_ref`, `service_po_ref`) |
| **Status columns** | `whm_subcontract_dispatches.status` (`DRAFT`/`DISPATCHED`/`CANCELLED`); `whm_subcontract_reconciliations.resolution` (derived `NONE`/`PARTIAL`/`RESOLVED`); `whm_subcontract_reconciliation_actions.status` (`REQUESTED`/`POSTED`/`REJECTED`) — no `CHECK` (`D-10`) |
| **Permission resources** | `whm_subcontract_dispatches:{view,create,edit,export,dispatch,cancel,recall,write_off,approve_write_off}` (MD-20) · receipt `whm_production_receipts:{create,post}` · close `whm_production_orders:close` |
| **Routes** | `/warehouse/manufacturing/subcontracting` (WS-330, tabs Dispatches · Reconciliation) · WS-323/WS-324 for the order · **mobile: none** |
| **Contract status / version** | `derived 2026-10-22 (v0), not ratified` · `v0 — 2026-10-22` |

### Acceptance checks

| # | The requester expects… | Delivered by |
|---|---|---|
| A1 | A subcontract order takes a `SUBCONTRACT` BOM: components we send, a **different** processed item back; job worker + `JOB_WORKER` location required (`WH-SC-645`) | `SUB-GRD-01`…`-04` |
| A2 | Dispatch posts one `SUBCONTRACT_DISPATCH` store → job-worker location, owner unchanged, with a returnable gate pass on the generic path and a dispatch note (`WH-SC-645`) | `SUB-T1-03`, `SUB-T4-01`, `SUB-T4-02` |
| A3 | With india on, dispatch calls `JobWorkDispatchPort.registerDispatch`; india raises **one** `JOB_WORK` challan (`INPUTS`/`CAPITAL_GOODS`) and the registration; india's clocks apply (`WH-SC-646`) | `SUB-T1-03`, `SUB-T4-03`, §3.1 |
| A4 | A subcontract receipt backflushes from the job-worker location, receives the processed item, scrap retained → `VIRT-SCRAP` or returned → by-product; india records the processed-form return + waste (`WH-SC-647`) | `SUB-T1-06`, `SUB-T4-05`…`-07` |
| A5 | A receipt of an item not on the order is refused (`WH-SC-649`) | `SUB-GRD-09` |
| A6 | Close is refused while a balance is open at the job worker; recall + approved write-off make it closable (`WH-SC-648`) | `SUB-T1-08`…`-10`, `SUB-GRD-14` |

---

## 1. T1 — State machine

### 1.1 Status inventory

| Entity | Status | Represented by | Reachable via | Exits via | Kind |
|---|---|---|---|---|---|
| Subcontract order | ordinary order ladder, `order_type = SUBCONTRACT` | `whm_production_orders.status` | `mfg-production-order` | same | — |
| Dispatch | `DRAFT` | `whm_subcontract_dispatches.status` | `SUB-T1-01` | `-03`, `-04` | initial, active |
| Dispatch | `DISPATCHED` | `status`; `movement_id`, `dispatched_at`, `gate_pass_id` **or** `challan_ref` + `jobwork_registration_ref` | `SUB-T1-03` | none — correction is recall (`SUB-UNR-02`) | **terminal** |
| Dispatch | `CANCELLED` | `status` | `SUB-T1-04` | none | **terminal** |
| Reconciliation row (order × item × lot) | *open* (derived) | `open_base_quantity` = sent − consumed − scrap retained − recalled − written off − pending write-off > 0 | `SUB-T4-04` | `SUB-T1-08`, `-09`, receipts | active |
| Reconciliation action | `REQUESTED` (write-off pending) | `whm_subcontract_reconciliation_actions.status`; row `pending_write_off_base_quantity` | `SUB-T1-09` | `SUB-T1-10` approve / reject | active (MD-26) |
| Reconciliation action | `POSTED` / `REJECTED` | `status`, `movement_id`, `approved_by/at` | `SUB-T1-08` (recall posts at once), `SUB-T1-10` | none | **terminal** |
| Reconciliation row | *settled* (derived) | `open_base_quantity = 0` | effects | none | terminal for close |

### 1.2 Transitions

| ID | From | Event / action | To | Guard (service, first) | Actor (permission) | Side effects | Comment/reason required | UI entry point | Source |
|---|---|---|---|---|---|---|---|---|---|
| SUB-T1-00 | — | Create subcontract order (type `SUBCONTRACT`) | order `PLANNED` | `SUB-GRD-01`…`-04` + order guards | `whm_production_orders:create` | BOM snapshot; components' `supply_location_id` = `subcontract_location_id` for receipt backflush; `service_po_line_ref` = the warehouse-trade subcontract PO's service line (FRD-TRADE FR-682…) with its `service_po_ref` frozen for display, when trade is on (D-18 item 3) | no | WS-323 **Add** (type select) | FR-658 |
| SUB-T1-01 | — | **Create dispatch** for a `RELEASED`/`IN_PROGRESS` subcontract order; lines proposed from open requirement = required − (sent − recalled) per component | `DRAFT` | `SUB-GRD-05` | `whm_subcontract_dispatches:create` | `SCD-` number at create (gapless, site, yearly); `to_location_id`, `job_worker_counterparty_id` copied from the order | no | WS-330 **Add**; WS-324 Materials tab **Dispatch to job worker** | FR-659 |
| SUB-T1-02 | `DRAFT` | Edit lines (item, lot, quantity, `job_work_type`) | `DRAFT` | `SUB-GRD-06`, `-07` | `whm_subcontract_dispatches:edit` | — | no | WS-330 **Edit** | FR-659 |
| SUB-T1-03 | `DRAFT` | **Dispatch** | `DISPATCHED` | `SUB-GRD-05`…`-08`, `-17`, `-18`, then `MPR-T1-01` guards (`MPR-GRD-01`, `-09`, `-15`, `-16`) | `whm_subcontract_dispatches:dispatch` — not `:edit` (`RJ-005`) | one `SUBCONTRACT_DISPATCH` movement, key `SUBCONTRACT_DISPATCH:<id>` (`SUB-T4-01`); path generic (`SUB-T4-02`) or India (`SUB-T4-03`) **in the same transaction**; reconciliation `sent` += (`SUB-T4-04`); order → `IN_PROGRESS` on first posting; the order's component holds on the dispatched positions are passed in `consumedReservationIds` and closed `CONSUMED` by the dispatch service (`WhbReservationStore.consume`); only the dispatched quantity loses its hold — the remainder of a larger hold is re-created at its source position, and nothing is reserved at the job worker (MD-31, R29 F3, R31 F-MF-002); a licensed line freezes the order's `bonded_duty_status` (`SUB-GRD-18`) | no | WS-330 row **Dispatch**; **Print dispatch note** after | FR-659, FR-660 |
| SUB-T1-04 | `DRAFT` | **Cancel** | `CANCELLED` | — | `whm_subcontract_dispatches:cancel` | none on stock; number stays issued | **yes** (note) | WS-330 row **Cancel** | FR-659 |
| SUB-T1-05 | `DISPATCHED` | Edit, cancel or reverse the dispatch movement | refused | `SUB-UNR-01`, `-02` | any | — | — | none | FR-659 |
| SUB-T1-06 | order `RELEASED`/`IN_PROGRESS` | **Subcontract receipt** post (a production receipt on the `SUBCONTRACT` order) | receipt `POSTED` | receipt guards + `SUB-GRD-09`…`-12` | `whm_production_receipts:post` | `SUB-T4-05`…`-07`; every component backflushed **from `subcontract_location_id`** regardless of supply method (FR-661) | per receipt contract | WS-326 **Add** (source: subcontract order) | FR-661 |
| SUB-T1-07 | `POSTED` subcontract receipt | Reversal (`PRV-`, FR-649) | receipt `REVERSED` | receipt reversal guards + `SUB-GRD-13` | `whm_production_receipt_reversals:{create,approve,post}` | reconciliation `consumed`/`scrap_retained` regress; India: port reversal call (`SUB-OPEN-04`); bonded stock: the `JOB_WORK_RETURN` mirror row re-opens the register quantity and re-arms `BND-T3-01` (`BND-T4-02`) | **yes** | WS-327 | FR-649, FR-661 |
| SUB-T1-08 | reconciliation *open* | **Recall** quantity q to a store location + status (`AVAILABLE`/`QC_HOLD`/`REJECTED`) | *open* (less) or *settled* | `SUB-GRD-15`, `MPR-T1-01` guards | `whm_subcontract_dispatches:recall` | a `POSTED` action (`SCR-` number) and one `SUBCONTRACT_RECALL` movement job-worker location → store (key `SUBCONTRACT_RECALL:<actionId>`), each inbound line stating `costSourceLineId` = the dispatch's store-side line for that item/lot, so the matched-return path restores the dispatched layers at their cost (`WhbCostingEngine.java:417-428`); the restored value (read back) goes on the action's `value` and leaves the pool (`CST-T4-12`, MD-32); `recalled` += q; India: `registerReturn(sameItem, consumedInputQty = 0, scrap 0)`; generic: gate-pass return line | **yes** (note) | WS-330 Reconciliation tab **Recall** | FR-661 |
| SUB-T1-09 | reconciliation *open* | **Write off** quantity q (lost / not returnable at the job worker) | *write-off pending* | `SUB-GRD-15`, `SUB-GRD-16` | `whm_subcontract_dispatches:write_off` | a `REQUESTED` action (`SCR-` number, reason, note); `pending_write_off_base_quantity` += q — **no movement yet**; a pending write-off still blocks close (MD-26) | **yes** — reason code | WS-330 Reconciliation tab **Write off** | FR-661 |
| SUB-T1-10 | *write-off pending* | Approve / reject the write-off | *open* (less) / *open* | approver ≠ requester (`403 WRITE_OFF_SELF_APPROVAL`, MD-21); `MPR-T1-01` guards on approve | `whm_subcontract_dispatches:approve_write_off` (MD-20) | approve: action `POSTED`, one `SUBCONTRACT_WRITE_OFF` movement job-worker location → `VIRT-SCRAP` (reason context `SUBCONTRACT_WRITE_OFF`, key `SUBCONTRACT_WRITE_OFF:<actionId>`), `written_off` += q, pending −= q; the movement is virtual to virtual and carries no value, so the action's `value` = q × the dispatch line's average dispatched value leaves the pool to the abnormal-loss record (`CST-T4-12`, MD-32); India: `registerLoss` (`SUB-T4-10`); reject: action `REJECTED`, pending −= q, nothing moves | reject: **yes** | WS-330 Reconciliation tab **Approve** / **Reject** | FR-661 |
| SUB-T1-11 | order `COMPLETED` | **Close** | settlement per `CST-T1-01` | `SUB-GRD-14` + `CST-GRD-*` | `whm_production_orders:close` | `mfg-costing-close` | no | WS-324 **Close** | FR-656, FR-661 |

### 1.3 Guards

| ID | Predicate (must hold to proceed) | Refusal: HTTP · code · field | Message shape | DB backstop | Source |
|---|---|---|---|---|---|
| SUB-GRD-01 | `order_type = SUBCONTRACT` ⇔ BOM `bom_usage = SUBCONTRACT` | `422 BOM_USAGE_MISMATCH` *(proposed)* · `bomId` | names usage found | — | FR-658 |
| SUB-GRD-02 | `subcontractor_counterparty_id` set, active | `422 SUBCONTRACTOR_REQUIRED` *(proposed)* · `subcontractorCounterpartyId` | — | FK | FR-658 |
| SUB-GRD-03 | `subcontract_location_id` is a location of **base type `JOB_WORKER`** (virtual counterparty, `V500006:132`) at the order's site — the site's `VIRT-JOB_WORKER-<site>` or a per-job-worker `JOB_WORKER` location maintained on the base locations screen (MD-28) | `422 SUBCONTRACT_LOCATION_INVALID` *(proposed)* · `subcontractLocationId` | names location + type | FK | FR-658, `V500006` |
| SUB-GRD-04 | Owner = house (`L-11`: dispatch never changes owner; non-own is `OD-42` v1.2) — the predicate of `PRO-GRD-17`, so its code (R31 F-MF-019) | `422 OWNER_NOT_HOUSE` *(proposed)* · `ownerId` | — | `whin_job_work_dispatch_lines` owner-change trigger (india path) | FR-632, `L-11` |
| SUB-GRD-05 | Order `RELEASED`/`IN_PROGRESS`, not on hold, type `SUBCONTRACT` | `409 ORDER_NOT_OPEN` / `409 ORDER_ON_HOLD` · `orderId` | — | — | FR-634 |
| SUB-GRD-06 | Each line's item is a component of the order; under `STRICT` cumulative dispatched − recalled ≤ required × (1 + tolerance); `WARN` needs `PRODUCTION_DEVIATION`; `FLEXIBLE` free | `422 ITEM_NOT_ON_ORDER` · `lines[n].itemId`; `422 DISPATCH_EXCEEDS_REQUIREMENT` · `lines[n].quantity` | names required, sent, policy | — | FR-643 |
| SUB-GRD-07 | Lot/serial per item control policy; quantity > 0; UoM convertible | `422 LOT_REQUIRED` · `lines[n].lotId`; `422 UOM_NOT_CONVERTIBLE` · `lines[n].uomCode` | — | `MPR-GRD-26` | FR-659, `RQP-GRD-02`, `-03` vocabulary |
| SUB-GRD-08 | India path: all lines share one `job_work_type` (the challan carries it at header); counterparty has what india requires (GSTIN, state) — india's refusal is propagated verbatim | `422 JOB_WORK_TYPE_MIXED` · `lines[n].jobWorkType`; `422 JOB_WORK_DISPATCH_REFUSED` · india's field | prefixes india's message | india service | FR-660, `WI/M/V540020:241-244` |
| SUB-GRD-09 | Every received output item is on the order's outputs (MAIN processed item, or a BY_PRODUCT row for returned scrap) | `422 OUTPUT_NOT_ON_ORDER` · `outputs[n].itemId` | names item and order | — | FR-661, `WH-SC-649` |
| SUB-GRD-10 | Backflush consumption per (item, lot) ≤ reconciliation open quantity at the job-worker location | `422 SUBCONTRACT_CONSUMPTION_EXCEEDS_SENT` · `consumptions[n].baseQuantity` | names sent, consumed, open | position at location (`BACKFLUSH_SHORTAGE` backstop) | FR-661 |
| SUB-GRD-11 | Scrap at the job worker: `retained` ⇒ consumption scrap line → `VIRT-SCRAP`; `returned` ⇒ a BY_PRODUCT output line exists (else `SUB-GRD-09`) | `422 SUBCONTRACT_SCRAP_MODE_REQUIRED` · `consumptions[n].scrapRetained` | — | — | FR-661 |
| SUB-GRD-12 | Gate-entry reference present for the inward receipt (`p8-03`) when the site requires gate entry | `422 GATE_ENTRY_REQUIRED` · `gateEntryId` (`SUB-OPEN-05`) | — | — | FR-661 |
| SUB-GRD-13 | Reversal of a subcontract receipt: the India port accepts the reversal (filed ITC-04 period ⇒ refused) | `409 JOB_WORK_RETURN_FILED` · `receiptId` | names the ITC-04 period | india frozen-return rule | `p4-02`, FR-649 |
| SUB-GRD-14 | **Close guard** — owned by `mfg-costing-close` (`CST-GRD-04`) and cited here, one guard (R31 F-MF-006): every reconciliation row of the order `open_base_quantity = 0` and no write-off pending; no `DRAFT` dispatch | `409 SUBCONTRACT_BALANCE_OPEN` · `orderId` (lists item/lot/qty); `409 SUBCONTRACT_DISPATCH_DRAFT_OPEN` · `orderId` | `WH-SC-648`: lists 4 `SHAFT-03` | — | FR-656, FR-661 |
| SUB-GRD-15 | Recall / write-off q ≤ `open_base_quantity` of that row — which already nets the pending write-off (FRD §4), so it is never subtracted twice (R31 F-MF-013: 100 out, 40 pending → a recall of 60 passes) | `422 RECONCILIATION_QUANTITY_EXCEEDS_OPEN` · `quantity` | — | — | FR-661 |
| SUB-GRD-16 | Write-off reason of context `SUBCONTRACT_WRITE_OFF` | `422 REASON_REQUIRED` · `reasonCodeId` | — | `MPR-GRD-11` | FR-661 |
| SUB-GRD-17 | A dispatch with any line in a licensed duty status carries `bond_permission_ref` and `expected_return_date`; the bond rule and licence hold at post (india guard) | `422 BOND_PERMISSION_REF_REQUIRED` · `bondPermissionRef`; `422 EXPECTED_RETURN_DATE_REQUIRED` · `expectedReturnDate`; `409 BONDED_LICENCE_NOT_ACTIVE` / `409 BONDED_OPERATION_NOT_PERMITTED` · `lines[n].duty_status` | names the duty status and licence | india guard | FR-671, FR-675 |
| SUB-GRD-18 | **Bonded regime at dispatch** (R31 F-MF-004): the dispatch's lines carry at most one licensed duty status, equal to the order's `bonded_duty_status` when frozen; the first licensed line freezes it (MD-43) — so a mixed second dispatch is refused **before the goods leave**, not at the subcontract receipt; refused too on an order that has already posted output outside that regime. A `MOOWR` line is refused while the `MOOWR` job-work rules are inactive (their seeded default, D-18 item 1) | `409 BONDED_REGIME_MIXED` / `409 BONDED_REGIME_AFTER_OUTPUT` *(proposed)* · `lines[n].dutyStatus`; `409 BONDED_OPERATION_NOT_PERMITTED` · `lines[n].duty_status` | names the frozen and the offered status | india guard | FR-671, FR-673, FR-675 |

### 1.4 Transitions that must be unreachable

| ID | Forbidden | What makes it unreachable | Source |
|---|---|---|---|
| SUB-UNR-01 | Editing a `DISPATCHED` dispatch | no edit for non-`DRAFT` | FR-659 |
| SUB-UNR-02 | Posting or reversing a `SUBCONTRACT_*` movement through the generic port | MFG's `WhbMovementPostGuard` bean refuses any `SUBCONTRACT_*` post or reversal not sourced by its MFG document (`MPR-GRD-35`; MD-35, R29 F5); MFG offers recall instead | FR-658, `L-3`, MD-03 |
| SUB-UNR-03 | Ownership changing at dispatch | type is INTERNAL, owner unchanged (`L-11`); india trigger backstop | FR-658 |
| SUB-UNR-04 | A second challan for one dispatch | port is called once per dispatch, idempotent on `SCD:<id>` | `FR-313`, MD-13 |
| SUB-UNR-05 | MFG writing a `whin_` table or importing `ai.warehouseindia` | port only; ArchUnit rule | FR-620, FR-660 |
| SUB-UNR-06 | Job-worker stock counted as MRP supply or allocatable elsewhere | `JOB_WORKER` positions excluded from MRP netting (`MRP-N-05`) and never allocatable — the allocator takes no virtual counterparty location (`WhbAllocationRepository.java:38`); no reservation is needed or possible there (MD-31) | FR-664 |

---

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from | Extra condition | Source |
|---|---|---|---|---|---|
| SUB-T2-01 | Create / edit dispatch | `:create` / `:edit` | order `RELEASED`/`IN_PROGRESS`; dispatch `DRAFT` | subcontract coordinator | FR-659 |
| SUB-T2-02 | Dispatch | `:dispatch` | `DRAFT` | path chosen by bean presence (`SUB-T4-02`/`-03`) | FR-659 |
| SUB-T2-03 | Cancel dispatch | `:cancel` | `DRAFT` | note | FR-659 |
| SUB-T2-04 | Recall | `:recall` | reconciliation *open* | — | FR-661 |
| SUB-T2-05 | Write off / approve write-off | `:write_off` / `:approve_write_off` | *open* / *write-off pending* | approver ≠ requester | FR-661 |
| SUB-T2-06 | Post subcontract receipt | `whm_production_receipts:post` | order open | `SUB-GRD-09`…`-12` | FR-661 |
| SUB-T2-07 | Print dispatch note | `:view` | `DISPATCHED` | — | FR-659 |
| SUB-T2-08 | View / export | `:view` / `:export` | any | AUDITOR no export | FR-669 |

## 3. T3 — Time-driven rules & notifications

### 3.1 Statutory values (India path) — **RE-VERIFY** before ratification

| Value | Current reading | Held in | Owner |
|---|---|---|---|
| Return window, inputs | **1 year** from the challan date (s.143(1)(a), r.45); extendable by the Commissioner by 1 year | `warehouse.india.job_work.return_period_years.inputs` = 1 (`V541053:115`) | india |
| Return window, capital goods | **3 years**; extendable by 2 years | `…capital_goods` = 3 (`V541053:121`) | india |
| Moulds, dies, jigs, tools | no time limit (s.143(2) proviso) | india | india |
| Missed window | deemed supply on the **date sent** | `deemed_supply_due_date` (`V540020:241-244`) | india |
| Direct-from-vendor | clock from receipt at the job worker | — (not supported in v1, `SUB-OPEN-07`) | india |
| Scrap at job worker | s.143(5): supplied by the job worker if registered, else by the principal | `V540190` scrap columns | india |
| ITC-04 frequency | half-yearly (due 25 Oct / 25 Apr) when AATO > ₹5 crore, annual (due 25 Apr) otherwise | india (`p4-02`) | india |
| E-way bill | required for an inter-state job-work movement regardless of value | india | india |

### 3.2 Rules

| ID | Rule | Trigger | What it changes | Who is notified | Channel | Job class | Notify-once? | Source |
|---|---|---|---|---|---|---|---|---|
| SUB-T3-01 | Challan approaching / past its return window | india clock (`p4-02`) | nothing in MFG; WS-330 shows `expectedReturnDate` and an *overdue* flag | india's alert recipients | india | india job | india | FR-660 |
| SUB-T3-02 | Generic path: returnable gate pass overdue | `p8-03` overdue rule | nothing in MFG; flag shown | `p8-03` | `p8-03` | `p8-03` job | `p8-03` | FR-659 |
| SUB-T3-03 | Write-off pending approval | `SUB-T1-09` | nothing | holders of `:approve_write_off` at the site | in-app — `TBD` DEFERRED-TO-p10-10 | event | once | FR-661 |
| SUB-T3-04 | No auto-recall, auto-write-off or auto-close | — | — | — | — | — | — | FR-661 |

## 4. T4 — Cross-entity effects

| ID | When this happens | Then this other record must change | Enforced in | Source |
|---|---|---|---|---|
| SUB-T4-01 | Dispatch | `SUBCONTRACT_DISPATCH` movement: store bin → `to_location_id`, owner/lot/status unchanged, balanced per `I-1`; `movement_id`, `movement_line_id` set; the order's holds on the source positions (found by holder quad) passed as `consumedReservationIds`, closed `CONSUMED` by the dispatch service (`WhbReservationStore.consume` — the id alone only exempts a hold from the availability check), the remainder of a hold larger than the dispatched quantity re-created at its source (R31 F-MF-002), and **nothing** re-created at the job worker — a `JOB_WORKER` location is virtual, admission gives ATP 0 there (`WhbStockPositionWriter.java:356-366`) and `V500087` refuses it (MD-31, R29 F3); `dispatched_value` per line = the store-side line's relieved value read back, added to the pool `P_D` (`CST-T4-12`, MD-32) | dispatch service → `WhbStockLedgerWriter.post` | FR-658, FR-659 |
| SUB-T4-02 | Dispatch, **no `JobWorkDispatchPort` bean** (or the bean declares the movement not job work, e.g. same GSTIN) | core returnable gate pass (`p8-03`, kind `RETURNABLE`, party = job worker, lines from the dispatch, `source_document_type = SUBCONTRACT_DISPATCH`, resolved by MFG's `GatePassSourceResolver`, MD-29) created `DRAFT` and then approved and gated out by core (`GTE-T1-11`/`-12`; gate-out needs the dispatch `DISPATCHED`, `GTE-GRD-13`); `gate_pass_id` stored | dispatch service | FR-659 |
| SUB-T4-03 | Dispatch, **india bean present** | `registerDispatch(dispatchId, movementId, jobWorker, lines, jobWorkType)` — india raises one `JOB_WORK` challan + registration; `challan_ref`, `jobwork_registration_ref` frozen on the dispatch; a port refusal rolls back the whole dispatch | port, same transaction | FR-660 |
| SUB-T4-04 | Dispatch / receipt / recall / approved write-off / receipt reversal | `whm_subcontract_reconciliations` row (order, item, lot) upserted; `open_base_quantity` re-derived on write | reconciliation service | FR-661 |
| SUB-T4-05 | Subcontract receipt post | one `PRODUCTION_RECEIPT` movement: consumption from the job-worker location → `VIRT-PRODUCTION`, retained scrap → `VIRT-SCRAP`, processed item ← `VIRT-PRODUCTION` into our store (`WH-SC-647`: 196 `SHAFT-03` out, 190 → production, 6 → scrap, 190 `SHAFT-03P` in) | receipt post | FR-661 |
| SUB-T4-06 | same, india bean present | `registerReturn(returnedAsItemId, consumedInputQty, scrapQty, scrapRetained)` per input line — india records the return **in processed form** and waste for ITC-04 (`V540190`) | port, same transaction | FR-660 |
| SUB-T4-06a | Subcontract receipt **reversal** post, india bean present | `reverseReturn(returnRef)` — india re-opens the registration quantity (its `reevaluateAfterReversal`) (MD-25) | port, same transaction | FR-660 |
| SUB-T4-07 | Subcontract receipt post | the backflush is job-worker → `VIRT-PRODUCTION`, virtual to virtual, so it carries no value (`B_r` = 0); the processed item — a different item — is received at the absorbed share of the pool: `P_D` (Σ dispatched value − recalled − written off) × `min(1, good ÷ remaining planned)`, all on a final receipt, stated as `extendedCost` on its inbound line, which the engine honours (`WhbCostingEngine.java:454`) — never ₹0 (`CST-T4-01`, MD-32, R29 F6); the processing charge is landed afterwards by warehouse-trade at the trade service confirmation (FRD-TRADE FR-686) as a value-only `LANDED_COST_APPLY` onto the received lots (D-18 item 3, SEAM-M7) — MFG posts none | `mfg-costing-close` | FR-654, FR-658 |
| SUB-T4-08 | Recall | india: return of the same item unprocessed; generic: gate-pass return line (`wh_gate_pass_returns`); value restored through `costSourceLineId` (`SUB-T1-08`) | recall service | FR-661 |
| SUB-T4-10 | Write-off approve, india bean present | `registerLoss(dispatchRef, itemId, lotId, qty, reasonCode)` — india records the loss at the job worker for ITC-04 (MD-25); the written-off value leaves the pool (`CST-T4-12`) | port, same transaction | FR-660, FR-661 |
| SUB-T4-09 | Order close | `SUB-GRD-14` read by `CST-GRD-04` | settlement service | FR-656 |
| SUB-T4-11 | Dispatch / receipt / recall / write-off of licensed-status stock, india bean present | `bond_permission_ref` and `expected_return_date` passed in `registerDispatch`; india writes `JOB_WORK_OUT` / `JOB_WORK_RETURN` register rows and, for a write-off or retained scrap, a `whin_bonded_losses` row; the processed item is received in the order's `bonded_duty_status` (`mfg-bonded-issue` `BND-T4-03`…`-06`) | port, same transaction; india recorder | FR-673, FR-675 |

## 5. T5 — Screen contract (web only)

### 5.1 `/warehouse/manufacturing/subcontracting` — WS-330 Subcontracting, tab **Dispatches**

| | |
|---|---|
| **Type** | list + transition modals (reference: **Service Vehicle**) |
| **Grid identifier** | `whm_subcontract_dispatches` · filter scope `WAREHOUSE_MFG_SUBCONTRACT_DISPATCH` |
| **Default sort** | `e.created_at DESC` |
| **Statistics tiles** | `DRAFT` · `DISPATCHED` · `CANCELLED` · open balance lines · overdue |
| **Columns** | `dispatchNumber`, `orderNumber` (GridLink), `outputItemName`, `jobWorkerName`, `toLocationCode`, `path` (`GENERIC`/`INDIA`, derived), `lineCount`, `totalBaseQuantity`, `gatePassNumber`, `challanRef`, `jobworkRegistrationRef`, `expectedReturnDate` (date-only → `formatDateSync`), `isOverdue`, `status`, `dispatchedAt` (timestamp), `createdByName`, `updatedByName` |
| **Filters** | `warehouseId` → `jobWorkerCounterpartyId` → `orderId` (typeahead); `status` (enum); `path` (enum); `dispatchedFrom`/`dispatchedTo` (`date`, timestamp); `expectedReturnFrom`/`expectedReturnTo` (**dateOnly**); `overdueOnly` (boolean) |
| **Row actions** | View · Edit (`DRAFT`) · Dispatch · Cancel (`DRAFT`) · Print dispatch note (`DISPATCHED`) |
| **Toolbar** | **Add** (dispatch modal `size="lg" minWidth={500} resizable`; order → lines editor) · Export |
| **Print** | `SUBCONTRACT_DISPATCH_NOTE`: dispatch + order numbers, job worker, `JOB_WORKER` location, components with lots/quantities/UoM, job-work type, gate pass or challan ref, `expected_return_date` (MD-26) |
| **Export columns** | grid columns + `createdByName`, `updatedByName` |

### 5.2 WS-330 tab **Reconciliation**

| | |
|---|---|
| **Grid identifier** | `whm_subcontract_reconciliations` · `WAREHOUSE_MFG_SUBCONTRACT_RECONCILIATION` — its own grid config, filter scope and `grid_preferences` in `V560080` (R31 `SUB-OPEN-08`) |
| **Columns** | `orderNumber`, `jobWorkerName`, `itemName`, `lotCode`, `sentBaseQuantity`, `consumedBaseQuantity`, `scrapRetainedBaseQuantity`, `recalledBaseQuantity`, `writtenOffBaseQuantity`, `pendingWriteOffQuantity`, `openBaseQuantity`, `resolution`, `resolvedByName`, `resolvedAt` |
| **Filters** | `warehouseId` → `jobWorkerCounterpartyId` → `orderId`; `itemId`; `openOnly` (boolean, default true) |
| **Row actions** | Recall (modal: quantity, target location, status, note) · Write off (reason, note) · Approve / Reject write-off |

## 6. Out of scope

| Not built | Where / why |
|---|---|
| Job work **in** (customer's material) | `OD-42`, v1.2 |
| Processing charge | the warehouse-trade subcontract PO (FRD-TRADE FR-682…), linked by trade's `subcontract_order_id` (FR-683; MFG's `service_po_line_ref` is a display back-reference) — trade lifts R9 for that service line; R8 general service POs stay refused (D-18 item 3) |
| Job-work invoice, debit/credit notes | accounting, R-14 |
| Direct-from-vendor to job worker; job worker → job worker; supply from the job worker's premises | v1 not built (`SUB-OPEN-07`) |
| ITC-04 generation, challan print, e-way bill | india (`p4-02`) |
| Mobile | R-13 |

## 7. Amendments

| Date | Row IDs affected | Change | Found by |
|---|---|---|---|
| 2026-10-22 | all | v0 derived from `docs/frd/FRD-MFG.md`; not ratified | contract derivation (design set) |
| 2026-10-22 | `SUB-T1-03`, `-08`, `-10`, `SUB-T4-01`, `-07`, `-08`, `-10`, `SUB-UNR-02`, `-06` | R29: dispatch consumes holds and re-reserves nothing (F3, MD-31); dispatched value in the pool, recall by `costSourceLineId`, write-off value out (F6, MD-32); MFG post guard (F5, MD-35); duplicate `SUB-T4-08` renumbered — the write-off India row is now `SUB-T4-10` (F31) | `R29-functional-review-mfg.md` |
| 2026-10-22 | T4, §9 | Consistency pass: MD-20, MD-21, MD-25, MD-26, MD-28; generic-path RGP sourced on the dispatch (MD-29) | FRD-MFG §9 |
| 2026-10-23 | `SUB-T1-00`, `-03`, `-07`, `SUB-GRD-01`…`-04`, `-14`, `-15`, `-18`, `SUB-T4-01`, `-07`, §5.2, §6, Source column, `SUB-OPEN-06`…`-09` | R31: holds closed explicitly, remainder re-created (F-MF-002); dispatch freezes the bonded regime (F-MF-004); trade subcontract PO carries the charge (F-MF-005, D-18 item 3); CST owns the close guard (F-MF-006); pending write-off not subtracted twice (F-MF-013); Source FR on every rule row (F-MF-018); one code per predicate (F-MF-019); DECIDE rows applied | `R31-functional-review-mfg.md`, `R31-decisions.md`, D-18 |
| 2026-10-23 | §0, `SUB-GRD-17`, `SUB-T4-11` | Bonded / MOOWR job work allowed under the bond rules (permission reference, return date, register, loss); rules in `mfg-bonded-issue` | R30 `CP-GB-001`, `CP-GA-007`; `D-17` item 3 |

## 8. Invariants and scenarios this workflow must not break

| Invariant | Rows | Scenarios |
|---|---|---|
| `L-11` owner unchanged at the job worker | `SUB-GRD-04`, `SUB-UNR-03` | `WH-SC-645` |
| `L-1` / `I-1` one balanced movement per document | `SUB-T4-01`, `-05` | `WH-SC-645`, `WH-SC-647` |
| One challan per dispatch (`FR-313`) | `SUB-UNR-04` | `WH-SC-646` |
| India optional, port only | `SUB-UNR-05` | `WH-SC-645` vs `-646` |
| Close only with zero open balance | `SUB-GRD-14` | `WH-SC-648` |

## 9. Open rows — contradictions and holes

| ID | Contradiction / hole | Recommendation | Authority | Status |
|---|---|---|---|---|
| SUB-OPEN-01 *(resolved — MD-26)* | FR-659 prints an **expected return date**, but `whm_subcontract_dispatches` has no such column (india's challan has one; the gate pass may) | add `expected_return_date DATE` to the dispatch; default from india's window or a per-counterparty lead time | FRD §4 | resolved |
| SUB-OPEN-02 *(resolved — MD-26: `whm_subcontract_reconciliation_actions`)* | `whm_subcontract_reconciliations` holds one `resolution` + one `resolution_movement_id`, but partial recalls and recall + write-off on one row are normal (`WH-SC-648`: recall 2 + write off 2) | child table `whm_subcontract_reconciliation_actions` (kind, qty, movement, actor); `resolution` becomes derived | FRD §4, FR-661 | resolved |
| SUB-OPEN-03 *(resolved — MD-20/MD-26: `:approve_write_off`, action `REQUESTED` state, own `SUBCONTRACT_WRITE_OFF` movement)* | FR-661 says write-off needs approval; §7 has no approve verb for subcontracting and the reconciliation has no pending state | approval through the `SCRAP` movement's `PENDING` (`MPR-T1-04`/`-05`), approver ≠ requester holding `:write_off`; or add `whm_subcontract_dispatches:approve_write_off` | FRD §7, FR-661 | resolved |
| SUB-OPEN-04 *(resolved — MD-25: `reverseReturn`, `registerLoss`; recall = `registerReturn` of the input)* | SEAM-M5 defines `registerDispatch` / `registerReturn` only; a subcontract receipt reversal, a recall and a write-off (loss at job worker) have no port call, so ITC-04 would keep an open quantity or a stale return | add `reverseReturn(...)` and `registerLoss(...)` to `JobWorkDispatchPort` (india already has `reevaluateAfterReversal`) | SEAM-M5 | resolved |
| SUB-OPEN-05 *(resolved — MD-26: `gate_entry_id` + `gate_entry_ref`)* | FR-661 references the gate entry (`p8-03`) on the receipt; `whm_production_receipts` has no gate-entry column | add `gate_entry_id` (bare UUID) to `whm_production_receipts` | FRD §4 | resolved |
| SUB-OPEN-06 *(resolved — D-18 item 3; no longer open)* | The processing charge never reaches the processed item's cost (FR-658 leaves it to trade/accounting; no landed-cost path designed) | the warehouse-trade subcontract PO (FRD-TRADE FR-682…) carries the charge on its service line, linked by trade's `subcontract_order_id` (FR-683), and trade lands it as a value-only `LANDED_COST_APPLY` at the trade service confirmation (FRD-TRADE FR-686) onto the received lots (`P2-28` path); MFG posts none (FR-658, SEAM-M7) | FR-658, D-18 | resolved |
| SUB-OPEN-07 *(resolved — R31-decisions DECIDE: default stands, v1 scope)* | Research §11: direct-from-vendor dispatch, rejection at the job worker, receipt without challan | v1: rejection at the job worker = recall into `REJECTED`; receipt without a dispatch refused by `SUB-GRD-10`; direct-from-vendor not built | research §7, §11 | resolved |
| SUB-OPEN-08 *(resolved — R31-decisions DECIDE: default stands)* | WS-330 has a Reconciliation tab (FRD §7) but only one grid id / filter scope is listed | ship `whm_subcontract_reconciliations` grid + `WAREHOUSE_MFG_SUBCONTRACT_RECONCILIATION` scope in `V560080` (§5.2, FRD §7, `p10-10`) | FR-669 | resolved |
| SUB-OPEN-09 | FR-659 "outside India or for an intra-GSTIN movement" uses the generic path — the predicate for "intra-GSTIN" is not defined | the india bean decides (`isJobWork(dispatch)`); MFG never inspects GSTINs | FR-659, MD-13 | resolved (R31-decisions DECIDE: default stands) |
