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

- `SCENARIO-CATALOGUE.md` §5 rule 3: *"New ids continue from `WH-SC-306`; ids are never reused."*
  That id does not exist yet, by definition. **31 declarations** name it — 27 region fences plus 4
  file-level — which is the structural number worth quoting; the count of *mentions* moves with every
  paragraph that discusses the marker, so read it with
  `grep -rh 'check-design-set: scenario-citations' --include=*.md . | grep -c WH-SC-306` rather than
  trusting a number on this page. The marker read `WH-SC-301` until
  2026-09-02, when review round 2 took `WH-SC-301`–`WH-SC-305` for §3.21 and every one of those
  mentions had to move with it — that is the price the marker idiom charges per allocation, and it is
  why §5 rule 3, not this page, is the one place to read the next free id.
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
| `issue-citations` | 5 | a `#NN` that is an **ordinal in prose** (*Refusal #2*, *ship-blocker #2*), a **document row number** (R2's feature-table rows), a **markdown in-page anchor** (`[§9](#9--…)`), or a **cross-repo citation elided** after its first mention (`classic#790, #791`) |
| `flyway-band` | 4 | a version deliberately claimed outside its module's band. **No file in the set declares one today** — `p4-10` is the case that reads like it needs one (`V530060` follows the `wh3_` prefix while the task follows `FR-301`'s phase) and it does not, because its header names **both** `warehouse-india` and `warehouse-3pl`. Declaring the second module is always better than fencing |
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

## Known residual hazard: check 5, now that the backlog is filed

`issues/CREATED.md` exists, so **check 5 no longer skips.** It activated against 152 rows and raised
**64** violations on the first run — and every one was a false positive, in three families:

| family | ids | why it is not an issue reference |
|---|---|---|
| ordinals in prose | `#2` `#9` | *Refusal #2* · *Adapter #2 (services)* · *ship-blocker #2* · *logistics needs #1, #2, #3, #5, #6, #10*. `COMPETITOR-BENCHMARK.md:70`/`:146` additionally use `#9` as the markdown anchor `[§9](#9--where-the-audits-disagree)`. In this repository `#2` and `#9` are the two **pull requests**, so no issue row can ever exist for them |
| document row numbers | `#230` `#263` `#275` `#303` `#312` `#314` `#325` `#334` `#375` `#388` | the row numbers of `R2-tier1-wms-audit.md`'s own feature tables — *"the single most important row in this table is #263"* |
| cross-repo, elided | `#790` `#791` | issues in `neetub1508/classic`, cited `classic#790, #791`. The first resolves; the elided continuation reads as a bare `#NN`. **Writing it `neetub1508/classic#791` is the real fix** and remains the preferred mitigation |

All 64 are declared, in the open, by 21 `issue-citations` file-scoped directives — one per offending
document — so the run prints `exempt 64 mentions — issue-citations 64 (21 declarations in 21 files)`
and any *new* dangling `#NN` still fails. **Nothing was fixed into an issue reference and the check
was not weakened.** In the seven `issues/*.md` files the directive sits in the **front matter, above
the `---`**, so it never enters an issue body and cannot drift against the filed issue.

**The hazard the exemptions do not cover, and cannot.** A row number that *resolves* is invisible to
this check — `IRREVERSIBLE.md:679`'s *"logistics needs #1, #2, #3, #5, #6, #10"* has `#2` flagged and
exempted while `#1`, `#3`, `#5`, `#6` and `#10` now silently resolve to the master epic and four
phase epics. That is accounting's 19 mis-resolving `FR` citations in a different costume, and **the
checker cannot detect it**, because a resolving reference is indistinguishable from a correct one.

Two mitigations, in order of preference: write a row number as `row 116` or inside a code span, and
write a cross-repo issue as `owner/repo#791`.

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

## Current state — re-run 2026-09-02, from the repo root

```
python3 tools/check-design-set.py --summary        # exit 0
```

| check | result | exempt | what changed in the remediation pass |
|---|---|---|---|
| 1 FR citations | **pass** | — | unchanged: 446 requirements defined, every citation across the set resolves |
| 2 scenario citations | **pass** | 45 | 26 → 0. Every subject was `WH-SC-301`, the §5 rule 3 allocation marker. **29 region fences**, each naming that one id, in the catalogue, the two phase epics and the 23 P5/P6 tasks that reserve from it |
| 3 table names | **pass** | 22 | 46 → 0. **4 typos fixed** in task files, **11 genuinely missing tables added** to `DATA-MODEL.md` §2 *and* §7, **20 report grid identifiers documented as non-tables** in §8.3, **22 prior-art and counter-example quotations fenced** by id across 9 task files |
| 4 Flyway | **pass** | — | 3 → 0. `p2-29`/`p3-04` now name `warehouse-base` on the header; `p6-08` withdraws its claim on `V524000`–`V524099`, because `D-2` allocates `logistics` no band. **0 duplicate versions of the 818 now claimed** |
| 5 issue refs | **pass** | 64 | **activated** — `issues/CREATED.md` now carries all 152 rows. 64 → 0, every one a false positive: ordinals in prose, R2 table row numbers, and the elided half of a `classic#790, #791` cross-repo citation. **21 file-scoped `issue-citations` directives**, one per offending document. Read the hazard note above, not this row |
| 6 required sections | **pass** | — | all 138 task files carry all six sections |
| 7 finding ids | **pass** | 52 | 8 → 0. Five R2 **capability-matrix rows** rewritten as `R2 §1.n row N`; `E-1`/`E-8` in R6 rewritten as `§L items 1–8`; `E-754` fenced — it is the tail of *IEEE-754* at `R1:441`, quoted to explain a counting command, not a fabrication |
| 8 plan ↔ files | **pass** | — | 138 = 138, both directions, no duplicate plan rows |
| 9 epic membership | **pass** | — | 6 → 0. All six epics now carry a real `## Tasks` heading with `__TASKS__` alone beneath it, and the 101 hand-maintained checklist rows are deleted. `create-issues.sh` no longer refuses |
| 10 FR ownership | **pass** | — | 3 → 0. `P2-14`'s §2 row carried two **escaped pipes**, splitting it into 9 cells and moving `Closes` out of column 6. Rewritten without them; `FR-224`/`FR-225` now resolve |
| 11 id collisions | **pass** | — | 14 → 0. `IRREVERSIBLE.md`'s rows renamed **`I-01`…`I-63` → `IRR-01`…`IRR-63`**, file by file; `IRR-`, `WS-` and the R1 §8 `T-n` trap register declared in `DECISIONS.md` §6 |
| 12 screen ids | **pass** | 13 | 1 → 0. `WS-238` is the next-free-screen marker; fenced by id in each of the five places that name it |
| | **0 violations** | **132** | |

**Read the exemption total sceptically, not the violation total.** Of the 132 suppressed mentions,
**118 are covered by 46 self-declared fences** and the other **14 are inside fenced code blocks**,
which every citation check skips by construction. Every count is printed on every run. No fence is a
path allowlist and none is bare: each names the exact ids it covers, so a *new* dangling id in the
same paragraph still fails. Run `--show-exempt` to see all 132 with the reason recorded on its fence. The checker reports a
declaration that suppresses nothing as **stale**; there are none.

**What the remediation was not allowed to do, and did not.** Exactly one line of
`check-design-set.py` changed: the `IRREVERSIBLE.md` definition anchor and its §6 probe followed that
register's rename from `I-` to `IRR-`. No check was relaxed, deleted or made advisory. The proof is
the intermediate state that was deliberately measured — with the ids renamed and the anchor updated
but **before** `DECISIONS.md` §6 was amended, check 11 still reported *"§6 declares no namespace for
the irreversible rows register (`IRR-…`, 63 ids, authority docs/IRREVERSIBLE.md)"*. The register is
still resolved, still counted at 63, and still required to be declared.

**Residual, stated plainly: zero failing violations, three non-failing advisories.** `p5-01:70`
(`V531100`), `p5-09:48` (`V510126`) and `p6-08:131` (`V524000`) are versions cited in a task body that
no task header claims. The first two are cross-references to blocks another task owns; the third is
the reserved logistics block that this design set deliberately no longer claims. All three are
correct as advisories and none should be silenced.

*For the record, because the number moved twice: this file previously carried **151**, measured before
the two census documents declared their own fences. With those fences in place the set measured
**107** at the start of the remediation pass, and **0** at the end. `docs/DESIGN-SET-DEFECTS.md`
records every FIX, FENCE and REPORT behind that.*

The set is under active authoring. `GAP-REGISTER.md` §4 dispositions the checker's own output against
`X-nnn` defect ids, and `DESIGN-SET-DEFECTS.md` carries the remediation record. **Re-run before
quoting a figure.**
