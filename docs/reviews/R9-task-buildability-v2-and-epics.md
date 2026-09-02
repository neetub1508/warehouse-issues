# R9 — Task buildability and spec completeness: the v1.1 / v2 / v3 phases, and the nine epics

<!-- check-design-set: screen-citations file WS-238 — the BUILD-SPEC-SCREENS.md §1 next-free allocation marker (X-001). §3 names it as the one WS- id with no index row and §4 refuses to re-file it; it is quoted as evidence, never used as a reference -->

**Date** 2026-09-02 · **Branch** `docs/round-2-functional-review` · **Finding prefix** `H-`
(verified unallocated: `grep -rohE "\bH-[0-9]{1,3}\b" docs/ issues/ | wc -l` → **0**)

**File set actually read.**

```bash
cd /Users/bbhushan/work/git/workspace/warehouse-issues
ls issues/p3-*.md issues/p4-*.md issues/p5-*.md issues/p6-*.md | wc -l   # → 68  (the tasks in scope)
ls issues/0*-EPIC-*.md | wc -l                                           # →  9  (all nine epics)
ls docs/*.md | wc -l                                                     # → 16  (the design set)
# plus issues/README.md and issues/create-issues.sh          → 95 files
```

**Method, in three sentences.** I applied a thirteen-point buildability bar to all 68 P3–P6 task
files — tables and their columns, validations, the state machine, verb permissions, grid identifier,
filter scope, export, cache, i18n, mobile, scenarios, migration number, dependencies — scoring a
section that exists but says nothing usable as absent, and computing every count with a command
rather than reading impressions. I then walked each of the nine epics against six questions: does its
task checklist match the file glob, does its exit criterion actually follow from its own tasks, does
it reflect `DECISIONS.md` §5.1's four amendments, does it carry the `L-n` invariants, does any
cross-phase dependency hide inside an exit criterion, and will `create-issues.sh` file all 147 bodies
correctly today. Where a marker scan and a full read disagreed I read the file — twice that reversed
a draft finding, and both reversals are recorded in §4 rather than quietly dropped.

---

## §1 · Verdict

**Zero of the 68 tasks could be handed to a builder today with no questions asked.** Not one of them
states the columns, types, nullability or defaults of the tables it creates — for the whole design
set, `grep -rhoE 'CREATE TABLE (IF NOT EXISTS )?(whb|wh|wh3|whad|whas|whaf|whaa|whae|whin)_[a-z0-9_]+' docs/ issues/ | sort -u | wc -l`
returns **0** against **270** tables named in `DATA-MODEL.md`. That is the single most expensive
thing missing, and it is expensive in a specific way: `DATA-MODEL.md` §1.12's row shape stops at
column *names*, so every engineer who opens a task will invent a type, a length and a nullability,
and `OD-7` (precision scales) is still open, so the money columns will be invented inconsistently
across five modules by people who never meet.

Second: the plan's dependency graph stops at P1. `IMPLEMENTATION-PLAN.md` §3.3 and §3.4 are titled
*"The dependency graph — P0"* and *"— P1"*, and §3.5's critical path ends at `P2-21`. For the 68
tasks in my scope there is **no** graph, **no** critical path, and only **10 of 68** task files state
a dependency of their own. A team starting P3 has 23 tasks and no order.

Third: P5 and P6 have no permissions at all. `grep -ohE '\b(whb|wh|wh3|whad|whas|whaf|whaa|whin)_[a-z_]+:[a-z_]+\b' issues/p5-*.md issues/p6-*.md | sort -u`
is **empty** across 33 files, and `BUILD-SPEC-SCREENS.md` §10.2's 37 verb permissions include exactly
**three** `wh3_` rows. `X-014` already records the P3/P4 half of this; the P5/P6 half is unfiled and
is worse, because in P3/P4 the task files at least name the strings themselves (28 of 35 do).

Fourth: **not one entity in this design set has an enumerated state machine.** 31 status-bearing
tables land in P3–P6; 7 enumerate a vocabulary; **0** state a transition, an actor, a guard or a
terminal state, and there is not one from→to table anywhere in `docs/` or `issues/`. With `D-10`
declining `CHECK` constraints on catalogues, nothing will constrain the ladder at any layer.

The epics are in far better shape than the tasks. All nine cite exactly the tasks their glob
contains; every exit-criterion scenario id — `WH-SC-044`…`062`, `206`…`213`, `227`, `228`, `234`,
`239`, `240` — has an owning task in its own phase; all 101 v1.1/v2/v3 screens have an owning task
with zero orphans; and `create-issues.sh` will file all 147 bodies correctly today, so there is **no
BLOCKER in this lens**. Two epics carry factual errors (`08-EPIC-p6`'s migration table contradicts
`p6-08.md`'s own header; `07-EPIC-p5` says "Thirteen" and lists fifteen), and none of the nine
carries a build order. **Seven of nine epics are factually correct; zero of nine are executable as a
phase plan; zero of 68 tasks are buildable without asking a question.**

---

## §2 · The findings

Ten findings: **0 BLOCKER · 6 MAJOR · 4 MINOR.**

### `H-001` · The P5 and P6 verb permissions exist in no document and in no task file — **MAJOR**

- **What is missing or wrong:** `BUILD-SPEC-SCREENS.md` §10.2 carries 37 verb permissions. Thirty-four
  gate v1 (P0/P1/P2/P2-IN) transitions; **three** gate P5 transitions (`wh3_accessorials:approve`,
  `wh3_billing_runs:approve`, `wh3_sla_breaches:waive`); **none** gates a P6 transition. §4 of the same
  document enumerates, in its own Actions cells, at least 28 further 3PL transitions — Onboard,
  Suspend, Terminate, Assign, Complete, Reopen, Clone as new version, Activate, Expire, Reverse,
  Compute, Recompute, Rate, Emit AR handover, Cancel, Raise, Reject, Investigate, Uphold, Confirm,
  Post penalty, Retry — and **not one of them has a permission string anywhere.** Worse, the 27 P5/P6
  screens outside §4 (carriers, channels, NDR, COD, RTO, returns grading, obsolescence, recalls, NRV,
  replenishment, three-way match, cross-dock, weighing, labour) sit under table headers whose sixth
  column is *"Notes"*, not *"Actions"* — so for those the **verb itself** is never enumerated, only
  described in prose. `X-014` records the P3/P4 half of this and explicitly says §10.2 *"covers P0–P2
  … and stops there"*; it does not mention the three `wh3_` rows, and its "Missing, by task" list has
  no P5 or P6 entry.
- **Why it matters:** §10.2's own sentence is the consequence: *"A transition with no verb permission
  is a transition anybody with `:edit` can perform."* The moment it bites is the first 3PL contract.
  `wh3_billing_runs:approve` exists; `wh3_billing_runs:rate`, `:emit_ar_handover` and `:cancel` do
  not — so the operator who is allowed to edit a draft run is also allowed to cancel an invoiced one,
  and `wh3_disputes:uphold` is ungated, meaning the person who raised a credit can grant it. `FR-408`
  is the requirement that says a second user must approve above a threshold; without the strings it
  is unenforceable. And the asymmetry is already visible in the document: §10.2 lists
  `whb_accounting_handovers:retry` but not `wh3_ar_handovers:retry`, which is the same button on the
  same kind of queue.
- **Negative evidence:**
  ```bash
  grep -ohE '\b(whb|wh|wh3|whad|whas|whaf|whaa|whin)_[a-z_]+:[a-z_]+\b' issues/p5-*.md issues/p6-*.md | sort -u
  # → (empty) — across 33 task files
  sed -n '1976,2103p' docs/BUILD-SPEC-SCREENS.md \
    | grep -ohE '`(whb|wh|wh3|whad|whas|whaf|whaa|whin)_[a-z_]+:[a-z_]+`' | sort -u | wc -l   # → 37
  sed -n '1976,2103p' docs/BUILD-SPEC-SCREENS.md | grep -c 'wh3_'                              # →  3
  # contrast, P3/P4 — the task files do name their strings:
  for p in p3 p4; do echo "$p $(grep -lE '\b(whb|wh|wh3|whad|whas|whaf|whaa|whin)_[a-z_]+:[a-z_]+\b' issues/$p-*.md | wc -l)"; done
  # → p3 17   p4 11      (of 23 and 12)
  ```
- **The strings, so this is executable.** Derivable today from §4's Actions cells, in
  `<table>:<verb>` form per §10.1:
  `wh3_clients:onboard` · `:suspend` · `:terminate` ·
  `wh3_client_onboarding_tasks:assign` · `:complete` · `:reopen` ·
  `wh3_rate_cards:clone_version` · `:activate` · `:expire` ·
  `wh3_billable_events:reverse` ·
  `wh3_storage_billing_periods:compute` · `:approve` · `:recompute` ·
  `wh3_billing_runs:rate` · `:emit_ar_handover` · `:cancel` ·
  `wh3_accessorials:raise` · `:reject` ·
  `wh3_disputes:raise` · `:investigate` · `:uphold` · `:reject` ·
  `wh3_sla_breaches:confirm` · `:post_penalty` ·
  `wh3_ar_handovers:retry` ·
  plus `wh3_freight_billing_rules:end_date` and the `PORTAL` grant that WS-172 describes as *"a
  permission surface over the existing screens"* and which today has no name at all.
  **Twenty-five strings** plus the portal grant. For the 27 non-§4 P5/P6 screens the verbs must be
  decided before their strings can be written — that is the same work, one step earlier.
- **Where it belongs:** `warehouse-3pl` and `warehouse` · v2/v3 · P5 and P6.
- **Disposition:** *fold into `BUILD-SPEC-SCREENS.md` §10.2* — add the 25 rows above with their
  gating screen, and add to `07-EPIC-p5.md` and `08-EPIC-p6.md` under Traps the line *"every verb in
  a §4 Actions cell is a `@PreAuthorize`, not an `:edit`; the strings are §10.2 rows, and a screen
  whose verbs §3/§7 describes only in prose must enumerate them in the task before the controller is
  written."* `P5-01` (`V531000`–`V531099`, the 3PL permission migration) is the task that seeds them.
- **Irreversibility:** reversible in schema, but the permission rows and their
  `permission_dependencies` back-fill land in `V531000`–`V531099`; adding a verb permission later
  means a second migration and a second `role_permissions` back-fill against live grants. Name it in
  `P5-01`.
- **Relationship to round 1:** materially extends **`X-014`**, which is scoped to P3 and P4 only.
  What is new: the P5/P6 half; the count that §10.2 does carry three `wh3_` rows (so `X-014`'s
  *"stops there"* is imprecise); and the observation that P3/P4 tasks self-declare their strings
  while **zero** P5/P6 tasks do.

### `H-002` · No table in the design set carries a column-level DDL specification — **MAJOR**

- **What is missing or wrong:** `DATA-MODEL.md` names 270 tables. Its §1.12 row shape is
  `Table | Purpose | Key columns | Keys/indexes | FKs | FR | Ver`, and the "Key columns" cell gives
  **names only** — no type, no length, no precision, no nullability, no default. There is not one
  `CREATE TABLE` for a warehouse table anywhere in the set. In my segment, 38 `v1.1` + 76 `v2` + 4
  `v3` = **118 tables** are created by tasks that do not say what their columns are. Nine of 68 task
  files contain any type token at all, and when read, those nine turn out to be prose about *other*
  tables (`p4-03.md:74` describes the prior product's `wms_stock_transactions.reason_code VARCHAR(50)`;
  `p4-10.md:100` is the `permission_dependencies` warning).
- **Why it matters:** the moment it bites is the first week of P5. `wh3_rate_card_lines` carries
  `rate`, `minimum_quantity`, `tier_from`, `tier_to`; `wh3_billing_runs` carries `subtotal`,
  `tax_amount`, `total_amount`. `OD-7` — *"precision scales — before `P0-02`"* — is **open**
  (`GAP-REGISTER.md:1228`), so nothing tells the engineer whether a rate is `DECIMAL(15,2)` or
  `DECIMAL(19,6)`. A rate card priced at `12.345` per pallet-day stored in a `(15,2)` column rounds
  to `12.35`, and `WH-SC-234` — the v2 exit criterion — requires that *"every charge traces to a
  billable event"* with the arithmetic reproducible. The customer's invoice is then wrong by an
  amount nobody can explain, which is the definition of the failure the exit criterion exists to
  prevent. The same gap decides whether `gstin` is `VARCHAR(15)`, whether `status` is `VARCHAR(20)`
  or `VARCHAR(30)`, and whether `quantity` matches `whb_stock_movement_lines`' scale — a mismatch
  there makes the billing meter and the stock ledger disagree in the last digit.
- **Negative evidence:**
  ```bash
  grep -ohE '^\| `(whb|wh|wh3|whad|whas|whaf|whaa|whae|whin)_[a-z0-9_]+`' docs/DATA-MODEL.md \
    | tr -d '|` ' | sort -u | wc -l                                            # → 270 tables named
  grep -rhoE 'CREATE TABLE (IF NOT EXISTS )?(whb|wh|wh3|whad|whas|whaf|whaa|whae|whin)_[a-z0-9_]+' docs/ issues/ \
    | sort -u | wc -l                                                          # →   0 with DDL
  for p in p3 p4 p5 p6; do printf '%s %s of %s\n' "$p" \
    "$(grep -lE 'CREATE TABLE|VARCHAR\(|NUMERIC\(' issues/$p-*.md | wc -l)" "$(ls issues/$p-*.md | wc -l)"; done
  # → p3 1 of 23   p4 2 of 12   p5 0 of 21   p6 0 of 12   — and all three are prose about other tables
  ```
  For contrast, the sibling design set in this monorepo's prior art does carry them:
  `grep -c "CREATE TABLE" /Users/bbhushan/work/git/workspace/classic-issues/assets/docs/PHASE_1_FOUNDATION.md`
  → **13**, under a `## 7. Complete SQL Table Structure` heading with one `### 7.n` subsection per
  table. That is the house standard this set is below.
- **Where it belongs:** all five warehouse modules · v1, v1.1, v2, v3 · every phase (my evidence is
  scoped to P3–P6; R8 owns P0–P2-IN and will see the same shape).
- **Disposition:** *needs an `FR-`-level decision first, then folds into `DATA-MODEL.md`*. Close
  `OD-7` (adopt the accounting set's resolved precision set, as `GAP-REGISTER.md:1228` already
  proposes) and add two columns to the §1.12 row shape — `Types` and `Nulls` — or a `§1.13 Column
  specifications` block. Do **not** put this in 138 task files; put it in one document and have the
  task headers cite the row. Add to the master epic's Definition of done: *"the migration's column
  types, nullability and defaults come from `DATA-MODEL.md`; a task that invents one is not done."*
- **Irreversibility:** **partly unbackfillable.** A numeric scale chosen too small cannot be widened
  without a data-loss-free rewrite of every stored value, and for `warehouse-base` the money and
  quantity columns land in `V500030` (`PNR-1`/`PNR-2`), after which
  `IRREVERSIBLE.md` §3.1's rule applies. For my segment the deadline is each task's own migration,
  but the *scale decision* must precede `V500030`.
- **Relationship to round 1:** materially extends **`OD-7`**, which covers numeric precision only.
  What is new: precision is one column of a spec that is absent in every column, for every table,
  and the computed 270-vs-0 count.

### `H-003` · The dependency graph and the critical path stop at P1; 68 tasks have no build order — **MAJOR**

- **What is missing or wrong:** `IMPLEMENTATION-PLAN.md` §3 is titled *"The critical path and the
  sequencing constraints"*. §3.3 is *"The dependency graph — P0"* (line 642); §3.4 is *"— P1"* (line
  700). There is no §3.x for P2, P2-IN, P3, P4, P5 or P6. §3.5's critical path is 21 tasks ending at
  `P2-21`. §3.6's parallelism table names P3–P6 in exactly two rows — *"P3 adapters: `P3-20 ‖ P3-21`"*
  and *"P4 ‖ P5: the whole of each"* — which between them order 2 of my 68 tasks. And the task files
  do not fill the gap: **10 of 68** state a dependency, against 14 of 37 in P0/P1 where the graph
  already exists. None of the nine epics has a build-order or dependency section at all
  (`grep -n '^## ' issues/0*-EPIC-*.md` — the sections are Overview, Exit criterion, Migration blocks,
  Tasks, Traps, Definition of done).
- **Why it matters:** the moment it bites is the P3 kickoff. A lead is handed 23 tasks and a
  two-scenario exit criterion and must reconstruct, from 23 task bodies, that `P3-02` (the task
  claiming query with `SKIP LOCKED`) gates `P3-01` (the nine RF screens) — which `p3-01.md:92` says
  in passing but no plan states — and that `P3-06` (waving), `P3-02` and `P3-12` must land together
  for `WH-SC-228`, which only `p3-02.md:44` records. In P5 it is worse: 21 tasks, three modules, an
  exit criterion in three clauses, and the only sequencing statement in the whole phase is that
  `P4-10` depends on `P5-01`. Teams will either serialise everything, or discover the edges by
  breaking the build.
- **Negative evidence:**
  ```bash
  grep -nE '^### 3\.' docs/IMPLEMENTATION-PLAN.md
  # → 3.1 The one sentence / 3.2 The four points of no return / 3.3 The dependency graph — P0
  #   3.4 The dependency graph — P1 / 3.5 The critical path, end to end / 3.6 What can run in parallel
  #   3.7 The sequencing constraints that are not dependencies      — nothing for P2..P6
  sed -n '761,764p' docs/IMPLEMENTATION-PLAN.md   # the critical path: ends "... P2-20 → P2-21"
  for p in p3 p4 p5 p6; do printf '%s %s of %s\n' "$p" \
    "$(grep -liE 'depends on|prerequisite|blocked by|must land (first|before)' issues/$p-*.md | wc -l)" \
    "$(ls issues/$p-*.md | wc -l)"; done      # → p3 1 of 23   p4 4 of 12   p5 3 of 21   p6 2 of 12
  grep -rn 'dependency graph\|critical path' docs/GAP-REGISTER.md docs/DESIGN-SET-DEFECTS.md | wc -l   # → 0
  ```
- **Where it belongs:** design-set process · v1.1/v2/v3 · P2 through P6.
- **Disposition:** *new document sections needed, not new tasks* — add `IMPLEMENTATION-PLAN.md` §3.8
  *"The dependency graph — P2 … P6"* in the shape of §3.3, and extend §3.5's chain past `P2-21`.
  Then add one `## Build order` section to each of `05-EPIC-p3` … `08-EPIC-p6` naming the phase's
  first task, its long pole and its parallel streams. Three edges are already discoverable and should
  be the seed rows: `P3-02 → P3-01` (`p3-01.md:92`), `{P3-02, P3-06, P3-12} → WH-SC-228`
  (`p3-02.md:44`), `P5-01 → P4-10` (`07-EPIC-p5.md`, §3.6 row 9).
- **Irreversibility:** reversible.
- **Relationship to round 1:** **new.** `grep -rn 'dependency graph\|critical path' docs/GAP-REGISTER.md docs/DESIGN-SET-DEFECTS.md`
  → 0.

### `H-004` · Not one entity has an enumerated state machine — 31 status-bearing tables in P3–P6, 0 transitions — **MAJOR**

- **What is missing or wrong:** across `docs/` and `issues/` there is **not one** from→to transition
  table. 94 `DATA-MODEL.md` table rows name a `status` or `state` column; 36 enumerate a vocabulary
  inline in the Key-columns cell (`wh3_billing_runs` … `status` (`DRAFT`/`RATED`/`APPROVED`/
  `INVOICED`/`CANCELLED`)); **0** state which transition is legal from which state, who may perform
  it, what guard it must pass, or which states are terminal. Scoped to my phases: **31**
  status-bearing tables, **7** with a vocabulary, **0** with transitions. Only 2 of 68 task files
  (`p5-02`, `p5-05`) contain even an arrow chain, and both are prose. `BUILD-SPEC-SCREENS.md:1177`
  (`WS-045`, periods) is the **single** line in all sixteen documents that draws a ladder.
- **Why it matters:** `D-10` declines `CHECK` constraints on the open catalogues, so the database
  will not constrain the ladder either. The moment it bites is the first billing dispute: `WS-162`'s
  Actions cell says Approve *"freezes the state"* and `WS-164`'s says Uphold *"becomes a credit
  charge code — **never a silent edit of the run**"*. Whether `INVOICED → CANCELLED` is legal decides
  whether an emitted AR handover can be revoked after the customer has the invoice, and nothing in
  the set answers it. Two engineers on `P5-05` and `P5-07` will answer it differently, and the
  divergence surfaces as a client seeing a cancelled invoice that accounting has already posted.
  The same silence covers `wh_recalls` (is `CLOSED` terminal, or may a recall be reopened when a
  second lot is implicated?) and `wh_shipment_ndrs` (`WS-120` is described as *"a workflow with a
  response clock"* with the actions in `wh_ndr_actions` — and no ladder).
- **Negative evidence:**
  ```bash
  grep -rniE '^\| *(from|current) *(state|status)? *\|' docs/ issues/
  # → 2 hits, neither a state machine: docs/reviews/R6...:1233 "| From | Failure mode to ratchet |"
  #                                     issues/p4-01.md:32  "| From | The defect | What this task must do |"
  grep -E '^\| `(whb|wh|wh3|whad|whas|whaf|whaa|whae|whin)_[a-z0-9_]+`' docs/DATA-MODEL.md \
    | grep -cE '`[a-z_]*status[a-z_]*`|`[a-z_]*state`'                        # → 94 status-bearing tables
  # ... of which, restricted to Ver v1.1/v2/v3: 31 rows, 7 with >=2 ALLCAPS tokens, 0 with an arrow
  grep -cE '[A-Z][A-Z_]{2,} *(→|->) *[A-Z][A-Z_]{2,}' issues/p3-*.md issues/p4-*.md issues/p5-*.md issues/p6-*.md \
    | grep -v ':0' | wc -l                                                     # → 2 of 68
  ```
- **Where it belongs:** `warehouse`, `warehouse-3pl` · v1.1/v2/v3 · P3–P6 (and, on the same evidence,
  v1 — R8's segment).
- **Disposition:** *fold into `BUILD-SPEC-SCREENS.md`* — one `§0.11 State ladders` table with the
  columns `Table | From | To | Verb | Actor (permission) | Guard | Terminal?`, one block per
  status-bearing table, seeded from the verb list in `H-001` (the two lists are the same list read
  from two sides, which is why they should be authored together). Then add to the master epic's
  Definition of done: *"a task creating a `status` column ships its ladder row; a state with no
  inbound transition and a non-terminal state with no outbound transition are both defects."*
- **Irreversibility:** reversible as a document; **not** reversible in data — a status value written
  by a build that guessed the ladder is in the customer's table forever, and `IRR-41`-shaped
  append-only tables cannot be corrected by `UPDATE`.
- **Relationship to round 1:** **new.** `grep -rniE 'state machine|state ladder|status ladder' docs/GAP-REGISTER.md docs/DESIGN-SET-DEFECTS.md`
  returns nothing that names the absence of transitions; `X-006` and `X-015` are about scenario
  coverage, not about ladders.

### `H-005` · Half the v1.1 exit criterion depends on a v1 schema fact that neither owning task states — **MAJOR**

- **What is missing or wrong:** `WH-SC-228` — *the* second half of the v1.1 exit criterion — requires
  *"task interleaving — the same operator's next task may be a **replenishment or a count** in the
  aisle they are already in"*. That is only implementable if `wh_count_tasks` and
  `wh_replenishment_tasks` are 1:1 extensions of `whb_tasks`, because the RF Task List (`WS-237`)
  backs `WS-059`, which reads `whb_tasks`. `DATA-MODEL.md` mandates exactly that — line 1002:
  *"`wh_count_tasks` | The 1:1 count extension of `whb_tasks` | `task_id` (uk) … `task_id ↓base
  whb_tasks`"*; line 1083 the same for `wh_replenishment_tasks`; and §3.4 defect **X-4** is named as
  the shape being avoided. **Neither owning task file says so.** `p2-04.md` creates `wh_count_tasks`
  at `V510033` and `p3-12.md` creates `wh_replenishment_tasks` at `V510108`, and in both files
  `grep -nE 'whb_tasks|task_id|1:1'` returns **nothing**. The two sibling task tables' files do say
  it, in their scope line *and* in an acceptance checkbox.
- **Why it matters:** the moment it bites is the P3 exit demo. If `wh_count_tasks` shipped in v1 with
  its own `assigned_to` / `started_at` / `completed_at` — which is what an engineer reading only
  `p2-04.md` will build, because that is what "a count task" means — then on the handheld the count
  queue and the pick queue are two queues. The operator finishes a pick and the device offers the
  next pick; the count in the same aisle is invisible. `WH-SC-228` fails, and the fix is not a code
  change but a migration that creates a `whb_tasks` row for every count task already written in
  production, with lifecycle timestamps that were recorded on the wrong row.
- **Negative evidence:**
  ```bash
  grep -nE 'whb_tasks|task_id|1:1' issues/p2-04.md issues/p3-12.md      # → (empty)
  grep -nE 'whb_tasks|task_id|1:1' issues/p2-09.md issues/p1-15.md
  # → p2-09.md:8   "**`V510041` — WH-31 — `wh_pick_tasks`.** The **1:1 pick extension of `whb_tasks`**"
  #   p2-09.md:100 "- [ ] `wh_pick_tasks` declares **no** duplicate of `whb_tasks`' lifecycle timestamps"
  #   p1-15.md:14  "- **Putaway tasks are `whb_tasks` rows** (`P0-10`) …"
  #   p1-15.md:90  "- [ ] The putaway task is a `whb_tasks` row with `assigned_at`/`started_at`/`completed_at`"
  sed -n '1002p;1083p' docs/DATA-MODEL.md      # both say "The 1:1 … extension of `whb_tasks`"
  ```
- **Where it belongs:** `warehouse` · v1 (`P2-04`) and v1.1 (`P3-12`) · P2 and P3.
- **Disposition:** *fold into `P2-04` and `P3-12`.* To `p2-04.md`, in the `V510033` scope bullet, add:
  *"`wh_count_tasks` is the **1:1 count extension of `whb_tasks`** (`P0-10`, `DATA-MODEL.md` line
  1002) — `task_id` unique and FK to base; it duplicates none of `whb_tasks`' lifecycle timestamps.
  `WH-SC-228`'s interleaving reads the base queue."* Add the matching acceptance checkbox in the
  shape of `p2-09.md:100`. To `p3-12.md`, in the `V510108` scope bullet, add the same sentence for
  `wh_replenishment_tasks` citing line 1083 and `FR-255`/`FR-259`.
- **Irreversibility:** **`V510033` is the point of no return for the count half** — it is a v1
  migration that ships before P3 begins, and once counts have been executed against it the lifecycle
  timestamps live on the wrong row and cannot be moved without inventing base rows for history.
  `V510108` (P3) is reversible because it lands in the same phase as the scenario that tests it.
- **Relationship to round 1:** **new.** `X-4` (in `DATA-MODEL.md` §3.4) records the *shape*; what is
  new is that two of the four task tables' task files omit the fact, and that one of those two is a
  **v1** migration on which the **v1.1** exit criterion silently depends — the cross-phase edge my
  brief asked me to look for, alongside the four already known (`X-018`, `X-025`, `X-026`, `X-031`).

### `H-006` · `08-EPIC-p6`'s migration table allocates a band that `p6-08.md` explicitly withdraws, and its "re-derived" command output is stale — **MAJOR**

- **What is missing or wrong:** `08-EPIC-p6.md:61` is headed *"Migration blocks — **re-derived from
  the task headers, not transcribed**"*, shows a fenced command, and prints
  `# → V500100 V500101 V510300 V510301 V510302 V524000 V524099 V530100 V530110 V530111`. Its table
  then carries the row `| V524000–V524099 | **logistics** | the module | P6-08 | …`. But `p6-08.md:4`
  says the opposite, in the header the epic claims to have derived from: *"Migrations **none in this
  design set's bands** — `D-2` allocates a band to warehouse's five modules and to no other"*, and
  `p6-08.md:57` states in terms that *"Claiming `V524000`–`V524099` on this header would have this
  design set allocate numbers for a module it does not specify."* Running the epic's own command
  today produces **`V524999`**, not `V524099` — the two numbers appear in `p6-08.md:4` only inside
  the refusal sentence, and the printed output has since drifted from what the command emits.
- **Why it matters:** `GAP-REGISTER.md:992` records this as **FIXED** — *"`p6-08` withdraws
  `V524000`–`V524099`, and `D-2` / `DATA-MODEL.md` §2.5.6 now state that `logistics` gets no band
  here"*. The fix landed in three of six places. It did not land in `08-EPIC-p6.md`, nor in
  `IMPLEMENTATION-PLAN.md` §1 (line 54 still lists `V524000–V524099` among P6's migrations) or §2.9
  (line 358, contradicting its own line 1189 which documents the withdrawal), nor in
  `PORT-AND-ADAPTER-CONTRACT.md:1179` and `:1184` (which shows a file path
  `logistics/backend/…/V524001__Register_logistics_with_warehouse.sql`). The moment it bites is when
  a builder opens the P6 epic — the document written to be the phase's front door — reads a
  migration table that says *"re-derived from the task headers"*, and allocates 100 numbers in the
  adapter band for a module whose own task refuses them. A number claimed in two design sets is the
  Flyway collision `DECISIONS.md` §6 exists to prevent.
- **Negative evidence:**
  ```bash
  cd issues && grep -h '^Part of' p6-*.md | grep -oE 'V5[0-9]{5}' | sort -u | tr '\n' ' '
  # → V500100 V500101 V510300 V510301 V510302 V524000 V524999 V530100 V530110 V530111
  #   the epic's fenced output claims  ... V524000 V524099 ...   ← stale
  grep -n 'V524099' p6-*.md
  # → p6-08.md:57  "Claiming `V524000`–`V524099` on this header would have this design set allocate numbers for a"
  sed -n '4p' p6-08.md | grep -o 'Migrations \*\*none in this design set.s bands\*\*'
  # → Migrations **none in this design set's bands**
  grep -n 'V524000' ../docs/IMPLEMENTATION-PLAN.md ../docs/PORT-AND-ADAPTER-CONTRACT.md | head
  # → IMPLEMENTATION-PLAN.md:54, :358 (still claiming) vs :1189 (documenting the withdrawal)
  #   PORT-AND-ADAPTER-CONTRACT.md:1179, :1184
  ```
- **Where it belongs:** design set · v3 · P6.
- **Disposition:** *fold into `08-EPIC-p6.md`* — replace the `V524000`–`V524099` table row with the
  refusal `p6-08.md:4` states, and re-paste the fenced command's real output. Then apply the same
  correction to `IMPLEMENTATION-PLAN.md` §1 line 54 and §2.9 line 358, and to
  `PORT-AND-ADAPTER-CONTRACT.md:1179`/`:1184`. And add to the epic authoring rule: a block headed
  *"re-derived, not transcribed"* must have its output regenerated in the same commit as any task
  header change, or the claim is worse than transcription because it invites trust.
- **Irreversibility:** reversible today; **irreversible the day a `V524xxx` file is committed** in
  either design set.
- **Relationship to round 1:** materially extends **`X-044`** (recorded FIXED at
  `GAP-REGISTER.md:992`). What is new: the fix is incomplete in four files, and the P6 epic's
  self-derivation claim is falsified by re-running its own command.

### `H-007` · `07-EPIC-p5` miscounts its own scenario-authoring list and calls two claimed migration numbers unclaimed — **MINOR**

- **What is missing or wrong:** two factual errors in the phase's front door. (1) Line 66:
  *"**Thirteen** P5 tasks therefore author their own scenarios as their first act"* — followed by a
  list of **fifteen** ids (`P5-05`, `-06`, `-07`, `-09`, `-10`, `-11`, `-12`, `-13`, `-15`, `-16`,
  `-17`, `-18`, `-19`, `-20`, `-21`). (2) Line 86, the migration table:
  *"| `V500064`–`V500199` | `warehouse-base` post-v1 DDL | **two numbers still to claim** — `P5-20`'s
  ratio-pack template, `P5-21`'s packaging balance |"* — but `p5-20.md:4` claims **`V500064`** and
  `p5-21.md:4` claims **`V500065`**, and both appear in the output of the epic's own derivation
  command four lines above.
- **Why it matters:** small, but it is the same failure mode as `H-006` in the same kind of block. A
  planner sizing P5 reads "thirteen" and budgets two fewer scenario-authoring efforts than the phase
  needs; an engineer picking up `P5-20` reads "still to claim" and takes the next free number,
  colliding with the header of the file they are implementing.
- **Negative evidence:**
  ```bash
  sed -n '65,67p' issues/07-EPIC-p5.md | grep -oE '`P5-[0-9]{2}`' | wc -l          # → 15
  sed -n '65,67p' issues/07-EPIC-p5.md | grep -o 'Thirteen'                        # → Thirteen
  sed -n '4p' issues/p5-20.md | grep -o 'V500064'                                  # → V500064
  sed -n '4p' issues/p5-21.md | grep -o 'V500065'                                  # → V500065
  cd issues && grep -h '^Part of' p5-*.md | grep -oE 'V5[0-9]{5}' | sort -u | head -2   # → V500064 V500065
  ```
- **Where it belongs:** design set · v2 · P5.
- **Disposition:** *fold into `07-EPIC-p5.md`* — change "Thirteen" to "Fifteen", and replace the
  `V500064`–`V500199` cell with `V500064` (`P5-20`) · `V500065` (`P5-21`) · `V500066`–`V500199`
  still free.
- **Irreversibility:** reversible.
- **Relationship to round 1:** **new** — `X-044` covers the numbers themselves; this is the epic's
  prose about them.

### `H-008` · Invariant and amendment carriage collapses after P0; `A-3` reaches no phase epic — **MINOR**

- **What is missing or wrong:** `X-050` tests amendment carriage across twelve `docs/*.md` files and
  finds five at zero. It never tests `issues/`. Run the same command there: `00-EPIC-master` cites
  all four `A-`; `03-EPIC-p2` cites `A-1`/`A-2`; `04-EPIC-p2in` and `06-EPIC-p4` cite `A-4`;
  `05-EPIC-p3` cites `A-2`; and **`01-EPIC-p0`, `02-EPIC-p1`, `07-EPIC-p5` and `08-EPIC-p6` cite
  none.** `A-3` — *item-variant schema to v1, matrix screens to v2* — appears in **no phase epic at
  all**, and its two owning phases are exactly two of those four (`P1` for the schema, `P5` for
  `WS-032`/`WS-033`). Invariant carriage shows the same shape: `01-EPIC-p0` cites 15 distinct `L-n`;
  `03-EPIC-p2` and `08-EPIC-p6` cite **zero**; the other five cite one or two. And only
  `01-EPIC-p0` and `02-EPIC-p1` have a `## The invariants this phase establishes` section —
  `05-EPIC-p3` … `08-EPIC-p6` have none.
- **Why it matters:** the epic is the document a phase lead reads on day one, and its job is to put
  the invariants in front of them before the first line of code. A P5 lead building `P5-20`'s
  Style × Variant Matrix has no way to learn from their own epic that `A-3` already put the schema in
  v1 and that they are building screens over existing tables — the risk is a second variant schema.
  A P6 lead reading `08-EPIC-p6` gets no `L-n` at all, in the phase that adds `warehouse-base`
  migrations (`V500100`, `V500101`) where `L-4` and `L-13` decide whether a column is a cache or a
  fact.
- **Negative evidence:**
  ```bash
  for f in issues/0*-EPIC-*.md; do printf '%-22s A:%s  L:%s\n' "$(basename $f .md)" \
    "$(grep -ohE '`A-[1-4]`' $f | sort -u | tr '\n' ' ')" \
    "$(grep -ohE '\bL-1?[0-9]\b' $f | sort -u | wc -l)"; done
  # 00-EPIC-master  A:`A-1` `A-2` `A-3` `A-4`   L:14
  # 01-EPIC-p0      A:                          L:15
  # 02-EPIC-p1      A:                          L: 2
  # 03-EPIC-p2      A:`A-1` `A-2`               L: 0
  # 04-EPIC-p2in    A:`A-4`                     L: 1
  # 05-EPIC-p3      A:`A-2`                     L: 2
  # 06-EPIC-p4      A:`A-4`                     L: 1
  # 07-EPIC-p5      A:                          L: 1
  # 08-EPIC-p6      A:                          L: 0
  grep -rlE '`A-3`' issues/     # → issues/00-EPIC-master.md issues/p1-01.md issues/p5-20.md
  ```
  On the house-style benchmark my brief named: `/Users/bbhushan/work/git/workspace/classic-issues/assets/`
  contains **no epic files at all** — `find assets -type f` returns 16 paths, all under `assets/docs/`,
  and `grep -ncE 'Exit criteri|Definition of Done|Invariant' assets/docs/PHASE_*.md` → **0** on all
  six. The warehouse epics are ahead of that benchmark on exit criteria and invariants and behind it
  on column specifications (`H-002`). There is no external standard to converge on; the standard is
  `01-EPIC-p0`.
- **Where it belongs:** design set · all versions · all phases.
- **Disposition:** *fold into the four epics* — add `A-3` to `02-EPIC-p1` and `07-EPIC-p5`; add a
  `## The invariants this phase establishes` section to `05-EPIC-p3` … `08-EPIC-p6` in
  `01-EPIC-p0`'s shape, naming at minimum `L-4`/`L-13` for P6 and `L-10`/`L-14` for P3/P5. Extend
  `X-050`'s command to `issues/*.md` so the next run catches it.
- **Irreversibility:** reversible.
- **Relationship to round 1:** materially extends **`X-050`**, whose evidence command covers
  `docs/` only. What is new: the same test applied to the nine epics, the four that fail, and the
  fact that `A-3` reaches no phase epic.

### `H-009` · The v3 zero-commit ratchet is stated in two forms in the same file; the executable one is not the one the epic quotes — **MINOR**

- **What is missing or wrong:** `p6-08.md:130` states the falsifier in a per-PR form —
  *"any commit **in this PR** touching `warehouse-base/**`"* — which is executable. Sixty lines later
  `p6-08.md:191` states it as a time window: *"`git log --oneline -- warehouse-base/ | wc -l` is
  **unchanged across the whole of `P6-08`**"*, and `08-EPIC-p6.md:169` repeats that form. The window
  form cannot hold, because `p6-01.md:4` writes `V500100` and `p6-04.md:4` writes `V500101` **to
  `warehouse-base`** in the same phase, and — per `H-003` — nothing orders P6's twelve tasks, so
  those commits may land at any point inside `P6-08`'s window.
- **Why it matters:** this is the headline proof of the whole port-and-adapter contract —
  `PORT-AND-ADAPTER-CONTRACT.md` §9.7 calls `P6-08` *"the consumer the whole contract is a test for"*.
  A ratchet that fails for a reason unrelated to what it measures gets waived, and a waived ratchet
  is not a ratchet. The moment it bites is the first `P6-08` PR filed after `P6-01` merges: the
  count has moved, the author cannot show it unchanged, and the reviewer either blocks a correct PR
  or ticks the box anyway.
- **Negative evidence:**
  ```bash
  grep -n 'git log' issues/p6-08.md issues/08-EPIC-p6.md
  # p6-08.md:130   "any commit in this PR touching `warehouse-base/**` — git log --oneline -- warehouse-base/ | wc -l"
  # p6-08.md:191   "**git log --oneline -- warehouse-base/ | wc -l is unchanged across the whole of P6-08**"
  # 08-EPIC-p6.md:169  same window form
  sed -n '4p' issues/p6-01.md   # Part of __P6__ · Module **`warehouse-base`** · Migrations **V500100**
  sed -n '4p' issues/p6-04.md   # Part of __P6__ · Module **`warehouse-base`** · Migrations **V500101**
  ```
- **Where it belongs:** `logistics` / `warehouse-base` · v3 · P6.
- **Disposition:** *fold into `p6-08.md` and `08-EPIC-p6.md`* — delete the window form and keep the
  per-PR form, phrased as *"`git diff --name-only origin/main...HEAD -- warehouse-base/ | wc -l` is
  `0` on every `P6-08` PR"*, which is what a CI check can assert. Note in the epic that `P6-01` and
  `P6-04` do commit to `warehouse-base/` and that this is expected and not a `P6-08` violation.
- **Irreversibility:** reversible.
- **Relationship to round 1:** **new.**

### `H-010` · Four P3/P4 tasks state no mobile verdict, which the set's own Definition of done calls a defect — **MINOR**

- **What is missing or wrong:** `00-EPIC-master.md`'s Definition of done requires *"**mobile
  counterpart delivered, or its absence declared with a reason — silence is a defect**"* (`D-13`,
  `FR-218`). All 33 P5/P6 tasks carry an explicit `**Mobile:**` line; the P3/P4 tasks carry the
  verdict as a `| Mobile |` row inside their Screen contract table. Four carry neither and never use
  the word: **`p3-14`, `p3-22`, `p3-23`, `p4-11`.**
- **Why it matters:** three of the four are defensibly deskless — `p3-22` is the event stream,
  `p3-23` is the sandbox and in-product help, `p4-11` is tax-basis inventory valuation. **`p3-14` is
  not.** It is a floor operation: its own scope says *"the verification is an ordinary count task
  against `whb_tasks` with its own task type"*, and `WS-235 RF Cycle Count` is one of the nine RF
  screens the v1.1 exit criterion `WH-SC-227` requires. Whether the verification count appears on the
  handheld was never decided, and by the set's own rule that silence is the defect — not the answer.
- **Negative evidence:**
  ```bash
  for f in issues/p3-*.md issues/p4-*.md issues/p5-*.md issues/p6-*.md; do
    grep -qi 'mobile' "$f" || echo "no mobile verdict: $(basename $f)"; done
  # → p3-14.md  p3-22.md  p3-23.md  p4-11.md      (4 of 68)
  for f in issues/p5-*.md issues/p6-*.md; do grep -qiE '\*\*Mobile' "$f" || echo "MISSING $(basename $f)"; done
  # → (empty) — all 33 P5/P6 tasks declare one
  ```
- **Where it belongs:** `mobile` · v1.1/v2 · P3 and P4.
- **Disposition:** *fold into the four task files* — add one `| Mobile |` row each. For `p3-14`, the
  line to add is *"**Mobile:** `WS-235 RF Cycle Count` — the verification count is a `whb_tasks` row
  of its own type and appears in the handheld task list like any other count (`D-13`)"*, or an
  explicit `none` with the reason. For `p3-22`, `p3-23` and `p4-11`, `none` with the reason already
  implied by their `Screens **—**` headers.
- **Irreversibility:** reversible.
- **Relationship to round 1:** **new.** `X-023` covers scenario ownership in P0/P1, not mobile
  verdicts; `D-13` states the rule and nothing tests it.

---

## §3 · What I checked and found sound

Everything below I went looking for, expecting a finding, and did not get one. Round 3 should not
re-walk it.

**Backlog filing — the designated BLOCKER, and it is clean.** `issues/create-issues.sh` (391 lines,
read in full) will file all 147 bodies correctly today.
- Fence parity: `render()` toggles a `fenced` flag on every ```` ``` ```` line and only substitutes
  `__TASKS__` when it is alone on an unfenced line. **Zero** files have an odd fence count
  (`for f in *.md; do n=$(grep -c '^[[:space:]]*```' "$f"); [ $((n%2)) -ne 0 ] && echo "ODD $f"; done`
  → empty across 148 files), so no tail is ever mis-treated as fenced.
- Labels: `ensure_labels` splits on `,` with no space trimming; **no** `LABELS:` line contains `, `
  (`grep -h '^LABELS: ' *.md | grep -c ', '` → 0), and 22 distinct labels are harvested.
- Body size: largest body is `00-EPIC-master.md` at **34,018** bytes, under GitHub's 65,536 limit;
  `wc -c *.md | sort -rn | head -3` confirms.
- Placeholders: `assert_placeholder_lines` runs before any mode; every task file references only its
  own phase placeholder; the `01-EPIC-p0` / `02-EPIC-p1` self-references resolve in step 4/6's
  `patch` via `set_phase_subst`.
- Globbing: `PHASES=(p0 p1 p2 p2in p3 p4 p5 p6)` with `"$DIR"/${PHASES[$i]}-*.md` — `p2-*` cannot
  match `p2in-01.md`, and `README.md` is never created because create mode never uses `*.md`.
- Idempotence: the script refuses to run if the repo already has issues, and step 6/6 writes
  `issues/CREATED.md`.
- One latent trap, benign today: `is_issue_file()` is `grep -q '^TITLE: '`, and `README.md` contains
  a `TITLE: ` line (inside its format example), so `--sync` / `--check` iterate over it — but both
  skip it for want of an `issue: NN` line. Worth a comment, not a finding.
- The only real gap is by design: the script creates **checklist** links (`- [ ] #N`) and a
  `Part of #N` prose line, **not** GitHub native sub-issue relationships. Stated here so nobody
  files it as a defect later.

**Epic checklist ↔ file glob (Part B check 1) — all nine correct, content as well as mechanics.**
Every epic cites exactly as many distinct task ids as its glob has files: `01`→17/17, `02`→20/20,
`03`→29/29, `04`→4/4, `05`→23/23, `06`→12/12, `07`→21/21, `08`→12/12, computed with
`for pair in "01-EPIC-p0 p0 P0" …; do ls ${g}-[0-9]*.md | wc -l; grep -ohE "\b${U}-[0-9]{2}\b" $e.md | sort -u | wc -l; done`.
`X-046`'s placeholder-placement defect has no content-level twin.

**Exit criteria — every scenario id has an owning task in its own phase.** `WH-SC-227` → `p3-01`
(which owns all nine RF screens `WS-229`…`WS-237`) · `WH-SC-228` → `p3-02`, `p3-06`, `p3-12` ·
`WH-SC-234` → `p5-03`, `p5-05` · `WH-SC-239` → `p4-02` · `WH-SC-240` → `p4-03`. The v1 and P2-IN
sets are complete too: of `WH-SC-044`…`062` and `206`…`213`, **zero** are orphaned.
The sub-clauses hold as well — P3's `FR-424` (<300 ms measured **at the handheld**) is `p3-01.md:106`
and `FR-425` (`SKIP LOCKED`, load-tested) is `p3-02.md:81`; P5's three `IMPLEMENTATION-PLAN.md` §1.7
clauses are owned by `p5-05` (reproducible arithmetic), `p5-08` (per-endpoint cross-client negative
test) and `p5-09.md:37` (*"the same `(channel account, external order id)` imported twice producing
**one**"*); P4's reproducibility addition is carried in `p4-02`, `p4-03` and `p4-08`. **P3 is the
best-specified phase in the set** — its exit criterion follows from its tasks with no gap I could
find.

**Screen coverage — zero orphans.** All **101** screens the build-spec index marks `v1.1 · P3`,
`v2 · P4`, `v2 · P5` or `v3 · P6` have at least one owning task file
(`grep -E '^\| WS-[0-9]{3} .*\| v(1\.1 · P3|2 · P4|2 · P5|3 · P6) \|' docs/BUILD-SPEC-SCREENS.md`
→ 101; every one greps to a task). And in reverse, the only `WS-` id cited in a P3–P6 task that has
no index row is `WS-238`, which is the fenced next-free allocation marker (`X-001`), not a citation.

**P5/P6 screens do have columns and filters, even though their task files carry no screen contract.**
Only 2 of 21 P5 and 1 of 12 P6 task files name a grid identifier — but `BUILD-SPEC-SCREENS.md` §4
gives every `wh3_` screen its scope, key columns, filters **with buckets**, actions and a per-section
mobile note, and §3.3/§3.5/§7/§8 do the same for the rest. §0.2 derives `gridIdentifier`, filter
scope, permission resource, route and i18n root mechanically from the table name. I drafted this as a
finding and withdrew it; see §4.

**Tasks that own no scenario are honest about it, with a reason.** `p3-08`, `p3-18`, `p3-21`,
`p4-07`, `p4-11` each open `## Scenarios closed` with **None.**, cite the specific
`SCENARIO-CATALOGUE.md` §4.2 unproven-requirement row, and say *"a scenario should be written with
this task rather than cited from thin air"*. That is exactly the discipline
`DESIGN-SET-DEFECTS.md:724` praises (*"No scenario id was invented to fill a section"*), and
`X-023`'s P0/P1 finding has no P3/P4 twin.

**Migration blocks in `05-EPIC-p3` are exactly accurate.** `V510100`–`V510108` map to
`P3-06`/`07`/`11`/`08`/`09`/`13`/`17`/`18`/`12` in that order, and the "seven tasks write no
migration" list is correct. **`07-EPIC-p5`'s** table is accurate too except for the one stale cell in
`H-007` — the apparent gaps at `V510204` and `V530041`/`V530042` are an artefact of task headers
using ranges (`V510203–V510205`), and the numbers are claimed in the task bodies and in
`DATA-MODEL.md` §7.

**The `logistics` cross-phase reservation chain is airtight.** `P0-14` reserves the band and the
`log_` prefix in v1; `P0-15` seeds `logistics:*` permission rows `is_active = false` in `V501000`;
`P6-08` carries six named falsifiers including *"any `REFERENCES … log_` clause in a migration
numbered below `V524000`"*. The band **allocation** is contradicted (`H-006`); the **reservation
mechanism** is not.

**Mobile verdicts are near-complete.** All 33 P5/P6 tasks declare one explicitly with a reason; 31 of
35 P3/P4 tasks declare one as a `| Mobile |` screen-contract row. Only four are silent (`H-010`), and
the `EntityListScreen` dropdown-only constraint is respected where it matters — `p3-03.md:48` makes
`lastSeenBefore` *"a dropdown of named ages, not a date filter … so the mobile screen can carry it"*,
citing `mobile/src/components/common/ListHeader.tsx:216`.

**Cross-cutting concerns are allocated centrally, not per task, and that is correct.** i18n
(`P0-01` scaffold, `P1-19` sweep, `P2-IN-01` India, `P5-01` 3PL), cache registration, export
supersetting and `filter_definitions`/`grid_preferences` parity are all clauses of the master epic's
Definition of done. A task file that is silent on them is covered; a task file that is silent on its
**columns**, its **verbs**, its **ladder** or its **dependencies** is not, because the DoD has no
clause for those four. That asymmetry is the shape of this whole lens.

---

## §4 · Refused

- **`WS-238` as a dangling screen citation.** It is the fenced next-free allocation marker declared by
  `SCENARIO-CATALOGUE.md`-style convention and already recorded as `X-001`. Filing it would be a
  restatement.
- **"P5 and P6 task files carry no screen contract" as a standalone finding.** Drafted, then
  withdrawn. Only 3 of 33 name a grid identifier, but §4/§3.3/§3.5/§7/§8 supply the columns, the
  filters with their buckets and (in §4) the actions, and §0.2 makes the four identifiers mechanical.
  What is genuinely missing from those files is the **verbs' permissions**, filed as `H-001`.
- **"P5/P6 tasks omit export column lists."** `BUILD-SPEC-SCREENS.md` §0.5 and CLAUDE.md both state
  the rule as *grid↔export parity* — a superset of the visible columns — not a fixed list. A task
  that specifies its grid has specified its export.
- **The five P3/P4 tasks with no screen contract.** Read all five headers: `p3-15`
  (*"Screens **— (WS-034 LPNs and every scan surface are the consumers)**"*), `p3-22` (*"WS-056 and
  WS-057 are `P0-11`'s"*), `p3-23` (*"help content attaches to every warehouse screen through the
  platform `HelpButton`"*), `p4-11` (*"the valuation reports of `P2-20`/`P2-21` gain a basis
  dimension"*), `p4-05` (`WS-226 Stock by MRP`). All are behaviour-over-existing-DDL tasks that name
  their consuming screen. Not under-specified.
- **"Mobile is missing from P5/P6."** Drafted from a marker scan whose last alternative matched the
  bare word `mobile`; dumping the matching lines showed all 33 carry a real `**Mobile:**` verdict with
  a stated reason. Reversed, and recorded in §3.
- **"Build-spec screen coverage is incomplete for P5/P6."** Drafted from an `awk` pattern that missed
  merged rows; a raw `grep -n "WS-nnn"` found `| WS-123–126 |`, `| WS-129/130 |`, `| WS-166–168 |`
  and §8.2 for `WS-228`. Coverage is complete. Reversed.
- **"`X-014` is wrong to say §10.2 stops at P0–P2."** It carries three `wh3_` rows, so the sentence is
  imprecise — but the substance of `X-014` holds and the correction is one clause. Noted inside
  `H-001` rather than filed as its own finding.
- **"The v3 exit criterion names capabilities (trips, ePOD, freight settlement) that no task in this
  design set delivers."** True — `p6-08.md:4` disclaims both the schema and the screens — but
  `00-EPIC-master.md:135` already says the criterion *"is therefore prose until `P6` authors it"* and
  `IMPLEMENTATION-PLAN.md` §11 item 3 says `P6-08` *"will not stay one task"*. The set is honest
  about it; filing it would restate a stated decision. The **executable** half of that criterion is
  filed as `H-009`.
- **`is_issue_file()` matching `README.md`.** Latent, harmless, requires someone to add an `issue: NN`
  line to a document that will never have one. Over-engineering to file it.
- **Structural drift between epics** (`## Open decisions that gate …` in four, `## Blocked on
  decisions` in two, `## What Pn deliberately does not do` in four). All nine share the load-bearing
  core — Overview, Exit criterion, Migration blocks, Tasks, Traps, Definition of done. Section-name
  variance is style, and style is not this gate's business. The **invariant** half of that
  observation is substantive and is filed as `H-008`.

---

## §5 · Counts

```bash
f=docs/reviews/R9-task-buildability-v2-and-epics.md
grep -c '^### `H-' $f                    # → 10   findings
grep -c '^### `H-.*BLOCKER\*\*$' $f      # →  0
grep -c '^### `H-.*MAJOR\*\*$' $f        # →  6
grep -c '^### `H-.*MINOR\*\*$' $f        # →  4
```

| Severity | Count | Ids |
|---|---|---|
| **BLOCKER** | 0 | — |
| **MAJOR** | 6 | `H-001` `H-002` `H-003` `H-004` `H-005` `H-006` |
| **MINOR** | 4 | `H-007` `H-008` `H-009` `H-010` |
| **Total** | **10** | |

Relationship to round 1: **6 new** (`H-003` `H-004` `H-005` `H-007` `H-009` `H-010`), **4 material
extensions** (`H-001`→`X-014`, `H-002`→`OD-7`,
`H-006`→`X-044`, `H-008`→`X-050`). Ten candidates refused, two of them reversals of my own drafts.

**The blunt answer.** Tasks that pass even three of the thirteen gates — a column spec, a stated
dependency, and one permission string:

```bash
pass=0; for f in issues/p3-*.md issues/p4-*.md issues/p5-*.md issues/p6-*.md; do
  c=$(grep -cE 'CREATE TABLE|VARCHAR\(|NUMERIC\(' "$f")
  d=$(grep -ciE 'depends on|prerequisite|blocked by|must land (first|before)' "$f")
  p=$(grep -ocE '\b(whb|wh|wh3|whad|whas|whaf|whaa|whin)_[a-z_]+:[a-z_]+\b' "$f")
  [ "$c" -gt 0 ] && [ "$d" -gt 0 ] && [ "$p" -gt 0 ] && pass=$((pass+1)); done; echo $pass
# → 2   (p4-03, p4-10)
```

Both are false positives: `p4-03.md:74` and `p4-10.md:100` match on prose about *other* tables
(`wms_stock_transactions.reason_code VARCHAR(50)`; the `permission_dependencies` `CREATE TABLE`
warning). **0 of 68.** And **0 of 9** epics carry a build order, so no phase can be scheduled from
its own front door either.

---

## Appendix A · Per-task completeness matrix — all 68 tasks

`Y` = present and usable · `~` = present but thin · `N` = absent.
Produced by a marker scan (`/tmp/matrix.sh`, reproduced below), calibrated against **12** task files
read in full (`p3-01`, `p3-02`, `p3-12`, `p3-14`, `p3-15`, `p3-22`, `p3-23`, `p4-02`, `p4-05`,
`p4-11`, `p5-05`, `p6-08`). Two columns are asserted rather than scanned because I verified them by
reading: **Col** is `N` for all 68 (`H-002` — the nine marker hits are prose about other tables), and
**Mob** below reflects the `**Mobile`-only pattern, so the P3/P4 `| Mobile |` screen-contract rows
read as `N`; the corrected verdict is in `H-010` — 64 of 68 declare one. **A marker scan is evidence
of shape, not of quality**; where shape and reading disagreed, the reading won and is recorded in §4.

```bash
for f in issues/p3-*.md issues/p4-*.md issues/p5-*.md issues/p6-*.md; do
  printf '%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s\n' "$(basename $f .md)" \
    "$(grep -ocE '`(whb|wh|wh3|whad|whas|whaf|whaa|whae|whin|log)_[a-z0-9_]+`' $f)" \
    "$(grep -cE 'VARCHAR\(|NUMERIC\(|DECIMAL\(|NOT NULL|CREATE TABLE' $f)" \
    "$(grep -ciE 'valid(at|ity)|@NotBlank|@Size|@Pattern|uniqueness|must be|reject' $f)" \
    "$(grep -cE '[A-Z][A-Z_]{2,} *(→|->) *[A-Z][A-Z_]{2,}' $f)" \
    "$(grep -ocE '\b(whb|wh|wh3|whad|whas|whaf|whaa|whin)_[a-z_]+:[a-z_]+\b' $f)" \
    "$(grep -ciE 'Grid identifier|gridIdentifier' $f)" "$(grep -cE 'WAREHOUSE_[A-Z_]+' $f)" \
    "$(grep -ci 'export' $f)" "$(grep -ciE 'filter-aware, FR-395|dropdown\.|CacheConfiguration' $f)" \
    "$(grep -ciE 'i18n|SafeTranslation' $f)" "$(grep -cE '\*\*Mobile' $f)" \
    "$(grep -ocE 'WH-SC-[0-9]{3}' $f)"; done
```

| Task | Tbl | Col | Val | State | Perm | Grid | Filt | Exp | Cache | i18n | Mob | Scen |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `p3-01` | N | N | N | N | N | N | N | Y | N | Y | N | Y |
| `p3-02` | Y | N | ~ | N | Y | Y | Y | N | Y | N | Y | Y |
| `p3-03` | Y | N | N | N | Y | Y | Y | Y | Y | N | Y | Y |
| `p3-04` | N | N | N | N | N | Y | N | N | N | Y | N | Y |
| `p3-05` | Y | N | N | N | Y | Y | Y | Y | Y | N | Y | Y |
| `p3-06` | Y | N | Y | N | Y | Y | Y | Y | Y | N | Y | Y |
| `p3-07` | Y | N | N | N | Y | Y | Y | Y | Y | N | Y | Y |
| `p3-08` | Y | N | N | N | Y | Y | Y | Y | Y | N | Y | N |
| `p3-09` | Y | N | N | N | N | Y | Y | N | Y | N | Y | Y |
| `p3-10` | Y | N | ~ | N | Y | Y | Y | Y | Y | N | Y | Y |
| `p3-11` | Y | N | N | N | Y | Y | Y | Y | Y | N | Y | Y |
| `p3-12` | Y | N | Y | N | Y | Y | Y | Y | Y | N | Y | Y |
| `p3-13` | Y | N | ~ | N | Y | Y | Y | Y | Y | N | Y | Y |
| `p3-14` | Y | N | N | N | N | N | N | N | N | N | N | Y |
| `p3-15` | Y | N | N | N | N | N | N | N | N | N | N | Y |
| `p3-16` | Y | N | Y | N | Y | Y | Y | Y | Y | N | Y | Y |
| `p3-17` | Y | N | N | N | Y | Y | Y | Y | Y | N | Y | Y |
| `p3-18` | Y | N | Y | N | Y | Y | Y | Y | Y | N | Y | N |
| `p3-19` | Y | N | N | N | Y | Y | Y | Y | Y | N | Y | Y |
| `p3-20` | Y | N | N | N | Y | Y | Y | Y | Y | N | Y | Y |
| `p3-21` | Y | N | N | N | Y | Y | Y | Y | Y | N | Y | N |
| `p3-22` | Y | N | ~ | N | Y | N | N | N | N | N | N | Y |
| `p3-23` | Y | N | N | N | N | N | N | Y | N | Y | N | Y |
| `p4-01` | Y | N | ~ | N | Y | N | Y | Y | Y | N | Y | Y |
| `p4-02` | Y | N | N | N | Y | Y | Y | Y | Y | N | Y | Y |
| `p4-03` | Y | N | ~ | N | Y | Y | Y | Y | Y | N | Y | Y |
| `p4-04` | Y | N | ~ | N | Y | Y | Y | Y | Y | N | Y | Y |
| `p4-05` | Y | N | Y | N | Y | Y | Y | Y | Y | N | Y | Y |
| `p4-06` | Y | N | N | N | Y | Y | Y | Y | Y | N | Y | Y |
| `p4-07` | Y | N | Y | N | Y | Y | Y | Y | Y | N | Y | N |
| `p4-08` | Y | N | ~ | N | Y | Y | Y | Y | Y | N | Y | Y |
| `p4-09` | Y | N | Y | N | Y | Y | Y | Y | Y | N | Y | Y |
| `p4-10` | Y | N | N | N | Y | Y | Y | Y | Y | N | Y | Y |
| `p4-11` | Y | N | ~ | N | N | N | N | N | N | N | N | N |
| `p4-12` | Y | N | Y | N | Y | Y | Y | Y | Y | N | Y | Y |
| `p5-01` | Y | N | Y | N | N | N | N | Y | Y | Y | Y | Y |
| `p5-02` | Y | N | ~ | Y | N | N | N | Y | N | Y | Y | Y |
| `p5-03` | Y | N | ~ | N | N | N | N | Y | Y | N | Y | Y |
| `p5-04` | Y | N | N | N | N | N | N | N | Y | N | Y | Y |
| `p5-05` | Y | N | Y | Y | N | N | N | Y | N | N | Y | Y |
| `p5-06` | Y | N | N | N | N | N | N | N | N | N | Y | Y |
| `p5-07` | Y | N | N | N | N | N | N | Y | N | N | Y | Y |
| `p5-08` | Y | N | N | N | N | Y | N | Y | Y | N | Y | Y |
| `p5-09` | Y | N | Y | N | N | N | N | N | N | N | Y | Y |
| `p5-10` | Y | N | N | N | N | N | N | N | N | N | Y | Y |
| `p5-11` | Y | N | Y | N | N | N | N | Y | N | N | Y | Y |
| `p5-12` | Y | N | ~ | N | N | N | N | Y | N | N | Y | Y |
| `p5-13` | Y | N | N | N | N | N | N | N | N | N | Y | Y |
| `p5-14` | Y | N | ~ | N | N | N | N | Y | N | N | Y | Y |
| `p5-15` | Y | N | N | N | N | N | N | N | N | N | Y | Y |
| `p5-16` | Y | N | Y | N | N | N | N | Y | Y | N | Y | Y |
| `p5-17` | Y | N | Y | N | N | N | N | Y | N | N | Y | Y |
| `p5-18` | Y | N | ~ | N | N | N | N | N | N | N | Y | Y |
| `p5-19` | Y | N | ~ | N | N | N | N | Y | N | N | Y | Y |
| `p5-20` | Y | N | ~ | N | N | Y | N | N | N | N | Y | Y |
| `p5-21` | Y | N | ~ | N | N | N | N | N | N | N | Y | Y |
| `p6-01` | Y | N | Y | N | N | N | N | N | N | N | Y | Y |
| `p6-02` | Y | N | ~ | N | N | N | N | N | N | N | Y | Y |
| `p6-03` | Y | N | ~ | N | N | N | N | N | Y | N | Y | Y |
| `p6-04` | Y | N | ~ | N | N | N | N | N | N | N | Y | Y |
| `p6-05` | Y | N | N | N | N | N | N | N | N | N | Y | Y |
| `p6-06` | Y | N | ~ | N | N | N | N | N | N | N | Y | N |
| `p6-07` | Y | N | Y | N | N | N | N | N | N | N | Y | Y |
| `p6-08` | Y | N | Y | N | N | N | Y | N | Y | Y | Y | Y |
| `p6-09` | Y | N | N | N | N | N | N | N | N | N | Y | N |
| `p6-10` | N | N | ~ | N | N | Y | N | Y | Y | Y | Y | Y |
| `p6-11` | Y | N | ~ | N | N | N | N | Y | N | N | Y | N |
| `p6-12` | Y | N | N | N | N | N | N | N | N | N | Y | N |

**How to read the columns.** `Tbl` — does the task name the tables it creates (67 of 68 do; `p3-01`
scores `N` because it names nine *screens*, correctly). `Col` — column types/nullability/defaults
(`H-002`, 0 of 68). `Val` — validation rules beyond "must be valid". `State` — an enumerated
transition ladder (`H-004`, 2 of 68 and both prose). `Perm` — at least one `resource:action` string
(`H-001`; 28 of 35 in P3/P4, **0 of 33** in P5/P6). `Grid` / `Filt` — a grid identifier and a
`WAREHOUSE_` filter scope (mostly delegated to `BUILD-SPEC-SCREENS.md` §0.2/§4, refused in §4).
`Exp` / `Cache` / `i18n` — delegated to the master epic's Definition of done, refused in §4.
`Mob` — see the caveat above; the real count is 64 of 68 (`H-010`). `Scen` — cites a `WH-SC-nnn`
(the nine that do not are honest `None.` declarations, §3).

**The three columns that decide buildability are `Col`, `State` and `Perm` — and they read
`0/68`, `2/68` and `35/68`.** Everything else in this table is either present or legitimately
delegated. That is the whole finding set in one row.

---

## Appendix B · Per-epic assessment — all 9 epics

| Epic | Checklist matches glob? | Exit criterion fully delivered by its own tasks? | §5.1 amendments reflected? | `L-n` invariants carried? | Build order? | Factually correct? |
|---|---|---|---|---|---|---|
| `00-EPIC-master` | n/a (links the 8) | n/a — states the ladder, does not own tasks | **Y** — all four `A-1`…`A-4` | **Y** — all 14 named | **N** — no cross-phase order beyond the ladder | **Y** |
| `01-EPIC-p0` | **Y** 17/17 | **Y** — `WH-SC-044`…`049` all owned | **N** — cites none | **Y** — 15 distinct, with a dedicated section | **N** | **Y** |
| `02-EPIC-p1` | **Y** 20/20 | **Y** — `WH-SC-050`…`055` all owned | **N** — cites none; **owns half of `A-3`** | ~ — 2, with a dedicated section | **N** | **Y** |
| `03-EPIC-p2` | **Y** 29/29 | **Y** — `WH-SC-056`…`062` all owned | **Y** — `A-1`, `A-2` (its own two) | **N** — zero `L-n` | **N** | **Y** |
| `04-EPIC-p2in` | **Y** 4/4 | **Y** — `WH-SC-206`…`213` all owned | **Y** — `A-4` | ~ — 1 | **N** | **Y** |
| `05-EPIC-p3` | **Y** 23/23 | **Y** — `WH-SC-227` → `p3-01` (all nine RF screens); `WH-SC-228` → `p3-02`/`p3-06`/`p3-12`; `FR-424`/`FR-425` owned. **Best-specified phase in the set** | ~ — `A-2` only | ~ — 2, no section | **N** (`H-003`) | **Y**, but `WH-SC-228` rests on a v1 schema fact neither owner states (`H-005`) |
| `06-EPIC-p4` | **Y** 12/12 | **Y** — `WH-SC-239` → `p4-02`, `WH-SC-240` → `p4-03`; reproducibility clause in `p4-02`/`p4-03`/`p4-08` | **Y** — `A-4` | ~ — 1 | **N** (`H-003`) | **Y** |
| `07-EPIC-p5` | **Y** 21/21 | **Y** — `WH-SC-234` → `p5-03`/`p5-05`; all three §1.7 clauses owned; correctly records `P5-01 → P4-10` as the only cross-phase edge | **N** — cites none; **owns half of `A-3`** | ~ — 1 | **N** (`H-003`) | **N** — "Thirteen" vs 15 ids; `V500064`/`V500065` called unclaimed (`H-007`) |
| `08-EPIC-p6` | **Y** 12/12 | **~** — the criterion is prose the phase authors (`p6-08` is *"not decomposed"*); the one executable half, the zero-commit ratchet, is stated in a form its own phase falsifies (`H-009`) | **N** — cites none | **N** — zero `L-n` | **N** (`H-003`) | **N** — allocates `V524000`–`V524099` to `P6-08`, which `p6-08.md:4` withdraws; fenced output stale (`H-006`) |

**Totals.** Checklist ↔ glob: **9 of 9 correct** — `X-046` has no content-level twin. Exit criterion
follows from the phase's own tasks: **7 of 8 phases yes**, P6 partially and by design. Amendments:
**4 of 8 phase epics cite none**, and `A-3` reaches no phase epic (`H-008`). Invariants: **2 of 8**
have a dedicated section; 2 cite zero. Build order: **0 of 9**. Factually correct throughout:
**7 of 9** — `07-EPIC-p5` and `08-EPIC-p6` are not.

---

*End of R9. Findings `H-001`…`H-010`. Nothing in this document was written to any file other than
this one; no source, migration, task file or document in the design set was modified.*
