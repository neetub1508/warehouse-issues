# R12 — Master-data lifecycle, go-live, data migration, administration and retirement

| | |
|---|---|
| **Date** | 2026-09-02 |
| **Lens** | R12 · how the data is born, amended, frozen, retired and disposed of |
| **Finding prefix** | `Z-` — confirmed unallocated: `grep -rohE "\bZ-[0-9]{1,3}\b" docs/ issues/ \| wc -l` → **0** |
| **Corpus greped** | `ls docs/*.md \| wc -l` → **16** · `ls issues/*.md \| wc -l` → **148** |
| **Read in full or in long section** | `DECISIONS.md`, `DATA-MODEL.md`, `BUILD-SPEC-SCREENS.md`, `SCENARIO-CATALOGUE.md`, `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md`, `GAP-REGISTER.md`, `DESIGN-SET-DEFECTS.md`, `IRREVERSIBLE.md` · task files `p0-04`, `p0-15`, `p1-01`, `p1-10`, `p2-19`, `p6-01` |
| **Read for de-duplication only** | `docs/reviews/R8`…`R11` — all 31 round-2 finding headings (`grep -hn "^### \`" …`) |

**Method, in three sentences.** I took the user journey of a master record rather than of a
transaction: created → imported → amended → frozen → merged → retired → archived → disposed of, and
for each step asked *is it specified, where, and what does the screen do*. Every candidate was greped
against `docs/` and `issues/` before filing, and discarded where round 1, an `X-` defect, a
`GAP-REGISTER` disposition or an R8–R11 finding already owned it. Where the design names a resolution
rule, I checked the rule against the table that has to express it and the trigger that has to enforce
it, because that is where four of the ten findings live.

---

## §1 · Verdict

**A real customer can be loaded onto this product, and cannot be run on it for a full financial
year.** Section A — go-live and opening stock — is the strongest part of the whole design set: `P2-19`
gives opening stock a status ladder, a dry run that persists nothing, per-row errors, an
`OPENING_BALANCE` posting from `VIRT-OPENING` that creates the first cost layer, a value tie-out
against the source system and a signed certificate that gates the period open. That is better than
most shipping WMS products do it.

Everything after day one is thinner than it looks. **The first thing that stops a customer is the
document number series.** `whb_number_series.reset_policy` offers `YEARLY`/`MONTHLY`, `I-20`'s own
unique index is `uk(series_id, issued_value)`, and `whb_number_series_issued` carries **no period
column** — so the first document of the second financial year tries to insert `issued_value = 1`
against a row that already exists and the insert fails. Nothing performs the reset, `WS-061` has no
reset action, and the nightly gaplessness assertion `MAX(issued_value) = COUNT(*)` is false for any
series that ever resets. India's delivery challan takes its statutory per-branch series from this same
table (`DATA-MODEL.md:1186`), so this is not a cosmetic default.

The second is that **policy resolution is specified in five places and implementable in two.**
`FR-014` scopes the negative-stock policy "by warehouse, owner or item group, resolved
most-specific-first"; the table is `uk(item_id, warehouse_id)` and the `I-6` trigger reads exactly one
row and hardcodes `'BLOCK'`. `FR-172` resolves allocation strategy "by site, item, owner, customer and
demand type"; the table carries one `(scope_type, scope_ref)` pair and three of those five dimensions
are absent from its enum. Two v1 acceptance scenarios — `WH-SC-018` (P0) and `WH-SC-089` (P2) — are
therefore unpassable as written. The set already contains the correct pattern twice
(`whb_gl_posting_rules.specificity`, `wh_putaway_rules.sequence`), so this is inconsistency, not
ignorance.

The most expensive *missing* thing is **amendment**. Fifty-one master screens ship a Department-shape
edit modal; the entire 2,126-line build spec contains **two** immutability statements
(`grep -c "immutable" docs/BUILD-SPEC-SCREENS.md` → 2). What happens when someone changes a UoM
conversion factor after three years, flips `lot_control_mode` from `NONE` to `REQUIRED` with 4,000
units on hand, or re-keys an item code is decided by whoever writes the service. And there is **no
bulk edit and no update handler at all** — the import framework's contract is create-and-reverse
(`p1-10.md:90`, `:95`), so a corrected re-import of a 40,000-row item file has no defined behaviour.

Retirement is the weakest section. No catalogue value can ever be deactivated, because the gate is
"a live row references the code" in a ledger where `L-2` makes every reference permanent. Duplicate
items and duplicate counterparties — which arrive on day one of any 40,000-SKU import against
`uk(owner_id, sku)` — have no merge path. And archiving, the one disposal mechanism, reads its
earliest legal cut-off from `P4-09`'s retention clocks, which live in `whin_retention_policies` —
`warehouse-india`, v2. A country-neutral install, which `D-1` says is the reference configuration,
has no retention policy and therefore cannot archive.

Go live: yes. Survive 1 April of year two: no.

---

## §1.1 · Coverage tables

### A · Go-live and data migration

| Item | Specified? | Where | Screen? | Verdict |
|---|---|---|---|---|
| Opening-stock batch with status ladder | **yes** | `p2-19.md:13`, `DATA-MODEL.md:1099-1100` | WS-150 | sound |
| Dry run that persists nothing | **yes** | `p1-10.md:31-32`, `p2-19.md:36` | WS-065, WS-150 | sound, with the duplicate-rows trap named |
| Per-row / per-cell error report | **yes** | `p1-10.md` traps, `whb_import_batch_rows` | child grid | sound |
| Partial acceptance vs all-or-nothing | **yes** | `FR-034`, `whb_import_batch_rows.status` | WS-055 | sound |
| Opening movement type + counter-side | **yes** | `OPENING_BALANCE` from `VIRT-OPENING`, `WH-SC-049` | — | sound |
| Opening cost and first cost layer | **yes** | `p2-19.md:47` | WS-150 | sound |
| Value tie-out + signed certificate | **yes** | `WH-SC-050`, `FR-412`/`FR-413` | WS-151 | sound — best-in-class |
| Reversal of a posted opening batch | **contradictory** | `p2-19.md:22` vs `p1-10.md:95` | WS-150 | **`Z-008`** |
| Re-import / corrected file / upsert | **no** | create-and-reverse only | — | **`Z-003`** |
| Idempotency of ingestion | **yes** | `L-9`, `uk(source_system, idempotency_key)` | — | sound |
| Master **load order** | **no** | checklist has one atomic "masters loaded ✔" | WS-151 | **`Z-009`** |
| Cut-over from `accessories` | **yes** | `COEXISTENCE.md` §7, `M1`–`M9` | WS-031 | sound |
| Cut-over from a competitor (Tally/Busy/Marg) | **yes, mis-phased** | `S-080` → `P3-18` | — | refused — `GAP-REGISTER` §7 row 5 |
| Parallel running / divergence detection | **no** | `grep -rin "parallel run\|dual run\|run both systems"` → 0 | — | refused — over-engineering for v1 |

### B · Amendment and freezing

| Item | Specified? | Where | Screen? | Verdict |
|---|---|---|---|---|
| Per-field freeze list, any master | **1 field of 51 screens** | `I-9` base UoM only | `WS-023` read-only | **`Z-004`** |
| Registry `code` immutable | **yes** | `BUILD-SPEC-SCREENS.md:545` | all 14 | sound |
| Item code re-key | **no** | `uk(code)` global, no immutability note | — | **`Z-004`** |
| UoM **conversion-factor** change | **line frozen, master not** | `L-7`/`IRR-34` freeze `conversion_factor_used`; WS-026 offers plain Edit | WS-026 | **`Z-004`** |
| `lot_control_mode` / `serial_control_mode` change with stock on hand | **no** | `BUILD-SPEC-SCREENS.md:816-817` carry no note | WS-023 | **`Z-004`** |
| Valuation method change mid-year | **partly** | `whb_valuation_policies` is effective-dated; no rule on existing layers | — | **`Z-004`** (secondary) |
| `is_taxable_supply` freeze (`OD-9`) | **decision open** | `OD-9` | — | refused — R10 `U-003` owns `OD-9` |
| Merge two duplicate **items** | **no** | supersession `MERGE_STOCK` is a different concept | — | **`Z-007`** |
| Merge two duplicate **counterparties** | **no** | `grep -i "merge" ` → nothing on counterparties | — | **`Z-007`** |
| Merge two **lots** | **yes** | `whb_lots` self-FK "split or merge parent", `whb_transformations` | WS-… split/merge | sound |
| Location rename / re-grid / merge bins | **no** | `FR-034`'s trap assumes bins get renamed and specifies nothing | — | **`Z-004`** |
| Bin capacity / type changed below contents | **no** | — | — | folded into **`Z-004`** |
| Bulk edit of any master | **no** | `grep -rin "bulk edit\|bulk update\|mass update"` → 0 | — | **`Z-003`** |

### C · Retirement and disposal

| Item | Specified? | Where | Screen? | Verdict |
|---|---|---|---|---|
| Deactivate an **item** holding stock | **yes** | `FR-051`, refusal + offered alternative | WS-023 | sound |
| Deactivate location / owner / warehouse | **no** | — | — | refused — R11 `Y-007` |
| Administrative journey for **closing a site** | **no** | `grep -rin "close a site\|site closure\|decommission"` → 0 in warehouse scope | — | **`Z-006`** (secondary) |
| Retire a **catalogue value** in use | **specified and impossible** | `BUILD-SPEC-SCREENS.md:549-550` | all 14 | **`Z-005`** |
| Historic label still renders after retirement | **yes** | `FR-381` badge variant + name fallback | — | sound |
| Retire a **barcode** without losing scan history | **yes** | `FR-057` — the correct pattern | WS-034 | sound |
| Statutory minimum retention (India) | **yes** | 8 financial years, `INDIA-LOCALISATION-PACK.md:59`, `:806` | WS-190 | sound |
| Retention policy for a **non-India** install | **no** | only table is `whin_retention_policies` (v2, india) | — | **`Z-006`** |
| Partitioning for volume | **yes** | `FR-022`, monthly `PARTITION BY RANGE (occurred_at)` from migration one | — | sound |
| Archive as a transaction | **yes** | `FR-023`, `P6-01` | none | sound |
| **Purge / disposal at end of retention** | **no** | archive tables are unbounded and never emptied | — | **`Z-006`** |

### D · Configuration and administration

| Item | Level | Precedence stated? | Screen? | Verdict |
|---|---|---|---|---|
| `warehouse.negative_stock.default_mode` | per-install | **no — and nothing reads it** | Admin Settings | **`Z-001`** |
| `whb_item_site_settings.negative_stock_mode` | item × site | **no** | WS-027 | **`Z-001`** |
| `whb_valuation_policies` | company × category × site, effective-dated | **no tie-break column** | — | **`Z-001`** |
| `whb_allocation_strategies` | one `(scope_type, scope_ref)` | **priority only, one dimension** | — | **`Z-001`** |
| `whb_gl_posting_rules` | full wildcard tuple | **yes — `specificity` + index + Test-resolution modal** | WS-051 | **the exemplar** |
| `wh_putaway_rules` | warehouse × sequence | **yes — `uk(warehouse_id, sequence)`** | — | sound |
| `whb_item_location_settings` | item × location | n/a (leaf) | WS-028 | sound |
| Numbering: prefix / padding / scope | series row | yes | WS-061 | sound |
| Numbering: **reset + year rollover** | `reset_policy` | **unimplementable** | no reset action | **`Z-002`** |
| Numbering: gaplessness under rollback | `I-20` | yes | — | sound |
| Numbering: failed transaction consumes a number | `I-20` "a rollback releases the number" | yes for a DB rollback | — | sound |
| Catalogue seeds: which ship, which are undeletable | `is_system` | yes | all 14 | sound |
| Catalogue seed change reaching an existing install | forward-only migration, idempotent | yes | — | sound (`WH-SC-292`) |
| **Operational roles** (storekeeper, picker, supervisor, stock controller, 3PL client) | — | **none seeded** | — | **`Z-010`** |
| ADMIN / ADMIN_GROUP / AUDITOR / Branch Admin | platform roles | yes | — | sound (`p0-15`) |

---

## §2 · The findings

### `Z-001` · Three of the set's five "most-specific-first" policy ladders cannot be expressed by their own tables, and two v1 acceptance scenarios are therefore unpassable — **BLOCKER**

- **What is missing or wrong:** The set states a most-specific-first resolution rule five times. Two
  implement it; three cannot.

  | Ladder | Dimensions the requirement names | What the table can express | Verdict |
  |---|---|---|---|
  | Negative stock (`FR-014`) | "warehouse, **owner** or **item group**" | `whb_item_site_settings uk(item_id, warehouse_id)` — one grain, no wildcard, no group | **cannot** |
  | Allocation strategy (`FR-172`) | "site, **item**, owner, **customer** and **demand type**" | `whb_allocation_strategies.scope_type ∈ GLOBAL/WAREHOUSE/ITEM_CATEGORY/OWNER/CHANNEL` + one `scope_ref` | **cannot** — 3 of 5 dimensions absent from the enum, and no pair is expressible |
  | Valuation method (`FR-235`) | company × category × site, nullable = all | `uk(company_id, category_id, warehouse_id, effective_from) NULLS NOT DISTINCT` — wildcards yes, **no specificity column and no stated tie-break** | **ambiguous** |
  | GL posting (`FR-246`) | full wildcard tuple | `specificity` computed column + `idx(company_id, specificity DESC)` + a **Test resolution** modal | **correct** |
  | Putaway (`FR-135`) | warehouse × sequence | `uk(warehouse_id, sequence)`, evaluated in sequence | **correct** |

  Two concrete consequences:
  1. **`WH-SC-018` is unbuildable.** It requires a policy row at `(warehouse = SITE-A, item_group = FASTENERS)` and then a more specific `(warehouse = SITE-A, item = WSH-0031)` row to win. `grep -rn "item_group" docs/ issues/` returns that scenario and **nothing else** — there is no item-group column, table or FK anywhere in the set.
  2. **The shipped install default is inert.** `P0-15` seeds `admin_settings` key `warehouse.negative_stock.default_mode`, and the `I-6` trigger reads `COALESCE(s.negative_stock_mode, 'BLOCK')` from one `whb_item_site_settings` row. An administrator who sets the install default to `WARN` changes nothing, and there is no screen or log that says so.
- **Why it matters:** `WH-SC-018` is a **v1·P0** scenario and `WH-SC-089` a **v1·P2** scenario; `DECISIONS.md` §5 makes scenarios the exit criteria for the phase. P0 cannot be signed off. Operationally, it bites the first time a stock controller wants "allow negative on-hand for consumables at the main store, block everywhere else" — a completely ordinary request — and discovers they must create one row per SKU per site, 40,000 of them, with no bulk edit (`Z-003`) to create them with. On the allocation side it bites the first time a customer wants FEFO for one item at one site (`WH-SC-089` verbatim) and the answer is a code change, which is precisely what `FR-172` exists to prevent.
- **Negative evidence:**
  - `grep -rn "item_group" docs/ issues/` → `docs/SCENARIO-CATALOGUE.md:178` only.
  - `grep -rn "negative_stock.default_mode\|negative_stock_mode" docs/ issues/` → 7 hits; `DATA-MODEL.md:2536` is the trigger body, `issues/p0-15.md:24` is the setting seed, and **no line joins them**.
  - `DATA-MODEL.md:825` — `whb_allocation_strategies … scope_type (GLOBAL/WAREHOUSE/ITEM_CATEGORY/OWNER/CHANNEL), scope_ref, priority`. No `ITEM`, no `CUSTOMER`, no `DEMAND_TYPE`; one `scope_ref`, so no conjunction.
  - `grep -rn "specificity" docs/ issues/` → 4 hits, all `whb_gl_posting_rules`.
- **Where it belongs:** `warehouse-base` · v1 · **P0** (negative stock) and **P2** (allocation)
- **Disposition:** *fold into tasks `P1-03` and `P2-07`*, plus a `DATA-MODEL.md` §2.1 amendment.
  - `P1-03` — add: *"`negative_stock_mode` resolution follows `whb_gl_posting_rules`'s shape, not a single row: a `whb_negative_stock_policies` table with nullable `warehouse_id`, `owner_id`, `item_category_id`, `item_id` and a computed `specificity`, resolved most-specific-first, seeded from `admin_settings.warehouse.negative_stock.default_mode` as the all-null row. `I-6`'s trigger calls the resolver function, never a single `SELECT`."*
  - `P2-07` — add: *"strategy selection is a `whb_allocation_rules` row over the full wildcard tuple `(warehouse_id, item_id, item_category_id, owner_id, counterparty_id, demand_type_code)` with a computed `specificity`, mirroring `whb_gl_posting_rules`; `whb_allocation_strategies.scope_type`/`scope_ref` is withdrawn. Ship the **Test resolution** modal, as WS-051 does."*
  - `whb_valuation_policies` needs one sentence in `DATA-MODEL.md:849` naming the tie-break when `(category, NULL)` and `(NULL, warehouse)` both match.
- **Irreversibility:** **reversible** — `whb_item_site_settings` is `V500050`, `whb_allocation_strategies` is `V500033`, both after `PNR-1` and neither sealed by `L-2`. The `I-6` trigger is a `CREATE OR REPLACE FUNCTION`. But it must be resolved **before P0 is called done**, because two of its exit scenarios depend on it.
- **Relationship to round 1:** **new.** `FR-014` and `FR-172` are both cited as COVERED in `GAP-REGISTER.md`; no round-1 finding compared the requirement text to the table grain. Adjacent to but distinct from `X-030` (missing `L-15` for value conservation).

---

### `Z-002` · `reset_policy` YEARLY/MONTHLY is unimplementable against `I-20`'s own unique index, nothing performs the reset, and the gaplessness assertion is false for any series that resets — **BLOCKER**

- **What is missing or wrong:** Four defects in one design, all in `DATA-MODEL.md:901-902` and `:2799-2812`:
  1. `whb_number_series.reset_policy ∈ NEVER/YEARLY/MONTHLY`, but `whb_number_series_issued` has columns `series_id, issued_value, formatted_number, issued_to_type, issued_to_id, issued_at, issued_by` — **no period, year or FY column** — and `I-20` creates `uk(series_id, issued_value)`. After a yearly reset the next issue is `issued_value = 1` for a `series_id` that already holds `issued_value = 1`. The insert **fails on a unique violation**.
  2. `uk(formatted_number)` does not save it: the index that collides is on `issued_value`.
  3. **Nothing performs the reset.** `last_reset_at` exists; there is no `@Scheduled` job, no trigger and no service method named anywhere. `WS-061`'s actions are *Add/Edit · Preview next number* and `current_value` is explicitly **read-only in the modal** (`BUILD-SPEC-SCREENS.md:1243`), so no human can do it either. `reset_policy` is a grid column that nothing acts on.
  4. The nightly assertion *"`MAX(issued_value) = COUNT(*)` per series"* (`DATA-MODEL.md:2807`) is **false by construction** for any resetting series — max is this period's counter, count is every period's rows — and also false for any `is_gapless = false` series, which the column explicitly permits.
- **Why it matters:** Name the moment. **1 April, year two, 08:05, the goods-inward desk.** The storekeeper receives the first delivery of the new financial year; `whb_next_document_number()` raises a unique violation inside the caller's transaction; the GRN cannot be created; **no goods can be received at that site** until someone changes the schema. Meanwhile, from the day of go-live, the nightly gaplessness job alerts on a correctly configured install, which is how a real alert gets muted. And this is not an optional feature for the target market: `whin_delivery_challans.series_id → whb_number_series` (`DATA-MODEL.md:1186`, `N3` at `:1451`) makes this the generator for India's statutory per-branch challan series, where per-financial-year serial numbering is the norm the pack itself assumes (`INDIA-LOCALISATION-PACK.md:1272`).
- **Negative evidence:**
  - `grep -rn "reset_policy\|resetPolicy" docs/ issues/ | grep -v reviews` → **3 hits**: `DATA-MODEL.md:901` (the column), `BUILD-SPEC-SCREENS.md:1243` (the grid column), `issues/p0-13.md` context. **No job, no service, no acceptance criterion.**
  - `sed -n '2799,2812p' docs/DATA-MODEL.md` → the index and the assertion, verbatim, with no period member.
  - `grep -rn "last_reset_at" docs/ issues/` → **1 hit**, the column definition itself.
- **Where it belongs:** `warehouse-base` · v1 · **P0/P1** (`WHB-20`, `V500020`)
- **Disposition:** *fold into task `P0-13`* (the task owning `V500020` / `WS-061` / `WS-062`). The line to add: *"`whb_number_series_issued` carries `period_key VARCHAR(10) NOT NULL` (`'ALL'` for `NEVER`, `'FY2026-27'` for `YEARLY`, `'2026-04'` for `MONTHLY`) and `I-20`'s index becomes `uk(series_id, period_key, issued_value)`. `whb_next_document_number(series_id)` computes the current `period_key` under the same `FOR UPDATE` lock, resets `current_value` to 0 and stamps `last_reset_at` when it differs from the last issue's — the reset is part of the allocation, never a separate job that can miss a midnight. The nightly assertion becomes `MAX(issued_value) = COUNT(*)` **per `(series_id, period_key)`, and only where `is_gapless = true`.** `WS-061` shows `currentPeriodKey` and Preview next number renders the post-reset number when the boundary has passed."*
- **Irreversibility:** **reversible in principle** — `V500020` predates `PNR-1` (`V500030`) but `whb_number_series_issued` is not covered by `L-2`'s `I-2` immutability trigger, so a later migration can add `period_key`, backfill it from `issued_at` and rebuild the index. **Land it in `V500020` anyway**: the collision surfaces at the first reset boundary in production, which is go-live + 12 months, by which time the backfill is a live-system index rebuild on the busiest audit table in the product.
- **Relationship to round 1:** **new.** `FR-426` is the only numbering requirement and is dispositioned COVERED; `C-019` covers only *"do not build this on the platform's scan-based generator"*. No finding examined the reset path.

---

### `Z-003` · The import framework has create-and-reverse semantics only: no master can be bulk-amended, and a corrected re-import has no defined behaviour — **MAJOR**

- **What is missing or wrong:** `P1-10` defines the handler contract as *"**Apply** creates the rows and records `createdEntityType`/`createdEntityId` per import row"* and *"**Reverse** removes exactly what a batch created, and is **refused** with a named blocker once any created entity has a movement"* (`p1-10.md:87`, `:89`). There is no update handler, no upsert semantics and no statement of what happens when an import row matches an existing `uk(owner_id, sku)`. Separately, `grep -rin "bulk edit\|bulk update\|mass update\|bulk change" docs/ issues/` returns **zero** — there is no bulk-edit action on any of the 51 master screens.

  So three ordinary operations have no path:
  - **The corrected file.** A customer sends a 40,000-row item master, then a corrected version with 300 fixed descriptions and 40 changed HSN codes. Create-only fails on the unique key for 39,700 rows; there is no stated upsert; and a reversal of the first batch is refused once any imported item has a movement.
  - **The bulk amendment.** Re-categorise 3,000 fasteners; change the reorder point at one site for a whole ABC class; set `lot_control_mode = REQUIRED` for every item whose `regulatory_class` is pharmaceutical (which `INDIA-LOCALISATION-PACK.md:995` says the regulatory class **forces**). Each of these is a per-row screen edit, 3,000 times.
  - **`Z-001`'s remediation.** Whatever shape the negative-stock policy takes, populating it for a real catalogue needs a bulk path.
- **Why it matters:** `FR-418` lists nine import kinds and the framework is presented as the answer to bulk work. It is not — it is the answer to *first* load. The gap is discovered on the implementation consultant's second week, when the customer's data cleanup arrives as a second spreadsheet, and the workaround is a `psql` `UPDATE` by whoever has the credentials — against a product whose entire premise is that data changes are recorded and attributable.
- **Negative evidence:**
  - `grep -rin "bulk edit\|bulk update\|mass update\|bulk change" docs/*.md issues/*.md` → **0**.
  - `grep -n -i "upsert\|update the existing\|matches an existing" issues/p1-10.md` → **0**.
  - `p1-10.md:87-89` — the two acceptance criteria quoted above are the whole handler contract.
- **Where it belongs:** `warehouse-base` · v1 · **P1**
- **Disposition:** *fold into task `P1-10`.* The lines to add: *"A handler declares a `mode` of `CREATE_ONLY`, `UPDATE_ONLY` or `UPSERT`, with the match key stated per import kind (`whb_items` matches on `(owner_id, sku)`). For `UPDATE_ONLY`/`UPSERT` the batch row records `beforeValueJson` per changed cell as `TEXT` (never JSONB — `DATA-MODEL.md` §1), which is what makes **Reverse** meaningful for an update: it restores the recorded prior values, and is refused where any field it would restore is frozen (`Z-004`). The dry run shows a per-cell before/after diff, not just a validation result. Master imports are the only bulk-amendment surface in v1; `WS-065`'s detail grid gains `changedCellCount`."*
  Bulk *edit from the grid* is deliberately **not** proposed: an import batch with a diff and a reversal is a better audit object than a multi-select toolbar action, and it reuses a framework that already exists.
- **Irreversibility:** **reversible** — `whb_import_batch_rows` is `V500046`, a work table with no ledger semantics.
- **Relationship to round 1:** **new.** `FR-416`–`FR-418` are dispositioned COVERED and `C-020` closed; no finding checked whether the framework's verbs cover amendment. Enables the remediation of `Z-001` and `Z-004`.

---

### `Z-004` · Fifty-one master screens, two immutability statements: the per-field freeze list does not exist — **MAJOR**

- **What is missing or wrong:** `grep -c "immutable" docs/BUILD-SPEC-SCREENS.md` → **2**. They are the
  registry `code` (`:545`) and `whb_items.base_uom_code` (`:815`, enforced by `I-9` at `V500036`).
  `awk` over the screen index counts **51 Department-shape master screens**. For 49 of them, and for
  every other field of the item, nothing states which fields become frozen once movements exist. The
  ones that will actually hurt, each with what the screen does today:

  | Field | Screen offers | What is unstated |
  |---|---|---|
  | `whb_item_uom_conversions.conversion_factor` | WS-026 plain Add/Edit, plus `isActive` | `L-7`/`IRR-34` freeze `conversion_factor_used` **on the line**, correctly. Nothing says what the *master* edit does to open reservations, `whb_item_packaging_levels`, reorder points expressed in that UoM, or a report that spans the change date. `IRR-34` says *"conversion factors are corrected over time"* — and then no screen rule follows |
  | `whb_items.lot_control_mode` | WS-023 select, no note (`:816`) | `NONE → REQUIRED` with 4,000 units on hand: the existing positions have `lot_id IS NULL` and the `L-5` grain now demands a lot. Is the change refused, or does it strand every pre-existing unit as unpickable? |
  | `whb_items.serial_control_mode` | WS-023 select, no note (`:817`) | same, and `IRR-14` already records that *the rows the wrong rule rejected were never written* — so retro-serialising has nothing to derive from |
  | `whb_items.code` | editable | `uk(code)` is *"the stable string key every FK and every bin label uses"* (`DATA-MODEL.md:2795`). A re-key invalidates printed bin labels and every external mapping |
  | `whb_items.category_id` | editable | `whb_valuation_policies` is keyed on `category_id`. Re-categorising an item mid-period silently changes its valuation method |
  | `whb_locations.code` | editable | `FR-034`'s own trap says *"a scan gun syncing 400 movements after a shift must not lose 399 because **one bin was renamed**"* — the design assumes bins get renamed and specifies nothing about the rename |
  | `whb_locations.location_type_code`, capacity | editable | changing a bin's type or capacity below its current contents has no rule |
  | `whb_valuation_policies.method` | effective-dated (correct shape) | no rule for what happens to existing `whb_cost_layers` on `AVCO → FIFO`, and no guard against an `effective_from` inside a closed period (`L-8` guards movements, not policy rows) |
- **Why it matters:** This is the day-400 question the lens exists to ask, and it is answered nowhere,
  so it will be answered by whichever developer writes each service — differently each time. The
  concrete moment: a parts manager corrects a case quantity from 12 to 6 because the supplier changed
  the pack; the screen accepts it; last year's stock report is now internally consistent and wrong, and
  `IRR-34` says exactly that failure is *"undetectable, because both numbers are internally
  consistent"* — it protected the ledger line and left the master edit wide open.
- **Negative evidence:**
  - `grep -c "immutable" docs/BUILD-SPEC-SCREENS.md` → **2**; `grep -n "immutable" docs/BUILD-SPEC-SCREENS.md` → lines 545 and 815.
  - `awk -F'|' '/^\| WS-[0-9]+ /{if ($0 ~ /\| D \|/) c++} END{print c}' docs/BUILD-SPEC-SCREENS.md` → **51**.
  - `grep -rn -i "frozen once\|cannot be changed\|no longer editable\|read-only once" docs/ issues/ | grep -v reviews` → only the base-UoM lines.
- **Where it belongs:** `warehouse-base` + `warehouse` · v1 · **P1**
- **Disposition:** *fold into `BUILD-SPEC-SCREENS.md` §2 as a per-master column, and into `P1-01`,
  `P1-02` and `P1-05` as acceptance criteria.* The line to add to the screen contract: *"Every master
  field table gains a **`Frozen when`** column with one of `never` · `once a ledger row exists` ·
  `once stock is on hand` · `once a movement in the current period exists`, and the modal renders the
  field read-only with a tooltip naming the reason. Where the freeze is load-bearing it is a database
  trigger, following `I-9`'s shape, not a service check."* The five fields above are the minimum set;
  `conversion_factor` and `lot_control_mode`/`serial_control_mode` are the two that need a trigger.
- **Irreversibility:** **reversible** — every one of these is a service/trigger addition on tables
  after `PNR-1`. But the *decision* is cheapest now: once a customer has amended a conversion factor
  in production, the correct behaviour is no longer a design choice, it is a data-repair project.
- **Relationship to round 1:** **new.** `FR-054`/`IRR-34`/`I-9` are the one instance that exists and
  are all dispositioned COVERED. R9 `H-004` is adjacent — it finds no enumerated *state machine* for
  31 P3–P6 status tables — but that is transitions between statuses, not amendment of master fields;
  this finding is the master-data half of the same omission and applies to v1·P1.

---

### `Z-005` · No catalogue value can ever be retired: the deactivation gate is undefined and, read against `L-2`, permanently closed — **MAJOR**

- **What is missing or wrong:** The shared contract for all fourteen registries says: *"Activate/Deactivate (`:edit`; deactivation refused where **a live row** references the code — the service returns `REGISTRY_ROW_IN_USE`) · Delete (`:delete` **and** `is_system = false` **and** zero references)"* (`BUILD-SPEC-SCREENS.md:549-550`, restated at `issues/p0-04.md:73`). The phrase *"a live row"* is used twice in the whole design set and **is never defined**. Against `L-2` — no posted line is ever updated or deleted — every `movement_type_code` and `stock_status_code` and reason code that has ever been used is referenced by a permanent row. So on the natural reading:
  - **Deactivate** is refused forever for every code that was ever used.
  - **Delete** is refused forever for the same reason (`zero references`).
  - The only codes that can be retired are the ones nobody ever used — which are exactly the ones nobody needs to retire.
- **Why it matters:** Day 400, the stock controller. Go-live seeded 18 adjustment reason codes; six were mis-specified, three are the customer's old vocabulary and two are duplicates of each other. Every one of them is still in every dropdown, on the mobile picker, in the filter list and in the export, forever, and the storekeeper picks the wrong one weekly. The same applies to an owner-specific stock status registered by an adapter that has since been decommissioned, and to a location type from a warehouse layout that no longer exists. This is the single most common master-data maintenance request in a stock system and the product's answer is *no*.

  The set already contains the correct pattern, one page away: `FR-057` gives the barcode registry *"a status that **retires a code without deleting scan history**"*. The registries needed the same sentence and did not get it.
- **Negative evidence:**
  - `grep -rn "REGISTRY_ROW_IN_USE\|live row" docs/ issues/ | grep -v reviews` → **4 hits**; two are the registry clause, one is `FR-422`'s position-table sizing, one is `p2-28`'s superseded-report index. **"Live row" is nowhere defined.**
  - `grep -rn -i "retire" docs/ issues/ | grep -v reviews` → `FR-057` (barcode) and `BUILD-SPEC-SCREENS.md:524` (`WH-SC-262`). **Nothing for the fourteen registries.**
  - `DECISIONS.md` `D-10` and `IRREVERSIBLE.md` §5 define the registry shape — `code`, `name`, `owning_module`, `is_system`, behaviour flags — and specify no retirement semantics.
- **Where it belongs:** `warehouse-base` · v1 · **P0** (`P0-04`/`P0-05` own the fourteen registries)
- **Disposition:** *fold into task `P0-04`.* The lines to add: *"**Deactivation is a retirement, not a delete.** `is_active = false` means **the code may no longer be selected on a new document**; it does **not** mean it is unreferenced. Deactivation is therefore **always permitted** and never returns `REGISTRY_ROW_IN_USE`. Historic rows continue to render the code's `name` and `badge_variant` exactly as before (`FR-381`), and the grid, filter and export continue to offer it as a filter value so a five-year-old document is still findable. The dropdown endpoint returns active rows only, **plus** the currently-selected value when editing an existing row, so an old document does not silently lose its code on save. `REGISTRY_ROW_IN_USE` is retained for **Delete** only — `:delete` and `is_system = false` and zero references — where it is correct, and the refusal message names the referencing table and count. `WS-…` gains an `isActive` filter defaulting to active."*
- **Irreversibility:** **reversible** — a service-layer rule and a dropdown query; no schema change. It should still land in P0, because fourteen registry screens will otherwise be built with the wrong gate and the fix is fourteen services.
- **Relationship to round 1:** **new.** `FR-375`/`FR-376`/`D-10` are dispositioned COVERED. R11 `Y-007` covers the *absence* of a deactivation guard on locations, owners and warehouses; this is the opposite defect on a different object — a guard that is present and too wide — and the two remediations must be written together so the product does not end up with no guard where it needs one and an absolute one where it does not.

---

### `Z-006` · The archive's cut-off has no retention policy to read outside India, and nothing is ever disposed of — **MAJOR**

- **What is missing or wrong:** Three linked gaps in the disposal story:
  1. **`P6-01` depends on a module that a reference install does not have.** It states *"`P4-09`'s two retention clocks — the Companies Act's financial years and the GST period — are what decide the earliest legal cut-off, and the archive refuses a cut-off that violates either."* Those clocks live in `whin_retention_policies`, which `DATA-MODEL.md:1215` and `WIN-20`/`V540170` place in **`warehouse-india`, v2**. `D-7` makes **standalone** — platform + `warehouse-base` + `warehouse`, no vertical, no India pack — the reference configuration. On that install the archive has no policy to consult and, by its own rule, no legal cut-off it can accept.
  2. **Nothing is ever disposed of.** The archive *moves* rows to `whb_stock_movements_archive` in the same database. `grep -rin "purge" docs/ issues/` returns one hit, `p3-23`'s sandbox purge, which is a test-data feature. At end of retention there is no delete path, no legal-hold release path and no statement that one is deliberately declined. The archive tables are as unbounded as the hot tables were.
  3. **Closing a site has no administrative journey.** `grep -rin "close a site\|site closure\|closing a warehouse\|decommission" docs/ issues/` returns one hit, in `COEXISTENCE.md` about decommissioning *accessories*. `whb_warehouses` has an `isActive` toggle and that is the entire specification. Beyond the stock (which R11 `Y-007` correctly says has no guard at all), a site being closed has open goods receipts, in-transit stock inbound to it, a per-site `whb_number_series` row, warehouse-scoped user grants from `P1-18`, `whb_devices`, open `whb_tasks` and `whb_reservations` — and no screen tells the administrator about any of them or in what order to clear them.
- **Why it matters:** Gap 1 bites in v3, at the first customer large enough to need archiving, and it bites as *"the archive refuses every cut-off"* with no obvious cause. Gap 2 is the question a CIO asks in the security review before signing: *"what is your data-disposal policy"* — and the honest answer today is *"we move it to another table in the same database and keep it forever."* Gap 3 bites the day a dealer group closes a branch: someone deactivates the warehouse, and either the toggle succeeds and orphans in-transit stock and a live number series, or it fails with a message that names one blocker at a time across six unrelated tables.
- **Negative evidence:**
  - `grep -rn "retention" docs/ issues/ | grep -v reviews` → the only policy table is `whin_retention_policies`; `WS-190` is `india · v2 · P4` (`BUILD-SPEC-SCREENS.md:442`).
  - `grep -rin "purge" docs/ issues/ | grep -v reviews` → **1 hit**, `issues/p3-23.md:51` (sandbox).
  - `grep -rin "close a site\|site closure\|closing a warehouse\|decommission" docs/ issues/ | grep -v reviews` → **1 hit**, `COEXISTENCE.md:650`, about accessories.
  - The Companies Act figure **is** correctly stated — 8 financial years, `INDIA-LOCALISATION-PACK.md:59` and `:806`, flagged `RE-VERIFY` — so the statutory minimum is named; it is just named in the wrong module.
- **Where it belongs:** `warehouse-base` · v1 (the base policy table and the site-closure runbook) · v3 (`P6-01` reads it)
- **Disposition:** *fold into `P4-09` and `P6-01`, and into `P1-05`.*
  - `P4-09` — add: *"the retention **table** is `warehouse-base` (`whb_retention_policies`: scope, clock kind, duration, legal-hold flag) with a country-neutral default of the longest applicable statutory period; `warehouse-india` **seeds** the two Indian clocks into it and adds the GST-specific report. India owns the clocks it knows about, not the mechanism."*
  - `P6-01` — add: *"on an install with no retention policy row the archive refuses with `NO_RETENTION_POLICY` and names the screen to configure — never a silent default cut-off. **Disposal at end of retention is explicitly out of scope for v3 and the reason is recorded**, because a delete against an append-only ledger needs the same privileged, audited path as the archive's own `DELETE` half and is a task in its own right."*
  - `P1-05` — add: *"deactivating a `whb_warehouses` row runs a **closure pre-check** that returns every blocking class at once — on-hand stock, in-transit inbound, open receipts and orders, open tasks and reservations, an active number series, warehouse-scoped user grants, assigned devices — with a count and a link per class. It is a screen, not a sequence of one-at-a-time refusals."*
- **Irreversibility:** **reversible** — `whb_retention_policies` would take a number from the declared `V500064`–`V500199` post-v1 base DDL gap, the same gap `WHB-66` already draws on.
- **Relationship to round 1:** **extends** `S-051`/`FR-329` (dispositioned COVERED) by one fact they do not carry: the policy table's *module* makes it unavailable to `D-7`'s reference configuration. The site-closure paragraph **extends R11 `Y-007`** — `Y-007` establishes that no deactivation guard exists on a warehouse; what is new here is that even with the guard there is no administrative journey, and that six non-stock object classes block a closure and none of them is enumerated anywhere.

---

### `Z-007` · Two duplicate items, or two duplicate counterparties, have no merge path — and a 40,000-SKU import against `uk(owner_id, sku)` produces them on day one — **MAJOR**

- **What is missing or wrong:** `whb_items` is `uk(owner_id, sku)` plus a global `uk(code)`. Nothing prevents the same physical part arriving twice under two SKUs — from two source systems, from the accessories cross-map, or from a supplier catalogue loaded alongside the customer's own. `whb_counterparties` has the same exposure and is worse: one supplier routinely arrives as three rows from three feeds. There is no merge action, no merge screen, no `merged_into_id` column and no statement that merging is declined.

  Two nearby things are **not** this, and should not be mistaken for it:
  - **`whb_item_supersessions` with `stockTreatment = MERGE_STOCK`** (`BUILD-SPEC-SCREENS.md:900`, gated on `whb_item_supersessions:merge`) models a **part being replaced by its successor** — it has an `effectiveDate`, a `quantityRatio` and a `chainSequence`, and it leaves both items live and orderable. That is a supersession, not a de-duplication, and nothing says it may be used for one.
  - **Lot split and merge** *is* properly specified — `whb_lots` self-FK *"split or merge parent"* (`DATA-MODEL.md:1714`) and `whb_transformations` recording genealogy at the moment of transformation (`:573`). The third item on the user's list is the one that is covered.
- **Why it matters:** The implementation consultant finds the duplicates during the parallel count, in the week before go-live. With no merge, the choices are: reverse the whole opening batch and re-import (which `Z-008` says may not work), or go live with two item rows for one shelf — which is the exact defect `COEXISTENCE.md` `C1` spends four pages costing for the accessories split, applied inside the new product. After go-live it is worse: both rows now carry movements, and `L-2` means the movements cannot be re-pointed, so a merge is necessarily a **transfer to the survivor plus a deactivation of the loser**, which is a design decision nobody has taken.
- **Negative evidence:**
  - `grep -rn -i "\bmerge\b" docs/ issues/ | grep -v reviews` → 30 hits: `COEXISTENCE.md`'s accessories merge analysis, Hibernate `cascade = MERGE`, lot split/merge, the supersession `MERGE_STOCK` treatment, and document/branch merges. **Nothing about duplicate item or counterparty records.**
  - `grep -rn -i "deduplicat\|duplicate item master\|duplicate counterpart" docs/ issues/ | grep -v reviews` → only `COEXISTENCE.md:195` `C1`, which is about the accessories/warehouse split.
  - `grep -rn "merged_into\|merge_target\|surviving_id" docs/ issues/` → **0**.
- **Where it belongs:** `warehouse-base` · v1 · **P1**
- **Disposition:** *new task needed*, next free id **`P1-21`** (`grep -l "^TITLE" issues/p1-*.md | wc -l` → the P1 series currently ends at `p1-20`). It contains: a `whb_master_merges` record (`entity_type`, `losing_id`, `surviving_id`, `merged_by`, `merged_at`, `reason`, `moved_stock_movement_id`); a pre-check screen listing everything that references the loser; for items, a **stock transfer to the survivor posted as a real movement through the port** with a dedicated reason code — never a re-pointing of history, which `L-2` forbids; deactivation of the loser with a redirect so a scan of the loser's barcode or SKU resolves to the survivor; and an explicit **refusal** to merge where the two rows differ in `base_uom_code`, `lot_control_mode` or `serial_control_mode`, because those are not reconcilable by a transfer. Counterparty merge is simpler and can share the record. **Alternatively `WONTFIX` for v1 with the reason written down** — but silence is not one of the options, because the implementation team will otherwise do it in `psql`.
- **Irreversibility:** **reversible** — a new table in the post-v1 base DDL gap and a movement posted through the existing port.
- **Relationship to round 1:** **new.** `COEXISTENCE.md` `C1` and `C11` cost the *cross-module* duplicate at length and `M1` mitigates it with a cross-map; nothing addresses a duplicate **within** `whb_items`.

---

### `Z-008` · `P2-19` delegates opening-stock reversal to a framework path whose own acceptance criterion refuses it — **MAJOR**

- **What is missing or wrong:** `p2-19.md:22` says *"The whole batch is **reversible** through `P1-10`'s import-framework reversal path"*, and its acceptance criterion `:90` repeats it. `p1-10.md`'s acceptance criterion for that same path says: *"**Reverse** removes exactly what a batch created, and is **refused** with a named blocker once any created entity has a movement."* An opening-stock batch's created entities **are** movements — 38,000 `OPENING_BALANCE` movements, per `WH-SC-049`. Read literally, the framework refuses every opening-stock reversal that has ever been posted.

  The two tasks are describing different mechanisms and neither says so:
  - The **import framework's** reversal is *"delete the rows this batch created"* — right for an item master, and `p1-10`'s own trap says a framework whose reversal is a delete *"fails the moment an imported item has a movement"*.
  - The **opening batch's** reversal must be an `L-3` **ledger reversal**: 38,000 mirrored lines with a mandatory reason code, the originals marked reversed, the cost layers unwound. `WH-SC-049` requires it to work, and `L-2` forbids the delete.

  Which one `WS-150`'s **Reverse** button does, and what it does to `whb_cost_layers` and to the `wh_cutover_checklists` row that was already certified against the old number, is unstated.
- **Why it matters:** This is the highest-stakes recovery path in the product and it is the one the user named: *"a reversal of 40,000 opening lines is a real event."* It happens on the Monday of go-live, when the tie-out variance is ₹4.2 lakh and the customer will not sign the certificate. If the implementer builds the framework reversal, the button is refused and the only remedy is a hand-written correction batch; if they build the ledger reversal without saying so, `P1-10`'s architecture test for "reversal refused once any created entity has a movement" fails on the one batch kind that matters.
- **Negative evidence:**
  - `grep -n -i "revers" issues/p2-19.md` → lines 13, 22, 36, 47, 62, 90 — all delegate to the framework, none describes mirrored ledger lines or a reason code.
  - `issues/p1-10.md:89` — the refusal criterion, verbatim.
  - `grep -n "L-3\|reason code" issues/p2-19.md` → **0**. The `L-3` reversal invariant is never named in the task that most needs it.
- **Where it belongs:** `warehouse` · v1 · **P2**
- **Disposition:** *fold into task `P2-19`.* The line to add: *"**Reverse on a `POSTED` opening batch is an `L-3` ledger reversal, not the import framework's row-delete.** It posts a mirrored `OPENING_BALANCE` movement per original through the single writer service with a mandatory reason code, unwinds the cost layers created by the batch, moves the batch to `REVERSED`, and **reopens the `wh_cutover_checklists` row**, invalidating any certificate already issued against the reversed number. `P1-10`'s framework reversal applies to the batch in `DRAFT`/`VALIDATED` only, where nothing has posted — and `P1-10`'s acceptance criterion is amended to say so, so the two tasks do not test each other's behaviour."*
- **Irreversibility:** **reversible** — behaviour in two services; `V510090` and `V500046` are unaffected.
- **Relationship to round 1:** **new.** `S-079`/`FR-411`–`FR-413` are dispositioned COVERED and `P2-19` is one of the best-written task files in the set; the contradiction is only visible by reading it against `P1-10`.

---

### `Z-009` · No master load order is stated, and the cut-over checklist collapses it into one tick — **MINOR**

- **What is missing or wrong:** `wh_cutover_checklists` items are *"masters loaded ✔ · mappings resolved ✔ · opening posted ✔ · value matched ✔ · period opened ✔"* (`DATA-MODEL.md:1101`, `WH-SC-050`). "Masters loaded" is one atomic item. The actual order is forced by the foreign keys and is nowhere written down: UoMs and the fourteen registries → item categories → owners → items → item identifiers and packaging levels → UoM conversions → counterparties and their role links → warehouses → locations (or the `P1-06` generator) → item × site settings → item × location settings → number series → **then** opening stock. An implementer who loads items before UoMs gets 40,000 FK violations and no guidance on which file to fix.
- **Why it matters:** It costs a day of the go-live weekend, once per customer, and the freeze window (`FR-413`: *"the count happens on a Sunday and go-live is Monday; anything that moves between is manual"*) is exactly one weekend long.
- **Negative evidence:** `grep -rn -i "load order\|loaded in the order\|in this order" docs/ issues/ | grep -v reviews` → 3 hits: `MODULE-INTEGRATION.md:987` (module install order), `IRREVERSIBLE.md:297` (the four points of no return), `WH-SC-263` (packaging resolution order). **None is a master load order.**
- **Where it belongs:** `warehouse` · v1 · **P2**
- **Disposition:** *fold into task `P2-19`.* The line to add: *"`wh_cutover_checklist_items` is **seeded with one `is_blocking` row per master in dependency order**, not one 'masters loaded' row: UoMs and registries → item categories → owners → items → identifiers and packaging → UoM conversions → counterparties and roles → warehouses → locations → item × site → item × location → number series. `WS-151` renders them in `sequence` and refuses to complete an item whose predecessor is open."*
- **Irreversibility:** **reversible** — `wh_cutover_checklist_items` already carries `sequence` and `is_blocking` (`DATA-MODEL.md:1102`); this is seed content, not schema.
- **Relationship to round 1:** **new**, and a small extension of `FR-413`'s runbook, which is dispositioned COVERED.

---

### `Z-010` · Not one operational role is seeded: storekeeper, picker, supervisor, stock controller and 3PL client exist as actors and as nothing else — **MINOR**

- **What is missing or wrong:** `P0-15`/`V501000` seeds permissions and grants for **ADMIN**, **ADMIN_GROUP**, **AUDITOR** and, at `V501001`, the dependency rows; `FR-403` re-takes the Branch Admin decision. Those are four platform roles. The FRD's actor table (`WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md:78`) and the scenario catalogue's cast (`SCENARIO-CATALOGUE.md:143` — `stores1`, `stores2`, `sup1`) name storekeeper, operator, supervisor, stock controller and 3PL client, and `FR-284` calls the client portal *"a permission surface over the existing screens"*. **No role row, no `role_permissions` grant and no permission set is defined for any of them.** Every install decides for itself whether a picker may post an adjustment.
- **Why it matters:** `FR-408` says *"a transition with no verb permission is a transition anybody with `:edit` can perform"* — `P0-15` fixes that at the permission level and then leaves the *bundle* undefined, so the first implementation grants a storekeeper `ADMIN` because it is 6pm on go-live Sunday and the pick list will not print. It also makes `WH-SC-243`'s branch-scope test ambiguous: `stores1` is described as *"granted warehouse access to `SITE-A` only"* with no statement of what else `stores1` holds.
- **Negative evidence:**
  - `grep -rn -i "storekeeper\|stock controller" docs/ issues/ | grep -v reviews` → 14 hits, all prose, scenario casts or the actor table. **No seed.**
  - `issues/p0-15.md` §Scope and §"The role decisions that must be re-taken" name ADMIN, ADMIN_GROUP, AUDITOR and Branch Admin **only**.
  - `grep -rn "role_permissions" docs/ issues/ | grep -v reviews` → 2 hits, both about the back-fill mechanism, neither naming an operational role.
- **Where it belongs:** `warehouse-base` · v1 · **P0**
- **Disposition:** *fold into task `P0-15`.* The line to add: *"`V501002` seeds four warehouse roles as **starting bundles**, documented as a customer-editable starting point and not as a security boundary: **Storekeeper** (every `:view`, receipt/putaway/pick/count execution, no `:approve`, no `:reverse`, no `:close`, no `:override`), **Supervisor** (Storekeeper + `whb_stock_movements:approve`, `whb_locations:block`, task reassignment, count-variance approval — and never approval of their own count, per `FR-408`), **Stock Controller** (masters `:create`/`:edit`, `whb_stock_periods:close`/`:reopen`, valuation and adjustment approval, `whb_stock_positions:rebuild`), **3PL Client** (`:view` filtered to their own `owner_id`, plus ASN and outbound-order create — the `FR-284` portal bundle). Every insert guarded `WHERE NOT EXISTS`; the grants are `role_permissions` rows, never a new permission."* If the set prefers to leave this to the implementer, that is a legitimate answer — but `D-7`'s standalone reference configuration then ships with no way to give anyone less than ADMIN, and that should be written down.
- **Irreversibility:** **reversible** — role seeds are forward-only inserts and a later migration can add or amend them; unlike a permission *name* (`FR-407`/`IRR-63`), a bundle is not retro-granting work.
- **Relationship to round 1:** **new.** R8 `Q-003` covers whether AUDITOR receives `:export` — a different question about a role that at least exists. `P-014`/`C-017`/`FR-401`–`FR-403` are all about permission naming and dependency mechanics, not bundles.

---

## §3 · What I checked and found sound

Listed so round 3 does not re-walk this ground.

| What I went looking for | Where it is covered |
|---|---|
| Opening stock as a first-class object, not a script | `P2-19` · `FR-411` · `wh_opening_stock_batches`/`_lines` (`DATA-MODEL.md:1099-1100`) · `WH-SC-049` |
| Batch status ladder `DRAFT → VALIDATED → POSTED → REVERSED` | `p2-19.md:13` |
| Dry run that persists nothing, **asserted by row count on both tables** | `p1-10.md` acceptance 1 · `FR-417` · `WH-SC-047`/`WH-SC-048`. The known "validate persists → duplicate rows" defect is named as a trap |
| Per-row, per-cell error report with a stable error vocabulary | `whb_import_batch_rows.errorCode` from `FR-039`'s vocabulary |
| Opening stock posts as `OPENING_BALANCE` from `VIRT-OPENING`, never a position `UPDATE` | `p1-10.md` traps · `WH-SC-049` · `FR-436` single-writer |
| Opening stock creates the **first cost layer** | `p2-19.md:47` |
| Closing-value tie-out and a signed reconciliation certificate that gates the period open | `WH-SC-050` · `FR-412`/`FR-413` · `WS-151` **Certify** blocked while any `is_blocking` item is open |
| Idempotent ingestion, caller-supplied key, `uk(source_system, idempotency_key)` spanning cut-over and steady state | `L-9` · `PORT-AND-ADAPTER-CONTRACT.md:1703` |
| Import re-runnable after a failure | `p2-19.md:90` |
| Reference preload so a 50,000-row import is not an N+1 | `p1-10.md` traps (CLAUDE.md CRITICAL #5) |
| Import date parsing as a SQL `DATE` with no timezone shift | `p1-10.md` traps · `FR-327` |
| Cut-over from `accessories`, costed, with nine merge-free mitigations and a cross-map from v1 | `COEXISTENCE.md` §5, §7 · `M1` · `WS-031` with its `UNMAPPED` tile |
| Migration from Tally / Busy / Marg with saveable mapping profiles | `S-080` → `P3-18`, and **its mis-phasing is already filed** at `GAP-REGISTER.md` §7 row 5 |
| Base stocking UoM immutable once a ledger row exists, by **trigger** not service | `FR-054` · `I-9` · `V500036` · `IRR-34` |
| Conversion factor frozen **on the movement line** | `L-7` · `IRR-34` · `whb_stock_movement_lines.conversion_factor_used` "frozen at post" |
| Registry `code` immutable after create, read-only on edit | `BUILD-SPEC-SCREENS.md:545` |
| Deactivating an **item** with non-zero on-hand blocked, with an offered alternative | `FR-051`, and `DATA-MODEL.md` §6.5 explains correctly why it is a service check and not a trigger |
| A retired barcode keeps its scan history | `FR-057` — the pattern `Z-005` says the registries should have copied |
| A newly registered catalogue value renders everywhere with no code change, i18n falling back to the row's `name` | `WH-SC-147` · `FR-381`/`FR-382` · `D-10` |
| Catalogue seeds idempotent and safe on a Flyway retry | `WH-SC-292` · `FR-356` · `p2-25.md:92` |
| No down-migrations; a reversal is a forward migration in the same band | `MODULE-INTEGRATION.md:1069` |
| Lot split and merge, with genealogy recorded at the moment of transformation | `whb_lots` self-FK (`DATA-MODEL.md:1714`) · `whb_transformations` (`:573`) · `FR-105` |
| Ledger partitioned `BY RANGE (occurred_at)` monthly **from migration one**, with the auto-partition job | `FR-022` · `IRR-62` · `DATA-MODEL.md` §1.9, including the PK consequence |
| Archiving is a transaction: `OPENING_BALANCE` at the cut-off **first**, rows moved second | `FR-023` · `P6-01` · `T-020a`. The `L-2`-trigger and sealed-`UPDATE` traps are both named |
| Statutory retention in India named and quantified | 8 financial years + GST 72 months, `INDIA-LOCALISATION-PACK.md:58-59`, `:806`, both flagged `RE-VERIFY` |
| Retention beats erasure, by pseudonymising the person and never the quantity | `FR-441` — stated once, deliberately |
| Performance targets stated so volume can be tested against something | `FR-422` — 1M ledger rows/day peak, position table ≤ 5M live rows |
| Gaplessness under a rolled-back transaction | `I-20` — the number is taken in the caller's transaction under `FOR UPDATE`, so a rollback releases it |
| `current_value` not hand-editable | `BUILD-SPEC-SCREENS.md:1243` — read-only in the modal, with the reason |
| GL posting rules resolved most-specific-first, with a **Test resolution** modal | `FR-246` · `WS-051` · `whb_gl_posting_rules.specificity` — **the exemplar `Z-001` asks the other three to copy** |
| Putaway rules evaluated in an explicit sequence | `wh_putaway_rules uk(warehouse_id, sequence)` · `FR-135` |
| Valuation method effective-dated rather than switched in place | `whb_valuation_policies.effective_from`/`_to` · `OD-6` |
| `@PreAuthorize` on every method, verb permissions enumerated, AUDITOR never holding one | `P0-15` · `FR-401` · `FR-408` · `WH-SC-241`/`WH-SC-245` |
| `permission_dependencies` inserted, never created; `dependent_permission_id` named correctly | `FR-402` · `C-017` · `p0-15` traps |
| The `logistics:*` namespace reserved in v1 so v2 does not retro-grant every role | `FR-346`/`FR-407` · `IRR-63` |
| Warehouse-scoped access as a record-level `WHERE` predicate, not a menu filter | `FR-404`/`FR-405` · `P1-18` · `WH-SC-243` |

---

## §4 · Refused

| Candidate | Why not filed |
|---|---|
| The migration-mapping profiles (`wh_migration_mappings`, `FR-414`) land in **v1.1·P3**, after the first customer needs them | Already filed — `GAP-REGISTER.md` §7 row 5: *"`S-080` sits in P3, after the first customer would need it."* |
| No deactivation guard on a location, an owner or a warehouse that holds stock | R11 **`Y-007`**. `Z-006`'s third paragraph cites it and adds only the administrative journey and the six non-stock blocking classes |
| Archiving must write an opening-balance row or reconstructibility dies | Round 1 **`T-020a`**, and `FR-023`/`P6-01` implement it correctly |
| The archive-run record has no allocated table | `DESIGN-SET-DEFECTS.md` §6.4 **R-3** — deliberately left to `P6-01` |
| The value-offset virtual location has two names and `FR-084` seeds neither | **`X-029`** |
| No `L-15` / `I-n` row for value conservation | **`X-030`** |
| Eight report and archive tables have no `DATA-MODEL.md` row | **`X-053`**, and largely remediated per `GAP-REGISTER.md` check-3 |
| `is_taxable_supply` frozen at creation (`OD-9`) and the decision's deadline falling after the task that builds it | R10 **`U-003`** owns `OD-9` |
| Status domains undeclared for 30 v1 tables | R8 **`Q-002`** |
| No enumerated state machine for 31 P3–P6 status-bearing tables | R9 **`H-004`**. `Z-004` is the master-field half and is scoped to v1·P1 masters |
| **Parallel running** for a month with automated divergence detection | Deliberate `WONTFIX` for v1. `COEXISTENCE.md` already builds the only parallel-run the product actually faces (warehouse alongside accessories) with `M1`–`M9`, and a generic dual-run reconciler against an arbitrary incumbent is a consulting deliverable, not a product feature. The freeze-count-load-verify runbook of `FR-413` is the right-sized answer for a weekend cut-over |
| A generic **competitor import shape** beyond `S-080`'s mapping profiles | Same reason. `S-080` + `P1-10`'s handler registry is the correct mechanism; a Tally-specific parser in the product would be one per incumbent, forever |
| **Bulk edit from the grid** with multi-select and a toolbar action | Deliberately not proposed. `Z-003` routes bulk amendment through the import framework instead, because a batch with a per-cell diff and a reversal is a better audit object than a multi-select, and it reuses a framework that already exists |
| `FOR UPDATE` on the series row serialising every document creation at `FR-422`'s 1M rows/day | Non-functional — R13's lens, not this one. Named here only so it is not lost |
| `whb_number_series_issued` growing unbounded | Subsumed by `Z-006`'s disposal gap; not worth a row of its own |
| The India retention figures are flagged `RE-VERIFY` | The set flags them itself, correctly and visibly. A reviewer re-verifying a statute from memory would be worse than the flag |

---

## §5 · Counts

```
$ grep -c "^### \`Z-" docs/reviews/R12-lifecycle-and-data-migration.md
10
$ grep "^### \`Z-" docs/reviews/R12-lifecycle-and-data-migration.md | grep -c "BLOCKER"
2
$ grep "^### \`Z-" docs/reviews/R12-lifecycle-and-data-migration.md | grep -c "MAJOR"
6
$ grep "^### \`Z-" docs/reviews/R12-lifecycle-and-data-migration.md | grep -c "MINOR"
2
```

| Severity | Count | Findings |
|---|---|---|
| **BLOCKER** | 2 | `Z-001` `Z-002` |
| **MAJOR** | 6 | `Z-003` `Z-004` `Z-005` `Z-006` `Z-007` `Z-008` |
| **MINOR** | 2 | `Z-009` `Z-010` |
| **Total** | **10** | `Z-001`…`Z-010` |

**Disposition shape:** 8 fold into an existing task (`P0-04`, `P0-13`, `P0-15`, `P1-03`, `P1-05`,
`P1-10`, `P2-07`, `P2-19`, `P4-09`, `P6-01`), 1 needs a new task (`P1-21`, `Z-007`), 1 also needs a
`DATA-MODEL.md` §2.1 amendment (`Z-001`). **Zero** require a decision `D-`/`OD-` row.
**Irreversibility:** all ten are reversible; `Z-002` should nonetheless land in `V500020` because its
failure surfaces twelve months after go-live, on the busiest audit table in the product.
