# Platform dependencies — what warehouse needs from `platform`, with a verdict per capability

<!-- check-design-set: issue-citations file #791 — `#790` and `#791` are issues in **`neetub1508/classic`**, cited as `classic#790, #791` with the second elided in the ordinary English way. The first resolves; the elided continuation reads to the checker as a bare `#NN`. It is a cross-repo citation, never a warehouse issue -->

> **What this document is.** A register. One row per platform capability the warehouse product
> depends on, with a verdict: **EXISTS AND FITS**, **EXISTS BUT SHAPE-MISMATCHES**, or **DOES NOT
> EXIST — BLOCKS SHIPPING**. Every row carries `file:line` and, where it blocks, the cost, the phase
> that owns the work, and whether it lands in `platform` or inside a warehouse module.
>
> **Authority.** [`DECISIONS.md`](DECISIONS.md) wins on module names, packages, bands and prefixes.
> [`reviews/R1-codebase-reality.md`](reviews/R1-codebase-reality.md) wins on what the existing
> codebase does. This document extends R1 §4, §7, §8 and §9 and **corrects four of its rows** where
> re-verification found them stale — those corrections are §0.
>
> **Method.** Reading and `grep` only, against `/Users/bbhushan/work/git/workspace/classic`,
> 2026-09-01. No `mvn` / `npm` / `tsc` was run. Every count carries its command. Anything not
> verified is marked **UNVERIFIED** with the command that would settle it.
>
> **The rule this document exists to enforce.** `warehouse-base` depends on **platform only** (D-1).
> Every row below is therefore either something platform already gives us, something platform gives
> us in the wrong shape, or something `warehouse-base` has to own itself. A row that would be
> satisfied by depending on a *vertical* is not a dependency — it is an architecture violation, and
> §1.4 lists the three places that temptation arises.

---

## 0. Corrections to R1 §4 found by re-verification

| # | R1 §4 / finding said | Verified reality (2026-09-01) | Consequence |
|---|---|---|---|
| **PD-1** | `branches` has `owner_type`/`owner_id` NOT NULL, `CHECK (owner_type IN (…,'WAREHOUSE',…))` and `UNIQUE (owner_type, owner_id, branch_code)` — cited from `V149:13-14,60,63`; `C-016` concludes *"`branches.owner_type` already allows `'WAREHOUSE'`"* | **The columns no longer exist.** `platform/…/V160__Remove_owner_fields_from_branches.sql:13` drops `owner_type`, `:16` drops `owner_id`, `:7` drops `uk_branches_owner_code`, `:10` drops `idx_branches_owner`, and `:19` adds `uk_branches_code UNIQUE (branch_code)` — **branch codes are now globally unique** (`:22` says so). The JPA entity confirms it: `platform/…/entity/Branches.java` has no `ownerType`/`ownerId` field, and its `@UniqueConstraint` at `:25` names `branch_code` alone | **`branches` is NOT polymorphic.** It was, for eleven migrations. Half of `C-016` still holds — `chk_branches_type` survives (`V149:61`) and still admits `'WAREHOUSE'` and `'DISTRIBUTION_CENTER'` — but there is no owner dimension to reuse. §2.1 |
| **PD-2** | `filterUtils.ts` has **210** scopes; `CacheConfiguration` has **202** cache names | **211** and **230**. Commands in §7 | Cosmetic, but it is why counts get re-computed rather than quoted |
| **PD-3** | R5 `S-092`: *"`grep -rli "impersonat"` across platform and both design sets = 0"* | **5 files now**, all in `accounting-base` — e.g. `accounting-base/…/service/audit/AccAuditActorKind.java:17` defines an actor kind for *"A support operator acting inside an impersonation grant"*. **The audit *schema* anticipates impersonation; no impersonation *feature* exists anywhere** | The ship-blocker stands (§3.6), but the schema precedent to copy now exists |
| **PD-4** | 6 assets `*_sequences` repositories carry `PESSIMISTIC_WRITE` | **8**: `ls assets/backend/src/main/java/ai/assets/repository/ \| grep -c SequenceRepository` → 8 (`AssetTag`, `AssetPo`, `AssetComplaint`, `AssetClearance`, `AssetWarrantyClaim`, `AssetInsuranceClaim`, `AssetServiceContract`, `AssetDisposal`) | More precedent, same conclusion. §4.5 |

---

## 1. EXISTS AND FITS — consume as-is

Fourteen capabilities warehouse inherits with no platform change. For each: the artefact, and how
warehouse uses it.

| # | Capability | Platform artefact (`file:line`) | How warehouse uses it |
|---|---|---|---|
| 1.1 | **Branch master** | `branches` @ `platform/…/V149__create_branches_table.sql:9`. Column is **`branch_name`, not `name`** (`:18`). `chk_branches_type` (`:61`) admits `SHOWROOM, SERVICE_CENTER, BOTH, WAREHOUSE, OFFICE, FACTORY, DISTRIBUTION_CENTER`. `branch_code` is **globally unique** since `V160:19` | A warehouse *site* **is** a platform branch with `branch_type='WAREHOUSE'` or `'DISTRIBUTION_CENTER'` — free, no schema change. `whb_locations` hangs off `branches.id`. **Do not repeat accessories' junction table**: `accessory_warehouses` has no `branch_id` and links through `accessory_warehouse_branch` (R1 `C-030`) |
| 1.2 | **Users and person display** | `user_details.employee_id` (**not** `employee_code`); canonical formatter `UserDetails.getFullName()` @ `platform/…/entity/UserDetails.java` | Every operator, counter, picker and approver is a platform user. Render people through the shared helper only — CLAUDE.md *USER DISPLAY FORMAT* and the duplicated-segment bug it names |
| 1.3 | **RBAC + permission dependencies** | `permissions` @ `V1_1__Initial_schema_safe.sql:30`; **`permission_dependencies` is a PLATFORM table** @ `V248:17-30`, with `uq_permission_dependency` (`:27`) and `chk_no_self_reference` (`:29`). Columns are `permission_id` / **`dependent_permission_id`** / `dependency_type DEFAULT 'REQUIRED'`. Semantics documented `V248:38-41` | `@PreAuthorize("hasAuthority('warehouse-movements:view')")` on every controller method. **INSERT rows into `permission_dependencies`; never `CREATE TABLE`** — the only other creator, `dealer/V20501:10`, is `IF NOT EXISTS` and now a no-op (R1 `C-017`, `T-10`) |
| 1.4 | **Menus** | `menus` @ `V16:7` with `CHECK (menu_level BETWEEN 1 AND 3)` (`:27`); `menu_translations` (`:49`); `menu_permissions` (`:36`); `required_permission_prefix` @ `V209:7`; `is_mobile_enabled` @ `V199:7` | One L1 "Warehouse" node for the whole family (the same decision `V600200:22-27` records for accounting). **Three menu levels only** — a receive→putaway→count tree must fit. **Every menu INSERT needs a `WHERE NOT EXISTS` guard**: there is no unique constraint on `(name, parent_id, menu_level)`, so `ON CONFLICT DO NOTHING` does not stop a duplicate on a Flyway retry (`assets/…/V60171:154-155` spells it out). Seed `en`/`fr`/`hi` `menu_translations` |
| 1.5 | **Grid configuration** | `grid_preferences` @ `V18:7` (`default_columns JSONB NOT NULL DEFAULT '[]'` `:12`), `user_grid_preferences` @ `V18:25`, `grid_column_definitions` @ `V18:43` (`UNIQUE(grid_identifier, column_key)` `:63`), **`filter_definitions`** @ `V229:8` (`uk_filter_definitions_grid_key` `:20`), `grid_preferences.default_filters JSONB` @ `V229:50-51` | Every warehouse grid is a `grid_identifier` with column and filter definition rows. **Two traps.** (a) `grid_filter_definitions` **does not exist** — `grep -rln "CREATE TABLE.*grid_filter_definitions"` → 0; the nine references in migrations are comments and one `IF EXISTS` guard. Inserting into that name crash-loops Flyway. (b) **`default_filters` AND `default_columns` must BOTH be populated**; `filter_definitions.default_visible = true` alone does not build the strip — `useGridPreferences` reads `grid_preferences.default_filters`. `V229:53-56` is the worked example |
| 1.6 | **Export** | `BaseExportService` @ `platform/…/service/BaseExportService.java`; `DEFAULT_MAX_EXPORT_ROWS = 10_000` (`:48`); `CSV_UTF8_BOM` (`:59`, with the reason at `:51-58`); `ExportService(List<ExportFormatHandler>)` @ `platform/…/service/export/ExportService.java:31`; `followVisibleColumns` @ `platform/frontend/src/types/export.ts:119`; ratchet `platform/backend/src/test/java/ai/platform/service/ExportServiceContractTest.java` | Grid↔export parity is the rule. **Return raw `Boolean` from `extractRowData`** — `BaseExportService` renders Yes/No on every path and does **not** expose `formatBoolean(Boolean)` (that is on `BaseController`), so calling it is a compile error (CLAUDE.md, R1 `T-17`). See §5.3 for the 10 000-row ceiling |
| 1.7 | **Import (frontend)** | `ImportButton.tsx`, `ImportModal.tsx` @ `platform/frontend/src/components/common/` | Reusable as-is for item master, opening stock and ASN import. The **backend** half is a mismatch — §2.5 |
| 1.8 | **Documents / object storage** | `documents` @ `V81:39`; `document_folders` (`:18`); `document_categories` (`:2`); `document_permissions` (`:75`); `ObjectStorageService`, `FileStorageService`, `FileSecurityService` @ `platform/…/service/` | Upload/download/permission machinery is complete and reusable. **Ownership is a mismatch** — §2.4 |
| 1.9 | **Notifications** | `notifications` @ `V319:13`; `notification_preferences` (`:95`); `notification_type_preferences` (`:137`); `NotificationDeliveryListener` @ `platform/…/listener/NotificationDeliveryListener.java:39` — `@TransactionalEventListener(phase = AFTER_COMMIT, fallbackExecution = true)` | Replenishment alerts, expiry warnings, count-overdue, blocked-move escalation. After-commit delivery is exactly right for a ledger: a notification never fires for a movement that rolled back |
| 1.10 | **Activity / audit telemetry** | `user_activity_logs` @ `V717:29`, fed by `UserActivityTrackingAspect`. Pointcut `within(ai..controller..*)` @ `:59`; module derived from **package segment 2**, uppercased, @ `:169-171` | Free write-auditing for every warehouse controller — **provided controllers live in `ai.<module>.controller…`**. Module names will render as `WAREHOUSEBASE`, `WAREHOUSE`, `WAREHOUSE3PL`, `WAREHOUSEINDIA`. It is telemetry, not the ledger's audit trail — §2.6 |
| 1.11 | **Global settings** | `global_settings` @ `V337:8`; `chk_global_setting_module` widened by `platform/…/V553:13-15` to include **`'WAREHOUSE'`** | **Free.** `module='WAREHOUSE'` is already allowed. V553's header (`:3-5`) credits a `V190035 (warehouse-core)` migration that does not exist in this checkout — a value left behind by a deleted module. Still emit the defensive merge migration of `MODULE-INTEGRATION.md` §10, because a later module's hardcoded DROP/ADD can discard it |
| 1.12 | **i18n** | `I18nConstants.SupportedLocales` @ `platform/…/constants/I18nConstants.java:28-33` → `en`, `hi`, `fr`; `platform/frontend/src/i18n/locales/{en,fr,hi}/` | Three locales from the first file, following `accounting-base` (R1 `C-050`). **RTL is absent platform-wide** — record it as a known limit (R5 `S-095`) |
| 1.13 | **Common component set** | Verified present: `DynamicDataTable.tsx`, `BaseFilter.tsx`, `ViewModalBase.tsx`, `SearchableSelect.tsx`, `ExportButton.tsx`, `ImportButton.tsx`, `ImportModal.tsx`, `HelpButton.tsx` — all in `platform/frontend/src/components/common/`; `lazyModal.ts` @ `platform/frontend/src/utils/`; `useUserBranches.ts` @ `platform/frontend/src/hooks/` | Every warehouse screen is built from these. `HelpButton` exists and **needs content** — R5 `S-094` |
| 1.14 | **Dark mode** | CLAUDE.md *DARK MODE (required on ALL UI)* token pairs | Applies unchanged. Non-negotiable on RF screens, which are used under warehouse lighting |

### 1.15 Three green-row facts not visible from the table

**(a) The `WAREHOUSE` global-settings value already exists because a warehouse module used to.**
`V553:3-5` names `V190035 (warehouse-core)`, which is absent from this checkout, and `platform/…/V528`
and `V663` still carry hardcoded `wms_*` / `scc_*` / `warehouse-*` permission exclusions from the same
deleted module. Those migrations have already run, so they grant a new module nothing — but they are
why D-3 forbids naming anything `wms_*` or `scc_*`. A `wms_`-prefixed permission would silently
inherit an exclusion nobody chose.

**(b) `dateOnly` is a distinct filter type and warehouse needs it everywhere.**
`platform/frontend/src/utils/filterUtils.ts:30` lists eight types; `:49-56` documents the difference:
`date` shifts to UTC day boundaries for `TIMESTAMP` columns, which *"moves the 'from' bound to the
previous calendar day for users east of UTC"*. `expiry_date`, `manufacture_date`, `count_date` and
`posting_date` are pure SQL `DATE` columns ⇒ **`dateOnly`**. Using `date` on them silently loses a
day of results for every Indian user (R1 `T-6`).

**(c) Filter-aware statistics must not be given a cache name.** `CacheConfiguration.java:190-196`
records the mistake by name (issues neetub1508/classic#790, #791): statistics computed from the same
search + filters as the rows are uncacheable under any key short of the full filter set, and the
`statistics.leave…` names that sat there *"cached nothing while reading as though leave statistics
were cached."* Warehouse's statistics strips are filter-aware by design ⇒ **register `dropdown.*`
names only** (R1 `C-043`).

---

## 2. EXISTS BUT SHAPE-MISMATCHES — the specific mismatch and what warehouse does about it

### 2.1 `branches` is not polymorphic, and branch codes are globally unique — **PD-1**

**The mismatch.** `V149` created `branches` with a comment at `:12` reading *"Owner information
(polymorphic - can belong to dealer, company, asset, etc.)"*, `owner_type VARCHAR(50) NOT NULL` +
`owner_id UUID NOT NULL` with **no FK** (`:13-14`), a `CHECK` admitting `'WAREHOUSE'` (`:63`), and
`UNIQUE (owner_type, owner_id, branch_code)` (`:60`).

**Eleven migrations later, all of that was removed.**
`platform/…/V160__Remove_owner_fields_from_branches.sql`:

```sql
-- :7   ALTER TABLE branches DROP CONSTRAINT IF EXISTS uk_branches_owner_code;
-- :10  DROP INDEX IF EXISTS idx_branches_owner;
-- :13  ALTER TABLE branches DROP COLUMN IF EXISTS owner_type;
-- :16  ALTER TABLE branches DROP COLUMN IF EXISTS owner_id;
-- :19  ALTER TABLE branches ADD CONSTRAINT uk_branches_code UNIQUE (branch_code);
-- :22  COMMENT ON TABLE branches IS 'Branch entities - branch_code is now globally unique without owner scoping';
```

Confirmed on the Java side: `platform/…/entity/Branches.java` declares no `ownerType` or `ownerId`
field, and its `@UniqueConstraint` at `:25` names `branch_code` alone.

**What warehouse must do.**

1. **Do not build anything on `branches.owner_type`.** There is no owner dimension on a branch to
   scope a warehouse site by. `chk_branches_type` (`V149:61`) survives and still admits `'WAREHOUSE'`
   and `'DISTRIBUTION_CENTER'`, so a warehouse site is a branch **by type**, not by owner.
2. **Branch codes are globally unique.** A warehouse site code shares a namespace with every dealer
   showroom and service centre in the same database. Warehouse's site-code generator must therefore
   check `branches.branch_code`, not just its own table — or, better, `whb_sites` carries its own
   code and references `branches.id` without duplicating the code.
3. **`warehouse-3pl`'s owner dimension is not `branches`.** D-5 already fixes this: `owner_id` lives
   on the movement and the position key, and a 3PL's clients are an owner dimension, not tenants
   (OD-3, R5 Fact 3). PD-1 removes the last argument for reaching for a branch owner column instead.
4. **`whb_locations` FKs `branches(id)`** and nothing else. That FK is on
   `WarehouseBaseCouplingTest`'s whitelist (`MODULE-INTEGRATION.md` §13.2 assertion 3).

**UNVERIFIED:** whether any live install still has the pre-`V160` columns (a database that never ran
`V160`, or a hand-applied schema). Settle with
`SELECT column_name FROM information_schema.columns WHERE table_name='branches' AND column_name IN ('owner_type','owner_id');`

### 2.2 GSTIN sits on `branches`, and it is per-state — right shape, easy to get wrong

`branches.gst_number VARCHAR(15)` @ `platform/…/V182__Add_financial_columns_to_branches.sql:7`, with
a partial index at `:18` and the comment at `:25`: *"GST registration number (format:
22AAAAA0000A1Z5)"*. The entity maps it at `Branches.java:113` (`gst_number`), plus `gst_name` (`:117`),
`pan_number` (`:122`) and `tan_number` (`:127`).

CLAUDE.md states the rule: *"GSTIN is per-state: stored on `branches` (platform), NOT on company.
PAN/CIN/TAN are per-legal-entity: stored on company."*

**Why this matters more for warehouse than for anything shipping today.** R5 §2.1 — a stock transfer
between two branches under **different GSTINs** is a taxable supply requiring a tax invoice and an
e-way bill; a transfer between two branches under the **same** GSTIN is not. The GSTIN comparison is
therefore a *branching condition in the transfer workflow*, not a display field.

**What warehouse does.** The transfer service reads `branches.gst_number` for source and destination
and branches on equality. `warehouse-india` owns the document generation; `warehouse` owns nothing
GST-specific (D-8). **`warehouse-base` must not learn what a GSTIN is** — it carries `company_id` on
the movement and nothing more.

### 2.3 Branch scoping is a per-module discipline, not a platform guarantee

**What exists.** `branch_staff` @ `platform/…/V150__create_branch_staff_table.sql:10` (`branch_id`,
`user_id`, `branch_role`, `is_primary_branch`, `assignment_end_date`). `BranchFilterService` @
`platform/…/service/common/BranchFilterService.java` supplies `resolveBranchFilter(userId)` (`:75`),
`resolveBranchAndHierarchyFilter(userId)` (`:97`), `toBranchIdsCsv(...)` (`:149`),
`getFilteredStatistics(...)` (`:179`), and the reusable SQL fragment at `:165-167`:

```java
"(CAST(:userBranchIds AS TEXT) IS NULL OR CAST(:userBranchIds AS TEXT) = '' " +
"OR %s.branch_id IN (SELECT CAST(UNNEST(STRING_TO_ARRAY(CAST(:userBranchIds AS TEXT), ',')) AS UUID)))"
```

Frontend counterpart: `useUserBranches` @ `platform/frontend/src/hooks/useUserBranches.ts`.

```bash
grep -rl "BranchFilterService" --include=*.java . | grep -v node_modules | wc -l   # → 251 files
```

**The mismatch.** Nothing enforces it. Row-level branch scoping is applied by each query that chooses
to apply it. Accessories does — `accessories/…/service/report/StockReportQueryService.java:67` calls
`BranchFilterService.toBranchIdsCsv(filter.getUserBranchIds())` and threads it through at `:79`,
`:100`. A query that forgets returns every branch's rows to every user, and no test catches it.

**What warehouse does.** Three things, and the third is the one that makes it stick:

1. Every `RepositoryCustomImpl` query takes `userBranchIds` and uses `BRANCH_FILTER_SQL`.
2. Note the empty-vs-null semantics — `StockReportQueryService.java:58-59` documents it: *"A non-null
   but EMPTY `userBranchIds` means the caller resolved to no branch access"*, which must return zero
   rows, **not** all rows. The SQL fragment above treats `''` as "no filter", so the **service** must
   short-circuit before the query. Getting this backwards is a data leak.
3. Add a rule to `warehouse-base`'s `ArchitectureInvariantsTest`: every native query in a
   `*RepositoryCustomImpl` that selects from a `whb_`/`wh_` table with a `branch_id` column must bind
   `:userBranchIds`. Empty baseline, so the first one that forgets fails the build.

### 2.4 `documents` has no polymorphic owner — every module builds its own link table

**The mismatch.** `documents` @ `V81:39` is owned by `folder_id` (`:50`), `category_id` (`:51`),
`owner_id` (`:64`) and `department_id` (`:65`). There is **no `entity_type`/`entity_id` pair**, so no
document can be attached to a business record generically.

Every module has therefore built its own link table: `accessory_stock_receipt_documents`,
`asset_documents`, and `acc_document_links` @ `accounting-base/…/V600110`.

**What warehouse does.** Own `whb_document_links` (GRN photos, damage certificates, packing
evidence, count sheets, hazmat declarations, customs documents).

**And change one thing from the accounting copy.** `V600110:100-105` sets the FK to `documents(id)`
as **`ON DELETE CASCADE`**, with a comment justifying it as *"matching every live platform/module link
table (`employee_documents` V133)"*. For a GRN photo or a damage certificate that is wrong: deleting
the file silently deletes the evidence that it ever existed. **Use `ON DELETE NO ACTION`** and let the
delete fail loudly, or add a `deleted_at` on the link. R1 `C-018` reaches the same conclusion.

### 2.5 There is no backend import framework — and warehouse needs the biggest importer in the suite

**The mismatch.** Every importer in this repo is bespoke: `platform/…/service/leave/LeaveBalanceImport*`
(9 classes), `accessories/…/StockReceiptBulkImportService`, and
`accounting-base/…/service/imports/AccImportHandlerRegistry`. The frontend half (`ImportButton`,
`ImportModal`) is reusable; the backend half is not.

**The best shape is accounting's, and it is recent.**
`AccImportHandlerRegistry.java:41-45` is a `List<AccImportHandler>` bean-collection registry with a
comment at `:26-29` that names the failure it prevents: *"Two handlers claiming one `import_type`
would make which one runs depend on bean ordering — and the symptom would be an import that silently
created the wrong kind of record. That is caught here, at startup, not by a reviewer."* It is paired
with `acc_import_batches` / `acc_import_batch_rows` (`V600120`) and a **reversal path**
(`AccImportBatchReverseModal.tsx`).

**What warehouse does.** Copy that whole shape into `warehouse-base` — `whb_import_batches`,
`whb_import_batch_rows`, `List<WhImportHandler>`, and the reverse modal. **Do not copy the leave
importer.** Then extend it for what warehouse specifically needs and accounting did not (R5 `S-079`,
`S-080`):

- opening stock at **200k–1M rows**, carrying position **and value and layers and lot and serial and
  owner and duty status**;
- a **dry run** with an error report and a **closing-stock-value tie-out against the source**, before
  apply (accounting's `P2-15` shape);
- mapping profiles for Tally / Busy / Marg / Excel, **exportable and importable**, because
  one-database-per-customer means the second customer is a different database;
- duplicate-SKU resolution and unit-mismatch validation (`PCS` vs `NOS` vs `EA` is the failure every
  time).

Owner: **P1** (masters, identity, inbound). It is a v1 ship-blocker — a warehouse product that cannot
load opening stock cannot be installed.

### 2.6 The audit trail is telemetry, not evidence

**The mismatch.** Two independent trails exist and neither is an audit trail for a statutory stock
ledger:

- `PlatformLogger.audit(...)` → the log stream only. Nothing queryable.
- `user_activity_logs` @ `V717:29`, fed by `UserActivityTrackingAspect`. It is **asynchronous,
  out-of-transaction, and swallows its own exceptions** — `accounting-base/V600111:23-30` states this
  explicitly as the reason it built its own.

**What warehouse does.** L-2 and R5 `S-083` already require it: the ledger's immutability evidence
lives in the ledger, not in a side table. `accounting-base/…/V600111` is the template — §4.4.

`user_activity_logs` stays useful for "who opened which screen", and it is free provided controllers
sit in `ai.<module>.controller…` (`UserActivityTrackingAspect.java:59`, `:169-171`).

### 2.7 `all_activity_history` is dealer-owned — stay out of it

The unified activity feed view is created and redefined **inside the dealer module**:
`dealer/…/V20412__create_pdi_and_business_activity_history.sql`,
`dealer/…/V20413__alter_activity_history_event_metadata_to_text.sql`,
`dealer/…/V20885__drop_user_role_from_activity_history.sql`. Accessories deliberately declined to
join it (`accessories/V30379:7-9`).

Joining or redefining it from a warehouse migration would make `warehouse-base` undeployable without
dealer — a direct D-1 violation. **Own `whb_activity_history` standalone**, as accessories did
(R1 `C-048`, `T-14`).

### 2.8 No shared party/supplier master — `warehouse-base` owns its own

R1 §7, re-verified. The candidates and why each fails:

| Candidate | Where | Why it does not work |
|---|---|---|
| `asset_vendors` | `assets/…/V60056:3-38` — a real vendor master with `code UNIQUE`, `ck_asset_vendors_type CHECK (vendor_type IN ('MANUFACTURER','RESELLER','SERVICE_PROVIDER','LEASING_COMPANY','INSURANCE_PROVIDER','OTHER'))` (`:34`), contacts, `tax_id`, payment terms, credit limit, currency | **Right shape, wrong owner.** It is in `assets`, a vertical. `warehouse-base → assets` inverts the arrows |
| `customers` / `customer_individuals` / `customer_companies` | `automotive/V10010:9`, `V10011:10,57` | Models buyers, and `automotive` is a vertical |
| `companies` | `automotive/V10002:11` | Legal-entity / OEM master, automotive-owned |
| accessories receiving | `accessories/…/dto/request/inventory/StockReceiptRequest.java:23-51` | **No supplier field exists at all** — 10 fields, none a vendor (R1 `C-031`) |

**The precedent that does work:** when a base module needs a party, it creates its own —
`acc_companies` @ `accounting-base/V600001`, paired in the same migration with an `external_refs`
table for exactly this mapping.

**What warehouse does.** `warehouse-base` owns `whb_counterparties` (supplier / customer / carrier /
3PL client, one table with a role flag) plus `whb_counterparty_external_refs`. Adapters carry the FK
to the vertical's party — `warehouse-adapter-dealer` maps to an automotive `companies` row, a future
`warehouse-adapter-assets` maps to an `asset_vendors` row. **The adapter carries the FK; the base
never does** (OD-4, R7 §3.3, and the previous attempt at this seam died of exactly the opposite — 84
FK references from warehouse into `scc_*`, several to tables that never existed).

### 2.9 No number series at platform level, and the platform generator is not gapless

**What exists.** `platform/…/util/SequentialCodeGenerator.java`. Its own javadoc (`:11-17`) explains
that the next sequence is derived from *codes already issued*, and `generate()` (`:40-53`) ends with:

```java
// Defensive check: covers rows the prefix lookup could not match and concurrent inserts
while (existsCheck.test(code)) { sequence++; code = format(basePrefix, padding, sequence); }
```

It is a scan-then-retry behind a unique constraint. **Explicitly not gapless, and racy.**

**The gapless precedent is per-module**, in assets: 8 `*_sequences` repositories with
`@Lock(LockModeType.PESSIMISTIC_WRITE)` on a `next_value` counter row (PD-4).
`AssetTagSequenceRepository.java:19-27` names the exact race: *"two concurrent asset creations in one
category read the same value and one of them fails on `uk_assets_tag` after the counter has already
moved. Only the generator needs this — it runs in its own short `REQUIRES_NEW` transaction."*

**What warehouse does.** `warehouse-base` owns `whb_number_series`, scoped by `owning_module` so an
adapter can take a number without touching base tables (R7 `A13`, `G-044`), with a
`PESSIMISTIC_WRITE`-locked counter row in a `REQUIRES_NEW` transaction. **Never `SequentialCodeGenerator`
for a GRN, pick, ship, adjustment or challan number** — a statutory document series with gaps is a
finding, and a duplicate is worse (R1 `C-019`).

### 2.10 No approval framework — five implementations, no generic one

`leave_approval_config` (platform V755), `service_approval_configs`,
`accessory_delivery_approval_config`, `asset_transfer_approval_configs`, and accounting's **port**:
`accounting-base/…/service/approval/AccApprovalGate.java` + `PermissionOnlyAccApprovalGate.java`
(the directory also holds `AccApprovalDecision`, `AccApprovalRequestContext`, `AccApprovalSubjects`).

**What warehouse does.** Warehouse needs approval on write-offs, negative adjustments, count-variance
posting above a threshold, period reopen and forced blocked-moves. Copy the **`AccApprovalGate` seam
shape** — interface + default implementation + a documented `@Primary` upgrade path — not any of the
four concrete configs.

**One caveat, and it is the difference between the two seams warehouse needs.** `AccApprovalGate` is
a **single-implementation** seam (`@Primary` admits exactly one). The **inbound movement port is
not** — it must be a `List<T>` bean-collection registry so every adapter registers alongside every
other. The three live precedents for the multi-implementation shape:
`ExportService(List<ExportFormatHandler>)` @ `platform/…/service/export/ExportService.java:31`;
`BoomBarrierWebhookController(List<IBoomBarrierHandler>)` @
`automotive/…/controller/BoomBarrierWebhookController.java:44-48`; and
`AccImportHandlerRegistry(List<AccImportHandler>)` @ `:41-45`. **Use `List<T>` for the port, `@Primary`
for approval** (R1 `C-039`).

### 2.11 No decimal library on the frontend — all arithmetic is backend `BigDecimal`

```bash
ls */frontend/package.json | wc -l        # → 1
```

Only `platform/frontend/package.json` exists. **A module cannot add an npm dependency**, and the
platform manifest carries no `decimal.js` / `big.js` / `bignumber.js`. Every quantity, cost and
valuation number in a browser is an IEEE-754 double.

**What warehouse does.** Compute **every** quantity, conversion, cost, layer consumption and valuation
on the backend in `BigDecimal` and send **formatted strings**. The frontend renders; it never
arithmetics. This is also CLAUDE.md's *"Frontend is DISPLAY ONLY"* rule, but for warehouse it is a
correctness requirement, not a style one: a UoM conversion done in a double is a stock discrepancy
(R1 `C-013`, `T-13`).

Related, and it belongs to OD-7: `currencies` @ `platform/…/V203:5` has
`default_decimal_places INT NOT NULL DEFAULT 2` with `CHECK (default_decimal_places >= 0 AND <= 4)`
(`:17`). A per-unit cost at `DECIMAL(19,6)` is storable but **not displayable** through that setting.
Decide the display rule with OD-7, not after.

### 2.12 No exchange-rate source

```bash
grep -rln "exchange_rate\|currency_rate\|fx_rate" --include=*.sql . | grep -v node_modules | grep -v target
```

→ **0 files.** `currencies` (`V203:5-18`) carries `currency_code`, `currency_name`, `currency_symbol`,
`default_decimal_places`, `is_active`, `is_default`, `sort_order` — and **no rate column of any kind**.

**What warehouse does.** Valuation in a second currency has no rate source. Two honest options:
(a) v1 values stock in the install's single default currency only, and says so; (b) landed cost with
a foreign-currency purchase carries the rate **on the movement line**, frozen — which is the same
discipline L-7 applies to UoM conversion factors and is the correct answer regardless. **Do not build
a rates table in `warehouse-base`** without deciding whether accounting owns it (D-6 gives accounting
value; a rate is value).

### 2.13 Mobile: text filters yes, **date filters no** — and `EntityListScreen` is the wrong base for RF

**CLAUDE.md is stale here and D-13 already records it.** `mobile/src/components/common/ListHeader.tsx:210-230`
defines `AdditionalFilterConfig` with **`type?: 'dropdown' | 'text'`** (`:216`), `options` for
dropdowns (`:218`), and `placeholder` for text (`:230`). CLAUDE.md's *"`additionalFilters` prop only
supports dropdowns"* is out of date (R1 `CM-1`, `C-044`).

**What is still true, and it matters:** there is **no date filter type**. Warehouse mobile screens
that need an expiry-date range, a count-date range or a posting-date range require changes to
`EntityListScreen`/`ListHeader` themselves. Budget that work in the mobile task, do not discover it.

**And a larger mismatch, from R5 `S-088`.** The RF screens a warehouse actually needs are
*one-handed, gloved, scanner-triggered, no free typing*. `EntityListScreen` is a list-plus-filters
component built for office use. **A dedicated RF screen family is required** — that is a warehouse
deliverable (phase P3, v1.1), not a platform gap, and it does not remove the D-13 obligation that
every web capability has a mobile counterpart in the same task.

### 2.14 Two platform CHECK constraints, one of which rejects warehouse today

Full treatment, including the merge idiom and the out-of-order re-assertion hazard, is in
[`MODULE-INTEGRATION.md`](MODULE-INTEGRATION.md) §10. In one line each:

- `global_settings.chk_global_setting_module` — **`'WAREHOUSE'` already allowed** (`V553:14-15`). Free.
- `widget_definitions.chk_module` — **`'warehouse'` NOT allowed**; latest assertion is
  `V557:16-18` = `('platform','dealer','shared','accessories','assets','insurance','services')`. The
  first warehouse dashboard widget insert fails with `23514`. One merge migration in the
  `warehouse-base` band, copying `accounting-base/V600200`, fixes it.

---

## 3. DOES NOT EXIST — BLOCKS SHIPPING

Six capabilities that do not exist anywhere in this repository and that a warehouse product cannot
ship without. Each row: the grep that proves absence, the cost, the owning phase, and **platform or
warehouse**.

R5 opens §5 with the sentence the whole section follows from: *"An accounting package that is down
for an hour is an inconvenience; a WMS that is down for an hour has forty people standing in an aisle,
and goods that moved anyway."*

### 3.1 No restore path — `S-082` · **platform** · v1

```bash
grep -c -i "restore" platform/backend/src/main/java/ai/platform/service/DatabaseBackupService.java   # → 0
```

`DatabaseBackupService` runs `pg_dump` (`:299`, `:314`), enforces a retention window
(`:92`, `:109`), cleans up expired backups (`:355`), lists history (`:386`) and issues download URLs
(`:395`). **There is no restore method, no WAL archiving, no PITR, no restore-verification job, and no
stated RPO/RTO.**

**Why it blocks warehouse specifically.** For an accounting package this is an availability risk. For
a **statutory stock ledger** it is a *records* risk: the Rule 56 stock account and the 3CD clause-35
quantitative statement must be reproducible for the full retention period (R5 `S-083`, `S-051`), and
an unrestorable backup does not satisfy that.

**Cost and owner.** Platform work — a restore path, WAL archiving, a scheduled restore-verification
job, and written RPO/RTO. It does not compete with warehouse engineers, which is precisely why it
must be filed as a platform task **now** rather than assumed.

### 3.2 No label rendering anywhere — `S-087` · **warehouse-base** · v1

```bash
grep -ril "zpl\|escpos\|dymo" --include=*.java --include=*.ts --include=*.tsx . | grep -v node_modules | wc -l   # → 0
```

**Zero.** There is no label rendering of any kind in this codebase — the prior WMS art has a
`wms_label_templates` table with no engine behind it.

**Why it blocks.** A warehouse without labels is not a warehouse. An operator with a pallet cannot use
a browser download dialog.

**What must be built** (R5 §5.7): **ZPL** as the primary target (EPL/TSPL for cheaper units, PDF for
laser); **direct-to-printer from the handheld** over the network; a **printer registry** — printer per
zone/dock, default label size, DPI (203 vs 300 changes every barcode's width), media type; a **print
job log with reprints flagged**, because a reprinted SSCC is a duplicate licence plate in the wild and
is exactly how two pallets end up with the same ID; and eleven label/document kinds — item/shelf,
LPN/pallet (SSCC, GS1-128), carton, shipping, location, GRN, pick list, packing slip, delivery
challan, e-way bill print, hazmat class label.

**Owner: `warehouse-base`, phase P0/P1.** It cannot be platform work — nothing else in the suite has
a use for it, and the label content is warehouse's domain. The **printer registry and the print-job
log are v1 schema even if the render engine is v1.1**: a reprint that was never recorded cannot be
reconstructed.

### 3.3 No offline mutation queue in mobile — `S-086` · **warehouse-base + mobile** · v1.1

```bash
grep -ril "persistQueryClient\|createAsyncStoragePersister\|offlineQueue" mobile/src | wc -l   # → 0
```

**Zero.** `mobile/src/contexts/NetworkContext.tsx` reports `isConnected` and nothing queues behind it.

**Why it blocks.** Metal racking, cold rooms and dead spots. A receiving dock has a truck waiting.
Three levels, one chosen per screen (R5 §5.6): **read-cached** (putaway/pick lists), **queued write**
(counting, receiving, picking), **true offline** (rarely needed — do not promise it).

**The part that is irreversible and therefore v1 schema, not v1.1:** the **idempotency key per scan**.
Replayed scans without one produce duplicate ledger rows, and a duplicate in an append-only ledger can
only be fixed by a reversal that looks like an adjustment. L-9 already requires
`(source_system, idempotency_key)` unique with the key **never** server-generated — that invariant is
what makes the offline queue buildable later. Ship the constraint in v1; ship the queue in v1.1.

### 3.4 No outbox, anywhere — **warehouse-base** · v1 (schema) / v2 (delivery)

```bash
grep -ril "outbox" --include=*.java --include=*.sql . | grep -v node_modules | wc -l   # → 0
```

**Zero.** There is no transactional-outbox pattern in this repository. Cross-module effects are
in-process: `@TransactionalEventListener(AFTER_COMMIT)` (`NotificationDeliveryListener.java:39`) and
direct service calls.

**Why warehouse needs one and accounting did not.** D-6 requires a **hand-over envelope** per
posting-relevant event, carrying `handover_id` + `posting_status (NOT_APPLICABLE | PENDING | POSTED |
REJECTED)` on the movement, so that *"does the stock ledger tie to the GL"* is answerable. R7 `A10`
additionally allows an adapter to subscribe over HTTP through `whb_outbox_subscriptions`. An
after-commit in-process listener cannot do either: it has no durability, no retry, no ordering and no
"stuck in PENDING" query.

**Owner: `warehouse-base`.** The **columns are v1** (R5's irreversible list item 12: pre-integration
movements have no marker, so the question is permanently unanswerable for the period the first audit
covers). The delivery machinery — dispatcher, retry, dead-letter, subscription rows — is v1.1/v2.

### 3.5 No tenancy — RESOLVED as one database per customer, and it is load-bearing

```bash
grep -ril "tenant" platform/backend/src/main/java | wc -l   # → 0
```

**Zero files.** Classic is **one database per customer**. This is not a gap to close; it is a fact
that shapes `warehouse-3pl`.

**What follows** (OD-3, R5 Fact 3, D-5): a 3PL's clients are **not** tenants. They are an **owner
dimension inside one database** — `owner_id` `NOT NULL` on every movement and in the position key, in
**v1**, in every install, even though `warehouse-3pl` ships in v2. There is no rule that recovers
whose a unit was, so the column is free now and **unbackfillable later**.

Two operational consequences that follow from one-DB-per-customer and are easy to miss:

- **The second customer is a different database.** So every mapping profile, import template, label
  template and reason-code catalogue must be **exportable and importable** (R5 `S-080`), or every
  install is hand-built.
- **`platform/…/db/client/<client>/` version numbers are deliberately reused across clients**
  (`V910001__` exists five times) because only one client directory is ever a Flyway location. That
  is why `V910000+` is unusable for warehouse and why D-2 moved the bands.

**No decision needed. Do not re-litigate it.** Deadline for confirming: before `warehouse-3pl` (P5)
starts.

### 3.6 No support impersonation — `S-092` · **platform (schema) + warehouse** · v1 schema

**PD-3** corrects R5's grep: `grep -ril "impersonat"` now returns **5 files**, all in `accounting-base`,
and all of them are the *audit schema* anticipating impersonation —
`accounting-base/…/service/audit/AccAuditActorKind.java:17` defines an actor kind for *"A support
operator acting inside an impersonation grant … BOTH identities are"* recorded.

**There is still no impersonation feature.** No consent flow, no time-box, no session mechanism, no UI.

**What warehouse must do in v1, even without the feature:** carry `on_behalf_of_actor_id` on the
movement and on the ledger's own audit event **from the first migration**. Adding it in year two
leaves year one unable to answer "was this posted by the user or by support acting as them" — and year
one is what the first audit covers. `accounting-base`'s `AccAuditActorKind` is the shape to copy.

The feature itself is platform work. Filing it is not optional: R5 ranks it a day-one ship-blocker for
a product whose support model is "we log in and look".

### 3.7 Summary — which of these stop a first customer

| Gap | Ship-blocker for the **first real customer**? | Lands in | Phase |
|---|---|---|---|
| Restore path (`S-082`) | **Yes** — statutory records risk | platform | v1 |
| Label rendering (`S-087`) | **Yes** — no labels, no warehouse | `warehouse-base` | v1 |
| Offline queue (`S-086`) | Idempotency key **yes** (v1 schema); the queue itself v1.1 | base + mobile | v1 / v1.1 |
| Outbox (`handover_id`, `posting_status`) | Columns **yes** (v1); delivery v1.1 | `warehouse-base` | v1 / v1.1 |
| Tenancy | No — **resolved**, one DB per customer; `owner_id` in v1 covers 3PL | — | — |
| Impersonation (`S-092`) | Column **yes** (v1 schema); feature is platform's | platform + base | v1 |

---

## 4. Concurrency toolkit — what exists, what is reusable, what warehouse invents

A stock ledger is the most concurrency-sensitive thing this suite has ever contained. R1 §9 surveyed
what exists; this section adds the verdict warehouse needs: **reuse / re-implement / extract to
platform**.

### 4.1 The state of the art in this repo, and why it is not enough

`accessories` is the only quantity-based inventory here, and it has **no concurrency control on
stock at all** (R1 `C-024`): `StockLevel` has no `@Version`, `StockLevelRepository` declares no
`@Lock`, and no migration puts a `CHECK (quantity_on_hand >= 0)` on any balance column. The negative
guard is a Java read-compare-write, and the code comment at
`accessories/…/InventoryStockAdjustmentService.java:63-72` **names the race and does not defend
against it**. Two concurrent issues both read the same on-hand, both pass, one deduction is lost.

Warehouse cannot inherit any of it. Everything below is built fresh, from precedent.

### 4.2 `@Version` optimistic locking — **reuse, idiomatic**

```bash
grep -rln "@Version" --include=*.java . | grep -v node_modules | wc -l   # → 34 files
```

Live in accessories (`Quotation`, `QuotationRevision`, `AccessoryProductDiscount`, `QuotationStatus`),
platform (`LeaveBalance`), and 10 dealer + 6 automotive entities. **Never used on a stock or balance
row.**

**Verdict: reuse.** `@Version` on `whb_stock_positions` — but it is the *weakest* of the three guards
L-6 requires, and on its own it is insufficient: R5 `S-085` shows why. Under a **generated**
`quantity_available` column, two concurrent allocations both read `available = 5`, both write, and
`CHECK (quantity_on_hand >= 0)` **does not fire** because on-hand did not change. Optimistic locking
catches the lost update only if both transactions touch the same row version — which they do for a
position, but not for a reservation-ledger insert.

### 4.3 `@Lock(PESSIMISTIC_WRITE)` on a counter row — **reuse verbatim**

Eleven files (PD-4): `platform/…/LeaveRequestRepository.java:29`, `LeaveBalanceRepository.java:27`,
and the **8** assets `*_sequences` repositories plus `AssetRepository`. The documented idiom is
`AssetTagSequenceRepository.java:19-27` (§2.9).

**Verdict: reuse verbatim** for `whb_number_series`. The cost is stated in the precedent and must be
carried into the design: a `REQUIRES_NEW`, very short transaction, or every document creation in one
series serialises for the life of the outer transaction.

### 4.4 PostgreSQL advisory locks — **reuse, and the right tool for the ledger**

Three sites, all the same shape (`SELECT pg_advisory_xact_lock(hashtext(:key))` via
`entityManager.createNativeQuery`):

- `platform/…/service/DocumentFolderService.java:266`
- `platform/…/service/GridPreferenceService.java:144`
- `services/…/service/BoomBarrierWebhookService.java:146`

**Verdict: reuse — and this is the right primitive for "serialise all movements for (item, location,
owner, lot, duty_status)"**, because there is no single row to lock when the first movement for a key
is being created. Note the transactional variant (`_xact_`) releases at commit; use it, never the
session variant.

### 4.5 `FOR UPDATE SKIP LOCKED` — **warehouse introduces it**

```bash
grep -rin "SKIP LOCKED" --include=*.java --include=*.sql . | grep -v node_modules | wc -l   # → 0
```

**Zero precedent.** Warehouse needs it for wave/pick-task claiming: N handhelds pulling the next task
from one queue without blocking each other.

**Verdict: re-implement (net-new).** Flag it as a new primitive in the design and write the DBA note
that goes with it: `SKIP LOCKED` silently returns fewer rows than requested, so a task-claim query
that asks for 1 and gets 0 means "all claimed", not "queue empty".

### 4.6 `CREATE CONSTRAINT TRIGGER … DEFERRABLE INITIALLY DEFERRED` — **exactly one precedent, and it is the template**

```bash
grep -rln "CREATE CONSTRAINT TRIGGER" --include=*.sql . | grep -v node_modules | grep -v target
```

→ **one file**:
`accounting-base/backend/src/main/resources/db/migration/V600111__Create_acc_audit_events_and_the_append_only_hash_chain.sql`
(`:812-815`, `:838-841`). The file says so itself at `:773-775`: *"THIS REPOSITORY HAS NO PRECEDENT FOR
`CREATE CONSTRAINT TRIGGER`. 109 migration files use plain `CREATE TRIGGER`; the count of
`CREATE CONSTRAINT TRIGGER` across the whole repository is ZERO."*

**Verdict: reuse — it is the mechanism for L-1.** "A movement's lines sum to zero at COMMIT" cannot be
a row trigger, because the second line does not exist when the first is inserted. Two PostgreSQL rules
the precedent records and warehouse must honour: a constraint trigger must be **`AFTER`**, and must be
**`FOR EACH ROW`**.

### 4.7 Append-only enforced in the database — **reuse the three-layer structure**

`accounting-base/V600111` is the best template in the repo for `whb_stock_movements`:

- a **BEFORE UPDATE OR DELETE reject trigger** on the append-only table;
- a head row created-or-locked with `INSERT … ON CONFLICT DO UPDATE … RETURNING` (`:673-690`) —
  the atomic get-or-create-and-lock idiom;
- sequence-must-be-head+1;
- a hash recomputed **in SQL** and cross-checked against the Java writer;
- a verifier that names the break — *"the break between events 59 and 61"*;
- and the cost stated honestly at `:364-386`, `:673-676`: *"from its first audit write to COMMIT, a
  mutating transaction holds this row's lock, so mutating transactions for ONE COMPANY serialise."*

**Verdict: reuse the structure — service exposes `append()` only, controller exposes `GET` only, the
database rejects `UPDATE`/`DELETE` (L-2's three layers).** Warehouse probably does **not** need the
hash chain, and it definitely **cannot afford the per-company serialisation**: a 1M-rows/day ledger
(R5 §5.4) cannot funnel every movement through one locked head row. Take the three layers, drop the
chain, and lock at the position key instead (§4.4).

### 4.8 Balance derived from an append-only table — **one good precedent, and it is dealer's**

`pdi_storage_slot_assignments` @ `dealer/V20735:8` is the best occupancy model in the repo:
append-only (released rows keep `released_at` and stay forever), exclusivity by **partial unique
index** (`uk_slot_active_index` `:57-59`, `uk_slot_active_vehicle` `:62-64`), and occupancy **derived
at read time, deliberately not cached** — `PdiYardStorageLocationService.java:67` and
`PdiStockYardMapper.java:83,118` both say so in comments.

**Verdict: reuse the shape** for `whb_location_occupancy` and for every "one active X" invariant
(one active reservation per line, one active putaway task per LPN).

**One inherited obligation:** a partial unique index **cannot** be declared `DEFERRABLE` in
PostgreSQL. Four files record this in the negative — `accounting-base/V600001:150`, `V600004:111`,
`V600120:90`, `insurance-360/V120175:35`, `V120180:41` — and each names the consequence: **the write
path owes an explicit `flush()`**.

### 4.9 Balance-cache-with-rebuild — **warehouse invents it. Budget it.**

**Zero precedents.** `accessory_stock_levels` is a cache with **no rebuild path**;
`pdi_yard_storage_locations.current_occupancy` is a column deliberately left unmaintained.

L-4 requires that a full rebuild from `whb_stock_movements` reproduces every `whb_stock_positions`
row **exactly**, that a nightly job proves it, and that drift alerts.

**Verdict: re-implement (net-new), and budget all four parts:** the rebuild query, the scheduled
reconciliation job, the variance report, and the operational runbook for what to do when it drifts.
This is the single largest piece of net-new correctness machinery in the product, and it is what
separates warehouse from accessories (D-4, R1 `C-021`).

### 4.10 The multi-implementation port — **reuse; the shape is settled**

`List<T>` bean-collection registry, three live precedents (§2.10). **Not `@Primary`**, which admits
exactly one implementation and would make the second adapter impossible.

### 4.11 Should any of this be extracted to `platform`?

| Mechanism | Extract? | Why |
|---|---|---|
| Gapless number series | **Eventually, yes — but not now.** | Nine implementations exist (8 assets sequences + `SequentialCodeGenerator`). A platform `NumberSeriesService` would serve all of them. But extracting it means editing assets, and D-11's ratchet is about `warehouse-base`, not about restraint on platform. **Recommendation:** `warehouse-base` owns `whb_number_series` in v1; file a separate platform task to extract, and do not block warehouse on it |
| Advisory-lock helper | **No.** | Three call sites, four lines each. A helper would hide the transactional-vs-session distinction, which is the only thing that can go wrong |
| Append-only trigger generator | **No.** | Two consumers (accounting, warehouse) with materially different needs (hash chain vs conservation). Two copies with a comment cross-referencing each other is more honest than one abstraction |
| Balance-cache-with-rebuild | **No, not yet.** | One consumer. Extract when a second appears — which, per D-9, will not be accessories |
| Branch-scope enforcement | **Yes, worth proposing.** | 251 files call `BranchFilterService` and every one of them can forget (§2.3). A platform-level `@BranchScoped` aspect or a repository base class would close a whole class of data leaks across the suite. File as a platform task; **warehouse does not wait for it** — it ships its own architecture rule instead |

---

## 5. Performance and scale reality

None of the platform's data-access stack was designed for a stock ledger. R5 §5.4 sets targets;
this section says where the platform breaks first.

### 5.1 The targets warehouse must design against (R5 §5.4, `S-084`)

| Dimension | Target |
|---|---|
| Stock ledger rows | **1M/day peak** for a large 3PL; 20k/day for a dealer parts department |
| Position table | ≤ 5M live rows — **the unique key is the hot spot**; every extra grain column multiplies it |
| Scan-to-response | **< 300 ms** at the handheld, or the operator works ahead of the system |
| Allocation | **200 order lines/second** with no oversell |
| Count sheet | 5 000 lines in one count, 10 counters concurrently |
| Pick list generation | a 500-line wave in **< 5 s** |
| Export | **100k-row stock report** without holding a transaction open |

For scale: the largest existing module by migration count is `dealer` at 736 migrations, and the
largest *inventory* implementation in the repo is accessories' 17 tables — whose movement log
(`accessory_inventory_transactions`) is a single-sided log, not a ledger. **A warehouse stock ledger
writes more rows than any table in this suite has ever held.**

### 5.2 Where the platform breaks first — pagination

`ApplicationConstants.MAX_PAGE_SIZE = 100` (`platform/…/constants/ApplicationConstants.java:64`),
`DEFAULT_PAGE_SIZE = 10` (`:62`), clamped in `PaginationService` at `:174-176`.

**Verdict: FITS, and it is the right constraint.** The correct answer for a 5M-row position table is
never "raise the page size"; it is DB-level `LIMIT`/`OFFSET` (CLAUDE.md *SQL Pagination Flow*) with
`SqlSortBuilder` whitelists.

**The real risk is `OFFSET` depth.** `OFFSET 200000` scans and discards 200 000 rows. Warehouse grids
over the movement ledger will hit this long before any other module does. **Design decision required
before P2:** keyset ("seek") pagination for the ledger grid, or an enforced date-range filter that
bounds the result set. Neither exists in the platform stack today, so this is a warehouse-owned
addition either way.

### 5.3 Where the platform breaks first — export

`BaseExportService.DEFAULT_MAX_EXPORT_ROWS = 10_000` (`:48`), overridable per screen via
`maxExportRows()` (`:61-64`).

**Verdict: MISMATCH against R5's 100k target.** Three separate problems, and raising the constant
solves only the first:

1. **The ceiling.** 10 000 rows is a tenth of the target. Overriding `maxExportRows()` is one line,
   and `:61` explicitly invites it — *"Override to raise it for a specific screen"*.
2. **The transaction.** The repo's known export failure mode is holding a transaction open for the
   duration (memory: *"Export transactional"*). A 100k-row stock report that materialises to a
   `List` inside a read transaction holds a snapshot while forty operators are posting movements.
   **Warehouse's ledger export must stream** — cursor/`Stream<T>` with a fetch size, written directly
   to the output — which is a shape `BaseExportService` does not currently offer.
3. **Excel cell styles.** `:801` and `:818` record the 64k cell-style limit and the "create the style
   ONCE" discipline that keeps a large export from blowing past it. Any warehouse export service that
   adds a per-cell style will fail at scale, not in dev.

Two related, already-known export facts that apply unchanged: exports **ignore grid filters and grid
sort** on ~50 endpoints today (a long-standing repo defect — do not copy the pattern), and CSV needs
the UTF-8 BOM, which `BaseExportService` supplies at `:59`.

### 5.4 Where the platform breaks first — statistics

Every management grid in this suite ships a statistics strip computed over the whole filtered set. On
a 5M-row position table with a 100M-row movement ledger, a `COUNT(*)`-per-card query is a full scan
per page load.

**Verdict: MISMATCH, and it is warehouse's to solve.** Caching is not available (§1.15(c) — the
strips are filter-aware). Options, to be decided before P2: pre-aggregated rollup tables refreshed by
the same reconciliation job that proves L-4; approximate counts for the unfiltered case; or accepting
a slower strip behind an explicit "compute" action. **Do not** register a `statistics.*` cache name —
that is the mistake `CacheConfiguration.java:190-196` already records.

### 5.5 Where the platform breaks first — grid config volume

Every warehouse grid needs rows in `grid_column_definitions`, `filter_definitions`,
`grid_preferences.default_columns` and `grid_preferences.default_filters`, **plus** a
`COMMON_FILTER_CONFIGS` scope in a TypeScript `const` (211 scopes today) **plus** cache names in a
Java `Arrays.asList` (230 today). None of these has a per-module extension point.

**Verdict: FITS functionally, MISMATCHES operationally.** A product with ~40 grids adds ~40 scopes and
~80 cache names to two platform files. That is not a defect — it is the honest statement D-10's
corollary makes and that `MODULE-INTEGRATION.md` §12.3 repeats: **the ratchet is on `warehouse-base`,
never on `platform`.**

### 5.6 Archival — required, and it must not break "as at" reproduction

R5 `S-096`: a 1M-rows/day ledger needs a stated partition/archive strategy **at design time**, and it
must not break the "stock ledger as at a date, reproducible" requirement (`S-083`) or the statutory
retention clocks (`S-051`).

**Nothing in this repo partitions any table.** **UNVERIFIED** — settle with
`SELECT relname FROM pg_class WHERE relkind = 'p';` on any install. Warehouse should assume no
precedent and design PostgreSQL declarative range partitioning on `posting_date` for
`whb_stock_movements`, with the partition key chosen **before the first row is written** (a
partition key cannot be added to a populated table without a full rewrite).

---

## 6. Decision deadlines

Every row here blocks a phase. The deadline is the point after which the decision becomes expensive
or impossible.

| # | Decision | Blocks | Deadline | Recommendation |
|---|---|---|---|---|
| **PD-D1** | **Does `enable.warehouse.3pl` relaxed-bind inside a `@ConditionalOnExpression`?** `@ConditionalOnProperty` with a digit segment is proven (`Insurance360ModuleConfig.java:29-33`); the combination is not | Every module's activation | **P0 bootstrap**, before any module config is written | Boot once with the flag and grep the log. Fallback is `@Conditional(AnyNestedCondition)` with per-flag `@ConditionalOnProperty`. Do **not** rename the module |
| **PD-D2** | **Ledger grid pagination:** keyset/seek, or an enforced bounding filter? | The movement grid and its export | **Before P2** (outbound, reports) | Enforced date-range filter in v1 (cheap, honest); keyset in v1.1. `OFFSET` depth is not survivable at 100M rows |
| **PD-D3** | **Streaming export.** `BaseExportService` materialises; the target is 100k rows | Every warehouse report | **Before P2** | Add a streaming path in `warehouse-base` rather than editing `BaseExportService`; propose the platform extraction separately |
| **PD-D4** | **Statistics strategy** for filter-aware strips over ledger-sized tables | Every warehouse grid | **Before P2** | Rollup tables maintained by the same job that proves L-4. Decide with the L-4 reconciliation design, not after |
| **PD-D5** | **Partition key** on `whb_stock_movements` | The ledger table's DDL | **Before P0 writes the first migration** — a partition key cannot be added to a populated table without a rewrite | Declarative range partition on `posting_date`. Even if partitions are created lazily, the table must be declared partitioned from day one |
| **PD-D6** | **`ON DELETE` on `whb_document_links`** — `CASCADE` (accounting's choice) or `NO ACTION` | Evidence retention | **Before P1** (documents) | `NO ACTION`. A GRN photo that vanishes with the file is not evidence |
| **PD-D7** | **Restore path** — is it filed as a platform task, or is warehouse shipping without one? | First customer go-live | **Before the first pilot install** | File it as platform work now. It does not compete with warehouse engineers, and a statutory ledger with no restore is not sellable |
| **PD-D8** | **Which precision set** (OD-7) — and its interaction with `currencies.default_decimal_places CHECK (<= 4)` (`V203:17`) | Every numeric column in the ledger | **Before P0-02** | Adopt accounting's resolved set verbatim, including the corrected `DECIMAL(9,6)` for percentages, and state the display rule for a `DECIMAL(19,6)` per-unit cost |
| **PD-D9** | **Mobile date filters** — extend `ListHeader`/`EntityListScreen`, or design warehouse mobile screens without date ranges? | Every mobile warehouse grid | **Before P3** (execution & mobile) | Extend `ListHeader` with a `'date'` type. It is a small platform-adjacent change and it unblocks every module, not just warehouse |
| **PD-D10** | **Does an adapter ship a frontend?** | The adapter scaffolds | **Before the first adapter is scaffolded** | No, following `accounting-adapter-dealer`. R7 `B10` forbids duplicating a base grid, which is the usual reason one would want a screen. If one ever does, it costs 8 aliases + SafeTranslation + 3 locale JSONs + Dockerfile.frontend + jest.config.js |
| **PD-D11** | **Extract branch-scope enforcement to platform?** (§4.11) | Nothing — but it prevents a class of leaks | Propose in v1, ship whenever | File the platform task; ship warehouse's own architecture rule regardless. Do not couple the two |
| **PD-D12** | **Impersonation column now, feature later** — is `on_behalf_of_actor_id` in v1? | The ledger's audit event DDL | **Before P0-02** | **Yes.** Copy `AccAuditActorKind`. Year one is what the first audit covers |

---

## 7. Verification commands — every claim in this document

Run from the `classic` repo root. Values are as of 2026-09-01.

```bash
# PD-1: branches is not polymorphic
grep -n "DROP COLUMN IF EXISTS owner_type\|DROP COLUMN IF EXISTS owner_id\|uk_branches_code" \
  platform/backend/src/main/resources/db/migration/V160__Remove_owner_fields_from_branches.sql
grep -c "ownerType\|ownerId" platform/backend/src/main/java/ai/platform/entity/Branches.java     # → 0

# branch_type still admits WAREHOUSE / DISTRIBUTION_CENTER
grep -n "chk_branches_type" platform/backend/src/main/resources/db/migration/V149__create_branches_table.sql

# GSTIN on branches
grep -n "gst_number" platform/backend/src/main/resources/db/migration/V182__Add_financial_columns_to_branches.sql

# grid_filter_definitions does not exist
grep -rln "CREATE TABLE.*grid_filter_definitions" --include=*.sql . | grep -v node_modules | wc -l  # → 0

# The five absences
grep -ril "tenant" platform/backend/src/main/java | wc -l                                          # → 0
grep -c -i "restore" platform/backend/src/main/java/ai/platform/service/DatabaseBackupService.java  # → 0
grep -ril "zpl\|escpos\|dymo" --include=*.java --include=*.ts --include=*.tsx . \
  | grep -v node_modules | wc -l                                                                   # → 0
grep -ril "persistQueryClient\|createAsyncStoragePersister\|offlineQueue" mobile/src | wc -l        # → 0
grep -ril "outbox" --include=*.java --include=*.sql . | grep -v node_modules | wc -l                # → 0

# PD-3: impersonation is schema-only, in accounting-base
grep -ril "impersonat" --include=*.java --include=*.ts --include=*.tsx . | grep -v node_modules     # → 5 files

# Concurrency toolkit
grep -rln "@Version" --include=*.java . | grep -v node_modules | wc -l                              # → 34
ls assets/backend/src/main/java/ai/assets/repository/ | grep -c "SequenceRepository"                # → 8
grep -rn "pg_advisory" --include=*.java . | grep -v node_modules | grep -v /test/                   # → 3 sites
grep -rin "SKIP LOCKED" --include=*.java --include=*.sql . | grep -v node_modules | wc -l           # → 0
grep -rln "CREATE CONSTRAINT TRIGGER" --include=*.sql . | grep -v node_modules | grep -v target     # → 1 file

# Scale ceilings
grep -n "MAX_PAGE_SIZE\|DEFAULT_PAGE_SIZE" platform/backend/src/main/java/ai/platform/constants/ApplicationConstants.java
grep -n "DEFAULT_MAX_EXPORT_ROWS" platform/backend/src/main/java/ai/platform/service/BaseExportService.java

# No exchange-rate source
grep -rln "exchange_rate\|currency_rate\|fx_rate" --include=*.sql . | grep -v node_modules | grep -v target
                                                                                                   # → 0
# Shared registries (PD-2)
awk '/COMMON_FILTER_CONFIGS/,0' platform/frontend/src/utils/filterUtils.ts | grep -cE "^  [A-Z0-9_]+: \{"   # → 211
awk 'NR>=101 && NR<=415' platform/backend/src/main/java/ai/platform/config/CacheConfiguration.java \
  | grep -cE '^[[:space:]]+"[a-zA-Z0-9._-]+",?$'                                                   # → 230
grep -rl "BranchFilterService" --include=*.java . | grep -v node_modules | wc -l                    # → 251

# Mobile filter surface
grep -n "type?: 'dropdown' | 'text'" mobile/src/components/common/ListHeader.tsx                    # → :216

# No per-module npm manifest
ls */frontend/package.json | wc -l                                                                  # → 1
```

### Claims this document does **not** make, because they cannot be verified statically

| Claim | Why not verified | What would settle it |
|---|---|---|
| The runtime definition of `chk_global_setting_module` / `chk_module` on a given install | Depends on which modules are enabled and in what order their migrations ran | `SELECT conname, pg_get_constraintdef(oid) FROM pg_constraint WHERE conname IN ('chk_global_setting_module','chk_module');` |
| Whether any live install still has pre-`V160` `branches.owner_type` | Needs a database | `SELECT column_name FROM information_schema.columns WHERE table_name='branches' AND column_name IN ('owner_type','owner_id');` |
| Whether any table in this suite is partitioned | Needs a database | `SELECT relname FROM pg_class WHERE relkind = 'p';` |
| Whether `enable.warehouse.3pl` binds inside `@ConditionalOnExpression` | No local Spring run; Docker-only build | One Docker boot with the flag, then `docker logs platform-backend \| grep "Warehouse Base Module"` — **PD-D1** |
| Free `menus.sort_order` at L1 for a Warehouse root node | Static analysis cannot see seeded rows | `SELECT name, sort_order FROM menus WHERE menu_level = 1 ORDER BY sort_order;` |
| Whether `mobile/src/screens/GenericScreen.tsx` gates a warehouse route | Not read | Read its `routePath.includes(...)` chain |
| Real export/pagination timings at warehouse volumes | Requires data and a running stack | A seeded 10M-row `whb_stock_movements` and `EXPLAIN (ANALYZE, BUFFERS)` on the grid query |

---

## Cross-references

- Module names, packages, bands, prefixes, invariants `L-1`…`L-14`, open decisions `OD-1`…`OD-7` —
  [`DECISIONS.md`](DECISIONS.md)
- How to land the five modules in the build, file by file —
  [`MODULE-INTEGRATION.md`](MODULE-INTEGRATION.md)
- The codebase evidence this register extends —
  [`reviews/R1-codebase-reality.md`](reviews/R1-codebase-reality.md) §4, §7, §8, §9
- The operational surface (`S-079`…`S-098`) —
  [`reviews/R5-standards-industry-ops.md`](reviews/R5-standards-industry-ops.md) §5, Register E
- The adapter contract and what an adapter may consume —
  [`reviews/R7-logistics-supply-chain-seam.md`](reviews/R7-logistics-supply-chain-seam.md) §4
