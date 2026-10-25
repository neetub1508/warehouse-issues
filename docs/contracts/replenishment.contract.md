# Functional Contract — Replenishment: reorder policy, the replenishment run and its suggestions, pick-face tasks, demand history, lost sales, order source

> **What this is.** The functional truth for how warehouse **proposes** stock: the reorder policy on
> item × site and item × location, the replenishment run that writes a suggestions document (manual or
> scheduled), sister-site transfer before purchase, pick-face replenishment tasks, demand history kept by
> posting, the lost-sale log, and the order source a purchase carries. **The warehouse never becomes a
> purchase-order engine**: a suggestion is converted by a person. External suggestions published by MRP
> through the core port are [`po-schedule-port`](po-schedule-port.contract.md) §8b (`POS-T1-30`…`-35`,
> `POS-GRD-30`…`-32`) and are not restated here.
>
> **Status.** Derived 2026-10-23 (v0) from `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` §6.14 (`FR-252`…`FR-260`)
> and verified against the built code in `classic`. Not ratified. Written for R30 `CP-FR-007` row 13 /
> `D-17` item 1.

---

## 0. Identity

| | |
|---|---|
| **Workflow** | Policy (WS-027 / WS-028) → run (manual on WS-140, or the per-site `SCHEDULED` job) → suggestions `PROPOSED` → buyer accepts (convert to a draft PO or a transfer order) or rejects with a reason. Separately: the pick-face job raises `REPLEN` tasks (WS-142); posting maintains demand history (WS-143); refused demand is logged (WS-096) |
| **Module** | `warehouse-base` (`whb_item_site_settings`, `whb_item_location_settings`; `WhbReplenishmentRunScheduler` / `WhbReplenishmentRunJob`, `WhbPickFaceReplenishmentScheduler` / `WhbPickFaceReplenishmentJob`) + `warehouse` (`WhReplenishmentEngine`, `WhReplenishmentRunExecutor`, `WhReplenishmentSuggestionService`, `WhReplenishmentNotifier`, `WhReplenishmentTaskGenerator`, `WhDemandHistoryRecorder`, `WhLostSaleRecorder`, `WhSupplierLeadTimeQueryService`) |
| **Domain baseline** | `D-14` (`REGISTERED` branch), `D-16` item 3 (`VOR` relabelled *line-stop / machine-down*), `D-17` items 4 and 6 · `RG-001`, `RK-004` · `po-schedule-port` §8b |
| **Owning tasks** | `issues/p1-03.md` (item × site policy) · `issues/p2-15.md` (run, suggestions, demand history, lost sales, order source — PARTIALLY VOID) · `issues/p3-12.md` (item × location, pick-face tasks) · `issues/p5-18.md` (sister transfer, emergency / top-off / break-case) · `issues/p1-12.md` (PO order source) · `issues/p6-02.md` (computed stocking level — **VOID**, `D-17` item 6) |
| **Primary tables** | `whb_item_site_settings` (`V500050`), `whb_item_location_settings` (`V500016`), `wh_replenishment_runs`, `wh_replenishment_suggestions`, `wh_demand_history` (`V510070`), `wh_replenishment_tasks`, `wh_insufficient_stock_log`, `wh_purchase_orders.order_source` (`V510011`) |
| **Status columns** | `wh_replenishment_runs.status` `RUNNING`/`COMPLETED`/`FAILED`, `run_type` CHECK `MANUAL`/`SCHEDULED` (`V510070:117`; `EXTERNAL` added by `POS` §8b) · `wh_replenishment_suggestions.status` `PROPOSED`/`ACCEPTED`/`CONVERTED`/`REJECTED`, `suggested_source` CHECK `PURCHASE`/`TRANSFER` (`V510070:223`) |
| **Permission resources** | `whb_item_site_settings:{view,create,edit,delete,export}` · `whb_item_location_settings:{view,create,edit,delete,export}` · `wh_replenishment_runs:{view,create,export}` · `wh_replenishment_suggestions:{view,accept,reject,export}` · `wh_replenishment_tasks:{view,assign,complete,cancel,export}` · `wh_demand_history:{view,export}` · `wh_insufficient_stock_log:{view,create,export}` |
| **Routes** | WS-027 `/warehouse/masters/item-site-settings` · WS-028 `/warehouse/masters/item-location-settings` · WS-140 `/warehouse/inventory/replenishment-runs` · WS-141 `/warehouse/inventory/replenishment-suggestions` · WS-142 `/warehouse/execution/replenishment-tasks` · WS-143 `/warehouse/inventory/demand-history` · WS-096 `/warehouse/inventory/insufficient-stock` · mobile: none (`D-16` item 7) |
| **Contract version** | `v0 — 2026-10-23` |

### Acceptance checks

| # | Expects | Delivered by |
|---|---|---|
| A1 | Reorder parameters live on item × site; pick-face min / max / trigger on item × location (`WH-SC-280`, `FR-252` as amended 2026-10-26) | `RPN-GRD-01`, `RPN-T5-01` |
| A2 | The run writes a document the buyer converts; no PO is raised automatically (`WH-SC-281`) | `RPN-T1-01`…`-06`, `RPN-UNR-01` |
| A3 | A sister site is proposed before a supplier (`WH-SC-353`) | `RPN-T4-02`, `RPN-GRD-05` |
| A4 | Pick-face, emergency, top-off and break-case tasks (`WH-SC-354`) | `RPN-T3-02`, `RPN-T4-04` |
| A5 | Demand history by posting; lost sales are demand (`WH-SC-282`, `WH-SC-283`) | `RPN-T4-05`, `-06` |
| A6 | Line-stop / emergency purchases are excluded from lead time (`WH-SC-284`) | `RPN-GRD-08` |

---

## 1. T1 — State machine

### 1.1 Status inventory

| Entity | Status | Reachable via | Exits via | Kind |
|---|---|---|---|---|
| Run | `RUNNING` | `RPN-T1-01`, `-02` | `-03`, `-04` | active (one per site at a time) |
| Run | `COMPLETED` / `FAILED` | `-03` / `-04` | none | **terminal** |
| Suggestion | `PROPOSED` | `RPN-T1-03` | `-05`, `-07` | initial |
| Suggestion | `ACCEPTED` | inside `RPN-T1-05` only | `CONVERTED` in the **same transaction** | **momentary** — Accept creates the document in the same transaction and a failed creation rolls both back, so a committed row is never left `ACCEPTED` (`WhReplenishmentSuggestion.java:35-37`); there is no queue of accepted-but-unconverted suggestions |
| Suggestion | `CONVERTED` / `REJECTED` | `-06` / `-07` | none here (`POS-T1-35` re-opens a PR conversion) | **terminal** |
| Replenishment task | `REPLEN` task, open → done / cancelled | `RPN-T4-04` | `-08`, `-09` | task |

### 1.2 Transitions

| ID | From | Event | To | Guard | Actor | Side effects | Reason? | Source |
|---|---|---|---|---|---|---|---|---|
| RPN-T1-01 | — | **Run** (manual): site, parameters | run `RUNNING` | `RPN-GRD-02` | `wh_replenishment_runs:create` | number `RPL…`; `run_type = MANUAL`, `run_by` = actor | no | FR-253 |
| RPN-T1-02 | — | Scheduled run (per site, nightly by default) | run `RUNNING` | `RPN-GRD-02` | system job (`RPN-T3-01`) | `run_type = SCHEDULED`, `run_by` null; a `whb_job_runs` row | no | FR-253 |
| RPN-T1-03 | run `RUNNING` | Engine completes | run `COMPLETED`; suggestions `PROPOSED` | `RPN-GRD-03`, `-05` | system | `RPN-T4-01`…`-03` | no | FR-253, FR-254 |
| RPN-T1-04 | run `RUNNING` | Engine throws | run `FAILED` | — | system | no suggestions survive | no | FR-253 |
| RPN-T1-05 | `PROPOSED` | Accept / bulk accept = convert (buyer may edit quantity, source, source site, supplier) | `CONVERTED`, passing through `ACCEPTED` inside the one transaction | `RPN-GRD-04`…`-06` | `wh_replenishment_suggestions:accept` | `RPN-T4-03` | no | FR-253 |
| RPN-T1-06 | — | *(folded into `RPN-T1-05`, R31 `F-CB-002`: there is no separate Convert action and no committed `ACCEPTED` row to convert)* | — | — | — | `resulting_document_type` `PO` / `TRANSFER_ORDER` is written by `-05` | no | FR-253 |
| RPN-T1-07 | `PROPOSED` | Reject | `REJECTED` | `RPN-GRD-07` | `:reject` | — | **yes** | FR-253 |
| RPN-T1-08 | task open | Complete (confirm the pick-face location) | done | `RPN-GRD-09` | `wh_replenishment_tasks:complete` | one internal move through the writer | no | FR-255 |
| RPN-T1-09 | task open | Cancel | cancelled | open only, else `409 REPLENISHMENT_TASK_NOT_OPEN` | `:cancel` | — | **yes** | FR-255 |

### 1.3 Guards

| ID | Predicate | Refusal | Backstop | Source |
|---|---|---|---|---|
| RPN-GRD-01 | Min, max, reorder point, reorder quantity, safety stock and lead time are held per **item × site** (`whb_item_site_settings`); pick-face min / max / trigger per **item × location** (`whb_item_location_settings`, dated `effective_from`/`_to`) | field-level `422` on the master | uk per grain | FR-252 (amended 2026-10-26, #33 S-16 / G4: two grains, no v1.1 location-level reorder point) |
| RPN-GRD-02 | One running run per site | `409 REPLENISHMENT_RUN_ALREADY_RUNNING` | one-running-run index `V510070:147` | FR-253 |
| RPN-GRD-03 | The run needs a house owner at the site | `REPLENISHMENT_NO_HOUSE_OWNER` | — | FR-253 |
| RPN-GRD-04 | Only a `PROPOSED` suggestion is accepted (and so converted); `ACCEPTED` is never a committed starting state | `409 REPLENISHMENT_SUGGESTION_NOT_PROPOSED` | — | FR-253 |
| RPN-GRD-05 | A `TRANSFER` names a source site that is a **sister**: a site of a different `REGISTERED` branch as at the run, holding allocatable house stock above its own minimum; a site is never its own sister and a shared site counts once | `422 REPLENISHMENT_SOURCE_WAREHOUSE_REQUIRED` / `_NOT_ALLOWED` / `REPLENISHMENT_SOURCE_NOT_A_SISTER` | `CHECK (suggested_source <> 'TRANSFER' OR source_warehouse_id IS NOT NULL)` `V510070:228` | FR-254 |
| RPN-GRD-06 | A `PURCHASE` names a supplier, an owner and an operating company | `422 REPLENISHMENT_SUPPLIER_REQUIRED` / `_OWNER_REQUIRED` / `_OPERATING_COMPANY_REQUIRED` | — | FR-253 |
| RPN-GRD-07 | A reject reason is an active code in its context; a note when the code requires one | `422 REPLENISHMENT_REJECT_REASON_NOT_FOUND` / `_WRONG_CONTEXT` / `_INACTIVE` / `REPLENISHMENT_REJECT_NOTE_REQUIRED` | FK `whb_reason_codes` | FR-253 |
| RPN-GRD-08 | Lead-time statistics exclude purchases whose `order_source` is `LINE_STOP` (*line-stop / machine-down*; the FRD's `VOR`) or `EMERGENCY` | — (excluded from the figure) | `ORDER_SOURCE_LINE_STOP`, `ORDER_SOURCE_EMERGENCY` (`EXCLUDED_FROM_LEAD_TIME`) in `WhSupplierLeadTimeQueryService`; pinned by `WhSupplierLeadTimeQueryServiceTest` | FR-260 |
| RPN-GRD-09 | A replenishment task's target is a valid pick-face location at the site and the source still holds the stock | `422 REPLENISHMENT_LOCATION_INVALID` / `REPLENISHMENT_SOURCE_EMPTY` | ledger guards | FR-255 |
| RPN-GRD-10 | A lost-sale capture (through the core API, from the guard or from `warehouse-trade`): item required, quantity > 0, not in the future, reason valid (note when required) | `422 LOST_SALE_ITEM_REQUIRED` / `LOST_SALE_QUANTITY_INVALID` / `LOST_SALE_OCCURRED_IN_FUTURE` / `LOST_SALE_REASON_INVALID` / `LOST_SALE_REASON_NOTE_REQUIRED` | — | FR-257 |
| RPN-GRD-11 | **An item planned elsewhere is not reorder-planned** (R31 `MRP-OPEN-10`, `mfg-mrp`): the reorder-point run skips an item × site for which the registered `ExternalPlanningOwner` (FRD-STORES registry R.3) answers `plansItem = true` — MFG's `planning_method = MRP` (FR-662) — so an `MRP` item with core reorder settings is not proposed twice; its supply arrives as `origin = MRP` suggestions (`p8-16`). With no bean registered (MFG absent) core's settings rule every item | — (skipped; no suggestion row) | one batch `plansItem` read per run before proposing; core reads no `whm_` | FR-253 |
| RPN-GRD-12 | **A make item or a non-purchasable item gets no purchase proposal** (#33 G8, `FR-731`): after the supersession terminal substitution, the run proposes no `PURCHASE` line for an item whose `make_or_buy` is `MAKE` or whose type is not `is_purchasable`. The count it leaves out is **logged only** (ratified 2026-10-26, #33 S3 F5): `wh_replenishment_runs.parameters_text` holds the run's inputs, not its outcome, and no outcome-note column is added | — (left out of the proposal) | `WhReplenishmentEngine` | FR-731 |
| RPN-GRD-13 | **The supersession substitution proposes nothing twice** (#106 H1, F5 / F7 + `RPN-GRD-11`): a superseded item's proposal is restated as its terminal only when the terminal has no live `PROPOSED` suggestion at the site (the one-live-suggestion rule `findCandidates` applies to every candidate) and no registered `ExternalPlanningOwner` plans the terminal; otherwise the predecessor's proposal is dropped — never a second live terminal suggestion, never an MRP-owned terminal re-introduced through an unclaimed predecessor. The dropped count is logged only (as `RPN-GRD-12`) | — (no suggestion row) | `WhReplenishmentEngine.proposeTerminals`, `WhReplenishmentRunRepositoryCustom.findItemsWithLiveProposal` | FR-071, FR-253 |
| RPN-GRD-14 | **A MAKE item below its reorder point gets no proposal from core** (#106 H5): `RPN-GRD-12` leaves it out of the purchase proposal and core proposes no work order; with `warehouse-manufacturing` absent, a non-MRP `MAKE` item is planned by no module. This is the stated boundary, not a defect: core replenishment is a purchase / transfer planner, and make-side planning is `warehouse-manufacturing`'s (P10, `MRP-OPEN-10`) | — (logged only, `RPN-GRD-12`) | `WhReplenishmentEngine` | FR-731, FR-253 |

### 1.4 Unreachable

| ID | Must never happen | Why it cannot | Source |
|---|---|---|---|
| RPN-UNR-01 | A purchase order raised automatically by a run, scheduled or manual | conversion is only `RPN-T1-05`/`-06`, a person's action | FR-253 |
| RPN-UNR-02 | A suggestion that is a grid filter rather than a stored row | suggestions are `wh_replenishment_suggestions` rows of a numbered run | FR-253 |
| RPN-UNR-03 | Adjustments, warranty issues or internal consumption counted as demand | the reason's `affects_demand_history = false` excludes the line | FR-256 |

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from | Source |
|---|---|---|---|---|
| RPN-T2-01 | Maintain item × site / item × location policy | `whb_item_site_settings:*` / `whb_item_location_settings:*` | — | FR-252 |
| RPN-T2-02 | Start a run | `wh_replenishment_runs:create` | — | FR-253 |
| RPN-T2-03 | Accept / bulk accept / reject a suggestion | `wh_replenishment_suggestions:accept` / `:reject` | `PROPOSED` | FR-253 |
| RPN-T2-04 | Assign / complete / cancel a replenishment task | `wh_replenishment_tasks:assign` / `:complete` / `:cancel` | open | FR-255 |
| RPN-T2-05 | Record a lost sale by hand — **removed** (R31 `RPN-OPEN-01`, `D-17` item 4): no core screen or endpoint records one; trade calls the core API | Route retired (`32311da2ce`: `WhInsufficientStockLogController` is GET-only, guarded by `WhInsufficientStockLogControllerRouteTest`); the `wh_insufficient_stock_log:create` verb is **kept** for the port (`WhLostSalePort.captureLostSale` → `capturePortLostSale`). The dead service method `captureLostSale` is removed (#106 S2) | — | FR-257 |

## 3. T3 — Time-driven rules

| ID | Rule | Trigger | Changes | Notified | Source |
|---|---|---|---|---|---|
| RPN-T3-01 | Scheduled run per site | `warehouse.replenishment.default_schedule` (nightly by default), ordinary job framework | `RPN-T1-02` | buyers (`RPN-T4-07`) | FR-253 |
| RPN-T3-02 | Pick-face replenishment | `WhbPickFaceReplenishmentScheduler` pass | `REPLEN` tasks for faces at or below their trigger (`MIN_MAX`); `OPPORTUNISTIC` top-off in idle time | — | FR-255, FR-259 |
| RPN-T3-03 | **Reorder-point and safety-stock proposal** (v3, restored by `D-18` item 6): for an item × site planned by `REORDER_POINT`, a scheduled computation proposes a reorder point and safety stock from the issue history over a demand window, a lead time and a service-level target; a planner accepts it or overrides it with a reason; the typed parameters (`RPN-GRD-01`, `FR-662`) stay what the run reads | policy run | a proposal only — never the typed parameter until accepted | planner | FR-258 — **not built; carrier `P10-11` as a later-version increment (§10 row 4)** |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in | Source |
|---|---|---|---|---|
| RPN-T4-01 | A run completes | per item × site below its reorder point: a suggestion carrying item, site, on-hand, allocated, on-order, ROP, suggested quantity, source (`PURCHASE`/`TRANSFER`), source site, supplier and reason. The supplier is the item's preferred **authorised** source (`WhbPreferredSupplierSourceSql`, `is_authorised_source = true`, `CPM-GRD-05`): the **effective row per supplier** is resolved first — that supplier's site row before its every-site row, exactly as the receipt resolves it — then a supplier whose effective row is unauthorised is dropped (so a supplier unauthorised at the site is never proposed there through its every-site row), and the site's own row still beats an every-site row among the authorised ones, and with no authorised current source the supplier is blank (the buyer names it at Accept) . **Superseded items** (#33 G3, #106 H2 / H3): a superseded item's need is restated as its terminal at the cumulative ratio; the terminal's position (on hand − allocated + on order) above its own reorder point — all of it when the terminal keeps no reorder point at the site — is counted into its predecessors' positions in their units, shared in predecessor order, so a terminal order raised from an earlier substitution stops the next run proposing it again; the terminal's whole need (its own plus every restated need) is raised to the **terminal's** supplier minimum and rounded to its multiple once — the supplier the row names. A terminal the run evaluated itself carries its **own** candidate and on-hand / allocated / on-order / ROP, and its reason says the predecessor's calculation is quoted while the row's figures are the terminal's own; a terminal outside the run carries its first predecessor's figures, and its reason says so (#33 S4c F1) | `WhReplenishmentEngine` | FR-253, FR-455, FR-071 |
| RPN-T4-02 | A sister holds surplus | the suggestion is a `TRANSFER` from the sister with the largest surplus, before any purchase line | same | FR-254 |
| RPN-T4-03 | A suggestion is converted | a **draft** purchase order (`PURCHASE`) or transfer order (`TRANSFER`) is created and linked (`resulting_document_*`); nothing is approved or sent | `WhReplenishmentSuggestionService` | FR-253 |
| RPN-T4-04 | A short pick, a min / max breach, an idle face, or a case-level item at an each face | a `REPLEN` task with trigger `SHORT_PICK` (emergency priority, ahead of every open task), `MIN_MAX`, `OPPORTUNISTIC` or `BREAK_CASE`; priority = max(task type default, max priority of the picks starving on that face + 1) | `WhReplenishmentTaskGenerator` | FR-255, FR-259 |
| RPN-T4-05 | An outbound movement posts | `wh_demand_history` for item × site × month: `hit_count` +1 and `quantity` += line quantity, unless the reason excludes it (`RPN-UNR-03`) | `WhDemandHistoryRecorder` (posting) | FR-256 |
| RPN-T4-06 | The insufficient-stock guard refuses a store issue or despatch, or a lost sale is captured | a `wh_insufficient_stock_log` row (type, resolution) and the month's `lost_sale_count` / `lost_sale_quantity`; the log is the fill-rate denominator | `WhbInsufficientStockRecorder`, `WhLostSaleRecorder` | FR-257 |
| RPN-T4-07 | A run produced suggestions | the site's buyers (holders of `:accept` whose site scope includes the run's site) are told in-app and by email: count, value, link | `WhReplenishmentNotifier` (`WAREHOUSE_REPLENISHMENT_SUGGESTED`) | FR-253 (`RK-004`) |
| RPN-T4-08 | A purchase is saved | `order_source` ∈ `STOCK`, `DAILY`, `VOR` (*line-stop / machine-down*), `EMERGENCY`, `SPECIAL_ORDER`, `BACK_ORDER`, `INITIAL_STOCK`, with a customer-waiting flag, a linked job reference and a promised date | `chk_wh_purchase_orders_order_source` `V510011:127`; `V511421`: `is_customer_waiting BOOLEAN NOT NULL DEFAULT false` (a null on the request — port, suggestion convert — is stored false), `job_reference VARCHAR(100)` (free text, no FK), `customer_promised_date DATE` (refused before `order_date`, `PO_EXPECTED_BEFORE_ORDER`); header edit rule, DRAFT only; no grid / filter / export column; the port command does not carry them (`P9-07`) | FR-260 — §10 row 2 closed |

## 5. T5 — Screen contract

| ID | Screen · grid · scope | Contract | Source |
|---|---|---|---|
| RPN-T5-01 | WS-027 Item × Site Settings · `whb_item_site_settings` · `WAREHOUSE_ITEM_SITE_SETTING`; WS-028 Item × Location Settings · `whb_item_location_settings` · `WAREHOUSE_ITEM_LOCATION_SETTING` | the reorder parameters of `RPN-GRD-01`, editable per grain | FR-252 |
| RPN-T5-02 | WS-140 Replenishment Runs · `wh_replenishment_runs` · `WAREHOUSE_REPLENISHMENT_RUN` | columns `runNumber`, `warehouseName`, `runType`, `runAt`, `runByName`, status; detail lists the run's suggestions; **Run** action | FR-253 |
| RPN-T5-03 | WS-141 Replenishment Suggestions · `wh_replenishment_suggestions` · `WAREHOUSE_REPLENISHMENT_SUGGESTION` | the `RPN-T4-01` columns; row actions Accept · Reject; toolbar Bulk accept; `/sister-sites` lists the sisters for a `TRANSFER` | FR-253, FR-254 |
| RPN-T5-04 | WS-142 Replenishment Tasks · `wh_replenishment_tasks` · `WAREHOUSE_REPLENISHMENT_TASK` | `taskNumber`, `itemCode`, `fromLocationCode`, `toLocationCode`, trigger, priority; Assign · Complete · Cancel | FR-255, FR-259 |
| RPN-T5-05 | WS-143 Demand History · `wh_demand_history` · `WAREHOUSE_DEMAND_HISTORY` | read-only: `itemCode`, `warehouseName`, `periodYearMonth`, `hitCount`, `quantity`, lost-sale count and quantity, `isMigrated` | FR-256, FR-257 |
| RPN-T5-06 | WS-096 Insufficient Stock & Lost Sales · `wh_insufficient_stock_log` · `WAREHOUSE_INSUFFICIENT_STOCK` | the log rows with policy (`BLOCK`/`WARN`/`ALLOW`), source type, type and resolution | FR-257 |

## 6. Out of scope

MRP planning parameters, demand plans and safety-stock planning (`warehouse-manufacturing`, `P10-11`,
`P10-12`); external suggestions and their withdraw / release (`po-schedule-port` §8b); the low-stock and
fill-rate reports (`reports-kpis`); producing lost sales from trade enquiries and orders (`D-17` item 4,
`warehouse-trade`).

## 7. Amendments

| Date | Change |
|---|---|
| 2026-10-23 | v0 derived (R30 `CP-FR-007` row 13) |
| 2026-10-23 | R31: `F-CB-002` (`ACCEPTED` momentary, `RPN-T1-06` folded into `-05`); `RPN-OPEN-01` decided (manual capture removed); `FR-258` restored by `D-18` item 6 (`RPN-T3-03`, `RPN-OPEN-02`, §10 row 4); `RPN-GRD-11` — the reorder run skips items an `ExternalPlanningOwner` plans (`mfg-mrp` `MRP-OPEN-10`, `p8-16`) |
| 2026-10-26 | R31 `P1-03` #33 S4 (S3 F5, F8 / G4): `FR-252` amended to two grains — §10 row 1 struck, `A1` and `RPN-GRD-01` pointers dropped; `RPN-GRD-12` added (MAKE / non-purchasable items get no purchase proposal; the excluded count is logged only) |
| 2026-10-26 | W72 #606 S4 / #106 H4 (classic `956d43c66f`): `RPN-T4-01` — the proposed supplier is an authorised source only; site-before-every-site order kept (`WhReplenishmentPreferredSupplierSourceIntegrationTest.shouldNeverProposeAnUnauthorisedSource`) |
| 2026-10-26 | W72 #606 S4 round b / S3 F-B1 (classic `b984bd1461`): `RPN-T4-01` — effective row per supplier (site row first, as the receipt) before the authorised filter, then rank; a supplier unauthorised at the site is never proposed via its every-site row (`WhReplenishmentPreferredSupplierSourceIntegrationTest.shouldResolveTheEffectiveRowPerSupplierBeforeDroppingUnauthorised`) |
| 2026-10-26 | R31 `P1-03` #33 A2 S4c (#106 pre-build H1–H3, H5): `RPN-GRD-13` added (the supersession substitution honours the one-live-suggestion rule and `RPN-GRD-11`); `RPN-T4-01` states the terminal-position netting and the terminal's supplier terms; `RPN-GRD-14` added (a MAKE item below its reorder point is planned by no core module — the stated boundary). Tests `WhReplenishmentSupersessionTest` |
| 2026-10-26 | R31 `P1-03` #33 S4d (S3 S4c F1): `RPN-T4-01` states which figures each kind of terminal row carries — an evaluated terminal its own, an outside terminal its first predecessor's — and the reason names them (`WhReplenishmentSupersessionTest.onlyTheTerminalsSpareStockCountsAndIsShared`, `.aSupersededItemIsProposedAsItsTerminal`) |

## 8. Invariants and scenarios

`WH-SC-280`…`WH-SC-284`, `WH-SC-353`, `WH-SC-354`. `FR-258` has no scenario.

## 9. Open rows

| ID | Question | Default |
|---|---|---|
| RPN-OPEN-01 | `FR-257` keeps a manual "not catalogued" capture; `D-17` item 4 says no core screen records a lost sale by hand. The built WS-096 still offers `POST` (`wh_insufficient_stock_log:create`). Which stands? | **DECIDED R31 (2026-10-23), default replaced:** the manual `POST` is removed from WS-096 and `FR-257` is restated; lost sales come through trade (§10 row 3; `P2-15` acceptance item) |
| RPN-OPEN-02 | **CLOSED 2026-10-23.** `FR-258`'s only owner `P6-02` is VOID (`D-17` item 6) | **RESTORED by `D-18` item 6** (R31 decisions; the R30 withdrawal is undone): rewritten without the dealer-parts wording as a reorder-point / safety-stock proposal from consumption history (`RPN-T3-03`); v3; carrier `P10-11`; an install without MFG would need it in core replenishment |

## 10. Code divergences

The FRD rule is kept; the code is what differs.

| # | File:line | FR | Difference |
|---|---|---|---|
| 1 | ~~`warehouse-base/…/entity/WhbItemLocationSetting.java` (columns `min_quantity`, `max_quantity`, `replen_trigger_quantity`)~~ | FR-252 | **STRUCK 2026-10-26 (#33 S-16 / G4, S3 F8):** `FR-252` is amended to the two grains the code holds — reorder point, reorder quantity, safety stock and lead time per item × site; min / max / trigger per item × location for internal moves. A location-level reorder point would have no consumer. No code is owed |
| 2 | `warehouse/backend/src/main/resources/db/migration/V510011__Create_wh_purchase_orders_and_lines.sql:95` | FR-260 | `order_source` exists; the customer-waiting flag, linked job reference and promised date are absent from `wh_purchase_orders` — **Triage 2026-10-23: FIX-CODE** — owner `P2-15` #106 (`FR-260`). **CLOSED 2026-10-26 (#106 S2 G1, classic `4309bed0cb`, `V511421`)** — see `RPN-T4-08`. reviewer-confirm settled: the trade PO does not carry them (R33 open question 2) |
| 3 | `warehouse/backend/src/main/java/ai/warehouse/controller/WhInsufficientStockLogController.java:175-183` (`POST`, `captureLostSale`) | FR-257 | manual capture is served; R31 `RPN-OPEN-01` removes it (`D-17` item 4); `P2-15` owns the removal (acceptance item added) — **Triage 2026-10-23: FIX-CODE** — owner `P2-15` #106. **CLOSED:** the `POST` was removed in classic `32311da2ce` (GET-only controller, `WhInsufficientStockLogControllerRouteTest`); the uncalled service method `captureLostSale` went in `4309bed0cb` |
| 4 | — (no reorder-point proposal anywhere in `warehouse-base` / `warehouse` / `warehouse-manufacturing`) | FR-258 | not built (v3); carrier `P10-11` (`D-18` item 6) — **Triage 2026-10-23: CARRIED** — `P10-11` #602 |
