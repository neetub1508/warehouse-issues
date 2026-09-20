# Open decisions — resolved

> **Current adopted amendment (2026-09-11):** [Global settings and resolved behaviour](GLOBAL-SETTINGS-DECISIONS.md) supplies defaults, scoped choices, resolved OD answers and acceptance cases. Earlier open/escalated or contradictory wording is historical where explicitly superseded there. Implement these answers; do not re-ask the same design questions.


**Date resolved: 2026-09-03.** Nine of the fifteen `OD-` rows in
[`DECISIONS.md`](DECISIONS.md) §3 are **decided**. Six remain open — **four escalated as business
calls** (`OD-1`, `OD-3`, `OD-8`, `OD-9`) and **two held by schedule for v3** (`OD-2`, `OD-4`) —
together with the design set's one unowned BLOCKER, `S-035`. Two new open decisions, `OD-16` and `OD-17`, are
**allocated by this document and escalated with it** — both move the v1 cut line, which is a product
call and not a technical one.

This page is the record. `DECISIONS.md` §3 carries the one-line state per row; this carries the
reasoning, the cost of being wrong, the downstream edits each decision owes, and the deadline each
one clears.

> **The instruction this executes:** *adopt the recommendations for the technical decisions;
> escalate only the genuine business calls.* Every row below is sorted into exactly one of those two
> buckets, and the sorting rule is stated: **a recommendation is technical when this design set can
> execute it inside this repository. It is a business call when it asks another team to build
> something, another repository to change, a segment to be served or declined, or the v1 cut line to
> move.** By that rule `OD-8` escalates — its recommendation is a request to the platform team —
> while its warehouse-side fallback is adopted so that `P0-08` is not blocked on someone else's
> roadmap.

**Three verifications contradicted a premise the set has been carrying.** Each is stated loudly
below rather than reconciled quietly:

1. **`OD-11`'s deadline in `DECISIONS.md` §3 was wrong** — it read *"Before `P2` valuation"* while
   `PORT-AND-ADAPTER-CONTRACT.md:2018` and `IMPLEMENTATION-PLAN.md:1319` both put it before
   `P0-02`. That is why the count of decisions gating `P0-02` computed as five and is really **six**.
2. **`OD-16`'s premise — *"zero exchange-rate sources monorepo-wide"* — is now FALSE.** There is
   one, it shipped since the review was written, and it is in `accounting-base`. The recommendation
   survives; the evidence for it changes. See §4.1.
3. **`O-001`'s window is still open but narrowing.** `accounting-base` has gone from 24 migrations
   to **32** in the live checkout, and `V600141`/`V600142` — numbers *above* the `V600136` this set
   is waiting on — have already shipped. See §3.2.

---

## 1. Counts, computed

Every count on this page was produced by the command printed beside it (`DECISIONS.md` §7 rule 1).
All commands run from the repository root on 2026-09-03.

```bash
# Rows in the open-decision register before this edit → 15
grep -coE '^\| \*\*OD-[0-9]+\*\*' docs/DECISIONS.md

# the rows whose DEADLINE CELL (field 4) gates P0-02 / PNR-1 = V500030, the migration
# that cannot be taken back. The cell is read, not the whole row: OD-16's deadline mentions
# V500030 in passing and is not one of these gates (DECISIONS.md sec 7 rule 8).
awk -F'|' '/^\| \*\*OD-/ && $4 ~ /[Bb]efore [^.;]*(P0-02|PNR-1)/ {gsub(/[*` ]/,"",$2); printf "%s ", $2}' docs/DECISIONS.md
# before this edit -> OD-10 OD-12 OD-14 OD-7 OD-1   (five; OD-11's deadline cell was wrong, see sec 6.1)
# after  this edit -> OD-10 OD-12 OD-14 OD-11 OD-7 OD-1   (six)

# Round-3 finding registers and their sizes
for f in R16:RA R17:RB R18:RC R19:RD R20:RE R21:RF; do r=${f%%:*}; p=${f##*:}; \
  printf '%s %s: ' "$r" "$p"; grep -cE "^###+ .*\`?${p}-[0-9]{3}\`?" docs/reviews/${r}-*.md; done
# → RA 8 · RB 9 · RC 9 · RD 8 · RE 8 · RF 10   = 52 round-3 findings

# accounting-base migrations in the live classic checkout, and whether V600136/V600137 have shipped
ls ../classic/accounting-base/backend/src/main/resources/db/migration/ | wc -l          # → 32
ls ../classic/accounting-base/backend/src/main/resources/db/migration/ | grep -c 600136 # → 0
```

**9 adopted · 4 escalated as business calls · 2 held by schedule for v3 · 2 newly allocated and
escalated · 1 unowned BLOCKER (`S-035`) escalated · 17 `OD-` rows · 0 rows deleted.**

---

### 1.1 Summary

| # | Question | State | The call |
|---|---|---|---|
| **OD-10** | Is MRP a dimension of the stock position? | **RESOLVED** | **No.** MRP lives on the lot. The position key stays at nine members |
| **OD-12** | Ledger partition key — `occurred_at` or `posting_date`? | **RESOLVED** | **`occurred_at`.** The as-at query and the rebuild run constantly; close runs monthly through an index |
| **OD-14** | Value conservation: a fifteenth invariant, or a behaviour column? | **RESOLVED** | **Invariant `L-15`**, scoped to `quantity = 0 AND unit_cost IS NOT NULL`, with a matching `I-21` |
| **OD-11** | Do value-only movements conserve value? | **RESOLVED** | **Yes**, and a `VALUE_OFFSET` virtual location carries the counter-side |
| **OD-7** | Precision — quantity, money, per-unit cost, percentage | **RESOLVED** | Adopt accounting's resolved set **verbatim**, plus one warehouse-only row: `conversion_factor_used DECIMAL(18,8)` |
| **OD-13** | The value-offset virtual location's code | **RESOLVED** | **`VALUE_OFFSET`**, added to `FR-084`'s seeded list |
| **OD-6** | Valuation-method scope in v1 | **RESOLVED** | **Weighted average + FIFO** in v1; standard cost v1.1; **LIFO never**, and never seeded |
| **OD-15** | Is the union valuation report built? | **RESOLVED** | **Not in v1.** Warehouse-only reports, with the separation stated on the report header |
| **OD-5** | Does the frontend re-close the vocabularies the backend opens? | **RESOLVED** | **It does not.** Catalogue-backed dropdowns fetch; string unions only for closed system vocabularies |
| **`S-035`** | Pharma: serve regulated goods, or decline the segment? | **ESCALATED** | Not ours. The design set's only unowned BLOCKER; silence is the option that fails |
| **OD-1** | The reciprocal accounting edits | **ESCALATED** | Owed to a different repository. Deadline **corrected** to accounting **P1**, and a **fourth** reciprocal edit folded in |
| **OD-3** | One database per customer, or shared multi-tenancy? | **ESCALATED** | Gates `P5-01`, the first task of P5 |
| **OD-9** | Does `warehouse` carry a tax engine? | **RESOLVED 2026-09-20** | **No — warehouse never computes tax.** Recommendation on the record taken by the owner; drops group **K**'s 6 conditional tables, India pack is **50** tables. See §3.4 |
| **OD-8** | How does an out-of-process consumer authenticate to the port? | **ESCALATED**, fallback adopted | The recommendation is a platform build. The v1 fallback is adopted so `P0-08` proceeds |
| **OD-2** | Does dealer vehicle inventory migrate onto the ledger? | **OPEN — v3** | Left open deliberately; deadline restated |
| **OD-4** | Who owns the shared counterparty master long-term? | **OPEN — v3** | Left open deliberately; deadline restated |
| **OD-16** | v1 foreign-currency costing has no exchange-rate source | **NEW · ESCALATED** | Recommended: v1 values in the install's base currency; the rate rides the line, frozen |
| **OD-17** | v1 prints an SSCC v1 can neither allocate nor read back | **NEW · ESCALATED** | Recommended: move the SSCC allocator into the v1 wave. Irreversible **in the physical world** |

---

## 2. Adopted — the nine technical decisions

Ordered by the deadline each clears, tightest first. Five of the nine gate `P0-02` / `V500030`,
which is `PNR-1` **and** `PNR-2` (`DATA-MODEL.md:2905`) and is unrecoverable once it runs.

### OD-10 — Is MRP a dimension of the stock position?

> **RESOLUTION — No. MRP belongs on the lot, not on the position key. The `L-5` key stays at its
> nine members and `V500030` may be written.**

**The question.** `FR-321` asks whether two MRP-labelled batches of one SKU must never merge. If they
must, MRP joins `whb_stock_positions`' unique key — and that key is set at `PNR-1`.

**The reasoning.**

- **The lot already carries it, and a lot is exactly the right home.** MRP is a printed attribute of
  a production batch, which is what a lot *is*. `FR-321`'s own segregation case — retail price
  labelling under Legal Metrology — is a lot-level question in every operating sense: the same
  physical carton carries one MRP, and that carton belongs to one lot.
- **A tenth key member is not free.** `L-5` already keys a position by
  `(company, owner, item, location, lot, serial, lpn, stock_status, duty_status)`. Every additional
  member widens the unique index, widens every position row, widens the `L-4` nightly rebuild that
  must reproduce the cache **exactly**, and appears in every position query plan in the product.
- **The counter-argument, stated fairly.** `P4-05` builds *MRP as a balance dimension* for
  non-batch-tracked items, with a stock-by-MRP report. For an item with no lot tracking there is no
  lot row to hang the MRP on, so under this resolution `P4-05` must read MRP from a lot that a
  non-batch-tracked item does not have. **That is a real gap and it is answered, not waved away:**
  an item whose MRP must be segregated is by definition batch-tracked, and `P4-05`'s task text
  already records the dependency (`IMPLEMENTATION-PLAN.md:541`: *"MRP is **not** in the position
  unique key — it lives on the lot, and this report reads it from there"*). The consequence below
  makes that binding rather than incidental.
- **The asymmetry decides it.** Adding a key member later is a re-key of every position row and a
  full rebuild. Removing one later is also a re-key. But an MRP that turns out to be needed can be
  reached through the lot; an MRP in the key that turns out not to be needed can never be taken out.
  The cheap direction is out of the key.

**What it costs if wrong.** If MRP genuinely must segregate stock for a non-lot item, the recovery is
a rebuild of `whb_stock_positions` against a key that `V500030`'s partitioned, `UPDATE`-sealed ledger
cannot supply — `IRR-01`/`WHB-30` make a post-hoc column `NULL` on every historical row with no
backfill path. The failure is silent: two MRP batches merge into one balance and no algorithm
separates them afterwards.

**What must change, and where.**

| Document | Edit | Owner |
|---|---|---|
| `DECISIONS.md` §3 | `OD-10` row moves to state **RESOLVED** and names this file | **this edit** |
| `DATA-MODEL.md` | Add to the `whb_lots` block: *MRP is a lot attribute, and the position key does not carry it (`OD-10`)*. State the rule where a reader looks for the column | **owed** — §5 |
| `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` | `FR-321` gains the answer inline, and §9's `OD-10` row moves to resolved | **owed** — §5 |
| `IRREVERSIBLE.md` | The `IRR` rows that name the position key gain *"nine members, `OD-10` resolved"* so a later author cannot reopen it by adding a tenth | **owed** — §5 |
| `issues/p4-05.md` | Its acceptance must state that an item whose MRP is segregated is batch-tracked, and refuse the report for a non-batch-tracked item rather than silently returning one bucket | **owed** — §5 |

**Deadline cleared:** `PNR-1` — migration `V500030` — *"the tightest deadline in the set."*
**Unblocks:** **`P0-02`** (one of six), and removes the tenth-member question from `P0-17` and
`P1-03`.

---

### OD-12 — The `whb_stock_movements` partition key: `occurred_at` or `posting_date`?

> **RESOLUTION — `PARTITION BY RANGE (occurred_at)`, monthly, as `FR-022` and `DATA-MODEL.md`
> `WHB-30` already specify. `posting_date` is served by a btree index, not by the partition.**

**The question.** `L-13` makes `occurred_at`, `recorded_at` and `posting_date` three different
columns, so this is a real choice and not a naming preference.
`DESIGN-SET-DEFECTS.md:1622` ranks it fourth and calls it *"the single most expensive thing on this
page to get wrong"*; a partition key cannot be added to a populated table without a rewrite, and
`V500030` is `PNR-1` **and** `PNR-2`.

**The losing argument, stated fairly, because it is substantive.**
`PLATFORM-DEPENDENCIES.md:808` (`PD-D5`) recommends `posting_date`, and it has three real points:

1. **Period close and the statutory register are `posting_date` queries.** `L-8` makes the ledger
   period-bound; the Rule 56 stock account and every close-period extract select by accounting date.
   Partitioning on `posting_date` prunes those to one partition.
2. **`posting_date` is monotonic with respect to what the business has committed.** `occurred_at` is
   **producer-supplied** (`L-13`) and can arrive arbitrarily late — offline replay and degraded-mode
   catch-up are explicit v1 behaviours. A partition keyed on `occurred_at` therefore receives inserts
   into historical partitions indefinitely, so **no partition can ever be declared closed**. That is
   the strongest form of the argument and it is not answered by choosing `occurred_at`; it is
   *accepted*.
3. **Archival and detach.** A partition that never stops receiving rows cannot be detached, compressed
   or moved to cheaper storage on a schedule.

**Why `occurred_at` wins anyway.**

- **Query frequency is not close.** The as-at position query and the `L-4` full rebuild are the
  ledger's two hot paths and both range over `occurred_at`. They run constantly — the rebuild nightly
  and the as-at query on every position screen, every allocation and every report. Period close runs
  **monthly**. Optimising the partition for the monthly query and the index for the constant one is
  the wrong way round.
- **Two documents specify it and one recommends against.** `FR-022` (`:139`) and `DATA-MODEL.md`
  `WHB-30` (`:2905`) both say `PARTITION BY RANGE (occurred_at)`, `IRR-62` records partitioning as
  irreversible, and `issues/p0-02.md` already builds it. `PD-D5` is a recommendation in a
  dependencies page. Following the two specifications means one document is amended; following the
  recommendation means three are, plus the task.
- **EPCIS is `occurred_at` by definition.** The v3 event-capture work (`P6`) keys on event time. A
  partition key chosen against it is chosen against the only future consumer whose access pattern is
  already known.
- **Point 2 is accepted and mitigated, not denied.** Late arrival into old partitions is real. The
  mitigation is that this ledger's retention obligation (`L-12`, full-retention genealogy in both
  directions) means partitions are **not** detached on a close schedule anyway; and a movement whose
  `occurred_at` falls in a locked period is refused by `L-8` regardless of which column partitions,
  so the late-arrival window is bounded by the period-lock policy, not by the partition key.

**What it costs if wrong.** A rewrite of the largest table in the product, on a deployment model that
`FR-022` states does not have the downtime for it. There is no incremental repair.

**What must change, and where.**

| Document | Edit | Owner |
|---|---|---|
| `DECISIONS.md` §3 | `OD-12` row moves to **RESOLVED** and names this file | **this edit** |
| `PLATFORM-DEPENDENCIES.md` `PD-D5` (`:808`) | **The losing document is amended, not left standing.** `PD-D5` must read: partition on `occurred_at` per `OD-12`; `posting_date` is served by a btree index on `(posting_date, company_id)` declared in the same migration; and the point-2 cost — no partition is ever closed — is recorded there as the accepted trade | **owed** — §5 |
| `issues/p0-02.md` | *Blocked on* loses the `OD-12` row; the index on `posting_date` becomes an acceptance line in `V500030`, not a later addition — `WHB-30` seals the table against `UPDATE`, and an index added later is fine, but the **column** is not | **owed** — §5 |
| `IMPLEMENTATION-PLAN.md` §2.10, §7, §11 | Stop carrying it as an unnumbered gate | **owed** — §5, and see §6.3 |

**Deadline cleared:** `PNR-1` = `PNR-2` = `V500030`.
**Unblocks:** **`P0-02`** (two of six).

---

### OD-14 — Is value conservation a fifteenth invariant, or a movement-type behaviour column?

> **RESOLUTION — A fifteenth invariant, `L-15`, scoped to lines where
> `quantity = 0 AND unit_cost IS NOT NULL`, with a matching enforceable constraint `I-21` in
> `DATA-MODEL.md` §6.3. It is not a behaviour column.**

**The question.** `PORT-AND-ADAPTER-CONTRACT.md:2018` states it and explicitly refuses to decide it:
*"Either a `value_balance_rule` behaviour column on `whb_movement_types`, or a fifteenth `L-`
invariant."* `DECISIONS.md` §4 stops at `L-14`; `DATA-MODEL.md` §6.3 stops at `I-20`.

**The reasoning.**

- **A behaviour column puts the ledger's correctness in data a migration can edit.** `D-10` is right
  that *extensible vocabularies* are catalogue tables with no CHECK — but conservation is not a
  vocabulary. It is the property `D-4` exists to guarantee. A `value_balance_rule` column means any
  install, support script or seed migration can switch conservation off for a movement type and
  nothing in the product will notice.
- **`L-1` has exactly this shape already** and is enforced by a deferred constraint trigger plus a
  service pre-check. `L-15` is the same mechanism over a different column, which makes it cheap to
  build and impossible to get subtly different.
- **The scope is the whole decision.** Unscoped value conservation is **wrong**: an ordinary issue
  moves quantity out and value with it, and the value column does not balance to zero across the
  movement — nor should it. The rule binds only where the movement carries **no quantity at all**,
  which is precisely the landed-cost / value-adjustment / assembly-completion shape. Hence the scope
  `quantity = 0 AND unit_cost IS NOT NULL`.
- **`OD-11` already recommended it.** What was missing was the row, not the argument.

**The precise statement, so a later wave can add the row without re-deciding anything.**

> **`L-15` · Value-only movements conserve value.** On a movement **all** of whose lines have
> `base_quantity = 0` and `unit_cost IS NOT NULL`, the signed `extended_cost` of the lines sums to
> **zero** in the install's base currency. The counter-side is the `VALUE_OFFSET` virtual location
> (`OD-13`), never an absent row — the same rule `L-1` applies to quantity. A movement mixing
> zero-quantity and non-zero-quantity lines is **refused**: it is two movements.
> *Enforced by:* deferred constraint trigger + service pre-check — identical to `L-1`.

> **`I-21` · (`DATA-MODEL.md` §6.3)** The database guard for `L-15`: a deferred constraint trigger on
> `whb_stock_movement_lines` that, for any movement whose lines are all `base_quantity = 0`, asserts
> `SUM(extended_cost) = 0` at commit, and rejects a movement whose lines are mixed. Sits in
> **`V500030`** with `I-1`…`I-17`, because `WHB-30` seals the table and a trigger added later does
> not retro-validate the rows written before it.

**What it costs if wrong.** Landed cost silently unbalances the value column. The symptom is a
valuation report that does not reconcile to the ledger by a small, growing, undrillable amount —
`FR-247`'s reconciliation trained into uselessness, which is the failure mode this design set is
written against.

**What must change, and where.**

| Document | Edit | Owner |
|---|---|---|
| `DECISIONS.md` §3 | `OD-14` row → **RESOLVED**, names this file | **this edit** |
| `DECISIONS.md` §6 | The invariant namespace records `L-15` as **allocated** and owed into §4 | **this edit** |
| `DECISIONS.md` §4 | Add the `L-15` row, verbatim from the block above | **owed** — §5. §4 is outside this edit's scope |
| `DATA-MODEL.md` §6.3 | Add the `I-21` row, verbatim from the block above; `WHB-30`'s invariant list gains `I-21` | **owed** — §5. **Do not edit `DATA-MODEL.md` in this wave** |
| `PORT-AND-ADAPTER-CONTRACT.md` §12.2 row 3 | Replace *"this document does not decide"* with the resolution | **owed** — §5 |
| `issues/p0-02.md`, `p2-17.md`, `p2-28.md`, `p3-11.md` | All four name `OD-14` as a dependency; each takes the resolved rule | **owed** — §5 |

**Deadline cleared:** before `P0-02` — the guard is a constraint on the table, not on a report.
**Unblocks:** **`P0-02`** (three of six), and `P2-17`, `P2-28`, `P3-11`.

---

### OD-11 — Do value-only movements conserve value?

> **RESOLUTION — Yes. A `VALUE_OFFSET` virtual location carries the counter-side, and `L-15`
> (`OD-14`) is the invariant that makes it testable.**

**The question.** `PORT-AND-ADAPTER-CONTRACT.md` `PC-12`: `L-1`…`L-14` conserve **quantity** only,
and a landed-cost movement posts `quantity = 0` with a value. `FR-084`'s seeded virtual-location list
(`:224`) has no value-offset row — it seeds `SUPPLIER`, `CUSTOMER`, `ADJUSTMENT`, `SCRAP`,
`PRODUCTION`, `IN_TRANSIT`, `COUNT_VARIANCE`, `OPENING_BALANCE`, `CONSUMED`, `JOB_WORKER` and nothing
that value can balance against.

**The reasoning.** This is `D-4` applied to the value column. A receipt balances against a virtual
location rather than against nothing (`IRR-05`, `:155`); a value-only movement has exactly the same
problem and there is no reason for it to have a different answer. Without the offset row, a
landed-cost movement has one line, which is not a movement under `D-4` — it is the single-sided log
`accessory_inventory_transactions` already is, and `D-4` exists to refuse.

**What it costs if wrong.** A one-line "movement" is not reversible under `L-3` and not rebuildable
under `L-4`, so the first landed-cost correction leaves the value column permanently off by the
amount of the correction.

**Deadline cleared:** **before `P0-02`.** `DECISIONS.md` §3 carried *"Before `P2` valuation"*, which
was **wrong** — `PORT-AND-ADAPTER-CONTRACT.md:2018` and `IMPLEMENTATION-PLAN.md:1319` both say before
`P0-02`, and the tighter deadline wins because a conservation invariant is a constraint on the table.
That correction is applied to §3 in this edit and is the sixth member of the `P0-02` gate set (§6.1).
**Unblocks:** **`P0-02`** (four of six), `P2-16`, `P2-17`, `P2-28`.

---

### OD-13 — The value-offset virtual location's code

> **RESOLUTION — `VALUE_OFFSET`. It is added to `FR-084`'s seeded list, seeded by `P1-05`'s
> `V500013`, and the two documents that use another name are amended.**

**The question.** `OD-11` and `P2-28` call it `VALUE_OFFSET`; `PORT-AND-ADAPTER-CONTRACT.md` `PC-12`
calls it `LANDED_COST_OFFSET` and offers reuse of an `ADJUSTMENT_OFFSET`-typed location.
**`FR-084` seeds none of the three.**

**The reasoning.**

- **`VALUE_OFFSET` does not presume *why* the value moved.** Landed cost is not its only use:
  a revaluation, a standard-cost variance and an assembly completion all post value with no
  quantity. `LANDED_COST_OFFSET` names one caller and would be a lie on the other three.
- **Reusing `ADJUSTMENT_OFFSET` is the worst option**, because it merges two different reports:
  quantity adjustments and value-only postings would then share a counter-side and no query
  separates them afterwards. `IRR-05` makes the virtual-location set a `PNR-1` decision.
- **Two documents already use `VALUE_OFFSET`**, so it is also the cheapest to converge on.

**What it costs if wrong.** Nothing structural — but the losing name must be *amended*, not left
standing, or the next author seeds two locations and the ledger balances value against two different
counter-sides.

**What must change, and where.**

| Document | Edit | Owner |
|---|---|---|
| `DECISIONS.md` §3 | `OD-13` row → **RESOLVED**, names this file | **this edit** |
| `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` `FR-084` (`:224`) | Add `VALUE_OFFSET` to the seeded list — an **eleventh** code — with `counts_as_on_hand = false` like the rest | **owed** — §5 |
| `PORT-AND-ADAPTER-CONTRACT.md` `PC-12` | Replace `LANDED_COST_OFFSET` and drop the `ADJUSTMENT_OFFSET` reuse option | **owed** — §5 |
| `DATA-MODEL.md` | The `whb_locations` / `whb_location_types` seed block gains the row | **owed** — §5 |
| `issues/p1-05.md` (`V500013`) | Seeds eleven virtual locations, not ten; acceptance updated | **owed** — §5 |
| `IRREVERSIBLE.md` `IRR-05` (`:155`) | Its virtual-location list gains `VALUE_OFFSET` | **owed** — §5 |

**Deadline cleared:** **before `P1-05` writes `V500013`**, which itself must precede `V500030`
(`DATA-MODEL.md` `WHB-13`: *"`V500013` must precede `V500030`"*).
**Unblocks:** **`P1-05`**, and `P2-28`.

---

### OD-7 — Precision

> **RESOLUTION — Adopt the accounting set's resolved precision table verbatim, by citation rather
> than restatement, and add exactly one warehouse-only row: `conversion_factor_used DECIMAL(18,8)`.
> The display rule is decided here too, because `PLATFORM-DEPENDENCIES.md` §2.11 requires it to be.**

**The authority, cited not restated.** `accounting/docs/OPEN-DECISIONS-RESOLVED.md` `OD-7` — money
`DECIMAL(19,4)`; exchange rate `DECIMAL(19,8)`; quantity / UoM `DECIMAL(18,4)`; per-unit figure
`DECIMAL(19,6)`; percentage / ratio `DECIMAL(9,6)`. **Both tie-breaks come with it**: `unit_*` beats
`value`/`*_amount`, so a per-unit figure is always `DECIMAL(19,6)` and `DECIMAL(19,4)` applies only to
an extended total; and `_percent` beats any reading of "rate", so a `*_percent` column is
`DECIMAL(9,6)` without exception and `DECIMAL(19,8)` is **the currency-conversion type and nothing
else**. The percentage row was stated wrongly for three rounds in that set; adopting the corrected
row is the point of citing rather than retyping.

**The one row warehouse adds, and why it is not a deviation.**
`conversion_factor_used` (`L-7`, frozen on the line) is neither money, nor a percentage, nor a
currency conversion. `R4` proposes `numeric(18,8)`. It cannot be `DECIMAL(9,6)`: a factor of
1 tonne = 1,000,000 grams does not fit in three integer digits. It **must not** be `DECIMAL(19,8)`,
which accounting reserves for currency alone.

> **`conversion_factor_used DECIMAL(18,8)`** — ten integer digits, eight decimal places. A **sixth,
> named kind** in the warehouse precision table: *UoM conversion factor*. It is distinguishable from
> the currency type by both scale and name, so no reader can cite one as authority for the other.

**The display rule, decided here.** `PLATFORM-DEPENDENCIES.md` §2.11 flags that
`currencies.default_decimal_places` is `INT NOT NULL DEFAULT 2` with
`CHECK (default_decimal_places >= 0 AND default_decimal_places <= 4)`
(`platform/backend/src/main/resources/db/migration/V203__Add_currency_format_to_users.sql:9,17`,
verified 2026-09-03), so a per-unit cost at `DECIMAL(19,6)` is **storable but not displayable**
through that setting, and instructs that the display rule be decided *with* `OD-7`, not after.

> **The rule.** Money and quantity render at the declared places for their currency / UoM.
> A **per-unit cost renders at six decimal places on cost surfaces** — the cost-layer grid, the
> movement-line detail, the valuation drill-down — and at the currency's declared places everywhere
> else. **The backend formats and sends a string; the frontend never arithmetics** (CLAUDE.md
> *"Frontend is DISPLAY ONLY"*, and `PLATFORM-DEPENDENCIES.md` §2.11 makes it a correctness rule
> here rather than a style one — a UoM conversion in a JavaScript double is a stock discrepancy).
> **`currencies.default_decimal_places` is never widened past 4 to make this work** — that is a
> platform table shared with every other module.

**What it costs if wrong.** Round-trip loss on every stored figure, discovered at the first
reconciliation and unrecoverable for rows already written — `V500030` seals the ledger against
`UPDATE`, so a widened column is `NULL`-or-truncated on history forever.

**What must change, and where.**

| Document | Edit | Owner |
|---|---|---|
| `DECISIONS.md` §3 | `OD-7` row → **RESOLVED**, names this file | **this edit** |
| `DATA-MODEL.md` §5 | The precision block cites accounting's table and adds the `conversion_factor_used` row and the display rule | **owed** — §5 |
| `PLATFORM-DEPENDENCIES.md` §2.11 | Records that the display rule is decided, and where | **owed** — §5 |
| CLAUDE.md / the standards owner (**`classic` repo — out of scope**) | The `DECIMAL(15,2)` money rule is scoped by module path. Accounting's carve-out names **four** module roots and says explicitly it *"must not be cited outside those four"*. Warehouse's five module roots (`D-1`) therefore need their **own** carve-out — adopting accounting's numbers does **not** adopt its exemption | **owed, different repository** — §5 |

**Deadline cleared:** **before `P0-02`.**
**Unblocks:** **`P0-02`** (five of six), and every numeric column in `P0-17`'s `V500021`.

---

### OD-6 — Valuation-method scope in v1

> **RESOLUTION — Weighted average **and** FIFO ship in v1, with `whb_cost_layers` present and the
> method configurable per item category × site. Standard cost with variances is v1.1. **LIFO is
> never built** — and, because `D-10` makes the method vocabulary an open catalogue with no CHECK, a
> `LIFO` row is never seeded either.**

**The question.** FIFO + weighted average + standard, or weighted average only? *Who owns the layers*
is **not** part of this any more: `D-6` settles it — whichever system is authoritative for quantity is
authoritative for cost, so with warehouse installed the layers are `whb_cost_layers`.

**The reasoning.**

- **Weighted-average-only is not a mid-market product.** FIFO is the default expectation in the
  segment this set benchmarks against, and a customer who runs FIFO cannot adopt a system that
  cannot.
- **The layer table is already v1 whichever way this goes.** `whb_cost_layers` DDL is `P0-17`'s
  `V500021`, and it must precede `V500030` because `whb_stock_movement_lines.cost_layer_id` is a real
  FK (`issues/p0-17.md`). Weighted-average-only would ship the layer table and then not use it —
  the cost of FIFO in v1 is the consumption logic, not the schema.
- **Standard cost is genuinely separable**, because it is not a costing method so much as a variance
  framework: it needs a standard, a revaluation cycle and purchase-price/usage variance accounts.
  Deferring it to v1.1 defers a feature, not a data shape.
- **LIFO is prohibited under Ind AS 2 / IAS 2.** Building it would be building an unusable method.
  The subtle part is `D-10`: because the method vocabulary is an **open catalogue with no CHECK**,
  "never built" is not enforced by the schema. It has to be enforced by never seeding the row and by
  saying so where the catalogue is seeded — otherwise an install adds `LIFO` as data and the engine
  silently has no implementation for it.

**What it costs if wrong.** `IRR-40` (`IRREVERSIBLE.md:220`) is the governing row and it cites
`OD-6`: *"Changing the grain restates every historical balance, which is an accounting event with a
disclosure and audit consequence, not a migration."* Choosing weighted-average-only and adding FIFO
later is exactly that restatement.

**What is NOT decided here, and must not be assumed to be.** `IRR-40` requires the **valuation grain**
to be declared in writing before the first movement. `OD-6` decides the *method set*, not the grain.
The grain declaration remains owed to `P0-17` and is called out in §5.

**What must change, and where.**

| Document | Edit | Owner |
|---|---|---|
| `DECISIONS.md` §3 | `OD-6` row → **RESOLVED**, names this file | **this edit** |
| `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` `FR-235` | Carries the answer; §9's `OD-6` row moves to resolved | **owed** — §5 |
| `DATA-MODEL.md` | `whb_valuation_policies` seeds `WEIGHTED_AVERAGE` and `FIFO` only, with a written note that `LIFO` is never seeded and `STANDARD` arrives in v1.1 | **owed** — §5 |
| `issues/p0-17.md` | `V500021` seeds the two methods; the `IRR-40` grain declaration is an acceptance line | **owed** — §5 |
| `issues/p2-16.md` | Scope fixed at two methods; the per item category × site policy resolution is an acceptance line | **owed** — §5 |

**Deadline cleared:** before P2's valuation tasks.
**Unblocks:** **`P2-16`** (the costing engine — *"the highest-risk task in P2 … the number the
customer signs"*), and the seed content of `P0-17`'s `V500021`.

---

### OD-15 — Is the union valuation report built?

> **RESOLUTION — Not in v1. `P2-27` ships reports over warehouse stock only, and the separation is
> stated on the report header and in `D-9`'s cost note. Revisit at v2 if a customer asks.**

**The question.** With `accessories` permanently separate (`D-9`, a user decision), a finance user
asking *"what is my total stock value"* gets two numbers. `R3`'s `M3` says build one report that
unions them; `R7` §4.6 item 4 says do not. `COEXISTENCE.md:555` carries the row as
*"disputed — needs an `OD-` row"*.

**The reasoning.**

- **A union whose halves use different valuation methods states a total that reconciles to nothing.**
  Warehouse values under `OD-6`'s weighted average or FIFO at full grain; `accessories` has no cost
  layers at all and its balance is an in-place-mutated `accessory_stock_levels` row that is **not
  derivable from its own movements** (`D-4`'s evidence: `accessories/backend/src/main/java/ai/accessories/service/inventory/StockReceiptService.java:374-411`
  — `reverseStockLevel` mutates the balance row in place and writes no movement; verified 2026-09-03). Adding those two numbers produces a figure with no owner and no
  audit path.
- **A wrong grand total is worse than two honest numbers**, because it will be signed. Two numbers
  side by side make the separation visible, which is `FR-370`'s stated requirement —
  *"where a screen could mislead a user into thinking it shows group-wide stock, it says plainly that
  these two inventories are separate."* `OD-15` and `FR-370` are the same instinct; this makes them
  consistent.
- **`D-9`'s mandatory mitigations are unaffected.** The cross-map registry
  (`whb_item_external_refs` with an `ACCESSORIES` source row) and the category-ownership
  reconciliation report are both still v1 and are both still tasks. **Detectability is preserved;
  only the false total is refused.**

**What it costs if wrong.** Nothing irreversible — this is the one adopted decision that is cheap to
reverse. If a customer asks in v2, the report is additive. That asymmetry is itself part of the
reasoning: refusing now costs a revisit, building now costs a number nobody can defend.

**What must change, and where.**

| Document | Edit | Owner |
|---|---|---|
| `DECISIONS.md` §3 | `OD-15` row → **RESOLVED**, names this file | **this edit** |
| `COEXISTENCE.md` `M3` (`:420`, `:555`) | Replace *"disputed — needs an `OD-` row"* with the resolution; keep the row (never delete), restate it as **not in v1, revisit v2** | **owed** — §5 |
| `issues/p2-20.md`, `issues/p2-27.md` | Warehouse-stock-only scope, and the separation statement on the report header as an acceptance line | **owed** — §5 |
| `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` §9 | `OD-15` row → resolved | **owed** — §5 |

**Deadline cleared:** *"before `P2-20` and `P2-27` merge — the deadline has arrived."*
**Unblocks:** **`P2-20`** and **`P2-27`**.

---

### OD-5 — Does the frontend re-close the vocabularies the backend opens?

> **RESOLUTION — It does not. A catalogue-backed dropdown **fetches** its values. A TypeScript string
> union is permitted only for a **closed system vocabulary** — one the product itself defines and no
> install may extend, such as `posting_status`. This is the ruling that makes `FR-380` enforceable.**

**The question.** CLAUDE.md TYPESCRIPT RULE #6 mandates string unions over enums; `D-10` mandates
open catalogues with no CHECK constraint. `R2` records the conflict as a **documented recurring
defect in this codebase**, and `G-064` (`docs/reviews/R7-logistics-supply-chain-seam.md:1371`) refers
it to the standards owner with a recommendation attached.

**Why this is adopted rather than escalated.** The *design-set* half is entirely ours: `FR-380` is
the rule and this is the ruling that gives it a test. The half that belongs to someone else — the
CLAUDE.md amendment in the `classic` repository — is recorded as owed and does not block a warehouse
page from being written correctly, because a page that fetches its dropdown values violates nothing
in CLAUDE.md today; it simply does not *use* rule #6.

**The test, so a reviewer can apply it without re-deriving it.**

> A TypeScript union may enumerate a vocabulary **only if** the same vocabulary is a closed set in the
> database — a `CHECK` or a system-owned enumeration that no install may extend. If the vocabulary is
> one of `D-10`'s thirteen catalogue tables, the union is a defect regardless of how convenient it is.
> The thirteen are: movement types, document types, source systems, reference types, stock statuses,
> location types, item types, reason codes, UoM classes, task types, owner types, hold types, charge
> codes.

**What it costs if wrong.** The backend opens a vocabulary, an install adds a row, and the frontend
drops it — a filter that appears to do nothing and a dropdown missing exactly the value the customer
added. It is invisible in review because both halves look correct in isolation.

**What must change, and where.**

| Document | Edit | Owner |
|---|---|---|
| `DECISIONS.md` §3 | `OD-5` row → **RESOLVED**, names this file | **this edit** |
| `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` `FR-380` | Carries the test above verbatim | **owed** — §5 |
| `BUILD-SPEC-SCREENS.md` | The catalogue screens' field specs say *fetched*, not *union* | **owed** — §5 |
| CLAUDE.md TYPESCRIPT RULE #6 (**`classic` repo — out of scope**) | Gains the carve-out: string unions do not enumerate a registry vocabulary. `G-064` is the referral | **owed, different repository** — §5 |

**Deadline cleared:** before the first warehouse page is written.
**Unblocks:** **`P0-04`**, whose catalogue screens are the first warehouse pages.

---

## 3. Escalated — not decided here, and deliberately so

Each row below fails the technical test stated at the top of this page. **None is left without a
recommendation and none is left without a deadline** — escalation means the call is someone else's,
not that the question is parked.

### 3.1 `S-035` — pharma: serve regulated goods, or decline the segment in writing

**This is the design set's only unowned BLOCKER** (`GAP-REGISTER.md` §5.1, *"the one unowned
BLOCKER"* and *"the most important line in this document"*). It is not a technical question: it asks
whether the product serves a regulated segment, which is a commercial and a liability decision.

**What is actually missing.** Pharma licences on our own entity and on every counterparty
(number, type, expiry), a **hard despatch block** against an expired or absent licence, and the
Schedule H1 register. The six `whin_` tables named in `INDIA-LOCALISATION-PACK.md` §11.2 group H —
`whin_entity_licences`, `whin_counterparty_licences`, `whin_licence_types`,
`whin_licence_quantity_ceilings`, `whin_schedule_h1_register`, `whin_recall_notifications` — have
**no `FR-` row, no `DATA-MODEL.md` row and no task**.

**Why no one caught it.** `GAP-REGISTER.md` §5.1 states the mechanism precisely: *"a promise with no
`FR-` behind it is invisible to a requirement-to-task tracer."* `IMPLEMENTATION-PLAN.md` §8's claim
that every requirement is owned by exactly one task stays true **only because there is no
requirement**. Three independent passes reached the edge of this and stopped.

**The two options, both cheap today.**
1. **Serve it** — write the `FR-` rows, then `P4-13` (the regulated-goods licence pack: one licence
   object, one expiry clock, one despatch guard, one register), a `DATA-MODEL.md` §7.6 block, and a
   migration in `V540000`–`V540199`. This also discharges `X-013`.
2. **Decline it in writing** — amend the four documents that promise *"the regulated-goods packs"*
   (`DECISIONS.md` §5, `IMPLEMENTATION-PLAN.md` §1.6, `PORT-AND-ADAPTER-CONTRACT.md` §9.6, the FRD
   §6.18 preamble) to stop promising them, and move `S-035` to **WONTFIX** with *"pharma is not a
   target segment"* recorded.

**Silence is the third option and it is the one that fails.** `R5` §6 marks pharmaceutical
distribution **CANNOT SERVE**, and a salesperson reading `DECISIONS.md` §5 will bid it.

**Deadline.** Before v2/P4 planning closes — and **before any customer conversation in the segment**,
which is the real clock and is outside this repository's control.
**Recommendation attached, not taken:** if there is no named pharma prospect, **decline in writing**.
Option 2 costs four sentences; option 1 costs a task and a migration band, and half-building licence
gating is worse than not having it, because a despatch guard that exists but is not enforced reads as
compliance.

### 3.2 `OD-1` — the reciprocal accounting edits, with two corrections and a fourth edit folded in

**Recorded as owed. Not made.** `neetub1508/accounting` is a different repository carrying unrelated
in-flight work; this design set does not edit it.

**What `D-6` requires of that set.** Stand down `acc_stock_balances`, `acc_physical_stock_counts`,
`acc_stock_journals`, `acc_cost_layers`' quantity grain and the port's `unit_cost` semantics when a
warehouse product is installed — expressed as a **third install state**: *a warehouse product is
present and owns quantity*.

**Correction 1 — the deadline is accounting's P1, not its P3.** `OD-1` states *"before accounting's
P3 starts."* Round 2's `O-001` establishes that this is wrong: `acc_godowns` is **`V600136`** and
`accounting/issues/p1-04.md:5,13,15` schedules it in **P1**, module `accounting-base`, with
`accounting/docs/DATA-MODEL.md:4291` confirming *"schema only, feature in P3 | P1-04"*. **The schema
lands in P1**; the feature lands in P3. `OD-1`'s deadline misses the migration by a whole phase, and
a migration is the thing that cannot be un-shipped. The corrected deadline —
**before accounting's `P1-04` ships `V600136`/`V600137`** — is applied to `DECISIONS.md` §3 in this
edit.

**Correction 2 — accounting's Mode C invariant contradicts `D-6`, and neither set says so.**
`accounting/docs/ACCOUNTING-FUNCTIONAL-REQUIREMENTS.md:48` requires Mode C to need *"zero change to
`accounting-base`"*. A quantity-owning warehouse is **not** zero change: it stands down four
`accounting-base` tables. `accounting/docs/MODULE-INTEGRATION.md:26` independently records warehouse
as **absent** — *"Mode C (warehouse) has no counterpart here."* The reciprocal edit therefore has to
relax that invariant in the same change, or the third install state is illegal in the set that
receives it.

**The fourth reciprocal edit, from round 3's `RF-005`.** The receiving schema cannot hold the value
warehouse computes. `acc_source_document_movements` (`accounting/docs/DATA-MODEL.md:277`) carries
`quantity`, `unit_cost` and one `movement_date` — **no extended-value column, no currency column, no
`cost_basis` column**. `FR-233` says warehouse sends the unit cost *and the extended value and the
basis*; `FR-446` makes *"accounting does not re-cost what it is handed"* a build-time falsifier. With
only `quantity` and `unit_cost` on the wire the receiver **must** recompute, which is the forbidden
step and also a **second rounding** — warehouse rounds `extended_cost` once at post, accounting
re-multiplies a `DECIMAL(19,6)` unit cost by a `DECIMAL(18,4)` quantity and rounds again. The
difference is up to half a paisa per line on AVCO costs and lands in `FR-247`'s variance column as a
permanent, undrillable reconciling item.

> **The fourth edit, stated precisely enough to file:** add `extended_value`, `currency_code`,
> `exchange_rate` and `cost_basis` to `acc_source_document_movements`, plus a receiving rule —
> *"where `extended_value` is present it is authoritative; `quantity × unit_cost` is never
> recomputed."*

**The three warehouse-side obligations that travel with it** — these are ours and are owed, not
escalated (§5): enumerate `envelope_kind`'s vocabulary in `DATA-MODEL.md` (`grep -rn "envelope_kind"
docs/ issues/` → 4 hits, none enumerating values); state in `P2-18` that a warehouse handover fills
`movements[]` and that `movement_date` = the warehouse **`posting_date`** (`L-13`'s accounting clock,
**not** `occurred_at` — and note that `OD-12` above chose `occurred_at` for the *partition*, which is
a different question and must not be conflated); and state that `cost_basis = ZERO_BAILMENT`
suppresses the envelope entirely, which is `L-14`'s only enforcement point.

**How much window is left, computed 2026-09-03.**

```bash
ls ../classic/accounting-base/backend/src/main/resources/db/migration/ | wc -l   # → 32 (was 24 when O-001 was written)
ls ../classic/accounting-base/backend/src/main/resources/db/migration/ | grep -c '600136\|600137'   # → 0
```

`V600136`/`V600137` have **not** shipped, so the edit is still a documentation edit and costs
nothing. But `V600141` and `V600142` — numbers **above** the one this set is waiting on — have
already shipped, so accounting P1 is actively landing migrations past the gate.
**The out-of-order hazard is neutralised and should not be raised as a blocker:**
`platform/backend/src/main/resources/application.yml:105` sets `out-of-order: true`, so a later-
authored `V600136` still runs against a database that already has `V600141`. What is *not*
neutralised is the underlying race — once `acc_godowns` exists in a customer database, the third
install state stops being a documentation edit and becomes a data migration.

**Deadline.** Before accounting's `P1-04` ships `V600136`/`V600137`, **and** before warehouse
`P0-02` writes `whb_stock_movements`.
**Recommendation attached, not taken:** file one issue in `neetub1508/accounting` — *"Add a third
install state — Mode D: `accounting-base` + a quantity-authoritative external stock system"* — whose
body edits four files (`ACCOUNTING-FUNCTIONAL-REQUIREMENTS.md:47-48`, `MODULE-INTEGRATION.md:26`,
`DATA-MODEL.md:434,436,507`, `issues/p1-04.md`) and carries the fourth edit above. **Blocking
accounting `P1-04`.**

### 3.3 `OD-3` — one database per customer, or shared multi-tenancy?

**Gates `P5-01`, the first task of P5** (`warehouse-3pl` scaffold, the client as an object, and the
build-time proof that it is a module). Nothing in P5 can be written against an undecided tenancy
model.

**Why it escalates.** The recommendation — keep one database per customer — is a **deployment and
commercial** decision about how the product is sold and operated, not a schema question. The schema
question is already answered and is not open: `owner_id` is `NOT NULL` in v1 in every install and in
the position key (`D-5`), so a 3PL's clients are an **owner dimension** and never tenants.

**Recommendation attached, not taken:** keep one database per customer.
`grep -ril "tenant" platform/backend/src/main/java` → **0 files**; classic is one-DB-per-customer
today, and `D-5` already carries the 3PL case. **Two consequences that are easy to miss and belong
with the decision:** the second customer is a *different database*, so every mapping profile, import
template, label template and reason-code catalogue must be exportable and importable; and
`platform/backend/src/main/resources/db/client/` version numbers are **deliberately reused across
clients**, which is why the `V910000+` band was unusable and `D-2` moved the warehouse bands.

**Deadline.** Before `warehouse-3pl` P5 starts.

### 3.4 `OD-9` — does `warehouse` carry a tax engine, or never compute tax?

**Gates `P2-IN-01` and `P4-01` — the first task of two phases.** `P2-IN-01` is the fifth module's
scaffold; `P4-01` builds the GST reference masters and the tax engine. The India pack is **50 or 56
tables** depending on the answer.

**Why it escalates.** `FR-325` has warehouse carrying a tax engine; `FR-294` and `R3` say warehouse
never computes tax. Choosing between them decides whether the product sells as a compliance product
or hands compliance to a partner — a positioning call with a support and liability tail, not an
architecture preference. It also determines what a third party must supply, which is a commercial
dependency.

**Recommendation attached, not taken:** **warehouse never computes tax.** It captures the
tax-relevant facts — HSN, place of supply, `is_taxable_supply` frozen at creation, taxable value —
and hands them over; accounting or the compliance provider computes. Same three-state shape as
`OD-1`. **This drops the 6 conditional tables.**

**Deadline — and a correction to it.** `DECISIONS.md` §3 carries *"Before `P2-IN`"*. The FRD §9 row
records a **tighter** one from round 2: *"its deadline moves to **before `P2-25`***, not before
`P2-IN` — `P2-25` builds the v1 table that implements the rejected option (`U-003`)."* The tighter
deadline governs, and §3 is corrected to carry it in this edit. `U-003` additionally records that the
v1 counter-sale walkthrough already **contradicts** `OD-9` by computing `tax_amount` on a v1 screen —
so the rejected option is being built while the decision is open, which is the strongest argument for
answering it now.

**ANSWERED — 2026-09-20.** The owner took **the recommendation on the record: `warehouse` never
computes tax.** It captures the tax-relevant facts — HSN, place of supply, `is_taxable_supply` frozen
at creation, taxable value — and hands them over; **accounting or the compliance provider computes.**
`FR-325`'s reading loses; `FR-294` and `R3 D4` win.

**What the answer decides, concretely:**

| Consequence | Value |
|---|---|
| India pack table count | **50**, not 56 |
| Group **K** — the 6 conditional relational-tax-engine tables (`whin_tax_entity_types`, `whin_tax_components`, `whin_tax_rules`, `whin_tax_rule_components`, `whin_tax_rule_conditions`, `whin_tax_resolution_audit`; §7.6 `WIN-13`, `INDIA-LOCALISATION-PACK.md` §11.2 group K and §11.4) | **dropped** |
| `P2-IN-01`'s scope | the 50-table shape — no tax engine scaffolded |
| `P4-01` | builds the GST reference **masters** only, not an engine |
| `P2-25`'s v1 counter sale computing `tax_amount` and taking payment inside a warehouse module (`U-003`) | **the losing side.** Flagged to `BATCH-WAREHOUSE-P2.md`; `RA-002`'s contingent amendment is now determined |

**This unblocks `P2-IN-01`,** which was the only task this decision gated inside P2-IN, and it
determines — rather than resolves — the `P2-25` amendment, which belongs to the P2 stream and is not
edited here.

### 3.5 `OD-8` — how does an out-of-process consumer authenticate to the port?

**Escalated, with the warehouse-side fallback adopted so `P0-08` is not blocked.**

**Why it escalates.** The recommendation is *"a platform service principal — a first-class non-human
identity with role grants"*, and `IMPLEMENTATION-PLAN.md:1275` (`PP-2`) states plainly that it is
**the only item in this set that platform must build for warehouse**. Asking another team to build a
new identity primitive is exactly the class this page does not decide. There is no API-key table in
platform (grep → 0) and the only API-key path in the repository is per-handler inside the boom-barrier
webhook, so this is net-new platform work with its own security review.

**What is adopted — the technical half that is ours.** `PP-2`'s own fallback:

> Warehouse ships the port authenticated by an **ordinary user account** holding
> `warehouse:movements:post`, and an out-of-process consumer — a separately deployed `logistics` —
> is **not supported until v3**. That is v1-acceptable and it is a v3 blocker.

This is adopted because it needs nothing from anyone else, and because it does not foreclose the
service principal: an endpoint authenticated by a role grant accepts a service principal unchanged on
the day platform ships one. **`P0-08` may therefore proceed**, and the escalation is about v3, not
about v1.

**Deadline.** The v1 fallback clears `P0-08` now. The platform ask must be answered **before `P6-08`
(`logistics`) is planned**, because a separately deployed consumer has nothing to authenticate with
until it exists.

### 3.6 `OD-2` and `OD-4` — left open, deliberately

Neither is a defect and neither is being resolved by silence: both are **v3 planning** questions whose
deadlines have not arrived, and both have a recommendation on file.

| # | Question | Deadline, restated | Recommendation on file |
|---|---|---|---|
| **OD-2** | Does dealer *vehicle* inventory (`pdi_vehicle_inventory`, `pdi_stock_yards`, `pdi_yard_storage_locations`, `pdi_storage_slot_assignments`) migrate onto the warehouse ledger? | **v3 planning, not before.** `P6-09` is where it is answered | **Do not migrate in v1 or v2.** Model it as a documented future `whad_` adapter and prove the ledger on **parts** first. `FR-365` states the *test* rather than the answer: can the serial-controlled item model carry a vehicle without weakening it? |
| **OD-4** | Who owns the shared supplier/counterparty master long-term? | **v3.** `P6-06` — `P1-08` proceeds regardless | `warehouse-base` keeps `whb_counterparties`; any future module joins through `whb_counterparty_external_refs`. **Never an FK from base into another module** — the previous attempt at this seam died of exactly that: 84 FK references into `scc_*`, several to tables that never existed |

**Why leaving them open is the correct action rather than a deferral.** `D-12` requires every
capability to be *placed in a version and carried in a task now*, and both are: `OD-2` in `P6-09`,
`OD-4` in `P6-06`. Deciding a v3 question in a v1 wave, against a v3 codebase nobody has seen, is how
a set acquires a decision it later has to unpick.

---

## 4. Two new open decisions, allocated by this document

Round 3 produced two BLOCKERs that are not defects in a document but **gaps in the v1 cut line**.
Both are allocated `OD-` ids here — `DECISIONS.md` §3 owns that namespace and no other document may
allocate — and both are **escalated**, because moving the v1 cut line is a product call.

`OD-16` and `OD-17` are the next two free ids
(`grep -coE '^\| \*\*OD-[0-9]+\*\*' docs/DECISIONS.md` → **15** before this edit, `OD-1`…`OD-15`
contiguous).

### 4.1 `OD-16` — v1 foreign-currency costing has no exchange-rate source

**Source:** `RF-004` (`docs/reviews/R21-money-costing-and-billing.md:322`), **BLOCKER**, which
*explicitly recommends promoting it* to a numbered open decision.

**The question.** `FR-245` is **v1**: *"the cost layer carries `currency_code` and `exchange_rate`
from v1."* `WH-SC-160` is a **v1·P2 happy path** with a concrete rate — USD 42.00 at 88.4150.
`issues/p2-16.md` requires both columns. Three things are missing under all of that:

- **(a) There is no rate.** `PLATFORM-DEPENDENCIES.md` §2.12 runs the grep, reports zero rate
  sources, offers *"two honest options"* — v1 values in the single default currency only, or the rate
  rides the movement line frozen — **and decides neither**, ending with *"Do not build a rates table
  in `warehouse-base`."* It is **not an `OD-` row**, so nothing gives it a deadline or an owner, and
  `OD-7` is the only currency-adjacent decision in `DECISIONS.md` §3.
- **(b) The wire cannot carry it.** `PORT-AND-ADAPTER-CONTRACT.md:280-282` gives the line
  `unit_cost`, `cost_currency_code`, `extended_cost`, `cost_basis`, `moving_average_after`,
  `cost_layer_id` — and **no `exchange_rate` field**. Option (b) is unbuildable as the contract
  stands. `cost_currency_code` is additionally marked *"Column v1, multi-currency v2"* while
  `FR-245` and `WH-SC-160` are v1.
- **(c) Nothing says which currency the stored numbers are in.** Is `unit_cost` 42.00 USD or
  3,713.43 INR? Is `layer_value` the transaction amount or the base amount? The valuation report sums
  `layer_value` across layers; if the column is transaction currency the total is a sum of unlike
  units, and if it is base currency then `exchange_rate` is the only record of what was paid.

> ### ⚠ The premise has changed since `RF-004` was written, and the correction runs *against* the finding
>
> `RF-004` and `PLATFORM-DEPENDENCIES.md` §2.12 both rest on **zero exchange-rate sources
> monorepo-wide**. Re-run on 2026-09-03:
>
> ```bash
> cd ../classic && grep -rln "exchange_rate\|currency_rate\|fx_rate" --include=*.sql . \
>   | grep -v node_modules | grep -v target | wc -l      # → 6, not 0
> ```
>
> **There is now a rate table**, and it is
> `accounting-base/backend/src/main/resources/db/migration/V600040__Create_acc_exchange_rates_permissions_menu_and_grid.sql:126,147`
> — `acc_exchange_rates` with `rate DECIMAL(19,8) NOT NULL`, a rate type, a source and a
> date-effective lookup. It shipped after the review was written.
>
> **This does not change the recommendation, and it must not be allowed to look as though it does.**
> Warehouse still cannot read it: `D-7` makes **standalone** the reference configuration and a
> standalone install has no `accounting-base` at all, and `FR-231` forbids reading it even where
> accounting *is* present. The finding's conclusion stands; one sentence of its evidence does not.
> **`PLATFORM-DEPENDENCIES.md` §2.12's grep output is now stale and is listed as an owed edit (§5).**

**Why it is escalated rather than adopted.** The cheap answer changes what v1 *is*: it declares that
v1 values stock in the install's single base currency, which is a statement to a customer about what
the product does, and it moves `cost_currency_code` from *"multi-currency v2"* to a v1 audit trail.
That is the v1 cut line, and `D-12` makes the cut line a product decision.

**Recommendation, attached and not taken.** Take `RF-004`'s cheap answer:

> **v1 values in the install's base currency.** The layer's `currency_code` / `exchange_rate` record
> **what was paid** and are the audit trail of the transaction amount, not the basis of the total.
> The rate is **supplied by the producer on the movement line and frozen at post**, exactly as
> `conversion_factor_used` is frozen under `L-7`.
> **One field on the wire** — `exchange_rate`, `DECIMAL(19,8)` per `OD-7`, optional, defaulting to 1.
> **One sentence** in `DATA-MODEL.md` §5.1 declaring `unit_cost` and `layer_value` to be **base
> currency**. **One `CHECK`**: `currency_code <> base` implies `exchange_rate IS NOT NULL`.
> **One falsifier** on `WH-SC-160`: the valuation report totals in base currency and the layer detail
> shows USD 42.00.

**What it costs if wrong / late.** `IRR-36` (`IRREVERSIBLE.md:216`) already marks the cost-currency
columns irreversible — *"retro-fitting currency onto a cost history is guessing"* — and the same is
true of the rate. Layers created before the decision carry a rate of 1 or a `NULL` and no algorithm
recovers what was paid. In the field, the first import of foreign stock produces a valuation wrong by
two orders of magnitude that **looks like a decimal-place bug**.

**Deadline.** **Before `P0-17` writes `V500021`** — the `whb_cost_layers` DDL — which itself must
precede `V500030` (`WHB-21`). Note that `IRR-36` puts `cost_currency_code` on the movement **line** at
`PNR-1`, so the wire field and the line column are both `V500030` questions: the binding deadline is
the earlier of the two, `V500021`.
**Gates.** **`P2-16`**, and the column set of **`P0-17`**.
**Documents it amends when answered.** `PORT-AND-ADAPTER-CONTRACT.md` §2.5 (the wire field),
`DATA-MODEL.md` §5.1 (the base-currency declaration), `PLATFORM-DEPENDENCIES.md` §2.12 (the decision
and the corrected grep), `SCENARIO-CATALOGUE.md` `WH-SC-160` (the falsifier).

### 4.2 `OD-17` — v1 prints a GS1-128 pallet label carrying an SSCC v1 can neither allocate nor read back

**Source:** `RD-001` (`docs/reviews/R19-integration-device-and-channel-surface.md:163`), **BLOCKER**.

**The question.** Three version cells, each defensible alone, do not compose:

1. **The label is v1.** `FR-225` puts *"LPN or pallet label with a GS1-128 symbology"* among the
   eleven kinds that ship in **v1/P2**; `WH-SC-203` (v1·P2, happy) has the storekeeper print an
   `LPN_LABEL` in ZPL carrying *"a GS1-128 symbology and the SSCC"*; `issues/p2-14.md`'s acceptance
   list contains, verbatim, *"The GS1-128 LPN label encodes AI `00`"*. **AI `00` is the SSCC** —
   there is nothing else it can be.
2. **The SSCC cannot be allocated until v1.1.** `FR-452` opens with *"An SSCC is allocated, not typed
   in. `FR-100` gives the LPN an `sscc` column and **nothing fills it**."* The allocator — GS1
   company prefix, extension digit, per-key gapless counter, mod-10 check digit — and its two tables
   `whb_gs1_settings` / `whb_gs1_serial_counters` are `V500056`, **v1.1**, task `P3-24`.
3. **The label cannot be read back until v1.1 either.** `FR-062`'s single scan-resolution service is
   v1/P1; `FR-063`'s GS1 element-string parsing (the AI table, fixed vs variable length, the FNC1
   separator) is **v1.1/P3**, and `WH-SC-266` is filed v1.1·P3. So in v1 the six scan surfaces of
   `WH-SC-265` hand a GS1-128 element string to a resolver with no parser for it and, per `FR-062`,
   log it as **unresolved**.

**No document in the set reads two of the three together.**

**The v1 behaviours this actually leaves, and both are bad.** `whb_lpns.sscc` is a nullable column on
a screen and nothing forbids typing one in. So v1 either (a) prints a GS1-128 barcode whose AI `00`
field is empty, which most ZPL renderers emit as a malformed element string, or (b) lets a user key
an SSCC — the exact practice `FR-452`'s title exists to prevent, and the one that produces duplicate
licence plates across two sites within a month.

**Why it is irreversible in the physical world, which is the reason it is escalated and not filed as
a defect.** `FR-064`'s stated reason for making `sscc` and `gln` v1 **columns** is that *"they are
printed on physical labels and exchanged with trading partners; issuing them later means
re-labelling."* This version pairing forces precisely the re-labelling `FR-064` was written to avoid.
After a v1.1 development window there are pallets in racking, in transit and **at customers** carrying
labels that have either no licence plate or one from a namespace the allocator does not know about —
and when `P3-24` ships, its counter **cannot be seeded to avoid collision, because nothing recorded
which values were hand-typed**. Second order: `PC-42`'s `carton.packed` event and per-pallet storage
billing both key on the LPN, so a 3PL client's storage invoice referencing a pallet with no SSCC is
not auditable.

**Why it is a product call.** Both fixes move the v1 cut line — one moves work **into** v1, the other
takes a promised v1 capability **out**. Neither is a technical judgement.

**Recommendation, attached and not taken — option (a).**

> **Move the SSCC allocator into the v1 wave.** It is `whb_gs1_settings` plus
> `whb_gs1_serial_counters` plus a mod-10 function, and it reuses the **same locked-counter-row
> idiom `FR-426` already builds in v1** for document numbers, so the marginal cost against `P2-14` is
> small.
> The alternative, option (b), is to **remove the GS1-128 LPN label from the v1 eleven**, ship a
> Code-128 licence plate carrying the internal `lpn_code` only, and say so in `FR-225` and
> `WH-SC-203`.
> **(a) is recommended: GS1-128 without an SSCC is not GS1-128**, and a v1 that prints a
> nearly-compliant pallet label is worse than one that prints an honest internal one.
> **Whichever wins**, `issues/p2-14.md`'s *"encodes AI `00`"* acceptance criterion and `WH-SC-203`'s
> *"and the SSCC"* move with it, and the print-side FNC1 encoding rule lands in the same task —
> `grep -rniE "FNC1" docs/ issues/` returns four matches, **all on the parse side and none on the
> print side**.

**Deadline.** **Before `P2-14` merges** — the moment a label template ships is the moment the first
label is printed, and a printed label cannot be recalled (`FR-064`).
**Gates.** `P2-14`; and `P3-24`'s counter seeding depends on the answer.

---

## 5. Owed downstream edits — every document this resolution touches and this wave does not own

**This wave owns exactly two files:** this one, and `DECISIONS.md` §3 and §6. Everything below is a
consequence of a decision taken above that lands in a document a later wave must edit. It is listed
here so that *"resolved"* never means *"resolved in one place and silently contradicted in nine"* —
which is how the accounting set acquired 25 dangling cross-references.

`GAP-REGISTER-R3.md` is being written concurrently by another author and is **not** in this table;
nothing here writes to it.

| # | Document | Edit owed | Because of | Blocking |
|---|---|---|---|---|
| 1 | `DECISIONS.md` **§4** | Add the **`L-15`** row, verbatim from §2 (`OD-14`) | `OD-14` | `P0-02` |
| 2 | `DATA-MODEL.md` **§6.3** | Add the **`I-21`** row, verbatim from §2 (`OD-14`); `WHB-30`'s invariant list gains `I-21` | `OD-14` | `P0-02` |
| 3 | `DATA-MODEL.md` | `whb_lots`: MRP is a lot attribute and is **not** in the position key | `OD-10` | `P0-02` |
| 4 | `DATA-MODEL.md` §5 | Cite accounting's precision table; add `conversion_factor_used DECIMAL(18,8)` and the display rule | `OD-7` | `P0-02`, `P0-17` |
| 5 | `DATA-MODEL.md` §5.1 | Declare `unit_cost` / `layer_value` **base currency** *(only once `OD-16` is answered)* | `OD-16` | `P0-17` |
| 6 | `DATA-MODEL.md` | `whb_locations` seed block gains `VALUE_OFFSET`; `whb_valuation_policies` seeds two methods and never `LIFO`; enumerate `envelope_kind`'s vocabulary | `OD-13`, `OD-6`, `OD-1` | `P1-05`, `P0-17`, `P2-18` |
| 7 | `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` `FR-084` (`:224`) | Seed **eleven** virtual locations — add `VALUE_OFFSET` | `OD-13` | `P1-05` |
| 8 | `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` `FR-321`, `FR-235`, `FR-380` | Each carries its answer inline | `OD-10`, `OD-6`, `OD-5` | `P0-02`, `P2-16`, `P0-04` |
| 9 | `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` **§9 and `:874`** | Nine rows move to resolved; `OD-16`/`OD-17` are added; **and the `:874`/`:978` contradiction is fixed** — see §6.2 | all | — |
| 10 | `IMPLEMENTATION-PLAN.md` **§7, §7.1, §2.10, §11** | Tabulate `OD-1`…`OD-17`; retire the *"unnumbered conflict"* row; **correct "five" to "six"** — see §6.1 and §6.3 | all | — |
| 11 | `PLATFORM-DEPENDENCIES.md` **`PD-D5`** (`:808`) | The **losing** document is amended, not left standing: `occurred_at` per `OD-12`, `posting_date` by index, and the never-closed-partition cost recorded as accepted | `OD-12` | `P0-02` |
| 12 | `PLATFORM-DEPENDENCIES.md` **§2.11, §2.12** | §2.11 records that the display rule is decided; **§2.12's grep output is stale — it now returns 6, not 0** (§4.1) and the section must state why the six do not help | `OD-7`, `OD-16` | `P0-17` |
| 13 | `PORT-AND-ADAPTER-CONTRACT.md` **§12.2 row 3**, `PC-12`, **§2.5** | Replace *"this document does not decide"*; replace `LANDED_COST_OFFSET` and drop the `ADJUSTMENT_OFFSET` reuse; add the `exchange_rate` wire field *(once `OD-16` is answered)* | `OD-14`, `OD-13`, `OD-16` | `P0-02`, `P1-05`, `P0-08` |
| 14 | `IRREVERSIBLE.md` `IRR-05` (`:155`), and the rows naming the position key | `VALUE_OFFSET` joins the virtual-location list; the key is **nine members, `OD-10` resolved** | `OD-13`, `OD-10` | `P1-05`, `P0-02` |
| 15 | `COEXISTENCE.md` `M3` (`:420`, `:555`) | Replace *"disputed — needs an `OD-` row"* with **not in v1, revisit v2**. **Keep the row** | `OD-15` | `P2-20`, `P2-27` |
| 16 | `SCENARIO-CATALOGUE.md` `WH-SC-160`, `WH-SC-203` | Falsifiers move with `OD-16` / `OD-17` when they are answered | `OD-16`, `OD-17` | `P2-16`, `P2-14` |
| 17 | `BUILD-SPEC-SCREENS.md` | Catalogue-screen field specs say **fetched**, not union | `OD-5` | `P0-04` |
| 18 | `issues/p0-02.md` | Drop five `OD-` rows from *Blocked on*; the `posting_date` index becomes an acceptance line | `OD-7`,`OD-10`,`OD-11`,`OD-12`,`OD-14` | `P0-02` |
| 19 | `issues/p0-17.md` | Seeds two valuation methods; **and the `IRR-40` valuation-grain declaration remains owed here — `OD-6` decided the method set, not the grain** | `OD-6` | `P0-17` |
| 20 | `issues/p1-05.md` | `V500013` seeds eleven virtual locations | `OD-13` | `P1-05` |
| 21 | `issues/p2-16.md`, `p2-17.md`, `p2-18.md`, `p2-20.md`, `p2-27.md`, `p2-28.md`, `p3-11.md`, `p4-05.md` | Each takes the resolved rule its *Blocked on* names; `p2-18` additionally states `movements[]`, `movement_date` = warehouse `posting_date`, and `cost_basis = ZERO_BAILMENT` suppresses the envelope | `OD-6`,`OD-10`,`OD-11`,`OD-13`,`OD-14`,`OD-15`,`OD-1` | those tasks |
| 22 | `tools/check-design-set.py` — `FINDING_CITE_RE` | Extend to the six two-letter round-3 registers — see §7 | round-3 allocation | CI |
| 23 | **`neetub1508/accounting`** (different repository) | The third install state, the Mode C relaxation, the corrected P1 deadline and the **fourth** reciprocal edit — §3.2 | `OD-1` | accounting `P1-04` |
| 24 | **CLAUDE.md / the standards owner** (`classic`, different repository) | A warehouse-scoped `DECIMAL` carve-out (accounting's names four module roots and forbids citing it outside them), and the TypeScript rule #6 carve-out | `OD-7`, `OD-5` | `P0-02`, `P0-04` |

**Rows 23 and 24 are in repositories this wave may not write to.** They are recorded as owed and
nothing more, which is the whole point of recording them.

---

## 6. Three stale statements, corrected or recorded

House rule: never state a count you did not compute. Each correction below carries the command.

### 6.1 *"for `P0-02` that is **five** open decisions"* — it is **six**, and the sentence is not in the file it was attributed to

```bash
grep -rn '\*\*five\*\* open decisions' docs/
# → docs/IMPLEMENTATION-PLAN.md:1333   (one hit, in that file's §7.1 "The gate, as a rule")
grep -cn 'five' docs/DECISIONS.md
# → 3 after this edit, and none of them is the sentence: line 64 is about V910001 existing five
#   times, and lines 304 and 318 are this resolution's own "six, not five" corrections.
#   DECISIONS.md has no §7.1 at all — §7 is "Rules every author of this design set follows".
```

**The sentence lives at `IMPLEMENTATION-PLAN.md:1331-1334`, not in `DECISIONS.md`.** It reads:

> *"No task in the 'Blocks' column above may be merged while its `OD-` row is open. For `P0-02` that
> is **five** open decisions — `OD-1`, `OD-7`, `OD-10`, `OD-11` and the partition key."*

**Two things are wrong with it and one is not.** The count is wrong: it is **six**, because the list
predates `OD-13`…`OD-15` and omits **`OD-14`**, whose own deadline cell reads *"Before `P0-02`,
because the guard is a constraint on the table."* The phrase *"the partition key"* is now
**`OD-12`**, which is right in substance and stale in form. What is *not* wrong is `OD-11`'s
inclusion — the plan had it right and `DECISIONS.md` §3 had it wrong (§2, `OD-11`).

**The six, computed after this edit:**

```bash
# the rows whose DEADLINE CELL (field 4) gates P0-02 / PNR-1 = V500030, the migration
# that cannot be taken back. The cell is read, not the whole row: OD-16's deadline mentions
# V500030 in passing and is not one of these gates (DECISIONS.md sec 7 rule 8).
awk -F'|' '/^\| \*\*OD-/ && $4 ~ /[Bb]efore [^.;]*(P0-02|PNR-1)/ {gsub(/[*` ]/,"",$2); printf "%s ", $2}' docs/DECISIONS.md
# -> OD-10 OD-12 OD-14 OD-11 OD-7 OD-1
```

**This wave does not own `IMPLEMENTATION-PLAN.md`, so the fix is recorded as owed (§5 row 10) rather
than made.** The two corrections that *are* ours were made: `OD-11`'s deadline cell in
`DECISIONS.md` §3 now reads before `P0-02`, which is what makes the command above return six.

### 6.2 The FRD contradicts itself about how many open decisions there are

```bash
sed -n '874p;978p' docs/WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md
# :874  "Thirteen decisions (`D-1` … `D-13`) and all seven open decisions (`OD-1` … `OD-7`) are cited."
# :978  "**All fifteen remain open** and each gates named requirements."
```

`:978` was corrected on 2026-09-02; `:874` was not, and still says **seven**. Both sentences are in
one document, 104 lines apart. After this resolution **neither** is true: fifteen existed, nine are
resolved, and two are added — so `:874` and `:978` both need rewriting, not just reconciling.

**We do not own the FRD. Recorded as owed (§5 row 9).** The correct replacement text, so the later
wave does not have to re-derive it:

> `:874` — *"Thirteen decisions (`D-1` … `D-13`) and all seventeen open decisions
> (`OD-1` … `OD-17`) are cited."*
> `:978` — *"**Nine of seventeen are resolved** (see `OPEN-DECISIONS-RESOLVED.md`); six remain open
> and escalated, and two — `OD-16`, `OD-17` — were allocated on 2026-09-03."*

### 6.3 `IMPLEMENTATION-PLAN.md` §7 tabulates only `OD-1`…`OD-11` and calls `OD-12` an unnumbered conflict

```bash
sed -n '1295p' docs/IMPLEMENTATION-PLAN.md
# → "Eleven `OD-` rows plus one unnumbered conflict."
grep -c '^| \*\*OD-' docs/IMPLEMENTATION-PLAN.md          # → 11
sed -n '1328p' docs/IMPLEMENTATION-PLAN.md | cut -c1-30
# → "| **⛔ unnumbered** | **The le"
```

The *"unnumbered conflict"* at `:1328` **is `OD-12`**, allocated in `DECISIONS.md` §3 on 2026-09-02
(`X-024`). The plan's §7 has been stale for a day; after this resolution it is stale by six rows
(`OD-12`…`OD-17`) plus nine state changes.

**We do not own the plan. Recorded as owed (§5 row 10).** The edit is: replace the `⛔ unnumbered`
row with an `OD-12` row carrying the **resolution**, add `OD-13`…`OD-17`, mark the nine resolved rows
resolved with a pointer to this file, and fix §7.1's *"five"* to **six** per §6.1. `DECISIONS.md` §3
is the authority for all of it — *"a document that disagrees with this one is wrong."*

---

## 7. The round-3 id namespaces, and why they needed two letters

Round 3 ran six lenses and allocated six finding registers. The allocation is recorded in
`DECISIONS.md` §6 by this edit; the reasoning is here.

```bash
# every two-letter R-register token in the set, and the files that define them
grep -rlE "\bR[A-Z]-[0-9]{1,3}\b" docs/ issues/ tools/
# → exactly the six round-3 reviews and nothing else

# sizes, from the finding headings themselves rather than from citations
for f in R16:RA R17:RB R18:RC R19:RD R20:RE R21:RF; do r=${f%%:*}; p=${f##*:}; \
  printf '%s %s: ' "$r" "$p"; grep -cE "^###+ .*\`?${p}-[0-9]{3}\`?" docs/reviews/${r}-*.md; done
# → RA 8 · RB 9 · RC 9 · RD 8 · RE 8 · RF 10   = 52
```

**The single-letter space is exhausted.** Round 1 took seven letters and round 2 took eight, leaving
fifteen of the alphabet spoken for as finding registers, on top of `D-` (decisions), `L-`
(invariants), `I-` (constraints) and `X-` (design-set defects). Re-run on 2026-09-03:

```bash
for L in A B M N R V W; do printf '%s: ' "$L"; \
  grep -rnoE "\b${L}-[0-9]{1,3}\b" docs/ issues/ tools/ | wc -l; done
# → A 289 · B 5 · M 0 · N 4 · R 37 · V 3 · W 4
```

**Only `M` is genuinely free**, and the letters that look free are not:

| Letter | What is already there | Why it cannot be taken |
|---|---|---|
| `A` | `DECISIONS.md` §5.1's four ladder amendments, `A-1`…`A-4` | 289 mentions; a load-bearing register |
| `B` | `B-04` is a **rack label** in `reviews/R2` (`:828`), quoted into the FRD (`:222`) and `reviews/R18` (`:657`, `:673`); `B-003` in `issues/README.md` | A finding id that is also a physical location in a worked example is unreadable in both directions |
| `N` | `N-045`, `N-043` — **citations into the *accounting* register**, in `IRREVERSIBLE.md:251` and `reviews/R5` | Cross-set citations that would silently resolve to a warehouse finding |
| `R` | `R-1`…`R-5`, the **rounding rules** in `DATA-MODEL.md` (`:2125`) | Load-bearing, and `R` is also the review-file prefix — `R-1` beside `R1` is exactly the `I-`/`IRR-` hazard |
| `V` | `V-3`, a citation into the accounting set (`reviews/R14:159`, `:193`, `:520`) | Same as `N`; and `V` is the Flyway prefix |
| `W` | `W-1`, `W-3`, `W-5`, `W-6` in `reviews/R6` | A small local register, but a register |
| `M` | nothing with a hyphen (`M3` in `COEXISTENCE.md` has none) | The one free letter — **and one letter is not six** |

**Six lenses needed six registers; the alphabet offered one.** Renumbering an existing review to free
letters is forbidden — §6 already records that *"renumbering a **review** is forbidden — a review is a
dated record of what was found, and rewriting its ids makes every external citation of it wrong."*

**Two letters are unambiguous under the rule §6 already uses.** The mechanism that keeps `O-` and
`OD-` apart is `FINDING_CITE_RE` requiring **a hyphen immediately after the register prefix**: `OD-1`
can never be read as an `O-` finding because `O` is followed by `D`, not by `-`. The same mechanism
separates `RA-`…`RF-` from `R-` and from every single letter: `RA-001` has no hyphen after `R`, so it
is not an `R-` id, and `R-2` has no letter after `R`, so it is not an `RA-` id. The separation is
mechanical, not editorial — which is the only kind this set accepts.

**The checker obligation, stated so it is not lost.** `tools/check-design-set.py`'s
`FINDING_CITE_RE` is `\b([CTEFSPGQHUYZKOJ])-(\d{1,3}[a-z]?)\b(?!-\d)` — a **single-letter** class. It
therefore does not match `RA-001`…`RF-010` at all, which is why citing round-3 findings passes CI
today: **they are invisible to check 7, not validated by it.** That is a silent hole, not a feature.

> **Owed to a later wave (§5 row 22):** extend `FINDING_CITE_RE` and
> `RULE_TOKEN_RE["finding-citations"]` to admit the two-letter registers, add the six review paths to
> `REVIEWS`, and add their definition anchors to `FINDING_DEF_RE`, so that a round-3 citation resolves
> against its own authority exactly as a round-1 citation does. Until that lands, **every `RA-`…`RF-`
> citation in this set is unchecked.** This wave does not edit `tools/`.

---

## 8. Verification

```bash
cd /Users/bbhushan/work/git/workspace/warehouse-issues
python3 tools/check-design-set.py
# → 0 violations across 12 checks
```

**Stated rather than glossed:** two transient violations appeared mid-run and were **not** from these
two files — both cited `docs/GAP-REGISTER-R3.md`, which another author is writing concurrently
— both were **next-free allocation markers**, one screen id and one scenario id, which by
definition have no index row until the screen and the scenario are written. Isolating this wave's work by setting
that file aside for one run returned **0 violations**, and the file was restored byte-identical
(`diff -q` clean) before the final run above, which is also 0. Nothing in this wave edited it.

**What this wave wrote:** `docs/OPEN-DECISIONS-RESOLVED.md` (new) and `docs/DECISIONS.md` §3 and §6.
Nothing else in this repository, and nothing at all in `neetub1508/accounting` or
`neetub1508/classic`.

**What this wave did not do, on purpose:** it did not edit `DATA-MODEL.md` (`I-21` is owed, not
written), `DECISIONS.md` §4 (`L-15` is owed, not written), the FRD, the plan, the port contract,
`COEXISTENCE.md`, `IRREVERSIBLE.md`, `PLATFORM-DEPENDENCIES.md`, any task file, `tools/`, or
`GAP-REGISTER-R3.md`, which another author holds. **No row was deleted from any register**; a
resolved decision changes state and names this file.
