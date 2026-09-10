# Module integration runbook — landing five warehouse modules in `classic`

<!-- check-design-set: issue-citations file #2 #791 — `#2` and `#9` are ordinals in prose, not issue references — *Refusal #2*, *Adapter #2 (services)*, *ship-blocker #2*, *logistics needs #1, #2, #3, #5, #6, #10* — and at COMPETITOR-BENCHMARK.md:70/:146 `#9` is the markdown in-page anchor `[§9](#9--where-the-audits-disagree)`. In this repository `#2` and `#9` are in fact the two **pull requests** opened while the backlog was being filed, so no issue row can ever exist for either: see issues/CREATED.md. And `#790` and `#791` are issues in **`neetub1508/classic`**, cited as `classic#790, #791` with the second elided in the ordinary English way. The first resolves; the elided continuation reads to the checker as a bare `#NN`. It is a cross-repo citation, never a warehouse issue -->

> **What this document is.** A runbook an engineer executes, top to bottom, to land
> `warehouse-base`, `warehouse`, `warehouse-adapter-<vertical>`, `warehouse-3pl` and `warehouse-india`
> in the `neetub1508/classic` monorepo. It is not a description of the build system. Every row names
> a file, what to add to it, the accounting equivalent at `file:line`, and whether missing it fails
> the build, fails at runtime, or is documentation.
>
> **Authority.** [`DECISIONS.md`](DECISIONS.md) wins on module names, packages, Flyway bands, table
> prefixes and the version ladder. [`reviews/R1-codebase-reality.md`](reviews/R1-codebase-reality.md)
> wins on what the existing codebase does. This document extends R1 §2 into something executable and
> corrects it where re-verification found it stale — those corrections are §1.
>
> **Method.** Reading and `grep` only, against `/Users/bbhushan/work/git/workspace/classic`,
> 2026-09-01. No `mvn` / `npm` / `tsc` was run — this project builds only in Docker (CLAUDE.md,
> *Build & run = Docker ONLY*). Every count below was computed with the command printed beside it.
> Anything not verified is marked **UNVERIFIED** with the command that would settle it.
>
> **The asset this document is built on.** Accounting has already landed **four** modules in this
> checkout — `accounting-base/`, `accounting/`, `accounting-adapter-dealer/`, `accounting-india/` —
> and is wired through every touchpoint. Warehouse is the same job with five modules, one of which
> (`warehouse-india`) is a direct analogue of `accounting-india`. **Copy the real files. Do not
> invent a second pattern.**

---

## 0. The five modules, at a glance

| Module | Java package | Depends on | Flyway band (D-2) | Table prefix (D-3) | Env flag | Spring property | Maven profile | Frontend? |
|---|---|---|---|---|---|---|---|---|
| `warehouse-base` | `ai.warehousebase` | platform only | **V500000–V509999** | `whb_` | `ENABLE_WAREHOUSE_BASE` | `enable.warehouse.base` | `with-warehouse-base` | **yes** (v1) |
| `warehouse` | `ai.warehouse` | platform + base | **V510000–V519999** | `wh_` | `ENABLE_WAREHOUSE` | `enable.warehouse` | `with-warehouse` | **yes** (v1) |
| `warehouse-adapter-dealer` | `ai.warehouseadapterdealer` | platform + base + automotive + dealer | **V520000–V520999** | `whad_` | `ENABLE_WAREHOUSE_ADAPTER_DEALER` | `enable.warehouse.adapter.dealer` | `with-warehouse-dealer` | no (v1) |
| `warehouse-adapter-services` | `ai.warehouseadapterservices` | platform + base + automotive + services | **V521000–V521999** | `whas_` | `ENABLE_WAREHOUSE_ADAPTER_SERVICES` | `enable.warehouse.adapter.services` | `with-warehouse-services` | no (v1) |
| `warehouse-3pl` | `ai.warehouse3pl` | platform + base + `warehouse` | **V530000–V539999** | `wh3_` | `ENABLE_WAREHOUSE_3PL` | `enable.warehouse.3pl` | `with-warehouse-3pl` | **yes** (v2, client portal) |
| `warehouse-india` | `ai.warehouseindia` | platform + base + `warehouse` | **V540000–V549999** | `whin_` | `ENABLE_WAREHOUSE_INDIA` | `enable.warehouse.india` | **yes** (v2, e-way bill / challan screens) |

D-1 lists five *kinds* of module; `warehouse-adapter-*` is one kind with one instance per vertical,
and D-11 puts **two** adapters (dealer, services) in v1 because one adapter proves nothing about
genericity. So the v1 landing is **four Maven modules** (base, app, two adapters) and the v2 landing
adds **two more** (3PL, India). Every table in this runbook carries all six columns so the v2 work is
already specified.

**Adapters are backend-only, exactly as `accounting-adapter-dealer` and `accounting-india` are** —
`shared/docker/Dockerfile.frontend:71` states it in a comment and the repo confirms it:

```bash
ls -d accounting-*/ accounting/*                 # → accounting-adapter-dealer/backend only; no frontend/
```

If an adapter ever needs a screen it becomes frontend-bearing and costs, in one change: 8
`tsconfig.json` aliases, a `<Mod>SafeTranslation.tsx`, three locale JSONs, a `Dockerfile.frontend`
`COPY` + merge block, a `jest.config.js` `roots`/`testMatch` pair, and a `NEXT_PUBLIC_*` env. Decide
per adapter, before it is scaffolded; R7 `B10` says an adapter must not ship a screen that duplicates
a base grid, which is the usual reason it does not need one.

### Free-band proof (D-2)

```bash
# from the classic repo root; excludes build output, which duplicates every file
find . -name "V*__*.sql" -not -path "./node_modules/*" -not -path "*/target/*" \
  | sed -E 's|.*/V([0-9]+)(_[0-9]+)?__.*|\1|' | grep -E '^[0-9]+$' \
  | awk '{if($1>=130000 && $1<=599999) c++} END{print c+0}'
```

→ **0**, computed 2026-09-01. The same command bounded to `500000..549999` also returns **0**. For
contrast, the bands the original brief proposed are occupied: `V90xxxx` → **135**, `V91xxxx` → **434**,
`V95xxxx` → **32** (same `find`, globbed by band). That is why D-2 moved them.

> **The `-not -path "*/target/*"` is load-bearing.** Without it the V91xxxx count comes back as
> **871**, because `platform/backend/target/classes/db/client/` holds a compiled copy of every client
> migration. R1's 434 is the correct figure; a count that includes `target/` is double.

---

## 1. Corrections to R1 §2, found by re-verification

R1 §2 is the source this runbook extends. Four of its rows moved or were incomplete. Each correction
below carries the evidence.

| # | R1 said | Verified reality (2026-09-01) | Consequence for warehouse |
|---|---|---|---|
| **MI-1** | "A new module is **16 files**" (`C-005`, `AF-6`) | **18.** Two touchpoints are missing from the list: `platform/frontend/jest.config.js` (`:54-61` `roots`, `:69-82` `testMatch`) and `.github/workflows/tests.yml` (`:259-408`, the `accounting-ratchets` job). The jest file states the hazard itself at `:45-47`: *"a module absent from BOTH lists has its suites silently ignored — a test file can be written, committed and never run"* | Two more rows, both **B**. See §13 |
| **MI-2** | "the existing ratchets are `continue-on-error` in CI" | **Half true, and the half that matters is false.** `tests.yml:97` and `:201` carry `continue-on-error` on the *frontend* and *backend* jobs. The `accounting-ratchets` job (`:259`) does **not** — and `:308-321` says so explicitly: *"Step 2 of 2 — THE GATE. Deliberately NOT `continue-on-error`."* It is followed by an anti-vacuous assertion (`:334-379`) that fails the job if surefire ran zero tests or if the `ScannerIntegrity` nested suite is missing | Warehouse gets its own blocking job on the same shape. Copy `tests.yml:259-408` and re-scope `-pl`. See §13.3 |
| **MI-3** | "mirror `automotive/backend/pom.xml` (base shape)" citing `:8-33` | Copying only `:8-33` yields parent + `platform-backend` + lombok and **nothing else** — no test dependencies, no `maven-compiler-plugin` annotation-processor path, no `maven-surefire-plugin`. Two live modules took exactly that shortcut: `assets/backend/pom.xml` and `product-lift/backend/pom.xml` are **62 lines each** and carry none of the three. `doc-ocr-ai/backend/pom.xml` (121 lines) has the test deps but no surefire | **Copy the whole 160-line file.** See §4 |
| **MI-4** | `branches.owner_type` already allows `'WAREHOUSE'` (`C-016`) | **The column no longer exists.** `platform/…/V160__Remove_owner_fields_from_branches.sql:13,16` drops `owner_type` and `owner_id`; `:7` drops `uk_branches_owner_code`; `:19` replaces it with `uk_branches_code UNIQUE (branch_code)` — branch codes are now **globally unique**. `branch_type`'s CHECK survives and still admits `'WAREHOUSE'` and `'DISTRIBUTION_CENTER'` (`V149:61`) | Half of C-016 holds, half is void. Full treatment in [`PLATFORM-DEPENDENCIES.md`](PLATFORM-DEPENDENCIES.md) §2 |

Counts that moved since R1 was written (the tree moves under you — see the repo's own history):
`filterUtils.ts` scopes **210 → 211**; `CacheConfiguration` cache names **202 → 230**; total versioned
migration files **3 297 → 3 300**. Commands for all three are in §16.

---

## 2. The complete touchpoint matrix

**Legend.** **B** = build-time gate — miss it and the build fails, or the JAR/source is *silently
omitted*. **R** = runtime gate — the build succeeds and the module is inert or 500s at first use.
**D** = documentation, no functional effect.

The three that fail **silently** are marked ⚠. They are the ones that cost a rebuild cycle:
`ModuleImportSelector.java` (JAR on the classpath, nothing loaded), `filterUtils.ts` (filter UI
appears to do nothing), `jest.config.js` (suites written and never run).

| # | File | Kind | `warehouse-base` | `warehouse` | adapters ×2 | `warehouse-3pl` | `warehouse-india` | Accounting evidence |
|---|---|---|---|---|---|---|---|---|
| 1 | `pom.xml` — profiles | **B** | `with-warehouse-base`, 1 module row | `with-warehouse`, base **then** app | `with-warehouse-dealer` = automotive→dealer→base→app→adapter; `with-warehouse-services` = automotive→services→base→app→adapter | `with-warehouse-3pl` = base→app→3pl | `with-warehouse-india` = base→app→india | `pom.xml:219-232`, `:233-246`, `:248-269`, `:270-284` |
| 2 | `pom.xml` — `all-modules` | **B** | 1 row, base first | 1 row | 2 rows | 1 row | 1 row | `pom.xml:286-306` — 16 rows today, counted by `awk 'NR>=287 && NR<=306' pom.xml \| grep -c "<module>"` |
| 3 | `<mod>/backend/pom.xml` | **B** | parent + `platform-backend` + lombok + **full test/compiler/surefire block** | + `warehouse-base-backend` | + `automotive-backend` + the vertical's backend | + `warehouse-backend` | + `warehouse-backend` | `accounting-base/backend/pom.xml:20-33`, `accounting/backend/pom.xml:28-33`, `accounting-adapter-dealer/backend/pom.xml:35-47` |
| 4 | `shared/docker/Dockerfile.backend` — 7 edits | **B** | ✓ | ✓ | ✓ | ✓ | ✓ | `:20-23`, `:42-45`, `:69-72`, `:80-81`, `:145-177`, `:213`, `:273`, `:341-344`, `:431-457`, `:459` |
| 5 | `Dockerfile.backend` — the **assertion block** | **B** | asserted-for | asserted | asserted | asserted | asserted | `:223-255` — four explicit `BUILD FAILED` guards |
| 6 | `shared/docker/Dockerfile.frontend` | **B** | `COPY` + merge + `ENV` | `COPY` + merge + `ENV` | flag `ARG`/`ENV` only, no `COPY` | `COPY` + merge + `ENV` (v2) | `COPY` + merge + `ENV` (v2) | `:41-44`, `:71-73`, `:158-176`, `:177`, `:194-197` |
| 7 | `platform/frontend/tsconfig.json` | **B** | 8 aliases | 8 aliases | — | 8 aliases (v2) | 8 aliases (v2) | `:162-186` (base), `:187-211` (app) |
| 8 | ⚠ `platform/…/config/ModuleImportSelector.java` | **R** | 1 constant + 1 block | 1 + 1 | 2 + 2 | 1 + 1 | 1 + 1 | `:51-54` constants, `:156-186` blocks |
| 9 | `<mod>/…/<Mod>ModuleConfig.java` | **R** | `@ConditionalOnExpression` OR-ing **every** consumer flag | `@ConditionalOnProperty` | `@ConditionalOnProperty` | see §9 caveat | `@ConditionalOnProperty` | `AccountingBaseModuleConfig.java:46-53`, `AccountingModuleConfig.java:51-55`, `AccountingAdapterDealerModuleConfig.java:52-56` |
| 10 | `shared/docker/docker-compose.yml` | **B+R** | 4 places | 4 | 4×2 | 4 | 4 | `:123-126` backend build args, `:148-151` backend env, `:293-296` frontend build args, `:325-328` frontend `NEXT_PUBLIC_*`; band comment `:50-54` |
| 11 | `shared/scripts/start.sh` | **B** | 8 places | 8 | 8×2 | 8 | 8 | `:36-39`, `:132-135`, `:289-303`, `:477-503`, `:775-778`, `:945-948`, `:1101-1120`, `:1562`, `:1810-1813` |
| 12 | `shared/scripts/startX2.sh` | **B**, optional | decide | decide | decide | decide | decide | `:94-97` (12 flags), `:183-194` — **accounting skipped it entirely**. See §15 `AF-4` |
| 13 | `shared/scripts/railway/template.conf` + `setup-railway-client.sh` | **D/B** | 1 key + 2 vars + 1 summary | same | same ×2 | same | same | `template.conf:41-44`; `setup-railway-client.sh:276-279`, `:423-426`, `:574-577` |
| 14 | `<Mod>SafeTranslation.tsx` | **R** | required | required | — | required (v2) | required (v2) | `accounting-base/frontend/src/components/AccountingBaseSafeTranslation.tsx:21-39`; `accounting/frontend/src/components/AccountingSafeTranslation.tsx` |
| 15 | i18n locale JSONs `en`/`fr`/`hi` | **R** | 3 files | 3 files | — | 3 (v2) | 3 (v2) | `accounting-base/frontend/src/i18n/locales/{en,fr,hi}/accountingBase.json`; locale set fixed at `platform/…/constants/I18nConstants.java:28-33` |
| 16 | `platform/…/config/CacheConfiguration.java` | **R** | every `@Cacheable`/`@CacheEvict` name | same | same | same | same | `:101-415`, warning at `:375-377` |
| 17 | ⚠ `platform/frontend/src/utils/filterUtils.ts` | **R** | 1 scope per grid | 1 per grid | 1 per adapter grid | 1 per grid | 1 per grid | `:346` onward; field-type union `:30`; `dateOnly` semantics `:49-56` |
| 18 | `<mod>/backend/src/test/…/ArchitectureInvariantsTest.java` | **B** | 1 per module | 1 | 1 each | 1 | 1 | `accounting-base/backend/src/test/java/ai/accountingbase/architecture/ArchitectureInvariantsTest.java` (660 lines) |
| 19 | ⚠ `platform/frontend/jest.config.js` | **B** | `roots` + 2 `testMatch` | same | — | same (v2) | same (v2) | `:54-61`, `:69-82`; hazard stated at `:45-53` — **MI-1** |
| 20 | `.github/workflows/tests.yml` | **B** | a `warehouse-ratchets` job + a blocking frontend step | same job | same job | same job | same job | `:106-128` (frontend gate), `:259-408` (backend gate) — **MI-1/MI-2** |
| 21 | `CLAUDE.md` MODULES table + SafeTranslation list | **D** | 1 row | 1 row | 2 rows | 1 row | 1 row | `CLAUDE.md:106-123` (18 rows today), `:125` |
| 22 | Widening migration for two platform CHECK constraints | **B/R** | owns it | — | — | — | — | `accounting-base/…/V600200__Allow_accounting_in_platform_module_check_constraints.sql` — see §10 |
| 23 | `mobile/src/navigation/screens/lazyScreens.ts` | **B/R** | one lazy registration per mobile screen | same | — (backend-only) | same (v2) | same (v2) | accounting has no mobile screen; accessories' warehouse list at `:1954-1956` — `RH-008` |
| 24 | `mobile/src/navigation/RootNavigator.tsx` | **B/R** | one route per mobile screen | same | — | same (v2) | same (v2) | the same accessories screen at `:4771` — `RH-008` |
| 25 | `mobile/src/screens/GenericScreen.tsx` — the `routePath.includes(…)` / `menuName ===` chain | **B/R** | one arm per mobile menu route | same | — | same (v2) | same (v2) | `:41-47` are its first arms (2,783 lines); the gate is a **string match**, verified by R23 — it closes `PLATFORM-DEPENDENCIES.md` §7's open row — `RH-008` |
| 26 | `menus` rows with `is_mobile_enabled = true` | **B/R** | the warehouse L1 and its mobile L2 children | its own L2 rows | — | same (v2) | same (v2) | `menuService.ts:303,320` requires it alongside `isActive && isVisible`; column `V199:7` — `RH-008` |
| 27 | Every level-1 menu needs a level-2 child | **B/R** | a warehouse L1 with at least one `is_mobile_enabled` L2 child, seeded **before any mobile task merges** (`P0-01`) | — | — | — | — | `BottomTabNavigator.tsx:516-534` drops an L1 with no L2 children — `RH-008` |

**Twenty-seven touchpoints.** Rows 1–22 land the module in the build and the platform. Rows 23–27
(`RH-008`) make its mobile screens reachable, and each is **B/R**: the app builds, and the screen is
unreachable. `D-13` puts a mobile counterpart in every task that ships a web screen, so the five apply
from the first mobile task; before round 4 this matrix did not contain the word *mobile*. The three
navigation files (rows 23–25) are also in §12.4's platform-file ledger.

**Verified NOT required** (contra a common assumption — R1 `C-007`, `C-008`, and the note under its
§2 table, all re-confirmed):

- `platform/…/config/FlywayConfiguration.java` — knows only six modules (`:74-79`:
  `enable.dealer`, `enable.assets`, `enable.accessories`, `enable.services`, `enable.insurance`,
  `enable.lead.sharing`). The last ten modules added to this repo did not touch it; its `enable.*`
  reads feed console logging only. Adding `enable.warehouse` there is cosmetics.
- `platform/backend/src/main/resources/application.yml` `enable:` block — same six. Spring relaxed
  binding resolves `enable.warehouse` from `ENABLE_WAREHOUSE` with no declaration.
- Any Flyway *location* registration. Module migrations reach `classpath:db/migration` because
  `Dockerfile.backend:145-177` physically `cp`s them into
  `platform/backend/src/main/resources/db/migration/` **before** the Maven build. That flattening is
  the mechanical reason a cross-module version collision is fatal rather than a merge (R1 `C-011`,
  `T-12`).

---

## 3. Maven profiles — the exact shapes, and the ordering that matters

Copy `pom.xml:219-284` and substitute. Two things are not cosmetic:

1. **Base is listed before the app in every profile that needs both.** `pom.xml:242-243` —
   `accounting-base/backend` then `accounting/backend`. Maven's reactor sorts by declared dependency,
   so the order is not strictly required for correctness, but it is what makes a partial reactor
   readable and it is what the Dockerfile assertion block checks for by name.
2. **An adapter profile lists the vertical chain in full.** `pom.xml:261-265` lists five modules —
   `automotive/backend`, `dealer/backend`, `accounting-base/backend`, `accounting/backend`,
   `accounting-adapter-dealer/backend` — with the reason in a comment at `:257-260`: *"The adapter
   compile-depends on automotive-backend and dealer-backend …, so both must be in the reactor or a
   standalone `-Pwith-accounting-dealer` build cannot resolve them."*

```xml
<!-- Warehouse Base (append-only double-sided stock ledger engine, V500000-V509999) -->
<profile>
    <id>with-warehouse-base</id>
    <activation>
        <property><name>enable.warehouse.base</name><value>true</value></property>
    </activation>
    <modules>
        <module>warehouse-base/backend</module>
    </modules>
</profile>

<!-- Warehouse (inventory application screens on top of the ledger, V510000-V519999) -->
<profile>
    <id>with-warehouse</id>
    <activation>
        <property><name>enable.warehouse</name><value>true</value></property>
    </activation>
    <modules>
        <module>warehouse-base/backend</module>
        <module>warehouse/backend</module>
    </modules>
</profile>

<!-- Warehouse Dealer Adapter (dealer spare-parts documents -> movement envelopes; needs dealer at runtime) -->
<profile>
    <id>with-warehouse-dealer</id>
    <activation>
        <property><name>enable.warehouse.adapter.dealer</name><value>true</value></property>
    </activation>
    <modules>
        <!-- The adapter compile-depends on automotive-backend and dealer-backend
             (warehouse-adapter-dealer/backend/pom.xml), so both must be in the reactor
             or a standalone -Pwith-warehouse-dealer build cannot resolve them.
             Mirrors with-accounting-dealer (pom.xml:257-265). -->
        <module>automotive/backend</module>
        <module>dealer/backend</module>
        <module>warehouse-base/backend</module>
        <module>warehouse/backend</module>
        <module>warehouse-adapter-dealer/backend</module>
    </modules>
</profile>

<!-- Warehouse Services Adapter (job-card parts lines -> movement envelopes) -->
<profile>
    <id>with-warehouse-services</id>
    <activation>
        <property><name>enable.warehouse.adapter.services</name><value>true</value></property>
    </activation>
    <modules>
        <module>automotive/backend</module>
        <module>services/backend</module>
        <module>warehouse-base/backend</module>
        <module>warehouse/backend</module>
        <module>warehouse-adapter-services/backend</module>
    </modules>
</profile>

<!-- Warehouse 3PL (owner-of-goods billing, client portal, V530000-V539999) — v2 -->
<profile>
    <id>with-warehouse-3pl</id>
    <activation>
        <property><name>enable.warehouse.3pl</name><value>true</value></property>
    </activation>
    <modules>
        <module>warehouse-base/backend</module>
        <module>warehouse/backend</module>
        <module>warehouse-3pl/backend</module>
    </modules>
</profile>

<!-- Warehouse India statutory pack (e-way bill, challan, ITC-04, Rule 56, V540000-V549999) — v2 -->
<profile>
    <id>with-warehouse-india</id>
    <activation>
        <property><name>enable.warehouse.india</name><value>true</value></property>
    </activation>
    <modules>
        <module>warehouse-base/backend</module>
        <module>warehouse/backend</module>
        <module>warehouse-india/backend</module>
    </modules>
</profile>
```

**`all-modules`** (`pom.xml:286-306`) gains six `<module>` rows, base first, in dependency order:

```xml
<module>warehouse-base/backend</module>
<module>warehouse/backend</module>
<module>warehouse-adapter-dealer/backend</module>
<module>warehouse-adapter-services/backend</module>
<module>warehouse-3pl/backend</module>
<module>warehouse-india/backend</module>
```

`all-modules` is 16 rows today and becomes 22. Verify with:

```bash
awk 'NR>=287 && NR<=306' pom.xml | grep -c "<module>"     # → 16 before the edit
```

> **The `with-accessories` bug the accounting set names — do not repeat it.** A profile that lists a
> consumer without its base compiles against a JAR that the reactor never produced. That is exactly
> what the `Dockerfile.backend` assertion block (§5.2) is there to catch, and it is why every
> warehouse consumer profile above lists `warehouse-base/backend` explicitly rather than relying on
> transitive resolution from the local repository.

---

## 4. `<mod>/backend/pom.xml` — copy the whole file, not the dependency block

**MI-3.** `automotive/backend/pom.xml` is 160 lines. The parent + `platform-backend` + lombok block
is only `:8-33`. The remaining 127 lines are what make the module testable:

| Lines | What | Why it is not optional |
|---|---|---|
| `:35-50` | `spring-boot-starter-test` with `mockito-core` and `byte-buddy` **excluded** | the exclusions are re-added at pinned versions below; without them the transitive versions clash |
| `:52-64` | `mockito-core` + `byte-buddy` at `${mockito.version}` / `${byte-buddy.version}` | — |
| `:66-82` | `spring-security-test`, `testcontainers:junit-jupiter`, `testcontainers:postgresql` | `@WebMvcTest` with `@PreAuthorize` needs the first |
| `:85-95` | `dependencyManagement` pinning lombok `1.18.30` `provided` | — |
| `:99-105` | `spring-boot-maven-plugin` with `<skip>true</skip>` | a module must produce a **plain** JAR, not an executable one, or `PropertiesLauncher` cannot load it from `/app/lib` |
| `:107-121` | `maven-compiler-plugin` with the lombok `annotationProcessorPaths` | without it every `@Getter` is unresolved at compile |
| `:123-135` | `flyway-maven-plugin` with `<location>classpath:db/migration/<module></location>` | standalone `mvn flyway:migrate` only |
| `:137-157` | `maven-surefire-plugin` 3.2.2 with `-Dnet.bytebuddy.experimental=true -XX:+EnableDynamicAgentLoading`, `**/*Test.java` includes, `spring.profiles.active=test` | **without this the module runs no tests at all** |

Evidence that the shortcut is real, and its blast radius:

```bash
for p in */backend/pom.xml; do
  printf "%-45s lines=%-4s starter-test=%s surefire=%s compiler=%s\n" "$p" \
    "$(wc -l < $p)" "$(grep -c spring-boot-starter-test $p)" \
    "$(grep -c maven-surefire-plugin $p)" "$(grep -c maven-compiler-plugin $p)"
done
```

→ `assets/backend/pom.xml` and `product-lift/backend/pom.xml` are **62 lines, 0/0/0**;
`doc-ocr-ai/backend/pom.xml` is **121 lines, 1/0/0**. `tests.yml:250-254` records the same finding
independently: *"assets and product-lift carry neither `spring-boot-starter-test` nor an explicit
`maven-surefire-plugin` … Those three took the abbreviated pom shortcut … so they could not run a
ratchet even if one were written."*

**Every warehouse module pom is a full copy of `accounting-base/backend/pom.xml` (160 lines) with the
`artifactId`, `name`, `description`, Flyway `<location>` and the extra `<dependency>` blocks changed.**

Dependency blocks per module — copy each from its accounting analogue:

| Module | Extra dependencies beyond platform + lombok | Copy from |
|---|---|---|
| `warehouse-base` | none | `accounting-base/backend/pom.xml:20-33` |
| `warehouse` | `warehouse-base-backend` | `accounting/backend/pom.xml:28-33` |
| `warehouse-adapter-dealer` | `warehouse-base-backend`, `automotive-backend`, `dealer-backend` | `accounting-adapter-dealer/backend/pom.xml:28-47` |
| `warehouse-adapter-services` | `warehouse-base-backend`, `automotive-backend`, `services-backend` | same shape |
| `warehouse-3pl` | `warehouse-base-backend`, `warehouse-backend` | `accounting-india/backend/pom.xml` |
| `warehouse-india` | `warehouse-base-backend`, `warehouse-backend` | `accounting-india/backend/pom.xml` |

All module artifacts use `<groupId>ai.platform</groupId>` and `<version>${project.parent.version}</version>`
— see `accounting/backend/pom.xml:29-32`. The `groupId` is `ai.platform` even for
`ai.warehousebase` classes; that is the repo convention, not a mistake.

> **An adapter does NOT depend on `warehouse`.** R7 §4.2/4.3: an adapter depends on `warehouse-base`
> and its vertical, and posts through the port. The *Maven profile* lists `warehouse/backend` so a
> standalone profile build produces a runnable image; the *pom* must not declare it as a dependency,
> or `WarehouseBaseCouplingTest` layer 1 has nothing to protect. Accounting's adapter pom
> (`accounting-adapter-dealer/backend/pom.xml:28-47`) declares `accounting-base-backend` and **not**
> `accounting-backend` — copy that exactly.

---

## 5. `shared/docker/Dockerfile.backend` — seven edits plus the assertion block

### 5.1 The seven edits

| # | Line today | Add |
|---|---|---|
| 1 | `:20-23` (`ARG ENABLE_ACCOUNTING_*=false`) | 6 × `ARG ENABLE_WAREHOUSE_*=false` |
| 2 | `:42-45` (`COPY accounting-*/backend/pom.xml …`) | 6 × `COPY warehouse-*/backend/pom.xml warehouse-*/backend/pom.xml` — the pom-only layer exists so a source change does not invalidate the dependency-download cache |
| 3 | `:69-72` (`COPY accounting-*/backend …`) | 6 × `COPY warehouse-*/backend warehouse-*/backend` |
| 4 | `:80-81` (`NEED_ACCOUNTING=false; NEED_ACCOUNTING_BASE=false;`) | `NEED_WAREHOUSE=false; NEED_WAREHOUSE_BASE=false;` inside the same `RUN set -ex` at `:77` |
| 5 | `:145-177` | one `if` per flag: accumulate `MAVEN_PROFILES`, set `NEED_*`, and `cp -v <mod>/backend/src/main/resources/db/migration/*.sql platform/backend/src/main/resources/db/migration/` |
| 6 | `:213` (`rm -rf …/target …`) | append 6 × `warehouse-*/backend/target` |
| 7 | `:273` (`RUN mkdir -p /build/…/target`) | append 6 × `/build/warehouse-*/backend/target` — this is what lets the `COPY --from=builder` at `:341-344` succeed even when a module was not built |
| 8 | `:341-344` | 6 × `COPY --from=builder /build/warehouse-*/backend/target/ /tmp/warehouse-*-jars/` |
| 9 | `:431-457` | 6 × the `if ls /tmp/<mod>-jars/<artifact>-*.jar … cp … chown … else echo "⨯ … disabled"` block |
| 10 | `:459` (`rm -rf /tmp/*-jars`) | append the 6 `/tmp/warehouse-*-jars` paths |

**The base-migration copy is derived, not flag-driven** — `:171-178` is the shape:

```dockerfile
if [ "$ENABLE_WAREHOUSE" = "true" ]; then \
    echo "=== Warehouse module enabled (migrations copied via NEED_WAREHOUSE below) ===" && \
    MAVEN_PROFILES="${MAVEN_PROFILES}with-warehouse," && \
    NEED_WAREHOUSE=true && \
    NEED_WAREHOUSE_BASE=true; \
fi; \
...
if [ "$NEED_WAREHOUSE_BASE" = "true" ]; then \
    echo "=== Copying warehouse-base migrations to platform BEFORE build ===" && \
    cp -v warehouse-base/backend/src/main/resources/db/migration/*.sql \
          platform/backend/src/main/resources/db/migration/ 2>/dev/null \
       || echo "No warehouse-base migrations to copy"; \
fi; \
```

Enabling an adapter must also force `NEED_DEALER=true` (or `NEED_SERVICES`), exactly as
`:156-163`/`:179-182` do for accounting's dealer adapter: the adapter's Flyway migrations reference
the vertical's tables, so the vertical's migrations must be in the same flattened directory.

### 5.2 The assertion block — copy it, it is the highest-value 30 lines in the file

`Dockerfile.backend:223-255`. Its own header (`:223-228`) states the reason:

> *"A build that enables a consumer but produces no accounting-base JAR would ship a container that
> migrates against tables which do not exist — a runtime Flyway failure. Assert it HERE, in the
> builder, where the cause is one line of output away, instead of at first container start."*

Four guards, verbatim shape:

1. **any warehouse flag ⇒ `warehouse-base-backend-*.jar` exists** (`:229-243`), else
   `⨯ BUILD FAILED: … Check that the selected root pom.xml profile lists <module>warehouse-base/backend</module>.` + `exit 1`
2. **any consumer flag (`WAREHOUSE`, adapters, `3PL`, `INDIA`) ⇒ `warehouse-backend-*.jar` exists** (`:244-247`)
3. **each adapter flag ⇒ that adapter's JAR exists** (`:248-251`)
4. **`ENABLE_WAREHOUSE_3PL` / `ENABLE_WAREHOUSE_INDIA` ⇒ that JAR exists** (`:252-255`)

Guard 2 needs one adjustment for warehouse and it is deliberate: **an adapter depends on
`warehouse-base`, not on `warehouse`** (§4). If you decide adapters may be installed without the
`warehouse` application module, drop the adapter flags from guard 2 and say so in the comment.
Accounting's guard 2 does include its adapter (`:244`), because `accounting-adapter-dealer`'s profile
pulls `accounting` into the reactor. Copy accounting's shape unless D-7's standalone-plus-adapter
configuration is meant to be buildable, in which case state the divergence in the block's comment.

---

## 6. `shared/docker/Dockerfile.frontend` — five edits and one hazard

### 6.1 The edits

| # | Line today | Add |
|---|---|---|
| 1 | `:41-44` | `ARG ENABLE_WAREHOUSE_BASE=false` … one per module (all six, including backend-only ones — the frontend image still needs the flag to emit `NEXT_PUBLIC_*`) |
| 2 | `:71-73` | `COPY warehouse-base/frontend/src/. /tmp/warehouse-base-src/` and `COPY warehouse/frontend/src/. /tmp/warehouse-src/` — **and a comment naming the adapters as backend-only**, mirroring `:71` |
| 3 | `:158-176` | the `NEED_WAREHOUSE` / `NEED_WAREHOUSE_BASE` derivation and the two `cp -r /tmp/<mod>-src/. ./src/` merges |
| 4 | `:177` | append `/tmp/warehouse-base-src /tmp/warehouse-src` to the `rm -rf` |
| 5 | `:194-197` | 6 × `ENV NEXT_PUBLIC_ENABLE_WAREHOUSE_*=$ENABLE_WAREHOUSE_*` |

The derivation shape at `:158-164` is the one to copy — every consumer turns the base on:

```dockerfile
if [ "$ENABLE_WAREHOUSE_BASE" = "true" ]; then NEED_WAREHOUSE_BASE=true; fi; \
if [ "$ENABLE_WAREHOUSE" = "true" ] || [ "$ENABLE_WAREHOUSE_ADAPTER_DEALER" = "true" ] \
   || [ "$ENABLE_WAREHOUSE_ADAPTER_SERVICES" = "true" ] || [ "$ENABLE_WAREHOUSE_3PL" = "true" ] \
   || [ "$ENABLE_WAREHOUSE_INDIA" = "true" ]; then \
    NEED_WAREHOUSE=true && NEED_WAREHOUSE_BASE=true; \
fi; \
```

**Merge order.** `Dockerfile.frontend:80-176` runs the merges in a fixed order and the *last* `cp -r`
wins on any colliding path. Accounting merges `accounting` (`:165-170`) **before** `accounting-base`
(`:171-176`), so base overwrites app. Warehouse must state its own order deliberately: put
`warehouse-base` **last** to match accounting, and record the reason (a base file is the shared one;
if an app file shadows it, the app's copy is the accident). Whatever you choose, assert it in a
comment — `PF-009` in the accounting set is the finding that this order is assumed and never written
down.

### 6.2 The last-write-wins hazard, quantified

Modules are merged by `cp -r /tmp/<mod>-src/. ./src/` into one tree. Two modules that ship a file at
the same relative path silently produce one file. Count the paths that already collide:

```bash
# from the classic repo root
for d in platform automotive dealer assets accessories services insurance lead-sharing \
         product-lift field-service submittals insurance-360 doc-ocr-ai accounting-base accounting; do
  [ -d "$d/frontend/src" ] && (cd "$d/frontend/src" && find . -type f | sed "s|^\./||")
done | sort | uniq -c | awk '$1>1' | sort -rn
```

→ **39 colliding relative paths**, computed 2026-09-01. 38 of them are real source files; one is
`.gitkeep` (5 copies). The worst offenders are deliberate duplication, not accidents —
`components/common/personaCharts.tsx` ×4, `types/pdiStockYard.ts` ×3, `hooks/useUserBranches.ts` ×3,
`components/common/ActivityDetailModal.tsx` ×3 — but `components/DealerSafeTranslation.tsx` ×2 and
`app/(public)/layout.tsx` ×2 show how easily a load-bearing file collides.

**The rule for warehouse, and it is absolute (D-3, R1 `C-012`/`T-11`):** every file warehouse adds to
a module `frontend/src/` tree must have a **globally unique path**. Prefix everything:

| Kind | Naming |
|---|---|
| components | `warehouse-base/frontend/src/components/whb<Entity>/Whb<Entity>ManagementTable.tsx` |
| API services | `services/api/whbStockMovementApi.ts` |
| types | `types/whbStockMovement.ts` |
| constants | `constants/warehouseBasePermissions.ts`, `constants/warehouseBaseGrids.ts` |
| i18n namespace | `i18n/locales/<lang>/warehouseBase.json` — **the namespace IS the file name**, and `AccountingBaseSafeTranslation.tsx:30-33` says so: *"a file name reused by another module would silently replace it"* |
| routes | `app/warehouse/...` under one root segment per module family |

Before adding any file, run the collision check for its exact path:

```bash
path="components/common/WhbScanInput.tsx"
for d in platform automotive dealer assets accessories services insurance lead-sharing \
         product-lift field-service submittals insurance-360 doc-ocr-ai accounting-base accounting; do
  [ -f "$d/frontend/src/$path" ] && echo "COLLIDES: $d/frontend/src/$path"
done; echo "checked: $path"
```

---

## 7. `platform/frontend/tsconfig.json` — 8 aliases per frontend-bearing module

`:162-186` is the accounting-base block; `:187-211` is accounting's. Eight entries each, all
resolving to `./src/*` because the Docker build has already merged the module tree into
`platform/frontend/src/`:

```jsonc
// Warehouse Base module paths (files are copied into src during Docker build)
"@warehouse-base/*":            ["./src/*"],
"@warehouse-base/components/*": ["./src/components/*"],
"@warehouse-base/services/*":   ["./src/services/*"],
"@warehouse-base/hooks/*":      ["./src/hooks/*"],
"@warehouse-base/types/*":      ["./src/types/*"],
"@warehouse-base/config/*":     ["./src/config/*"],
"@warehouse-base/constants/*":  ["./src/constants/*"],
"@warehouse-base/i18n/*":       ["./src/i18n/*"],
```

Repeat for `@warehouse/*` in v1, and `@warehouse-3pl/*` / `@warehouse-india/*` in v2 — **32 entries
across the four frontend-bearing modules**. Platform's own aliases (`@platform/*`, `:85-111`) stay
untouched and remain how a warehouse page imports a shared component.

The alias set does not include `@warehouse-base/utils/*` — accounting has no `utils` alias either.
If a warehouse module needs one, add it in the same shape and to every frontend-bearing module at
once, so the set stays symmetric.

---

## 8. `ModuleImportSelector.java` — the gate that fails silently

`platform/backend/src/main/java/ai/platform/config/ModuleImportSelector.java`. **This is the one
touchpoint where a miss produces no error of any kind:** the module JAR ships in `/app/lib`, Spring
starts, and not one warehouse bean is created. The only symptom is a missing `✓ … Module ENABLED`
line in the boot log.

Two edits per module. Constants block, after `:54`:

```java
private static final String WAREHOUSE_BASE_MODULE_CONFIG = "ai.warehousebase.WarehouseBaseModuleConfig";
private static final String WAREHOUSE_MODULE_CONFIG = "ai.warehouse.WarehouseModuleConfig";
private static final String WAREHOUSE_ADAPTER_DEALER_MODULE_CONFIG = "ai.warehouseadapterdealer.WarehouseAdapterDealerModuleConfig";
private static final String WAREHOUSE_ADAPTER_SERVICES_MODULE_CONFIG = "ai.warehouseadapterservices.WarehouseAdapterServicesModuleConfig";
private static final String WAREHOUSE_3PL_MODULE_CONFIG = "ai.warehouse3pl.Warehouse3plModuleConfig";
private static final String WAREHOUSE_INDIA_MODULE_CONFIG = "ai.warehouseindia.WarehouseIndiaModuleConfig";
```

Selector block, after `:186`, one per module, copying `:156-162` verbatim in shape:

```java
// Try to load Warehouse Base Module (shared stock ledger engine - auto-enabled with any warehouse consumer)
if (isClassPresent(WAREHOUSE_BASE_MODULE_CONFIG)) {
    imports.add(WAREHOUSE_BASE_MODULE_CONFIG);
    logger.info("✓ Warehouse Base Module configuration found - will be loaded if enabled (ENABLE_WAREHOUSE_BASE/ENABLE_WAREHOUSE/ENABLE_WAREHOUSE_ADAPTER_*/ENABLE_WAREHOUSE_3PL/ENABLE_WAREHOUSE_INDIA=true)");
} else {
    logger.debug("Warehouse Base Module configuration not found on classpath - skipping");
}
```

Also update the class javadoc list at `:16-30` — it is the only human-readable index of what the
selector knows about.

### 8.1 `<Mod>ModuleConfig.java` — one per module

Copy `accounting-base/backend/src/main/java/ai/accountingbase/AccountingBaseModuleConfig.java`
entirely, including its javadoc, which carries four rules warehouse needs verbatim:

- **`:46-49`** — the base's condition ORs in **every** consumer flag, so a consumer install turns the
  base on without the operator having to know:
  ```java
  @ConditionalOnExpression(
      "${enable.warehouse.base:false} or ${enable.warehouse:false} "
    + "or ${enable.warehouse.adapter.dealer:false} or ${enable.warehouse.adapter.services:false} "
    + "or ${enable.warehouse.3pl:false} or ${enable.warehouse.india:false}"
  )
  ```
- **`:50-52`** — `@ComponentScan("ai.warehousebase")`, `@EntityScan("ai.warehousebase.entity")`,
  `@EnableJpaRepositories("ai.warehousebase.repository")`.
- **`AccountingModuleConfig.java:22-25`** — *"The dealer adapter lives in
  `ai.accountingadapterdealer`, a **SIBLING** package … `@ComponentScan` matches by package prefix,
  so an adapter placed under `ai.accounting` would be component-scanned and its beans loaded in an
  install that never set ENABLE_ACCOUNTING_ADAPTER_DEALER."* This is D-1's rule with the mechanism
  spelled out. `ai.warehouseadapterdealer`, never `ai.warehouse.adapter.dealer`.
- **`AccountingBaseModuleConfig.java:41-45`** — *"Controllers MUST live in
  `ai.accountingbase.controller`. `UserActivityTrackingAspect` advises `within(ai..controller..*)`,
  so a controller placed anywhere else is invisible to write auditing."* Verified:
  `platform/…/aspect/UserActivityTrackingAspect.java:59` is the pointcut, `:169-171` derives the
  module name from package segment 2. Warehouse controllers therefore live in
  `ai.warehousebase.controller`, `ai.warehouse.controller`, … and the activity log will record the
  module as `WAREHOUSEBASE` / `WAREHOUSE` / `WAREHOUSE3PL` / `WAREHOUSEINDIA` (R1 `C-049`, `T-16`).

A consumer module's `@EntityScan` must list **both** packages — `AccountingModuleConfig.java:54`:
`@EntityScan(basePackages = {"ai.accounting.entity", "ai.accountingbase.entity"})`. An adapter lists
three, including the vertical's — `AccountingAdapterDealerModuleConfig.java:55`.

**Route convention.** `AccountingBaseModuleConfig.java:27-36`: `server.servlet.context-path: /api/v1`
is global, so a controller declares only `@RequestMapping("/warehouse/<resource>")`; writing
`/api/v1/...` inside the annotation yields `/api/v1/api/v1/...`. All six warehouse modules share the
`/warehouse` namespace (`:35-36` states the accounting equivalent), so **resource segments must be
globally unique across the family** — `whb-` / `wh-` / `wh3-` / `whin-` prefixes on the resource
segment are the cheapest way to guarantee that.

---

## 9. Environment and property naming

Spring relaxed binding maps `ENABLE_WAREHOUSE_BASE` → `enable.warehouse.base` with no declaration
anywhere (R1 `C-008`, re-verified: `application.yml`'s `enable:` block lists only six modules and the
other ten bind fine).

| Env var | Property | Maven activation property |
|---|---|---|
| `ENABLE_WAREHOUSE_BASE` | `enable.warehouse.base` | same |
| `ENABLE_WAREHOUSE` | `enable.warehouse` | same |
| `ENABLE_WAREHOUSE_ADAPTER_DEALER` | `enable.warehouse.adapter.dealer` | same |
| `ENABLE_WAREHOUSE_ADAPTER_SERVICES` | `enable.warehouse.adapter.services` | same |
| **`ENABLE_WAREHOUSE_3PL`** | **`enable.warehouse.3pl`** | same |
| `ENABLE_WAREHOUSE_INDIA` | `enable.warehouse.india` | same |

### 9.1 The digit-leading segment — what is proven and what is not

`enable.warehouse.3pl` has a path segment that starts with a digit. The precedent is
**`enable.insurance.360`**, and it is live in three places:

- `pom.xml:195` — profile activation `<name>enable.insurance.360</name>`, and the module builds.
- `shared/docker/docker-compose.yml:121,146` — `ENABLE_INSURANCE_360` build arg + env.
- `insurance-360/backend/src/main/java/ai/insurance360/Insurance360ModuleConfig.java:29-33` —
  **`@ConditionalOnProperty(name = "enable.insurance.360", havingValue = "true", matchIfMissing = false)`**.

**The precedent is `@ConditionalOnProperty`, not `@ConditionalOnExpression`.** That distinction
matters exactly once:

- `Warehouse3plModuleConfig` needs only its own flag → use `@ConditionalOnProperty`, which is the
  proven shape. Zero risk.
- `WarehouseBaseModuleConfig` must OR in six flags → it needs `@ConditionalOnExpression`, and one of
  the six placeholders is `${enable.warehouse.3pl:false}`. A digit-leading segment inside a
  SpEL-embedded property placeholder has **no precedent in this repo** —
  `AccountingBaseModuleConfig.java:47-49` proves the OR-expression shape, and `enable.insurance.360`
  proves the digit segment, but nothing proves the combination.

**UNVERIFIED, and how to settle it:** boot the stack once with `ENABLE_WAREHOUSE_3PL=true` and check
for `✓ Warehouse Base Module ENABLED` in `docker logs platform-backend`. Do this in `P0-01`, before
any code depends on it. If it fails, the fallback is `@Conditional(AnyNestedCondition.class)` with
one `@ConditionalOnProperty` per flag — mechanical, and it uses only the proven annotation. **Do not
rename the module to avoid the digit**: D-1 fixes `ai.warehouse3pl`, and the property name follows
the env var, which follows the module name.

---

## 10. The two platform CHECK constraints that reject an unknown module value

Two platform tables enumerate which modules may own a row. Warehouse needs one migration in the
`warehouse-base` band (`V500000–V509999`) to widen them, and it must **merge**, never replace.

| Constraint | Current definition | Warehouse status |
|---|---|---|
| `global_settings.chk_global_setting_module` | `('PLATFORM','DEALER','ACCESSORIES','ATTENDANCE','ASSETS','SERVICE','WAREHOUSE')` — `platform/…/V553__global_settings_allow_warehouse_module.sql:14-15`, superseding `V337:42` | **`'WAREHOUSE'` is already allowed, free.** V553's header (`:3-5`) credits a `V190035 (warehouse-core)` migration that **does not exist in this checkout** — a value left behind by a deleted module (R1 `C-015`) |
| `widget_definitions.chk_module` | `('platform','dealer','shared','accessories','assets','insurance','services')` — `platform/…/V557__Extend_widget_definitions_module_constraint.sql:16-18`, superseding `V234:36`, `V276:9`, `insurance/V50009:8` | **`'warehouse'` is NOT allowed.** The first warehouse dashboard widget insert fails with SQLSTATE `23514` (R1 `C-014`) |

Note the case difference and that it is deliberate: `global_settings.module` is `UPPER_SNAKE`,
`widget_definitions.module` is lower-case. `V600200:18-20` records exactly this.

### 10.1 The out-of-order re-assertion hazard

`widget_definitions.chk_module` has been rebuilt by a hardcoded `DROP CONSTRAINT` + `ADD CONSTRAINT`
**four times** — `V234:36`, `V276:7-9`, `V557:16-18`, `insurance/V50009:7-8`. Each one substitutes its
own literal list. Consequences for a warehouse migration that does the same:

1. A hardcoded list from `V5xxxxx` discards any value added by a migration that sorts differently —
   and `global_settings`' last writer today is `product-lift/…/V800039`, which sorts **after** the
   whole warehouse band.
2. Worse: rebuilding a narrower constraint over a table that already has rows for the discarded
   module fails with `23514` at migration time — and `FlywayConfiguration.java:246-264` responds to
   any migration failure with a blind `flyway.repair()` + one retry, so the second failure leaves the
   history half-repaired.

### 10.2 The prescription — copy `V600200`

`accounting-base/backend/src/main/resources/db/migration/V600200__Allow_accounting_in_platform_module_check_constraints.sql`
is the merge idiom, and `:36-44` states the reasoning in full. Its shape, per constraint:

```sql
DO $$
DECLARE v_def text; v_values text[]; v_list text;
BEGIN
    SELECT pg_get_constraintdef(oid) INTO v_def
    FROM pg_constraint
    WHERE conname = 'chk_global_setting_module' AND conrelid = 'global_settings'::regclass;

    IF v_def IS NULL THEN
        v_values := ARRAY['PLATFORM','DEALER','ACCESSORIES','ATTENDANCE','ASSETS','SERVICE','WAREHOUSE'];
    ELSE
        -- works for `module IN (...)` and for the normalized `module = ANY (ARRAY[...])` form
        SELECT array_agg(DISTINCT m[1]) INTO v_values
        FROM regexp_matches(v_def, chr(39) || '([^' || chr(39) || ']+)' || chr(39), 'g') AS m;
    END IF;

    IF NOT ('WAREHOUSE' = ANY (v_values)) THEN
        -- array_append, NOT `|| 'WAREHOUSE'`: the operator resolution picks text[] || text[]
        -- and 22P02 "malformed array literal" follows (V600200:79-82)
        v_values := array_append(v_values, 'WAREHOUSE'::text);
    END IF;

    SELECT string_agg(quote_literal(val), ', ') INTO v_list FROM unnest(v_values) AS val;

    EXECUTE 'ALTER TABLE global_settings DROP CONSTRAINT IF EXISTS chk_global_setting_module';
    EXECUTE format('ALTER TABLE global_settings ADD CONSTRAINT chk_global_setting_module CHECK (module IN (%s))', v_list);
END $$;
```

Then repeat for `widget_definitions.chk_module` with the lower-case `'warehouse'`, and finish with
`V600200:150-161`'s verification block, which re-reads both constraint definitions and
`RAISE EXCEPTION` if either does not contain the new value — because a `DO` block that silently did
nothing is indistinguishable from one that worked.

**How many values, and which.** One per constraint, not one per module. `V600200:22-27` explains:
these two columns name the *user-facing* module, and the warehouse family presents a single
"Warehouse" surface (one L1 menu). A second `WAREHOUSE_BASE` value would render an extra, permanently
empty Global Settings tab. `permissions.resource_type` names the *migration-owning* module and has no
CHECK to widen.

**Do not name anything `wms_*` or `scc_*`** (D-3). `platform/…/V528` and `V663` still carry hardcoded
`wms_*` / `scc_*` / `warehouse-*` permission exclusions from a deleted earlier module; they have
already run, so they grant a new module nothing, but a `wms_`-prefixed permission would inherit a
decision nobody took.

### 10.3 Runtime truth is per-install — verify, do not assume

Which values a constraint actually allows depends on which modules are enabled and in what order
their migrations ran. **UNVERIFIED** for any given install; settle it with:

```sql
SELECT conname, pg_get_constraintdef(oid)
FROM pg_constraint
WHERE conname IN ('chk_global_setting_module', 'chk_module');
```

---

## 11. The frontend story

### 11.1 `<Mod>SafeTranslation.tsx` — one per frontend-bearing module

Copy `accounting-base/frontend/src/components/AccountingBaseSafeTranslation.tsx`. It exports three
things, all required: `clearTranslationCache()` (`:21-24`), the `SafeTranslation` component, and
`useSafeTranslation()`. **A warehouse page imports `t()` from its own module's file, never from
`@platform/hooks/useSafeTranslation`** — a page that imports the platform hook renders blank labels
for every module key (memory: *"Wrong ns = silent English"* / *"No module: prefix = BLANK"*).

The module list at `:34-39` is the registry to edit per module:

```ts
const WAREHOUSE_BASE_MODULES = [
  // Platform shared modules (loaded first for common + errors + validation keys)
  'common', 'errors', 'systemInfo', 'export', 'gridPreferences',
  // Warehouse Base module
  'warehouseBase',
];
```

The loader (`:46-58`) tries `@/i18n/locales/<lang>/<ns>.json` first and falls back to
`@platform/i18n/locales/...`, which is how the five shared namespaces resolve without duplication.

`CLAUDE.md:125` lists the SafeTranslation files; add `WarehouseBaseSafeTranslation.tsx`,
`WarehouseSafeTranslation.tsx`, and in v2 `Warehouse3plSafeTranslation.tsx` and
`WarehouseIndiaSafeTranslation.tsx`.

### 11.2 i18n namespaces and locales

**Three locales, not one.** `platform/backend/src/main/java/ai/platform/constants/I18nConstants.java:28-33`
fixes the supported set as `en`, `hi`, `fr`, and `platform/frontend/src/i18n/locales/` has exactly
those three directories. Accounting ships all three
(`accounting-base/frontend/src/i18n/locales/{en,fr,hi}/accountingBase.json`); older modules ship `en`
only. **Follow accounting** (R1 `C-050`, `AF-2`), and seed `menu_translations` rows for all three in
every menu migration.

Namespace = file name = global. Warehouse namespaces:
`warehouseBase.json`, `warehouse.json`, `warehouse3pl.json`, `warehouseIndia.json` — 12 files across
the four frontend-bearing modules once all locales are counted.

> **R5 `S-095` is a real product constraint here, not a nicety.** Warehouse operators are the most
> language-diverse users in the suite, and the RF screens are where Hindi actually matters. Plan for
> `hi` to be *translated*, not stubbed. **RTL is absent platform-wide** and silently rules out the
> Gulf — record that as a known limit rather than discovering it in a demo.

### 11.3 `jest.config.js` — **MI-1**, the third silent gate

`platform/frontend/jest.config.js:45-53` states the hazard in its own comment: *"`roots` and
`testMatch` below enumerate module frontends one by one, so a module absent from BOTH lists has its
suites silently ignored — a test file can be written, committed and never run."*

Add to `roots` (`:54-61`):

```js
'<rootDir>/../../warehouse-base/frontend',
'<rootDir>/../../warehouse/frontend',
```

and **two** entries per module to `testMatch` (`:69-82`) — the `__tests__/` glob and the
sibling-file glob:

```js
'<rootDir>/../../warehouse-base/frontend/src/**/__tests__/**/*.{test,spec}.{js,jsx,ts,tsx}',
'<rootDir>/../../warehouse-base/frontend/src/**/*.{test,spec}.{js,jsx,ts,tsx}',
```

Note `:64-68`: only `*.test.*` / `*.spec.*` are suites. A shared fixtures module living under
`__tests__/` is not, and adding one without that suffix fails with *"Your test suite must contain at
least one test"*.

---

## 12. Shared registries — and the honest limit on the loose-coupling ratchet

Two platform files change on **every new warehouse grid**. Neither has a per-module extension point.

### 12.1 `platform/frontend/src/utils/filterUtils.ts` — silent gate ⚠

`COMMON_FILTER_CONFIGS` is a TypeScript `const` beginning at `:346`. A filter field not listed in its
scope is **dropped by `convertFiltersForApi()` before the request is built** — the filter UI renders,
accepts input, and does nothing.

```bash
awk '/COMMON_FILTER_CONFIGS/,0' platform/frontend/src/utils/filterUtils.ts | grep -cE "^  [A-Z0-9_]+: \{"
```

→ **211 scopes**, computed 2026-09-01 (R1 recorded 210; the tree moved).

Eight field types, `:30`: `text | select | enum | multiselect | boolean | date | dateOnly | number`.

**`dateOnly` is load-bearing for warehouse.** `:49-56` documents it: `date` shifts to UTC day
boundaries for `TIMESTAMP` columns, which *"moves the 'from' bound to the previous calendar day for
users east of UTC"*. Warehouse's `expiry_date`, `manufacture_date`, `count_date` and `posting_date`
are pure SQL `DATE` columns and must use `dateOnly` (R1 `T-6`, `C-042`).

One scope per grid, named for the grid identifier: `WAREHOUSE_STOCK_MOVEMENT`,
`WAREHOUSE_STOCK_POSITION`, `WAREHOUSE_ITEM`, … Grep the SCOPE name before adding it — the file
already holds 25+ `ACCESSORY_*` blocks (`:1624-2269`) and a name clash is a silent merge of two
grids' allowlists.

### 12.2 `platform/…/config/CacheConfiguration.java`

```bash
awk 'NR>=101 && NR<=415' platform/backend/src/main/java/ai/platform/config/CacheConfiguration.java \
  | grep -cE '^[[:space:]]+"[a-zA-Z0-9._-]+",?$'
```

→ **230 cache names**, computed 2026-09-01 (R1 recorded 202).

`:375-377` is the warning, in the file: *"An unregistered name throws `IllegalArgumentException` on
the FIRST call, not at startup, so it must be here."* Register `dropdown.warehouse.<entity>` and
`statistics.warehouse.<entity>` before the first `@Cacheable` uses them.

**And do not register a name for a filter-aware statistics strip.** `:190-196` records that exact
mistake (issues neetub1508/classic#790, #791): statistics computed from the same search + filters as
the rows *"are uncacheable under any key short of the full filter set, and the `statistics.leave…`
names that used to sit here were registered and evicted but never produced by a single `@Cacheable`
— so they cached nothing while reading as though leave statistics were cached."* Warehouse's
statistics strips are filter-aware by design ⇒ **no `statistics.*` name for them**. `dropdown.*`
names are fine.

### 12.3 The ratchet, stated honestly

> **The loose-coupling ratchet can only ever be *zero commits to `warehouse-base`*. It can never be
> *zero commits to `platform`*.**

`COMMON_FILTER_CONFIGS` is a `const` in platform; `CacheConfiguration` is platform Java. Every
warehouse grid, in every module including every adapter, edits both. D-10's corollary and R7 `G-047`
say the same thing, and R7 §4.4 layer 3 repeats it as a caveat on the review ratchet. A contract that
claims platform is untouched is false on day one and, being false, gets ignored — taking the true
invariants with it.

The measurable ratchet, and it is worth measuring:

```bash
# at the commit that merges the SECOND adapter, this must equal its value at the previous commit
git log --oneline -- warehouse-base/ | wc -l
```

Record the number in the adapter's PR description (R7 §4.4 layer 3). CI cannot see this reliably
across rebases; a reviewer can, in one command.

### 12.4 The platform-file ledger — every platform file a warehouse module keeps editing

§12.3 is honest only if the list of platform files is complete. Round 4 found it short by seven
(`RH-006`, `RH-007`, `RH-008`). [`PLATFORM-DEPENDENCIES.md`](PLATFORM-DEPENDENCIES.md) §2.15 carries them
as `PDEP-1`…`PDEP-7`, and `IMPLEMENTATION-PLAN.md` `PP-9` lists the commits.

| Platform file | Edited when | What changes | Owner | Source |
|---|---|---|---|---|
| `platform/frontend/src/utils/filterUtils.ts` | every grid | one `COMMON_FILTER_CONFIGS` scope | the grid's task | §12.1 |
| `platform/…/config/CacheConfiguration.java` | every cached name | one `dropdown.warehouse.<entity>` name | the service's task | §12.2 |
| `platform/…/constants/NotificationCategory.java` | the first warehouse notification, then each category | a `WAREHOUSE_*` enum value (`:14`), `WAREHOUSE_REPLENISHMENT` first | `P2-15`, then `P3-16` | `RH-007`, `PDEP-1` |
| `platform/…/service/notification/email/EmailTemplateDefaults.java` | each warehouse email kind | one `register(new EmailTemplateDef(…))` (`:82` onward) | `P2-15` first, then each kind's task | `RH-007`, `PDEP-2` |
| `platform/…/service/dashboard/DashboardWidgetScopeResolver.java` | the first warehouse widget | one `FALLBACK_MODES` entry (`:104-118`; `Map.of`, 6 of 10 used) | `P6-10` | `RH-006`, `PDEP-4` |
| `platform/frontend/src/components/dashboard/widgets/registry.ts` | the first warehouse widget | `'warehouse'` in the module union (`:35`) | `P6-10` | `RH-006`, `PDEP-5` |
| `mobile/src/navigation/screens/lazyScreens.ts` | every mobile screen | one lazy registration | the screen's task | §2 row 23, `PDEP-6` |
| `mobile/src/navigation/RootNavigator.tsx` | every mobile screen | one route | the screen's task | §2 row 24, `PDEP-6` |
| `mobile/src/screens/GenericScreen.tsx` | every mobile menu route | one arm in the string-match chain (`:41-47`) | the screen's task | §2 row 25, `PDEP-6` |

§2 names the files each module edits **once**, when it lands (`ModuleImportSelector.java`,
`tsconfig.json`, `jest.config.js`, the two Dockerfiles). This ledger is the set that keeps changing
after that. The SMS gateway (`PDEP-3`) and the v1.1 shared scanner (`PDEP-7`, extracted from
`AssetQrScannerScreen.tsx`) are new platform or platform-adjacent files rather than edits, and are
listed in `PLATFORM-DEPENDENCIES.md` §2.15.

---

## 13. The adapter contract as buildable artefacts

D-11 says adapters are proved by a build-time test, not by intent. R7 §4.4 specifies three layers.
This section turns them into files.

### 13.1 `warehouse-adapter-example` — the fixture adapter

A real Maven module in the reactor, listed only in `all-modules` and in its own
`with-warehouse-adapter-example` profile. **Zero screens.** It contains exactly one of each thing an
adapter is allowed to have (R7 §4.2): one movement type, one document type, one item external ref,
one reservation with a holder quad, one `WhMovementEventSubscriber`, one row in `whb_source_systems`,
one `whb_number_series` scope. Its integration test posts a movement, reserves, consumes, reverses
and reads back **using only the public API of R7 §4.2** — no repository, no table.

The value: *if the fixture compiles and passes, the contract is expressible; if a real adapter needs
something the fixture cannot express, that is a base gap found before the base ships.* It is
materially stronger than any grep, and it is what R2 `T-079` and R3 `E-006` ask for without naming a
mechanism. It also fails loudly the day someone adds a base capability that only `warehouse` can
reach.

Its Flyway sub-band comes out of the adapter band: **`V529000–V529999`**, at the top, so it never
collides with a real adapter allocated from the bottom.

### 13.2 `WarehouseBaseCouplingTest` — the static gate

A test class in `warehouse-base/backend/src/test/java/ai/warehousebase/architecture/`. It is
**net-new** — R7 §4.4 verified that accounting's equivalent *"does not exist as a test — it exists as
a comment"* (`AccountingModuleConfig.java:22`), and that neither `ArchitectureInvariantsTest` copy
contains a dependency-direction rule (inspected `@DisplayName` list, `:64-346`; re-verified here —
the five nested classes are `PreAuthorizeRule`, `CacheRegistrationRule`, `PageRequestRule`,
`NPlusOneRule`, `ScannerIntegrity`, and none of them looks at imports).

Six assertions (R7 §4.4 layer 1):

1. No file under `warehouse-base/backend/src/main/java` contains `import ai.warehouse.`,
   `import ai.warehouseadapter`, `import ai.warehouse3pl`, `import ai.warehouseindia`,
   `import ai.logistics`, or any vertical package — `ai.dealer`, `ai.services`, `ai.assets`,
   `ai.fieldservice`, `ai.automotive`, **`ai.accessories`**, `ai.insurance`, `ai.insurance360`,
   `ai.submittals`, `ai.leadsharing`, `ai.productlift`, `ai.accounting*`.
2. No migration in `V500000–V509999` contains `wha_`, `wh3_`, `whin_`, `log_`, `accessory_`, `pdi_`,
   `service_`, `asset_`, `acc_` in a `REFERENCES` clause.
3. Every `FOREIGN KEY … REFERENCES` in the base band targets a `whb_` table or a **whitelisted**
   platform table (`users`, `user_details`, `branches`, `documents`). The whitelist is itself
   asserted, so widening it is a reviewed act.
4. No `CHECK (… IN (…))` on any of D-10's **thirteen** registry columns. The test names the thirteen
   `table.column` pairs explicitly; a fourteenth registry means a row here.
5. **Scanner self-tests**, copying the shape at
   `accounting-base/…/ArchitectureInvariantsTest.java:224-346` — every scanner runs over a synthetic
   fixture tree containing one known violation of each rule and must report it. Without this, a
   scanner pointed at the wrong directory passes for the wrong reason.
6. `whb_source_systems` contains a row for `ACCESSORIES` with `is_reserved = true` and no adapter
   claims it (D-9, R7 `G-052`).

Assertion 5 is not optional. `accounting-base/…/ArchitectureInvariantsTest.java:43-57` explains why:
*"a scan that finds nothing because there is nothing to find is indistinguishable from a scan that
finds nothing because it is pointed at the wrong directory or its regexes are broken."*

### 13.3 Per-module `ArchitectureInvariantsTest` — **an edit, not a copy**

House style is one per module — `accounting-base` and `accounting` each ship a 660-line copy
(`find . -name ArchitectureInvariantsTest.java` → 3 files: platform 713 lines, accounting-base 660,
accounting 660). Six warehouse modules ⇒ six copies.

The header of the accounting copy (`:35-41`) states exactly why porting is an edit:

> *"The platform test resolves every scan root relative to the module basedir and then **hardcodes
> `ai/platform`** into those roots, so it can only ever see platform sources. Porting is therefore an
> edit, not a copy: the roots below point at this module's own package, and the frozen baselines are
> **EMPTY** because a greenfield module has no legacy to freeze."*

Three edits per copy:

| Edit | Where | Value for `warehouse-base` |
|---|---|---|
| Package root | `:67-68` | `MODULE_PACKAGE = JAVA_SOURCES.resolve(Paths.get("ai", "warehousebase"))` |
| Baselines | `:91`, `:177`, `:202` | **empty** — `new TreeMap<>()` / `new LinkedHashSet<>()`. An empty baseline makes the first unannotated controller, the first unregistered cache name, the first hand-built `Pageable` and the first `findById()` in a loop fail the build |
| Vacuity guard | `:56-57` | platform's `assertThat(total).isGreaterThan(500)` **cannot be ported** — zero endpoints is the correct answer on day one. `ScannerIntegrity` replaces it |

The four rules the ratchet carries (`@DisplayName`s at `:79`, `:121`, `:173`, `:198`) map to CLAUDE.md
CRITICAL #1, #2, #4, #5. Rule 2 reaches into platform's registry —
`import ai.platform.config.CacheConfiguration;` at `:3`, with a self-test at `:152-160` asserting the
registry is reachable at all.

### 13.4 `.github/workflows/tests.yml` — the edit that makes the ratchet actually run

**MI-2.** The `frontend` and `backend` jobs carry `continue-on-error: true` (`:97`, `:201`) because
both suites are red — *"frontend: ~810 suites, ~126 failing; backend: 1433 tests, 11 failures + 1
error (measured 2026-08-26)"* (`:19-21`). A ratchet inside either job would enforce nothing.

Accounting solved this with **two blocking additions**, and warehouse copies both:

**(a) A backend gate job.** Copy `tests.yml:259-408` as `warehouse-ratchets`, changing three things:

- both `mvn` invocations move to `-Pwith-warehouse` and
  `-pl warehouse-base/backend,warehouse/backend,warehouse-adapter-dealer/backend,warehouse-adapter-services/backend`
  (add `warehouse-3pl/backend,warehouse-india/backend` in v2). The two-step shape at `:300-321` is
  load-bearing and its comment (`:275-299`) says why: step 1 is `-am … -Dmaven.test.skip=true install`
  so `-am` drags `platform/backend` into the reactor **without running its red suite**; step 2 drops
  `-am` so surefire runs only in the selected modules.
- the "Assert the ratchets actually executed" step (`:334-379`) gets one `dir:prefix` pair per
  warehouse module. Its non-obvious rule (`:326-333`) must be preserved verbatim: surefire 3.2.2
  writes **one XML per `@Nested` class** — `TEST-<FQCN>$<Nested>.xml` — and the plain
  `TEST-<FQCN>.xml` is either absent or has `tests="0"`, *"so checking the plain file alone fails a
  GREEN build in both directions. Sum the whole family instead."*
- the `$ScannerIntegrity.xml` existence check (`:372-377`) is kept per module; it is what makes an
  empty module unable to pass vacuously.

**No `continue-on-error` on this job.** `:240-241`: *"A ratchet that runs behind `continue-on-error`
enforces nothing, so this job does not have it."*

**(b) A blocking frontend step inside the existing `frontend` job.** Copy `tests.yml:123-128`:

```yaml
- name: Run Jest - warehouse frontend suites (blocking)
  env:
    NODE_OPTIONS: --max-old-space-size=4096
  run: |
    npx jest --ci --maxWorkers=2 --passWithNoTests \
      --testPathPattern '/warehouse(-base|-3pl|-india)?/frontend/'
```

Three notes from `:106-122`, all of which apply unchanged: `--passWithNoTests` is required because
"no tests found" is a non-zero exit in Jest and the trees are empty on day one; `--testPathPattern`
is a regex over absolute paths, so the alternation group must cover every module or one tree is
matched and the others missed; and this is Jest 29 spelling — it becomes `--testPathPatterns` if the
repo moves to Jest 30.

**Scoping is what makes this safe.** `:255-257`: *"Scoping the gate to `-pl accounting-base/backend,accounting/backend`
means nothing outside those two directories can turn this job red. The two jobs above are untouched,
so no existing module's CI behaviour changes."* Same for warehouse. Add `warehouse-ratchets` to the
repository's required status checks the day it lands; it does not wait on the Phase 1 exit criteria
at `:410-418`.

---

## 14. Numbered install order — a fresh module landing

Execute in this order. Each step is verifiable before the next.

**Phase A — the module exists and builds (per module, base first)**

1. `mkdir -p <mod>/backend/src/main/{java/ai/<pkg>,resources/db/migration}` and, for a frontend-bearing
   module, `<mod>/frontend/src/{components,services/api,types,constants,config,i18n/locales/{en,fr,hi}}`.
2. **`<mod>/backend/pom.xml`** — full copy of `accounting-base/backend/pom.xml` (§4). Change
   `artifactId`, `name`, `description`, the Flyway `<location>`, and add the extra dependencies.
3. **Root `pom.xml`** — the profile (§3) and the `all-modules` row.
4. **`<Mod>ModuleConfig.java`** in `ai.<pkg>` (§8.1). Controllers under `ai.<pkg>.controller` from
   the first file.
5. **`ModuleImportSelector.java`** — constant + block + javadoc line (§8). ⚠ Silent if skipped.
6. **`ArchitectureInvariantsTest.java`** in `<mod>/backend/src/test/java/ai/<pkg>/architecture/`
   (§13.3), baselines empty.
7. *Verify:* `docker logs platform-backend | grep "Module configuration found"` after step 12's
   build shows the module.

**Phase B — the build system knows about it**

8. **`Dockerfile.backend`** — all seven edits **and** the assertion block (§5). Do the assertion
   block in the same commit; it is what turns a step-3 mistake into a build failure rather than a
   runtime 500.
9. **`Dockerfile.frontend`** — five edits, frontend-bearing modules only for the `COPY`/merge (§6).
10. **`docker-compose.yml`** — four blocks (`:123-126`, `:148-151`, `:293-296`, `:325-328`) plus the
    band comment at `:50-54`.
11. **`start.sh`** — eight places (`:36-39`, `:132-135`, `:289-303`, the dependency-derivation block
    at `:477-503`, `:775-778`, `:945-948`, `:1101-1120`, `:1810-1813`). The derivation block is the
    one with logic: every consumer auto-enables `ENABLE_WAREHOUSE_BASE`, an adapter auto-enables its
    vertical, `3PL`/`INDIA` auto-enable `ENABLE_WAREHOUSE`.
12. *Verify:* `./start.sh --docker --enable-warehouse` builds and boots.

**Phase C — the platform accepts its data**

13. **The CHECK-widening migration** in the `warehouse-base` band (§10), copying `V600200`'s merge
    idiom. This is `V500000`-something and lands before any widget or global setting.
14. **`CacheConfiguration.java`** — every cache name the first services will use (§12.2).
15. **`filterUtils.ts`** — one `COMMON_FILTER_CONFIGS` scope per grid (§12.1). ⚠ Silent if skipped.
16. **`tsconfig.json`** — 8 aliases per frontend-bearing module (§7).
17. **`<Mod>SafeTranslation.tsx`** + three locale JSONs per frontend-bearing module (§11.1, §11.2).
18. **`jest.config.js`** — `roots` + 2 `testMatch` entries per frontend-bearing module (§11.3).
    ⚠ Silent if skipped.

**Phase D — the gates**

19. **`.github/workflows/tests.yml`** — the `warehouse-ratchets` job and the blocking frontend step
    (§13.4). Add `warehouse-ratchets` to required status checks.
20. **`WarehouseBaseCouplingTest`** (§13.2) and **`warehouse-adapter-example`** (§13.1). The fixture
    adapter lands with the *first* adapter, not after the second — its whole purpose is to find base
    gaps before the base ships.

**Phase E — documentation and deployment**

21. **`CLAUDE.md`** — six MODULES rows with the D-2 bands, and the SafeTranslation list at `:125`.
22. **`shared/scripts/railway/template.conf`** + **`setup-railway-client.sh`** (§15 `AF-3`) — or an
    explicit written decision that Railway is out of scope for warehouse.
23. **`shared/scripts/startX2.sh`** — or an explicit written decision that it is not (§15 `AF-4`).

**Migration idempotency, every file, no exceptions.** `FlywayConfiguration.java:246-264` responds to
any migration failure with a blind `flyway.repair()` and one retry. Every warehouse migration must be
individually idempotent (`IF NOT EXISTS` / `ON CONFLICT` / `WHERE NOT EXISTS`), as every
`accounting-base` file is (R1 `C-047`).

**The upgrade path is not free** and must be documented, not discovered. The effective Docker Flyway
setting is `out-of-order: false` — `application.yml:105` defaults it to `true` but
`docker-compose.yml:183` overrides it with `SPRING_FLYWAY_OUT_OF_ORDER: "${FLYWAY_OUT_OF_ORDER:-false}"`,
and `startX2.sh:200` hard-codes `false`. A warehouse-only install (V5xxxxx applied) that later adds
dealer (V2xxxx) will be refused unless `FLYWAY_OUT_OF_ORDER=true`. Only `start.sh --restore-backup`
flips it, and it persists the flip to `.env` (`start.sh:367`, `:377`, `:785`). **State
"warehouse first, verticals later requires `FLYWAY_OUT_OF_ORDER=true`" in the install guide** (R1
`C-046`).

---

## 15. Rollback

**Rolling back the code is easy; rolling back the schema is not.** Be explicit about which one you
are doing.

| Scope | How | Cost |
|---|---|---|
| **Disable a module** (no schema change) | set `ENABLE_WAREHOUSE*=false`, rebuild the image | Free and instant. `@ConditionalOnExpression` stops the beans, `ModuleImportSelector` still finds the class and logs it as "will be loaded if enabled". **The tables and their rows stay.** Nothing reads them |
| **Remove a module from an image** | drop its profile from `MAVEN_PROFILES`, rebuild | The JAR is not produced, the `mkdir -p` at `:273` keeps `COPY --from=builder` working, the jar-copy block at `:431-457` prints `⨯ … disabled`. **Its migrations were already copied into the flattened directory in an earlier build only if its flag was on** — so a fresh build without the flag does not copy them, and an existing database keeps the applied rows |
| **Un-apply a migration** | **There is no down-migration mechanism in this repo.** `grep -rl "^-- *DOWN\|undo" */backend/src/main/resources/db/migration/` finds nothing structural | A reversing migration in the same band, forward-only. For `warehouse-base` v1 that means a `DROP TABLE IF EXISTS whb_*` migration authored deliberately — never a deletion of the original file, which changes its checksum and makes Flyway fail validation on every existing install |
| **Roll back a `platform` edit** | revert the `filterUtils.ts` / `CacheConfiguration.java` / `tsconfig.json` hunks | Free — none of them has a database side. `CacheConfiguration` is the only one with a runtime failure mode, and removing a name only breaks code that still uses it |
| **Roll back the CHECK-widening migration** | **do not.** It is a superset widening; narrowing it fails with `23514` if any module inserted a row | Leave it. `V553`'s own header (`:8-10`) states the rule: *"keep this list as a SUPERSET … Dropping an entry here would invalidate rows previously inserted by an enabled module."* |

**The one thing that cannot be rolled back is a Flyway version number that has been applied on a
customer install.** `FlywayConfiguration.java:322-327` deletes duplicate-version history rows
(*"keep lowest installed_rank per version"*) with no warning. Allocate every warehouse migration
number in the design set, in `tools/check-design-set.py`, before it is written — never at authoring
time.

---

## 16. What accounting got wrong or skipped — do not inherit it

R1 §1.2 records six divergences between the accounting design set and this checkout (`AF-1`…`AF-6`).
Each is re-verified here with what warehouse must do differently.

| # | What happened | Verified now | Warehouse's decision |
|---|---|---|---|
| **AF-1** | The accounting R1 asserted the repo root held no `accounting*` dirs and listed 13 module dirs | Superseded — `ls -d */` shows `accounting-base accounting accounting-adapter-dealer accounting-india` at the root, and still no `warehouse*` | Warehouse's own reviews must be re-verified against the tree at the moment of use, not against a quoted list. The tree moves under you |
| **AF-2** | *"Every module ships `en` only"* | **False now.** `accounting-base/frontend/src/i18n/locales/{en,fr,hi}/accountingBase.json` | **Ship three locales from the first file** (§11.2). Retrofitting `hi`/`fr` means re-opening every JSON |
| **AF-3** | Railway config stale by five modules | **Half-fixed.** `template.conf:41-44` and `setup-railway-client.sh:276-279`, `:423-426`, `:574-577` now carry all four accounting flags + `ENABLE_DOC_OCR_AI`. **Still absent: `ASSETS`, `PRODUCT_LIFT`, `FIELD_SERVICE`, `SUBMITTALS`, `INSURANCE_360`**; the frontend var list additionally drops `LEAD_SHARING` | Do the Railway edits **or** write down that warehouse is not Railway-deployable and why. The current state — five modules silently missing — is what "we'll do it later" produces |
| **AF-4** | *"`startX2.sh` — doc-ocr-ai HAS done this"* | **Accounting skipped it entirely.** `startX2.sh:94-97` carries 11 module flags + `ENABLE_ATTENDANCE` and **no accounting flag**; `:183-194` writes the same 11 into `.env`. So `startX2.sh` cannot start an accounting install at all | **Decide explicitly, in writing, in `P0-01`.** Two edits if yes. The failure mode of "skip it silently" is a developer running `startX2.sh` and getting a warehouse-free container with no error |
| **AF-5** | OEM/client bands reserved, versions reused across clients | **Verified exactly right**, and it is the fact that killed the original band choice. `ls platform/…/db/client/*/V910001__*.sql` → 5 files, one per client | Already resolved by D-2. Do not revisit |
| **AF-6** | *"12 files across 2 build systems"* | Now **18** (**MI-1**) | §2 is the current list. Expect it to grow again; re-derive it, do not quote it |

Three more, found here rather than in R1:

| # | What | Evidence | Warehouse's decision |
|---|---|---|---|
| **AF-7** | **`accounting/frontend` ships exactly one file** — its `SafeTranslation` component — and **no `i18n/` directory at all**. So the `accounting` namespace has no locale JSON, and `AccountingSafeTranslation`'s module list can only resolve platform-shared namespaces | `find accounting/frontend/src -type f` → 1 file | A scaffolded module with a `SafeTranslation` and no locale JSON is a component that silently falls back to platform namespaces for everything. **Land `warehouse.json` in all three locales in the same commit as `WarehouseSafeTranslation.tsx`**, even if it holds only the module title |
| **AF-8** | **`accounting-india` is banded `V602000–V602999`, nested inside `accounting-base`'s `V600000–V609999`** — a dependent module's DDL sorted numerically *below* its base's later migrations (`V600200` already exists) | `CLAUDE.md:120-123`; `docker-compose.yml:50-54` | **Do not copy.** D-2 gives each warehouse module a disjoint band, ordered base < app < adapters < 3PL < India, so a partial install always migrates in dependency order. `warehouse-india` at `V540000–V549999` is above everything it depends on (R1 `C-004`, `T-15`) |
| **AF-9** | The `accounting-ratchets` CI job hardcodes `ScannerIntegrity` as the nested-class name in a shell string (`tests.yml:372`) and prints *"If the nested class was renamed, update this check to match."* | `tests.yml:372-377` | Keep the nested class named `ScannerIntegrity` in all six warehouse copies. A rename that the workflow does not follow turns the anti-vacuous guard into a hard failure — which is the safe direction, but only if someone reads the message |

---

## 17. Verification commands — every count in this document

Run from the `classic` repo root. Values are as of 2026-09-01, HEAD on `main`.

```bash
# Flyway: the warehouse band is free
find . -name "V*__*.sql" -not -path "./node_modules/*" -not -path "*/target/*" \
  | sed -E 's|.*/V([0-9]+)(_[0-9]+)?__.*|\1|' | grep -E '^[0-9]+$' \
  | awk '{if($1>=500000 && $1<=549999) c++} END{print "V500000-V549999:", c+0}'      # → 0

# Flyway: the bands the brief proposed are not
for b in 90 91 95; do
  printf "V%sxxxx: " "$b"
  find . -name "V${b}[0-9][0-9][0-9][0-9]__*.sql" -not -path "./node_modules/*" -not -path "*/target/*" | wc -l
done                                                                                  # → 135 / 434 / 32

# Total versioned migrations
find . -name "V*__*.sql" -not -path "./node_modules/*" -not -path "*/target/*" | wc -l   # → 3300

# all-modules profile rows
awk 'NR>=287 && NR<=306' pom.xml | grep -c "<module>"                                 # → 16

# Module poms that cannot run a test
for p in */backend/pom.xml; do
  printf "%-45s %-5s %s %s %s\n" "$p" "$(wc -l < $p)" \
    "$(grep -c spring-boot-starter-test $p)" "$(grep -c maven-surefire-plugin $p)" \
    "$(grep -c maven-compiler-plugin $p)"
done                                                                # → assets, product-lift: 62 0 0 0

# Frontend path collisions across all module src trees
for d in platform automotive dealer assets accessories services insurance lead-sharing \
         product-lift field-service submittals insurance-360 doc-ocr-ai accounting-base accounting; do
  [ -d "$d/frontend/src" ] && (cd "$d/frontend/src" && find . -type f | sed "s|^\./||")
done | sort | uniq -c | awk '$1>1' | wc -l                                            # → 39

# Filter scopes
awk '/COMMON_FILTER_CONFIGS/,0' platform/frontend/src/utils/filterUtils.ts \
  | grep -cE "^  [A-Z0-9_]+: \{"                                                      # → 211

# Registered cache names
awk 'NR>=101 && NR<=415' platform/backend/src/main/java/ai/platform/config/CacheConfiguration.java \
  | grep -cE '^[[:space:]]+"[a-zA-Z0-9._-]+",?$'                                      # → 230

# Architecture ratchets in the repo
find . -name "ArchitectureInvariantsTest.java" -not -path "./node_modules/*" -exec wc -l {} \;
                                                        # → platform 713, accounting-base 660, accounting 660

# grid_filter_definitions does not exist — the real table is filter_definitions (V229)
grep -rln "CREATE TABLE.*grid_filter_definitions" --include=*.sql . | grep -v node_modules | wc -l   # → 0

# Only one frontend package.json exists — a module cannot add an npm dependency
ls */frontend/package.json | wc -l                                                    # → 1
```

Two things this document deliberately does **not** state, because they cannot be verified without
running something:

- **Flyway's exact error text on a duplicate version across locations.** Requires running Flyway;
  Docker-only build. Settle with `./start.sh --docker` and a deliberately colliding file.
- **Whether `enable.warehouse.3pl` relaxed-binds from `ENABLE_WAREHOUSE_3PL` inside a
  `@ConditionalOnExpression`.** §9.1. Settle with one Docker boot and
  `docker logs platform-backend | grep "Warehouse Base Module"`.

---

## Cross-references

- Module names, packages, bands, prefixes, the version ladder — [`DECISIONS.md`](DECISIONS.md)
- What warehouse needs *from* platform, with a verdict per capability —
  [`PLATFORM-DEPENDENCIES.md`](PLATFORM-DEPENDENCIES.md)
- The codebase evidence this runbook extends —
  [`reviews/R1-codebase-reality.md`](reviews/R1-codebase-reality.md) §2, §3, §8
- The adapter contract in full — [`reviews/R7-logistics-supply-chain-seam.md`](reviews/R7-logistics-supply-chain-seam.md) §4
- The operational surface that the build system does not supply —
  [`reviews/R5-standards-industry-ops.md`](reviews/R5-standards-industry-ops.md) §5
