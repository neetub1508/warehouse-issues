# R23 — platform alignment

**Date** 2026-09-10 · **Prefix** `RH-` · **Branch** `docs/round-4-cardinality-and-gaps`

**File set read — 16 design files, ~70 codebase files.**

```bash
cd warehouse-issues
# docs/ (6, in full or in the sections cited): README.md · DECISIONS.md · PLATFORM-DEPENDENCIES.md
#   MODULE-INTEGRATION.md (§1, §2, §10) · DATA-MODEL.md (targeted rows) · WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md (targeted rows)
# docs/reviews/ (3 in full): R1 · R14 · R16 (for shape);  R17–R21 finding headings; GAP-REGISTER{,-R2,-R3}.md by grep
# issues/ (14): p0-01 p0-07 p0-15 p1-05 p1-09 p1-10 p1-17 p1-18 p2-14 p2-20 p2-21 p2in-01 p3-16 p6-10
# BUILD-SPEC-SCREENS.md WS-016, WS-061; SCENARIO-CATALOGUE.md WH-SC-242/243; INDIA-LOCALISATION-PACK.md §3.3–3.4
grep -rohE "\bRH-[0-9]{1,3}\b" docs/ issues/ tools/ | wc -l        # → 0 before this file (the prefix is free)
cd /Users/bbhushan/work/git2/workspace/classic   # live codebase, read-only, main @ f7276dcc0c
```

**Premise taken from the brief, not re-derived.** The user has decided that branch ↔ warehouse is
**many-to-many** through `whb_warehouse_branches`, with **exactly one `REGISTERED` link per warehouse**
(the GSTIN anchor). The table itself is specified by the R22 lens, and R22 is not in this checkout
(`ls docs/reviews/ | grep R22` → nothing). This report assumes only those three facts about it and covers
how the junction plugs into platform behaviour.

**Method, in three sentences.** I built an inventory of every user-facing or cross-cutting capability
`platform` (and, where platform is silent, a sibling module) **already implements**. It covers 31
capabilities, each verified against the migration, service or component that implements it rather than
against any document. I then classified the warehouse design's use of each one as **REUSE**,
**DUPLICATE** (a defect), **GAP** (warehouse needs it and ignores it) or **PLATFORM-DEP** (warehouse cannot
use it without a platform commit). Finally I walked the **branch concept end to end** under the new M:N
premise: assignment → scope → picker → rollup → code namespace → tax anchor. Anything already owned by R1,
R14, a GAP register or a round-3 lens was refused (§4), unless that lens's disposition turned out to be
wrong. Three were wrong.

---

## §1 · Verdict

**The set reads `platform` as it stood two review rounds ago, and on the branch axis that is now
expensive.** The five rows R1 and `PLATFORM-DEPENDENCIES.md` rely on most — branch scoping, the branch
picker, the company axis, the dashboard framework and the import path — have all moved, or were always
shaped differently from how the set describes them:

- **Branch scoping is already a platform service.** `BranchScopeService` (`platform/…/service/common/BranchScopeService.java:14-40`)
  was *"extracted from the copies that had accumulated"* and is called from 153 files across six modules.
  It is keyed on a **`<resource>:view:all` / `<resource>:view:branch` permission pair**, and 94 distinct
  `:view:branch` names are already seeded.
- **The set does not know it exists.** It re-specifies the pattern as *"the three-mode view pattern"*
  (`FR-404`). It seeds **no** scope-tier permission (`grep -rn "view:all" docs issues` → 0), and it asks
  platform to extract what platform has already extracted (`PP-13`, `PD-D11`). → `RH-002`
- **Every branch predicate in the set binds a scalar that no longer exists.** The user's M:N decision
  removes `whb_warehouses.branch_id`, yet `FR-079`, DATA-MODEL `B1`, `P1-05`, `WS-016`, `P1-18` and PD §2.3
  all bind a single `branch_id`. The only platform SQL fragment for branch scope is column-shaped
  (`BranchFilterService.java:167-169`, `%s.branch_id IN (…)`).
- **The one live M:N guard in the monorepo treats an unlinked warehouse as visible to everyone.**
  That guard is accessories' `AccessoryStockTransferAccessGuard.isWarehouseAllowed`
  (`accessories/…/AccessoryStockTransferAccessGuard.java:186-206`). → `RH-001`

**The three attributions a shared warehouse needs are nowhere written down.** Once one warehouse serves
several branches, "the warehouse's branch" is a set, and the set must answer three different questions:

1. **Who may see it** — any active link.
2. **Whose GSTIN and number series it uses** — the `REGISTERED` link, frozen on the document.
3. **Whose total its stock counts toward** — the `REGISTERED` branch, or branch totals double-count.

The set answers none of them, because it was written for a scalar. → `RH-001`, `RH-005`, `RH-006`

**On the headline question — should a warehouse site also *be* a platform branch?** **No: link it, never
mirror it.** The evidence is §2 `RH-003`:

- `branch_code` is globally unique (`V160:19`).
- **154 of the 254** `useUserBranches(...)` calls pass no `branchType`, so every one of those showroom,
  service, leave and attendance pickers would list every warehouse site.
- All three modules that stock goods already keep their own location entity *linked* to branches, and
  none of them made it a branch.
- `'WAREHOUSE'` as a `branch_type` is used only by a test (`BranchIntegrationTest.java:369`).

A branch row of type `WAREHOUSE` is created **only** when a site is itself a GST place of business with no
existing branch. That row then becomes the site's `REGISTERED` link, and nothing else changes.

**Outside the branch axis, the pattern is platform edits the budget does not list.** The set's honest
limit — *"zero commits to `warehouse-base`, never zero commits to `platform`"* — is right, but its list of
platform files is short by seven:

- `NotificationCategory` (a Java enum), `EmailTemplateDefaults`, an SMS channel that is a stub → `RH-007`
- `DashboardWidgetScopeResolver.FALLBACK_MODES` and the frontend widget `registry.ts` union → `RH-006`
- three mobile navigation files and a string-matching gate the runbook never mentions → `RH-008`
- a 500-row client-side import cap the set calls *"reusable as-is for opening stock"* → `RH-009`

Two capabilities the set says do not exist do exist, and should be reused:

- a pluggable **scheduled-report** engine → `RH-010`
- a branch-assignable **holiday calendar** and a **timezone** master → `RH-011`

---

## §1.1 · Coverage table — the platform inventory

**Verdict key:**

| Verdict | Meaning |
|---|---|
| **REUSE** | The design uses the platform capability correctly |
| **DUP** | Duplicates it — a defect |
| **GAP** | Warehouse needs it and ignores it |
| **PDEP** | Cannot use it without a platform commit |
| **OWN✔** | Platform has nothing, and the design correctly owns its own |

Paths abbreviate `platform/backend/src/main/resources/db/migration/` as `PM/` and `platform/backend/src/main/java/ai/platform/` as `PJ/`.

| # | Capability | Live artefact (verified) | Design | Verdict | Owner |
|---|---|---|---|---|---|
| 1 | Branch master + `branch_type` | `PM/V149:9-68`, `chk_branches_type :61` (incl. `WAREHOUSE`, `DISTRIBUTION_CENTER`); `V160:19` `uk_branches_code` global; `parent_branch_id :65` unused | FR-079 scalar `branch_id`; PD §1.1 "a site **is** a branch" | **GAP** (M:N unmodelled) · contradiction | **`RH-001` `RH-003`** |
| 2 | User↔branch assignment | `branch_staff` `PM/V150:10-57` (no `user_branches` table; no one-primary rule); `BranchStaffRepository.findActiveBranchIdsByUserId :267-272` | assumed, never named | REUSE (implicit) | `RH-002` |
| 3 | Branch-scope guard + `:view:all`/`:view:branch` | `PJ/service/common/BranchScopeService.java:110,143,208,226`; `PM/V685:20-47,72-85` | re-specified as "three-mode"; no tier permission seeded | **DUP + GAP** | **`RH-002`** |
| 4 | Column-shaped SQL fragment | `PJ/service/common/BranchFilterService.java:167-169` | PD §2.3 prescribes it verbatim | **wrong shape under M:N** | **`RH-001`** |
| 5 | M:N warehouse↔branch guard (sibling) | `accessories/…/AccessoryStockTransferAccessGuard.java:126,143,186-206`; `WarehouseBranchRepository.java:96` | "do not repeat the accessories junction" | **GAP** — now the precedent, with one semantic to refuse | **`RH-001`** |
| 6 | Branch picker | `PF/hooks/useUserBranches.ts:73` → `GET /branches/my-branches` (`BranchesController.java:578-593`; params `activeOnly`, `branchType`, `isFieldServiceRequired`); mobile copy `mobile/src/hooks/useUserBranches.ts:75` | WS-016 `companyId → branchId` cascade | **GAP** — no company parameter exists | **`RH-004`** |
| 7 | Company / legal entity | **automotive**: `companies` `automotive/…/V10002:11-48`; branch link `company_branches` `V10014:7-23` (M:N) | `whb_companies` (P0-07) · `whb_api_clients.company_id → companies (platform)` | OWN✔ · **one wrong FK** | **`RH-004`** |
| 8 | Departments | `PM/V13:5-34` global, no `branch_id` | not used | OWN✔ (not a scope axis) | §3 |
| 9 | Designations | `PM/V13:45-74`; M:N to departments `PM/V449:90-98` | not used | OWN✔ | §3 |
| 10 | Roles / permissions / menus | `PM/V1_1:21-51`, `V16:7,27,36,49`, `V209:7` | P0-15 | REUSE | R1, `O-004` |
| 11 | Permission dependencies | `PM/V248:17-30` (inert at runtime); live: `menu_permission_dependencies` `PM/V225` | P0-15 | REUSE | `O-004` (not re-raised) |
| 12 | Approvals | leave only in platform (`PM/V755:15,140,173`); per-module copies in dealer/services/assets/submittals/accessories | copy `AccApprovalGate` seam | OWN✔ | R1, PD §2.10 |
| 13 | Delegation | `permission_delegations` `PM/V25:132` only — no approval-task delegation | none | OWN✔ (maker-checker is permission-based) | §3 |
| 14 | In-app notifications | `notifications` `PM/V319:13`; `NotificationService.java:74,104` | "through `NotificationService`" (`p3-16.md:84`) | REUSE · **PDEP** | **`RH-007`** |
| 15 | Notification category | `PJ/constants/NotificationCategory.java:14` — a **Java enum**, no `WAREHOUSE*` | not named (0 hits) | **PDEP** | **`RH-007`** |
| 16 | Email templates | `PJ/service/notification/email/EmailTemplateDefaults.java:82` — code-registered | not named (0 hits) | **PDEP** | **`RH-007`** |
| 17 | SMS | `NotificationDeliveryService.java:423` — `// TODO: Implement SMS` | `whb_alert_rules.notify_sms` | **GAP** | **`RH-007`** |
| 18 | WhatsApp | `WhatsAppProviderRegistry`, `AisensyWhatsAppProvider` | `p2-14.md:28` reuses | REUSE | — |
| 19 | Push | `FCMService.java:36-103`, `notification_devices` `PM/V319:217` | `notify_push` column | REUSE (unnamed, fits) | — |
| 20 | Documents + viewer | `PM/V81:39` (no polymorphic owner); `PF/components/common/DocumentViewerPane.tsx:97`, `DocumentPreviewModal.tsx:62`, `useDocumentViewerControls.ts` | `whb_document_links`; the viewer is named nowhere (0 hits) | REUSE · one line owed | `RH-012` |
| 21 | Audit / activity | `audit_logs` `PM/V5:6`; `user_activity_logs` `PM/V717:29` **opt-in per role/user** (`PM/V719:12-13`); `all_activity_history` dealer-owned | `whb_audit_events` own; stay out of the view | OWN✔ · one stale PD row | `C-048`, **`RH-012`** |
| 22 | Number series | `SequentialCodeGenerator` (not gapless); `acc_number_series` `accounting-base/…/V600080:110-175` | `whb_number_series` with `branch_id` | OWN✔ · **branch key ambiguous under M:N** | `C-019`, **`RH-005`** |
| 23 | `admin_settings` / `global_settings` | `PM/V110:5-24` (description `VARCHAR(255)` `PM/V157:112`); `PM/V337:8-43`, `WAREHOUSE` allowed `PM/V553:14-15` | P0-15 `V501100` | REUSE | `RE-003` |
| 24 | Grid config | `PM/V18:7,25,43`, `PM/V229:8-20,52-53` | every grid | REUSE | R1 `T-8` |
| 25 | Export | `PJ/service/BaseExportService.java:39,62,119` | every grid | REUSE | PD §5.3 |
| 26 | Import (frontend) | `ImportModal.tsx:174` cap = `bulk_import_max_rows` (`PM/V628:11`, default **500**), client-side parse (`useImport.ts`) | PD §1.7 "reusable as-is for … opening stock" | **wrong verdict** | **`RH-009`** |
| 27 | Dashboards / widgets | `widget_definitions.chk_module` (`PM/V557:16-18`); `widget:<group>:view:all|branch` `PM/V722:37-49`; `DashboardWidgetScopeResolver.java:104-118,377-381`; `PF/components/dashboard/widgets/registry.ts:35` | P0-01 widens `chk_module` only | **PDEP ×3** | **`RH-006`** |
| 28 | Holidays / working hours / weekly off | `holiday_calendars` `PM/V753:19`; `holiday_calendar_assignments.branch_id :117-142`; `branch_working_hours` `PM/V294:11,30`; `weekly_off_patterns` `PM/V751:26,57` | `wh_working_calendars` (v2) re-keys holidays | **DUP (v2)** | **`RH-011`** |
| 29 | Shifts / leave / attendance | no shift table anywhere; leave `PM/V747–V759`, attendance `PM/V296` | none in v1 | OWN✔ / not needed | §3 |
| 30 | Currency / timezone / date format | `currencies` `PM/V203:5`; `users.timezone_id`, `date_format_code` `PM/V60:85-87`; `timezones` `PM/V55:31` | `whb_warehouses.timezone` free string | **GAP** (validate against master) | **`RH-011`** |
| 31 | i18n | per-module `<Mod>SafeTranslation.tsx`; `en`/`fr`/`hi` | P0-01 | REUSE | `C-050` |
| 32 | Public no-login pages | `SecurityConstants.PUBLIC_PATTERN :16`; `(public)` route groups (assets, dealer) | none in v1 | n/a v1 | `RD-007` |
| 33 | QR | `PJ/service/QrCodeService.java:33,54` | labels | REUSE | `RD-006` |
| 34 | Mobile offline | none (`mobile/src/config/reactQuery.ts:70` `networkMode:'online'`) | v1.1 queue | OWN✔ | `RD-003`, PP-12 |
| 35 | Mobile navigation + menu gate | `mobile/src/navigation/screens/lazyScreens.ts:1954`; `RootNavigator.tsx:4771`; `GenericScreen.tsx:41-47`; `menuService.ts:303,320`; `BottomTabNavigator.tsx:516-534` | no touchpoint (MODULE-INTEGRATION: 0 "mobile" rows) | **GAP** | **`RH-008`** |
| 36 | Backup | `DatabaseBackupService.java:36` — no restore | PP-1 | PDEP (filed) | PP-1 |
| 37 | Rate limiting | `RateLimitingFilter.java:151-178`; `/public/**` exempt | v2 per-client | covered | `RD-007` |
| 38 | API keys | none (only `BoomBarrierWebhookController.java:62`) | `whb_api_clients` v2 | OWN✔ · one wrong FK | PP-2, **`RH-004`** |
| 39 | Reports / scheduling | `report_types` `PM/V431`; `scheduled_report_configs/_recipients/_executions` `PM/V429:3,33,48`; `ReportDataProviderRegistry.java:23-25` (`List<>`, 6 modules implement) | "no scheduling substrate in v1" (R18) | **GAP** — refusal wrong | **`RH-010`** |

```bash
cd /Users/bbhushan/work/git2/workspace/classic
grep -rl "BranchScopeService" --include=*.java . | grep -v /test/ | awk -F/ '{print $2}' | sort | uniq -c
#   46 accessories · 67 assets · 8 automotive · 25 dealer · 3 platform · 4 services  (153 files)
grep -rhoE "'[a-z0-9_:-]+:view:branch'" --include=*.sql . | sort -u | wc -l          # 94
grep -rhoE "useUserBranches\([^)]*\)" --include=*.ts --include=*.tsx . | wc -l      # 254
grep -rhoE "useUserBranches\(\)" --include=*.ts --include=*.tsx . | wc -l           # 154 — no branchType
cd warehouse-issues
for t in BranchScopeService "view:all" DashboardWidgetScopeResolver NotificationCategory \
         EmailTemplateDefaults company_branches scheduled_report "registry.ts" RootNavigator lazyScreens; do
  printf "%-30s %s\n" "$t" "$(grep -rn "$t" docs issues | wc -l)"; done                # all 0
```

**Inventory arithmetic:** 39 rows.

| Verdict | Count | Rows |
|---|---|---|
| REUSE (fits) | 13 | — |
| OWN✔ | 11 | — |
| GAP | 8 | 1, 5, 6, 17, 26, 30, 35, 39 |
| PDEP | 5 | 14–16, 27, 36 |
| DUP | 2 | 3, 28 |

Rows 1 and 3 are double-classed; see the table.

---

## §2 · The findings

### `RH-001` · Every branch predicate in the set binds `whb_warehouses.branch_id`, which the M:N decision removes; platform's only branch-scope SQL fragment is column-shaped; and the one live M:N guard treats an unlinked warehouse as visible to everyone — **BLOCKER**

**What is missing or wrong.**

- **The scalar is load-bearing in eight places**, all written for a warehouse that belongs to exactly one
  branch:
  - `FR-079` (`WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md:219`, *"belongs to exactly one branch (`branch_id
    NOT NULL`)"*)
  - DATA-MODEL `whb_warehouses` `idx(branch_id)` (`DATA-MODEL.md:452`), and FK `B1` (`:1411`), whose note
    reads *"Do not repeat accessories' many-to-many junction"*
  - `:3991`, which drops the prior art's `wms_warehouse_branches` junction *"because one branch, one
    GSTIN"*
  - `p1-05.md:56-57` and `:130-132`
  - `WS-016`'s grid column `branchName` *"via `branch_id`"* and its `companyId → branchId` cascade
    (`BUILD-SPEC-SCREENS.md:816,829-830`)
  - `P1-18`'s composition, *"2. Branch scope — the platform three-mode pattern"* (`p1-18.md:26-35`)
- **PD §2.3 prescribes the fragment the M:N model cannot use.** `PLATFORM-DEPENDENCIES.md:148-181`
  prescribes `BRANCH_FILTER_SQL` for *"every `RepositoryCustomImpl` query"*. Live, that fragment is
  `"… OR %s.branch_id IN (SELECT CAST(UNNEST(STRING_TO_ARRAY(…))))"`
  (`platform/…/service/common/BranchFilterService.java:167-169`). It binds a column on the queried alias,
  and under M:N neither `whb_warehouses` nor any ledger table has that column.
- **Accessories solved M:N once, with a rule warehouse must refuse.**
  `AccessoryStockTransferAccessGuard.isWarehouseAllowed` resolves a warehouse to its linked branches
  (`WarehouseBranchRepository.findActiveBranchIdsByWarehouseId`, `:96`) and allows it when
  `linked.isEmpty() || !Collections.disjoint(linked, scope.getUserBranchIds())`
  (`accessories/…/service/inventory/AccessoryStockTransferAccessGuard.java:186-206`). The comment names the
  rule: *"unassigned warehouses stay shared"*. For a stock ledger, "an unlinked site is visible to every
  branch-scoped user" is exactly the leak `FR-405` forbids.
- **Accessories' `is_primary` is not the `REGISTERED` link.** `accessory_warehouse_branch.is_primary`
  means *"the primary warehouse **for the branch**"* (`accessories/…/V30018:13,35`), which is the opposite
  axis to *"the registered branch **of the warehouse**"*. Copying the column name copies the wrong
  meaning.

**Why it matters.** Picture a dealer group with one parts godown serving a showroom branch and a service
branch. `P1-18`'s acceptance box
*"a storekeeper scoped to site A gets zero rows for site B on the grid, the export, the statistics strip
and every dropdown"* (`p1-18.md:86`) cannot be written as SQL: there is no `branch_id` to put in the
`WHERE`. Each engineer will improvise one of three predicates:

- `REGISTERED` only — the service-branch storekeeper sees nothing in the godown they work in;
- any link — correct;
- the accessories rule — unlinked sites leak.

`P1-18`'s own trap says *"the order of composition must be written down so two engineers do not build
two different intersections"* (`:33-35`), and today it is written against a column that is gone. Every
management query in two modules is built on this predicate, and it lands **before** `P1-18`'s
architecture rule freezes it.

**Negative evidence.**

```bash
cd warehouse-issues
grep -nE "^\| \`[a-z0-9_]+\` \|" docs/DATA-MODEL.md | grep branch_id | cut -d'|' -f2
#   whb_warehouses · whb_number_series · wh_transfer_orders · whin_gstin_profiles · whad_counter_sales · (wms_warehouse_branches, dropped)
grep -rn "whb_warehouse_branches\|allowedWarehouseIds\|any active link" docs issues   # 0
cd /Users/bbhushan/work/git2/workspace/classic
sed -n '167,169p' platform/backend/src/main/java/ai/platform/service/common/BranchFilterService.java
sed -n '186,206p' accessories/backend/src/main/java/ai/accessories/service/inventory/AccessoryStockTransferAccessGuard.java
```

**Where it belongs.** `warehouse-base` + `warehouse` · v1 · **P1** (`P1-18`), with `P0-15` and `P1-05`.

**Disposition.** Fold into `P1-18` as a new first section, *"Three attributions, one resolver"*, and
correct the scalar everywhere it appears.

*The line for `P1-18`:*

> **Access scope** is *any active link*: a branch-scoped caller may see warehouse W when an active
> `whb_warehouse_branches` row joins W to one of the caller's active `branch_staff` branches.
> **An unlinked warehouse is visible to no branch-scoped caller.** The `REGISTERED` rule makes every
> warehouse linked, and the resolver fails closed if it is not — the accessories *"unassigned warehouses
> stay shared"* arm (`AccessoryStockTransferAccessGuard.java:186-187`) is refused by name.
>
> **Resolve once, bind a set.** The resolver takes platform's `BranchScope` (`RH-002`) and returns
> `Set<UUID> allowedWarehouseIds`, where `null` means admin mode and empty means no access
> (short-circuit before SQL, per PD §2.3 item 2). Every query binds `:allowedWarehouseIds` against the
> denormalised `warehouse_id` (`DATA-MODEL.md:755`) — never a join to the junction on a ledger-sized
> table.
>
> **The architecture rule is re-aimed** from `:userBranchIds` to `:allowedWarehouseIds`.
>
> **Composition** is owner ∩ warehouses-from-branches ∩ warehouse grants (`RA-001`). A user with no
> warehouse-grant row keeps every warehouse their branches reach.

*The other edits:*

| File | Edit |
|---|---|
| `FR-079` | Rewrite to name the junction and the `REGISTERED` link |
| DATA-MODEL `B1` and `:3991` | Reverse |
| `WS-016` | `branchName` becomes *"`branches.branch_name` of the `REGISTERED` link"*, and a *Linked branches* column (count) is added |
| PD §2.3 | Items 1–3 re-point to the warehouse-id set |
| `P1-05` Trap *"Do not repeat the accessories junction"* | Replace with: *"the junction is the model; do not copy accessories' `is_primary` meaning (`V30018:35`) or its unlinked-is-shared guard"* |

**Irreversibility.** **Reversible** until `P1-18` ships. After that, it is every management query,
export, statistics map and dropdown in two modules re-touched, which is the same argument `RA-001` makes.

**Relationship to earlier rounds.** **New.** `RA-001` is the grant *table* for the warehouse axis; this is
the *branch* axis's mechanics once a warehouse has several branches. `O-005` corrected
`branches.owner_type`, not cardinality. R22 owns the junction's DDL; this finding owns how it is read.

---

### `RH-002` · The set re-specifies branch scoping from scratch while platform already ships it — `BranchScopeService` and the `<resource>:view:all` / `:view:branch` pair — so `P0-15` seeds no scope tier, `WH-SC-242`'s branch-scoped user cannot be granted, and `PP-13` asks platform to extract what it has already extracted — **BLOCKER**

**What is missing or wrong.**

- **The platform service exists and says so.**
  `platform/…/service/common/BranchScopeService.java:14-40` is a platform service whose javadoc reads:
  *"Resolves and enforces a caller's branch-access scope for pages that support the `<resource>:view:all`
  / `<resource>:view:branch` permission pair … Extracted from the copies that had accumulated … so every
  branch-scoped page shares one implementation."*
  - `resolve(principal, viewAll)` (`:110`) and `resolveStrict(principal, viewAll, viewBranch)` (`:143`,
    fails closed)
  - `BranchScope.allows` (`:96`), `assertBranchAccess` (`:208`) and `restrictToScope` (`:226`)
  - *"no permission combination yields unscoped access except `:view:all`"* (`:28-30`)
- **It is how the monorepo does this today.**
  - It is called from 153 files in six modules (§1.1 command), and 94 distinct `:view:branch`
    permissions are seeded.
  - `PM/V685__Add_users_view_branch_scope_and_branch_column.sql:20-47` is the pattern: ADMIN gets `:all`.
  - `:72-85` then states the Branch Admin rule: `:branch`, **never** `:all`.
  - The dashboard resolver keys off the same pair: `DashboardWidgetScopeResolver.java:377-381`
    (`hasAnyPageView` checks `:view`, `:view:all`, `:view:branch`, `:view:assigned`).
- **The warehouse set never mentions any of it.** `FR-404` (`:710`), `p0-15.md:44-46`, `p1-18.md:12-13`
  and `BUILD-SPEC-SCREENS.md:2320-2321` describe *"the three-mode view pattern — view-all, view-branch, no
  view"* as though it were new.
  - `grep -rn "view:all" docs issues` → **0**, and `BranchScopeService` → **0**.
  - `P0-15`'s permission set is `view/create/edit/delete/export` plus verbs, with **no tier permission**.
    So a *"branch-scoped"* user (`WH-SC-242`, `SCENARIO-CATALOGUE.md:489`) has no grant that makes them
    one. The only things left to distinguish the three users are role names, which `P1-18`'s own trap
    forbids (*"`hasAnyRole` skips named roles"*, `:72`).
- **The disposition of `PP-13` / `PD-D11` is wrong.** `IMPLEMENTATION-PLAN.md:1286` (`PP-13`) and
  `PLATFORM-DEPENDENCIES.md:695,814` (§4.11, `PD-D11`) recommend *"a platform-level `@BranchScoped`
  aspect … File as a platform task"*. The extraction happened. What remains missing — enforcement by
  aspect rather than by call — is a different ask and does not block anyone.

**Why it matters.** `WH-SC-242` is **v1·P0**. Without the pair, `P0-15` either ships a scope mechanism of
its own — a **duplicate** of a platform service whose whole reason for existing is that duplicates had
accumulated — or cannot pass its own scenario. The dashboard (`RH-006`) needs the pair too: the resolver
denies a widget whose source resource has no `:view*` grant at all, and falls back to branch scope only
through the pair. Every role grant written after go-live against a scope-less permission set has to be
re-migrated by hand.

**Negative evidence.**

```bash
cd warehouse-issues
grep -rn "view:all\|view:branch\|BranchScopeService" docs issues | grep -v reviews   # 0
sed -n '1286p' docs/IMPLEMENTATION-PLAN.md                                               # PP-13 — "Extract branch-scope enforcement to platform"
cd /Users/bbhushan/work/git2/workspace/classic
sed -n '14,40p' platform/backend/src/main/java/ai/platform/service/common/BranchScopeService.java
sed -n '72,85p' platform/backend/src/main/resources/db/migration/V685__Add_users_view_branch_scope_and_branch_column.sql
```

**Where it belongs.** `warehouse-base` · v1 · **P0** (`P0-15`), consumed by `P1-18`.

**Disposition.** Fold into `P0-15` and `P1-18`, and amend `PP-13` and `PD-D11`.

*The line for `P0-15`:*

> For every management resource, seed `<resource>:view:all` and `<resource>:view:branch` beside
> `:view`, with `menu_permission_dependencies` rows (`O-004`).
>
> - ADMIN and AUDITOR get `:all`.
> - Branch Admin gets `:branch` and **never** `:all` (`V685:72-85`).
> - The warehouse operational bundles (`RA-003`) get `:branch`.
>
> The three-mode pattern **is** `branchScopeService.resolveStrict(principal, VIEW_ALL, VIEW_BRANCH)`,
> wrapped by `RH-001`'s warehouse-set resolver.
>
> An `ArchitectureInvariantsTest` rule refuses any `ai.warehouse*` class that injects
> `BranchStaffRepository` or re-implements branch resolution.

**`PP-13` / `PD-D11`:** restate as *"reuse `BranchScopeService` (shipped). An aspect-level enforcement
is optional platform work, never blocking."* **`FR-404`:** name the pair.

**Irreversibility.** Reversible — they are seed rows — but P0: grants accumulate from the first install.

**Relationship to earlier rounds.** **New, and it corrects a disposition.** `RA-007` is the collision
between `PC-31` and §10.2 over **verb** strings; this is the missing **tier** strings. `PP-13` was
dispositioned against a platform that had already extracted the service.

---

### `RH-003` · The set states two contradictory models of what a site is — PD says a site **is** a platform branch, DATA-MODEL says it **belongs to** one — and under M:N neither holds; the evidence says link, never mirror — **MAJOR**

**What is missing or wrong.**

- **The two authorities disagree.**
  - `PLATFORM-DEPENDENCIES.md:45` (§1.1): *"A warehouse site **is** a platform branch with
    `branch_type='WAREHOUSE'`… `whb_locations` hangs off `branches.id`"*.
  - `:111-121` (§2.1): *"`whb_sites` carries its own code and references `branches.id`"*. That table name
    does not exist; DATA-MODEL `:3977` says so.
  - `DATA-MODEL.md:452-453`: `whb_warehouses` is its own table with its own `code`, and `whb_locations`
    hangs off `whb_warehouses`, not off branches.
  - The FRD follows DATA-MODEL; PD's green row was never corrected. No document asks the question the
    user's M:N decision now forces: *should a site also be a branch row?*
- **The case against mirroring, from the live code:**
  1. **`branch_code` is one global namespace.** `PM/V160:19`, `uk_branches_code UNIQUE (branch_code)`, and
     `Branches.java:25`. Every site would consume a code that competes with every showroom and service
     centre (`O-005` named the collision; this is its cost).
  2. **Pickers would fill with godowns.** Of 254 `useUserBranches(...)` calls, **154 pass no
     `branchType`**, and the endpoint returns every type (`useUserBranches.ts:73`; query key
     `branchType ?? 'all'`). Every no-arg picker — dealer, services, leave, attendance and more — would list
     warehouse sites the day the first one is created.
  3. **A branch-row site drags in HR config.** A site that is a branch needs `branch_staff` rows before
     anyone can be scoped to it (`BranchScopeService.java:25-27`). It inherits `holiday_calendar_assignments`
     (`PM/V753:117-142`), `branch_working_hours` (`PM/V294:11`) and `weekly_off_patterns` (`PM/V751:57`), all
     branch-keyed HR configuration. And through automotive's `company_branches` (`V10014`) it joins a
     company hierarchy warehouse does not own (`RH-004`).
  4. **Nobody in the monorepo made a warehouse a branch.**
     - accessories: `accessory_warehouses` + the `accessory_warehouse_branch` M:N (`V30017`, `V30018`)
     - dealer: `pdi_stock_yards` + the `pdi_stock_yard_branches` M:N (`V20078`, `V20123:8-43`)
     - assets: `asset_locations` (`V60004:2-25`) with a `branch_id` (`V60101:15`), whose ledger comment reads
       *"BRANCH IS NOT A COLUMN … `asset_locations.branch_id` is the only branch key"* (`V60586:59-60`)

     `'WAREHOUSE'` in `chk_branches_type` is exercised only by `BranchIntegrationTest.java:369`.

**Why it matters.** `P1-05` builds `whb_warehouses` (`V500012`) **before `PNR-1`**. A builder who reads PD
§1.1 first creates branch rows. The first week then produces the symptoms above — godowns in the showroom
picker, and a site no storekeeper can see until HR assigns them to it — and unwinding it means deleting
branch rows that other modules' FKs (`branch_staff`, holiday assignments) already reference.

**Negative evidence.**

```bash
cd warehouse-issues
sed -n '45p;111,121p' docs/PLATFORM-DEPENDENCIES.md      # "a site IS a branch" · "whb_sites"
sed -n '3977p' docs/DATA-MODEL.md                        # "There is no whb_sites"
cd /Users/bbhushan/work/git2/workspace/classic
grep -rln "'WAREHOUSE'" --include=*.java --include=*.ts --include=*.tsx platform | grep -v node_modules   # the test only
```

**Where it belongs.** `warehouse-base` · v1 · **P1** (`P1-05`).

**Disposition.** Fold into `P1-05` and amend PD §1.1 / §2.1.

**The recommendation, as the line for `P1-05`:**

> **A warehouse is linked to branches, never mirrored as one.** `whb_warehouses.code` is its own
> namespace; it is never derived from, copied to or validated against `branch_code`.
>
> **One exception.** When a site is itself a GST place of business and no branch row carries that
> GSTIN, the administrator first creates an **ordinary** branch (type `WAREHOUSE` or
> `DISTRIBUTION_CENTER`, carrying `gst_number`) and makes it the site's `REGISTERED` link. That branch
> is the tax and organisation anchor; the warehouse remains the stock anchor.
>
> Branch pickers on warehouse screens call `useUserBranches()` unfiltered: a warehouse may serve any
> branch type.

PD §1.1's green row changes to *"a site is **linked** to branches (M:N, one `REGISTERED`)"*, and §2.1
item 2 loses `whb_sites`.

**Irreversibility.** Reversible before `V500012`. After go-live, **irreversible in practice** — branch rows
acquire FKs from other modules.

**Relationship to earlier rounds.** **Extends `C-016` / `C-030` / `PD-1` / `O-005`**, none of which
compared PD §1.1 with DATA-MODEL, and none of which had an M:N premise to test. R14's refusal *"`whb_warehouses.code`
collides with `branches.branch_code`"* is **upheld**: the two codes stay independent, and this finding is
what keeps them independent.

---

### `RH-004` · The company axis has no platform anchor: `companies` and `company_branches` are automotive, branches carry no company, so `WS-016`'s `companyId → branchId` cascade is unimplementable, nothing ties the `REGISTERED` branch to `whb_warehouses.company_id`, and `whb_api_clients.company_id` points at an automotive table labelled "platform" — **MAJOR**

**What is missing or wrong.**

- **Platform has no company, and the only branch→company link is automotive.** Live, `companies` is
  created only by `automotive/…/V10002__Create_companies_table.sql:11-48`
  (`grep -rl "CREATE TABLE.*companies\b"` → that file alone). The branch→company link is automotive's M:N
  `company_branches` (`automotive/…/V10014:7-23`, `uk_company_branch`). `branches` has **no** `company_id`
  (V149, and no later ALTER). Accessories states the consequence in a comment: *"NO company_id — derived
  via branch → company_branches"* (`accessories/…/V30071:77`). In a standalone install (`D-7`) a branch
  belongs to no company at all.
- **`WS-016`'s cascade has nothing to call.** `WS-016` specifies `companyId` select → *"cascades to
  `branchId` select (`useUserBranches` …)"* (`BUILD-SPEC-SCREENS.md:829-830`, and the mobile block at
  `:844`). `useUserBranches` accepts `branchType` / `isFieldServiceRequired` only, and
  `/branches/my-branches` accepts `activeOnly`, `branchType` and `isFieldServiceRequired`
  (`BranchesController.java:578-593`). There is no company parameter to cascade on. CLAUDE.md rule 8
  forbids doing it with a frontend `.filter()`.
- **Nothing ties the GSTIN's legal entity to the warehouse's company.** Under M:N, the `REGISTERED`
  branch's GSTIN belongs to one legal entity, and `whb_warehouses.company_id → whb_companies`
  (`DATA-MODEL.md:450,452`) is another column. Nothing asserts that they agree, and in a standalone
  install nothing *can*: no table maps a `whb_companies` row to a branch.
- **One FK points at a vertical.** `whb_api_clients.company_id → companies (platform)`
  (`DATA-MODEL.md:882`) names an automotive table as platform. That is a `D-7` violation in `P5-22`'s DDL.

**Why it matters.** WS-016 is the first master screen an implementer opens. Its filter strip either
ships a cascade that does nothing, or a frontend filter the reviewer agent rejects. Worse, a warehouse can
be saved under company A with a `REGISTERED` branch whose GSTIN is company B's. Every transfer from it is
then classified supply or non-supply (`FR-080`, `IRR-57`) against the wrong entity, and that
classification is frozen on documents for periods already filed.

**Negative evidence.**

```bash
cd /Users/bbhushan/work/git2/workspace/classic
grep -rlE "CREATE TABLE( IF NOT EXISTS)? companies\b" --include=*.sql . | grep -v node_modules   # automotive/…/V10002 only
grep -n "company" platform/backend/src/main/resources/db/migration/V149__create_branches_table.sql  # 0
sed -n '578,593p' platform/backend/src/main/java/ai/platform/controller/BranchesController.java
cd warehouse-issues
grep -rn "company_branches\|whb_company_branches" docs issues                                    # 0
sed -n '882p' docs/DATA-MODEL.md | grep -o "companies (platform)"
```

**Where it belongs.** `warehouse-base` · v1 · **P0/P1** (`P0-07`, `P1-05`); `whb_api_clients` v2 · **P5** (`P5-22`).

**Disposition.** Fold into `P0-07`, `P1-05` and `P5-22`.

*The line for `P0-07`:*

> `whb_company_branches` (`company_id → whb_companies`, `branch_id ↓platform branches`, `is_active`,
> `uk(company_id, branch_id)`) is the warehouse-owned company axis.
>
> - It is maintained on WS-015.
> - `warehouse-adapter-dealer` seeds it from automotive `company_branches` through
>   `whb_company_external_refs`. **The adapter carries the read; the base never does.**

*The line for `P1-05`:*

> Saving a warehouse refuses a `REGISTERED` branch that is not in `whb_company_branches` for
> `whb_warehouses.company_id` (error code `WAREHOUSE_BRANCH_COMPANY_MISMATCH`).
>
> WS-016's branch options come from a warehouse endpoint returning *my-branches ∩ the company's
> branches*, intersected in the backend.

*The line for `P5-22`:* `whb_api_clients.company_id → whb_companies`, not `companies`.

**Irreversibility.** Reversible; all of it is after `PNR-1` except that the mismatch rule must exist before
the first transfer document is classified.

**Relationship to earlier rounds.** **New.** PD §2.8 and `C-035` establish that `companies` is automotive
for the *counterparty* question. No lens followed the company axis through the branch picker or the GSTIN
anchor, and no lens caught the `whb_api_clients` FK.

---

### `RH-005` · Under M:N, three rules that need "the warehouse's branch" now receive a set: the same-GSTIN transfer test, the per-branch statutory number series, and `whin_gstin_profiles` — which also stores a second copy of `branches.gst_number` with no equality rule — **MAJOR**

**What is missing or wrong.**

- **The supply test reads "the branch" of each end of a transfer.** `wh_transfer_orders` carries
  `source_branch_id` / `destination_branch_id` (`DATA-MODEL.md:1003`, `P1-17`), and the supply-vs-non-supply
  test is *"read `branches.gst_number` for source and destination and branch on equality"*
  (`PLATFORM-DEPENDENCIES.md:143`). With two linked branches per warehouse, the set never says which
  branch fills those columns.
- **The statutory number series is keyed by branch.**
  - `whb_number_series` is keyed `uk(owning_module, series_code, company_id, warehouse_id, branch_id)`
    (`DATA-MODEL.md:910`, WS-061 `BUILD-SPEC-SCREENS.md:1449`, `P1-09`).
  - `P2-IN-03`'s title is *"the delivery challan … on its own **per-branch** series"*. GST numbers
    documents per registration (GSTIN), so a warehouse linked to two branches could draw one challan
    series from either.
- **The GSTIN is stored a second time with no rule tying the copies.** `whin_gstin_profiles` stores
  `gstin` **unique** plus `branch_id` (`DATA-MODEL.md:1189`, `p2in-01.md:47`), while `p2in-01.md:51`
  asserts *"the GSTIN is read from the branch and profiled here — it is never duplicated"*. The column is
  a second copy of `branches.gst_number` (`PM/V182:7`), and no document states that the two must be equal.
- **The registration is not dated.** When a warehouse's `REGISTERED` link moves — a godown re-registered
  under another GSTIN — no document says the link is dated. `IRR-57`'s argument (a historical transfer
  must be classifiable for a filed period) applies to the link exactly as it applies to
  `tax_registration_id`.

**Why it matters.**

- **Month-end.** Two challans for the same GSTIN carry numbers from two series, which is a gap and a
  duplicate in one statutory register.
- **Supply test.** A transfer between two godowns that share a `REGISTERED` GSTIN — the cheap,
  non-supply case — is classified as a taxable supply because the service branch was picked for one end.
- **Drift.** A branch's GSTIN corrected on the platform Branches screen silently diverges from
  `whin_gstin_profiles.gstin`, which the e-way bill payload reads.

**Negative evidence.**

```bash
cd warehouse-issues
grep -rn "REGISTERED" docs issues | grep -iv "registered_at\|unregistered\|registration_type" | wc -l   # 0
grep -rn "gst_number" docs/DATA-MODEL.md issues/p2in-01.md | wc -l                                      # 0 — no equality rule
sed -n '1p' issues/p2in-03.md                                                                           # "per-branch series"
```

**Where it belongs.** `warehouse` (`P1-17`, `P2-02`) · `warehouse-base` (`P1-09`) · `warehouse-india`
(`P2-IN-01`, `P2-IN-03`) · v1 · **P1 / P2-IN**.

**Disposition.** Fold into those five tasks.

> **The `REGISTERED` link is the only branch any tax, statutory-numbering or supply rule reads.**
>
> - **Transfers.** `source_branch_id` / `destination_branch_id` are the `REGISTERED` branch of each
>   warehouse **at `dispatched_at`**, written once and frozen, as `L-7` freezes a conversion factor. A
>   transfer created before a re-registration keeps its classification.
> - **Number series.** A statutory series (challan, e-way-bill-bearing documents) is keyed by the
>   `REGISTERED` branch, never by the operating branch.
> - **`whin_gstin_profiles`.** Either drop `gstin` and read `branches.gst_number` through `branch_id`, or
>   keep it with a service equality check on save and a nightly drift row on the `P3-16` health grid.
>   Choose one in `P2-IN-01`; *"read from the branch"* and a unique `gstin` column cannot both stand.
> - **The link itself** (R22's table) carries `effective_from` / `effective_to`, so *"which GSTIN was
>   this warehouse registered under on 30 June"* is a query.

**Irreversibility.** **Irreversible per document.** A classification or a number, once printed on a
challan, is filed.

**Relationship to earlier rounds.** **New consequence of the M:N premise.** INDIA-LOCALISATION-PACK §3.3
records the GSTIN census (`:318-340`) but assumed one branch per warehouse.

---

### `RH-006` · Branch-level rollups double-count a shared warehouse, and the dashboard path the set relies on needs three platform edits it does not list — `FALLBACK_MODES`, the `widget:<group>` tier seeds, and the frontend widget module union — **MAJOR**

**What is missing or wrong.**

- **Rollups over a shared warehouse double-count.**
  - Every warehouse report and tile that groups or filters by branch (WS-210 godown statement in `P2-20`;
    `P2-21`; `P6-10`'s *"a branch-scoped user showing only that branch's numbers in every tile"*,
    `p6-10.md:37-38`) was specified when a warehouse had one branch.
  - Under M:N, a godown linked to three branches appears under all three, so the sum of branch totals is
    three times the company total.
  - Platform has **no** region, zone or cluster table to roll up through (a repo-wide grep finds none).
    `branches.parent_branch_id` exists (`PM/V149:65`) and nothing reads it.
- **Dashboard edit 1 — the fallback rule.** The widget scope a warehouse tile needs is resolved by
  `DashboardWidgetScopeResolver`, and its fallback rules are a **Java `Map.of`** that its javadoc forbids
  extending *"from a naming pattern"* (`platform/…/service/dashboard/DashboardWidgetScopeResolver.java:100-118`).
  Six of the ten entries `Map.of` accepts are used.
- **Dashboard edit 2 — the tier seeds.** Tier permissions are seeded per widget group:
  `widget:inventory:view:*` belongs to **dealer vehicles** and `widget:accessories:inventory:view` to
  accessories (`PM/V727:43,52`; `PM/V722:37-49`). A `widget:warehouse:*` group is needed.
- **Dashboard edit 3 — the frontend union.** The frontend widget registry closes the module union at
  `'platform' | 'dealer' | 'shared' | 'accessories' | 'assets' | 'services'`
  (`platform/frontend/src/components/dashboard/widgets/registry.ts:35`).
- **The set touches none of the three.** `P0-01` widens `chk_module` (`V500200`), the database half, and
  nothing else (`grep "registry.ts\|FALLBACK_MODES\|widget:warehouse"` → 0).

**Why it matters.** The first regional-manager dashboard is the moment this becomes visible: three
branches' tiles each show the full godown value, and their sum exceeds the valuation report by a factor
of three. `L-4`'s *"reconcile to each other"* exit criterion (`DECISIONS.md` §5 v1) fails between two
screens of the same product. Separately, the first warehouse widget either fails to type-check against
`registry.ts`, or renders with no scope because the resolver has no rule for its group.

**Negative evidence.**

```bash
cd /Users/bbhushan/work/git2/workspace/classic
sed -n '100,118p' platform/backend/src/main/java/ai/platform/service/dashboard/DashboardWidgetScopeResolver.java
sed -n '35p' platform/frontend/src/components/dashboard/widgets/registry.ts
grep -n "inventory" platform/backend/src/main/resources/db/migration/V727__Revoke_widget_branch_tiers_not_backed_by_page_access.sql
cd warehouse-issues
grep -rn "FALLBACK_MODES\|registry.ts\|widget:warehouse\|double.count" issues | wc -l      # 0
```

**Where it belongs.** `warehouse` · v1 (reports, `P2-20` / `P2-21` / `P2-27`) and v3 (`P6-10`);
`warehouse-base` · v1 (`P0-01`, the seeds). **Platform-dependency rows** for the resolver and the union.

**Disposition.** Fold into `P2-20` / `P2-21` (the rollup rule), `P0-01` (the seeds) and `P6-10` (the
platform edits).

> **The rollup rule, stated on every branch-grouped report header.**
>
> - **Stock and value** roll up to the `REGISTERED` branch only, so each warehouse is counted once.
> - **Flows and demand** roll up to the document's own branch (the counter sale's `branch_id`, the
>   transfer's ends).
> - A **branch-filtered** view of a shared warehouse shows its whole stock under each linked branch, and
>   the header says *"shared by N branches"*. A total row over a branch-filtered set is refused.
>
> **Seeds and edits.**
>
> - `P0-01` seeds `widget:warehouse:view`, `:view:all` and `:view:branch` (the `V722` shape) and the
>   `V727`-style source-page row.
> - `P6-10` adds one `FALLBACK_MODES` entry (`BRANCH`, source resource = the stock-position resource) and
>   one `'warehouse'` member of the `registry.ts` union.
>
> Both are platform commits, and both are listed in `PP-9`.

**Irreversibility.** Reversible, but a report that shipped with a double-counted total has been
exported.

**Relationship to earlier rounds.** **New.** R18's §3 row *"Are widgets scoped? — Yes"* (`:741`) checked
the scope, not the rollup, and not the platform files the scope needs. `C-014` owns only `chk_module`.

---

### `RH-007` · Warehouse notifications need three platform edits the budget does not list — a `NotificationCategory` enum value, a code-registered email template, and a menu-route binding — and the SMS channel the alert rules offer is a stub — **MAJOR**

**What is missing or wrong.** The set says, correctly, *"Notifications go through the platform's
`NotificationService`"* (`p3-16.md:84`, `p2-14.md:28`), and PD §1.9 lists the capability as *"EXISTS AND
FITS"*. What it does not see:

- **The category is a Java enum.** `NotificationCategory` is a platform enum
  (`platform/…/constants/NotificationCategory.java:14`) with members such as `LEAVE_APPROVAL` (`:35`) and no
  warehouse value. Unread counts bind to a menu route through `NotificationCategoryMenuMapping`, which
  resolves unknown category strings to nothing.
- **Email templates are registered in code.** They live in the platform class
  `EmailTemplateDefaults.java` (`register(new EmailTemplateDef(…))` at `:82` onward), and sibling modules
  reference its constants directly. Admin overrides live in `notification_templates` (`PM/V319:166`), but
  a key must first exist in code.
- **SMS does not send.** `NotificationDeliveryService.deliverViaSMS` logs and returns: *"`// TODO:
  Implement SMS sending via SMS gateway`"* (`:423`). `whb_alert_rules.notify_sms` (`DATA-MODEL.md:930`,
  `P3-16`) and `WS-080`-class alerts offer the channel anyway.
- **The count is wrong.** `PP-9` counts two platform files and `RE-003` counts three. The first
  warehouse notification adds up to three more.

**Why it matters.** `U-002` — *"nobody is told that work is waiting"*, a BLOCKER re-phased to **P2** —
is remediated by notifications. The first one warehouse sends needs a platform enum commit that no
task owns and no reviewer expects. A supervisor who ticks *SMS* on an expiry alert gets silence, and
the alert-events grid records the delivery as sent.

**Negative evidence.**

```bash
cd /Users/bbhushan/work/git2/workspace/classic
grep -n "^public enum\|WAREHOUSE" platform/backend/src/main/java/ai/platform/constants/NotificationCategory.java   # :14, no WAREHOUSE
grep -n "TODO: Implement SMS" platform/backend/src/main/java/ai/platform/service/notification/NotificationDeliveryService.java  # :423
cd warehouse-issues
grep -rn "NotificationCategory\|EmailTemplateDefaults\|notification_templates" docs issues | wc -l          # 0
```

**Where it belongs.** `warehouse-base` · v1 (`P2`, via `U-002`'s owner) and v1.1 (`P3-16`) ·
**platform-dependency rows**.

**Disposition.** Fold into `P3-16` and the task that carries `U-002`'s remediation, and add three rows to
PD §1.9 and `PP-9`.

> A warehouse notification needs:
>
> 1. `NotificationCategory.WAREHOUSE_*` values — a platform commit;
> 2. an `EmailTemplateDefaults` registration per email kind — a platform commit;
> 3. a menu row whose route the category mapping resolves — a warehouse migration.
>
> **`notify_sms` is hidden in the UI until platform ships an SMS gateway** (a platform dependency).
> `notify_push` reuses `FCMService` and `notification_devices` unchanged.

**Irreversibility.** Reversible.

**Relationship to earlier rounds.** **New.** R19 read `EmailTemplateService` for its *renderer*
(`RD-006`), not for its *registration*. PD §1.9 verified the tables and the listener.

---

### `RH-008` · `D-13` makes mobile mandatory, and the module-integration runbook has no mobile touchpoint: a new module's screen needs three navigation files and a string-matching gate, none named by any task — **MAJOR**

**What is missing or wrong.**

- **The runbook is silent on mobile.** `MODULE-INTEGRATION.md`'s 18-touchpoint matrix (§2) contains the
  word *mobile* **zero** times, and sixteen task files name a `mobile/src/screens/…` folder. Live, a
  screen is not reachable from that folder alone.
- **What a mobile screen actually needs:**
  1. a lazy registration in `mobile/src/navigation/screens/lazyScreens.ts` (accessories' warehouse list
     at `:1954-1956`);
  2. a route in `mobile/src/navigation/RootNavigator.tsx` (`:4771` for the same screen);
  3. a branch in `mobile/src/screens/GenericScreen.tsx`'s `routePath.includes(…)` / `menuName ===` chain
     (`:41-47` are its first arms; 2,783 lines);
  4. menus rows with `is_mobile_enabled = true`, which `menuService.ts:303,320` requires alongside
     `isActive && isVisible`;
  5. **every level-1 menu must have level-2 children**, or `BottomTabNavigator.tsx:516-534` drops it.
- **PD §7 left this open.** It lists *"Whether `mobile/src/screens/GenericScreen.tsx` gates a warehouse
  route"* as **UNVERIFIED** (`PLATFORM-DEPENDENCIES.md:885`). It is verified here: it does, by string
  match.
- **There is no shared scanner.** The one scanner is asset-specific (`screens/assets/AssetQrScannerScreen.tsx:130-131`,
  code types `qr`, `code-128`, `code-39`, `ean-13`, with no DataMatrix and no GS1).

**Why it matters.** Every v1 web task ships its mobile counterpart in the same task (`D-13`). The first
one that reaches review ships a screen folder no navigator reaches: *"done"* on paper, invisible on the
handheld. The failure is silent, like `ModuleImportSelector` — the gate R1 called *"the one everyone
forgets"*.

**Negative evidence.**

```bash
cd warehouse-issues
grep -ci "mobile" docs/MODULE-INTEGRATION.md                                             # 0
grep -rln "mobile/src/screens" issues | wc -l                                            # 16
grep -rn "lazyScreens\|RootNavigator\|GenericScreen\|BottomTabNavigator" issues | wc -l  # 0
cd /Users/bbhushan/work/git2/workspace/classic/mobile/src
grep -n "AccessoryWarehouseListScreen" navigation/screens/lazyScreens.ts navigation/RootNavigator.tsx
```

**Where it belongs.** all five modules + `mobile` · v1 · **P0** (`P0-01`, the runbook).

**Disposition.** Fold into `P0-01` and `MODULE-INTEGRATION.md` §2.

> The matrix gains touchpoints **19–23** as listed above. Each is **B/R**: the app builds, and the
> screen is unreachable.
>
> A warehouse L1 menu is seeded with at least one `is_mobile_enabled` L2 child before any mobile task
> merges.
>
> The shared RF scanner is a `P3` (v1.1) deliverable, extracted from `AssetQrScannerScreen` with GS1
> DataMatrix and GS1-128 added — a platform-adjacent mobile file, listed in `PP-9`.

**Irreversibility.** Reversible.

**Relationship to earlier rounds.** **New.** `C-044`, `RB-001` and `PP-3` concern mobile **filters**;
`RD-003` concerns the offline queue. No lens asked how a mobile screen becomes reachable.

---

### `RH-009` · PD §1.7 calls platform's import frontend *"reusable as-is for item master, opening stock and ASN import"*; it parses client-side under a global 500-row cap, and opening stock is 200k–1M rows — **MAJOR**

**What is missing or wrong.**

- **The platform importer is capped at 500 rows by default.** `ImportModal` computes
  `effectiveMaxRows = useBulkImportMaxRows() ?? config.maxRows ?? IMPORT_MAX_ROWS`
  (`platform/frontend/src/components/common/ImportModal.tsx:174`).
  - `IMPORT_MAX_ROWS = 500` (`platform/frontend/src/constants/import.ts:6`).
  - The admin setting `bulk_import_max_rows` is seeded `'500'` (`PM/V628:11`) and is **one value for
    every module's import**.
- **It parses in the browser.** The spreadsheet is parsed client-side (`ImportModal.tsx`,
  `hooks/useImport.ts`) and posted as rows.
- **The set's own target is three orders of magnitude larger.** PD §2.5 sets opening stock at
  **200k–1M rows** (`PLATFORM-DEPENDENCIES.md:221-222`), yet PD §1.7 (`:51`) marks the frontend half
  *"EXISTS AND FITS … reusable as-is"* for exactly that import. `P1-10` names the backend registry and
  says nothing about how a million-row file reaches it.

**Why it matters.** Go-live week: the implementer uploads the opening-stock workbook and gets *"maximum
500 rows"*. Raising the setting to a million raises it for every module's importer in the install, and
still parses a million rows in a browser tab. Opening stock is `P2-19`'s *"first-class feature, with a
signed reconciliation certificate"*, and v1's exit criterion begins *"imports an item master and opening
stock"*.

**Negative evidence.**

```bash
cd /Users/bbhushan/work/git2/workspace/classic
sed -n '174p' platform/frontend/src/components/common/ImportModal.tsx
grep -n "IMPORT_MAX_ROWS" platform/frontend/src/constants/import.ts
cd warehouse-issues
grep -rn "bulk_import_max_rows\|IMPORT_MAX_ROWS\|client-side" docs/PLATFORM-DEPENDENCIES.md issues/p1-10.md issues/p2-19.md | wc -l   # 0
```

**Where it belongs.** `warehouse-base` · v1 · **P1** (`P1-10`), consumed by `P2-19`.

**Disposition.** Fold into `P1-10`, and correct PD §1.7's verdict to **SHAPE-MISMATCH**.

> Imports above `bulk_import_max_rows` take a **server-side path**. The file is uploaded to platform
> `documents` (`whb_import_batches.document_id` already exists), then parsed, validated and applied
> by the handler in batches, with progress on the batch row.
>
> `ImportButton` is used only for the small masters.
>
> The global setting is not raised.

**Irreversibility.** Reversible.

**Relationship to earlier rounds.** **New.** R6 verified the cap exists (*"HOLDS"*,
`R6-prior-art-triage.md:554`). No lens compared it with PD §2.5's target, and `Z-003` / `Z-008` concern
import *modes* and reversal.

---

### `RH-010` · R18 refused *"schedulable reports"* as having *"no scheduling substrate in v1"*; platform ships one, pluggable by a module-local bean with zero platform commits — **MINOR**

**What is missing or wrong.**

- **The refusal.** R18 §4 (`R18-reporting-and-analytics-completeness.md:759`) refuses the finding and
  asks that *"the word schedulable … be struck"* from `P2-21`'s acceptance, sending it to `U-002`.
- **What platform ships:**
  - `scheduled_report_configs`, `_recipients` and `_executions` (`PM/V429:3,33,48`; recipients `USER`
    / `ROLE` / `GROUP` at `:43`)
  - `ReportGenerationScheduler`
  - `ReportDataProviderRegistry(List<ReportDataProviderInterface> providers)`
    (`platform/…/service/report/ReportDataProviderRegistry.java:23-25`), dispatching on `canHandle(reportType)`
    and implemented by six modules
  - `report_types.module` with no `CHECK` (`PM/V431`), which `COEXISTENCE.md:537-547` already verified
- **So a warehouse schedule is module-local.** It is one `WarehouseReportDataProvider` bean plus
  `report_types` rows.

**Why it matters.** A v1 acceptance line is about to be struck for a capability that costs one bean. The
low-stock report is exactly what a buyer wants emailed at 07:00.

**Negative evidence.**

```bash
cd /Users/bbhushan/work/git2/workspace/classic
sed -n '23,25p' platform/backend/src/main/java/ai/platform/service/report/ReportDataProviderRegistry.java
grep -rl "implements ReportDataProviderInterface" --include=*.java . | wc -l               # 6
cd warehouse-issues
grep -rn "scheduled_report\|ReportDataProvider" docs issues | wc -l                         # 0
```

**Where it belongs.** `warehouse` · v1 · **P2** (`P2-21`).

**Disposition.** Fold into `P2-21`, and reverse R18's refusal row.

> *Schedulable* stays. It is met by a `ReportDataProviderInterface` bean registered against
> `report_types` rows `module = 'warehouse'`.
>
> **UNVERIFIED, and required:** that a scheduled run applies the **recipient's** branch and owner
> scope, not the creator's. Settle by reading `ReportDataProviderInterface`'s signature before
> writing the provider. If the interface carries no principal, the provider resolves each
> recipient's scope itself (`RH-001`, `RH-002`).

**Irreversibility.** Reversible.

**Relationship to earlier rounds.** **Corrects R18 §4's disposition.** `U-002` still owns alert rules.

---

### `RH-011` · The working calendar re-keys holidays that platform already assigns per branch, and `whb_warehouses.timezone` is a free string beside a platform timezone master — **MINOR**

**What is missing or wrong.**

- **Platform already has branch-assignable calendars:**
  - `holiday_calendars` (`PM/V753:19`) and `holidays` (`:69`)
  - `holiday_calendar_assignments`, which attaches a calendar to exactly one of branch, department or user
    (`:117-142`, `chk_hca_exactly_one_target :131`)
  - `branch_working_hours` (`PM/V294:11`, `uk(branch_id, day_of_week) :30`)
  - `weekly_off_patterns` with `scope_type 'BRANCH'` (`PM/V751:26,57`)
- **The v2 calendar re-enters them.** `wh_working_calendars` / `_days` (`DATA-MODEL.md:1062-1063`,
  `P5-10`, v2) carry `day_kind = 'DATE'` holiday rows of their own.
- **The timezone has no validation.** `FR-439` (v1·P0) stores the site timezone as a free string
  (`whb_warehouses.timezone`, `:452`), while platform has a `timezones` master (`PM/V55:31`) and
  `users.timezone_id` (`PM/V60:85-87`).

**Why it matters.** Diwali is entered twice, in HR and in the warehouse, and the SLA clock and the leave
ledger disagree the first year one copy is corrected. A mistyped `Asia/Kolkatta` buckets a site's local
day in UTC.

**Negative evidence.**

```bash
cd warehouse-issues
grep -rn "holiday_calendars\|holiday_calendar_assignments\|branch_working_hours\|timezones" docs issues | wc -l   # 0
```

**Where it belongs.** `warehouse-base` · v1 (`P1-05`, the timezone) · `warehouse` · v2 (`P5-10`, the calendar).

**Disposition.**

> **`P1-05`:** `whb_warehouses.timezone` is validated against platform `timezones`.
>
> **`P5-10`:** a warehouse calendar layers per-client cut-offs and exceptions **over** the `REGISTERED`
> branch's platform holiday assignment, read-only, and never re-enters a public holiday.

**Irreversibility.** Reversible.

**Relationship to earlier rounds.** **New.** `FR-181` was written without a platform comparison.

---

### `RH-012` · Three platform facts the reference documents state wrongly or omit: activity telemetry is opt-in per role, the shared document viewer is named nowhere, and the prior warehouse module's *code* survives on `origin/warehouse` — **MINOR**

**What is missing or wrong.**

1. **Telemetry is opt-in, not free.** PD §1.10 (`PLATFORM-DEPENDENCIES.md:54`) says *"Free write-auditing
   for every warehouse controller"*. `user_activity_logs` is written only for a user or role with
   `activity_tracking_enabled` (`PM/V719:12-13`; column at `:26`).
2. **The document viewer is never named.** The set names platform `documents` and its own
   `whb_document_links`, and never the shared viewer — `DocumentViewerPane.tsx:97`,
   `DocumentPreviewModal.tsx:62`, `useDocumentViewerControls.ts` (zoom 0.5–3). A GRN-photo or
   damage-certificate screen built without it is a second viewer (`grep` → 0 in `docs/` and `issues/`).
3. **The deleted module's code still exists.** `classic` has remote branches `origin/warehouse` (last
   commit `2244152dc0`, 2026-04-11) and `origin/warehouse-backup`, carrying `warehouse-core/` and
   `warehouse-base/` with migrations `V190001…`. That is the deleted module whose leftovers `D-3` and
   `PD` §1.15(a) describe. R6 triaged the `classic-issues` **documents**, not this code. The migrations
   there sit in a band (`V190000+`) that `D-2` does not use, so there is no collision. But it is the
   only place the prior module's permission names — the `wms_*` exclusions in `V528` / `V663` — can be
   read from source.

**Why it matters.** An auditor told that every warehouse write is telemetered will find gaps for every
role nobody flagged. The other two items are cost only: a second viewer, or prior art re-derived.

**Negative evidence.**

```bash
cd /Users/bbhushan/work/git2/workspace/classic
grep -n "activity_tracking_enabled" platform/backend/src/main/resources/db/migration/V719__*.sql | head -2
git branch -r | grep -i warehouse; git log -1 --format='%h %ad' --date=short origin/warehouse
```

**Where it belongs.** documentation · v1.

**Disposition.** Correct PD §1.10 to *"opt-in per role (`V719`)"*. Add the three viewer components to
`P1-04`'s document-link task. Add one row to R6's source list naming `origin/warehouse` as un-triaged
code prior art.

**Irreversibility.** Reversible.

**Relationship to earlier rounds.** **New.** (1) corrects `PD` §1.10 and `C-049`'s *"free"* framing.

---

## §2.1 · New platform dependencies

None of these is on PD §3 or `PP-1`…`PP-13`. Each is a platform (or platform-adjacent) commit that
warehouse cannot make inside its own modules.

| # | Dependency | File | Needed by | Version | Finding |
|---|---|---|---|---|---|
| PDEP-1 | `NotificationCategory.WAREHOUSE_*` enum values | `PJ/constants/NotificationCategory.java:14` | the first warehouse notification (`U-002`) | v1 · P2 | `RH-007` |
| PDEP-2 | `EmailTemplateDefaults` registrations per warehouse email kind | `PJ/service/notification/email/EmailTemplateDefaults.java:82` | document e-mail (`P2-14`), alerts | v1 · P2 | `RH-007` |
| PDEP-3 | An SMS gateway behind `deliverViaSMS` | `NotificationDeliveryService.java:402-423` | `whb_alert_rules.notify_sms` | v1.1 · P3 | `RH-007` |
| PDEP-4 | One `FALLBACK_MODES` entry for the warehouse widget group (≤10 entries in `Map.of`, 6 used) | `DashboardWidgetScopeResolver.java:104-118` | `P6-10`, any v1 widget | v1 / v3 | `RH-006` |
| PDEP-5 | `'warehouse'` in the widget module union | `platform/frontend/…/widgets/registry.ts:35` | the first widget | v1 / v3 | `RH-006` |
| PDEP-6 | Mobile navigation touchpoints — `lazyScreens.ts`, `RootNavigator.tsx`, `GenericScreen.tsx` | `mobile/src/navigation/…`, `mobile/src/screens/GenericScreen.tsx` | every mobile counterpart (`D-13`) | v1 · P0 onward | `RH-008` |
| PDEP-7 | A shared barcode/RF scanner component with GS1 DataMatrix / GS1-128 | extract from `mobile/src/screens/assets/AssetQrScannerScreen.tsx` | RF task flows | v1.1 · P3 | `RH-008` |

**Withdrawn:** `PP-13` / `PD-D11` (*"extract branch-scope enforcement to platform"*). It is **already
shipped** as `BranchScopeService`; see `RH-002`.

**Not a platform dependency, stated so nobody files one:**

- the scheduled-report engine (`RH-010`) — module-pluggable;
- the company axis (`RH-004`) — warehouse-owned `whb_company_branches`;
- the import server path (`RH-009`) — warehouse-owned.

---

## §3 · What I checked and found sound

| What I went looking for | Where it is covered |
|---|---|
| **Departments and designations are not a scope axis** | `PM/V13:5-74` — both global, no `branch_id`; `branch_staff.department` is free text (`PM/V150:19`). The set rightly never uses them for scope or routing |
| **Approval delegation** | Platform has only `permission_delegations` (`PM/V25:132`), no approval-task delegation. Warehouse's maker–checker is permission-based (`FR-408`), so an absent approver is covered by a role grant. Nothing to reuse, nothing duplicated |
| **Shifts** | No shift table exists in any module; "shift" in the set is prose. Correct to own nothing in v1 |
| **Number series and audit trail owned, not borrowed** | `SequentialCodeGenerator` is not gapless, and `acc_number_series` (`accounting-base/…/V600080`) is behind `D-7`. `whb_number_series` and `whb_audit_events` are correctly warehouse-owned (`C-019`, PD §2.6). Only the M:N branch key is wrong (`RH-005`) |
| **Job-run tracking** | Platform has 19 `@Scheduled` classes and no job-run table or ShedLock. `whb_job_runs` is correctly warehouse-owned |
| **WhatsApp and push** | `p2-14.md:28` reuses `AisensyWhatsAppProvider` and adds no provider; `FCMService` + `notification_devices` fit `notify_push` unchanged |
| **`global_settings` / `admin_settings`** | `WAREHOUSE` is already allowed (`PM/V553:14-15`); `admin_settings.category` has no CHECK. The 255-char `description` limit (`PM/V157:112`) is the only trap, and it belongs to `RE-003`'s seed-completeness fix |
| **Grid config, export, QR, i18n, backup, rate limiting, offline, API keys** | All REUSE or already owned — rows 24, 25, 31, 33, 34, 36–38 of §1.1 — by R1, `RD-003`, `RD-006`, `RD-007`, `PP-1`, `PP-2` |

---

## §4 · Refused

1. **"`widget_definitions.chk_module` rejects `warehouse`."** → `C-014`, `PP-5`, `P0-01` `V500200`.
   `RH-006` files only the three *other* files the dashboard needs.
2. **"`permission_dependencies` grants nothing at runtime."** → `O-004`.
3. **"`branches.owner_type` no longer exists; `branch_code` is global."** → `PD-1`, `MI-4`, `O-005`.
   `RH-003` uses the global namespace as *evidence* for the link-not-mirror recommendation and does not
   re-file it.
4. **"No warehouse-scoped grant table."** → `RA-001`. `RH-001` is the branch axis under M:N and composes
   with it.
5. **"`all_activity_history` is dealer-owned."** → `C-048`, `T-14`.
6. **"Documents have no polymorphic owner."** → `C-018`, PD §2.4.
7. **"No restore path / no service principal / no offline queue / no label renderer."** → `PP-1`, `PP-2`,
   `PP-12`, `PP-10`.
8. **"Public endpoints are rate-limit-exempt and the allow-list is hard-coded."** → `RD-007`.
9. **"Email template renderer is a flat string map."** → `RD-006`. `RH-007` is about *registration*, not
   rendering.
10. **"Mobile date filters."** → `RB-001` / `PP-3`.
11. **"An accessories-style `ACCESSORY_WAREHOUSE` scope / `accessoryWarehouse` screen / `widget:accessories:warehouse:*`
    name collides with warehouse."** Refused. Warehouse's scopes are `WAREHOUSE_*`, its mobile folders
    `whb*`, and its widget group will be `widget:warehouse:*` (`RH-006`). No live collision.
12. **"Warehouse should reuse leave/attendance for labour standards."** Refused for v1. Labour is `P6-03`
    (v3); `attendance_records` (`PM/V296`) is the obvious source then, and naming it now would be
    speculative.

---

## §5 · Counts

```bash
cd warehouse-issues/docs/reviews
grep -cE '^### `RH-[0-9]{3}`' R23-platform-alignment.md                                  # 12
grep -E '^### `RH-' R23-platform-alignment.md | grep -oE '\*\*(BLOCKER|MAJOR|MINOR)\*\*$' | sort | uniq -c
#   2 **BLOCKER**
#   7 **MAJOR**
#   3 **MINOR**
```

| Severity | Count | Findings |
|---|---|---|
| **BLOCKER** | 2 | `RH-001` `RH-002` |
| **MAJOR** | 7 | `RH-003` `RH-004` `RH-005` `RH-006` `RH-007` `RH-008` `RH-009` |
| **MINOR** | 3 | `RH-010` `RH-011` `RH-012` |
| **Total** | **12** | |

**Inventory:** 39 platform capabilities.

- 13 REUSE, 11 OWN✔, 8 GAP, 5 PDEP, 2 DUP.
- **7 new platform dependencies**; **1 withdrawn** (`PP-13`).
- **3 earlier dispositions corrected:** `PP-13` / `PD-D11`, R18 §4 row 759, PD §1.7.

**Affected tasks:**

- `P0-01` `P0-07` `P0-15`
- `P1-04` `P1-05` `P1-09` `P1-10` `P1-17` `P1-18`
- `P2-02` `P2-19` `P2-20` `P2-21` `P2-IN-01` `P2-IN-03`
- `P3-16` `P5-10` `P5-22` `P6-10`

**Affected documents:**

- `FR-079` `FR-404` `FR-439`
- `DATA-MODEL.md` `:452`, `:882`, `:1003`, `:1189`, `B1` `:1411`, `:3991`
- `PLATFORM-DEPENDENCIES.md` §1.1, §1.7, §1.9, §1.10, §2.1, §2.3, §4.11, `PD-D11`
- `IMPLEMENTATION-PLAN.md` `PP-9`, `PP-13`
- `MODULE-INTEGRATION.md` §2
- `BUILD-SPEC-SCREENS.md` WS-016, WS-061
- `R18` §4

**No migration version is invented.** Every change rides its owning task's existing band. **No screen id
is taken.** `whb_company_branches` (`RH-004`) is maintained on the existing WS-015.

**Owed, not done here** (this file edits nothing else):

- a `DECISIONS.md` §6 row for `RH-001`…`RH-012`;
- the `tools/check-design-set.py` two-letter-register extension, which §6 already records as undischarged.
