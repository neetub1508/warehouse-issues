# Functional Contract — Repairable spares: old part in, out to the repairer, back as refurbished

> **What this is.** The functional truth for the maintenance-stores repair cycle of `#737` (WR3-14, catalogue
> row 39). A repairable spare is issued only against its worn unit. The worn unit is booked back as a separate
> **defective** item at an assessed value. A **repair order** sends it to the repairer and brings it back as a
> separate **refurbished** item, valued at the defective value plus the repair charge. The RGP and the delivery
> challan ride on the repair order, and the RGP-pending register ages what is at the repairer.
>
> **What this is not.** It does not post the repairer's bill, decide GST input credit, deduct TDS or touch the GL.
> Those are accounting's (§6). It does not change the valuation grain (`IRR-40`) and does not build on the fenced
> style / variant schema (`DECISIONS.md` D-18 item 2: "nothing more is built on it").
>
> **Status.** Derived 2026-11-16 (v0) by the functional-reviewer in DECISION MODE (R49 lane RA1, Claude + GPT),
> from the `#737` S1 review (R39), the code at classic `dc9b39f1a7`, and the precedents named per row. Not ratified.
> It supersedes the S1 driver ruling's "CONDITION variant axis" (see §7, 2026-11-16).

---

## 0. Identity

| | |
|---|---|
| **Workflow** | (1) Store issue of a repairable item → the worn unit booked back at post (or later, under `WARN`) as the item's **defective** twin. (2) Repair order: create → dispatch (stock to the repairer's custody location; RGP + challan raised from it) → receive (repaired → **refurbished** twin; not repairable → defective twin back) → `RECEIVED`, or close short |
| **Module** | `warehouse` (repair order, old-part capture, register, setting); `warehouse-base` (item columns, reason code, movement type); `warehouse-india` (challan source only) |
| **Domain baseline** | `L-1`, `L-11` (goods at a job worker / repairer are still ours), `IRR-40` (grain `COMPANY_OWNER_ITEM_SITE`, unchanged), `STO-D4` (a gate pass posts no stock — unchanged), `#22 G3` custody pool (`WhbCostingEngine.java:459`, `WhbOpenCostLayerSql.custodyLayer`), `SUB-T4-07` (stated `extendedCost` on a converted inbound line, `WhbCostingEngine.java:454`), `SIR-T4-03` (the `ISSUE_RETURN` leg from `VIRT-CONSUMED`), [`store-issue-return`](store-issue-return.contract.md), [`gate-entry`](gate-entry.contract.md), [`india-movement-documents`](india-movement-documents.contract.md), [`accounting-handover`](accounting-handover.contract.md) `AHO-T1-01` |
| **Owning task** | `issues/rw-wr3-14.md` (`#737`) |
| **Primary tables** | `whb_items` + 3 columns (`is_repairable`, `repair_defective_item_id`, `repair_refurbished_item_id`); `wh_store_issue_old_parts` (one row per old-part booking: issue line, defective item, base quantity, serial, location, assessed value, movement id, posted by/at); `wh_repair_orders`, `wh_repair_order_lines`, `wh_repair_order_receipt_lines` |
| **Status column** | `wh_repair_orders.status` — `DRAFT` · `DISPATCHED` · `PARTIALLY_RECEIVED` · `RECEIVED` · `CLOSED` · `CANCELLED` (CHECK) |
| **Permission resources** | `wh_repair_orders:{view,view:all,view:branch,create,edit,dispatch,receive,close,cancel,export}` (site scope pair as on `wh_store_issues`). Old-part booking reuses `wh_store_issues:post`. Item columns reuse `whb_items:edit`. Value cells need `warehouse:cost:view` |
| **Routes** | `/warehouse/stores/repairs` (Repair Orders, reference shape **Service Vehicle**); WS-271 issue detail (old-part section); WS-277 RGP pending tab; Item modal (warehouse-base) |
| **Migrations** | next free at build — warehouse-base `V5014xx` (HEAD `V501405`), warehouse `V5119xx` (HEAD `V511961`), warehouse-india `V5412xx` (HEAD `V541276`). The S1 reservations `V501377` / `V511845` are **void** (`V501377` is taken by the invoice-price-variance seed) |
| **Mobile** | `none` — warehouse has no mobile work (user rule; `DECISIONS.md` D-20 item 5) |
| **Contract version** | `v0 — 2026-11-16` |

### Acceptance checks (`#737`)

| # | Expects | Delivered by |
|---|---|---|
| A1 | Issuing a repairable spare without an old-part return is refused or warned (setting) | `RPR-GRD-03`, `RPR-T1-01`…`-03` |
| A2 | An old part sent on RGP shows in "at repairer" ageing | `RPR-T1-05`, `RPR-T5-03` |
| A3 | The repaired receipt is valued as old value + repair cost and is allocatable as refurbished | `RPR-T1-06`, `RPR-T4-04` |

### Why three items, not a variant axis or a stock status (decision record)

- **Valuation needs its own pool.** The grain has no condition (`WhbCostingEngine.java:207`) and is CHECK-locked
  (`V500021:194`, `IRR-40`). A defective or refurbished unit kept under the new item's id would blend into the
  new-part average. SAP solves this with split valuation (valuation types New / Refurbished / Defective, separate
  valuation records under one material). The equivalent here, without touching the grain, is a separate item id.
- **Not a variant axis.** The S1 ruling chose a seeded CONDITION variant axis. `DECISIONS.md` D-18 item 2
  (amended 2026-11-11, user) keeps the style / variant schema but says **nothing more is built on it**. So the three
  items are ordinary item-master rows linked by two columns on the new item. This is also how Tally users do it
  (separate stock items for the repaired / defective part).
- **Not a new stock status.** `whb_stock_statuses` is a registry, and condition is kept apart from status
  (`V500005:146`). A defective twin lands in the existing non-allocatable `DAMAGED`; a refurbished twin lands
  `AVAILABLE`, so it can be allocated and issued like any item.

---

## 1. T1 — State machine

### 1.1 Status inventory

| Entity | Status | Represented by | Reachable via | Exits via | Kind |
|---|---|---|---|---|---|
| Store issue line (repairable) | old part `NOT_REQUIRED` · `PENDING` · `BOOKED` | derived: policy frozen on the issue at post (`old_part_policy`) and Σ `wh_store_issue_old_parts.base_quantity` vs the line's base quantity | `RPR-T1-01`, `-02` | `RPR-T1-03` | attribute of a `POSTED` issue |
| Repair order | `DRAFT` | `status` | `RPR-T1-04` | `-05`, `-09` | initial |
| Repair order | `DISPATCHED` | `status`; `dispatch_movement_id`, `dispatched_by/at` | `RPR-T1-05` | `-06`, `-08` | active |
| Repair order | `PARTIALLY_RECEIVED` | `status` | `RPR-T1-06` (some quantity still at the repairer) | `-06`, `-08` | active |
| Repair order | `RECEIVED` | `status` | `RPR-T1-06` (nothing left at the repairer) | none | **terminal** |
| Repair order | `CLOSED` | `status`; reason, `closed_by/at` | `RPR-T1-08` | none | **terminal** |
| Repair order | `CANCELLED` | `status`; reason | `RPR-T1-09` | none | **terminal** |
| Receipt line | outcome `REPAIRED` · `NOT_REPAIRED` | `wh_repair_order_receipt_lines.outcome` (CHECK) | `RPR-T1-06` | — | attribute |

### 1.2 Transitions

| ID | From | Event | To | Guard | Actor | Side effects | Reason? | UI |
|---|---|---|---|---|---|---|---|---|
| RPR-T1-01 | issue `DRAFT` | **Post** a store issue (any kind) with a repairable line, old part captured on the line (defective twin, base quantity, serials when serialised, location, assessed value — default 0) | issue `POSTED`, line old part `BOOKED` | `SIR-T1-03` guards, then `RPR-GRD-01`…`-04` under the same issue lock | `wh_store_issues:post` | `SIR-T4-01` unchanged, plus `RPR-T4-01` in the same transaction | no | WS-271 **Post** modal — old-part section per repairable line |
| RPR-T1-02 | issue `DRAFT` | Post with the old part short or absent while the frozen policy is `WARN` | issue `POSTED`, line `PENDING` | `RPR-GRD-03` (`WARN`): the modal shows the warning and the user confirms (`oldPartShortAcknowledged = true`), else `409 REPAIRABLE_OLD_PART_CONFIRM_REQUIRED` | `:post` | issue posts; nothing else | no | WS-271 Post modal (warning + confirm) |
| RPR-T1-03 | issue `POSTED`, line `PENDING` | **Book old part** later | line `PENDING` or `BOOKED` | `RPR-GRD-01`, `-02`, `-04`; Σ booked ≤ issued base | `wh_store_issues:post` | `RPR-T4-01` | no | WS-271 lines tab row action **Book old part** (only while `PENDING`) |
| RPR-T1-04 | — | Create repair order: site, repairer (counterparty), custody location, expected return date, lines (defective twin, quantity, serials, source location) | `DRAFT` | `RPR-GRD-05`, `-06` | `wh_repair_orders:create` | gapless `RPO` number | no | Repair Orders **Add**; WS-271 old-part row **Send for repair** (prefills) |
| RPR-T1-04a | `DRAFT` | Edit | `DRAFT` | same | `:edit` | — | no | **Edit** |
| RPR-T1-05 | `DRAFT` | **Dispatch** | `DISPATCHED` | `RPR-GRD-05`, `-06` re-checked under lock; free `DAMAGED` stock of the defective twin at each source location | `wh_repair_orders:dispatch` | `RPR-T4-02`; the order becomes a gate-pass source (`RPR-T4-03`) and, with warehouse-india installed, a `REPAIR` challan source | no | **Dispatch** |
| RPR-T1-06 | `DISPATCHED` · `PARTIALLY_RECEIVED` | **Receive** per line: quantity, serials, outcome, repair charge (≥ 0, base currency), receiving location | `PARTIALLY_RECEIVED` / `RECEIVED` | `RPR-GRD-07`…`-09` under lock | `wh_repair_orders:receive` | `RPR-T4-04`; one movement per receipt; idempotent on the receipt id | charge 0 on `REPAIRED` needs a note (warranty repair) | **Receive** modal |
| RPR-T1-07 | — | Gate return of the RGP | (no repair-order change) | existing `GTE` rules | gate staff | records quantity returned at the gate only; posts no stock (`STO-D4`) | — | WS-263 (unchanged) |
| RPR-T1-08 | `DISPATCHED` · `PARTIALLY_RECEIVED` | **Close short** (lost, or scrapped at the repairer) | `CLOSED` | `RPR-GRD-10` | `wh_repair_orders:close` | none of its own — the remaining custody stock was already removed through the existing approved `SCRAP` route | **yes** | **Close** |
| RPR-T1-09 | `DRAFT` | Cancel | `CANCELLED` | — | `:cancel` | number stays issued | **yes** (the shared cancel reason, `warehouse.approval.document_cancel_reason_required`) | **Cancel** |

### 1.3 Guards

| ID | Predicate | Refusal | Backstop | Source |
|---|---|---|---|---|
| RPR-GRD-01 | the old part is the line item's **defective twin**: the issued item `N` has `is_repairable`, or is some `N`'s refurbished twin; the old part's item = that `N.repair_defective_item_id`; same owner and site as the issue | `422 REPAIRABLE_OLD_PART_ITEM_INVALID` · `lines[i].oldPart.itemId` | FK | `#737` G2 |
| RPR-GRD-02 | serialised defective twin: one serial per base unit, not a serial issued on this line (the new unit's serial is never the old one), not already on hand | `422 REPAIRABLE_OLD_PART_SERIALS_INVALID` · `lines[i].oldPart.serialIds` | `uk(owner, item, serial)` | `#737` G2 |
| RPR-GRD-03 | frozen policy `REQUIRE`: Σ old-part base = the line's issued base for every repairable line. `WARN`: short is allowed after the confirm. `OFF`: no check, the old-part section stays available | `422 REPAIRABLE_OLD_PART_REQUIRED` · `lines[i].oldPart.quantity` (names the base still owed) | — | `#737` A1 |
| RPR-GRD-04 | Σ old-part base on the line ≤ the line's issued base; assessed value ≥ 0; the location is a stock-holding, non-virtual location of the issue's site. A booking is keyed on the issue line and the posting attempt, so a retry never books twice | `422 REPAIRABLE_OLD_PART_EXCEEDS_ISSUED` · `422 REPAIRABLE_OLD_PART_VALUE_INVALID` · `422 REPAIRABLE_OLD_PART_LOCATION_INVALID` | CHECK `base_quantity > 0`, `assessed_value >= 0` | `#737` G2 |
| RPR-GRD-05 | each repair-order line's item is a defective twin; quantity > 0; serials when serialised; source is a stock-holding location of the site; status `DAMAGED` | `422 REPAIR_ORDER_ITEM_NOT_DEFECTIVE` · `422 REPAIR_ORDER_STOCK_INSUFFICIENT` (at dispatch) | ledger | `#737` G3 |
| RPR-GRD-06 | the custody location is a `whb_locations` row of type `JOB_WORKER` at the order's site whose `custodian_counterparty_id` is the repairer (or null); expected return date ≥ the site's today | `422 REPAIR_ORDER_CUSTODY_LOCATION_INVALID` · `422 REPAIR_ORDER_EXPECTED_RETURN_INVALID` | FK | `#737` G3, `#22 G3` |
| RPR-GRD-07 | receive quantity ≤ dispatched − received on the line; serials ⊆ the dispatched ones not yet received | `422 REPAIR_RECEIPT_EXCEEDS_OUTSTANDING` · `lines[i].quantity` | CHECK `received_quantity <= quantity` | `#737` G3 |
| RPR-GRD-08 | when an RGP was raised from the order, cumulative received on a line ≤ the RGP line's returned quantity (gate first, stores second) | `409 REPAIR_RECEIPT_AHEAD_OF_GATE` (names the gate pass) | — | Indian gate practice; `GTE` |
| RPR-GRD-09 | repair charge ≥ 0 with at most 2 dp; a `NOT_REPAIRED` line carries charge 0 (an inspection fee for an unrepaired part is the repairer's bill to accounting, not stock value) | `422 REPAIR_CHARGE_INVALID` · `lines[i].repairCharge` | CHECK `repair_charge >= 0` | Ind AS 2 para 10 |
| RPR-GRD-10 | close short only when the order's lines hold no stock at the custody location any more (the remaining units left through the approved `SCRAP` route) | `409 REPAIR_ORDER_STOCK_AT_REPAIRER` (names the quantity) | — | no automatic write-off |
| RPR-GRD-11 | the repairable family is consistent on the item master: `N.is_repairable` needs both twins; each twin is a different, active, stock-holding item with the same base UoM, owner and serial / lot control as `N`; an item is in at most one family; a twin can't itself be repairable | `422 ITEM_REPAIR_TWIN_INVALID` · `repairDefectiveItemId` / `repairRefurbishedItemId` | unique indexes on both twin columns | `#737` G1 |

### 1.4 Unreachable

| ID | Must never happen |
|---|---|
| RPR-UNR-01 | a defective twin allocated, picked or issued (it lands `DAMAGED`; the issue guard `SIR-GRD-04` reads `AVAILABLE` only) |
| RPR-UNR-02 | a gate pass or gate return posting stock (`STO-D4` stands; the stock moves on the repair order) |
| RPR-UNR-03 | a change to the valuation grain or a condition column on cost layers (`IRR-40`) |
| RPR-UNR-04 | a new style / variant axis for condition (D-18 item 2) |
| RPR-UNR-05 | a repair charge capitalised twice (one movement per receipt, idempotency key `REPAIR_RECEIPT:<receipt id>`) |
| RPR-UNR-06 | an automatic scrap of a part that was not repaired |

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from | Extra | Source |
|---|---|---|---|---|---|
| RPR-T2-01 | Capture / book old part | `wh_store_issues:post` | issue `DRAFT` (at post) / `POSTED` with line `PENDING` | site and department scope of the issue | — |
| RPR-T2-02 | Create / edit repair order | `wh_repair_orders:create` / `:edit` | — / `DRAFT` | site scope | — |
| RPR-T2-03 | Dispatch | `:dispatch` | `DRAFT` | stores in-charge | — |
| RPR-T2-04 | Receive | `:receive` | `DISPATCHED`, `PARTIALLY_RECEIVED` | gate staff hold no `wh_repair_orders` verb; the gate-pass source read is site-scoped and shows no cost (as `WhStoreIssueGatePassSource`) | `#737` G3 |
| RPR-T2-05 | Close short / cancel | `:close` / `:cancel` | `DISPATCHED`·`PARTIALLY_RECEIVED` / `DRAFT` | reason | — |
| RPR-T2-06 | View / export | `:view` (+ `:view:all` / `:view:branch`), `:export` or `ADMIN` | any | carrying value and repair charge need `warehouse:cost:view` (nulled and dropped from sort and export otherwise) | — |
| RPR-T2-07 | Mark an item repairable, name its twins | `whb_items:edit` | — | `RPR-GRD-11` | — |
| RPR-T2-08 | Change `warehouse.stores.repairable_old_part_return` | `admin_settings:edit` + `whb_settings:edit` | — | audited; frozen on each issue at post | DECISION RULE §4 |

Seeded grants: the bundles that hold `wh_store_issues:post` get `wh_repair_orders:view/create/edit/dispatch/receive/export`; `:close` and `:cancel` go to the stores-manager bundles that hold `wh_store_returns:post`.

## 3. T3 — Time-driven rules

| ID | Rule | Trigger | Changes | Notified | Job | Once? |
|---|---|---|---|---|---|---|
| RPR-T3-01 | Days at repairer | read time: site today − the order's `dispatched_at` (site date) | nothing — a computed column and ageing bucket | — | none (computed on read) | — |
| RPR-T3-02 | Repair overdue | the RGP's expected return date passed | nothing | as `GTE-T3-01` | the existing `WhGatePassOverdueScheduler` — no second scheduler | as `GTE-T3-01` |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in | Source |
|---|---|---|---|---|
| RPR-T4-01 | old part booked (`RPR-T1-01`, `-03`) | one `ISSUE_RETURN` movement (existing type; `sourceDocumentType = STORE_ISSUE_OLD_PART`, reason `REPAIRABLE_OLD_PART` in context `STORE_RETURN`, idempotency key `STORE_ISSUE_OLD_PART:<old-part row id>`): −qty of the **defective twin** at the issue line's `counter_location_purpose` location, +qty at the chosen location, status **`DAMAGED`**, cost basis `ACTUAL`, value = the assessed value (default 0). The new item's consumption is not re-priced | issue service → writer | SAP split valuation; `SIR-T4-03` leg |
| RPR-T4-02 | dispatch | one movement (the move type `#22` uses for a job-work dispatch to a `JOB_WORKER` premises — reuse, no new type): −qty of the defective twin at each source location, +qty at the custody location. The value moves into the `#22 G3` custody pool at the twin's ledger cost; the owner is unchanged (`L-11`) | repair order service → writer | `#22 G3`, `#718 G2` |
| RPR-T4-03 | dispatch | the order is offered as a gate-pass source (`WhRepairOrderGatePassSource implements GatePassSourceResolver`, kind `RETURNABLE`, purpose `REPAIR`, party = repairer, expected return = the order's) and, with warehouse-india installed, as a delivery-challan source with purpose `REPAIR` (existing `WHIN_CHALLAN_PURPOSE` value, `V540020:100`) | gate source resolver; challan source (warehouse-india) | `#140`, `#723` pattern (`V541175`) |
| RPR-T4-04 | receive | one movement of the new base type **`REPAIR_RECEIPT`** (direction conversion, `cost_basis_default = ACTUAL`, `requires_reason = false`, no reversal type — a wrong receipt is corrected by an adjustment, as `ISSUE_RETURN` is): −qty of the defective twin at the custody location, valued by the engine from the custody pool (`C`); +qty at the receiving location of the **refurbished twin** (`REPAIRED`, status `AVAILABLE`, value stated as `extendedCost = C + repair charge`) or of the **defective twin** (`NOT_REPAIRED`, status `DAMAGED`, value `C`). Serials carry across unchanged. Under `STANDARD` on the refurbished twin the difference goes to `PURCHASE_PRICE_VARIANCE` as `CVL-T4-03` | repair order service → writer | `SUB-T4-07` stated `extendedCost`; Ind AS 2 para 10 |
| RPR-T4-05 | every movement above | the existing per-movement handover (`AHO-T1-01`); the `REPAIR_RECEIPT` line payload carries `repairCharge` and `repairerCounterpartyId` as additive fields (as `#722` added lot fields to `WhbAccountingDocumentPayloads`). `STANDALONE`: emitted and parked, as every movement | `WhbAccountingHandoverEmitter`; payload builder | `accounting-handover` |
| RPR-T4-06 | receive / close | order line `received_quantity` += ; order status by remaining quantity; audit log | repair order service, same transaction | — |

## 5. T5 — Screen contract

### 5.1 Repair Orders (new; reference **Service Vehicle**)

| | |
|---|---|
| **Grid** | `wh_repair_orders` · scope `WAREHOUSE_REPAIR_ORDER` · sort `e.created_at DESC` |
| **Tiles** (5) | `DRAFT` · at repairer (`DISPATCHED` + `PARTIALLY_RECEIVED`) · overdue · received this month · value at repairer (cost:view) — filter-aware, no cache name (`FR-395`) |
| **Columns** | `orderNumber`, `warehouseName`, `repairerName`, `custodyLocationCode`, `lineCount`, `itemSummary` (one item or *Mixed*), `quantityAtRepairer`, `dispatchedAt`, `daysAtRepairer`, `expectedReturnDate`, `isOverdue`, `valueAtRepairer` (cost:view), `repairChargeTotal` (cost:view), `status`, `gatePassNumber`, `challanNumber`, audit |
| **Filters** | `warehouseId`; `repairerId` (typeahead); `status`; `itemId`; `overdueOnly`; `dispatchedFrom/To` (`dateOnly`) — every field in `COMMON_FILTER_CONFIGS.WAREHOUSE_REPAIR_ORDER` and forwarded by the API service |
| **Row actions** | View · Edit (`DRAFT`) · Dispatch (`DRAFT`) · Receive (`DISPATCHED`/`PARTIALLY_RECEIVED`) · Close (same) · Cancel (`DRAFT`), each gated by its T2 verb and the response's `can*` flag |
| **Detail / View popup** | header; lines (item, serials, quantity, received, at repairer, value); receipts tab (outcome, quantity, charge, refurbished value, movement) |
| **Export** | grid superset + lines sheet + `createdByName`, `updatedByName`; value columns dropped without cost:view |

### 5.2 Store issue (WS-270 / WS-271) — amended

Post modal: an **Old part** section per repairable line (defective twin preset and read-only, quantity defaulted to
the issued quantity, serial picker, location, assessed value default 0) and the `WARN` confirm. Lines tab: `oldPartStatus`
(`NOT_REQUIRED`/`PENDING`/`BOOKED`) and booked quantity; row actions **Book old part** (`PENDING`) and **Send for repair**
(`BOOKED`, prefills a repair order). WS-270 gets the tile *Old parts pending* (lines `PENDING`) and filter
`oldPartPending` in `COMMON_FILTER_CONFIGS.WAREHOUSE_STORE_ISSUE`. Grid and export carry `oldPartStatus`.

### 5.3 WS-277 RGP pending tab — amended (`SIR-T5-03`)

| ID | Rule | Proved by |
|---|---|---|
| RPR-T5-03 | Add `dispatchedAt` (gate-out time, site date), `daysOut`, `ageingBucket` (0–30 · 31–60 · 61–90 · >90 days), `repairOrderNumber`, `serialNumbers`, `carryingValue` (cost:view; the custody value of the open quantity) — a pass not yet due still ages; a partial return reduces the open quantity and the value. New filter `ageingBucket`. Export columns ⊇ grid | grid and export agree for the same filters; `purpose = REPAIR` filter (existing) lists exactly the repair RGPs |

### 5.4 Item master (warehouse-base) — amended

Item modal: `isRepairable` toggle and, when on, two item pickers `repairDefectiveItemId`, `repairRefurbishedItemId`
(`RPR-GRD-11`). View popup shows them. Grid column + filter `isRepairable` (`COMMON_FILTER_CONFIGS` item scope) +
export columns for the flag and both twin codes. Item import gains the three columns.

### 5.5 Settings

`warehouse.stores.repairable_old_part_return` on the Warehouse tab (`AdminSettingsWarehouseTab`), Stores section.

| Key | Type | Default | Allowed | Stored with |
|---|---|---|---|---|
| `warehouse.stores.repairable_old_part_return` | SELECT | `REQUIRE` | `REQUIRE` · `WARN` · `OFF` | group `stores`, displayOrder after `warehouse.stores.issue_attachment_window_hours`; frozen on the issue at post (`old_part_policy`); a change never re-judges a posted issue |

Upgrade-safe: no item is repairable until a user flags it, so the `REQUIRE` default changes nothing on upgrade (`D-21` item 7).

## 6. Out of scope — accounting side (waits for accounting; not a warehouse blocker)

| Item | Owner | Note |
|---|---|---|
| GL for `REPAIR_RECEIPT`: Dr inventory (refurbished) / Cr inventory (defective, custody) for `C`; Dr inventory / Cr **repair charges clearing** for the charge | accounting receiver of the handover | the warehouse sends the value split (`RPR-T4-05`) |
| Booking the repairer's bill against the clearing account, the difference to repairs expense / variance | accounting (AP) | the clearing account plays the GRNI role |
| GST on the repair service (SAC 9987, generally 18%), input credit under s.16 / s.17(5) | accounting (tax engine) | warehouse sends no tax figure |
| TDS on a repair contract (contract-payment provision of the Income-tax Act 2025; formerly s.194C — **UNVERIFIED** section number) | accounting | — |
| Lower of cost and NRV for refurbished stock (Ind AS 2 para 9) | accounting period close | not a warehouse posting |
| Old-part assessed value: Dr inventory (defective) / Cr consumption | accounting receiver | 0 by default, so usually nothing |
| Major spares that meet the PPE test (Ind AS 16 para 8) | assets | out of warehouse scope |

Also out: mobile; automatic scrapping; reversal of a `REPAIR_RECEIPT`; a repair PO in warehouse-trade (the charge is entered at receipt).

## 7. Amendments

| Date | Change |
|---|---|
| 2026-11-16 | v0 derived (R49 RA1, DECISION MODE, Claude + GPT). **Supersedes the S1 driver ruling of 2026-11-07** on one point: condition is carried by three linked item-master rows (`is_repairable` + two twin columns), not a seeded CONDITION variant axis, because `DECISIONS.md` D-18 item 2 (amended 2026-11-11) builds nothing more on the style / variant schema. Kept from S1: assessed value default 0, `REQUIRE` default, repair dispatch reuses the `REPAIR` challan, no grain change. Repairer custody reuses the `JOB_WORKER` location type and the `#22 G3` custody pool (no new location type, no costing-engine change). Old part posts as `ISSUE_RETURN` (existing type) at `DAMAGED`; no new stock status. One new movement type `REPAIR_RECEIPT`. Setting key in the `warehouse.stores.*` form: `warehouse.stores.repairable_old_part_return` (the issue's `WAREHOUSE_REPAIRABLE_OLD_PART_RETURN` label) |

## 8. Invariants and scenarios

`L-1`, `L-11`, `IRR-40`, `STO-D4`; catalogue row 39.

## 9. Open rows

| ID | Question | Default |
|---|---|---|
| RPR-OPEN-01 | Is goods-sent-for-repair "job work" under CGST s.2(68) / s.143 (ITC-04), or a Rule 55 movement "other than by way of supply"? The R3 audit lists reboring and battery refurbishment as job work (`R3-erp-midmarket-audit.md:1094-1102`); common practice sends repairs on a returnable delivery challan | **v1 default: Rule 55 `REPAIR` challan, no ITC-04** — **UNVERIFIED**, confirm against the law in force at build. A plant that treats a repair as job work uses the existing `#22` job-work flow for that dispatch |
| RPR-OPEN-02 | Which existing movement type `#22` posts for a job-work dispatch to a `JOB_WORKER` premises | reuse it as-is for `RPR-T4-02`; confirm the code at build |
