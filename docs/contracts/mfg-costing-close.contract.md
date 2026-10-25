# Functional Contract — Production costing, settlement and close (`warehouse-manufacturing`)

> **What this is.** The functional truth for valuing production output at actual (`OD-40`, MD-06): the
> order's cost pool in `VIRT-PRODUCTION-<site>`, what each production receipt absorbs, by-product NRV
> credit, abnormal scrap, the exact co-product split, and the **close** — a settlement
> (`DRAFT → POSTED` below the variance threshold, `DRAFT → APPROVED → POSTED` above it, `DRAFT → REJECTED` — MD-22) that posts one value-only `PRODUCTION_SETTLEMENT` movement
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
| **Workflow** | Issues / backflush fill the pool → each receipt absorbs → final receipt → order `COMPLETED` → late store issues / returns accepted while `COMPLETED` (MD-14) → **Close** computes the residual → settlement `DRAFT` → (approve, above threshold) → `POSTED` → order `CLOSED` |
| **Module** | `warehouse-manufacturing` (`whm_`). Value math through `WhbCostLayerMath` (`WB/…/WhbCostLayerMath.java:31-32`, `split` = `R-4`); receipts post through `WhbStockLedgerWriter.post` (`:333`); the settlement through `WhbValueOnlyMovementPoster` + `WhbCostingEngine.lockLayers` / `restateLayerValue` (`WhbCostingEngine.java:946-975`), in the order `WhLandedCostPostingService.java:170-190` uses (MD-34) |
| **Domain baseline** | FRD-MFG FR-638, FR-646, FR-654…FR-657, FR-661, §3.1 (`PRODUCTION_SETTLEMENT`), §8 settings, MD-06, `OD-40`, `OD-43` · `DECISIONS.md` `L-1`, `L-8`, `L-10`, `L-14`, `L-15`, `R-4`, `RF-009` · `MPR-T1-01`, `MPR-T1-11`, `MPR-GRD-02`, `-09`, `-10` |
| **Owning task bodies** | **`p10-07`** builds the per-receipt absorption and split (§1.5, `CST-T4-01`…`-04`, `CST-GRD-01`) inside the receipt post (MD-37, R29 F23); **`p10-09`** builds close, settlement and the cost sheet (the rest). `p10-09` depends on `p10-07`, `p8-09`/`p8-10`/`p8-11` + SEAM-M1/M2 (issues land in `VIRT-PRODUCTION` and roll up), `p10-10` (subcontract balance) |
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
| A2 | By-product credit at NRV first; abnormal scrap share out of the pool to the MFG-side loss record; rest split over MAIN + CO_PRODUCT; Σ output values = absorbed pool exactly, reproducible (`WH-SC-630`, `WH-SC-640`) | `CST-T4-02`…`-04`, `CST-GRD-01`, §1.5 example 2 |
| A3 | Close posts one value-only `PRODUCTION_SETTLEMENT` putting the residual on on-hand output lots and `VIRT-COST_OF_SALES` for the consumed/shipped part (`WH-SC-641`) | `CST-T1-01`, `CST-T1-04`, `CST-T4-05` |
| A4 | Residual share above `close_variance_approval_percent` waits for a second user; the order stays `COMPLETED` (`WH-SC-642`) | `CST-T1-01`, `CST-T1-02`, `CST-GRD-06` |
| A5 | Close requires no open staging list, draft receipt or open subcontract balance; releases reservations; closes the MRQ; `CLOSED` refuses further issues (`WH-SC-643`, `WH-SC-648`) | `CST-GRD-02`…`-05`, `CST-T4-06`…`-08` |
| A6 | Non-own orders are never valued; labour/overhead recorded, not absorbed (`L-14`, `OD-43`) *(second half superseded by `D-20` item 20: absorbed — `CST-T4-20`…`-22`)* | `CST-GRD-09`, `CST-T4-10` |
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

| ID | From | Event / action | To | Guard (service, first) | Actor (permission) | Side effects | Comment/reason required | UI entry point | Source |
|---|---|---|---|---|---|---|---|---|---|
| CST-T1-01 | order `COMPLETED`, no live settlement | **Close** — compute pool, absorbed, residual, variance %, target lines | `DRAFT` when `requires_approval`; else **`POSTED` in the same transaction** (MD-22) | `CST-GRD-02`…`-05`, `-07`, `-08`, `-09`; when posting, also `CST-GRD-10` + `MPR-T1-11` guards | `whm_production_orders:close` | `PST-` number at create (gapless, site, yearly); lines computed (`CST-T4-05`); `requires_approval = variance_percent > setting`; when posting: `CST-T4-06`…`-09`; order `CLOSED`; a **zero residual** posts no movement — the settlement is `POSTED` with a null `movement_id`, exempt from the deferred trigger (R31 `CST-OPEN-08`) | no (a note may be added) | WS-323 row / WS-324 header **Close**; modal shows the computed lines before confirm | FR-656 |
| CST-T1-02 | `DRAFT` | **Approve** | `APPROVED` | `CST-GRD-06`, `CST-GRD-11` | `whm_production_settlements:approve` | `approved_by/at` | no | WS-329 row **Approve** | FR-656 |
| CST-T1-03 | `DRAFT` | **Reject** | `REJECTED` | approver ≠ creator (`CST-GRD-06`) | `whm_production_settlements:approve` | order stays `COMPLETED`; reopen or a new Close becomes possible again (MD-22) | **yes** | WS-329 row **Reject** | FR-656 |
| CST-T1-04 | `APPROVED` | **Post** | `POSTED`; order `CLOSED` — one transaction | `CST-GRD-10`, `CST-GRD-11`, then `MPR-T1-11` (`MPR-GRD-02`, `-09`, `-10`, `-11`) | `whm_production_settlements:post` — not `:approve` (`RJ-005`) | `CST-T4-06`…`-09` | no | WS-329 row **Post** | FR-656 |
| CST-T1-05 | `APPROVED` | Reject an approved settlement whose Post is refused (stale, period closed) | `REJECTED` | — | `whm_production_settlements:approve` | as `-03` | **yes** | WS-329 row **Reject** | FR-656 |
| CST-T1-06 | — | **Recompute** a `DRAFT` (pool moved) | `DRAFT` (lines replaced) | `CST-GRD-03` | `whm_production_settlements:create` | lines and values rewritten; `approved_*` stays null | no | WS-329 row **Recompute** | FR-656 |
| CST-T1-07 | `POSTED` | Reverse the settlement / reopen the order | refused | `CST-UNR-01` | any | — | — | none | FR-656 |

### 1.3 Guards

| ID | Predicate (must hold to proceed) | Refusal: HTTP · code · field | Message shape | DB backstop | Source |
|---|---|---|---|---|---|
| CST-GRD-01 | Σ output `extended_value` + abnormal-scrap value + by-product credit = receipt absorbed value, to the scale of `WhbCostLayerMath.split`; split by largest remainder, ties to lowest output `sequence` | — (service-constructed; asserted by test; a mismatch is an incident) | — | `MPR-GRD-01`/`I-21` value balance | FR-655, `R-4`, `RF-009` |
| CST-GRD-02 | **This contract owns the close guard** (`CST-GRD-02`…`-08`; `PRO-GRD-15` and `SUB-GRD-14` cite it — R31 F-MF-006). The order's **line-side balance is zero** — staged − unstaged − consumed at the line side, read from the positions whatever any staging list's status (a `STAGED` or `CLOSED` list can still leave stock there) — and no staging list of the order is `DRAFT`/`RELEASED`/`PARTIALLY_STAGED` | `409 ORDER_HAS_OPEN_STAGING` · `orderId` | lists `STG-` numbers and the line-side quantity per component | — | FR-656 |
| CST-GRD-03 | No receipt of the order in `DRAFT`/`PENDING_APPROVAL`; no reversal `REQUESTED`/`APPROVED` | `409 ORDER_HAS_OPEN_RECEIPT` · `orderId` | lists `FGR-`/`PRV-` | — | FR-656, FR-649 |
| CST-GRD-04 | Subcontract order: every reconciliation `open_base_quantity = 0` and `pending_write_off_base_quantity = 0` — a `REQUESTED` write-off action still blocks (MD-26) — and no dispatch of the order is `DRAFT` (R31 F-MF-006) | `409 SUBCONTRACT_BALANCE_OPEN` · `orderId`; `409 SUBCONTRACT_DISPATCH_DRAFT_OPEN` · `orderId` | lists item/lot/qty (`WH-SC-648`) or the `SCD-` numbers | — | FR-661 |
| CST-GRD-05 | No live settlement for the order (`DRAFT`/`APPROVED`/`POSTED`) | `409 SETTLEMENT_EXISTS` · `orderId` | names the `PST-` | partial unique index `(order_id) WHERE status <> 'REJECTED'` (MD-22) | FR-656 |
| CST-GRD-06 | Approver/rejecter ≠ settlement creator | `403 SETTLEMENT_SELF_APPROVAL` · `id` (MD-21) | — | — | FR-656 |
| CST-GRD-07 | Order status `COMPLETED` | `409 ORDER_NOT_COMPLETED` · `orderId` | names status | — | FR-656 |
| CST-GRD-08 | The order's MRQ (if any) can be closed through `WhMaterialRequisitionPort.close` (no unposted store issue against it) | `409 ORDER_REQUISITION_OPEN` · `orderId` | names MRQ and the draft issue | — | FR-656, `p8-09` |
| CST-GRD-09 | Order owner is the house owner; a non-own order (`OD-42`, v1.2) posts **no** value and no settlement movement | `422 NON_OWN_ORDER_NOT_VALUED` (informational only when OD-42 lands) · `ownerId` | — | `L-14` writer rule | FR-654, `L-14` |
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

- **The pool is MFG's record.** Virtual lines carry no cost layer (`WhbCostingEngine.java:257`); the engine mirrors each virtual line from its real side (`mirrorVirtualLines`). So MFG reads every value it pools **back from the posted movement's real lines** and keeps it on its own rows; nothing in the ledger "holds" WIP.
- **Issued pool** `P_I` = Σ value of store issues into `VIRT-PRODUCTION` for the order (SEAM-M1) − Σ value of store returns (`p8-11`) **+ `P_D`** for a `SUBCONTRACT` order: Σ `whm_subcontract_dispatch_lines.dispatched_value` (the store-side lines' relieved value) − Σ recalled value (recall restores the dispatched layers through `costSourceLineId`, `WhbCostingEngine.java:417-428`) − Σ written-off value (moved to the abnormal-loss record) (MD-32, R29 F6). Staged stock is at `LINE_SIDE` and is **not** in the pool until backflushed.
- **Receipt r** with good main base `g_r`, remaining planned main base `M_r` = planned − Σ good main base of earlier posted receipts:
  - `B_r` = value of this receipt's backflush consumption lines read back from the movement (absorbed fully; 0 for a subcontract receipt, whose backflush is job-worker → `VIRT-PRODUCTION`, virtual to virtual);
  - `I_r` = (`P_I` − Σ earlier `I`) × `min(1, g_r ÷ M_r)`; `M_r ≤ 0` ⇒ ratio 1; `is_final` ⇒ all unabsorbed;
  - `A_r = B_r + I_r` (absorbed by this receipt).
- **Split of `A_r`** in order: (1) by-product credit `C_r` = Σ qty × `by_product_unit_value` (null ⇒ 0), capped at `A_r` — the excess is not credited and is flagged on the cost sheet (`CST-OPEN-05`); (2) abnormal scrap `S_r` = (`A_r` − `C_r`) × abnormal-scrapped main ÷ (good + rejected + all scrapped main), taken out of the pool as an **MFG-side loss record** (`whm_production_receipts.scrap_value`, WS-337) — the `SCRAPPED` line pair is `VIRT-PRODUCTION` → `VIRT-SCRAP`, virtual only, and the ledger cannot carry its value (R29 F20); normal scrap carries no value of its own; (3) `R_r = A_r − C_r − S_r` split over MAIN (100 − Σ co shares) and each CO_PRODUCT (`cost_share_percent`) by largest remainder; within an output, over its good + rejected quantity; each real output line **states `extendedCost`** (its share) with `costBasis` null — the type default — and the counter lines no cost (the VAS shape, `WhWorkOrderPostingService.java:78-93`; `PRODUCTION_ACTUAL` is not a known basis, `WhbMovementTypeValidationService.java:46`; R29 F19); `unit_cost` on MFG's own rows is display only (= extended ÷ base quantity).
- **Same-item output** (rework): when the output grain nets to zero against its input the engine posts the grain's current average whatever is stated (`WhbCostingEngine.java:278-289`); the receipt states that figure (the F460 precedent), `A_r` = that figure, and the extras stay in the residual for the settlement (MD-33, R29 F7).
- **Residual at close** `RES` = (`P_I` + Σ `B`) − Σ `A`.

**Example 1 (`WH-SC-639`, `WH-SC-630`).** `PRD-000101`, planned 100, `P_I` = ₹4,00,000.

| Receipt | good / rej / scrap (abnormal) | `B_r` | `M_r` | `I_r` | `A_r` | `S_r` | Output value |
|---|---|---|---|---|---|---|---|
| FGR-51 | 40 / 0 / 0 | 24,000 | 100 | 4,00,000 × 40/100 = 1,60,000 | 1,84,000 | 0 | 40 × 4,600 = 1,84,000 |
| FGR-52 | 55 / 2 / 3 | 36,000 | 60 | 2,40,000 × 55/60 = 2,20,000 | 2,56,000 | 2,56,000 × 3/60 = 12,800 | 2,43,200 over 57 units: good 2,34,666.67, rejected 8,533.33 (unit 4,266.666667) |
| FGR-53 final | 5 / 0 / 0 | 3,000 | 5 | remaining 20,000 (final) | 23,000 | 0 | 5 × 4,600 |

Σ `I` = 4,00,000; `RES` = 0 unless an issue or return lands later — accepted while the order is `COMPLETED` (MD-14).

**Example 2 (`WH-SC-640`, largest remainder).** `RESIN-A` final receipt, pool ₹1,00,001: solvent credit
50 × 12 = 600; `R` = 99,401.00 → A 70 % = 69,580.70, B 30 % = 29,820.30; Σ = 1,00,001.00. With a pool of
₹1,00,000.01: `R` = 99,400.01 → raw 69,580.007 / 29,820.003 → floors 69,580.00 / 29,820.00, one paisa left
goes to the largest remainder (A, 0.7) → **69,580.01 / 29,820.00**; a tie would go to `sequence` 1.

**Example 3 (`WH-SC-641`, settlement).** `RES` = ₹2,000, outputs 100 `PUMP-100`, 40 still on hand →
`ON_HAND_OUTPUT` ₹800 (spread over the on-hand lot/location positions by quantity, largest remainder),
`COST_OF_SALES` ₹1,200. Residual is first split across targets by each target's share of Σ absorbed
(MAIN, each CO_PRODUCT, `ABNORMAL_SCRAP`), then within an output by on-hand vs gone. The `ABNORMAL_SCRAP` share is a record line (no movement line); only `ON_HAND_OUTPUT` and `COST_OF_SALES` lines reach the movement.

---

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from | Extra condition | Source |
|---|---|---|---|---|---|
| CST-T2-01 | Close (compute; post when under threshold) | `whm_production_orders:close` | order `COMPLETED`, no live settlement | `CST-GRD-02`…`-09` | FR-656 |
| CST-T2-02 | Recompute | `whm_production_settlements:create` | `DRAFT` | — | FR-656 |
| CST-T2-03 | Approve / Reject | `whm_production_settlements:approve` | `DRAFT` (Reject also `APPROVED`) | ≠ creator; production manager | FR-656 |
| CST-T2-04 | Post | `whm_production_settlements:post` | `APPROVED` | `CST-GRD-10` | FR-656 |
| CST-T2-05 | View / export settlements, Cost tab | `:view` / `:export` | any | cost accountant exports; AUDITOR never | FR-656, FR-669 |
| CST-T2-06 | Print cost sheet | `whm_production_settlements:view` | order `COMPLETED` (watermark *provisional*) or `CLOSED` | — | FR-656 |

## 3. T3 — Time-driven rules & notifications

| ID | Rule | Trigger | What it changes | Who is notified | Channel | Job class | Notify-once? | Source |
|---|---|---|---|---|---|---|---|---|
| CST-T3-01 | Settlement awaiting approval | `CST-T1-01` with `requires_approval` | nothing | holders of `whm_production_settlements:approve` at the site | in-app — `TBD` DEFERRED-TO-p10-09 | event | once | FR-656 |
| CST-T3-02 | Pending-approval escalation | `warehouse.approval.pending_alert_hours` (as `RQP-T3-03`) | nothing; never auto-approves | as `RQP-T3-03` | as there | `p2-23` job | per episode | FR-656 |
| CST-T3-03 | `COMPLETED` orders not closed at period end (WIP register flag) | stock period soft-close date | nothing — WS-337 WIP-by-order shows them | — | — | computed on read | — | FR-656 |
| CST-T3-04 | No auto-close | — | — | — | — | — | — | FR-656 |

## 4. T4 — Cross-entity effects

| ID | When this happens | Then this other record must change | Enforced in | Source |
|---|---|---|---|---|
| CST-T4-01 | Receipt post | `A_r` computed per §1.5; `extended_value` (and display `unit_cost`) on output and consumption rows; each real output movement line states `extendedCost`, `costBasis` null (MD-34) | receipt post service (`p10-07`), same transaction | FR-654 |
| CST-T4-02 | Receipt with BY_PRODUCT output | by-product lines valued at NRV; credit deducted before the split | same | FR-654 |
| CST-T4-03 | Receipt with `SCRAPPED` main units of an `is_abnormal` reason | `S_r` leaves the pool into `whm_production_receipts.scrap_value` — an MFG-side record and a recorded accounting handover point; **no** value on the virtual scrap lines (R29 F20) | same | FR-654 |
| CST-T4-04 | Receipt with CO_PRODUCT outputs | largest-remainder split (`CST-GRD-01`) | same | FR-655 |
| CST-T4-05 | Close computes | settlement lines: `ON_HAND_OUTPUT` per (item, lot, location) of the order's output still held by the house owner at the site (any status), each **capped at that position's carried value** (R31 `CST-OPEN-07`); output **consumed into a parent production order** follows the parent (R31 `CST-OPEN-06`): while the parent is open a `PARENT_ORDER_WIP` line (`parent_order_id`) adds the share to the parent's pool `P_I`, stated at `VIRT-PRODUCTION-<site>` with the parent as source; once the parent is closed, the share goes to the parent's output lots still on hand (capped the same way); a parent's closure alone is never treated as a sale; `COST_OF_SALES` takes the rest — and any capped excess; `ABNORMAL_SCRAP` share as a record line with no movement line; `quantity = 0` on every movement line | settlement service | FR-656 |
| CST-T4-06 | Settlement posted | the landed-cost path (MD-34, R29 F8): (1) one `PRODUCTION_SETTLEMENT` movement through **`WhbValueOnlyMovementPoster`**, key `PRODUCTION_SETTLEMENT:<id>`, `source_document_type = PRODUCTION_SETTLEMENT` — stated lines `quantity = 0`, signed `extendedCost` on each on-hand output lot / location and on the site's `COST_OF_SALES` virtual location; the poster **generates** the `VALUE_OFFSET` counter line (`WhbValueOnlyMovementPoster.java:22-31`) — the "`+layer / +cogs / −whole`" shape; (2) `WhbCostingEngine.lockLayers` on every on-hand layer of those lots, re-check the split against what was read (refuse `409 SETTLEMENT_STALE` if a layer moved); (3) `restateLayerValue(warehouseId, layerId, part, actor, movementId, occurredAt)` per layer, because a zero-quantity line never touches a layer (`WhbCostingEngine.java:257`) and restatement is the caller's job (`:946-952`); `movement_id` set (deferred trigger refuses `POSTED` with null, FRD §5; a zero residual posts nothing and is exempt — `CST-OPEN-08`) | settlement service → `WhbValueOnlyMovementPoster`, `WhbCostingEngine` | FR-656 |
| CST-T4-07 | Settlement posted | order `CLOSED`, `closed_at`, `settlement_id`; every reservation of holder `(WAREHOUSE_MANUFACTURING, PRODUCTION_ORDER, orderId, *)` released (`WhbReservationService.releaseByHolder`, `L-10`); open MRQ closed via `WhMaterialRequisitionPort.close`; event `CLOSED` | same transaction | FR-656 |
| CST-T4-08 | Order `CLOSED` | cost-object resolver refuses further issues/returns `409 ORDER_NOT_OPEN` (`WH-SC-643`); MRP stops counting the order as supply | resolver, MRP | FR-656 |
| CST-T4-09 | Any MFG movement posts (`PRODUCTION_RECEIPT`, `PRODUCTION_SETTLEMENT`, `SUBCONTRACT_*`) | standard envelope row in `whb_accounting_handovers` (handover point only) | base writer (`accounting-handover.contract.md`) | FR-657 |
| CST-T4-10 | Operation confirmation minutes × work-centre `cost_rate_per_hour` | shown on the cost sheet as *recorded, not absorbed*; never in `A_r` *(superseded by `D-20` item 20 when `costing.absorb_conversion` = `true` (default): conversion rows `CST-T4-20` enter the pool)* | cost-sheet provider (`OD-43`) | FR-654 |
| CST-T4-11 | Receipt reversal posted (FR-649) | absorbed values regress by the reversed movement's values; the pool record is restored | `mfg-production-receipt` | FR-649 |
| CST-T4-12 | Subcontract dispatch / recall / approved write-off posted (`SUB-T4-01`, `-08`, `-10`) | `P_D` += dispatched value / −= restored value / −= written-off value (written-off value → the abnormal-loss record) (MD-32) | `mfg-subcontracting` → costing service | FR-654, FR-658 |

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
| ~~Labour / overhead absorption~~ | ~~`OD-43` — recorded only~~ — **superseded by `D-20` item 20** (§12) |
| GL postings, journals, debit/credit notes | R-14, FR-657 |
| Subcontract processing charge in FG cost | the warehouse-trade subcontract service-line PO lands it on the processed item (FR-658, D-18 item 3, SEAM-M7); MFG posts no charge |
| Period-end WIP revaluation | WIP stays at actual in the order's pool record (MFG); WS-337 reports it |

## 7. Amendments

| Date | Row IDs affected | Change | Found by |
|---|---|---|---|
| 2026-10-22 | all | v0 derived from `docs/frd/FRD-MFG.md`; not ratified | contract derivation (design set) |
| 2026-10-22 | §0, §1.5, `CST-T4-01`, `-03`, `-05`, `-06`, `-11`, `-12`, `CST-OPEN-04` | R29: subcontract dispatched value in the pool, recall and write-off out (F6, MD-32); same-item rework extras to settlement (F7, MD-33); settlement restates layers on the landed-cost path (F8); `extendedCost`, type-default basis (F19); abnormal scrap MFG-side (F20); absorption built in `p10-07` (F23, MD-37); `LANDED_COST_APPLY` row shape, `CST-OPEN-04` closed (F30, MD-34) | `R29-functional-review-mfg.md` |
| 2026-10-23 | `CST-T1-01`, `CST-GRD-02`, `-04`, §1.5, `CST-T4-05`, `-06`, §6, Source column, `CST-OPEN-05`…`-08` | R31: CST owns the one close guard, line-side balance read whatever the list status, `DRAFT` dispatch blocks (F-MF-006); parent-order target, on-hand cap, zero residual (DECIDE rows); processing charge via the trade subcontract PO (D-18 item 3); Source FR on every rule row (F-MF-018) | `R31-functional-review-mfg.md`, `R31-decisions.md` |
| 2026-10-22 | T1, §9 | Consistency pass: `DRAFT → POSTED` below threshold and partial unique index (MD-22), late issues on `COMPLETED` (MD-14), `403` self-approval (MD-21), `REQUESTED` write-off blocks close (MD-26) | FRD-MFG §9 |
| 2026-10-25 | R32 (`D-20` item 20, Ind AS 2; `OD-43` reversed): §12 — conversion cost from bookings absorbed into WIP / FG, abnormal time excluded, GL left to accounting; pre-sale cost estimate service (FR-829, FR-831) |

## 8. Invariants and scenarios this workflow must not break

| Invariant | Rows | Scenarios |
|---|---|---|
| `L-15` value conservation | `CST-T4-06`, `MPR-T1-11`, `MPR-GRD-02` | `WH-SC-641` |
| Exact split (`R-4`, `RF-009`) | `CST-GRD-01`, `CST-T4-04` | `WH-SC-640` |
| One movement per posting document (FRD §5) | `CST-T4-06` | `WH-SC-641` |
| `L-14` non-own never valued | `CST-GRD-09` | — (OD-42 v1.2) |
| `L-8` period-bound | `CST-T1-04` via `MPR-GRD-09`/`-10` | — |
| Abnormal scrap outside good-unit cost | `CST-T4-03` | `WH-SC-630` |

## 9. Open rows — contradictions and holes

| ID | Contradiction / hole | Recommendation | Authority | Status |
|---|---|---|---|---|
| CST-OPEN-01 *(resolved — MD-22)* | §5 ladder is `DRAFT → APPROVED → POSTED`, but FR-656 needs approval only above threshold; no `DRAFT → POSTED` path is listed | below threshold Close creates and posts in one transaction (`CST-T1-01`) | FR-656 vs §5 | resolved |
| CST-OPEN-02 *(resolved — MD-22)* | `whm_production_settlements.order_id` is a plain **uk**: after a `REJECTED` settlement no new one can be created; FR-634 "reopen until a settlement exists" ignores `REJECTED` | partial uk `WHERE status <> 'REJECTED'` (the reversal-table shape); a `REJECTED` settlement does not block reopen | FRD §4, FR-634 | resolved |
| CST-OPEN-03 *(resolved — MD-14: the resolver admits `COMPLETED` for issues and returns under the normal consumption policy; STORES `FR-533` / `SIR-GRD-01a` amended)* | `WH-SC-641` has a store issue **after** the final receipt, but the `PRODUCTION_ORDER` resolver accepts only `RELEASED`/`IN_PROGRESS` (§3.2, FR-640) and the final receipt sets `COMPLETED` — the residual's main source is unreachable | resolver admits `COMPLETED` for **returns** always and for issues with a `PRODUCTION_DEVIATION` reason (not under `STRICT`); or amend `WH-SC-641` to a return | FR-640, FR-656, `WH-SC-641` | resolved |
| CST-OPEN-04 *(resolved — R29 F30, MD-34; no base change)* | `MPR-T1-11` balances a value-only movement against `VALUE_OFFSET`; the settlement's counter-value is the residual in `VIRT-PRODUCTION` | the counter is `VALUE_OFFSET`, generated by `WhbValueOnlyMovementPoster`; the pool is MFG's record and empties on MFG's rows, so no `VIRT-PRODUCTION` counter is needed; `PRODUCTION_SETTLEMENT` copies the `LANDED_COST_APPLY` row (`V500003:225`) | `MPR-T1-11`, FR-656 | resolved |
| CST-OPEN-05 *(resolved — R31-decisions DECIDE: default stands)* | By-product NRV credit above the absorbed value (research §11) is undefined | cap at `A_r`; the excess is not credited; flagged on the cost sheet (§1.5; IAS 2 §14) | FR-654 | resolved |
| CST-OPEN-06 *(resolved — R31-decisions DECIDE: default replaced)* | FR-656 sends the consumed part to `VIRT-COST_OF_SALES`; output consumed by a **parent production order** (sub-assembly) is WIP of the parent, not cost of sales | quantity consumed into a parent follows the parent: while it is open, its `VIRT-PRODUCTION` pool (`PARENT_ORDER_WIP`); once closed, its output lots still on hand (capped as `CST-OPEN-07`), the remainder to COGS; the parent's closure alone is not a sale (`CST-T4-05`, FRD §4) | FR-656, FR-633 | resolved |
| CST-OPEN-07 *(resolved — R31-decisions DECIDE: default stands)* | A negative residual larger than the on-hand lots' value would drive a lot's value below zero | cap the on-hand share at the positions' carried value; the remainder goes to the target `CST-OPEN-06` gives (`CST-T4-05`) | `L-15`, FR-656 | resolved |
| CST-OPEN-08 *(resolved — R31-decisions DECIDE: default stands)* | Zero residual: the deferred trigger refuses `POSTED` with null `movement_id`, but a zero-value movement is pointless | exempt `residual_value = 0` from the trigger and post no movement (`CST-T1-01`, `CST-T4-06`, FRD §5) | FRD §5 | resolved |

## 12. R32 rules (PRD 2026-10-24, `D-20`)

Owning tasks: `issues/p10-09.md` (FR-829) and `issues/p10-25.md` (FR-831), each under its R32 section.

| ID | Rule | Refusal / effect | Source |
|---|---|---|---|
| CST-T4-20 | Each booking adds `whm_order_conversion_costs` rows: crew minutes × labour rate, machine minutes × machine rate (machine override, else work centre), overhead per `costing.overhead_basis`; a cancelled booking adds reversing rows; orders without bookings take routing standard minutes at receipt | pool += conversion | FR-829 |
| CST-T4-21 | Absorption: each receipt absorbs conversion by the FR-654 proportion; the settlement capitalises the residual conversion with the material residual; WS-337 WIP shows material and conversion separately | — | FR-829 |
| CST-T4-22 | Time booked with an abnormal idle / downtime reason is valued and reported as abnormal, never absorbed into output (Ind AS 2 ¶16) | abnormal record | FR-829 |
| CST-UNR-20 | MFG posting a GL entry for absorption or under / over-absorption | handover only; GL is accounting's (`neetub1508/accounting`) | FR-829 |
| CST-T1-20 | `CostEstimatePort.estimate` (and WS-395 *Run estimate*): explode the BOM (variant-aware), price each component from current cost layers, else last purchase price (flagged), add routing minutes × rates and overhead, compute DVA % by item origin; store a `whm_cost_estimates` row | `422 BOM_NOT_FOUND` / `ROUTING_NOT_EFFECTIVE` when neither exists; `missing_cost_count` reported | FR-831 |
| CST-UNR-21 | The estimate proposing a selling price or margin | pricing stays trade's | FR-831 |
