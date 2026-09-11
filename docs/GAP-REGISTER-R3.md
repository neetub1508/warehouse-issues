# GAP-REGISTER-R3 — the disposition of every round-3 finding

<!-- check-design-set: scenario-citations file WH-SC-306 — the SCENARIO-CATALOGUE.md §5 rule 3 next-free allocation marker, the same allocation GAP-REGISTER-R2.md, DESIGN-SET-DEFECTS.md and GAP-REGISTER.md already declare. Cited once in §4.4 as the precedent for how round 2's Q-006 moved the marker when it minted WH-SC-301-WH-SC-305; an allocation marker, not a citation of a scenario -->

> **What this document is for.** `GAP-REGISTER.md` dispositions the **575** findings of review round 1.
> `GAP-REGISTER-R2.md` dispositions the **62** findings of round 2. This one dispositions the **52**
> findings of round 3, under the same rule that produced both — `D-12`: *every capability found by any
> lens is placed in a version and carried in a task file **now***. A finding with no disposition row is
> a finding the implementation team rediscovers at the worst possible moment.
>
> **Rounds 1 and 2 are not superseded.** Nothing here withdraws a round-1 or round-2 finding or its
> disposition — with **exactly one exception**, and it is the most valuable single output of this
> round: `RB-001` proves that round 1's `C-044` is **wrong** about mobile date filters, and the false
> clause has already propagated into a requirement (`FR-220`), six documents and eight task files.
> That correction is tracked as a finding, not as a quiet edit.
>
> **This file is the register only.** It changes no task file, no `DECISIONS.md` row and no
> `IMPLEMENTATION-PLAN.md` line. It tells the next wave what to change and where.

**Date** 2026-09-03 · **Branch** `docs/round-3-functional-completeness`

> **State of the decision surface, 2026-09-03.** A concurrent `DECISIONS.md` pass landed while this
> register was being written: it resolved nine open decisions, escalated six, and **allocated `OD-16`
> (`RF-004`, foreign-currency costing) and `OD-17` (`RD-001`, the SSCC pallet label) for round 3** —
> the two this register references and deliberately did not number. `OD-1` and `OD-9`, which gate
> `RF-005` and `RA-002` here, are **escalated**, i.e. still awaiting a person. `OD-6` is **RESOLVED**
> without answering `RF-006`; §2.6 records that. `docs/OPEN-DECISIONS-RESOLVED.md` carries the evidence
> for all of it. **This register changed neither file.**

---

## §1 · Why there was a round 3, and what it was allowed to do

Round 1 asked *"does the design cover its market?"* — seven lenses, 575 findings, a 236-row benchmark.
Round 2 asked *"can it be built, operated and lived with?"* — eight lenses, 62 findings, and a task set
that turned out to be right and thin.

Neither of those is the question round 3 asks. Round 3 walks **six surfaces that are orthogonal to both
a document and a journey**: a *person*, a *field*, a *number a reader is shown*, a *wire*, an *install*,
and *money*. Those surfaces do not decompose along the axes rounds 1 and 2 swept, which is why they
produce different findings from the same documents. A screen can be journey-complete (round 2's R10
marked it ✔) and still name eight columns its table does not have. A workflow can be exception-complete
(R11) and still have no person authorised to run it.

### 1.1 The six axes

| Lens | Prefix | The axis, and why rounds 1–2 could not have swept it | n |
|---|---|---|---|
| **R16** | `RA-` | **Role and persona completeness** — sixteen roles walked through a *shift*, not a document: every screen opened in order, every permission held, every signal that starts work, every handoff out. Rounds 1–2 walked orders and exceptions; neither walked a person | 8 |
| **R17** | `RB-` | **Screen and field buildability** — can a developer sit down and build the *form*, not the grid? Every filter key resolved against `filter_definitions`, `COMMON_FILTER_CONFIGS` and the backend param; every column resolved against `DATA-MODEL.md`. Two of its findings required reading the **live tree**, which is why round 2 could not have filed them | 9 |
| **R18** | `RC-` | **Reporting and analytics completeness** — the number a reader is shown, and whether it is reproducible. Twenty reports against `L-13`'s three clocks, `L-14`'s suppression rule, and the substrate that renders a total | 9 |
| **R19** | `RD-` | **Integration, device and channel surface** — everything that crosses a wire: the outbound webhook, the batch envelope, the label the printer emits, the queue on a handheld in a dead aisle, the carrier connector | 8 |
| **R20** | `RE-` | **Configuration and day-one setup** — the value, the row, the screen and the person, on the Monday of go-live. Not *what must a setting be* (the set answers that superbly) but *what is it set to, who sets it, and on what screen* | 8 |
| **R21** | `RF-` | **Money, costing and billing** — the arithmetic itself, in the five places the set states an outcome and never states the algorithm; and the 3PL biller one level up | 10 |
| | | **Total** | **52** |

**The governing rule, given to every lens before it read anything:** *"Rounds 1 and 2 already ran fifteen
lenses and dispositioned 637 findings. Your job is to find what those fifteen did NOT. Grep before you
file."* Every lens carries a `§4 Refused` section naming the earlier id that already owns each declined
candidate.

### 1.2 The counts, computed

```bash
cd /Users/bbhushan/work/git/workspace/warehouse-issues
for p in RA:R16 RB:R17 RC:R18 RD:R19 RE:R20 RF:R21; do
  pre=${p%%:*}; grep -c "^### \`$pre-" docs/reviews/${p##*:}-*.md; done | paste -sd+ - | bc
# -> 52

grep -hoE '^### `R[A-F]-[0-9]{3}`.*\*\*(BLOCKER|MAJOR|MINOR)\*\*$' \
     docs/reviews/R1[6-9]-*.md docs/reviews/R2[01]-*.md \
  | grep -oE '(BLOCKER|MAJOR|MINOR)' | sort | uniq -c
#  16 BLOCKER
#  28 MAJOR
#   8 MINOR
```

| | BLOCKER | MAJOR | MINOR | Total |
|---|---|---|---|---|
| **R16** `RA-` role and persona | 2 | 5 | 1 | 8 |
| **R17** `RB-` screen and field | 2 | 7 | 0 | 9 |
| **R18** `RC-` reporting | 2 | 6 | 1 | 9 |
| **R19** `RD-` integration and device | 3 | 3 | 2 | 8 |
| **R20** `RE-` configuration and day one | 2 | 4 | 2 | 8 |
| **R21** `RF-` money and costing | 5 | 3 | 2 | 10 |
| **Total** | **16** | **28** | **8** | **52** |

The verified totals match the brief exactly: **16 BLOCKER · 28 MAJOR · 8 MINOR**.

### 1.3 What was refused, which is again the more important number

```bash
tot=0
for f in docs/reviews/R1[6-9]-*.md docs/reviews/R2[01]-*.md; do
  n=$(awk '/^## §4 · Refused/{p=1;next} /^## §5/{p=0} p' "$f" | grep -cE '^\| [^-|]|^[0-9]+\. ')
  h=$(awk '/^## §4 · Refused/{p=1;next} /^## §5/{p=0} p' "$f" | grep -cE '^\|---|^\|:?-')
  echo "$(basename $f): $((n-h))"; tot=$((tot+n-h)); done; echo "TOTAL: $tot"
# R16 14 · R17 14 · R18 16 · R19 26 · R20 21 · R21 16
# TOTAL: 107
```

**107 candidates were refused against 52 filed** — a 2.06:1 ratio, higher than round 2's 83:62. Every
refusal names the round-1 or round-2 id that already owns it (`U-001`, `U-002`, `U-004`, `U-005`,
`Y-004`, `K-002`, `K-003`, `K-005`, `Z-001`, `Z-006`, `O-001`, `O-002`, `O-003`, `H-002`, `Q-004`,
`Q-005`, `X-024`, `X-027`, `X-029`, `X-036`, `X-050`, `C-014`, `C-033`, `C-042`, `OD-6`, `OD-7`,
`OD-9`, `OD-11`, `OD-12`, `OD-13`, `OD-14`, `OD-15`, `PNR-3`, `PP-6`, `FR-039`, `FR-450`), or the
argued refusal that already covers it. That ratio is the evidence that round 3 is not padding a register.

### 1.4 The task map, computed — and a correction to the investigation pass

An investigation pass supplied a task-hit table with `P0-15` at 22, `P0-13` at 17, `P2-20` at 17 and so
on. **Those are raw mention counts over the whole lens file**, including each lens's `§1.1` inventory,
its `§3 What I checked and found sound`, its `§4 Refused` and its `§5 Counts` — none of which is a
finding. Recomputed over **the findings sections only** (`§2`, i.e. the text between the first
`### \`Rx-nnn\`` heading and `## §3`), and counting **distinct findings** rather than mentions:

```bash
python3 - <<'PY'
import re,glob,collections
files=sorted(glob.glob('docs/reviews/R1[6-9]-*.md')+glob.glob('docs/reviews/R2[01]-*.md'))
hits=collections.defaultdict(set); sev={}
for f in files:
    txt=open(f).read().split('\n## §3')[0]          # findings section only
    parts=re.split(r'(?m)^### `(R[A-F]-\d{3})`(.*)$',txt)
    for i in range(1,len(parts),3):
        fid,head,body=parts[i],parts[i+1],parts[i+2]
        sev[fid]=re.search(r'(BLOCKER|MAJOR|MINOR)',head).group(1)
        for t in set(x.upper() for x in re.findall(r'\b[Pp][0-6]-\d{2}\b',head+body)): hits[t].add(fid)
print(len(sev), dict(collections.Counter(sev.values())))
for t,s in sorted(hits.items(),key=lambda kv:(-len(kv[1]),kv[0]))[:18]:
    print(f"{t:8} {len(s):2}  {' '.join(sorted(s))}")
PY
# 52 {'BLOCKER': 16, 'MAJOR': 28, 'MINOR': 8}
```

| Task | Findings | Which |
|---|---:|---|
| `P2-16` | **8** | `RC-003` `RF-001` `RF-002` `RF-004` `RF-005` `RF-006` `RF-009` `RF-010` |
| `P2-20` | **7** | `RB-008` `RC-001` `RC-003` `RC-004` `RC-005` `RC-006` `RC-008` |
| `P2-21` | **7** | `RB-005` `RC-001` `RC-004` `RC-005` `RC-006` `RC-007` `RC-008` |
| `P0-15` | **6** | `RA-001` `RA-003` `RA-006` `RA-007` `RE-003` `RE-008` |
| `P0-02` | **4** | `RA-004` `RE-001` `RE-002` `RF-001` |
| `P0-13` | **4** | `RA-005` `RC-008` `RE-001` `RE-007` |
| `P1-05` | **4** | `RA-001` `RA-004` `RB-002` `RE-002` |
| `P2-18` | **4** | `RC-001` `RC-002` `RC-006` `RF-005` |
| `P2-29` | **4** | `RB-003` `RB-005` `RC-004` `RC-005` |
| `P0-07` · `P0-08` · `P1-03` · `P1-20` · `P2-01` · `P2-02` · `P2-15` · `P2-19` · `P5-22` | 3 each | see §2 |

The ordering is stable against the investigation pass at the top — `P2-16`, `P2-20`, `P2-21`, `P0-15`,
`P0-13`, `P1-05`, `P2-18`, `P2-29`, `P0-02` and `P0-07` are the heavy files either way — and two of its
claims do not survive verification and are corrected here:

- **`P1-18` is a 3-finding file, not 12** (`RA-001`, `RA-008`, `RF-010` — and two of those three only
  mention it). That does **not** reduce `RA-001`: `P1-18`'s header reads `Migrations **none** ·
  Screens **none**` (`issues/p1-18.md:5`) and the finding requires it to gain both. The count is small
  because the defect is one thing, not because it is cheap.
- **`P2-25` is a 3-finding file, not 13** — but `RA-002` alone makes it a header amendment (two new
  adapter tables and a screen).

Two further placements the lenses did not name, established here:

- **`RB-004`'s owning task is `P1-01`.** `whb_items` is created in `V500015`, and
  `grep -rln V500015 issues/*.md` resolves to `issues/p1-01.md` (and `p0-02.md`, which only FKs to it).
  The review names only `DATA-MODEL.md:527`.
- **`RD-005`'s `owning_module` column lands in `P2-10`.** `grep -rln V510044 issues/*.md` resolves to
  `issues/p2-10.md`. The review names the migration and not the task.

### 1.5 The headline

- **A fresh install cannot post its first movement.** `whb_stock_movements.period_id` is `NOT NULL`,
  and nothing in the set creates a stock period — no seed, no screen action, no job (`RE-001`).
- **A v1 install prints a GS1-128 pallet label carrying an SSCC v1 cannot allocate, and cannot read its
  own label back.** The label is glued to a pallet (`RD-001`).
- **The moving average must recompute forward and the ledger's own `I-2` trigger forbids the write that
  does it.** The trigger ships in `V500030` — `PNR-1` and `PNR-2` collapsed into one file (`RF-001`).
- **`C-044` is wrong.** Mobile date-range filters are supported —
  `mobile/src/components/common/ListHeader.tsx:123-170` declares two ranges,
  `mobile/src/components/common/EntityListScreen.tsx:428-441` forwards them, and
  `grep -rl "showDateRangeFilter" mobile/src/screens/ | wc -l` → **56** live screens use them. Six
  invented `<x>Within` filter keys were designed around the false clause and four of them carry no
  option list, no `filter_definitions` row and no backend parameter (`RB-001`).
- **The "two platform files" budget is wrong by a factor of two to three.** See §4.5: four are certain
  and two more are conditional.
- **Zero new task files.** All 52 land in files that already exist — 39 as body lines, 10 as
  amendments that change a named task's header, 3 as decisions. See §2.7 and §4.

---

## §2 · The disposition of all 52

### 2.0 The buckets

- **`CITED`** — a task file already carries the capability *and* cites the finding's subject. Nothing to do.
- **`COVERED-uncited`** — the capability is inside an existing task's declared scope, and the task does
  not say it. The named task gains a line, a column value, a seed list, an acceptance box or a
  scenario. **The task header does not change.** This is the cheap majority.
- **`NEEDS-TASK`** — a new task file, **or an amendment to a named existing task whose header changes**
  (a migration it did not claim, a table it did not own, a screen it did not list, a deliverable it did
  not produce). Round 3 produces **ten of the second kind and zero of the first**.
- **`DECIDED`** — not an authoring gap. A human chooses, and the `D-`/`OD-` row that carries the choice
  is named.
- **`WONTFIX`** — declined with a reason. Round 3 produces none; `RC-009` is the only candidate and it
  is placed rather than refused, because `D-12` forbids silence.

**Deadline** is the migration or task at which the finding stops being free. `docs/IRREVERSIBLE.md` §3.2
is the authority: **`PNR-1`** is the migration creating `whb_stock_movements`/`_lines` — `V500030`,
task `P0-02` — and **`PNR-2`**, the `L-2` append-only trigger, ships in the same file
(`DATA-MODEL.md:2903`, `:2486`). **`PNR-3`** is the first movement posted in any install.

### 2.1 R16 · `RA-` — role and persona completeness

| Finding | Sev | The defect, in one line | Disposition | Owning file — and exactly what it must gain | Deadline | Person? |
|---|---|---|---|---|---|---|
| `RA-001` | **BLOCKER** | The warehouse axis of `FR-405`'s scope predicate has no table, no screen and no migration, so no administrator can restrict a storekeeper to a site — while the owner axis has both halves (`whb_owner_grants` + `WS-020`) | **NEEDS-TASK** (amendment) | **`P1-18`** — header moves from `Migrations **none** · Screens **none**` (`issues/p1-18.md:5`) to one `warehouse-base` P1 migration and one screen. It gains `whb_warehouse_grants` mirroring `whb_owner_grants` exactly (`warehouse_id`, `grantee_type` `USER`/`ROLE`/`GROUP`, `grantee_id`, `access_level` `VIEW`/`OPERATE`/`ADMIN`, `effective_from`, `effective_to`, `uk(warehouse_id, grantee_type, grantee_id, effective_from)`), read by the **same single server-side resolver**, plus **`WS-238` Warehouse Grants** on the Customer reference beside `WS-020`, plus **the shipped default stated in one sentence** — *a user with no grant row is unscoped, not blind* — or the first install locks every operator out of every site. **`P1-05`** gains the real table name and screen link for the *"warehouse-scoped user grants"* class its site-closure pre-check already counts (`issues/p1-05.md:37`, `:186`) | **Before `P1-18` writes the resolver.** A resolver shipped against branch scope and later widened to a third axis is every management query in two modules re-touched. Schema itself is after `PNR-1` and reversible | **yes** — the no-grant default is a product call (§5.6) |
| `RA-002` | **BLOCKER** | The counter clerk cannot price a line: `price_level` is a keystroke and a column with no vocabulary, no price table exists anywhere in `DATA-MODEL.md`, and the only price loader (`whad_price_files`) is v1.1 | **NEEDS-TASK** (amendment) | **`P2-25`** — header gains `V520015` creating `whad_price_levels` (`code`, `name`, `is_default`, `is_active` — a `D-10` catalogue, no `CHECK`) and `whad_item_prices` (`item_id`, `price_level_code`, `unit_price`, `currency_code`, `effective_from`, `effective_to`, `uk(item_id, price_level_code, effective_from)`), **both adapter-owned so base learns nothing about selling** (`D-11`), plus a Department-shape screen with `ImportButton` — thirty thousand prices are never keyed. `FR-359`'s row names the table; one v1 scenario in the `WH-SC-216` shape asserts a line resolves its price | **Before `P2-25`** — which is also `OD-9`'s corrected deadline (`GAP-REGISTER-R2.md` §3 gate 10) | **yes** — contingent on `OD-9` (§5.5) |
| `RA-003` | MAJOR | The four seeded role bundles are a **four-verb deny-list over a sixty-verb space**, so Storekeeper silently holds the QC release gate, the blocked-movement force, the hold release and the reservation release; and four of eight human actors — including `mgr1`, actor of 17 scenarios — have no bundle | **COVERED-uncited** | **`P0-15`** — amend the existing `Z-010` block (`issues/p0-15.md:15-24`), do not add a second: **(1) bundles become allow-lists**, each naming its verb strings, with acceptance *"every §10.2 verb appears in at least one bundle or in an explicit `granted to no seeded bundle` list, asserted by a query that fails when §10.2 grows"*; **(2) two more bundles** — Warehouse Manager and Finance Controller, verb lists as R16 specifies; **(3) a QA bundle and a QA actor row**, since `wh_quality_inspections:disposition` and `wh_return_receipts:disposition` belong to it and nothing else, and the FRD §4 actor table gains the row | `V501002` · before any customer clones a bundle — narrowing an over-granted bundle later is a **revocation** across every clone | no |
| `RA-004` | MAJOR | Closing a stock period strands every in-flight approval: the pre-check is one condition, and `FR-020` then refuses the approved posting *"including a reversal"*, so a submitted scrap becomes an unpostable, undeletable row `L-2` forbids cleaning up | **COVERED-uncited** | **`P0-07`** — the close pre-check returns **every** blocking class at once in the `P1-05` shape (pending handovers, movements at `approval_status = PENDING` dated in the period, `wh_stock_adjustments` and `wh_counts` awaiting approval, unresolved `wh_blocked_movements`), each with a count and a link; `WS-045` gains `pendingApprovalCount` and `unresolvedBlockedCount`; **soft close warns and lists, hard close refuses**. **`P0-02`** — a movement approved after its period closed is refused with a named code whose message states the only correct act (*withdraw and resubmit current-dated*, the `WH-SC-021` pattern), which requires a terminal **`WITHDRAWN`** value on `approval_status`. One scenario in the `WH-SC-021` shape | **`V500030`** for the `WITHDRAWN` value — free in the `CREATE TABLE`, a `CHECK` drop-and-rebuild on the hottest table afterwards | no |
| `RA-005` | MAJOR | The auditor's tamper evidence has **no verifier**: three v1·P0 scenarios assert the chain verifies, no screen action and no job recomputes it, and `PC-31` states the feature is v2 | **COVERED-uncited** | **`P0-13`** — a **tenth** dated obligation, `chain-verify`: nightly per warehouse, walks `whb_stock_movements` in `sequence_no` order, recomputes each `prev_payload_hash` against its predecessor's `payload_hash`, writes a `whb_job_runs` row on success **and** failure, raises a `wh_reconciliation_exceptions` row naming the first divergent `sequence_no`. **`WS-040`** gains a `Verify chain` toolbar action over the filtered range. Acceptance asserts a deliberately corrupted row is named — *a verification that cannot fail is not a control*. Amend `PC-31`'s `prev_payload_hash` row so it stops saying v2 while three v1 scenarios spend it. **Merge the remediation with `RC-008`** — same missing verifier, two lenses | Before the v1 exit criterion is claimed; columns already ship at `V500030` | no |
| `RA-006` | MAJOR | The picker is offered *emergency replenish* on a v1 screen whose entire mechanism (`wh_replenishment_tasks`, `WS-142`, trigger `SHORT_PICK`) is v1.1, so an emptied pick face stays empty | **COVERED-uncited** | **`P2-09`** — v1 emergency replenish **creates a `wh_transfer_orders` row of type `BIN_TO_BIN`** from the resolved reserve location to the short pick face, pre-filled with the shortfall and carrying the pick task's exception code as reference: one existing v1 object, one existing v1 screen (`WS-090`), no new table; `FR-255`'s task engine and `WS-142` stay v1.1 and supersede it. **Or** strike *emergency replenish* from `FR-185`'s v1 offer and amend `issues/p2-09.md:38` — but **write down which**. Also give the per-site auto-count switch a home: `admin_settings` key `warehouse.short_pick.auto_count`, seeded in `P0-15`'s `V501100` | Before `P2-09` builds `WS-102`'s short-pick action set | **yes** — build-or-withdraw is a product call (§5.8) |
| `RA-007` | MAJOR | The permission the integration principal and the device authenticate with is defined **twice, in two namespaces** — `PC-31` and `BUILD-SPEC-SCREENS.md` §10.2 — and `P0-15` seeds one; six of `PC-31`'s ten v1 strings appear nowhere in §10.2 | **COVERED-uncited** | **`P0-15`** seeds §10.2 (the migration is written from it and it follows §10.1's table-name rule). **`PORT-AND-ADAPTER-CONTRACT.md` `PC-31` is rewritten** to cite §10.2's strings — the loser must be edited, not left standing — and §10.2 gains the two gates the port needs and no screen has: **`whb_stock_movements:post_backdated`** (posting into a `SOFT_CLOSED` period, `mgr1`'s `WH-SC-022` authority, distinct from `whb_stock_periods:override`) and **`whb_outbox:view`**. `WH-SC-022` and `WH-SC-241` are amended to the seeded strings — a scenario asserting `403` on a name that does not exist tests nothing | **`V501000`.** Permission *names* are `IRR-63`: forward-only, and a rename after go-live is retro-granting across every role a customer built | **yes** — one namespace must lose, and round 2's `Q-003` (does AUDITOR get `:export`?) is answered in the same migration (§5.7) |
| `RA-008` | MINOR | The warehouse manager's authority boundary is undefined data: `FR-145` mandates an approval threshold **by value as well as by quantity**, and no column, `admin_settings` key or screen field holds one — while `wh_count_programs` does this correctly | **NEEDS-TASK** (amendment) | **`P2-01`** — its `V510030` gains `wh_adjustment_approval_policies` (nullable `warehouse_id`, `owner_id`, `item_category_id`, `reason_code_id`, computed `specificity`, `threshold_quantity`, `threshold_value`), resolved most-specific-first, **mirroring `whb_gl_posting_rules` exactly** as `Z-001` requires of every ladder, with the all-null row seeded from `admin_settings warehouse.adjustment.default_threshold_value`. `WS-089` shows the resolved threshold, which row supplied it, and offers the **Test resolution** modal `WS-051` already defines. Amend `DATA-MODEL.md:999`'s description so it stops asserting a threshold its columns do not carry | `V510030` — well after `PNR-1`, nothing sealed | no |

### 2.2 R17 · `RB-` — screen and field buildability

| Finding | Sev | The defect, in one line | Disposition | Owning file — and exactly what it must gain | Deadline | Person? |
|---|---|---|---|---|---|---|
| `RB-001` | **BLOCKER** | Round 1's `C-044` says mobile date filters are unsupported. **They are supported** — and on that false premise six `<x>Within` dropdown keys were invented, four with no option list, no `filter_definitions` row and no backend parameter, and the false clause was written into `FR-220`, a requirement | **COVERED-uncited** | **`docs/reviews/R1-codebase-reality.md`** — amend `C-044` to *"text **and date-range** filters are supported; `ListHeader.tsx:123-170` exposes two ranges and `EntityListScreen.tsx:428-441` forwards them"*, then propagate to **`FR-220`**, `BUILD-SPEC-SCREENS.md` §0.7, `IRREVERSIBLE.md:723`, `DATA-MODEL.md:4172`, `INDIA-LOCALISATION-PACK.md:446`, `PLATFORM-DEPENDENCIES.md:369`. Then **delete the four option-less `<x>Within` keys** and restore the web `…From`/`…To` pair on the mobile block in **`P0-16`**, **`P1-12`**, **`P1-13`**, **`P2-08`**, **`P2-10`**. **Keep `expiringWithinDays` and `inTransitOverDays`** — they are bucket filters, better than a range on both surfaces, and the only two with a stated option list or a stated reason | **Before `P1-12`, `P1-13`, `P2-08` and `P2-10` are signed off** — each carries an invented key in an *acceptance criterion*, so each will be signed off as met | no — this is a transcription, not a choice |
| `RB-002` | **BLOCKER** | `WS-017`'s filter strip and export name **eight fields `whb_locations` does not have**, two of them on no table in the product (`is_pickable` belongs to `whb_stock_statuses`, `DATA-MODEL.md:414`) | **COVERED-uncited** | **`BUILD-SPEC-SCREENS.md`** `WS-017` (`:862-879`) — one editing pass against `DATA-MODEL.md:451`: fix the six renames and `commingePolicy` in both places. **`P1-05`** records the decision on the three fields with no column: `check_digit` (a real GS1 location-label need — *probably add the column in `V500013`*), `isPickable` and `isReceivable` (*probably delete the filters* — pickability at a location is `status`, receivability is an item fact) | **`V500013`** if `check_digit` is added — before `PNR-1`, on the hottest master in the base module | **yes** — three add-or-delete calls (§5.12) |
| `RB-003` | MAJOR | Two v1 report grids carry **two different `COMMON_FILTER_CONFIGS` scope names**, and the losing one is a filter strip that renders and does nothing (§0.5's own rule) | **COVERED-uncited** | **`BUILD-SPEC-SCREENS.md` §7 wins** — the `WAREHOUSE_RPT_*` form is what `DATA-MODEL.md:3542-3561` registers for all twenty report grids and is the only self-consistent family. Correct **`issues/p2-05.md:49,95`** and **`issues/p2-02.md:46`**, and reconcile `WS-221`'s filter set between §7 and `p2-05.md:47-51` in the same edit | Before the `filter_definitions` inserts are written (`P2-29` band) | no |
| `RB-004` | MAJOR | `whb_items.lifecycle_status` has **four** values in the column authority and **five** everywhere else — `BLOCKED` is missing from `DATA-MODEL.md:527` | **COVERED-uncited** | **`DATA-MODEL.md:527`** gains `BLOCKED`. Owning task is **`P1-01`**, which claims `V500015` (`grep -rln V500015 issues/*.md`). Five sources against one is not a decision; it is a transcription. Check the row's siblings while there — `lot_control_mode`, `serial_control_mode`, `expiry_policy` all agree with `WS-023`, so this is the only one | **`V500015`** — after it, a `CHECK` drop-and-rebuild against a live item master, and `DECISIONS.md`'s own rule stands: a constraint firing in production is an incident | no |
| `RB-005` | MAJOR | The export-parity ratchet six task files cite scans **`ai.platform` only**, so it discovers zero warehouse export services — and the 43 warehouse exports §0.5 ships *without* audit columns cannot be registered in a `Set.of(...)` its own contract says may shrink, never grow | **COVERED-uncited** | **`MODULE-INTEGRATION.md` §12** gains two lines — (a) the scan at `ExportServiceContractTest.java:137` must take a **package list** and warehouse's packages must be added to it, making this a **fourth** shared platform file (§4.5), which `D-10`'s §11 corollary already concedes; (b) the frozen-baseline contract needs a stated exception shape for a module whose ledger grids are audit-columnless **by design** — most cheaply a `boolean isLedgerStyle()` hook on `BaseExportService` the test reads instead of a name list, so `WITHOUT_AUDIT_COLUMNS` (`ExportServiceContractTest.java:80`) keeps shrinking and warehouse never enters it. Add `whb_transformations` to §0.5's list in the same edit. **`P2-29`** carries it as a Trap | Before the first warehouse `BaseExportService` subclass is written (`P1-20`/`P2-29` band) | no |
| `RB-006` | MAJOR | **No grid in the set states an empty state, a loading state or a statistics tile set** — 214 empty-state strings and their i18n keys will be invented one at a time, and `Q-005` already records that P2's non-grid i18n has no owner and no key-diff gate | **COVERED-uncited** | **`BUILD-SPEC-SCREENS.md` §0** gains a new **§0.13** in §0.7's shape: every block states an `emptyMessage` i18n key, and the six workflow-gating grids state the *three* distinguishable messages (`empty` / `out of scope` / `never populated`); `never` — the platform default — is a legitimate answer for a master grid and need not be written, exactly as §0.12 handles `Frozen when`. Statistics tiles: state them per screen or state `none`, because §0.3 already asserts a cache rule for *"every warehouse statistics strip"*. Acceptance in **`P2-29`** | Cheap per screen, expensive in aggregate — before grid-config wave 1 (`P1-20`) | no |
| `RB-007` | MAJOR | **No screen names a uniqueness-validation endpoint**; `/validate/code` appears **zero** times in the design set, over ~65 masters with unique keys | **COVERED-uncited** | **`BUILD-SPEC-SCREENS.md` §0.6 (Modals)** gains one row: *"every master modal with a unique key carries the `GET /validate/{code|name}` pair of the Department reference (`platform/backend/…/DepartmentController.java:301,318`), called debounced at ≥300 ms on blur, binding its error to the field."* Then per screen state only the **partial**-unique cases the generic pair does not cover — `WS-019`'s `is_house`, `WS-015`'s `is_default`, `WS-023`'s `uk(owner_id, sku)`. Acceptance in **`P1-01`** and **`P1-05`** | Before the master modals are written and reviewed as complete (`P1-01`/`P1-02`/`P1-05`) | no |
| `RB-008` | MAJOR | Four enumerated-`select` filters have **no option list and no source**, and `WS-212`'s `bucketSetCode` contradicts its own frozen columns | **COVERED-uncited** | **`BUILD-SPEC-SCREENS.md`** — state the options inline for `ageOverDays` and `inTransitOverDays` the way `:1170` and `:1300` already do (one list, reused: an ageing bucket set is a product decision, not a per-screen one, and it is the same decision `FR-388` and `FR-162` are already making); point `rejectionCode` at `FR-039`'s vocabulary and say whether UI-originated refusals extend it; **delete `bucketSetCode` from `WS-212`, or** make the six bucket columns a stated consequence of one seeded default bucket set — not both. Blocks: §7 (`WS-212`, `WS-220`), §3.2 (`WS-098`, `WS-090`, `WS-097`), §3.3 (`WS-122`), §2.8 (`WS-052`). Acceptance in **`P2-20`**, **`P2-02`**, **`P2-09`** | Before the `filter_definitions` inserts; `ageOverDays` spans three screens in two phases, so the divergence is structural | no |
| `RB-009` | MAJOR | **Nineteen screen-level refusals, five named error codes, and no register binding any of them to a field** — nineteen invented code strings across five modules and three surfaces, each a breaking rename once shipped | **COVERED-uncited** | **Extend `FR-039`'s register rather than starting a second one** — one table in `BUILD-SPEC-SCREENS.md` §0, in `PORT-AND-ADAPTER-CONTRACT.md:563`'s exact columns (`code` · HTTP · retryable · **scope: field / header / line**), one row per screen refusal, seeded with the five that exist. Each per-screen block then cites a code instead of describing a refusal, and `check-design-set.py` can assert every `refused`/`blocked` sentence carries one. **Do this in the same edit as `RD-008`** — the same requirement, folded once | `PC-29` makes the vocabulary additive-only; before any producer ships against `FR-039` | no |

### 2.3 R18 · `RC-` — reporting and analytics completeness

| Finding | Sev | The defect, in one line | Disposition | Owning file — and exactly what it must gain | Deadline | Person? |
|---|---|---|---|---|---|---|
| `RC-001` | **BLOCKER** | Seven as-at reports, and **not one says which of `L-13`'s three clocks it reads** — while the v1 exit criterion requires two of them, on different clocks by their own parameter types (`WS-211`'s `asAtDate` is `dateOnly`, `WS-224`'s `asAtDateTime` is an instant), to reconcile *"to the unit and to the paisa"* | **COVERED-uncited** | **`BUILD-SPEC-SCREENS.md` §7 gains a mandatory `Clock` column**, non-blank for all 20 rows, three legal values: `occurred_at`, `posting_date`, or *"parameter — the user chooses, and the choice is rendered on the report"*. Recommended assignment: `WS-209` `WS-224` `WS-212` `WS-218` `WS-220` → `occurred_at`; `WS-210` `WS-211` `WS-213` `WS-219` `WS-226` → `posting_date`; `WS-208` `WS-215` `WS-221` `WS-223` → *current, not as-at*, stated on the screen. **`WH-SC-060`** names the clock all three reports run on, and a **second `edge` scenario** asserts a movement whose `occurred_at` and `posting_date` fall in different periods appears in `WS-224` for one date and `WS-211` for the other **without either being a defect**. Every report footer states its clock beside its reconciliation. Folds into **`P2-20`** (six reports), **`P2-18`** (`WS-219`), **`P2-21`** (the rest). No migration | **Before `P2-20`.** Not schema-irreversible — but every as-at figure, bank stock statement, section-44AB quantitative statement and 3PL invoice already issued was computed on a clock the customer was never told, so correcting the query later **restates numbers a third party holds** | **yes** — the finance controller signs which clock the bank statement is on (§5.6) |
| `RC-002` | **BLOCKER** | The stock-to-GL reconciliation — *"the report that makes a finance director trust the system"* — ships with **no GL control-account balance column, no owner grain and no item-group grain**, and its `difference` compares warehouse to its own handover outbox rather than to the ledger it is named after; the number it needs lives in `acc_*`, which `WH-SC-162` fails the build for referencing | **COVERED-uncited** | **`P2-18`**, three edits: (1) `WS-219` gains `ownerName` and `itemCategoryName` columns and `ownerId`/`itemCategoryId` filters, and `difference` drills through to `WS-209` filtered to period × site × owner × group, per `FR-247`'s last clause; (2) a **`glControlAccountBalance` column** with **one** source — a `GlBalanceProvider` **port interface declared in `warehouse-base` with no implementation there**, implemented in the accounting-facing adapter and absent on Mode A, the same shape `FR-357`'s display resolver already uses, so no `acc_*` reaches warehouse's classpath; (3) Mode A renders an explicit *"no accounting module installed"* provider reason, not a blank cell (`FR-398`). One line in `PORT-AND-ADAPTER-CONTRACT.md` §4 recording this as the **only** read direction across the seam; one in `MODULE-INTEGRATION.md`; `FR-247` amended to name the provider, not the table. No migration | Before `P2-18` | no |
| `RC-003` | MAJOR | The as-at valuation has **no reproducible formula**: it reads `quantity_remaining`, a column mutated in place, and the rows that could un-mutate it (`whb_cost_layer_consumptions`) are never named as its input | **COVERED-uncited** | **`P2-20`** — `WS-211`'s **Reads** cell becomes *"`whb_cost_layers` **net of `whb_cost_layer_consumptions` as at the parameter date** — never `quantity_remaining`"*, and the formula joins `P2-20`'s scope beside the existing *"the as-at answer is always computed from movements"* sentence. Amend `FR-387`, `WS-211`, `WS-222` | Before `P2-20`; `FR-387`'s *"reproducing the same answer for the same date next year"* is unachievable until it lands | no |
| `RC-004` | MAJOR | Every report is declared *"a real grid"*, the v1 exit criterion requires a report footer, and **`DynamicDataTable` has no footer** — `grep -c "summaryRow\|footer" platform/frontend/src/components/common/DynamicDataTable.tsx` → **0** | **COVERED-uncited** | Two parts, the first free: (1) **`BUILD-SPEC-SCREENS.md` §7 gains a `Statistics strip` column** stating the tiles for all 20 rows — the filter-aware strip `FR-395` already mandates uncached for these screens *is* a report total: `WS-210` closing quantity and closing value, `WS-219` the five terms and the difference, `WS-211` total value and the method used. Today §7 states tiles for none of the 20. (2) Where a per-column total genuinely belongs under the columns — `WS-210` alone in v1, because a bank statement is read column-wise — add a **`PP-`-style row to `PLATFORM-DEPENDENCIES.md`** budgeting an optional `summaryRow` prop on `DynamicDataTable` as **platform** work, proposed separately, exactly as `PP-6` handled the export cap. **Do not hand-roll a second table component.** Strips in **`P2-29`**, footer wording in **`P2-20`** | Before `P2-29` seeds the strips; the platform prop must be proposed before P2 or `WS-210` ships without it | no |
| `RC-005` | MAJOR | A **required** report parameter has no enforcement point anywhere in the platform; the failure mode is the set's own phrase — *"a report of today, mislabelled"* | **COVERED-uncited** | **`P2-29`** — the enforcement point is stated once as a **backend** rule for all parameterised reports: the report controller reads its grid's required filters (the `FilterDefinitionRepository` query that already exists and has no caller) and returns a **field-level `400`** naming the missing parameter, generalising what `WS-218` already specifies. `BUILD-SPEC-SCREENS.md` §7's preamble gains *"a required parameter is refused server-side with a field-level error; a report that silently defaults to today is a defect"*. Frontend: the parameter renders above the filter strip and the grid does not fetch until set — a page rule, not a `BaseFilter` change. Acceptance in **`P2-20`** and **`P2-21`**. No schema — `filter_definitions.is_required` already exists | Before `P2-20`/`P2-21` acceptance | no |
| `RC-006` | MAJOR | `L-14` — *non-own stock is never valued* — is written onto **one enquiry screen** and onto **none of the fourteen valued report rows**, including `WS-210`, the one that goes to a bank | **COVERED-uncited** | **`BUILD-SPEC-SCREENS.md` §7 preamble**, applying to all 20 rows: *"`L-14` — every value column is suppressed where `owner_type != OWN`, as on `WS-042`; every report carrying a value column also carries `ownerTypeCode` as a column and an `ownerType` filter defaulting to `OWN`, and states on the report which owners are included."* **`WS-210` gets an explicit `ownerTypeCode` default of `OWN`** with the inclusion stated in the footer. One `SCENARIO-CATALOGUE.md` scenario: consignment stock at `SITE-A`, run `WS-210`, assert closing quantity excludes it by default and that including it is a visible, labelled choice. Folds into **`P2-20`** and **`P2-21`**. No new `FR-` — `FR-112` already carries the rule; only the report rows must obey it. Kept **disjoint from `K-002`/`FR-450`**, which is the *actor* axis, not the owner axis | Before `WS-210` leaves the building — a bank statement including someone else's consignment stock is a misstatement | no |
| `RC-007` | MAJOR | The KPI report ships a `metricCode`, a `target` and a `variance` with **no table behind any of the three**, over a twenty-nine-metric list this design set never enumerates | **NEEDS-TASK** (amendment) | **`P2-21`** — header gains two tables on a migration **next free in `V510…`, taken from `DATA-MODEL.md` §8.4's ledger, not guessed**: `whb_metric_definitions` as a `D-10` catalogue (`code`, `name`, `unit`, `definition_text_key`, `owning_module`, `is_system`, `higher_is_better`) seeded by the registry migration, and `wh_metric_targets` (`metric_code`, `warehouse_id`, `owner_id`, `period_grain`, `target_value`, effective dates) for `WS-216`'s target and variance, plus a small admin screen. **Enumerate the twenty-nine in `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` §6.22** under `FR-394` with metric · frozen definition · **fact source**, starting from R6:306's list; any metric with a blank fact source is placed in a later version **with the fact that enables it** or **refused in writing** in §9. **Bind `definition_text_key` to the live explainer** at `platform/frontend/src/components/common/metricInfo/` (`MetricInfoModal.tsx`, `MetricInfoTable.tsx`, `metricText.ts:15`'s `createMetricText(prefix)`), which is what `FR-393`'s *rendered, not documented* means. One new `FR-` for the target object. The two tables may land via **`P1-03`** or the registry band | Before `P2-21`. The **unrecoverable** part is the subset: a metric whose fact was never captured cannot be back-filled — the reason `FR-213` pulled the task timestamps into v1 | no — but the *refusal* half needs a sales-facing sign-off |
| `RC-008` | MAJOR | The auditor's fifth artefact — immutability evidence — is promised in v1 (`FR-427`) and has **no screen, no report, no export and no action**; the only chain verifier in the set runs over `whb_audit_events`, the wrong table | **COVERED-uncited** | **`P0-13`** — point the same verifier at `whb_stock_movements` (**this is `RA-005`; do the two as one edit**), with permission `whb_stock_movements:verify`, scoped by warehouse × date range, returning verified/broken and naming the two `sequence_no` values either side of a break. **`P2-20`** — an **exportable evidence artefact**: verification result, range, row count, head and tail hashes, run timestamp; add `payloadHash` and `prevPayloadHash` to `WS-040`'s **export** columns (already on `WS-041`'s panel, so no new fact is exposed). **`P3-17`/`WS-223`** — a `LEDGER_CHAIN_BROKEN` signal, run nightly beside `L-4`'s rebuild, the same job's natural pair. **Reconcile the version**: `COMPETITOR-BENCHMARK.md:467` says v1.1, `FR-427` says v1 — `FR-427` wins, amend the benchmark row | Before the first audit; data is captured, so recoverable — but discovered in the worst room | no |
| `RC-009` | MINOR | Space and location utilisation is **unreportable in every version**, although the capacity columns are v1, the location hierarchy's stated justification is utilisation, and 3PL storage bills by the pallet | **NEEDS-TASK** (amendment) | **`P6-02`** — which already owns `FR-070`'s ABC/velocity recompute and is the natural home for velocity × cube. **Place it, do not build it in v1**: one requirement in §6.22 — *"a location utilisation report: occupied against capacity by weight, volume, units and LPNs, rolled up the hierarchy to rack, aisle, zone and site, from `whb_locations`' capacity block and `whb_stock_positions`; the analysis, never an optimiser"* — at **v3 · P6**, beside the slotting *analysis* §9's refusal row 7 already calls *"v3 and not refused"*. One new `FR-` and one screen row, **`WS-238`** — see the collision in §4.4. **If the answer is instead *never*, it belongs in §9's refusals table with a reason.** Silence is the only outcome `D-12` forbids | v3 · P6; facts are captured from v1, so this is a placement question | **yes** — build-at-v3 or refuse-in-writing (§5.11) |

### 2.4 R19 · `RD-` — integration, device and channel surface

| Finding | Sev | The defect, in one line | Disposition | Owning file — and exactly what it must gain | Deadline | Person? |
|---|---|---|---|---|---|---|
| `RD-001` | **BLOCKER** | v1 prints a GS1-128 pallet label whose `p2-14` acceptance is *"encodes AI `00`"* — AI `00` **is** the SSCC — while SSCC allocation (`FR-452`) and the element-string parser (`FR-063`) are both v1.1, so v1 prints a label v1 cannot fill and cannot read back. **The label is glued to a pallet** | **DECIDED** | **`OD-17`** — being allocated by the concurrent `DECISIONS.md` pass; **do not allocate it here**. The decision is a **version move, not code**: **(a)** move the SSCC allocator into the v1 wave — `whb_gs1_settings` + `whb_gs1_serial_counters` + a mod-10 function, the same locked-counter idiom `FR-426` already builds in v1, so the marginal cost against `P2-14` is small — **or (b)** remove the GS1-128 LPN label from the v1 eleven, ship a Code-128 licence plate carrying the internal `lpn_code`, and say so in `FR-225` and `WH-SC-203`. **R19 recommends (a):** GS1-128 without an SSCC is not GS1-128. Whichever wins, `p2-14`'s acceptance and `WH-SC-203`'s *"and the SSCC"* move with it, and `RD-006`'s FNC1 encoding rule lands in the same task. Owning tasks after the decision: **`P2-14`** ↔ **`P3-24`** (`V500056` moves into the v1 wave, or nothing moves) | **Before `P2-14` prints anything.** **Physically irreversible** — printed labels cannot be recalled, and `FR-064`'s own reason for making `sscc` a v1 column is *"issuing them later means re-labelling"* | **yes** (§5.3) |
| `RD-002` | **BLOCKER** | `whb_outbox_subscriptions` ships an `endpoint_url` and a `secret_ref` **in v1** and no document says what is sent, how the receiver verifies us, or which HTTP status means delivered — and a v1 HTTP subscription with no successful delivery **pins outbox retention forever** under `PC-46` | **COVERED-uncited** | **`PORT-AND-ADAPTER-CONTRACT.md` §4.5** gains three `PC-` rows: the signed-request contract (`SHA-256` HMAC over `subscriber_code . sequence_no . timestamp . body`, header name, tolerance window reusing `p5-22`'s `max_clock_skew_seconds`); the status→ladder mapping (`2xx` = `OK`; `408`/`429`/`5xx` = `RETRY`; every other `4xx` = `DEAD` at once, because retrying a `400` eight times only delays the dead-letter); one-in-flight-per-subscription with a stated timeout. **`P0-11`**'s outbox migration gains two nullable columns on the **v1** table — `signing_algorithm`, `delivery_timeout_seconds` — on the same argument `PC-40` already makes about the table itself. **`P3-22`** carries the contract. **Separately and immediately: `WS-057` must refuse `transport = HTTP` in v1, or `PC-46`'s retention rule must exempt a subscription that has never had a delivery attempt** | The columns are cheap while `P0-11`'s migration is unwritten. The **retention** consequence is not reversible once the outbox has grown | no |
| `RD-003` | **BLOCKER** | The v1 offline statement is written against a mobile substrate nobody examined: `onlineManager` is never wired to NetInfo (`grep -rn "onlineManager" mobile/src` → 0), so `networkMode: 'online'` (`mobile/src/config/reactQuery.ts:70,111`) pauses nothing and a write in a dead aisle **fails once and is discarded**; meanwhile a persisted queue **does** exist at `mobile/src/services/backgroundLocationService.ts` with a **drop-oldest** policy (`:525`), and no document in the set states a queue-overflow rule | **COVERED-uncited** | **`FR-221`** and **`P3-04`** gain three sentences: (a) **the queue is durable and never evicts** — it is bounded by refusing new scans with a visible *"queue full, N pending, reconnect to continue"* state, because refusing to accept work is honest and discarding accepted work is not; (b) **the substrate is chosen explicitly**, and if it is TanStack Query then wiring `onlineManager.setEventListener` with NetInfo is a named, testable line item, not an assumption; (c) `backgroundLocationService.ts` is cited as **the structural precedent and the policy counter-example**, so the next implementer copies the persistence and not the `slice()`. **`P0-16` §4** carries the v1 statement; **`PLATFORM-DEPENDENCIES.md` §3.3**'s *"nothing queues behind `NetworkContext`"* is corrected | Reversible in design; **each dropped scan is not**. Before `P0-16` §4 is signed | no |
| `RD-004` | MAJOR | `POST /movements/batch` has a response specified to the byte, **a request specified nowhere**, no size bound, and a unique key on the batch envelope with no replay rule | **COVERED-uncited** | **`PORT-AND-ADAPTER-CONTRACT.md` §3.4** gains a `PC-` row for the batch **request** envelope (`source_system`, `batch_reference`, `device_id`, `actor_type`, `movements[]`) and a second extending `PC-15`'s ladder to the batch key — *"a repeated `batch_reference` returns `200` with the **stored** per-movement result array from `whb_movement_batch_results`, which `PC-34`'s persist-first rule already makes possible"*, closing the replay hole with no new endpoint. **`P0-08`** gains a declared maximum (`max_batch_size` as an `admin_settings` row in `WHB-75`, tunable per install, defaulting to the number the acceptance test uses) with a **`BATCH_TOO_LARGE` 422**, and **`RETRY_AFTER`/`429` reserved in `FR-039` now** even though `P5-22` builds the limiter in v2 | **`PC-29` makes the error vocabulary a compatibility surface** — add both codes before a producer ships. Do it in **`RD-008`'s single `FR-039` edit** | no |
| `RD-005` | MAJOR | Channel connectors have an adapter contract and **carrier connectors have none**, while `wh_carriers.api_enabled` and `wh_carrier_accounts.credentials_ref` ship in v1 and two task headers name a module class `D-1` does not contain | **COVERED-uncited** | **`FR-196`** is amended in the shape `FR-207` already uses: *"`warehouse` owns the carrier, service and account masters and **never names a carrier vendor**; each carrier connector is an adapter registered through the `PC-04` `List<T>` bean registry, and a connector not on the classpath leaves `api_enabled` inert with a stated fallback."* **`wh_carriers` gains `owning_module`** — one nullable column, **in `V510044`, which `grep -rln V510044 issues/*.md` resolves to `issues/p2-10.md`** (the lens named the migration and not the task). Fix the two task headers to name a real module and correct `issues/p5-11.md`'s label. **If the decision is instead that carriers deliberately live in the app, that needs an `OD-` row** — it is the mirror image of a decision the set took explicitly the other way | The column is cheap now; **package placement follows table placement** and is not cheap later | **yes**, if the answer is "in the app" (§5.9) |
| `RD-006` | MAJOR | The print template's `body` has **no representation, no variable-binding contract, no repeat construct and no escaping rule** — and the *"zero precedent"* claim misallocates the budget across three ingredients already on the classpath | **COVERED-uncited** | **`P2-14`** gains three specification blocks and **`FR-224`** one sentence: name the body language per format class once (recommended: **target-native source** — ZPL for the label kinds, an HTML/CSS document for the PDF kinds through the existing OpenPDF path — with one `{{…}}` binding syntax shared by both); declare a **per-`template_kind` data contract** including the repeat construct for line collections, which is the difference between a renderer and a string replace; state the **escaping rule per format**, naming the ZPL control characters and the GS1-128 FNC1 sequences. Replace the *"zero precedent"* sentence with the three live dependencies (OpenPDF, ZXing, the `{{…}}` template renderer in `EmailTemplateService`) and the one genuinely net-new writer, so the risk lands where it is | Reversible, but on the critical path — and `RD-001`'s FNC1 rule must land in the same task | no |
| `RD-007` | MINOR | An unauthenticated inbound endpoint **cannot be added by a module** — the platform allow-list is a hard-coded constant (`platform/backend/…/config/SecurityConfig.java:159`) — and the set's *"complete touchpoint matrix"* has no row for it, while the platform rate limiter it will duplicate is never named | **COVERED-uncited** | **`MODULE-INTEGRATION.md` §2** gains a **23rd row** — `platform/…/constants/SecurityConstants.java` + `SecurityConfig.java`, kind **R**, *required only for a module exposing an unauthenticated inbound endpoint*, evidenced at `SecurityConfig.java:159`. **`PLATFORM-DEPENDENCIES.md` §2** gains one sentence recording that the allow-list is a platform constant and that `RateLimitingConfig` already exists, so **`P5-22`** extends it rather than building a second | Before `P5-22`; a conditional sixth shared platform file (§4.5) | no |
| `RD-008` | MINOR | The port's error vocabulary is **43 codes** and `FR-039` — the requirement that freezes it — still lists **21**; the fold the contract requires *"before v1 ships"* never happened, and the set already cites the number it does not contain | **COVERED-uncited** | Copy `PORT-AND-ADAPTER-CONTRACT.md` §3.9.2's twelve rows into **`FR-039`** verbatim, state the total as 43, and add one line to **`P0-08`**'s acceptance: *"`FR-039` and §3.9 enumerate the same set, and a test asserts the enum's cardinality."* **Land `RD-004`'s two capacity codes and `RB-009`'s nineteen screen refusals in the same edit** — `PC-29` makes every later addition a second compatibility event | Fold before v1 ships, as the contract already says | no |

### 2.5 R20 · `RE-` — configuration and day-one setup

| Finding | Sev | The defect, in one line | Disposition | Owning file — and exactly what it must gain | Deadline | Person? |
|---|---|---|---|---|---|---|
| `RE-001` | **BLOCKER** | **Nothing in the set creates a stock period** — no seed, no screen action, no job — while `period_id` is `NOT NULL` on every movement, `WS-045`'s actions are *Soft close · Close · Reopen*, the one described creation path is guarded *"the previous period exists"*, and `P2-19`'s cut-over checklist opens the first period **after** the opening stock has been posted into it | **COVERED-uncited** | **`P0-07`** — *"`V500019` **seeds the current and next stock period** for the default company with `warehouse_id = NULL` (all sites), derived from the install date, so an install can post before anyone opens a screen. `WS-045` gains a **Generate periods** action (`whb_stock_periods:create`) taking a company, an optional warehouse, a start date and a count, and a **period-generation job** joins `P0-13`'s register with cadence `MONTHLY` and missed-run policy `CATCH_UP` — a period boundary that arrives while the job is down must not stop receiving. §0.11's guard becomes 'the previous period exists **or none exists for this (company, warehouse)**'."* **`P2-19`** — *"the checklist item is **'operating period opened'**, distinct from the period the opening balances post into. The opening batch posts into a period whose `end_date` is the as-at date, which the batch opens and closes as part of `apply`; certification gates the **operating** period, not the opening one. `WS-151` states which period each item refers to."* | **`V500019` — before `PNR-1`.** It must land in `V500019` itself, because every later P0 migration and every P0 acceptance test posts a movement | no |
| `RE-002` | **BLOCKER** | The virtual-location seed — the migration that must exist **before the ledger's first row** — is specified **five different ways**, and its stated mechanism cannot give a second site any virtual locations at all | **COVERED-uncited** | **`P1-05`** — *"**the virtual-location code convention is `VIRT-<PURPOSE>-<SITE CODE>`**, because `whb_locations.code` is globally unique; the display name is the unprefixed purpose. The v1 purposes are the ten of `FR-084` — `SUPPLIER`, `CUSTOMER`, `ADJUSTMENT`, `SCRAP`, `PRODUCTION`, `IN_TRANSIT`, `COUNT_VARIANCE`, `OPENING_BALANCE`, `CONSUMED`, `JOB_WORKER` — spelled that way in every document. `V500013` seeds them for the sites that exist; **creating a `whb_warehouses` row creates its virtual-location set in the same transaction**, in the warehouse service, and `WS-016`'s create modal states it. `V500012` seeds the non-physical `TRANSIT-WH` warehouse (`is_physical = false`) that `FR-085`'s per-reference transit locations hang from."* **`FR-084`** and **`DATA-MODEL.md:478-481`** are amended to the same ten codes; `issues/p1-05.md:66`'s ellipsis and its `OPENING` are removed | **`V500012`/`V500013` — before `PNR-1`.** **Reversible while `V500013` is unwritten; irreversible after**: the location `code` is a stable key ledger rows resolve against (`IRR-26`), so renaming it after the first movement means rewriting `whb_stock_movement_lines`, which `L-2` forbids | no |
| `RE-003` | MAJOR | **Seven install parameters, no defaults, no scopes, no screen**, one platform permission gating all of them — and the *"two platform files"* the plan budgets for is **three** | **COVERED-uncited** | **`P0-15`** — *"`V501100` seeds **every** base key with `setting_value`, `default_value`, `setting_type`, `description` and a `validation_rules` bound, and the list is closed — no ellipsis. The seven v1 keys and their defaults: `negative_stock.default_mode` = `BLOCK` (STRING); `period.soft_close_requires_approval` = `true` (BOOLEAN) **and it may not be set false — the key records who approves, never whether approval is required (`L-8`)**; `outbox.max_attempts` = `10` (INTEGER, the **fallback** for a subscription whose own `max_attempts` is null; the subscription wins); `reservation.default_ttl_minutes`; `port.rejected_queue_threshold`; `position.max_contention_retries`; `outbox.max_cursor_lag`. **Every key states its scope in `description`, and `admin_settings` can express only install scope** — a key needing company × site scope is a table, not a key."* **`P1-20`** — *"the honest limit is **three** platform files, not two: `platform/frontend/src/utils/filterUtils.ts`, `platform/backend/…/config/CacheConfiguration.java` **and `platform/frontend/src/app/dashboard/admin-settings/page.tsx`**, which needs a thirteenth tab and an `AdminSettingsWarehouseTab.tsx` gated on a warehouse permission — following the Doc OCR AI precedent at `:145-152`, invisible in a deployment without the module. The warehouse tab is gated `whb_settings:edit`, seeded in `V501000`, checked **in addition to** the platform's `admin_settings:edit`."* | `V501100` (P0) and `V511200` (P1). Reversible — a seed value is editable and the tab is frontend-only | no |
| `RE-004` | MAJOR | Over- and short-receipt tolerance is a v1·P1 **two-level ladder with no column at either level**, and the one column that exists is at a third grain nobody named | **COVERED-uncited** | **`P1-03`** — *"`whb_items` gains `over_receipt_tolerance_pct` and `short_receipt_tolerance_pct` (`DECIMAL(9,6)`, nullable = inherit), and `whb_warehouses` gains the same pair as the site default. Resolution is most-specific-first — PO line → PO header → item → warehouse → `BLOCK` — and it is the **sixth** ladder, so it is stated in `DATA-MODEL.md` §2.1 alongside the other five (`Z-001`)."* **`P1-13`** — *"the receipt service resolves through the ladder and the `422` message quotes **which level supplied the number**, because `WH-SC-066` and `WH-SC-067` differ only in that. `COMPETITOR-BENCHMARK.md:238`'s v1.1 placement is corrected to v1; the **per-supplier** grain stays v1.1 on `whb_item_supplier_sources`."* | The `whb_items` half is **`V500015` — before `PNR-1`**; the `whb_warehouses` half is `V500012`. Both nullable, neither `L-2`-sealed | no |
| `RE-005` | MAJOR | **Thirteen of the fourteen registries are told to ship "+ seed" and given no values to seed**; the only enumerated lists live in `IRREVERSIBLE.md` §5, which **no task cites**, and they contradict their own requirements in five places | **COVERED-uncited** | Each of **`P0-04`**, **`P0-05`**, **`P0-06`**, **`P1-02`**, **`P1-08`** gains: *"the seed value list for this registry is `IRREVERSIBLE.md` §5's **v1 seed** column, cited by row number, and reproduced in this task's Scope. A code that appears in a requirement, a scenario fixture or another task and not in the seed is a merge blocker — the rule `FR-165` applies to threshold columns."* Plus the five specific corrections: **`P0-05`** — `V500005` seeds the eight stock statuses of §5 row 4 **plus `PENDING_RESOLUTION`** (`is_on_hand = true`, `is_allocatable = false`, `is_shippable = false`, `requires_reason_to_leave = true`), which `P2-12` and `FR-028` both consume; `V500006`'s location-type seed gains `OPENING_BALANCE`, `COUNT_VARIANCE`, `CONSUMED`; `V500008`'s item-type seed replaces `KIT` with `KIT_STOCKED` and `KIT_PHANTOM` and adds `ASSET`, per `FR-049`. **`P0-06`** — add `TRANSIT` to the owner-type seed, per `FR-108`. **`P1-02`** — the UoM seed is `EA` `BOX` `CASE` `PALLET` `BAG` `CARTON` `KG` `L` `M` `CFT`, **each row carrying its `unece_rec20_code` and `gst_uqc_code` literal in the migration**. **`DATA-MODEL.md` §7.2** gains a *"seed authority"* column pointing each registry row at its `IRREVERSIBLE.md` §5 row, which also closes `X-004`'s referral | **`V500002`–`V500011` — before `PNR-1`.** Reversible as inserts, but the *absence* is not: seven of the thirteen are `PNR-1` and their `code` values are what ledger rows carry, so a code seeded wrong and used cannot be renamed under `L-2` | no |
| `RE-006` | MAJOR | **Twelve deferrals across eight files to an "install guide" that does not exist**, has no owning task and no acceptance criterion — and it is where four undiscoverable install steps are being sent | **NEEDS-TASK** (amendment) | **`P0-16`** — header gains a **deliverable**: *"**`P0-16` produces `docs/INSTALL.md`**, and its acceptance is that `grep -rn -i 'install guide' docs/ issues/` resolves to a section heading in it for every deferral. Minimum contents: module enable flags and their order; `FLYWAY_OUT_OF_ORDER=true` for a warehouse-first install; the platform restore gap stated as 'unknown' with the customer's decision recorded; the day the snapshot job is switched on and which reports begin then; the ordered day-1 master load (`Z-009`) with its screens; the period-generation step (`RE-001`); the settings whose defaults must be reviewed before go-live (`RE-003`); and the port's authentication limit until v3."* This is a `docs/` file, **not** a design document, so it does not enter `check-design-set.py`'s citation graph | Before go-live planning. Every month it is unwritten, another task defers another fact to it — four mentions became twelve in one authoring wave | no |
| `RE-007` | MINOR | `FR-165` is enforced **in one direction only**: three v1 alert horizons have a job, a recipient and a report, and **no column, key or field to hold the number** | **COVERED-uncited** | **`P0-13`** — *"`FR-165`'s register is **bidirectional**: a threshold column with no job is a defect, **and a job whose horizon is not a column, an `admin_settings` key or a screen field is the same defect**. The register's table gains a **Threshold home** column and no row may leave it blank. The two rows this task adds take `admin_settings` keys `warehouse.approval.pending_alert_hours` and `warehouse.blocked_movement.alert_minutes`, seeded in `V501100` with defaults."* **`P1-03`** — *"`whb_items.near_expiry_days` and `whb_item_site_settings.near_expiry_days` (nullable = inherit), resolved item × site → item → the `admin_settings` install default, so `FR-160`'s notification horizon is data. `WS-023` and `WS-027` carry the field; `WH-SC-130`'s 45 becomes a fixture value rather than a constant."* | Nullable columns after `V500015`/`V500050` — reversible | **yes**, lightly — item property vs install default is *"a decision that is not yet an `OD-`"* in R20's own words (§5.10) |
| `RE-008` | MINOR | **Disabling a module leaves its menus, permissions and settings live**, and `MODULE-INTEGRATION.md` §15 says nothing reads them | **COVERED-uncited** | **`P0-15`** — *"the menu rows this migration seeds for modules that are not `warehouse-base`/`warehouse` are seeded `is_active = false` and enabled by the module's own migration when it runs — the pattern the Doc OCR AI tab uses at the frontend (`admin-settings/page.tsx:145-152`), applied at the data layer."* **`MODULE-INTEGRATION.md` §15**'s disable row is corrected: **the `whb_*` tables are inert; `menus`, `permissions` and `admin_settings` are not**, and disabling a module after enabling it leaves a visible menu that must be deactivated on the platform menu screen | `V501000`/`V501100`. Reversible | no |

### 2.6 R21 · `RF-` — money, costing and billing

| Finding | Sev | The defect, in one line | Disposition | Owning file — and exactly what it must gain | Deadline | Person? |
|---|---|---|---|---|---|---|
| `RF-001` | **BLOCKER** | Four documents require a backdated receipt to **restate the weighted average forward**, and `I-2`'s line trigger ships an **empty** mutable-column allowlist while `DATA-MODEL.md:2480` says `moving_average_after` is frozen — so the v1 acceptance box cannot be passed by any implementation | **NEEDS-TASK** (amendment), **decision first** | **Decide before `P0-02` writes `V500030`.** Recommended answer, which costs nothing later and keeps every invariant: **`moving_average_after` is never restated** — it is a snapshot of the average when that line posted, exactly what `IRR-39` says it is for; a backdated receipt inserts a layer, and the *current* average is `Σ open layer_value / Σ open quantity_remaining`, computed on read from the layer table and never stored. **`P2-16`** and **`P0-02`** carry it; `IRR-39`, `WH-SC-151`, `issues/p2-16.md:140,168` and `DATA-MODEL.md` §6.4 are rewritten to say so; the **falsifier** is added — *post a backdated receipt, re-read a following movement line, assert `moving_average_after` is byte-identical*. State the FIFO rule in the same edit: a backdated layer is consumed by **future** issues only; already-written consumptions are never re-drawn, because `L-2`/`L-3` make correction a reversal and the layer link is what `P4-04`'s ITC reversal walks. **If instead the set wants restatement, `I-2`'s allowlist grows a sixth column in `V500030`** — a header change to `P0-02`, and the argument `DATA-MODEL.md:2481` demands | **`V500030` = `PNR-1` **and** `PNR-2`, collapsed into one file** (`DATA-MODEL.md:2903`). After it, `UPDATE` is refused to every actor including `ADMIN`, and a column added later is `NULL` forever with no backfill path — *the backfill is an `UPDATE`* | **yes — the single tightest decision in round 3** (§5.1) |
| `RF-002` | **BLOCKER** | Negative stock is a shipped v1, seeded, per-item × per-site policy with its own resolver and log tables, and **the costing engine never says what an issue costs when no layer is open** — `issues/p2-16.md` contains the word *negative* zero times | **COVERED-uncited** | **`P2-16`** — one paragraph with a scenario. The defensible answer: **an issue with no open layer creates a negative layer** — a `whb_cost_layers` row with negative `quantity_remaining`, `cost_basis = 'ESTIMATED'`, and `unit_cost` from the resolved policy source (last receipt cost, then standard cost, then zero, **in that order, recorded on the row**) — and the covering receipt **consumes the negative layer first**, writing an ordinary consumption row that carries the difference as a *cost-variance* value-only movement rather than restating the original relief. That keeps `L-2` intact, keeps the difference visible on a report, and makes the retro-cost an auditable event rather than an edit. Two scenarios (`ALLOW` issue with no layer; the covering receipt) and an acceptance box asserting the variance movement exists **and nets to zero**. One line in **`P2-01`**. Needs a `cost_basis` vocabulary value, so it touches `V500021`'s DDL comment, not the ledger | **`V500021`** for the vocabulary value — before `PNR-1`. Recoverable afterwards only by re-costing a period, which the append-only design makes a reversal-and-repost across every affected issue | no |
| `RF-003` | **BLOCKER** | Landed cost on a **partly-consumed layer** has no split columns and no destination, and `WH-SC-153` — a **v1 happy path** — states both *"+4,500.00 at the receipt location"* and *"₹2,700 revalues the 72 EA remaining … ₹1,800 posts as a COGS adjustment"*; taken as written the remaining stock is overstated by ₹25/EA | **NEEDS-TASK** (amendment) | **`P2-17`** — header gains three columns on `wh_landed_cost_allocations` in `V510080`: `quantity_remaining_at_apply`, `amount_to_layer`, `amount_to_cogs`, with `amount_to_layer + amount_to_cogs = allocated_amount` as a `CHECK`. **Seed an eleventh virtual location for the cost-of-sales side and add it to `FR-084`'s list** — the movement is then `+2,700` receipt location, `+1,800` COGS location, `−4,500` value offset: three lines, and both quantity and value conserve. Rewrite `WH-SC-153`'s posting sentence to show the three lines its own second sentence already computes, and add the falsifier: *apply a charge to a fully consumed layer and assert the stock value does not move at all* | **The eleventh virtual location is a seed row in `V500013` — before `PNR-1`,** and it travels with `RE-002`'s ten. `V510080`'s columns are cheap until `quantity_remaining` moves, after which the split is unrecoverable | no |
| `RF-004` | **BLOCKER** | Foreign-currency costing ships in v1 (`FR-245`, `WH-SC-160`, `p2-16`'s acceptance) with **no rate source anywhere in the monorepo**, no `exchange_rate` field on the wire, and **no statement of which currency `unit_cost` and `layer_value` are in** | **DECIDED** | **`OD-16`** — the concurrent `DECISIONS.md` pass is promoting `PLATFORM-DEPENDENCIES.md` §2.12 to a numbered open decision; **reference it, do not allocate it here**. Deadline **before `P0-17` writes `V500021`**. The cheap answer: **v1 values in the install's single base currency; the layer's `currency_code`/`exchange_rate` record what was paid**, supplied by the producer on the movement line, frozen at post exactly as `conversion_factor_used` is under `L-7`. That is one field on the wire (`exchange_rate`, `DECIMAL(19,8)`, optional, defaulting to 1), one sentence in `DATA-MODEL.md` §5.1 declaring `unit_cost` and `layer_value` are **base currency** while `currency_code`/`exchange_rate` are the transaction's audit trail, and one `CHECK` that `currency_code <> base` implies `exchange_rate IS NOT NULL`. Falsifier on `WH-SC-160`: *the valuation report totals in base currency and the layer detail shows USD 42.00.* Folds into **`P2-16`** and **`P0-17`**; amends `PORT-AND-ADAPTER-CONTRACT.md` §2.5, `DATA-MODEL.md` §5.1, `PLATFORM-DEPENDENCIES.md` §2.12 | **`V500021`, before `P0-17`** — `IRR-36`: currency cannot be retro-fitted | **yes** (§5.2) |
| `RF-005` | **BLOCKER** | The value warehouse computes **has no column to land in on the accounting side**: `acc_source_document_movements` carries `quantity`, `unit_cost` and one date — no extended value, no currency, no cost basis — so the receiver must re-cost, which `FR-446`'s falsifier 2 exists to forbid | **DECIDED** | **`OD-1` gains a FOURTH reciprocal edit**, explicitly: add `extended_value`, `currency_code`, `exchange_rate` and `cost_basis` to `acc_source_document_movements`, plus a receiving rule *"where `extended_value` is present it is authoritative; `quantity × unit_cost` is never recomputed"*. **This is an edit in the `accounting` repository and it is that set's to make, not ours** — `DECISIONS.md:195` already says so for the first three. On the warehouse side: enumerate `envelope_kind`'s vocabulary in `DATA-MODEL.md` §2.1.11, and **`P2-18`** states that a warehouse handover fills `movements[]`, that `movement_date` = the warehouse `posting_date` (`L-13`'s accounting clock, **not** `occurred_at`), and that `cost_basis = ZERO_BAILMENT` suppresses the envelope entirely. Falsifier in `P2-18`: *post one AVCO issue whose extended value does not equal `round(quantity × unit_cost, 4)`, and assert the accounting-side value matches to the paisa.* Also **`P0-12`**. No warehouse migration | **Before accounting's `P3` starts.** `acc_source_document_movements` is P3 and unbuilt — exactly the window `OD-1` was created to use. Once it has rows the column is an `ALTER` plus a backfill with **no source**, because the warehouse envelope is stored as `TEXT` for replay (`DATA-MODEL.md:858`) | **yes — and the person is in another repository** (§5.4) |
| `RF-006` | MAJOR | Specific identification is a v1 requirement, a v1 happy-path scenario **and a v1 acceptance box**, and `whb_valuation_policies` has **no method value that can select it** | **COVERED-uncited** | **`P2-16`** — **`OD-6` was RESOLVED on 2026-09-03 by the concurrent `DECISIONS.md` pass — weighted average + FIFO in v1, standard in v1.1, LIFO never built and never seeded — and it says nothing about specific identification, which is exactly this finding.** The resolution therefore needs the rule made explicit rather than emergent: **`SPECIFIC` is not a policy value at all — it is implied.** An item whose `serial_control_mode` requires a serial is costed by specific identification regardless of category policy, because its layer is already keyed by `serial_id` (`DATA-MODEL.md:855`) and there is exactly one layer to consume. One sentence in `P2-16` and one in **`FR-235`** — *"specific identification is selected by the item's serial control, not by the valuation policy; the policy governs interchangeable stock only"* — closes it with no schema change and no fourth enum value. **If instead it is to be a policy value**, add `SPECIFIC` to `V500021` and an item-level override column to the policy key **before `PNR-3`**. Amends `OD-6`, `FR-235`, `DATA-MODEL.md` §2.1.11 | **`OD-6` has closed without it** — so this is now an amendment to a resolved decision, and it must land before `P2-16` builds the engine. The policy *key* is `PNR-3` (`IRR-40`) and changing it afterwards restates every balance; `IRR-40`'s *valuation grain* declaration is separately still owed to `P0-17` | no — the recommended answer needs no fourth enum value |
| `RF-007` | MAJOR | **Every rating modifier a 3PL contract actually contains** — minimum monthly charge, free days, minimum billable quantity, aged surcharge bands, rounding mode — is named in the requirement **and** in the task and **exists in no table** | **NEEDS-TASK** (amendment) | **`P5-01`**, **`P5-02`**, **`P5-04`** — headers gain the columns restored into `DATA-MODEL.md` §2.3 and the `V530010`/`V530021`/`V530031` DDL: `wh3_clients.{go_live_date, minimum_monthly_charge, minimum_scope, tax_profile_id}`; `wh3_rate_card_lines.{free_quantity, minimum_charge, maximum_charge, rounding_mode}`; a **`wh3_storage_aging_bands`** child of the rate-card line; `wh3_storage_billing_lines.{free_days_applied, days_charged, is_prorated}`. Extend `method` with `SPLIT_MONTH` and `basis` with `LOCATION`, `WEIGHT` and the occupied/allocated split, **or** amend `FR-288` down to what will be built and say so — either is fine, **disagreeing is not**. Enumerate `wh3_rate_card_lines.basis`'s whitelist in the same edit | Before `P5` starts. After the first billing run these are an `ALTER` plus a **re-rate of a period a client has already paid**, which `FR-292` forbids | no |
| `RF-008` | MAJOR | The billing meter and the client contract are **specified twice** and the two specifications disagree on **eleven columns**, on the rate-card status vocabulary, and on **whether the meter can be updated at all** | **NEEDS-TASK** (amendment) | **`DATA-MODEL.md` §2.3 is the authority, so it takes `issues/p5-03.md`'s columns, not the reverse.** Resolve the three conflicts explicitly: `source_event_key` vs `idempotency_key` (pick one — it is a unique index); the eight subject FKs vs the generic pair (**the generic pair is the house style, §1.9**); `SUPERSEDED` vs `EXPIRED`. Then state the mutability rule **once**: the meter is append-only **except** `billing_run_id` and the four rating columns, guarded by a `to_jsonb`-diff trigger with an explicit allowlist — the same shape as `I-2` — **and therefore `wh3_billable_events` does need `updated_at`/`updated_by` after all, so `DATA-MODEL.md:104` must lose that row.** Headers change on **`P5-03`** (+ `P5-01`, `P5-02`, `P5-05`); migrations `V530010`, `V530021`, `V530030` | **Before `V530030` is written.** `wh3_billable_events` is the 3PL equivalent of the stock ledger — adding `unit_rate`/`rated_amount` after the first billed period leaves every historical event with NULL rating data and every historical dispute unanswerable | no |
| `RF-009` | MINOR | `R-4`'s largest-remainder tie-break is `line_no`, and **two of the three cases `R-4` itself names have no `line_no`** | **COVERED-uncited** | **`P5-05`** — add `line_no INTEGER NOT NULL` to `wh3_billing_run_lines` with `uk(run_id, line_no)` in `V530040` (which `grep -rln V530040 issues/*.md` confirms `p5-05.md` claims), and name the kit-output ordinal when **`P3-11`**'s table is specified. Amend `R-4` in `DATA-MODEL.md` §5.3: *"ties broken by the sink's declared ordinal — `line_no` on a document line, `line_no` on a billing run line, `sequence` on a kit output — and every sink of a largest-remainder split must declare one."* | Before `P5-05`. One column; trivial to fix, embarrassing to explain | no |
| `RF-010` | MINOR | The two documents a reader consults about the accounting seam **still quote the overruled version of `D-6`** — *"accounting is the system of record for value"* — which `DECISIONS.md:146-195` rewrote and `FR-230` carries | **COVERED-uncited** | Documentation only, **no task, no migration**. Replace the stale quote at **`COEXISTENCE.md:154`** and **`COMPETITOR-BENCHMARK.md:583`** with `D-6`'s current sentence and add the second half — *"and therefore for cost"* — and update **`COMPETITOR-BENCHMARK.md:966`** from **AMBIGUOUS** to the resolution, citing `X-032`'s precedent for exactly this staleness in `IRREVERSIBLE.md` §7.3. **Travels with `RF-005`**, because `COEXISTENCE.md:167-174` is the only place the `acc_source_document_movements.unit_cost` write-once problem is written down | With the next `COEXISTENCE.md` edit. Cheap, and free now | no |

### 2.7 The disposition tally

| Bucket | Count | Findings |
|---|---:|---|
| **`CITED`** | **0** | — round 3's findings are new; none is already carried with its citation |
| **`COVERED-uncited`** | **39** | `RA-003` `RA-004` `RA-005` `RA-006` `RA-007` · `RB-001`…`RB-009` (all 9) · `RC-001` `RC-002` `RC-003` `RC-004` `RC-005` `RC-006` `RC-008` · `RD-002` `RD-003` `RD-004` `RD-005` `RD-006` `RD-007` `RD-008` · `RE-001` `RE-002` `RE-003` `RE-004` `RE-005` `RE-007` `RE-008` · `RF-002` `RF-006` `RF-009` `RF-010` |
| **`NEEDS-TASK`** (all amendments to named existing tasks) | **10** | `RA-001` (`P1-18`) · `RA-002` (`P2-25`) · `RA-008` (`P2-01`) · `RC-007` (`P2-21`) · `RC-009` (`P6-02`) · `RE-006` (`P0-16`) · `RF-001` (`P0-02`+`P2-16`) · `RF-003` (`P2-17`) · `RF-007` (`P5-01`/`P5-02`/`P5-04`) · `RF-008` (`P5-03`) |
| **`DECIDED`** | **3** | `RD-001` → **`OD-17`** · `RF-004` → **`OD-16`** · `RF-005` → **`OD-1`**, fourth reciprocal edit |
| **`WONTFIX`** | **0** | — |
| **Total** | **52** | |

**Zero new task files.** That is the headline of §4 and it is the same shape round 2 found: the task set
is right, the task files are thin.

---

## §3 · The sixteen BLOCKERs, walked — the section a delivery lead reads

Ordered by **when the finding stops being free**, not by lens. Eleven of the sixteen are gated at or
before `PNR-1` (`V500030`) or by a decision that must precede it.

### 3.1 At or before `PNR-1` — nine of the sixteen

| # | Gate | Finding | Owning task | What must land before it, and why it cannot wait |
|---|---|---|---|---|
| 1 | **`V500012`/`V500013`** virtual locations | **`RE-002`** | `P1-05` | The ten `FR-084` purposes, spelled one way, on the `VIRT-<PURPOSE>-<SITE CODE>` convention, **plus the rule that creating a warehouse creates its virtual-location set in the same transaction** — because the stated mechanism cannot give a second site any virtual locations at all. `whb_locations.code` is a stable key ledger rows resolve against (`IRR-26`); renaming it after the first movement means rewriting `whb_stock_movement_lines`, which `L-2` forbids |
| 2 | **`V500013`** the same seed | **`RF-003`** | `P2-17` (+ `P1-05`) | **An eleventh virtual location, for the cost-of-sales side of a landed-cost split.** Without it the v1 happy path `WH-SC-153` posts ₹4,500 into stock when its own second sentence says ₹1,800 belongs in COGS, and the remaining stock is overstated by ₹25/EA. It travels with item 1: one seed migration, eleven rows, one editing pass |
| 3 | **`V500013`** (conditional) | **`RB-002`** | `P1-05` | `check_digit` on `whb_locations`, **or** an explicit written decision that GS1 location labels do without it. Two of `WS-017`'s eight phantom fields are add-or-delete calls on the hottest master in the base module; after `V500030` an addition is a schema change on a table the ledger FKs into |
| 4 | **`V500019`** stock periods | **`RE-001`** | `P0-07` (+ `P2-19`) | **A seed for the current and next period, a `Generate periods` action on `WS-045`, and a `MONTHLY`/`CATCH_UP` job in `P0-13`'s register.** Today `period_id` is `NOT NULL`, nothing creates a period, and the one described creation path is guarded *"the previous period exists"* — so a fresh install cannot post its first movement, and every P0 acceptance test that posts one fails on an FK violation nobody can read |
| 5 | **`V500021`** cost layers | **`RF-004`** | `P0-17` (+ `P2-16`) · **`OD-16`** | **Which currency `unit_cost` and `layer_value` are in**, and an `exchange_rate` field on the wire. `IRR-36`: currency cannot be retro-fitted. The decision is being numbered `OD-16` by the concurrent `DECISIONS.md` pass; the deadline is *before `P0-17` writes `V500021`* |
| 6 | **`V500021`** cost layers | **`RF-002`** | `P2-16` (+ `P2-01`) | **A `cost_basis` value for `ESTIMATED`, and one paragraph saying what an issue costs when no layer is open.** `negative_stock_mode = ALLOW` is a shipped v1 policy with its own resolver and log tables, and every conservation invariant passes while the value is wrong |
| 7 | **`V500030` = `PNR-1` + `PNR-2`** | **`RF-001`** | `P0-02` (+ `P2-16`) · **decision** | **Does the moving average restate on a backdated receipt?** Four documents say yes; `I-2`'s trigger ships an empty mutable-column allowlist and `DATA-MODEL.md:2480` says the column is frozen. **The v1 acceptance box cannot be passed by any implementation.** After `V500030`, `UPDATE` is refused to every actor including `ADMIN`, so if the answer is *restate*, the allowlist must grow its sixth column **in that file** — and if it is *never restate* (recommended), four documents and one scenario must say so before a builder guesses. See §5.1 |
| 8 | **`P0-11`'s outbox migration** | **`RD-002`** | `P0-11` (+ `P3-22`) | Two nullable columns on the **v1** table (`signing_algorithm`, `delivery_timeout_seconds`), the signed-request and status→ladder `PC-` rows, **and — immediately — either `WS-057` refusing `transport = HTTP` in v1 or `PC-46` exempting a subscription that has never had a delivery attempt.** A v1 HTTP subscription pins outbox retention forever, and that consequence is not reversible once the outbox has grown |
| 9 | **accounting `V600xxx`, accounting's P3** | **`RF-005`** | `P2-18`/`P0-12` · **`OD-1`** | **Four value columns on `acc_source_document_movements`** and a receiving rule that `extended_value` is authoritative. This is a **fourth** reciprocal edit inside `OD-1`, in the *other* repository, and it is free only while accounting's P3 is unbuilt. Once it has rows the backfill has no source: warehouse's envelope is `TEXT` for replay (`DATA-MODEL.md:858`) |

### 3.2 After `PNR-1`, and still on the critical path — seven of the sixteen

| # | Gate | Finding | Owning task | What must land before it |
|---|---|---|---|---|
| 10 | **Before `P1-12`, `P1-13`, `P2-08`, `P2-10` are signed off** | **`RB-001`** | six documents + five task files | **`C-044` is wrong.** Amend it, propagate through `FR-220`, §0.7, `IRREVERSIBLE.md:723`, `DATA-MODEL.md:4172`, `INDIA-LOCALISATION-PACK.md:446`, `PLATFORM-DEPENDENCIES.md:369`, then delete the four option-less `<x>Within` keys and restore the `…From`/`…To` pair. Four task files carry an invented key **in an acceptance criterion**, so each will otherwise be signed off as met |
| 11 | **Before `P1-18` writes the resolver** | **`RA-001`** | `P1-18` (+ `P1-05`) | `whb_warehouse_grants` mirroring `whb_owner_grants`, `WS-238` Warehouse Grants, and **the shipped default stated**. A resolver written against branch scope and later widened to a third axis is every management query in two modules re-touched — and `P1-18`'s own acceptance (*"a user restricted on all three axes"*) is vacuous until the third axis exists |
| 12 | **Before `P2-14` prints anything — physically irreversible** | **`RD-001`** | `P2-14` ↔ `P3-24` · **`OD-17`** | **Move the SSCC allocator into v1, or take GS1-128 out of the v1 eleven.** A label is glued to a pallet, and `FR-064`'s own justification for a v1 `sscc` column is *"issuing them later means re-labelling"*. Recommended: move the allocator |
| 13 | **Before `P2-18`** | **`RC-002`** | `P2-18` | `ownerName`/`itemCategoryName` grain, a drill-through to `WS-209`, and a **`GlBalanceProvider` port interface declared in `warehouse-base` with no implementation there** — the only read direction across the accounting seam. Today the reconciliation *"that makes a finance director trust the system"* compares warehouse to its own outbox |
| 14 | **Before `P2-20`** | **`RC-001`** | `P2-20`/`P2-18`/`P2-21` | **A mandatory `Clock` column on all 20 rows of §7**, and a `WH-SC-060` that names the clock. Not schema-irreversible; **practically irreversible after go-live**, because a bank stock statement, a section-44AB quantitative statement and a 3PL invoice are held by third parties |
| 15 | **Before `P2-25`, which is `OD-9`'s corrected deadline** | **`RA-002`** | `P2-25` | `whad_price_levels` + `whad_item_prices` in `V520015`, adapter-owned, with an `ImportButton` screen — **or** `OD-9` resolves that the counter sale leaves the warehouse module and the finding evaporates. Today the counter clerk cannot price a line |
| 16 | **Before `P0-16` §4 is signed** | **`RD-003`** | `P0-16`/`P3-04` | The queue is **durable and never evicts**, bounded by refusing new scans; the substrate is chosen explicitly; `backgroundLocationService.ts` is cited as the precedent **and the policy counter-example**. Reversible in design; **each dropped scan is not** |

---

## §4 · What round 3 adds to the backlog

### 4.1 New task files: none

**No round-3 finding requires a task file that does not exist.** All 52 land in the 143 files already
authored. That is the same verdict round 2 reached with one exception (`P1-21`), and it is the strongest
evidence available that the task *set* is right.

### 4.2 The ten amendments that change a task header

These are the rows the next wave cannot do as a body edit, because the file's header line — its
`Migrations`, `Screens` or deliverables — becomes false otherwise:

| Task | Header today | Header after | Finding |
|---|---|---|---|
| **`P1-18`** | `Migrations **none** · Screens **none**` (`issues/p1-18.md:5`) | one `warehouse-base` P1 migration (`whb_warehouse_grants`) · `WS-238` | `RA-001` |
| **`P2-25`** | adapter tables as listed | `+ V520015` — `whad_price_levels`, `whad_item_prices` · one Department-shape screen with `ImportButton` | `RA-002` |
| **`P2-01`** | `V510030` as listed | `+ wh_adjustment_approval_policies` in `V510030` | `RA-008` |
| **`P2-21`** | report pack 2 | `+ whb_metric_definitions`, `wh_metric_targets` on a migration **next free in `V510…`, taken from `DATA-MODEL.md` §8.4's ledger** · one admin screen · one new `FR-` for targets | `RC-007` |
| **`P6-02`** | ABC/velocity recompute | `+` the location-utilisation report, one new `FR-` in §6.22 at v3, `WS-238` | `RC-009` |
| **`P0-16`** | non-functional foundations | `+ docs/INSTALL.md` as a **deliverable**, with the `grep`-resolvable acceptance | `RE-006` |
| **`P0-02`** | `V500030` | unchanged **if** the answer is *never restate*; `I-2`'s allowlist gains a sixth column **if** it is *restate* | `RF-001` |
| **`P2-17`** | `V510080` | `+` three columns on `wh_landed_cost_allocations` with a summing `CHECK`; `+` one seed row in `P1-05`'s `V500013` | `RF-003` |
| **`P5-01` `P5-02` `P5-04`** | `V530010` `V530021` `V530031` | `+` the four `wh3_clients` columns, the four `wh3_rate_card_lines` columns, `wh3_storage_aging_bands`, the three `wh3_storage_billing_lines` columns | `RF-007` |
| **`P5-03`** (+ `P5-01` `P5-02` `P5-05`) | `V530010` `V530021` `V530030` | reconciled against `DATA-MODEL.md` §2.3 on eleven columns; `wh3_billable_events` gains `updated_at`/`updated_by` and `DATA-MODEL.md:104` loses its row | `RF-008` |

Each of these also needs its `IMPLEMENTATION-PLAN.md` §2 row and its phase-epic table row updated in the
same commit, or check-8 and check-9 will catch it.

### 4.3 The next free task id per phase, computed — and the issue-filing rule

```bash
cd /Users/bbhushan/work/git/workspace/warehouse-issues
for p in 0 1 2 3 4 5 6; do
  last=$(ls issues/p$p-*.md | sed "s|issues/p$p-||;s|\.md||" | sort -n | tail -1)
  echo "p$p: highest p$p-$last · next free p$p-$(printf '%02d' $((10#$last+1)))"; done
ls issues/p*.md | wc -l          # -> 143
ls issues/p2in-*.md | wc -l      # -> 4  (the India wave is p2in-01..04, outside the p<n>- series)
```

| Phase | Highest today | Next free |
|---|---|---|
| P0 | `p0-17` | **`p0-18`** |
| P1 | `p1-21` | **`p1-22`** |
| P2 | `p2-29` | **`p2-30`** |
| P3 | `p3-24` | **`p3-25`** |
| P4 | `p4-13` | **`p4-14`** |
| P5 | `p5-23` | **`p5-24`** |
| P6 | `p6-12` | **`p6-13`** |

**Round 3 claims none of them.** Recorded because one amendment is a plausible split: if the delivery
lead prefers `RA-001`'s table and screen in a file of their own rather than inside `P1-18`, that file is
**`p1-22`**.

**If a new task file is ever created for a round-3 finding, an issue must be filed for it.**
`issues/CREATED.md` now exists, every task file carries an `issue: NN` line
(`grep -l "^issue: " issues/p*.md | wc -l` → **143**), and `check-design-set.py` check 5 resolves every
`#NN` cross-reference against that map. The number comes from `create-issues.sh`, **never from an
author**: `CREATED.md`'s own preamble records that the sequence is shared with pull requests, which is
why the tasks run #12–#154 rather than #10–#152. **Do not invent one.**

### 4.4 The `WS-238` collision — three findings, one next-free id

`WS-237 RF Task List` (`BUILD-SPEC-SCREENS.md:686`) is the last allocated screen; `WS-238` is the
**next-free allocation marker**, fenced by `issues/p5-13.md:47` and declared as an exemption in six
files. **Three round-3 findings each propose taking it**, and two of them are in the same lens:

| Finding | Proposed screen | Order |
|---|---|---|
| `RA-001` | **Warehouse Grants** — the site-scope grant screen, `P1`, the Customer reference beside `WS-020` | first, if `RA-001` is built as an amendment to `P1-18` |
| `RA-002` | **Item Prices** — the adapter-owned price screen, `P2`; R16's own exemption note says it takes *"the id after"* `RA-001`'s | second |
| `RC-009` | **Location Utilisation** — v3 · `P6-02` | last, and the only one whose version makes it safe to defer |

**They cannot all be `WS-238`.** The allocation order above is the recommendation: the two v1 screens
take `WS-238` and `WS-239`, `RC-009`'s v3 screen takes whatever is next free when it is authored, and
the marker moves once — in the same commit that writes the rows — exactly as `WH-SC-306` was handled
when round 2's `Q-006` minted five scenario ids. **Do not write a `WS-238` row in one file and leave the
marker at `WS-238` in the other seven.**

### 4.5 Shared platform files — the "two files" budget is wrong

The set has consistently budgeted **two** platform files. Round 3 establishes **four certain and two
conditional**, all verified against the live tree:

| # | File | Why | Finding | Status |
|---|---|---|---|---|
| 1 | `platform/frontend/src/utils/filterUtils.ts:346` (`COMMON_FILTER_CONFIGS`) | every warehouse filter scope | already budgeted | certain |
| 2 | `platform/backend/src/main/java/ai/platform/config/CacheConfiguration.java:101` (`setCacheNames`) | every warehouse statistics cache | already budgeted | certain |
| 3 | `platform/frontend/src/app/dashboard/admin-settings/page.tsx` — a thirteenth tab beside `id: 'docOcrAi'` at `:151` | the warehouse settings tab; there is no other screen for the seven install keys | **`RE-003`** | **certain, newly established** |
| 4 | `platform/backend/src/test/java/ai/platform/service/ExportServiceContractTest.java:137` — the scanner takes a package list; `:80`'s `WITHOUT_AUDIT_COLUMNS` gets an `isLedgerStyle()` hook rather than 43 new names | six task files cite this ratchet and it discovers **zero** warehouse services today | **`RB-005`** | **certain, newly established** |
| 5 | `platform/frontend/src/components/common/DynamicDataTable.tsx` — an optional `summaryRow` prop (`grep -c "summaryRow\|footer"` → **0**) | `WS-210` is read column-wise and the v1 exit criterion requires a footer; propose separately, as `PP-6` did for the export cap | **`RC-004`** | conditional — proposed, not assumed |
| 6 | `platform/backend/…/constants/SecurityConstants.java` + `config/SecurityConfig.java:159` | only if a module ever exposes an unauthenticated inbound endpoint | **`RD-007`** | conditional |

`D-10`'s §11 corollary already concedes the honest form of this — *"never zero commits to `platform`"*.
**`MODULE-INTEGRATION.md` §12 is where the ledger lives and where all four certain rows belong.**

### 4.6 The documents amended, grouped by what you open

Round 3's output is again overwhelmingly *lines added to files that already exist*. Grouped so the work
is one pass per file:

| Target | Findings | Nature of the edit |
|---|---|---|
| `BUILD-SPEC-SCREENS.md` **§7** (the report table) | `RC-001` `RC-004` `RC-006` `RC-005` `RB-008` | a mandatory **`Clock`** column and a **`Statistics strip`** column, both non-blank for all 20 rows; an `L-14` preamble; a required-parameter preamble; option lists for four enum filters |
| `BUILD-SPEC-SCREENS.md` **§0** | `RB-006` `RB-007` `RB-009` | a new **§0.13** empty/loading/tiles rule in §0.7's shape; a `/validate/{code|name}` row in §0.6; the screen-refusal error-code register in `PORT-AND-ADAPTER-CONTRACT.md:563`'s columns |
| `BUILD-SPEC-SCREENS.md` **§10.2** | `RA-007` | two gates the port needs and no screen has: `whb_stock_movements:post_backdated`, `whb_outbox:view`; §10.2 becomes the sole seed authority |
| `BUILD-SPEC-SCREENS.md` `WS-017` | `RB-002` | six renames, `commingePolicy` in both places, three add-or-delete decisions |
| `PORT-AND-ADAPTER-CONTRACT.md` | `RA-005` `RA-007` `RC-002` `RD-002` `RD-004` `RF-004` | `PC-31` rewritten to §10.2's names and its `prev_payload_hash` row de-v2'd; §4 records the single GL read direction; §4.5 gains three webhook `PC-` rows; §3.4 gains the batch request and replay rows; §2.5 gains `exchange_rate` |
| `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` | `RB-001` `RC-007` `RC-009` `RD-005` `RD-006` `RD-008` `RE-002` `RF-006` `RA-002` `RA-006` | `FR-220`'s false clause; §6.22's twenty-nine metrics + a target `FR-` + the v3 utilisation `FR-`; `FR-196`'s adapter sentence; `FR-224`; **`FR-039` folded to 43 codes, once, carrying `RB-009`'s nineteen and `RD-004`'s two**; `FR-084`'s ten purposes (eleven with `RF-003`); `FR-235`; `FR-359`; `FR-185` |
| `DATA-MODEL.md` | `RB-004` `RC-003` `RE-002` `RE-005` `RF-006` `RF-008` `RF-009` `RA-008` `RF-005` | `:527` gains `BLOCKED`; `WS-211`'s Reads cell; `:478-481`'s ten codes; §7.2 gains a **seed authority** column (closing `X-004`); §2.1.11's method and `envelope_kind` vocabularies; §2.3 reconciled on eleven columns and `:104`'s row removed; §5.3's `R-4` tie-break; `:999`'s threshold prose |
| `IRREVERSIBLE.md` | `RB-001` `RF-001` | `:723`'s mobile-filter clause; `IRR-39`'s restatement sentence |
| `MODULE-INTEGRATION.md` | `RB-005` `RC-002` `RD-007` `RE-008` | §12 gains the third and fourth platform files; §2 gains a 23rd row; §15's disable row corrected |
| `PLATFORM-DEPENDENCIES.md` | `RB-001` `RC-004` `RD-003` `RD-007` `RF-004` | `:369`; a new `PP-` row for `summaryRow`; §3.3's *"nothing queues"* correction; §2's allow-list sentence; **§2.12 promoted to `OD-16` by the concurrent pass** |
| `SCENARIO-CATALOGUE.md` | `RA-004` `RA-005` `RA-007` `RC-001` `RC-006` `RF-001` `RF-003` `RF-004` `RA-002` | `WH-SC-060` names its clock + one new `edge`; a consignment/`WS-210` scenario; `WH-SC-021`-shape withdrawal scenario; `WH-SC-022`/`WH-SC-241` re-pointed at seeded permission names; `WH-SC-151`'s restatement; `WH-SC-153`'s three lines; `WH-SC-160`'s base-currency falsifier; one `WH-SC-216`-shape price scenario |
| `COEXISTENCE.md` · `COMPETITOR-BENCHMARK.md` | `RF-010` `RC-008` `RE-004` | the two stale `D-6` quotes and `:966`'s AMBIGUOUS row; `:467`'s v1.1 auditor-artefact row; `:238`'s v1.1 tolerance row |
| `docs/reviews/R1-codebase-reality.md` | `RB-001` | `C-044`'s second clause corrected — **the only round-1 finding round 3 overturns** |

---

## §5 · What needs a person, not an author

Twelve items cannot be authored around. The first six are hard gates; the rest are smaller calls that
still need somebody's name on them. **Two allocations are being made by the concurrent `DECISIONS.md`
pass and are referenced here, not allocated.**

| # | Decision | Deadline | Why it cannot wait |
|---|---|---|---|
| **1** | **`RF-001` — does the moving average restate on a backdated receipt?** Recommended: **never restate** — `moving_average_after` is a snapshot, the current average is computed on read from the open layers. The answer must then be written into `IRR-39`, `WH-SC-151`, `issues/p2-16.md:140,168` and `DATA-MODEL.md` §6.4, and **recorded as a new `D-` row by the `DECISIONS.md` pass — do not number it here** | **Before `P0-02` writes `V500030`** | `V500030` is `PNR-1` **and** `PNR-2` in one file (`DATA-MODEL.md:2903`). After it, `UPDATE` is refused to every actor including `ADMIN`; if the answer is *restate*, `I-2`'s allowlist must grow its sixth column **in that file**, and no later migration can add it usefully because the backfill is itself an `UPDATE`. Today the v1 acceptance box is unpassable by any implementation |
| **2** | **`RF-004` — foreign-currency costing.** Which currency are `unit_cost` and `layer_value` in, and where does a rate come from? Being allocated as **`OD-16`** (promotion of `PLATFORM-DEPENDENCIES.md` §2.12) by the concurrent pass | **Before `P0-17` writes `V500021`** | There is **no rate source anywhere in the monorepo**, the port has no `exchange_rate` field, and `IRR-36` says currency cannot be retro-fitted. `FR-245`, `WH-SC-160` and `p2-16`'s acceptance are all v1 and all three need a rate |
| **3** | **`RD-001` — SSCC and the GS1-128 pallet label.** Move the allocator into v1, or take GS1-128 out of the v1 eleven. Being allocated as **`OD-17`** by the concurrent pass. R19 recommends the move | **Before `P2-14` prints anything** | **The only physically irreversible finding in the round.** Labels are glued to pallets and cannot be recalled; `FR-064`'s own argument for a v1 `sscc` column is that *"issuing them later means re-labelling"*, and this version pairing guarantees exactly that |
| **4** | **`RF-005` — `OD-1` gains a FOURTH reciprocal edit**: `extended_value`, `currency_code`, `exchange_rate`, `cost_basis` on `acc_source_document_movements`, plus *"where `extended_value` is present it is authoritative"* | **Before accounting's `P3` starts** | The edit is in **another repository**, and `DECISIONS.md:195` already establishes that those edits are that set's to make. It is free only while `acc_source_document_movements` is unbuilt; afterwards the backfill has no source, because the warehouse envelope is stored as `TEXT` for replay. This is the second round in a row that `OD-1` has grown without a reciprocal commitment being obtained, and it is **ESCALATED** as of 2026-09-03 |
| **5** | **`RA-002` / `OD-9` — is pricing warehouse's business at all?** If the counter sale stays, `P2-25` gains two adapter-owned price tables and a screen; if `OD-9` moves it out, the finding evaporates | **Before `P2-25`** — the deadline round 2 already corrected `OD-9` to, and `OD-9` is **ESCALATED** as of 2026-09-03 | Round 2's `U-003` established that `P2-25` builds the losing side of `OD-9`. Round 3 shows the same table cannot even price a line. Deciding `OD-9` answers both; deciding neither builds a counter sale nobody can use |
| **6** | **`RC-001` — which of `L-13`'s three clocks does each of the twenty reports read?** A recommended assignment exists; it needs a **finance sign-off**, not an author's preference | **Before `P2-20`** | The godown statement goes to a bank, the quantitative statement goes to a tax auditor, and the 3PL figure goes on an invoice. Once those are issued, changing the clock **restates numbers a third party already holds** — the practical equivalent of irreversibility |
| **7** | **`RA-007` — one permission namespace must lose**, `PC-31` or §10.2 (recommended: §10.2 wins and `PC-31` is rewritten). **Answer round 2's still-open `Q-003` — does AUDITOR receive `:export`? — in the same migration** | **`V501000`** | Permission *names* are `IRR-63`: forward-only. A rename after roles have been built on it is hand work in every deployed environment, which is the exact argument `FR-407` uses to reserve `logistics:*` in v1. `Q-003` has now survived two review rounds unanswered |
| **8** | **`RA-006` — build the v1 `BIN_TO_BIN` emergency-replenish path, or withdraw the offer from `FR-185`** | Before `P2-09` | Either is acceptable; **silence is not**. A screen that offers a button it cannot honour is the worse of the two, and it is the picker who finds out |
| **9** | **`RD-005` — do carrier connectors live in an adapter, or in the app?** If the app, it needs an `OD-` row of its own | Before `V510044` (`P2-10`) | It is the **mirror image** of a decision the set took explicitly in the other direction for channels (`FR-207`). Two task headers already name a module class `D-1` does not contain, so the ambiguity is already producing wrong text |
| **10** | **`RE-007` — is `near_expiry_days` an item property or an install default?** Recommended: item × site with an install fallback. R20's own words: *"a decision that is not yet an `OD-`"* | Before `V500050` | Small, but `WH-SC-130`'s 45 is currently a constant in a scenario rather than a fixture value, so the test proves nothing about the configurable behaviour |
| **11** | **`RC-009` — build the location-utilisation report at v3, or refuse it in writing** in §9's refusals table with a reason | Before P6 planning | `D-12` forbids the third option. The facts are captured from v1, so this is a placement decision, not a schema one; the cost of getting it wrong is a demo against an incumbent |
| **12** | **`RB-002` — three fields with no column**: `check_digit` (probably add, at `V500013`), `isPickable` and `isReceivable` (probably delete) | **`V500013`**, before `PNR-1` | Two of the three are on the hottest master in the base module. Whichever way each goes, `P1-05` writes it down |

### 5.1 Two things a lens could not close, and did not file as defects

Both are recorded here so round 4 does not re-derive them, and both need an answer from a person rather
than more reading:

- **`FR-244`'s transfer price.** An inter-branch transfer must carry **two** numbers — a transfer price
  for the tax document and a cost that follows the goods. `FR-236` states the cost half. R21 could not
  establish whether `whin_delivery_challans.declared_value` (`DATA-MODEL.md:1196`) **is** the transfer
  price or a separate insurance figure, and could not find a transfer-price column on
  `wh_transfer_orders`/`_lines`. **UNVERIFIED.** What settles it: a `valuation_basis`/`declared_value`
  semantics sentence in `DATA-MODEL.md` §2.4 or in `p2in-01`, or one `WH-SC-` scenario showing both
  numbers on one transfer. If `declared_value` is not the transfer price, this is a real gap.
- **Whether `WS-015`'s and `WS-045`'s *Actions* cells are exhaustive**, or list only the non-obvious
  verbs. The Department and Service Vehicle references both carry an **Add** toolbar button, so a create
  path may be implied. `RE-001` is deliberately written so it does not depend on the answer — the seed,
  the job and the guard are each independently missing — but **two reviewers have now had to guess**, so
  `BUILD-SPEC-SCREENS.md` §0.2 should state the convention once.

---

## §6 · What round 3 did NOT find — the axes that came back clean

A round that reports only gaps misrepresents the set. Six lenses swept six new surfaces and **did not
file a single finding** against the following, each of which they went looking for and each of which is
recorded in a `§3 What I checked and found sound` section:

**The ledger invariants held.** Not one of `L-1`…`L-14`, `I-1`…`I-19` or `IRR-01`…`IRR-63` was disputed
by any of the six lenses. `RF-001` and `RC-006` are *applications* of `I-2` and `L-14` that the set
failed to make — the invariants themselves survived a costing lens, a reporting lens and a wire lens
reading them adversarially. That is the single most reassuring result in the round.

| Axis | What came back clean |
|---|---|
| **Persona** | 3 of 16 roles **COMPLETE** and the two v2-only roles correctly deferred. The stock controller is the best-served persona in the set (programme by ABC class, blind counts with the book snapshot stored anyway, tolerance by percentage **and** value, recount, `FR-408`'s self-approval bar). The buyer's decision surface is complete. Maker–checker is a **stated rule** with a `403` scenario, not an assumption. The auditor is read-only and it is **asserted** (`P0-15`'s trap). Cost suppression by actor is already owned by `K-002` → `P1-18`. The 3PL client's row-level segregation exists in v1 even though the portal is v2. `wh_blocked_movements` — *"refusing the transaction does not un-move the goods"* — is the best single decision in the set for the operator personas. Device and scheduler are first-class non-human actors |
| **Screen** | `BUILD-SPEC-SCREENS.md` is *"the strongest screen specification in either design set"*; the eight filter types are correct against `filterUtils.ts:36-59`; the **grid** half of every block — `gridIdentifier`, filter scope, per-column `table.column` source, export superset, row actions with gates, mobile verdict — is buildable as written. R17 re-filed **none** of `H-002`, `Q-002`, `Q-004` or `Z-004`, which own the form half |
| **Reporting** | As-at is computed **from movements, never from balances**, stated three times and made an acceptance box; snapshots are *"explicitly a cache"*. A back-dated post legitimately changing a past as-at answer is **written down** (`PC-25`, `WH-SC-040`) with the `sequence_no` on the response so a consumer knows why. The reports prove themselves **against a rebuild**, not against each other (`WH-SC-061`). Ageing is measured from the **last outward movement**. `FR-392` refuses to compute a KPI from `updated_at` and `FR-213` pulled the task timestamps into v1 for it. Pre-aggregation is **refused until measured**. Engineered labour standards are **refused in writing with a re-entry condition**. Owner scope is a record-level guard with a build-failing contract test. The widget `chk_module` trap is known and fixed by read-and-union rather than a restated list. Mobile report verdicts are stated, including `none` with a reason. `PNR-3`/`IRR-51` — that ageing and 3PL anniversary billing begin the day the snapshot job was switched on — is flagged more loudly by the set than a reviewer would |
| **Integration** | **Channels are better specified than carriers by a wide margin**: `FR-207`'s owning-module rule, `FR-208`'s idempotency on `(channel account, external order id)` **with an external version so a stale re-poll is discarded** plus an import decision log, and `FR-209`'s publish rules with a publish log recording what the channel acknowledged. EDI is refusal #20 with a stated reason. The **automation seam** is right: `actor_type = DEVICE`, `device_id` on the movement, task timestamps in v1 so RF and automation are new consumers rather than rewrites, and the outbox subscribable **by row**. The port's boundary discipline — `FR-041`/§2.9's list of what the port must **not** carry, with a destination for each, and `p0-08`'s test that a payload carrying a carrier, a sales price or a JSONB blob is **rejected, not ignored** — is what keeps the seam from rotting. `PC-30`/`PC-32` return `403` rather than a filtered grid, *"because an empty grid is indistinguishable from no stock"* |
| **Configuration** | Twenty-two rows of sound design, including: every extensible vocabulary a table with no `CHECK`, **proved by a build-time test**; `code` immutable after create; seeds idempotent on a Flyway retry; the mobile zod-enum trap named where it bites; reorder policy at item × site; valuation policy effective-dated rather than switched in place; `whb_gl_posting_rules`' specificity ladder with a **Test resolution** modal (the exemplar `Z-001` asks the others to copy); putaway rules in an explicit `uk(warehouse_id, sequence)` order; counting as a **policy object**; GSTIN on the branch, not the warehouse; `owner_id` on the line, not the header; exactly one house owner and **no single-owner mode**; the adapter package a sibling so a component scan cannot load it; `MODULE-INTEGRATION.md` §15 — *"the best rollback section in either design set"*; both `default_columns` **and** `default_filters` seeded; `filter_definitions`, never `grid_filter_definitions`; three locales on every menu; `permission_dependencies` **inserted, never created**, with `dependent_permission_id` named correctly; `logistics:*` reserved in v1; retention as a country-neutral policy table; precision fixed once and cited; and `P2-19`'s go-live batch as a first-class object with a dry run that persists nothing and a signed certificate |
| **Money** | The costing **architecture** is right and better than anything shipping in this monorepo: `D-6` puts the engine where the grain is; `FR-234` insists on layers **plus** consumptions rather than a cost column on a balance; `FR-240` makes revaluation a document; `L-14` refuses to value other people's goods; §5.3's five rounding rules and §5.4's rounding-away-from-zero analysis are the most careful numeric writing in either set; and `C-027` — the live accessories defect where the valuation report reads `last_cost` while the balance carries `average_cost` — is named, understood and designed against. On the 3PL side, the SLA measurement stores **numerator and denominator**, not just a percentage, and freight billing's four modes are typed correctly under the precision tie-break |

**And the negative result that matters most:** across 52 findings, **zero** contradicted a round-1 or
round-2 *disposition*. Round 3 overturns exactly one earlier **fact** — `C-044` — and it did so by
reading the live tree, which is the one thing a design-set review cannot do from documents.

---

## §7 · Traceability — how this register is kept true

```bash
cd /Users/bbhushan/work/git/workspace/warehouse-issues
python3 tools/check-design-set.py | tail -1
# -> 0 violations across 12 checks
```

- **check-7 (`finding-citations`) needs no exemption for `RA-`…`RF-`.** `FINDING_CITE_RE` is
  `\b[CTEFSPGQHUYZKOJ]-\d{1,3}[a-z]?\b`, and the leading `R` in `RA-001`…`RF-010` removes the word
  boundary, so none of the six new registers is read as a round-1 or round-2 id — `RC-001` cannot be
  mistaken for `C-001` for exactly the reason `O-001` cannot be mistaken for `OD-1`. The round-1 and
  round-2 ids this register **does** cite (`C-044`, `Q-003`, `Q-005`, `U-003`, `Y-`, `Z-`, `K-002`,
  `O-`, `H-002`, `X-004`, `X-032`) are real findings in their owning reviews and resolve normally.
- **check-5 (`issue-citations`) needs no exemption**, because this file contains no bare `#NN` issue
  reference. §4.3's `#12–#154` appears only inside a quotation of `issues/CREATED.md`'s own preamble
  about the PR-number gap; if a future edit adds a real cross-reference, it must resolve to
  `issues/CREATED.md` or carry an `issue-citations` declaration.
- **check-12 (`screen-citations`) does need one**, and it is declared at the top of this file in the
  house idiom: **`WS-238`** is the `BUILD-SPEC-SCREENS.md` §1 next-free allocation marker, and §4.4
  exists precisely because three findings propose taking it. By definition it has no index row yet.
  This is the same declaration `GAP-REGISTER.md`, `GAP-REGISTER-R2.md`, `DESIGN-SET-DEFECTS.md`,
  `docs/reviews/R9`, `R10`, `R16`, `R18`, `issues/README.md` and `issues/p5-13.md` already carry.
- **The check-13 that `DESIGN-SET-DEFECTS.md` §5 asks for now has a third clause.** Its rule was
  *"every finding in `reviews/R1`–`R7` has a disposition row in `GAP-REGISTER.md` §2.5"*, extended by
  round 2 to *"every finding in `reviews/R8`–`R15` has a disposition row in `GAP-REGISTER-R2.md` §2.1"*.
  It must now also assert *"every finding in `reviews/R16`–`R21` has a disposition row in
  `GAP-REGISTER-R3.md` §2.1–§2.6"*. This register's §2 was generated from the lens headings, so it is
  complete by construction today; check-13 is what keeps it complete tomorrow.

## §8 · The honest readiness statement

1. **The task set is still right, and it is now the third round to say so.** 52 findings, **zero** new
   task files, ten header amendments, 39 body edits and three decisions. That is a **days** problem for
   an author and a **weeks** problem only where a person must decide first.
2. **Eleven of the sixteen BLOCKERs are gated at or before `V500030`.** `PNR-1` and `PNR-2` are the same
   file, and five of those eleven are seed content of migrations that run before it (`V500012`,
   `V500013`, `V500015`, `V500019`, `V500021`). None of them is expensive today and none of them is
   recoverable by a later migration, because the recovery would be an `UPDATE`.
3. **A fresh install cannot post its first movement** (`RE-001`), and **the v1 costing acceptance box
   cannot be passed by any implementation** (`RF-001`). Those two are the sharpest answers round 3 has
   to the product owner's actual question — *will we say we should have thought of this earlier?* — and
   both are invisible until the first demo and the first backdated receipt respectively.
4. **One round-1 fact is wrong and has propagated into a requirement** (`RB-001`). It cost six invented
   filter keys, a mobile design divergence written down as deliberate, and four acceptance criteria that
   will be signed off as met. The lesson is narrow and repeatable: **a claim about the live tree has a
   shelf life, and `C-044`'s expired.**
5. **`OD-1` has now grown in two consecutive rounds without a reciprocal commitment being obtained.**
   Round 2 added the third install state and the Mode C invariant; round 3 adds four value columns. It
   is still free, and it is free in a repository this programme does not own.

**The shortest true statement.** Round 2 said the set was closer to buildable than any comparable design
set in this programme and not buildable that day. Round 3 does not move that verdict — it moves the
*reason*. The blocking work is no longer *"the columns are not specified"*; it is **eleven seed rows,
one job, one table, one screen and six decisions, all before `V500030`**. Take the six decisions in §5,
land the nine gates in §3.1 in migration order, and the *"we should have thought of this earlier"*
surface that six new lenses could find is closed.
