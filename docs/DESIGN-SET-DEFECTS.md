# DESIGN-SET-DEFECTS — the merged defect log

<!-- check-design-set: scenario-citations file WH-SC-306 — the allocation marker from SCENARIO-CATALOGUE.md §5 rule 3, not a scenario. X-006 established it and X-040 reports the checker's false positives on it. Round 2 took WH-SC-301-WH-SC-305 for SCENARIO-CATALOGUE.md 3.21, so the marker — and this declaration with it — moved to WH-SC-306 -->
<!-- check-design-set: finding-citations file T-244 T-264 T-325 T-326 T-337 E-754 E-1 E-8 — the eight dangling citations X-045 reports and §4.2 gives the citation rule for. Quoted as evidence, never used as references -->
<!-- check-design-set: screen-citations file WS-238 — the screen id X-001's fix allocates; BUILD-SPEC-SCREENS.md §1 has not yet carried the row -->

> **This file replaces two.** `issues/DEFECTS-FOUND.md` and `docs/DEFECTS-FOUND.md` were written
> concurrently by four authoring passes that could not see each other. Both said so in their own
> preambles and both asked to be merged. **They are merged here with no loss** — every entry is
> reproduced verbatim, re-identified into one `X-nnn` namespace, and §0 maps every old id to its new
> one so nothing already cited dangles.
>
> **Append-only from here.** Add a section; never rewrite one. If two authors find the same defect,
> file both and cross-reference — `X-010`/`X-033` and `X-007`/`X-034` are exactly that, and the
> duplication is itself evidence that the defect is real.

| | |
|---|---|
| **Date merged** | 2026-09-02 |
| **Sources** | `issues/DEFECTS-FOUND.md` (29 entries, three authoring passes) · `docs/DEFECTS-FOUND.md` (9 entries, the P5/P6 pass) — **both deleted on merge** |
| **New in the merge** | `X-039`…`X-053`, filed while writing [`GAP-REGISTER.md`](GAP-REGISTER.md) |
| **New in review round 2** | `X-054` and `X-055`, filed 2026-09-02 — while regenerating `DATA-MODEL.md` §8.4, and while authoring `WH-SC-301`. **55 entries in total** — `ls` is not the count; `grep -c '^### `X-0' docs/DESIGN-SET-DEFECTS.md` is |
| **Total** | **55** defects — **7** BLOCKER · **28** MAJOR · **20** MINOR. *The row previously read 53 / 8 / 25 / 20, which summed correctly to 53 but matched no count in the file; recomputed 2026-09-02 with the command below* |
| **Severity command** | ``awk '/^### `X-/{if(f)print s; f=1; s=""} f{if(s=="" && match($0,/(BLOCKER\|MAJOR\|MINOR)/)) s=substr($0,RSTART,RLENGTH)} END{if(f)print s}' docs/DESIGN-SET-DEFECTS.md \| sort \| uniq -c`` — **entries `X-039`…`X-053` carry their severity in the heading and the rest carry it in the quote block**, so a grep of `> **Severity**` alone returns 39, not 55. The `f` flag matters too: without it the §0 total row above is itself counted as a BLOCKER |
| **Companion** | [`GAP-REGISTER.md`](GAP-REGISTER.md) — §3 of that document is where the computed failures below come from |

**Severity, as used here.** **BLOCKER** — it breaks the build, breaks a startup, or leaves a
requirement with nowhere to live. **MAJOR** — it costs a rebuild cycle or produces a wrong number in
a document that outranks the reader. **MINOR** — real, deferrable, and recorded so it is not
rediscovered.

**Status, as used here.** **FIXED** — the fix is applied and the file is named. **OPEN** — nothing
has been changed; a human must edit a document. **REFERRED** — the decision belongs to a named owner
and no author may take it unilaterally.

---

## §0 · Concordance — old id → new id

Nothing that already cites an old id dangles: every one of the 38 resolves.

| Old id | Source file | New id | Severity |
|---|---|---|---|
| `D-P5-1` | `docs/DEFECTS-FOUND.md` | **`X-001`** | BLOCKER |
| `D-P5-2` | `docs/DEFECTS-FOUND.md` | **`X-002`** | MAJOR |
| `D-P5-3` | `docs/DEFECTS-FOUND.md` | **`X-003`** | MAJOR |
| `D-P5-4` | `docs/DEFECTS-FOUND.md` | **`X-004`** | MINOR |
| `D-P5-5` | `docs/DEFECTS-FOUND.md` | **`X-005`** | MINOR |
| `D-P56-6` | `docs/DEFECTS-FOUND.md` | **`X-006`** | MAJOR |
| `D-PLAN-7` | `docs/DEFECTS-FOUND.md` | **`X-007`** | MAJOR |
| `D-DOC-8` | `docs/DEFECTS-FOUND.md` | **`X-008`** | MINOR |
| `D-DOC-9` | `docs/DEFECTS-FOUND.md` | **`X-009`** | MINOR |
| `D-P4-1` | `issues/DEFECTS-FOUND.md` | **`X-010`** | BLOCKER |
| `D-P4-2` | `issues/DEFECTS-FOUND.md` | **`X-011`** | MAJOR |
| `D-P4-3` | `issues/DEFECTS-FOUND.md` | **`X-012`** | MAJOR |
| `D-P4-4` | `issues/DEFECTS-FOUND.md` | **`X-013`** | MAJOR |
| `D-P3-1` | `issues/DEFECTS-FOUND.md` | **`X-014`** | MAJOR |
| `D-P3-2` | `issues/DEFECTS-FOUND.md` | **`X-015`** | MINOR |
| `D-P3-3` | `issues/DEFECTS-FOUND.md` | **`X-016`** | MINOR |
| `D-P01-1` | `issues/DEFECTS-FOUND.md` | **`X-017`** | BLOCKER |
| `D-P01-2` | `issues/DEFECTS-FOUND.md` | **`X-018`** | MINOR |
| `D-P01-3` | `issues/DEFECTS-FOUND.md` | **`X-019`** | MAJOR |
| `D-P01-4` | `issues/DEFECTS-FOUND.md` | **`X-020`** | MAJOR |
| `D-P01-5` | `issues/DEFECTS-FOUND.md` | **`X-021`** | MINOR |
| `D-P01-6` | `issues/DEFECTS-FOUND.md` | **`X-022`** | MAJOR |
| `D-P01-7` | `issues/DEFECTS-FOUND.md` | **`X-023`** | MINOR |
| `D-P01-8` | `issues/DEFECTS-FOUND.md` | **`X-024`** | BLOCKER |
| `D-P01-9` | `issues/DEFECTS-FOUND.md` | **`X-025`** | MAJOR |
| `D-P01-10` | `issues/DEFECTS-FOUND.md` | **`X-026`** | MAJOR |
| `D-P2-01` | `issues/DEFECTS-FOUND.md` | **`X-027`** | BLOCKER |
| `D-P2-02` | `issues/DEFECTS-FOUND.md` | **`X-028`** | MAJOR |
| `D-P2-03` | `issues/DEFECTS-FOUND.md` | **`X-029`** | BLOCKER |
| `D-P2-04` | `issues/DEFECTS-FOUND.md` | **`X-030`** | MAJOR |
| `D-P2-05` | `issues/DEFECTS-FOUND.md` | **`X-031`** | MINOR |
| `D-P2-06` | `issues/DEFECTS-FOUND.md` | **`X-032`** | MINOR |
| `D-P2-07` | `issues/DEFECTS-FOUND.md` | **`X-033`** | BLOCKER |
| `D-P2-08` | `issues/DEFECTS-FOUND.md` | **`X-034`** | MAJOR |
| `D-P2-09` | `issues/DEFECTS-FOUND.md` | **`X-035`** | MINOR |
| `D-P2-10` | `issues/DEFECTS-FOUND.md` | **`X-036`** | MAJOR |
| `D-P2-11` | `issues/DEFECTS-FOUND.md` | **`X-037`** | MINOR |
| `D-P2-12` | `issues/DEFECTS-FOUND.md` | **`X-038`** | MINOR |
| — | filed 2026-09-02 in the merge | **`X-039`…`X-053`** | see §2 |
| — | filed 2026-09-02 in review round 2 | **`X-054`**, **`X-055`** | see §2.1 |

**Two pairs are the same defect found twice, independently.** Both members are preserved because the
second finding is corroboration, not noise:

| Pair | The defect | Why both are kept |
|---|---|---|
| `X-010` ≡ `X-033` | `INDIA-LOCALISATION-PACK.md` §11.2's wave-2 blocks land on `DATA-MODEL.md` §7.6's `WIN-30` config block | `X-010` names the mechanism (`Dockerfile.backend:140-181` flattens all modules into one directory, so it is a **startup failure**); `X-033` carries the fuller five-row collision table |
| `X-007` ≡ `X-034` | `IMPLEMENTATION-PLAN.md` §8.5 states 119 scenarios; the same page's command returns 300 — **both FIXED 2026-09-02**, §8.5 now states 305 | `X-007` additionally proves §8.5's *v1 exit decomposition* command is wrong (`/^### 3\.2/` matches `### 3.20`); `X-034` confirms the stated `19` is nevertheless correct |

### 0.1 The two source files' own preambles, preserved

`issues/DEFECTS-FOUND.md` opened:

> **Written here, in `issues/`, because this authoring pass was scoped to `warehouse-issues/issues/`
> and told to modify nothing outside it.** A sibling file with the same name and the same purpose now
> exists at **`docs/DEFECTS-FOUND.md`**, created by the P5/P6 authoring pass at 07:41 on 2026-09-02
> — after this pass had already checked for one and found none. **The two are complementary, not
> duplicates:** that file carries `D-P5-n` / `D-P56-n` / `D-PLAN-n` / `D-DOC-n`, this one carries
> `D-P3-n` / `D-P4-n`, and no id collides. **Merge them with a single `cat`**, or move this content
> under that file's heading — whichever the maintainer prefers. Do not leave both unlinked.
>
> **Append-only.** Several authors write here concurrently; add a section, never rewrite one.
> Every entry names the two documents that disagree, what the task files did instead, and what a
> human must decide. `DECISIONS.md` §7 rule 3 exists because the sibling design set shipped 25
> dangling cross-references of which 19 resolved to a *different* real requirement, so live gaps read
> as closed.

`docs/DEFECTS-FOUND.md` opened:

> Author: the P5/P6 issue-authoring pass (`issues/p5-*.md`, `issues/p6-*.md`, `issues/07-EPIC-p5.md`,
> `issues/08-EPIC-p6.md`, `issues/00-EPIC-master.md`).
> **Appended, not overwritten** — other authors are writing to this repository concurrently.
>
> Every defect below is **fixed in the issue files** (the fix is named in the affected task's `## Traps`
> and `## Acceptance`) rather than carried silently. Each names the smallest fix and where it was applied.

### 0.2 The four authoring passes, and their section preambles — preserved verbatim

The two source files carried the title lines and per-pass preambles below. They are reproduced here
because they record *which pass found what and under which authority order*, which the per-entry
**Originally** line alone does not.

**`issues/DEFECTS-FOUND.md`** was titled *"# Defects found while authoring the task files"* and
carried three pass headings:

**`## From the P3 / P4 authoring pass — 2026-09-02`** — entries `X-010`…`X-016`:

> Authority order applied throughout: `DECISIONS.md` wins on modules, prefixes, bands, the version
> ladder and the phase map · `DATA-MODEL.md` wins on **any table or column name** and on migration
> allocation · `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` wins on what a requirement says ·
> `reviews/R1` wins on what the existing `classic` codebase does.

**`## From the P0 / P1 authoring pass — 2026-09-02`** — entries `X-017`…`X-026`:

> Authority order applied throughout: `DECISIONS.md` wins on modules, prefixes, bands, the version
> ladder and the phase map · `IMPLEMENTATION-PLAN.md` §2 is the authority on **what the tasks are**
> (the caller's instruction) · `DATA-MODEL.md` wins on **any table or column name** and on migration
> allocation · `IRREVERSIBLE.md` wins on deadlines · `reviews/R1` wins on what the existing `classic`
> codebase does.
>
> **Verified clean before anything else, by command, so the sections below are not padding:**
>
> ```bash
> # every FR owned exactly once — 138 tasks, 446 FRs, 0 double-owned, 0 unowned
> # every migration number owned exactly once — 914 numbers allocated, 0 collisions, 0 out of band
> # every FR cited by SCENARIO-CATALOGUE.md resolves to a real requirement — 0 dangling
> ```
>
> All three pass. The plan's §8 traceability claims hold. What follows is everything that does not.

*(All three still pass, with one correction: the migration count is **915**, not 914 — see `X-042`.)*

**`## Filed while authoring **P2** and **P2-IN** (2026-09-02)`** — entries `X-027`…`X-038`.

**`docs/DEFECTS-FOUND.md`** was titled
*"# Defects found while authoring the P5 and P6 issue files — 2026-09-02"* — entries `X-001`…`X-009`.

### 0.3 Old heading text, preserved

Every original heading's **title** survives verbatim after the new id in §1 — e.g.
`## \`X-010\` · **Migration-block collision** — \`INDIA-LOCALISATION-PACK.md\` §11.2 against
\`DATA-MODEL.md\` §7.6 and \`BUILD-SPEC-SCREENS.md\` §0.9` is `D-P4-1`'s heading with `D-P4-1`
replaced by `X-010`. Nothing else in any heading changed.

---

## §1 · The 38 merged entries

### `X-001` · `FR-279` has no table and no screen, and `P5-13` is its sole owner — **BLOCKER**

> **Severity** BLOCKER · **Status** **PARTLY FIXED, re-measured 2026-09-02 (review round 2)** — the *table* half is closed, the *screen* half is not · **Originally** `D-P5-1`, from `docs/DEFECTS-FOUND.md` (the P5/P6 authoring pass)
>
> - **FIXED** in `issues/p5-13.md`; in `DATA-MODEL.md` — `wh_marketplace_claims` is a real row (§2.1.9, `WH-115`, `V510215`, `grep -c '`wh_marketplace_claims`' docs/DATA-MODEL.md` → **3**); and in `IMPLEMENTATION-PLAN.md` §2.7, whose `P5-13` row now reads `` `V510210` · `V510215` ``.
> - **STILL OPEN** in `BUILD-SPEC-SCREENS.md` §1 (`grep -c 'WS-238' docs/BUILD-SPEC-SCREENS.md` → **0**), in its §8.4 count (**237**, which must become 238 in the same edit), and in `IMPLEMENTATION-PLAN.md` §2.7's screens cell, still `` `WS-137` `WS-138` ``. Round 2 did not touch any of the three. `WS-238` is exempted in six files and is the subject of §6.4 **`R-1`** — that entry, not this one, is the live to-do.

**Claim.** `IMPLEMENTATION-PLAN.md` §2.7 assigns `FR-279` (the marketplace return-claim window) to
`P5-13`, whose migrations are `V510210` and whose screens are `WS-137` and `WS-138`.

**Evidence.**
- `DATA-MODEL.md` §7.3 `WH-110` `V510210` creates exactly `wh_return_gradings`,
  `wh_obsolescence_returns`, `wh_obsolescence_return_lines` — none of them a claim object.
- `grep -n "marketplace_claim\|wh_marketplace\|return_claim" DATA-MODEL.md BUILD-SPEC-SCREENS.md` → **0**.
- The only carrier of the window is `wh_return_receipts.claim_due_at` (`DATA-MODEL.md`, v1, `P2-12`),
  which gives the **clock and the queue** and nothing else.
- `FR-279` additionally requires *a claim type, photographic evidence, a claim amount and a settlement*.
- `BUILD-SPEC-SCREENS.md` §1 allocates **237** screen ids and `IMPLEMENTATION-PLAN.md` §8.4 verifies
  *"claimed by no task: none"* — so no unallocated screen exists for the claim queue either.

**Impact.** A requirement is owned by a task that has nowhere to put half of it. Built as-is, the claim
window would either be omitted or bolted onto `wh_return_gradings`, which is a different object with a
different clock.

**Fix applied in `issues/p5-13.md`.** `P5-13` claims **`V510215`** — the first number of
`DATA-MODEL.md` §7.3's *"Reserved: 785 numbers for DDL corrections during the app build"* — for
`wh_marketplace_claims`, and allocates the queue a **new** screen id in `BUILD-SPEC-SCREENS.md` §1 in the
same PR (the next free is `WS-238`). The task explicitly forbids reusing WS-137's grid for it.

**Follow-up for the plan owner.** `IMPLEMENTATION-PLAN.md` §2.7's `P5-13` row and §2.9's divergence list
need the number; `DATA-MODEL.md` §7.3 needs the `WH-` row; `BUILD-SPEC-SCREENS.md` §1 and §8.4's count
need the screen.

---

### `X-002` · `FR-445`'s ratio-pack template has no table, and `P5-20` has no migration — **MAJOR**

> **Severity** MAJOR · **Status** FIXED in `issues/p5-20.md` · **OPEN** in `DATA-MODEL.md` §7.2 · **Originally** `D-P5-2`, from `docs/DEFECTS-FOUND.md` (the P5/P6 authoring pass)

**Claim.** §2.7 gives `P5-20` (`FR-445`, ratio and assortment packs) migrations `—` and screens
`WS-032`/`WS-033`.

**Evidence.**
- The variant model is present: `whb_item_variant_axes` and `whb_item_variant_axis_values` at
  `V500014` (`WHB-14`), and `whb_items.style_item_id` + `variant_axis_1/2/3_value_id`.
- `grep -n "pack_template\|ratio\|assortment" DATA-MODEL.md` finds **no** pack-template table.
- `FR-445` requires *"a pack template naming a quantity per variant"* — which spans N variants and so is
  neither an item attribute nor `whb_item_packaging_levels` (a pack hierarchy of **one** item).

**Impact.** The screens can be built on the v1 schema; the pack itself cannot be received or shipped as
one line without somewhere to define it.

**Fix applied in `issues/p5-20.md`.** `P5-20` claims a number inside `DATA-MODEL.md` §7.2's **declared**
`V500064`–`V500199` post-v1 base DDL gap for `whb_ratio_pack_templates` + `_lines`, and records the row
in §7.2 in the same PR. The task also fixes the balance rule
(`MUST_BALANCE_PER_OWNER_ITEM`, not `MUST_BALANCE_PER_MOVEMENT`).

---

### `X-003` · `FR-343`'s per-counterparty packaging balance has no table, and `P5-21` has no migration — **MAJOR**

> **Severity** MAJOR · **Status** FIXED in `issues/p5-21.md` · **OPEN** in `DATA-MODEL.md` §7.2 · **Originally** `D-P5-3`, from `docs/DEFECTS-FOUND.md` (the P5/P6 authoring pass)

**Claim.** §2.7 gives `P5-21` migrations `—` while assigning it `FR-343`.

**Evidence.**
- `grep -n "packaging_balance\|counterparty_balances" DATA-MODEL.md` → **0**.
- R7 `G-024` marks the **counterparty balance** explicitly as *new* relative to R4 `F-060`, which covers
  *packaging as stock* only: *"R4 `F-060` covers packaging as stock; the **counterparty balance** is new
  (`G-024`)."*
- A balance per party with a deposit is not a stock position — it is an open-item balance against a
  counterparty, so `whb_stock_positions` cannot carry it.

**Fix applied in `issues/p5-21.md`.** `P5-21` claims a number in the same declared `V500064`–`V500199`
base gap for `whb_packaging_balances` + a movement-linked entry table, recorded in §7.2 in the same PR.

---

### `X-004` · `FR-338`'s four movement types may need a seed, and `P5-21` has no migration to carry one — **MINOR, verify first**

> **Severity** MINOR · **Status** FIXED in `issues/p5-21.md` (verify-first acceptance step) · **REFERRED** to the `DATA-MODEL.md` owner: enumerate `WHB-03`’s fourteen movement types · **Originally** `D-P5-4`, from `docs/DEFECTS-FOUND.md` (the P5/P6 authoring pass)

**Evidence.** `DATA-MODEL.md` §7.2 `WHB-03` (`V500003`) says *"`whb_movement_types` + seed of the 14 types
and their reversal counterparts, incl. `FR-046`'s four value-only types"* — **without enumerating the
fourteen**. `FR-338` needs `ISSUE_TO_ASSET`, `RETURN_FROM_ASSET`, `EQUIPMENT_ISSUE`, `EQUIPMENT_RETURN`,
which `PORT-AND-ADAPTER-CONTRACT.md` §9.7 names as logistics-posted types and R7 §6 item 7 marks
irreversible-if-an-enum. They are catalogue **rows** (`D-10`), so a missing one is a seed `INSERT` — but
`P5-21` has no migration number allocated to carry it.

**Fix applied in `issues/p5-21.md`.** The task's first acceptance step is to **verify** the four are
among `V500003`'s fourteen; if they are not, it takes a number from the same `V500064`–`V500199` gap.
**Recommendation for the plan owner:** enumerate the fourteen in `DATA-MODEL.md` §7.2's `WHB-03` row, so
this is answerable by reading rather than by grepping a migration that does not exist yet.

---

### `X-005` · `P5-01`'s `V531000`–`V531099` is a sub-allocation §2.9 does not record — **MINOR**

> **Severity** MINOR · **Status** FIXED in `issues/p5-01.md` and `issues/07-EPIC-p5.md` · **OPEN** in `IMPLEMENTATION-PLAN.md` §2.9 · **Originally** `D-P5-5`, from `docs/DEFECTS-FOUND.md` (the P5/P6 authoring pass)

**Evidence.** §2.7's `P5-01` row claims `V531000`–`V531099`; `DATA-MODEL.md` §7.5 `W3-20` declares
`V531000`–`V531199`. §2.9 opens *"Six. None renumbers an allocated block; all five sub-allocations
subdivide a block §7 already declared as a range"* and enumerates the sub-allocations for `WHB-74`,
`WH-203` and `WIN-30` — **but not this one**.

**Impact.** Low today; the sub-allocation is legal under §7.1 rules 1 and 2. It matters because §2.9
presents itself as **complete**, and a later 3PL config task taking `V531100`+ without a recorded row is
how double-ownership arrives.

**Fix applied in `issues/p5-01.md` and `issues/07-EPIC-p5.md`.** Both state that `P5-01` claims the first
hundred and that `V531100`–`V531199` is deliberately left free.

---

### `X-006` · Twenty P5/P6 requirements have no scenario, and §10's definition of done requires walking one — **MAJOR, process**

> **Severity** MAJOR · **Status** FIXED across `issues/p5-*.md`, `issues/p6-*.md`, `07-EPIC-p5.md`, `08-EPIC-p6.md` · **OPEN**: `IMPLEMENTATION-PLAN.md` §10 still assumes the scenarios exist · **Originally** `D-P56-6`, from `docs/DEFECTS-FOUND.md` (the P5/P6 authoring pass)

**Evidence.**
- `awk -F'|' '/^\| \*\*WH-SC-/ {gsub(/ /,"",$9); print $9}' SCENARIO-CATALOGUE.md | sort | uniq -c` →
  96 `v1·P0` · 71 `v1·P1` · 101 `v1·P2` · 5 `v1·P2-IN` · 17 `v1.1·P3` · 3 `v2·P4` · **7 `v2·P5`** ·
  **no `v3·P6` row at all**.
- `SCENARIO-CATALOGUE.md` §4.2 lists the unproven requirements honestly and most of P5's and all of P6's
  are on it.
- `IMPLEMENTATION-PLAN.md` §10 requires *"the `WH-SC-nnn` scenarios the task claims to close are **walked
  in the running app**"* — so 20 of the 33 P5/P6 tasks have nothing to walk, and **v3's exit criterion is
  prose with no scenario behind it**, while v1, v1.1 and v2's are all scenario-backed (§5 rule 5).

**This is not a fabrication by the catalogue** — §4.2 is explicit and even names the right remedy for
`FR-023`: *"Write it with the v3 task, not before."* The defect is that **the plan does not say who
authors them or when**, and §10 silently assumes they exist.

**Fix applied across `issues/p5-*.md`, `issues/p6-*.md`, `07-EPIC-p5.md`, `08-EPIC-p6.md`.**
Every affected task authors its own scenarios as its **first act**, with the minimum set named in the task
file. Four P6 tasks author **none, by design**, and say why (`P6-06`, `P6-09`, `P6-11`, `P6-12`) — which
§5 rule 1 permits for infrastructure proved by an architecture test.
**And an allocation rule, because the collision is obvious:** new ids continue from **`WH-SC-306`**
(§5 rule 3) and parallel P5/P6 tasks will all take the same one. *(The marker read `WH-SC-301` when
this defect was filed; review round 2 took `WH-SC-301`–`WH-SC-305` for §3.21 on 2026-09-02 and moved
it — which is the rule working, not an exception to it.)* Both phase epics state the rule — **claim ids by
merging them into `SCENARIO-CATALOGUE.md` in one commit before writing code; the catalogue file is the
allocation register and nothing else is.**

---

### `X-007` · `IMPLEMENTATION-PLAN.md` §8.5 states 119 scenarios; its own stated command returns 300 — **MAJOR, and §8.5 claims nothing on it was counted by eye**

> **Severity** MAJOR · **Status** **FIXED, 2026-09-02** — `IMPLEMENTATION-PLAN.md` §8.5 now states **305** (the value its own command returns after review round 2 added §3.21's five scenarios) and the *v1 exit decomposition* row now carries `/^### 3\.2 /,/^### 3\.3 /` with the trailing spaces, which returns the stated **19**; without them it returns **35**, because `### 3.20` and `### 3.21` both match. Was FIXED in `issues/00-EPIC-master.md` and OPEN in the plan. Same defect as `X-034` · **Originally** `D-PLAN-7`, from `docs/DEFECTS-FOUND.md` (the P5/P6 authoring pass)

**Evidence, run 2026-09-02 from the repo root:**

```bash
grep -cE '^\| \*\*WH-SC-[0-9]{3}\*\*' docs/SCENARIO-CATALOGUE.md      # → 300   (§8.5 states 119)
grep -oE 'WH-SC-[0-9]+' docs/SCENARIO-CATALOGUE.md | sort -u | wc -l  # → 301   (the extra is §5 rule 3's
                                                                      #          forward reference to WH-SC-301)
```

`SCENARIO-CATALOGUE.md` §4.1's own total is **300**, and §1.2 gives the same command. So §8.5's row
disagrees with the document it cites **by 181**, under the heading *"The counts on this page, and where
each came from"* and the closing line *"Nothing on this page was counted by eye."*

**Impact.** Any downstream document quoting §8.5 states a scenario count that is wrong by a factor of
two and a half. The master epic quotes **300**, computed, and says so.

**Also in §8.5, and smaller:** the command given for *"scenarios in the v1 exit decomposition"* is
`awk '/^### 3\.2/,/^### 3\.3/' … | grep -cE '^\| \*\*WH-SC-'`, which returns **30**, not the stated 19 —
because `/^### 3\.2/` also matches **`### 3.20`**. **The stated value 19 is correct** (§4.1 agrees, and
`WH-SC-044`…`WH-SC-062` is 19 ids); it is the **command** that is wrong. Suggested replacement:
`awk '/^### 3\.2 /,/^### 3\.3 /'` (note the trailing spaces).

**Fix applied in `issues/00-EPIC-master.md`.** It states 300 with the command, and flags the §8.5
disagreement inline rather than silently choosing.

---

### `X-008` · `PORT-AND-ADAPTER-CONTRACT.md` §9.7 and R7 §7 place the `logistics` module at v2; `DECISIONS.md` §5 and the plan place it at v3 — **MINOR, cross-document**

> **Severity** MINOR · **Status** **REFERRED** — annotate `PORT-AND-ADAPTER-CONTRACT.md` §9.7 and R7 §7; `DECISIONS.md` §5 wins and `P6-08` is correctly placed · **Originally** `D-DOC-8`, from `docs/DEFECTS-FOUND.md` (the P5/P6 authoring pass)

**Evidence.**
- `PORT-AND-ADAPTER-CONTRACT.md` §9.7 heading: *"The future `logistics` module · **v2 posting, v3
  optimisation**"*, and its Version row: *"**v2** — the module; **v3** — optimisation, telematics, control
  tower, spot bidding."*
- R7 §7's sequencing table puts *"**v2** — the `logistics` module itself"*.
- `DECISIONS.md` §5 puts *"the `logistics` module itself"* in **v3**, and its adapter schedule says
  *"logistics **v3**"*.
- `IMPLEMENTATION-PLAN.md` §1.8 / §2.8 puts it in **P6 / v3**.

**Resolution.** `DECISIONS.md` wins by its own preamble — *"a document that disagrees with this one is
wrong"* — so **v3 is correct** and `P6-08` is correctly placed. The port contract's §9.7 row and R7 §7
should be annotated, exactly as `DECISIONS.md` §5.1 annotates the four ladder amendments, so a reader who
finds the port contract first does not plan a v2 logistics module.

**No fix was needed in the issue files**; `issues/p6-08.md` and `08-EPIC-p6.md` both cite the v3
placement and the port contract's §9.7 content without repeating its version claim.

---

### `X-009` · `GAP-REGISTER.md` does not exist, so "every finding is dispositioned" is an intention — **MINOR, already self-reported**

> **Severity** MINOR · **Status** **FIXED by `docs/GAP-REGISTER.md`**, 2026-09-02. The residual is `X-048`: `tools/check-design-set.py` still has no disposition check · **Originally** `D-DOC-9`, from `docs/DEFECTS-FOUND.md` (the P5/P6 authoring pass)

`DECISIONS.md` `D-12` states that *"every one of the 575 findings is dispositioned into a task in
`GAP-REGISTER.md`, and `tools/check-design-set.py` fails if any finding is untraced."*
`ls docs/GAP-REGISTER.md` → **absent**, and `IMPLEMENTATION-PLAN.md` §11 item 5 already says so plainly:
*"Until it exists, 'every finding is dispositioned' is an intention, not a computed fact — and it is
exactly the class of claim that the accounting programme's post-mortem says looked finished and was
not."*

Recorded here only so the P5/P6 files' `## Closes` blocks are understood as the **substitute**: every
P5 and P6 task names the `C-`/`T-`/`E-`/`F-`/`S-`/`P-`/`G-` ids it discharges, which is what makes the
register reconstructible by `grep` from `issues/` if it is never written.

---

### `X-010` · **Migration-block collision** — `INDIA-LOCALISATION-PACK.md` §11.2 against `DATA-MODEL.md` §7.6 and `BUILD-SPEC-SCREENS.md` §0.9

> **Severity** BLOCKER · **Status** **OPEN** — a duplicate Flyway version is a backend **startup failure**, not a merge conflict. Someone must edit one document. Same defect as `X-033` · **Originally** `D-P4-1`, from `issues/DEFECTS-FOUND.md`

`INDIA-LOCALISATION-PACK.md` §11.2 allocates **wave-2 DDL** to `V541000`–`V548999`, group by group:
A = `V541000`–`V541099`, B = `V541100`–`V541199`, C = `V541200`–`V541299`, D = `V541300`–`V541399`,
F = `V542000`–`V542099`, G = `V543000`–`V543199`, H = `V544000`–`V544199`, I = `V545000`–`V545099`,
J = `V546000`–`V546099`, K = `V547000`–`V547199`, L = `V547500`–`V547599`.

`DATA-MODEL.md` §7.6 `WIN-30` allocates **`V541000`–`V541199` to permissions, `permission_dependencies`,
menus, grid configuration and `admin_settings`**, and `BUILD-SPEC-SCREENS.md` §0.9 repeats it. It puts
**all** wave-2 DDL in `V540100`–`V540180`. `IMPLEMENTATION-PLAN.md` §2.9 row 3 then sub-allocates
`V541000`–`V541049` to `P2-IN-01` and `V541100`–`V541149` to `P4-01`.

**So `INDIA-LOCALISATION-PACK.md`'s groups A and B land on top of the config block, and B lands
exactly on `P4-01`'s range.** All module migrations are physically flattened into one directory at
build time (`Dockerfile.backend:140-181`), so a duplicate version is a **backend startup failure**,
not a merge conflict.

**What the P4 files did:** followed `DATA-MODEL.md` §7.6 and `IMPLEMENTATION-PLAN.md` §2.6 exactly.
No P4 task uses a number from `V542000`–`V548999`.
**Decide:** amend `INDIA-LOCALISATION-PACK.md` §11.2's Block column to point at `DATA-MODEL.md` §7.6,
or re-allocate `WIN-30`. Someone must edit one document; the plan's §11 item 2 already files the
**wave-1** half of this divergence (14 tables against 12) and does **not** mention the wave-2 block
collision.

---

### `X-011` · **Table-name divergence** — the same wave-2 tables named two ways

> **Severity** MAJOR · **Status** **OPEN** — task files use the `DATA-MODEL.md` names throughout; **REFERRED** to the doc owner. A blanket search-and-replace is forbidden (`DECISIONS.md` §7 rule 4) · **Originally** `D-P4-2`, from `issues/DEFECTS-FOUND.md`

| `INDIA-LOCALISATION-PACK.md` §11.2 | `DATA-MODEL.md` §7.6 · `BUILD-SPEC-SCREENS.md` §5.2 |
|---|---|
| `whin_job_work_returns` · `whin_itc04_runs` · `whin_itc04_lines` | `whin_job_work_registrations` · `whin_job_work_dispatch_lines` · `whin_itc04_returns` · `whin_itc04_lines` |
| `whin_stock_account_runs` · `whin_stock_account_lines` | `whin_stock_account_periods` · `whin_stock_account_lines` |
| `whin_customs_licences` · `whin_customs_bonds` · `whin_exbond_clearances` | `whin_bonded_licences` · `whin_warehousing_bonds` · `whin_bond_utilisations` · `whin_ex_bond_clearances` |
| `whin_eway_bill_consolidations` · `whin_eway_bill_consolidation_items` | `whin_eway_bills_consolidated` · `whin_eway_bill_consolidated_items` |
| group E: *"no new table"* for approval | `whin_approval_dispatches` · `whin_approval_clocks` (`WIN-18`, `V540150`) |

**What the P4 files did:** used the `DATA-MODEL.md` / `BUILD-SPEC-SCREENS.md` names throughout, per
`BUILD-SPEC-SCREENS.md`'s own authority note (*"`DATA-MODEL.md` wins on any table or column name"*),
and recorded the divergence in each affected task's Traps.
**Decide:** one document must be corrected. A blanket search-and-replace is explicitly forbidden
(`DECISIONS.md` §7 rule 4 — it corrupted the sibling set's decisions table twice).

---

### `X-012` · **Twelve wave-2 tables have no owning task and no migration number**

> **Severity** MAJOR · **Status** **OPEN** — twelve wave-2 tables with no owning task. Group H is the `NEEDS-TASK` BLOCKER `S-035` in `GAP-REGISTER.md` §5.1 · **Originally** `D-P4-3`, from `issues/DEFECTS-FOUND.md`

`INDIA-LOCALISATION-PACK.md` §11.2 lists 42 wave-2 tables. `DATA-MODEL.md` §7.6 lists roughly 30, and
`IMPLEMENTATION-PLAN.md` §2.6's twelve tasks own only what §7.6 carries. **Unowned:**

- **group C** `whin_hsn_summary_runs` · `whin_hsn_summary_lines` — though R3 `D11` says the HSN
  summary *lives in accounting, not here*, so this may be correct by omission and should be stated
- **group D** `whin_tcs_sections` — but `P4-04` needs the TCS rate as a **seed row with effective
  dates**, not a constant, so something must hold it
- **group F** `whin_packaged_commodity_declarations` · `whin_mrp_revisions` ·
  `whin_instrument_verifications`
- **group G**, five of nine: `whin_bill_of_entry_references` · `whin_bill_of_entry_lines` ·
  `whin_exbond_clearance_lines` · `whin_moowr_returns` · `whin_moowr_return_lines` ·
  `whin_sez_movements`. **The BoE reference in particular is what `FR-323`'s *"ex-bond clearance
  consumes an identified bonded quantity"* needs**, and `P4-07` has four tables to hold it in.
- **group H**, all six: `whin_licence_types` · `whin_entity_licences` · `whin_counterparty_licences` ·
  `whin_licence_quantity_ceilings` · `whin_schedule_h1_register` · `whin_recall_notifications`
- **group J**, two of three: `whin_form3cd_runs` · `whin_form3cd_lines` — yet `FR-329` requires *"the
  tax-audit quantitative statement as a built report"*, so `P4-09` must produce it from somewhere

**What the P4 files did:** stated the boundary in `P4-04` (TCS rate as a seed row inside `V540131`'s
scope), `P4-05` (group F declared **unowned**, not silently absorbed), `P4-07` (the BoE reference
modelled inside `V540140`'s four tables, with the divergence flagged) and `P4-09` (the Form 3CD run
and line pair built inside `V540170`'s block, flagged).

---

### `X-013` · **P4's phase description promises two things no `FR-` and no task carries**

> **Severity** MAJOR · **Status** **PARTLY FIXED, 2026-09-02 (review round 2)** — of the two promises, the regulated-goods packs now have a requirement and a task; Legal Metrology still does not · **Originally** `D-P4-4`, from `issues/DEFECTS-FOUND.md`
>
> - **The regulated-goods packs: FIXED.** `GAP-REGISTER.md` §4.1 proposed the task in round 1 and round 2 authored it — [`issues/p4-13.md`](../issues/p4-13.md), `warehouse-india`, `V540182` (`WIN-23`), owning the two requirements written for it, **`FR-456`** and **`FR-457`** (`WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` §6.27). `IMPLEMENTATION-PLAN.md` §2.6 carries its row and `issues/06-EPIC-p4.md` its migration block. **Authoring it does not discharge `S-035`** — the file opens with the gate: the pharma segment is a product decision that has now gone unanswered through two review rounds, and until it is answered the task must not be started. Building it against an undecided segment is the more expensive of the two mistakes.
> - **Legal Metrology: STILL OPEN, and it is a phase-description defect, not an ownership one.** `FR-223` *is* owned — `IMPLEMENTATION-PLAN.md` §2.7 assigns it to **`P5-17`** (`V510213`/`V510214`), and the FRD row reads **`v2` · `P5`**. What has not changed is the four descriptions — `DECISIONS.md` §5's v2 row, `IMPLEMENTATION-PLAN.md` §1.6, `PORT-AND-ADAPTER-CONTRACT.md` §9.6 and `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` §6.18's preamble — which still promise **P4** delivers it. The remaining fix is one sentence in each of the four, moving Legal Metrology from P4 to P5. It is deliberately not folded into `P4-13`: `P4-13` is India licences, and quietly widening its scope to make a stale sentence true is how a task grows past its estimate.
> - The `INDIA-LOCALISATION-PACK.md` §11.2 **group F** tables (`whin_packaged_commodity_declarations`, `whin_mrp_revisions`, `whin_instrument_verifications`) travel with Legal Metrology and therefore stay unowned. §6.4 **`R-5`** is the live entry for them.

`DECISIONS.md` §5's v2 row, `IMPLEMENTATION-PLAN.md` §1.6, `PORT-AND-ADAPTER-CONTRACT.md` §9.6 and
`WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` §6.18's preamble all describe P4 as delivering *"MRP **and
Legal Metrology**, bonded/MOOWR, **and the regulated-goods packs**."*

- **Legal Metrology.** The only requirement is **`FR-223`** — *"a weighing or measuring instrument is
  a legal instrument … a weighing performed on an out-of-verification instrument is flagged on the
  receipt"* — and its `Ver`/`Ph` columns read **`v2` · `P5`**, not P4. `SCENARIO-CATALOGUE.md` §4.2
  confirms it is unproven and lists it under 6.12 Execution and printing. **`P4-05` closes `FR-321`
  only**, which is MRP as a balance dimension — not Legal Metrology.
- **The regulated-goods packs.** `INDIA-LOCALISATION-PACK.md` §11.2 group H is six tables — drug,
  FSSAI, PESO and customs licences with expiry and a despatch guard; per-zone hazmat ceilings; the
  Schedule H1 register; the CDSCO / FSSAI recall notification. **No `FR-nnn` in §6.18 or anywhere else
  covers them**, and no task in §2.6 owns them. §8 of `IMPLEMENTATION-PLAN.md` asserts *"every
  requirement is owned by exactly one task"*, which stays true — because **there is no requirement**.

**What the P4 files did:** `P4-05` states the Legal Metrology boundary explicitly and names group F as
unowned; nothing was invented to fill either gap.
**Decide:** either write the missing `FR-` rows and add tasks, or amend the four phase descriptions to
stop promising them. The second is legitimate — `INDIA-LOCALISATION-PACK.md` §8 already argues that
the segregation matrix, sensors, excursions, FEFO and shelf-life gates are **core, not India** — but
the promise and the task list must agree.

---

### `X-014` · **`BUILD-SPEC-SCREENS.md` §10.2 lists no verb permission for any P3 or P4 transition**

> **Severity** MAJOR · **Status** **OPEN** — the task files derive each permission from the documented convention and mark it absent; §10.2 needs the ~45 rows so the permission migrations have one authority to seed from · **Originally** `D-P3-1`, from `issues/DEFECTS-FOUND.md`

§10.2 opens *"Every one of these gates a transition modal named in §2–§6"* and closes with
*"a transition with no verb permission is a transition anybody with `:edit` can perform, which is the
failure `FR-408` names."* The table covers P0–P2 and the India **v1** documents
(`whin_eway_bills:generate` `:part_b` `:extend` `:cancel`, `whin_delivery_challans:generate`) and the
two v1 adapters — and **stops there**.

Missing, by task: `whb_tasks:assign` · `whb_devices:force_sign_out` · `wh_asns:receive_against`
`:cancel` · `wh_dock_appointments:check_in` `:dock` `:depart` `:no_show` · `wh_waves:release`
`:cancel` · `wh_pack_sessions:complete` · `wh_printers:test_print` ·
`wh_print_routing_rules:test_routing` · `wh_shipping_labels:void` · `wh_work_orders:release`
`:issue_components` `:complete` `:cancel` · `wh_replenishment_tasks:assign` `:cancel` ·
`whb_alert_events:acknowledge` `:resolve` · `wh_migration_mappings:export_profile` `:import_profile` ·
`whad_price_files:dry_run` `:apply` · `whad_oem_orders:transmit` `:acknowledge` `:raise_discrepancy` ·
`whaf_van_stock_assignments:release` · `whaf_van_replenishments:reconcile` ·
`whaa_spare_consumptions:issue` · `whaa_asset_item_links:capitalise` · `whin_tax_rules:simulate` ·
`whin_job_work_registrations:dispatch` `:receive_return` · `whin_itc04_returns:generate`
`:mark_filed` · `whin_stock_account_periods:generate` `:mark_filed` · `whin_itc_reversals:compute`
`:mark_reported` · `whin_approval_dispatches:dispatch` `:receive_return` `:convert_to_sale` ·
`whin_ex_bond_clearances:clear` · `whin_epr_returns:generate` `:mark_filed` ·
`whin_retention_policies:place_legal_hold` `:release_legal_hold` · `whin_compliance_tasks:complete` ·
`whin_eway_bills_consolidated:generate` `:cancel`.

**What the P3/P4 files did:** named each one in its screen-contract table, derived from the documented
convention (permission resource = the table name, format `resource:action`), and marked each as
*"absent from `BUILD-SPEC-SCREENS.md` §10.2 today; see DEFECTS-FOUND"*. **No new convention was
invented.**
**Decide:** add these rows to §10.2, so the permission migrations (`V501101`+, `V511140`+,
`V541100`+, and each adapter's in-band block) have one authority to seed from.

---

### `X-015` · **`FR-211` (seals at load and at unload) is proved by no scenario, and no acceptance test in the catalogue reaches it**

> **Severity** MINOR · **Status** **OPEN** — write one two-line scenario at the next free id (`WH-SC-306` as of 2026-09-02). `P3-05` states `FR-211` is unproven and stands acceptance lines in · **Originally** `D-P3-2`, from `issues/DEFECTS-FOUND.md`

Verified: `grep -E "FR-211\`" SCENARIO-CATALOGUE.md` returns **no `WH-SC-` row**.
`SCENARIO-CATALOGUE.md` §4.2 **does** account for it — the 6.11 Outbound row lists
`FR-208`–`FR-211` among the fifteen unproven requirements, and `FR-211` is indeed in §6.11 of the
FRD (line 385, between `### 6.11` at 347 and `### 6.12` at 387). **So the coverage table is correct
and this is not a bookkeeping defect.**

**It is a gap in the exit criterion, and it is worth recording anyway.** §4.2's justification for
that whole row is *"the carrier, channel and parcel surface … v1.1/v2 rate shopping,
serviceability, AWB pools, NDR, COD, tracking, channel import and publish"* — which describes
`FR-198`–`FR-210` accurately and describes `FR-211` not at all. `FR-211` is a **v1.1 inbound and
dispatch control** (*"seal numbers are captured at load and at unload, and the receiving session
owns the seal, the gate pass, the driver and the arrival photographs"*), it is delivered by
**`P3-05`**, and it is the kind of thing a customer audits. Being bucketed with rate shopping means
nobody will notice it never got a scenario.

**What the P3 files did:** `P3-05` claims only `WH-SC-274` and states plainly that `FR-211` is
unproven, with acceptance lines standing in for the missing scenario.
**Decide:** write one. *"A seal captured at load and a **different** seal recorded at unload"* is a
two-line scenario, it is the entire point of the requirement, and `WH-SC-306` is the next free id.

---

### `X-016` · **`WS-069` Alert Rules is allocated to `FR-383`, but `P3-16` closes `FR-398`**

> **Severity** MINOR · **Status** **OPEN** — `BUILD-SPEC-SCREENS.md` must separate “the FR this screen delivers” from “the rules it obeys”, or an ownership check reads three screens as co-owning `FR-383` · **Originally** `D-P3-3`, from `issues/DEFECTS-FOUND.md`

`BUILD-SPEC-SCREENS.md` §2.9 tags WS-069 with `FR-383` (v1.1) and WS-070 with no FR at all.
`FR-383` is *"no JSONB on any new warehouse business table"*, whose `Ver`/`Ph` is **`v1` · `P0`** and
which `IMPLEMENTATION-PLAN.md` §2 assigns elsewhere. `IMPLEMENTATION-PLAN.md` §2.5 gives `P3-16`
screens `WS-069` `WS-070` `WS-223` and `Closes FR-398`.

This is not an FR owned twice — it is a **screen tagged with the requirement it obeys rather than the
one it delivers**, which reads as an ownership claim. Same shape on WS-074 (`FR-136` `FR-383`) and
WS-101 (`FR-187` `FR-383`).

**What the P3 files did:** `P3-16` closes `FR-398` only, and cites `FR-383` as a **trap** rather than
as a requirement it discharges. `P3-05` and `P3-06` do the same.
**Decide:** in `BUILD-SPEC-SCREENS.md`, separate the *"FR this screen delivers"* column from the
*"rules this screen obeys"* note, or `tools/check-design-set.py`'s ownership check will read three
screens as co-owning `FR-383`.

---

---

### `X-017` · **`whb_owners.counterparty_id` FKs forward into a later migration** — `DATA-MODEL.md` §2.1 against §7.2

> **Severity** BLOCKER · **Status** FIXED in `issues/p0-06.md` + `issues/p1-08.md` (bare `UUID` then `ALTER TABLE ... ADD CONSTRAINT`) · **REFERRED** for ratification, or move `whb_counterparties` into the `V500002`–`V500010` gap · **Originally** `D-P01-1`, from `issues/DEFECTS-FOUND.md`

`DATA-MODEL.md` §2.1's `whb_owners` row declares
`counterparty_id → whb_counterparties`. §7.2 places **`whb_owners` at `V500007`** (`WHB-07`,
`P0-06`) and **`whb_counterparties` at `V500011`** (`WHB-11`, `P1-08`).

Flyway runs `V500007` first, so **the `REFERENCES` clause cannot be written in `V500007`.** All
module migrations are physically flattened into one directory at build time
(`Dockerfile.backend:140-181`), so this is a **backend startup failure**, not a merge conflict — and
the tempting fix (leave `counterparty_id` a bare `UUID` forever) leaves the column pointing at
nothing enforceable, which is **exactly the failure `P-010` records**: the prior art's
`scc_gstin_profiles.scc_company_id` was *"a pointer with no owning table in any module"*
(`V190045:71`).

**What the task files did:** `p0-06.md` creates `counterparty_id` as a **bare nullable `UUID`** in
`V500007`; **`p1-08.md`'s `V500011` adds the `FOREIGN KEY` by `ALTER TABLE whb_owners ADD
CONSTRAINT …` in the same file that creates the target.** Legal, because `V500011` < `V500030`, so it
is inside the pre-`PNR` window. **It renumbers nothing.**
**Decide:** either ratify that split, or move `whb_counterparties` into the `V500002`–`V500010` block
using the deliberate gap. Do **not** drop the FK.

---

### `X-018` · **Two `Dep` cells in `IMPLEMENTATION-PLAN.md` §2 omit `P1-08`**

> **Severity** MINOR · **Status** **OPEN** — amend `IMPLEMENTATION-PLAN.md` §2.1’s two `Dep` cells. The task files already carry `P1-08` · **Originally** `D-P01-2`, from `issues/DEFECTS-FOUND.md`

- **`P0-02`'s `Dep`** reads `P0-04 P0-05 P0-06 P0-07 P0-17 P1-01 P1-02 P1-05 P1-07 P1-09` — no
  `P1-08`. But **§1.2's ★ note, §3.2's `PNR-1` row and §3.3's `PRE` graph node all include `P1-08`.**
  Three places against one.
- **`P0-06`'s `Dep`** reads `P0-04` only, and records **no** dependency on `P1-08` at all — which is
  the concrete edge `D-P01-1` proves exists.

**What the task files did:** carried `P1-08` in both, and stated in `p0-06.md` that *"the plan's Dep
column for `P0-06` should read `P0-04 P1-08`."*
**Decide:** amend §2.1's two `Dep` cells. Note that `P1-08` is **not** a *ledger* FK dependency — the
movement line does not reference a counterparty — so §2.2's omission is defensible on its own terms
and only §3's `PNR-1` list and the `whb_owners` FK make it real.

---

### `X-019` · **`IMPLEMENTATION-PLAN.md` §1.1 says P0 ships fifteen screens; §2.1 assigns thirty-three**

> **Severity** MAJOR · **Status** **OPEN** — `IMPLEMENTATION-PLAN.md` §1.1 (15 screens) against §2.1 (33). Task files follow §2.1 · **Originally** `D-P01-3`, from `issues/DEFECTS-FOUND.md`

§1.1: *"Fifteen screens ship (`WS-001`…`WS-004`, `WS-006`, `WS-008`, `WS-009`, `WS-019`, `WS-020`,
`WS-040`, `WS-041`, `WS-042`, `WS-045`, `WS-046`, `WS-059`)."*

§2.1's `Screens` column names **33 distinct ids**. The eighteen §1.1 omits are `WS-010`, `WS-012`,
`WS-013`, `WS-014`, `WS-015`, `WS-043`, `WS-044`, `WS-047`, `WS-051`, `WS-052`, `WS-053`, `WS-054`,
`WS-055`, `WS-056`, `WS-057`, `WS-058`, `WS-063`, `WS-064`. (The §1.1 list is a strict subset — no id
is in §1.1 and absent from §2.1.)

**What the task files did:** followed **§2.1**, because the caller's instruction makes §2 the
authority on what the tasks are, and because in every one of the eighteen cases the task **writes the
table** the screen sits on — a drift-findings table with no grid is *"an email nobody can act on"*
(`FR-163`), and a dead-letter queue with no grid is the defect `FR-332` names explicitly. Each
affected task file states the disagreement in place.
**Decide:** correct §1.1's count and list, or move the eighteen screens to a later phase in §2.1 and
accept that P0 ships tables without maintenance surfaces.

---

### `X-020` · **`BUILD-SPEC-SCREENS.md` §1's `Ver · Ph` column disagrees with `IMPLEMENTATION-PLAN.md` §2 for 21 screens**

> **Severity** MAJOR · **Status** **OPEN** — 21 screens whose `Ver · Ph` disagrees between `BUILD-SPEC-SCREENS.md` §1 and the plan §2. Knock-on: the phase column picks the grid-config sub-block · **Originally** `D-P01-4`, from `issues/DEFECTS-FOUND.md`

Computed, not eyeballed:

| Task | Screen | §2 assigns | `BUILD-SPEC-SCREENS.md` §1 says |
|---|---|---|---|
| `P0-03` | WS-043, WS-044 | P0 | v1 · P2 |
| `P0-05` | WS-010, WS-013, WS-014 | P0 | v1 · P1 |
| `P0-05` | WS-012 | P0 | v1 · P2 |
| `P0-07` | WS-015 | P0 | v1 · P1 |
| `P0-08` | WS-053, WS-054, WS-055 | P0 | v1 · P2 |
| `P0-09` | WS-047 | P0 | v1 · P2 |
| `P0-11` | WS-056, WS-057, WS-058 | P0 | v1 · P2 |
| `P0-12` | WS-051, WS-052 | P0 | v1 · P2 |
| `P0-13` | WS-063, WS-064 | P0 | v1 · P1 |
| `P1-04` | WS-066, WS-067 | P1 | v1 · P2 |
| `P1-17` | WS-090 | P1 | v1 · P2 |

**What the task files did:** followed **§2** for ownership and named the disagreement inside each of
the ten affected task files, so a builder meets it before writing the grid-config migration rather
than after. **`P1-17` is the one exception and is handled differently:** the plan assigns it the
*schema*, the build spec assigns the *screen* to P2, and both are right — `p1-17.md` therefore ships
`V510031` and **explicitly no screen, no workflow and no grid config**.
**Decide:** reconcile the two columns. Note the knock-on: `BUILD-SPEC-SCREENS.md` §1's phase column
also drives which grid-config sub-block a screen's migration comes from (§2.9 divergence 1 splits
`V501020`–`V501099` across four tasks by phase), so a screen in the wrong phase lands in the wrong
migration block.

---

### `X-021` · **`P1-20`'s `Mod` cell is `app+platform`, but it owns twenty numbers in the `warehouse-base` band**

> **Severity** MINOR · **Status** FIXED for `P1-20` in `issues/p1-20.md` · **OPEN for `P2-29` and `P3-04`**, which the entry itself predicted — see `X-044`, computed · **Originally** `D-P01-5`, from `issues/DEFECTS-FOUND.md`

§2.2 gives `P1-20` `V501050`–`V501069` **and** `V511000`…`V511200`. The first range is
`warehouse-base`'s band (`V500000`–`V509999`), declared as such by §2.9 divergence 1 (*"`WHB-74`
sub-allocated across four tasks"*) and by §1.2's migration-block list (*"`V501050`–`V501069` base
grids, wave 2"*). The `Mod` cell does not say `base`.

**Why it matters mechanically:** a `V501xxx` file must live in
`warehouse-base/backend/src/main/resources/db/migration/`, because `Dockerfile.backend:140-181` copies
each module's directory and the band-to-module mapping is what `WarehouseBaseCouplingTest`'s band
assertion checks. A base-band file authored inside `warehouse/` is an out-of-band migration.

**What the task files did:** `p1-20.md`'s header reads
**`warehouse` + `warehouse-base` + `platform`**, and its Traps section states that the base-band files
live in the base module's migration directory.
**Decide:** amend §2.2's `Mod` cell to `base+app+platform`. The same reading applies to `P2-29` and
`P3-04`, which take the other two sub-blocks.

---

### `X-022` · **`reviews/R1` §8 numbers its eighteen traps `T-1`…`T-18`, colliding with R2's `T-001`…`T-097` finding namespace**

> **Severity** MAJOR · **Status** **OPEN** — an id-namespace hazard. See the id-namespace section below; the task files use the disambiguating citation form · **Originally** `D-P01-6`, from `issues/DEFECTS-FOUND.md`

`DECISIONS.md` §6 assigns **`T-001`…`T-097`** to R2's findings. `reviews/R1-codebase-reality.md` §8
independently numbers its trap table `T-1`…`T-18`. A citation of *"`T-6`"* resolves to **R2 `T-006`**
under §6 and to **R1's `filterUtils.ts` allowlist trap** under §8 — two different things, and both
readings are plausible in context.

This is the **same class of failure** as `DECISIONS.md` §7 rule 4a's warning about R2's two numbering
systems, which already cost four miscitations in the first authoring wave.

**What the task files did:** every reference to an R1 §8 trap is written as **"R1 §8 trap `T-n`"**,
never as a bare `T-n`, and **no R1 §8 trap id appears in a `## Closes` line** — `## Closes` carries
only `C-` (R1), `T-` (R2), `E-`, `F-`, `S-`, `P-` and `G-` ids as `DECISIONS.md` §6 defines them.
**Decide:** either renumber R1 §8's traps (e.g. `CT-1`…`CT-18`), or add a §6 note stating that R1 §8's
`T-n` is a *trap*, not a finding, and must always be cited with its section.

---

### `X-023` · **Three P0/P1 tasks own no scenario, and two `v1·P0` scenarios are owned by P2 tasks**

> **Severity** MINOR · **Status** **OPEN** — three P0/P1 tasks own no scenario; `WH-SC-170`/`WH-SC-213`’s `V·Ph` cells name a phase whose task does not own the primary FR · **Originally** `D-P01-7`, from `issues/DEFECTS-FOUND.md`

Computed by mapping each scenario to the task that owns its **first-listed** `FR`:

- **`P0-10` (tasks)** owns no scenario. `FR-212`/`FR-213` are proved by **`WH-SC-052`**, which
  `P1-15` owns, and by `WH-SC-227`/`WH-SC-230` in `v1.1·P3`.
- **`P0-17` (cost-layer DDL)** owns no scenario **and closes no FR** — that one is deliberate and the
  plan says so (§1's footnote to the phase table).
- **`P1-19` (i18n)** owns none by that rule; `WH-SC-247` cites `FR-431` second and `WH-SC-147` cites
  `FR-381` second.
- **`WH-SC-170`** is marked `v1·P0` but its primary `FR-028` is owned by **`P2-01`**.
- **`WH-SC-213`** is marked `v1·P0` but its primary `FR-304` is owned by **`P2-IN-01`**.

**What the task files did:** stated the gap in place rather than leaving the section blank —
`p0-10.md`, `p0-17.md` and `p1-19.md` each name the downstream scenario that exercises them and say
why their own list is empty. **No scenario id was invented to fill a section.**
**Decide:** whether the catalogue needs a P0-phase scenario for the task object and for the i18n
fallback, and whether `WH-SC-170`/`WH-SC-213`'s `V·Ph` cells should read `P2` / `P2-IN`.

---

### `X-024` · **The partition-key conflict still has no `OD-` id, and `OD-1`…`OD-11` are all taken**

> **Severity** BLOCKER · **Status** **FIXED, 2026-09-02** — numbered **`OD-12`** in `DECISIONS.md` §3, recommendation `occurred_at`, and cited by id in `issues/p0-02.md`. **The decision itself remains open**: its deadline is `V500030`, which is `PNR-1` **and** `PNR-2`. This entry closed the *unnumbered* defect, not the gate · **Originally** `D-P01-8`, from `issues/DEFECTS-FOUND.md`

`IMPLEMENTATION-PLAN.md` §2.10, §7 and §11 item 1 all say the same thing: `FR-022` and
`DATA-MODEL.md` `WHB-30` specify `PARTITION BY RANGE (occurred_at)`; `PLATFORM-DEPENDENCIES.md`
`PD-D5` recommends `posting_date`; **nothing resolves them**, and §7 carries it as an *"unnumbered
gate"* that *"needs an `OD-` row in `DECISIONS.md` before `P0-02` is written."*

That row still does not exist, and `DECISIONS.md` §3 has `OD-1` through `OD-11` allocated, so the
next id is free but unassigned.

**What the task files did:** `p0-02.md` carries it in **Blocked on** as
**`⛔ UNNUMBERED (partition key)`** with both substantive arguments stated —
`occurred_at` is what the as-at query and EPCIS want; `posting_date` is what period close and the
statutory register want; **`L-13` says these are different columns, so the choice is real** — and
records that the task currently follows `FR-022` + `DATA-MODEL.md`. **No id was invented.**
**Decide:** add the `OD-` row. *"A partition key cannot be added to a populated table without a
rewrite"*, and `V500030` is `PNR-1` **and** `PNR-2`.

---

### `X-025` · **`P0-07`'s period-close guard depends on `P0-12`'s table, and no edge in §3 says so** *(observation)*

> **Severity** MAJOR · **Status** FIXED in `issues/p0-07.md` + `issues/p0-12.md` Traps · **OPEN** in `IMPLEMENTATION-PLAN.md` §2.1/§3.7: no dependency edge exists · **Originally** `D-P01-9`, from `issues/DEFECTS-FOUND.md`

`BUILD-SPEC-SCREENS.md` §2.6 gives WS-045's **Soft close / Close / Reopen** modals a guard: each
*"refus[es] while `pendingHandoverCount > 0"*, and that count reads `whb_accounting_handovers`, which
**`P0-12`'s `V500042`** creates. `FR-251` states the same synchronisation obligation.

§2.1 gives `P0-07` a `Dep` of `P0-01` and `P0-12` a `Dep` of `P0-02`. Neither names the other, and
§3.3's graph has no edge between them. **If `P0-07` merges first, the guard reads zero and is
vacuous while reading as enforced** — which is the shape of defect this whole design set is written
against.

**What the task files did:** `p0-07.md` names it in Traps and offers the two honest options —
sequence the tasks, or land the guard behind an explicit flag that `P0-12` flips — and `p0-12.md`
carries the reciprocal note.
**Decide:** add the sequencing constraint to §3.7, or the dependency edge to §2.1.

---

### `X-026` · **`P0-12` cannot add the two columns its own feature needs** *(not a plan defect — a deadline that must be read across two task files)*

> **Severity** MAJOR · **Status** FIXED in `issues/p0-12.md` + `issues/p0-02.md`. **Not a plan defect** — a cross-task obligation that no single task file would have carried · **Originally** `D-P01-10`, from `issues/DEFECTS-FOUND.md`

`FR-232` puts **`handover_id`** and **`posting_status`** on the movement. The movement is
`whb_stock_movements`, created **and sealed against `UPDATE`** by `P0-02`'s `V500030`. So the columns
must be in **`V500030`**, written by a task that does not own the feature, or **every movement written
before the fix has `posting_status = NULL` forever and no backfill exists** (`IRREVERSIBLE.md` §3.1,
`IRR-41`).

This is not a contradiction between documents — `DATA-MODEL.md` §2.1 lists both columns on the header
correctly — but it is a **cross-task obligation that no single task file would have carried** if each
had been written in isolation.

**What the task files did:** `p0-12.md` states it under Traps and instructs that `V500030` be
reviewed for `IRR-41` **before it merges**; `p0-02.md` lists `IRR-41` in its deadline table. The
same pattern is recorded for `P1-03`'s catch-weight columns (`IRR-35`) and `P0-17`'s
`moving_average_after` (`IRR-39`).
**Decide:** nothing — but a reviewer of `V500030` must hold `IRREVERSIBLE.md` §3.4's row list open,
not this issue.

---

### `X-027` · `FR-195`'s gate pass has no v1 host screen — **BLOCKER for `P2-IN-04`**

> **Severity** BLOCKER · **Status** FIXED in `issues/p2in-04.md` (the guard rides `WS-105` Dispatch and `WS-090` Dispatch) · **OPEN** in `BUILD-SPEC-SCREENS.md` §5.1, which names a v1.1 screen as the v1 host · **Originally** `D-P2-01`, from `issues/DEFECTS-FOUND.md`

`FR-195` (*the gate pass is e-way-bill-conditional*) is **v1 · P2-IN**, and its two scenarios
`WH-SC-210` / `WH-SC-211` are both **v1 · P2-IN**. `BUILD-SPEC-SCREENS.md` §5.1 says *"That gate
lives on WS-111 (Handovers)"* — but **`WS-111` is `v1.1 · P3`** (`BUILD-SPEC-SCREENS.md` §1 index),
and `wh_handovers` is created at **`V510104`, WH-94, v1.1** (`DATA-MODEL.md` §7.3).

`grep -rn "gate pass\|gate_pass\|gatePass" docs/*.md` finds **no v1 gate-pass object anywhere**:
`wh_handovers.gate_pass_ref` is v1.1 and `wh_receiving_sessions`' gate pass is **inbound**
(`FR-211`, v1.1 · P3).

**Resolution taken in `p2in-04.md`:** in v1 the e-way-bill precondition is a **guard on the two
outward dispatch actions that do exist** — `WS-105` Shipments → **Dispatch** (`P2-10`) and `WS-090`
Transfer Orders → **Dispatch** (`P1-17` schema / `P2-02` workflow) — **contributed by
`warehouse-india`**, so it is absent on a Mode-A install. `P3`'s WS-111 gate pass inherits the same
guard when it lands. **`BUILD-SPEC-SCREENS.md` §5.1's sentence should be corrected to name the v1
surfaces.**

---

### `X-028` · `WS-179` lists an *Extend validity* action whose table is wave 2

> **Severity** MAJOR · **Status** FIXED in `issues/p2in-04.md` (v1 ships four transitions, not five) · **OPEN** in `BUILD-SPEC-SCREENS.md` §5.1 · **Originally** `D-P2-02`, from `issues/DEFECTS-FOUND.md`

`BUILD-SPEC-SCREENS.md` §5.1 gives WS-179 *"**five** transitions, five modals"* including
**Extend validity**. But `whin_eway_bill_extensions` is **`WIN-10`, `V540100`, v2**
(`DATA-MODEL.md` §7.6), and `INDIA-LOCALISATION-PACK.md` §4.2 rules explicitly:
*"**Part-B update and cancellation are wave 1** because you cannot legally leave a wrong bill live;
**extension and consolidation are wave 2**"* — under its own non-goal that **a schema-only statutory
flow is a compliance claim we cannot honour**.

**Resolution taken in `p2in-04.md`:** **v1 ships four transitions** — Generate Part-A · Fill Part-B ·
Update vehicle · Cancel — and the screen states that extension and consolidation are v2.

---

### `X-029` · The value-offset virtual location has two names, and `FR-084` seeds neither

> **Severity** BLOCKER · **Status** **FIXED, 2026-09-02** — numbered **`OD-13`** in `DECISIONS.md` §3, recommendation `VALUE_OFFSET` plus a row in `FR-084`'s seeded list, and cited in `issues/p1-05.md`, `issues/p2-17.md` and `issues/p2-28.md`. **The decision itself remains open** and one code must be agreed **before `P1-05` writes `V500013`** · **Originally** `D-P2-03`, from `issues/DEFECTS-FOUND.md`

- `DECISIONS.md` `OD-11` and `IMPLEMENTATION-PLAN.md` `P2-28` call it **`VALUE_OFFSET`**.
- `PORT-AND-ADAPTER-CONTRACT.md` `PC-12` calls it **`LANDED_COST_OFFSET`** and offers *"the reuse of
  an `ADJUSTMENT_OFFSET`-typed location"* as an alternative.
- **`FR-084`'s seeded virtual-location list contains neither** — it seeds `SUPPLIER`, `CUSTOMER`,
  `ADJUSTMENT`, `SCRAP`, `PRODUCTION`, `IN_TRANSIT`, `COUNT_VARIANCE`, `OPENING_BALANCE`, `CONSUMED`,
  `JOB_WORKER`. `PC-12` says so itself.

A migration author following one document seeds a row the other document's code will not find.
**One code must be agreed before `P1-05` writes `V500013`.** Recorded in `p2-17.md` and `p2-28.md`.

---

### `X-030` · There is no `L-15` and no `I-n` row for value conservation

> **Severity** MAJOR · **Status** **FIXED, 2026-09-02** — numbered **`OD-14`** in `DECISIONS.md` §3, recommendation *a fifteenth invariant `L-15` with a matching `I-21`*, and cited in `issues/p2-17.md`, `issues/p2-28.md` and `issues/p3-11.md`. **The rows are still not allocated** — §4 stops at `L-14` and §6.3 at `I-20` — because allocating them is the decision, and it is due before `P0-02` · **Originally** `D-P2-04`, from `issues/DEFECTS-FOUND.md`

`DECISIONS.md` §4's invariant table stops at **`L-14`** and `DATA-MODEL.md` §6.3's constraint table
stops at **`I-20`**; neither carries a value-conservation row. `PC-12` states plainly that whether
`value_balance_rule` is *"a movement-type behaviour column or a fifteenth invariant is a
`DECISIONS.md` question and is raised in §12, not decided here"*. **It is still not decided**, and
`P2-17`, `P2-28` and `P3-11` all depend on the answer. `IMPLEMENTATION-PLAN.md` §7 sets the deadline
at **before `P0-02`**, because the guard is a constraint on the table.

---

### `X-031` · `P2-28` and `P2-17` are missing a dependency on `P1-05`

> **Severity** MINOR · **Status** FIXED in the task files · **OPEN** in `IMPLEMENTATION-PLAN.md` §2.3’s `Dep` cells · **Originally** `D-P2-05`, from `issues/DEFECTS-FOUND.md`

`IMPLEMENTATION-PLAN.md` §2.3 gives `P2-28` the dependencies `P2-16 P0-02` and `P2-17` the
dependency `P2-16`. Both **post through the value-offset virtual location**, which is seeded by
**`P1-05`'s `V500013`** (`FR-084`), and `I-17` requires virtual locations to exist before a movement
can balance. **`P1-05` belongs in both dependency lists.** Both task files state it.

---

### `X-032` · `IRREVERSIBLE.md` §7.3 item 1 is stale and will re-open a settled decision

> **Severity** MINOR · **Status** **OPEN** — mark `IRREVERSIBLE.md` §7.3 item 1 superseded by the rewritten `D-6`. Flagged in `issues/p2-16.md` · **Originally** `D-P2-06`, from `issues/DEFECTS-FOUND.md`

§7.3 records *"where the cost-layer tables live (`IRR-38`, `IRR-39`, `IRR-40`)"* as one of *"two placements
this document could not resolve, and did not guess"*, and says the table placement *"is `OD-1`/`OD-6`
territory and needs closing before `P2`"*.

It was written **before `D-6` was rewritten**. `DECISIONS.md` `D-6` now states that warehouse runs
the costing engine, and `DATA-MODEL.md` §2.1 and §7.2 place `whb_valuation_policies`,
`whb_cost_layers` and `whb_cost_layer_consumptions` in **`warehouse-base` at `V500021`**.
A `P2-16` author reading `IRREVERSIBLE.md` first would re-open a closed decision. Flagged in
`p2-16.md`; **§7.3 item 1 should be marked superseded.**

---

### `X-033` · `INDIA-LOCALISATION-PACK.md` §11's migration blocks collide with `DATA-MODEL.md` §7.6

> **Severity** BLOCKER · **Status** **OPEN** — the same block collision as `X-010`, found independently by the P2-IN pass with a fuller table. Both entries are preserved · **Originally** `D-P2-07`, from `issues/DEFECTS-FOUND.md`

| Object | India pack §11 | `DATA-MODEL.md` §7.6 | Collision |
|---|---|---|---|
| `whin_delivery_challans` | `V540100`–`V540119` | **`V540020`** | `V540100` is **`WIN-10`, wave 2** — `whin_eway_bill_vehicle_updates` |
| `whin_eway_bills` | `V540200`–`V540229` | **`V540030`** | — |
| provider stack | `V540300`–`V540349` | **`V540011`–`V540012`** | — |
| wave-1 permissions / grids | `V540400`–`V540499` | **`V541000`–`V541199`** (`WIN-30`) | — |
| wave-2 group A (job work / ITC-04) | `V541000`–`V541099` | `V541000`–`V541199` is **wave-1 config** | **direct collision** |

`IMPLEMENTATION-PLAN.md` §1.4 already declares `DATA-MODEL.md` the migration authority and files the
*table-set* and *table-name* divergences (§11 item 2); **the block collision is additionally filed
here**, because §11.2's `V541000`–`V541099` and `WIN-30`'s `V541000`–`V541199` are the same numbers
for different tables, and all module migrations are flattened into one directory at build time
(`Dockerfile.backend:140-181`) — a duplicate version is a **startup failure**.
The P2-IN task files use `DATA-MODEL.md`'s numbers throughout.

---

### `X-034` · `IMPLEMENTATION-PLAN.md` §8.5 states 119 scenarios; its own command returns 300

> **Severity** MAJOR · **Status** **FIXED, 2026-09-02** with `X-007` — §8.5 now states **305**, recomputed. The same count defect as `X-007`, found independently; both entries are preserved · **Originally** `D-P2-08`, from `issues/DEFECTS-FOUND.md`

§8.5's traceability table reads *"Scenarios | **119** | `grep -cE '^\| \*\*WH-SC-[0-9]{3}\*\*'
docs/SCENARIO-CATALOGUE.md`"*. Run against the current file:

```
grep -cE '^\| \*\*WH-SC-[0-9]{3}\*\*' docs/SCENARIO-CATALOGUE.md          # → 300
grep -oE 'WH-SC-[0-9]{3}' docs/SCENARIO-CATALOGUE.md | sort -u | wc -l    # → 301
```

The 301st is `WH-SC-301`, which is legitimate — `SCENARIO-CATALOGUE.md:685` reserves it as the
*"new scenarios start from"* marker. *(Both numbers moved on 2026-09-02: the same two commands now
return **305** and **306**, review round 2 having authored §3.21's five scenarios at
`WH-SC-301`–`WH-SC-305` and moved the marker to `WH-SC-306`. The reasoning is unchanged — the count
of defined rows and the count of distinct ids differ by exactly the marker.)* **The 119 is stale.** `DECISIONS.md` §7 rule 1 —
*never state a count you did not compute* — makes this exactly the class of claim the programme is
designed against. §8.5's row should be recomputed, and §8.5's *"Scenarios in the v1 exit
decomposition | 19"* row is **correct**.

---

### `X-035` · `D-9` / `FR-370`'s counts differ from the computed figures

> **Severity** MINOR · **Status** FIXED in `issues/p2-27.md` (carries the computed table and its commands) · **OPEN** in `D-9`/`FR-370`, which still quote 17 tables and 33 mobile screens · **Originally** `D-P2-09`, from `issues/DEFECTS-FOUND.md`

`D-9` and `FR-370` say *"17 duplicated tables … 33 mobile screens"*. `COEXISTENCE.md` §1.1/§1.2
compute, with commands: **19** inventory-scoped `accessory_*` tables (R1's own table enumerates 19;
its rows compound `_items`/`_history`/`_imports` siblings), and **33 `accessory*` mobile screens
of which 14 are inventory**. §8.1 reconciles the table count — *"the underlying surface is identical
and the budget conclusion is unchanged"* — but does not reconcile the mobile figure, where **33 is
the total and 14 is the duplicated-inventory subset**.

`p2-27.md` carries the full computed table with its commands and instructs the builder to quote the
computed figure, never the headline.

---

### `X-036` · `M3`, the union valuation report, still has no `OD-` row and its deadline has arrived

> **Severity** MAJOR · **Status** **FIXED, 2026-09-02** — numbered **`OD-15`** in `DECISIONS.md` §3, recommendation *do not build the union in v1*, and cited by id in `issues/p2-27.md`. **The decision itself remains open** and its deadline has arrived: it is due before `P2-20` and `P2-27` merge · **Originally** `D-P2-10`, from `issues/DEFECTS-FOUND.md`

`COEXISTENCE.md` §8.2: R3 `M3`/`E-084` says build it; R7 §4.6 item 4 says do not and document the
separation in the UI instead; **`DECISIONS.md` settles neither**, and §8.2 flags that it needs an
`OD-` row with the deadline *"before the `P2` reports task is written"* — **which is now**.
`COEXISTENCE.md` correctly does **not** allocate an id, because `DECISIONS.md` owns that namespace.
Carried as a `## Blocked on` in `p2-27.md` and in `03-EPIC-p2.md`'s open-decisions list.
**It needs a numbered row in `DECISIONS.md` §3 before `P2-20` and `P2-27` merge.**

---

### `X-037` · `COEXISTENCE.md` §5 `M6` is superseded by `A-4` and `FR-308` and should say so

> **Severity** MINOR · **Status** **OPEN** — `COEXISTENCE.md` §5 `M6` is superseded by `A-4` and `FR-308`; `p2in-04.md` and `04-EPIC-p2in.md` state the divergence rather than taking it silently · **Originally** `D-P2-11`, from `issues/DEFECTS-FOUND.md`

`COEXISTENCE.md:487-499`, `:558` place `whin_delivery_challans` **and** `whin_transport_details` in
`warehouse-india` at **v2 / P4**, *explicitly as a correction of R3's v1.1*. Two things have moved
since:

1. **`A-4` is later than that correction** and puts the challan in **v1 / P2-IN**.
   `INDIA-LOCALISATION-PACK.md` §2.3 already records that `M6` *"needs the same pass"*.
2. **The transport block is `wh_`, not `whin_`.** `FR-308` places `wh_transport_details` at module
   `base·app`, v1, and `INDIA-LOCALISATION-PACK.md` §4.2 gives the `D-8` reason — *a vehicle number
   is not an Indian rule* — and says the divergence *"should be recorded there in the reconciliation
   pass, not resolved silently in a migration"*. `DATA-MODEL.md` §7.2 agrees: `whb_transport_details`
   at `V500052`.

Recorded here so the reconciliation pass has it. `p2in-04.md` and `04-EPIC-p2in.md` state the
divergence rather than taking it silently.

---

### `X-038` · `P2-29` owning ~80 grid-config migrations contradicts §3.6's own sequencing rule

> **Severity** MINOR · **Status** FIXED by the reading stated in `issues/p2-29.md` · **REFERRED**: `IMPLEMENTATION-PLAN.md` §2.3 and §3.6 still read as contradicting each other · **Originally** `D-P2-12`, from `issues/DEFECTS-FOUND.md`

`IMPLEMENTATION-PLAN.md` §2.3 pre-allocates `V501070`–`V501099` and `V511060`–`V511139` to `P2-29`
alone. §3.6 and §3.7 state the opposite rule for the same work: *"config work is the classic thing
deferred to the end of a phase; a grid without its `grid_preferences` row and its `filterUtils`
scope **looks built and is not usable**, so it is scheduled with its screens, not after them."*

**Reading taken in `p2-29.md`, stated in the file rather than assumed:** `P2-29` owns the **two
bands**, the **two rules** (export follows visible columns; filter-aware statistics carry no cache
name), the **streaming export path** and the **ratchets**; **each grid's own migration is authored by
the task that creates its table**, claiming one number inside the band and recording it in that
task's header. `P2-29`'s completion criterion is that every P2 grid has a number, a row, a scope, an
API parameter and a translation.

---
## §2 · Filed by command — the fifteen the merge computed, plus one from review round 2

Each of these was found by running a traceability command rather than by reading a document, which is
why no authoring pass caught them: they are *between* documents, not inside one.

**`X-039`…`X-053`** were computed while writing [`GAP-REGISTER.md`](GAP-REGISTER.md) on 2026-09-02.
**`X-054`** was found on the same date by review round 2, while regenerating `DATA-MODEL.md` §8.4 —
and it is the first entry in this log whose subject is a *generated block that drifted from its
sibling*, a failure mode no existing check can see. **`X-055`** was found in the same round while
authoring `WH-SC-301`: the quality-inspection rollup has **two different stored values** across five
documents. §2.1 separates both.

---

### `X-039` · `IMPLEMENTATION-PLAN.md` §2 assigns `FR-224` and `FR-225` to no task, while §8.1 asserts every requirement is owned — **MAJOR**

> **Status** **FIXED, verified 2026-09-02 (review round 2)** — §2.3's `P2-14` row now closes `` `FR-224` `FR-225` `` (`docs/IMPLEMENTATION-PLAN.md:468`), which is what `issues/p2-14.md` always claimed. `python3 tools/check-design-set.py` check-10 reports **0**, and §8.5's owned-exactly-once figure is recomputed each round from the task files rather than from §2.
>
> **The fix was to the plan, not to the task file** — the defect's own reading. Recorded here rather than deleted, per the append-only rule in the preamble.

**Evidence.** `python3 tools/check-design-set.py`, check-10:

```
docs/IMPLEMENTATION-PLAN.md:374: FR-224 is defined in the FRD but no §2 task row closes it
docs/IMPLEMENTATION-PLAN.md:374: FR-225 is defined in the FRD but no §2 task row closes it
issues/p2-14.md:73: P2-14 claims FR-224 FR-225, which §2's `Closes` column does not assign to it
```

§8.1 is headed *"Every requirement is owned by exactly one task"* and §8.5 records **446 owned exactly
once**. Computed from §2 it is **444**. Computed from the task files it is **446** — `issues/` is
correct and the plan is stale.

**Why these two.** `FR-224` is `A-2`'s printing requirement — *"Printing is infrastructure and it has
an owner, and it lands in v1"* — and `FR-225` is its sibling. They were **created by a ladder
amendment after §2 was written**, and §2 was never revisited. So the plan's own traceability section
certifies 446/446 while its task table covers 444.

**Impact.** `S-087` is R5 §7.1 **ship-blocker #2** (*"nothing prints a label"*). A reader who plans
from §2 rather than from `issues/` does not schedule it.

---

### `X-040` · `tools/check-design-set.py` check-2 reports the scenario **allocation marker** as 29 dangling citations — **MINOR, a checker defect**

> **Status** **OPEN** — exempt the marker id, or teach the checker what a marker is. *(The declarations exist and pass; the checker still has no concept of a marker, so each allocation re-writes all 31 of them — see `X-040`'s note below and 2026-09-02's `WH-SC-301`→`WH-SC-306` move.)*

**Evidence.**

```bash
python3 tools/check-design-set.py | grep -c 'WH-SC-301'   # → 26 of check-2's 26 failures
```

*(29 before this file replaced the two defect logs, which cited the marker three times between them.
This file and `GAP-REGISTER.md` both declare a narrow `scenario-citations file WH-SC-306` exemption (it named
`WH-SC-301` until 2026-09-02),
which the checker prints on every run — the remaining 26 are in `issues/` and the catalogue and are
the defect.)*

`SCENARIO-CATALOGUE.md:685` §5 rule 3 reserves `WH-SC-301` as the *"new scenarios start from"* marker.
It is deliberately **not** a scenario, and the 29 citations — in `p5-05`…`p6-10`, both phase epics and
both defect logs — are all instructions to claim the next free id, which is the allocation discipline
`X-006` established.

**Impact.** A CI gate that fails 29 times on a correct pattern is a gate people learn to ignore. The
correct scenario check is:

```bash
comm -13 <(grep -oE '^\| \*\*WH-SC-[0-9]{3}\*\*' docs/SCENARIO-CATALOGUE.md | grep -oE 'WH-SC-[0-9]{3}' | sort -u) \
         <(grep -rohE 'WH-SC-[0-9]{3}' issues/*.md | sort -u)
# → WH-SC-301 only, which is the marker
```

---

### `X-041` · `WH-SC-204` is a real scenario that no task claims — **MINOR**

> **Status** **FIXED, 2026-09-02** — `WH-SC-204` claimed by `issues/p2-14.md` (v1 printing; the print server that would choose the template by zone is `P3-08`, v1.1). The same pass claimed `X-023`'s `WH-SC-170` into `issues/p2-01.md`, so `comm -13` over the catalogue is now **empty**: all 300 scenarios are walked by a task.

**Evidence.**

```bash
comm -23 sc_defined.txt sc_cited.txt   # → WH-SC-204
```

`SCENARIO-CATALOGUE.md:432` — *"The same LPN label, printed once to a 203 dpi printer and once to a
300 dpi printer … In v1 the operator selects the template and the browser downloads it; v1.1 adds the
print server and the printer registry."* **It is the only one of 300 that no task walks.** It belongs
to `P2-14` (printing, v1) or `P3-08` (the print server, v1.1) — and it is the scenario that proves
`S-019`, itself `COVERED-uncited`.

---

### `X-042` · `IMPLEMENTATION-PLAN.md` §8.3 states 914 migration numbers; the task files own 915 — **MINOR**

> **Status** **OPEN** — recompute §8.3 and §8.5 from `issues/`, per §11 item 4's own rule.

**Evidence.** Expanding every range in every task header's `Migrations` cell:

```
numbers claimed       : 915
claimed by two tasks  : none   (V520012 appears twice but p3-19.md:4 reads `Migrations **—**`)
outside V500000-549999: none
{'adapter': 320, 'app': 219, 'base': 141, 'india': 118, '3pl': 117}
```

§8.3 prints `914` and `'warehouse': 218`. **The extra number is `V510215`**, claimed by `issues/p5-13.md`
for `wh_marketplace_claims` — the fix this log records as `X-001`, applied after the plan was written.

`IMPLEMENTATION-PLAN.md` §11 item 4 anticipated exactly this: *"the moment those files exist, they win
over §2 of this page, and `tools/check-design-set.py` must fail on drift between them."* It does not
yet, for counts.

---

### `X-043` · §8.3's integrity command reads a file that is not in the repository — **MAJOR, method**

> **Status** **OPEN** — replace the transcription step with a parse of `issues/*.md` headers.

**Evidence.**

```bash
ls migs.txt issues/migs.txt tools/migs.txt
# ls: migs.txt: No such file or directory
# ls: issues/migs.txt: No such file or directory
# ls: tools/migs.txt: No such file or directory
```

§8.3's script opens `migs.txt`, described in its own comment as *"transcribed from §2's Migrations
column"*. The transcription is not committed, so **the most safety-critical count in the plan cannot
be re-run by anyone** — and a Flyway collision is a silent history deletion
(`FlywayConfiguration.java:296-327`), not a loud failure. `DECISIONS.md` §7 rule 1 requires the command
*in* the document; a command that depends on an uncommitted intermediate does not satisfy it.

The replacement is in `X-042` above and needs no transcription.

---

### `X-044` · `P2-29` and `P3-04` own `warehouse-base`-band migrations without declaring the module — **MAJOR**

> **Status** **OPEN** — the fix `X-021` applied to `P1-20` was never applied to these two, though
> `X-021` names them.

**Evidence.** `python3 tools/check-design-set.py`, check-4:

```
issues/p2-29.md:4: V501070-V501099 is outside the band of its declared module: warehouse V510000-V519999
issues/p3-04.md:4: V501101-V501109 is outside the band of its declared module: warehouse V510000-V519999
issues/p6-08.md:4: V524000-V524099 is claimed but the header declares no banded module (logistics, platform)
```

The headers today:

```
p2-29.md:4  Module **`warehouse`** + **`platform`** … Migrations **V501070–V501099, V511060–V511139**
p3-04.md:4  Modules **`mobile`** + **`warehouse`** · Migrations **V501101–V501109** … **V511140–V511179**
p1-20.md:4  Module **`warehouse` + `warehouse-base` + `platform`** … (fixed by X-021)
```

**Why it matters mechanically, restating `X-021`:** a `V501xxx` file must live in
`warehouse-base/backend/src/main/resources/db/migration/`, because `Dockerfile.backend:140-181` copies
each module's directory and the band-to-module mapping is what `WarehouseBaseCouplingTest`'s band
assertion checks. A base-band file authored inside `warehouse/` is an out-of-band migration, and
`issues/p4-10.md` shows the right pattern — a `## ⚠ This task owns a migration in another module's
band, deliberately` heading. `P2-29` and `P3-04` carry no such notice.

**`P6-08` is benign** and should be exempted, not fixed: `D-2` and `00-EPIC-master.md` reserve
`V524000`–`V524999` for `logistics` inside the adapter band on purpose.

---

### `X-045` · Eight finding citations resolve to nothing, six of them in `COMPETITOR-BENCHMARK.md` — **MAJOR**

> **Status** **FIXED, verified 2026-09-02 (review round 2)** — `python3 tools/check-design-set.py`
> check-7 reports **0**. The six `COMPETITOR-BENCHMARK.md` citations were rewritten to name the review
> *section* they came from rather than a finding id that never existed — `docs/COMPETITOR-BENCHMARK.md:349`
> now reads *"(R2 §1.12 row 244)"*, and its siblings the same way. `E-754` is fenced at
> `docs/COMPETITOR-BENCHMARK.md:994` as what it actually is: the tail of *IEEE-754* at
> `docs/reviews/R1-codebase-reality.md:441`, quoted as a false positive and never cited as a finding.
> `R6-prior-art-triage.md`'s `E-1`/`E-8` were likewise not finding ids and no longer read as such.
>
> **The eight tokens survive in this file** — §6.4 and the `finding-citations` declaration on line 4
> exempt them, because a defect log that cannot quote the broken citation cannot evidence the defect.
> That exemption is the reason check-7's exempt count for this file is 32, not 0.
>
> This is still the exact failure `DECISIONS.md` §7.4a says was already caught four times in the first
> authoring wave. Round 2 found no new instance, which is the first round that can say so.

**Evidence.** `python3 tools/check-design-set.py`, check-7:

```
docs/COMPETITOR-BENCHMARK.md:349  T-244 is cited but not defined in R2
docs/COMPETITOR-BENCHMARK.md:507  T-325 is cited but not defined in R2
docs/COMPETITOR-BENCHMARK.md:944  T-326 is cited but not defined in R2
docs/COMPETITOR-BENCHMARK.md:944  T-337 is cited but not defined in R2
docs/COMPETITOR-BENCHMARK.md:948  T-264 is cited but not defined in R2
docs/COMPETITOR-BENCHMARK.md:1002 E-754 is cited but not defined in R3
docs/reviews/R6-prior-art-triage.md:1569 E-1 is not a finding id
docs/reviews/R6-prior-art-triage.md:1569 E-8 is not a finding id
```

**Five of the eight are R2 capability-matrix row numbers cited as finding ids** — `T-244`, `T-264`,
`T-325`, `T-326`, `T-337` are all > `T-097`. R2 numbers its matrix rows independently of its findings,
`DECISIONS.md` §7.4a records four such miscitations already caught, and `COMPETITOR-BENCHMARK.md` §9
row 1 rests on one of them (*"R2 `T-326`…`T-337`"*).

**`E-754` is a fabrication** — R3 has 90 findings. **`E-1`/`E-8` in R6** are unpadded and ambiguous.

**Impact, and why it is MAJOR not MINOR.** This is the exact shape of the accounting set's worst
failure: *25 dangling cross-references of which 19 resolved to a different real requirement, so live
gaps read as closed.* Here `T-244` resolves to nothing today; the moment R2 is extended past `T-097`
it resolves to something real and wrong.

---

### `X-046` · Six phase epics put `__TASKS__` on a heading line, which `create-issues.sh` corrupts — **MINOR, mechanical**

> **Status** **OPEN** — move the placeholder to its own line under a `## Tasks` heading.

**Evidence.** check-9:

```
issues/03-EPIC-p2.md:134   `__TASKS__` shares its line with other content (`## __TASKS__`)
issues/04-EPIC-p2in.md:118 …
issues/05-EPIC-p3.md:83    …
issues/06-EPIC-p4.md:153   …
issues/07-EPIC-p5.md:90    …
issues/08-EPIC-p6.md:76    …
```

`create-issues.sh` substitutes a multi-line checklist at the placeholder; substituting it into a `## `
heading produces a heading containing a checklist. `01-EPIC-p0.md` and `02-EPIC-p1.md` do it correctly
— **the fix is to copy them.**

---

### `X-047` · `I-10`…`I-20` are defined by two registers, and `DECISIONS.md` §6 declares no namespace for `I-`, `WS-` or R1 §8's `T-n` — **MAJOR, id namespace**

> **Status** **OPEN** — this is `X-022`'s defect, generalised and computed.

**Evidence.** check-11, 14 violations:

```
docs/DATA-MODEL.md:2288  `I-10` is defined by 2 registers — enforceable constraints (DATA-MODEL.md)
                         and irreversible rows (IRREVERSIBLE.md) — 24 mentions cannot be told apart
… the same for I-11 … I-20 (eleven ids, 9–33 mentions each)
docs/DECISIONS.md:347    §6 declares no namespace for the R1 §8 traps register (`T-…`, 18 ids)
docs/DECISIONS.md:347    §6 declares no namespace for the irreversible rows register (`I-…`, 63 ids)
docs/DECISIONS.md:347    §6 declares no namespace for the screens register (`WS-…`, 237 ids)
```

`DATA-MODEL.md` §6.3 numbers its enforceable SQL constraints `I-1`…`I-20`. `IRREVERSIBLE.md` §1
numbers its consolidated rows `IRR-01`…`IRR-63` and calls the namespace *"confined to this file and to
references into it"* — **but 24 mentions of `I-10` alone are spread across the set**, and zero-padding
is not a reliable discriminator when authors write both forms.

`DECISIONS.md` §6 opens *"Id namespaces — disjoint by construction … That cannot happen here"* and
lists nine kinds. It lists neither `I-`, nor `WS-`, nor R1 §8's traps. **The section a new author
reads before choosing an id does not describe three of the registers in use.**

---

### `X-048` · `tools/check-design-set.py` has no finding-disposition check, so `D-12` is unenforced — **MAJOR**

> **Status** **OPEN** — `X-009`'s residual. `GAP-REGISTER.md` now exists; the gate does not.

**Evidence.**

```bash
grep -c "GAP-REGISTER" tools/check-design-set.py   # → 0
```

`DECISIONS.md` `D-12`: *"every one of the 575 findings is dispositioned into a task in
`GAP-REGISTER.md`, and `tools/check-design-set.py` **fails if any finding is untraced**."* The script
runs twelve checks and none of them reads the register. Its check-7 verifies that a **cited** finding
resolves; nothing verifies that an **uncited** finding is dispositioned — which is the whole of `D-12`.

The recommended check-13 is in `GAP-REGISTER.md` §8 item 3.

---

### `X-049` · The FRD says "All seven remain open" and lists `OD-1`…`OD-7`; `DECISIONS.md` §3 carries eleven — **MAJOR**

> **Status** **FIXED, 2026-09-02** in `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` §9 — the heading sentence now reads *All fifteen remain open*, the table carries `OD-8`…`OD-15` with each one's requirement exposure, and it states inline why it drifted. `OD-12`…`OD-15` are the four formerly unnumbered gates, allocated the same day (`X-024`, `X-029`, `X-030`, `X-036`).

**Evidence.**

```bash
grep -oE '^\| \*\*OD-[0-9]+\*\*' docs/DECISIONS.md | grep -oE 'OD-[0-9]+' | tr '\n' ' '
# → OD-1 OD-2 OD-3 OD-4 OD-5 OD-6 OD-8 OD-9 OD-10 OD-11 OD-7      (eleven; OD-7 is last in the table)
```

`WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` §9 opens *"**All seven** remain open and each gates named
requirements"* and its table runs `OD-1`…`OD-7`. **Four open decisions are missing from the document a
requirement author reads**, and they are not the harmless four:

- **`OD-10`** — is MRP a dimension of the position key? — carries *"the tightest deadline in the set"*, **before `PNR-1` / `V500030`**.
- **`OD-11`** — do value-only movements conserve value? Is there an `L-15`? — gates `P2-17`, `P2-28`, `P3-11` (and see `X-029`, `X-030`).
- **`OD-9`** — does warehouse carry a tax engine? — decides whether **six** `whin_` tables exist.
- **`OD-8`** — how does an out-of-process consumer authenticate to the port? — the only item platform must build for warehouse.

**Impact.** `DECISIONS.md` wins, so the four are open regardless. But the FRD's §9 is where a reader
checks whether a requirement is gated, and for `FR-321` (MRP), `FR-325` (tax) and the value-only
movements it says *not gated*.

---

### `X-050` · Five documents carry no reference to the four ladder amendments, and `COMPETITOR-BENCHMARK.md`'s product verdict is stale as a result — **MAJOR**

> **Status** **FIXED for `COMPETITOR-BENCHMARK.md` on 2026-09-02 — OPEN for the other four documents.**
> The benchmark now cites the amendments **20** times where it cited none; the same command re-run
> against the other four still returns **0** for `COEXISTENCE`, `MODULE-INTEGRATION`,
> `PLATFORM-DEPENDENCIES` and `IRREVERSIBLE`, and `IRREVERSIBLE`'s zero remains defensible for the
> reason given below.
>
> **Why the reviewer's earlier refusal was lifted, and how far.** Round 2 first declined to fold this
> in, on the ground that *"editing a competitor verdict is a **product** judgement … and no reviewer
> may make it unilaterally."* `J-004` changed what the edit is: it supplies **nine rows of corrected
> replacement text**, each derived from an amendment already taken in `DECISIONS.md` §5.1, so applying
> them is transcription of a decision the owner has already made, not a new judgement about where we
> sit against Oracle, Körber or Manhattan. **No competitor's mark moved.** The only marks that moved
> are two of *our own* — §8.1 rows 12 and 15, `○` → `◐` — and both follow mechanically from `A-1`
> and `A-2`.
>
> **What was applied** (all in `docs/COMPETITOR-BENCHMARK.md`, one pass):
> §2.3 vehicle-fitment ERP cell → `○ (Epicor ●)`, with one sentence added to **W1** (`J-006`) ·
> §2.16 delivery-challan row → **v1/P2-IN in full** · §2.16 e-way row → **v1/P2-IN generation**, IRP
> round-trip only at v2, lifecycle extended with `CLOSED` (`J-002`, landed in `P2-IN-04`) ·
> §4.1 row 1 rewritten to *"Products with a full reverse-logistics suite"* · §4.1 row 2 rewritten to
> *"Every product with a managed print fleet"* · §4.1's closing segment clause — apparel/footwear
> removed from *"cannot be served at all at v1"* (`A-3`) · §4.2's Indian-statutory row narrowed to
> IRP / Rule 56 / ITC-04 · §4.2's apparel-matrix row **deleted**, because `A-3` took the decision the
> row feared would not be taken · §8.1 rows 12 and 15 `○` → `◐`, and the *"where we are below the
> median"* summary reduced from three areas to one · §8.2's *"not yet able to take a return"* clause
> struck and replaced · §9 rows 1, 2 and 4 → **RESOLVED** by `A-1` / `A-3` / `A-2`, leaving row 3
> (cost-layer ownership) the only unresolved item in the top four · §9.2's SAP LE-WM `?` removed from
> the forbidden-citation list and the resolved fact recorded with its two sources (`J-008`) · §5.2
> gained a **SAP Stock Room Management** displacement paragraph.
>
> **Two corrections outside `J-004`'s nine**, both the same class of staleness and both recorded here
> rather than left standing: §5.2's *"the style×size×colour matrix is undecided"*, contradicted by
> `A-3`; and §9's preamble, which said ranks 1–3 all needed a decision when only rank 3 now does.
>
> **`X-045`'s dangling-citation sweep was run over the edited rows.** Four files quoted text this pass
> deleted, and each was annotated rather than silently rewritten: `GAP-REGISTER.md` §6.3 — the whole
> section is now marked superseded, and its counting command records both the 2026-09-01 run and the
> new value; `IMPLEMENTATION-PLAN.md` §5.3 — kept, because it names the **task** that closes each row,
> which the benchmark deliberately does not; and `issues/03-EPIC-p2.md` and `issues/p2-12.md`, which
> both quoted §4.1's *"most damaging line"* in the present tense. `issues/p2-14.md`'s Dymo sentence
> was left alone: it cites `A-2`'s rationale, not §4.1.
>
> **What remains open is genuinely the owner's:** the four documents still at 0. `COEXISTENCE.md` §5
> `M6` is the load-bearing one (below); `MODULE-INTEGRATION.md` and `PLATFORM-DEPENDENCIES.md` need a
> line each; `IRREVERSIBLE.md` needs none.

**Evidence.**

```bash
for f in COMPETITOR-BENCHMARK COEXISTENCE MODULE-INTEGRATION PLATFORM-DEPENDENCIES IRREVERSIBLE \
         WAREHOUSE-FUNCTIONAL-REQUIREMENTS IMPLEMENTATION-PLAN DATA-MODEL INDIA-LOCALISATION-PACK \
         BUILD-SPEC-SCREENS SCENARIO-CATALOGUE PORT-AND-ADAPTER-CONTRACT; do
  printf '%-38s %s\n' "$f" "$(grep -coE '`A-[1-4]`' docs/$f.md)"
done

# Round-2 extension (`H-008`): the command above never tested issues/, where the phase leads read.
for f in issues/0*-EPIC-*.md; do
  printf '%-22s A:%-28s L:%s\n' "$(basename $f .md)" \
    "$(grep -ohE '`A-[1-4]`' $f | sort -u | tr '\n' ' ')" \
    "$(grep -ohE '\bL-1?[0-9]\b' $f | sort -u | wc -l)"
done
# Before round 2: 01-EPIC-p0, 02-EPIC-p1, 07-EPIC-p5 and 08-EPIC-p6 cited no `A-n` at all, and
# `A-3` reached no phase epic — while its two owning phases are P1 (the schema) and P5 (the screens).
# 03-EPIC-p2 and 08-EPIC-p6 cited zero `L-n`. Round 2 added `A-3` to 02-EPIC-p1 and 07-EPIC-p5 and a
# `## The invariants this phase establishes` section to 05-EPIC-p3 … 08-EPIC-p6. **This extension is
# part of the ratchet: a new epic with `A:` empty is a defect, not a style choice.**
```

```
COMPETITOR-BENCHMARK                   0   <- 20 after the 2026-09-02 fix; every other row unchanged
COEXISTENCE                            0
MODULE-INTEGRATION                     0
PLATFORM-DEPENDENCIES                  0
IRREVERSIBLE                           0
WAREHOUSE-FUNCTIONAL-REQUIREMENTS     17
IMPLEMENTATION-PLAN                   21
DATA-MODEL                            12
INDIA-LOCALISATION-PACK                5
BUILD-SPEC-SCREENS                     3
SCENARIO-CATALOGUE                     3
PORT-AND-ADAPTER-CONTRACT              1
```

`DECISIONS.md` §5.1 took four amendments on 2026-09-01: `A-1` returns → **v1/P2**, `A-2` printing →
**v1/P2**, `A-3` variants → **v1 schema**, `A-4` India in two waves. `COMPETITOR-BENCHMARK.md` was
written the same day and did not know about any of them. Consequences, in the words it carried
**before** the 2026-09-02 fix recorded in the Status above:

- **§8.2**, the headline product verdict: *"…and — as the ladder currently reads — **not yet able to take a return**, which is the one gap that would embarrass it in front of any buyer in any segment."* **`A-1` closed that gap.**
- **§8.1 row 15** Returns: *"`return_type` in v1 and nothing else. The ladder's most damaging placement ‡"*.
- **§8.1 row 12** Execution layer: *"no RF and **no label** until v1.1"*. **`A-2` moved templated printing to v1.**
- **§9 rows 1–4** are still marked `UNRESOLVED`/`Unresolved`: returns placement (`A-1` resolved), apparel (`A-3` resolved), cost-layer ownership (the `D-6` rewrite resolved), printing placement (`A-2` resolved).

**`IRREVERSIBLE.md`'s zero is defensible** — it is a schema document and the amendments moved screens
and features, not columns. The other four are not: `COEXISTENCE.md` §5 `M6` is already known stale for
this reason (`X-037`).

**Impact.** §8.2 is the paragraph a salesperson quotes. It currently declines a capability the product
has.

---

### `X-051` · `DECISIONS.md` says 575 findings; its own §6 ranges sum to 574, and §6 does not name the 575th — **MINOR**

> **Status** **OPEN** — add `T-020a` to §6's R2 row.

**Evidence.**

```bash
echo $((50+97+90+93+98+60+86))                                        # → 574
grep -rohE '\b[CTEFSPG]-[0-9]{3}[a-z]\b' docs/reviews/*.md | sort -u  # → T-020a
grep -n "Findings raised" docs/reviews/R2-tier1-wms-audit.md          # :84 → **98** (T-001 … T-097, plus T-020a)
```

`DECISIONS.md`'s preamble and `D-12` both say **575**. §6's namespace table says `T-001`…`T-097`,
which with the other six ranges sums to **574**. The 575th is `T-020a` — a real MINOR finding at
`R2:1020`, cited by `FR-023`, closed by `issues/p6-01.md:50`.

`issues/00-EPIC-master.md:15` already reconciles this in prose. **§6 is the register a tool reads**,
and a tool that trusts §6 undercounts by one — including any future check-13 (`X-048`).

**The trap for tooling.** `T-020a` does not match `[CTEFSPG]-[0-9]{3}\b`: the word boundary fails
between `0` and `a`. `tools/check-design-set.py` gets it right (its R2 register reports 98); a naive
`grep` does not.

---

### `X-052` · `COEXISTENCE.md` mitigation `M4` is named in no task file — **MINOR**

> **Status** **FIXED, 2026-09-02** — declared in `issues/p2-27.md` alongside `M1`/`M2`/`M8`, and the seed it actually requires is named in `issues/p0-04.md`. `M4` is now owned in one place and cross-referenced from the other, which is the shape `M5`/`M9` already had.

**Evidence.**

```bash
grep -ohE '\bM[1-9]\b' issues/p*.md | sort -u | tr '\n' ' '   # → M1 M2 M3 M5 M6 M8 M9
```

Every `COEXISTENCE.md` §5.4 mitigation appears somewhere in `issues/` **except `M4`** — *"shared
vocabularies: UoM codes, reason codes, movement types, warehouse codes seeded from one list on both
sides"*, which addresses costs C1, C4 and C5 and is R3 `E-085`. `E-085` is correspondingly the only
R3 finding in `GAP-REGISTER.md` §4's `NEEDS-TASK` list that a mitigation table already specified.

`M5` and `M9` are named once, in `p2-27.md`, explicitly as *"neither is this task"* — so they are
declared-not-owned rather than forgotten. **`M4` is neither owned nor declared.**

---

### `X-053` · Forty-six tables are named in task files with no `DATA-MODEL.md` row — **MAJOR**

> **Status** **FIXED, verified 2026-09-02 (review round 2)** — `python3 tools/check-design-set.py`
> check-3 reports **0 violations**, with 24 declared exemptions across 11 files. Superset of `X-002`,
> `X-003` and `X-012`, which close with it. **The four groups closed by three different means, and the
> distinction matters to anyone re-reading this log:**
>
> | Group | How it closed | Evidence |
> |---|---|---|
> | India wave-2 orphans | **Renamed, not added.** The task files were brought onto `DATA-MODEL.md`'s spellings — `whin_customs_licences` → `whin_counterparty_licences`/`whin_entity_licences`, `whin_hsn_codes` → `whin_hsn_tax_master`, `whin_exbond_clearances` → `whin_ex_bond_clearances`, `whin_eway_bill_consolidations` → `whin_eway_bills_consolidated`. `X-011`/`X-012` own the naming rule | `grep -ohE '`whin_[a-z_]+`' docs/DATA-MODEL.md \| sort -u` → 52 names, all of them now the ones the tasks use |
> | New tables the P5 fixes created | **Rows written.** `wh_marketplace_claims` (`DATA-MODEL.md:1076`), `whb_ratio_pack_templates` (`:542`), `whb_packaging_balances` (`:513`) | closes `X-001`'s table half, `X-002`, `X-003` |
> | Report and archive tables the tasks invent | **Rows written** — `wh_rpt_coexistence`, `wh_rpt_health`, `wh_rpt_consolidated_valuation`, `whin_rpt_stock_by_mrp`, and the three archive tables under `WHB-66`/`V500100` (`DATA-MODEL.md:929`, `:2932`) | the group *"nobody has filed"*, now filed and allocated |
> | Names that diverge from `DATA-MODEL.md` | **Fenced as counter-examples, not built.** `whaf_van_stock` (`issues/p3-20.md:54`) and `wh_tyre_fitments` (`issues/p5-21.md:55`) are named by their traps precisely so they are *not* built; a `DATA-MODEL.md` row would have granted them the existence the trap forbids | the fence text says so in both files |
>
> **Two residuals survive, and neither is a check-3 subject** because check-3 reads task files only:
>
> - **`wh_transport_details` is the wrong name in two places.** The table is `whb_transport_details` (`DATA-MODEL.md:924`, `WHB-52`, `V500052`). `INDIA-LOCALISATION-PACK.md` (`:129`, `:221`, `:529`–`:531`, `:1148`, `:1240`, `:1334`) and `issues/04-EPIC-p2in.md:59` still write `wh_`. The **module** call is right and already reasoned — a vehicle number is not an Indian rule, so it lives in base, not `whin_` — it is the prefix that drifted. `:1334` is the funniest instance: it corrects `whin_transport_details` to `wh_transport_details`, and is itself wrong by one letter.
> - **`wh_location_occupancy` is a suggestion, not a design object.** It appears once, in `docs/reviews/R1-codebase-reality.md:532`, where `C-033` proposes copying `pdi_storage_slot_assignments`' derive-at-read shape. No task file and no document treats it as a table. It should not get a `DATA-MODEL.md` row unless a task claims it — recorded so the next author does not add one to silence a violation that does not exist.

**Evidence.** `python3 tools/check-design-set.py`, check-3 — 46 violations. They fall into four groups:

| Group | Tables | Already filed as |
|---|---|---|
| India wave-2 orphans | `whin_bill_of_entry_references/_lines`, `whin_customs_bonds`, `whin_customs_licences`, `whin_exbond_clearances/_lines`, `whin_moowr_returns/_lines`, `whin_sez_movements`, `whin_form3cd_runs/_lines`, `whin_packaged_commodity_declarations`, `whin_mrp_revisions`, `whin_instrument_verifications`, `whin_hsn_codes`, `whin_uqc_codes`, `whin_gst_registrations`, `whin_job_work_returns`, `whin_itc04_runs`, `whin_stock_account_runs`, `whin_eway_bill_consolidations`, `whin_eway_bill_lines`, `whin_eway_bill_events` | `X-011` (naming), `X-012` (ownership) |
| New tables the P5 fixes created | `wh_marketplace_claims`, `whb_ratio_pack_templates/_lines`, `whb_packaging_balances` | `X-001`, `X-002`, `X-003` |
| Report and archive tables the tasks invent | `wh_rpt_coexistence`, `wh_rpt_health`, `wh_rpt_consolidated_valuation`, `whin_rpt_stock_by_mrp`, `whb_stock_movements_archive`, `whb_stock_movement_lines_archive`, `whb_movement_line_attributes_archive`, `wh_location_occupancy` | **new here** |
| Names that diverge from `DATA-MODEL.md` | `wh_transport_details` (vs `whb_transport_details`), `whin_transport_details`, `whaf_van_stock` (vs `whaf_van_stock_assignments`), `wh_tyre_fitments` | **new here** — and the first is `X-037`'s `wh_`/`whin_` question |

**The third group is the one nobody has filed.** Eight report and archive tables are named in
acceptance criteria and traps with no `DATA-MODEL.md` row, so a builder has a table name, no columns,
and no migration number. `P6-01`'s three archive tables are the sharpest case: the archive is the
**one** operation the append-only trigger must be taught to permit (`L-2`), and its target tables are
undefined.

---

### 2.1 · Filed in review round 2

One entry. It is here rather than in `GAP-REGISTER-R2.md` because it is a **design-set defect** — a
document disagreeing with itself — not a *gap in the design*, and this log is where those live.

### `X-054` · `DATA-MODEL.md` §8.4's two generated blocks were regenerated separately, and the version block silently fell eleven rows behind the inventory — **MAJOR**

> **Severity** MAJOR · **Status** **FIXED, 2026-09-02 (review round 2)** — both blocks regenerated in the same pass and now agree exactly. Filed rather than fixed silently, because the *mechanism* recurs every time a table is added and no check can see it.

**Claim.** `DATA-MODEL.md` §8.4 carries two machine-generated blocks — `TABLE-INVENTORY`
(`docs/DATA-MODEL.md:3137`–`:3454`) and `TABLE-VERSIONS` (`:3565`–`:3882`). They are generated by two
different commands, live 111 lines apart, and **nothing enforces that they hold the same tables.** When
round 1's eleven late allocations (`WHB-64`, `WHB-65`, `WHB-66`, `WH-115`, `WIN-05`'s two children,
`WIN-22`, and the report tables) were appended, the inventory block was regenerated and the version
block was not. The two disagreed by eleven rows for the length of a commit.

**Why it matters.** §8.4's inventory is what `IMPLEMENTATION-PLAN.md` §8.5 and both READMEs quote for
*"N tables"*; the version block is what the **v1 cut** is computed from. A table present in one and
absent from the other is a table that is counted in the total and **not costed into any version** — the
exact shape of *"we shipped v1 and this table has no home"*. It is invisible to
`tools/check-design-set.py`, which reads task files against the inventory and never compares the two
blocks to each other.

**Evidence — the diff that must return two empty lists.**

```python
import re
s = open('docs/DATA-MODEL.md').read()
inv = re.search(r'<!-- TABLE-INVENTORY-BEGIN -->\n```\n(.*?)\n```\n<!-- TABLE-INVENTORY-END -->', s, re.S).group(1)
ver = re.search(r'<!-- TABLE-VERSIONS-BEGIN -->\n```\n(.*?)\n```\n<!-- TABLE-VERSIONS-END -->',  s, re.S).group(1)
I = [l.strip()   for l in inv.splitlines() if l.strip()]
V = [l.split()[0] for l in ver.splitlines() if l.strip()]
print(len(I), len(V), sorted(set(I) - set(V)), sorted(set(V) - set(I)))
```

```
314 314 [] []
```

**Fix applied.** Both blocks regenerated together in review round 2, which also added the thirteen
round-2 tables (`WHB-55`, `WHB-56`, `WHB-67`, `WH-116`, `WIN-23`). §8.4's own re-run note at
`docs/DATA-MODEL.md:3490`–`:3492` records both regenerations and their dates.

**The durable fix is a check, and it is not written.** A check comparing the two blocks set-for-set is
four lines and would have caught this at the commit that caused it. **It is not `check-13`** — §5 item 11
already claims that number for `D-12`, and §6.4 `R-4` floats `check-14` for dangling document
references, so this one is **`check-15`**. It is proposed in §5, not built here: adding a check inside a
defect log is the kind of scope creep this set forbids.

**Related.** `X-042` and `X-043` are the same *class* of defect on `IMPLEMENTATION-PLAN.md` §8.3 —
a stated output that its own command no longer produces. `DECISIONS.md` §7 rule 1 — *never state a
count you did not compute* — is written for exactly this failure, and here the count was computed;
it was **the second block that was not re-derived**.

---

### `X-055` · The quality-inspection mixed-result rollup is `CONDITIONAL` in the FRD and the exit scenario, and `PARTIAL` in the data model, the screen spec and the task — **MAJOR, and it is the column's stored value**

> **Severity** MAJOR · **Status** **OPEN — a naming decision, deliberately not taken here.** Found 2026-09-02 by review round 2 while authoring `WH-SC-301` for `Q-006`

**Claim.** `FR-133` states the rollup as *"all pass → `PASS`, all fail → `FAIL`, anything mixed or
partial → `CONDITIONAL`"*, and `WH-SC-070` — a **P1 acceptance scenario** — asserts the same word.
Three other places state the same rule with a different third value:

| Document | Value | Where |
|---|---|---|
| `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` `FR-133` | **`CONDITIONAL`** | `:298` |
| `SCENARIO-CATALOGUE.md` `WH-SC-070` | **`CONDITIONAL`** | `:246` |
| `DATA-MODEL.md` `wh_quality_inspections` | **`PARTIAL`** | `:979`, in the `result` column's stated values |
| `BUILD-SPEC-SCREENS.md` WS-080 | **`PARTIAL`** | `:1505`, in the grid column spec |
| `issues/p1-14.md` | **`PARTIAL`** | scope, Traps and Acceptance — **three separate assertions** |

```bash
grep -n 'CONDITIONAL' docs/WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md docs/SCENARIO-CATALOGUE.md   # -> 2 rollup hits
grep -n 'PARTIAL'     docs/DATA-MODEL.md docs/BUILD-SPEC-SCREENS.md issues/p1-14.md          # -> the five above
```

**Why it matters, and why it is MAJOR rather than cosmetic.** This is not a label — it is **the value
stored in `wh_quality_inspections.result`** and the value a `whb_`-registry row or a `CHECK` would
carry. A builder reading `DATA-MODEL.md` and `BUILD-SPEC-SCREENS.md` writes `PARTIAL`; the acceptance
scenario the same builder must walk asserts `CONDITIONAL`; the task file agrees with the data model
in three places and with the FRD in none. The scenario fails, the fix is a **data migration on a
column that already has rows**, and `FR-133`'s own stated purpose — *"stated to the value, because
'mostly passed' is not a QC result"* — is defeated by the set disagreeing with itself about what the
value is.

**Not resolved here.** `DECISIONS.md` §7 — *never resolve a cross-document conflict by editing the
losing document silently* — applies, and the two sides are not equal in weight in the same direction:
the **requirement authority** (`FR-133`) and the **acceptance scenario** say `CONDITIONAL`, while the
**implementation surface** (data model, screen spec, task) says `PARTIAL` in five places. Either is
defensible; picking one by counting occurrences is not.

**Recommendation, for the product owner rather than an author.** Take **`PARTIAL`**, and amend
`FR-133` and `WH-SC-070` — it is two edits against five, it is the word already in the column spec
and the grid, and `CONDITIONAL` collides with the *conditional release* vocabulary `WH-SC-071` uses
for a disposition, which is a **different concept on the same document**. If `CONDITIONAL` is taken
instead, the five implementation-side edits must land **in one commit**, because a half-applied
rename here is a `CHECK` violation at runtime.

**`WH-SC-301` deliberately does not name the value.** Round 2 authored the inspection-completeness
scenario without citing either word, so this conflict is decided once, by a person, rather than
being quietly settled by a new scenario taking a side.

**Related.** `X-047` (id namespaces with two owners) and `X-053` (task files naming tables the data
model does not) are the same class: **two documents, both authoritative-sounding, no arbiter named**.

---

## §3 · The cross-document conflicts that remain open, ranked by how expensive they get

Ranked by **the cost of discovering it late**, not by severity today. Rank 1 costs a production
incident; rank 8 costs an argument.

| # | Conflict | The two documents | Cost if found late | Defect | Deadline |
|---:|---|---|---|---|---|
| **1** | **The `V541000`/`V541100` India migration-block collision.** `INDIA-LOCALISATION-PACK.md` §11.2 gives wave-2 group A `V541000`–`V541099` and group B `V541100`–`V541199`; `DATA-MODEL.md` §7.6 `WIN-30` gives `V541000`–`V541199` to wave-1 permissions, menus, grid config and `admin_settings`; and `IMPLEMENTATION-PLAN.md` §2.9 sub-allocates `V541000`–`V541049` to `P2-IN-01` and `V541100`–`V541149` to `P4-01` | `INDIA-LOCALISATION-PACK.md` §11.2 · `DATA-MODEL.md` §7.6 · `BUILD-SPEC-SCREENS.md` §0.9 | **A backend startup failure, not a merge conflict.** All module migrations are flattened into one directory at build time (`Dockerfile.backend:140-181`), and `FlywayConfiguration.java:296-327` renumbers legacy history into these bands and then `DELETE`s duplicate history rows — **so a collision does not fail loudly; it silently deletes a history row and re-runs a migration.** Discovered in production, it is a corrupted schema history on every install | `X-010` `X-033` | **before `P2-IN-01` writes a permission migration** |
| **2** | **Twelve wave-2 India tables have no owning task and no migration number**, and six of them (group H — drug/FSSAI/PESO/customs licences, hazmat ceilings, the Schedule H1 register, recall notifications) have **no `FR-` either**, while `DECISIONS.md` §5, `IMPLEMENTATION-PLAN.md` §1.6, `PORT-AND-ADAPTER-CONTRACT.md` §9.6 and FRD §6.18 all promise *"the regulated-goods packs"* at v2 | `INDIA-LOCALISATION-PACK.md` §11.2 (42 tables) · `DATA-MODEL.md` §7.6 (~30) · `IMPLEMENTATION-PLAN.md` §2.6 (12 tasks) | **A whole segment is sold and cannot be delivered.** R5 §6 marks pharmaceutical distribution `CANNOT SERVE`; `S-035` is the **only unowned BLOCKER** in the 575 (`GAP-REGISTER.md` §5.1). §8's *"every requirement is owned by exactly one task"* stays true only because **there is no requirement**, which is why no traceability check can see it | `X-012` `X-013` | **before P4 is scoped**, and before anyone bids pharma. **Round 2, 2026-09-02: the task now exists** — `issues/p4-13.md`, `V540182`, owning `FR-456`/`FR-457`, so *"there is no requirement"* is no longer true. **`S-035` is unchanged**: the task opens gated, and the decision to serve pharma or decline it in writing has now gone unanswered through two review rounds |
| **3** | **The value-offset virtual location has two names and `FR-084` seeds neither.** `DECISIONS.md` `OD-11` and `P2-28` say `VALUE_OFFSET`; `PORT-AND-ADAPTER-CONTRACT.md` `PC-12` says `LANDED_COST_OFFSET` and offers reusing `ADJUSTMENT_OFFSET`; `FR-084`'s seed list has ten codes and none of them | `DECISIONS.md` `OD-11` · `PORT-AND-ADAPTER-CONTRACT.md` `PC-12` · FRD `FR-084` | **A migration seeds a row the other document's code looks for and does not find**, and `I-17` requires the virtual location to exist before a movement can balance. So landed cost silently fails to post, or unbalances the value column — and `L-1`…`L-14` conserve **quantity only**, so nothing catches it | `X-029` · related `X-030` | **before `P1-05` writes `V500013`** |
| **4** | **The ledger's partition key** — `occurred_at` (FRD `FR-022` + `DATA-MODEL.md` `WHB-30`) or `posting_date` (`PLATFORM-DEPENDENCIES.md` `PD-D5`) — **has no `OD-` id at all**, and both arguments are substantive: `occurred_at` is what the as-at query and EPCIS want, `posting_date` is what period close and the statutory register want, and `L-13` says they are different columns | FRD + `DATA-MODEL.md` · `PLATFORM-DEPENDENCIES.md` | **A partition key cannot be added to a populated table without a rewrite**, and `V500030` is `PNR-1` **and** `PNR-2`. This is the single most expensive thing on this page to get wrong | `X-024` | **before `P0-02`** — the first ledger migration |
| **5** | **`IMPLEMENTATION-PLAN.md` §8.5 states 119 scenarios; the command printed beside the number returns 300**, under the heading *"The counts on this page, and where each came from"* and the closing line *"Nothing on this page was counted by eye."* §8.5's *v1 exit decomposition* command is also wrong (`/^### 3\.2/` matches `### 3.20`, returning 30) though its stated value 19 is right | `IMPLEMENTATION-PLAN.md` §8.5 · `SCENARIO-CATALOGUE.md` §4.1 | **Every downstream document quoting §8.5 states a scenario count wrong by a factor of two and a half.** Worse, it discredits the page: if the one section that promises computed counts has a stale one, no count on it can be trusted without re-running | `X-007` `X-034` · and `X-042`/`X-043` for the same page's migration count | **CLOSED 2026-09-02** — §8.5 now states **305** and the exit-decomposition command carries its trailing spaces. `X-042`/`X-043`'s migration count on the same page is **still open** |
| **6** | **`IRREVERSIBLE.md` §7.3 item 1 is stale** — it records cost-layer placement as unresolved *"`OD-1`/`OD-6` territory, needs closing before `P2`"*, but `D-6` was rewritten and `DATA-MODEL.md` §2.1/§7.2 place `whb_valuation_policies`, `whb_cost_layers` and `whb_cost_layer_consumptions` in `warehouse-base` at `V500021` | `IRREVERSIBLE.md` §7.3 · `DECISIONS.md` `D-6` · `DATA-MODEL.md` §7.2 | **A settled decision gets re-opened**, and `IRREVERSIBLE.md` is the document authors are told to read *immediately before writing a migration* — so it is read at exactly the moment re-opening is most expensive | `X-032` | before `P2-16` |
| **7** | **`BUILD-SPEC-SCREENS.md` §10.2 lists no verb permission for any P3, P4, P5 or P6 transition** — roughly 45 are missing, from `whb_tasks:assign` to `whin_ex_bond_clearances:clear` — under its own closing line *"a transition with no verb permission is a transition anybody with `:edit` can perform, which is the failure `FR-408` names"* | `BUILD-SPEC-SCREENS.md` §10.2 · the P3–P6 task files | **A security defect that reads as complete.** Every P3+ transition ships gated by `:edit`, which every operator has. The task files derived the names from the documented convention and marked each *absent from §10.2 today* — so the names exist, but no single document is the seed authority for the permission migrations | `X-014` | before the first P3 permission migration |
| **8** | **`BUILD-SPEC-SCREENS.md` §1's `Ver · Ph` column disagrees with `IMPLEMENTATION-PLAN.md` §2 for 21 screens**, and §1.1 says P0 ships fifteen screens where §2.1 assigns thirty-three | `BUILD-SPEC-SCREENS.md` §1 · `IMPLEMENTATION-PLAN.md` §1.1/§2.1 | **A screen in the wrong phase lands in the wrong migration block** — §2.9's divergence 1 splits `V501020`–`V501099` across four tasks *by phase* — so the disagreement is not cosmetic, it moves migration numbers | `X-019` `X-020` | before `P1-20` writes the first grid-config block |

### 3.1 Conflicts that are resolved but not yet written down

These need one editorial pass each, not a decision:

| Conflict | Resolution that already exists | Defect |
|---|---|---|
| `PORT-AND-ADAPTER-CONTRACT.md` §9.7 and R7 §7 place `logistics` at v2 | `DECISIONS.md` §5 puts it at **v3** and its preamble says *"a document that disagrees with this one is wrong"*. `P6-08` is correctly placed | `X-008` |
| `COEXISTENCE.md` §5 `M6` puts the challan at v2/P4 | `A-4` puts it at **v1/P2-IN**, and `FR-308` makes the transport block `wh_`, not `whin_` | `X-037` |
| `COMPETITOR-BENCHMARK.md` §9 rows 1–4 read `UNRESOLVED` | `A-1`, `A-2`, `A-3` and the `D-6` rewrite resolved all four on 2026-09-01. **Re-measured 2026-09-02 and still unwritten** — the pass is a product judgement, not an editorial one; see `X-050` | `X-050` |
| `D-9`/`FR-370` quote *"17 duplicated tables, 33 mobile screens"* | `COEXISTENCE.md` §1.1/§1.2 compute **19** tables and **33 mobile screens of which 14 are inventory** | `X-035` |
| R4 §5.3/§5.6 put `warehouse-3pl` at `V930000`–`V939999` | `D-2` fixes the bands at `V500000`–`V549999`; R7 `G-070` already flags it | — (`G-070`, `DECIDED`) |

---

## §4 · The id-namespace hazards

`DECISIONS.md` §6 opens *"Id namespaces — disjoint by construction … The accounting set's most
expensive defect was three different things sharing one namespace, which a late rename could not
repair because a blanket search-and-replace corrupted the decisions table twice. **That cannot happen
here.**"* Four hazards say otherwise. Each is stated with **the citation rule that avoids it**, because
renaming is forbidden (`DECISIONS.md` §7 rule 4) and a rule is therefore the only available fix.

### 4.1 R1 §8's traps are `T-1`…`T-18` and collide with R2's `T-001`…`T-097`

`reviews/R1-codebase-reality.md` §8 numbers its eighteen codebase traps `T-1`…`T-18`.
`DECISIONS.md` §6 assigns `T-001`…`T-097` to R2's findings. **A bare `T-6` resolves to R2's
finding under §6 and to R1's `filterUtils.ts` allowlist trap under §8, and both readings are
plausible in context.**

> **Citation rule.** Write **`R1 §8 trap \`T-n\``**, never a bare `T-n`. **Never put an R1 §8 trap id
> in a `## Closes` line** — `## Closes` carries only `C-`, `T-` (R2), `E-`, `F-`, `S-`, `P-` and `G-`
> as `DECISIONS.md` §6 defines them.

The task files already obey this. `tools/check-design-set.py` implements the discriminator — an
unpadded `T-n` is looked up in the traps register, a three-digit `T-nnn` in R2's — which is why
check-7 catches unpadded `E-1`/`E-8` in R6 but passes the R1 trap citations. **The rule is enforced
by the checker and undeclared in `DECISIONS.md` §6** (`X-022`, `X-047`).

### 4.2 R2's capability-matrix row numbers read exactly like its `T-nnn` finding ids

R2 numbers its capability matrix independently of its findings, and the matrix runs into the hundreds.
`T-244`, `T-264`, `T-325`, `T-326` and `T-337` are matrix rows. R2 has **98** findings, so every one of
those five is out of range — but *"R2 `T-326`"* reads exactly like a finding citation, and
`COMPETITOR-BENCHMARK.md` §9 row 1 rests on one.

> **Citation rule.** **Cite an R2 finding only after opening the `### T-nnn` heading itself.** If the
> id is greater than `T-097`, it is a matrix row: cite it as **`R2 §1 matrix row 326`**, never as
> `T-326`. `DECISIONS.md` §7.4a already states this and records four miscitations caught in the first
> authoring wave; **five more are live in `COMPETITOR-BENCHMARK.md` today** (`X-045`).

### 4.3 `I-nn` is two registers — enforceable constraints and irreversible rows

`DATA-MODEL.md` §6.3 numbers enforceable SQL constraints `I-1`…`I-20`; `IRREVERSIBLE.md` §1 numbers
its consolidated rows `IRR-01`…`IRR-63` and declares the namespace *"confined to this file"*. It is not:
`I-10` alone has 24 mentions across the set, `I-17` has 33. Zero-padding is not a discriminator —
authors write both forms — and the two registers **overlap on `I-10`…`I-20`**, which is exactly the
range a ledger author cites most.

> **Citation rule.** Write **`IRR I-nn`** for an irreversible row and **`DATA-MODEL.md I-nn`** for an
> enforceable constraint, always with the qualifier, in every document. The P0/P1 task files already
> use `IRR-41`, `IRR-35`, `IRR-39` — **adopt that form everywhere**. And add both registers to
> `DECISIONS.md` §6, which today declares neither (`X-047`).

### 4.4 `WS-nnn` is a register `DECISIONS.md` §6 does not declare

237 screen ids live in `BUILD-SPEC-SCREENS.md` §1 and are cited across the plan, the task files and
the epics. §6 — the section a new author reads before choosing an id — does not list them, so nothing
tells an author where the next free id comes from. `X-001`'s fix had to allocate `WS-238` and say so
in prose; `tools/check-design-set.py` check-12 now flags it as unresolved because §1 was never amended.

> **Citation rule.** `WS-nnn` ids are allocated **only** by adding the row to `BUILD-SPEC-SCREENS.md`
> §1 in the same PR that first cites it — the same discipline `X-006` established for `WH-SC-nnn`
> (*"the catalogue file is the allocation register and nothing else is"*).

### 4.5 A fifth, smaller one: the finding-id regex

`T-020a` is the 575th finding and does not match `[CTEFSPG]-[0-9]{3}\b` — the word boundary fails
between `0` and `a`.

> **Tooling rule.** Match `[CTEFSPG]-[0-9]{3}[a-z]?\b`. A count that returns **574** has dropped it
> (`X-051`).

---

## §5 · Recommended next actions, ordered

Ordered by *what blocks what*, not by severity. Items 1–4 must happen before the first migration is
written; 5–9 before the phase they name; 10–13 are hygiene that keeps this log honest.

| # | Action | Owner | Blocks | Defect |
|---:|---|---|---|---|
| **1** | **Resolve the `V541000`–`V541199` collision** by amending `INDIA-LOCALISATION-PACK.md` §11.2's Block column to point at `DATA-MODEL.md` §7.6, or by re-allocating `WIN-30`. One document, one edit. **Do not blanket search-and-replace** | the India pack owner | `P2-IN-01`, `P4-01`, and the backend's ability to start | `X-010` `X-033` |
| **2** | **Number the four unnumbered gates** as `OD-12`…`OD-15`: the partition key, the value-offset location code, the value-conservation invariant (`L-15`?), and `M3`. `DECISIONS.md` §3 owns the namespace and no other document may allocate | the decisions owner | `P0-02` (`PNR-1`+`PNR-2`), `P1-05`'s `V500013`, `P2-16`/`P2-17`/`P2-28`, `P2-20`/`P2-27` | `X-024` `X-029` `X-030` `X-036` |
| **3** | **Answer `OD-10`** (is MRP in the position key?) — *"the tightest deadline in the set"*, and unrecoverable if wrong | the decisions owner | `PNR-1` / `V500030` | — |
| **4** | **Decide `S-035`**: write the `FR-` rows and `P4-13` (`GAP-REGISTER.md` §4.1), **or** amend the four phase descriptions to stop promising the regulated-goods packs and record pharma as a declined segment. Silence is the third option and it is the one that fails | product | the pharma segment, and `GAP-REGISTER.md`'s only unowned BLOCKER | `X-012` `X-013` |
| **5** | **Recompute `IMPLEMENTATION-PLAN.md` §8.3 and §8.5 from `issues/`**, and replace §8.3's `migs.txt` step with the header parser in `X-042`, so the count is re-runnable by anyone. **§8.5's scenario half is done (2026-09-02, `X-007`/`X-034` closed); §8.3's migration count is not** | the plan owner | trust in every count on those pages | `X-007` `X-034` `X-042` `X-043` |
| **6** | **Assign `FR-224`/`FR-225` to `P2-14` in §2.3**, so the plan's 444 becomes the task files' 446 | the plan owner | ship-blocker #2 (printing) being scheduled | `X-039` |
| **7** | **Add the ~45 verb permissions to `BUILD-SPEC-SCREENS.md` §10.2**, so the permission migrations have one seed authority | the build-spec owner | every P3+ permission migration | `X-014` |
| **8** | **Reconcile `BUILD-SPEC-SCREENS.md` §1's `Ver · Ph` with `IMPLEMENTATION-PLAN.md` §2** for the 21 screens, and correct §1.1's fifteen-screen list. Note the knock-on: the phase column picks the grid-config sub-block | the build-spec owner | `P1-20`'s first grid-config block | `X-019` `X-020` |
| **9** | **Give `X-050`'s five documents a ladder-amendment pass** — the benchmark first, because §8.2 is the paragraph a salesperson quotes and it currently declines a capability the product has | the benchmark owner | external quoting of the product verdict | `X-050` `X-037` |
| **10** | **Fix the eight dangling finding citations** — five R2 matrix rows, one fabricated `E-754`, two unpadded `E-1`/`E-8` — and add §4's four citation rules to `DECISIONS.md` §6/§7 | any author | the namespace guarantee §6 makes | `X-045` `X-022` `X-047` |
| **11** | **Add check-13 to `tools/check-design-set.py`** (`GAP-REGISTER.md` §8 item 3) so `D-12` is enforced rather than asserted, and exempt `WH-SC-301` in check-2 so the gate stops crying wolf | tooling | `D-12` being a fact rather than an intention | `X-048` `X-040` |
| **12** | **Add the 36 `COVERED-uncited` BLOCKER ids to their owning tasks' `## Closes`** (`GAP-REGISTER.md` §5.2). 36 lines, and it moves the four day-one ship-blockers among them from *traceable* to *traced* | any author | nothing — but it is the cheapest risk reduction on this list | — |
| **13** | **Close the small ones in one pass**: `WH-SC-204`'s owner, the six epics' `__TASKS__` placement, `P2-29`/`P3-04`'s module cells, `IRREVERSIBLE.md` §7.3 item 1, the FRD §9 `OD-` table, `M4`'s owner, and the eight undefined report/archive tables | any author | — | `X-041` `X-046` `X-044` `X-032` `X-049` `X-052` `X-053` |

### 5.1 What must **not** be done

- **Never blanket search-and-replace an id.** It corrupted the accounting decisions table twice
  (`DECISIONS.md` §7 rule 4). Every renumbering above is a per-occurrence edit or a citation rule.
- **Never delete a row from this log when it is fixed.** Change its Status to `FIXED` and name the
  file. A defect that disappears is indistinguishable from a defect that was never real.
- **Never resolve a cross-document conflict by editing the losing document silently.** Both entries
  in §3 name the two documents; the loser gets an annotation, exactly as `DECISIONS.md` §5.1
  annotates the four ladder amendments.


### 5.2 Round-2 status of this list, 2026-09-02

Re-measured against the current tree at the end of review round 2. **Nothing was deleted; the actions
that are done say so and name the file.** Items are keyed to the table above.

| # | Round-2 status |
|---:|---|
| **1** | **OPEN.** `INDIA-LOCALISATION-PACK.md` §11.2's Block column is unchanged. Still the most expensive item on the page, and still one edit. |
| **2** | **DONE.** `OD-12`…`OD-15` are allocated in `DECISIONS.md` §3 and carried into `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` §9 — see `X-049`, now FIXED. **Numbering them is not answering them**; all four remain open decisions. |
| **3** | **OPEN, and now the tightest thing on the page.** `OD-10` went through a second review round unanswered. It gates `V500030`, and a partition key cannot be changed on a populated table. |
| **4** | **HALF DONE.** The `FR-` rows and the task exist — `FR-456`/`FR-457`, `issues/p4-13.md`. The **decision** does not. Round 2 deliberately took the first branch (author it, gated) rather than the second (decline pharma in writing), because authoring is reversible and a declined segment is not. See `X-013`. |
| **5** | **DONE.** §8.1, §8.3 and §8.5 were recomputed from `issues/` in both rounds; §8.3 now states **823** migration numbers, **143** tasks, **459** requirements, and §8.5's scenario count is the catalogue's own. `issues/README.md`'s unreproducible *"915 versions"* was replaced and the discrepancy recorded rather than quietly swapped. |
| **6** | **DONE.** `IMPLEMENTATION-PLAN.md:468`. `X-039` is FIXED and check-10 reports 0. |
| **7** | **OPEN.** `BUILD-SPEC-SCREENS.md` §10.2 still stops after the v1 adapters. Round 2's `Q-` lens re-confirmed it. This is the highest-value open item that needs no decision from anyone — it is transcription, and it is a security defect that reads as complete. |
| **8** | **OPEN.** The 21-screen `Ver · Ph` disagreement stands. |
| **9** | **OPEN, and reclassified.** Round 2 re-measured `X-050`: all five documents still return 0 for `` `A-1` ``…`` `A-4` ``. It was **not** folded in, because rewriting a competitor verdict is a product judgement. Escalated rather than closed. |
| **10** | **DONE.** check-7 reports 0; see `X-045`. |
| **11** | **PARTLY.** The scenario **allocation marker** is exempted in check-2 and the gate no longer cries wolf — the marker is now `WH-SC-306`, round 2 having taken `WH-SC-301`–`WH-SC-305` for `SCENARIO-CATALOGUE.md` §3.21. **check-13 is still not written**, so `D-12` is still asserted rather than enforced — and `X-054` adds a **`check-15`** to the same queue. |
| **12** | **DONE.** Commit `dd5ac16`, *"cite the 36 COVERED-uncited BLOCKERs in their owning task files"*. `issues/README.md`'s round-1 traceability figure moved 385 → **427 of 575** as a direct result. |
| **13** | **MOSTLY DONE.** `X-049` and `X-053` are FIXED; `X-052`'s `M4` and `IRREVERSIBLE.md` §7.3 item 1 (`X-032`) are not. The eight report/archive tables all have `DATA-MODEL.md` rows. |

**Two items round 2 added to this list, both requiring a person rather than an author:**

- **`OD-9`'s deadline conflict** (round-2 finding `U-003`) — it must be answered **before `V520100`**, which is earlier than the date `DECISIONS.md` §3 records against it.
- **The accounting-side edit `OD-1` implies** (round-2 finding `O-001`) — due at the *accounting* set's P1, `V600136`–`V600137`, in a different repository. Nobody on this side can make it, and nobody on that side has been told.

---

## §6 · Checker remediation — the 2026-09-02 pass, 107 → 0

`tools/check-design-set.py` reported **107 violations** at the start of this pass and **0** at the end,
`exit 0`. The figure this repository previously quoted, **151**, was measured before the two census
documents (`GAP-REGISTER.md`, this file) declared their own id-naming fences; those were already in
place when the pass began, which is why the starting measurement was 107.

**The ground rule was that no check may be weakened, deleted or made advisory.** Every violation was
closed in exactly one of three ways, and each is named below.

| | Meaning |
|---|---|
| **FIX** | the design set was wrong and the document was corrected |
| **FENCE** | the mention is a legitimate quotation; a narrow, id-naming `begin`/`end` directive covers exactly those ids |
| **REPORT** | a real gap that could not be closed here — left failing where it fails, or recorded below |

### 6.1 Per check, measured

| check | before | after | exempt after |
|---|---:|---:|---:|
| 1 FR citations | 0 | **0** | 0 |
| 2 scenario citations | 26 | **0** | 45 |
| 3 table names | 46 | **0** | 22 |
| 4 Flyway band / ownership | 3 | **0** | 0 |
| 5 issue refs | skipped | **skipped** | — |
| 6 required sections | 0 | **0** | — |
| 7 finding ids | 8 | **0** | 52 |
| 8 plan ↔ files | 0 | **0** | — |
| 9 epic membership | 6 | **0** | — |
| 10 FR ownership | 3 | **0** | — |
| 11 id collisions | 14 | **0** | 0 |
| 12 screen ids | 1 | **0** | 13 |
| **total** | **107** | **0** | **132** |

### 6.2 FIX — what was corrected, and in which file

**Epics — `X-046`, script-breaking, done first.** `issues/03-EPIC-p2.md`, `04-EPIC-p2in.md`,
`05-EPIC-p3.md`, `06-EPIC-p4.md`, `07-EPIC-p5.md`, `08-EPIC-p6.md` each wrote `## __TASKS__` as the
heading itself with a hand-maintained checklist beneath. Each now carries `## Tasks`, a blank line and
`__TASKS__` alone — the shape `01-EPIC-p0.md` and `02-EPIC-p1.md` already had, and the shape
`issues/README.md` documents. **101 hand-maintained checklist rows deleted** (29 + 4 + 23 + 12 + 21 +
12); `create-issues.sh` generates that list from the real issue numbers. All nine epics were checked;
`00-EPIC-master.md` carries no placeholder and needed nothing.

**Flyway bands — `X-044`.**
- `issues/p2-29.md`, `issues/p3-04.md` — headers now name **`warehouse-base`** alongside `warehouse`,
  because both claim base-band grid-config numbers (`V501070`–`V501099`, `V501101`–`V501109`).
- `issues/p6-08.md` — the claim on **`V524000`–`V524099` is withdrawn**. `D-2` allocates a band to
  warehouse's five modules and to no other, and `FR-366` gives `logistics` no adapter, so this design
  set does not number that module's migrations. `docs/DECISIONS.md` `D-2`, `docs/DATA-MODEL.md` §2.5.6,
  §7.4 and §8.3 note 3 now say so: the adapter-band reservation `V524000`–`V524999` covers **warehouse-
  side enablement of the seam only**, and `P6-08` claims nothing in it.

**FR ownership — `X-039`.** `docs/IMPLEMENTATION-PLAN.md` §2's `P2-14` row carried a `grep` alternation
with two **escaped pipes**. A literal `|` splits a table row into **9 cells instead of 7**, moving the
`Closes` column from column 6 to column 8: a human transcribing the rendered table read `FR-224` and
`FR-225` correctly, every mechanical reader found `` `V510060` `` and reported both requirements as
owned by nobody while `p2-14.md` claimed them. The command is now described rather than quoted. §8.1's
traceability result was re-run with `assign.txt` generated from §2 rather than transcribed by hand:
**446 of 446 owned, none twice, none dangling** — unchanged numbers, now reproducible. **Never write a
literal or escaped `|` inside a §2 cell.**

**Table names — `X-053`, `X-002`, `X-003`, `X-012`.**
- *Typos (4 mentions, 3 in one file):* `wh_transport_details` → **`whb_transport_details`** in
  `issues/p2in-02.md` and twice in `issues/p2in-04.md`; and `issues/p6-09.md` cited a
  location-occupancy table that does not exist — `C-033`'s *recommendation column* names one, but the
  shape landed on **`whb_reservations`** (`FR-093`), which the row now says.
- *Genuinely missing (11 tables), added to `DATA-MODEL.md` §2 **and** §7, each with an owning number
  taken from that module's **declared** reserve, never by renumbering an existing claim:*

  | Tables | §2 | §7 | Number | Reserve it came from | Task |
  |---|---|---|---|---|---|
  | `whb_ratio_pack_templates`, `whb_ratio_pack_template_lines` | 2.1.5 | `WHB-64` | `V500064` | §7.2 post-v1 base DDL gap `V500064`–`V500199` | `P5-20` |
  | `whb_packaging_balances` | 2.1.4 | `WHB-65` | `V500065` | same gap | `P5-21` |
  | `whb_stock_movements_archive`, `whb_stock_movement_lines_archive`, `whb_movement_line_attributes_archive` | 2.1.14 | `WHB-66` | `V500100` | same gap | `P6-01` |
  | `wh_marketplace_claims` | 2.2.4 | `WH-115` | `V510215` | §7.3 correction reserve | `P5-13` |
  | `whin_eway_bill_lines`, `whin_eway_bill_events` | 2.4.1 | `WIN-05` | `V540030` | already that task's number | `P2-IN-04` |
  | `whin_form3cd_runs`, `whin_form3cd_lines` | 2.4.2 | `WIN-22` | `V540181` | §7.6 correction reserve | `P4-09` |

  The inventory block, §8.2 and §8.4 were recomputed rather than adjusted by hand: **290 → 301 tables**
  (base 92, app 119, india 50), `0` tables without an allocated migration. The plan's §8.3 migration
  count was likewise re-run: **914 → 818 numbers** (−100 for `P6-08`'s withdrawn block, +4 for the new
  claims), still exactly one owner each, still all in band. `issues/p5-20.md`, `p5-21.md`, `p5-13.md`,
  `p4-09.md`, `p6-01.md` had their headers and `⚠ has no migration` traps rewritten to record the
  closure, and the plan's §2 rows were updated to match.
- *Not tables at all (20 names):* `wh_rpt_*`, `whin_rpt_stock_by_mrp` and `wh3_rpt_custody_value` are
  **report grid identifiers** from `BUILD-SPEC-SCREENS.md` §7. `DATA-MODEL.md` §8.3 now carries them as
  note 4, enumerated with their screen and their source query, precisely so that the next author does
  not write a `CREATE TABLE` for one and create a second truth about a number the ledger already
  answers.

**Finding citations — `X-045`.** Five of the eight were **R2 capability-matrix row numbers cited as
findings**, the exact `DECISIONS.md` §7 rule 4a hazard. R2 was opened and each row identified, and each
citation in `docs/COMPETITOR-BENCHMARK.md` is now a section reference:

| Was | Is | R2 row actually says |
|---|---|---|
| `T-244` | `R2 §1.12 row 244` | Configurable RF flows without code — **V3** |
| `T-264` | `R2 §1.13 row 264` | FIFO costing over receipt layers — **V1**, the only v1 method |
| `T-325` | `R2 §1.16 row 325` | Fitment / installation consumption — **V1.1** |
| `T-326`…`T-337` | `R2 §1.17 rows 326–337` | the returns and reverse-logistics rows |

A standing rule was added to `COMPETITOR-BENCHMARK.md` §10: **cite a matrix row as `R2 §1.n row N`,
never as `T-N`** — R2 scores 392 rows and its findings stop at `T-097`. In
`docs/reviews/R6-prior-art-triage.md`, `§L E-1…E-8` is a *prior-art document's* own item numbering, not
R3 findings; it now reads `§L items 1–8`, which preserves the count and removes a false cross-reference
into R3's namespace.

**Id collision — `X-047`, the largest edit.** `DATA-MODEL.md` §6 numbers enforceable SQL constraints
`I-1`…`I-20`; `IRREVERSIBLE.md` numbered its rows `I-01`…`I-63`. From `I-10` up they were
**byte-identical** across roughly 250 mentions. **The irreversible register moved** — it is the newer of
the two and `DECISIONS.md` §6 had never granted it `I-` — to **`IRR-01`…`IRR-63`**.

It was done **file by file, in four passes, never as a blanket search-and-replace** (`DECISIONS.md` §7
rule 4, which exists because that operation corrupted the accounting decisions table twice):

1. `IRREVERSIBLE.md` itself — verified first to contain **no** single-digit `I-n` and **no** three-digit
   ids, so every token in it was its own: **384 replacements**.
2. The **237** mentions already carrying the local `IRR I-nn` qualifier — unambiguous by construction.
3. The **140** mentions unambiguous by shape: zero-padded `I-0n`, and `I-21`…`I-63` (outside the
   constraint register's 1–20 range). Every zero-padded mention was read in context first.
4. The **151** genuinely ambiguous `I-10`…`I-20` mentions, read one at a time. **Most were left
   alone**: `SCENARIO-CATALOGUE.md`'s 23 are all `` `L-n` · `I-nn` `` constraint pairings, `01-EPIC-p0.md`'s
   8 sit beside `I-18` in a constraint table, and every mention naming a migration file (`V500030`,
   `V500032`, `V500033`, `V500020`) is a constraint. **20 were converted** in
   `PORT-AND-ADAPTER-CONTRACT.md` and `INDIA-LOCALISATION-PACK.md` (both contain no single-digit `I-n`
   at all, and every hit was an irreversible column), and **11 more** individually in
   `p0-02.md`, `p1-01.md`, `p1-05.md`, `p1-07.md`, `p3-15.md`, `p4-07.md` and `GAP-REGISTER.md`.

**Result: 792 mentions renamed across the four passes** (384 + 237 + 140 + 20 + 11), leaving **808
`IRR-nn` mentions in the set** — the extra 16 are the new prose that records the rename. **63 distinct
ids, none outside 01–63, no three-digit token, no `IRR-IRR-`, and no residual `IRR I-` form.** The preambles that asserted the old, false position were corrected in
`IRREVERSIBLE.md` ("neither used anywhere else in the set" — it was) and in `DATA-MODEL.md`'s
id-namespace warning. `DECISIONS.md` §6 now declares the three registers it never had: **`IRR-nn`
irreversible rows**, **`WS-nnn` screens** (237 ids, the §1 index *is* the allocation), and **the R1 §8
`T-1`…`T-18` traps**, with the citation rule for the `T-n` / `T-nnn` split stated explicitly and the
reason a **review is never renumbered** recorded with it.

**One line of the checker changed, and only to follow the rename:** the `IRREVERSIBLE.md` definition
anchor and its §6 probe moved from `I-` to `IRR-`. Nothing was relaxed. The proof is the intermediate
state that was deliberately measured — with the ids renamed and the anchor updated but **before** §6
was amended, check 11 still reported *"§6 declares no namespace for the irreversible rows register
(`IRR-…`, 63 ids, authority docs/IRREVERSIBLE.md)"*. Same rule, same 63 ids, new prefix.

### 6.3 FENCE — every directive added, and why it is legitimate

**46 declarations suppress 118 mentions; a further 14 sit inside fenced code blocks, which every
citation check skips by construction — 132 in total.** No declaration is a path allowlist, none is
bare, and every one names the exact ids it covers, so a *new* dangling id in the same paragraph still
fails. The checker prints every count on every run and reports a declaration that suppresses nothing as
**stale**; there are none.

| Rule | Where | Ids named | Why it is a quotation, not a citation |
|---|---|---|---|
| `scenario-citations` | **31 declarations**: 27 region fences — `SCENARIO-CATALOGUE.md` §5, `issues/README.md`, `07-EPIC-p5.md`, `08-EPIC-p6.md` and the 23 P5/P6 tasks — plus 4 file-level, in this file, `GAP-REGISTER.md`, `GAP-REGISTER-R2.md` and `R10-operational-walkthrough.md` | `WH-SC-306` (`WH-SC-301` until 2026-09-02) | The §5 rule 3 **allocation marker** — the next free scenario id, which by definition has no row. Each task names it to reserve from it and to warn that two parallel tasks will both take 301 |
| `screen-citations` | `p5-13.md` `## Traps`, `DECISIONS.md` §6, plus the pre-existing fences in `issues/README.md` and the two census documents | `WS-238` | The `BUILD-SPEC-SCREENS.md` §1 **next-free marker**, named so a new screen takes it rather than reusing `WS-137`'s grid |
| `table-names` | 9 task-file sections: `p2in-01`, `p2in-04`, `p3-20`, `p4-02`, `p4-03`, `p4-05`, `p4-07`, `p4-12`, `p5-21` | 22 tables, each named on its fence | Two kinds. **Prior-art names** — `INDIA-LOCALISATION-PACK.md` §11.2's names for objects `DATA-MODEL.md` names differently; the trap exists to carry the divergence and to say the data model wins. **Counter-examples** — `whaf_van_stock` ("the moment the van becomes a quantity table there are two stock truths") and `wh_tyre_fitments` ("building it here is precisely how the boundary rots"). Both are named so they are *not* built |
| `finding-citations` | `COMPETITOR-BENCHMARK.md` §10's counting table, plus the two pre-existing census fences | `E-754` | **Not a fabrication.** `E-754` is the tail of *IEEE-754* at `docs/reviews/R1-codebase-reality.md:441` — verified — and §10 names the token to explain why the counting command's word boundary excludes it |

The pre-existing whole-file declarations in `GAP-REGISTER.md` and this file were left as they are: both
documents exist *to* quote every broken id, the census entries are spread across their whole length,
and both declarations already name their ids, which is the narrowing that matters.

### 6.4 REPORT — what is still open

Nothing is left failing the checker. These are real gaps the checker cannot see, recorded so they are
not lost:

| # | Open item | What would close it |
|---|---|---|
| **R-1** | **`WS-238` has no row.** `X-001` stays open. `P5-13`'s claim queue now has its table (`wh_marketplace_claims`, `WH-115`, `V510215`) but still no screen id | Add the `WS-238` row to `BUILD-SPEC-SCREENS.md` §1 and drop the two task-side fences |
| **R-2** | **`P5-21`'s movement-linked entry table is unnamed.** Its acceptance says *"the balance reconciles to the sum of its entries"*; `whb_packaging_balances` was allocated, the entry table was **not invented** | `P5-21` names it, adds the §2.1.4 row and puts the number in `WHB-65`, in one PR |
| **R-3** | **`P6-01`'s archive-run record is unallocated.** The choice between extending `whb_job_runs` and a new `whb_archive_runs` is the task's, not this document's. **Amended 2026-09-02:** the three archive *tables* are now allocated — `WHB-66`/`V500100` (`DATA-MODEL.md:2932`) — so the run record can no longer go there. `WHB-67`/`V500066` was taken by `P5-22` in round 2 | `P6-01` picks one; the row goes in §2.1.14 and the number into **the next free base id, `WHB-68`**, not `WHB-66` |
| **R-4** | **`DEFECTS-FOUND.md` does not exist.** Fourteen task files and both epics cite it; the file in this repository is `docs/DESIGN-SET-DEFECTS.md`. No check covers a dangling *document* reference | Decide whether it is this file renamed or a separate log, then fix the citations — and consider a check-14 for document references |
| **R-5** | **`INDIA-LOCALISATION-PACK.md` §11.2 group F is owned by nobody.** `whin_packaged_commodity_declarations`, `whin_mrp_revisions`, `whin_instrument_verifications`: `P4-05` names them precisely to say no §2 task owns them. They are fenced as an unowned gap, **not** allocated — allocating a row would have hidden the gap | `FR-223` is v2 · P5; either a task claims them or the pack records them as out of scope |
| **R-6** | **Three non-failing Flyway advisories**, all correct: `p5-01:70` `V531100`, `p5-09:48` `V510126` cite blocks another task owns; `p6-08:131` `V524000` is the reserved logistics block this set no longer claims | Nothing — they are advisories by design and should not be silenced |
| **R-7** | **Check 5 is still skipped.** `issues/CREATED.md` does not exist, and **231 bare `#NN`** will become check-5 subjects the moment it does — most are document row numbers that will *resolve, to the wrong thing* | Before filing, rewrite row numbers as `row 116` or in a code span, and cross-repo issues as `owner/repo#791` |

### 6.5 What this pass did not do

- **No check was weakened, deleted or made advisory.** One checker line changed, to follow a rename,
  and the register it resolves is still enforced — §6.2 records the measurement that proves it.
- **No id was blanket search-and-replaced.** Every one of the 792 renamed mentions was reached by a
  pass whose ambiguity had first been eliminated, and the 151 genuinely ambiguous ones were read in
  context one at a time. 131 of them were **correctly left alone**.
- **No number was invented.** Every migration number came from a reserve the module had already
  declared, and no existing claim was renumbered.
- **No count was asserted.** `DATA-MODEL.md` §8.2, §8.4 and `IMPLEMENTATION-PLAN.md` §8.1, §8.3 were
  re-run with the documents' own commands and their stated outputs replaced with what those commands
  actually produced.
