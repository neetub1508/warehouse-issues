TITLE: [Warehouse] EPIC: P4 — India statutory & compliance
LABELS: epic,warehouse,phase-p4
issue: 8
---
Part of __MASTER__ · Modules `warehouse-india` (wave 2) · `warehouse` · `warehouse-base` · one table in the `warehouse-3pl` band · Migrations — **7 blocks, enumerated below** · Ships in **v2**

## Overview

**Everything that reads history and files it.** P4 is the second `warehouse-india` wave: the
relational tax engine with its known defects fixed as blockers, job work and ITC-04, the **Rule 56
statutory stock account**, ITC reversal reaching back to the receipt that brought the lot in and
scrap sale as a supply, MRP as a balance dimension, goods on approval with the deemed-supply clock,
bonded and MOOWR warehousing, EPR reporting, the two retention clocks, the compliance task and rules
engine, the tax-basis inventory value, and the e-way bill wave-2 lifecycle.

**Twelve tasks.** `IMPLEMENTATION-PLAN.md` §9.3 sizes them 0 XL · 3 L · 6 M · 3 S and says the thing
worth repeating: *reporting and filing over data that already exists; **the hard part is domain
correctness, not code***. §9.4 asks for 2 backend, 2 frontend, 0 mobile and **1–2 QA with Indian
statutory knowledge**.

## P4 is registers and filings only — `A-4` already moved the documents into v1

`DECISIONS.md` §5.1 amendment **A-4** split `warehouse-india` into two waves, and **the movement
documents are v1/P2-IN, not here**: the delivery challan, the e-way bill payload and generation, the
GST-aware transfer document, HSN on the item, and the cross-GSTIN transfer treated as a supply. In
India goods physically cannot move between branches without them, so a v1 that shipped transfers and
no challan would have shipped a feature an Indian customer may not legally use.

**Do not rebuild what P2-IN owns.** Concretely, and this is the single most expensive mistake
available in this phase:

- **There is one challan table** (`FR-313`, `WH-SC-207`). Warehouse's delivery challan **is** the
  challan, with its own per-branch series from `whb_number_series`. `P4-02` (job work) and `P4-06`
  (approval) are **challan purposes on it**, not new documents.
- **The deemed-supply clock columns already exist** on `whin_delivery_challan_lines` —
  `expected_return_date`, `deemed_supply_due_date`, `quantity_returned`, `closed_at`,
  `job_work_type`. P4 **ages** them; it does not add them. *A movement recorded before the challan
  object existed can never acquire one*, which is exactly why the challan is v1 and the return is v2.
- **The compliance provider abstraction is v1** (`FR-326`, `P-044`): provider, per-provider
  environment, credential spec, encrypted credentials, auth session, document, task queue. P4's
  e-invoicing and wave-2 e-way work goes **through it**.
- **The reason code's `itc_treatment` and `statutory_category` are v1/P0 columns** (`FR-315`,
  `WH-SC-215`). They are why `P4-03` and `P4-04` are possible at all — *a year of free-text reasons
  cannot be reclassified*, and that year is the one the first audit covers.
- **`duty_status` has been in the position key and on every movement line since v1** (`FR-104`,
  `V500030`). It is why `P4-07` can exist — *bonded and duty-paid stock of one SKU commingled is a
  customs offence, not a data-quality issue.*

## What P4 deliberately does not do

**It does not compute tax** (`OD-9`) and **it does not issue an invoice or a credit note** — those
are accounting's. It does not build the six conditional `whin_` tables a warehouse-side tax engine
would need **unless `OD-9` resolves the other way**, which is what makes the India pack **50 tables
or 56**.

## The invariants this phase establishes

This phase **establishes no new `L-n`** — `P0` and `P1` did that. What it does is put existing
invariants under **new writers**, and a new writer is exactly how an invariant is lost. Each row names
the invariant, the new writer, and the specific way this phase could break it (`H-008`).

| # | Invariant | The new writer P4 introduces | How this phase breaks it if unwatched |
|---|---|---|---|
| **L-13** | **Three timestamps, never one:** `occurred_at`, `recorded_at`, `posting_date` | the **statutory registers and filings**, which are the first readers that must choose *one* of the three | a register that sums on `recorded_at` puts a late-entered movement in the wrong return period, and an amended return is a regulator-visible defect. Every P4 register states which timestamp it periodises on, in its task file, before the query is written |
| **L-7** | **Quantity in base UoM with the conversion factor frozen on the line** | the **HSN-wise and quantity-wise statutory summaries**, which report in statutory UoM, not base | re-deriving the statutory quantity from today's conversion factor **silently restates a filed period**. The register reads the factor frozen on the line, exactly as the ledger does |
| **L-12** | **Traceability is reconstructible in both directions**, for the full retention period | the **compliance document archive** and the API-log trail | a filing whose supporting movements have aged out of a partition is not defensible in an assessment. P4's retention floor is a **statutory** number, and it is the longer of the two — `P6-01`'s archive job reads it, never overrides it |

## Exit criterion

`DECISIONS.md` §5's v2 half is *"a 3PL bills a client for a month of storage and handling from
metered events, **and** a customer files ITC-04 and the Rule 56 stock account from warehouse data."*
`SCENARIO-CATALOGUE.md` §5 item 5 resolves it to three ids, of which **P4 owns two**:

> **`WH-SC-239`** — goods to job worker `JW-0044` under a challan dated 2026-08-12, owner unchanged,
> expected return 2026-11-10, the clock running **from the challan date**; the ageing job runs on
> 2026-10-27 and the customer **files ITC-04** for the quarter from warehouse data.
>
> **`WH-SC-240`** — a registration's quarter of movements, with reason codes carrying statutory
> categories, filed as the **Rule 56 statutory stock account** in the mandated categories, reconciling
> to the movement register.

`WH-SC-234` (the 3PL billing run) is **P5's** half.

**And one addition this programme makes so the criterion is falsifiable** (`IMPLEMENTATION-PLAN.md`
§1.6): the same closed period **reproduces identical figures a quarter later**. *A statutory register
that moves after filing is worse than no register.*

## Every statutory threshold in this phase — value at cutoff, and **RE-VERIFY before build**

Knowledge cutoff is **May 2026**. Indian indirect-tax thresholds move by notification several times a
year and at least one row below is probably already stale. Consolidated from
`INDIA-LOCALISATION-PACK.md`'s threshold register; each task repeats only the rows it uses.

| Rule | Value at cutoff | Used by |
|---|---|---|
| E-way bill consignment value, **inter-state** | ₹50,000 | `P4-12` |
| E-way bill threshold, **intra-state** | **state by state**; several states ₹1 lakh; some exempt intra-city | `P4-12` |
| E-way bill required **irrespective of value** | inter-state movement to a job worker; handicraft goods | `P4-02`, `P4-12` |
| E-way bill validity, regular cargo | 1 day per **200 km** from first Part-B entry — **has already changed once (100→200)** | `P4-12` |
| E-way bill validity, over-dimensional cargo | 1 day per 20 km | `P4-12` |
| E-way bill cancellation window | 24 hours, if the goods were not transported | `P4-12` |
| E-way bill generation blocked | GSTIN with two consecutive periods unfiled | `P4-12` |
| E-invoice applicability | aggregate turnover above ₹5 crore, B2B / export / CDN | `P4-01` |
| E-invoice reporting window | 30 days from document date, above ₹10 crore turnover (from 2025) | `P4-01` |
| HSN reporting digits | 4 / 6 / 8, by turnover | `P4-01` |
| Job-work return window | 1 year inputs, 3 years capital goods | `P4-02` |
| ITC-04 periodicity | turnover-dependent, half-yearly / annually around a ₹5 crore line | `P4-02` |
| Goods on approval — deemed supply | 6 months | `P4-06` |
| GST records retention | 72 months from the annual-return due date | `P4-03`, `P4-09` |
| Companies Act books retention | 8 financial years | `P4-09` |
| Food records retention | 1 year or the shelf life, whichever is longer | `P4-09` |
| TCS on scrap | 1 % | `P4-04` |
| Warehousing bond amount | commonly 3× the duty | `P4-07` |
| Bonded warehousing period | 1 year general goods, extendable; interest after 90 days for some categories | `P4-07` |
| Warehousing services SAC | `996729`, 18 % — **and the place-of-supply rule changed in 2023; do not state it from memory** | `P4-10` |

**Every one is `RE-VERIFY`.** Every value appears in its migration's header comment with the marker.

**Citation discipline, non-negotiable.** *No invented legal citation.* Where the rule is known and
the section number is not, the rule is stated and the citation is marked **`UNVERIFIED`**. **A
confidently wrong section number in a design document becomes a confidently wrong comment in a
migration and then a confidently wrong answer to an auditor.** The instruments named across P4 —
CGST Act s.35/s.36 with Rules r.56 · CGST Rules r.28, r.55, r.138 · CGST Act s.143 with Rules r.45 ·
CGST s.17(5)(h) · Income-tax s.206C(1) and s.44AB with Form 3CD · Companies Act 2013 s.128(5) and
s.148 · Customs Act 1962 Chapter IX ss.57–73, the Warehouse (Custody and Handling of Goods)
Regulations 2016 and MOOWR 2019 s.65 · Legal Metrology Act 2009 and the Packaged Commodities Rules
2011 · Battery Waste, E-Waste and Plastic Waste Management Rules · DPDP Act 2023 — carry
**`UNVERIFIED`** section numbers, and each task repeats that where it uses one.

## Migration blocks

**7 blocks**, re-derived from the `Migrations` field of every P4 task header — not transcribed from
an earlier table. That glob is the authority; **re-run it after any header change**:

```bash
for f in issues/p4-*.md; do
  printf "%s  " "$(basename "$f" .md)"
  grep -m1 '^Part of ' "$f" | sed 's/.*· Migrations \*\*//; s/\*\* · Screens.*//; s/\*\*//g'
done
```

- `V540100`–`V540101` — `P4-12` e-way bill wave 2: vehicle updates, cancellations, extensions;
  consolidated bills and their items
- `V540110`–`V540111` — `P4-01` GST state codes, HSN and SAC masters; the six-table relational tax
  rule engine
- `V540120`–`V540180` — `P4-02` job work and ITC-04 (`V540120`) · `P4-03` Rule 56 stock account
  (`V540130`) · `P4-04` ITC reversals (`V540131`) · `P4-07` bonded licences, bonds, utilisations,
  ex-bond clearances (`V540140`) · `P4-06` approval dispatches and clocks (`V540150`) · `P4-08` EPR
  categories, returns and lines (`V540160`) · `P4-09` retention policies (`V540170`) · `P4-10`
  compliance tasks, rules and rule conditions (`V540180`)
- `V540182` — `P4-13` the regulated-goods licence pack: licence types, entity and counterparty
  licences, quantity ceilings, the Schedule H1 register, recall notifications (`FR-456` `FR-457`).
  **Gated on a product decision — see the task file** (`S-035`, unanswered through two review rounds)
- `V541100`–`V541149` — `P4-01` permissions, `permission_dependencies`, menus, grid configuration and
  filter scopes for the whole wave (`V541150`–`V541199` left free)
- **`V530060`** ⚠ — `P4-10` `wh3_client_gst_registrations`, **in the 3PL band**
- **no migration** — `P4-05` (MRP report over v1 lot columns) · `P4-11` (tax-basis value)

**The one crossing, stated rather than silently taken** (`IMPLEMENTATION-PLAN.md` §2.9 row 6):
`W3-13`'s `V530060` sits in the **3PL** band because the band follows the table's `wh3_` prefix,
while `FR-301`'s phase is **P4** so the task follows the requirement's phase. Both rules are obeyed.
**It makes `P4-10 → P5-01` the only edge between the two v2 phases**, which otherwise run entirely in
parallel (§3.6).

**`V541100`–`V541149` is a sub-allocation of `WIN-30`** (§2.9 row 3): `P2-IN-01` took
`V541000`–`V541049` for wave 1, this wave takes `V541100`–`V541149`, and `V541050`–`V541099` plus
`V541150`–`V541199` are left free.

## Build order

`IMPLEMENTATION-PLAN.md` §3.8 graphs this phase; this is the same information as a schedule. **`A → B`
means A precedes B.**

- **First task: `P4-01` (GST reference masters and the tax engine).** Six P4 tasks write against it and
  none of them can be started honestly before it — a register built on a guessed rate table is a
  filing built on a guessed rate table.
- **Long pole: `P4-04` (ITC reversal reaching back to the receipt that brought the lot in).** It is the
  only P4 task that needs both the tax engine *and* the statutory stock account, and the reach-back is
  a ledger query over a period that may already be archived — which is why `P4-09`'s retention clocks
  sit beside it and not after it.
- **`P4-10` runs last on the 3PL leg, not first on the India leg.** It writes
  `wh3_client_gst_registrations` **in the 3PL band** (`V530060`, §2.9 divergence 6), so it needs
  `wh3_clients` from `P5-01`. **`P4-10` waits on `P5-01`** — the one edge between the two v2 phases, and
  its direction is the opposite of the one the task numbers suggest.
- **Parallel streams**, once `P4-01` lands: `{P4-03 → P4-04}` the statutory core · `{P4-02, P4-12}` job
  work and e-way bill wave 2 · `{P4-06, P4-07}` approval sales and bonded/MOOWR · `{P4-08, P4-13}`
  EPR and the regulated-goods licence pack · `{P4-05, P4-11}` MRP and the tax-basis value.
- **⚠ `P4-05` carries a deadline this phase does not own.** `OD-10` decides whether MRP is a
  **position-key dimension**; a position key is `L-5` and is decided **before `V500030`**, in P0. If the
  answer is yes and it arrives late, the column cannot be added — if it is no, `P4-05` carries a second
  balance model for the life of the product. **This is the tightest open deadline in the programme.**

## Tasks

__TASKS__

**Order.** `P4-01` first — the reference masters and the config block gate everything.
Then `P4-02 → P4-03 → {P4-04, P4-08, P4-09}` and `P4-01 → {P4-07, P4-12}`; `P4-06` follows `P4-02`
because it reuses the same ageing machinery; `P4-05` needs only `P1-03` and `P2-20`; `P4-11` needs
`P2-16`. **`P4-10` waits on `P5-01`.**

## Traps

- **`OD-9` is open and it decides whether six tables exist.** *Does `warehouse` carry a tax engine, or
  never compute tax?* `FR-325` has it carrying one; `FR-294` and R3 `D4` say it never computes tax.
  The India pack is **50 tables or 56**. `INDIA-LOCALISATION-PACK.md` §11.4 recommends the `OD-1`
  three-install-state shape and **deliberately refuses to number a new `OD-`**, because inventing one
  there is how two things end up sharing an id.
- **No `whb_` or `wh_` table gains a foreign key to a `whin_` table, in either direction** (`D-11`).
  Cross-module references are stable string keys or external-ref rows. `warehouse-india` also **may
  not add a column to a base table** or widen a base vocabulary by `ALTER` — it inserts rows.
- **The item stores its tax classification code as a string, never an FK into the HSN master**
  (`FR-066`), and it is **snapshotted on every movement and document line** (`FR-318`) so a
  reclassification does not rewrite a filed return.
- **Statutory registers are computed from movements, never from balances** (`FR-328`, `E-053`). A
  balance table answers *now*; every register here asks *"as at a date in the past, recomputed
  including entries made since"*. Period rows are a **cache** under the same `L-4` discipline as
  positions.
- **A filed period is frozen.** Re-generating it a quarter later reproduces identical figures; a
  backdated movement into a filed period raises a **visible reconciliation exception**, never a
  silently changed number.
- **The relational tax engine's four known defects are blockers, not deferred items** (`P-043`,
  `FR-325`): the nondeterministic slab resolver (`T-H1`), missing
  `UNIQUE(tax_rule_id, tax_component_id)` (`T-H2`), overlapping effective-date ranges (`T-H3`), and
  seed guards that can never fire because `rule_code` is `NULL` and **NULLs never collide** (`T-M11`).
  *A tax engine with a nondeterministic resolver is worse than none, because it is confidently wrong.*
- **Two prior security findings are constraints, not features** (`P-044`, `FR-326`): compliance
  request and response bodies are **never stored unencrypted** — the prior log table was *designed* to
  store raw bodies including auth calls carrying client secrets and NIC passwords, and had no index
  on `created_at` so any retention purge is a full scan — and **no demo or test controller may trigger
  a real statutory filing**, which the prior `ComplianceDemoController` could, in production code.
- **No schema-only statutory flow.** Three of the prior stack's eighteen tables shipped with no
  repository and no service; IRN cancellation and EWB extension were stubs. Build it properly or
  leave the tables out.
- **Every statutory, expiry, manufacture and count date is a SQL `DATE` mapped to `LocalDate` with a
  `dateOnly` filter** (`FR-327`, `P-045`). The prior art typed licence dates as
  `TIMESTAMP WITH TIME ZONE` and *"expired today"* shifted across a day boundary. And
  `filterUtils.ts:49-56`: a `date` filter on a `DATE` column moves the "from" bound back a calendar
  day **for users east of UTC** — for an Indian statutory register that is every user, and a quarter
  starting 1 July silently including 30 June is a filed return that is wrong.
- **`FR-165` binds every clock in this phase** — job-work ageing, the approval deemed-supply clock,
  licence expiry, the warehousing clock, the e-way cancellation window, GST-registration expiry.
  *A threshold column with no scheduled job that reads it is a defect at the moment it is merged*, and
  every job needs its `whb_job_runs` row (WS-064).
- **Do not build a second number-series allocator.** `warehouse-india` registers series *kinds* and
  consumes the base allocator. The prior art built its own and shipped `scc_document_sequences` with
  no `updated_at` even though `next_value` mutates on every allocation.
- **Precision.** Money `DECIMAL(19,4)` · quantities `DECIMAL(18,4)` · per-unit figures
  `DECIMAL(19,6)` · **any `*_percent` or `*_ratio` `DECIMAL(9,6)`**. `DECIMAL(19,8)` is the
  **currency-conversion** type and nothing else, even where a column is named `..._rate`.
- **`warehouse` never writes an `acc_*` table** (`D-6`). An architecture test fails the build if any
  class under `ai.warehouse*` references an `acc_*` table or an `ai.accounting*` type. Warehouse hands
  over an envelope and carries `handover_id` + `posting_status` on its own movement.
- **The mobile answer for this whole module is one screen.** `screens/whinEwayBill` —
  **Fill Part-B and Update vehicle only**, because a driver whose vehicle changed at a transhipment
  point must update Part-B from the road. **Everything else is `none`, stated with its reason**
  (`BUILD-SPEC-SCREENS.md` §5): the rest of `warehouse-india` is a compliance desk. Silence would be a
  defect (`FR-218`, `D-13`); this is a decision.

## Open decisions that gate P4 tasks

- **`OD-9`** — tax engine or never compute tax. Gates **`P4-01`**'s `V540111`. Deadline was *before
  `P2-IN`* and has passed by the time P4 starts.
- **`OD-1`** — the reciprocal accounting edits (the third install state). Gates **`P4-11`**. It is an
  edit to a different repository's design set and is **that set's to make**.
- **`OD-10`** — MRP in the position key. Answered before `P0-02`; the recommendation is **No**, MRP on
  the lot, and **`P4-05` reads it from there**. If `P0-02` shipped it in the key against the
  recommendation, `P4-05` is a different report.

## Definition of done
Per __MASTER__ and `IMPLEMENTATION-PLAN.md` §10, with the four programme-specific additions, plus one
that is specific to this phase: **every threshold in a migration comment carries its value and a
`RE-VERIFY` marker, and no section number appears that has not been verified** — where the rule is
known and the citation is not, the citation is marked `UNVERIFIED`.
