# 05 — Warehouse Code Gaps for a Service-Parts Planning Module

Scope: `warehouse-base/`, `warehouse/`, `warehouse-3pl/`, `warehouse-india/`. This was a read-only audit on 2026-09-30.

Path prefixes used below:
- `WB` = `warehouse-base/backend/src/main/resources/db/migration`
- `WH` = `warehouse/backend/src/main/resources/db/migration`
- `WBJ` = `warehouse-base/backend/src/main/java/ai/warehousebase`
- `WHJ` = `warehouse/backend/src/main/java/ai/warehouse`

Severity is judged for the future planning module:
- **BLOCKER**: planning would be wrong or impossible without the fix.
- **MAJOR**: planning quality or autopilot safety would suffer materially.
- **MINOR**: a hygiene or edge case.

Limits of this audit:
- The repo has no literal `#168` or `#182` strings. Those issue references are mapped here by subject only.
- Timezone rules are mixed across the codebase. Recent commits (a926b11876, d32bec2190) moved report bucketing to the *user* zone (`WhbStockAgeingService.java:72`), while demand history and KPI snapshots use the site zone.
- Outbox detail:
  - At-least-once delivery, in cursor order.
  - A DEAD event blocks its subscriber (head-of-line) (`WhbOutboxDeliveryStep.java`).
  - 17 event types, with no demand, PO-line or transfer-line events (`WB/V500040:108-128`).
- The job lock is the `whb_job_runs` unique index, not ShedLock (`WB/V501011:142-143`).

---

## 0. Top 12 (read these first)

| # | ID | Severity | One line |
|---|----|----------|----------|
| 1 | DH-01 | BLOCKER | Supplier-return (VENDOR_RETURN) despatches are counted as customer demand. |
| 2 | DH-02 | BLOCKER | The warranty/internal exclusion never fires on the main outbound path: despatch posts with no reason code. |
| 3 | DH-03 | BLOCKER | Demand history has no owner dimension, so 3PL-client issues inflate the house site's demand. |
| 4 | DH-04 | BLOCKER | Monthly buckets only, by issue/posting date. There is no order-date demand, no daily/weekly series and no order-line identity. |
| 5 | DH-05 | MAJOR→BLOCKER for migration | A live posting into an imported (`is_migrated`) month is later wiped by a re-import or import reversal. |
| 6 | LS-01 | BLOCKER | The guard lost-sale recorder (`WhLostSaleRecorder`) has zero callers. Only manual capture feeds lost sales. |
| 7 | RE-01 | MAJOR | The replenishment engine's "on hand" includes QC_HOLD/DAMAGED/QUARANTINE/EXPIRED stock, so it under-orders. |
| 8 | SUP-01 | BLOCKER | On-order supply is not time-phased: no due date in the port, and the engine reads all open POs regardless of date. |
| 9 | SS-01 | BLOCKER | Supersession `MERGE_DEMAND` is stored but never read. `MERGE_STOCK` is a hard-coded refusal. No planning path uses the chain. |
| 10 | NW-01 | BLOCKER | No network model: no parent/child site, no "replenished-from" relation, no transfer lanes or lanes' lead times, no van locations. |
| 11 | LT-01 | MAJOR | Actual lead time is not stored per receipt. It is computed per supplier from PO header date to the *first* GRN in UTC, with no variability written back. |
| 12 | RE-05 | MAJOR | A PROPOSED suggestion never expires, and an item with one is excluded from every later run for ever. |

---

## 1. Demand history (`wh_demand_history`, `WhDemandHistoryRecorder`)

**DH-01: Supplier returns counted as demand (BLOCKER)**
- Evidence:
  - The recorder counts any forward movement whose direction is `OUT`, except `TRANSFER_DEPART` (`WHJ/service/whdemandhistory/WhDemandHistoryRecorder.java:71-82`).
  - A VENDOR_RETURN demand order is despatched as `ISSUE` to the SUPPLIER virtual location (`WHJ/service/whpicktask/WhDespatchService.java:64-66, 80, 96, 242-247`).
  - The code base itself treats these as "not a sale" for landed cost: `NON_SALE_DEMAND_TYPES = VENDOR_RETURN, TRANSFER` (`WHJ/service/whlandedcost/WhLandedCostPostingService.java:81-85`).
- Problem: every return to a supplier raises that part's demand hits and quantity, and so its reorder point and forecast.
- Required change: pass the demand type or source document type in the `Effect`, or stamp a non-demand reason on VENDOR_RETURN despatch. Exclude it in the recorder, and backfill or correct history already posted.

**DH-02: Reason-based exclusion is inert on despatch (BLOCKER)**
- Evidence:
  - Despatch builds `WhbMovementPostCommand` with `reasonCodeId = null` (`WhDespatchService.java:242-247`; the constructor field order is at `WBJ/service/ledger/writer/WhbMovementPostCommand.java:27-48`).
  - Relief lines also carry no reason (`WHJ/service/whpicktask/WhPickTaskWriter.java:585-593`).
  - The recorder treats "no reason" as ordinary demand (`WhDemandHistoryRecorder.java:30-33, 131-134`).
  - `affects_demand_history` defaults to `true` (`WB/V500004__Create_whb_reason_codes.sql:65`).
- Problem: warranty issues, internal consumption, goodwill and JOB_ISSUE-for-warranty cannot be excluded on the path that carries almost all demand. The `affects_demand_history` exclusion only works for adjustments and scrap.
- Required change:
  - Carry the demand-order line's classification (demand type, warranty flag, charge type, customer class) into the ledger line or the `Effect`.
  - Add a demand-classification catalogue (e.g. `counts_as_demand` per demand type) and a per-line warranty/internal flag on `wh_demand_order_lines`.
  - Seed the warranty reason: the contract carries this as RPL-C-03 (`warehouse/docs/contracts/replenishment.contract.md:61-65`).

**DH-03: No owner (HOUSE vs 3PL) dimension (BLOCKER)**
- Evidence:
  - `WhbMovementEffectRecorder.Line(itemId, warehouseId, virtualLocation, baseQuantity, reasonCodeId)` has no owner (`WBJ/service/ledger/writer/WhbMovementEffectRecorder.java:53-57`).
  - The table key is `(item_id, warehouse_id, period_year_month)` (`WH/V510070...sql:292`).
  - The replenishment engine, by contrast, plans HOUSE stock only (`WhReplenishmentEngine.java:44-46, 137-141`).
- Problem: on a mixed 3PL/house site, client issues are counted as house demand, while the supply side excludes client stock. The two sides are inconsistent.
- Required change: add `owner_id` (and `company_id`) to the Effect line and to the demand-history key, or filter to HOUSE owners in the recorder.

**DH-04: Granularity and demand semantics (BLOCKER)**
- Evidence:
  - The period is YYYYMM text only (`WhDemandHistory.java:58-60`; `WH/V510070...sql:293`).
  - The period comes from the posting date of the stock movement, i.e. ship/issue date, not order date (`WhDemandHistoryRecorder.java:146-152`).
  - The `Effect` carries no source document or line and no customer (`WhbMovementEffectRecorder.java:35-44`), although the post command has `sourceDocumentType/Id/LineNo`.
  - Hits are counted "one per item per movement" (`WhDemandHistoryRecorder.java:28-29, 80`), so a line shipped in three partial despatches counts as 3 hits.
  - Demand orders do hold `order_date`, `original_item_id` (substitution), `backordered_quantity` and `cancelled_quantity` (`WHJ/entity/WhDemandOrder.java:174`; `WhDemandOrderLine.java:99-138`), but none of it reaches demand history.
- Problem: forecasting needs:
  - demand by requested/order date, not fill date;
  - weekly or daily buckets for intermittent-demand methods (Croston/SBA/bootstrapping);
  - hits per order line;
  - requested-part vs supplied-part (supersession/substitution);
  - customer and channel for segmentation.

  Backorders shift demand into a later month, so stock-outs distort the history.
- Required change: add a line-level demand-event fact table (append-only, partitioned). One row per demand-order line event: ordered, amended, cancelled, backordered, shipped, lost. It should carry order date, requested date, requested item, supplied item, customer, channel, owner, demand type, warranty flag, quantity in base UoM, and source ids. Derive buckets from it; the monthly table becomes a projection.

**DH-05: Migrated and live rows collide (MAJOR; BLOCKER at go-live)**
- Evidence:
  - The posting upsert does not touch `is_migrated` (`WHJ/repository/WhDemandHistoryRepositoryCustomImpl.java:93-107`).
  - The import upsert overwrites absolute values `WHERE is_migrated = true` (:263-271).
  - The import reversal restores or deletes migrated rows (:277-298).
  - The import refuses only *future* periods, so the current (go-live) month is accepted (`WhDemandHistoryImportHandler.java` class Javadoc).
- Problem: import month M, then postings in month M add to that row. A corrected re-import, or an import reversal, overwrites or deletes the live postings. The row also stays flagged `is_migrated = true`, so reports cannot separate measured from imported quantity.
- Required change: keep migrated and observed quantities in separate columns or rows, and refuse import of the current open month (or months with observed postings).

**DH-06: Customer returns and RTO never net demand (MAJOR)**
- Evidence: the recorder ignores all forward `IN` movements (`WhDemandHistoryRecorder.java:72`). `RETURN_RECEIPT` and `RTO_RECEIPT` are IN (`WB/V500003...sql` seeds). An RTO means the customer never took delivery.
- Problem: failed deliveries and customer returns stay counted as demand, which inflates the forecast.
- Required change: add a configurable netting policy per return reason (net back into the original period, or record as a separate "returns" series).

**DH-07: Drop-ship and kitting demand invisible (MAJOR)**
- Evidence:
  - `DROP_SHIP` is `INTERNAL` direction, virtual to virtual (`WH/V510200__Create_wh_cross_dock_plans.sql:451-453`).
  - Work-order movements post under `work_order_type` (`WHJ/service/whworkorder/WhWorkOrderPostingService.java:226-228`) and do not count as outbound demand.
- Problem:
  - Demand met by drop-ship is lost to the forecast, so the stock/no-stock decision is blind to it.
  - Component (dependent) demand from kits is not captured.
- Required change: emit demand events from demand-order lines, not only from stock movements (see DH-04). Add BOM/kit explosion for dependent demand.

**DH-08: Floored subtraction hides inconsistencies (MINOR)**
- Evidence: `GREATEST(hit_count - :hits, 0)` (`WhDemandHistoryRepositoryCustomImpl.java:111-124`). One hit is subtracted per reversal, even when the original counted hits for several items or sites.
- Problem: silent clamping masks double reversals or migrated-vs-live mismatch.
- Required change: log or raise a drift finding when clamping occurs.

**DH-09: UoM and timezone (MINOR)**
- Evidence:
  - Posting uses `baseQuantity` (fine), but the import has no UoM column and assumes base (`WhDemandHistoryImportHandler.java` COLUMN_* constants).
  - The period falls back to the site timezone, else UTC, with a warn on a bad zone (`WhDemandHistoryRecorder.java:154-166`).
  - Supplier lead-time dates use UTC instead (LT-01).
- Required change: add a UoM column to the import, and use one site-timezone bucketing rule everywhere.

**DH-10: Performance and indexes (MINOR)**
- Evidence: indexes are `(warehouse_id, period)`, `(item_id)` and `(period DESC)` (`WH/V510070...sql:314-317`). The table is not partitioned.
- Required change: add `(item_id, warehouse_id, period)`. It is already unique, so fine. Add an owner/company dimension index once DH-03 is done.

## 2. Lost sales

**LS-01: Guard refusal capture is unwired (BLOCKER)**
- Evidence:
  - `WhLostSaleRecorder.recordRefusal` (`WHJ/service/whdemandhistory/WhLostSaleRecorder.java:56-86`) has no caller anywhere in the repo.
  - The contract carries this as RPL-C-02, "guard half of lost sales left to adapters (P2-25/P2-26)" (`warehouse/docs/contracts/replenishment.contract.md:61-65`).
- Problem: counter and job-issue refusals are never recorded, so lost-sales history depends on manual discipline. Censored-demand correction becomes impossible.
- Required change: wire refusals at allocation failure, short-pick, backorder auto-cancel, and counter/job-card adapters.

**LS-02: Backorder auto-cancel, short-pick and order cancel for no-stock are not lost sales (MAJOR)**
- Evidence:
  - `WhBackorderHorizonSweeper` moves backordered to cancelled and records nothing else (`WHJ/service/whdemandorder/WhBackorderHorizonSweeper.java` Javadoc).
  - The short pick moves quantity to backordered (`WhDemandOrderQuantityRules.java:127`).
- Required change: treat a cancel-for-stock-out as a lost-sale event, classified by reason.

**LS-03: Requested quantity, not shortfall, rolls into demand (MAJOR)**
- Evidence: manual capture adds `requestedQuantity` even when `available > 0` (`WHJ/service/WhInsufficientStockLogService.java:156-185`). The guard path does the same (`WhLostSaleRecorder.java:81`).
- Problem: if a partial is also fulfilled, demand is double-counted (issued quantity plus the full requested quantity).
- Required change: record `requested − supplied` as lost, or store both and let planning decide.

**LS-04: No void or correction of a captured lost sale (MINOR)**
- Evidence: `WhInsufficientStockLogService` exposes capture only (`:146`), with no delete or void.
- Required change: add a reversible capture that subtracts from `wh_demand_history`.

**LS-05: Not-catalogued lost sales cannot feed item introduction (MINOR)**
- Evidence: `item_description` is free text only (`WH/V510070...sql` §3a).
- Required change: add a later link to a catalogued item, and roll it into demand once the item is created.

**LS-06: Transfer refusals are logged at the source site (MINOR)**
- Evidence: `recordRefusedDemand` logs at `transfer.getSourceWarehouseId()` with `isLostSale = false` (`WHJ/service/WhTransferOrderService.java:811-830`).
- Problem: this is fine for fill-rate. Multi-echelon planning needs the destination's unmet requirement as an explicit dependent-demand record.

## 3. Stock truth for planning

**ST-01: Engine on-hand includes unusable statuses (MAJOR, defect)**
- Evidence:
  - Site figures take `row[2]` of `findAvailabilityPositions` (`WhReplenishmentEngine.java:406-409`). That column is "on hand (physical … any status)" (`WBJ/repository/WhbAllocationRepository.java:216-221`).
  - The sister path correctly uses `row[3]`, allocatable (`WhReplenishmentEngine.java:379-381`).
  - The Javadoc claims only virtual and in-transit are excluded (:44-46).
- Problem: QC_HOLD, DAMAGED, QUARANTINE, EXPIRED, BLOCKED, CORE_UNGRADED and RETURNED stock counts as available, so the engine under-orders. Status flags are in `WB/V500005...sql:80-88, 135-143`.
- Required change: use allocatable or ATP stock for position. Expose a separate "recoverable" bucket (QC/RETURNED/CORE_UNGRADED) for planning.

**ST-02: UTC date used for expiry-aware reads (MINOR, defect)**
- Evidence: the own-site read passes `now.atZoneSameInstant(UTC).toLocalDate()` (`WhReplenishmentEngine.java:407`). The sister path uses the site day (:348).
- Required change: use the site timezone for both.

**ST-03: As-at reconstruction is costly and business-time only (MAJOR)**
- Evidence:
  - As-at sums all ledger lines with `occurred_at <= at`: one site per call, no checkpoint (`WBJ/service/ledger/WhbStockAsAtQueryService.java:33-62`; `WBJ/controller/WhbStockAsAtController.java:36-43`).
  - Backdating is allowed (`WB/V500030...sql:282-283`), so past answers change after the fact, and there is no `recorded_at <= knownAt` filter.
  - `ledgerSequenceNo` is the current maximum, not the maximum at `at` (:61-62).
  - The daily snapshots `whb_stock_position_snapshots` (`WB/V500045...sql:47-111`) cannot be backfilled; history starts at job switch-on (`warehouse/docs/runbooks/opening-stock-cutover.md:48`).
  - Stock periods carry no balances (`WB/V500019...sql:80-125`).
- Problem: time-travel scenarios and "what did the planner know then" need a bitemporal view, and must reconstruct efficiently across many items and sites.
- Required change:
  - Add a bitemporal filter.
  - Add period or daily closing balances, and a snapshot-backfill-from-ledger tool.
  - Add a multi-site, multi-item as-at API.
  - Add a lines index on `(item, warehouse, occurred_at)`, or a `warehouse_id` column on lines. Today lines have no `warehouse_id` (`WB/V500030...sql:315-411`, indexes :416-424).

**ST-04: In-transit attributed to the sender (MAJOR)**
- Evidence: in-transit is a transit location under the source site (`WB/V500013...sql:36-44`). Availability groups it by the position's warehouse (`WhbAllocationRepository.java:227-230`). The engine separately adds open inbound transfer lines as on-order (`WhReplenishmentRunRepositoryCustomImpl.java:215-233`).
- Problem: multi-echelon planning must see in-transit as dated inbound supply at the destination, not as sender stock.

**ST-05: Reservations and demand lines are not time-phased (MAJOR)**
- Evidence:
  - `whb_reservations` has no required-by date; `expires_at` is a SOFT TTL (`WB/V500033...sql:346-419`).
  - Demand-order lines have no dates; only the header has `promised_ship_at` / `promised_deliver_at` (`WH/V510040...sql:105-106, 278`).
- Required change: add a need-by date per line and per reservation.

## 4. Supply: on-order and transfers

**SUP-01: No time-phased supply (BLOCKER)**
- Evidence:
  - `WhbOnOrderSource.OnOrder(itemId, warehouseId, uomCode, quantity)` has no date (`WBJ/service/allocation/WhbOnOrderSource.java:21, 35-37`).
  - The engine passes `expectedBy = null`, so it reads all open supply regardless of arrival (`WhReplenishmentEngine.java:415-417`).
  - Draft/submitted POs from converted suggestions are added undated (:427-437).
- Problem: supply arriving after the lead-time horizon is treated as covering current need. There is no bucketed projection, so time-phased netting is impossible.
- Required change: return dated supply lines (PO line, ASN ETA, transfer ETA), and add a projected-available-balance service.

**SUP-02: PO lines lack confirmed dates and quantities (MAJOR)**
- Evidence:
  - PO lines have `expected_delivery_date` only (`WH/V510011...sql:202-250`, :213). The header has `acknowledged_at` as a timestamp only (:113-118).
  - There are no schedule lines and no date-change history.
  - ASN `expected_arrival_at` (`WH/V510012...sql:91`) is not used by on-order.
- Required change: add a supplier-confirmed date and quantity, schedule lines, a date-change audit, and an ASN-ETA override.

**SUP-03: Open transfers (MINOR)**
- Evidence: `expected_arrival_date` is entered by hand (`WH/V510031...sql:121-122`), with no lane derivation. There is an overdue-arrival job (`WBJ/service/jobs/WhbJobCatalogue.java:136`).

## 5. Lead time

**LT-01: Actual lead time is not captured per receipt (MAJOR)**
- Evidence: `WhSupplierLeadTimeQueryService` computes whole days from PO header `order_date` to the first receipt's UTC date. It works per supplier, not per item, excludes VOR/EMERGENCY, and returns avg/min/max only (`WHJ/service/whreplenishment/WhSupplierLeadTimeQueryService.java:24-35, 96-120`). It is API-only with no screen (RPL-C-04).
- Problem:
  - There is no item-level or line-level lead time, and later partial receipts are ignored.
  - There is no standard deviation, and the site timezone is not used.
  - Nothing is written back to settings.
- Required change: add a receipt-line lead-time fact (PO line → GRN line, quantity-weighted), with item × supplier × site statistics (mean, σ, P90) on a schedule.

**LT-02: Two competing static lead-time fields (MAJOR)**
- Evidence: `whb_item_site_settings.lead_time_days` and `whb_item_supplier_sources.lead_time_days` (`WB/V500050...sql:108, 164`). The DATED-OBLIGATION-REGISTER calls them "planning inputs" and says no job reads them (`warehouse-base/docs/DATED-OBLIGATION-REGISTER.md:86`). The engine only prints lead time in its note (`WhReplenishmentEngine.java:276-277`).
- Required change: define precedence, and use lead time in the reorder-point maths.

**LT-03: Supplier sources are not site-scoped (MAJOR)**
- Evidence: no `warehouse_id`, deferred to V500077 (`WB/V500050...sql:41-42`), and V500077 does not exist. The supplier source query is item-global (`WhReplenishmentRunRepositoryCustomImpl.java:299-311`). There is no price (FR-119) and no purchase UoM, so MOQ and multiple are applied in the base unit (`WhReplenishmentEngine.java:257-270`).
- Required change: add a site/company-scoped source, a purchase UoM, and a price/contract reference.

**LT-04: No transfer-lane transit time (BLOCKER for multi-echelon)**
- Evidence: the only transit days are on outbound carrier services, `transit_days_min/max` (`WH/V510044...sql:110-111`).
- Required change: see NW-01.

## 6. Item × site settings, classes, lifecycle

**IS-01: Manual-only, no source/authority, no history, no effective dating (BLOCKER for autopilot)**
- Evidence:
  - `whb_item_site_settings` has one row per item × site with `version` and `updated_by` only (`WB/V500050...sql:98-145`).
  - Writes come only from CRUD in `WBJ/service/WhbItemSiteSettingService.java:124-185` (audit log line plus `trackChanges`).
  - There is no history table, no `source` (MANUAL / PLANNING / IMPORT) field, no `locked/override_until` flag, and no `effective_from`.
- Problem: planning autopilot would overwrite buyer overrides silently. There is no as-at view of parameters for scenario or time-travel replay.
- Required change: add a parameter-version table (effective-dated, with source and approval), override locks, and planning-owned fields separate from manual ones.

**IS-02: ABC/XYZ/velocity are never computed (MAJOR)**
- Evidence:
  - The columns exist (`WB/V500050...sql:109-115`), and the comment says "ABC recomputed by v1.1 job (FR-463); XYZ/velocity by P6-02".
  - V500069 (`previous_abc_class`, `abc_computed_at`) does not exist, and no job exists in `WhbJobCatalogue`.
- Required change: add a classification job with history.

**IS-03: Missing planning attributes (MAJOR)**
- Absent from both `whb_item_site_settings` and `whb_items`:
  - criticality / service-level target, lifecycle stage (NEW / ACTIVE / PHASE_OUT / OBSOLETE);
  - stock/no-stock (stocking) flag, planner and buyer assignment, planning method;
  - forecast model and parameters, review period, order cost, holding-cost rate.
- VED/HML free-text classes exist, but nothing reads them.
- Shelf life lives in `near_expiry_days` and `whb_shelf_life` only.
- Required change: add a planning-parameter entity in the planning module, keyed by item × site × owner.

**IS-04: Candidate filter is naive (MAJOR)**
- Evidence: the candidate query requires `reorder_point IS NOT NULL AND i.is_active`, and excludes items with a PROPOSED suggestion (`WhReplenishmentRunRepositoryCustomImpl.java:133-155`).
- Problem: it does not exclude superseded predecessors, no-stock items or phase-out items.

## 7. Supersession

**SS-01: Supersession is not used by planning or demand (BLOCKER)**
- Evidence:
  - `MERGE_DEMAND` exists as a value only (`WBJ/entity/WhbItemSupersession.java:46-48, 83-86`; `WB/V500050...sql` CHECK). Nothing reads it; zero references in `WHJ` (grep).
  - `mergeStock` always throws `MERGE_STOCK_POSTING_UNAVAILABLE`, although the ledger writer exists (`WBJ/service/WhbItemSupersessionService.java:196-208`).
  - The chain resolver resolves one item at a time (`WBJ/service/whbitemsupersession/WhbSupersessionChainResolver.java:24-54`, `MAX_STEPS = 100`). There is no batch API, which is N+1 at planning scale.
  - Reservation allocation can pick a superseding item (`warehouse-base/docs/contracts/reservation.contract.md:129`). That substitution is not reflected in demand (see DH-04, `original_item_id`).
- Required change:
  - Add a supersession-aware demand roll-up that applies `quantity_ratio`, effective dates and chain order.
  - Support `PARTIAL` (one-to-many) and `INTERCHANGE` semantics.
  - Add a batch chain resolver, and implement MERGE_STOCK through the writer.
  - Stop proposing replenishment for superseded predecessors.

**SS-02: Model limits (MAJOR)**
- Evidence:
  - The unique key is `(predecessor, successor, effective_date)`, with `chain_sequence` choosing among several live links (resolver Javadoc :29-30).
  - There is no kit/one-to-many quantity per successor beyond one ratio, and no use-up/"sell existing stock first" flag.
  - The effective window is applied on read only (`DATED-OBLIGATION-REGISTER.md:101`).
- Required change: add a use-up policy and a phase-in/out date per site.

**SS-03: No tests (MAJOR)**
- There are no tests for the chain resolver, the cycle trigger, MERGE_STOCK or MERGE_DEMAND (see §13).

## 8. Location and network model *(spot-checked)*

**NW-01: No supply network (BLOCKER)**
- Evidence:
  - A grep of `WB` migrations finds no `parent_warehouse_id`, "replenish from" or supplying-site column; `source_warehouse_id` exists only on transfers and suggestions.
  - The "sister" concept is any site of a different registered branch under the same operator company (`WhReplenishmentEngine.java:57-64`; `WH/V510070...sql:264-266`).
  - "Sister-branch-first preference is later work (FR-254, P6)" (`WH/V510070...sql:265-266`).
- Problem: there is no DC→branch→van hierarchy, no lanes and no lane lead times, so multi-echelon planning is impossible.
- Required change: add a network table (source site, destination site, priority, transit days mean/σ, calendar, cost) and an echelon role per site.

**NW-02: Sister transfers can over-draw (MAJOR)**
- Evidence: sister surplus = allocatable − open holds (`WhReplenishmentEngine.java:375-389`). REQUESTED-but-not-despatched outbound transfers to other sites are not subtracted, and runs are per site (`uk_wh_replenishment_runs_one_running` per warehouse, `WH/V510070...sql` runs indexes).
- Problem: two branches' runs can draw on the same sister surplus. There is also no lane cost or time comparison with purchasing.

**NW-03: Van stock is a location, not a plannable node (MAJOR)**
- Evidence:
  - The location types VEHICLE ("van or truck stock, held by its custodian"), MOBILE and TRAILER are seeded (`WB/V500006__…sql:124-127`).
  - Custody is dated, with one CUSTODIAN at a time enforced by an EXCLUDE constraint (`WB/V500013…sql:260-290`; `WBJ/service/WhbLocationService.java:429-473`).
  - Van locations sit inside a parent site. `whb_item_site_settings` is item × site, so vans get no replenishment run; only the pick-face location min/max ladder applies (`pick-face-replenishment.contract.md:70`).
- Required change: model the van as a site or node (or add location-level planning plus a van-restock flow), with a technician link.

**NW-04: Calendars not used in planning maths (MAJOR)**
- Evidence:
  - The tables `wh_working_calendars`, `_days` and `_assignments` are assigned per site and owner (`WH/V510202…sql:38-41, 69-166`). Holidays come from the REGISTERED branch's platform calendar (`WHJ/service/WhWorkingCalendarService.java:95-112`).
  - The API is `resolve`, `promiseShipBy`, `addWorkingHours` and `workingTime` (:135-262), with no add-working-days.
  - Only three consumers use it: demand-order promise, 3PL SLA and NDR.
  - Replenishment, transfer ETA, PO due dates and lead-time maths ignore it. There are no receiving-day or supplier calendars.

**NW-05: Sites are flat; the branch junction is not a supply relation (MAJOR)**
- Evidence: `whb_warehouses` has no parent (`WB/V500012…sql:223-267`). `whb_warehouse_branches` roles are REGISTERED, SERVING, FULFILMENT and RETURNS (`V500012:133-136, 295-310`). Transfer ETA is typed by the user (`WHJ/service/WhTransferOrderService.java:213, 261`).

## 9. Replenishment engine (`WhReplenishmentEngine`)

**RE-01**: see ST-01 (on-hand includes unusable stock).

**RE-02: Rule is static ROP/min-max; demand history is never read (BLOCKER)**
- Evidence: position = on hand − allocated + on order. The engine orders up to max, else ROP + ROQ, else ROP (`WhReplenishmentEngine.java:53-55, 223-283`). "Computed best stocking level is P6-02, v3" (:66). Safety stock is used only as a sister minimum (`WhReplenishmentRunRepositoryCustomImpl.java:237-246`).
- Required change: the planning module must own the parameter computation. Keep the engine as the executor, or replace it.

**RE-03: Suggestion data is thin for autopilot (MAJOR)**
- Evidence: suggestion columns are `on_hand`, `allocated`, `on_order`, `reorder_point`, quantity, cost, source and a `basis_note` free-text field (`WH/V510070...sql:180-251`). Statuses are PROPOSED / ACCEPTED / CONVERTED / REJECTED with no CHECK (:261-263).
- Problem: there is no structured explanation (forecast, SS, LT, service level), no required-by date, no confidence score and no auto-approval policy or threshold. `run_by` must be NULL for SCHEDULED (:119-120), so there is no system actor for auto-accept.
- Required change: add structured inputs per suggestion, a need-by date, and an auto-approve policy with audit.

**RE-04: Per-site, serial runs (MINOR→MAJOR at scale)**
- Evidence: one RUNNING run per site (unique partial index); `CHUNK = 200` reads. The scheduled job runs each quarter hour per site (`WhbJobCatalogue.java:161-168`). Sites with no ledger get no scheduled run (RPL-C-05). Each sister's owners are fetched per sister (`WhReplenishmentEngine.java:341-344`).
- Required change: network-wide batch runs, performance tests at around 100k SKUs × N sites.

**RE-05: PROPOSED suggestions never expire (MAJOR)**
- Evidence: suggestion statuses have no EXPIRED/SUPERSEDED (`WHJ/entity/WhReplenishmentSuggestion.java:56-60`). The candidate query excludes items with any PROPOSED suggestion (`WhReplenishmentRunRepositoryCustomImpl.java:~142-145`).
- Problem: an ignored suggestion freezes that item out of replenishment indefinitely, and its figures go stale.
- Required change: supersede prior PROPOSED suggestions on each run, or add an expiry.

**RE-06: Unit cost and value gaps (MINOR)**
- Evidence: unit cost is the weighted average of *open* cost layers at the site (`WhReplenishmentRunRepositoryCustomImpl.java:275-295`). With no stock, value is null and the run total understates (`WhReplenishmentEngine.java:178-183`).
- Required change: fall back to the last PO price, standard or replacement cost.

**RE-07: Transfer acceptance status (MINOR)**
- Evidence: the contract says TRANSFER accept is refused (RPL-C-01), but the service now accepts TRANSFER (`WHJ/service/WhReplenishmentSuggestionService.java:255-319`). The contract is stale ("DERIVED — ratify before trusting", `replenishment.contract.md:11-12`).

## 10. Costing inputs

**CO-01: No planning cost basis (MAJOR)**
- Evidence:
  - Valuation is AVCO or FIFO; STANDARD is v1.1 (`WB/V500021...sql:165-233`).
  - `whb_items` forbids cost columns (`WB/V500015...sql:808-811`).
  - Supplier sources have no price (`WB/V500050...sql:41`).
  - The cost fallback is last receipt, then (absent) standard, then zero (`WBJ/service/costing/WhbCostingEngine.java:639`).
  - 3PL stock is `ZERO_BAILMENT` (`WB/V500030...sql:410`).
- Required change: add a planning/replacement cost per item × site, holding-cost rate, ordering cost per supplier or lane, and a currency conversion policy for investment roll-ups.

## 11. Returns, repair, cores, warranty *(spot-checked)*

**RR-01: Repair and core only scaffolded, with no lifecycle (BLOCKER for the repair/cores scope)**

What exists:
- `CORE` item type, "deposit until graded" (`WB/V500008:95`).
- `CORE_UNGRADED` status (`WB/V500005:141`).
- `whb_serials.linked_core_serial_id` and warranty start/end dates (`WB/V500018:359-373`).
- `whb_condition_codes.is_repairable` (`WB/V500005:162, 208-213`).
- The `REFURB` and `RTV` dispositions (`WB/V500010:362-370`), and return types WARRANTY and EXCHANGE (`V500010:154-163`).
- `wh_return_gradings` as evidence only, moving no stock (`WH/V510210:66-101`).

What does not work end to end:
- Return receipt in v1 posts only `RESTOCK_SELLABLE`, `QUARANTINE` and `SCRAP` (`WHJ/service/whreturnreceipt/WhReturnReceiptValidationService.java:96`). The UI says refurbish, repack and RTV come "later" (`warehouse/frontend/src/app/dashboard/warehouse/inbound/rmas/page.tsx:383`).
- There are no repair orders, no core deposit amount, no core-return-due tracker, no exchange-unit logic, and no repair TAT or yield.
- Supplier claim types have no WARRANTY (`WH/V510216:107-108`).
- The India REPAIR challan purpose (`warehouse-india/.../V540020:53, 100`) is the only outbound repair loop.

Required change: add a repair loop (unserviceable → in repair → serviceable pools), core obligations per sale, repair yield and TAT statistics, and warranty claims.

**RR-02: Warranty only as a reason code (MAJOR)**
- Evidence: the `WARRANTY_RETURN` reason exists in context `RETURN` (`WB/V500004...sql:118-145`), and the warranty issue reason seed is still carried (RPL-C-03). See also DH-02.

## 12. Events, jobs, imports

**EV-01: Useful outbox, but no planning payloads (MAJOR)** *(spot-checked)*
- Evidence: the ledger writer emits outbox events with company, site, sequence, lineage and actor (`WBJ/service/ledger/writer/WhbStockLedgerWriter.java:1047-1055`). The outbox publisher runs every 10 s (`WhbJobCatalogue.java:86`).
- Problem: there are no demand-order-line events (ordered / cancelled / backordered) and no PO date-change events that planning could consume incrementally. The in-process `WhbMovementEffectRecorder` is synchronous, and "a recorder that throws fails the post" (`WhbMovementEffectRecorder.java:20-26`). A planning recorder added there puts planning failures on the posting critical path.
- Required change: planning should consume the outbox asynchronously, not the effect port. Add demand-line and supply-date events.

**EV-02: Job framework is fine (MINOR)**
- Evidence: `WhbJobCatalogue` descriptors carry cadence, scope and a missed-run policy (`WBJ/service/jobs/WhbJobCatalogue.java:60-230`).
- Planning jobs would register there. A demand-history backfill or rebuild job from the ledger does not exist: history is "never a nightly recompute" (`WH/V510070...sql:302-306`), so any fix to DH-01, DH-02 or DH-03 needs a one-off rebuild tool.

**EV-03: Import framework (MINOR)**
- Evidence: there is an import-kind seam with handlers (e.g. `WhDemandHistoryImportHandler`, IMPORT_KIND `DEMAND_HISTORY`). There is no import kind for item-site planning parameters or supplier lead times.

## 13. Performance and scale (#182 subject)

**PF-01: Whole-ledger scans (MAJOR)**
- `WHJ/repository/WhStockAgeingRepositoryCustomImpl.java`:
  - :51-56 and :174-188 say outright there is no lower bound, filtering only `occurred_at < :asAtInstant`.
  - The filters use `(CAST(:x AS UUID) IS NULL OR …)`, a generic-plan pattern that likely defeats partition pruning.
  - One screen load runs the CTE 4–5 times (:404-461).
  - It has per-row `LATERAL` lookups (:145-164).
- The same problem appears in `WhPartsKpiRepositoryCustomImpl.java:82-84, 271`, `WhStockAsAtRepositoryCustomImpl.java:104` and `WhinStockByMrpRepositoryCustomImpl.java:29`.
- `WhReportsComputeFromLedgerTest` forbids using positions or snapshots in these reports, which blocks the obvious fix.

**PF-02: Ledger indexes for time series (MAJOR)**
- Evidence: the ledger is partitioned monthly by `occurred_at` (`WB/V500030...sql:68-76, 288, 411`). Lines are indexed `(item_id, occurred_at)` and `(owner, item, occurred_at)`, with no warehouse on lines (:416-424).
- Required change: add a planning-side demand fact table (DH-04) instead of scanning the ledger. If ledger reads remain, add `warehouse_id` to lines or a covering index.

**PF-03: Partition detach/archive deferred to P6-01 (MINOR)**
- Evidence: `WB/V500030...sql:76`; `WhbRetentionResolver.java:20, 77`.
- Problem: long demand histories depend on the archive keeping data queryable.

## 14. Data quality, multi-company, timezones

**DQ-01: Company and owner scoping is inconsistent across planning inputs (MAJOR)**

| Input | Scope | Evidence |
|---|---|---|
| Demand history | item × site | DH-03 |
| Supplier source | item-global | LT-03 |
| Replenishment | HOUSE owners of the operator company | `WhReplenishmentRunRepositoryCustomImpl.java:258-263` |
| Unit cost | site open layers, all owners | `:275-295` |

- Required change: use a canonical planning key of company × owner × item × site.

**DQ-02: Mixed date bucketing (MINOR)**

| Input | Date basis |
|---|---|
| Demand | posting date, else site timezone |
| Lead time | UTC dates |
| Own-site engine day | UTC (ST-02) |
| Sister day | site timezone |

**DQ-03: Currency (MINOR)**
- Evidence: the run takes the site currency (`WhReplenishmentEngine.java:209-211`). Cost layers hold the base currency plus the paid currency and rate.
- Problem: a multi-site investment roll-up needs FX policy.

## 15. Test coverage

The explorer counted 490 test files.

Present:
- `WhDemandHistoryRecorderTest`: outbound counts, write-off exclusion, line-over-header reason, reversal, TRANSFER_DEPART, lost sale.
- `WhReplenishmentEngineProposeTest`: 4 cases.
- `WhReplenishmentEngineSisterTransferTest`: 5 cases.
- `WhSupplierLeadTimeQueryServiceTest`.
- Ledger: `WhbLedgerInvariantsIntegrationTest`, `WhbStockLedgerWriterIntegrationTest`, `LedgerVolumeFixtureTest`.

Missing, all MAJOR for planning safety:
- VENDOR_RETURN or JOB_ISSUE despatch vs demand (DH-01/02).
- 3PL owner demand (DH-03).
- Import vs live collision (DH-05).
- `WhLostSaleRecorder`.
- Engine using unusable stock (ST-01).
- Run executor and scheduled runner (one-running rule, re-proposal, accept→PO).
- Suggestion expiry.
- Item-site validation (min ≤ max).
- Supersession resolver, cycle and merge.
- Query-plan or bound tests for the ledger reports.

## 16. Open follow-ups in repo docs

| Doc | Item |
|---|---|
| `warehouse/docs/contracts/replenishment.contract.md` | Status "DERIVED — ratify before trusting" (:11-12). RPL-C-01 TRANSFER accept (stale), RPL-C-02 guard lost sales, RPL-C-03 warranty seed, RPL-C-04 lead-time report API-only, RPL-C-05 ledger-less sites not scheduled (:61-65). |
| `warehouse/docs/contracts/pick-face-replenishment.contract.md` | RPF-OPEN-01 source not reserved, RPF-OPEN-02 no partial completion, RPF-OPEN-03 v2 triggers (:137-139). |
| `warehouse-base/docs/DATED-OBLIGATION-REGISTER.md` | :43 (replenishment run), :52 (backorder horizon), :53 (P6-01 archiver), :86 (lead-time fields unread), :101 (supersession window read-only). No row for ABC/XYZ reclassification. |
| Migration comments | FR-463 ABC job, P6-02 velocity/XYZ/computed stocking level, V500069 and V500077 promised but absent, FR-254 sister preference P6. |

Frontend: there are no forecast, classification, planning-parameter or lead-time pages. The existing pages are:
- `warehouse/frontend/src/app/dashboard/warehouse/inventory/{demand-history,replenishment-runs,replenishment-suggestions,insufficient-stock}/page.tsx`
- `warehouse-base/frontend/src/app/dashboard/warehouse/masters/{item-site-settings,item-supplier-sources,supersessions}/page.tsx`

## 17. warehouse-3pl / warehouse-india *(spot-checked)*

- **3PL**: client-owned stock (`CLIENT_3PL` owner type, `WB/V500007...sql:143-147`) shares sites with house stock. This is the root of DH-03. Planning must key on owner.
- **India**: `WhinStockByMrpRepositoryCustomImpl.java:29` is another unbounded ledger read. Bonded-warehouse consumption (`WB`-india `V540140`) is a statutory ledger and is not a demand source. There was no planning conflict beyond an MRP (price) dimension on stock.
