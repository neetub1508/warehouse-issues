# R11 — Exceptions, unhappy paths and concurrent business events

**Date:** 2026-09-02 · **Finding prefix:** `Y-` · **Branch:** `docs/round-2-functional-review`

**File set actually read — 17 files:**

```bash
cd /Users/bbhushan/work/git/workspace/warehouse-issues
# docs/: DECISIONS.md README.md GAP-REGISTER.md DESIGN-SET-DEFECTS.md
#        WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md DATA-MODEL.md SCENARIO-CATALOGUE.md
#        BUILD-SPEC-SCREENS.md IMPLEMENTATION-PLAN.md IRREVERSIBLE.md
#        PORT-AND-ADAPTER-CONTRACT.md PLATFORM-DEPENDENCIES.md COMPETITOR-BENCHMARK.md
# issues/: p0-04.md p0-10.md p1-15.md p2-08.md
ls docs/*.md | wc -l        # 20 in docs/, 13 of them read
```

**Method, in three sentences.** I built a 61-row inventory of the exceptions a real warehouse
produces — physical reality, process interruption, data and integration, people and authority — and
walked each one against the FRD, the data model, the scenario catalogue, the screen spec and the task
files, asking four questions: is it specified, is the *outcome* specified, if not what will the code
actually do reasoned from `L-1`…`L-14`, and does the result produce a wrong balance, a stuck document
or an unanswerable support question. Every row got a `grep`; every absence in this document prints the
command that established it. Findings that share a root cause are filed once with their symptoms
listed, per the brief.

---

## §1 · Verdict

**This design set is far better at unhappy paths than any predecessor I have reviewed, and it is not
finished.** The claim measures well: of 300 scenarios, **135 (45%) are non-happy and 65 (21.7%) are
hard `error` or `conc` cases** — computed below, not estimated. The `wh_blocked_movements` queue
(`FR-028`, `WH-SC-249`) is the single best decision in the set: it accepts that refusing a transaction
does not un-move the goods, which is the failure that turns warehouse staff into system-avoiders.
`WH-SC-190`…`WH-SC-198` are a genuine concurrency chapter, `L-9`'s different-payload replay is fully
answered by `FR-017`/`PC-17`/`WH-SC-165`, and `FR-165`'s rule — *a threshold column with no scheduled
job that reads it is a defect at the moment it is merged* — is exactly the right law.

**But `FR-165`'s law is not applied to itself.** Its enumeration lists ten dated obligations and omits
three abnormal-state clocks that the schema already carries: in-flight tasks, movements pending
approval, and unresolved queue rows. And two whole classes of exception are missing outright: **what
happens to stock the system has already moved when the reason for moving it disappears** (cancel after
pick), and **what happens to an open reservation when the stock underneath it changes status**
(quarantine, hold, recall, and the unattended nightly expiry job).

**Of the 61 exceptions I walked, 36 (59%) are specified to the point that a builder knows what to
code**, 13 are named but their *outcome* is not, and 12 are absent entirely. The count and its
derivation are in §2.1.

**The single most expensive one is `Y-002`.** A status change against stock that carries an open
reservation drives `quantity_available` negative, and `I-6` is a bare
`CHECK (quantity_available >= 0)` at `V500031` with **no policy escape and no error code in
`FR-039`'s vocabulary**. `FR-160`'s nightly auto-expiry job is a status change. So on the first night
a hard-reserved lot crosses its shelf-life threshold, an unattended job hits a raw PostgreSQL check
violation — no field-level error, no `BusinessException`, no queue row, and by `DECISIONS.md`'s own
standard *"a trigger firing in production is an incident, not a validation"*. Meanwhile the QA manager
who tries to quarantine contaminated stock that someone reserved this morning gets an opaque 500. This
costs nothing to fix now and costs a customer's confidence in month one.

`Y-001` is the one with a deadline: `on_behalf_of_actor_id` is mandated on **the movement** by
`PLATFORM-DEPENDENCIES.md:522-523` and is not in the movement header's column list, and that header is
`V500030` — `PNR-1`.

---

## §2 · The findings

### 2.1 · The exception coverage table

The measured framing first, with the commands:

```bash
cd docs && grep -cE '^\| \*\*WH-SC-[0-9]{3}\*\*' SCENARIO-CATALOGUE.md
# 300
grep -E '^\| \*\*WH-SC-[0-9]{3}\*\*' SCENARIO-CATALOGUE.md \
  | awk -F'|' '{print $(NF-1)}' | sed 's/ //g' | sort | uniq -c | sort -rn
#  165 happy
#   70 edge
#   52 error
#   13 conc
# non-happy = 70+52+13 = 135 / 300 = 45.0%   hard failure = 52+13 = 65 / 300 = 21.7%
```

**Verdict key.** `SPEC` = specified *and* the outcome is stated (resulting state, movement, reason
code, who is notified). `PART` = named somewhere, outcome not stated, or the outcome is deferred past
the version that ships the capability. `NONE` = no row anywhere outside `docs/reviews/`.

#### Group A · Physical reality (23)

| # | Exception | Authority | Outcome stated? | Verdict |
|---|---|---|---|---|
| A1 | Short shipment | `FR-130` `FR-122` · `match_status = QTY_UNDER` | yes — explicit close-short with reason | **SPEC** |
| A2 | Over-receipt beyond tolerance | `FR-130` · `wh_purchase_orders.over_receipt_tolerance_pct` · `FR-138` case type `over-receipt` | yes | **SPEC** |
| A3 | Damaged on arrival | `FR-122` (received/accepted/rejected/damaged) · `wh_goods_receipt_lines.{condition_code, rejection_reason_code_id, damage_notes}` · `FR-134` disposition | yes | **SPEC** |
| A4 | **Wrong item delivered** | — | — | **NONE** → `Y-005` |
| A5 | Wrong quantity | as A1/A2 | yes | **SPEC** |
| A6 | Goods with no paperwork | `wh_goods_receipts.is_blind_receipt` · `FR-124` nullable supplier | column exists; no rule for no-PO/no-ASN/no-supplier | **PART** |
| A7 | Paperwork with no goods | `FR-130` `QTY_UNDER` · `FR-138` ASN case | yes | **SPEC** |
| A8 | **Unlabelled pallet** | — | — | **NONE** → `Y-009` |
| A9 | Mixed-lot pallet | `FR-087` `commingle_policy = SINGLE_LOT` · `whb_lpns.is_mixed_lot` · `LOCATION_POLICY_VIOLATED` | yes | **SPEC** |
| A10 | Expired lot at receipt | `FR-161` point 1 — refuse receipt below X% shelf life remaining | yes | **SPEC** |
| A11 | Expired lot discovered at pick | `FR-160` `EXPIRED` state; physically-expired-but-system-clean falls to `FR-028` | generic queue only | **PART** |
| A12 | Lot expiring between allocation and despatch | `FR-161` point 3 — refuse to ship below Y days remaining | yes | **SPEC** |
| A13 | Serial not in system | `FR-039` `UNKNOWN_ITEM` · `FR-097` · `FR-028` | generic queue only | **PART** |
| A14 | Serial in wrong location | `whb_serials.current_location_id` exists; no reconcile rule | no | **PART** |
| A15 | Serial scanned twice | `FR-039` `SERIAL_ALREADY_ISSUED` · `FR-097` `uk(owner,item,serial)` · `FR-106` | yes | **SPEC** |
| A16 | **LPN split** | — | — | **NONE** → `Y-006` |
| A17 | **LPN merged** | — | — | **NONE** → `Y-006` |
| A18 | **Lost LPN** | — | — | **NONE** → `Y-006` |
| A19 | Stock found with no record | `FR-153` count → `COUNT_ADJ` vs `VIRT-COUNT-VAR` · `FR-145` reason code | yes (for an *identifiable* item) | **SPEC** |
| A20 | Record with no physical stock | as A19 | yes | **SPEC** |
| A21 | Bin cannot hold what putaway suggested | `FR-086` (enforced v1.1) · `WS-082` captures the override reason in v1 | v1 accepts with a captured reason — ugly but correct | **PART** |
| A22 | **Quarantined after putaway *and allocated*** | `FR-103` posts the movement; nothing decides the reservation | no | **NONE** → `Y-002` |
| A23 | Recall | `FR-280` `FR-270` `WH-SC-137` — quarantine in place, release reservations, no disposition restocks | yes (v2) | **SPEC** |

#### Group B · Process interruption (20)

| # | Exception | Authority | Outcome stated? | Verdict |
|---|---|---|---|---|
| B1 | Cancel before allocation | `FR-132` PO cascade with stock gate · `FR-171` | yes | **SPEC** |
| B2 | Cancel after allocation | `FR-171` · `WH-SC-096` — availability returns to **exactly** its pre-allocation value | yes | **SPEC** |
| B3 | **Cancel mid-pick** | — | — | **NONE** → `Y-003` |
| B4 | Cancel after pack | `FR-183` names *unpack* as a compensating action — **v1.1/P3**, while pack ships v1/P2 | deferred past the capability | **PART** |
| B5 | Cancel after ship | `FR-183` — *"after ship there is no edit; the answer is a return or an RTO"* | yes | **SPEC** |
| B6 | Amend quantity after allocation | `FR-183` · `WH-SC-095` rule matrix + amendment log | yes (v1.1) | **SPEC** |
| B7 | Substitute item mid-pick | `FR-176` is *allocation-time* supersession; `wh_demand_order_lines.{original_item_id, substitution_reason_code_id}` exist | no mid-pick path | **PART** |
| B8 | **Pick task abandoned (log-off, dead device)** | — | — | **NONE** → `Y-004` |
| B9 | Wave released against stock since gone | `FR-185` short pick — exception code, reservation released, three offered actions, auto cycle-count | yes | **SPEC** |
| B10 | Count started on a location being picked | `WH-SC-192` — both `freeze_locations` branches stated | yes | **SPEC** |
| B11 | Two operators picking the same location | `WH-SC-191` — resolved at allocation, not at pick | yes | **SPEC** |
| B12 | Two allocations racing for the last unit | `WH-SC-190` `FR-175` — `@Version` + `CHECK` + lock ordering | yes | **SPEC** |
| B13 | **Putaway half-completed** | — | — | **NONE** → `Y-004` |
| B14 | Receipt whose purchase document is cancelled afterwards | `FR-132` — refused if any GRN line has received stock or an `ARRIVED` ASN exists | yes | **SPEC** |
| B15 | Backdated movement | `FR-007` `L-13` three timestamps · `WH-SC-250` catch-up entry | yes | **SPEC** |
| B16 | Movement into a soft-closed period | `L-8` · `PERIOD_CLOSED` · approved override | yes | **SPEC** |
| B17 | Movement into a hard-closed period | `L-8` — admits nothing | yes | **SPEC** |
| B18 | Reversal of a reversal | `FR-005` · `CANNOT_REVERSE_A_REVERSAL` in `FR-039` | yes | **SPEC** |
| B19 | Transfer despatched to a site then closed | `FR-147`–`FR-149` per-transfer in-transit + ageing report; nothing about the receiving site being deactivated | no | **PART** → `Y-007` |
| B20 | Shipment refused at the customer's door | `FR-270` `return_type` includes refused delivery and cancelled in transit | yes | **SPEC** |

#### Group C · Data and integration (12)

| # | Exception | Authority | Outcome stated? | Verdict |
|---|---|---|---|---|
| C1 | Idempotency key replayed with a **different payload** | `FR-017` `FR-033` `PC-17` `WH-SC-165` `WH-SC-166` `IRR-04` — `409 IDEMPOTENCY_KEY_REUSED`, body names the original movement id, nothing posted, nothing overwritten | yes, exhaustively | **SPEC** |
| C2 | Out-of-order arrival, `occurred_at` before a posted movement | `WH-SC-170` — sufficiency evaluated at **post** time, not as-at, and the refusal routes to the blocked-move queue | yes | **SPEC** |
| C3 | Movement referencing an item deactivated since | `FR-051` blocks deactivation with stock; nothing about a zero-stock deactivated item receiving a new movement | partial | **PART** |
| C4 | UoM conversion factor changed after movements exist | `FR-009` `L-7` — factor frozen on the line; `WH-SC-011` replays the frozen factor on reversal | yes | **SPEC** |
| C5 | **Location deleted or merged with stock in it** | — | — | **NONE** → `Y-007` |
| C6 | **Owner deactivated holding stock** | — (`FR-051` covers items only) | — | **NONE** → `Y-007` |
| C7 | Negative available attempted | `FR-014` `L-6` `I-6` `WH-SC-190` | yes | **SPEC** |
| C8 | Negative on-hand under per-item policy | `WH-SC-018` — `BLOCK`/`WARN`/`ALLOW`, most-specific-first, log row + report on every breach | yes | **SPEC** |
| C9 | Rounding residue | `WH-SC-004` — rounded **away from zero** to the smallest representable base quantity; never offers the DB a zero base quantity for a non-zero transaction quantity | yes | **SPEC** |
| C10 | Position-cache rebuild disagrees with the ledger | `L-4` · `whb_position_drift_findings` · `WS-043` (Assign/Resolve) · `FR-163` · `wh_reconciliation_exceptions.age_days` · `WS-098` | **who is paged** is `FR-398`/`WS-223`, **v1.1** — v1 has the findings but no watcher | **PART** |
| C11 | Outbox backing up | `WH-SC-252` — at-least-once with backoff, dead-letter grid, `POST /outbox/replay?from_cursor=` | yes | **SPEC** |
| C12 | A consumer that never acknowledges | `WH-SC-252` — consumers read by gapless cursor and dedupe on `(consumer, sequence)`; base does not know its consumers | yes | **SPEC** |

#### Group D · People and authority (6)

| # | Exception | Authority | Outcome stated? | Verdict |
|---|---|---|---|---|
| D1 | **Operator loses permission for the next step of a started flow** | — | — | **NONE** → `Y-004` |
| D2 | Supervisor override — permission? reason? audit row? | all three, per surface: `wh_blocked_movements:force` *"mandatory reason + approver"* (`WS-097`) · `WS-082` putaway override reason *"captured, never silently discarded"* · `FR-408` approver ≠ actor · `whb_audit_events` hash-chained | yes | **SPEC** |
| D3 | An approval that never comes, goods on the dock | `FR-027` `WH-SC-039` — `PENDING`, no ledger effect; `WS-040` has the action and a tile | **no filter, no clock, no job, not a health signal** | **PART** → `Y-008` |
| D4 | Escalation path | `PLATFORM-DEPENDENCIES.md:51` names *"blocked-move escalation"* as a notification use case | no `FR-` row, no rule | **PART** → `Y-008` |
| D5 | Support engineer who must see customer data | `FR-409` `S-092` `IRR-61` `PD-D12` — consent, time-box, audit; `whb_audit_events.on_behalf_of_actor_id` | **the movement header does not carry the column** | **PART** → `Y-001` |
| D6 | Undoing a wrong adjustment at 6pm on a Friday | `FR-005` `L-3` `WH-SC-011` — mirror movement, mandatory reason, both visible; `L-8` decides whether the period admits it | yes | **SPEC** |

**The computed answer.**

```bash
# counting the verdict column of the four tables above
SPEC = A(1,2,3,5,7,9,10,12,15,19,20,23)=12 + B(1,2,5,6,9,10,11,12,14,15,16,17,18,20)=14
     + C(1,2,4,7,8,9,11,12)=8 + D(2,6)=2                                              = 36
PART = A(6,11,13,14,21)=5 + B(4,7,19)=3 + C(3,10)=2 + D(3,4,5)=3                       = 13
NONE = A(4,8,16,17,18,22)=6 + B(3,8,13)=3 + C(5,6)=2 + D(1)=1                          = 12
                                                                          total        = 61
```

**36 of 61 (59.0%) are specified to the point that a builder knows what to code.**

---

### `Y-001` · `on_behalf_of_actor_id` is mandated on the movement, is absent from the movement header, and the movement header is `PNR-1` — **BLOCKER**

- **What is missing or wrong:** `PLATFORM-DEPENDENCIES.md:522-523` states the requirement in exactly
  these words: *"carry `on_behalf_of_actor_id` on the movement and on the ledger's own audit event
  **from the first migration**"*. `whb_audit_events` has it (`DATA-MODEL.md:911`). The
  `whb_stock_movements` header column list (`DATA-MODEL.md:594-624`) carries `actor_type`,
  `actor_user_id` and `device_id` and **not** `on_behalf_of_actor_id`, and the *"Deliberately not on
  the header"* list at `DATA-MODEL.md:650-653` does not decline it either — so it is an omission, not
  a decision. `IMPLEMENTATION-PLAN.md:415` places the column in `P0-13` = `V500043`, thirteen versions
  **after** the ledger's `V500030`.
- **Why it matters:** the ledger, not the audit-event table, is where a stock posting lives. On day two
  of the first install support is asked *"who scrapped these twelve ECUs?"*. The audit event can answer
  it for a master-data change; the movement register — `WS-040`, *"the product's report number one"* —
  answers `stores1`, with no way to say *"support, acting as `stores1`"*. `IRR-61`'s own sentence
  applies verbatim to the movement: sessions recorded before the column exists are indistinguishable
  from the customer's own actions, which voids the audit claim retrospectively for that whole period.
  `L-2` makes the movement append-only and `V500030` seals it against `UPDATE`, so the value can never
  be written afterwards for year-one rows.
- **Negative evidence:**
  ```bash
  cd /Users/bbhushan/work/git/workspace/warehouse-issues
  sed -n '594,624p' docs/DATA-MODEL.md | grep -c on_behalf_of        # 0
  sed -n '650,653p' docs/DATA-MODEL.md | grep -c on_behalf_of        # 0  (not declined either)
  grep -rn "on_behalf_of" docs/ issues/ | grep -v '^docs/reviews'    # 8 hits, none on the movement header
  grep -n "on_behalf_of" docs/DATA-MODEL.md                          # 911 only — whb_audit_events
  ```
- **Where it belongs:** `warehouse-base` · v1 · P0
- **Disposition:** **fold into task `P0-02`.** Add to the `whb_stock_movements` header column list, next
  to `actor_user_id`: `` `on_behalf_of_actor_id` | UUID ↓platform `users(id)` | yes | v1 column, v1.1
  feature | `IRR-48` `IRR-61` `` — and one line to the task's acceptance list: *"the movement header
  carries `on_behalf_of_actor_id`, null until platform ships impersonation (`PD-D12`, `FR-409`)"*.
  Mirror it in `DATA-MODEL.md` §7.2's `WHB-*` row for `V500030`.
- **Irreversibility:** **`PNR-1` = `V500030`.** After the append-only seal the column can be added but
  never populated for existing rows, which is the whole point of `IRR-61`.
- **Relationship to round 1:** materially extends **`S-092`** / **`IRR-61`** / **`FR-409`**. What is new:
  round 1 and `GAP-REGISTER.md:1217` both close the finding on *"the schema half must land in the first
  audit migration"* — but `PLATFORM-DEPENDENCIES.md` asks for the column on **two** tables and
  `DATA-MODEL.md` delivers it on one, and the missing one is under an earlier point of no return than
  the one the register names.

---

### `Y-002` · A status change against stock that carries an open reservation has no stated outcome and no error code — and `FR-160`'s nightly expiry job is a status change — **BLOCKER**

- **What is missing or wrong:** `FR-103` makes a status change *"a balanced two-line movement at the
  same location with a mandatory reason code"*. `whb_reservations` carries `stock_status_code`
  (`DATA-MODEL.md:824`), so a reservation is held against a specific status. `FR-014` says
  `available = on_hand − Σ open reservations` **may never go below zero**, and `I-6` at `V500031`
  enforces it as a bare `CHECK (quantity_available >= 0)` with — deliberately, per
  `DATA-MODEL.md:2519-2523` — **no policy escape**, unlike the on-hand trigger beside it. Nothing
  anywhere states what happens when stock under an open reservation is moved to a status with
  `is_allocatable = false`. There is no error code for it in `FR-039`'s 43-code vocabulary, and no
  scenario. `WH-SC-137` *does* state *"every reservation allocated to it is released"* — but that is
  the **recall workflow, v2·P5**, not the v1 single-object status change (`FR-103`/`FR-152`/`P2-03`)
  and not the expiry job.
- **Why it matters:** three moments, and one of them is unattended.
  1. **The nightly job.** `FR-160` makes expiry *a state, not an alert*: a scheduled job sets `EXPIRED`.
     `EXPIRED` is not allocatable. The first night a hard-reserved lot crosses its threshold, the job's
     status-change movement drives `quantity_available` negative on the source position and hits
     `chk_whb_stock_positions_available_nonneg` — a raw PostgreSQL check violation inside a `@Scheduled`
     job, with no `BusinessException`, no field-level error, no queue row and no operator. Either the
     job dies and expiry silently stops for the whole install, or the service catches it and the lot
     stays sellable past expiry. `DECISIONS.md`'s own rule is *"a trigger firing in production is an
     incident, not a validation"* — and this is a `CHECK`, which is worse, because a `CHECK` cannot even
     be caught and translated the way `I-6`'s on-hand trigger explicitly can.
  2. **The QA manager**, 09:40, quarantining a contaminated lot that the 06:00 wave reserved. She gets
     an opaque 500. Per `reference_opaque_500_form_save_causes` this is the single most-reported defect
     shape in this monorepo.
  3. **The hold.** `wh_hold_types.blocks_allocation` prevents a *new* allocation. It says nothing about
     the reservation already held, so a `CREDIT_REVIEW` hold placed at 10:00 leaves this morning's
     reservation live and the goods pickable.
  Whichever branch the implementer picks by accident becomes the behaviour, and two of the three
  branches produce a wrong `available`.
- **Negative evidence:**
  ```bash
  cd /Users/bbhushan/work/git/workspace/warehouse-issues
  grep -rniE "status change|hold" docs/WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md | grep -icE "reserv|alloc"
  # 0 rows where a status-change/hold requirement mentions reservations
  grep -rn "RESERVED_STOCK\|STATUS_CHANGE_BLOCKED\|RESERVATION_CONFLICT" docs/ issues/ \
    | grep -v '^docs/reviews' | wc -l                                     # 0
  grep -n "FR-103\b\|FR-152\b" docs/SCENARIO-CATALOGUE.md | wc -l          # 0 scenarios pair them with a reservation
  ```
  The only pairing anywhere is `WH-SC-137` (`docs/SCENARIO-CATALOGUE.md:333`), marked `v2·P5`.
- **Where it belongs:** `warehouse-base` (the port guard) + `warehouse` (the hold/expiry surfaces) ·
  v1 · P0 for the guard, P2 for the screens
- **Disposition:** **needs an `FR-` row first**, then folds into two existing tasks. The `FR-` row must
  choose one of three and say so: *(a)* refuse the status change while an open reservation exists,
  naming the holders — a new code such as `RESERVED_STOCK_STATUS_CHANGE_BLOCKED`, permitted by `PC-29`
  which allows a code to be added but never renamed; *(b)* release the reservations, reason-coded,
  notify each holder per `FR-170`'s existing shape, and write the movement-free audit row; *(c)* offer
  both behind a per-status-transition flag on `whb_stock_statuses`, which is the `D-10` registry answer
  and the one that lets a recall force and a credit hold refuse. Then: add the guard line to **`P0-05`**
  — the task that already owns *"status change as a balanced movement"*, i.e. `FR-103` itself — and the
  release-with-notify path to **`P2-03`** (`V510032`,
  holds) — *"a status change to a non-allocatable status resolves its open reservations by the
  transition's configured rule before the movement posts; `available` never transits through a negative
  value"* — and one line to **`P2-07`**, *"Allocation — soft and hard reservations, **expiry as a
  job**"*, so `FR-160`'s auto-expiry runs through that same resolution path rather than posting raw.
- **Irreversibility:** `reversible` for the rule. The `whb_stock_statuses` flag from option *(c)* is a
  `D-10` catalogue column and can land any time; it does **not** need `PNR-1`.
- **Relationship to round 1:** `new`. It is adjacent to `WH-SC-186` (orphaned reservations whose
  *holder* was cancelled) but is the opposite direction — here the holder is alive and the *stock*
  moved out from under it — and adjacent to `WH-SC-137`, which states the answer for one v2 workflow
  and never generalises it.

---

### `Y-003` · Cancelling after stock has been picked to staging has no de-stage path: the units become an unallocatable, unreported balance — **BLOCKER**

- **What is missing or wrong:** `FR-188` makes pick move stock to *"a real, countable staging
  location"* and `FR-189` makes dispatch *"the inventory-relief event and it is the only one"*.
  `FR-171` handles cancel by releasing reservations and *"cancels un-started tasks"* — un-started only.
  `WS-102` offers **Cancel** as a row action on a pick task that may already carry
  `picked_quantity > 0`, and `WS-105` offers **Cancel** on a shipment. Nothing states what movement
  returns the staged units to a storage location, whether it is mandatory, who raises it, what reason
  code it carries, or what happens if nobody does it. `FR-183`'s rule matrix — the one document that
  would own this — is **v1.1/P3** and even it names only *"cancel the un-started pick task"*.
- **Why it matters:** name the moment. Tuesday 11:20, `SO-2026-01188`, 144 `EA` picked to
  `STAGE-OUT-01` (this is `WH-SC-054`, verbatim). 11:35 the customer cancels. `FR-171` releases the
  reservation and the demand line reads `picked 144, cancelled 144`. The 144 units are physically in
  the staging lane and on-hand is correct — so no drift finding fires, `L-1` holds, and the nightly
  rebuild agrees. But **availability is wrong in whichever direction the location type happens to be
  configured**: `whb_location_types` carries `is_pickable` and `is_staging`, and if a staging lane is
  not pickable the 144 units are on hand, unreserved and permanently unallocatable — invisible dead
  stock that no report in the set lists, because every ageing report in `FR-165` ages a *document*, not
  a bin. If it *is* pickable, tomorrow's allocator routes a picker into an outbound staging lane. This
  is the brief's exact test: a wrong balance, a stuck document and an unanswerable support question, in
  one event, and B2C order cancellation after picking is a daily occurrence, not an edge case.
- **Negative evidence:**
  ```bash
  cd /Users/bbhushan/work/git/workspace/warehouse-issues
  grep -rn "PUTBACK\|PUT_BACK\|DESTAGE\|UNPICK" docs/ issues/ --include=*.md \
    | grep -v '^docs/reviews' | wc -l                                       # 0
  grep -rniE "stranded|orphan.*stag|stag.*orphan|left in staging" docs/ issues/ --include=*.md \
    | grep -v '^docs/reviews' | wc -l                                       # 0
  grep -rniE "de.?stage|restow|return to (the )?(bin|shelf|pick face)|cancel.*(after|mid).?pick" \
    docs/ issues/ --include=*.md | grep -v '^docs/reviews' | wc -l          # 11 — all FR-178's six
                                                                            # quantity columns or
                                                                            # supplier-return picking
  ```
  The movement-type seed does not contain one either: `docs/IRREVERSIBLE.md:663` and `issues/p0-04.md`
  both enumerate the fourteen seeded types and neither carries a pick-cancel or de-stage code.
- **Where it belongs:** `warehouse` · v1 · P2
- **Disposition:** **needs an `FR-` row first**, then **fold into `P2-09`** (`V510041`, discrete
  picking). The `FR-` row states: cancelling a demand line whose `picked_quantity > 0` requires a
  de-stage movement returning the staged quantity to a storage location before the line may close; the
  de-stage is a reason-coded `INTERNAL` movement raised as a task; until it completes the line sits in
  a named state and appears on a report; and `whb_location_types.is_staging = true` locations are
  excluded from allocation, which makes the un-de-staged case *visible* rather than merely wrong. The
  movement type is a `D-10` catalogue row seeded in `V500003` (`P0-04`), so add it to that seed list
  and to `IRREVERSIBLE.md:663`'s enumeration in the same change.
- **Irreversibility:** `reversible`. A movement type is a catalogue row (`FR-003`), so a later seed
  migration is sufficient — but every cancel that happens before it ships leaves stock the ledger
  cannot explain, so the cost of deferring is data, not schema.
- **Relationship to round 1:** `new`. `F-034` and `T-049` produced `FR-171` and `FR-183`, both of which
  stop at *un-started* tasks; no round-1 finding addresses stock already physically moved.

---

### `Y-004` · Work that is in flight has no abandonment clock, no reclaim and no signal — one root cause, four symptoms — **MAJOR**

- **What is missing or wrong:** `whb_tasks` (`DATA-MODEL.md:899`) has `status ∈ CREATED / ASSIGNED /
  STARTED / PAUSED / COMPLETED / CANCELLED / EXCEPTION` and timestamps `assigned_at` / `started_at` /
  `completed_at` / `paused_seconds`. There is **no `stale_after`**, no reclaim or unassign job, no
  orphan-task report, and no health signal. `FR-165` is the law that would catch this — *"a threshold
  column with no scheduled job that reads it is a defect at the moment it is merged"* — and its
  enumeration lists expiry, reservation expiry, obsolescence, core return, warranty hold, job work,
  e-way validity, RTO ageing, COD ageing and licence expiry, and **not tasks**. `FR-398` / `WS-223`
  (`BUILD-SPEC-SCREENS.md:1791`) enumerate seven health signals and stale tasks are not among them.
  The four symptoms are one gap:
  1. **operator logs off / device dies mid-pick** — task stays `STARTED` forever, holding its
     reservation via `wh_pick_tasks.reservation_id`;
  2. **putaway half-completed** — same shape, stock left at `wh_putaway_tasks.staging_location_id`;
  3. **operator loses the permission for the next step of a flow already started** — `@PreAuthorize`
     refuses the completion call and the task has no state that says so;
  4. **shift change** — `FR-222`'s session handover is the *deliberate* case and is **v1.1/P3**, while
     `whb_tasks` and discrete picking both ship **v1** (`P0-10` `V500034`, `P2-09` `V510041`).
- **Why it matters:** `FR-170` already proves the pattern is understood — a reservation held against an
  abandoned estimate *"is invisible dead stock"* and ships with its job, its recipients and its report
  in the same task. A reservation held by a task nobody will ever finish is the identical loss, and it
  is worse because the demand line is stuck between allocated and picked, so the order neither ships
  nor releases. The moment: Friday 17:55, a picker's handheld battery dies mid-task and he goes home.
  Nothing reports it, `WS-102`'s only status filter is a multiselect a supervisor must think to open,
  and on Monday the customer rings about an order that has been `STARTED` for 62 hours.
- **Negative evidence:**
  ```bash
  cd /Users/bbhushan/work/git/workspace/warehouse-issues
  grep -rn "stale_after\|reclaim\|unassign\|task_timeout" docs/ issues/ --include=*.md \
    | grep -v '^docs/reviews' | wc -l                                       # 0
  grep -rniE "logs off|device dies|half.complet" docs/ issues/ --include=*.md \
    | grep -v '^docs/reviews' | wc -l                                       # 0
  grep -n "FR-165" docs/WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md | grep -c task # 0
  sed -n '1791p' docs/BUILD-SPEC-SCREENS.md | grep -ci "task"               # 0
  ```
- **Where it belongs:** `warehouse-base` · v1 · P0
- **Disposition:** **fold into task `P0-10`** (`whb_tasks`, `V500034`). Add: a `stale_after_minutes`
  column on the **task type** registry (not the task — it is per work kind); a scheduled job that moves
  a `STARTED`/`ASSIGNED` task past its threshold to `EXCEPTION` with a seeded exception code, unassigns
  it and notifies the supervisor; and an unresolved/aged task report. Then two one-line amendments:
  add *"in-flight task ageing"* to `FR-165`'s enumeration, and add *"tasks stale beyond their type's
  threshold"* to `FR-398`/`WS-223`'s signal list. `P3-03`'s session handover then becomes the
  *deliberate* case on top of a mechanism that already exists.
- **Irreversibility:** `reversible` — a registry column and a job. But `FR-165` makes shipping the
  column without the job a merge-blocking defect, so the two must land together in `P0-10`.
- **Relationship to round 1:** `new`. `T-041` produced the task table and `FR-212` its duration columns;
  `T-057`/`T-092` produced `FR-216`'s v1.1 console. No round-1 finding asks what happens to a task
  nobody finishes, and `FR-216` is not a substitute because it is a *view* over exception-coded tasks
  and nothing sets the exception code here.

---

### `Y-005` · A wrong or unordered item on the dock has no rule and no reconciliation case type — **MAJOR**

- **What is missing or wrong:** `FR-130` governs over- and short-receipt **by quantity**, and `FR-138`'s
  inbound reconciliation case enumerates seven types — quantity, over-receipt, invoice, ASN, inventory
  variance, receipt reversal, supplier return. None of them is *the supplier sent a different item*.
  `wh_goods_receipt_lines` carries `po_line_id` and `item_id` as separate columns, so the shape is
  representable — a line with a null `po_line_id`, or with an `item_id` that differs from its
  `po_line_id`'s — but no requirement says whether either is permitted, what `match_status` it produces
  (`MATCHED`/`QTY_OVER`/`QTY_UNDER` has no `ITEM_MISMATCH`), or which of `FR-138`'s five resolutions
  applies.
- **Why it matters:** a distributor receives a wrong or unordered line most weeks; an OEM parts feed
  substitutes a superseded part number routinely. The receiver has three bad options and the system
  picks none: refuse the delivery (the goods go back on a truck and the shortage is invisible), receive
  it against the wrong PO line (the ledger now says the ordered item arrived — a wrong balance on two
  items at once, and the supersession chain in `FR-176` will happily allocate it), or key a blind
  receipt and lose the PO link. `FR-123`'s layered-truth model — the set's own answer to *"which
  quantity is right"* — is quantity-only and has nothing to say about identity.
- **Negative evidence:**
  ```bash
  cd /Users/bbhushan/work/git/workspace/warehouse-issues
  grep -rniE "unordered|un-ordered|item not on the po|wrong item deliver" docs/ issues/ --include=*.md \
    | grep -v '^docs/reviews' | wc -l                                       # 0
  grep -rniE "wrong item" docs/ issues/ --include=*.md | grep -v '^docs/reviews'
  # 1 hit: WH-SC-176, which is an identifier *conflict at the port*, not a physical mis-delivery
  grep -n "match_status" docs/DATA-MODEL.md    # MATCHED/QTY_OVER/QTY_UNDER — no identity value
  ```
- **Where it belongs:** `warehouse` · v1 · P2
- **Disposition:** **fold into task `P2-12`** (inbound reconciliation, which owns `FR-138`). Add an
  eighth case type — *item mismatch / unordered item* — and one line to `FR-138`: a GRN line whose
  `item_id` does not match its `po_line_id`, or which carries no `po_line_id` on a non-blind receipt,
  posts to a **`PENDING_RESOLUTION`** stock status and auto-creates the case; the resolutions are
  accept-and-amend-the-PO, accept-as-free-issue, or return-to-vendor through `wh_supplier_returns`, each
  of which is an existing document. Add `ITEM_MISMATCH` to `wh_goods_receipts.match_status`.
- **Irreversibility:** `reversible`. `match_status` is a `VARCHAR` on an application table with no
  `CHECK` per `D-10`, and the case type is a registry row.
- **Relationship to round 1:** `new`. `P-028`/`T-038` produced `FR-138` and its seven types; none of the
  seven is identity.

---

### `Y-006` · LPN split, merge and loss are entirely unspecified, while the LPN is a v1 ledger object with a status ladder — **MAJOR**

- **What is missing or wrong:** `FR-100`/`FR-101` make the LPN a ledger object in v1 with
  `status ∈ OPEN / CLOSED / SHIPPED / CONSUMED` (`DATA-MODEL.md:572`), and `DATA-MODEL.md:577-578`
  states deliberately that *"there is no `whb_lpn_contents` table"* — an LPN's contents are exactly the
  `whb_stock_positions` rows carrying that `lpn_id`. That is a good decision and it makes split and
  merge *representable* as movements that change `lpn_id`. But no requirement, no scenario, no movement
  type and no status transition describes splitting a pallet, combining two, or an LPN that is
  physically lost. Nested LPN is explicitly deferred to v2 (`FR-101`) — deconsolidation is not the same
  thing and is not deferred anywhere; it is simply absent. `FR-105` mentions *"a kit, repack, decant,
  split or merge"* but scopes itself to **lot and serial genealogy**, not to LPN identity.
- **Why it matters:** a pallet arriving as one LPN and going out across three orders is the ordinary
  case in any 3PL or distribution site, and `warehouse-3pl` bills by pallet (`FR-288`: anniversary
  storage billing keys off `whb_lpns.received_at`). Without a split rule the implementer's obvious move
  is to null the `lpn_id` on the picked portion — which silently destroys the LPN grain in the `L-5`
  position key, and `IRR-09` says rows that merged under a narrower key **cannot be un-merged**. A lost
  LPN has the same shape as `FR-149`'s in-transit residue and gets none of its treatment: no ageing,
  no report, no claim.
- **Negative evidence:**
  ```bash
  cd /Users/bbhushan/work/git/workspace/warehouse-issues
  grep -rniE "(split|merge|deconsolidat|consolidat).{0,40}(lpn|pallet)|(lpn|pallet).{0,40}(split|merge|deconsolidat)" \
    docs/ issues/ --include=*.md | grep -v '^docs/reviews'
  # 1 hit: FR-288 "split month" — a billing method, unrelated
  grep -rniE "lost lpn|lpn.*lost|missing pallet" docs/ issues/ --include=*.md \
    | grep -v '^docs/reviews' | wc -l                                       # 0
  ```
- **Where it belongs:** `warehouse-base` (the transitions) + `warehouse` (the screen) · v1 schema ·
  v1.1 handling, matching `FR-101`'s existing split of schema from handling
- **Disposition:** **fold into task `P1-07`** (`V500018` — lots, serials and LPNs) for the rule, and
  **`P3-15`** — which already owns *"LPN move as one movement with stored expanded lines"* — for the
  execution half. The rule is three sentences and one seed: split is a movement whose lines
  move quantity from `lpn_A` to a new `lpn_B` at the same location, conserving under `L-1`, permitted
  only on an `OPEN` LPN; merge is the same in reverse and sets `is_mixed_item`/`_lot`/`_owner` from the
  resulting contents; a lost LPN is a reason-coded write-off against the shrinkage virtual location
  that closes the LPN. Two `INTERNAL` movement types join `V500003`'s seed.
- **Irreversibility:** `reversible` — movement types are catalogue rows and `whb_lpns.status` has no
  `CHECK` under `D-10`. But every split performed by nulling `lpn_id` before the rule ships is
  unrecoverable per `IRR-09`, so this should land before the first LPN-using install, not before a
  migration.
- **Relationship to round 1:** `new`. `F-015` and `S-005` produced `FR-100`'s columns and the SSCC gap
  (`GAP-REGISTER.md` §4 row 2); neither asks what operations an LPN supports.

---

### `Y-007` · There is no deactivation guard on a location, an owner or a warehouse that holds stock, while `FR-051` provides exactly that guard for an item — **MAJOR**

- **What is missing or wrong:** `FR-051` is precise and good: *"Deactivating an item with non-zero
  on-hand across any site, status or owner is blocked; the offered alternative is blocking it for
  receipt or issue"*, with `WH-SC-259` proving it names the site, the status, the owner and the
  quantity. The same guard does not exist for any of the other three members of the `L-5` position key
  that a user can retire: **the location**, **the owner** and **the warehouse**. `whb_locations` has a
  `status` (`FR-091`) that blocks it for operations but says nothing about deactivation or merge;
  `whb_owners` has nothing; and `B19` above — a transfer despatched to a site that is then closed —
  is the same gap seen from the in-transit side, where the receiving location is a per-transfer
  `IN_TRANSIT-*` location and the site behind it can be retired while 36 `EA` are on the road.
- **Why it matters:** `L-4` makes positions a rebuildable cache keyed on nine members. Retire a location
  holding stock and the position rows survive with a dangling parent, the location dropdowns stop
  offering it, and the stock becomes unreachable through every screen in the product while continuing
  to count in the valuation — a wrong number that reconciles perfectly. This happens during exactly one
  activity, and it is an activity every install performs: re-racking a zone, or closing a branch. The
  merge case is worse: `IRR-09` states that rows merged under a narrower key cannot be un-merged, and
  merging two locations is the manual version of that.
- **Negative evidence:**
  ```bash
  cd /Users/bbhushan/work/git/workspace/warehouse-issues
  grep -rniE "location.{0,30}(deactivat|delet|retire|archiv)|(deactivat|delet).{0,30}location" \
    docs/ issues/ --include=*.md | grep -v '^docs/reviews'
  # 1 hit, PORT-AND-ADAPTER-CONTRACT.md:1040, about deleting a *module*, not a location
  grep -rniE "deactivat" docs/WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md   # FR-051 only, and it is items
  grep -rniE "owner.{0,30}deactivat|deactivat.{0,30}owner" docs/ issues/ --include=*.md \
    | grep -v '^docs/reviews' | wc -l                                       # 0
  ```
- **Where it belongs:** `warehouse-base` · v1 · P1
- **Disposition:** **fold into tasks `P1-05`** (`V500012`/`V500013`, locations) **and `P0-06`**
  (owners). One line each, modelled on `FR-051` verbatim so the message shape matches: *"Deactivating a
  location, an owner or a warehouse holding non-zero on-hand across any item, status or lot is blocked,
  naming the item, quantity and lot; the offered alternative is `FR-091`'s block status. Merging two
  locations requires the source to be empty."* Add a companion scenario in the `WH-SC-259` shape.
  Recorded as a service guard, not a trigger, for `FR-051`'s stated reason.
- **Irreversibility:** `reversible` — a service guard, no schema.
- **Relationship to round 1:** materially extends **`T-029`** (*"deactivation must not orphan stock"*,
  `IRREVERSIBLE.md:534`). What is new: `T-029` was discharged as `FR-051` on the **item** axis only, and
  three of the nine `L-5` key members that a user can retire were left without the same guard.

---

### `Y-008` · Movements pending approval have a tile and an action but no filter, no clock, no job and no health signal — **MINOR**

- **What is missing or wrong:** `FR-027` gives `requires_approval` movement types
  `approval_status`/`approved_by`/`approved_at`, and `WH-SC-039` proves the maker-checker rule
  (`PENDING`, no ledger effect, `FR-408` approver ≠ actor). `WS-040` carries an `approvalStatus`
  **column** (`vis = N`, hidden by default), an Approve/Reject row action, and a *"pending approval"*
  statistics tile. Its filter list (`BUILD-SPEC-SCREENS.md:1054-1060`) is twenty filters long and
  **`approvalStatus` is not one of them**. There is no submission clock, no ageing report, no escalation,
  no entry in `FR-165`'s enumeration and no signal in `FR-398`/`WS-223`. The same is true of the
  escalation path generally: `PLATFORM-DEPENDENCIES.md:51` names *"blocked-move escalation"* as a
  notification use case and no `FR-` row establishes it.
- **Why it matters:** the tile says *"7 pending approval"* and the supervisor cannot click through to
  the seven — the one filter that would find them is absent while `isReversed` and `periodId` are
  present. Meanwhile the goods those seven movements describe are physically scrapped or written down:
  a `SCRAP` submitted Friday with the approver on leave leaves twelve ECUs at ₹48,000 each on hand in a
  ledger that is otherwise the statutory record, for as long as nobody thinks to look. This is MINOR
  rather than MAJOR because the outcome is *correct* — `WH-SC-039` is explicit that a `PENDING` movement
  has no ledger effect — it is merely invisible, and one filter plus one job fixes it.
- **Negative evidence:**
  ```bash
  cd /Users/bbhushan/work/git/workspace/warehouse-issues
  sed -n '1054,1060p' docs/BUILD-SPEC-SCREENS.md | grep -ci approvalStatus  # 0
  grep -n "FR-165" docs/WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md | grep -ci approval  # 0
  sed -n '1791p' docs/BUILD-SPEC-SCREENS.md | grep -ci approval             # 0
  grep -rn "escalat" docs/WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md | wc -l      # 0 FR rows
  ```
- **Where it belongs:** `warehouse-base` · v1 · P0
- **Disposition:** **fold into task `P0-02`** for the filter (`approvalStatus` select, alongside
  `postingStatus`, on `WS-040`) and **`P0-13`** for the clock — `P0-13` already owns the
  *dated-obligation register*, so the amendment is to add two rows to that register: *movements pending
  approval beyond N hours* and *unresolved `wh_blocked_movements` beyond N minutes* (`WS-097` already
  computes `ageMinutes`; nothing reads it), each with its recipient. Add both to `FR-398`/`WS-223`'s
  signal list in the same change.
- **Irreversibility:** `reversible`.
- **Relationship to round 1:** `new`. `T-090`/`E-034` produced `FR-408`'s separation of approval from
  execution; no round-1 finding asks what happens when the approver does not act.

---

### `Y-009` · Stock found on the floor that nobody can identify has no entry path — **MINOR**

- **What is missing or wrong:** `FR-153`'s count answers *stock found with no record* and *record with
  no physical stock* completely — but only for stock whose **item is known**. An unlabelled pallet, a
  carton with a rubbed-off barcode, or a returned unit with no paperwork cannot be counted, because
  `wh_count_lines` is keyed on `item_id`. There is no unidentified-stock disposition, no
  `FOUND_UNIDENTIFIED` reason code in the eleven seeded contexts, and no virtual location for it.
- **Why it matters:** small, real and constant. The operator's only options today are to guess the item
  — which puts a wrong number into a statutory ledger under a reason code that says it was found — or
  to leave the pallet in the aisle, which is what actually happens. It is MINOR because the
  ugly-but-correct outcome (leave it off the books until identified) is what a paper warehouse does
  anyway, and because the fix is one reason code and one virtual location.
- **Negative evidence:**
  ```bash
  cd /Users/bbhushan/work/git/workspace/warehouse-issues
  grep -rniE "unlabel|unidentified|no paperwork" docs/ issues/ --include=*.md \
    | grep -v '^docs/reviews' | wc -l                                       # 0
  ```
- **Where it belongs:** `warehouse` · v1 · P2
- **Disposition:** **fold into task `P2-01`** (adjustments, `V510030`/`V510034`), which already owns the
  reason-code catalogue and the blocked-move queue. Add a `FOUND_UNIDENTIFIED` reason code with
  `requires_note = true` and `affects_demand_history = false`, and one line: unidentified stock is held
  at a named quarantine location under a placeholder item until identified, then transferred by an
  ordinary two-line movement. Alternatively **`WONTFIX` with a stated reason** — that is a legitimate
  answer here, and stating it is the point.
- **Irreversibility:** `reversible` — a `V500004` reason-code seed row.
- **Relationship to round 1:** `new`.

---

## §3 · What I checked and found sound

This section exists so round 3 does not re-walk this ground. Each item is something I went looking
for expecting a gap and did not find one.

**The port and idempotency.**
- Idempotency key replayed with a **different payload** — the classic port defect — is answered in four
  places, not one: `FR-017`, `FR-033`, `PC-17` (`payload_hash` is SHA-256 over the canonicalised
  **caller-supplied** envelope, computed server-side **before** enrichment), `WH-SC-165` (`409`, body
  names the original movement id, *"nothing is posted and nothing is overwritten"*), `WH-SC-166`, and
  the retryability table at `PORT-AND-ADAPTER-CONTRACT.md:589` marks it *"no — never retry"*.
  `IRR-04` makes the key never server-generated. This is the best-specified thing in the set.
- Absent key → `422 IDEMPOTENCY_KEY_REQUIRED`; unseen → `201`; seen with identical hash → `200` and the
  original id, not an error. All three rows present at `PORT-AND-ADAPTER-CONTRACT.md:415-417`.
- Late arrival whose `occurred_at` precedes a posted movement — `WH-SC-170` decides it explicitly and
  states the trade: sufficiency is evaluated **at post time, not as-at**, because as-at would require
  replaying the ledger on every post and would let a late arrival retro-invalidate accepted movements.
  The refusal is then routed, not swallowed (`WH-SC-249`).
- Future `occurred_at` — `FR-008`, `OCCURRED_AT_IN_FUTURE`.
- Reversal of a reversal — `FR-005`, `CANNOT_REVERSE_A_REVERSAL`.

**The blocked-move queue — the best decision in the set.**
- `FR-028`, `WH-SC-170`, `WH-SC-249`, `wh_blocked_movements` (`DATA-MODEL.md:1004`), `WS-097` with
  `ageMinutes` and a **Force with approval** action gated on `wh_blocked_movements:force` requiring a
  mandatory reason and an approver, owned by `P2-01` (`V510030`/`V510034`). The framing —
  *"refusing a movement the operator has already physically performed, with nowhere for it to go, is
  how a warehouse learns to work around the system"* — is the correct product instinct and closes a
  large fraction of Group A on its own.

**Concurrency.** `WH-SC-190` (two issues, one unit — *"exactly one succeeds… no third state exists"*,
defended by `@Version` + `CHECK` + stated lock ordering) · `WH-SC-191` (two pickers, resolved at
allocation not at pick) · `WH-SC-192` (count vs allocation, **both** `freeze_locations` branches
stated, with variance computed net of movements during the count window) · `WH-SC-194` (gapless
document numbers from a pessimistically locked counter, explicitly not the platform's racy scan-based
generator) · `WH-SC-196` (optimistic retry in the service, not surfaced) · `WH-SC-198` (advisory lock
for a position key with no row yet) · `FR-175`'s locking discipline stated **and tested** ·
`WH-SC-197`'s assertion is *the absence of oversell*, not the run finishing quickly.

**Cancellation, up to the point stock has moved.** `FR-132` (PO cascade with a stock gate, refused if
any GRN line has received stock **or** an `ARRIVED` ASN exists) · `FR-171` + `WH-SC-096` (availability
returns to **exactly** `96 EA` — *"not 95, not 97, not 'about 96'"*) · `FR-178` + `WH-SC-088` (six
independent quantity columns, because deriving backorder makes short-ship and cancellation
indistinguishable) · `FR-183` + `WH-SC-095` (from-status × edit-type rule matrix with compensating
actions and an append-only amendment log).

**Reservations.** `L-10` open-item ledger, never a counter, with `IRR-45` listing the four ways a
counter fails · holder quad + `DELETE /reservations?holder…` (`FR-167`) · `FR-170` expiry job with
recipients and an ageing report · `WH-SC-186` — a user reports *"it says insufficient stock and there
are 40 on the shelf"* and `POST /movements/simulate` returns `INSUFFICIENT_STOCK` **with the
reservation rows that caused it**, naming each holder quad, and the same rows appear on the
reconciliation-exception grid with an owner and an action. That is a support answer, not a log line.

**Counting.** `FR-153` — a count is a document that **proposes** an adjustment and never writes
on-hand (`WH-SC-116` watches the position table through the whole cycle to prove it) · book quantity
frozen at count start and stored on the line (`IRR-52`) · `FR-155` variance tolerance by quantity
**and value**, and the approver may not be the counter.

**Expiry and shelf life.** `FR-160` expiry is a state, not an alert · `FR-161` names **four**
enforcement points separately — refuse receipt below X% remaining, allocate FEFO, refuse to ship below
Y days remaining, auto-expire on a schedule. (The interaction between the fourth and an open
reservation is `Y-002`; the four points themselves are right.)

**Physical inbound.** `FR-122` GRN carries received/accepted/rejected/damaged as four columns ·
`FR-123`'s layered-truth model with its worked number (*ordered 100 → shipped 95 → received 92 →
billed 100 → on-hand 89, all five correct simultaneously*) · `FR-124` receiving session as one truck
against N POs × N ASNs × N GRNs with a nullable supplier · `FR-129` a receipt may land in a
non-available status **on the first transaction**, closing the window a wave could pick through ·
`FR-130` tolerance + `match_status` + explicit close-short · `FR-131` receipt reversal blocked once
stock has moved on · `FR-134` QA-gated disposition with regulated classes quarantined by default ·
`FR-138` inbound reconciliation case with its **resolution-document pointer** · `FR-106` duplicate
serials, LPN codes and lot codes detected at receipt · `FR-087` `commingle_policy` rejecting a movement
whose *resulting balance* would violate it.

**Degraded operation.** `WH-SC-250` catch-up entry after a four-hour outage carrying true event times ·
`WH-SC-252` outbox at-least-once with backoff, dead-letter grid, `POST /outbox/replay?from_cursor=`,
consumers deduplicating on `(consumer, sequence)`, and the honest note that *"there is no outbox
anywhere in this repository today"* · `WH-SC-253` point-in-time restore verified against a known
position report and valuation, with *"a job that cannot fail is not a control"* · `WH-SC-254` training
in a sandbox because you cannot train pickers on live stock in an append-only ledger · `WH-SC-255` the
four-type `Object → OffsetDateTime` mapping with a warning on unknowns.

**Data integrity edges.** `WH-SC-004` rounding **away from zero** — the service never offers the
database a zero base quantity for a non-zero transaction quantity, because `L-1` would pass while the
bearing left the shelf · `FR-009`/`L-7` conversion factor frozen on the line, replayed on reversal
(`WH-SC-011`) · `FR-014`/`WH-SC-018` negative on-hand as a most-specific-first policy with a log row
and a report on **every** `WARN`/`ALLOW` breach — *"a policy that permits an outcome without recording
it is not a policy"* · `FR-051`/`WH-SC-259` item deactivation blocked across any site, status or owner ·
`WH-SC-142` lot codes normalised on write so a recall does not miss half the stock.

**Authority.** `FR-408` approval permissions distinct from execution and approver ≠ actor, proven in
both `WH-SC-039` and `WH-SC-059` · the supervisor-override shape is consistent across surfaces
(permission **and** reason **and** approver **and** a hash-chained audit row) · `FR-409`/`IRR-61`
support impersonation with consent, time-box and audit, with the honest note that the platform has no
such feature today and `accounting-base`'s `AccAuditActorKind` is the shape to copy. *(The one hole in
this row is `Y-001`.)*

**Recall and returns.** `WH-SC-137` — four things happen and all four are single queries because lot
landed on the ledger line in v1 · `FR-270` `return_type` is a day-one column including refused delivery
and cancelled in transit, and *"a recall must not be restocked under any disposition"*, with
`WH-SC-200` proving `RESTOCK` is **not offered** rather than offered and rejected.

---

## §4 · Refused

Candidate findings I deliberately did **not** file.

1. **The movement-type seed enumerations disagree, and neither contains an `INTERNAL`-direction code.**
   `IRREVERSIBLE.md:663` lists fourteen types; `issues/p0-04.md:39-44` says the fourteen *include*
   `COST_ADJUSTMENT`, `REVALUATION`, `LANDED_COST_APPLY` and `WRITE_DOWN`; and neither list carries a
   code for putaway (`FR-135`), bin-to-bin (`FR-150`) or pick-to-staging (`FR-188`), all of which are
   v1. **Refused as a separate finding**: this is `X-004`'s territory (*"FR-338's four movement types
   may need a seed… enumerate the fourteen in `DATA-MODEL.md` §7.2's `WHB-03` row"*), and the two
   `INTERNAL` codes `Y-003` and `Y-006` require will be added to the same seed. Filing it again would
   be padding. **It does mean `X-004` is bigger than it reads** — worth one sentence there.
2. **`FR-216`'s supervisor exception console is v1.1/P3 while every exception it consolidates ships
   v1** — short picks (`FR-185`), `whb_tasks.exception_code`, inbound reconciliation cases (`FR-138`),
   reconciliation exceptions (`FR-163`), failed `whb_inbound_messages`. **Refused**: `WS-153`
   (`BUILD-SPEC-SCREENS.md:1591`) is explicit that the console *"has no grid of its own"* — it is one
   screen over `WS-097`, `WS-098`, `WS-054` and the task grids, **all four of which ship v1 with their
   own actions**. The v1 supervisor opens four grids instead of one. That is a usability deferral with
   the deferral stated, not a functional gap, and `FR-216`'s own sentence — *"without it every
   exception goes to a phone call"* — is the argument for pulling it forward, not evidence that
   anything is unreachable. If the caller wants it in v1 that is a scheduling decision, not a finding.
3. **`FR-086` capacity constraints are enforced at putaway only from v1.1**, so in v1 a bin that
   physically cannot hold what putaway suggested accepts the stock. **Refused as ugly-but-correct**:
   `WS-082` captures the operator's override reason in v1 and states *"the reason is captured, never
   silently discarded"*, and `FR-086` states the deferral explicitly with a hard-block-vs-warn setting
   waiting for it. The balance is right and the deviation is recorded. MINOR at most, and the deferral
   was decided rather than overlooked.
4. **Support-engineer data access beyond the audit column** — time-box duration, consent-record shape,
   customer notification, whether an impersonated session may post a movement at all. **Refused as
   over-engineering *here***: `FR-409` places the feature in platform and `PP-4`
   (`PLATFORM-DEPENDENCIES.md:979`) already scopes it as *"consent flow, time-box, session mechanism,
   UI"*. Warehouse's obligation is the columns, and that obligation is `Y-001`.
5. **`C10` position-cache drift: *who is paged*.** `FR-398`/`WS-223`'s watcher is v1.1/P3 while
   `whb_position_drift_findings`, `WS-043` and `wh_reconciliation_exceptions.age_days` all ship v1.
   **Refused as a duplicate of `Y-008`'s disposition**, which adds two rows to the same
   dated-obligation register in `P0-13`; pulling the watcher itself forward is the same scheduling
   conversation as item 2. Recorded as `PART` in the coverage table so it is visible without being
   double-counted.
6. **Group C's "movement referencing an item deactivated since"** (`C3`). **Refused**: `FR-051` makes
   the only reachable case an item with zero on-hand everywhere, and `FR-050`'s four independent status
   facts (`is_stocked`, `is_purchasable`, `is_sellable`, `is_active`, `IRREVERSIBLE.md:534`) already
   give the port something to check. A receipt against a deactivated zero-stock item is a
   one-line service guard the implementer will write anyway, and inventing an `FR-` row for it would be
   the over-engineering `DECISIONS.md` §7 warns against.

---

## §5 · Counts

```bash
cd /Users/bbhushan/work/git/workspace/warehouse-issues/docs/reviews
grep -cE '^### `Y-[0-9]{3}`' R11-exception-and-unhappy-paths.md                    # 9
grep -E '^### `Y-' R11-exception-and-unhappy-paths.md \
  | grep -oE '\*\*(BLOCKER|MAJOR|MINOR)\*\*$' | sort | uniq -c
#   3 **BLOCKER**
#   4 **MAJOR**
#   2 **MINOR**
grep -rohE "\bY-[0-9]{1,3}\b" ../../docs ../../issues 2>/dev/null | sort -u | wc -l  # 9, all in this file
```

| Severity | Count | Findings |
|---|---|---|
| **BLOCKER** | 3 | `Y-001` `Y-002` `Y-003` |
| **MAJOR** | 4 | `Y-004` `Y-005` `Y-006` `Y-007` |
| **MINOR** | 2 | `Y-008` `Y-009` |
| **Total** | **9** | |

**Exception inventory:** 61 walked · **36 SPEC (59.0%)** · 13 PART · 12 NONE.
**Scenario mix:** 300 scenarios · 165 happy · 70 edge · 52 error · 13 conc · **45.0% non-happy**.

**Prefix allocation check, run before writing:**

```bash
grep -rohE "\bY-[0-9]{1,3}\b" docs/ issues/ | sort -u | wc -l     # 0 before this file existed
```

**New ids proposed:** none. All nine findings fold into existing tasks — `P0-02` (×2), `P0-05`,
`P0-06`, `P0-10`, `P0-13`, `P1-05`, `P1-07`, `P2-01`, `P2-03`, `P2-07`, `P2-09`, `P2-12`, `P3-15`.
Two need an `FR-` row authored first (`Y-002`, `Y-003`). No new migration number is proposed and none
is invented: `Y-001` rides the **existing** `V500030` (`P0-02`, `PNR-1`); every other schema touch is a
catalogue or seed row in a migration its owning task already holds.
