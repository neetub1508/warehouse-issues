# 06 — Warehouse design decisions vs a future service-parts PLANNING module

**Scope.** This report covers every decision, refusal, contract, invariant and irreversible choice in the warehouse design that a
future service-parts planning module would conflict with, depend on, or need changed. The module is assumed to cover forecasting, service-level stocking,
multi-echelon, supersession-aware demand, repair/cores/warranty, van/field stock, dealer network,
scenarios/time-travel, autopilot auto-approval and pricing.

**Sources read (2026-09-30).** Design repo `neetub1508/warehouse-issues`, branch `docs/ptc-servigistics-comparison`,
which is up to date with origin: `docs/DECISIONS.md`, `docs/WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` (§6.14, §9, §10), `docs/DATA-MODEL.md`,
`docs/PORT-AND-ADAPTER-CONTRACT.md`, `docs/IRREVERSIBLE.md`, `docs/IMPLEMENTATION-PLAN.md`, `docs/COMPETITOR-BENCHMARK.md`,
`docs/GLOBAL-SETTINGS-DECISIONS.md`, `docs/GAP-REGISTER*.md`, `docs/reviews/R6-prior-art-triage.md` (`P-052`),
`issues/p6-*.md`, `docs/competitive/*.md`, and GitHub issues (open list, closed-not-planned list, and bodies of #75, #81, #95,
#102, #108, #121, #134, #150, #151, #167–#186, #191).
I also checked the built state with static greps of `classic/warehouse-base` and `classic/warehouse`, covering migrations
and Java. No build or runtime checks were run.

**Legend.** *Action*: **KEEP** means planning builds on it as is. **AMEND** means extend or clarify it without reversing it. **REVERSE** means formally
overturn it. **ADD** means a new decision, column or contract is needed. *Pre?* **YES** means it must change or be decided before the
planning module's first migration or first design freeze. **EARLY** means it must happen before the relevant planning feature ships. **NO** means planning can
live with it.

---

## 0. The five facts that shape everything else

1. **The module was planned for, then left undefined.** FRD §10 row 8 says: *"Relocated, not refused — a planning module with its own
   band, consuming a forecast through an interface. `FR-258` is the boundary."* Row 9 routes service-parts planning to
   *"the same planning module. Four nullable seam columns and two shared classification fields cost nothing now (`FR-070`)"*.
   R6 `P-052` names those four seam columns: `spi_recommendation_id`, `spi_order_id`, and SPI-writable stocking and
   classification fields. **Only part of that seam exists** (§3, row DM-9).
2. **The vertical adapters are gone for good.** They were deleted on 2026-09-21 (commit `64d1fe74d5`, #150/#151). The user ruled on 2026-09-23 that
   *no warehouse adapter module is built at all* (#102, #108) and that there is *no dealer-management or vehicle work in warehouse*
   (#134). Everything the design put in `whad_`/`whas_`/`whaf_`/`whaa_` has lost its home. That covers counter sale, prices, OEM order and
   acknowledgement, cores, warranty holds, fitment, job-card issues and van replenishment.
3. **Warehouse will never forecast.** `P6-02` (#99) says levels are *"Computed from our own demand history … never from a
   forecast"*. It *"writes the item × site reorder point that P2-15's run already reads"*. Once a planning module also writes
   targets, two writers compete for one column.
4. **Warehouse will never auto-approve.** The rules are FR-253 (*"No purchase order is raised automatically; the human still accepts"*), `RK-004`
   (*no auto-PO*), GLOBAL-SETTINGS `warehouse.approval.pending_alert_hours` (*"never auto-approve"*) and FR-408
   (*approver may not be the actor*). An "autopilot" contradicts all four.
5. **Demand history is monthly, per item and site, and drops excluded demand.** `wh_demand_history` stores item × site × `YYYYMM`,
   with no owner, no demand stream and no week or day grain. Warranty and internal consumption are *excluded*, not stored in a separate stream.
   The ledger still holds the movements, so this can be rebuilt. It is not lost, but it is not available either.

---

## 1. Decision / refusal / invariant register

### 1.1 Refusals (FRD §10) and boundary statements

| ID | What it says (short quote) | Impact on planning | Action | Pre? |
|---|---|---|---|---|
| **Refusal #8** (FRD §10; COMPETITOR-BENCHMARK:351, :688, :892) | *"Demand forecasting, multi-echelon optimisation, seasonal profiles, fair-share allocation … Relocated, not refused — a planning module with its own band, consuming a forecast through an interface. FR-258 is the boundary"* | The planning module's reason to exist. It rules forecasting out of the warehouse core, not out of the product. The "interface" it names was never specified | **AMEND**: record in DECISIONS that `warehouse-planning` (or a similar name) *is* the relocated module. Define "the interface" as a contract (§4) | **YES** |
| **Refusal #9** (FRD §10; GAP-REGISTER `P-052` WONTFIX) | *"Service-parts planning — initial provisioning, last-time-buy, rotable pools, installed base, PBL … The same planning module"* | Same as #8. `P-052` is marked **WONTFIX**, so no task traces it | **AMEND**: move `P-052` from WONTFIX to a disposition that points at the new module's backlog. Otherwise `tools/check-design-set.py` still counts it as resolved | **YES** |
| **Refusal #7** slotting solver | *"the optimiser is an operations-research problem … Report the recommendation in v3 and let a human move the stock"* | A MEO or network solver has the same shape: an optimiser whose output a human applies | **KEEP**, and use the same pattern: planning recommends and a human approves | NO |
| **Refusal #11** rules engine / scripting | *"A new bounded operator, reviewed once. Never an interpreter"* | Autopilot rules, exception rules and policy-selection logic must be **typed bounded rows**, not user expressions | **KEEP**, and make planning policy tables bounded and typed | EARLY |
| **Refusal #24** workflow designer | *"A new bounded column on `wh_approval_levels` … Never an interpreter"* | Recommendation-approval chains must reuse `wh_approval_levels` (FR-466) or add bounded columns | **KEEP** | EARLY |
| **Refusal #12** JSONB bags | Forbidden (platform rule) | Forecast model parameters, scenario assumptions and explanation payloads cannot go in JSONB. They need typed child tables or TEXT (as in `wh_blocked_movements.attempted_payload TEXT`) | **KEEP** | YES (schema design) |
| **Refusal #13 / OD-3 / FR-440** multi-tenant | *"One database per customer installation. A 3PL client is an owner … never a database tenant"* (OD-3 RESOLVED) | A **dealer-network** planner spanning independent dealers, meaning separate legal entities in separate installs, cannot read across installs. Only multi-company *inside one install* works | **ADD** an explicit dealer-network decision: either one install with many companies or owners, or federation by import/API. Never a shared DB | EARLY (before dealer-network work) |
| **Refusal #17 / #18 / FR-274** no invoice, refund or payment | *"A refund is a receivable event … belongs where the receivable lives"* | **Pricing** in planning (price levels, core charges, warranty credits) must not become a receivable inside warehouse or planning | **KEEP**. Pricing lives in a price master. Receivables stay in accounting | EARLY |
| **Refusal #23** marketplace catalogue/price sync | Channel tool owns listing and price | Planning pricing must not grow channel price sync | **KEEP** | NO |
| **Refusal #25** consignment-to-customer auto-invoice | Stock at a customer is modelled (FR-113); converting to sale is accounting's | Dealer-network consignment and VMI planning can read the position but cannot invoice | **KEEP** | NO |
| **FR-268 / P6-12 (#144)** multi-level BOM not built | *"belongs to a manufacturing module"* | Planning's **installed base / part–equipment applicability** is not a BOM with routings, but it could be mistaken for one. Needs its own table | **ADD** an applicability model in planning (equipment model ↔ part, dated). Record that it is not FR-268's BOM | EARLY |
| **FR-142 / P6-05 (#112)** supplier scorecard not built here | *"the supplier scorecard itself is a supply-chain concern and is not built inside warehouse"* | Planning needs lead-time **mean and variance**, OTIF and ASN accuracy. Warehouse only *emits evidence*, and P6-05 is still open | **KEEP** the boundary. Planning (or a supply-chain module) owns the scorecard. **Schedule P6-05 before** service-level stocking | EARLY |
| **FR-228 / P6-03** no engineered standards before a year of data | Pattern: *measure, don't guess* | The same principle applies to forecasts: refuse or mark a forecast as provisional below a history threshold (P6-02 already does this for levels) | **KEEP** and adopt the pattern | NO |
| **IMPLEMENTATION-PLAN §P6 "does not do"** | *"demand forecasting inside warehouse"* | Consistent with #8 | **KEEP** | NO |
| **§6.14 preamble** | *"a WMS holds reorder point, min/max and safety stock as item-site attributes … forecasting, multi-echelon optimisation and purchase planning belong to a planning product"* | Planning **writes** those attributes. Warehouse only reads them | **AMEND**: add "and who may write them" (see DM-1) | **YES** |

### 1.2 D-decisions (DECISIONS.md §2)

| ID | What it says | Impact on planning | Action | Pre? |
|---|---|---|---|---|
| **D-1** five modules | `warehouse-base`, `warehouse`, adapter, `-3pl`, `-india` | Planning is a **sixth** module. It is not an adapter, because adapters are ruled out (#102/#108) | **AMEND**: add `warehouse-planning` (package `ai.warehouseplanning`, a sibling like the adapters so that `@ComponentScan("ai.warehouse")` does not auto-load it) | **YES** |
| **D-2** bands | *"Five modules get a band; nothing else does."* Warehouse is V500000–V549999. V130000–V599999 was "entirely empty" when D-2 was written | Planning needs a band. The PTC note proposes **V550000–V559999**. Check first that it is free: CLAUDE.md's MODULES table shows nothing in V550000–V599999, but D-2's "empty" claim is out of date (a dealer inventory adapter now uses V130000+) | **AMEND** D-2 and CLAUDE.md's MODULES table. Also add the band to `WarehouseBaseCouplingTest.warehouseBands()` and to `tools/check-design-set.py` | **YES** |
| **D-3** prefixes | `whb_`, `wh_`, `wh3_`, `whin_`, `wha*_`. No `wms_`/`scc_` | Planning needs its own prefix (for example `whp_`). **Do not use `spi_`**, because the old SPI docs use `wms_*` names (PTC doc §10 row 5) | **ADD** a prefix | **YES** |
| **D-4 / L-1–L-4 / IRR-01–02** double-sided, append-only ledger. Positions are a cache | *"Neither is a ledger. Do not copy either."* | Planning must **never write stock or positions**. Its outputs (orders and transfers) go through the existing document services and the port | **KEEP** | YES (architecture test) |
| **D-5 / IRR-06** `owner_id` NOT NULL everywhere | Owner in the position key | Planning must plan **per owner**. Today's engine plans **HOUSE-owned stock only** (PTC doc §4). `wh_demand_history` has **no owner_id** | **AMEND**: owner-scoped planning needs owner on the demand history (DM-3) | EARLY |
| **D-6** quantity authority = cost authority; accounting owns the ledger | Warehouse runs costing | Inventory-investment and budget what-if scenarios read **warehouse cost** (`whb_cost_layers`), never `acc_*`. #169–#172 (costing gaps) make the values unreliable today | **KEEP**, with dependency on #169–#172 | EARLY |
| **D-7** standalone is the reference config | No v1 capability requires another module | Warehouse must run **without** planning, and planning must degrade clearly without warehouse. This is the FR-336 deletion test | **KEEP**, and add FR-336-style deletion tests for planning | YES |
| **D-8** country-neutral core | No GST or MRP logic in core | Planning must not hard-code India rules. However, rebalancing cost across GSTINs is a taxable supply (FR-461, OD-19), which a network planner must see through a provider or hook | **ADD** a hook: "transfer is taxable supply" read from `whin_`/provider, never computed | EARLY (multi-echelon) |
| **D-9** accessories stays separate | Two stock truths, no union (OD-15/OD-20: side-by-side, **no grand total**) | Planning cannot plan accessories stock. The PTC doc's idea to "reuse the `accessories` pricing model" crosses this boundary | **KEEP**. Planning scope = warehouse-owned categories per `whb_category_stocking_ownership`. **REVERSE the reuse idea**: price master goes elsewhere (§2.10) | YES (scope statement) |
| **D-10 / FR-375 / OD-5** open vocabularies are catalogue tables, no CHECK, no TS union | 13 registries | Demand stream, forecast method, policy type, exception type and recommendation status must be **catalogue rows**. The frontend fetches them | **KEEP** | YES (schema design) |
| **D-11** adapters proved by test. Must not write `whb_`/`wh_` directly or add base columns | Arch test and zero commits to base | Planning is not an adapter, but the same risk applies: planning writing `whb_item_site_settings` directly is the forbidden pattern. P6-02's own write is inside `warehouse` and legal | **ADD** a rule: planning publishes targets through a **warehouse service API** (policy-publish endpoint), never by direct table write. Add an ArchitectureInvariantsTest | **YES** |
| **D-12** v1 is a cut line; every finding placed | `check-design-set.py` fails on untraced findings | Planning findings (from the PTC gap analysis, G1–G19) must be registered and dispositioned | **ADD** a gap register or planning backlog | EARLY |
| **D-13** mobile is not optional | Web↔mobile mirroring | The PTC doc says the planner workbench is desktop-only and van counting is the exception. That needs an explicit `D-13` declaration per task (P6-02 already declares `none`) | **KEEP**, with per-task declarations | NO |
| **D-14** dated many-to-many associations; exactly one REGISTERED branch | Junctions are effective-dated with EXCLUDE | (a) The planning network topology (hub ↔ branch, dealer ↔ supplying DC) is an **association** and must be a dated junction. (b) FR-254 defines "sister" by REGISTERED branch, which is a tax notion, not a network one | **ADD** a dated `site_supply_lanes` junction (source site → destination site, lane lead time, priority) | EARLY (multi-echelon) |
| **D-15** posted moving average never restated. Backdated receipt inserts a layer | `moving_average_after` snapshot | Scenario and time-travel valuation must read snapshots and layers, and must never recompute history | **KEEP** | NO |

### 1.3 L-invariants and IRR items

| ID | What it says | Impact on planning | Action | Pre? |
|---|---|---|---|---|
| **L-6** ATP = max(0, allocatable − reservations). Negative on-hand is policy | Availability semantics | Planning's "usable stock" input must use the same ATP and `is_allocatable` stock-status flags (IRR-10). Quarantine, returns and warranty-hold statuses are not usable supply | **KEEP**, and consume FR-174 | NO |
| **L-10 / IRR-45** reservations are rows with a holder quad and `expires_at` | Open-item ledger | Committed demand = open reservations plus demand lines. Planning must not double count a reservation and its demand line | **KEEP** | NO |
| **L-12 / IRR-24** lineage quad on every movement | Source-document traceability | Planning outcome tracking (recommendation → PO → receipt) can use the quad, **but only if** POs and transfers carry the planning recommendation id (DM-9) | **KEEP**, and **ADD** the seam id | EARLY |
| **L-13 / IRR-21** three timestamps (`occurred_at`, `recorded_at`, `posting_date`) | Never collapsed | Time-travel ("what did we know on date X") needs **`recorded_at`**, not `occurred_at`. Late-arriving movements change past demand. Planning snapshots must record both | **KEEP**. Planning input snapshots must state the clock (RC-001 rule, #178) | YES (contract) |
| **L-14** non-own stock never valued | Custody only | Consignment and VMI inventory investment is not a warehouse value. Budget scenarios must exclude or separate it | **KEEP** | NO |
| **L-15 / OD-11/13/14** value-only movements conserve value | VALUE_OFFSET | Revaluation from price files (FR-419) or obsolescence write-downs proposed by planning must be movements, approved by accounting (FR-240) | **KEEP** | NO |
| **OD-12 / IRR-62 / FR-022** ledger partitioned by `occurred_at`. *"no partition is ever closed"* | Late arrivals write old partitions | Demand re-derivation from the ledger for a closed month can change. Planning backtests must pin the snapshot (`recorded_at ≤ cutoff`) | **KEEP**, and planning snapshotting (DM-12) | YES |
| **IRR-23 / FR-180** lifecycle timestamps on headers | PO `submitted_at`, `acknowledged_at`, `first_receipt_at`, `received_at`, `closed_at` are built | Lead-time actuals are derivable (WhSupplierLeadTimeQueryService excludes VOR/EMERGENCY). They are **header-level only**: no per-line promised or confirmed date and no per-receipt-line lead time | **ADD** line-level supplier-confirmed date (DM-5) | EARLY (service-level SS) |
| **IRR-48** `actor_type` includes `SCHEDULED_JOB`, `INTEGRATION` | Who moved it | Planning-originated documents must post with `actor_type = INTEGRATION/SCHEDULED_JOB` and a named human approver, so autopilot is auditable | **KEEP** | NO |
| **IRR-50 / IRR-66 / PC-42 / PC-43 / PC-38** outbox, fixed event catalogue, **dimension set fixed in v1** | *"Add a dimension to an existing outbox event: no, in effect"* (PC-38) | Planning's durable feed. The catalogue has **no demand-signal events**: no `lost_sale.captured`, no `demand_line.created/backordered`, no master-data events (item, supersession, item-site policy). New *codes* are additive (PC-43 seed INSERT). New *dimensions* on existing events are not | **ADD** event codes now: `demand.line.created`, `demand.line.backordered`, `lost_sale.captured`, `item_site_policy.changed`, `supersession.changed`, `po.line.confirmed`. The earlier they ship, the more history planning can replay | **YES** (every day of delay is unrecoverable history) |
| **IRR-51** daily position snapshot from v1 | `whb_stock_position_snapshots` (built) | Supports **stock-out-day censoring** (demand while at zero stock) and historical inventory for scenario baselines | **KEEP**, and planning reads it | NO |
| **IRR-11** condition axis separate from workflow status | Condition ≠ status | Repairable/defective/serviceable planning (cores, rotables) needs condition as a separate axis. It exists | **KEEP** | NO |
| **IRR-30 / FR-088** location custody dated junction (`CUSTODIAN`/`DRIVER`/`HELPER`), MOBILE/VEHICLE location types | Van stock = a location (built, V500013; types seeded) | Van/field stock planning has its **object** but lost its **workflow** (van replenish, consume at job close, unreturned-part ageing: FR-363, #102 not required) | **AMEND**: re-scope van replenishment onto `warehouse` (vertical-neutral) as its own task. Do not resurrect the adapter | EARLY (field-stock feature) |
| **IRR-31** item types incl. `CORE`, `RETURNABLE_EQUIPMENT`, `TYRE` seeded | Built | Cores have a type but no ledger or workflow (#81 void) | See §2.6 | EARLY |
| **IRR-32 / FR-146** reason code `affects_demand_history` | Built, and read by `WhDemandHistoryRecorder` | This is a single boolean. Planning needs **demand streams** (paid, warranty, internal, maintenance), not include/exclude. Warranty demand is real physical demand for availability planning (PTC doc §8) | **AMEND**: add a `demand_stream_code` (catalogue) to reason codes or movement types. Keep the boolean for FR-393's frozen KPI | EARLY |
| **IRR-25/26** external refs and stable codes | `whb_item_external_refs` and item `code` | Planning must key on `whb_items.id`/`code`, not a second part master. Installed-base or equipment IDs from assets/services map through external refs | **KEEP** (PTC doc §8 item 6) | YES |
| **IRR-40 / FR-236** valuation grain `(company, owner, item, site)` | Declared | Inventory budget scenarios aggregate at this grain | **KEEP** | NO |
| **PNR-3** (IRREVERSIBLE §3.2) *"The first movement posted in any install"* | Observation not captured is gone | **Demand signals not captured by warehouse today are lost for planning.** That covers per-line promised dates, lost-sale resolution and the requested (asked-for) part when a substitute is sold outside allocation. **`wh_demand_history`, lost sales and demand streams are not in IRREVERSIBLE.md** even though they are UB-class | **ADD** IRR rows for demand-signal capture (lost sale with resolution, requested item, demand stream, supplier confirmed date) | **YES** |

### 1.4 Open decisions (OD-n) and adopted settings

| ID | Status | Impact on planning | Action | Pre? |
|---|---|---|---|---|
| **OD-2** vehicle inventory | **Withdrawn** 2026-09-23 (#134: *"should not be re-opened in a later phase"*) | Installed-base planning for **vehicles** (dealer parc) cannot use warehouse serials for vehicles. Parc must come from dealer/automotive by reference | **KEEP**. Planning reads parc from the source vertical through an import or read contract | EARLY |
| **OD-3** one DB per install | Resolved | See refusal #13 | KEEP | EARLY |
| **OD-4** counterparty master stays in base; other products join by external refs | Resolved | Supplier identity for planning = `whb_counterparties`. No second supplier master | **KEEP** | NO |
| **OD-6** FIFO and AVCO v1, standard v1.1, no LIFO | Resolved (#169 shows AVCO/FIFO only; STANDARD refused by engine) | Planning's per-unit cost for EOQ and budget reads layers. Standard cost variance is not available yet | KEEP | NO |
| **OD-7** precision (18,4 qty; 19,4 money; 19,6 per-unit; 9,6 percent; 18,8 conversion) | Resolved. P6-02: *"No float or double anywhere, including the frontend DTO"* | Forecast and stat libraries compute in double. Planning must **round at the persistence boundary** and state its rounding. Service-level targets = `DECIMAL(9,6)`. Forecast quantities = `DECIMAL(18,4)` | **KEEP**, and **ADD** a planning-local rule: doubles allowed in memory, never stored or returned | YES |
| **OD-8** out-of-process auth | Resolved: user JWT; service consumers wait for the v3 identity adapter. P5-22 API keys only narrow a JWT | A **separately deployed** forecasting service or scheduled autopilot has no service principal | **ADD** (or wait for) a platform service principal. Until then planning runs **in-process** | **YES** (deployment model choice) |
| **OD-16** foreign currency: base-currency cost, rate frozen | Resolved | Budget scenarios in base currency only | KEEP | NO |
| **OD-18** drop-ship v2 | Resolved, default disabled | Drop-shipped demand never touches a site, so planning must decide whether it is demand for stocking (normally not) | **ADD** a demand-stream rule | NO |
| **OD-19** cross-GSTIN registration change refused with stock | Resolved | Network rebalancing across GSTINs = taxable transfer (FR-461) | KEEP, and model as a cost in the planner | EARLY |
| **OD-20** no union valuation total | Default (#178) | Planning dashboards must not total warehouse and accessories inventory | KEEP | NO |
| **GLOBAL-SETTINGS** `warehouse.approval.pending_alert_hours`: *"never auto-approve"*; `warehouse.adjustment.auto_post_below_thresholds` (install-scope, default false) | Adopted 2026-09-11 / 09-18 | **Autopilot conflicts.** The only precedent for auto-posting is an install-scope boolean for low-value adjustments | **AMEND** (see §2.9): a bounded, per-policy autopilot band modelled on `auto_post_below_thresholds` + FR-466 value bands. Never "auto-approve everything" | **YES** (business decision) |

### 1.5 FRs and tasks that are decisions in themselves

| ID | What it says | Impact | Action | Pre? |
|---|---|---|---|---|
| **FR-253** | *"The warehouse never becomes a purchase-order engine … No purchase order is raised automatically; the human still accepts"* | Directly blocks autopilot purchase release | **AMEND** (§2.9) | **YES** |
| **FR-258 / P6-02 (#99)** | *"The best stocking level is computed, not typed"*; *"never from a forecast"*; *"writes the item × site reorder point"*; override *"survives the next run"* | (a) It is the boundary object: historical policies live in `warehouse`, forecast-driven ones in planning. (b) Two writers of one column. (c) Its override-retention design is exactly what planning also needs | **AMEND P6-02 before it is built**: store the computed level in its own history table, and add a **policy-authority** column on the item-site row (`MANUAL` / `HISTORICAL_POLICY` / `PLANNING`) plus a pointer to the producing run. Planning then writes through the same authority mechanism. Do not open a second issue (PTC doc §9) | **YES** |
| **FR-254** | Sister = *"a site with a different `REGISTERED` branch"* | A tax definition used as a network definition. Two sites under one branch are never sisters, and sister ≠ supplying DC | **AMEND**: keep for FR-254. Planning uses supply lanes (D-14 row) | EARLY |
| **FR-257** | Lost sales captured with *"a type and a resolution"* | `wh_insufficient_stock_log` has `is_lost_sale`, `lost_sale_reason_code_id`, `captured_manually`. **No resolution column** was found, and there is no customer or requested-alternative link | **ADD** resolution (e.g. `SUBSTITUTED`, `BACKORDERED`, `LOST`, `SPECIAL_ORDERED`) so a lost sale later fulfilled is not counted twice (PTC doc §8) | **YES** (PNR-3 class) |
| **FR-260** | PO carries order source, *"customer-waiting flag, a linked job reference and a promised date"*; VOR/emergency excluded from lead-time stats | `order_source` built. VOR/EMERGENCY exclusion built in `WhSupplierLeadTimeQueryService`. **Customer-waiting flag, job reference and promised date are not in `wh_purchase_orders`** (column list checked) | **ADD** the three columns. They are FR-required already, v1 | **YES** |
| **FR-165** | *"A threshold column with no scheduled job that reads it is a defect"* | Every planning threshold (service-level target, phase-out months, LTB horizon) must ship with its job | KEEP | NO |
| **FR-393** | Frozen fill-rate, turns, obsolescence and days-supply definitions | Planning outcome KPIs must **register new metrics** (FR-470 catalogue) rather than redefine these. The fill-rate denominator depends on lost-sale hits | **KEEP**, and register planning metrics separately | NO |
| **FR-405 / #185** warehouse-scoped access, and scheduled reports cannot be scoped per recipient | Platform `ReportDataProviderInterface` has no principal | Planner digests and exception emails cannot be sent as scheduled platform reports without leaking other sites' data | **ADD** a platform change (per-recipient provider) or use in-app notifications only | EARLY |
| **FR-408 / FR-466** approver ≠ actor; bounded value-banded levels | Built at v1 / v2 | Planning approval of recommendations uses these. Autopilot = a system actor, which FR-408 does not contemplate | **AMEND**: define whether `SCHEDULED_JOB` may be the *maker* when a human policy owner approved the *policy* | **YES** |
| **FR-419 / FR-420** OEM price file and OEM order/ack interface | FR-420 **void** (#95). FR-419 was delivered in #90, but its tables (`whad_price_files`) were adapter-owned | Pricing, supersession-from-price-file and OEM ETA per line (`whad_oem_order_lines.eta_date`) have **no home** | **ADD** (§2.10) | EARLY |
| **FR-461** serving-branch rule; cross-GSTIN draw = taxable transfer | Built | Constraint for rebalancing | KEEP | NO |
| **FR-470** KPI targets as data (`whb_metric_definitions`, `wh_metric_targets`) | v1 | Reuse for service-level targets per class? A metric target is a KPI goal, not a stocking-policy input. Keep them separate but link | **KEEP**, and planning registers metrics via INSERT | NO |
| **P6-01 / FR-023** archiving writes `OPENING_BALANCE` then moves rows | v3 | After archiving, demand **cannot be re-derived from the hot ledger** for archived months. Planning must keep its own demand store and not rely on ledger re-derivation | **AMEND P6-01**: archiving must not start until planning's demand store (or `wh_demand_history` with streams) is authoritative | EARLY |

---

## 2. Capability-by-capability conflicts

### 2.1 Forecasting
- **Conflicts:** Refusal #8 in warehouse (fine, because it is relocated). P6-02 *"never from a forecast"* is fine for P6-02 but must not block planning from writing. OD-7 bans doubles in storage.
- **Depends on:** `wh_demand_history` (built, V510070), FR-415 import (built, #90, `is_migrated`), IRR-51 snapshots (built), lost sales (built, partial).
- **Gaps:** monthly grain only. No owner. No stream. No stock-out-day censor flag. No forecast storage anywhere. The demand-history import is monthly too.
- **Needed before:** demand-stream decision (IRR-32 row), PNR-3 additions, and the P6-02 authority column.

### 2.2 Service-level stocking
- **Depends on:** `whb_item_site_settings` (ROP, SS, min, max, ROQ, `lead_time_days`, ABC/XYZ/VED/FSN/HML/velocity; built V500050). `whb_item_supplier_sources` (dated, lead time, MOQ, order multiple; built).
- **Gaps:** no service-level target column. No lead-time variance. `lead_time_days` is an INTEGER with no source. No criticality column: `ved_class` is the only proxy. `DATA-MODEL.md:4749` says *"`is_vor_eligible` and `criticality_level` become item columns"*, but **neither is in the `whb_items` key-column list nor in any migration** (grep = 0). That is a design-set inconsistency. No review cycle or order frequency.
- **Conflict:** single writer. P6-02 and planning both target the same columns (see FR-258 row).

### 2.3 Multi-echelon / network
- **Depends on:** FR-254 sister-transfer heuristic (built #96, HOUSE-owned only). FR-174 availability API with in-transit and on-order (built). `wh_transfer_orders` + in-transit.
- **Conflicts:** sister is defined by REGISTERED branch (FR-254/FR-073). Cross-GSTIN transfer = taxable supply (FR-461/OD-19). D-14 requires dated junctions for any topology. D-8 means no GST logic in core.
- **Gaps:** no supply-lane / echelon table. No inter-site transfer lead time. No hub designation.
- **#177:** emergency replenish is unbuildable as specified. **#176:** bin-to-bin move has no owner. Both affect execution of planning-triggered internal moves.

### 2.4 Supersession-aware demand
- **Built:** `whb_item_supersessions` (V500050: type REPLACES/INTERCHANGE/PARTIAL, `chain_sequence`, `quantity_ratio DECIMAL(9,6)`, effective/end date, `stock_treatment`, `is_bidirectional`). The chain response exists. Allocation consults the chain (FR-176, V500038 `allow_supersession`). `whb_reservations.requested_item_id` exists (V500038), so **#167 is largely stale** (PTC doc §6).
- **Gaps:** FR-071 says *"Every lookup path — counter enquiry, workshop request, reorder, receipt matching, barcode scan — goes through the resolver"*. A grep finds supersession consumers only in allocation and master-merge. **Replenishment, scan resolution and demand history do not use the resolver.** MERGE_DEMAND has no consumer (**#168**). `wh_demand_order_lines.original_item_id` exists. Lost-sale rows do not record the requested-vs-offered item.
- **Precision note:** `quantity_ratio DECIMAL(9,6)` caps at 999.999999. That is fine for parts, but it is the percent type, which OD-7's tie-break reserves for `*_ratio`, so it is consistent.
- **Action:** #168 is the first data-foundation fix. Decide whether the merge happens **in `wh_demand_history`** (warehouse) or in planning's transformed demand. Recommendation: keep raw per-item history in warehouse and do the chain roll-up in planning with ratio and effective date. That avoids a history rewrite when a supersession is corrected. Then **re-word #168's acceptance** accordingly. It still names the removed dealer adapter.

### 2.5 Repair / cores / warranty
- **Cancelled:** #81 (P5-15 *Cores are inventory, and warranty scrap-and-hold*) is **VOID**. *"If cores-as-inventory is wanted later it must be re-scoped onto `warehouse`/`warehouse-base` with numbers from their own bands."*
- **Surviving foundations:** `CORE` item type (seeded). Condition axis (IRR-11). `return_type` includes WARRANTY (FR-270). Serial warranty start/end (FR-099). Dispositions registry (FR-273).
- **Gaps:** no core ledger or due date (`whad_core_exchanges` never built). No warranty-hold location workflow (`whas_warranty_holds` never built). No repair order, turnaround or yield. Warranty issues are **excluded** from demand history, not kept as a separate stream.
- **Action:** re-scope FR-277/FR-278 onto `warehouse` (vertical-neutral) only if a repair-heavy pilot needs it (PTC doc §5). Repairable *supply planning* belongs in planning. The *core and warranty custody ledger* belongs in warehouse.

### 2.6 Van / field stock
- **Cancelled:** #102 (P3-20 field-service adapter): *"NOT REQUIRED … No warehouse adapter module is built"*. #108 (assets adapter) was cancelled the same way.
- **Surviving:** FR-088 custody junction. MOBILE/VEHICLE location types. Transfers.
- **Gaps:** no job-close consumption path, no van min/max workflow, no unreturned-part ageing (FR-363 lost). Consumption at a van is demand at a **mobile location**, but `wh_demand_history` is item × *site*. Van demand either rolls into the parent site or needs location grain.
- **Action:** decide the demand grain for mobile locations (site vs location) **before** demand-stream work.

### 2.7 Dealer network
- **Conflicts:** user decision 2026-09-23 *"no dealer-management or vehicle-management work in warehouse"* (#134). Dealer adapter deleted (#150). OD-3 one DB per install. OD-2 withdrawn.
- **Depends on:** owner dimension (consignment/VMI, FR-113). Multi-company within one install (IRR-17 `company_id`).
- **Action:** a **product decision** is needed. Either dealer-network planning is out of scope for the SMB pilot (as the PTC doc recommends: defer), or it is built on an import/API feed of dealer stock and demand with no shared DB. Record it in DECISIONS as a new OD.

### 2.8 Scenarios / time-travel
- **Supports:** L-13 three clocks. IRR-51 daily snapshots. FR-174 as-of date. D-15 no restatement. `whb_item_supplier_sources` dated.
- **Gaps:**
  - **`whb_item_site_settings` is not dated.** It has a `version` column but no history, so "what was the ROP on 1 March" is unanswerable. That is the core of policy backtesting.
  - **#179:** WS-224 as-at is a 365-day windowed net, not a balance.
  - **#182:** WS-212 ageing scans the whole ledger (unmeasured cost).
  - The ledger's `occurred_at` partitions are never closed (OD-12), so re-derived history drifts.
- **Action:** **ADD** a dated policy-history table (warehouse-owned, written by every policy change including P6-02 and planning). Planning keeps **immutable input snapshots** (PTC doc §8 items 2 and 6).

### 2.9 Autopilot / auto-approval
- **Conflicts (all explicit):** FR-253 *"No purchase order is raised automatically"*. RK-004 *"no auto-PO"*. GLOBAL-SETTINGS *"never auto-approve"*. FR-408 approver ≠ actor. Refusals #11 and #24 (no interpreter, no workflow designer).
- **Precedent to reuse:** `warehouse.adjustment.auto_post_below_thresholds` (install-scope boolean, default false, decision 2026-09-18) and FR-466 value-banded `wh_approval_levels`.
- **Recommended amendment:**
  - Autopilot is a **bounded, per-policy** release band: item class × value ceiling × supplier, stored as typed rows.
  - A human **approves the policy**, with maker ≠ checker. Documents released under it carry `actor_type = SCHEDULED_JOB` and a `released_under_policy_id`.
  - It is off by default. It is never an expression language.
  - This **reverses the letter of FR-253** for opted-in policies and must be a recorded DECISIONS amendment. The PTC doc recommends deferring autonomous purchasing, so it can wait. The *decision* must still exist before any planning schema assumes a human accept step.

### 2.10 Pricing
- **Removed:** `whad_price_levels`, `whad_item_prices` (WS-239) and `whad_price_files` all went with the dealer adapter (#150). `whb_item_supplier_sources` is deliberately *"No price"*. The only cost on the item is `standard_cost`.
- **Conflicts:** refusals #17/#18/#23. D-9 (the PTC note proposes reusing accessories pricing, which crosses the permanent separation).
- **Action:** **ADD** a decision on who owns the price master (sell prices, core charges, supplier price lists). Options: a planning-owned price table, a platform or commercial module, or re-scoping FR-359/FR-419 into `warehouse`. Pricing *optimisation* stays deferred (PTC doc §7).

---

## 3. Data-model gaps (tables relevant to planning)

| # | Table (migration) | Exists | Missing for planning | Class | Pre? |
|---|---|---|---|---|---|
| **DM-1** | `whb_item_site_settings` (V500050) | ROP, SS, min, max, ROQ, `lead_time_days`, abc/xyz/ved/fsn/hml/velocity/count-freq, `previous_abc_class`, `abc_computed_at` (V500050, but **no Java writes them**), `negative_stock_mode`, `near_expiry_days`, `version` | `policy_authority` (MANUAL/HISTORICAL/PLANNING), `policy_run_id`, `override_reason`/`override_by`/`override_until`, `service_level_target DECIMAL(9,6)`, `review_period_days`, `lifecycle_phase` (phase-in/active/phase-out per site), `criticality_code`, **effective-dated history** | Additive, but history before the change is **lost** (UB) | **YES** |
| **DM-2** | `whb_items` (V500015) | `lifecycle_status` (NEW/ACTIVE/PHASE_OUT/OBSOLETE/BLOCKED), four status facts, `style_item_id`, `standard_cost`, `shelf_life_days` | `criticality_level` and `is_vor_eligible` (claimed at DATA-MODEL:4749 but absent), `end_of_support_date` / `last_time_buy_date`, `is_repairable`, `mean_time_between_failure` (installed-base), `introduction_date` (initial provisioning) | Additive | EARLY |
| **DM-3** | `wh_demand_history` (V510070) | item, site, `YYYYMM`, hits, qty, lost-sale count/qty, `is_migrated`. Maintained by posting; excludes `TRANSFER_DEPART` and `affects_demand_history=false` | `owner_id`; `demand_stream_code`; finer grain (week/day) or a raw demand-event table; `stockout_days` / censor flag; history-coverage start; location grain for vans | Additive for the future, **UB for the past** (re-derivable from the ledger only until archiving, P6-01) | **YES** |
| **DM-4** | `wh_insufficient_stock_log` (V510034 + `item_description`) | warehouse, item, owner, location, requested/available qty, source, policy, `is_lost_sale`, reason, `captured_manually` | **resolution** (FR-257 requires it), `requested_item_id` vs offered substitute, customer counterparty, demand-order line link (de-dup of lost-then-fulfilled) | **UB (PNR-3)** | **YES** |
| **DM-5** | `wh_purchase_orders` / `_lines` (V510011, V510021) | header `order_source`, `expected_delivery_date`, `acknowledged_at`, `first_receipt_at`, `received_at`, `closed_at`, `replenishment_suggestion_id`. Line `expected_delivery_date`, received/accepted/rejected/cancelled/remaining | FR-260's **customer-waiting flag, linked job ref, promised date**; line-level **supplier-confirmed date** and ack quantity (was `whad_oem_order_lines.eta_date`, now gone); `planning_recommendation_id` | UB for lead-time-variance history | **YES** |
| **DM-6** | `whb_item_supplier_sources` (V500050) | dated; lead time, MOQ, order multiple, preferred, priority | lead-time **std-dev / source** (quoted vs measured), site scope (v2 FR-468), price (deliberately absent) | Additive | EARLY |
| **DM-7** | `whb_item_supersessions` (V500050) | see §2.4 | `demand_treatment` separated from `stock_treatment` (today one column mixes KEEP_SEPARATE/MERGE_DEMAND/MERGE_STOCK, so a supersession cannot be both merge-demand and merge-stock); chain/group id; source (price file / manual) | AMEND: small | EARLY |
| **DM-8** | `wh_replenishment_runs` / `_suggestions` (V510070) | run type incl. SCHEDULED, `basis_note`, suggested source PURCHASE/TRANSFER, accept/reject with reason, resulting document | `policy_authority` of the ROP used, `planning_recommendation_id`, exception type; HOUSE-owner-only scope must be stated as a decision | Additive | EARLY |
| **DM-9** | Seam columns (`P-052`) | `wh_purchase_orders.replenishment_suggestion_id` (≈ `spi_recommendation_id`, but it points to a *warehouse* suggestion). SPI-writable stocking/classification fields exist (DM-1) | **`spi_order_id` equivalent on `wh_demand_orders` / `wh_transfer_orders`** (a planning-originated transfer or rebalancing order); a planning recommendation id on transfers | Additive; lineage for past orders is **UB** | **YES** |
| **DM-10** | `whb_location_user_assignments` (V500013), location types MOBILE/VEHICLE | built | van min/max are in `whb_item_location_settings` (built, P3-12). No job-consumption link | — | EARLY |
| **DM-11** | Network topology | **none** | dated `site_supply_lanes` (from/to site, lead time, cost, priority, echelon) | ADD | EARLY |
| **DM-12** | Planning-owned (new band) | **none** | input snapshots (with `recorded_at` cutoff), forecast versions, policy runs, recommendations, exceptions, scenario results, backtest results, installed-base/applicability, price master (if decided) | ADD | YES |
| **DM-13** | `whb_stock_position_snapshots` | built (IRR-51) | — (use for censoring) | KEEP | NO |
| **DM-14** | `wh_metric_definitions` / `wh_metric_targets` (FR-470) | v1 | planning metric codes (INSERT) | KEEP | NO |

---

## 4. Contracts planning needs (none exist today)

1. **Planning-input contract.** Item, site, owner and company identity; base UoM; usable stock (L-6); commitments (L-10); dated open supply; demand by stream; and the source event id plus cursor. This is the "interface" refusal #8 promises (PTC doc §8.1).
2. **Event feed.** Extend the PC-42 catalogue with demand, lost-sale and master-data events (§1.3 IRR-50 row). Planning deduplicates on `(subscriber_code, cursor)` (PC-44).
3. **Policy-publish contract.** Planning → warehouse service. It sets targets with an authority, run id and approval. It never writes tables directly (D-11 analogue). Overrides survive (P6-02 acceptance).
4. **Execution contract.** Approved recommendations create POs and transfers through the existing document services, idempotent on the recommendation id (*"Re-running the same accepted recommendation cannot create duplicate supply"*, PTC doc §9 pilot criteria). Source-site approval for transfers is kept.
5. **Scope contract.** FR-405 site scope and IRR-60 owner grants apply to planning reads, jobs and exports. #185 blocks scheduled per-recipient delivery.
6. **Clock contract.** Every planning read declares its clock: `occurred_at`, `recorded_at` or `posting_date` (RC-001, #178).

---

## 5. Planning-relevant FRs: built / not-built status

Status comes from migration and Java greps in `classic` plus GitHub issue state. "Verify" means I did not confirm it in code.

| FR | Short | Ver/Ph | Status | Evidence |
|---|---|---|---|---|
| FR-050 | 4 status facts + `lifecycle_status` | v1 P1 | **Built** | `whb_items` column; 9 migration refs |
| FR-053 / FR-252 | ROP/SS/min/max/ROQ/lead time at item×site (v1), item×location (v1.1) | v1·v1.1 | **Built** | V500050; `whb_item_location_settings`; #61 P3-12 |
| FR-070 | ABC/velocity/count-freq columns (v1); velocity/XYZ recompute v3 | v1·v3 | **Columns built; recompute not built** | V500050; no Java writes `abc_computed_at` |
| FR-071 | Supersession chains + resolver on *every* lookup path | v1 P1 | **Partial** | Table and chain built (#149). Resolver used only by allocation and master-merge |
| FR-072 | Stock/demand treatment | v1 P2 | **Stored; MERGE_DEMAND not consumed** | #168 open |
| FR-073 | Interchange bidirectional + counter enquiry across branches | v1 P2 | **Partial** | Rows built. Counter enquiry lived in the deleted dealer adapter |
| FR-074 | Vehicle fitment in dealer adapter | v1 P2 | **Removed** | #150 adapter deleted |
| FR-088 | Dated custody; van = location | v1 P1 | **Built** | V500013 |
| FR-099 | Serial warranty start/end, sold-to | v1 P2 | Verify | — |
| FR-113 | Consignment / VMI / customer-owned as owner types | v1·v2 | Base v1 built (owner model) | D-5 |
| FR-142 | Receipt facts emitted; scorecard not built here | v3 P6 | **Not built** | #112 (P6-05) open |
| FR-146 | `affects_demand_history` | v1 P2 | **Built** | read by `WhDemandHistoryRecorder` |
| FR-174 | Availability API (as-of, in-transit, on-order) | v1 P2 | **Built** | #34 P0-03 |
| FR-176 | Allocation may consult supersession | v1 P2 | **Built** | V500038 `allow_supersession`; `WhbAllocationService` |
| FR-177/178/180 | One demand model; 6 qty columns; promised ship/deliver | v1 P2 | **Built** | #59 P2-08; `promised_ship_at`/`promised_deliver_at` |
| FR-253 | Replenishment document + SCHEDULED run + buyer notify; no auto-PO | v1 P2 | **Built** | #106 P2-15; V510070; `WhReplenishmentNotifier` |
| FR-254 | Sister-branch transfer before purchase | v2 P5 | **Built (heuristic, HOUSE-owned only)** | #96 P5-18 |
| FR-255 | Pick-face replenishment tasks | v1.1 P3 | **Built** | #61; V510108 |
| FR-256 | Demand history by posting | v1 P2 | **Built** | `WhDemandHistoryRecorder` |
| FR-257 | Lost sales captured with type and resolution | v1 P2 | **Partial**: no resolution column | V510034 |
| FR-258 | Computed best stocking level | v3 P6 | **Not built** | #99 open |
| FR-259 | Emergency / opportunistic / break-case replenish | v2 P5 | **Partial**: emergency is unbuildable as specified | #96 closed; #177 open |
| FR-260 | PO order source, customer-waiting, job ref, promised date; VOR excluded from lead time | v1 P2 | **Partial**: source and exclusion built; 3 columns missing | V510011; `WhSupplierLeadTimeQueryService` |
| FR-268 | Multi-level BOM not built | v3 P6 | Refusal record open | #144 |
| FR-270 | `return_type` incl. WARRANTY | v1 P0 | **Built** | code list |
| FR-276 | Obsolescence return to OEM | v2 P5 | Verify | — |
| FR-277 / FR-278 | Cores; warranty scrap-and-hold | v2 P5 | **Void, not built** | #81 NOT_PLANNED |
| FR-358/360/363/364 | Dealer / services / field-service / assets adapters | v1·v1.1 | **Removed / not required** | #150, #151, #102, #108 |
| FR-365 | Vehicle inventory test (OD-2) | v3 P6 | **Withdrawn** | #134 NOT_PLANNED |
| FR-393 | Four parts KPIs, frozen definitions | v1 P2 | **Built** | #141 (WS-217) |
| FR-415 | 12 months demand history importable | v1.1 P3 | **Built** | #90 P3-18; `is_migrated` |
| FR-419 | OEM price file with dry-run diff | v1.1·v2 | **Delivered in #90; adapter-hosted tables removed**: verify what survives | #90, #150 |
| FR-420 | OEM order interface / ack / ETA | v1.1 P3 | **Void** | #95 NOT_PLANNED |
| FR-443 | Style/variant schema | v1·v2 | **Schema built; style creation missing** | #191 |
| FR-463 | ABC recompute v1.1 | v1.1 P3 | **Not built** (#156 closed as *duplicate* into #33, but no recompute code exists) | grep = 0 |
| FR-466 | Approval levels | v2 P5 | Verify | — |
| FR-470 | KPI targets as data | v1 P2 | Verify | — |
| FR-471 | Location utilisation | v3 P6 | **Not built** | in #99's scope |

---

## 6. Cancelled tasks relevant to planning

All are GitHub `NOT_PLANNED` unless noted.

| Issue | Task | Reason (quoted/condensed) | Planning consequence |
|---|---|---|---|
| **#81** | P5-15 Cores are inventory, and warranty scrap-and-hold | *"VOID — both target modules removed 2026-09-21 … If cores-as-inventory is wanted later it must be re-scoped onto `warehouse`/`warehouse-base` with numbers from their own bands"*; bands V520xxx/V521xxx reserved | No core ledger or warranty holds. Repairable planning and core-return ageing have no data |
| **#95** | P3-19 OEM order interface: transmit, consume ack | Built into the dealer adapter, which was removed; *"it should not be reopened here"* | No supplier ack quantities or ETA per line, so no supplier-confirmed dates for lead-time variance |
| **#102** | P3-20 field-service adapter: van as a mobile location | *"NOT REQUIRED — user decision 2026-09-23. No warehouse adapter module is built"* | Van replenish, job-close consumption and unreturned-part ageing are missing. Only the location/custody object remains |
| **#108** | P3-21 assets adapter: spares against complaint resolution | Same ruling as #102 | No asset-linked spare consumption, so no installed-base / maintenance demand feed |
| **#121** | P3-24 GS1 identity (SSCC, EPC, Digital Link) | OD-17: deferred to v1.1; *"built only when a customer's trading partner actually needs GS1 labels"* | Minor for planning (traceability only) |
| **#134** | P6-09 dealer vehicle-inventory test | *"NOT REQUIRED — no dealer-management or vehicle-management work in warehouse … OD-2 is withdrawn, not deferred; it should not be re-opened"* | Vehicle parc for installed-base planning must come from dealer/automotive by reference |
| **#150 / #151** (closed COMPLETED, then modules **deleted**) | P2-25 dealer adapter (counter sale, item prices); services adapter (job-card issues, returns, warranty split) | *"the warehouse product adapters are not wanted; only the dealer vertical is … This module will not come back"* | Lost: price levels and item prices (WS-239), counter-sale substitution UX, job-card consumption demand, warranty split, WIP |
| **#156** (closed DUPLICATE) | P3-25 Simple ABC recompute | Folded into #33 (P1-03). No recompute code found | ABC classes are hand-maintained. Planning's first classifier has no warehouse baseline |

---

## 7. Open issues relevant to planning data quality

| Issue | What it is | What it blocks for planning | Pre? |
|---|---|---|---|
| **#99** P6-02 computed stocking level | Open v3 task | The boundary object. Its schema must include the policy-authority / override / history design **before** planning (FR-258 row) | **YES** (amend first) |
| **#167** requested item on reservation | Largely stale: `whb_reservations.requested_item_id` exists (V500038) | Asked-for vs held reporting. The counter-adapter acceptance is moot. **Re-scope/close** | YES (housekeeping) |
| **#168** MERGE_DEMAND not consumed | Genuine gap; names a removed adapter | Supersession-aware demand. Without it, a successor's history is zero on supersession day | **YES** |
| **#169** Cost Layers / Valuation Policies screens | Seeds missing | Visibility of the unit cost used in inventory-investment scenarios | EARLY |
| **#170** approved cost / source currency / cost source line on movement lines | Line keeps submitted cost | Budget and value scenarios read wrong unit costs for approval-gated movements | EARLY |
| **#171** receipts, supplier returns, transfers and workshop returns pass what costing needs | FX receipts refused; transfer cost; replenishment `findUnitCosts` wrong | Suggestion values and EOQ cost inputs | EARLY |
| **#172** ratify costing defaults, contract codes, integration tests in gate | AVCO default, precedence, `WEIGHTED_AVERAGE` vs `AVERAGE` naming | Consistent cost semantics for planning | EARLY |
| **#173** accounting envelope v2 (duty, lot, serial, FX) | Blocked on receiving side | Not planning-critical | NO |
| **#174** accounting adapter has no home | INTEGRATED mode unreachable | Only if planning reports need GL tie-out | NO |
| **#175** prove INTEGRATED mode | Same | Same | NO |
| **#176** bin-to-bin move has no owning task | FR-150 unowned | Planning-triggered internal rebalancing inside a site | EARLY |
| **#177** emergency replenish unbuildable (BIN_TO_BIN removed) | P2-09 falsely ticked | FR-259 emergency replenishment; a short pick is a demand signal with no path | EARLY |
| **#178** OD-20 no union valuation | Default side-by-side, no total | Inventory-budget dashboards cannot total accessories and warehouse | NO |
| **#179** WS-224 as-at = 365-day windowed net | Not an all-time balance | **Time-travel / scenario baselines**: dormant stock is silently netted | **YES** (for scenarios) |
| **#180** unescaped LIKE in WhStockToGl | Minor | — | NO |
| **#181** dead filter seed | Minor | — | NO |
| **#182** WS-212 ageing scans the whole ledger | Deliberate, cost unmeasured | Obsolescence and LTB candidate lists read ageing. Performance risk at scale | EARLY |
| **#184** P2-21 four default product calls (KPIs) | WS-216/217 behaviour | Planning outcome KPIs must align with the WS-217 pivot semantics | NO |
| **#185** RH-010: scheduled reports cannot be per-recipient scoped | Platform `ReportDataProviderInterface` has no principal | Planner digests and exception emails | EARLY |
| **#186** WH-SC-044…059 not demonstrated | v1 exit scenarios unproven | The capability baseline planning builds on is unproven (PTC doc §9 step 0) | **YES** (baseline) |
| **#191** no code creates a style | Variant matrix empty | Style-level planning ("plan at the style, transact at the variant", FR-443) is impossible | EARLY (if apparel) |
| **#75** P4-11 tax-basis inventory value | Open | Budget scenarios must pick a basis, not sum both | NO |
| **#112** P6-05 receipt facts as evidence | Open | Supplier lead-time variance and OTIF inputs | EARLY |
| **#94** P6-01 archiving | Open | Ends ledger re-derivation of demand for archived months | EARLY (sequence after DM-3) |

---

## 8. Must-change-before-planning-starts checklist

1. **DECISIONS amendments:**
   - Name the planning module under refusal #8/#9 and move `P-052` off WONTFIX.
   - D-1: add a sixth module.
   - D-2: allocate a band (verify V550000–V559999 is free) and update CLAUDE.md's MODULES table and the coupling tests.
   - D-3: add a prefix.
   - D-11 analogue: planning writes only through a warehouse service API, backed by an arch test.
2. **Policy authority:** amend **P6-02 (#99)** before it is built. Add `policy_authority`, run id, override-retention fields and **effective-dated history** for `whb_item_site_settings` (DM-1).
3. **Demand-signal capture (PNR-3, unrecoverable history):**
   - Lost-sale resolution and requested item (DM-4).
   - PO customer-waiting flag, job ref, promised date and line-level supplier-confirmed date (DM-5, FR-260).
   - Demand stream on reason codes (IRR-32 amend).
   - Owner on demand history (DM-3).
   - A recommendation/seam id on transfers and demand orders (DM-9).
   - Add these as new IRR rows.
4. **Event catalogue additions** (PC-43 seed INSERT): demand-line, backorder, lost-sale, policy-change, supersession-change and PO-line-confirmation events.
5. **Autopilot decision:** either keep FR-253/RK-004/"never auto-approve" as a hard boundary (the PTC doc recommends deferring autonomous purchasing), or record the bounded per-policy release band. Planning schema depends on which.
6. **OD-8 deployment model:** in-process planning (for now), or a platform service principal first.
7. **Fix #168** and close or re-scope **#167**. Demonstrate **#186**. Resolve **#179** before scenario/time-travel work.
8. **Scope statements:**
   - HOUSE-owner-only replenishment (keep or extend to owners).
   - D-9: accessories is out of scope.
   - Dealer network: a new OD, given OD-3 and the 2026-09-23 no-dealer ruling.
   - Pricing owner (price master homeless since #150).
   - Van demand grain (site vs location).
9. **Doc inconsistency:** `DATA-MODEL.md:4749` claims `criticality_level` and `is_vor_eligible` are `whb_items` columns. They are neither in the table spec nor in any migration. Either add them (DM-2) or correct the mapping row.
