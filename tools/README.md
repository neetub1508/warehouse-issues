# tools

## `check-design-set.py` — design-set integrity checker

`DECISIONS.md` §7 rule 3 is the whole reason this file exists:

> **Every cross-reference must resolve.** `FR-nnn` to a real requirement, `WH-SC-nnn` to a real
> scenario, a table name to a row in `DATA-MODEL.md`, an issue `#NN` to a row in
> `issues/CREATED.md`, a migration number to exactly one task inside its module's band.
> `tools/check-design-set.py` enforces all of it.

The design set is prose, but it is **built from as if it were a schema**. `DATA-MODEL.md` is the
migration authority, `## Scope` is the build list, `FR-nnn` / `WH-SC-nnn` citations are the
acceptance contract, and the `Part of …` header line is the migration allocation. When one of those
references dangles, nothing breaks loudly — a live gap simply reads as **closed**.

```bash
python3 tools/check-design-set.py              # full report, one line per violation
python3 tools/check-design-set.py --summary    # counts only
python3 tools/check-design-set.py --check 4    # one check (repeatable: --check 4 --check 11)
python3 tools/check-design-set.py --show-exempt # every mention an exemption swallowed
python3 tools/check-design-set.py --root PATH  # a different checkout
python3 tools/check-design-set.py --no-advisory # drop the non-failing notes
```

Exit status: **0** clean · **1** violations found · **2** bad invocation or a missing authority file.
Python 3 **standard library only** — no dependency to install, so CI needs nothing but `python3`.
This is deliberate: the repo has no build tooling, and a checker that needs `pip install` is a
checker that gets skipped.

---

## The twelve checks, and the specific failure each one prevents

| # | Invariant | Authority | The failure it prevents |
|---|---|---|---|
| 1 | every `FR-nnn` cited anywhere resolves | `docs/WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` | see **Why check 1** below — the single most expensive defect the accounting programme shipped |
| 2 | every `WH-SC-nnn` cited anywhere resolves | `docs/SCENARIO-CATALOGUE.md` | a scenario id that is a *sequential fabrication*: acceptance criteria that name a test nobody wrote |
| 3 | every `whb_`/`wh_`/`wh3_`/`whin_`/`wha*_` table named in a task file exists | `docs/DATA-MODEL.md` | a task whose DDL nobody has designed, discovered at migration-writing time |
| 4 | every Flyway version is claimed by **exactly one** task, inside its module's band | task `Part of …` header lines | a **boot failure**, not a lint warning — see **Why check 4** |
| 5 | every `#NN` cross-reference resolves | `issues/CREATED.md` | an epic pointing at an issue that does not exist, or at another repository's |
| 6 | every task file carries `## Scope`, `## Requirements closed`, `## Scenarios closed`, `## Closes`, `## Traps`, `## Acceptance` | the task files | a task that cannot be built, accepted or traced from its own issue |
| 7 | every finding id (`C-`/`T-`/`E-`/`F-`/`S-`/`P-`/`G-`) resolves in its **owning** review | `docs/reviews/R1`…`R7` | a capability-matrix row number cited as a finding — `DECISIONS.md` §7 rule 4a, and it is live today |
| 8 | `IMPLEMENTATION-PLAN.md` §2 and `issues/` agree, both ways | the plan and the file glob | a task in the plan with no file (unbuildable) or a file not in the plan (unscheduled) |
| 9 | every task sits in exactly one phase epic's task region | `issues/0N-EPIC-*.md` | a task nobody's epic tracks — and a `__TASKS__` placeholder `create-issues.sh` would corrupt |
| 10 | every `FR-nnn` is owned by **exactly one** task, both unowned and double-owned | plan §2 `Closes` column + each task's `## Requirements closed` | a requirement that reads as covered and is owned by nobody |
| 11 | no id is used for two different kinds of thing | the id registers + `DECISIONS.md` §6 | the accounting set's worst structural defect, repeated — see **Why check 11** |
| 12 | every `WS-nnn` cited resolves | `docs/BUILD-SPEC-SCREENS.md` §1 | a task whose screen was never specced, and a screen id silently allocated twice |

### Why check 1 — dangling `FR` citations, and the 19 that resolved to the *wrong* requirement

The accounting design set carried **25 dangling `FR-nnn` citations**. That alone would be tolerable.
What was not tolerable is that **19 of the 25 resolved to a *different real* requirement** in the
current FRD — the ids came from a superseded FRD version whose numbering had shifted. A reviewer
following `FR-183` landed on a requirement that existed, read plausibly, and was not the one the
author meant. Every one of those citations looked correct in review and was wrong.

That is why the check is *resolution*, not *shape*. A shape check (`FR-\d{3}`) passes all 25.

Check 1 currently **passes** here: all 446 requirements are defined and every citation in the set
resolves. It is cheap to keep true and catastrophic to discover false.

### Why check 4 — a Flyway band claimed by two modules refuses to boot

Two independent reasons, both evidenced in `DECISIONS.md` `D-2` from `reviews/R1`:

1. **The bands in the original brief were already occupied.** `V900000`–`V909999` holds **135** OEM
   seed migrations and `V910000`–`V919999` holds **434** per-client migrations with versions
   *deliberately reused across five client directories* (`V910001__` exists five times). Building
   into either band is a collision on day one (R1 `C-001`).
2. **A collision does not fail loudly.** `FlywayConfiguration.java:296-320` renumbers legacy history
   rows into those bands and `:322-327` then `DELETE`s duplicate history rows — so the symptom is a
   silently deleted history row and a re-run migration, not an error (R1 `C-002`).

Accounting nearly shipped the same defect: its `accounting-india` band `V602000`–`V602999` is a
carve-out *inside* `accounting-base`'s `V600000`–`V609999`, and a base-module task claiming
`V602xxx` came within one task of colliding. Warehouse's five bands are **disjoint and contiguous**
precisely so that this check is a simple range test:

| Module | Band |
|---|---|
| `warehouse-base` | `V500000`–`V509999` |
| `warehouse` | `V510000`–`V519999` |
| `warehouse-adapter-*` (all adapters, sub-allocated per adapter) | `V520000`–`V529999` |
| `warehouse-3pl` | `V530000`–`V539999` |
| `warehouse-india` | `V540000`–`V549999` |

The check reads the `Part of … · Module … · Migrations … · Screens …` header line of every task
file, expands `V500030–V500032, V500036` and `V501020`–`V501049` into individual versions, and
asserts each is claimed once and sits in a band one of its declared modules owns. **915 versions
across 138 tasks are currently claimed with zero duplicates** — that discipline is what the check is
protecting, not repairing.

Two parsing rules matter and are deliberate:

- **Only the bold runs inside the Migrations field are claims.** `Migrations **—**
  (`whad_oem_orders` … already exist at `V520012`)` claims nothing; reading the parenthetical as a
  claim would invent a duplicate that is not there.
- The field ends at ` · Screens`, so a version mentioned in a screen note is not a claim either.

### Why check 11 — the id-collision guard

The accounting programme's most expensive *structural* defect was three different things sharing one
namespace: `A-01`…`E-03` were tasks while `A-`/`B-`/`C-`/`D-` were round-1 findings, `E-` was
round-2 findings, and `D-01`…`D-08` were architecture decisions. The late rename fixed the titles and
left **231 ambiguous references** in the bodies, because a blanket search-and-replace corrupted the
decisions table twice. `DECISIONS.md` §6 exists to make that impossible here, and check 11 is what
makes §6 true rather than aspirational.

It reports two things:

**(a) A literal id defined by two registers.** The brief names two known hazards and both are
handled:

- **R1 §8's traps are `T-1`…`T-18`; R2's findings are `T-001`…`T-097`.** They are separated by
  zero-padding alone. Check 11 asserts the separation holds — no literal token is defined by both —
  and check 7 resolves each citation against its *own* register, so `T-4` is looked up in R1 §8 and
  `T-004` in R2. It holds today.
- **R2's capability-matrix rows are numbered independently of its findings**, so a matrix row number
  reads exactly like a finding id. Those rows run past 097, so a row copied as `T-244` is caught by
  **check 7** as a citation that resolves to nothing. Five such miscitations are live in the set
  right now — the exact failure `DECISIONS.md` §7 rule 4a says was already caught once by hand.

The collision the check actually finds is a third one nobody had named: **`I-10`…`I-20` are defined
by two registers** — `DATA-MODEL.md`'s enforceable constraints (`I-1`…`I-20`) and `IRREVERSIBLE.md`'s
irreversible rows (`I-01`…`I-63`). `I-01`…`I-09` are distinguishable by their leading zero; from
`I-10` up they are byte-identical, and roughly 250 mentions across the set cannot be told apart by
shape. `DATA-MODEL.md` itself writes `` `L-2`/`IRR I-03` `` in places, which is the disambiguating
convention — but it is a convention, applied inconsistently, not a namespace.

**(b) A register the checker can resolve that `DECISIONS.md` §6 does not declare.** §6 is what the
next author reads before choosing an id; a register missing from it is the next collision. Three are
missing today: screens (`WS-`, 237 ids), the irreversible rows (`I-`, 63 ids — `IRREVERSIBLE.md:19`
believes §6 covers it and §6 does not), and R1 §8's traps (`T-n`, 18 ids).

### Why check 9 — the placeholder that corrupts the epic it is meant to fill

`__TASKS__` is replaced by a **multi-line** checklist at filing time. Six phase epics currently write
it as `## __TASKS__` — as the heading itself — and follow it with a hand-maintained checklist.
Substituting there produces a mangled heading *and* leaves the hand-written list below it as a
duplicate. `create-issues.sh` refuses to file in that state; check 9 reports it first, so CI catches
it before anyone runs the script.

Where an epic carries a bare `__TASKS__` on its own line and no hand-written list (P0 and P1),
membership is filled from the `pN-*.md` glob at creation time and is correct by construction. Where
an epic carries a hand-written checklist, check 9 asserts it matches the glob exactly — every task of
that phase present, once, and no task from another phase.

---

## The exemption model — read this before you "fix" it

Some citations are **deliberately** unresolvable. The canonical case here is a forward reference to
the next free id:

- `SCENARIO-CATALOGUE.md` §5 rule 3: *"New ids continue from `WH-SC-301`; ids are never reused."*
  That id does not exist yet, by definition. It is cited **35 times** across the set.
- `p5-13.md` and `DEFECTS-FOUND.md`: *"the next free is `WS-238`"*, with the task explicitly
  forbidding reuse of another screen's grid.
- `GAP-REGISTER.md` §4 and `DESIGN-SET-DEFECTS.md` carry a **census** of every dangling id the
  checker finds, quoting each one so the register is greppable by the broken id. Between them they
  are 44 of the 151 violations reported below.

Reporting those as violations buries the handful of live miscitations and gets the check switched
off. That is exactly how a checker dies.

So the checker honours **self-declared** exemptions, and prints how many mentions each one swallowed.
**Nothing is exempt by path, ever.** A path allowlist would silence the very document a defect was
copied *from*, and would grant the exemption to every future file in that directory for free.

### Syntax

```
<!-- check-design-set: <rule> file [ID ...] — why -->

<!-- check-design-set: <rule> begin [ID ...] — why -->
...
<!-- check-design-set: <rule> end -->
```

`file` scopes the exemption to the whole document; `begin`/`end` to a region. **Naming ids on the
fence narrows it to exactly those**, so one fence can cover a whole census table while a *new*
dangling id in that same table still fails. Prefer the narrowest form that reads naturally, and
prefer a narrowed fence to a bare one. Put the fences **outside** a table or list — an HTML comment
between two rows splits the table.

| rule | check | what it exempts |
|---|---|---|
| `fr-citations` | 1 | an `FR-nnn` that resolves to nothing |
| `scenario-citations` | 2 | a `WH-SC-nnn` that resolves to nothing |
| `table-names` | 3 | a warehouse table with no `DATA-MODEL.md` row |
| `flyway-band` | 4 | a version deliberately claimed outside its module's band — `p4-10` has one: `V530060` follows the `wh3_` prefix while the task follows `FR-301`'s phase |
| `finding-citations` | 7 | a finding id named as the subject of a discussion rather than cited |
| `id-collision` | 11 | an ambiguous id in a document that says which register it means |
| `screen-citations` | 12 | a `WS-nnn` forward reference to the next free id |

Worked example, for `GAP-REGISTER.md` §4's dangling-id census:

```
<!-- check-design-set: finding-citations begin T-244 T-264 T-325 T-326 T-337 E-754 — the census names each broken citation so §4 is greppable by it -->
| **check-7** (8) | 5 R2 capability-matrix rows cited as findings … |
<!-- check-design-set: finding-citations end -->
```

A *new* dangling id appearing in that same table still fails, because the fence names six ids and
only those six.

### The guard rails that stop a declaration rotting into a blanket

- A `begin` fence that is never closed, an `end` with no `begin`, a nested `begin`, a second `file`
  declaration for one rule, or an unknown rule name is reported under a **`directive`** heading that
  prints before any check and counts toward the failure total. An unterminated fence can never
  silently swallow the rest of a file.
- A declaration that exempts **nothing** is printed as `stale … remove it`, with the reason you gave,
  so a fence left behind after a cleanup gets deleted instead of quietly widening.
- Every run — `--summary` included — prints the count per rule and the file:line of each declaration:

```
check-12 pass    0  WS-nnn citations resolve to BUILD-SPEC-SCREENS.md
        exempt 2 mentions — screen-citations 2 (2 declarations in 2 files)
          docs/DEFECTS-FOUND.md:34: [screen-citations] exempts 1 mention
          issues/p5-13.md:5: [screen-citations] exempts 1 mention
```

- `--show-exempt` lists every exempted mention, `file:line`, with its rule and your stated reason.

Directives are parsed for **every** file before any check runs, not per check, so a malformed fence
is reported once and wherever it sits — including in a document the check it names does not
otherwise scan. When you *fix* a citation, delete the fence with it. When you add one, say why: the
reason is printed back at the next reader.

### Why not the obvious alternatives

- **A path allowlist for `docs/reviews/**` or `GAP-REGISTER.md`.** Rejected. `GAP-REGISTER.md` is
  written *from* the checker's output; a path rule would silence the one document whose job is to be
  audited against it, and would exempt every future file in that directory for free.
- **Strip inline code spans.** Rejected for id citations. In this set the ids are almost always
  inside backticks (`` `FR-001` ``), so the backtick carries no signal and stripping would hand
  anyone a one-character way to mute the check. **Fenced code blocks** are different and *are*
  skipped — a `grep FR-` example is a command, not a citation — and that skip is counted in the
  ledger as rule `code-block`, never silently.
- **Renaming the second `I-` register.** Tempting, and it is the right fix for `I-10`…`I-20`, but it
  is the design set's decision to take, not the checker's. `DECISIONS.md` §7 rule 4 forbids a blanket
  search-and-replace of an id for good reason: it corrupted the accounting decisions table twice.

---

## What it deliberately does not flag

- **A task body citing a version another task owns.** That is normal cross-referencing. It appears
  under a non-failing **advisory** heading only when *no* task header claims the version at all —
  currently 2 such notes, both in prose warning a later author off a number.
- **A version range in a task body** (`V500064`–`V500199`) is a reserved gap being described, not a
  claim on a file, and is not read as one.
- **`PR #92`** is a pull request, not an issue, and is skipped by check 5.
- **A `#NN` inside a code span** (`` `#77` ``) is prose, not a reference, and is skipped by check 5.
- **An id inside a fenced code block** is an example, and is skipped by every citation check.
- **`wh_orders:edit_after_release`** is a permission string, not a table name; a token followed by
  `:` is not read as a table by check 3.
- **`tools/` is not scanned at all.** This file is the checker's documentation, not the design set,
  and the directive examples above must stay examples — a checker must not be able to exempt itself.

## Known residual hazard: check 5 after the backlog is filed

`issues/CREATED.md` does not exist until `issues/create-issues.sh` runs, so check 5 skips cleanly and
prints a count instead:

```
check-5  pass    0  #NN issue cross-references resolve to issues/CREATED.md
        note: issues/CREATED.md does not exist yet — the backlog is unfiled. 231 bare `#NN` mentions
        will become check-5 subjects the moment it does; most are document row numbers, not issues.
```

Read that note as a warning, not a reassurance. Of those 231 mentions, the great majority are
**document row numbers** — CLAUDE.md rule numbers, R2/R3 capability-matrix rows, `IRREVERSIBLE.md`
question numbers — and once 147 issues exist, `#116` will *resolve*, to the wrong thing, exactly like
accounting's 19 mis-resolving `FR` citations. **The checker cannot detect that**, because a
resolving reference is indistinguishable from a correct one.

Two mitigations, in order of preference: write a row number as `row 116` or inside a code span, and
write a cross-repo issue as `owner/repo#791` (the four `#791` mentions in this set are
`classic-issues` issues and will be reported by check 5 as unresolvable, which is correct).

## CI

There is **no CI runner in this repository yet** (no `.github/workflows/`). This should run on every
push and pull request:

```yaml
# .github/workflows/design-set-integrity.yml
name: design-set integrity
on: [push, pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: python3 tools/check-design-set.py
      - run: issues/create-issues.sh --check     # needs GH_TOKEN once the backlog is filed
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

The second step is `DECISIONS.md` §7 rule 5 made enforceable: the `.md` files win, GitHub is a
mirror, and CI fails when the two part company.

Until the runner exists, run both before every `issues/create-issues.sh --sync`.

## Current state — run 2026-09-02 08:25 IST, from the repo root

```
python3 tools/check-design-set.py --summary        # exit 1
```

| check | result | what it is |
|---|---|---|
| 1 FR citations | **pass** | 446 requirements defined, every citation across the set resolves |
| 2 scenario citations | **35** | every one is `WH-SC-301`, `SCENARIO-CATALOGUE.md` §5 rule 3's allocation marker |
| 3 table names | **46** | 40 distinct tables named by 18 task files with no `DATA-MODEL.md` row — the wave-2 India orphans, P5's new tables, and the report/archive tables the tasks invent |
| 4 Flyway | **3** | `p2-29` and `p3-04` claim base-band grid config without naming `warehouse-base` on the header; `p6-08` claims `V524000`–`V524099` for `logistics`, which `D-2` gives no band. **0 duplicate versions of the 915 claimed** |
| 5 issue refs | **pass** | skipped — `issues/CREATED.md` does not exist yet; 231 bare `#NN` are waiting for it |
| 6 required sections | **pass** | all 138 task files carry all six sections |
| 7 finding ids | **39** | 8 originals — 5 R2 capability-matrix rows cited as findings and one fabricated `E-754` in `COMPETITOR-BENCHMARK.md`, 2 unpadded `E-1`/`E-8` in R6 — plus 31 census mentions |
| 8 plan ↔ files | **pass** | 138 = 138, both directions, no duplicate plan rows |
| 9 epic membership | **6** | six phase epics put `__TASKS__` on a `## ` heading line |
| 10 FR ownership | **3** | `FR-224`/`FR-225` are closed by no plan §2 row; `p2-14` claims both |
| 11 id collisions | **14** | `I-10`…`I-20` defined by two registers (11), and 3 registers absent from `DECISIONS.md` §6 |
| 12 screen ids | **5** | 1 original — `p5-13` claims `WS-238` before §1 allocates it — plus 4 census mentions |
| | **151 violations** | |

**Read the composition, not just the total.** Two census documents — `docs/GAP-REGISTER.md` and
`docs/DESIGN-SET-DEFECTS.md` — exist to *quote* the broken ids so the registers are greppable by
them, and they account for **44 of the 151**: 9 of check 2, 31 of check 7, 4 of check 12. Fence those
blocks with `begin`/`end` naming the ids and the total falls to 107 originals without weakening a
single check. That is the whole argument for the exemption model in one number.

Of the 35 check-2 violations, **every one is `WH-SC-301`** — the §5 rule 3 allocation marker,
cited by 25 P5/P6 task files, two phase epics, the catalogue's own rule and the census documents.
One region fence in the catalogue plus a per-file declaration is the whole fix. Of the 39 check-7
violations, only **8 are originals**; of the 5 check-12 violations, only **1** is.

The set is under active authoring. `GAP-REGISTER.md` and `DESIGN-SET-DEFECTS.md` both appeared while
this checker was being written, and `GAP-REGISTER.md` §4 already dispositions the checker's own output
against `X-nnn` defect ids. Re-run before quoting a figure.
