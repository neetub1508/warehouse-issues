# Warehouse-only readiness: gap register

Audit date: 2026-10-01. Baseline: `0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa` in `neetub1508/classic`. No forecasting, inventory optimization, historical planning scenarios or planning AutoPilot work is included. Existing warehouse execution replenishment remains in scope.

## Reading this register

- **Code-supported:** current inspected code supports the limitation/path; this does not imply a new runtime reproduction.
- **Runtime-observed:** a read-only check in the current environment reproduced the stated observation.
- **Reported:** issue/contract records the concern; full current behavior still needs a targeted test.
- **Verification gap:** implementation may exist, but the required release evidence was not established here.
- **Accepted/intentional limitation:** a supported scope decision; fix only if the selected offer/customer needs more.
- **Documentation drift:** wording and implementation disagree; update the evidence and guidance.

**Priorities are audit recommendations:** P0 = stock-trust/recovery release gate; P1 = resolve or prove before releasing the affected workflow; P2 = workflow/product constraint to resolve or explicitly accept for the selected customer; P3 = minor consistency defect. Optional scopes do not block an unrelated warehouse-only customer.

This is not a list of confirmed failures on every install. Each item states its applicable scope and how to close it. Sources are pinned where possible. GitHub remains unchanged.

## W01 — Historical stock report can omit older surviving stock

**Code-supported · P0 · Scope: Stock As-At reporting**

**Evidence:** [#179](https://github.com/neetub1508/warehouse-issues/issues/179); [WhStockAsAtQueryService.java:129](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse/backend/src/main/java/ai/warehouse/service/whstockasat/WhStockAsAtQueryService.java#L129); [WhStockAsAtRepositoryCustomImpl.java:105](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse/backend/src/main/java/ai/warehouse/repository/WhStockAsAtRepositoryCustomImpl.java#L105).

**Finding:** The current query sums movements only in the preceding 365 days. It is not an all-time balance if stock predates that window. A footer stating the window does not make it a correct balance.

**Next action:** Use a valid opening snapshot plus deltas, or a complete balance computation with measured performance.

**Close when:** Stock received more than 365 days earlier, with no later movement, appears correctly; compare report with independent ledger reconstruction.

## W02 — Zone-less putaway rules can throw during response mapping

**Code-supported · P1 · Scope: Receiving/putaway**

**Evidence:** [#189](https://github.com/neetub1508/warehouse-issues/issues/189); [WhPutawayRuleQueryService.java:411](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse/backend/src/main/java/ai/warehouse/service/whputawayrule/WhPutawayRuleQueryService.java#L411); [WhPutawayRuleMapper.java:61](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse/backend/src/main/java/ai/warehouse/service/whputawayrule/WhPutawayRuleMapper.java#L61).

**Finding:** An empty immutable map is used for absent zones and then queried with a nullable zone ID. This matches the reported Java null-key failure path. No new live create was performed.

**Next action:** Handle the optional zone before lookup; cover create, edit, list and detail.

**Close when:** FIXED_LOCATION and CONSOLIDATE_SAME_LOT rules work in an otherwise zone-less result page, without HTTP 500 or rollback.

## W03 — Blank unit on imported/direct demand order is not defaulted

**Code-supported · P1 · Scope: Demand orders and channel imports**

**Evidence:** [#193](https://github.com/neetub1508/warehouse-issues/issues/193); [WhDemandOrderValidationService.java:214](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse/backend/src/main/java/ai/warehouse/service/whdemandorder/WhDemandOrderValidationService.java#L214).

**Finding:** Validation passes the nullable request unit to the conversion guard despite the request contract promising the item base unit as default.

**Next action:** Normalize omitted/blank unit once before validation and persistence; return line-specific errors for invalid supplied units.

**Close when:** Direct API and channel import with omitted UOM use the item base unit; explicit incompatible UOM is refused atomically.

## W04 — Style/variant matrix has no supported style-creation path found

**Code-supported · P1 · Scope: Variant/style feature**

**Evidence:** [#191](https://github.com/neetub1508/warehouse-issues/issues/191); [WhbStyleVariantAxisRepository.java:1](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-base/backend/src/main/java/ai/warehousebase/repository/WhbStyleVariantAxisRepository.java#L1); [WhbVariantMatrixRepository.java:1](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-base/backend/src/main/java/ai/warehousebase/repository/WhbVariantMatrixRepository.java#L1).

**Finding:** Style reads require style-axis associations. Searches found readers and a migration self-test, but no production association writer.

**Next action:** Provide a supported association setup flow, or disable the advertised matrix capability until it exists.

**Close when:** A fresh install can create a style, assign axes, create variants and use a ratio-pack template without direct SQL.

## W05 — Supplier preference by site remains unverified in implementation

**Code-supported · P1 · Scope: Multi-site purchasing/replenishment**

**Evidence:** [#157](https://github.com/neetub1508/warehouse-issues/issues/157); [#33](https://github.com/neetub1508/warehouse-issues/issues/33); [WhbItemSupplierSource.java:1](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-base/backend/src/main/java/ai/warehousebase/entity/WhbItemSupplierSource.java#L1).

**Finding:** Supplier-source entity has no site field. #157 was closed as duplicate and folded into other tasks, so its closed state is not shipped evidence.

**Next action:** Reconcile the folded requirement and implement/verify per-site selection and default fallback in current consumers.

**Close when:** One item selects supplier A for one site and B for another, with effective-date behavior and deterministic fallback.

## W06 — Cost-layer and valuation-policy maintenance surfaces remain unbuilt/unproven

**Code-supported · P1 · Scope: Valued stock**

**Evidence:** [#169](https://github.com/neetub1508/warehouse-issues/issues/169); [warehouse-base/backend/src/main/java/ai/warehousebase/controller](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-base/backend/src/main/java/ai/warehousebase/controller).

**Finding:** The follow-up identifies missing screens/seeds; controller search did not find CostLayer or ValuationPolicy controllers. Existing costing engine is not a substitute for supported policy maintenance.

**Next action:** Deliver or identify the supported configuration, inspection and export surfaces; reconcile seeds and permissions.

**Close when:** A stock controller can inspect layers and an authorized user can maintain effective policies through supported UI/API.

## W07 — Approval cost and original-currency evidence require persistence reconciliation

**Reported / partial code check · P1 · Scope: Approval-gated valued movements**

**Evidence:** [#170](https://github.com/neetub1508/warehouse-issues/issues/170); [WhbStockLedgerWriter.java:879](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-base/backend/src/main/java/ai/warehousebase/service/ledger/writer/WhbStockLedgerWriter.java#L879).

**Finding:** The issue reports differences between submitted line cost and approval-time valuation, and missing persisted source amount/rate/source-line identity. Command fields alone do not prove reload after approval preserves them.

**Next action:** Trace submitted → pending → approved → line/layer/envelope; choose the adopted immutable persistence approach and migrate accordingly.

**Close when:** After restart and approval, reports, layers and handover values agree; source currency and originating cost line remain recoverable.

## W08 — Cost inputs from receipt/return/transfer producers need end-to-end proof

**Code-supported / reported · P1 · Scope: Foreign purchases, returns and transfers**

**Evidence:** [#171](https://github.com/neetub1508/warehouse-issues/issues/171); [WhGoodsReceiptPostingService.java:849](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse/backend/src/main/java/ai/warehouse/service/whgoodsreceipt/WhGoodsReceiptPostingService.java#L849); [WhTransferOrderPostingService.java:265](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse/backend/src/main/java/ai/warehouse/service/whtransferorder/WhTransferOrderPostingService.java#L265).

**Finding:** Current movement constructors use the shorter shape with absent currency/source-cost details. The issue reports foreign receipt refusal and missing return/transfer cost lineage. Some older adapter references are obsolete.

**Next action:** Audit current native producers individually; retain sender/origin cost and normalize source currency exactly once.

**Close when:** Foreign PO receipt, matched supplier return and transfer receipt preserve correct cost without double conversion or destination recosting.

## W09 — Costing contract documentation and runtime evidence need reconciliation

**Reported / documentation · P1 · Scope: Valued stock**

**Evidence:** [#172](https://github.com/neetub1508/warehouse-issues/issues/172); [warehouse-base/backend/pom.xml](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-base/backend/pom.xml).

**Finding:** The adopted settings amendment already answers several cost-policy questions that #172 calls open. Database costing tests are excluded from the default gate.

**Next action:** Apply the adopted decisions, update stale wording and execute the costing integration scenarios; avoid reopening answered product questions.

**Close when:** FIFO/average, effective policy changes, rounding, negative stock and approval cost cases pass against PostgreSQL.

## W10 — Accounting-integrated mode lacks an installed implementation

**Code-supported · P1 · Scope: Only accounting-integrated customers**

**Evidence:** [#174](https://github.com/neetub1508/warehouse-issues/issues/174); [#175](https://github.com/neetub1508/warehouse-issues/issues/175); [WhbAccountingHandoverSink.java:1](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-base/backend/src/main/java/ai/warehousebase/service/accounting/WhbAccountingHandoverSink.java#L1); [WhbGlBalanceProvider.java:1](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-base/backend/src/main/java/ai/warehousebase/service/accounting/WhbGlBalanceProvider.java#L1).

**Finding:** No production implementations were found for these interfaces. Standalone valuation remains supported; an integrated accounting promise is not established.

**Next action:** Assign the adapter owner and prove handover/reconciliation before enabling integrated mode.

**Close when:** One dispatch yields one correctly valued accounting result; retries do not duplicate it; unavailable GL is never shown as zero.

## W11 — Versioned accounting-envelope extension

**Reported · P1 · Scope: Only customers requiring the expanded accounting interface**

**Evidence:** [#173](https://github.com/neetub1508/warehouse-issues/issues/173); [accounting-handover.contract.md:1](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-base/docs/contracts/accounting-handover.contract.md#L1).

**Finding:** Required per-line details and version negotiation are not established by the frozen v1 contract.

**Next action:** Define v2 with the receiving module and resolve account-reference ownership using adopted authority.

**Close when:** Receiver accepts the negotiated version and preserves duty/lot/serial/rate evidence without recosting.

## W12 — RMA expiry has no scheduled transition found

**Code-supported · P1 · Scope: Returns/RMA**

**Evidence:** [#165](https://github.com/neetub1508/warehouse-issues/issues/165); [warehouse-base/docs/DATED-OBLIGATION-REGISTER.md](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-base/docs/DATED-OBLIGATION-REGISTER.md).

**Finding:** Expiry is enforced when matching a return, but the scheduled status transition remains marked owed and no RMA expiry job was found.

**Next action:** Implement the site-date job using existing job infrastructure and idempotent transitions.

**Close when:** Expired OPEN/APPROVED RMAs become EXPIRED once; the list and receipt validation agree across timezones.

## W13 — Sealed-carton/item attachments lack an owning-module delete guard

**Code-supported · P1 · Scope: Packing evidence and item documents**

**Evidence:** [#166](https://github.com/neetub1508/warehouse-issues/issues/166); [DocumentService.java:425](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/platform/backend/src/main/java/ai/platform/service/DocumentService.java#L425).

**Finding:** Document deletion checks checkout state and deletes object storage before the database record; no warehouse reference guard was found in this path. A later FK rejection would not restore the external object.

**Next action:** Check all owning references before storage deletion and cover bulk/deletion variants.

**Close when:** Sealed-carton evidence cannot be deleted; eligible unattached/open evidence follows the documented policy and no dangling object reference remains.

## W14 — Generic bin movement ownership remains unresolved

**Reported · P1 · Scope: Warehouses needing ad hoc internal moves**

**Evidence:** [#176](https://github.com/neetub1508/warehouse-issues/issues/176).

**Finding:** Removal of BIN_TO_BIN from transfer documents leaves a reported unowned generic internal movement workflow. Existing task-driven movements do not prove a general operator path.

**Next action:** Identify the supported movement action and task ownership; do not add an invalid transfer type back by default.

**Close when:** An authorized user moves stock between bins with scope, lot/serial, capacity and ledger evidence, using a documented UI/API.

## W15 — Emergency replenishment issue is partly stale

**Documentation / verification · P2 · Scope: Picking and pick-face replenishment**

**Evidence:** [#177](https://github.com/neetub1508/warehouse-issues/issues/177); [WhPickTaskWriter.java:520](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse/backend/src/main/java/ai/warehouse/service/whpicktask/WhPickTaskWriter.java#L520); [WhReplenishmentTaskGenerator.java:257](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse/backend/src/main/java/ai/warehouse/service/whreplenishmenttask/WhReplenishmentTaskGenerator.java#L257).

**Finding:** Current short-pick code raises or escalates replenishment through the task path. The old issue wording saying nothing is built no longer describes all current behavior.

**Next action:** Reconcile the obsolete BIN_TO_BIN acceptance with current task flow and run the full short-pick recovery.

**Close when:** Short pick → one replenishment task → physical move → resumed demand works without duplicate task or unsupported transfer type.

## W16 — Replenishment source is not reserved when task is raised

**Accepted limitation · P2 · Scope: Concurrent pick-face replenishment**

**Evidence:** [pick-face-replenishment.contract.md:137](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse/docs/contracts/pick-face-replenishment.contract.md#L137).

**Finding:** The documented behavior permits source stock to be consumed before the task completes; completion then refuses.

**Next action:** Measure customer impact and either retain the explicit refusal/recovery flow or add properly released source reservation.

**Close when:** Competing picks cannot create negative stock; operator receives a recoverable shortage and can cancel/regenerate work.

## W17 — Partial pick-face replenishment is unsupported

**Accepted limitation · P2 · Scope: Pick-face replenishment**

**Evidence:** [pick-face-replenishment.contract.md:138](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse/docs/contracts/pick-face-replenishment.contract.md#L138).

**Finding:** Documented workaround is cancel and regenerate; partial completion is not built.

**Next action:** Disclose the limitation and validate operator recovery; implement partial completion only if required for the selected customer.

**Close when:** Moving less than requested has a documented, auditable recovery with no phantom full completion.

## W18 — Replenishment priority is not recalculated at claim time

**Accepted limitation · P2 · Scope: Busy task queues**

**Evidence:** [pick-face-replenishment.contract.md:140](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse/docs/contracts/pick-face-replenishment.contract.md#L140).

**Finding:** Current contract intentionally defers recalculating starvation priority during claim.

**Next action:** Validate queue behavior under load and disclose the scheduling rule; avoid claiming dynamic priority not implemented.

**Close when:** High-priority emergency tasks are claimable as specified and stale priorities do not leave operators without a recovery action.

## W19 — Generic task completion/cancellation signaling is inconsistent or unproven

**Code-supported / verification · P1 · Scope: Shared task console and app task families**

**Evidence:** [task.contract.md:130](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-base/docs/contracts/task.contract.md#L130); [WhbTaskService.java:428](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-base/backend/src/main/java/ai/warehousebase/service/WhbTaskService.java#L428); [WhPutawayTaskService.java:496](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse/backend/src/main/java/ai/warehouse/service/WhPutawayTaskService.java#L496).

**Finding:** App paths emit completion events; the reviewed generic base completion path changes task state and audit without the same event emission. Contract open items identify app reconciliation questions.

**Next action:** Trace each allowed supervisor transition to the owning operational document and event; respect existing PICK/PUTAWAY restrictions.

**Close when:** Supervisor cancellation/exception completion cannot strand held stock, child documents or downstream billing state.

## W20 — Blocked-task alert setting has no consumer found

**Code-supported · P2 · Scope: Task operations monitoring**

**Evidence:** [task.contract.md:142](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-base/docs/contracts/task.contract.md#L142); [warehouse/backend/src/main/resources/db/migration/V511200__Seed_warehouse_app_admin_settings.sql](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse/backend/src/main/resources/db/migration/V511200__Seed_warehouse_app_admin_settings.sql).

**Finding:** warehouse.tasks.blocked_alert_minutes is seeded; source search found no Java consumer. The old contract also incorrectly says the setting is absent.

**Next action:** Connect the adopted blocked-state definition to the existing alert framework and update the contract.

**Close when:** A qualifying blocked task alerts once after the configured threshold and resolves without approving/discarding work.

## W21 — Snapshot schedule outage and missing-day recovery need proof

**Verification gap · P1 · Scope: Snapshot-dependent reports and 3PL storage**

**Evidence:** [WhbPositionSnapshotService.java:33](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-base/backend/src/main/java/ai/warehousebase/service/ledger/snapshot/WhbPositionSnapshotService.java#L33); [warehouse-base/INSTALL.md](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-base/INSTALL.md).

**Finding:** Snapshots select sites in the last quarter-hour of their local day. The install guide says missed history cannot be backfilled. A scheduler outage can therefore create a meaningful missing day.

**Next action:** Prove outage detection and agreed recovery; distinguish a missing snapshot from zero occupancy.

**Close when:** A missed daily snapshot raises a visible exception; reports/billing do not silently interpret missing history as no stock.

## W22 — Full-history ageing performance remains unmeasured

**Verification gap · P1 · Scope: Large/old ledgers**

**Evidence:** [#182](https://github.com/neetub1508/warehouse-issues/issues/182); [WhStockAgeingRepositoryCustomImpl.java:1](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse/backend/src/main/java/ai/warehouse/repository/WhStockAgeingRepositoryCustomImpl.java#L1).

**Finding:** Removing the lower window protects old stock correctness but requires a measured query plan and workload test. Later last-outward changes do not themselves prove scale.

**Next action:** Benchmark representative history, indexes and concurrent operations; retain correctness.

**Close when:** Oldest-stock buckets remain correct and latency meets an agreed measured target without slowing posting.

## W23 — Archiving and hot-ledger reconstruction are deferred

**Intentional scope limit · P2 · Scope: Long-lived/high-volume deployments**

**Evidence:** [#94](https://github.com/neetub1508/warehouse-issues/issues/94).

**Finding:** Archiving is a later-version task. It must not be assumed operational just because partitions and retention configuration exist.

**Next action:** Publish supported retention/capacity bounds; implement archival opening balances before activating archive.

**Close when:** Any future archive preserves rebuild and audit checks; current deployments have a measured storage-growth plan.

## W24 — Scheduled reports cannot yet guarantee recipient-specific scope

**Code-supported / reported · P1 · Scope: Customers enabling scheduled warehouse reports**

**Evidence:** [#185](https://github.com/neetub1508/warehouse-issues/issues/185); [ReportGenerationService.java:1](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/platform/backend/src/main/java/ai/platform/service/report/ReportGenerationService.java#L1).

**Finding:** The recorded platform contract collects/render once per execution and lacks recipient identity for data filtering. Interactive scope does not prove scheduled scope.

**Next action:** Implement recipient-scoped collection/rendering in the existing reporting framework before enabling sensitive warehouse schedules.

**Close when:** Two recipients with different sites receive different authorized data; restricted costs remain masked.

## W25 — Stock-to-GL search treats literal wildcards as patterns

**Reported · P2 · Scope: Stock-to-GL reporting**

**Evidence:** [#180](https://github.com/neetub1508/warehouse-issues/issues/180).

**Finding:** The issue records unescaped percent/underscore matching in a bound LIKE parameter. This is search semantics, not SQL injection.

**Next action:** Verify current query and escape literal search consistently.

**Close when:** Searching ITEM_1 does not also match ITEMX1 unless wildcard search is explicitly requested.

## W26 — Stock-period Site sort is advertised but unsupported

**Code-supported · P2 · Scope: Stock period administration**

**Evidence:** [#192](https://github.com/neetub1508/warehouse-issues/issues/192); [WhbStockPeriodQueryService.java:54](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-base/backend/src/main/java/ai/warehousebase/service/whbstockperiod/WhbStockPeriodQueryService.java#L54).

**Finding:** The query map excludes warehouseName while the issue records it as a sortable grid field.

**Next action:** Align saved preferences, grid metadata and SQL sort support.

**Close when:** Selecting Site sort produces correct order or the UI no longer offers an unsupported choice.

## W27 — Opening-stock row validation filter has no operator surface

**Reported / UI check · P2 · Scope: Opening-stock onboarding**

**Evidence:** [#181](https://github.com/neetub1508/warehouse-issues/issues/181); [warehouse/frontend/src/components/whOpeningStock/WhOpeningStockViewModal.tsx](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse/frontend/src/components/whOpeningStock/WhOpeningStockViewModal.tsx).

**Finding:** A seeded child-grid filter has no matching filter strip; the reported consequence is difficulty isolating invalid rows.

**Next action:** Add a supported filter or align metadata and error-download workflow.

**Close when:** An operator can isolate invalid rows in a large staged batch and export/fix them without scanning all rows.

## W28 — Receiving-session export label differs from grid

**Code-supported · P3 · Scope: Receiving exports**

**Evidence:** [#190](https://github.com/neetub1508/warehouse-issues/issues/190); [WhReceivingSessionExportService.java:77](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse/backend/src/main/java/ai/warehouse/service/WhReceivingSessionExportService.java#L77).

**Finding:** Export still labels the site column Warehouse instead of the grid’s Site.

**Next action:** Align the label and translations across formats.

**Close when:** Grid, CSV and spreadsheet use the agreed same label.

## W29 — Handover shipment picker renders a null name

**Code-supported · P3 · Scope: Carrier handovers**

**Evidence:** [#194](https://github.com/neetub1508/warehouse-issues/issues/194); [WhHandoverQueryService.java:219](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse/backend/src/main/java/ai/warehouse/service/whhandover/WhHandoverQueryService.java#L219).

**Finding:** Description concatenates tracking with nullable ship-to text.

**Next action:** Join only present display fields.

**Close when:** Tracking-only and name-only shipments have clean labels with no literal null.

## W30 — Site-access denial reports misleading permission

**Reported · P2 · Scope: All scoped operations**

**Evidence:** [#187](https://github.com/neetub1508/warehouse-issues/issues/187); [GlobalExceptionHandler.java:187](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/platform/backend/src/main/java/ai/platform/exception/GlobalExceptionHandler.java#L187).

**Finding:** The recorded platform handler substitutes endpoint permissions for site-scope failure detail. This is misleading diagnostics, not proof of unauthorized access.

**Next action:** Preserve safe structured scope-denial codes and messages.

**Close when:** User can distinguish lacking endpoint permission from lacking access to the selected site.

## W31 — Date/filter/export consistency still needs broad UI verification

**Verification gap · P2 · Scope: Operational registers and saved filters**

**Evidence:** [WhExpiryRegisterQueryService.java:1](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse/backend/src/main/java/ai/warehouse/service/whexpiryregister/WhExpiryRegisterQueryService.java#L1); [warehouse/frontend/src/app/dashboard/warehouse/reports/expiry/page.tsx](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse/frontend/src/app/dashboard/warehouse/reports/expiry/page.tsx).

**Finding:** Date handling is actively changing across the suite. Source/gate checks do not prove saved-filter migration, site/user date boundaries and exported results agree across all warehouse screens.

**Next action:** Run representative date-only and timestamp boundary cases with saved filters and multiple timezones.

**Close when:** Grid, totals, detail and export agree on included rows around midnight, month end and daylight-saving boundaries.

## W32 — Install and contract documents contain contradictory current-state claims

**Documentation drift · P1 · Scope: All installs**

**Evidence:** [warehouse-base/INSTALL.md](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-base/INSTALL.md); [task.contract.md:1](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-base/docs/contracts/task.contract.md#L1); [outbox.contract.md:1](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-base/docs/contracts/outbox.contract.md#L1).

**Finding:** Install guide still says ledger not built and restore path absent despite implemented ledger and restore helper. Other open sections describe work now implemented.

**Next action:** Rewrite current behavior, retain historical notes separately, and reconcile the adopted decision hierarchy.

**Close when:** A new operator can follow the guide without direct SQL guesses or contradictions; each outstanding limitation has a current owner/evidence.

## W33 — Warehouse-only disaster recovery is not demonstrated

**Verification / integration gap · P0 · Scope: Every production deployment**

**Evidence:** [DatabaseBackupService.java:390](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/platform/backend/src/main/java/ai/platform/service/DatabaseBackupService.java#L390); [accounting-base/backend/src/main/java/ai/accountingbase/service/jobs/AccRestoreVerifyJob.java](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/accounting-base/backend/src/main/java/ai/accountingbase/service/jobs/AccRestoreVerifyJob.java); [shared/scripts/start.sh](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/shared/scripts/start.sh).

**Finding:** Backup and scratch restore exist; the scheduled verification found is accounting-owned. No warehouse-only restore/rebuild/value/hash-chain recovery evidence was established. PITR and achieved recovery objectives remain unproven.

**Next action:** Run an isolated recovery drill for the actual deployment, including object attachments and replay state; agree measured recovery objectives.

**Close when:** Recovered stock, valuation and hash chain reconcile to known checkpoints; no duplicate external execution; recovery duration/data loss recorded.

## W34 — Database integration tests are outside the passing default gate

**Verified test-scope gap · P1 · Scope: All warehouse modules**

**Evidence:** [warehouse-base/backend/pom.xml](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-base/backend/pom.xml); [warehouse/backend/pom.xml](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse/backend/pom.xml); [shared/scripts/ci-gate/20-warehouse.def](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/shared/scripts/ci-gate/20-warehouse.def).

**Finding:** Module Surefire configuration excludes IntegrationTest.java; many tests also require TESTCONTAINERS_ENABLED. The fresh default gate pass does not exercise those database/concurrency scenarios.

**Next action:** Provide an explicit isolated integration-test job and retain its results per commit.

**Close when:** Ledger, allocation, costs, claims, reversals, imports, holds, 3PL storage and India reach-back integration tests actually execute and pass.

## W35 — The standalone acceptance sequence remains incompletely demonstrated

**Reported verification gap · P1 · Scope: Initial warehouse release**

**Evidence:** [#186](https://github.com/neetub1508/warehouse-issues/issues/186).

**Finding:** The earlier run demonstrated 060–062 but not 044–059 in sequence. The catalogue is now available; lack of access is no longer a reason to leave the sequence undefined.

**Next action:** Execute 044–062 in order on an isolated Mode-A install and preserve setup/data/results.

**Close when:** One install proves onboarding, receive/putaway, order/pick/ship, return, transfer, count and independent reconciliation without accounting/vertical modules.

## W36 — Frontend test breadth does not establish operator-flow readiness

**Verification gap · P1 · Scope: All advertised UI workflows**

**Evidence:** [warehouse-base/frontend/src/__tests__](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-base/frontend/src/__tests__); [warehouse/frontend/src/__tests__](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse/frontend/src/__tests__).

**Finding:** Inventory found 225 page files and eight frontend test files across the four modules, largely metadata/contract checks. Counts do not prove or disprove coverage, but no complete browser workflow evidence was established.

**Next action:** Add/run representative browser acceptance and operator walkthroughs rather than treating metadata tests as task-flow tests.

**Close when:** Users can complete core flows, refusal/retry paths and corrections with scoped roles and realistic data.

## W37 — Warehouse is deliberately web-only and online-only

**Intentional scope limit · P2 · Scope: Handheld/offline customer fit**

**Evidence:** [warehouse-base/INSTALL.md](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-base/INSTALL.md); [warehouse-base/frontend/src/__tests__/warehouseMobileDecisionGate.test.ts](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-base/frontend/src/__tests__/warehouseMobileDecisionGate.test.ts).

**Finding:** The September 11 user decision excludes native warehouse mobile, nine RF screens and offline queue. Do not count these as accidental implementation defects or quietly rebuild them.

**Next action:** Sell the supported web workflow; validate browser/scanner ergonomics. Reconsider scope only for customers who require RF/offline operation.

**Close when:** Sales/demo/install guide agree; lost connectivity has an explicit paper/re-entry procedure and no unsupported offline promise.

## W38 — Physical scanner, printer and device operation is not field-proven

**Verification gap · P1 · Scope: Barcode/label-dependent customers**

**Evidence:** [warehouse/frontend/src/app/dashboard/warehouse/printing](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse/frontend/src/app/dashboard/warehouse/printing); [warehouse-base/frontend/src/app/dashboard/warehouse/ledger/scan](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-base/frontend/src/app/dashboard/warehouse/ledger/scan).

**Finding:** Software routes and device records do not prove hardware connectivity, scan formats, printer retry or label readability.

**Next action:** Test the supported device/browser/printer combinations on a representative network.

**Close when:** Scan resolves correct item/lot/serial/LPN; reprint preserves identity; printer failure/retry is visible and does not duplicate stock.

## W39 — Frontend health endpoint fails, with an additional localhost binding mismatch

**Runtime-observed · P1 · Scope: Observed deployment monitoring**

**Evidence:** [platform/frontend/src/app/api/health/route.ts](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/platform/frontend/src/app/api/health/route.ts); [shared/docker/Dockerfile.frontend](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/shared/docker/Dockerfile.frontend).

**Finding:** Docker health checks fail connecting to IPv6 localhost. The root page responds HTTP 200 over IPv4, but the exact /api/health endpoint returns HTTP 503: environment is not defined. Current route.ts logs an undeclared environment identifier. This is a runtime-observed shared-platform dependency affecting warehouse deployment.

**Next action:** Fix the undefined health-route variable and align the health-check address with the bind address; verify the exact endpoint and container readiness.

**Close when:** The health endpoint returns its intended status without ReferenceError, and Docker health checks reflect application readiness.

## W40 — Fresh install / upgrade / module combinations need runtime proof

**Verification gap · P1 · Scope: Every sold configuration**

**Evidence:** [warehouse-base/INSTALL.md](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-base/INSTALL.md); [shared/scripts/ci-gate/20-warehouse.def](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/shared/scripts/ci-gate/20-warehouse.def).

**Finding:** The gate compiles several modules together; that does not demonstrate clean base-only, warehouse-only, India/3PL activation or later lower-band migrations on a real DB.

**Next action:** Run the supported deployment matrix with seeded roles/settings and an upgrade copy.

**Close when:** All enabled menus/endpoints work; absent optional modules cause clear capability refusal, not missing beans or migration failures.

## W41 — Import validation cache assumes one backend instance

**Code-supported limitation · P1 · Scope: Multi-replica deployments**

**Evidence:** [WhbImportValidationStore.java:17](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-base/backend/src/main/java/ai/warehousebase/service/whbimport/WhbImportValidationStore.java#L17); [import-batch.contract.md:97](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-base/docs/contracts/import-batch.contract.md#L97).

**Finding:** Validation reports use a per-JVM cache. Polling another replica can miss the report.

**Next action:** Document single-instance deployment or implement routing/shared state before scaling out.

**Close when:** Polling/retry across replicas and worker restart has defined behavior and never loses import outcome silently.

## W42 — Import update cannot clear optional values

**Accepted limitation · P2 · Scope: Master-data maintenance**

**Evidence:** [import-batch.contract.md:275](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-base/docs/contracts/import-batch.contract.md#L275).

**Finding:** Blank update cells mean leave unchanged; no clearing token is specified.

**Next action:** Document this clearly and provide an explicit supported clearing operation if customer migration requires it.

**Close when:** A user can distinguish leave unchanged, set value and clear value without destructive ambiguity.

## W43 — Large generated import reverse still needs execution-budget decision

**Reported contract limitation · P2 · Scope: Large master/location imports**

**Evidence:** [import-batch.contract.md:86](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-base/docs/contracts/import-batch.contract.md#L86).

**Finding:** The contract records request-bound validation/dry-run and reverse behavior for generated batches while apply is backgrounded.

**Next action:** Verify current cap/routing and measure large reverse; move work to existing jobs if needed.

**Close when:** Timeout or retry during reversal leaves an unambiguous outcome and no partially reversed batch.

## W44 — Dock data and picker can admit confusing legacy combinations

**Reported / code-supported · P2 · Scope: Dock receiving**

**Evidence:** [dock-door.contract.md:71](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse/docs/contracts/dock-door.contract.md#L71); [WhDockDoorValidationService.java:44](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse/backend/src/main/java/ai/warehouse/service/whdockdoor/WhDockDoorValidationService.java#L44).

**Finding:** Save validation exists, but contract records legacy doors on non-DOCK locations and a picker offering invalid types.

**Next action:** Reconcile legacy data and check-in validation; narrow the selector or explain invalid choices before save.

**Close when:** New doors use valid dock locations; legacy invalid rows have a clear supported correction path.

## W45 — Regulated-item setup refuses contradictions too late

**Reported conditional gap · P1 · Scope: Only enabled regulated profiles**

**Evidence:** [#188](https://github.com/neetub1508/warehouse-issues/issues/188).

**Finding:** The issue records non-lot-controlled regulated items being accepted at setup and refused at dispatch. Other requested jurisdiction fields remain adviser-gated.

**Next action:** Validate the enabled profile’s contradictions at item save; confirm profile-specific requirements before implementation.

**Close when:** Activation/setup catches invalid item configuration before goods reach dispatch; disabled profiles make no compliance promise.

## W46 — Optional tax-basis valuation remains deferred

**Intentional scope limit · P1 · Scope: Only customers needing the second valuation basis**

**Evidence:** [#75](https://github.com/neetub1508/warehouse-issues/issues/75).

**Finding:** A separate tax-basis inventory value is recorded as future work. Ordinary book valuation does not establish this capability.

**Next action:** Keep unsupported basis unavailable; implement and validate only for applicable contracted scope.

**Close when:** Book and tax bases are separately labeled, reconciled and never summed as one inventory value.

## W47 — Provider-backed operational features require actual connector evidence

**Verification gap · P1 · Scope: Enabled tax, carrier, drop-ship and other providers**

**Evidence:** [WhDropShipAvailability.java:1](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse/backend/src/main/java/ai/warehouse/service/whdropship/WhDropShipAvailability.java#L1); [WhinComplianceProviderService.java:1](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-india/backend/src/main/java/ai/warehouseindia/service/WhinComplianceProviderService.java#L1).

**Finding:** Registries and adapter ports do not establish a working customer provider. Credentials and external-system behavior were not exercised.

**Next action:** List supported providers and run sandbox acceptance for every sold connector; enforce unavailable-capability gates.

**Close when:** Authentication, retry, duplicate acknowledgment, timeout, rejection, cancellation and recovery work with the actual provider.

## W48 — 3PL billing needs an independent cycle-level reconciliation

**Verification gap · P1 · Scope: 3PL customers**

**Evidence:** [warehouse-3pl/backend/src/test/java/ai/warehouse3pl/service/wh3plstoragebilling/Wh3plStorageBillingSnapshotDayIntegrationTest.java](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-3pl/backend/src/test/java/ai/warehouse3pl/service/wh3plstoragebilling/Wh3plStorageBillingSnapshotDayIntegrationTest.java); [#122](https://github.com/neetub1508/warehouse-issues/issues/122).

**Finding:** Unit/contract tests passed in the current backend gate, but database storage billing and a complete client billing cycle were not demonstrated in this audit. Rate escalation/SLA credits/profitability are separate deferred capabilities.

**Next action:** Run occupancy/handling/VAS/rate-version/dispute/credit scenarios against independently calculated results.

**Close when:** One full bill reconciles to stock snapshots and events, with owner isolation and no duplicate charges after retry.

## W49 — Permissions need adversarial workflow tests, not only annotations

**Verification gap · P1 · Scope: Every deployment**

**Evidence:** [warehouse/backend/src/test/java/ai/warehouse/architecture/WhWarehouseScopeContractTest.java](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse/backend/src/test/java/ai/warehouse/architecture/WhWarehouseScopeContractTest.java); [warehouse/backend/src/test/java/ai/warehouse/architecture/WhOwnerScopeContractTest.java](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse/backend/src/test/java/ai/warehouse/architecture/WhOwnerScopeContractTest.java).

**Finding:** Scope architecture tests pass, but complete cross-site/owner access and indirect export/attachment/public-link behavior were not exercised against deployed roles.

**Next action:** Test ordinary operator, supervisor, finance and external-user roles across reads/writes/exports/links.

**Close when:** Foreign IDs, changed filters, stale grants and bulk actions do not widen scope; legitimate transfer receipt exceptions remain narrow.

## W50 — Idempotency/concurrency across the complete order flow needs proof

**Verification gap · P1 · Scope: Every transactional deployment**

**Evidence:** [warehouse-base/backend/src/test/java/ai/warehousebase/service/allocation/WhbAllocationIntegrationTest.java](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-base/backend/src/test/java/ai/warehousebase/service/allocation/WhbAllocationIntegrationTest.java); [warehouse/backend/src/test/java/ai/warehouse/service/whawbpool/WhAwbClaimConcurrencyIntegrationTest.java](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse/backend/src/test/java/ai/warehouse/service/whawbpool/WhAwbClaimConcurrencyIntegrationTest.java).

**Finding:** Relevant database concurrency tests exist but are outside the default gate. Whole-flow retry behavior was not reproduced.

**Next action:** Exercise competing reservations, double dispatch, partial receipt, cancellation and retry after lost response in an isolated database.

**Close when:** No oversell, duplicate movement, reused serial/AWB or orphan reservation; accepted operations recover their original identity.

## W51 — Cut-over performance and opening-stock reversal need measured evidence

**Verification gap · P1 · Scope: Customer onboarding**

**Evidence:** [warehouse/docs/runbooks/opening-stock-cutover.md](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse/docs/runbooks/opening-stock-cutover.md).

**Finding:** A detailed runbook and content-hash protection exist. The stated 38,000-position timing and full cut-over/reversal sequence were not benchmarked here.

**Next action:** Time the supported reference load and prove freeze/count/post/certify/reverse/retry with independent values.

**Close when:** Opening quantity/value tie out, duplicate content is refused and reversal invalidates certification without losing lineage.

## W52 — Alert and background-job recovery need an operational drill

**Verification gap · P1 · Scope: Every production deployment**

**Evidence:** [WhbIntegrationHealthSignalSource.java:1](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-base/backend/src/main/java/ai/warehousebase/service/jobs/WhbIntegrationHealthSignalSource.java#L1); [WhbJobRunner.java:1](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-base/backend/src/main/java/ai/warehousebase/service/jobs/WhbJobRunner.java#L1).

**Finding:** Outbox lag/silent-subscription monitoring and job recovery exist. Generic statements that warehouse has no monitoring would be wrong; actual incident response remains unproven.

**Next action:** Exercise dead delivery, stuck job, missed schedule and scope-safe notifications; publish the operator runbook.

**Close when:** Alert reaches the right operator, names affected work and supports safe retry without skipping stock events.

## W53 — Production performance and resource limits lack a current benchmark

**Verification gap · P1 · Scope: Agreed customer size**

**Evidence:** [warehouse-base/backend/src/test/java/ai/warehousebase/nonfunctional/LedgerVolumeFixtureTest.java](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-base/backend/src/test/java/ai/warehousebase/nonfunctional/LedgerVolumeFixtureTest.java).

**Finding:** The volume fixture needs an external DB setting and does not establish a current measured customer envelope. Default gate counts are not throughput figures.

**Next action:** Benchmark posting, allocation, search, counts, reports, import and concurrent users at the intended scale.

**Close when:** Publish data size/hardware/concurrency and percentile latency; heavy reports stay within agreed execution impact.

## W54 — Backup retention, attachments and external acknowledgments need one recovery policy

**Verification gap · P1 · Scope: Every production deployment**

**Evidence:** [DatabaseBackupService.java:1](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/platform/backend/src/main/java/ai/platform/service/DatabaseBackupService.java#L1); [DocumentService.java:1](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/platform/backend/src/main/java/ai/platform/service/DocumentService.java#L1); [outbox.contract.md:1](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-base/docs/contracts/outbox.contract.md#L1).

**Finding:** Database dump recovery alone does not prove attachment availability, key configuration or agreement with external receivers after restore.

**Next action:** Define coordinated backup/retention/reconciliation for DB, object storage and external delivery state.

**Close when:** Restore cannot reference missing evidence or resend acknowledged business events without controlled reconciliation.

## W55 — Data import handoff and document permissions complicate onboarding

**Accepted limitation / verification · P2 · Scope: Multi-user onboarding**

**Evidence:** [import-batch.contract.md:273](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-base/docs/contracts/import-batch.contract.md#L273).

**Finding:** Contract limits large-file validation to uploader/admin under platform document ownership. Batch expiry and abandoned report behavior also need clear operator guidance.

**Next action:** Document handoff rights, cleanup and recovery; use existing grants rather than bypasses.

**Close when:** An authorized onboarding team can resume/fix an import under the agreed role model without sharing accounts.

## W56 — Product promises exceed the evidence in some help text

**Documentation / commercial readiness · P2 · Scope: Sales/help/training**

**Evidence:** [warehouse-base/frontend/src/components/warehouseCatalogues/WhbTaskTypeModal.tsx](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-base/frontend/src/components/warehouseCatalogues/WhbTaskTypeModal.tsx); [warehouse-base/INSTALL.md](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-base/INSTALL.md).

**Finding:** Help text includes numerical scan-accuracy claims and handheld references while warehouse mobile is explicitly absent. These are not measured product outcomes from this audit.

**Next action:** Remove unsupported percentages and stale workflows; publish actual supported configuration and limitations.

**Close when:** Demo, help, proposals and install guide describe the same shipped workflow and measured claims.

## W57 — Operational KPI semantics and coexistence defaults require sign-off

**Reported / verification · P2 · Scope: Management reports and legacy coexistence**

**Evidence:** [#184](https://github.com/neetub1508/warehouse-issues/issues/184); [#178](https://github.com/neetub1508/warehouse-issues/issues/178).

**Finding:** Open issues record reversible report decisions, including side-by-side valuations without a combined grand total. They are product choices, not automatically defects.

**Next action:** Confirm adopted defaults, explain them in reports, and independently reconcile KPI denominators and cost bases.

**Close when:** Users can reproduce key metrics and distinguish native/external stock values; no misleading combined valuation.

## W58 — Existing demand-merge option has no calculation consumer found

**Code-supported · P2 · Scope: Only advertised supersession demand reporting**

**Evidence:** [#168](https://github.com/neetub1508/warehouse-issues/issues/168); [WhbItemSupersessionService.java:173](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-base/backend/src/main/java/ai/warehousebase/service/WhbItemSupersessionService.java#L173).

**Finding:** The warehouse exposes the treatment but source search found configuration/validation rather than a consumer. This item concerns existing warehouse reporting semantics only; forecasting is excluded.

**Next action:** Either implement the promised current-report behavior or label/disable the unavailable treatment in the warehouse-only offer.

**Close when:** Choosing the treatment has the documented reporting effect; physical substitution remains separately controlled.

## W59 — Advanced operational features must remain explicitly outside the basic offer

**Intentional scope limit · P2 · Scope: Customer/package selection**

**Evidence:** [#103](https://github.com/neetub1508/warehouse-issues/issues/103); [#109](https://github.com/neetub1508/warehouse-issues/issues/109); [#112](https://github.com/neetub1508/warehouse-issues/issues/112); [#131](https://github.com/neetub1508/warehouse-issues/issues/131); [#138](https://github.com/neetub1508/warehouse-issues/issues/138); [#142](https://github.com/neetub1508/warehouse-issues/issues/142); [#144](https://github.com/neetub1508/warehouse-issues/issues/144).

**Finding:** Engineered labor/incentive pay, robotics control, supplier scorecard, logistics, dashboard expansion, accessories absorption and manufacturing routings are deferred or deliberately outside scope. They are not universal release blockers.

**Next action:** Publish the supported warehouse-only package and extension boundaries; do not quietly rebuild removed adapters or promise future work as shipped.

**Close when:** Customer requirements are mapped to supported workflows or explicit exclusions before go-live.

## W60 — Filter parity gate cannot reliably parse current filter declarations/helpers

**Verified gate failure · P1 · Scope: Frontend release gate**

**Evidence:** [warehouse/frontend/src/__tests__/whGridFilterParity.test.ts](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse/frontend/src/__tests__/whGridFilterParity.test.ts).

**Finding:** 45 assertions fail. Demonstrated scanner defects include one-line FilterFieldConfig definitions and APIs forwarding filters through a generic withFilters helper. These failures do not establish 45 broken UI filters.

**Next action:** Correct parser/helper recognition and then investigate remaining real UI/API/seed discrepancies.

**Close when:** Every advertised filter is exercised through request to result/export; gate recognizes supported syntax and catches deliberately removed wiring.

## W61 — Registry-label gate has parser/mapping failures and unresolved label checks

**Verified gate failure · P1 · Scope: Frontend labels and release gate**

**Evidence:** [warehouse-base/frontend/src/__tests__/whbRegistryLabelFallback.test.ts](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-base/frontend/src/__tests__/whbRegistryLabelFallback.test.ts).

**Finding:** Six assertions fail, including parser anti-vacuous checks, unknown table mappings and locale label checks. A seeded counterparties table is treated as vocabulary; parser failures prevent treating all reported labels as confirmed omissions.

**Next action:** Fix seed parsing and vocabulary classification; then resolve actual missing en/fr/hi labels.

**Close when:** Gate passes with valid seed shapes and detects a genuinely missing label; rendered customer workflows show appropriate labels.

## W62 — Registry and mobile gates conflate equal strings from different domains

**Verified gate failure · P1 · Scope: Frontend release gate**

**Evidence:** [warehouse-base/frontend/src/__tests__/warehouseMobileDecisionGate.test.ts](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-base/frontend/src/__tests__/warehouseMobileDecisionGate.test.ts); [warehouse-base/frontend/src/__tests__/warehouseRegistryOpenness.test.ts](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-base/frontend/src/__tests__/warehouseRegistryOpenness.test.ts).

**Finding:** Three assertions fail. Global literal intersections flag common words such as HIGH/LOW in other mobile domains and WAREHOUSE in a closed job-scope type. Demonstrated domain collisions require triage; not every flagged union violates registry openness.

**Next action:** Use field/domain-aware checks while preserving actual extensibility constraints. Do not remove unrelated enums or build warehouse mobile to satisfy a lexical scanner.

**Close when:** Gates distinguish closed system enums from warehouse registries and detect actual hardcoded warehouse vocabulary.

## W63 — Carrier and shipment lifecycle has recorded unowned transitions

**Reported closed-issue carry-forward · P1 · Scope: Carrier-integrated shipping**

**Evidence:** [#10](https://github.com/neetub1508/warehouse-issues/issues/10).

**Finding:** Closed exit issue records DELIVERED-to-shipment status, AWB-to-tracking-number mapping, auto-void AWB on shipment cancel and automatic reversal of related charges as unowned/unbuilt. Manual compensating reversal was demonstrated. Current provider-specific paths need targeted verification.

**Next action:** Assign current owners and prove each transition; reconcile provider acknowledgments, local shipment state and charges.

**Close when:** Dispatch, delivery and cancellation keep shipment, label/tracking and charges consistent under retry, delayed webhook and failed void.

## W64 — Client offboarding and accounting-related operational follow-ups remain recorded

**Reported closed-issue carry-forward · P1 · Scope: 3PL/client portal and integrated accounting**

**Evidence:** [#10](https://github.com/neetub1508/warehouse-issues/issues/10).

**Finding:** The exit comment lists offboarding end date, COD/AR sinks, X-068 G-013 FK ruling and Stock-to-GL showing zero as ownerless. Accounting ports are separately covered in W10; a displayed zero must not imply a real reconciliation.

**Next action:** Triage each against current source and assign disposition. Enforce agreed offboarding cutoff and distinguish unavailable reconciliation from zero balance.

**Close when:** Offboarded access and transactions obey dates; unavailable financial integrations are explicit; the FK decision is reflected consistently in schema and deletes.

## W65 — Task assignment may accept an inactive or out-of-site operator

**Reported closed-issue carry-forward · P1 · Scope: Task queue assignment**

**Evidence:** [#14](https://github.com/neetub1508/warehouse-issues/issues/14).

**Finding:** Closure explicitly records assignment without checking that the named operator is active and authorized at the site. No fresh runtime reproduction was performed.

**Next action:** Trace current assignment and reassignment endpoints and enforce eligibility consistently.

**Close when:** Inactive/out-of-site assignees are refused; revocation after assignment has a defined reclaim/escalation path.

## W66 — Paper catch-up and device session edge cases need acceptance

**Reported closed-issue carry-forward · P2 · Scope: Device sessions and continuity**

**Evidence:** [#23](https://github.com/neetub1508/warehouse-issues/issues/23); [#19](https://github.com/neetub1508/warehouse-issues/issues/19).

**Finding:** Recorded gaps: supervisor-only catch-up not enforced; batch tests use stand-in posting; catch-up test bypasses movement port; expired-session task ownership is not transferred; force sign-out also ends web sessions; version checks apply only to device-session requests. Some are deliberate limits needing clear policy.

**Next action:** Validate the supported web/device flow and permissions; document session blast radius and task recovery.

**Close when:** Catch-up requires the intended role, preserves event time and transaction isolation, and expired sessions leave recoverable tasks without duplicate posting.

## W67 — GS1 pallet identity remains intentionally deferred

**Intentional scope limit · P2 · Scope: Trading partners requiring GS1**

**Evidence:** [#121](https://github.com/neetub1508/warehouse-issues/issues/121).

**Finding:** Closed as not planned for v1: customer-prefix SSCC allocation, GS1-128/Digital Link parsing, EPC and settings. Generic labels must not be marketed as these capabilities.

**Next action:** Keep unsupported format switches locked; validate a customer-driven GS1 implementation before enabling it.

**Close when:** Supported identifiers remain stable; a GS1-requiring customer has validated allocation/parser/label workflows or is outside the release scope.

## W68 — Weighing and labour capture have recorded interface limits

**Intentional / reported limitation · P2 · Scope: Weighing and labour-enabled operations**

**Evidence:** [#91](https://github.com/neetub1508/warehouse-issues/issues/91).

**Finding:** Labour timing is API-only under the no-mobile decision; return-receipt weighing warning is deferred.

**Next action:** Describe current capture method; validate return weighing if sold. Do not assume a native timer screen exists.

**Close when:** Operators can use the supported capture flow; returns behave according to the advertised weight-tolerance policy.

## W69 — India e-way lifecycle has recorded state and race gaps

**Reported closed-issue carry-forward · P1 · Scope: Enabled India e-way workflow**

**Evidence:** [#147](https://github.com/neetub1508/warehouse-issues/issues/147).

**Finding:** Recorded follow-ups: expired never-moved bill clears only through challan cancellation; CLOSED unreachable in v1; already-live filing without accepted record stays Part A pending; challan cancellation check lacks row lock; failed-after-filed cancellation untested; pending cancellation wording misleading; response time measures local system; English fallback labels remain.

**Next action:** Reconcile current implementation and accepted states; test concurrent dispatch/cancel and provider ambiguity; correct UI diagnostics.

**Close when:** Documented lifecycle has no unexplained stranded state and cannot dispatch against invalid/cancelled evidence after a race. Provider recovery and display semantics are explicit.

## W70 — India challan evidence and setup need further closure

**Reported closed-issue carry-forward · P1 · Scope: Enabled India challans**

**Evidence:** [#140](https://github.com/neetub1508/warehouse-issues/issues/140).

**Finding:** Recorded follow-ups: concurrent issuing untested; new-branch series manual; legal name/transport details read at print time rather than frozen at issue; demand-order source always non-taxable; source-eligibility cases incomplete; GSTIN profile dates show timezone shift. Transfer-source scenarios were code-read only in earlier acceptance.

**Next action:** Verify current state; freeze required issue-time evidence, validate branch setup and source decisions, and execute concurrent/transfer/date cases.

**Close when:** Reprints preserve required historical evidence, issuance is unique, supported sources behave correctly and calendar dates remain stable across zones.

## W71 — Closed receiving and access work contains unresolved smaller obligations

**Reported closed-issue carry-forward · P2 · Scope: Receiving documents and access model**

**Evidence:** [#113](https://github.com/neetub1508/warehouse-issues/issues/113); [#137](https://github.com/neetub1508/warehouse-issues/issues/137).

**Finding:** Receiving closure records GRN documents deferred without an owner. Access closure records access_level as inert for reads with write semantics undecided. Current advertised attachment and grant behavior requires reconciliation.

**Next action:** Confirm whether these are still promised requirements; assign implementation or explicitly remove the unsupported promise.

**Close when:** Receiving documents have a supported governed path; exposed access levels have clear enforced semantics rather than inert choices.

