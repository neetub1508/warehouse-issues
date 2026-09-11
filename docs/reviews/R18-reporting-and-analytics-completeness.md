# R18 — reporting, analytics and the information-output surface


> **Date** 2026-09-02 · **Branch** `docs/round-3-functional-completeness` · **Finding prefix** `RC-`
> (`grep -rohE "\bRC-[0-9]{1,3}\b" docs/ issues/ | wc -l` → **0**, so the namespace was free, and
> `RC-` cannot be read as an `R`- or `C`- finding: `check-design-set.py`'s `FINDING_CITE_RE`
> requires a hyphen immediately after a single register letter.)
>
> **File set.** The design set is 186 markdown files / 58,046 lines
> (`find docs issues -name '*.md' | wc -l` → `186`;
> `cat $(find docs issues -name '*.md') | wc -l` → `58046`). Read whole: `DECISIONS.md`,
> `DATA-MODEL.md`, `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` §6.22 and §6.24–§6.26,
> `BUILD-SPEC-SCREENS.md` §7 and §8, `COMPETITOR-BENCHMARK.md`, `GAP-REGISTER.md`,
> `GAP-REGISTER-R2.md`, `docs/reviews/R13`, and `issues/p2-18`, `p2-20`, `p2-21`, `p0-13`, `p2-16`.
> `COEXISTENCE.md`, `IRREVERSIBLE.md`, `IMPLEMENTATION-PLAN.md`, `SCENARIO-CATALOGUE.md`,
> `PORT-AND-ADAPTER-CONTRACT.md` and the remaining 149 task files were searched by grep, not read;
> every count and every negative-evidence command below was run across **all** of `docs/` and
> `issues/`.
>
> On the live side I read `platform/frontend/src/utils/filterUtils.ts`,
> `platform/frontend/src/hooks/useGridPreferences.ts`,
> `platform/frontend/src/components/common/DynamicDataTable.tsx`,
> `platform/frontend/src/components/common/BaseFilter.tsx`,
> `platform/frontend/src/components/common/metricInfo/`,
> `platform/backend/src/main/resources/db/migration/V229__Add_filter_definitions_table.sql`,
> `platform/backend/src/main/resources/db/migration/V557__Extend_widget_definitions_module_constraint.sql`,
> `platform/backend/src/main/java/ai/platform/repository/FilterDefinitionRepository.java`, and
> `accessories/frontend/src/app/accessories/reports/`.
>
> **Method, in three sentences.** Every other lens so far has reviewed what the product *records*;
> this one reviews what it can *tell somebody*. I enumerated the specified output surface with
> commands first — 20 report rows, 21 report screens, 10 widgets, 17 requirements — and then asked
> three questions of each: which clock does it read, which fact does it read, and can the substrate
> render it. Where the set was already right I recorded it in §3 with its id so round 4 does not
> re-walk the ground; I filed only where a decision the product promises to support has no report
> that supports it, or a report is specified over a fact the ledger never captured.

---

## §1 · Verdict

**The report inventory is the most complete I have seen in this repository, and its clocks are not
stated.** Twenty reports, sixteen of them v1, each with a `gridIdentifier`, a filter scope, an export
and an FR; a movement register that carries `occurred_at`, `recorded_at` and `posting_date` as three
separate columns; an as-at stock report that reads the ledger and never the balance table; a
reconciliation the v1 exit criterion turns on. Nothing in the accounting set or the live modules is
close to this. The godown-wise statement, the adjustment register, the count-variance register and
the traceability query are all specified at a level a builder can start from, and `FR-392`'s refusal
to compute a KPI from `updated_at` is exactly the right instinct stated at exactly the right time.

The defect is one shape, and it repeats. **`L-13` says `occurred_at`, `recorded_at` and
`posting_date` are three different columns, and then seven as-at reports never say which of them they
read.** `grep`-verified: of the 20 rows in `BUILD-SPEC-SCREENS.md` §7, seven carry an `asAt*`
parameter and **zero** name the ledger column that parameter is compared against. Two of the seven
disagree with each other by their own parameter *types* — `WS-211`'s `asAtDate` is `dateOnly`, which
`issues/p2-20.md:74` ties to `posting_date`, while `WS-224`'s `asAtDateTime` is an instant, which only
`occurred_at` can answer — and `WH-SC-060` requires those same reports to reconcile *"to the unit and
to the paisa"*. In a product whose entire justification for three timestamps is that they differ, a
reconciliation across two of them is a scenario that passes in the test data and fails at the first
period boundary. That is `RC-001`, and it is the reason this lens exists.

The second defect is the finance seam's flagship. `FR-247`'s stock-to-GL reconciliation is *"the
report that makes a finance director trust the system"*; `WS-219` ships it with **no GL
control-account balance column, no owner grain and no item-group grain**, and its `difference` column
compares warehouse to its own handover outbox rather than to the ledger it is named after. The
number `FR-247` exists to reconcile against lives in `acc_*`, and `WH-SC-162` fails the build on any
`acc_*` reference from `ai.warehouse*`. Nothing in the set defines how that number crosses the seam.
That is `RC-002`.

Below those two, four smaller gaps share a single character: **the set specified the report and not
the substrate that renders it.** A required report parameter has no enforcement point anywhere in
the platform (`RC-005`). A report footer — required by the v1 exit criterion, by `P2-20`'s acceptance
and by the shape of the godown statement — does not exist in `DynamicDataTable` and nobody has
budgeted it (`RC-004`). `L-14` is written onto one enquiry screen and onto none of the fourteen
valued report rows (`RC-006`). And `WS-216` ships a `metricCode`, a `target` and a `variance` with no
table behind any of the three, over a twenty-nine-metric list that this design set never enumerates
(`RC-007`).

**Nine findings: two BLOCKER, six MAJOR, one MINOR.** Eight fold into existing tasks; one needs a
version placement rather than a task. None requires a new migration beyond amendments to migrations
already claimed.

---

## §1.1 · The report inventory, computed

```bash
cd /Users/bbhushan/work/git/workspace/warehouse-issues
awk '/^## 7\. Reports and registers/,/^## 8\. Dashboards/' docs/BUILD-SPEC-SCREENS.md \
  | grep -c '^| WS-'                                                            # → 20  report rows
grep -E '^\| WS-2(0[8-9]|1[0-9]|2[0-8]) ' docs/BUILD-SPEC-SCREENS.md \
  | awk -F'|' '{print $8}' | sort | uniq -c                                     # → 16 v1·P2 · 2 v1.1·P3
                                                                                #   1 v2·P4 · 1 v2·P5 · 1 v3·P6
awk '/^### 6\.22 /,/^### 6\.23 /' docs/WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md \
  | grep -c '^| \*\*FR-'                                                        # → 17  requirements
awk '/^### 8\.2 The widget set/,/^## 9\./' docs/BUILD-SPEC-SCREENS.md \
  | grep -c '^| .* | `warehouse` |'                                             # → 10  widgets
```

| Surface | Count | Where |
|---|---|---|
| Report / register screens (`WS-208`…`WS-227`) | **20** | `BUILD-SPEC-SCREENS.md:1982-2001` |
| — of them v1 · P2 | **16** | index rows `:657-676` |
| Ledger enquiries that are reports in all but name | **9** | `WS-040` `WS-041` `WS-042` `WS-044` `WS-049` `WS-063` `WS-064` `WS-098` `WS-146` |
| Dashboard widgets (v3 · P6, `WS-228`) | **10** | `BUILD-SPEC-SCREENS.md` §8.2 |
| Requirements in §6.22 *Reports, KPIs and analytics* | **17** | `FR-384`…`FR-400` |

**The clock question, computed.** This is the number the rest of this review turns on:

```bash
awk '/^## 7\. Reports and registers/,/^## 8\. Dashboards/' docs/BUILD-SPEC-SCREENS.md \
  | grep '^| WS-' | grep -c 'asAt'                                              # → 7
awk '/^## 7\. Reports and registers/,/^## 8\. Dashboards/' docs/BUILD-SPEC-SCREENS.md \
  | grep '^| WS-' | grep 'asAt' | grep -cE 'asAt.*(occurred_at|posting_date)'   # → 0
```

Seven as-at reports — `WS-211` `WS-212` `WS-222` `WS-224` `WS-225` `WS-226` `WS-227` — and not one
names the column its as-at date is compared against.

**The owner question, computed.** `L-14` is the rule that non-own stock is never valued:

```bash
awk '/^## 7\. Reports and registers/,/^## 8\. Dashboards/' docs/BUILD-SPEC-SCREENS.md \
  | grep '^| WS-' | grep -cE '(value|Value|unitCost|valueImpact|insuredValue)'  # → 14
awk '/^## 7\. Reports and registers/,/^## 8\. Dashboards/' docs/BUILD-SPEC-SCREENS.md \
  | grep '^| WS-' | grep -E 'value|Value' | grep -cE 'L-14|owner_type'          # → 1  (WS-227, v2)
```

**What a manager runs a building on, against this schema.** Each row answers *can it be computed at
all*, not *is a screen specified*:

| Manager's number | Computable? | From what |
|---|---|---|
| Inventory record accuracy | **Yes**, v1 | `wh_counts` variance → `WS-214`, `FR-390` |
| Fill rate | **Yes**, v1 — and honestly, which is rarer | `wh_demand_history` + `wh_insufficient_stock_log`'s `is_lost_sale`, `FR-393` |
| Dock-to-stock | **Schema yes, writer no** | `wh_dock_appointments.arrived_at` — **owned by `U-004`**, not re-filed |
| Order cycle time · on-time ship · dwell · putaway cycle | **Yes**, v1 | lifecycle timestamps, `FR-392`, `FR-213` |
| Pick rate / labour productivity | **Yes**, as measured actuals | `whb_tasks` timestamps from v1 (`FR-213`); engineered standards deliberately refused (`FR-228`) |
| Ageing · slow-moving · dead stock · obsolescence | **Yes**, v1 | `WS-212` + `FR-393`'s twelve-month rule; ageing history begins at the snapshot job (**`PNR-3`**, already owned) |
| Shrinkage | **Yes**, v1 | reason-coded adjustments → `WS-213`, `FR-164` |
| Inventory turns | **Yes**, v1 | `FR-393`, with average inventory value from `whb_stock_position_snapshots` |
| **Space / location utilisation** | **No — in any version** | capacity block exists on `whb_locations` from v1 and nothing reads it → **`RC-009`** |
| **Perfect-order rate** | **No** | needs damage-free and documentation-accuracy facts that no v1 table carries; never named in any `FR-`, any version or any refusal list → folded into **`RC-007`** |
| **Pick accuracy** | **No before v1.1** | requires scan verification (`FR-192`, v1.1) or a mis-pick record; no table carries one → folded into **`RC-007`** |

---

## §2 · The findings

### `RC-001` · Seven as-at reports, and not one says which of `L-13`'s three clocks it reads — while the v1 exit criterion requires two of them, on different clocks by their own parameter types, to reconcile to the paisa — **BLOCKER**

- **What I found.** `L-13` is the invariant that `occurred_at` (when it physically happened),
  `recorded_at` (when we heard) and `posting_date` (the accounting date) are three different columns,
  and `DECISIONS.md` says collapsing them *"kills offline replay, degraded-mode catch-up, cut-off and
  EPCIS simultaneously"*. Every document in the set honours that on the **write** side and none
  honours it on the **read** side. `WS-209`, the movement register, offers `occurredFrom`/`occurredTo`
  **and** `postingDateFrom`/`postingDateTo` as two independent filters — correct, and the set is right
  to be proud of it — but `FR-385` requires that register to render *"in opening → in → out → closing
  shape per item"*, and an opening balance can only be struck on **one** clock. Nothing says which.
  `WS-210`, the godown statement a bank reads against a cash-credit limit, takes `periodId` **or**
  `fromDate`/`toDate` with no column named. `WS-211`'s `asAtDate` is typed `dateOnly`, and the only
  sentence in the set that explains that typing — `issues/p2-20.md:74` — justifies it as
  *"`posting_date` and the statutory dates are `DATE`"*. `WS-224`'s parameter is `asAtDateTime`, an
  instant, and `FR-013`'s `GET /stock/as-at?at=…` is likewise an instant; only `occurred_at` can
  answer an instant. So the valuation-as-at and the stock-as-at are on **different clocks**, by
  construction, undeclared — and `WH-SC-060`, *the v1 exit criterion*, requires the movement register,
  the position report and the valuation report to *"reconcile to each other to the unit and to the
  paisa"* as at one date.
- **Evidence.**
  ```bash
  awk '/^## 7\. Reports and registers/,/^## 8\. Dashboards/' docs/BUILD-SPEC-SCREENS.md \
    | grep '^| WS-' | grep -c 'asAt'                                             # → 7
  awk '/^## 7\. Reports and registers/,/^## 8\. Dashboards/' docs/BUILD-SPEC-SCREENS.md \
    | grep '^| WS-' | grep 'asAt' | grep -cE 'asAt.*(occurred_at|posting_date)'  # → 0
  grep -rn "which clock\|reads .occurred_at. rather than\|as-at is measured on" docs/ issues/
  # → (no output)
  ```
  - `docs/DECISIONS.md:326` — `L-13`, the three columns.
  - `docs/BUILD-SPEC-SCREENS.md:1983` — `WS-209`, both date pairs, no rule for the opening balance.
  - `docs/BUILD-SPEC-SCREENS.md:1984` — `WS-210`, `periodId` **or** `fromDate`/`toDate`, no column.
  - `docs/BUILD-SPEC-SCREENS.md:1985` — `WS-211`, `asAtDate` (`dateOnly`, required).
  - `docs/BUILD-SPEC-SCREENS.md:1998` — `WS-224`, `asAtDateTime` (required).
  - `issues/p2-20.md:74` — the only clock statement in the set, and it points `asAtDate` at
    `posting_date`: *"`postingDateFrom`/`postingDateTo`, `asAtDate`, `fromDate`/`toDate` are
    **`dateOnly`** (`posting_date` and the statutory dates are `DATE`)"*.
  - `docs/SCENARIO-CATALOGUE.md:231` (`WH-SC-060`) and `issues/p2-20.md:87` — the paisa-level
    reconciliation across exactly those reports.
- **Why it matters.** Take one movement: a gate-out that physically happened at 23:40 on 31 March and
  was posted on 2 April into the March period. `occurred_at` = 31 March, `posting_date` = 31 March if
  the period is still open, or 2 April if it is not — and `L-8` makes both legal outcomes reachable.
  Run `WS-224` for 31 March 23:59 and `WS-211` for 31 March. If one reads `occurred_at` and the other
  `posting_date`, the two reports differ by that movement, and both are correct. The v1 exit criterion
  says the build is not done until they agree. A team facing that will make them agree — by quietly
  putting both on whichever clock is easier — and the clock that is easier is `posting_date`, which
  is the one `occurred_at` was partitioned for (`OD-12`) and the one EPCIS, offline replay and the
  bank statement all want to be `occurred_at`. The decision gets taken by an implementer, at 4pm, in
  a query, and nobody records it.
- **Cost if found late.** Low to fix now — this is a column in a spec table. After go-live it is a
  **restatement**: every previously issued as-at figure, bank stock statement, section-44AB
  quantitative statement and 3PL invoice was computed on a clock the customer was never told about,
  and correcting the query changes numbers a third party already holds. `FR-387`'s promise —
  *"reproducing the same answer for the same date next year"* — is technically satisfiable on either
  clock and is worthless when the reader does not know which.
- **Recommendation.** Add a **`Clock` column to `BUILD-SPEC-SCREENS.md` §7's table**, mandatory and
  non-blank for all 20 rows, with three legal values: `occurred_at`, `posting_date`, or *"parameter —
  the user chooses, and the choice is rendered on the report"*. Recommended assignment, following
  `OD-12`'s own reasoning (the as-at query wants `occurred_at`; period close and the statutory
  register want `posting_date`):

  | Report | Clock | Because |
  |---|---|---|
  | `WS-209` register, `WS-224` stock as-at, `WS-212` ageing, `WS-218` traceability, `WS-220` in-transit ageing | **`occurred_at`** | they answer *what physically was*; `WS-209` keeps both filters, and the opening/closing shape is struck on `occurred_at` |
  | `WS-210` godown statement, `WS-211` valuation, `WS-213` adjustment register, `WS-219` stock-to-GL, `WS-226` stock by MRP | **`posting_date`** | they answer *what the books say*; the bank statement, the register and the GL tie must agree with the period |
  | `WS-208` on hand, `WS-215`, `WS-221`, `WS-223` | now — **stated as "current, not as-at"** on the screen | a report of today, labelled |

  Then make `WH-SC-060` honest: it must name the clock all three reports are run on, and a **second
  `edge` scenario** should assert that a movement whose `occurred_at` and `posting_date` fall in
  different periods appears in `WS-224` for one date and in `WS-211` for the other **without either
  being a defect**. Every report footer states its clock beside its reconciliation. Folds into
  **`P2-20`** (six reports), **`P2-18`** (`WS-219`) and **`P2-21`** (the rest); amend
  `BUILD-SPEC-SCREENS.md` §7 and `SCENARIO-CATALOGUE.md`. No migration.

---

### `RC-002` · The stock-to-GL reconciliation ships with no GL column, no owner grain and no item-group grain — and the number it is named after lives in a module the architecture test forbids it to read — **BLOCKER**

- **What I found.** `FR-247` specifies the report in one sentence with five parts: the five-term
  identity, **per site, owner and item group**, **with the GL control-account balance**, and **a
  variance column that drills to the offending movements**. `WS-219` implements the identity and
  drops the rest. Its columns are `periodCode`, `companyName`, `warehouseName`, the five value terms,
  then `handedOverValue`, `pendingValue`, `rejectedValue`, `difference` — there is **no owner column,
  no item-group column, and no GL control-account balance column at all**. `difference` therefore
  reconciles warehouse's closing value to *warehouse's own handover outbox*, which is a useful number
  and is not the number `FR-247` asks for. `issues/p2-18.md:66` addresses only the standalone case —
  *"On a Mode-A install with no accounting module the GL column is empty and the report says so"* —
  and never says where the column's value comes from on **Mode C**, the mode the report exists for.
  It cannot come from a query: `WH-SC-162` requires an architecture test that *"fails the build on any
  `acc_*` reference or `ai.accounting*` import under `ai.warehouse*`"*, and `D-6` gives warehouse no
  chart of accounts. There is no read direction on the port (`PORT-AND-ADAPTER-CONTRACT.md` §4 is
  warehouse→consumer), no envelope back from accounting carrying a balance, and no `whb_` table to
  land one in.
- **Evidence.**
  ```bash
  grep -rn "control account\|control-account" docs/ issues/ | wc -l          # → 8, all restating FR-247
  grep -rn "acc_account_balances\|trial balance\|glControlAccount" docs/ issues/
  # → (no output outside docs/reviews/)
  grep -rn "ownerName\|itemCategoryName" docs/BUILD-SPEC-SCREENS.md | grep WS-219
  # → (no output)
  ```
  - `docs/WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md:450` — `FR-247`, the five parts.
  - `docs/BUILD-SPEC-SCREENS.md:1993` — `WS-219`'s columns and filters, with three of the five absent.
  - `issues/p2-18.md:61-67` — the task restates `FR-247` verbatim and then answers only Mode A.
  - `docs/SCENARIO-CATALOGUE.md:360` (`WH-SC-159`) — asserts the full report *"alongside the GL
    control-account balance"*, so the scenario cannot pass as specified.
  - `docs/SCENARIO-CATALOGUE.md` `WH-SC-162` — the build fails on any `acc_*` reference.
- **Why it matters.** This is the report the whole `D-6`/`D-7` costing-authority decision was taken to
  make possible, and `FR-247` says accounting *"makes it a blocking close precondition"*. On the first
  month-end of the first Mode-C install, the controller opens `WS-219`, sees warehouse's own closing
  value beside warehouse's own handover total, and has learned nothing about whether the sub-ledger
  ties to the GL — which is the only question being asked. The owner grain is not cosmetic either:
  `L-14` means non-own stock contributes quantity and no value, so a reconciliation with no owner
  column cannot show *why* the sub-ledger is lower than the physical count, and a 3PL install cannot
  demonstrate that client stock stayed off its balance sheet. Note this is **not** `O-002`: that
  finding is about accounting's `account_strategy` being unable to resolve warehouse's classification
  quad into the right account. This one is about the reconciliation report having no way to read
  *any* account balance at all. Both must be fixed, and fixing `O-002` does not fix this.
- **Cost if found late.** The columns are cheap; the **interface** is not. Discovering at
  implementation that the GL number cannot cross the seam leaves three bad options — an `acc_*` read
  that fails the architecture test, a manual paste, or a report shipped with a permanently blank
  column that trains the controller to ignore it. The last is what happens in practice, and it is
  indistinguishable from not shipping the report.
- **Recommendation.** Three edits, all before `P2-18`:
  1. Add `ownerName` and `itemCategoryName` to `WS-219`'s columns and `ownerId` / `itemCategoryId` to
     its filters, and make `difference` drill through to the movement register (`WS-209`) filtered to
     the offending period × site × owner × group, per `FR-247`'s last clause.
  2. Add a **`glControlAccountBalance` column** and define its **one** source: a pull-side read on the
     accounting adapter, not a warehouse table — a `GlBalanceProvider` port interface declared in
     `warehouse-base` with **no implementation there**, implemented in the accounting-facing adapter
     and absent on Mode A. That is the same shape `FR-357`'s display resolver already uses (a bean
     collection with a base fallback), so it is a pattern the set owns rather than an invention, and
     it does not put `acc_*` on warehouse's classpath.
  3. State the Mode-A rendering as it already is — an explicit *"no accounting module installed"*
     provider reason, not a blank cell (`FR-398`'s empty-state rule).

  Folds into **`P2-18`**, with one line in `PORT-AND-ADAPTER-CONTRACT.md` §4 recording that this is
  the **only** read direction across the accounting seam, and one line in `MODULE-INTEGRATION.md`.
  Needs `FR-247` amended to name the provider rather than the table. No migration.

---

### `RC-003` · The as-at valuation has no reproducible formula: it reads a column that is mutated in place, and the only rows that could un-mutate it are never named as its input — **MAJOR**

- **What I found.** `FR-387` requires stock valuation with an as-at date *"computed from the ledger,
  reproducing the same answer for the same date next year"*, and `issues/p2-20.md:89` makes it an
  acceptance box: *"`WS-211` run for 31 March today and again next year returns the same figure."*
  `WS-211`'s **Reads** cell says *"ledger + `whb_cost_layers`"*. But `whb_cost_layers` carries
  `quantity_remaining` and `is_open` — both mutated in place as FIFO consumes the layer
  (`DATA-MODEL.md:855`), and `WS-049` renders `quantityRemaining` with a `hasRemaining` filter
  defaulting true. A query over `whb_cost_layers` therefore answers *today*, not 31 March, and the
  same query re-run next year returns a **different** number for the same date, which is precisely
  the failure the acceptance box was written to catch. The rows that make the answer reconstructible
  exist: `whb_cost_layer_consumptions` records `issue_movement_line_id`, **`issue_occurred_at`**,
  `quantity_consumed`, `value_consumed` and `reversal_of_consumption_id`, so the as-at remaining
  quantity of a layer is `quantity_in − Σ consumptions on or before the as-at date, net of reversals`.
  That table is named in the data model, in `P2-16`, in `WS-049`'s drill-down and in `WS-184`'s ITC
  reversal — and **not** in `WS-211`, not in `P2-20`, and not in `FR-387`.
- **Evidence.**
  ```bash
  grep -rn "cost_layer_consumptions" docs/ issues/ | grep -c .        # → 19 mentions
  grep -rn "cost_layer_consumptions" docs/BUILD-SPEC-SCREENS.md | grep -c "WS-211"   # → 0
  grep -rn "cost_layer_consumptions" issues/p2-20.md | wc -l          # → 0
  ```
  - `docs/DATA-MODEL.md:855` — `whb_cost_layers` with `quantity_remaining`, `is_open`.
  - `docs/DATA-MODEL.md:856` — `whb_cost_layer_consumptions` with `issue_occurred_at`.
  - `docs/BUILD-SPEC-SCREENS.md:1985` — `WS-211` reads *"ledger + `whb_cost_layers`"*.
  - `docs/BUILD-SPEC-SCREENS.md:1408` — `WS-049` exposes `quantityRemaining`, `hasRemaining` default
    true — the today-shaped view of the same table.
  - `issues/p2-20.md:89` — the acceptance box the current Reads cell cannot pass.
  - `docs/reviews/R1-codebase-reality.md:526` (`C-027`) — the live accessories valuation report reads
    `last_cost` instead of `average_cost`, so *"the report and the balance disagree by construction"*.
    This is the same class of defect, one table deeper.
- **Why it matters.** The failure is silent and it is directional: every historical valuation is
  *understated*, because layers consumed since the as-at date have already been decremented. The
  first time anyone notices is when last year's 31 March figure is re-run for the auditor and does not
  match the signed accounts — at which point the ledger is right, the report is wrong, and the
  reconciliation certificate (`FR-412`) that the customer signed off is unreproducible.
- **Cost if found late.** Recoverable, but expensively and publicly. The data is all there — this is
  a query rewrite, not a schema change — but it is discovered by an auditor, against a number the
  customer has already filed, and it takes the credibility of `WS-219` and `WS-224` down with it
  because a reader cannot tell which of the three reports is the wrong one.
- **Recommendation.** Change `WS-211`'s **Reads** cell to *"`whb_cost_layers` **net of
  `whb_cost_layer_consumptions` as at the parameter date** — never `quantity_remaining`"*, and add the
  formula to `P2-20`'s scope beside the sentence that already says *"the as-at answer is always
  derived from movements"* (`issues/p2-20.md:25`). Add a trap: *"`quantity_remaining` and `is_open`
  are today-shaped and must not appear in any as-at query; `WS-049` is the only screen that may read
  them."* Extend the acceptance box to a **falsifier**: issue stock after the as-at date, re-run the
  report for the earlier date, and assert the figure is unchanged. Same treatment for `WS-222`, whose
  `value` column has the same source. Folds into **`P2-20`**; amend `FR-387` and `BUILD-SPEC-SCREENS.md`
  §7. No migration.

---

### `RC-004` · Every report is declared "a real grid", the v1 exit criterion requires a report footer, and the grid component has no footer — **MAJOR**

- **What I found.** `BUILD-SPEC-SCREENS.md:1964` opens §7 with *"Every report here is a **real grid**
  … they are not special-cased screens"*, which is the right call and is why the export, filter and
  preference machinery all come for free. It is also why the totals do not. Three v1 obligations need
  a summary row that is not a data row:
  - `WH-SC-060` and `issues/p2-20.md:36,87` — *"**Each report footer states the reconciliation**"*,
    twice, once as a scenario and once as an acceptance box;
  - `FR-386`'s godown statement — opening / inward / outward / closing **with value**, which a bank
    reads against a cash-credit limit and which is meaningless without a column total;
  - `WS-219`'s five-term identity, which is an equation and reads as one only when it is totalled.

  `DynamicDataTable.tsx` is 651 lines and contains the strings `footer`, `tfoot`, `totalRow` and
  `summaryRow` **zero** times. Repo-wide there are five files containing a `<tfoot>` and not one of
  them is a `DynamicDataTable` grid — two are hand-rolled tables in dealer, two the same in services,
  one in mobile. The set never notices: §7's table has no footer, total or summary column, and
  `PLATFORM-DEPENDENCIES.md` — which correctly budgets the *export* streaming path as
  `warehouse-base` work under `PP-6` — has no equivalent row for a totals row.
- **Evidence.**
  ```bash
  grep -c "footer\|tfoot\|totalRow\|summaryRow" \
    platform/frontend/src/components/common/DynamicDataTable.tsx          # → 0
  wc -l platform/frontend/src/components/common/DynamicDataTable.tsx      # → 651
  grep -rln "tfoot" --include=*.tsx . | grep -v node_modules | wc -l      # → 5
  grep -rln "tfoot" --include=*.tsx . | grep -v node_modules
  # → dealer/…/UsedVehiclePurchaseTab.tsx · dealer/…/customerFeedbackPerformance/UsageReport.tsx
  #   mobile/…/ServiceVehicleReplacementTab.tsx · services/…/serviceFeedbackPerformance/UsageReport.tsx
  #   services/…/ServiceVehicleReplacementTab.tsx
  awk '/^## 7\. Reports and registers/,/^## 8\. Dashboards/' docs/BUILD-SPEC-SCREENS.md \
    | grep -ci "footer\|grand total"                                      # → 0
  ```
- **Why it matters.** The two live precedents show what happens when someone needs a total on this
  platform: they abandon the grid and hand-roll a `<table>` — `dealer/…/UsageReport.tsx:339` is
  literally a report page that did exactly that. A warehouse team facing `WH-SC-060`'s footer
  requirement will do the same, and the moment `WS-210` stops being a `DynamicDataTable` it loses grid
  preferences, the column config, the filter strip and — the one that bites — **export parity**,
  because `ExportButton` follows the visible grid columns (`FR-400`). The v1 exit criterion then
  quietly depends on a screen that has left the standard.
- **Cost if found late.** Discovered during `P2-20`, at the end of the v1 critical path, when
  `IMPLEMENTATION-PLAN.md:809` already records that *"`P2-21` is the last link because the v1 exit is
  a reconciliation, not a feature"*. The choices at that point are to hand-roll (losing the substrate)
  or to slip the exit criterion.
- **Recommendation.** Two parts, and the first is free:
  1. **Use the mechanism that already exists for a headline number.** The filter-aware statistics
     strip is exactly a report total and `FR-395` already mandates it uncached for these screens. Add
     a **`Statistics strip` column to §7's table** and state the tiles for all 20 rows — for `WS-210`
     that is closing quantity and closing value; for `WS-219` the five terms and the difference; for
     `WS-211` total value and the method used. Today §7 states tiles for none of the 20, while the
     detailed blocks state them for the screens that have one (`WS-040`, `BUILD-SPEC-SCREENS.md:1296`).
  2. **Where a per-column total genuinely belongs under the columns** — `WS-210` is the only v1 case,
     because a bank statement is read column-wise — add a `PP-`-style row to `PLATFORM-DEPENDENCIES.md`
     budgeting an optional `summaryRow` prop on `DynamicDataTable` as **platform** work, proposed
     separately, exactly as `PP-6` handled the export cap. Do **not** hand-roll a second table
     component.

  Folds into **`P2-29`** (the grid-config task) for the strip definitions and **`P2-20`** for the
  reconciliation footer wording; one new `PLATFORM-DEPENDENCIES.md` row. No migration.

---

### `RC-005` · A required report parameter has no enforcement point anywhere in the platform, and the failure mode is the set's own words — "a report of today, mislabelled" — **MAJOR**

- **What I found.** `issues/p2-20.md:20` is unambiguous: *"**`asAtDate` on `WS-211`/`WS-212` and
  `asAtDateTime` on `WS-224` are required parameters, not filters.** A report of this shape with no
  as-at date is a report of today, mislabelled."* §7's own preamble adds that *"a parameter is still a
  `filter_definitions` row and still needs a scope entry, or it is silently dropped like any other
  field"*. Both are right, and neither names an enforcement point. The platform has exactly one
  mechanism called `is_required` and it does something else: `filter_definitions.is_required` exists
  (`V229:15`), and the only place the frontend reads it is
  `useGridPreferences.ts:487`, where it **prevents the user hiding the filter chip** —
  `logger.warn('Cannot hide required filter')` — and nothing more. `BaseFilter.tsx` contains the
  string `required` **zero** times, so nothing blocks submit. On the backend,
  `FilterDefinitionRepository.java:24-25` declares
  `findRequiredFiltersByGridIdentifier` and that method has **zero callers repo-wide**, so nothing
  refuses the query either. Of the seven parameterised reports, exactly **one** — `WS-218` — states a
  refusal (*"at least one required — the query is refused, not silently unbounded"*), and `P2-21`
  turns it into an acceptance box. The other six state no refusal, no default and no label.
- **Evidence.**
  ```bash
  grep -c "required" platform/frontend/src/components/common/BaseFilter.tsx        # → 0
  grep -rn "findRequiredFiltersByGridIdentifier" --include=*.java . \
    | grep -v node_modules | wc -l                                                 # → 1 (its own declaration)
  ```
  - `platform/backend/src/main/resources/db/migration/V229__Add_filter_definitions_table.sql:15` —
    `is_required BOOLEAN NOT NULL DEFAULT FALSE`.
  - `platform/frontend/src/hooks/useGridPreferences.ts:487` — the only consumer: it gates
    `toggleFilterVisibility`, i.e. hiding, not running.
  - `platform/backend/src/main/java/ai/platform/repository/FilterDefinitionRepository.java:24` — the
    query that would let a controller enforce it, with no caller.
  - `docs/BUILD-SPEC-SCREENS.md:1992` — `WS-218`, the one report that states the refusal.
- **Why it matters.** `WS-211` opened with no `asAtDate` will do one of two things and the set does
  not say which: return today's valuation under a heading the user believes is dated, or return
  nothing. The first is worse and is the likelier default, because the backend has no reason to reject
  a null parameter it was never told was mandatory. `p2-20` names the consequence precisely and then
  leaves it unenforced. There is a second, sharper case: `WS-224` and `WS-209` also carry
  *"an enforced date-range filter"* as v1's answer to `PP-7`'s OFFSET-depth problem
  (`issues/p2-20.md` traps) — that enforcement rides on the same non-existent mechanism, so
  *"every report has an enforced bounded scope; none opens on 'all time'"* (`p2-20` acceptance) is
  today an acceptance box with no implementation behind it.
- **Cost if found late.** Cheap to build and expensive to discover: a wrong-but-plausible number on a
  finance report is the single hardest defect class to detect, and the first person to catch it is
  usually an external party. The performance half is worse — an unbounded `WS-209` on a 100M-row
  ledger is the timeout `PP-7` was written to prevent.
- **Recommendation.** State the enforcement point as a **backend** rule, once, for all parameterised
  reports: the report controller reads its grid's required filters (the `FilterDefinitionRepository`
  query that already exists and has no caller) and returns a **field-level `400`** naming the missing
  parameter — the same shape `WS-218` already specifies, generalised. Add to §7's preamble: *"a
  required parameter is refused server-side with a field-level error; a report that silently defaults
  to today is a defect"*, and add the mandatory-parameter refusal to `P2-20`'s and `P2-29`'s
  acceptance. On the frontend, the parameter renders above the filter strip and the grid does not
  fetch until it is set — a page rule, not a `BaseFilter` change. Folds into **`P2-29`** (which owns
  the grid/filter-config band) with acceptance boxes in **`P2-20`** and **`P2-21`**; the `V5…`
  `filter_definitions` inserts already carry `is_required` and need no schema change.

---

### `RC-006` · `L-14` is written onto one enquiry screen and onto none of the fourteen valued report rows — including the one that goes to a bank — **MAJOR**

- **What I found.** `L-14` and `FR-112` are categorical: non-own stock is never valued, it carries
  `cost_basis = ZERO_BAILMENT`, and what we hold for it is *"a custody liability and an insured
  value — a different number, on a different report"*. The build spec honours this in exactly two
  places: `WS-042`'s `unitCost`/`value` row, which says *"**suppressed where `owner_type != OWN`**"*
  (`:1345`), and the *"stock value by site"* widget, *"non-own stock excluded"* (`:2047`). Of the 20
  report rows in §7, **14 carry a money column** and **1** mentions `owner_type` or `L-14` — and that
  one is `WS-227`, the custody report, which is **v2 · P5**. So in v1 and v1.1 there are thirteen
  valued reports with no stated owner-type treatment, no `ownerType` column, and no default; and the
  report that is supposed to carry the other number does not exist yet. `WS-210`, the godown-wise
  statement, is the sharp case: `FR-386` says *"a bank asks for it monthly against a cash-credit
  limit"*, and its `ownerId` is an optional filter with no default and no owner-type column, so the
  default rendering aggregates every owner's quantity into one closing column.
- **Evidence.**
  ```bash
  awk '/^## 7\. Reports and registers/,/^## 8\. Dashboards/' docs/BUILD-SPEC-SCREENS.md \
    | grep '^| WS-' | grep -cE '(value|Value|unitCost|valueImpact|insuredValue)'   # → 14
  awk '/^## 7\. Reports and registers/,/^## 8\. Dashboards/' docs/BUILD-SPEC-SCREENS.md \
    | grep '^| WS-' | grep -E 'value|Value' | grep -cE 'L-14|owner_type'           # → 1  (WS-227, v2)
  ```
  - `docs/DECISIONS.md:339` — `L-14`.
  - `docs/WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md:267` — `FR-112`, `cost_basis` including
    `ZERO_BAILMENT` and `INFORMATIONAL`.
  - `docs/BUILD-SPEC-SCREENS.md:1345` — `WS-042`, the one screen that states the suppression.
  - `docs/BUILD-SPEC-SCREENS.md:1984` — `WS-210`, value columns, `ownerId` optional, no owner type.
  - `docs/BUILD-SPEC-SCREENS.md:2001` — `WS-227`, the custody report, **v2**.
  - `docs/WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md:445` (`FR-242`) — `owner_id` answers the consignment
    cut-off, so non-`OWN` owners are reachable in v1, not only in the 3PL release.
- **Why it matters.** This is not the same rule as `K-002`/`FR-450`, which suppress cost from an
  *actor* who lacks `warehouse:cost:view`; `FR-450` itself says so — *"`L-14` suppresses another
  owner's value from a 3PL client; it says nothing about the storekeeper"*. The reverse is also true
  and is what is missing: `FR-450` says nothing about the owner axis on a report. The concrete
  outcome is a godown statement that shows a bank a closing quantity including goods held on
  consignment, or a closing value that silently sums `ZERO_BAILMENT` lines as zero and so understates
  nothing while overstating quantity — either way a number a third party relies on that no document
  defines. `p2-18`'s trap gets the *posting* side right and the *reporting* side is unstated.
- **Cost if found late.** Reversible in code and not in trust. It is the failure `p2-18` already names
  in the other direction: *"a 3PL that posts its clients' stock to its own balance sheet has a
  catastrophe in both directions."* A bank statement is that catastrophe with a counterparty attached.
- **Recommendation.** Add one line to §7's preamble, applying to all 20 rows: *"`L-14` — every value
  column is suppressed where `owner_type != OWN`, as on `WS-042`; every report carrying a value column
  also carries `ownerTypeCode` as a column and an `ownerType` filter defaulting to `OWN`, and states
  on the report which owners are included."* Give `WS-210` an explicit **`ownerTypeCode` default of
  `OWN`** with the inclusion stated in the footer, because that is the report that leaves the
  building. Add a scenario to `SCENARIO-CATALOGUE.md`: consignment stock at `SITE-A`, run `WS-210`,
  assert the closing quantity excludes it by default and that including it is a visible, labelled
  choice. Folds into **`P2-20`** and **`P2-21`**; no migration; no new `FR-` needed — `FR-112` already
  carries the rule and only the report rows need to obey it.

---

### `RC-007` · The KPI report has a metric vocabulary, a target and a variance, and none of the three has a table — over a twenty-nine-metric list this design set never enumerates — **MAJOR**

- **What I found.** `FR-394` promises that *"the twenty-nine-metric warehouse KPI list is computed
  from the ledger"* and `WS-216` renders `metricCode`, `metricName`, `value`, `unit`, **`target`** and
  **`variance`**. Three things are missing behind that row.
  1. **The list.** The phrase *"twenty-nine-metric"* appears in five places and the twenty-nine
     metrics are enumerated in **none** of them. The only enumeration anywhere is a prior-art column
     in `docs/reviews/R6-prior-art-triage.md:306`, describing the **deleted** product's
     `wms_kpi_snapshots` table, and `P-058` is dispositioned `ADAPT` — *"take the metric list"*. A
     list nobody has transcribed is a list nobody can check, and checking it matters: at least three
     of its metrics have **no fact source in this schema** — `location_utilization_pct`
     (see `RC-009`), `perfect_order_rate_pct` (needs damage-free and documentation-accuracy facts no
     v1 table carries, and the phrase *perfect order* appears in no requirement, no version and no
     refusal list), and `pick_accuracy_pct` (needs a mis-pick record; scan verification is `FR-192`,
     v1.1, and nothing records a mis-pick before it).
  2. **The vocabulary's table.** `metricCode` is an extensible vocabulary, and `D-10` is categorical
     that every extensible vocabulary in this product is *"a catalogue table with no `CHECK`
     constraint"* with `code`, `name`, `owning_module`, `is_system` and behaviour flags. There is no
     `whb_metric_definitions` / `wh_metrics` anywhere in `DATA-MODEL.md`.
  3. **The target.** `grep` for a KPI target or metric-definition table returns nothing. `target` and
     `variance` are columns with no source, no screen to set them on, and no permission.
- **Evidence.**
  ```bash
  grep -rn "twenty-nine\|29 metric\|29-metric" docs/ issues/ | wc -l               # → 8 mentions
  grep -rn "twenty-nine" docs/WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md docs/DATA-MODEL.md \
    docs/BUILD-SPEC-SCREENS.md issues/ | grep -c ":.*1\..*2\..*3\."                # → 0 (no enumeration)
  grep -rn "kpi_target\|metric_definition\|metric_target\|whb_metrics\|wh_metrics" docs/ issues/
  # → (no output)
  grep -rn -i "perfect.order" docs/ --include=*.md | grep -v reviews/              # → (no output)
  ```
  - `docs/WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md:695` — `FR-394`, the promise.
  - `docs/BUILD-SPEC-SCREENS.md:1990` — `WS-216`'s `metricCode` / `target` / `variance`.
  - `docs/DATA-MODEL.md:1114` — `wh_kpi_snapshots` (**v1.1**) described as *"the 29 metric columns of
    `FR-394`"*, which is a forward reference to a list that does not exist.
  - `docs/reviews/R6-prior-art-triage.md:306` — the only enumeration, of the prior product's table.
  - `docs/DECISIONS.md` `D-10` — the catalogue-table rule `metricCode` should obey.
- **Why it matters.** `FR-393` gets this exactly right for the four parts KPIs — it freezes each
  definition and requires it *rendered in the metric explainer*, on the principle that *"a KPI a
  manager cannot reproduce by hand is a KPI they will not trust"*. `FR-394` then asks for
  twenty-five more with no list, no definitions and no home for the definitions. A builder starting
  `P2-21` cannot tell whether they are done, a reviewer cannot tell whether a metric is missing, and
  the metrics that are genuinely uncomputable are invisible precisely because nobody wrote them down.
  The `target` column is the small version of the same problem: it will either be hard-coded or
  silently dropped, and `FR-165`'s rule — *"a threshold column with no scheduled job that reads it is
  a defect at the moment it is merged"* — applies with equal force to a target column with no screen
  that writes it.
- **Cost if found late.** Low if fixed now; at `P2-21` it is the last link on the v1 critical path
  (`IMPLEMENTATION-PLAN.md:809`) and the team will either enumerate the list themselves under time
  pressure or ship the four `FR-393` KPIs and quietly drop `FR-394`. The unrecoverable part is the
  subset: a metric whose fact was never captured cannot be back-filled, which is the reason
  `FR-213` pulled the task timestamps into v1 in the first place.
- **Recommendation.** Three edits:
  1. **Enumerate the twenty-nine in `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` §6.22**, as a table under
     `FR-394` with three columns — metric, frozen definition, **fact source** (the ledger column or
     table it reads) — starting from `R6:306`'s list. Any metric whose fact source is blank is either
     placed in a later version with the fact that enables it, or **refused in writing** in §9's
     deliberate-refusals table. On today's schema `perfect_order_rate_pct` and `pick_accuracy_pct` are
     v1.1-or-later at the earliest, and `location_utilization_pct` is `RC-009`.
  2. **Add `whb_metric_definitions`** to `DATA-MODEL.md` as a `D-10` catalogue — `code`, `name`,
     `unit`, `definition_text_key`, `owning_module`, `is_system`, `higher_is_better` — seeded by the
     same migration that seeds the other registries, with `wh_metric_targets`
     (`metric_code`, `warehouse_id`, `owner_id`, `period_grain`, `target_value`, effective dates)
     for `WS-216`'s `target`/`variance`, plus a small admin screen. This also removes a
     `FR-380`/`OD-5` hazard: without a catalogue, `metricCode` becomes a TypeScript string union.
  3. **Bind the definitions to the explainer that already exists.** `FR-393` says *rendered*, and the
     component is live: `platform/frontend/src/components/common/metricInfo/` —
     `MetricInfoModal.tsx`, `MetricInfoTable.tsx`, and `metricText.ts:15`'s `createMetricText(prefix)`
     helper that binds an i18n namespace per metric. `definition_text_key` on the catalogue row is
     what feeds it.

  Folds into **`P2-21`** (the list and the explainer binding) and **`P1-03`** or the registry
  migration band for the two tables; needs `FR-394` amended and one new `FR-` row for the target
  object. A migration is required for the two tables, in `warehouse`'s band — **next free in
  `V510…`**, to be taken from the module's ledger in `DATA-MODEL.md` §8.4 rather than guessed here.

---

### `RC-008` · The auditor's fifth artefact — immutability evidence — is promised in v1 and has no screen, no report, no export and no action; the only chain verifier in the set runs over the wrong table — **MAJOR**

- **What I found.** `FR-427` says the ledger *is* the audit trail and that *"the five artefacts an
  auditor asks for are shipped: the ledger as at a date and reproducible, a movement-level audit
  export for a period, the adjustment analysis, the count history with variance, and **immutability
  evidence**"* — `base·app`, **v1**, `P0`. `WH-SC-245` has the auditor open all six reads. Four of
  the five artefacts have a screen: `WS-224`, `WS-209` (line-grain export), `WS-213`, `WS-214`. The
  fifth has nothing. `FR-427` is owned by exactly one task, `P0-13`, and `P0-13` builds its hash chain
  and *"a verifier that names the break"* over **`whb_audit_events`** — warehouse's master-data and
  configuration audit — not over `whb_stock_movements`. The ledger's own chain does exist:
  `WH-SC-033` asserts `sequence_no` gapless per warehouse with each row's `prev_payload_hash` chaining
  to its predecessor. Its output surface is one line of one detail panel — `WS-041`'s header shows
  `payload_hash`, `prev_payload_hash` and `idempotency_key` for a single movement
  (`BUILD-SPEC-SCREENS.md:1307`) — with no verify action, no period-scoped verification, no report and
  no export. `WS-040`'s export carries neither hash column. The word *immutability* appears nowhere in
  `BUILD-SPEC-SCREENS.md`, `p2-20` or `p2-21`. `COMPETITOR-BENCHMARK.md:467` compounds it by placing
  the five artefacts at **v1.1** while `FR-427` places them at v1 — the two documents disagree and
  neither notices.
- **Evidence.**
  ```bash
  grep -rn -i "immutab" docs/BUILD-SPEC-SCREENS.md issues/p2-20.md issues/p2-21.md
  # → BUILD-SPEC-SCREENS.md:382,386 only — a meta-count of the word "immutable" in field specs
  grep -rln "FR-427" issues/                                        # → issues/p0-13.md   (one task)
  grep -n -i "prev_payload_hash" docs/BUILD-SPEC-SCREENS.md         # → 1307  (WS-041 header panel)
  ```
  - `docs/WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md:747` — `FR-427`, five artefacts, v1.
  - `issues/p0-13.md:33-36` — the chain and the verifier, scoped to `whb_audit_events`.
  - `docs/DATA-MODEL.md:918` — `whb_audit_events`, a **different table** from the ledger.
  - `docs/SCENARIO-CATALOGUE.md:193` (`WH-SC-033`) — the ledger's own chain, asserted and unsurfaced.
  - `docs/SCENARIO-CATALOGUE.md:492` (`WH-SC-245`) — the auditor opens the immutability evidence.
  - `docs/COMPETITOR-BENCHMARK.md:467` — the same five artefacts at v1.1.
- **Why it matters.** *"The ledger is the audit trail"* is the claim on which `FR-427` declines to use
  the platform activity log, and immutability evidence is the only one of the five artefacts that
  substantiates it. Without a verification surface, an auditor is asked to take append-only on trust —
  and the product has already paid for the mechanism that would prove it. There is a second, quieter
  consequence: an unverified chain is an unmonitored chain. `WS-223`'s health signals include negative
  positions, orphaned reservations and dead outbox deliveries, and do **not** include *the ledger
  chain does not verify*, which is the single strongest integrity signal the schema is capable of
  emitting.
- **Cost if found late.** The data is captured, so this is recoverable — but it is discovered in an
  audit, which is the worst room to discover it in, and `FR-427`'s own logic applies: the artefact is
  requested for a period that has already closed.
- **Recommendation.** Small and concrete:
  1. **A `Verify chain` action on `WS-040`**, permission `whb_stock_movements:verify`, scoped by
     warehouse × date range, returning verified / broken and naming the two `sequence_no` values
     either side of a break — the same output `P0-13`'s verifier already produces for
     `whb_audit_events`, pointed at `whb_stock_movements`.
  2. **An exportable evidence artefact**: the verification result, the range, the row count, the head
     and tail hashes and the run timestamp — the thing an auditor takes away. Add `payloadHash` and
     `prevPayloadHash` to `WS-040`'s **export** columns (they are already on `WS-041`'s panel, so no
     new fact is exposed).
  3. **A `LEDGER_CHAIN_BROKEN` signal on `WS-223`**, run nightly beside `L-4`'s rebuild — the two are
     the same job's natural pair.
  4. Reconcile the version: `COMPETITOR-BENCHMARK.md:467` says v1.1, `FR-427` says v1. `FR-427` wins;
     amend the benchmark row rather than leaving two answers standing.

  Folds into **`P0-13`** (which owns `FR-427`) with the surface half in **`P2-20`**, and one signal in
  **`P3-17`**/`WS-223`. No migration — the columns exist from `V500030`.

---

### `RC-009` · Space and location utilisation is unreportable in every version, although the capacity columns are v1, the hierarchy's stated justification is utilisation, and 3PL storage bills by the pallet — **MINOR**

- **What I found.** `whb_locations` carries a full capacity block from v1 — `max_weight_kg`,
  `max_volume_cc`, `max_units`, `max_lpns`, `height_cm`/`width_cm`/`depth_cm` — and
  `BUILD-SPEC-SCREENS.md:419` freezes it *"once stock is on hand"* because *"lowering capacity below
  current contents … has no defined outcome otherwise"*, so the columns are enforced, not decorative.
  `FR-082`'s justification for building the location hierarchy at all is, in its own words, that four
  flat VARCHARs *"cannot answer 'count zone A', 'block aisle 12', **'utilisation of rack B-04'**"*.
  Nothing reads them. There is no utilisation report among the 20, no utilisation widget among the
  10, no `FR-` requiring one, no P6 task carrying one, and no row in §9's deliberate-refusals table
  declining one. The version ladder's v3 line mentions *"control-tower analytics"* and the P6 task
  files cover archiving, stocking levels, labour, automation, receipt facts, 3PL v3, logistics, the
  dealer test, the dashboard, accessories and BOM — none of them occupancy. Meanwhile the live
  `accessories` module, whose eleven reports `D-9` counts as a duplication cost, already ships one.
- **Evidence.**
  ```bash
  grep -rn -i "utilisation\|utilization\|occupancy" docs/BUILD-SPEC-SCREENS.md issues/p6-*.md \
    | grep -vi "bond"                                     # → capacity-block field notes + p6-09 prior-art aside only
  ls accessories/frontend/src/app/accessories/reports/     # → 11 report pages, incl. warehouse-utilization
  grep -n "gridIdentifier: 'accessory_report_warehouse_utilization'" \
    accessories/frontend/src/app/accessories/reports/warehouse-utilization/page.tsx   # → 84, 102, 143
  ```
  - `docs/DATA-MODEL.md:451` — the capacity block, v1.
  - `docs/WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md:222` — `FR-082`, *"utilisation of rack B-04"*.
  - `docs/BUILD-SPEC-SCREENS.md:1824` — `WS-161`, 3PL storage billing on a `PALLET`/`SQFT`/`CBM`
    basis, reading `whb_stock_position_snapshots` and *"never recomputing occupancy"*.
  - `docs/COEXISTENCE.md:74` — the accessories report list, including `warehouse-utilization`.
- **Why it matters.** It is a manager's number and a salesperson's demo, and it is the one the
  incumbent already has. It also has a commercial edge in v2: `WS-161` bills a 3PL client by the
  pallet position, and no screen tells the operator how many pallet positions the building has or how
  many are occupied — so a rate is negotiated against a capacity nobody can display. This is a MINOR
  rather than a MAJOR because no v1 requirement, screen or task depends on it and `D-12` is satisfied
  by placing it, not by building it — but `D-12`'s rule is precisely that *"every capability found by
  any lens is placed in a version and carried in a task file now"*, and this one is placed nowhere.
- **Cost if found late.** Low and additive — the facts are all captured from v1, which is why this is
  a placement question and not a schema one. The only real cost is a competitive one on a demo against
  an incumbent, and the risk of it being invented ad hoc as a hand-rolled page.
- **Recommendation.** Place it, do not build it in v1. Add one requirement to §6.22 — *"a location
  utilisation report: occupied against capacity by weight, volume, units and LPNs, rolled up the
  location hierarchy to rack, aisle, zone and site, from `whb_locations`' capacity block and
  `whb_stock_positions`; the analysis, never an optimiser"* — at **v3 · P6**, alongside the
  slotting *analysis* that §9's refusal row 7 already declares *"is **v3 and not refused**"*. Carry
  it on **`P6-02`**, which already owns `FR-070`'s ABC/velocity recompute and is the natural home for
  velocity × cube. Add the screen to `BUILD-SPEC-SCREENS.md` §1 as **`WS-238`**, the next free id.
  If the answer is instead *never*, it belongs in §9's refusals table with a reason — silence is the
  only outcome `D-12` forbids.

---

## §3 · What I checked and found sound

Recorded with ids so round 4 does not re-walk this ground.

### A · The report inventory itself

| What I checked | Found | Where |
|---|---|---|
| Are the reports real grids or special-cased screens? | **Real grids, deliberately** — `gridIdentifier`, `grid_column_definitions`, `filter_definitions`, a `grid_preferences` row and a `COMMON_FILTER_CONFIGS` scope each, with the three differences (ledger-style so no audit columns; filter-aware uncached strips; parameters are filter rows too) stated up front | `BUILD-SPEC-SCREENS.md:1964-1980` |
| Does every §6.22 requirement have a screen? | **Yes, all 17.** `FR-384`→`WS-208` … `FR-400`→§7 preamble. No orphan requirement and no orphan screen | §7 table vs `FRD` §6.22 |
| Is the filter table named correctly? | **Yes** — `filter_definitions`, with the explicit warning that `grid_filter_definitions` does not exist and *"crash-loops the backend"*, verified against `V229:8` | `BUILD-SPEC-SCREENS.md` §9.1 |
| Numeric-range parameters (`valueImpactMin/Max`, `mrpFrom/mrpTo`) | **Supported** — `FilterFieldType` includes `number` and `convertFiltersForApi` converts it (`filterUtils.ts:30,203-208`). No gap |
| The `date` vs `dateOnly` split | **Correct and unusually careful.** `p2-20` states it per parameter and cites the reason: `date` *"moves the 'from' bound to the previous calendar day for users east of UTC"* — `filterUtils.ts:49-56` says exactly that | `issues/p2-20.md:71-76` |
| Export parity | **Right, including the exception.** Ledger-style grids carry no `createdByName`/`updatedByName` and therefore none in the export; `ExportServiceContractTest.WITHOUT_AUDIT_COLUMNS` is named as a ratchet that may shrink and never grow. `PP-6`/`FR-400` own the 100,000-row streaming path with the `BaseExportService.DEFAULT_MAX_EXPORT_ROWS = 10_000` trap called out | §7 preamble, `p2-20` traps |
| Statistics caching | **Right, and rare.** `FR-395` forbids a cache name on filter-aware strips and cites the live registry mistake with its issue numbers | `FR-395`, `C-043` |

### B · The as-at problem, where the set is right

| What I checked | Found | Where |
|---|---|---|
| Is as-at computed from balances or from movements? | **From movements, stated three times and made an acceptance box**: *"stock as at a back date computed from movements, **never from balances**"*; snapshots are *"explicitly a cache"* | `FR-328`, `IMPLEMENTATION-PLAN.md:476`, `p2-20:23-25` |
| Does a back-dated post change a past as-at answer? | **Yes, by design, and it is written down** — `PC-25` and `WH-SC-040`: the November run legitimately differs from the October run by exactly the entries posted since, and the response carries the `sequence_no` it was computed at so a consumer that cached the earlier figure can tell why | `PC-25`, `WH-SC-040` |
| Do the reports prove themselves against a rebuild? | **Yes, and the reasoning is exactly right**: *"three reports that agree with each other are not evidence, because they could all read the same broken cache. Agreeing with a rebuild from the movements is"* | `WH-SC-061` |
| Ageing measured from what? | **Last outward movement**, not receipt — *"a lot received two years ago that shipped last week is not aged stock"* | `FR-388`, `FR-162`, `WH-SC-286` |
| Does the set know the snapshot's start date is irreversible? | **Yes** — `PNR-3`/`IRR-51`: ageing, days-on-hand, obsolescence and 3PL anniversary billing *"all begin on the day the job was switched on"*, marked on the table row, the migration ledger and the screen | `IRREVERSIBLE.md:234`, `DATA-MODEL.md:2916` |

### C · KPIs

| What I checked | Found | Where |
|---|---|---|
| Are KPIs computed from status columns and `updated_at`? | **No, and the refusal is the requirement.** `FR-392`: *"Not one of them can be computed from a status column and an updated-at, because updated-at is overwritten by the next status change"* — and the timestamps were pulled into v1/P0 for it (`FR-213`) | `FR-392`, `FR-213` |
| Are the ambiguous KPIs frozen? | **Four of them, to the denominator**, with fill rate's lost-sale denominator sourced from `wh_insufficient_stock_log.is_lost_sale` and an acceptance box that *"changes the answer"* | `FR-393`, `p2-21` |
| Is there a metric explainer to render them in? | **Yes, live** — `platform/frontend/src/components/common/metricInfo/` (`MetricInfoModal.tsx`, `MetricInfoTable.tsx`, `metricText.ts:15`). `FR-393`'s *rendered, not documented* is buildable today |
| Pre-aggregation | **Refused until measured**, with the live precedent named: *"the repo's own best precedent is a derived-at-read-time model that deliberately does not cache"*; `wh_kpi_snapshots` is v1.1 and `p2-21` forbids this task from creating it | `FR-394`, `C-033` |
| Engineered labour standards | **Refused, in writing, with the condition for re-entry** — measure actuals, never compute incentive pay from a warehouse metric | `FR-228` |

### D · Owner scope, dashboards and mobile

| What I checked | Found | Where |
|---|---|---|
| Is owner scope a `WHERE` clause or a UI filter? | **A record-level guard**, with a contract test failing the build if an owner-scoped repository method takes no owner-set parameter, and the explicit note that *"each grid identifier has an export path and a statistics map, and every one of them is a leak site"* | `FR-406`, `FR-404`, `F-004` |
| Are the widgets buildable on the platform framework? | **Not today, and the set knows exactly why and exactly how to fix it.** `widget_definitions.chk_module` admits neither `warehouse` nor `logistics` — verified at `V557__Extend_widget_definitions_module_constraint.sql:16-18` — and `WHB-70`/`V500200` widens it by **reading and unioning** the existing definition rather than restating a hardcoded list, which is how `V557` erased `V276`'s additions. `'logistics'` is added in the same migration because retro-granting a v3 value is hand work | `C-014`, `FR-377`, `FR-378` |
| Are widgets scoped? | **Yes** — every widget is scoped by the three-mode view pattern **and** by owner grants, with the note that *"a widget that ignores the record-level guard leaks across branches and owners exactly where nobody is looking"*, and empty states name the provider reason | `BUILD-SPEC-SCREENS.md` §8.2 |
| Mobile for the report pack | **Decided, not silent.** Two mobile reports (`whStockOnHandReport`, `whExpiryReport`) with the reason — *an operator asks "what have I got" and "what is about to expire"* — and **`none` stated for every other report** with the constraint named (`ListHeader` has no date parameter). `D-13`/`FR-218` satisfied | `BUILD-SPEC-SCREENS.md:2003-2007` |
| Statutory registers | **Present and correctly versioned** — the Rule 56 stock account (`FR-314`), stock by MRP (`WS-226`), EPR (`WS-189`) and the tax-audit quantitative statement (`FR-329`) at v2/P4, with the v1 India wave limited to the documents that let goods move legally (`A-4`) | `FRD` §6.20, `DECISIONS.md` §5.1 |

---

## §4 · Refused

Candidate findings I deliberately did **not** file, and the id that owns each.

| Candidate | Why refused |
|---|---|
| *"The as-at reports depend on an unresolved partition key"* | **`X-024` / `OD-12`**, the set's own loudest gate, carried in five places. `RC-001` is deliberately **independent of which column wins the partition**: it asks which column each *report* compares its parameter to, which is a different question and stays open whichever way `OD-12` is decided |
| *"Dock-to-stock cannot be computed because nothing writes `arrived_at` in v1"* | **`U-004`** (R10), filed last round with the same evidence I would have used. My §1.1 table records it as owned rather than re-filing it |
| *"Cost and value are visible to anyone who can open the report"* | **`K-002`** (R13) and its resulting `FR-450`, which covers every endpoint returning `unit_cost`, `total_value`, `standard_cost` or a cost layer, exports included. `RC-006` is the **owner** axis, which `FR-450` explicitly says it does not cover — I have kept them disjoint and said so in the finding |
| *"There is no per-install health surface"* | **`S-093`** → `FR-398`/`WS-223`. `RC-008`'s recommendation adds **one signal** to that existing screen rather than proposing another |
| *"The eight performance targets have no measurement method"* | **`K-003`** (R13). My reports inherit those targets and add nothing to the argument |
| *"Queue and consumer signals are failure-shaped, never lag-shaped"* | **`K-005`** (R13) |
| *"Low-stock and replenishment reports are specified as *schedulable* with no scheduling substrate in v1"* (`issues/p2-21.md` acceptance) | **`U-002`** owns the absent alert-rule / recipient / event substrate, and `FR-284` places scheduled report delivery in the v2 client portal. The word *schedulable* in that acceptance box should be struck when `U-002` is dispositioned; that is an edit to `U-002`'s remediation, not a new finding |
| *"Ageing, obsolescence and turns all start on the day the snapshot job was switched on"* | **`PNR-3` / `IRR-51`**, marked on the table row, the migration ledger, `WS-044` and `WS-161`. The set flags it more loudly than I would have |
| *"A 100,000-row export holds a transaction open and `DEFAULT_MAX_EXPORT_ROWS` is 10,000"* | **`PP-6` / `FR-400`**, with the streaming path assigned to `warehouse-base` (not platform) and an explicit *"do not edit `BaseExportService` to raise the row cap"* trap |
| *"Warehouse widgets cannot be inserted because of `chk_module`"* | **`C-014`** → `FR-377`/`FR-378`/`WHB-70`, including the read-and-union rule that stops the next module erasing ours |
| *"The stock-to-GL report cannot classify a write-off, shrinkage or a customer-owned adjustment to the right account"* | **`O-002`** (R14). `RC-002` is a different defect on the same screen — that report has no way to read *any* account balance — and fixing `O-002` does not fix it. Stated in the finding so the two are not merged |
| *"Filter fields will be silently dropped by `COMMON_FILTER_CONFIGS`"* | **`FR-432`** / `C-042`, with the honest note that this will be the largest single addition to that allowlist the codebase has seen |
| *"ABC / velocity classes are stored and never consumed"* | Not true: the cycle-count programme scopes by ABC class in v1 (`WH-SC-268`) and the recompute job is `FR-070` → **`P6-02`**, traced in `IMPLEMENTATION-PLAN.md:1417` |
| *"There is no consolidated report across warehouse and accessories"* | **`D-9`** costs it in writing and `OD-15` asks the question directly; `FR-397`/`WS-222` and `FR-369`/`WS-225` already ship the two honest halves. Nothing to add |
| A saved-report / report-subscription / ad-hoc query builder | **Over-engineering for v1**, and against the grain of a design whose reports are real grids with saved grid preferences and a filter strip — which *is* the saved-report mechanism this platform has. `FR-284` puts scheduled delivery in the v2 portal, which is the right place for it |
| A separate data-warehouse / OLAP projection for analytics | **Over-engineering, and explicitly pre-refused** by `FR-394`'s measure-first rule and `C-033`'s derived-at-read-time precedent. Filing it would contradict a decision the set took deliberately |

---

## §5 · Counts

```bash
cd /Users/bbhushan/work/git/workspace/warehouse-issues
grep -c "^### \`RC-" docs/reviews/R18-reporting-and-analytics-completeness.md                  # → 9
grep -o "\*\*BLOCKER\*\*$" docs/reviews/R18-reporting-and-analytics-completeness.md | wc -l    # → 2
grep -o "\*\*MAJOR\*\*$"   docs/reviews/R18-reporting-and-analytics-completeness.md | wc -l    # → 6
grep -o "\*\*MINOR\*\*$"   docs/reviews/R18-reporting-and-analytics-completeness.md | wc -l    # → 1
```

| Severity | Count | Findings |
|---|---|---|
| **BLOCKER** | **2** | `RC-001` `RC-002` |
| **MAJOR** | **6** | `RC-003` `RC-004` `RC-005` `RC-006` `RC-007` `RC-008` |
| **MINOR** | **1** | `RC-009` |
| **Total** | **9** | |

**By disposition** — eight fold into existing tasks; one needs a version placement and a screen id:

| Finding | Folds into | Documents amended | Migration | Irreversible? |
|---|---|---|---|---|
| `RC-001` | `P2-20` · `P2-18` · `P2-21` | `BUILD-SPEC-SCREENS.md` §7 (new **Clock** column) · `SCENARIO-CATALOGUE.md` (`WH-SC-060` + one new `edge`) | none | **no** — but the answers it produces are quoted to third parties, so it is *practically* irreversible after go-live |
| `RC-002` | `P2-18` | `FR-247` · `WS-219` · `PORT-AND-ADAPTER-CONTRACT.md` §4 · `MODULE-INTEGRATION.md` | none | no |
| `RC-003` | `P2-20` | `FR-387` · `WS-211` · `WS-222` | none | no |
| `RC-004` | `P2-29` (strips) · `P2-20` (footer wording) | `BUILD-SPEC-SCREENS.md` §7 (new **Statistics strip** column) · one new `PLATFORM-DEPENDENCIES.md` `PP-` row | none | no |
| `RC-005` | `P2-29`, with acceptance in `P2-20` / `P2-21` | `BUILD-SPEC-SCREENS.md` §7 preamble | none — `filter_definitions.is_required` already exists | no |
| `RC-006` | `P2-20` · `P2-21` | `BUILD-SPEC-SCREENS.md` §7 preamble · `WS-210` · one new scenario | none | no |
| `RC-007` | `P2-21`; the two tables on the registry band | `FR-394` (+ one new `FR-` for targets) · `DATA-MODEL.md` §2 and §8.4 | **yes** — two tables, **next free in `V510…`**, taken from `DATA-MODEL.md` §8.4's ledger, not guessed | no |
| `RC-008` | `P0-13` (verifier) · `P2-20` (surface) · `P3-17`/`WS-223` (signal) | `FR-427` · `WS-040` · `COMPETITOR-BENCHMARK.md:467` version row | none | no — the hash columns ship at `V500030` |
| `RC-009` | `P6-02` | one new `FR-` in §6.22 at v3 · `BUILD-SPEC-SCREENS.md` §1 as **`WS-238`** | none in v1 | no |

**One cross-cutting correction** that is not a finding in its own right but must travel with the
above: `COMPETITOR-BENCHMARK.md:467` places *"the auditor's five artefacts"* at **v1.1** while
`FR-427` places them at **v1 · P0** and `WH-SC-245` asserts them as a v1 behaviour. `DECISIONS.md`'s
precedence rule makes the FRD's version the answer; the benchmark row is stale and must be amended
rather than left standing, because a reader who finds the benchmark first will schedule the work a
release late — which is exactly how `RC-008`'s artefact came to have no surface.
