# Issue backlog — the source of truth

The full Classic Warehouse backlog, ready to file on GitHub: **1 master epic + 8 phase epics + 138
task issues = 147 issues**, 16,719 lines of task and epic text.

Every count on this page was computed, not estimated. The command is next to the number, and
the checker figures are from the run of **2026-09-02 08:25 IST** — the design set is under active
authoring, so re-run before quoting one.

```bash
ls issues/p*.md | wc -l              # 138 tasks
ls issues/0*-EPIC-*.md | wc -l       #   9 epics (1 master + 8 phase)
```

Written in the shape the Assets remediation uses in `neetub1508/classic-issues` and the accounting
set uses in `neetub1508/accounting` — epics carry Overview → Exit criterion → Invariants → Tasks
checklist → traps → Definition of done; task issues open with
`Part of #EPIC · Module · Migrations · Screens`.

---

## The backlog is **not filed yet** — read this before running the script

`issues/CREATED.md` does not exist, no file carries an `issue: NN` line, and
`tools/check-design-set.py --check 5` skips cleanly and says so. That is the current state.

**`DECISIONS.md` §7 rule 5 fixes the authority direction now, before anything is filed:**

> The `.md` files in this repository are authoritative; GitHub issue bodies are a **mirror** kept in
> sync mechanically by `issues/create-issues.sh --sync`, and `--check` fails CI on drift. **Never
> edit an issue body in the GitHub UI.**

This is not a preference. The accounting programme inverted it once — round 2 corrected 91 filed
bodies in place on GitHub and declared GitHub the winner — and round 3 then amended **86 of the 91
`.md` files** without pushing any of it back. A builder following the stated rule read the stale
artefact for weeks (accounting round 4, `B-003`). Reconciling in the other direction meant re-keying
~1,140 lines by hand and would have left the same failure mode in place.

So: **files win, and the files are pushed to GitHub mechanically.**

```bash
gh auth login                                   # needs a token with Issues: write
./issues/create-issues.sh --dry-run             # walks all 147 without writing anything
./issues/create-issues.sh                       # files the backlog, first run only
./issues/create-issues.sh --sync                # push every .md to its issue
./issues/create-issues.sh --check               # diff filed bodies against the .md; non-zero on drift
REPO=owner/other-repo ./issues/create-issues.sh # stand this backlog up somewhere else
```

`create-issues.sh` **refuses to run the create path against a repository that already has issues**,
so a re-run cannot duplicate 147 issues or orphan every cross-reference in the first set. Once filed
it remains useful for standing the backlog up in a *different* repository, and `--sync` / `--check`
are what you use from then on.

## What the script does, in order

1. creates the **22 labels** the files name — there is no other create-label step anywhere
2. master epic
3. **8 phase epics** — P0 · P1 · P2 · **P2-IN** · P3 · P4 · P5 · P6, each linked back to the master
4. **138 task issues**, each linked back to its phase epic
5. phase epics patched with their real task checklists
6. master epic patched with the real phase-epic numbers
7. writes `issues/CREATED.md` — the map `tools/check-design-set.py` check 5 resolves every `#NN`
   against — and stamps an `issue: NN` line into each file's front matter, so `--sync` and `--check`
   need no hand-keyed list of 147 numbers

## File format

Every issue file is **`TITLE:` / `LABELS:` / `---` / body**:

```
TITLE: [Warehouse] P0-02 · The ledger — movements, lines, positions and every invariant trigger
LABELS: task,warehouse,phase-p0,warehouse-base
---
Part of __P0__ · Module **`warehouse-base`** · Migrations **V500030–V500032, V500036** · Screens …
```

`create-issues.sh` reads the title from `TITLE:`, the labels from `LABELS:`, and the body as
everything after the first `---`. After filing, an `issue: NN` line is written between `LABELS:` and
`---`; it stays out of the body because the body starts after the `---`.

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
| `00-EPIC-master.md` | Master epic — the 13 decisions, five modules, the Flyway bands, the 14 invariants, the version ladder, `OD-1`…`OD-11`, the definition of done |
| `01-EPIC-p0.md` | **P0** Ledger foundation · `warehouse-base` · 16 migration blocks · **v1** |
| `02-EPIC-p1.md` | **P1** Masters, identity, inbound · base + app · **v1** |
| `03-EPIC-p2.md` | **P2** Outbound, counting, valuation, returns, printing, reports · **v1** |
| `04-EPIC-p2in.md` | **P2-IN** The India movement documents · `warehouse-india` wave 1 · **v1** |
| `05-EPIC-p3.md` | **P3** Execution & mobile · **v1.1** |
| `06-EPIC-p4.md` | **P4** India statutory & compliance · `warehouse-india` wave 2 · **v2** |
| `07-EPIC-p5.md` | **P5** 3PL, channels and reverse logistics · **v2** |
| `08-EPIC-p6.md` | **P6** Optimisation, planning and the logistics seam · **v3** |
| `p0-01.md` … `p0-17.md` | **17** P0 tasks |
| `p1-01.md` … `p1-20.md` | **20** P1 tasks |
| `p2-01.md` … `p2-29.md` | **29** P2 tasks |
| `p2in-01.md` … `p2in-04.md` | **4** P2-IN tasks — phase **`P2-IN`**, epic `04-EPIC-p2in.md`, placeholder `__P2IN__` |
| `p3-01.md` … `p3-23.md` | **23** P3 tasks |
| `p4-01.md` … `p4-12.md` | **12** P4 tasks |
| `p5-01.md` … `p5-21.md` | **21** P5 tasks |
| `p6-01.md` … `p6-12.md` | **12** P6 tasks |
| `DEFECTS-FOUND.md` | Defects found while authoring the task files — not an issue |
| `create-issues.sh` | The filing and sync tool |

`p2in-*` is the one place where the file stem (`p2in`), the phase id (`P2-IN`), the placeholder
(`__P2IN__`) and the epic number (`04`) all differ. The glob `p2-*.md` does not match `p2in-*.md`,
so the two phases stay separate by construction.

## Task ids are phase-prefixed, and that is deliberate

`P0-01` … `P6-12`, matching the filenames — **138 ids**, `ls issues/p*.md | wc -l`. The ids must never
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
  parallel work cannot collide. **915 versions are claimed across 138 tasks with zero duplicates**;
  33 tasks write no migration, which is not a defect — the DDL sits in another task, or the work is
  service, frontend or registry only
- the **screens** (`WS-nnn` from `BUILD-SPEC-SCREENS.md`)
- **`## Requirements closed`** — the `FR-nnn` this task owns. Every FR is owned by exactly one task
- **`## Scenarios closed`** — the `WH-SC-nnn` its acceptance criteria are tied to
- **`## Closes`** — the review findings it dispositions
- **`## Traps`** — the traps *specific to this codebase* that will otherwise cost a rebuild cycle,
  each with `file:line` evidence from `reviews/R1`
- **`## Acceptance`** — checkboxes, each naming the scenario that proves it
- **`## Blocked on`** — on the **24** tasks that are gated on an open decision

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
# 138 tasks, and the plan's §2 table agrees in both directions
ls issues/p*.md | wc -l                                                  # 138
python3 tools/check-design-set.py --check 8                              # pass

# every requirement is owned by exactly one task
grep -ohE '\bFR-[0-9]{3}\b' issues/p*.md | sort -u | wc -l               # 446 of 446
python3 tools/check-design-set.py --check 10                             # pass

# every review finding is cited by the task that closes it
grep -ohE '\b[CTEFSPG]-[0-9]{3}\b' issues/p*.md | sort -u | wc -l        # 385 of 575

# scenarios, screens and tables the tasks reach for
grep -ohE '\bWH-SC-[0-9]{3}\b' issues/p*.md | sort -u | wc -l            # 299 (298 real + WH-SC-301)
grep -ohE '\bWS-[0-9]{3}\b'    issues/p*.md | sort -u | wc -l            # 238 (237 real + WS-238)
grep -ohE '\b(whb|wh3|whin|wha[a-z]|wh)_[a-z0-9_]+\b' issues/p*.md | sort -u | wc -l   # 330

# the whole gate
python3 tools/check-design-set.py --summary                              # 0 violations, exit 0
```

<!-- check-design-set: scenario-citations begin WH-SC-301 - the allocation marker named as the subject of this paragraph, not cited as a scenario -->
<!-- check-design-set: screen-citations begin WS-238 - the next free screen id named as the subject of this paragraph, not cited as a screen -->

Read those last three the way the checker does. **301 scenario ids** is all 300 of the catalogue
plus the `WH-SC-301` allocation marker. `WH-SC-170` and `WH-SC-204` were the last two cited by no
task; `X-041` closed them on 2026-09-02 into `P2-01` and `P2-14`, so **every scenario in the
catalogue is now walked by a task**. **238
screen ids** is 237 real ones plus `WS-238`, which `p5-13` claims for the marketplace-claim queue
before `BUILD-SPEC-SCREENS.md` §1 allocates it — **the table it also needed now exists**
(`wh_marketplace_claims`, `WH-115`, `V510215`); the screen id is still to be allocated.
**330 table names** is down from 332 because two were typos for tables that already existed. **385 of 575 findings** are cited by a task; the
remaining 190 are dispositioned in `docs/GAP-REGISTER.md`, whose own §4 says fourteen are owned by
nothing — read that document, not this line, for the honest number.

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
