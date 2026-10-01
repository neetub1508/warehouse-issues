PTC SERVIGISTICS 13.x: INVENTORY OPTIMIZATION (IO/MEO), NETWORK OPTIMIZATION, MODELING/SCENARIOS/SIMULATION. NOTES FROM THE LOCAL HELP CRAWL

Citation convention: every source URL begins with
B = https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/
so "[B]inv_opt/..." means B + that path. Every URL below is the first line of a file in the local crawl. Nothing was written to the repo. Scratch concat files are in the scratchpad (a1..a18.txt).

Coverage gaps (stated up front):
- The crawl has no IO page on seasonality in the optimizer. The only "season" hits are forecasting glossary terms such as Croston and double exponential smoothing. IO consumes the forecast (Forecast Type / Causal Forecast Scenario).
- It has no "lateral transfer" term. The closest are Order Plan Balancing, the IO Balancing Parameters and Inventory Studio Transfer Recommendations.
- It has no "system availability" or "product availability" wording. Availability is equipment availability under MIME, with network, location and contract variants.
- "Response time" appears only in Network Optimization.
- There is no explicit "min stock rules" or "stock/no-stock rule" page. What exists: the ASL Strategy/ASL Method, SKU Constraints/Overrides, Committed Parts, and ROP = -1 meaning not stocked.

======================================================================
1. MODULE OVERVIEW AND PURPOSE
======================================================================
- Goal: "stock the right parts, in the right place, at the right time". The questions IO answers:
  - What fill rate is achievable for a given investment?
  - What would an optimal solution cost at the existing fill rate?
  - What does fill rate X% cost for a group?
  - What is the best solution given budget X, group fill rate Y% and a minimum Z% at all locations?
  Source: [B]inv_opt/inv_opt_topics/inventory_optimization_overview.html
- IO "extends the capabilities of the Stock Level Generation process by providing stocking recommendations to meet target service levels (and/or budget limitations)". It considers the network as a whole, "where the stock level at upper echelons impact the resupply lead time for the downstream stocking locations". PTC cites "typically 25 to 40 percent" savings on top of SKU-based planning. (same URL)
- Scope rules (same URL):
  - Only ASL SKUs are considered.
  - A SKU is excluded when it is not in the scenario segment coverage, or when its price is below the OPT_MIN_UNIT_COST global setting.
- IO considers (same URL):
  - replenishment and procurement lead times
  - backorder delays that affect resupply lead time
  - target objectives
  - stock overrides, minimums and maximums per SKU or for all SKUs
  - min/max fill rate per SKU, per subset or for all SKUs
  - maximum budget per subset or for all SKUs
  - how far ahead to consider forecasts
- Optimizer core: "a suite of Marginal Analysis algorithms that minimize inventory investment subject to a configurable combination of aggregate performance targets and SKU constraints and overrides". Source: [B]glossary/inventory_optimization_objective_cost.html

Optimization modes. Global setting INVENTORY_OPTIMIZATION_MODE; default MEO. Source: [B]glossary/global_settings_io.html
| Value | Meaning |
|---|---|
| SIO | Single Item Optimization |
| MIO | Multi-Item Optimization |
| MEO | Multi-Echelon Optimization (default) |
| MIME | Multi-Indenture Multi-Echelon Optimization |

Mode-dependent behaviour:
- SIO:
  - Service targets cannot be added or modified [B]inv_opt/inv_opt_pid/pid_service_group_parameters_create_edit.html
  - Budget constraints cannot be added or modified (same URL)
  - The Churn Control field is disabled [B]glossary/churn_control_method.html
- MIO: the Minimum Network Fill Rate target cannot be added or modified [B]glossary/customer_location_fill_rate.html
- MIME only:
  - the "Availability and Fill Rate" service metric [B]glossary/service_metric.html
  - Network/Location Availability [B]glossary/network_availability.html
  - the Network Availability Exchange Curve page [B]inv_opt/inv_opt_smart_help/sh_network_availability_exchange_curve.html
  - the Contract display on Service Group Results [B]glossary/global_settings_io.html
  - the "*…with Availability" containers on Scenario Budget Summary [B]inv_opt/inv_opt_smart_help/sh_scenario_budget_summary.html
- ASL Strategy defaults to Optimize ASL in MIO/MEO [B]glossary/asl_strategy.html

Menu structure (IO pages), from [B]inv_opt/inv_opt_topics/meo_available_pages.html:
- Scenario Results: Scenario 360, Scenarios, Scenario Summary, Location Summary, Part Summary, Segment Summary, SKU Summary, Service Group Results, Part Supply Chain, Stocking Policy, Inventory Collaboration
- Scenario Analysis: Network Visual Analytics, Location Visual Analytics, Location Detail Report, SKU Detail Report, Forecast Pooling Report, Rotable Pool Report, Indenture and Echelon Report, Network Availability Exchange Curve
- Budget Report: Scenario Budget Summary, Part Budget Summary, Service Group Budget Summary, Prioritized Buy List
- Overrides: SKU Overrides, Override Security, Override Assignment, Override Reasons, Optimization Set Assignments
- Base Setup: Inventory Optimization Planning Parameters, Segments, Service Group Parameters, Optimization Sets
- Optional Parameter Setup: Rotable Pool Constraints, Forecast Pooling Parameters, Coefficient of Variation Parameters, Variance to Mean Cap Parameters, Respect Production Parameters, Inventory Optimization Balancing Parameters, Current Inventory Parameters, Category
- Optional Feature Setup: External Scenario, External Stock Level, Analytic Type, Exception Criteria, Replacement Rate, What-If Model
- Menu path groupings seen in breadcrumbs:
  - Scenario Configuration > Parameters / Churn Control / SKU Override / Optional Features
  - Advanced Configuration: Time Phased Service Groups, CoV Cap, VMR Cap, Rotable Pool Constraints
  - Additional Modules: Network Optimization, K-Curve Methodology
  Sources: [B]core/core_topics/module_io_configuration_churn_control.html, [B]core/core_topics/module_io_network_optimization.html, [B]inv_opt/inv_opt_pid/pid_time_phased_service_groups_create_edit.html

======================================================================
2. SERVICE-LEVEL TARGETS: METRICS, LEVELS, HOW THEY ARE SET
======================================================================
2.1 Service Metric (chosen per Service Group; "Once the service metric selection is saved, it cannot be changed"). Source: [B]glossary/service_metric.html
- Fill Rate: "percentage of demand met from off-the-shelf inventory". Only fill rate targets can be set.
- Availability and Fill Rate: "percent of time the equipment is operational". Both targets can be set. MIME only.
- Fill Rate with Emergency Backup: considers stock at a designated emergency backup location when the primary lacks stock.

2.2 Service Group Parameter = "a set of service targets and constraints that are applied to SKUs belonging to segments". Source: [B]glossary/service_group_parameter.html
- Targets drive Availability, Fill Rate, Emergency Fill Rate and Wait Time at group level. Three kinds: Service Targets, Location Targets, Contract Targets.
- Constraints:
  - Budget Constraints: collective, across one or more segments
  - Space Constraints: collective
  - SKU Constraints: per SKU
- Segments associate SKUs with the group.
- Can be entered on the Service Group Parameters page and in the Service Group Parameters container on Scenarios.
- "Service targets drive the performance at a group level; SKU constraints enforce the performance of segments" [B]glossary/sku_constraint.html

2.3 Create/Edit Service Group Parameter dialog (eight section groups). Source: [B]inv_opt/inv_opt_pid/pid_service_group_parameters_create_edit.html

Details section:
- Name, Service Metric, Parent Membership, Location Hierarchy, Emergency Backup Location Hierarchy, Comments, Category, Currency, Minimize Stockout Cost (checkbox), Reference/Stockout Unit Cost (Fill Rate), Reference/Stockout Unit Cost (Wait Time).
- Location Hierarchy is only for Fill Rate or Availability+FR. Emergency Backup Location Hierarchy is only for FR with Emergency Backup.

Parent Membership options:
- Direct: only segment-matching SKUs are in the group; parent SKUs don't participate in result aggregation. With location-based FR/wait-time targets, "Parents SKUs not in the service group will get optimal stocking to support the targets at child locations". With Network Targets, only in-group items are optimized. "Not supported for availability service groups due to the inherent nature of multi-echelon optimization".
- Derived – Reporting: as Direct, but parent SKUs participate in total result aggregation.
- Derived – Targets and Constraints: segment SKUs and parent SKUs are placed in the group and participate in optimization and aggregation.

Service Targets tab (Count and Range are rolled up from the Location and Contract tabs; example "99… 2 of 49… 15% to 88%"):
- Customer Network Fill Rate: "lowest acceptable percentage of time that the parts … are available to the technicians… overall fill rate for the network".
- Customer Location Fill Rate (Default): weighted by external demand only.
- Total Location Fill Rate (Default): weighted by external plus internal demand.
- Primary Emergency Fill Rate (Default): customer-facing plus first-level emergency location.
- Secondary Emergency Fill Rate (Default): first level plus the backup covering the first-level backup.
- Network Wait Time (days), Location Wait Time (days) (Default).
- Network Availability, Location Availability (Default): MIME only.
- Contract Wait Time (days) (Default), Contract Availability (Default).

Location Targets tab (per location): Customer Fill Rate, Total Fill Rate, Primary Emergency FR, Secondary Emergency FR, Average Wait Time (Days).

Contract Targets tab (per contract): Min Contract Availability, Max Contract Wait Time.

Capacity/Space Constraints tab:
- Tab label comes from SPACE_CONSTRAINT_TYPE; default "Cubic Meter".
- Fields: Default Max Space (all locations); Max Space (by location).
- Required space = Stock Maximum x Cubic Meter per Unit (from the Parts page).

Budget Constraints tab:
- Currency.
- Reference/Stock Maximum Budget: "maximum inventory investment… stock maximum quantity (TSL) multiplied by the price".
- New Buy Budget Scope: Interval (same budget every period) or Fiscal Year (enables Fiscal Optimization). Does not affect Stock Max value constraints.
- Reference/New Buy Budget: new buy qty x price.
- Reference/Repair Budget: "repair cost limit in an optimization interval".

SKU Constraints tab: Min/Max Fill Rate, Min/Max ROP, Min/Max ROP (days), Min/Max Safety Stock, Min/Max Safety Stock (days), Min/Max Stock Maximum, Maximum Stock Maximum (days), Maximum Wait Time, Wait Time Confidence Level.

2.4 Service Group Parameters page groups:
- Groups: Details, Service Targets, Budget Constraints, SKU Constraints, Adjustments for Location/Contract Targets.
- Extra list fields: Cubic Metric Constraints indicator, Space Constraint check, Time Phased Records (count of time-phased groups), Wait Time Confidence Percent.
- Total Location Fill Rate = "aggregated service level of SKUs in the group weighted by total forecast".
Source: [B]inv_opt/inv_opt_pid/pid_service_group_parameters_page.html

2.5 Time Phased Service Groups: the same targets, constraints and budgets with a Begin Period.
- "The Date for the Begin Period… determines what service group is effective on the Optimization Interval Calculate For Date. If a scenario is recalculated during a period, the Time Phased Service Group associated with that date is used." [B]release_notes/release_13_0_0_0/rn_enhancements_io_5.html
- Fields: [B]inv_opt/inv_opt_pid/pid_time_phased_service_groups_create_edit.html
- Can also be created for emergency-backup groups [B]glossary/emergency_backup_location_optimization.html

2.6 Metric definitions
- Fill Rate / Total Fill Rate: "fraction of demand that is met through immediate stock availability, without being backordered… based on the Fill Rate Method selected on the scenario" [B]glossary/fill_rate.html, [B]glossary/total_fill_rate.html
- Customer Fill Rate: "average total customer fill rate" [B]glossary/customer_fill_rate.html
- Network Fill Rate: "weighted by both external customer and internal forecasts across network" [B]glossary/network_fill_rate.html
- Customer Location Fill Rate: "weighted by external customer forecast for a location"; also computed for New Targets and Optimized Targets [B]glossary/customer_location_fill_rate.html
- Unit vs Line Fill Rate (scenario flag Use Line Fill Rate). Source: [B]glossary/use_line_fill_rate.html
  - Example: 7 on shelf and an order for 10 gives unit FR 70%, line FR 0%.
  - Line FR uses Customer Order Size (avg default 1, std dev default 0, Line Fill Rate Safety Factor default 0).
  - SS, ROP and Stock Max become multiples of the Customer Order Size.
  - Not considered for availability models.
  - "Contact your PTC Account Representative to change the line fill rate safety factor" [B]inv_opt/inv_opt_pid/pid_scenarios_page_create_and_edit_fields.html
- Availability: "expected percentage of time that equipment is operational" [B]glossary/availability.html
- Location Availability: "weighted by population at each location" [B]glossary/location_availability.html
- Average Population: "average product roll out multiplied by the quantity of the part per unit of the product… used by the availability calculation" [B]glossary/average_population.html
- Wait Time: "expected time in days that the incoming demand has to wait", = Expected Backorder / Total Daily Forecast [B]glossary/wait_time.html
- Location Wait Time: "weighted by customer forecast at each location" [B]glossary/location_wait_time.html
- Network Wait Time / Equipment Wait Time: expected wait for equipment to be available upon failure [B]glossary/network_wait_time_days.html, [B]glossary/equipment_wait_time_days.html
- Wait Time Confidence Level: "probability… that the true wait time would be below the calculated wait time with large samples", a user SKU Constraint [B]glossary/wait_time_confidence_level.html
- IO_HIGHEST_WAIT_TIME_CONF: sets the confidence level used to report the calculated wait time for the user-specified Max Wait Time [B]inv_opt/inv_opt_pid/pid_sku_summary_container.html
- Customer Backorder Days (Wait Time): expected days a customer waits [B]glossary/customer_backorder_days_wait_time.html
- Customer Demands (Fill Rate): "expected number of unsatisfied customer demands" [B]release_notes/release_13_1_0_0/rn_enhancements_io_20.html
- EBO (Expected Backorder): "average units of demands that are waiting to be filled at any point of time in an optimization interval… function of pipeline forecast, pipeline forecast variance and stock level… EBO is Wait Time * Total Daily Forecast" [B]glossary/ebo.html
- Weighted EBO = (EBO x Customer Period Forecast x Criticality Multiplier) / Total Period Forecast [B]glossary/weighted_ebo.html
- Network Weighted EBO = sum over SKUs [B]glossary/network_weighted_ebo.html
- Weighted Backorder is "Replaced with Weighted Equipment EBO" [B]glossary/weighted_backorder.html
- Total EBO: summed per page level (location, part, scenario, segment) [B]glossary/total_ebo.html
- Criticality Multiplier: "criticality factor of the SKU that can be used to influence the optimization selection. For the availability model, this also impacts the availability calculation" [B]glossary/criticality_multiplier.html
- Contract Availability [B]glossary/contract_availability.html
- Mean Days to Remove and Replace: a scenario input, up to 4 decimals [B]glossary/mean_days_to_remove_and_replace.html
- Customer Order Size: "effective quantity in which customers use SKU… when Use Line Fill Rate is enabled… performance is measured by the ability to satisfy complete orders"; default 1 [B]glossary/customer_order_size.html

2.7 Segments, criticality and target assignment
- Segment: "group of SKUs that have attributes in common". Parameters are applied via segment coverages.
  - Example: a critical-parts segment with Demand Accommodation set to 100%.
  - Strategies: Matrix Segmentation and Pyramid Segmentation.
  Source: [B]glossary/segment.html
- Segment Tree: node coverages are AND-ed with segment coverages; it is also a security layer (User Rights > Segment Folders) [B]glossary/segment_tree.html
- Optimization Set: "collection of service groups that are assigned to a scenario". Tabs [B]inv_opt/inv_opt_pid/pid_optimization_set_create_edit.html:
  - Service Groups (none selected means all)
  - Exception Criteria
  - Segments ("limited to part and location dimensions… define the set of SKU that will be modeled")
  - Summary Segments (drive the Segment Summary page)
  - Optional Process Group [B]release_notes/release_13_1_0_0/rn_enhancements_io_17.html
- An Optimization Set cannot be deleted while in use [B]inv_opt/inv_opt_pid/pid_optimization_set_fields.html
- Committed Parts page (forced minimum stocking): "a minimum quantity of a part must be stocked at a given location, regardless of the calculated stock level… a contract detail record can be overridden by a committed part record". A contract detail service level is ignored when a matching committed part exists. [B]inv_opt/inv_opt_smart_help/sh_committed_parts.html

======================================================================
3. OPTIMIZATION LOGIC: MARGINAL ANALYSIS, OBJECTIVES, COSTS
======================================================================
- Marginal Analysis: IO uses it "to optimally determine the best inventory investments in a service network" [B]glossary/marginal_analysis.html
- Bang for Buck (B4B): "the change in the SKU Objective Benefit divided by the change in the SKU Objective Cost" [B]glossary/bang_for_buck.html
- Objective Benefit Criteria (scenario setting) [B]glossary/objective_benefit_criteria.html:
  - Fill Rate Increment
  - EBO Reduction
  - If the SKU's Service Group has Minimize Stockout Cost on, the benefit is reduced stockout cost.
- Objective Cost Criteria [B]glossary/objective_cost_criteria.html:
  - Part Cost (default)
  - Optimization Cost. Waterfall: SKU Optimization Cost > Part Optimization Cost > SKU Part Cost > Part Part Cost.
  - "Carbon Tax (Embodied) + Part Cost" = (Embodied Carbon Per New Buy x Carbon Tax Rate) + Part Cost.
  - Regardless of the selection: New Buy Cost is the objective cost when enforcing New Buy Budget constraints; Repair plus New Buy cost is the objective cost in the "Availability with Repair Optimization algorithm".
- Three knobs "allow tuning of Bang for Buck": Objective Benefit Criteria, Objective Cost Criteria, Fill Rate Method [B]glossary/inventory_optimization_objective_cost_2.html
- Uses of a custom objective cost: reduce carbon, honor vendor incentives, apply promotions, "reduce the sensitivity of cost-based optimization on low cost parts that require high levels of service" [B]glossary/inventory_optimization_objective_cost.html. Introduced in 13.1.0.0; Optimization Cost can come via the Gateway [B]release_notes/release_13_1_0_0/rn_enhancements_io_5.html
- Minimize Stockout Cost [B]glossary/minimize_stockout_cost.html, [B]glossary/minimize_stockout_cost_2.html:
  - Stockout costs (loan cost, contract penalty, expedite cost) influence "mix and depth".
  - Waterfall: SKU > Part > IO Planning Parameter > Service Group Parameter.
  - "If a SKU in Service Group does not have a stockout cost defined, it cannot be stocked"; the Service Group default (system default 1) is the "safety net".
  - Stockout Cost (Fill Rate) = (1 - Fill Rate) x Interval Customer Forecast x Stockout Unit Cost (FR) [B]glossary/stockout_cost_fill_rate.html
  - Stockout Cost (Wait Time) = (EBO / Total Daily Forecast) x Interval Customer Forecast x Stockout Unit Cost (WT) [B]glossary/stockout_cost_wait_time.html
- Budget-constrained optimization: Stock Maximum Budget, New Buy Budget (Interval or Fiscal Year scope) and Repair Budget per service group (section 2.3).
- Fiscal Optimization (scenario checkbox) [B]glossary/fiscal_optimization.html, [B]glossary/fiscal_optimization_2.html:
  - Enables Number of Fiscal Years and Fiscal Interval (Period / Quarter / Year; default Quarter) and disables Horizon/Interval.
  - Uses FISCAL_YR_STARTING_MONTH. IO_FISCAL_YR_STARTING_MONTH is also listed as a 13.0 global setting [B]release_notes/new_in_13_0_0_0.html
  - A fiscal budget defined without Fiscal Optimization is ignored, with a warning.
- Repair Optimization: recommends a mix of existing good inventory, repairing repairables/repair forecasts, and new buy; "an enhancement of Churn Control". Source: [B]glossary/repair_optimization.html
  - Enable with IO_ENABLE_REPAIR_OPTIMIZATION=true: "currently only works with the availability model and the repair budget is for the period only".
  - Churn Control must be Use Inventory Balance or Use Inventory Balance with Reference Scenario.
  - Order Plan ignores Repair Budgets.
  - Is Repair Optimizable flag per SKU: when No, all repair forecast is assumed repaired and initial repairables count as serviceable [B]glossary/is_repair_optimizable.html
- Processing order with emergency backup (from [B]glossary/emergency_backup_location_optimization.html):
  1) location optimization and multi-echelon optimization
  2) network service group optimization
  3) emergency backup optimization
  4) MIME ignores emergency networks
  5) budget optimization
- Emergency Backup notes (same URL):
  - Setup: location hierarchy, then SGP with metric FR with Emergency Backup plus Primary/Secondary emergency targets, then add to an Optimization Set.
  - Not allowed with the approximate fill rate methods.
  - Emergency SKUs are excluded from churn-control group allocation.
  - Glossary says Covered SKUs always use Lost Sales FR. 13.0.1.0 changed this: "The Fill Rate method specified on the scenario is used instead of the Lost Sales Fill Rate method to make more conservative estimates", and allowed resupply-as-emergency-backup SKUs with local repair/NFF supply to participate [B]release_notes/release_13_0_1_0/rn_enhancements_io_3.html
- Exchange curves / investment curves:
  - Network Exchange Curve (Prioritized Buy List page): steps from mandatory new buy, then SKU minimum constraints/overrides, then discretionary increments, then the final mix meeting all targets, maximums, overrides and budgets. Trade-off of network backorders vs new buy cost; displays new buy cost vs availability/backorders/fill rate/wait time. "To see a path up to the levels that satisfy all targets, budget constraints should not be included in the scenario". Sources: [B]inv_opt/inv_opt_smart_help/sh_network_exchange_curve_container.html, [B]release_notes/release_13_0_1_0/rn_enhancements_io_5.html
  - Prioritized Buy List: Investment axis = New Buy Cost or Stock Maximum Value; Performance axis = Fill Rate, Weighted EBO or Availability. Part Buy List container. Generated only if the scenario flag "Generate Prioritized Buy List" is set. User right "Prioritized Buy List" [B]inv_opt/inv_opt_smart_help/sh_prioritized_buy_list_page.html
  - BUY_LIST_ROUNDING_RULE: -1 = no rounding; value v in (0,1] rounds as Truncate(qty + (1 - v)). Examples for 10.35: .0001 gives 11, .35 gives 11, .5 gives 10, 1 gives 10 [B]glossary/global_settings_io.html, [B]release_notes/release_13_1_0_3/rn_enhancements_io_2.html
  - Network Availability Exchange Curve (MIME): compares two curves of solutions at a performance metric (Backorders / Availability / Wait Time) vs stock max investment. Initial point is based on FR targets and location/contract availability or wait-time targets. The selected point is the current levels. Requires network targets [B]inv_opt/inv_opt_smart_help/sh_network_availability_exchange_curve.html. Fields: Availability, EBO, Index, Optimized Average Wait Time, ROP / ROP Value, SS / SS Value, Selected, Stock Max / Value [B]inv_opt/inv_opt_pid/pid_network_availability_exchange_curve.html
  - Inventory Collaboration has Fill Rate Exchange Curve, Fill Rate by Stock Level and Forecast vs ROP Value containers [B]inv_opt/inv_opt_smart_help/sh_inventory_collaboration_page.html
- Mandatory new buy: New Buy Need (Mandatory Local) = "minimum required new buy quantity over the optimization interval to prevent the inventory from falling below zero at the end of the optimization interval" [B]glossary/new_buy_need_mandatory_local.html

======================================================================
4. MULTI-ECHELON, MULTI-INDENTURE, POOLING
======================================================================
- Echelon: "The hierarchy level of the supply chain" [B]glossary/echelon.html
  - Shown in Lead Time Inputs [B]inv_opt/inv_opt_pid/pid_lead_time_inputs_container.html
  - A child's echelon must be greater than its parent's. Otherwise Apply Overrides To Production reduces backorders-from-above to 0 and logs "…the echelon value of the child is not greater than that of the parent" [B]release_notes/release_13_0_0_0/rn_enhancements_io_3.html
- Location Type: "type of this location in the procurement and replenishment hierarchy", defined on the Location Types page [B]glossary/location_type.html
- Location Hierarchy: associated with an SGP; ENABLE_LOCATION_HIERARCHY global setting (default false) [B]glossary/location_hierarchy.html, [B]glossary/global_settings_io.html
- Exclude MEO (system set): the calculation "identifies the set of root locations for those SKU, and then identifies all of the descendants"; SKUs needed for model completeness but outside the segment get Exclude MEO=True and are "fixed at their production stock levels" (ROP = Min ROP = Max ROP = Production ROP) [B]glossary/exclude_meo.html
- Is Optimized: Yes = planned by IO; No = level came from a constraint, override (incl. non-stock) or production [B]glossary/is_optimized.html
- Resupply lead time effects:
  - Effective Lead Time "includes the wait time due to shortages from the replenishment parent and from components" [B]glossary/effective_lead_time.html
  - Pipeline Forecast is demand over effective lead time "that includes the wait time from replenishment parent locations" [B]glossary/pipeline_forecast.html
  - Backorder from Parent Location and Backorder from Components are glossary terms (per the file list).
- Customer Order Size at resupply locations: IO_CALC_RESUPPLY_CUST_ORDER_SIZE (default CUSTOMER):
  - CUSTOMER = uses the children's COS
  - EFFOQ = uses the children's Effective Order Quantity
  - NONE
  - Previously IO_CALC_CUST_ORDER_SIZE true/false; the upgrade maps true to CUSTOMER and false to NONE.
  Sources: [B]glossary/global_settings_io.html, [B]release_notes/release_13_1_0_0/rn_enhancements_io_6.html
- Multi-indenture:
  - Indenture: "first indenture items are called LRU (Line Replacement Unit) and the lower indenture items are called SRU (Shop Replacement Unit)" [B]glossary/indenture.html
  - Replacement Rate page maintains replacement rates "for multi-indenture optimization" (the page text says "(MIO)") [B]inv_opt/inv_opt_smart_help/sh_replacement_rate.html
  - Indenture and Echelon Report: "aggregated system performance and investment by a combination of echelons and indentures" [B]inv_opt/inv_opt_smart_help/sh_indenture_and_echelon_report.html
  - Echelon and Indenture Details container on Service Group Results [B]inv_opt/inv_opt_pid/pid_indenture_echelon_container.html
- Rotable Pooling [B]glossary/rotable_pooling.html:
  - For "expensive, repairable, and have limited supply" parts. "should not be used for planning high volume parts".
  - Treats pool demand/stock "as though they were at one shared location" (Houston 5 + Chicago 13 = 18; a service group would average to 9).
  - Expected Pool FR/Wait Time is evaluated on an aggregate SKU: demands summed; Effective Lead Time and EOQ are demand-weighted averages.
  - Each pooled stock-max increment is checked against the Max Pool Stock Max and the targets. "The lowest cost solution that satisfies the parameter targets… is the result".
  - Processing: pool must contain locations with external demand; FR/WT use only external demand; all pre-opt overrides/constraints are respected; Min Pool FR / Max Pool WT overrides are applied before the Service Group Optimization; Pool Max Stock Max is enforced post-optimization; "Service Group targets may be violated".
  - Rotable Pool Constraints fields: Is Enabled, Maximum Pool Stock Maximum, Maximum Pool Wait Time (days), Minimum Pool Fill Rate, Name, Use Inventory Balance As Max [B]inv_opt/inv_opt_pid/pid_rotable_pool_constraints.html
  - Rotable Pool Report fields include per-part overrides for Max Pool Stock Max, Max Pool Wait Time and Min Pool FR (require recalculation), Primary Pool Location and Primary Pool Location EOQ [B]inv_opt/inv_opt_pid/pid_rotable_pooling_report_fields.html
  - 13.1 added the wait-time pooling target [B]release_notes/release_13_1_0_0/rn_enhancements_io_7.html
  - Parts module: SL_ROTABLE_ALLOCATION_BY_SS allocates Pool Safety Stock to locations on the Rotables page [B]parts/parts_pid/pid_rotable_levels_page.html
- Forecast Pooling: "compromise between consolidating parts into central stocking locations or utilizing regional warehouses and stocking many parts in the field locations"; defined on the Forecast Pooling Parameters page [B]glossary/pooling.html
  - Scenario flag "Run Forecast Pooling" [B]inv_opt/inv_opt_pid/pid_scenarios_page_create_and_edit_fields.html
  - Report fields: Annual Pool Savings (carrying-cost savings minus transport cost), Annual Transportation Cost, Pool Average Inventory Reduction, Pool Inventory Cost Savings, Pool Location, Pool Parameter, Pool Transport Mode, Pre-Pool Average Customer Daily Forecast [B]inv_opt/inv_opt_pid/pid_forecast_pooling_report_fields.html
- Not Repairable This Station (NRTS): "percentage rate at which the part will not be able to be repaired at the location" [B]glossary/not_repairable_this_station.html. ENABLE_NRTS (default true) uses the Return Wash Rate and NFF Rate for consumables [B]glossary/global_settings_io.html
- No Fault Found for Consumables was added to IO in 13.0 [B]release_notes/release_13_0_0_0/rn_enhancements_io_17.html

======================================================================
5. STOCK LEVELS: ROP, SAFETY STOCK, STOCK MAX, EOQ, ROUNDING
======================================================================
- ROP: "inventory position level at which a Procurement or Replenishment order is triggered". "A ROP of -1 indicates that the SKU is not stocked". Aggregated for a single period on the Part/Location/Scenario Summary pages; forecast-weighted average across periods on the Budget Summary pages [B]glossary/rop.html
- Safety Stock = Round((ROP - Pipeline Forecast) / Customer Order Size) x COS. Minimum -1; rounded again if COS is fractional [B]glossary/safety_stock.html
  - Under the Time-Phased ROP Order Policy: ((ROP - Pipeline Forecast)/COS) x COS, 2 decimals, no floor (13.1 change) [B]release_notes/release_13_1_0_0/rn_enhancements_io_19.html
  - "t" superscript marks a time-phased SS override set on the Interactive Planner Worksheet Time Series tab [B]glossary/safety_stock.html
- Safety Stock (days) = SS / Total Daily Forecast (0 if SS = -1 or no forecast) [B]glossary/safety_stock_days.html
- ALLOW_NEGATIVE_SAFETY_STOCK (default false): false floors SS at -1; true computes SS = ROP - rounded pipeline forecast. "The negative Safety Stock constraints and overrides drive the ROP required to yield ROP - rounded(onOrderMean)… ROP remains floored at -1" [B]glossary/global_settings_io.html, [B]inv_opt/inv_opt_pid/pid_service_group_parameters_create_edit.html
- IO_TPROP_ROUND_SS (default false): only evaluated when the Time-Phased ROP Order Policy is on. true rounds SS by the SS rounding rule (similar to Time-Phased SS results); false does not round, "consistent with Inventory Optimization, and is the recommended setting when using Time-Phased ROP" [B]glossary/global_settings_io.html
- Stock Maximum = ROP + Effective Order Quantity. 0 means not stocked [B]glossary/stock_maximum.html
- EOQ naming: in Supply Planning, EOQ = Economic Order Quantity; in IO, EOQ = Effective Order Quantity [B]glossary/eoq.html
- Effective Order Quantity: "result of applying rules, constraints, and overrides to the Economic Order Quantity" [B]glossary/effective_order_quantity.html
- EOQ inputs (IO Planning Parameters > Reorder Quantity tab) [B]inv_opt/inv_opt_pid/pid_inv_opt_planning_parameters_create_edit_fields.html:
  - Max EOQ (slices), Min EOQ (slices), Set EOQ (slices) (e.g. 20/slice x 1.25 = 25 units), Set EOQ (Quantity), Max REOQ (slices), Set REOQ (slices).
  - Ordering Costs: Procurement / Repair / Replenishment Order Cost (with reference currency). "Increasing Order Cost increases the EOQ".
  - Carrying Cost (%): "normally between 25% and 35% per year… Raising Carrying Cost lowers the EOQ".
- LEVELS_DAYS_CONSTANT (default false): true uses 30 (monthly) or 7 (weekly) days to convert EOQ slices to qty; false uses actual days [B]glossary/global_settings_io.html
- Lot sizing / rounding inputs (Reorder Quantity Inputs): Lot Size ("increments… for compatibility with vendor packaging"), Minimum Order Quantity, Procurement/Repair/Replenishment Fixed Order Size, Packaging Size, Pallet Size, Sales Size (falls back to Lot Size and Lot Size Round), EOQ Override [B]inv_opt/inv_opt_pid/pid_reorder_quantity_inputs_container.html
- IO_EXCLUDE_REPAIRS_IN_EOQ_DAYS_OF_SUPPLY: when true, the non-repaired daily demand rate uses the look-ahead-days average instead of the optimization-interval average [B]release_notes/release_13_0_1_2/resolved_issues_13_0_1_2.html
- IO_NEW_BUY_PROC_EFFOQ_THRESHOLD (default false): true triggers a PO only when New Buy Need (Procurement) is at least the Effective Order Quantity (compared) [B]glossary/global_settings_io.html
- Additive ROP: post-opt value added after all other overrides; integer > 0 (-1 + 5 = 4; 5 + 5 = 10) [B]glossary/additive_rop.html
- Order Periods (procurement/repair/replenishment; 0 = none): "Raising the number of days between Order Periods can significantly increase the ROP" [B]inv_opt/inv_opt_pid/pid_inv_opt_planning_parameters_create_edit_fields.html
- Time-Phased ROP vs Time-Phased Safety Stock order policies differ in Critically Short thresholds and Projected Net On Hand Good [B]core/core_pid/pid_loc_prop_page_stocked_parts_tab.html

K-Curve Methodology (KCM, cycle stock / order quantity), an IO "Additional Module":
- "operational approach to determine order quantity"; derives order frequencies meeting workload and inventory goals; "optimal exchange curve (workload vs. inventory)".
- "Inventory savings of 10%-15%… using 7 order frequencies versus the traditional ABC plans with only 3". "The parameter K links ABC order plans to EOQ theory".
- Steps: Order Frequencies, then Order Frequency Sets, then KCM Scenarios, Run (simulates cycle stock over a K range), pick a point, Generate SetEOQ, Make Scenario Production / Reject.
- Source: [B]parts/parts_topics/overview_of_k_curve_management.html
- KCM Scenario fields: Name, Note, Slice Type (monthly/weekly), Bucket Length, Min K Value, Max K Value, K Value Count, State, Respect Overrides, Segments, Order Frequency Set [B]parts/parts_pid/pid_new_edit_kcm_scenario_page.html
- Details page: Exchange Curve (Y = cycle stock inventory, X = number of orders); Details of Point Selected (K Value, Order Frequency Set, Average Inventory On Hand, Total Receipts); SKU Details (SetEOQ, Number Of Orders, Average On Hand) [B]parts/parts_pid/pid_kcm_scenario_details_page.html, [B]parts/parts_topics/viewing_managing_kcm_scenario_results.html

======================================================================
6. OVERRIDES, CONSTRAINTS AND PRIORITY RULES (MIN/MAX/FORCED STOCKING)
======================================================================
- SKU Override: pre- or post-optimization min, max or fixed on levels. Fixed excludes min/max; max must exceed min [B]glossary/sku_override.html
- Pre- vs post-optimization:
  - Pre-optimization values are applied before level optimization and "may impact other SKUs in the group" [B]glossary/pre_optimization.html
  - Post-optimization values impact only that SKU [B]glossary/post_optimization.html
  - Pre-opt limits can make other SKUs over-stock to compensate; post-opt limits may under-achieve targets [B]glossary/sku_constraints_and_overrides_2.html
- Override types (Create/Edit SKU Override): Fill Rate, ROP, Safety Stock, Stock Maximum, ROP (days), Safety Stock (days), Stock Maximum (days), EOQ, Repair EOQ, EOQ (slices), Repair EOQ (slices), Wait Time (days), Additive ROP. Default shown = MEO_SKU_OVERRIDE_TYPE (default ROP) [B]inv_opt/inv_opt_pid/pid_sku_overrides_page_create_edit.html
- Pre/Post matrix [B]glossary/sku_override.html:
  - EOQ and Repair EOQ (and the slice versions): pre-opt only.
  - Additive ROP: post-opt fixed only.
  - Wait Time: max only, both phases.
  - Others: fixed/min/max in both phases.
- Other override fields: Part, Location (both immutable), Begin/End Date, Reason (general), Comment, Reason (type), Production value [B]inv_opt/inv_opt_pid/pid_sku_overrides_page_create_edit.html
- Entry points: SKU Overrides page, SKU Detail Report, Stocking Policy (SKU Overrides container), Inventory Collaboration (Fill Rate by Stock Level, SKU Levels, SKU Overrides) [B]glossary/sku_override.html
- Deleting an override then running Apply Overrides does not revert the level; re-calculate instead (same URL).
- Supersession: the "Inventory Optimization - Run Supercession Changes" AutoPilot process moves overrides to the Top Most Revision part; the down-chain override End Date is set to the day before (same URL).
- Priority rules [B]glossary/sku_constraints_and_overrides.html:
  - If min and max conflict, the max wins.
  - Of multiple maxima, the lowest wins.
  - Of multiple minima, the highest wins.
- Optimization Phase order (lowest to highest): Pre-Opt Constraint, Post-Opt Constraint, Pre-Opt Override, Post-Opt Override [B]glossary/optimization_phase.html
- Override Rules [B]glossary/override_rules.html:
  - All types are converted to effective ROP.
  - A Fixed EOQ violating SM = ROP + EOQ is reset to SM override - ROP override.
  - "Avoid Having a SKU with Multiple Fixed Overrides": Fixed ROP 60 + Fixed FR 90% with 0 forecast gives ROP -1.
  - "A fixed Fill Rate or a maximum Fill Rate or days of supply override along with a 0 forecast will set the ROP = -1".
  - Worked examples cover min/max SM and ROP combos, and mixed pre/post (Pre Max ROP 5 + Post Min ROP 25 gives 25).
- Automatic Effective Order Quantity from overrides: Fixed ROP 3 + Fixed SM 7 gives Fixed EOQ 4; Fixed ROP + Min SM gives Min EOQ; Max ROP + Fixed or Min SM gives Min EOQ [B]glossary/sku_constraints_and_overrides.html
- SKU Constraints (on the SGP, segment-wide, pre/post min/max). Example: Min ROP 20 for a group. Changes require recalculation [B]glossary/sku_constraint.html
- Respect Override (scenario Yes/No): whether SKU Overrides and post-opt SKU Constraints are used. Must be Yes to Make Production [B]glossary/respect_override.html, [B]glossary/scenario_processes.html
- Override global settings [B]glossary/global_settings_io.html:
  - MEO_OVERRIDE_MAX_QTY (0 = no limit; above it requires confirmation)
  - MEO_OVERRIDE_CODE_REQUIRED (default false; Reason required)
  - MEO_OVERRIDE_DEFAULT_PERIODS_TO_EXPIRE (0 = no End Date; n = end of the nth period, e.g. 3 gives Apr 15 to Jun 30)
  - MEO_SKU_OVERRIDE_TYPE
  - IO_OVERRIDE_CLEANUP_EXPIRED_RECORDS_DAYS (default 180; purged by Synchronize Database; 0/-1 = never)
  - DEALER_APP_RESTRICTIONS (Dealer role cannot see Min/Max or pre-opt fields)
  - IO_APPLY_OVERRIDE_INCLUDE_POST_OPT_ONLY [B]glossary/scenario_processes.html
- Override Reasons page with a Default Override Reason flag [B]inv_opt/inv_opt_pid/pid_override_reasons_page_field.html
- ASL / stock-no-stock:
  - ASL Strategy: Respect External All (IO makes no ASL decision); Respect External Non-ASL ("may take ASL SKUs off ASL"); Optimize ASL ("recommended") [B]glossary/asl_strategy.html
  - ASL Method result: External Off (forced off), External On (forced on), Optimize [B]glossary/asl_method.html
  - ASL generation uses Pareto on Demand Accommodation %; non-ASL inventory is treated as excess [B]glossary/authorized_stocking_list.html
  - "Service Groups Include Non Stockable Items" (stockmax = 0): if selected, non-ASL demand is included and targets may not be reached [B]inv_opt/inv_opt_pid/pid_scenarios_page_create_and_edit_fields.html

======================================================================
7. DEMAND DISTRIBUTIONS, VARIABILITY CAPS, LEAD TIMES
======================================================================
- Distribution Profile [B]glossary/distribution_profile.html:
  - Low volume + low variance: Poisson
  - Low volume + high variance: Negative Binomial
  - High volume: mostly Normal. If IO_COV_THRESHOLD_NORMAL_TO_NEGBINOM >= 0 and the SKU COV exceeds it, Negative Binomial is used, shown as "Negative Binomial (High Volume)".
- Thresholds [B]glossary/global_settings_general.html:
  - SL_LOW_VOL_THRESH (default 25; range -1 or 0–25): Average Period Demand below it means low volume.
  - SL_LOW_VOL_VMR_THRESH (default 1.1; at least 1.0): VMR above it gives Negative Binomial, otherwise Poisson.
  - SL_LOW_VOL_VARIABILITY_CAP (default 9).
  - SL_HIGH_VOL_VARIABILITY_CAP (default 30).
  - SL_VARIABILITY_TYPE COV|VMR (default COV).
- SL_VARIABILITY_TYPE also enables the Coefficient of Variation Cap Parameters or VMR Cap Parameters page. Low/high volume caps are assigned per segment [B]glossary/global_settings_io.html. Page fields: Parameter Name, Low Volume and High Volume Cap [B]inv_opt/inv_opt_pid/pid_coefficient_of_variation_parameter_page_fields.html, [B]inv_opt/inv_opt_pid/pid_vmrcap_parameters_page.html
- COV = std dev / mean of pipeline forecasts; VMR = variance / mean [B]glossary/coefficient_of_variation.html, [B]glossary/variance_to_mean_ratio.html
- Non Capped Pipeline Forecast Variance: pipeline variance is "a function of the Average Demand, the Variance of Demand, the Average Composite Lead Time, and the Variance of the Composite Lead Time"; shows the value before caps [B]glossary/non_capped_pipeline_fcst_variance.html
- Look-ahead demand rate: Demand Rate Days Constant + (Demand Rate Days Multiplier x SKU Resupply Lead Time Days). "Used in the calculation of standard deviation in the levels calculations" [B]glossary/demand_rate_days_multiplier.html
- Lead-time inputs (mean and variance for each pipeline) [B]inv_opt/inv_opt_pid/pid_lead_time_inputs_container.html, [B]inv_opt/inv_opt_pid/pid_inv_opt_planning_parameters_create_edit_fields.html:
  - Composite Lead Time and Variance
  - Procurement, Repair, Replenishment and Return Lead Time and Variance
  - Order Periods
  - Return Wash Rate (returns forecast = Forecast x (1 - RWR)), Repair Wash Rate (10% gives repair 11 to get 10), NFF Rate, NRTS
  - Roll Up Demand as Repairable
  - Use Procurement/Replenishment Lead Time flags
  - Generate Procurement/Repair/Replenishment Orders
- Composite Lead Time method, MEO_REPAIR_TYPE [B]release_notes/release_13_0_1_0/rn_enhancements_io_2.html:
  - 1 = Serial Mode ("not recommended… backward compatibility")
  - 2 = Aggregate Mode (weights by proportion of use and wash rate, not demand; default for existing customers)
  - 3 = Demand Weighted Mode (weights by Return/Repair Wash Rate, NRTS, NFF and hierarchy; default for new installs; recommended on upgrade)
- Customer Order Size calculation (13.1): new AutoPilot "Customer Order Size Calculator" run by segment; Demand Streams "Use In Customer Order Size". Global settings [B]release_notes/release_13_1_0_0/rn_enhancements_io_6.html, [B]glossary/global_settings_io.html:
  - CUST_ORDER_SIZE_DMD_HIST_HORIZON = 24 months
  - CUST_ORDER_SIZE_MIN_DMD_RECS = 5 (below it, COS = 1 and SD = 0)
  - CUST_ORDER_SIZE_OUTLIER_HANDLING = REMOVE | REPLACE (mean ± std)
  - CUST_ORDER_SIZE_OUTLIER_STD = 3.0 (-1 = off)
  - CUST_ORDER_SIZE_VARIABILITY_CAP = -1 (a COV or VMR multiple per SL_VARIABILITY_TYPE; e.g. 3 under COV gives SD ≤ 3 x COS; under VMR gives SD ≤ sqrt(3 x COS))
- IO_EVALUATE_EMERGENCY_BACKUP_VALUES (default false; recommended for summarization speed) populates Emergency Period Forecast (Optimized) and Primary/Secondary Emergency FR [B]glossary/global_settings_io.html, [B]release_notes/release_13_0_0_0/rn_inv_opt_calc_improvements_5.html
- IO_EMERGENCY_NETWORK_SOLVES_COMMON_GROUPS (default true): loads non-emergency groups that share SKUs into the emergency algorithm [B]release_notes/release_13_0_0_0/rn_enhancements_io_14.html

======================================================================
8. CHURN CONTROL, CURRENT INVENTORY, BALANCING
======================================================================
- Churn Control Method (scenario) [B]glossary/churn_control_method.html:
  - None.
  - Use Inventory Balance with Reference Scenario: "most recently calculated non-churn scenario with the same scenario attributes".
  - Use Inventory Balance: current balance first, then the condemned forecast burns it down over the horizon.
  - Respect Production: ROP constraints from production values.
  - Respect Previous Period: from the prior period's results.
  - Tip: a high control/threshold above 100% in Respect Production lets ROP -1 go to 0 and 0 go to 1.
- Churn Control Reference Scenario [B]glossary/churn_control_reference_scenario.html
- Respect Production Parameters (min/max control as % that becomes SKU constraints, by segment) [B]inv_opt/inv_opt_smart_help/sh_respect_prod_parameters_page.html. Fields [B]inv_opt/inv_opt_pid/pid_respectprod_parameters_page.html:
  - Demand High / Low Threshold Percent: e.g. if current LTD > High% x production LTD, the high control limit is not applied.
  - High / Low Control Limit Percent: % above/below ROP acceptable.
  - Is Enabled, Parameter Name.
- Current Inventory Parameters ("inventory amounts to be used in churn control and in current inventory based scenarios"): multipliers for Onhand New, Onhand Fixed, Onorder, Backorder, Allocated, Inrepair, Onhand Bad, Inreturn [B]inv_opt/inv_opt_pid/pid_current_inventory_parameters_page.html
- IO Balancing Parameters ("cost effective rebalancing to occur quickly… excess to be worked down") [B]inv_opt/inv_opt_smart_help/sh_io_balancing_parameters_page.html
  - Fields: Name, Is Enabled, Reference Transshipment Cost/Currency, Transportation Cost.
  - Transport cost waterfall: Replenishment/Balance/Excess Recall use the Variable Transportation Cost on Replenishment/Balancing SKU Lead Time; Procurement/Repair use Vendor Location SKU Lead Time [B]inv_opt/inv_opt_pid/pid_io_balancing_parameters_page.html
- Order Plan Balancing (the lateral-transfer equivalent): moves excess to shortage locations "outside of normal replenishment", supports reverse balancing, prioritizes by need/proximity/excess. Shortage sort via OP_SHORTAGE_SORT_CRITERIA_1/2. "Balance also for downstream need" is not available with Time-Phased ROP [B]glossary/balancing.html, [B]glossary/balancing_2.html
- Availability Based Replenishment (OP_ENABLE_ABR): constrains downstream replenishment to source availability [B]glossary/availability_based_replenishment.html

======================================================================
9. SCENARIOS: DEFINITION, FIELDS, PROCESSES, STATES
======================================================================
- Scenario: "unique name given to a collection of inputs and results". The system scenario "Production" is read-only and cannot be deleted or run [B]glossary/scenario.html
- Create/Edit Scenario sections: General, Optimization Scope, Stocking Strategy, Look Ahead Days for Demand Rate [B]inv_opt/inv_opt_pid/pid_scenarios_page_create_and_edit_fields.html

General:
- Name (no single quote).
- Production Approval Type: Approve All / Pending All / Exception Criteria. Exception Criteria forces "Run exceptions for all periods".
- Complete Before Summarization: splits Calculate Stock Levels and Calculate Summary Values. After stock levels, SKU Summary, SKU Detail Report, Inventory Collaboration and Part Supply Chain are visible and Make Production / Generate Order Plan can run while summaries continue.
- Exception Criteria: all periods / first period / do not run.
- Category, Generate Prioritized Buy List, Reporting Hierarchy, Note.
- Summarize Excluded SKUs (formerly "Summarize Excluded Pairs") [B]release_notes/release_13_1_0_0/rn_enhancements_io_11.html

Optimization Scope:
- Optimization Set, Fiscal Optimization, Start Date.
- Horizon (periods): e.g. 48 slices = 4 yrs. "The zero (0) slice in the Horizon is the End Of Production (EOP) date".
- Interval (periods): 3 = quarterly, 12 = yearly, 1 = monthly.
- Number of Fiscal Years, Fiscal Interval, What-If Model.

Stocking Strategy:
- Objective Benefit Criteria, Mean Days to Remove and Replace, Respect Override, ASL Strategy, Use Line Fill Rate.
- Fill Rate Method:
  - "Fill Rate/Probability In Stock"
  - "…with Reorder Quantity Benefit"
  - "Approximate Fill Rate: 1 – Expected Backorder (ROP+1) / Reorder Quantity" (supply perspective)
  - "Approximate Fill Rate: 1 – Expected Backorder (ROP+1) / Pipeline Forecast" (demand perspective)
- Service Groups Include Non Stockable Items, Churn Control Method, Run Forecast Pooling, Objective Cost Criteria.
- Forecast Type: Production / Recommended (only if ENABLE_FORECAST_APPROVAL) / Causal Forecast Scenario. Causal Forecast Scenario.
- Use External Values: None / Use Inventory Position (Current Inventory Parameters) / Use External (External Scenario). External Scenario.

Look Ahead: Constants (Days), Lead Time Multiplier.

- Interval > 1 made production back-fills the in-between slices (e.g. May 45 fills Jun and Jul) [B]inv_opt/inv_opt_smart_help/sh_scenarios_page.html
- Scenarios page Run menu: Calculate; Evaluate Exception Criteria; Make Production; Clear Optimized Production Values; Apply Overrides; Delete; Approve All Pending SKU; Copy; Approve All Overrides; Apply Overrides To Production; Apply SKU Overrides Locally To Production; Generate Summary Data for Production; Generate External Reporting Data; Generate External Production Reporting Data; Start Collaboration. Containers: Global Settings at Runtime, Scenarios, Service Group Parameters, Tasks (same URL).
- Process semantics [B]glossary/scenario_processes.html:
  - Calculate: deletes prior results; copy first to retain them.
  - Make Production (from Complete or Promoted To Production): uploads SKUs whose Production Approval Type is not Pending or Disapproved; warns about pending SKUs; multiple production scenarios are supported; the previous production scenario reverts to Complete; needs Respect Override = Yes; deletes future-period order plan net forecast stock level records per SKU uploaded (worked 5/7/9 example).
  - Clear Optimized Production Values: removes the Production scenario and future order-plan levels; "designed for use during testing".
  - Apply Overrides: the apply-post-opt flag is ignored, so all overrides are applied as post-opt, subject to IO_APPLY_OVERRIDE_INCLUDE_POST_OPT_ONLY.
  - Apply Overrides To Production: run twice for TMR EOQ overrides.
  - Apply SKU Overrides Locally To Production: daily incremental; does not remove deleted or expired overrides, update summaries or apply EOQ.
  - Generate Summary Data for Production: only when IO_CREATE_PROD_SUMMARY_IN_STANDALONE_JOB_ONLY = true.
  - Generate External (Production) Reporting Data: for legacy custom code only; IPCS_MEO_SCENARIO_SKU.
  - Start Collaboration: sets In Collaboration = Yes.
- Global settings tied to Make Production and summaries [B]glossary/make_production.html, [B]glossary/global_settings_io.html:
  - IO_EVALUATE_OVERRIDE_COUNT, IO_EVALUATE_PRODUCTION_PART_SUMMARY, IO_EVALUATE_EMERGENCY_BACKUP_VALUES
  - IO_PRODUCTION_SCENARIO_SKU_SQL_METHOD (1 default: create + append; 2: union)
  - IO_PROD_SKU_TRACKING (0 = none, so no "Promoted to Production"; 1 = current period, recommended for large configs; 2 = all periods, default; table IPCS_MEO_PROD_SKU)
  - IO_CREATE_PROD_SUMMARY_IN_STANDALONE_JOB_ONLY
- Scenario State (system-controlled): Completed, Created, Failed, Needs Recalculation, Production, Running, Waiting To Run, Waiting to Delete, Waiting to Apply Overrides, Waiting To Make Production, Promoted To Production [B]glossary/state.html
- Scenario Workflow Status (with Complete Before Summarization): Model Incomplete, Making Stock Level Changes, Candidate (external scenario or Respect Override on), Non-Candidate, Making Production, Promoted, Production [B]glossary/scenario_workflow_status.html
- External Scenario / External Stock Level: define external levels per part/location "to compare against the optimal stocking levels" [B]inv_opt/inv_opt_smart_help/sh_external_scenario_page.html, [B]inv_opt/inv_opt_smart_help/sh_external_stock_level_page.html
- Global Settings at Runtime container: global setting values at scenario run time; needs the Global Parameters right [B]release_notes/release_13_1_0_0/rn_enhancements_io_12.html
- AutoPilot performance properties: servigistics.meo.max.concurrent.index.creation (default 10), servigistics.meo.max.concurrent.parts, servigistics.submit.part.model.queries.sequentially, servigistics.io.make.production.create.table.update, servigistics.meo.update.locnode / "-param buildLocNode" [B]release_notes/release_13_0_0_0/rn_inv_opt_calc_improvements_2.html, [B]release_notes/release_13_0_0_0/rn_inv_opt_calc_improvements_4.html, [B]release_notes/release_13_0_0_0/rn_inv_opt_calc_improvements_7.html
- Exception results table per scenario "EC<scenarioId>" [B]release_notes/release_13_0_0_0/rn_inv_opt_calc_improvements_3.html

======================================================================
10. SCENARIO RESULTS PAGES AND COMPARISON (UI TERMS)
======================================================================
- Scenario Summary: compare at three levels (scenario, location, service group). Read-only. Production is hidden unless "All" is selected. Run: Approve Pending / Reject Pending (by scenario and Calculate For Date). Containers: Distinct Location (ROP>0), Effective Service Group Parameter, Exception Criteria, Fill Rate, Fill Rate vs ROP Value, Scenario Inputs, Scenario Job History, Scenario Summary, Scenario Values, Tasks [B]inv_opt/inv_opt_smart_help/sh_scenario_summary_page.html
  - Comparison fields show (A), (B) and (Delta) [B]glossary/fill_rate.html
- Scenario Summary container fields (partial list): Allocated Inventory Balance, Annual Pool Savings, Approved Overrides, Approved SKUs, Availability (Optimized), Average Population, Carbon Tax fields, Churn Control Method, Cubic Meter Required, Customer Backorder Days, Customer Demands (FR), Customer Daily/Period Forecast (In Line)(Optimized), Distinct Parts, Distinct ROP/SS Locations and Parts, Embodied Carbon, Emergency Period Forecast (Optimized), Expected Gross Profit, Expected Inbound/Outbound Orders, Expected On Hand Value, Equipment Wait Time, Inventory Balance (Value), Inventory Turns, Locations with Error/Hold/Warning Exception Criteria, New Buy / Cost / Cost (Mandatory), New Buy Need (Mandatory Local), Optimized SKUs, Parent Scenario, Pending Overrides, Pending SKU, Planned COGS… [B]inv_opt/inv_opt_pid/pid_scenario_summary_container.html
- SKU Summary: compares two scenarios per part. Run [B]inv_opt/inv_opt_smart_help/sh_sku_summary_page.html:
  - Approve (sets Approved)
  - Disapprove
  - Approve All Pending SKU and Disapprove All Pending SKU (by page criteria, "includes SKUs that are not visible")
  - Additional Data / containers: Constraint and Override Details, Exception Criteria, Journal, Part Chain Details, Service Group, SKU Exception, SKU Overrides
  - Delta filter
  - IO_FULL_COMPARE_MODE (default false = only records in the first scenario) [B]glossary/global_settings_io.html
  - EXCEL_EXPORT_ESCAPE_CHARACTER (= or t) [B]release_notes/release_13_1_0_0/rn_enhancements_io_9.html
- Location Summary: compares two scenarios at a location; Hierarchy or List display. Run: Approve Pending / Reject Pending (sets Disapproved). Containers: Location Summary, Exception Criteria, Service Group A, Service Group B, SKU Summary [B]inv_opt/inv_opt_smart_help/sh_location_summary_page.html
- Location Detail Report Run: Approve, Approve All Overrides for Selected Location, Disapprove [B]inv_opt/inv_opt_procedures/proc_location_detail_report_page_approve.html, [B]inv_opt/inv_opt_procedures/proc_location_summary_page_approve_all_overrides.html, [B]inv_opt/inv_opt_procedures/proc_scenario_location_summary_disapprove.html
- Part Supply Chain: distribution over the network for a part in two scenarios. Run: Approve/Reject Pending [B]inv_opt/inv_opt_smart_help/sh_part_supply_chain_page.html
- Service Group Results: "compares the minimum performance level that was expected and the actual performance level" for two scenarios. Display Contract/Location/All. Approve/Reject Pending. Echelon and Indenture Details container [B]inv_opt/inv_opt_smart_help/sh_service_group_results_page.html
- Segment Summary: compares segments. Run: Approve All Pending SKU, Start Collaboration (schedulable) [B]inv_opt/inv_opt_smart_help/sh_segment_summary_page.html, [B]release_notes/release_13_1_0_0/rn_enhancements_io_18.html
- Scenario 360°: KPIs with drill-down; many containers (Budget Report, exception containers, Production Summary, SKU Override and Constraint Overview…) [B]inv_opt/inv_opt_smart_help/sh_scenario_360.html
- Scenario Budget Summary: compares 2+ scenarios of future investment. MAXIMUM_ADDITIONAL_SCENARIOS_DISPLAY_COUNT (0–12, default 5; user override on "Set Additional Scenarios Selection Size"). Containers include Budget Detail, Carbon Footprint/Summary, Inventory Turns with FR, New Buy Cost with FR/Availability, Planned Revenue, Stock Max with FR/Availability, Total Cash Outflow… [B]inv_opt/inv_opt_smart_help/sh_scenario_budget_summary.html, [B]release_notes/release_13_1_0_0/rn_enhancements_io_2.html
- Inventory Collaboration: "view and approve level recommendations… and enter SKU overrides". Containers: Constraint and Override Details, Daily Demands, Demand/Forecast Graph, Fill Rate by Stock Level, Fill Rate Exchange Curve, Forecast vs ROP Value, Journal, Part Chain Details, SKU Demand Details, SKU Exception, SKU Levels, SKU Overrides, Time Series [B]inv_opt/inv_opt_smart_help/sh_inventory_collaboration_page.html
  - The feature was renamed "Dealer Planning" [B]release_notes/release_13_0_0_0/rn_enhancements_io_8.html
- Optimization Set Assignments: planner-to-set mapping; after Start Collaboration the planner's Scenario selector auto-populates [B]inv_opt/inv_opt_smart_help/sh_optimization_set_assignments.html
- SIOP metrics (13.1) [B]release_notes/release_13_1_0_0/rn_enhancements_io_14.html:
  - Expected Gross Profit = Resale Price x Interval Forecast - (newbuy + repair cost)
  - Expected Inbound Orders
  - Expected Outbound Orders
  - Inventory Turns = (Daily Demand Rate x 365) / Average Inventory
  - Planned COGS = New Buy Cost + Repair Cost
  - Planned Revenue = Resale Price x Interval Forecast
  - Planned Revenue at Risk = (1 - FR) x Resale Price x Interval Forecast [B]release_notes/release_13_1_0_5/rn_enhancements_io.html
  - Resale Price, Resale Value
  - Stocking Policy container "Sales, Inventory and Operations Planning"

======================================================================
11. APPROVAL WORKFLOW (SKU SUMMARY / LOCATION SUMMARY), EXCEPTIONS, OVERRIDE SECURITY
======================================================================
- Production Status per scenario SKU: Approved (manual), Disapproved, Pending, Auto Approved (set by calculation), None, Production, Promoted To Production. Editable in SKU Levels (Inventory Collaboration), SKU Detail Report, and the SKU Summary tab of Stocking Policy [B]glossary/production_status.html
- Pending SKU "will not be made production until they are approved" [B]glossary/pending_sku.html
- Approved SKUs "free to be made production according to the production holds workflow" [B]glossary/approved_skus.html
- Rejected SKU (formerly "Held SKUs") [B]glossary/rejected_sku.html, [B]release_notes/release_13_0_0_0/rn_enhancements_io_15.html
- Pending / Approved / Rejected Overrides counts [B]glossary/pending_overrides.html
- Approve paths:
  - Scenario level: Approve All Pending SKU, Approve All Overrides (Scenarios page)
  - Scenario Summary: Approve/Reject Pending
  - Location Summary: Approve/Reject Pending
  - Location Detail Report: Approve / Disapprove / Approve All Overrides for Selected Location
  - SKU Summary: Approve/Disapprove / All Pending
  - Part Supply Chain, Service Group Results, Segment Summary
  (sources in section 10)
- Rights renamed:
  - "MEO Approve Holds" became "MEO Approve All Pending SKU"
  - Location/Part/Scenario/Service Group Hold became "MEO Approve/Reject SKU by Location/Part/Scenario/Service Group" (Action Setup Rights)
  [B]release_notes/release_13_0_0_0/rn_enhancements_io_15.html
- Holding thresholds via Exception Criteria. Production Approval Type = Exception Criteria "evaluated using holding thresholds" [B]glossary/production_approval_type.html
  - Exception Criteria fields [B]inv_opt/inv_opt_pid/pid_exception_criteria_page.html:
    - Compare To: Production or None
    - Compare Value / Compare To Value / Operation (Manual SQL)
    - Exception Description, Resolution Description
    - Include in Optimization Set: On By Default / Manual Selection / Not Allowed
    - Level: Notification / Alert / Hold / Critical
    - SQL Method: SQL Builder / Manual SQL (needs the right "Manual SQL Entry on Exception Criteria")
    - View Type: PART / LOCATION / SCENARIO / SERVICE GROUP / SKU
    - Optional segment assignment [B]inv_opt/inv_opt_smart_help/sh_exception_criteria_page_create_edit.html
  - Evaluate Exception Criteria process re-checks against updated production [B]glossary/scenario_processes.html
- Override Security (recommend/approve/delete). Source: [B]inv_opt/inv_opt_pid/pid_override_security_page.html
  - Role Name, Description.
  - Allow Recommend.
  - Allow Review ("approve or reject overrides that were recommended").
  - Allow Deletion of overrides set by other planners.
  - Assigned to planners by segment on Override Assignment [B]inv_opt/inv_opt_smart_help/sh_override_security_page.html (worked examples: recommend at Central Parts, view elsewhere)
  - Table IPCS_OVR_USER_LOCATIONS for performance [B]release_notes/release_13_0_0_0/rn_enhancements_io_20.html
- Audit Trail covers Exception Criteria, Optimization Sets, Service Group Parameters, SKU Overrides (incl. approvals/rejections) and Time Phased Service Groups. AUDIT_TRAIL_KEEP_DAYS (90) with Gateway Clean-up [B]release_notes/release_13_0_0_0/rn_enhancements_io_4.html
- Inventory Studio (lighter-weight approval UI for e.g. dealership parts managers) [B]parts/parts_smart_help/sh_inventory_studio_page.html:
  - Tabs: Purchase Recommendations, Excess Return Recommendations, Transfer Recommendations, Stocking Policy Recommendations ("scheduled… future release" / "under construction" [B]parts/parts_smart_help/sh_invst_stocking_policy_recommendations_tab.html), Requests Received, Requests Sent, Order Status, Parts (Part Catalog, Part Locator)
  - Each recommendation tab has Pending/Approved/Rejected/All subtabs and Approve / Reject / Override Quantity actions. Approval Status becomes "Manually Approved" or "Rejected" [B]parts/parts_smart_help/sh_invst_transfer_recommendations_tab.html
  - Settings: INVENTORY_STUDIO_MAP_DISPLAY (Bing Maps), FUTURE11. Balancing Parameters define which locations Part Locator can search. Rights: View / Approve & Reject / Override per tab [B]parts/parts_smart_help/sh_inventory_studio_page_2.html, [B]core/core_smart_help/sh_urs_page_inventory_studio_tab.html, [B]release_notes/release_13_1_0_0/rn_enhancements_sp_16.html

======================================================================
12. WHAT-IF MODELING
======================================================================
- Purpose: "recognize changes to stocking plans and budget the impact from events and changing assumptions" [B]glossary/what_if_modeling.html
- Introduced as Beta in 13.0.1.0; "users can change many data items such as lead times, repair wash rates, part costs" [B]release_notes/new_in_13_0_1_0.html
- What-If Model page containers: What-If Model, Details, Assigned Segments, Assigned SKUs. Right "What-If Model" (View / View and Modify) [B]release_notes/release_13_1_0_0/rn_enhancements_io_3.html
- Carbon Tax Rate can be a What-If Detail field [B]release_notes/release_13_1_0_0/rn_enhancements_io_4.html
- Scenario What-If Model selection: changing it flags the scenario Needs Recalculation. Fields "What-If SKU" (count) and "Modified by What-If" (Y/N) [B]glossary/what_if_model.html, [B]glossary/what_if_sku.html
- Example workflow: three copies of a baseline with +5% forecast (current inventory / optimized / current recommended). Compare on Scenario Summary, Scenario Budget Summary and Service Group Budget Summary [B]glossary/what_if_modeling_2.html

======================================================================
13. SUSTAINABILITY / CARBON
======================================================================
- Carbon focus areas: embodied carbon ("Buy Less Through Optimized Inventory", "Repair and Reuse More", circular supply chain, useful life), emissions (disposal, transportation), reliability. Carbon Tax: "Support optimizing to minimize the sum of carbon tax and ROP value while satisfying the Service Group targets" [B]glossary/sustainability.html
- Inputs (IO Planning Parameters Sustainability tab, Parts, SKU): Embodied Carbon Per New Buy, Embodied Carbon Per Repair, Transportation Carbon Per Expedited Order, Per Repair, Per Standard Order [B]inv_opt/inv_opt_pid/pid_inv_opt_planning_parameters_create_edit_fields.html
- Outputs [B]inv_opt/inv_opt_pid/pid_sustainability_container.html:
  - Embodied Carbon (New Buy) = per-new-buy x New Buy
  - Embodied Carbon (Repair) = per-repair x Repair Order Qty
  - Transportation Carbon (Standard / Repair / Expedited)
  - Supply Shipment Regular / Expedited and (Lines) = qty / COS
  - Carbon Tax (Embodied) = (EC NewBuy + EC Repair) x rate
  - Carbon Tax (Transportation) = sum of transport carbon x rate
  - Carbon Tax (Total)
- Carbon Tax Rate waterfall: Location, then Region, then CARBON_TAX_RATE (default 0). Reference Carbon Tax Rate/Currency on Locations and Regions (same URL; [B]release_notes/release_13_1_0_0/rn_enhancements_io_4.html)
- CARBON_MEASURE_TYPE (default "kg of CO2e") labels the headings. IO_CALCULATE_SUSTAINABILITY (default false) shows the Carbon Footprint row on the budget summaries [B]release_notes/release_13_0_1_3/rn_enhancements_io_3.html
- Objective Cost option "Carbon Tax (Embodied) + Part Cost" (section 3).

======================================================================
14. NETWORK OPTIMIZATION (NETWORK DESIGN)
======================================================================
- Purpose: SLAs per product and install site; "a strategic process, not a tactical one… run on an infrequent basis (monthly or quarterly)" [B]glossary/network_optimization.html
  - Finds "the least expensive network of Field Service Locations (FSLs) needed to satisfy the SLA".
  - Recommends which locations to open or close and which support which contracts.
  - Minimizes the number of open locations, then assigns coverage to the closest open location.
  - "only considers locations that are currently in the network… will select from a pre-populated candidate list" (it does not use centroids).
  - "Transportation costs are ignored".
- Workflow [B]glossary/network_optimization_2.html:
  1) Set the Network Optimization fields on Locations
  2) Include in Network Optimization = Yes on Install Base
  3) Create Rules
  4) Optional imports (locations, install sites)
  5) Process the scenario
  6) Optional overrides of active/inactive
  7) Review the map
- Scenario fields: Copy Scenario Values, Scenario Name, Description, Staging Time (hours), Miles Per Hour ("as the crow flies"), Number of Closest Locations to Display, Budget, Coverage Percentage (keeps assigning until reached). Location Criteria: Import Location Master, Region, Location Type. Install Base Criteria: Import Install Base, Product, Product Group, Date, Contract Type, Import Stocking Coverages [B]parts/parts_pid/pid_new_edit_network_optimization_scenario_page.html
- Location tab fields include: # of Install Base Recommended, Critical, Include in Network Optimization, Is Geolocated, Geo Quality of Match, Location Fixed/Startup/Shutdown Cost, Location Type, Locked on Network Optimization, Network Optimization Priority (1 = highest), Parent Location, Third Party, Procurement/Repair Allowed, Put Away Length/Std Dev [B]parts/parts_pid/pid_network_optimization_scenario_page_locations_tab.html
- Coverage tab: Closest / Current / Recommended / Override Location with Distance and Est. Response Time, Committed Response Time (SLA), Current Covered, Recommended Covered, Override Covered, Rule [B]parts/parts_pid/pid_network_optimization_scenario_page_coverage_Tab.html
- Rules: override install base coverage by Location, Scenario, Contract Type, Product/Type, Install Site, Region/City/State/Country/Postal Code [B]parts/parts_pid/pid_new_edit_network_optimization_rule_page.html, [B]release_notes/release_13_0_1_1/rn_enhancements_io_2.html
- Cross-border: Country Borders "Hours to Cross". NOPT_CROSS_BORDERS (default true: response = drive time + Hours to Cross; false: same country only) [B]release_notes/release_13_0_1_2/rn_enhancements_io_3.html, [B]glossary/global_settings_io.html
- Map tab: Display By Compliance or Response Time; Range Analysis in 2/4/6/8/10 hour rings; filters [B]parts/parts_smart_help/sh_network_optimization_scenario_page_map_tab.html
- Related Additional Module: New Business Scenarios (Profit Analyzer) [B]parts/parts_topics/creating_modifying_new_business_analysis_scenarios.html

======================================================================
15. MODELING MODULE: ESCM, SIMULATIONS, AUTOMATED DATASET COMPARISON
======================================================================
Enhanced Supply Chain Modeling (ESCM)
- "modeling larger sets of data, beyond the scenario-based modeling capabilities of… Inventory Optimization and Causal Forecasting… without impacting the current production data" [B]glossary/enhanced_supply_chain_modeling.html
- Concepts:
  - Sandbox = the server
  - Snapshot = DB backup at a point in time (of production or of a modeling instance)
  - Modeling Instance = snapshot plus sandbox
- Settings [B]glossary/enhanced_supply_chain_modeling_2.html:
  - ENABLE_ESCM, ESCM_MAX_SNAPSHOTS, ESCM_MAX_SANDBOXES
  - ESCM_CREATE_MI_AP_DEPENDENCY, ESCM_CREATE_SNAPSHOT_AP_DEPENDENCY
  - MANUAL_SYSTEM_DATE (sandbox gets the snapshot date if production is null)
  - Rights: Snapshot Management, Sandbox Pool, Modeling Instances
- Workflow: Sandbox Pool, then Snapshot Management, then Modeling Instances (create/run, update settings, run simulation), sign in to review, then Return Sandbox to Pool [B]glossary/enhanced_supply_chain_modeling_3.html
- Page notes: [B]core/core_smart_help/sh_sandbox_pool.html ("Production sandbox is created by default", not counted); [B]core/core_smart_help/sh_snapshot_management.html; [B]core/core_smart_help/sh_modeling_instances.html (Available Sandboxes x of y; Run gives Create Modeling Instance / Return Sandbox to Pool)

History Based Simulator (Modeling > Simulations)
- "historical (Replay) Simulation by turning the clock back in time… complete interconnected supply chain from a point in history"
- Uses: service/budget metrics, config change impact, root cause, de-risking, generating PAI history
- Reports: Service and Inventory Monthly Average Summary, Fill Rate by Part, Fill Rate by SKU, SKU Simulation Report
- Source: [B]core/core_smart_help/sh_history_based_simulator.html
- Fields [B]core/core_pid/pid_history_based_simulator_add_edit.html:
  - Start/End Date
  - Prepare Start Data (No reuses the snapshot; tables IPCS_SIM_*)
  - Enable Inventory Reconciliation
  - Status: Blank / Waiting / Preparing / Running / Paused / Paused (Failed) / Failed / Preparing Results / Aborted / Completed
  - Current Simulation Date, Pause after Every Simulation Day, Pause on Date, Look Ahead Days for Sales Orders
  - Causal Forecast Scenario, Inventory Optimization Scenario, Segment
  - Configure Processes: Best Fit … Inventory Optimization … Synchronize Database, with Frequency Daily/Weekly/Monthly/Quarterly/Start Only/Never, Pause After Running, Record History, Threads. Tip: start/end on a weekend.
  - Review Type / Exception history tabs
  - Start Data: Initialize Stock Amount (Use Current Levels sets OHG = Stock Max), Create Initial Order (Use Current EOQ), Create Demand Over Period (Auto / Demand Detail / Demand History / None), Create Sales Return Over Period
- Global settings: ENABLE_HISTORICAL_SIMULATION, SIM_CLEANUP_USING_SEGMENT, SIM_MAX_SEGMENT_SIZE, SIM_UPDATE_ORDER_PLAN_HIST. Right: History Based Simulator (Modeling tab) [B]core/core_smart_help/sh_history_based_simulator_2.html
- SKU Simulation Report: daily SKU results, Graph and Data tabs [B]core/core_smart_help/sh_sku_simulation_report.html

Automated Dataset Comparison
- Compares backup vs current. Benefits: upgrade testing, tuning, feature impact. Base stored via an AutoPilot process. Needs WebUI property servigistics.intellicus.automated.comparison.categoryid = Modeling [B]core/core_topics/module_modeling_automated_dataset_comparison.html
- Pages: Forecast Comparison Summary (SKU Stream, Forecast Value, Bias, Outliers, Repair Forecast, delta classes Increase/Decrease/No Change/SKU Added, Top 10 by delta) [B]core/core_smart_help/sh_forecast_comparison_summary.html; Order Plan Comparison Summary (Full Horizon / Today / 13 Week, by Order Type, Top 10 parts) [B]core/core_smart_help/sh_order_plan_comparison_summary.html
- No IO-specific comparison dashboard was found in the crawl.

======================================================================
16. OTHER IO GLOBAL SETTINGS NOT COVERED ABOVE
======================================================================
Source: [B]glossary/global_settings_io.html unless noted.
- AUDIT_TRAIL_KEEP_DAYS (90).
- EXCEL_EXPORT_ESCAPE_CHARACTER (=).
- SPACE_CONSTRAINT_TYPE (Cubic Meter).
- OPT_MIN_UNIT_COST: excludes SKUs priced below it [B]glossary/excluded_pairs.html
- FISCAL_YR_STARTING_MONTH [B]glossary/fiscal_optimization_2.html
- ENABLE_FORECAST_APPROVAL controls the Forecast Type options [B]inv_opt/inv_opt_pid/pid_scenarios_page_create_and_edit_fields.html
- Full list of IO_* tokens found anywhere in the corpus: IO_CALC_RESUPPLY_CUST_ORDER_SIZE, IO_CALC_CUST_ORDER_SIZE (old), IO_EVALUATE_EMERGENCY_BACKUP_VALUES, IO_EMERGENCY_NETWORK_SOLVES_COMMON_GROUPS, IO_FULL_COMPARE_MODE, IO_NEW_BUY_PROC_EFFOQ_THRESHOLD, IO_OVERRIDE_CLEANUP_EXPIRED_RECORDS_DAYS, IO_PROD_SKU_TRACKING, IO_PRODUCTION_SCENARIO_SKU_SQL_METHOD, IO_TPROP_ROUND_SS, IO_COV_THRESHOLD_NORMAL_TO_NEGBINOM, IO_CALCULATE_SUSTAINABILITY, IO_HIGHEST_WAIT_TIME_CONF, IO_CREATE_PROD_SUMMARY_IN_STANDALONE_JOB_ONLY, IO_FISCAL_YR_STARTING_MONTH, IO_EXCLUDE_REPAIRS_IN_EOQ_DAYS_OF_SUPPLY, IO_EVALUATE_PRODUCTION_PART_SUMMARY, IO_EVALUATE_OVERRIDE_COUNT, IO_APPLY_OVERRIDE_INCLUDE_POST_OPT_ONLY, IO_ENABLE_REPAIR_OPTIMIZATION. (IO_PAI_ML_* are Intellicus report names, not settings [B]admin/admin_export_data_3.html)
- Related MEO_*: MEO_OVERRIDE_MAX_QTY, MEO_OVERRIDE_CODE_REQUIRED, MEO_OVERRIDE_DEFAULT_PERIODS_TO_EXPIRE, MEO_SKU_OVERRIDE_TYPE, MEO_REPAIR_TYPE.
- Related others: INVENTORY_OPTIMIZATION_MODE, ALLOW_NEGATIVE_SAFETY_STOCK, BUY_LIST_ROUNDING_RULE, CARBON_*, CUST_ORDER_SIZE_*, SL_*, LEVELS_DAYS_CONSTANT, MAXIMUM_ADDITIONAL_SCENARIOS_DISPLAY_COUNT, NOPT_CROSS_BORDERS, DEALER_APP_RESTRICTIONS, ENABLE_LOCATION_HIERARCHY, ENABLE_NRTS, ESCM_*, SIM_*, SL_ROTABLE_ALLOCATION_BY_SS, INVENTORY_STUDIO_MAP_DISPLAY.
- Troubleshooting workflow "A SKU Is Stocking Less Than Expected": check Exclude MEO and Is Optimized, then the forecast in Performance Summary, then max/fixed constraints and overrides [B]process/workflow_sku_stocking_less_than_expected.html