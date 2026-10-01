# Servigistics 13.x — Inventory Optimization (IO/MEO) gap notes

Prefix `HC/` = `https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/`.
Excludes items already known (distribution switching, Type I/II MOE, global_settings_io list, override priority, ASL strategy, B4B, service metric, parent membership, fill-rate methods, Parts Planning Parameters DA/DS/pipelines/EOQ/wash/rotable).
Anything not stated verbatim in the help is marked **UNVERIFIED**.

---

## 1. IO Planning Parameters (Create/Edit)

Source for the whole section: HC/inv_opt/inv_opt_pid/pid_inv_opt_planning_parameters_create_edit_fields.html (+ `_fields.html` for list columns).
Tabs: Details · Reorder Quantity · Optimization Costs · Pipeline · Custom · Sustainability · Segments. The list page also has **Priority Sequence** (the order in which schemes are evaluated). The help gives **no default values** on this page. Default-looking values appear only as *sample* audit entries (see end of table).

| Name | Meaning | Default/range | Source |
|---|---|---|---|
| Scheme Name / Description / Comments | Identity of the scheme | — | create_edit_fields |
| Max EOQ (slices) / Min EOQ (slices) | Pre-optimization max/min on EOQ, expressed in slices of forecast | Conflicts: min of maxes / max of mins wins | same |
| Set EOQ (slices) | Fixed EOQ as slices of forecast, e.g. 20/slice × 1.25 = 25 units. Overrides the calculated EOQ and therefore Stock Max. Has End Date and Note | — | same |
| Set EOQ (Quantity) | Fixed EOQ in units. Has End Date and Note | — | same |
| Max REOQ (slices), Set REOQ (slices) | Same idea for the Repair EOQ. Set REOQ has End Date and Note | — | same |
| Reference Procurement / Repair / Replenishment Order Cost + Currency | Order cost in the reference currency. "Process Changes" converts it to local currency | — | same |
| Procurement / Repair / Replenishment Order Cost | Internal overhead cost per order (repair = cost to process one repair order). A higher value gives a higher EOQ, which gives a higher Stock Max | — | same |
| Carrying Cost (%) | Annual holding cost as a % of part value (also called holding cost). A higher value gives a lower EOQ and a lower Stock Max | "normally between 25% and 35% per year" (guidance, not a default) | same |
| Reference Stockout Unit Cost (Fill Rate / Wait Time) + Currency | Stockout costs in the reference currency | Set to 1 by the system when the SG has Minimize Stockout Cost on | same |
| Stockout Unit Cost (Fill Rate) | Cost per unsatisfied demand. Precedence: SKU > Part > IO Planning Parameter | 1 when Minimize Stockout Cost is on | same |
| Stockout Unit Cost (Wait Time) | Cost of customer waiting. Precedence: SKU > Part > Service Group Parameter > IO Planning Parameter | 1 when Minimize Stockout Cost is on | same |
| Procurement/Repair/Replenishment/Return Average + Std Dev | Pipeline lead times in days. "Procurement Average" text also covers the wait for parent/component shortages | days | same |
| Return Wash Rate | % of removed parts that never reach repair. Returns = Forecast × (1 − Return Wash Rate) | % | same |
| Repair Wash Rate | % of units in repair that cannot be repaired (10% → 11 bad units repaired to get 10 good) | % | same |
| NFF Rate | % of returns that need no repair and go straight to good stock | % | same |
| Procurement / Repair / Replenishment Order Period | Minimum number of days between orders. Effectively adds to the pipeline length | 0 = no order period | same |
| Custom Planning 1–5 | Values for custom code only | — | same |
| Embodied Carbon per New Buy / per Repair; Transportation Carbon per Expedited / Standard Order / per Repair | kg CO2e factors used for sustainability | — | same |
| Segments (Available/Selected) | The segments this scheme governs | — | same |

Sample audit values (these are examples, **UNVERIFIED** as defaults): DA 100, DS 95, SOrderCost/SRepairOrderCost/SReplOrderCost 100, SCarryingCost 15, ScrapRate 10, ReturnWashRate 10, DmdRateDaysConstant 0, DmdRateDaysLTMultiplier 0, RotableBankDS 50, DaysConsidered 365, OvrSL −1 — HC/glossary/audit_trail_fields_planning_parameters.html

Related IO containers:
- **Reorder Quantity Inputs** adds Lot Size, Minimum Order Quantity, Sales Size, and Fixed Order / Packaging / Pallet Size per procurement, repair and replenishment. It also defines Repair Cost (network-wide repair need cost, e.g. 5 units × $10 + 5 units × $100 = $550 charged to the child). HC/inv_opt/inv_opt_pid/pid_reorder_quantity_inputs_container.html
- **Lead Time Inputs** adds Composite Lead Time and its variance, Echelon, Parent Location, NRTS, and Generate Procurement/Repair/Replenishment Orders flags (these come from Parts). HC/inv_opt/inv_opt_pid/pid_lead_time_inputs_container.html
- **Stockout Costs**:
  - Stockout Cost (FR) = (1 − Fill Rate) × Interval Customer Forecast × Stockout Unit Cost (FR)
  - Stockout Cost (WT) = (EBO / Total Daily Forecast) × Interval Customer Forecast × Stockout Unit Cost (WT)
  - Source: HC/inv_opt/inv_opt_pid/pid_stockout_costs_container.html

## 2. Scenario Create/Edit

Source: HC/inv_opt/inv_opt_pid/pid_scenarios_page_create_and_edit_fields.html. Sections: General · Optimization Scope · Stocking Strategy · Look Ahead Days for Demand Rate.

| Name | Meaning | Default/range | Source |
|---|---|---|---|
| Name | Unique; a single quote is not allowed | — | create_and_edit |
| Production Approval Type | How scenario SKUs are approved | Approve All / Pending All / Exception Criteria. Exception Criteria forces "Run for all periods" | same |
| Complete Before Summarization | Splits the calculation into two steps: Calculate Stock Levels, then background Calculate Summary Values. SKU-level pages, Make Production and Generate Order Plan become usable after step 1 | checkbox | same |
| Exception Criteria | Run for all periods / first period / Do not run | **Default: Run for all periods** | same |
| Category, Reporting Hierarchy, Note | Labels | — | same |
| Generate Prioritized Buy List | Produces the PBL (see §5) | checkbox | same |
| Summarize Excluded SKUs | Includes excluded SKUs (outside segment coverage, or price < OPT_MIN_UNIT_COST) in the summary | checkbox | same |
| Optimization Set | The set of Service Groups used | — | same |
| Fiscal Optimization | When on, enables Number of Fiscal Years and Fiscal Interval and disables Horizon/Interval | checkbox | same |
| Horizon (periods) | Number of slices to calculate (48 = 4 yrs monthly). Slice 0 = EOP date | **no default given** | same |
| Interval (periods) | How often to calculate (1 = monthly, 3 = quarterly, 12 = yearly) | **no default given** | same |
| Fiscal Interval | Period / Quarter / Year | **Default Quarter** when Fiscal Optimization is on | same |
| What-If Model | Optional model applied during the calculation. Changing it flags the scenario for recalculation | none | same |
| Objective Benefit Criteria | B4B numerator: Fill Rate Increment or EBO Reduction. For Minimize-Stockout-Cost SGs the benefit is the stockout-cost reduction | — | same |
| Objective Cost Criteria | B4B denominator: Part Cost **(default)**, Optimization Cost (SKU > Part > Part Cost fallback), or Carbon Tax (Embodied) + Part Cost = EmbodiedCarbonPerNewBuy × CarbonTaxRate + Part Cost. New Buy Cost is always the objective cost when a New Buy Budget is enforced. Repair + New Buy cost is the objective cost in the Availability-with-Repair-Optimization algorithm | Part Cost | same |
| Mean Days to Remove and Replace | MDRR in days (4 decimals stored, 3 shown). Availability input, **UNVERIFIED** role | — | same |
| Respect Override | Apply SKU Overrides and post-optimization SG SKU Constraints. **Must be Yes to Make Production** | Y/N | same + HC/glossary/scenario_processes.html |
| Use Line Fill Rate | Line fill rate instead of unit fill rate. Levels become multiples of Customer Order Size (COS avg default 1, SD default 0, Line FR safety factor default 0). Not applied in availability models | off (COS = 1) | same |
| Service Groups Include Non Stockable Items | Includes non-ASL (stockmax = 0) demand in the SG optimization. The target may then be unreachable | checkbox | same |
| Churn Control Method | None / Use Inventory Balance with Reference Scenario (latest non-churn scenario with the same attributes) / Use Inventory Balance (current balance first, condemned forecast burns it down) / Respect Production (ROP bands vs production) / Respect Previous Period. Disabled when mode = SIO | — | same; HC/glossary/churn_control_method.html |
| Run Forecast Pooling | Include the pooling phase, using Forecast Pooling Parameters | Y/N | same |
| Forecast Type | Production / Recommended (only if ENABLE_FORECAST_APPROVAL) / Causal Forecast Scenario | — | same |
| Use External Values + External Scenario | None / Use Inventory Position (Current Inventory Parameters) / Use External (External Scenario page) | None | same |
| Look Ahead Days: Constants (Days), Lead Time Multiplier | Days for the demand rate = Constant + Multiplier × SKU Resupply Lead Time Days. Feeds the std dev in the levels calculation | — | same; HC/glossary/demand_rate_days_constant.html |

### Churn control parameter pages
- **Respect Production Parameters** — HC/inv_opt/inv_opt_pid/pid_respectprod_parameters_page.html
  - Fields: High/Low Control Limit % (acceptable band above/below the production ROP), Demand High/Low Threshold %, Is Enabled.
  - If current LTD > DemandHigh% × production LTD, the high limit is not applied. If current LTD < DemandLow% × production LTD, the low limit is not applied.
  - A control limit > 100% lets ROP go −1→0 or 0→1 (source: create_and_edit).
- **IO Balancing Parameters** — HC/inv_opt/inv_opt_pid/pid_io_balancing_parameters_page.html
  - Fields: Reference Transshipment Cost + currency, Transportation Cost (waterfall across the SKU / lane / vendor lead time pages), Is Enabled.
  - Churn Transportation Cost = the transshipment unit cost of this parameter (HC/glossary/churn_transportation_cost.html).
- **Current Inventory Parameters** — HC/inv_opt/inv_opt_pid/pid_current_inventory_parameters_page.html
  - One multiplier each for OnhandNew, OnhandFixed, Onorder, Backorder, Allocated, Inrepair, OnhandBad and Inreturn. Used by "Use Inventory Position".
- **Churn Controlled Minimum** = inventory granted by churn control, enforced as a minimum Stock Max (HC/glossary/churn_controlled_minimum.html).

### Scenario lifecycle
Source: HC/glossary/scenario_processes.html, HC/glossary/scenario_workflow_status.html, HC/glossary/in_collaboration.html.
- **Processes:**
  - Calculate: deletes prior results. Copy the scenario first to keep them.
  - Evaluate Exception Criteria: runs on Complete or Promoted.
  - Make Production: runs on Complete or Promoted, needs Respect Override = Yes, and uploads only SKUs that are not Pending or Disapproved. More than one Production scenario is allowed. The previous production scenario goes back to Complete. It deletes future order-plan net forecast stock level records only for uploaded SKU-periods (quirk documented with a 5/7/9 example).
  - Clear Optimized Production Values.
  - Apply Overrides: applies all overrides as post-optimization. With IO_APPLY_OVERRIDE_INCLUDE_POST_OPT_ONLY = true, only post-opt overrides are applied.
  - Approve All Pending SKU.
  - Generate Summary Data for Production: only when IO_CREATE_PROD_SUMMARY_IN_STANDALONE_JOB_ONLY = true (default false).
  - Generate External (Production) Reporting Data: legacy tables.
  - Start Collaboration: sets In Collaboration = Yes and makes the scenario visible on Inventory Collaboration. Can also run per segment.
  - Delete.
- **Workflow Status** (only when Complete Before Summarization is on): Model Incomplete → Making Stock Level Changes → Candidate (external scenario, or Respect Override on) / Non-Candidate → Making Production → Promoted → Production.
- **Production scenario expiry:** no scenario-expiry setting was found. The expiry settings that do exist are for overrides:
  - MEO_OVERRIDE_DEFAULT_PERIODS_TO_EXPIRE (default 0 = no End Date).
  - IO_OVERRIDE_CLEANUP_EXPIRED_RECORDS_DAYS (default 180; purged by Synchronize Database).
  - Source: HC/glossary/global_settings_io.html.
- **Optimization Set** tabs:
  - Service Groups: none selected = all.
  - Exception Criteria: none selected = none.
  - Segments: part/location segments that define the modelled SKUs.
  - Summary Segments: none selected = all.
  - Process Group.
  - Source: HC/inv_opt/inv_opt_pid/pid_optimization_set_create_edit.html
- **External Scenario:**
  - Type: ROP / Safety Stock / Stock Maximum / Fill Rate.
  - Unspecified SKU: None or Use Production Values.
  - Host ID.
  - Source: HC/inv_opt/inv_opt_pid/pid_external_scenario_page.html
- **Exception Criteria:**
  - Compare To: Production or None.
  - Include in Optimization Set: On By Default / Manual Selection / Not Allowed.
  - Level: Notification / Alert / Hold.
  - Source: HC/inv_opt/inv_opt_pid/pid_exception_criteria_page.html

## 3. Service Group Parameters (Create/Edit) + Effective container

Source: HC/inv_opt/inv_opt_pid/pid_service_group_parameters_create_edit.html. Groups: Details, Service Targets, Location Targets, Contract Targets, Capacity (Space) Constraints, Budget Constraints, SKU Constraints.

| Name | Meaning | Default/range | Source |
|---|---|---|---|
| Location Hierarchy | Hierarchy scope. Only for the Fill Rate and Availability & Fill Rate metrics | — | create_edit |
| Emergency Backup Location Hierarchy | Only for the Fill Rate with Emergency Backup metric | — | same |
| Currency, Category, Comments | — | — | same |
| Minimize Stockout Cost | Invest to reduce stockout cost. Enables the stockout unit cost fields (default 1) | checkbox | same |
| Customer Network Fill Rate | Minimum overall network fill rate. Not editable in MIO | % | same |
| Customer Location Fill Rate (Default) | Location target weighted by external demand only | % | same |
| Total Location Fill Rate (Default) | Weighted by external + internal demand | % | same |
| Primary Emergency Fill Rate (Default) | Filled at the customer-facing location + first-level emergency location | % | same |
| Secondary Emergency Fill Rate (Default) | Adds demand filled at the backup of the first-level emergency location | % | same |
| Network Wait Time (days) / Location Wait Time (days) (Default) | Expected wait for equipment on failure, aggregated over the network or per location | days | same |
| Network Availability / Location Availability (Default) | % of time equipment is up. **MIME mode only** | % | same |
| Contract Wait Time (Default) / Contract Availability (Default) | Per-contract defaults | — | same |
| Location Targets (per location) | Customer FR, Total FR, Primary/Secondary Emergency FR, Average Wait Time. The Service Targets tab shows Count (e.g. "2 of 49") and Range (e.g. 15%–88%) of these overrides | — | same |
| Contract Targets (per contract) | Min Contract Availability, Max Contract Wait Time | — | same |
| Default Max Space / Max Space (by location) | Space cap. Space required = Stock Max × <SPACE_CONSTRAINT_TYPE> per Unit (from Parts). The tab label comes from SPACE_CONSTRAINT_TYPE | GS default "Cubic Meter" | same; HC/glossary/global_settings_io.html |
| Stock Maximum Budget (+Reference) | Cap on Σ(Stock Max × price) | currency | same; HC/glossary/stock_maximum_budget.html |
| New Buy Budget Scope | Interval (same cap every period) or Fiscal Year (needs Fiscal Optimization). Does not affect the Stock Max budget | — | same; HC/glossary/new_buy_budget_scope.html |
| New Buy Budget (+Reference) | Cap on Σ(new buy qty × price) | — | same |
| Repair Budget (+Reference) | Repair cost limit per optimization interval. Needs repair optimization (§4). Order Plan ignores it | — | same; HC/glossary/repair_optimization.html |
| SKU Constraints | Min/Max Fill Rate; Min/Max ROP and ROP (days); Min/Max Safety Stock and SS (days); Min/Max Stock Maximum; Maximum Wait Time; Wait Time Confidence Level. Each is pre- or post-optimization. Max of the mins / min of the maxes wins. Values above MEO_OVERRIDE_MAX_QTY (default 0 = no check) ask for confirmation | — | same |
| Negative SS constraint | Allowed only if ALLOW_NEGATIVE_SAFETY_STOCK (default false). It drives ROP so that ROP − round(onOrderMean) = the value. ROP stays floored at −1 | — | same |
| Wait Time Confidence Level | Probability that the true wait time is below the calculated wait time (large samples). A user SKU constraint | % | HC/glossary/wait_time_confidence_level.html |

Other notes:
- Service targets cannot be edited when mode = SIO. Budget constraints cannot be edited when mode = SIO.
- The service metric cannot be changed after the first save.
- **Time-Phased Service Groups:**
  - The same Service Targets, Budget and SKU Constraints groups, plus Begin Period (date only) and Comments.
  - The Effective Service Group Parameter container shows which record applied, with its Begin Period.
  - Emergency-backup SGs can also be time-phased.
  - Sources: HC/inv_opt/inv_opt_pid/pid_time_phased_service_groups_create_edit.html, HC/inv_opt/inv_opt_pid/pid_effective_service_group_parameter_container.html
- **Criticality Multiplier** (on the SKU) influences B4B selection. In the availability model it also changes the availability calculation.
  - Weighted EBO = EBO × Customer Period Forecast × Criticality Multiplier / Total Period Forecast.
  - Sources: HC/glossary/criticality_multiplier.html, HC/glossary/weighted_ebo.html
- **Include non-stock items:** the scenario flag "Service Groups Include Non Stockable Items" (see §2).

## 4. Multi-echelon mechanics

| Concept | Fact | Source |
|---|---|---|
| Effective Lead Time | Expected days to receive an order via replenishment, repair, procurement or a mix, **including the wait from parent and component shortages** | HC/glossary/effective_lead_time.html |
| Pipeline Forecast / Variance | Demand over the effective lead time, including parent wait time / its squared deviation | HC/glossary/pipeline_forecast.html, pipeline_forecast_variance.html |
| EBO | Average units backordered at any time in the interval. A function of pipeline forecast, variance and stock level. **Total EBO = Wait Time × Total Daily Forecast** | HC/glossary/ebo.html |
| Backorder from Parent Location | Expected backorder caused by a shortage at the replenishment location | HC/glossary/backorder_from_parent_location.html |
| Backorder Variance from Parent | Its variance, "a global setting defined during implementation" | HC/glossary/backorder_variance_from_parent_location.html |
| Backorder from Components | Expected backorder caused by component shortages (indenture) | HC/glossary/backorder_from_components.html |
| Composite Lead Time (+Variance) | Average days to obtain the part | HC/glossary/composite_lead_time.html |
| MEO_REPAIR_TYPE | 1 = Serial (not recommended; Levels back-compatibility). 2 = Aggregate: repair/return and procure/replenish lead times weighted by share of use; wash rates count, demand does not; default for existing customers. 3 = Demand Weighted (Return/Repair Wash, NRTS, NFF, hierarchy); **default for new installs** and recommended on upgrade | HC/release_notes/release_13_0_1_0/rn_enhancements_io_2.html |
| Echelon | Hierarchy level of the supply chain | HC/glossary/echelon.html |
| Indenture | Assembly level. First indenture = LRU, lower levels = SRU | HC/glossary/indenture.html |
| MIME | INVENTORY_OPTIMIZATION_MODE values: SIO / MIO / MEO (**default MEO**) / MIME. Availability targets exist only under MIME | HC/glossary/global_settings_io.html |
| Weighted Equipment EBO | Backorder weighted by daily causal forecast / total forecast, contract population / total population, and criticality | HC/glossary/weighted_equipment_ebo.html |
| Availability formula | **Not published.** The help says only "expected % of time equipment is operational". MDRR and criticality feed into it (**UNVERIFIED**; usual A = MTBF/(MTBF+MDT) form not confirmed) | HC/glossary/availability.html |
| NRTS | % that cannot be repaired at this location. ENABLE_NRTS (default true) models local condemnations at return (Return Wash) and after repair (Repair Wash). When false, one blended Condemnation Rate is used at the root only | HC/glossary/not_repairable_this_station_2.html, condemnation_rate.html |
| Local Condemned Period Forecast | CPF×RWR + CPF×(1−RWR)(1−NRTS)(1−NFF)×RepWR + RepairableFromBelow×(1−NRTS)[×(1−NFF) if APPLY_NFF_TO_INT_RETURN_FCST]×RepWR | HC/glossary/local_condemned_period_forecast.html |
| Roll Up Demand As Repairable | Y = the demand rolls to the parent and is inducted into repair there | HC/glossary/roll_up_demand_as_repairable.html |
| Repair Optimization | Chooses a mix of good stock, repairing repairables and new buy. An extension of churn control. Enable with IO_ENABLE_REPAIR_OPTIMIZATION = true (availability model only; period repair budget) + Churn = Use Inventory Balance (or with Reference) + SG Repair Budget. Is Repair Optimizable = N means the whole repair forecast is assumed repaired and repairables count as serviceable | HC/glossary/repair_optimization.html, is_repair_optimizable.html |
| Emergency Backup | Metric "Fill Rate with Emergency Backup" + backup hierarchy + Primary/Secondary Emergency FR targets. Order: location & ME optimization → network SG → emergency backup → (MIME ignores emergency) → budget. A covered SKU always uses Lost Sales fill rate. Not allowed with the approximate fill-rate methods. Emergency SKUs are excluded from churn allocation. IO_EVALUATE_EMERGENCY_BACKUP_VALUES default false | HC/glossary/emergency_backup_location_optimization.html |
| Forecast pooling | One field location per region acts as a mini-warehouse. Member forecasts are consolidated there. Params: Param1–5/Operator1–5, Candidate Locations, Pooling Location, Force Pooling Location on ASL, Transport Mode. Annual Pool Savings = carrying-cost savings − transport cost | HC/glossary/forecast_pooling_parameter.html, audit_trail_fields_pooling_parameters.html, annual_pool_savings.html |
| ASL pooling | "Pooled ASL Management Recommendations" moves parts from location ASLs to the pooling location ASL (ASL Management "Pooled" tab) | HC/glossary/pooled_asl_management_recommendations.html |
| Rotable Pool Constraints (IO) | Fields: Is Enabled, Max Pool Stock Maximum, Max Pool Wait Time (days), Min Pool Fill Rate, Use Inventory Balance As Max. The pool is evaluated as one aggregate SKU: demand is summed, and effective lead time and EOQ are demand-weighted averages. The algorithm steps up the pooled stock max and returns the lowest-cost solution that meets the targets | HC/inv_opt/inv_opt_pid/pid_rotable_pool_constraints.html, HC/glossary/rotable_pooling.html |
| Ideal Bank Size (Parts Planning rotable) | Pooled Bank Size = Pool-level ROP + 1. Non-Pooled = Σ round(location ROP) + 1. **Ideal = min(Pooled, Non-Pooled)**. Bank Size Override is available. Review types 142/143/144/248/249 | HC/parts/parts_pid/pid_rotable_levels_page.html, HC/parts/parts_topics/review_types_for_rotable_parts_planning.html |
| Kits | A Part Kit (Is Part Kit = Y) cannot be on the ASL. Kit demand is exploded to components through dummy internal sales orders per the Kit BOM. Kitting types: Global (cannot be overridden), Location Specific, Default (overridable) | HC/glossary/part_kit.html, kitting.html |

## 5. KCM, EOQ, PBL, exchange curves

- **EOQ**:
  - The term means *Economic* OQ in Supply Planning and *Effective* OQ in IO. Effective OQ = the EOQ after rules, constraints and overrides.
  - EOQ is where order cost and carrying cost intersect. The explicit formula is not given (assume √(2DS/H), **UNVERIFIED**).
  - OP_USE_REPAIR_COST_FOR_REPAIR_AUTOAPPR = true means repair orders use Repair Cost, procurement orders use Order Cost, and replenishment/balancing orders use Replenishment Order Cost.
  - Sources: HC/glossary/eoq.html, economic_order_quantity.html, effective_order_quantity.html, order_cost.html
- **KCM (K-Curve Management)**: turns workload/inventory goals into order frequencies. K links ABC order plans to EOQ theory.
  - Claimed benefit: 10–15% inventory saving with 7 order frequencies instead of 3 (ABC).
  - Steps: Order Frequencies → Order Frequency Sets → KCM Scenario (Slice Type monthly/weekly, Bucket Length, Min K, Max K, K Value Count, Respect Overrides; State Created/Running/Completed/Production) → Run (simulates cycle stock over the K range) → pick a point on the exchange curve (K, Avg Inventory On Hand, Total Receipts) → Promote to production.
  - Sources: HC/parts/parts_topics/overview_of_k_curve_management.html, HC/parts/parts_pid/pid_new_edit_kcm_scenario_page.html, pid_kcm_scenario_details_page.html, HC/glossary/order_frequency_set.html
- **Prioritized Buy List**: shows the performance trade-off at funding levels below the recommended level.
  - Buy Type: **Mandatory** (new buy to keep a zero stock max), **Rule** (to meet min constraints and overrides), **Discretionary** (steps toward the final mix).
  - Per step: Part Sequence, B4B, Incremental FR / New Buy / New Buy Cost / Stock Max / SM Value, Network New Buy Cost, Network SM Value, Network (Weighted/Equipment) EBO, Weighted EBO Reduction.
  - Sources: HC/inv_opt/inv_opt_pid/pid_part_buy_list_container.html, HC/glossary/prioritized_buy_list.html
- **Exchange curves**:
  - Network Availability Exchange Curve plots Availability, EBO, Optimized Avg Wait Time, ROP, SS, SM and values per Index point, with a Selected flag.
  - Fill Rate Exchange Curve plots Fill Rate by Stock Max / SS / ROP in Units or Value for the selected SKU.
  - Sources: HC/inv_opt/inv_opt_pid/pid_network_availability_exchange_curve.html, HC/inv_opt/inv_opt_smart_help/sh_fill_rate_exchange_curve_container.html
- **Fill Rate by Stock Level**: a per-SKU table of Fill Rate against ROP/SM candidates, with Override Value (capped by MEO_OVERRIDE_MAX_QTY) and Production Value. Overrides can be entered from it. Source: HC/inv_opt/inv_opt_pid/pid_fill_rate_by_stock_level_container.html

## 6. IO KPIs / outputs

| KPI | Definition / formula | Source |
|---|---|---|
| Expected On Hand | Expected mean inventory level in the interval. Value = EOH × Part Cost | HC/glossary/expected_on_hand.html, expected_on_hand_value.html |
| Wait Time | EBO / Total Daily Forecast (days) | HC/glossary/wait_time.html |
| Fill Rate / Total Fill Rate | Share of demand filled from stock without backorder, per the scenario's Fill Rate Method | HC/glossary/fill_rate.html |
| Customer Location FR / Customer Network FR | Weighted by external forecast (per location / across the network) | HC/glossary/customer_location_fill_rate.html, customer_network_fill_rate.html |
| Total Location FR / Network FR | Weighted by total forecast (external + internal) | HC/glossary/total_location_fill_rate.html, network_fill_rate.html |
| Inventory Turns | (Daily Demand Rate × 365) / Average Inventory, where Daily Demand Rate = customer + resupply demand | HC/glossary/inventory_turns.html |
| Planned Revenue at Risk | (1 − Fill Rate) × Resale Price × Interval Forecast | HC/glossary/planned_revenue_at_risk.html |
| New Buy Need (Local) | Stockmax − Allocated Inventory Balance − Allocated Repairable Inv Balance + New Buy Need (Mandatory Local) | HC/glossary/new_buy_need_local.html |
| New Buy Need (Mandatory Local) / Cost (Mandatory) | Minimum buy that keeps inventory ≥ 0 at the end of the interval | HC/glossary/new_buy_need_mandatory_local.html |
| New Buy Need (Procurement) | Local + all descendants' local need, at the procurement location. IO_NEW_BUY_PROC_EFFOQ_THRESHOLD (default false): true means a PO is raised only when need ≥ Effective OQ | HC/glossary/new_buy_need_procurement.html, global_settings_io.html |
| New Buy / Allocated New Buy | New Buy = the need if a PO is triggered at the procurement location, otherwise 0 (0 at non-procurement locations). Allocated New Buy = local need if triggered, otherwise 0 | HC/glossary/new_buy.html, allocated_new_buy.html |
| Repair Need / Repair Need (Mandatory) | Supply through repair, possibly at the parent. Mandatory = minimum repair that keeps inventory from going negative at the end of the interval | HC/glossary/repair_need.html, repair_need_mandatory.html |
| Condemned Interval Forecast | Forecast scrapped units over the scenario days | HC/glossary/condemned_interval_forecast.html |
| Stockout Cost (FR / WT) | See §1 | pid_stockout_costs_container |
| Weighted EBO / Network Weighted (Equipment) EBO | See §3/§4. The network figure is the sum over SKUs | HC/glossary/network_weighted_equipment_ebo.html |

## 7. Level formulas

- **Stock Maximum**:
  - Stock Maximum = ROP + Effective Order Quantity.
  - SM 0 = not stocked.
  - Multi-period summary values are forecast-weighted averages.
  - Source: HC/glossary/stock_maximum.html
- **ROP**:
  - The inventory position that triggers an order. −1 = not stocked.
  - Source: HC/glossary/rop.html
- **Safety Stock**:
  - SS = Round((ROP − Pipeline Forecast) / COS) × COS.
  - The minimum is −1; it is rounded again if COS is fractional.
  - Under Time-Phased ROP there is no rounding and no floor (2 decimal places).
  - Source: HC/glossary/safety_stock.html
- **Repair Stock Max**:
  - Repair Stock Max = SS + Repair Pipeline Forecast + Repair EOQ.
  - Stock Max ≤ Repair Stock Max.
  - Repair ROP depends on the repair-type global setting.
  - Sources: HC/glossary/repair_stock_maximum.html, repair_rop.html
- **Additive ROP**:
  - A post-optimization integer > 0, added after all min/max/fixed overrides (e.g. −1 + 5 = 4).
  - Additive ROP Value = Additive ROP × Part Cost.
  - Source: HC/glossary/additive_rop.html
- **Days-based conversion**:
  - X(days) = X / Total Daily Forecast for ROP, SS and Stock Max.
  - The result is 0 if X = −1, or if the forecast is 0 or missing.
  - Min/Max/Fixed (days) constraints presumably convert back as days × Total Daily Forecast (**UNVERIFIED**; not stated).
  - Sources: HC/glossary/rop_days.html, safety_stock_days.html, stock_maximum_days.html
- **Demand-rate look-ahead**:
  - Days = Demand Rate Days Constant + Multiplier × SKU Resupply Lead Time Days.
  - Used for the std dev in the levels calculation.
  - Look Ahead Days for Sales Orders (History Based Simulator) default 0.
  - Sources: HC/glossary/demand_rate_days_multiplier.html, look_ahead_days_for_sales_orders.html
- **Levels flags**:
  - LEVELS_TYPE2_TREAT_EOQ_ONE_AS_USUAL: by default, low-volume Type II with EOQ = 1 uses Type I.
  - Use Procurement / Use Replenishment Lead Time are Y/N flags that include each lead time in the levels calculation.
  - Sources: HC/glossary/levels_calculations.html, use_procurement_lead_time.html
- **VMR / CoV caps**:
  - Named parameter sets, each with a Low-Volume and High-Volume cap.
  - Sources: HC/inv_opt/inv_opt_pid/pid_vmrcap_parameters_page.html, pid_coefficient_of_variation_parameter_page_fields.html

## Other IO defaults found

| Global setting | Default | Note | Source |
|---|---|---|---|
| INVENTORY_OPTIMIZATION_MODE | MEO | SIO/MIO/MEO/MIME | HC/glossary/global_settings_io.html |
| ENABLE_NRTS | true | — | same |
| MEO_OVERRIDE_MAX_QTY | 0 | 0 = no confirmation threshold | same |
| MEO_OVERRIDE_DEFAULT_PERIODS_TO_EXPIRE | 0 | 0 = no End Date | same |
| IO_OVERRIDE_CLEANUP_EXPIRED_RECORDS_DAYS | 180 | — | same |
| ALLOW_NEGATIVE_SAFETY_STOCK | false | — | same |
| IO_NEW_BUY_PROC_EFFOQ_THRESHOLD | false | — | same |
| IO_EVALUATE_EMERGENCY_BACKUP_VALUES | false | — | same |
| SPACE_CONSTRAINT_TYPE | Cubic Meter | — | same |
| IO_CREATE_PROD_SUMMARY_IN_STANDALONE_JOB_ONLY | false | — | HC/glossary/scenario_processes.html |
| MEO_REPAIR_TYPE | 3 (new installs) / 2 (existing) | — | rn_enhancements_io_2 |

Not found in the corpus: IO_ENABLE_REPAIR_OPTIMIZATION default, OPT_MIN_UNIT_COST default, FISCAL_YR_STARTING_MONTH default, scenario Horizon/Interval defaults, a closed-form availability formula, a lateral-transshipment feature (no "lateral" hits; pooling covers it).
