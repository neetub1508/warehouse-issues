TITLE: [Warehouse] EPIC: P2 — Outbound, counting, valuation, returns, printing, reports
LABELS: epic,warehouse,phase-p2
issue: 5
<!-- check-design-set: issue-citations file #2 — `#2` and `#9` are ordinals in prose, not issue references — *Refusal #2*, *Adapter #2 (services)*, *ship-blocker #2*, *logistics needs #1, #2, #3, #5, #6, #10* — and at COMPETITOR-BENCHMARK.md:70/:146 `#9` is the markdown in-page anchor `[§9](#9--where-the-audits-disagree)`. In this repository `#2` and `#9` are in fact the two **pull requests** opened while the backlog was being filed, so no issue row can ever exist for either: see issues/CREATED.md — declared in the front matter, above the `---`, so the declaration never enters the issue body and cannot drift against the filed issue -->
---
Part of __MASTER__ · Modules `warehouse` · `warehouse-base` · `warehouse-adapter-dealer` · `warehouse-adapter-services` · `platform` · Migrations — **12 blocks, enumerated below** · Ships in **v1**

## Overview

**The other half of the daily loop, and the numbers that prove it.** P0 built the ledger and P1 built
the masters and the inbound chain. P2 is where stock leaves, where it is counted, where it acquires a
defensible cost, where a return comes back, where a document gets printed, and where three reports
have to agree with each other and with a rebuild from the movements.

Adjustments with a value-based approval threshold · three-leg transfers through a per-transfer
in-transit location · holds as records · cycle and physical counting with a frozen book quantity ·
expiry as a state · allocation and discrete picking to a real staging location · ship confirm as the
single inventory-relief event · cartons and pack evidence · **basic returns and return-to-vendor
(`A-1`)** · **templated document and label printing including a ZPL path (`A-2`)** · replenishment
suggestions and demand history · **the costing engine, weighted average and FIFO on
`whb_cost_layers`** · landed cost and revaluation · the accounting handover and the stock-to-GL
reconciliation · opening stock and the go-live certificate · the report pack · and **both v1
adapters, because one adapter proves nothing about genericity**.

**Twenty-nine tasks** — the widest phase in the programme. Sized in `IMPLEMENTATION-PLAN.md` §9.3 as
**2 XL · 9 L · 13 M · 5 S**, with `P2-16` (costing) the XL that matters and `P2-14` (printing) the L
with no precedent at all. §9.4 puts it at 4–5 backend, 3–4 frontend, 2 QA, across **six streams**.

## Two amendments made this phase bigger than the ladder first said, and both were right

`DECISIONS.md` §5.1, taken 2026-09-01 after the first authoring wave:

- **`A-1` — returns move to v1.** R2, R3 and R4 all placed RMA at v1/v1.1. *"A stock product with no
  return path at v1 is not credible in any segment"* — and **a customer return that cannot be
  received is a stock movement the ledger simply loses.** Basic returns are `P2-12`; full reverse
  logistics stays v2/P5. `COMPETITOR-BENCHMARK.md` §4.1 called the returns row *"the most damaging
  line in the table and self-inflicted"* until `X-050`'s 2026-09-02 fix rewrote it to name only the
  v2 RMA programme; this phase is what closed it.
- **`A-2` — printing moves to v1.** R5 ranks it **ship-blocker #2**, and
  `grep -rli "zpl\|escpos\|dymo"` across all Java and TypeScript returns **0**. *A warehouse that
  cannot print a pick list, a GRN, a delivery document or a bin label cannot be operated, and loses
  to a spreadsheet and a Dymo.* The renderer and the job log are `P2-14`; **the print server, printer
  routing and device management stay v1.1/P3** — `A-2` splits it there deliberately.

## The one decision this phase is built on

> **`D-6`, rewritten: whichever system is authoritative for quantity is authoritative for cost.**
> Warehouse is the system of record for every movement, position, count, adjustment and physical
> truth at full grain — **and therefore for cost. Warehouse runs the costing engine and owns
> `whb_cost_layers`.** Accounting is always the system of record for **the ledger**: it receives
> **valued** movements through its source-document port and posts them, and it owns everything
> downstream.
>
> **Accounting does not re-cost what warehouse hands it. Warehouse never writes an `acc_*` table and
> never writes a journal.** It carries `handover_id` + **`posting_status`**
> (`NOT_APPLICABLE` · `PENDING` · `POSTED` · `REJECTED`) on its own movement, and **a rejected
> handover lands in a queue that has a name, an owner and an ageing clock** — never in a swallowed
> exception (`P2-18`, `P2-22`).
>
> Two reasons, and both are testable: only warehouse holds the grain the costing methods need —
> **FEFO and specific identification are not expressible at accounting's item × godown × batch ×
> serial grain** — and a **standalone** install (`D-7`) must produce an inventory valuation with **no
> accounting module present**. `FR-446` makes both falsifiers acceptance tests.
> **R5 `S-066` is overruled**, and `IRREVERSIBLE.md` §7.3 item 1 — which still records the cost-layer
> placement as *"could not resolve"* — is **stale**; `DATA-MODEL.md` §2.1 and §7.2 put
> `whb_cost_layers` in `warehouse-base` at `V500021`.

## Exit criterion — nineteen scenarios, in order, on one install, in one sitting

`DECISIONS.md` §5's v1 sentence, decomposed by `SCENARIO-CATALOGUE.md` §3.2 into
**`WH-SC-044` … `WH-SC-062`**, run **in order, on one Mode-A install** — platform +
`warehouse-base` + `warehouse`, **no vertical, no accounting** — **in one sitting.**
If any one fails, v1 has not shipped.

**The three that decide it are the last three:**

> **`WH-SC-060`** — the **stock movement register**, the **position report** and the **valuation
> report** reconcile **to each other, to the unit and to the paisa**: the register's
> `opening + in − out` per item equals the position report's closing, and the valuation report's
> closing value equals `Σ (closing quantity × layer cost)` from the same layers. **Each report footer
> states the reconciliation.**
>
> **`WH-SC-061`** — a **full rebuild from `whb_stock_movements` reproduces the position report
> exactly, row for row.** *Three reports that agree with each other are not evidence, because they
> could all read the same broken cache. Agreeing with a rebuild from the movements is.*
>
> **`WH-SC-062`** — the valuation is produced **with no accounting module installed**, because
> warehouse holds the grain (`D-6`). This is **falsifier 1** of the costing-authority rule; falsifier
> 2 is `WH-SC-141`.

**Plus the port proof:** `warehouse-adapter-dealer` **and** `warehouse-adapter-services` both post
through `POST /api/warehouse/movements` with **zero commits to `warehouse-base`** (`D-11`,
`FR-352`, `WH-SC-223`). The ratchet is a command:
`git log --oneline -- warehouse-base/ | wc -l` unchanged at the merge commit, in the PR description.

## Migration blocks

**13 blocks**, re-derived from the `Migrations` field of every P2 task header — not transcribed from
an earlier table. That glob is the authority; **re-run it after any header change**:

```bash
for f in issues/p2-*.md; do
  printf "%-9s " "$(basename "$f" .md)"
  grep -m1 '^Part of ' "$f" | sed 's/.*· Migrations \*\*//; s/\*\* · Screens.*//; s/\*\*//g'
done
```

- `V510019`–`V510020` — `P2-13` reconciliation cases · supplier returns. **In the inbound block by
  design** (`DATA-MODEL.md` §7.3 WH-10/WH-11); do not "tidy" them upward
- `V510030`, `V510032`–`V510035` — `P2-01` adjustments (with `wh_adjustment_approval_policies`, `RA-008`) and the insufficient-stock / blocked-move logs
  · `P2-03` hold types and holds · `P2-04` counting · `P2-06` reconciliation exceptions.
  **`V510031` in the middle of this block is `P1-17`'s transfer orders** and is not P2's
- `V510040`–`V510044` — `P2-08` demand orders · `P2-09` pick tasks · `P2-11` cartons ·
  `P2-10` shipments and carriers
- `V510050` — `P2-12` RMAs, return receipts, RTO consignments (`A-1`)
- `V510060` — `P2-14` print templates, versions, jobs (`A-2`)
- `V510070` — `P2-15` replenishment runs, suggestions, demand history
- `V510080` — `P2-17` landed cost documents and allocations (with the three split columns, `RF-003`), revaluations
- `V510090` — `P2-19` opening-stock batches, cut-over checklists
- `V500048` · `V510091` · `V511211` + `V511241` — `P2-21` the KPI catalogue `whb_metric_definitions` (base),
  `wh_metric_targets`, and its `WS-244` resource permissions (`RC-007`, round 3)
- `V510222` `V511180` `V511210` `V511240` — `P2-23` **v2 increment**: `wh_approval_levels`, its `WS-241` grid, its resource permissions and menu (`RK-008`, folded from former `P5-27`)
- `V501070`–`V501099` — `P2-29` `warehouse-base` grid configuration, wave 3
- `V511060`–`V511139` — `P2-29` `warehouse` grid configuration, wave 3
- `V511201`–`V511207` **and** `V511231`–`V511237` — the `WH-206` verb-permission pairs, one per task that
  ships a status transition (`RJ-005`, round 4): `P2-01` adjustments · `P2-02` transfers
  (`request` `approve` `reject` `report_variance` `cancel`, `RK-001`) · `P2-04` counts · `P2-10` shipments ·
  `P2-12` RMAs and return receipts · `P2-13` supplier returns · `P2-15` replenishment suggestions. The
  first number of each pair seeds the permissions, the second the dependency rows. `V511000`/`V511001`
  are released and are never edited for this (`IMPLEMENTATION-PLAN.md` §2.9 row 2a)
- `V520000`, `V520010`–`V520012`, `V520015`, `V520100`–`V520149` — `P2-25` dealer adapter (with `whad_price_levels` and `whad_item_prices` at `V520015`, `RA-002`) · `P2-24` fitments
- `V521000`, `V521010`–`V521012`, `V521100`–`V521149` — `P2-26` services adapter

**Eight tasks write no migration** — `P2-05`, `P2-07`, `P2-16`, `P2-18`, `P2-20`,
`P2-22`, `P2-27`, `P2-28` (`P2-21` left the list when round 3 gave it `V500048` and `V510091`). **That is not a defect**: it is service, frontend, job and report
work over DDL that `P0` and `P1` already shipped — most visibly `P2-16`, whose three tables are
`P0-17`'s `V500021` because `whb_stock_movement_lines.cost_layer_id` is a real FK and `V500021` must
precede `V500030`. *(`P2-02` left this list in round 4: its transfer verbs claim the `V511202`/`V511232`
pair. `P2-23` left it at the 2026-09-10 fold: it claims former `P5-27`'s four numbers as its v2 increment.)*

**One sub-allocation is stated rather than taken silently.** `P2-29` owns the two grid-config bands,
but `IMPLEMENTATION-PLAN.md` §3.6 also says config *"is scheduled with its screens, not after them"*
— so **each grid's own migration is authored by the task that creates its table, claiming one number
inside `V501070`–`V501099` or `V511060`–`V511139` and recording it in that task's header.**
`P2-29` owns the bands, the two rules, the streaming export path and the ratchets.

## Tasks

__TASKS__

**Order.** The critical path through this phase is
`P2-08 → P2-09 → P2-10 → P2-14 → P2-16 → P2-18 → P2-20 → P2-21`
(`IMPLEMENTATION-PLAN.md` §3.5), and three of those links are on the path rather than beside it for
stated reasons: **`P2-14` because printing is net-new infrastructure and `WH-SC-055` is an exit
scenario**; **`P2-16` because a report pack built before the costing engine reports a number nobody
can defend**; and **`P2-21` last because the v1 exit is a reconciliation, not a feature.**

Six streams run in parallel (§3.6): inbound `P1-12`→`P1-16` **‖** inventory control
`P2-01`→`P2-06`, both after `P0-03` · outbound `P2-08`→`P2-11` **‖** valuation `P2-16`→`P2-17`,
both after `P2-07`, **meeting at `P2-18`** · reports `P2-20` **‖** `P2-21` then `P2-27`, after
`P2-16` · adapters `P2-25` **‖** `P2-26` after `P0-14`, **and their independence *is* the genericity
proof** · India wave 1 alongside all of it.

**`P2-29` must not be left to the end.** *A grid without its `grid_preferences` row and its
`filterUtils` scope looks built and is not usable.*

## Traps

- **`grep -rli "zpl\|escpos\|dymo"` across all Java and TypeScript → 0.** There is **no label or
  document rendering anywhere in this codebase**. `PP-10` names it warehouse's own work, not
  platform's. `P2-14` is infrastructure, and `T-13` closes the easy escape: **there is no per-module
  npm manifest** — only `platform/frontend/package.json` exists, 38 dependencies — so a module
  **cannot add a frontend library**. Rendering is a backend concern.
- **`BaseExportService.DEFAULT_MAX_EXPORT_ROWS = 10_000`** (`platform/…/service/BaseExportService.java:48`)
  against a **100,000-row** warehouse target. **Raising the constant solves only the first of three
  problems** — the transaction is held open for the duration, and a per-cell style blows the 64k
  Excel cell-style limit **at scale, not in dev**. Add a **streaming** path in `warehouse-base`
  (`Stream<T>` with a fetch size, written straight to the output) rather than editing
  `BaseExportService`, and propose the platform extraction **separately** (`PP-6`, `PD-D3`).
- **Filter-aware statistics carry no cache name** (`FR-395`). `CacheConfiguration.java:190-196`
  records that exact mistake with its issue numbers (`neetub1508/classic#790`, `#791`): those names
  **cached nothing while reading as though they did**. **No v1 warehouse screen qualifies for a
  `statistics.*` name.** `dropdown.*` names must be registered — an unregistered name throws on the
  **first call**, not at startup (`:375-377`).
- **`OFFSET` depth is not survivable at 100M rows** (`PP-7`). v1's answer is an **enforced date-range
  filter** on the ledger-scale grids; keyset/seek is v1.1. A report that opens on "all time" times
  out on the first real install.
- **`accessories` is the worked counter-example for almost every task in this phase, and all of it is
  live code.** No stock ledger — `accessory_inventory_transactions` is a single-sided log beside an
  in-place-mutated balance, and `StockReceiptService.java:373-411` moves the balance and writes **no**
  transaction at all (`C-021`). Reservations schema-only — `quantity_reserved` read in 7 places,
  **written in 0** (`C-022`). Counts never post — `InventoryCountService.java:325-345` sets
  `status='POSTED'` and generates nothing (`C-023`). No concurrency control — no `@Version`, no
  `@Lock`, **no `CHECK (quantity_on_hand >= 0)`**, and a code comment naming the race it does not
  defend (`C-024`). Valuation is one moving average, its reversal *"subtracts the reversed receipt's
  own cost"* which is not the inverse of a weighted average, and the report reads **`last_cost`, not
  `average_cost`** (`C-027`, `StockReportQueryService.java:543`). **Copy the ideas, never the code**
  — none of it is extractable, being FK-bound to `accessory_products` (`V30130:34-36`).
- **`T-1` — `cascade = CascadeType.ALL` on a line collection resurrects a repository-deleted child**;
  105 occurrences repo-wide. On a posted document a `getLines().clear()` issues `DELETE`s that `I-2`
  rejects, so **the code works on drafts and fails in production**.
- **`T-4` — a native-query timestamp comes back as any of four types** — `OffsetDateTime`, `Instant`,
  `java.sql.Timestamp`, `LocalDateTime`. Returning `null` for an unhandled type is **silent data
  loss**: the cell renders blank over real data. Copy
  `platform/…/service/UserActivityLogQueryService.java:288-307`, **including its warning**.
- **`dateOnly` versus `date` is load-bearing, not cosmetic.** `filterUtils.ts:49-56`: `date` shifts to
  UTC day boundaries and *"moves the 'from' bound to the previous calendar day for users east of
  UTC"*. `FR-327` makes every statutory, expiry, manufacture and count date a SQL `DATE` — **those
  filters are `dateOnly`.** And the DB side is a **different registry**:
  `filter_definitions.filter_type` (`V229:13`) takes `text | select | date | number | boolean |
  multiselect`, so **a `dateOnly` scope entry pairs with a `date` row there**.
- **There is no `daterange` filter type** — eight only (`filterUtils.ts:30`). Every from→to is **two
  keys**, both in the allowlist, **and both forwarded by the API service** — an enumerating
  `getForManagement` silently drops unknown keys, which is the third filter surface people forget.
- **`filter_definitions` is the table; `grid_filter_definitions` does not exist** — 0 hits over all
  migrations — and an insert into that name **fails at Flyway and crash-loops the backend** (`CM-4`).
- **`grid_preferences.default_filters` AND `default_columns` must both be populated** as
  `'[…]'::jsonb`; `filter_definitions.default_visible = true` alone builds nothing (`V18:12`,
  `V229:50-51`). And **"NO JSONB" is overstated**: the repo's own ratchet freezes a baseline rather
  than banning it (`ArchitectureInvariantsTest.java:225-239`); the rule that holds is *no JSONB on new
  `wh_` business tables*.
- **`menus` has no unique constraint on `(name, parent_id, menu_level)`**, so `ON CONFLICT DO NOTHING`
  does not stop a duplicate on a Flyway retry. `WHERE NOT EXISTS`, per `assets/…/V60171:154-155`.
- **`permission_dependencies` is a PLATFORM table** (`V248:17-30`). Insert rows; **never
  `CREATE TABLE`**. Columns are `permission_id` and **`dependent_permission_id`**.
- **All module migrations are flattened into one directory at build time**
  (`Dockerfile.backend:140-181`) and **the frontend merges last-write-wins across the whole `src/`
  tree** (`Dockerfile.frontend:80-177`). Every migration number and every file name must be globally
  unique; `wh`-prefix everything.
- **Adapter packages are siblings** — `ai.warehouseadapterdealer`, never
  `ai.warehouse.adapter.dealer`. `@ComponentScan("ai.warehouse")` would load an adapter in installs
  where its vertical is not built (`D-1`) — the exact trap the accounting round-4 review corrected.
- **Controllers live in `ai.<module>.controller…`** or `UserActivityTrackingAspect` cannot see them
  (pointcut `:59`, module from package segment 2 at `:167-174`).
- **There is no decimal library on the frontend.** Every quantity, cost, weight and percentage is
  `BigDecimal` on the backend and a formatted string on the wire (`FR-031`).
- **`BaseExportService` does not expose `formatBoolean(Boolean)`** — that is on `BaseController`, so
  calling it from an export service is a **compile error**. Return the raw `Boolean`; the framework
  renders Yes/No on every path and nulls as blank (`T-17`). Do **not** write a `formatYesNo`.
- **Every threshold column ships with the scheduled job that reads it** (`FR-165`). This phase has
  four dated obligations — expiry, reservation expiry, the count schedule and the coexistence
  reconciliation — and *a dated obligation with no actor is a defect at the moment it is merged.*
- **Precision, and the two normative tie-breaks** (`OD-7`, `DATA-MODEL.md` §5.1): quantities
  `DECIMAL(18,4)` · extended money `DECIMAL(19,4)` · **per-unit `DECIMAL(19,6)` — `unit_*` beats
  `value` and `*_amount`** · **percentages and ratios `DECIMAL(9,6)` — `_percent` beats any reading
  of "rate"** · `DECIMAL(19,8)` is the **currency-conversion** type and, in the whole warehouse set,
  belongs to `whb_cost_layers.exchange_rate` **and nothing else**.

## Open decisions that gate P2 tasks

- **`OD-6`** — valuation-method scope in v1. Gates **`P2-16`**. *Weighted average + FIFO in v1, layers
  present, method per item category × site; standard cost v1.1; **LIFO never** (prohibited under
  Ind AS 2 / IAS 2).* Deadline: **before P2's valuation tasks**.
- **`OD-1`** — the reciprocal `accounting` edits: a **third install state**, *"a warehouse product is
  present and owns quantity"*. Gates **`P2-16`** and **`P2-18`**, and `P2-IN-03`'s one-challan rule
  reaches into it too. **It is a different repository's design set to change**, it is cheap while
  accounting P3 is unbuilt, and it is expensive once `acc_valuation_entries` has rows.
- **`OD-11`** — do value-only movements conserve value? Gates **`P2-17`** and **`P2-28`**, and its
  guard belongs to **`P0-02`'s `V500030`** — `IMPLEMENTATION-PLAN.md` §7: *"the tighter deadline wins
  — a conservation invariant is a constraint on the table, not on the report"*. Three sub-questions
  are open together: the invariant, the **name of the value-offset virtual location**, and whether
  `value_balance_rule` is a movement-type column or a fifteenth `L-` invariant.
- **`OD-5`** — does the frontend re-close the vocabularies the backend opens? Touches every catalogue
  dropdown in this phase and `mobile/src/schemas/common.schemas.ts`, which is a **third copy** of
  every vocabulary. Referred to the standards owner.
- **An unnumbered decision — `M3`, the union valuation report.** R3 says build it; R7 says do not and
  document the separation in the UI instead; `DECISIONS.md` settles neither. `COEXISTENCE.md` §8.2
  sets the deadline at *"before the `P2` reports task is written"* — **which is now** — and says it
  needs an `OD-` row. Gates **`P2-20`** and **`P2-27`**.

## What P2 deliberately does not do

**No waves** — v1 ships the **Release** action on the demand header and says so (`FR-187`).
**Discrete picking only**; batch is `P3-06` and cluster, zone, pick-and-pass, pick-to-carton and
put-wall are v2/v3. **No pack session as an operator flow** — cartons exist, the flow is `P3-07`.
**No print server, printer registry or routing rules** — the renderer and the job log are v1, the
server is `P3-08`, and `A-2` splits it there deliberately. **No carrier integration** beyond the
carrier, service and account masters. **No grading, no NDR, no COD, no RTO workflow** — only the RTO
**columns** (`FR-205`). **No computed best stocking level** — that is `P6-02`, v3, and
`IMPLEMENTATION-PLAN.md` §5.3 calls it *"the most commercially dangerous deferral in the plan"*, in
the one segment we are best positioned to win. Every one of these is **stated on the screen**, because
a screen that silently lacks a capability reads as unfinished and one that says so reads as scoped.

## Definition of done
Per __MASTER__ and `IMPLEMENTATION-PLAN.md` §10, with the four programme-specific additions: a
migration that only `RAISE NOTICE`s its checks is not verified · every `L-n` invariant has a database
guard **and** a service guard that rejects first with a field-level error, because **a trigger firing
in production is an incident, not a validation** · the loose-coupling ratchet runs in CI, not in a
reviewer's memory · **every threshold column ships with the scheduled job that reads it** (`FR-165`).
