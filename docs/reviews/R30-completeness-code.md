# R30 — Completeness audit, part CODE (classic warehouse code vs the P7 removal and rename plan)

*2026-10-23 · read-only · `classic` @ `65b41be8a6` (main, clean) · inputs: `DECISIONS.md` D-16, `reviews/R28` (RN-001…024, §8b),
`frd/FRD-REM.md` (Appendices A–F, §6 gates), `issues/p7-01…p7-13.md` · code: `classic/{warehouse-base,warehouse,warehouse-3pl,warehouse-india}`
plus `platform` (CacheConfiguration, filterUtils, logix client seeds), `*SafeTranslation.tsx`, `shared/docker/*`, `shared/scripts/start.sh`,
`shared/scripts/ci-gate/*.def`, `.claude/tasks/BATCH-WAREHOUSE-*`, `.claude/testing/descriptors`, `mobile/`, every other module root.*

Prefix `CP-CODE-`. `WB` = `warehouse-base/backend/src/main/resources/db/migration`, `W` = `warehouse/…`, `IN` = `warehouse-india/…`,
`LGX` = `platform/backend/src/main/resources/db/client/logix`.

## 0. Method

1. Parsed FRD-REM Appendix A into 478 paths and tested each with `os.path.exists`.
2. Ran GATE-1…GATE-7 of FRD-REM §6, verbatim, over `$W $P` on today's tree (11,570 unique hit lines). Then sorted each hit into one of three classes: in an Appendix-A file (deleted), in a file named by FRD-REM or a P7 task, or in neither. For kept files, I also matched each hit's line against the line ranges that the tasks cite (±3 lines).
3. Ran a broad case-insensitive sweep for the terms in the brief (dealer, retail, e-commerce, storefront, marketplace, channel, COD, AWB/waybill, NDR, RTO, courier, VOR, OEM, workshop, job card/service job, vehicle, VIN, adapter-dealer/services), excluding Appendix-A files and `*.md`.
4. Checked every name that the plan removes or renames against the code: tables, functions, permissions, routes, menus, caches, filter scopes, i18n sections and keys, permission constants, help entries and descriptors.
5. Found every kept Java and TS file that references a deleted class or module (compile-break check). Grepped every non-warehouse root for removed objects.

## 1. Inventory

### 1.1 Hit counts by class (gate scope `$W $P`)

| Class | Lines | Files | Carrier |
|---|---|---|---|
| **Remove — whole file** (Appendix A, all 478 paths exist; A.1 338 Java, A.3 140 FE) | 8,305 | 474 | `P7-02`…`P7-09` per group |
| **Remove — whole migration** (B.1, 20 files, all exist once) | (inside the next row) | 20 | `P7-02`…`P7-10` |
| **Remove / trim inside a kept or rewritten file** (B.2 migrations, Appendix C seams, filterUtils, CacheConfiguration, logix) | 2,676 | 246 | per Appendix B.2 / C |
| **Rename** (`PartsKpi`, `parts-kpis`, `wh_rpt_parts_kpis`, `OEM_PART_NUMBER`, `'VOR'`, `'WORKSHOP'`) | 439 | — | `P7-11` |
| **i18n (deleted sections + vocabulary keys)** | 150 (+ section bodies) | 6 locale files | per Appendix E |
| **Uncovered** (no task names the file or the line) | **≈ 40** | **≈ 30** | see CP-CODE-001…009 |

### 1.2 Broad-term sweep (kept, non-doc files)

| Term | Hits | Class | Note |
|---|---|---|---|
| `vehicle` | 1,892 | false positive | dock-door vehicle types, gate/trip vehicle numbers, e-way bill vehicle updates — transport, not automotive. No `VIN`, chassis or vehicle-model anywhere (0 hits) |
| `AWB` / `waybill` | 5,077 | false positive / keep | e-way bill (`ewaybill`) and the carrier tracking-number word (REM-D12). Pool code is in Appendix A |
| `channel` | 2,274 | keep / trim | `whb_channels` and `channel_id` columns stay (REM-D2). Removed channel features are in Appendix A. Kind trim is `P7-10` |
| `marketplace` | 283 | remove (covered) | residue → CP-CODE-007 |
| `COD` | 225 | remove (covered) | residue → CP-CODE-001, 005, 006 |
| `NDR` / `RTO` | 270 / 251 | remove (covered) | `RPO/RTO` in `NonFunctionalFoundationsTest` = recovery-time objective, false positive. Residue → CP-CODE-005, 007 |
| `OEM` | 105 | remove (covered) / false positive | obsolescence i18n goes with its section. `help.itemIdentifiers.overview` "OEM" part numbers is generic manufacturing wording |
| `dealer` | 108 | mixed | covered: `P7-10`'s list. Uncovered comment residue → CP-CODE-008. Keep: coupling guards (`WarehouseBaseCouplingTest`, `WhbLogisticsSeamContractTest`, `WB/V500054`), the platform module list `WB/V500200:75,120` (REM-D19), and `WhbAccountingMode:60` (accounting fence) |
| `retail` | 31 | false positive | MRP "maximum retail price" (India legal metrology), `DRUG_RETAIL` licence type, "Acme/Nova Retail" test fixtures |
| `courier` | 29 | keep | carrier type `COURIER` (`WhCarrier:53`), 3PL charge `SHP_COURIER` |
| `VOR` | 20 | rename | `P7-11` |
| `workshop` | 13 | rename / uncovered | `WORKSHOP` → `P7-11`. "Workshop Parts" comments → CP-CODE-002 |
| `job card` / `service job` | 19 | remove (covered) / false positive | `JOB_CARD` → `P7-10`. The rest is `jobWorkService` (India job work), a false positive |
| `adapter-(dealer\|services)` | 35 | remove / keep | `P7-10` list. The band ratchet stays (REM-D3). Residue → CP-CODE-002 |
| `e-commerce`, `storefront` | 0, 3 | false positive | `BuildingStorefrontIcon` menu icon |

### 1.3 Names verified to exist exactly as the plan states (step 2)

| Object | Check | Result |
|---|---|---|
| Appendix A files | 478 / 478 exist | OK |
| D.1 tables | all 24 `CREATE TABLE` found, each in the B.1/B.2 file named | OK. Also 13 guard/ladder functions for removed tables. Of these, `wh_cod_remittances_guard` and `wh_shipment_ndrs_guard` are redefined in `W/V511306`, `wh_awb_numbers_guard` in `V511275`, `wh_obsolescence_returns_assert_ladder` in `V510216`, and `wh_cod_remittances_matched_once` in `V511276`/`V511277`. All of these files are named |
| D.2 permissions | per-resource counts match (`wh_obsolescence_returns` 9 = "8 live" + 1 retired; `whb_*` 4 + 2 plus the `V501000` generated rows) | OK |
| D.3 routes / menus | 17 removed routes plus `reports/parts-kpis`: each has one page dir and one seeding migration. Containers `warehouse_channels` (L1 in `V511271`, L3 in `V500051`/`V501101`), `_fulfilment`, `_carriers`, `warehouse_trade`, `_trade_customers` and `warehouse_parts_kpis` all found. `warehouse_shipping*` and `warehouse_stock_kpis` do not exist yet (expected) | OK |
| Caches | `CacheConfiguration` registers 58 warehouse names. Only `dropdown.whChannelAccount` and `dropdown.whChannelPublishRule` are used solely by Appendix-A classes | OK (`P7-04`) |
| filterUtils scopes | all 17 + 7 + `WAREHOUSE_RPT_PARTS_KPI` present. `isDualEligible` `:1021`, `supportsCod` `:1900`. The kept `WAREHOUSE_CARRIER_ACCOUNT.paymentMode` `:1904` is correctly spared | OK. Line numbers drift by 1–10 (re-read rule applies) |
| Permission constants / help entries | all 16 + 2 constants and 15 + 2 help keys found at the cited lines (±5) | OK |
| i18n sections | all 17 `warehouse.json` + 2 `warehouseBase.json` sections present in en/fr/hi, leaf counts equal to Appendix E | OK. `help.rateQuotes`/`carrierServiceability`/`awbPools` exist only as `warehouseHelp.ts` fallbacks (no locale key). Harmless |
| i18n `outboxEvent.eventTypeByCode["channel.inventory.published"]` | **not present under that key.** Stored nested as `eventTypeByCode.channel.inventory.published` | **CP-CODE-004** |
| Descriptors | 17 to delete and 4 to trim all exist | OK, but `wh-consignments.json:44` `_derivation` cites "wh-cod-remittances descriptor" (cosmetic) |
| B.2 FAIL-point lines | `V511248:298`, `V511268:300-306,371`, `V500010:810-813`, `V510050:944-947`, `V500002:461-470`, `V500003:429-433`, `V500004:342` read as cited, and the post-P7 numbers follow from the seed rows (9→4, 13→11, 18→17, 11→9, 10→8) | OK |

### 1.4 Mixed migrations (step 3)

Every warehouse or logix migration that hits a removed term falls into one of these groups:

- B.1: 20 files.
- B.2: 42 files, counting the comment-only row.
- Named exceptions: `WB/V500200` (REM-D19) and `WB/V500005:202` (`P7-10`).
- **Not named anywhere:**
  - `W/V510101:319`, `IN/V540000:33` and `WB/V500001:51` (comments)
  - `IN/V541000:165` (the file is named, but only for `:38`)
  - `LGX/V910031:37-46` (the file is named, but this DDL-bearing INSERT is not)

  See CP-CODE-001 and 002.

Each file that carries both removed DDL and kept DDL is named in B.2 with a carrier task: `V510204`, `V510210`, `V510050`, `V510040`, `V510044`, `V510203`, `V510216`, `V511306`, `V511308`, `V511275`, `V511268`, `V511271`–`V511273`, `WB/V500010`, `WB/V500014`, `WB/V500046`, `IN/V540130` and the logix seeds.

### 1.5 Compile-break check

- **Java.** 299 main classes are deleted. Every kept Java file, in main or test, that names one of them is named in FRD-REM or a P7 task. None is missing.
- **Frontend.** 120 deleted frontend modules. Only three kept files import them: `whCostColumnVisibility.test.tsx`, `supplier-claims/page.tsx` and `WhClaimTransitionModal.tsx`. All three are named. (`platform/.../layout.test.tsx` is a name collision on `layout`, not an import of `(public)/layout.tsx`.)
- **ci-gate.** `20-warehouse.def`'s only executable line that names a removed or renamed class is `:64` (`P7-11`).

## 2. Findings

### CP-CODE-001 · BLOCKER · The logix seed still inserts `supports_cod`, so `WH-SC-678` fails
**Evidence.** `LGX/V910031__logix_wh_outbound.sql:37` is `INSERT INTO wh_carrier_services (…, supports_cod, supports_reverse, …)`, and its value rows at `:41-46` carry `cod`. `P7-03` drops the column (`OD-22`, `V510044:112`). But both `P7-03` and FRD-REM B.2 (row `LGX/V910031`) edit only `:24-34` (carrier clocks) and `:433,448-449` (`P7-04`). A fresh install with `CLIENT_NAME=logix` raises "column supports_cod does not exist". `P7-03`'s acceptance grep would flag the file, but neither the scope, the B.2 table nor the hazard list names it.
**Carrier.** `P7-03`: add `LGX/V910031:37-46` (drop the column and the `v.cod` value) to its Migrations list, to B.2 and to the B.2 hazard list.

### CP-CODE-002 · MAJOR · Five GATE-6 lines have no carrier, so `P7-13` fails GATE-6
**Evidence.** These GATE-6 hits sit in kept files, and no task cites the line:

| File | Line | Text |
|---|---|---|
| `WB/V500001` | `:51` | "warehouse-adapter-dealer may seed it" |
| `WB/V500002` | `:41` | "warehouse-adapter-dealer register itself" |
| `W/V510101` | `:319` | "reserved for the Parts Counter and Workshop Parts sections" |
| `IN/V540000` | `:33` | "or in `warehouse-adapter-dealer`" |
| `IN/V541000` | `:165` | "Parts Counter (P2-25) is 60, Workshop Parts (P2-26) is 70" |

`P7-10` lists `V500002:82,141-149` and `V541000:38`, but not these lines. FRD-REM §6 says a `P7-13` gate failure "is fixed in the owning P7 task's files", so the fix belongs to `P7-10` now.
**Carrier.** `P7-10`: add the five lines to "Doc rewording" / "Menu-slot comments". `V510101` and `V540000` also join B.2's comment-only row.

### CP-CODE-003 · MAJOR · The source-system help text describes the deleted adapter rows, and a kept test pins that text
**Evidence.**
- **Help text.** `help.sourceSystems.overview` in `warehouseBase.json:7878` (en; fr and hi alike) and its fallback in `warehouseBaseHelp.ts:2898` say: "The dealer, services, field service and assets adapter rows and the logistics row are catalogue rows with no module behind them". Once `P7-10` deletes those rows, the text is false. `P7-10` rewords only `help.channels.*`.
- **Test.** `warehouse-base/frontend/src/__tests__/warehouseMobileDecisionGate.test.ts` GATE 3 checks this wording. Its fixtures name "dealer, services, field service and assets adapters" at `:773,800,813`, and `:813` is the anti-false-positive case.
- **INSTALL.md.** `:781-783` of the same test pins the `INSTALL.md` §16 sentence "No planning, forecasting, optimisation or competitor features, and no removed adapters. User decision, 2026-09-30" (`INSTALL.md:2064`). `P7-12` edits `INSTALL.md:2059-2102` as docs-only and runs no tests.

**Carrier.** `P7-10`: reword `help.sourceSystems.overview` (en/fr/hi plus the fallback) and update the test fixtures `:773-813`. `P7-12`: add a trap to keep, or co-edit, the pinned §16 sentence, and run `warehouseMobileDecisionGate` and `NonFunctionalFoundationsTest` (it reads §16.1, `:452`) after the `INSTALL.md` edit.

### CP-CODE-004 · MAJOR · An i18n key is named in a shape that does not exist, so the label survives and no gate catches it
**Evidence.** `P7-04` and FRD-REM Appendix E name the key `outboxEvent.eventTypeByCode["channel.inventory.published"]`. In en/fr/hi `warehouseBase.json` the label is nested instead, as `outboxEvent.eventTypeByCode.channel.inventory.published` (en "Channel inventory published"). That nesting has three effects:
- A delete of the flat key is a no-op.
- GATE-3's `channel\.inventory\.published` cannot match nested JSON keys.
- GATE-8 does not check `warehouseBase` beyond two sections.

The dead label would survive `P7-13` green.
**Carrier.** `P7-04`: delete the subtree `outboxEvent.eventTypeByCode.channel` (it holds only `inventory.published`) and add `jq -e '.outboxEvent.eventTypeByCode | has("channel")'` (false) to its acceptance.

### CP-CODE-005 · MINOR · Reason-code labels for rows seeded only by deleted files are not listed
**Evidence.** `warehouseBase.json` `reasonCode.byCode` (en/fr/hi) keeps labels for codes that only deleted migrations seed:
- `CUSTOMER_REFUSED`, `ADDRESS_INCOMPLETE`, `PREMISES_CLOSED`, `COD_NOT_READY`, `FUTURE_DELIVERY_REQUESTED`, `CARRIER_REPORTED` — seeded only by `W/V510206`, which `P7-03` deletes.
- `CARRIER_REJECTED` — seeded only by `W/V510205`, which `P7-02` deletes.

Appendix E lists only `NDR_*` (5), `CARRIER_INITIATED` and "the RTO reason labels". REM-D8 requires every removed feature's keys to go. `SHIPMENT_CANCELLED`, `CARRIER_CHANGED` and `LABEL_DAMAGED` are also seeded by kept `W/V510103` (and `V510060`), so they **stay**.
**Carrier.** `P7-03` (the six NDR-only labels) and `P7-02` (`CARRIER_REJECTED`). Add them to Appendix E.

### CP-CODE-006 · MINOR · `supportsCod` sites missing from `P7-03`'s list
**Evidence.**
- `warehouse/frontend/src/types/whCarrierService.ts:19,35,44,52`, including the statistics field `supportsCodCount`.
- `components/whCarrierService/WhCarrierServiceFilter.tsx:26,126,128`.
- i18n `carrierService.statistics.supportsCod`.
- The comment `W/V510044:417`.
- The COD prose in `help.carrierServices.{flow1,flow2,purposeDescription}`.

`P7-03` names only the page, Table, Modal and ViewModal. The acceptance grep catches the identifiers but not the help prose.
**Carrier.** `P7-03`.

### CP-CODE-007 · MINOR · Retail prose left in kept files, not assigned to any task
**Evidence (kept files; no gate matches the bare words).**

| Kind | Location | Text |
|---|---|---|
| user-facing error | `WhOrderEditRuleValidationService:50,82` | "after ship there is no edit; the answer is a return or an RTO" |
| i18n | `help.supplierClaims.flow1`, `supplierClaim.hints.headerExplainer` | obsolescence return |
| i18n | `rma.placeholders.externalRef` | marketplace (`P7-05` names only `WhRmaModal.tsx:691`) |
| i18n | `shipment.hints.trackingEvents`, `help.shipmentDetail.{flow3,rule3}`, `help.carriers.{flow2,rule3}` | tracking link |
| doc | `WhShipmentTrackingEventRepositoryCustom:59` | NDR |
| doc | `WhWorkingCalendarService:43,248` | NDR response clock |
| doc | `WhbItemIdentifier:88` | "Set for a marketplace listing" |
| doc | `WhEvidencePhotoStore:22` | marketplace claim evidence |
| doc | `W/V511294:26` | marketplace-claim-window job |
| doc | 3PL `Wh3plBillableEventVocabulary:15` | "an RTO'd … shipment" |

**Carrier.**
- `P7-03`: the tracking-link, NDR and working-calendar items.
- `P7-05`: the RTO and marketplace items, including the 3PL comment.
- `P7-07`: the supplier-claim help.
- `P7-10`: `WhbItemIdentifier:88`.

### CP-CODE-008 · MINOR · Dealer-persona and dealer-adapter comments outside `P7-10`'s reword list
**Evidence.**

| Location | Text or content |
|---|---|
| `WarehouseBaseModuleConfig:28-29` javadoc | "the dealer and services adapters, 3PL, India" (`P7-10` cuts `:53` only) |
| `WarehousePrintDataProvider:12`, `WhPrintRenderer:27` | "the dealer adapter's" print kind |
| `WhHoldQueryService:284` | "no dealer or services resolver" |
| `whHold.ts:15` | dealer resolver |
| `WhHold.java:35` | cites `dealer/V20735` |
| `WhbCompanyOptionResponse:11` | dealer `PdiStockYardCompaniesModal` |
| `WhbItemSiteSetting:27` | "ten-branch dealer" |
| `WB/V500048:57` | cites a dealer frontend file |
| `W/V510090:493` | "Dealer 60, Workshop 70" |
| `WarehouseDocumentDisplayRegistryTest:87-155` | `dealerSalesOrderResolver` / `PDI_JOB` fixtures |
| `NonFunctionalFoundationsTest:169` + `INSTALL.md:2177` | the FR-422 sizing target "20,000 ledger rows per day (dealer parts department)" |

None of these trips a gate. FR-493 and D-16 intent say no dealer persona remains.
**Carrier.** `P7-10`, in the same reword pass as its list. The `INSTALL.md:2177` row and the test row must change together (`P7-12` plus `P7-10`). The FR-422 wording itself is a spine edit (FRD).

### CP-CODE-009 · MINOR · `P7-12` ledger and batch-file lists are incomplete
**Evidence.**
- **Batch files.** REM-D17 lists superseded notes for `BATCH-WAREHOUSE-{P5,FINDINGS,P2,P3,P2-IN,P01-CONTINUE}` and `WAVE-STATE-WAREHOUSE-P5`. `BATCH-WAREHOUSE-P1.md`, `-P4.md`, `-P6.md` and `WAVE-STATE-WAREHOUSE-P4.md` also name removed features (1 hit each). `INTEGRATION-*` and `LANE-BRIEF-*` have 0 hits.
- **ci-gate ledger.** `20-warehouse.def:792-794` (the comment for `WhbOwnerScopeResolverCustomerPersonaTest`, deleted by `P7-08`) lies outside the prune ranges (`:795-833`). `P7-12`'s def-check script would catch it.

**Carrier.** `P7-12`.

### CP-CODE-010 · DECISION · The logix demo stays a D2C (consumer e-commerce) dataset after `P7`
**Evidence.** `LGX/V910031` models consumer orders, and `P7-04` removes only `payment_mode`, `cod_amount` and `cod_pct` use:
- site flag `d2c` and `cod_pct` (`:93,105`)
- consumer consignee table `lgx_ob_d2c` (`:206-218`)
- web-shop order references `VE-WEB-` / `UW-SHOP-` (`:159`)
- single-parcel courier cartons (`:378-381`)
- `d2c`-branched pricing, tracking and handovers (`:473-942`)

The demo a client sees still tells a retail story.
**Decision for the user.** Either keep the data as a generic-shipping demo and rename `d2c` to a neutral "parcel" flag, or re-seed the logix outbound as B2B distributor orders. A re-seed is a new task: no P7 task owns it, and `RN-054` does not fence logix (FRD-REM `$P`).

### CP-CODE-011 · DECISION · Automotive-flavoured base vocabulary not in the RN-024 inventory
**Evidence.**
- `WB/V500008:95` item type `CORE`: "A returnable core carrying a deposit until it is graded" — automotive core exchange. The dealer `whad_core_exchanges` was its consumer.
- `:99` item type `TYRE`: "fitment and retread history".
- `WB/V500010:151` `DEMAND_TYPE` `JOB_ISSUE`: "Issue to a job".

R28 keeps `FITMENT`/`ISSUE_TO_ASSET` but does not mention these three.
**Decision for the user.** Keep all three. `CORE` fits remanufacturing, `TYRE` fits fleet stores, and `JOB_ISSUE` fits production or maintenance jobs. Optionally reword `CORE`'s description so that it does not imply a dealer core exchange. If any is removed, that belongs in `P7-10`.

### CP-CODE-012 · INFO · Unspecced implemented behaviour (step 4): none found
**Evidence.** All 220 kept controllers trace to a requirement or task, so no unspecced behaviour was found beyond CP-CODE-011:
- **217 controllers** carry `FR-`/`WS-` ids, and every id exists in the design set.
- **3 controllers** without such ids trace to a task or finding:
  - `WhFulfilmentPolicyController` → `P3-13`
  - `WhinEwayBillEvidenceController` → `#241`
  - `WhinBondedLossController` → F526 / `FR-323` / `FR-383` (`IN/V541156:1-4`)

Eight pages lack a `WS-` id. That is a screens finding (`R30-completeness-screens` §1, `:113`), not unspecced code.

### CP-CODE-013 · INFO / DECISION · Cross-module coupling (step 5): nothing breaks
**Evidence.**

**Removed objects referenced outside the four modules.** A grep of every non-warehouse root for removed tables, classes, routes, caches, flags and the tracking-link secret finds only the three platform files that FRD-REM §1 already authorises:
- `CacheConfiguration.java:781,783` (`P7-04`)
- `filterUtils.ts` (the scopes `P7-02`…`P7-11` delete)
- the logix seeds `V910021`, `V910031`, `V910032` and `V910033`

The non-warehouse roots grepped:
- dealer, automotive, accessories, services, insurance (+360), assets
- accounting-* and leads*
- voice-agent, mobile, docs and `.claude`

Of these, `leads-base`, `leads` and `accounting-base` cite only **kept** `whb_*` objects, in comments or precedent text. `mobile/` has no warehouse-module screen; its `warehouse` hits are accessories types, so no web↔mobile parity applies.

**Kept couplings that need no edit:**
- `WB/V500200:75,120`: the platform module CHECK list names `'DEALER'`/`'ACCESSORIES'` as modules (REM-D19).
- `CsrfTokenFilter:53` keeps `"/public"` (REM-D16). No platform frontend allowlist names `/track`.
- `WhbAccountingMode:60` cites `AccountingAdapterDealerModuleConfig`. This is the accounting fence; `ENABLE_ACCOUNTING_ADAPTER_DEALER` in `.env`, Dockerfiles, compose, `start.sh` and the railway scripts is out of scope.
- `WB/V500054` + `WhbLogisticsSeamContractTest` guard against the dealer-owned `all_activity_history`.
- `WarehouseBaseCouplingTest` keeps its `ai.dealer` import bans and band ratchet.
- `warehouse-adapter-example` depends on no removed object. It seeds its own `ADAPTER_EXAMPLE` (`V525000`) and does not implement `WhCarrierConnector`.

**Build flags.**
- Docker and `start.sh` carry only `ENABLE_WAREHOUSE`, `_BASE`, `_3PL` and `_INDIA`, plus a flag-less `warehouse-adapter-example`.
- No `ENABLE_WAREHOUSE_ADAPTER_*` and no `enable.warehouse.adapter.*` property exists outside `WarehouseBaseModuleConfig:53`, which `P7-10` cuts.
- SafeTranslation files: `WarehouseBaseSafeTranslation`, `WarehouseSafeTranslation`, `Warehouse3plSafeTranslation`, `WarehouseIndiaSafeTranslation`. No adapter file exists.

**Decision items (other modules are not edited).**
1. `CLAUDE.md:155` lists the non-existent `WarehouseAdapterDealerSafeTranslation.tsx`. `P7-12` reports it, and the user approves or declines the edit.
2. The logix demo shape (CP-CODE-010).

## 3. Summary for the carrier tasks

| Task | Add |
|---|---|
| `P7-02` | `reasonCode.byCode.CARRIER_REJECTED` (CP-005) |
| `P7-03` | `LGX/V910031:37-46` `supports_cod` (CP-001, BLOCKER); NDR-only reason labels (CP-005); `whCarrierService.ts`, `WhCarrierServiceFilter.tsx`, `carrierService.statistics.supportsCod`, `help.carrierServices.*`, `V510044:417` (CP-006); tracking-link, NDR and working-calendar prose (CP-007) |
| `P7-04` | the nested `outboxEvent.eventTypeByCode.channel` subtree and a jq check (CP-004) |
| `P7-05` | `WhOrderEditRuleValidationService:50,82`, `rma.placeholders.externalRef`, `WhEvidencePhotoStore:22`, `V511294:26`, `Wh3plBillableEventVocabulary:15` (CP-007) |
| `P7-07` | `help.supplierClaims.flow1`, `supplierClaim.hints.headerExplainer` (CP-007) |
| `P7-10` | five GATE-6 lines (CP-002); `help.sourceSystems.overview` + `warehouseMobileDecisionGate.test.ts:773-813` (CP-003); dealer comment and persona residue (CP-008); `WhbItemIdentifier:88` (CP-007) |
| `P7-12` | `BATCH-WAREHOUSE-{P1,P4,P6}`, `WAVE-STATE-WAREHOUSE-P4`, def `:792-794` (CP-009); the pinned `INSTALL.md` §16/§16.1/`:2177` text, then run the two tests that read `INSTALL.md` (CP-003, CP-008) |
| user | CP-010 (logix D2C demo), CP-011 (`CORE`/`TYRE`/`JOB_ISSUE`), the `CLAUDE.md:155` approval (CP-013) |
