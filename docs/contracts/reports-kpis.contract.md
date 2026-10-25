# Functional Contract — Reports and KPIs (WS-208…WS-218, WS-243, WS-244, the operations dashboard)

> **What this is.** The functional truth for warehouse's core report pack: what each report reads, its
> columns, filters and permission, and **the computation rule its requirement states**. Reports change
> nothing; every figure is computed in the backend from the ledger and lifecycle timestamps, and the page
> does no arithmetic. A T5-only contract, as R30 `CP-FR-007` row 21 proposes. The valuation report's cost
> rules are [`costing-valuation`](costing-valuation.contract.md); WS-219 Stock-to-GL is
> [`accounting-handover`](accounting-handover.contract.md) `AHO-RPT-*`; trade's reports are
> [`trade-reports`](trade-reports.contract.md).
>
> **Status.** Derived 2026-10-23 (v0) from `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` §6.22 (`FR-384`…`FR-394`,
> `FR-396`, `FR-397`, `FR-399`) with `FR-470`, `FR-471`, and `BUILD-SPEC-SCREENS.md` §7, verified against the
> built controllers in `classic` `warehouse`. Not ratified.

---

## 0. Identity

| | |
|---|---|
| **Workflow** | none — read-only reports; each row drills to the movement or document it came from. WS-244 Metric Targets is the one writable master |
| **Module** | `warehouse` (`ai.warehouse.controller.Wh*Controller` under `/warehouse/reports`); metric catalogue in `warehouse-base` (`whb_metric_definitions`, `V500048`) |
| **Domain baseline** | `D-14` / `RG-001` (the `REGISTERED` branch), `L-12` (retention), `L-14` · `RC-005`, `RC-007`, `RC-009` · CLAUDE.md rule 8 (no arithmetic in the page) |
| **Owning tasks** | `issues/p2-20.md` (pack 1: WS-208…WS-212) · `issues/p2-21.md` (pack 2: WS-213…WS-218, WS-244, `FR-470`) · `issues/p3-17.md` (KPI snapshots — PARTIALLY VOID; its consolidated valuation is VOID) · `issues/p6-10.md` (dashboard) · `issues/p6-02.md` (location utilisation — VOID) |
| **Primary tables** | none of their own except `wh_metric_targets` (`V510091`) and `wh_kpi_snapshots` (`V510106`); the reports read `whb_stock_movements`, `whb_stock_movement_lines`, `whb_stock_positions`, `whb_cost_layers`, `wh_counts`, `wh_count_lines`, `whb_item_site_settings`, `wh_insufficient_stock_log`, `wh_demand_history`, `whb_transformations`, `whb_locations` |
| **Permission resources** | per report `wh_rpt_<name>:view` and `:export` (`hasAuthority(…) or hasRole('ADMIN')` on export) — names in §5 · `wh_metric_targets:{view,create,edit,delete,export}` |
| **Routes** | `/warehouse/reports/<report>` per §5 · mobile: none (`D-16` item 7) |
| **Contract version** | `v0 — 2026-10-23` |

### Acceptance checks

| # | Expects | Delivered by |
|---|---|---|
| A1 | Every report computes in SQL from the ledger; no figure in the page (`WH-SC-298`) | `RKP-GRD-01`, `RKP-UNR-04` |
| A2 | The godown statement splits a re-registered site at the switch (`WH-SC-060`) | `RKP-T5-03` |
| A3 | Valuation as at a date reproduces next year (`WH-SC-040`) | `RKP-T5-04` |
| A4 | The four stock KPIs carry frozen definitions (`WH-SC-283`) | `RKP-T5-10` |
| A5 | A KPI with no target shows a blank variance, never zero | `RKP-T5-09`, `RKP-T5-14` |
| A6 | Traceability both ways for the retention period (`WH-SC-029`) | `RKP-T5-11`, `RKP-GRD-03` |

---

## 1. T1 — State machine

None. A report has no state and no transition. WS-244 rows are effective-dated master rows.

### 1.3 Guards

| ID | Predicate | Refusal | Source |
|---|---|---|---|
| RKP-GRD-01 | Every figure is computed from the ledger and lifecycle timestamps at read time; a pre-aggregated snapshot (`wh_kpi_snapshots`) exists only for a metric measured too slow | — | FR-394 |
| RKP-GRD-02 | Record scope: rows only for the sites (and owners) the caller is granted; a site the caller names outside scope is refused | `403` naming the report | FR-384, FR-385 |
| RKP-GRD-03 | Traceability: `direction` is a **required parameter**; at least one of `lotId` / `serialNumber` / `shipmentId`; the query is refused, never silently unbounded | `400` field-level (`WhbReportParameterGuard`) | FR-396 |
| RKP-GRD-04 | Godown statement: `periodId` **or** a `fromDate`/`toDate` pair; the range is ordered; the period exists | `422 DATE_RANGE_INVALID` · `fromDate` / `PERIOD_NOT_FOUND` · `periodId` | FR-386 |
| RKP-GRD-05 | The report's sort key is on its `SqlSortBuilder` whitelist; export reads the same filter map and sort as the grid | unknown key → default sort | FR-384 |
| RKP-GRD-06 | A **filter-aware statistics strip carries no cache name**: no `@Cacheable` on any warehouse statistics method, and no `statistics.*` name registered for one | — | FR-395 |

### 1.4 Unreachable

| ID | Forbidden | Why | Source |
|---|---|---|---|
| RKP-UNR-01 | A KPI computed from a status column and `updated_at` | `updated_at` is overwritten by the next status change; KPIs read the lifecycle timestamps | FR-392 |
| RKP-UNR-02 | A zero rendered for a metric with no target, or a zero variance standing for "no target" | `RKP-T5-14` | FR-470 |
| RKP-UNR-03 | A slotting optimiser behind the utilisation report (it recommends no move) | `RKP-T5-12` is analysis only | FR-471 |
| RKP-UNR-04 | Arithmetic in a report page | every value is a backend column | FR-394 |

## 2. T2 — Action × role × state

| ID | Action | Permission | Source |
|---|---|---|---|
| RKP-T2-01 | Open a report | `wh_rpt_<name>:view` (§5) | FR-384 |
| RKP-T2-02 | Export a report | `wh_rpt_<name>:export` or `ADMIN` | FR-385 |
| RKP-T2-03 | Maintain metric targets | `wh_metric_targets:create` / `:edit` / `:delete` | FR-470 |

## 3. T3 — Time-driven rules

| ID | Rule | Trigger | Changes | Source |
|---|---|---|---|---|
| RKP-T3-01 | KPI snapshot written for the metrics that were proved slow | scheduled job (`WhKpiSnapshotRecorder`, audit `WH_KPI_SNAPSHOT_WRITTEN`), grains `DAY` / `MONTH` | `wh_kpi_snapshots` | FR-394 |
| RKP-T3-02 | **Per-install health signals** (WS-223): movements posted today against a baseline (`warehouse.health.movement_baseline_days`, default 14; no history = a number, never a failure), handovers stuck pending, counts overdue, negative positions, orphaned reservations, unreconciled positions — each `OK` / `WARNING` / `FAILING` against its bound; alerts go in-app, email and push; the SMS channel is never offered while platform's SMS delivery is a stub | each health run (`WhbBaseHealthSignalSource`, `WhHealthSignalSource`) | the signal rows; nothing is scheduled, assigned or resolved (`FR-408`) | FR-398 |

## 4. T4 — Cross-entity effects

None. Reports read; only WS-244 writes, to its own table.

## 5. T5 — Screen contract

Every report: `DynamicDataTable` with its grid id and `preloadedGridPreferences`; backend pagination; Export
(a superset of the visible columns); no Add / Edit (except WS-244). Columns and filters are BUILD-SPEC §7's.
Permission for each is `<grid id>:view` / `:export`.

| ID | Report · route · grid id | Columns | Filters / parameters | Computation rule | Source |
|---|---|---|---|---|---|
| RKP-T5-01 | WS-208 Stock on Hand · `/stock-on-hand` · `wh_rpt_stock_on_hand` | **two tabs** — *by item*: `itemCode`, `itemName`, `categoryName`, `ownerName`, `warehouseName`, `onHand`, `reserved`, `available`, `inTransit`, `onOrder`, `baseUomCode`, `value`; *by location*: the full grain (item, location, lot, serial, LPN, status, owner, duty status) plus quantities | `warehouseId` → `locationId` → `itemId` · `ownerId` · `itemCategoryId` · `stockStatusCode` · `dutyStatus` · `lotId` · `nonZeroOnly` (default true) · `expiringWithinDays` | from `whb_stock_positions` at every dimension | FR-384 |
| RKP-T5-02 | WS-209 Stock Movement Register · `/movement-register` · `wh_rpt_movement_register` | line grain: `occurredAt`, `postingDate`, `movementTypeCode`, `sequenceNo`, `sourceSystem`, `sourceDocumentType`, `sourceDocumentNo`, `reasonCodeName`, `itemCode`, `ownerName`, `locationCode`, `lotCode`, `serialNumber`, `stockStatusCode`, `quantity`, `baseQuantity`, `uomCode`, `unitCost`, `extendedCost`, `actorUserName` | item, warehouse, location, lot, serial, movement type, reason, source system → document type, `occurredFrom`/`To`, `postingDateFrom`/`To`, `periodId`, `itemCategoryId` (`V511431`, P2-18 #128 G1) | opening → in → out → closing per item; drills to the movement and through the display resolver to the source document. **Note (2026-10-26):** the WS-219 drill target — with `periodId` bound the register reads at WS-219's grain (header site, held stock only) and the 365-day `PP-7` cap does not apply; the item group is the STOCKING assignment at `occurred_at` (`AHO-RPT-05`) | FR-385 |
| RKP-T5-03 | WS-210 Godown-wise Stock Statement · `/godown-statement` · `wh_rpt_godown_statement` | `warehouseName`, `itemCategoryName`, `itemCode`, `itemName`, opening / inward / outward / closing quantity and value | `periodId` or `fromDate`/`toDate` · `companyId` → `branchId` → `warehouseId` · `itemCategoryId` · `ownerId` | godown × item group × item; the branch filter reads each movement's site's `REGISTERED` branch at `occurred_at` for opening, inward, outward and closing alike, so a re-registered site splits at the switch | FR-386 |
| RKP-T5-04 | WS-211 Stock Valuation (as-at) · `/stock-valuation` · `wh_rpt_valuation` | `itemCode`, `ownerName`, `warehouseName`, `lotCode`, `quantity`, `unitCost`, `value`, `method`, `currencyCode` | `asAtDate` (required) · `companyId` → `warehouseId` → `itemCategoryId` · `ownerId` · `method` · `valuedOnly` | computed from the ledger and cost layers (value restatements dated by their movement), so the same date gives the same answer next year | FR-387 |
| RKP-T5-05 | WS-212 Stock Ageing · `/stock-ageing` · `wh_rpt_ageing` | `itemCode`, `warehouseName`, `ownerName`, six fixed buckets (0-30 … over 365) each with quantity **and value**, `lastOutwardMovementAt` | `asAtDate` · `warehouseId` → `itemCategoryId` → `itemId` · `ownerId` | age measured from the **last outward movement** as at the date (never-moved stock in the oldest bucket), value per bucket, warehouse split | FR-388 |
| RKP-T5-06 | WS-213 Adjustment Register · `/adjustment-register` · `wh_rpt_adjustment_register` | `postingDate`, `adjustmentNumber`, `reasonCodeName`, `warehouseName`, `itemCode`, `quantity`, `valueImpact`, `actorUserName`, `approvedByName` | `warehouseId` → `reasonCodeId` · `actorUserId` · `approvedBy` · `postingDateFrom`/`To` · `valueImpactMin`/`Max` | every quantity that entered or left without a commercial document, by reason, user and value | FR-389 |
| RKP-T5-07 | WS-214 Count History & Variance · `/count-variance` · `wh_rpt_count_variance` | `countNumber`, `countType`, `warehouseName`, `zoneLocationCode`, `countedByName`, `countedAt`, `itemCode`, `bookQuantity`, `countedQuantity`, `varianceQuantity`, `variancePct`, `varianceValue`, `recountSequence`, `isWithinTolerance` | `warehouseId` → `programId` → `countedBy` · `countType` · `hasVariance` · `countedFrom`/`To` · `includeRecounts` | by counter, including recounts, with the variance value | FR-390 |
| RKP-T5-08 | WS-215 Low & Insufficient Stock · `/low-stock` · `wh_rpt_low_stock` | **three tabs**: *Low stock* (`itemCode`, `warehouseName`, `onHand`, `available`, `reorderPoint`, `safetyStock`, `shortfall`, `suggestedQuantity`) · *Insufficient-stock breaches* · *Replenishment suggestions* | `warehouseId` → `itemCategoryId` → `itemId` · `ownerId` · `belowSafetyOnly` · `occurredFrom`/`To` | shipped reports, not grid filters; read `whb_item_site_settings` and `wh_insufficient_stock_log` | FR-391 |
| RKP-T5-09 | WS-216 Operational KPIs · `/kpis` · `wh_rpt_kpis` | `metricCode`, `metricName`, `warehouseName`, `ownerName`, `periodLabel`, `value`, `unit`, `target`, `variance` | `warehouseId` → `ownerId` → `metricCode` · `periodFrom`/`To` · `granularity` (day / week / month) | dock-to-stock, order cycle time, on-time ship, inventory record accuracy from counts, dwell time and putaway cycle time, each from lifecycle timestamps; the twenty-nine-metric list computed from the ledger | FR-392, FR-394 |
| RKP-T5-10 | WS-217 Stock KPIs · `/stock-kpis` · `wh_rpt_stock_kpis` | `fillRate`, `inventoryTurns`, `trueInventoryTurns`, `obsolescencePct`, `daysSupply` (+ hidden `tracedSharePct`), by `warehouseName` and period | as WS-216 | frozen definitions shown in the metric explainer: **fill rate** = filled demand hits ÷ (filled + no-stock lost-sale hits); **inventory turns** = annualised issue value at cost ÷ average inventory value, with a true-turns variant (`trueInventoryTurns`, a column, not a metric code — no target or variance) excluding non-stocked and special-order issue lines over the same denominator. **Rule (R32 D1, V511432):** non-stocked by `warehouse.reports.true_turns_non_stocked_basis` — `SITE_POLICY` (default: item type `is_stocked=false`, or no item/site row, or reorder point, min and max all NULL; zero counts as configured) or `ITEM_TYPE` (the type flag only); special-order by `warehouse.reports.true_turns_special_order_basis` — `ANY_SPECIAL_LAYER` (default: the whole line when any positive-quantity cost-layer draw traces layer → receipt line → GRN line → PO line → `order_source='SPECIAL_ORDER'`) or `SPECIAL_QUANTITY_SHARE` (only those draws' `value_consumed`); a zero-quantity AVCO residue draw never marks a line; a reversal inherits its issue's classification; an untraceable receipt counts as ordinary and `tracedSharePct` shows the traced share of issue value; under AVCO the split is an allocation, not physical pegging (explainer); **obsolescence** = value with no outward movement in twelve months ÷ total inventory value; **days supply** = on-hand ÷ average daily demand over the row's period; a zero denominator gives a blank | FR-393 |
| RKP-T5-11 | WS-218 Traceability · `/traceability` · `wh_rpt_traceability` | *forward*: lot → every shipment and consignee that received it; *backward*: shipment or serial → supplier lot and receipt | `direction` (required) · `lotId` / `serialNumber` / `shipmentId` (one required) · `warehouseId` · `occurredFrom`/`To` | walks movements and `whb_transformations` for the full retention period (`L-12`) | FR-396 |
| RKP-T5-12 | WS-243 Location Utilisation · `/location-utilisation` · `wh_rpt_location_utilisation` | `locationCode`, `rollupLevel` (location / rack / aisle / zone / site), `warehouseName`, weight / volume / unit / LPN capacity and occupied, `utilisationPct` | `warehouseId` → `zoneLocationId` · `rollupLevel` · `utilisationOver` | occupied against capacity from `whb_locations`' capacity block and `whb_stock_positions`, rolled up the hierarchy | FR-471 *(restored `D-18` item 6, carrier `P8-13`, v3)* — **not built, §10 row 4** |
| RKP-T5-13 | WS-228 Operations Dashboard · `/dashboard` | real-time operations widgets | — | on the platform widget framework, once `widget_definitions.chk_module` admits `warehouse` (BUILD-SPEC §8.1) | FR-399 — **not built, §10 row 5** |
| RKP-T5-14 | WS-244 Metric Targets · `/metric-targets` · `wh_metric_targets` | `metricCode`, `metricName`, `warehouseName`, `ownerName`, `periodGrain`, `targetValue`, `unit`, `effectiveFrom`, `effectiveTo`, audit names | `metricCode` (from `whb_metric_definitions`) · `warehouseId` · `ownerId` · `periodGrain` | a target per metric × optional warehouse × optional owner × period grain, effective-dated; WS-216's `target` / `variance` read the effective row; no row ⇒ blank variance. `whb_metric_definitions` (code, name, unit, definition text key, owning module, direction) has no `CHECK`, so a module registers a metric by `INSERT` | FR-470 |
| RKP-T5-15 | Consolidated valuation across both inventories (WS-222) | per FRD: tagged by source system, the differing-method caveat rendered on the report | — | **WS-222 is REMOVED by `D-16` (`RN-051`, `P7-09`)**; `FR-397` is withdrawn in the FRD (`D-17`; `D-18` item 6 keeps it withdrawn) — this row records the removal only (`RKP-OPEN-01`) | FR-397 |

## 6. Out of scope

WS-219 Stock-to-GL (`accounting-handover`), WS-220 in-transit ageing, WS-221 expiry register,
WS-224 stock as-at (their FRs sit in other sections); trade reports (`trade-reports`); the coexistence
reconciliation (removed, `D-16`). WS-223 health is **in** scope through `RKP-T3-02` only (R31 `F-CB-021`).

## 7. Amendments

| Date | Change |
|---|---|
| 2026-10-23 | v0 derived (R30 `CP-FR-007` row 21) |
| 2026-10-23 | R31: `F-CB-021` (`RKP-T5-15`; WS-223 out of §6); `FR-471` restored (`D-18` item 6: `RKP-T5-12`, §10 row 4, `RKP-OPEN-01`); `RKP-OPEN-02` decided with §9.1 dispositions |

## 8. Invariants and scenarios

`L-12`, `L-14`; `WH-SC-018`, `WH-SC-029`, `WH-SC-040`, `WH-SC-052`, `WH-SC-060`, `WH-SC-113`, `WH-SC-119`,
`WH-SC-283`, `WH-SC-286`, `WH-SC-298`. `FR-397`, `FR-399`, `FR-470`, `FR-471` have no scenario.

## 9. Open rows

| ID | Question | Default |
|---|---|---|
| RKP-OPEN-01 | **CLOSED 2026-10-23.** `FR-397` (the accessories consolidated view, WS-222 REMOVED) and `FR-471` (location utilisation, only owner `P6-02` VOID) | both **withdrawn under `D-16`** in the FRD and plan §2 (`D-17` items 5–6); `P7-09` still removes the served WS-222 (§10 row 6). **Amended R31 (2026-10-23), `D-18` item 6:** `FR-471` is **restored** (carrier `P8-13`, v3 increment); `FR-397` stays withdrawn |
| RKP-OPEN-02 | `FR-394` names a twenty-nine-metric list; the catalogue seeds ten. Which are placed later or refused in writing (`p2-21.md` acceptance)? | **DECIDED R31 (2026-10-23):** the ten seeded metrics stand; every listed metric has a written disposition in §9.1 |

### 9.1 `FR-394` metric dispositions (`RKP-OPEN-02`)

The only enumeration of the list is the prior-art column at `reviews/R6-prior-art-triage.md:308`, which names 21 metric columns of the deleted product's table; the rest of the twenty-nine are not named anywhere in this design set and are **refused until named with a fact source**. The ten seeded codes are `V500048__Create_whb_metric_definitions.sql:159-205`.

| Metric | Disposition |
|---|---|
| `DOCK_TO_STOCK`, `PUTAWAY_CYCLE_TIME`, `ORDER_CYCLE_TIME`, `ON_TIME_SHIP`, `DWELL_TIME`, `INVENTORY_RECORD_ACCURACY`, `FILL_RATE`, `INVENTORY_TURNS`, `OBSOLESCENCE`, `DAYS_SUPPLY` | **seeded** (v1, `p2-21`); prior-art `dock_to_stock_hours_avg`, `putaway_cycle_time_hours`, `inventory_accuracy_pct`, `order_fill_rate_pct` and `dead_stock_pct` are these |
| `location_utilization_pct` | **placed** — WS-243 (`RKP-T5-12`, `FR-471` restored), carrier `P8-13` |
| `total_sku_count`, `total_stock_units`, `total_stock_value_cost` | **refused as metric codes** — stock totals, not rates; read from the stock and valuation reports |
| `total_stock_value_retail` | **refused** — warehouse holds no retail price (`D-16`) |
| `vor_fill_rate_pct`, `vor_response_time_hours` | **refused in v1, no carrier** — `D-16` item 3 renames VOR to line-stop / machine-down, it does not delete it: the facts exist (`order_source='LINE_STOP'`, `V510011:128`, plus the PO lifecycle stamps `:113-118`); re-open with a task (#141 S1 F2) |
| `core_return_rate_pct` | **refused** — dealer-parts core returns leave the warehouse with the dealer adapter (`D-16`) |
| `perfect_order_rate_pct` | **refused** — no damage-free or documentation-accuracy fact exists (R18 `RC-007`) |
| `pick_accuracy_pct` | **refused** — no mis-pick record; scan verification `FR-192` is deferred (`D-17`) |
| `backorder_rate_pct`, `same_day_ship_rate_pct` | **refused as separate codes** — the complement of `FILL_RATE` and a bound on `ORDER_CYCLE_TIME` |
| `shrinkage_value`, `receiving_accuracy_pct`, `return_processing_hours`, `return_to_stock_rate_pct` | **refused in v1, no carrier** — the facts exist (reason-coded write-offs, receipt variances, return timestamps), but no task places them; re-open with a task |

## 10. Code divergences

The FRD rule is kept; the code is what differs.

| # | File:line | FR | Difference |
|---|---|---|---|
| 1 | `warehouse/…/controller/WhPartsKpiController.java:98` | FR-393 | WS-217 is still served at its pre-rename route and permission resource (`wh_rpt_parts_kpis:*`); the rename to Stock KPIs by `P7-11` is pending — **Triage 2026-10-23: P7-REMOVES** — `P7-11` #559 (the rename) — **CLOSED 2026-10-26:** `P7-11` renamed it to `WhStockKpiController` / `wh_rpt_stock_kpis` |
| 2 | `warehouse/…/repository/WhPartsKpiRepositoryCustomImpl.java:134-137` | FR-393 | four metrics only; the true-turns variant (excluding non-stocked and special-order lines) is absent — **Triage 2026-10-23: FIX-CODE** — owner `P2-21` #141 (`FR-393`), reopened; runs after `P7-11` — **CLOSED 2026-10-26** (`P2-21` #141 G1, `V511432`): `trueInventoryTurns` + `tracedSharePct` on WS-217 grid, view and export, rule in `RKP-T5-10` |
| 3 | `warehouse-base/…/db/migration/V500048__Create_whb_metric_definitions.sql:159` | FR-394 | ten metric codes seeded, not twenty-nine — **Triage 2026-10-23: FIX-CODE** — owner `P2-21` #141 (`FR-394`), reopened. reviewer-confirm — **CLOSED 2026-10-26 as DECIDED** (§9 `RKP-OPEN-02`: ten stand, §9.1 gives every other metric a disposition; #141 S1 G2) |
| 4 | — (no controller for `/warehouse/reports/location-utilisation`) | FR-471 | WS-243 not built — `FR-471` restored by `D-18` item 6; carrier `P8-13` (v3 increment) — **Triage 2026-10-23: CARRIED** — `P8-13` #574 |
| 5 | — (no warehouse widget) | FR-399 | WS-228 not built (v3) — **Triage 2026-10-23: CARRIED** — `P6-10` #138 |
| 6 | `warehouse/…/controller/WhConsolidatedValuationController.java:52` | FR-397 | the removed WS-222 is still served (`P7-09` removal pending) — **Triage 2026-10-23: P7-REMOVES** — `P7-09` #557 |
