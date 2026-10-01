# Warehouse foundation gap register

Research date: 2026-09-30. This is an implementation-readiness review, not a runtime certification.

## Evidence and scope

Local checkout: `neetub1508/classic`, HEAD `fcdbe1748b7d0a510d156d760ddf54cbb1854db5`. Source inspection included the working tree; pinned links identify the corresponding committed files. Existing uncommitted edits, including warehouse KPI work, were left untouched. Issue repository: `neetub1508/warehouse-issues`; refreshed snapshot contains **189 issues: 144 closed, 45 open**. Issue closure does not prove shipped behavior.

The earlier design repository snapshot was `7b96725eb5850748cd94b2a784466cb16728a55d`. Local `docs/spi` contains product proposals; it is not a running planning module. This report proposes changes and does not amend adopted repository decisions.

**Evidence levels:** Observed = inspected implementation limitation; Open issue = reported defect/dependency not reproduced here; New capability = required in the proposed planning design but not established in inspected code; Contract risk = behavior must be proven at the new integration boundary. “Not found” does not prove that no equivalent exists anywhere in the repository.

**Gates:** A = before production planning inputs/publication contracts are frozen; B = before advisory planning pilot; C = before automatic release; D = before that advanced capability is promised. A prototype may proceed in parallel with A work using isolated data.

## Foundations to retain

- `warehouse-base` owns stock identities, ledger/positions, reservations, movement contracts and transactional events.
- `warehouse` provides procurement, replenishment documents, monthly demand/lost-sales summaries, calendars and reporting.
- Existing replenishment includes stock-policy thresholds, source constraints and sister-site surplus logic. It is useful execution behavior; it does not establish statistical forecasting or joint multi-echelon optimization.
- Outbox appends occur in the stock transaction. Delivery already has scoped subscriptions, ordered cursors, failure blocking and retry behavior.
- Daily stock snapshots already exist, use site-local dates, retain superseded versions and record an event cursor. Planning needs additional input state, not a second stock ledger.
- Owner is part of item identity. Preserve that rule throughout planning.

## Prioritized gaps and acceptance evidence

### G01 — Source-level demand facts

- **Status / gate:** Observed limitation; A.
- **Owner:** Planning ingestion + warehouse app.
- **Evidence:** [E01](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse/backend/src/main/java/ai/warehouse/entity/WhDemandHistory.java); [E02](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse/backend/src/main/java/ai/warehouse/service/whdemandhistory/WhDemandHistoryRecorder.java).
- **Required change or decision:** Retain demand identity, requested item, fulfilled item, event time, known time, quantity/UOM, stream and source revision. Keep current monthly totals as a projection.
- **Acceptance:** A late cancellation changes the corrected view but does not alter a previously sealed as-known training set.

### G02 — Zero demand versus missing data

- **Status / gate:** New contract; A.
- **Owner:** Integration.
- **Evidence:** [E01](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse/backend/src/main/java/ai/warehouse/entity/WhDemandHistory.java); [E02](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse/backend/src/main/java/ai/warehouse/service/whdemandhistory/WhDemandHistoryRecorder.java).
- **Required change or decision:** Add feed completeness, site opening/closing dates, observed-through and explicit unavailable state.
- **Acceptance:** An absent week triggers incomplete-data handling; a complete zero week remains a valid zero.

### G03 — Demand deduplication and commercial/service meaning

- **Status / gate:** Observed limitation; A.
- **Owner:** Planning + warehouse app.
- **Evidence:** [E02](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse/backend/src/main/java/ai/warehouse/service/whdemandhistory/WhDemandHistoryRecorder.java).
- **Required change or decision:** Define demand at request, sale, service consumption and shipment grain. Warranty/internal exclusions in commercial demand must not silently erase physical service need.
- **Acceptance:** A request partly filled with a substitute, then returned, produces the agreed demand and service metrics exactly once.

### G04 — Policy history and override authority

- **Status / gate:** Observed limitation; A.
- **Owner:** Planning + base API.
- **Evidence:** [E03](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse-base/backend/src/main/java/ai/warehousebase/entity/WhbItemSiteSetting.java); [E04](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse-base/backend/src/main/java/ai/warehousebase/service/WhbItemSiteSettingService.java); [#99](https://github.com/neetub1508/warehouse-issues/issues/99).
- **Required change or decision:** Version calculated policies and overrides separately; record validity, source, approval, reason and expiry. Publish only effective execution values.
- **Acceptance:** A run cannot overwrite a later manual override; removing an override has a defined recomputation/result transition.

### G05 — One owner of policy calculation

- **Status / gate:** Backlog/design decision; A.
- **Owner:** Product + planning.
- **Evidence:** [#99](https://github.com/neetub1508/warehouse-issues/issues/99); [E09](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse/backend/src/main/java/ai/warehouse/service/whreplenishment/WhReplenishmentEngine.java).
- **Required change or decision:** Resolve computed-stock-policy scope with the new planning module. Keep execution replenishment and forecasting responsibilities explicit.
- **Acceptance:** One documented authority exists for each ROP/safety/min/max field; scheduled jobs cannot fight over it.

### G06 — Detailed time-phased supply projection

- **Status / gate:** Observed limitation; A.
- **Owner:** Warehouse app + planning.
- **Evidence:** [E07](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse-base/backend/src/main/java/ai/warehousebase/service/allocation/WhbOnOrderSource.java); [E08](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse/backend/src/main/java/ai/warehouse/entity/WhPurchaseOrderLine.java).
- **Required change or decision:** Add dated supply-line feed with order/line/revision, status, expected serviceable date, remaining quantity and firmness; retain aggregate on-order API for its current clients.
- **Acceptance:** Partial receipt, rejection, cancellation and delayed delivery alter the correct buckets without counting the original line twice.

### G07 — Unknown supply versus verified zero

- **Status / gate:** Contract risk; A.
- **Owner:** Integration.
- **Evidence:** [E07](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse-base/backend/src/main/java/ai/warehousebase/service/allocation/WhbOnOrderSource.java).
- **Required change or decision:** Declare capability and completeness separately from numeric quantity. A missing optional provider cannot imply authoritative no supply for automatic planning.
- **Acceptance:** An unavailable purchasing feed blocks automatic release while allowing a visibly incomplete advisory run.

### G08 — Lead-time measurement

- **Status / gate:** Observed limitation; B.
- **Owner:** Warehouse app analytics + planning.
- **Evidence:** [E06](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse/backend/src/main/java/ai/warehouse/service/whreplenishment/WhSupplierLeadTimeQueryService.java); [E08](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse/backend/src/main/java/ai/warehouse/entity/WhPurchaseOrderLine.java).
- **Required change or decision:** Retain distributions by relevant item/source/site/lane and normal/emergency path. Distinguish first receipt, final receipt and quality release; include late open orders as censored observations.
- **Acceptance:** Two partial receipts and a QC hold yield separate first-receipt and usable-supply measures; timezone boundaries are explicit.

### G09 — Supplier site preference

- **Status / gate:** Observed mismatch; A.
- **Owner:** Base + warehouse app.
- **Evidence:** [E05](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse-base/backend/src/main/java/ai/warehousebase/entity/WhbItemSupplierSource.java); [#157](https://github.com/neetub1508/warehouse-issues/issues/157).
- **Required change or decision:** Current entity has no warehouse field. #157 was closed as duplicate, not implementation proof. Reconcile folded tasks and add/verify site-specific resolution and fallback before relying on it.
- **Acceptance:** The same item at Delhi and Mumbai resolves different valid preferred suppliers, with deterministic global fallback.

### G10 — Demand merging for supersession

- **Status / gate:** Open integration gap; A.
- **Owner:** Planning + warehouse app.
- **Evidence:** [#168](https://github.com/neetub1508/warehouse-issues/issues/168); [E02](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse/backend/src/main/java/ai/warehouse/service/whdemandhistory/WhDemandHistoryRecorder.java).
- **Required change or decision:** Consume MERGE_DEMAND deliberately in planning; preserve physical item history and keep interchange authorization separate.
- **Acceptance:** A dated A→B change aggregates permitted demand once; disabling demand merge does not disable a separately valid substitute.

### G11 — Requested versus fulfilled item across all paths

- **Status / gate:** Partial; integration unproven; A.
- **Owner:** Base + adapters.
- **Evidence:** [#167](https://github.com/neetub1508/warehouse-issues/issues/167).
- **Required change or decision:** Base support exists in requested-item/reservation paths; prove all supported callers retain it. Do not treat obsolete deleted adapters as pending deployment dependencies.
- **Acceptance:** Reservation, split picks, cancellation and replenishment analytics preserve the original request while tracing fulfilled substitutes.

### G12 — Planning network model

- **Status / gate:** New capability; B.
- **Owner:** Planning.
- **Evidence:** [E09](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse/backend/src/main/java/ai/warehouse/service/whreplenishment/WhReplenishmentEngine.java); [E16](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse-base/backend/src/main/java/ai/warehousebase/entity/WhbItem.java).
- **Required change or decision:** Add effective-dated planning nodes, stock responsibilities, lanes, priorities, transit/handling times and calendars without repurposing bins.
- **Acceptance:** A lane closes mid-horizon; no supply crosses it after closure, and existing transit remains represented.

### G13 — Owner/company boundaries in planning

- **Status / gate:** Extension validation; A.
- **Owner:** Planning + base.
- **Evidence:** [E10](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse-base/backend/src/main/java/ai/warehousebase/service/outbox/WhbOutboxEvent.java); [E16](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse-base/backend/src/main/java/ai/warehousebase/entity/WhbItem.java).
- **Required change or decision:** Carry company and owner in projections and authorization. Item identity already includes immutable owner: do not claim the monthly table creates cross-owner leakage simply because it lacks owner_id.
- **Acceptance:** Same SKU text for two owners stays distinct; aggregate views and exports honor grants.

### G14 — New sites without a ledger

- **Status / gate:** Observed scheduling limitation; A.
- **Owner:** Planning scheduler.
- **Evidence:** [E14](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse-base/backend/src/main/java/ai/warehousebase/service/jobs/WhbJobDescriptor.java); [E15](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse-base/backend/src/main/java/ai/warehousebase/service/jobs/WhbJobRunner.java).
- **Required change or decision:** Planning scope must enumerate configured planning pairs/nodes, including new/no-stock sites. Warehouse-scoped job discovery uses sites with ledger activity.
- **Acceptance:** A newly commissioned site receives an initial recommendation before its first stock movement.

### G15 — Reusable transactional event foundation

- **Status / gate:** Reuse with new consumer; A.
- **Owner:** Base + integration.
- **Evidence:** [E10](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse-base/backend/src/main/java/ai/warehousebase/service/outbox/WhbOutboxEvent.java); [E11](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse-base/backend/src/main/java/ai/warehousebase/service/outbox/WhbOutboxAppender.java); [E12](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse-base/backend/src/main/java/ai/warehousebase/service/outbox/WhbOutboxDeliveryStep.java).
- **Required change or decision:** Reuse same-transaction outbox and delivery/retry behavior. Add planning consumer checkpoints, canonical event identity and schema-version handling.
- **Acceptance:** A crash after applying an event but before acknowledgment causes no duplicate demand or supply when redelivered.

### G16 — Snapshot boundary and event replay

- **Status / gate:** Contract risk; A.
- **Owner:** Planning ingestion + base.
- **Evidence:** [E11](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse-base/backend/src/main/java/ai/warehousebase/service/outbox/WhbOutboxAppender.java); [E13](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse-base/backend/src/main/java/ai/warehousebase/service/ledger/snapshot/WhbPositionSnapshotService.java).
- **Required change or decision:** Daily stock snapshot cursor is a lower-bound inclusion marker read before positions. Do not assume it is an exact upper cutoff. Define atomic cut or overlap dedup/reconciliation for bootstrap.
- **Acceptance:** A movement committed between cursor capture and row scan is reflected once after snapshot plus replay.

### G17 — Complete planning run snapshot

- **Status / gate:** New capability; A.
- **Owner:** Planning.
- **Evidence:** [E13](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse-base/backend/src/main/java/ai/warehousebase/service/ledger/snapshot/WhbPositionSnapshotService.java); [E01](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse/backend/src/main/java/ai/warehouse/entity/WhDemandHistory.java); [E03](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse-base/backend/src/main/java/ai/warehousebase/entity/WhbItemSiteSetting.java).
- **Required change or decision:** Reuse stock snapshots but add versioned demand, supply, policy, master, network, calendar, costs and model input manifests.
- **Acceptance:** Two reruns using a sealed manifest produce equivalent results even after live master edits.

### G18 — Historical as-known state

- **Status / gate:** New capability; A.
- **Owner:** Planning + integration.
- **Evidence:** [E01](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse/backend/src/main/java/ai/warehouse/entity/WhDemandHistory.java); [E02](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse/backend/src/main/java/ai/warehouse/service/whdemandhistory/WhDemandHistoryRecorder.java); [E13](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse-base/backend/src/main/java/ai/warehousebase/service/ledger/snapshot/WhbPositionSnapshotService.java).
- **Required change or decision:** Track business-effective time and when information became known. Mark reconstructed histories when original state is unavailable.
- **Acceptance:** A July event received in August is excluded from a July as-known backtest and included in a corrected-history view.

### G19 — Historical balance defect backlog

- **Status / gate:** Open issue; not reproduced; A.
- **Owner:** Warehouse reporting.
- **Evidence:** [#179](https://github.com/neetub1508/warehouse-issues/issues/179).
- **Required change or decision:** Reconcile reported 365-day window limitation before using the as-at report as a validation oracle. Verify against ledger opening balance plus movements.
- **Acceptance:** Stock received over a year earlier and still held remains in the historical quantity.

### G20 — Scenario isolation

- **Status / gate:** New planning capability; A.
- **Owner:** Planning + platform.
- **Evidence:** Warehouse sandbox boundary migration V511258; [E13](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse-base/backend/src/main/java/ai/warehousebase/service/ledger/snapshot/WhbPositionSnapshotService.java).
- **Required change or decision:** Use distinct scenario state and prohibit production commands, notifications and integrations from simulation. Existing sandbox sites alone are not a full historical model.
- **Acceptance:** Simulation cannot create a PO, send a supplier message, post GL or change execution policy.

### G21 — Planning run orchestration

- **Status / gate:** Extension; B.
- **Owner:** Planning.
- **Evidence:** [E14](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse-base/backend/src/main/java/ai/warehousebase/service/jobs/WhbJobDescriptor.java); [E15](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse-base/backend/src/main/java/ai/warehousebase/service/jobs/WhbJobRunner.java).
- **Required change or decision:** Add dependencies, input seals, pause checkpoints, cancellation, retries, fencing tokens and atomic output activation on top of existing scheduling.
- **Acceptance:** A timed-out worker returning after takeover cannot publish; resumed work does not rerun completed external effects.

### G22 — Recommendation write-back contract

- **Status / gate:** New capability; A.
- **Owner:** Planning + warehouse app.
- **Evidence:** [E09](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse/backend/src/main/java/ai/warehouse/service/whreplenishment/WhReplenishmentEngine.java).
- **Required change or decision:** Use typed recommendation acceptance APIs with expected target version, run identity, business idempotency key and result reference. Never directly update execution tables.
- **Acceptance:** Lost acknowledgment followed by retry produces one execution document, and changed live conditions produce a reviewable conflict.

### G23 — Automation release guardrails

- **Status / gate:** New capability; C.
- **Owner:** Planning + platform.
- **Evidence:** [E09](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse/backend/src/main/java/ai/warehouse/service/whreplenishment/WhReplenishmentEngine.java); [E15](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse-base/backend/src/main/java/ai/warehousebase/service/jobs/WhbJobRunner.java).
- **Required change or decision:** Separate calculation, approval and release rights. Add scope/value/quantity limits, freshness gates, high-risk exclusions, kill switch and fallback.
- **Acceptance:** One invalid source or exceeded spend cap stops release; valid recommendations stay visible for manual review.

### G24 — Forecast netting and reservations

- **Status / gate:** New capability; B.
- **Owner:** Planning.
- **Evidence:** [E02](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse/backend/src/main/java/ai/warehouse/service/whdemandhistory/WhDemandHistoryRecorder.java); [E07](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse-base/backend/src/main/java/ai/warehousebase/service/allocation/WhbOnOrderSource.java); [E09](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse/backend/src/main/java/ai/warehouse/service/whreplenishment/WhReplenishmentEngine.java).
- **Required change or decision:** Define consumption between forecasts and actual orders. Do not subtract reservation and its underlying order twice.
- **Acceptance:** Forecast 10 with confirmed demand 4 yields 10 total expected units under the agreed netting rule, not 14 or 6.

### G25 — Classification calculation

- **Status / gate:** Backlog not proven implemented; B.
- **Owner:** Planning.
- **Evidence:** [#33](https://github.com/neetub1508/warehouse-issues/issues/33); [E03](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse-base/backend/src/main/java/ai/warehousebase/entity/WhbItemSiteSetting.java).
- **Required change or decision:** Existing ABC/XYZ/VED/FSN/HML fields are useful inputs. A closed folded issue is not evidence of automated recomputation. Specify time window, cost/usage basis, ties and override precedence.
- **Acceptance:** Classification is reproducible at cutoff, respects exclusions and does not change a manual criticality designation silently.

### G26 — Forecast validation and fallback

- **Status / gate:** New capability; B.
- **Owner:** Planning.
- **Evidence:** SPI draft; competitor file §§11–14.
- **Required change or decision:** Baseline and intermittent methods, rolling-origin evaluation, zero-safe metrics, stable switching and explicit no-history fallback.
- **Acceptance:** An all-zero series, one spike and a new item produce finite outputs and intelligible method-selection reasons.

### G27 — Service objective semantics

- **Status / gate:** New contract; A.
- **Owner:** Product + planning.
- **Evidence:** [E18](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse/backend/src/main/java/ai/warehouse/service/whpartskpi/WhPartsKpiQueryService.java).
- **Required change or decision:** Define units/lines/orders, requested/fulfilled item, time promised/achieved and observation window before tuning stock.
- **Acceptance:** A split line and late completion yield correct unit fill, line fill and on-time service independently.

### G28 — Uncertainty and constrained stock policy

- **Status / gate:** New capability; B.
- **Owner:** Planning.
- **Evidence:** [#99](https://github.com/neetub1508/warehouse-issues/issues/99).
- **Required change or decision:** Start with explicit service/stock targets and uncertainty. Enforce MOQ/multiples/budgets and report infeasibility; use full multi-echelon optimization only when independently validated.
- **Acceptance:** An impossible service target under a budget reports shortfall rather than returning a misleading optimal status.

### G29 — Shared donor and supplier capacity

- **Status / gate:** Extension; B.
- **Owner:** Planning + execution acceptance.
- **Evidence:** [E09](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse/backend/src/main/java/ai/warehouse/service/whreplenishment/WhReplenishmentEngine.java).
- **Required change or decision:** Existing donor surplus heuristic is useful but not joint network optimization. Coordinate competing proposals and revalidate at acceptance.
- **Acceptance:** Two recipients cannot both consume the same last ten donor units; supplier capacity is shared across relevant items.

### G30 — Order stability and approval feedback

- **Status / gate:** Extension; B.
- **Owner:** Planning.
- **Evidence:** [E09](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse/backend/src/main/java/ai/warehouse/service/whreplenishment/WhReplenishmentEngine.java).
- **Required change or decision:** Define frozen horizons, change thresholds and accepted-order feedback to prevent buy/cancel oscillation.
- **Acceptance:** A second run after approval includes created supply once; small forecast changes do not breach the frozen horizon.

### G31 — Repairable and core planning

- **Status / gate:** New capability; D.
- **Owner:** Planning + optional repair integration.
- **Evidence:** Prior [#81](https://github.com/neetub1508/warehouse-issues/issues/81) closure is VOID; competitor file §18.
- **Required change or decision:** Add core/repair feeds, return probability/delay, NFF, repair yield/capacity, serial applicability and repair-vs-buy economics when target customers require it.
- **Acceptance:** A core is never simultaneously serviceable on-hand and expected repaired supply; scrap removes the appropriate expected receipt.

### G32 — Installed base and maintenance

- **Status / gate:** New capability; D.
- **Owner:** Planning + optional adapters.
- **Evidence:** SPI draft; [#108](https://github.com/neetub1508/warehouse-issues/issues/108) adapter not required by prior decision.
- **Required change or decision:** Define optional exposure, utilization, failures and maintenance feed; separate asset master integration from warehouse execution.
- **Acceptance:** A retired machine stops contributing future exposure while its historical failure data remains valid.

### G33 — Lifecycle and last-time buy

- **Status / gate:** New capability; D.
- **Owner:** Planning.
- **Evidence:** Competitor reference §§2,14,17,25.
- **Required change or decision:** Represent introduction, phase-in/out, substitute availability, final order date, support horizon, decay and recoverable supply; run sensitivity analysis.
- **Acceptance:** A future replacement reduces legacy need only from its effective availability; final-buy deadline is enforced.

### G34 — UOM and part conversion integrity

- **Status / gate:** Extension + open issue; A.
- **Owner:** Base + warehouse app + ingestion.
- **Evidence:** [#193](https://github.com/neetub1508/warehouse-issues/issues/193); [E08](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse/backend/src/main/java/ai/warehouse/entity/WhPurchaseOrderLine.java); [E16](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse-base/backend/src/main/java/ai/warehousebase/entity/WhbItem.java).
- **Required change or decision:** Reuse frozen line UOM conversion and add canonical planning base units and supersession ratios. Resolve import default behavior deliberately.
- **Acceptance:** Two old units per new item cannot be interpreted as the reciprocal; rounding conserves material and rejects invalid factors.

### G35 — Calendars and usable dates

- **Status / gate:** Reuse + extension; A.
- **Owner:** Planning.
- **Evidence:** [E17](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse/backend/src/main/java/ai/warehouse/service/whworkingcalendar/WhWorkingCalendarService.java); [E06](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse/backend/src/main/java/ai/warehouse/service/whreplenishment/WhSupplierLeadTimeQueryService.java).
- **Required change or decision:** Reuse calendars while recording the version, site timezone, supplier workdays, dispatch/receive cutoffs and QC release timing.
- **Acceptance:** Weekend, holiday and daylight-saving transitions produce reproducible dates; UTC first-receipt reporting is not silently treated as site-local serviceability.

### G36 — Cost and accounting readiness

- **Status / gate:** Open integration dependency; B.
- **Owner:** Accounting integration + planning.
- **Evidence:** [#174](https://github.com/neetub1508/warehouse-issues/issues/174); [#175](https://github.com/neetub1508/warehouse-issues/issues/175).
- **Required change or decision:** Reconcile cost-input/provenance/policy follow-ups #169–#173 as well as accounting mode and cost/GL reconciliation. Planning costs may be estimates, but must be labeled and isolated from ledger valuation.
- **Acceptance:** Missing landed cost blocks cost-optimized auto-release or uses a disclosed fallback; simulations never post journal entries.

### G37 — Performance isolation

- **Status / gate:** Open measurement + new workload; A.
- **Owner:** Platform + planning.
- **Evidence:** [#182](https://github.com/neetub1508/warehouse-issues/issues/182); [E13](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse-base/backend/src/main/java/ai/warehousebase/service/ledger/snapshot/WhbPositionSnapshotService.java).
- **Required change or decision:** Measure historical extraction and run work outside long OLTP write transactions; set query/resource budgets and data-size targets.
- **Acceptance:** A representative planning batch meets agreed duration while warehouse receipt/ship latency stays within the agreed budget.

### G38 — Operational release blockers

- **Status / gate:** Open issue evidence; A.
- **Owner:** Warehouse + platform.
- **Evidence:** [#183](https://github.com/neetub1508/warehouse-issues/issues/183); [#186](https://github.com/neetub1508/warehouse-issues/issues/186); [#189](https://github.com/neetub1508/warehouse-issues/issues/189).
- **Required change or decision:** Revalidate CI migration-header failure, missing acceptance demonstrations and zone-less putaway defect before pilot readiness. These were not reproduced during this research.
- **Acceptance:** Affected CI gate passes and representative receiving/putaway/order workflows pass in the supported build environment.

### G39 — Bin replenishment versus network transfer

- **Status / gate:** Open design/execution mismatch; B.
- **Owner:** Warehouse app.
- **Evidence:** [#176](https://github.com/neetub1508/warehouse-issues/issues/176); [#177](https://github.com/neetub1508/warehouse-issues/issues/177).
- **Required change or decision:** Resolve owning task for internal bin movement/emergency replenishment. Keep planning transfers between sites distinct from bin replenishment.
- **Acceptance:** A network plan cannot emit an unsupported BIN_TO_BIN document; emergency picking follows an executable warehouse path.

### G40 — Reporting and export permissions

- **Status / gate:** Open dependency + validation; A.
- **Owner:** Platform + planning.
- **Evidence:** [#185](https://github.com/neetub1508/warehouse-issues/issues/185); [E18](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse/backend/src/main/java/ai/warehouse/service/whpartskpi/WhPartsKpiQueryService.java).
- **Required change or decision:** Use scope-safe per-recipient reporting and cost masking; scenario and forecast exports require the same grant rules as interactive views.
- **Acceptance:** A scheduled report cannot widen a recipient’s company/site/owner scope or leak restricted cost data.

### G41 — Recommendation explanations

- **Status / gate:** New capability; B.
- **Owner:** Planning.
- **Evidence:** Competitor reference §22.
- **Required change or decision:** Store calculation components, input versions, constraints, alternatives considered and rejection reasons.
- **Acceptance:** A planner can reconstruct why an item was recommended, which target bound, and why transfer lost to purchase.

### G42 — Exception workflow

- **Status / gate:** New planning capability; B.
- **Owner:** Planning.
- **Evidence:** Competitor reference §22.
- **Required change or decision:** Group repeated alerts, retain acknowledged/delayed/resolved states, severity, assignee, reason and next review date.
- **Acceptance:** A still-failing condition does not vanish when acknowledged and does not create a new identical alert every run.

### G43 — External integration scope

- **Status / gate:** Decision; prior removals; A.
- **Owner:** Product + integration.
- **Evidence:** [#95](https://github.com/neetub1508/warehouse-issues/issues/95); [#102](https://github.com/neetub1508/warehouse-issues/issues/102); [#108](https://github.com/neetub1508/warehouse-issues/issues/108); [#150](https://github.com/neetub1508/warehouse-issues/issues/150); [#151](https://github.com/neetub1508/warehouse-issues/issues/151).
- **Required change or decision:** Respect removed/deferred dealer, service, asset and OEM adapters. Define supported initial sources; do not silently restore deleted modules to satisfy an old SPI diagram.
- **Acceptance:** Deployment supports its advertised feeds using current modules and reports unsupported feeds explicitly.

### G44 — Deployment and sizing promises

- **Status / gate:** Draft correction; A.
- **Owner:** Product + architecture.
- **Evidence:** docs/spi/SPI_FUNCTIONAL_DOCUMENT.md.
- **Required change or decision:** Replace unmeasured 500k SKU/750k pair scale and universal real-time uniqueness claims with measured sizing and a chosen target customer profile.
- **Acceptance:** Capacity statement has a dataset, hardware, concurrency, workload and measured result; no extrapolated enterprise parity claim.

### G45 — Retention, reproducibility and export

- **Status / gate:** New contract; A.
- **Owner:** Planning + platform.
- **Evidence:** [E11](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse-base/backend/src/main/java/ai/warehousebase/service/outbox/WhbOutboxAppender.java); [E13](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse-base/backend/src/main/java/ai/warehousebase/service/ledger/snapshot/WhbPositionSnapshotService.java).
- **Required change or decision:** Reconcile archiving/opening-balance issue #94; choose data/event/snapshot/model retention and customer deletion behavior before schemas freeze. Preserve manifests or mark historical runs non-reproducible after lawful purge.
- **Acceptance:** Exported run package can be explained without live tables; expired data produces an explicit unavailable state.

### G46 — Source authority and reconciliation

- **Status / gate:** New contract; A.
- **Owner:** Integration.
- **Evidence:** [E10](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse-base/backend/src/main/java/ai/warehousebase/service/outbox/WhbOutboxEvent.java); [E11](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse-base/backend/src/main/java/ai/warehousebase/service/outbox/WhbOutboxAppender.java); [E07](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse-base/backend/src/main/java/ai/warehousebase/service/allocation/WhbOnOrderSource.java).
- **Required change or decision:** Specify authority per field/feed, external-to-internal identity mapping, load versions and reconciliation tolerances. Keep native and external positions from double-counting.
- **Acceptance:** An overlapping native/external item-site feed is detected; partial loads cannot replace the active complete dataset.

### G47 — Security of scenario and AI features

- **Status / gate:** New validation; A.
- **Owner:** Platform + planning.
- **Evidence:** Proposed extension of existing grants.
- **Required change or decision:** Scope all scenario copies, shared views, exports and any AI retrieval to authorized data; prohibit tools from executing recommendations without normal command authorization.
- **Acceptance:** A copied scenario cannot expose a source site after the user loses access; generated text cannot bypass approval.

### G48 — Migration and numerical contract

- **Status / gate:** New contract; A.
- **Owner:** Base + planning.
- **Evidence:** Existing frozen execution quantities; SPI draft.
- **Required change or decision:** Version schema/model/config; define decimal money/UOM boundaries, solver tolerance and output rounding. Use additive migrations and dry-run reconciliation.
- **Acceptance:** A model upgrade can compare old/new results on the same manifest; rounding cannot violate MOQ or available stock.

## Important corrections to previous interpretation

1. **Supplier site scope is not verified as shipped.** #157’s only reviewed closure comment says its work was folded into other issues. Current `WhbItemSupplierSource` lacks a warehouse field. The earlier assumption that the closed issue proved a site junction existed was too strong.
2. **Snapshots and retry infrastructure already exist.** Missing planning snapshots/orchestration must not be described as a complete absence of warehouse snapshots/jobs/events.
3. **Requested-item support is partly implemented.** #167 needs caller-by-caller proof, not a blanket claim that base reservations lack requested identity.
4. **Deleted adapters are intentional prior scope decisions.** #81/#95 were voided; #102/#108 marked not required; dealer/services adapters were removed. Product expansion requires explicit scope reconciliation.
5. **Closed duplicate work is not implementation evidence.** This affects classification and supplier/site work as well as the overall completion percentage.
6. **No runtime defect was reproduced in this review.** Open issues are readiness dependencies; code observations identify missing contracts/capabilities and specific risks.

## Source file index

- [E01](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse/backend/src/main/java/ai/warehouse/entity/WhDemandHistory.java) — `warehouse/backend/src/main/java/ai/warehouse/entity/WhDemandHistory.java`.
- [E02](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse/backend/src/main/java/ai/warehouse/service/whdemandhistory/WhDemandHistoryRecorder.java) — `warehouse/backend/src/main/java/ai/warehouse/service/whdemandhistory/WhDemandHistoryRecorder.java`.
- [E03](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse-base/backend/src/main/java/ai/warehousebase/entity/WhbItemSiteSetting.java) — `warehouse-base/backend/src/main/java/ai/warehousebase/entity/WhbItemSiteSetting.java`.
- [E04](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse-base/backend/src/main/java/ai/warehousebase/service/WhbItemSiteSettingService.java) — `warehouse-base/backend/src/main/java/ai/warehousebase/service/WhbItemSiteSettingService.java`.
- [E05](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse-base/backend/src/main/java/ai/warehousebase/entity/WhbItemSupplierSource.java) — `warehouse-base/backend/src/main/java/ai/warehousebase/entity/WhbItemSupplierSource.java`.
- [E06](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse/backend/src/main/java/ai/warehouse/service/whreplenishment/WhSupplierLeadTimeQueryService.java) — `warehouse/backend/src/main/java/ai/warehouse/service/whreplenishment/WhSupplierLeadTimeQueryService.java`.
- [E07](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse-base/backend/src/main/java/ai/warehousebase/service/allocation/WhbOnOrderSource.java) — `warehouse-base/backend/src/main/java/ai/warehousebase/service/allocation/WhbOnOrderSource.java`.
- [E08](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse/backend/src/main/java/ai/warehouse/entity/WhPurchaseOrderLine.java) — `warehouse/backend/src/main/java/ai/warehouse/entity/WhPurchaseOrderLine.java`.
- [E09](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse/backend/src/main/java/ai/warehouse/service/whreplenishment/WhReplenishmentEngine.java) — `warehouse/backend/src/main/java/ai/warehouse/service/whreplenishment/WhReplenishmentEngine.java`.
- [E10](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse-base/backend/src/main/java/ai/warehousebase/service/outbox/WhbOutboxEvent.java) — `warehouse-base/backend/src/main/java/ai/warehousebase/service/outbox/WhbOutboxEvent.java`.
- [E11](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse-base/backend/src/main/java/ai/warehousebase/service/outbox/WhbOutboxAppender.java) — `warehouse-base/backend/src/main/java/ai/warehousebase/service/outbox/WhbOutboxAppender.java`.
- [E12](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse-base/backend/src/main/java/ai/warehousebase/service/outbox/WhbOutboxDeliveryStep.java) — `warehouse-base/backend/src/main/java/ai/warehousebase/service/outbox/WhbOutboxDeliveryStep.java`.
- [E13](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse-base/backend/src/main/java/ai/warehousebase/service/ledger/snapshot/WhbPositionSnapshotService.java) — `warehouse-base/backend/src/main/java/ai/warehousebase/service/ledger/snapshot/WhbPositionSnapshotService.java`.
- [E14](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse-base/backend/src/main/java/ai/warehousebase/service/jobs/WhbJobDescriptor.java) — `warehouse-base/backend/src/main/java/ai/warehousebase/service/jobs/WhbJobDescriptor.java`.
- [E15](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse-base/backend/src/main/java/ai/warehousebase/service/jobs/WhbJobRunner.java) — `warehouse-base/backend/src/main/java/ai/warehousebase/service/jobs/WhbJobRunner.java`.
- [E16](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse-base/backend/src/main/java/ai/warehousebase/entity/WhbItem.java) — `warehouse-base/backend/src/main/java/ai/warehousebase/entity/WhbItem.java`.
- [E17](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse/backend/src/main/java/ai/warehouse/service/whworkingcalendar/WhWorkingCalendarService.java) — `warehouse/backend/src/main/java/ai/warehouse/service/whworkingcalendar/WhWorkingCalendarService.java`.
- [E18](https://github.com/neetub1508/classic/blob/fcdbe1748b7d0a510d156d760ddf54cbb1854db5/warehouse/backend/src/main/java/ai/warehouse/service/whpartskpi/WhPartsKpiQueryService.java) — `warehouse/backend/src/main/java/ai/warehouse/service/whpartskpi/WhPartsKpiQueryService.java`.

## Suggested delivery sequence

1. Resolve G04–G07, G09–G11, G13–G20 and G34–G35 as durable data/identity/time contracts.
2. Revalidate known warehouse release blockers and historical reports (G19, G36–G40).
3. Ship source completeness, baseline forecasts, policy calculation and explanations in read-only shadow mode.
4. Add reviewed acceptance into current warehouse documents; prove idempotency and concurrency (G22).
5. Enable narrowly scoped automation only after G23 evidence and an observed pilot period.
6. Add repair, installed base, lifecycle and advanced network methods only for validated customer needs.
