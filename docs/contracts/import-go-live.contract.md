# Functional Contract — Import framework and go-live: opening stock, cut-over checklist, reconciliation certificate, migration mappings

> **What this is.** The functional truth for bringing an install live: the **handler-registry import
> framework** (batches, rows, a typed handler per kind, dry run that persists nothing, a server-side path
> for large files, **a reversal path**), opening stock as a first-class document that posts
> `OPENING_BALANCE` movements, the cut-over checklist with its stock freeze window, the closing-value
> tie-out and **reconciliation certificate**, migration mapping profiles and imported demand history.
> Posting opening stock is the irreversible act here — it is corrected only by its own reversal.
>
> **Status.** Derived 2026-10-23 (v0) from `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` §6.24 (`FR-411`…`FR-418`)
> and verified against the built code in `classic`. Not ratified. Written for R30 `CP-FR-007` row 23 /
> `D-17` item 1.

---

## 0. Identity

| | |
|---|---|
| **Workflow** | Import: upload → validate (dry run) → apply → `APPLIED` / `FAILED` · reverse · discard. Go-live: cut-over checklist `OPEN` (freeze window, items) → mappings resolved → opening stock batch `DRAFT` → upload / validate / stage → `VALIDATED` → **Post** (`OPENING_BALANCE` movements) → value matched → **Certify** (`CERTIFIED`, certificate) · Reopen |
| **Module** | `warehouse-base` (`ai.warehousebase.service.whbimport`: `WhbImportHandler`, `WhbImportHandlerRegistry`, `WhbImportRunner`, `WhbImportServerPathJob`, `WhbImportErrorCodes`; `WhbImportBatchService`) + `warehouse` (`WhOpeningStockBatchService`, `WhOpeningStockImportHandler`, `WhCutoverChecklistService`, `WhCutoverCertificateService`, `WhMigrationMappingService`, `WhMigrationMappingImportHandler`, `WhDemandHistoryImportHandler`) |
| **Domain baseline** | `D-7` (standalone), `L-2` (append-only; correction is a reversal) · `RH-009` · [`accounting-handover`](accounting-handover.contract.md) `AHO-X-08`, `AHO-RPT-02` (opening stock as `OPENING_BALANCE` movements) · [`costing-valuation`](costing-valuation.contract.md) `CVL-T4-01` (the first layers) |
| **Owning tasks** | `issues/p1-10.md` (framework, reversal, dry run) · `issues/p1-01.md` (bulk import kinds) · `issues/p2-19.md` (opening stock, certificate, cut-over) · `issues/p3-18.md` (mapping profiles, demand history — PARTIALLY VOID) |
| **Primary tables** | `whb_import_batches`, `whb_import_batch_rows`; `wh_opening_stock_batches`, `wh_opening_stock_lines`; `wh_cutover_checklists`, `wh_cutover_checklist_items`; `wh_migration_mappings`; `wh_demand_history.is_migrated` |
| **Status columns** | `whb_import_batches.status` `VALIDATING`/`VALIDATED`/`APPLYING`/`APPLIED`/`FAILED`/`REVERSED`/`DISCARDED` (rows `VALID`/`INVALID`/`CREATED`/`UPDATED`/`SKIPPED`) · `wh_opening_stock_batches.status` `DRAFT`/`VALIDATED`/`POSTED`/`REVERSED` · `wh_cutover_checklists.status` `OPEN`/`CERTIFIED` (items `OPEN`/`DONE`) |
| **Permission resources** | `whb_import_batches:{view,create,apply,reverse,export}` · `wh_opening_stock_batches:{view,create,edit,post,reverse,delete,export}` · `wh_cutover_checklists:{view,create,edit,certify,delete,export}` · `wh_migration_mappings:{view,edit,export,export_profile}` |
| **Routes** | WS-065 `/warehouse/platform/imports` · WS-150 `/warehouse/golive/opening-stock` · WS-151 `/warehouse/golive/cutover` · WS-152 `/warehouse/golive/mappings` · mobile: none (`D-16` item 7) |
| **Contract version** | `v0 — 2026-10-23` |

### Acceptance checks

| # | Expects | Delivered by |
|---|---|---|
| A1 | Opening stock carries quantity, cost, layer, lot, expiry, MRP, serial, bin, owner and duty status and posts balanced (`WH-SC-049`) | `IGL-T1-05`, `IGL-T4-01` |
| A2 | Tie-out and a reconciliation certificate (`WH-SC-050`) | `IGL-T1-08`, `IGL-GRD-08` |
| A3 | Cut-over checklist with a freeze window (`WH-SC-050`) | `IGL-T1-07`, `IGL-GRD-07` |
| A4 | Handler-registry framework with a reversal path; large files server-side (`WH-SC-047`) | `IGL-T1-01`…`-04`, `IGL-GRD-01`, `-02` |
| A5 | Validate honours dry run and persists nothing (`WH-SC-048`) | `IGL-UNR-01` |

---

## 1. T1 — State machine

### 1.1 Status inventory

| Entity | Status | Reachable via | Exits via | Kind |
|---|---|---|---|---|
| Import batch | `VALIDATING` → `VALIDATED` | `IGL-T1-01` | `-02`, `-04` | initial |
| Import batch | `APPLYING` → `APPLIED` / `FAILED` | `IGL-T1-02` | `APPLIED` → `-03`; `FAILED` → re-apply | active |
| Import batch | `REVERSED` / `DISCARDED` | `-03` / `-04` | none | **terminal** |
| Opening stock batch | `DRAFT` → `VALIDATED` → `POSTED` → `REVERSED` | `IGL-T1-05`, `-06` | — | ladder |
| Cut-over checklist | `OPEN` ↔ `CERTIFIED` | `IGL-T1-07`, `-08`, `-09` | — | ladder |

### 1.2 Transitions

| ID | From | Event | To | Guard | Actor | Side effects | Reason? | Source |
|---|---|---|---|---|---|---|---|---|
| IGL-T1-01 | — | **Validate** a file for an import kind (small path `POST /validate`; above `bulk_import_max_rows`: `POST /documents` upload, then `POST /documents/{id}/validate`, 202, polled on `GET /validations/{token}`) | no batch (nothing stored) | `IGL-GRD-01`, `-02` | `whb_import_batches:create` | **persists nothing** — per-row results with a per-cell error preview are returned, not stored (`WhbImportBatchController.java:51-54`) | no | FR-416, FR-418 |
| IGL-T1-01a | — | **Store the dry run** (small path `POST /`; server path `POST /documents/{id}`, 202 background) | `VALIDATING` → `VALIDATED` | `IGL-GRD-01`, `-02` | `whb_import_batches:create` | the batch row and its row results are stored — this is the dry run Apply later re-validates and writes; progress on the batch row | no | FR-416, FR-417 |
| IGL-T1-02 | `VALIDATED` · `FAILED` | Apply (re-validates every row against the database as it is now) | `APPLYING` → `APPLIED` / `FAILED` | `IGL-GRD-03` | `:apply` | the handler writes in batches; a failed apply leaves nothing and the batch is re-runnable | no | FR-416 |
| IGL-T1-03 | `APPLIED` | **Reverse** | `REVERSED` | `IGL-GRD-04` | `:reverse` | the handler's reversal undoes what the batch applied | **yes** | FR-416 |
| IGL-T1-04 | `VALIDATED` · `FAILED` | Discard | `DISCARDED` | — | `:apply` | nothing applied | no | FR-416 |
| IGL-T1-05 | — | Create an opening stock batch for a company / site / as-at date under an `OPEN` cut-over checklist; upload, validate (dry run), stage | `DRAFT` → `VALIDATED` | `IGL-GRD-05` | `wh_opening_stock_batches:create` / `:edit` | lines: item, location (bin), owner, lot, serial, stock status, duty status, quantity, UoM, unit cost, extended value, layer date, MRP, expiry | no | FR-411 |
| IGL-T1-06 | `VALIDATED` | **Post** | `POSTED` | `IGL-GRD-05`, `-06` | `:post` | `IGL-T4-01` | no | FR-411 |
| IGL-T1-06a | `POSTED` | Reverse | `REVERSED` | the operating period has not opened and the site is not certified (`OPENING_OPERATING_PERIOD_OPENED`, `OPENING_SITE_CERTIFIED`) | `:reverse` | reversal movements; the layers are relieved | **yes** | FR-411, FR-416 |
| IGL-T1-07 | — | Create a cut-over checklist: company, site, as-at date, target go-live, **freeze window** (`freeze_starts_at`/`_ends_at`) | `OPEN` | `IGL-GRD-07` | `wh_cutover_checklists:create` / `:edit` | items seeded in order: `MAPPINGS_RESOLVED`, `FREEZE_STARTED`, `COUNT_COMPLETED`, `OPENING_POSTED`, `VALUE_MATCHED`, `OPENING_PERIOD_CLOSED`, `SNAPSHOT_JOB_ENABLED`, `OPERATING_PERIOD_OPENED`; system items complete themselves | no | FR-413 |
| IGL-T1-08 | `OPEN` | **Certify** | `CERTIFIED` | `IGL-GRD-08` | `:certify` | the certificate: `certified_source_value`, `certified_posted_value`, `certified_variance`, a platform document (`certificate_document_id`) | no | FR-412 |
| IGL-T1-09 | `CERTIFIED` | Reopen | `OPEN` | — | `:certify` | `certificate_invalidated_at`, `reopened_at` | **yes** | FR-412 |
| IGL-T1-10 | — | Resolve / bulk-resolve / unresolve a migration mapping (source value → target) | — | `IGL-GRD-09` | `wh_migration_mappings:edit` | — | no | FR-414 |

### 1.3 Guards

| ID | Predicate | Refusal | Backstop | Source |
|---|---|---|---|---|
| IGL-GRD-01 | The kind has a registered handler; the caller holds the kind's permission; the header carries every column; the file is readable | `IMPORT_PERMISSION_REQUIRED` / `IMPORT_HEADER_MISSING` / `IMPORT_FILE_UNREADABLE` | `WhbImportHandlerRegistry` | FR-416 |
| IGL-GRD-02 | Per row: required fields present, within length, valid, not frozen, not duplicated in the file; an unknown item is named | `IMPORT_FIELD_REQUIRED` / `_TOO_LONG` / `_INVALID` / `_FROZEN` / `IMPORT_DUPLICATE_ROW` / `UNKNOWN_ITEM` per cell | — | FR-418 |
| IGL-GRD-03 | Apply re-validates; a row that no longer holds is refused, not applied | `IMPORT_ROW_NO_LONGER_VALID` | — | FR-416 |
| IGL-GRD-04 | A reversal reverses an applied batch once, never a reversal, and not when later data depends on it | `ALREADY_REVERSED` / `CANNOT_REVERSE_A_REVERSAL` / `IMPORT_REVERSAL_BLOCKED` | — | FR-416 |
| IGL-GRD-05 | Opening stock: one batch per checklist and site; the checklist is `OPEN` and its predecessor items are done; a file is uploaded; validation finished and every row ready; the opening period is open; the site's branch links are effective | `OPENING_BATCH_EXISTS` / `OPENING_CHECKLIST_NOT_OPEN` / `OPENING_PREDECESSORS_OPEN` / `OPENING_FILE_REQUIRED` / `OPENING_VALIDATION_NOT_FINISHED` / `OPENING_ROWS_NOT_READY` / `OPENING_PERIOD_NOT_OPEN` / `OPENING_LINKS_NOT_EFFECTIVE` / `OPENING_BATCH_STATUS` | — | FR-411 |
| IGL-GRD-06 | A line's content is posted once (a retry after failure never double-posts); the `OPENING_BALANCE` location exists at the site | `OPENING_CONTENT_ALREADY_POSTED` / `OPENING_LOCATION_MISSING` / `OPENING_MOVEMENT_NOT_POSTED` | movement idempotency key | FR-411 |
| IGL-GRD-07 | A checklist starts only with its freeze window recorded; one checklist per site and as-at; items complete in order; a system item is not completed by hand | `409 CUTOVER_FREEZE_REQUIRED` / `CUTOVER_DUPLICATE` / `CUTOVER_PREDECESSOR_OPEN` / `CUTOVER_ITEM_SYSTEM` / `CUTOVER_ITEM_DONE` | — | FR-413 |
| IGL-GRD-08 | Certify: opening posted, no blocking item open, the period ready, and the posted closing value equals the source value — a variance is refused, or accepted only with a justification | `409 CUTOVER_OPENING_NOT_POSTED` / `CUTOVER_BLOCKING_OPEN` / `CUTOVER_PERIOD_NOT_READY` / `CUTOVER_VARIANCE` / `422 CUTOVER_JUSTIFICATION_REQUIRED` | — | FR-412 |
| IGL-GRD-09 | Mapping: target exists, not mapped twice, a unit conversion that is possible, a proposal exists and its confidence clears the bound | `422 MAPPING_TARGET_NOT_FOUND` / `MAPPING_DUPLICATE_TARGET` / `MAPPING_IMPOSSIBLE_CONVERSION` / `MAPPING_NO_PROPOSAL` / `MAPPING_CONFIDENCE_BELOW_BOUND` | — | FR-414 |

### 1.4 Unreachable

| ID | Must never happen | Why it cannot | Source |
|---|---|---|---|
| IGL-UNR-01 | A validate or dry-run call that persists rows (the duplicate-rows-on-real-import defect) | `WhbImportRunner` validates read-only for the validate endpoints (`IGL-T1-01`, which store nothing); only the dry-run endpoints (`IGL-T1-01a`) store a batch, and they write the batch and its row results, never target rows | FR-417 |
| IGL-UNR-02 | Opening stock loaded by a script or as an unexplained opening figure | it is a document that posts `OPENING_BALANCE` movements (`AHO-RPT-02`) | FR-411 |
| IGL-UNR-03 | An import that cannot be reversed | every handler supplies a reversal; the batch keeps what it applied | FR-416 |
| IGL-UNR-04 | Raising the global `bulk_import_max_rows` to fit a large file | large files take the server-side path | FR-416 |
| IGL-UNR-05 | Migrated demand mixed silently with posted demand | every row the demand-history import writes carries `is_migrated = true` | FR-415 |

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from | Source |
|---|---|---|---|---|
| IGL-T2-01 | Import create / apply / reverse / discard | `whb_import_batches:create` / `:apply` / `:reverse` / `:apply` | see §1.2 | FR-416 |
| IGL-T2-02 | Opening stock create / edit / post / reverse / delete | `wh_opening_stock_batches:*` | `DRAFT` (edit, delete), `VALIDATED` (post), `POSTED` (reverse) | FR-411 |
| IGL-T2-03 | Checklist create / complete items / certify / reopen | `wh_cutover_checklists:create` / `:edit` / `:certify` / `:certify` | `OPEN` / `OPEN` / `OPEN` / `CERTIFIED` | FR-412, FR-413 |
| IGL-T2-04 | Export / import a mapping profile | `wh_migration_mappings:export_profile` / `whb_import_batches:create` (kind `MIGRATION_MAPPING`) | — | FR-414 |

## 3. T3 — Time-driven rules

| ID | Rule | Trigger | Changes | Source |
|---|---|---|---|---|
| IGL-T3-01 | The server-side path parses, validates and applies in batches, reporting progress; a pass that stops reporting is marked interrupted | `WhbImportServerPathJob` | batch progress, `FAILED` | FR-416 |
| IGL-T3-02 | The stock freeze window: between `freeze_starts_at` and `freeze_ends_at` (the count on the Sunday, go-live on the Monday) anything that moves is handled manually | the checklist's window | — | FR-413 |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in | Source |
|---|---|---|---|---|
| IGL-T4-01 | Opening stock posts | `OPENING_BALANCE` movements from the site's `OPENING_BALANCE` virtual location, at full grain (owner, duty status, lot, serial, bin), valued at the line's unit cost, so the ledger starts balanced and the **first cost layers** exist before the first issue (`CVL-T4-01`); handed over per `AHO-X-08` | `WhOpeningStockImportHandler` → writer | FR-411 |
| IGL-T4-02 | Opening posted and value matched | the checklist's `OPENING_POSTED` / `VALUE_MATCHED` items complete; the tie-out compares the posted closing value with the source value | `WhCutoverChecklistProgressService` | FR-412, FR-413 |
| IGL-T4-03 | A mapping profile is exported, or imported into another install | the profile (item master with classification, UoM and alternate units, godowns, parties, opening stock with batch and expiry, supersessions) moves as a file; install-created configuration rows carry `owning_module = 'INSTALL'` so an export can tell them from module seed | `WhMigrationMappingService`, `WhMigrationMappingImportHandler` | FR-414 |
| IGL-T4-04 | Twelve months of demand history are imported | `wh_demand_history` rows with `is_migrated = true` | `WhDemandHistoryImportHandler` (`DEMAND_HISTORY`) | FR-415 |
| IGL-T4-05 | A bulk import of a master kind applies | the master rows are created or updated through the kind's handler; covered kinds: items, identifiers and barcodes, packaging, locations, opening stock, ASN lines, supersessions, price files | the kind's `WhbImportHandler` | FR-418 — **see §10 row 1** |

## 5. T5 — Screen contract

| ID | Screen · grid · scope | Contract | Source |
|---|---|---|---|
| IGL-T5-01 | WS-065 Import Batches · `whb_import_batches` · `WAREHOUSE_IMPORT_BATCH` | `importKind`, `fileName`, `status`, `totalRows`, valid / invalid counts; detail = rows with the per-cell error preview; actions Apply · Reverse · Discard | FR-416, FR-418 |
| IGL-T5-02 | WS-150 Opening Stock Batches · `wh_opening_stock_batches` · `WAREHOUSE_OPENING_STOCK_BATCH` | `batchNumber`, `companyName`, `warehouseName`, `asAtDate`, status; rows grid with validation status and error; actions Upload · Validate · Stage · Post · Reverse · Delete by state | FR-411 |
| IGL-T5-03 | WS-151 Cut-over Checklists · `wh_cutover_checklists` · `WAREHOUSE_CUTOVER_CHECKLIST` | `checklistNumber`, `companyName`, `warehouseName`, target go-live, freeze window, items with state; **Certificate** view (`/certificate`); Certify · Reopen | FR-412, FR-413 |
| IGL-T5-04 | WS-152 Migration Mappings · `wh_migration_mappings` · `WAREHOUSE_MIGRATION_MAPPING` | `profileCode`, `sourceProduct`, `entityKind`, `sourceValue`, target, confidence; Resolve · Bulk resolve · Unresolve; Export profile | FR-414 |

## 6. Out of scope

The platform's client-side `ImportButton` wizard itself (platform); demand forecasting from imported history
(`warehouse-manufacturing`); the configuration-package import kinds (v1.1, see §10 row 2).

## 7. Amendments

| Date | Change |
|---|---|
| 2026-10-23 | v0 derived (R30 `CP-FR-007` row 23) |
| 2026-10-23 | R31 `F-CB-017`: validate (`IGL-T1-01`, stores nothing) split from the stored dry run (`IGL-T1-01a`); `IGL-UNR-01` restated; `IGL-OPEN-01` decided |

## 8. Invariants and scenarios

`L-2`, `D-7`; `WH-SC-047`…`WH-SC-050`. `FR-414`, `FR-415` have no scenario.

## 9. Open rows

| ID | Question | Default |
|---|---|---|
| IGL-OPEN-01 | Does anything refuse a movement at the site inside the freeze window, or is the window a record only? | **DECIDED R31 (2026-10-23):** default stands — record only, as built; the runbook captures movements made during the window (`FR-413` "anything that moves between is manual") |

## 10. Code divergences

The FRD rule is kept; the code is what differs.

| # | File:line | FR | Difference |
|---|---|---|---|
| 1 | `warehouse-base/…/service/whbitem/WhbItemImportHandler.java`, `warehouse-base/…/service/whblocation/WhbLocationGenerateImportHandler.java`, `warehouse/…/service/whopeningstock/WhOpeningStockImportHandler.java` (the registered handlers) | FR-418 | items, locations and opening stock have handlers; identifiers and barcodes, packaging, ASN lines, supersessions and price files have none — **Triage 2026-10-23: FIX-CODE** — owner `P1-10` #92, reopened |
| 2 | — (no configuration-object import kind under `warehouse-base` / `warehouse`) | FR-414 | the v1.1 configuration package (one import kind per configuration object, upserted on `code`, dry run as a diff) is not built — **Triage 2026-10-23: FIX-CODE** — owner `P3-18` #90 (v1.1), reopened |
