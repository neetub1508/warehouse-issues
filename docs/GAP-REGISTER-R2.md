# GAP-REGISTER-R2 — the disposition of every round-2 finding

<!-- FR-447 was a proposal when this file was written; it is now a real row in WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md §6.27, so the fr-citations exemption that stood here has been removed rather than left stale -->
<!-- check-design-set: scenario-citations file WH-SC-306 — the SCENARIO-CATALOGUE.md §5 rule 3 next-free allocation marker, the same allocation DESIGN-SET-DEFECTS.md and GAP-REGISTER.md already declare. Round 2 took WH-SC-301-WH-SC-305 for SCENARIO-CATALOGUE.md 3.21, so the marker — and this declaration with it — moved to WH-SC-306 -->

> **What this document is for.** `GAP-REGISTER.md` dispositions the **575** findings of review round 1.
> This one dispositions the **62** findings of round 2, under the same rule that produced it —
> `D-12`: *every capability found by any lens is placed in a version and carried in a task file **now***.
> A finding with no disposition row is a finding that will be rediscovered by the implementation team
> at the worst possible moment, which is the entire failure mode this programme exists to avoid.
>
> **Round 1 is not superseded.** Nothing here withdraws a round-1 finding or a round-1 disposition.
> Round 2 was run specifically to find what round 1's seven lenses did **not**, and every one of the
> eight lenses carries a `§ Refused` section recording the candidates it declined precisely because
> round 1 already owned them.

**Date** 2026-09-02 · **Branch** `docs/round-2-functional-review`

---

## §1 · Why there was a round 2, and what it was allowed to do

Round 1 was a **breadth** exercise: seven lenses swept the market, the standards, the statute, the
prior art and the live codebase, and produced 575 findings and a 236-row competitor benchmark. It
answered *"what should a warehouse product do?"* very well.

It did not answer the question the product owner actually asked, which is a **completeness** question:
*"after implementation, will we say — this thing was pending, we should have thought of it earlier?"*
Those two questions have different failure modes. Breadth misses nothing in the market and everything
in the seams: the step between two specified steps, the exception in the middle of a specified happy
path, the field a builder needs that no document states, day 400 of a system that only specifies day 1.

So round 2 ran **eight orthogonal lenses**, chosen so that none of them repeats a round-1 angle:

| Lens | Prefix | What it attacked | Findings |
|---|---|---|---|
| **R8** | `Q-` | Per-task buildability across the **70 v1 task files** (8,399 lines) — could a builder start? | 6 |
| **R9** | `H-` | The same, for the **68 P3–P6 tasks and the 9 epics** | 10 |
| **R10** | `U-` | An **operational walkthrough** — 10 real journeys, 121 enumerated steps, journey-first not document-first | 6 |
| **R11** | `Y-` | The **exception and unhappy paths** — 61 exceptions walked to an outcome | 9 |
| **R12** | `Z-` | The **lifecycle of the data itself** — go-live, opening balances, amendment, freezing, retirement, disposal | 10 |
| **R13** | `K-` | **Non-functional** — scale, concurrency, observability, security, degraded mode, DR, performance | 6 |
| **R14** | `O-` | **Re-verification** against the live `classic` checkout and the sibling `accounting` / `classic-issues` sets | 7 |
| **R15** | `J-` | **Competitor round 2** — current 2026 feature sets, web-verified, against the 236-row benchmark | 8 |
| | | **Total** | **62** |

**The governing rule, stated to every lens before it read anything:** *"Round 1 already ran seven
lenses and dispositioned 575 findings. Your job is to find what those seven did NOT. Grep before you
file. A finding that restates round 1 is worse than no finding, because it inflates a register the
implementation team has to read."* Every lens was required to produce a `§ Refused` section.

### 1.1 The count, computed

```bash
cd /Users/bbhushan/work/git/workspace/warehouse-issues
for p in Q:R8 H:R9 U:R10 Y:R11 Z:R12 K:R13 O:R14 J:R15; do
  pre=${p%%:*}; grep -c "^### \`$pre-" docs/reviews/${p##*:}-*.md; done | paste -sd+ | bc
# -> 62

grep -hoE '^### `[QHUYZKOJ]-[0-9]{3}`.*\*\*(BLOCKER|MAJOR|MINOR)\*\*$' docs/reviews/R{8,9,1[0-5]}-*.md \
  | grep -oE '(BLOCKER|MAJOR|MINOR)' | sort | uniq -c
#  14 BLOCKER
#  31 MAJOR
#  17 MINOR
```

| | BLOCKER | MAJOR | MINOR | Total |
|---|---|---|---|---|
| R8 `Q-` | 2 | 2 | 2 | **6** |
| R9 `H-` | 0 | 6 | 4 | **10** |
| R10 `U-` | 3 | 2 | 1 | **6** |
| R11 `Y-` | 3 | 4 | 2 | **9** |
| R12 `Z-` | 2 | 6 | 2 | **10** |
| R13 `K-` | 1 | 4 | 1 | **6** |
| R14 `O-` | 2 | 3 | 2 | **7** |
| R15 `J-` | 1 | 4 | 3 | **8** |
| **Total** | **14** | **31** | **17** | **62** |

### 1.2 What was refused, which is the more important number

```bash
# rows in the eight `Refused` sections — table rows and top-level bullets
# (an upper bound on distinct candidates; some rows are multi-part)
```

**83 candidate findings were refused across the eight lenses** — more refusals than findings. The
refusals are in each lens's own `§ Refused` section with the round-1 finding or `X-` defect that
already owns them. Three of them are corrections a lens made to **its own draft** after checking:
R13 withdrew *"two concurrent reservations bypass the position row"* on discovering that
`quantity_available` is a writer-maintained projection with its own `CHECK`, and recorded it in
*What I checked and found sound* instead. That ratio is the evidence that round 2 is not padding.

### 1.3 The headline

Round 1 asked whether the design covers the market. It does. Round 2 asked whether the design can be
**built**, **operated** and **lived with**, and the answers are less comfortable:

- **`0 of 70`** v1 task files are hand-off-ready with no partials (R8). `19 of 70` clear if partials
  are allowed. **`44 of 70`** would clear if just `Q-001` and `Q-002` were closed.
- **`0 of 68`** P3–P6 task files, and **`0 of 9`** epics, carry a build order (R9).
- **270 tables** are named in `DATA-MODEL.md`; the count of `CREATE TABLE` statements anywhere in the
  set is **0** (R9 `H-002`). The house prior art in `classic-issues` carries **101** of them
  (R14 `O-007`) — the local bar was already met once and regressed from.
- **31 status-bearing tables in P3–P6, 0 enumerated state machines** (R9 `H-004`); `status` has no
  declared domain for **30 v1 tables and 38 v1 screens** (R8 `Q-002`).
- Of 61 exceptions walked, **36 (59.0%)** are specified enough to code; 13 are named without an
  outcome and 12 are absent (R11).
- A customer **can** be taken live, and **cannot survive 1 April of year two** — the number series
  cannot reset (R12 `Z-002`).

---

## §2 · The disposition of all 62

**The buckets.** `FOLD-TASK` — the finding's content is added to an existing task file, which is the
default and the cheapest. `FOLD-DOC` — it belongs in a reference document or a phase epic, not a task.
`NEW-FR` — the set has no requirement to hang it on, so an `FR-` row must be written first and the
task line follows from it. `NEW-TASK` — it needs a task file of its own. `DECISION` — it is not an
authoring gap at all; a human must choose, and no amount of writing substitutes.

| Bucket | Count | Findings |
|---|---|---|
| `FOLD-TASK` | 40 | the majority — see the register |
| `FOLD-DOC` | 11 | `H-001` `H-003` `H-004` `H-006` `H-007` `H-008` `Z-004` `O-007` `J-004` `J-006` `J-008` |
| `NEW-FR` | 4 | `U-005` `Y-002` `Y-003` `K-002` |
| `NEW-TASK` | 1 | `Z-007` |
| `DECISION` | 6 | `Q-003` `H-002` `U-003` `O-001` `J-003` `J-005` |
| **Total** | **62** | |

**`NEW-TASK` is 1 of 62, and that is the finding this register wants to make.** Round 1's
`GAP-REGISTER.md` §4 proposed four new tasks out of 575. Round 2 proposes one out of 62. The set's
138 tasks are, with one exception, the *right* tasks — what round 2 found is that they are
under-specified inside, not missing from the outside. That is a much cheaper problem, and it is why
almost every disposition below is a line to add to a file that already exists.

### 2.1 The register

| Id | Sev | What it is | Bucket | Lands in |
|---|---|---|---|---|
| `Q-001` | BLOCKER | The P2 wave's 25 verb permissions, their dependency rows and their menu grants have no migration to live in | FOLD-TASK | `P2-29` |
| `Q-002` | BLOCKER | `status` has no declared domain for 30 v1 tables and 38 v1 screens, because §1.12 defers it to a §1.4 that only defines the masters' soft-delete flag | FOLD-TASK | `P0-01` |
| `Q-003` | MAJOR | Whether AUDITOR receives `:export` is answered both ways by four documents each, and it lands in a forward-only permission migration | **DECISION** | a new `OD-` row |
| `Q-004` | MAJOR | 115 of 136 v1 screens carry no per-column `sortable` / `default-visible` decision, and both are migration content | FOLD-TASK | `P2-29`, `P0-15`, `P1-20` |
| `Q-005` | MINOR | P2's non-grid i18n — modal titles, verb-button labels, validation messages, menu leaves — has no owner and no key-diff gate | FOLD-TASK | `P2-29` |
| `Q-006` | MINOR | Seven v1 tasks cite no failure-path scenario, and two of them are the India statutory tasks | FOLD-TASK | `P2-IN-01`, `P2-IN-02` |
| `H-001` | MAJOR | The P5 and P6 verb permissions exist in no document and in no task file | FOLD-DOC | `BUILD-SPEC-SCREENS.md` §10.2 |
| `H-002` | MAJOR | No table in the design set carries a column-level DDL specification | **DECISION** | then `DATA-MODEL.md` |
| `H-003` | MAJOR | The dependency graph and the critical path stop at P1; 68 tasks have no build order | FOLD-DOC | `IMPLEMENTATION-PLAN.md` §3.8 |
| `H-004` | MAJOR | Not one entity has an enumerated state machine — 31 status-bearing tables in P3–P6, 0 transitions | FOLD-DOC | `BUILD-SPEC-SCREENS.md` §0.11 |
| `H-005` | MAJOR | Half the v1.1 exit criterion depends on a v1 schema fact that neither owning task states | FOLD-TASK | `P2-04`, `P3-12` |
| `H-006` | MAJOR | `08-EPIC-p6`'s migration table allocates a band that `p6-08.md` explicitly withdraws, and its "re-derived" command output is stale | FOLD-DOC | `08-EPIC-p6.md` |
| `H-007` | MINOR | `07-EPIC-p5` miscounts its own scenario-authoring list and calls two claimed migration numbers unclaimed | FOLD-DOC | `07-EPIC-p5.md` |
| `H-008` | MINOR | Invariant and amendment carriage collapses after P0; `A-3` reaches no phase epic | FOLD-DOC | four phase epics |
| `H-009` | MINOR | The v3 zero-commit ratchet is stated in two forms in the same file; the executable one is not the one the epic quotes | FOLD-TASK | `P6-08` + `08-EPIC-p6.md` |
| `H-010` | MINOR | Four P3/P4 tasks state no mobile verdict, which the set's own Definition of done calls a defect | FOLD-TASK | four P3/P4 tasks |
| `U-001` | BLOCKER | No carton can be created in v1: the only screen with a create/seal action is v1.1, and `P2-11` closes the gap with an action that exists in no screen co… | FOLD-TASK | `P2-11` |
| `U-002` | BLOCKER | In v1 nothing tells anyone anything: the alert rule / recipient / event substrate is v1.1 while six v1 requirements — two of them P0 — mandate a notific… | FOLD-TASK | `P3-16`, re-phased to P2 |
| `U-003` | BLOCKER | The v1 counter sale computes tax and takes payment inside a warehouse module — the losing side of `OD-9` and a direct contradiction of `FR-274` — and `O… | **DECISION** | `OD-9`'s deadline |
| `U-004` | MAJOR | `wh_dock_appointments.arrived_at` was pulled into v1 *because it cannot be backfilled*, and has no v1 writer on any surface | FOLD-TASK | `P1-06` |
| `U-005` | MAJOR | The outbound journey has no closing event in v1: `delivered_at`, `pod_document_id` and the `deliveredAt` grid column exist in v1 and nothing writes them… | NEW-FR | `FR-447` then `P2-10` |
| `U-006` | MINOR | `WS-132 Print Jobs` ships in v1 with a `printerName` column and a `printerId` filter over `wh_printers`, which is v1.1 | FOLD-TASK | `P2-14` |
| `Y-001` | BLOCKER | `on_behalf_of_actor_id` is mandated on the movement, is absent from the movement header, and the movement header is `PNR-1` | FOLD-TASK | `P0-02` |
| `Y-002` | BLOCKER | A status change against stock that carries an open reservation has no stated outcome and no error code — and `FR-160`'s nightly expiry job is a status c… | NEW-FR | then `P0-05`, `P2-03` |
| `Y-003` | BLOCKER | Cancelling after stock has been picked to staging has no de-stage path: the units become an unallocatable, unreported balance | NEW-FR | then `P2-09` |
| `Y-004` | MAJOR | Work that is in flight has no abandonment clock, no reclaim and no signal — one root cause, four symptoms | FOLD-TASK | `P0-10` |
| `Y-005` | MAJOR | A wrong or unordered item on the dock has no rule and no reconciliation case type | FOLD-TASK | `P2-12` |
| `Y-006` | MAJOR | LPN split, merge and loss are entirely unspecified, while the LPN is a v1 ledger object with a status ladder | FOLD-TASK | `P1-07` |
| `Y-007` | MAJOR | There is no deactivation guard on a location, an owner or a warehouse that holds stock, while `FR-051` provides exactly that guard for an item | FOLD-TASK | `P1-05`, `P0-06` |
| `Y-008` | MINOR | Movements pending approval have a tile and an action but no filter, no clock, no job and no health signal | FOLD-TASK | `P0-02` |
| `Y-009` | MINOR | Stock found on the floor that nobody can identify has no entry path | FOLD-TASK | `P2-01` |
| `Z-001` | BLOCKER | Three of the set's five "most-specific-first" policy ladders cannot be expressed by their own tables, and two v1 acceptance scenarios are therefore unpa… | FOLD-TASK | `P1-03`, `P2-07` |
| `Z-002` | BLOCKER | `reset_policy` YEARLY/MONTHLY is unimplementable against `I-20`'s own unique index, nothing performs the reset, and the gaplessness assertion is false f… | FOLD-TASK | `P0-13` |
| `Z-003` | MAJOR | The import framework has create-and-reverse semantics only: no master can be bulk-amended, and a corrected re-import has no defined behaviour | FOLD-TASK | `P1-10` |
| `Z-004` | MAJOR | Fifty-one master screens, two immutability statements: the per-field freeze list does not exist | FOLD-DOC | `BUILD-SPEC-SCREENS.md` §2 + `P1-01`/`P1-02`/`P1-05` |
| `Z-005` | MAJOR | No catalogue value can ever be retired: the deactivation gate is undefined and, read against `L-2`, permanently closed | FOLD-TASK | `P0-04` |
| `Z-006` | MAJOR | The archive's cut-off has no retention policy to read outside India, and nothing is ever disposed of | FOLD-TASK | `P4-09`, `P6-01` |
| `Z-007` | MAJOR | Two duplicate items, or two duplicate counterparties, have no merge path — and a 40,000-SKU import against `uk(owner_id, sku)` produces them on day one | **NEW TASK** | **`P1-21`** |
| `Z-008` | MAJOR | `P2-19` delegates opening-stock reversal to a framework path whose own acceptance criterion refuses it | FOLD-TASK | `P2-19` |
| `Z-009` | MINOR | No master load order is stated, and the cut-over checklist collapses it into one tick | FOLD-TASK | `P2-19` |
| `Z-010` | MINOR | Not one operational role is seeded: storekeeper, picker, supervisor, stock controller and 3PL client exist as actors and as nothing else | FOLD-TASK | `P0-15` |
| `K-001` | BLOCKER | No job in the product has an execution contract: nothing declares when a job should run, nothing stops two instances running it, and a job that never fi… | FOLD-TASK | `P0-13` |
| `K-002` | MAJOR | Cost and value are visible to anyone who can open the screen: the only suppression rule in the set is `L-14`'s owner-type rule, and there is no actor-si… | NEW-FR | then `P1-18` |
| `K-003` | MAJOR | Eight performance numbers, zero measurement methods and zero load tests — and `p0-16`'s own acceptance criterion demands the method it does not supply | FOLD-TASK | `P0-16` |
| `K-004` | MAJOR | The position row is defended by an optimistic `@Version` and nothing says what happens when it loses: no retry, no backoff, no stated caller-visible out… | FOLD-TASK | `P0-03` |
| `K-005` | MAJOR | Every outbox and queue signal in the set is failure-shaped; none is lag-shaped, so a consumer that is falling behind — or a subscription somebody disabl… | FOLD-TASK | `P0-11` |
| `K-006` | MINOR | `occurred_at` has a ceiling and no floor, and it is the partition key — so a late-arriving movement dated before the oldest live partition fails as a ra… | FOLD-TASK | `P0-02` |
| `O-001` | BLOCKER | The `accounting` design set has no third install state, records warehouse as ABSENT, and holds a Mode C invariant that `D-6` contradicts — and the stand… | **DECISION** | amend `OD-1` |
| `O-002` | BLOCKER | `acc_posting_rule_lines.account_strategy` is a closed ten-value vocabulary with no strategy keyed on reason code, item group or owner type — so the clas… | FOLD-TASK | `P0-12` |
| `O-003` | MAJOR | The handover status ladder and `acc_source_documents`' ladder do not map: three accounting states have no warehouse counterpart, and the column is `IRR-… | FOLD-TASK | `P0-12`, `P2-18` |
| `O-004` | MAJOR | The set names only `permission_dependencies` — the registry that grants nothing at runtime — and never `menu_permission_dependencies`, which is the live… | FOLD-TASK | `P0-01` |
| `O-005` | MAJOR | Two P0/P1 task files carry `branches.owner_type` as a Trap — a claim the set's own `PD-1` and `MI-4` declare void | FOLD-TASK | `P0-06`, `P1-05` |
| `O-006` | MINOR | The set states five different values for two registry counts across four documents; live is 218 and 240, and only one document knows its own command is… | FOLD-TASK | `P0-01` |
| `O-007` | MINOR | The house prior art in `classic-issues` carries 101 full `CREATE TABLE` blocks; the entire warehouse task set carries 17 — the local standard for DDL ri… | FOLD-DOC | `H-002`'s disposition |
| `J-001` | BLOCKER | `whb_transport_details` has no Ship-To GSTIN, and from 1 August 2026 the NIC API rejects a payload without one | FOLD-TASK | `P0-03` |
| `J-002` | MAJOR | The India pack's statutory watch-list is fifteen months stale — five in-force GSTN changes are absent | FOLD-TASK | the `P2-IN` e-way bill task |
| `J-003` | MAJOR | The set has no stated position on AI, in a year when it is the first line of the RFP | **DECISION** | a stated AI position |
| `J-004` | MAJOR | The benchmark's sales-facing loss tables are stale after `A-1`…`A-4` in nine places — `X-050` names four | FOLD-DOC | `COMPETITOR-BENCHMARK.md` (`X-050`) |
| `J-005` | MAJOR | `doc-ocr-ai` — an OCR module this company already ships — is never named as a functional dependency | **DECISION** | the `doc-ocr-ai` seam |
| `J-006` | MINOR | §2.3 scores the ERP column `○` for vehicle fitment while its own neighbouring rows carry `◐ (Epicor ●)` | FOLD-DOC | `COMPETITOR-BENCHMARK.md` |
| `J-007` | MINOR | WhatsApp document delivery appears in none of the 236 rows, though Marg, Busy and Vyapar ship it and the platform already carries the provider | FOLD-TASK | the P2 printing task |
| `J-008` | MINOR | §9.2's open `?` on SAP LE-WM's maintenance status is now answerable | FOLD-DOC | `COMPETITOR-BENCHMARK.md` |

---

## §3 · The deadline-ordered gate list — read this one first

A disposition tells you *where* a finding goes. It does not tell you *when it stops being free*. This
is the section the P0 builder needs, because the set's own `PNR-1` is migration **`V500030`** — the
`whb_stock_movements` header and the position unique key — and after `L-2` seals that table
append-only, a missing column on it is not a schema change, it is a history you never recorded.

Ordered by the migration at which the finding becomes expensive:

| # | Gate | Finding | What must be decided or added before it |
|---|---|---|---|
| 1 | **`V500020`** `whb_number_series_issued` | `Z-002` **BLOCKER** | `period_key VARCHAR(10) NOT NULL`, and `I-20`'s index becomes `uk(series_id, period_key, issued_value)`. Without it `reset_policy` YEARLY/MONTHLY is unimplementable against the set's own unique index, and the gaplessness assertion is false for every resetting series. The table is not `L-2`-sealed, so a later migration *can* add it — but the India statutory challan series uses this generator |
| 2 | **`V500030` = `PNR-1`** movement header | `Y-001` **BLOCKER** | `on_behalf_of_actor_id`. It is *mandated on the movement* by the set's own requirement, absent from the header, and after the append-only seal every movement already posted has no answer for "who was this done on behalf of" — **unbackfillable, not merely awkward** |
| 3 | **`V500030` = `PNR-1`** movement header | `O-003` **MAJOR** | The `posting_status` `CHECK` vocabulary. `acc_source_documents` carries `SUPERSEDED`, `PENDING_PREDECESSOR` and `DISCARDED`; `posting_status` has no counterpart, so a discarded envelope sits at `PENDING` forever in the queue `idx_whb_stock_movements_posting` drives. The column is `IRR-41` and it ships at `PNR-1` |
| 4 | **every table's DDL migration** | `H-002` **MAJOR** · `Q-002` **BLOCKER** | Column-level DDL — types, nullability, defaults, and **numeric scale**, which cannot be widened on a populated ledger without a rewrite; and the `status` domain, whose `CHECK` lands with each table |
| 5 | **`V500043`** `whb_job_runs` | `K-001` **BLOCKER** | `scheduled_for` and the execution contract. Nine v1 dated obligations have no declaration of when they run, nothing stops two instances, and a job that never fires is invisible on every surface — including the `L-4` drift rebuild, which is the only control that makes the position cache trustworthy, and the monthly partition-creation job, whose silence stops every `POST /movements` at a month boundary |
| 6 | **the `whb_` band, before base freezes** | `J-001` **BLOCKER** | **Ship-To GSTIN** on `whb_transport_details`. GSTN Advisory 664 made it mandatory from **1 August 2026**; `A-4` puts e-way-bill generation in v1/P2-IN, so a v1 India install cannot legally move goods without it. *(R15 proposes `P0-03` as the owning task and says to confirm the exact one — do that before editing.)* |
| 7 | **`V501000`** the permission migration | `Q-003` **MAJOR** · `K-002` **MAJOR** | Whether AUDITOR receives `:export` (answered both ways by four documents each), and reserving `warehouse:cost:view`. Permission **names** are `IRR-63`-class: forward-only, and a grant added later needs a new migration in every deployed environment |
| 8 | **`V510033`** | `H-005` **MAJOR** | The v1 schema fact half of the v1.1 exit criterion, which neither owning task states |
| 9 | **`V511000`** | `Q-001` **BLOCKER** | The P2 wave's 25 verb permissions, their dependency rows and their menu grants — which today have **no migration to live in** |
| 10 | **`V520100`–`V520149`** (`P2-25`) | `U-003` **BLOCKER** | **`OD-9`'s deadline is wrong.** It reads *"Before `P2-IN`"*, but `P2-25` builds the table that implements the option `OD-9` rejected — a v1 counter sale that computes tax and takes payment inside a warehouse module, contradicting `FR-274`. The deadline must move to *"Before `P2-25`"* |
| 11 | **`V524xxx`** | `H-006` **MAJOR** | `08-EPIC-p6`'s migration table allocates a band `p6-08.md` explicitly withdraws. Free today; irreversible the day a `V524xxx` file is committed |
| 12 | **accounting `V600136`/`V600137`, in accounting's P1** | `O-001` **BLOCKER** | The reciprocal half of `D-6`. The accounting set has **no third install state**, records warehouse as ABSENT, and holds a Mode C invariant — *"must require zero change to `accounting-base`"* — that `D-6` contradicts. `OD-1`'s stated deadline of *"before accounting's P3"* is **one phase late**. Neither migration exists in live `classic` yet, so the edit is still free **today** |

**Two of these are irreversible as *data* rather than as schema**, which is worse because no migration
fixes them: `U-004` (`wh_dock_appointments.arrived_at` was pulled into v1 *because it cannot be
backfilled* and has no v1 writer on any surface) and `U-002` (v1 mandates notifications in six
requirements, two of them P0, while the alert/recipient/event substrate is v1.1 — the events not
raised are unrecoverable).

---

## §4 · The edit list, grouped by what you open

Round 2's output is overwhelmingly *lines to add to files that already exist*. Grouped by target, so
the work can be done in one pass per file rather than one pass per finding:

| Target | Findings | Nature of the edit |
|---|---|---|
| `p0-01.md` (permissions & menus) | `Q-002` `O-004` `O-006` | the `status` domain requirement; `menu_permission_dependencies` — the registry that actually grants at runtime, which the set names **zero** times while naming the inert `permission_dependencies` 26 times; and five wrong registry counts |
| `p0-02.md` (`PNR-1`, the movement header) | `Y-001` `Y-008` `K-006` | `on_behalf_of_actor_id`; the `approvalStatus` filter and clock; `occurred_at`'s missing floor |
| `p0-03.md` (masters / concurrency) | `K-004` `J-001` `K-003` | the optimistic-lock **retry** contract and `409 POSITION_CONTENTION`; Ship-To GSTIN; named performance assertions |
| `p0-04.md` (catalogues) | `Z-005` `Y-003` `Y-006` `Y-009` | deactivation is a retirement, not a delete; the `INTERNAL`-direction movement types the set's own seed lists omit |
| `p0-11.md` (outbox) | `K-005` | lag-shaped signals — every outbox signal in the set is failure-shaped, so a consumer falling behind is invisible and a 3PL client is under-billed for a month |
| `p0-12.md` (the accounting seam) | `O-002` `O-003` | `account_strategy` cannot resolve the classification quad warehouse hands over — write-off, shrinkage and customer-owned adjustments all land in one account **and the totals still balance**; and the status-ladder mapping |
| `p0-13.md` (number series, jobs) | `Z-002` `K-001` | `period_key`; the job execution contract |
| `p0-15.md` / `p0-16.md` | `Z-010` `K-003` | seed four operational role bundles; performance measurement methods |
| `p1-05.md` / `p0-06.md` (locations, sites) | `Y-007` `O-005` `Z-006` | the deactivation guard for a location/owner/warehouse holding stock; **delete the void `branches.owner_type` Trap** and state the real consequence — `branch_code` is globally unique, so a warehouse site code shares a namespace with every dealer showroom |
| `p1-10.md` (import framework) | `Z-003` `Z-008` | `CREATE_ONLY`/`UPDATE_ONLY`/`UPSERT` modes with a stated match key — today no master can be bulk-**amended**; and stop refusing the opening-stock reversal `P2-19` delegates to it |
| `p2-19.md` (cutover) | `Z-008` `Z-009` | opening-stock reversal as an `L-3` ledger reversal; a per-master load order instead of one "masters loaded" tick |
| `p2-29.md` (grids / i18n) | `Q-001` `Q-004` `Q-005` | the P2 permission migration; 115 of 136 v1 screens' per-column `sortable`/`default-visible`; P2's non-grid i18n |
| `BUILD-SPEC-SCREENS.md` | `H-001` `H-004` `Z-004` | §10.2 gains the P5/P6 verb permissions; a new **§0.11 State ladders**; a per-master **freeze list** — 51 master screens, **2** immutability statements in the whole build spec. `H-004` landed as **§0.11** and `Z-004` as **§0.12** with its nine-field minimum set, plus acceptance criteria in `P1-01`, `P1-02` and `P1-05` |
| `DATA-MODEL.md` | `H-002` `O-007` `Z-001` | column-level DDL; the policy-ladder tables that cannot express their own ladders. **`O-007` folds into `H-002`'s disposition and files no task of its own:** the bar has already been met inside `classic-issues` — the six assets phase documents carry **101** `CREATE TABLE` blocks (`grep -ci 'CREATE TABLE' assets/docs/PHASE*.md`), and the warehouse prior art at `classic-issues/warehouse-base/docs/spi/WMS_DATABASE_DESIGN.md` already contains **72** — so the remedy is to **lift and correct**, not to author from nothing |
| `IMPLEMENTATION-PLAN.md` | `H-003` `J-002` | a build order for 68 tasks; the India statutory watch-list, fifteen months stale |
| `COMPETITOR-BENCHMARK.md` | `J-004` `J-006` `J-008` | the nine stale "where we lose" rows — this discharges the part of `X-050` that `X-050` does not name. **Applied 2026-09-02:** all nine rows plus the two consequential edits (§8.2's returns clause; §9 rows 1, 2 and 4 → RESOLVED), §2.3's Epicor cell and W1 (`J-006`), §9.2's LE-WM entry and a §5.2 Stock Room Management paragraph (`J-008`), and two same-class corrections `J-004` did not name (§5.2's apparel clause, §9's preamble). `X-050`'s Status records the full list and what stays open — the four other documents still at zero `A-n` citations |
| the phase epics | `H-006` `H-007` `H-008` `H-009` | band corrections, miscounts, and invariant/amendment carriage, which collapses after P0 |

---

## §5 · New tasks

> **Status, 2026-09-02 — all five are now authored.** This section was written as a proposal and is
> kept as written; what follows each proposal is the file that discharges it. `issues/p1-21.md`,
> `issues/p3-24.md`, `issues/p4-13.md`, `issues/p5-22.md` and `issues/p5-23.md` exist, carry their
> `IMPLEMENTATION-PLAN.md` §2 rows, own `FR-447`–`FR-459`, and pass all twelve checks. The task count
> moved **138 → 143** and the table count **301 → 314**. `P4-13` is authored **and still gated** — its
> file opens by saying so; see §6 decision 4.

### 5.1 The one new task round 2 requires

**`P1-21` — master merge** (`Z-007`, MAJOR). Two duplicate items, or two duplicate counterparties,
have **no merge path**, and a 40,000-SKU import against `uk(owner_id, sku)` produces duplicates on day
one. The task contains: a `whb_master_merges` record; a pre-check screen listing everything that
references the loser; for items, a **stock transfer to the survivor posted as a real movement through
the port** with a dedicated reason code — never a re-pointing of history, which `L-2` forbids;
deactivation of the loser with a scan redirect; and an explicit **refusal** to merge where the two rows
differ in `base_uom_code`, `lot_control_mode` or `serial_control_mode`.

`WONTFIX` for v1 is a legitimate answer here. **Silence is not**, because the implementation team will
otherwise do it in `psql` against an append-only ledger.

**Authored as [`issues/p1-21.md`](../issues/p1-21.md)** — `warehouse-base`, `V500055` (`WHB-55`,
`whb_master_merges`), owning `FR-451`, closing `Z-007`. The refusal list and the *"never
`UPDATE whb_stock_movement_lines SET item_id = …`"* trap are in the file verbatim.

### 5.2 The four tasks round 1 already proposed, still unwritten

`GAP-REGISTER.md` §4.1 proposed these and they have not been authored. Round 2 does not change their
scope; `J-005` and `K-002` add weight to two of them:

| Task | What it is | Round-2 pressure |
|---|---|---|
| `P4-13` | regulated-goods licence pack | gated on the `S-035` pharma decision — see §6 |
| `P3-24` | GS1 identity | — |
| `P5-22` | integration surface (API keys, webhooks, rate limits) | `K-005`'s lag signals and `S-097` both land here |
| `P5-23` | supplier claim register | `Y-005`'s wrong-item-on-the-dock path feeds it |

**All four are now authored.** What each one landed as:

| Task | File | Module · migration | Owns | Closes |
|---|---|---|---|---|
| `P3-24` | [`issues/p3-24.md`](../issues/p3-24.md) | `warehouse-base` · `V500056` (`WHB-56`) | `FR-452`–`FR-455` | `S-005` `S-010` `S-017` `S-049` |
| `P4-13` | [`issues/p4-13.md`](../issues/p4-13.md) | `warehouse-india` · `V540182` (`WIN-23`) | `FR-456` `FR-457` | `S-035` `F-073` `X-013` |
| `P5-22` | [`issues/p5-22.md`](../issues/p5-22.md) | `warehouse-base` · `V500066` (`WHB-67`) | `FR-458` | `S-097` `K-005` `OD-8` |
| `P5-23` | [`issues/p5-23.md`](../issues/p5-23.md) | `warehouse` · `V510216` (`WH-116`) | `FR-459` | `E-081` `Y-005` |

**Two authoring decisions are recorded rather than left to be rediscovered.** `P4-13` is
`warehouse-india`, **not** an adapter — a stated divergence from `S-035`'s `adapter-pharma` and
`F-073`'s `warehouse-adapter-pharma`, because the objects are licences under Indian law and `D-2`
gives licence tables the india band. And `P5-22`'s migration is `V500066` owned by **`WHB-67`**:
`WHB-66` is already allocated at `V500100`, and `DECISIONS.md` §7.4 forbids renumbering an allocated
id, so the id and the version deliberately do not run in step there.

### 5.3 New requirement rows (`NEW-FR`)

Four findings have no requirement to hang on. Each needs one `FR-` row written **before** the task
line, because a task line citing no requirement is exactly the shape `check-10` exists to catch:

| Finding | Requirement to write | Then folds into |
|---|---|---|
| `U-005` | `FR-447` — *delivery is confirmed, not inferred*: `WS-105` gains a **Confirm delivery** action in v1 (the driver-side ePOD stays `logistics` at v3) | `P2-10`, and a scenario **authored by that task** at the next free id |
| `Y-002` | a status change against stock carrying an open reservation has a stated outcome and an error code — and `FR-160`'s nightly expiry job **is** a status change | `P0-05`, `P2-03` |
| `Y-003` | cancelling after stock is picked to staging has a de-stage path — today the units become an unallocatable, unreported balance | `P2-09` |
| `K-002` | cost and value are suppressed by **actor**, not only by owner type — the guard is response-DTO omission, because platform's `role_field_configs` is client-side only | `P1-18` |

**All four are written**, as `FR-447`–`FR-450` in `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` §6.27, and
each is folded into its task on **both** sides — the task file's `## Requirements closed` and the
plan's §2 `Closes` cell — because `check-10` compares the two and a one-sided fold is exactly the
drift it exists to catch. Each task also gained a `> **Round-2 addition**` blockquote and at least one
acceptance bullet, so the obligation is visible to whoever picks the task up rather than only to
whoever reads this register.

**No scenario id was pre-allocated for any of them.** *(Superseded on 2026-09-02: `Q-006`'s remediation
did mint five — `WH-SC-301`–`WH-SC-305`, §3.21 — and moved the marker to `WH-SC-306`. The reasoning
below still governs the thirteen new requirements this paragraph is about; it is not a rule against
minting, it is a rule against minting a placeholder no task walks.)* `WH-SC-301` stayed what
`SCENARIO-CATALOGUE.md` §5 rule 3 says it is — the **next-free allocation marker**, fenced in some
thirty places — and the five task files say *"the scenario ids this task authors"* instead, the same
idiom `p5-13.md` uses for `WS-238`. Writing a literal `WH-SC-301` row would have required bumping
every one of those markers forward by one in the same commit, for no gain: the obligation is carried
by the task, and `SCENARIO-CATALOGUE.md` §4.2 §6.27 now lists all thirteen new requirements as
unproven so the coverage number stays honest (**375 of 459, 81.7%**) rather than silently improving.

---

## §6 · The six decisions a human must take

These cannot be authored around. Each is stated with its deadline and the cost of taking it late.

| # | Decision | Deadline | Why it cannot wait |
|---|---|---|---|
| **1** | **`OD-1` — the accounting reciprocal.** The accounting set must acknowledge `D-6`'s third install state, and its Mode C invariant *"zero change to `accounting-base`"* must be amended or `D-6` withdrawn | **accounting's P1**, not its P3 — `V600136`/`V600137` | `O-001`. Written into eleven warehouse documents and four task files with **no reciprocal commitment in the accounting repository**. Neither migration exists in live `classic` yet, so it is free today and expensive the day it ships |
| **2** | **`OD-9`'s deadline moves to *"Before `P2-25`"*** | before `V520100` | `U-003`. `P2-25` builds a v1 table that computes tax and takes payment inside a warehouse module — the losing side of `OD-9` and a direct contradiction of `FR-274` |
| **3** | **`OD-10` — is MRP a position-key dimension?** *(carried from round 1)* | **before `PNR-1` = `V500030`** | The tightest deadline in the whole programme. The full-grain position key is `L-5`; a dimension added after the seal is a rebuild of every position row |
| **4** | **`S-035` — pharma.** Build `P4-13`, or declare the segment declined in writing | before P4 planning | The one unowned BLOCKER in round 1's audit. "Not decided" ships as "not built" |
| **5** | **`Q-003` — does AUDITOR receive `:export`?** | `V501000` | Four documents say yes, four say no. Permission names are forward-only |
| **6** | **`J-003` — the set's position on AI**, and **`J-005` — whether `doc-ocr-ai` is a supplier-document capture source** | before the next sales conversation | `grep` for agentic/conversational/LLM/ML across 38,065 lines returns **0** while Manhattan, Blue Yonder, Infor, Cin7, Odoo and Unicommerce all ship one. The ask is a **refusal row with a reason** plus at most one narrow non-refused item (natural-language query over the immutable movement register). This is a documentation decision, not a phase |

**Two of these — 3 and 4 — are carried from round 1 unresolved.** They are restated here because a
decision that survives two review rounds without being taken is not pending, it is being avoided, and
`OD-10`'s deadline is the earliest migration in the programme.

---

## §7 · Traceability — how this register is kept true

`tools/check-design-set.py` was extended in the same commit as the lens documents so that round 2 is
governed exactly as round 1 is. The eight registers are declared in `REVIEWS`, `FINDING_DEF_RE`,
`REVIEW_LABEL` and `AUTHORITY_STEM`, and `FINDING_CITE_RE` accepts their letters.

```bash
cd /Users/bbhushan/work/git/workspace/warehouse-issues
python3 tools/check-design-set.py | tail -1
# -> 0 violations across 12 checks
```

- **check 7** now resolves every one of the 62 round-2 citations against its own authority, and found
  **zero** false positives from the eight new letters — `O-001` cannot be read as `OD-1`, and
  `WH-SC-nnn` cannot be read as an `H-` or `S-` finding, because the citation regex requires a hyphen
  immediately after the register letter.
- **check 11** asserts the eight registers collide with nothing, and it **demanded** the `DECISIONS.md`
  §6 rows before it would pass — which is the ratchet working as designed.
- Three next-free allocation markers (`FR-447`, `WH-SC-301` — now `WH-SC-306`, `WS-238`) are named by R9 and R10 as
  proposals and refusals, never as citations. Each carries a self-declared exemption in the house
  idiom — in the open, in the file, with a stated reason — rather than a silent path exclusion.

**The check-13 that `DESIGN-SET-DEFECTS.md` §5 asks for should be written against both registers.**
Its rule is *"every finding in `reviews/R1`–`R7` has a disposition row in `GAP-REGISTER.md` §2.5"*;
it must now also assert *"every finding in `reviews/R8`–`R15` has a disposition row in
`GAP-REGISTER-R2.md` §2.1"*. This register's §2.1 was generated mechanically from the lens headings,
so it is complete by construction today — check-13 is what keeps it complete tomorrow.

---

## §8 · The honest readiness statement

Round 1 closed with the claim that the design set covers its market. Round 2 does not dispute that,
and nothing found here reopens a segment verdict.

What round 2 changes is the readiness claim for **implementation**:

1. **The task set is right; the task files are thin.** 1 new task out of 62 findings. The other 61 are
   lines to add to files that already exist, and 40 of them are one file each. This is a **days**
   problem, not a re-plan.
2. **Three things must be decided before `V500030` is written**, and one of them (`OD-10`) has been
   open across two review rounds. `PNR-1` is the only genuinely unforgiving moment in the programme.
3. **The reciprocal half of `D-6` does not exist.** The most valuable single output of round 2 is
   `O-001`: an edit that must be made in the **accounting** repository, at a deadline one phase
   earlier than `OD-1` currently states, and it is free only until `V600136` ships.
4. **A customer can be taken live and cannot survive 1 April of year two.** `Z-002` is the sharpest
   answer to the product owner's actual question, because it is exactly the class of thing that is
   invisible at UAT and unavoidable at the fiscal-year boundary.
5. **Four gaps are irreversible as data rather than as schema** — `Y-001`, `U-004`, `U-002`, and the
   numeric scales inside `H-002`. No later migration repairs them; they are simply history the product
   never recorded.

**The shortest true statement.** The set is closer to buildable than any comparable design set in this
programme, and it is not buildable today: a builder handed `p0-01.md` cannot write the first migration
without inventing the `status` domain, the column types and the permission migration that three of
these findings say are missing. Close `Q-001`, `Q-002` and `H-002` and **44 of 70** v1 tasks clear
their own bar. Close the twelve gates in §3 in order, take the six decisions in §6, and the
"we should have thought of this earlier" surface that round 2 could find is closed.
