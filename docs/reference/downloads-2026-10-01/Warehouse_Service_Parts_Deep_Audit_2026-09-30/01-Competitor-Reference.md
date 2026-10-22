# Service-parts planning: competitor reference

Research date: 2026-09-30. Read [the index](README.md) for scope and evidence rules.

**Evidence:** vendor documentation establishes documented behavior; marketing establishes a vendor claim. Every paragraph labeled “our proposal,” “lesson,” or “inference” is our analysis. It is not a claim about proprietary implementation. PTC technical help reviewed identifies Servigistics 13.1.0.5 and PAI 5.0.0.1; individual release-note behavior is version-specific.

## 1. Product scope and commercial boundaries

Servigistics covers service-parts forecasting, inventory optimization and supply planning. Its current website also describes AI-assisted supply-chain optimization. A marketed capability does not establish its algorithm, tenant architecture, availability in every package, or measured performance in our data.

For this product comparison, keep four separate layers: warehouse execution; statistical planning; network/asset optimization; analytics and planner workflow. Our warehouse primarily supplies execution and planning inputs. Adding the other layers requires a new planning component and explicit write-back contracts.

Source: [P01: Servigistics product overview](https://www.ptc.com/en/products/servigistics)

## 2. Packages affect what “PTC has” means

The August 2025 SaaS service description distinguishes cumulative commercial packages and separate aviation/defense offerings. Foundation includes core forecasting, multi-echelon inventory optimization, order planning and foundational analytics. Higher tiers add capabilities such as historical simulation, advanced analytics, network optimization, connected service-parts management, advanced forecasting and asset-oriented optimization. Snowflake credits appear in the analytics entitlement. Package, usage and sizing terms must be checked against a customer’s contract; no defensible dollar-price comparison was established here. Product documentation is therefore evidence that a capability exists in a documented configuration, not that every Servigistics customer receives it.

Source: [P02: PTC SaaS service description, August 2025](https://ptc-p-001.sitecorecontenthub.cloud/api/public/content/312715bc95994beb94cb013a4906dbe8?v=9c7c8608)

## 3. Snowflake: the documented architecture

The PAI Advanced installation guide documents this analytics pipeline:

```text
Servigistics source RDBMS: Oracle or SQL Server
  → AutoPilot extraction → temporary CSV → Snowflake stage → Snowflake tables
  → Intellicus queries and cube processing → Intellicus database
  → dashboards consuming Snowflake and Intellicus data
```

This establishes a Snowflake analytics path. It does not establish that Snowflake is the transactional stock ledger, the universal planning engine, or the storage behind all modeling instances.

**Our proposed decision:** preserve warehouse OLTP; isolate planning projections and compute; add analytical infrastructure only when measured workload warrants it. Snowflake is an optional deployment choice. The important reusable idea is separating operational writes, analytical reads and expensive calculations.

Source: [P03: PAI Advanced with Snowflake](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/install/install_planning_advanced_snowflake.html)

## 4. Snowflake operational details

PTC documents a database/schema/stage and separate AutoPilot and Intellicus warehouses and users/roles. AutoPilot has loading/creation responsibilities; Intellicus reads analytical data. Example configuration includes auto-suspend/resume and small compute.

**Our proposed requirements:** independent credentials, least-privilege loading and querying, compute budgets, failed-load isolation, freshness reporting, atomic activation of a completed dataset, schema compatibility checks and a deletion/export policy. Do not copy installation-example passwords or assume example sizing is a production recommendation.

Source: [P04: Snowflake installation instructions](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/install/install_instructions_pai_advanced_snowflake_2.html)

## 5. AutoPilot is a batch-processing framework

The documented AutoPilot runs configured processes over segments at configured frequencies. The documented integration flow downloads host data through transfer tables, processes application data and writes upload transfer tables for the host. Processes can run separately or together.

**Our proposed equivalent:** an observable dependency graph for ingestion, validation, forecasting, policy calculation, supply proposals and publishing. Each step needs a durable checkpoint and explicit failure behavior. AutoPilot terminology alone does not justify unattended purchase approvals or an LLM making stock decisions.

Source: [P05: AutoPilot glossary](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/autopilot.html)

## 6. Manual runs and a different base date

A manual AutoPilot run can select processes and segment scope; Parts AutoPilot Base Date can replace the current date for processing. This is a calculation-date control.

**Inference:** a base-date override alone cannot prove that input data were restored to what users knew on that date. Our UI must separate “calculate using a past business date with these inputs” from “replay the historical information available then.” Never move the warehouse system clock or backdate real receipts to implement a scenario.

Source: [P06: Running AutoPilot manually](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/core/core_topics/running_the_autopilot_manually.html)

## 7. Scheduling details

The job page exposes active state, frequency, scheduled date/time and selected segments/processes/reports/scenarios. Manual execution does not count toward scheduled frequency.

**Our proposed requirements:** timezone and daylight-saving rules; missed-run/catch-up policy; no overlapping publisher for the same scope; cancellation and pause semantics; scheduling priority; retries; bounded resources; and a trace from schedule to run to business output. Existing warehouse jobs are useful infrastructure but do not supply these planning semantics automatically.

Source: [P07: New/Edit Job Page (Fields)](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/core/core_pid/pid_new_edit_job_page.html)

## 8. Snapshots and modeling instances

Snapshot management records source instance, creation metadata, snapshot date, backup/schema information, usage and lifecycle status. It distinguishes production and modeling sources. A snapshot is a named input-state artifact.

A modeling instance combines a snapshot with a sandbox and has its own readiness/running/failure/pool lifecycle. These are separate concepts: retaining an input state, provisioning a place to calculate, and running a model.

**Our proposal:** named immutable input manifests plus isolated scenario output. Full database cloning is optional; referentially complete dataset snapshots may be simpler for SMB deployments.

Source: [P08: Snapshot Management Page (Fields)](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/core/core_pid/pid_snapshot_management.html); [P09: Modeling Instances Page (Fields)](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/core/core_pid/pid_modeling_instances.html)

## 9. Historical simulation and “manual state”

The simulator exposes a simulation period and advancing simulation date independently of actual execution dates. It supports pause/resume/stop and comparison of supply-chain results. Its edit page includes preparation/reuse of initial data, per-process frequencies, pause points and parameters for initial stock, orders, demand and returns. Some starting conditions can be manually supplied or synthesized. Aborting and restarting have different effects from pausing.

Therefore “manual state” may mean manually initialized simulation inventory, a paused simulator, a manual forecast/override, or a base-date override. The exact phrase supplied by the user was not tied to a specific vendor screen.

**Our proposal:** label each scenario OBSERVED, RECONSTRUCTED or SYNTHETIC; show what was assumed. A historical date is not evidence that a scenario recreates real history.

Source: [P10: History Based Simulator Page](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/core/core_smart_help/sh_history_based_simulator.html); [P11: Historical simulator configuration](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/core/core_pid/pid_history_based_simulator_add_edit.html)

## 10. Snowflake Time Travel is a different mechanism

Snowflake Time Travel queries or clones retained past database state. Retention depends on edition and object type; the documentation describes a standard one-day period and up to 90 days for eligible permanent objects on higher editions. Historical queries use current schema, and some object types are not covered by cloning in the same way.

No evidence reviewed establishes that PTC’s historical simulator or modeling instances use Snowflake Time Travel. Database retention also cannot supply missing business events, expired external feeds or unrecorded historical configuration.

**Our proposal:** application-level run manifests and explicit history retention remain necessary regardless of database choice.

Source: [S01: Snowflake Time Travel](https://docs.snowflake.com/en/user-guide/data-time-travel)

## 11. Forecast method catalog

The documented method catalog includes Average, Causal, Composite, Croston, Do Not Forecast, Double Exponential Smoothing, Disaggregation, Intermittence Smoothing, Leading Indicators, Life Limited Parts, Linear Regression, LLP Maintenance Raw, LLP Maintenance Smooth, Manual, Moving Average, Replacement Rate, Same As Last Year, Scheduled Event Maintenance, Single Exponential Smoothing, Servigistics ML, Servigistics ML Composite, TSB, Weighted Average and Winters Multiplicative.

This is a method inventory, not a recommendation to implement all methods. Our MVP should provide transparent baselines, intermittent-demand methods, explicit manual/no-forecast modes and backtesting before adding more complex models. Preserve a model interface so additional methods do not require changes to warehouse tables.

Source: [P12: Forecast method catalog](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/forecast_method.html)

## 12. Best fit and method stability

Best-fit configuration includes historical horizons, evaluation windows, error measures and model/smoothing parameters. Reviewed documentation includes RMSE, MAPE, MAD, composite/tracking measures, statistical/ML blending and TSB probability smoothing. Method evaluation is more than selecting the smallest in-sample error.

A release note adds a required improvement percentage before switching methods, with different new-install and upgrade defaults. This is useful evidence of the need to prevent method churn; it is not justification for copying a default into our product.

**Our proposal:** rolling-origin tests; protected holdouts; explicit zero-demand metric behavior; baseline comparison; stable fallback; model-switch threshold; user-visible training window and selection explanation.

Source: [P13: Best Fit Management](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/core/core_pid/pid_best_fit_management_page.html); [P14: Forecast error improvement enhancement](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/release_notes/release_13_1_0_0/rn_enhancements_fcst_3.html)

## 13. Intermittent and declining demand

PTC’s Croston documentation separately smooths demand sizes and intervals. The documented implementation has a history requirement and a fallback/review path; such a requirement is product behavior, not a universal mathematical rule. TSB updates occurrence probability each period, making the treatment of consecutive zero periods explicit.

**Our proposed requirements:** distinguish a true zero from an absent feed; test long runs of zero demand; separate demand-size and occurrence parameters; handle first demand after inactivity; and avoid treating blocked sales as genuinely zero demand. Monitor forecast bias and inventory outcomes as well as statistical error.

Source: [P15: Croston Forecast Method](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/croston_forecast_method.html); [P16: Servigistics TSB Forecast Method](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/servigistics_tsb_forecast_method.html)

## 14. ML and equipment-driven forecasting

The ML-method page names candidates including BATS, AutoETS, Prophet, XGBoost and SARIMA. These belong to different modeling families; “ML” is a product grouping and does not imply every candidate is deep learning.

Life-limited forecasting uses utilization such as cycles/hours and maintenance-life information. The documented page also guides new adopters toward causal forecasting.

**Our proposal:** create optional installed-base/usage/maintenance feeds with time-valid part applicability and data-quality scores. Keep deterministic maintenance requirements separate from stochastic failures and routine sales. Do not promise useful equipment forecasts without reliable asset exposure data.

Source: [P17: Servigistics ML Forecast Method](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/servigistics_ml_forecast_method.html); [P18: Life Limited Parts Forecast Method](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/life_limited_parts_forecast_method.html)

## 15. Demand streams and forecast consumption

The documentation distinguishes demand and forecast streams. Forecast netting prevents confirmed demand from simply being added again to an unconsumed forecast.

**Our proposed requirements:** explicit sales, service, warranty, emergency, planned-maintenance and internal-transfer treatment; mapping between order and forecast buckets; forward/backward consumption windows; cancellation/unconsumption; and protections against counting a request, reservation, shipment and return as four independent demands. Our present monthly totals are useful summaries, but this new module needs source-level facts.

Source: [P19: Demand Stream](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/demand_stream.html); [P20: Forecast Stream](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/forecast_stream.html); [P21: Forecast Netting](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/forecast_netting.html)

## 16. Inventory policy and service trade-offs

Stocking-policy what-if supports changing assumptions, recalculating/resetting and examining inventory/service consequences and exchange curves. Space constraints can limit the recommended volume of parts at a location.

**Our proposal:** first define the service target: unit fill, line fill, cycle service, response-time attainment and equipment availability are different objectives. Calculate constrained recommendations with a visible infeasibility result; preserve non-stock policies and critical minimums. Warehouse bin capacity and planning location budget are separate constraints. A locally calculated safety-stock number is not multi-echelon optimization.

Source: [P22: Stocking Policy Page (What If)](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/inv_opt/inv_opt_smart_help/sh_stocking_policy_what_if.html); [P23: Space Constraints](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/space_constraints.html)

## 17. Part chains and future applicability

Part chains distinguish replacement/alternate behavior and the use of older stock, demand and condition quantities. Future part-chain logic includes location-specific availability, planning effectivity and lead-time/buffer interactions.

**Our proposal:** retain requested item and fulfilled item; keep physical interchange permission separate from demand aggregation; support directional and effective-dated edges, quantity ratios and location applicability. Detect cycles, overlapping alternatives and conversions that create fractional indivisible units. Changing a future chain must not relabel historic shipments.

Source: [P24: Part Chain](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/part_chain.html); [P25: Future Part Chains](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/part_chain_2.html)

## 18. Rotables, return losses and repair yield

PTC describes rotable-bank planning and distinguishes usable and repairable conditions and purchase/repair options. Separate glossary concepts cover losses before a return reaches the depot, unsuccessful repair, and no-fault-found returns that can become usable without a normal repair cycle.

**Our proposal:** independent return probability, return delay, inspection delay, no-fault-found probability, repair success, repair time, scrap and supplier capacity. A returned core cannot immediately count as usable supply. Tie a forecast repair receipt to a core or an explicitly probabilistic return model; do not count both.

Source: [P26: Rotable parts planning](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/parts/parts_topics/overview_of_rotable_parts_planning.html); [P27: Return Wash Rate](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/return_wash_rate.html); [P28: Repair Wash Rate](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/repair_wash_rate.html); [P29: No Fault Found Rate](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/no_fault_found_rate.html)

## 19. Supply changes, capacity and fairness

Schedule Change Suppression uses controls on order changes and timing to reduce unnecessary rescheduling. Its interactions with procurement and repair matter. Fair-share priority orders shortage allocation objectives; its documented value is advisory rather than a universal hard enforcement switch.

Capacity release notes describe supplier monthly capacity for procurement and repair, priority behavior and configuration dependencies.

**Our proposal:** use separate frozen, controlled-change and open horizons; model dated capacity and explicit shortfall; recheck shared supplier/donor capacity across recommendations. Show whether a constraint is hard, soft or informational. Avoid oscillating buy/expedite/cancel recommendations on each run.

Source: [P30: Schedule Change Suppression](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/schedule_change_suppression.html); [P31: Fair Share Priority](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/fair_share_priority.html); [P32: Supplier capacity enhancement](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/release_notes/release_13_1_0_0/rn_enhancements_sp_2.html)

## 20. Time-phased planning interaction details

A 13.1.0.4 change adjusts which future requirements affect certain present-day review reasons and order timing. It also addresses inventory-position interpretation on repeated same-day runs after auto-approval.

**Our proposed regression lesson:** separately test today’s stock risk, future dated need and the position before/after approval. Rerunning after accepting proposals must recognize newly created supply. An “available now” warning cannot simply reuse a future net-requirement expression.

Source: [P33: Time-Phased ROP](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/release_notes/release_13_1_0_4/rn_enhancements_sp_2.html)

## 21. Location, coverage and network design

The network-optimization release note describes installed-base coverage by response time, manual assignment rules and cumulative cross-border delays. A location detail page also contains location-lock and planning/network attributes.

**Our proposal:** distinguish site, bin, virtual planning node, stocking responsibility, geographic service territory and supply lane. Store response-time assumptions and border/handling delay separately from distance. Existing warehouse locations should remain execution identities; dealer or customer coverage should not require fake physical bins.

Source: [P34: Network Optimization](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/release_notes/release_13_1_0_0/rn_enhancements_io_16.html); [P35: Part-chain location details](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/core/core_pid/pid_part_chain_details_page_locations_tab.html)

## 22. Overrides, exceptions and explanations

SKU override documentation describes expiry and precedence interactions; removing an override does not necessarily immediately restore recalculated values. The Review Board supports scoped review types and workflow status/notes. Order Explanation retains process/date/sequence context and calculation detail.

**Our proposal:** override reason, author, scope, effective dates, expiry and conflict precedence; explicit recomputation; acknowledgment separate from resolution; exception deduplication; and an explanation linking the input facts and rule versions to each recommendation. A free-text AI explanation must never replace the actual calculation trace.

Source: [P36: SKU overrides](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/sku_override.html); [P37: Review Board](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/parts/parts_smart_help/sh_ipws_forecast_review_board.html); [P38: Order Explanation (Fields)](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/core/core_pid/pid_order_explanation_report.html)

## 23. A documented integration example

The ServiceMax integration describes flows through AWS AppFlow and S3 CSV, with inbound master/demand/stock data and outbound stock levels. ERP retains authority for several commercial/master attributes. This is evidence of a defined adapter pipeline, not a universal real-time integration topology.

The page’s stated input-flow count and the enumerated list are not fully aligned. Do not infer an unnamed dataset; validate the chosen product version’s complete interface specification during implementation.

**Our proposal:** publish a canonical interface catalog with source authority, schema version, timestamps, batch completeness, reconciliation and target acknowledgment. Native and external sources should share business semantics.

Source: [P39: ServiceMax integration: creating flows](https://support.ptc.com/help/servicemaxcore/en/articles/servigistics_integration/creating-flows.html)

## 24. Syncron: service network and lifecycle integration

Syncron markets service-parts planning around demand, inventory and network decisions, including installed-base/service-history inputs and dealer/distributor planning. Its service-supply-chain material describes segmentation, supersession, supplier collaboration and broader service processes.

**Lesson for us:** design optional collaboration boundaries and external-node feeds from the start. A native WMS connection can simplify onboarding, but it is not evidence that competitors lack execution integration. Validate a vendor’s exact supported workflow and connector freshness in a demonstration.

Source: [C01: Syncron service-parts planning](https://www.syncron.com/solutions/service-parts-planning); [C02: Syncron service supply chain](https://www.syncron.com/solutions/service-supply-chain/)

## 25. Baxter Planning: planning through execution

BaxterPredict is presented as a platform linking service-parts planning, order execution and issue resolution with enterprise-system integration. Its lifecycle material addresses new-product introduction, end-of-life and repair planning; Planning as a Service adds an operating-service model.

**Lesson for us:** track a recommendation through acceptance, execution and actual outcome, and budget for onboarding/planner support. Integration and exception follow-through are competitive requirements. Do not assume a forecasting screen alone completes the service-parts workflow.

Source: [C03: Baxter platform](https://baxterplanning.com/platform/); [C04: Baxter service-parts planning](https://baxterplanning.com/resources/blog/reimagining-service-parts-planning/); [C05: Planning as a Service](https://baxterplanning.com/resources/blog/planning-as-a-service-explained-benefits-for-your-business/)

## 26. ToolsGroup: uncertainty and service-driven inventory

ToolsGroup’s aftermarket material emphasizes probabilistic demand, slow/intermittent items and inventory planning across a network to meet service objectives.

**Lesson for us:** preserve uncertainty, not only a point forecast. Test forecast distributions over lead-time demand and evaluate achieved service and inventory. Product marketing does not disclose enough to replicate its proprietary optimizer or establish superiority on our customers’ data.

Source: [C06: ToolsGroup aftermarket planning](https://www.toolsgroup.com/industries/aftermarket/)

## 27. Smart Software: modular inventory-policy decisions

Smart IP&O presents demand planning, inventory optimization and inventory-policy analysis with collaborative and what-if workflows.

**Lesson for us:** a smaller customer can receive value from defensible reorder-policy recommendations, service-risk visibility and a practical review queue before advanced network or asset optimization. Preserve modular adoption. This research does not establish an exclusive vendor position in the midmarket or a comparable public price.

Source: [C07: Smart IP&O](https://smartcorp.com/demand-inventory-planning-optimization-software/)

## 28. Netstock: a small detail with large consequences

Netstock’s supersession help distinguishes supersession from interchange. It describes moving history to a new parent, treatment of old stock/open orders and different factor conventions in different import formats: one direction expresses old units per new unit, another new units per old unit. Combining overlapping source mechanisms can be invalid.

**Our proposed requirement:** normalize every external conversion to a single named numerator/denominator convention. For example, two old units replacing one new unit must behave identically regardless of import format. Preserve the original factor and source format for audit. Test reciprocal mistakes, zero/negative factors and multi-edge chains.

Netstock’s broader material also emphasizes supplier and classification visibility; this illustrates that pragmatic replenishment UX belongs in our SMB benchmark.

Source: [C08: Netstock supersessions explained](https://help.netstock.com/en/articles/12441710-supersessions-explained); [C09: Netstock advanced bundle](https://www.netstock.com/ce/advanced-bundle/)

## 29. SAP: time-valid network and planning interactions

SAP’s APO service-parts documentation includes distribution-network structure, forecasting, distribution requirements and repair-related planning. This source is legacy APO documentation, not evidence of all current S/4HANA packaging.

A versioned S/4HANA page documents specific supersession/ROP behavior and limitations. Such restrictions are a reminder that a capability matrix must record combinations and versions, not merely mark individual features “yes.”

**Our proposal:** test network validity dates, successor dates and planning policy together, including a topology change mid-horizon. Keep interface migrations and historical model compatibility explicit.

Source: [C10: SAP APO service-parts planning](https://help.sap.com/docs/sap_supply_chain_management/cd9e0c364e1e41e19ea633db7862222e/47e12f019e014ac5e10000000a42189d.html); [C11: SAP S/4HANA versioned supersession planning](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/f340785101c548c9beeda9284efd18a0/2bdec353b677b44ce10000000a174cb4.html?locale=en-US&state=PRODUCTION&version=2025.001)

## 30. Oracle: substitution and repair interaction

Oracle EBS 12.2 service-parts planning documentation combines supersession, repair-related supply, installed-base considerations and sourcing. It distinguishes substitution/repair relationships and sequences the consideration of usable alternative supply and replenishment.

**Our proposal:** a single requirement can be met by local stock, an allowed substitute, a transfer, repair or purchase. Evaluate the permitted options without double-counting the underlying stock or core. Expose the order of evaluation and its constraints. This source concerns EBS 12.2, not a claim about current Oracle Fusion architecture.

Source: [C12: Oracle EBS 12.2 Service Parts Planning](https://docs.oracle.com/cd/E26401_01/doc.122/e48778/T515331T515340.htm)

## 31. Lokad: decisions under uncertainty

Lokad’s material describes probabilistic forecasts and economic decisions for stock and assets.

**Our proposal:** evaluate expected stockout, holding, obsolescence, expedite and service costs when reliable inputs exist. Report sensitivity when costs are estimates. A simple, explainable constrained policy is preferable for an initial SMB deployment to an apparently precise objective built from invented penalty costs.

Source: [C13: Lokad probabilistic forecasting](https://www.lokad.com/probabilistic-forecasting-definition/); [C14: Lokad asset and stock management](https://www.lokad.com/asset-and-stock-management/)

## 32. K-curve: inventory versus ordering workload

PTC documents K-curve scenarios that compare cycle inventory with ordering/receipt workload across order-frequency sets and K values. Selected scenario results can be promoted into tactical planning. This is a different trade-off from safety-stock versus service probability.

**Our proposal:** retain order/receipt workload as a future policy objective; a recommendation that saves stock but creates hundreds of tiny orders may be impractical for a small team. Promotion must use the same controlled policy-publication path as other model outputs. No vendor savings percentage is adopted as our expected benefit.

Source: [P40: K-curve methodology](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/parts/parts_topics/overview_of_k_curve_management.html)

## 33. Aggregation and disaggregation

PTC supports aggregation of an item’s demand from multiple locations, forecasting at an aggregation location and distribution back to children using calculated historical shares or user weights.

**Our proposal:** version membership and allocation weights, conserve totals after rounding, define zero-history children and new sites, and prevent aggregate forecasts from being counted as additional independent demand. Forecast hierarchy reconciliation and network supply optimization are distinct functions.

Source: [P41: Demand aggregation and forecast disaggregation](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/demand_aggregation_and_forecast_disaggregation.html)

## 34. Last-time-buy details

The documented workflow covers end-of-production/vendor discontinuation, remaining support demand, alternative supply and usage decay. It supports centrally planned allocation and independent regional planning. Where installed-base history is unavailable, comparable lifecycle patterns can inform the estimate. A separate profile feature clusters completed lifecycles, retains profile statistics and requires profile approval before forecasting use.

**Our proposal:** store analog/profile selection, evidence quality, regional constraints, support horizon and uncertainty. Reapprove materially changed profiles. Separate the final ordering deadline from last delivery date and end of support; these are not interchangeable dates.

Sources: [P42: Last Time Buy](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/last_time_buy.html); [P43: Last Time Buy Profile](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/last_time_buy_profile.html)

## 35. Causal forecasting: evidence thresholds and BOM

PTC documents BOM-based forecasts and failure-rate estimation from demand, installed base and causal exposure. It can force a host-provided failure rate or transition to a calculated rate when configured exposure/population/history thresholds are met.

**Our proposal:** retain rate provenance and evidence thresholds; never infer a reliable failure rate from a tiny exposure denominator. Version BOM/application dates and distinguish replacement at assembly level from component consumption. Account for changing installed populations, retired equipment and incomplete telemetry. Defaults in vendor documentation are not validated thresholds for our customers.

Source: [P44: Causal Forecast](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/causal_forecast.html)

## 36. Broader capability families and naming changes

PTC’s current capabilities page names forecasting, multi-echelon optimization, asset sustainability optimization, network optimization, lifecycle analysis, connected service-parts management with ThingWorx, initial provisioning, K-curve, last-time buy and dealer inventory management. Its asset-oriented capability targets stocking decisions against complex-asset availability objectives.

The SaaS description and other materials use additional naming such as AUO. Do not assume identical algorithms or licensing from similar names across document versions. Service pricing and the broader service portfolio also require separate scope checks.

**Our proposal:** treat asset availability, IoT/condition-based demand, dealer collaboration and service pricing as explicitly gated expansion areas. A warehouse fill-rate metric cannot substantiate an equipment-uptime guarantee. Package and naming reconciliation belongs in a vendor demonstration, not in speculative schema design.

Source: [P45: PTC Servigistics capabilities](https://www.ptc.com/en/products/servigistics/capabilities)

## 37. What is still not publicly established

- Exact proprietary optimization objectives, solvers, convergence tolerances, inventory-distribution fitting and source code.
- Current hosted deployment topology, tenant isolation implementation, all failover internals, data residency options and actual measured end-to-end latency.
- Complete API/export schemas, entitlement-by-contract, rate limits, support SLAs and comparable commercial quotes.
- All interactions of advanced asset optimization, K-curve, clustering, pricing and connected-product feeds.
- Whether every current customer uses the documented PAI/Snowflake path or any given historical-simulation implementation.
- Exact meaning of the user’s remembered “manual state” screen.

These are vendor-validation items. They are not assumed warehouse defects. The architecture in file 03 is a proposed design for our product, not a reconstruction of private PTC internals.
