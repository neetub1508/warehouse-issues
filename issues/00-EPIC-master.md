TITLE: [Warehouse] EPIC: Warehouse and inventory management — master
LABELS: epic,warehouse
issue: 1
<!-- check-design-set: issue-citations file #2 — `#2` and `#9` are ordinals in prose, not issue references — *Refusal #2*, *Adapter #2 (services)*, *ship-blocker #2*, *logistics needs #1, #2, #3, #5, #6, #10* — and at COMPETITOR-BENCHMARK.md:70/:146 `#9` is the markdown in-page anchor `[§9](#9--where-the-audits-disagree)`. In this repository `#2` and `#9` are in fact the two **pull requests** opened while the backlog was being filed, so no issue row can ever exist for either: see issues/CREATED.md — declared in the front matter, above the `---`, so the declaration never enters the issue body and cannot drift against the filed issue -->
---
Build a **standalone-capable, country-neutral warehouse and inventory-management product** for the
Classic platform, as **five Maven modules plus adapters**.

Design set: **`neetub1508/warehouse-issues`** — read order at the bottom of this page. Code lands in
**`neetub1508/classic`**.

> **Seven audit lenses, 2026-09-01.** The live `classic` checkout, the in-flight `accounting` design set,
> and 28,928 lines of prior warehouse / supply-chain / TMS design art → **575 findings** across
> `reviews/R1`–`R7`, 11,750 lines. `DECISIONS.md` §6 allocates the namespaces: `C-001`…`C-050` (codebase
> reality) · `T-001`…`T-097` (tier-1 WMS) · `E-001`…`E-090` (ERP/mid-market) · `F-001`…`F-093`
> (fulfilment/3PL) · `S-001`…`S-098` (standards/statute) · `P-001`…`P-060` (prior art) ·
> `G-001`…`G-086` (the logistics seam). *(Those seven ranges span 574 ids; the total is 575 because at
> least one finding carries a suffixed id — `T-020a`, cited by `FR-023`. Stated rather than papered over,
> per §7 rule 1.)* Every decision on this page traces to at least one finding, and the namespaces are
> disjoint **by construction** — because *the accounting set's most expensive defect was three different
> things sharing one namespace, which a late rename could not repair.*

## The product in one paragraph

`platform + warehouse-base + warehouse` is a **complete, shippable stock product** — no dealer, no
automotive, no accounting. At its centre is **one immutable, double-sided, append-only stock ledger at
full grain**: every stock event is a movement with two or more lines that conserve quantity, positions are
a **cache** that a full rebuild must reproduce exactly, and a correction is a **reversal** — there is no
edit anywhere in the product. Around it sit the application layers that write to it and a **generic
inbound movement port**, so that any number of future consumers — a logistics/TMS module, a
supply-chain/procurement module, a POS, an eCommerce channel, or any vertical in the suite — can move
stock **without `warehouse-base` ever depending on them**. It is not a replacement for anything currently
shipping: `services`, `field-service` and `assets` have **no** stock capability at all (R1 `C-034`), and
`services.parts_used` is free `TEXT`. It is the first real stock ledger in this suite.

## The five modules

| Module | Java package | Prefix | Flyway band | Depends on | Ships |
|---|---|---|---|---|---|
| **`warehouse-base`** | `ai.warehousebase` | **`whb_`** | **V500000–V509999** | **platform only** | v1 |
| **`warehouse`** | `ai.warehouse` | **`wh_`** | **V510000–V519999** | platform + base | v1 |
| **`warehouse-adapter-<vertical>`** | `ai.warehouseadapter<vertical>` — a **sibling**, never `ai.warehouse.adapter.*` | `whad_` dealer · `whas_` services · `whaf_` field-service · `whaa_` assets · `whae_` example | **V520000–V529999**, sub-allocated 1,000 per adapter | platform + base + that vertical | v1 → v1.1 |
| **`warehouse-3pl`** | `ai.warehouse3pl` | **`wh3_`** | **V530000–V539999** | platform + base + app | v2 |
| **`warehouse-india`** | `ai.warehouseindia` | **`whin_`** | **V540000–V549999** | platform + base + app | v1 (documents) + v2 (registers) |

Reserved since v1 and built in v3: **`logistics`** — package `ai.logistics`, prefix **`log_`**, band
**V524000–V524999**, and the `logistics:*` permission namespace seeded by `WHB-71` (`V501000`).

**The adapter package must be a sibling.** `@ComponentScan("ai.warehouse")` matches by package **prefix**,
so `ai.warehouse.adapter.dealer` would load in **every** install, including ones where dealer is not
built. This is the exact trap the accounting round-4 review found and corrected.

## The fourteen decisions — do not re-litigate these

| # | Decision |
|---|---|
| **D-1** | **Five modules, not four.** `warehouse-india` is the fifth and was not in the brief: the brief's four modules carry a *vertical* axis and **no jurisdiction axis**, so every India rule would otherwise live in `warehouse` (unsellable outside India) or in an adapter (invisible to a pharma customer). Accounting took the same decision and shipped `accounting-india` |
| **D-2** | **The bands are V500000–V549999, not V900000+.** `V900000`–`V909999` holds **135** OEM-seed migrations and `V910000`–`V919999` holds **434** per-client migrations with versions **deliberately reused across five client directories** (`V910001__` exists five times); `V950000+` holds 32 test-data files. `FlywayConfiguration.java:296-327` renumbers legacy history into both bands (`+830000`) and then **`DELETE`s duplicate history rows** — so a collision does not fail loudly, **it silently deletes a history row and re-runs a migration**. `V130000`–`V599999` is entirely empty (0 files, computed) |
| **D-3** | **Table prefixes are fixed** — `whb_` · `wh_` · `wh3_` · `whin_` · `whad_`/`whas_`/`whaf_`/`whaa_`/`whae_` · `log_`. Three lenses proposed three different schemes; this is the resolution. **Never name anything `wms_*` or `scc_*`**: live platform migrations still carry hardcoded exclusions for those prefixes from a deleted earlier module |
| **D-4** | **The stock ledger is double-sided, append-only and immutable.** A receipt's counter-side is a **virtual location**, never an absent row. This is the single decision that separates this product from everything already in the suite — `accessory_inventory_transactions` is a single-sided log written next to an **in-place-mutated** balance row, and some paths write no movement at all (`StockReceiptService.java:373-411`), so the balance is **not derivable from the movements**. Neither it nor the prior WMS art is a ledger. **Do not copy either** |
| **D-5** | **`owner_id` is `NOT NULL` in v1, in every install, and in the position key.** `warehouse-3pl` ships in v2; the column ships in v1, because consignment stock, customer-owned repair goods, job-work material at a job worker, bailed 3PL stock and our own stock are the same shape and differ only by owner — and **no rule recovers whose a unit was.** Free now, unbackfillable later. Without it `warehouse-3pl` is not a module, it is a rewrite. The same argument, with the same verdict, applies to `duty_status`, `stock_status_code`, `lot_id`, `serial_id` and `lpn_id` |
| **D-6** | **Whichever system is authoritative for quantity is authoritative for cost; accounting always owns the ledger.** Warehouse is the system of record for every movement, position, count, adjustment and physical truth — and therefore for cost, because only warehouse holds the grain the costing methods need. **Warehouse never writes an `acc_*` table**; it hands over one envelope per posting-relevant event and carries `handover_id` + `posting_status` so *"does the stock ledger tie to the GL"* is answerable |
| **D-7** | **Standalone is the reference configuration**, not a degraded mode. No v1 capability may require any vertical or accounting to be installed |
| **D-8** | **Country-neutral core.** No GST, HSN semantics, e-way bill or MRP rule is hardcoded in base or app. India ships as `warehouse-india`. The core carries only the *hooks* India needs, and those are in v1 because they cannot be added later |
| **D-9** | **`accessories` inventory stays permanently separate — and the cost is named, not hidden.** 17 tables, 71 backend files, 11 reports and 33 mobile screens duplicated; a second item master; **two stock truths with no reconciliation and no unified report**; and the load-bearing one — **the same physical unit counted in both systems is not merely unmitigated but undetectable.** Two mitigations are therefore mandatory in v1 and are tasks, not advice: an `ACCESSORIES` cross-map row per dual-stocked SKU, and a category-ownership rule with a report naming every violation |
| **D-10** | **Every extensible vocabulary is a catalogue table with no `CHECK` constraint** — thirteen of them. The precedent that works is live and self-documenting (`acc_reason_codes.context`: *"It is a CATALOGUE, not an enum"*); the counter-example is equally live (`widget_definitions.chk_module`, dropped and rebuilt **three times** and still admitting neither `warehouse` nor `logistics`) |
| **D-11** | **Adapters are proved by a build-time test, not by intent.** `warehouse-adapter-dealer` ships with **zero commits to `warehouse-base`**, enforced by an `ArchitectureInvariantsTest` per module and a `warehouse-adapter-example` fixture CI builds. **Adapter #2 (services) is in v1 for the reason that one adapter proves nothing about genericity** |
| **D-12** | **v1 is a cut line, not the scope limit.** Every capability found by any lens is placed in a version and carried in a task file **now**. Nothing is deferred to *"we'll look at it later"* — which is why P5 and P6 exist and why four P6 tasks produce a written determination and no code |
| **D-13** | **Mobile is not optional.** Every user-visible capability with a web screen has a mobile counterpart **in the same task**, per CLAUDE.md's web↔mobile mirroring rule — or a stated `none` with a reason. **Silence is a defect.** Note the correction R1 `CM-1` found: `mobile/…/ListHeader.tsx:210-218` now supports `type?: 'dropdown' \| 'text'`; **date filters are still unsupported** |
| **D-14** | **Associations between masters are dated many-to-many; a warehouse has exactly one `REGISTERED` branch** (user decision, 2026-09-10, round 4). Every association between two independent masters is an effective-dated junction; composition and ledger fact rows stay scalar. A warehouse links to branches through `whb_warehouse_branches`, with exactly one `REGISTERED` link at every instant, which supplies its GSTIN; `SERVING` links grant visibility and let a branch draw stock, and a draw across GSTINs is a taxable transfer. A registration change is maker–checker and refused while stock is held (`OD-19`). Useful-but-not-day-one work goes to a later version **and is still tracked** — as a versioned increment of the most similar existing task (round 4 filed `P3-25` and `P5-24`…`P5-28`, and folded all six into their hosts on 2026-09-10: no duplicate tasks). Reverses `FR-079`'s *"belongs to exactly one branch"*; `RG-001` is canonical |

## The fourteen load-bearing invariants

Each has **a database guard and a service guard**. The service guard rejects **first, in the transaction,
with a field-level error**; the database guard is the backstop for the paths the service does not own.
**A trigger firing in production is an incident, not a validation.**

| # | Invariant | Why it matters |
|---|---|---|
| **L-1** | **Conservation** — every movement's lines sum to zero in base UoM per (owner, item, lot, serial, duty status), balancing against a **virtual location**, never against nothing | Without it a "receipt" can create stock from nowhere and no rebuild will ever tie |
| **L-2** | **Append-only** — no posted line is ever `UPDATE`d or `DELETE`d. Three layers: one writer service with no update method, a `to_jsonb`-diff trigger rejecting `INSERT` into a posted movement as well as `UPDATE`/`DELETE`, and no repository path | Two layers is one bug away from a mutable ledger. The trigger protects later-added columns automatically |
| **L-3** | **Correction is reversal** — mirrored lines, a mandatory reason code from the catalogue, the original marked reversed. **"Edit" is never offered anywhere in the product** | It erodes under *"just let the storekeeper fix it"* pressure, which is why it is written as a product rule, not a service rule |
| **L-4** | **Positions are a cache** — a full rebuild from `whb_stock_movements` reproduces every position row **exactly**, proved nightly with a drift alert | It is the only thing that makes the ledger the truth rather than a second opinion |
| **L-5** | **Full-grain key** — (company, owner, item, location, lot, serial, lpn, stock_status, duty_status). **Every column exists in v1 even where its feature ships later** | A key member added after the ledger has rows is a re-key of the hottest table in the product |
| **L-6** | **Negative available is refused; negative on-hand is a policy** — `available = on_hand − Σ open reservations` may never go below zero; physical on-hand may only where an explicit per-item × per-site policy allows | The accessories code comment names the exact race its Java read-compare-write does not win |
| **L-7** | **Quantity is in base UoM with the conversion factor frozen on the line** | A ledger that re-derives from today's factor **silently restates last year** |
| **L-8** | **Period-bound** — a movement into a locked period is refused, **including a reversal**; a soft close needs an approved override, a hard close admits nothing | It is what makes a closed period mean something to an auditor |
| **L-9** | **Ingestion is idempotent** — `(source_system, idempotency_key)` unique; a repeat returns the original and posts nothing. **The key is never server-generated** | An already-double-posted ledger cannot be deduplicated afterwards: the duplicate is indistinguishable from a legitimate repeat |
| **L-10** | **Allocation is an open-item ledger, not a counter** — every reservation is a row with a holder quad and an `expires_at` | With a counter you cannot release **one** order's hold, and the only repair is to zero it — which releases everyone's |
| **L-11** | **Ownership never changes silently** — a title transfer is an explicit movement type with its own reason code. Goods can change owner without moving, and move without changing owner | Whose a unit is, is a contractual fact, not a derived one |
| **L-12** | **Traceability is reconstructible in both directions** — forward *(where did this lot go)* and backward *(what went into this unit)*, for the full retention period, **across the kit boundary** | A recall is retrospective by definition; genealogy not captured at the moment of transformation can never be acquired |
| **L-13** | **Three timestamps, never one** — `occurred_at` (when it physically happened, producer-supplied), `recorded_at` (when we heard), `posting_date` (the accounting date) | One timestamp cannot be split later, and collapsing them kills offline replay, degraded-mode catch-up, cut-off and EPCIS **simultaneously** |
| **L-14** | **Non-own stock is never valued** — `owner_type != OWN` hands over for quantity and custody reporting only; what we carry is a custody liability and an insured value, **a different number on a different report** | A 3PL that posts its clients' stock to its own balance sheet has a catastrophe in both directions |

## The eleven open decisions

Each is a **merge gate on a named task**, not a note.

> ## ⛔ `OD-10` HAS THE TIGHTEST DEADLINE IN THE PROGRAMME
>
> **Is MRP a dimension of the stock position?** It must be answered **before `P0-02` writes migration
> `V500030`** — the file that sets the position unique key **and, in the same file, seals the ledger
> against `UPDATE` forever**. There is no later window. A tenth key member added afterwards is
> recoverable **only** because `L-4` makes the position a cache — **and only if the ledger line already
> carries the column.** If MRP is in the key and the line does not carry it, the answer is a re-key of the
> hottest table in the product **plus** an unbackfillable column, simultaneously.
> **The recommendation is NO** — MRP belongs on the **lot**. **If this is wrong it is unrecoverable, so it
> must be answered, not assumed.**

| # | Decision | Blocks | Deadline |
|---|---|---|---|
| **OD-10** | MRP in the position key? | `P0-02` / `V500030` | **before `P0-02`** — the tightest in the set |
| **OD-7** | Precision — quantities `DECIMAL(18,4)`, money `DECIMAL(19,4)`, per-unit `DECIMAL(19,6)`, **percentages `DECIMAL(9,6)`**, UoM conversion factor `DECIMAL(18,8)` | `P0-02` and every numeric ledger column | **before `P0-02`** |
| **OD-11** | Do value-only movements conserve **value**? `L-1`…`L-14` conserve quantity only, and a landed-cost movement posts `quantity = 0` with a value | `P0-02`, `P2-16`/`P2-17`/`P2-28` | **before `P0-02`** — a conservation invariant is a constraint on the table, not on the report |
| **OD-1** | The **reciprocal accounting edits** — a third install state, *"a warehouse product is present and owns quantity"*. **A different repository's design set to amend** | `P0-02`, `P2-16`/`P2-18`, reaches `P5-16` | before `P0-02`, and before accounting's P3 |
| **OD-8** | How does an **out-of-process consumer authenticate** to the port? There is no API-key table in platform (grep → 0) | `P0-08`, reaches `P6-04` and `P6-08` | **before `P0-08`** — the auth model shapes the endpoint |
| **OD-5** | Does the frontend **re-close the vocabularies the backend opens**? CLAUDE.md mandates string unions; `D-10` mandates open catalogues, and R2 records the conflict as a *documented recurring defect in this codebase* | `P0-04` | **before the first warehouse page** |
| **OD-6** | Valuation method scope in v1 — FIFO + weighted average + standard, or weighted average only? **LIFO is never built** (prohibited under Ind AS 2 / IAS 2) | `P2-16` | before P2's valuation tasks |
| **OD-9** | Does `warehouse` carry a tax engine, or **never compute tax**? The India pack is **50 or 56 tables** depending on the answer | `P2-IN-01`, `P4-01` | before `P2-IN` |
| **OD-3** | One database per customer, or shared multi-tenancy? `grep -ril "tenant" platform/backend/src/main/java` → **0 files** | **`P5-01`** | before `warehouse-3pl` starts |
| **OD-4** | Who owns the shared supplier/counterparty master long-term? **Never an FK from base into another module** — the previous attempt died of exactly that | **`P6-06`** (`P1-08` proceeds regardless) | v3 |
| **OD-2** | Does the dealer vehicle inventory migrate onto the ledger? The **test** is stated rather than the answer | **`P6-09`** | v3 planning, not before |

**Round 4 adds two, both escalated, each with a safe default already in the design** (`DECISIONS.md`
§3.5): **`OD-19`** — the statutory treatment of on-hand stock when a site's `REGISTERED` branch moves to
another GSTIN; it gates `P1-05`'s *Change registration* action, which is refused while stock is held
until it is answered. **`OD-18`** — what v1 records for a drop-shipment; it gates `P5-09`'s `FR-467`
at the first drop-shipped purchase.

**And one unnumbered conflict that must become an `OD-` row before `P0-02` is written:** the ledger's
**partition key**. `FR-022` and `DATA-MODEL.md` `WHB-30` say `occurred_at`; `PLATFORM-DEPENDENCIES.md`
`PD-D5` says `posting_date`. **Nothing resolves them**, and *a partition key cannot be added to a
populated table without a rewrite.* Both sides have a real argument — `occurred_at` is what the as-at
query and EPCIS want; `posting_date` is what period close and the statutory register want — and `L-13`
says they are **different columns**, so the choice is real.

## The version ladder

| Version | Phases | What it is | Exit criterion — **as scenario ids** |
|---|---|---|---|
| **v1** | __P0__ · __P1__ · __P2__ · __P2IN__ | The stock ledger and inventory control, standalone: multi-site/bin stock at full grain, items and UoM, lots/expiry/serials, receiving/QC/putaway, allocation and pick/pack/dispatch, transfers with in-transit, adjustments, cycle and physical counts, costing and valuation, reorder, **basic returns**, **printing including ZPL**, **the India movement documents**, the report pack, **and the dealer-parts + services adapters** | **`WH-SC-044` … `WH-SC-062`** — the 19-scenario decomposition of §3.2: on a **standalone** install a storekeeper runs a full day and produces a stock ledger, a position report and a valuation report **that reconcile to each other and to a full ledger rebuild** |
| **v1.1** | __P3__ | The warehouse floor: RF/handheld task flows, task management and priority, wave planning and release, batch/cluster/zone picking, packing and cartonisation, the print server and device management, dock appointments, van stock, the field-service and assets adapters | **`WH-SC-227`** (a full receive→putaway→pick→pack→ship cycle **entirely on a handheld**) and **`WH-SC-228`** (a 200-line wave releasing, picking and shipping with task interleaving) |
| **v2** | __P4__ · __P5__ | Sellable as a compliance product **and** to a 3PL: job work and ITC-04, the Rule 56 stock account, MRP and Legal Metrology, bonded/MOOWR; owner-of-goods billing, rate cards, storage and handling meters, the client portal, channel intake, carrier integration, full reverse logistics, NDR/RTO/COD | **`WH-SC-234`** (a 3PL bills a month of storage and handling **from metered events**) **plus `WH-SC-239`/`WH-SC-240`** (ITC-04 and the Rule 56 stock account filed **from warehouse data**) — with three clauses added by `IMPLEMENTATION-PLAN.md` §1.7: the invoice arithmetic is **reproducible from the meter**; a portal user **cannot see another client's stock through any endpoint**, proved per endpoint; and a channel order imported twice produces **one** demand order |
| **v3** | __P6__ | Slotting, replenishment optimisation, labour standards, ABC/XYZ and velocity, demand and reorder planning, supplier scorecards, EPCIS/GS1 event capture, automation interfaces, control-tower analytics — **and the `logistics` module itself** | **No `v3·P6` scenario exists in the catalogue today** (computed). The criterion is therefore prose until __P6__ authors it: *`logistics` ships trips, ePOD and freight settlement, moves stock **only** through the port, and `git log --oneline -- warehouse-base/` shows **zero** commits attributable to it* — plus `FR-336`'s **two deletion tests**. **`P6-08` authors those scenarios as its first act, because they are the exit criterion** |

**Adapter schedule:** dealer-parts **v1** (proves the port) · services **v1** (proves genericity — *one
adapter proves nothing*) · field-service and assets **v1.1** · logistics **v3** · **accessories never**
(`D-9`).

## The phases

| Phase | Epic | Name | Tasks | Ships |
|---|---|---|---|---|
| P0 | __P0__ | Ledger foundation | **17** | v1 |
| P1 | __P1__ | Masters, identity, inbound | **21** | v1 |
| P2 | __P2__ | Outbound, counting, valuation, returns, printing, reports | **29** | v1 |
| P2-IN | __P2IN__ | The India movement documents | **4** | v1 |
| P3 | __P3__ | Execution and mobile | **24** | v1.1 |
| P4 | __P4__ | India statutory and compliance | **13** | v2 |
| P5 | __P5__ | 3PL, channels and reverse logistics | **23** | v2 |
| P6 | __P6__ | Optimisation, planning and the logistics seam | **12** | v3 |

**143 tasks** — `ls issues/p*.md | wc -l`, and 17 + 21 + 29 + 4 + 24 + 13 + 23 + 12. Round 4 filed six
(`P3-25`, `P5-24`…`P5-28`, `#156`–`#161`) and on 2026-09-10 folded each into its most similar existing
task; the six issues are closed as duplicates (`issues/CREATED.md`, `GAP-REGISTER-R4.md` §4.6).
**471 requirements**, each owned by **exactly one** task. **305 scenarios** (computed:
`grep -cE '^\| \*\*WH-SC-[0-9]{3}\*\*' docs/SCENARIO-CATALOGUE.md`; 300 before review round 2 added
§3.21's five. `IMPLEMENTATION-PLAN.md` §8.5 stated **119** for that same command until 2026-09-02,
when `X-007`/`X-034` were closed by recomputing it). **314 tables. 237 screens**, 215 of them
carrying a `gridIdentifier`. **823 migration numbers allocated** — `D-2`'s five bands only; `P6-08`'s
`logistics` schema is numbered outside them.

> **The file glob is the count.** `DECISIONS.md` §6 makes `issues/pN-nn.md` the authority on the task
> list. **The moment those files exist they win over `IMPLEMENTATION-PLAN.md` §2**, and
> `tools/check-design-set.py` must fail on drift between them.

## Migration discipline

| Module | Band |
|---|---|
| `warehouse-base` | **V500000 – V509999** |
| `warehouse` | **V510000 – V519999** |
| `warehouse-adapter-*` (shared, sub-allocated 1,000 per adapter: dealer V520000, services V521000, field-service V522000, assets V523000, **logistics V524000**) | **V520000 – V529999** |
| `warehouse-3pl` | **V530000 – V539999** |
| `warehouse-india` | **V540000 – V549999** |

- **Exactly one task owns each number**, pre-allocated in that task's header, inside its module's band, so
  parallel work cannot collide. A task needing a second file takes the next number **inside its own
  block**, never the next globally free one. A number is never reused even if its task is dropped.
- **Never invent a number that looks plausible.** An early draft cited `V510126` for `wh_tracking_links`;
  the table is `WH-109` at `V510209`. It was caught before publication and recorded, because *"an invented
  migration number that looks plausible is precisely the failure mode `DECISIONS.md` §7 rule 3 exists to
  prevent."*
- **Every migration is individually idempotent** (`IF NOT EXISTS` / `ON CONFLICT` / `WHERE NOT EXISTS`).
  `FlywayConfiguration.java:246-264` runs a blind `flyway.repair()` and one retry on **any** failure, so a
  partially-failed migration **re-runs**.
- **Two shared files are not migrations and are the highest merge-conflict surface in the plan:**
  `platform/frontend/src/utils/filterUtils.ts` (213 scopes — a field absent from its scope is **silently
  dropped** before the request is built) and `CacheConfiguration.java` (234 names — an unregistered name
  throws on the **first call, not at startup**). Batch their edits.
- **The grid config table is `filter_definitions`** (`platform/…/V229:8`). **`grid_filter_definitions`
  does not exist** and inserting into that name crash-loops the backend.

## Definition of done — every task in every phase

`/grill` before any code, with the canonical reference named (Department / Customer / Service Vehicle) and
**diffed against it** · **`reviewer` agent**: zero load-bearing and zero parity findings ·
**`functional-reviewer` in conformance mode** against the matching contract in `docs/contracts/`, authored
in the task if the workflow has none · **the `WH-SC-nnn` scenarios the task claims are walked in the
running app**, not reasoned about · migration idempotent, forward-only, never edited in place, number
owned by exactly one task, carrying `IRREVERSIBLE.md` §3.6's four-question header comment · permissions
granted with the `role_permissions` back-fill in the same migration, `permission_dependencies` rows
**`INSERT`ed, never `CREATE TABLE`d** (it is a platform table, `V248:17-30`), AUDITOR gets `:view` and
never `:export` · grid ships column definitions, `filter_definitions` **and** `grid_preferences` with
**both** `default_columns` and `default_filters` · filter keys in `COMMON_FILTER_CONFIGS` **and** accepted
by the controller, every as-on/from-to filter authored as **two `date` filters** (there is no `daterange`
type, and `dateOnly` is a distinct type from `date`) · cache names registered — **and filter-aware
statistics registered nowhere** · export a superset of the visible grid columns honouring filters **and
sort** · i18n **en / fr / hi** in the module's SafeTranslation · **mobile counterpart delivered, or its
absence declared with a reason — silence is a defect** · **Docker build requested; there is no local
toolchain, so never run `mvn`, `npm` or `tsc` to "verify"**.

**Five additions specific to this programme:**

1. **A migration that only `RAISE NOTICE`s its checks is not verified.** Assert with `RAISE EXCEPTION`, so
   a future apply against a different database fails loudly.
2. **Every `L-n` invariant has a database guard *and* a service guard**, and the service guard rejects
   **first, in the transaction, with a field-level error**. *A trigger firing in production is an incident,
   not a validation.*
3. **The loose-coupling ratchet runs in CI**, not in a reviewer's memory: `WarehouseBaseCouplingTest`'s six
   assertions, a per-module `ArchitectureInvariantsTest`, and `warehouse-adapter-example` built green, with
   `warehouse-ratchets` running on every PR (required-check setting waived).
4. **Every threshold column ships with the scheduled job that reads it.** *A dated obligation with no actor
   is a defect at the moment it is merged, not when it is noticed.*
5. **A task creating a `status` column ships its ladder rows** in `BUILD-SPEC-SCREENS.md` §0.11, in the same
   PR — `Table | From | To | Verb | Actor (permission) | Guard | Terminal?`. **A state with no inbound
   transition, and a non-terminal state with no outbound transition, are both defects.** Every verb in the
   ladder is a §10.2 permission string, not an `:edit` (`H-004`, `H-001`). *A status value written by a
   build that guessed the ladder is in the customer's table forever, and the `IRR-41`-shaped append-only
   tables cannot be corrected by `UPDATE`.*

## Accepted limitations — what a v1 buyer does not get

Cross-referenced to `COMPETITOR-BENCHMARK.md` §4.1, **as corrected by `DECISIONS.md` §5.1's amendments**.
Three of §4.1's thirteen loss rows are now **closed** and must not be quoted as live losses: returns
(`A-1`, v1/`P2-12`), label and document printing (`A-2`, v1/`P2-14`), and the apparel variant **schema**
(`A-3`, v1/`P1-01`). India is **partly** closed — goods can now legally move at v1 (`A-4`), while filing
remains v2.

**The losses that stand, unsoftened:**

- **CDK · Reynolds · Tekion · Karmak · Autologue** — the **computed best stocking level**, *"the single row
  a parts manager tests us on"*. It closes at `P6-02`, **v3**, and it is **the most commercially dangerous
  deferral in the plan**, in the one segment we are best positioned to win.
- **Infor WMS · Extensiv · Camelot · Infoplus · Logiwa · CartonCloud** — 3PL billing, rate cards, meters,
  the client portal. **We cannot bill for stored goods at all in v1.** We *can* hold them correctly, which
  is the part that cannot be added later. Closes at `P5`, v2.
- **Unicommerce · EasyEcom · Vinculum · Shiprocket · WareIQ · Cin7 Omni** — the entire Indian D2C surface:
  marketplace connectors, AWB pools, pincode serviceability, NDR, COD, RTO. Closes at `P5`, v2.
  **Do not bid the segment at v1.**
- **Manhattan · Blue Yonder · SAP EWM** — waving, labour management, slotting, integrated planning,
  MFS/AS-RS. v1.1 waves; the rest **refused**, and it is the right loss: *Manhattan's labour management
  alone is larger than our whole v1.*
- **Oracle WMS Cloud · Körber** — customer-configurable RF flows, LPN-native receiving. **Do not bid.**
- **Marg · GoFrugal · Busy** — schemes beyond free quantity, van sales, claim automation, and a price point
  we cannot match. Acceptable **provided** we do not also lose on batch, expiry, MRP, godown statement,
  challan or as-at date — all of which are in the v1 cut for exactly this reason.
- **Tally Prime** — ten valuation methods and universal accountant familiarity. **Never.** Not the fight;
  we win as the *operational* system feeding one GL.

**Segments a v1 install cannot serve at all:** pharmaceutical distribution, cold chain, 3PL contract
logistics and eCommerce fulfilment — all v2. Apparel and footwear becomes servable at v2 **because** `A-3`
put the variant schema in v1; had it not, the segment would have been **permanently** declined.

**23 deliberate refusals** (`COMPETITOR-BENCHMARK.md` §7), each with a stated re-entry path and each of
which **must appear in the product documentation in the place a reader would look for the feature** —
*"'Not built, because X' is a credible answer in a sales conversation; silence is not."* Among them: a TMS,
distributed order management, a labour-standards engineering engine, incentive pay, direct automation
control, voice picking, a slotting solver, demand forecasting, LIFO, a general-purpose rules engine or
expression language, JSONB custom-field bags, multi-tenant SaaS, UDI/pharma serialisation regimes, export
and customs documentation, an invoice or tax engine inside `warehouse-3pl`, a consumer returns portal, an
EPCIS repository, retail-compliance EDI, and yard/trailer management.

**The honest one-line summary.** A v1 install is a **correct, auditable, multi-site, multi-owner stock
ledger with a parts catalogue, an Indian-legal movement document set and enough screens for a storekeeper
to run a day** — and it is **not** a warehouse *execution* system, a 3PL platform, a fulfilment platform or
a compliance filing product until v1.1, v2 and v2 respectively.

## Read order for the design set

1. **[`DECISIONS.md`](../blob/main/docs/DECISIONS.md)** — **first, always.** It wins over every other
   document except `reviews/R1`, which wins on any question about what the *existing* codebase does,
   because it carries `file:line` evidence. Module names, packages, bands, prefixes, id namespaces and the
   version ladder are fixed there **and nowhere else**.
2. **[`IRREVERSIBLE.md`](../blob/main/docs/IRREVERSIBLE.md)** — what is free now and impossible later.
3. **[`WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md`](../blob/main/docs/WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md)** —
   the 446 `FR-nnn`, each with its module, version, phase and source findings.
4. **[`DATA-MODEL.md`](../blob/main/docs/DATA-MODEL.md)** — the migration authority: every table (§2), **the
   split proof** (§3 — every boundary-crossing FK and the proof it points downward), the `I-n` enforceable
   constraints (§6), and the allocation (§7).
5. **[`PORT-AND-ADAPTER-CONTRACT.md`](../blob/main/docs/PORT-AND-ADAPTER-CONTRACT.md)** — the wire: the
   envelope, idempotency, **§4 the outbox and its billable granularity**, reservations, the open
   catalogues, the build-time coupling test, and **§9 the consumers**.
6. **[`SCENARIO-CATALOGUE.md`](../blob/main/docs/SCENARIO-CATALOGUE.md)** — **these are the acceptance
   criteria.** "Done" means walked in a running application.
7. **[`BUILD-SPEC-SCREENS.md`](../blob/main/docs/BUILD-SPEC-SCREENS.md)** — the 237 screens, their tables,
   columns, filters, actions and mobile verdicts.
8. **[`IMPLEMENTATION-PLAN.md`](../blob/main/docs/IMPLEMENTATION-PLAN.md)** — the 143-task decomposition,
   the critical path, the four points of no return, the open decisions as gates, and the traceability.
9. **[`MODULE-INTEGRATION.md`](../blob/main/docs/MODULE-INTEGRATION.md)** — the **22** integration
   touchpoints, three of which fail **silently**.
10. **[`PLATFORM-DEPENDENCIES.md`](../blob/main/docs/PLATFORM-DEPENDENCIES.md)** ·
    **[`COEXISTENCE.md`](../blob/main/docs/COEXISTENCE.md)** ·
    **[`INDIA-LOCALISATION-PACK.md`](../blob/main/docs/INDIA-LOCALISATION-PACK.md)** ·
    **[`COMPETITOR-BENCHMARK.md`](../blob/main/docs/COMPETITOR-BENCHMARK.md)**.
11. **`reviews/R1`–`R7`** — the 575 findings, when a task's `## Closes` block needs its evidence.
    **`R1` wins on any claim about the live codebase.** And beware **`R2`'s two numbering systems**: its
    capability-matrix rows are numbered independently of its `T-nnn` findings, so a matrix row number reads
    exactly like a finding id and resolves to the wrong thing. **Cite an R2 finding only after opening the
    `T-nnn` heading itself.**

## The rules every author of this design set follows

1. **Never state a count you did not compute with a command.** Put the command in the document.
2. **Every claim about the `classic` codebase carries `file:line`.** If you could not verify it, write
   `UNVERIFIED` and say what would verify it.
3. **Every cross-reference must resolve.** *The accounting set's worst failure was fabricated
   cross-references that looked plausible and resolved to nothing — 25 dangling `FR-nnn` citations of which
   **19 resolved to a different real requirement**, so live gaps read as closed.*
4. **Never blanket search-and-replace an id.** It corrupted the accounting decisions table twice.
5. **The `.md` files are authoritative; GitHub issue bodies are a mirror** kept in sync by
   `issues/create-issues.sh --sync`, with `--check` failing CI on drift. **Never edit an issue body in the
   GitHub UI.**
6. **Do not run `mvn` / `npm` / `tsc`.** This project builds only in Docker. Verification is by reading,
   grep and diff against the canonical references named in CLAUDE.md.
