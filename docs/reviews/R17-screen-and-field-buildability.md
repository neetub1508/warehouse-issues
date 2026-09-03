# R17 — screen and field-level buildability

<!-- check-design-set: issue-citations file #2 — `#2` and `#9` are ordinals in prose, not issue references — *Refusal #2*, *Adapter #2 (services)*, *ship-blocker #2*, *logistics needs #1, #2, #3, #5, #6, #10* — and at COMPETITOR-BENCHMARK.md:70/:146 `#9` is the markdown in-page anchor `[§9](#9--where-the-audits-disagree)`. In this repository `#2` and `#9` are in fact the two **pull requests** opened while the backlog was being filed, so no issue row can ever exist for either: see issues/CREATED.md -->

**Date:** 2026-09-02 · **Finding prefix:** `RB-` · **Branch:** `docs/round-3-functional-completeness`
· **Round:** 3, lens 17

**The question this lens asks.** Not *"can a builder start this task?"* (that is `R8`/`R9`, `Q-`/`H-`)
but **"can a builder render this screen and save a valid record without inventing anything?"** Every
finding below is a decision a builder must take that the design set did not authorise them to take.

**File set actually read — 30 files:**

```bash
cd /Users/bbhushan/work/git/workspace/warehouse-issues
# docs/  DECISIONS.md · BUILD-SPEC-SCREENS.md (§0,§1,§2.1–2.6,§3.1–3.2,§6,§7,§8,§10,§11 in full;
#        §3.3–3.5,§4,§5,§9 by grep) · DATA-MODEL.md · WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md
#        GAP-REGISTER.md · GAP-REGISTER-R2.md · DESIGN-SET-DEFECTS.md · contracts/README.md
#        SCENARIO-CATALOGUE.md · reviews/R1-codebase-reality.md · reviews/R11-…(house form)
# issues/ p0-16 p1-01 p1-02 p1-07 p1-12 p1-13 p2-02 p2-05 p2-08 p2-10 p2-11 p2-15 p2-20 p2-21
#         p2-26 p2-29 p3-16 p3-17 p3-20 p3-21 p4-05
# classic/ platform/frontend/src/utils/filterUtils.ts
#          platform/frontend/src/components/common/DynamicDataTable.tsx
#          platform/backend/src/main/java/ai/platform/controller/DepartmentController.java
#          platform/backend/src/test/java/ai/platform/service/ExportServiceContractTest.java
#          mobile/src/components/common/ListHeader.tsx
#          mobile/src/components/common/EntityListScreen.tsx
#          mobile/src/screens/accessoryStockReceipt/AccessoryStockReceiptListScreen.tsx
```

---

## §1 · Verdict

**`BUILD-SPEC-SCREENS.md` is the strongest screen specification I have read in either the accounting
or the warehouse set, and its remaining defects are of one shape: the document specifies the *grid*
extremely well and the *form* barely at all.** For a sampled screen it will tell you the
`gridIdentifier`, the filter scope, every column with its source `table.column`, the export superset,
the row actions with their gates and the mobile verdict — and then say `*Identity* (`owner`, `sku`,
`code`, `name`, `description`)` and stop. Which of those five is mandatory, what the maximum length
is, what happens when a duplicate `sku` is submitted, what the user sees while the grid loads and
what they see when it returns zero rows are, for all 237 screens, unwritten.

Rounds 1 and 2 already own the biggest slice of that (`H-002` no column-level DDL, `Q-002` no `status`
domain, `Q-004` no per-column `sortable`/`default-visible`, `Z-004` no per-field freeze list) and this
review does not re-file any of it. What is left after those are removed is nine findings, and **two of
them are of a kind round 2 could not have found, because they require reading the live tree rather
than the design set**:

- **`RB-001` is a false premise, not a gap.** `C-044` — a round-1 finding, cited in **22 files** — says
  mobile date filters "still are not" supported. They are. `ListHeader.tsx:123-170` exposes **two**
  date ranges, `EntityListScreen.tsx:157-195,428-441` forwards both, and **56 live mobile screens use
  them**. On that false premise the set replaced the date filters of every warehouse mobile grid with
  six invented `<x>Within` dropdown keys that have no option list, no `filter_definitions` row and no
  backend parameter anywhere in the set, and wrote the constraint into `FR-220` — a requirement.
- **`RB-005`.** Six task files cite `ExportServiceContractTest.WITHOUT_AUDIT_COLUMNS` as the gate that
  keeps their export honest. That test's scanner reads **`ai.platform` only**
  (`ExportServiceContractTest.java:137`), so it will discover zero warehouse export services; and the
  43 warehouse exports §0.5 deliberately ships *without* audit columns cannot be registered in it
  anyway, because the list is a `Set.of(...)` the test's own contract says may **shrink, never grow**.

The rest are single-screen errors of the kind that cost one rebuild cycle each — `RB-002`'s two
filters over columns that exist on no table, `RB-003`'s two grids with two scope names, `RB-004`'s
four-value column behind a five-value dropdown.

**Nothing here changes the shape of the product.** All nine are corrections inside documents that
already exist, and eight of the nine are edits to `BUILD-SPEC-SCREENS.md` or to one task file.

---

## §1.1 · How I sampled

237 screens is too many to read at field level, and reading them uniformly would have found the same
thing 237 times. I sampled **52 blocks (22%)**, chosen so that each of the five failure modes my lens
hunts had somewhere to hide:

| Band | Why this band | Screens |
|---|---|---|
| **Create/edit modals over v1 masters** | the only screens in the set that take field input from a keyboard; if mandatory-ness and validation are missing anywhere they are missing here | WS-015 · WS-016 · **WS-017** · WS-018 · WS-019 · WS-020 · WS-021 · **WS-023** · WS-026 · WS-030 · WS-031 · WS-036 · WS-038 · WS-039 |
| **Workflow transition screens** | §0.6 makes each transition its own modal, so each is a form nobody has specified; and `FR-005` forbids an edit path, which means the transition modal is the *only* write surface | WS-045 · WS-046 · WS-072 · WS-075 · WS-076 · WS-080 · WS-082 · WS-089 · **WS-090** · WS-092 · WS-094 · WS-095 · WS-097 · WS-098 · WS-099 |
| **Enquiry and report grids** | parameters, not filters; `gridIdentifier`s that are not tables; the place export↔grid parity breaks | WS-040 · WS-042 · WS-071 · **WS-208** · WS-209 · WS-211 · **WS-212** · **WS-220** · **WS-221** · WS-224 |
| **Mobile** | `D-13` makes silence a defect, and the module has real constraints that a spec can get wrong in both directions | the `Mobile` row of every screen above, plus **WS-229 … WS-237** (the nine RF screens) |
| **Adapters** | the thinnest blocks in the document, and the ones furthest from the canonical references | WS-194 · WS-199 · WS-203 · WS-206 |

Bolded screens are the ones a finding landed on. I read `BUILD-SPEC-SCREENS.md` §0, §1, §2.1–§2.6,
§3.1–§3.2, §6, §7, §8, §10 and §11 in full and the rest by grep; every field-name claim below was
checked against `DATA-MODEL.md`'s own row for the table, which `DECISIONS.md` makes the authority on
any column name.

---

## §2 · The findings

### `RB-001` · Mobile date filters **are** supported; `C-044` says they are not, and six invented filter keys were designed around the false premise — **BLOCKER**

**What I found.** `C-044` (round 1, `R1` §7) records that CLAUDE.md's *"`additionalFilters` only
supports dropdowns"* is stale, which is correct, and then adds a second clause that is not: *"**date
filters still are not** [supported] … Date-range filtering on mobile still needs `EntityListScreen`
work."* That second clause is false against the tree it cites.

`ListHeader.tsx` exposes a **first** date range at `:123-145` (`showDateRangeFilter`, `fromDate`,
`toDate`, `onFromDateChange`, `onToDateChange`, `fromDateLabel`, `toDateLabel`) and a **second**,
additive one at `:146-170` (`showSecondDateRangeFilter`, `secondFromDate`, `secondToDate`, …).
`EntityListScreen` declares all of them at `:157-195` and forwards every one to `ListHeader` at
`:428-441`. It is not a latent capability: a shipped screen wires it end to end —
`AccessoryStockReceiptListScreen.tsx:62-63` holds the two dates in state, `:143-150` converts them to
`startDate` / `endDate` API parameters through `dateToStartOfDayUTC` / `dateToEndOfDayUTC`, and
`:288-294` passes them to `EntityListScreen`.

On the strength of the false clause, the set replaced every date-driven mobile filter strip with a
**bounded dropdown of named periods**. `p0-16.md:55-60` states the policy:

> *"Note the correction to CLAUDE.md found by R1 `CM-1` … **date filters are still unsupported**
> (`C-044`). Every warehouse mobile grid therefore replaces a date range with a bounded **dropdown**
> (`expiringWithinDays`, `occurredWithin`, `receivedWithin`, `inTransitOverDays`), resolved to a range
> on the backend. That divergence is deliberate…"*

The divergence is not deliberate; it is a workaround for a constraint that does not exist. And it is
not free — it invents six filter keys that exist nowhere else in the product:

| Invented key | Replaces | Where | Option list stated? | `filter_definitions` row? | Backend param? |
|---|---|---|---|---|---|
| `expectedWithin` | `expectedFrom`/`To` on WS-072 | `BUILD-SPEC:1524`, `p1-12` | **no** | no | no |
| `receivedWithin` | `receivedFrom`/`To` on WS-076 | `BUILD-SPEC:1558`, `p1-13` | **no** | no | no |
| `promisedWithin` | the two ranges on WS-099 | `BUILD-SPEC:1705`, `p2-08` | **no** | no | no |
| `dispatchedWithin` | `dispatchedFrom`/`To` | `p2-10:65,113` | **no** | no | no |
| `occurredWithin` | `occurredFrom`/`To` on WS-040 | `BUILD-SPEC:1300` | yes — Today / 7 / 30 | no | no |
| `expiringWithin` | `expiryFrom`/`To` on WS-042 | `BUILD-SPEC:1370` | via `expiringWithinDays` at `:1170` (30/60/90) | no | no |

§0.5 of the same document is unambiguous that a filter which is not in **all three** registries
"renders, accepts input and does nothing". These six are in none of them.

**Evidence.**
- `/Users/bbhushan/work/git/workspace/classic/mobile/src/components/common/ListHeader.tsx:123-170`
- `/Users/bbhushan/work/git/workspace/classic/mobile/src/components/common/EntityListScreen.tsx:157-195`, `:428-441`
- `/Users/bbhushan/work/git/workspace/classic/mobile/src/screens/accessoryStockReceipt/AccessoryStockReceiptListScreen.tsx:62-63,143-150,288-294`
- `docs/reviews/R1-codebase-reality.md:543` (`C-044`), `docs/reviews/R1-codebase-reality.md:89` (`CM-1`)
- `docs/WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md:405` — **`FR-220` carries the false clause as a requirement**
- `issues/p0-16.md:55-60` · `docs/BUILD-SPEC-SCREENS.md:170-172` (§0.7) · `:1300` · `:1370` · `:1524` · `:1558` · `:1705`
- `docs/IRREVERSIBLE.md:723` · `docs/DATA-MODEL.md:4172` · `docs/INDIA-LOCALISATION-PACK.md:446` · `docs/PLATFORM-DEPENDENCIES.md:369`

```bash
# 56 shipped mobile screens already render the date range C-044 says is unavailable
cd /Users/bbhushan/work/git/workspace/classic
grep -rl "showDateRangeFilter" mobile/src/screens/ | wc -l          # → 56

cd /Users/bbhushan/work/git/workspace/warehouse-issues
grep -rl '`C-044`' docs/ issues/ | wc -l                            # → 22 files cite it
grep -rlEi 'date filters (still )?(are )?(not|un)' docs/ issues/ | wc -l   # → 6 restate the false clause
```

*(The backtick in the first grep is load-bearing: `grep -rl 'C-044'` returns 31 files because
`WH-SC-044` contains the string — the trap `DECISIONS.md` §7 rule 8 warns about.)*

**Why it matters.** A stock controller filtering the movement register on a handheld gets *Today / 7
days / 30 days* and cannot ask for last month. More expensively, six filter keys that no registry
carries will be built by six different developers in six phases, each inventing an option list and a
backend parameter name, and each one is a `COMMON_FILTER_CONFIGS` allowlist miss away from a filter
strip that renders and does nothing.

**Cost if found late.** `FR-220` is a requirement and `IRREVERSIBLE.md:723` reads it as settled, so
this is corrected in **six documents plus eight task files** today and in a shipped mobile app plus a
re-versioned filter contract later. `p1-12`, `p1-13`, `p2-08` and `p2-10` each carry an invented key in
an **acceptance criterion**, so each will be signed off as met.

**Recommendation.** Amend `C-044` in `R1` to *"text **and date-range** filters are supported;
`ListHeader.tsx:123-170` exposes two ranges and `EntityListScreen.tsx:428-441` forwards them"* and
propagate to `FR-220`, §0.7, `IRREVERSIBLE.md:723`, `DATA-MODEL.md:4172`, `INDIA-LOCALISATION-PACK.md:446`
and `PLATFORM-DEPENDENCIES.md:369`. Then delete the four option-less `<x>Within` keys and restore the
web `…From`/`…To` pair on the mobile block. Keep `expiringWithinDays` and `inTransitOverDays` — they
are *bucket* filters that are better than a date range on both surfaces, and they are the two that
already have a stated option list or a stated reason.

---

### `RB-002` · WS-017's filter strip and export name eight fields that `whb_locations` does not have, two of them on no table in the product — **BLOCKER**

**What I found.** WS-017 Locations is v1 · P1 over `whb_locations`, whose column list is fixed by
`DATA-MODEL.md:451`. The screen block names eight fields that row does not carry:

| Screen block says | `DATA-MODEL.md:451` says | Verdict |
|---|---|---|
| filter `isPickable` boolean (`:873`) | — | **no such column on any location table.** `is_pickable` is a column of **`whb_stock_statuses`** (`DATA-MODEL.md:414`) |
| filter `isReceivable` boolean (`:873`) | — | **no such column.** `is_receivable` is a column of **`whb_items`** (`DATA-MODEL.md:527`) |
| export `max_lpn_count` (`:876`) | `max_lpns` | renamed |
| export `max_unit_count` (`:876`) | `max_units` | renamed |
| export `max_height_cm` (`:875`) | `height_cm` | renamed |
| export `allow_mixed_item` / `_lot` / `_owner` (`:876`) | `allows_mixed_item` / `_lot` / `_owner` | renamed (verb agreement) |
| export + modal *Scanning* tab `check_digit` (`:877`, `:879`) | — | **absent from the column list entirely** |
| column key `commingePolicy` (`:862`, and again in the filter list `:872`) | `commingle_policy` | **misspelt key**, both occurrences; the correct spelling appears nowhere |

**Evidence.** `docs/BUILD-SPEC-SCREENS.md:862`, `:867`, `:872-877`, `:879` against
`docs/DATA-MODEL.md:451`; `is_pickable` at `docs/DATA-MODEL.md:414`; `is_receivable` at
`docs/DATA-MODEL.md:527`. `DECISIONS.md` §1 makes `DATA-MODEL.md` the authority on any column name.

```bash
cd /Users/bbhushan/work/git/workspace/warehouse-issues
grep -c 'commingePolicy' docs/BUILD-SPEC-SCREENS.md   # → 2  (the typo)
grep -c 'comminglePolicy' docs/BUILD-SPEC-SCREENS.md  # → 0  (the correct key, nowhere)
grep -c 'check_digit' docs/DATA-MODEL.md              # → 0
```

**Why it matters.** Two of these are not typos. `isPickable` and `isReceivable` are **filters over
columns that exist on no location table**, and a builder who takes the screen block at its word will
add two booleans to `whb_locations` — a table `DATA-MODEL.md:2893` marks ★ *must precede `V500030`*,
which is `PNR-1`, the point of no return. The rename family is cheaper but not free: `grid_column_definitions`
keys must match the frontend keys exactly, so `commingePolicy` shipped in a migration is a column that
renders blank forever and is fixed only by a second migration.

**Cost if found late.** `check_digit`, `isPickable` and `isReceivable` are each a column added to the
hottest master in the base module after `V500030` has sealed the ledger, or a modal field silently
dropped on submit. The rename family is one migration each.

**Recommendation.** One editing pass over WS-017 against `DATA-MODEL.md:451`: fix the six renames,
fix `commingePolicy` in both places, and take an explicit decision on the three fields that have no
column — `check_digit` (a real GS1 location-label need, so probably *add the column in `V500013`*),
`isPickable` and `isReceivable` (probably *delete the filters* — pickability at a location is
`status`, and receivability is an item fact). Whichever way each goes, it is `P1-05`'s to write down.

---

### `RB-003` · Two v1 report grids carry two different `COMMON_FILTER_CONFIGS` scope names, and the losing one is a filter strip that renders and does nothing — **MAJOR**

**What I found.** The screen spec and the owning task file name a different filter scope for the same
grid, twice, both in v1 · P2:

| Screen | `BUILD-SPEC-SCREENS.md` §7 | Owning task | Same grid? |
|---|---|---|---|
| WS-221 Expiry & Shelf-life Register | `WAREHOUSE_RPT_EXPIRY` (`:1995`) | `WAREHOUSE_EXPIRY_REGISTER` (`p2-05.md:49`, repeated in its Traps at `:95`) | yes — same route `/warehouse/reports/expiry` |
| WS-220 In-transit Ageing | `WAREHOUSE_RPT_IN_TRANSIT_AGEING` (`:1994`) | `WAREHOUSE_IN_TRANSIT_AGEING` (`p2-02.md:46`) | yes — same route `/warehouse/reports/in-transit-ageing` |

The same two blocks also disagree on WS-221's **filter set**: §7 gives it `expiringWithinDays` select ·
`expiredOnly` boolean · `expiryFrom`/`To` (`dateOnly`); `p2-05.md:47-51` gives it a *"bucket filter …
a dropdown of named buckets"* and a `bucket` column, neither of which appears in §7's row.

**Evidence.**

```bash
cd /Users/bbhushan/work/git/workspace/warehouse-issues
grep -ohE '\bWAREHOUSE(_3PL|_INDIA|_DEALER|_SERVICES|_FIELD_SERVICE|_ASSETS)?_[A-Z0-9_]+' issues/*.md \
  | sort -u > /tmp/task.txt
grep -ohE '\bWAREHOUSE(_3PL|_INDIA|_DEALER|_SERVICES|_FIELD_SERVICE|_ASSETS)?_[A-Z0-9_]+' \
  docs/BUILD-SPEC-SCREENS.md | sort -u > /tmp/spec.txt
comm -23 /tmp/task.txt /tmp/spec.txt
# WAREHOUSE_3PL                      <- prose (module name)
# WAREHOUSE_ALLOW_NEGATIVE_STOCK     <- a global-setting key, not a scope
# WAREHOUSE_ASSETS_ASSET_ITEM_LINK   <- spec abbreviates it as `_ASSET_ITEM_LINK` at :1928 — agrees
# WAREHOUSE_BASE                     <- prose (module name)
# WAREHOUSE_CORE_ISSUES              <- a filename in p6-08
# WAREHOUSE_EXPIRY_REGISTER          <- REAL CONFLICT (WS-221)
# WAREHOUSE_FIELD_SERVICE_JOB_CONSUMPTION      <- spec abbreviates as "etc." at :1926 — agrees
# WAREHOUSE_FIELD_SERVICE_VAN_REPLENISHMENT    <- same
# WAREHOUSE_IN_TRANSIT_AGEING        <- REAL CONFLICT (WS-220)
# WAREHOUSE_STOCK_PERIOD_OVERRIDE    <- WS-046 has no scope in the spec; the task supplies one — agrees
```

**Why it matters.** `filterUtils.ts` is a single object literal; the scope key is looked up by string
at the call site. Whichever name the page passes to `convertFiltersForApi()` is the one that must exist,
and the *other* name is dead weight. Because `P2-29` owns the shared-registry edits and `P2-02`/`P2-05`
own the pages, the two halves are written by different tasks — which is precisely how CLAUDE.md
CRITICAL #17's failure ("the filter UI will appear to do nothing") happens: the registry gets one name,
the page uses the other, and every filter on the expiry register is dropped before the request is built.

**Cost if found late.** It presents as *"the expiry report ignores its filters"* — a full-stack bug
hunt across a page, an API service, a migration and a platform registry, for a one-word disagreement.

**Recommendation.** `BUILD-SPEC-SCREENS.md` §7 wins (the `WAREHOUSE_RPT_*` form is what
`DATA-MODEL.md:3542-3561` registers for all twenty report grids and it is the only self-consistent
family). Correct `p2-05.md:49,95` and `p2-02.md:46`, and reconcile WS-221's filter set between §7 and
`p2-05.md:47-51` in the same edit.

---

### `RB-004` · `whb_items.lifecycle_status` has four values in the column authority and five everywhere else — **MAJOR**

**What I found.** `DATA-MODEL.md:527` — which `DECISIONS.md` §1 makes the authority on any column —
gives `lifecycle_status` as `(NEW/ACTIVE/PHASE_OUT/OBSOLETE)`. Every other document gives five:

| Where | Vocabulary |
|---|---|
| `docs/DATA-MODEL.md:527` | `NEW` `ACTIVE` `PHASE_OUT` `OBSOLETE` — **four** |
| `docs/WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md:185` (`FR-050`) | + `BLOCKED` — five |
| `docs/BUILD-SPEC-SCREENS.md:1020` (WS-023 column) | + `BLOCKED` — five |
| `issues/p1-01.md:40` (the owning task) | + `BLOCKED` — five |
| `docs/reviews/R2:1017`, `R3:533` (the sources the value came from) | + `BLOCKED` — five |

```bash
cd /Users/bbhushan/work/git/workspace/warehouse-issues
grep -rn 'PHASE_OUT' docs/ issues/ | wc -l    # → 7 statements
grep -rln 'PHASE_OUT' docs/ issues/           # → the six files above; only DATA-MODEL omits BLOCKED
```

**Why it matters.** `P1-01` writes the DDL for `whb_items`, and `DECISIONS.md` tells its author to read
`DATA-MODEL.md` for the column. A four-value `CHECK` behind a five-value dropdown is not a cosmetic
mismatch: `BLOCKED` is the value `FR-050` exists to provide (an item that is neither obsolete nor
usable), the filter offers it, the badge-variant map needs a variant for it, and saving it raises a raw
PostgreSQL `23514` from inside a `@Transactional` boundary that no field-level error can reach. This is
`X-055`'s shape (`CONDITIONAL` vs `PARTIAL`) on a different column, and `X-055` was filed precisely
because *"it is the column's stored value"*.

It is also **not** `Q-002`: `Q-002` is about the 30 tables whose `status` domain is *undeclared*.
`lifecycle_status` is declared twice, differently.

**Cost if found late.** Free today (one cell in `DATA-MODEL.md:527`). After `V500015` it is a
`CHECK`-constraint drop-and-rebuild against a live item master, and `DECISIONS.md`'s own rule stands:
a trigger or constraint firing in production is an incident, not a validation.

**Recommendation.** Add `BLOCKED` to `DATA-MODEL.md:527`. Five sources against one is not a decision
that needs taking; it needs transcribing. While there, check the same column's siblings on that row —
`lot_control_mode`, `serial_control_mode` and `expiry_policy` all agree with WS-023, so this is the
only one.

---

### `RB-005` · The export-parity ratchet six task files cite scans `ai.platform` only, and the 43 warehouse exports §0.5 ships without audit columns cannot be registered in it — **MAJOR**

**What I found.** Six task files name `ExportServiceContractTest.WITHOUT_AUDIT_COLUMNS` as the gate
that keeps their export↔grid parity honest — `p2-11.md:92`, `p2-15.md:90`, `p2-21.md:95`,
`p2-29.md:49`, `p3-17.md:80`, `p3-21.md:70`. Two facts about that test break both halves of the claim:

1. **It cannot see warehouse.** Its class-path scan is
   `scanner.findCandidateComponents("ai.platform")` — a single hardcoded package
   (`ExportServiceContractTest.java:137`). Warehouse export services live in `ai.warehousebase`,
   `ai.warehouse`, `ai.warehouse3pl`, `ai.warehouseindia` and the four adapter packages. **The gate is
   inert for every warehouse module**, so the six tasks that cite it as their proof have no proof.
2. **If it could see them, it would fail them.** `:276-280` asserts that any service exporting neither
   `createdByName` nor `updatedByName` **must already be listed** in `WITHOUT_AUDIT_COLUMNS`, which is
   an immutable `Set.of(...)` at `:80` whose javadoc at `:76-78` reads *"FROZEN BASELINE: it may
   shrink, never grow."* §0.5 of the screen spec deliberately ships **23 ledger-style tables** plus
   **every report grid in §7 (20)** with no audit columns — 43 export services with no legitimate home
   in that list.

A third, smaller inconsistency sits inside §0.5 itself: it says the no-audit grids are *"named once,
here"* and gives 23 tables, but **WS-039 Genealogy Explorer declares itself ledger-style outside the
list** — *"Ledger-style: no created-by/updated-by column, and none in the export"*
(`BUILD-SPEC-SCREENS.md:1220`) — over `whb_transformations`, which the §0.5 list does not contain.

**Evidence.**

```bash
cd /Users/bbhushan/work/git/workspace/classic
sed -n '76,80p;137p;276,280p' platform/backend/src/test/java/ai/platform/service/ExportServiceContractTest.java
#  76-78  "FROZEN BASELINE: it may shrink, never grow."
#  80     private static final Set<String> WITHOUT_AUDIT_COLUMNS = new TreeSet<>(Set.of(
#  137    for (BeanDefinition definition : scanner.findCandidateComponents("ai.platform")) {

cd /Users/bbhushan/work/git/workspace/warehouse-issues
awk '/^`whb_stock_movements` · `whb_stock_movement_lines`/,/plus every report grid in §7/' \
  docs/BUILD-SPEC-SCREENS.md | grep -oE '`[a-z0-9_]+`' | sort -u | wc -l    # → 23 tables
grep -c 'whb_transformations' <(awk '/^`whb_stock_movements`/,/plus every report grid/' \
  docs/BUILD-SPEC-SCREENS.md)                                              # → 0  (WS-039 is outside the list)
grep -rn 'WITHOUT_AUDIT_COLUMNS' issues/ | wc -l                           # → 6 task files rely on it
```

**Why it matters.** This is the one gate in the whole design set that would have caught the
export-parity regression class CLAUDE.md calls out by name, and it will silently pass on day one
because it never looks at warehouse code. The second half is worse: the obvious remediation — widen the
scan — turns 43 correct exports into 43 red tests with no sanctioned way to green them, because the
list's contract forbids adding to it. That would be discovered by the first engineer who tries to do
the right thing, in P2, under deadline.

**Cost if found late.** Either 43 warehouse exports quietly grow `createdByName`/`updatedByName`
columns on ledger grids that show neither — which is the *opposite* regression, and the one CLAUDE.md's
Table Rules explicitly warn produces "a column no reader can select" — or the ratchet is deleted, and
with it the only mechanical export gate the monorepo has.

**Recommendation.** Two lines in `MODULE-INTEGRATION.md` (§12, the shared-registry ledger, which
already owns the two platform files warehouse must edit) plus a Trap in `P2-29`:
(a) the scan at `:137` must take a package list, and warehouse's packages must be added to it — this
is a **third** shared-platform file warehouse touches, and `D-10`'s corollary at §11 already concedes
the ratchet can never be *"zero commits to platform"*;
(b) the frozen-baseline contract needs a stated exception shape for a module whose ledger grids are
audit-columnless **by design** — most cheaply an annotation or a `boolean isLedgerStyle()` hook on
`BaseExportService` that the test reads instead of a name list, so the list keeps shrinking and
warehouse never enters it. Add `whb_transformations` to §0.5's list in the same edit.

---

### `RB-006` · No grid in the set states an empty state, a loading state or a statistics tile set — **MAJOR**

**What I found.** Three per-grid render decisions that the migration and the API response both need are
stated for almost no screen:

| Decision | Where it must land | Stated for |
|---|---|---|
| **Empty state** — the text shown at zero rows | `DynamicDataTable`'s `emptyMessage` prop + an i18n key | **1 screen in 39,628 lines**, and it is the v3 widget set |
| **Loading state** | the page's `isLoading` branch | 0 screens |
| **Statistics tiles** — which tiles, and what each counts | the backend `statistics` map + i18n | **6 of 214 configured grids** |

```bash
cd /Users/bbhushan/work/git/workspace/warehouse-issues
grep -ric 'empty state' docs/ | grep -v ':0'
# docs/BUILD-SPEC-SCREENS.md:1     <- §8.2, the v3 widget set: "Empty state names the provider reason"
grep -in 'statistics strip' docs/BUILD-SPEC-SCREENS.md | grep -vE ':(78|1471|1971):' | wc -l   # → 6 screens
awk '/^## 1\. Screen index/,/^## 2\./' docs/BUILD-SPEC-SCREENS.md \
  | awk -F'|' '/^\| WS-[0-9]{3} \|/ && $7 ~ /Y/' | wc -l                                        # → 214 grids
```

`DynamicDataTable.tsx:113,149,605` defaults `emptyMessage` to the **hardcoded English string
`'No data found'`** — so a grid built without the decision ships an untranslated string, and every
locale JSON the module writes is silently incomplete.

**Why it matters.** For most master grids "No data found" is adequate and this is documentation debt.
For the **workflow-gating grids it is not**, and the set already knows why: `FR-114` rules that a
request naming an owner the caller has no grant for is rejected **`403`, never returned empty**,
*"because an empty grid is indistinguishable from 'no stock'"*. That reasoning applies unchanged to
WS-082 Putaway Tasks, WS-092 Holds, WS-097 Blocked Movements, WS-098 Reconciliation Exceptions,
WS-052 the handover queue and WS-053 Inbound Messages — on each of those, *"nothing to do"* and
*"your branch/owner scope returned nothing"* and *"the job that fills this queue has not run"* are three
different operational facts behind one blank rectangle. `WS-223 Install Health Signals` exists to detect
exactly the third one, which is proof the set cares about the distinction and did not carry it onto the
grids.

**Cost if found late.** Cheap per screen and expensive in aggregate: 214 empty-state strings and their
i18n keys, invented one at a time by whoever builds each grid, and `Q-005` already records that P2's
non-grid i18n has no owner and no key-diff gate — so they will not be caught by review either.

**Recommendation.** One paragraph in §0 of `BUILD-SPEC-SCREENS.md`, in the shape §0.7 uses for the
mobile verdict: **every block states an `emptyMessage` i18n key**, and for the six workflow-gating
grids above it states the *three* distinguishable messages (`empty` / `out of scope` / `never
populated`). `never` — i.e. the platform default — is a legitimate answer for a master grid and does
not have to be written, exactly as §0.12 handles `Frozen when`. Statistics tiles: state them per screen
or state `none`; §0.3 already asserts a cache rule for *"every warehouse statistics strip"*, which
reads as though every grid has one.

---

### `RB-007` · No screen names a uniqueness-validation endpoint, and `/validate/code` appears zero times in the design set — **MAJOR**

**What I found.** CLAUDE.md's Controller Rules list `/validate/code` and `/validate/name` among the
**required endpoints** for every entity, and its Validation rules require *"debounced uniqueness API
calls"* on the frontend. The Department canonical reference implements both —
`DepartmentController.java:301` (`@GetMapping("/validate/code")`) and `:318`
(`@GetMapping("/validate/name")`). The design set names neither, anywhere:

```bash
cd /Users/bbhushan/work/git/workspace/warehouse-issues
grep -rc 'validate/code' docs/ issues/ | grep -v ':0' | wc -l   # → 0
grep -c 'debounce' docs/BUILD-SPEC-SCREENS.md                   # → 0
```

This is not an abstract omission. §2.1's fourteen catalogues, the 51 Department-shape masters and every
`code`-bearing master in `DATA-MODEL.md`'s "Natural" row (`:89` — `whb_items.code`,
`whb_locations.code`, `whb_warehouses.code`, `whb_counterparties.code`, `whb_owners.code`,
`whb_uoms.code`, *"every catalogue's `code`"*) carry a unique key, and several carry a **partial**
unique index whose violation the screen block itself promises to surface as a field error:

- WS-019 Owners: *"the `is_house` partial unique index means the modal must refuse a second house owner
  per company with a **field-level error rather than a 500**"* (`BUILD-SPEC-SCREENS.md:942-944`) — the
  obligation is stated, the mechanism that satisfies it is not.
- WS-015 Companies: *"a partial unique index enforces one default"* (`:801`).
- WS-023 Items: `uk(owner_id, sku)` **and** `uk(code)` (`DATA-MODEL.md:527`), on a screen whose primary
  bulk path is a 40,000-row import.

**Why it matters.** Without the validate endpoints, uniqueness is discovered at submit, as a
`DataIntegrityViolationException` the service did not catch, which reaches the user as the opaque 500
this monorepo has a memory entry about. The screen spec has *stated the requirement* — WS-019's
"field-level error rather than a 500" — while omitting the only mechanism in the house that delivers
it. That is the exact failure mode my lens hunts: a block that reads complete and cannot be built
without a decision the builder is not authorised to make (namely: what is the endpoint called, what
does it take, what does it return, and which field does the error bind to).

**Cost if found late.** One endpoint pair per entity across ~65 masters, retro-fitted, plus a debounced
call per modal — and the modals will already have been written and reviewed as complete.

**Recommendation.** One row in §0.6 (Modals): *"every master modal with a unique key carries the
`GET /validate/{code|name}` pair of the Department reference (`DepartmentController.java:301,318`),
called debounced at ≥300 ms on blur, binding its error to the field."* Then, per screen, state only the
**partial**-unique cases that need more than the generic pair — WS-019's `is_house`, WS-015's
`is_default`, WS-023's `uk(owner_id, sku)` — because those are the ones a generic `/validate/code` does
not cover.

---

### `RB-008` · Four enumerated-`select` filters have no option list and no source, and WS-212's `bucketSetCode` contradicts its own frozen columns — **MAJOR**

**What I found.** §0.2 promises that every dropdown's source is named. For catalogue-backed filters it
is (the fourteen registries of §2.1 back them, and `D-10` forbids a hard-coded vocabulary). For four
*computed-bucket* filters there is no table, no vocabulary and no option list:

| Filter | Screens | What populates it? |
|---|---|---|
| `bucketSetCode` select | WS-212 (`:1986`) | **nothing.** `grep -c 'bucket_set' docs/DATA-MODEL.md` → 0 |
| `ageOverDays` select | WS-098 (`:1640`), WS-122 (`:1740`), WS-220 (`:1994`) | unstated on all three |
| `inTransitOverDays` select | WS-090 (`:1619`), and it is the mobile filter (`p2-02.md:49`) | unstated |
| `rejectionCode` select | WS-052 (`:1411`), WS-097 (`:1639`), WS-170 (`:1831`) | unstated. `FR-039`'s 21 port codes are the obvious source, but `FR-039` scopes them to *"the port's"* vocabulary and WS-097 rows are written by the port **and** by the UI |

**`bucketSetCode` is worse than unstated — it is self-contradicting.** WS-212's columns are six
hard-coded buckets: `bucket0_30`, `bucket31_60`, `bucket61_90`, `bucket91_180`, `bucket181_365`,
`bucketOver365` (`:1986`). A `bucketSetCode` selector's entire purpose is to change the bucket
boundaries — and a grid whose `grid_column_definitions` rows are frozen to *one* bucket set cannot
render a second one. Either the columns are dynamic (which no grid in this monorepo is) or the filter
should not exist. The task, `p2-20.md`, does not mention the filter at all.

**Evidence.** `docs/BUILD-SPEC-SCREENS.md:1411`, `:1619`, `:1639`, `:1640`, `:1740`, `:1831`, `:1986`, `:1994`;
`issues/p2-02.md:47-51`; `issues/p2-20.md:17` (WS-212's rule, with no bucket-set concept);
`grep -c 'bucket_set' docs/DATA-MODEL.md` → 0.

Contrast with the two the document got right: `expiringWithinDays` states its options inline
(*"30/60/90"*, `:1170`) and `occurredWithin` states *"Today / 7 days / 30 days"* (`:1300`). The pattern
exists; it was applied twice out of six.

**Why it matters.** A `select` with no option list is not buildable — the builder invents the options,
and because these are the *mobile* filters too (`p2-02.md:49` says so explicitly), they get invented
twice, on two surfaces, by two people, and `mobile/src/schemas/common.schemas.ts` is a third copy of
every dropdown vocabulary (§0.7 already warns about this). Three copies of an invented list is three
chances for a value the backend accepts and the mobile schema rejects with no message.

**Cost if found late.** Small per filter, but `ageOverDays` alone appears on three screens in two
phases, so the divergence is structural rather than accidental.

**Recommendation.** State the options inline for `ageOverDays` and `inTransitOverDays` the way
`:1170` and `:1300` already do (one list, reused — an ageing bucket set is a product decision, not a
per-screen one, and it is the same decision `FR-388` and `FR-162` are already making). Point
`rejectionCode` at `FR-039`'s vocabulary explicitly and say whether UI-originated refusals extend it.
Delete `bucketSetCode` from WS-212, or make the six bucket columns a stated consequence of one
seeded default bucket set — but not both.

---

### `RB-009` · Nineteen screen-level refusals, five named error codes, and no register that binds any of them to a field — **MAJOR**

**What I found.** `docs/contracts/README.md` states the obligation exactly right:

> *"Every guard, as a predicate over named columns, and what a violation returns to the user: **the
> field and the message shape**, not just 'an error'."*

— and then says, correctly, that no contract exists yet because *"a contract describes a built
workflow"*. So at build time nothing carries that obligation, and the screen spec does not fill the
gap. It describes **19 refusals** and names **five** error codes across all of them:

```bash
cd /Users/bbhushan/work/git/workspace/warehouse-issues
grep -icE 'refus|blocked with|is refused|must refuse' docs/BUILD-SPEC-SCREENS.md      # → 19
grep -iE  'refus|blocked with|is refused|must refuse' docs/BUILD-SPEC-SCREENS.md \
  | grep -oE '`[A-Z][A-Z0-9]+(_[A-Z0-9]+)+`' | sort -u
# `CONVERSION_IN_USE` `ITEM_HAS_LEDGER_ROWS` `ITEM_HAS_STOCK` `OWNER_HAS_STOCK` `PENDING_RESOLUTION`
# (the rest of the matches are filter-scope tokens, not codes)
```

The set has exactly **one** error-code register, `FR-039` (21 codes,
`WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md:165`), and `FR-039` is explicit that it is **the port's**
vocabulary. `PORT-AND-ADAPTER-CONTRACT.md:563` gives each of those a HTTP status, a retryability flag
and a **scope (`line` / `header`)** — which is the field binding `contracts/README.md` asks for, done
properly, for the port and only for the port. The screen refusals — deactivation guards, freeze
refusals, ladder guards, threshold guards — have none of it.

Concretely, these refusals are described in prose with no code, no field and no message shape:
WS-016's site deactivation, WS-017's Block/Unblock guard, WS-021's role end-dating, WS-045's *"each
refusing while `pendingHandoverCount > 0`"* (`:1391`), WS-072's cancel cascade *"refused if any GRN
line has received stock, **and the modal says which**"* (`:1511-1512`), WS-094's *"the counter may not
approve their own count"*, WS-097's force-with-approval, and the four `wh3_` money guards of §0.11.

**Why it matters.** `FR-039` states that **renaming a code is a breaking change to five callers**, so
a code invented at build time by whoever writes the service is a name the mobile app, the port, the
adapters and the i18n files must all live with. And the guards that most need a field binding are the
ones §0.12 already flagged: *"Where the freeze is refused, the error names the field and the blocking
fact — `ITEM_HAS_LEDGER_ROWS`, `ITEM_HAS_STOCK`, `PERIOD_HAS_MOVEMENTS` — with the count"*
(`:423-424`). That is the right rule, written once, for one of the nineteen.

There is a mechanical reason this cannot be deferred: `contracts/README.md` itself notes that *"a
deferred constraint trigger raises at `COMMIT`, outside every `@Transactional` boundary, so no service
`catch` can translate it and the message never reaches a form field"* — and §0.12 puts **three of the
nine load-bearing freezes on triggers**. For those three, the error code and its field binding are not
a presentation choice; they are a design constraint on where the check lives.

**Cost if found late.** Nineteen invented code strings across five modules and three surfaces, each a
breaking rename once shipped, plus nineteen missing i18n keys (`Q-005` records that P2's validation-message
i18n already has no owner).

**Recommendation.** Extend `FR-039`'s register rather than starting a second one — one table in
`BUILD-SPEC-SCREENS.md` §0, in `PORT-AND-ADAPTER-CONTRACT.md:563`'s exact columns
(`code` · HTTP · retryable · **scope: field / header / line**), with one row per screen refusal, seeded
with the five codes that already exist. Then the per-screen block cites a code instead of describing a
refusal, and `check-design-set.py` can assert that every `refused`/`blocked` sentence carries one.

---

## §3 · What I checked and found sound

The following were candidates for findings and survived the check. They are recorded because a later
reviewer will otherwise re-derive them.

1. **The eight filter types are right.** §0.4 quotes `FilterFieldType` and I confirmed all eight
   buckets exist — `text`, `select`, `enum`, `multiselect`, `boolean`, `date`, `dateOnly`, `number`
   (`platform/frontend/src/utils/filterUtils.ts:36-59`). §0.4's two consequences (no range type, so
   every from→to is two keys; `dateOnly` for SQL `DATE` columns) are both correct and correctly
   reasoned — `:49-56` is the comment §0.4 paraphrases. Every `…Min`/`…Max` **number** pair I sampled
   (WS-089's `valueImpactMin`/`Max`, WS-195's `yearFrom`/`yearTo`, WS-226's `mrpFrom`/`mrpTo`) is
   expressible in the `number` bucket.
2. **The `WAREHOUSE_*` scope namespace does not collide with itself.** Stripping the module infix from
   all 204 named scopes and looking for duplicates returns nothing —
   `sed -E 's/^WAREHOUSE_(3PL|INDIA|DEALER|SERVICES|FIELD_SERVICE|ASSETS)_/WAREHOUSE_/' | sort | uniq -d`
   → empty. Two grids in different warehouse modules will not overwrite each other's allowlist entry.
3. **The 20 report `gridIdentifier`s are correctly declared as non-tables.** §0.2's rule is
   *"gridIdentifier = the table name"* and the `wh_rpt_*` family breaks it — but `DATA-MODEL.md:3538-3561`
   pre-empts exactly that reading with an explicit "these are grid identifiers, not tables; there is no
   DDL for any of them" and a twenty-row table. That is the right defence written in the right place.
4. **`whb_lpns`' status vocabulary matches** across `DATA-MODEL.md:574` and WS-038 (`:1198`):
   `OPEN`/`CLOSED`/`SHIPPED`/`CONSUMED`. So does `whb_locations.status`
   (`AVAILABLE`/`BLOCKED`/`COUNTING`/`DAMAGED`/`FROZEN`, `:451` vs `:861`) and `whb_items`'
   `lot_control_mode`, `serial_control_mode` and `expiry_policy`. `RB-004` is the only vocabulary
   divergence I found in the sample.
5. **WS-023's seven modal tabs map to real columns.** Every field named across *Identity*,
   *Classification*, *Units*, *Control*, *Status facts*, *Tax & compliance* and *Attributes*
   (`:1046-1053`) resolves to `DATA-MODEL.md:527`, including `purchase_uom_code`, `sale_uom_code`,
   `min_shelf_life_receipt_pct`/`_ship_pct` and the whole hazmat block. §0.6's ">6 groups → multi-tab"
   rule is correctly applied here and on WS-017.
6. **`FR-395`'s no-cache-name rule for filter-aware statistics is right**, and §0.3's reasoning
   (`CacheConfiguration.java:190-196`, issues `#790`/`#791`) matches the live file. This is the one
   place a design set would normally get CLAUDE.md CRITICAL #2 wrong by over-applying it.
7. **`filter_definitions` vs the non-existent `grid_filter_definitions`** is correctly stated at §0.5
   and §9.1, with the right migration (`V229`) and the right failure mode.
8. **The mobile `none` verdicts carry reasons.** Of the ~40 `Mobile:` rows I read, every `none` gave a
   reason, per `D-13`/`FR-218`. That obligation is genuinely met — the failure in `RB-001` is in the
   *constraint* the reasons appeal to, not in the discipline of stating them.

---

## §4 · Refused

Every candidate below was found, checked against the round-1 and round-2 registers, and **not filed**
because an existing id owns it.

| Candidate I found | Owned by | Why I refused it |
|---|---|---|
| No screen states which modal fields are mandatory, their maximum length, or their `@Pattern` | **`H-002`** (MAJOR, `DECISION`) | `H-002` is *"no table in the design set carries a column-level DDL specification"*, disposition = a human decision then `DATA-MODEL.md`. Field length and nullability are that decision's output. `O-007` (`FOLD-DOC` into `H-002`) is the same thing measured against the house prior art |
| WS-090, WS-094, WS-099 and ~35 other screens filter and badge on `status` with no vocabulary anywhere | **`Q-002`** (BLOCKER) | *"`status` has no declared domain for 30 v1 tables and 38 v1 screens"*. `RB-004` is filed only because `lifecycle_status` **is** declared — twice, differently |
| 115 of the sampled grids state no per-column `sortable` / `default-visible` | **`Q-004`** (MAJOR) | exactly the finding, with the same count method, folded to `P2-29`/`P0-15`/`P1-20` |
| Most master screens state no `Frozen when` per field | **`Z-004`** (MAJOR, `FOLD-DOC`) | §0.12 was written *as* its disposition, and it states the completion rule for the rest |
| The P3/P4 transition modals I sampled (WS-080 disposition, WS-082 override) have no verb permission string | **`X-014`** | *"§10.2 lists no verb permission for any P3 or P4 transition"* |
| The 27 P5/P6 screens outside §4 have no verb permissions | **`H-001`** (`FOLD-DOC` → §10.2) | §10.2's own closing paragraph already records it as a known hole |
| Modal titles, verb-button labels and validation messages have no i18n owner | **`Q-005`** (MINOR) | folded to `P2-29`. `RB-009` is filed on the *codes and their field binding*, not on their translation |
| WS-076's mobile row routes receiving to WS-229 RF Receive, which is v1.1, so v1 has no mobile receiving | **`U-001`** class | `U-001` is *"no carton can be created in v1: the only screen with a create/seal action is v1.1"* — the identical shape. A second instance is not a second finding |
| WS-086's dock schema is v1 and its screen v1.1 | **`X-019`/`X-020`** + **`U-004`** | the `Ver · Ph` disagreement register, and `U-004` owns `arrived_at`'s missing v1 writer specifically |
| WS-132 Print Jobs shows a `printerName` column over a v1.1 table | **`U-006`** (MINOR) | filed verbatim in round 2 |
| WS-208…WS-225's `:view`/`:export` permission strings are named in no P2 task file | **`Q-001`** (BLOCKER) | *"The P2 wave's 25 verb permissions, their dependency rows and their menu grants have no migration to live in"*, folded to `P2-29`, which is where the report permissions land too |
| WS-194's `priceLevel` is a keystroke on the counter-sale flow with no vocabulary and no source — the same shape as `RB-008` | **`RA-002`** (BLOCKER, `R16`, this round) | R16 ran concurrently on the role/persona lens and reached the same field from the other side, with the far more serious half: there is no price table anywhere in the data model. Its finding subsumes mine; I did not restate it, and `RB-008` deliberately covers only the four *bucket* selects R16 does not touch |
| Six tables named in the screen blocks I read have no `DATA-MODEL.md` row | **`X-053`** (MAJOR) | *"Forty-six tables are named in task files with no `DATA-MODEL.md` row"* |
| `BUILD-SPEC-SCREENS.md` §1's stated command returns **431**, not the 237 it claims, and §11.1's returns **0**, not 215 | *(not refused — see below)* | filed as the MINOR note at the end of `RB-003`'s evidence block rather than as a tenth finding, because the underlying numbers are right when the awk range is scoped to §1: `awk '/^## 1\. Screen index/,/^## 2\./' … \| grep -cE '^\| WS-[0-9]{3} \|'` → **237**, and `… && $7 ~ /Y/` → **214**. §11.1's *"215 scopes"* has no such rescue — its stated command greps a section that contains no scope names, and the document enumerates **204** distinct scope tokens in total. The two commands need replacing; the 215 needs recomputing or the missing ~11 scopes naming. This belongs in the same editing pass as `RB-003` |

---

## §5 · Counts

```bash
cd /Users/bbhushan/work/git/workspace/warehouse-issues
grep -cE '^### `RB-[0-9]{3}`' docs/reviews/R17-screen-and-field-buildability.md   # → 9
grep -cE '^\| .* \| \*\*.*\*\* \|' docs/reviews/R17-screen-and-field-buildability.md  # tables, not findings
```

| Severity | Count | Findings |
|---|---|---|
| **BLOCKER** | 2 | `RB-001` `RB-002` |
| **MAJOR** | 7 | `RB-003` `RB-004` `RB-005` `RB-006` `RB-007` `RB-008` `RB-009` |
| **MINOR** | 0 | — |
| **Total** | **9** | |

**Where they land** (proposed; the round-3 register decides):

| Finding | Bucket | Lands in |
|---|---|---|
| `RB-001` | FOLD-DOC | `reviews/R1` (`C-044` amendment) → `FR-220`, §0.7, `IRREVERSIBLE.md:723`, `DATA-MODEL.md:4172`, `INDIA-LOCALISATION-PACK.md:446`, `PLATFORM-DEPENDENCIES.md:369`, then `p0-16` `p1-12` `p1-13` `p2-08` `p2-10` |
| `RB-002` | FOLD-DOC + FOLD-TASK | `BUILD-SPEC-SCREENS.md` WS-017 (`:862-879`) + `P1-05` (the three fields that need a decision) |
| `RB-003` | FOLD-TASK | `p2-05.md:49,95` · `p2-02.md:46` |
| `RB-004` | FOLD-DOC | `DATA-MODEL.md:527` |
| `RB-005` | FOLD-DOC + FOLD-TASK | `MODULE-INTEGRATION.md` §12 (a third shared platform file) + `P2-29` Traps |
| `RB-006` | FOLD-DOC | `BUILD-SPEC-SCREENS.md` §0 (a new §0.13, in §0.7's shape) |
| `RB-007` | FOLD-DOC | `BUILD-SPEC-SCREENS.md` §0.6 (Modals) |
| `RB-008` | FOLD-DOC | `BUILD-SPEC-SCREENS.md` §7 (WS-212), §3.2 (WS-098, WS-090, WS-097), §3.3 (WS-122), §7 (WS-220), §2.8 (WS-052) |
| `RB-009` | FOLD-DOC | `BUILD-SPEC-SCREENS.md` §0 (a new error-code register in `PORT-AND-ADAPTER-CONTRACT.md:563`'s columns) |

**Zero of the nine needs a new task**, and eight of the nine are edits to one document. `RB-005` is the
only one that reaches outside the design set — it names a change to a platform test that the set has
not previously counted among the platform files it must touch, and §11's own honesty about *"never
zero commits to `platform`"* is the right place to record it.
