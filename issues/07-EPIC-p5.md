TITLE: [Warehouse] EPIC: P5 — 3PL, channels and reverse logistics
LABELS: epic,warehouse,phase-p5
issue: 10
<!-- check-design-set: issue-citations file #791 — `#790` and `#791` are issues in **`neetub1508/classic`**, cited as `classic#790, #791` with the second elided in the ordinary English way. The first resolves; the elided continuation reads to the checker as a bare `#NN`. It is a cross-repo citation, never a warehouse issue — declared in the front matter, above the `---`, so the declaration never enters the issue body and cannot drift against the filed issue -->
---
Part of __MASTER__ · Modules `warehouse-3pl` (new) · `warehouse` · `warehouse-adapter-dealer` · `warehouse-adapter-services` · Migrations — **four blocks, enumerated below** · Ships in **v2**

## Overview

**23 tasks. Three products sharing one base, and two of them can be built in parallel by two teams.**
Round 4 filed five more P5 task files under `D-14` item 7 and, on 2026-09-10, folded each into its most
similar existing task (no duplicate tasks; `#157`–`#161` closed as duplicates): the trade-customer
portal into `P5-08` as its second persona, the print-template scopes into `P5-21`, and the rest into v1
hosts as **v2 increments built in this wave** — the v2 junctions into their parent-table owners
(`P0-04`, `P0-06`, `P0-11`, `P1-01`, `P1-02`, `P1-03`, `P1-05`, `P1-14`, `P2-04`), inter-company sale
and purchase into `P1-17`, value-banded approval levels into `P2-23`, registry translations into `P1-19`.

- **3PL** — clients as objects with contracts and onboarding templates, charge codes, versioned
  effective-dated rate cards, **the append-only reversible billable-event meter**, storage billing in four
  methods with the minimum-monthly true-up as a *visible metered event*, billing runs with a frozen
  approved state, accessorials, disputes, the AR handover envelope, freight billing modes, SLA
  definitions and measurements and breaches, the client portal as a **permission surface**, and row-level
  owner segregation **with a negative test per endpoint**.
- **Channels and carriers** — channel accounts and idempotent order import, publish rules as the oversell
  control, tracking events normalised **and** raw, rate shopping with the quote persisted, pincode
  serviceability, AWB pools claimed transactionally, NDR with a response clock, COD remittance
  reconciliation, RTO as an inbound stock stream.
- **Reverse logistics** — grading at receipt, obsolescence returns, the marketplace claim window, recall,
  cores, warranty scrap-and-hold, NRV write-down as a register, the COGS recognition policy.

**The whole phase stands on concessions already made in v1**, and none of them can be made now:
`owner_id NOT NULL` in the position key (`D-5`), `whb_lpns.received_at`, **outbox events at billable
granularity** (`PC-42`), `cost_basis` including `ZERO_BAILMENT`, owner-scoped access grants, and the
persisted daily storage snapshot whose start date is `PNR-3`. R4 §5.3 puts it plainly: `warehouse-3pl` is
*"a thin module standing on a wide base concession, and the concession is not optional, not deferrable
and not flaggable."*

## The invariants this phase establishes

This phase **establishes no new `L-n`** — `P0` and `P1` did that. What it does is put existing
invariants under **new writers**, and a new writer is exactly how an invariant is lost. Each row names
the invariant, the new writer, and the specific way this phase could break it (`H-008`).

| # | Invariant | The new writer P5 introduces | How this phase breaks it if unwatched |
|---|---|---|---|
| **L-14** | **Non-own stock is never valued.** `owner_type != OWN` hands over for quantity and custody only | **3PL billing** — the first subsystem whose whole purpose is to attach money to somebody else's stock | this is the invariant P5 is most likely to break, and it would look like a feature. Billing prices a **service** (storage, handling, accessorials) against a client, and posts to AR through `wh3_ar_handovers`. It never writes a valuation row against `owner_type != OWN`, and no billing run may be the reason a stock value appears |
| **L-10** | **Allocation is an open-item ledger** | **channel/marketplace order intake** and the returns-grading path | a marketplace connector that "reserves 40" against a channel rather than against a holder quad reintroduces the counter the invariant exists to forbid. Every channel reservation carries the same quad as a demand-order reservation |
| **L-11** | **Ownership never changes silently** | **returns grading, refurbishment and RTO/NDR**, where goods change hands as a side effect of a workflow | a graded unit that becomes ours, or a client's unsold stock that becomes ours at contract end, is an explicit title-transfer movement type with its own reason code — never an `UPDATE` of `owner_id` |

## Exit criterion — as scenario ids

**`WH-SC-234`** is **half the v2 exit criterion** (the other half, `WH-SC-239`/`WH-SC-240`, is `P4`'s):
*a 3PL bills a client for a month of storage and handling from metered events.*

`IMPLEMENTATION-PLAN.md` §1.7 adds **three clauses that make it a real test**, and all three are in this
phase's acceptance:

1. **The invoice arithmetic is reproducible from the meter** — re-rating the same period against the same
   card version returns the same total (`P5-03`, `WH-SC-234` · `WH-SC-236`).
2. **A client user in the portal cannot see another client's stock through any endpoint**, proved by a
   **negative test per endpoint** (`FR-300`; `P5-08`, `WH-SC-140` · `WH-SC-244`).
3. **A channel order imported twice on the same `(channel account, external order id)` produces one
   demand order** (`P5-09`).

The full walked set for the phase: **`WH-SC-032` · `WH-SC-135` · `WH-SC-137` · `WH-SC-140` ·
`WH-SC-200` · `WH-SC-233` · `WH-SC-234` · `WH-SC-235` · `WH-SC-236` · `WH-SC-237` · `WH-SC-238` ·
`WH-SC-244` · `WH-SC-296`** — **thirteen**, plus the scenarios thirteen tasks must author (below).

## ⚠ Twenty of this phase's requirements have no scenario, and that is a gate, not a footnote

<!-- check-design-set: scenario-citations begin WH-SC-306 — the SCENARIO-CATALOGUE.md §5 rule 3 allocation marker — the next free scenario id, which by definition has no row yet. Named here so a parallel task does not silently take it twice; it is never a citation of a scenario that exists -->

`SCENARIO-CATALOGUE.md` §4.2 lists them honestly: of 71 unproven requirements, **43 are v2**, and the bulk
of those are this phase's — the whole carrier/channel surface (`FR-198`, `FR-200`–`FR-204`, `FR-208`–`FR-210`),
returns (`FR-272`, `FR-276`–`FR-279`), 3PL (`FR-293`, `FR-295`, `FR-297`, `FR-298`, `FR-303`), valuation
(`FR-241`, `FR-243`), replenishment (`FR-254`, `FR-259`), execution (`FR-223`, `FR-226`, `FR-227`),
`FR-140`, `FR-181`, `FR-267`, `FR-338`, `FR-343`, `FR-445`.

`IMPLEMENTATION-PLAN.md` §10 requires that *"the `WH-SC-nnn` scenarios the task claims to close are
**walked in the running app**"* — so a task with none has nothing to walk. **Seventeen P5 tasks therefore
author their own scenarios as their first act** (`P5-05`, `P5-06`, `P5-07`, `P5-09`, `P5-10`, `P5-11`,
`P5-12`, `P5-13`, `P5-15`, `P5-16`, `P5-17`, `P5-18`, `P5-19`, `P5-20`, `P5-21`, `P5-22`, `P5-23`).
Round-2 correction (`H-007`): the word said *thirteen* while the list held fifteen ids, and the two
round-2 task files were missing from both. `P5-22` and `P5-23` are the sharper case — their
`## Scenarios closed` sections hold **unnumbered prose bullets** rather than no scenarios at all
(*"a key is issued, the plaintext is shown once, and a second read returns only `hasValue`"*;
*"a GRN short by four units raises a claim from the receipt screen, pre-filled from the receipt line"*).
Those bullets are real scenarios that were never allocated ids: the first act of each task is to
number them from the `WH-SC-306` marker and add the rows to `SCENARIO-CATALOGUE.md`, not to invent
new prose. `P5-14` is correctly absent — it closes catalogued scenarios only.

> **⚠ ID COLLISION IS THE OBVIOUS FAILURE.** New ids continue from **`WH-SC-306`**
> (`SCENARIO-CATALOGUE.md` §5 rule 3), and two parallel P5 tasks will both take 301.
> **The rule for this phase: claim your ids by merging them into `SCENARIO-CATALOGUE.md` in one commit
> BEFORE writing code.** The catalogue file is the allocation register; nothing else is.

<!-- check-design-set: scenario-citations end -->

## `A-3` — P5 builds screens over tables that already exist

`H-008` found that this epic cited none of the four ladder amendments, and that the one it most needs
reaches no phase epic at all. **`A-3` (`DECISIONS.md` §5.1) put the item-variant *schema* in v1 and
kept only the *screens* in v2** — so `P5-20`'s Style × Variant Matrix (`WS-033`) and `WS-032`'s Variant
Axes & Values are built **over `V500014`/`V500015`, which `P1-01` already shipped**. The failure this
paragraph exists to prevent is a P5 lead reading their own epic, finding no variant model, and
authoring a second one. `whb_items.style_item_id` and the axis/value tables are the model; the only
genuinely missing table in this area is `FR-445`'s ratio/assortment **pack template**, which is
`P5-20`'s own new table (`V500064`) and is recorded three sections down.

## Migration blocks — re-derived from the task headers, not transcribed

```bash
# from issues/ — the header line of every P5 task file
grep -h '^Part of' p5-*.md | sed 's/.*Migrations //; s/ · Screens.*//'
grep -h '^Part of' p5-*.md | grep -oE 'V5[0-9]{5}' | sort -u
```

| Band | Module | Numbers this phase claims | Owners |
|---|---|---|---|
| `V510000`–`V519999` | `warehouse` | `V510200`–`V510214` **+ `V510215`, `V510216`** · round 4: **`V510221`**, **`V510223`**, **`V511209` + `V511239`** | `P5-09` `V510200` `V510208` `V510209` · `P5-10` `V510201`–`V510202` · `P5-11` `V510203`–`V510205` · `P5-12` `V510206`–`V510207` · `P5-13` `V510210` **+ `V510215`** · `P5-14` `V510211` · `P5-16` `V510212` · `P5-17` `V510213`–`V510214` · **`P5-23` `V510216`** · **`P5-08` `V510221` + the pair `V511209`/`V511239`** (the trade persona, folded from former `P5-25`) · **`P5-21` `V510223`** (print-template scopes, folded from former `P5-24`). `V510221` and `V510223` are carved from the correction reserve and the pair is `WH-206`'s (`IMPLEMENTATION-PLAN.md` §2.9 rows 2a and 7). Round 4's other app claims left this phase at the fold: `V510220` is `P1-14`'s, and `V510222`, `V511180` and `V511210`/`V511240` are `P2-23`'s — v2 increments of v1 tasks, built in this wave |
| `V520000`–`V529999` | adapters | `V520014` · `V521013` | `P5-15` (dealer cores · services warranty holds) |
| `V530000`–`V539999` | `warehouse-3pl` | `V530000` · `V530010`–`V530011` · `V530020`–`V530021` · `V530030`–`V530031` · `V530040`–`V530044` · `V530050` · `V531000`–`V531099` | `P5-01` … `P5-07` |
| `V500064`–`V500199` | `warehouse-base` post-v1 DDL | `V500064` · `V500065` · **`V500066`** | `P5-20` ratio-pack templates · `P5-21` packaging balances · **`P5-22` API clients and keys** (`WHB-67`, not `WHB-66` — see `DATA-MODEL.md` §7), plus `whb_api_client_endpoints` and `whb_api_client_companies` (`RG-018`). The two numbers this row once called *"still to claim"* were claimed in round 1; the third is round 2's. Round 4's base numbers `V500069`–`V500077` are claimed by P0/P1 hosts as v1.1 or v2 increments since the 2026-09-10 fold, so no P5 header carries them |

**Not this phase's, and it is easy to assume otherwise:** **`V530060` (`W3-13`,
`wh3_client_gst_registrations`) belongs to `P4-10`** — a P4 task inside the 3PL band, because the band
follows the table's prefix and the task follows the requirement's phase (`IMPLEMENTATION-PLAN.md` §2.9
divergence 6). `P4-10` therefore depends on `P5-01`, and it is **the only P4→P5 dependency in the plan**.

**Exactly one task owns each number.** A task needing a second file takes the next number **inside its own
block**, never the next globally free one.

## Build order

`IMPLEMENTATION-PLAN.md` §3.8 graphs this phase; this is the same information as a schedule. **`A → B`
means A precedes B.**

- **First task: `P5-01`** — the module scaffold, the client object and the build-time ratchet. Every
  other P5 task and one P4 task (`P4-10`) hang off `wh3_clients`.
- **Long pole: the billing chain, `P5-02 → P5-03 → P5-04 → P5-05`.** `P5-05` is where the money
  freezes, and `P5-03` is where it is measured — an event vocabulary that cannot price per line cannot
  be repaired downstream.
- **⚠ The one edge drawn across four phases: `P0-11 → P5-03`.** `P5-03`'s **first act** is to verify
  `P0-11`'s event vocabulary. If `pick.line.confirmed` does not carry quantity, item and location, then
  per-line handling billing — how every audited 3PL prices — is **permanently unavailable for the
  past**, the defect is `P0-11`'s, and this phase stops until it is fixed.
- **Parallel streams**, once `P5-01` lands: `{P5-02 → P5-03 → P5-04 → P5-05}` billing · `{P5-06}` and
  `{P5-07}` freight and SLA, both joining at `P5-05` · `{P5-22 → P5-09 → P5-10, P5-11, P5-12}` the
  integration surface then channels, match, carriers and NDR/COD · `{P5-13, P5-14, P5-15}` reverse
  logistics · `{P5-16, P5-17}` NRV and weighing/labour · `{P5-18, P5-19, P5-20, P5-21, P5-23}`.
- **`P5-08` (the portal) is scheduled after `P5-05`, not beside it.** It is a permission surface over
  screens that must already exist, and the thing it exposes to a client is the billing run.
- **Round 4's P5 work is increments of existing tasks, not tasks** (folded 2026-09-10). The trade-customer
  persona is built inside `P5-08`, after its client persona; the print-template scopes inside `P5-21`.
  The v2 increments of v1 hosts (`P0-04`, `P0-06`, `P0-11`, `P1-01`, `P1-02`, `P1-03`, `P1-05`, `P1-14`,
  `P1-17`, `P1-19`, `P2-04`, `P2-23`) are scheduled into this wave's gaps. Schedule `P1-03`'s v2 increment
  before `P5-18` where possible: the site-scoped supplier preference is what sister-branch replenishment
  reads per site (`WH-SC-324`).

## Tasks

__TASKS__

**Sizing** (`IMPLEMENTATION-PLAN.md` §9.3): 1 XL · 6 L · 15 M · 6 S. **Staffing** (§9.4): 3–4 backend,
3 frontend, 1 mobile, 2 QA. *"Two independent sub-streams. Billing needs someone who has built billing
before."* §9.5 assumption 6: **P4 and P5 are two products** — they run fully concurrently with two teams
and one shared base reviewer, and cannot be compressed into one team without serialising v2.

## Four defects found in `IMPLEMENTATION-PLAN.md` §2.7 while authoring this phase

All four are recorded in `DEFECTS-FOUND.md` and fixed in the task files rather than carried silently.

1. **`FR-279` (the marketplace return-claim window) has no table and no screen.** `V510210` creates only
   the three grading/obsolescence tables (`DATA-MODEL.md` `WH-110`); `wh_return_receipts.claim_due_at`
   carries the clock alone; and all 237 screen ids in `BUILD-SPEC-SCREENS.md` §1 are claimed and none is
   this. **`P5-13` claims `V510215`** from §7.3's correction reserve and allocates a new screen id.
2. **`FR-445` (the ratio/assortment pack template) has no table.** The variant *axes* exist (`V500014`)
   and `whb_items.style_item_id` exists — the **pack template naming a quantity per variant** does not.
   **`P5-20` claims a number in §7.2's declared `V500064`–`V500199` post-v1 base gap.**
3. **`FR-343` (returnable packaging's per-counterparty balance) has no table**, and `G-024` marks it as
   *new* relative to `F-060`, which covers packaging as stock only. **`P5-21` claims a number in the same
   base gap.**
4. **`P5-01`'s `V531000`–`V531099` sub-allocates `W3-20`'s declared `V531000`–`V531199`**, and §2.9 —
   which enumerates every other sub-allocation and asserts *"Six"* — does not record it.

## Traps this phase must not get wrong

- **Every verb in a §4 Actions cell is a `@PreAuthorize`, not an `:edit`** (`H-001`). The strings are
  rows in `BUILD-SPEC-SCREENS.md` §10.2 — twenty-five were added in round 2 and are seeded by `P5-01`
  (`V531000`–`V531099`) — and **a screen whose verbs §3/§7 describes only in prose must enumerate them
  in the task before the controller is written.** The failure this prevents is already visible in the
  document: `wh3_billing_runs:approve` existed while `:cancel` did not, so anyone who could edit a
  draft run could cancel an invoiced one.

- **⚠ The meter's granularity reaches back into base and cannot be fixed here.** `PC-42`/`F-012`: *"a
  design that emits only `order.shipped` makes per-line handling billing — how every audited 3PL prices —
  permanently unavailable for the past."* **`P5-03`'s first act is to verify `P0-11`'s event vocabulary**;
  if `pick.line.confirmed` does not carry quantity, item and location, the defect is `P0-11`'s and this
  phase stops until it is fixed.
- **⚠ There is no outbox precedent anywhere in this repository.** `grep -rli "outbox"` → **0 files**
  (`PC-35`). If `P0-11` budgeted *"a table"*, the missing five items — gapless cursor, publisher job,
  retry with backoff, dead-letter grid, replay-from-cursor — surface in `P5-03`. `@Async` is not a
  substitute; `reference_async_notification_lazyinit` is a live trap in this repo.
- **⚠ `PNR-3` decides what is billable at all.** Storage billing, ageing, days-on-hand and obsolescence
  *"all begin on the day the [snapshot] job was switched on"*. A period before it **cannot be billed by
  any method**, and `P5-04` must refuse rather than return zero.
- **⚠ Owner segregation has four leak sites per grid, not one** — grid, **export**, **statistics map**,
  dropdown (`WH-SC-242`), plus the availability API and the lineage query. A `403`, **never an empty
  grid** (`WH-SC-140`): an empty grid reads as *"no stock"*, not as a boundary.
- **`warehouse-3pl` contains no invoice, no numbering sequence and no tax engine, in any version.**
  Asserted by the coupling test: *"a `wh3_` invoice table appearing in any migration fails the module's own
  coupling test"* (`WH-SC-238`).
- **Non-own stock is never valued** (`L-14`). *A 3PL that posts its clients' stock to its own balance
  sheet has a catastrophe in both directions.* The custody number is a **different number on a different
  report**, and the assertion is *the number is absent*, not *zero*.
- **`FOR UPDATE SKIP LOCKED` has zero precedent in this codebase** (R1 `C-040`). `P5-11`'s AWB pool and
  `P3-02`'s task claiming both need it — write and review it **once**.
- **Five objects in this phase will move to `logistics` in P6** (R7 §2.6): `wh_carriers` /
  `wh_carrier_services` / `wh_carrier_accounts`, `wh_shipment_tracking_events`, `wh_shipment_ndrs`,
  `wh_cod_remittances` — and `wh_rto_consignments` **never fully**, because the receipt stays.
  **All five are referenced by stable string code resolved through a service, never by an FK from the
  referencing table into the relocatable one.** *"Applying that rule to one object and not the other four
  is how the move stops being cheap"* (`G-013`).
- **The ratchet is "zero commits to `warehouse-base`", never "zero commits to `platform`"** (`D-10`
  corollary, `G-047`). This phase adds ~25 grids; every one edits `filterUtils.ts` (213 scopes, a missing
  field is **silently dropped**) and `CacheConfiguration.java` (234 names, an unregistered name throws on
  the **first call**, not at startup). Budget the merge contention (§9.5 assumption 2).
- **Filter-aware statistics get no cache name at all** — `CacheConfiguration.java:190-196` records that
  exact mistake (classic#790, #791; R1 `C-043`).
- **The table is `filter_definitions`** (`platform/…/V229:8`); **`grid_filter_definitions` does not exist**
  and inserting into it crash-loops the backend (R1 `CM-4`). `grid_preferences` needs **both**
  `default_columns` and `default_filters`.
- **Every warehouse frontend filename must be globally unique** — `Dockerfile.frontend:80-177` merges
  module `src/` last-write-wins (R1 `C-012`).

## Blocked on decisions

- **⛔ `OD-3`** blocks **`P5-01`** — *"before `warehouse-3pl` starts"*. One database per customer;
  a 3PL's clients are an **owner dimension, not tenants**. `grep -ril "tenant" platform/backend/src/main/java`
  → **0 files**. **Do not re-litigate.**
- **⛔ `OD-1`** reaches **`P5-16`** — the reciprocal accounting edits that let warehouse own cost while
  accounting owns the ledger (`D-6`). It is *a different repository's design set to amend*.
- **`OD-5`** (does the frontend re-close the vocabularies the backend opens) lands first in this phase at
  `P5-02`'s charge-code categories and `P5-13`'s condition grades.
- **`OD-9`** is already answered — **warehouse never computes tax** — and `P5-05` depends on it.
- **⛔ `OD-18`** blocks **`P5-09`'s drop-ship requirement `FR-467`** (round 4, `RK-005`) — *what v1
  records for a drop-shipment*, answered by the first drop-shipped purchase. The channel work in `P5-09`
  proceeds; the drop-ship movement type is **not** seeded in v1, and any module seeds it under `D-10` once
  the row is answered.

## Definition of done
Per __MASTER__ — including the four additions specific to this programme, of which two bite hardest here:
**every `L-n` invariant has a database guard *and* a service guard, and the service guard rejects first
with a field-level error**; and **every threshold column ships with the scheduled job that reads it**
(`P5-07`'s SLA windows, `P5-11`'s AWB low watermark, `P5-12`'s NDR clock and COD ageing, `P5-13`'s three
windows, `P5-15`'s two, `P5-17`'s certificate expiry). *A dated obligation with no actor is a defect at
the moment it is merged.*
