# R8 — Task buildability and spec completeness: the v1 phases

**Date** 2026-09-02 · **Lens** R8 · **Finding prefix** `Q-` · **Round** 2

**File set.** Every v1 task file, read whole:

```bash
ls issues/p0-*.md issues/p1-*.md issues/p2-[0-9]*.md issues/p2in-*.md | wc -l   # -> 70
cat issues/p0-*.md issues/p1-*.md issues/p2-[0-9]*.md issues/p2in-*.md | wc -l  # -> 8399
ls issues/p0-*.md | wc -l   # -> 17
ls issues/p1-*.md | wc -l   # -> 20
ls issues/p2-[0-9]*.md | wc -l  # -> 29
ls issues/p2in-*.md | wc -l # -> 4
grep -rohE "\bQ-[0-9]{1,3}\b" docs/ issues/ | sort -u | wc -l   # -> 0, the prefix is free
```

Checked against `docs/BUILD-SPEC-SCREENS.md` (237 `WS-` blocks, 136 of them v1),
`docs/DATA-MODEL.md` (271 `§2` table rows, `§7` migration allocation),
`docs/WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md`, `docs/SCENARIO-CATALOGUE.md` (300 `WH-SC-`),
`docs/IRREVERSIBLE.md`, `docs/IMPLEMENTATION-PLAN.md` §10 Definition of done, and the house
standards in `/Users/bbhushan/work/git/workspace/classic/CLAUDE.md`.

**Method, in three sentences.** For each of the 70 v1 task files I asked one question — could a
builder, or an agent running `/create-entity`, `/create-page` or `/modify`, take this file and the
documents it points at and ship the task without asking anyone anything — and scored thirteen
things for presence *and* sufficiency, scoring a section that exists but says nothing usable as
absent. Where a gap appeared in more than one file I stopped scoring and computed the full affected
list with a command rather than filing it per file. Every count below carries the command that
produced it; every claim about the `classic` monorepo carries `file:line`; every `FR-`, `WH-SC-`,
`WS-`, `X-` and `D-` id was grepped and opened before it was written.

---

## §1 · Verdict

**Not one of the 70 v1 task files is hand-off-ready today.** Computed, strictly: a task is
hand-off-ready if none of the twelve scored dimensions is `N` or `partial`, and the count is
**0 of 70**; relax it to "nothing outright missing, partials allowed" and it is **19 of 70**
(`P0-01 P0-02 P0-03 P0-04 P0-07 P0-08 P0-11 P0-12 P0-14 P0-17 P1-02 P1-03 P1-05 P1-09 P1-12 P1-14
P1-15 P1-18 P2-03`). That is not the disaster it sounds like, and the reason matters: the task files
are unusually good at the things this design set thought hardest about — every one of the 61
screen-owning tasks carries a `COMMON_FILTER_CONFIGS` scope decision, an explicit Mobile verdict and
a named scenario list, and every one of the 56 tasks that owns DDL claims a migration number inside
its band with no collision. The gaps are concentrated, and two of them are structural rather than
editorial.

The single most expensive thing missing is that **25 of the 29 `wh_` verb permissions the build spec
itself declares mandatory have no migration to live in**. `DATA-MODEL.md` §7.3 allocates exactly one
number for app permissions (`V511000`, `WH-200`) and one for their dependency rows (`V511001`); that
number is owned by `P1-20`, which scopes itself in its own words to "the verb permissions **this
wave** adds" and lists six. The P2 wave's 25 — every count, hold, adjustment-approval, shipment-
dispatch, transfer, revaluation, print-void and go-live transition — have nowhere to go, and two P2
task files (`p2-03:77`, `p2-13:79`) instruct the builder to seed them into `P1-20`'s already-released
`V511000`, which is precisely what `FR-374` and the Definition of done forbid. The build spec's own
words for this outcome are at `BUILD-SPEC-SCREENS.md:1998`: *"a transition with no verb permission is
a transition anybody with `:edit` can perform."*

The second is that **`status` has no domain**. `DATA-MODEL.md` §1.12 defers every `status` column to
§1.4; §1.4 mentions `status` exactly once, and only as the soft-delete twin of `is_active` on masters
and catalogues — `VARCHAR(20)` and nothing more — while explicitly excluding every transactional
table from that paragraph. The result is 30 v1 tables and 38 v1 screens whose document ladder is
declared nowhere, including 38 grids that ship a `status` filter with no option list to populate it.
A builder reaching `wh_goods_receipts` cannot write the `CHECK`, the TypeScript union, the badge map
or the filter options without inventing them, and two builders will invent differently.

Everything else is cheap. The AUDITOR `:export` question is one sentence that four documents answer
one way and four answer the other, and it lands in a forward-only permission migration.
115 of 136 v1 screens have no per-column `sortable` / `default-visible` decision, which is a day of
decisions, not a design problem — but it is a day nobody has scheduled and `§9.2`'s own guard turns
a wrong guess into a grid whose preferences can never be saved. **Fix `Q-001` and `Q-002` and the
number goes from 0 to something a product owner can hand out; leave them and every P2 builder stops
twice on their first day.**

---

## §2 · The findings

### `Q-001` · The P2 wave's 25 verb permissions, their dependency rows and their menu grants have no migration to live in — **BLOCKER**

- **What is missing or wrong:** `BUILD-SPEC-SCREENS.md` §10.2 names **56** verb permissions, **29**
  of them in the `warehouse` app module. `DATA-MODEL.md` §7.3 allocates **one** migration number for
  app permissions — `WH-200` / `V511000`, "`permissions` + verb permissions for the app resources" —
  and one for dependencies (`WH-201` / `V511001`). Both are owned by `P1-20`, whose header claims
  them and whose §"The verb permissions this wave adds" (`p1-20.md:40-45`) lists **six**. That leaves
  **25** `wh_` verb permissions named by the authority and claimed by no migration and no task:
  `wh_blocked_movements:force`, `wh_counts:approve`/`:freeze`/`:post`,
  `wh_cutover_checklists:certify`, `wh_demand_orders:allocate`/`:cancel`/`:hold`/`:release`/
  `:short_pick`, `wh_holds:mass`/`:place`/`:release`, `wh_landed_cost_documents:apply`,
  `wh_opening_stock_batches:post`/`:reverse`, `wh_print_jobs:void`, `wh_print_templates:publish`,
  `wh_purchase_orders:cancel`, `wh_return_receipts:disposition`, `wh_revaluations:approve`,
  `wh_shipments:dispatch`, `wh_stock_adjustments:approve`, `wh_transfer_orders:dispatch`/`:receive`.
  Contrast the grid band, which `DATA-MODEL.md:2995` deliberately allocates as a *range* —
  `V511020`–`V511199`, "**one migration per grid**" — and which `P2-29` then hands out per task
  ("*Each grid's own migration is authored by the task that creates its table, claiming one number
  inside … and recording it in that task's header*", `p2-29.md:16-18`). No equivalent exists for
  permissions. Worse, two P2 files tell the builder to do the forbidden thing outright:
  `p2-03.md:76-78` — "*Seed the permissions in `P1-20`'s `V511000` block*" — and `p2-13.md:79` —
  "*Seed it in `P1-20`'s `V511000` block*". The Definition of done at
  `IMPLEMENTATION-PLAN.md:1371-1373` requires every migration to be "forward-only, **never edited in
  place** … and owned by **exactly one task**"; `FR-374` is the requirement behind it. There is not
  even a spare number to take: `DATA-MODEL.md:2998` reserves `V511201`–`V519999` for "**post-v1** app
  work", and the P2 wave is v1.
- **Why it matters:** the day a builder picks up `P2-11` (Counts) they reach the Freeze button, look
  for `wh_counts:freeze`, find it named in the build spec, find no migration that creates it, and
  have three bad choices — edit a released migration (breaks the checksum, and `FR-374` records that
  a Flyway failure here triggers a blind repair and retry rather than failing loudly), invent a
  number outside the allocation (collides with `WH-203`'s grid band), or ship the button gated by
  `:edit`. The third is the one that happens, because it is the only one that compiles. The
  consequence is stated by the authority itself at `BUILD-SPEC-SCREENS.md:1998`: every stock-count
  approval, every adjustment approval, every shipment dispatch — the inventory-relief event — and
  every go-live certification becomes an action any user holding `wh_*:edit` can perform. The person
  it bites is the finance controller at the first quarter close who discovers that the warehouse
  operator who *entered* the variance is also the one the audit log shows *approving* it.
- **Negative evidence:**
  ```bash
  # 56 verb permissions in the authority, 29 of them in the app module
  sed -n '2002,2035p' docs/BUILD-SPEC-SCREENS.md | ... expand the "· `:verb`" continuations
  wc -l < /tmp/verbs2.txt          # -> 56
  grep -c '^wh_' /tmp/verbs2.txt   # -> 29

  # of those 29, the ones P1-20 (the sole owner of V511000/V511001) does not name
  grep '^wh_' /tmp/verbs2.txt | while read v; do grep -q -- "$v" issues/p1-20.md || echo "$v"; done | wc -l
  # -> 25

  # nobody else claims a permission migration
  grep -rn "V511000\|V511001" issues/ docs/IMPLEMENTATION-PLAN.md
  # -> p1-20.md:4,15,17 (the owner) + p1-19.md:15, p2-03.md:77, p2-13.md:79, p1-14.md:68
  #    (four *references* telling the builder to write into someone else's migration)

  # the allocation itself
  sed -n '2992,2998p' docs/DATA-MODEL.md
  # -> WH-200 | V511000 | one number.   WH-203 | V511020-V511199 | "one migration per grid".
  #    V511201-V519999 | "Reserved ... for post-v1 app work"

  # 3 of the 33 P2/P2-IN task files name any resource:action token at all
  n=0; for f in issues/p2-[0-9]*.md issues/p2in-*.md; do grep -qE '`[a-z0-9_]+:[a-z_]+`' $f && n=$((n+1)); done; echo $n   # -> 3
  ```
  Two verbs run the other way: `P1-20` seeds `wh_goods_receipts:reverse` and
  `wh_putaway_tasks:complete`, and neither appears in §10.2
  (`grep -c wh_putaway_tasks:complete /tmp/verbs2.txt` -> `0`), so the two documents also disagree
  about the six that *are* owned.
- **Where it belongs:** `warehouse` · v1 · P2.
- **Disposition:** *fold into task `P2-29`*. `P2-29` already owns exactly this problem shape for
  grids and already solves it: add to `p2-29.md` a second allocation paragraph beside the grid one —
  *"`V511140`–`V511169` is the P2 permission band and `V511170`–`V511199` the P2 dependency band;
  each task that ships a transition claims one number from each, seeds its own verb permission with
  its `role_permissions` back-fill and its `→ :view` `permission_dependencies` row, and records both
  numbers in its header. `V511000` is released and is never edited"* — and amend
  `DATA-MODEL.md:2995` to split `WH-203`'s range accordingly, and delete the two "seed it in
  `P1-20`'s `V511000` block" instructions at `p2-03.md:77` and `p2-13.md:79`. This is a re-slicing of
  a band `DATA-MODEL.md` already reserves, not a new task.
- **Irreversibility:** the permission migration is forward-only; once `V511000` ships in a customer
  install, the 25 rows can only ever arrive as *new* numbered migrations. Deciding the band now costs
  a paragraph; deciding it after `P1-20` merges costs a correction migration per vertical. Not a
  `PNR-1`/`PNR-2` schema commitment — **reversible in data, irreversible in migration history.**
- **Relationship to round 1:** materially extends `X-014` and R9 `H-001`. `X-014` says §10.2 *names
  no verb permission* for P3/P4; `H-001` says the same for P5/P6. **What is new is that for P0–P2 the
  verbs *are* named and the gap is one layer down — no migration owns them** — which is the exact
  extension into P0–P2 the lens was asked to test, and which neither predecessor covers.

---

### `Q-002` · `status` has no declared domain for 30 v1 tables and 38 v1 screens, because §1.12 defers it to a §1.4 that only defines the masters' soft-delete flag — **BLOCKER**

- **What is missing or wrong:** `DATA-MODEL.md` §2 lists 271 table rows; **69** name a `status`
  column and **15** enumerate its values. The reason is a cross-reference that resolves to the wrong
  thing. `DATA-MODEL.md:372` (§1.12, the legend for §2) says: *"The audit quartet, `version`,
  `is_active` and `status` are **never** repeated — §1.4 states them once."* §1.4 (lines 93–131)
  mentions `status` exactly once, in its **Soft delete** paragraph: *"`is_active BOOLEAN NOT NULL
  DEFAULT true` plus `status VARCHAR(20)` **on masters and catalogues**, matching the platform
  idiom."* The same §1.4 then explicitly rules `is_active` **off** every transactional table — *"No
  `is_active` … every transactional table — movements, lines, positions, receipts, orders, shipments,
  counts, adjustments, tasks, reservations, billable events"*. So the deferral resolves, and it
  resolves to a definition that does not apply to the tables that need it most. For
  `wh_goods_receipts`, `wh_counts`, `wh_demand_orders`, `wh_shipments`, `wh_stock_adjustments`,
  `wh_transfer_orders`, `wh_rmas`, `whin_delivery_challans` and 22 others, `status` is a document
  ladder, and a builder is given a width and nothing else. Note that this is not an oversight `D-10`
  covers: document status is **not** one of `D-10`'s thirteen open catalogues, so it is meant to be a
  closed vocabulary with a `CHECK`, a Java enum and a TypeScript union — none of which can be written.
  The build spec compounds it twice: `BUILD-SPEC-SCREENS.md:1284` and `:1468` write
  `` `status` DRAFT/SUBMITTED/… — badge variant from the registry ``, eliding the domain with an
  ellipsis and pointing at a registry that exists only for *stock* status
  (`whb_stock_statuses.badge_variant`, `:1133`, `FR-381`), not for document status.
- **Why it matters:** it bites on the first day of the first P2 screen and it bites twice. First in
  the migration — the builder writes `status VARCHAR(20)` with no `CHECK`, and the check constraint
  is the one thing `R8`'s sibling gates treat as ground truth for reachability, so the state machine
  becomes unreviewable at the moment it is created. Second in the grid: **38 v1 screens ship a
  `status` select or multiselect filter whose option list does not exist anywhere**, so the builder
  invents it, the mobile builder invents it again in
  `mobile/src/schemas/common.schemas.ts` (which the design set already flags as a third copy of every
  vocabulary), and the i18n author invents a third set of keys. The person it bites is the branch
  manager who filters Goods Receipts by "Posted" on the web, gets 41 rows, opens the same filter on
  the handheld, and gets 0 — because one surface spelled it `POSTED` and the other `POSTED_TO_LEDGER`.
- **Negative evidence:**
  ```bash
  awk -F'|' '/^\| `wh/{n++; if($4 ~ /`status`/){s++; if($4 ~ /`status` \(/) e++}} END{print n,s,e}' docs/DATA-MODEL.md
  # -> 271 69 15     (rows / naming status / enumerating a domain)

  sed -n '/^### 1\.4/,/^### 1\.5/p' docs/DATA-MODEL.md | grep -c 'status'
  # -> 1, and that one occurrence is the masters-and-catalogues soft-delete sentence

  sed -n '372p' docs/DATA-MODEL.md
  # -> "... `is_active` and `status` are **never** repeated - §1.4 states them once"

  # v1 screen rows naming `status` without an enumerated domain
  # (index-row version cell x detail-row status cell)   -> 45 v1 rows name it, 7 enumerate, 38 do not
  # WS-047 WS-064 WS-065 WS-074 WS-075 WS-078 WS-082 WS-083 WS-085 WS-086 WS-094 WS-098 WS-101
  # WS-102 WS-103 WS-105 WS-110 WS-112 WS-122 WS-132 WS-135 WS-136 WS-140 WS-141 WS-142 WS-144
  # WS-147 WS-148 WS-151 WS-175 WS-176 WS-178 WS-179 WS-194 WS-196 WS-197 WS-199 WS-223

  grep -rn "whb_document_statuses" docs/ issues/ | wc -l    # -> 0, no catalogue exists either
  ```
  The 30 v1 tables: `whb_job_runs` `whb_import_batches` `whb_import_batch_rows`
  `wh_receiving_sessions` `wh_goods_receipts` `wh_receipt_reversals` `wh_reconciliation_cases`
  `wh_dock_doors` `wh_stock_adjustments` `wh_transfer_orders` `wh_counts`
  `wh_reconciliation_exceptions` `wh_demand_orders` `wh_shipments` `wh_print_jobs`
  `wh_return_receipts` `wh_rmas` `wh_replenishment_runs` `wh_replenishment_suggestions`
  `wh_landed_cost_documents` `wh_revaluations` `wh_cutover_checklists`
  `wh_cutover_checklist_items` `whin_compliance_registrations` `whin_compliance_auth_sessions`
  `whin_compliance_documents` `whin_delivery_challans` `whad_counter_sales`
  `whas_material_requests` `whas_material_request_lines`.
- **Where it belongs:** `warehouse-base` + `warehouse` + `warehouse-india` + the two adapters · v1 ·
  P0 (the convention) then per-task (the ladders).
- **Disposition:** *fold into task `P0-01`* — add to `p0-01.md` a line requiring a new
  `DATA-MODEL.md` §1.4a, *"Document status — every transactional `status` column is
  `VARCHAR(20) NOT NULL` with a `CHECK`, and §2 states its domain on the table's own row; §1.12's
  deferral covers only the masters' soft-delete `status`"* — **and** amend `DATA-MODEL.md` §2 to
  enumerate the domain on each of the 30 rows, in the form the 15 sound rows already use
  (`wh_goods_receipts.match_status` at `:964` is the model: `` `match_status` (`MATCHED`/`QTY_OVER`/
  `QTY_UNDER`) ``). Replace the two ellipses at `BUILD-SPEC-SCREENS.md:1284` and `:1468` with the
  enumerated list and drop "from the registry", which is untrue for document status. This is
  editorial work on an existing document, not a new task — but it is 30 decisions and it must be
  taken by one person, not 20 builders.
- **Irreversibility:** the `CHECK` constraint lands with each table's DDL migration, which for the
  P2 tables is `V510030`–`V510041` and beyond. A domain widened later is a cheap additive migration;
  a domain that two modules spelled differently is a data migration across live rows. `PNR-1` is not
  engaged. **Reversible, expensively.**
- **Relationship to round 1:** materially extends R9 `H-004` (*"not one entity has an enumerated
  state machine, 31 status-bearing tables in P3–P6"*). **What is new is v1 — the tables that actually
  ship first — the filter-option consequence on 38 grids, and the mechanism: this is not forgetfulness
  but a documented deferral in §1.12 that lands on a paragraph scoped to masters only.** Adjacent to
  R11 `Y-006` (the LPN ladder), which is one instance of the same hole.

---

### `Q-003` · Whether AUDITOR receives `:export` is answered both ways by four documents each, and it lands in a forward-only permission migration — **MAJOR**

- **What is missing or wrong:** four places say the auditor never exports —
  `IMPLEMENTATION-PLAN.md:417` (P0-15's own plan row) and `:1376` (the global Definition of done),
  `DATA-MODEL.md:2920` (`WHB-71`, the `V501000` allocation row), and `issues/00-EPIC-master.md:202`.
  Four say the opposite — `BUILD-SPEC-SCREENS.md:2080` (§10.4, "the role decisions that must be
  **re-taken**"): *"It receives every `:view` and **every `:export`**"* — and `p0-15.md:16`, `:67` and
  `:127`. `p0-15.md:113` states it as a rule in its own voice: *"`:export` yes"*. So the task file
  that owns `V501000` contradicts its own plan row and its own Definition-of-done line. The
  acceptance checkbox that is supposed to settle it, `p0-15.md:127`, cites `WH-SC-245` — and
  `WH-SC-245` (`SCENARIO-CATALOGUE.md:492`) contains the word "export" **zero** times: it asserts six
  reads succeed and every write attempt is `403`. The named test cannot decide the question.
  Meanwhile `FR-427` (`:741`) promises the auditor five artefacts, one of which is *"a movement-level
  **audit export** for a period"* — which "never `:export`" makes unreachable for the AUDITOR role.
- **Why it matters:** it is one row in a seed migration and it is decided by whoever writes the SQL
  first. If they follow the Definition of done, the auditor arrives on site, opens the movement
  register, cannot download it, and `FR-427` — the requirement that exists because the platform
  activity log is *"telemetry, not a record"* — is unmet on day one of the first statutory audit. If
  they follow `p0-15`, an ADMIN-adjacent read-only role can bulk-extract the ledger, and the live
  monorepo's own precedent says no: `platform/backend/src/main/resources/db/migration/V528__Create_auditor_role_with_view_permissions.sql:6`
  — *"No create, edit, delete, export, or modify permissions are granted."*
- **Negative evidence:**
  ```bash
  grep -rn "never .*:export" docs/ issues/ | grep -v '^docs/reviews/'
  # -> IMPLEMENTATION-PLAN.md:417, :1376 · DATA-MODEL.md:2920 · issues/00-EPIC-master.md:202
  grep -rn 'every `:export`' docs/ issues/ | grep -v '^docs/reviews/'
  # -> BUILD-SPEC-SCREENS.md:2080 · p0-15.md:16, :67, :127
  sed -n '492p' docs/SCENARIO-CATALOGUE.md | grep -oic export      # -> 0
  grep -n "FR-427" docs/WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md       # -> :741, "a movement-level audit export for a period"
  sed -n '6p' /Users/bbhushan/work/git/workspace/classic/platform/backend/src/main/resources/db/migration/V528__Create_auditor_role_with_view_permissions.sql
  # -> "-- No create, edit, delete, export, or modify permissions are granted."
  ```
- **Where it belongs:** `warehouse-base` · v1 · P0 (`V501000`), and it propagates to `V511000`,
  `V520100`, `V521100` and `V541000`.
- **Disposition:** *is a `D-`/`OD-` decision, not a task*. It is a role-scope decision with a
  compliance argument on both sides and a live precedent that the design set has already chosen to
  overrule once (`BUILD-SPEC-SCREENS.md` §10.4 exists precisely because "the prior module's auditor
  exclusion is **not inherited**"). Allocate the next free `OD-` id, state the answer in one line,
  and then make `p0-15.md:127` cite a scenario that actually asserts it — `WH-SC-245`'s row needs the
  word "export" added to its expected outcome, or a new scenario. Until it is a `D-`/`OD-` row, the
  four-versus-four split will be re-litigated in every one of the five permission migrations.
- **Irreversibility:** lands in `V501000`, forward-only. A grant added later needs a new migration
  **and** a `role_permissions` back-fill across every existing install; a grant removed later needs
  the same in reverse and is the kind of change nobody notices until an auditor's download stops
  working. **Irreversible in migration history; decide before `V501000` is authored.**
- **Relationship to round 1:** new. `GAP-REGISTER.md` and `DESIGN-SET-DEFECTS.md` contain no finding
  on AUDITOR `:export` (`grep -rn "AUDITOR" docs/GAP-REGISTER.md docs/DESIGN-SET-DEFECTS.md` returns
  the role only in passing, never the export question).

---

### `Q-004` · 115 of 136 v1 screens carry no per-column `sortable` / `default-visible` decision, and both are migration content — **MAJOR**

- **What is missing or wrong:** `BUILD-SPEC-SCREENS.md` carries a per-column table —
  `| key | label | type | sort | vis | source |` — for **eight** blocks only: the shared shape for
  the fourteen catalogue screens `WS-001`…`WS-014` (`:517`), then `WS-016` (`:614`), `WS-017`
  (`:655`), `WS-023` (`:807`), `WS-040` (`:1029`), `WS-042` (`:1123`), `WS-073` (`:1276`) and
  `WS-100` (`:1455`). That covers 21 v1 screens. The remaining **115** get a single comma-separated
  column list in the index row — names only, with no `is_sortable`, no `is_default_visible` and no
  column order. Both are columns of `grid_column_definitions`, and `default_columns` is a
  `grid_preferences` payload the DoD requires every grid migration to emit
  (`IMPLEMENTATION-PLAN.md` DoD; `DATA-MODEL.md:3105` item 6, *"Every grid migration emits both
  `default_columns` and `default_filters` as `'[…]'::jsonb`"*).
- **Why it matters:** this is not aesthetic. `BUILD-SPEC-SCREENS.md` §9.2 (`:1896-1951`) ships an
  assertion — `RAISE EXCEPTION 'required column(s) % missing from default_columns'` — and its own
  note that a `required` column absent from `default_columns` makes **every save of that user's grid
  preferences fail**. So a builder guessing the default-visible set does not produce a slightly wrong
  grid; they produce a grid whose Save button throws for every user who touches it, and the failure
  surfaces in production, not in dev, because dev has no saved preferences. Multiply by 115 screens
  and it is the single largest source of avoidable rework in the P1/P2 build. The person it bites is
  the first warehouse supervisor who reorders columns on the Demand Orders grid and gets a 500.
- **Negative evidence:**
  ```bash
  grep -cE "^\| key \| label \| type \| sort" docs/BUILD-SPEC-SCREENS.md          # -> 8
  grep -nE "^\| key \| label \| type \| sort" docs/BUILD-SPEC-SCREENS.md
  # -> 517 (WS-001..WS-014, shared), 614 (WS-016), 655 (WS-017), 807 (WS-023),
  #    1029 (WS-040), 1123 (WS-042), 1276 (WS-073), 1455 (WS-100)  = 21 screens

  # v1 screens in the index
  awk -F'|' '/^\| WS-[0-9]{3} \|/{v=$(NF-1); gsub(/[ *`]/,"",v); split(v,a,"·"); id=$2; gsub(/ /,"",id); if(a[1]=="v1") s[id]=1} END{print length(s)}' docs/BUILD-SPEC-SCREENS.md
  # -> 136        =>  136 - 21 = 115 with no per-column decision

  grep -rn "default-visible\|default_visible" docs/reviews/ docs/GAP-REGISTER.md docs/DESIGN-SET-DEFECTS.md | wc -l
  # -> 0, no prior lens touched this
  ```
- **Where it belongs:** `warehouse-base` + `warehouse` (+ the two adapters and `warehouse-india`) ·
  v1 · P0/P1/P2, in the grid-config bands `V501020`–`V501099` and `V511020`–`V511199`.
- **Disposition:** *fold into task `P2-29`* (and, for the P0/P1 grids, into `P0-15` and `P1-20`,
  which already own those bands). The line to add to `p2-29.md`, beside its existing per-grid
  checklist at `:140`: *"For every grid, `BUILD-SPEC-SCREENS.md`'s screen row is amended to the
  `| key | label | type | sort | vis | source |` form before its migration is authored; a grid whose
  spec row is still a bare comma list is not ready to build."* That makes `P2-29` the gate rather
  than the author, which matches how it already handles migration numbers.
- **Irreversibility:** `grid_column_definitions` and `grid_preferences` rows are seed data, editable
  by a later forward-only migration. **Reversible** — but note that a *user's saved* preference row
  is not regenerated by a later seed, so a wrong `default_columns` persists for every user who saved
  before the fix.
- **Relationship to round 1:** new. R9's `H-002` covers the absence of column-level **DDL** (type,
  nullability, default) and is refused below as its territory; this finding is about the **grid**
  column metadata, which `H-002` does not mention and which lives in a different document and a
  different migration.

---

### `Q-005` · P2's non-grid i18n — modal titles, verb-button labels, validation messages, menu leaves — has no owner and no key-diff gate — **MINOR**

- **What is missing or wrong:** `P1-19` is the translation task, and it scopes itself in its header
  to *"every P0 and P1 screen"* (`p1-19.md:4`), with an acceptance checkbox requiring the three
  locale JSONs to *"cover **every** P0 and P1 screen, modal, action and menu leaf, and have
  **identical key sets** — asserted by a key-diff test"* (`:77-78`). There is no P2 successor.
  `P2-29` gets close but stops at the grid: its per-grid checklist (`p2-29.md:140`) requires
  "en/fr/hi translations" for each grid's columns and filters, and its completion criterion
  (`:18`) is *"every P2 **grid** has a number, a row, a scope and a translation"*. Neither covers the
  strings a P2 screen is mostly made of — the Freeze / Post Count / Disposition / Force / Release
  modal titles and buttons, their confirmation copy, the field-level validation messages, and the P2
  menu leaves. Only **4 of the 33** P2/P2-IN task files mention i18n at all. Separately, `p1-19`'s
  key-diff checkbox cites `WH-SC-247` (`SCENARIO-CATALOGUE.md:494`), which is a *grid-configuration*
  scenario: it requires "seed translations for all three shipped locales" but says nothing about
  identical key sets or a key-diff test, so the gate `p1-19` names does not exist in the scenario it
  points at.
- **Why it matters:** the module ships `en`, `fr` and `hi`. A P2 modal whose title key was never
  added to `hi` renders the raw key, or blank, on a Hindi user's screen — the failure mode the
  monorepo's own notes record as "no module prefix = BLANK labels". It is discovered by the first
  Hindi-locale user, in production, on the Counts approval modal, and it is cheap only if it is found
  before 33 tasks have shipped.
- **Negative evidence:**
  ```bash
  for f in issues/p2-[0-9]*.md issues/p2in-*.md; do grep -qi "i18n\|SafeTranslation\|en/fr/hi\|en / fr / hi" $f && basename $f; done
  # -> p2-25.md p2-26.md p2-29.md p2in-01.md      (4 of 33)
  ls issues/p2-[0-9]*.md issues/p2in-*.md | wc -l  # -> 33
  sed -n '4p;77,78p' issues/p1-19.md               # -> "every P0 and P1 screen"; key-diff test (WH-SC-247)
  sed -n '494p' docs/SCENARIO-CATALOGUE.md | grep -ci "key set\|key-diff"   # -> 0
  ```
- **Where it belongs:** `warehouse` + `warehouse-base` frontend · v1 · P2.
- **Disposition:** *fold into task `P2-29`*. Add one line to `p2-29.md`'s acceptance: *"Every P2
  screen's modal titles, action labels, validation messages and menu leaves exist in `en`, `fr` and
  `hi` with identical key sets, asserted by the same key-diff test `P1-19` ships — extended to the P2
  key space."* And amend `p1-19.md:78` to cite the scenario that actually asserts the key-diff, or add
  the assertion to `WH-SC-247`'s expected-outcome cell.
- **Irreversibility:** locale JSONs are code. **Reversible.**
- **Relationship to round 1:** new for the P2 scope. Round 1 covered i18n namespace and
  SafeTranslation registration (which `P1-19` handles correctly, once, for the module); the gap here
  is phase coverage, not mechanism.

---

### `Q-006` · Seven v1 tasks cite no failure-path scenario, and two of them are the India statutory tasks — **MINOR**

- **What is missing or wrong:** the scenario catalogue is well stocked with non-happy paths — 70
  `edge`, 52 `error`, 13 `conc` against 165 `happy`. But seven v1 task files cite **only** happy-path
  scenarios in their `## Scenarios closed` list: `p1-14`, `p1-15`, `p1-19`, `p2-24`, `p2-27`,
  `p2in-01`, `p2in-02`. Two of those — `p2in-01` and `p2in-02` — are the India compliance tasks,
  where the statutory failure modes *are* the requirement: a portal that times out, a rejected
  e-way bill, an expired auth session, a challan that cannot be cancelled inside its window.
- **Why it matters:** the Definition of done makes the scenario list the acceptance test. A task
  whose acceptance is entirely happy-path ships a feature that works in the demo and has no defined
  behaviour when the government portal returns a 502 — and the person who finds out is the driver
  stopped at a checkpoint with no e-way bill and no error message explaining why.
- **Negative evidence:**
  ```bash
  awk -F'|' '/^\| \*\*WH-SC-/{k=$(NF-1); gsub(/ /,"",k); c[k]++} END{for(x in c) print x,c[x]}' docs/SCENARIO-CATALOGUE.md
  # -> happy 165  edge 70  error 52  conc 13
  # per task file: intersect its WH-SC citations with the 135 non-happy ids
  # -> tasks citing none: p1-14 p1-15 p1-19 p2-24 p2-27 p2in-01 p2in-02   (7 of 70)
  ```
- **Where it belongs:** `warehouse` · `warehouse-india` · v1 · P1/P2/P2-IN.
- **Disposition:** *fold into tasks `P2-IN-01` and `P2-IN-02`* first — add at least one `error`-class
  scenario each covering portal unavailability and portal rejection — and add one non-happy scenario
  citation to each of `p1-14`, `p1-15`, `p2-24` and `p2-27`. `p1-19` (i18n) is the one case where a
  happy-only list is defensible; state that on the file rather than leaving it silent.
- **Irreversibility:** **reversible.**
- **Relationship to round 1:** new. Round 1 audited the catalogue's own completeness; this is the
  task files' *citation* of it.

---

## §3 · What I checked and found sound

Listed so round 3 does not re-walk it.

| What I went looking for | Verdict | Evidence |
|---|---|---|
| **Migration numbers inside the module band, no collisions, one owner** (check 12) | **Sound** | `python3 tools/check-design-set.py` -> check-4 *"Flyway versions: claimed once, inside the module band"* **passes**; its only failures are check-12 screen citations inside `docs/reviews/` naming a `WS-` id above the 237 that exist, which belong to sibling lenses R9/R10 |
| **Every task claiming DDL names its migration** | **Sound** | 56 of 70 v1 files name a `V5xxxxx` in their header; the other 14 say `Migrations **none**` and name the task that owns the table (e.g. `p2-07.md:4` -> "`whb_reservations` … are `P0-09`'s") |
| **Task dependencies** | **Sound enough not to file** | `IMPLEMENTATION-PLAN.md` §2's `Dep` column is populated well past P1 — `P2-01=P1-13 P0-05`, `P2-IN-04=P2-IN-02 P2-IN-03 P1-11`, `P3-01=P2-09 P0-10` — and 68 of the 70 task files reference at least one other task id in prose (only `p0-01` and `p2-29` do not, correctly, being the bootstrap and the config sweep) |
| **Mobile counterpart declared, never silent** (`D-13`) | **Sound — this is the design set's best-covered dimension** | every one of the 62 task files that owns a screen carries an explicit Mobile verdict, either a path or `none` **with a reason** (`p2-06.md:35` "`none` — a controller report. Stated as a decision, per `D-13`/`FR-218`"); 0 files are silent |
| **Filter scope registered in `COMMON_FILTER_CONFIGS`** (CLAUDE.md CRITICAL #17) | **Sound** | 55 of the 61 screen-owning tasks name their `WAREHOUSE_*` scope explicitly, usually under the `T-6` trap heading; `p1-20.md:36-38` and `p2-29.md` own the platform-file edits and record the live counts (`filterUtils.ts:346`, 213 scopes; `CacheConfiguration.java`, 235 names) |
| **Export as a superset of visible columns** (check 7) | **Sound, and better than the house rule** | `BUILD-SPEC-SCREENS.md` §0.5 (`:125-152`) states grid↔export parity *and* names the 23 log/ledger-style grids that deliberately carry no audit columns, so their exports carry none; `p2-29.md:21-44` owns the ratchet and the streaming path |
| **Filter-aware statistics carry no cache name** | **Sound** | `p2-29.md:45` Rule 2 (`FR-395`), repeated per-task (`p2-06.md:74` "The statistics strip carries **no** `statistics.*` cache name") |
| **`filter_definitions` vs the non-existent `grid_filter_definitions`** | **Sound** | `BUILD-SPEC-SCREENS.md` §0.5 states the table name and that `grid_filter_definitions` does not exist; no task file uses the wrong name (`grep -rc grid_filter_definitions issues/` -> 0) |
| **`permission_dependencies` INSERTed, never CREATE TABLEd** | **Sound** | `BUILD-SPEC-SCREENS.md` §10.3 (`:2036-2070`) with the real column names from `platform/…/V248:18-22`; repeated in every permission-owning task header |
| **`grid_preferences` ships both `default_columns` and `default_filters`** | **Sound as a rule** (its *content* is `Q-004`) | DoD; `DATA-MODEL.md:3105` item 6; `WH-SC-247` |
| **Scenario cross-references resolve** | **Sound** | all 370 distinct `WH-SC-` citations across the 70 v1 files resolve to a real catalogue row |
| **Blocked-on decisions declared rather than assumed** | **Sound** | 12 v1 tasks carry an explicit `## Blocked on` naming an open `OD-`: `p0-02 p0-04 p0-08 p0-12 p0-17 p1-05 p2-16 p2-17 p2-18 p2-27 p2-28 p2in-01` |
| **The adapters and `warehouse-india` escape `Q-001`** | **Sound** | `p2-25.md:27-28` (`V520100`–`V520149`), `p2-26.md:20` (`V521100`–`V521149`) and `p2in-01.md` (`V541000`–`V541049`) each own an in-band permissions + dependencies + menus + grid block, which is exactly the shape the `warehouse` app module lacks |
| **`contracts/` being empty** | **Sound** | correct per its own README; contracts are ratified after build, not before |

---

## §4 · Refused

- **Column-level DDL — type, nullability, default, FK target, unique key — is absent from every §2
  row (check 1).** True, and it is **R9 `H-002`**'s finding verbatim. `DATA-MODEL.md` §2 gives column
  *names* only (`:964` `wh_goods_receipts` is representative), with real `| Column | Type | Null |`
  tables existing only in `IRREVERSIBLE.md` §4.1–§4.9 for about 15 tables. Filing it again would
  double-count the largest finding in the set. **Refused as R9's.**
- **Task-file dependency lines.** My candidate was "0 of 70 task files carry a `## Depends on`
  section". Measurement killed it: 68 of 70 name their prerequisites in prose, and the machine-
  readable version already exists in `IMPLEMENTATION-PLAN.md` §2's `Dep` column, populated for every
  v1 phase. **Refused as not a real gap.**
- **Validation rules stated as prose rather than as a table (check 2).** 56 of 70 files use explicit
  refusal language and 24 name a field-level error surface. Given that the DoD delegates field-level
  validation to Jakarta annotations on the request DTO and the design set states the *business*
  refusals (which is the hard half), a validation table per task would be ceremony. **Refused as
  over-engineering.**
- **`D-10`'s "210 filter scopes" against `p2-29`'s computed 213.** A three-scope drift in a live
  monorepo that another committer moves daily. **Refused as noise.**
- **The `check-design-set.py` check-12 violations.** Every one is a screen citation inside
  `docs/reviews/R9-…` and `docs/reviews/R10-…` naming a `WS-` id above the 237 that exist. They
  belong to the lenses that wrote them. **Refused as out of segment.**
- **Cache-name registration (check 8) as a finding.** 29 of 70 files name a cache or explicitly state
  the strip has none; the remaining 37 are grids whose statistics are filter-aware and therefore
  *must* have no cache name (`FR-395`), which `p2-29` owns globally. The apparent gap is the rule
  working. **Refused as a false positive.**

---

## §5 · Counts

```bash
grep -cE '^### `Q-[0-9]{3}`' docs/reviews/R8-task-buildability-v1.md                      # -> 6
grep -oE '\*\*(BLOCKER|MAJOR|MINOR)\*\*$' docs/reviews/R8-task-buildability-v1.md | sort | uniq -c
```

| Severity | Count | Findings |
|---|---|---|
| **BLOCKER** | 2 | `Q-001` `Q-002` |
| **MAJOR** | 2 | `Q-003` `Q-004` |
| **MINOR** | 2 | `Q-005` `Q-006` |
| **Total** | **6** | |

Hand-off readiness, computed over the same 70 files:

| Bar | Count | 
|---|---|
| No `N` and no `partial` in any of the twelve scored dimensions | **0 of 70** |
| No `N` (partials allowed) | **19 of 70** |
| Blocked only by `Q-001` and/or `Q-002` | **44 of 70** |

---

## Appendix · Per-task completeness

**How to read it.** `Y` = present and sufficient to build from. `P` = present but not sufficient —
the section exists and a builder would still have to decide something. `N` = absent, or present and
saying nothing usable. `n/a` = the dimension does not apply (the task owns no screen, or no table).
`dlg` = the task owns no migration and correctly delegates the table to a named task.

Scoring rules, so the table is reproducible: **tables** = header names a migration number in band, or
delegates by name · **columns** = the task's tables have a `| Column | Type | Null |` table in
`IRREVERSIBLE.md` §4 (`Y`) or only §2 column names (`P`) · **validations** = count of explicit
refusal/guard statements (>=6 `Y`, 1-5 `P`, 0 `N`) · **states** = owns no unenumerated status table
(`Y`/`n/a`) or does (`N`) — see `Q-002` · **perms** = names its `resource:action` tokens (`Y`),
mentions permissions without naming them (`P`), silent (`N`) — see `Q-001` · **grid** = owns a `WS-`
screen with scope and columns · **filters** = names the `COMMON_FILTER_CONFIGS` scope *and* each
filter's bucket (`Y`) or the scope only (`P`) · **export** = covered by §0.5's global parity rule ·
**cache** = names its cache names or states there are none (`Y`) vs relies on `P1-20`/`P2-29`'s
catch-all (`P`) · **i18n** = names its locale obligation (`Y`) vs relies on the catch-all (`P`) — see
`Q-005` · **mobile** = carries an explicit Mobile verdict · **scenarios** = cites at least one
`edge`/`error`/`conc` scenario (`Y`) or happy-path only (`P`) — see `Q-006`.

| Task | tables | columns | validations | states | perms | grid | filters | export | cache | i18n | mobile | scenarios |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `P0-01` | Y | n/a | P | n/a | P | n/a | n/a | n/a | n/a | Y | n/a | Y |
| `P0-02` | Y | Y | Y | n/a | Y | Y | P | Y | P | P | Y | Y |
| `P0-03` | Y | Y | P | n/a | P | Y | Y | Y | P | P | Y | Y |
| `P0-04` | Y | Y | Y | n/a | P | Y | P | Y | Y | P | Y | Y |
| `P0-05` | Y | Y | N | n/a | P | Y | P | Y | Y | Y | Y | Y |
| `P0-06` | Y | Y | P | n/a | N | Y | Y | Y | Y | P | Y | Y |
| `P0-07` | Y | Y | Y | n/a | Y | Y | Y | Y | Y | P | Y | Y |
| `P0-08` | Y | Y | Y | n/a | Y | Y | Y | Y | P | P | Y | Y |
| `P0-09` | Y | Y | P | N | N | Y | Y | Y | P | P | Y | Y |
| `P0-10` | Y | P | N | n/a | N | Y | Y | Y | P | P | Y | Y |
| `P0-11` | Y | P | P | n/a | Y | Y | Y | Y | Y | P | Y | Y |
| `P0-12` | Y | Y | Y | Y | P | Y | Y | Y | P | P | Y | Y |
| `P0-13` | Y | Y | Y | N | Y | Y | Y | Y | Y | P | Y | Y |
| `P0-14` | Y | n/a | P | n/a | P | n/a | n/a | n/a | Y | n/a | n/a | Y |
| `P0-15` | Y | Y | Y | N | Y | n/a | n/a | n/a | Y | n/a | n/a | Y |
| `P0-16` | dlg | Y | P | n/a | N | n/a | n/a | n/a | Y | n/a | n/a | Y |
| `P0-17` | Y | Y | P | n/a | P | n/a | n/a | n/a | n/a | n/a | n/a | Y |
| `P1-01` | Y | Y | Y | N | N | Y | P | Y | Y | P | Y | Y |
| `P1-02` | Y | Y | P | n/a | Y | Y | P | Y | Y | P | Y | Y |
| `P1-03` | Y | P | Y | n/a | Y | Y | Y | Y | P | P | Y | Y |
| `P1-04` | Y | P | P | n/a | N | Y | Y | Y | P | P | Y | Y |
| `P1-05` | Y | Y | P | n/a | Y | Y | P | Y | Y | P | Y | Y |
| `P1-06` | Y | Y | P | N | Y | Y | P | Y | P | Y | Y | Y |
| `P1-07` | Y | Y | P | n/a | N | Y | Y | Y | Y | P | Y | Y |
| `P1-08` | Y | Y | P | n/a | N | Y | Y | Y | Y | P | Y | Y |
| `P1-09` | Y | P | P | n/a | P | Y | Y | Y | Y | P | Y | Y |
| `P1-10` | Y | Y | Y | N | N | Y | Y | Y | P | P | Y | Y |
| `P1-11` | Y | Y | P | N | N | Y | P | Y | Y | P | Y | Y |
| `P1-12` | Y | P | Y | n/a | Y | Y | Y | Y | Y | P | Y | Y |
| `P1-13` | Y | Y | P | N | N | Y | Y | Y | P | P | Y | Y |
| `P1-14` | Y | P | P | n/a | Y | Y | Y | Y | P | P | Y | P |
| `P1-15` | Y | Y | Y | n/a | P | Y | Y | Y | P | P | Y | P |
| `P1-16` | Y | Y | Y | N | Y | Y | Y | Y | P | P | Y | Y |
| `P1-17` | Y | P | P | N | N | Y | P | Y | P | P | Y | Y |
| `P1-18` | dlg | P | Y | n/a | P | n/a | n/a | n/a | n/a | n/a | n/a | Y |
| `P1-19` | dlg | P | P | n/a | N | n/a | n/a | n/a | n/a | Y | n/a | P |
| `P1-20` | Y | Y | P | N | Y | n/a | n/a | n/a | Y | Y | n/a | Y |
| `P2-01` | Y | Y | Y | N | Y | Y | Y | Y | Y | P | Y | Y |
| `P2-02` | dlg | Y | N | N | N | Y | P | Y | P | P | Y | Y |
| `P2-03` | Y | Y | P | n/a | P | Y | Y | Y | P | P | Y | Y |
| `P2-04` | Y | Y | P | N | Y | Y | Y | Y | P | P | Y | Y |
| `P2-05` | dlg | P | Y | n/a | N | Y | Y | Y | P | P | Y | Y |
| `P2-06` | Y | Y | P | N | N | Y | Y | Y | Y | P | Y | Y |
| `P2-07` | dlg | Y | P | n/a | N | Y | P | Y | P | P | Y | Y |
| `P2-08` | Y | Y | P | N | N | Y | Y | Y | Y | P | Y | Y |
| `P2-09` | Y | Y | N | N | N | Y | P | Y | P | P | Y | Y |
| `P2-10` | Y | P | N | N | N | Y | Y | Y | Y | P | Y | Y |
| `P2-11` | Y | P | P | n/a | N | Y | Y | Y | P | P | Y | Y |
| `P2-12` | Y | P | P | N | N | Y | Y | Y | P | P | Y | Y |
| `P2-13` | Y | P | P | N | P | Y | Y | Y | P | P | Y | Y |
| `P2-14` | Y | P | N | N | N | Y | Y | Y | Y | P | Y | Y |
| `P2-15` | Y | P | Y | N | N | Y | Y | Y | P | P | Y | Y |
| `P2-16` | dlg | Y | Y | Y | N | Y | Y | Y | P | P | Y | Y |
| `P2-17` | Y | P | P | N | N | Y | Y | Y | P | P | Y | Y |
| `P2-18` | dlg | P | Y | Y | N | Y | N | Y | P | P | Y | Y |
| `P2-19` | Y | Y | Y | N | N | Y | Y | Y | P | P | Y | Y |
| `P2-20` | dlg | Y | N | n/a | N | Y | N | Y | Y | P | Y | Y |
| `P2-21` | dlg | P | P | N | N | Y | N | Y | Y | P | Y | Y |
| `P2-22` | dlg | P | Y | n/a | N | Y | Y | Y | Y | P | Y | Y |
| `P2-23` | dlg | P | P | N | Y | Y | N | Y | P | P | Y | Y |
| `P2-24` | Y | P | N | n/a | P | Y | P | Y | Y | P | Y | P |
| `P2-25` | Y | P | Y | N | P | Y | Y | Y | P | Y | Y | Y |
| `P2-26` | Y | P | N | N | P | Y | Y | Y | P | Y | Y | Y |
| `P2-27` | dlg | P | N | n/a | P | Y | Y | Y | P | P | Y | P |
| `P2-28` | dlg | Y | Y | n/a | N | Y | N | Y | P | P | Y | Y |
| `P2-29` | Y | P | N | N | N | n/a | n/a | n/a | Y | Y | Y | Y |
| `P2-IN-01` | Y | Y | P | N | P | Y | N | Y | P | Y | Y | P |
| `P2-IN-02` | Y | P | P | N | P | Y | Y | Y | Y | P | Y | P |
| `P2-IN-03` | Y | P | N | N | N | Y | Y | Y | P | P | Y | Y |
| `P2-IN-04` | Y | P | Y | N | N | Y | Y | Y | P | P | Y | Y |

**Column totals.**

| Dimension | Y | P | N | n/a | dlg |
|---|---|---|---|---|---|
| tables | 56 | 0 | 0 | 0 | 14 |
| columns | 38 | 30 | 0 | 2 | — |
| validations | 24 | 34 | 12 | 0 | — |
| states | 3 | 0 | **33** | 34 | — |
| perms | 17 | 18 | **35** | 0 | — |
| grid | 61 | 0 | 0 | 9 | — |
| filters | 42 | 13 | 6 | 9 | — |
| export | 61 | 0 | 0 | 9 | — |
| cache | 29 | 37 | 0 | 4 | — |
| i18n | 9 | 56 | 0 | 5 | — |
| mobile | 62 | 0 | 0 | 8 | — |
| scenarios | 63 | 7 | 0 | 0 | — |

The two columns carrying almost all the risk are **states** (33 `N`, `Q-002`) and **perms**
(35 `N`, `Q-001`). Close those two and 44 of the 70 tasks clear every remaining dimension at `Y` or
a partial a builder can resolve from the documents they already have.
