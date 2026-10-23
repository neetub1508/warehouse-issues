# Functional Contract — Non-functional requirements as checkable rules

> **What this is.** `D-17` item a: every active FR is covered by a contract rule, so each non-functional FR
> of §6.25, the variant FRs of §6.26, the regulated-goods FRs `FR-456` / `FR-457` and the v2 dated junctions
> `FR-468` are stated here as a **checkable rule**: the measurable threshold, **where it is verified**
> (ci-gate job `warehouse-ratchets` in `classic/shared/scripts/ci-gate/20-warehouse.def`, a named test class,
> an architecture test, or the reviewer gate where nothing is mechanised), and the Source FR. There is no state
> machine. A rule verified only by a reviewer says so; that is a weaker proof and is counted in §2.
>
> **Status.** Derived 2026-10-23 (v0) for R30 `CP-FR-007` row 24. FRD status re-read the same day: `FR-424`,
> `FR-430`, `FR-431` are **DEFERRED by `D-17`** (mobile) and `FR-422` is **WITHDRAWN by `D-16`** — none is
> covered. `FR-436` (single writer) is carried by `movement-post-reverse` and is not restated; `FR-439` (site timezone), cited elsewhere only outside a Source column, is `NFR-22`. `FR-443`…`445` and
> `FR-456` / `FR-457` remain active and carry the R30 `CP-FR-012` segment note; their rules state what is built
> and their segment call is an OPEN row (§4). Verified against `classic` by grep. Not ratified.

---

## 0. Identity

| | |
|---|---|
| **Scope** | `FR-423`, `FR-425`…`FR-429`, `FR-432`…`FR-435`, `FR-437`, `FR-438`, `FR-439`, `FR-440`…`FR-445`, `FR-456`, `FR-457`, `FR-468` |
| **Modules** | all warehouse modules; `FR-429` is platform |
| **Verification home** | ci-gate `warehouse-ratchets` (blocking; `ASSERT_SPECS` lists the surefire reports that must exist): `NonFunctionalFoundationsTest`, `ArchitectureInvariantsTest` (base, warehouse, adapter-example, india, 3PL), `WarehouseBaseCouplingTest`, `Wh3plCouplingTest`, `WhbGridConfigContractTest`, `WhGridConfigContractTest`, `Wh*GridFilterBindingContractTest` (base, warehouse, 3PL, india), `WhSandboxExclusionContractTest`, `WhbSandboxPurgeContractTest`, `WhReportsComputeFromLedgerTest` |
| **Owning tasks** (R30 §4) | `p0-02` (`423`, `439`) · `p3-02` (`425`) · `p1-09` (`426`) · `p0-13` (`427`) · `p1-11` (`428`) · `p0-16` (`429`) · `p1-20` (`432`, `433`, `438`) · `p0-01` (`434`, `435`, `440`) · `p0-03` (`437`) · `p4-09` (`441`) · `p3-23` (`442`) · `p1-01` (`443`, `444`) · `p5-20` (`445`) · `p4-13` (`456`, `457`) · `p1-05` (`468`) |
| **Contract version** | `v0 — 2026-10-23` |

---

## 1. Checkable rules

| ID | Rule | Measurable threshold | Verified in | Source |
|---|---|---|---|---|
| NFR-01 | The partition and archive strategy is stated at design time and breaks neither as-at reproduction nor either retention clock | 0 archive / purge jobs outside the stated boundary; archiving disclosed as deferred in the supported offer; partitioned tables declared in their migrations (`V500041`, `V500045`, `V501119`) | `NonFunctionalFoundationsTest$ArchiveBoundary` (`shouldFindNoOutOfBandArchive`, `shouldCatchPlantedArchives`, `shouldDiscloseArchivingDeferredInTheSupportedOffer`) · ci-gate `warehouse-ratchets` | FR-423 |
| NFR-02 | Task claiming uses `FOR UPDATE SKIP LOCKED` (new work, no precedent) | two concurrent claimers receive 0 shared tasks | `WhbTaskClaimConcurrencyIntegrationTest`, `WhbZoneMembershipClaimContractTest`; main `WhbTaskRepositoryCustomImpl` | FR-425 |
| NFR-03 | Gapless numbering from a locked counter row, module-scoped; a branch-scoped series resolves to the issuing site's `REGISTERED` branch at the document date, and a re-registration renumbers nothing | 0 gaps; 0 sequences; issue only inside the caller's transaction | `WarehouseBaseCouplingTest.shouldLockTheCounterRowAndNeverUseASequence`, `shouldIssueInsideTheCallersTransactionOnly`, `shouldKeepTheIssueLogAppendOnly`; `WhbNumberSeriesBranchScopeTest`, `WhbNumberSeriesIssuedBranchScopeTest` | FR-426 |
| NFR-04 | The ledger is the audit trail; the five auditor artefacts ship: ledger as at a date (reproducible), movement audit export for a period, adjustment analysis, count history with variance, immutability evidence | each of the five reachable from a menu; as-at recomputed from movements | `WhReportsComputeFromLedgerTest` (ci-gate); `WhStockAsAt*`; ledger immutability triggers (`movement-post-reverse`) · the five-artefact list itself: reviewer | FR-427 |
| NFR-05 | Warehouse owns `whb_activity_history` over its own ledger and never reads or redefines the dealer-owned cross-module view | 0 migrations / 0 Java readers of the dealer view | `WhbLogisticsSeamContractTest.shouldDefineTheViewOverTheLedgerAlone`, `shouldFindNoMigrationUsingTheDealerView`, `shouldFindNoJavaReaderOfTheDealerView` | FR-428 |
| NFR-06 | Restore exists: restore path, WAL archiving, point-in-time recovery, restore verification, stated RPO / RTO (platform work) | a stated RPO and RTO and a passing restore-verification job | `NonFunctionalFoundationsTest$RestoreGapDisclosure` asserts the gap is **still disclosed** (`shouldStillFindNoPointInTimeRecoveryOrStatedObjective`) — see `NFR-DIV-02` | FR-429 |
| NFR-07 | Every warehouse grid registers its filter scope in the platform allowlist and its cache names in the platform cache registry; expiry, count and manufacture dates use the date-only filter type | 0 grid filters missing from `COMMON_FILTER_CONFIGS`; 0 unregistered cache names | `WhbGridFilterBindingContractTest`, `WhGridFilterBindingContractTest`, `Wh3plGridFilterBindingContractTest`, `WhinGridFilterBindingContractTest`; `ArchitectureInvariantsTest.shouldRegisterEveryAnnotatedCacheName` · ci-gate | FR-432 |
| NFR-08 | Every grid migration writes column definitions, filter definitions and both `default_columns` and `default_filters`, into `filter_definitions` | 0 grids missing either default; every default key has its definition row | `WhbGridConfigContractTest`, `WhGridConfigContractTest` (ci-gate); per-migration self-asserts (e.g. `V530030` "needs BOTH default_columns AND default_filters") | FR-433 |
| NFR-09 | The nineteen named failure modes are the architecture ratchet and the screen obligations | 0 new violations against each module's frozen baseline | `ArchitectureInvariantsTest` in base, warehouse, adapter-example, india and 3PL (ci-gate `ASSERT_SPECS`) | FR-434 |
| NFR-10 | Seven-layer definition of done per task: column / seed, service, authorised endpoint, frontend API method, permission- and status-gated control on a menu-reachable page, a top-level menu path, a runtime effect after rebuild. No mobile eighth layer under `D-16` item 7 / `D-17` | 7 of 7 ticked per task, no aggregate tick | reviewer + functional-reviewer gate (not mechanised) | FR-435 |
| NFR-11 | The five concurrency mechanisms are named and used: advisory locks, a pessimistic-locked counter row, a deferrable constraint trigger for balance-at-commit, optimistic versioning on the position, skip-locked claiming | each mechanism has ≥ 1 test | `WhbAdvisoryLockBucketHeldTest`; `WarehouseBaseCouplingTest.shouldLockTheCounterRowAndNeverUseASequence`; deferrable triggers `V501220`, `V501224`; `WhbPositionContentionRetrierTest`; `WhbTaskClaimConcurrencyIntegrationTest` | FR-437 |
| NFR-12 | Native-query timestamp mapping handles `OffsetDateTime`, `Instant`, `Timestamp` and `LocalDateTime` and warns on an unknown type | 0 nulls for a known type; 1 warning per unknown | `WhbNativeRowValues`, `WhbNativeRowValuesTest` | FR-438 |
| NFR-13 | Multi-tenant SaaS is not built; the owner dimension is multi-client separation inside one install (`OD-3`) | 0 tenant columns or tenant resolvers in warehouse code | reviewer grep (`tenant` appears only in comments) — not mechanised | FR-440 |
| NFR-22 | Multi-timezone: each site posts in its own local day; the site's `timezone` is an IANA id validated against platform `timezones.code` on save (never a free string) and is used for local-day bucketing | 0 sites with an unvalidated zone; a site's zone is frozen once it holds postings | `whb_warehouses.timezone` (`V500012`, validated on save in `WhbWarehouse` service path); `WhbWarehouseTimezoneFrozenIntegrationTest`; `WhbValuationPolicyBoundaryTimezoneIntegrationTest` | FR-439 |
| NFR-14 | Retention beats erasure: the person is pseudonymised, never the quantity | an erasure request changes 0 ledger quantities | `whb_person_pseudonyms` (`V500067`); `WhbPersonPseudonymServiceTest`, `WhbPersonNameResolverTest` | FR-441 |
| NFR-15 | A sandbox / practice warehouse with disposable data, excluded from live figures and purgeable; in-product help per screen on the platform help affordance | 0 sandbox rows in live reports; purge removes all sandbox rows; every warehouse page carries `HelpButton` | `WhSandboxExclusionContractTest`, `WhbSandboxPurgeContractTest` (ci-gate); help: reviewer (`HelpButton` in 111 warehouse frontend files by grep) | FR-442 |
| NFR-16 | Variant model is v1 schema: a style parent, ordered axes, every stocked variant an item row; values are rows, not slots; an item's category is a dated assignment per scheme and `STOCKING` is mandatory for stocked items and the only scheme a costing, posting or allocation resolver reads, at `occurred_at` | a fourth axis needs 0 schema change; 0 resolvers reading a non-`STOCKING` scheme | schema `whb_style_variant_axes`, `whb_item_variant_axes`, `whb_item_variant_axis_values`, `whb_item_variant_values`, `whb_item_category_assignments` (`V500014`, `V500015`) · resolver rule: reviewer | FR-443 |
| NFR-17 | A variant axis carries an explicit integer order so a size run sorts and ranges in size order | ordering column present and used by sort | `whb_style_variant_axes.sort_order` · reviewer | FR-444 |
| NFR-18 | Ratio / assortment packs: a template of quantity per variant, received and shipped as one line, exploded into variant-level movements | one scan → n variant movement lines summing to the template | `whb_ratio_pack_templates`, `whb_ratio_pack_template_lines` (`V500090`) · explosion: reviewer | FR-445 |
| NFR-19 | Regulated goods: licence types; licences of our own entity and of each counterparty with validity and a document; per-licence quantity ceilings; a **hard despatch block**; `regulatory_class` makes batch / expiry mandatory | a despatch to a party without a required, valid licence is refused 100% of the time | `WhinRegulatedGoodsDispatchGuard` → `409 OWN_LICENCE_REQUIRED` / `409 COUNTERPARTY_LICENCE_REQUIRED` / `409 LICENCE_CEILING_EXCEEDED` / `409 REGULATED_ITEM_NOT_LOT_CONTROLLED` · `status`; `WhinRegulatedGoodsDispatchGuardTest`, `WhinRegulatedItemValidationContributorTest`; tables `V540183` | FR-456 |
| NFR-20 | The Schedule H1 register and recall notification are outputs of the ledger, not a parallel book; a recall lists every counterparty that received the lot, from genealogy and movement history | register rebuilt from movements equals the stored register; 0 recall rows kept in step by hand | `WhinScheduleH1RegisterService`, `WhinScheduleH1RegisterRebuildIntegrationTest`; `WhinRecallNotificationService`, `WhinRecallNotificationNoLotListTest` | FR-457 |
| NFR-21 | v2 association junctions are effective-dated with one current row per key (UoM defaults per supplier and B2B channel, site-scoped supplier preference, owner-set cages, tax-scheme codes for item / UoM / reason code, configuration scopes); warehouse and owner companies are v1 | overlap refused by the database for every junction | `EXCLUDE` constraints on `whb_reason_code_tax_treatments` (`V500072`), `whb_owner_companies` (`V500073`), `whb_warehouse_companies` (`V500078`) · the remaining junctions: not built (`NFR-DIV-03`) | FR-468 |

## 2. Code divergences

| ID | FR says | Code has (grep) | Source |
|---|---|---|---|
| NFR-DIV-01 | The partition **and archive** strategy is in force | archiving is disclosed as deferred (`NonFunctionalFoundationsTest$ArchiveBoundary.shouldDiscloseArchivingDeferredInTheSupportedOffer`) | FR-423 |
| NFR-DIV-02 | "Restore exists" | the test asserts restore, PITR and stated objectives are still **absent** and disclosed (PP-1) | FR-429 |
| NFR-DIV-03 | Six v2 dated junction families | only the reason-code tax treatments junction exists; no supplier UoM default, supplier preference, owner-set cage, item / UoM tax-scheme or configuration-scope junction table | FR-468 |
| NFR-DIV-04 | `FR-456` / `FR-457`: "no `P7`…`P10` task builds it" (R30 note in the FRD) | the regulated-goods pack is built and tested in `warehouse-india` (`V540183`, licence services, dispatch guard, Schedule H1 register, recall notifications) | FR-456, FR-457 |
| NFR-DIV-05 | `FR-422` is WITHDRAWN | `NonFunctionalFoundationsTest$PerformanceTargets` still asserts the eight `FR-422` numbers (R30 `CP-FR-003`) | FR-422 |
| NFR-DIV-06 | `FR-425` names **waybill** claiming | waybill / AWB pools are removed by `D-16` item 2; only task and zone claiming remain | FR-425 |
| NFR-DIV-07 | Rules verified only by the reviewer gate | `NFR-04` (list), `NFR-10`, `NFR-13`, `NFR-15` (help), `NFR-16`…`NFR-18` (behaviour) — 7 rows with no automated check | FR-427, FR-435, FR-440, FR-442, FR-443, FR-444, FR-445 |

## 3. Amendments

| Date | Change |
|---|---|
| 2026-10-23 | v0 derived for R30 `CP-FR-007` row 24 (`D-17` item a) |

## 4. Open rows

| ID | Question | Default | Source |
|---|---|---|---|
| NFR-OPEN-01 | **Segment decision (R30 `CP-FR-012`):** keep the style / variant / ratio-pack model for plant stores, or withdraw `FR-443`…`FR-445` as apparel-retail shape (`D-16` item 2). The schema is built (`NFR-16`…`NFR-18`) | keep the v1 schema rows already built; build nothing more until the user decides (recorded in `RETARGET-PROGRAM-STATUS.md` pending items) | FR-443, FR-444, FR-445 |
| NFR-OPEN-02 | **Segment decision `S-035` (pharma):** serve regulated goods or decline the segment in writing. The pack is built (`NFR-DIV-04`); if declined, `FR-456` / `FR-457` are withdrawn and the pack is removed or fenced behind a setting | rules `NFR-19`, `NFR-20` stand as built until the user decides | FR-456, FR-457 |
| NFR-OPEN-03 | `FR-468` names "B2B channel" UoM defaults; `whb_channels` keeps only the B2B kind (`D-16` item 2) — is the channel axis still wanted, or is the junction per customer / ship-to | per customer / ship-to | FR-468 |

## 5. Invariants and scenarios

Scenarios `WH-SC-043`, `WH-SC-198`, `WH-SC-051`, `WH-SC-119`, `WH-SC-300`, `WH-SC-253`, `WH-SC-247`, `WH-SC-248`, `WH-SC-241`, `WH-SC-194`, `WH-SC-255`, `WH-SC-254`, `WH-SC-270`, `WH-SC-385`, `WH-SC-389`, `WH-SC-392`, `WH-SC-324`.
