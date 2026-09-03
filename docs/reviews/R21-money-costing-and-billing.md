# R21 — money, costing and billing

> **Date** 2026-09-02 · **Branch** `docs/round-3-functional-completeness` · **Finding prefix** `RF-`
> (`grep -rohE "\bRF-[0-9]{1,3}\b" docs/ issues/ | wc -l` → **0**, so the namespace was free)
>
> **File set.** The design set is 190 markdown files / 61,102 lines
> (`find docs issues -name '*.md' | wc -l` → `190`; `cat $(find docs issues -name '*.md') | wc -l`
> → `61102`). Read whole: `docs/DECISIONS.md`, `docs/DATA-MODEL.md` §1.5, §2.1.11, §2.2, §2.3, §5,
> §6.3, §6.4, §7, `docs/PORT-AND-ADAPTER-CONTRACT.md` §2.3–§2.8 and §12,
> `docs/WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` §6.15–§6.18, `docs/COEXISTENCE.md` §2–§3,
> `docs/PLATFORM-DEPENDENCIES.md` §2.11–§2.12, and `issues/p0-17`, `p2-16`, `p2-17`, `p2-28`,
> `p5-01`, `p5-02`, `p5-03`, `p5-04`, `p5-05`, `p5-16`. Sibling set, read for the seam:
> `accounting/docs/DATA-MODEL.md` §2 (the inbox tables `:274`–`:278`, the stock tables `:434`–`:436`)
> and §5.1 (`:2443`–`:2470`). Prior lenses read before writing: `R14` (`O-001`…`O-007`), `R16`
> (`RA-`), `R17` (`RB-`), `R18` (`RC-`), `R19` (`RD-`), plus `GAP-REGISTER.md` and
> `GAP-REGISTER-R2.md` for every candidate below.
>
> **Method.** I walked every place the set derives a number, from the base-quantity conversion at
> post to the 3PL invoice, and asked one question of each: *can a customer or an auditor be shown
> this number a year later, from stated columns, and get the same answer?* Where the set already
> answers it, §3 records that so round 4 does not re-walk it. Where a **numbered open decision**
> already owns the question — `OD-11`, `OD-13`, `OD-14`, `OD-6`, `OD-7`, `OD-1` — I built on it and
> did not re-file it; §4 names the owner of every declined candidate.

---

## §1 · Verdict

**Ten findings: five BLOCKER, three MAJOR, two MINOR.**

The costing *architecture* is right, and it is better than anything shipping in this monorepo. `D-6`
puts the engine where the grain is; `FR-234` insists on layers **plus** consumptions rather than a
cost column on a balance; `FR-240` makes revaluation a document; `L-14` refuses to value other
people's goods; §5.3's five rounding rules and §5.4's rounding-away-from-zero analysis are the most
careful numeric writing in either design set. `C-027` — the live accessories defect where the
valuation report reads `last_cost` while the balance carries `average_cost` — is named, understood
and designed against.

What is missing is **the arithmetic itself**, in five places where the set states an outcome and
never states the algorithm that produces it. Each of the five is a number a customer will be shown:

1. **A backdated receipt.** `FR-237` and `p2-16` require the moving average to *recompute forward*.
   `I-2`'s line trigger ships an **empty** mutable-column allowlist and `DATA-MODEL.md:2480` says in
   terms that `moving_average_after` is frozen. The v1 acceptance box cannot be passed by any
   implementation, and the two documents disagree about whether last month's average restates.
2. **Negative stock.** `negative_stock_mode = ALLOW` is a v1, seeded, per-item×per-site policy with
   its own resolver table and its own log table. `issues/p2-16.md` contains the word *negative* zero
   times. What an issue costs when no layer is open, and what the covering receipt then does to the
   value already relieved, is undefined — and every conservation invariant passes while it is wrong.
3. **Landed cost on a partly-consumed layer.** `WH-SC-153` is a **v1 happy path** that states both
   *"+4,500.00 at the receipt location"* and *"₹2,700 revalues the 72 EA remaining … ₹1,800 posts as
   a COGS adjustment"*. Those cannot both be true; taken as written the remaining stock is
   overstated by ₹25/EA. No column anywhere records the split.
4. **Foreign currency.** `FR-245`, `WH-SC-160` and `p2-16`'s acceptance are v1 and all three need an
   exchange rate. `PLATFORM-DEPENDENCIES.md` §2.12 proves there is **no rate source in the entire
   monorepo**, offers two options, decides neither, and is not an `OD-` row. The port has no
   `exchange_rate` field. Nothing states which currency `unit_cost` and `layer_value` are in.
5. **The value that crosses to accounting.** `FR-233` hands over *"the unit cost and extended value
   warehouse computed"*. The receiving schema has `quantity`, `unit_cost` and one date — **no
   extended-value column, no currency, no `cost_basis`** — so accounting must re-multiply and
   re-round, which is the re-costing step `FR-446` falsifier 2 exists to forbid.

The 3PL biller has the same shape one level up: the meter and the contract exist in **two**
documents that disagree on eleven columns, and the rating *modifiers* every 3PL contract contains —
free days, a minimum monthly charge, aged surcharge bands, a rounding mode — are named in the
requirement and in the task and exist in **no table in either**.

None of the ten is expensive today. Four of them (`RF-001`, `RF-004`, `RF-005`, `RF-006`) become
irreversible or publicly embarrassing later: `RF-001`'s trigger is written in `V500030`, which is
`PNR-1` and `PNR-2` collapsed into one file; `RF-005`'s missing column is in the *other* repository,
whose P3 is still unbuilt — exactly the window `OD-1` was created to use.

---

## §1.1 · The money surface, computed

Every place this set derives a number. Counts are commands, run in the repository root:

```bash
grep -cE "^\| \*\*FR-[0-9]+\*\*.*(cost|value|charge|rate card|price|amount|billing)" \
  docs/WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md                                            # → 107
grep -cE "^\| \`(whb|wh|wh3|whin|wha)[a-z_0-9]*\` \|.*(unit_cost|layer_value|extended_cost|amount|charge|rate|declared_value|write_down|assessed_nrv|value_consumed|total_value)" \
  docs/DATA-MODEL.md                                                                   # → 63
grep -c "₹" docs/SCENARIO-CATALOGUE.md                                                 # → 30
grep -rlE "unit_cost|layer_value|allocated_amount|charge|rate card" issues/p*.md | wc -l # → 29
```

**107 requirements, 63 table rows, 30 worked rupee figures and 29 task files touch money.** The
derivations themselves:

| # | Number derived | From | Ver | Verdict |
|---|---|---|---|---|
| 1 | `base_quantity` = `quantity × conversion_factor_used` | `R-5`, `L-7`, `IRR-34` | v1 | **sound** — frozen factor, round-away-from-zero rule, counter side negated not reconverted (§5.4) |
| 2 | `moving_average_after` at post | `FR-237`, `IRR-39` | v1 | **`RF-001`** — the forward recompute is forbidden by `I-2` |
| 3 | FIFO relief = Σ `value_consumed` over layers in receipt order | `FR-234`, `WH-SC-149` | v1 | sound for the happy path; **`RF-002`** when no layer is open |
| 4 | Specific-identification relief | `FR-235`, `WH-SC-150` | v1 | **`RF-006`** — no `method` value can select it |
| 5 | `layer_value` = `quantity_in × unit_cost` | `whb_cost_layers` | v1 | sound arithmetic; **`RF-004`** — currency undeclared |
| 6 | Foreign-currency cost via `exchange_rate` | `FR-245`, `WH-SC-160` | v1 | **`RF-004`** — no rate source, no wire field |
| 7 | Landed-cost apportionment across receipt lines | `R-4`, `FR-238`/`FR-239` | v1 | basis and largest-remainder stated; **`RF-003`** for the split, **`RF-009`** for the tie-break |
| 8 | Layer vs COGS split on a partly-consumed layer | `FR-238`, `WH-SC-153` | v1 | **`RF-003`** — no columns, no destination, scenario self-contradictory |
| 9 | `wh_revaluation_lines.value_change` | `FR-240` | v1 | sound — a document, not an `UPDATE`; `old_unit_cost`/`new_unit_cost` both stored |
| 10 | Count variance value | `FR-236`, `count_snapshot_quantity` | v1 | sound — snapshot quantity frozen (`IRR-52`) |
| 11 | Inter-site transfer at sending-site cost, plus a transfer price | `FR-236`, `FR-244` | v1 | rule stated; the *second* number has no column — see §3 note |
| 12 | Opening-balance value and the go-live tie-out | `FR-249`, `FR-411`…`FR-413` | v1 | sound — a movement with layers, not a column |
| 13 | Handed-over envelope value | `FR-233`, `FR-248` | v1 | **`RF-005`** — no receiving column, no currency, no clock mapping |
| 14 | Stock-to-GL reconciliation | `FR-247` | v1 | shape owned by `RC-002`; the inputs are `RF-005`'s |
| 15 | As-at valuation, ageing value per bucket | `FR-387`, `WS-211`/`WS-212` | v1 | owned by `RC-003` — do not re-file |
| 16 | Storage charge = method × basis × rate | `FR-288`, `P5-04` | v2 | **`RF-007`** — 4 of 5 methods, 4 of 7 bases, no modifiers |
| 17 | Activity rating = event × rate-card line | `FR-287`, `P5-02`/`P5-03` | v2 | **`RF-008`** — the meter's rating columns exist in one document only |
| 18 | Minimum monthly true-up | `FR-290`, `WH-SC-237` | v2 | **`RF-007`** — the minimum itself has no column |
| 19 | SLA penalty amount | `FR-297`/`FR-299` | v2·v3 | sound — numerator and denominator both stored (`wh3_sla_measurements`) |
| 20 | Freight billing in four modes | `FR-295` | v2 | sound — `markup_percent` `DECIMAL(9,6)`, `markup_fixed`, reconciled on carrier invoice |
| 21 | NRV write-down and its reversal | `FR-241` | v2 | sound — a register with `reversal_of_assessment_id` |
| 22 | Tax-basis second inventory value | `FR-250`, `P4-11` | v2 | deferred with an argument — not a finding |
| 23 | Client profitability contribution | `FR-302` | v3 | deferred; inputs (labour minutes, snapshots) ship earlier |

**Where the arithmetic runs.** `FR-031` is right and is worth restating because it is the one rule
that cannot be repaired later: there is **no arbitrary-precision decimal library anywhere in this
monorepo**. Verified:

```bash
cd /Users/bbhushan/work/git/workspace/classic          # the live checkout, not this repo
find . -maxdepth 3 -name package.json -not -path "*/node_modules/*"   # → 3 files
# ./package.json ./mobile/package.json ./platform/frontend/package.json
grep -rn "decimal\|bignumber\|big\.js\|dinero\|currency\.js" --include=package.json . # → 0 hits
```
`platform/frontend/package.json` declares 38 dependencies and `mobile/package.json` 46; none is a
decimal library. Any value computed in the browser or in React Native is IEEE-754 double. No screen
in `BUILD-SPEC-SCREENS.md` asks for a client-side computation, and `FR-031` forbids it — that is
sound, and it is the reason `RF-009`'s tie-break matters: the split must be identical on the server
every time, because nothing downstream can re-derive it.

---

## §2 · The findings

### `RF-001` · The moving average must recompute forward on a backdated receipt, and the ledger's own immutability trigger forbids the write that does it — **BLOCKER**

- **What I found.** Four documents require a backdated receipt to restate the weighted average on
  the movement rows that follow it. `IRREVERSIBLE.md:217` (`IRR-39`): *"A backdated receipt
  recomputes the average."* `WH-SC-151` (`docs/SCENARIO-CATALOGUE.md:352`), a **v1·P2** scenario:
  *"The average recomputes from 20 August forward."* `issues/p2-16.md:140`: *"Backdating recomputes
  forward and must do it **inside the posting transaction**, not in a nightly job."* And the
  acceptance box, `issues/p2-16.md:168`: *"a backdated receipt recomputes forward in the posting
  transaction, **and the prior period's figure is still reproducible from the snapshots**."*
  `moving_average_after` lives on `whb_stock_movement_lines` (`docs/DATA-MODEL.md:697`). That table
  is governed by `I-2`, whose line trigger is created with an **empty** mutable-column array —
  `whb_reject_posted_mutation('{}')` at `docs/DATA-MODEL.md:2472-2475` — and whose design note at
  `:2477-2481` says it in words: *"Everything else — including `unit_cost`, **including
  `moving_average_after`**, including `occurred_at` — is frozen. Adding a sixth column to this array
  is a design decision with an argument, not a convenience."* `L-2` (`docs/DECISIONS.md:315`) adds
  two more layers: a writer service with no update method, and no repository path.
  So the recompute is impossible, and the acceptance box is unpassable as written. Worse, the two
  halves of the acceptance box want opposite things: if the snapshots restate, *"the prior period's
  figure"* is the **new** average, not the one that was true on 31 August; if they do not restate,
  the average is never recomputed at all and every issue after the backdate relieves at a stale
  cost. **Nobody has chosen which.** There is no FIFO counterpart at all: a backdated receipt
  creates a layer whose `layer_date` precedes layers already consumed, and no document says whether
  the existing `whb_cost_layer_consumptions` rows are reversed and re-drawn (the
  `reversal_of_consumption_id` column exists, `docs/DATA-MODEL.md:856`) or left alone.
  A secondary drift makes the collision arrive sooner than the version labels suggest:
  `docs/DATA-MODEL.md:697` marks `moving_average_after` *"v1.1 AVCO"* and
  `docs/PORT-AND-ADAPTER-CONTRACT.md:282` says *"Columns v1; AVCO v1.1, FIFO v1.1"*, while `OD-6`,
  `FR-235` and `issues/p2-16.md:49` all ship AVCO **and** FIFO in **v1**.
- **Evidence.**
  ```bash
  grep -c "negative" issues/p2-16.md                                  # → 0   (see RF-002)
  grep -n "trg_whb_movement_lines_immutable" docs/DATA-MODEL.md       # → 2472
  grep -rn "recomputes forward\|recomputes the average" docs/ issues/ # → IRR-39, WH-SC-151, p2-16 ×2
  ```
  - `docs/DATA-MODEL.md:2472-2475` — the trigger, allowlist `'{}'`.
  - `docs/DATA-MODEL.md:2477-2481` — *"including `moving_average_after` … is frozen"*.
  - `docs/DATA-MODEL.md:2328` — `I-2`, enforcement `T` + `S`, migration `V500030`.
  - `docs/DECISIONS.md:315` — `L-2`, three layers.
  - `docs/IRREVERSIBLE.md:217` — `IRR-39`, `PNR-1`.
  - `docs/SCENARIO-CATALOGUE.md:352` — `WH-SC-151`, **v1·P2**.
  - `issues/p2-16.md:140`, `:168` — the trap and the acceptance box.
- **Why it matters.** This is the number `p2-16` calls *"the number the customer signs"*. Whichever
  way an implementer resolves it silently, the customer gets a defensible answer to only one of the
  two questions an auditor asks — *"what is the cost today"* and *"what was the cost on 31 March"* —
  and cannot be told which one is wrong. `IRR-39`'s own justification cites the live accessories
  defect where the reversal path *"recomputes the average by subtracting the reversed receipt's own
  cost, which is not the inverse of a weighted average"* (`R1 C-027`); an unstated backdating rule
  is the same defect with better intentions.
- **Cost if found late.** The trigger is written in `V500030`, which `DATA-MODEL.md:2903` marks
  *"`PNR-1` **AND** `PNR-2`, collapsed into one file"* — after it, `UPDATE` is refused to every actor
  including `ADMIN`, and a column added later is `NULL` forever with no backfill path because the
  backfill is an `UPDATE`. If the answer turns out to be *"the restated average is a new row"*, that
  row needs a table that does not exist, and it cannot be reconstructed for history.
- **Recommendation.** Decide it now, before `P0-02`. The answer that costs nothing later and keeps
  every invariant: **`moving_average_after` is never restated.** It is a snapshot of what the average
  was when that line posted, which is precisely what `IRR-39` says it is for. A backdated receipt
  then does what a backdated receipt does in a layered engine — it inserts a layer, and the *current*
  average is `Σ open layer_value / Σ open quantity_remaining`, computed on read from the layer table,
  never stored. Rewrite `IRR-39`, `WH-SC-151` and `issues/p2-16.md:140`/`:168` to say so, and add the
  falsifier: *post a backdated receipt, re-read a movement line that follows it, assert
  `moving_average_after` is byte-identical to what it was before.* State the FIFO rule in the same
  edit: a backdated layer is consumed by **future** issues only; already-written consumptions are
  never re-drawn, because `L-2` and `L-3` make correction a reversal and the layer link is what
  `P4-04`'s ITC reversal walks. If instead the set wants restatement, `I-2`'s allowlist grows a sixth
  column in `V500030` — and that is the design decision `DATA-MODEL.md:2481` demands an argument for.
  Folds into **`P2-16`** and **`P0-02`**; amends `IRREVERSIBLE.md` `IRR-39`, `SCENARIO-CATALOGUE.md`
  `WH-SC-151`, `DATA-MODEL.md` §6.4. Migration: `V500030` only if the allowlist changes.

---

### `RF-002` · Negative stock is a shipped v1 policy with its own resolver table, and the costing engine never says what an issue costs when no layer is open — **BLOCKER**

- **What I found.** `L-6` (`docs/DECISIONS.md:319`) makes negative on-hand *"a policy"*, and the set
  builds that policy properly: `whb_item_site_settings.negative_stock_mode` ∈
  `BLOCK`/`WARN`/`ALLOW` (`docs/DATA-MODEL.md:535`), a most-specific-first resolver table
  `whb_negative_stock_policies` (`:828`), an `I-6` trigger that calls the resolver rather than a
  single `SELECT` (`:2543-2556`), a `wh_insufficient_stock_log` row for *"every `WARN`/`ALLOW`
  breach"* (`issues/p2-01.md:45-48`), and an `admin_settings` default. All v1.
  The costing engine says nothing about it. `grep -c "negative" issues/p2-16.md` → **0**. Under
  FIFO, an issue with `quantity_remaining = 0` across every open layer has **no stated unit cost**:
  the implementer picks zero, or the last known unit cost, or the standard cost, and each choice is
  a different set of books. Under AVCO the arithmetic is worse than undefined — `p2-16`'s own
  formula is `Σ layer_value / Σ quantity`, and at on-hand ≤ 0 that is a division by zero or a
  negative average. And nothing states what happens when the covering receipt arrives: the classic
  ERP answer is that the negative issue must be **retro-costed** to the receipt's cost, which is a
  restatement of an already-posted relief and therefore collides with `L-2` exactly as `RF-001`
  does. `L-1` conservation, `L-4` rebuild and `I-6` all pass throughout, because they check
  quantities and this is a value failure — §5.4 makes precisely this argument about a different
  rounding case: *"the one place in this design where a wrong number would look verified."*
- **Evidence.**
  ```bash
  grep -c "negative" issues/p2-16.md                                     # → 0
  grep -rn "no open layer\|insufficient layer\|layers are exhausted" docs/ issues/  # → 0 hits
  grep -rn "negative_stock_mode" docs/ issues/ | wc -l                   # → 6
  ```
  - `docs/DECISIONS.md:319` — `L-6`.
  - `docs/DATA-MODEL.md:535`, `:828`, `:2543-2556` — the policy, the resolver, the trigger.
  - `issues/p2-01.md:45-48`, `:141` — the `WARN`/`ALLOW` log, v1.
  - `issues/p2-16.md:36-46` — the layer/consumption scope, with no empty-layer case.
- **Why it matters.** A customer who turns `ALLOW` on — and the set ships it, defaults it from
  `admin_settings` and logs it, so customers will — gets a valuation that drifts by an amount nobody
  can quantify after the fact, because the issue that had no cost is indistinguishable from an issue
  that legitimately cost zero. The stock-to-GL reconciliation (`FR-247`) then shows a variance with
  no drillable cause, which is the exact failure `FR-247` exists to prevent.
- **Cost if found late.** Recoverable only by re-costing a period from the ledger, which the append-
  only design makes a reversal-and-repost exercise across every affected issue. If the answer is
  retro-costing, it needs a stated relationship between the negative relief and the covering receipt
  — a column or a consumption row shape — and adding that after `V500021` means history has none.
- **Recommendation.** State the rule in `P2-16`, in one paragraph, with a scenario. The defensible
  answer: **an issue with no open layer creates a negative layer** — a `whb_cost_layers` row with
  negative `quantity_remaining`, `cost_basis = 'ESTIMATED'`, and `unit_cost` taken from the resolved
  policy source (last receipt cost, then standard cost, then zero, in that order, recorded on the
  row) — and the covering receipt **consumes the negative layer first**, writing an ordinary
  consumption row that carries the difference as a *cost-variance* value-only movement rather than
  restating the original relief. That keeps `L-2` intact, keeps the difference visible on a report,
  and makes the retro-cost an auditable event rather than an edit. Add two scenarios — `ALLOW` issue
  with no layer, then the covering receipt — and an acceptance box asserting the variance movement
  exists and nets to zero. Folds into **`P2-16`** (+ one line in `P2-01`); needs a `cost_basis`
  vocabulary value, so it touches `V500021`'s DDL comment, not the ledger.

---

### `RF-003` · Landed cost on a partly-consumed layer has no split columns and no destination, and the v1 scenario that shows the split posts all of it into stock — **BLOCKER**

- **What I found.** `FR-238` (`docs/WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md:441`) requires that where a
  receipt layer is already partly consumed, the charge *"splits into a layer adjustment and a **COGS
  adjustment for what already shipped**"*. `issues/p2-17.md:17-19` repeats it and `:108` makes it an
  acceptance box: *"Applying against a partly-consumed layer produces **both** a layer adjustment and
  a COGS adjustment, distinguishable by their classification quads."* The worked example,
  `WH-SC-153` (`docs/SCENARIO-CATALOGUE.md:354`), is **v1·P2, happy path**, and it contains both of
  these sentences:
  > *"It posts as a zero-quantity, non-zero-value movement: **`+4,500.00` at the receipt location**
  > and `−4,500.00` at `VIRT-LANDED-COST-OFFSET`"* … *"The ₹4,500 spreads at ₹37.50/EA and
  > **splits**: ₹2,700 revalues the 72 EA remaining in the layer, and ₹1,800 posts as a COGS
  > adjustment for the 48 that already shipped."*

  The receipt location is a stock-bearing location. If `+4,500.00` lands there, the 72 remaining
  units carry ₹4,500 of freight instead of ₹2,700 — **₹25.00/EA of overstatement on a ₹412.50 unit,
  6.1%** — and the goods that consumed the other ₹1,800 never see it. The two sentences cannot both
  be true. Beneath the scenario, the schema cannot record the split either:
  `wh_landed_cost_allocations` is `(landed_cost_document_id, grn_line_id, basis_value,
  allocated_amount)` (`docs/DATA-MODEL.md:1105`) — one amount per receipt line, with no
  layer/COGS division and no record of the layer's remaining quantity **at apply time**, which is
  the only input from which the split can be re-derived next year. And there is no destination for
  the COGS half: `FR-084`'s seeded virtual-location list
  (`docs/WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md:224`) is `SUPPLIER`, `CUSTOMER`, `ADJUSTMENT`, `SCRAP`,
  `PRODUCTION`, `IN_TRANSIT`, `COUNT_VARIANCE`, `OPENING_BALANCE`, `CONSUMED`, `JOB_WORKER` — ten
  rows, none of which is a cost-of-sales offset.
- **Evidence.**
  ```bash
  grep -rn "COGS" docs/*.md issues/*.md | wc -l          # → 10 mentions, 4 of them the same sentence
  grep -n "wh_landed_cost_allocations" docs/DATA-MODEL.md # → 1105, 3211, 3642
  ```
  - `docs/WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md:441` — `FR-238`, the split.
  - `docs/SCENARIO-CATALOGUE.md:354` — `WH-SC-153`, the self-contradicting v1 happy path.
  - `docs/DATA-MODEL.md:1105` — the allocation table's four columns.
  - `docs/WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md:224` — `FR-084`'s ten seeded virtual locations.
  - `issues/p2-17.md:17-19`, `:87`, `:108` — scope, trap and acceptance box, all v1.
  - Related and **not** re-filed: `OD-11`/`OD-14` (whether value conserves), `OD-13` (what the offset
    location is called). This finding stands **after** both are closed as recommended — an `L-15`
    that asserts `+4,500 − 4,500 = 0` makes `WH-SC-153` balance while it is economically wrong.
- **Why it matters.** Freight capitalisation into the wrong half of a partly-shipped receipt
  overstates closing inventory and understates cost of sales, in the same period, by the same
  amount. That is a two-sided misstatement of profit, on the one document class — duty, freight,
  clearing — that arrives late by definition and therefore *always* lands on a partly-consumed
  layer. `R7 §1.7` records that no prior-art transport document in this monorepo connects freight to
  inventory value at all, so there is no existing behaviour to fall back on.
- **Cost if found late.** The columns are cheap now (`V510080` is unwritten) and impossible later:
  `quantity_remaining` is mutated in place, so the remaining-at-apply figure is unrecoverable once
  the layer moves on. `RC-003` already establishes that reading `quantity_remaining` as history is a
  defect; this is the same column with a second consumer, and unlike `RC-003`'s report the split
  cannot be rebuilt from `whb_cost_layer_consumptions` after the fact, because the allocation is not
  a consumption.
- **Recommendation.** Three edits, all in `P2-17`. (a) Add `quantity_remaining_at_apply`,
  `amount_to_layer` and `amount_to_cogs` to `wh_landed_cost_allocations` in `V510080`, with
  `amount_to_layer + amount_to_cogs = allocated_amount` as a `CHECK`. (b) Seed an eleventh virtual
  location for the cost-of-sales side and add it to `FR-084`'s list — the movement is then
  `+2,700` receipt location, `+1,800` COGS location, `−4,500` value offset, three lines, and both
  quantity and value conserve. (c) Rewrite `WH-SC-153`'s posting sentence to show the three lines it
  already computes in its second sentence, and add the falsifier: *apply a charge to a fully
  consumed layer and assert the stock value does not move at all.* Folds into **`P2-17`**; migration
  `V510080`; amends `FR-084`, `FR-238` and `WH-SC-153`.

---

### `RF-004` · Foreign-currency costing ships in v1 with no rate source anywhere in the monorepo, no field on the wire to carry one, and no statement of which currency `unit_cost` and `layer_value` are in — **BLOCKER**

- **What I found.** `FR-245` (`:448`) is v1: *"The cost layer carries `currency_code` and
  `exchange_rate` from v1."* `WH-SC-160` (`docs/SCENARIO-CATALOGUE.md:361`) is a **v1·P2 happy
  path** with a concrete rate — USD 42.00 at 88.4150. `issues/p2-16.md:72` and its acceptance box
  require both columns. `docs/DATA-MODEL.md:2069` reserves `DECIMAL(19,8)` for
  `whb_cost_layers.exchange_rate` *"and nothing else"*.
  Three things are missing under all of that.
  **(a) There is no rate.** `docs/PLATFORM-DEPENDENCIES.md` §2.12 (`:348-362`) runs the grep and
  reports it: `grep -rln "exchange_rate\|currency_rate\|fx_rate" --include=*.sql .` → **0 files**;
  `currencies` (`platform/…/V203:5-18`) carries code, name, symbol, decimal places and flags and *"no
  rate column of any kind"*. §2.12 then offers *"two honest options"* — v1 values in the single
  default currency only, or the rate rides the movement line frozen — **and decides neither**, ending
  with *"Do not build a rates table in `warehouse-base`"*. It is not an `OD-` row, so nothing gives
  it a deadline or an owner, and `OD-7` (precision) is the only currency-adjacent decision in
  `DECISIONS.md` §3.
  **(b) The wire cannot carry it.** The port's line-field table
  (`docs/PORT-AND-ADAPTER-CONTRACT.md:280-282`) has `unit_cost`, `cost_currency_code`,
  `extended_cost`, `cost_basis`, `moving_average_after`, `cost_layer_id` — and **no `exchange_rate`
  field**. §2.12's option (b) is therefore unbuildable as the contract stands. `cost_currency_code`
  is additionally marked *"Column v1, multi-currency **v2**"* both there and at
  `docs/DATA-MODEL.md:694`, while `FR-245` and `WH-SC-160` are v1.
  **(c) Nothing says which currency the stored numbers are in.** `whb_cost_layers` holds `unit_cost`,
  `layer_value`, `currency_code` and `exchange_rate` in one row (`docs/DATA-MODEL.md:855`). Is
  `unit_cost` 42.00 USD or 3,713.43 INR? Is `layer_value` the transaction amount or the base amount?
  The valuation report sums `layer_value` across layers; if the column is transaction currency the
  total is a sum of unlike units, and if it is base currency then `exchange_rate` is the only record
  of what was paid and `unit_cost` cannot be reconciled to the supplier invoice. Accounting solved
  the same problem by carrying **both** — `debit_amount` and `base_debit_amount` on every journal
  line (`accounting/docs/DATA-MODEL.md:2444`) with a `CHECK` tying their signs together. Warehouse
  carries one of each.
- **Evidence.**
  ```bash
  grep -rn "exchange_rate" docs/ issues/ | wc -l          # → 20, every one either the type ruling or the column name
  grep -rn "exchange_rate" docs/PORT-AND-ADAPTER-CONTRACT.md | grep -c "^docs.*| \`exchange_rate\`"  # → 0 wire fields
  ```
  - `docs/PLATFORM-DEPENDENCIES.md:348-362` — §2.12, *"No exchange-rate source"*, 0 files, two
    options, no decision.
  - `docs/PORT-AND-ADAPTER-CONTRACT.md:280-282` — the cost fields on the wire; no rate.
  - `docs/DATA-MODEL.md:694`, `:855`, `:2069` — `cost_currency_code` v2, the layer's four money
    columns, the `DECIMAL(19,8)` reservation.
  - `docs/SCENARIO-CATALOGUE.md:361` — `WH-SC-160`, **v1·P2, happy**.
  - `issues/p2-16.md:72`, `:103`, `:174` — scope, scenario, acceptance.
- **Why it matters.** `D-7` makes standalone the reference configuration, and a standalone install
  has no `acc_exchange_rates` to read — and `FR-231` forbids reading it even where accounting is
  present. So a v1 customer importing spares either types a rate into a field that does not exist,
  or gets a layer valued at 42.00 of something. The first import of foreign stock produces a
  valuation that is wrong by two orders of magnitude and looks like a decimal-place bug.
- **Cost if found late.** `IRR-36` already marks the cost-currency columns irreversible —
  *"retro-fitting currency onto a cost history is guessing"* — and the same is true of the rate.
  Layers created before the decision carry a rate of 1 or a NULL, and no algorithm recovers what was
  paid.
- **Recommendation.** Promote §2.12 to a numbered open decision in `DECISIONS.md` §3 with the
  deadline **before `P0-17` writes `V500021`**, and take the cheap answer: **v1 values in the
  install's single base currency; the layer's `currency_code`/`exchange_rate` record what was paid,
  supplied by the producer on the movement line, frozen at post exactly as `conversion_factor_used`
  is under `L-7`.** That requires one field on the wire (`exchange_rate`, `DECIMAL(19,8)`, optional,
  defaulting to 1), one sentence in §5.1 declaring that `unit_cost` and `layer_value` are **base
  currency** and `currency_code`/`exchange_rate` are the audit trail of the transaction amount, and
  one `CHECK` that `currency_code <> base` implies `exchange_rate IS NOT NULL`. Add the falsifier to
  `WH-SC-160`: *the valuation report totals in base currency and the layer detail shows USD 42.00.*
  Folds into **`P2-16`** and **`P0-17`**; migration `V500021`; amends
  `PORT-AND-ADAPTER-CONTRACT.md` §2.5, `DATA-MODEL.md` §5.1 and `PLATFORM-DEPENDENCIES.md` §2.12.

---

### `RF-005` · The value warehouse computes has no column to land in on the accounting side: the inbox carries `quantity`, `unit_cost` and one date — no extended value, no currency, no cost basis — so the receiver must re-cost, which `FR-446` forbids — **BLOCKER**

- **What I found.** `FR-233` (`docs/WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md:436`) states what crosses:
  per movement line, *"`owner_type`, `duty_status`, lot and serial identity, quantity, base UoM,
  **the unit cost and extended value warehouse computed**, and `cost_basis` declaring the basis on
  which it was computed"*, and adds *"**Accounting does not re-cost what it is handed**"*.
  `FR-446` makes that a build-time falsifier and `issues/p2-16.md:164` an acceptance box:
  *"the posted value equals warehouse's computed value exactly, and `grep` finds **no re-costing
  step** on the receiving side."*
  The receiving schema cannot hold it. `acc_source_document_movements`
  (`accounting/docs/DATA-MODEL.md:277`) is `direction`, `item_external_id`, `item_id`,
  `godown_external_id`, `godown_id`, `quantity`, `unit_cost`, `movement_date`, `status`,
  `valuation_entry_id`. **There is no extended-value column, no currency column and no `cost_basis`
  column.** The alternative array, `acc_source_document_lines` (`:275`), does carry an extended
  `amount` — but no item-location, lot, serial or owner, so it cannot value a stock movement. And
  **no document in either set says which array a warehouse handover fills**: `whb_accounting_handovers`
  has an `envelope_kind` column (`docs/DATA-MODEL.md:858`) whose vocabulary is stated nowhere
  (`grep -rn "envelope_kind" docs/ issues/` → 4 hits, none enumerating values).
  Three consequences follow mechanically.
  **(a) The value is re-derived, not received.** With only `quantity` and `unit_cost` on the wire,
  `acc_valuation_entries.value` (`accounting/docs/DATA-MODEL.md:436`) must be computed as
  `quantity × unit_cost` on the receiving side. That is the re-costing step `FR-446` falsifier 2
  forbids, and it is also a **second rounding**: warehouse rounds `extended_cost` to
  `DECIMAL(19,4)` once, at post (`R-2`, `docs/DATA-MODEL.md:2123-2126`); accounting re-multiplies a
  `DECIMAL(19,6)` unit cost (`accounting/docs/DATA-MODEL.md:2449`) by a `DECIMAL(18,4)` quantity and
  rounds to `DECIMAL(19,4)` (`:2452`) again. The two agree for round numbers and differ by up to
  half a paisa per line for AVCO costs, which — as accounting's own §5.2 argument says — *"almost
  never land on two decimals"*. Every one of those differences lands in `FR-247`'s variance column
  as an unexplained reconciling item.
  **(b) `L-14` and `cost_basis` do not survive the crossing.** `grep -rn "cost_basis" accounting/docs`
  → **0**; `grep -rn "ZERO_BAILMENT" accounting/docs` → **0**; `grep -rn "extended_cost"
  accounting/docs` → **0**. `owner_type` appears 37 times in the accounting set and **every one is
  about whether `branches` is polymorphic** (`accounting/docs/ACCOUNTING-FUNCTIONAL-REQUIREMENTS.md:446`),
  not about the owner of goods. Warehouse's gate — do not emit an envelope for non-own stock — is
  the only thing preventing a 3PL's client stock reaching a balance sheet, and it is a service rule
  with no receiving-side backstop.
  **(c) The clock is unmapped.** `L-13` gives warehouse three timestamps and `OD-12` decides which
  one partitions. `acc_source_document_movements` has one, `movement_date`, and the header has
  `document_date`, `posting_date` and `source_timezone` (`:274`). `grep -rn "movement_date" docs/
  issues/` finds **10 hits in this set, none of them about the handover** — every one is a quote of
  a review or of the accessories schema. Which of `occurred_at`, `recorded_at` and `posting_date`
  becomes `movement_date` is unstated on both sides, and it is the field that decides which
  accounting period a movement lands in.
- **Evidence.**
  ```bash
  cd ../accounting
  grep -rn "extended_cost" docs/ | wc -l     # → 0
  grep -rn "cost_basis"    docs/ | wc -l     # → 0
  grep -rn "ZERO_BAILMENT" docs/ | wc -l     # → 0
  grep -rn "owner_type"    docs/ | wc -l     # → 37, all about branches
  cd ../warehouse-issues
  grep -rn "envelope_kind" docs/ issues/ | wc -l   # → 4, no vocabulary
  ```
  - `accounting/docs/DATA-MODEL.md:274-277` — the inbox header and the three normalised arrays.
  - `accounting/docs/DATA-MODEL.md:436` — `acc_valuation_entries.value`, computed there.
  - `accounting/docs/DATA-MODEL.md:2449`, `:2452` — the two precisions the double rounding crosses.
  - `docs/WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md:436` — `FR-233`, what warehouse believes it sends.
  - `docs/DATA-MODEL.md:858` — `whb_accounting_handovers`, `envelope_kind` undefined.
  - **Not** `O-001` (no third install state), **not** `O-002` (`account_strategy` cannot resolve the
    classification quad), **not** `O-003` (the status ladders do not map), and **not** `OD-1`'s text,
    which books the stand-down and *"the port's `unit_cost` semantics"*. This finding is what remains
    **after** all four are done: there is still no column for the extended value, the currency or the
    basis, and still no statement of which array or which clock.
- **Why it matters.** `FR-247`'s reconciliation is the report that makes a finance director trust
  the system, and accounting makes it a blocking close precondition. A per-line half-paisa
  difference multiplied across a month of picks produces a variance that is small, permanent and
  undrillable — the worst possible shape, because it trains everyone to ignore the report.
- **Cost if found late.** `acc_source_document_movements` is `P3` and unbuilt, which is exactly the
  window `OD-1` was created to use. Once it has rows the column is an `ALTER` plus a backfill that
  has no source, because the warehouse-side envelope is stored as `TEXT` for replay
  (`docs/DATA-MODEL.md:858`) and re-parsing archived payloads to synthesise a value column is the
  unreconstructible-axis failure the accounting set already records once for its inbound dimensions
  (`accounting/docs/DATA-MODEL.md:346`).
- **Recommendation.** Carry it into `OD-1` as a **fourth** reciprocal edit, explicitly: add
  `extended_value`, `currency_code`, `exchange_rate` and `cost_basis` to
  `acc_source_document_movements`, and a receiving rule *"where `extended_value` is present it is
  authoritative; `quantity × unit_cost` is never recomputed"*. On this side, enumerate
  `envelope_kind`'s vocabulary in `DATA-MODEL.md` §2.1.11 and state in `P2-18` that a warehouse
  handover fills `movements[]`, that `movement_date` = the warehouse `posting_date` (`L-13`'s
  accounting clock, not `occurred_at`), and that `cost_basis = ZERO_BAILMENT` suppresses the
  envelope entirely. Add the falsifier to `P2-18`: *post one AVCO issue whose extended value does
  not equal `round(quantity × unit_cost, 4)`, and assert the accounting-side value matches
  warehouse's to the paisa.* Folds into **`P2-18`** (+ `P0-12`) and one amendment in the
  `accounting` repository; no warehouse migration.

---

### `RF-006` · Specific identification is a v1 requirement, a v1 happy-path scenario and a v1 acceptance box, and `whb_valuation_policies` has no method value that can select it — **MAJOR**

- **What I found.** `FR-235` requires *"specific identification for serial- and lot-tracked items"*
  and says why: *"required here even though the accounting set defers it, because vehicles,
  high-value electronics and any serialised spare are non-interchangeable by definition."*
  `WH-SC-150` (`docs/SCENARIO-CATALOGUE.md:351`) is **v1·P2, happy path**: serial
  `ECU55010000771` relieves at ₹49,600, *"not the average and not FIFO"*. `issues/p2-16.md:167` makes
  it an acceptance box. `GAP-REGISTER.md:1158` sells it — the electronics vertical is *"SERVES WITH
  ADDITIONS"* on the strength of specific identification at v1.
  `whb_valuation_policies.method` is `AVCO`/`FIFO`/`STANDARD` (`docs/DATA-MODEL.md:853`). There is
  no fourth value. `OD-6`'s recommendation (`docs/DECISIONS.md:292`) names only weighted average and
  FIFO for v1 and standard cost for v1.1, and does not mention specific identification at all — so
  the open decision that must close before `P2-16` merges does not decide the method the task's own
  acceptance box tests.
  The policy **grain** cannot express it either. The unique key is
  `(company_id, category_id, warehouse_id, effective_from)` — a policy is chosen by item *category*
  and site. Serial control is an item attribute (`whb_items.serial_control_mode`), not a category:
  one category routinely contains both serialised and non-serialised items, and `FR-235` scopes
  specific identification to *"serial- and lot-tracked items"*, not to categories. So even adding a
  `SPECIFIC` value leaves no way to say *"this category is FIFO, except its serialised members"*.
- **Evidence.**
  ```bash
  grep -rn "AVCO\`/\`FIFO\`/\`STANDARD" docs/DATA-MODEL.md    # → 853, the whole vocabulary
  grep -rn "SPECIFIC" docs/DATA-MODEL.md docs/DECISIONS.md    # → 0 as a method value
  ```
  - `docs/DATA-MODEL.md:853` — `method` ∈ `AVCO`/`FIFO`/`STANDARD`, uk on category × warehouse.
  - `docs/WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md:438` — `FR-235`.
  - `docs/SCENARIO-CATALOGUE.md:351` — `WH-SC-150`, v1 happy.
  - `issues/p2-16.md:49-53`, `:167` — the scope paragraph and the acceptance box.
  - `docs/DECISIONS.md:292` — `OD-6`, which does not mention it.
  - `docs/GAP-REGISTER.md:1158` — the electronics vertical claim that rests on it.
- **Why it matters.** A dealer selling a ₹49,600 ECU and relieving it at a ₹48,266 average has
  overstated that sale's margin by ₹1,334 and understated the next one's — and for vehicles, which
  `OD-2` explicitly contemplates moving onto this ledger in v3, the per-unit differences are lakhs.
  It is also the argument `D-6` uses to justify putting the costing engine in warehouse at all
  (*"not expressible at accounting's item × godown × batch × serial grain"*), so shipping without it
  weakens the decision that shapes the whole module.
- **Cost if found late.** Low if caught before `V500021`, because the method vocabulary and the
  policy key are both in that one migration. After it, changing the policy key restates every
  balance — `IRR-40` marks the valuation grain `PNR-3` for exactly this reason.
- **Recommendation.** Close `OD-6` with four methods, not three, and make the resolution rule
  explicit rather than emergent: **`SPECIFIC` is not a policy value at all — it is implied.** An item
  whose `serial_control_mode` requires a serial is costed by specific identification regardless of
  the category policy, because its layer is already keyed by `serial_id`
  (`docs/DATA-MODEL.md:855`) and there is exactly one layer to consume. One sentence in `P2-16` and
  one in `FR-235` (*"specific identification is selected by the item's serial control, not by the
  valuation policy; the policy governs interchangeable stock only"*) closes it with no schema change
  and no fourth enum value. If instead it is to be a policy value, add `SPECIFIC` to `V500021` and
  add an item-level override column to the policy key **before** `PNR-3`. Folds into **`P2-16`**;
  amends `OD-6`, `FR-235` and `DATA-MODEL.md` §2.1.11.

---

### `RF-007` · Every rating modifier a 3PL contract actually contains — the minimum monthly charge, free days, minimum billable quantity, aged surcharge bands, the rounding mode — is named in the requirement and in the task and exists in no table — **MAJOR**

- **What I found.** `FR-282` requires the client to carry *"a go-live date, **a minimum monthly
  charge** and a tax profile"*. `FR-288` requires storage billing *"over seven bases — pallet,
  location, unit, weight, cubic, square feet occupied and square feet allocated — with **free days,
  a minimum billable quantity and aged-inventory surcharge bands**"*, in *"four methods"* which it
  then lists as five (period-end, period-start, anniversary, daily average **and split month**).
  `FR-290` requires the minimum monthly charge to post a true-up. `issues/p5-04.md:27` repeats the
  bases and modifiers verbatim; `issues/p5-04.md:56` makes free days an acceptance-adjacent trap —
  *"a pallet received on the 28th with 7 free days has no billable storage month at all"* — and
  `:67` says a pallet is charged a whole month *"unless the contract says pro-rata"*.
  None of it has a column. `wh3_clients` (`docs/DATA-MODEL.md:1147`) is 13 columns and has no
  minimum charge, no minimum scope, no go-live date and no tax profile. `wh3_rate_card_lines`
  (`:1153`) has `rate`, `minimum_quantity`, `tier_from`, `tier_to`, `charge_kind`, `basis`,
  `sequence` — no free quantity, no maximum charge, no rounding mode, and `basis` is
  *"(whitelisted)"* with the whitelist stated nowhere. `wh3_storage_billing_periods` (`:1155`)
  offers `method` ∈ `PERIOD_END`/`PERIOD_START`/`ANNIVERSARY`/`AVERAGE_DAILY` — **four of the five**,
  no split month — and `basis` ∈ `PALLET`/`SQFT`/`CBM`/`UNIT` — **four of the seven**, with location,
  weight and the occupied/allocated distinction absent. `wh3_storage_billing_lines` (`:1156`) has
  `age_days` and `anniversary_anchor_date` but no free-day, band or proration column.
  These are not oversights of invention: **R4 specified every one of them** and they were dropped in
  the re-homing. `docs/reviews/R4-fulfilment-3pl-audit.md:789` — *"`wh3pl_clients.minimum_monthly_charge`
  + `minimum_scope`"*; `:714` — *"`minimum_charge`, `maximum_charge` nullable, `free_quantity`,
  `rounding_mode`"*; `:754` — *"`free_days`, `minimum_billable_quantity`, and
  `wh3pl_storage_aging_bands`"*. `GAP-REGISTER.md:339`/`:341` record `F-015` and `F-017` as **CITED**
  into `P5-04`, so the register believes they are carried.
- **Evidence.**
  ```bash
  grep -rn "free_days\|minimum_monthly\|minimum_charge\|tax_profile" docs/ issues/
  # → 6 hits: 4 in reviews/R4 (the proposal), 1 in issues/p5-01.md:27 (prose), 1 unrelated
  grep -rn "SPLIT_MONTH\|split_month" docs/ issues/ | wc -l     # → 1, in COMPETITOR-BENCHMARK prose
  grep -rn "rounding_mode" docs/ issues/ | wc -l                # → 1, in reviews/R4
  ```
  - `docs/DATA-MODEL.md:1147`, `:1153`, `:1155`, `:1156` — the four tables, as shipped.
  - `docs/WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md:521`, `:527`, `:529` — `FR-282`, `FR-288`, `FR-290`.
  - `issues/p5-04.md:27`, `:56`, `:67` — the scope line, the free-days trap, the pro-rata clause.
  - `docs/reviews/R4-fulfilment-3pl-audit.md:714`, `:754`, `:789` — the columns that existed once.
- **Why it matters.** This is revenue, and it fails in the direction that loses money quietly.
  A biller with no free-day column bills the free days — the client notices and disputes, and the
  3PL loses the argument and the credibility. A biller with no minimum-charge column cannot compute
  `WH-SC-237`'s ₹25,700 true-up at all: `FR-290` calls the manual version *"the single most common
  source of leaked 3PL revenue"*, and without the column the automatic version is the manual version.
  A biller with four of seven bases cannot quote the two square-foot variants, which is how
  ambient-warehouse contracts are written.
- **Cost if found late.** Moderate and rising. These are configuration columns on v2 tables that
  do not exist yet, so today it is a DDL edit. After the first billing run they are an `ALTER` plus a
  re-rate of a period a client has already paid, and `FR-292` forbids re-rating after approval — so
  the correction is an ad-hoc run of reversing events per client per period.
- **Recommendation.** Restore R4's columns into `DATA-MODEL.md` §2.3 and the `V530010`/`V530021`/
  `V530031` DDL: `wh3_clients.{go_live_date, minimum_monthly_charge, minimum_scope, tax_profile_id}`;
  `wh3_rate_card_lines.{free_quantity, minimum_charge, maximum_charge, rounding_mode}`;
  a `wh3_storage_aging_bands` child of the rate-card line; `wh3_storage_billing_lines.{free_days_applied,
  days_charged, is_prorated}`. Extend `method` with `SPLIT_MONTH` and `basis` with `LOCATION`,
  `WEIGHT` and the occupied/allocated split, or amend `FR-288` down to what will be built and say so
  — either is fine, disagreeing is not. Enumerate `wh3_rate_card_lines.basis`'s whitelist in the same
  edit. Folds into **`P5-01`**, **`P5-02`** and **`P5-04`**; migrations `V530010`, `V530021`,
  `V530031`.

---

### `RF-008` · The billing meter and the client contract are specified twice, and the two specifications disagree on eleven columns, on the rate-card status vocabulary and on whether the meter can be updated at all — **MAJOR**

- **What I found.** `DATA-MODEL.md` is the schema authority. Its `wh3_billable_events`
  (`:1154`) has 17 columns: `event_code`, `client_id`, `owner_id`, `warehouse_id`, `charge_code`,
  `quantity`, `uom_code`, `occurred_at`, `posting_date`, `source_system`, `idempotency_key`,
  `outbox_cursor`, `subject_type`, `subject_id`, `is_reversed`, `reversal_of_event_id`,
  `billing_run_id`. `issues/p5-03.md:22-30` specifies the same table with **`source_event_key`**
  (not `idempotency_key`), eight nullable subject FKs instead of the `subject_type`/`subject_id`
  pair, and six columns the data model does not have: **`rate_card_line_id`, `unit_rate`,
  `rated_amount`, `currency_code`, `status` ∈ {`METERED`,`RATED`,`BILLED`,`REVERSED`,`EXCLUDED`},
  `exclusion_reason_code`**. `FR-285` cites `(source_system, source_event_key)` as the key;
  `DATA-MODEL.md:1154`'s unique index is on `(source_system, idempotency_key)`.
  The same drift runs through the money path. `wh3_clients` (`:1147`) lacks the three contract terms
  `issues/p5-01.md:27` requires (`RF-007`). `wh3_billing_runs` (`:1157`) carries `rate_card_id` — a
  card — while `issues/p5-05.md:12` requires *"rate-card **version** used"*. `wh3_rate_cards.status`
  is `DRAFT`/`ACTIVE`/`SUPERSEDED` (`:1152`) and `issues/p5-02.md:20` says
  `DRAFT → ACTIVE → EXPIRED` — the vocabulary that decides which card is live when an event is
  rated.
  And the two copies contradict each other on mutability. `DATA-MODEL.md:104` lists
  `wh3_billable_events` among the tables with **no `updated_at`/`updated_by`**, because it is
  *"append-only by invariant (`L-2`)"*. `issues/p5-03.md:28` says *"The only columns an `UPDATE` may
  touch are the rating fields and `billing_run_id`"* — an update path on a table with no audit
  columns to record that it happened.
  The money consequence is single and sharp: **whether the rate applied to an event is stored at
  event grain.** With `p5-03`'s columns it is, and `WH-SC-236`'s promise — *"a dispute three months
  later re-rates to the same number"* — is answerable. With the data model's columns it is not: the
  only stored rate is `wh3_billing_run_lines.rate` (`:1158`), one line per charge code, so a period
  spanning a rate-card version change (which is exactly `WH-SC-236`) collapses two rates into one
  line and one `amount`, and the run header names a single `rate_card_id` that is wrong for half the
  events. `FR-293` disputes and `FR-287`'s *"rated against the version live on that event's date"*
  both become unprovable.
- **Evidence.**
  ```bash
  grep -n "wh3_billable_events" docs/DATA-MODEL.md            # → 104, 1154, 1450, 3048
  sed -n '22,30p' issues/p5-03.md                             # → the 11 divergent columns
  grep -n "rate-card version used" issues/p5-05.md            # → 12
  grep -n "DRAFT → ACTIVE → EXPIRED" issues/p5-02.md          # → 20
  ```
  - `docs/DATA-MODEL.md:104`, `:1147`, `:1152`, `:1154`, `:1157`, `:1158` — the schema of record.
  - `issues/p5-01.md:27`, `p5-02.md:20`, `p5-03.md:22-30`, `p5-05.md:11-12` — the other one.
  - `docs/SCENARIO-CATALOGUE.md:478` — `WH-SC-236`, the re-rate promise.
- **Why it matters.** `DECISIONS.md` §7 rule 3 requires every cross-reference to resolve and
  `check-design-set.py` check 3 asserts task-file tables exist in `DATA-MODEL.md` — which they do,
  by name. Nothing checks the **columns**, so this drift is invisible to the gate and visible only
  to whoever writes `V530030`. Whichever document they pick decides whether a client dispute can be
  answered, and they will pick the one in front of them.
- **Cost if found late.** `wh3_billable_events` is the 3PL equivalent of the stock ledger — append-
  only, reversible, and the sole evidence behind every invoice. Adding `unit_rate`/`rated_amount`
  after the first billed period means every historical event has NULL rating data and every historical
  dispute is answered from the aggregated run line or not at all.
- **Recommendation.** Reconcile in `DATA-MODEL.md` §2.3 — it is the authority, so it takes
  `p5-03`'s columns, not the reverse — and resolve the three specific conflicts explicitly:
  `source_event_key` vs `idempotency_key` (pick one, it is a unique index), the eight subject FKs vs
  the generic pair (the generic pair is the house style, §1.9), and `SUPERSEDED` vs `EXPIRED`. Then
  state the mutability rule once: the meter is append-only **except** `billing_run_id` and the four
  rating columns, guarded by a `to_jsonb`-diff trigger with an explicit allowlist — the same shape
  as `I-2`, and the reason `wh3_billable_events` needs `updated_at`/`updated_by` after all, so
  `DATA-MODEL.md:104` must lose that row. Folds into **`P5-03`** (+ `P5-01`, `P5-02`, `P5-05`);
  migrations `V530010`, `V530021`, `V530030`.

---

### `RF-009` · `R-4`'s largest-remainder tie-break is `line_no`, and two of the three cases `R-4` itself names have no `line_no` — **MINOR**

- **What I found.** `R-4` (`docs/DATA-MODEL.md:2132-2139`) is the apportionment rule, and it is
  stated well: floor each provisional share, distribute the remaining minor units *"largest
  fractional remainder first, **ties broken by `line_no`**"*, so `Σ parts == whole` always. It names
  three consumers: *"landed cost apportioned across receipt lines, **a minimum charge trued up
  across charge codes**, **a kit's cost across outputs**."*
  Only the first has a `line_no`. `wh_landed_cost_allocations` carries `grn_line_id`
  (`:1105`), and a GRN line has an ordinal — fine. `wh3_billing_run_lines` (`:1158`) is
  `run_id`, `charge_code`, `quantity`, `uom_code`, `rate`, `amount`, `event_count`,
  `computation_note`, `is_minimum_true_up`, `is_sla_credit`, `accessorial_id`, `dispute_id` — **no
  ordinal column of any kind**, and its only index is `idx(run_id)`. The kit case (`P3-11`,
  `FR-261`…`FR-265`) has no output-line table named anywhere in §2.2.
  A largest-remainder split whose tie-break is undefined is not deterministic: two runs of the same
  arithmetic can assign the odd paisa to different charge codes, and `R-4`'s own justification —
  *"the apportionment must be reproducible next year"* — fails on the exact case `FR-290` calls the
  most common source of leaked revenue.
- **Evidence.**
  ```bash
  grep -n "ties broken by" docs/DATA-MODEL.md issues/*.md | wc -l   # → 4 restatements of R-4
  grep -n "wh3_billing_run_lines" docs/DATA-MODEL.md                # → 1158, 3050 — no line_no
  ```
  - `docs/DATA-MODEL.md:2132-2139` — `R-4` and its three named cases.
  - `docs/DATA-MODEL.md:1158` — the run-line columns.
  - `issues/p2-17.md:33-36`, `issues/p2-16.md:143-146` — `R-4` restated in both tasks.
- **Why it matters.** Small money, but it is the class of defect that destroys trust in a biller:
  the same period re-rated twice produces two invoices differing by one paisa on two lines, and a
  client who spots it has grounds to question everything else.
- **Cost if found late.** Trivial to fix, embarrassing to explain. One column.
- **Recommendation.** Add `line_no INTEGER NOT NULL` to `wh3_billing_run_lines` with
  `uk(run_id, line_no)` in `V530040`, and name the kit-output ordinal when `P3-11`'s table is
  specified. Amend `R-4` to say *"ties broken by the sink's declared ordinal — `line_no` on a
  document line, `line_no` on a billing run line, `sequence` on a kit output — and every sink of a
  largest-remainder split must declare one."* Folds into **`P5-05`** (+ a line in `P3-11` and one in
  `DATA-MODEL.md` §5.3); migration `V530040`.

---

### `RF-010` · The two documents a reader consults about the accounting seam still quote the overruled version of `D-6` — *"accounting is the system of record for value"* — **MINOR**

- **What I found.** `DECISIONS.md:146-195` rewrote `D-6` to *"whichever system is authoritative for
  quantity is authoritative for cost"*, overruled `R5 S-066` explicitly, and `FR-230` carries the
  rewrite. Two documents still quote the superseded sentence as if it were current, in quotation
  marks and attributed to `D-6`:
  - `docs/COEXISTENCE.md:152-154` — *"`D-6` resolves it in one sentence — «`warehouse` is the system
    of record for every movement, position, count, adjustment and physical truth, at full grain;
    `accounting` is the system of record for **value**»"*.
  - `docs/COMPETITOR-BENCHMARK.md:583` — the same clause, in the competitive positioning section.
  A third, `COMPETITOR-BENCHMARK.md:966`, records the question as *"**AMBIGUOUS.** Resolve inside
  `OD-1`/`OD-6`"*, which `D-6`'s rewrite closed and `DESIGN-SET-DEFECTS.md:1623` (`X-032`) already
  fixed for `IRREVERSIBLE.md` §7.3 — the same stale-quote defect, in a document nobody swept.
- **Evidence.**
  ```bash
  grep -rn "system of record for \*\*value\*\*\|system of record for value" docs/ issues/  # → 2
  ```
  - `docs/COEXISTENCE.md:154`, `docs/COMPETITOR-BENCHMARK.md:583` — the stale quote.
  - `docs/DECISIONS.md:146-195`, `docs/WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md:433` — the live rule.
  - `docs/DESIGN-SET-DEFECTS.md:1623` (`X-032`) — the precedent: the same staleness in
    `IRREVERSIBLE.md` §7.3 was filed as a defect because *"a settled decision gets re-opened"*.
- **Why it matters.** `COEXISTENCE.md` is the document a builder reads when asking *"who owns the
  number"* — it is the only place the `acc_source_document_movements.unit_cost` write-once problem is
  written down (`:167-174`), which is `RF-005`'s neighbourhood. A builder who reads `:154` and stops
  builds the seam backwards, and `D-6`'s own text warns that *"a builder who half-remembers `D-6`
  will build the wrong thing"* (`issues/p2-16.md:8`).
- **Cost if found late.** One wrong conversation with a customer's finance team, or one wrong
  handover implementation caught in review. Cheap, but free to fix now.
- **Recommendation.** Replace both quotes with `D-6`'s current sentence and add the second half —
  *"and therefore for cost"* — and update `COMPETITOR-BENCHMARK.md:966`'s row from **AMBIGUOUS** to
  the resolution, citing `X-032`'s precedent. No task, no migration; a documentation edit that
  travels with `RF-005`.

---

## §3 · What I checked and found sound

Recorded so round 4 does not re-walk it. Each of these is a place a number is derived where the set
already answers the audit question.

1. **The precision ruling is cited, not re-derived** (`docs/DATA-MODEL.md` §5.1, `:2055-2083`).
   Both normative tie-breaks are restated verbatim with the warehouse column that catches people
   (`whin_delivery_challan_lines.unit_value`), and the sixth kind — the UoM conversion factor at
   `DECIMAL(18,8)` — is offered to `OD-7` as a recommendation carrying an argument rather than
   asserted. `OD-7` is open with a deadline; that is a decision, not a gap.
2. **`HALF_UP` everywhere, and the `float8` trap is named greppably** (`R-1`, `:2114-2122`).
   PostgreSQL's `round(numeric, int)` is HALF_UP while `double precision` is banker's rounding, so
   `::float`, `::double precision` and `CAST(… AS DOUBLE PRECISION)` are forbidden on any warehouse
   numeric column. This is the single most valuable line in §5 and I could not fault it.
3. **Round once, and complementary pairs by subtraction** (`R-2`, `R-3`). `available = on_hand −
   reserved`, `variance = counted − snapshot`, `net = gross − tare` — every pair sums back to its
   parent exactly, by construction rather than by a second rounding.
4. **The rounding-away-from-zero analysis** (§5.4, `:2145-2201`) is the best numeric writing in
   either design set: it identifies that `L-1` would *pass* on a zero base quantity, chooses a
   bounded visible error over a silent one, explains the 122% overstatement it accepts and why,
   generates the counter-side line from the primary rather than reconverting it (which is what makes
   `is_counter_side` exist), and records the rejected alternative so it is not re-proposed.
5. **Cost is layers plus consumptions, never a column on a balance** (`FR-234`, `IRR-38`), with the
   trap stated: ship both tables even where the policy is AVCO, because an AVCO-only v1 has nothing
   to build layers from when the customer switches. `whb_cost_layer_consumptions.reversal_of_
   consumption_id` is what makes a return restore the original layers (`WH-SC-152`).
6. **Revaluation and NRV are documents and registers, not `UPDATE`s** (`FR-240`, `FR-241`).
   `wh_revaluation_lines` stores `old_unit_cost` **and** `new_unit_cost`; `wh_nrv_assessments`
   stores `reversal_of_assessment_id` because Ind AS 2 requires reversal when the cause ceases.
   Both are derivable after the fact.
7. **`L-14` is a schema fact, not only a service rule** (`docs/DATA-MODEL.md:865-868`):
   `owner_type.posts_to_our_gl = false` ⇒ no value on the handover, `movement_type.is_financial =
   false` ⇒ no envelope at all. The 3PL catastrophe in both directions is designed against.
   (`RC-006` owns the fact that it is written onto only one screen; I did not re-file.)
8. **LIFO is refused with a citation and a reason** (`FR-235`, `WH-SC-161`), including the
   instruction that the method dropdown must not offer it. A migrating customer's question has a
   written answer.
9. **`FR-031` and the absence of a frontend decimal library** — verified above with a command. No
   screen in `BUILD-SPEC-SCREENS.md` asks for client-side arithmetic.
10. **Storage billing reads persisted snapshots and never recomputes occupancy** (`FR-289`,
    `P5-04`), with a re-run **superseding** rather than updating, and the `PNR-3` consequence stated
    plainly: a period before the snapshot job started cannot be billed by any method, and the screen
    must say so rather than returning zero.
11. **The SLA measurement stores numerator and denominator**, not just the percentage
    (`FR-297`) — the one thing that makes an SLA conversation possible.
12. **Freight billing's four modes** (`FR-295`) with `markup_percent` correctly typed
    `DECIMAL(9,6)` under tie-break 2, and the pass-through reconciled when the carrier invoice lands.

**One thing I checked, could not close, and am not filing as a defect.** `FR-244` requires an
inter-branch transfer to carry **two numbers** — a transfer price for the tax document and a cost
that follows the goods — *"plus the data to eliminate unrealised profit"*. `FR-236` states the cost
half (transfer at the sending site's cost, so no profit sits in stock). I could not find a column
for the **transfer price** on `wh_transfer_orders`/`_lines` or on `whin_delivery_challans` other
than `declared_value` (`docs/DATA-MODEL.md:1196`), and I could not establish from the documents
whether `declared_value` **is** the transfer price or a separate insurance figure. If it is the
transfer price the requirement is met and one sentence should say so; if it is not, this is a real
gap. **UNVERIFIED** — what would settle it: a `valuation_basis`/`declared_value` semantics sentence
in `DATA-MODEL.md` §2.4 or in `p2in-01`, or a worked `WH-SC-` scenario showing both numbers on one
transfer.

---

## §4 · Refused

Every candidate I declined, and the existing id that owns it.

| Candidate I could have filed | Owned by | Why I did not file |
|---|---|---|
| Value-only movements do not conserve value; `L-1`…`L-14` conserve quantity only | **`OD-11`**, **`OD-14`**, `PC-12` | Numbered open decisions with deadlines and recommendations. `RF-003` builds on them and survives their closure |
| The value-offset location has three names and `FR-084` seeds none — and `WH-SC-153` uses a **fourth**, `VIRT-LANDED-COST-OFFSET` | **`OD-13`**, `X-029` | The name is `OD-13`'s to settle; the fourth spelling is evidence for it, not a new finding. I flag it here only so the decider sees all four |
| The as-at valuation reads `quantity_remaining`, which is mutated in place | **`RC-003`** | Explicitly owned by R18. `RF-003` cites the same column for a different consumer (the landed-cost split) and says so |
| Cost and value are visible to any actor who can open the report | **`K-002`**, `FR-450` | Round 2, folded into `P1-18` |
| The stock-to-GL reconciliation has no GL column and no owner or item-group grain | **`RC-002`** | R18 owns the report's shape; `RF-005` owns the inputs it reconciles |
| Seven as-at reports do not say which of `L-13`'s three clocks they read | **`RC-001`** | R18. `RF-005`'s clock claim is about the **handover** field `movement_date`, not about a report parameter |
| The accounting set has no third install state / `account_strategy` cannot resolve the quad / the status ladders do not map | **`O-001`**, **`O-002`**, **`O-003`** | R14 owns the seam as such. `RF-005` is what remains after all three are done |
| The precision types are not authoritative until someone closes them | **`OD-7`** | An open decision with a deadline (*before `P0-02`*) and a recommendation to adopt accounting's set verbatim |
| Valuation-method scope in v1 | **`OD-6`** | Open decision. `RF-006` reports that its recommendation omits a method the v1 acceptance box tests — a different claim |
| No union valuation report across warehouse and accessories | **`OD-15`**, `X-036`, `M3` | Decided: do not build in v1, make the separation explicit |
| The warehouse manager's approval threshold *by value* has no column | **`RA-008`** | R16 |
| The counter clerk cannot price a line; no price table exists | **`RA-002`** | R16. Price is not cost — `FR-041` keeps it off the ledger line, correctly |
| Reports are grids and the grid has no footer, so a valuation total has nowhere to render | **`RC-004`** | R18 |
| `currencies.default_decimal_places CHECK (<= 4)` cannot display a `DECIMAL(19,6)` unit cost | `PLATFORM-DEPENDENCIES.md` §2.11, folded into **`OD-7`** | Already written down with the instruction *"decide the display rule with `OD-7`, not after"* |
| Standard cost with purchase-price and usage variances is v1.1, not v1 | `FR-235`, `DECISIONS.md` §5 | A deferred capability is a decision. No v1 requirement, screen or task depends on it |
| COGS recognition point, the tax-basis second value and client profitability are v2/v3 | `FR-243`, `FR-250`, `FR-302` | Same — deferred with arguments, and none costs an irreversible column now |

---

## §5 · Counts

```bash
cd /Users/bbhushan/work/git/workspace/warehouse-issues
grep -c "^### \`RF-" docs/reviews/R21-money-costing-and-billing.md                  # → 10
grep -o "\*\*BLOCKER\*\*$" docs/reviews/R21-money-costing-and-billing.md | wc -l    # → 5
grep -o "\*\*MAJOR\*\*$"   docs/reviews/R21-money-costing-and-billing.md | wc -l    # → 3
grep -o "\*\*MINOR\*\*$"   docs/reviews/R21-money-costing-and-billing.md | wc -l    # → 2
python3 tools/check-design-set.py | tail -1                                         # → 0 violations across 12 checks
```

| Severity | Count | Findings |
|---|---|---|
| **BLOCKER** | **5** | `RF-001` `RF-002` `RF-003` `RF-004` `RF-005` |
| **MAJOR** | **3** | `RF-006` `RF-007` `RF-008` |
| **MINOR** | **2** | `RF-009` `RF-010` |
| **Total** | **10** | |

**By disposition** — nine fold into existing tasks; **no new task is proposed**. One (`RF-005`)
requires an amendment in the sibling `accounting` repository, carried by `OD-1`.

| Finding | Folds into | Migration touched | Deadline | Irreversible? |
|---|---|---|---|---|
| `RF-001` | `P2-16`, `P0-02` | `V500030` **only if** `I-2`'s allowlist changes | **before `P0-02`** | yes if the allowlist changes — `V500030` is `PNR-1`+`PNR-2` |
| `RF-002` | `P2-16` (+ one line in `P2-01`) | `V500021` DDL comment / `cost_basis` vocabulary | before `P2-16` merges | no, but history is uncostable |
| `RF-003` | `P2-17` | `V510080` (three columns) + `V500013` (one seed row) | before `P1-05` seeds `V500013` | the split is unrecoverable once `quantity_remaining` moves |
| `RF-004` | `P2-16`, `P0-17` | `V500021` (+ one port field) | **before `P0-17`** | yes — `IRR-36`, currency cannot be retro-fitted |
| `RF-005` | `P2-18`, `P0-12`; **`OD-1`** carries the accounting-side edit | none here; `accounting` `P3` DDL | before accounting `P3` starts | yes once `acc_source_document_movements` has rows |
| `RF-006` | `P2-16` | none if selected by serial control; `V500021` if a fourth method | before `OD-6` closes | the policy **key** is `PNR-3` (`IRR-40`) |
| `RF-007` | `P5-01`, `P5-02`, `P5-04` | `V530010`, `V530021`, `V530031` | before `P5` starts | no, but a billed period cannot be re-rated (`FR-292`) |
| `RF-008` | `P5-03` (+ `P5-01`, `P5-02`, `P5-05`) | `V530010`, `V530021`, `V530030` | before `V530030` is written | rating columns cannot be backfilled onto billed events |
| `RF-009` | `P5-05` (+ a line in `P3-11`) | `V530040` | before `P5-05` | no |
| `RF-010` | none — documentation edit, travels with `RF-005` | none | with the next `COEXISTENCE.md` edit | no |

**Two cross-cutting corrections** that are not findings in their own right but must travel with the
above, because both are load-bearing statements that are now false:

1. `docs/DATA-MODEL.md:697` and `docs/PORT-AND-ADAPTER-CONTRACT.md:282` label the valuation columns
   *"v1.1 AVCO, v1.1 FIFO"* while `OD-6`, `FR-235`, `DECISIONS.md` §5 and `issues/p2-16.md:49` all
   ship **both methods in v1**. The columns exist in v1 either way, so nothing breaks — but a
   builder reading the Feature column will not implement the engine in `P2`, and the v1 exit
   criterion requires a valuation report that reconciles.
2. `docs/DATA-MODEL.md:104` lists `wh3_billable_events` as having no `updated_at`/`updated_by`
   because it is append-only, and `issues/p5-03.md:28` gives it an update path for the rating
   columns. Whichever `RF-008` resolves to, that row must be corrected in the same commit — an
   updatable table with no audit columns is the shape of every unexplainable invoice.
