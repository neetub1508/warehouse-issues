# Service-Parts Planning Module: Research Pack and Warehouse-Readiness Synthesis

*Prepared 2026-09-30. Scope: everything a future **service-parts planning module** (forecasting, service-level stocking, multi-echelon, supersession-aware demand, repair/cores, van/dealer stock, scenarios, autopilot) needs to learn from PTC Servigistics and its competitors. Also covers everything in our existing warehouse modules that must change first so the planning module has a strong base.*

This file is the **synthesis**. The detail, with file:line evidence and source URLs, is in the numbered files.

| File | What it contains | Size |
|---|---|---|
| `00-README-Synthesis.md` | This file: conclusions, the master "fix-first" list, architecture blueprint, roadmap, decisions | — |
| `01-PTC-Servigistics-Functional.md` | Modules, packaging and licensing tiers, data model, forecasting methods and parameters, IO/MEO, order policies, LTB, dealer, field stock, pricing, analytics, AI; replicate / simplify / skip list | ~390 lines |
| `02-PTC-Servigistics-Architecture.md` | SaaS deployment, AutoPilot batch engine, data model, the four "go back in time" mechanisms, Snowflake/PAI, security, implementation method; **architecture decisions for us** | ~360 lines |
| `03-Competitors-Feature-Sweep.md` | 19 vendors or vendor groups (Syncron, Baxter, ToolsGroup, GAINS, Smart, Lokad, Blue Yonder, SAP, Oracle/NetSuite, Kinaxis, o9, Slim4, EazyStock, Netstock, Intuiflow, IFS, Epicor/Infor, dealer DMS/RIM programs); 70-row feature matrix; table stakes vs differentiators | ~900 lines |
| `04-Planning-Methods-and-Algorithms.md` | Every method with formulas and defaults (demand prep, classification, forecasting, policies, multi-echelon, repairables, lifecycle, supplier lead time, KPIs, automation), 20 pitfalls, **MVP method set M1–M17 and the exact data fields each needs** | ~900 lines |
| `05-Warehouse-Code-Gaps.md` | Code audit of `warehouse-base`, `warehouse`, `-3pl`, `-india`: ~60 findings with severity and file:line | ~490 lines |
| `06-Warehouse-Design-Decision-Gaps.md` | Every DECISIONS / FRD refusal / invariant / IRR / open issue that planning conflicts with or depends on; data-model gaps DM-1…14; required contracts; pre-start checklist | ~370 lines |
| `appendix/PTC-A…L-*.md` | Raw research notes, every fact with its URL. I–L are late gap-fills (data inputs and pricing; IO defaults, distributions, scenarios; forecasting; supply planning, repair/returns, order lifecycle). A–F come from PTC's public Servigistics 13.x help center (4,417 pages crawled): forecasting, inventory optimisation, supply planning and workbench, 13.0.1–13.1.0.5 release notes, PAI/AI/ML, dealer/security/segments/AutoPilot. G is outside sources: SaaS licensing tiers (PMI/PXL/DAL/PLP limits), case-study metrics, ServiceMax field-stock data flows, heritage. H is pricing, global settings and corpus gaps. Parameter names, defaults and menu paths throughout | ~540 KB |

---

## 1. Headline conclusions

1. **Servigistics is a planning layer, not an execution system.** Its system of record is an Oracle or SQL Server planning database fed by ERP/WMS "download transfer tables". It sends recommended orders back through "upload transfer tables". We already own the execution half (the WMS), which PTC deliberately leaves to SAP.
2. **Our warehouse base is not yet a safe foundation for planning.** The code audit found **~60 gaps**, of which **9 are BLOCKERs**. The most serious make today's demand history wrong, not just thin:
   - Supplier returns are counted as customer demand.
   - The warranty/internal exclusion never fires on the main despatch path.
   - 3PL client issues inflate house demand.
   - Lost-sale capture from the system has zero callers.
   - On-order supply is undated.
   - The replenishment engine counts QC/damaged/quarantined/expired stock as available, so it under-orders today.
3. **Some of the damage is unrecoverable.** Demand signals we don't capture now can never be rebuilt: lost-sale resolution, requested vs supplied part, supplier-confirmed dates, demand stream, owner. Our own design classes this as PNR-3 / UB ("unrecoverable if not captured"). **These fixes should start before any planning code, because every day of delay is lost history.**
4. **The design set blocks planning in four places, and each needs a decision.**
   - Refusals #8/#9 relocated forecasting to a planning module that was never defined.
   - P6-02 (#99) will write the same reorder-point column that planning would write, so there would be two writers.
   - FR-253, RK-004 and the "never auto-approve" setting rule out any autopilot.
   - The 2026-09-21/23 adapter deletions left pricing, cores/warranty, van workflow, OEM ETA and job-card demand with no home.
5. **The PTC model is learnable and mostly simple at its core.**
   - SKU = part × location (PLP).
   - Nightly AutoPilot batch.
   - Best-fit selection over about 24 forecast methods, with fallbacks (e.g. Croston needs 12 slices, else SES).
   - Normal demand for high volume, Poisson/negative binomial for low volume (switch at mean 25 / VMR 1.1).
   - Stock/no-stock via an Authorised Stocking List (Pareto demand coverage per location).
   - Two main order policies: Trigger Point (the default) and Time-Phased Safety Stock.
   - A review board of 145 exception reasons.
   - Guard-railed auto-approval.

   All of this can be reproduced at mid-market scale on Postgres.
6. **What the market expects of a mid-market tool** (03 §5):
   - intermittent-aware forecasting with automatic pattern classification;
   - service-level safety stock with lead-time variability;
   - supersession with demand inheritance;
   - phase-in/out by hits rules;
   - MOQ, pack and calendar-aware order proposals;
   - an exception workbench;
   - overrides with expiry;
   - E&O and return-to-vendor handling;
   - lateral transfers;
   - KPIs.

   Our **differentiators** could be:
   - probabilistic demand over lead time (bootstrap / compound Poisson);
   - a $-ranked purchase list under a budget;
   - Syncron-style "auto-confirm unless a blocking rule fires";
   - a stock-to-service curve;
   - repairables-lite;
   - one product for execution plus planning.

---

## 2. Your beliefs about PTC's architecture, checked

| Belief | Verdict | What it really is | Detail |
|---|---|---|---|
| "They use **Snowflake** in between" | **Partly: at the edge, not in the middle** | Planning runs on Oracle or SQL Server. Snowflake holds data only for **PAI Advanced** (Performance Analytics & Intelligence). AutoPilot exports CSV, PUTs it to a Snowflake stage and COPYs it into tables, and Intellicus dashboards read it. Data flows **one way, downstream**. Snowflake credits (200–600) are bundled in the Advanced/Premium SaaS tiers | 02 §0, §5 |
| "They use **location**" | **True** | Location → Location Type → **Location Hierarchies** (a per-part replenishment tree) → Echelon. Process Groups of locations; emergency-backup locations. The part × location pair (PLP) is the sizing and **licensing** unit (cap about 25M) | 02 §3; 01 §0–1 |
| "Planners can **go back in time**" | **True, through four mechanisms, none of them Snowflake Time Travel** | (1) **Enhanced Supply Chain Modeling**: full database snapshots restored into a small pool of sandboxes (examples cap at 5 or 10). (2) **History Based Simulator**: replays planning day by day with an injectable process date. (3) **Automated Dataset Comparison**: backup-vs-current diffs. (4) SKU Supply Chain History dashboard, audit trail and journal | 02 §4 |
| "They have an **autopilot**" | **True, but it is the batch job engine, not an AI** | "AutoPilot is an agent that runs selected processes": a dependency-ordered batch runner, nightly, plus more frequent runs per process group. Autonomy comes from **Auto Approval** guardrails (horizon, value cap, per-user approve limit, lock flag), the **Order Explanation Report**, the **AI Assistant** (GA Oct 2025) and "agentic AI" for approvals, work queues and exceptions (Spring 2026) | 02 §2; appendix F |

---

## 3. Fix the warehouse base first: master prerequisite list

This list consolidates `05` (code) and `06` (design). The IDs point back to those files. The tiers are in the order they should be done.

### Tier 0: Decisions (before any design or migration)

| # | Decision | Source | Recommendation |
|---|---|---|---|
| T0-1 | Name the planning module as the one refusals #8/#9 relocated to. Move R6 `P-052` off WONTFIX | 06 §1.1 | Yes, as **`warehouse-planning`**, package `ai.warehouseplanning` (a sibling, so it is not auto-scanned) |
| T0-2 | D-1 sixth module, D-2 Flyway band, D-3 table prefix | 06 §1.2 | Band **`V550000`–`V559999`** (verified free: 0 migrations exist in V55xxxx–V59xxxx). Prefix **`whp_`** (not `spi_`/`wms_`). Update CLAUDE.md MODULES, `WarehouseBaseCouplingTest.warehouseBands()`, `check-design-set.py` |
| T0-3 | **Single writer of stocking parameters.** P6-02 (#99) and planning both target `whb_item_site_settings` | 06 FR-258 row, DM-1; 05 IS-01 | Amend #99 **before it is built**: `policy_authority` (MANUAL / HISTORICAL_POLICY / PLANNING), `policy_run_id`, override fields (reason/by/until), **effective-dated history table**. Planning publishes through a warehouse **policy-publish service API**, never by direct table write, enforced by an architecture test (D-11 analogue) |
| T0-4 | **Autopilot stance.** FR-253, RK-004 and "never auto-approve" conflict with any auto-release | 06 §2.9 | Keep "no auto-PO" for the first release (shadow/recommend-only). Record now the future amendment: a bounded **per-policy release band** (item class × value ceiling × supplier; typed rows; human approves the *policy*; documents carry `actor_type=SCHEDULED_JOB` + `released_under_policy_id`; off by default) |
| T0-5 | Deployment model (OD-8: no service principal for out-of-process consumers) | 06 §1.4 | Run planning **in-process** (same Spring Boot app, own module) until a platform service principal exists |
| T0-6 | Scope statements | 06 §1.2 D-9, §2.6–2.10 | (a) Plan per **owner**: HOUSE first, 3PL owners opt-in. (b) Accessories out of scope (D-9). **Do not reuse accessories pricing**, which reverses the idea in our earlier comparison doc. (c) Dealer network: new OD, import/API federation only, never a shared DB (OD-3). (d) Price master owner. (e) Van demand grain: site or location |
| T0-7 | Demand streams instead of include/exclude | 06 IRR-32 row; 05 DH-02 | Add a `demand_stream_code` catalogue (PAID, WORKSHOP, WARRANTY, INTERNAL, EMERGENCY, CAMPAIGN, …). Keep the `affects_demand_history` boolean only for FR-393's frozen KPI |

### Tier 1: Capture now (unrecoverable history, PNR-3 class)

| # | Change | Source |
|---|---|---|
| T1-1 | **Line-level demand-event fact table** (append-only, partitioned). One row per demand-order-line event: ordered / amended / cancelled / backordered / shipped / lost. Carries order date, requested date, requested item, supplied item, customer, channel, owner, company, demand stream, warranty flag, base qty, source ids. `wh_demand_history` becomes a projection | 05 DH-04; 06 DM-3 |
| T1-2 | **Owner (and company) on demand history** | 05 DH-03; 06 D-5 row |
| T1-3 | **Lost-sale resolution** (SUBSTITUTED / BACKORDERED / LOST / SPECIAL_ORDERED), requested item vs offered substitute, customer, demand-line link; record `requested − supplied`, not full requested | 05 LS-03; 06 FR-257, DM-4 |
| T1-4 | **PO fields FR-260 already requires**: customer-waiting flag, job reference, promised date. Plus **line-level supplier-confirmed date and quantity**, and a date-change audit | 05 SUP-02; 06 FR-260, DM-5 |
| T1-5 | **Planning recommendation / seam id** on POs, transfers and demand orders (lineage recommendation → document → receipt) | 06 DM-9, L-12 row |
| T1-6 | **Outbox event codes** (additive seed INSERT, PC-43): `demand.line.created`, `demand.line.backordered`, `lost_sale.captured`, `item_site_policy.changed`, `supersession.changed`, `po.line.confirmed` | 06 IRR-50 row; 05 EV-01 |
| T1-7 | Add IRR rows for demand-signal capture to `IRREVERSIBLE.md` | 06 PNR-3 row |

### Tier 2: Correctness defects in existing code (planning would be wrong)

| # | Defect | Sev | Source |
|---|---|---|---|
| T2-1 | VENDOR_RETURN despatch counted as customer demand | BLOCKER | 05 DH-01 |
| T2-2 | Despatch posts `reasonCodeId = null`, so the warranty/internal exclusion is inert on the main path | BLOCKER | 05 DH-02 |
| T2-3 | `WhLostSaleRecorder` has zero callers. Wire it at allocation failure, short pick and backorder auto-cancel | BLOCKER | 05 LS-01, LS-02 |
| T2-4 | Import into the current month collides with live postings; a re-import or reversal wipes them | MAJOR→BLOCKER at go-live | 05 DH-05 |
| T2-5 | Replenishment engine "on hand" includes QC_HOLD / DAMAGED / QUARANTINE / EXPIRED / CORE_UNGRADED | MAJOR (live defect) | 05 ST-01 |
| T2-6 | PROPOSED suggestions never expire and freeze the item out of all later runs | MAJOR (live defect) | 05 RE-05 |
| T2-7 | Customer returns and RTO never net demand | MAJOR | 05 DH-06 |
| T2-8 | Hits counted per movement, so 3 partial despatches = 3 hits | MAJOR | 05 DH-04 |
| T2-9 | Sister transfers can over-draw (two branches' runs claim the same surplus) | MAJOR | 05 NW-02 |
| T2-10 | Mixed timezone bucketing (UTC vs site vs user zone) | MINOR | 05 ST-02, DQ-02 |
| T2-11 | Supersession `MERGE_DEMAND` never read (#168). Planning must roll up the chain with ratio and effective date; keep raw history per item in warehouse | BLOCKER | 05 SS-01; 06 §2.4 |
| T2-12 | One-off **demand-history rebuild tool** from the ledger, needed after T2-1/2/7 and T1-2. Must run **before P6-01 archiving** removes re-derivability | MAJOR | 05 EV-02; 06 P6-01 row |

### Tier 3: Structural additions planning needs

| # | Addition | Source |
|---|---|---|
| T3-1 | **Time-phased supply**: dated on-order (PO line due, ASN ETA, transfer ETA) and a projected-available-balance service | 05 SUP-01 |
| T3-2 | **Lead-time actuals per receipt line** (PO line → GRN line, qty-weighted); item × supplier × site mean, σ and P90 on a schedule. Precedence between the two static `lead_time_days` fields; lead time actually used in ROP maths | 05 LT-01/02 |
| T3-3 | **Supplier sources scoped to site/company**, with purchase UoM and price/contract ref (V500077 was promised and never written) | 05 LT-03 |
| T3-4 | **Supply network**: dated `site_supply_lanes` junction (from → to, priority, transit mean/σ, calendar, cost), echelon role per site, hub designation | 05 NW-01/05; 06 D-14, DM-11 |
| T3-5 | **Calendars in the maths**: add-working-days API; receiving and supplier calendars | 05 NW-04 |
| T3-6 | **Planning attributes**: criticality, service-level target (`DECIMAL(9,6)`), lifecycle phase per site, stocking flag, planner/buyer, review period, holding-cost rate, order cost. `criticality_level` / `is_vor_eligible` are claimed in DATA-MODEL:4749 but exist in no migration | 05 IS-03; 06 DM-1/2 |
| T3-7 | **ABC/XYZ classification job** with history (FR-463 was never built; #156 closed as a duplicate with no code) | 05 IS-02; 06 #156 |
| T3-8 | **Time travel**: bitemporal as-at (`recorded_at ≤ knownAt`), daily closing balances, snapshot backfill-from-ledger, multi-item/multi-site as-at API; fix #179 (365-day windowed net) | 05 ST-03; 06 §2.8 |
| T3-9 | In-transit as dated inbound at the **destination**; need-by dates on demand lines and reservations | 05 ST-04/05 |
| T3-10 | **Planning cost basis**: replacement/last-PO cost fallback when there is no stock; FX policy for roll-ups; costing follow-ups #169–#172 | 05 CO-01, RE-06; 06 #169–172 |
| T3-11 | **Ledger read performance**: `warehouse_id` on ledger lines or a covering index; planning reads the demand fact table, not the ledger; #182 ageing full scan | 05 PF-01/02 |
| T3-12 | Supersession model: split `demand_treatment` from `stock_treatment`; use-up policy; per-site phase-in/out dates; batch chain resolver (today it is N+1); implement MERGE_STOCK via the writer; don't propose for superseded predecessors | 05 SS-01/02, IS-04; 06 DM-7 |
| T3-13 | Tests: VENDOR_RETURN/JOB_ISSUE vs demand, owner demand, import collision, lost-sale recorder, engine usable stock, suggestion expiry, supersession resolver/cycle/merge, ledger-report query bounds | 05 §15 |
| T3-14 | Baseline proof: demonstrate WH-SC-044…059 (#186); close or re-scope stale #167 | 06 §7 |

### Tier 4: Feature-specific (only when that feature is scheduled)

| Feature | Base changes needed | Source |
|---|---|---|
| Repair / cores / warranty | Repair loop (unserviceable → in repair → serviceable), core obligations per sale with due-date ageing, repair TAT and yield stats, WARRANTY supplier-claim type. Re-scope void #81 onto `warehouse` | 05 RR-01/02; 06 §2.5 |
| Van / field stock | Van as a plannable node or location-level planning; job-close consumption; unreturned-part ageing. Re-scope #102 as a vertical-neutral `warehouse` task, not an adapter | 05 NW-03; 06 §2.6 |
| Dealer network | New OD; import/API federation; protected vs unprotected (returnable) stock | 06 §2.7; 03 §5.2 |
| Pricing | Decide the price-master owner (sell price, core charge, supplier price lists); the dealer adapter's price tables were deleted | 06 §2.10 |
| Kits / installed base | Dependent demand explosion for kits; an applicability model (equipment model ↔ part, dated), explicitly not the FR-268 BOM | 05 DH-07; 06 FR-268 row |
| Planner digests | #185: scheduled reports cannot be scoped per recipient; use in-app notifications until the platform is fixed | 06 FR-405 row |

---

## 4. Recommended architecture (from 02 §9 and 06 §4)

```text
warehouse-base / warehouse (execution, system of record)
   │  outbox events (async, cursor)          ▲ policy-publish API (authority, run id, approval)
   │  + read contracts (usable stock,        │ execution API (create PO / transfer, idempotent
   │    dated supply, demand facts)          │   on recommendation id, source approval kept)
   ▼                                         │
warehouse-planning (whp_, V550000+)  ────────┘
   ├─ input snapshot per run (declares its clock: recorded_at cut-off; immutable)
   ├─ SCD-2 history on planning masters (params, lead times, supersession, lanes)
   ├─ DAG job runner on existing WhbJobCatalogue pattern, partitioned by process group
   │    classify → cleanse → forecast → backtest → policy → proposals → exceptions → KPIs
   ├─ PlanningClock / asOfDate injected everywhere (never now()) → history-based replay
   ├─ plan-run ledger (append-only run/result/order-line tables, partitioned by month)
   ├─ scenarios = copy-on-write overlay rows keyed by scenario_id; Production read-only
   ├─ autopilot = guardrails + explanation record + shadow mode + kill switch
   └─ analytics = Postgres summary tables per run; Parquet export later; Snowflake only as outbound share
```

Rules that carry over from our design set: no JSONB (typed child tables); open vocabularies as catalogue rows (D-10); bounded typed rule rows, never an expression language (refusals #11/#24); doubles in memory only, rounded at persistence (OD-7); planning never writes stock or positions (D-4); warehouse must run without planning (D-7).

---

## 5. Capability roadmap for the planning module

The method set is from 04 §12. The PTC replicate/simplify/skip list is 01 "Implications". Table stakes are 03 §5.

| Phase | Capabilities |
|---|---|
| **MVP** (after Tiers 0–2 and T3-1/2/6/7/12) | M1 demand prep (request-date, streams, returns netting, zero vs missing, censoring from snapshots) · M2 supersession roll-up · M3 robust outliers · M4 classification (value ABC + hits + SBC ADI 1.32/CV² 0.49 + lifecycle + VED) · M5 method-by-class forecasting (SES/damped Holt, SBA, TSB, Poisson for very slow, analogue for new) with best-fit and fallbacks · M6 rolling-origin backtest (RMSSE, bias, PIS) · M7 LTD distribution (normal vs NB/Poisson switch) · M8 (R,s,S) min/max from fill-rate target, EOQ/MOQ/pack · M9 service-target matrix · M10 stock/no-stock hits rule with hysteresis · M14 lead time from receipts · M16 KPIs · M17 exception workbench, overrides with expiry, dead-band smoothing, **recommend-only** |
| **Phase 2** (after T3-3/4/5/8/9) | M11 budget / stock-to-service curve · M12 two-echelon DC → branch · M13 rebalancing with donor protection · M15 phase-in/out, dead stock, simple LTB · scenarios overlay · history-based replay · guard-railed auto-approval (after T0-4 amendment and a shadow period) |
| **Phase 3** (customer-led) | Repairables-lite · van stock · dealer-network mode (protected/unprotected stock, compliance %) · pricing (rules-based) · installed-base / campaign demand streams · override-impact analytics |
| **Skip** | Full METRIC/VARI-METRIC, asset-uptime/PBL, IoT failure forecasting, ML ensembles, network design, carbon optimisation, price elasticity, agentic AI that writes directly |

---

## 6. Decisions needed from you

1. Confirm `warehouse-planning` as the relocated module (T0-1), with band **V550000–V559999** and prefix **`whp_`** (T0-2).
2. Approve amending **#99 (P6-02) before it is built** so it has policy authority and dated history (T0-3).
3. Autopilot: recommend-only for the first release, with the bounded-policy amendment recorded now (T0-4)?
4. Start **Tier 1 capture** and the **Tier 2 defect fixes** now as warehouse issues, independent of the planning module? These are recommended because the history is unrecoverable and T2-5/T2-6 are live defects today.
5. Scope: owners (HOUSE first?), dealer network (defer?), price-master owner, van demand grain (T0-6).
6. File the Tier 0–3 items as issues in `warehouse-issues`, folding each into the most similar existing task per the no-duplicate rule?

---

## 7. Evidence quality and caveats

- **PTC functional and architecture facts** come mostly from PTC's own public Servigistics 13.x help center (`trne-prod.ptcmanaged.com/servigistics_help/...`). 4,417 pages were crawled and cited per fact. Other sources: the Aug 2025 SaaS Service Description, a PTC Stanford lecture, case studies and release notes. Items marked **UNVERIFIED** are inferences. Some help-center formulas are images and were not captured. The crawl lives in a temporary scratchpad and is not part of this pack.
- **Competitor facts** have a source URL per claim. Single-source and aggregator claims are marked UNVERIFIED. Several comparisons are written by Lokad, itself a vendor. Pricing for many vendors is not public.
- **Methods (04)** were written from literature knowledge, and **its citations were not web-verified**. Defaults marked "(practice)" are rules of thumb and should be configurable.
- **Code findings (05)** come from a static read of `classic` on 2026-09-30. No tests or runtime checks were run. Line numbers drift as code changes.
- **Design findings (06)** come from `warehouse-issues` `main` plus live GitHub issue state on 2026-09-30.
- This pack **supersedes** one recommendation in the earlier `docs/competitive/Warehouse-vs-PTC-Servigistics-Comparison.md`: reusing the `accessories` price-list model would cross D-9's permanent separation (06 §1.2).
