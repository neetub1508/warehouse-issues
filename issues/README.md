# Issue backlog — the source of truth

The full Classic Warehouse backlog, **filed on GitHub** in `neetub1508/warehouse-issues`:
**1 master epic + 8 phase epics + 143 task issues = 152 issues**, 17,362 lines of task and epic text.
**Round 4 (2026-09-10) added six task files — `p3-25`, `p5-24`…`p5-28` — so the backlog is now 149
task files: 143 filed + 6 to file** (`GAP-REGISTER-R4.md` §4.0, `D-14` item 7).

Every count on this page was computed, not estimated. The command is next to the number, and
the checker figures are from the run of **2026-09-02 08:25 IST** — the design set is under active
authoring, so re-run before quoting one.

```bash
ls issues/p*.md | wc -l              # 149 tasks (143 filed + 6 round-4 files to file)
ls issues/0*-EPIC-*.md | wc -l       #   9 epics (1 master + 8 phase)
```

Written in the shape the Assets remediation uses in `neetub1508/classic-issues` and the accounting
set uses in `neetub1508/accounting` — epics carry Overview → Exit criterion → Invariants → Tasks
checklist → traps → Definition of done; task issues open with
`Part of #EPIC · Module · Migrations · Screens`.

---

## The backlog is **filed** — read this before touching anything

All **152** issues exist. `issues/CREATED.md` is written and holds the full
`Issue | Task file | Title` map; **every one of the 152 files carries an `issue: NN` line** in its
front matter; and `tools/check-design-set.py --check 5` therefore no longer skips — it resolves
every `#NN` cross-reference against that map.

| | |
|---|---|
| Master epic | `#1` |
| Phase epics | P0 `#3` · P1 `#4` · P2 `#5` · P2-IN `#6` · P3 `#7` · P4 `#8` · P5 `#10` · P6 `#11` |
| The 143 filed tasks | **`#12`–`#154`** |
| Round 4's six task files | **not yet filed** — `p3-25`, `p5-24`, `p5-25`, `p5-26`, `p5-27`, `p5-28` carry no `issue:` line |

**Six new files await `create-issues.sh`.** They were authored without an `issue:` line, as
`GAP-REGISTER-R3.md` §4.3 requires, because a hand-typed number is how cross-references rot. Until they
are filed, `CREATED.md` has no row for them and `--sync` / `--check` skip them. The create path refuses a
repository that already has issues (below), so filing them is a deliberate single-file step, not a
re-run of the whole backlog.

**`#2` and `#9` are pull requests, not issues.** GitHub numbers issues and pull requests from one
sequence per repository, and two PRs were opened while the backlog was being filed. That is the
whole reason the phase epics are not `#2`–`#9` and the tasks are not `#10`–`#152`. **Nothing is
missing from the backlog** — the two absent numbers are the PRs.

**`DECISIONS.md` §7 rule 5 fixes the authority direction, and it is now load-bearing rather than
prospective:**

> The `.md` files in this repository are authoritative; GitHub issue bodies are a **mirror** kept in
> sync mechanically by `issues/create-issues.sh --sync`, and `--check` fails CI on drift. **Never
> edit an issue body in the GitHub UI.**

This is not a preference. The accounting programme inverted it once — round 2 corrected 91 filed
bodies in place on GitHub and declared GitHub the winner — and round 3 then amended **86 of the 91
`.md` files** without pushing any of it back. A builder following the stated rule read the stale
artefact for weeks (accounting round 4, `B-003`). Reconciling in the other direction meant re-keying
~1,140 lines by hand and would have left the same failure mode in place.

So: **files win, and the files are pushed to GitHub mechanically.** Now that the backlog is filed,
the only two commands that matter are `--sync` (push every `.md` to its issue) and `--check` (fail
CI on drift). **Never edit an issue body in the GitHub UI** — an edit there is drift `--check` will
flag and `--sync` will overwrite.

```bash
gh auth login                                   # needs a token with Issues: write
./issues/create-issues.sh --dry-run             # walks all 147 without writing anything
./issues/create-issues.sh                       # files the backlog, first run only
./issues/create-issues.sh --sync                # push every .md to its issue
./issues/create-issues.sh --check               # diff filed bodies against the .md; non-zero on drift
REPO=owner/other-repo ./issues/create-issues.sh # stand this backlog up somewhere else
```

`create-issues.sh` **refuses to run the create path against a repository that already has issues** —
which `neetub1508/warehouse-issues` now does — so a re-run cannot duplicate the 152 or orphan every
cross-reference in the first set. The create path remains useful only for standing the backlog up in
a *different* repository; **`--sync` / `--check` are what you use from here on.**

## What the script does, in order

1. creates the **22 labels** the files name — there is no other create-label step anywhere
2. master epic
3. **8 phase epics** — P0 · P1 · P2 · **P2-IN** · P3 · P4 · P5 · P6, each linked back to the master
4. **143 task issues**, each linked back to its phase epic
5. phase epics patched with their real task checklists
6. master epic patched with the real phase-epic numbers
7. writes `issues/CREATED.md` — the map `tools/check-design-set.py` check 5 resolves every `#NN`
   against — and stamps an `issue: NN` line into each file's front matter, so `--sync` and `--check`
   need no hand-keyed list of 152 numbers

## File format

Every issue file is **`TITLE:` / `LABELS:` / `---` / body**:

```
TITLE: [Warehouse] P0-02 · The ledger — movements, lines, positions and every invariant trigger
LABELS: task,warehouse,phase-p0,warehouse-base
---
Part of __P0__ · Module **`warehouse-base`** · Migrations **V500030–V500032, V500036** · Screens …
```

`create-issues.sh` reads the title from `TITLE:`, the labels from `LABELS:`, and the body as
everything after the first `---`. The `issue: NN` line sits between `LABELS:` and `---`; it stays
out of the body because the body starts after the `---`. **All 152 files carry theirs** — `p0-02.md`
carries `issue: 25`, one line below its `LABELS:` and one above its `---` — which is what makes
`--sync` and `--check` work with no hand-keyed list of 152 numbers.

> The line is deliberately **not** reproduced at the left margin anywhere on this page.
> `create-issues.sh` reads it with `sed -n 's/^issue: *//p'`, which does not know a fenced code
> block from a file, so an example here would make this README look like issue #25 and `--sync`
> would overwrite that issue with this page. Read a real file for the shape.

`DEFECTS-FOUND.md` and this README live in `issues/` and declare no `TITLE:`, so the script skips
them. They are documents, not issues.

## The placeholder mechanism — why these files are not valid issue bodies

Ten placeholders are substituted with real issue numbers **at creation time**:

| Placeholder | Becomes | Appears in |
|---|---|---|
| `__MASTER__` | `#N` of the master epic | all 8 phase epics |
| `__P0__` … `__P6__`, `__P2IN__` | `#N` of that phase epic | the master epic, and every task of that phase |
| `__TASKS__` | the phase's task checklist, `- [ ] #N · P0-01 · …` | each phase epic, once |

A file read straight off disk therefore contains `Part of __P0__`, which is not a link. **The files
are not valid issue bodies until the script runs.** That is deliberate: hand-keying 147 numbers into
147 files is how cross-references rot.

Two rules the script enforces, both learned the hard way:

- **A placeholder inside a fenced code block is left alone.** `01-EPIC-p0.md` and `02-EPIC-p1.md`
  document a runnable command — ``grep -h '^Part of __P0__' issues/p0-*.md`` — and substituting there
  would file an example that silently matches nothing.
- **`__TASKS__` must be alone on its own line.** It is replaced by a multi-line checklist; on a line
  with anything else the substitution corrupts that line. Six phase epics currently write
  `## __TASKS__` — the placeholder *as* the heading — with a hand-maintained checklist below it. The
  script **refuses to file** in that state and names the file and line;
  `tools/check-design-set.py --check 9` reports the same six, so CI catches it first. The fix is
  three lines per epic: a `## Tasks` heading, a blank line, `__TASKS__`, and delete the hand-written
  list the script now generates.

## Layout

| File | What it is |
|---|---|
| `00-EPIC-master.md` | Master epic — the 14 decisions (`D-14` from round 4), five modules, the Flyway bands, the 14 invariants, the version ladder, `OD-1`…`OD-11`, the definition of done |
| `01-EPIC-p0.md` | **P0** Ledger foundation · `warehouse-base` · 16 migration blocks · **v1** |
| `02-EPIC-p1.md` | **P1** Masters, identity, inbound · base + app · **v1** |
| `03-EPIC-p2.md` | **P2** Outbound, counting, valuation, returns, printing, reports · **v1** |
| `04-EPIC-p2in.md` | **P2-IN** The India movement documents · `warehouse-india` wave 1 · **v1** |
| `05-EPIC-p3.md` | **P3** Execution & mobile · **v1.1** |
| `06-EPIC-p4.md` | **P4** India statutory & compliance · `warehouse-india` wave 2 · **v2** |
| `07-EPIC-p5.md` | **P5** 3PL, channels and reverse logistics · **v2** |
| `08-EPIC-p6.md` | **P6** Optimisation, planning and the logistics seam · **v3** |
| `p0-01.md` … `p0-17.md` | **17** P0 tasks |
| `p1-01.md` … `p1-21.md` | **21** P1 tasks |
| `p2-01.md` … `p2-29.md` | **29** P2 tasks |
| `p2in-01.md` … `p2in-04.md` | **4** P2-IN tasks — phase **`P2-IN`**, epic `04-EPIC-p2in.md`, placeholder `__P2IN__` |
| `p3-01.md` … `p3-25.md` | **25** P3 tasks — `p3-25` is round 4's |
| `p4-01.md` … `p4-13.md` | **13** P4 tasks |
| `p5-01.md` … `p5-28.md` | **28** P5 tasks — `p5-24`…`p5-28` are round 4's |
| `p6-01.md` … `p6-12.md` | **12** P6 tasks |
| `DEFECTS-FOUND.md` | Defects found while authoring the task files — not an issue |
| `create-issues.sh` | The filing and sync tool |

`p2in-*` is the one place where the file stem (`p2in`), the phase id (`P2-IN`), the placeholder
(`__P2IN__`) and the epic number (`04`) all differ. The glob `p2-*.md` does not match `p2in-*.md`,
so the two phases stay separate by construction.

## Task ids are phase-prefixed, and that is deliberate

`P0-01` … `P6-12`, matching the filenames — **149 ids**, `ls issues/p*.md | wc -l`. The ids must never
collide with anything else in this design set. `DECISIONS.md` §6 fixes the namespaces:

> Tasks `P0-01`… · Requirements `FR-001`… · Decisions `D-1`… · Open decisions `OD-1`… · Invariants
> `L-1`…`L-14` · Enforceable constraints `I-1`…`I-20` · Irreversible rows `IRR-01`…`IRR-63` ·
> Scenarios `WH-SC-001`… · Screens `WS-001`…`WS-237` · Findings `C-`/`T-`/`E-`/`F-`/`S-`/`P-`/`G-`
> per review · R1 §8 traps `T-1`…`T-18`, unpadded.

`P-001` (R6 prior-art findings) and `P0-01` (a task) are distinguishable because a task id always
carries a phase digit. `tools/check-design-set.py --check 11` asserts no id is used for two kinds of
thing. It found one collision nobody had named — `I-10`…`I-20`, defined by **both** `DATA-MODEL.md`
(enforceable constraints) and `IRREVERSIBLE.md` (irreversible rows), byte-identical across ~250
mentions. **Resolved 2026-09-02** by renaming the irreversible register to `IRR-01`…`IRR-63`, file by
file and verified in context, and by declaring `IRR-`, `WS-` and the `T-n`/`T-nnn` split in
`DECISIONS.md` §6.

## What every task issue carries

- **`## Scope`** — the build list
- the **module** it lands in and its **pre-allocated migration numbers**, on the header line, so
  parallel work cannot collide. **851 migration numbers are allocated across 149 tasks with zero
  duplicates and none outside its module's band** (823 before round 4, which claimed twenty-nine and
  released `V500061`) — the computed figure and the script that produces
  it are `IMPLEMENTATION-PLAN.md` §8.3, which is the one place this number is derived; **33 tasks
  write no migration**, which is not a defect — the DDL sits in another task, or the work is
  service, frontend or registry only

  > **This line previously read *"915 versions"*, a figure no command in this repository reproduces
  > and which disagreed with §8.3's own run. Recorded rather than silently corrected, per
  > `DECISIONS.md` §7 rule 1.**
- the **screens** (`WS-nnn` from `BUILD-SPEC-SCREENS.md`)
- **`## Requirements closed`** — the `FR-nnn` this task owns. Every FR is owned by exactly one task
- **`## Scenarios closed`** — the `WH-SC-nnn` its acceptance criteria are tied to
- **`## Closes`** — the review findings it dispositions
- **`## Traps`** — the traps *specific to this codebase* that will otherwise cost a rebuild cycle,
  each with `file:line` evidence from `reviews/R1`
- **`## Acceptance`** — checkboxes, each naming the scenario that proves it
- **`## Blocked on`** — on the **25** tasks that are gated on an open decision
  (`grep -l '^## Blocked on' issues/p*.md | wc -l`; round 4 added `P5-09` → `OD-18`)

## The six tasks that carry the most risk

`IMPLEMENTATION-PLAN.md` §4 ranks these, and each one names the *consequence*, not the difficulty.

| Task | Consequence if it is wrong |
|---|---|
| **P0-02** · the ledger | **Rebuild the product.** `PNR-1` and `PNR-2` collapsed into one migration. After `V500030` runs, a column added to either ledger table is `NULL` forever on every row that already existed, **to every actor including `ADMIN`** — `ALTER TABLE … ADD COLUMN` is DDL and the append-only trigger does not block it, the backfill is an `UPDATE` and the trigger does. There is no later window |
| **P0-06** · owners | **Rebuild `warehouse-3pl`.** `owner_id` is `NOT NULL` on every line, position, lot, serial, LPN, reservation and cost layer from v1. There is no rule that recovers whose a unit was, so the column is free now and unbackfillable later. Four lenses reached this independently |
| **P0-04** · the open catalogues | **A base release per adapter, forever.** A `CHECK` constraint, a Java enum or a TypeScript union on a movement type, stock status or reason code means every new adapter needs a `warehouse-base` migration — which is the loose-coupling claim failing on its first integration |
| **P0-08** · the movement port | **A wire contract you cannot take back.** The envelope, the idempotency conflict semantics and the v1 offline hooks ship before any consumer exists, and every future consumer is bound by them |
| **P0-03** · the writer service | **No precedent to copy.** The single-writer rule, computed availability, the concurrency discipline and the `L-4` full-rebuild proof have no equivalent anywhere in this repository |
| **P2-16** · the costing engine | **The number the customer signs.** `D-6` gives warehouse the costing engine wherever it is installed, because only warehouse holds the grain FEFO and specific identification need |

## Traceability — the commands, and what they actually return

Run these after any change to the backlog. Each audit round of the accounting programme found that
the *previous* round's findings were indexed and not traced; indexing feels like closure and is not.

```bash
# 149 tasks, and the plan's §2 table agrees in both directions
ls issues/p*.md | wc -l                                                  # 149
python3 tools/check-design-set.py --check 8                              # pass

# every requirement is owned by exactly one task
grep -ohE '\bFR-[0-9]{3}\b' issues/p*.md | sort -u | wc -l               # 469 of 469
python3 tools/check-design-set.py --check 10                             # pass once the FRD's §6.28 lands

# every review finding is cited by the task that closes it
grep -ohE '\b[CTEFSPG]-[0-9]{3}\b' issues/p*.md | sort -u | wc -l        # 427 of 575  (round 1)
grep -ohE '\b[QHUYZKOJ]-[0-9]{3}\b' issues/p*.md | sort -u | wc -l        #  46 of  62  (round 2)
grep -ohE '\bR[GHJKL]-[0-9]{3}\b' issues/p*.md | sort -u | wc -l         #  80 of  83  (round 4)

# scenarios, screens and tables the tasks reach for
grep -ohE '\bWH-SC-[0-9]{3}\b' issues/p*.md | sort -u | wc -l            # 324 (catalogue: 327 once §3.22 lands)
grep -ohE '\bWS-[0-9]{3}\b'    issues/p*.md | sort -u | wc -l            # 240 (237 + WS-238 + WS-240 + WS-241)
grep -ohE '\b(whb|wh3|whin|wha[a-z]|wh)_[a-z0-9_]+\b' issues/p*.md | sort -u | wc -l   # 391

# the whole gate
python3 tools/check-design-set.py --summary                              # 0 violations, exit 0
```

<!-- check-design-set: scenario-citations begin WH-SC-328 - the allocation marker named as the subject of this paragraph, not cited as a scenario -->
<!-- check-design-set: screen-citations begin WS-238 WS-239 WS-242 - WS-238 and WS-239 are reserved for round 3 (WS-238 is also claimed by p5-13), and WS-242 is the next free screen id; all three are named as the subject of this paragraph, not cited as screens -->

**The figures above were computed on 2026-09-10 against the P-LATE tree, before the other three round-4
fold partitions merged. Re-run them after the merge** (`GAP-REGISTER-R4.md` §4.1 rule 3). The
scenario, round-2 and table figures move when the other partitions' task files land.

Read those last three the way the checker does. **The scenario marker is now `WH-SC-328`.** Round 4
took `WH-SC-306`–`WH-SC-327` for §3.22 and moved the marker, just as round 2 took
`WH-SC-301`–`WH-SC-305` for §3.21. That movement is the reason the marker exists. `WH-SC-170` and `WH-SC-204` were the last two cited by no
task; `X-041` closed them on 2026-09-02 into `P2-01` and `P2-14`, so **every scenario in the
catalogue is now walked by a task**. **240
screen ids** is 237 real ones, plus `WS-240` (`P5-25`) and `WS-241` (`P5-27`) from round 4, plus
`WS-238`. **The screen marker is now `WS-242`.** `p5-13` claims `WS-238` for the marketplace-claim
queue before `BUILD-SPEC-SCREENS.md` §1 allocates it — **the table it also needed now exists**
(`wh_marketplace_claims`, `WH-115`, `V510215`). But `GAP-REGISTER-R4.md` §4.0 **reserves `WS-238` and
`WS-239`** for round 3's `RA-001` and `RA-002`. The two claims on `WS-238` collide, and the next screen
allocation must settle it. That is recorded here, not decided.
**391 table names** is up from 345: the round-4 files name the junctions and side tables
`GAP-REGISTER-R4.md` §4.2 owes to `DATA-MODEL.md` §2, plus two fenced counter-examples (`whb_rfid_reads` in `p3-24`, `wh_damage_claims` in `p5-23`)
which are named **so they are not built** and are excluded from check-3 by their own fences.

**427 of 575 round-1 findings** are cited by a task — up from 385 when `X-050` closed the 36
COVERED-uncited BLOCKERs into their owning files; the remaining 148 are dispositioned in
`docs/GAP-REGISTER.md`, whose own §4 says fourteen are owned by nothing — read that document, not
this line, for the honest number. **7 of 62 round-2 findings** are cited by a task, and that low
number is correct rather than alarming: `GAP-REGISTER-R2.md` §2.1 dispositions 51 of the 62 as
`FOLD-TASK` or `FOLD-DOC` amendments to text that already exists, and only the five new tasks carry a
round-2 id in a `## Closes` block.

**80 of 83 round-4 findings** (`RG-`, `RH-`, `RJ-`, `RK-`, `RL-`) are cited by a task file, measured on
the same partial tree. `GAP-REGISTER-R4.md` §2 dispositions all 83. The six new task files carry their
own `## Closes` blocks: `RK-003` (`P3-25`), `RG-010`…`RG-014`, `RG-018` and `RG-020` (`P5-24`), `RK-006`
(`P5-25`), `RK-007` (`P5-26`), `RK-008` (`P5-27`) and `RL-015` (`P5-28`). Requirements now run to
`FR-469`, and the screen marker is `WS-242`.

<!-- check-design-set: screen-citations end -->
<!-- check-design-set: scenario-citations end -->

## Before you file

```bash
python3 tools/check-design-set.py       # must pass, or you know why each violation is accepted
./issues/create-issues.sh --dry-run     # must reach "==> 6/6", not "REFUSING:"
```

**The dry run no longer stops at `REFUSING:`.** All six epics that wrote `## __TASKS__` as the heading
now carry a real `## Tasks` heading with the placeholder alone on the line beneath it, and the 101
hand-maintained checklist rows below them are deleted — the script generates that list from the real
issue numbers. `tools/check-design-set.py --check 9` passes, which is the same assertion made earlier
in CI.
