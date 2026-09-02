TITLE: [Warehouse] EPIC: P3 — Execution & mobile
LABELS: epic,warehouse,phase-p3
---
Part of __MASTER__ · Modules `mobile` · `warehouse` · `warehouse-base` · `warehouse-adapter-field-service` · `warehouse-adapter-assets` · `warehouse-adapter-dealer` · Migrations — **10 blocks, enumerated below** · Ships in **v1.1**

## Overview

**The warehouse floor.** v1 built a stock ledger and the screens that write to it. P3 is the phase
where an operator stops using a browser: the RF screen family with its own interaction contract and
its nine screens, task assignment as pull **and** push, the device registry, the offline queue, waves
and batch picking, the pack session, the print server, manifests and handovers, kits and work orders,
pick-face replenishment, order-edit rules, LPN move expansion and GS1 parsing, alert rules and health
signals, the migration workbench, and the field-service and assets adapters.

**Twenty-three tasks.** Sized in `IMPLEMENTATION-PLAN.md` §9.3 as 1 XL · 8 L · 9 M · 5 S, with
`P3-01` (the RF family) the XL and a long tail behind it. It is the **only** phase with a real mobile
load — 2–3 mobile engineers — and §9.6 says plainly that mobile is where the estimate is least
trustworthy.

## This is where `D-13` inverts

Every earlier phase applied *mobile is not optional* by building a web screen and mirroring it. In P3
the handheld **is** the product for nine screens, and the web grid is the supervisor's view of it.
`FR-220` is the load-bearing sentence: the RF screens are a **separate screen family** from
`EntityListScreen`, which is a list-plus-filters component built for office use and is the wrong base
for one-handed, gloved operation.

## The three things this codebase does not have, that P3 must build

Each verified by command against the live `classic` checkout on **2026-09-02**:

| | Command | Result | Who builds it |
|---|---|---|---|
| **No offline mutation queue in mobile** | `grep -rlE "persistQueryClient\|createAsyncStoragePersister\|offlineQueue" mobile/src \| wc -l` | **0** — `mobile/src/services/networkService.ts:124-125` detects the drop and nothing queues behind it | `P3-04` |
| **No `FOR UPDATE SKIP LOCKED` anywhere** | `grep -rn "SKIP LOCKED" --include=*.java --include=*.sql . \| wc -l` | **0** — zero precedent; it is **built and load-tested, not assumed** (`FR-425`) | `P3-02` |
| **No label or document rendering anywhere** | `grep -rliE "zpl\|escpos\|dymo" --include=*.java --include=*.ts --include=*.tsx . \| wc -l` | **0** — the renderer is `P2-14`'s (`A-2` moved it into v1); P3 adds the **print server** on top of it | `P3-08` |

## Exit criterion

`DECISIONS.md` §5, and `SCENARIO-CATALOGUE.md` §5 item 5 makes it two scenario ids and nothing else:

> **`WH-SC-227`** — an operator with a handheld and no desk completes a full
> **receive → putaway → move → pick → pack → ship** cycle **entirely on the handheld**. Every step is a
> mobile screen from the named family and **no step requires a browser**.
>
> **`WH-SC-228`** — a wave of **200 order lines across 6 zones** releases, picks and ships **with task
> interleaving**, and the wave generates in **under five seconds**.

Two additions this programme makes testable rather than aspirational: **scan-to-response is measured
at the handheld and is under 300 ms** (`FR-424`), and **task claiming uses `FOR UPDATE SKIP LOCKED`
and is load-tested** (`FR-425`).

## Migration blocks

**10 blocks**, re-derived from the `Migrations` field of every P3 task header — not transcribed from
an earlier table. That glob is the authority; **re-run it after any header change**:

```bash
for f in issues/p3-*.md; do
  printf "%s  " "$(basename "$f" .md)"
  grep -m1 '^Part of ' "$f" | sed 's/.*· Migrations \*\*//; s/\*\* · Screens.*//; s/\*\*//g'
done
```

- `V500060` — `P3-10` kits and kit components
- `V500061` — `P3-12` item × location settings
- `V500062` — `P3-03` devices
- `V500063` — `P3-16` alert rules, conditions, recipients, events
- `V501101`–`V501109` — `P3-04` base grid configuration, wave 4
- `V510012` — `P3-05` ASNs, ASN lines, ASN line serials
- `V510100`–`V510108` — `P3-06` waves · `P3-07` pack sessions · `P3-11` work orders and VAS service types · `P3-08` printers, routing rules, shipping labels · `P3-09` consignments, manifests, handovers, pickup requests · `P3-13` order-edit rules · `P3-17` KPI snapshots · `P3-18` migration mappings · `P3-12` replenishment tasks
- `V511140`–`V511179` — `P3-04` app grid configuration, wave 4 (`V511180`–`V511199` left free on purpose)
- `V520013` — `P3-18` OEM price files and lines
- `V522000`–`V522149` **and** `V523000`–`V523149` — `P3-20` field-service adapter · `P3-21` assets adapter

**Seven tasks write no migration** — `P3-01`, `P3-02`, `P3-14`, `P3-15`, `P3-19`, `P3-22`, `P3-23`.
That is not a defect: it is service, frontend and mobile work over DDL that v1 already shipped.

**Two sub-allocations are stated rather than taken silently** (`IMPLEMENTATION-PLAN.md` §2.9 rows 1
and 2): `V501101`–`V501109` comes out of `DATA-MODEL.md` §7.2's *"reserved for post-v1 base work"*,
and `V511140`–`V511179` sits inside `WH-203`'s `V511020`–`V511199`.

## Tasks

__TASKS__

**Order.** `P3-01 → P3-03 → P3-04` is the mobile spine and nothing else on a handheld is real until
it lands. `P3-02` gates `P3-06`, `P3-12` and `P3-14` — all three are tasks in a queue. `P3-10 → P3-11`.
`P3-20 ‖ P3-21` run in parallel after `P0-14` and their verticals' P2 dependencies
(`IMPLEMENTATION-PLAN.md` §3.6). `P3-22` is independent. **`P3-04` must not be left to the end** — a
grid without its `grid_preferences` row and its `filterUtils` scope looks built and is not usable.

## Traps

- **`EntityListScreen`/`ListHeader` supports `dropdown` and `text` filters and *not* dates.**
  `mobile/src/components/common/ListHeader.tsx:216` declares `type?: 'dropdown' | 'text'`; CLAUDE.md's
  *"only supports dropdowns"* is stale (R1 `CM-1`). **Every P3 screen whose default filter strip is
  date-driven ships the mobile equivalent as a dropdown of named periods**, and the task says so —
  `lastSeenBefore`, `dueWithinDays`, `expiringWithinDays` are all dropdowns for this reason.
- **Mobile API services are object literals**, not `BaseApiService` subclasses
  (`mobile/src/api/documentCategoryApi.ts:61`, `serviceJobApi.ts:31`, and ~200 siblings). Do not
  refactor them and do not import the web service.
- **`mobile/src/schemas/common.schemas.ts` is 5,852 lines and is a third copy of every dropdown
  vocabulary.** A catalogue value the backend opened and this file closed as a zod enum **fails the
  save with no message** (`FR-382`, `OD-5`, `WH-SC-147`). `P3-04` owns the sweep; every other task
  owns not creating a new one.
- **The idempotency key is client-generated and never server-generated** (`L-9`). It is the
  irreversible half of the offline design, it shipped as a v1 constraint, and it is what makes the
  queue buildable at all. A replayed scan without one puts a duplicate in an append-only ledger,
  fixable only by a reversal that looks like an adjustment.
- **`SKIP LOCKED` silently returns fewer rows than requested.** A claim that asks for 1 and gets 0
  means *all claimed*, not *queue empty*. Treating them as the same tells an operator there is no work
  while 40 tasks are open.
- **203 dpi against 300 dpi changes every barcode's width.** DPI is a column on the printer, passed
  to the renderer — never a template constant.
- **A reprinted SSCC is a duplicate licence plate in the wild.** Labels are **voided, never deleted**.
- **Filter-aware statistics carry no cache name** (`FR-395`). `CacheConfiguration.java:190-196`
  records that exact mistake with its issue numbers — those names cached nothing while reading as
  though they did. Every P3 statistics strip is filter-aware.
- **`filter_definitions` is the table; `grid_filter_definitions` does not exist.** An unguarded insert
  into that name fails at Flyway and **crash-loops the backend** (R1 `CM-4`).
- **`grid_preferences.default_filters` AND `default_columns` must both be populated** as
  `'[…]'::jsonb`; `filter_definitions.default_visible = true` alone does nothing (`V18:12`,
  `V229:50-51`).
- **There is no `daterange` filter type** — eight types only (`filterUtils.ts:30`). Every from→to
  filter is **two keys**, both in the allowlist, both accepted by `getForManagement`.
- **There is no decimal library on the frontend** — one `package.json`, 38 dependencies, no
  `decimal.js`/`big.js`. Every quantity, weight, cost and percentage is `BigDecimal` on the backend
  and a formatted string on the wire.
- **Adapters ship with zero commits to `warehouse-base`.** The ratchet is
  `git log --oneline -- warehouse-base/ | wc -l` unchanged at the merge commit, recorded in the PR
  description, plus `ArchitectureInvariantsTest` per module and `warehouse-adapter-example` built
  green in CI.
- **Adapter packages are siblings** — `ai.warehouseadapterfieldservice`, never
  `ai.warehouse.adapter.fieldservice`. `@ComponentScan("ai.warehouse")` would load an adapter in
  installs where its vertical is not built (`D-1`).
- **Controllers live in `ai.<module>.controller…`** or `UserActivityTrackingAspect` cannot see them
  (pointcut `:59`, module from package segment 2 at `:167-174`).
- **Menu inserts need `WHERE NOT EXISTS`** — `menus` has no unique constraint on
  `(name, parent_id, menu_level)` and `ON CONFLICT DO NOTHING` does not stop a duplicate on a Flyway
  retry (`assets/.../V60171:154-155`).
- **`permission_dependencies` is a PLATFORM table** (`V248:17-30`). Insert rows; **never
  `CREATE TABLE`**. Columns are `permission_id` and **`dependent_permission_id`**.
- **The frontend and mobile trees merge last-write-wins** (`Dockerfile.frontend:80-177`), and all
  module migrations are flattened into one directory at build time (`Dockerfile.backend:140-181`).
  Every file name and every migration number must be globally unique.

## Open decisions that gate P3 tasks

- **`OD-11`** — do value-only movements conserve value? Gates **`P3-11`**'s assembly-completion
  trigger, which is the second call site of the proposed `L-15` after landed cost. Deadline in
  `IMPLEMENTATION-PLAN.md` §7 is *before `P0-02`*.
- **`OD-8`** — how an out-of-process consumer authenticates to the port. Gates **`P3-22`**'s HTTP
  subscription. The recommendation is a **platform service principal**, and it is the **only** item in
  this design set that platform must build for warehouse.

## What P3 deliberately does not do

No voice picking. No automation control. **No engineered labour standards** — labour *timing* is P5
and *standards* are refused until we have a year of our own data (`FR-228`). No cluster, zone,
pick-and-pass, pick-to-carton or put-wall picking (v2/v3) — **batch picking is the one method v1.1
adds**, and the rest is a stated deferral in the product, not silence. No India, no 3PL, no channels.

## Definition of done
Per __MASTER__ and `IMPLEMENTATION-PLAN.md` §10, with the four programme-specific additions:
a migration that only `RAISE NOTICE`s its checks is not verified · every `L-n` invariant has a
database guard **and** a service guard that rejects first with a field-level error · the
loose-coupling ratchet runs in CI, not in a reviewer's memory · **every threshold column ships with
the scheduled job that reads it** (`FR-165`) — a dated obligation with no actor is a defect at the
moment it is merged.
