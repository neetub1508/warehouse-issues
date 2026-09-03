# R20 — configuration, master data and the day-1 setup surface

**Date** 2026-09-02 · **Prefix** `RE-` · **Branch** `docs/round-3-functional-completeness`

**File set read — 24 files.**

```bash
cd /Users/bbhushan/work/git/workspace/warehouse-issues
# docs/ (10): DECISIONS.md · WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md · DATA-MODEL.md
#             BUILD-SPEC-SCREENS.md · IRREVERSIBLE.md · MODULE-INTEGRATION.md
#             SCENARIO-CATALOGUE.md · PORT-AND-ADAPTER-CONTRACT.md
#             GAP-REGISTER.md · GAP-REGISTER-R2.md   (+ DESIGN-SET-DEFECTS.md §X-004, §X-029 read in place)
# docs/reviews/ (5): R11 R12 R16 R17 R18 R19   (read first, per the brief's governing rule)
# issues/ (9): p0-04 p0-05 p0-06 p0-07 p0-13 p0-15 p1-02 p1-05 p1-20   (+ p1-03 p2-05 p2-12 p2-19 p5-16 in section)
# classic (4): platform/backend/src/main/resources/db/migration/V110__Add_aws_s3_configuration_settings.sql
#              platform/backend/src/main/resources/db/migration/V16__Add_menu_management_system.sql
#              platform/backend/src/main/java/ai/platform/controller/AdminSettingsController.java
#              platform/frontend/src/app/dashboard/admin-settings/page.tsx
grep -rohE "\bRE-[0-9]{1,3}\b" docs/ issues/ | wc -l        # → 0   (the prefix is free)
```

**Method, in three sentences.** I did not read the set as a feature list; I read it as an *installer*
— an empty database on a Monday morning, and the question of whether anything can be posted to the
ledger by Friday without someone inventing a value. Every parameter, flag, threshold, policy row and
seed list the set names anywhere was extracted by command and then asked five questions: does it have
a **column**, a **default**, a **screen**, a **permission**, and a stated **scope**. Where two of them
could contradict I looked for the precedence rule, and where `Z-001` had already found the ladder
missing I moved on rather than restating it.

---

## §1 · Verdict

**A fresh install of this product cannot post its first movement, and the reason is not a hard one —
it is that nothing in the set creates a stock period.** `whb_stock_movements.period_id` is `NOT NULL`
with an FK to `whb_stock_periods` (`DATA-MODEL.md:616`), `V500019` is a `CREATE TABLE` with no seed
(`DATA-MODEL.md:2899`), `WS-045`'s action list is *Soft close · Close · Reopen*
(`BUILD-SPEC-SCREENS.md:1390`), and the one place the set describes creating a period gives it the
guard *"the previous period exists"* (`BUILD-SPEC-SCREENS.md:270`). `P0-07` knows: *"periods must be
seeded before the first post … the install guide must say so, or the first demo fails with an FK
violation nobody can read"* (`p0-07.md:79-81`). There is no seed and there is no install guide.

That is the shape of this whole lens. The set is **exceptionally good at deciding what a setting must
be** — thirteen open catalogues instead of enums (`D-10`), a dated-obligation register that makes a
threshold without a job a merge blocker (`FR-165`), effective-dated valuation policies, a specificity
ladder on GL posting rules that `Z-001` correctly holds up as the exemplar. It is **weak at the last
mile**: the value, the row, the screen and the person. Seven `admin_settings` keys are named across
the set and not one carries a default, a type or a scope; the migration that seeds them lists five and
an ellipsis; the platform screen that would edit them is a hard-coded twelve-entry array with no
warehouse tab. Fourteen registries are told to ship "+ seed" and exactly one of them — owner types —
has its values written in the task file that writes the migration.

Three things are worth saying in the set's favour before the findings. `MODULE-INTEGRATION.md` §15 is
the best rollback section I have read in either design set and answers the disable/remove/un-apply
question properly. The **per-what** question is answered correctly nearly everywhere it matters:
`owner_id` on the line not the header, GSTIN on the branch not the warehouse, reorder policy at item ×
site, valuation effective-dated per company × category × site. And `P2-19`'s go-live machinery is
genuinely strong — which is exactly why the period ordering defect in `RE-001` matters: it is a bug in
the best part of the plan, not in the worst.

**Eight findings: 2 BLOCKER, 4 MAJOR, 2 MINOR.** All eight are reversible in schema terms; four must
land before `PNR-1` (`V500030`) because they are seed content of migrations that precede it.

---

## §1.1 · The settings inventory, computed

**Every `admin_settings` key the set names, anywhere:**

```bash
grep -rhoE "warehouse\.[a-z0-9_]+\.[a-z0-9_.]+" docs/*.md issues/*.md | grep -v adapter | sort -u
# → 7 keys
```

| # | Key | Named at | Default | Type | Scope stated | Screen | In a seed migration? |
|---|---|---|---|---|---|---|---|
| 1 | `warehouse.negative_stock.default_mode` | `p0-15.md:40` · `DATA-MODEL.md:828`,`:2944` · `p1-03.md:12` | — | — | install (inert — `Z-001`) | none | `V501100` |
| 2 | `warehouse.period.soft_close_requires_approval` | `p0-15.md:40` · `DATA-MODEL.md:2944` | — | — | — | none | `V501100` |
| 3 | `warehouse.outbox.max_attempts` | `p0-15.md:41` · `DATA-MODEL.md:2944` | — | — | — (and duplicates a column) | none | `V501100` |
| 4 | `warehouse.reservation.default_ttl_minutes` | `p0-15.md:41` · `DATA-MODEL.md:2944` | — | — | — | none | `V501100` |
| 5 | `warehouse.port.rejected_queue_threshold` | `p0-15.md:42` · `p0-08.md:82` · `p0-13.md:59` · `BUILD-SPEC-SCREENS.md:1432` | — | — | — | none | `V501100` |
| 6 | `warehouse.position.max_contention_retries` | `p0-03.md:18` **only** | — | — | — | none | **no** |
| 7 | `warehouse.outbox.max_cursor_lag` | `p0-11.md:19` **only** | — | — | — | none | **no** |

Both seed migrations end in an ellipsis: `V501100` names five keys then *"…"* (`p0-15.md:39-42`,
`DATA-MODEL.md:2944`); `V511200` names **none** — *"`admin_settings` seed, category `WAREHOUSE`,
app-owned keys"* (`p1-20.md:23`, `DATA-MODEL.md:3017`).

**Every non-`admin_settings` configuration surface, and what it is scoped to.** This is the part the
set does well, and it is listed so the findings below read against it rather than around it:

| Configuration object | Grain | Screen | Ver |
|---|---|---|---|
| `whb_item_site_settings` — reorder point, safety stock, min/max, lead time, ABC/XYZ/VED/FSN/HML, count class, `negative_stock_mode`, `default_receipt_status_code` | item × site | WS-027 | v1·P1 |
| `whb_items` — `shelf_life_days`, `min_shelf_life_receipt_pct`, `min_shelf_life_ship_pct`, lot/serial/expiry control modes, four status facts | item | WS-023 | v1·P1 |
| `whb_valuation_policies` — method, effective-dated | company × category × site | WS-050 | v1·P2 |
| `whb_gl_posting_rules` — full wildcard tuple + computed `specificity` + a **Test resolution** modal | wildcard | WS-051 | v1·P2 |
| `wh_putaway_rules` — `uk(warehouse_id, sequence)` | warehouse × sequence | WS-088 | v1·P2 |
| `whb_allocation_strategies` — `scope_type`/`scope_ref` | one dimension (`Z-001`: insufficient) | WS-048 | v1·P2 |
| `wh_count_programs` — `frequency_days`, `schedule_cron`, `is_blind_count`, `recount_threshold_pct`, `approval_threshold_pct`, `approval_threshold_value`, `freeze_locations`, `max_tasks_per_run` | warehouse × programme | WS-104 | v1·P2 |
| `whb_number_series` — prefix, width, `reset_policy`, `is_gapless` | document type × company × warehouse | WS-061 | v1·P1 |
| `whb_outbox_subscriptions` — `max_attempts`, `backoff_seconds`, `event_type_filter`, `owner_filter_id` | subscriber | WS-057 | v1·P2 |
| `whb_retention_policies` | country / record class | — | v1·P4 |
| `wh_purchase_orders.over_receipt_tolerance_pct` | **PO header only** (`RE-004`) | WS-085 | v1·P1 |
| Module enable flags `ENABLE_WAREHOUSE*` / `enable.warehouse.*` | deploy | none (env) | v1 |

**Thresholds named in a v1 requirement or task with no column, no key and no screen** — the shape this
lens hunts. `RA-008` owns `FR-145`'s adjustment threshold; these are the others:

| Threshold | Named at | Home |
|---|---|---|
| `near_expiry_days` — the notify-before-expiry horizon | `FR-160` (`:330`) · `p2-05.md:18,76,106` · fixture *"near-expiry 45 days"* `SCENARIO-CATALOGUE.md:326` | **none** — `grep -c near_expiry docs/DATA-MODEL.md` → **0**, `docs/BUILD-SPEC-SCREENS.md` → **0** |
| item over-receipt tolerance · warehouse default tolerance | `FR-130` (`:295`) · `WH-SC-066`/`WH-SC-067` | **none** — `RE-004` |
| *movements pending approval beyond **N hours*** | `p0-13.md:27-29` | **none** |
| *unresolved `wh_blocked_movements` beyond **N minutes*** | `p0-13.md:27-29` | **none** (`WS-097` computes `ageMinutes`; nothing reads it) |

---

## §1.2 · The day-1 path, step by step

`Z-009` established that **no master load order is stated** and folded the fix into `P2-19`'s
checklist seed. This table is the other half of the same question and does not repeat it: for each
step, **is there a screen at the version the step is needed, and who performs it.** The order below is
`Z-009`'s, extended at both ends — install before masters, first transaction after.

| # | Step | Object | Screen · Ver·Ph | Performed by | Gap |
|---|---|---|---|---|---|
| 0 | Build the image, enable the modules | `MAVEN_PROFILES`, `ENABLE_WAREHOUSE*` | none (deploy) | ops | `FLYWAY_OUT_OF_ORDER=true` for warehouse-first is *"not discoverable"* and is deferred to the install guide — **`RE-006`** |
| 1 | The fourteen registries seed themselves | `whb_movement_types` … `whb_condition_codes` | WS-001–WS-014 · P0/P1 | migration | 1 of 14 seed value lists is enumerated in its own task file — **`RE-005`** |
| 2 | Company | `whb_companies` | WS-015 · v1·P1 (built in `P0-07`) | ADMIN | ✔ Department-shape screen |
| 3 | **The first stock period** | `whb_stock_periods` | WS-045 · v1·P0 | **nobody** | **`RE-001`** — no seed, no create action, no job, and the only stated guard is unsatisfiable |
| 4 | House owner | `whb_owners` | WS-019 · v1·P0 | migration | ✔ `FR-108` *"exactly one house owner is seeded by the first migration"* |
| 5 | Site | `whb_warehouses` | WS-016 · v1·P1 | ADMIN | the non-physical `TRANSIT-WH` the transfer flow posts through is in no migration and no task — **`RE-002`** |
| 6 | That site's virtual locations | `whb_locations` | **none** | migration `V500013` only | a site created on WS-016 *after* `V500013` has run gets none — **`RE-002`** |
| 7 | Location hierarchy / bin grid | `whb_locations` | WS-017 · WS-018 · v1·P1 | ADMIN | ✔ generator screen exists |
| 8 | UoM classes and UoMs | `whb_uom_classes`, `whb_uoms` | WS-007 · WS-034 · v1·P1 | migration + ADMIN | seed carries no code list and no `unece_rec20_code`/`gst_uqc_code` values — **`RE-005`** |
| 9 | Item categories | `whb_item_categories` | WS-022 · v1·P1 | ADMIN | ✔ |
| 10 | Items, identifiers, packaging, conversions | `whb_items` + 3 | WS-023–WS-026 · WS-065 · v1·P1 | ADMIN | ✔ import framework is strong (`P1-10`) |
| 11 | Counterparties and their roles | `whb_counterparties` | WS-021 · WS-011 · v1·P1 | ADMIN | ✔ |
| 12 | Item × site settings | `whb_item_site_settings` | WS-027 · v1·P1 | ADMIN | negative-stock ladder (`Z-001`); `near_expiry_days` has no field (**`RE-007`**) |
| 13 | Number series | `whb_number_series` | WS-061 · v1·P1 | ADMIN | reset path (`Z-002`) |
| 14 | Install parameters | `admin_settings` category `WAREHOUSE` | **none** | — | no tab, no permission of its own — **`RE-003`** |
| 15 | Roles and grants | `roles`, `role_permissions`, owner grants, warehouse scope | WS-020 · platform · v1·P0 | ADMIN | no operational role bundle (`Z-010`); warehouse scope has no table (`RA-001`) |
| 16 | Opening stock | `wh_opening_stock_batches` | WS-150 · v1·P2 | manager | posts `OPENING_BALANCE` movements that need a period — **`RE-001`** |
| 17 | Cut-over certification | `wh_cutover_checklists` | WS-151 · v1·P2 | manager | the checklist opens the period *after* the opening is posted — **`RE-001`** |
| 18 | First receipt against a PO | `wh_purchase_orders` → GRN | WS-085 · WS-090 · v1·P1 | storekeeper | over/short-receipt tolerance has no column at either grain — **`RE-004`** |

**Steps with no screen at all: two** — #6 (virtual locations for a site created after go-live) and
#14 (the warehouse settings). **Steps with a screen and no creation path: one** — #3.

---

## §2 · The findings

### `RE-001` · Nothing in the set creates a stock period — no seed, no screen action, no job — while `period_id` is `NOT NULL` on every movement, and the cut-over checklist opens the first period *after* the opening stock has been posted into it — **BLOCKER**

- **What is missing or wrong.** Four facts that cannot all be true.

  1. **The column is mandatory.** `whb_stock_movements.period_id` — *"UUID → `whb_stock_periods` · Null: **no**"* (`DATA-MODEL.md:616`), `IRR-22`. `IRREVERSIBLE.md:345` makes the period table a `PNR-1` prerequisite: *"the period table's `CREATE TABLE`, **before `P0-02`**"*, and `DATA-MODEL.md:3098` lists `V500019` among `PNR-1`'s six prerequisites.
  2. **No migration seeds a period row.** `WHB-19` is *"`whb_stock_periods`, `whb_stock_period_overrides`. **Must precede `V500030`**"* (`DATA-MODEL.md:2899`) — two `CREATE TABLE`s. `P0-07`'s `V500019` scope (`p0-07.md:24-26`) is the column list and nothing else. `grep -n "whb_stock_periods" docs/DATA-MODEL.md | grep -c seed` → **0**.
  3. **No screen creates one.** `WS-045`: *"Actions: **Soft close** · **Close** · **Reopen** — three modals"* (`BUILD-SPEC-SCREENS.md:1390`), repeated verbatim in the task (`p0-07.md:52`). The only description of period creation anywhere is the §0.11 ladder row: `whb_stock_periods | — | OPEN | **period generation** | whb_stock_periods:create | **the previous period exists** | no` (`BUILD-SPEC-SCREENS.md:270`). *"Period generation"* names no screen, no modal, no endpoint and no service method; and its guard makes the **first** period unreachable by its own rule, because no previous period exists on a fresh install.
  4. **No job rolls the period forward.** `P0-13` owns the job register and enumerates the v1 dated obligations (`p0-13.md:55-63`) — reservation expiry, position snapshot, drift rebuild, outbox publisher, rejected-queue alert, ledger partitions, lot expiry, cycle-count scheduling. **Period generation is not among them.** So even if the first period is created by hand, the first movement of the following month fails the same FK.

  **And the go-live sequence is inverted.** `FR-413`'s checklist is *"masters loaded, mappings
  resolved, opening posted, value matched, period opened"* (`:728`), `WH-SC-050` repeats it, and
  `p2-19.md:88-89` makes it a gate: *"certification blocks opening the first stock period"*, with
  acceptance *"The first stock period **cannot** be opened while `tie_out_variance <> 0`"*
  (`p2-19.md:107`). But the opening stock **is** movements — `OPENING_BALANCE` postings from
  `VIRT-OPENING` (`p2-19.md:31`, `WH-SC-049`) — each carrying a `NOT NULL period_id`, and `FR-020`
  (`:137`) refuses a posting whose date does not fall in an open period. The step that produces the
  evidence for opening the period is gated on the period being open.

- **Why it matters.** `D-7`'s standalone reference configuration and `DECISIONS.md` §5's v1 exit
  criterion both begin *"a storekeeper creates a site … receives against a purchase document"*. On a
  clean install that first `POST /api/warehouse/movements` returns a foreign-key violation on
  `period_id` and there is no screen anywhere in the product that fixes it. `P0-07` predicted this
  exactly — *"the install guide must say so, or the first demo fails with an FK violation nobody can
  read"* (`p0-07.md:80-81`) — and then deferred it to a document that does not exist (`RE-006`). The
  second failure is dated: **1 April year one plus one month, 00:00**, when the period the install
  engineer typed by hand ends and nothing has created the next one.
- **Negative evidence.**
  - `grep -rn "whb_stock_periods" docs/DATA-MODEL.md issues/*.md | grep -ci seed` → **0**.
  - `grep -rn -i "period generation\|generate period\|period roll" docs/ issues/ | grep -v reviews` → **1 hit**, `BUILD-SPEC-SCREENS.md:270`.
  - `grep -rn "whb_stock_periods:create" docs/ issues/` → **1 hit**, the same line. The permission is seeded by `V501000`'s blanket *"view/create/edit/delete/export"* (`DATA-MODEL.md:2940`) and nothing in the product calls it.
  - `p0-13.md:55-63` — the eight v1 dated obligations, none of them period generation.
- **Where it belongs.** `warehouse-base` · v1 · **P0** — `V500019`, and it must land there because
  `V500019` precedes `PNR-1`.
- **Disposition.** *Fold into tasks `P0-07` and `P2-19`.*
  - `P0-07` — add: *"`V500019` **seeds the current and next stock period** for the default company with `warehouse_id = NULL` (all sites), derived from the install date, so an install can post before anyone opens a screen. `WS-045` gains a **Generate periods** action (`whb_stock_periods:create`) taking a company, an optional warehouse, a start date and a count, and a **period-generation job** joins `P0-13`'s register with cadence `MONTHLY` and missed-run policy `CATCH_UP` — a period boundary that arrives while the job is down must not stop receiving. §0.11's guard becomes 'the previous period exists **or none exists for this (company, warehouse)**'."*
  - `P2-19` — add: *"the checklist item is **'operating period opened'**, and it is distinct from the period the opening balances post into. The opening batch posts into a period whose `end_date` is the as-at date, which the batch opens and closes as part of `apply`; certification gates the **operating** period, not the opening one. `WS-151` states which period each item refers to."*
- **Irreversibility.** **Reversible** — a seed row and a job, not a schema change. But it must land in
  `V500019` itself, because every later migration and every acceptance test in P0 posts a movement.
- **Relationship to earlier rounds.** **New.** `RA-004` covers what a *close* does to in-flight
  approvals; `Z-008` covers opening-stock *reversal*; `Q-002` covers undeclared status domains.
  Nothing asked who creates the first row.

---

### `RE-002` · The virtual-location seed — the migration that must exist before the ledger's first row — is specified five different ways, and its stated mechanism cannot give a second site any virtual locations at all — **BLOCKER**

- **What is missing or wrong.** `IRR-05` requires virtual locations to exist *before the first
  movement can balance*, and `WHB-13` marks `V500013` *"★ Must precede `V500030`"*
  (`DATA-MODEL.md:2893`). Five documents give its content, and no two agree:

  | Source | Codes | n |
  |---|---|---|
  | `FR-084` (`:224`) | `SUPPLIER` `CUSTOMER` `ADJUSTMENT` `SCRAP` `PRODUCTION` `IN_TRANSIT` `COUNT_VARIANCE` `OPENING_BALANCE` `CONSUMED` `JOB_WORKER` | 10 |
  | `DATA-MODEL.md:478-481` | `SUPPLIER` `CUSTOMER` **`ADJUSTMENT_OFFSET`** `SCRAP` `PRODUCTION` `JOB_WORKER` `OPENING_BALANCE` `COUNT_VARIANCE` `IN_TRANSIT` | 9 |
  | `p1-05.md:66-68` — the task that writes the migration | `SUPPLIER` `CUSTOMER` `ADJUSTMENT` `SCRAP` `PRODUCTION` `IN_TRANSIT` `COUNT_VARIANCE` **`OPENING`** *"…"* | 8 + ellipsis |
  | `SCENARIO-CATALOGUE.md:115-117` | `VIRT-SUPPLIER` `VIRT-CUSTOMER` `VIRT-ADJUSTMENT` `VIRT-SCRAP` `VIRT-PRODUCTION` `VIRT-COUNT-VAR` `VIRT-OPENING` `VIRT-CONSUMED` `VIRT-JOB-WORKER` (+ the value-offset row) | 10, prefixed |
  | `PORT-AND-ADAPTER-CONTRACT.md:1739-1741` | `VIRT-SUPPLIER` `VIRT-CUSTOMER` `VIRT-ADJUSTMENT` `VIRT-SCRAP` `VIRT-OPENING` `VIRT-COUNT-VAR` + the warehouse `TRANSIT-WH` | 6 + a warehouse |

  **Exactly three codes — `SUPPLIER`, `CUSTOMER`, `SCRAP` — are spelled identically in all five.** The
  opening-balance location is `OPENING_BALANCE`, `OPENING` and `VIRT-OPENING` in three of them; the
  count-variance location is `COUNT_VARIANCE` and `COUNT-VAR`; `CONSUMED` is in two and absent from
  three. The `VIRT-` prefix that every worked example and every acceptance criterion uses
  (`p0-02.md:196`, `p2-09.md:32`, `p2-19.md:31,61,102`, `p2-02.md:64`) appears in **no requirement and
  no task file**.

  **The mechanism is worse than the naming.** `DATA-MODEL.md:478` — *"Virtual locations are seeded per
  install **and per site**, **by the same migration that creates the table** (`V500013`)"*. A migration
  runs once, at install, before any site exists; sites are created afterwards on `WS-016`. **Nothing
  creates virtual locations for the second site**, and no service hook, trigger or post-create step is
  specified anywhere. And the fixed code list cannot be per-site in any case, because
  `whb_locations.code` is **globally unique** — *"uk(`warehouse_id`,`code`); uk(`code`) globally, so a
  scanned location string resolves without a site"* (`DATA-MODEL.md:451`), restated in the ER block as
  *"globally unique — a scan resolves without a site"* (`:1742`). Two sites cannot both hold a location
  coded `VIRT-SUPPLIER`, and no document states the per-site code convention that would resolve it.

  **`TRANSIT-WH` is in the same condition.** The transfer flow posts `TRANSFER_DEPART` to
  `TRANSIT-WH / IN_TRANSIT-<ref>` (`PORT-AND-ADAPTER-CONTRACT.md:1592-1593`, `p2-02.md:16`), and the
  fixture declares it *"`TRANSIT-WH` with `is_physical = false`"* (`SCENARIO-CATALOGUE.md:111`). It is
  a `whb_warehouses` row. `P1-05`'s `V500012` creates the table and seeds nothing;
  `grep -rn "TRANSIT-WH" issues/*.md` → **2 hits**, both consumers (`p2-02.md:16`, `p6-08.md:156`).

- **Why it matters.** `L-1` is the invariant the whole ledger rests on, and a receipt's counter-side is
  one of these rows. A migration author reading `p1-05.md:66` seeds eight unprefixed codes; every
  acceptance test in the set asserts against `VIRT-`-prefixed ones; the port contract's worked receipt
  balances against `VIRT-SUPPLIER`. Whichever is written, the other four documents are wrong, and this
  is a `PNR-1` prerequisite so the codes are on ledger rows forever (`IRR-26` makes the location code a
  stable string key). The per-site consequence is sharper and lands on the exit criterion directly:
  `DECISIONS.md` §5 requires the v1 storekeeper to *"transfer stock to a second site through
  in-transit"*, and the second site has no `VIRT-CUSTOMER` to ship to and no `TRANSIT-WH` to depart to.
- **Negative evidence.**
  - `grep -rn "VIRT-" docs/ issues/ | grep -v reviews` → hits in `SCENARIO-CATALOGUE.md`, `PORT-AND-ADAPTER-CONTRACT.md` and six acceptance criteria; **zero** in `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` and **zero** in `p1-05.md`.
  - `grep -rn -i "when a warehouse is created\|per site" docs/ issues/ | grep -v reviews` → 6 hits, all the phrase *"per install and per site"*; **none** names a service, trigger or screen step that creates them for a new site.
  - `grep -rn "TRANSIT-WH" issues/*.md | wc -l` → **2**, both readers.
- **Where it belongs.** `warehouse-base` · v1 · **P1**, in `V500013` (and `V500012` for `TRANSIT-WH`) —
  both before `PNR-1`.
- **Disposition.** *Fold into task `P1-05`, plus a one-line amendment to `FR-084` and
  `DATA-MODEL.md` §2.1 note 2.*
  - `P1-05` — add: *"**The virtual-location code convention is `VIRT-<PURPOSE>-<SITE CODE>`**, because `whb_locations.code` is globally unique; the display name is the unprefixed purpose. The v1 purposes are the ten of `FR-084` — `SUPPLIER`, `CUSTOMER`, `ADJUSTMENT`, `SCRAP`, `PRODUCTION`, `IN_TRANSIT`, `COUNT_VARIANCE`, `OPENING_BALANCE`, `CONSUMED`, `JOB_WORKER` — spelled that way in every document. `V500013` seeds them for the sites that exist; **creating a `whb_warehouses` row creates its virtual-location set in the same transaction**, in the warehouse service, and `WS-016`'s create modal states it. `V500012` seeds the non-physical `TRANSIT-WH` warehouse (`is_physical = false`) that `FR-085`'s per-reference transit locations hang from."*
  - `FR-084` and `DATA-MODEL.md:478-481` are amended to the same ten codes; `p1-05.md:66`'s ellipsis and its `OPENING` are removed.
- **Irreversibility.** **Reversible while `V500013` is unwritten; irreversible after.** The location
  `code` is a stable key that ledger rows resolve against (`IRR-26`), so renaming it after the first
  movement means rewriting `whb_stock_movement_lines`, which `L-2` forbids.
- **Relationship to earlier rounds.** **New for the nine functional locations and the per-site
  mechanism.** `X-029`/`OD-13` own **only** the value-offset location's name
  (`VALUE_OFFSET` / `LANDED_COST_OFFSET` / `ADJUSTMENT_OFFSET`) and are deliberately excluded from the
  table above. `Y-007` owns location *deactivation*, not creation.

---

### `RE-003` · Seven install parameters, no defaults, no scopes, no screen, and one platform permission that gates all of them — and the "two platform files" the plan budgets for is three — **MAJOR**

- **What is missing or wrong.** Four defects in one surface (the inventory is §1.1 above).

  1. **No key has a value.** Not one of the seven carries a default, a `setting_type`, a validation
     rule or a stated scope anywhere in the set. `admin_settings` has all four columns —
     `default_value`, `setting_type`, `validation_rules`, `description`
     (`platform/backend/src/main/resources/db/migration/V110__Add_aws_s3_configuration_settings.sql:5-24`)
     — and the seed migration that must fill them lists five key *names* and an ellipsis.
  2. **Two keys are in no seed migration at all.** `warehouse.position.max_contention_retries`
     (`p0-03.md:18`) and `warehouse.outbox.max_cursor_lag` (`p0-11.md:19`) are both `warehouse-base`
     concerns and neither appears in `V501100`'s list. A `getSettingByKey` on an absent key needs a
     code-side fallback that no document specifies.
  3. **No screen edits any of them, and the platform screen is not extensible by data.** The tabs are a
     hard-coded array literal — `const tabs = [ … ]` at
     `platform/frontend/src/app/dashboard/admin-settings/page.tsx:85-162`,
     `grep -c "      id: '" …` → **12** — each backed by a bespoke
     `AdminSettings<X>Tab.tsx` (14 components in `platform/frontend/src/components/adminSettings/`).
     `grep -in warehouse …/admin-settings/page.tsx` → **0**. The backend is generic — category is a
     `@PathVariable` on `GET /category/{category}` and `PUT /category/{category}/bulk`
     (`AdminSettingsController.java:94-100`, `:201-212`) — so the rows are reachable by API and by
     nothing a user can click. `grep -rn -i "admin.settings" docs/BUILD-SPEC-SCREENS.md` finds the
     phrase only as the *secret-masking idiom* for `WS-175`; **no `WS-nnn` is a warehouse settings
     screen.**
  4. **The only permission is platform-wide.** Both endpoints are gated
     `hasAuthority('admin_settings:view')` / `('admin_settings:edit')`
     (`AdminSettingsController.java:81`, `:202`). Whoever may change the application logo may change
     `warehouse.negative_stock.default_mode`; a stock controller who should own it cannot, without
     being granted edit rights over Security, Email, Storage and Backup as well. `FR-401`'s
     `resource:action` model reaches every warehouse table and stops at the settings that govern them.

  **Two further consequences, each small and each real.** `warehouse.period.soft_close_requires_approval`,
  read plainly, switches off `L-8` — *"a soft-close needs an approved override"* — and `FR-020`'s
  *"`SOFT_CLOSED` requires an override permission and records the override"*; nothing states what the
  `false` branch means, and `I-10`'s session-GUC trigger has no `false` branch either. And
  `warehouse.outbox.max_attempts` (install) duplicates `whb_outbox_subscriptions.max_attempts`
  (subscriber, `DATA-MODEL.md:878`) **with no precedence rule** — the same defect shape `Z-001` found
  in the negative-stock ladder, in a pair `Z-001` does not cover.

  Lastly, `P1-20` is explicit that *"`COMMON_FILTER_CONFIGS` … and `CacheConfiguration.java` … **Neither
  has a per-module extension point**, and **every warehouse grid edits both**"* (`p1-20.md:30-38`), and
  `D-10`'s corollary names the same two files. **It is three.** `admin-settings/page.tsx` has no
  per-module extension point either, and a warehouse tab is a platform frontend commit plus a new
  component — which is the same serialisation hazard the task tells the reader to plan for.

- **Why it matters.** A shipped install default that no administrator can see or change is not a
  default, it is a constant with extra steps. The first support call — *"we want negative stock allowed
  at the main store"* — has no screen to point at, and `Z-001` has already established that the value,
  once changed, does nothing. The permission gap is the one that bites in an audit: `FR-408`'s whole
  argument is that a transition with no verb permission is a transition anybody with `:edit` can
  perform, and here the transition is *changing the rule that governs the ledger*.
- **Negative evidence.**
  - `grep -rhoE "warehouse\.[a-z0-9_]+\.[a-z0-9_.]+" docs/*.md issues/*.md | grep -v adapter | sort -u | wc -l` → **7**.
  - `grep -rn "default_value\|setting_type\|validation_rules" docs/ issues/ | grep -v reviews` → **0**.
  - `grep -c "      id: '" platform/frontend/src/app/dashboard/admin-settings/page.tsx` → **12**; `grep -in warehouse` on the same file → **0**.
  - `grep -rn "admin_settings:" docs/ issues/ | grep -v reviews` → **0** — the set never names the permission its own settings will actually be gated by.
- **Where it belongs.** `warehouse-base` + `platform` · v1 · **P0** (`V501100`) and **P1** (`V511200`).
- **Disposition.** *Fold into tasks `P0-15` and `P1-20`.*
  - `P0-15` — add: *"`V501100` seeds **every** base key with `setting_value`, `default_value`, `setting_type`, `description` and a `validation_rules` bound, and the list is closed — no ellipsis. The seven v1 keys and their defaults are: `negative_stock.default_mode` = `BLOCK` (STRING), `period.soft_close_requires_approval` = `true` (BOOLEAN) **and it may not be set false — the key records who approves, never whether approval is required (`L-8`)**, `outbox.max_attempts` = `10` (INTEGER, the **fallback** for a `whb_outbox_subscriptions` row whose own `max_attempts` is null; the subscription wins), `reservation.default_ttl_minutes`, `port.rejected_queue_threshold`, `position.max_contention_retries`, `outbox.max_cursor_lag`. **Every key states its scope in `description`, and `admin_settings` can express only install scope** — a key needing company × site scope is a table, not a key (`p5-16.md:18`)."*
  - `P1-20` — add: *"the honest limit is **three** platform files, not two: `filterUtils.ts`, `CacheConfiguration.java` **and `platform/frontend/src/app/dashboard/admin-settings/page.tsx`**, which needs a thirteenth tab and an `AdminSettingsWarehouseTab.tsx` gated on a warehouse permission — following the Doc OCR AI precedent at `:145-152`, whose tab is invisible in a deployment without the module. The warehouse tab is gated `whb_settings:edit`, a warehouse permission seeded in `V501000`, checked **in addition to** the platform's `admin_settings:edit`."*
- **Irreversibility.** **Reversible.** A seed row's value is editable and the tab is frontend-only.
- **Relationship to earlier rounds.** **New.** `Z-001` owns the *inertness* of one key against its
  ladder; this is the surface all seven sit on. `RA-007` owns the integration/device permission
  namespace; `RA-003` owns the role bundles. Nothing asked which screen edits a warehouse setting.

---

### `RE-004` · Over- and short-receipt tolerance is a v1·P1 two-level ladder with no column at either level, and the one column that exists is at a third grain nobody named — **MAJOR**

- **What is missing or wrong.** `FR-130` (v1·P1) reads: *"**Over- and short-receipt** are governed by a
  tolerance **on the item and a warehouse default**"* (`:295`). Two scenarios spend that requirement:

  - `WH-SC-066` (v1·P1) — *"item over-receipt tolerance 5%, **warehouse default 2%** … **the item
    tolerance (5%) wins over the warehouse default**"* (`SCENARIO-CATALOGUE.md:242`).
  - `WH-SC-067` (v1·P1) — the refusal message quotes the resolved value to two decimals:
    *"received 560 exceeds ordered 500 by 12.00%, over which the tolerance is 5.00%"* (`:243`).

  **Neither column exists.** `whb_items`' column list (`DATA-MODEL.md:527`) has no tolerance;
  `whb_warehouses`' (`:450`) has none; `whb_item_site_settings`' (`:535`) has none. The single
  occurrence of the concept in the schema is `wh_purchase_orders.over_receipt_tolerance_pct`
  (`DATA-MODEL.md:965`) — **on the PO header**, a grain `FR-130` never mentions and `WH-SC-066` never
  uses. `grep -rn "over_receipt_tolerance_pct" docs/ issues/ | grep -v reviews` → **2 hits**: that
  column list, and the precision table at `:2068`.

  So this is a **sixth** most-specific-first ladder, and `Z-001`'s table enumerates five. It is also
  the only one of the six whose resolution order is written into a scenario's *expected result*, which
  makes it the one an implementer is most likely to hard-code and least likely to be caught doing.

  `COMPETITOR-BENCHMARK.md:238` compounds it: *"Over-receipt / short-receipt tolerance, per item and
  supplier | … | **v1.1** (`T-036`)"*. The benchmark defers to v1.1 the grain that two v1·P1 scenarios
  require, and no document reconciles the two placements.

- **Why it matters.** `WH-SC-066` and `WH-SC-067` are v1·P1 and `DECISIONS.md` §5 makes scenarios the
  phase exit criteria, so P1 cannot be signed off as written. Operationally it lands on the goods-inward
  desk on day one: with only a PO-header column, the tolerance must be typed on every purchase order by
  whoever raises it, which means it is either blank (every over-receipt refused, and `FR-138`'s
  reconciliation queue fills with cases that are not exceptions) or copied wrong. And the requirement's
  own justification — *"without it, PO lines accumulate forever and the open-PO report is meaningless
  within a quarter, which then breaks reorder"* — is a slow failure that surfaces one quarter after
  go-live.
- **Negative evidence.**
  - `grep -rn "tolerance" docs/DATA-MODEL.md | grep -i "whb_items\|whb_warehouses\|item_site"` → **0**.
  - `grep -rn -i "short.receipt tolerance\|under_receipt" docs/ issues/ | grep -v reviews` → **0** — `FR-130` says *"over- and short-receipt"* and no column, at any grain, expresses the short side.
  - `p1-13.md:122` — the acceptance criterion *"An over-receipt beyond tolerance sets `match_status = QTY_OVER` and is gated"* names no source for the number.
- **Where it belongs.** `warehouse-base` (the columns) + `warehouse` (the resolver) · v1 · **P1**.
- **Disposition.** *Fold into tasks `P1-03` and `P1-13`.*
  - `P1-03` — add: *"`whb_items` gains `over_receipt_tolerance_pct` and `short_receipt_tolerance_pct` (`DECIMAL(9,6)`, nullable = inherit), and `whb_warehouses` gains the same pair as the site default. Resolution is most-specific-first — PO line → PO header → item → warehouse → `BLOCK` — and it is the **sixth** ladder, so it is stated in `DATA-MODEL.md` §2.1 alongside the other five (`Z-001`)."*
  - `P1-13` — add: *"the receipt service resolves the tolerance through the ladder and the `422` message quotes **which level supplied the number**, because `WH-SC-066` and `WH-SC-067` differ only in that. `COMPETITOR-BENCHMARK.md:238`'s v1.1 placement is corrected to v1; the **per-supplier** grain stays v1.1 and is the row `whb_item_supplier_sources` will carry."*
- **Irreversibility.** **Reversible** — nullable columns on `V500015`/`V500012`, both after the tables
  exist and neither sealed by `L-2`.
- **Relationship to earlier rounds.** **New.** `Z-001` enumerates five ladders and this is not among
  them; `T-036` is dispositioned COVERED against `FR-130`, which is the requirement whose columns are
  missing.

---

### `RE-005` · Thirteen of the fourteen registries are told to ship "+ seed" and are given no values to seed; the only enumerated lists live in `IRREVERSIBLE.md` §5, which no task cites, and they contradict their own requirements in five places — **MAJOR**

- **What is missing or wrong.** `D-10` makes every extensible vocabulary a catalogue table with no
  `CHECK`, and `IRR-27`–`IRR-33` make seven of them `PNR-1`. The tables are therefore only as good as
  their seed rows, and the seed rows are specified twice, incompletely, in a document that is not about
  seeds.

  **What the task files — the documents a migration author reads — actually say:**

  | Registry | Task · migration | Seed values enumerated there? |
  |---|---|---|
  | `whb_movement_types` | `p0-04.md:58` · `V500003` | partial — *"the fourteen types"*, 4 named (**`X-004`**) |
  | `whb_document_types` | `p0-04.md:53` · `V500002` | no — *"+ seed"* |
  | `whb_source_systems` | `p0-04.md:53` · `V500002` | partial — `ACCESSORIES` only |
  | `whb_reason_codes` | `p0-04.md:63` · `V500004` | no — *"the seed of the **eleven contexts**"*, contexts unnamed |
  | `whb_stock_statuses` | `p0-05.md:29` · `V500005` | **no, and the task does not even say "+ seed"** |
  | `whb_condition_codes` | `p0-05.md:32` · `V500005` | no |
  | `whb_location_types` | `p0-05.md:34` · `V500006` | no — *"including every virtual and transit type"* |
  | `whb_item_types` | `p0-05.md:38` · `V500008` | partial — 4 of 12 |
  | `whb_task_types` | `p0-05.md:41` · `V500010` | no |
  | `whb_dispositions` | `p0-05.md:42-43` · `V500010` | no |
  | `whb_attribute_keys` | `p0-05.md:44` · `V500010` | no |
  | `whb_owner_types` | `p0-06.md:39-40` · `V500007` | **yes — all six** |
  | `whb_uom_classes` + `whb_uoms` | `p1-02.md:27` · `V500009` | no — *"+ seed"*, and no `unece_rec20_code`/`gst_uqc_code` values, which `FR-056` and the `WH-SC-261` acceptance both require |
  | `whb_counterparty_roles` | `p1-08.md:27` · `V500011` | no — *"+ seed"* |

  **One of fourteen.** The values do exist — in `IRREVERSIBLE.md` §5's *"v1 seed"* column
  (`:661-675`) and §4.5's location-type line (`:555-558`) — but `IRREVERSIBLE.md` is a document about
  what cannot be changed later, no task file cites it as the seed authority
  (`grep -n IRREVERSIBLE issues/p0-04.md issues/p0-05.md` → **0**), and where it does enumerate, it
  disagrees with the requirement that owns the vocabulary:

  | # | Registry | `IRREVERSIBLE.md` §5 seed | The consumer | Missing from the seed |
  |---|---|---|---|---|
  | 1 | Item type | `:672` — 10 codes incl. a single `KIT` | `FR-049` (`:184`) — 12 codes | **`KIT_STOCKED`**, **`KIT_PHANTOM`** (the seed has an undifferentiated `KIT`), **`ASSET`** |
  | 2 | Owner type | `:671` — 6 codes | `FR-108` (`:263`) — 6 codes incl. `TRANSIT` | **`TRANSIT`** |
  | 3 | UoM | `:669` — `EA` `BOX` `CASE` `PALLET` `KG` `L` `M` `CFT` | the scenario item fixtures (`SCENARIO-CATALOGUE.md:133-137`) | **`BAG`** (`WSH-0031`), **`CARTON`** (`VAC-2210`) |
  | 4 | Stock status | `:666` — 8 codes | `p2-12.md:12` posts to a **`PENDING_RESOLUTION`** stock status (v1·P2); `FR-028` uses the same word for the blocked-move disposition | **`PENDING_RESOLUTION`** — and no migration in the set inserts it |
  | 5 | Location type | `:555-558` — 16 codes | `FR-084`'s ten virtual locations, each needing a type (`location_type_code` is an FK, `DATA-MODEL.md:451`) | a type for **`OPENING_BALANCE`**, **`COUNT_VARIANCE`**, **`CONSUMED`** |

- **Why it matters.** Every one of these is a `NOT NULL` foreign key from the ledger
  (`whb_stock_movement_lines.stock_status_code` — *"`NOT NULL` and FKs to `whb_stock_statuses(code)`"*,
  `p0-05.md:8`), so a consumer reaching for a code the seed does not contain does not degrade — it
  raises a foreign-key violation in the middle of a receipt. The failure is silent in review and loud in
  production, and it is exactly the failure `D-10` exists to prevent: the openness of the catalogue is
  worth nothing if the row is not there, and `IRR-31`'s promise that *"adding a vocabulary value is a
  seed `INSERT`"* only holds once somebody notices. `FR-056`'s two UoM columns are the sharpest case —
  they exist precisely so that *"every compliance payload and every EDI mapping"* is not hand-mapped,
  and no document supplies a single UNECE or UQC value for the eight seeded UoMs.
- **Negative evidence.**
  - `grep -rn "IRREVERSIBLE" issues/p0-04.md issues/p0-05.md issues/p1-02.md issues/p1-08.md` → **0**.
  - `grep -c "near_expiry\|unece_rec20_code = \|gst_uqc_code = " docs/DATA-MODEL.md` → **0** — no seed values for either UoM column anywhere.
  - `grep -rn "PENDING_RESOLUTION" docs/ issues/ | grep -v reviews` → **3 hits** (`FR-028`, `p2-01.md:57`, `p2-12.md:12`), none of them a seed.
  - `grep -rnoE '`(BAG|CARTON)`' docs/*.md issues/*.md` → **2 hits**, both scenario fixtures.
- **Where it belongs.** `warehouse-base` · v1 · **P0**/**P1** — `V500002`–`V500011`, all before
  `PNR-1`.
- **Disposition.** *Fold into tasks `P0-04`, `P0-05`, `P0-06`, `P1-02` and `P1-08`, plus one
  amendment to `DATA-MODEL.md` §7.2.*
  - Each task gains: *"the seed value list for this registry is `IRREVERSIBLE.md` §5's **v1 seed** column, cited by row number, and it is reproduced in this task's Scope. A code that appears in a requirement, a scenario fixture or another task and not in the seed is a merge blocker — the same rule `FR-165` applies to threshold columns."*
  - `P0-05` additionally: *"`V500005` **seeds** `whb_stock_statuses` — the eight of §5 row 4 **plus `PENDING_RESOLUTION`** (`is_on_hand = true`, `is_allocatable = false`, `is_shippable = false`, `requires_reason_to_leave = true`), which `P2-12` and `FR-028` both consume; `V500006`'s location-type seed gains `OPENING_BALANCE`, `COUNT_VARIANCE` and `CONSUMED`; `V500008`'s item-type seed replaces `KIT` with `KIT_STOCKED` and `KIT_PHANTOM` and adds `ASSET`, per `FR-049`."*
  - `P0-06`: add `TRANSIT` to the owner-type seed, per `FR-108`.
  - `P1-02`: *"the UoM seed is `EA` `BOX` `CASE` `PALLET` `BAG` `CARTON` `KG` `L` `M` `CFT`, **each row carrying its `unece_rec20_code` and `gst_uqc_code` literal in the migration** — the values are the deliverable, not the columns."*
  - `DATA-MODEL.md` §7.2 gains a *"seed authority"* column pointing each registry row at its `IRREVERSIBLE.md` §5 row, which also closes `X-004`'s referral.
- **Irreversibility.** **Reversible as inserts**, but the *absence* is not: seven of the thirteen are
  `PNR-1` and their `code` values are what ledger rows carry, so a code seeded wrong and used is a code
  that cannot be renamed under `L-2`.
- **Relationship to earlier rounds.** **New as the general case and for divergences 1–5.**
  `X-004` owns the **movement-type** row and only that row, and is deliberately excluded from the
  divergence table; R11 §4 refused a second movement-type finding for the same reason and noted
  *"it does mean `X-004` is bigger than it reads"* — this finding is what it is bigger by.
  `Z-005` owns catalogue *retirement*, the opposite end of the same life.

---

### `RE-006` · Twelve deferrals across eight files to an "install guide" that does not exist, has no owning task, and has no acceptance criterion — and it is where four undiscoverable install steps are being sent — **MAJOR**

- **What is missing or wrong.** Eight files defer a fact to *"the install guide"*:

  ```bash
  grep -rn -i "install guide" docs/*.md issues/*.md | wc -l    # → 12 mentions
  grep -rl -i "install guide" docs/*.md issues/*.md | wc -l    # → 8 files
  ```

  What is being deferred to it is not documentation polish — it is four things a customer cannot
  discover and one that stops a demo:

  | Deferred fact | Deferred at |
  |---|---|
  | `FLYWAY_OUT_OF_ORDER=true` is **required** for a warehouse-first install; without it the install is *"refused … it is not discoverable"* | `p0-01.md:155` · `p0-16.md:117,140` · `IMPLEMENTATION-PLAN.md:1100` · `MODULE-INTEGRATION.md:1055` |
  | The platform has **no restore path** (`PP-1`, `grep -c -i restore DatabaseBackupService.java` → 0) — *"say 'unknown' in the install guide and the customer decides"* | `p0-16.md:77,138` |
  | The position-snapshot job's switch-on date, *"recorded in the install guide as the day the ageing reports begin"* | `p0-03.md:161` |
  | Stock **periods must be seeded before the first post** — *"the install guide must say so"* | `p0-07.md:79-81` (**`RE-001`**) |
  | The India pack's `out-of-order: false` rule; the port's v3 auth limit; the e-way-bill precondition | `p2in-01.md:144` · `p0-08.md:175` · `p2in-04.md:176` |

  **No task produces the document.** `grep -rn -i "install guide" issues/*.md` returns two acceptance
  criteria, both in `P0-16`, and both are about what the guide *carries* rather than who writes it;
  `P0-16`'s header is *"Migrations **none** · Screens **none**"* and its Scope contains no document
  deliverable. `IMPLEMENTATION-PLAN.md` §2 has no documentation task. `docs/` has no install or
  runbook file (`ls docs/*.md | wc -l` → 18, none of them).

- **Why it matters.** `D-7` promises a **standalone-capable** product and `DECISIONS.md` §5's v1 exit
  criterion is a fresh install with no vertical and no accounting. That install currently requires the
  installer to know an undocumented environment variable, to seed a table by hand, and to record a date
  that four v1·P2 reports silently depend on. Each of those was correctly identified by the task that
  found it and then written to a forwarding address. The set's own rule — a threshold with no job is a
  defect at merge (`FR-165`) — has an exact analogue here: **an instruction with no document is a
  defect at merge.**
- **Negative evidence.** As above; plus `grep -rn -i "runbook" docs/ issues/ | grep -v reviews` →
  hits only for `FR-413`'s freeze-count-load-verify **go-live** runbook, which is a screen (`WS-151`)
  and a different artefact from a technical install guide.
- **Where it belongs.** `warehouse-base` · v1 · **P0**.
- **Disposition.** *Fold into task `P0-16`* (which already owns the non-functional facts and both
  existing acceptance criteria). The line to add: *"**`P0-16` produces `docs/INSTALL.md`** as a task
  deliverable, and its acceptance is that `grep -rn -i 'install guide' docs/ issues/` resolves to a
  section heading in it for every deferral. Minimum contents: module enable flags and their order;
  `FLYWAY_OUT_OF_ORDER=true` for a warehouse-first install; the platform restore gap stated as
  'unknown', with the customer's decision recorded; the day the snapshot job is switched on and which
  reports begin then; the ordered day-1 master load (`Z-009`) with its screens; the period-generation
  step (`RE-001`); the settings whose defaults must be reviewed before go-live (`RE-003`); and the port's
  authentication limit until v3."* This is a `docs/` file, not a `docs/` design document, so it does not
  enter `check-design-set.py`'s citation graph.
- **Irreversibility.** **Reversible** — but every month it is not written, another task defers another
  fact to it, and the four above became twelve mentions over one authoring wave.
- **Relationship to earlier rounds.** **New.** `Z-009` owns the **master load order** — the data
  sequence, folded into `P2-19`'s checklist seed. This is the *technical* install: flags, seeds,
  switch-on dates and known platform gaps, none of which is a checklist item on a go-live screen.
  `C-046` is the underlying Flyway fact and is correctly recorded; what is missing is its destination.

---

### `RE-007` · `FR-165` is enforced in one direction only: three v1 alert horizons have a job, a recipient and a report, and no column, key or field to hold the number — **MINOR**

- **What is missing or wrong.** `FR-165` is one of the best rules in the set: *"**A threshold column
  with no scheduled job that reads it is a defect at the moment it is merged.**"* (`:335`), and
  `P0-13` turns it into a register with an owning task per row (`p0-13.md:55-63`). The rule has no
  inverse, and three v1 obligations fall through it:

  | Obligation | Job exists | Threshold lives |
  |---|---|---|
  | Notify at `expiry − near_expiry_days` (`FR-160`, v1·P2) | yes — `P2-05`, registered in `P1-20` | **nowhere.** `grep -c near_expiry docs/DATA-MODEL.md` → **0**; `docs/BUILD-SPEC-SCREENS.md` → **0**. `p2-05.md:76` calls it *"a `near_expiry_days` column"*; the column is on no table |
  | Movements pending approval beyond **N hours** (`p0-13.md:27-29`, v1·P0) | yes — the register row is added | **nowhere** — N is not a column, not an `admin_settings` key, not a field |
  | Unresolved `wh_blocked_movements` beyond **N minutes** (`p0-13.md:27-29`, v1·P0) | yes | **nowhere** — `WS-097` computes `ageMinutes`, which is the age, not the horizon |

  `SCENARIO-CATALOGUE.md:326` hard-codes the first one as a fixture — *"`VAC-2210` with
  `shelf_life_days = 540` … **near-expiry 45 days**"* — without saying where the 45 is stored, which is
  precisely how a fixture becomes a constant in the service.

- **Why it matters.** A notification threshold that is not data is a redeploy every time a customer
  asks for 30 days instead of 45, and pharmaceutical and food customers ask on the first call —
  `WH-SC-130` is the cold-chain scenario. The scope question is live too and nobody has taken it: 45
  days is right for vaccines and absurd for engine oil, so the horizon almost certainly belongs on the
  item (with a site override), not on the install — and that is a column decision, taken now or taken
  after the job ships reading a constant.
- **Negative evidence.** The four `near_expiry_days` mentions are `FR-160` and three lines of
  `p2-05.md`; zero in `DATA-MODEL.md`, `BUILD-SPEC-SCREENS.md` and every other task file.
  `grep -rn "pending_approval_hours\|blocked_move_.*minutes\|alert_horizon" docs/ issues/` → **0**.
- **Where it belongs.** `warehouse-base` · v1 · **P1** (the columns) and **P0** (the register rule).
- **Disposition.** *Fold into tasks `P0-13` and `P1-03`.*
  - `P0-13` — add: *"`FR-165`'s register is **bidirectional**: a threshold column with no job is a defect, **and a job whose horizon is not a column, an `admin_settings` key or a screen field is the same defect**. The register's table gains a **Threshold home** column and no row may leave it blank. The two rows this task adds take `admin_settings` keys `warehouse.approval.pending_alert_hours` and `warehouse.blocked_movement.alert_minutes`, seeded in `V501100` with defaults (`RE-003`)."*
  - `P1-03` — add: *"`whb_items.near_expiry_days` and `whb_item_site_settings.near_expiry_days` (nullable = inherit), resolved item × site → item → the `admin_settings` install default, so `FR-160`'s notification horizon is data. `WS-023` and `WS-027` carry the field; `WH-SC-130`'s 45 becomes a fixture value rather than a constant."*
- **Irreversibility.** **Reversible** — nullable columns after `V500015`/`V500050`.
- **Relationship to earlier rounds.** **New.** `RA-008` owns `FR-145`'s adjustment approval threshold
  as a single missing value; this is the register rule that would have caught it and the three other
  rows it also misses. `RB-008` owns the `ageOverDays`/`inTransitOverDays` **filter option lists**,
  which are a user-chosen report parameter and not an alert horizon; `FR-149` is therefore excluded
  here and refused below.

---

### `RE-008` · Disabling a module leaves its menus, permissions and settings live, and `MODULE-INTEGRATION.md` §15 says nothing reads them — **MINOR**

- **What is missing or wrong.** §15's disable row reads: *"set `ENABLE_WAREHOUSE*=false`, rebuild the
  image | Free and instant. `@ConditionalOnExpression` stops the beans … **The tables and their rows
  stay. Nothing reads them**"* (`MODULE-INTEGRATION.md:1068`). That is true of `whb_*` tables and false
  of three platform tables the warehouse migrations write to and the platform reads unconditionally:

  - **`menus`** — seeded by `V501010` and `V511010` (`p0-15.md:35-37`, `p1-20.md:18`). The table has no
    module column and no enablement flag; `is_active BOOLEAN NOT NULL DEFAULT TRUE`
    (`platform/backend/src/main/resources/db/migration/V16__Add_menu_management_system.sql:7-33`) is what
    controls visibility (`MenuService.java:1006`), and nothing flips it. The sidebar therefore renders
    every warehouse menu in an install where the module is disabled, and the routes are not in the
    frontend bundle because the module's `src/` tree was not merged (`Dockerfile.frontend:80-177`,
    R1 `C-012`).
  - **`permissions` / `role_permissions`** — `V501000` grants ADMIN and AUDITOR every warehouse
    permission. Disabling the module does not revoke them, so the permission matrix screen shows verbs
    for a product that is not running.
  - **`admin_settings`** category `WAREHOUSE` — `V501100`/`V511200`. Once `RE-003`'s tab exists it will
    render for a disabled module too, because the tab's own gate would be a permission that is still
    granted.

  Nothing in the set states the intended behaviour for any of the three, and §15 is the only place the
  question is asked.

- **Why it matters.** It is a support-call defect, not a data defect: a user clicks *Warehouse →
  Movements* and gets a blank page or a 404 that nobody can explain, in an install that was deliberately
  configured without the module. `warehouse-3pl` and `warehouse-india` make it likely rather than
  theoretical — both are v2, both seed their own menus (`W3-20`, `WIN-30`), and most installs will never
  enable them.
- **Negative evidence.**
  - `grep -rn -i "menu" docs/MODULE-INTEGRATION.md | grep -iE "disab|hidden|403|404"` → **0**.
  - `grep -n "module" platform/backend/src/main/resources/db/migration/V16__Add_menu_management_system.sql` → **0** — the menu row cannot name the module that owns it.
- **Where it belongs.** `warehouse-base` · v1 · **P0** — a documentation and seed-convention change, not
  a platform schema change.
- **Disposition.** *Fold into task `P0-15`.* The line to add: *"the menu rows this migration seeds for
  modules that are not `warehouse-base`/`warehouse` are seeded `is_active = false` and enabled by the
  module's own migration when it runs — the pattern the Doc OCR AI tab uses at the frontend
  (`admin-settings/page.tsx:145-152`), applied at the data layer. `MODULE-INTEGRATION.md` §15's disable
  row is corrected: **the `whb_*` tables are inert; `menus`, `permissions` and `admin_settings` are
  not**, and disabling a module after it has been enabled leaves a visible menu that must be
  deactivated on the platform menu screen."*
- **Irreversibility.** **Reversible.**
- **Relationship to earlier rounds.** **New.** `RA-003` and `Z-010` own role *bundles*; `C-012` owns
  the frontend filename merge. Nobody asked what a disabled module leaves behind.

---

## §3 · What I checked and found sound

The configuration surface is better than these eight findings suggest, and the list below is
deliberately long because a reviewer who reports only gaps misrepresents the document.

| What I went looking for | Where it is covered |
|---|---|
| Every extensible vocabulary a table with no `CHECK`, proved by a build-time test | `D-10` · `I-18` · `WarehouseBaseCouplingTest` enumerating the thirteen `table.column` pairs (`IRREVERSIBLE.md:686-690`) |
| A registry's `code` immutable after create and read-only on the edit modal | `BUILD-SPEC-SCREENS.md:545` · `p0-04.md` row actions |
| A newly registered value rendering everywhere with no code change, i18n falling back to the row's `name` | `FR-381`/`FR-382` · `WH-SC-147` · `p1-19.md:95` |
| Catalogue seeds idempotent and safe on a Flyway retry | `FR-356` · `WH-SC-292` · `p2-25.md:92` |
| The mobile zod-enum trap named where it bites — a value the backend opened and `common.schemas.ts` closed | `p0-04.md` mobile note, verbatim |
| Reorder policy at **item × site**, with item-level values as defaults that seed the row | `FR-053` · `whb_item_site_settings` (`DATA-MODEL.md:535`) |
| Valuation policy **effective-dated**, not switched in place | `whb_valuation_policies.effective_from`/`_to` · `OD-6` |
| GL posting rules with a computed `specificity` and a **Test resolution** modal | `FR-246` · `WS-051` — the exemplar `Z-001` asks the others to copy, and it is genuinely good |
| Putaway rules evaluated in an explicit `uk(warehouse_id, sequence)` order | `FR-135` · `wh_putaway_rules` |
| Counting as a **policy object** rather than a screen — frequency, cron, blind flag, recount and approval thresholds by percent **and** by value, `freeze_locations`, `max_tasks_per_run` | `wh_count_programs` (`DATA-MODEL.md:1005`) · `p2-04.md:43-44` |
| GSTIN on the **branch**, not duplicated onto the warehouse — one branch, one GSTIN | `FR-079` · `C-016`/`C-030` · `p1-05.md:54-56` |
| `owner_id` on the **line**, not the header, with a per-movement-type `balance_rule` | `FR-042` · `L-11` |
| Exactly one house owner seeded by the first migration, and **no single-owner mode** | `FR-108` · `FR-109` |
| Module enable flags as env + Maven property, with the adapter package a **sibling** so a component scan cannot load it | `D-1` · `MODULE-INTEGRATION.md:33-34,188,538,580-581` |
| Disable / remove-from-image / un-apply-a-migration answered separately, with the `FlywayConfiguration` duplicate-version hazard named | `MODULE-INTEGRATION.md` §15 — the best rollback section in either design set, and `RE-008` corrects one row of it, not its shape |
| The CHECK-widening migration explicitly **not** rolled back, quoting `V553`'s own superset rule | `MODULE-INTEGRATION.md` §15 row 5 |
| Grid configuration seeded with **both** `default_columns` and `default_filters` | `p0-15.md:38` · `p2in-01.md:62` — the trap CLAUDE.md names, applied |
| `filter_definitions`, never `grid_filter_definitions` | `p1-20.md` Traps, with the crash-loop consequence stated |
| Three locales seeded on every menu and translation file | `FR-431` · `p0-15.md:36` |
| `permission_dependencies` **inserted, never created**, and `dependent_permission_id` named correctly | `FR-402` · `p0-15.md:34` · `C-017` |
| The `logistics:*` namespace reserved in v1 so v2 does not retro-grant every role | `FR-346`/`FR-407` · `IRR-63` |
| Retention as a country-neutral policy table that `warehouse-india` seeds rather than owns | `whb_retention_policies` (`DATA-MODEL.md:854`) · `Z-006`'s fix, correctly landed |
| Precision fixed once and cited rather than restated, including the corrected `DECIMAL(9,6)` | `FR-030` · `OD-7` · `DATA-MODEL.md:2068` |
| The go-live batch as a first-class object with a status ladder, a dry run that persists nothing, per-row errors and a signed certificate | `P2-19` · `FR-411`–`FR-413` — `RE-001` is a sequencing bug inside a strong design, not a weakness of it |

**One thing I could not verify.** Whether `WS-015`'s and `WS-045`'s *Actions* cells are exhaustive or
list only the non-obvious verbs: the Department and Service Vehicle references both carry an **Add**
toolbar button, so a create path may be implied by the reference. `RE-001` is written so that it does
not depend on the answer — the seed, the job and the *"previous period exists"* guard are each
independently missing — but if the convention is *"Add is implied"* then `BUILD-SPEC-SCREENS.md` §0.2
should say so once, because two reviewers have now had to guess.

---

## §4 · Refused

| Candidate | Why not filed — the id that owns it |
|---|---|
| The `admin_settings` install default for negative stock is inert against a single `whb_item_site_settings` row | **`Z-001`**, second consequence, verbatim. `RE-003` covers the *surface* the key sits on and cites `Z-001` for the ladder |
| Three of five most-specific-first ladders inexpressible by their own tables | **`Z-001`**. `RE-004` adds a **sixth** ladder `Z-001`'s table does not enumerate, and says so |
| `reset_policy` YEARLY/MONTHLY unimplementable; nothing performs the reset | **`Z-002`** |
| No master load order is stated; the cut-over checklist collapses it into one tick | **`Z-009`**. §1.2 extends it with the *screen and actor* axis and does not restate the FK order |
| No operational role is seeded — storekeeper, picker, supervisor, stock controller, 3PL client | **`Z-010`**, and `RA-003` for the four-verb deny-list |
| No catalogue value can ever be retired; the deactivation gate is undefined | **`Z-005`** |
| `WHB-03`'s fourteen movement types are never enumerated | **`X-004`**, and R11 §4 refused it a second time. `RE-005` excludes the movement-type row from its divergence table for this reason |
| The value-offset virtual location has three names and `FR-084` seeds none of them | **`X-029`** / **`OD-13`**. `RE-002`'s table excludes that row |
| No `L-15`/`I-21` row for value conservation | **`X-030`** |
| The adjustment approval threshold by value and by quantity has no column | **`RA-008`**. `RE-007` files the *register rule* that would catch it, and the three other rows it misses |
| Warehouse-scoped user access has no table, screen or migration | **`RA-001`** — a day-1 setup step, but it is a permission model finding and `RA-001` states it completely |
| `ageOverDays` / `inTransitOverDays` / `bucketSetCode` selects have no option list | **`RB-008`**. `FR-149`'s *"beyond N days"* is a user-chosen report parameter, not a stored horizon, so it is excluded from `RE-007` |
| WS-220 and WS-221 carry two different `COMMON_FILTER_CONFIGS` scope names | **`RB-003`** |
| `whb_items.lifecycle_status` has four values in one authority and five elsewhere | **`RB-004`**. It is a status domain, not a seeded catalogue, so `RE-005` does not restate it |
| `whb_outbox_subscriptions` ships `endpoint_url` and `secret_ref` in v1 with no delivery contract | **`RD-002`**. `RE-003` cites only the `max_attempts` **precedence** question, which `RD-002` does not raise |
| No grid states an empty state, a loading state or a statistics tile set | **`RB-006`** |
| No screen names a uniqueness-validation endpoint | **`RB-007`** — including the registry `code` uniqueness a day-1 administrator hits first |
| The `V541000`/`V541100` India migration-block collision | `DESIGN-SET-DEFECTS.md` §6 row 1, already open with a deadline |
| A **settings audit trail** — who changed `negative_stock.default_mode`, when, from what | Deliberately not filed. `admin_settings` carries `updated_by`/`updated_at` (`V110:19-22`) and the platform owns the screen; a warehouse-specific settings audit would duplicate `whb_audit_events` for rows warehouse does not own. It belongs on the platform's backlog, not this set's |
| A **configuration export/import** for moving a tuned install to a second customer | Deliberately not filed. It is a consulting deliverable — the same judgement R12 §4 made when it refused a generic competitor import shape — and `P1-10`'s handler registry already covers per-entity loads |
| `whb_companies` has no seeded default company | Not filed as a defect: `WS-015` is a Department-shape screen with a create path and `company_id` has no chicken-and-egg guard, unlike the period. Named in §1.2 step 2 so the install-guide ordering picks it up |

---

## §5 · Counts

```bash
$ grep -c "^### \`RE-" docs/reviews/R20-configuration-and-day-one-setup.md
8
$ grep "^### \`RE-" docs/reviews/R20-configuration-and-day-one-setup.md | grep -c "BLOCKER"
2
$ grep "^### \`RE-" docs/reviews/R20-configuration-and-day-one-setup.md | grep -c "MAJOR"
4
$ grep "^### \`RE-" docs/reviews/R20-configuration-and-day-one-setup.md | grep -c "MINOR"
2
```

| Severity | Count | Findings |
|---|---|---|
| **BLOCKER** | 2 | `RE-001` `RE-002` |
| **MAJOR** | 4 | `RE-003` `RE-004` `RE-005` `RE-006` |
| **MINOR** | 2 | `RE-007` `RE-008` |
| **Total** | **8** | `RE-001`…`RE-008` |

**Disposition shape:** all eight fold into existing tasks — `P0-04`, `P0-05`, `P0-06`, `P0-07`,
`P0-13`, `P0-15`, `P0-16`, `P1-02`, `P1-03`, `P1-05`, `P1-08`, `P1-13`, `P1-20`, `P2-19`. **Zero** need
a new task. Three also need a document amendment: `FR-084` and `DATA-MODEL.md` §2.1 note 2 (`RE-002`),
`DATA-MODEL.md` §7.2 gaining a *seed authority* column (`RE-005`, which also closes `X-004`'s
outstanding referral), and `MODULE-INTEGRATION.md` §15's disable row (`RE-008`). One needs a decision
that is not yet an `OD-`: whether `near_expiry_days` is an item property or an install default
(`RE-007`) — recommended as item × site with an install fallback.

**Irreversibility.** All eight are reversible in schema terms. **Four must land before `PNR-1`
(`V500030`)** because they are the content of migrations that precede it: `RE-001` (`V500019`),
`RE-002` (`V500012`/`V500013`), `RE-005` (`V500002`–`V500011`) and the `whb_items` half of `RE-004`
(`V500015`). `RE-002` is the one that becomes genuinely irreversible if missed: a virtual-location
`code` is a stable key on ledger rows that `L-2` forbids rewriting.

**Where the set stands after this lens.** Every one of the eight is a *last-mile* defect — a value, a
row, a screen or a document, never a wrong decision. That is a good place for a design set to be, and
it is also the place where a set is most likely to ship the gap, because the decisions read as made and
the implementer discovers on a Monday that the number was never written down.
