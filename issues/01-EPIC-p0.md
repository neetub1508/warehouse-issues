TITLE: [Warehouse] EPIC: P0 — Ledger foundation
LABELS: epic,warehouse,phase-p0
issue: 3
---
Part of __MASTER__ · Modules `warehouse-base` + the CI-only `warehouse-adapter-example` · Migrations — **16 blocks, enumerated below** · Ships in **v1**

## Overview

**The stock ledger itself, and everything that must exist before its first row.** This suite has no
stock ledger today: `services`, `field-service`, `assets`, `insurance-360` and `submittals` contain
**zero** stock tables (`C-034`), `services.parts_used` is free `TEXT`, and the one quantity-based
inventory that does exist — `accessories` — is **not a ledger**:
`accessory_inventory_transactions` is a single-sided log written next to an in-place-mutated
`accessory_stock_levels` row, and **`StockReceiptService.java:373-411` moves the balance and writes
no movement at all**, so the balance is not derivable from the movements (`C-021`).

P0 delivers: the immutable, double-sided, append-only ledger at full grain; the fourteen open
catalogues; owners; companies and stock periods; the position cache and its rebuild proof; the
inbound movement port with its exact idempotency contract; reservations as an open-item ledger;
tasks; the outbox; the accounting-handover seam; the ledger's own audit trail; base permissions and
menus; and **the adapter contract as a build-time test rather than an intention**.

**What P0 deliberately does not do:** no receiving screen, no picking, no counting, no valuation
engine, no report beyond the movement register and the position enquiry, no India, no mobile
operator screen.

## Exit criterion — a **Mode F** install, `platform` + `warehouse-base` only

No application module, no vertical, no accounting. All six hold in one sitting:

1. An integration principal posts a two-line receipt through `POST /api/warehouse/movements` carrying
   **its own** `idempotency_key`; the lines sum to zero against a **virtual location**; the response
   carries the assigned gapless `sequence_no`.
2. The **same key with the same payload hash** returns `200` with the original movement and writes
   nothing; the same key with a **different** hash returns `409`.
3. `POST /movements/{id}/reverse` with a catalogue reason code produces the mirror, links it, and
   **refuses to reverse the reversal**. No endpoint anywhere offers an edit or a delete.
4. `GET /stock/as-at?at=…` reproduces a past balance **from the ledger**, and a full rebuild of
   `whb_stock_positions` reproduces **every row exactly**; the drift job reports zero findings.
5. A movement whose `effective_date` falls in a `CLOSED` period is refused **including a reversal**;
   a `SOFT_CLOSED` period admits it only with the override permission and **records the override**.
6. `WarehouseBaseCouplingTest` passes and CI builds `warehouse-adapter-example` green: no forbidden
   import, no FK out of `warehouse-base`, no `CHECK (x IN (…))` on any of the fourteen catalogues.

**Scenario coverage:** `WH-SC-001` … `WH-SC-043` (`SCENARIO-CATALOGUE.md` §3.1, one per `L-1`…`L-14`
plus the ledger-shape requirements) **plus `WH-SC-044`**.

## The invariants this phase establishes

Get these wrong and everything after is built on sand. **Each has a database guard *and* a service
guard; the service guard rejects first, in the transaction, with a field-level error, and the
database guard is the backstop for the paths the service does not own** — a migration, a support
script, a second writer, direct SQL. **A trigger firing in production is an incident, not a
validation.**

| # | Invariant | Enforced by |
|---|---|---|
| **L-1** | **Conservation.** Every movement's lines sum to zero in base UoM per (owner, item, lot, serial, duty status). A receipt or an issue balances against a **virtual location**, never against nothing | deferred constraint trigger + service pre-check · `I-1` |
| **L-2** | **Append-only.** Three layers: one writer service with **no update method**, a `to_jsonb`-diff trigger rejecting **`INSERT` into a posted movement as well as `UPDATE`/`DELETE`**, and no repository path | service + trigger + review · `I-2` |
| **L-3** | **Correction is reversal** — mirrored lines, a mandatory catalogue reason code, the original marked reversed, a single-set link. **"Edit" is never offered anywhere in the product** | service · `I-3` |
| **L-4** | **Positions are a cache.** A full rebuild reproduces every row **exactly**; a nightly job proves it and alerts on drift | rebuild job + `whb_position_drift_findings` · `I-7` |
| **L-5** | **Full-grain key.** `(company, owner, item, location, lot, serial, lpn, stock_status, duty_status)` — every column in v1 **even where its feature ships later** | unique index · `I-5` |
| **L-6** | **Negative available is refused; negative on-hand is a policy** per item × site | `CHECK` + service · `I-6` |
| **L-7** | **Quantity in base UoM with the conversion factor frozen on the line.** A ledger that re-derives from today's factor **silently restates last year** | `CHECK` + service + trigger · `I-8`, `I-9` |
| **L-8** | **Period-bound.** A movement into a locked period is refused, **including a reversal**. Soft close needs an approved, recorded override; hard close admits nothing | trigger with session-GUC gating · `I-10` |
| **L-9** | **Ingestion is idempotent.** `(source_system, idempotency_key)` unique; a repeat returns the original and posts nothing. **The key is never server-generated** | unique index + service · `I-11` |
| **L-10** | **Allocation is an open-item ledger**, never a counter — a holder quad and an `expires_at` per row | service + FK · `I-12` |
| **L-11** | **Ownership never changes silently.** A title transfer is an explicit movement type with its own reason code | catalogue + service · `I-14` |
| **L-12** | **Traceability is reconstructible in both directions**, for the full retention period | schema + report + test · `I-15` |
| **L-13** | **Three timestamps, never one:** `occurred_at`, `recorded_at`, `posting_date`. Collapsing them kills offline replay, degraded-mode catch-up, cut-off and EPCIS **simultaneously** | `NOT NULL` columns · `I-13` |
| **L-14** | **Non-own stock is never valued.** `owner_type != OWN` hands over for quantity and custody only | service + handover contract · `I-16` |

`I-18` — **no `CHECK (… IN (…))` on any of the fourteen registry columns** — is asserted by
`WarehouseBaseCouplingTest`, not by the database, because the point is that the database has no such
constraint.

## The four points of no return, and what P0 does about them

| Gate | The migration | What is lost |
|---|---|---|
| **PNR-1** | `V500030` (`P0-02`) | Every column on the ledger header or line must be in that `CREATE TABLE`. Miss one and the only way to compile is a nullable FK — which silently converts the grain from *enforced* to *hoped for* |
| **PNR-2** | **`V500030` — the same file** | After it, `UPDATE` is refused to every actor. **A column added later is `NULL` on every pre-existing row forever, with no backfill path, because the backfill is an `UPDATE`.** `PNR-1` and `PNR-2` are collapsed deliberately: *"the gap between them is the only window in which a column can be added and backfilled, and a window that exists will be used, quietly, by someone who does not know what it costs"* |
| **PNR-3** | **the first movement posted in any install** | Nothing breaks; truth is absent. A duration cannot be backfilled, so month-one dock-to-stock cannot be produced; occupancy on each past day cannot be reconstructed, so **ageing, days-on-hand, obsolescence and anniversary storage billing all begin on the day the job was switched on** |
| **PNR-4** | `V500015` (`P1-01`), `V500018` (`P1-07`), `V500031` (`P0-02`) | **Rows that merged under a narrower key cannot be un-merged.** `whb_stock_positions` is the exception — `L-4` makes it a cache, recoverable by dropping the index and rebuilding, **if and only if the ledger line already carries the column** |

**Twelve tasks must land in the database before `P0-02`** — six P0 (`P0-04`, `P0-05`, `P0-06`,
`P0-07`, `P0-17`, and `P0-01`'s bootstrap) and **six P1** (`P1-01`, `P1-02`, `P1-05`, `P1-07`,
`P1-08`, `P1-09`). Their **screens and services are P1 work and are not on this path; only their
`CREATE TABLE` migrations are.** `P0-02` is not the first warehouse migration; **it is roughly the
tenth.**

**Every `V5*` migration carries `IRREVERSIBLE.md` §3.6's four-question header comment**, and items 2,
3 and 4 of it are mechanically asserted by `WarehouseBaseCouplingTest`.

## Migration blocks

**19 blocks** (16 v1, and three v2 increments folded in on 2026-09-10), re-derived from the `Migrations` field of every P0 task header, not transcribed from
an earlier table:

```bash
# from the warehouse-issues repo root
grep -h '^Part of __P0__' issues/p0-*.md | sed 's/.*Migrations \*\*//; s/\*\*.*//'
```

That command is the authority; re-run it after any header change.

- `V500000` `V500200` — `P0-01` module bootstrap · the platform `CHECK` widening
- `V500001` `V500019` — `P0-07` companies · stock periods ★ *both before `V500030`*
- `V500002`–`V500004` — `P0-04` source systems, document types, movement types, reason codes ★
- `V500072` — `P0-04` **v2 increment**: `whb_reason_code_tax_treatments` (`RG-020`, folded from former `P5-24`)
- `V500005` `V500006` `V500008` `V500010` — `P0-05` stock statuses, condition codes, location types, item types, task types, dispositions, attribute keys ★
- `V500007` `V500044` — `P0-06` owner types and owners ★ · owner grants
- `V500073` — `P0-06` **v2 increment**: `whb_owner_companies` (`RG-013`, folded from former `P5-24`)
- `V500021` — `P0-17` cost-layer schema, DDL only ★
- **`V500030`–`V500032`, `V500036`, `V500037` — `P0-02` ★★ THE LEDGER · `PNR-1` + `PNR-2` in one file ★★** · positions · the period trigger · the base-UoM trigger · **`V500037`: `I-23`**, the `REGISTERED`-history guard (exclusion, deferred at-least-one, append-only once a movement stands in range). It reads the ledger, so it cannot sit in `P1-05`'s `V500012`; `I-22` rides `V500030` (`RG-001`, `D-14`)
- `V500033` — `P0-09` reservations, allocation strategies and rules
- `V500034` — `P0-10` tasks
- `V500040` — `P0-11` the outbox, subscriptions, deliveries and the cursor
- `V500074` — `P0-11` **v2 increment**: `whb_outbox_subscription_owners` (`RG-018`, folded from former `P5-24`)
- `V500041` — `P0-08` inbound messages, movement batches and results
- `V500042` — `P0-12` accounting handovers and GL posting rules
- `V500043` — `P0-13` audit events, change rows and job runs
- `V500045` — `P0-03` position snapshots and drift findings
- `V501000` `V501001` `V501010` `V501020`–`V501049` `V501100` — `P0-15` permissions, dependencies, menus, base grids wave 1, admin settings
- `V525000` `V525010` — `P0-14` the reference adapter

`P0-16` writes **no migration** — that is not a defect, it is a task whose product is written
decisions, a filed platform dependency and `INSTALL.md` (`RE-006`).

**Deliberate gap `V500022`–`V500029`:** eight numbers between the last prerequisite and the ledger,
*"so a forgotten prerequisite has somewhere to land **before** the point of no return."* Use it; do
not renumber.

## Tasks

__TASKS__

**Order:** `P0-01 → P0-04 → {P0-05, P0-06, P0-07, P0-17} → {P1-01, P1-02, P1-05, P1-07, P1-08,
P1-09 — migrations only} → P0-02 → P0-03 → {P0-08, P0-09} → {P0-10, P0-11, P0-12, P0-13} → P0-14 →
P0-15`. **P0-16** is documentation and a filed platform task, and runs in parallel from the start.

- **`P0-01` must be first** — it is the five-module wiring, and nothing compiles until it lands.
- **`P0-02` gates the entire programme**, and **twelve tasks gate `P0-02`**. Every other ordering
  question here is negotiable; that one is not.
- **`P0-04` before `P0-05` and `P0-06`** — the ledger-critical catalogues come first, and `OD-5` must
  be answered before `P0-04` writes the **first warehouse page**.
- **`P0-15` must not be left to the end.** A grid without its `grid_preferences` row and its
  `filterUtils` scope **looks built and is not usable**.
- **`P0-14` lands with the *first* adapter, not after the second** — its whole purpose is to find base
  gaps before the base ships.

## Traps this phase must not walk into

- **Both bands in the original brief are occupied.** `V900000`–`V909999` holds 135 dealer OEM-seed
  files; `V910000`–`V919999` holds 434 per-client files with versions **deliberately reused across
  five client directories** (`C-001`). And a collision does **not** fail loudly:
  `FlywayConfiguration.java:296-327` renumbers legacy history into those bands and then **`DELETE`s
  duplicate history rows** (`C-002`). `V500000`–`V549999` is verified empty (`C-003`).
- **Migrations are physically flattened into one directory at build time**
  (`Dockerfile.backend:140-181`), which is the mechanical reason a cross-module version collision is
  a **build failure, not a merge conflict** (`C-011`).
- **The frontend merge is last-write-wins across the whole `src/` tree**
  (`Dockerfile.frontend:80-177`) — every warehouse filename must be globally unique (`C-012`).
- **Three integration gates fail silently:** `ModuleImportSelector.java` (the JAR is on the classpath
  and nothing loads), `filterUtils.ts` (the filter UI appears to do nothing), `jest.config.js`
  (suites are written and never run).
- **`CREATE CONSTRAINT TRIGGER` has exactly one precedent in this repo**
  (`accounting-base/V600111:812-815`), and it records the two PostgreSQL rules: a constraint trigger
  must be **`AFTER`** and must be **`FOR EACH ROW`**. `V500030` should be the **first** migration run
  against a real Docker build.
- **`cascade = CascadeType.ALL` on a collection resurrects a repository-deleted child** — 105
  occurrences repo-wide (R1 §8 trap `T-1`). Never on ledger lines;
  `whb_stock_movements → whb_stock_movement_lines` is `ON DELETE RESTRICT`.
- **A JPA field initialiser beats the column DEFAULT** (`StockLevel.java:58-64`, trap `T-2`) — it
  bites `posting_status DEFAULT 'NOT_APPLICABLE'` directly.
- **Hibernate native-query timestamps come back as any of four types** and a `null` return is silent
  data loss (trap `T-4`). The ledger carries **three** timestamp columns.
- **`filter_definitions` is the table; `grid_filter_definitions` has never existed** and is named in
  six prior-art documents fourteen times (`P-006`). Inserting into it crash-loops the backend.
- **Do not register a `statistics.*` cache name for a filter-aware strip** — the repo records that
  exact mistake at `CacheConfiguration.java:190-196`.
- **Do not name anything `wms_*` or `scc_*`** (`P-014`), and **do not copy accounting's band nesting**
  (`C-004`).
- **No local toolchain.** Do not run `mvn`, `npm` or `tsc` to "verify"; this project builds only in
  Docker.

## Open decisions that gate P0

> # ⛔ `OD-10` IS THE TIGHTEST DEADLINE IN THE PROGRAMME
>
> **Is MRP a dimension of the stock position?** (`FR-321`.) It must be answered **before `P0-02`
> writes `V500030`** — the migration that sets the position unique key **and, in the same file, seals
> the ledger against `UPDATE` forever.** There is no later window. **Recommendation: No** — MRP
> belongs on the **lot** (`FR-320`), and `P4-05` reads it from there. **If this is wrong it is
> unrecoverable, so it must be answered, not assumed.**

| # | Decision | Blocks |
|---|---|---|
| **OD-10** | MRP in the position key? | **`P0-02` / `V500030`** |
| **OD-7** | **Precision.** Adopt accounting's resolved set **verbatim and by citation** (`accounting/docs/DATA-MODEL.md:2443-2453` §5.1): quantities `DECIMAL(18,4)` · money `DECIMAL(19,4)` · **per-unit** `DECIMAL(19,6)` · **percentages and ratios — any `*_percent`, `*_ratio` — `DECIMAL(9,6)`** · exchange rates `DECIMAL(19,8)`. **Two normative tie-breaks: `unit_*` beats `value`/`*_amount`; `*_percent` beats any reading of "rate".** Check against `currencies.default_decimal_places CHECK (<= 4)` (`V203:17`) | **`P0-02`**, `P0-17`, every numeric column in the ledger |
| **OD-11** | Do value-only movements conserve value? A landed-cost movement posts `quantity = 0` with a value. **The tighter of the two stated deadlines wins — before `P0-02`**, because a conservation invariant is a constraint on the table, not on the report. Recommendation: a `VALUE_OFFSET` virtual location (seeded by `P1-05`) and an `L-15` | **`P0-02`**, `P1-05` |
| **OD-1** | The **reciprocal accounting edits** — a **third install state** in the `accounting` design set. **That set's edit to make**, cheap now, expensive once `acc_valuation_entries` has rows | **`P0-02`**, `P0-12` |
| **OD-8** | How does an out-of-process consumer authenticate to the port? *The auth model shapes the endpoint.* Recommendation: a **platform service principal** — `PP-2`, and **the only item in this set platform must build for warehouse** | **`P0-08`** |
| **OD-5** | Does the frontend re-close the vocabularies the backend opens? R2 records this as **a documented recurring defect in this codebase**. Must be answered **before the first warehouse page**, which is `P0-04`'s own screens | **`P0-04`** |
| **⛔ unnumbered** | **The ledger's partition key — `occurred_at` or `posting_date`?** `FR-022` and `DATA-MODEL.md` `WHB-30` say `occurred_at`; `PLATFORM-DEPENDENCIES.md` `PD-D5` says `posting_date`. **Nothing resolves them and the conflict has no `OD-` id** — `OD-1`…`OD-11` are taken, so one must be added to `DECISIONS.md` §3 **before `P0-02` is written**. *"A partition key cannot be added to a populated table without a rewrite."* `L-13` says these are **different columns**, so the choice is real | **`P0-02`** |

> **No task in the "Blocks" column may be merged while its `OD-` row is open. For `P0-02` that is
> five open decisions, and it is the single reason `P0-02` is not the first task started.**

## Definition of done
Per __MASTER__.
