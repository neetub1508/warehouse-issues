# R13 — Non-functional: scale, concurrency, observability, security, resilience and operability

> **Date** 2026-09-02 · **Branch** `docs/round-2-functional-review` · **Finding prefix** `K-`
> (`grep -rohE "\bK-[0-9]{1,3}\b" docs/ issues/ | wc -l` → **0**, so the namespace was free)
>
> **File set.** The design set is 176 markdown files / 52,713 lines
> (`find docs issues -name '*.md' | wc -l` → `176`; `cat $(find docs issues -name '*.md') | wc -l`
> → `52713`). I read whole: all 16 `docs/*.md`; `docs/reviews/R8`, `R9`, `R10`, `R11` (headings and
> the finding blocks that touch my inventory); and `issues/p0-02`, `p0-03`, `p0-08`, `p0-11`,
> `p0-13`, `p0-16`, `p0-17`, `p3-01`, `p3-02`, `p3-03`, `p3-04`, `p5-08`, `p6-01`,
> `01-EPIC-p0`, `05-EPIC-p3`. The remaining 133 task files were searched by grep, not read; every
> negative-evidence command below was run across **all** of `docs/` and `issues/`.
>
> On the live side I read `pom.xml`, `platform/backend/pom.xml`,
> `platform/backend/.../V452__create_role_field_configs_table.sql`,
> `platform/backend/.../RoleFieldConfigController.java`, and the whole of
> `accounting-base/backend/src/main/java/ai/accountingbase/service/jobs/` plus
> `V600121__Create_acc_job_runs_and_the_scheduler_run_log.sql`.
>
> **Method, in three sentences.** I took each of the six areas the lens owns — scale, concurrency,
> observability, security, resilience, performance budgets — and, for each, first established what
> the set *already* says, because this design set says a great deal and a finding that restates it is
> worthless. Where the set was sound I recorded it in §3 with its id so round 3 does not re-walk the
> ground. Only where a mechanism was genuinely absent, and where I could name the mechanism that
> should replace the absence, did I file.

---

## §1 · Verdict

This is the strongest non-functional design set I have reviewed in this repository, and it is not
close. Performance targets are stated as numbers (`FR-422`), the five concurrency mechanisms are
named with their precedents counted (`FR-437`), the ledger is partitioned from migration one with
the composite-PK consequence worked through (`DATA-MODEL.md` §1.9), the position cache has a
rebuild, a drift-findings table, a findings grid and an ageing exception console (`L-4`, `WS-043`,
`WS-098`), restore is filed as platform work with a written "unknown" RPO/RTO as the honest fallback
(`FR-429`, `p0-16` §5), offline is decided per screen with v1 declared online-only and the
irreversible half of the mechanism shipped anyway (`p0-16` §4, `IRR-49`), and owner scope is a
`WHERE`-clause guard returning `403`, never a filtered grid (`PC-32`, `P1-18`). Round 1's central
non-functional charge — that the live codebase has no concurrency control on stock anywhere — is
answered in the design, properly, at three layers.

The area is buildable. What it is not yet is **operable**, and the gap has one shape: **the design
specifies what each background job does and never specifies how any of them runs.** Nine dated
obligations ship in v1. `whb_job_runs` records what happened. Nothing anywhere records what was
*supposed* to happen, and no document in the set contains the words *single instance*, *scheduler
lock*, *cadence*, *scheduled_for* or *missed run*. So a second application instance runs the drift
rebuild twice against the same company, and — far worse — a job that stops firing altogether leaves
no evidence at all, because `WS-064`'s only exception filter is `failedOnly` and a run that never
started is not a failed run. The screen's own justification sentence, *"a job with no run record
cannot be proved to have run"* (`BUILD-SPEC-SCREENS.md:1246`), is a promise this schema cannot keep.

**The single most expensive thing missing is not a feature — it is a framework the company already
owns.** `platform/backend/pom.xml:29-41` puts ShedLock on the runtime classpath with a comment
saying it is *"used by warehouse-base schedulers"*, and there is no `shedlock` table in any migration
and no `@SchedulerLock` in any Java file. Meanwhile `accounting-base` shipped, on **2026-09-01 — the
day before this design set's own date** — a complete 23-file, 2,709-line scheduled-job framework with
slot-based cadence, a catch-up planner, an explicit missed-run policy per job, a
`uk_acc_job_runs_single_running` unique index used as the job lock, and a balance-rebuild job with a
drift detector and a drift-alert service carrying a written runbook. That is precisely the shape
`PLATFORM-DEPENDENCIES.md` §4.9 and `issues/p0-03.md` instruct the builder to **budget as
invention** (*"balance-cache-with-rebuild — warehouse invents it. Budget it."*). That instruction is
now false, and following it costs a quarter of engineering and produces a second, divergent job
framework in the same database.

**At what scale, and on what event, does this design first fall over?** Not at a row count. It falls
over on a **Tuesday in month two of the first install, at 03:00**, when the `L-4` rebuild job stops
firing — because the app was redeployed with the schedule disabled, or because two instances
deadlocked on it, or because it silently threw before it could write its own run row. Every position
in the database is thereafter of unknown validity, every valuation and every availability number
reads from a cache nobody is checking, and the only surface that would have told anyone is a grid
filtered on `failedOnly`. The second-order version of the same event is worse and is dated: if the
**monthly partition-creation job** stops firing, every `POST /movements` in the product fails at
00:00 on the first of the month with a raw PostgreSQL "no partition found for row" error, and the
warehouse stops.

**Is the fix a v1 column or a v2 project?** A v1 column, and a small one — `scheduled_for` plus a
partial unique index on `whb_job_runs`, a job-descriptor registry with a declared cadence and
missed-run policy, and one health signal shaped *"expected N runs, saw N−1"*. It is `PNR`-free and
reversible. But it must land in `P0-13`'s `V500043`, because a run-history table that shipped without
`scheduled_for` cannot answer the question retroactively for the months it was live.

---

## §2 · The findings

### `K-001` · No job in the product has an execution contract: nothing declares when a job should run, nothing stops two instances running it, and a job that never fires is invisible on every surface — **BLOCKER**

- **What is missing or wrong:** `P0-13` specifies `whb_job_runs` as *"one row per scheduled-job
  execution"* with `job_code`, `started_at`, `finished_at`, `status`, `records_read`,
  `records_written`, `error_detail`, `duration_seconds`. That is a **log**. Three things a scheduled
  job needs are absent from the design set entirely:
  1. **A declared cadence and an expected-run row.** There is no `scheduled_for`, no job registry, no
     descriptor. Without it, "did the 03:00 drift rebuild run last night?" is not a query — it is an
     eyeball over a grid, per job, per company, per night.
  2. **A single-instance guarantee.** Nothing states that only one instance may run a job. Two app
     replicas both fire `L-4`'s rebuild against the same company and both write positions; two fire
     the reservation-expiry job and both post status changes; two drain the outbox and both advance
     `whb_outbox_subscriptions.last_delivered_cursor`.
  3. **A missed-run semantic.** For each of the nine v1 obligations, when the process was down over a
     slot, does the job replay that slot dated as it was, do the work once for today, or skip and
     report? The three answers are materially different for *reservation expiry* (dated), *position
     snapshot* (dated — `WHB-45` is `PNR-3` precisely because a missed snapshot day is
     unreconstructable), and *drift rebuild* (today). The set does not choose for any of them.

  The nine v1 dated obligations this covers are listed by `P0-13` itself: reservation expiry,
  position snapshot, position drift rebuild, outbox publisher, port rejected-queue alert, monthly
  partition creation, lot expiry, cycle-count scheduling, and the threshold/alert job. Two of them
  are load-bearing beyond their own feature: **the drift rebuild is the only control that makes the
  position cache safe to read**, and **monthly partition creation is the only thing that keeps
  `POST /movements` working across a month boundary** (`p0-02` acceptance:188 — *"a movement dated
  into an unmade partition fails loudly"*).

  `WS-064`'s only exception filter is `failedOnly` (`BUILD-SPEC-SCREENS.md:1246`) and `WS-223 Install
  Health Signals`' seven signals include *"failed jobs"* and nothing shaped *"absent jobs"*
  (`:1791`). A job that never started is neither.

- **Why it matters:** Two moments, both concrete.

  **03:00, some Tuesday in month two.** The rebuild job stops firing — a redeploy with the schedule
  property off, a poison row, an unhandled `LazyInitializationException` before the run row is
  written. `whb_job_runs` gains no row. `WS-064` filtered on `failedOnly` shows nothing. The drift
  findings grid `WS-043`, whose default filter is `unresolvedOnly`, shows nothing, because a rebuild
  that did not run finds no drift. Every number on the valuation report, the availability check, the
  as-at report and the 3PL custody report is read from a cache that has not been checked since
  Monday, and **it all looks right.** This is the exact failure mode `AccBalanceDriftAlertService`'s
  javadoc calls *"the most important alert in the product"* — *"If it drifts and nobody is told,
  every one of those reports is wrong and looks right."*

  **00:00 on the first of the month.** Partition creation has not run for two months. The first
  `POST /movements` of the new month raises `no partition of relation "whb_stock_movements" found for
  row`. Receiving stops, picking stops, the port stops, every adapter stops. Recovery is a DBA
  writing `CREATE TABLE ... PARTITION OF` by hand at midnight, and the diagnosis is not obvious
  because the error surfaces as a 500 on an unrelated screen.

  **And the duplicate-execution case is not hypothetical in this deployment model.** The moment the
  install runs two replicas — which is the first thing anyone does for availability — the reservation
  expiry job posts every expiry twice.

- **Negative evidence:**

  ```bash
  cd /Users/bbhushan/work/git/workspace/warehouse-issues
  grep -rniE "shedlock|scheduler lock|single.instance|leader elect|distributed lock|scheduled_for|missed run|missed-run|catch.up planner|job cadence" docs/ issues/
  #  → only two irrelevant hits: "Multiple sites / warehouses in one instance"
  #    (COMPETITOR-BENCHMARK.md:214) and "release cadence" (COMPETITOR-BENCHMARK.md:1036).
  #    Zero hits for shedlock, scheduled_for, single-instance, leader election or missed-run.

  grep -rn "cadence" docs/ issues/ | grep -vi "release cadence" | wc -l      # → 0
  ```

  ```bash
  cd /Users/bbhushan/work/git/workspace/classic
  grep -n "shedlock" pom.xml platform/backend/pom.xml
  #  pom.xml:34   <shedlock.version>5.10.0</shedlock.version>
  #  pom.xml:343-350  shedlock-spring + shedlock-provider-jdbc-template in dependencyManagement
  #  platform/backend/pom.xml:35-41  both artifacts declared as runtime deps

  grep -rn "shedlock" --include=*.sql . | wc -l                 # → 0   (no lock table exists)
  grep -rn "shedlock\|SchedulerLock" --include=*.java . | wc -l # → 0   (nothing uses it)
  grep -rln "@Scheduled" --include=*.java . | wc -l             # → 30  (30 files schedule work)
  ```

  `platform/backend/pom.xml:29-34` carries the comment verbatim:
  *"ShedLock for distributed scheduler locking (used by **warehouse-base schedulers**). MUST be
  declared here: platform-backend is the ONLY module repackaged into the runnable fat app.jar…"* —
  someone has already reasoned about warehouse's scheduler locking and put the library on the
  classpath. The design set does not know.

- **The mechanism I want, named.** Do not invent it — **port `accounting-base`'s**, which is live and
  was committed on 2026-09-01 (`git log`: `812b310dad`, `a31405c85c`):

  | Piece | File in `accounting-base` | What warehouse needs it for |
  |---|---|---|
  | Slot-sequence cadence, not cron | `service/jobs/AccJobCadence.java` — *"A cron expression can say when the next fire is; it cannot enumerate the fires that did not happen. The catch-up planner needs the enumeration."* `nextSlot` / `previousSlot` / `slotsBetween` | Turns "did it run?" into arithmetic |
  | Per-job missed-run policy, **no default** | `service/jobs/AccJobMissedRunPolicy.java` — `RUN_MISSED_DATED_AS_SCHEDULED` / `RUN_MISSED_DATED_TODAY` / `SKIP_AND_REPORT`, and *"a job that does not declare one cannot be constructed"* | Snapshot = dated-as-scheduled; drift rebuild = dated-today; retry-shaped jobs = skip-and-report |
  | The job **lock** with no new infrastructure | `V600121__…:224` `CREATE UNIQUE INDEX … uk_acc_job_runs_single_running`, and `AccJobRunRecorder.java:63-79`: *"`uk_acc_job_runs_single_running` is the job lock - there is no ShedLock in this repository - so a second instance trying to start the same job for the same company gets a unique violation. That violation is deliberately NOT caught here"* | Single-instance execution for **zero** added dependencies |
  | The failure row that survives the failure | `AccJobRunRecorder.java:22-38` — `@Transactional(propagation = REQUIRES_NEW)`, because *"The run row would then roll back with the work it was recording, and a failed job would leave no evidence that it ever ran."* | Without this, `whb_job_runs` is empty in exactly the case it exists for |
  | `scheduled_for` and the catch-up planner | `V600121__…:71,75,156,231` — `scheduled_for TIMESTAMPTZ NOT NULL`, `CHECK (triggered_by IN ('SCHEDULE','MANUAL','CATCH_UP'))`, and an index on `(scheduled_for)` for the planner | The column that makes "expected but absent" queryable |
  | Bounded catch-up | `AccJobCatchUpPlanner.java` + `getCatchUpMaxSlots()` — beyond the bound, **one** `SKIPPED` row naming the count | Stops "missed 40 runs → 40 catch-ups on restart" |

  Warehouse needs one thing accounting does not: `AccJobRunRecorder` locks per `(job, company)`.
  Warehouse's snapshot, drift and partition jobs are per **company × warehouse**, so the single-running
  index must carry `warehouse_id` — and that is a column decision, which is why it belongs in
  `V500043` and not in a later release.

- **Where it belongs:** `warehouse-base` · **v1** · **P0**
- **Disposition:** ***Fold into `P0-13`***, whose `V500043` already creates `whb_job_runs`. Add to
  its Scope:
  > **The job registry and the execution contract.** `whb_job_runs` gains `scheduled_for TIMESTAMPTZ
  > NOT NULL`, `triggered_by VARCHAR(20) NOT NULL CHECK (triggered_by IN
  > ('SCHEDULE','MANUAL','CATCH_UP'))`, and `CREATE UNIQUE INDEX uk_whb_job_runs_single_running ON
  > whb_job_runs (job_code, company_id, warehouse_id) WHERE status = 'RUNNING'` — the index **is** the
  > job lock; there is no ShedLock table in this repository despite the dependency being declared at
  > `platform/backend/pom.xml:35-41`. Each of the nine v1 jobs declares a **cadence** and a
  > **missed-run policy** with no default, ported from
  > `accounting-base/…/service/jobs/{AccJobCadence,AccJobMissedRunPolicy,AccJobCatchUpPlanner,AccJobRunRecorder}.java`
  > rather than reinvented. The run row is written `REQUIRES_NEW` so a failure row survives the
  > failure. `WS-064` gains a `notRunSince` filter and an **Expected vs actual** column; `WS-223`
  > gains a `JOB_DID_NOT_RUN` signal alongside `failed jobs`.
  Also amend **`p0-03.md`** and **`PLATFORM-DEPENDENCIES.md` §4.9**: see the note in `K-004`'s
  disposition — the "warehouse invents it, budget it" instruction is now false for the
  rebuild-plus-drift-alert half, and following it buys a second job framework in the same database.
- **Irreversibility:** `scheduled_for` is `NOT NULL` on a table that is **not** the append-only
  ledger, so it is backfillable in principle — but only with a fabricated value, which makes every
  pre-existing row's "did it run on time" answer a lie. **Land it in `V500043` (`P0-13`).** Not a
  `PNR`; the ledger is untouched.
- **Relationship to round 1:** **new.** `FR-165` requires that every dated obligation ships with its
  job and that the job appears on `WS-064`; `S-084`/`FR-422` set performance targets; neither states
  how a job runs, and no round-1 finding, no `X-` defect, and none of `Q-`/`H-`/`U-`/`Y-` touches
  scheduler execution. `U-002` (no v1 alerting substrate) is adjacent and **not** restated here: this
  finding is about the *signal not existing*, not about the delivery channel not existing.

---

### `K-002` · Cost and value are visible to anyone who can open the screen: the only suppression rule in the set is `L-14`'s owner-type rule, and there is no actor-side gate anywhere — **MAJOR**

- **What is missing or wrong:** Every cost suppression in the design set is a property of the
  **stock**, never of the **user**. `BUILD-SPEC-SCREENS.md:1139` is the whole of the rule:

  > `unitCost` / `value` | Cost / Value | number | Y | N | joined from `whb_cost_layers`;
  > **suppressed where `owner_type != OWN`** — non-own stock is never valued (`L-14`, `FR-112`)

  That is bailment, correctly enforced. It says nothing about *who is looking*. The v1 screens that
  render acquisition cost, and the roles that reach them:

  | Screen | Version | Cost fields | Who opens it |
  |---|---|---|---|
  | `WS-043` Stock Positions | v1 · P2 | `unitCost`, `value` | anyone with positions `:view` — every storekeeper |
  | **`WS-095` Count Entry & Variance** | **v1 · P2** | **`unitCost`, `varianceValue`** | **the counter, including on `WS-235 RF Count`** |
  | `WS-049` Cost Layers | v1 | `unitCost`, `layerValue`, `exchangeRate` | anyone with cost-layer `:view` |
  | `WS-209` Stock Movement Register | v1 | `unitCost`, `extendedCost` | anyone with register `:view` — and it exports |

  `WS-095` is the sharp one. A cycle count is the job you hand to a temp, a new starter or a
  contractor, and this design hands them a line-by-line list of what the company paid for every SKU
  they touch, on a handheld, with export available one screen up. The set clearly understands
  field-level suppression on this exact screen — `countSnapshotQuantity` is *"hidden when `is_blind`"*
  — so the machinery is conceptually present and pointed at the wrong column.

  There is exactly one cost-scoped permission in the whole set, `wh_rpt_consolidated_valuation:view`
  (`issues/p3-17.md:35`), and it gates a *report*, not the cost columns embedded in operational grids.

- **Why it matters:** The person who tells you about this is not an auditor — it is a customer's
  purchasing manager, in week three of UAT, when a storekeeper mentions a supplier's price in front
  of that supplier's rep. In the 3PL configuration it is worse than embarrassing: `owner_type != OWN`
  is suppressed, so a 3PL's own-stock cost is what leaks, to floor staff who are frequently agency
  labour. And it is not fixable by hiding the grid column afterwards, because **the value is in the
  JSON payload either way** — the column chooser and `grid_column_definitions` decide rendering, not
  transmission.

- **Negative evidence:**

  ```bash
  cd /Users/bbhushan/work/git/workspace/warehouse-issues
  grep -rniE "cost:view|costs:view|cost visib|see cost|hide cost|role_field_config|field-level permission|column-level permission" docs/ issues/
  #  → 1 hit, and it is not this: issues/p3-17.md:35  `wh_rpt_consolidated_valuation:view` `:export`
  #    Zero hits for role_field_config anywhere in the design set.

  grep -rn "suppressed where" docs/BUILD-SPEC-SCREENS.md
  #  → BUILD-SPEC-SCREENS.md:1139 only — one suppression rule, and it is keyed on owner_type
  ```

- **The mechanism I want, named — and the half of it that does not exist.** The platform **already
  ships** a role-scoped field-configuration table, used in production for exactly this class of
  problem:

  - `platform/backend/src/main/resources/db/migration/V452__create_role_field_configs_table.sql` —
    `role_field_configs (module, page_key, field_key, config_type, config_value, role_id, priority)`,
    header comment: *"Generic, reusable table for role-based field-level configurations. Supports:
    dropdown option restrictions, **field hide/show**, readonly, required, disable… ADMIN role
    bypasses all restrictions."*
  - Live precedents seeding it for money fields:
    `platform/backend/src/main/resources/db/client/{vehicron,ktlautomobiles,pasco}/V910043__*_service_advisor_financial_tab.sql`
    and `…V910053__*_create_cashier_role.sql`.

  **But it is a client-side mechanism today and must not be trusted as a security boundary as-is.**
  `RoleFieldConfigController.java:35-63` exposes `GET /field-configs?module=&pageKey=`, returning a
  `fieldKey → config` map; the consumer is `platform/frontend/src/hooks/useFieldConfigs.ts`. **No
  service anywhere reads it to strip a field from a response** — I grepped: the only Java references
  are the controller, the service, the repository and the entity. So the correct specification is
  two-sided, and the set already has the idiom for the server side: `p0-11` requires that
  `secret_ref` *"is masked at the edge: the response carries `hasValue`, never the value."* Cost needs
  the same treatment — **`unitCost` / `value` omitted from the response DTO** when the caller lacks
  the grant — with `role_field_configs` as the *configuration* surface so a customer can retune it
  per role without a release.

- **Where it belongs:** `warehouse-base` (the response-side guard, alongside `P1-18`'s owner scope) ·
  `warehouse` (the screens) · **v1** · **P1/P2**
- **Disposition:** ***Fold into `P1-18`***, which already owns *"warehouse ∩ branch ∩ owner scope in
  the `WHERE` clause — a menu filter is not a guard"*. Add a fourth scope to its list:
  > **4. Cost scope.** A `warehouse:cost:view` permission seeded in `V501000` alongside the other
  > verb permissions. Where the caller lacks it, `unitCost`, `value`, `extendedCost`, `layerValue`
  > and `varianceValue` are **omitted from the response DTO**, not hidden in the grid — the same
  > edge-masking rule `P0-11` applies to `secret_ref`. `role_field_configs`
  > (`platform/…/V452__create_role_field_configs_table.sql`, `RoleFieldConfigController.java`,
  > `useFieldConfigs.ts`) is the **configuration** surface and is presentation-only today; it is not
  > the guard. Affects `WS-043`, `WS-049`, `WS-095`, `WS-209`, `WS-211`, and `WS-235 RF Count`.
  Needs one `FR-` row first (there is no requirement to hang it on) — file it beside `FR-112`, whose
  scope is the stock's owner, and say plainly that the two are different rules.
- **Irreversibility:** **reversible** as data — but the *permission string* is not: `IRR-63` records
  that a permission invented later must be re-granted by hand to every role on every install.
  **Reserve `warehouse:cost:view` in `V501000` (`WHB-71`) in v1** even if the enforcement lands in P2.
- **Relationship to round 1:** **new.** `S-078`/`F-010`/`L-14` are the bailment rule (the stock's
  owner); `F-004` is the role model; `PC-32`/`FR-114` are owner scope. None of them asks whether the
  *actor* may see cost, and `grep -rn "role_field_config" docs/ issues/` → 0.

---

### `K-003` · Eight performance numbers, zero measurement methods and zero load tests — and `p0-16`'s own acceptance criterion demands the method it does not supply — **MAJOR**

- **What is missing or wrong:** `FR-422` states eight targets: 1M ledger rows/day at peak (20k for a
  dealer parts department), ≤5M live position rows, scan-to-response <300 ms, 200 order lines/s
  allocated with no oversell, a 5,000-line count entered by 10 concurrent counters, a 500-line wave
  in <5 s, and a 100,000-row export that does not hold a transaction open. `p0-16` §1 restates them
  and its acceptance box says:

  > *"The performance targets are written into the repository as testable statements, **each with its
  > measurement method**"*

  No measurement method appears in `p0-16`, in `FR-422`, or anywhere else. **No v1 task builds a load
  harness, and no v1 task carries a load-test acceptance line.** The only load-testing obligation in
  the entire set is `FR-425`'s, for `FOR UPDATE SKIP LOCKED`, discharged in `P3-02` — **v1.1**:
  *"N concurrent claimers against one queue produce zero double-claims under load, and the load test
  is in the PR"* (`p3-02.md:81`). That is the right shape. It exists once, for the one mechanism that
  is not on the v1 critical path.

  `p0-16` also names the hazard itself and then does not close it: *"A performance target with no
  measurement is decoration. Each number here needs a test or a stated measurement method, or it will
  be quoted in a sales conversation and discovered in production."*

  Two further gaps in the number set itself, both cheap:
  - **No concurrency figure for operators.** 200 order lines/s is a throughput; the number that
    decides whether the position-row optimistic lock survives is *how many operators contend on one
    position key*, and nothing states it.
  - **No page-budget for the web grids**, which is where every UAT complaint actually originates
    — `WS-041 Stock Positions` over 5M rows with the nine-member grain and a cascading filter set.

- **Why it matters:** These numbers will be quoted. `FR-422` exists *because* the prior art stated
  nothing, and the set is rightly proud of that. But an unmeasured target is not a weaker target — it
  is a **liability**, because it will be repeated in a sales conversation with the authority of a
  written specification and then discovered, at UAT, on a customer's data, with no baseline to argue
  from and no way to tell whether the regression arrived in P1 or P2. The specific moment: the first
  install with real volume runs the movement register with a two-month date range, the page takes 40
  seconds, and there is no captured number from any earlier build that says whether it was ever
  faster.

- **Negative evidence:**

  ```bash
  cd /Users/bbhushan/work/git/workspace/warehouse-issues
  grep -rniE "load test|load-test|jmeter|gatling|k6|benchmark harness|soak test|measurement method|p95|p99" docs/ issues/
  #  → only FR-425's SKIP LOCKED load test (IMPLEMENTATION-PLAN.md:270,502; 05-EPIC-p3.md:35,51;
  #    p3-01.md:92; p3-02.md:18,60,81) — all v1.1 · P3.
  #    Zero hits for measurement method, p95, p99, or any harness name.

  grep -rn "load-test\|load test" issues/p0-*.md | wc -l        # → 0   (no P0 task load-tests anything)
  ```

- **The mechanism I want, named:** A **seeded-volume performance fixture** and a per-number
  measurement statement, in `warehouse-base`, built once in P0 and reused. Concretely: a seed
  generator that produces N months of ledger at the `FR-422` daily rate for one company × two
  warehouses; a `@Tag("perf")` test class excluded from the default build; and for each of the eight
  numbers, a one-line statement of *what is measured, where, with what data*. Three of the eight are
  already testable as plain integration tests with no harness at all — 200 lines/s with no oversell
  is `p0-03`'s "two concurrent issues of the last unit" scaled up; the 10-concurrent-counter case is a
  `wh_counts` test; the 100k export is a stream test asserting the transaction is not held. The other
  five need the fixture.

- **Where it belongs:** `warehouse-base` · **v1** · **P0**
- **Disposition:** ***Fold into `P0-16`***, adding to its Scope §1:
  > **The measurement method, per number.** For each of `FR-422`'s eight targets, state what is
  > measured, on what fixture, and by what assertion. Ship a **seeded-volume fixture** in
  > `warehouse-base` (`@Tag("perf")`, excluded from the default build) generating N months of ledger
  > at the stated daily rate. Three targets need no fixture and become ordinary tests in `P0-03`
  > (concurrent allocation), `P2-13` (10 concurrent counters) and `P2-29` (100k streaming export);
  > name them there. Add two numbers the set does not yet state: **concurrent operators per warehouse**
  > and a **page-render budget for the ledger and position grids**.
  And add one acceptance line: *"Each `FR-422` number names its measurement method and the task that
  asserts it; a number with neither is deleted rather than left undefended."*
- **Irreversibility:** **reversible.**
- **Relationship to round 1:** **materially extends `S-084`.** `S-084` is *"no performance targets are
  stated anywhere"*, and the set closed it by stating them (`FR-422`). What is new is that stating
  them created a second, unclosed obligation — `p0-16`'s own acceptance box demands a measurement
  method that no document supplies and no v1 task builds.

---

### `K-004` · The position row is defended by an optimistic `@Version` and nothing says what happens when it loses: no retry, no backoff, no stated caller-visible outcome — **MAJOR**

- **What is missing or wrong:** `FR-016` is unusually good: *"Concurrency on the position row is
  defended by **all three** of an optimistic `@Version`, a database `CHECK`, and a stated
  lock-ordering discipline. A generated `available` column does not protect against two concurrent
  allocations, because on-hand did not change."* `p0-03` repeats it as *"all three, not a choice of
  one"*, and `DATA-MODEL.md` closes the subtlest hole by making `quantity_available` a
  **writer-maintained stored projection** carrying `CHECK (quantity_available >= 0)`, written in the
  same transaction as the reservation — so a reservation *does* touch the position row and the
  `@Version` *does* fire. I went looking for a hole there and did not find one.

  The hole is one step later. **Optimistic locking is a detection mechanism, not a resolution
  mechanism.** When `@Version` loses, the transaction throws `OptimisticLockingFailureException`, and
  the set never says what happens next:
  - how many times the writer retries,
  - with what backoff (a bare immediate retry under contention is a livelock),
  - what the caller sees when retries are exhausted — a `409` with which error code, on which field,
    and is it the same code as `INSUFFICIENT_STOCK`? It must not be: one means *try again*, the other
    means *there is not enough*, and an operator who cannot tell them apart will stop trusting both,
  - and whether the retry is safe with respect to `L-9` idempotency — a retried `POST /movements`
    inside the server must not consume the caller's idempotency key twice.

  `grep -rn "retry" issues/p0-03.md` → **0**.

- **Why it matters:** `FR-422` asks for **200 order lines a second with no oversell**. Warehouse
  demand is Pareto-shaped: the top 20 SKUs are most of the picks, and they live in one pick face — so
  those 200 lines/s converge on a small number of position rows. Advisory locking on the position key
  (`WH-SC-198`) correctly serialises *creation*; the `@Version` correctly detects *update* conflict.
  With no retry policy, a 5% conflict rate becomes ten user-visible failures a second on the hottest
  SKUs, at exactly the moment the warehouse is busiest — and the operator's experience is a pick that
  "randomly fails" on the fastest-moving part and works on the slow ones. That is the single most
  corrosive thing that can happen to floor trust in a WMS, and `FR-424` (*"scan-to-response under 300
  ms, or the operator stops trusting the system and works ahead of it"*) is the set's own statement of
  why.

- **Negative evidence:**

  ```bash
  cd /Users/bbhushan/work/git/workspace/warehouse-issues
  grep -rniE "retry|backoff|OptimisticLock|version conflict|contention|livelock|CONFLICT_RETRY" issues/p0-03.md
  #  → 0

  grep -rniE "optimistic.*(retr|backoff)|retr.*optimistic|OptimisticLockingFailure" docs/ issues/
  #  → 0

  grep -rn "retry" docs/WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md
  #  → FR-017 (idempotency key distinguishes a retry), FR-044 (inbound-message retry count),
  #    FR-332 (outbox publisher retry with backoff), FR-356/FR-374/FR-410 (Flyway blind repair).
  #    Every one is an *integration* retry. None is a *lock-contention* retry.
  ```

- **The mechanism I want, named:** State the contention response in `p0-03` as part of the writer
  service contract — **retry the transaction on `OptimisticLockingFailureException` up to a stated
  bound with jittered backoff, re-reading the position inside the retry; on exhaustion return `409`
  with a distinct code (`POSITION_CONTENTION`, not `INSUFFICIENT_STOCK`) and no field error, because
  it is not the caller's input that is wrong; and the caller's idempotency key is consumed once
  regardless of retry count.** Both bounds are numbers, and both belong in `admin_settings` under the
  `WAREHOUSE` category alongside `warehouse.outbox.max_attempts`, which `WHB-75` already seeds. Then
  add the assertion to `FR-422`'s allocation number so the retry policy is what the load test in
  `K-003` actually exercises.

- **Where it belongs:** `warehouse-base` · **v1** · **P0**
- **Disposition:** ***Fold into `P0-03`***, in the paragraph that already says *"The concurrency
  discipline — all three, not a choice of one"*. Add:
  > **And the response to contention, which is the fourth thing.** `@Version` detects; it does not
  > resolve. The writer service retries on `OptimisticLockingFailureException` up to
  > `warehouse.position.max_contention_retries` with jittered backoff, re-reading the position inside
  > the retry; on exhaustion it returns `409 POSITION_CONTENTION` — **a different code from
  > `INSUFFICIENT_STOCK`**, because one means *try again* and the other means *there is not enough*,
  > and an operator who cannot tell them apart stops trusting both. The caller's `(source_system,
  > idempotency_key)` is consumed exactly once regardless of retry count (`L-9`). Both settings seed
  > in `WHB-75` beside `warehouse.outbox.max_attempts`.
  Add an acceptance line: *"200 concurrent allocations against **one** position row produce no
  oversell, no livelock, and a bounded number of `409 POSITION_CONTENTION` responses"* — and a
  scenario, next to `WH-SC-198`, in the `conc` class.

  **While `p0-03` is open, correct its opening premise.** It leads with
  `PLATFORM-DEPENDENCIES.md` §4.9: *"balance-cache-with-rebuild — **warehouse invents it. Budget it
  as invention, not as a port.**"* As of 2026-09-01 that is **false**:
  `accounting-base/…/service/jobs/{AccBalanceRebuildJob,AccBalanceDrift,AccBalanceDriftAlertService,AccBalanceCacheProvider}.java`
  are live, and `AccBalanceDriftAlertService` ships the runbook (`ACC-RUNBOOK-BALANCE-DRIFT`) that
  `L-4`'s alert will need verbatim — *"Are the reports still trustworthy? **No, and they must not be
  treated as such.**"* The *shape* is a port; only the nine-member key and the warehouse-specific
  finding types are invention. Getting this wrong costs a quarter and produces two divergent job
  frameworks in one database.

- **Irreversibility:** **reversible** — service behaviour and two `admin_settings` rows. The only
  thing to get right at migration time is that the settings are seeded in `WHB-75` with the rest.
- **Relationship to round 1:** **materially extends `S-085`** (COVERED-uncited BLOCKER, *"allocation
  concurrency"*). `S-085` asked *which mechanism*; the set answered with `FR-016`'s three-layer
  defence, which is a good answer. What is new is the layer after detection: **`S-085` is closed on
  the mechanism and open on the response to contention**, and the response is what the operator
  actually experiences.

---

### `K-005` · Every outbox and queue signal in the set is failure-shaped; none is lag-shaped, so a consumer that is falling behind — or a subscription somebody disabled and forgot — is invisible — **MAJOR**

- **What is missing or wrong:** The outbox is well built. `whb_outbox_deliveries` records every
  attempt with `status ∈ {OK, RETRY, DEAD}`, has a partial index `WHERE status = 'DEAD'`, and
  `WS-058 Outbox Dead-letter` defaults its status filter to `DEAD` with **Retry** and **Retry all
  dead for subscription** actions. `WS-223`'s health signals include *"dead outbox deliveries"*.

  Every one of those is a **failure** signal. Two states produce no failure at all:

  1. **A subscription falling behind.** `whb_outbox_subscriptions.last_delivered_cursor` is a column
     on `WS-057`; the outbox's max cursor is on `WS-056`. **Nothing computes the difference**, no
     screen shows it, and no health signal names it. A subscriber that is up, returning `200`, and
     delivering 300 events/minute against 900/minute of production has zero `RETRY` rows, zero `DEAD`
     rows and an ever-growing lag. In v2 that subscriber is `wh3_billable_events` — the 3PL billing
     meter, which `DATA-MODEL.md:1958` describes as *"the meter reads the outbox by cursor"*. A
     month-end billing run over a meter that is four days behind under-invoices every client, and the
     first person to notice is the client who is *over*-invoiced next month when it catches up.
  2. **A subscription switched off.** `is_active` is on `WS-057` with an **Add/Edit/Disable** action.
     A disabled subscription attempts nothing, so it generates no `RETRY`, no `DEAD` and no row on
     `WS-058`. It is silent by construction, and the only thing that would find it is a human reading
     `WS-057` and noticing a `false`.

  The same shape appears once more, and it is the one `IRREVERSIBLE.md` calls out itself. `IRR-21`
  says the delta between `occurred_at` and `recorded_at` *"is **the only latency diagnostic that
  exists**"* — and `recordedAt` appears on exactly **one** row of `BUILD-SPEC-SCREENS.md` (`:1036`, a
  movement-detail field), on no grid, in no filter, and in no health signal. The set went to the
  trouble of making three timestamps `NOT NULL` at `PNR-1` in order to have this diagnostic, and then
  never surfaces it.

- **Why it matters:** The distinction is between *broken* and *behind*, and warehouses fail in the
  second mode far more often. Broken is loud and someone fixes it in an hour. Behind is silent,
  compounds daily, and is discovered on the day it becomes a number on an invoice — at which point
  the argument with the customer is about a month of data, not an outage. The lag number is one
  subtraction over two columns that already exist, on a table that already has `uk(cursor)`.

- **Negative evidence:**

  ```bash
  cd /Users/bbhushan/work/git/workspace/warehouse-issues
  grep -rniE "\blag\b|backlog|falling behind|behind by|cursor gap|queue depth|watermark|staleness|max_lag" docs/ issues/
  #  → "low-watermark alert" (FR-202, the v2 AWB pool) and nothing else. No outbox lag, no queue
  #    depth, no staleness signal anywhere.

  grep -c "recordedAt" docs/BUILD-SPEC-SCREENS.md    # → 1   (BUILD-SPEC-SCREENS.md:1036, a detail field)
  grep -n "signalCode\|Install Health" docs/BUILD-SPEC-SCREENS.md | head -3
  #  → :1791 WS-223 — seven signals: movements posted today vs baseline · handovers stuck pending ·
  #    counts overdue · negative positions · orphaned reservations · dead outbox deliveries ·
  #    failed jobs.  All seven are failure- or absence-of-work shaped. None is lag-shaped.
  ```

- **The mechanism I want, named:** Three signals, all computable from columns that already exist, no
  new table:
  - **`OUTBOX_LAG`** — `MAX(whb_outbox.cursor) − whb_outbox_subscriptions.last_delivered_cursor`, per
    active subscription, with a threshold seeded in `admin_settings` under `WAREHOUSE` beside
    `warehouse.outbox.max_attempts` (`WHB-75`). Surface it as a column on `WS-057` — the two source
    columns are already on that grid and on `WS-056` — and as a `WS-223` signal.
  - **`OUTBOX_SUBSCRIPTION_DISABLED`** — count of `is_active = false` subscriptions, so switching one
    off during an incident and forgetting is a visible state rather than a memory.
  - **`INGESTION_LATENCY`** — the p95 of `recorded_at − occurred_at` over the last hour, per
    `source_system`. This is `IRR-21`'s stated purpose finally having a consumer, and it is the one
    number that distinguishes *"the handhelds are offline"* from *"the port is slow"* from *"an
    adapter is replaying history"*, which look identical on every other screen in the product.

- **Where it belongs:** `warehouse-base` (the two outbox signals, with `P0-11`) · `warehouse`
  (`WS-223`'s row) · **v1** for the computation, **v1.1** for the `WS-223` tile, since that screen is
  `P3`
- **Disposition:** ***Fold into `P0-11`*** (the outbox task, which owns `WS-056`/`WS-057`/`WS-058`),
  adding to its Scope:
  > **Lag is a first-class signal, not an absence of failure.** `WS-057` gains a computed
  > **`cursorLag`** column (`MAX(whb_outbox.cursor) − last_delivered_cursor`) and a
  > `lagOverEvents` number filter; a threshold seeds in `WHB-75` as
  > `warehouse.outbox.max_cursor_lag`. `WS-223` (`P3-17`) gains `OUTBOX_LAG`,
  > `OUTBOX_SUBSCRIPTION_DISABLED` and `INGESTION_LATENCY` alongside its seven existing signals —
  > *"dead deliveries"* is a failure count and cannot see a subscriber that is merely behind, or one
  > that was disabled and forgotten.
  And add one line to `P0-08` (the port): *"`recorded_at − occurred_at` is `IRR-21`'s stated latency
  diagnostic and must be queryable per `source_system`, not only visible on a single movement."*
- **Irreversibility:** **reversible** — computed columns and a settings row; no schema change.
- **Relationship to round 1:** **new.** `G-045`/`FR-332` cover retry, backoff and the dead-letter
  grid; `FR-398`/`WS-223` cover install health; `U-002` covers the absence of an alerting substrate.
  None of them distinguishes a queue that has failed from a queue that is behind, and
  `grep -rniE "\blag\b|backlog|queue depth"` over the whole set returns only the v2 AWB
  low-watermark.

---

### `K-006` · `occurred_at` has a ceiling and no floor, and it is the partition key — so a late-arriving movement dated before the oldest live partition fails as a raw PostgreSQL error rather than a stated refusal — **MINOR**

- **What is missing or wrong:** The design is careful about the future boundary and silent about the
  past one.
  - **Ceiling, specified:** `WH-SC-031` — a device whose clock is 26 hours fast gets
    `422 OCCURRED_AT_IN_FUTURE` with `details.errors["occurred_at"]`, nothing is written, *"a future
    business time breaks every ageing calculation silently, which is why this is a refusal and not a
    warning."*
  - **Forward partition boundary, specified:** `WH-SC-043` advances the clock into a new month and
    asserts the creation job made the partition ahead of need.
  - **Floor:** nothing. There is no lower bound on `occurred_at` and no scenario for a movement dated
    into a month whose partition does not exist. `p0-02`'s acceptance says *"a movement dated into an
    unmade partition **fails loudly**"* — but the failure it gets is PostgreSQL's
    `no partition of relation "whb_stock_movements" found for row`, raised at `INSERT`, inside a
    transaction that has already done work, surfacing as a **500** rather than a `4xx` with a code.

  The past boundary is not static. `FR-023` / `P6-01` archiving detaches old partitions, and
  `p6-01.md:75-78` already worries that *"the cut-off must be expressed in the column the partition is
  on, or the archive moves the wrong rows."* The moment the first partition is detached, the floor
  becomes real and it moves every archive run.

  The paths that reach it are the set's own: `WH-SC-169` (*"a movement is **never refused** for
  arriving after a movement with a later `occurred_at`; late arrival is not an error condition"*),
  `WH-SC-195` (400 queued scans after a full shift out of coverage), and `FR-430`'s catch-up entry
  mode, which exists precisely to accept backdated movements carrying the true event time.

- **Why it matters:** Small in v1 — the floor is the install date, and `FR-020`'s period lock catches
  most back-dating first, on a *different* column (`effective_date`, per `L-13`), which is why it does
  not catch all of it. It becomes real at the first archive run, and it is cheapest to fix now because
  `WH-SC-031`'s refusal path already exists and this is its mirror image. The bad version of the day
  it bites: a supervisor uses catch-up entry mode after a long outage, keys the true times, and gets a
  500 with no field error and no explanation.

- **Negative evidence:**

  ```bash
  cd /Users/bbhushan/work/git/workspace/warehouse-issues
  grep -rniE "OCCURRED_AT_IN_PAST|OCCURRED_AT_TOO_OLD|BEFORE_RETENTION|oldest partition|earliest partition|occurred_at floor|lower bound.*occurred" docs/ issues/
  #  → 0

  grep -rn "OCCURRED_AT_IN_FUTURE" docs/ issues/
  #  → SCENARIO-CATALOGUE.md:191 (WH-SC-031) — the ceiling exists and has a code; the floor has neither
  ```

- **The mechanism I want, named:** Symmetry. A stated floor — the lower bound of the oldest live
  partition — checked in the writer service **before** the insert, refused as
  `422 OCCURRED_AT_BEFORE_RETENTION` with `details.errors["occurred_at"]`, in exactly the shape
  `WH-SC-031` already uses. The check is a bounded read of the partition catalogue, cacheable, and it
  converts a database-level 500 into a domain refusal an operator can act on.

- **Where it belongs:** `warehouse-base` · **v1** (the check and the code) · **P0**
- **Disposition:** ***Fold into `P0-02`***, whose acceptance already carries the loud-failure line.
  Amend it to:
  > *"Monthly partitions are created by a job, not by hand; a movement dated **forward** into an
  > unmade partition finds the partition already made (`WH-SC-043`), and a movement dated **backward**
  > before the oldest live partition is refused with `422 OCCURRED_AT_BEFORE_RETENTION` on
  > `occurred_at` — the mirror of `WH-SC-031`'s ceiling — rather than reaching PostgreSQL and
  > surfacing as a 500."*
  Add one scenario in the `edge` class next to `WH-SC-031`, and one line to `P6-01`: *"detaching a
  partition moves the `occurred_at` floor; the refusal boundary is read from the live partition set,
  never from a constant."*
- **Irreversibility:** **reversible** — a service-level check and an error code. It is only listed
  against `P0-02` because that is where the partition strategy and its acceptance line live.
- **Relationship to round 1:** **new.** `T-095`/`S-096`/`S-051`/`FR-423` cover the partition and
  archive *strategy*; `FR-008`/`WH-SC-031` cover the future bound. No finding covers the past bound,
  and `grep -rniE "OCCURRED_AT_IN_PAST|BEFORE_RETENTION|oldest partition"` → 0.

---

## §3 · What I checked and found sound

This section exists so round 3 does not re-walk this ground. Everything below I went looking for as a
suspected gap and found already closed, with the id that closes it.

### A · Scale and volume

| What I checked | Found | Where |
|---|---|---|
| Are the volume numbers stated at all, or did I have to derive them? | **Stated by the set.** 1M ledger rows/day peak, 20k for a dealer parts department, ≤5M live position rows, *"with the unique key understood as the hot spot"* | `FR-422` |
| Is the ledger partitioned, and from when? | **From migration one**, both tables, `PARTITION BY RANGE (occurred_at)` monthly, with an automatic creation job. The PK consequence is worked through: `(id, occurred_at)` composite, `occurred_at` denormalised onto the line and held identical by `IRR-13`, *"a line in a different partition from its header is unrepresentable"*, and every FK into the ledger degraded to a bare UUID (`G13`) | `DATA-MODEL.md` §1.9, `:286-317`, `:593`, `:657`, `WHB-30`, `IRR-62` |
| Should `whb_stock_positions` be partitioned too? | **Correctly not.** *"Not partitioned: it is bounded by grain, not by time"* — with three partial indexes `WHERE quantity_on_hand <> 0` so the dead grain is out of the index | `DATA-MODEL.md:746` |
| The `OFFSET`-depth problem at 100M rows | **Known, costed, and answered honestly for v1**: an enforced date-range filter on the ledger grid, keyset/seek paging named as the v1.1 successor rather than promised now | `PD-D2`/`PP-7`, `p0-16` §1, `WH-SC-197` |
| Export at 100k rows | **Three problems separated**, which is the part everyone gets wrong: the 10,000-row cap, the transaction held open, and the 64k Excel cell-style limit *"at scale, not in dev"*. Answer is a streaming path **in `warehouse-base`**, with the platform extraction proposed separately and explicitly decoupled | `PD-D3`/`PP-6`, `p0-16` §1, `P2-29` |
| Filter-aware statistics over ledger-sized tables | **Rollup tables maintained by the job that proves `L-4`**, decided *with* the reconciliation design — and an explicit instruction **never** to register a `statistics.*` cache name, citing `CacheConfiguration.java:190-196` and issues `#790`/`#791` | `FR-395`, `PD-D4`/`PP-8`, `p0-16` trap 3 |
| Archiving without breaking the rebuild | **Archiving is a transaction**: an `OPENING_BALANCE` movement dated at the cut-off is written *first*, then rows move — *"otherwise `L-4` becomes false for every install that has ever archived"* | `FR-023`, `DATA-MODEL.md:924`, `P6-01` |
| The `L-4` nightly rebuild's own runtime and window | Not stated as a duration — but this is subsumed by `K-001`: the rebuild has no cadence declaration, so "what runs it, when, and what if it is still running at 9am" has no answer to critique yet. Filed there, not twice |
| The partition-key conflict (`occurred_at` vs `posting_date`) | **Already the set's own top unnumbered gate.** `X-024`, `⛔ UNNUMBERED` in `01-EPIC-p0.md:201`, `p0-02.md:228`, `00-EPIC-master.md:122`, `08-EPIC-p6.md:131`, `p6-01.md:102`. Not restated |

### B · Concurrency

| What I checked | Found | Where |
|---|---|---|
| Is the allocation mechanism named or hand-waved? | **Named, all five, each with its precedent counted**: advisory lock for a key with no row to lock, pessimistic-locked counter row for gapless numbering, deferrable constraint trigger for balance-at-commit, optimistic `@Version` on the position, `FOR UPDATE SKIP LOCKED` for task claiming — *"four of the five have exactly one precedent each in this repository and the fifth has none"* | `FR-437`, `WH-SC-198` |
| **The hole I expected and did not find.** Two concurrent reservations insert into `whb_reservations` without touching the position, so neither `@Version` nor the `CHECK` fires | **Closed by design.** `quantity_available` is a **stored, writer-maintained projection** (deliberately *not* `GENERATED`) carrying `CHECK (quantity_available >= 0)` and *written in the same transaction as the reservation*. The position row **is** touched; `@Version` **does** fire. `FR-016` states the reasoning explicitly: *"a generated `available` column does not protect against two concurrent allocations, because on-hand did not change"* | `DATA-MODEL.md` `whb_stock_positions`, `FR-016`, `I-6` |
| Why there is no `CHECK (quantity_on_hand >= 0)` | **Deliberate and correct** — negative on-hand is a per-item × site policy (`BLOCK`/`WARN`/`ALLOW`), so it cannot be a table constraint. The non-negative guarantee lives on `quantity_available`, which is the column that actually governs allocation | `DATA-MODEL.md`, `L-6`, `I-6` |
| First-ever write to a position tuple — nothing to lock pessimistically | **`pg_advisory_xact_lock(hashtext(:key))` on the position key**; one creates, the other updates, *"neither raises a unique-key violation to the caller"* | `WH-SC-198`, `FR-437` |
| The nine-member key with three nullable members | `CREATE UNIQUE INDEX … NULLS NOT DISTINCT`, and the `L-4` rebuild joins on `IS NOT DISTINCT FROM` for the same three. Both halves present — this is the pair people get half-right | `DATA-MODEL.md`, `L-5`, `I-5` |
| Gapless numbering under concurrency | **Pessimistic-locked counter row** (`SELECT … FOR UPDATE`), module-scoped, with the platform's scan-based generator explicitly rejected as *"not gapless and racy"* (`C-019`) | `FR-426`, `whb_number_series`, `DATA-MODEL.md:2508,:2806` |
| The outbox cursor under rollback | **The trap is named and the wrong answer is pre-refused**: *"A Postgres sequence advances outside the transaction, so a rolled-back movement leaves a hole and a consumer reading 'by cursor + 1' stalls forever. Decide the mechanism explicitly — a locked counter row in the same transaction is the shape that works."* A locked counter row also makes cursor order equal commit order, which closes the in-flight-commit skip hazard as a side effect | `p0-11` traps |
| `@TransactionalEventListener(AFTER_COMMIT)` substituted for an outbox | **Pre-refused, with the four reasons**: no durability, no retry, no ordering, no "stuck in PENDING" query | `p0-11`, `PP-11` |
| Idempotent ingestion under a concurrent duplicate | `uk(source_system, idempotency_key)` + `payload_hash` distinguishing a retry from a reused key + **persist-before-process** with a status ladder and the stored result returned on replay | `FR-017`, `FR-044`, `L-9`, `IRR-49` |
| Task claiming by N concurrent handhelds | `FOR UPDATE SKIP LOCKED`, flagged as zero-precedent and **load-tested in the PR, not reasoned about** — the acceptance line is *"N concurrent claimers against one queue produce zero double-claims under load"* | `FR-425`, `p3-02.md:60,:81`, `WH-SC-230` |
| Two pickers on one location / a count against an actively-picked location | Covered as *business* exceptions by the count freeze and the blocked-move queue (`FR-153` — a count never writes on-hand; `WH-SC-170` — sufficiency is evaluated at post time, and the refusal *"is a real stock discrepancy and belongs in the blocked-move queue"*). R11 owns this class; not restated | `FR-153`, `WH-SC-170`, `WH-SC-249` |

### C · Observability and support

| What I checked | Found | Where |
|---|---|---|
| Is there a drift findings **grid**, or just an alert? | **A grid, v1·P2**, with all four finding types, `unresolvedOnly` default, Assign and Resolve (note mandatory). *"A drift alert with no findings grid is an email nobody can act on"* | `WS-043`, `whb_position_drift_findings`, `FR-012`/`FR-163` |
| Does an exception get an owner and a clock? | **Yes** — `wh_reconciliation_exceptions` carries `owner_user_id`, `age_days`, `status`, `resolution_note` and an FK to the drift finding. *"An exception nobody owns is an exception nobody clears"* | `WS-098`, `DATA-MODEL.md:1005`, `W12` |
| Dead-letter visibility and replay | `WS-058` defaulting to `DEAD`, with **Retry**, **Retry all dead for subscription**, and **Replay from cursor** with a typed confirmation on the cursor reset | `WS-056`–`WS-058`, `FR-332` |
| Is the audit trail the ledger or the platform activity log? | **The ledger, explicitly** — *"the platform's activity log is asynchronous, out of transaction and swallows its own exceptions; for a stock ledger that is telemetry, not a record"* — with five named auditor artefacts and field-level before/after in `whb_audit_event_changes` | `FR-427`, `S-083`/`C-049` |
| "Who changed this" when the actor is not a person | `actor_type ∈ {USER, DEVICE, INTEGRATION, SCHEDULED_JOB, IMPORT, SYSTEM_CORRECTION}` + `device_id`, at `PNR-1`, with the scheduled job carrying a **null user rather than an ADMIN id** | `IRR-48`, `WH-SC-037` |
| Does the audit answer survive `L-2`'s append-only rule? | **Yes** — the mutable-column allowlist on the `L-2` trigger is explicit (`posting_status`, `is_reversed`, `reversed_by_movement_id`), and the lines table drops `updated_at`/`updated_by` entirely because *"a column that can never change should not exist to be changed"* | `DATA-MODEL.md:104`, `IRREVERSIBLE.md` §4.1 |
| "Replay this movement" | **`POST /movements/{id}/reverse`** with its own idempotency key, mandatory reason code, mirror lines, refusal to reverse a reversal — and correction is *never* an edit, anywhere in the product | `FR-005`, `FR-035`, `L-3` |
| "Show me this document's whole chain" | Bidirectional traceability (`L-12`), the lineage `GET` on the port, `whb_cost_layer_consumptions` recording **which layer fed which issue**, and `chosen_reason` on the allocation — *"why this lot and not that one"* | `FR-349`, `DATA-MODEL.md:851,:1787` |
| A job-runs surface at all | **`WS-064`**, with a **Run now** action gated on `whb_job_runs:trigger` — the manual-trigger half of operability is present. Only the *expected-run* half is missing (`K-001`) | `WS-064`, `FR-165` |

### D · Security and isolation

| What I checked | Found | Where |
|---|---|---|
| Owner-level row isolation — is the enforcement point named? | **Named, and it is the right one.** `PC-32`: *"Owner scope is a `WHERE`-clause guard, not a UI filter."* `P1-18` builds warehouse ∩ branch ∩ owner in the `WHERE` clause across all four surfaces of `FR-114`, with the epic's line *"a menu filter is not a guard"* | `PC-32`, `FR-114`, `P1-18`, `02-EPIC-p1.md:74` |
| Does a denied owner get an empty grid or a refusal? | **`403 OWNER_NOT_PERMITTED`, never an empty grid** — which is the difference between an access control and *"a leak with a friendly UI"*, in the task's own words | `p1-18.md:54,:80`, `WH-SC-140` |
| Can a 3PL client see another client's anything? | `OD-3` settles it: one database per customer, no tenancy layer (`grep -ril "tenant" platform/backend/src/main/java` → 0), and `PC-32`'s owner scope carries the 3PL case either way. The v2 portal is *"a permission surface over the existing screens, not a second application with its own authentication"* | `OD-3`, `FR-284`, `PORT-AND-ADAPTER-CONTRACT.md:2017` |
| Handheld session lifetime, shared scanners, a stolen gun | **Fully specified at v1.1** — `whb_devices` (inventory, assignment, `last_seen_at`, `app_version`), device-bound long sessions, fast shared-device sign-in, shift handover, and **remote kill designed for the offline case**: *"Kill is a server-side session revocation checked on the next request, not a push the lost gun must receive — a gun in a taxi has no network"*, with an acceptance line proving it with the device offline at the moment of the kill | `FR-222`, `S-088`, `p3-03.md:15,:55-56,:66` |
| Movement attribution on a shared device | `actor_type = DEVICE`, `actor_user_id = <the signed-in operator>`, `device_id = RF-0117` — all three on the row, so *"a mis-scanning gun is diagnosable retroactively"* | `WH-SC-037`, `IRR-48` |
| Non-own stock never valued — is the **read** side enforced? | **Yes, and the assertion is the strong one.** `WH-SC-032` asserts *"the number is **absent**, not that it is zero"*; `L-14` is a schema fact (`owner_type.posts_to_our_gl = false`), not only a service rule; custody value is *"a different number, on a different report"* (`WS-227`) | `FR-112`, `L-14`/`I-16`, `WH-SC-032`, `DATA-MODEL.md:860` |
| Secrets on integration surfaces | Masked at the edge: `secret_ref` responses carry `hasValue`, **never the value**, and `hasValue` is null-vs-present rather than undefined | `p0-11`, `wh_channel_accounts`, `whin_compliance_credentials` |
| Support impersonation | **Split correctly**: the feature is platform's, the **column is warehouse's and it is v1** — `on_behalf_of_actor_id`, because *"without the feature the column is always null; without the column, year one cannot answer the question, forever."* (Its absence from the movement header is `Y-001`, R11's; not restated) | `p0-16` §6, `PP-4`, `S-092` |
| Port authentication for an out-of-process consumer | `OD-8`, open with a stated recommendation (a platform service principal) and named as *"the only item in this set that platform must build for warehouse"* | `OD-8`, `PP-2` |
| API keys, webhooks, rate limits | Already `NEEDS-TASK` with a proposed id — `S-097` → `P5-22`, v2, argued as platform work first. Not restated | `GAP-REGISTER.md:660,:1024,:1044` |
| `@PreAuthorize` on the port | On **every** method, plus the posting permission checked against the caller's **owner grants** — the second check is the one usually forgotten | `FR-043` |

### E · Resilience and degraded mode

| What I checked | Found | Where |
|---|---|---|
| Is there an offline mutation queue in the live mobile app? | **No — verified.** `grep -rli "offlinequeue\|offline_queue\|mutationqueue\|pendingmutation" mobile/src/` → **0**; 40 files mention `offline` and they are network *detection* (`NetworkContext.tsx`, `reactQuery.ts`, `errorClassifier.ts`). The set's claim is correct | `PLATFORM-DEPENDENCIES.md`, verified against `classic` |
| So what does v1 do when Wi-Fi drops mid-aisle? | **v1 is online-only and says so** — and ships the *irreversible* half anyway: per-scan client-generated idempotency key and device-supplied `occurred_at` in `P0-08`, *"because adding them later means re-versioning every RF endpoint."* The queue itself is `P3-04` | `p0-16` §4, `FR-221`, `IRR-49`, `PP-12` |
| Is `L-13`'s three-timestamp design a behaviour or only columns? | **A behaviour, and it is specified.** `WH-SC-030` (pick at 22:05 IST, sync at 06:12 next day: three distinct stored values, September's register includes it, dock-to-stock measured from `occurred_at`); `WH-SC-169` (late arrival is never an error; `sequence_no` is acceptance order and *"nothing in the product may assume the two agree"*); `WH-SC-195` (400 queued scans, 6 duplicates return their originals, conflicts *"surfaced to the operator, never swallowed"*); `WH-SC-250` (four-hour outage, paper fallback, catch-up entry with the true event time) | `L-13`, `FR-007`, `FR-430`, `WH-SC-030/169/195/250` |
| Backup and restore | **Filed, with an owner, and with the honest fallback stated**: *"`grep -c -i "restore" DatabaseBackupService.java` → 0 … no restore method, no WAL archiving, no PITR, no restore-verification job and no stated RPO/RTO. This is platform's to build, and it must be filed now rather than assumed."* Warehouse's fallback is **a disclosure, not a workaround** — a written RPO/RTO of "unknown" in the install guide | `FR-429`, `S-082`, `PP-1`, `p0-16` §5, `WH-SC-253` |
| Print server down at dispatch; a label printed wrong after the pallet moved | Printing is v1 (`A-2` moved it), with `wh_print_jobs` as *"a stored artefact with a void path, never a delete"*, reason-coded **Void**, **Reprint** flagged as a reprint (*"a reprinted pallet label is a duplicate licence plate in the wild"*), versioned template bodies never edited in place so *"a reprint of last month's label reproduces last month's layout"*, and reprint-from-the-floor on mobile | `FR-224`, `FR-225`, `WS-131`/`WS-132`, `DATA-MODEL.md:1027-1028` |
| Port consumer down | Retry with backoff to `max_attempts`, then the dead-letter grid with `httpStatus` and `errorDetail`, then **Retry all dead** and **Replay from cursor**. (What is *not* covered is the consumer that is merely slow — `K-005`) | `FR-332`, `WS-058`, `WH-SC-252` |
| Accounting down at period close | `posting_status` `PENDING → POSTED` with `handover_id`, so an unhanded-over movement is a queryable state rather than a lost one; *"handovers stuck pending"* is one of `WS-223`'s seven signals | `WH-SC-156`, `FR-233`, `WS-223` |

### F · Performance budgets and known live traps

| What I checked | Found | Where |
|---|---|---|
| Does any document state a target? | **Eight of them.** The measurement method is what is missing (`K-003`) | `FR-422`, `FR-424` |
| Export per-cell AOP logging / export ignores filters and grid sort | **Named as three separate problems** with the streaming answer, and `p0-16` carries an explicit trap: *"Do not edit `BaseExportService` to raise the row cap"* | `PD-D3`/`PP-6`, `p0-16` §1 |
| Filter-scope allowlist silently dropping filter fields | `FR-432`, with the honest note that this *"will be the largest single addition to that allowlist the codebase has seen"* | `FR-432`, `C-042` |
| `grid_preferences.default_filters` **and** `default_columns` both required | `FR-433`, including that the filter table's real name is `filter_definitions` and *"the name six prior-art documents use does not exist and would crash Flyway"* | `FR-433`, `C-036`/`P-006`/`P-055` |
| Native-query timestamp mapping returning null on an unhandled driver type | `FR-438` — all four types handled, warning logged on an unknown one, *"returning null for an unhandled type is silent data loss"* | `FR-438`, `C-036` |
| Unregistered cache names throwing on first call | Named twice, with the line reference: `CacheConfiguration.java:375-377`, and the `statistics.*` mistake at `:190-196` cited with its issue numbers | `p0-11` traps, `p0-16` traps |

---

## §4 · Refused

Candidate findings I deliberately did **not** file, and why.

| Candidate | Why refused |
|---|---|
| *"The partition key is unresolved between `occurred_at` and `posting_date`"* | **Already the set's own loudest gate.** `X-024`, carried as `⛔ UNNUMBERED` in five places including `01-EPIC-p0.md:201` and `p0-02.md:228`. Restating it would be exactly the padding the brief warns about. `K-006` deliberately does **not** depend on which column wins |
| *"v1 has no alerting infrastructure"* | **`U-002`** (R10), filed this round. My `K-001` and `K-005` are about which *signals* should exist, not about the delivery channel; I have kept them disjoint and said so in each |
| *"`on_behalf_of_actor_id` is mandated but absent from the movement header"* | **`Y-001`** (R11), filed this round |
| *"Work in flight has no abandonment clock"* | **`Y-004`** (R11). The stuck-task-queue item on my inventory is that finding seen from the machine side; filing it again would be the same defect twice |
| *"API keys, webhooks and rate limits are unspecified"* | **`S-097`**, already `NEEDS-TASK` with a proposed `P5-22` and a stated argument that it should be platform work. Nothing to add |
| *"Support impersonation does not exist"* | **`S-092`** + `p0-16` §6, which already splits feature (platform) from column (warehouse, v1) correctly |
| *"There is no restore path"* | **`S-082`**/`FR-429`/`PP-1`, filed with an owner and a written-"unknown" disclosure fallback. The set's answer is better than most shipped products' |
| *"Two concurrent reservations bypass the position row, so `@Version` never fires"* | **I was wrong** — `quantity_available` is a writer-maintained stored projection updated in the reservation's own transaction, with `CHECK (quantity_available >= 0)`. Recorded in §3 as sound rather than filed. `FR-016` even pre-refutes the generated-column version of the same mistake |
| *"The outbox publisher can double-deliver with more than one worker"* | **Tolerated by design and stated**: `FR-330` specifies at-least-once with consumer-side dedupe on `(consumer, sequence)`. The *single-instance* half of it is real and is folded into `K-001` rather than filed separately, per the brief's rule 8 |
| *"The outbox cursor can skip an in-flight commit"* | Closed as a side effect of `p0-11`'s locked-counter-row ruling: the counter is taken inside the movement's transaction, so cursor order equals commit order and there is no window in which a higher cursor is visible before a lower one |
| *"No mobile counterpart is decided for screen X"* | **`FR-218`/`p0-16` §3** make a blank mobile cell a review failure with a CI check; the four tasks that still state no verdict are **`H-010`** (R9) |
| A field-level encryption / PII scheme for warehouse tables | **Over-engineering, out of segment.** Warehouse holds no PII beyond the platform user reference. Cost visibility (`K-002`) is a real commercial exposure; encryption at rest is not this product's problem to solve twice |
| Rate limiting `POST /movements` in v1 | **Over-engineering for v1** given `OD-3` (one database per customer, no shared tenancy) — a runaway adapter is a support call, not a cross-customer incident. Correctly deferred with `S-097` |
| A separate "why is this unit not allocatable" diagnostic screen | The composition already exists across `WS-043` (positions with reserved and available), the reservations grid with the holder quad, `WS-098` (orphaned reservations with an owner and a clock) and `chosen_reason` on the allocation. A fifth screen composing them is a nice-to-have, not a gap — and `P3-23`'s in-product help is where the explanation belongs |

---

## §5 · Counts

```bash
cd /Users/bbhushan/work/git/workspace/warehouse-issues
grep -c "^### \`K-" docs/reviews/R13-non-functional-and-operability.md                  # → 6
grep -o "\*\*BLOCKER\*\*$" docs/reviews/R13-non-functional-and-operability.md | wc -l  # → 1
grep -o "\*\*MAJOR\*\*$"   docs/reviews/R13-non-functional-and-operability.md | wc -l  # → 4
grep -o "\*\*MINOR\*\*$"   docs/reviews/R13-non-functional-and-operability.md | wc -l  # → 1
```

| Severity | Count | Findings |
|---|---|---|
| **BLOCKER** | **1** | `K-001` |
| **MAJOR** | **4** | `K-002` `K-003` `K-004` `K-005` |
| **MINOR** | **1** | `K-006` |
| **Total** | **6** | |

**By disposition** — all six fold into existing tasks; **no new task is proposed**:

| Finding | Folds into | Migration touched | Irreversible? |
|---|---|---|---|
| `K-001` | `P0-13` (+ amend `p0-03`, `PLATFORM-DEPENDENCIES.md` §4.9) | `V500043` | must land in `V500043`; not a `PNR` |
| `K-002` | `P1-18` (+ reserve the permission in `WHB-71`/`V501000`); needs one new `FR-` row | `V501000` for the permission string only | permission string is `IRR-63`-class; the guard is reversible |
| `K-003` | `P0-16` (+ named assertions in `P0-03`, `P2-13`, `P2-29`) | none | reversible |
| `K-004` | `P0-03` (+ two `admin_settings` rows in `WHB-75`) | `V501100` for the settings rows | reversible |
| `K-005` | `P0-11` (+ a line in `P0-08`, three signals in `P3-17`/`WS-223`) | `V501100` for the threshold row | reversible |
| `K-006` | `P0-02` (+ one line in `P6-01`, one new `edge` scenario) | none | reversible |

**Two cross-cutting corrections** that are not findings in their own right but must travel with the
above, because both are load-bearing instructions that are now false:

1. `PLATFORM-DEPENDENCIES.md` §4.9 and `issues/p0-03.md`'s opening — *"balance-cache-with-rebuild —
   warehouse invents it. Budget it as invention, not as a port."* As of **2026-09-01**
   (`812b310dad`, `a31405c85c`), `accounting-base` ships `AccBalanceRebuildJob`, `AccBalanceDrift`,
   `AccBalanceDriftAlertService` and `AccBalanceCacheProvider`, plus a 23-file / 2,709-line job
   framework. The shape is a port; only the nine-member key and the warehouse finding types are
   invention.
2. `platform/backend/pom.xml:29-41` already declares ShedLock *"used by warehouse-base schedulers"*,
   root `pom.xml:34` pins `5.10.0`, and there is **no** `shedlock` table in any `.sql` and **no**
   `@SchedulerLock` in any `.java`. Either warehouse uses it and ships the table, or — following
   `AccJobRunRecorder.java:63-79`, *"there is no ShedLock in this repository"* — it uses the partial
   unique index as the job lock and someone removes the dependency. Both are decisions; neither has
   been taken.
