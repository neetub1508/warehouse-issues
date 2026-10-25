# Functional Contract — The module boundary, proved by `warehouse-adapter-example`

> **What this is.** The module-boundary invariants a reviewer can check by reading or by running the
> ratchets: **FK direction** (down only), the **enable flag**, the **owning-module guard** on seeded codes, **no
> cross-module table reads or writes**, the **sibling package**, the adapter's MAY / MUST-NOT list, the
> **reference fixture** that proves the port is expressible, the base **coupling test**, standalone as the
> reference configuration, the registration runbook and the migration rules. It is stated against
> `warehouse-adapter-example` (`D-11`), the only adapter that survives `D-16` (`D-1` amendment), and applies
> unchanged to every sibling module (`warehouse-3pl`, `warehouse-india`, `warehouse-trade`,
> `warehouse-manufacturing`, `D-16` item 5).
>
> **Status.** Derived 2026-10-23 (v0) from `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` §6.20 (`FR-349`…`FR-374`,
> withdrawn rows skipped) for R30 `CP-FR-007` row 19 under `D-17` item a. Verified against
> `classic/warehouse-adapter-example`, `warehouse-base` and `platform` by grep. v1 2026-10-26: R32 overlay conformance-reviewed on P0-14 #110 S3/S4. There is no state
> machine: every row is a structural invariant; T1 is the fixture's one document.

---

## 0. Identity

| | |
|---|---|
| **Workflow** | Install loads a module only when its flag is on → its own Flyway sub-band registers its codes under an owning-module guard → it posts and reverses through the movement port, reads through APIs, owns only its own tables → deleting it changes no line of `warehouse-base` |
| **Modules** | fixture `warehouse-adapter-example` (`ai.warehouseadapterexample`, band `V525000`–`V525999`, prefix `whae_`, flag `enable.warehouse.adapter.example`, CI-only: `warehouse-ratchets` job, not in `ModuleImportSelector`, Dockerfile or compose) · base `warehouse-base` |
| **Domain baseline** | `FR-349`…`FR-357`, `FR-363`, `FR-364`, `FR-366`, `FR-367`, `FR-371`…`FR-374` · `D-1` (amended), `D-2`, `D-7`, `D-9`, `D-10`, `D-11`, `D-16` items 4–5 · `L-3` |
| **Owning tasks** (R30 §4) | `issues/p0-14.md` (`FR-349`…`351`, `353`…`356`) · `p0-04` (`357`, `367`) · `p0-01` (`371`…`374`) · `p3-20` (`363`) · `p3-21` (`364`) · `p6-08` (`366`) |
| **Primary artefacts** | `V525000` (registers `ADAPTER_EXAMPLE`, `EXAMPLE_DOCUMENT`, `EXAMPLE_RECEIPT`), `V525010` (`whae_example_documents`, item cross-reference `EXAMPLE-ITEM-0001`), `V525020` (`whae_example_received_events`, `ADAPTER_EXAMPLE` outbox subscription, hold release reason) · `WarehouseAdapterExampleModuleConfig`, `WhaeExampleDocumentPostingService`, `WhaeExampleDocumentRepository` · tests `ArchitectureInvariantsTest` (example), `WhaeExampleDocumentPostingIntegrationTest`, `WarehouseBaseCouplingTest` · `platform/.../ModuleImportSelector.java` |
| **Withdrawn, not covered** | `FR-352`, `FR-358`…`FR-362`, `FR-365`, `FR-368`…`FR-370` (`D-16` / `D-17` item 5) |
| **Contract version** | `v1 — 2026-10-26` |

### Acceptance checks

| # | Expects | Delivered by |
|---|---|---|
| A1 | No base or core table keys to a module table; module FKs point down | `MOD-GRD-01`, `MOD-UNR-01` |
| A2 | A module is inert unless its flag is on | `MOD-GRD-02` |
| A3 | A module inserts only codes it owns | `MOD-GRD-03` |
| A4 | A module changes stock only through the port and reads no other module's tables | `MOD-GRD-04`, `MOD-UNR-02` |
| A5 | The fixture posts, reserves, releases, subscribes and reverses using only the public API (consume through the port: `MOD-DIV-04`) | `MOD-T1-01`–`MOD-T1-04`, `MOD-T4-05` |

---

## 1. T1 — The fixture's document

| ID | From | Event | To | Guard | Actor / class | Side effects | Source |
|---|---|---|---|---|---|---|---|
| MOD-T1-01 | `DRAFT` | Post an example document | posted (movement id recorded) | **DRAFT only** — any other status → `EXAMPLE_DOCUMENT_NOT_DRAFT` 409, no port call (R32 F6); then the port's own guards; item named by `(source_module ADAPTER_EXAMPLE, external_id)` and resolved by the port through `whb_item_external_refs` — unmapped → the port's `UNKNOWN_ITEM` refusal | `WhaeExampleDocumentPostingService.post` → `WhbMovementPortService` | one `EXAMPLE_RECEIPT` movement; only `whae_example_documents` is saved by the adapter | FR-349, FR-353 |
| MOD-T1-02 | posted | Reverse with a reason | reversed | **POSTED only** — any other status → `EXAMPLE_DOCUMENT_NOT_POSTED` 409, no port call (R32 F6); reason code required by the port. **Amended R32 D2:** reverse AFTER release (`MOD-T1-04`) — with the document's own hold open, the reversal is refused `INSUFFICIENT_STOCK` when the position's free stock is below the reversal quantity, and nothing changes (`WhbStockPositionWriter`). Once the P0-08 follow-up lands (`MOD-DIV-04`), the reversal names the hold and consumes it in the same transaction | `WhaeExampleDocumentPostingService.reverse` | `RECEIPT_REVERSAL` (a true reversal type, `L-3`, asserted in `V525000`) | FR-349, FR-353 |
| MOD-T1-03 | posted | Hold the received stock | posted, hold OPEN | **POSTED only** → `EXAMPLE_DOCUMENT_NOT_POSTED` 409; base's reservation guards (holder system / document type ACTIVE, free stock — shortage → `INSUFFICIENT_STOCK`) | `WhaeExampleReservationService.reserve` → `WhbReservationService.create` (`POST /warehouse/ledger/reservations`) | one HARD reservation, holder quad `ADAPTER_EXAMPLE / EXAMPLE_DOCUMENT / <document id> / 1`, the destination line's item (read back through `WhbStockMovementQueryService.getById`); on-hand unchanged | FR-353, R32 D1 |
| MOD-T1-04 | posted, hold OPEN | Release the hold | posted, hold **RELEASED** | base's release guards (owner + site scope, release guard); reason `RESERVATION_RELEASE/EXAMPLE_DOCUMENT_CANCELLED` (adapter-owned, V525020 — `requireReleaseReason` accepts any ACTIVE `RESERVATION_RELEASE` reason outside `SYSTEM_ONLY_REASONS`) | `WhaeExampleReservationService.release` → `WhbReservationService.releaseByHolder` (`DELETE /warehouse/ledger/reservations`) | `stock.reservation.released` on the outbox; the hold reads RELEASED, never CONSUMED (`WhaeExampleDocumentPostingIntegrationTest.anAdapterReleasesItsHoldThenReversesAndItsSubscriberReceivesTheFacts`) | FR-353, R32 D1 |

## 2. Guards

| ID | Predicate (must hold) | Refusal / where it fails | Checked by | Source |
|---|---|---|---|---|
| MOD-GRD-01 | **FK direction.** Every FK on a module table points to its own tables, a base table or a platform table; no `whb_`/`wh_` table carries an FK to a module table | `V525010` raises `(WH-SC-225): a warehouse table carries a foreign key to whae_example_documents`; build fails | `V525010` self-assert; `WarehouseBaseCouplingTest.shouldDeclareNoForeignKeyOutOfWarehouseBase`, `shouldDetectABaseTableKeyedToAnAdapterTable` | FR-350, FR-354 |
| MOD-GRD-02 | **Enable flag.** The module's config is `@ConditionalOnExpression("${enable.<module>:false}")`; off means no bean, no endpoint, no job | inert install | `WarehouseAdapterExampleModuleConfig`; same shape in `Wh3plModuleConfig`, `WarehouseIndiaModuleConfig` | FR-371, FR-373 |
| MOD-GRD-03 | **Owning-module guard.** A seed migration inserts only codes whose `owning_module` is itself and refuses if the code exists under another module; inserts are idempotent (`ON CONFLICT DO NOTHING`) | `V525000 (RL-003): a code owned by warehouse-adapter-example already exists under another module` | `V525000`; `WarehouseBaseCouplingTest.shouldOwnEverySeededCodeOnce`, `shouldDetectACodeSeededByTwoModules` | FR-356, FR-349 |
| MOD-GRD-04 | **No cross-module table reads.** A module reads balances and availability through an API, never a table; it never reads or writes another module's (or accessories') stock tables | build fails | `ArchitectureInvariantsTest` (example) `shouldNameOnlyPlatformBaseAndItself`, `shouldKeepItsMigrationsToItsOwnBandAndTables`; `WarehouseBaseCouplingTest.shouldNeverReadTheOtherSystemsTables` | FR-349, FR-350, FR-367 |
| MOD-GRD-05 | **Sibling package.** A module lives in `ai.<module>` (e.g. `ai.warehouseadapterexample`), never under `ai.warehouse.*` | build fails | `ArchitectureInvariantsTest.shouldLiveInTheSiblingPackage` | FR-351 |
| MOD-GRD-06 | **Own sub-band.** A module's migrations are inside its declared band and create only its own prefix; the only base writes are INSERTs into the §8.2 A6–A8 registration tables **and `whb_outbox_subscriptions`** (R32 D3, §8.2 A10 — an IN_PROCESS subscriber's row ships with its bean); an UPDATE / DELETE of it, or any other `whb_` write, is B1 | build fails | `shouldKeepItsMigrationsToItsOwnBandAndTables`; `WarehouseBaseCouplingTest.shouldDetectBandViolations`; `tools/check-design-set.py` check 4 | FR-356, FR-374 |
| MOD-GRD-07 | **Open vocabularies.** No `CHECK (… IN (…))` on any registry column | build fails | `WarehouseBaseCouplingTest.shouldFindNoCheckConstraintOnARegistryColumn`, `shouldDetectAPlantedCheckConstraint`, `shouldLeaveTheOpenVocabulariesUnchecked` | FR-354, FR-350 |
| MOD-GRD-08 | **Forbidden imports.** Base imports no app, adapter, 3PL, India, logistics or vertical package; the scanners are proved non-vacuous | build fails | `WarehouseBaseCouplingTest.shouldDetectAForbiddenImport`, planted-violation self-tests | FR-354, FR-371 |
| MOD-GRD-09 | **Accessories reserved.** Its source-system row is reserved and unclaimable; its package is on the forbidden-import list | build fails | `WarehouseBaseCouplingTest.shouldKeepAccessoriesReserved`, `shouldDetectAnUnreservedOrClaimedAccessoriesRow` | FR-367 |
| MOD-GRD-10 | **Display resolver fallback.** Resolvers are a bean collection; base ships a fallback rendering type + id; a module may register none (`display_resolver_bean NULL` on `EXAMPLE_DOCUMENT`) | unresolved reference renders type + id, never blank | `BaseWarehouseDocumentDisplayResolver`, `WarehouseDocumentDisplayResolver` | FR-357 |
| MOD-GRD-11 | **Controller package and frontend names.** Controllers sit in `ai.<module>.controller`; every frontend filename carries the module prefix (`Wh3pl*`, `Whin*`, `Whb*`, `Wh*`) | activity aspect blind / last-write-wins merge | grep; `ArchitectureInvariantsTest` per module | FR-372 |
| MOD-GRD-12 | **Registration runbook.** A shipped module has its `ModuleImportSelector` entry (base, warehouse, 3PL, India present) and the rest of the 16-file list; the CI-only fixture deliberately has none | JAR ships and loads nothing | `ModuleImportSelector` constants; `p0-01` runbook | FR-373 |
| MOD-GRD-13 | **Migrations idempotent.** Every DDL `IF NOT EXISTS`, every seed `ON CONFLICT` / `WHERE NOT EXISTS` | blind repair + retry re-runs it | `V525000`, `V525010`; reviewer | FR-374, FR-356 |
| MOD-GRD-14 | **Zero commits to base.** Adding the fixture (or any module) changes no file under `warehouse-base`; platform edits (filter allowlist, cache registry) are expected (`D-10`) | ratchet broken | `git log` of the module's tasks; the fixture's `EXAMPLE_RECEIPT` description states it | FR-355 |

### 2.1 Unreachable

| ID | Forbidden | What makes it unreachable | Source |
|---|---|---|---|
| MOD-UNR-01 | A module writing a base or app table, adding a base column, defining a second envelope or idempotency scheme, reusing another module's source-system code | port is the only writer; `ADAPTER_EXAMPLE` claimed once; `MOD-GRD-01`, `-03`, `-04` | FR-350 |
| MOD-UNR-02 | Stock changed outside the port | the fixture's only stock change is `WhbMovementPortService`; from base it also imports the reservation API (`WhbReservationService`, its request / response DTOs), the movement read (`WhbStockMovementQueryService`) and the outbox SPI (`WhbOutboxEventSubscriber`, `WhbOutboxEventResponse`) — none of them moves stock. **"Consume" through the port** means the post / reverse envelope names a hold of its own source quad and the hold closes CONSUMED in the same transaction; the port cannot express it yet (`MOD-DIV-04`), so the fixture releases instead | FR-350, FR-349 |
| MOD-UNR-03 | An adapter between two of our own modules (logistics) | logistics posts through the port directly (`FR-366`) | FR-366 |
| MOD-UNR-04 | Dealer or automotive as a dependency of any warehouse capability | `D-16`; forbidden-import scanner | FR-371 |
| MOD-UNR-05 | A screen in the fixture | it ships zero screens | FR-353 |

## 3. T3 — Time rules

None. The fixture has no clock.

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in | Source |
|---|---|---|---|---|
| MOD-T4-01 | the fixture's migrations run | `ADAPTER_EXAMPLE` (claimable, not reserved, `post_permission warehouse:movements:post`), `EXAMPLE_DOCUMENT` (stock-bearing, external), `EXAMPLE_RECEIPT` (`IN`, `MUST_BALANCE_PER_OWNER_ITEM`, billable) registered in base registries; one item cross-reference seeded; release reason `EXAMPLE_DOCUMENT_CANCELLED` and IN_PROCESS subscription `WHAE_EXAMPLE_EVENTS` registered | `V525000`, `V525010`, `V525020`; `WhaeExampleDocumentPostingIntegrationTest.theAdaptersOwnMigrationsRegisterItsCodesInItsOwnSubBand` | FR-349, FR-356 |
| MOD-T4-02 | an upgrade adds a lower-banded module after warehouse | out-of-order migration is required and the upgrade guide says so | Flyway config; install guide | FR-374 |
| MOD-T4-03 | field-service adapter (v1.1) | the van is a mobile location, replenished by transfer, consumed at job close, counted, unreturned parts aged | `issues/p3-20.md` — **VOID** (R31 `MOD-OPEN-01`); `FR-363` WITHDRAWN by `D-16` — row kept as the record | FR-363 |
| MOD-T4-05 | an `ADAPTER_EXAMPLE` movement is posted or reversed, or its hold released | base's publisher delivers `stock.movement.posted` / `stock.reservation.released` / `stock.movement.reversed` to `WhaeExampleMovementEventSubscriber` (IN_PROCESS, filter of those three codes, version 1); each is recorded once in `whae_example_received_events`, unique `(subscriber_code, outbox_cursor)` — a redelivery records nothing new (PC-44); another source system's fact is skipped. **§8.2 A10 amended (R32 D3):** an in-process subscriber needs its `whb_outbox_subscriptions` row too, seeded by the module's own migration, not the bean alone | `V525020`; `WhaeExampleMovementEventSubscriber`; `WhaeExampleDocumentPostingIntegrationTest.anAdapterReleasesItsHoldThenReversesAndItsSubscriberReceivesTheFacts`; `WhaeExampleMovementEventSubscriberTest` | FR-353, PC-44 |
| MOD-T4-04 | assets adapter (v1.1) | spares issued against a complaint; hand-off to assets is an event carrying the serial | `issues/p3-21.md` — **VOID** (R31 `MOD-OPEN-01`); `FR-364` WITHDRAWN by `D-16` — row kept as the record | FR-364 |

## 5. T5 — Screen contract

None (`MOD-UNR-05`).

## 6. Code divergences

| ID | FR says | Code has (grep) | Source |
|---|---|---|---|
| MOD-DIV-01 | The fixture has one reservation and one subscriber, and its integration test posts, **reserves**, releases, reverses and reads back | **Split R32 D1, closed 2026-10-25 (P0-14 #110 S2):** reserve and subscribe are built — `WhaeExampleReservationService`, `WhaeExampleMovementEventSubscriber`, `V525020`; the IT pins (i) open hold → reversal refused `INSUFFICIENT_STOCK`, nothing changes, and (ii) release → reverse → hold reads RELEASED, released event received. The consume clause moved to `MOD-DIV-04` | FR-353 |
| MOD-DIV-04 | The fixture **consumes** its hold through the public API (`FR-353`, `MOD-OPEN-02`) | the movement port carries no consumed-hold reference: `WhbMovementPostCommand.consumedReservationIds` is set only in-process, `WhbMovementEnvelopeCodec` builds the command without it, `WhbMovementPortService.reverse` carries none; the only consume path is `WhbPickReservationService.consumeForDespatch` (`Propagation.MANDATORY`) — **Triage R32 D1: FIX-CODE (base)** — owner: the P0-08 #71 follow-up (port envelope consumed-hold reference on post and reverse); its acceptance includes the fixture IT step: reverse with the hold reference → the hold reads CONSUMED with the movement-line id. Apply-to `warehouse-3pl`, `warehouse-india` | FR-353, §8.2 A5 |
| MOD-DIV-02 | `warehouse-adapter-field-service` and `warehouse-adapter-assets` ship in v1.1 | no such module directory in `classic` — **resolved R31**: both FRs withdrawn, `p3-20` / `p3-21` VOID; no divergence remains — **Triage 2026-10-23: AMEND-SPEC** — applied R31 (FRs withdrawn); stands as the rule | FR-363, FR-364 |
| MOD-DIV-03 | "A released migration is never edited in place" | `D-16` item 4 supersedes it **for warehouse only** (clean rewrite, one DB rebuild); the FR carries no `D-16` note — **Triage 2026-10-23: AMEND-SPEC** — rule: for warehouse only, `D-16` item 4 supersedes the never-edit rule once — a clean migration rewrite and one DB rebuild (`P7-13`); every later migration is forward-only again. `FR-374` amended | FR-374 |

## 7. Out of scope

Withdrawn dealer / services / accessories adapter rows (see §0); the logistics module (`outbox-events.contract.md` `OEV-T4-09`).

## 8. Amendments

| Date | Change |
|---|---|
| 2026-10-23 | v0 derived for R30 `CP-FR-007` row 19 (`D-17` item a) |
| 2026-10-23 | R31: `MOD-OPEN-01` (withdraw; `MOD-T4-03`, `-04`, `MOD-DIV-02`), `MOD-OPEN-02` (extend the fixture) decided |
| 2026-10-25 | R32 D1–D3 (P0-14 #110 S2): `MOD-DIV-01` split — reserve + subscribe closed, consume → new `MOD-DIV-04` (P0-08 follow-up); `MOD-T1-01`/`-02` state the DRAFT / POSTED guards (F6) and `-02` reverses after release; `MOD-T1-03`/`-04` (reserve, release), `MOD-T4-05` (subscriber delivery + dedup, §8.2 A10 in-process row) added; `MOD-GRD-06` allowlists `whb_outbox_subscriptions` INSERT; `MOD-UNR-02` states what consume means through the port |
| 2026-10-26 | v1 (P0-14 #110 S4, S3 functional F3): `MOD-T1-02` refusal restated — an open hold refuses the reversal only when the position's free stock is below the reversal quantity; `V525020` added to the primary artefacts |

## 9. Invariants and scenarios

`L-3`; scenarios `WH-SC-044`, `WH-SC-164`, `WH-SC-179`, `WH-SC-223`, `WH-SC-224`, `WH-SC-225`, `WH-SC-246`, `WH-SC-272`, `WH-SC-292`.

## 10. Open rows

| ID | Question | Default | Source |
|---|---|---|---|
| MOD-OPEN-01 | `FR-363` / `FR-364` are active with live tasks `p3-20` / `p3-21`, but the `D-1` amendment says the adapter row survives only as the CI fixture — keep the two vertical adapters or withdraw them | **DECIDED R31 (2026-10-23):** withdraw — `FR-363` / `FR-364` WITHDRAWN by `D-16`, `p3-20` / `p3-21` VOID; plant spares to machines are core store issue to `MACHINE` (`D-1` amendment) | FR-363, FR-364 |
| MOD-OPEN-02 | `MOD-DIV-01`: extend the fixture to reserve, consume and subscribe, or restate `FR-353` | **DECIDED R31 (2026-10-23):** default stands — extend the fixture to reserve, consume and subscribe (`p0-14` acceptance). **R32 D1 (2026-10-25):** consume is not expressible through the port — reserve + release + subscribe built in P0-14; consume is `MOD-DIV-04` (P0-08 follow-up) | FR-353 |
