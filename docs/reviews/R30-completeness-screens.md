# R30 — Completeness audit, part SC (screens)

*2026-10-23 · read-only · inputs: `DECISIONS.md` D-16, `reviews/R28` §8b, `BUILD-SPEC-SCREENS.md`,
`frd/FRD-{REM,STORES,TRADE,MFG}.md`, `contracts/*.contract.md` §5, `issues/p7-*…p10-*`; code:
`classic/{warehouse-base,warehouse,warehouse-3pl,warehouse-india}/frontend` (228 `page.tsx`) and the
menu INSERTs of their migration folders (134 files, 245 menu rows parsed).*

## 0. Reading notes

- **`WH-SC-` ids are scenarios, not screens.** Screens are `WS-nnn` (`BUILD-SPEC-SCREENS.md` §0.10). The
  re-target screens are `WS-260…WS-339`; `WH-SC-420…679` are the scenarios. This report builds the matrix
  on `WS` ids and checks the scenarios in §3.
- **Menu rows** are the first `INSERT INTO menus` that carries the route (`V<version>:<line>`). Where a
  later migration re-parents a leaf (`V511248`, `V501101`, `V511250`), the INSERT line is still the one
  cited. No live database holds the warehouse menus (local `platform-postgres` has 0 warehouse rows), so
  the counts in CP-SC-001 come from `FRD-REM.md:75`, checked against the migrations.
- **D-16 status:** *keep* · *keep, trim* (a retail field leaves a kept page) · *re-home* (menu move, same
  route) · *rename* · *remove* · *new*.

## 1. Summary

| Measure | Count |
|---|---|
| Existing pages (base 75 · app 108 · 3pl 18 · india 27) | **228** |
| — keep / keep-trim / re-home / rename / remove | 200 / 5 / 4 / 1 / 18 |
| — with a `WS` id | 219 (8 have none or a drifted route, CP-SC-007; the public track page has none by design) |
| — removal pages that P7 carries (`FRD-REM.md` A.3, `p7-02…p7-12`) | 18 of 18 |
| Dealer/retail pages in code **not** in P7 | **0** (a keyword scan of all 228 pages finds only removal pages, the parts-KPI rename and generic uses of *AWB* that `REM-D12` keeps) |
| New screens `WS-260…337` (STORES 18 · TRADE 34 · MFG 18) | **70** (+2 reserved) |
| — with a carrier task | 70 / 70 |
| — with a contract §5 entry | 69 / 70 (WS-312 has none, CP-SC-005) |
| Scenarios `WH-SC-420…679` defined / closed by a task | 257 / 257 (597–599 unused) |
| Menu-cap breaches planned | **1 L1** (`warehouse_operations`, CP-SC-001) |

Client-flow screens (all have a spec): PR WS-286 · RFQ/quotation WS-288/289/290 · PO fixed/open/blanket
+ schedule WS-292/294 + core WS-072/275 · gate entry (party, PO, bill no/date) WS-260 · GRN short/excess
WS-076/077 (debit/credit note **deferred by D-16 §6**: claim / reconciliation case only, `FRD-STORES.md`
§8) · QC sampling bands WS-264/265 · QC reject → supplier return WS-080/084 (debit note deferred) · MRN
WS-266 · material requisition WS-268 · store issue WS-270 · store return WS-272 · BOM WS-320 · production
order WS-323 · staging WS-325 · production receipt WS-326 · subcontracting WS-330 · MRP WS-333/334/335.
**No client-flow screen is missing a spec.**

## 2. Findings

### CP-SC-001 · P8 stores menus breach the 10-section cap on `warehouse_operations` — **high**
- **Evidence.** `FRD-REM.md:75` (`REM-D15`): *"Warehouse Operations already has 10 L2s"*, Outbound has
  8 leaves and Packing & VAS has 8. Code agrees: ten L2s parented to `warehouse_operations` (inbound,
  inventory, outbound, printing, packing_and_vas, analytics, putaway_replenishment, returns, costing,
  stock_reports — `V510010:250`, `V510032:398`, `V510040:583`, `V510060:562`, `V510101:325`,
  `V511211:234`, `V511248:72-81`).
  `issues/p8-14.md:11-22` adds three new L2s (*Gate*, *Stores*, *Quality*): 13 sections. It also sends
  WS-276 to *Outbound*, which is full, so a fourth section is needed. Its fallback (*"Gate merges into
  Stores only if Stores stays ≤ 8"*) cannot apply: 7 + 2 = 9. *"Otherwise split per the regroup rule"*
  adds sections, it does not remove them.
- **Proposed carrier.** Amend `p8-14`. Give the stores screens their own L1, the same way trade
  (`TRD-07`) and manufacturing (`V561000`) do. For example, L1 `warehouse_stores` (*Stores & Gate*) with
  L2 *Gate* (2), *Stores* (7) and *Quality* (4, re-parenting WS-079/080 out of Putaway & Replenishment).
  WS-275 and WS-276 go into a *Schedules* L2 there. Record the decision in `FRD-STORES.md` §7.

### CP-SC-002 · Menu name `warehouse_trade` is removed by P7, then created again by P9 — **medium**
- **Evidence.** P7 deletes L1 `warehouse_trade` (the Trade Portal; `FRD-REM.md:109` FR-491, `:490`,
  `:605`). `WH-SC-662` (`FRD-REM.md:129`) and `p7-08.md:59` assert *"no menu `warehouse_trade`"*. P9
  then inserts L1 `warehouse_trade` (*Purchase & Sales*) (`p9-01.md:80`, `FRD-TRADE.md:308,571`). The
  P7 exit check fails on any install that has trade enabled. The reused key also brings back any
  favourites, visit history or role grants that were stored against the old portal key.
- **Proposed carrier.** Change `p9-01` to a new key, e.g. `warehouse_purchase_sales`, and update
  `FRD-TRADE` `TRD-07`. Otherwise, scope `WH-SC-662` / `p7-08` to Mode A and say why in `FRD-REM` §5.

### CP-SC-003 · STORES has no module-wide grid-configuration rule; per-screen defaults are unstated — **medium**
- **Evidence.** TRADE requires `grid_column_definitions` + `filter_definitions` + `grid_preferences` with
  **both** default arrays (`FRD-TRADE.md:258`, FR-616). MFG has the same rule (`FRD-MFG.md:421`, FR-669).
  `FRD-STORES.md` has no such FR (no hit for `grid_preferences` / `default_columns`), and no STORES
  contract §5 names default filters or default columns. Of the P8 tasks, `p8-04`, `p8-06`, `p8-07`,
  `p8-11` and `p8-15` say nothing about `grid_preferences`. `p8-09` (WS-273, WS-274) says only
  *"Grids/filters/exports"* (`p8-09.md:69`). Several of these tasks change existing grids (GRN,
  quality inspections, supplier returns), so new columns may not reach `default_columns`.
- **Proposed carrier.** Add a STORES FR mirroring FR-616/FR-669 (a free id in `FR-500…539`), cite it in
  every P8 screen task, and add default filters/columns lines to each STORES contract §5.

### CP-SC-004 · `BUILD-SPEC-SCREENS.md` index is stale for six removed screens and one rename; no P7 task owns the fix — **medium**
- **Evidence.** These are removed by P7 but not marked **REMOVED (`D-16`)**: WS-066 (`:637`), WS-067
  (`:638`), WS-222 (`:793`), WS-225 (`:796`), WS-240 (`:811`), WS-242 (`:813`). The same rows in the
  grid blocks are unmarked too (`:1863`, `:1864`, `:3199`, `:3202`). WS-217 is still *Parts KPIs* at
  `/reports/parts-kpis` (`:788`, `:3194`), although `p7-11` renames it to Stock KPIs `/reports/stock-kpis`.
  No P7 file mentions `BUILD-SPEC`.
- **Proposed carrier.** A design-set edit under `p7-13` (the REM close-out), or a one-line addition to
  `09-EPIC-p7.md`'s exit list: mark the six rows, rename WS-217, and add its `obsolescencePct` column to
  the P7 trim list if it is dealer-only.

### CP-SC-005 · WS-312 Trade Reports has no screen contract — **low**
- **Evidence.** No `contracts/*.md` mentions WS-312. The eight report grids are specified only in
  `p9-14.md` (Reports table: `wht_rpt_*`, columns and filters). That table has no actions, no tiles and
  no default filters/columns, and no export rule beyond FR-616.
- **Proposed carrier.** `p9-14`. Either add a §5 entry to `trade-purchase-order.contract.md` and
  `trade-sales-order.contract.md`, or write a short `trade-reports` contract. Copy `grid_preferences`
  from the `p9-14` table.

### CP-SC-006 · WS-276 Customer Delivery Schedule contract is columns-only — **low**
- **Evidence.** `po-schedule-port.contract.md:158-160` (§5.3) says *"Same shape"* and lists columns. It
  gives no grid id, filter scope, filters, export or actions. The grid id `wh_demand_order_schedule_lines`
  appears only in `p8-02.md:20`, and the scope `WAREHOUSE_DEMAND_SCHEDULE` only in `p8-14`. Other thin
  STORES §5 entries: WS-274 (no export or scope), WS-273 (no actions or export, though the Department
  reference implies them), WS-264 (no row actions).
- **Proposed carrier.** `p8-02` / contract edit: state the WS-276 grid id, scope, filters
  (`customerId`, `itemId`, `kind`, `status`, `requestedFrom/To`, `insideHorizonOnly`), export and
  actions, mirroring WS-275 §5.2.

### CP-SC-007 · Eight existing pages have no spec id or a drifted route — **low**
- **Evidence (code route vs spec).** `vas/work-orders` vs WS-144 `/execution/work-orders`;
  `vas/service-types` vs WS-145 `/execution/vas-service-types`; `execution/exception-console` vs WS-153
  `/execution/exceptions`; `reports/stock-valuation` vs WS-211 `/reports/valuation`;
  `reports/stock-ageing` vs WS-212 `/reports/ageing`; `india/delivery-challans` vs WS-178
  `/india/challans`. Two pages have no id at all: `india/bonded-losses` (menu `V541156:258`) and
  `outbound/fulfilment-policies` (menu `V511263:134`).
  Separately, `BUILD-SPEC` §0.8 does not cover `/warehouse/vas/*` (used by `warehouse`), and
  `warehouse-base` ships `/execution/tasks`, inside `warehouse`'s `/execution/*` root.
- **Proposed carrier.** Design-set edit (no code): re-point WS-144/145/153/178/211/212 to the built
  routes, register two ids for bonded losses and fulfilment policies (`BUILD-SPEC` §1 free ids), and add
  `/warehouse/vas/*` to §0.8.

### CP-SC-008 · Route-ownership table (§0.8) omits the P8–P10 roots and still lists removed adapters — **low**
- **Evidence.** `BUILD-SPEC-SCREENS.md:194-213` lists no `/warehouse/gate/*`, `/warehouse/stores/*` or
  `/warehouse/quality/*` (core, P8), no `/warehouse/trade/*` (trade) and no `/warehouse/manufacturing/*`
  (MFG). It still lists `warehouse-adapter-dealer` and `-services`. Frontends merge last-write-wins (§0.8),
  so an unregistered root has no collision guard.
- **Proposed carrier.** Design-set edit with `p8-14` / `p9-01` / `p10-01` acceptance lines: add the five
  roots and strike the two removed adapters (D-16).

### Checked, no finding
- **Spec screens without a task:** none. Every WS-260…337 maps to a `p8`/`p9`/`p10` task (matrix B).
- **TRADE and MFG menu depth:** trade has 6 L2 under its own L1, with 8/5/6/5/7/8 leaves
  (`FRD-TRADE.md` §6). MFG has 3 L2 with 8/6/3 leaves (`FRD-MFG.md:450-453`, `p10-01.md:99-104`). Both
  are within the caps. The P7 re-home creates one L1 `warehouse_shipping` with one L2 of 4 leaves
  (`REM-D15`), also within the caps.
- **Pre-D-16 spec screens with no page (out of this program's scope, noted only):** WS-154, WS-171,
  WS-192, WS-228, WS-241, WS-243 are later phases (v2/v3). WS-144/145/153/178/211/212 are the route
  drifts in CP-SC-007.
- **Supersessions** stay as-is by `FR-496` (`FRD-REM.md:114`). D-16 §3's *"stay as engineering change"*
  is read as a description, not a relabel. If a relabel was meant, it is missing from `p7-11`.

## 3. Scenarios `WH-SC-420…679`

| Range | FRD | Defined | Closed by a task (`## Scenarios closed`, ranges expanded) |
|---|---|---|---|
| 420–479 | FRD-STORES §9 | 60 | 60 (`p8-01…p8-16`) |
| 480–596 | FRD-TRADE §7 | 117 | 117 (`p9-01…p9-14`); 597–599 unused |
| 600–659 | FRD-MFG §12 | 60 | 60 (`p10-*`, `12-EPIC-p10.md:195`) |
| 660–679 | FRD-REM §5 | 20 | 20 (`p7-*`) |

Only 9 distinct `WS` ids are named inside the 257 scenario rows. Scenarios reach screens through FR → task
→ screen, not directly. That is traceable, but a screen-level walk (`/spec-preview`) cannot be driven
from the scenarios alone.

## 4. Matrix A — existing code pages (228)

Route relative to `/dashboard/warehouse/`. *Contract §5* is shown where a contract's screen section names
the id. Older screens are mostly specified in `BUILD-SPEC` §2–§5, not in a contract.

| # | screen | spec id | route | menu row (migration:line) | in code | D-16 | carrier | contract §5 | verdict |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Public tracking page | — | `(public)/track/[token]` | — | Y (app) | remove | p7-03 (+p7-12 FE) | — | OK — RN-014 removal; no WS id by design |
| 2 | exception-console | — | `execution/exception-console` | V511140:105 | Y (app) | keep | — | — | **no spec id** — route drift: spec WS-153 `/execution/exceptions` |
| 3 | Labour Tasks | WS-146 | `execution/labour-tasks` | V510214:288 | Y (app) | keep | — | — | OK |
| 4 | Replenishment Tasks | WS-142 | `execution/replenishment-tasks` | V511255:57 | Y (app) | keep | — | — | OK |
| 5 | Weighing Instruments | WS-129 | `execution/weighing-instruments` | V510213:490 | Y (app) | keep | — | — | OK |
| 6 | Weighing Records | WS-130 | `execution/weighing-records` | V510213:493 | Y (app) | keep | — | — | OK |
| 7 | Cut-over Checklists | WS-151 | `golive/cutover` | V510090:523 | Y (app) | keep | — | — | OK |
| 8 | Migration Mappings | WS-152 | `golive/mappings` | V511256:59 | Y (app) | keep | — | — | OK |
| 9 | Opening Stock Batches | WS-150 | `golive/opening-stock` | V510090:510 | Y (app) | keep | — | — | OK |
| 10 | ASNs | WS-074 | `inbound/asns` | V511250:95 | Y (app) | keep | — | — | OK |
| 11 | Cross-dock Plans | WS-087 | `inbound/cross-dock` | V511271:91 | Y (app) | keep, re-home menu → `warehouse_shipping_planning` | p7-06 | — | OK |
| 12 | Dock Appointments | WS-086 | `inbound/dock-appointments` | V511250:98 | Y (app) | keep | — | — | OK |
| 13 | Dock Doors | WS-085 | `inbound/dock-doors` | V510010:263 | Y (app) | keep | — | — | OK |
| 14 | Goods Receipts | WS-076 | `inbound/goods-receipts` | V510014:545 | Y (app) | keep | p8-04 (changed) | grn-bill-match§5:142 | OK |
| 15 | Goods Receipt Detail | WS-077 | `inbound/goods-receipts/[goodsReceiptId]` | — | Y (app) | keep | p8-04/p8-08 (changed) | grn-bill-match§5:142 | OK |
| 16 | Inspection Plans | WS-079 | `inbound/inspection-plans` | V510015:271 | Y (app) | keep | p8-05 (changed) | incoming-inspection-sampling§5:145 | OK |
| 17 | Marketplace Claims | WS-242 | `inbound/marketplace-claims` | V510215:293 | Y (app) | remove | p7-05 (+p7-12 FE) | — | BUILD-SPEC index not marked REMOVED (CP-SC-004) |
| 18 | Obsolescence Returns | WS-138 | `inbound/obsolescence-returns` | V510210:466 | Y (app) | remove | p7-07 (+p7-12 FE) | — | OK |
| 19 | Purchase Orders | WS-072 | `inbound/purchase-orders` | V510011:336 | Y (app) | keep | p8-01 (changed) | po-schedule-port§5:148 | OK |
| 20 | Purchase Order Detail | WS-073 | `inbound/purchase-orders/[purchaseOrderId]` | — | Y (app) | keep | p8-01 (changed) | po-schedule-port§5:148 | OK |
| 21 | Putaway Rules | WS-081 | `inbound/putaway-rules` | V510017:529 | Y (app) | keep | — | receipt-qc-putaway§5:348 | OK |
| 22 | Putaway Tasks | WS-082 | `inbound/putaway-tasks` | V510017:544 | Y (app) | keep | — | receipt-qc-putaway§5:348 | OK |
| 23 | Quality Inspections | WS-080 | `inbound/quality-inspections` | V510016:378 | Y (app) | keep | p8-05/06/07 (changed) | incoming-inspection-sampling§5:145 | OK |
| 24 | Receipt Reversals | WS-078 | `inbound/receipt-reversals` | V510018:305 | Y (app) | keep | — | receipt-qc-putaway§5:362 | OK |
| 25 | Receiving Sessions | WS-075 | `inbound/receiving-sessions` | V510013:308 | Y (app) | keep | p8-03 (changed) | receipt-qc-putaway§5:292 | OK |
| 26 | Inbound Reconciliation Cases | WS-083 | `inbound/reconciliation-cases` | V510019:318 | Y (app) | keep | — | — | OK |
| 27 | Return Gradings | WS-137 | `inbound/return-gradings` | V510210:461 | Y (app) | keep | — | — | OK |
| 28 | Return Receipts | WS-135 | `inbound/returns` | V510050:700 | Y (app) | keep | — | — | OK |
| 29 | RMAs | WS-136 | `inbound/rmas` | V510050:703 | Y (app) | keep | — | — | OK |
| 30 | Supplier Claims | WS-248 | `inbound/supplier-claims` | V510216:614 | Y (app) | keep | — | — | OK |
| 31 | Supplier Claim Detail | WS-249 | `inbound/supplier-claims/[claimId]` | — | Y (app) | keep | — | — | OK |
| 32 | Supplier Returns | WS-084 | `inbound/supplier-returns` | V510020:333 | Y (app) | keep | p8-07/p8-15 (changed) | — | OK |
| 33 | Three-way Matches | WS-088 | `inbound/three-way-match` | V511272:57 | Y (app) | keep | — | — | OK |
| 34 | Stock Adjustments | WS-089 | `inventory/adjustments` | V511201:130 | Y (app) | keep | — | — | OK |
| 35 | Blocked Movements Queue | WS-097 | `inventory/blocked-movements` | V511201:136 | Y (app) | keep | — | — | OK |
| 36 | Count Programs | WS-093 | `inventory/count-programs` | V511203:99 | Y (app) | keep | — | — | OK |
| 37 | Counts | WS-094 | `inventory/counts` | V511203:102 | Y (app) | keep | — | — | OK |
| 38 | Count Entry & Variance | WS-095 | `inventory/counts/[countId]` | — | Y (app) | keep | — | — | OK |
| 39 | Demand History | WS-143 | `inventory/demand-history` | V511207:104 | Y (app) | keep | — | — | OK |
| 40 | Hold Types | WS-091 | `inventory/hold-types` | V510032:411 | Y (app) | keep | — | — | OK |
| 41 | Holds | WS-092 | `inventory/holds` | V510032:424 | Y (app) | keep | — | — | OK |
| 42 | Insufficient Stock & Lost Sales | WS-096 | `inventory/insufficient-stock` | V511201:133 | Y (app) | keep | — | — | OK |
| 43 | Landed Cost Documents | WS-147 | `inventory/landed-costs` | V510080:459 | Y (app) | keep | — | — | OK |
| 44 | NRV Assessments | WS-149 | `inventory/nrv-assessments` | V510212:487 | Y (app) | keep | — | — | OK |
| 45 | Recalls | WS-139 | `inventory/recalls` | V511268:117 | Y (app) | keep | — | — | OK |
| 46 | Reconciliation Exceptions | WS-098 | `inventory/reconciliation-exceptions` | V510035:233 | Y (app) | keep | — | — | OK |
| 47 | Replenishment Runs | WS-140 | `inventory/replenishment-runs` | V511207:98 | Y (app) | keep | — | — | OK |
| 48 | Replenishment Suggestions | WS-141 | `inventory/replenishment-suggestions` | V511207:101 | Y (app) | keep | — | — | OK |
| 49 | Revaluations | WS-148 | `inventory/revaluations` | V510080:472 | Y (app) | keep | — | — | OK |
| 50 | Transfer Orders | WS-090 | `inventory/transfers` | V511202:151 | Y (app) | keep | — | — | OK |
| 51 | AWB Pools & Numbers | WS-119 | `outbound/awb-pools` | V511273:78 | Y (app) | remove | p7-02 (+p7-12 FE) | — | OK |
| 52 | Working Calendars | WS-127 | `outbound/calendars` | V511272:60 | Y (app) | keep, re-home menu → `warehouse_shipping_planning` | p7-06 | — | OK |
| 53 | Carrier Accounts | WS-109 | `outbound/carrier-accounts` | V510044:287 | Y (app) | keep | — | — | OK |
| 54 | Carrier Services | WS-108 | `outbound/carrier-services` | V510044:284 | Y (app) | keep, trim | p7-03 (drop supportsCod, OD-22) | — | OK |
| 55 | Carriers | WS-107 | `outbound/carriers` | V510044:281 | Y (app) | keep | — | — | OK |
| 56 | Cartons | WS-104 | `outbound/cartons` | V510042:403 | Y (app) | keep | — | — | OK |
| 57 | Channel Accounts | WS-123 | `outbound/channel-accounts` | V511271:82 | Y (app) | remove | p7-04 (+p7-12 FE) | — | OK |
| 58 | Channel Order Imports | WS-124 | `outbound/channel-imports` | V511271:85 | Y (app) | remove | p7-04 (+p7-12 FE) | — | OK |
| 59 | COD Remittances | WS-121 | `outbound/cod-remittances` | V511274:84 | Y (app) | remove | p7-03 (+p7-12 FE) | — | OK |
| 60 | Consignments | WS-113 | `outbound/consignments` | V511265:190 | Y (app) | keep | — | — | OK |
| 61 | fulfilment-policies | — | `outbound/fulfilment-policies` | V511263:134 | Y (app) | keep | — | — | **no spec id** — no spec id |
| 62 | Handovers | WS-111 | `outbound/handovers` | V511265:184 | Y (app) | keep | — | — | OK |
| 63 | Manifests | WS-110 | `outbound/manifests` | V511265:181 | Y (app) | keep | — | — | OK |
| 64 | NDR Console | WS-120 | `outbound/ndr` | V511274:81 | Y (app) | remove | p7-03 (+p7-12 FE) | — | OK |
| 65 | Order Edit Rules | WS-128 | `outbound/order-edit-rules` | V511261:102 | Y (app) | keep | — | — | OK |
| 66 | Demand Orders | WS-099 | `outbound/orders` | V510040:596 | Y (app) | keep, trim | p7-04 (drop payment_mode/cod_amount); p8-02 (changed) | — | OK |
| 67 | Demand Order Detail | WS-100 | `outbound/orders/[demandOrderId]` | — | Y (app) | keep, trim | p7-04 (drop payment_mode/cod_amount) | — | OK |
| 68 | Pack Sessions | WS-103 | `outbound/pack-sessions` | V510101:339 | Y (app) | keep | — | — | OK |
| 69 | Pick Tasks | WS-102 | `outbound/pick-tasks` | V510041:310 | Y (app) | keep | — | — | OK |
| 70 | Pickup Requests | WS-112 | `outbound/pickup-requests` | V511265:187 | Y (app) | keep | — | — | OK |
| 71 | Channel Publish Rules | WS-125 | `outbound/publish-rules` | V511271:88 | Y (app) | remove | p7-04 (+p7-12 FE) | — | OK |
| 72 | Rate Quotes | WS-117 | `outbound/rate-quotes` | V511273:72 | Y (app) | remove | p7-02 (+p7-12 FE) | — | OK |
| 73 | RTO Consignments | WS-122 | `outbound/rto` | V510050:706 | Y (app) | remove | p7-05 (+p7-12 FE) | — | OK |
| 74 | Carrier Serviceability | WS-118 | `outbound/serviceability` | V511273:75 | Y (app) | remove | p7-02 (+p7-12 FE) | — | OK |
| 75 | Shipments | WS-105 | `outbound/shipments` | V510043:373 | Y (app) | keep | — | — | OK |
| 76 | Shipment Detail | WS-106 | `outbound/shipments/[shipmentId]` | — | Y (app) | keep | — | — | OK |
| 77 | Shipping Labels | WS-114 | `outbound/shipping-labels` | V511250:112 | Y (app) | keep | — | — | OK |
| 78 | Carrier Status Mappings | WS-116 | `outbound/status-mappings` | V511273:69 | Y (app) | keep, re-home menu → `warehouse_shipping_planning` | p7-06 | — | OK |
| 79 | Tracking Events | WS-115 | `outbound/tracking-events` | V511273:66 | Y (app) | keep, re-home menu → `warehouse_shipping_planning` | p7-03/p7-06 | — | OK |
| 80 | Tracking Links | WS-126 | `outbound/tracking-links` | V511271:94 | Y (app) | remove | p7-03 (+p7-12 FE) | — | OK |
| 81 | Trade Portal | WS-240 | `outbound/trade-portal` | V511209:186 | Y (app) | remove | p7-08 (+p7-12 FE) | — | BUILD-SPEC index not marked REMOVED (CP-SC-004) |
| 82 | Waves | WS-101 | `outbound/waves` | V511250:102 | Y (app) | keep | — | — | OK |
| 83 | Print Jobs | WS-132 | `printing/jobs` | V510060:588 | Y (app) | keep | — | — | OK |
| 84 | Printers | WS-133 | `printing/printers` | V511250:105 | Y (app) | keep | — | — | OK |
| 85 | Print Routing Rules | WS-134 | `printing/routing-rules` | V511250:108 | Y (app) | keep | — | — | OK |
| 86 | Print Templates | WS-131 | `printing/templates` | V510060:575 | Y (app) | keep | — | — | OK |
| 87 | Adjustment Register | WS-213 | `reports/adjustment-register` | V511211:256 | Y (app) | keep | — | — | OK |
| 88 | Coexistence Reconciliation | WS-225 | `reports/coexistence` | V511249:190 | Y (app) | remove | p7-09 (+p7-12 FE) | — | BUILD-SPEC index not marked REMOVED (CP-SC-004) |
| 89 | Consolidated Valuation | WS-222 | `reports/consolidated-valuation` | V511262:108 | Y (app) | remove | p7-09 (+p7-12 FE) | — | BUILD-SPEC index not marked REMOVED (CP-SC-004) |
| 90 | Count History & Variance | WS-214 | `reports/count-variance` | V511211:259 | Y (app) | keep | — | — | OK |
| 91 | Expiry & Shelf-life Register | WS-221 | `reports/expiry` | V511060:183 | Y (app) | keep | — | — | OK |
| 92 | Godown-wise Stock Statement | WS-210 | `reports/godown-statement` | V511066:227 | Y (app) | keep | — | — | OK |
| 93 | Install Health Signals | WS-223 | `reports/health` | V510109:118 | Y (app) | keep | — | — | OK |
| 94 | In-transit Ageing | WS-220 | `reports/in-transit-ageing` | V511202:164 | Y (app) | keep | — | — | OK |
| 95 | Operational KPIs | WS-216 | `reports/kpis` | V511211:265 | Y (app) | keep | — | — | OK |
| 96 | Low & Insufficient Stock | WS-215 | `reports/low-stock` | V511211:262 | Y (app) | keep | — | — | OK |
| 97 | Metric Targets | WS-244 | `reports/metric-targets` | V511211:274 | Y (app) | keep | — | — | OK |
| 98 | Stock Movement Register (report) | WS-209 | `reports/movement-register` | V511066:214 | Y (app) | keep | — | — | OK |
| 99 | Parts KPIs | WS-217 | `reports/parts-kpis` | V511211:268 | Y (app) | rename → Stock KPIs `/reports/stock-kpis` | p7-11 | — | BUILD-SPEC still "Parts KPIs" (CP-SC-004) |
| 100 | stock-ageing | — | `reports/stock-ageing` | V511066:253 | Y (app) | keep | — | — | **no spec id** — route drift: spec WS-212 `/reports/ageing` |
| 101 | Stock As-At | WS-224 | `reports/stock-as-at` | V511066:266 | Y (app) | keep | — | — | OK |
| 102 | Stock on Hand | WS-208 | `reports/stock-on-hand` | V511066:201 | Y (app) | keep | — | — | OK |
| 103 | Stock-to-GL Reconciliation | WS-219 | `reports/stock-to-gl` | V511065:120 | Y (app) | keep | — | accounting-handover§5:220 | OK |
| 104 | stock-valuation | — | `reports/stock-valuation` | V511066:240 | Y (app) | keep | — | — | **no spec id** — route drift: spec WS-211 `/reports/valuation` |
| 105 | Supplier Claim Ageing | WS-250 | `reports/supplier-claim-ageing` | V511269:65 | Y (app) | keep | — | — | OK |
| 106 | Traceability | WS-218 | `reports/traceability` | V511211:271 | Y (app) | keep | — | — | OK |
| 107 | service-types | — | `vas/service-types` | V511208:189 | Y (app) | keep | — | — | **no spec id** — route drift: spec WS-145 `/execution/vas-service-types` |
| 108 | work-orders | — | `vas/work-orders` | V511208:185 | Y (app) | keep | — | — | **no spec id** — route drift: spec WS-144 `/execution/work-orders` |
| 109 | Accessorials | WS-163 | `3pl/accessorials` | V531008:148 | Y (3pl) | keep | — | — | OK |
| 110 | AR Handover Queue | WS-170 | `3pl/ar-handovers` | V531008:154 | Y (3pl) | keep | — | — | OK |
| 111 | Billable Events | WS-160 | `3pl/billable-events` | V530030:345 | Y (3pl) | keep | — | — | OK |
| 112 | Billing Runs | WS-162 | `3pl/billing-runs` | V531008:145 | Y (3pl) | keep | — | — | OK |
| 113 | Charge Codes | WS-158 | `3pl/charge-codes` | V530020:207 | Y (3pl) | keep | — | — | OK |
| 114 | Client GST Registrations | WS-169 | `3pl/client-gst` | V531150:111 | Y (3pl) | keep | — | — | OK |
| 115 | 3PL Clients | WS-155 | `3pl/clients` | V531000:234 | Y (3pl) | keep | — | — | OK |
| 116 | Custody & Insured Value | WS-227 | `3pl/custody-value` | V531009:133 | Y (3pl) | keep | — | — | OK |
| 117 | Disputes | WS-164 | `3pl/disputes` | V531008:151 | Y (3pl) | keep | — | — | OK |
| 118 | Freight Billing Rules | WS-165 | `3pl/freight-rules` | V530044:132 | Y (3pl) | keep | — | — | OK |
| 119 | Onboarding Tasks | WS-157 | `3pl/onboarding-tasks` | V531000:240 | Y (3pl) | keep | — | — | OK |
| 120 | Onboarding Templates | WS-156 | `3pl/onboarding-templates` | V531000:237 | Y (3pl) | keep | — | — | OK |
| 121 | Client Portal | WS-172 | `3pl/portal` | V531009:147 | Y (3pl) | keep | — | — | OK |
| 122 | Rate Cards | WS-159 | `3pl/rate-cards` | V530021:406 | Y (3pl) | keep | — | — | OK |
| 123 | SLA Breaches | WS-168 | `3pl/sla-breaches` | V530050:336 | Y (3pl) | keep | — | — | OK |
| 124 | SLA Definitions | WS-166 | `3pl/sla-definitions` | V530050:330 | Y (3pl) | keep | — | — | OK |
| 125 | SLA Measurements | WS-167 | `3pl/sla-measurements` | V530050:333 | Y (3pl) | keep | — | — | OK |
| 126 | Storage Billing Periods | WS-161 | `3pl/storage-billing` | V530031:310 | Y (3pl) | keep | — | — | OK |
| 127 | Attribute Keys | WS-013 | `catalogues/attribute-keys` | V500010:595 | Y (base) | keep | — | — | OK |
| 128 | Condition Codes | WS-014 | `catalogues/condition-codes` | V500005:398 | Y (base) | keep | — | — | OK |
| 129 | Counterparty Roles | WS-011 | `catalogues/counterparty-roles` | V500011:459 | Y (base) | keep | — | — | OK |
| 130 | Dispositions | WS-012 | `catalogues/dispositions` | V500010:594 | Y (base) | keep | — | — | OK |
| 131 | Document & Reference Types | WS-002 | `catalogues/document-types` | V500002:317 | Y (base) | keep | — | — | OK |
| 132 | Item Types | WS-010 | `catalogues/item-types` | V500008:168 | Y (base) | keep | — | — | OK |
| 133 | Location Types | WS-005 | `catalogues/location-types` | V500013:437 | Y (base) | keep | — | — | OK |
| 134 | Movement Types | WS-001 | `catalogues/movement-types` | V500003:318 | Y (base) | keep | — | — | OK |
| 135 | Owner Types | WS-009 | `catalogues/owner-types` | V500007:361 | Y (base) | keep | — | — | OK |
| 136 | Reason Codes | WS-006 | `catalogues/reason-codes` | V500004:247 | Y (base) | keep | — | — | OK |
| 137 | Source Systems | WS-003 | `catalogues/source-systems` | V500002:318 | Y (base) | keep | — | — | OK |
| 138 | Stock Statuses | WS-004 | `catalogues/stock-statuses` | V500005:397 | Y (base) | keep | — | — | OK |
| 139 | Task Types | WS-008 | `catalogues/task-types` | V500010:593 | Y (base) | keep | — | — | OK |
| 140 | UoM Classes | WS-007 | `catalogues/uom-classes` | V500009:302 | Y (base) | keep | — | — | OK |
| 141 | Tasks | WS-059 | `execution/tasks` | V500034:300 | Y (base) | keep | — | — | OK |
| 142 | Cost Layers | WS-049 | `ledger/cost-layers` | V501119:158 | Y (base) | keep | — | — | OK |
| 143 | Position Drift Findings | WS-043 | `ledger/drift-findings` | V500045:250 | Y (base) | keep | — | — | OK |
| 144 | Genealogy Explorer | WS-039 | `ledger/genealogy` | V500035:260 | Y (base) | keep | — | — | OK |
| 145 | Stock Movement Register | WS-040 | `ledger/movements` | V500030:1112 | Y (base) | keep | — | movement-post-reverse§5:241 | OK |
| 146 | Movement Detail | WS-041 | `ledger/movements/[movementId]` | — | Y (base) | keep | — | movement-post-reverse§5:259 | OK |
| 147 | Soft-close Overrides | WS-046 | `ledger/period-overrides` | V500019:321 | Y (base) | keep | — | — | OK |
| 148 | Stock Periods | WS-045 | `ledger/periods` | V500019:305 | Y (base) | keep | — | — | OK |
| 149 | Stock Position Enquiry | WS-042 | `ledger/positions` | V500031:376 | Y (base) | keep | — | movement-post-reverse§5:271 | OK |
| 150 | Reservations | WS-047 | `ledger/reservations` | V500033:708 | Y (base) | keep | — | — | OK |
| 151 | Scan Enquiry Console | WS-071 | `ledger/scan` | V500016:679 | Y (base) | keep | — | — | OK |
| 152 | Position Snapshots | WS-044 | `ledger/snapshots` | V500045:264 | Y (base) | keep | — | — | OK |
| 153 | Allocation Strategies | WS-048 | `masters/allocation-strategies` | V501070:88 | Y (base) | keep | — | — | OK |
| 154 | Category Stocking Ownership | WS-066 | `masters/category-ownership` | V500053:209 | Y (base) | remove | p7-09 (+p7-12 FE) | — | BUILD-SPEC index not marked REMOVED (CP-SC-004) |
| 155 | Channels | WS-068 | `masters/channels` | V500051:154 | Y (base) | keep, trim | p7-10 (B2B kind only) | — | OK |
| 156 | Companies | WS-015 | `masters/companies` | V500001:299 | Y (base) | keep | — | — | OK |
| 157 | Counterparties | WS-021 | `masters/counterparties` | V500011:473 | Y (base) | keep | — | — | OK |
| 158 | GL Posting Rules | WS-051 | `masters/gl-posting-rules` | V500042:280 | Y (base) | keep | — | accounting-handover§5:246 | OK |
| 159 | Item Categories | WS-022 | `masters/item-categories` | V500014:267 | Y (base) | keep, trim | p7-09 (drop isDualEligible) | — | OK |
| 160 | Item External References | WS-031 | `masters/item-external-refs` | V500017:192 | Y (base) | keep | — | — | OK |
| 161 | Item Identifiers & Barcodes | WS-024 | `masters/item-identifiers` | V500016:670 | Y (base) | keep | — | — | OK |
| 162 | Item × Location Settings | WS-028 | `masters/item-location-settings` | V501103:142 | Y (base) | keep | — | — | OK |
| 163 | Item × Site Settings | WS-027 | `masters/item-site-settings` | V500050:374 | Y (base) | keep | — | — | OK |
| 164 | Item Supplier Sources | WS-029 | `masters/item-supplier-sources` | V500050:377 | Y (base) | keep | — | — | OK |
| 165 | Items | WS-023 | `masters/items` | V500015:636 | Y (base) | keep | — | — | OK |
| 166 | Kit Definitions | WS-035 | `masters/kits` | V500060:231 | Y (base) | keep | — | — | OK |
| 167 | Locations | WS-017 | `masters/locations` | V500013:451 | Y (base) | keep | — | — | OK |
| 168 | Location Generator | WS-018 | `masters/locations/generate` | — | Y (base) | keep | — | — | OK — opened by the *Generate locations* action (BUILD-SPEC-SCREENS.md:1065), no leaf needed |
| 169 | Lots | WS-036 | `masters/lots` | V500018:571 | Y (base) | keep | — | — | OK |
| 170 | LPNs | WS-038 | `masters/lpns` | V500018:577 | Y (base) | keep | — | — | OK |
| 171 | Master Merge Log | WS-245 | `masters/master-merges` | V500055:205 | Y (base) | keep | — | — | OK |
| 172 | Number Series | WS-061 | `masters/number-series` | V500020:491 | Y (base) | keep | — | — | OK |
| 173 | Owner Grants | WS-020 | `masters/owner-grants` | V500044:176 | Y (base) | keep | — | — | OK |
| 174 | Owners | WS-019 | `masters/owners` | V500007:390 | Y (base) | keep | — | — | OK |
| 175 | Item Packaging Levels | WS-025 | `masters/packaging-levels` | V500016:673 | Y (base) | keep | — | — | OK |
| 176 | Serials | WS-037 | `masters/serials` | V500018:574 | Y (base) | keep | — | — | OK |
| 177 | Item Supersessions | WS-030 | `masters/supersessions` | V500050:380 | Y (base) | keep | — | — | OK |
| 178 | Item UoM Conversions | WS-026 | `masters/uom-conversions` | V500016:676 | Y (base) | keep | — | — | OK |
| 179 | Units of Measure | WS-034 | `masters/uoms` | V500009:316 | Y (base) | keep | — | — | OK |
| 180 | Valuation Policies | WS-050 | `masters/valuation-policies` | V501119:161 | Y (base) | keep | — | — | OK |
| 181 | Variant Axes & Values | WS-032 | `masters/variant-axes` | V500090:374 | Y (base) | keep | — | — | OK |
| 182 | Style × Variant Matrix | WS-033 | `masters/variant-matrix` | V500090:377 | Y (base) | keep | — | — | OK |
| 183 | Warehouse Grants | WS-238 | `masters/warehouse-grants` | V501010:67 | Y (base) | keep | — | — | OK |
| 184 | Warehouses (sites) | WS-016 | `masters/warehouses` | V500012:475 | Y (base) | keep | — | — | OK |
| 185 | Alert Events | WS-070 | `platform/alert-events` | V500063:591 | Y (base) | keep | — | — | OK |
| 186 | Alert Rules | WS-069 | `platform/alert-rules` | V500063:588 | Y (base) | keep | — | — | OK |
| 187 | API Client Keys | WS-247 | `platform/api-client-keys` | V500066:309 | Y (base) | keep | — | — | OK |
| 188 | API Clients | WS-246 | `platform/api-clients` | V500066:306 | Y (base) | keep | — | — | OK |
| 189 | Warehouse Audit Events | WS-063 | `platform/audit-events` | V501011:780 | Y (base) | keep | — | — | OK |
| 190 | Devices | WS-060 | `platform/devices` | V500062:240 | Y (base) | keep | — | — | OK |
| 191 | External Stock Snapshots | WS-067 | `platform/external-snapshots` | V500053:213 | Y (base) | remove | p7-09 (+p7-12 FE) | — | BUILD-SPEC index not marked REMOVED (CP-SC-004) |
| 192 | Accounting Handover Queue | WS-052 | `platform/handovers` | V500042:294 | Y (base) | keep | — | accounting-handover§5:203 | OK |
| 193 | Import Batches | WS-065 | `platform/imports` | V500046:280 | Y (base) | keep | — | — | OK |
| 194 | Job Runs | WS-064 | `platform/job-runs` | V501011:783 | Y (base) | keep | — | — | OK |
| 195 | Movement Batches | WS-055 | `platform/movement-batches` | V500041:363 | Y (base) | keep | — | — | OK |
| 196 | Numbers Issued | WS-062 | `platform/numbers-issued` | V500020:520 | Y (base) | keep | — | — | OK |
| 197 | Outbox Monitor | WS-056 | `platform/outbox` | V500040:527 | Y (base) | keep | — | — | OK |
| 198 | Outbox Dead-letter | WS-058 | `platform/outbox-deliveries` | V500040:531 | Y (base) | keep | — | — | OK |
| 199 | Outbox Subscriptions | WS-057 | `platform/outbox-subscriptions` | V500040:529 | Y (base) | keep | — | — | OK |
| 200 | Port Monitor — Inbound Messages | WS-053 | `platform/port-monitor` | V500041:336 | Y (base) | keep | — | movement-post-reverse§5:287 | OK |
| 201 | Port Rejected Queue | WS-054 | `platform/port-rejected` | V500041:350 | Y (base) | keep | — | movement-post-reverse§5:287 | OK |
| 202 | Compliance API Logs | WS-177 | `india/api-logs` | V541050:141 | Y (india) | keep | — | — | OK |
| 203 | Goods on Approval | WS-188 | `india/approval-dispatches` | V541110:163 | Y (india) | keep | — | — | OK |
| 204 | Bonded Licences | WS-185 | `india/bonded-licences` | V541112:193 | Y (india) | keep | — | — | OK |
| 205 | bonded-losses | — | `india/bonded-losses` | V541156:258 | Y (india) | keep | — | — | **no spec id** — no spec id |
| 206 | Warehousing Bonds | WS-186 | `india/bonds` | V541112:196 | Y (india) | keep | — | — | OK |
| 207 | Compliance Documents | WS-176 | `india/compliance-documents` | V541050:138 | Y (india) | keep | — | — | OK |
| 208 | Compliance Tasks & Rules | WS-191 | `india/compliance-tasks` | V541124:111 | Y (india) | keep | — | — | OK |
| 209 | Counterparty Licences | WS-253 | `india/counterparty-licences` | V541122:211 | Y (india) | keep | — | — | OK |
| 210 | delivery-challans | — | `india/delivery-challans` | V541052:117 | Y (india) | keep | — | — | **no spec id** — route drift: spec WS-178 `/india/challans` |
| 211 | Our Licences | WS-252 | `india/entity-licences` | V541122:208 | Y (india) | keep | — | — | OK |
| 212 | EPR Returns | WS-189 | `india/epr` | V541114:45 | Y (india) | keep | — | — | OK |
| 213 | E-way Bills | WS-179 | `india/eway-bills` | V541054:116 | Y (india) | keep | — | — | OK |
| 214 | Consolidated E-way Bills | WS-180 | `india/eway-bills-consolidated` | V541118:144 | Y (india) | keep | — | — | OK |
| 215 | Ex-bond Clearances | WS-187 | `india/ex-bond` | V541112:199 | Y (india) | keep | — | — | OK |
| 216 | GSTIN Profiles | WS-173 | `india/gstin-profiles` | V541000:197 | Y (india) | keep | — | — | OK |
| 217 | ITC Reversals | WS-184 | `india/itc-reversals` | V541106:48 | Y (india) | keep | — | — | OK |
| 218 | ITC-04 Returns | WS-182 | `india/itc04` | V541102:179 | Y (india) | keep | — | — | OK |
| 219 | Job Work Registrations | WS-181 | `india/job-work` | V541102:166 | Y (india) | keep | — | — | OK |
| 220 | Quantity Ceilings | WS-254 | `india/licence-ceilings` | V541122:214 | Y (india) | keep | — | — | OK |
| 221 | Licence Types | WS-251 | `india/licence-types` | V541122:205 | Y (india) | keep | — | — | OK |
| 222 | Compliance Providers | WS-174 | `india/providers` | V541050:135 | Y (india) | keep | — | — | OK |
| 223 | Recall Notifications | WS-255 | `india/recall-notifications` | V541122:217 | Y (india) | keep | — | — | OK |
| 224 | Compliance Registrations | WS-175 | `india/registrations` | V541000:200 | Y (india) | keep | — | — | OK |
| 225 | Retention Policies | WS-190 | `india/retention-policies` | V541116:145 | Y (india) | keep | — | — | OK |
| 226 | Statutory Stock Account | WS-183 | `india/stock-account` | V541104:45 | Y (india) | keep | — | — | OK |
| 227 | Stock by MRP | WS-226 | `india/stock-by-mrp` | V541108:169 | Y (india) | keep | — | — | OK |
| 228 | HSN / SAC / State Codes | WS-193 | `india/tax-reference` | V541100:233 | Y (india) | keep | — | — | OK |

## 5. Matrix B — new screens WS-260…WS-339 (planned, none in code)

The menu column shows the planned L2 and the migration that seeds it. Detail pages get no leaf.

| # | screen | spec id | route | menu row (planned) | in code | D-16 | carrier | contract §5 | verdict |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Gate Entries | WS-260 | `/warehouse/gate/entries` | Gate (new L2, p8-14) — p8-14 `V511413` | N | new (P8 core) | p8-03 | gate-entry§5:163 | menu breaches 10-L2 cap (CP-SC-001) |
| 2 | Gate Entry detail | WS-261 | `/warehouse/gate/entries/[id]` | — (detail) — p8-14 `V511413` | N | new (P8 core) | p8-03 | gate-entry§5 | OK |
| 3 | Gate Passes | WS-262 | `/warehouse/gate/passes` | Gate (new L2, p8-14) — p8-14 `V511413` | N | new (P8 core) | p8-03 | gate-entry§5:178 | menu breaches 10-L2 cap (CP-SC-001) |
| 4 | Gate Pass detail (lines, returns) | WS-263 | `/warehouse/gate/passes/[id]` | — (detail) — p8-14 `V511413` | N | new (P8 core) | p8-03 | gate-entry§5:178 | OK |
| 5 | Sampling Schemes | WS-264 | `/warehouse/quality/sampling-schemes` | Quality (new L2) — p8-14 `V511413` | N | new (P8 core) | p8-05 | incoming-inspection-sampling§5:125 | no row actions/status in contract; menu breaches 10-L2 cap (CP-SC-001) |
| 6 | Inspection Plan Assignments | WS-265 | `/warehouse/quality/plan-assignments` | Quality (new L2) — p8-14 `V511413` | N | new (P8 core) | p8-05 | incoming-inspection-sampling§5:136 | menu breaches 10-L2 cap (CP-SC-001) |
| 7 | Material Receipt Notes | WS-266 | `/warehouse/stores/mrns` | Stores (new L2) — p8-14 `V511413` | N | new (P8 core) | p8-08 | mrn-authorisation§5:116 | menu breaches 10-L2 cap (CP-SC-001) |
| 8 | MRN detail (+ print) | WS-267 | `/warehouse/stores/mrns/[id]` | — (detail) — p8-14 `V511413` | N | new (P8 core) | p8-08 | mrn-authorisation§5 | OK |
| 9 | Material Requisitions | WS-268 | `/warehouse/stores/requisitions` | Stores (new L2) — p8-14 `V511413` | N | new (P8 core) | p8-09 | material-requisition§5:140 | menu breaches 10-L2 cap (CP-SC-001) |
| 10 | Material Requisition detail | WS-269 | `/warehouse/stores/requisitions/[id]` | — (detail) — p8-14 `V511413` | N | new (P8 core) | p8-09 | material-requisition§5 | OK |
| 11 | Store Issues | WS-270 | `/warehouse/stores/issues` | Stores (new L2) — p8-14 `V511413` | N | new (P8 core) | p8-10 | store-issue-return§5:130 | menu breaches 10-L2 cap (CP-SC-001) |
| 12 | Store Issue detail | WS-271 | `/warehouse/stores/issues/[id]` | — (detail) — p8-14 `V511413` | N | new (P8 core) | p8-10/p8-11 | store-issue-return§5:130 | OK |
| 13 | Store Returns | WS-272 | `/warehouse/stores/returns` | Stores (new L2) — p8-14 `V511413` | N | new (P8 core) | p8-11 | store-issue-return§5:142 | menu breaches 10-L2 cap (CP-SC-001) |
| 14 | Cost Centres | WS-273 | `/warehouse/stores/cost-centres` | Stores (new L2) — p8-14 `V511413` | N | new (P8 core) | p8-09 | store-issue-return§5:146 | no actions/export in contract (Department ref implies); menu breaches 10-L2 cap (CP-SC-001) |
| 15 | Issue queue (approved requisitions awaiting issu | WS-274 | `/warehouse/stores/issue-queue` | Stores (new L2) — p8-14 `V511413` | N | new (P8 core) | p8-09 | material-requisition§5:152 | no export/scope stated in contract (task p8-14 names scope); menu breaches 10-L2 cap (CP-SC-001) |
| 16 | PO Delivery Schedule | WS-275 | `/warehouse/inbound/purchase-orders/schedule` | Inbound, or new *Purchasing* L2 — p8-14 `V511413` | N | new (P8 core) | p8-01 | po-schedule-port§5:154 | menu breaches 10-L2 cap (CP-SC-001) |
| 17 | Customer Delivery Schedule | WS-276 | `/warehouse/outbound/demand-schedule` | Outbound (full, 8) → new L2 — p8-14 `V511413` | N | new (P8 core) | p8-02 | po-schedule-port§5:158 | contract §5.3 gives columns only: no grid id/scope, filters, export, actions (CP-SC-006); menu breaches 10-L2 cap (CP-SC-001) |
| 18 | Stores Registers (RGP pending, requisitions pend | WS-277 | `/warehouse/stores/registers` | Stores (new L2) — p8-14 `V511413` | N | new (P8 core) | p8-13 | store-issue-return§5:150 | tab spec in p8-13, not contract; menu breaches 10-L2 cap (CP-SC-001) |
| 19 | Supplier Trade Profiles | WS-280 | `/warehouse/trade/masters/supplier-profiles` | Trade Masters — p9-01 `V551000` | N | new (P9 trade) | p9-02 | trade-counterparty-evaluation§5 | OK |
| 20 | Customer Trade Profiles | WS-281 | `/warehouse/trade/masters/customer-profiles` | Trade Masters — p9-01 `V551000` | N | new (P9 trade) | p9-02 | trade-counterparty-evaluation§5 | OK |
| 21 | Approved Vendor List | WS-282 | `/warehouse/trade/masters/approved-vendors` | Trade Masters — p9-01 `V551000` | N | new (P9 trade) | p9-02 | trade-counterparty-evaluation§5 | OK |
| 22 | Customer Item References | WS-283 | `/warehouse/trade/masters/customer-items` | Trade Masters — p9-01 `V551000` | N | new (P9 trade) | p9-02 | trade-counterparty-evaluation§5 | OK |
| 23 | Approval Rules | WS-284 | `/warehouse/trade/masters/approval-rules` | Trade Masters — p9-01 `V551000` | N | new (P9 trade) | p9-03 | trade-approval-matrix§5:140 | OK |
| 24 | My Approvals | WS-285 | `/warehouse/trade/approvals` | Trade Masters — p9-01 `V551000` | N | new (P9 trade) | p9-03 | trade-approval-matrix§5:149 | OK |
| 25 | Purchase Requisitions | WS-286 | `/warehouse/trade/purchase/requisitions` | Purchasing — Sourcing — p9-01 `V551000` | N | new (P9 trade) | p9-04 | trade-purchase-requisition§5:132 | OK |
| 26 | Requisition Workbench | WS-287 | `/warehouse/trade/purchase/requisition-workbench` | Purchasing — Sourcing — p9-01 `V551000` | N | new (P9 trade) | p9-04 | trade-purchase-requisition§5:143 | OK |
| 27 | RFQs | WS-288 | `/warehouse/trade/purchase/rfqs` | Purchasing — Sourcing — p9-01 `V551000` | N | new (P9 trade) | p9-05 | trade-rfq-award§5:150 | OK |
| 28 | Vendor Quotations | WS-289 | `/warehouse/trade/purchase/vendor-quotations` | Purchasing — Sourcing — p9-01 `V551000` | N | new (P9 trade) | p9-05 | trade-rfq-award§5:157 | OK |
| 29 | Comparative Statements | WS-290 | `/warehouse/trade/purchase/comparative-statements` (+ `/[id]`) | Purchasing — Sourcing — p9-01 `V551000` | N | new (P9 trade) | p9-05 | trade-rfq-award§5:166 | OK |
| 30 | Purchase Rate Contracts | WS-291 | `/warehouse/trade/purchase/rate-contracts` | Purchasing — Orders — p9-01 `V551000` | N | new (P9 trade) | p9-06 | trade-rate-contract§5 | OK |
| 31 | Purchase Orders | WS-292 | `/warehouse/trade/purchase/orders` | Purchasing — Orders — p9-01 `V551000` | N | new (P9 trade) | p9-07 | trade-purchase-order§5:202 | OK |
| 32 | Purchase Order Detail | WS-293 | `/warehouse/trade/purchase/orders/[id]` | (detail) — p9-01 `V551000` | N | new (P9 trade) | p9-07 | trade-purchase-order§5:213 | OK |
| 33 | Schedule Releases | WS-294 | `/warehouse/trade/purchase/releases` | Purchasing — Orders — p9-01 `V551000` | N | new (P9 trade) | p9-07 | trade-purchase-order§5:215 | OK |
| 34 | Purchase Expediting | WS-295 | `/warehouse/trade/purchase/expediting` | Purchasing — Orders — p9-01 `V551000` | N | new (P9 trade) | p9-10 | trade-purchase-order§5:226 | OK |
| 35 | PO Amendments | WS-296 | `/warehouse/trade/purchase/amendments` | Purchasing — Orders — p9-01 `V551000` | N | new (P9 trade) | p9-11 | trade-order-amendment§5 | OK |
| 36 | Vendor Evaluations | WS-297 | `/warehouse/trade/purchase/vendor-evaluations` | Purchasing — Orders — p9-01 `V551000` | N | new (P9 trade) | p9-12 | trade-counterparty-evaluation§5 | OK |
| 37 | Sales Enquiries | WS-298 | `/warehouse/trade/sales/enquiries` | Sales — Pre-sales — p9-01 `V551000` | N | new (P9 trade) | p9-08 | trade-sales-enquiry-quotation§5:139 | OK |
| 38 | Customer Quotations | WS-299 | `/warehouse/trade/sales/quotations` | Sales — Pre-sales — p9-01 `V551000` | N | new (P9 trade) | p9-08 | trade-sales-enquiry-quotation§5:147 | OK |
| 39 | Quotation Win/Loss | WS-300 | `/warehouse/trade/sales/win-loss` | Sales — Pre-sales — p9-01 `V551000` | N | new (P9 trade) | p9-08 | trade-sales-enquiry-quotation§5:156 | OK |
| 40 | Price Lists | WS-301 | `/warehouse/trade/sales/price-lists` | Sales — Pre-sales — p9-01 `V551000` | N | new (P9 trade) | p9-06 | trade-rate-contract§5 | OK |
| 41 | Sales Rate Contracts | WS-302 | `/warehouse/trade/sales/rate-contracts` | Sales — Orders — p9-01 `V551000` | N | new (P9 trade) | p9-06 | trade-rate-contract§5 | OK |
| 42 | Sales Orders | WS-303 | `/warehouse/trade/sales/orders` | Sales — Orders — p9-01 `V551000` | N | new (P9 trade) | p9-09 | trade-sales-order§5:204 | OK |
| 43 | Sales Order Detail | WS-304 | `/warehouse/trade/sales/orders/[id]` | (detail) — p9-01 `V551000` | N | new (P9 trade) | p9-09 | trade-sales-order§5:215 | OK |
| 44 | Dispatch Planning | WS-305 | `/warehouse/trade/sales/dispatch-planning` | Sales — Orders — p9-01 `V551000` | N | new (P9 trade) | p9-09 | trade-sales-order§5:236 | OK |
| 45 | Delivery Commitments | WS-306 | `/warehouse/trade/sales/commitments` | Sales — Orders — p9-01 `V551000` | N | new (P9 trade) | p9-10 | trade-sales-order§5:227 | OK |
| 46 | SO Amendments | WS-307 | `/warehouse/trade/sales/amendments` | Sales — Orders — p9-01 `V551000` | N | new (P9 trade) | p9-11 | trade-order-amendment§5 | OK |
| 47 | Sales Return Authorisations | WS-308 | `/warehouse/trade/sales/return-authorisations` | Sales — Orders — p9-01 `V551000` | N | new (P9 trade) | p9-13 | trade-sales-return-authorisation§5 | OK |
| 48 | Dispatch Releases | WS-313 | `/warehouse/trade/sales/dispatch-releases` | Sales — Orders — p9-01 `V551000` | N | new (P9 trade) | p9-09 | trade-sales-order§5:217 | OK |
| 49 | Customer Ratings | WS-309 | `/warehouse/trade/sales/customer-ratings` | Sales — Pre-sales — p9-01 `V551000` | N | new (P9 trade) | p9-12 | trade-counterparty-evaluation§5 | OK |
| 50 | Evaluation Schemes | WS-310 | `/warehouse/trade/masters/evaluation-schemes` | Trade Masters — p9-01 `V551000` | N | new (P9 trade) | p9-12 | trade-counterparty-evaluation§5 | OK |
| 51 | T&C Templates | WS-311 | `/warehouse/trade/masters/terms-templates` | Trade Masters — p9-01 `V551000` | N | new (P9 trade) | p9-02 | trade-counterparty-evaluation§5 | OK |
| 52 | Trade Reports | WS-312 | `/warehouse/trade/reports/<report>` (8 reports) | Trade Reports — p9-01 `V551000` | N | new (P9 trade) | p9-14 | — | **no screen contract**; spec only in p9-14 table (CP-SC-005) |
| 53 | BOMs | WS-320 | `/warehouse/manufacturing/boms` | Production — p10-01 `V561000` | N | new (P10 mfg) | p10-03 | mfg-bom§5:159 | OK |
| 54 | BOM Explosion & Where-used | WS-321 | `/warehouse/manufacturing/bom-explorer` | Costing & Reports — p10-01 `V561000` | N | new (P10 mfg) | p10-03 | mfg-bom§5:173 | report: no filters listed |
| 55 | Work Centres | WS-322 | `/warehouse/manufacturing/work-centres` | Production — p10-01 `V561000` | N | new (P10 mfg) | p10-04 | mfg-bom§5:177 | OK |
| 56 | Production Orders | WS-323 | `/warehouse/manufacturing/production-orders` | Production — p10-01 `V561000` | N | new (P10 mfg) | p10-05 | mfg-production-order§5:197 | OK |
| 57 | Production Order detail | WS-324 | `/warehouse/manufacturing/production-orders/[id]` | — (detail) — p10-01 `V561000` | N | new (P10 mfg) | p10-05 | mfg-costing-close§5:192 | OK |
| 58 | Staging Lists | WS-325 | `/warehouse/manufacturing/staging-lists` | Production — p10-01 `V561000` | N | new (P10 mfg) | p10-06 | mfg-material-staging-issue§5:149 | OK |
| 59 | Production Receipts | WS-326 | `/warehouse/manufacturing/production-receipts` | Production — p10-01 `V561000` | N | new (P10 mfg) | p10-07 | mfg-production-receipt§5:185 | OK |
| 60 | Receipt Reversals | WS-327 | `/warehouse/manufacturing/receipt-reversals` | Production — p10-01 `V561000` | N | new (P10 mfg) | p10-07 | mfg-production-receipt§5:201 | OK |
| 61 | Operation Confirmations | WS-328 | `/warehouse/manufacturing/operation-confirmations` | Production — p10-01 `V561000` | N | new (P10 mfg) | p10-08 | mfg-qc-rework§5:168 | OK |
| 62 | Settlements & Close | WS-329 | `/warehouse/manufacturing/settlements` | Costing & Reports — p10-01 `V561000` | N | new (P10 mfg) | p10-09 | mfg-costing-close§5:176 | OK |
| 63 | Subcontracting | WS-330 | `/warehouse/manufacturing/subcontracting` | Production — p10-01 `V561000` | N | new (P10 mfg) | p10-10 | mfg-subcontracting§5:167 | OK |
| 64 | Item Planning Parameters | WS-331 | `/warehouse/manufacturing/planning-parameters` | Planning — p10-01 `V561000` | N | new (P10 mfg) | p10-11 | mfg-mrp§5 | OK |
| 65 | Demand Plans | WS-332 | `/warehouse/manufacturing/demand-plans` | Planning — p10-01 `V561000` | N | new (P10 mfg) | p10-11 | mfg-mrp§5 | OK |
| 66 | MRP Runs | WS-333 | `/warehouse/manufacturing/mrp-runs` | Planning — p10-01 `V561000` | N | new (P10 mfg) | p10-12 | mfg-mrp§5 | OK |
| 67 | MRP Proposals (planner workbench) | WS-334 | `/warehouse/manufacturing/mrp-proposals` | Planning — p10-01 `V561000` | N | new (P10 mfg) | p10-12 | mfg-mrp§5, mfg-production-order§5 | OK |
| 68 | MRP Exceptions | WS-335 | `/warehouse/manufacturing/mrp-exceptions` | Planning — p10-01 `V561000` | N | new (P10 mfg) | p10-12 | mfg-mrp§5 | OK |
| 69 | Capacity Load | WS-336 | `/warehouse/manufacturing/capacity-load` | Planning — p10-01 `V561000` | N | new (P10 mfg) | p10-13 | mfg-mrp§5:200 | OK |
| 70 | Manufacturing Registers (production register, WI | WS-337 | `/warehouse/manufacturing/registers` | Costing & Reports — p10-01 `V561000` | N | new (P10 mfg) | p10-13 | mfg-production-order§5:231 | OK |
| 71 | *reserved* | WS-338 | — | — | N | — | — | — | unused id |
| 72 | *reserved* | WS-339 | — | — | N | — | — | — | unused id |

## 6. Method (reproducible)

- Pages: `find <module>/frontend -name page.tsx` across the four modules.
- Menus: a parse of every `INSERT INTO menus` / `UPDATE menus … parent_id` in `*/backend/src/main/resources/db/migration`, plus a raw grep of `'/dashboard/warehouse…'` for leaves the parser missed.
- Spec ids: `BUILD-SPEC-SCREENS.md` §1 index (255 rows), joined on route with `/dashboard` stripped and `[param]` normalised.
- Contracts: the `## 5.` subsections of each contract, keyword-checked for grid, columns, filters, actions, status/tiles, export and modal, then read by hand where a check came back empty.
- Scenarios: the `WH-SC` rows of the four FRDs against the `## Scenarios closed` lists of `p7…p10` (ranges `A … B` expanded).
