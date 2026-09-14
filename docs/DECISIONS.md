# Decisions — the spine of the Warehouse design set

<!-- check-design-set: issue-citations file #2 — `#2` and `#9` are ordinals in prose, not issue references — *Refusal #2*, *Adapter #2 (services)*, *ship-blocker #2*, *logistics needs #1, #2, #3, #5, #6, #10* — and at COMPETITOR-BENCHMARK.md:70/:146 `#9` is the markdown in-page anchor `[§9](#9--where-the-audits-disagree)`. In this repository `#2` and `#9` are in fact the two **pull requests** opened while the backlog was being filed, so no issue row can ever exist for either: see issues/CREATED.md -->

> **This document wins over every other document in this repository except
> [`reviews/R1-codebase-reality.md`](reviews/R1-codebase-reality.md), which wins on any question about what
> the *existing* `neetub1508/classic` codebase does, because it carries `file:line` evidence.**
>
> Every author — human or agent — reads this file before writing anything else. Module names, package
> names, Flyway bands, table prefixes, id namespaces and the version ladder are fixed here and nowhere
> else. A document that disagrees with this one is wrong.

Established 2026-09-01 from seven `functional-reviewer` lenses (`reviews/R1`–`R7`, 11,750 lines,
**575 findings**) run against the live `classic` checkout, the in-flight `accounting` design set, and
28,928 lines of prior warehouse/supply-chain/TMS design art in `neetub1508/classic-issues`.

> **2026-09-11 current resolution:** [Global settings and resolved behaviour](GLOBAL-SETTINGS-DECISIONS.md) is adopted by this decision spine. All nineteen allocated OD rows now have a warehouse-side answer. Historical escalation headings below describe their origin, not a pending request to a human. External adapter work remains an explicit capability gate. This amendment governs conflicts about negative stock, currency, tax and label format.

---

## 1. What is being built

A **standalone-capable, country-neutral warehouse and inventory-management product**: one immutable,
double-sided, append-only stock ledger at full grain, with the application layers that write to it, and
a generic inbound movement port so that any number of future consumers — a logistics/TMS module, a
supply-chain/procurement module, a POS, an eCommerce channel, or any vertical in the suite — can move
stock **without `warehouse-base` ever depending on them**.

It is not a replacement for anything currently shipping. It is the first real stock ledger in this
suite: `services`, `field-service` and `assets` have **no** stock capability at all
(R1 `C-034`), and `services.parts_used` is free `TEXT`
(`services/…/V40095__Change_parts_used_from_jsonb_to_text.sql`, R5 Fact 2).

---

## 2. D — the decisions. Do not re-litigate these.

### D-1 · Five modules, not four

| Module | Java package | Depends on | Ships |
|---|---|---|---|
| **`warehouse-base`** | `ai.warehousebase` | **platform only** | v1 |
| **`warehouse`** | `ai.warehouse` | platform + `warehouse-base` | v1 |
| **`warehouse-adapter-<vertical>`** | `ai.warehouseadapter<vertical>` — a **sibling**, never `ai.warehouse.adapter.*` | platform + `warehouse-base` + that vertical | v1 → v2, one per vertical |
| **`warehouse-3pl`** | `ai.warehouse3pl` | platform + `warehouse-base` + `warehouse` | v2 |
| **`warehouse-india`** | `ai.warehouseindia` | platform + `warehouse-base` + `warehouse` | v1 foundation / v2 extension |

`warehouse-india` is the **fifth** module and was not in the original brief. It exists because the
brief's four modules carry a *vertical* axis and no *jurisdiction* axis, and every India rule —
e-way bill, delivery challan, job work and ITC-04, the Rule 56 stock account, MRP declarations, bonded
warehousing — would otherwise have to live either in `warehouse` (making the core product unsellable
outside India) or in `warehouse-adapter-dealer` (making it invisible to a pharma customer). Accounting
took the same decision and shipped `accounting-india`. Source: R5 `S-021`.

**The adapter package must be a sibling.** `@ComponentScan("ai.warehouse")` would load
`ai.warehouse.adapter.dealer` unconditionally, in every install, including ones where dealer is not
built. This is the exact trap the accounting round-4 review found and corrected.

### D-2 · Flyway bands are **V500000–V549999**, not V900000+

**The bands named in the original brief are occupied and are hard-reserved by platform code.** Verified:

| Band | Occupant | Count |
|---|---|---|
| `V900000`–`V909999` | dealer OEM seed — `dealer/backend/src/main/resources/db/seed/{maruti,honda,tata,hyundai,mahindra,toyota,kia,mg,jcb,tatacommercial}/` | 135 `.sql` |
| `V910000`–`V919999` | platform per-client — `platform/backend/src/main/resources/db/client/{ktlautomobiles,logix,pasco,platinum,vehicron}/`, version numbers **deliberately reused across clients** (`V910001__` exists five times) | 434 `.sql` |
| `V950000`+ | platform test data | 32 `.sql` |

`FlywayConfiguration.java:296-320` additionally **renumbers legacy history rows into both bands**
(`+830000`), and `:322-327` then `DELETE`s duplicate history rows — so a collision does not fail
loudly, it silently deletes a history row. Source: R1 `C-001`, `C-002`, `C-003`.

`V130000`–`V599999` is **entirely empty** (0 files, computed). The allocation is:

| Module | Band |
|---|---|
| `warehouse-base` | **V500000 – V509999** |
| `warehouse` | **V510000 – V519999** |
| `warehouse-adapter-*` (all adapters share the band, sub-allocated per adapter) | **V520000 – V529999** |
| `warehouse-3pl` | **V530000 – V539999** |
| `warehouse-india` | **V540000 – V549999** |

Every task file pre-allocates its own migration numbers inside its module's band, so parallel work
cannot collide. `tools/check-design-set.py` fails the build on double-ownership or an out-of-band
number.

**Five modules get a band; nothing else does.** `platform`, `mobile` and `logistics` are named on task
headers and hold **no band here**. For `platform` and `mobile` that is right by construction — a task
writes to platform registries, it does not create platform tables (`DATA-MODEL.md` §8.3 note 2). For
`logistics` it is a boundary, and `P6-08` states it: `logistics` is a first-class module of our own
that gets no adapter (`FR-366`), so **its `log_*` schema is numbered by the `logistics` design set,
outside these bands.** The adapter-band reservation `V524000`–`V524999` covers only the warehouse-side
enablement of that seam — catalogue seed rows and the seam's permission, menu and grid configuration
(`DATA-MODEL.md` §2.5.6, §7.4). A design set that numbered another module's migrations would be
claiming ownership it does not have, which is the `scc_*` failure `P6-08` exists not to repeat.

### D-3 · Table prefixes — fixed, because three lenses proposed three different ones

`Dockerfile.backend` flattens every module's migrations into **one directory** and the frontend merges
every module's `src/` **last-write-wins**, so prefixes are not cosmetic.

| Module | Prefix | Example |
|---|---|---|
| `warehouse-base` | **`whb_`** | `whb_stock_movements` |
| `warehouse` | **`wh_`** | `wh_pick_tasks` |
| `warehouse-3pl` | **`wh3_`** | `wh3_rate_cards` |
| `warehouse-india` | **`whin_`** | `whin_eway_bills` |
| adapter · dealer | **`whad_`** | `whad_part_supersessions` |
| adapter · services | **`whas_`** | `whas_job_part_issues` |
| adapter · field-service | **`whaf_`** | `whaf_van_stock_assignments` |
| adapter · assets | **`whaa_`** | `whaa_spare_consumptions` |
| adapter · **reference example** (CI artefact, `D-11`) | **`whae_`** | `whae_demo_movements` |

R2 proposed `wb_`/`w3_`, R4 proposed `whb_`/`wh3pl_`, R3 proposed `wh_` for base. R7 `G-079` raised the
collision as a coordination BLOCKER. **The table above is the resolution.** Note in particular that
`wh_` is the *application*, not the base — R3's usage is the one that changes.

**Do not name anything `wms_*` or `scc_*`.** `platform/…/V528:37,57,59` and `V663:17-19` still carry
hardcoded `wms_*` / `scc_*` / `warehouse-*` permission exclusions from a deleted earlier module. Those
migrations have already run, so they grant a new module nothing — but a new `wms_`-prefixed permission
would inherit a decision nobody took. Source: R6.

### D-4 · The stock ledger is double-sided, append-only and immutable

Every stock event is a **movement** with **two or more lines** that conserve quantity — a receipt's
counter-side is a virtual location, not an absent row. Posted lines are never updated and never
deleted; a correction is a reversal. Positions (on-hand) are a **cache** that a full rebuild must
reproduce exactly.

This is the single decision that separates this product from everything already in the suite.
`accessory_inventory_transactions` is a **single-sided log written alongside an in-place-mutated
`accessory_stock_levels` row**, and some paths — `StockReceiptService.java:373-411` — move the balance
and write no movement at all, so the balance is not derivable from the movements (R1 `C-021`). The
prior WMS art has the same shape: one row carrying both `from_warehouse_id/from_bin_id` and
`to_warehouse_id/to_bin_id` (R2 `T-001`). **Neither is a ledger. Do not copy either.**

### D-5 · `owner_id` is `NOT NULL` in `warehouse-base` v1, in every install, and in the position key

`warehouse-3pl` ships in v2. **`owner_id` ships in v1.** Consignment stock, customer-owned goods under
repair, job-work material at a job worker, bailed 3PL stock and our own stock are the same shape and
differ only by owner. There is no rule that recovers whose a unit was, so the column is free now and
**unbackfillable later**; without it `warehouse-3pl` is not a module, it is a rewrite. Four lenses
reached this independently: R2 `T-002`, R4 `F-001`/`F-002`, R5, R7 §6 item 1.

The same argument, with the same verdict, applies to `duty_status` (bonded vs duty-paid stock of one
SKU must never merge — once commingled no algorithm separates them, and it is a customs offence, not a
data-quality issue), `stock_status_code`, `lot_id`, `serial_id` and `lpn_id`. See
[`IRREVERSIBLE.md`](IRREVERSIBLE.md) for the complete list and the argument per item.

### D-6 · Whichever system is authoritative for **quantity** is authoritative for **cost**; accounting always owns the **ledger**

The `accounting` design set already specifies a valued stock ledger — `acc_valuation_entries`
(*"every quantity move with its value"*, `accounting/docs/DATA-MODEL.md:436`), `acc_cost_layers`
(`:434`), `acc_stock_balances` keyed item × godown × batch × serial (`:507`), `acc_godowns`,
`acc_batches`, `acc_stock_journals`, `acc_physical_stock_counts`, plus `acc_source_documents` /
`acc_source_document_movements` (`:274-277`), which is already an idempotent inbound movement port.
Left alone, two products would be the system of record for quantity, at two grains, with two counts
and two adjustment documents. Source: R5 Fact 1 and `S-064`, R3 `E-001`.

**The split:**

> `warehouse` is the system of record for every **movement, position, count, adjustment and physical
> truth**, at full grain — **and therefore for cost**. `accounting` is always the system of record for
> **the ledger**: it receives valued movements through its source-document port and posts them, and it
> owns everything downstream — the GL, revaluation approval, NRV and provisioning, period close and
> the financial statements.
>
> **The rule, in one sentence: whichever system is authoritative for quantity is authoritative for
> cost.** Warehouse installed → warehouse runs the costing engine, because only warehouse holds the
> grain the costing methods need (owner, duty status, lot, serial, location — FEFO and specific
> identification are not expressible at accounting's item × godown × batch × serial grain), and
> because a **standalone** install (`D-7`) must be able to produce an inventory valuation with no
> accounting module present. Accounting then does **not** re-cost what it is handed.
> Warehouse absent → accounting's own P3 stock engine does both, exactly as its design set already
> says. Where the warehouse product is installed, accounting's quantity balance and its own costing
> stand down: `acc_stock_balances` becomes a read-through projection, `acc_cost_layers` is not
> maintained, and `acc_physical_stock_counts` / `acc_stock_journals` become *inbound document kinds*,
> not screens.

This resolves the ambiguity the benchmark author flagged between R5 `S-066` (*accounting computes
value*) and R3 `E-001` (*warehouse owns quantity + layers*). **R5 `S-066` is overruled**, for the two
reasons above; its underlying concern — that FIFO/AVCO/standard must live in exactly one place per
install — is met by the authority rule rather than by fixing the place. `OD-1` is the amendment that
carries this into the accounting set, and it is now a **three-state** decision there, not two.

**Warehouse never writes an `acc_*` table.** It hands over one envelope per posting-relevant event
through accounting's existing source-document port, and carries `handover_id` +
`posting_status (NOT_APPLICABLE | PENDING | POSTED | REJECTED)` on its own movement so that "does the
stock ledger tie to the GL" is answerable. An architecture test fails the build if any class under
`ai.warehouse*` references an `acc_*` table or an `ai.accounting*` type. Sources: R5 §4.8, `S-066`,
`S-067`, `S-068`.

**Movements whose `owner_type != OWN` are handed over for quantity and custody reporting only, and are
never valued.** A 3PL that posts its clients' stock to its own balance sheet has a catastrophe in both
directions. Source: R5 `S-078`.

> The reciprocal edits to the `accounting` design set are **`OD-1`**. They are that set's to make, not
> this one's.

### D-7 · Standalone is the reference configuration

`platform + warehouse-base + warehouse` is a complete, shippable product — not a degraded mode. No
capability in v1 may require `dealer`, `automotive`, `accounting` or any other vertical to be
installed. This is what makes `warehouse-base`'s zero-vertical-dependency claim testable rather than
aspirational.

### D-8 · Country-neutral core

No GST, HSN semantics, e-way bill or MRP rule is hardcoded in `warehouse-base` or `warehouse`. Tax
identity, document types, statutory registers and print layouts are **data**. India ships as
`warehouse-india`. The core carries only the *hooks* India needs — and those hooks are in v1 because
they cannot be added later (`company_id` on the movement, `reason_code_id` from a closed tax-mapped
catalogue, HSN on the item, `duty_status` in the position key). Sources: R3 §3, R5 §2.

### D-9 · `accessories` inventory stays permanently separate — and the cost is named, not hidden

**User decision, taken 2026-09-01.** `accessories` keeps `accessory_warehouses`,
`accessory_storage_bins`, `accessory_stock_levels`, `accessory_inventory_transactions`,
`accessory_stock_transfers`, `accessory_stock_adjustments`, `accessory_inventory_counts`, its stock
receipts, its issuance workflow and its 11 reports. Warehouse serves the verticals that have nothing.

This design set does not argue with that. It **costs** it, in writing
([`COEXISTENCE.md`](COEXISTENCE.md)): 17 tables, 71 backend files, 11 reports and 33 mobile screens
duplicated; a second item master; **two stock truths with no reconciliation and no unified report**;
and — the load-bearing one — the same physical unit counted in both systems is not merely unmitigated
but **undetectable**. Two mitigations are therefore mandatory in v1 and are tasks, not advice:

1. **`whb_item_external_refs` carries an `ACCESSORIES` source-module row for every dual-stocked SKU** —
   the cross-map registry, so double-counting is at least *detectable*.
2. **A category-ownership rule**, recorded as data: for any item category, exactly one of the two
   systems is the stocking system of record, and a reconciliation report names every violation.

Sources: R1 `C-032`, R3 §5 (11 named costs C1–C11, 9 merge-free mitigations M1–M9).

### D-10 · Every extensible vocabulary is a catalogue table with **no CHECK constraint**

Thirteen of them (R7 §5): movement types, document types, source systems, reference types, stock
statuses, location types, item types, reason codes, UoM classes, task types, owner types, hold types,
charge codes. Each is a table with `code`, `name`, `owning_module`, `is_system`, and behaviour flags —
never a `CHECK (x IN (…))`, never a Java enum, never a TypeScript string union that re-closes on the
frontend what the backend opened.

The precedent that works is live and self-documenting: `acc_reason_codes.context` carries no CHECK
**deliberately** — *"It is a CATALOGUE, not an enum"*
(`accounting-base/…/V600002__Create_acc_reason_codes.sql:22-26`). The counter-example is equally live:
`widget_definitions.chk_module` has been widened by DROP/ADD **three times**
(`V234:36` → `V276:10` → `V557:18`) and still admits neither `warehouse` nor `logistics`. The prior
warehouse product broke on exactly this: `location_type` / `zone_type` CHECKs *"dropped and recreated
with completely different enum value sets"* 36 versions after creation (R6).

**Corollary, and it is a real constraint on the plan:** the loose-coupling ratchet can only ever be
*"zero commits to `warehouse-base`"* — **never** *"zero commits to `platform`"*. `COMMON_FILTER_CONFIGS`
is a TypeScript `const` at `platform/frontend/src/utils/filterUtils.ts:346` with 210 scopes, and
`CacheConfiguration.java` is platform Java. Every new grid edits both. A contract that claims otherwise
is false on day one and, being false, gets ignored — taking the true invariants with it. Source: R7
`G-047`.

### D-11 · Adapters are proved by a build-time test, not by intent

An adapter **may**: depend on `warehouse-base` and its own vertical; post movements through the port;
register its own permissions, menus, grids and filter scopes; own its own `wha*_` tables; read the
vertical's tables.
An adapter **must not**: be depended upon by `warehouse-base` or `warehouse`; write `whb_`/`wh_` tables
directly; add a column to a base table; extend a base vocabulary by `ALTER`.
**The test:** `warehouse-adapter-dealer` ships with **zero commits to `warehouse-base`**, enforced by an
`ArchitectureInvariantsTest` in each module and by a `warehouse-adapter-example` reference adapter that
CI builds. Adapter #2 (services) is in v1 for the same reason accounting put its adapter in v1: one
adapter proves nothing about genericity. Source: R7 §4, R3 `E-006`.

### D-12 · v1 is a cut line, not the scope limit

**User decision, taken 2026-09-01.** Every capability found by any lens is placed in a version and
carried in a task file **now**. Nothing is deferred to "we'll look at it later". §5 is the version
ladder; every one of the 575 findings is dispositioned into a task in
[`GAP-REGISTER.md`](GAP-REGISTER.md), and `tools/check-design-set.py` fails if any finding is untraced.

### D-13 · Mobile is not optional

Every user-visible warehouse capability that has a web screen has a mobile counterpart in the same
task, per CLAUDE.md's web↔mobile mirroring rule. A warehouse product whose operators cannot work from a
handheld is not a warehouse product. Note the correction to CLAUDE.md found by R1 `CM-1`:
`mobile/…/ListHeader.tsx:210-218` now supports `type?: 'dropdown' | 'text'` filters — **date filters
are still unsupported**.

### D-14 · Associations between masters are dated many-to-many; a warehouse has exactly one REGISTERED branch

**User decision, taken 2026-09-10**, on round 4's findings (`reviews/R22`–`R26`, §6). The disposition of
all 83 findings and the full fold plan are in [`GAP-REGISTER-R4.md`](GAP-REGISTER-R4.md).

1. **Every association between two independent masters is an effective-dated many-to-many junction.**
   *(Narrowed 2026-09-14 by item 8: dates only where history is read; a pure link-set is edited from a
   row action.)*
   It carries `is_primary`, or a role, where a default is needed. **Two kinds of row stay scalar**:
   composition, where a line belongs to its parent document, and ledger fact rows, which record what
   happened and are never re-pointed. The junction shape is R22 §1.3: `effective_from`/`effective_to`,
   one current row per key enforced by an `EXCLUDE` constraint, and no `is_active` on a dated junction.
   R22's six KEEP-SCALAR findings (`RG-022`…`RG-027`) mark the edge of this rule.
2. **A warehouse is linked to platform branches through `whb_warehouse_branches`.** At every instant it
   has **exactly one `REGISTERED` link**. That branch supplies the site's GSTIN, its branch-scoped
   statutory numbering, and its tax attribution. `whb_warehouses` loses `branch_id`,
   `tax_registration_id` and `legal_entity_id`.
   - `SERVING` links grant visibility and let the branch draw stock.
   - Classification reads the `REGISTERED` link at the movement's `occurred_at`. Access reads today's
     links.
   - A site with no link is visible to no branch-scoped user.
   - **This reverses `FR-079`'s *"belongs to exactly one branch"*, `DATA-MODEL.md` §9.2's
     dropped-junction row, and the advice of `C-016`/`C-030`.** `RG-001` is canonical.
3. **The serving-branch rule.**
   - A document handed over at the requesting branch (a counter sale, a job issue) posts directly from a
     site only when that branch holds a current `REGISTERED` or `SERVING` link to the site **and** its
     GSTIN equals the site's `REGISTERED` GSTIN.
   - **A `SERVING` branch under a different GSTIN draws by transfer, and that transfer is a cross-GSTIN
     supply.** It sets `is_taxable_supply = true` and carries a challan or invoice and, above the
     threshold, an e-way bill. The source is the `REGISTERED` branch; the destination is a site
     registered to the serving branch. The counter refuses a direct sale with
     `422 CROSS_GSTIN_COUNTER_SALE`.
   - A demand order despatched to a third party is billed from the site's `REGISTERED` GSTIN at despatch.
4. **A registration change is maker–checker, and it is refused while the site holds stock** under a
   different GSTIN. It closes one history row and opens the next at the same instant. `OD-19` asks
   whether that refusal can ever be relaxed.
5. **Link, never mirror.** A site is not a branch row. A `WAREHOUSE`-type branch is created only when a
   site is itself a GST place of business that no existing branch carries (`RH-003`).
6. **One branch-scope mechanism.** Scope uses platform's `BranchScopeService` and the
   `:view:all`/`:view:branch` pair. The warehouse resolver returns the set of allowed warehouse ids
   (`RH-001`, `RH-002`).
7. **Not everything on day one** (user decision 3, same date). A capability that is useful but not needed
   on day one goes into v2 or a later phase **and still gets a task file**, per `D-12`. Round 4 therefore
   adds six task files: one at v1.1 and five at v2. It also lifts every v2 junction a lens had placed on
   a v1 task out into a v2 task. Where a lens offered a heavier and a lighter shape, the lighter one is
   taken and the reason is written in `GAP-REGISTER-R4.md` §3.7.
   *Amended the same day, 2026-09-10 (user rule: **no duplicate tasks**).* The six task files were then
   folded into their most similar existing tasks and deleted; `#156`–`#161` are closed as duplicates. The
   substance stands — useful-but-not-day-one work is still tracked and still versioned later — but it is
   tracked as a *v1.1* or *v2 increment* inside an existing task, not as a new task file.
   `GAP-REGISTER-R4.md` §4.6 has the mapping.
8. **Round-5 amendment, 2026-09-14 (user decision): follow the existing pages, and go no heavier than the
   need.** Items 1–7 stand except where this item narrows them.
   - **a. Dates only where history is read.** A junction carries `effective_from`/`effective_to` and an
     `EXCLUDE` only when something must answer *"which link held at a past instant"* — a movement's
     `occurred_at`, a filed return, a custody shortage. That is `whb_warehouse_branches`,
     `whb_company_branches`, `whb_warehouse_companies`, `whb_owner_companies`,
     `whb_location_user_assignments`, `whin_gstin_profile_branches`, and the dated junctions already
     specified (category assignments, supplier sources, lot parties). **Any other association between two
     masters uses the plain junction of the existing pages**: `(parent_id, child_id, is_active,
     display_order)`, plus `is_primary` where a default is needed, and `uk(parent_id, child_id)` — as
     dealer `pdi_stock_yard_branches` (`V20123`), `pdi_stock_yard_companies` (`V20121`) and automotive
     `company_branches` (`V10014`). The undated junctions already in `DATA-MODEL.md` stay as specified.
     Item 1's *"every association is effective-dated"* is narrowed to this.
   - **b. A pure link-set is maintained from a row action, not from a sub-grid.** Where a parent's
     association with another master carries nothing but the link (role, primary, dates), the parent's
     list has a **row action button** that opens `<Parent><Children>Modal`, a thin wrapper over one
     module-local generic assignment modal: current list + available list, add several, remove one;
     `Modal size="xl" resizable minWidth={800}`, `lazyModal()` + `Suspense`, mounted only when open. The
     backend is `GET /{id}/<children>`, `POST /{id}/<children>` (a list of ids) and
     `DELETE /{id}/<children>/{childId}` on the parent's controller, gated on the parent's `:edit` — **no
     new permission, no new screen id, no grid of its own**. On a dated junction *remove* is **End link**
     (`PATCH /{id}/<children>/{linkId}/end` sets `effective_to`, never deletes). **Copy these, do not
     redesign them** (classic repo):
     - platform Users — `platform/frontend/src/components/userManagement/UserManagementTable.tsx:695-701`
       (the button), `platform/frontend/src/app/dashboard/admin/users/page.tsx:22,423,1006-1012`,
       `UserBranchesModal.tsx`
     - dealer PDI Stock Yards — `dealer/frontend/src/components/pdi-stock-yards/PdiStockYardManagementTable.tsx:599-611`,
       `dealer/frontend/src/app/dealers/pdi-stock-yards/page.tsx:20-21,668-698,1019-1032`,
       `PdiStockYardCompaniesModal.tsx`, `PdiStockYardBranchesModal.tsx`,
       `dealer/backend/src/main/java/ai/dealer/controller/PdiStockYardController.java:535-632`
     - automotive Companies — `automotive/frontend/src/components/companies/CompanyBranchesModal.tsx` over
       `CompanyAssignmentModal.tsx`, `automotive/backend/src/main/java/ai/automotive/controller/CompanyController.java:423-464`

     A tab that edits a record's **own child rows** stays a child editor, as on the existing pages:
     counterparty roles, addresses and tax registrations (WS-021), item identifiers, packaging and
     category-per-scheme (WS-023), lot parties (WS-036). A lifecycle transition keeps its own modal
     (*Change registration*). **The rule applies to WS-015 *Branches*, WS-016 *Branches* and *Companies*,
     WS-017 *Custody*, WS-019 *Companies*, WS-173 *Places of business*, and every future pure link-set.**
   - **c. A warehouse and an owner link to companies; neither carries `company_id`.**
     `whb_warehouse_companies` (`OPERATOR`/`STOCK_HOLDER`, one current `OPERATOR`) and
     `whb_owner_companies` (`HOUSE`/`SERVICED_BY`, one current `HOUSE` owner per company) move from v2
     to **v1**, and `whb_warehouses.company_id` and `whb_owners.company_id` are dropped once backfilled.
     Create writes the first company link in the same transaction, as it writes the `REGISTERED` branch.
     The movement company assertion (`RG-012`) reads a `STOCK_HOLDER` link at `occurred_at`, and a
     transfer's two sites must both hold a current link to its company (`RK-007`). This takes the
     warehouse and owner parts of `FR-468` into v1.
   - **d. Codes are unique across the install** on `whb_warehouses` and `whb_owners` — `uk(code)`, as
     platform `branches.branch_code` is. This supersedes `RL-004` for these two tables only; locations
     stay `uk(warehouse_id, code)` and LPNs stay install-wide. House owners sharing the seeded code `HOUSE`
     are renamed `HOUSE-<company code>` before the key is added (a single-company install keeps `HOUSE`),
     and the migration refuses to run while any other duplicate code exists.
   - **e. A branch belongs to one company at a time.** `whb_company_branches` gains
     `EXCLUDE (branch_id =, range &&)`. The round-4 constraint only refused the same pair twice, while
     WS-016's branch options and `422 WAREHOUSE_BRANCH_COMPANY_MISMATCH` already read *"the branch's
     company now"* as one answer.
   - **f. Built work is corrected by one task, `P1-22`**, because closed tasks are never reopened. Its
     migrations are forward-only — `V500073` (reassigned from `P0-06`), `V500078`, `V500079` — and no
     applied migration is edited.

### D-15 · A posted moving average is never restated; a backdated receipt inserts a layer

**User decision, taken 2026-09-11**, on round 3's `RF-001` (`GAP-REGISTER-R3.md` §2.6 and §5.1). It
was adopted with the `GLOBAL-SETTINGS-DECISIONS.md` pass and folded into `P2-16` by lane `W0-1b`.

1. **`moving_average_after` on a movement line is a snapshot** of the weighted average at the moment
   that line posted (`IRR-39`). It is never restated.
2. **A backdated receipt inserts a cost layer.** The *current* average is
   `Σ open layer_value / Σ open quantity_remaining`, computed on read from `whb_cost_layers` and never
   stored.
3. **`I-2`'s line allowlist stays `'{}'`.** `V500030` ships it that way, so nothing about this decision
   needs a column added after `PNR-1`.
4. **FIFO follows the same rule.** A backdated layer is consumed by **future** issues only. Consumptions
   already written are never re-drawn, because `L-2`/`L-3` make a correction a reversal and `P4-04`'s
   ITC reversal walks that link.
5. **Falsifier:** post a backdated receipt, re-read a following movement line, and assert that its
   `moving_average_after` is byte-identical.

`P0-02` and `P2-16` carry it, and `WH-SC-151` asserts it. Restating was the alternative: it would have
grown `I-2`'s allowlist by a sixth column in `V500030`, and it was declined.

---

## 3. OD — open decisions. Each names its deadline and who decides.

> **State, 2026-09-03.** Fifteen rows stood open through three review rounds with nothing in the fourth column but a
> *Recommendation*. **Nine are now decided**; **four** (`OD-1`, `OD-3`, `OD-8`, `OD-9`) are **escalated** as business
> calls; **two** (`OD-2`, `OD-4`) stay open **by schedule** for v3; and **two** — `OD-16`, `OD-17` — were allocated on
> this date by round 3 and escalated with them. Seventeen rows, none deleted: a resolved decision changes state and
> names the file that carries its evidence,
> [`OPEN-DECISIONS-RESOLVED.md`](OPEN-DECISIONS-RESOLVED.md).
>
> **2026-09-10.** Round 4 allocated **`OD-18`** and **`OD-19`**, both escalated (§3.5). Nineteen rows now stand.
>
> **The sorting rule, stated so it can be applied again:** a recommendation is *technical* — and is adopted here —
> when this design set can execute it inside this repository. It is a *business call* — and is escalated — when it
> asks another team to build something, another repository to change, a segment to be served or declined, or the v1
> cut line to move.

```bash
# the rows whose DEADLINE CELL (field 4) gates P0-02 / PNR-1 = V500030, the migration
# that cannot be taken back. The cell is read, not the whole row: OD-16's deadline mentions
# V500030 in passing and is not one of these gates (DECISIONS.md sec 7 rule 8).
awk -F'|' '/^\| \*\*OD-/ && $4 ~ /[Bb]efore [^.;]*(P0-02|PNR-1)/ {gsub(/[*` ]/,"",$2); printf "%s ", $2}' docs/DECISIONS.md
# -> OD-10 OD-12 OD-14 OD-11 OD-7 OD-1   -- six, not five
```

`S-035` — **pharma: serve regulated goods or decline the segment in writing** — is escalated alongside these. It is a
finding rather than an `OD-` row and it stays in `GAP-REGISTER.md` §5.1 as the design set's one **unowned BLOCKER**;
it is not renumbered here, because a finding is a dated record. See [`OPEN-DECISIONS-RESOLVED.md`](OPEN-DECISIONS-RESOLVED.md) §3.1.

### 3.1 Resolved — the nine technical decisions

| # | Decision | Deadline it cleared | Resolution |
|---|---|---|---|
| **OD-10** | **Is MRP a dimension of the stock position?** `FR-321`. If two MRP-labelled batches of one SKU must never merge, MRP joins the position unique key — and that key is set at `PNR-1`, warehouse's first point of no return | **Before `PNR-1`** (migration `V500030`) — this is the tightest deadline in the set | **RESOLVED 2026-09-03 · No.** MRP belongs on the **lot**, not on the position key; the `L-5` key stays at nine members. A tenth member widens the unique index, every position row and the `L-4` rebuild, and can never be removed; an MRP that turns out to be needed is reachable through the lot. `P4-05`'s report reads it from there, and an item whose MRP is segregated is by definition batch-tracked. Record, reasoning and owed edits: [`OPEN-DECISIONS-RESOLVED.md`](OPEN-DECISIONS-RESOLVED.md) §2 |
| **OD-12** | **The `whb_stock_movements` partition key — `occurred_at` or `posting_date`?** `FR-022` and `DATA-MODEL.md` `WHB-30` specify `PARTITION BY RANGE (occurred_at)`; `PLATFORM-DEPENDENCIES.md` `PD-D5` recommends `posting_date`. `L-13` makes these different columns, so the choice is real: `occurred_at` is what the as-at query and EPCIS want, `posting_date` is what period close and the statutory register want | **Before `PNR-1` (migration `V500030`)**, which is also `PNR-2`. A partition key cannot be added to a populated table without a rewrite | **RESOLVED 2026-09-03 · `occurred_at`.** As `FR-022` and `WHB-30` specify and `issues/p0-02.md` already builds. The as-at query and the `L-4` rebuild run constantly and range over `occurred_at`; period close runs monthly and reads `posting_date` through a btree index declared in the same migration. **`PD-D5`'s argument is real and is accepted as a cost, not denied**: `occurred_at` is producer-supplied, so late arrivals write into historical partitions and **no partition is ever closed**. `PLATFORM-DEPENDENCIES.md` `PD-D5` must be amended, not left standing. Record: [`OPEN-DECISIONS-RESOLVED.md`](OPEN-DECISIONS-RESOLVED.md) §2 |
| **OD-14** | **Is value conservation a fifteenth invariant (`L-15`) or a movement-type behaviour column?** `PC-12` states the question and explicitly refuses to decide it. `DECISIONS.md` §4 stops at `L-14` and `DATA-MODEL.md` §6.3 stops at `I-20`; neither carries a value-conservation row, and `P2-17`, `P2-28` and `P3-11` all depend on the answer | **Before `P0-02`**, because the guard is a constraint on the table | **RESOLVED 2026-09-03 · A fifteenth invariant `L-15`**, scoped to `quantity = 0 AND unit_cost IS NOT NULL`, with a matching `I-21` in `DATA-MODEL.md` §6.3, both sitting in `V500030`. Not a behaviour column: a `value_balance_rule` puts the ledger's correctness in data any migration or support script can edit. A movement mixing zero- and non-zero-quantity lines is refused — it is two movements. **The `L-15` row is owed to §4 and the `I-21` row to `DATA-MODEL.md`; both are stated verbatim in** [`OPEN-DECISIONS-RESOLVED.md`](OPEN-DECISIONS-RESOLVED.md) §2 |
| **OD-11** | **Do value-only movements conserve value?** `PC-12`: `L-1`…`L-14` conserve **quantity** only, and a landed-cost movement posts `quantity = 0` with a value. `FR-084`'s seeded virtual-location list has no value-offset row | **Before `P0-02`.** *(Corrected 2026-09-03: this cell read "Before `P2` valuation". `PORT-AND-ADAPTER-CONTRACT.md` §12.2 row 3 and `IMPLEMENTATION-PLAN.md`:1319 both say before `P0-02`, and the tighter deadline wins — a conservation invariant is a constraint on the table, not on a report. This correction is why the `P0-02` gate set computes as **six**, not five.)* | **RESOLVED 2026-09-03 · Yes.** A `VALUE_OFFSET` virtual location (`OD-13`) carries the counter-side and `L-15` (`OD-14`) is the invariant that makes it testable. This is `D-4` applied to the value column: a one-line "movement" is the single-sided log `D-4` exists to refuse, is not reversible under `L-3` and is not rebuildable under `L-4`. Record: [`OPEN-DECISIONS-RESOLVED.md`](OPEN-DECISIONS-RESOLVED.md) §2 |
| **OD-7** | **Precision.** Quantities `DECIMAL(18,4)`? Money `DECIMAL(19,4)`? Per-unit cost `DECIMAL(19,6)`? Percentages `DECIMAL(9,6)`? Accounting took a CLAUDE.md deviation for exactly this and the percentage row was stated wrongly for three rounds | Before `P0-02` | **RESOLVED 2026-09-03 · Adopt accounting's resolved set verbatim, by citation** — `accounting/docs/OPEN-DECISIONS-RESOLVED.md` `OD-7`, including the corrected `DECIMAL(9,6)` for percentages and both tie-breaks (`unit_*` beats `value`; `_percent` beats "rate"; `DECIMAL(19,8)` is the currency-conversion type and nothing else). **One warehouse-only row is added**: `conversion_factor_used DECIMAL(18,8)`, a sixth named kind — it cannot be `DECIMAL(9,6)` (1 tonne = 1,000,000 g) and must not be `DECIMAL(19,8)` (reserved). **The display rule is decided with it**, as `PLATFORM-DEPENDENCIES.md` §2.11 requires. Record: [`OPEN-DECISIONS-RESOLVED.md`](OPEN-DECISIONS-RESOLVED.md) §2 |
| **OD-13** | **The value-offset virtual location's code.** `OD-11` and `P2-28` call it `VALUE_OFFSET`; `PORT-AND-ADAPTER-CONTRACT.md` `PC-12` calls it `LANDED_COST_OFFSET` and offers reuse of an `ADJUSTMENT_OFFSET`-typed location. **`FR-084`'s seeded list contains none of the three** | **Before `P1-05` writes `V500013`** — the seed migration | **RESOLVED 2026-09-03 · `VALUE_OFFSET`**, added to `FR-084`'s seeded list as an eleventh code and seeded by `P1-05`'s `V500013`. It does not presume *why* the value moved — revaluation, standard-cost variance and assembly completion post value with no quantity too. **Reusing `ADJUSTMENT_OFFSET` is refused**: it would merge quantity adjustments and value-only postings behind one counter-side that no query separates afterwards. **`PC-12`'s `LANDED_COST_OFFSET` must be amended, not left standing.** Record: [`OPEN-DECISIONS-RESOLVED.md`](OPEN-DECISIONS-RESOLVED.md) §2 |
| **OD-6** | **Valuation method scope in v1** — FIFO + weighted average + standard, or weighted average only? *(Who owns the layers is no longer open: **D-6** settles it — whichever system is authoritative for quantity is authoritative for cost, so with warehouse installed the layers are `whb_cost_layers`.)* | Before `P2` valuation tasks | **RESOLVED 2026-09-03 · Weighted average + FIFO in v1**, `whb_cost_layers` present (its DDL is `P0-17`'s `V500021` regardless), method configurable per item category × site; **standard cost with variances in v1.1**; **LIFO never built** — and, because `D-10` makes the method vocabulary an open catalogue with no CHECK, **never seeded either**. `IRR-40`'s *valuation grain* declaration is **not** discharged by this and remains owed to `P0-17`. Record: [`OPEN-DECISIONS-RESOLVED.md`](OPEN-DECISIONS-RESOLVED.md) §2 |
| **OD-15** | **Is the union valuation report (`M3`) built?** With `accessories` permanently separate (`D-9`), a finance user asking *"what is my total stock value"* gets two numbers. R3 `M3`/`E-084` says build one report that unions them; R7 §4.6 item 4 says do not, and document the separation in the UI instead | **Before `P2-20` and `P2-27` merge** — the deadline has arrived | **RESOLVED 2026-09-03 · Do not build the union in v1.** `P2-27` ships reports over warehouse stock only, with the separation stated on the report header and in `D-9`'s cost note; revisit at v2 if a customer asks. A union whose halves use different valuation methods states a total that reconciles to nothing — `accessories` has no cost layers and its balance is not derivable from its own movements. **`D-9`'s two mandatory mitigations are unaffected**: detectability is preserved, only the false total is refused. `COEXISTENCE.md`'s `M3` row must be restated, not deleted. Record: [`OPEN-DECISIONS-RESOLVED.md`](OPEN-DECISIONS-RESOLVED.md) §2 |
| **OD-5** | **Does the frontend re-close the vocabularies the backend opens?** CLAUDE.md TYPESCRIPT RULE #6 mandates string-union types over enums; D-10 mandates open catalogues. These conflict, and R2 records it as a *documented recurring defect* in this codebase | Before the first warehouse page is written | **RESOLVED 2026-09-03 · The frontend does not re-close them.** A catalogue-backed dropdown **fetches** its values; a TypeScript string union is permitted **only** for a closed system vocabulary the product itself defines and no install may extend (e.g. `posting_status`). If the vocabulary is one of `D-10`'s thirteen catalogue tables, a union is a defect. `FR-380` is the rule and this is the ruling that gives it a test. **The CLAUDE.md rule #6 carve-out is owed to the standards owner in a different repository and does not block a warehouse page**, because a page that fetches its values violates nothing today. Record: [`OPEN-DECISIONS-RESOLVED.md`](OPEN-DECISIONS-RESOLVED.md) §2 |

### 3.2 Escalated — the business calls. Recommendation attached; **not** taken here

| # | Decision | Deadline | Recommendation · why it is not ours to take |
|---|---|---|---|
| **OD-1** | **The reciprocal accounting edits.** D-6 requires `accounting` to stand down `acc_stock_balances`, `acc_physical_stock_counts`, `acc_stock_journals`, `acc_cost_layers`' quantity grain and the port's `unit_cost` semantics when warehouse is installed. That is an edit to a *different* repository's design set (`neetub1508/accounting`, phase P3, tasks not yet built) | **Before accounting's `P1-04` ships `V600136`/`V600137`** — the schema lands in accounting's **P1**, not its P3 (`accounting/issues/p1-04.md:5,13,15`; `accounting/docs/DATA-MODEL.md:4291`). *(Corrected 2026-09-03 from "Before accounting's P3", per round 2's `O-001`.)* And before warehouse `P0-02` writes `whb_stock_movements` | **RESOLVED 2026-09-11.** Warehouse owns quantity and cost. Default STANDALONE; INTEGRATED requires an installed, tested accounting adapter that accepts authoritative extended values and stable idempotency keys. Missing capabilities block activation, not standalone stock posting. Reciprocal work in another repository remains an external integration dependency, not an unanswered warehouse decision. [Contract](GLOBAL-SETTINGS-DECISIONS.md). |
| **OD-9** | **Does `warehouse` carry a tax engine, or never compute tax?** `FR-325` has warehouse carrying one; `FR-294` and R3 `D4` say warehouse never computes tax. This decides whether 6 `whin_` tables exist — the India pack is **50 or 56 tables** depending on the answer | **Before `P2-25`**, not before `P2-IN` — `P2-25` builds the v1 table that implements the rejected option (`U-003`), so the rejected option is being built while the decision is open. *(Corrected 2026-09-03; the FRD §9 row already carried the tighter deadline.)* Gates `P2-IN-01` **and** `P4-01` | **RESOLVED 2026-09-11.** Warehouse does not implement its own tax calculation engine. PROVIDER uses a tested accounting/localisation provider; MANUAL_EVIDENCE records an externally issued document and its totals; NONE permits only operations requiring no tax document. Never silently treat missing tax as zero. Conditional engine schema remains documented as reserved history, with no active build obligation. [Contract](GLOBAL-SETTINGS-DECISIONS.md). |
| **OD-3** | **One database per customer, or shared multi-tenancy?** `grep -ril "tenant" platform/backend/src/main/java` → **0 files**. Classic is one-DB-per-customer today, which is why a 3PL's clients must be an **owner dimension**, not tenants | Before `warehouse-3pl` P5 starts | **RESOLVED 2026-09-11.** One database per customer installation. A 3PL client is an owner with enforced row scope, never a database tenant. Configuration export/import is supported through the existing task with identifier remapping and no secrets. [Contract](GLOBAL-SETTINGS-DECISIONS.md). |
| **OD-8** | **How does an out-of-process consumer authenticate to the port?** `PORT-AND-ADAPTER-CONTRACT.md` `PC-33`: a `logistics` module deployed separately has nothing to authenticate with. There is no API-key table in platform (grep → 0); the only API-key path in the repo is per-handler inside the boom-barrier webhook | Before `P0` builds the port, because the auth model shapes the endpoint | **RESOLVED 2026-09-11.** Use existing authenticated users and movement permissions in v1. Separate service consumers remain capability-gated to the v3 identity adapter with revocation, scope and audit tests. No anonymous/API-key shortcut and no warehouse-owned duplicate identity store. [Contract](GLOBAL-SETTINGS-DECISIONS.md). |

### 3.3 Open by schedule — v3, and deliberately not decided in a v1 wave

| # | Decision | Deadline | Recommendation |
|---|---|---|---|
| **OD-2** | **Does the dealer *vehicle* inventory (`pdi_vehicle_inventory`, `pdi_stock_yards`, `pdi_yard_storage_locations`, `pdi_storage_slot_assignments`) migrate onto the warehouse ledger?** A vehicle is a serial-controlled item in a location; the model fits. But it is a shipped, load-bearing dealer workflow | v3 planning, not before | **RESOLVED 2026-09-11.** Keep vehicle inventory in its existing authority in v1/v2. In v3 offer an opt-in adapter only after serial, custody, reconciliation, rollback and source-write-exclusion acceptance passes. No automatic migration and no dual writer. [Contract](GLOBAL-SETTINGS-DECISIONS.md). |
| **OD-4** | **Who owns the shared supplier/counterparty master long-term?** `warehouse-base` owns `whb_counterparties` in v1 because nothing else does (`asset_vendors` is assets-owned; accessories receiving has no supplier field at all). If a supply-chain module is built in v3 it will want one too | v3 | **RESOLVED 2026-09-11.** warehouse-base keeps its counterparty master. Other products join through external references; no upward foreign key. A future extraction must preserve identifiers and port compatibility; it is not a customer toggle. [Contract](GLOBAL-SETTINGS-DECISIONS.md). |

### 3.4 Allocated 2026-09-03 by round 3 — open, escalated, and both move the v1 cut line

Round 3's lenses (`reviews/R16`–`R21`, §6) produced two BLOCKERs that are not defects in a document but gaps in the
**v1 cut line**. `DECISIONS.md` §3 owns the `OD-` namespace and no other document may allocate, so they are numbered
here. Both are escalated: `D-12` makes the cut line a product decision.

| # | Decision | Deadline | Recommendation · why it is not ours to take |
|---|---|---|---|
| **OD-16** | **v1 foreign-currency costing has no exchange-rate source, no field on the wire to carry one, and no statement of which currency the stored numbers are in.** `FR-245` and `WH-SC-160` are **v1** and carry a concrete rate; `PORT-AND-ADAPTER-CONTRACT.md:280-282` has no `exchange_rate` wire field; `cost_currency_code` is marked *"column v1, multi-currency v2"*. `PLATFORM-DEPENDENCIES.md` §2.12 states the problem, offers two options, **decides neither**, and is **not an `OD-` row**, so nothing gives it a deadline or an owner. Source: `RF-004`, which explicitly recommends promoting it | **Before `P0-17` writes `V500021`** (the `whb_cost_layers` DDL, which itself precedes `V500030` per `WHB-21`); `IRR-36` puts `cost_currency_code` on the line at `PNR-1`, so the earlier of the two binds. **Gates `P2-16`** and the column set of `P0-17` | **RESOLVED 2026-09-11.** Stored unit_cost and layer_value are in company base currency. Preserve original currency, original amount, positive exchange_rate and rate evidence on the source snapshot; rate is base units per one original-currency unit and is frozen at post. Only base-currency input may default to rate 1. SOURCE_RATE is the standalone default; PROVIDER_RATE is optional after capability validation. No direct read of accounting tables. [Contract](GLOBAL-SETTINGS-DECISIONS.md). |
| **OD-17** | **v1 prints a GS1-128 pallet label carrying an SSCC that v1 cannot allocate and cannot read back.** Three version cells, each defensible alone, do not compose: `FR-225` and `WH-SC-203` put the GS1-128 LPN label in **v1/P2** and `issues/p2-14.md` accepts *"encodes AI `00`"* — AI `00` **is** the SSCC; `FR-452` puts the allocator (`whb_gs1_settings`, `whb_gs1_serial_counters`, `V500056`) in **v1.1/P3**; `FR-063`'s GS1 element-string parsing is **v1.1/P3**, so v1 hands the string to a resolver that logs it unresolved. No document in the set reads two of the three together. Source: `RD-001` | **Before `P2-14` merges** — the moment a template ships is the moment the first label is printed, and `FR-064` records that a printed label cannot be recalled | **RESOLVED 2026-09-11.** v1 ships an internal Code-128 LPN label encoding lpn_code and resolvable by the v1 scanner. GS1-128/SSCC is an optional v1.1 capability enabled only when the existing allocator and parser tasks both pass. All eleven document kinds remain in v1; GS1 symbology is not falsely promised in v1. Existing labels remain resolvable after a setting change. [Contract](GLOBAL-SETTINGS-DECISIONS.md). |

### 3.5 Allocated 2026-09-10 by round 4 — open and escalated

Round 4's lenses (`reviews/R22`–`R26`, §6) produced two questions that a person must answer. They are numbered here,
because this section owns the `OD-` namespace. After them, nineteen rows stand and the next free id is `OD-20`. Neither
blocks the fold of round 4: each has a safe default already written into the design. Disposition:
[`GAP-REGISTER-R4.md`](GAP-REGISTER-R4.md) §5.

| # | Decision | Deadline | Recommendation · why it is not ours to take |
|---|---|---|---|
| **OD-18** | **What does the product record for a drop-shipment?** A drop-shipment is goods bought from a supplier and shipped by that supplier straight to a customer, never touching a warehouse. R7 asked for a decision in v1 with the implementation in v2 (`G-037`); nothing decided it. The movement model has one answer that costs nothing now — a virtual-to-virtual movement — but the product must say what it claims to track. Source: `RK-005` | Before the first purchase of a drop-shipped part is posted in any install; the v2 posting itself is built by `P5-09`, which is blocked on this row | **RESOLVED 2026-09-11.** v2 drop shipment uses a SUPPLIER-to-CUSTOMER virtual movement with purchase and demand line references and required lot/serial evidence, without changing physical on-hand. Default disabled; refuse in v1 or when the adapter is unavailable. Receipt/dispatch confirmations are idempotent and reversal follows the original links. [Contract](GLOBAL-SETTINGS-DECISIONS.md). |
| **OD-19** | **What is the statutory treatment of on-hand stock when a site's `REGISTERED` branch moves to a branch under a different GSTIN?** `D-14` makes a registration change a dated history event. Goods held at that instant move from one registration to another, and the design set cannot say whether that is a supply, a transfer of a going concern, or an amendment of the place of business. Source: `RG-001` (R22 §1.2.6) | **Before `P1-05` ships the *Change registration* action** on `WS-016`. The history table itself (`V500012`) does not wait: it is correct under every answer | **RESOLVED 2026-09-11.** Changing registered branch across GSTINs is allowed only with zero on-hand and no open reservations, in-flight transfers, counts or unposted warehouse documents tied to the old registration. Otherwise refuse with actionable dependency links; use the existing transfer/settlement workflow. Maker-checker and effective history are mandatory; there is no bypass switch. [Contract](GLOBAL-SETTINGS-DECISIONS.md). |

## 4. L — the load-bearing invariants

Get these wrong and everything after is built on sand. Each has **a database guard and a service
guard**; the service guard rejects first, in the transaction, with a field-level error, and the
database guard is the backstop for the paths the service does not own (a migration, a support script,
a second writer, direct SQL). **A trigger firing in production is an incident, not a validation.**

| # | Invariant | Enforced by |
|---|---|---|
| **L-1** | **Conservation.** Every movement's lines sum to zero in base UoM per (owner, item, lot, serial, duty status). A receipt or an issue balances against a **virtual location**, never against nothing | deferred constraint trigger + service pre-check |
| **L-2** | **Append-only.** No posted movement line is ever UPDATEd or DELETEd. Three layers: one writer service with no update method, a `to_jsonb`-diff trigger rejecting `INSERT` into a posted movement as well as `UPDATE`/`DELETE`, and no repository path | service + trigger + code review |
| **L-3** | **Correction is reversal** — mirrored lines, a mandatory reason code from the catalogue, the original marked reversed, a single-set link. "Edit" is never offered anywhere in the product | service |
| **L-4** | **Positions are a cache.** A full rebuild from `whb_stock_movements` reproduces every `whb_stock_positions` row **exactly**. A nightly job proves it and alerts on drift | nightly rebuild + drift alert |
| **L-5** | **Full-grain key.** A position is keyed by `(company, owner, item, location, lot, serial, lpn, stock_status, duty_status)`. Every one of those columns exists in v1 even where its feature ships later | unique index |
| **L-6** | **Allocations cannot exceed free stock; negative physical on-hand is an explicit policy.** Signed balance remains visible; ATP = max(0, allocatable on-hand minus open reservations). Clamp never authorizes a reservation or consumes another holder's stock. BLOCK default; WARN/ALLOW follow the adopted configuration contract | transactional service + allocation guards |
| **L-7** | **Quantity is stored in base UoM with the conversion factor frozen on the line.** A ledger that re-derives from today's factor silently restates last year | CHECK + service |
| **L-8** | **Period-bound.** A movement into a locked period is refused, including a reversal. A soft-close needs an approved override; a hard close admits nothing | trigger with session-GUC gating |
| **L-9** | **Ingestion is idempotent.** `(source_system, idempotency_key)` is unique; a repeat returns the original movement and posts nothing. The key is **never** server-generated | unique index + service |
| **L-10** | **Allocation is an open-item ledger**, not a counter. Every reservation is a row with a holder quad `(holder_system, holder_document_type, holder_document_id, holder_line_no)` and an `expires_at`, so "release everything trip X held" is answerable | service + FK |
| **L-11** | **Ownership never changes silently.** A title transfer is an explicit movement type with its own reason code — goods can change owner without moving, and can move without changing owner | movement-type catalogue + service |
| **L-12** | **Traceability is reconstructible in both directions.** Every movement resolves to a source-document quad; lot and serial genealogy is answerable forward (where did this lot go) and backward (what went into this unit) for the full retention period | schema + report + test |
| **L-13** | **Three timestamps, never one:** `occurred_at` (producer-supplied, when it physically happened), `recorded_at` (when we heard), `posting_date` (the accounting date). One timestamp cannot be split later, and collapsing them kills offline replay, degraded-mode catch-up, cut-off and EPCIS simultaneously | NOT NULL columns |
| **L-14** | **Non-own stock is never valued.** `owner_type != OWN` hands over for quantity and custody reporting only. What we carry for it is a custody liability and an insured value — a different number, on a different report | service + handover contract |
| **L-15** | **Value-only movements conserve signed extended value by currency.** All quantity is zero and value is explicit; VALUE_OFFSET balances the posting. Mixed quantity/value-only movements are refused | deferred constraint + service |

---

## 5. The version ladder — all versions defined now

Per **D-12**, nothing is left undefined. Phases are the delivery unit; versions are the release unit.

| Version | Phases | What it is | Exit criterion |
|---|---|---|---|
| **v1** | **P0** ledger foundation · **P1** masters, identity, inbound · **P2** outbound, counting, valuation, returns, printing, reports | The stock ledger and inventory control: multi-site/bin stock at full grain, items & UoM, lots/expiry/serials, receiving & QC & putaway, allocation & pick/pack/dispatch, transfers with in-transit, adjustments, cycle & physical counts, costing & valuation, reorder, **basic returns**, **printing**, **the India movement documents**, the reports, **and the dealer-parts + services adapters** | On a **standalone** install (platform + `warehouse-base` + `warehouse`, no vertical, no accounting) a storekeeper creates a site, generates a bin grid, imports an item master and opening stock, receives against a purchase document, puts away, allocates and picks an order, ships it with a printed pick list and delivery document, takes a customer return back into stock, transfers stock to a second site through in-transit, counts a zone and posts the variance, and produces a stock ledger, a position report and a valuation report **that reconcile to each other and to a full ledger rebuild** |
| **v1.1** | **P3** execution & mobile | The warehouse floor: RF/handheld task flows, task management & priority, wave planning & release, batch/cluster/zone picking, packing & cartonisation, the print server & device management, dock appointments, van stock, the field-service and assets adapters | An operator completes a full receive→putaway→pick→pack→ship cycle **entirely on a handheld**, and a wave of 200 order lines releases, picks and ships with task interleaving |
| **v2** | **P4** India statutory & compliance · **P5** 3PL, channels & reverse logistics | Sellable as a compliance product and to a 3PL: job work & ITC-04, the Rule 56 stock account, MRP & Legal Metrology, bonded/MOOWR, the regulated-goods packs; owner-of-goods billing, rate cards, storage & handling meters, the client portal, channel/marketplace order intake, carrier integration, full reverse logistics, NDR/RTO/COD | A 3PL bills a client for a month of storage and handling from metered events, and a customer files ITC-04 and the Rule 56 stock account from warehouse data |
| **v3** | **P6** optimisation, planning & the logistics seam | Slotting, replenishment optimisation, labour standards, ABC/XYZ & velocity, demand & reorder planning, supplier scorecards, EPCIS/GS1 event capture, automation interfaces, control-tower analytics — **and the `logistics` module itself**, consuming `warehouse-base` through the port with zero commits to it | The `logistics` module ships trips, ePOD and freight settlement, moves stock through the port, and `warehouse-base` has not been edited to allow it |

**Adapter schedule:** dealer-parts **v1** (proves the port) · services **v1** (proves genericity —
one adapter proves nothing) · field-service and assets **v1.1** · logistics **v3** · accessories
**never** (D-9).

### 5.1 · Four amendments to the ladder, taken 2026-09-01 after the first authoring wave

Four documents came back arguing the same cut lines were wrong. Three are accepted, one is refined.
Each is recorded here because a later reader will otherwise find a review and the ladder disagreeing
and not know which won.

| # | The argument | Verdict |
|---|---|---|
| **A-1 · Returns move to v1** | R2, R3 and R4 all placed RMA at v1/v1.1; the ladder had all reverse logistics in v2. *"A stock product with no return path at v1 is not credible in any segment"* — and a customer return that cannot be received is a stock movement the ledger simply loses | **Accepted.** **Basic returns are v1/P2**: sales-return receipt, purchase return / return-to-vendor, and disposition to a stock status (restock · quarantine · scrap). **Full reverse logistics stays v2/P5**: RMA portal, grading & refurbishment, credit interface, NDR/RTO/COD |
| **A-2 · Printing moves to v1** | R5 ranks it ship-blocker #2, and `grep -rli "zpl\|escpos\|dymo"` across all Java/TS returns **0** — there is no label or document rendering anywhere in this codebase. A warehouse that cannot print a pick list, a GRN, a delivery document or a bin/product label cannot be operated | **Accepted.** **Templated document and label printing is v1/P2**, including a ZPL path, because it is net-new infrastructure with no precedent and a v1 without it loses to a spreadsheet and a Dymo. **The print server, printer routing and device management stay v1.1/P3** |
| **A-3 · Item variants are v1 schema** | R5 `S-056` calls the style × variant matrix v1 schema; R2/R3 place it at v2. Apparel and footwear is the largest Indian segment we would otherwise decline, and a flat SKU model is **unrecoverable** — it is a re-keying of the item master and every movement that references it | **Accepted, as schema only.** The variant model (`style`/parent item, variant axes and values) is **v1 schema** under the same rule as `owner_id` (D-5); the **matrix screens, grids and reports are v2**. This is the 47-requirement pattern the FRD already uses: the column lands in one version, the screen in a later one |
| **A-4 · India splits in two** | R3 and R5 mark the delivery challan, the e-way bill and the GST-aware transfer document as **v1 BLOCKERs**; the ladder put all of India in v2. In India goods physically cannot move between branches without them, so a v1 that ships transfers but no challan ships a transfer feature an Indian customer may not legally use | **Accepted, refined.** `warehouse-india` still exists as a module (D-1) and still ships country-neutrally (D-8), but it lands in **two waves**: **v1/P2-IN — the documents required to move goods legally** (delivery challan, e-way bill payload and generation, the GST-aware transfer document, HSN on the item, cross-GSTIN transfer as a supply). **v2/P4 — the statutory registers and filings** (Rule 56 stock account, ITC-04 and job work, MRP & Legal Metrology, bonded/MOOWR, the regulated-goods packs). The v1 wave is small, self-contained, and is the difference between a demo and a deployment |

---

## 6. Id namespaces — disjoint by construction

<!-- check-design-set: screen-citations begin WS-242 WS-245 — the BUILD-SPEC-SCREENS.md §1 allocation marker and the id reserved ahead of it: WS-242 reserved for P5-13's marketplace-claim queue, WS-245 the next free. Neither has a row yet; named so a new screen takes the marker instead of reusing another screen's grid -->

The accounting set's most expensive defect was three different things sharing one namespace, which a
late rename could not repair because a blanket search-and-replace corrupted the decisions table twice.
That cannot happen here.

| Kind | Namespace | Authority |
|---|---|---|
| Tasks | **`P0-01` … `P6-nn`** | `issues/pN-nn.md` — the file glob is the count |
| Requirements | **`FR-001` …** | `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` |
| Decisions | **`D-1` …** | this file |
| Open decisions | **`OD-1` …** | this file |
| Invariants | **`L-1` … `L-14`** — plus **`L-15`, allocated 2026-09-03** by `OD-14` and **owed into §4**, which still stops at `L-14`. The row is written verbatim in [`OPEN-DECISIONS-RESOLVED.md`](OPEN-DECISIONS-RESOLVED.md) §2 so the later wave transcribes rather than re-derives it | this file |
| Enforceable constraints | **`I-1` … `I-20`** — plus **`I-21`, allocated 2026-09-03** by `OD-14` as `L-15`'s database guard and **owed into `DATA-MODEL.md` §6.3**, which still stops at `I-20`. Allocating it here rather than there is deliberate: §6 is the allocation, and an id claimed in two places is the collision this table exists to prevent. **`I-22`, `I-23`, `I-24`** were **allocated 2026-09-10** by `GAP-REGISTER-R4.md` §4.0 and are owed into §6.3 after `I-21`: `I-22`, a movement at an instant with no `REGISTERED` link is refused (`V500030`); `I-23`, the `REGISTERED` history is exclusive and append-only (`V500037`); `I-24`, a rule row that a reservation or task references is immutable (`V500031`, `V500033`, `V510017`) | `DATA-MODEL.md` §invariants-as-SQL |
| Irreversible rows | **`IRR-01` … `IRR-63`** — plus **`IRR-64` … `IRR-67`, allocated 2026-09-10** by `GAP-REGISTER-R4.md` §4.0 and owed into `IRREVERSIBLE.md` §2: registration history, v1 junction history, the outbox event schema, and non-ledger partitioning at `CREATE`. The next free is `IRR-68` | `IRREVERSIBLE.md` §2 |
| Scenarios | **`WH-SC-001` …** | `SCENARIO-CATALOGUE.md` |
| Screens | **`WS-001` … `WS-237`** — **`WS-238`** *Warehouse Grants* was **allocated 2026-09-11** to round 3's `RA-001` (`P1-18`). The same day's second fold (lane `W0-1b`) allocated **`WS-239`** *Item Prices* (`RA-002`, `P2-25`), **`WS-243`** *Location Utilisation* (`RC-009`, `P6-02`) and **`WS-244`** *Metric Targets* (`RC-007`, `P2-21`), and **reserved `WS-242`** for `P5-13`'s marketplace-claim queue. **`WS-240`** *Trade Portal* and **`WS-241`** *Approval Levels* were **allocated 2026-09-10** by `GAP-REGISTER-R4.md` §4.0 | `BUILD-SPEC-SCREENS.md` §1 — the index is the allocation; the next free is `WS-245` |
| Findings — R1 codebase reality | **`C-001` … `C-050`** | `reviews/R1` |
| Findings — R2 tier-1 WMS | **`T-001` … `T-097`** | `reviews/R2` |
| Findings — R3 ERP / mid-market | **`E-001` … `E-090`** | `reviews/R3` |
| Findings — R4 fulfilment / 3PL | **`F-001` … `F-093`** | `reviews/R4` |
| Findings — R5 standards / statute | **`S-001` … `S-098`** | `reviews/R5` |
| Findings — R6 prior art | **`P-001` … `P-060`** | `reviews/R6` |
| Findings — R7 logistics seam | **`G-001` … `G-086`** | `reviews/R7` |
| Findings — R8 task buildability v1 | **`Q-001` … `Q-006`** | `reviews/R8` |
| Findings — R9 task buildability v2 / epics | **`H-001` … `H-010`** | `reviews/R9` |
| Findings — R10 operational walkthrough | **`U-001` … `U-006`** | `reviews/R10` |
| Findings — R11 exception & unhappy paths | **`Y-001` … `Y-009`** | `reviews/R11` |
| Findings — R12 lifecycle & data migration | **`Z-001` … `Z-010`** | `reviews/R12` |
| Findings — R13 non-functional & operability | **`K-001` … `K-006`** | `reviews/R13` |
| Findings — R14 codebase & sibling re-verify | **`O-001` … `O-007`** | `reviews/R14` |
| Findings — R15 competitor round 2 | **`J-001` … `J-008`** | `reviews/R15` |
| Findings — R16 role & persona completeness | **`RA-001` … `RA-008`** | `reviews/R16` |
| Findings — R17 screen & field buildability | **`RB-001` … `RB-009`** | `reviews/R17` |
| Findings — R18 reporting & analytics completeness | **`RC-001` … `RC-009`** | `reviews/R18` |
| Findings — R19 integration, device & channel surface | **`RD-001` … `RD-008`** | `reviews/R19` |
| Findings — R20 configuration & day-one setup | **`RE-001` … `RE-008`** | `reviews/R20` |
| Findings — R21 money, costing & billing | **`RF-001` … `RF-010`** | `reviews/R21` |
| Findings — R22 cardinality & junctions | **`RG-001` … `RG-027`** | `reviews/R22` |
| Findings — R23 platform alignment | **`RH-001` … `RH-012`** | `reviews/R23` |
| Findings — R24 workflow contract completeness | **`RJ-001` … `RJ-018`** | `reviews/R24` |
| Findings — R25 competitor gap, round 3 | **`RK-001` … `RK-009`** | `reviews/R25` |
| Findings — R26 extensibility & future-proofing | **`RL-001` … `RL-017`** | `reviews/R26` |
| Traps — R1 §8 | **`T-1` … `T-18`**, unpadded | `reviews/R1` §8 |

`P-` (prior art) and `Pn-nn` (tasks) are distinguishable because a task id always carries a phase digit
and a hyphen-separated pair. The check script asserts no id is used for two things.

**`O-` is not `OD-`.** The R14 register and the open-decision register differ by one letter that is
itself a register prefix, which is the exact shape of the `I-`/`IRR-` collision this table was
extended to record. They do not collide, and the reason is mechanical rather than editorial:
`check-design-set.py`'s `FINDING_CITE_RE` requires a hyphen immediately after the register letter, so
`OD-1` can never be read as an `O-` finding, and `O-001` can never be read as an open decision because
the open-decision register is unpadded and single-digit. Nothing else in the set may take `OD` as a
finding prefix.

**The eight round-2 rows were added on 2026-09-02, before their findings were cited anywhere.** Round 2
ran eight lenses against the set that round 1's seven had not: per-task buildability over v1 (R8) and
over v1.1–v3 plus the epics (R9), a journey-first operational walkthrough (R10), the exception and
unhappy paths (R11), the master-data lifecycle from go-live to disposal (R12), the non-functional
surface (R13), a re-verification against the live `classic` checkout and the sibling `accounting` and
`classic-issues` sets (R14), and a live competitor diff (R15). Every prefix was grep-verified free
against the whole repository before allocation — the eight letters `Q H U Y Z K O J` are precisely the
letters that were free — and `check-design-set.py` check 7 resolves each of the 62 round-2 citations
against its own authority exactly as it does the round-1 registers. `GAP-REGISTER-R2.md` holds the
disposition of all 62.

**The six round-3 rows were added on 2026-09-03, and they are the first two-letter registers in this
set. The two letters are not a style choice — the single-letter space is exhausted.** Round 3 ran six
lenses (`reviews/R16`–`R21`) and needed six registers; the alphabet had one to give.

```bash
# every finding id of the shape LETTER-digits, by letter, across the whole set
for L in A B M N R V W; do printf '%s: ' "$L"; \
  grep -rnoE "\b${L}-[0-9]{1,3}\b" docs/ issues/ tools/ | wc -l; done
# -> A 289 · B 5 · M 0 · N 4 · R 37 · V 3 · W 4

# the two-letter space, run BEFORE allocation on 2026-09-02  -> nothing
# re-run today it returns only the six round-3 reviews themselves, and nothing else:
grep -rlE "\bR[A-Z]-[0-9]{1,3}\b" docs/ issues/ tools/
# -> docs/reviews/R16 R17 R18 R19 R20 R21
```

Fifteen letters are already finding registers (seven from round 1, eight from round 2), on top of
`D-`, `L-`, `I-` and `X-`. Of the seven that look free, **only `M` is free**, and one letter is not
six:

- **`A`** is `§5.1`'s ladder amendments `A-1`…`A-4` — 289 mentions, load-bearing.
- **`B`** collides: **`B-04` is a rack label** in a worked example in `reviews/R2`:828, quoted into
  the FRD at `:222` and into `reviews/R18` at `:657` and `:673`. A finding id that is also a physical
  location reads wrong in both directions.
- **`N`** collides: `N-045` and `N-043` are **citations into the *accounting* set's register**
  (`IRREVERSIBLE.md`:251, `reviews/R5`). A cross-set citation that silently resolves to a local
  finding is the failure this table exists to prevent.
- **`R`** is the **rounding-rules register** `R-1`…`R-5` in `DATA-MODEL.md`:2125 — and `R` is also the
  review-file prefix, so `R-1` beside `R1` is exactly the `I-`/`IRR-` hazard recorded below.
- **`V`** is a citation into the accounting register (`V-3`, `reviews/R14`:159) and is the Flyway
  prefix. **`W`** is a small local register in `reviews/R6` (`W-1`, `W-3`, `W-5`, `W-6`).

**Renumbering a review to free a letter is forbidden** — the rule is already stated below: a review is
a dated record of what was found, and rewriting its ids makes every external citation of it wrong.

**Two letters are unambiguous under the same hyphen rule this section already uses to separate `O-`
from `OD-`.** `FINDING_CITE_RE` requires a hyphen immediately after the register prefix, so `OD-1`
can never be read as an `O-` finding. The identical mechanism separates the six new registers from
every single letter and from each other: `RA-001` has no hyphen after `R`, so it is not an `R-` id;
`R-2` has no letter after `R`, so it is not an `RA-` id. Mechanical, not editorial.

**One obligation follows, and it is not discharged.** `tools/check-design-set.py`'s
`FINDING_CITE_RE` is `\b([CTEFSPGQHUYZKOJ])-(\d{1,3}[a-z]?)\b(?!-\d)` — a **single-letter** class, so
it does not match `RA-001`…`RF-010` **at all**. Round-3 citations therefore pass CI because they are
**invisible to check 7, not because they resolve**. `FINDING_CITE_RE`,
`RULE_TOKEN_RE["finding-citations"]`, `REVIEWS` and `FINDING_DEF_RE` must all be extended to admit the
two-letter registers so that a round-3 citation is resolved against its own authority exactly as a
round-1 citation is. **A later wave does it; until then every `RA-`…`RF-` citation in this set is
unchecked**, and that is recorded rather than assumed.

**The five round-4 rows were added on 2026-09-10, and the obligation above is discharged with them.**
Round 4 ran five lenses (`reviews/R22`–`R26`) and took five more two-letter registers under the same
hyphen rule: `RG`, `RH`, `RJ`, `RK` and `RL`.
- **`RI` is skipped on purpose.** `I` beside `1` is the `I-`/`IRR-` hazard recorded below, and `RI-001`
  would read like a mis-typed `R1` citation.
- **`tools/check-design-set.py` now admits every two-letter register:** `FINDING_CITE_RE` and
  `RULE_TOKEN_RE["finding-citations"]` take `R[A-HJ-L]`, and `REVIEWS`, `FINDING_DEF_RE`,
  `REVIEW_LABEL` and `AUTHORITY_STEM` carry R22–R26. So a round-3 or round-4 citation resolves against
  its own authority, or fails.
- **Negative test, run 2026-09-10:** an undefined `RG-` id cited in a doc failed check 7, and the
  citation was removed.
- `GAP-REGISTER-R4.md` holds the disposition of all 83 findings.


**Three of the rows above were added on 2026-09-02, and two of them are the record of a collision that
had already happened.** They are stated here rather than only in the documents that own them, because
§6 is what the next author reads before choosing an id — a register missing from this table is the next
collision.

- **`IRR-nn` — irreversible rows.** `IRREVERSIBLE.md` numbered its 63 rows `I-01`…`I-63`, in the same
  prefix `DATA-MODEL.md` uses for its `I-1`…`I-20` enforceable constraints. Zero-padding did not
  separate them: from `I-10` up the two registers were **byte-identical**, across roughly 250 mentions,
  and `DATA-MODEL.md` had adopted a local `IRR I-nn` qualifier that no other document applied
  consistently. **The irreversible register moved**, because it is the newer of the two and this table
  never granted it `I-`. Every citation across the set was rewritten **file by file, verified in
  context** — never by blanket search-and-replace, which is rule 4 below and which corrupted the
  accounting decisions table twice.
- **`WS-nnn` — screens.** 237 ids, resolvable by the checker and never declared here. **The index in
  `BUILD-SPEC-SCREENS.md` §1 is the allocation**: a screen that is not a row there does not exist, and a
  new screen takes the next free id (`WS-245` at the time of writing) rather than reusing another
  screen's grid.
- **`T-n` and `T-nnn` — two trap/finding registers under one prefix, deliberately not renumbered.**
  R1 §8's traps are **`T-1`…`T-18`, unpadded**; R2's findings are **`T-001`…`T-097`, three digits**.
  They are separated by zero-padding alone, and the separation holds today. **The rule is a citation
  rule, not a renumbering:** always write an R1 trap unpadded and an R2 finding three-digit, and
  never introduce a `T-` id that is padded differently from its own register. Renumbering a **review**
  is forbidden — a review is a dated record of what was found, and rewriting its ids makes every
  external citation of it wrong. `tools/check-design-set.py` check 11 asserts the two registers stay
  disjoint and check 7 resolves each citation against its own authority; R2's **capability-matrix row
  numbers**, which run past `097` and read exactly like finding ids, are the live hazard here and are
  caught by check 7 rather than by shape.

---

<!-- check-design-set: screen-citations end -->

## 7. Rules every author of this design set follows

1. **Never state a count you did not compute with a command.** Put the command in the document.
2. **Every claim about the `classic` codebase carries `file:line`.** If you could not verify it, write
   `UNVERIFIED` and say what would verify it.
3. **Every cross-reference must resolve.** `FR-nnn` to a real requirement, `WH-SC-nnn` to a real
   scenario, a table name to a row in `DATA-MODEL.md`, an issue `#NN` to a row in `issues/CREATED.md`,
   a migration number to exactly one task inside its module's band. `tools/check-design-set.py`
   enforces all of it. The accounting set's worst failure was fabricated cross-references that looked
   plausible and resolved to nothing — 25 dangling `FR-nnn` citations of which **19 resolved to a
   different real requirement**, so live gaps read as closed.
4. **Never blanket search-and-replace an id.** It corrupted the accounting decisions table twice.
4a. **Beware `reviews/R2`'s two numbering systems.** Its capability-matrix rows are numbered
   independently of its `T-nnn` findings, so a matrix row number reads exactly like a finding id and
   resolves to the wrong thing. Four such miscitations were caught and fixed during the first
   authoring wave. **Cite an R2 finding only after opening the `T-nnn` heading itself** — this is the
   same failure that left the accounting set with 19 citations resolving to a different real
   requirement.
5. **The `.md` files in this repository are authoritative; GitHub issue bodies are a mirror** kept in
   sync mechanically by `issues/create-issues.sh --sync`, and `--check` fails CI on drift. Never edit
   an issue body in the GitHub UI.
6. **Do not run `mvn` / `npm` / `tsc`.** This project builds only in Docker; there is no usable local
   toolchain. Verification is by reading, grep and diff against the canonical reference pages named in
   CLAUDE.md.
7. **A block headed *"re-derived, not transcribed"* must have its output regenerated in the same
   commit as any task-header change it reads.** A stale generated block is worse than a hand-written
   one, because the heading invites the trust that stops the next reader checking. Round 2 found
   `08-EPIC-p6.md`'s block showing `V524099` — a number no task header has ever contained (`H-006`).
   The same rule covers `DATA-MODEL.md` §8.4's two generated blocks, which must be regenerated
   **together** or the table count and the version table disagree (`X-054`).
8. **A grep over header text cannot tell a claim from a refusal.** `Migrations **none in this design
   set's bands** — ... the reservation `V524000`–`V524999` ...` yields two version numbers to
   `grep -oE 'V5[0-9]{5}'` and zero claims. Always read the field verbatim before reading the
   extracted numbers.
