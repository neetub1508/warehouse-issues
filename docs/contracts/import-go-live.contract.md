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
| IGL-GRD-04 | A reversal reverses an applied batch once, never a reversal, and not when later data depends on it; an `ASN_LINES` reversal also refuses an ASN at a site outside the actor's tier or no longer `EXPECTED`; an `ITEM_SUPERSESSIONS` reversal locks the links first and refuses one gone since the import or one that has merged its stock (its `whb_stock_movements` name it) | `ALREADY_REVERSED` / `CANNOT_REVERSE_A_REVERSAL` / `IMPORT_REVERSAL_BLOCKED` | — | FR-416 |
| IGL-GRD-05 | Opening stock: one batch per checklist and site; the checklist is `OPEN` and its predecessor items are done; a file is uploaded; validation finished and every row ready; the opening period is open; the site's branch links are effective | `OPENING_BATCH_EXISTS` / `OPENING_CHECKLIST_NOT_OPEN` / `OPENING_PREDECESSORS_OPEN` / `OPENING_FILE_REQUIRED` / `OPENING_VALIDATION_NOT_FINISHED` / `OPENING_ROWS_NOT_READY` / `OPENING_PERIOD_NOT_OPEN` / `OPENING_LINKS_NOT_EFFECTIVE` / `OPENING_BATCH_STATUS` | — | FR-411 |
| IGL-GRD-06 | A line's content is posted once (a retry after failure never double-posts); the `OPENING_BALANCE` location exists at the site | `OPENING_CONTENT_ALREADY_POSTED` / `OPENING_LOCATION_MISSING` / `OPENING_MOVEMENT_NOT_POSTED` | movement idempotency key | FR-411 |
| IGL-GRD-07 | A checklist starts only with its freeze window recorded; one checklist per site and as-at; items complete in order; a system item is not completed by hand | `409 CUTOVER_FREEZE_REQUIRED` / `CUTOVER_DUPLICATE` / `CUTOVER_PREDECESSOR_OPEN` / `CUTOVER_ITEM_SYSTEM` / `CUTOVER_ITEM_DONE` | — | FR-413 |
| IGL-GRD-08 | Certify: opening posted, no blocking item open, the period ready, and the posted closing value equals the source value — a variance is refused, or accepted only with a justification | `409 CUTOVER_OPENING_NOT_POSTED` / `CUTOVER_BLOCKING_OPEN` / `CUTOVER_PERIOD_NOT_READY` / `CUTOVER_VARIANCE` / `422 CUTOVER_JUSTIFICATION_REQUIRED` | — | FR-412 |
| IGL-GRD-09 | Mapping: target exists, not mapped twice, a unit conversion that is possible, a proposal exists and its confidence clears the bound | `422 MAPPING_TARGET_NOT_FOUND` / `MAPPING_DUPLICATE_TARGET` / `MAPPING_IMPOSSIBLE_CONVERSION` / `MAPPING_NO_PROPOSAL` / `MAPPING_CONFIDENCE_BELOW_BOUND` | — | FR-414 |
| IGL-GRD-10 | A kind that declares `requiresAllRowsValid()` (every configuration kind) applies only when every row is valid | `IMPORT_BATCH_HAS_INVALID_ROWS` (refused up front; the batch is not marked FAILED) | `WhbImportBatchService` apply, `WhbImportBatchMapper.canApply` | CONFIG-CASE-13 |

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
| IGL-T4-05 | A bulk import of a master kind applies | the master rows are created or updated through the kind's handler, with the target screen's own rules, codes and words (one rule set); covered kinds: items, identifiers and barcodes, packaging, locations, opening stock, ASN lines, supersessions. **`ITEM_IDENTIFIERS`** — CREATE_ONLY, `whb_item_identifiers:create`; key owner + SKU + identifier type + value (+ counterparty), compared on channel-less rows; Primary = Yes only while the item has no primary, at most one per item per file; the packaging level is named by code — the row's counterparty's level, then the supplier-agnostic one, then the item's only level of that code; a code several counterparties' levels share is refused asking for the counterparty. **`ITEM_PACKAGING_LEVELS`** — CREATE_ONLY, `whb_item_packaging_levels:create`; key item + level code (+ counterparty); the parent may be on file or on an earlier row of the file (resolved as the identifier's level); the screen's hierarchy guard; Default = Yes only while the item has none, and **refused on a retired level** (`IMPORT_FIELD_INVALID`; the screen silently stores No — the import reports instead). **`ASN_LINES`** — CREATE_ONLY, `wh_asns:edit`; each row appends one line to an existing `EXPECTED` ASN named by site + supplier + ASN number, numbered after its last line (never the edit's delete-and-rewrite); the actor's site tier; the site, supplier and the ASN's carrier still active (`WAREHOUSE_RETIRED` / `COUNTERPARTY_RETIRED`, as the screen's edit); the line guard (`ASN_PO_LINE_NOT_FOUND`, declarable PO line, `UOM_NOT_CONVERTIBLE`); serials unique across the whole ASN; apply locks each header, **re-reads it under the lock** and re-checks `EXPECTED` and serial uniqueness on the re-read state (`ASN_NOT_EDITABLE` / `ASN_SERIAL_DUPLICATE` fail the batch); **the re-read header's site and supplier must still be the ones the PO lines were validated against** — an ASN moved while the import waited fails the batch `IMPORT_ROW_NO_LONGER_VALID`. **`ITEM_SUPERSESSIONS`** — CREATE_ONLY, `whb_item_supersessions:create`; key old part (owner + SKU) + new part (owner + SKU) + effective date (`SUPERSESSION_ALREADY_EXISTS`, in-file `IMPORT_DUPLICATE_ROW`); the screen's shape guard (`SUPERSESSION_SELF` / `BIDIRECTIONAL_ONLY_INTERCHANGE` / `SUPERSESSION_DATES_INVALID`); the old part may be retired, the new part active (`UNKNOWN_ITEM` / `ITEM_RETIRED`); dates are SQL `DATE`, a zoned value a cell error; **the cycle is walked over the chain on file and the file's earlier rows together** (A → B and B → A in one file refused `SUPERSESSION_CYCLE`), the database function's own rule (links not ended before the row's date; INTERCHANGE exempt); apply re-validates every row in its own transaction and the V500050 trigger is the backstop; stock treatment always `KEEP_SEPARATE` — MERGE_STOCK stays its own action under `:merge` (FR-072). Supplier price files are not a kind here — `P9-06` #583 | the kind's `WhbImportHandler` | FR-418 — **see §10 row 1** |
| IGL-T4-06 | A configuration kind's transfer file is imported (FR-414 / RL-012, CONFIG-CASE-13) | each row is upserted on the object's portable key through the object screen's own request, rules and create / update (INSTALL stamping, audit and cache eviction stay the screen's); only codes travel, resolved against the target's masters by one batch read per chunk; a row naming module seed is refused `IMPORT_SEED_ROW`; an identical re-import is UNCHANGED, an update records each changed cell before → after; a versioned object (allocation strategy, putaway rule) updates through its cut-version path; a number series never carries its counter; reversal restores before-images or retires created rows, never deletes, and is refused `IMPORT_REVERSAL_BLOCKED` once a row changed (any write after the batch applied, or a changed cell) or is in use (a template whose rows straddle a reversal chunk is not refused for that reversal's own earlier write); a scoped importer never reads or writes a row outside its scope (`IMPORT_PERMISSION_REQUIRED`) — a caller with no read tier reads no number series, a company-wide one included; scope and permission checks are the batch's named actor's, so a document-path pass on the background executor (no security context) answers exactly as the HTTP path would for that user. Kinds: `REASON_CODES` (context + code), `TASK_TYPES`, `DISPOSITIONS`, `DOCUMENT_TYPES`, `LOCATION_TYPES`, `STOCK_STATUSES`, `UOM_CLASSES`, `SOURCE_SYSTEMS`, `ATTRIBUTE_KEYS`, `MOVEMENT_TYPES`, `CHANNELS`, `ITEM_VARIANT_AXES` (values in one cell, a value a variant item carries is never dropped), `WH_HOLD_TYPES` (code); `ALLOCATION_STRATEGIES` (code → active version, ordering rules in one cell; selection rules never travel — they name this database's sites, items, owners and counterparties — and an update keeps the stored ones, R33 D8); `WH_PUTAWAY_RULES` (site + code); `NUMBER_SERIES` (module + series + company / site / branch codes); `ALERT_RULES` (alert type + scope type + scope code, conditions and recipients in cells); `WAREHOUSE_SETTINGS` (UPDATE_ONLY on `setting_key`, revision-aware `bulkUpdateSettings`, only values that differ from the default travel; a stale dry run is refused per key against the before-value it showed, and `whb_settings:edit` + `admin_settings:edit` are checked at the dry run); `WH_PRINT_TEMPLATE` (UPSERT on code, every published version, a present version with another body refused). Permission `<resource>:import` (→ own `:view` + `whb_import_batches:view/create/apply`); settings `whb_settings:edit` | `WhbRegistryImportHandler` + one handler per kind; `WhbImportBatchService` | FR-414, RL-012 |

## 5. T5 — Screen contract

| ID | Screen · grid · scope | Contract | Source |
|---|---|---|---|
| IGL-T5-01 | WS-065 Import Batches · `whb_import_batches` · `WAREHOUSE_IMPORT_BATCH` | `importKind`, `fileName`, `status`, `totalRows`, valid / invalid counts; detail = rows with the per-cell error preview; actions Apply · Reverse · Discard | FR-416, FR-418 |
| IGL-T5-02 | WS-150 Opening Stock Batches · `wh_opening_stock_batches` · `WAREHOUSE_OPENING_STOCK_BATCH` | `batchNumber`, `companyName`, `warehouseName`, `asAtDate`, status; rows grid with validation status and error; actions Upload · Validate · Stage · Post · Reverse · Delete by state | FR-411 |
| IGL-T5-03 | WS-151 Cut-over Checklists · `wh_cutover_checklists` · `WAREHOUSE_CUTOVER_CHECKLIST` | `checklistNumber`, `companyName`, `warehouseName`, target go-live, freeze window, items with state; **Certificate** view (`/certificate`); Certify · Reopen | FR-412, FR-413 |
| IGL-T5-04 | WS-152 Migration Mappings · `wh_migration_mappings` · `WAREHOUSE_MIGRATION_MAPPING` | `profileCode`, `sourceProduct`, `entityKind`, `sourceValue`, target, confidence; Resolve · Bulk resolve · Unresolve; Export profile | FR-414 |
| IGL-T5-05 | Every configuration object's own screen (the 17 registries / masters of `IGL-T4-06`; Admin Settings → Warehouse for settings) | an "Export Transfer File" button gated by `<resource>:export` (settings: `whb_settings:edit`) writes `GET …/export-import-file`, the kind's own CSV built from the handler's columns: the whole INSTALL set (never the grid filter), no ids, no audit; number series and putaway rules limited to what the caller may read. Import needs no new screen — the kind is in the Import Batches picker. Grants (V511436): each of the 17 `<resource>:import` verbs is granted to every role other than `ADMIN` and `AUDITOR` that holds both that screen's `:create` and `:edit` — the `V510223` rule for `wh_print_templates:import`; `AUDITOR` never imports; the settings kind needs no `:import` verb (`whb_settings:edit` + `admin_settings:edit`) | FR-414 |

## 6. Out of scope

The platform's client-side `ImportButton` wizard itself (platform); demand forecasting from imported history
(`warehouse-manufacturing`); one bundled "configuration package" file carrying every kind at once (each kind is its own transfer file, `IGL-T4-06` — a bundle is a follow-up, not v1.1); `whb_code_list_values` (seed only, no writer service).

## 7. Amendments

| Date | Change |
|---|---|
| 2026-10-23 | v0 derived (R30 `CP-FR-007` row 23) |
| 2026-10-23 | R31 `F-CB-017`: validate (`IGL-T1-01`, stores nothing) split from the stored dry run (`IGL-T1-01a`); `IGL-UNR-01` restated; `IGL-OPEN-01` decided |
| 2026-10-25 | `P1-10` #92 S4 (S3 F4/F5): `IGL-T4-05` records the `ITEM_IDENTIFIERS`, `ITEM_PACKAGING_LEVELS` and `ASN_LINES` modes, keys and rules (retired-level default refused; ASN header and serials re-read under the lock; retired site / supplier / carrier refused) and drops price files (`P9-06` #583); `IGL-GRD-04` gains the `ASN_LINES` reversal refusals; §10 row 1 partially closed (supersessions pending, #33) |
| 2026-10-26 | `P1-10` #92 S4 (S3 re-verify N1) + `G3`: `IGL-T4-05` — the `ASN_LINES` re-read header's site and supplier re-checked under the lock (`IMPORT_ROW_NO_LONGER_VALID`); `ITEM_SUPERSESSIONS` mode, key and rules (in-file cycle walk, KEEP_SEPARATE only); `IGL-GRD-04` gains the `ITEM_SUPERSESSIONS` reversal refusals; §10 row 1 closed |
| 2026-10-26 | `P3-18` #90 S2 (V511434): §6 narrowed (configuration kinds are in scope; a bundle file is not); `IGL-T4-06` configuration kinds, `IGL-GRD-10` all-or-nothing apply, `IGL-T5-05` transfer-file buttons; §10 row 2 closed |
| 2026-10-26 | `P3-18` #90 S4 (V511436): `IGL-T4-06` — selection rules do not travel (R33 D8), settings staleness is per key (G1.7 amended), reversal refuses any row written after apply, scoped importers confined to their scope |
| 2026-10-26 | `P3-18` #90 S4b (no migration): `IGL-T4-06` — no read tier reads no number series (F1), putaway and settings reversal refuse any write after apply (F2), print reversal is not refused for its own earlier chunk (F3), document-path passes check as the named actor (F4); `IGL-T5-05` states V511436's `:import` grants (F5) |

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
| 1 | `warehouse-base/…/service/whbitem/WhbItemImportHandler.java`, `warehouse-base/…/service/whblocation/WhbLocationGenerateImportHandler.java`, `warehouse/…/service/whopeningstock/WhOpeningStockImportHandler.java` (the registered handlers) | FR-418 | items, locations and opening stock have handlers; identifiers and barcodes, packaging, ASN lines, supersessions and price files have none — **Triage 2026-10-23: FIX-CODE** — owner `P1-10` #92, reopened. **2026-10-25: partially closed** — `WhbItemIdentifierImportHandler`, `WhbItemPackagingLevelImportHandler`, `WhAsnLineImportHandler` registered; supersessions pending (`G3`, #33 A2); price files moved to `P9-06` #583. **2026-10-26: closed** — `WhbItemSupersessionImportHandler` registered (`G3`) |
| 2 | — (no configuration-object import kind under `warehouse-base` / `warehouse`) | FR-414 | the v1.1 configuration package (one import kind per configuration object, upserted on `code`, dry run as a diff) is not built — **Triage 2026-10-23: FIX-CODE** — owner `P3-18` #90 (v1.1), reopened. **Closed 2026-10-26 (`P3-18` #90 S2, V511434):** 18 configuration kinds (`IGL-T4-06`), `WH_PRINT_TEMPLATE` upgraded to UPSERT with every version, all-or-nothing apply (`IGL-GRD-10`), transfer-file buttons (`IGL-T5-05`). `whb_alert_rules` / `whb_number_series` tell install rows by `created_by IS NOT NULL`, not an `owning_module` column (R33 decision on #90) |
