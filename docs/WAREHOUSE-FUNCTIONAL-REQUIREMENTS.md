# Warehouse — functional requirements

**v1.1 · 2026-09-01** — reconciled against `DECISIONS.md`'s rewritten `D-6`, the four ladder
amendments `A-1`…`A-4` in §5.1, the revised `OD-6` and the new rule §7.4a. **No published `FR-nnn`
was renumbered** (§7.4); the four requirements the amendments required are appended as §6.26 at
`FR-443`–`FR-446`. §8 carries a before-and-after table of exactly what each amendment moved.

> **Round-2 amendment · 2026-09-02.** `GAP-REGISTER-R2.md` §5 added thirteen requirements as **§6.27,
> `FR-447`–`FR-459`**, on the same no-renumbering rule. Nine give a round-2 finding somewhere to live;
> four give the four tasks `GAP-REGISTER.md` §4.1 proposed in round 1 and nobody authored (`P3-24`,
> `P4-13`, `P5-22`, `P5-23`) the requirement each needs before its plan row can cite one. §7's two
> traceability commands were widened in the same commit to read the round-2 prefixes and review files.

> **Precedence.** [`DECISIONS.md`](DECISIONS.md) wins over this document on module names, packages,
> Flyway bands, table prefixes, id namespaces, the version ladder and the phase map.
> [`reviews/R1-codebase-reality.md`](reviews/R1-codebase-reality.md) wins over everything on any
> question about what the *existing* `neetub1508/classic` codebase does, because it carries
> `file:line` evidence. Where this document and a review disagree, the disagreement is stated in the
> requirement row and the reason is given. Nothing is silently resolved.

---

## 1. What is being built

A **standalone-capable, country-neutral warehouse and inventory-management product**: one immutable,
double-sided, append-only stock ledger at full grain, the application layers that write to it, and a
generic inbound movement port so that any number of future consumers — a logistics/TMS module, a
supply-chain module, a POS, an eCommerce channel, or any vertical in the suite — can move stock
**without `warehouse-base` ever depending on them**.

Five modules (`D-1`):

| Module | Package | Flyway band (`D-2`) | Prefix (`D-3`) | Depends on | Ships |
|---|---|---|---|---|---|
| `warehouse-base` | `ai.warehousebase` | V500000–V509999 | `whb_` | **platform only** | v1 |
| `warehouse` | `ai.warehouse` | V510000–V519999 | `wh_` | platform + base | v1 |
| `warehouse-adapter-<vertical>` | `ai.warehouseadapter<vertical>` — a **sibling** | V520000–V529999 (sub-banded) | `whad_` `whas_` `whaf_` `whaa_` | platform + base + that vertical | v1 → v2 |
| `warehouse-3pl` | `ai.warehouse3pl` | V530000–V539999 | `wh3_` | platform + base + app | v2 |
| `warehouse-india` | `ai.warehouseindia` | V540000–V549999 | `whin_` | platform + base + app | v1 · v2 |

It is not a replacement for anything currently shipping. It is the **first real stock ledger in this
suite**: `services`, `field-service` and `assets` have no stock capability at all (`C-034`), and
`services.parts_used` is free `TEXT` (`R5` Fact 2).

## 2. How to read a requirement row

Every requirement carries six things.

| Column | Meaning |
|---|---|
| **#** | `FR-nnn`. Contiguous from `FR-001`. Never renumbered, never reserved as a gap |
| **Requirement** | Behaviour a user or a system observes. Load-bearing invariants name their `L-n` |
| **Module** | `base` = `warehouse-base` · `app` = `warehouse` · `adapter` · `3pl` = `warehouse-3pl` · `india` = `warehouse-india` · `mobile` · `platform` |
| **Ver** | `v1` · `v1.1` · `v2` · `v3` — the release unit (`D-12`, §5 of `DECISIONS.md`) |
| **Ph** | The delivery unit. `v1`→`P0`/`P1`/`P2`/**`P2-IN`** · `v1.1`→`P3` · `v2`→`P4`/`P5` · `v3`→`P6`. **`P2-IN`** is the v1 India wave added by `DECISIONS.md` `A-4`; a row may carry two v1 phases (`v1·v1` / `P1·P2-IN`) where a base column and an India document land in the same release at different times |
| **Closes** | The `C-`/`T-`/`E-`/`F-`/`S-`/`P-`/`G-` findings it closes, or the `D-n` it derives from |

**A row that says `v1` and `P0` with no v1 screen is deliberate.** Forty of R4's v1 items are columns,
keys or seeded tables carrying no v1 screen at all (R4 §2.10), and twenty-eight of R5's are the same
(R5 *"CANNOT BE ADDED LATER"*). They are here because a ledger cannot be retro-fitted with a dimension
it never recorded.

**`⛔ OD-n`** marks a requirement whose shape depends on an open decision in `DECISIONS.md` §3. It is
still a requirement; it is not yet buildable.

## 3. Deployment modes

| Mode | Composition | Status |
|---|---|---|
| **A** | platform + `warehouse-base` + `warehouse` | **The reference implementation** (`D-7`). Every v1 requirement must work here with no vertical and no accounting module |
| **B** | Mode A + a vertical + its adapter | v1. Two adapters (dealer parts, services), because one adapter proves nothing (`D-11`, `E-006`) |
| **C** | Mode A + `accounting` | v1. Warehouse hands over **already-valued** movements and accounting posts them without re-costing; warehouse never writes an `acc_*` table (`D-6`) |
| **D** | Mode A + `warehouse-india` | **v1** for the documents that let goods move legally, **v2** for the statutory registers (`A-4`). Every India rule is data or lives in this module (`D-8`) |
| **E** | Mode A + `warehouse-3pl` | v2. A thin module on a wide v1 base concession (R4 §5) |
| **F** | platform + `warehouse-base` only | A ledger with no application. Legitimate: an adapter posts, nobody uses receiving or picking |

Mode F is why the split proof matters. If any FK points from `warehouse-base` up into `warehouse`,
an adapter, `warehouse-3pl` or `warehouse-india`, Mode F does not install.

## 4. Actors

| Actor | Is | Notes |
|---|---|---|
| **Storekeeper / operator** | a person | Receives, puts away, picks, packs, counts. Lives on a handheld, not a desk |
| **Warehouse supervisor** | a person | Assigns tasks, resolves exceptions, approves variances within tolerance |
| **Warehouse manager** | a person | Adjustments above threshold, write-offs, period close, count approval |
| **Inventory controller** | a person | Counting programmes, reason-code administration, reconciliation |
| **Buyer / parts manager** | a person | Replenishment, purchase documents, supersession, KPIs |
| **Finance / controller** | a person | Valuation, the handover queue, the stock-to-GL reconciliation |
| **Auditor** | a person | **Read-only across everything**, including the ledger. Never a writer (`P-014` — the prior module's AUDITOR exclusion is not inherited and must be re-taken) |
| **3PL client user** | a person | Portal-scoped, owner-bound, `PORTAL` grant only (`F-004`, `F-008`) |
| **Integration** | a system principal | Posts through the movement port. Owns an `idempotency_key` namespace via its `source_system` |
| **Device** | a system principal | A scan gun, an RFID portal, a dock terminal, a boom barrier. `actor_type = DEVICE` + `device_id` |
| **Scheduler** | a system principal | Runs the reconciliation, expiry, snapshot, reservation-expiry and alert jobs. Its own actor, never ADMIN |

## 5. The load-bearing invariants

`L-1` … `L-14` are defined in [`DECISIONS.md`](DECISIONS.md) §4 and are not restated here. Each is
carried by at least one requirement below, and the requirement names the `L-n`. Every `L-n` has **a
database guard and a service guard**; the service guard rejects first, in the transaction, with a
field-level error. A trigger firing in production is an incident, not a validation.

---

## 6. Requirement catalogue

**459 requirements in 27 areas.** Every one closes at least one review finding or derives from a
numbered decision in `DECISIONS.md`. Requirements with no source are not requirements.

> **§6.26 was appended after `DECISIONS.md` §5.1 landed** and renumbers nothing. `FR-443`–`FR-446`
> continue the contiguous range at the end rather than sitting where they belong thematically,
> because §7.4 forbids renumbering a published id. The sections they belong to point at them.

### 6.1 The stock ledger *owner: base*

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-001** | Every stock event is a **movement header with two or more signed lines**, and the lines sum to zero in base UoM per `(company, owner, item, lot, serial, duty_status)`. A single row carrying `from_*` and `to_*` is not a ledger — it makes "on hand at location L" a `CASE` over two nullable columns and makes conservation uncheckable (`L-1`) | base | v1 | P0 | `T-001` `E-026` `P-009` `C-021` `D-4` |
| **FR-002** | A receipt's or an issue's counter-side is a **virtual location**, never an absent row. Without them the ledger has a hole and a leak is undetectable | base | v1 | P0 | `T-009` `S-069` `E-021` `D-4` |
| **FR-003** | `movement_type` is a **catalogue row with behaviour flags** (`direction`, `is_financial`, `affects_on_hand`, `balance_rule`, `allows_mixed_owner`, `requires_reason`, `requires_approval`, `reversal_type_code`, `is_billable_event`, `default_stock_status_code`, allowed from/to statuses), never a Java enum, a `CHECK` or a TypeScript union. An adapter that needs `PDI_CONSUME` or `TRANSFER_DEPART` must not need a core release | base | v1 | P0 | `T-015` `F-087` `G-054` `D-10` |
| **FR-004** | A posted movement line is **never `UPDATE`d and never `DELETE`d**, enforced in three layers: one writer service with no update method, a database trigger rejecting `UPDATE`/`DELETE` (and `INSERT` into a posted movement), and no repository path (`L-2`) | base | v1 | P0 | `T-017` `F-082` `S-054` `P-009` `P-022` `C-038` |
| **FR-005** | Correction is **reversal** — mirrored lines, a mandatory reason code from the catalogue, the original marked reversed, a single-set link. Reversing a reversal is refused; redoing is a new forward movement. "Edit" is never offered anywhere in the product (`L-3`) | base | v1 | P0 | `T-017` `F-082` `S-054` |
| **FR-006** | Every movement carries a **gapless `sequence_no` per warehouse** and a `prev_payload_hash`, giving a tamper-evident chain. A sequence cannot be started retroactively over rows that already exist | base | v1 | P0 | `F-082` `C-038` |
| **FR-007** | **Three timestamps, never one**: `occurred_at` (producer-supplied business time), `recorded_at` (server clock), `effective_date` (the accounting/billing date). Collapsing them kills offline replay, degraded-mode catch-up, cut-off, storage-anniversary billing and EPCIS simultaneously (`L-13`) | base | v1 | P0 | `T-018` `F-083` `S-007` |
| **FR-008** | An `occurred_at` in the future is refused outright, because a future business time breaks every ageing calculation silently | base | v1 | P0 | `F-083` |
| **FR-009** | Quantity is stored in **base UoM with the conversion factor frozen on the line**, alongside the entered quantity and entered UoM. A ledger that re-derives from today's factor silently restates last year (`L-7`) | base | v1 | P0 | `T-011` `F-093` `S-012` `E-009` |
| **FR-010** | **Zero-quantity, non-zero-value movements are legal.** There is no `CHECK (quantity <> 0)`. Freight, duty, clearing and write-downs arrive after the goods and must land on the received lot | base | v1 | P0 | `F-088` `T-063` `G-023` |
| **FR-011** | A position is keyed by `(company, owner, item, location, lot, serial, lpn, stock_status, duty_status)` — **every column present in v1 even where its feature ships later** — with a nil-UUID sentinel discipline chosen once so the unique index fires on nulls (`L-5`) | base | v1 | P0 | `T-003` `F-001` `S-044` `P-008` |
| **FR-012** | **Positions are a cache.** A full rebuild from the ledger reproduces every position row exactly; a nightly job proves it, writes findings to a reconciliation-exception table and alerts on drift (`L-4`) | base | v1 | P0 | `T-019` `F-091` `C-021` |
| **FR-013** | `GET /stock/as-at?at=…` answers a past balance **from the ledger**, so the reconstructibility claim is exercised in production and not only in tests | base | v1 | P0 | `T-019` `E-053` `S-083` |
| **FR-014** | **Negative available is refused; negative on-hand is a policy.** `available = on_hand − Σ open reservations` may never go below zero. Physical on-hand may go negative only where an explicit policy row (scoped by warehouse, owner or item group, resolved most-specific-first) allows `WARN` or `ALLOW`; the default is `BLOCK` (`L-6`) | base | v1 | P0 | `T-025` `F-090` `E-045` `S-076` `C-024` |
| **FR-015** | Every `WARN`/`ALLOW` breach writes an **insufficient-stock log row** (item, warehouse, requested, available, source, user, time) and appears on a report. The accessories precedent for this is good and is copied as an idea, not as code | app | v1 | P2 | `E-045` `C-045` |
| **FR-016** | Concurrency on the position row is defended by **all three** of an optimistic `@Version`, a database `CHECK`, and a stated lock-ordering discipline. A generated `available` column does not protect against two concurrent allocations, because on-hand did not change | base | v1 | P0 | `C-024` `S-085` `P-024` |
| **FR-017** | Ingestion is **idempotent**: `(source_system, idempotency_key)` is unique, `payload_hash` distinguishes a retry from a reused key, and the key is **never server-generated** (`L-9`) | base | v1 | P0 | `T-091` `F-081` `E-003` |
| **FR-018** | Every movement resolves to a **source-document quad** — `source_system`, `source_document_type`, `source_document_id`, `source_document_line_no` — on the header, plus `source_line_ref` on the line, all indexed. A free-text reference cannot be joined (`L-12`) | base | v1 | P0 | `F-084` `E-004` `G-003` |
| **FR-019** | `reason_code_id` is an FK to a **closed, tax-mapped catalogue** on the header and available on the line. Free text cannot be grouped, trended, approved-against, mapped to a GL account or reclassified into the six statutory categories a year later | base | v1 | P0 | `T-010` `S-028` `E-033` `P-027` `G-058` |
| **FR-020** | A movement whose `effective_date` falls in a **`CLOSED` stock period is refused, including a reversal**; `SOFT_CLOSED` requires an override permission and records the override with the overriding user (`L-8`) | base | v1 | P0 | `T-064` `F-085` `E-046` `S-090` |
| **FR-021** | Every movement carries `period_id`. Rows posted before periods existed belong to no period, so the first close has an un-closeable opening set | base | v1 | P0 | `S-090` `S-051` |
| **FR-022** | The ledger is declared `PARTITION BY RANGE (occurred_at)` with monthly partitions and an automatic partition-creation job **from migration one**, with the index strategy stated at the same time. Converting a large heap table later requires downtime this deployment model does not have | base | v1 | P0 | `T-095` `S-096` |
| **FR-023** | Archiving is a **transaction**: for each surviving position tuple it writes an `OPENING_BALANCE` movement dated at the cut-off, then moves the archived rows. The rebuild invariant then holds against the hot table alone. Designed in v1, run in v3 | base | v3 | P6 | `T-020a` `S-096` `S-051` |
| **FR-024** | Every movement records `actor_type` ∈ {`USER`,`DEVICE`,`INTEGRATION`,`SCHEDULED_JOB`,`IMPORT`,`SYSTEM_CORRECTION`}, `actor_user_id` and `device_id`. "Who moved this" is the first audit question and it is not always a user; diagnosing a mis-scanning device retroactively is impossible without the id | base | v1 | P0 | `F-072` `G-072` |
| **FR-025** | Every movement carries `company_id`. A GST return computed from guessed entities is a filing error, and the axis cannot be added after the ledger has rows | base | v1 | P0 | `F-025` `S-022` `G-076` |
| **FR-026** | Producer-specific data goes in a **typed, registered-key attribute side table**, never JSONB. An unregistered key is a column nobody can filter, export or index | base | v1 | P0 | `T-013` `F-087` `P-007` `G-063` |
| **FR-027** | Movement types flagged `requires_approval` (scrap, write-down, negative adjustment) carry `approval_status`, `approved_by` and `approved_at`, and post only when approved | base | v1 | P0 | `T-015` `F-087` `E-034` |
| **FR-028** | A **physical move the system rejected** is a first-class object: a discrepancy / blocked-move queue records the attempted movement, the rejection reason, the operator and the physical reality, holds the goods in a `PENDING_RESOLUTION` disposition, and routes to a supervisor who can force it with a reason and an approval. Refusing the transaction does not un-move the goods | app | v1 | P2 | `S-089` |
| **FR-029** | The ledger **never returns quietly**. Every refusal is an exception carrying a stable machine-readable code; every success returns a movement id the caller stores | base | v1 | P0 | `C-025` `F-081` |
| **FR-030** | Precision is fixed once, in the data model, and cited rather than restated: quantities `DECIMAL(18,4)`, money `DECIMAL(19,4)`, per-unit cost `DECIMAL(19,6)`, percentages `DECIMAL(9,6)`. **⛔ OD-7** | base | v1 | P0 | `E-010` `C-013` `OD-7` |
| **FR-031** | Every quantity, cost and valuation figure is computed on the **backend in `BigDecimal`**; the frontend renders formatted strings. There is no per-module npm manifest and no decimal library, so frontend arithmetic is IEEE-754 double | base·app | v1 | P0 | `C-013` |

### 6.2 The movement port *owner: base*

The port is a **stock journal**: a header with lineage and time, balanced signed lines, immutable once
posted, corrected only by reversal. R4 §3 and R7 §6 are the authorities for the field list; where they
differ from a placement below, the divergence is stated in the row.

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-032** | One inbound endpoint, `POST /api/warehouse/movements`, accepting `{source_system, source_document_*, idempotency_key, movement_type_code, occurred_at, effective_date, actor, lines[]}`. Five callers must post through it without base depending on any of them: `warehouse`, an adapter, a future logistics module, a POS/channel, and `warehouse-3pl` | base | v1 | P0 | `T-033` `F-081` `E-003` |
| **FR-033** | Idempotency conflict semantics are exact and documented: unseen key → `201` with the assigned `sequence_no`; seen key with an identical `payload_hash` → `200` and the **original** movement id, not an error; seen key with a different hash → `409 IDEMPOTENCY_KEY_REUSED` and nothing posted; absent key → `422 IDEMPOTENCY_KEY_REQUIRED` | base | v1 | P0 | `F-081` `T-091` |
| **FR-034** | `POST /movements/batch` accepts N movements, **each with its own idempotency key, each in its own transaction**, and returns a per-movement result array with per-movement error codes. Never all-or-nothing: a scan gun syncing 400 movements after a shift must not lose 399 because one bin was renamed. *R4 places this at v1.1 and R7 at v1; this document follows R7, because the port's shape is a P0 concern and the endpoint is what makes the offline decision of `FR-047` honest* | base | v1 | P0 | `F-092` `G-072` |
| **FR-035** | `POST /movements/{id}/reverse` takes its own idempotency key and a mandatory reason code, produces the mirror, sets `reversal_of_movement_id`, and refuses to reverse a reversal | base | v1 | P0 | `F-082` `T-038` |
| **FR-036** | `GET /movements?source_system=&source_document_type=&source_document_id=` is a single indexed lineage query. It is how a logistics module finds its own postings without `warehouse-base` knowing what a trip is | base | v1 | P0 | `F-084` `G-003` |
| **FR-037** | `POST /movements/simulate` runs the whole validation chain and returns the resulting balance deltas and the error list **without writing**. It is what a channel adapter calls before promising stock, what an operator screen calls to explain a rejection, and what support calls when a client says "it says insufficient stock and there are 40 on the shelf" | base | v1 | P0 | `G-073` |
| **FR-038** | A line identifies its item by **`id`, or `sku`, or `barcode`, or `(source_module, external_id)`**. A dealer's own part number, a job card's material code and an OEM's number are none of the first three | base | v1 | P1 | `T-033` `G-040` |
| **FR-039** | The port's **error-code vocabulary is stable and documented from v1** — `UNKNOWN_ITEM`, `LOT_REQUIRED`, `SERIAL_ALREADY_ISSUED`, `INSUFFICIENT_STOCK`, `NEGATIVE_STOCK_NOT_ALLOWED`, `MOVEMENT_UNBALANCED`, `MIXED_OWNER_NOT_ALLOWED`, `STATUS_TRANSITION_NOT_ALLOWED`, `LOCATION_POLICY_VIOLATED`, `SHELF_LIFE_RULE_VIOLATED`, `EXPIRED_LOT_NOT_ISSUABLE`, `UOM_NOT_CONVERTIBLE`, `PERIOD_CLOSED`, `OWNER_NOT_PERMITTED`, `LPN_CLOSED`, `APPROVAL_REQUIRED`, `IDEMPOTENCY_KEY_*`, `ALREADY_REVERSED`, `CANNOT_REVERSE_A_REVERSAL`, `OCCURRED_AT_IN_FUTURE`, `TEMPERATURE_ZONE_MISMATCH`. Renaming one is a breaking change to five callers | base | v1 | P0 | `F-081` |
| **FR-040** | A single movement posts **wholly or not at all**. There is no partial success within one movement; a producer wanting per-line independence sends one movement per line and uses the batch endpoint | base | v1 | P0 | `F-081` |
| **FR-041** | The port carries **no** carrier, AWB, trip, vehicle, **sales price**, customer, tax, billing charge code, channel-specific field, free-text reference or JSONB payload. A **unit cost** does ride the line, because warehouse owns cost (`D-6`); a *price* is a commercial fact about a sale and belongs to the document that sells. Each has a stated home instead: the lineage quad, the accounting envelope, the billable-event meter, the attribute side table | base | v1 | P0 | `G-035` `T-013` `D-6` |
| **FR-042** | `owner_id` is **on the line, not on the header**, and each movement type declares a `balance_rule` ∈ {`MUST_BALANCE_PER_OWNER_ITEM`, `MUST_BALANCE_PER_ITEM`, `UNBALANCED_ALLOWED`} plus `allows_mixed_owner` (default false). A 3PL's own carton consumed against a client's order is one atomic event with two owners | base | v1 | P0 | `F-059` `F-009` |
| **FR-043** | `@PreAuthorize` on every port method (`warehouse:movements:post`, `:reverse`, `:view`, `:simulate`), and the posting permission is additionally checked against the caller's owner grants | base | v1 | P0 | `F-004` |
| **FR-044** | The request is **persisted before it is processed**: an inbound-message row with the payload reference, a status ladder (`RECEIVED`/`PROCESSED`/`FAILED`/`REJECTED`), the resulting movement id, the error detail and a retry count. Persist first, process second, return the stored result on replay | base | v1 | P0 | `T-091` `T-092` |
| **FR-045** | An **interface error queue** grid over failed inbound messages and failed posting events, with a reprocess action (idempotent by construction) and an alert when the queue is non-empty beyond a threshold | base | v1 | P2 | `T-092` |
| **FR-046** | Value-only movement types are seeded in v1: `COST_ADJUSTMENT`, `REVALUATION`, `LANDED_COST_APPLY`, `WRITE_DOWN` | base | v1 | P0 | `F-088` `T-063` |
| **FR-047** | **v1 is online-only and says so.** The offline hooks land anyway and cost nothing: a client-generated transaction id, a device-supplied `occurred_at`, and duplicate rejection on the client id. Adding them later means re-versioning every RF endpoint | base·mobile | v1 | P0 | `T-053` `S-086` |

### 6.3 Items, units of measure, identification and packaging *owner: base*

> **See also `FR-443`–`FR-445` in §6.26** — the style-and-variant model, its axis ordering and
> assortment packs. They belong in this section and are numbered at the end of the range because
> `DECISIONS.md` `A-3` landed after it was written.

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-048** | There is **one item master**, `whb_items`, and no module other than `accessories` (`D-9`) may own a second. Every consumer reads it or links to it | base | v1 | P1 | `E-007` `C-032` `D-9` |
| **FR-049** | `item_type` is a **registry row**, not an enum, and admits at least `STOCK`, `NON_STOCK`, `SERVICE`, `KIT_STOCKED`, `KIT_PHANTOM`, `CORE`, `CONSUMABLE`, `PACKAGING`, `RETURNABLE_EQUIPMENT`, `TYRE`, `FUEL`, `ASSET`. *R3 `E-007` proposes an enum; R7 `G-060` diverges and this document follows R7, because the four fleet types are exactly what stops a logistics module building private ledgers* | base | v1 | P1 | `G-060` `E-007` `G-002` `G-003` `G-004` `G-005` |
| **FR-050** | Item status is **four independent facts** — receivable, issuable, orderable, countable — plus a `lifecycle_status` (`NEW`/`ACTIVE`/`PHASE_OUT`/`OBSOLETE`/`BLOCKED`) for reporting. One enum forces a combinatorial explosion or a wrong answer; `is_active` alone cannot express "no longer orderable but still stocked", which is where a superseded part lives for two years | base | v1 | P1 | `T-020` `E-008` |
| **FR-051** | Deactivating an item with non-zero on-hand across any site, status or owner is **blocked**; the offered alternative is blocking it for receipt or issue | base | v1 | P1 | `T-029` |
| **FR-052** | There is **no cost column on the item master.** Cost is a property of a receipt layer. The only legitimate item-level cost is a standard cost, and that is a separate effective-dated table with different semantics | base | v1 | P1 | `T-026` |
| **FR-053** | Reorder point, safety stock, min, max, reorder quantity and lead time live on **item × site** in v1 and on **item × location** in v1.1. Item-level values are defaults that seed the row, never the operative numbers | base | v1·v1.1 | P1·P3 | `T-027` `E-013` |
| **FR-054** | The base stocking UoM is **immutable once a ledger row exists**, enforced by a database trigger and not trusted to the service layer | base | v1 | P1 | `T-011` |
| **FR-055** | UoM conversion belongs **on the item**, not on the UoM master. A case of oil filters is 12; a case of wiper blades is 6. A global factor is correct only for physical dimension conversion. A null-item row is the global conversion; a non-null row overrides it | base | v1 | P1 | `T-011` `E-009` |
| **FR-056** | Every UoM carries `unece_rec20_code` and `gst_uqc_code`. Two columns, without which every compliance payload and every EDI mapping is hand-mapped and the IRP rejects invoices | base | v1 | P1 | `S-011` `G-059` `E-047` |
| **FR-057** | A barcode resolves to a **packaging level**, not to an item. The barcode registry carries the normalised GTIN-14, a packaging reference, a barcode type (purpose) distinct from a barcode format (symbology), and a status that retires a code without deleting scan history. **Quantity is derived from the packaging row and is never stored on the barcode.** *R2 `T-022` puts a UoM on the barcode; the prior art (`P-034`) is more correct — a UoM on the barcode is the same dual truth in a different column — and this document follows `P-034`* | base | v1 | P1 | `S-001` `S-003` `P-034` `T-022` |
| **FR-058** | Packaging is **supplier-specific**, with a deterministic resolution order: supplier-specific → supplier-agnostic default → loose/each, `priority` breaking ties inside a tier. The same part bought from two vendors ships in different pack quantities on day one | base | v1 | P1 | `P-035` |
| **FR-059** | One **alias table** carries owner SKU, GTIN-13/14, UPC/EAN, marketplace codes, OEM part number, supplier code, customer part number and legacy code, with `pack_qty` on the alias. It is deliberately **not globally unique** — two owners legitimately carry the same EAN | base | v1 | P1 | `F-006` `E-012` |
| **FR-060** | Item uniqueness is `(owner_id, sku)`, plus a globally unique internal `item_code` that every FK points at and that appears on a bin label. A global unique SKU is a one-way door the first 3PL client walks through | base | v1 | P1 | `F-005` |
| **FR-061** | `whb_item_external_refs (item_id, source_module, external_id, external_label)` with `uk(source_module, external_id)` is a **v1 table**. Without it, either every adapter stores a warehouse UUID in its own tables, or the port grows a per-vertical identification mode | base | v1 | P1 | `G-040` `E-083` `D-9` |
| **FR-062** | One **scan-resolution service** resolves any scanned string against barcodes, location codes, lot codes, serial numbers and document numbers and returns a typed object. Every scan surface calls it; nothing parses barcodes inline; **no scanner SDK ever enters the codebase** (the engine consumes a plain string, so any keyboard-wedge device works); every scan is logged, resolved or not | base | v1 | P1 | `S-002` `E-071` `P-036` |
| **FR-063** | GS1 element-string parsing (AI `01`/`10`/`17`/`21`/`00`/`310n`, fixed vs variable length, FNC1 separator) returns a composite `{gtin, lot, expiry, serial, sscc, quantity}` in one scan. The resolver's return shape admits a composite result from v1 so this is not a rewrite | base | v1.1 | P3 | `S-002` `T-032` `F-070` |
| **FR-064** | `sscc` on the LPN and `gln` on the warehouse, the location and the party are **v1 columns**. They are printed on physical labels and exchanged with trading partners; issuing them later means re-labelling | base | v1 | P1 | `S-004` `S-006` `F-070` |
| **FR-065** | Catch weight is a **second, independent quantity**: `secondary_quantity` + `secondary_uom_id` on the movement line and the position, and `is_catch_weight` on the item. v1 writes null. The weights were never captured, so there is nothing to backfill from | base | v1·v2 | P1·P5 | `T-012` `S-013` `E-011` |
| **FR-066** | `tax_classification_code` (HSN/SAC in India) lives on the item as a **string, never an FK into a tax master**, and is **snapshotted** onto every document and movement line. Reading the item master later gives the new code for old documents and the filed return no longer reconciles | base | v1 | P1 | `E-047` `S-031` `G-035` |
| **FR-067** | The hazmat classification block — UN number, class 1–9, packing group, proper shipping name, subsidiary classes — is on the item in v1. The prior art's block is correct and is kept verbatim; what is missing is everything that uses it | base | v1 | P1 | `S-042` |
| **FR-068** | A temperature/storage class is on the item and a temperature zone on the location, in v1. A putaway into the wrong zone is rejected by the port with `TEMPERATURE_ZONE_MISMATCH` | base | v1·v2 | P1·P5 | `S-041` `F-069` |
| **FR-069** | `shelf_life_days`, `min_shelf_life_receipt_pct` and `min_shelf_life_ship_pct` are v1 item columns even though FEFO and the shelf-life rules ship later, so the data exists before the rules that consume it | base | v1 | P1 | `T-028` `T-030` `F-067` |
| **FR-070** | ABC class, velocity/movement class and count-frequency class are v1 columns on item × site; the recomputation job and its consumers ship in v3. A classification stored and never consumed is a defect the prior product shipped | base | v1·v3 | P1·P6 | `T-027` `E-066` `P-051` `P-058` |
| **FR-071** | **Supersession chains** with `chain_sequence`, a quantity ratio, a type (`REPLACES`/`INTERCHANGE`/`PARTIAL`), an effective date, cycle detection and a resolver that walks to the terminal item. **Every** lookup path — counter enquiry, workshop request, reorder, receipt matching, barcode scan — goes through the resolver. No tier-1 WMS has this; it is why a dealer chooses us | base | v1 | P1 | `T-021` `E-055` `P-031` |
| **FR-072** | A supersession records its **stock and demand treatment** — `KEEP_SEPARATE`, `MERGE_DEMAND` (weighted by the quantity ratio) or `MERGE_STOCK` (a movement at the old part's cost layers) — so the decision is reproducible. Without it, the successor's computed stocking level is zero the day it supersedes. *`E-056` places this at v1.1; `DECISIONS.md` §5 makes v1.1 = P3 execution, and the parts differentiators are in the v1 exit criterion, so it lands v1/P2* | app | v1 | P2 | `E-056` `D-12` |
| **FR-073** | Interchange and alternate parts are bidirectional supersession rows; the counter enquiry shows "not in stock — 2 available as `<interchange>`" with availability across every branch | app | v1 | P2 | `E-057` `T-021` |
| **FR-074** | **Vehicle fitment lives in `warehouse-adapter-dealer`**, referencing the automotive model master, and never in `warehouse-base`. If base learns about vehicles it cannot serve assets, field-service or logistics | adapter | v1 | P2 | `T-023` `E-058` |
| **FR-075** | Kits are a master with components, and **virtual and physical kits are different objects with the same BOM**: a virtual kit never holds stock and its availability is `MIN(component available ÷ required)`; a physical kit holds stock and a work order converts components into it. A design supporting only one is rebuilt when the second client arrives | base | v1.1 | P3 | `F-057` `T-031` `E-044` |
| **FR-076** | Variable item attributes are a **typed attribute-definition / attribute-value pair**, never JSONB, and only registered keys are accepted | base | v1 | P1 | `T-013` `P-007` `G-063` |
| **FR-077** | Item images and documents link to the platform `documents` table through a warehouse-owned link table with **`ON DELETE NO ACTION`**. A cascading link means a GRN photo or a damage certificate vanishes when the file is deleted, with no referential trace | base | v1 | P1 | `C-018` `P-017` |
| **FR-078** | There are **no user-defined JSONB custom fields**. The answer is a typed column on request, or the attribute tables of `FR-076`. Stated so it is not built by accident, because this is where every tier-1 offers a bag | base | v1 | P1 | `T-094` `T-013` |

### 6.4 Identity and the facility model *owner: base*

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-079** | A warehouse **belongs to exactly one branch** (`branch_id NOT NULL`) and the GSTIN is read from the branch, never duplicated onto the warehouse. A warehouse under two tax registrations is not a thing, so the accessories many-to-many bridge is not copied. `branches.branch_type` already admits `WAREHOUSE` and `DISTRIBUTION_CENTER` at no cost | base | v1 | P1 | `E-048` `S-022` `C-016` `C-030` |
| **FR-080** | A warehouse carries a **structured address** — line 1/2, city, `state_code`, pincode, country, latitude, longitude — plus `gln`, `legal_entity_id` and `tax_registration_id`. Without them a historical transfer cannot be classified as supply or non-supply for a period already filed | base | v1 | P1 | `S-016` `S-022` `E-048` |
| **FR-081** | `is_physical` on the warehouse permits a **warehouse row that maps to no building** — a carrier, a trip, a transit pool. This is the single most important seam column for the logistics module | base | v1 | P1 | `F-089` |
| **FR-082** | Locations are a **self-referencing hierarchy** (site → building → zone → aisle → rack → level → position) with a `location_level` and a materialised `path` for subtree queries. Four independent VARCHARs cannot answer "count zone A", "block aisle 12", "utilisation of rack B-04" — there is no row representing the zone | base | v1 | P1 | `T-008` `E-020` `C-029` |
| **FR-083** | `location_type` is a **registry with behaviour flags** (`is_physical`, `is_stock_holding`, `is_virtual_counterparty`, `is_mobile`, `is_transit`, `allows_mixed_owner`, `requires_assigned_user`, `is_pickable`, `is_receivable`, `counts_as_on_hand`, `is_staging`, `is_dock`) and admits `IN_TRANSIT`, `MOBILE`, `VEHICLE`, `TRAILER`. **The prior product broke exactly this**: `location_type` and `zone_type` CHECKs were dropped and recreated with different value sets 36 versions after creation | base | v1 | P1 | `F-089` `G-055` `E-021` `D-10` |
| **FR-084** | Virtual locations are seeded per install and per site — `SUPPLIER`, `CUSTOMER`, `ADJUSTMENT`, `SCRAP`, `PRODUCTION`, `IN_TRANSIT`, `COUNT_VARIANCE`, `OPENING_BALANCE`, `CONSUMED`, `JOB_WORKER` — with `counts_as_on_hand = false`, so they never appear in a stock report and always balance the ledger. Every movement has a real from- and to-location, one of which may be virtual | base | v1 | P1 | `T-009` `S-069` `E-021` |
| **FR-085** | The transit location is **per reference** (per transfer, per trip), not one global `IN_TRANSIT` bucket, so two consignments on the road are separately countable and separately ageable | base | v1 | P1 | `G-074` |
| **FR-086** | Capacity and constraint columns land on the location in v1 — weight, volume, height, LPN count, unit count, mixed-item, mixed-lot, mixed-owner, temperature zone, pick sequence, barcode and check digit — and are **enforced at putaway** in v1.1 with a hard-block-vs-warn setting | base·app | v1·v1.1 | P1·P3 | `T-074` `E-022` `F-003` `F-069` |
| **FR-087** | `commingle_policy` ∈ {`FREE`,`SINGLE_OWNER`,`SINGLE_ITEM`,`SINGLE_LOT`,`SINGLE_LPN`} and `dedicated_owner_id` on the location; the port rejects a movement whose resulting balance would violate the policy, naming the policy and the conflicting owner, item or lot. Hard-coding "commingling allowed" makes a bonded or pharma client unsellable; hard-coding the opposite makes bulk storage uneconomic | base | v1 | P1 | `F-003` |
| **FR-088** | `assigned_user_id` on the location, with `MOBILE` and `VEHICLE` types, makes **van stock the same object as a delivery vehicle's load**. Without it van stock becomes a separate table and a separate reconciliation problem, and last-mile is unbuildable on the ledger | base | v1 | P1 | `T-080` `S-060` |
| **FR-089** | A **location generator** takes zone, aisle range, rack range, level range, position range, a format mask, a location type and default capacities, previews the count and the first and last codes, then commits. A modest warehouse has 3,000–20,000 locations; without a generator, implementation is a spreadsheet exercise and the barcodes disagree with the labels already on the racking. CSV import is the fallback | app | v1 | P1 | `T-024` |
| **FR-090** | `whb_location_external_refs (location_id, source_module, external_id)` carries the **dual identity** of a vehicle: a location in the ledger and an asset in logistics, joined by an xref, never by a foreign key. Without it either base gets an FK into logistics, or logistics duplicates the location tree | base | v1 | P1 | `G-017` `G-021` |
| **FR-091** | A location has a **status** (available / blocked / counting / damaged / frozen) and is blockable with a reason, so maintenance and counting do not require moving stock | base | v1 | P1 | `T-075` |
| **FR-092** | Dock doors and staging lanes are locations; the dock and dock-appointment **schema lands in v1** with `arrived_at`, `docked_at`, `departed_at`, `no_show` and `detention_minutes`, and the screens land in v1.1. *R4 `F-080` places this at v2; R7 `G-014` argues the schema is v1 because dock-to-stock starts from `arrived_at` and detention is metered from it — this document follows R7* | app | v1·v1.1 | P1·P3 | `F-080` `G-014` `G-015` |
| **FR-093** | Occupancy is **derived at read time** from active assignments and is not a maintained counter; exclusivity is a partial unique index, not application logic; released assignments are retained forever. This is the repo's own best precedent and it is copied verbatim | base | v1 | P1 | `C-033` |

### 6.5 Lots, serials, LPNs, stock status and duty status *owner: base*

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-094** | A lot is an **entity**, keyed `uk(owner, item, lot_code)`, with codes normalised on write. On a `VARCHAR` you cannot hold a lot across every location at once, cannot compute FEFO without parsing, cannot attach a certificate, cannot detect that one physical lot was keyed two ways, and cannot answer a recall in minutes | base | v1 | P1 | `T-005` `E-014` `F-063` |
| **FR-095** | Lot attributes are v1 columns: manufacture date, expiry, **best-before and use-by as separate columns with different despatch rules**, retest date, supplier lot, country of origin, HS code, MRP, net content, pack month/year, received date and `parent_lot_id`. Every one is printed on a pack already put away; nobody re-opens cartons to backfill, and a split or merge not recorded when it happened is invisible forever | base | v1 | P1 | `S-033` `S-038` `F-063` `E-014` `E-016` |
| **FR-096** | A lot has **its own status**, independent of item and location, so a whole lot can be held everywhere at once without moving anything | base | v1 | P2 | `T-005` `F-068` |
| **FR-097** | A serial is an **entity** with a current location, status, owner, LPN and lot, keyed `uk(owner, item, serial_number)` — **never globally unique**, because a second manufacturer's identical serial is legitimate and a global key rejects it forever, and the rejected rows were never recorded at all | base | v1 | P1 | `T-006` `E-019` `F-063` `S-018` |
| **FR-098** | Serial control is a **mode** (`NONE`/`RECEIPT`/`SHIP`/`FULL`), lot control is a mode (`NONE`/`OPTIONAL`/`REQUIRED`), and expiry is a policy (`NONE`/`OPTIONAL`/`REQUIRED`). A boolean cannot express the four control modes every tier-1 supports, and "captured at ship only" is the common case for automotive spares | base | v1 | P1 | `T-006` `F-063` |
| **FR-099** | A serial answers the three post-sale questions: **where is it now, who did we sell it to, is it in warranty** — sold-to party, warranty start and end, current custody, and the shipment that carried it | base | v1 | P2 | `E-019` `S-057` |
| **FR-100** | The **LPN is a ledger object** — code, SSCC, type, `parent_lpn_id`, current location, status, mixed-item/lot/owner flags, gross weight, dimensions and **`received_at`, the storage-anniversary anchor**. `lpn_id` and `from_lpn_id`/`to_lpn_id` are nullable v1 columns. Per-pallet and anniversary storage billing are defined over pallets and cannot be computed for a past a ledger never recorded | base | v1·v1.1 | P1·P3 | `T-007` `F-064` `S-004` |
| **FR-101** | An LPN move is **one movement** whose lines the service expands from the LPN's current contents and **stores**, never leaves implicit, so the ledger remains self-explaining. Nested-LPN operations are v2; `parent_lpn_id` is a v1 column | base | v1.1·v2 | P3·P5 | `F-064` `T-007` |
| **FR-102** | Stock status is a **registry with behaviour flags** (`is_on_hand`, `is_available_to_promise`, `is_allocatable`, `is_pickable`, `is_shippable`, `is_countable`, `is_valued`, `is_owned_asset`, `blocks_shipment`, `requires_reason_to_enter`/`_to_leave`, `badge_variant`), `stock_status_code` is `NOT NULL` on every line, and the status **participates in the position unique key**. Quarantined stock is on hand, owned, valued and not allocatable — four independent facts a bin cannot express | base | v1 | P0 | `T-004` `F-068` `G-056` |
| **FR-103** | A status change is a **balanced two-line movement at the same location** with a mandatory reason code, so quarantine never requires a physical move and a recall can hold in place | base | v1 | P0 | `T-004` `F-066` |
| **FR-104** | `duty_status` ∈ {`DOMESTIC`,`BONDED`,`MOOWR`,`SEZ`,`FTWZ`,`EXPORT_UNDER_BOND`} is **in the position key and on every movement line from v1**. Bonded and duty-paid stock of one SKU must never merge into one balance; once commingled no algorithm separates them, and clearing the wrong one is a customs offence, not a data-quality issue (`D-5`) | base | v1·v2 | P0·P4 | `S-044` `D-5` |
| **FR-105** | Genealogy is recorded **at the moment of transformation** — a kit, repack, decant, split or merge writes its inputs and outputs — and is answerable **forward** (where did this lot go) and **backward** (what went into this unit) for the full retention period. A recall that must cross a kit boundary has nothing to walk otherwise (`L-12`) | base | v1·v2 | P1·P5 | `S-008` `F-065` |
| **FR-106** | Duplicate serials, duplicate LPN codes and duplicate lot codes are **detected at receipt** and reported, with a site-level duplicate warning where the scope permits the duplicate | base | v1 | P1 | `T-006` `F-064` |

### 6.6 Owner of goods *owner: base*

`owner_id` ships in v1 in **every** install (`D-5`). Consignment stock, customer-owned goods under
repair, job-work material at a job worker, bailed 3PL stock and our own stock are the same shape and
differ only by owner. There is no rule that recovers whose a unit was, so the column is free now and
unbackfillable later. Four lenses reached this independently.

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-107** | `owner_id` is `NOT NULL` on every movement line, position, reservation, lot, serial, LPN, alias, cost layer, task and pick task, **and participates in the position unique key**. Adding it later is a rebuild of the two largest tables plus every allocation, valuation, index, grid filter, export and statistics map (`L-5`) | base | v1 | P0 | `F-001` `T-002` `E-024` `P-025` `S-064` `D-5` |
| **FR-108** | `whb_owners` and a `whb_owner_types` **registry** (`HOUSE`, `CLIENT_3PL`, `CONSIGNOR`/`SUPPLIER_CONSIGNED`, `CUSTOMER_OWNED`, `JOB_WORK`, `TRANSIT`) with `is_house`, `posts_to_our_gl` and `default_cost_basis`. Exactly one house owner is seeded by the first migration | base | v1 | P0 | `F-002` `T-002` `G-053` |
| **FR-109** | `warehouse` v1 posts against the seeded house owner on every movement, so the code path is exercised from day one. **There is no single-owner mode** | app | v1 | P0 | `F-001` |
| **FR-110** | A single movement may carry lines of **two different owners** where the movement type permits it, and it balances per `(owner, item)` rather than per movement. Otherwise the 3PL's own carton consumed against a client's order is a second call that can fail independently, and the consumable silently vanishes | base | v1 | P0 | `F-059` |
| **FR-111** | `OWNER_CHANGE` is a seeded movement type: goods change owner **without moving**, posted as a negative line on the outgoing owner and a positive on the incoming, same item, lot, serial, LPN, location and status. An `UPDATE` to the position's owner would mean the ledger no longer explains the balance and the storage biller bills the wrong client for the whole month (`L-11`) | base | v1·v2 | P0·P5 | `F-009` `T-077` |
| **FR-112** | **Non-own stock is never valued** (`L-14`). `is_financial` on the movement type says whether the type can produce an accounting envelope at all; `cost_basis` ∈ {`ACTUAL`,`STANDARD`,`AVERAGE`,`INFORMATIONAL`,`ZERO_BAILMENT`} on the line says whether this one does. `INFORMATIONAL` exists separately from `ZERO_BAILMENT` because a client's declared value is needed for insurance and a loss claim even though it must never post | base | v1 | P0 | `F-010` `S-078` `D-6` |
| **FR-113** | Consignment in, consignment out, VMI, customer-owned repair stock, goods on approval and job-work material are **one model in three configurations**, built once, distinguished by owner type. Stated explicitly so it is not built three times | base | v1·v2 | P0·P5 | `T-077` `E-032` `S-032` |
| **FR-114** | Owner-scoped access is resolved **server-side by one resolver** and passed to every query service, export service, statistics map and dropdown endpoint. A request naming an owner the caller has no grant for is rejected `403`, **never returned empty**, because an empty grid is indistinguishable from "no stock". A contract test fails the build if a repository method touching an owner-scoped table has no owner-set parameter | base | v1·v2 | P0·P5 | `F-004` `T-073` |
| **FR-115** | For non-own stock the product reports a **custody liability and an insured value** — a different number, on a different report, never mixed into the inventory asset | 3pl | v2 | P5 | `S-078` `F-010` |

### 6.7 Counterparties *owner: base*

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-116** | `warehouse-base` owns a **thin counterparty identity** — code, name, legal name, national tax id, active flag — because nothing else in the repo does: `asset_vendors` is assets-owned, automotive `customers`/`companies` model buyers and OEMs, and accessories receiving has no supplier field at all. **⛔ OD-4** on the long-term home | base | v1 | P1 | `C-035` `G-027` `T-040` `OD-4` |
| **FR-117** | A counterparty's **roles are a many-to-many link table** (`SUPPLIER`, `CUSTOMER`, `CARRIER`, `CLIENT_3PL`, `TRANSPORTER`, `JOB_WORKER`, `INTERNAL`) with validity dates, not a `partner_type` enum. *R2 `T-040` proposes the enum; R7 `G-057` diverges and this document follows R7 — a carrier is a counterparty with a role, and a party is routinely two roles at once* | base | v1 | P1 | `G-057` `T-040` |
| **FR-118** | `whb_counterparty_external_refs (counterparty_id, source_module, external_id)` with `uk(source_module, external_id)` and **`source_module` as an opaque string, never an FK**. An automotive or assets party is *linked*, never copied; in a standalone install the table is empty and everything works | base | v1 | P1 | `C-035` `G-027` `G-031` |
| **FR-119** | The counterparty carries **no payment terms, credit limit, bank details, contacts or scorecard**. Those belong to whichever module owns the commercial relationship, and adding them here is how the seam leaks | base | v1 | P1 | `G-030` |
| **FR-120** | **Every inbound receipt names a counterparty.** Without it a GRN cannot be traced to who shipped, supplier holds cannot exist, lot traceability has no backward end, and return-to-vendor has no party | app | v1 | P1 | `C-031` `T-040` |
| **FR-121** | The trigger for extracting a shared `party-base` is recorded: **the third module that needs the same GSTIN to be authoritative for tax filing**. Until then extraction is speculative; after then it is overdue. The cost of not extracting — up to seven party-shaped masters across the monorepo — is stated here rather than discovered. **⛔ OD-4** | base | v3 | P6 | `G-029` `OD-4` |

### 6.8 Inbound *owner: app*

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-122** | Purchase order and goods receipt are **distinct documents**: the PO carries ordered / received / cancelled quantities per line, the GRN carries received / accepted / rejected / damaged. The quantity event and the value event are different events with different dates | app | v1 | P1 | `E-027` `P-019` |
| **FR-123** | The **layered-truth model** is stated with its worked number and is the product's answer to "which quantity is right": PO = commitment · ASN = shipment declaration · receiving session = the physical inbound shipment · GRN = the single receipt truth · invoice = billed · inventory = on-hand. *Ordered 100 → Shipped 95 → Received 92 → Billed 100 → On-hand 89.* All five are correct simultaneously | app | v1 | P1 | `P-019` |
| **FR-124** | A **receiving session** is one truck against N POs × N ASNs × N GRNs, with a nullable supplier for a multi-supplier consolidator's load and an ASN assignable to exactly one session. The rollup iterates GRNs by session, not by PO. A one-PO-per-receipt model forces the operator to lie | app | v1 | P1 | `P-021` |
| **FR-125** | The **purchase order is the lifecycle command centre**: a detail page with sub-tabs where every GRN, invoice, return, QC result, putaway and exception rolls up. A document owns only the information that legally belongs to it — the session owns physical arrival, the GRN owns the legal receipt, the invoice owns finance, the PO owns the lifecycle | app | v1 | P1 | `P-020` |
| **FR-126** | Receiving behaviour is **per-warehouse configuration**, not two parallel workflows: receiving mode, GRN timing relative to the physical count, QC policy and putaway automation level, with defaults that preserve simple behaviour. One product must serve a dock-managed DC and a two-person store | app | v1 | P1 | `P-057` |
| **FR-127** | **Receiving verification always happens; quality inspection is optional.** They are different acts and the 72-table prior design does not distinguish them | app | v1 | P1 | `P-057` |
| **FR-128** | **Blind receipt is a first-class v1 flow**, requiring only item, quantity, UoM, owner, status and location. Three of our own scenarios have no PO at the moment of receipt — a 3PL client's goods, a customer return, an over-the-counter purchase — and if v1 only receives against a PO, the first pilot keys fake POs and fake POs become permanent | app | v1 | P1 | `T-034` |
| **FR-129** | A receipt can land in a **non-available status** on the first transaction, defaulted item → supplier → `AVAILABLE`. If v1 hardcodes `AVAILABLE`, every quarantine flow is a second transaction that briefly exposes the stock to allocation, and a wave released in that window picks quarantined goods | app | v1 | P1 | `T-035` `S-037` |
| **FR-130** | **Over- and short-receipt** are governed by a tolerance on the item and a warehouse default, with `match_status` (`MATCHED`/`QTY_OVER`/`QTY_UNDER`) and an explicit close-short action carrying a reason. Without it, PO lines accumulate forever and the open-PO report is meaningless within a quarter, which then breaks reorder | app | v1 | P1 | `T-036` `P-026` |
| **FR-131** | **Receipt reversal is an action**, not a data fix: it generates a `REVERSAL` movement linked to the original, decrements the PO line's received quantity, and is blocked once the stock has moved on — at which point it is correctly an adjustment | app | v1 | P1 | `T-038` `P-028` |
| **FR-132** | **Cancellation is a cascade with a stock gate.** A PO is cancellable only before stock is posted; it is refused if any GRN line has received stock **or an ARRIVED ASN exists**; otherwise it cascade-cancels the receiving session and every non-completed GRN. Partial receipt stays open and resolves to fully-received or a manual short-close, with no auto-backorder | app | v1 | P1 | `P-026` `T-036` |
| **FR-133** | **Quality inspection is a header over lines**, one inspection number per GRN, with rollup rules stated to the value: all pass → `PASS`, all fail → `FAIL`, anything mixed or partial → `CONDITIONAL`; started = min of line starts, completed = max when all lines complete. One submit takes per-line results; per-line endpoints remain for incremental capture. A GRN with fourteen lines stops producing fourteen QC documents | app | v1 | P1 | `P-029` `E-029` |
| **FR-134** | Quarantine and **disposition** (release / reject / return to supplier / scrap) is a workflow with a QA-role gate, and regulated item classes are quarantined **by default** on receipt rather than flagged | app | v1 | P2 | `S-037` `E-029` |
| **FR-135** | **Putaway rules are data**, evaluated in sequence, returning a suggested location the operator may override with a reason that is captured. v1 ships the evaluation harness with one rule ("the item's fixed location, else any location with capacity in the default zone"); the rule editor and the strategy set land in v1.1. Building putaway as a dropdown in v1 means rewriting the receiving service | app | v1·v1.1 | P1·P3 | `T-037` `E-023` |
| **FR-136** | The **ASN** is a document with lines carrying shipped quantity, lot, expiry, serial and SSCC, and it drives dock appointments, pre-allocation and cross-dock. It is a receipt expectation, not a transport object, and warehouse owns it | app | v1.1 | P3 | `S-015` `G-032` `P-019` |
| **FR-137** | A **cross-dock reference is a nullable v1 column on the receipt line** even though cross-dock ships in v2, because "which receipts were cross-docked" is a KPI from day one and retrofitting the flag leaves the history blank | app | v1·v2 | P1·P5 | `T-039` |
| **FR-138** | **Inbound reconciliation is a decision centre that never moves stock itself.** A case carries a type (quantity / over-receipt / invoice / ASN / inventory variance / receipt reversal / supplier return), a severity, a status, nullable document links, a root cause and — the load-bearing column — a **resolution-document pointer**. Cases are auto-created at variance points and each of the five resolutions creates a document. *`P-028` places this at v1.1; `DECISIONS.md` §5 makes v1.1 = P3 execution and puts adjustments in the v1 exit criterion, so it lands v1/P2* | app | v1 | P2 | `P-028` `T-038` `D-12` |
| **FR-139** | A **supplier return is not an RMA.** It is its own document with its own state ladder, and **inventory is reduced only at dispatch**. The prior system's bug was a QC-fail auto-RMA stuffing the supplier's name into a customer field | app | v1 | P2 | `P-028` `F-056` |
| **FR-140** | The **three-way match is built on an allocation junction** — invoice line × GRN line × PO line with an allocated quantity and amount — not on a 1:1:1 header assumption. One table delivers partial invoicing, multiple invoices per PO, one invoice spanning GRNs and one GRN line split across invoices. Pairing lines by "closest price" is a named anti-pattern. The value leg belongs to accounting | app | v2 | P5 | `P-039` `E-028` `G-034` |
| **FR-141** | **Free / scheme quantity** is a column on the receipt line in v1 with a scheme reference, and the landed value spreads across billed plus free so the unit cost falls. Bolting it on later corrupts cost layers already written, and any tolerance check must know about it | app | v1·v2 | P1·P5 | `E-080` |
| **FR-142** | Receipt facts — on-time, short, damaged, labelling, ASN accuracy — are **emitted as evidence**; the supplier scorecard itself is a supply-chain concern and is not built inside warehouse | app | v3 | P6 | `G-032` `T-036` |
| **FR-143** | The receiving path enforces the item's **UoM convertibility guard**. The prior system's PO and SO screens had the guard and the GRN modal offered the full UoM master, so a receipt could post the wrong base quantity — a silent data-corruption path no other lens names | app | v1 | P1 | `P-019` |
| **FR-144** | Tracking is decided by the **item's lot and serial control policy**, never by a mode string read in isolation. The prior system read a `tracking_mode` string and ignored the booleans, so an item could be silently received untracked | app | v1 | P1 | `P-019` `T-006` |

### 6.9 Inventory control *owner: app*

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-145** | Every adjustment carries a **mandatory catalogue reason code** and is gated by an approval threshold expressed **by value as well as by quantity**. A one-unit variance on a washer line is noise; a one-unit variance on an engine control unit is an investigation | app | v1 | P2 | `T-010` `E-033` `E-034` `T-090` |
| **FR-146** | A reason code carries `affects_demand_history`, so a write-off or a warranty issue does not inflate the reorder point | base | v1 | P2 | `E-033` `E-066` |
| **FR-147** | An inter-site transfer is **three legs**: depart from the source location into a per-transfer in-transit location **at the sending site**, arrive from in-transit into the destination location, and — where shipped and received differ — an explicit transit-loss adjustment with a reason code. Real transfers take days; during them the stock exists, is owned by somebody and is at risk to somebody | app | v1 | P2 | `T-016` `E-032` `F-089` `G-071` `S-069` |
| **FR-148** | The in-transit **ownership policy is stated**: the sender bears the risk and holds the in-transit stock until receipt. The decision determines which site the in-transit lines carry and changes valuation and branch reporting, so it is taken in v1 | app | v1 | P2 | `T-016` |
| **FR-149** | An **in-transit ageing report** highlights the residue — shipped and not received beyond N days — so the column is exercised and carrier-lost stock is found | app | v1 | P2 | `E-032` `G-075` |
| **FR-150** | Bin-to-bin movement within a site is an ordinary two-line movement with the same status and owner at both ends | app | v1 | P2 | `T-008` `T-015` |
| **FR-151** | **Holds are records with a release audit, not a status.** An order or a lot can be on two holds at once (fraud review *and* out of stock), and `status = ON_HOLD` cannot represent that; releasing one hold would wrongly release the whole thing. Each hold type carries `blocks_allocation` and `blocks_pick` | app | v1 | P2 | `F-033` |
| **FR-152** | Status change and **mass hold / release** by lot, LPN, location, supplier, item or date range, each posting a balanced status-change movement with a reason. Single-object status change is v1; the mass action and the recall workflow are v2 | app | v1·v2 | P2·P5 | `T-004` `F-066` |
| **FR-153** | **A count is a document that proposes an adjustment and never writes on-hand.** The book quantity is frozen at count start and stored on the line; the variance posts as `COUNT_ADJ` movements against a virtual variance location at posting time. If a count writes the balance, the ledger no longer explains it, there is no adjustment to post, the variance is unrecoverable, and a count keyed against a stale snapshot silently reverses movements made during the count | app | v1 | P2 | `T-089` `E-038` `C-023` `S-091` |
| **FR-154** | Counting supports **blind counting** (the counter does not see the book quantity, which is stored anyway), recount thresholds with a recount sequence, multi-counter assignment by zone, and printable sheets that can be keyed back | app | v1 | P2 | `S-091` `P-033` `T-089` |
| **FR-155** | Variance **tolerance gates posting** by quantity percentage and by value; lines inside tolerance post automatically, lines outside move the count to pending approval and may generate a recount task. Approval is a distinct permission and **the approver may not be the counter** | app | v1 | P2 | `T-090` `P-033` |
| **FR-156** | Cycle counting is a **policy object**: programme type (ABC / random / full / zone / item / discrepancy-triggered), frequency, schedule, scope by zone, ABC class or item, blind flag, recount threshold, approval threshold, `freeze_locations` and a per-run task cap. `freeze_locations` and the recount attempt are what distinguish a counting programme from a spreadsheet | app | v1 | P2 | `P-033` `E-039` |
| **FR-157** | A **full physical stocktake** with a freeze window, a snapshot of book quantity at start, multi-counter zones and approval before posting with the variance value shown. Every auditor attends one and every customer does at least one a year | app | v1 | P2 | `S-091` |
| **FR-158** | **Zero-stock / empty-bin verification** is triggered on the last pick from a location — the highest-yield count type per hour, and nearly free once tasks exist | app | v1.1 | P3 | `T-089` `T-041` |
| **FR-159** | Count posting emits **one movement per non-zero variance line**, carrying the count's reason code, so a count is indistinguishable from any other ledger event to every downstream consumer | app | v1 | P2 | `T-089` `E-038` |
| **FR-160** | **Expiry is a state, not an alert**: a scheduled job moves lots past expiry into an `EXPIRED` status the allocator refuses, and raises a notification at `expiry − near_expiry_days`. A near-expiry report with configurable buckets is shipped with it. This is a dated obligation and it ships with its job, its recipients and its report or not at all | app | v1 | P2 | `E-018` `T-030` `P-051` |
| **FR-161** | The **four shelf-life enforcement points are named separately**, not collapsed into the word FEFO: refuse receipt below X% remaining; allocate earliest-expiry-first; refuse to ship below Y days remaining (per customer or channel); auto-expire on a schedule. A design that says FEFO and implements only the second fails a food or pharma demo on the first and third and fails an audit on the fourth | app | v1·v2 | P2·P5 | `T-030` `F-067` `S-039` |
| **FR-162** | **Aged stock and no-movement buckets are measured from the last outward movement**, not from receipt, with value per bucket and a branch and warehouse split. This is the raw material for the obsolescence percentage and the obsolescence return | app | v1 | P2 | `E-076` |
| **FR-163** | A **reconciliation-exception grid** exposes ledger-versus-position drift, position-versus-allocation drift and orphaned reservations, with an owner and an action, rather than only an alert in a log | app | v1 | P2 | `T-019` `F-091` `E-042` |
| **FR-164** | Scrap and write-off carry a reason, an approval and an explicit **value-destroying movement**. Unexplained shrinkage in a 3PL is a claim against the 3PL | app | v1 | P2 | `F-052` `T-010` |
| **FR-165** | **A threshold column with no scheduled job that reads it is a defect at the moment it is merged.** Every dated obligation in this product — expiry, reservation expiry, obsolescence window, core return deadline, warranty hold, job-work clock, e-way validity, RTO ageing, COD ageing, licence expiry — ships with its job, its notification recipients and its report, in the same task | base·app | v1 | P0 | `P-051` `E-018` `E-043` |

### 6.10 Reservations and allocation *owner: base*

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-166** | Allocation is an **open-item ledger**, never a counter (`L-10`). With a counter you cannot say who holds a reservation, cannot release one order's hold, cannot distinguish soft from hard, cannot reserve a specific lot, serial or LPN, cannot expire a stale reservation and cannot reconcile — so it drifts, and the only repair is to zero it, which releases everyone's stock at once | base | v1 | P0 | `T-014` `F-028` `E-042` `C-022` |
| **FR-167** | Every reservation carries the **holder quad** `(holder_system, holder_document_type, holder_document_id, holder_line_no)` and an `expires_at`, and `DELETE /reservations?holder…` answers *"release everything trip X held"*. Without it a cancelled trip's orphaned reservations silently and permanently reduce availability, and the symptom is the exact support call `FR-037` exists for | base | v1 | P0 | `G-042` `F-028` |
| **FR-168** | **Availability is computed, never stored**: `available = Σ on_hand where status.is_allocatable − Σ open reservations`. A stored column drifts and its formula changes when soft allocation arrives. The denormalised allocated quantity on the position exists only as a cache with a nightly reconciliation | base | v1 | P0 | `T-003` `T-014` `F-028` |
| **FR-169** | Soft and hard reservations are distinct, and **the Release action exists in v1 even though the wave does not**. Release is the moment soft becomes hard and tasks are created; without it every order hard-allocates at creation, a cancelled order's stock stays locked and one shortage blocks another | app | v1 | P2 | `T-014` `T-044` |
| **FR-170** | Reservations **expire**: a scheduled job releases them, notifies the holder, writes a movement-free audit row and feeds an ageing report. A part held against an abandoned estimate is invisible dead stock, and every DMS ages special orders | app | v1 | P2 | `E-043` `G-042` |
| **FR-171** | De-allocation on cancel is **deterministic and reason-coded**, cancels un-started tasks, and has a stated acceptance test: allocate ten, cancel, and availability returns to exactly its pre-allocation value | app | v1 | P2 | `T-049` `F-034` |
| **FR-172** | Allocation strategy is a **configured value, not an if-statement**: strategies are rows carrying a whitelisted ordering key (FIFO, FEFO, LIFO, lot-specific, nearest location, fewest locations, single-LPN-preferred, highest-quantity bin), and rules resolve most-specific-first by site, item, owner, customer and demand type. v1 seeds FIFO-by-receipt and fixed-location-first. Hard-coding FIFO makes FEFO a branch and the allocator untestable by v2 | base | v1 | P2 | `T-043` `F-028` `E-017` |
| **FR-173** | The **rule and strategy that chose the stock are recorded on the reservation row** and shown on its detail view. "Why did the system pick lot B when lot A expires sooner" is asked weekly | base | v1 | P2 | `T-048` |
| **FR-174** | A first-class **availability API**, single and bulk, returns on-hand, hard-allocated, soft-allocated, available, in-transit, on-order and earliest expiry, scoped by item, site, owner and as-of date. Before any vertical wants waves it wants "can I promise this part today", and a quotation screen asks for forty items at once | base | v1 | P2 | `T-085` `G-032` |
| **FR-175** | The **locking discipline for allocation is stated and tested**. Two pickers and one unit is a correctness problem, not a speed problem, and a generated available column does not catch it because on-hand did not change | base | v1 | P0 | `S-085` `C-024` |
| **FR-176** | Where the requested item is short, allocation may consult the **supersession chain** under an explicit rule flag, and reporting distinguishes "stock of A" from "stock of A including superseded equivalents" | app | v1 | P2 | `T-021` `E-057` |

### 6.11 Outbound *owner: app*

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-177** | **One demand model for every demand type** — sales, transfer, work order, replenishment, VAS, sample, scrap, job issue — with document-specific extras in adapter tables keyed to the demand header. Allocation, waving, picking, packing and shipping are identical regardless of why the stock is leaving; three parallel implementations mean three places to fix every allocation bug and three sets of KPIs that do not add up | app | v1 | P2 | `T-042` |
| **FR-178** | The demand line carries **six quantity columns** — ordered, allocated, picked, shipped, cancelled, backordered. Deriving backorder from two of them fails the moment a partial cancel lands | app | v1 | P2 | `F-031` |
| **FR-179** | **Order → many shipments → many cartons** is three tables in v1, even though v1 ships one carton per shipment in practice. A tracking-number column on the order is wrong within a month, and retrofitting changes every screen, export, tracking webhook and channel confirmation | app | v1 | P2 | `F-030` |
| **FR-180** | Priority, `promised_ship_at`, `promised_deliver_at` and an SLA reference are **v1 columns on the order**. Every operational KPI in this category is a difference between two timestamps and none can be recovered later | app | v1 | P2 | `F-032` `F-074` |
| **FR-181** | A **working calendar** with per-warehouse and per-client working days, open and close times, cut-off times and holidays, used by **the same code** for computing a promise and for measuring a breach. Without it a 24-hour SLA measured across Diwali reports a breach the contract does not consider one | app | v2 | P5 | `F-032` |
| **FR-182** | Order **holds are records** with per-type `blocks_allocation` and `blocks_pick` flags; an order releases to picking only when it has zero open holds, and the check is a query rather than a status | app | v1 | P2 | `F-033` |
| **FR-183** | **Order edit after release** is governed by a seeded rule matrix — from-status × edit type → allowed, required permission, compensating action (release reservation, cancel pick task, reprint pick list, void label, unpack, reverse movements) — plus an append-only amendment log. After ship there is no edit; the answer is a return or an RTO, and the rule table says so rather than the UI silently disabling a button | app | v1.1 | P3 | `F-034` |
| **FR-184** | **Fulfilment policy** — ship complete, ship partial and backorder, ship partial and cancel — is set per owner and per channel, with a minimum fill percentage, a backorder hold period and an auto-cancel horizon. Three different customer promises; warehouses that guess get it wrong on the orders that matter | app | v1.1 | P3 | `F-031` `T-047` |
| **FR-185** | A **short pick is a first-class outcome**, not a silently reduced quantity: it records the shortfall against an exception code, releases the unmet reservation, offers re-allocate / emergency replenish / short the line, and — under a site switch — **auto-creates a cycle-count task for the location**, because a short pick is the highest-quality signal of an inventory error a warehouse ever gets | app | v1 | P2 | `T-045` `F-029` |
| **FR-186** | Picking methods are staged and each deferral is stated: **discrete pick in v1**; batch pick in v1.1; cluster, zone, pick-and-pass, pick-to-carton and put-wall in v2 and v3. The pick task carries `owner_id` from v1 so cross-client waving is possible later without a re-key | app | v1·v1.1·v2 | P2·P3·P5 | `F-029` `T-041` |
| **FR-187** | **Wave is a real object and its absence in v1 is a stated deferral, not silence.** v1 ships the Release action on the demand header; v1.1 groups releases into waves and the same action operates on N orders | app | v1·v1.1 | P2·P3 | `T-044` `F-029` |
| **FR-188** | **Pick moves stock to a real, countable staging location; ship confirm relieves it from staging to the virtual customer location and closes the reservation in one transaction.** If stock is relieved at pick, picked-not-shipped goods vanish from on-hand while physically present and a count of the staging lane disagrees | app | v1 | P2 | `T-046` `P-038` |
| **FR-189** | **Dispatch is the inventory-relief event and it is the only one.** Stated as a workflow rule the whole team can hold, because every alternative reading produces a different set of bugs | app | v1 | P2 | `P-038` `T-046` |
| **FR-190** | The **pack session** is designed as an operator flow, not as arithmetic: one active carton, auto-create the first carton on session start, auto-create the next on seal only while units remain, a quantity field on scan, repeat scans merged into the existing pack line rather than N rows of one, a change-package control directly above the scanner, and **no loose packing option**. Loading consumes only sealed cartons. The result is *scan × N, seal × cartons, complete × 1* | app | v1.1 | P3 | `P-037` |
| **FR-191** | **Cartons are mandatory and the reasons are enumerated**: you load and scan cartons, not a thousand items; the consignment note has a mandatory package count; the e-way bill requires package count and description; a carton rides exactly one truck in a split dispatch; damage and loss claims are per handling unit; 3PL handover manifests are carton-based. Item dimensions, weights and stackability are **v1 columns**; cartonisation and dimensional weight are v2 | base·app | v1·v2 | P1·P5 | `P-037` `F-038` |
| **FR-192** | **Scan verification at pick is configuration per task type** — requires location scan, item scan, lot scan, serial scan, quantity entry — honoured identically by web and mobile. A confirm button produces about 98% pick accuracy; scan verification produces above 99.9%, and the difference is the entire business case | app·mobile | v1.1 | P3 | `T-050` |
| **FR-193** | The outbound object chain is **shipment (ours) → consignment (transport, 1:1 and optional) → manifest → trip**, with "add truck" living on the shipment so a child consignment cannot create siblings. A third-party parcel simply has no consignment | app | v1·v2 | P2·P5 | `P-038` `G-013` |
| **FR-194** | **Manifest, handover and pickup request are three objects**, not one: the carrier's signed AWB list, *our* record that N shipments physically left with whom at what time against which signature, and a scheduled request for a vehicle with a window. Keeping them separate is what lets a logistics module take over the transport leg without touching the carrier manifest | app | v1.1 | P3 | `F-040` |
| **FR-195** | The **gate pass is e-way-bill-conditional**: it issues freely where no e-way bill is required and blocks only where one is legally required and not yet generated. Full decoupling would let e-way-mandatory goods leave without one | india·app | v1 | P2-IN | `P-038` `S-024` `D-12` |
| **FR-196** | Carrier, carrier service and carrier account masters exist in `warehouse` in v1, and **`owner_id` on the carrier account is nullable** — null means the house account. That one nullable column is the whole of "ship on the client's account", a standard contract clause | app | v1 | P2 | `F-036` |
| **FR-197** | **Labels are stored artefacts with a void path**, never deleted: type, carrier, tracking number, format, a link to the platform document, generated-at, voided-at, void reason and the carrier's void reference. An Indian carrier bills for a generated-and-unused AWB in some contracts and the void call is what stops it | app | v1.1 | P3 | `F-039` |
| **FR-198** | Tracking events are stored **normalised and raw**, with per-carrier status mappings held as **data**, so a mapping can be corrected and the history re-derived. A Java `switch` per carrier becomes unmaintainable at carrier six | app | v2 | P5 | `F-043` |
| **FR-199** | The **five relocatable objects** — carriers, tracking events, NDR, RTO receipts and COD remittances — are referenced by a stable code resolved through a service, never by an FK from the referencing table, so moving them into a logistics module later is a refactor and not a data migration. *R4 names one movable boundary; R7 `G-013` finds five and this document follows R7* | app | v1 | P2 | `G-013` `F-036` |
| **FR-200** | **Rate shopping persists the quote** — carrier, service, account, amount, transit estimate, billable weight, whether it was selected and why — because the selection has to be explainable three months later when the carrier invoice disagrees. Rules are bounded rows with an objective, an allowed and blocked carrier list and a maximum, never an expression language | app | v2 | P5 | `F-037` |
| **FR-201** | **Pincode serviceability gates the rate shop; address validation only warns.** Serviceability asks whether *this carrier* delivers here, accepts COD here, collects a return here and whether it is an out-of-delivery-area location with a surcharge — and in India it is checked before rating, because half the carriers do not serve half the pincodes | app | v2 | P5 | `F-041` |
| **FR-202** | An **AWB pool**: waybill numbers are fetched in blocks ahead of time, held per carrier, account, service and payment mode, claimed transactionally with `SELECT … FOR UPDATE SKIP LOCKED`, and topped up by a background job behind a low-watermark alert. Indian carriers do not mint a tracking number as a side effect of a label call; a design that assumes they do does not work here, and running out of AWBs stops dispatch entirely | app·adapter | v2 | P5 | `F-042` |
| **FR-203** | **NDR is a workflow with a response clock**, not an exception code: a reason, a computed response-due time from a per-carrier SLA, an action (reattempt, reattempt on a date, change address, change phone, authorise RTO, hold at hub), the carrier acknowledgement and the outcome — with a queue sorted by due time, bulk actions and a breach counter. No response and the shipment auto-RTOs at the client's cost | app·adapter | v2 | P5 | `F-044` |
| **FR-204** | **COD remittance reconciliation happens where the AWB lives.** A remittance carries a UTR, gross, deductions and net; its lines match to shipments with a match status and a variance; delivered-but-not-remitted ages on a report; and the matched net emits a receipt envelope to accounting while the deduction emits an expense line. Warehouse posts no journal itself | app | v2 | P5 | `F-045` |
| **FR-205** | **RTO is an inbound stock stream, not an order status.** The RTO columns — initiated at, reason, the return leg's own AWB, received at, status — are **v1 columns on the shipment**; the consignment receipt, AWB scan, match, open-and-verify, grade and put-back flow is v2, and a lost RTO becomes a claim rather than a silent shrinkage adjustment | app | v1·v2 | P2·P5 | `F-046` |
| **FR-206** | The **pack photo and scale weight are captured at pack time in v1**, because the evidence for a carrier weight-discrepancy dispute cannot be created retroactively; the dispute object, its due date and the carrier-invoice reconciliation are v2 | app | v1·v2 | P2·P5 | `F-047` |
| **FR-207** | The **channel master lives in base** (the ledger's source lineage and the item alias both reference it); per-owner channel accounts live in `warehouse` with credentials stored through the platform's secret masking; **each connector is an adapter and `warehouse-base` never names a channel vendor** | base·app·adapter | v1·v2 | P1·P5 | `F-026` |
| **FR-208** | Channel order import is **idempotent on (channel account, external order id)** with an external version so a stale re-poll is discarded, and an import decision log records created / updated / ignored-stale / rejected with the reason. "The order never came through" is the commonest support call in this category and must be answerable in one screen | app | v2 | P5 | `F-027` |
| **FR-209** | **Channel inventory publish rules** are the oversell control: a basis (available, on-hand, available-minus-buffer, fixed, percent), a buffer, a maximum, a minimum threshold below which zero is published, included statuses and warehouses, and a publish log recording what was pushed and what the channel acknowledged | app | v2 | P5 | `F-035` |
| **FR-210** | A signed, expiring **public tracking link** per shipment and consumer notification rules on dispatch, out-for-delivery, NDR and delivery, reusing the platform's existing providers rather than adding a second | app | v2 | P5 | `F-049` |
| **FR-211** | **Seal numbers are captured at load and at unload**, and the receiving session owns the seal, the gate pass, the driver and the arrival photographs | app | v1.1 | P3 | `P-020` `P-038` |

### 6.12 Execution, mobile, scanning and printing *owner: app · mobile*

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-212** | **Tasks exist in v1 even though v1 has no RF gun.** Every tier-1 WMS separates the business document from the execution instruction. v1 creates one task per receipt line and per pick line and completes it in the same request; the screens change in v1.1, the model does not. If v1's receiving and pick screens write the ledger directly, then RF, assignment, interleaving, labour measurement, exception queues, wave release and automation are each a rewrite of inbound and outbound rather than a new consumer of an existing table | base | v1 | P0 | `T-041` |
| **FR-213** | Tasks carry `assigned_at`, `started_at`, `completed_at`, paused seconds, `device_id` and travel distance **from v1**, because labour reporting in v2 needs history and a duration cannot be backfilled | base | v1 | P0 | `T-058` `F-074` |
| **FR-214** | Task assignment supports **both pull and push** from one table: an operator asks for the next task honouring zone, task type and equipment capability, and a supervisor assigns a queue. Building one and adding the other later changes the task lifecycle | app | v1.1 | P3 | `T-055` |
| **FR-215** | A task carries priority, zone and a **required resource type**, with user qualifications, so assignment does not send a trolley picker to a high rack and interleaving is possible. Columns in v1, behaviour in v1.1 and v2 | base·app | v1·v1.1 | P0·P3 | `T-056` `T-041` |
| **FR-216** | A **supervisor exception console** is one grid over short and exception-coded tasks, reconciliation exceptions and failed inbound messages, with actions. Without it every exception goes to a phone call | app | v1.1 | P3 | `T-057` `T-045` `T-092` |
| **FR-217** | The **mobile screens are named in the design set at the same time as the web ones**: Receive, Putaway, Move, Pick, Pack, Ship, Cycle Count, Stock Enquiry, Task List. The prior product shipped ~65 web operations screens and **zero** mobile screens; a WMS without a handheld is a stock ledger with a web form (`D-13`) | mobile | v1.1 | P3 | `T-051` `E-072` `P-054` `D-13` |
| **FR-218** | **A mobile decision is stated per screen with a reason, and silence is a defect.** Where no mobile counterpart is built, the contract says so and says why (`D-13`) | mobile | v1 | P0 | `P-054` `D-13` |
| **FR-219** | RF screens have their own **interaction contract**: one active input, scan advances, no free text where a scan exists, no mouse, no scrolling, a persistent current-task banner, an always-available report-exception action, and every screen resumable after a dropped connection. Designing them as mobile versions of web forms is the standard failure | mobile | v1.1 | P3 | `T-052` `S-088` |
| **FR-220** | RF screens are a **separate screen family** from the generic list screen, which is the wrong base for one-handed, gloved operation. Text filters are now supported on the shared list header but **date filters still are not**, and that constraint is recorded rather than discovered | mobile | v1.1 | P3 | `C-044` `S-088` |
| **FR-221** | Offline behaviour is decided per screen and stated: **read-cached** lists for putaway and pick; **queued writes** with a per-scan idempotency key and surfaced — never swallowed — conflicts for counting, receiving and picking; **no true offline authority**, ever, because it would falsify the append-only sequence and the hash chain simultaneously. There is no offline mutation queue anywhere in this codebase today | mobile·base | v1·v1.1 | P0·P3 | `T-053` `S-086` `E-074` |
| **FR-222** | A **device registry** with device inventory and assignment, device-bound long sessions, fast shared-device sign-in, session handover at shift change and remote session kill on a lost gun. The platform's existing device registration is a push-notification token, not a device | base·mobile | v1.1 | P3 | `S-088` |
| **FR-223** | A weighing or measuring instrument is a **legal instrument**: it carries a verification certificate number and validity, and a weighing performed on an out-of-verification instrument is flagged on the receipt | app | v2 | P5 | `S-034` `S-058` |
| **FR-224** | **Printing is infrastructure and it has an owner, and it lands in v1** — a case-insensitive search for `zpl`, `escpos` or `dymo` across all Java and TypeScript returns **0**, so there is no label or document rendering anywhere in this codebase and it is net-new. **v1 ships the template object and the renderer**: a template with a document kind, a format, a body and its dimensions, rendered to **ZPL first** and to PDF for laser, with a print-job log that **flags reprints** — a reprinted pallet label is a duplicate licence plate in the wild. **v1.1 ships the print server**: direct-to-printer from the handheld over the network rather than a browser download, and a printer registry holding printer per zone and dock, default label size, DPI and media, because 203 against 300 dots per inch changes every barcode's width | base·app | v1·v1.1 | P2·P3 | `S-087` `T-054` `E-073` `D-12` |
| **FR-225** | The **eleven label and document kinds ship in v1**: item and shelf label, LPN or pallet label with a GS1-128 symbology, carton label, shipping label, location label, goods-receipt note, pick list, packing slip, delivery document, movement-document print and hazard class label. A warehouse that cannot print a pick list, a receipt note, a delivery document or a bin label cannot be operated, and loses to a spreadsheet and a desktop label printer | app | v1 | P2 | `S-087` `F-062` `D-12` |
| **FR-226** | Print templates carry an optional `owner_id`, because client-specific label layouts are a real 3PL requirement and that column is the whole of it | app | v2 | P5 | `F-062` |
| **FR-227** | **Labour tasks are timed**: who, from when to when, paused seconds, units processed, reference and device. The same record is the only honest input to VAS-by-the-minute billing and to cost-to-serve | app | v2 | P5 | `F-023` `F-079` |
| **FR-228** | **Engineered labour standards are not built before a year of our own actual data.** We measure actual task duration and report it; we do not claim to compute an engineered standard, and incentive pay is never computed from a warehouse metric | app | v3 | P6 | `F-079` `T-058` |
| **FR-229** | Automation, conveyors, sorters, AS/RS and robotics integrate through a **published task-event contract and the movement port** (`actor_type = DEVICE`), never through protocol-level control in our codebase. An AMR vendor integrating against a documented event stream is a two-week integration for them | base | v3 | P6 | `T-059` `F-072` |

### 6.13 Valuation and the accounting seam *owner: base (cost) ↔ accounting (the ledger)*

> The tier-1 consensus is that a WMS holds **no value at all** — SAP EWM, Manhattan, Blue Yonder,
> Körber and Oracle WMS Cloud are quantity engines that hand movements to an ERP. **We deliberately
> depart from it**, and `D-6` makes the departure a rule rather than a preference: *whichever system
> is authoritative for quantity is authoritative for cost, and accounting is always authoritative for
> the ledger.* With warehouse installed, warehouse runs the costing engine — because only warehouse
> holds the grain FEFO and specific identification need, and because a standalone install must value
> its stock with no accounting module present. With warehouse absent, accounting's own stock engine
> does both, exactly as its design set already says. **R5 `S-066` argued for the opposite split and is
> overruled**; the unacceptable outcome it warned about — value computed in two places — is prevented
> by the authority rule instead.
>
> **See also `FR-446` in §6.26** — the two falsifiers that make the authority rule testable.

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-230** | **Whichever system is authoritative for quantity is authoritative for cost; accounting is always authoritative for the ledger.** Warehouse is the system of record for every movement, position, count, adjustment and physical truth **at full grain, and therefore for cost**: it runs the costing engine, holds the cost layers, and produces the inventory valuation. Accounting receives **valued** movements and posts them, and owns everything downstream — the GL, revaluation approval, NRV and provisioning, period close and the statements. Where warehouse is installed, accounting's quantity balance and its own costing stand down: its balance becomes a read-through projection, its cost layers are not maintained, and its counts and stock journals become inbound document kinds rather than screens. Two systems authoritative for one quantity at two grains, with two counts and two adjustment documents, is the failure that killed a shipping competitor as a standalone product. *R5 `S-066` argued the opposite — that accounting computes value — and `D-6` **overrules it**, for the two reasons in `FR-446`. Its underlying concern, that the costing method must live in exactly one place per install, is met by the authority rule rather than by fixing the place.* **⛔ OD-1** — the reciprocal edits are the accounting set's to make, and are now a three-state decision there | base | v1 | P0 | `S-064` `S-066` `E-001` `T-060` `D-6` `OD-1` |
| **FR-231** | **Warehouse never writes an `acc_*` table and never imports an `ai.accounting*` type**, enforced by an architecture test that fails the build. The accounting ledger is hash-chained and append-only and a foreign writer breaks the chain that is its whole claim | base | v1 | P0 | `S-068` `D-6` |
| **FR-232** | Every movement carries `handover_id` and `posting_status` ∈ {`NOT_APPLICABLE`,`PENDING`,`POSTED`,`REJECTED`}, and a **rejected-handover queue has an owner and an alert**. Two columns, without which "does the stock ledger tie to the GL" is permanently unanswerable for the period before the seam was built — which is exactly the period the first audit covers | base | v1 | P0 | `S-067` `D-6` |
| **FR-233** | Posting-relevant events hand over **one envelope each**, through accounting's existing source-document port, carrying the idempotency key, company, branch, document kind, posting date, reason code and, per movement line, `owner_type`, `duty_status`, lot and serial identity, quantity, base UoM, **the unit cost and extended value warehouse computed**, and `cost_basis` declaring the basis on which it was computed and whether it posts at all. **Accounting does not re-cost what it is handed**; the envelope's value is authoritative and a re-costing step on the receiving side would reintroduce the two-truths failure the authority rule exists to prevent. **⛔ OD-1** | base·app | v1 | P2 | `S-065` `S-066` `D-6` `OD-1` |
| **FR-234** | Cost is held as **layers with a remaining quantity plus a consumption table** linking each issue to the layers it consumed. A sales return or credit note consumes in reverse and **restores the original layer**. A cost column on a balance cannot produce FIFO, cannot produce specific identification, cannot be revalued without destroying history and cannot answer what the stock we shipped last March cost | base | v1 | P2 | `T-061` `E-035` `S-070` `C-027` |
| **FR-235** | Valuation methods: **weighted average and FIFO in v1** with the layer table present and the method **configurable per item category × site**, standard cost with purchase-price and usage variances in v1.1, and **specific identification for serial- and lot-tracked items** — required here even though the accounting set defers it, because vehicles, high-value electronics and any serialised spare are non-interchangeable by definition, and because FEFO and specific identification are **not expressible at accounting's item × godown × batch × serial grain**. That grain argument is half of why the costing engine is here rather than there. **LIFO is never built, and this document says why**: prohibited under Ind AS 2 / IAS 2 and ICDS II, and a migrating customer will ask. **⛔ OD-6** | base | v1·v1.1 | P2·P3 | `S-053` `T-068` `S-065` `C-027` `D-6` `OD-6` |
| **FR-236** | The **valuation grain is declared, not emergent**: `(company, owner, item, site)`. Site-level makes an inter-site transfer a valuation event; company-level hides branch performance. Changing it later restates every balance, and the inter-site transfer valuation rule — transfer at the sending site's cost, so there is no profit in stock to eliminate — is written at the same time | base | v1 | P2 | `T-062` |
| **FR-237** | The **moving average after the movement is snapshotted on the movement row**. A backdated receipt recomputes the average; without the snapshot there is no evidence of what the cost was on 31 March and the year-end valuation cannot be reproduced | base | v1 | P2 | `S-053` `C-027` |
| **FR-238** | **Landed cost** has an apportionment basis per charge (value / quantity / weight / volume / manual), retrospectively revalues the receipt layer, and — where the layer is already partly consumed — splits into a layer adjustment and a **COGS adjustment for what already shipped**, with a link from the charge document back to the receipt movements it loads. The column lands in v1 always zero; the document is v2. The trap: a port whose `unit_cost` is write-once cannot carry this | base·app | v1·v2 | P2·P5 | `T-063` `S-071` `E-036` |
| **FR-239** | **The apportionment basis lives on the receipt, not on the freight charge.** The charge is a transport fact; the effect on stock value is a warehouse fact | app | v1 | P2 | `G-023` |
| **FR-240** | **Revaluation is a document, not an `UPDATE`** — a movement type with zero quantity and a non-zero value, so the stock ledger and the ledger of record stay in step through a price escalation or a year-end write-down. **Warehouse posts the movement; accounting approves the revaluation**, because approval is a downstream act on the ledger of record | base·app | v1 | P2 | `E-037` `F-088` `D-6` |
| **FR-241** | **NRV write-down is a register, not a one-way provision column**: item or lot, assessed net realisable value, basis, assessor, date, amount and **the reversal linked to the original**, because Ind AS 2 requires reversal when the cause ceases. **Warehouse supplies the evidence and the candidates** — ageing, slow-moving, obsolete, damaged, expired — and posts the resulting movement; **accounting owns NRV and provisioning** and the judgement someone signs | app·base | v2 | P5 | `S-072` `D-6` |
| **FR-242** | **Cut-off is answered by three columns and the owner dimension**: `invoice_matched` on the receipt for goods-received-not-invoiced, `ownership_transfer_point` on the purchase and transfer documents for goods in transit under the applicable Incoterm, and `owner_id` for consignment. A design that keys stock only to physical locations we control reports the wrong balance sheet twice a year | app | v1·v2 | P2·P5 | `S-073` `G-018` |
| **FR-243** | **COGS recognition point is a configured policy** — dispatch, delivery or invoice — with a stock state per stage and an in-transit account. Warehouse computes the cost of goods sold at the configured point from its own layers and hands it over valued; accounting posts it. Hardcoding "COGS on dispatch" is wrong every month end for every delivery-terms customer | app·base | v2 | P5 | `S-075` `D-6` |
| **FR-244** | An inter-branch transfer carries **two numbers**: a transfer price (the tax document) and a cost (what follows the goods), plus the data to eliminate unrealised profit. One unit cost either overstates inventory or files a wrong invoice | app·india | v1·v1 | P2·P2-IN | `S-074` `E-050` `D-12` |
| **FR-245** | The cost layer carries `currency_code` and `exchange_rate` from v1, defaulted to the install's base currency. Imported spares are bought in USD or EUR, and a layer without them can never record what was actually paid | base | v1 | P2 | `T-070` |
| **FR-246** | The envelope carries the **classification quad** — movement type, reason code, item group and owner type — and **accounting resolves it to an account**. Account determination is a ledger concern and the ledger is accounting's. *R2 `T-065` puts the posting-rule table in the warehouse and this document diverges under `D-6`: warehouse is authoritative for cost, accounting for the ledger, and a chart of accounts the warehouse does not own is not a table it should key on. What warehouse owes is a classification stable enough to key on, which is `FR-003` and `FR-019`* | base | v1 | P2 | `T-065` `D-6` |
| **FR-247** | The **stock-to-GL reconciliation report** — opening value + receipts + adjustments + revaluations − issues = closing value, per site, owner and item group, with the GL control-account balance and a variance column that drills to the offending movements. It is the report that makes a finance director trust the system and the report that finds every integration defect; accounting makes it a blocking close precondition, so warehouse must be obliged to produce the number it reconciles against | app | v1 | P2 | `T-066` `E-002` `S-067` |
| **FR-248** | The warehouse **publishes movements already valued and never writes journals**. Failures land in a retryable queue, not in a swallowed exception. The accounting module has its own posting rules, immutability triggers, period locks, numbering and approvals, and a foreign writer defeats all of them | base | v1 | P2 | `T-067` `D-6` |
| **FR-249** | **Opening balance is a movement, not a column**, posted from a virtual opening-balance location with unit costs, creating the first cost layer. Writing opening stock straight to the balance table means the ledger does not explain it, the rebuild invariant fails on day one, and the first issue has no cost | app | v1 | P2 | `T-069` `E-088` |
| **FR-250** | A **second, tax-basis value** is carried alongside the book value where the jurisdiction requires inventory to be valued inclusive of duties and taxes actually paid. Warehouse carries both bases because warehouse owns the cost; with one unit cost per movement the adjustment is a spreadsheet forever | base·india | v2 | P4 | `S-053` `D-6` |
| **FR-251** | **Stock periods are separate from accounting periods and close earlier**, and the two locks are synchronised so the ledgers cannot be closed at different moments and disagree at the boundary | base | v1 | P0 | `E-046` `S-090` `T-064` |

### 6.14 Replenishment and reorder *owner: app*

> The tier-1 boundary is consistent and we draw it in the same place: a WMS holds reorder point,
> min/max and safety stock as item-site attributes and generates replenishment inside the four walls;
> forecasting, multi-echelon optimisation and purchase planning belong to a planning product.

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-252** | Min, max, reorder point, reorder quantity, safety stock and lead time live on **item × site** (v1) and **item × location** (v1.1). A ten-branch dealer does not want the same reorder point at the flagship and the satellite | base | v1·v1.1 | P1·P3 | `T-027` `E-013` |
| **FR-253** | The **replenishment run produces a document, not a grid**: suggestions carrying item, site, on-hand, allocated, on-order, ROP, suggested quantity, a source (`PURCHASE` or `TRANSFER`), a source warehouse, a supplier and a reason, which the buyer edits and converts in one action. **The warehouse never becomes a purchase-order engine** | app | v1 | P2 | `T-084` `E-040` `G-036` |
| **FR-254** | The run **proposes a sister-branch transfer before a purchase** where another branch holds stock above its own minimum. For a multi-branch dealership that is where the money is: the part is already in the group | app | v2 | P5 | `E-041` |
| **FR-255** | **Pick-face replenishment tasks** are generated from item × location min/max, with priority against pick starvation | app | v1.1 | P3 | `T-027` `T-041` |
| **FR-256** | **Demand history** records hits and quantity per item, site and month, maintained by movement posting, with adjustments, warranty issues and internal consumption excluded via the reason code's `affects_demand_history`. Hits matter more than quantity — two hits of one unit is a stocking case, one hit of two units is not | app | v1 | P2 | `E-066` `E-033` |
| **FR-257** | **Lost sales are captured**, automatically by the insufficient-stock guard at the counter and at the job-issue screen, and manually for "not catalogued", with a type and a resolution. The demand you refused is still demand; without it the stocking level converges on the stock you happen to have, and fill rate has no honest denominator | app | v1 | P2 | `E-067` `S-063` `E-045` |
| **FR-258** | The **best stocking level is computed, not typed**: phase-in after *k* hits in *m* months, a level from the demand window and a days-supply target, phase-out after *n* months with no hits, under a named parameterised policy. No human maintains 30,000 reorder points, and this is the single biggest gap between a stock system and a parts system | app | v3 | P6 | `E-066` |
| **FR-259** | Emergency replenishment triggered by a short pick, opportunistic top-off during idle time, and break-case replenishment from case reserve to an each pick face | app | v2 | P5 | `T-041` `E-040` `T-045` |
| **FR-260** | The purchase document carries an **order source** — stock, daily, VOR, emergency, special order, back order, initial stock — with a customer-waiting flag, a linked job reference and a promised date. VOR and emergency purchases are **excluded from lead-time statistics** or the reorder mathematics is poisoned, and the order mix is a monthly management question | app | v1 | P2 | `E-061` |

### 6.15 Kitting, assembly and value-added services *owner: app*

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-261** | Kit assembly and disassembly are **balanced ledger transactions**, never an update to a parent quantity. A stocked kit is assembled in advance and has its own on-hand and cost; a phantom kit is exploded at allocation and never has stock | app | v1.1 | P3 | `T-031` `E-044` `F-057` |
| **FR-262** | The **work order is both the VAS record and the light-manufacturing record**: type, kit, output item, planned and produced and scrapped quantities, a scrap reason, planned and actual start and end, assignee, a client-instruction document reference and a billing charge code. The instruction document exists because VAS instructions arrive as a PDF and the operator needs exactly the version that was priced | app | v1.1 | P3 | `F-058` |
| **FR-263** | An assembly completion posts **one balanced movement** that balances **by value, not by quantity** — components in, kit out — and carries a variance reason where it does not | base·app | v1.1 | P3 | `F-059` |
| **FR-264** | Repack, break-case and UoM conversion are **two-sided ledger events**, never an `UPDATE` to a quantity in a different unit | app | v1.1 | P3 | `T-011` `T-015` |
| **FR-265** | **Packaging and consumables are ordinary stock items**, consumed by a line on the same movement as the pack, owned by the house owner unless the client supplies them — which is why the packaging master carries a nullable owner | app | v1.1 | P3 | `F-060` `F-038` |
| **FR-266** | **Lot and serial genealogy survives assembly**: which input lots and serials went into which output unit, recorded at completion. A recall that must cross a kit boundary has nothing to walk otherwise | base | v2 | P5 | `S-008` `F-065` |
| **FR-267** | VAS priced **by the labour minute** reads the timed work-order task, and the same record is the cost side of client profitability | app·3pl | v2 | P5 | `F-023` |
| **FR-268** | **Multi-level BOM with routings is not built.** It belongs to a manufacturing module; the re-entry path is that a manufacturing system posts N issues and one receipt through the port and the cost-layer table values them | — | v3 | P6 | `E-044` |

### 6.16 Returns and reverse logistics *owner: app*

> **`A-1` moved the cut line.** Three reviews placed returns at v1 or v1.1 and the ladder had all
> reverse logistics in v2; a customer return that cannot be received is a stock movement the ledger
> simply loses. **Basic returns are v1/P2** — the sales-return receipt, the purchase return and
> return-to-vendor, and disposition to a stock status (restock · quarantine · scrap). **Full reverse
> logistics stays v2/P5** — the RMA portal, grading and refurbishment, the credit interface, and the
> undelivered / return-to-origin / cash-on-delivery stream.

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-269** | **The return receipt is the primary object and the RMA is optional**, matched to it later on a screen rather than by re-receiving. Modelling returns as "an RMA that is later received" makes the blind return unrepresentable, and in India and in marketplace returns generally the blind return is the majority case | app | v1 | P2 | `F-050` |
| **FR-270** | `return_type` — customer return, RTO, refused delivery, cancelled in transit, vendor return, recall, client withdrawal, marketplace return, warranty, exchange — is a **day-one column**, because the disposition rules branch on it: an RTO has no customer to refund, a recall must not be restocked under any disposition, and a client withdrawal is an outbound billed differently | base | v1 | P0 | `F-054` |
| **FR-271** | **Returns land in a dedicated stock status, never straight to available** | app | v1 | P2 | `F-068` `F-052` |
| **FR-272** | Inspection and grading happen **at the point of receipt**, with a condition grade from a seeded vocabulary, notes, photographs, serial and lot verification, weight check and packaging-intact flags. Per-client inspection checklists are v2, because a hard-coded checklist is unsellable | app | v2 | P5 | `F-051` |
| **FR-273** | **Disposition is a registry** and each value posts a specified movement to a specified status. **v1 ships the three that close the loop** — restock to available, quarantine for investigation, and scrap — so a return can always be put somewhere. v2 adds the rest of the vocabulary: refurbish, repack, return to vendor as a shipment, return to client, hold for client decision and donate. **A disposition never silently discards stock**: scrap and donate post an explicit value-destroying movement with a reason and an approver | base·app | v1·v2 | P2·P5 | `F-052` `G-062` `D-12` |
| **FR-274** | **The warehouse emits the disposition; it never decides a refund.** There is no refund screen, no refund amount and no payment path in any warehouse module in any version. A refund is a receivable event with tax consequences and it belongs where the receivable lives | app | v1 | P0 | `F-053` |
| **FR-275** | **Return to vendor is an ordinary outbound**, with a vendor party and a reference to the originating receipt or lot — it is not a special ledger case. **The movement and the document are v1**, because a purchase return that cannot be shipped is stock the ledger cannot release; **the emitted debit-note proposal and the credit interface are v2** | app | v1·v2 | P2·P5 | `F-056` `P-028` `D-12` |
| **FR-276** | **Obsolescence return to the OEM**: an authorisation with a window, an allowance amount, a claimed amount, eligibility rules per line, a restocking fee and a **scheduled job that warns before the window closes**, plus a candidates report combining no-movement-in-N-months, OEM eligibility and remaining allowance. Missing the window converts inventory into a write-off, and no generic product models it | app | v2 | P5 | `E-060` |
| **FR-277** | **Cores are inventory.** A `CORE` item type linked to the serviceable part, a core charge, a core-bank location with its own valuation, a core transaction ledger with a due date and a status ladder from charged through credited, and an ageing job on uncredited cores. A parts business that cannot track cores loses real money, and no tier-1 WMS models it | app·adapter | v2 | P5 | `T-082` `E-063` `S-047` `P-032` |
| **FR-278** | **Warranty scrap-and-hold**: a part replaced under warranty moves to a warranty-hold location tagged with the claim, held until a retention date, with a scheduled job flagging holds past the date for scrap approval and a **permission required to release early**. Scrapping it early forfeits the claim | app·adapter | v2 | P5 | `E-064` |
| **FR-279** | The **marketplace return-claim window**: a claim type, a due date computed at receipt from a per-channel window, photographic evidence, a claim amount and a settlement, in a queue sorted by due date. Sellers routinely lose one to three percent of revenue purely by missing this clock | adapter | v2 | P5 | `F-055` |
| **FR-280** | **Recall**: quarantine all matching on-hand stock **in place** with a status-change movement, list every shipment that carried the lot with its consignee and tracking, release every reservation allocated to it, and export the affected-customer list. All four are single queries if and only if lot and serial land on the ledger line in v1 | app | v2 | P5 | `F-066` `S-040` `F-063` |

### 6.17 Third-party logistics *owner: warehouse-3pl*

> `warehouse-3pl` is a real module — about 28% of the 3PL capability surface is genuinely 3PL-only and
> cohesive — but it is **a thin module standing on a wide base concession**, and the concession is not
> optional, not deferrable and not flaggable. A feature flag would not save a single column, because
> the unaddable items are in `warehouse-base` and are required whether or not anyone ever buys 3PL.

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-281** | `warehouse-3pl` depends on base and app; **neither depends on it**. No `whb_`/`wh_` table has a foreign key to a `wh3_` table, no service imports the 3PL package, and no migration below the 3PL band references a `wh3_` name. The only structural link is the 3PL client's FK to the base owner, and it points the right way. A build-time check enforces it, because the first violation is always innocent and always load-bearing | 3pl | v2 | P5 | `D-11` `D-1` `F-002` |
| **FR-282** | A **client is an object**, not a customer record: contract start and end, notice period, billing cycle and day, currency, payment terms, credit limit, a status ladder from prospect through offboarding, a go-live date, a minimum monthly charge and a tax profile. A 3PL's growth is measured in clients onboarded per month | 3pl | v2 | P5 | `F-007` |
| **FR-283** | **Client onboarding is a task set from a template**, so every client is onboarded the same way, plus a per-client document number series — a client sees *their* order numbers, not ours | 3pl | v2 | P5 | `F-007` |
| **FR-284** | The **client portal is a permission surface over the existing screens**, not a second application with its own authentication. v1.1 of the portal surfaces stock, inbound ASN creation and receipt status, outbound order creation and CSV upload with cancel-while-unallocated, shipment tracking, returns and billing runs; v2 adds a document vault, dispute raising, scheduled reports, client API keys and per-client notification routing | 3pl | v2 | P5 | `F-008` `T-076` |
| **FR-285** | The **billable-event meter is append-only and reversible**, exactly like the stock ledger, with its own idempotency key on `(source_system, source_event_key)`. A cancelled pick does not delete its billable event; it adds a reversing one. That is what makes a re-run of a period produce the same number twice and a dispute resolvable without archaeology. An excluded event carries a reason and an author — never a deleted row | 3pl | v2 | P5 | `F-011` `T-071` |
| **FR-286** | **Charge codes are a master** with a category, a default UoM, recurring and pass-through and taxable flags, a tax code, a SAC/HSN code and a **revenue purpose code** the accounting module resolves to an account — never a GL account id, because accounting owns the chart. Around forty codes are seeded so a new client's rate card is built by pricing existing codes rather than inventing strings; the minimum true-up and the SLA credit are charge codes, not special cases in the biller | 3pl | v2 | P5 | `F-013` |
| **FR-287** | **Rate cards are versioned and effective-dated**, a card may inherit a standard card and override lines, and a billing run rates each event against the version live **on that event's date**. Resolution is most-specific-wins with an explicit priority order and a **fail-rather-than-guess rule**: an unrated event blocks the run and names the missing combination, and is never silently rated at zero | 3pl | v2 | P5 | `F-014` `T-075` |
| **FR-288** | **Storage billing implements four methods** — period-end snapshot, period-start snapshot, anniversary (each pallet billed for a storage month starting on its own receipt date), daily average and split month — over seven bases — pallet, location, unit, weight, cubic, square feet occupied and square feet allocated — with free days, a minimum billable quantity and aged-inventory surcharge bands. Anniversary is the one that cannot be computed from a month-end balance and is the clearest single argument for `FR-100`'s LPN `received_at` | 3pl | v2 | P5 | `F-015` |
| **FR-289** | **Daily storage snapshots are persisted, not recomputed** — one row per date, client, owner, warehouse, basis and identity, carrying the oldest receipt date as the anniversary anchor, the age in days and the outbox cursor at computation time. A re-run for a date **supersedes** rather than updates, with the superseded row retained, because a billed snapshot that silently changes is the same defect class as a mutable ledger. **The nightly job starts in v1**, because it doubles as the ageing and days-on-hand source and because starting it in v2 means no billing history | base·3pl | v1·v2 | P2·P5 | `F-016` `T-072` |
| **FR-290** | The **minimum monthly charge posts a metered true-up event** on a seeded charge code with the arithmetic shown, not a hidden invoice line. It is visible in the meter, disputable, reversible and on the portal. It is also the single most common source of leaked 3PL revenue when it is a manual adjustment | 3pl | v2 | P5 | `F-017` |
| **FR-291** | **Accessorials are ad-hoc charges with an author, a date, a reason and an approval threshold** above which a second user must approve, keyed in under thirty seconds from a dedicated screen. Auto-captured accessorials — detention from the dock appointment, after-hours from the receipt timestamp against the client's calendar — write the same table with their own source | 3pl | v2 | P5 | `F-018` |
| **FR-292** | The **billing run is an object with a frozen approved state**: a period, a type, a status ladder, rated and approved and invoiced timestamps, totals and an unrated-event count that **blocks the transition to review**. Re-rating is permitted before approval and forbidden after; a change after approval is a **new ad-hoc run carrying reversing events**, never an edit | 3pl | v2 | P5 | `F-019` |
| **FR-293** | **Disputes are records** raisable from the portal, with a reason, a disputed quantity and amount, a status and a resolution. An upheld dispute posts a reversing or credit **billable event**; it never edits a billed line | 3pl | v2 | P5 | `F-020` |
| **FR-294** | **`warehouse-3pl` contains no invoice, no numbering sequence and no tax engine, in any version.** An approved run emits **one AR document envelope** to accounting carrying the party, date, currency, one line per run line with its revenue purpose code, SAC/HSN, quantity, UoM, rate, amount and tax code, and a stable idempotency key; accounting resolves the account, the tax, the place of supply, the number and the e-invoice. Where no accounting module is installed the same envelope exports as CSV and the run is marked invoiced manually — **the port shape does not change** | 3pl | v2 | P5 | `F-021` `T-078` |
| **FR-295** | **Four freight-billing modes** — at cost, cost plus percent, cost plus fixed, own published tariff, and the client's own carrier account with no freight charge at all. The carrier's actual charge arrives later than the shipment, so the pass-through is metered at the quoted amount and **reconciled when the carrier invoice lands** | 3pl | v2 | P5 | `F-024` |
| **FR-296** | **Rate escalation generates a new rate-card version for review; it never mutates an active card.** Deferred because a spreadsheet plus versioning does the job for the first hundred clients — recorded so it is not later discovered as an oversight | 3pl | v3 | P6 | `F-022` |
| **FR-297** | **SLA definitions, measurements and breaches are objects.** A definition names a metric, a target, a comparison, a measurement window, a calendar, exclusion rules and a penalty charge code. A measurement stores the **numerator and the denominator**, not just the percentage, because every SLA conversation begins with "which orders were in the denominator" | 3pl | v2 | P5 | `F-075` |
| **FR-298** | The portal carries a **performance tab** rendering SLA measurements as trend plus current period with drill-through to the failing orders, permission-filtered to the client's own owner, and a scheduled monthly export | 3pl | v2 | P5 | `F-077` |
| **FR-299** | A confirmed breach with a penalty charge code posts a **negative billable event** on the SLA-credit code, subject to approval, appearing as a visible credit line. Deferred to v3 because until the measurements are trusted an automatic credit is a liability — but the charge code and the foreign key exist from v2 so the wiring is a service, not a migration | 3pl | v3 | P6 | `F-078` |
| **FR-300** | **Owner segregation is enforced at the row level in the query layer**, with a negative test per endpoint. A client seeing another client's stock is a contract breach, not a bug, and a UI filter is not a guard — this codebase's own memory records the identical class of problem for branch scope | 3pl | v2 | P5 | `T-073` `F-004` |
| **FR-301** | **Client GST registrations** with the warehouse declared as an additional place of business, a certificate document, effective dates and an **expiry alert**. A 3PL is asked about this in every RFP because the client cannot legally hold stock at an undeclared premises | 3pl·india | v2 | P4 | `F-025` |
| **FR-302** | **Client profitability** joins metered revenue to labour minutes at a loaded rate and to storage snapshot × a space cost. It is the honest answer to "which clients are we losing money on" and it is only possible because the labour task and the snapshot exist | 3pl | v3 | P6 | `F-023` |
| **FR-303** | **One database per customer stands; a 3PL's clients are an owner dimension, not tenants.** `grep -ril "tenant" platform/backend/src/main/java` returns zero files, and the two concepts must never be conflated in a sales conversation. **⛔ OD-3** | 3pl | v2 | P5 | `OD-3` `D-5` |

### 6.18 India *owner: warehouse-india · hooks in base*

> `D-8` holds: no GST, HSN semantics, e-way bill or MRP rule is hardcoded in `warehouse-base` or
> `warehouse`, and the core carries only hooks. **`A-4` changed when the pack lands.** The earlier
> ladder put all of India in v2/P4 and this document followed it, flagging the section as the one to
> re-cut if that reading of `D-8` was wrong. It was. R3 and R5 both marked the delivery challan, the
> e-way bill and the GST-aware transfer document as **v1 BLOCKERs**, and in India goods physically
> cannot move between branches without them — so a v1 that ships transfers and no challan ships a
> feature an Indian customer may not legally use.
>
> **`warehouse-india` now lands in two waves.** **v1/P2-IN — the documents required to move goods
> legally**: delivery challan, e-way bill payload and generation, the GST-aware transfer document,
> HSN on the item, and the cross-GSTIN transfer treated as a supply. **v2/P4 — the statutory
> registers and filings**: the Rule 56 stock account, job work and ITC-04, MRP and Legal Metrology,
> bonded and MOOWR, and the regulated-goods packs.
>
> The column-versus-feature asymmetry still governs everything below and is still the whole argument:
> ship the schema without the feature and every row of stock is correct; ship the feature without the
> schema and the product looks compliant in a demo while every branch transfer ever recorded is wrong.

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-304** | `warehouse-india` is the **fifth module**, with its own package, band and prefix, and it lands in **two waves**. Putting India in `warehouse` makes the core unsellable outside India; putting it in a vertical adapter makes it invisible to a pharma customer; putting all of it in v2 makes the v1 transfer feature unusable in the market the product is being built for | india | v1·v1 | P0·P2-IN | `S-021` `D-1` `D-8` `D-12` |
| **FR-305** | A transfer between two branches under **different GSTINs is a deemed supply**: the two branch references and the taxable-supply flag are **derived at creation from the two registrations and frozen**, and the document kind is derived, never chosen by a user. It changes the document, the numbering, the valuation and the posting, none of which is a setting. **The columns are v1/P1 and the GST-aware transfer document is v1/P2-IN** | base·india | v1·v1 | P1·P2-IN | `E-050` `S-022` `T-083` `D-12` |
| **FR-306** | The transfer records its **valuation method and price** — cost, transfer price or open-market value — so the basis can be defended three years later | app·india | v1·v1 | P1·P2-IN | `E-050` `S-074` `D-12` |
| **FR-307** | The **delivery challan is a numbered document with its own per-branch series**, not a print template, covering branch transfer, job work, goods on approval, exhibition, repair and any other movement otherwise than by way of supply. Movements that need it have **no invoice** to hang attributes on, which is why it cannot borrow another document's block | india | v1·v1 | P1·P2-IN | `E-049` `S-023` `T-083` `D-12` |
| **FR-308** | **Transport details attach polymorphically** to a transfer, a challan or an issue and carry every field an e-way bill needs: dispatch-from and deliver-to blocks with pincode and state, transport mode, transporter party and registration, vehicle number and type, consignment-note number and date, and approximate distance. **All columns land in v1/P1**, optional at the core and made mandatory by a localisation rule; the generation path is v1/P2-IN. A compliance-reference store holds a number, not a vehicle | base·india | v1·v1 | P1·P2-IN | `E-051` `S-024` `G-077` `D-12` |
| **FR-309** | The **e-way bill lifecycle is implemented in v1, not just its number**: Part-A generated by the consignor, Part-B fillable later and required before movement, validity derived from distance, extension in transit, cancellation within the permitted window, a consolidated bill for multiple consignments in one vehicle, and the blocked-registration case. The prior product's implementation is transplanted and **its known null-Part-B defect is fixed rather than reproduced** | india | v1 | P2-IN | `S-024` `P-044` `D-12` |
| **FR-310** | The e-way bill adapter reads **only** the v1 columns plus the compliance store; it never reaches into an operational table for a field the schema did not reserve | india | v1 | P2-IN | `E-051` `G-077` |
| **FR-311** | The **inter-state stock-transfer invoice needs an invoice reference number** and routes through the same e-invoicing adapter as a sales invoice; a design that treats transfers as internal ships a legally invalid document. **The e-invoicing adapter itself is v2/P4**, which is the honest boundary of the v1 India wave: an install above the reporting threshold cannot ship the v1 transfer document without it, and this document says so rather than leaving it to be discovered at a go-live | india | v2 | P4 | `S-025` |
| **FR-312** | **Job work**: goods leave under a job-work challan to a location at the job worker's premises **with the owner unchanged**, carrying an expected return date; a scheduled job ages open challan lines against the statutory clock and raises the obligation before it becomes a deemed supply. The clock is measured from the challan date, so a movement recorded before the challan object exists can never acquire one | india·app | v1·v2 | P1·P4 | `E-054` `S-026` `F-061` |
| **FR-313** | **There is one challan table.** Warehouse's delivery challan *is* the challan; the accounting set's parallel job-work challan is reduced to a view over it or deleted. The rule lands with the challan in v1 so a second one is never built. **⛔ OD-1** | india | v1 | P2-IN | `E-054` `S-026` `OD-1` |
| **FR-314** | The **statutory stock account** is a shipped report, per registration and per period, in the mandated categories — opening, receipts, supplies, goods lost, stolen, destroyed, written off, disposed of by gift or free sample, closing — separately for raw material, finished goods, scrap and wastage, plus goods lying with a job worker. It is not a generic movement grid | india | v2 | P4 | `S-027` |
| **FR-315** | The **reason code is a tax classification**: it carries an ITC treatment and a statutory category, so the input-tax reversal on a write-off is computable and the six statutory categories are reportable. A year of free-text reasons cannot be reclassified, so that year's reversal cannot be computed | base·india | v1·v2 | P0·P4 | `S-028` `S-029` `E-033` |
| **FR-316** | An ITC-reversal amount needs the original credit, so **a write-off movement must be able to reach the receipt that brought the lot in** — which is the lot-to-layer linkage of `FR-234` | base·india | v2 | P4 | `S-029` |
| **FR-317** | **Scrap is inventory, and its sale is a supply** with its own classification code and a tax-collected-at-source flag — not shrinkage | india·app | v2 | P4 | `S-030` |
| **FR-318** | The tax classification code is **snapshotted on every movement and document line** so a reclassification does not rewrite a filed return | base | v1 | P0 | `S-031` `E-047` |
| **FR-319** | The statutory **unit-quantity code** is on the item and copied onto every line. The return carries the government's unit code, not our UoM name, and a line with no unit cannot be summarised | base | v1 | P1 | `E-047` `S-011` |
| **FR-320** | **MRP, net content, country of origin and pack month/year live on the lot**, with item-level defaults. MRP is a property of the pack run: two batches of one SKU legitimately carry different MRPs after a price revision and must be sold and reported separately. Adding it later leaves every historical lot with a null nobody can recover | base | v1 | P1 | `S-033` `E-016` |
| **FR-321** | **MRP becomes a balance dimension** for non-batch-tracked items too, with a stock-by-MRP report and MRP-inclusive back-calculation of the taxable value on the issue document | app·india | v2 | P4 | `E-016` |
| **FR-322** | **Goods sent on approval / sale or return** are a stock state at the customer that is still our asset, on a challan, with a deemed-supply clock — the same owner-and-location mechanism as consignment | app·india | v2 | P4 | `S-032` |
| **FR-323** | **Bonded and MOOWR warehousing**: the site is a licensed object with a validity; a warehousing bond carries a running utilisation balance; a per-bill-of-entry warehousing clock accrues where required; ex-bond clearance **consumes an identified bonded quantity**; inter-warehouse removal preserves duty status; and a monthly statutory statement is produced. All of it rests on `FR-104`'s v1 column | india | v2 | P4 | `S-044` `S-045` |
| **FR-324** | **Extended-producer-responsibility reporting** by category for batteries, e-waste, tyres and plastic packaging — pure reporting over quantities we already hold, and every automotive or electronics warehouse handles all four | india | v2 | P4 | `S-050` |
| **FR-325** | The **relational tax engine is carried forward with its known defects fixed as v1 blockers of the India pack**, not deferred: a deterministic discriminator so slab rules cannot all match simultaneously, non-overlapping effective-date ranges enforced by an exclusion constraint, seed guards that can actually fire, and a uniqueness rule on rule version. A tax engine with a nondeterministic resolver is worse than none, because it is confidently wrong | india | v2 | P4 | `P-043` |
| **FR-326** | The **compliance provider abstraction is transplanted** — provider, per-provider environment, credential specification, encrypted credentials, auth session, document, task queue — and it lands in **v1, because e-way bill generation depends on it**. **Two prior security findings are carried as constraints**: raw request and response bodies of compliance calls are never stored unencrypted, and no demo or test controller may trigger a real statutory filing. Schema-only statutory flows are either built properly or left out, because a schema-only compliance flow is a claim we cannot honour | india | v1 | P2-IN | `P-044` `D-12` |
| **FR-327** | Every statutory, expiry, manufacture and count date is a **`DATE` mapped to a date-only type with a date-only filter**, not a timestamp with a zone, so "expired today" cannot shift across a day boundary | base | v1 | P1 | `P-045` `C-042` |
| **FR-328** | **Stock as at a back date is computed from movements, never from balances.** Month-end snapshots exist for performance and are explicitly a cache. The section-44AB quantitative statement, the bank stock statement and the 31-March closing stock all ask "as at a date in the past, recomputed including entries made since" | app | v1 | P2 | `E-053` `S-083` |
| **FR-329** | **Two retention clocks run on the same rows** — the Companies Act's financial years and the GST period — with per-item shelf-life-based retention where the food rules require it, a legal-hold flag, and the tax-audit quantitative statement as a built report | india·base | v2 | P4 | `S-051` |

### 6.19 Events, the outbox and the logistics seam *owner: base*

> **Warehouse owns *how much of what, whose, in what condition, and where*. Logistics owns *which
> vehicle, on whose journey, at what freight cost*.** If a fact answers the first question it is a
> warehouse ledger fact even while the goods are moving; if it answers the second it is logistics even
> while the vehicle is parked. R4's dock-door rule remains exactly right for the physical handover;
> the ledger boundary is the movement port, and the port never moves.

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-330** | `warehouse-base` maintains an **outbox with a gapless monotonic cursor**, and **base does not know its consumers**. Consumers read by cursor, at-least-once, and deduplicate on (consumer, sequence). **There is no outbox anywhere in this repository today** — it is net-new infrastructure with no precedent to copy | base | v1 | P0 | `F-086` `G-045` |
| **FR-331** | **The event vocabulary is fixed in v1 and emits at billable granularity**: receipt line confirmed, putaway task completed, pick line confirmed, carton packed, shipment confirmed, task completed, stock movement posted and reversed, count variance posted, return line dispositioned, work order completed, owner changed. **Adding an event code later is cheap; adding a dimension to an existing code is not** — which is why owner, lot, LPN, warehouse and the three timestamps are on every event from day one even where v1 has no consumer for them. A design that emits only "order shipped" makes per-line handling billing — how every audited 3PL prices — permanently unavailable for the past | base | v1 | P0 | `F-012` `T-071` |
| **FR-332** | The outbox budget is stated honestly: the table, the cursor, a publisher job, retry with backoff, a **dead-letter grid** and a replay-from-cursor endpoint. Estimating it as "a table" will be wrong, and an async annotation is not sufficient | base | v1 | P0 | `G-045` |
| **FR-333** | **Outbox subscriptions are a table in v1**, carrying a subscriber code, an in-process or HTTP target, an endpoint, a secret reference, an event filter and a per-subscriber cursor; only the in-process path is implemented in v1 and HTTP delivery lands in v1.1. A future logistics module **may be a separate deployable** and an in-process bean list cannot reach one; adding the subscription table after three in-process subscribers exist means redesigning all three | base | v1·v1.1 | P0·P3 | `G-046` `F-086` |
| **FR-334** | The event stream is **the adapters' subscription point** and the automation vendor's integration surface; no consumer is registered in base | base | v1.1 | P3 | `T-059` `G-046` |
| **FR-335** | **In-transit stock is countable, adjustable, ageable and attributable**, because a transfer posts two movements through an in-transit location rather than one movement that teleports. A transit loss is then a normal reason-coded adjustment against the transit location — which is what makes it claimable against a carrier and stops it becoming a mysterious shrinkage at the destination. A partial arrival is representable: twelve of fifteen cartons arrive, three stay in transit and age | base·app | v1 | P2 | `F-089` `G-071` `S-069` |
| **FR-336** | **The seam's acceptance criterion is two deletion tests.** Delete the logistics module: warehouse still works (locations remain, external references resolve to null and the display resolver falls back). Delete the warehouse module: logistics still works (its vehicles have no foreign key into ours). Any design where either answer is no has a foreign key pointing the wrong way | base | v1 | P0 | `G-021` `G-025` |
| **FR-337** | **Transport equipment, tyres, depot bulk fuel and fleet spare parts are warehouse stock with warehouse item types**, not private ledgers inside a transport module. Serialised tarpaulins with a condition, a tyre lifecycle from in-stock to fitted to retread to scrapped, diesel in a tank we own and a spare consumed by a maintenance work order all have a quantity and a condition, and every one of them was reinvented as a private table in the transport prior art | base | v1 | P1 | `G-002` `G-003` `G-004` `G-005` |
| **FR-338** | A tyre fitted to an axle and a tarpaulin issued to a trip are **fitments and reservations against warehouse stock**, posted through the port as issue-to-asset, return-from-asset, equipment-issue and equipment-return; the fitment record itself belongs to logistics | base·app | v2 | P5 | `G-003` `G-002` |
| **FR-339** | **The vehicle has two identities and neither is the other's master**: a location row so stock can sit on it, be counted on it and be short-picked from it, and a logistics asset row so it can have a registration, an insurance expiry, a tyre and an odometer. They are joined by the location external-reference table, never by a foreign key | base | v1 | P1 | `G-017` `G-010` |
| **FR-340** | **The gate belongs to neither module.** A gate event answers neither *how much of what* nor *which journey* — it answers which vehicle crossed a line at what time, and both modules want it. It is published to a handler list, exactly as the existing boom-barrier webhook does; warehouse claims it to stamp a dock appointment and logistics claims it to stamp a trip departure | app | v2 | P5 | `G-016` |
| **FR-341** | **A trailer parked in the yard holding stock is a warehouse location**, or that stock is off the books while it sits there. Yard slot management is logistics; a yard slot holding a stock-bearing trailer is not. And **the weighbridge measures the stock, not the yard** — its tare, gross and net readings belong to the receipt | base·app | v1·v2 | P1·P5 | `G-011` `G-012` |
| **FR-342** | **"Delivery is not a movement" is true for a customer and false for our own branch.** Delivery to a customer posts nothing, because the stock left at despatch. Delivery to our own branch posts an arrival, and a partial arrival is fewer lines. Delivery to a 3PL client's site is an owner change or an arrival depending on the contract. An implementer who reads only the first rule builds inter-branch transfers that never arrive | app | v1 | P2 | `G-019` |
| **FR-343** | **Returnable packaging carries a per-counterparty balance** — pallets, crates, cylinders and totes exchanged at a stop are assets with a deposit and a balance per party, and nobody currently has one | base·app | v2 | P5 | `G-024` `F-060` |
| **FR-344** | `ownership_transfer_point` sits on the purchase and transfer document **as a v1 column**. The in-transit location says *where*, the owner says *whose*, and neither says *when title passed*; under the applicable Incoterm the goods may be ours from the moment they leave the supplier's dock, and without the column a period-end goods-in-transit figure is a guess | app | v1·v2 | P1·P5 | `G-018` `S-073` |
| **FR-345** | **Freight capitalisation crosses the seam as a value-only movement.** The freight charge is a transport document; its effect on stock cost is a zero-quantity `LANDED_COST_APPLY`. **No prior-art transport document in this monorepo connects freight to inventory value at all**, which is exactly why the hook must exist before the logistics module does | base | v1·v2 | P2·P5 | `G-023` `F-088` |
| **FR-346** | The **logistics band `V524000–V524999`, the `log_` prefix and the `logistics:*` permission namespace are reserved in v1**, with the migration ordering rule recorded. A logistics user who dispatches a trip posts a stock movement; if that permission is invented in v2, every existing role must be re-granted by hand | base·platform | v1 | P0 | `G-069` `G-068` `D-2` |
| **FR-347** | Before a logistics module is built, the **four transport-shaped surfaces already in this monorepo are enumerated in its pre-flight**: field-service trips with polylines and track points, the services doorstep pickup and drop ladder, the automotive gate-event webhook, and dealer PDI vehicle movements. A logistics trip model would be the **third GPS trip model** in the repository, and that must be said before it is built, not after | platform | v3 | P6 | `G-020` `G-084` |
| **FR-348** | Driver and vehicle masters in a future logistics module **overlap platform HR and two verticals' vehicle masters**, and the overlap is named rather than discovered. The cost of module independence — up to seven party-shaped masters and three vehicle-shaped ones — is stated in this document | platform | v3 | P6 | `G-085` `G-029` |

### 6.20 Adapters and the module contract *owner: all*

> An adapter is a module that translates one vertical's documents into warehouse movements and back,
> owns only its own tables, and **can be added or deleted without a single line changing in
> `warehouse-base`**. The generality question is decided by the *first* adapter, and the second copies
> the first — which is why the contract is written before the first adapter, and why the first adapter
> is a fixture we control.

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-349** | **An adapter MAY**: post movements through the port and its batch and reverse variants; simulate before promising; find its own postings by lineage; read balances and availability through an API, never a table; hold and release a reservation with a holder quad and a TTL; register its own movement types, document types, reason-code contexts, stock statuses, location types, task types and item types by its own migration; register its source-system id; map its own identifiers through the three external-reference tables; register a document display resolver; subscribe to stock events; own tables under its own prefix; register permissions, menus, grids and filters; and take a gapless document number from the module-scoped series | adapter | v1 | P0 | `G-039` `T-079` `E-006` |
| **FR-350** | **An adapter MUST NOT**: write to any base or app table; add a column to a base table; create a foreign key from a base table to an adapter table; be imported by base; change stock outside the port; define a second envelope shape or a second idempotency scheme; reuse another adapter's source-system code; put a `CHECK` on a registry column; read or write the accessories stock tables; or ship a screen that duplicates a base grid | adapter | v1 | P0 | `G-039` `T-079` `E-087` |
| **FR-351** | The adapter package is a **sibling** — `ai.warehouseadapter<vertical>`, never `ai.warehouse.adapter.*` — because a component scan on the parent package would load the adapter unconditionally in every install, including ones where the vertical is not built. This is the exact trap the accounting round-4 review found and corrected | adapter | v1 | P0 | `D-1` `C-005` |
| **FR-352** | **Two adapters ship in v1**, not one, because one adapter proves nothing about genericity. The port is accepted only if neither required a base-schema change the other did not want | adapter | v1 | P2 | `E-006` `D-11` `T-079` |
| **FR-353** | A **reference adapter fixture** ships in the repository and CI builds it: zero screens, one movement type, one document type, one item cross-reference, one reservation, one subscriber, and an integration test that posts, reserves, consumes, reverses and reads back **using only the public API**. If the fixture compiles the contract is expressible; if a real adapter needs something the fixture cannot express, that is a base gap found before base ships | adapter | v1 | P0 | `G-049` `T-079` |
| **FR-354** | A **coupling test in `warehouse-base`** asserts six things: no forbidden import of any app, adapter, 3PL, India, logistics or vertical package; no base-band migration referencing another module's prefix in a `REFERENCES` clause; every base-band foreign key targeting a base table or an asserted platform whitelist; **no `CHECK (… IN (…))` on any of the thirteen registry columns**; a self-test that the scanners are not passing vacuously; and the reserved accessories source-system row | base | v1 | P0 | `G-039` `C-041` `P-055` |
| **FR-355** | **The loose-coupling ratchet is "zero commits to `warehouse-base`", never "zero commits to `platform`".** The filter allowlist is a TypeScript constant and the cache registry is platform Java; every new grid edits both. A contract that claims otherwise is false on day one and, being false, gets ignored — taking the true invariants with it (`D-10`) | base | v1 | P0 | `G-047` `D-10` |
| **FR-356** | Adapters **register reference data by migration, in their own Flyway sub-band**, idempotently, because any Flyway failure in this codebase triggers a blind repair and one retry | adapter | v1 | P0 | `G-043` `C-047` `D-2` |
| **FR-357** | Document display resolvers are a **bean-collection registry**, not a primary-bean override, and **base ships a fallback** that renders the document type and id so an unresolved reference is ugly rather than blank. A base-only install may legitimately have none on the classpath | base | v1 | P0 | `G-041` `E-004` `C-039` |
| **FR-358** | **`warehouse-adapter-dealer` (spare parts) ships in v1**: counter sale, workshop parts request, OEM order and core return, registering its own movement types and owning its own tables | adapter | v1 | P2 | `E-006` `T-021` `C-034` |
| **FR-359** | **Counter sale is keyboard-first**: scan or part number, quantity, price level, print, next — a sub-ten-second bill, with trade price levels and a cash ticket. The bar is set by the Indian retail incumbents, not by an ERP | app·adapter | v1 | P2 | `E-065` `S-063` |
| **FR-360** | **`warehouse-adapter-services` ships in v1** and is the largest consumer: a material request against a job card → reservation before it is an order → issue in parts as the job progresses → **return to store of unused parts crediting the job** → the warranty split. The `services` module has no parts table of any kind today, so this is a clean sheet, and without the return path the job is over-costed, the stock is short and the variance appears three months later as shrinkage | adapter | v1 | P2 | `E-065` `T-081` `S-061` `C-034` |
| **FR-361** | **Parts issued to open jobs are neither stock nor cost of sale** and are reported as work-in-progress at every month end | adapter·app | v1 | P2 | `E-065` |
| **FR-362** | A serialised part fitted to a customer's vehicle **records the vehicle it was fitted to at issue time**, because retro-linking a year of parts issues to vehicle identifiers is impossible and a vehicle-linked recall depends on it | adapter | v1 | P2 | `S-048` |
| **FR-363** | **`warehouse-adapter-field-service` ships in v1.1**: the van is a mobile location owned by a technician, replenished by a transfer, consumed at job close, cycle-counted, and its unreturned parts age. The trip model already knows where the van is | adapter | v1.1 | P3 | `T-080` `S-060` `C-034` |
| **FR-364** | **`warehouse-adapter-assets` ships in v1.1**, issuing spares against a complaint resolution, and **the boundary is stated**: warehouse owns the item until issue, the assets module owns it after capitalisation, and the hand-off is an event carrying the serial. The existing asset purchase receipt receives *assets*, not stock, and is a model to extend rather than reuse | adapter | v1.1 | P3 | `T-087` `C-034` |
| **FR-365** | **The dealer vehicle inventory is not migrated in v1 or v2.** The test for whether it ever should be is stated rather than the answer: *can the serial entity carry a chassis number, a colour, a variant and a pre-delivery-inspection status without `warehouse-base` learning what a vehicle is?* If the answer needs a base column, the answer is no. **⛔ OD-2** | adapter | v3 | P6 | `G-050` `OD-2` |
| **FR-366** | **A future logistics module posts directly through the port and gets no adapter.** An adapter exists to translate a vertical that does not know about warehouse; logistics is a first-class module of our own that can be built knowing the port, and an adapter between two of our own modules is a layer with no translation in it | — | v3 | P6 | `G-048` |
| **FR-367** | **`accessories` is never an adapter.** Its source-system code is **reserved and unclaimable** with a comment naming the decision, its package is on the forbidden-import list by decision rather than by the general rule, and **no adapter may read or write its stock tables** — the separation is worthless if a helpful adapter tunnels under it (`D-9`) | base | v1 | P0 | `D-9` `G-052` `E-087` |
| **FR-368** | The item external-reference table carries an **accessories row for every dual-stocked SKU**, so double-counting the same physical unit in two systems is at least *detectable*. Without it, it is not merely unmitigated but undetectable (`D-9`) | base | v1 | P1 | `D-9` `E-083` |
| **FR-369** | A **category-ownership rule is recorded as data**: for any item category, exactly one of the two inventory systems is the stocking system of record, and a scheduled **reconciliation report names every violation** — every part number present in both with stock in both. It is a detective control, not a preventive one, and a named detective control beats an unnamed hole (`D-9`) | app | v1 | P2 | `D-9` `E-086` |
| **FR-370** | The **counted cost of the accessories separation is carried in this document and surfaced in the product**: 17 duplicated tables, 71 backend files, 11 reports, 33 mobile screens, 25+ filter scopes and 12 permission resources, a second item master, a second UoM vocabulary, a second warehouse master — and no query that can answer "how much of part X do we hold" across both. Where a screen could mislead a user into thinking it shows group-wide stock, it says plainly that these two inventories are separate | app | v1 | P2 | `C-032` `G-051` `D-9` |
| **FR-371** | **Standalone is the reference configuration.** No v1 capability may require dealer, automotive, accounting or any other vertical to be installed, which is what makes the zero-vertical-dependency claim testable rather than aspirational (`D-7`) | base·app | v1 | P0 | `D-7` |
| **FR-372** | Controllers live under `ai.<module>.controller` or the platform's activity-tracking aspect cannot see them, and the recorded module names are a consequence of the package layout, not a style preference. Every warehouse frontend filename is globally unique and prefixed, because the frontend build merges module source trees last-write-wins | base·app | v1 | P0 | `C-049` `C-012` |
| **FR-373** | The **new-module integration list is 16 files and ~40 edits across two build systems, plus one runtime gate that fails silently** — the module import selector, without an entry in which the JAR ships and loads nothing. The list is executed in the bootstrap task and nothing is assumed to be optional without saying so | base·platform | v1 | P0 | `C-005` `C-006` `C-011` `T-096` `P-059` |
| **FR-374** | **Migrations are forward-only and additive; a released migration is never edited in place**, and every migration is individually idempotent. Fourteen prior-art documents instruct the opposite and attribute the rule to a standard that does not contain it; the house style is provably the reverse, and a checksum break caused by an in-place edit does not fail loudly because any Flyway failure triggers a blind repair and one retry. The bands are fixed by `D-2`; a warehouse-first install that later adds a lower-banded vertical **requires out-of-order migration and the upgrade guide says so** | all | v1 | P0 | `P-001` `P-002` `C-001` `C-002` `C-003` `C-046` `C-047` `D-2` |

### 6.21 Open registries and extensible vocabularies *owner: base*

> The precedent that works is live and self-documenting: an accounting reason-code context carries no
> `CHECK` **deliberately**, because *it is a catalogue, not an enum*. The counter-example is equally
> live: a platform module constraint has been widened by drop-and-add **three times** and still admits
> neither `warehouse` nor `logistics`. The prior warehouse product broke on exactly this — location
> and zone type constraints dropped and recreated with completely different value sets 36 versions
> after creation.

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-375** | **Thirteen vocabularies are catalogue tables with no `CHECK` constraint, no Java enum and no re-closing TypeScript union**: movement type, document/reference type, source system, stock status, location type, reason code and reason context, UoM class and UoM, task type, owner type, item type, counterparty role, disposition, and attribute key. Accounting's base found six; a warehouse has more axes than a ledger, and every one of the thirteen is a place a future consumer must extend without a core release (`D-10`) | base | v1 | P0 | `G-053` `T-004` `T-015` `F-087` `D-10` |
| **FR-376** | Every registry has the **same shape**: code, name, `owning_module` as an **opaque string and not a foreign key**, `is_system` marking undeletable rows, a sort order, typed behaviour columns that describe how the row behaves, and the standard audit set | base | v1 | P0 | `G-053` `D-10` |
| **FR-377** | Where a **platform `CHECK` must be widened anyway**, the migration reads the existing constraint definition, unions the new value and rebuilds — never a hardcoded drop-and-add, which silently discards another module's value | base·platform | v1 | P0 | `C-014` `C-015` `G-053` |
| **FR-378** | The platform's **widget module constraint must admit `warehouse` before the first warehouse widget**, or the first insert fails at runtime | base·platform | v1 | P0 | `C-014` `P-016` |
| **FR-379** | The platform's **global-settings module constraint already admits `WAREHOUSE`** and is used free; a defensive merge migration ships anyway, in case a later module's hardcoded rebuild omits it | base·platform | v1 | P0 | `C-015` |
| **FR-380** | **No TypeScript string-union type may enumerate a registry vocabulary.** Catalogue-backed dropdowns fetch their values; string unions are permitted only for genuinely closed system vocabularies such as a posting status. This knowingly diverges from the platform's own typing rule, which is right for fixed sets and wrong for a catalogue. **⛔ OD-5** — referred to the standards owner with this recommendation attached | app | v1 | P0 | `G-064` `OD-5` |
| **FR-381** | A status badge's **variant comes from a column on the registry row**, and i18n **falls back to the registry row's name** when a translation key misses, so a newly registered status renders in English rather than as a raw key. One less place to forget | app | v1 | P1 | `G-065` |
| **FR-382** | Every registry gets a **mobile-vocabulary consideration on day one**, because the mobile schema file is a third copy of every dropdown vocabulary and a missing value makes the mobile save fail validation silently | mobile | v1.1 | P3 | `G-066` `E-072` |
| **FR-383** | **No JSONB on any new warehouse business table.** Grid-preference columns are the only permitted use, and every warehouse grid migration must emit them. The prior design made JSONB a convention and used it on eleven business tables; each of those is normalised into a child or attribute table here | base·app | v1 | P0 | `T-013` `P-007` `C-036` |

### 6.22 Reports, KPIs and analytics *owner: app*

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-384** | **Stock on hand by every dimension** — item, location, lot, serial, LPN, status, owner, duty status — with a by-location tab and a by-item tab, following the two-tab pattern a shipped module already cites | app | v1 | P2 | `T-003` `P-014` |
| **FR-385** | The **stock movement register** is report number one: filterable by item, warehouse, location, lot, serial, movement type, reason, source module and date range, in opening → in → out → closing shape per item, drilling to the movement and from the movement to the source document through the display resolver. It is the report auditors and storemen both live in | app | v1 | P2 | `E-075` |
| **FR-386** | The **godown-wise stock statement** — godown × item group × item, opening, inward, outward, closing, value — with branch and period filters. A grid with a warehouse dropdown is not this report; the opening/inward/outward/closing shape is the whole point, and a bank asks for it monthly against a cash-credit limit | app | v1 | P2 | `E-052` |
| **FR-387** | **Stock valuation with an as-at date**, computed from the ledger, reproducing the same answer for the same date next year | app | v1 | P2 | `E-053` `T-019` |
| **FR-388** | **Stock ageing** with buckets measured from the last outward movement, with value per bucket and a warehouse split | app | v1 | P2 | `E-076` |
| **FR-389** | The **adjustment register** by reason code, by user and by value — every quantity that entered or left without a commercial document. This is the fraud report and it is the one an internal auditor asks for first | app | v1 | P2 | `S-083` |
| **FR-390** | The **count history and variance register**, by counter, including recounts, with the variance value | app | v1 | P2 | `S-083` `S-091` |
| **FR-391** | **Low stock, insufficient stock and replenishment suggestions** as shipped reports rather than grid filters | app | v1 | P2 | `C-045` `E-040` |
| **FR-392** | **Operational KPIs computed from the lifecycle timestamps**: dock-to-stock, order cycle time, on-time ship, inventory record accuracy from counts, dwell time and putaway cycle time. Not one of them can be computed from a status column and an updated-at, because updated-at is overwritten by the next status change, and the first time they are asked for — month two of the first client — the answer has to cover month one | app | v1 | P2 | `F-074` `P-058` |
| **FR-393** | **The four parts KPIs carry frozen definitions rendered in the metric explainer**: fill rate as filled demand hits ÷ (filled + no-stock lost-sale hits); inventory turns as annualised issue value at cost ÷ average inventory value, with a true-turns variant excluding non-stocked and special-order lines; obsolescence as the value with no outward movement in twelve months ÷ total inventory value; and days supply as on-hand ÷ average daily demand over the policy window. Each has three plausible definitions and a KPI a manager cannot reproduce by hand is a KPI they will not trust | app | v1 | P2 | `E-077` |
| **FR-394** | The **twenty-nine-metric warehouse KPI list is computed from the ledger**, and a pre-aggregated snapshot table is added only for what is provably too slow, only after measuring. The repo's own best precedent is a derived-at-read-time model that deliberately does not cache | app | v1 | P2 | `P-058` `C-033` |
| **FR-395** | **Filter-aware statistics strips carry no cache name.** The platform's cache registry records that exact mistake with its issue numbers: those names cached nothing while reading as though they did. Most warehouse strips are filter-aware | app | v1 | P2 | `C-043` `G-047` |
| **FR-396** | **Forward and backward traceability**: lot → every shipment and consignee that received it, and shipment or serial → supplier lot and receipt, for the full retention period (`L-12`) | app | v1 | P2 | `F-065` `F-066` `S-040` |
| **FR-397** | A **consolidated valuation view spanning both inventories**, tagged by source system, with the differing-valuation-method caveat **rendered on the report itself** rather than in a footnote nobody reads. Ugly, honest, and the only way a finance director gets one number without a merge | app | v1.1 | P3 | `E-084` `D-9` |
| **FR-398** | **Per-install health signals**: movements posted today against a baseline, handovers stuck pending, counts overdue, negative positions, orphaned reservations and unreconciled positions — all already-modelled data with no watcher today | app | v1.1 | P3 | `S-093` |
| **FR-399** | A **real-time operations dashboard** on the platform's widget framework, once the module constraint admits warehouse | app | v3 | P6 | `C-014` `P-058` |
| **FR-400** | **Export follows the visible columns and is a superset of them**, carrying created-by and updated-by wherever the grid shows them, and a 100,000-row export does not hold a transaction open | app | v1 | P2 | `C-036` `S-084` |

### 6.23 Permissions and access control *owner: all*

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-401** | **`@PreAuthorize` on every controller method**, in `resource:action` form, and the permission resources are prefixed for this product and **never named after the deleted prior module** — a live platform migration excludes that prefix pattern from a bulk role grant, and a new resource inheriting the name would inherit a decision nobody took | all | v1 | P0 | `P-014` `D-3` |
| **FR-402** | Permission dependency rows are **inserted, never the table created**. It is a platform table and the defensive re-creation in another module is a documented false premise | base·app | v1 | P0 | `C-017` `P-014` |
| **FR-403** | The prior module's **auditor and branch-admin exclusions are not inherited**. Both migrations are one-shot and have already run, so the recorded product decisions — "the auditor cannot see warehouse", "branch admin must not hold warehouse view-all" — grant a new module nothing and are simply absent. They are **re-taken explicitly** in this product's permission chapter, and if reversed, the warehouse migration grants the rows itself | base·app | v1 | P0 | `P-014` |
| **FR-404** | The **three-mode view pattern** — view-all, view-branch, no view — is implemented by every management query as a **record-level guard in the `WHERE` clause**, not as a UI filter. A branch admin holds the branch tier only | app | v1 | P0 | `P-014` `E-046` |
| **FR-405** | **Warehouse-scoped user access** participates in every management query's predicate. A storekeeper at branch A must not adjust branch B's stock, and a menu filter is not a guard | base·app | v1 | P1 | `E-046` |
| **FR-406** | **Owner grants are enforced by a single server-side resolver** and a contract test fails the build if a repository method touching an owner-scoped table takes no owner-set parameter. Each grid identifier has an export path and a statistics map, and every one of them is a leak site | base | v1 | P0 | `F-004` |
| **FR-407** | The **`logistics:*` permission namespace and its dependency rows are reserved in v1**, because retro-granting a permission invented in v2 to every existing role is hand work | base·platform | v1 | P0 | `G-068` |
| **FR-408** | **Approval permissions are distinct from execution permissions**, and the approver may not be the actor — the counter may not approve their own count, the adjuster may not approve their own write-off | app | v1 | P2 | `T-090` `E-034` |
| **FR-409** | **Support impersonation exists, with consent, time-boxed and audited**, and the schema half — an on-behalf-of actor on the audit event — lands in the **first** audit migration. Support sessions recorded before the column exists are indistinguishable from the customer's own actions, which voids the audit claim retrospectively for that period. There is no impersonation capability anywhere in this platform today | platform | v1·v1.1 | P0·P3 | `S-092` |
| **FR-410** | **Menu inserts are guarded by an existence check**, not by conflict handling, because the menu table has no unique constraint on the natural key and a Flyway retry duplicates the row; and every menu seeds translations for all three shipped locales | app | v1 | P0 | `C-036` `C-050` |

### 6.24 Import, go-live and data migration *owner: app*

> This is the single most common reason an implementation fails, and there is no way to onboard
> customer number one without loading their stock, with value, from an incumbent that exports a
> godown-level closing quantity and nothing else.

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-411** | **Opening stock is a first-class feature, not an import script.** It carries quantity **and cost and layers and lot and expiry and MRP and serial and bin and owner and duty status**, stages into a batch with a status ladder, validates, runs dry, reports errors per row, applies, and is **re-runnable after a failed attempt**. It posts opening-balance movements so the ledger starts balanced and the first issue has a cost. Design for 200,000 to 1,000,000 position rows | app | v1 | P2 | `E-088` `S-079` `T-069` |
| **FR-412** | Go-live produces a **closing-value tie-out against the source and a reconciliation certificate**. That certificate is what makes the customer sign off the number | app | v1 | P2 | `S-079` `E-088` |
| **FR-413** | A **cut-over checklist screen** — masters loaded, mappings resolved, opening posted, value matched, period opened — and a documented freeze-count-load-verify runbook with a **stock freeze window** as an object. The count that establishes opening stock happens on a Sunday and go-live is Monday; anything that moves between is manual | app | v1 | P2 | `S-081` `E-088` |
| **FR-414** | **Migration mapping profiles** for the incumbent products — item master with classification, UoM and alternate units, godowns, parties, opening stock with batch and expiry, and the supersession list — with duplicate-SKU resolution, unit-conversion validation, and a profile that is **exportable and importable**, because one database per customer means the second customer is a different database | app | v1.1 | P3 | `S-080` `E-089` |
| **FR-415** | **Twelve months of demand history is importable**, marked as migrated, because without it the computed stocking level takes a year to become useful and the first year's fill rate has no denominator | app | v1.1 | P3 | `E-089` `E-066` |
| **FR-416** | The import framework is the **handler-registry shape** — batches, rows, a typed handler per import kind and **a reversal path** — not the bespoke importer shape. An opening-stock import that cannot be reversed is a ledger you cannot correct | base | v1 | P1 | `C-020` `P-041` |
| **FR-417** | A **validate endpoint honours dry-run and persists nothing.** This codebase has met the opposite defect — a validate endpoint that persisted, producing duplicate rows on the subsequent real import — and the obligation is on the backend handler, not on the frontend flag | base | v1 | P1 | `P-041` |
| **FR-418** | **Bulk import covers** items, identifiers and barcodes, packaging, locations, opening stock, ASN lines, supersessions, vehicle applications and price files, on the platform's existing six-stage wizard with a per-cell error preview and an admin-configurable row cap | app | v1 | P1 | `C-020` `E-059` `P-041` |
| **FR-419** | An **OEM price file loads with a dry-run diff before apply**, writing item and price rows, supersessions and — where the direction warrants it — a revaluation movement for the on-hand quantity and a price-protection claim. Loading thirty thousand part numbers by hand is untenable | app | v1.1·v2 | P3·P5 | `E-068` |
| **FR-420** | An **OEM order interface** transmits the order and consumes the acknowledgement — allocated and back-ordered quantities and an ETA per line — then matches the receipt against the OEM invoice file and raises typed discrepancies feeding the claim register. Format-pluggable per OEM; no single OEM's layout is hard-coded | adapter | v1.1 | P3 | `E-062` |
| **FR-421** | If the accessories inventory is ever absorbed, the path is stated in advance: **import current balances as opening-balance movements at a cut-over date, archive the old transaction table read-only, and do not attempt to replay history** — because historical owner, status and lot can only be synthesised as defaults, which is itself an argument for migrating early rather than late. The same applies to any other vertical that later acquires stock (`D-9`) | app | v3 | P6 | `T-086` `D-9` |

### 6.25 Non-functional *owner: all*

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-422** | **Performance targets are stated so the design can be tested against something**: one million ledger rows a day at peak for a large third-party site and twenty thousand for a dealer parts department; a position table at or below five million live rows, with the unique key understood as the hot spot; scan-to-response under 300 ms at the handheld; allocation at 200 order lines a second with no oversell; a five-thousand-line count entered by ten counters concurrently; a five-hundred-line wave generated in under five seconds; and a hundred-thousand-row export that does not hold a transaction open. None of these was stated anywhere in the prior art | all | v1 | P0 | `S-084` |
| **FR-423** | The **partition and archive strategy is stated at design time**, not after, and it does not break as-at reproduction or either retention clock | base | v1 | P0 | `T-095` `S-096` `S-051` |
| **FR-424** | **Scan-to-response under 300 ms** at the handheld, or the operator stops trusting the system and works ahead of it | mobile·app | v1.1 | P3 | `S-084` |
| **FR-425** | Task and waybill claiming uses **`FOR UPDATE SKIP LOCKED`**, which has **zero precedent in this codebase** and is flagged as new work rather than assumed | base·app | v1.1 | P3 | `C-040` `F-042` |
| **FR-426** | **Gapless document numbering** from a locked counter row, module-scoped so a future consumer need not build a second generator. GRN, pick, ship, adjustment, QC, challan and gate-pass numbers must be gapless — a missing GRN number is an audit question. The platform's existing code generator is scan-based, explicitly not gapless and racy | base | v1 | P1 | `C-019` `P-046` `G-044` |
| **FR-427** | **The ledger is the audit trail.** The platform's activity log is asynchronous, out of transaction and swallows its own exceptions; for a stock ledger that is telemetry, not a record. The five artefacts an auditor asks for are shipped: the ledger as at a date and reproducible, a movement-level audit export for a period, the adjustment analysis, the count history with variance, and immutability evidence | base·app | v1 | P0 | `S-083` `C-049` |
| **FR-428** | Warehouse owns **its own activity-history view** and does not join or redefine the dealer-owned cross-module view, because doing so would make warehouse depend on dealer. Another vertical already declined it for the same reason | base | v1 | P1 | `C-048` |
| **FR-429** | **Restore exists.** The platform backup service has no restore path at all, no write-ahead archiving, no point-in-time recovery, no restore-verification job and no stated recovery objectives. For a statutory stock ledger that is a records risk, not an availability risk. **This is platform work and does not compete with warehouse engineers** | platform | v1 | P0 | `S-082` |
| **FR-430** | **Degraded-mode operation is designed**: a documented paper fallback and a **catch-up entry mode** that accepts backdated movements carrying the true event time. It is possible only because `FR-007` separates the business time from the record time | app·mobile | v1.1 | P3 | `S-098` |
| **FR-431** | **Three locales ship on every warehouse translation file**, following the newest module rather than the older ones, and menu translations are seeded for all three. The RF screens are where regional languages actually matter and where icons beat words; **right-to-left support is absent platform-wide and silently rules out one market**, which is stated rather than discovered | app·mobile | v1 | P1 | `C-050` `S-095` |
| **FR-432** | **Every warehouse grid registers its filter scope in the platform allowlist and its cache names in the platform cache registry**, and expiry, count and manufacture dates use the date-only filter type because the timestamp type moves the lower bound back a day east of UTC. A field absent from the allowlist is silently dropped before the API call, and this will be the largest single addition to that allowlist the codebase has seen | app·platform | v1 | P1 | `T-097` `C-042` `C-043` |
| **FR-433** | **Every grid migration writes column definitions, filter definitions and both the default columns and the default filters** on the grid-preference row. Setting a filter definition visible alone does not build the default strip. The filter table's real name is used; the name six prior-art documents use does not exist and would crash Flyway | app | v1 | P1 | `C-036` `P-006` `P-055` |
| **FR-434** | The **nineteen named failure modes from auditing two real modules built against these same conventions become the warehouse architecture ratchet and the screen obligations** — orphaned grid configuration, a column bound to a field the response does not carry, a hardcoded constraint alongside a catalogue, a nullable column an entity declares non-null, an operator-precedence bug in a guard clause, a migration that deletes users' grid customisation, a conflict guard that can never fire, foreign-key-less identifier columns, unbounded log tables, JSON smuggled in a text column, an unregistered i18n namespace, an API service calling a path no controller exposes, a fully built backend with no reachable UI, and a demo controller that can trigger a real statutory filing | all | v1 | P0 | `P-055` `C-041` |
| **FR-435** | The **seven-layer definition of done** governs every warehouse task: database column or seed, service method, endpoint with its authorisation, frontend API method, UI control rendered and permission-gated and status-gated on a **menu-reachable** page, an **access path clickable from a top-level menu**, and a **runtime effect observable after rebuild**. A tick requires all seven; there is no aggregate "all done". The mobile counterpart is the eighth where the change is user-facing (`D-13`) | all | v1 | P0 | `P-023` `D-13` |
| **FR-436** | **A single writer service is the only path that touches the ledger and the position cache**, and an architecture test asserts it. The gateway alone is a convention; the test is what makes it survive contact with the next feature, and it pairs with the database-level rejection so the invariant is defended at two layers | base | v1 | P0 | `P-022` `T-017` `C-025` |
| **FR-437** | The concurrency mechanisms are **named and their precedents cited**: advisory locks for serialising movements on a key with no row to lock, a pessimistic-locked counter row for gapless numbering, a deferrable constraint trigger for balance-at-commit, optimistic versioning on the position, and skip-locked claiming for tasks. Four of the five have exactly one precedent each in this repository and the fifth has none | base | v1 | P0 | `C-037` `C-038` `C-039` `C-040` |
| **FR-438** | **Native-query timestamp mapping handles all four types a driver may return** and logs a warning on an unknown one. Returning null for an unhandled type is silent data loss — cells render blank while the database holds data | base·app | v1 | P1 | `C-036` |
| **FR-439** | **Multi-timezone**: each site posts in its own local day, with the site's timezone stored and used for local-day bucketing, because "the 30th" is a different 24 hours at each site | base | v1 | P0 | `T-018` `S-007` |
| **FR-440** | **Multi-tenant SaaS is not built.** The platform is single-tenant per install by existing decision, and the owner dimension gives multi-*client* separation inside one install — which is what a third-party operator needs and is **not the same thing**. High availability, on-premise and private deployment are inherited from the platform and stated. **⛔ OD-3** | all | v1 | P0 | `OD-3` `D-5` |
| **FR-441** | **Retention beats erasure**, satisfied by pseudonymising the person and never the quantity. Stated once so the precedence question is not re-litigated per screen | base | v2 | P4 | `S-055` |
| **FR-442** | **A sandbox or practice warehouse with disposable data**, and in-product help content per screen on the platform's existing help affordance. For a warehouse this is not a nicety — **you cannot train pickers on live stock** | app | v1.1 | P3 | `S-094` |

---

### 6.26 Amendments — requirements added after the first authoring wave

**These four continue the range at `FR-443` rather than being inserted where they belong
thematically, because `DECISIONS.md` §7.4 forbids renumbering a published id.** `FR-443`–`FR-445`
belong with §6.3 and are cross-referenced from it; `FR-446` belongs with §6.13 and is
cross-referenced from there. They exist because `DECISIONS.md` §5.1 amendments `A-3` and `D-6`'s
rewrite landed after the catalogue was written.

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-443** | **The style-and-variant model is v1 schema**: a parent style item, an ordered set of variant axes (size, colour, fit) and their values, and every stocked variant as an item row carrying its style and its value on each axis. Plan at the style, transact at the variant. It falls under the same rule as `owner_id` (`D-5`) — **converting a year of flat SKUs into a matrix is a re-keying of the item master and every movement that references it**, with human judgement in it, not a schema change. **The matrix screens, the grids and the style-level reports are v2.** Apparel and footwear is the largest organised-retail inventory segment in this market, and a flat item master declines it permanently rather than deferring it | base·app | v1·v2 | P1·P5 | `S-056` `D-12` `D-5` |
| **FR-444** | **A variant axis carries an explicit ordering**, so a size run renders and reports in size order rather than alphabetically, and a range selection ("S through XL") is expressible. This is one integer column and it is unrecoverable in the same way the model is: the order a customer's sizes were meant to take is not derivable from their names | base·app | v1·v2 | P1·P5 | `S-056` `D-12` |
| **FR-445** | **Ratio and assortment packs**: a pack template naming a quantity per variant, received and shipped as one line and exploded into variant-level movements, so a carton of "2 small, 4 medium, 4 large" is one scan and eight units of ledger truth | app | v2 | P5 | `S-056` |
| **FR-446** | The costing-authority rule has **two falsifiers, and both are acceptance tests**. First: on a **standalone** install with no accounting module, the product produces an inventory valuation report that reconciles to the ledger and to a full rebuild — which is why the costing engine cannot live in a module that may not be installed (`D-7`). Second: on an install with accounting present, a handed-over movement's value is **the value warehouse computed**, and a re-costing step on the receiving side is a defect, not a safeguard. Together they are what makes `D-6`'s one-sentence rule testable rather than a preference | base | v1 | P2 | `D-6` `D-7` `S-066` `E-001` |

### 6.27 Amendments — the requirements round 2 required

**These thirteen continue the range at `FR-447` for the same reason §6.26 does: `DECISIONS.md` §7.4
forbids renumbering a published id.** **Five** exist because `GAP-REGISTER-R2.md` §5.1 and §5.3 found
a task line with no requirement to cite — the shape `check-10` exists to catch (`FR-447`–`FR-451`) —
and **eight** because `GAP-REGISTER.md` §4.1 proposed four tasks in round 1 that were never authored,
and each of those four needs its own requirements before its task line can exist (`FR-452`–`FR-455`
for `P3-24`, `FR-456`–`FR-457` for `P4-13`, `FR-458` for `P5-22`, `FR-459` for `P5-23`). Each row names the task
that owns it; **the round-2 finding prefixes (`Q- H- U- Y- Z- K- O- J-`) are registered in
`DECISIONS.md` §6 exactly as the round-1 prefixes are**, and §7's backward check below reads all
fifteen review files.

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-447** | **Delivery is confirmed, not inferred.** `wh_shipments.delivered_at` and `pod_document_id` are v1 columns and the `deliveredAt` grid column is a v1 column, and **nothing in v1 writes any of them** — the driver-side ePOD is `logistics` at v3. `WS-105` therefore carries a **Confirm delivery** action in v1: an authorised user records the delivery date-time, an optional proof document and an optional receiver name, gated on `wh_shipments:confirm_delivery`. Without it the outbound journey has no closing event, every delivery-lead-time KPI reads null, and an NDR has nothing to be an exception *to* | app | v1 | P2 | `U-005` |
| **FR-448** | **A status change against stock carrying an open reservation has one stated outcome and one error code**, and it is the same rule wherever the change originates: a manual status change, a disposition, a quality result — **and `FR-160`'s nightly expiry job, which is a status change and is the one nobody classifies as one**. The rule: a change that would move reserved units out of an available status is **refused** with `409 RESERVED_STOCK` naming the reservations, unless the caller passes an explicit release intent and holds `whb_reservations:release`, in which case the reservations are released, the release is audited against the reason code, and the demand documents behind them are flagged for re-allocation. **The nightly job never releases silently**: it refuses, records the refusal on the job run, and raises the exception for a human | base | v1 | P0 | `Y-002` |
| **FR-449** | **Cancelling an order after its stock has been picked to staging has a de-stage path.** Pick moves stock to a real, countable staging location (`FR-189`); cancellation after that point must post the units back — `MOVE` from staging to the source or to a nominated putaway location, through the port, with a cancellation reason code — before the order may reach `CANCELLED`. An order cancelled with units still in staging is **refused** with `409 STAGED_STOCK`, because the alternative is a balance that is on hand, unreserved, unallocatable by any strategy and invisible to every report that reads demand | app | v1 | P2 | `Y-003` |
| **FR-450** | **Cost and value are suppressed by actor, not only by owner type.** `L-14` suppresses another owner's *value* from a 3PL client; it says nothing about the storekeeper who can open the valuation report. The gate is a **response-DTO omission** driven by `warehouse:cost:view`, applied in the mapper and asserted per endpoint — **never a frontend column hide**, because platform's `role_field_configs` is client-side only and the payload still carries the number. Every endpoint that returns `unit_cost`, `total_value`, `standard_cost` or a cost layer is in scope, exports included | base·app | v1 | P1 | `K-002` |
| **FR-451** | **Two duplicate item rows, or two duplicate counterparty rows, have a merge path — or the product says in writing that they do not.** A 40,000-SKU import against `uk(owner_id, sku)` produces duplicates on day one, from two source systems, from the accessories cross-map, or from a supplier catalogue loaded beside the customer's own. The merge is **a stock transfer to the survivor posted as a real movement through the port** plus a deactivation of the loser with a scan redirect — **never a re-pointing of history**, which `L-2` forbids — recorded once in `whb_master_merges`. It is **refused** where the two rows differ in `base_uom_code`, `lot_control_mode` or `serial_control_mode`, because those are not reconcilable by a transfer. This is not `whb_item_supersessions`, which models a part replaced by its successor and leaves both rows live | base | v1 | P1 | `Z-007` |
| **FR-452** | **An SSCC is allocated, not typed in.** `FR-100` gives the LPN an `sscc` column and nothing fills it. Allocation needs the install's GS1 **company prefix**, an extension digit, a serial reference drawn from a per-key counter and a mod-10 check digit — and it is **not derivable later for labels already printed**, which is why the settings and the counters are v1.1 and not v2 | base | v1.1 | P3 | `S-005` |
| **FR-453** | **EPC is an identity column, and a reader event is an inbound message.** `epc` on the serial and on the LPN; RFID/EPC Gen2 reads arrive at the existing movement port as **inbound messages idempotent by `(epc, read_point, event_at)`** through `whb_inbound_messages`' `uk(source_system, idempotency_key)` (`L-9`) — **no second ingestion table, no second idempotency mechanism**. A read that resolves to no serial or LPN is a recorded rejection, not a dropped packet. The columns are v1.1; the reader endpoint is v2 | base | v1.1·v2 | P3 | `S-010` |
| **FR-454** | **The scan resolver accepts a URI.** GS1 Digital Link puts a URL, not a digit string, behind a 2D code; `whb_item_identifiers.barcode_format` gains `GS1_DIGITAL_LINK` as a **seed row in an open registry, never a `CHECK` value**, and the one scan-resolution service (`FR-062`) parses the AI path segments out of the URI and resolves exactly as it does for a GTIN. A resolver that only accepts digits fails silently on the first customer whose supplier has moved | base | v1.1 | P3 | `S-017` |
| **FR-455** | **Counterfeit control is two rows and a flag**: `is_authorised_source` on item × supplier, and a `SUSPECT` **row in `whb_dispositions`** — a catalogue row, not an enum value — so a part received from an unauthorised source, or one an inspection doubts, is quarantined into a non-available status by the disposition path that already exists rather than by a bespoke workflow | base | v1.1 | P3 | `S-049` |
| **FR-456** | **A regulated-goods licence is an object with an expiry clock and a despatch guard.** A licence type registry; licences held by **our own entity** and by **each counterparty**, each with number, type, issuing authority, validity dates and a document; per-licence quantity ceilings where the schedule imposes one; and a **hard despatch block** — a shipment to a party whose required licence is absent or expired is refused, not warned. `regulatory_class` on the item is what makes batch and expiry tracking mandatory rather than optional for those items. **This requirement is the pharma segment**: if it is not built, four phase descriptions promise a regulated-goods pack the product does not have | india | v2 | P4 | `S-035` `F-073` |
| **FR-457** | **The Schedule H1 register and recall notification are outputs of the ledger, not a parallel book.** The register is a query over movements of `regulatory_class`-flagged items with the prescriber and patient fields the rule requires, rendered and retained for the statutory period; a recall notification is raised against a lot or a batch and lists every counterparty that received it, answered by `whb_transformations` genealogy and the movement history — never by a second table that has to be kept in step | india | v2 | P4 | `S-035` |
| **FR-458** | **The integration surface is named**: API clients, per-client keys with rotation and revocation, a per-client rate limit, and replay. Warehouse's outbox already delivers (`whb_outbox_subscriptions`, `whb_outbox_deliveries`); what is missing is **who** is calling, **how fast** they may, and **how a consumer that fell behind catches up** — and a **lag-shaped signal** beside the failure-shaped ones, because a subscription somebody disabled and forgot is invisible today. It is argued as **platform** work first — `OD-8`'s service-principal recommendation is the same conversation — and built in `warehouse-base` only if platform declines | base | v2 | P5 | `S-097` `K-005` `OD-8` |
| **FR-459** | **One supplier claim register**, not three. A receipt discrepancy, an expiry or breakage claim and a price claim are the same object with different reason codes: a header against a counterparty, lines that reference the movement or the receipt line that evidences them, a status ladder, a settlement amount, and **an ageing report** — because the money is lost by not being asked for, not by being refused. For a distributor this is Marg/GoFrugal parity; for a dealership it is the OEM claim book | app | v2 | P5 | `E-081` |

## 7. Traceability

Every requirement is traceable in both directions, and the check is mechanical.

**Forward — every `FR` has a source.** Zero rows carry an empty *Closes* cell:

```
awk -F'|' '/^\| \*\*FR-[0-9]{3}\*\*/{c=$7;
  if (c !~ /[CTEFSPGQHUYZKOJ]-[0-9]/ && c !~ /D-[0-9]/ && c !~ /OD-[0-9]/) print $2}' \
  WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md | wc -l
→ 0
```

**Backward — every cited finding id resolves to a real finding** in its own register:

```
for p in C:R1-codebase-reality T:R2-tier1-wms-audit E:R3-erp-midmarket-audit \
         F:R4-fulfilment-3pl-audit S:R5-standards-industry-ops \
         P:R6-prior-art-triage G:R7-logistics-supply-chain-seam \
         Q:R8-task-buildability-v1 H:R9-task-buildability-v2-and-epics \
         U:R10-operational-walkthrough Y:R11-exception-and-unhappy-paths \
         Z:R12-lifecycle-and-data-migration K:R13-non-functional-and-operability \
         O:R14-codebase-and-sibling-set-reverification J:R15-competitor-benchmark-r2; do
  grep -oE "\b${p%%:*}-[0-9]{3}[a-z]?\b" reviews/${p#*:}.md
done | sort -u > /tmp/valid_all.txt
grep -oE '`[CTEFSPGQHUYZKOJ]-[0-9]{3}[a-z]?`' WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md \
  | tr -d '`' | sort -u | comm -23 - /tmp/valid_all.txt
→ (empty)
```

**Numbering is contiguous, unique and in order** from `FR-001` to `FR-446`:

```
grep -o '^| \*\*FR-[0-9]\{3\}\*\*' WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md \
  | grep -o '[0-9]\{3\}' > /tmp/frnums.txt
diff /tmp/frnums.txt <(seq -f "%03g" 1 446)
→ (no output)
```

**Distinct findings cited, per register.** The denominator column is
`grep -oE "\bX-[0-9]{3}[a-z]?\b" reviews/Rn-….md | sort -u | wc -l` run over each review; the
numerator is the same pattern, backtick-delimited, run over this document. The valid-id set built by
the command above contains **575** ids, which is the figure `DECISIONS.md` states.

| Register | Findings in the review | Distinct cited here |
|---|---|---|
| `C-` R1 codebase reality | 50 | **43** |
| `T-` R2 tier-1 WMS | 98 | **96** |
| `E-` R3 ERP / mid-market | 90 | **77** |
| `F-` R4 fulfilment / 3PL | 93 | **89** |
| `S-` R5 standards / statute | 98 | **81** |
| `P-` R6 prior art | 60 | **40** |
| `G-` R7 logistics seam | 86 | **65** |
| **Total** | **575** | **491** |

The 84 uncited findings are not lost. They fall into three groups, and
[`GAP-REGISTER.md`](GAP-REGISTER.md) is where each is dispositioned per `D-12`:
(a) findings that are **decisions already taken in `DECISIONS.md`** and therefore have no separate
requirement — the Flyway band, the module split, the prefix table, the accessories separation;
(b) findings **superseded by a sibling** and explicitly deferred to it by their own author — most of
R6's `DUPLICATE` rows and R2's capability-matrix rows without a finding id; and (c) findings that are
**observations about the reviews themselves** rather than about the product — R6 §6's reusability
counts, R7 §8.7's coordination rows, and every register's *"what this lens did not do"* appendix.
`tools/check-design-set.py` fails the build if any of the 575 is untraced in the gap register.

Thirteen decisions (`D-1` … `D-13`) and all seven open decisions (`OD-1` … `OD-7`) are cited.
Eleven requirement rows carry a `⛔ OD-n` block, and §9 lists exactly those eleven.

**Amendment traceability.** The five changes in `DECISIONS.md` §5.1 and the `D-6` rewrite are
each traceable to the rows they moved: `D-6` cited by `FR-041`, `FR-230`, `FR-233`, `FR-235`,
`FR-240`, `FR-241`, `FR-243`, `FR-246`, `FR-248`, `FR-250` and `FR-446`; `D-12` — the "nothing is
deferred to later" decision the amendments were taken under — cited by every row `A-1`…`A-4`
moved, so a reader can find them with one grep.

## 8. Coverage

**459 requirements across 27 areas.** Counted with the command below, which counts each row's
**distinct** versions — a row carrying `v1·v1` (a base column and an India document, both in v1, at
different phases) contributes **one** to the v1 column, not two:

```
awk -F'|' '
/^### 6\./ { sec=$0; sub(/^### /,"",sec); sub(/ \*owner.*/,"",sec); next }
/^\| \*\*FR-[0-9]{3}\*\*/ {
  ver=$5; gsub(/^ +| +$/,"",ver); n[sec]++
  delete seen; nv=split(ver,a,"·")
  for(i=1;i<=nv;i++){ v=a[i]; gsub(/ /,"",v)
    if(!(v in seen)){ seen[v]=1; cnt[sec SUBSEP v]++; tot[v]++ } } }
END { for (s in n) print s, n[s] }' WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md
```

| Area | FRs | v1 | v1.1 | v2 | v3 |
|---|---|---|---|---|---|
| 6.1 The stock ledger | 31 | 30 | — | — | 1 |
| 6.2 The movement port | 16 | 16 | — | — | — |
| 6.3 Items, units of measure, identification and packaging | 31 | 29 | 3 | 2 | 1 |
| 6.4 Identity and the facility model | 15 | 15 | 2 | — | — |
| 6.5 Lots, serials, LPNs, stock status and duty status | 13 | 12 | 2 | 3 | — |
| 6.6 Owner of goods | 9 | 8 | — | 4 | — |
| 6.7 Counterparties | 6 | 5 | — | — | 1 |
| 6.8 Inbound | 23 | 20 | 2 | 3 | 1 |
| 6.9 Inventory control | 21 | 20 | 1 | 2 | — |
| 6.10 Reservations and allocation | 11 | 11 | — | — | — |
| 6.11 Outbound | 35 | 18 | 9 | 16 | — |
| 6.12 Execution, mobile, scanning and printing | 18 | 7 | 9 | 3 | 2 |
| 6.13 Valuation and the accounting seam | 22 | 19 | 1 | 5 | — |
| 6.14 Replenishment and reorder | 9 | 5 | 2 | 2 | 1 |
| 6.15 Kitting, assembly and value-added services | 8 | — | 5 | 2 | 1 |
| 6.16 Returns and reverse logistics | 12 | 6 | — | 8 | — |
| 6.17 Third-party logistics | 23 | 1 | — | 20 | 3 |
| 6.18 India | 26 | 16 | — | 12 | — |
| 6.19 Events, the outbox and the logistics seam | 19 | 13 | 2 | 6 | 2 |
| 6.20 Adapters and the module contract | 26 | 22 | 2 | — | 2 |
| 6.21 Open registries and extensible vocabularies | 9 | 8 | 1 | — | — |
| 6.22 Reports, KPIs and analytics | 17 | 14 | 2 | — | 1 |
| 6.23 Permissions and access control | 10 | 10 | 1 | — | — |
| 6.24 Import, go-live and data migration | 11 | 6 | 4 | 1 | 1 |
| 6.25 Non-functional | 21 | 16 | 4 | 1 | — |
| 6.26 Amendments — requirements added after the first authoring wave | 4 | 3 | — | 3 | — |
| 6.27 Amendments — the requirements round 2 required | 13 | 5 | 4 | 5 | — |
| **Total** | **459** | **335** | **56** | **98** | **17** |

**The version columns sum to 506, not 459, and that is not an error.** 413 rows resolve to a single
version; **45 span two and one spans three**, because the column lands in one version and the screen
or behaviour in a later one — `v1·v2` for the duty-status column and the bonded feature, `v1·v1.1`
for the print renderer and the print server, `v1·v2` for the landed-cost column and the landed-cost
document, `v1·v2` for the variant schema and the matrix screens, and now `v1.1·v2` for the EPC
column and the reader endpoint (`FR-453`). **Those 46 rows are the whole argument of this document in
one number.** *(The pre-round-2 edition of this paragraph said "401 rows / 45 span two", which summed
to 491 rather than the stated 492: it counted the one three-version row as a two. The distribution is
now computed rather than carried forward — `distinct=1 413 · distinct=2 45 · distinct=3 1`.)*

A further **six rows carry two v1 phases** (`v1·v1` at `P1·P2-IN` or `P2·P2-IN`) — `FR-244`,
`FR-304`, `FR-305`, `FR-306`, `FR-307`, `FR-308`. They are not split deliveries across releases; they
are a base column and its India document landing in the same release at different phases, which is
exactly the shape `A-4` created.

By phase, counting the same way over the `Ph` column (here a row *does* contribute to each distinct
phase it names):

| Phase | What it is | FR touches |
|---|---|---|
| **P0** | ledger foundation | 117 |
| **P1** | masters, identity, inbound | 102 |
| **P2** | outbound, counting, valuation, returns, printing, reports | 111 |
| **P2-IN** | the India movement documents | 11 |
| **P3** | execution & mobile | 56 |
| **P4** | India statutory & compliance | 18 |
| **P5** | 3PL, channels & reverse logistics | 79 |
| **P6** | optimisation, planning & the logistics seam | 17 |

**The shape to read from this table:** 335 of 459 requirements are v1, and the great majority of the
v1 count is in P0 and P1 — columns, keys, registries and seeded tables with **no v1 screen**. That is
deliberate. The 40 v1 schema items R4 lists and the 28 R5 lists are the ones that are free before the
first migration runs and either very expensive or genuinely impossible afterwards, in the specific
sense that *the historical values do not exist and cannot be invented*.

**What the `DECISIONS.md` §5.1 amendments moved**, measured the same way before and after:

| Amendment | Before | After |
|---|---|---|
| `A-1` returns to v1 | §6.16 was 4 v1 / 8 v2 | **6 v1 / 8 v2** — `FR-273` and `FR-275` split rather than moved wholesale |
| `A-2` printing to v1 | §6.12 was 5 v1 / 10 v1.1 | **7 v1 / 9 v1.1** — `FR-225` moved, `FR-224` split |
| `A-3` variants v1 schema | absent from the catalogue | **3 new requirements**, `FR-443`–`FR-445` |
| `A-4` India in two waves | §6.18 was 12 v1 / 21 v2 | **16 v1 / 12 v2**, with a new `P2-IN` phase carrying 11 |
| `D-6` rewrite | 10 rows assumed accounting computes cost | **10 rows rewritten**, 1 new falsifier requirement `FR-446` |

## 9. Open decisions

**All fifteen remain open** and each gates named requirements. `DECISIONS.md` §3 carries the deadline
and the recommendation for each; this table carries only the requirement exposure. *(This section
listed seven until 2026-09-02 while `DECISIONS.md` §3 carried eleven — `X-049`. `OD-12`…`OD-15` were
allocated the same day for the four gates that had been tracked without an id, `X-024`/`X-029`/
`X-030`/`X-036`.)*

| # | Decision | Requirements blocked |
|---|---|---|
| **OD-1** | The reciprocal accounting edits — a **three-state** decision in that set: warehouse absent, warehouse present, and the transition. Accounting stands down its quantity balance, **its own costing**, its counts and its stock journals when warehouse is installed, and posts the value it is handed without re-costing | `FR-230` `FR-233` `FR-313` `FR-446` |
| **OD-2** | Whether the dealer vehicle inventory ever migrates onto the ledger | `FR-365` |
| **OD-3** | One database per customer, or shared multi-tenancy | `FR-303` `FR-440` |
| **OD-4** | Who owns the shared supplier/counterparty master long-term | `FR-116` `FR-121` |
| **OD-5** | Whether the frontend re-closes the vocabularies the backend opens | `FR-380` |
| **OD-6** | Valuation-method scope in v1 — weighted average and FIFO, with the method configurable per item category × site. **Layer ownership is no longer part of this decision**: `D-6` settles it, and the layers are warehouse's | `FR-235` |
| **OD-7** | Precision — quantity, money, per-unit cost and percentage scales | `FR-030` |
| **OD-8** | How an out-of-process consumer authenticates to the port. Recommended: a **platform service principal**, the one item in this set platform must build for warehouse | `FR-284` — and every `logistics` requirement at v3, because a separately deployed consumer has nothing to authenticate with |
| **OD-9** | Whether `warehouse` carries a tax engine, or never computes tax. **Its deadline moves to *before `P2-25`***, not before `P2-IN` — `P2-25` builds the v1 table that implements the rejected option (`U-003`) | `FR-325` against `FR-294` — the India pack is **50 or 56 tables** depending on the answer |
| **OD-10** | Is MRP a dimension of the stock position? **The tightest deadline in the programme**, `PNR-1` = `V500030` | `FR-321`, and through the position key every requirement that reads a balance |
| **OD-11** | Do value-only movements conserve value? | `FR-084` — whose seeded virtual-location list has no value-offset row |
| **OD-12** | The ledger partition key — `occurred_at` or `posting_date`? Recommended: `occurred_at` | `FR-022` against `PLATFORM-DEPENDENCIES.md` `PD-D5`; `L-13` makes them different columns |
| **OD-13** | The value-offset virtual location's **code** — `VALUE_OFFSET`, `LANDED_COST_OFFSET`, or a reused `ADJUSTMENT_OFFSET`. Recommended: `VALUE_OFFSET`, seeded here | `FR-084`, which seeds none of the three |
| **OD-14** | Is value conservation a fifteenth invariant `L-15`, or a movement-type behaviour column? Recommended: the invariant, with a matching `I-21` | `FR-084`, and the landed-cost and assembly-completion requirements that post `quantity = 0` with a value |
| **OD-15** | Is the union valuation report (`M3`) built, given `D-9`'s permanent separation? Recommended: not in v1 | `FR-370` and `D-9`'s cost note — a finance user asking for total stock value gets two numbers |

## 10. What this product deliberately does not do

An unstated absence reads as an oversight and invites someone to build it badly. Each refusal below
appears in this document in the place a reader would look for the feature, with its reason and — where
one exists — its re-entry path. Drawn from R2 §4 (fifteen refusals) and R4 §5.5 (twelve), merged and
de-duplicated to **twenty-one**.

| # | Not building | Who has it | Why not | Re-entry path |
|---|---|---|---|---|
| 1 | **A transportation management system** — carrier rate shopping, freight procurement, route optimisation | Manhattan, Blue Yonder, SAP, Oracle — all *separate products even at their own vendors* | Rating needs carrier contracts, fuel surcharges, accessorial rules and dimensional-weight logic. It is a product, not a feature | A carrier API connector for labels (`FR-202`), then the future logistics module (§6.19) |
| 2 | **Distributed order management / order sourcing across sites** | Manhattan, Blue Yonder, Softeon | This is an OMS: it decides *where* to fulfil from, and a WMS executes once that is decided. Building it would make the warehouse the system of record for orders, which it must not be | A separate module reading the availability API (`FR-174`) |
| 3 | **A labour-standards engineering engine** — element libraries, travel-time models, discrete engineered standards | Manhattan, Blue Yonder, SAP EWM, Infor | Engineered standards need industrial-engineering time studies per site. We measure *actual* task duration and report it (`FR-213`, `FR-227`) | `FR-228`, on a year of our own data |
| 4 | **Incentive pay computation** | Manhattan, Blue Yonder | Payroll consequences from a warehouse metric is a labour-relations product, and a wrong number is a legal problem, not a bug | None |
| 5 | **Direct automation control** — PLC telegrams, AS/RS material flow, conveyor and sorter control | SAP EWM's material-flow system is uniquely deep here; Körber via its automation arm | Real-time control software with safety implications, written to a different engineering standard than a web application | `FR-229` — a task event contract and the port; the automation vendor integrates |
| 6 | **Voice recognition** | Körber, Infor, Manhattan, Blue Yonder | Speech recognition tuned for warehouse noise and accents is a specialist product | Integrate; never build |
| 7 | **A slotting optimisation solver** | Manhattan, Blue Yonder, SAP EWM | The *analysis* — velocity, cube, affinity — is worth having; the optimiser is an operations-research problem whose value depends on constraints we will not have modelled | Report the recommendation in v3 and let a human move the stock |
| 8 | **Demand forecasting, multi-echelon optimisation, seasonal profiles, fair-share allocation** | Blue Yonder, SAP IBP, Oracle | A planning product. A WMS that guesses at forecasts is a worse forecaster than a spreadsheet and a worse WMS for the distraction | **Relocated, not refused** — a planning module with its own band, consuming a forecast through an interface. `FR-258` is the boundary |
| 9 | **Service-parts planning** — initial provisioning, last-time-buy, rotable pools, installed base, performance-based logistics | The specialist service-parts vendors | It sells to an OEM rather than a distributor and it is a separate product with sixteen modules of its own | The same planning module. Four nullable seam columns and two shared classification fields cost nothing now (`FR-070`) |
| 10 | **LIFO costing** | SAP, Oracle, jurisdiction-limited | Prohibited under Ind AS 2 / IAS 2 and ICDS II. Offering it invites a customer to produce non-compliant accounts, and "we removed it" is a better answer than "we never thought about it" | Never (`FR-235`) |
| 11 | **A general-purpose rules engine or scripting layer** | Körber's configuration toolkit, Blue Yonder, Manhattan, Oracle's RF screen configuration | Five ordered, typed rule tables give most of the benefit and stay reviewable and testable. A scripting layer becomes the place business logic hides from code review. **Four rule sets in this document are bounded rows** — putaway, allocation, rate-shopping and negative stock — and the fifth must not introduce an interpreter because the other four feel limiting | A new bounded operator, reviewed once. Never an interpreter |
| 12 | **JSONB custom-field bags** | Every tier-1 offers user-defined fields | Forbidden by the platform's own standards, and the mechanism by which filters, indexes and reports become impossible | Typed attribute tables (`FR-076`) or a typed column on request (`FR-078`) |
| 13 | **Multi-tenant SaaS** — one database, many customers | Oracle WMS Cloud, Manhattan Active | The platform is single-tenant per install by existing decision. The owner dimension gives multi-*client* separation inside one install, which is what a third-party operator needs and is **not the same thing** (`FR-440`) | **⛔ OD-3** |
| 14 | **Medical-device and pharma-serialisation compliance regimes** | The healthcare-supply-chain specialists | Each is a regulatory programme with certification, not a feature. Decline the vertical rather than half-support it | We implement the *shape* — unit identity, aggregation, and an event log with the four standard dimensions — so an adapter can emit either (`FR-100`, `FR-105`) |
| 15 | **International trade compliance** — export and customs documentation, free-trade zones | SAP's trade-services product, Manhattan and Infor partially | Country-specific regulatory software. Our India obligations are in scope; global trade compliance is not | Bonded and MOOWR are in scope (`FR-323`); customs declarations for parcels are a v3 adapter |
| 16 | **Shift simulation, digital twin, 3D warehouse visualisation** | Infor's 3D visualisation; simulation offerings | Demo-ware at our stage. It sells to buyers who are not our buyers, and it consumes the effort that should go into RF screens | None |
| 17 | **An invoice, a tax engine or a receivable inside `warehouse-3pl`** | **No audited 3PL product does this either** — every one of them hands off | It duplicates the accounting module and gives the customer two receivable subledgers and double-counted turnover | Never. The AR envelope is the interface, and the CSV fallback covers an install with no accounting module (`FR-294`) |
| 18 | **A refund or payment path anywhere in warehouse** | Storefront-adjacent tools | A refund is a receivable event with tax consequences | Emit the disposition; the channel or accounting decides (`FR-274`) |
| 19 | **A consumer returns portal** | The eCommerce fulfilment platforms | It belongs to the brand's storefront. Building it means owning consumer identity, consumer support and a public attack surface for a screen the brand wants to skin themselves | An API — the RMA object accepts an externally created authorisation today (`FR-269`) |
| 20 | **An event-standard repository with a query and subscription interface** | The standards-body solution vendors | It is a compliance product in its own right. Our obligation is to *emit* correct events | A projection over the port in v3; a repository only if a trading partner requires one, and then as an adapter |
| 21 | **Offline write *authority*** — a session that is the source of truth while disconnected | Some legacy WMS | It would falsify the append-only sequence and the tamper chain simultaneously | Offline **capture** with deferred sync through the port's idempotency and batch endpoints, which is the actual requirement (`FR-221`, `FR-034`) |

One further boundary is a **deferral, not a refusal**, and is recorded here because a deferral
written down nowhere becomes a re-opened finding at the next audit:

| # | Deferred | Why not v1 | Re-entry cost |
|---|---|---|---|
| B | **Cold chain** — sensor readings, excursion events and a quality disposition | The v1 cost is small (bind readings to a zone, location, LPN or shipment) but the excursion *decision* is a workflow. Item-level temperature limits with nothing measuring against them is a requirement with no enforcement | `FR-068` puts the zone columns in v1; the readings, excursions and auto-quarantine are v2 |

**One row was removed from this table by `DECISIONS.md` `A-3`, and the removal is recorded rather than
silent.** The first draft deferred **apparel and footwear** — the style × size × colour matrix — and
said that if apparel was not a target market this document should say so rather than leave it to be
discovered. `A-3` answered: the matrix is a **v1 schema commitment** under the same rule as
`owner_id`, because a flat item master does not defer apparel, it declines it permanently. The
requirements are `FR-443`–`FR-445`; the screens remain v2. **A deferral that turns out to be a
refusal in disguise is exactly what this table exists to catch, and in this case it caught one.**

## 11. A standing instruction

Every factual claim in this document about the *existing* codebase comes from
[`reviews/R1-codebase-reality.md`](reviews/R1-codebase-reality.md), which carries `file:line`
evidence and was verified against the live checkout on **2026-09-01**.

**Re-verify before relying on any of them.** The prior warehouse design set verified its claims too —
against a different checkout — and by the time anyone read it, `supply-chain-core` and
`warehouse-core` had ceased to exist, forty-six foreign-key targets had evaporated, and fourteen
documents were instructing an author to edit released migrations in place under a rule that never
existed. That is not a criticism of that work; it is the reason this section exists.

Three further standing rules, from the same source:

1. **Never state a count you did not compute with a command**, and put the command in the document.
   Every count in §7 and §8 carries its command.
2. **Every cross-reference must resolve.** The accounting set's worst failure was fabricated
   cross-references that looked plausible and resolved to nothing — 25 dangling requirement citations
   of which 19 resolved to a *different* real requirement, so live gaps read as closed.
3. **Never blanket search-and-replace an id.** It corrupted the accounting decisions table twice.
4. **`reviews/R2` has two numbering systems and they look alike.** Its capability-matrix rows are
   numbered independently of its `T-nnn` findings, so a matrix row number reads exactly like a
   finding id and resolves to the wrong thing. **Four such miscitations were caught and fixed in this
   document during the first authoring wave** — a capacity row cited as an owner-segregation finding,
   a genealogy row cited twice as a supervisor-console finding, and a traceability row cited as a
   stock-period finding. Cite an R2 finding only after opening the `T-nnn` heading itself. Now
   recorded as `DECISIONS.md` §7.4a.
