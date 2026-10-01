# PTC Servigistics: Functional Capabilities, Methods and Planning Workflow

Research date: 2026-09-30. Primary source: the public Servigistics 13.x online help center (`https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/`, abbreviated **HC/** below). It was crawled locally (4,417 pages) to `scratchpad/spm/ptc/txt/`, where the first line of each file is its source URL. Secondary sources: PTC blogs, case studies and press, the Servigistics SaaS Service Description (Aug 2025), a Stanford EE392b lecture by PTC (Apr 2023), Lokad's vendor review and Inbound Logistics.

Anything marked **UNVERIFIED** is an inference that was not read in a source.

Coverage caveat: the help center is very large. This report covers the most important definitions and parameters. For finer page-level detail, grep the local crawl, for example `grep -l -i 'rotable' txt/*`.

---

## 0. Product map and packaging

| Package (SaaS, Aug 2025) | Features included |
|---|---|
| Commercial Foundation | Forecasting, Optimization (MEO), Order Planning, Last Time Buy (LTB) Planning, PAI Foundation |
| Foundation+ | Adds Advanced Forecasting, Advanced MEO, Advanced Order Planning, History Based Simulation, Global Part Chains, Enhanced Supply Chain Modeling |
| Commercial Advanced | Adds Cluster Based LTB, Local Part Chains, Network Optimization, Service Parts Pricing, Connected SPM, PAI Advanced, Data Science/ML hours, Snowflake credits |
| Premium | Adds AUO and K-Curve |
| FA&D (aviation and defense) variants | Optimization "MEO and AUO"; defense adds Global Part Chains, Enhanced Supply Chain Modeling and History Based Simulation |

Source for the packaging table: SaaS Service Description PDF, https://ptc-p-001.sitecorecontenthub.cloud/api/public/content/312715bc95994beb94cb013a4906dbe8?v=9c7c8608

- **What "AUO" stands for:** probably Asset Uptime Optimization, sold as "Asset Sustainability Optimization (ASO)", which "develops stocking plans to guarantee desired uptime or availability levels of complex assets". The ASO quote is from https://www.ptc.com/en/products/servigistics/capabilities. The AUO = ASO mapping is **UNVERIFIED**.
- **Licensing units:**
  - PMI: inventory value in US$1M blocks.
  - PXL: number of parts × number of locations.
  - DAL: Dealer Assigned Locations. This is the "Servigistics SaaS Retail Inventory Management (RIM) for OEM", the dealer offering.
  - PLP (part/location pairs): a sizing constraint. "In SPM forecasting and planning are done for each part at each location where it has been used in the past (demand) or is anticipated to be used in the future (forecast)."
  - Source for licensing units: SaaS Service Description (link above).
- **Capability list on the PTC product site:** Forecasting, MEO, ASO, Network Optimization, Lifecycle Analysis, Connected SPM (with ThingWorx), Initial Provisioning, K-curve Cycle Stock, Last Time Buy, Demand Planning, Lifecycle Management, Dealer Inventory Management ("Empowers your dealers to maintain optimal stocking levels"). Source: https://www.ptc.com/en/products/servigistics/capabilities
- **Suite pillars (PTC lecture):**
  - Demand Forecasting
  - Inventory Optimization ("AI optimized stocking levels using a predictive twin")
  - Order Planning & Planner Workbench ("optimize return, repair, transfer and reuse of existing assets … procurement averse")
  - Pricing
  - Advanced Analytics & Modeling ("ML based root cause analysis, what-if modeling and simulation")
  - Source: https://web.stanford.edu/class/archive/ee/ee392b/ee392b.1236/lecture/apr18/PTC.pdf
- **Heritage:**
  - PTC acquired Servigistics in October 2012 (https://www.lokad.com/review-of-ptc-com/).
  - The LPA/Xelus planning design "has since been incorporated into the Servigistics platform" (https://www.ptc.com/en/blogs/service/multi-echelon-planning-not-multi-echelon-optimization).
  - The MCA Solutions lineage is Poisson/compound-Poisson demand plus simulation (per search summaries; **UNVERIFIED** in a primary source).
- **Reference scale:** 10,000 locations, 200,000 parts, 5–6 echelons, 300 planners, $1B inventory. Echelon chain: Global Warehouse → regional DC → Country Hub → FSL / Super FSL / Remote FSL → Dealer/Distributor, plus Repair Centers and Supplier Repair. Source: Stanford PDF (above).
- **Optimization pipeline (PTC's own words):**
  1. Estimate supply and demand uncertainty, using time-series forecasting, equipment data, anomaly detection and clustering.
  2. Predict supply-chain performance with a "Probabilistic Twin, Markov chains, Monte-Carlo Simulations".
  3. Optimize stocking, repair, buy and move decisions using "Heuristics for Stochastic NLIP".
  4. Improve the model configuration using "ML on historicized data".
  - Source: Stanford PDF.

---

## 1. Core data model and terms planners use

- **Core objects:**
  - SKU = part at a location. Ranges, results and overrides are all SKU-level.
  - Demand Stream: "A grouping of related demand values over time" (HC/glossary/demand_stream.html).
  - Forecast Stream, Stream Configuration, Segment, Segment Group, Segment Node, Service Group, Part Family, Part Chain (supersession/substitution chain), Location Type, Ordering Parameter, Order Policy, Scenario.
- **Time buckets are "slices".** Dates must align to slice boundaries, for example month start in a monthly database. Some parameters are counted in slices, such as "Fixed EOQ (slices)" and "# of Slices for Forecast Error Calculation". Sources: HC/glossary/causal_forecast_method.html, HC/glossary/fixed_eoq_slices.html.
- **AutoPilot is the batch process framework.** The manual AutoPilot run offers Synchronize Database, Forecasting and Forecast Netting. AutoPilot Parameters assign Stream Configurations to segments. Other AutoPilot processes include Generate Order Plan and Customer Order Size. Sources: HC/core/core_topics/forecasting_configuration.html; release notes.
- **Cadence:** "Every night, the system looks at what occurred during the day, and comes up with new numbers the next day" (Cray, https://www.inboundlogistics.com/articles/servigistics-service-parts-planning-more-science-less-art/).
- **Main UI pages named in the help:**
  - Demand Detail, Demand Summary, Demand Streams, Forecast Streams, Forecast Parameters, Forecast Analysis, Forecast Review
  - Best Fit, Best Fit Details, Best Fit Management
  - Interactive Planner Worksheet (IPWS; tabs Plan / Forecast; containers such as Forecast Metrics and Forecast/Parameter Metrics)
  - Review Board, Work Queue, Alerts, Critical Shortages, Excess, Procurement, Repair, Replenishment
  - ASL Management, Stocking Policy, SKU Overrides, SKU Summary, SKU Detail Report, Location Summary, Part Summary, Part Supply Chain, Segment Summary
  - Service Group Parameters, Service Group Results, Scenario Summary, Scenario Budget Summary, Part/Service Group Budget Summary
  - Inventory Collaboration (containers: SKU Levels, SKU Overrides, Fill Rate by Stock Level, SKU Demand Details)
  - KCM Scenarios, Order Frequency Sets, Inventory Studio, Planner 360
  - Sources: glossary "Appears on these pages" lists (for example HC/glossary/alert.html, HC/glossary/customer_demands_fill_rate.html, HC/glossary/mape.html).
- **Scenario comparison convention:** many optimization fields display (A) the first scenario, (B) the compare scenario, and (Delta). Source: HC/glossary/availability.html.

---

## 2. Forecasting / demand planning

### 2.1 Forecast methods (24 listed in the glossary, HC/glossary/forecast_method.html)

| Method | Mechanics and parameters (verbatim or near-verbatim) | Source |
|---|---|---|
| Average, Weighted Average | Simple and weighted means. Moving Average's weight factor (0 behaves like Average, 1 like Weighted Average) links them. | HC/glossary/moving_average_forecast_method.html |
| Moving Average | "weighted average of the last n slices". Example for n=3: (H1×3+H2×2+H3×1)/6. Minimum 1 month of history. | same |
| Single / Double Exponential Smoothing, Winters Multiplicative, Linear Regression, Same As Last Year | Classical level, trend and seasonal methods. Best-fit eligibility rules apply; for example "Last 5 demand slices contains at least one zero demand. Linear Regression eliminated." | HC glossary (best-fit rule text, crawl) |
| **Croston** | "designed for intermittent and erratic demand … infrequent events … not necessarily unit-sized." Separate exponential smoothing of inter-demand interval and demand size; no seasonality. Needs **12 months of history**; otherwise it falls back to SES **and creates a review record**. `crostons_alpha` global setting controls demand-size smoothing. Tracks interval SD and size SD, updated only after each **non-zero** demand period. | HC/glossary/croston_forecast_method.html |
| **Intermittence Smoothing** | Hybrid: "modified Croston" when demand is intermittent, SES-like when steady. Single α. Recommended "as the default forecast method for those streams where a lack of data does not allow for the use of Best Fit." | HC/glossary/intermittence_smoothing_forecast_method.html |
| **Servigistics TSB** | Teunter-Syntetos-Babai: demand **probability** updated every period in place of the interval. This decays forecasts during long zero runs; the decay behaviour is the known TSB property and is **UNVERIFIED** in the help text. | HC/glossary/servigistics_tsb_forecast_method.html |
| **Causal** (install-base) | "BOM based forecasting of parts at all levels in the BOM … forecasts failure rates for parts using historic demand and installed base." Formula: `(Current Effective Total Population OR Product Rollout × BOM Qty × Attach Rate) × Σ(Causal Value × Failure Rate × Weight Factor)`. Failure rate is exponentially smoothed with emphasis on recent data. Forecast is at the top-level part of a chain; replaced parts' populations roll up. Alternates are treated as independent parts. | HC/glossary/causal_forecast_method.html |
| **Leading Indicators** | Installed quantity × usage/failure rate. Usage rate comes from MTBF, an external source, or history ÷ install base. Smoothing: "previously calculated usage rate is weighted 80% and the current slice's usage rate is weighted 20%". Needs at least one full month of non-zero install base and demand. | HC/glossary/leading_indicators_forecast_method.html |
| **Replacement Rate** | Component forecast = Replacement Rate × Repair Rate × Parent total forecast (internal + external). `Repair Rate = (1−ReturnWash)(1−RepairWash)(1−NFF) + (1−ReturnWash)·NFF`. No variance is generated. In 13.1 the child variability can be taken from the parent (`FCST_REP_RATE_USE_PARENT_SD`). | HC/glossary/replacement_rate_forecast_method.html; release notes |
| Life Limited Parts; LLP Maintenance – Raw / Smooth | Predicts service events from flight hours/cycles versus maximum allowable life (aerospace). | HC/glossary/life_limited_parts_forecast_method.html |
| Scheduled Event Maintenance | Dependent demand from scheduled maintenance events. Lower-level streams roll up via bidirectional Related Stream IDs. External Indicator flag is "y" on the event stream and "n" on the rollup stream. | HC/glossary/scheduled_event_maintenance_forecast_method.html |
| Composite | Blends streams: `Σ weightfactor(i)×(forecast + scheduled + non-recurring)`. Weights can be time-varying. Cannot be manually adjusted. Computes MAD, MAPE, RMSE and tracking signal. | HC/glossary/composite_forecast_method.html |
| Forecast Disaggregation | Aggregates child-location demand to a parent, forecasts there, then allocates back by system-calculated or user weights. | HC/glossary/forecast_disaggregation_forecast_method.html |
| **Servigistics ML / ML Composite** | AutoPilot picks among **BATS, Auto ETS, Prophet, XGBoost, SARIMA**. Integrated into Best Fit in 13.1 (PAI 5.0). Multivariate ML: "any economic factor or non-demand based attribute can be used". | HC/glossary/servigistics_ml_forecast_method.html; HC/release_notes/release_note_section.html |
| Initial Provisioning; Re-provisioning | New-product forecast methods. Pages: HC/core/core_topics/initial_provisioning_forecast_method.html and re_provisioning_forecast_method.html. Detail not extracted here. | those pages |
| Manual Forecast; Do Not Forecast | Planner-entered values; exclusion. | glossary |

New parts and locations: a "similar part" or "similar location" can be used "to estimate demand for the part [location] … if the part is new and has no demand history" (HC glossary, crawl; like-item NPI).

### 2.2 Best Fit (method selection)

- Mechanism: backtests every method enabled in Forecast Parameters over a Holdout Window. "The forecast method that results in the smallest forecast error over the specified time period is designated … Best Fit" (HC/glossary/best_fit_analysis.html).
- Data recommendation: "three years of demand history (36 slices …) and a one year forecast window (12 slices)".
- Two modes:
  - **Auto Approved**: assigned automatically. When configured at stream-configuration level it runs once, then pins the method at SKU level.
  - **Recommended**: results post to the Best Fit page for planner approval.
- Churn guard: the help warns that unstable best-fit switching causes "unstable levels which … lead to excess or stock-outs". 13.1 added a parameter to reduce method churn (release notes).
- Rule-based elimination: methods are removed when the data does not fit them (for example the zero-in-last-5-slices rule for Linear Regression).

### 2.3 Demand streams, netting, non-recurring demand, outliers

- **Demand streams.** History is split into streams that are analysed and forecast separately; the help's framing is "to create a more accurate forecast" (HC/core/core_topics/overview_of_demand_forecasting.html). Examples such as warranty vs paid or internal vs external are **UNVERIFIED** as named defaults, but the Replacement Rate method explicitly refers to "internal & external forecast".
- **Scheduled demand vs non-recurring demand** (recalls, field change orders). Three rules decide what counts as "normal usage" when a planner enters a non-recurring adjustment:
  1. Actual demand > adjustment: the whole adjustment is backed out and the excess is normal usage.
  2. Actual demand < adjustment: remaining actual demand is backed out and the calculated forecast is normal usage.
  3. Actual demand < calculated forecast: no adjustment, and actual demand is normal usage.
  - Source: HC/core/core_topics/overview_of_demand_forecasting.html.
- **Forecast netting (consumption):** `Netted Forecast = max[(Forecast − Demand), 0]` within the slice (HC/glossary/forecast_netting.html). Netting is its own AutoPilot step.
- **Outlier Adjustment (for slow and intermittent demand):**
  - Probabilistic control limits. Upper Control Limit Confidence Level defaults to **99.73%**.
  - There is also an adjustment limit.
  - The **lower control limit is fixed at 0** because intermittent SKUs "will never have a negative spike".
  - Outliers are computed on raw history, while the displayed history average and SD include adjustments.
  - A parameter sets the minimum number of non-zero slices that must remain after outlier correction.
  - Since 13.1, outliers are "automatically cleaned up based on Forecast Parameter settings", with `OUTLIER_USE_VARIABILITY_CAP`.
  - Sources: HC/glossary/outlier_adjustment.html; release notes.
- **Zero-demand treatment:**
  - Croston and TSB smooth only on non-zero events (Croston) or per period (TSB).
  - Intermittency is measured "from the first non-zero demand".
  - Zero-demand slices can disqualify trend methods.
  - Sources: HC glossary (Croston, best-fit rule text).

### 2.4 Accuracy metrics and review

- Metrics: MAD, MAPE, RMSE, tracking signal, History Avg/SD, Forecast Error SD, Forecast SD (HC/glossary/composite_forecast_method.html).
- **Tracking Signal** = (RSFE / count) / MAD. The count is "# of Slices for Forecast Error Calculation" or the Best Fit "Holdout Window" (HC/glossary/tracking_signal.html).
- **MAPE** uses N = holdout slices for Best Fit, or the error-calculation window for Demand. The help notes that MAPE can exceed 2 when demand is negative (HC/glossary/mape.html).
- **Forecast Error SD** = sqrt(Σ(Demand−Forecast)²/(N−1)). This is the variability passed to optimization (HC/glossary/replacement_rate_forecast_method.html).
- **Forecast Review page** (13.1): aggregated monetary values for SIOP; SKU overrides for SIOP scenarios; worksheet highlights the top contributing locations (release notes).
- **Forecast Override Intelligence:** "Machine learning-based recommendations against detrimental forecast overrides" (PAI 5.0 release notes).
- **Consensus forecasting for SIOP** and MTBF/multivariate methods were added in 14.0 (https://www.ptc.com/en/blogs/service/servigistics-transformative-release).
- Adjustments are made on the Demand Summary page, the Demand page, and per-stream demand settings, and results can be regenerated per stream (links from the overview page).

### 2.5 Supersession, part chains, lifecycle

- **Part Chains:** the audit fields show Relation Type, Part Procurable (y/n), Part Repairable (y/n), Roll Up Demand Percent, Roll Up Bad, ASL Retention Min Forecast / Min Inventory, and Global vs location-specific chains (HC/glossary/audit_trail_fields_part_chain.html).
  - Demand therefore rolls up to the chain head by a percentage.
  - Old-part inventory can be used up. The mechanism is **UNVERIFIED**; "Allow Substitution Excess Transfer" supports it.
- **Substitution settings:** Enable Part Substitution, and Allow Substitution Excess Transfer with options No / Yes, all locations / Yes, only at non-replenishment source locations (default) (HC/glossary/allow_substitution_excess_transfer.html).
- **Packaging:** Global Part Chains are in Foundation+; Local Part Chains are in Advanced (SaaS PDF).
- **Lifecycle:**
  - NPI through Initial Provisioning, Causal/Leading Indicator with product rollout, and similar part.
  - EOL through Last Time Buy.
  - "cluster analysis to support the launch and end-of-life forecasts" (PTC blog search summary, https://www.ptc.com/en/blogs/service/gartner-perspective-service-supply-chains-servigistics).
  - Life Cycle Planner persona: "New parts and End of Life Forecast; MTBF; Life cycle KPIs" (Stanford PDF).
- **MTBF:** forecasted MTBF/failure rate via statistical and ML methods, "Cutover from Engineering to Forecasted MTBF", new-part MTBF prediction, product- and region-specific MTBF (Stanford PDF). 13.1 lets dashboards switch between MTBF and failure rate.
- **Remaining Useful Life:** ML prediction per serialized item from utilization and sensor data (PAI 5.0).

---

## 3. Inventory optimization (MEO)

### 3.1 Philosophy

- MEO "establishes inventory levels based on the relationships between all the locations … and all of the parts at the lowest cost." It considers effective lead times between locations, the overall service target, demand for all parts, and budget constraints.
- It works on "the matrix of availability targets for part groups and location types".
- It "computes the marginal contribution to level of service for each dollar of inventory 'spent'".
- It holds stock at higher echelons where utilization is higher.
- "Critical slow moving parts are assigned high levels of service".
- This is contrasted with "multi-echelon planning", which sets per-location fill rates in isolation.
- Source: https://www.ptc.com/en/blogs/service/multi-echelon-planning-not-multi-echelon-optimization
- **Claimed outcomes:** fill rate target at "up to 30%" lower inventory. Pratt & Whitney: 20 MRO sites, fill rate +10%, inventory −10%. Source: https://www.ptc.com/en/solutions/reduce-costs/field-service-cost/inventory-optimization (search summary).
- **Academic basis:** a METRIC-style model. The pipeline is `μ = m[rT + (1−r)(O + EBO_parent/m_parent)]`, and marginal analysis starts from minimum stock and allocates each increment to the part/location with the greatest Δavailability per $. This is from **SAP** patent US7778857B2 (https://patents.google.com/patent/US7778857B2/en), shown for context only. It is not a Servigistics document, and Servigistics' internal solver is not published (Lokad review).

### 3.2 Service targets and definitions

- **Fill rate:**
  - Customer Demands (Fill Rate) is "The expected number of unsatisfied customer demands".
  - Line fill rate is optimized via a Customer Order Size AutoPilot. Settings: `CUST_ORDER_SIZE_DMD_HIST_HORIZON`, `_MIN_DMD_RECS`, `_OUTLIER_HANDLING`, `_OUTLIER_STD`, `_VARIABILITY_CAP`, `IO_CALC_CUST_ORDER_SIZE`.
  - Sources: HC/glossary/customer_demands_fill_rate.html; 13.1 release notes.
- **Type I vs Type II service:** "Type I service only considers demand satisfaction in calculating safety quantities and, thus, is not directly affected by order sizes. … when the on hand stock level drops to zero, Type I will not get any credit …, while Type II may get credit since it is based on backorder." (HC glossary, crawl).
- **Availability:** "The expected percentage of time that equipment is operational" (HC/glossary/availability.html). This is the system/asset-level target used by ASO/AUO and multi-indenture.
- **Response time and wait time:**
  - Rotable pools have "maximum pool wait time targets" (13.1).
  - Network design uses driving distance and SLA (Stanford PDF).
- **Service Groups:**
  - Targets and constraints are set per service group (Service Group Parameters, Service Group Results).
  - A flag controls whether service groups include non-stock items (HC/glossary/service_groups_include_non_stock_items.html).
  - Criticality, cost and lifecycle drive differentiated targets. Example: 99.8% for cheap critical new-product parts versus 70% for old expensive ones (https://www.inboundlogistics.com/articles/servigistics-service-parts-planning-more-science-less-art/).
- **Segmentation:** "segments are assigned to a 'best-fit' planning model … describing the deployment, replenishment, forecasting and review parameters for the segment" (Inbound Logistics). In the product, segments feed Forecast Parameters, AutoPilot Parameters, KCM scenarios and so on.
- **Optimization objective:**
  - Selectable cost metric, or carbon minimization (13.1 "Inventory Optimization Cost").
  - Settings: `CARBON_MEASURE_TYPE`, `CARBON_TAX_RATE`, `IO_CALCULATE_SUSTAINABILITY`.
  - Mode switch `INVENTORY_OPTIMIZATION_MODE` (for example SIO) (HC/glossary/churn_control_method.html).
- **Budget:** Scenario Budget Summary, Part Budget Summary and Service Group Budget Summary pages. "Budget Optimized" is a maturity tier. Multi-period optimization and time-phased budget metrics were added in 13.1/14.0 (Stanford PDF; release notes).

### 3.3 Stocking decision (stock / no-stock) and levels

- **Authorized Stocking List (ASL):**
  - Only ASL parts get optimal levels, order recommendations and critical-shortage notices.
  - Inventory of a non-ASL part is **excess**.
  - ASL membership comes from **Pareto analysis**: parts are sorted by share of location demand and added "until their cumulative demand equals the **Demand Accommodation** percentage", or added manually.
  - Source: HC/glossary/authorized_stocking_list.html.
  - "ASL Method" and ASL Retention Min Forecast/Inventory are part-chain fields. ASL Management is a page.
- **Output levels per SKU:**
  - ROP and ROP (days), each with Min/Max.
  - Safety Stock and Safety Stock (days), each with Min/Max.
  - Stock Maximum and Stock Maximum (days), with Min/Max. "Minimum Stock Maximum" is a floor on the post-optimization stock maximum.
  - Separate procurement, replenishment and repair ROPs.
  - Sources: HC/glossary/rop_days.html, safety_stock_days.html, stock_maximum_days.html, minimum_stock_maximum.html.
- **Overrides versus constraints:** overrides are set per SKU (SKU Overrides page, SKU Detail Report, Stocking Policy and Inventory Collaboration containers); constraints are set per service group (Service Group Parameters) (HC/glossary/minimum_stock_maximum.html).
- **Churn control** limits period-to-period swings of ROP. Methods:
  - None
  - Use Inventory Balance with Reference Scenario
  - Use Inventory Balance (current stock first; "condemned forecast" burns down inventory over the horizon)
  - Respect Production
  - Respect Previous Period
  - A threshold above 100% lets ROP −1 become 0, or 0 become 1.
  - Source: HC/glossary/churn_control_method.html.
- **Cycle stock / EOQ:**
  - K-Curve Methodology (KCM) scenarios with **Order Frequency Sets** assigned per segment. "Determine order quantity … developing an optimal ABC classification of parts by order frequency, including annual usage, part/pair cost and order frequency sets" (https://www.ptc.com/en/products/servigistics/capabilities; HC/parts/parts_topics/creating_modifying_kcm_scenarios.html).
  - Fixed EOQ (slices) is an override (HC/glossary/fixed_eoq_slices.html).
- **Rounding:** `IO_TPROP_ROUND_SS` for time-phased ROP safety-stock rounding (13.1 settings).
- **Rotables:**
  - Repair pipeline with wash rates. "Repair Wash Rate = 10% … recommended quantity will be 11 units of On Hand Bad" (HC/glossary/repair_wash_rate.html).
  - Also Return Wash Rate and NFF (No Fault Found) rate.
  - Rotable pooling optimization.
  - Multi-indenture support for "MIO SKUs".
- **Lateral and upchain transfers:** Allow Upchain Excess Transfer. Rebalance cost is "The expected cost of placing orders to satisfy removals" (HC/glossary/rebalance_cost.html).

### 3.4 Network optimization, scenarios, simulation

- **Network Optimization:** "Uses driving distance and SLA to minimize the number of stocking locations", models location start-up, shut-down and operating costs, and "Assigns Installed Base/contract customer sites to best stocking locations" (Stanford PDF).
- **What-if scenarios (13.1):** "Simulate forecast, price, and carbon tax changes, in addition to SKU data such as lead times, wash rates, and costs". Multiple-scenario comparison supports SIOP. The display limit is `MAXIMUM_ADDITIONAL_SCENARIOS_DISPLAY_COUNT` (release notes).
- **Modeling module:** Simulations, Automated Dataset Comparison, Enhanced Supply Chain Modeling, History Based Simulation (HC/core/core_topics/module_modeling*.html; SaaS PDF).
- **Inventory Studio:** a map display, controlled by `INVENTORY_STUDIO_MAP_DISPLAY`.

---

## 4. Supply / order planning (execution)

- **Order Policies,** assigned via Ordering Parameters to a part or SKU (HC/glossary/order_policy_type.html):
  - **Trigger Point (TR):** need is evaluated at order date; order when Inventory Balance ≤ ROP; quantity "Up to Stock Max, then order sized". Recommended default: "It is almost always best to use Trigger Point". Good fit for low-volume, cheap, less critical, short-lead-time parts.
  - **Time-Phased Safety Stock:** need is evaluated at available date, through the horizon; triggers when Projected On Hand < SL; quantity is "Multiples of EOQ to cover need, then order sized".
  - **Time-Phased ROP** (13.1.0.1 enhancements).
- **Trigger Point exception semantics:**
  - Stock at or below the procurement, replenishment or repair ROP generates a recommendation back to Stock Max.
  - Stock at Safety Stock posts a **critical shortage** record to the Review Board.
  - Stock above Stock Max posts an **excess** record to the Review Board.
  - Source: HC/glossary/trigger_point.html.
- **Availability-Based Replenishment (ABR):** "When ABR is not enabled in a connected model, it allows the source location inventory balance to go negative and results in backorders at the topmost procuring locations" (HC/glossary/availability_based_replenishment.html).
- **Chain deficit:** "Ending Time Phased Chain Deficit" is the down-chain requirement that available supply could not meet (HC/glossary/ending_time_phased_chain_deficit.html). Setting: `OP_ENABLE_TIMEPHASED_REPL_CHAIN_DEFICIT`.
- **Generate Order Plan AutoPilot:** produces buy, repair, replenish/deploy, transfer/excess and return recommendations. Pages: Procurement, Repair, Replenishment, Excess, Critical Shortages.
- **Order Explanation Report** (13.1.0.1) explains "the sequence of decisions made during the Generate Order Plan AutoPilot process for each day". This is the explainability feature.
- **13.1 supply enhancements** (source: release notes, HC/release_notes/release_note_section.html):
  - Vendor capacity: monthly limit per vendor.
  - Multi-vendor use in priority order.
  - Order spreading: a large order spread over time before vendor closure.
  - Improved order sizing rules to avoid overstock; `BUY_LIST_ROUNDING_RULE`.
  - Alternate transport mode chosen for backorder prevention.
  - Calendar adjustments driven by process time + transportation time + put-away time; settings `OP_TIME_PHASED_ROP_CALENDAR_ADJUSTMENTS_AT_TOP_MOST_LOC_ONLY` and `…_IO_LEAD_TIME_INCREASE`.
  - Sales returns counted through the horizon (`OP_COUNT_SALES_RETURNS_THROUGH_HORIZON`).
  - Return wash rate applied at non-repair locations (`APPLY_RETURN_WR_NON_REPAIR_LOC`).
- **Backorder categorization:** subcategories such as vendor delay and under-forecast (13.1; PAI Demand Miss Analysis). PAI glossary includes a "root cause categorization" page.
- **IPWS** (Interactive Planner Worksheet) is the core planner screen:
  - Time-series graph including Safety Stock and ROP with schedule-change suppression.
  - Deployments shown with totals and subtotals.
  - Child ending inventory position.
  - "Effective Ending On Hand Good".
  - Forecast tab with metrics.
  - A Go To menu into PAI dashboards and external applications.
- **Plan Intelligence** (`ENABLE_PLAN_INTELLIGENCE_IPWS`): "provides guidance and suggests best practices and root causes for common planning issues" (release notes).
- **Exceptions and workflow:**
  - **Review Board** records, which include system review reasons such as `COSTDATE_EARLIER_THAN_PRICEDATE_ALERT` and a forecast fallback review record.
  - My Review Reasons filter, Manually Delay Review, review comments, Work Queue.
  - **Alerts** are user-created dated reminders, addressed to All or a named user (HC/glossary/alert.html; HC/glossary/audit_trail_fields_review_reasons.html).
  - Approvals on the SKU Summary and Location Summary pages (13.1).
  - Every change is audit-trailed.
- **Supplier lead time:** Stanford lists "Predicting Part Lead Time" as a Metso challenge that ML addresses. Lead-time settings live in Module Settings › Lead Time (HC/core/core_topics/modules_settings_lead_time.html). Lead-time variability handling: detail not extracted, **UNVERIFIED**.

---

## 5. Last Time Buy, Initial Provisioning, EOL

- **LTB trigger:** end of production, or the vendor stops manufacturing. The planner recommends a quantity sufficient for the install base "but that does not cause excessive inventory at the end of the support period" (HC/glossary/last_time_buy.html).
- **LTB pages:** LTB Profiles, LTB Planning, LTB Actions (HC/core/core_topics/module_order_plan_last_time_buy*.html).
- **Data-driven LTB:** "Systematically mines lifecycle demand data from parts that have been through the entire lifecycle" (capabilities page). "Cluster Based LTB" is an Advanced-package feature.
- **14.0 LTB** "combines forecasting, repair planning, and contract-awareness" (14.0 blog).
- **Initial Provisioning:** "procurement and stocking recommendations for parts associated with new products or product families" (capabilities page).

---

## 6. Dealer, field stock, pricing

- **Dealer:**
  - DAL-licensed "Retail Inventory Management (RIM) for OEM". Dealers log in, restricted to the OEM's parts (SaaS PDF).
  - OEM + dealers are optimized "in single model" (Stanford PDF).
  - 14.0 adds dealer compliance dashboards and dealer- and customer-specific price simulations (14.0 blog).
- **Field / van stock (ServiceMax):**
  - ServiceMax sends demand details, parts master, product replacement (supersession) info, inventory levels and locations.
  - Servigistics returns "optimized inventory levels by location and product", shown as target stock in ServiceMax for technician vans and forward stocking locations (Core 23R3).
  - Source: https://support.ptc.com/help/servicemax_asset360/en/articles/servigistics_integration/field-stock-optimization.html
- **Pricing (Service Parts Pricing):**
  - Price policies, price buckets, custom offsets (`PRC_USE_CUSTOM_OFFSETS`), part-kit pricing using component prices.
  - Dealer price feedback management (`ENABLE_PRC_FEEDBACK_MANAGEMENT`).
  - Price–volume elasticity estimation, price transactions, monthly financial process for active SKUs, price-action gateway propagation.
  - Source: 13.1 release notes.
  - Customers: GM, SAIC-GM, JLG (https://www.ptc.com/en/case-studies/general-motors).

---

## 7. Analytics, KPIs, AI

- **PAI (Performance Analytics & Intelligence) dashboards:**
  - Demand Miss Analysis
  - Fill Rate Analysis and Service Group Fill Rate Detail (Unplanned Missed, Total, Line, Unplanned Line Missed)
  - SKU Supply Chain History (daily balance, shortage, excess)
  - Backorder Days
  - Performance 360
  - Vendor Prioritization & Performance (Service Impact score; settings `PI_VENDOR_PERF_*`)
  - Vendor Forecast (collaboration)
  - Forecasting dashboards drilling from system to SKU
  - Tooling: Intellicus self-serve analytics and a Zeppelin Data Science Workbench
  - Source: PAI 5.0 release notes via HC/release_notes/release_note_section.html
- **Value claims (PTC):** part availability +10–25%, inventory −10–35%, backorders −18–37%, "3X planner productivity" (Stanford PDF).
- **ML:** best-fit ML ensemble (BATS / ETS / Prophet / XGBoost / SARIMA), multivariate forecasting, RUL, override intelligence, Plan Intelligence, Order Explanation Report.
- **AI Assistant:** GA October 2025, "improving forecast accuracy and accelerating planning cycles". Agentic "troubleshooting, root-cause analysis, and continuous improvement" (https://www.prnewswire.com/news-releases/ptc-delivers-new-service-lifecycle-management-ai-solutions-to-modernize-field-service-and-the-service-supply-chain-302570030.html).
- **14.0 (2025):** more than 40 enhancements, including agentic assistant across forecasting / IO / order planning, multi-period optimization, SIOP consensus forecasting.
- **External critique:** public material "does not expose much about solver families, uncertainty models, calibration, override logic" (https://www.lokad.com/review-of-ptc-com/).

---

## 8. Gaps not resolved in this pass (UNVERIFIED / not extracted)

- Exact demand distributions used by IO (Poisson / negative binomial / normal switching rules).
- Lead-time variability math.
- Full list of AutoPilot processes and their schedule.
- Complete review-reason catalogue.
- Pricing policy formulas.
- Default planning horizon and bucket length. Daily order planning is implied by "for each day" in the Order Explanation Report; monthly slices are typical.
- The help center crawl (`scratchpad/spm/ptc/txt/`, 4,417 pages; sections `inv_opt__*`, `parts__*`, `pricing__*`, `core__*`, `glossary__*`, `functional__*` PAI) holds these pages for follow-up.

---

## Implications for a mid-market planning module on top of our WMS

**Replicate (core value, feasible):**
1. **SKU = part × location, monthly slices, nightly batch.** This matches Servigistics' AutoPilot cadence and PLP model.
2. **Demand history per stream,** with at least a customer/paid vs internal/warranty split and non-recurring flagging (using the 3 normal-usage rules), plus forecast netting `max(F−D,0)`.
3. **A small method library with automatic selection:**
   - Methods: SES, moving average, Croston/SBA, TSB, a seasonal method (Holt-Winters), manual, do-not-forecast.
   - Best-fit by holdout MAPE/MAD, with elimination rules (for example no trend methods with recent zeros).
   - Minimum-history fallbacks, such as Croston needing 12 slices and falling back to SES while raising a review item.
   - Recommended-vs-auto-approve mode and a churn damper.
4. **Outlier cleansing** with a one-sided upper control limit (default 99.73%) and lower limit 0 for intermittent items.
5. **Accuracy KPIs:** MAD, MAPE, RMSE, tracking signal, forecast-error SD. Pass the error SD to safety stock.
6. **Stock / no-stock via ASL,** using Pareto demand-accommodation % per location plus manual add. Non-ASL on-hand counts as excess.
7. **Two order policies:**
   - Trigger Point (ROP / Stock Max, the default).
   - Time-phased safety stock for critical, long-lead parts.
   - Order sizing with MOQ, multiple, EOQ, and ABC by order frequency (a simple K-curve).
8. **Exception-driven workbench:**
   - Review board with critical shortage (at or below SS), excess (above Max), forecast fallback and data-quality reasons.
   - Per-user alerts, delay-review, approval of buy/transfer recommendations.
   - Audit trail.
   - An "order explanation" text per recommendation.
9. **Supersession chains** with demand roll-up % to the chain head and use-up of old stock.
10. **SKU overrides** (min/max ROP, SS, stock max, fixed EOQ) that sit above the calculated values.

**Simplify:**
- **MEO:** begin with single-echelon, per-SKU service-level (Type I / fill-rate) safety stock differentiated by segment (criticality × ABC). Add a 2-echelon DC → branch marginal-analysis allocator later. Avoid full METRIC / multi-indenture.
- **Churn control:** threshold-based damping only.
- **Rotables:** support repair orders with repair wash rate and NFF as parameters; skip pool wait-time optimization.
- **Scenarios:** one what-if copy of parameters (lead time, target, cost) with an A/B/Δ comparison grid.
- **LTB:** a formula-based remaining-life demand × horizon, with an installed-base decay option.
- **Dealer / van stock:** treat these as additional locations in the same SKU model.

**Skip (for now):**
- Causal / BOM failure-rate forecasting, LLP, scheduled-event maintenance.
- ML ensembles and multivariate models.
- RUL.
- Network design.
- Carbon optimization.
- Pricing / elasticity.
- PAI-grade analytics warehouse.
- Agentic AI assistant. Explainability text is the cheap, high-value substitute.
