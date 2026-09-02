TITLE: [Warehouse] EPIC: P6 — Optimisation, planning and the logistics seam
LABELS: epic,warehouse,phase-p6
---
Part of __MASTER__ · Modules `warehouse-base` · `warehouse` · `warehouse-3pl` · **`logistics` (new)** · Migrations — **four blocks, enumerated below** · Ships in **v3**

## Overview

**12 tasks, and one of them is a module.**

Ledger archiving as a transaction that writes an `OPENING_BALANCE` movement at the cut-off **before** it
moves a row, so the rebuild still reproduces; the **computed** best stocking level with phase-in and
phase-out; labour standards measured from a year of our own data and **not engineered**; the automation
and AS/RS event contract; supplier-scorecard evidence emitted rather than scored; the `party-base`
extraction trigger recorded rather than acted on; 3PL v3 — rate escalation, SLA credits, client
profitability; the operations dashboard on the platform widget framework; the documented accessories
absorption path and the dealer vehicle-inventory test; **and the `logistics` module itself.**

Four of the twelve produce **a written determination and no code** — `P6-06` (the `party-base` trigger),
`P6-09` (the vehicle test), `P6-11` (the accessories path), `P6-12` (the BOM refusal). That is not
padding: `D-12` says *"every capability found by any lens is placed in a version and carried in a task
file now; nothing is deferred to 'we'll look at it later'."* A refusal with a written re-entry path is a
decision. A silence is a gap someone rediscovers as a defect.

## The invariants this phase establishes

This phase **establishes no new `L-n`** — `P0` and `P1` did that. What it does is put existing
invariants under **new writers**, and a new writer is exactly how an invariant is lost. Each row names
the invariant, the new writer, and the specific way this phase could break it (`H-008`).

| # | Invariant | The new writer P6 introduces | How this phase breaks it if unwatched |
|---|---|---|---|
| **L-4** | **Positions are a cache.** A full rebuild reproduces every row **exactly** | `V510300`'s **computed stocking level** and `V510302`'s **dashboard**, plus `P6-03`'s labour rollup | this is the phase that adds derived numbers to `warehouse-base` and `warehouse`, and the question `L-4` forces on each of them is *"is this a cache or a fact?"* A cache must have a rebuild that reproduces it exactly and a drift check that proves it; a fact must be written by the ledger. A derived column with neither is the defect |
| **L-13** | **Three timestamps, never one** | `V500101`'s **automation event contract** and `P6-01`'s **archiving** | an event contract that emits one timestamp makes offline replay and degraded-mode catch-up unreconstructible for subscribers, permanently and for the past. The archive job partitions on **`occurred_at`**, and a row archived on `recorded_at` silently changes which period a rebuild can reach |
| **L-2** | **Append-only** | **archiving**, the first process allowed to remove ledger rows from the live table | archiving is not deletion. Rows move to an archive partition or store that a rebuild and a traceability query can still read for the full retention period; `P6-01` refuses to run where no retention policy resolves (`NO_RETENTION_POLICY`), and disposal is explicitly out of v3 scope |

## Exit criterion — as scenario ids

<!-- check-design-set: scenario-citations begin WH-SC-306 — the SCENARIO-CATALOGUE.md §5 rule 3 allocation marker — the next free scenario id, which by definition has no row yet. Named here so a parallel task does not silently take it twice; it is never a citation of a scenario that exists -->

`DECISIONS.md` §5's v3 sentence, made mechanical by `IMPLEMENTATION-PLAN.md` §1.8:

> The `logistics` module ships **trips, ePOD and freight settlement**, moves stock **only** through
> `POST /api/warehouse/movements`, and **`git log --oneline -- warehouse-base/` shows zero commits
> attributable to it** — plus `FR-336`'s **two deletion tests**: delete `logistics` and warehouse still
> works; delete `warehouse` and `logistics` degrades to a **stated, documented** mode rather than failing
> to start.

**`SCENARIO-CATALOGUE.md` contains zero `v3·P6` scenarios today** — computed:

```bash
awk -F'|' '/^\| \*\*WH-SC-/ {gsub(/ /,"",$9); print $9}' ../docs/SCENARIO-CATALOGUE.md | sort | uniq -c
# → 96 v1·P0 · 71 v1·P1 · 101 v1·P2 · 5 v1·P2-IN · 17 v1.1·P3 · 3 v2·P4 · 7 v2·P5 · (no P6 row)
```

**So this phase's exit criterion is prose and cannot be walked until its scenarios exist.** The catalogue
says so itself, in §4.2, for `FR-023`: *"Write it with the v3 task, not before."* Eight P6 tasks
therefore author their scenarios as their first act (`P6-01`–`P6-05`, `P6-07`, `P6-08`, `P6-10`), and
**`P6-08` must author `FR-336`'s two deletion tests, because they *are* the exit criterion.**
Four tasks author none, by design, and say why (`P6-06`, `P6-09`, `P6-11`, `P6-12`) — permitted by
§5 rule 1: *"a task with no scenarios is either infrastructure with an architecture test instead, or it
is under-specified — and the reviewer says which."*

> **⚠ ID COLLISION.** New ids continue from **`WH-SC-306`** (§5 rule 3), and P5 is claiming from the same
> counter concurrently. **Claim ids by merging them into `SCENARIO-CATALOGUE.md` in one commit BEFORE
> writing code.** The catalogue file is the allocation register; nothing else is.

Scenarios this phase inherits and re-walks: **`WH-SC-236`** (`P6-07` — an escalation generates a new
version for review and **never mutates an active card**; *"a dispute three months later re-rates to the
same number"*).

<!-- check-design-set: scenario-citations end -->

## Migration blocks — re-derived from the task headers, not transcribed

```bash
# from issues/ — the header line of every P6 task file
grep -h '^Part of' p6-*.md | sed 's/.*Migrations //; s/ · Screens.*//'
grep -h '^Part of' p6-*.md | grep -oE 'V5[0-9]{5}' | sort -u
# → V500100 V500101 V510300 V510301 V510302 V524000 V524999 V530100 V530110 V530111
```

**Round-2 correction (`H-006`).** The output above was **re-run on 2026-09-02**, and it did not match
what this block previously showed: the transcribed line read `V524099`, a number no task header has
ever contained. `V524000` and `V524999` appear in the second grep only because they sit inside
`p6-08.md:4`'s **refusal sentence** — *"Migrations **none in this design set's bands**"* — which the
`grep -oE` cannot tell apart from a claim. Read the first command's output, which prints the field
verbatim and shows `none in this design set's bands` for `P6-08`, before reading the second's.

| Band | Module | Numbers | Owner | Where the range comes from |
|---|---|---|---|---|
| `V500100`–`V500101` | `warehouse-base` | archiving · the automation event contract | `P6-01` · `P6-04` | inside `DATA-MODEL.md` §7.2's declared **`V500064`–`V500199` post-v1 base DDL** gap. **Neither table has a §7.2 row yet — each task adds its own in the same PR** |
| `V510300`–`V510302` | `warehouse` | computed stocking level · labour measurement rollup · the dashboard | `P6-02` · `P6-03` · `P6-10` | §7.3 allocates **no v3 block** for `warehouse`; `IMPLEMENTATION-PLAN.md` §2.9 **divergence 4** carves the top of the `V510215`–`V510999` correction reserve, leaving `V510215`–`V510299` for corrections as intended |
| **none** | **`logistics`** | the module | `P6-08` | **`P6-08` writes no migration in any band of this design set**, which is what its header states. `V524000`–`V524999` is a **reservation** (`FR-346`) held open for the `logistics` design set alongside the `log_` prefix and the `logistics:*` permission namespace; `D-2` gives this set a band for warehouse's five modules and for no other, so numbering inside it here would be this set writing another module's migrations. The only v1 work is the permission seed, and it lives in `WHB-71` (`V501000`). The withdrawn `V524000`–`V524099` claim is recorded in `IMPLEMENTATION-PLAN.md` §11 |
| `V530100` · `V530110`–`V530111` | `warehouse-3pl` | client profitability · escalation · SLA penalty | `P6-07` | `V530100` is `W3-14` as allocated; `V530110`–`V530111` are §2.9 **divergence 5**, carved from §7.5's *"reserved for corrections"* because §7.5 allocates one v3 table and v3 needs three |

**Exactly one task owns each number**, and a task needing a second file takes the next number **inside its
own block** — never the next globally free one, and never a number that "looks plausible".

## Build order

`IMPLEMENTATION-PLAN.md` §3.8 graphs this phase; this is the same information as a schedule. **`A → B`
means A precedes B.**

- **First task: `P6-01` (archiving).** It is the only P6 task that touches `warehouse-base` DDL
  (`V500100`), and it is where `L-2`, `L-4` and `L-13` are re-tested against a table whose rows have
  moved. **It refuses to run where no retention policy resolves** (`NO_RETENTION_POLICY`), which makes
  `P4-09 → P6-01` the only hard edge from v2 into v3.
- **Long pole: `P6-08` (the `logistics` module).** It is a whole module, not a feature, and it writes
  **no migration in any band of this design set** — the seam is `P6-04`'s published task-event
  contract, so `P6-04 → P6-08` binds.
- **Parallel streams**, once `P6-01` lands: `{P6-02, P6-03, P6-05}` the derived numbers, all three
  feeding `{P6-10}` the dashboard · `{P6-07}` 3PL v3, after `P5-07` · `{P6-04 → P6-08}` automation and
  logistics.
- **`P6-06`, `P6-09`, `P6-11` and `P6-12` write records and decisions, not code.** They have no
  successors by design, they can run at any point in the phase, and **shipping them is still shipping
  them** — an unwritten decision is the failure they exist to prevent.

## Tasks

__TASKS__

**Sizing** (`IMPLEMENTATION-PLAN.md` §9.3): 1 XL · 3 L · 4 M · 4 S. **Staffing** (§9.4): 2–3 backend,
2 frontend, 1 QA — *"`P6-08` is a module and will be re-planned as one."*
§9.5 assumption 7 and §11 item 3 both say it: **`P6-08` is out of scale with every other row here. It is
carried as one task because `D-12` requires every capability to be placed now; it will not stay one
task.** §9.6: it is **not sized**. Re-plan it when v3 is planned.

## Traps this phase must not get wrong

- **Every verb in a §4 Actions cell is a `@PreAuthorize`, not an `:edit`** (`H-001`). The strings are
  rows in `BUILD-SPEC-SCREENS.md` §10.2 — twenty-five were added in round 2 and are seeded by `P5-01`
  (`V531000`–`V531099`) — and **a screen whose verbs §3/§7 describes only in prose must enumerate them
  in the task before the controller is written.** The failure this prevents is already visible in the
  document: `wh3_billing_runs:approve` existed while `:cancel` did not, so anyone who could edit a
  draft run could cancel an invoiced one.

- **⚠ THE FAILURE P6 EXISTS NOT TO REPEAT.** The previous attempt at the warehouse↔supply-chain seam made
  warehouse **structurally FK-dependent** on a supply-chain module: **84 FK references into `scc_*`**,
  several of them **to tables that never existed** (`scc_items` 4 refs, `scc_drivers`, `scc_alert_rules`,
  `scc_alert_history`); a designated owner entity (`SccCompany`) that was **never built**, leaving an
  orphan `scc_company_id` column with no FK; ~50 `Scc*` interfaces across ~60 files living *inside*
  warehouse-core with the untangling deferred; and a bulk-import feature whose table and **menu** sat in
  one module while its controller and **page** sat in the other, so *"core deployed alone renders a menu
  entry that 404s"* — which only worked because the Docker frontend `cp`-merges both trees.
  **`G-025`: 84 FKs is not a seam. Zero FKs from `warehouse-base` into any supply-chain, logistics or
  vertical table, enforced by `WarehouseBaseCouplingTest` assertion 3.**
  The ghost is still in the tree: `grep -rl "scc_"` over `classic` returns exactly **two files, both
  comments** — `platform/…/V663:18` and `platform/…/util/CountryStateRegistry.java:32`, the latter a
  Javadoc line still asserting the platform stores states in `scc_warehouses.state`, **a reference to a
  table that does not exist here**.
- **⚠ What would falsify "zero commits to `warehouse-base`"** — six things, all checked in `P6-08`'s PR:
  a commit touching `warehouse-base/**`; a new column on any `whb_` table; a new vocabulary value added by
  `ALTER` rather than a seed `INSERT` from logistics' own migration; a `REFERENCES … log_` in a migration
  below `V524000`; an `import ai.logistics` under base or app; **or a base API change made "so logistics
  can call it"**, including a widened response field. **Items 2 and 3 are the ones that arrive
  innocently.**
- **⚠ And the caveat, stated inside the contract because a false invariant gets ignored, taking the true
  ones with it** (`D-10` corollary, `G-047`, `PC-74`): **the ratchet can only ever be "zero commits to
  `warehouse-base`". It can never be "zero commits to `platform`."** `COMMON_FILTER_CONFIGS` is a
  TypeScript `const` at `platform/frontend/src/utils/filterUtils.ts:346` with 213 scopes and a missing
  field is **silently dropped**; `CacheConfiguration.java` has 234 names and warns at `:375-376` that an
  unregistered name throws on the **first call, not at startup**. Every logistics grid edits both.
- **⚠ *"Delivery is not a movement"* is true for a customer and FALSE for our own branch** (`G-019`,
  `FR-342`). *"An implementer who reads only 'delivery is not a movement' builds inter-branch transfers
  that depart and never arrive."*
- **⚠ `log_trips` + `log_gps_pings` would be the third GPS trip model in this monorepo** (`G-020`,
  `FR-347`): `field-service/…/V80007:13-80` already has `job_trips` + `job_track_points`;
  `services/…/V40197:15-60` has a driver-assigned doorstep ladder; `automotive`'s boom-barrier webhook and
  `dealer`'s `pdi_vehicle_movements` are the other two. **The pre-flight enumeration is mandatory and
  merges before any `log_` migration.**
- **`logistics` gets no adapter and posts directly** (`FR-366`, `G-048`) — *"an adapter between two of our
  own modules is a layer with no translation in it."* Recorded so a later reviewer does not "discover"
  the missing adapter.
- **The ledger is sealed against `UPDATE` from `V500030`** — so `P6-01`'s archive **moves rows and never
  marks them**; an `is_archived` flag would need an `UPDATE` and is refused.
- **⚠ The partition key is unresolved.** `FR-022` and `DATA-MODEL.md` `WHB-30` say `occurred_at`;
  `PLATFORM-DEPENDENCIES.md` `PD-D5` says `posting_date`; **nothing resolves them**
  (`IMPLEMENTATION-PLAN.md` §2.10, §7, §11 item 1). It blocks `P0-02` and it reaches `P6-01`, whose
  cut-off must be expressed in the partition column.
- **`PNR-3` limits what P6 can measure.** Durations, occupancy and demand history *"begin on the day the
  job was switched on"*. `P6-02` refuses a demand window longer than the install's history; `P6-03`
  reports the months it has and does not annualise; `P6-10` renders **stale**, never `0`.
- **Adding an event *code* is cheap; adding a *dimension* to an existing code is not** (`PC-38`) — the
  dimension was never emitted for events already consumed and consumers' cursors have passed them.
  This binds `P6-04` and `P6-05` directly.
- **Filter-aware statistics get no cache name** (R1 `C-043`, `CacheConfiguration.java:190-196`, issues
  classic#790/#791) — and a dashboard is a wall of them.
- **Never name anything `wms_*` or `scc_*`.** `platform/…/V528:37,57,59` and `V663:17-19` carry hardcoded
  exclusions from the deleted earlier module; they grant a new module nothing, *"but a new `wms_`-prefixed
  permission would inherit a decision nobody took"* (`D-3`).
- **`widget_definitions.chk_module` admits neither `warehouse` nor `logistics`** after three DROP/ADD
  rewrites (`V234:36` → `V276:10` → `V557:18`). Both widenings use the **merge** idiom of
  `accounting-base/…/V600200:56-99` — read the live constraint, union, rebuild — because the last writer
  may sort after this file (`FR-377`).

## Blocked on decisions

- **⛔ `OD-8`** blocks **`P6-04`** and **`P6-08`** — how an out-of-process consumer authenticates to the
  port. There is no API-key table in platform (grep → 0); the only API-key path is per-handler inside the
  boom-barrier webhook. `PP-2`'s answer is a **platform service principal**, and it is *"the only item in
  this set that platform must build for warehouse."* Its fallback is explicit: an out-of-process consumer
  is **not supported until v3** — which is this version. **If it is still open, `logistics` ships
  in-process only and says so.**
- **⛔ `OD-2`** blocks **`P6-09`** — *"v3 planning, not before."* This phase is where it is **answered**,
  not deferred a third time.
- **⛔ `OD-4`** blocks **`P6-06`** — who owns the shared party master. The recommendation stands: base
  keeps `whb_counterparties`; future modules join through `whb_counterparty_external_refs`;
  **never an FK from base into another module.**
- **⛔ the unnumbered partition-key conflict** reaches **`P6-01`**.

## Definition of done
Per __MASTER__, plus the two that decide this phase:

1. **`git log --oneline -- warehouse-base/ | wc -l` is recorded in every `P6-08` PR description and is
   unchanged across the phase.** CI cannot see this reliably across rebases; a reviewer can, in one
   command (`PC-74`).
2. **The two deletion tests of `FR-336` are automated, not walked once.** Delete `logistics` and warehouse
   builds, migrates and runs; delete `warehouse` and `logistics` **starts** and degrades to a stated,
   documented mode. A seam is only proved by removing one side of it.
