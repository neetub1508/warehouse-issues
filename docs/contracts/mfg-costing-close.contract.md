# Functional Contract — Production costing, settlement and close (`warehouse-manufacturing`)

> **What this is.** The functional truth for valuing production output at actual (`OD-40`, MD-06): the
> order's cost pool in `VIRT-PRODUCTION-<site>`, what each production receipt absorbs, by-product NRV
> credit, abnormal scrap, the exact co-product split, and the **close** — a settlement
> (`DRAFT → APPROVED → POSTED` / `REJECTED`) that posts one value-only `PRODUCTION_SETTLEMENT` movement
> (`L-15`) splitting the residual between output still on hand and `VIRT-COST_OF_SALES`, the approval
> threshold, the close preconditions, the cost sheet and the accounting handover (WS-329).
>
> **What this is not.** It does not restate ledger guards (`MPR-*`,
> [`movement-post-reverse.contract.md`](movement-post-reverse.contract.md)), the receipt post
> (`mfg-production-receipt.contract.md`) or the order ladder (`mfg-production-order.contract.md`), nor
> the handover envelope ([`accounting-handover.contract.md`](accounting-handover.contract.md)). MFG posts no
> GL, journal, debit or credit note (FR-657, R-14).
>
> **Status.** Derived 2026-10-22 (v0), **not ratified**. No code exists. Authority: `docs/frd/FRD-MFG.md`.

---

## 0. Identity

| | |
|---|---|
| **Workflow** | Issues / backflush fill the pool → each receipt absorbs → final receipt → order `COMPLETED` → **Close** computes the residual → settlement `DRAFT` → (approve) → `POSTED` → order `CLOSED` |
| **Module** | `warehouse-manufacturing` (`whm_`). Value math through `WhbCostLayerMath` (`WB/…/WhbCostLayerMath.java:31-32`, `split` = `R-4`); posting through `WhbStockLedgerWriter.post` (`:333`) |
| **Domain baseline** | FRD-MFG FR-638, FR-646, FR-654…FR-657, FR-661, §3.1 (`PRODUCTION_SETTLEMENT`), §8 settings, MD-06, `OD-40`, `OD-43` · `DECISIONS.md` `L-1`, `L-8`, `L-10`, `L-14`, `L-15`, `R-4`, `RF-009` · `MPR-T1-01`, `MPR-T1-11`, `MPR-GRD-02`, `-09`, `-10` |
| **Owning task bodies** | `p10-09` (FRD §13; body not yet written). Depends on `p10-07` (receipt writes absorption), `p8-09`/`p8-10`/`p8-11` + SEAM-M1/M2 (issues land in `VIRT-PRODUCTION` and roll up), `p10-10` (subcontract balance) |
| **Primary tables** | `whm_production_settlements`, `whm_production_settlement_lines` (`V560070`); reads `whm_production_receipt_outputs/_consumptions` (`unit_cost`, `extended_value`), `whm_production_orders` (`planned_cost`, `settlement_id`, `closed_at`) |
| **Status columns** | `whm_production_settlements.status` (`DRAFT`/`APPROVED`/`POSTED`/`REJECTED`) — no `CHECK` (`D-10`) |
| **Permission resources** | `whm_production_orders:close` (entry point) · `whm_production_settlements:{view,create,export,approve,post}` · `whm_production_orders:view` (Cost tab) · cost accountant reads + exports; AUDITOR reads only |
| **Settings** | `warehouse.manufacturing.close_variance_approval_percent` (default 5) · `scrap_value_approval_threshold` (receipt-side, cited) |
| **Routes** | `/warehouse/manufacturing/settlements` (WS-329) · `/production-orders/[id]` Cost tab (WS-324) · **mobile: none** |
| **Contract status / version** | `derived 2026-10-22 (v0), not ratified` · `v0 — 2026-10-22` |

### Acceptance checks

| # | The requester expects… | Delivered by |
|---|---|---|
| A1 | A receipt absorbs its own backflush fully plus the unabsorbed issued pool × good ÷ remaining planned (cap 1); the final receipt absorbs all (`WH-SC-639`) | `CST-T4-01`, §1.5 example 1 |
| A2 | By-product credit at NRV first; abnormal scrap share to `VIRT-SCRAP`; rest split over MAIN + CO_PRODUCT; Σ output values = absorbed pool exactly, reproducible (`WH-SC-630`, `WH-SC-640`) | `CST-T4-02`…`-04`, `CST-GRD-01`, §1.5 example 2 |
| A3 | Close posts one value-only `PRODUCTION_SETTLEMENT` putting the residual on on-hand output lots and `VIRT-COST_OF_SALES` for the consumed/shipped part (`WH-SC-641`) | `CST-T1-01`, `CST-T1-04`, `CST-T4-05` |
| A4 | Residual share above `close_variance_approval_percent` waits for a second user; the order stays `COMPLETED` (`WH-SC-642`) | `CST-T1-01`, `CST-T1-02`, `CST-GRD-06` |
| A5 | Close requires no open staging list, draft receipt or open subcontract balance; releases reservations; closes the MRQ; `CLOSED` refuses further issues (`WH-SC-643`, `WH-SC-648`) | `CST-GRD-02`…`-05`, `CST-T4-06`…`-08` |
| A6 | Non-own orders are never valued; labour/overhead recorded, not absorbed (`L-14`, `OD-43`) | `CST-GRD-09`, `CST-T4-10` |
| A7 | The cost sheet prints planned vs actual by component and output | §5.3 (cost sheet) |
| A8 | Accounting is a handover only | `CST-T4-09`, `CST-UNR-04` |

---

## 1. T1 — State machine

### 1.1 Status inventory

| Entity | Status | Represented by | Reachable via | Exits via | Kind |
|---|---|---|---|---|---|
| Settlement | `DRAFT` | `whm_production_settlements.status`, `requires_approval = true` | `CST-T1-01` | `-02`, `-03` | initial, active |
| Settlement | `APPROVED` | `status`; `approved_by/at` | `CST-T1-02` | `-04`, `-05` | active |
| Settlement | `POSTED` | `status`; `movement_id`, `posted_by/at` | `CST-T1-01` (no approval needed), `CST-T1-04` | none | **terminal** |
| Settlement | `REJECTED` | `status`; reason on history | `CST-T1-03`, `CST-T1-05` | none — a new Close may compute a new one (`CST-OPEN-02`) | **terminal** |
| Order | `COMPLETED` → `CLOSED` | `whm_production_orders.status`, `closed_at`, `settlement_id` | `CST-T1-01`/`-04` (effect) | none (`CLOSED` terminal) | effect |

### 1.2 Transitions

| ID | From | Event / action | To | Guard (service, first) | Actor (permission) | Side effects | Comment/reason required | UI entry point |
|---|---|---|---|---|---|---|---|---|
| CST-T1-01 | order `COMPLETED`, no live settlement | **Close** — compute pool, absorbed, residual, variance %, target lines | `DRAFT` when `requires_approval`; else **`POSTED` in the same transaction** (`CST-OPEN-01`) | `CST-GRD-02`…`-05`, `-07`, `-08`, `-09`; when posting, also `CST-GRD-10` + `MPR-T1-11` guards | `whm_production_orders:close` | `PST-` number at create (gapless, site, yearly); lines computed (`CST-T4-05`); `requires_approval = variance_percent > setting`; when posting: `CST-T4-06`…`-09`; order `CLOSED` | no (a note may be added) | WS-323 row / WS-324 header **Close**; modal shows the computed lines before confirm |
| CST-T1-02 | `DRAFT` | **Approve** | `APPROVED` | `CST-GRD-06`, `CST-GRD-11` | `whm_production_settlements:approve` | `approved_by/at` | no | WS-329 row **Approve** |
| CST-T1-03 | `DRAFT` | **Reject** | `REJECTED` | approver ≠ creator (`CST-GRD-06`) | `whm_production_settlements:approve` | order stays `COMPLETED`; reopen becomes possible again (`CST-OPEN-02`) | **yes** | WS-329 row **Reject** |
| CST-T1-04 | `APPROVED` | **Post** | `POSTED`; order `CLOSED` — one transaction | `CST-GRD-10`, `CST-GRD-11`, then `MPR-T1-11` (`MPR-GRD-02`, `-09`, `-10`, `-11`) | `whm_production_settlements:post` — not `:approve` (`RJ-005`) | `CST-T4-06`…`-09` | no | WS-329 row **Post** |
| CST-T1-05 | `APPROVED` | Reject an approved settlement whose Post is refused (stale, period closed) | `REJECTED` | — | `whm_production_settlements:approve` | as `-03` | **yes** | WS-329 row **Reject** |
| CST-T1-06 | — | **Recompute** a `DRAFT` (pool moved) | `DRAFT` (lines replaced) | `CST-GRD-03` | `whm_production_settlements:create` | lines and values rewritten; `approved_*` stays null | no | WS-329 row **Recompute** |
| CST-T1-07 | `POSTED` | Reverse the settlement / reopen the order | refused | `CST-UNR-01` | any | — | — | none |

### 1.3 Guards

| ID | Predicate (must hold to proceed) | Refusal: HTTP · code · field | Message shape | DB backstop | Source |
|---|---|---|---|---|---|
| CST-GRD-01 | Σ output `extended_value` + abnormal-scrap value + by-product credit = receipt absorbed value, to the scale of `WhbCostLayerMath.split`; split by largest remainder, ties to lowest output `sequence` | — (service-constructed; asserted by test; a mismatch is an incident) | — | `MPR-GRD-01`/`I-21` value balance | FR-655, `R-4`, `RF-009` |
| CST-GRD-02 | No staging list of the order in `DRAFT`/`RELEASED`/`PARTIALLY_STAGED`/`STAGED` with line-side stock not unstaged/consumed | `409 ORDER_HAS_OPEN_STAGING` · `orderId` | lists `STG-` numbers | — | FR-656 |
| CST-GRD-03 | No receipt of the order in `DRAFT`/`PENDING_APPROVAL`; no reversal `REQUESTED`/`APPROVED` | `409 ORDER_HAS_OPEN_RECEIPT` · `orderId` | lists `FGR-`/`PRV-` | — | FR-656, FR-649 |
| CST-GRD-04 | Subcontract order: every reconciliation `open_base_quantity = 0`, no `PENDING` write-off (`SUB-GRD-14`) | `409 SUBCONTRACT_BALANCE_OPEN` · `orderId` | lists item/lot/qty (`WH-SC-648`) | — | FR-661 |
| CST-GRD-05 | No live settlement for the order (`DRAFT`/`APPROVED`/`POSTED`) | `409 SETTLEMENT_EXISTS` · `orderId` | names the `PST-` | uk `(order_id) WHERE status <> 'REJECTED'` (`CST-OPEN-02`) | FR-656 |
| CST-GRD-06 | Approver/rejecter ≠ settlement creator | `409 SETTLEMENT_SELF_APPROVAL` · `id` | — | — | FR-656 |
| CST-GRD-07 | Order status `COMPLETED` | `409 ORDER_NOT_COMPLETED` · `orderId` | names status | — | FR-656 |
| CST-GRD-08 | The order's MRQ (if any) can be closed through `WhMaterialRequisitionPort.close` (no unposted store issue against it) | `409 ORDER_REQUISITION_OPEN` · `orderId` | names MRQ and the draft issue | — | FR-656, `p8-09` |
| CST-GRD-09 | Order owner is the house owner; a non-own order (`OD-42`, v1.1) posts **no** value and no settlement movement | `422 NON_OWN_ORDER_NOT_VALUED` (informational only when OD-42 lands) · `ownerId` | — | `L-14` writer rule | FR-654, `L-14` |
| CST-GRD-10 | Recomputed pool / absorbed / residual at post equals the stored values (nothing posted to the order since compute) | `409 SETTLEMENT_STALE` · `id` | shows stored vs current residual | — | FR-656 |
| CST-GRD-11 | While a settlement is `DRAFT`/`APPROVED`, the `PRODUCTION_ORDER` cost-object resolver refuses issues and returns to the order (`409 ORDER_SETTLEMENT_PENDING` · `costObjectId`) — so a DRAFT cannot go stale through MFG-visible postings | as stated | names the `PST-` | — | FR-640, FR-656 |
| CST-GRD-12 | Approval threshold: `variance_percent = |residual| ÷ absorbed × 100`, compared **strictly greater** than the setting; `absorbed = 0` and `residual ≠ 0` ⇒ approval required | — (computed) | — | — | FR-656 |

### 1.4 Transitions that must be unreachable

| ID | Forbidden | What makes it unreachable | Source |
|---|---|---|---|
| CST-UNR-01 | Reversing a `POSTED` settlement or reopening a `CLOSED` order | `CLOSED` terminal; `PRODUCTION_SETTLEMENT` reversal only by its owning document (`MPR-GRD-35`), which offers none | FR-634, FR-656 |
| CST-UNR-02 | A second settlement while one is live | `CST-GRD-05` + partial uk | FR-656 |
| CST-UNR-03 | Reopen after a live settlement exists | `mfg-production-order` reopen guard reads `CST-GRD-05` | FR-634, `WH-SC-644` |
| CST-UNR-04 | MFG writing a GL account, journal, debit/credit note | no such table/port in the module (grep) | FR-657, R-14 |
| CST-UNR-05 | Frontend computing any cost | rule 8; every figure comes from the backend | FR-628, FR-654 |

### 1.5 The absorption formula, stated

Per order, all values in company currency, base UoM:

- **Issued pool** `P_I` = Σ value of store issues into `VIRT-PRODUCTION` for the order (SEAM-M1) − Σ value of store returns (`p8-11`). Staged stock is at `LINE_SIDE` and is **not** in the pool until backflushed.
- **Receipt r** with good main base `g_r`, remaining planned main base `M_r` = planned − Σ good main base of earlier posted receipts:
  - `B_r` = value of this receipt's backflush consumption lines (absorbed fully);
  - `I_r` = (`P_I` − Σ earlier `I`) × `min(1, g_r ÷ M_r)`; `M_r ≤ 0` ⇒ ratio 1; `is_final` ⇒ all unabsorbed;
  - `A_r = B_r + I_r` (absorbed by this receipt).
- **Split of `A_r`** in order: (1) by-product credit `C_r` = Σ qty × `by_product_unit_value` (null ⇒ 0), capped at `A_r` (`CST-OPEN-05`); (2) abnormal scrap `S_r` = (`A_r` − `C_r`) × abnormal-scrapped main ÷ (good + rejected + all scrapped main), valued to `VIRT-SCRAP`; normal scrap carries no value of its own; (3) `R_r = A_r − C_r − S_r` split over MAIN (100 − Σ co shares) and each CO_PRODUCT (`cost_share_percent`) by largest remainder; within an output, over its good + rejected quantity; `unit_cost` written with `cost_basis = PRODUCTION_ACTUAL`.
- **Residual at close** `RES` = (`P_I` + Σ `B`) − Σ `A`.

**Example 1 (`WH-SC-639`, `WH-SC-630`).** `PRD-000101`, planned 100, `P_I` = ₹4,00,000.

| Receipt | good / rej / scrap (abnormal) | `B_r` | `M_r` | `I_r` | `A_r` | `S_r` | Output value |
|---|---|---|---|---|---|---|---|
| FGR-51 | 40 / 0 / 0 | 24,000 | 100 | 4,00,000 × 40/100 = 1,60,000 | 1,84,000 | 0 | 40 × 4,600 = 1,84,000 |
| FGR-52 | 55 / 2 / 3 | 36,000 | 60 | 2,40,000 × 55/60 = 2,20,000 | 2,56,000 | 2,56,000 × 3/60 = 12,800 | 2,43,200 over 57 units: good 2,34,666.67, rejected 8,533.33 (unit 4,266.666667) |
| FGR-53 final | 5 / 0 / 0 | 3,000 | 5 | remaining 20,000 (final) | 23,000 | 0 | 5 × 4,600 |

Σ `I` = 4,00,000; `RES` = 0 unless an issue or return lands later (`CST-OPEN-03`).

**Example 2 (`WH-SC-640`, largest remainder).** `RESIN-A` final receipt, pool ₹1,00,001: solvent credit
50 × 12 = 600; `R` = 99,401.00 → A 70 % = 69,580.70, B 30 % = 29,820.30; Σ = 1,00,001.00. With a pool of
₹1,00,000.01: `R` = 99,400.01 → raw 69,580.007 / 29,820.003 → floors 69,580.00 / 29,820.00, one paisa left
goes to the largest remainder (A, 0.7) → **69,580.01 / 29,820.00**; a tie would go to `sequence` 1.

**Example 3 (`WH-SC-641`, settlement).** `RES` = ₹2,000, outputs 100 `PUMP-100`, 40 still on hand →
`ON_HAND_OUTPUT` ₹800 (spread over the on-hand lot/location positions by quantity, largest remainder),
`COST_OF_SALES` ₹1,200. Residual is first split across targets by each target's share of Σ absorbed
(MAIN, each CO_PRODUCT, `ABNORMAL_SCRAP`), then within an output by on-hand vs gone.

---

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from | Extra condition |
|---|---|---|---|---|
| CST-T2-01 | Close (compute; post when under threshold) | `whm_production_orders:close` | order `COMPLETED`, no live settlement | `CST-GRD-02`…`-09` |
| CST-T2-02 | Recompute | `whm_production_settlements:create` | `DRAFT` | — |
| CST-T2-03 | Approve / Reject | `whm_production_settlements:approve` | `DRAFT` (Reject also `APPROVED`) | ≠ creator; production manager |
| CST-T2-04 | Post | `whm_production_settlements:post` | `APPROVED` | `CST-GRD-10` |
| CST-T2-05 | View / export settlements, Cost tab | `:view` / `:export` | any | cost accountant exports; AUDITOR never |
| CST-T2-06 | Print cost sheet | `whm_production_settlements:view` | order `COMPLETED` (watermark *provisional*) or `CLOSED` | — |

## 3. T3 — Time-driven rules & notifications

| ID | Rule | Trigger | What it changes | Who is notified | Channel | Job class | Notify-once? |
|---|---|---|---|---|---|---|---|
| CST-T3-01 | Settlement awaiting approval | `CST-T1-01` with `requires_approval` | nothing | holders of `whm_production_settlements:approve` at the site | in-app — `TBD` DEFERRED-TO-p10-09 | event | once |
| CST-T3-02 | Pending-approval escalation | `warehouse.approval.pending_alert_hours` (as `RQP-T3-03`) | nothing; never auto-approves | as `RQP-T3-03` | as there | `p2-23` job | per episode |
| CST-T3-03 | `COMPLETED` orders not closed at period end (WIP register flag) | stock period soft-close date | nothing — WS-337 WIP-by-order shows them | — | — | computed on read | — |
| CST-T3-04 | No auto-close | — | — | — | — | — | — |

## 4. T4 — Cross-entity effects

| ID | When this happens | Then this other record must change | Enforced in |
|---|---|---|---|
| CST-T4-01 | Receipt post | `A_r` computed per §1.5; `unit_cost`/`extended_value` on output and consumption rows and on the movement lines (`PRODUCTION_ACTUAL`) | receipt post service, same transaction |
| CST-T4-02 | Receipt with BY_PRODUCT output | by-product lines valued at NRV; credit deducted before the split | same |
| CST-T4-03 | Receipt with `SCRAPPED` main units of an `is_abnormal` reason | `S_r` on the scrap line to `VIRT-SCRAP`; `whm_production_receipts.scrap_value` | same |
| CST-T4-04 | Receipt with CO_PRODUCT outputs | largest-remainder split (`CST-GRD-01`) | same |
| CST-T4-05 | Close computes | settlement lines: `ON_HAND_OUTPUT` per (item, lot, location) of the order's output still held by the house owner at the site (any status); `COST_OF_SALES` for the rest; `ABNORMAL_SCRAP` share to `VIRT-SCRAP`; `quantity = 0` on every line | settlement service |
| CST-T4-06 | Settlement posted | one `PRODUCTION_SETTLEMENT` movement, key `PRODUCTION_SETTLEMENT:<id>`, `source_document_type = PRODUCTION_SETTLEMENT`; counter-value from `VIRT-PRODUCTION` (`CST-OPEN-04`); `movement_id` set (deferred trigger refuses `POSTED` with null, FRD §5) | settlement service → `WhbStockLedgerWriter.post` |
| CST-T4-07 | Settlement posted | order `CLOSED`, `closed_at`, `settlement_id`; every reservation of holder `(WAREHOUSE_MANUFACTURING, PRODUCTION_ORDER, orderId, *)` released (`WhbReservationService.releaseByHolder`, `L-10`); open MRQ closed via `WhMaterialRequisitionPort.close`; event `CLOSED` | same transaction |
| CST-T4-08 | Order `CLOSED` | cost-object resolver refuses further issues/returns `409 ORDER_NOT_OPEN` (`WH-SC-643`); MRP stops counting the order as supply | resolver, MRP |
| CST-T4-09 | Any MFG movement posts (`PRODUCTION_RECEIPT`, `PRODUCTION_SETTLEMENT`, `SUBCONTRACT_*`) | standard envelope row in `whb_accounting_handovers` (handover point only) | base writer (`accounting-handover.contract.md`) |
| CST-T4-10 | Operation confirmation minutes × work-centre `cost_rate_per_hour` | shown on the cost sheet as *recorded, not absorbed*; never in `A_r` | cost-sheet provider (`OD-43`) |
| CST-T4-11 | Receipt reversal posted (FR-649) | absorbed values regress by the reversed movement's values; the pool is restored to `VIRT-PRODUCTION` | `mfg-production-receipt` |

## 5. T5 — Screen contract (web only)

### 5.1 `/warehouse/manufacturing/settlements` — WS-329 Settlements & Close

| | |
|---|---|
| **Type** | list + transition modals (reference: **Service Vehicle**) |
| **Grid identifier** | `whm_production_settlements` · filter scope `WAREHOUSE_MFG_SETTLEMENT` |
| **Default sort** | `e.created_at DESC` |
| **Statistics tiles** | `DRAFT` · `APPROVED` · `POSTED` · `REJECTED` · Σ residual (filter-aware) |
| **Columns** | `settlementNumber`, `orderNumber` (GridLink), `orderType`, `itemName`, `warehouseName`, `poolValue`, `absorbedValue`, `residualValue`, `variancePercent`, `requiresApproval`, `status`, `approvedByName`, `approvedAt`, `postedByName`, `postedAt`, `createdByName`, `updatedByName` (money via the currency formatter; timestamps `formatDateWithTimezoneSync`) |
| **Filters** | `warehouseId` → `orderId` (typeahead); `itemId`; `status` (enum); `requiresApproval` (boolean); `createdFrom`/`createdTo` (`date`, timestamp range); `postedFrom`/`postedTo` (`date`) |
| **Row actions** | View (lines by target, `ViewModalBase` tabs Summary · Lines · History) · Recompute (`CST-T2-02`) · Approve · Reject (reason modal) · Post · Print cost sheet |
| **Toolbar** | Export (no Add — creation is **Close** on WS-323/WS-324) |
| **Modals** | Close / Reject / Post: `Modal size="lg" minWidth={500} resizable`; a refused submit shows `<AlertBox type="error">` inside the modal |
| **Export columns** | grid columns + `createdByName`, `updatedByName` |
| **Mobile counterpart** | none |

### 5.2 WS-324 Cost tab (read-only)

Planned cost (rolled at release), pool to date (`P_I` + Σ `B`), absorbed to date, WIP balance
(pool − absorbed), per-receipt absorption rows, by-product credit, abnormal scrap, settlement link.

### 5.3 Print `PRODUCTION_COST_SHEET`

Header (order, item, BOM version, quantities planned/received/scrapped/rejected, dates); components
(required vs consumed base qty, planned unit cost vs actual value, deviation reason); outputs (planned,
received, absorbed value, unit cost, settlement share); scrap normal/abnormal with reasons; by-product
credit; residual and its target split; work-centre minutes × rate *recorded, not absorbed*. Provider
implements `WarehousePrintDataProvider`; kind seeded in `V560001`.

## 6. Out of scope

| Not built | Where / why |
|---|---|
| Standard costing, price/quantity/lot-size variance accounts | R-05, `OD-40` re-entry path |
| Labour / overhead absorption | `OD-43` — recorded only |
| GL postings, journals, debit/credit notes | R-14, FR-657 |
| Subcontract processing charge in FG cost | trade/accounting (FR-658); `SUB-OPEN-06` |
| Period-end WIP revaluation | WIP stays at actual in `VIRT-PRODUCTION`; WS-337 reports it |

## 7. Amendments

| Date | Row IDs affected | Change | Found by |
|---|---|---|---|
| 2026-10-22 | all | v0 derived from `docs/frd/FRD-MFG.md`; not ratified | contract derivation (design set) |

## 8. Invariants and scenarios this workflow must not break

| Invariant | Rows | Scenarios |
|---|---|---|
| `L-15` value conservation | `CST-T4-06`, `MPR-T1-11`, `MPR-GRD-02` | `WH-SC-641` |
| Exact split (`R-4`, `RF-009`) | `CST-GRD-01`, `CST-T4-04` | `WH-SC-640` |
| One movement per posting document (FRD §5) | `CST-T4-06` | `WH-SC-641` |
| `L-14` non-own never valued | `CST-GRD-09` | — (OD-42 v1.1) |
| `L-8` period-bound | `CST-T1-04` via `MPR-GRD-09`/`-10` | — |
| Abnormal scrap outside good-unit cost | `CST-T4-03` | `WH-SC-630` |

## 9. Open rows — contradictions and holes

| ID | Contradiction / hole | Recommendation | Authority | Status |
|---|---|---|---|---|
| CST-OPEN-01 | §5 ladder is `DRAFT → APPROVED → POSTED`, but FR-656 needs approval only above threshold; no `DRAFT → POSTED` path is listed | below threshold Close creates and posts in one transaction (`CST-T1-01`) | FR-656 vs §5 | open |
| CST-OPEN-02 | `whm_production_settlements.order_id` is a plain **uk**: after a `REJECTED` settlement no new one can be created; FR-634 "reopen until a settlement exists" ignores `REJECTED` | partial uk `WHERE status <> 'REJECTED'` (the reversal-table shape); a `REJECTED` settlement does not block reopen | FRD §4, FR-634 | open |
| CST-OPEN-03 | `WH-SC-641` has a store issue **after** the final receipt, but the `PRODUCTION_ORDER` resolver accepts only `RELEASED`/`IN_PROGRESS` (§3.2, FR-640) and the final receipt sets `COMPLETED` — the residual's main source is unreachable | resolver admits `COMPLETED` for **returns** always and for issues with a `PRODUCTION_DEVIATION` reason (not under `STRICT`); or amend `WH-SC-641` to a return | FR-640, FR-656, `WH-SC-641` | open |
| CST-OPEN-04 | `MPR-T1-11` balances a value-only movement against `VALUE_OFFSET`; the settlement's counter-value is the residual in `VIRT-PRODUCTION` | admit `VIRT-PRODUCTION` as the counter location for `PRODUCTION_SETTLEMENT` (type-level `value_counter_purpose`), else the pool never empties | `MPR-T1-11`, FR-656 | open |
| CST-OPEN-05 | By-product NRV credit above the absorbed value (research §11) is undefined | cap at `A_r`; the excess is not credited; flagged on the cost sheet | FR-654 | open |
| CST-OPEN-06 | FR-656 sends the consumed part to `VIRT-COST_OF_SALES`; output consumed by a **parent production order** (sub-assembly) is WIP of the parent, not cost of sales | consumed-into-order quantity → that parent's `VIRT-PRODUCTION` pool when it is still open, else COGS | FR-656, FR-633 | open |
| CST-OPEN-07 | A negative residual larger than the on-hand lots' value would drive a lot's value below zero | cap the on-hand share at the positions' carried value; remainder to `COST_OF_SALES` | `L-15`, FR-656 | open |
| CST-OPEN-08 | Zero residual: the deferred trigger refuses `POSTED` with null `movement_id`, but a zero-value movement is pointless | exempt `residual_value = 0` from the trigger and post no movement | FRD §5 | open |
