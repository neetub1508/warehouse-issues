# Sources, coverage and unresolved evidence

Research date: 2026-09-30. This file records what supports the pack and what still requires validation.

## Method and limits

- Inspected the current local warehouse implementation, targeted entities/services/migrations and draft SPI documents. File 02 links the principal code evidence at commit `fcdbe1748b7d0a510d156d760ddf54cbb1854db5`.
- Refreshed the warehouse GitHub issue inventory and reviewed relevant issue bodies and selected closure comments. All 189 issues were inventoried; comments, linked artifacts and runtime behavior were not exhaustively verified for every issue.
- Used PTC technical help for methods/workflows, installation documentation for architecture, a SaaS description for package context and current public product pages for broader positioning.
- Reviewed selected primary materials from eight other vendors. Public claims were not independently benchmarked.
- The PTC navigation index was used to find topics; discovering links is not equivalent to reading or verifying every topic. No count of navigation links is presented as feature coverage.
- Summaries intentionally avoid copying complete vendor manuals. Proposed requirements and acceptance cases are our analysis.
- No vendor demo, licensed source code, production database, contract or proprietary API specification was available.

## Checkout advanced during the review

At final verification the checkout had advanced to `c9bd3c7254bd21cbbb2f35a24acdb8639d5670f9`. The warehouse diff from the audited baseline concerns KPI snapshot timezone handling and stock-ageing last-outward logic/tests. The principal gap-evidence files linked in file 02 were unaffected by that diff. Those newer KPI/ageing changes were not fully re-audited, and open issue status remains a snapshot rather than proof that a reported defect still reproduces. The working tree was clean at final verification.

## Evidence labels to preserve in future updates

| Label | Meaning |
|---|---|
| Documented | Primary technical source describes behavior for the identified product/version |
| Vendor claim | Public positioning; not independently demonstrated |
| Observed implementation | Inspected code supports the statement; runtime behavior still requires testing |
| Reported issue | GitHub issue records a defect or deferred task; current reproducibility may differ |
| Proposed | Our recommended design/requirement; not a competitor fact or existing implementation |
| Unknown | Evidence insufficient; requires a targeted check |

## Vendor source register

PTC help pages are part of the public help set identifying Servigistics 13.1.0.5 / PAI 5.0.0.1; release notes are version-specific. P02 is August 2025. C10 is legacy SAP APO; C11 is a versioned S/4HANA page; C12 is Oracle EBS 12.2. Marketing pages are observations as of the research date, not versioned contracts.

- **P01** — [Servigistics product overview](https://www.ptc.com/en/products/servigistics).
- **P02** — [PTC SaaS service description, August 2025](https://ptc-p-001.sitecorecontenthub.cloud/api/public/content/312715bc95994beb94cb013a4906dbe8?v=9c7c8608).
- **P03** — [PAI Advanced with Snowflake](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/install/install_planning_advanced_snowflake.html).
- **P04** — [Snowflake installation instructions](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/install/install_instructions_pai_advanced_snowflake_2.html).
- **P05** — [AutoPilot glossary](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/autopilot.html).
- **P06** — [Running AutoPilot manually](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/core/core_topics/running_the_autopilot_manually.html).
- **P07** — [New/Edit Job Page (Fields)](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/core/core_pid/pid_new_edit_job_page.html).
- **P08** — [Snapshot Management Page (Fields)](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/core/core_pid/pid_snapshot_management.html).
- **P09** — [Modeling Instances Page (Fields)](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/core/core_pid/pid_modeling_instances.html).
- **P10** — [History Based Simulator Page](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/core/core_smart_help/sh_history_based_simulator.html).
- **P11** — [Historical simulator configuration](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/core/core_pid/pid_history_based_simulator_add_edit.html).
- **S01** — [Snowflake Time Travel](https://docs.snowflake.com/en/user-guide/data-time-travel).
- **P12** — [Forecast method catalog](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/forecast_method.html).
- **P13** — [Best Fit Management](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/core/core_pid/pid_best_fit_management_page.html).
- **P14** — [Forecast error improvement enhancement](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/release_notes/release_13_1_0_0/rn_enhancements_fcst_3.html).
- **P15** — [Croston Forecast Method](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/croston_forecast_method.html).
- **P16** — [Servigistics TSB Forecast Method](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/servigistics_tsb_forecast_method.html).
- **P17** — [Servigistics ML Forecast Method](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/servigistics_ml_forecast_method.html).
- **P18** — [Life Limited Parts Forecast Method](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/life_limited_parts_forecast_method.html).
- **P19** — [Demand Stream](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/demand_stream.html).
- **P20** — [Forecast Stream](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/forecast_stream.html).
- **P21** — [Forecast Netting](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/forecast_netting.html).
- **P22** — [Stocking Policy Page (What If)](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/inv_opt/inv_opt_smart_help/sh_stocking_policy_what_if.html).
- **P23** — [Space Constraints](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/space_constraints.html).
- **P24** — [Part Chain](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/part_chain.html).
- **P25** — [Future Part Chains](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/part_chain_2.html).
- **P26** — [Rotable parts planning](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/parts/parts_topics/overview_of_rotable_parts_planning.html).
- **P27** — [Return Wash Rate](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/return_wash_rate.html).
- **P28** — [Repair Wash Rate](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/repair_wash_rate.html).
- **P29** — [No Fault Found Rate](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/no_fault_found_rate.html).
- **P30** — [Schedule Change Suppression](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/schedule_change_suppression.html).
- **P31** — [Fair Share Priority](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/fair_share_priority.html).
- **P32** — [Supplier capacity enhancement](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/release_notes/release_13_1_0_0/rn_enhancements_sp_2.html).
- **P33** — [Time-Phased ROP](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/release_notes/release_13_1_0_4/rn_enhancements_sp_2.html).
- **P34** — [Network Optimization](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/release_notes/release_13_1_0_0/rn_enhancements_io_16.html).
- **P35** — [Part-chain location details](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/core/core_pid/pid_part_chain_details_page_locations_tab.html).
- **P36** — [SKU overrides](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/sku_override.html).
- **P37** — [Review Board](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/parts/parts_smart_help/sh_ipws_forecast_review_board.html).
- **P38** — [Order Explanation (Fields)](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/core/core_pid/pid_order_explanation_report.html).
- **P39** — [ServiceMax integration: creating flows](https://support.ptc.com/help/servicemaxcore/en/articles/servigistics_integration/creating-flows.html).
- **C01** — [Syncron service-parts planning](https://www.syncron.com/solutions/service-parts-planning).
- **C02** — [Syncron service supply chain](https://www.syncron.com/solutions/service-supply-chain/).
- **C03** — [Baxter platform](https://baxterplanning.com/platform/).
- **C04** — [Baxter service-parts planning](https://baxterplanning.com/resources/blog/reimagining-service-parts-planning/).
- **C05** — [Planning as a Service](https://baxterplanning.com/resources/blog/planning-as-a-service-explained-benefits-for-your-business/).
- **C06** — [ToolsGroup aftermarket planning](https://www.toolsgroup.com/industries/aftermarket/).
- **C07** — [Smart IP&O](https://smartcorp.com/demand-inventory-planning-optimization-software/).
- **C08** — [Netstock supersessions explained](https://help.netstock.com/en/articles/12441710-supersessions-explained).
- **C09** — [Netstock advanced bundle](https://www.netstock.com/ce/advanced-bundle/).
- **C10** — [SAP APO service-parts planning](https://help.sap.com/docs/sap_supply_chain_management/cd9e0c364e1e41e19ea633db7862222e/47e12f019e014ac5e10000000a42189d.html).
- **C11** — [SAP S/4HANA versioned supersession planning](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/f340785101c548c9beeda9284efd18a0/2bdec353b677b44ce10000000a174cb4.html?locale=en-US&state=PRODUCTION&version=2025.001).
- **C12** — [Oracle EBS 12.2 Service Parts Planning](https://docs.oracle.com/cd/E26401_01/doc.122/e48778/T515331T515340.htm).
- **C13** — [Lokad probabilistic forecasting](https://www.lokad.com/probabilistic-forecasting-definition/).
- **C14** — [Lokad asset and stock management](https://www.lokad.com/asset-and-stock-management/).
- **P40** — [K-curve methodology](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/parts/parts_topics/overview_of_k_curve_management.html).
- **P41** — [Demand aggregation and forecast disaggregation](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/demand_aggregation_and_forecast_disaggregation.html).
- **P42** — [Last Time Buy](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/last_time_buy.html).
- **P43** — [Last Time Buy Profile](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/last_time_buy_profile.html).
- **P44** — [Causal Forecast](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/causal_forecast.html).
- **P45** — [PTC Servigistics capabilities](https://www.ptc.com/en/products/servigistics/capabilities).

## GitHub issue coverage

Repository: [neetub1508/warehouse-issues](https://github.com/neetub1508/warehouse-issues). Snapshot: **189 issues, 45 open and 144 closed**. The table below preserves every open issue in that snapshot so lower-level warehouse concerns remain visible. Categories are our triage, not new priority decisions. Titles are the repository’s wording.

A closed item may be implemented, duplicated, voided, removed or explicitly not required. In particular, [#157’s closure](https://github.com/neetub1508/warehouse-issues/issues/157) says its work was folded into other tasks; it does not prove site-specific supplier resolution shipped.

| Issue | Title | Planning relevance / disposition |
|---|---|---|
| [#1](https://github.com/neetub1508/warehouse-issues/issues/1) | [Warehouse] EPIC: Warehouse and inventory management — master | Warehouse master epic; umbrella only |
| [#8](https://github.com/neetub1508/warehouse-issues/issues/8) | [Warehouse] EPIC: P4 — India statutory & compliance | India compliance epic; customer-scope dependency |
| [#11](https://github.com/neetub1508/warehouse-issues/issues/11) | [Warehouse] EPIC: P6 — Optimisation, planning and the logistics seam | Planning/logistics epic; use to reconcile scope |
| [#75](https://github.com/neetub1508/warehouse-issues/issues/75) | [Warehouse] P4-11 · A second, tax-basis inventory value carried alongside the book value | Tax-basis valuation scope; distinguish planning economic cost |
| [#94](https://github.com/neetub1508/warehouse-issues/issues/94) | [Warehouse] P6-01 · Archiving as a transaction — an `OPENING_BALANCE` movement at the cut-off before a single row moves | Archiving/opening balance boundary; historical reconstruction G19/G45 |
| [#99](https://github.com/neetub1508/warehouse-issues/issues/99) | [Warehouse] P6-02 · The best stocking level is computed, not typed | Computed stocking policy ownership; G04/G05/G28 |
| [#103](https://github.com/neetub1508/warehouse-issues/issues/103) | [Warehouse] P6-03 · Measured labour, not engineered standards — and the refusal is the requirement | Labor measurement scope; useful later for order-workload objective |
| [#109](https://github.com/neetub1508/warehouse-issues/issues/109) | [Warehouse] P6-04 · Automation, AS/RS and robotics through a published task-event contract and the movement port — an interface, never a control layer | Automation/robotics interface; separate from planning AutoPilot |
| [#112](https://github.com/neetub1508/warehouse-issues/issues/112) | [Warehouse] P6-05 · Receipt facts emitted as evidence — and the supplier scorecard is deliberately not built here | Receipt evidence and supplier scorecard seam; G08 |
| [#118](https://github.com/neetub1508/warehouse-issues/issues/118) | [Warehouse] P6-06 · The `party-base` extraction trigger is recorded, not acted on | Party-base extraction trigger; no immediate refactor implied |
| [#122](https://github.com/neetub1508/warehouse-issues/issues/122) | [Warehouse] P6-07 · 3PL v3 — rate escalation as a new version, the SLA credit as a negative billable event, and client profitability | 3PL advanced billing/SLA scope; separate from owned-stock planning |
| [#131](https://github.com/neetub1508/warehouse-issues/issues/131) | [Warehouse] P6-08 · The `logistics` module — trips, ePOD and freight settlement, posting through the port, with zero commits to `warehouse-base` | Logistics module future seam; dated transit feed G12/G43 |
| [#138](https://github.com/neetub1508/warehouse-issues/issues/138) | [Warehouse] P6-10 · The real-time operations dashboard on the platform widget framework | Operations dashboard scope; distinguish from planning analytics |
| [#142](https://github.com/neetub1508/warehouse-issues/issues/142) | [Warehouse] P6-11 · The accessories absorption path, stated in advance so it is a decision rather than a discovery | Accessories absorption scope; do not assume integration G43 |
| [#144](https://github.com/neetub1508/warehouse-issues/issues/144) | [Warehouse] P6-12 · Multi-level BOM with routings is not built — recorded so the refusal is a decision with a way back in | Multi-level BOM/routings intentionally deferred; advanced scope G32/G33 |
| [#165](https://github.com/neetub1508/warehouse-issues/issues/165) | [Warehouse] P2-12 follow-up · RMA expiry job (RJ-012) — open RMAs expire on the site's date | RMA expiry in local date; return-supply completeness if used |
| [#166](https://github.com/neetub1508/warehouse-issues/issues/166) | [Warehouse] P2-11 follow-up · Pack evidence and item documents cannot be deleted out from under a sealed carton | Sealed packing evidence retention; execution integrity |
| [#167](https://github.com/neetub1508/warehouse-issues/issues/167) | [Warehouse] P2-24 follow-up · A reservation remembers the part the customer asked for when a substitute is held | Requested/fulfilled identity; G11 |
| [#168](https://github.com/neetub1508/warehouse-issues/issues/168) | [Warehouse] P2-24 follow-up · MERGE_DEMAND is read by the demand calculation | Demand merge consumer; G10 |
| [#169](https://github.com/neetub1508/warehouse-issues/issues/169) | [Warehouse] P2-16 follow-up · Cost Layers and Valuation Policies screens | Valuation-policy/cost-layer maintenance; G36 |
| [#170](https://github.com/neetub1508/warehouse-issues/issues/170) | [Warehouse] P2-16 follow-up · Movement lines keep the approved cost, the source-currency amount and the cost source line | Frozen approved cost/source currency; G36/G48 |
| [#171](https://github.com/neetub1508/warehouse-issues/issues/171) | [Warehouse] P2-16 follow-up · Receipts, supplier returns, transfers and workshop returns give the costing engine what it needs | Cost source inputs on movements; G36 |
| [#172](https://github.com/neetub1508/warehouse-issues/issues/172) | [Warehouse] P2-16 follow-up · Ratify costing defaults, contract codes and run the integration tests in the gate | Cost defaults and gate validation; G36 |
| [#173](https://github.com/neetub1508/warehouse-issues/issues/173) | [Warehouse] Follow-up · Accounting envelope v2 — duty status, lot, serial and exchange rate per line | Cost envelope completeness; G36/G48 |
| [#174](https://github.com/neetub1508/warehouse-issues/issues/174) | [Warehouse] Follow-up · The accounting-facing adapter has no home — no module owns WhbAccountingHandoverSink or WhbGlBalanceProvider | Accounting adapter ownership; G36 |
| [#175](https://github.com/neetub1508/warehouse-issues/issues/175) | [Warehouse] Follow-up · Prove INTEGRATED mode end to end — WH-SC-156, WH-SC-157, CONFIG-CASE-07/10 | Accounting integration proof; G36 |
| [#176](https://github.com/neetub1508/warehouse-issues/issues/176) | [Warehouse] P2-02 follow-up · FR-150 / WH-SC-285 bin-to-bin movement has no owning task — the deferral, not a closure | Internal movement ownership; G39 |
| [#177](https://github.com/neetub1508/warehouse-issues/issues/177) | [Warehouse] P2-02 follow-up · RA-006 — P2-09's emergency replenish is specified as a BIN_TO_BIN transfer, which V511246 makes unbuildable | Emergency bin replenishment mismatch; G39 |
| [#178](https://github.com/neetub1508/warehouse-issues/issues/178) | [Warehouse] OD-20 · Does v1 ship a union valuation report across the two ownership domains? (gates P2-20, P2-27) | External/native valuation scope; G36/G46 |
| [#179](https://github.com/neetub1508/warehouse-issues/issues/179) | [Warehouse] P2-20 · WS-224's 365-day lower bound makes the as-at quantity a windowed net, not an all-time balance | Historical stock correctness; G19 |
| [#180](https://github.com/neetub1508/warehouse-issues/issues/180) | WhStockToGl search: an unescaped LIKE makes '_' and '%' live wildcards | Report search semantics; preserve literal/wildcard decision |
| [#181](https://github.com/neetub1508/warehouse-issues/issues/181) | wh_opening_stock_lines.validationStatus: a seeded filter row nothing can consume | Filter API/UI mismatch; include warehouse quality cleanup |
| [#182](https://github.com/neetub1508/warehouse-issues/issues/182) | WS-212 Ageing now scans the whole ledger: PP-7's bound was removed on purpose, and the cost is unmeasured | History-query performance; G37 |
| [#183](https://github.com/neetub1508/warehouse-issues/issues/183) | V511248's header loses its § characters, so MigrationHeaderRule fails and blocks every warehouse ci-gate run | CI blocker reported; G38 |
| [#184](https://github.com/neetub1508/warehouse-issues/issues/184) | P2-21: four product calls taken by default in report pack 2 | Unratified report product decisions; reconcile before planner KPI reuse |
| [#185](https://github.com/neetub1508/warehouse-issues/issues/185) | RH-010 unmet: WS-215 cannot be scheduled without a platform commit | Scheduled report permissions/platform dependency; G40 |
| [#186](https://github.com/neetub1508/warehouse-issues/issues/186) | [Warehouse] W13-1 carry: WH-SC-044…WH-SC-059 not demonstrated (SCENARIO-CATALOGUE.md not available locally) | Missing acceptance evidence; G38 |
| [#187](https://github.com/neetub1508/warehouse-issues/issues/187) | [Warehouse] Site-access 403s name the wrong permission (shared requirePermitted) | Permission diagnostics; scope testing G40/G47 |
| [#188](https://github.com/neetub1508/warehouse-issues/issues/188) | [Warehouse] P4-13 follow-up · Refuse an unlotted regulated item at the item screen; Schedule H1 prescriber/patient fields (adviser-gated) | Regulated-item scope; validate applicable customer requirements with appropriate expertise |
| [#189](https://github.com/neetub1508/warehouse-issues/issues/189) | [Warehouse] Putaway Rules: creating/editing a zone-less rule (FIXED_LOCATION or CONSOLIDATE_SAME_LOT) always 500s | Putaway execution blocker; G38 |
| [#190](https://github.com/neetub1508/warehouse-issues/issues/190) | [Warehouse] Receiving Sessions export labels the Site column "Warehouse" | Export label consistency |
| [#191](https://github.com/neetub1508/warehouse-issues/issues/191) | [Warehouse Base] Style x Variant Matrix: no code path ever creates a "style" — page is permanently empty | Master-data creation path; assess style/variant scope |
| [#192](https://github.com/neetub1508/warehouse-issues/issues/192) | [Warehouse Base] Stock Periods: "Site" column marked sortable but sort is silently ignored | Master-grid UX; verify sorting contract |
| [#193](https://github.com/neetub1508/warehouse-issues/issues/193) | [Warehouse] Channel order import rejects lines with no uomCode instead of defaulting to the item's base unit | UOM import contract; G34 |
| [#194](https://github.com/neetub1508/warehouse-issues/issues/194) | [Warehouse] Handovers: shipment picker shows literal "TRACKING - null" when ship-to name is blank | Execution UI quality; retain in normal warehouse backlog |

## Closure semantics that affect this comparison

- #106 and #96 have corresponding demand/replenishment and sister-transfer implementation evidence.
- #99 is open and is the primary policy-computation scope anchor.
- #156 was folded into #33; that does not establish a shipped classification recomputation engine.
- #157 was closed as duplicate, with work folded into multiple master/configuration issues; current supplier-site behavior must be reconciled.
- #81 and #95 were voided. #102 and #108 were recorded as not required. #150/#151 refer to removed dealer/services adapters. Their closed state is not current integration coverage.
- #167 includes stale caller assumptions alongside base requested-item support; #168 remains relevant to demand calculation.

## Coverage not to confuse with competitor absence

The reference catalog covers forecasting, segmentation, streams/netting, policy optimization, network/location, supersession, repair, causal inputs, lifecycle, last buy, K-curve, historical scenarios, overrides, explanations, integration, analytics and automation. It also records broader asset/connected/dealer capability families.

It does not establish complete implementations of vendor pricing optimization, every asset optimization variant, mobile/offline operation, all solver algorithms, every industry-specific regulatory control or all deployment/security options. Mark these **unknown or out of selected scope**, not “vendor lacks feature.”

## Targeted vendor demonstration / evidence requests

1. Confirm current version, modules and exact entitlement; reconcile AUO/ASO and package naming.
2. Demonstrate a forecast-to-order flow with a late correction, substitute and partial receipt; export the explanation and source lineage.
3. Show AutoPilot failure, restart and repeated same-day approval behavior; identify exact publish/idempotency semantics.
4. Demonstrate base-date change versus restored snapshot versus historical simulation; show synthetic initial-state labels.
5. Provide current read/write API contracts, data-cutoff/reconciliation rules and source-authority matrix.
6. Confirm Snowflake’s role in the selected deployment, data residency, retention, compute costs and export/exit process.
7. Demonstrate supplier/site validity, capacity, frozen horizons and a network change mid-horizon.
8. Show demand-merge versus physical substitution and direction/quantity-factor behavior.
9. Demonstrate uncertainty/service target calibration and an infeasible constrained plan.
10. Explain current hosting/recovery/security controls with contractual evidence; do not infer them from a marketing claim or a single customer certification.
11. Price the same scope and data size across vendors, including implementation, connectors, users, support and ongoing analytics consumption.
12. Identify the specific “manual state” screen the user remembers; map it to a documented mechanism.

## Local follow-up evidence before implementation approval

- Re-run the affected warehouse CI/acceptance scenarios in the repository’s supported environment.
- Inspect folded-task outcomes and current source resolution for supplier-site preferences and classification calculation.
- Prove consistent snapshot/event bootstrap and complete master-change feeds.
- Trace all supported demand, reservation, substitute, return, purchase and transfer callers.
- Confirm current adopted design decisions before amending SPI documentation or assigning modules.
- Benchmark a representative pilot dataset and verify restoration without duplicate execution.
- Validate source readiness and desired service outcomes with actual SMB/midmarket pilot customers.

The architecture and checklist provide a strong starting contract. A staged pilot and these targeted checks are still necessary to discover customer-specific behavior that public documentation and static inspection cannot establish.
