# R29 — functional review (Claude + GPT dual engine), area REM

**Date** 2026-10-22 · **Reviewer** functional-reviewer, pre-build audit mode · **Dispositions** recorded in the area FRD §"R29 dispositions"

**Summary.** The P7 plan can't be built one task at a time as written: 5 blockers, 5 major, 7 minor. The cut seams, the five count asserts the brief named and the migration inventory all check out against the code.

I did not write `FR-REVIEW-REM.md`. My agent definition forbids report files, so the full report is below and can be posted as-is.

**Top 5**
1. **F1 (BLOCKER).** After P7-02, a fresh install fails at `V511273:202`, and from P7-03 also at `V511271:223`. Their leaves outlive their permissions until P7-06.
2. **F2 (BLOCKER).** `WhCarrierConnectorRegistryTest:90-91` still calls `rate()` and `fetchAwbBlock()`, so P7-02's connector trim breaks the test build.
3. **F3 (BLOCKER).** `WhTradePortalService:336-337` still uses the payment fields, so P7-04 can't compile before P7-08.
4. **F4 (BLOCKER).** Seed count floors the FRD doesn't list fail a fresh install: `V500002:461,464`, `V500003:429,432`, `V500004:342`.
5. **F5 (BLOCKER).** Kept ratchets assert the deleted `ACCESSORIES` row (`WarehouseBaseCouplingTest:1872,2195` and three registry-openness tests).

Engines: Claude + GPT (gpt-6.1-sol, medium) — 4 both · 9 Claude only · 4 GPT only · 0 dropped

---

# Functional conformance — warehouse REM / P7 (pre-build gap review)
Contract: `warehouse-issues/docs/frd/FRD-REM.md` (2026-10-22), plus `issues/p7-01..13.md` and `09-EPIC-p7.md` | Mode: audit, pre-build (the FRD is the contract)
Files reviewed: the 15 design inputs, plus targeted reads of about 60 classic files at `65b41be8a6`. Repository-wide greps cover the four warehouse modules, the three platform files, all client seeds, `shared/scripts/ci-gate`, `.claude/testing/descriptors` and `mobile/src`. | File set: derived from the brief
Engines: Claude + GPT (gpt-6.1-sol, medium) — 4 both · 9 Claude only · 4 GPT only · 0 dropped

## Verdict
**17 findings: 5 BLOCKER, 5 MAJOR, 7 MINOR.** No build or database run was done. Everything here comes from reading the code and grepping it.

What holds:
- **Cut seams.** Each named seam has a replacement behaviour, and the line numbers were spot-checked exact: `WhShipmentService:282-287,343-345,376,469,493-499,534`, `WhReturnReceiptService:337-340,509-510`, `WhCarrierRepositoryCustomImpl:212-214`, `WhTrackingEventIngestService:182-194`, `V510216:274`.
- **Listed count asserts.** All five are correct:
  - `V511248:298`: 45 → 44. RTO is the only removed leaf in the eight sections (`V511248:127-175`).
  - `V511268:304`: 8 → 6 → 5. `V511268:371`: 24 → 21 → 18.
  - `V500010:811` and `V510050:945`: 10 → 8.
  - `V500002:468`.
- **Migration inventory.** Every migration or client seed that names a removed table, column or menu container appears in Appendix B.
- **P7-01 moves.** The fingerprint hash moves byte-identically (`WhChannelOrderImportPayloadCodec:60-63`). The category picker is served per module (`WhbGlPostingRuleController:169`, `WhbValuationPolicyController:146`, and allocation via `/item-categories`).

## Status reachability (kept lifecycles touched by P7)
| Status | In CHECK / enum | In contract | Inbound | Outbound | UI reachable | Verdict |
|---|---|---|---|---|---|---|
| Shipment `DISPATCHED` | `WhShipment.java:55` | WH-SC-666 wrongly says `SHIPPED` | dispatch | deliver / mapped delivery | yes | F15 |
| Shipment `DELIVERED` | enum | yes | manual or mapped `DELIVERED` (`WhTrackingEventIngestService:189-191`) | terminal | yes | OK |
| Carrier `NDR` / `RTO_*` | `V510203:80-82,151-153` | removed (REM-D4) | — | — | removed | OK; `EXCEPTION` stays as the fallback |
| Supplier claim source `OBSOLESCENCE_RETURN` | trigger arm `V510216:274-275` (no CHECK, `:109`) | removed | — | — | removed | OK. With the arm gone, the trigger refuses an unknown source ("names source … which does not exist") |
| Return type `RTO` / `MARKETPLACE` | `V500010:155,161` | removed (OD-23) | — | — | removed | OK. No kept Java reads `RTO_RECEIPT` |

## Findings

### F1 — BLOCKER: intermediate trees fail a fresh install in V511273 and V511271
- Contract row: FR-498; EPIC property "every intermediate tree installs fresh". Source: **Both**.
- Evidence:
  - P7-02 deletes the `wh_rate_quotes`, `wh_carrier_serviceability` and `wh_awb_pools` permissions (V510204/V510205), but `V511273` keeps seeding their leaves. Its check at `V511273:194-202` raises "leaf prefix(es) % have no :view permission".
  - The same happens at `V511271:214-223` once P7-03 deletes V510209 (tracking links) and P7-04 deletes V510208 (channel accounts, imports and publish rules).
  - The rewrites are deferred to P7-06 (`issues/p7-06.md`, "Depends on P7-02, P7-03 and P7-04").
- Impact: the P7-02, P7-03, P7-04 and P7-05 trees fail Flyway on an empty volume.
- Fix: each deleting task strips its own leaves, translations, IN-lists and verification counts from V511271/V511273. P7-06 keeps only the L1/L2 rename and the four re-homes.

### F2 — BLOCKER: P7-02's connector trim breaks a kept test that no task owns
- Contract row: REM-D13 / FR-481. Source: **GPT**, verified.
- Evidence: `WhCarrierConnectorRegistryTest.java:85-91` (`defaultConnectorOffersNothing` calls `rate(null)` and `fetchAwbBlock(null)`). No P7 task names this test.
- Fix: add it to P7-02's kept tests. Delete that one method, keep the registration, duplicate-owner and unavailable tests, and reword the `:22` comment.

### F3 — BLOCKER: P7-04 removes demand-order payment accessors while the trade portal still calls them
- Contract row: REM-D1; task order. Source: **GPT**, verified.
- Evidence: `WhTradePortalService.java:331-337` (`redact()` calls `setPaymentMode(null)` and `setCodAmount(null)`) and `WhTradePortalServiceScopeTest.java:258,265`. The portal is deleted in P7-08, which runs after P7-04 (`09-EPIC-p7.md:63`).
- Fix: put the two `redact()` lines and their test asserts in P7-04's seams, or move P7-08 before P7-04 and update the order line.

### F4 — BLOCKER: seed count floors missing from the "fresh-install hazards" list
- Contract row: FR-498, FR-494; brief item (c). Source: **Claude**.
- Evidence (each fails Flyway in the P7-10 tree):
  - `V500002__Create_whb_source_systems_and_document_types.sql:461` checks `v_sources < 9`. It seeds exactly 9 (`:153-165`), and REM-D3 removes 5, leaving 4.
  - `V500002:464` checks `v_documents < 13`. 13 seeded (`:178-193`), minus `JOB_CARD` and `POS_SHIFT`, leaves 11.
  - `V500003__Create_whb_movement_types.sql:429,432` check `v_forward < 18` and `v_reversal < 18`. The 18 pairs include `RTO_RECEIPT` and `RTO_RECEIPT_REVERSAL`, so both drop to 17.
  - `V500004__Create_whb_reason_codes.sql:342` checks `v_contexts < 11`. Removing the RTO and NDR contexts leaves 9.
  - `FRD-REM.md:539` and the P7-10 table list only `V500002:468-470` and `V500004:190-191`.
- Fix: add these five asserts to Appendix B.2, the hazard list and P7-10's table, each with its new number (4 / 11 / 17 / 17 / 9). Update the "eleven contexts" and "18" header comments too.

### F5 — BLOCKER: kept ratchets require the deleted `ACCESSORIES` source system
- Contract row: REM-D3 / FR-493 / WH-SC-676. Source: **Both** (GPT found the backend ratchets, Claude the frontend ones).
- Evidence:
  - `WarehouseBaseCouplingTest.java:1871-1872` ("seeds no ACCESSORIES source system", run at `:2177`) and `:2195`, whose anti-vacuous check needs `whb_source_systems:ACCESSORIES`. This class is a mandatory ci-gate class.
  - `warehouseRegistryOpenness.test.ts:957`, `wh3plRegistryOpenness.test.ts:977` and `whinRegistryOpenness.test.ts:1035`, each with `expect(seeded.has('ACCESSORIES')).toBe(true)`.
  - P7-10's test list names only `WhbPortReferenceResolverClaimabilityTest` and `whbCatalogueModalPlaceholders`.
- Fix: P7-10 retires `ReservedAccessoriesRule` and its scanner, and swaps every anti-vacuous anchor for a kept seeded row (for example `LOGISTICS`) in all four modules. Keep the band ratchet.

### F6 — MAJOR: the final grep gates can't pass without editing preserved or fenced code
- Contract row: FRD §6 / WH-SC-675 ("Gate exceptions are not allowed"). Source: **Both**.
- Evidence:
  - GATE-3 `PAYMENT_MODE` matches kept carrier-account code: `WhCarrierAccount.java:52,55,92` and `WhCarrierAccountRequest.java:13` (REM-D12 keeps it).
  - GATE-3 `'ACCESSORIES'` matches `V500200__Allow_warehouse_in_platform_module_check_constraints.sql:75`. That is the platform module list behind a global-settings CHECK, which is generic and has to stay.
  - GATE-3 `ADAPTER_*` matches the band-ratchet fixtures that REM-D3 keeps. Only GATE-6 excludes that file.
  - Scope `$P` takes all of `platform/.../db/client`. GATE-3/4 then hit dealer client seeds the fence (RN-054) forbids editing: `vehicron|pasco|ktlautomobiles/V910001__*_departments.sql:15,33,37` (`'ACCESSORIES'`, `'RTO'`, `'WORKSHOP'`), `*/V910096__*:52` (`'RTO'`) and `pasco/V910131:32` (`'WORKSHOP'`).
- Fix: narrow `$P` to `db/client/logix`. Anchor GATE-3 to demand-order and wave payment vocabulary, not bare `PAYMENT_MODE`. Record the V500200 module list and the ratchet fixtures as named §2 exceptions.

### F7 — MAJOR: per-task gates depend on later tasks, and some hits have no owner
- Contract row: WH-SC-675; task-level acceptance. Source: **Both**.
- Evidence:
  - P7-10 acceptance requires GATE-3 to be empty, but GATE-3 includes `OEM_PART_NUMBER`, which only P7-11 renames.
  - The P7-02 to P7-09 greps run over `warehouse*`, which includes docs, and docs are P7-12's (`warehouse/docs/contracts/shipment-carrier-lifecycle.contract.md`, `warehouse-base/INSTALL.md` and `DATED-OBLIGATION-REGISTER.md` all match `AwbPool`/`wh_awb_`).
  - GATE-1 comment hits that no task owns:
    - working calendars: `WhWorkingCalendarController:49`, `WhWorkingCalendarRepositoryCustomImpl:21`, `WhWorkingCalendarExportService:19`, `WhWorkingCalendarMapper:17`, `WhWorkingCalendarValidationService:28`
    - carrier account scopes: `WhCarrierAccountScopeController:29`, `WhCarrierAccountScopeService:38`, `WhCarrierAccountScopeValidationService:17`
    - other warehouse files: `WhShipmentTrackingEventMapper:14`, `WhDemandOrderRepository:131`, `WhCarrierConnectorRegistryTest:22`
    - 3PL: `Wh3plArAccountingSink:12`
    - India: `WhinDeliveryChallanIssueIntegrationTest:104`
    - docs: `warehouse-base/docs/contracts/outbox.contract.md:254`
- Fix: each task gets a gate scoped to its own surfaces (excluding docs and codes renamed later). The full gate set stays in P7-13. Assign each orphan comment to the task that deletes the class it names.

### F8 — MAJOR: install-health integration tests assert the deleted role in all four modules
- Contract row: FR-491 / WH-SC-676. Source: **Claude**.
- Evidence: `WhInstallHealthIntegrationTest.java:79-82`, `Wh3plInstallHealthIntegrationTest.java:67-70` and `WhinUpgradeAndActivationIntegrationTest.java:86-89` list "Warehouse Trade Customer" as a seeded starting bundle (V511209). `WhbBaseOnlyInstallHealthIntegrationTest.java:75-76` lists it as an absent bundle, which is stale but harmless. The `WhPermissionAdversarialFixture.java:51` doc also cites V511209. None of these appears in the design.
- Fix: P7-08 removes the role from those lists in warehouse, 3PL and India.

### F9 — MAJOR: dealer and services adapter filter scopes stay in `filterUtils.ts`, and no gate catches them
- Contract row: FR-493 ("no dead adapter switch"); brief item (a). Source: **Claude**.
- Evidence:
  - `platform/frontend/src/utils/filterUtils.ts:1983` `WAREHOUSE_DEALER_COUNTER_SALE`, `:1993` `WAREHOUSE_DEALER_ITEM_PRICE`, `:2002` `WAREHOUSE_DEALER_PRICE_LEVEL`, `:2010` `WAREHOUSE_SERVICES_MATERIAL_REQUEST`, `:2019` `WAREHOUSE_SERVICES_JOB_PART_ISSUE`, `:2029` `WAREHOUSE_SERVICES_FITTED_SERIAL`, `:2106` `WAREHOUSE_DEALER_VEHICLE_FITMENT`. These belong to the adapters removed on 2026-09-21. They are not among the 17 scopes in Appendix E, and GATE-6 doesn't scan `$P`.
  - `whad_`/`whas_` comment remnants outside GATE-6: `WhbExportService.java:55`, `V510040:42-43`, `V500005:202`, `whinPermissions.ts:15`.
- Fix: add the 7 scopes to P7-10's `filterUtils` cuts. Extend GATE-6 to `filterUtils.ts` with `WAREHOUSE_(DEALER|SERVICES)_|whad_|whas_`.

### F10 — MAJOR: tester descriptors for removed screens aren't covered
- Contract row: FR-499 (docs/QA clause); P7-13 step 5 ("the tester agent can drive them"). Source: **Claude**.
- Evidence:
  - `.claude/testing/descriptors/`: `wh-awb-pools`, `wh-ndr`, `wh-cod-remittances`, `wh-channel-accounts`, `wh-channel-imports`, `wh-publish-rules`, `wh-tracking-links`, `wh-marketplace-claims`, `wh-rto`, `wh-serviceability`, `wh-rate-quotes`, `wh-obsolescence-returns`, `wh-rpt-coexistence`, `wh-rpt-consolidated-valuation`, `whb-external-snapshots` and `whb-category-ownership` (`.json`).
  - `wh-rpt-parts-kpis.json` needs the rename.
  - `wh-carrier-services.json` and `whb-item-categories.json` still carry `supportsCod` / `isDualEligible`.
  - No task names the folder.
- Fix: put descriptor delete/rename/trim in each feature's task, or in P7-12.

### F11 — MINOR: field inventory gaps, caught only by gates
- Source: **Claude**.
- Evidence:
  - `supports_cod` is used beyond "entity, DTOs, mapper, export, query filter": `WhCarrierServiceLevelStatisticsResponse:18,33-34` (stat tile), `WhCarrierServiceLevelRepositoryCustomImpl:122` (stats SQL, a runtime SQL error if missed), `WhCarrierServiceLevelService:191` (trackChanges) and `WhCarrierServiceLevelController:76,167` (request params).
  - The wave-criterion label `PAYMENT_MODE` at `warehouse.json:5219` (×3 languages) isn't in P7-04's i18n list.
  - `warehouseBase.json` `reasonCode.byCode.CARRIER_INITIATED` isn't named in P7-03 or P7-10.
- Fix: name them in P7-03, P7-04 and P7-10.

### F12 — MINOR: WH-SC-669 leaves the unknown-field policy open, but the code already settles it
- Source: **Claude**.
- Evidence: `platform/backend/src/main/java/ai/platform/config/JacksonConfig.java:73` disables `FAIL_ON_UNKNOWN_PROPERTIES`. A body that still carries `paymentMode` is therefore ignored, not refused with 400.
- Fix: write "ignored" into WH-SC-669 and P7-04.

### F13 — MINOR: requirement ownership contradicts itself across tasks
- Source: **Claude**.
- Evidence:
  - The P7-03 header closes FR-483, but the demand-order payment and COD work is in P7-04, and P7-04 says FR-483 is "owned by P7-03".
  - The P7-04 header lists FR-495 but says it is P7-10's.
  - The P7-03 header lists FR-489, and P7-05 says FR-489 "is owned by P7-02".
- Fix: one owner per FR: FR-483 to P7-04, FR-489 to P7-02, FR-495 to P7-10.

### F14 — MINOR: the design set's `IRREVERSIBLE.md` isn't amended
- Source: **Claude**.
- Evidence: `warehouse-issues/docs/IRREVERSIBLE.md:210` (IRR-28 lists `POS_SHIFT`, `JOB_CARD`) and `:686-690` (§5 rows 2, 3 and 6 list `ADAPTER_*`, `ACCESSORIES` and the "eleven contexts"). The rewritten seed asserts cite §5 for their counts.
- Fix: add a design-set edit (§5 rows and IRR-28, with a D-16 note) to P7-12's scope.

### F15 — MINOR: WH-SC-666 expects the wrong shipment status
- Source: **GPT**, verified.
- Evidence: `FRD-REM.md:130` says the shipment becomes `SHIPPED`, but the shipment enum has `DISPATCHED` (`WhShipment.java:55`). The scenario's "pre-P7 baseline test" isn't named either.
- Fix: assert `DISPATCHED` → `DELIVERED` on the shipment, and `SHIPPED` on the demand order if needed. Name the baseline test.

### F16 — MINOR: P7-05's acceptance SQL uses a column that doesn't exist
- Source: **GPT**, verified.
- Evidence: `issues/p7-05.md:62` filters on `code_list='RETURN_TYPE'`, but the column is `list_code` (`V500010:52`).
- Fix: use `WHERE list_code='RETURN_TYPE'` and assert the exact set of 8 codes.

### F17 — MINOR (brief item f): external-order deduplication disappears with no successor noted
- Source: **Claude**.
- Evidence: REM-D1 drops `uk_wh_demand_orders_channel_external_ref` (`V510040:217-218`). P7-04's trap says no replacement. P8-02 adds a sales-order creation port that will need external-reference idempotency.
- Fix: add one line to P8-02, or an OD, saying whether `(channel_id, external_order_ref)` uniqueness comes back there. Nothing else generic that manufacturing or storage needs is removed: the OBSOLESCENCE KPI, `whb_channels`/`channel_id`, item external refs, working calendars, carrier account scopes and return gradings all stay.

## Dropped after verification
- None.

## Remediation backlog
| Finding | Files to touch | Migration | Shared registries | Parity apply-to | Contract |
|---|---|---|---|---|---|
| F1 | `issues/p7-02.md`, `p7-03.md`, `p7-04.md`, `p7-06.md`; `W/V511271`, `W/V511273` | rewrite only (no new version) | menu_permissions | none (no mobile) | EPIC order; Appendix B.2 V511271/V511273 rows |
| F2 | `issues/p7-02.md`; `WhCarrierConnectorRegistryTest.java` | none | none | none | Appendix C kept tests |
| F3 | `issues/p7-04.md` (or `09-EPIC-p7.md` order); `WhTradePortalService.java`, `WhTradePortalServiceScopeTest.java` | none | none | none | Appendix C |
| F4 | `FRD-REM.md` B.2 and `:539`; `issues/p7-10.md`; `WB/V500002`, `V500003`, `V500004` | rewrite only | none | none | Appendix B hazard list |
| F5 | `issues/p7-10.md`; `WarehouseBaseCouplingTest.java`, `warehouseRegistryOpenness.test.ts`, `wh3plRegistryOpenness.test.ts`, `whinRegistryOpenness.test.ts` | none | none | warehouse-3pl, warehouse-india tests | REM-D3 |
| F6 | `FRD-REM.md` §2 and §6 | none | `filterUtils.ts` scope list unchanged | dealer client seeds fenced (RN-054) | §6 GATE-3/4 scope |
| F7 | `issues/p7-02..p7-11.md` acceptance; the 14 orphan comment files | none | none | warehouse-3pl, warehouse-india | §6 per-task gates |
| F8 | `issues/p7-08.md`; 4 install-health tests | none | none | warehouse-3pl, warehouse-india | FR-491 |
| F9 | `issues/p7-10.md`; `filterUtils.ts`; `FRD-REM.md` §6 GATE-6 and Appendix E | none | `filterUtils.ts` (7 scopes) | none | FR-493 |
| F10 | `issues/p7-12.md` (or each feature task); `.claude/testing/descriptors/*` | none | none | none | Appendix F |
| F11 | `issues/p7-03.md`, `p7-04.md`, `p7-10.md` | none | `filterUtils.ts` `WAREHOUSE_CARRIER_SERVICE` | none | Appendix C and E |
| F12 | `FRD-REM.md` WH-SC-669; `issues/p7-04.md` | none | none | none | WH-SC-669 |
| F13 | `issues/p7-03.md`, `p7-04.md`, `p7-05.md` headers | none | none | none | §4 ownership |
| F14 | `issues/p7-12.md`; `warehouse-issues/docs/IRREVERSIBLE.md` | none | none | none | IRR-28, §5 |
| F15 | `FRD-REM.md` WH-SC-666 | none | none | none | WH-SC-666 |
| F16 | `issues/p7-05.md` | none | none | none | P7-05 acceptance |
| F17 | P8-02 issue, or a new OD in `FRD-REM.md` §3 | none | none | none | REM-D1 |

## Parity (C10)
- Mobile: none. FRD §1 says warehouse has no mobile screens. `grep mobile/src` finds only accessories `accessoryWarehouse*`, which I confirmed.
- Siblings sharing this pattern: single product, four modules: warehouse-base, warehouse, warehouse-3pl and warehouse-india. Each 3PL/India test or comment named in F5, F7 and F8 is part of the apply-to list. The dealer, automotive, accessories, services, insurance and assets modules stay fenced.

## In code, not in contract
- 7 adapter filter scopes in `filterUtils.ts:1983-2106`: remove them under FR-493 (F9).
- Tester descriptors (F10), the install-health role lists (F8), the `ACCESSORIES` anchors (F5), `WhTradePortalService.redact` (F3) and `WhCarrierConnectorRegistryTest` (F2): add each to its owning task.

## Contract quality
- Could not verify: actual Flyway execution of the rewritten SQL, HTTP behaviour (WH-SC-666 to 674) and stock-movement equivalence (WH-SC-668). These need the P7-13 runs.
- Checked and clean:
  - logix seeds use no removed status, return type, claim type or warehouse type. The only hits are the columns already listed: `V910031:24-34,448-449` and `V910021:139,141`.
  - `warehouse_shipping` and `warehouse_shipping_planning` collide with no existing menu name.
  - Warehouse Operations does hold 10 L2s (`V511268:40-41`), so REM-D15's rationale stands.
  - `btree_gist` is declared in `V500001`.
- Note: the logix demo stays a D2C web-order narrative (`V910031:93-218`). P7 strips only the columns. That is a product call and not a defect.
- Kept from Appendix F: report the stale `CLAUDE.md` mention of `WarehouseAdapterDealerSafeTranslation.tsx` to the user; do not edit it.

## Referred to standards reviewer
- None.
