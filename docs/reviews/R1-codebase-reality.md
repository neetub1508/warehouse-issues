# LENS R1 — Codebase Reality

<!-- check-design-set: issue-citations file #791 — `#790` and `#791` are issues in **`neetub1508/classic`**, cited as `classic#790, #791` with the second elided in the ordinary English way. The first resolves; the elided continuation reads to the checker as a bare `#NN`. It is a cross-repo citation, never a warehouse issue -->

**Target:** a new four-module Warehouse / Inventory product
(`warehouse-base` + `warehouse` + `warehouse-adapter-<vertical>` + `warehouse-3pl`)
**Truth source:** `/Users/bbhushan/work/git/workspace/classic` — branch `main`, HEAD `f9b43a5804`, working tree clean
**Shape learned from (not trusted for facts):** `/Users/bbhushan/work/git/workspace/accounting/docs/`
**Date:** 2026-09-01
**Method:** reading and `grep` only. No `mvn` / `npm` / `tsc` was run (Docker-only build). Every count in this
report was computed with a command; anything not computed is marked `UNVERIFIED`.

> **Repo-state note, and it matters.** Since the accounting R1 review was written, the accounting product has
> **landed in this checkout**: `accounting-base/` (96 Java files, 11 migrations), `accounting/`,
> `accounting-adapter-dealer/` and `accounting-india/` (stubs) now exist at the repo root, and the full
> 4-module integration is wired through `pom.xml`, both Dockerfiles, `tsconfig.json`, `ModuleImportSelector`,
> `start.sh`, `docker-compose.yml` and Railway. **This is the single most valuable asset for the warehouse
> build:** a complete, recent, four-module base+app+adapter+pack decomposition that already solved the exact
> structural problem warehouse faces. Copy it. Section 2 is that copy list, verified line by line.

---

## 0. Executive summary — the ten load-bearing conclusions

1. **The proposed Flyway bands V900000–V909999 and V910000–V919999 are already occupied and are hard-reserved
   by platform code.** 135 OEM-seed `.sql` files sit in V900000–V909999 and **434 per-client `.sql` files** sit
   in V910000–V919999, and `FlywayConfiguration.java:296-320` renumbers legacy history rows *into* both bands.
   A warehouse migration numbered V910001 collides with `V910001__pasco_departments.sql` on every client
   install. **This is a BLOCKER and the band must change before a single issue is written.** (C-001, C-002)
2. **V500000–V599999 is entirely free** (0 files) and is the recommended home:
   base `V500000–V509999`, app `V510000–V519999`, adapters `V520000+`, 3PL `V530000–V539999`. (C-003)
3. **A new module is 16 files and ~40 edits across 2 build systems, plus one runtime gate that fails silently.**
   The gate everyone forgets is `ModuleImportSelector.java` — without an entry the JAR ships and loads nothing.
   Accounting did all 16; `startX2.sh` is the one it missed. (C-005..C-011)
4. **Accessories has no stock ledger.** `accessory_inventory_transactions` is a *single-sided log written
   alongside* an in-place-mutated `accessory_stock_levels` row. Balance is not derivable from movements;
   some paths (receipt reversal) move the balance and write no movement at all. (C-021)
5. **Three headline inventory capabilities in accessories are schema-only, with zero call sites**: reservations
   (`quantity_reserved` is never written; `reserveQuantity()` is dead code), UoM conversion (`conversion_factor`
   is stored, displayed, exported — never applied), and physical counts (`generateAdjustments()` sets
   `status='POSTED'` and generates nothing). (C-022, C-023, C-026)
6. **No concurrency control anywhere on stock.** `StockLevel` has no `@Version`, no `@Lock`, and the DB has no
   `CHECK (quantity_on_hand >= 0)`. Two concurrent issues both read the same on-hand, both pass the guard, and
   one deduction is lost. The code comment even names the race and does not defend against it. (C-024)
7. **Every other vertical has zero stock capability.** `services`, `field-service` and `assets` contain **no**
   stock/parts/consumable table of any kind. Dealer's PDI is a serialised, one-unit-per-row vehicle inventory,
   not a quantity ledger. Warehouse is the only path to job parts, van stock and asset spares. (C-034)
8. **There is no shared party/supplier master.** `asset_vendors` is assets-owned; automotive `customers` is a
   customer master; accessories receipts carry **no supplier field at all**. `warehouse-base` must own its own
   counterparty entity or inbound receiving cannot name who shipped. (C-035)
9. **The concurrency toolkit warehouse needs mostly exists as precedent, in four places** — advisory locks
   (3 sites), `PESSIMISTIC_WRITE` counter rows (assets `*_sequences`), `CREATE CONSTRAINT TRIGGER …
   DEFERRABLE INITIALLY DEFERRED` (accounting-base V600111 — the *first and only* in the repo), and a
   derived-balance-not-cached precedent (`pdi_storage_slot_assignments`). None of it is in a reusable platform
   utility; warehouse re-implements each. (C-037..C-041)
10. **"Permanently separate" costs 17 tables, 71 backend files, 11 reports, 33 mobile screens and one duplicate
    item master, permanently** — and buys back nothing, because none of the accessories code is reusable as a
    library (it is not extracted, not interfaced, and depends on `accessory_products`). The real cost is not the
    duplication; it is that **there will be two stock truths with no reconciliation and no unified report.** (C-032)

---

## 1. CORRECTED FACTS

### 1.1 Corrections to the *warehouse brief* (what the caller asked for that the code contradicts)

| # | Brief says | Reality in `classic` | Consequence |
|---|---|---|---|
| **WF-1** | `warehouse-base` Flyway **V900000–V909999** | **OCCUPIED.** 135 files in `dealer/backend/src/main/resources/db/seed/{maruti,honda,tata,hyundai,mahindra,toyota,kia,mg,jcb,tatacommercial}/`, e.g. `dealer/.../seed/maruti/V900000__maruti_cleanup.sql`, `V900001__maruti_company_setup.sql`. `FlywayConfiguration.java:151` labels the band `"OEM Seed: … (V900000+)"` and `:296-304` renumbers legacy V70000-range history rows into it | **BLOCKER.** Move the band. See C-001/C-003 |
| **WF-2** | `warehouse` Flyway **V910000–V919999** | **OCCUPIED, 434 files.** `platform/backend/src/main/resources/db/client/{ktlautomobiles,logix,pasco,platinum,vehicron}/V910001…`. `FlywayConfiguration.java:157` — *"Client data uses V910000+ range (moved from V80000+)"*. Version numbers are **deliberately reused across clients**: `V910001__` exists in all five directories | **BLOCKER.** Any warehouse V9100xx collides with a client migration on every `CLIENT_NAME` install |
| **WF-3** | adapters **V920000+**, 3PL **V930000–V939999** | Free today (0 files), but they sit **between** two platform-reserved bands (V910000 client, V950000 test) inside the same "seed/client/test" numbering region that `FlywayConfiguration` treats as its own. Numerically safe, semantically a landmine | Move with the rest. Do not colonise the seed region |
| **WF-4** | four Maven modules mirroring accounting | Accounting is now **four modules in this checkout** and every touchpoint is done. The brief's decomposition is directly supported by precedent | Copy `pom.xml:220-283`, `Dockerfile.backend:19-23/41-45/68-72/140-260/273/340-459`, `Dockerfile.frontend:41-44/72-73/158-177/194-197` |
| **WF-5** | package `ai.warehouse3pl` | Legal Java. But the Spring property would be `enable.warehouse.3pl` → env `ENABLE_WAREHOUSE_3PL`, and the Maven profile activation property likewise. Relaxed binding of a **digit-leading path segment** has no precedent in this repo (`enable.insurance.360` is the closest, `pom.xml:195`, and it works) | Low risk, but pin it: `enable.insurance.360` proves digit segments bind. Reuse that exact shape |
| **WF-6** | "generic inbound movement port so a future logistics module can move stock without warehouse-base depending on it" | The pattern exists three times — `ExportService(List<ExportFormatHandler>)` (`platform/.../service/export/ExportService.java:31`), `BoomBarrierWebhookController(List<IBoomBarrierHandler>)` (`automotive/.../controller/BoomBarrierWebhookController.java:44-48`), `AccImportHandlerRegistry(List<AccImportHandler>)` (`accounting-base/.../service/imports/AccImportHandlerRegistry.java:36-44`) | **The port shape is settled.** `List<T>` bean-collection registry, not `@Primary` override (which allows only one implementation) |

### 1.2 Corrections to the *accounting design set* (things it asserts that this checkout now contradicts)

| # | Accounting doc claim | Reality (file:line) |
|---|---|---|
| **AF-1** | R1 §0 row 2 / CF-2: *"`warehouse-base` … do not exist in this repo at all"* and *"Top-level module dirs are: platform automotive dealer accessories services insurance insurance-360 assets lead-sharing field-service submittals product-lift doc-ocr-ai"* | **Superseded.** The root now also holds `accounting-base/ accounting/ accounting-adapter-dealer/ accounting-india/`. Still no `warehouse*/` or `supply-chain-core/`. The list needs 4 more rows |
| **AF-2** | R1 CF-14: *"Every module ships `en` only"* | **FALSE now.** `accounting-base/frontend/src/i18n/locales/{en,fr,hi}/accountingBase.json` — three locales. The newest module ships all three. Warehouse should follow accounting, not submittals |
| **AF-3** | R1 CF-23: *"the Railway path is already stale by five modules … Assets, product-lift, field-service, submittals, insurance-360 and doc-ocr-ai are absent from both"* | **Half-fixed.** `shared/scripts/railway/template.conf:41-46` and `setup-railway-client.sh:276-281,423-429` now carry all four `ENABLE_ACCOUNTING*` plus `ENABLE_DOC_OCR_AI`. Still absent: `ASSETS`, `PRODUCT_LIFT`, `FIELD_SERVICE`, `SUBMITTALS`, `INSURANCE_360`. Frontend var list (`:421-430`) additionally drops `LEAD_SHARING` |
| **AF-4** | R1 §2.12 *"`shared/scripts/startX2.sh` — B — doc-ocr-ai HAS done this"* | `startX2.sh:94-97,183-194` carries 12 flags and **no accounting flag at all**. Accounting skipped it. So the touchpoint is real but *not* uniformly applied — treat it as optional-but-name-it, not mandatory |
| **AF-5** | `PLATFORM-DEPENDENCIES.md:515-516` — OEM seed `V900000–V909999`, per-client `V910000–V919999`, *"version numbers deliberately reused across clients"* | **VERIFIED, exactly right, and it is the fact that kills the warehouse band choice.** `ls db/client/*/V910001__*.sql` → 5 files, one per client. Counts: 135 / 434 / 32 (test, V950000+) |
| **AF-6** | R1 CF-4: *"12 files across 2 build systems"* | Now **16** files. Add: `platform/frontend/tsconfig.json` (aliases), `shared/scripts/railway/template.conf`, `setup-railway-client.sh`, and the per-module `ArchitectureInvariantsTest` (new house style — accounting-base and accounting each ship one) |

### 1.3 Corrections to `CLAUDE.md`

| # | CLAUDE.md says | Reality (file:line) |
|---|---|---|
| **CM-1** | MOBILE MODULE: *"`EntityListScreen` `additionalFilters` prop **only supports dropdowns**"* | **STALE.** `mobile/src/components/common/ListHeader.tsx:210-218` — `AdditionalFilterConfig` now has `type?: 'dropdown' \| 'text'`. Text filters are supported; **date filters still are not** |
| **CM-2** | MODULES table | Has no `warehouse*` rows and (correctly) 4 accounting rows. Adding warehouse means 4 new rows and a band that does not collide (C-003) |
| **CM-3** | *"NO JSONB"* | Overstated, and the repo's own ratchet says so — `platform/backend/src/test/java/ai/platform/architecture/ArchitectureInvariantsTest.java:225-239` freezes a **baseline** of existing jsonb migrations rather than banning it. `grid_preferences.default_columns` is `JSONB NOT NULL DEFAULT '[]'` (`V18:12`) and `default_filters` is `JSONB` (`V229:50-51`), so **every warehouse grid migration must emit `'[…]'::jsonb`**. The rule that holds is "no jsonb on new `wh_` business tables" |
| **CM-4** | *"Migration Rules — always include `grid_column_definitions` and `filter_definitions`"* | Correct, and `grid_filter_definitions` **does not exist** — 0 hits over all migrations. The brief's own task text mentions `grid_filter_definitions`; that name would crash Flyway |

---

## 2. THE COMPLETE NEW-MODULE TOUCHPOINT LIST — verified against the accounting 4-module landing

Legend: **B** = build-time gate (miss → build fails, or the JAR/source is silently omitted).
**R** = runtime gate (build succeeds, module is inert or 500s at first use). **D** = documentation.

| # | File | Kind | What warehouse must add | Evidence (accounting's version) |
|---|---|---|---|---|
| 1 | `pom.xml` — profiles | **B** | 4 profiles: `with-warehouse-base`, `with-warehouse` (lists base **then** app), `with-warehouse-dealer` (lists automotive→dealer→base→app→adapter), `with-warehouse-3pl` | `pom.xml:220-283`. Copy the **ordering** exactly: `:242-243` base before app, `:261-265` five modules in dependency order |
| 2 | `pom.xml` — `all-modules` | **B** | 4 `<module>` rows, base first | `pom.xml:286-306` (16 rows today) |
| 3 | `<mod>/backend/pom.xml` ×4 | **B** | base = parent + `platform-backend` + lombok; app = + `warehouse-base-backend`; adapter = + `dealer-backend` | mirror `automotive/backend/pom.xml` (base shape) and `dealer/backend/pom.xml` (consumer shape) |
| 4 | `shared/docker/Dockerfile.backend` | **B** | 4 `ARG ENABLE_*`; 4 `COPY */pom.xml`; 4 `COPY */backend`; the `NEED_*` derivation + profile accumulation + migration `cp`; the `rm -rf */target` list; the `mkdir -p` list; 4 `COPY --from=builder … /tmp/*-jars/`; 4 jar-copy blocks; the `rm -rf /tmp/*-jars` list; **and the build-time assertion block** | `:19-23`, `:41-45`, `:68-72`, `:80-81`, `:145-181`, `:213`, `:223-256`, `:273`, `:340-344`, `:431-457`, `:459` |
| 5 | `shared/docker/Dockerfile.backend` — the assertion block | **B** | Copy it. It is the only thing that turns "consumer enabled, base JAR missing" from a silent runtime 500 into a build failure | `:223-256` — four explicit `BUILD FAILED` guards |
| 6 | `shared/docker/Dockerfile.frontend` | **B** | 4 `ARG`; `COPY <mod>/frontend/src/.` for the two modules that **have** a frontend (adapters/3PL may not); the merge `if` blocks; the `rm -rf /tmp/*-src`; 4 `ENV NEXT_PUBLIC_ENABLE_*` | `:41-44`, `:72-73`, `:158-177`, `:194-197`. Note accounting copies **no** adapter frontend — adapters are backend-only |
| 7 | `platform/frontend/tsconfig.json` | **B** | 8 alias entries per frontend-bearing module (`@warehouse/*`, `/components/*`, `/services/*`, `/hooks/*`, `/types/*`, `/config/*`, `/constants/*`, `/i18n/*`), all pointing at `./src/*` | `:162-215` (accounting-base + accounting) |
| 8 | `platform/backend/.../config/ModuleImportSelector.java` | **R** | 4 FQCN constants + 4 `isClassPresent` blocks. **The gate that fails silently.** A module JAR on the classpath with no entry here loads nothing | `:52-55` constants, `:154-186` blocks |
| 9 | `<mod>/backend/.../<Mod>ModuleConfig.java` ×4 | **R** | `@Configuration` + `@ConditionalOnExpression` (base must OR in every consumer flag) + `@ComponentScan/@EntityScan/@EnableJpaRepositories` on the module package | `accounting-base/.../AccountingBaseModuleConfig.java:46-53` |
| 10 | `shared/docker/docker-compose.yml` | **B+R** | 4 flags in the **backend build args**, 4 in **backend environment**, 4 in **frontend build args**, 4 `NEXT_PUBLIC_*` in frontend environment | `:123-126`, `:148-151`, `:293-296`, `:325-328` |
| 11 | `shared/scripts/start.sh` | **B** | 4 defaults, 4 `--enable-*` flags + help text, the dependency-derivation block, 4 `.env` writes, 2× 4 `export`s, the summary block | `:36-39`, `:132-135`, `:289-303`, `:479-503`, `:775-778`, `:945-948`, `:1101-1119`, `:1810-1813` |
| 12 | `shared/scripts/startX2.sh` | **B** (optional) | Accounting **skipped this**. Decide explicitly; if warehouse is meant to be startable there, 2 edits (`:94-97`, `:183-194`) | `startX2.sh` has 12 flags, no accounting |
| 13 | `shared/scripts/railway/template.conf` + `setup-railway-client.sh` | **D/B** | 4 config keys + 4 backend vars + 4 frontend vars + 4 summary lines | `template.conf:41-44`; `setup-railway-client.sh:276-279`, `:423-426`, `:574-577` |
| 14 | `<Mod>SafeTranslation.tsx` ×2 | **R** | One per frontend-bearing module, exporting `clearTranslationCache()`, the `SafeTranslation` component and `useSafeTranslation()`. Pages import `t()` from **their module's** file, never from `@platform/hooks/useSafeTranslation` | `accounting-base/frontend/src/components/AccountingBaseSafeTranslation.tsx`; `accounting/frontend/src/components/AccountingSafeTranslation.tsx` |
| 15 | `CacheConfiguration.java` | **R** | Every `@Cacheable`/`@CacheEvict` name. `:375-376` — *"An unregistered name throws IllegalArgumentException on the FIRST call, not at startup"*. 202 names registered today | `platform/.../config/CacheConfiguration.java:101-404` |
| 16 | `platform/frontend/src/utils/filterUtils.ts` | **R** | One `COMMON_FILTER_CONFIGS.<SCOPE>` block per grid. 210 scopes today. A field absent here is **silently dropped** before the API call | `:346` onward |
| 17 | `<mod>/backend/src/test/.../ArchitectureInvariantsTest.java` ×4 | **B** | New house style: each accounting module ships its own 660-line ratchet (`@PreAuthorize` coverage, cache-name registration, no `PageRequest.of`, no `findById` in a loop, plus self-tests that the scanners are not passing vacuously) | `accounting-base/backend/src/test/java/ai/accountingbase/architecture/ArchitectureInvariantsTest.java` |
| 18 | `CLAUDE.md` MODULES table | **D** | 4 rows with the chosen band | `CLAUDE.md` MODULES table (18 rows today) |

**NOT required** (verified, contra a common assumption):

- `FlywayConfiguration.java` — knows only **six** modules (`dealer, assets, accessories, services, insurance, lead.sharing`, `:73-78`). The last **ten** modules added to this repo did not touch it. Its `enable.*` flags feed only console logging (`:89-217`, printed `:225-240`). Adding `enable.warehouse` there is cosmetics.
- `application.yml` `enable:` block (`:366-373`) — same six. Spring relaxed binding resolves `enable.warehouse` from `ENABLE_WAREHOUSE` without a declaration.
- Any Flyway *location* registration — `configuration.locations(...)` at `:217-219` adds `classpath:db/migration` once (`:87`); module migrations reach it because **`Dockerfile.backend` physically copies them into `platform/backend/src/main/resources/db/migration/` before the Maven build** (`:140-181`). That flattening is why cross-module version collisions are fatal (C-011).

---

## 3. FLYWAY REALITY

### 3.1 The occupancy map — computed, not recalled

`find . -path "*/db/migration/*" -o -name "V*__*.sql"` over the whole tree, 3 297 versioned files, bucketed per 10 000:

| Band | Owner | Files |
|---|---|---|
| V0–V9 999 | platform | 751 (`ls platform/.../db/migration/*.sql` → 753 incl. 2 non-integer `V1_1`, `V1_2`) |
| V10 000–V19 999 | automotive | 116 |
| V20 000–V29 999 | dealer | 736 |
| V30 000–V39 999 | accessories | 325 |
| V40 000–V49 999 | services | 249 |
| V50 000–V59 999 | insurance | 42 |
| V60 000–V69 999 | assets | 150 |
| V70 000–V79 999 | lead-sharing | 14 |
| V80 000–V89 999 | field-service | 63 |
| **V90 000–V99 999** | *(legacy test-data source range; renumber source)* | 0 on disk |
| **V100 000–V109 999** | **FREE** | 0 |
| V110 000–V119 999 | submittals | 18 |
| V120 000–V129 999 | insurance-360 | 146 |
| **V130 000–V599 999** | **FREE (47 bands)** | 0 |
| V600 000–V609 999 | accounting-base | 11 (max V600200) |
| V610 000–V619 999 | accounting *(declared, empty)* | 0 |
| V620 000–V620 999 | accounting-adapter-dealer *(declared, empty)* | 0 |
| V602 000–V602 999 | accounting-india *(declared, **nested inside base's band**)* | 0 |
| **V621 000–V699 999** | **FREE** | 0 |
| V700 000–V709 999 | doc-ocr-ai | 34 |
| **V710 000–V799 999** | **FREE** | 0 |
| V800 000–V809 999 | product-lift | 41 |
| **V810 000–V899 999** | **FREE** | 0 |
| **V900 000–V909 999** | **OEM SEED — RESERVED** | **135** |
| **V910 000–V919 999** | **CLIENT DATA — RESERVED** | **434** |
| **V920 000–V949 999** | free but inside the reserved region | 0 |
| **V950 000–V959 999** | **TEST DATA — RESERVED** | **32** |

OEM sub-bands (`dealer/backend/src/main/resources/db/seed/<oem>/`):
maruti V900000–V900024 (25) · honda V901001–V901011 (11) · tata V902001–V902011 (11) ·
hyundai V903001–V903011 (11) · mahindra V904001–V904011 (11) · toyota V905001–V905011 (11) ·
kia V906001–V906011 (11) · mg V907001–V907011 (11) · jcb V908001–V908013 (13) ·
tatacommercial V909001–V909020 (20).

Client dirs (`platform/backend/src/main/resources/db/client/<client>/`):
ktlautomobiles 100 · logix 6 · pasco 203 · platinum 22 · vehicron 103. **Versions are reused across clients**
(`V910001__` exists five times), because only one client directory is ever a Flyway location.

### 3.2 The reservation is code, not convention

```java
// FlywayConfiguration.java:296-304
// Fix 2: Renumber OEM Seed V70000-V79999 -> V900000-V909999 (offset +830000)
"UPDATE flyway_schema_history SET version = CAST(CAST(version AS INTEGER) + 830000 AS TEXT) ..."
// :306-312  Client Data V80000-V89999 -> V910000-V919999
// :314-320  Test Data   V90000-V99999 -> V950000-V959999
```

and, immediately after (`:322-327`):

```java
// Remove duplicate entries (keep lowest installed_rank per version)
"DELETE FROM flyway_schema_history a USING flyway_schema_history b"
+ " WHERE a.version = b.version AND a.installed_rank > b.installed_rank"
```

That `DELETE` is the second half of the blocker. If a warehouse `V900001` history row and a renumbered OEM-seed
`V900001` history row both exist, **one is deleted without a warning** and Flyway will re-run the surviving
file's counterpart on the next boot. The renumber is gated behind `flyway.legacy-fix.enabled` (default `false`,
`:251-252`), so it is a latent landmine rather than an immediate one — which is worse, because it fires on the
one deployment that turns it on.

Locations are added conditionally: OEM seed only when a dealer-family module **and** `dealer.oem` are set
(`:143-153`); client data only when `client.name` names an existing folder (`:163-180`); test data only with
`test.data.brand` (`:192-212`). So a *warehouse-only* install would not load them — but a
**dealer + warehouse** install, or **any install with `CLIENT_NAME` set**, would, and Flyway rejects two
migrations with the same version in its configured locations.

### 3.3 `out-of-order` — three settings, two of them opposed

| Where | Value | Evidence |
|---|---|---|
| Spring Boot default | `true` | `platform/backend/src/main/resources/application.yml:105` |
| Spring Boot in Docker | **overridden to `${FLYWAY_OUT_OF_ORDER:-false}`** | `shared/docker/docker-compose.yml:183` — `SPRING_FLYWAY_OUT_OF_ORDER` |
| Standalone `db-migrate` service (platform migrations only) | `${FLYWAY_OUT_OF_ORDER:-false}` | `shared/docker/docker-compose.yml:88` |
| `start.sh` | default `false`, flipped to `true` **and persisted to `.env`** by `--restore-backup` | `start.sh:48`, `:367`, `:377`, `:784-785`, `:1308-1312` |
| `startX2.sh` | hard `false` | `startX2.sh:200` |
| Test profile | `true` | `platform/backend/src/test/resources/application.yml:42` |

**Consequence for a standalone-first-then-upgradable warehouse install:** the effective Docker default is
`out-of-order: false`. A warehouse-only install that later adds dealer would try to apply dealer's V20000-range
migrations *below* already-applied warehouse V5xxxxx rows and be refused unless `FLYWAY_OUT_OF_ORDER=true`.
**Pick a band numerically ABOVE every vertical warehouse may later be installed alongside**, or document
`FLYWAY_OUT_OF_ORDER=true` as a required upgrade step. V500000+ satisfies neither for dealer (V20000) —
so the upgrade path is: *warehouse first + verticals later requires out-of-order*. State it, do not discover it.

### 3.4 `repair()` on failure

`FlywayConfiguration.java:246-264` — `flywayMigrationStrategy()`:

```java
try { flyway.migrate(); }
catch (Exception e) {
    System.out.println("  ⚠ Migration failed, running repair and retrying: " + e.getMessage());
    flyway.repair(); flyway.migrate();
}
```

Any migration failure is followed by a blind `repair()` + retry. `repair()` removes failed-migration rows and
**realigns checksums**, so a genuinely broken warehouse migration is retried once and, if it fails again, the
history is left half-repaired. `start.sh:1191-1302` runs a real `flyway repair` as part of
`restore_backup_and_repair()`. Warehouse migrations must therefore be **individually idempotent and
transactional** — the accounting-base files are (every one is `ON CONFLICT` / `WHERE NOT EXISTS` / `IF NOT EXISTS`
guarded, e.g. `V600000:21`).

---

## 4. WHAT WAREHOUSE INHERITS FROM PLATFORM — and where the shape is wrong

| Capability | Table / class | Shape | Fit for warehouse |
|---|---|---|---|
| Branches | `branches` @ `platform/.../V149__create_branches_table.sql:9`; `branch_name` not `name` (`:18`); `owner_type`/`owner_id` NOT NULL, **no FK** (`:13-14`) | `CHECK (owner_type IN ('DEALER','COMPANY','ASSET','MANUFACTURING','WAREHOUSE','PLATFORM'))` `:63`; `CHECK (branch_type IN (…,'WAREHOUSE',…,'DISTRIBUTION_CENTER'))` `:61`; `UNIQUE (owner_type, owner_id, branch_code)` `:60` | **GOOD — `'WAREHOUSE'` is already in both vocabularies.** Warehouse sites can be platform branches. But the vocabulary is closed: no `'3PL'` value exists, so warehouse-3pl needs a widening migration |
| Branch scoping | `branch_staff` @ `V150__create_branch_staff_table.sql:10`; `useUserBranches` (`platform/frontend/src/hooks/useUserBranches.ts`); `BranchFilterService.toBranchIdsCsv` used in accessories reports | Row-level guard is per-module, not enforced by platform | **PARTIAL.** Reusable, but each warehouse query must pass `userBranchIds` itself (accessories does — `StockReportQueryService.java:516`) |
| Users / person display | `user_details.employee_id` (not `employee_code`); `UserDetails.getFullName()` | Canonical | GOOD |
| Permissions | `permissions` @ `V1_1__Initial_schema_safe.sql:30`; `permission_dependencies` @ **`V248:17-30`** — **a PLATFORM table**, with `uq_permission_dependency` `:27` and `chk_no_self_reference` `:29`. The only other creator, `dealer/V20501:10`, is `IF NOT EXISTS` and now a no-op | Columns `permission_id`, **`dependent_permission_id`**, `dependency_type DEFAULT 'REQUIRED'`. Semantics documented `V248:38-41` | **GOOD.** Warehouse must **NOT** create this table |
| Menus | `menus` @ `V16:7`, `CHECK (menu_level BETWEEN 1 AND 3)` `:27`; `menu_translations` `:49`; `menu_permissions` `:36`; `required_permission_prefix` @ `V209:7`; `is_mobile_enabled` @ `V199:7` | 3 levels only; no unique constraint on `(name,parent_id,menu_level)` | **GOOD, with a trap.** Menu inserts need `WHERE NOT EXISTS` guards (`assets/.../V60171:154-155` spells out why `ON CONFLICT` does not work). Seed `en`/`fr`/`hi` `menu_translations` rows |
| Grid config | `grid_preferences` @ `V18:7` (`default_columns JSONB NOT NULL DEFAULT '[]'` `:12`), `grid_column_definitions` @ `V18:43`, `filter_definitions` @ `V229:8`, `grid_preferences.default_filters JSONB` @ `V229:50-51`, `user_grid_preferences` @ `V18:24` | `grid_filter_definitions` **does not exist** (0 hits) | **GOOD.** Both `default_columns` AND `default_filters` must be populated — `filter_definitions.default_visible` alone does nothing |
| Filter allowlist | `platform/frontend/src/utils/filterUtils.ts:346+`, **210 scopes** today; 8 field types `:30` (`text select enum multiselect boolean date dateOnly number`) | `dateOnly` vs `date` is documented `:49-56`: `date` shifts to UTC day boundaries and moves the "from" bound back a day for users east of UTC | **GOOD, and `dateOnly` is load-bearing for warehouse** — `expiry_date`, `manufacture_date`, `count_date`, `posting_date` are pure DATE columns |
| Export | `BaseExportService` (`platform/.../service/BaseExportService.java`); `BaseController.createExportResponse(byte[], String filename, String contentType)`; `followVisibleColumns` (`platform/frontend/src/types/export.ts`); `ExportServiceContractTest` ratchet | Grid↔export parity is the rule, frozen by a ratchet that "may shrink, never grow" | GOOD |
| Import | **No generic backend framework.** Every importer is bespoke: `platform/.../service/leave/LeaveBalanceImport*` (9 classes), `accessories/.../StockReceiptBulkImportService`, `accounting-base/.../service/imports/AccImportHandlerRegistry` + `AccImportHandler`. Frontend has reusable `ImportButton.tsx` + `ImportModal.tsx` | The **best** shape is accounting's: `acc_import_batches` + `acc_import_batch_rows` + a `List<AccImportHandler>` registry + a reversal path (`AccImportBatchReverseModal.tsx`) | **MISMATCH → build it.** Warehouse needs batch import for items, opening stock, ASN lines. Copy `AccImportHandlerRegistry`, do not copy the leave importer |
| Documents / S3 | `documents` @ `V81:39`; `document_permissions` `:74`; `ObjectStorageService`, `FileStorageService`, `FileSecurityService` | **No polymorphic owner** — no `entity_type`/`entity_id`. Ownership is `folder_id`/`category_id`/`owner_id`/`department_id` | **MISMATCH.** Every module builds its own link table: `accessory_stock_receipt_documents`, `asset_documents`, `acc_document_links` (`V600110`). Warehouse needs `wh_document_links`. **Note `acc_document_links` FK is `ON DELETE CASCADE` (`V600110:104-105`) — the link vanishes when the file is deleted.** For a GRN photo or a damage certificate that is probably wrong; use `NO ACTION` |
| Notifications | `notifications` @ `V319:13`; `NotificationService`; `NotificationDeliveryListener` with `@TransactionalEventListener(AFTER_COMMIT, fallbackExecution = true)` | Async, after-commit | GOOD for replenishment alerts / expiry warnings |
| Audit | Two independent trails. (a) `PlatformLogger.audit(...)` → log stream only. (b) `user_activity_logs` @ `V717:29` fed by `UserActivityTrackingAspect` — pointcut `within(ai..controller..*)` (`:59`), module derived from package segment 2 (`:167-174`), entity from the controller class name (`:176-181`) | **Package-shape requirement:** controllers MUST be in `ai.<module>.controller…`, or writes are invisible to auditing. `ai.warehousebase.controller` → module `WAREHOUSEBASE` | **PARTIAL.** Async, out-of-transaction, swallows its own exceptions (`accounting-base/V600111:23-30` states this explicitly). For a stock ledger that is telemetry, not an audit trail |
| Dashboards / widgets | `widget_definitions` @ `V234:12`, `CONSTRAINT chk_module CHECK (module IN ('platform','dealer','shared'))` `:36`, widened by `V276:9-10`, `V557:16-18`, `insurance/V50009:7-8`, `accounting-base/V600200` | **`'warehouse'` is NOT in the list.** Latest platform assertion `V557:18` = `('platform','dealer','shared','accessories','assets','insurance','services')` | **BLOCKED until widened.** First warehouse widget insert → `23514` |
| Global settings | `global_settings` @ `V337:8`, `chk_global_setting_module` `:42`; widened `V553:14-15` (**adds `'WAREHOUSE'`**), `field-service/V80013:22-25`, `insurance-360/V120122:25-28`, `product-lift/V800039:80-83`, `accounting-base/V600200` | **`'WAREHOUSE'` is ALREADY allowed** — added by `platform/V553`, which credits a `V190035 (warehouse-core)` migration that does not exist in this checkout | **GOOD, and free.** Use `module='WAREHOUSE'` |
| Activity history feed | `all_activity_history` view — **dealer-owned**, `dealer/V20412:354` created, `dealer/V20885:85-177` redefined; unions `login_activity_history` ∪ `pdi_activity_history` ∪ `business_activity_history` | Accessories deliberately stayed out (`accessories/V30379:7-9`) | **MISMATCH.** Joining it would make warehouse depend on dealer. Build `wh_activity_history` standalone, as accessories did |
| Currency | `currencies` @ `V203:5` | No rate column | PARTIAL — warehouse valuation in a second currency has no rate source |
| Number series | **DOES NOT EXIST at platform level.** `SequentialCodeGenerator` (`platform/.../util/SequentialCodeGenerator.java`) is scan-based: `nextSequence()` reads existing codes for the prefix, `generate()` then loops `while (existsCheck.test(code)) sequence++` | Explicitly **not gapless** and racy — the loop is a best-effort defence behind a unique constraint | **MISSING → blocks a compliant GRN/pick/ship numbering.** The gapless precedent is per-module: `assets/.../AssetTagSequenceRepository.java:25-27` — `@Lock(PESSIMISTIC_WRITE)` on a `next_value` counter row (`assets/V60014:2-9`), with a comment naming the exact race |
| Approval framework | `leave_approval_config` (platform V755), `service_approval_configs`, `accessory_delivery_approval_config`, `asset_transfer_approval_configs`, and the accounting **port** `AccApprovalGate` + `PermissionOnlyAccApprovalGate` | 5 independent implementations; no platform-generic one | **MISMATCH.** Warehouse write-off / negative-adjustment approval: copy the `AccApprovalGate` seam shape, not any of the concrete configs |

---

## 5. THE EXISTING INVENTORY IMPLEMENTATIONS, IN FULL

### 5.1 Accessories — the only quantity-based inventory in the repo

**17 of its 71 tables are inventory-scoped**, and **71 Java files** sit under
`accessories/backend/src/main/java/ai/accessories/**/inventory*`.

| Table | Created by | What it is |
|---|---|---|
| `accessory_warehouses` | `V30017:8` | Warehouse master. `code`, `name`, `warehouse_type ('MAIN','SATELLITE','VIRTUAL','RETURNS')`, address, `capacity INTEGER`. **No `branch_id`** |
| `accessory_warehouse_branch` | — | Junction warehouse↔branch |
| `accessory_storage_bins` | `V30033:8` | `bin_code`, `warehouse_id`, and **free-text** `zone`/`aisle`/`rack`/`level` VARCHARs, `bin_type`, `max_weight`, `max_volume`. **No zone entity, no bin hierarchy, no putaway rules** |
| `accessory_stock_levels` | `V30130:6` | The balance. `product_id, warehouse_id, bin_id, quantity_on_hand DECIMAL(18,4), quantity_reserved, quantity_available GENERATED ALWAYS AS (on_hand - reserved) STORED, batch_number VARCHAR(50), serial_number VARCHAR(100), expiry_date, average_cost, last_cost, last_count_date, last_movement_date`. Unique on `(product, warehouse, COALESCE(bin), COALESCE(batch), COALESCE(serial))` `:39-46` |
| `accessory_inventory_transactions` | `V30131:6` | The movement log. `transaction_number UNIQUE, transaction_date, transaction_type ('RECEIPT','ISSUE','TRANSFER','ADJUSTMENT','RETURN'), product_id, quantity, uom_id, from_warehouse/from_bin, to_warehouse/to_bin, unit_cost, total_cost, reference_type/reference_id/reference_number, batch/serial/expiry`. **Also doubles as the Stock Receipt entity** |
| `accessory_stock_transfers` / `_items` | `V30...:6` | Header/line transfer document |
| `accessory_stock_adjustments` | `V30...:6` | Adjustment document |
| `accessory_inventory_counts` / `_items` | `V30...:6` | Count document |
| `accessory_stock_receipt_documents`, `_history`, `_imports`, `_import_batches` | various | Receipt attachments, edit history, bulk import |
| `accessory_issuance_records` / `_items` | `V30...:9/29` | Issuance from a sales order |
| `accessory_insufficient_stock_logs` | `V30...:8` | Log of blocked/pended issuances |
| `accessory_uom` / `accessory_uom_company` | `V30013:8` | UoM master with `base_unit_id` self-FK and `conversion_factor DECIMAL(18,6)` |

**Screens:** 12 inventory routes under `accessories/frontend/src/app/accessories/` — `inventory`, `inventory-counts`,
`stock-adjustments`, `stock-receipts`, `stock-receipt-imports`, `stock-transfers`, `storage-bins`, `warehouses`,
`units-of-measure`, `products`, plus `reports/`.
**Reports: 11**, all under `reports/` — `stock-summary`, `stock-movement`, `low-stock`, `insufficient-stock`,
`inventory-valuation`, `warehouse-utilization`, `slow-moving`, `top-selling`, `category-performance`,
`sales-summary`, `return-analysis`.
**Permission resources: 23** total for the module, of which 12 are inventory:
`accessory-warehouses`, `accessory-storage-bins`, `accessory-uom`, `accessory-stock-levels`,
`accessory-stock-receipts`, `accessory-stock-adjustments`, `accessory-stock-transfers`,
`accessory-inventory-counts`, `accessory-inventory-transactions`, `accessory-insufficient-stock`,
`accessory-reports`, `accessory-products`.
**Mobile: 33 `accessory*` screens** under `mobile/src/screens/` including `accessoryStockLevel`,
`accessoryStockReceipt`, `accessoryStockTransfer`, `accessoryStockAdjustment`, `accessoryInventoryCount`,
`accessoryWarehouse`, `accessoryStorageBin`, `accessoryUom`, and 9 report screens.
**Filter scopes: 25+** `ACCESSORY_*` blocks in `filterUtils.ts` (`:1624-2269`).

#### What it does well

- **Grid/filter/export/report machinery is complete and standards-compliant.** DB-level pagination,
  `SqlSortBuilder` whitelists, filter-aware statistics, branch-scoped queries
  (`StockReportQueryService.java:516`), 11 reports with summary cards computed over the whole filtered set.
- **Bin-level granularity exists in the schema**, and the stock-level unique index correctly treats
  `bin`/`batch`/`serial` as part of the identity via `COALESCE` (`V30130:39-46`).
- **Negative stock is guarded in two of three write paths** with a clear error
  (`StockAdjustmentService.java:394-399`, `InventoryStockAdjustmentService.java:66-72`).
- **A configurable enforcement switch** exists: `ACCESSORIES_ENFORCE_STOCK_VALIDATION`
  (`AccessoryStockEnforcementSettingService.java:17,31`) lets an install choose "block" vs "issue and mark
  PENDING". That is a genuinely good product decision worth keeping.
- **Receipt edit/deactivate/reactivate reverses and re-applies stock** (`StockReceiptService.java:373-420`) —
  most modules would just soft-delete and leave the balance wrong.

#### What it structurally cannot do

| # | Missing capability | Evidence |
|---|---|---|
| 1 | **There is no double-sided stock ledger.** `accessory_inventory_transactions` has a single `quantity` and *optional* from/to warehouses. It is a log written *next to* an in-place update of `accessory_stock_levels`, not the source of the balance. Nothing recomputes the balance from movements, and nothing reconciles them | balance writes at `StockReceiptService.java:347`, `:406`; `StockAdjustmentService.java:401`; entity helpers `StockLevel.addQuantity/removeQuantity` `:170-186` |
| 2 | **Some balance changes write no movement at all.** `reverseStockLevel()` subtracts the receipt quantity and recomputes average cost, and inserts **no** `InventoryTransaction`. The ledger silently disagrees with the balance from that moment on | `StockReceiptService.java:373-411` |
| 3 | **Reservations do not exist.** `quantity_reserved` is read in 7 places and **written in none**. `StockLevel.reserveQuantity()` / `releaseReservedQuantity()` have **zero call sites**. `quantity_available` is therefore always equal to `quantity_on_hand` | `grep -rn "reserveQuantity\|releaseReservedQuantity" accessories/backend/src/main/java` excluding the entity → 0 hits. Entity `:189-206` |
| 4 | **Physical counting never posts.** `generateAdjustments()` validates, sets `count.setStatus("POSTED")`, saves, logs — and creates no adjustment, no stock-level write and no transaction. `InventoryCountService` contains **zero** references to `StockLevel` | `InventoryCountService.java:322-345`; `grep -c "StockLevel" InventoryCountService.java` → 0 |
| 5 | **No UoM conversion is ever applied.** `conversion_factor` appears only in `Uom.java`, `UomRequest`, `UomResponse`, `UomMapper`, `UomExportService`. `accessory_stock_levels` has **no UoM column at all**; `accessory_inventory_transactions.uom_id` is nullable and never used in arithmetic. All stock is in one implicit unit | `V30013:13-14`; `grep -rln conversionFactor` → 5 files, all display/CRUD |
| 6 | **Valuation is a single moving-average number on the balance row, with no cost layers.** No FIFO/LIFO, no as-at-date valuation, no revaluation. The reversal path recomputes the average by *subtracting the reversed receipt's own cost*, which is not the inverse of a weighted average and drifts | `StockReceiptService.java:346-364` (forward), `:386-408` (reverse) |
| 7 | **The valuation report does not use the average cost it maintains.** Default sort and value are `quantity_on_hand * last_cost`, while the receipt path maintains `average_cost` | `StockReportQueryService.java:543` |
| 8 | **Lots and serials are strings on the balance row, not entities.** No lot master, no serial master, no genealogy, no split/merge, no per-lot attributes beyond `expiry_date`. A serial number is not unique anywhere — it is part of a composite index alongside `batch_number` | `V30130:17-19`, `:39-46` |
| 9 | **No concurrency control on the balance row.** `StockLevel` has no `@Version`; `StockLevelRepository` declares no `@Lock`; the DB has **no `CHECK (quantity_on_hand >= 0)`**. The guard is a Java read-compare-write | entity `:35-68`; repository `:23-88`; `grep quantity_on_hand … | grep -i check` → 0 hits |
| 10 | **Issuing against a product with no stock-level row silently succeeds.** `issueStock()` returns early with a `logger.warn` — no deduction, no transaction, no error to the caller | `InventoryStockAdjustmentService.java:56-60` |
| 11 | **Issuance swallows non-business exceptions.** `catch (Exception e) { logger.warn("Stock adjustment failed for product {}, continuing", …); }` — a DB error during deduction lets the issuance complete with stock unchanged | `AccessoryIssuanceService.java:275-278` |
| 12 | **Issuance is bin-blind.** `issueStock()` uses `findByProductAndWarehouse`, so with bin-level rows present the deduction hits an arbitrary row or none | `InventoryStockAdjustmentService.java:51-53` |
| 13 | **No supplier, anywhere in receiving.** `StockReceiptRequest` has 10 fields: product, warehouse, bin, quantity, unitCost, referenceNumber, batch, serial, expiry, notes. There is no vendor id, no vendor name, no PO | `dto/request/inventory/StockReceiptRequest.java:23-51` |
| 14 | **No purchase order, no ASN, no GRN, no QC, no putaway, no wave, no pick/pack/ship, no kitting, no RMA, no replenishment, no cycle-count scheduling, no slotting, no labour, no dock/yard** | absence: no such table in the 71-table list |
| 15 | **No cross-warehouse "in transit" state.** `StockTransferService` removes from source and adds to destination — the goods are never *in transit*, so a two-step transfer is not modelled | `StockTransferService.java:502-544` (out), `:561-591` (in) |
| 16 | **Bins have `max_weight`/`max_volume` and warehouses have `capacity`, none of which is enforced** | `V30033:23-24`, `V30017:19`; no validation service reads them |

#### The concrete cost of "permanently separate"

- **Two item masters.** `accessory_products` is the only SKU master; `warehouse-base` will own a second one.
  An install running both has two records for the same physical part, two SKU codes, two UoM tables
  (`accessory_uom` + `wh_uom`), two warehouse masters, two bin masters.
- **Two stock truths, no reconciliation.** Nothing can answer "how much of part X do we hold" across both.
- **Reports cannot be unified.** The 11 accessories reports all read `accessory_stock_levels` directly
  (`StockReportQueryService` injects `StockLevelRepository`). A warehouse report cannot union them without a
  compile-time dependency on accessories.
- **Duplication surface, counted:** 17 tables, 71 backend files, ~12 web routes, 11 reports, 33 mobile screens,
  25+ filter scopes, 12 permission resources.
- **Nothing is reusable as a library.** None of it is behind an interface, none is in a shared artifact, and
  `StockLevel`/`InventoryTransaction` are FK-bound to `accessory_products`, `accessory_warehouses`,
  `accessory_storage_bins`, `accessory_uom`. Extraction is a rewrite, not a refactor.
- **What the decision *buys*:** accessories keeps shipping. There is no migration, no data move, no regression
  risk to a live vertical. Given items 1–16 above, warehouse would not inherit anything worth keeping anyway.
  **The decision is right; it is the duplication that must be budgeted, not re-litigated.**

### 5.2 Dealer PDI — a serialised, one-unit-per-row inventory (26 `pdi_*` tables)

| Table | Created by | Shape |
|---|---|---|
| `pdi_stock_yards` | `V20078` | Yard master (+ `pdi_stock_yard_branches`, `_companies`, `_employee_assignments`) |
| `pdi_yard_storage_locations` | `V20080:4` | `yard_id`, `location_code`, `location_type ('BAY','PARKING_SLOT','COVERED_AREA','OPEN_AREA','WASHING_BAY')`, `bay_number/row_number/slot_number/floor_number/zone`, `capacity INTEGER DEFAULT 1`, `current_occupancy INTEGER DEFAULT 0`, `is_covered`, `has_charging_point`, physical dimensions |
| `pdi_storage_slot_assignments` | `V20735:10` | **The best occupancy model in the repo.** Append-only: released rows keep `released_at` and stay forever (`:8`). `CREATE UNIQUE INDEX uk_slot_active_index ON (storage_location_id, slot_index) WHERE released_at IS NULL AND slot_index IS NOT NULL` `:57-59`; `uk_slot_active_vehicle ON (pdi_vehicle_id) WHERE released_at IS NULL` `:62-64`; partial index for occupancy lookups `:67-69`. Three CHECK constraints enforce the release triple `:43-52` |
| `pdi_vehicle_inventory` | `V20083:4` | One row per chassis. `chassis_number UNIQUE`, model/variant/colour FKs, `current_yard_id`/`current_branch_id`/`storage_location_id`, purchase + entry details, `current_status`, `location_status`, PDI + QC status, damage |
| `pdi_vehicle_movements`, `_locations`, `_status`, `_status_history`, `pdi_movement_*` (approvals, costs, damages, documents, incidents, inspections, locations, timeline) | V20xxx | Full movement workflow with approvals |

**What it does exceptionally well, and warehouse should copy verbatim:**

- **Occupancy is DERIVED, not cached.** `pdi_yard_storage_locations.current_occupancy` exists as a column but
  the code does **not** maintain it — `PdiStockYardMapper.java:83` / `:118`: *"currentOccupancy is no longer set
  manually — it's calculated from storage locations"*, and `PdiYardStorageLocationService.java:67`:
  *"currentOccupancy: count of active (released_at IS NULL) assignments."* This is exactly the
  balance-from-ledger discipline the accessories stock table lacks.
- **Exclusivity is a DB partial unique index, not application logic.** Two concurrent assignments to the same
  slot cannot both commit.
- **History is never deleted.** Release is a column write, not a row delete.

**What it structurally cannot do for warehouse:** it is quantity-free. Every row is one physical serialised
unit. There is no UoM, no cost, no lot, no reservation, no valuation, no partial quantity. It is the right model
for *serial-tracked* warehouse stock and useless for everything else.

### 5.3 Everything else

`grep` for any table containing `stock|inventory|part|spare|consumable|material|warehouse|bin` in
`services`, `field-service`, `assets`, `insurance-360`, `submittals` migrations → **zero hits in all five.**

---

## 6. VERTICALS WITH NO STOCK CAPABILITY — and the concrete integration point

| Vertical | Tables today | What is missing | The concrete call site for the port |
|---|---|---|---|
| **services** (28 tables: `service_entries`, `service_entry_charges`, `service_types`, `service_approvals`, body shop, replacements, fuel fillings, pickup/drop) | No parts table. A job's parts are invisible; `service_entry_charges` is a money line with no stock link | Job parts issue/return, consumables, oil/fluids by volume, warranty parts segregation, core returns | `services/.../service/ServiceEntryService` at the point a charge line is added — call `WarehouseInboundPort.issue(itemId, qty, uom, jobRef)` and hold the returned movement id on the charge row. Reverse on job cancellation |
| **field-service** (15 tables: `service_jobs`, `service_job_assignments`, `job_trips`, `job_track_points`, `customer_machines`, `fs_*` lookups) | No van/boot stock. A technician's stock is not modelled at all. `job_trips` + `job_track_points` already know where the van is | Van as a mobile stock location, truck replenishment, consumption at job close, cycle count of the van, unreturned-parts ageing | `field-service/.../JobTripService` (trip start/end) → warehouse location transfer; `service_jobs` status→`COMPLETED` → issue consumed parts. The van maps to a `wh_location` of type `MOBILE`, owned by the technician's user id |
| **assets** (62 tables: `assets`, `asset_purchase_orders`+`_lines`+`_po_receipts`, `asset_transfers`, `asset_complaints`, `asset_warranty_claims`, `asset_service_contracts`, `asset_vendors`) | No spares/consumables. `asset_po_receipts` receives *assets* (serialised, one per line), not stock | Spare-part stock for maintenance, consumables (filters, belts), parts issued against a complaint, min/max per store | `assets/.../AssetComplaintService` at resolution → issue spares; `asset_po_receipts` is the **model to extend, not reuse** — it has no quantity semantics. Assets already has the vendor master warehouse lacks (§7) |
| **dealer spare parts** (vs vehicles) | `pdi_*` covers vehicles only | An entire spare-parts business: parts master, VOR/emergency orders, OEM parts catalogue, supersessions, returns to OEM | New; nothing to hook. This is the clean-sheet case and the best first vertical for `warehouse` proper |
| **accessories** | Full but structurally limited (§5.1) | — | **Explicitly out of scope by decision.** Do not build an accessories adapter |

---

## 7. PARTY / SUPPLIER REALITY

| Candidate | Where | What it is | Fit |
|---|---|---|---|
| `asset_vendors` | `assets/.../V60056:3-38` | A real vendor master: `name`, `code UNIQUE`, `vendor_type CHECK ('MANUFACTURER','RESELLER','SERVICE_PROVIDER','LEASING_COMPANY','INSURANCE_PROVIDER','OTHER')`, contacts, address, `tax_id`, `payment_term_id → asset_payment_terms`, `credit_limit`, `currency VARCHAR(3) DEFAULT 'USD'`, `rating` | **Right shape, wrong owner.** It is in `assets`, a vertical. `warehouse-base` depending on `assets` inverts the arrows |
| `customers` + `customer_individuals` + `customer_companies` | `automotive/.../V10010:9`, `V10011:10,57` | The shared *customer* party master, with `addresses`, `customer_contacts`, `customer_segments` | **Wrong direction and wrong module.** It models buyers, not suppliers, and `automotive` is a vertical |
| `companies` + `company_contacts` + `company_partnerships` | `automotive/.../V10002:11,75,126` | Legal-entity / OEM master | Same problem: automotive-owned |
| `acc_companies` | `accounting-base/V600001` | Accounting's own book-owning entity, deliberately *not* a vertical's | The precedent: **when a base module needs a party, it creates its own** |
| accessories receiving | — | **No supplier field exists at all** (`StockReceiptRequest.java:23-51`) | Nothing to inherit |

**Conclusion.** There is no shared supplier master and no platform party model. `warehouse-base` must own
`wh_counterparties` (supplier / customer / carrier / 3PL-client, one table with a role flag or a type CHECK),
exactly as `accounting-base` owns `acc_companies`. Adapters then map: `warehouse-adapter-dealer` links a
`wh_counterparty` to an automotive `companies` row; a future `warehouse-adapter-assets` links it to an
`asset_vendors` row. **The adapter carries the FK; the base never does.** `V600001__Create_acc_companies_and_external_refs.sql`
is the copy target — it pairs the owned entity with an `external_refs` table for exactly this mapping.

---

## 8. TRAPS THAT COST A REBUILD CYCLE

| # | Trap | Evidence | What warehouse must do |
|---|---|---|---|
| T-1 | **`cascade = CascadeType.ALL` on a collection resurrects a repository-deleted child.** 105 occurrences repo-wide | e.g. `accessories/.../entity/SalesOrder.java:161,166`, `Product.java:192,197`, `Quotation.java:108` | Never on ledger lines. A `wh_stock_ledger` row must not be reachable through a cascading parent |
| T-2 | **A JPA field initialiser beats the column DEFAULT.** `@Builder.Default private BigDecimal quantityOnHand = BigDecimal.ZERO` writes `0`, so a DB `DEFAULT` is never observed | `accessories/.../entity/StockLevel.java:58-64` | Decide in one place. For quantity columns, initialise in Java and make the DB `NOT NULL` with no default |
| T-3 | **A generated column read through JPA is stale after an in-session write.** `quantity_available` is `@Column(insertable=false, updatable=false)`; after `setQuantityOnHand(...)` the in-memory `quantityAvailable` still holds the pre-write value until a refresh | `StockLevel.java:66-68`; DB side `V30130:14` | Do not expose a generated column on the entity. Compute available in SQL for reads, or `@Formula` |
| T-4 | **Hibernate native-query timestamps come back as any of 4 types.** `OffsetDateTime`, `Instant`, `java.sql.Timestamp`, `LocalDateTime`. Returning null for an unhandled type is silent data loss | the correct handler: `platform/.../service/UserActivityLogQueryService.java:288-307`, which logs a warning on an unknown type | Copy that method verbatim into every `RepositoryCustomImpl` that maps `Object[]` |
| T-5 | **`SqlSortBuilder` whitelist or no sorting.** ORDER BY is never concatenated | `platform/.../util/SqlSortBuilder.java`; use e.g. `getAccessoryInventoryValuationReportFieldMappings()`; a call site `StockReportQueryService.java:541-545` with default `"COALESCE(sl.quantity_on_hand * sl.last_cost, 0) DESC"` | One `get<Wh…>FieldMappings()` per grid, always with a default sort |
| T-6 | **`filterUtils.ts` allowlist — an unlisted field is silently dropped.** 210 scopes today | `platform/frontend/src/utils/filterUtils.ts:346+`; type union `:30` | One scope per warehouse grid. **Use `dateOnly` for `expiry_date`/`count_date`/`manufacture_date`** — `:49-56` documents that `date` moves the lower bound back a day east of UTC |
| T-7 | **An unregistered cache name throws on the FIRST call, not at startup.** 202 names registered | `CacheConfiguration.java:375-376` (the warning), `:101-404` (the list) | Register `statistics.warehouse.<entity>` / `dropdown.warehouse.<entity>`. **And do not register a name for a filter-aware statistics strip** — `:190-196` records that exact mistake (issues neetub1508/classic#790, #791): those names cached nothing while reading as though they did |
| T-8 | **`grid_preferences.default_filters` AND `default_columns` must BOTH be populated.** `filter_definitions.default_visible = true` alone does not build the default filter strip | `V18:12` (`default_columns JSONB NOT NULL DEFAULT '[]'`), `V229:50-51` (`default_filters JSONB`), example `V229:53-55` | Every warehouse grid migration writes both, as `'[…]'::jsonb` |
| T-9 | **`menus` has no unique constraint on `(name, parent_id, menu_level)`, so `ON CONFLICT DO NOTHING` does not stop a duplicate on a Flyway retry** | `assets/.../V60171__Asset_service_contract_permissions_and_menu.sql:154-155` spells it out; the other idiom is `V757:137-165` (`SELECT id INTO … IF NULL THEN INSERT`) | `WHERE NOT EXISTS` on every menu insert, and seed `en`/`fr`/`hi` `menu_translations` |
| T-10 | **`permission_dependencies` is a PLATFORM table.** Creating it defensively from a module migration is a documented false premise | `V248:17-30`; header `:4-13`; the vestigial second creator `dealer/V20501:10` | Insert rows; never `CREATE TABLE`. Columns are `permission_id` / **`dependent_permission_id`** |
| T-11 | **The frontend merge is last-write-wins across the whole `src/` tree.** Modules are `cp -r /tmp/<mod>-src/. ./src/` in a fixed order | `Dockerfile.frontend:80-177` | Every warehouse file name must be globally unique — locales, components, services, types. `wh*`-prefix everything |
| T-12 | **All module migrations are physically flattened into `platform/backend/src/main/resources/db/migration/` at build time.** Two modules with the same version number is a build/startup failure, not a merge | `Dockerfile.backend:140-181` (`cp -v <mod>/.../db/migration/*.sql platform/.../db/migration/`) | This is the mechanical reason C-001 is a blocker |
| T-13 | **No per-module npm manifest.** Only `platform/frontend/package.json` exists (38 dependencies). A module cannot add a library | `ls */frontend/package.json` → 1 file | **There is no decimal library** (no `decimal.js` / `big.js` / `bignumber.js`). Frontend quantity/cost arithmetic is IEEE-754 double. Warehouse must compute **every** quantity, cost and valuation on the backend in `BigDecimal` and send formatted strings |
| T-14 | **The `all_activity_history` view is dealer-owned.** Redefining it from warehouse would create a dealer dependency | `dealer/V20412:354`, `dealer/V20885:85-177`; accessories' explicit opt-out `accessories/V30379:7-9` | Own `wh_activity_history`; stay out of the view |
| T-15 | **`accounting-india` is banded V602000–V602999, *inside* `accounting-base`'s V600000–V609999.** A sub-band carve-out that puts a dependent module's DDL numerically *below* its base's later migrations | `CLAUDE.md` MODULES table; `docker-compose.yml:54` | **Do not copy.** Give each warehouse module a disjoint band: base < app < adapters < 3PL |
| T-16 | **Controllers must live in `ai.<module>.controller…`** or `UserActivityTrackingAspect` cannot see them | pointcut `:59` `within(ai..controller..*)`; module resolution `:167-174` (package segment 2, uppercased) | `ai.warehousebase.controller`, `ai.warehouse.controller`, … Module names will render as `WAREHOUSEBASE` / `WAREHOUSE3PL` in the activity log |
| T-17 | **`BaseExportService` does NOT expose `formatBoolean(Boolean)`** (it is on `BaseController`), and it already renders a raw `Boolean` as Yes/No on every path | CLAUDE.md BACKEND RULES; verified by the absence of the method on `BaseExportService` | Return the raw `Boolean` from `extractRowData` |
| T-18 | **Verify DB column names before writing native SQL.** Known mismatches: `service_entries.entry_status`, `branches.branch_name`, `user_details.employee_id` | CLAUDE.md; `V149:18`; `V169:1` | Applies to every warehouse join onto platform tables |

---

## 9. CONCURRENCY AND CORRECTNESS FOR A STOCK LEDGER

### 9.1 What the codebase gives you

| Mechanism | Precedent | Assessment for warehouse |
|---|---|---|
| **`@Version` optimistic locking** | 18 entities: `accessories/Quotation.java:85`, `QuotationRevision.java:122`, `AccessoryProductDiscount.java:109`, `QuotationStatus.java:55`; `platform/LeaveBalance.java:111`; 10 dealer entities; 6 automotive entities | **Never used on a stock/balance row.** `StockLevel` has none. Available and idiomatic — use it on `wh_stock_balances` |
| **`@Lock(LockModeType.PESSIMISTIC_WRITE)`** | `platform/LeaveRequestRepository.java:29`, `LeaveBalanceRepository.java:27`; assets **6** sequence repositories — `AssetTagSequenceRepository.java:25-27`, `AssetPoSequence…`, `AssetComplaintSequence…`, `AssetClearanceSequence…`, `AssetWarrantyClaimSequence…`, `AssetInsuranceClaimSequence…`, `AssetServiceContractSequence…` | **The gapless-numbering precedent.** `AssetTagSequenceRepository:19-24` documents the exact race: *"two concurrent asset creations in one category read the same value and one of them fails on uk_assets_tag after the counter has already moved"*. Runs in its own `REQUIRES_NEW` transaction |
| **PostgreSQL advisory locks** | 3 sites: `platform/.../service/DocumentFolderService.java:266`, `platform/.../service/GridPreferenceService.java:144`, `services/.../BoomBarrierWebhookService.java:146` — all `SELECT pg_advisory_xact_lock(hashtext(:key))` via `entityManager.createNativeQuery` | **Available and proven.** The right tool for "serialise all movements for item+location" without a row to lock |
| **`SELECT … FOR UPDATE` on a head/counter row** | Specified and reasoned in `accounting-base/V600111:364-386` and `:673-676`; the concrete idiom is the `@Lock(PESSIMISTIC_WRITE)` repositories above | Documented, with the cost stated: *"from its first audit write to COMMIT, a mutating transaction holds this row's lock, so mutating transactions for ONE COMPANY serialise"* |
| **`FOR UPDATE SKIP LOCKED`** | **0 hits** | No precedent. Needed for wave/pick-task claiming — warehouse introduces it |
| **`CREATE CONSTRAINT TRIGGER … DEFERRABLE INITIALLY DEFERRED`** | **`accounting-base/V600111:812-815` and `:838-841`** — and the file says so itself at `:773-775`: *"THIS REPOSITORY HAS NO PRECEDENT FOR `CREATE CONSTRAINT TRIGGER`. 109 migration files use plain CREATE TRIGGER; the count of CREATE CONSTRAINT TRIGGER across the whole repository is ZERO"* (168 distinct `CREATE TRIGGER` names repo-wide today) | **Now there is exactly one precedent, and it is recent and well-documented.** Two PostgreSQL rules it records: a constraint trigger must be `AFTER`, and must be `FOR EACH ROW`. This is the mechanism for "a movement's debit and credit must balance at COMMIT" |
| **Append-only enforced in the database** | `accounting-base/V600111` — `acc_audit_events` with a BEFORE UPDATE OR DELETE reject trigger, a `acc_audit_chain_heads` row created-or-locked via `INSERT … ON CONFLICT DO UPDATE … RETURNING` (`:673-690`), sequence-must-be-head+1, hash recomputed in SQL and cross-checked against the Java writer, plus a verifier that names *"the break between events 59 and 61"* | **The single best template in the repo for `wh_stock_ledger`.** Copy the three-layer structure: service exposes `append()` only, controller exposes `GET` only, database rejects `UPDATE`/`DELETE` |
| **Balance derived from an append-only table, not cached** | `pdi_storage_slot_assignments` (`dealer/V20735`) with partial unique indexes `:57-64`; occupancy computed at read time (`PdiYardStorageLocationService.java:67`, `PdiStockYardMapper.java:83,118`) | **The pattern to follow for on-hand.** If a cached balance is added later it must be rebuildable from the ledger and reconciled by a scheduled job |
| **Balance-cache-with-rebuild** | **0 precedents.** `accessory_stock_levels` is a cache with no rebuild path; `pdi_yard_storage_locations.current_occupancy` is a column deliberately left unmaintained | Warehouse invents this. Budget: the rebuild query, the reconciliation job, the variance report |
| **Gapless numbering** | Two shapes. (a) `SequentialCodeGenerator` (`platform/.../util/SequentialCodeGenerator.java:41-53`) — scan-based, explicitly *not* gapless, races behind a unique constraint. Used by accessories transaction numbers (`InventoryStockAdjustmentService.java:152-159`). (b) assets `*_sequences` + `PESSIMISTIC_WRITE` — gapless, serialising | Use (b). Never (a) for a GRN / pick / ship / adjustment number |
| **Multi-implementation registry (the inbound port)** | `ExportService(List<ExportFormatHandler>)` `:31`; `BoomBarrierWebhookController(List<IBoomBarrierHandler>)` `:44-48`; `AccImportHandlerRegistry(List<AccImportHandler>)` `:36-44` | Use this, **not** the `@Primary` override shape of `AccApprovalGate` (which admits only one implementation) |
| **Single-implementation seam with a documented upgrade path** | `accounting-base/.../service/approval/AccApprovalGate.java` + `PermissionOnlyAccApprovalGate` — interface, default impl, and a header that specifies exactly how a later module adds an `@Primary` replacement without touching a caller | The right shape for warehouse's *approval* seam (write-offs, negative adjustments) |
| **Deferred FK / deferrable unique** | Only in the negative: 4 files record that *"a partial unique index CANNOT be declared DEFERRABLE in PostgreSQL"* — `accounting-base/V600001:150`, `V600004:111`, `V600120:90`, `insurance-360/V120175:35`, `V120180:41`, and each names the consequence: **the write path owes an explicit `flush()`** | Warehouse's "one active reservation per line" style partial unique indexes carry the same obligation |

### 9.2 What is missing and must be built

1. `wh_stock_ledger` as a genuinely append-only, double-sided table with a DB-level UPDATE/DELETE reject trigger.
2. A deferred constraint trigger asserting each movement's debits equal its credits at COMMIT.
3. A `wh_number_series` table + `PESSIMISTIC_WRITE` (or `pg_advisory_xact_lock` + `UPDATE … RETURNING`) generator.
4. A balance cache with a documented rebuild query and a scheduled reconciliation.
5. `FOR UPDATE SKIP LOCKED` task claiming for waves/picks.
6. `CHECK (quantity >= 0)` at the DB level on any balance column — no existing stock table has one.

---

## 10. UNVERIFIED — stated plainly

| Claim | Why not verified | What would verify it |
|---|---|---|
| Flyway's exact error text on a duplicate version across locations (*"Found more than one migration with version X"*) | Requires running Flyway; Docker-only build | `./start.sh --docker` with a deliberately colliding file, or the Flyway 10.4.1 source |
| Whether any *live* database already has V900000+/V910000+ rows renumbered by `fixLegacyMigrationVersions` | Needs a DB query | `SELECT version FROM flyway_schema_history WHERE version::int >= 900000` on the target instance |
| The current runtime value of `chk_global_setting_module` and `chk_module` on any given install | Depends on which modules are enabled and migration order | `SELECT pg_get_constraintdef(oid) FROM pg_constraint WHERE conname IN ('chk_global_setting_module','chk_module')` |
| Free `menus.sort_order` at L1 for a warehouse root node | Static analysis cannot see seeded rows | `SELECT name, sort_order FROM menus WHERE menu_level = 1 ORDER BY sort_order` |
| Whether `enable.warehouse.3pl` relaxed-binds cleanly from `ENABLE_WAREHOUSE_3PL` | No local Spring run | A Docker boot with the flag set, checking the `ModuleImportSelector` log line |
| Whether `accessory_inventory_transactions` rows and `accessory_stock_levels` balances actually agree in production today | Needs data | `SELECT product_id, warehouse_id, SUM(signed_qty) FROM … EXCEPT SELECT …` — but the transaction table has no sign column, which is itself the finding (C-021) |
| Row counts / real-world usage of the 11 accessories reports | Needs a live DB and analytics | — |
| Whether `mobile/src/screens/GenericScreen.tsx` (2 783 lines) gates a warehouse route | Read only the size, not the route chain | Read `GenericScreen.tsx` `routePath.includes(...)` chain |

---

## 11. FINDINGS

| ID | Sev | What is true | Evidence | What it means for the warehouse design | Module | Version |
|---|---|---|---|---|---|---|
| **C-001** | **BLOCKER** | `V900000–V909999` holds **135** OEM-seed migrations and `V910000–V919999` holds **434** per-client migrations, with versions deliberately reused across the 5 client dirs | `dealer/backend/src/main/resources/db/seed/maruti/V900000__maruti_cleanup.sql`; `platform/backend/src/main/resources/db/client/{ktlautomobiles,logix,pasco,platinum,vehicron}/V910001__*.sql`; `FlywayConfiguration.java:151`, `:157`, `:183` | Both proposed bands are unusable. Choose before writing any issue | all | v1 |
| **C-002** | **BLOCKER** | `fixLegacyMigrationVersions` renumbers legacy history into V900000/V910000/V950000 and then `DELETE`s duplicate-version history rows | `FlywayConfiguration.java:296-327`; gated by `flyway.legacy-fix.enabled` default `false` at `:251-252` | A band collision does not fail loudly — it deletes a history row and re-runs a migration | all | v1 |
| **C-003** | **MAJOR** | `V500000–V599999` is entirely free (0 files); so are V100000–V109999, V130000–V599999, V621000–V699999, V710000–V799999, V810000–V899999 | computed band-occupancy table, §3.1 | **Recommend: base `V500000–V509999`, app `V510000–V519999`, adapters `V520000–V529999`, 3PL `V530000–V539999`.** Disjoint, contiguous, ordered, far from the seed region | all | v1 |
| **C-004** | **MINOR** | `accounting-india` is banded `V602000–V602999`, nested inside `accounting-base`'s `V600000–V609999` | `CLAUDE.md` MODULES table; `docker-compose.yml:54` | Do not copy the nesting. Disjoint bands, base lowest | all | v1 |
| **C-005** | **MAJOR** | A new module is **16 files** across 2 build systems + 1 silent runtime gate | §2 table, all rows evidenced | The build-spec's integration chapter is §2 verbatim | all | v1 |
| **C-006** | **MAJOR** | `ModuleImportSelector.java` is the gate that fails silently — no entry means the JAR loads nothing | `ModuleImportSelector.java:52-55`, `:154-186` | 4 constants + 4 blocks, in the P0 bootstrap issue | platform | v1 |
| **C-007** | **MINOR** | `FlywayConfiguration` knows only 6 modules; the last 10 modules added did not touch it | `FlywayConfiguration.java:73-78` | Skipping it is the house style. Do not spend an issue on it | platform | — |
| **C-008** | **MINOR** | `application.yml` `enable:` block lists the same 6; relaxed binding covers the rest | `application.yml:366-373` | No edit needed | platform | — |
| **C-009** | **MAJOR** | `startX2.sh` carries 12 module flags and **no accounting flag** | `startX2.sh:94-97`, `:183-194` | The touchpoint list is not uniformly applied. Decide explicitly for warehouse | shared | v1 |
| **C-010** | **MINOR** | Railway config now carries accounting + doc-ocr-ai but still omits ASSETS, PRODUCT_LIFT, FIELD_SERVICE, SUBMITTALS, INSURANCE_360; frontend var list also drops LEAD_SHARING | `template.conf:39-49`; `setup-railway-client.sh:274-284`, `:421-430` | 12 lines if Railway is in scope; say so explicitly | shared | v1.1 |
| **C-011** | **MAJOR** | `Dockerfile.backend` physically copies every enabled module's migrations into the platform migration directory before the Maven build | `Dockerfile.backend:140-181` | This is the mechanism that makes C-001 fatal rather than cosmetic | shared | v1 |
| **C-012** | **MAJOR** | `Dockerfile.frontend` merges module `src/` trees with `cp -r`, last write wins, order fixed at `:80-177` | `Dockerfile.frontend:80-177` | Every warehouse frontend filename must be globally unique. Prefix `wh` | warehouse | v1 |
| **C-013** | **MINOR** | Only `platform/frontend/package.json` exists (38 deps); no decimal library | `ls */frontend/package.json`; dependency list computed | All quantity/cost/valuation arithmetic on the backend in `BigDecimal`. Frontend renders strings | warehouse | v1 |
| **C-014** | **MAJOR** | `widget_definitions.chk_module` does not allow `'warehouse'`; latest platform assertion is `V557:18` | `V234:36`, `V276:9-10`, `V557:16-18`, `insurance/V50009:7-8` | A widening migration is required before the first warehouse widget. Copy the **merge** idiom of `accounting-base/V600200:56-99` (read the existing list, union, rebuild) — a hardcoded DROP/ADD discards another module's value | warehouse-base | v1 |
| **C-015** | **MINOR** | `global_settings.chk_global_setting_module` **already allows `'WAREHOUSE'`**, added by `platform/V553:14-15` crediting a `V190035 (warehouse-core)` that does not exist here | `V553:1-15`; carried forward by `field-service/V80013:22-25` and `insurance-360/V120122:25-28` | Use `module='WAREHOUSE'` free. Still emit a defensive merge migration in case a later module's hardcoded DROP/ADD omits it | warehouse-base | v1 |
| **C-016** | **MINOR** | `branches.owner_type` and `branches.branch_type` already allow `'WAREHOUSE'`; `branch_type` also allows `'DISTRIBUTION_CENTER'` | `V149:61`, `:63` | Warehouse sites can be platform branches with no schema change. `warehouse-3pl` may need a new `owner_type` value | warehouse-base | v1 |
| **C-017** | **MAJOR** | `permission_dependencies` is a platform table (`V248`), created with `uq_permission_dependency` and `chk_no_self_reference` | `V248:17-30`; header `:4-13`; vestigial `dealer/V20501:10` | Insert rows only. Never `CREATE TABLE` | warehouse-base | v1 |
| **C-018** | **MAJOR** | `documents` has no polymorphic owner; every module builds its own link table | `V81:39-72`; `acc_document_links` `V600110` | Build `wh_document_links`. Use `ON DELETE NO ACTION`, not `CASCADE` — `V600110:104-105` shows the cascade and `V600111:52-58` explains why it is wrong for evidence | warehouse-base | v1 |
| **C-019** | **MAJOR** | No platform number-series table. `SequentialCodeGenerator` is scan-based and explicitly not gapless | `SequentialCodeGenerator.java:9-19`, `:41-53`; the gapless precedent `assets/V60014:2-9` + `AssetTagSequenceRepository.java:19-27` | `warehouse-base` owns `wh_number_series` with a locked counter row. GRN/pick/ship/adjustment numbers must be gapless | warehouse-base | v1 |
| **C-020** | **MAJOR** | No generic backend import framework. Best shape is `AccImportHandlerRegistry` + `acc_import_batches`/`_rows` + a reversal path | `AccImportHandlerRegistry.java:36-44`; `V600120`; `AccImportBatchReverseModal.tsx` | Copy it for item master, opening stock and ASN import | warehouse-base | v1 |
| **C-021** | **BLOCKER** (for the design, not the build) | Accessories has **no stock ledger**: `accessory_inventory_transactions` is a single-sided log written next to an in-place-mutated balance row, and some balance changes (receipt reversal) write no movement at all | balance writes `StockReceiptService.java:347,406`; `StockAdjustmentService.java:401`; reversal with no transaction `StockReceiptService.java:373-411`; entity helpers `StockLevel.java:170-186` | Warehouse's central design decision: **balance is derived from an append-only ledger**, never mutated in place. This is the thing accessories got wrong and the reason a new module is justified | warehouse-base | v1 |
| **C-022** | **BLOCKER** (design) | Reservations are schema-only. `quantity_reserved` is read in 7 places, written in 0. `StockLevel.reserveQuantity()` / `releaseReservedQuantity()` have zero call sites | `StockLevel.java:189-206`; `grep -rn "reserveQuantity\|releaseReservedQuantity" accessories/backend/src/main/java` excl. entity → 0 | Reservations/allocations are net-new in warehouse. Do not assume any prior art exists | warehouse-base | v1 |
| **C-023** | **BLOCKER** (design) | Physical counts never post. `generateAdjustments()` sets `status='POSTED'` and creates nothing; `InventoryCountService` has 0 references to `StockLevel` | `InventoryCountService.java:322-345` | Cycle/physical count posting is net-new. Budget it as a full workflow, not a port | warehouse | v1 |
| **C-024** | **MAJOR** | No concurrency control on stock: `StockLevel` has no `@Version`, `StockLevelRepository` no `@Lock`, and there is **no `CHECK (quantity_on_hand >= 0)`** in any migration. The negative guard is a Java read-compare-write, and the code comment names the race | entity `:35-68`; repo `:23-88`; `InventoryStockAdjustmentService.java:63-72` ("this only fires when that check raced against another movement") | `wh_stock_balances` needs `@Version` **and** a DB CHECK **and** a lock ordering discipline. All three | warehouse-base | v1 |
| **C-025** | **MAJOR** | `issueStock()` silently no-ops when no stock-level row exists; `AccessoryIssuanceService` swallows non-`BusinessException` failures and continues | `InventoryStockAdjustmentService.java:56-60`; `AccessoryIssuanceService.java:275-278` | A ledger port must never return quietly. Every refusal is an exception; every success returns a movement id the caller stores | warehouse-base | v1 |
| **C-026** | **MAJOR** | UoM conversion is never applied. `conversion_factor` appears only in entity/DTO/mapper/export. `accessory_stock_levels` has no UoM column; `accessory_inventory_transactions.uom_id` is nullable and unused in arithmetic | `V30013:13-14`; `grep -rln conversionFactor` → 5 display-only files; `V30130` has no uom column | UoM + conversions are net-new and belong in `warehouse-base` **from v1** — retrofitting a stocking unit is a data migration | warehouse-base | v1 |
| **C-027** | **MAJOR** | Valuation is one moving-average number on the balance row. No cost layers, no FIFO/LIFO, no as-at-date. The reversal recomputes the average by subtracting the reversed receipt's own cost. The valuation report uses `last_cost`, not `average_cost` | `StockReceiptService.java:346-364`, `:386-408`; `StockReportQueryService.java:543` | Cost layers (`wh_cost_layers`) are v1 if COGS is v1; otherwise the same drift arrives | warehouse | v1 |
| **C-028** | **MAJOR** | Lots and serials are `VARCHAR` columns on the balance row, part of a composite index. No lot entity, no serial entity, no genealogy, no uniqueness | `V30130:17-19`, `:39-46` | Real lot/serial entities in `warehouse-base`. Serial uniqueness is a global constraint, not a composite-index fragment | warehouse-base | v1 |
| **C-029** | **MINOR** | Bins are flat: `zone`/`aisle`/`rack`/`level` are free-text VARCHARs on `accessory_storage_bins`; no zone entity; `max_weight`/`max_volume`/`capacity` are stored and never enforced | `V30033:16-24`; `V30017:19` | Warehouse needs a real location hierarchy (site→zone→aisle→bay→level→bin) with enforced capacity | warehouse-base | v1 |
| **C-030** | **MINOR** | `accessory_warehouses` has no `branch_id`; the link is the `accessory_warehouse_branch` junction | `V30017:8-31` | Decide once: a warehouse site **is** a platform branch (C-016 makes this free) or references one. Do not repeat the junction | warehouse-base | v1 |
| **C-031** | **MAJOR** | Accessories receiving has **no supplier field at all** — 10 fields, none a vendor | `StockReceiptRequest.java:23-51`; `accessory_inventory_transactions` has no vendor column | Inbound in warehouse needs a counterparty from day one, or GRNs cannot be traced to a shipper | warehouse-base | v1 |
| **C-032** | **MAJOR** | "Permanently separate" duplicates 17 tables, 71 backend files, ~12 web routes, 11 reports, 33 mobile screens, 25+ filter scopes, 12 permission resources — and none of the accessories code is extractable (FK-bound to `accessory_*`, no interfaces, no shared artifact) | counts computed; `StockLevel` FKs `V30130:33-36` | The decision is sound. The **budget** must carry a second item master, a second UoM table and no cross-vertical stock report — say so in the FRD rather than letting it surface later | warehouse | v1 |
| **C-033** | **MAJOR** | `pdi_storage_slot_assignments` is the repo's best occupancy model: append-only, released rows retained, exclusivity via **partial unique indexes**, occupancy **derived** at read time and deliberately not cached | `dealer/V20735:8`, `:43-52`, `:57-69`; `PdiYardStorageLocationService.java:67`; `PdiStockYardMapper.java:83,118` | Copy this shape for `wh_location_occupancy` and for any "one active X" invariant | warehouse-base | v1 |
| **C-034** | **MAJOR** | `services`, `field-service`, `assets`, `insurance-360`, `submittals` contain **zero** stock/parts/consumable tables | table enumerations, §5.3 | Warehouse is the only path. §6 names the concrete call sites | adapters | v1.1–v2 |
| **C-035** | **MAJOR** | No shared supplier/party master. `asset_vendors` is assets-owned (`V60056:3-38`), automotive `customers`/`companies` are automotive-owned and model buyers/OEMs | `V60056`, `automotive/V10002:11`, `V10010:9` | `warehouse-base` owns `wh_counterparties` + an external-refs table; adapters carry the FK to a vertical's party. Copy `accounting-base/V600001` | warehouse-base | v1 |
| **C-036** | **MAJOR** | 18 named traps, each with `file:line` | §8 | Fold into the build spec's per-screen obligations | all | v1 |
| **C-037** | **MAJOR** | `CREATE CONSTRAINT TRIGGER … DEFERRABLE INITIALLY DEFERRED` exists in exactly **one** place, added recently, with the PostgreSQL rules recorded (must be `AFTER`, must be `FOR EACH ROW`) | `accounting-base/V600111:773-786`, `:812-815`, `:838-841` | The mechanism for "a movement balances at COMMIT". Precedent now exists — use it | warehouse-base | v1 |
| **C-038** | **MAJOR** | A three-layer append-only design (service `append()` only, controller `GET` only, DB rejects UPDATE/DELETE) with a hash chain, a locked head row, an in-SQL hash recomputation and a gap-naming verifier | `accounting-base/V600111` throughout; `:38-44`, `:364-386`, `:660-690` | The template for `wh_stock_ledger`. Warehouse likely does not need the hash chain, but needs every other layer | warehouse-base | v1 |
| **C-039** | **MAJOR** | The multi-implementation port shape is settled: `List<T>` bean-collection registries in 3 places | `ExportService.java:31`; `BoomBarrierWebhookController.java:44-48`; `AccImportHandlerRegistry.java:36-44` | The generic inbound movement port is `List<WhInboundMovementHandler>` keyed by source type — **not** `@Primary`, which admits only one | warehouse-base | v1 |
| **C-040** | **MINOR** | Advisory locks are used in 3 places; `FOR UPDATE SKIP LOCKED` in **0** | `DocumentFolderService.java:266`; `GridPreferenceService.java:144`; `services/BoomBarrierWebhookService.java:146` | Advisory locks are safe to use. Task claiming for waves/picks introduces `SKIP LOCKED` — flag it as new | warehouse | v2 |
| **C-041** | **MINOR** | Per-module `ArchitectureInvariantsTest` is now house style — accounting-base and accounting each ship a 660-line ratchet including self-tests that the scanners are not passing vacuously | `accounting-base/backend/src/test/java/ai/accountingbase/architecture/ArchitectureInvariantsTest.java:64-350` | One per warehouse module, in the bootstrap issue | all | v1 |
| **C-042** | **MINOR** | 210 filter scopes in `filterUtils.ts`; 202 cache names in `CacheConfiguration`; `dateOnly` is a distinct type from `date` and matters for DATE columns | `filterUtils.ts:30`, `:49-56`, `:346+`; `CacheConfiguration.java:101-404`, `:375-376` | Every warehouse grid adds a scope; expiry/count/manufacture dates use `dateOnly` | warehouse | v1 |
| **C-043** | **MINOR** | Filter-aware statistics must **not** be given a `statistics.*` cache name — the repo records that exact mistake | `CacheConfiguration.java:190-196` (issues neetub1508/classic#790, #791) | Warehouse statistics strips are filter-aware ⇒ no cache name for them. `dropdown.*` names are fine | warehouse | v1 |
| **C-044** | **MINOR** | CLAUDE.md's "`EntityListScreen` additionalFilters only supports dropdowns" is stale — `type?: 'dropdown' \| 'text'` is supported; **date filters still are not** | `mobile/src/components/common/ListHeader.tsx:210-218` | Mobile warehouse screens can carry text filters. Date-range filtering on mobile still needs `EntityListScreen` work | mobile | v1.1 |
| **C-045** | **MINOR** | Accessories' most transferable *product* idea: a global setting that chooses "block issuance on insufficient stock" vs "issue and mark PENDING", plus an `accessory_insufficient_stock_logs` table and a report | `AccessoryStockEnforcementSettingService.java:17,31`; `AccessoryIssuanceService.java:101`; `accessory_insufficient_stock_logs` | Warehouse should ship the same switch (`WAREHOUSE_ALLOW_NEGATIVE_STOCK`) with the log and the report. Copy the idea, not the code | warehouse | v1 |
| **C-046** | **MINOR** | Effective Docker Flyway default is `out-of-order: false` (compose overrides `application.yml`), flipped to `true` only by `--restore-backup` and persisted to `.env` | `application.yml:105` vs `docker-compose.yml:88`, `:183`; `start.sh:48`, `:367`, `:784-785` | "Standalone first, verticals later" requires `FLYWAY_OUT_OF_ORDER=true` at the upgrade. Document it as a required step, not a surprise | shared | v1 |
| **C-047** | **MINOR** | Any Flyway failure triggers a blind `flyway.repair()` + one retry | `FlywayConfiguration.java:246-264` | Every warehouse migration must be individually idempotent (`IF NOT EXISTS` / `ON CONFLICT` / `WHERE NOT EXISTS`), as accounting-base's are | all | v1 |
| **C-048** | **MINOR** | The `all_activity_history` view is dealer-owned; accessories explicitly declined to join it | `dealer/V20412:354`, `dealer/V20885:85-177`; `accessories/V30379:7-9` | Own `wh_activity_history`; do not touch the dealer view | warehouse-base | v1 |
| **C-049** | **MINOR** | `UserActivityTrackingAspect` derives the module from package segment 2 and requires controllers under `ai.<module>.controller…` | `UserActivityTrackingAspect.java:59`, `:167-181` | Package layout is a functional requirement, not a style preference. `WAREHOUSEBASE` / `WAREHOUSE` / `WAREHOUSE3PL` will be the recorded module names | all | v1 |
| **C-050** | **MINOR** | Accounting ships `en` + `fr` + `hi` locale JSONs; older modules ship `en` only | `accounting-base/frontend/src/i18n/locales/{en,fr,hi}/accountingBase.json` | Follow accounting: three locales, and seed `menu_translations` for all three | warehouse | v1 |

---

## 12. THE ONE RECOMMENDATION THAT CHANGES THE MOST

**Change the Flyway bands before anything else is written.**

```
warehouse-base            V500000 – V509999
warehouse                 V510000 – V519999
warehouse-adapter-<v>     V520000 – V529999   (one 1000-wide sub-band per adapter: dealer V520000-520999,
                                               services V521000-521999, field-service V522000-522999,
                                               assets V523000-523999, logistics V524000-524999)
warehouse-3pl             V530000 – V539999
```

Every one of those numbers is unoccupied today (0 files in V130000–V599999), the four bands are disjoint and
ordered base→app→adapter→3PL so a partial install always migrates in dependency order, and none of them is
within reach of `FlywayConfiguration`'s `+830000` / `+860000` legacy renumber. The proposed
V900000/V910000/V920000/V930000 scheme fails on the first two of those three tests.
