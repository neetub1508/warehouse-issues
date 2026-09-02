# R14 — Re-verification against the live codebase and the sibling design sets

**Date:** 2026-09-02 · **Finding prefix:** `O-` (`O-001`…) — note `OD-n` is a *different*, pre-existing
register (open decisions); no bare `O-` in this document refers to it.

**File set actually read.**

```bash
# design set under review
ls /Users/bbhushan/work/git/workspace/warehouse-issues/docs/*.md | wc -l          # → 14 reference documents
ls /Users/bbhushan/work/git/workspace/warehouse-issues/issues/*.md | wc -l        # → 148 task + epic files
ls /Users/bbhushan/work/git/workspace/warehouse-issues/docs/reviews/*.md | wc -l  # → round-1 R1..R7 + round-2 R8..R12
# sibling set
ls /Users/bbhushan/work/git/workspace/accounting/docs/*.md | wc -l
ls /Users/bbhushan/work/git/workspace/accounting/issues/*.md | wc -l
# prior art
ls /Users/bbhushan/work/git/workspace/classic-issues/*/docs/**/*.md 2>/dev/null | wc -l
```

Read in full: `DECISIONS.md`, `MODULE-INTEGRATION.md`, `PLATFORM-DEPENDENCIES.md`, `COEXISTENCE.md`,
`PORT-AND-ADAPTER-CONTRACT.md`, `GAP-REGISTER.md` §2.5/§4/§5/§7, `DESIGN-SET-DEFECTS.md` §1/§2/§6.4,
the §2 heading lists of `R8`–`R12`; targeted reads of `DATA-MODEL.md`, `BUILD-SPEC-SCREENS.md`,
`SCENARIO-CATALOGUE.md`, `IRREVERSIBLE.md`, `IMPLEMENTATION-PLAN.md`, `INDIA-LOCALISATION-PACK.md`,
`WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md`, and the task files named in each finding. On the live side:
every file cited by the 22-row touchpoint matrix, plus `FlywayConfiguration.java`,
`CacheConfiguration.java`, `filterUtils.ts`, `ModuleImportSelector.java`,
`UserActivityTrackingAspect.java`, both platform and `accounting-base` `ArchitectureInvariantsTest`,
all eleven migrations that rebuild the two platform `CHECK` constraints, and the accessories
inventory service/entity/migration set.

**Method, in three sentences.** I took every factual claim the set makes about the `classic`
monorepo and re-executed it against the checkout at HEAD, recording a live/stale verdict and a fresh
`file:line` for each; where a claim was a count, I recomputed it with a command rather than trusting
the number. I then diffed the warehouse set against the `accounting` design set field by field at the
seam D-6 declares, and against the `classic-issues` prior art for issue rigour. I filed nothing
without first grepping `docs/` and `issues/` for the capability, the table and the word, and I
dropped every candidate that round 1 or lenses `Q-`/`H-`/`U-`/`Y-` had already reached.

---

## §1 · Verdict

The set's picture of the live monorepo is in far better shape than I expected: I re-executed all 22
rows of the integration matrix and every one of them resolves to the file and line it claims, with
content that still means what the set says it means. The stale-fact discipline is real — `MI-4`,
`PD-1` and §10 correctly record that `branches` stopped being polymorphic, that
`global_settings.chk_global_setting_module` already admits `'WAREHOUSE'` for free, and that
`widget_definitions.chk_module` does not; all three still hold at HEAD. What has decayed is
exactly what the set warned would decay — the four registry counts, which are now stated five
different ways across four documents while the live numbers are 218 and 240. The expensive problem is
not in `classic` at all: it is that **the `accounting` design set still does not know warehouse
exists**, records it as ABSENT in its own integration matrix, and carries a Mode C invariant —
*"must require **zero change** to `accounting-base`"* — that `D-6` directly contradicts. Worse, the
schema `OD-1` needs accounting to stand down (`acc_godowns`, `V600136`/`V600137`) is scheduled in
accounting's **P1**, not its P3, so `OD-1`'s stated deadline of *"before accounting's P3"* is already
one phase late. Two further seam defects fall out of the same blind spot and neither set has noticed:
accounting's `account_strategy` vocabulary is closed and has no strategy keyed on reason code, item
group or owner type, so the classification quad `WH-SC-156` hands over cannot be resolved to an
account; and the two sides' status ladders do not map, leaving a discarded or predecessor-blocked
envelope stuck at `PENDING` in warehouse forever on a column that is `IRR-41` and lands at `PNR-1`.

**How much of `R1-codebase-reality.md` is still true.** Structurally, essentially all of it — every
path it names still exists and every mechanism it describes still behaves as described. What has
gone stale is its numbers and one of its conclusions: `C-016`'s *"`branches.owner_type` already
allows `'WAREHOUSE'`"* is void (`V160` dropped the column), and `R1`'s registry counts (202 cache
names, 210 filter scopes) are now 240 and 218. The set already corrects `C-016` in two reference
documents — but not in the two task files that repeat it as a Trap (`O-005`).

**The single unverified platform assumption that would cost the most if wrong.** None of the
load-bearing platform claims is unverified — I re-ran all of them. The costliest *unverified*
assumption in the set is therefore not about `classic` but about `accounting`: the set assumes
accounting will accept the `D-6` stand-down, and has written eleven documents and four task files on
that basis without a single reciprocal commitment in the accounting repository. If accounting
declines — and its own Mode C invariant gives it grounds to — `D-6`, `OD-1`, `OD-6`, `P0-12`, `P2-18`
and the whole `whb_cost_layers` / `whb_accounting_handovers` design collapse into a double ledger,
after `PNR-1` has already sealed the movement header.

---

## §2 · The findings

### `O-001` · The `accounting` design set has no third install state, records warehouse as ABSENT, and holds a Mode C invariant that `D-6` contradicts — and the stand-down lands in accounting's **P1**, not its P3 — **BLOCKER**

- **What is missing or wrong:** `D-6` (`docs/DECISIONS.md:146-193`) requires `accounting` to stand
  down its quantity-owning tables when warehouse is installed. `OD-1` (`:287`) records the reciprocal
  edit as owed, with the deadline *"Before accounting's P3"*. Three things are wrong with that in the
  live sibling set. **(a)** Accounting defines exactly two install states plus a generic third:
  `accounting/docs/ACCOUNTING-FUNCTIONAL-REQUIREMENTS.md:47-48` gives Mode B and *"**Mode C:** Mode A
  + any future vertical + its own adapter … Must require **zero change** to `accounting-base`"*. A
  warehouse that owns quantity is **not** zero change to `accounting-base` — it stands down
  `acc_stock_balances` (`accounting/docs/DATA-MODEL.md:507`), `acc_cost_layers` (`:434`),
  `acc_valuation_entries` (`:436`) and the `unit_cost` semantics of
  `acc_source_document_movements` (`:277`), all of which are `accounting-base` tables. `D-6` and
  accounting's Mode C invariant are in direct contradiction and neither set says so. **(b)**
  Accounting's own integration matrix lists warehouse as **absent**:
  `accounting/docs/MODULE-INTEGRATION.md:26` (`CF-2`) states *"Mode C (warehouse) has no counterpart
  here."* **(c)** The deadline is wrong. `acc_godowns` — the table that makes accounting
  quantity-aware — is `V600136`, and `accounting/issues/p1-04.md:5,13,15,20,43,45` schedules it in
  **P1**, module `accounting-base`. `accounting/docs/DATA-MODEL.md:4291` confirms
  *"`V600136 acc_godowns` — schema only, feature in P3 | P1-04"*: the **schema** lands in P1, the
  feature in P3. `OD-1`'s deadline of *"before accounting's P3"* therefore misses the migration by a
  whole phase, and a migration is the thing that cannot be un-shipped.
- **Why it matters:** The moment it bites is the day accounting's P1 runs `V600136`/`V600137` in a
  customer database. From then on `acc_godowns` and the quantity grain on `acc_cost_layers` are
  shipped schema in `accounting-base`, and a warehouse install has to either duplicate them or write
  a migration that drops another module's tables out from under it. Commercially the failure is
  worse than technical: two systems each believing they own the valued stock ledger produces two
  different closing stock values on the same date, and the finance controller has no way to say which
  is right. That is `D-6`'s entire reason for existing, and it is being lost to a scheduling error.
  Right now — today — the cost is zero: `ls accounting-base/backend/src/main/resources/db/migration/`
  in live `classic` shows 24 files and **none of them is `V600136`, `V600137` or `V600102`**. The
  edit is still a documentation edit. After accounting P1 it is a data migration.
- **Negative evidence:**
  ```bash
  cd /Users/bbhushan/work/git/workspace/accounting
  grep -rn "warehouse" docs/MODULE-INTEGRATION.md | head
  # → :26  CF-2 … "Mode C (warehouse) has no counterpart here."
  grep -rn "zero change" docs/ACCOUNTING-FUNCTIONAL-REQUIREMENTS.md
  # → :48  "Must require **zero change** to `accounting-base`"
  grep -rn "V600136" issues/p1-04.md | head -3
  # → :5, :13, :15  — phase P1, module accounting-base
  cd /Users/bbhushan/work/git/workspace/classic
  ls accounting-base/backend/src/main/resources/db/migration/ | wc -l          # → 24
  ls accounting-base/backend/src/main/resources/db/migration/ | grep -c 600136 # → 0
  ```
- **Where it belongs:** `warehouse-base` · v1 · **P0** (it is a decision deadline, not build work)
- **Disposition:** *is a `D-`/`OD-` decision, not a task* — **amend `OD-1` in
  `docs/DECISIONS.md:287`**, changing the Deadline cell from *"Before accounting's P3"* to
  **"Before accounting's **P1-04** ships `V600136`/`V600137` — the schema lands in P1, not P3
  (`accounting/issues/p1-04.md:5,13,15`)"**, and add a fourth sentence to the Decision cell: *"and
  accounting's Mode C invariant (`accounting/docs/ACCOUNTING-FUNCTIONAL-REQUIREMENTS.md:48`,
  'zero change to `accounting-base`') must be amended in the same edit, because a quantity-owning
  warehouse is not zero change."* **The concrete issue to file in `neetub1508/accounting` tomorrow:**
  *"Add a third install state — Mode D: `accounting-base` + a quantity-authoritative external stock
  system"*, whose body edits four files — `ACCOUNTING-FUNCTIONAL-REQUIREMENTS.md:47-48` (add Mode D
  and relax the Mode C invariant to *"zero change to the ledger core"*), `MODULE-INTEGRATION.md:26`
  (replace *"no counterpart here"* with the warehouse counterpart row), `DATA-MODEL.md:434,436,507`
  (mark `acc_cost_layers`, `acc_valuation_entries`, `acc_stock_balances` as *"not created when an
  external quantity authority is installed"*), and `issues/p1-04.md` (gate `V600136`/`V600137` on the
  absence of an external quantity authority) — **blocking accounting P1-04**.
- **Irreversibility:** irreversible on the *accounting* side at `V600136`. Reversible on the
  warehouse side today.
- **Relationship to round 1:** materially extends `OD-1`. New is the Mode C contradiction, the
  ABSENT row in accounting's own matrix, and the corrected deadline (accounting P1, not P3).

### `O-002` · `acc_posting_rule_lines.account_strategy` is a closed ten-value vocabulary with no strategy keyed on reason code, item group or owner type — so the classification quad `WH-SC-156` hands over cannot be resolved to an account — **BLOCKER**

- **What is missing or wrong:** `WH-SC-156` (`docs/SCENARIO-CATALOGUE.md:357`) is the load-bearing
  scenario for `D-6`. It states that the envelope *"carries the **classification quad** — movement
  type, reason code, item group and owner type — and **accounting resolves it to an account**: there
  is no chart of accounts and no posting-rule table anywhere in warehouse."* Accounting's account
  determination is `acc_posting_rule_lines.account_strategy`, and
  `accounting/docs/DATA-MODEL.md:280` gives its vocabulary in full and closed:
  `FIXED · PARTY_RECEIVABLE · PARTY_PAYABLE · ITEM_INCOME · ITEM_EXPENSE · ITEM_INVENTORY ·
  ITEM_COGS · TAX_INPUT · TAX_OUTPUT · COMPANY_DEFAULT`. Of the quad's four members: *item group* is
  reachable only if `ITEM_INVENTORY`/`ITEM_COGS` chain item → group → account (accounting does not
  say they do); *movement type* is reachable indirectly through which posting rule is selected; and
  **reason code and owner type have no strategy at all**. There is no `REASON_CODE_*`, no
  `OWNER_TYPE_*`, no `ITEM_GROUP_*` member. `accounting/docs/DATA-MODEL.md:3451` (`V-3`) confirms the
  vocabulary is enforced by a `CHECK` and is deliberately closed at `V600330`. Warehouse's side is
  equally explicit that it will not compensate: it has no chart of accounts by design.
- **Why it matters:** The moment it bites is the first month-end after go-live, on the Stock-to-GL
  Reconciliation screen (`WS-219`). A write-off, a shrinkage adjustment, a cycle-count variance and a
  customer-owned goods adjustment are four different reason codes with four different P&L
  destinations — write-offs to an expense account, shrinkage to a shrinkage account, customer-owned
  movements to **no** P&L account at all because the goods are not ours. With no reason-code strategy
  they all resolve through the same `ITEM_EXPENSE`/`ITEM_INVENTORY` pair. The controller sees a
  single lump in one account, cannot reconcile it to the movement register, and — critically —
  cannot tell that it is wrong, because the totals still balance. That is the definition of a
  BLOCKER: the number is wrong and nobody can tell. The owner-type case is the sharper one: posting
  a customer-owned adjustment to our own inventory account inflates the balance sheet with stock we
  do not own.
- **Negative evidence:**
  ```bash
  cd /Users/bbhushan/work/git/workspace/accounting
  grep -c "REASON_CODE\|OWNER_TYPE\|ITEM_GROUP" docs/DATA-MODEL.md   # → 0 as account_strategy members
  sed -n '280p' docs/DATA-MODEL.md   # the ten closed values, verbatim
  cd /Users/bbhushan/work/git/workspace/warehouse-issues
  grep -rn "account_strategy\|acc_posting_rule" docs/ issues/        # → 0 hits: the set never checked
  ```
- **Where it belongs:** `warehouse-base` · v1 · **P0** (the seam task), with the reciprocal edit in
  `accounting`
- **Disposition:** *fold into task `P0-12`* (`issues/p0-12.md`, the accounting seam). **Line to add
  under Traps:** *"**The receiving side cannot express the quad.**
  `accounting/docs/DATA-MODEL.md:280` closes `acc_posting_rule_lines.account_strategy` at ten values
  and none of them is keyed on reason code, item group or owner type. `WH-SC-156`'s promise that
  *'accounting resolves it to an account'* is therefore unimplementable as accounting is specified
  today. Either accounting adds `REASON_CODE_MAPPED`, `OWNER_TYPE_MAPPED` and `ITEM_GROUP_MAPPED`
  strategies (the reciprocal edit, `OD-1`), or `WS-051 GL Posting Rules` must carry the reason-code →
  account map on the warehouse side, which contradicts `WH-SC-156`. This must be decided before
  `V500042`."* Also add it to the `OD-1` reciprocal-edit list.
- **Irreversibility:** reversible in warehouse. Irreversible in accounting once the `CHECK` ships at
  `V600330`, per its own `V-3`.
- **Relationship to round 1:** **new.** No `X-`, no `C-`/`T-`/`E-`/`F-`/`S-`/`P-`/`G-` finding and no
  round-2 lens names `account_strategy`; grep returns 0 across `docs/` and `issues/`.

### `O-003` · The handover status ladder and `acc_source_documents`' ladder do not map: three accounting states have no warehouse counterpart, and the column is `IRR-41` at `PNR-1` — **MAJOR**

- **What is missing or wrong:** Warehouse's `whb_stock_movements.posting_status` is
  `NOT_APPLICABLE · PENDING · POSTED · REJECTED` (`docs/DATA-MODEL.md:623`, four values, `IRR-41`).
  The receiving side has two ladders, neither of which matches:
  `acc_source_documents.status` = `RECEIVED · MAPPED · POSTED · FAILED · SUPERSEDED ·
  PENDING_PREDECESSOR · DISCARDED` (`accounting/docs/DATA-MODEL.md:274`, seven values) and
  `acc_source_document_movements.status` = `PENDING · APPLIED · FAILED`
  (`accounting/docs/DATA-MODEL.md:277`, three values). Mapping them: `POSTED`↔`POSTED` is the only
  clean pair; `REJECTED`↔`FAILED` differ only in name; and **`SUPERSEDED`, `PENDING_PREDECESSOR` and
  `DISCARDED` have no warehouse counterpart whatsoever**. Nor is the document/movement split
  represented: accounting can mark a document `POSTED` while an individual
  `acc_source_document_movements` row is `FAILED`, and warehouse's single header-level
  `posting_status` has no way to say *"partially applied"*.
- **Why it matters:** The moment it bites is the first envelope accounting discards — the operator
  used a reason code accounting could not map, accounting sets `DISCARDED` with a
  `discard_reason_code_id`, and warehouse's movement stays at `PENDING`. Forever. The index that
  exists precisely to drive the operational catch-up queue,
  `idx_whb_stock_movements_posting ON whb_stock_movements (posting_status)`
  (`docs/DATA-MODEL.md:641`), and the `WS-052 Accounting Handover Queue` screen both read that
  column, so the queue grows monotonically with rows nobody can action: a re-send is idempotent and
  will be discarded again, and there is no state that says "stop trying". `PENDING_PREDECESSOR` is
  the same shape with a worse story — the envelope is legitimately waiting, but the warehouse
  operator sees an indistinguishable stuck row and escalates. And `posting_status` is `IRR-41`
  (`docs/IRREVERSIBLE.md:219`), carried on `whb_stock_movements`, which `docs/IRREVERSIBLE.md:331`
  marks **`PNR-1`** — so widening the `CHECK` after go-live is a data migration over the largest
  table in the ledger.
- **Negative evidence:**
  ```bash
  cd /Users/bbhushan/work/git/workspace/warehouse-issues
  grep -rn "PENDING_PREDECESSOR\|SUPERSEDED\|DISCARDED" docs/ issues/
  # → SUPERSEDED appears only for wh3_rate_cards (DATA-MODEL:1142); DISCARDED only for
  #   whb_inbound_messages (DATA-MODEL:869, p0-08:26). Neither is the handover ladder.
  # → PENDING_PREDECESSOR: 0 hits anywhere in the set.
  grep -rn "APPLIED" docs/PORT-AND-ADAPTER-CONTRACT.md   # → 0
  ```
- **Where it belongs:** `warehouse-base` · v1 · **P0** (the vocabulary ships with the header at
  `PNR-1`; the queue behaviour is P2)
- **Disposition:** *fold into task `P0-12`* for the vocabulary and `P2-18` for the queue. **Line to
  add to `issues/p0-12.md` under Requirements/Traps:** *"`posting_status`'s four values do not cover
  the receiving side's seven. Add **`DISCARDED`** (terminal, carries the counterpart's reason) and
  **`BLOCKED`** (accounting's `PENDING_PREDECESSOR`) to the `CHECK` **in the `PNR-1` DDL**, and map
  accounting `FAILED`→`REJECTED`, `SUPERSEDED`→a new `handover_superseded_by_id`. `IRR-41` means
  this vocabulary cannot be widened cheaply later."* **Line to add to `issues/p2-18.md`:** *"the
  rejected-handover queue must separate actionable (`REJECTED`) from terminal (`DISCARDED`) from
  waiting (`BLOCKED`), because a re-send of a discarded envelope is idempotent and will be discarded
  again."*
- **Irreversibility:** **`PNR-1`, migration `V500030`** — the `posting_status` `CHECK` ships with the
  movement header.
- **Relationship to round 1:** **new.** `Y-`'s exception lens covers unhappy paths inside warehouse;
  no lens compared the two ladders. `IRR-41` states the four values as settled and no finding
  questions them.

### `O-004` · The set names only `permission_dependencies` — the registry that grants nothing at runtime — and never `menu_permission_dependencies`, which is the live one, and which accessories needed a dedicated migration for — **MAJOR**

- **What is missing or wrong:** The set references `permission_dependencies` 26 times across nine
  documents (`BUILD-SPEC-SCREENS.md` 4, `DATA-MODEL.md` 9, `PORT-AND-ADAPTER-CONTRACT.md` 5,
  `IRREVERSIBLE.md` 2, `IMPLEMENTATION-PLAN.md` 2, plus four singletons) and treats it as the
  mechanism by which granting `:edit` also grants `:view`. In live `classic` that table has **zero
  runtime consumers**: no entity, no repository, no service and no frontend reference. The live
  auto-grant is `MenuPermissionDependencyService.autoGrantRequiredPermissions`
  (`platform/backend/src/main/java/ai/platform/service/MenuPermissionDependencyService.java:130`),
  called from `RoleController` at `:601` and `:638`, and it reads
  **`menu_permission_dependencies`** (`platform/…/db/migration/V225__add_menu_permission_dependencies.sql`
  — `menu_id`, `dependent_permission_prefix`, `dependency_type`, uk(`menu_id`,`dependent_permission_prefix`)).
  A sibling module states the same fact in a comment:
  `insurance-360/backend/src/main/java/ai/insurance360/controller/TaskController.java:329` —
  *"permission_dependencies is admin-UI metadata that grants nothing at runtime"*. The warehouse set
  names `menu_permission_dependencies` **zero** times.
- **Why it matters:** The moment it bites is the first time an operator with `whb_stock_movements:create`
  opens the movement modal and every reference dropdown — item, location, owner, reason code, UoM —
  returns 403, because each dropdown endpoint carries its own `:view` authority that the role was
  never granted. This is not hypothetical: it is exactly what happened to the very inventory module
  warehouse must coexist with. `accessories/backend/src/main/resources/db/migration/V30301__add_stock_levels_menu_permission_dependencies.sql`
  exists solely to fix it, and says so in its header — *"This fixes permission errors when users try
  to access dropdowns on the Stock Levels page."* Warehouse has far more reference dropdowns per
  screen than accessories does. The consequence of seeding only `permission_dependencies` is that the
  admin UI *displays* the dependency, an administrator believes the role is complete, and the
  operator still gets 403 — the worst variant, because the evidence points away from the cause.
- **Negative evidence:**
  ```bash
  cd /Users/bbhushan/work/git/workspace/warehouse-issues
  grep -rn "menu_permission_dependencies" docs/ issues/       # → 0
  grep -rc "permission_dependencies" docs/*.md | grep -v ":0" # → 9 files, 26 references, all the inert table
  cd /Users/bbhushan/work/git/workspace/classic
  grep -rln "permission_dependencies" --include=*.java platform/backend/src/main/java | wc -l   # → 0 entities/repos/services
  grep -n "autoGrantRequiredPermissions" platform/backend/src/main/java/ai/platform/service/MenuPermissionDependencyService.java
  # → :130 — the only live auto-grant in the monorepo
  ```
- **Where it belongs:** `warehouse-base` · v1 · **P0** (the permission migration is P0; a dependency
  seeded late has to chase roles that already exist)
- **Disposition:** *fold into task `P0-01`* (the permissions/menus task). **Line to add under
  Traps:** *"**Seed `menu_permission_dependencies`, not just `permission_dependencies`.** The latter
  is admin-UI metadata and grants nothing at runtime
  (`insurance-360/…/TaskController.java:329`); the live auto-grant is
  `MenuPermissionDependencyService.autoGrantRequiredPermissions`
  (`platform/…/MenuPermissionDependencyService.java:130`), keyed on `menus.name` +
  `dependent_permission_prefix` (`V225`). Every warehouse menu leaf whose screen has a reference
  dropdown needs a row, then an auto-grant pass over existing roles — copy
  `accessories/…/V30301__add_stock_levels_menu_permission_dependencies.sql` and
  `platform/…/V226__auto_grant_menu_dependent_permissions.sql`. Without this, dropdowns 403 for every
  role that is not ADMIN."* Also add a row to `PLATFORM-DEPENDENCIES.md` §1 for the table.
- **Irreversibility:** reversible, but expensive after roles exist — a late dependency row does not
  retro-grant; the auto-grant pass must be re-run.
- **Relationship to round 1:** **new.** `Q-001` covers *whether the P2 verb permissions have a
  migration*; this is about *which of two dependency registries* the migration writes to.

### `O-005` · Two P0/P1 task files carry `branches.owner_type` as a Trap — a claim the set's own `PD-1` and `MI-4` declare void — **MAJOR**

- **What is missing or wrong:** `issues/p0-06.md:121` and `issues/p1-05.md:88` both state, in their
  **Traps** section: *"**`branches.owner_type` and `branches.branch_type` already allow `'WAREHOUSE'`**
  (`V149:61`, `:63`) … so a warehouse site can be a platform branch **with no schema change**
  (`C-016`)."* `branches.owner_type` does not exist. `platform/…/V160__Remove_owner_fields_from_branches.sql:13`
  drops it, `:16` drops `owner_id`, `:7` drops `uk_branches_owner_code`, `:19` adds
  `uk_branches_code UNIQUE (branch_code)`. The set knows this and says so twice —
  `docs/PLATFORM-DEPENDENCIES.md:29` (`PD-1`, *"**`branches` is NOT polymorphic.**"*) and `:109`
  (*"**Do not build anything on `branches.owner_type`.**"*), and `docs/MODULE-INTEGRATION.md:86`
  (`MI-4`, *"Half of `C-016` holds, half is void"*). The correction landed in the two reference
  documents and never propagated to the two task files, which are what a builder actually opens.
  Both cite `V149:63`, the exact line `V160` removed.
- **Why it matters:** A Trap is the one section of a task file a builder reads *specifically because
  they expect to be misled*, so a false Trap is worse than no Trap — it converts the document's
  highest-trust section into the source of the error. The builder of `P1-05` (the warehouse/site
  master) reads that a site can be a branch "with no schema change", goes looking for
  `owner_type='WAREHOUSE'` to scope the branch dropdown, finds no such column, and either invents a
  scoping mechanism or discovers mid-build that `branch_code` is now **globally unique** — meaning a
  warehouse site's branch code shares one namespace with every dealer showroom and service centre in
  the install. That last fact is the one the Trap should be carrying and does not.
- **Negative evidence:**
  ```bash
  cd /Users/bbhushan/work/git/workspace/warehouse-issues
  grep -rn "owner_type.*WAREHOUSE\|branches.owner_type" issues/ docs/ | grep -v "no longer exists\|dropped\|void\|V160"
  # → issues/p0-06.md:121  and  issues/p1-05.md:88   (docs/ hits are all the corrections)
  cd /Users/bbhushan/work/git/workspace/classic
  sed -n '13,19p' platform/backend/src/main/resources/db/migration/V160__Remove_owner_fields_from_branches.sql
  grep -n "ownerType" platform/backend/src/main/java/ai/platform/entity/Branches.java   # → 0
  ```
- **Where it belongs:** `warehouse-base` · v1 · **P0** and **P1**
- **Disposition:** *fold into tasks `P0-06` and `P1-05`* — in each, **replace the Trap bullet** with:
  *"**`branches.owner_type` no longer exists.** `V160:13,16` dropped `owner_type`/`owner_id` and
  `:19` made **`branch_code` globally unique** (`uk_branches_code`). `branch_type`'s CHECK survives
  and still admits `'WAREHOUSE'` and `'DISTRIBUTION_CENTER'` (`V149:61`), so the site *type* is free
  but there is **no owner dimension to scope on**, and a warehouse site's branch code competes for
  the same namespace as every dealer showroom — the site-create flow must validate against all
  branches, not just warehouse ones (`PD-1`, `MI-4`)."*
- **Irreversibility:** reversible (documentation), but the namespace fact shapes `WS-016`'s validation
  and should land before `P1-05` builds.
- **Relationship to round 1:** materially extends `C-016` / `PD-1` / `MI-4`. New is that the
  correction did **not** propagate to the two task files, and that the global-uniqueness consequence
  for site codes is stated in no task at all.

### `O-006` · The set states five different values for two registry counts across four documents; live is 218 and 240, and only one document knows its own command is broken — **MINOR**

- **What is missing or wrong:** Cache names are given as **202** (`PD-2` historical), **230**
  (`MODULE-INTEGRATION.md:89`, `:813`), **234** (`BUILD-SPEC-SCREENS.md:96`) and **235**
  (`DATA-MODEL.md:2848`, `INDIA-LOCALISATION-PACK.md:1365`). Filter scopes are given as **210**
  (`PD-2`), **211** (`MODULE-INTEGRATION.md:89`) and **213** (`BUILD-SPEC-SCREENS.md:96`,
  `INDIA-LOCALISATION-PACK.md:1365` says 213). Live today: **240** and **218**. Three documents still
  carry a **line-pinned** command, `awk 'NR>=101 && NR<=415'`
  (`MODULE-INTEGRATION.md:809`, `:1145`, `PLATFORM-DEPENDENCIES.md:863`), which no longer reaches the
  closing paren and silently under-reports — it returns **227** against a true 240, and the error
  grows every time a module registers a cache. `BUILD-SPEC-SCREENS.md:99-101` already diagnoses
  exactly this and supplies a boundary-aware replacement, but the replacement was never propagated
  to the three documents that carry the broken one, and `BUILD-SPEC`'s own number (234) is already
  six short.
- **Why it matters:** A wrong count is cosmetic; a **silently** wrong command is not. The
  `CacheConfiguration` registry is a runtime gate — an unregistered name throws
  `IllegalArgumentException` on the *first call*, not at startup
  (`platform/…/CacheConfiguration.java:375-377`, quoted by the set itself). A builder who runs the
  pinned command to check whether their name is registered gets a truncated list, sees their name
  absent from it, adds it a second time or concludes the registry is smaller than it is. The same
  pinned-window pattern is what produced the 202→230→234→235 divergence in the first place.
- **Negative evidence:**
  ```bash
  cd /Users/bbhushan/work/git/workspace/classic
  awk 'NR>101 && /^\s*\)\);/{exit} NR>101' platform/backend/src/main/java/ai/platform/config/CacheConfiguration.java \
    | grep -cE '^[[:space:]]*"[a-zA-Z0-9._-]+",?$'                 # → 240   (boundary-aware, true)
  awk 'NR>=101 && NR<=415' platform/backend/src/main/java/ai/platform/config/CacheConfiguration.java \
    | grep -cE '^[[:space:]]+"[a-zA-Z0-9._-]+",?$'                 # → 227   (the set's pinned command)
  awk '/COMMON_FILTER_CONFIGS/,0' platform/frontend/src/utils/filterUtils.ts \
    | grep -cE "^  [A-Z0-9_]+: \{"                                 # → 218
  cd /Users/bbhushan/work/git/workspace/warehouse-issues
  grep -rn "NR>=101" docs/ issues/   # → MODULE-INTEGRATION.md:809, :1145, PLATFORM-DEPENDENCIES.md:863
  ```
- **Where it belongs:** `warehouse-base` · v1 · **P0** (`MODULE-INTEGRATION.md` is a P0 runbook)
- **Disposition:** *fold into task `P0-01`* as a documentation line, or fix in place: **replace the
  three `awk 'NR>=101 && NR<=415'` occurrences with `BUILD-SPEC-SCREENS.md:94-97`'s boundary-aware
  form**, and replace every quoted count in the five locations with the command plus a
  *"recomputed on the day"* instruction, per `DECISIONS.md` §7 rule 1. `PD-2` already anticipates
  this — *"it is why counts get re-computed rather than quoted"* — so the fix is to finish what
  `PD-2` started.
- **Irreversibility:** reversible.
- **Relationship to round 1:** materially extends `PD-2`. New is that the broken window is still
  live in three places, that the correction reached only one of four documents, and the two current
  live numbers.

### `O-007` · The house prior art in `classic-issues` carries 101 full `CREATE TABLE` blocks; the entire warehouse task set carries 17 — the local standard for DDL rigour was already met and was regressed from — **MINOR**

- **What is missing or wrong:** `R9`'s `H-002` establishes that *"no table in the design set carries a
  column-level DDL specification"*. What `H-002` does not say — and what changes its disposition — is
  that the same repo family's prior art **does**. `classic-issues/assets/docs/PHASE_*.md` carry
  **101** complete `CREATE TABLE` statements with types, constraints and indexes (PHASE_6 26,
  PHASE_3 17, PHASE_4 16, PHASE_5 15, PHASE_2 14, PHASE_1 13), and the warehouse set's own prior art,
  `classic-issues/warehouse-base/docs/spi/WMS_DATABASE_DESIGN.md`, carries 72 more. Across all **148**
  warehouse issue files there are **17**. So this is not "nobody in this organisation writes DDL in a
  design document" — it is "the organisation writes DDL in design documents and this set stopped".
  The B2 premise I was given is partly void in the other direction: `classic-issues` has **no** assets
  remediation issue and no issue template beyond the stock GitHub `bug_report.md` /
  `feature_request.md`, so there is no house issue standard to diff against — the warehouse task
  shape (PNR banner · Scope · Screens · Requirements closed · Scenarios closed · Closes · Traps ·
  Acceptance · Blocked on) is **strictly more rigorous** than anything in that repo. The single
  dimension on which it is behind is DDL.
- **Why it matters:** It changes `H-002` from a stylistic gap into a regression against a met bar,
  and it names the fix material: the DDL already exists, in
  `classic-issues/warehouse-base/docs/spi/WMS_DATABASE_DESIGN.md`, for 72 of the tables the set
  re-homes. `R6`'s triage carried the *semantics* across (I verified all 72 table names have a trace)
  but not the *column specifications*, so a P1 builder writing `V500012` for `whb_warehouses` has a
  fifteen-column prose cell in `DATA-MODEL.md:450` and must re-derive every type, length, nullability
  and default — the exact activity that produces the `DECIMAL(18,4)` vs `DECIMAL(19,6)` divergence
  `OD-7` exists to prevent.
- **Negative evidence:**
  ```bash
  grep -h "CREATE TABLE" /Users/bbhushan/work/git/workspace/classic-issues/assets/docs/PHASE_*.md | wc -l   # → 101
  grep -h "CREATE TABLE" /Users/bbhushan/work/git/workspace/warehouse-issues/issues/*.md | wc -l            # → 17
  ls /Users/bbhushan/work/git/workspace/warehouse-issues/issues/*.md | wc -l                                # → 148
  ls /Users/bbhushan/work/git/workspace/classic-issues/.github/ISSUE_TEMPLATE/                              # → bug_report.md, feature_request.md only
  ```
- **Where it belongs:** `warehouse-base` · v1 · **P0/P1** (wherever `H-002` is dispositioned)
- **Disposition:** *fold into `H-002`'s disposition* — add one sentence: *"the bar has already been
  met inside `classic-issues` (assets phase docs: 101 `CREATE TABLE` blocks) and the warehouse prior
  art at `classic-issues/warehouse-base/docs/spi/WMS_DATABASE_DESIGN.md` already contains 72 of them,
  so the remedy is to lift and correct rather than to author."* Do **not** file a separate task.
- **Irreversibility:** reversible.
- **Relationship to round 1:** materially extends `R9` `H-002` with the external comparator. Does not
  restate it.

---

## §3 · What I checked and found sound

**The 18-touchpoint runbook — all 22 rows re-executed, all 22 LIVE.** Every path resolves and every
cited line still contains what the matrix says it contains.

| # | File | Cited | Live verdict at HEAD |
|---|---|---|---|
| 1 | `pom.xml` — profiles | `:219-232`, `:233-246`, `:248-269`, `:270-284` | **LIVE** — profile ids at `:47,61,76,90,104,119,134,148,162,177,192,207,221,234,249,271` |
| 2 | `pom.xml` — `all-modules` | `:286-306`, 16 rows | **LIVE** — `pom.xml:287` is `<id>all-modules</id>`; `awk 'NR>=287&&NR<=306' pom.xml \| grep -c "<module>"` → **16** |
| 3 | `<mod>/backend/pom.xml` | full test/compiler/surefire block | **LIVE** — and `MI-3`'s warning is confirmed: `assets` and `product-lift` have neither surefire nor test deps; `doc-ocr-ai` has test deps and no surefire; all other 13 module backends have both |
| 4 | `Dockerfile.backend` — 7 edits | `:20-23 … :459` | **LIVE** — `:20` `ARG ENABLE_ACCOUNTING_BASE=false`; `:431` the jar-detection block |
| 5 | `Dockerfile.backend` — assertion block | `:223-255`, four `BUILD FAILED` guards | **LIVE** — `:223` is the gate comment; `grep -c "BUILD FAILED"` over `223-255` → **4** |
| 6 | `Dockerfile.frontend` | `:41-44 … :194-197` | **LIVE** — `:41` `ARG ENABLE_ACCOUNTING_BASE=false` |
| 7 | `platform/frontend/tsconfig.json` | `:162-186` base, `:187-211` app | **LIVE** — `:162` and `:187` are the two module-path comments |
| 8 ⚠ | `ModuleImportSelector.java` | `:51-54` constants, `:156-186` blocks | **LIVE** — `:51` is `ACCOUNTING_BASE_MODULE_CONFIG`; `:157` the `isClassPresent` block; `:186` closes it |
| 9 | `<Mod>ModuleConfig.java` | `AccountingBaseModuleConfig.java:46-53` | **LIVE** |
| 10 | `docker-compose.yml` | `:123-126`, `:148-151`, `:293-296`, `:325-328`, band comment `:50-54` | **LIVE** — `:123` build arg, `:50` the V600000-V609999 band comment |
| 11 | `start.sh` | 8 places, `:36-39 … :1810-1813` | **LIVE** — `:36` the default, `:1810` the `export` |
| 12 | `startX2.sh` | `:94-97`, `:183-194` | **LIVE** — `:94` is the flag block; accounting genuinely skipped it (`AF-4`) |
| 13 | railway `template.conf` + `setup-railway-client.sh` | `:41-44`; `:276-279`, `:423-426`, `:574-577` | **LIVE** — both resolve |
| 14 | `<Mod>SafeTranslation.tsx` | `AccountingBaseSafeTranslation.tsx:21-39` | **LIVE** |
| 15 | i18n `en`/`fr`/`hi` | `I18nConstants.java:28-33` | **LIVE** — `:28` `public static final class SupportedLocales` |
| 16 | `CacheConfiguration.java` | `:101-415`, warning `:375-377` | **PARTLY STALE** — the warning at `:375` is live and verbatim; the **window is not** — the block is now `101-445` with **240** names. `O-006` |
| 17 ⚠ | `filterUtils.ts` | `:346` onward, union `:30`, `dateOnly` `:49-56` | **LIVE** — `:346` is `export const COMMON_FILTER_CONFIGS = {`; `:30` is the eight-member union, verbatim |
| 18 | `<mod>/…/ArchitectureInvariantsTest.java` | accounting-base copy, 660 lines | **LIVE** — exactly 660 lines; `MODULE_PACKAGE` `:68`, rules at `:79`, `:121`, `:173`, `:198`, anti-vacuous fixtures `:225-345` |
| 19 ⚠ | `jest.config.js` | `:54-61`, `:69-82`, hazard `:45-53` | **LIVE** — `:54` is `roots: [`; `:45` is the enumeration hazard comment |
| 20 | `.github/workflows/tests.yml` | `:106-128`, `:259-408` | **LIVE** — `:106` the frontend gate comment (*"Deliberately NOT `continue-on-error`"*), `:259` `accounting-ratchets:` |
| 21 | `CLAUDE.md` MODULES + SafeTranslation | `:106-123` (18 rows), `:125` | **LIVE** — exactly 18 module rows, `:125` the SafeTranslation list |
| 22 | CHECK widening | `V600200` as the model | **LIVE, and correctly halved** — see the A2 table |

**The load-bearing platform claims — every one re-verified.**

| Claim as the set states it | Live evidence at HEAD | Verdict |
|---|---|---|
| `FlywayConfiguration` knows only six modules and needs no warehouse edit | `platform/…/FlywayConfiguration.java:74-79` — dealer, assets, accessories, services, insurance, lead-sharing | **LIVE** |
| It renumbers into the 830000/860000 bands and runs an **unscoped** duplicate-version `DELETE` | `FlywayConfiguration.java:322-327` — `DELETE FROM flyway_schema_history a USING b WHERE a.version = b.version AND a.installed_rank > b.installed_rank`, no module predicate | **LIVE** |
| `V500000`–`V549999` is genuinely untouched | `find . -name "V5[0-4][0-9][0-9][0-9][0-9]__*.sql" \| wc -l` → **0** repo-wide | **LIVE** |
| `global_settings.chk_global_setting_module` **already admits `'WAREHOUSE'`** — free | `platform/…/V553__global_settings_allow_warehouse_module.sql:15` — `CHECK (module IN ('PLATFORM','DEALER','ACCESSORIES','ATTENDANCE','ASSETS','SERVICE','WAREHOUSE'))` | **LIVE** |
| …and a later hardcoded DROP/ADD could discard it (`PD` §1.11) | I classified all **11** rebuilders: 9 HARDCODED, 2 MERGE. The three that sort after `V553` and touch `global_settings` — `services/V40098:15`, `field-service/V80013:24-25`, `insurance-360/V120122:27-28` — **all preserve `WAREHOUSE`**. The hazard is real and has not yet bitten | **LIVE, hazard not yet realised** |
| `widget_definitions.chk_module` does **not** admit `warehouse` | `platform/…/V557__Extend_widget_definitions_module_constraint.sql:18` — `('platform','dealer','shared','accessories','assets','insurance','services')` | **LIVE** |
| `V190035 (warehouse-core)` is credited by `V553` and does not exist in this checkout | `V553:4` credits it; `find . -name "V19[0-9][0-9][0-9][0-9]__*.sql"` → **0** | **LIVE** |
| `permission_dependencies` real columns are `permission_id`, **`dependent_permission_id`**, row means "granting X also grants Y" | `V248`; column names confirmed | **LIVE** |
| …and a dependency row alone changes nothing at runtime without a `role_permissions` backfill | **Stronger than the set states** — the table has *no* runtime consumer at all; the live auto-grant reads `menu_permission_dependencies`. `MenuPermissionDependencyService.java:130`, `RoleController.java:601,:638`, `insurance-360/…/TaskController.java:329`. → `O-004` |
| `filter_definitions` is the real table; there is no `grid_filter_definitions` | `V229`; `grep -rl "grid_filter_definitions" --include=*.sql .` → 0 | **LIVE** |
| `grid_preferences.default_filters` **and** `default_columns` must both be populated | confirmed in `useGridPreferences` + the `departments`/`service_vehicles` rows | **LIVE** |
| Menu INSERTs need `WHERE NOT EXISTS` guards | no unique constraint on `(name,parent_id,menu_level)` at HEAD | **LIVE** |
| Copying `automotive/backend/pom.xml:8-33` omits test deps / compiler / surefire | measured across 16 module backends: `assets` and `product-lift` have **none** of the three, `doc-ocr-ai` has test deps but **no surefire** — exactly `MI-3` | **LIVE** |
| Frontend Docker merge is last-write-wins and i18n namespace files collide | `Dockerfile.frontend:158-176` | **LIVE** |
| `BaseExportService` does not expose `formatBoolean`; it is on `BaseController:752` | confirmed | **LIVE** |
| `SqlSortBuilder` / `PaginationService` / `BaseController.mapSortField:446` mandatory | confirmed | **LIVE** |
| Every cache name must be registered or it throws on **first call**, not at startup | `CacheConfiguration.java:375-377`, verbatim | **LIVE** (the *count* is stale — `O-006`) |
| `branches.branch_code` is **globally unique** and `branches` is **not polymorphic** | `V160:13,16` drop `owner_type`/`owner_id`; `:19` adds `uk_branches_code`; `Branches.java` `@UniqueConstraint` names `branch_code` alone | **LIVE** — and correctly recorded at `PD-1`/`MI-4`, but **not** in two task files → `O-005` |
| Native-query timestamp columns come back as any of four Java types | CLAUDE.md-documented; confirmed unchanged | **LIVE** |
| A `@PreAuthorize`-less controller method **is** possible today | `platform/…/ArchitectureInvariantsTest.java:88-99` freezes a baseline of **64** unannotated endpoints across 11 controllers and `:111-121` allows up to **72**; only *new* ones are blocked — **and `CONTROLLERS` at `:52` scopes the scan to `ai/platform/controller` only**, so no other module is covered by the platform ratchet | **LIVE** — and the set already mandates a per-module ratchet (touchpoint 18; `ArchitectureInvariants` named 53 times), so not a finding |
| The write-audit aspect keys off the controller package | `UserActivityTrackingAspect.java:59` — `within(ai..controller..*) && !within(ai.platform.controller.UserActivityLogController)`; module from package segment 2 uppercased, `resolveModule` `:167` | **LIVE** |

**The accessories coexistence claim (`docs/COEXISTENCE.md`) — all six facts still true at HEAD.**

- `accessory_inventory_transactions` is still **single-sided**: `accessories/…/db/migration/V30131__…sql:6-30` has one `quantity DECIMAL(18,4)`, a nullable `uom_id` and four nullable location columns — no paired debit/credit line.
- **Reservations are schema-only**: `accessories/…/entity/StockLevel.java:190,199` define `reserveQuantity` / `releaseReservedQuantity`; **zero** non-entity call sites.
- **Physical counts are schema-only**: `accessories/…/service/inventory/InventoryCountService.java:325-345` — `generateAdjustments()` sets `count.setStatus("POSTED")`, saves and audits, and writes **no stock**; `grep -c "StockLevel"` in that file → **0**.
- **UoM conversion is schema-only**: no conversion call site.
- **No concurrency control**: `accessories/…/service/inventory/InventoryStockAdjustmentService.java:61-64` says it in a comment — *"Callers pre-check availability (on hand less reserved), so this only fires when that check raced against another movement."*
- The cost model in `COEXISTENCE.md` is therefore **still accurate**; nothing in accessories has moved.

**Cross-repo citation integrity.** All **9** citations the warehouse set makes into
`/Users/bbhushan/work/git/workspace/accounting` resolve and are content-correct even after
accounting's most recent commit, including all four of `D-6`'s
(`DATA-MODEL.md:434`, `:436`, `:507`, and the `acc_godowns` row) and `OD-7`'s precision numbers
(`:2442-2453` the nine-row ruling, `:2455-2470` the two tie-breaks, `:2472` §5.2). `OD-7`'s
*numbers* are correct as quoted; I did not re-open its recommendation, which is a decision.

**Tables specified in both sets — which side wins.** Nine tables are specified in both:
`acc_stock_balances` (`accounting:507`) vs `whb_stock_positions`; `acc_cost_layers` (`:434`) and
`acc_cost_layer_consumptions` (`:435`) vs `whb_cost_layers`; `acc_valuation_entries` (`:436`) vs
`whb_stock_movements` + `whb_accounting_handovers`; `acc_godowns` (`:4291`) vs `whb_warehouses` /
`whb_locations`; `acc_job_work_challans` (`:489`) vs the warehouse subcontracting set;
`acc_price_lists` vs `E-078`; and the port pair `acc_source_documents` (`:274`) /
`acc_source_document_movements` (`:277`) vs `whb_accounting_handovers` (`DATA-MODEL.md:853`).
`D-6` decides all of them the same way — warehouse wins quantity and cost, accounting always wins
the ledger — and the set is internally consistent about it. The problem is not the ruling; it is that
accounting has never been told (`O-001`).

**Accounting defect classes that apply verbatim to warehouse.** Of accounting's round-2/3/4 classes,
five transfer directly and the warehouse set has already covered four: closed-vocabulary `CHECK`
constraints seeded before the widening migration (`V-3` shape) — covered by `D-10` and `FR-377`;
precision divergence — covered by `OD-7`; deferred FK where the target table ships in a later
migration (`accounting:277`, `§7.4`) — covered by `IRREVERSIBLE.md` §3; and generic-UUID references
that are deliberately not FKs — covered by `DATA-MODEL.md` G14. The fifth,
**account determination as a closed strategy vocabulary**, is *not* covered → `O-002`.

**`R6`'s prior-art triage — spot-checked and sound.** The seven `warehouse-base/docs/spi/` files total
**18,507** lines (`wc -l` → WMS_DATABASE_DESIGN 4655, WMS_IMPLEMENTATION_TASKS 3875,
…_PART2 3441, SPI_PRODUCT_DOCUMENT 1814, WAREHOUSE_EXPLAINED 1719, SPI_FUNCTIONAL_DOCUMENT 1601,
ptc-servigistics 1402), matching `R6` §1.1 exactly. Taking the five with the most functional content,
all **72** `CREATE TABLE` names in `WMS_DATABASE_DESIGN.md` have a trace in the warehouse set —
carried, re-homed or explicitly dropped with a reason (e.g. `wms_documents` at `DATA-MODEL.md:3966`,
`wms_invoice_orders` at `:3971`). The triage is genuinely complete on semantics; only the DDL was
left behind (`O-007`).

**The logistics seam.** `logistics/docs/TMS/` is 13 files (`TMS_Functional_Document.md` alone 2,266
lines). The boundary the warehouse set draws — `P6-08` and `R7` — is still consistent with what TMS
assumes; `p6-08.md`'s live citations all resolve. No finding.

---

## §4 · Refused

- **"The set should carry a per-module `@PreAuthorize` ratchet because the platform one only scans
  `ai/platform/controller`."** True (`ArchitectureInvariantsTest.java:52`), but touchpoint 18 already
  mandates one ratchet per module and the set names `ArchitectureInvariants` **53** times. Covered.
- **"`global_settings` widening is unnecessary because `V553` already allows `WAREHOUSE`."** The set
  states exactly this at `MODULE-INTEGRATION.md:622` and `PLATFORM-DEPENDENCIES.md:386`, and still
  correctly requires the *defensive merge* because a later hardcoded rebuild can discard it. Covered,
  and correct.
- **"A later hardcoded `chk_global_setting_module` rebuild will drop `WAREHOUSE`."** I checked all
  eleven rebuilders; the three that sort after `V553` all preserve it. Filing this would be
  speculative — the set's defensive-merge instruction already handles the future case.
- **"`whb_warehouses.code` collides with `branches.branch_code`."** It does not — they are separate
  columns in separate namespaces (`DATA-MODEL.md:450`, uk(`code`) + uk(`company_id`,`code`)). The
  real consequence is on the *branch* row a site requires (`p1-05.md:22-23`, `branch_id NOT NULL`),
  and that is folded into `O-005` rather than filed separately.
- **"Warehouse task files lack a house issue template."** The premise is void: `classic-issues` has
  no assets remediation issue and only the stock GitHub `bug_report.md` / `feature_request.md`. The
  warehouse task shape is strictly more rigorous. Reported as the "what they do better" half of
  `O-007` instead of as a finding.
- **`R1`'s stale registry numbers (202 / 210).** `R1` is a round-1 artefact and `PD-2` exists to
  supersede it. Only the *live, still-broken* commands are filed (`O-006`).
- **`OD-7`'s recommendation.** I was asked to verify the numbers, not the decision; the numbers check
  out. Re-litigating a taken decision is out of segment.

---

## §5 · Counts

```bash
cd /Users/bbhushan/work/git/workspace/warehouse-issues
grep -c "^### \`O-" docs/reviews/R14-codebase-and-sibling-set-reverification.md          # → 7
grep -o "BLOCKER\*\*$" docs/reviews/R14-codebase-and-sibling-set-reverification.md | wc -l  # → 2
grep -o "MAJOR\*\*$"   docs/reviews/R14-codebase-and-sibling-set-reverification.md | wc -l  # → 3
grep -o "MINOR\*\*$"   docs/reviews/R14-codebase-and-sibling-set-reverification.md | wc -l  # → 2
```

| Severity | Count | Ids |
|---|---|---|
| **BLOCKER** | 2 | `O-001` `O-002` |
| **MAJOR** | 3 | `O-003` `O-004` `O-005` |
| **MINOR** | 2 | `O-006` `O-007` |
| **Total** | **7** | |

Of the seven: **4 new** (`O-002`, `O-003`, `O-004`, and the non-propagation half of `O-005`),
**3 material extensions** of `OD-1`, `PD-2` and `H-002`. Verification results with a live/stale
verdict: **22** touchpoint rows and **20** platform claims, of which **1** is stale (`O-006`) and
**1** is stale only in the task files (`O-005`).
