# IRREVERSIBLE — free now, impossible later

<!-- check-design-set: issue-citations file #2 #9 — `#2` and `#9` are ordinals in prose, not issue references — *Refusal #2*, *Adapter #2 (services)*, *ship-blocker #2*, *logistics needs #1, #2, #3, #5, #6, #10* — and at COMPETITOR-BENCHMARK.md:70/:146 `#9` is the markdown in-page anchor `[§9](#9--where-the-audits-disagree)`. In this repository `#2` and `#9` are in fact the two **pull requests** opened while the backlog was being filed, so no issue row can ever exist for either: see issues/CREATED.md -->

> **Read this immediately before writing the first migration of any phase.** Not at planning time,
> not at review time — at the moment the `.sql` file is created. Every row below is a column, a key,
> a table or a trigger that costs hours today and is either unaffordable or *untruthful* later.
>
> This document is subordinate to [`DECISIONS.md`](DECISIONS.md). Where a source review disagrees
> with `DECISIONS.md`, the correction is stated in §7, never applied silently.

**Scope.** `warehouse-base` (V500000–V509999), `warehouse` (V510000–V519999), and the handful of
rows that land in `platform` because the table is platform's. Adapters, `warehouse-3pl` and
`warehouse-india` appear only where a v1 base column is what makes them possible.

**Established** 2026-09-01 by consolidating four lenses — R2 §3, R4 §3.7 + §5.4, R5's
*cannot be added later* table, R7 §6 — against the live `classic` checkout. Every codebase claim
carries `file:line`; every count carries the command that produced it.

**Id namespace, and it was renamed once.** This document owns two prefixes, both declared in
`DECISIONS.md` §6: **`IRR-01`…`IRR-67`** for the consolidated rows, and **`PNR-1`…`PNR-4`** for the four
points of no return. `IRR-64`…`IRR-67` were allocated 2026-09-10 by `GAP-REGISTER-R4.md` §4.0; the next
free id is **`IRR-68`**.

The consolidated rows were **`I-01`…`I-63`** until 2026-09-02, and this preamble asserted the prefix was
"not used anywhere else in the set". **That was wrong.** `DATA-MODEL.md` §6 numbers its enforceable SQL
constraints `I-1`…`I-20` in the same prefix; from `I-10` up the two registers were byte-identical across
roughly 250 mentions, and no reader or `grep` could tell a constraint from an irreversible row. This
register moved rather than that one because it is the newer of the two and `DECISIONS.md` §6 had never
granted it `I-`. **A citation of an old `I-nn` from before that date means whichever register its
context meant** — every one in this set was re-read in context and rewritten, and
`tools/check-design-set.py` check 11 now fails the build if either register is redefined under the
other's prefix.

---

## §1 — The rule and the three classes

> **The rule: a schema decision is cheap exactly until the first row exists, and then it is
> permanent. Everything else is negotiable.**

R2 §3 states the classification this document adopts, and it is the only part of any lens that must
be memorised:

| Class | What it means | What it costs if deferred | On this list? |
|---|---|---|---|
| **Additive** | A new nullable column, a new table, a new screen | Cheap whenever it is done. This is why most of v1.1/v2/v3 can be deferred without anxiety | **No.** Deliberately. A list that contains everything protects nothing |
| **Re-keying** | Changing the unique key of a large table, or adding a `NOT NULL` dimension to it | Mechanically possible. Backfill a value, re-index, and touch every query, report, export and integration that joins on it. **Weeks, plus silent breakage** — the queries that still compile and now return a different number | **Yes** |
| **Unbackfillable** | The column's historical value **was never observed and cannot be derived** | You can add the column. You cannot populate it truthfully. Every aggregate that crosses the boundary becomes **a lie that looks like data** | **Yes, and this is the class the list exists for** |

The distinction that decides whether a row belongs here is not difficulty. It is this test:

> **If we add this in year two, can the year-one data be made correct?**

*No* → the row is here, class **unbackfillable**.
*Yes, but only by re-keying the hottest table in the product* → the row is here, class **re-keying**.
*Yes, by an `ALTER TABLE … ADD COLUMN`* → the row is **not** here, and nobody should spend a day
defending it. §6 names the things people reliably fear that fall in this bucket.

**Two sharpenings that the classification alone does not give you.**

1. **Re-keying is recoverable; unbackfillable is not.** Ranking them equally is how a plan spends its
   contingency on the wrong row. Where a row is both — `owner_id` (`IRR-06`) is a re-key *and* an
   unbackfillable — it is the unbackfillable half that sets the deadline.
2. **A cache has no deadline of its own.** `whb_stock_positions` is a cache under `L-4` — a full
   rebuild from `whb_stock_movements` must reproduce it exactly. Therefore **every position-key
   column's real deadline is the movement line's deadline**, and adding a member to the position key
   later is free *if and only if* the ledger already carries it. This one observation removes about a
   dozen rows' worth of anxiety and is the reason §3 has four gates rather than one per table.

---

## §2 — The consolidated list

### 2.1 How the four lenses were merged, and the arithmetic

Five enumerated source lists, because R4 carries two:

| Source list | Rows |
|---|---|
| R2 §3 — *The structural ones* (`T-001`…`T-095`) | 22 |
| R4 §3.7 — *The day-one column list, restated as a single claim* (twelve provably-unaddable properties) | 12 |
| R4 §5.4 — *What MUST land in `warehouse-base` v1 even though `warehouse-3pl` ships later* | 15 |
| R5 — *CANNOT BE ADDED LATER — the v1 schema commitments* | 28 |
| R7 §6 — *The irreversible list* | 25 |
| **Total source rows before de-duplication** | **102** |

**Merge rule.** Two source rows collapse into one only when they name the *same schema object* —
the same column, key, table or trigger. Two rows that name different objects for the same *reason*
stay separate (`IRR-13` `lot_id` and `IRR-14` `serial_id` share every word of their argument and are two
columns, so they are two rows). Rows that name an object *plus* its registry table stay separate
where the registry is independently omissible (`IRR-06` `owner_id` and `IRR-07` `whb_owners`).

**Result: 102 source rows → 62 merged rows.** Ids run `IRR-01`…`IRR-63`; **`IRR-18` is a retired id**
(R4 §3.2's `warehouse_id` was drafted separately and then merged into `IRR-17`, and per
`DECISIONS.md` rule 4 the id is left vacant rather than renumbered). Every source row maps to at
least one merged row and no source row is dropped; several map to two — R4 §3.7 item 5 covers
append-only *and* `sequence_no`, which are `IRR-02` and `IRR-03`.

**Round 4 (2026-09-10) added four rows outside this arithmetic.** `IRR-64`…`IRR-67` come from R22 and
R26 through `GAP-REGISTER-R4.md` §4.0, not from the five source lists above, so the 102 → 62 merge
stands as computed. The list now holds **66 populated rows**.

**What each lens uniquely contributed** — the answer to *"could we have run three lenses instead of
four?"*, and it is no:

| Lens | Merged rows it is the **sole** source of | Count |
|---|---|---|
| R2 §3 | `IRR-01` double-sided · `IRR-16` location hierarchy · `IRR-40` declared valuation grain · `IRR-46` tasks in v1 · `IRR-47` allocation strategy as data · `IRR-51` daily snapshot job · `IRR-62` partitioning | **7** |
| R4 §3.7 + §5.4 | `IRR-07` `whb_owners` · `IRR-08` `balance_rule`/`allows_mixed_owner` · `IRR-19` `(owner_id, sku)` + aliases · `IRR-23` lifecycle timestamps · `IRR-58` `commingle_policy` · `IRR-59` carrier account owner · `IRR-60` owner-scoped grants | **7** |
| R5 | `IRR-11` condition axis · `IRR-12` `duty_status` · `IRR-20` read-point vs biz-location · `IRR-38` cost layers · `IRR-39` `moving_average_after` · `IRR-41` `handover_id`/`posting_status` · `IRR-42` `hsn_code` snapshot · `IRR-43` barcode `pack_quantity` · `IRR-44` GLN/UQC · `IRR-52` `count_snapshot_quantity` · `IRR-53` lot attribute columns · `IRR-54` `transformation_id` · `IRR-55` style/variant · `IRR-56` regulatory block · `IRR-57` warehouse legal identity · `IRR-61` `on_behalf_of_actor_id` | **16** |
| R7 §6 | `IRR-17` `company_id`/`warehouse_id` · `IRR-25` external-ref tables · `IRR-26` stable string keys · `IRR-28` document/source-system registries · `IRR-29` transit/mobile location types · `IRR-30` custody history (`whb_location_user_assignments`) · `IRR-31` `whb_item_types` · `IRR-33` `whb_counterparties` · `IRR-37` value-only movements · `IRR-48` `actor_type`/`device_id` · `IRR-49` batch posting · `IRR-63` permission namespace | **12** |
| **Sole-source rows** | | **42** |
| **Rows found by two or more lenses** | | **20** |

Twenty rows were found independently by two to five lenses. Those twenty are not the important
ones — they are the *obvious* ones. The 42 sole-source rows are what running four lenses bought, and
R5 and R7 between them contributed 28 of the 42. A three-lens review would have shipped without
`duty_status`, without `handover_id`, without the external-ref tables and without the reserved
permission namespace.

**Commands used for the arithmetic:**

```
# source row counts, per list
sed -n '/^| # | Finding | Change class if deferred/,/^$/p'   docs/reviews/R2-tier1-wms-audit.md          | grep -c '^| [0-9]'
sed -n '/^Twelve properties, each of which/,/^Everything else in this report/p' docs/reviews/R4-fulfilment-3pl-audit.md | grep -cE '^[0-9]+\.'
sed -n '/^| # | Must be in base\/app v1/,/^\*\*Fifteen items/p'  docs/reviews/R4-fulfilment-3pl-audit.md | grep -c '^| [0-9]'
sed -n '/^| # | Column \/ key \/ dimension/,/^\*\*Cost of all 28/p' docs/reviews/R5-standards-industry-ops.md | grep -c '^| [0-9]'
sed -n '/^| # | Must be in `warehouse-base` v1/,/^\*\*Twenty-five items/p' docs/reviews/R7-logistics-supply-chain-seam.md | grep -c '^| [0-9]'
```

### 2.2 Reading the table

- **Class** is `RK` (re-keying), `UB` (unbackfillable), or `RK+UB` where both apply. `UB` rows outrank
  `RK` rows for scheduling: an `RK` row that slips costs weeks, a `UB` row that slips costs the truth.
- **Deadline** is the gate from §3 (`PNR-1` … `PNR-4`) plus, where `DECISIONS.md` names it, the task.
  `DECISIONS.md` `OD-1` and `OD-7` both name **`P0-02`** as the task that writes `whb_stock_movements`;
  that is the only task id this document cites, because it is the only one already fixed. Every other
  deadline is expressed against a migration or a gate, never against an invented task id.
- **Band** is the Flyway band from `DECISIONS.md` `D-2`. `platform` means the table is platform's and
  the change is an `INSERT` or an `ALTER` in platform's own range — see `D-10`'s corollary: *the
  ratchet can only ever be "zero commits to `warehouse-base`", never "zero commits to `platform`"*.
- **Sources** are finding ids in the `DECISIONS.md` §6 namespaces. `[R4 §3.7 n]` and `[R7 §6 n]` mean
  item *n* of that list where the list is numbered rather than id'd.

It is **one list**, presented in eight blocks so it can be read. No row appears twice; the numbering
runs `IRR-01` → `IRR-67` without a break. Rows added after a block was written sit in the block they
belong to, and the block heading names them (`IRR-62` in A, `IRR-63` in H, and round 4's four).

---

### Block A — The shape of the ledger (`IRR-01` … `IRR-05`, `IRR-62`, `IRR-67`)

| # | What must exist | Table · column | Module · band | Deadline | Class | The argument — what breaks one version later | Sources |
|---|---|---|---|---|---|---|---|
| **IRR-01** | The ledger is **double-sided**: a movement is two or more signed lines that conserve quantity. Never one row carrying `from_*` and `to_*` | `whb_stock_movement_lines` — one `location_id`, one signed `base_quantity`, no `from_/to_` pair | base · V500000–V509999 | **PNR-1** · `P0-02` | **rewrite** (worse than `RK`) | *"What was on hand at location L, item I, owner O, status S, at 14:00 on 3 March?"* is `SUM(base_quantity) WHERE …` with signed lines, and a `CASE` over two nullable location columns — one branch per movement type, the branch list growing forever — with from/to. Worse, the `CASE` is **uncheckable**: there is no "the lines sum to zero" invariant, so a movement that decrements the source and forgets the destination is a **silent stock leak**. `L-1` does not exist as a testable statement without this row. Every other row in this document depends on it | `T-001`, `D-4`, `L-1` |
| **IRR-02** | **Append-only**, correction by reversal only: no `UPDATE`, no `DELETE` on a posted movement or line; `reversal_of_movement_id` + `reversed_by_movement_id` + `is_reversed` | `whb_stock_movements`, `whb_stock_movement_lines` + the `L-2` trigger | base | **PNR-2** | **UB** | Immutability is a claim *about history*. Turning it on in year two says nothing about year one, and year one is the period the first audit tests. Rows already updated in place cannot be un-updated. `reversal_of_movement_id` added late is worse than useless: if v1 permitted edits, the corrections are already invisible, so the column describes a history that no longer exists | `T-017`, `[R4 §3.7 5,6]`, `F-082`, R5 row 8, `[R7 §6 6]`, `L-2`, `L-3` |
| **IRR-03** | **Gapless monotonic `sequence_no`** (per warehouse) + `prev_payload_hash` | `whb_stock_movements.sequence_no BIGINT NOT NULL`, `prev_payload_hash CHAR(64)` | base | **PNR-1** | **UB** | A sequence cannot be started retroactively over rows that already exist — the rows that already collide on `occurred_at` can never be ordered, so *"balance as at"* is permanently ambiguous for that period. The outbox cursor (`IRR-50`) and the tamper chain both key on it. A hash chain begun in v2 proves nothing about v1 | `[R4 §3.7 5]`, `F-082`, `F-086`, R5 row 21, `[R7 §6 6]` |
| **IRR-04** | **`idempotency_key` + `payload_hash`**, unique on `(source_system, idempotency_key)` **across months** — the `PRIMARY KEY` of the non-partitioned `whb_movement_idempotency_keys` registry, because a unique index on the partitioned ledger holds per partition only (`DATA-MODEL.md` §1.9, `MPR-OPEN-07`) — **never server-generated** | `whb_stock_movements` | base | **PNR-1** | **UB + live corruption** | This is the most irreversible field in the schema. **An already-double-posted ledger cannot be deduplicated afterwards**, because a duplicate produced by a retry is byte-identical to a legitimate repeat of the same real event, and no human can tell them apart a year later. In an append-only ledger the only removal is a reversal, which then looks like a shrinkage adjustment forever. Server-generating the key defeats the whole mechanism: a retried network timeout posts twice | `T-091`, `[R4 §3.7 4]`, `F-081`, R5 row 22, `[R7 §6 5]`, `L-9` |
| **IRR-05** | **Virtual locations exist and every line resolves to one.** A receipt balances against a virtual counterparty, never against nothing. `IN_TRANSIT`, `SUPPLIER`, `CUSTOMER`, `ADJUSTMENT_OFFSET`, `SCRAP`, `PRODUCTION`, `JOB_WORKER` are location rows with `is_virtual_counterparty` / `is_transit` flags | `whb_locations`, `whb_location_types` | base | **PNR-1** | **rewrite of every movement** | Without them the ledger has no balancing counterparty, so `L-1` has nothing to test and a leak was never detectable. Concretely: in-transit stock, consignment stock, at-job-worker stock and at-customer stock are **nowhere** — the first period end produces a balance sheet wrong in three directions, and `IRR-12`'s bonded segregation and `IRR-06`'s ownership have no location to live at. Backfilling a null "from" is guessing | `T-009`, R5 row 20, `[R7 §6 2]`, `L-1`, `S-069` |
| **IRR-62** | The ledger is **partitioned by `occurred_at`** from the first migration | `whb_stock_movements`, `whb_stock_movement_lines` | base | **PNR-1** | **RK** | Nothing historical is lost — but **migrations in this repo are baked into the backend image at build time** (`Dockerfile.backend:140-181`, R1 `C-011`), so a partition conversion has no comfortable window: it is a rebuild plus downtime on the two largest tables in the product, on a customer's live stock. Free in the `CREATE TABLE`; a project in year three | `T-095`, `C-011` |
| **IRR-67** | **The non-ledger high-volume tables are partitioned at `CREATE`**: `whb_stock_position_snapshots` by `snapshot_date` (non-zero positions only), `whb_outbox` by `recorded_at` with PK `(cursor, recorded_at)`, `whb_outbox_deliveries`, `whb_inbound_messages`, `whb_movement_batch_results`, and `whb_audit_events` by `occurred_at` with PK `(sequence_no, occurred_at)` | the six tables, reusing `P0-02`'s partition job, each with a retention-class row | base · `V500040`–`V500045` | each table's `CREATE`; the snapshot's **start date** is **PNR-3** (`IRR-51`) | **RK** | `IRR-62`'s argument, applied to the tables that grow as fast as the ledger. A migration is baked into the backend image, so converting a live table to partitions is a rebuild plus downtime. And a primary key that omits the partition key cannot be partitioned at all without re-keying it. The outbox and the audit trail are also the two tables a retention policy must drop by range, which an unpartitioned table can only do by a mass `DELETE` | `RL-011`, `IRR-62`, `IRR-51` |

### Block B — Grain and keys (`IRR-06` … `IRR-20`)

| # | What must exist | Table · column | Module · band | Deadline | Class | The argument | Sources |
|---|---|---|---|---|---|---|---|
| **IRR-06** | **`owner_id NOT NULL`** on every movement line, position, lot, serial, LPN, reservation and cost layer, **and in the position unique key**. **On an LPN it is the custodian/label owner**, not the owner of every unit on it: a mixed-owner pallet keeps its per-unit owners on its positions, and owner reporting reads positions (`RG-022`) | `whb_stock_movement_lines.owner_id`, `whb_stock_positions.owner_id`, `whb_lots`, `whb_serials`, `whb_lpns`, `whb_reservations` | base | **PNR-1** · `P0-02` | **RK + UB** | **The single most expensive column to add late in the entire design.** No rule recovers whose a unit was, so everything historical defaults to `OWN` — which means consignment stock received before the column existed is *already on the balance sheet* and cannot be reclassified without restating closed periods, and 3PL history begins at the migration date. It simultaneously changes the unique key of the hottest table in the product, so it is a re-key *and* an unbackfillable. Four lenses reached it independently. Without it `warehouse-3pl` is not a module, it is a rewrite, and the prior product's own build contract already knew: *"Pre-prod = cheap now; brutal retrofit later"* (`classic-issues/warehouse-base/docs/WMS/WMS_Inbound_Corrections_Build_Contract.md:109`) | `T-002`, `F-001`, `F-059`, `[R4 §3.7 1]`, `[R4 §5.4 1,3]`, `S-064`, `[R7 §6 1]`, `D-5`, `RG-022` |
| **IRR-07** | **`whb_owners` + `whb_owner_types`** registry, house owner seeded, `is_house` / `posts_to_our_gl` / `default_cost_basis` flags | base tables | base | **PNR-1** | **RK** | `IRR-06` is a column; this is where the column points. Omitting it does not merely delay 3PL — **consignment and customer-owned-goods-under-repair have nowhere to live in v1 either**, and both are ordinary business for a dealership workshop. `owner_type` as a `CHECK` re-closes what `D-10` opens | `F-002`, `[R4 §5.4 2]`, `D-10` registry #9 |
| **IRR-08** | **`balance_rule`** on the movement type and **`allows_mixed_owner`** on the location | `whb_movement_types`, `whb_locations` | base | **PNR-1** | **RK** | `L-1` balances per owner. A 3PL's own packaging consumed against a client's order is one physical act and two owners; without a declared balance rule the movement is either refused or silently mis-attributed, and there is no atomic way to post it at all | `[R4 §5.4 3]`, `F-059`, `L-1` |
| **IRR-09** | The **full position unique key**: `(company_id, owner_id, item_id, location_id, lot_id, serial_id, lpn_id, stock_status_code, duty_status)` | `whb_stock_positions` | base | **PNR-4** (but see §3.4 — the real gate is **PNR-1**) | **RK** | Rows that merged under a narrower key **cannot be un-merged**: two lots in one bin become one number and the split is gone. *But* `L-4` makes positions rebuildable, so this is recoverable **iff every key member is on the movement line**. That is the whole reason `IRR-10` through `IRR-15` are ledger-line rows and not position rows | `T-003`, `L-5`, `L-4` |
| **IRR-10** | **`stock_status_code`** on every movement line and **in the position key**; statuses are a registry with behaviour flags (`is_available`, `is_allocatable`, `is_shippable`, `is_countable`, `is_owned_asset`, `requires_reason_to_enter/leave`, `badge_variant`), never an enum and never a location | `whb_stock_movement_lines.stock_status_code`, `whb_stock_positions.stock_status_code`, `whb_stock_statuses` | base | **PNR-1** | **UB** | Whether historical stock was available, quarantined or damaged is **not derivable**: everything becomes `AVAILABLE` retroactively. Three shortcuts each fail: *"damaged goes in the DAMAGED bin"* forces a physical move for a paperwork event and makes counting a bin disagree with counting an item; *"status is a `CHECK` enum"* makes every new status a migration **plus** a code change in every query that hardcodes the available list — this repo's documented recurring defect; *"available means `status='AVAILABLE'`"* breaks on the second allocatable status. If it is not in the position key, every historic position row is wrong the day it is added | `T-004`, `[R4 §3.7 9]`, `[R4 §5.4 14]`, `F-068`, `[R7 §6 18]` |
| **IRR-11** | **Condition/disposition as an axis separate from workflow step** | `whb_stock_movement_lines` + `whb_stock_statuses` split into a status axis and a condition axis | base | **PNR-1** | **UB** | Merging workflow state and goods condition into one column — as the prior product's `wms_inventory.stock_status` does — is unrecoverable: `PICKED` and `DAMAGED` are simultaneously true and one column silently drops one of them. Splitting later cannot tell which historical `DAMAGED` rows were also allocated | R5 row 3, `S-069` |
| **IRR-12** | **`duty_status`** on every movement line and in the position key, as `VARCHAR(40) NOT NULL DEFAULT 'DOMESTIC'` **`REFERENCES whb_duty_statuses(code)`** — registry 15, created in `V500005`. **Base seeds `DOMESTIC` only.** The regime values are jurisdiction data: India's list is in [`INDIA-LOCALISATION-PACK.md`](INDIA-LOCALISATION-PACK.md) §7.1, seeded by `warehouse-india` | `whb_stock_movement_lines`, `whb_stock_positions`, `whb_cost_layers`, `whb_duty_statuses` | base | **PNR-1** | **UB** | **Bonded and duty-paid stock of one SKU must never merge into one balance.** Once a year of movements has commingled them no algorithm separates them, the ex-bond Bill of Entry cannot consume identified bonded quantity, and the warehouse cannot be licensed retrospectively over the mixture. This is a **customs offence, not a data-quality issue** — the only row on this list whose failure mode is criminal rather than commercial. **The FK is part of the row.** As a free string a typo is a new balance grain rather than an error, so one regime splits across two spellings that no later merge can rejoin under `L-2`/`L-3`. Feature ships v2 (`warehouse-india`); the column and its registry ship v1 | R5 row 2, `S-044`, `D-5`, `D-8`, `RL-001` |
| **IRR-13** | **`lot_id`** as an FK to a lot entity, not a `VARCHAR` on the line | `whb_stock_movement_lines.lot_id → whb_lots` | base | **PNR-1** | **RK + data quality** | Lots keyed as strings cannot be proven identical after the fact: `"L-2024/07"` and `"L2024-07"` are the same lot and nothing can demonstrate it. A recall is a question about the past, so the identity must have been right at the time. Accessories is the live counter-example: `accessory_stock_levels.batch_number VARCHAR(50)` is part of a composite index and nothing else (`accessories/…/V30130__Create_accessory_stock_levels_table.sql:17-19,40-46`) | `T-005`, `[R4 §3.7 7]`, `F-063`, `[R7 §6 19]`, `C-028` |
| **IRR-14** | **`serial_id`** FK to a serial entity with a current state; serial control is a **mode**, not a boolean; **`uk(item_id, serial_number)`**, not a global unique | `whb_stock_movement_lines.serial_id → whb_serials` | base | **PNR-1** | **RK** | A serial's past locations reconstructed from string matches is not traceability. And the key choice is a one-way door in a second way: changing a global unique key after data exists is a migration with duplicates to resolve by hand — **and the rows the wrong constraint *rejected* were never recorded at all**, so there is nothing to migrate them from | `T-006`, `[R4 §3.7 7]`, R5 row 16, `[R7 §6 19]`, `C-028` |
| **IRR-15** | **`lpn_id`** on the line + **`whb_lpns.received_at`** + `parent_lpn_id` for nesting | `whb_stock_movement_lines.lpn_id`, `whb_lpns` | base | **PNR-1** | **UB** | What was on which pallet, ever, before the change — gone. Pallet-level history cannot be reconstructed from item-level rows. Concretely: **anniversary storage billing has no other anchor than `whb_lpns.received_at`**, so per-pallet billing for any past period is not merely hard, it is undefined; and every EPCIS `AggregationEvent` and every ASN carrying an SSCC depends on it. LPN *handling* is v1.1/v2; the two columns are v1 | `T-007`, `[R4 §3.7 8]`, `[R4 §5.4 6]`, `F-064`, R5 row 13, `[R7 §6 19]` |
| **IRR-16** | The **location model is a hierarchy** (site → zone → aisle → bay → level → bin), typed, with enforced capacity — not four free-text VARCHARs | `whb_locations` with `parent_location_id`, `whb_location_types` | base | **PNR-1** | **rewrite** | Zone- and aisle-level history silently rewrites itself if the hierarchy is later reparented: last year's zone report returns a different number this year and nothing says why. The live counter-example is `accessory_storage_bins`, whose `zone`/`aisle`/`rack`/`level` are free-text VARCHARs with no zone entity (`accessories/…/V30033__…:16-24`), and whose `max_weight`/`max_volume` are stored and never read | `T-008`, `C-029` |
| **IRR-17** | **`company_id`** and **`warehouse_id`** on the movement header | `whb_stock_movements` | base | **PNR-1** | **UB** | Adding a company axis after the ledger has rows means every historic row is assigned to a *guessed* legal entity — and **a GST return computed from guessed entities is a filing error**, not a report defect. `warehouse_id` is separately required because `sequence_no` (`IRR-03`) is gapless *per warehouse*; adding the axis later renumbers history | `[R4 §3.2]`, `[R7 §6 22]`, `F-025`, `D-8` |
| **IRR-18** | *(merged into `IRR-17`)* | — | — | — | — | — | — |
| **IRR-19** | **Item uniqueness is `(owner_id, sku)`**, plus the alias / identifier table that is also the channel-listing table | `whb_items`, `whb_item_identifiers` | base | **PNR-1** | **RK** | A globally unique SKU is a one-way door: **the second client with a colliding SKU cannot be onboarded**, and the repair is a re-key of the item master plus every FK to it. The alias table is the same decision seen from the other side — one item, many external codes, each with its own UoM (`IRR-43`) | `[R4 §5.4 10]`, `F-005`, `F-006` |
| **IRR-20** | **`read_point_location_id`** and **`biz_location_id`** as two columns, not one `location_id` | `whb_stock_movement_lines` | base | **PNR-1** | **UB** | Where a scan happened and where the goods then were are different facts. A single column has already merged them, and the merge is not undoable. This is the EPCIS `readPoint` vs `bizLocation` distinction; the *feature* is v2, the two columns are v1 | R5 row 7, `S-007` |

### Block C — Time (`IRR-21` … `IRR-23`)

| # | What must exist | Table · column | Module · band | Deadline | Class | The argument | Sources |
|---|---|---|---|---|---|---|---|
| **IRR-21** | **Three timestamps, never one**: `occurred_at` (**producer-supplied** business time) · `recorded_at` (server clock) · `posting_date` (the accounting date) — plus `occurred_at_tz_offset` | `whb_stock_movements` | base | **PNR-1** · `P0-02` | **UB** | **One timestamp cannot be split into three afterwards.** Collapsing them kills four things at once and every one of them silently: offline RF replay (a gate-out at 22:00 synced at 09:00 dates itself wrong), degraded-mode catch-up, period cut-off, and EPCIS `eventTime` vs `recordTime`. Commercially: storage days, split-month and anniversary billing all bill from the wrong date, and a 2nd-of-month posting of a 31st-of-month event lands in the wrong invoice. The difference between `occurred_at` and `recorded_at` is also **the only latency diagnostic that exists** | `T-018`, `[R4 §3.7 2,3]`, `[R4 §5.4 7]`, `F-083`, R5 row 6, `[R7 §6 4]`, `L-13` |
| **IRR-22** | **`period_id` on the movement** + `whb_stock_periods` with `OPEN` / `SOFT_CLOSED` / `CLOSED` and an override audit | `whb_stock_movements.period_id`, `whb_stock_periods` | base | **PNR-1** | **UB** | Rows posted before periods existed belong to **no** period, so the first close has an un-closeable opening set and the first signed valuation report is over a set that cannot be frozen. Downstream: an approved 3PL invoice silently changes after billing, because nothing refused the backdated post | `[R4 §5.4 13]`, `F-085`, R5 row 28, `L-8` |
| **IRR-23** | **Lifecycle timestamps** on receipt, order, task and shipment headers — not just `created_at`/`updated_at` | `wh_*` document headers; `whb_tasks` in base | `warehouse` · V510000–V519999 (+ base for tasks) | **PNR-3** | **UB** | **A duration cannot be backfilled.** Dock-to-stock, order-to-ship, pick-to-pack and every SLA number in the product is a difference between two timestamps that were either captured or were not. The first client's month-one SLA report cannot be produced, ever, if they were not | `[R4 §5.4 8]`, `F-074`, `F-075` |

### Block D — Identity, lineage and idempotency (`IRR-24` … `IRR-26`)

| # | What must exist | Table · column | Module · band | Deadline | Class | The argument | Sources |
|---|---|---|---|---|---|---|---|
| **IRR-24** | The **lineage quad** on the header — `source_system`, `source_document_type`, `source_document_id`, `source_document_line_no` — plus **`source_line_ref`** on the line | `whb_stock_movements`, `whb_stock_movement_lines` | base | **PNR-1** | **UB** | A single free-text `reference` cannot be joined, indexed or grouped, so it is a dimension that never becomes a report. Operationally it is how a consumer **finds its own postings**: `GET /movements?source_document_type=TRIP&source_document_id=…` is the call the logistics module makes, and without it every consumer builds a private mapping table. `source_document_line_no` is separately load-bearing: a partially reversed multi-line source document cannot be reconciled line by line without it. The live counter-example is `accessory_inventory_transactions`, whose `reference_type VARCHAR(50)` carries its vocabulary **in a SQL comment** and no registry (`accessories/…/V30131__Create_accessory_inventory_transactions_table.sql:27-29`) | `[R4 §3.7 11]`, `F-084`, `[R7 §6 3]`, `L-12` |
| **IRR-25** | The **three external-ref tables**: `whb_item_external_refs`, `whb_counterparty_external_refs`, `whb_location_external_refs` — `(source_module, external_id)` unique, `source_module` an **opaque string, not an FK** | base tables | base | **PNR-1** | **UB** | This is the adapter join, and it is what keeps `D-11`'s dependency arrow pointing the right way. Without `whb_location_external_refs`, a vehicle-as-location either forces `whb_locations.vehicle_id → logistics` (base depends on logistics — fatal) or forces logistics to duplicate the whole location tree. Without `whb_item_external_refs`, **every historic movement has an unresolvable external identity**: a dealer's own part number is neither a SKU nor a barcode, so the port cannot identify it and the mapping cannot be reconstructed after the fact. Shape verbatim from `accounting-base/…/V600001__Create_acc_companies_and_external_refs.sql:204-229`, whose own comment states the rule: *"map, not mirror. source_module is an opaque string"* (`:234-235`). **`D-9` additionally makes `whb_item_external_refs` mandatory in v1 with an `ACCESSORIES` row per dual-stocked SKU** — see [`COEXISTENCE.md`](COEXISTENCE.md) §5 | `[R7 §6 14,15]`, `C-035`, `D-9`, `OD-4` |
| **IRR-26** | A **stable string key** on every base-resolved object another module holds a reference to — item code, location code, counterparty code, carrier code | `whb_items.code`, `whb_locations.code`, `whb_counterparties.code`, … | base | **PNR-1** | **RK** | It is what makes the five movable module boundaries a *refactor* rather than a *data migration*. If a consumer holds a `whb_locations.id` UUID and the table later moves module, every held reference is dangling; if it holds a code, the move is a re-point. Cheap now: one `VARCHAR` + unique index per master | `[R7 §6 24]`, `[R4 §4.5]` |

### Block E — Vocabularies that must be rows, not enums (`IRR-27` … `IRR-33`)

Each is *also* one of the thirteen registries in §5. It appears here as well because the **column that
references it** is on the ledger and is therefore subject to `PNR-1`/`PNR-2`, whereas the registry
table itself is merely early.

| # | What must exist | Table · column | Module · band | Deadline | Class | The argument | Sources |
|---|---|---|---|---|---|---|---|
| **IRR-27** | **`whb_movement_types` as rows** with behaviour flags: `direction`, `is_financial`, `cost_basis_default`, `reversal_type_code`, `requires_approval`, `requires_reason`, `affects_availability`, `is_stock_bearing`, `is_billable_event` | `whb_movement_types` + `whb_stock_movements.movement_type_code` FK | base | **PNR-1** | **refactor + UB** | The movement type is the join point for posting treatment, billability and the reversal counterpart of every historical movement — all three of which are **unrecoverable** if the type was a bare string. `is_billable_event` in particular: 3PL activity billing computed from real history rather than from its own go-live date exists only if the flag was on the type from v1. And as an enum or `CHECK`, **every adapter is blocked on a base release** — a vertical needing `PDI_CONSUME` must not need a core deploy (`D-11`) | `T-015`, `F-087`, `[R7 §6 7]`, `D-10` |
| **IRR-28** | **`whb_document_types`** and **`whb_source_systems`** as rows | base tables | base | **PNR-1** | **RK** | `TRIP`, `MANIFEST`, `CONSIGNMENT`, `POS_SHIFT`, `JOB_CARD` are other modules' document types. Same argument as `IRR-27`, plus one more: **`source_system` partitions the idempotency-key namespace** (`IRR-04`), so if two producers were ever allowed the same code their keys collide *retroactively* and the collision cannot be undone. `whb_source_systems` also carries the `ACCESSORIES` reserved row that `D-9` depends on | `[R7 §6 8]`, `D-9`, `D-10` |
| **IRR-29** | **`whb_location_types`** with `is_physical`, `is_stock_holding`, `is_virtual_counterparty`, `is_mobile`, `is_transit`, `allows_mixed_owner`, `requires_assigned_user`; seeded with `IN_TRANSIT`, `MOBILE`, `VEHICLE`, `TRAILER` | `whb_location_types` | base | **PNR-1** | **RK** | **This is the row the prior product actually broke.** `zone_type` and `location_type` `CHECK` constraints were *"dropped and recreated with completely different enum value sets"* 36 versions after creation — `classic-issues/warehouse-core/docs/WAREHOUSE_CORE_ISSUES.md:87`, naming `V200006`'s `PUTAWAY_STAGING/BULK_STORAGE/FORWARD_PICK` replaced wholesale by `V200042`'s `PICK_FORWARD/PICK_RESERVE/COLD/FROZEN`. Every historical row's type then means something else. Without `is_transit` a transfer is one movement and stock **falls off the books between despatch and arrival**; every historic transfer becomes unsplittable and in-transit ageing is unanswerable for the past | `[R7 §6 2,13]`, `F-089`, `D-10` registry #5 |
| **IRR-30** | **Location custody as a dated junction**: `whb_location_user_assignments`, with `assignment_role` from the `CUSTODY_ROLE` code list (`CUSTODIAN` · `DRIVER` · `HELPER`), one current `CUSTODIAN` per location and an `EXCLUDE` on its range. `whb_locations.assigned_user_id` is dropped | `whb_location_user_assignments` (`V500013`) | base | **PNR-1** | **RK** (the custody history is **UB** from the first reassignment) | The van, the technician's boot and the last-mile driver's stock are locations with an owner-of-custody. Without custody on the location, van stock becomes a separate table with a separate reconciliation problem, and `warehouse-adapter-field-service` (v1.1) is unbuildable on the ledger. `field-service` already knows where the van is — `job_trips` + `job_track_points` — and has **no stock table at all**. **A scalar was the wrong shape** (`D-14` item 1): a shortage belongs to whoever held the location *when the stock left*, a reassigned column says only who holds it now, and a van with a driver and a helper cannot be recorded at all | `[R7 §6 13]`, `T-080`, `C-034`, `RG-004` |
| **IRR-31** | **`whb_item_types`** admitting `RETURNABLE_EQUIPMENT`, `TYRE`, `FUEL`, `PACKAGING` alongside `STOCK`/`NON_STOCK`/`SERVICE`/`KIT`/`CORE`/`CONSUMABLE`, with `is_stocked`, `is_serial_default`, `is_lot_default`, `is_value_only` flags | `whb_item_types` | base | **PNR-1** | **RK** | **Four seed rows in v1 are what stops a future module building private ledgers.** Without them a logistics module builds `tms_equipment_inventory` and `tms_tyres` as its own stock tables, and the suite acquires a fourth and fifth stock truth. Packaging and consumables are the same argument inside the warehouse: they are stock, and stock that is billable | `[R7 §6 20]`, `F-060`, `D-10` registry #10 |
| **IRR-32** | **`whb_reason_codes`** — `context` with **no `CHECK`**, plus `tax_treatment_code` (named `itc_treatment` until round 4, `RL-008`; values seeded by the jurisdiction module) and `statutory_category`; `reason_code_id` on the movement **header and line** | `whb_reason_codes`, `whb_stock_movements.reason_code_id`, `whb_stock_movement_lines.reason_code_id` | base | **PNR-1** | **UB** | **Free-text reasons cannot be mapped backwards.** A year of `"damaged in handling"` / `"dmgd"` / `"broken"` cannot be classified into the six statutory categories the GST stock account requires, so **that year's ITC reversal cannot be computed** and the Rule 56 stock account cannot be produced. Commercially the same shape: a transit loss without a categorical reason is unreportable and unclaimable against the carrier. The precedent is live and self-documenting — `accounting-base/…/V600002__Create_acc_reason_codes.sql:22-26`: *"`context` carries NO CHECK constraint, deliberately. It is a CATALOGUE, not an enum"* | `T-010`, R5 row 9, `S-028`, `[R7 §6 10]`, `D-10` |
| **IRR-33** | **`whb_counterparties`** + `whb_counterparty_roles` + `whb_counterparty_role_links` — roles as a **link table**, not a `partner_type` enum | base tables | base | **PNR-1** | **RK** | Inbound receiving that cannot name who shipped is a GRN with no traceable shipper. There is **no shared supplier or party master in this repo**: `asset_vendors` is assets-owned (`assets/…/V60056__…:3-38`), automotive's `customers`/`companies` model buyers and OEMs and are automotive-owned, and accessories receiving has **no supplier field at all** — `StockReceiptRequest.java:23-51` has ten fields and none is a vendor. `accounting-base` set the precedent by owning `acc_companies`. A role link table rather than an enum because a carrier is a counterparty *with a role*, and one party is routinely two roles | `[R7 §6 21]`, `C-031`, `C-035`, `OD-4`, `D-10` registry #11 |

### Block F — Quantity, UoM and value (`IRR-34` … `IRR-44`)

| # | What must exist | Table · column | Module · band | Deadline | Class | The argument | Sources |
|---|---|---|---|---|---|---|---|
| **IRR-34** | **`uom_code` + `base_uom_code` + `base_quantity` + frozen `conversion_factor_used`** on every line; conversion lives on the **item**, not on the UoM master; base UoM immutable once stock exists | `whb_stock_movement_lines`, `whb_item_uom_conversions` | base | **PNR-1** · `P0-02` | **UB** | Conversion factors are corrected over time. **A ledger that re-derives from today's factor silently restates last year** — and the restatement is undetectable, because both numbers are internally consistent. If history stores only the transaction UoM, the statutory stock account for a closed period changes retroactively. Accessories is the live proof of the failure mode: `conversion_factor` appears in exactly five files, all display/CRUD (`grep -rln conversionFactor accessories/backend/src/main/java` → `Uom.java`, `UomRequest`, `UomResponse`, `UomMapper`, `UomExportService`), `accessory_stock_levels` has **no UoM column at all**, and `accessory_inventory_transactions.uom_id` is nullable and never used in arithmetic. All accessories stock is in one implicit unit | `T-011`, `[R4 §3.7 10]`, `F-093`, R5 row 4, `[R7 §6 23]`, `C-026`, `L-7` |
| **IRR-35** | **`secondary_quantity` + `secondary_uom_code`** reserved on line and position (catch weight) | `whb_stock_movement_lines`, `whb_stock_positions` | base | **PNR-1** | **UB** | The actual weights were never captured. **There is nothing to backfill from.** Two nullable columns now; a reshaped ledger and every aggregate over it later. The feature is v1.1+ and the vertical it unlocks — meat, chemicals, bulk construction materials, anything weighed rather than counted — is unreachable without it | `T-012`, R5 row 5, `S-013` |
| **IRR-36** | **`unit_cost` + `cost_currency_code` + `extended_cost` + `cost_basis`** on the line; **`is_financial`** on the movement type. `cost_basis` ∈ `ACTUAL` · `STANDARD` · `AVERAGE` · `INFORMATIONAL` · `ZERO_BAILMENT` | `whb_stock_movement_lines`, `whb_movement_types` | base | **PNR-1** | **UB** | `cost_basis` decides whether an accounting envelope is emitted at all. Decided downstream, it is **a year of wrong journals**: a 3PL's clients' bailed stock posts to our own balance sheet and is unwound by hand, and our storage revenue has no cost of goods. `L-14` (*non-own stock is never valued*) is unenforceable without these two columns. `cost_currency_code` even in a single-currency v1 — retro-fitting currency onto a cost history means guessing | `[R4 §3.7 12]`, `[R4 §5.4 4]`, `F-010`, `L-14`, `S-078` |
| **IRR-37** | **Value-only movements**: `quantity = 0` permitted where `unit_cost` is present. **No `CHECK (quantity <> 0)`** | `whb_stock_movement_lines` | base | **PNR-1** | **RK** | Landed cost — duty, freight, insurance, clearing, port handling — arrives *after* the goods, on a different document, weeks later. Applying it is a `LANDED_COST_APPLY` movement with zero quantity and a value. A `CHECK (quantity <> 0)` written in v1 refuses it, and **freight can then never enter stock cost**, so warehouse and accounting disagree permanently on inventory value with no reconciling item. Removing the constraint later does not recover the year of receipts that were never loaded | `[R7 §6 9]`, `F-088`, `S-071` |
| **IRR-38** | **`cost_layer_id` on issue lines** + a layer table carrying `quantity_remaining` + a consumption table | `whb_stock_movement_lines.cost_layer_id` + layer/consumption tables | **see §7.3 — module placement is on the `D-6`/`OD-6` seam** | **PNR-1** for the *column*; `OD-6` for the tables | **UB** | An AVCO-only v1 keeps no layer history. **Switching to FIFO in v2 has nothing to build layers from**, so the change silently begins at the switch date and the opening layer set is a guess that no auditor will accept. Two tables, not one: a layer without a consumption link cannot answer *"which layer fed this issue"*, which is what a credit note needs in order to restore the original layer | R5 row 10, `S-053`, `OD-6` |
| **IRR-39** | **`moving_average_after`** snapshotted on every movement line | `whb_stock_movement_lines` | see `IRR-38` | **PNR-1** | **UB** | A backdated receipt **never restates** a snapshot already written (`RF-001`, adopted 2026-09-11): it inserts a cost layer, and the current average is computed on read from the open layers. **Without the snapshot there is no evidence of what the cost was on 31 March**, and the year-end valuation cannot be reproduced — which is precisely the number the auditor re-derives. Accessories demonstrates the drift concretely: `StockReceiptService.java:374-411` reverses a receipt by *subtracting the reversed receipt's own cost* from the weighted average, which is not the inverse of a weighted average, so the number drifts with every reversal and nothing records what it used to be | R5 row 11, `C-027` |
| **IRR-40** | The **valuation grain is declared in writing** before the first movement | design decision + the columns of `IRR-36`/`IRR-38`/`IRR-39` | — | **PNR-3** | **restatement** | Nothing is lost mechanically, and that is why it is dangerous. **Changing the grain restates every historical balance**, which is an accounting event with a disclosure and audit consequence, not a migration. Declare it, or the first grain change is discovered by the customer's auditor | `T-062`, `OD-6` |
| **IRR-41** | **`handover_id` + `posting_status`** (`NOT_APPLICABLE` · `PENDING` · `POSTED` · `REJECTED`) on every movement | `whb_stock_movements` | base | **PNR-1** | **UB** | Two columns. Without them, *"does the stock ledger tie to the GL?"* is **permanently unanswerable for every movement posted before the seam was built** — which is exactly the period the first audit covers, and it is the first question at every close. `D-6` already mandates them; this row is why they cannot wait for the GL integration that uses them | R5 row 12, `S-067`, `D-6` |
| **IRR-42** | **`tax_classification_code` + `tax_classification_scheme` snapshotted** on the movement or document line, mirroring the item's `tax_classification_code` (scheme `HSN` in India) | `whb_stock_movement_lines.tax_classification_code`, `.tax_classification_scheme` | base | **PNR-1** | **UB** | Tariff reclassification (HSN, in India) is retrospective in effect: reading the item master later gives the **new** code for **old** documents, so the historical GST return no longer reconciles to the system that produced it. Two `VARCHAR(20)` on the line. **The neutral name is part of the row**: the line is on the port response, the outbox and every export, and `PORT-AND-ADAPTER-CONTRACT.md` §10.2 forbids renaming a field, so a column called `hsn_code` would leave a second jurisdiction's 10-digit code nowhere to go (`RL-008`). Note that `accessories` has no HSN on its item master at all — the module's only `hsn_code` is on `accessory_quotation_pricing_components` (`accessories/…/V30066__…:37`), a pricing line, not a product | R5 row 18, `S-031`, `E-047`, `RL-008` |
| **IRR-43** | **`uom_code` + `pack_quantity` on the barcode / identifier row** | `whb_item_identifiers` | base | **PNR-1** | **UB** | Without it a case scan books one *each* — **the most common WMS data-quality failure in existence.** And it is unbackfillable in an unusual direction: the scans already recorded interpreted the barcode as base units, and reinterpreting them later would restate quantities that were *physically correct at the time* | R5 row 15, `S-001` |
| **IRR-44** | **`gln`** on warehouse, location and counterparty; **`unece_rec20_code` + `gst_uqc_code`** on the UoM master | `whb_locations`, `whb_counterparties`, `whb_uoms` | base | **PNR-1** | **RK** | Four nullable columns now. Later they are four migrations across live master data **plus a re-mapping of every integration already in production**, because every partner's existing payload was built against the un-coded master. `gst_uqc_code` is separately load-bearing for every Indian statutory payload, and it makes every compliance and EDI mapping derivable rather than hand-maintained | R5 row 26, `S-006`, `S-011` |

### Block G — Allocation, tasks and event plumbing (`IRR-45` … `IRR-52`, `IRR-66`)

| # | What must exist | Table · column | Module · band | Deadline | Class | The argument | Sources |
|---|---|---|---|---|---|---|---|
| **IRR-45** | **`whb_reservations` as rows** — never a `quantity_reserved` counter — with a **holder quad** `(holder_system, holder_document_type, holder_document_id, holder_line_no)` and `expires_at` | `whb_reservations` | base | **PNR-1** | **rewrite** | A counter is right in total and useless in detail, and it fails four ways: it **cannot release** (cancelling an order must decrement by exactly what that order held, and a counter does not remember); it **cannot reconcile** (there is nothing to compare it to, so drift is undetectable until available goes negative and the only repair is to zero it, releasing every reservation at once); it **cannot qualify** (soft vs hard, allocated-to-lot, expiring); it **cannot audit** (*"why can't I pick this stock?"* has no answer). The holder quad is what lets a module that is not `warehouse` hold stock — *"release everything trip X held"* is answerable only with it, and orphaned reservations otherwise reduce availability forever. Accessories proves the counter's fate: `quantity_reserved` is read in seven places and **written in none** — `grep -rn "reserveQuantity\|releaseReservedQuantity" accessories/backend/src/main/java \| grep -v /entity/` → **0** — so `quantity_available` (a `GENERATED` column, `V30130:14`) always equals `quantity_on_hand` | `T-014`, `F-028`, `[R7 §6 16]`, `C-022`, `L-10` |
| **IRR-46** | **A task table exists in v1**, with one synchronous consumer, even though v1 has no RF device | task table (see §7.3 on module placement) + `whb_task_types` in base | base (types) · `warehouse` (tasks) | **PNR-3** | **rewrite of inbound + outbound** | Not data — architecture. With a task table from v1, RF screens, assignment, interleaving, labour standards, the exception console and automation are each **a consumer**. Without it, each is a **rebuild of receiving and picking**. This is the only row on the list whose loss is measured in engineering months rather than in truth | `T-041` |
| **IRR-47** | **Allocation strategy is data** — bounded rows, not an `if`-ladder and not an expression language | allocation-rule rows | base | **PNR-3** | **refactor, growing** | Nothing historical is lost. But the allocator becomes untestable, and **by the third hardcoded strategy the cost exceeds the original build**. Listed because it is reliably the first thing cut for time and the cut is never revisited | `T-043`, `F-028` |
| **IRR-48** | **`actor_type`** (`USER` · `DEVICE` · `INTEGRATION` · `SCHEDULED_JOB` · `IMPORT` · `SYSTEM_CORRECTION`) + **`device_id`** | `whb_stock_movements` | base | **PNR-1** | **UB** | *"Who moved this"* is the first audit question and the answer is not always a user: a geofence-triggered arrival, an RFID portal read and a scan-gun posting have no attributable person. **Diagnosing a mis-scanning device retroactively is impossible without `device_id`** — and a mis-scanning device is a support case that happens, not a hypothetical | `[R4 §3.2]`, `[R7 §6 11]`, `F-072` |
| **IRR-49** | A **batch posting endpoint** with **per-movement** idempotency and per-movement results | port surface + `whb_stock_movements` | base | **PNR-1** | **RK** | A device syncing forty scans after a route must not lose thirty-nine because of one bad row. It is a v1 *schema* commitment rather than a v1 feature because per-movement idempotency is the same `uk(source_system, idempotency_key)` as `IRR-04` — but "one movement per request" designs routinely put the key on the request instead, and moving it afterwards means the batch era's duplicates are already in the ledger | `[R7 §6 12]`, `F-092` |
| **IRR-50** | **`whb_outbox`** with a monotonic cursor, emitting at **billable granularity** (receipt line, putaway, pick line, carton, task) + **`whb_outbox_subscriptions`** for out-of-process consumers | `whb_outbox`, `whb_outbox_subscriptions` | base | **PNR-1** | **UB** | Granularity is the unbackfillable half: **per-line handling billing — how every audited 3PL prices — is permanently unavailable for the past** if the outbox emitted at document granularity. The subscription table is the cheap half now and a redesign later: it is one table today, and after three in-process subscribers exist it is a redesign of all three. This is **net-new infrastructure either way** — `grep -ril outbox` across `platform`, `accounting-base`, `accounting`, `dealer`, `automotive`, `services`, `assets` returns **0 files** | `[R4 §5.4 5]`, `F-012`, `F-086`, `[R7 §6 17]` |
| **IRR-51** | The **daily stock position snapshot job runs from v1** | `whb_stock_position_snapshots` + a scheduled job | base | **PNR-3** | **UB** | Occupancy on each past day cannot be cheaply reconstructed from a movement ledger — the query is a running balance per position per day over the whole history, and it is exactly the query that is too slow to run on demand, which is why the snapshot exists. So **storage billing, ageing, days-on-hand and obsolescence all begin on the day the job was switched on**, and a client's dispute about last month is unanswerable. The job is trivial; the *start date* is the irreversible part | `T-072`, `F-016` |
| **IRR-52** | **`count_snapshot_quantity`** on count lines | count line table | `warehouse` · V510000–V519999 | **PNR-3** | **UB** | Variance computed against a **live** quantity is not reproducible: the book figure at count time is gone the moment the next movement posts, so the variance on last quarter's count cannot be re-derived and the count cannot be defended. One column, captured at freeze | R5 row 23, `S-091`, `F-076` |
| **IRR-66** | **The outbox event schema**: `PC-36`'s dimensions as typed columns and `event_version` on every event, event codes from `whb_event_types` (registry 17), `accepted_event_version` on each subscription, and **no opaque payload in v1** | `whb_outbox`, `whb_event_types`, `whb_outbox_subscriptions` | base · `V500040` | **the first event emitted** — `V500040` | **one-way from the first event** | An emitted event is stored and replayed by consumers the warehouse does not control. A dimension missing from an event already emitted cannot be added to it: `PC-38` says adding a dimension to an existing event code is not additive. An event with no version cannot be evolved without breaking every subscriber at once. And a `TEXT` payload is the opaque blob `PC-37` forbids, which a consumer parses privately and the producer can then never change | `RL-002`, `PC-36`, `PC-37`, `PC-38`, `IRR-50` |

### Block H — Masters, statutory identity and platform (`IRR-53` … `IRR-61`, `IRR-63` … `IRR-65`)

| # | What must exist | Table · column | Module · band | Deadline | Class | The argument | Sources |
|---|---|---|---|---|---|---|---|
| **IRR-53** | **Lot attribute columns**: `manufacture_date`, `expiry_date`, `best_before_date`, `use_by_date`, `retest_date`, `country_of_origin`, `mrp`, `net_content`, `supplier_lot`, `parent_lot_id` | `whb_lots` | base | **PNR-3** | **UB** | **Every one of these is printed on a pack that has already been put away, and nobody will re-open cartons to backfill.** `best_before` and `use_by` must be separate columns because they are different legal facts with different dispositions. `parent_lot_id` is the sharpest: a lot split or merge not recorded when it happened is **invisible forever**, so genealogy has a hole that no later work can find, let alone fill | R5 row 17, `S-038`, `S-033`, `L-12` |
| **IRR-54** | **`transformation_id`** + transformation input/output tables | `whb_transformations` + input/output line tables | base | **PNR-3** | **UB** | A recall that must cross a kit or repack boundary needs the genealogy recorded **at the moment of transformation**. Nothing later can say which input lots went into which kit — the physical evidence is inside the kit. Kitting ships v1.1; the genealogy tables ship v1 because they are only populated by the act itself | R5 row 14, `S-008`, `L-12` |
| **IRR-55** | **Style / variant model** on the item — `dimension_1/2/3` + a size-scale concept | `whb_items` | base | **PNR-3** | **UB (data migration with judgement)** | Converting a year of flat SKUs into a style × size × colour matrix is a **data-migration project with human judgement in it**, not a schema change: nothing in the data says which flat SKUs were the same style. If apparel and footwear are not a target market, `DECISIONS.md` should say so explicitly rather than leave it to be discovered — it is the largest single addressable segment on the declined list | R5 row 24, `S-056` |
| **IRR-56** | **`epr_category`, `regulatory_class`, `is_catch_weight`, hazmat block** on the item | `whb_items` | base | **PNR-3** | **UB (economically)** | Classification of a live catalogue of 50,000 items is manual work **nobody funds** — so in practice the columns are added and stay null, which is worse than not having them because reports then look complete. Seeding them at item-creation time costs nothing. `is_catch_weight` is separately the switch that `IRR-35`'s columns key off | R5 row 27 |
| **IRR-57** | **`state_code`** on the warehouse **+ the dated `REGISTERED` link** to a platform branch — exactly one `REGISTERED` row in `whb_warehouse_branches` at every instant. The site's GSTIN, statutory series and legal entity are read through that branch, never copied onto the site: `whb_warehouses` has **no** `branch_id`, `tax_registration_id` or `legal_entity_id` (`D-14` item 2) | `whb_warehouses.state_code`, `whb_warehouse_branches` (`relationship_role_code = 'REGISTERED'`, `effective_from`, `effective_to`) | base · `V500012` | **PNR-1** | **UB** | Without them a historical transfer **cannot be classified as supply vs non-supply**, so it cannot be established whether a tax invoice was legally required — for a period whose return has already been filed. This is a filed-return exposure, not a report gap. `D-8` keeps the *rules* out of the core; `state_code` and the link are the *hooks*, and they are core. **The two scalars this row used to name were the wrong shape.** A `tax_registration_id` on the site is overwritten by the first re-registration, and every earlier movement then resolves to the new GSTIN. That overwritten history is exactly what this row exists to keep. Classification reads the link at `occurred_at`; the history itself is `IRR-64` | R5 row 19, `S-022`, `D-8`, `RG-001`, `D-14` |
| **IRR-58** | **`commingle_policy` + `dedicated_owner_id`** on locations | `whb_locations` | base | **PNR-1** | **RK** | Commingling is the economically correct default and the policy is the column. Without it you choose once, globally, between uneconomic bulk storage and an unsellable bonded or pharma client — and the choice is baked into every location row already created | `[R4 §5.4 11]`, `F-003` |
| **IRR-59** | **`owner_id` nullable on the carrier account** | `wh_carrier_accounts` | `warehouse` · V510000–V519999 | **PNR-3** | **RK** | *"Ship on the client's account"* is a standard 3PL contract clause. Nullable column now; a schema change plus a re-mapping of every existing account later | `[R4 §5.4 12]`, `F-036` |
| **IRR-60** | **Owner-scoped access grants** + **one** server-side resolver that every query goes through | `whb_owner_grants` + a single resolver bean | base | **PNR-1** | **RK** | Owner segregation enforced only in the UI leaks. It leaks through **an export, a statistics tile or a dropdown** — three surfaces that routinely bypass the list query. One resolver from v1 or the leak is found by a client. The platform's role model is global, so this is genuinely net-new: `grep -ril "tenant" platform/backend/src/main/java` → **0 files** (`OD-3`) | `[R4 §5.4 9]`, `F-004`, `T-073`, `OD-3` |
| **IRR-61** | **`on_behalf_of_actor_id`** on the audit event | platform audit table | **platform** · V1–V9999 | **PNR-3** | **UB** | Support sessions before the column exists are **indistinguishable from the customer's own actions**, which voids the audit claim retrospectively for that whole period. On day two of the first install, support is asked a question that needs the customer's data; the two available answers today are their password or a standing admin account, and the second silently destroys the trail. Platform's table, so it does not compete with warehouse engineers — and it is the identical defect accounting logged as `N-045`, so **fix it once, in platform** | R5 row 25, `S-092` |
| **IRR-63** | **Permission namespace reserved and `permission_dependencies` rows inserted**: `warehouse:movements:post` exists in v1; `logistics:*` reserved | `permissions`, `permission_dependencies` (**platform tables — `INSERT` rows, never `CREATE TABLE`**) | base migration writing platform tables | **PNR-3** | **RK** | A logistics user who dispatches a trip posts a stock movement. If that permission is invented in v2, **every existing role must be re-granted by hand** across every install. Reserving the string costs one seed row. The `CREATE TABLE` warning is not theoretical: `permission_dependencies` is platform's, created at `platform/…/V248__…:17-30`, and `dealer/…/V20501:10` is the vestigial second attempt that documents the mistake. Column names are `permission_id` and **`dependent_permission_id`** | `[R7 §6 25]`, `C-017` |
| **IRR-64** | **The site's registration history**: `whb_warehouse_branches` `REGISTERED` rows dated `[effective_from, effective_to)`, at most one at every instant (the exclusion; a site with none is refused when used, `D-14` item 8g), and **append-only once a posted movement stands in their range** (`I-23`). `whin_gstin_profile_branches` likewise: which branches a GSTIN covered, as principal or additional place of business, and since when | `whb_warehouse_branches`, `whin_gstin_profile_branches` | base · `V500012` (`I-23` in `V500037`); `warehouse-india` · `V540010` | **PNR-1** — `V500012`; `V540010` before the first challan | **UB** — unrecoverable from the first registration change | Every tax rule reads the `REGISTERED` link **at `occurred_at`**: the transfer's supply test, the Rule 56 account per registration, the statutory series. A history that was overwritten, or never kept, resolves every past movement to today's GSTIN. That silently restates filed periods. The history is written only by the act of changing, so nobody can later say which branch a site was registered under on a past date. The GSTIN half has the same shape: `branches.gst_number` is a mutable platform scalar with no dates, so *"which branches did this registration cover in Q4"* is lost the day a number is edited. A registration change is refused while the site holds stock under a different GSTIN, and whether that can ever be relaxed is `OD-19` | `RG-001`, `RG-002`, `RH-005`, `D-14`, `OD-19` |
| **IRR-65** | **Master-association history on the v1 junctions** (`D-14` item 1): counterparty tax registrations and addresses, **frozen onto the challan and the e-way bill** that used them; location custody (`IRR-30`); an item's category per scheme, read at `occurred_at` for costing; a lot's parties (manufacturer, packer, importer); a serial's identifiers | `whb_counterparty_tax_registrations`, `whb_counterparty_addresses`, `whb_location_user_assignments`, `whb_item_category_assignments`, `whb_lot_counterparties`, `whb_serial_identifiers` | base · `V500011`, `V500013`, `V500015`, `V500018` | **PNR-3** | **UB** | Each of these was a scalar that the next edit overwrites. Each records a fact observed at a moment: which of the recipient's per-state GSTINs a filed e-way bill used; who held the van when the stock left; which category, and therefore which cost method, applied when the layer was consumed; whose name was on the pack. An overwritten scalar keeps only the latest answer. The dated junction keeps every answer with its range, and the document keeps the one it filed | `RG-003`, `RG-004`, `RG-005`, `RG-006`, `RG-007`, `RG-021`, `D-14` |

**Row count check.** `grep -c '^| \*\*IRR-' docs/IRREVERSIBLE.md` → **67** ids present in the eight
blocks, of which **`IRR-18` is the retired placeholder**, leaving **66 populated rows**: 62 against 102
source rows, plus round 4's `IRR-64`…`IRR-67`.

---

## §3 — The deadline mechanism: exactly which migration is the point of no return

### 3.1 The trap, named — and it is already documented, in a sibling design set

Accounting hit this and wrote it down. Its immutability guard is deliberately generic: it diffs
`to_jsonb(OLD)` against `to_jsonb(NEW)` rather than enumerating columns, **so that a column added by
a later `ALTER TABLE` is protected the day it appears rather than the day someone remembers to
update the trigger** (`accounting/docs/DATA-MODEL.md:2746-2749`, the function body at `:2751-2794`).

That is the right design. It also has one consequence that is easy to miss and impossible to undo:

> `ALTER TABLE … ADD COLUMN` is DDL, so the trigger does not block it. `UPDATE` is DML, so the
> trigger **does**. Therefore **every column added after the immutability trigger ran is `NULL`
> forever on every row that already existed, and no backfill can ever set it** — the backfill is an
> `UPDATE`, and the `UPDATE` is refused, to every actor, including `ADMIN`.

Accounting's own set records the concrete instance rather than the principle, which is how you can
tell it was learned rather than theorised. `DATA-MODEL.md:309`:

> *"`acc_journals.book_id` must exist **before** `V600094`'s `to_jsonb`-diff immutability trigger,
> which protects later-added columns automatically — a `book_id` added afterwards is immutable on
> every existing row and can never be set, and a backfill is not available."*

**Warehouse has the identical mechanism, and it is mandatory here, not optional.** `DECISIONS.md`
`L-2` specifies three layers — *"one writer service with no update method, a `to_jsonb`-diff trigger
rejecting `INSERT` into a posted movement as well as `UPDATE`/`DELETE`, and no repository path"*.
The middle layer is the trap. `L-3` closes the last escape: *"'Edit' is never offered anywhere in
the product."*

The live precedent for the trigger *style* is `accounting-base/…/V600111__Create_acc_audit_events_and_the_append_only_hash_chain.sql`
— `acc_reject_audit_event_mutation()` at `:616-624`, attached `BEFORE UPDATE OR DELETE` at `:626-629`,
with the message *"append-only; % on event % is not permitted to any actor, including ADMIN.
Correction is a NEW event, never an edit."* The deferred-constraint-trigger mechanism warehouse needs
for `L-1` is in the same file at `:773-786` and `:811-815`, with the PostgreSQL rules recorded in the
comment (must be `AFTER`, must be `FOR EACH ROW`) — and the file itself notes that **this repository
had no prior `CREATE CONSTRAINT TRIGGER` at all** (`:773-777`).

### 3.2 The four gates

Warehouse does not have one point of no return. It has four, and they fire in this order. Every
`Deadline` cell in §2 names one of them.

| Gate | What it is | Why it is a gate | Class it closes |
|---|---|---|---|
| **PNR-1** | **The migration that creates `whb_stock_movements` and `whb_stock_movement_lines`** — task **`P0-02`**, in `V500000–V509999` | Every column on the ledger header or line must be in this `CREATE TABLE`, or in an `ALTER` that runs strictly before `PNR-2`. In practice: **put it in the `CREATE TABLE`.** An `ALTER` in the window between `PNR-1` and `PNR-2` is legal and is a code smell — it means the column was argued about after the table was designed | Everything on the ledger |
| **PNR-2** | **The migration that installs the `L-2` append-only trigger on the movement tables** | After this, `UPDATE` is refused to every actor. A column added later is `NULL` on every pre-existing row **forever**, with no backfill path. This is the hard, mechanical, dated gate — the one an engineer can point at | Converts everything still missing from `RK` to `UB` |
| **PNR-3** | **The first movement posted in any install** — go-live, or the first demo on customer data | Schema-permissive but truth-destroying. The column may still be addable and writable; the *historical observation* it was supposed to record was never made. Nobody re-opens cartons to backfill `country_of_origin`; nobody remembers what the moving average was on 31 March | Everything observational: `IRR-23`, `IRR-39`, `IRR-40`, `IRR-46`, `IRR-51`…`IRR-57`, `IRR-61`, `IRR-63`, `IRR-65` |
| **PNR-4** | **The migration that creates a unique index on a hot table** — `whb_stock_positions`, `whb_items`, `whb_serials` | Adding a member to a unique key after rows exist means backfilling a value, re-indexing, and touching every query, report, export and integration that joins on it. **Rows that merged under the narrower key cannot be un-merged** | `RK` on the key columns: `IRR-09`, `IRR-14`, `IRR-19` |

### 3.3 The correction that removes a whole table's worth of anxiety

**`whb_stock_positions` has no independent deadline.** `L-4` makes it a cache — *"a full rebuild
from `whb_stock_movements` reproduces every `whb_stock_positions` row exactly"* — so a member added
to its unique key after `PNR-4` is recovered by **dropping the index, adding the column, and
rebuilding from the ledger**, with a downtime window and no loss of truth.

That holds **if and only if the ledger line already carries the column.** Which is the entire reason
`IRR-06`, `IRR-10`, `IRR-12`, `IRR-13`, `IRR-14`, `IRR-15` and `IRR-17` are specified as *movement-line* rows in §2
and not as position rows.

> **State it once and act on it:** the position table's deadline is `PNR-1`, wearing `PNR-4`'s
> clothes. Do not spend review time defending `whb_stock_positions`; spend it defending
> `whb_stock_movement_lines`.

The same reasoning does **not** transfer to `whb_lots`, `whb_serials`, `whb_locations`, `whb_items`
or `whb_counterparties`. Those are masters, not caches: their rows are mutable, so a column is
technically addable and writable at any time — and their gate is therefore `PNR-3`, not `PNR-2`.
The loss is observational, not mechanical, and it is no less permanent for that.

### 3.4 Per-table: what the point of no return actually is

| Table | Gate that binds it | The migration to check before writing | Rows it carries |
|---|---|---|---|
| `whb_stock_movements` | **PNR-2**, and in practice **PNR-1** | `P0-02` creates it; the `L-2` trigger migration seals it. **These two should be the same migration** — see §3.5 | `IRR-02` `IRR-03` `IRR-04` `IRR-17` `IRR-21` `IRR-22` `IRR-24` `IRR-27` `IRR-28` `IRR-32` `IRR-41` `IRR-48` `IRR-62` |
| `whb_stock_movement_lines` | **PNR-2**, and in practice **PNR-1** | as above | `IRR-01` `IRR-06` `IRR-10` `IRR-11` `IRR-12` `IRR-13` `IRR-14` `IRR-15` `IRR-20` `IRR-24` `IRR-32` `IRR-34` `IRR-35` `IRR-36` `IRR-37` `IRR-38` `IRR-39` `IRR-42` `IRR-62` |
| `whb_stock_positions` | **none of its own** — inherits `PNR-1` from the line (§3.3) | the position `CREATE UNIQUE INDEX` migration; but the *real* check is the line's | `IRR-09`, plus the key members listed against the line |
| `whb_items` | **PNR-4** for the key; **PNR-3** for the attributes | the migration creating `uk(owner_id, sku)` | `IRR-19` `IRR-31` `IRR-55` `IRR-56`; `IRR-26` |
| `whb_item_identifiers` | **PNR-3** — the first scan | the identifier table's `CREATE TABLE` | `IRR-43` |
| `whb_locations` | **PNR-1** (referenced by every line) then **PNR-3** | the migration creating `whb_locations` + `whb_location_types` — **must precede `P0-02`**, because `IRR-05` requires virtual locations to exist before the first movement can balance | `IRR-05` `IRR-16` `IRR-29` `IRR-44` `IRR-58`; `IRR-26` |
| `whb_warehouses` | **PNR-1** | same migration set as locations — `V500012`, which also creates the `REGISTERED` link, so no site exists without one | `IRR-17` `IRR-57` (`state_code` only — `branch_id`, `tax_registration_id` and `legal_entity_id` are **not** columns; reversed 2026-09-10 by `D-14`) |
| `whb_warehouse_branches` · `whin_gstin_profile_branches` | **PNR-1** — every movement's classification reads the `REGISTERED` link, and `I-22` refuses a movement at an unregistered instant | `V500012`, with `whb_warehouses`, **before `P0-02`**; `I-23`'s append-only trigger in `V500037`; the GSTIN half in `V540010`, before the first challan | `IRR-57` `IRR-64` |
| The v1 association junctions — custody, category per scheme, lot parties, serial identifiers, counterparty addresses and tax registrations | **PNR-3** | each junction's `CREATE TABLE` (`V500011`, `V500013`, `V500015`, `V500018`) | `IRR-30` `IRR-65` |
| `whb_lots` | **PNR-3** | `whb_lots` `CREATE TABLE` | `IRR-53`; `IRR-13`'s FK target |
| `whb_serials` | **PNR-4** for `uk(item_id, serial_number)`; **PNR-3** otherwise | the serial table's unique index | `IRR-14` |
| `whb_lpns` | **PNR-3** for `received_at` | the LPN table's `CREATE TABLE` | `IRR-15` |
| `whb_reservations` | **PNR-1** — the holder quad must exist before the first reservation | the reservation table's `CREATE TABLE` | `IRR-45` |
| `whb_owners` · `whb_owner_types` | **PNR-1** — must precede `P0-02`, because `IRR-06` is `NOT NULL` | the owner tables' `CREATE TABLE` | `IRR-06` `IRR-07` `IRR-60` |
| The thirteen catalogues (§5) | **PNR-1** for the seven the ledger FKs to; **PNR-3** for the rest | each catalogue's `CREATE TABLE`; **plus** the `WarehouseBaseCouplingTest` assertion that none of the thirteen carries a `CHECK (… IN (…))` | `IRR-07` `IRR-27` `IRR-28` `IRR-29` `IRR-31` `IRR-32` `IRR-33` `IRR-10` |
| `whb_outbox` · `whb_outbox_subscriptions` | **PNR-1** for granularity; **PNR-3** for the subscription table | the outbox `CREATE TABLE` (`V500040`), which also fixes the event schema and the partitioning | `IRR-50` `IRR-66` `IRR-67` |
| `whb_stock_periods` | **PNR-1** — `IRR-22` is `NOT NULL` on the movement | the period table's `CREATE TABLE`, **before `P0-02`** | `IRR-22` |
| `whb_stock_position_snapshots` | **PNR-3** — the job's start date | the snapshot table, partitioned at `CREATE` (`V500045`), + the scheduled job | `IRR-51` `IRR-67` |
| `wh_*` document headers (receipt, order, shipment, count) | **PNR-3** | each document's `CREATE TABLE` in `V510000–V519999` | `IRR-23` `IRR-52` `IRR-59` |
| platform `permissions` / `permission_dependencies` / audit | **PNR-3** | the base migration that `INSERT`s into them — **never a `CREATE TABLE`** (`C-017`) | `IRR-61` `IRR-63` |

**Ordering consequence, stated because it is the thing that gets it wrong:** six tables must be
created **before** `P0-02`, because `whb_stock_movement_lines` carries `NOT NULL` foreign keys into
them — `whb_owners`, `whb_locations` (+ `whb_location_types`), `whb_warehouses`, `whb_items`,
`whb_stock_periods`, and the seven ledger-referenced catalogues. `P0-02` is therefore **not** the
first warehouse migration; it is roughly the tenth. Anyone who plans `P0-02` as migration one will
discover this at the first `REFERENCES` clause and will be tempted to make the FKs nullable. Do not.

### 3.5 One recommendation, and it is the cheapest insurance in the plan

> **Install the `L-2` append-only trigger in the *same migration* that creates the movement tables.**
> Collapse `PNR-1` and `PNR-2` into one file.

The gap between them is the only window in which a column can be added and backfilled — and a window
that exists will be used, quietly, by someone who does not know what it costs. Accounting kept them
apart (`V600090`/`V600094`) and paid for it with a documented near-miss on `acc_journals.book_id`
(`DATA-MODEL.md:309`, `:3307`). Closing the window converts a *discipline* into a *mechanism*, which
is the whole argument of this document applied to itself.

If they must be separate migrations, then **no migration may run between them**, and the migration
number gap must be zero, so that `V50000n` and `V50000n+1` are visibly a pair.

### 3.6 The instruction to put in front of every migration

Copy this into the header comment of every `V5*` migration file, and into the phase's task file:

```
-- BEFORE WRITING THIS MIGRATION:
--   1. Read docs/IRREVERSIBLE.md §2. If this migration creates or alters whb_stock_movements,
--      whb_stock_movement_lines, whb_stock_positions, whb_items, whb_locations, whb_lots,
--      whb_serials, whb_reservations or any of the thirteen catalogues, every row in §2 that
--      names that table must be present in THIS file or in one that already ran.
--   2. Is this migration at or after PNR-2 (the L-2 append-only trigger)? If yes, no column
--      added from here on can ever be backfilled. Stop and re-read §2.
--   3. Does this migration add a CHECK (x IN (...)) to any of the thirteen columns in
--      docs/IRREVERSIBLE.md §5? If yes, it is wrong. Use a catalogue row.
--   4. Is the migration number inside this module's band (DECISIONS.md D-2) and owned by
--      exactly one task?
```

And, because a checklist nobody runs is decoration, the same four questions are assertions in
`WarehouseBaseCouplingTest` (R7 §4.4, layer 1) — items 2, 3 and 4 are mechanically checkable and
item 1 is checkable for the subset of §2 rows that name a literal `table.column`.

---

## §4 — The v1 schema commitments, table by table

**What this section is for.** §2 argues *why*. This section is the thing a builder diffs their
`CREATE TABLE` against, so that "we don't need this yet, it's a v2 feature" cannot delete a column
whose *feature* is v2 and whose *column* is v1. The **Feature ships** column is deliberately loud
about that: about half of these columns have no v1 screen at all.

**Two conventions.**

- **Precision is `OD-7` and is not settled.** `DECISIONS.md` recommends adopting accounting's
  resolved set *verbatim and by citation* — `accounting/docs/DATA-MODEL.md:2443-2453`, §5.1: ledger
  and document amounts `DECIMAL(19,4)`, quantities `DECIMAL(18,4)`, **per-unit** figures
  `DECIMAL(19,6)`, percentages and ratios `DECIMAL(9,6)`, exchange rates `DECIMAL(19,8)`, with two
  normative tie-breaks (`unit_*` beats `value`/`*_amount`; `*_percent` beats any reading of "rate").
  Types below follow that recommendation. **They are not authoritative until `OD-7` is closed** —
  note in particular that R4 §3.3 proposes `numeric(18,6)` for `unit_cost` and `numeric(18,8)` for
  the conversion factor, which the accounting set would make `DECIMAL(19,6)` and a `*_factor`
  question `OD-7` has not answered.
- **`—` in the Feature column** means the column is load-bearing in v1 itself.

### 4.1 `whb_stock_movements` — the ledger header

| Column | Type | Null | Feature ships | Why it is v1 | §2 row |
|---|---|---|---|---|---|
| `id` | UUID PK | no | — | — | — |
| `company_id` | UUID FK | **no** | v1 (multi-entity: v2 India) | Cross-GSTIN transfers; a GST return over guessed entities is a filing error | `IRR-17` |
| `warehouse_id` | UUID FK | **no** | — | `sequence_no` is gapless *per warehouse*; adding the axis later renumbers history | `IRR-17` |
| `movement_type_code` | VARCHAR(40) FK → `whb_movement_types` | **no** | — | A **row**, never an enum. An adapter needing `PDI_CONSUME` must not need a base release | `IRR-27` |
| `source_system` | VARCHAR(40) FK → `whb_source_systems` | **no** | — | Half of the idempotency key; partitions the key namespace across producers | `IRR-04` `IRR-24` `IRR-28` |
| `source_document_type` | VARCHAR(40) FK → `whb_document_types` | **no** | — | `SALES_ORDER` · `TRIP` · `JOB_CARD` · `POS_SHIFT` · `WORK_ORDER` | `IRR-24` `IRR-28` |
| `source_document_id` | VARCHAR(100) | **no** | — | Deliberately `VARCHAR`, not UUID: an external system's id is not ours | `IRR-24` |
| `source_document_line_no` | INTEGER | yes | — | A partially reversed multi-line source document cannot otherwise be reconciled line by line | `IRR-24` |
| `idempotency_key` | VARCHAR(200) | **no** | v1.1 (offline) | Unique per `source_system` across months through `whb_movement_idempotency_keys` (`PRIMARY KEY (source_system, idempotency_key)`); the ledger's own `uk(source_system, idempotency_key, occurred_at)` is a per-partition backstop. **Never server-generated** | `IRR-04` |
| `payload_hash` | CHAR(64) | **no** | — | Distinguishes "retry" from "different payload, reused key". Without it the conflict rule cannot exist | `IRR-04` |
| `sequence_no` | BIGINT | **no** | v1.1 (outbox), v2 (billing) | Gapless per warehouse. Cannot be started retroactively | `IRR-03` |
| `prev_payload_hash` | CHAR(64) | yes | v2 (tamper evidence) | A chain begun in v2 proves nothing about v1 | `IRR-03` |
| `occurred_at` | TIMESTAMPTZ | **no** | — | **Producer-supplied** business time | `IRR-21` |
| `occurred_at_tz_offset` | SMALLINT (minutes) | yes | v1.1 (multi-site) | A UTC instant does not say which local day it was, and every statutory register is a local-day register | `IRR-21` |
| `recorded_at` | TIMESTAMPTZ | **no** | — | Server clock. The delta from `occurred_at` is the only latency diagnostic that exists | `IRR-21` |
| `posting_date` | DATE | **no** | — | The accounting date. Diverges from `occurred_at` at a period boundary and at a client's cycle | `IRR-21` |
| `period_id` | UUID FK → `whb_stock_periods` | **no** | v1 (close), v2 (3PL billing) | Rows posted before periods exist belong to no period, so the first close has an un-closeable opening set | `IRR-22` |
| `reversal_of_movement_id` | UUID, **bare** — no `REFERENCES` on a partitioned table (`DATA-MODEL.md` §1.9, `MPR-OPEN-08`) | yes | — | If v1 permits `UPDATE`, the corrections are already invisible by the time this arrives | `IRR-02` |
| `reversed_by_movement_id` | UUID, **bare** (as above) | yes | — | Denormalised for *"is this still live"* | `IRR-02` |
| `is_reversed` | BOOLEAN | **no** | — | — | `IRR-02` |
| `actor_type` | VARCHAR(30) | **no** | v1 (`USER`), v1.1 (`DEVICE`), v2 (`INTEGRATION`) | *"Who moved this"* is the first audit question and it is not always a person | `IRR-48` |
| `actor_user_id` | UUID FK → `users` | yes | — | — | `IRR-48` |
| `device_id` | VARCHAR(100) | yes | v1.1 (RF), v2 (RFID) | Diagnosing a mis-scanning device retroactively is impossible without it | `IRR-48` |
| `reason_code_id` | UUID FK → `whb_reason_codes` | yes | — | Free text in v1 is a categorical dimension that can never be reported on | `IRR-32` |
| `handover_id` | UUID | yes | v1.1 (GL seam) | Pre-integration movements have no marker, so *"does stock tie to the GL"* is unanswerable for the audited period | `IRR-41` |
| `posting_status` | VARCHAR(20) | **no** | v1.1 | `NOT_APPLICABLE` · `PENDING` · `POSTED` · `REJECTED`. Default `NOT_APPLICABLE` | `IRR-41` |
| `approval_status` · `approved_by` · `approved_at` | — | yes | v1 (scrap), v1.1 (write-down) | For movement types with `requires_approval`. **`approval_status` carries the lifecycle — there is no header `status` column** (`MPR-OPEN-05`): `NULL`/`APPROVED` has ledger effect; `PENDING` has none and is the only mutable header; `REJECTED`/`WITHDRAWN` are terminal | `IRR-27` |
| `posted_at` | TIMESTAMPTZ | **no** | — | — | — |
| `notes` | TEXT | yes | — | — | — |
| audit columns | `created_by`, `created_at`, `updated_by`, `updated_at`, `version` | — | — | House convention. `updated_*` exist and are **never written after post** | `IRR-02` |

**Deliberately not on the header** — stated so it is not "discovered" as a gap: `owner_id`
(per line, `IRR-06`), `item_id`, `quantity`, `location_id` (a movement is not a single line), any
JSONB payload, any carrier / AWB / trip / vehicle (`source_document_type = 'TRIP'` carries it), any
price / customer / tax, any billing charge code, and any free-text `reference`.

### 4.2 `whb_stock_movement_lines` — the ledger line

> **Read this before the table.** `D-4` and `L-1` make a movement **two or more signed lines that
> conserve quantity**. A line therefore carries **one** `location_id`, **one** `stock_status_code`,
> **one** `owner_id`, **one** `lpn_id`, **one** `duty_status`, and a **signed** `base_quantity`.
> R4 §3.3 and R5 row 20 both propose `from_location_id` / `to_location_id` (and R4 additionally
> `from_stock_status_code`, `from_lpn_id`/`to_lpn_id`) **on one line**. Under `D-4` that is the
> from/to row — the exact shape `IRR-01` exists to prevent — and `DECISIONS.md` wins. See §7.1.
> The irreversible *content* of both proposals survives intact: virtual locations must exist so no
> side is ever absent (`IRR-05`), and status must be on the line and in the position key (`IRR-10`). A
> `STATUS_CHANGE`, an `OWNER_CHANGE` and a putaway are each **two lines**, not one row with two ends.

| Column | Type | Null | Feature ships | Why it is v1 | §2 row |
|---|---|---|---|---|---|
| `movement_id` · `line_no` | UUID FK · INTEGER | no | — | — | — |
| **`owner_id`** | UUID FK → `whb_owners` | **no** | v1 (house), v1.1 (consignment), v2 (3PL) | **The single most expensive column to add late in the design.** No rule recovers whose a unit was | `IRR-06` |
| `item_id` | UUID FK → `whb_items` | no | — | — | — |
| `location_id` | UUID FK → `whb_locations` | **no** | — | Includes virtual locations. `NOT NULL` is the whole of `L-1` | `IRR-01` `IRR-05` |
| `quantity` | DECIMAL(18,4) | no | — | **Signed.** No `CHECK (quantity <> 0)` — value-only movements need zero | `IRR-01` `IRR-37` |
| `uom_code` | VARCHAR(20) FK → `whb_uoms` | **no** | — | As entered by the producer | `IRR-34` |
| `base_uom_code` | VARCHAR(20) FK | **no** | — | — | `IRR-34` |
| `base_quantity` | DECIMAL(18,4) | **no** | — | Signed, computed at post. `L-1` sums this | `IRR-34` |
| `conversion_factor_used` | DECIMAL(18,8) *(`OD-7`)* | **no** | — | **Frozen at post.** Re-deriving from today's factor silently restates last year | `IRR-34` `L-7` |
| `secondary_quantity` · `secondary_uom_code` | DECIMAL(18,4) · VARCHAR(20) | yes | **v1.1–v2** (catch weight) | The weights were never captured; there is nothing to backfill from | `IRR-35` |
| `lpn_id` | UUID FK → `whb_lpns` | yes | **v1.1–v2** (LPN handling) | Anniversary storage billing has no other anchor | `IRR-15` |
| `lot_id` | UUID FK → `whb_lots` | yes | v1 (batch), v1.1 (FEFO) | A recall is a question about the past | `IRR-13` |
| `serial_id` | UUID FK → `whb_serials` | yes | v1 | — | `IRR-14` |
| `stock_status_code` | VARCHAR(40) FK → `whb_stock_statuses` | **no** | v1 (QC hold), v1.1 (grading) | Otherwise condition and place are permanently conflated. **Bonded is not a status**: the regime is `duty_status`, and a customs hold is a `wh_hold_types` row (`RL-001`) | `IRR-10` |
| `condition_code` | VARCHAR(40) FK | yes | **v1.1** | Condition is an axis **separate** from workflow step; merged, the single column silently drops one | `IRR-11` |
| `duty_status` | VARCHAR(40) FK → `whb_duty_statuses` | **no** | **v2** (`warehouse-india`) | Default `DOMESTIC`, the only value base seeds. Bonded and duty-paid stock of one SKU must never merge — customs offence, not data quality | `IRR-12` |
| `read_point_location_id` · `biz_location_id` | UUID FK · UUID FK | yes | **v2** (EPCIS) | Where the scan happened and where the goods then were are different facts | `IRR-20` |
| `unit_cost` | DECIMAL(19,6) *(`OD-7`)* | yes | v1 (receipt cost), v1.1 (valuation) | — | `IRR-36` |
| `cost_currency_code` | CHAR(3) | yes | **v2** (multi-currency) | Retro-fitting currency onto a cost history is guessing | `IRR-36` |
| `extended_cost` | DECIMAL(19,4) | yes | v1.1 | — | `IRR-36` |
| `cost_basis` | VARCHAR(30) | **no** | v1.1 (GL seam), v2 (3PL) | `ACTUAL`·`STANDARD`·`AVERAGE`·`INFORMATIONAL`·`ZERO_BAILMENT`. Decided downstream = a year of wrong journals | `IRR-36` `L-14` |
| `moving_average_after` | DECIMAL(19,6) | yes | v1.1 (AVCO) | Without the snapshot, the 31 March cost is not reproducible | `IRR-39` |
| `cost_layer_id` | UUID | yes | **v1.1** (FIFO) | An AVCO-only v1 has nothing to build layers from later | `IRR-38` |
| `tax_classification_code` · `tax_classification_scheme` | VARCHAR(20) · VARCHAR(20) | yes | **v2** (India) | Reading the item master later gives the *new* code for *old* documents. Named for no one scheme (`RL-008`) | `IRR-42` |
| `reason_code_id` | UUID FK | yes | — | Line-level override of the header reason | `IRR-32` |
| `source_line_ref` | VARCHAR(100) | yes | — | The producer's own line identity, distinct from the header's `source_document_line_no` | `IRR-24` |
| `expiry_date_override` · `qc_result_code` | DATE · VARCHAR(30) | yes | v1 | Where the producer knows an expiry the lot does not yet carry; receipts arriving already inspected | — |
| audit columns | — | — | — | — | `IRR-02` |

**Attributes side table `whb_movement_line_attributes`** — `(movement_line_id, occurred_at, attribute_key_id
FK → whb_attribute_keys, value_string, value_number, value_date, value_boolean)`: **four typed value
columns**, as `DATA-MODEL.md` specifies. It is not one text value with a type tag, which is JSON
smuggled into a text column at a smaller scale. The table is append-only from `V500030`, so its shape
is `PNR-1` (`RL-007`). **Registered keys only. No JSONB** — CLAUDE.md's
DATABASE CONVENTIONS forbid it, and an unregistered key is a column nobody can filter, export or
index. The prior WMS set violated this (`metadata JSONB DEFAULT '{}'::jsonb` on `wms_items`), which
is why it is stated rather than assumed.

### 4.3 `whb_stock_positions` — the cache

`L-4`: a full rebuild from the ledger reproduces every row **exactly**, proved nightly with a drift
alert. Therefore this table has **no independent deadline** (§3.3) — but its *unique key* is `L-5`
and every member of it must be on the line above.

| Column | Type | Feature ships | Note |
|---|---|---|---|
| `company_id` · `owner_id` · `item_id` · `location_id` · `lot_id` · `serial_id` · `lpn_id` · `stock_status_code` · `duty_status` | the **`L-5` unique key**, nine members, `NULLS NOT DISTINCT` | v1 → v2 per member | Nullable members need `NULLS NOT DISTINCT` or the cache inserts a fresh row per movement and the drift alert fires forever — the exact defect `accounting/docs/DATA-MODEL.md:507` records against the `COALESCE`-sentinel alternative used at `accessories/…/V30130__…:40-46` |
| `quantity_on_hand` | DECIMAL(18,4) | — | Signed sum of `base_quantity` |
| `quantity_reserved` | DECIMAL(18,4) | — | **Derived from `whb_reservations`, never incremented in place** (`IRR-45`) |
| `quantity_available` | DECIMAL(18,4) | — | `L-6`: may never go below zero. Physical on-hand may go negative **only** where an explicit per-item × per-site policy allows it |
| `secondary_quantity` | DECIMAL(18,4) | v1.1 | `IRR-35` |
| `last_movement_at` · `last_count_date` | TIMESTAMPTZ · DATE | — | — |
| `version` | BIGINT | — | Optimistic lock. Accessories has **no** `@Version`, **no** `@Lock` and **no** `CHECK (quantity_on_hand >= 0)` anywhere (`C-024`) — three absences, and the code comment names the race it produces (`InventoryStockAdjustmentService.java:63-65`) |

### 4.4 `whb_items`

| Column | Feature ships | Note | §2 row |
|---|---|---|---|
| `owner_id` + `sku`, **`uk(owner_id, sku)`** | v1 key; v2 second client | A global unique SKU is a one-way door | `IRR-19` |
| `code` (stable string key) | — | What makes a module boundary a refactor, not a data migration | `IRR-26` |
| `item_type_code` FK → `whb_item_types` | — | Registry, not enum | `IRR-31` |
| `base_uom_code`, per-item conversions in `whb_item_uom_conversions` | — | Conversion belongs on the **item**, not on the UoM master | `IRR-34` |
| `lot_control_mode`, `serial_control_mode` | v1 | **Modes, not booleans** — `NONE`/`AT_RECEIPT`/`AT_ISSUE`/`FULL` | `IRR-14` |
| `is_catch_weight` | **v1.1** | The switch `IRR-35`'s columns key off | `IRR-56` |
| `tax_classification_code` (HSN/SAC in India — a string) | **v2** | Snapshotted onto the line at post, with its scheme (`IRR-42`) | `IRR-42` |
| `dimension_1_id` · `dimension_2_id` · `dimension_3_id` + size scale | **v2** (apparel) | Retrofitting a flat SKU catalogue into a matrix is a judgement project, not a migration | `IRR-55` |
| `epr_category` · `regulatory_class` · `hazmat_*` block | **v2** | Classifying 50k live items manually is work nobody funds | `IRR-56` |
| `shelf_life_days`, `min_remaining_shelf_life_days` | **v1.1** (FEFO) | Cheap columns; the rule is v1.1 | R2 `T-028` |
| item status as **four independent facts** (`is_stocked`, `is_purchasable`, `is_sellable`, `is_active`), not one enum | v1 | R2 `T-020`; deactivation must not orphan stock (`T-029`) | — |
| audit + `version` | — | — | — |

`whb_item_identifiers` — `(item_id, owner_id, identifier_type, identifier_value, normalised_value,
counterparty_id, channel_id, uom_code, pack_quantity, is_primary)`, `uk` on `(identifier_type,
normalised_value, owner_id, counterparty_id, channel_id) NULLS NOT DISTINCT`. The key is **not** global:
a supplier part number is unique per supplier and an EAN per owner, and a scan matching two candidates
is `AMBIGUOUS_IDENTIFIER` (`RL-005`). `owner_id` is denormalised from the item; `identifier_type` comes
from the `IDENTIFIER_TYPE` code list. **`uom_code` + `pack_quantity` are v1**
(`IRR-43`): without them a case scan books one *each*. This table is also the channel-listing table
(`F-006`) and the multiple-barcodes-per-item table (`T-022`).

### 4.5 `whb_locations` and `whb_warehouses`

| Column | Feature ships | Note | §2 row |
|---|---|---|---|
| `parent_location_id` + `location_type_code` FK | — | A **hierarchy**, not four VARCHARs. Reparenting later silently rewrites historical zone reports | `IRR-16` `IRR-29` |
| `code` (stable string key) | — | — | `IRR-26` |
| custody — `whb_location_user_assignments` (dated; `CUSTODIAN` · `DRIVER` · `HELPER`), **not** an `assigned_user_id` column | **v1.1** (van stock) | Without it van stock is a separate table and a separate reconciliation problem. As a scalar it forgets who held the stock when it left (`RG-004`) | `IRR-30` |
| `commingle_policy` + `dedicated_owner_id` | **v2** (3PL) | Otherwise: uneconomic bulk storage, or an unsellable bonded/pharma client | `IRR-58` |
| `gln` | **v1.1–v2** (GS1) | Four nullable columns now; four migrations plus an integration re-map later | `IRR-44` |
| capacity: `max_weight`, `max_volume`, `max_units` — **and enforcement** | v1 | Accessories stores all three and enforces none (`V30033:23-24`, `V30017:19`; no validation service reads them) | `C-029` |
| `whb_warehouses.state_code` | **v1** (wave 1 — the India link validator) | The site's own address fact, the two-digit GST state code. `warehouse-india` refuses a `REGISTERED` link whose GSTIN is from another state. Without it, and without the link below, a historical transfer cannot be classified as supply vs non-supply, for a filed period | `IRR-57` |
| `whb_warehouse_branches` — dated links to platform branches, **exactly one `REGISTERED` at every instant**. The site has no `branch_id`, `tax_registration_id` or `legal_entity_id` | v1 | **Reversed 2026-09-10 by `D-14`.** This row said *"one branch, one GSTIN; do not repeat accessories' many-to-many junction"*. The many-to-many shape is right; what accessories' `accessory_warehouse_branch` (`V30018:8`) lacks is a role and dates. The `REGISTERED` link at `occurred_at` gives the site's GSTIN, series and tax attribution. `SERVING`, `FULFILMENT` and `RETURNS` links grant visibility and draw stock. `branches.branch_type` still admits `'WAREHOUSE'` (`platform/…/V149:61,63`), but such a branch is created only for a site that is itself a place of business no existing branch carries (`RH-003`) | `IRR-57` `IRR-64` · `RG-001`; supersedes `C-016` `C-030` (§7.1) |

`whb_location_types` seed — `BIN`, `BULK`, `STAGING`, `RECEIVING`, `SHIPPING`, `DOCK`,
**`IN_TRANSIT`**, **`MOBILE`**, **`VEHICLE`**, **`TRAILER`**, `CUSTOMER`, `SUPPLIER`, `SCRAP`,
`ADJUSTMENT_OFFSET`, `PRODUCTION`, `JOB_WORKER` — with `is_physical`, `is_stock_holding`,
`is_virtual_counterparty`, `is_mobile`, `is_transit`, `allows_mixed_owner`, `requires_assigned_user`.
**No `CHECK`.**

### 4.6 `whb_lots`, `whb_serials`, `whb_lpns`

| Table | v1 columns whose feature is later | §2 row |
|---|---|---|
| `whb_lots` | `owner_id` (`IRR-06`); `manufacture_date`, `expiry_date`, **`best_before_date` and `use_by_date` as separate columns**, `retest_date`, `country_of_origin`, `mrp`, `net_content`, `supplier_lot`, **`parent_lot_id`** — features v1.1–v2, columns v1, because every one is printed on a pack already put away and `parent_lot_id` records a split/merge that is otherwise invisible forever | `IRR-53` `IRR-06` |
| `whb_serials` | `owner_id`; **`uk(item_id, serial_number)`** not a global unique; a current-state column (location, status, owner); a second identity key for IMEI-shaped items (v1.1) | `IRR-14` `IRR-06` |
| `whb_lpns` | `owner_id` — the custodian/label owner, not the owner of every unit on the pallet (`RG-022`); **`received_at`** (v2 feature, v1 column — anniversary storage billing has no other anchor); `parent_lpn_id` for nesting; `status` (`OPEN`/`CLOSED`) | `IRR-15` `IRR-06` |

### 4.7 `whb_reservations`

`(id, company_id, owner_id, item_id, location_id, lot_id, serial_id, lpn_id, stock_status_code,
quantity, base_quantity, uom_code, holder_system, holder_document_type, holder_document_id,
holder_line_no, reservation_type, priority, expires_at, released_at, release_reason_code_id,
created_by, created_at)`.

- The **holder quad** and `expires_at` are `IRR-45` and they are v1 even though the first non-warehouse
  holder (a logistics trip) is v3. Without them base cannot answer *"release everything trip X held"*,
  and orphaned reservations reduce availability forever with no way to find them.
- `released_at` rather than a delete, following the best occupancy model in this repo:
  `pdi_storage_slot_assignments` keeps released rows and enforces exclusivity with **partial unique
  indexes** — `dealer/…/V20735__…:8`, `:57-59`, `:62-64` — and derives occupancy at read time rather
  than caching it (`PdiYardStorageLocationService.java:67`). Copy that shape (`C-033`).

### 4.8 The catalogues — one shape, thirteen tables

Every one of the thirteen in §5 has this shape, and the shape is copied verbatim from a live,
commented precedent:

```
<name> (
  id, [company_id],
  code           VARCHAR(40)  NOT NULL,               -- NO CHECK CONSTRAINT, EVER
  name           VARCHAR(255) NOT NULL,
  owning_module  VARCHAR(30)  NOT NULL,               -- OPAQUE STRING, NOT AN FK
  is_system      BOOLEAN      NOT NULL DEFAULT false, -- system rows undeletable
  sort_order     INTEGER      NOT NULL DEFAULT 0,
  <behaviour columns: typed booleans / small closed sets describing HOW the row behaves>,
  is_active, status, version, created_at, updated_at, created_by, updated_by,
  uk(code) or uk(company_id, code)
)
```

**`owning_module` is an opaque string and not a foreign key.** That is the accounting precedent
(`accounting-base/…/V600001__…:234-235`: *"map, not mirror. source_module is an opaque string"*) and
it is what lets an adapter register a row from its own migration without base learning the adapter
exists (`D-11`).

### 4.9 The three external-ref tables

`whb_item_external_refs`, `whb_counterparty_external_refs`, `whb_location_external_refs`. Shape
verbatim from `accounting-base/…/V600001__Create_acc_companies_and_external_refs.sql:204-229`:

```
whb_item_external_refs (
  id, item_id UUID NOT NULL,
  source_module VARCHAR(30)  NOT NULL,      -- opaque; e.g. 'ACCESSORIES', 'DEALER', 'SERVICES'
  external_id   VARCHAR(100) NOT NULL,      -- a code or a UUID rendered as text
  is_active, status, version, audit columns,
  CONSTRAINT uk_whb_item_external_refs_source_external UNIQUE (source_module, external_id),
  FK item_id -> whb_items(id) ON DELETE RESTRICT
)
```

- `uk(source_module, external_id)` — **map, not mirror.** One external identity resolves to at most
  one warehouse item, which is exactly what `D-9`'s double-count detection needs.
- **No index on `item_id`.** The accounting precedent states why (`:231-233`): the query this table
  exists to serve is *"which warehouse item is source X's item Y"*, which the unique key seeks
  directly.
- `D-9` makes `whb_item_external_refs` **mandatory in v1** with an `ACCESSORIES` row per
  dual-stocked SKU. See [`COEXISTENCE.md`](COEXISTENCE.md) §5, `M1`.

---

## §5 — The thirteen vocabularies that must be open on day one

**Why they are on an irreversibility list at all.** Closing a vocabulary is not a data loss, so it
is not `UB`. It is a **re-keying migration plus a service-layer change in every consumer**, and — the
part that makes it worse than an ordinary re-key — a `CHECK` widened by `DROP` + `ADD` **silently
discards any value another module added**. So the cost is not just weeks; it is weeks *and* a
regression nobody notices until a second module's rows start failing to insert.

**The precedent that works**, live and self-commenting — `accounting-base/…/V600002__Create_acc_reason_codes.sql:22-26`:

> *"`context` carries NO CHECK constraint, deliberately. It is a CATALOGUE, not an enum: p1-20 adds
> an `ORDER_SHORT_CLOSE` context and p2-10 an interest-waiver context, and both must be a seed
> `INSERT` rather than an `ALTER` of a `CHECK` in accounting-base."*

**The counter-precedent**, equally live, three migrations deep: `widget_definitions.chk_module` has
been dropped and rebuilt **three times** — `('platform','dealer','shared')` at
`platform/…/V234__Create_dashboard_system_tables.sql:36` → five at `V276:10` → seven at `V557:18` —
and **still admits neither `warehouse` nor `logistics`**. Same story for
`global_settings.chk_global_setting_module`: five at `V337:42`, seven at `V553:15`.

**And the one the prior warehouse product actually broke**, which is why this section is not
theoretical: `zone_type` and `location_type` `CHECK` constraints *"dropped and recreated with
**completely different enum value sets**"* 36 versions after creation —
`classic-issues/warehouse-core/docs/WAREHOUSE_CORE_ISSUES.md:87`, naming `V200006`'s
`PUTAWAY_STAGING`/`BULK_STORAGE`/`FORWARD_PICK` replaced wholesale by `V200042`'s
`PICK_FORWARD`/`PICK_RESERVE`/`COLD`/`FROZEN`. Every historical row's type then means something else.

| # | Vocabulary | Registry table | Behaviour columns — what makes it a table rather than a list | Gate | v1 seed |
|---|---|---|---|---|---|
| 1 | **Movement type** | `whb_movement_types` | `direction`, `is_financial`, `cost_basis_default`, `reversal_type_code`, `requires_approval`, `requires_reason`, `affects_availability`, `is_stock_bearing`, `is_billable_event` | **PNR-1** | `RECEIPT`, `ISSUE`, `TRANSFER_DEPART`, `TRANSFER_ARRIVE`, `TRANSIT_LOSS`, `ADJUST_UP`/`ADJUST_DOWN`, `COUNT_ADJUST`, `STATUS_CHANGE`, `OWNER_CHANGE`, `SCRAP`, `RETURN_RECEIPT`, `RTO_RECEIPT`, `LANDED_COST_APPLY`, `TRANSFER_RETURN` (a transfer cancelled in transit, `RJ-006`) + reversal counterparts |
| 2 | **Document / reference type** | `whb_document_types` | `owning_module`, `display_resolver_bean`, `is_stock_bearing`, `is_external` | **PNR-1** | `SALES_ORDER`, `TRANSFER_ORDER`, `WORK_ORDER`, `JOB_CARD`, `PO`, `ASN`, `GRN`, `COUNT`, `TRIP`, `MANIFEST`, `CONSIGNMENT`, `POS_SHIFT`, `RMA` |
| 3 | **Source system / adapter id** | `whb_source_systems` | `module`, `is_reserved`, `is_claimable`, `post_permission` | **PNR-1** | `WAREHOUSE`, `ADAPTER_DEALER`, `ADAPTER_SERVICES`, `ADAPTER_FIELD_SERVICE`, `ADAPTER_ASSETS`, `LOGISTICS`, `WAREHOUSE_3PL`, `IMPORT`, **`ACCESSORIES` (`is_reserved=true`, `is_claimable=false` — `D-9`)** |
| 4 | **Stock status** | `whb_stock_statuses` | `is_available`, `is_allocatable`, `is_shippable`, `is_countable`, `is_owned_asset`, `requires_reason_to_enter`, `requires_reason_to_leave`, `badge_variant` | **PNR-1** | **Ten.** `AVAILABLE`, `QC_HOLD`, `DAMAGED`, `QUARANTINE`, `EXPIRED`, `BLOCKED`, `CORE_UNGRADED`, plus `PENDING_RESOLUTION` (`RE-005`; `WH-SC-249`'s blocked-move queue holds stock in it), `RETURNED` (`WH-SC-057` and `DATA-MODEL.md` §`wh_return_receipt_lines` both require a dedicated return status — *"never straight to `AVAILABLE`"* — so it is v1 seed, not a `P2` addition) and `REJECTED` (QC's reject disposition, `WH-SC-071`/`WH-SC-072`; added 2026-09-14 by `P1-14`'s `V500058` because `V500005` is applied — `receipt-qc-putaway.contract.md` `RQP-OPEN-12`). **Not** `BONDED`: the regime is `duty_status` (`IRR-12`) and a customs hold is a `wh_hold_types` row, so one fact is not recorded on two axes (`RL-001`) |
| 5 | **Location type** | `whb_location_types` | `is_physical`, `is_stock_holding`, `is_virtual_counterparty`, `is_mobile`, `is_transit`, `allows_mixed_owner`, `requires_assigned_user` | **PNR-1** | see §4.5 |
| 6 | **Reason code + context** | `whb_reason_codes` | `context` (**no `CHECK`**), `requires_note`, `owning_module`, `blocks_posting`, `tax_treatment_code`, `statutory_category` | **PNR-1** | adjustment, short-pick, damage, transit-loss, scrap, return, count-variance, hold, release, RTO, NDR — plus **`REVERSAL`**, seeded by `P0-02` in `V500030` with a seed `INSERT` (the list is the starting seed of an open catalogue, not a closed set; `MPR-GRD-11`) |
| 7 | **UoM class + UoM** | `whb_uom_classes` + `whb_uoms` + `whb_item_uom_conversions` | `is_base_for_class`, `decimal_places`, `unece_rec20_code`, `gst_uqc_code` | **PNR-1** | `MASS`, `VOLUME`, `LENGTH`, `COUNT`, `AREA`, `TIME`; `EA`, `BOX`, `CASE`, `PALLET`, `KG`, `L`, `M`, `CFT` |
| 8 | **Task type** | `whb_task_types` | `owning_module`, `is_directed`, `default_priority`, `interleavable`, `labour_standard_minutes` | PNR-3 | `PUTAWAY`, `PICK`, `REPLEN`, `COUNT`, `MOVE`, `LOAD`, `PACK`, `QC`, `VAS` |
| 9 | **Owner type** | `whb_owner_types` | `is_house`, `posts_to_our_gl`, `default_cost_basis` | **PNR-1** | `HOUSE`, `CLIENT_3PL`, `CONSIGNOR`, `CUSTOMER_OWNED`, `SUPPLIER_CONSIGNED`, `JOB_WORK` |
| 10 | **Item type** | `whb_item_types` | `is_stocked`, `is_serial_default`, `is_lot_default`, `is_returnable_equipment`, `is_asset_shaped`, `is_value_only` | **PNR-1** | `STOCK`, `NON_STOCK`, `SERVICE`, `KIT`, `CORE`, `CONSUMABLE`, **`PACKAGING`**, **`RETURNABLE_EQUIPMENT`**, **`TYRE`**, **`FUEL`** |
| 11 | **Counterparty role** | `whb_counterparty_roles` + `whb_counterparty_role_links` | `role_code`, `owning_module`; the link row carries `is_primary`, `valid_from`/`valid_to` | **PNR-1** | `SUPPLIER`, `CUSTOMER`, `CARRIER`, `CLIENT_3PL`, `TRANSPORTER`, `JOB_WORKER`, `INTERNAL` |
| 12 | **Disposition** (return/RMA outcome) | `whb_dispositions` | `movement_type_code`, `target_stock_status_code`, `requires_inspection`, `emits_credit_signal` | PNR-3 | `RESTOCK_SELLABLE`, `RESTOCK_UNSELLABLE`, `REFURB`, `REPACK`, `SCRAP`, `RTV`, `DONATE`, `HOLD_FOR_CLIENT`, `RETURN_TO_CLIENT`, and `REJECT` (`STATUS_CHANGE` → `REJECTED`; added 2026-09-14 by `P1-14`'s `V500058` — `receipt-qc-putaway.contract.md` `RQP-OPEN-12`) |
| 13 | **Attribute key** (the §4.2 side-table keys) | `whb_attribute_keys` | `value_type`, `owning_module`, `is_filterable`, `is_exportable` | PNR-3 | temperature, cold-chain excursion, COA ref, channel order id, GS1 AI codes |

**Thirteen, not six.** Accounting's round-4 review found six closed vocabularies in its base. A
warehouse has more axes than a ledger, and every one of these is a place a future consumer must
extend: logistics needs #1, #2, #3, #5, #6, #10; a supply-chain module needs #2, #6, #11; a 3PL needs
#4, #9, #12; an EDI adapter needs #13.

**Seven of the thirteen are `PNR-1`, not merely "early"** — #1, #2, #3, #4, #5, #6, #7, #9, #10, #11
carry `NOT NULL` foreign keys from the ledger, so their tables must exist *before* `P0-02` runs
(§3.4's ordering consequence).

### 5.1 The two rules that stop the openness being cosmetic

1. **`WarehouseBaseCouplingTest` asserts, by name, that none of the thirteen `table.column` pairs
   carries a `CHECK (… IN (…))`.** The test enumerates the thirteen explicitly, so adding a
   fourteenth registry means adding a row to the test — which is the point. (R7 §4.4 layer 1,
   assertion 4.)
2. **The frontend may not re-close what the backend opened.** This repo has a documented recurring
   defect of exactly that shape: a status present in the `CHECK` constraint but missing from the
   frontend union, the variant map, the filter options or the i18n keys. Three checkable rules:
   no TypeScript string-union type enumerates a registry vocabulary (`type MovementTypeCode = string`
   plus a fetched list); `StatusBadge` variant comes from the registry row's `badge_variant` column,
   not a frontend map; i18n falls back to the registry row's `name` when
   `t('warehouse:statuses.<code>')` misses, so a newly seeded status renders in English rather than
   as a raw key.

**This knowingly conflicts with CLAUDE.md TYPESCRIPT RULE #6** (*"String union types over TypeScript
enums"*). That rule is right for genuinely fixed sets (`'ACTIVE' | 'INACTIVE'`) and wrong for a
catalogue. `DECISIONS.md` **`OD-5`** carries the conflict, its deadline (*before the first warehouse
page is written*) and its recommendation. **This document does not adjudicate it** — it is referred
to the standards owner, and the recommendation is `OD-5`'s, not mine.

---

## §6 — What is **not** on this list

A list that contains everything protects nothing. These are the items people reliably fear are
irreversible and are not. **Do not spend review time, plan contingency or an argument on any of
them.** Each row says the class and the reason, so the reassurance is checkable rather than
asserted.

| Feared as irreversible | Actual class | Why it is safe to defer, and what the re-entry looks like |
|---|---|---|
| **Wave planning** (`wh_waves`, wave strategies, release rules) | **additive** | A wave is a *grouping over demand that already exists*. New tables, new screens, no change to the ledger, no change to the reservation grain — because `IRR-45` already makes allocation an open-item ledger, and a wave is a set of allocations. R2 `T-044` asks only that the v1 absence be a **stated deferral rather than silence** |
| **Packing, cartonisation, `wh_cartons`** | **additive** | New tables hanging off the shipment. The one column that would have been irreversible — `lpn_id` on the ledger — is already `IRR-15` |
| **The client portal** | **additive** | It is a **permission surface over the existing grids**, not a second application. The irreversible half is `IRR-60`, the owner-scoped grant plus one server-side resolver. R4 §5.5 #9 additionally warns against a *second* grid-preferences or filter mechanism for it — that is a standing hazard, not an irreversibility |
| **Rate cards, charge codes, billing runs, accessorials, disputes** — the whole of `warehouse-3pl` | **additive** | Eighteen tables in their own module and band. The concession that is *not* deferrable is class B in R4 §5.2 — `IRR-06`, `IRR-07`, `IRR-08`, `IRR-15`, `IRR-19`, `IRR-36`, `IRR-50`, `IRR-58`, `IRR-59`, `IRR-60` — and every one of those is already above. **A feature flag would not have saved a single column** |
| **E-way bill, delivery challan, ITC-04, the Rule 56 stock account, MRP declarations** | **additive**, in `warehouse-india` | `D-8` keeps the rules out of the core as *data*. The **hooks** are irreversible and are already here: `IRR-17` `company_id`, `IRR-32` tax-mapped reason codes, `IRR-42` tax-classification snapshot, `IRR-57` warehouse legal identity, `IRR-12` `duty_status`. Ship the hooks, defer the rules |
| **RF / handheld screens** and the mobile counterpart | **additive** | v1.1 by the ladder. The irreversible halves are `IRR-46` (a task table exists), `IRR-21` (`occurred_at` producer-supplied) and `IRR-49` (batch posting) — all above. Note `D-13`: mobile is not optional, and `C-044` corrects CLAUDE.md — `mobile/src/components/common/ListHeader.tsx:210-218` now supports `type?: 'dropdown' \| 'text'`; **date filters are still unsupported** |
| **Label printing (ZPL), pick lists, document print** | **additive** | Genuinely urgent — R5 ranks *"nothing prints a label"* as ship-blocker #2, and `grep -rli zpl` across the repo returns 0 — but urgent is not irreversible. A print service is new files, no schema |
| **Slotting, replenishment optimisation, labour standards, ABC/XYZ** | **additive** | All read history and write suggestions. They need `IRR-51` (the snapshot job's start date) and `IRR-23` (task durations) to have data to read; the *engines* are v3 by design, and R4 §5.5 #5 argues they should be, because both need a year of our own data |
| **EPCIS event repository** | **additive** | Our obligation is to **emit** correct events, which is a projection over the ledger. The irreversible halves are `IRR-20` (read point vs biz location) and `IRR-21` (event time vs record time). A queryable repository is a compliance product in its own right and is deliberately not built (R4 §5.5 #4) |
| **Carrier integration, rate shopping, AWB pools, manifests** | **additive**, and largely `warehouse-3pl` / adapter | The one v1 column is `IRR-59`, `wh_carrier_accounts.owner_id` nullable |
| **Marketplace / channel connectors** | **additive** | Channel is a master with per-owner accounts; the connector is an adapter. Order-import idempotency reuses `IRR-04`'s mechanism at a different scope |
| **Kitting and light manufacturing** | **mostly additive** | The exception is `IRR-54`, the transformation genealogy tables, which are v1 because they can only be populated by the act itself. The kit *workflow* is v1.1 and additive |
| **Cross-docking** | **additive** | One nullable flag on the receipt line in v1 (R2 `T-039`); the flow is v2 |
| **Dock appointments and the yard** | **additive** | The dock door is a warehouse resource (v2); the yard beyond it is transport and belongs to the future logistics module. `wh_dock_appointments` is the join |
| **More statuses, more movement types, more reason codes, more location types, more item types** | **additive — by construction** | This is the entire payoff of §5. Adding a vocabulary value is a **seed `INSERT`**, in the adding module's own migration, with no base release and no `ALTER`. It is only irreversible if someone writes a `CHECK` |
| **New grids, filters, columns, exports, statistics tiles** | **additive** | Ordinary platform work. It does cost a `COMMON_FILTER_CONFIGS` scope in `platform/frontend/src/utils/filterUtils.ts` and a cache name in `CacheConfiguration.java` **per grid** — which is `D-10`'s corollary, not an irreversibility. Computed 2026-09-01: `awk 'NR>346' platform/frontend/src/utils/filterUtils.ts \| grep -cE '^  [A-Z][A-Z0-9_]*: \{'` → **211** scopes; `grep -cE '^\s+"[a-zA-Z]' platform/backend/src/main/java/ai/platform/config/CacheConfiguration.java` → **231** cache-name lines |
| **`accessories` absorbing into warehouse, or warehouse absorbing accessories** | **decided, not deferred** | `D-9` settles it: permanently separate. The two mitigations that make the cost *detectable* are v1 and are tasks — see [`COEXISTENCE.md`](COEXISTENCE.md) |
| **The dealer vehicle inventory (`pdi_*`) migrating onto the ledger** | **open decision, `OD-2`** | Explicitly **not** v1 or v2. Modelled as a documented future adapter. Prove the ledger on parts first |
| **Multi-tenancy** | **open decision, `OD-3`** | `grep -ril "tenant" platform/backend/src/main/java` → **0 files**. Classic is one-DB-per-customer, which is exactly why a 3PL's clients are an **owner dimension** (`IRR-06`) rather than tenants. Keeping one-DB-per-customer is the recommendation, and `IRR-06` already carries the case |

**And one that looks like it belongs here and does not:** *"we can always rebuild the positions
table"*. That is true (§3.3) and it is **not** a general licence. It is true only for columns the
**ledger line** already carries, which is the reason §2 places them on the line.

---

## §7 — Corrections, conflicts and what could not be verified

`DECISIONS.md` rule 2 requires that a claim be evidenced or marked `UNVERIFIED`, and its preamble
requires that a disagreement with a source review be stated rather than diverged from silently.

### 7.1 Where a source review is superseded by `DECISIONS.md`

| Source | What it says | What supersedes it | Effect on this document |
|---|---|---|---|
| **R4 §3.2 / §3.3** names the ledger tables **`whb_movements`** / **`whb_movement_lines`** | — | `DECISIONS.md` `L-1`, `L-2`, `L-4` name them **`whb_stock_movements`** / **`whb_stock_movement_lines`** | Names corrected throughout. No content change |
| **R4 §3.3** puts `from_location_id` **and** `to_location_id` (and `from_stock_status_code`, `from_lpn_id`/`to_lpn_id`) **on one line**; **R5 row 20** asks for `from_location_id` + `to_location_id` both `NOT NULL` | — | `D-4` + `L-1`: a movement is **two or more signed lines that conserve quantity**. A single row with two ends is the from/to shape `T-001` (this document's `IRR-01`) exists to prevent, and it is the shape the prior WMS art used | §4.2 specifies **one** `location_id`, one `stock_status_code`, one `lpn_id`, one `owner_id`, one `duty_status` per line, signed. **The irreversible content of both proposals survives**: virtual locations must exist so no side is ever absent (`IRR-05`), status must be on the line and in the position key (`IRR-10`). Only the mechanism changes |
| **R4 §5.1 / §5.6** places `warehouse-3pl` at **V930000–V939999** and warns about ordering there | — | `D-2`: the V900000+ bands are **occupied** — 135 OEM-seed files in `V900000–V909999`, 434 per-client files in `V910000–V919999` with versions deliberately reused across five client directories — and `FlywayConfiguration.java:296-327` renumbers legacy history into both bands and then **`DELETE`s duplicate history rows**, so a collision deletes a history row rather than failing loudly. `warehouse-3pl` is **V530000–V539999** | All bands in this document are `D-2`'s. Verified 2026-09-01: `find . -path '*/db/*' -name 'V*__*.sql' \| sed -E 's\|.*/V([0-9]+)__.*\|\1\|' \| awk '$1>=130000 && $1<=599999' \| wc -l` → **0** |
| **R3 §5.4 `M1`** proposes **`wh_external_item_map`**; **R3 §2.11 `E-083`** the same; R3 uses `wh_` for base tables throughout (`wh_items`, `wh_stock_balances`, `wh_uoms`, `wh_cost_layers`) | — | `D-3`: **`wh_` is the *application*, `whb_` is the base** — *"R3's usage is the one that changes"*. `D-9` names the table **`whb_item_external_refs`** | `IRR-25` and §4.9 use `whb_item_external_refs`. R3's `map_status` enrichment (`MAPPED`/`UNMAPPED`/`AMBIGUOUS`/`DELIBERATELY_SEPARATE`) is carried forward in [`COEXISTENCE.md`](COEXISTENCE.md) §5 |
| **R2 §3** names the task table **`wb_tasks`**; **R7 §4.5** uses the adapter prefix **`wha_<vertical>_`** | — | `D-3` fixes the prefixes: `whb_` / `wh_` / `wh3_` / `whin_` / `whad_` / `whas_` / `whaf_` / `whaa_`. There is no `wb_` and no `wha_` | Names corrected. See §7.3 for the one placement this document could **not** resolve |
| **R5 §4.1** describes `acc_stock_balances` as a second authoritative quantity balance | — | The accounting set has since made it explicit that it **is a cache** — *"maintained in the posting transaction and rebuilt nightly with a drift alert… **It is a cache**, subject to the same L-9 discipline: derived, never authoritative"* (`accounting/docs/DATA-MODEL.md:507`) | Does not weaken `D-6` or `OD-1`. A cache of *what* is still the question, and `D-6`'s answer — accounting's balance becomes a read-through projection of the warehouse ledger — is unchanged. It does make `OD-1` cheaper than R5 assumed: `acc_stock_balances`, `acc_valuation_entries` and `acc_cost_layers` are all **phase P3** in the accounting set (`DATA-MODEL.md:434`, `:436`, `:507`), and P3 is unbuilt |
| **R1 §5.1 item 15** — *"No cross-warehouse 'in transit' state… the goods are never in transit, so a two-step transfer is not modelled"* | — | Verified more precisely | The two-step transfer **is** modelled — as a **document status**. `StockTransferService.shipTransfer()` deducts from source and sets `transfer.setStatus("IN_TRANSIT")` (`:283-316`, deduction at `:495`), `receiveTransfer()` adds to destination (`:322`, `:554`). What does not exist is in-transit **stock**: between ship and receive the goods are on **no** balance row anywhere. R1's conclusion is right; the mechanism is "transit is a status, not a location", which is R3 `E-032`, and it is exactly what `IRR-05` and `IRR-29` prevent |
| **R1 §5.1 headline** — *"17 of its 71 tables are inventory-scoped"* | — | R1's own table enumerates **19** distinct table names | Computed: `grep -rhoiE 'CREATE TABLE (IF NOT EXISTS )?(public\.)?accessory_[a-z_]+' accessories/backend/src/main/resources/db/migration/ \| sed -E 's/.*(accessory_[a-z_]+)/\1/' \| sort -u \| grep -cE 'stock\|inventory\|warehouse\|storage_bin\|issuance\|uom'` → **19**; total `accessory_*` tables → **71**. `D-9` quotes R1's 17. Detail and the full reconciliation in [`COEXISTENCE.md`](COEXISTENCE.md) §1 |
| **R1 `C-016` / `C-030`** — *one branch, one GSTIN*; do not repeat accessories' many-to-many warehouse–branch junction | — | `DECISIONS.md` **`D-14`** (2026-09-10, a user decision on round 4): a warehouse links to branches through the dated `whb_warehouse_branches`, with exactly one `REGISTERED` link at every instant. `RG-001` is canonical | `IRR-57` keeps `state_code` and replaces `legal_entity_id` + `tax_registration_id` with the link; §3.4 and §4.5 are reversed; `IRR-64` is added. R1's underlying concern, a site under two registrations at once, survives as the exclusion on `REGISTERED` ranges |

### 7.2 A conflict between two lenses that neither `DECISIONS.md` nor this document resolves

**R3 `M3`/`E-084` proposes a union valuation report** across both inventories, tagged by
`source_system`, with the differing-method caveat rendered on the report itself — *"ugly, honest, and
the only way a CFO gets one number without a merge"*.

**R7 §4.6 item 4 argues the opposite**: *"the honest mitigation is a documented 'these two
inventories are separate' statement in the UI, not a union view."*

Both are defensible and they cannot both be built. It is a product decision, not a schema one, so it
does not gate any migration and it is **not** on this list. It is raised, with a recommendation, in
[`COEXISTENCE.md`](COEXISTENCE.md) §5 (`M3`), and it needs an `OD-` row in `DECISIONS.md` — which is
that document's to allocate, not this one's.

### 7.3 Two placements this document could not resolve, and did not guess

1. **Where the cost-layer tables live** (`IRR-38`, `IRR-39`, `IRR-40`). `D-6` is unambiguous that
   **accounting owns value**, and R5 `S-066` recommends *"accounting computes value; warehouse
   supplies quantity, identity and the receipt-side purchase cost only."* But `D-7` makes
   **`platform + warehouse-base + warehouse` with no accounting module the reference
   configuration**, and the v1 exit criterion requires that install to produce *"a stock ledger, a
   position report and a **valuation report** that reconcile to each other"*. Something in warehouse
   must therefore compute value when accounting is absent. `OD-6` says *"ship weighted average +
   FIFO in v1 **with the layer table present**"* without saying whose table it is.
   **What is not in doubt, and is what this list needs:** `cost_basis`, `unit_cost`,
   `cost_currency_code`, `moving_average_after` and `cost_layer_id` are **columns on the ledger
   line** and are `PNR-1`, whoever computes the numbers. The *table* placement is `OD-1`/`OD-6`
   territory and needs closing before `P2`.
2. **Whether the task table is base or app** (`IRR-46`). R7 §5.2 puts the **type registry**
   `whb_task_types` in base, which settles half of it. `D-3`'s only worked example of a `wh_` table
   is `wh_pick_tasks`, which suggests the task table is the application's. R2 `T-041`'s argument is
   about the table existing **in v1**, not about which module owns it, and that argument is
   unaffected either way. Recorded as an open placement, not guessed.

### 7.4 `UNVERIFIED`, stated plainly

- **The `PNR-2` migration number.** `DECISIONS.md` names `P0-02` as the task that writes
  `whb_stock_movements` (`OD-1`, `OD-7`) but no task file exists yet — `ls issues/` in
  `warehouse-issues` returns an empty directory — so no migration number can be cited. §3.5's
  recommendation (collapse `PNR-1` and `PNR-2` into one migration) is made **precisely so that no
  number needs to be cited**: the gate becomes "the migration that creates the ledger", which is
  self-identifying. **Do not write a number here until `issues/p0-02.md` exists.**
- **`GAP-REGISTER.md`, `DATA-MODEL.md`, `SCENARIO-CATALOGUE.md`, `issues/`, `tools/check-design-set.py`**
  are all referenced by `DECISIONS.md` and **none of them exists yet** (verified: `ls -R` on the repo
  shows `docs/DECISIONS.md`, `docs/reviews/R1`–`R7`, and empty `docs/contracts/`, `issues/`,
  `tools/`). This document deliberately cites **no `FR-nnn`, no `WH-SC-nnn`, no `I-n` SQL-invariant
  id and no `#NN` issue number**, because every one of them would resolve to nothing. The accounting
  set's worst failure was 25 dangling `FR-nnn` citations of which 19 resolved to a *different real
  requirement*, so live gaps read as closed.
- **Precision (`OD-7`) is open**, so every type in §4 is a recommendation carrying a citation, not a
  ruling. The one substantive divergence to resolve is `conversion_factor_used`: R4 proposes
  `numeric(18,8)`; the accounting set has no `*_factor` row, and its `DECIMAL(19,8)` is explicitly
  *"the **currency-conversion** type and nothing else"* (`accounting/docs/DATA-MODEL.md:2462-2467`).
- **The India rule detail behind `IRR-12`, `IRR-32`, `IRR-42`, `IRR-44` and `IRR-57`** is R5's, and R5 states
  its own knowledge ends **May 2026** and that at least one of its numbers is probably already
  wrong. Nothing in this document depends on a threshold, a rate or a periodicity — only on the
  existence of the columns, which is not date-sensitive.

### 7.5 Referred to the standards reviewer — not this document's business

One line each, no detail, because `.claude/commands/standards-parity-checklist.md` and the
`reviewer` agent own them:

- `OD-5` — whether a TypeScript string union may enumerate an open backend catalogue (§5.1).
- Every warehouse grid needs a `COMMON_FILTER_CONFIGS` scope, a `CacheConfiguration` cache name,
  `grid_column_definitions` + `filter_definitions` rows and both `grid_preferences.default_filters`
  **and** `default_columns` populated.
- Web↔mobile parity (`D-13`, CLAUDE.md Principle #3) applies to every warehouse screen; the RF
  screen family is a deliberate divergence from `EntityListScreen` and needs an explicit ruling.
- The prior WMS art's `metadata JSONB` on `wms_items` is forbidden here (§4.2) — noted so the
  prohibition is not re-litigated as a style preference.

---

*Established 2026-09-01. Every `grep`, `find` and `sed` count in this document was run on that date
against `/Users/bbhushan/work/git/workspace/classic`, `.../accounting`, `.../classic-issues` and
`.../warehouse-issues`. Re-run before treating one as current — `DECISIONS.md` rule 1.*
