TITLE: [Warehouse] EPIC: P1 — Masters, identity, inbound
LABELS: epic,warehouse,phase-p1
issue: 4
---
Part of __MASTER__ · Modules `warehouse-base` (masters) + `warehouse` (inbound documents) · Migrations — **20 blocks, enumerated below** · Ships in **v1**

## Overview

**One item master, one facility model, one party identity, one numbering generator, one import
framework — and the whole inbound chain on top of them:** purchase order → receiving session → GRN →
QC → putaway, with reversal and the layered-truth model.

**`A-3` is why the variant schema is here and not in v2** (`DECISIONS.md` §5.1; `H-008` — this epic
cited no amendment at all). R2 and R3 placed the style × variant model at v2; R5 `S-056` argued it is
v1 *schema*, and the amendment accepted that **as schema only**: the style/parent item, the variant
axes and their values land in `V500014`/`V500015` under the same rule as `owner_id` (`D-5`), while the
matrix screens, grids and reports (`WS-032`, `WS-033`) stay v2/P5. The reason is that a flat SKU model
is **unrecoverable** — correcting it later is a re-keying of the item master and of every movement
that references it — and apparel and footwear is the largest Indian segment we would otherwise
decline. **`P1-01` ships the columns whether or not any screen reads them yet.**

P1 delivers: the item master with its four independent status facts and its **v1 variant schema**;
UoM, packaging and the barcode registry with **one scan-resolution service**; the item's commercial
and compliance block and supersession chains; the facility model with its **virtual-location seed**
and the bin generator; lots, serials and LPNs **as entities**; counterparties; **gapless** document
numbering; the import framework with a **reversal path**; the transfer-order schema carrying the
India and ownership hooks; warehouse-scoped access as a record-level guard; `en`/`fr`/`hi`
throughout; and every P1 grid's configuration.

**What P1 deliberately does not do:** no allocation, no picking, no shipping, no counting, no
valuation, no printing, no returns, no reports beyond the masters' own grids. **The ASN is not in
P1** — it is `P3-05`, because the ASN's job is to drive dock appointments, pre-allocation and
cross-dock, none of which exists yet. **Blind receipt (`FR-128`) is what covers the no-PO case in
v1.**

## ★ Seven P1 tasks are P0-blocking

`IRREVERSIBLE.md` §3.4 is explicit: six master tables carry **`NOT NULL` foreign keys** from
`whb_stock_movement_lines`, so *"`P0-02` is therefore not the first warehouse migration; it is
roughly the tenth."*

**`P1-01`, `P1-02`, `P1-05`, `P1-07`, `P1-08` and `P1-09` — plus `P0-17` — must have their migrations
written and merged before `P0-02`'s**, even though **their screens and services are P1 work**.

> **Anyone who plans `P0-02` as migration one will meet this at the first `REFERENCES` clause and
> will be tempted to make the foreign keys nullable. Do not.** That silently converts the grain from
> *enforced* to *hoped for*, and `owner_id`, `item_id`, `location_id` and `period_id` are the four
> columns the entire product's grain rests on.

`P1-08`'s case is the subtle one and it is **not** a ledger FK: `whb_owners.counterparty_id`
references `whb_counterparties`, and `whb_owners` is `V500007` while `whb_counterparties` is
`V500011`. See *Defects* below and `DEFECTS-FOUND.md`.

## Exit criterion — a **Mode A** install, `platform` + `warehouse-base` + `warehouse`

`WH-SC-045` … `WH-SC-052` run **in order**:

1. **`WH-SC-045`** — create a warehouse with its `REGISTERED` branch link, a structured address and a
   timezone; the GSTIN is **read from that branch**, never duplicated. A second current `REGISTERED`
   link is refused and `SERVING` is offered (`FR-460`, `D-14`).
2. **`WH-SC-046`** — generate **1,152 bins** from a format mask, with the **count and the first and
   last codes previewed before anything is written**.
3. **`WH-SC-047`** — import an item master where the dry run reports **per-row, per-cell** errors.
4. **`WH-SC-048`** — `validate` **persists nothing**, asserted by row count on the target table
   **and** on `whb_import_batches`.
5. **`WH-SC-049`** — post opening stock as **`OPENING_BALANCE` movements from the opening virtual
   location** with unit costs, **never as a position `UPDATE`**. *(Owned by `P2-19`; listed because
   it is the next link in the exit chain.)*
6. **`WH-SC-050`** — produce the closing-value tie-out certificate. *(`P2`.)*
7. **`WH-SC-051`** — receive against a purchase document with a **gapless GRN number issued from the
   locked counter row**.
8. **`WH-SC-052`** — put away with a suggested location, **an accepted override, and the override
   reason captured**.

## The invariants and properties this phase establishes

| | What P1 makes true | Where |
|---|---|---|
| **`uk(owner_id, sku)` + a globally unique `item_code`** | **`PNR-4`.** Rows that merged under a narrower key **cannot be un-merged** | `P1-01` · `V500015` · `I-19` |
| **`uk(owner_id, item_id, serial_number)` — never globally unique** | **`PNR-4`**, and sharper: the rows a global unique would have **rejected were never recorded**, so there is nothing to migrate from | `P1-07` · `V500018` · `I-19` |
| **Base stocking UoM immutable once a ledger row exists** | A **database trigger**, not a service check | `P1-02` behaviour · `V500036` trigger (`P0-02`) · `I-9` |
| **`location_id NOT NULL` *is* `L-1`** | Virtual locations **must exist before the first movement can balance** | `P1-05` · `V500013` · `I-17` |
| **Gapless document numbering from a locked counter row** | Gapless ≠ unique. A unique constraint plus a retry burns a number per failure | `P1-09` · `V500020` · `I-20` |
| **Genealogy recorded at the moment of transformation** | Answerable **both** directions; **never reconstructed** | `P1-07` · `V500035` · `L-12` |
| **Warehouse ∩ branch ∩ owner scope in the `WHERE` clause** | **A menu filter is not a guard** | `P1-18` |
| **`is_taxable_supply` derived at creation and frozen** | A branch's GST registration changes; a filed return does not | `P1-17` · `V510031` |
| **One `REGISTERED` branch at every instant** (`FR-460`, `D-14`) | A warehouse links to branches through `whb_warehouse_branches`; the `REGISTERED` link supplies the GSTIN, the branch-scoped series and the tax attribution, and classification reads it at `occurred_at`. Its history is dated and append-only once a movement stands in its range, so a re-registration closes one row and opens the next — it never overwrites (`RG-001`) | `P1-05` · `V500012` · `I-22`/`I-23` (`P0-02`, `V500030`/`V500037`) |

**Two `PNR-3` deadlines land in P1** and neither breaks anything on the day:
**GRN lifecycle timestamps** (`V510014`, `P1-13`) — *a duration cannot be backfilled, so the first
client's month-one dock-to-stock report cannot be produced*; and **`whb_lpns.received_at`**
(`V500018`, `P1-07`) — **3PL anniversary storage billing has no other anchor.**

## Migration blocks

**26 blocks** (20 v1, and six v1.1/v2 increments folded in on 2026-09-10), re-derived from the `Migrations` field of every P1 task header, not transcribed from
an earlier table:

```bash
# from the warehouse-issues repo root
grep -h '^Part of __P1__' issues/p1-*.md | sed 's/.*Migrations \*\*//; s/\*\*.*//'
```

That command is the authority; re-run it after any header change.

**`warehouse-base` band — ★ marks a block that must land before `V500030`:**

- ★ `V500009` `V500016` — `P1-02` UoM classes and UoMs · identifiers, packaging levels, conversions, attribute values
- `V500076` — `P1-02` **v2 increment**: `whb_uom_scheme_codes` (`RG-020`, folded from former `P5-24`)
- ★ `V500011` — `P1-08` counterparty roles, counterparties, role links, external refs **+ the `whb_owners` FK**
- ★ `V500012` `V500013` — `P1-05` warehouses · locations, location external refs **and the virtual-location seed**
- `V500070` — `P1-05` **v2 increment**: `whb_location_owner_dedications` (`RG-014`, `FR-468`, folded from former `P5-24`; `whb_warehouse_companies`, `RG-012`, moved to `P1-22` at v1)
- ★ `V500014` `V500015` — `P1-01` categories and variant axes · **`whb_items`, `PNR-4`**
- `V500075` — `P1-01` **v2 increment**: `whb_item_uom_defaults`, `whb_item_tax_classifications` (`RG-010`, `RG-020`, folded from former `P5-24`)
- ★ `V500018` `V500035` — `P1-07` **lots, serials (`PNR-4`), LPNs** · transformations
- ★ `V500020` — `P1-09` number series, issued numbers, `whb_next_document_number()`, `I-20`
- `V500017` `V500053` — `P1-04` item external refs and documents · **`D-9`'s two mandatory mitigations**
- `V500046` — `P1-10` import batches and rows
- `V500047` — `P1-18` `whb_warehouse_grants`, the warehouse axis of the scope predicate (`RA-001`)
- `V500050` — `P1-03` item × site settings, supplier sources, supersessions
- `V500069` `V500077` — `P1-03` **v1.1 increment**: the ABC cut-offs and previous class (`RK-003`, folded from former `P3-25`) · **v2 increment**: `warehouse_id` on supplier sources (`RG-011`, folded from former `P5-24`)
- `V500071` — `P1-19` **v2 increment**: `whb_registry_translations` (`RL-015`, folded from former `P5-28`)
- `V500055` — `P1-21` **`whb_master_merges`** — the round-2 master-merge task (`FR-451`, `Z-007`)
- `V500073` — `P1-22` **`whb_owner_companies`** (v1, reassigned from `P0-06`; drops `whb_owners.company_id`, `uk(code)`, `RG-013`, `D-14` item 8)
- `V500078` — `P1-22` **`whb_warehouse_companies`** (v1; drops `whb_warehouses.company_id`, `uk(code)`, `RG-012`, `D-14` item 8)
- `V500079` — `P1-22` one company per branch — `EXCLUDE` on `whb_company_branches` (`D-14` item 8e)
- `V500051` `V500052` `V500054` — `P1-11` channels · transport details · the `whb_activity_history` **view**
- `V501050`–`V501069` — `P1-20` base grid configuration, **wave 2**

**`warehouse` band:**

- `V510010` — `P1-06` dock doors, vehicle types, dock appointments *(★ `PNR-3` for the dock clock)*
- `V510011` — `P1-12` purchase orders and lines
- `V510013` `V510014` — `P1-13` receiving sessions · **GRNs** *(★ `PNR-3` for the lifecycle timestamps)*
- `V510015` `V510016` — `P1-14` inspection plans and criteria · inspections, lines, results
- `V510220` — `P1-14` **v2 increment**: `wh_inspection_plan_assignments` (`RG-018`, folded from former `P5-24`)
- `V510017` — `P1-15` putaway rules and tasks
- `V510018` — `P1-16` receipt reversals and lines
- `V510031` — `P1-17` transfer orders and lines — **schema only**
- `V511000` `V511001` `V511010` `V511020`–`V511059` `V511200` — `P1-20` app permissions, dependencies, menus, app grids wave 1, admin settings

`P1-19`'s v1 work writes **no migration** (its `V500071` is the v2 increment above); that is not a
defect — it is content and registration. `P1-18` writes one, `V500047` (`RA-001`, round 3).

## Tasks

__TASKS__

**Order:** `{P1-01, P1-05, P1-08, P1-09} → {P1-02, P1-07} → P1-03 → P1-04 → P0-02 → … → P1-06 →
P1-12 → P1-13 → {P1-14, P1-15, P1-16} → P1-17`. `P1-10` follows `P1-01`; `P1-22` follows `P1-05`; `P1-18`, `P1-19` and
`P1-20` follow `P0-15`.

- **The six starred masters' migrations come first**, before `P0-02`; **their screens and services
  come after it**, because the item, location and lot pages read on-hand from a ledger that does not
  exist yet.
- **`P1-12 → P1-13` is the critical path through P1**, and `P1-13` additionally needs `P0-08` (the
  port) and `P0-03` (the writer service).
- **`P1-20` must not be left to the end.** A grid without its `grid_preferences` row and its
  `filterUtils` scope **looks built and is not usable**.
- **`P1-18` and `P1-19` are cheap and are always deferred.** A scope guard added after ten screens
  ship is ten retrofits; a locale added after the strings are written is a re-read of every file.

## Traps this phase must not walk into

- **`whb_owners.counterparty_id` FKs forward.** `whb_owners` is `V500007`; `whb_counterparties` is
  `V500011`. Flyway runs them in that order, so the FK **cannot be declared in `V500007`**.
  **Resolution:** `V500007` creates a bare nullable `UUID`; **`V500011` adds the constraint by
  `ALTER TABLE`** in the same file that creates the target — legal, because `V500011` < `V500030`.
- **A "single-owner mode" for v1 convenience is the failure `FR-109` forbids.** v1 posts against the
  **seeded house owner** on every movement, so the owner code path is exercised from day one rather
  than from the day the first 3PL client arrives.
- **A globally unique serial rejects a legitimate second receipt**, and **the rejected rows were
  never written**, so there is nothing to migrate from later (`FR-097`).
- **One global `IN_TRANSIT` bucket** makes two consignments on the road one number nobody can age,
  count or attribute (`FR-085`). Transit locations are **per reference**.
- **Hard-coding `AVAILABLE` on receipt** makes every QC-controlled item available to promise the
  moment it lands (`FR-129`). The chain is **item → supplier → `AVAILABLE`**.
- **The UoM convertibility guard must be on the GRN modal, not only on the PO** — a named
  prior-system failure (`FR-143`).
- **A `validate` endpoint that persists** has already shipped in this codebase and produced
  **duplicate rows on the subsequent real import** (`FR-417`). The assertion is a **row count**, not
  a code review.
- **`accessory_*` is not prior art to port.** Reservations there are schema-only —
  `quantity_reserved` read in 7 places, written in 0 (`C-022`); physical counts **never post** —
  `generateAdjustments()` sets `status='POSTED'` and creates nothing (`C-023`); UoM conversion is
  **never applied** (`C-026`); lots and serials are `VARCHAR`s on the balance row (`C-028`); bins are
  flat free-text with capacity stored and never enforced (`C-029`); and receiving has **no supplier
  field at all** (`C-031`).
- **Do not join or redefine `all_activity_history`** — it is dealer-owned and `accessories`
  explicitly opted out (`C-048`). Warehouse owns `whb_activity_history`.
- **`SequentialCodeGenerator` is scan-based and explicitly not gapless** (`C-019`). Use the assets
  `PESSIMISTIC_WRITE` counter shape, which documents the exact race it prevents.
- **`branches.branch_name`, not `branches.name`**, in every platform branch join (R1 §8 trap `T-18`).
- **`dateOnly` versus `date`** — `date` moves the lower bound to the previous calendar day east of
  UTC (`filterUtils.ts:49-56`). Every statutory, expiry, manufacture, count and order date is
  `dateOnly` (`FR-327`).
- **No JSONB on any new business table** (`FR-383`). The prior art made it a convention on **eleven**
  tables (`P-007`); `inspection_criteria`, `compatible_vehicles`, `serial_numbers` and
  `trigger_conditions` are all **rows** here.
- **Mobile has no date filter.** `mobile/…/ListHeader.tsx:210-218` supports `'dropdown' | 'text'`
  only (`C-044`), so every mobile grid replaces a range with a bounded dropdown —
  `expiringWithinDays`, `receivedWithin`, `expectedWithin`. **That divergence is deliberate and must
  be stated per screen; silence is a defect** (`FR-218`, `D-13`).

## Defects found in `IMPLEMENTATION-PLAN.md` §2 while authoring these files

Recorded in full in [`DEFECTS-FOUND.md`](DEFECTS-FOUND.md); the two that change a task file:

1. **`whb_owners.counterparty_id` FK ordering** — `V500007` cannot reference `V500011`. Fixed in
   `p0-06.md` and `p1-08.md` as an `ALTER TABLE` in `V500011`. **§2.2's `Dep` cell for `P0-06` should
   read `P0-04 P1-08`.**
2. **`P0-02`'s `Dep` cell omits `P1-08`**, which §1.2, §3.2 and §3.3 all include. Both halves are
   carried in the task files.

## Definition of done
Per __MASTER__.
