# Servigistics 13.x — Forecasting / Demand gap notes

Source prefix `HC/` = `https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/`.
Excludes what was already known (24 methods, Croston/TSB/IS basics, Best Fit basics, Error Improvement %, UCL 99.73%, netting formula, MAPE/MAD/RMSE/TS defs, `global_settings_fcst`). Anything inferred is marked **UNVERIFIED**.

## 1. Forecast Parameters (per forecast stream + segment)

Scope: one Forecast Parameter scheme = Name + Forecast Stream + assigned Segments. It drives Forecast, Best Fit and Seasonal Profiles. It can be set globally, per segment, or per demand stream (HC/glossary/forecast_parameter.html).

### 1a. Forecasting tab: smoothing constants (defaults stated on the page)
Src: HC/parts/parts_pid/pid_new_edit_forecast_parameter_page_forecasting_tab.html

| Method | Param | Meaning | Default |
|---|---|---|---|
| Winters Multiplicative | Alpha | level | 0.1900 |
| Winters Multiplicative | Beta | trend | 0.0530 |
| Winters Multiplicative | Gamma | seasonality | 0.5 |
| Exp Smoothing (Single/Double) | Alpha | level | 0.1000 |
| Exp Smoothing (Single/Double) | Beta | trend | 0.0500 |
| Exp Smoothing (Single/Double) | Phi | trend damping (phi=1 means no damping; smaller phi damps more) | 0.7000 |
| Croston | Alpha | level + periods-between-demand | 0.1000 |
| Croston | Omega | history std-dev smoothing | 0.1000 |
| Servigistics TSB | Alpha | demand level | 0.3000 |
| Servigistics TSB | Beta | demand occurrence | 0.1000 |
| Same As Last Year | Trend % | % applied to last year's demand | 0.0000 |
| Moving Average | # of Slices, Weight | weight 0..1 inclusive; 0 behaves as Average, 1 behaves as Weighted Avg | — (HC/core/core_pid/pid_demand_detail_page.html, HC/glossary/moving_average_forecast_method.html) |

The same page lists "Alpha/Beta/Gamma/Omega +/-" analysis fields and "Allow <method>" Best Fit candidate flags. Winters Additive is "reserved for future use" (HC/parts/parts_pid/pid_forecast_parameters_page.html).

### 1b. Forecasting tab: general, std-dev and outlier fields
Src: same forecasting_tab page unless noted.

| Name | Meaning | Default / range |
|---|---|---|
| Seasonal Profile | Assigned profile. Final slice forecast = base × slice multiplier | optional |
| # of Slices for Forecast Error Calculation | Slices used for MAPE/MAD/RMSE on the Demand page. Display only, no effect on Best Fit | — |
| Std Deviation – Use forecast error | Yes: Forecast Error SD is used in safety stock. No: History Avg/SD is used | — |
| Std Deviation – Use de-seasonalized and de-trended history | Lowers SD for seasonal/trend SKUs. **Must be No when Outlier Definition is set** | — |
| Std Deviation – Use Scaled Percentage | ForecastSD = (HistorySD/HistoryAvg) × ForecastAvg, where ForecastAvg is over the stream-config forecast horizon | — |
| Enable Tracking Signal | TS = (RSFE/count)/MAD; count = "# Slices for FE Calc" or Holdout Window. Raises review types 138/139 | Y/N |
| Outlier – Management | **Change**: auto-adjust history and post a Review Board note (Adjustment line). **Notify**: no adjust, post RB, remove existing outlier adjustments. **Ignore**: no processing, existing adjustments removed | enum |
| Outlier – Definition | ± std-devs from mean that flag an outlier | **1.0–5.0 inclusive**. Hidden if Mgmt=Ignore or ConfLevel=All |
| Outlier – Correction | SD factor to correct to: 0 = mean, 2.0 = ±2σ. Must be ≤ Definition | **0–5.0** |
| Outlier – Max Consecutive Occurrences Allowed | After N consecutive outliers, prior N adjustments are removed (a new trend is assumed). Null = no max; 0 not allowed | null |
| Adjust if history less than LCL | LCL = HistAvg − (Outlier Detection Limit × SD) | Y/N |
| Use Confidence Level for Outlier Adjustments | All = probability distributions for all SKUs; Slow or Intermittent = only those SKUs; None = SD-multiplier method | **recommended All** |
| Upper Control Limit Confidence Level / Correction Confidence Level | Hidden if ConfLevel=None or Mgmt=Ignore | 99.73%, 3 dp |
| Outlier Method Used (read-only, IPWS) | Confidence Level or Mean and Standard Deviation. UCL/LCL shown per SKU | HC/parts/parts_pid/pid_ipws_forecast_forecast_parameters.html |
| Ignore demand before first non-zero slice | Yes: history starts at the first non-zero slice. Example: horizon 36 with first demand 3 slices ago uses 3 slices | Advanced (HC/parts/parts_pid/pid_forecast_parameters_page.html) |
| Use Phase In Date / Use Phase Out Date | Respect part phase dates. No forecast is generated past a valid Phase Out | Advanced |

### 1c. Best Fit tab
Src: HC/parts/parts_pid/pid_edit_forecast_parameter_page_best_fit_tab.html

| Name | Meaning | Default / rule |
|---|---|---|
| Maximum # of History Slices | Uses max(this, stream-config history horizon). Global settings may cap it | Winters and Croston need ≥12 slices, so with a 12-slice fit window Max must be ≥24 (HC/parts/parts_pid/pid_forecast_parameters_page.html) |
| Minimum # of History Slices | Slices for Best Fit methods other than Winters/Croston/DES | **blank = 12**. If fewer are available, all are used and the error "Slides<1" is raised |
| Holdout Window | Sub-window used for error calc | — |
| Holdout Window equals lead time | If Holdout is blank, it is set to the SKU lead time | Y/N |
| Best Fit Selection Criteria | Composite Error, Best 2 Out Of 3, MAPE, MAD, RMSE | — |
| Tie-breaker Error Type | Used with Best 2 of 3 | — |
| Best Fit Methods (ordered list) | Order is the tie-break | — |
| Check for Intermittency | If `INTERMITTENCY_TEST_USE_ADI`=true: intermittent when ADI > threshold. Else: PBD > threshold **and** MVR > MVR threshold | Y/N |
| Intermittency Test – Periods Between Demand | PBD = zeros/(nonzeros−1), counted from the first non-zero. Seeded from global `PERIODS_BETWEEN_DEMAND` when blank | **1.25** |
| Intermittency Test – Average Demand Interval Threshold | ADI = total periods / non-zero periods | **1.32** |
| Intermittency Test – Minimum Demand Interval MVR | Ratio of zero periods to demand periods. "Default should normally be used" | default value not stated |
| COV Squared Threshold | Non-intermittent SKU: CoV² < threshold is Smooth, otherwise Erratic | **0.49** (HC/parts/parts_pid/pid_forecast_parameters_page.html) |
| Select Forecast Method for Intermittent Demand | Intermittent Smoothing / Croston / Servigistics TSB | — |
| Apply personal seasonal profile to forecast | Non-Winters methods use deseasonalized history in error calc | — |
| Maximum number of rolling forecasts | Caps error samples per method; **6–12 recommended** for speed | — |
| Use Autocorrelation Analysis to consider Winters | Seasonal SKU → Winters is forced (stat-only config). Non-seasonal → Winters is dropped | — |
| Use Autocorrelation Analysis to detect trend | Trend detected → all flat-line methods are dropped | — |
| Min # History Slices to Consider Croston / Winters / DES | blank = Minimum # of History Slices. For Croston, min(max(this, Min), stream-config slices) is used | — |
| Force Servigistics ML Composite | Always recommend ML Composite | — |

Demand category (HC/glossary/demand_category.html): **Smooth** is ADI < 1.32 and CoV² < 0.49. **Erratic** is ADI < 1.32 and CoV² ≥ 0.49. **Intermittent** is ADI ≥ 1.32.

### 1d. Minimum history per method (method glossary pages)
| Method | Min history / fallback | Src |
|---|---|---|
| Croston | 12 months. Otherwise uses SES and posts RB (review 64) | HC/glossary/croston_forecast_method.html |
| Winters Multiplicative | 12 months. Otherwise uses Average and posts RB (review 62). `WINTERS_VERSION` global setting controls inputs | HC/glossary/winters_multiplicative_forecast_method.html |
| Double Exp Smoothing | DES global-setting value + 3 months. Otherwise uses SES and posts RB (review 63) | HC/glossary/double_exponential_smoothing_forecast_method.html |
| Same As Last Year | 12 months. Otherwise uses Average and posts RB | HC/glossary/same_as_last_year_forecast_method.html |
| Average, Linear Regression, Moving Avg, Weighted Avg, SES | 1 month | respective glossary pages |

Conflict: the Demand Detail page says Winters and DES need ≥2 years of history, while Same As Last Year needs ≥1 year (HC/core/core_pid/pid_demand_detail_page.html). SES formula: F(t+1)=αD(t)+(1−α)F(t), F(2)=D(1). `EXP_SMOOTHING_USE_HIST_AVG_BASE` sets base initialization.
Manual Forecast is the only method with no std-dev. It takes the host forecast as given (HC/glossary/manual_forecast_forecast_method.html).

### 1e. History Analysis tab (seasonality)
Src: HC/parts/parts_pid/pid_edit_forecast_parameter_page_history_analysis_tab.html
- **Determine Seasonality**: builds a per-SKU profile when the SKU is seasonal. A profile assigned on the Forecasting tab overrides it.
- **Consider as Group?**: one profile for the whole segment.
- **Output Seasonal Profile? / Output Adjusted History?**: offline output only; slows processing.
- **# of History Slices for History Analysis**.
- **YoY Trend Determination Threshold (%)**: YoY Trend Starting Weight and Weight Decrement default to **2 and 1**, giving weights 2/3 and 1/3.
- **Seasonal Indices Starting Weight / Weight Decrement**: defaults **5 and 2**, giving 5/8 and 3/8 (or 5/9, 3/9, 1/9 over 3 years).
- Seasonal profile page: indices per slice, and **the sum must equal the number of slices** (HC/parts/parts_pid/pid_new_edit_seasonal_profile_page.html).
- A profile has 12 slices (monthly) or 52 (weekly) (HC/glossary/seasonal_profile.html). Indices use ≥1 year and ≤3 years of history. Year weights are 1; 0.6/0.4; 0.5/0.3/0.2 (HC/glossary/seasonal_profile_3.html).

## 2. Streams, stream configuration, netting, pooling, aggregation

| Object / field | Meaning | Src |
|---|---|---|
| Demand Stream: Related Stream | Links internal ↔ external streams | HC/core/core_pid/pid_demand_stream_page_view_new_edit.html |
| Demand Stream: Accumulate | Include in total demand | same |
| Demand Stream: Display On Planner WS, Use In Customer Order Size, Use In Usage Rate, Use In Decay Rate (LTB) | flags | same |
| Forecast Stream: External Indicator | Netting against sales/replenishment orders | HC/core/core_pid/pid_forecast_stream_page_view_new_edit.html |
| Forecast Stream: Type | Composite / Non-Composite | same |
| Forecast Stream: Count In Order Plan | Used by Generate Order Plan. **No** for internal streams of downstream time-phased SKUs or kit component demand. **Yes** for internal streams under Time-Phased ROP | same; HC/glossary/count_in_order_plan_fcst_stream.html |
| Forecast Stream: Count Internal Return Forecast in Order Plan | Internal return forecast feeds the order plan | HC/core/core_pid/pid_forecast_streams_page.html |
| Forecast Stream: Include SD | Stream variance feeds levels, only if Use In Total = Yes | pid_forecast_stream_page_view_new_edit |
| Forecast Stream: Use In Equipment; Non Recurring (load NR adjustments via DD tables) | flags | same |
| Stream Configuration | Name, **# of History Slices**, **# of Forecast Horizon Slices**. Assigned to SKUs through AutoPilot Parameters | HC/core/core_pid/pid_new_edit_stream_configurations_page.html; HC/glossary/stream_configurations.html |
| Stream Config Detail | Demand Stream→Forecast Stream map, default Forecast Method, LLP type (stub/lost, default blank), **Run Best Fit (Recommended / Auto-Approved)**, **Used In Total Forecast**, Demand/Forecast Display, Used in Composite / Replacement Rate, Weight Factor Profile. Method and Best Fit are unavailable for internal streams | HC/core/core_pid/pid_new_edit_stream_configuration_details_page.html |
| Count in Netting (order-level) | Whether an order is included in netting | HC/glossary/count_in_netting.html |
| Used In Forecast | LTB only: whether the profile is evaluated. It is *not* a stream flag | HC/glossary/used_in_forecast.html |

**Time bucket**: AutoPilot Parameter "Forecast Slice Days" is Monthly or Weekly and can only be changed in the DB (all AutoPilot processes must be re-run afterward). "Forecast Start Slice Day" is the weekday a slice starts (HC/parts/parts_pid/pid_ps_page_autopilot_tab.html). Horizon example: monthly site uses 48 = 4 years (HC/glossary/horizon.html). Demand Detail says a 12-month forecast "is best when only viewed a few months out" (pid_demand_detail_page).

**Forecast Netting Parameters** (internal and external variants): HC/parts/parts_pid/pid_new_edit_forecast_netting_parameters_internal_page.html, …_external_page.html

| Field | Meaning |
|---|---|
| Forecast Stream | Net by a single stream or a group of streams |
| Enable Forecast Netting | on/off |
| Enable Network Consumption | Excess demand consumes forecast at other locations in the replenishment hierarchy |
| Consume Orders | No = only demand history (past + current slice) nets |
| Use Demand History or Order Data | Demand History / Closed Orders / Both (needs Consume Orders=Yes) |
| Consumption Date (internal only) | Order date vs ship date picks the slice |
| Consume From Future Slices + Forward Consumption Slices | Forward boundary in slices |
| Use Remaining Forecast | Example: fcst 30, demand 5, half-slice left. Yes gives 25. No gives ((30−5)/30)×15 = 12.5 |
| Rollover Unconsumed Forecast (needs URF=Yes) | Previous-slice leftover rolls into the current slice |
| Enable Backward Consumption (needs URF + Rollover) | Consume prior slice |
| Netting Start / End Date | Default is current slice → end of horizon. Can be overridden at segment and SKU level |

**Forecast Pooling Parameters** (HC/parts/parts_pid/pid_new_edit_pooling_parameter_page.html; HC/glossary/forecast_pooling_parameter.html; HC/glossary/run_forecast_pooling.html)
- Candidate Locations: All Segment / Only Non-ASL / Only ASL.
- Primary Location and Pool Transport Mode.
- **Maximum Slice forecast**: SKUs with forecast ≤ max are pooled; higher-demand SKUs are excluded.
- Dynamic rule rows: the first row met (annual forecast, current slice forecast, or on-hand) picks the pool location. Example: Annual Forecast > 50 picks the location with the largest annual forecast.
- "Run Forecast Pooling" Y/N includes the pooling phase.

**Demand Aggregation / Forecast Disaggregation** (HC/core/core_pid/pid_forecast_disaggregation_page_create_edit.html; HC/glossary/demand_aggregation_and_forecast_disaggregation_2.html)

Fields: Aggregate to Location, Demand Stream, Disaggregation Type **Even / Proportional**, **Disaggregate Slices (blank = 3)** for weight calculation, **Aggregation History Slices (blank = all)**, Is Active, Segments.

Setup: child locations use method "Forecast Disaggregation"; the aggregation location uses a statistical method or Best Fit. Run order is Synchronize Database → Demand Aggregation (not by segment) → Forecasting.

Hierarchy aggregation (separate feature): internal streams sum child external demand and forecast. External demand = historyamount + historyschamount + historycopyamount. When forecast aggregation is used, netting must be disabled on internal streams (HC/core/core_topics/demand_and_forecast_aggregation.html).

**Copy Demand** (HC/parts/parts_pid/pid_new_copy_demand_history_page.html)
- Demand Percentage (%): 100 copies everything.
- Refresh Type Full (begin→end) or Partial (last run→end).
- Source Action: Copy / Move. Destination Action: Add / Replace. Each side has its own date range.
- Copied values appear on a "Copy Demand" row. The AutoPilot process is "Copy Demand".

## 3. Adjustments, overrides, production

- **Demand Detail rows** (HC/core/core_pid/pid_demand_detail_page.html):
  - History side: Demand (includes rolled-up down-chain demand), Adjustment, Non-Recurring, Copy Demand, Seasonal Profiles, Deseasonalized History = Demand/Index, Total.
  - Forecast side: Forecast, **Scheduled** (user or profile adjustment that does not alter history), **Non-Recurring**, Returned/Repaired/NFF, Total Net Forecast.
- **Non-recurring back-out rules** (HC/core/core_topics/overview_of_demand_forecasting.html). Example with calc fcst 10 and NR adj 50:
  - Actual 75 backs out 50.
  - Actual 45 backs out 35.
  - Actual 6 backs out 0.
- **Forecast Adjustment Profiles** (HC/parts/parts_pid/pid_additional_data_forecast_adjustment_profile_details.html):
  - Fields: Start/End Date, Value, assigned to multiple external Forecast Streams and Segments.
  - Operations map to ForecastSchAmount:
    - Replace: Value − Fcst.
    - Inc Value: +Value.
    - Dec Value: −Value.
    - Inc %: Fcst×V/100.
    - Dec %: −Fcst×V/100, with 0 ≤ V ≤ 100.
  - Value ≥ 0.
- **Annual Override** (Forecast WS, SKU-stream):
  - The difference between Annual Raw Forecast and the override is spread over the next 12 periods, weighted by the raw forecast.
  - From-only means it never expires.
  - From+To applies the override in rolling 12-month windows, one starting in each month of the range (HC/parts/parts_smart_help/sh_ipws_forecast_demand_forecast_container_annual_override.html; HC/release_notes/release_13_1_0_0/rn_enhancements_fcst_4.html).
- **Annual Forecast**: next 12 months including scheduled/NR adjustments. Used in EOQ (HC/glossary/annual_forecast.html).
- **Override expiry flags**: Past Override = end date passed; Current Period Override = active now; Future Override = applies in future (HC/glossary/past_override.html, current_period_override.html, future_override.html). These are SKU-override indicators, not forecast-specific.
- **Demand Satisfaction Override**: manual override of the calculated Demand Satisfaction value (HC/glossary/demand_satisfaction_override.html).
- **Make Forecast Production**: the approved forecast is made production. Forecast Review splits the total into Total Production Forecast and Total Recommended. The Review Process uses the recommended forecast (HC/glossary/autopilot_processes_8.html; HC/core/core_topics/overview_of_forecast_review.html).
- **Post Forecast**: updates Annual Demand and Forecast SD in forecast detail. Governed by `RUN_POST_FORECAST` (autopilot_processes_8).
- **Other AutoPilot processes** (autopilot_processes_8):
  - Demand History Management does categorization and outlier adjustment, and is required before Best Fit/Causal.
  - Forecasting-Calculate Metrics (auto-run if `RUN_CALCULATE_METRICS_WITH_FORECAST`).
  - Forecasting Database Cleanup removes stale Best Fit overrides when Run Best Fit changes from Auto-Approved. It falls back to the user method, then the stream default.
- **Forecast-change review** (AutoPilot Parameter): Forecast Monitor Slice 1–3 × Percent Change 1–3 × Forecast Minimum 1–3 give review types 4–6. Review types 1–3 cover actual vs forecast outside N·SD (Review Slices/Limit 1–3) (HC/parts/parts_pid/pid_ps_page_autopilot_tab.html; HC/glossary/review_reason.html).
- **Tracking-signal reviews 138/139**: Parameter 1 default is ±0.5 when `TRACKING_SIGNAL_NORMALIZED`=true (default), ±4 otherwise (HC/glossary/review_reason_2.html).
- **Over/Under Consumed Forecast**: reviews 92 and 111 (review_reason_2).

## 4. Supersession / part chains

| Item | Meaning | Src |
|---|---|---|
| Part Chain | Up-chain = newer revision. Global Y/N, or location-specific | HC/glossary/part_chain.html; HC/core/core_pid/pid_new_edit_part_chains_page.html |
| Relation Type | **Replace**: down-chain part not planned and removed from ASL; stock can roll up (two-way compatibility). **Alternate**: one-way, newer serves older after burn-off | HC/glossary/relation_type.html |
| Part Relationship Type | Prime / Alternate / Replaced | HC/glossary/part_relationship_type.html |
| Roll Up Demand Percent | % of down-chain demand added to up-chain. When < 100%: Replace drops the remainder, Alternate keeps it at the down-chain part | HC/core/core_pid/pid_part_chain_details_page_parts_tab.html; HC/glossary/roll_up_demand_percent.html |
| Roll Up Good / Good As Bad / Bad | Down-chain stock counted as up-chain good, up-chain bad, or bad→bad. Replace only | HC/glossary/roll_up_good.html, roll_up_good_as_bad.html, roll_up_bad.html |
| ASL Retention Min Inventory / Min Forecast | Alternate parts: recommend ASL removal below threshold | parts_tab |
| Part Chain Depth / Index | Hierarchy level / unique index | HC/glossary/part_chain_depth.html, part_chain_index.html |
| TMR | Top Most Revision, the parent part. Causal forecasts TMR only | HC/glossary/top_most_revision.html; HC/glossary/causal_forecast_method.html |
| Future Part Chains | `FUTURE_PART_CHAINS`=true. Effective Date = Available Date − Lead Time − Buffer Days; the part joins the chain at Sync DB | HC/glossary/part_chain_2.html |
| Run Supercession Changes | Merges child SKU overrides into the TMR (max of mins, min of maxes, min of fixed) and ends child overrides yesterday. Child ROP = −1; child demand/variance not updated; child Part Relationship Type = 0. Sums child daily forecast etc. into the TMR | HC/glossary/autopilot_processes_8.html |
| Part Transition | Linear bleed-down of forecast from old part to new part between Transition Start and End Date. Periodic Review + Review Period (days) give **review 50 "Part in Transition"**. Informational only; the planner must replace the part manually | HC/parts/parts_topics/overview_of_part_transitions.html; creating_part_transitions.html; HC/glossary/review_reason_2.html |
| Like Part / Like Location | Borrow history for a new part or location | HC/glossary/like_part.html, like_location.html |
| Demand Incr Factor | Borrowed history × %. 100% = unchanged. Example: 75% for a new drive with 75% failure rate. Exists on both Part and Location | HC/core/core_pid/pid_new_edit_parts_page.html; pid_new_edit_location_page.html |

## 5. Installed base / causal / leading indicators

- **Causal forecast**: BOM-based forecast at all BOM levels.
  - Formula: Current Effective Total Population × Σ(CausalValue × FailureRate × WeightFactor), or (RolloutAmt × BOM Qty × AttachRate) × Σ(…).
  - With no part_causal_type row: (Rollout × BOMQty × Attach) × FailureRate.
  - All rollout, failure-rate, contract and causal dates must be on the first day of a slice.
  - Replaced-part population rolls to the TMR; Alternates are standalone.
  - Src: HC/glossary/causal_forecast_method.html
- **Host vs calculated failure rate**:
  - `UseHostFailureRate`='y' forces the host rate. Otherwise the calculated rate is used only when all three are met:
    - `FAILURE_RATE_MIN_CUM_CAUSAL`, default **1,000**.
    - `FAILURE_RATE_MIN_CUM_POPULATION`, default **30**.
    - `FAILURE_RATE_MIN_DEMAND_PERIODS`, default **0**.
  - Src: HC/glossary/causal_forecast.html
- **Effective Failure Rate**:
  - Host + override, with operations Replace / ±Value / ±%.
  - `CF_USE_MTBF_FOR_FAILURE_RATE` switches to MTBF (MTBF = 1/FR).
  - The host FR wins if both FR and MTBF are given.
  - Failure-rate record fields include Calculation Slices, Cumulative Part Population, Cumulative Causal Value and Threshold Met.
  - Src: HC/core/core_pid/pid_failure_rate_detail_page_fields.html
- **Workflow**:
  1. Product rollouts and causal values.
  2. Part causal types (Part + Forecast Stream + Causal Type + Weight Factor, e.g. flight hours or landings).
  3. Failure rate / MTBF (keyed by Part, Product, Contract, Location, Causal Type).
  4. Product BOM (Included Part Qty, Attach Rate, Start/End).
  5. Multi-level BOM Sync DB (needed after a BOM change) → Causal Forecast Detail → Forecasting.
  - Src: HC/glossary/causal_forecast_2.html; HC/core/core_pid/pid_create_edit_causal_forecast_product_bom_page.html; HC/core/core_pid/pid_new_edit_part_causal_type_page.html
- **Causal Forecast Scenario**: Name + Forecast Stream. Used by IO when Forecast Type = Causal Forecast Scenario, and by the History Based Simulator (None / Scenario / Production) (HC/glossary/causal_forecast_scenario.html, causal_forecast_type.html).
- **Failure-rate reviews** (need `ENABLE_CF_FR_REVIEW`=true):
  - 342 first calculated.
  - **343 change > `FR_CHANGE_ALERT` (default 20%)**.
  - 344 zero.
  - Src: HC/glossary/review_reason_2.html
- **Install Base**: Product, Install Site, Contract Type, Begin Date, auto End Date (latest record is null), Amount, Serial No, Include in Network Optimization. Used by Leading Indicators and Network Optimization (HC/core/core_pid/pid_new_edit_install_base_page.html; HC/glossary/install_base.html).
- **Average Population** (IO): average rollout × part qty per unit (HC/glossary/average_population.html).
- **Leading Indicators** (PTC recommends Causal instead). Src: HC/glossary/leading_indicators_forecast_method.html; HC/core/core_pid/pid_new_edit_parts_page.html
  - Forecast = installed parts × usage rate.
  - Calculated Usage Rate = slice global demand / (Effective + Accumulated Part Population) × 100. Example: 10/5000 = 0.2%.
  - Smooth Usage Rate weights are **80% previous / 20% slice**, and a global setting can change them.
  - Override Amount/Date, MTBF with Usage Hours Per Month (**default 720**), Part Type Default Usage Rate ("1 in N").
  - Reviews 41–46 (Lifecycle): 41 cannot calculate, 42 last-month rate too high/low, 43 first auto-calc, 44 change exceeds limit, 45 accumulated population too high, 46 zero usage rate. **The numeric limits for 42/44 were not found in the corpus (UNVERIFIED; likely Review Parameter 1/2).**

## 6. NPI (new part introduction)
- Initial Provisioning and Re-Provisioning methods are **no longer supported since 12.0.0.0**. They remain only for existing users (HC/core/core_topics/initial_provisioning_forecast_method.html; HC/core/core_topics/re_provisioning_forecast_method.html).
- Provision Forecasting was removed; PTC says to use Causal Forecasting instead (HC/parts/parts_topics/overview_of_provision_forecasting.html).
- Current NPI tools:
  - Like Part / Like Location × Demand Incr Factor (§4).
  - Use Phase In Date.
  - Leading Indicators or Causal (population-based).
  - Lifecycle Forecast Seed Stock: Strategic Locations / Deployment Cycle spread per slice, e.g. 101/4 gives 25, 25, 25, 26 (HC/parts/parts_topics/calculating_initial_demand_forecast.html).
  - PAI ML "New Part Introduction": similar-part matching on numeric and text attributes, then an ensemble forecast; outputs RMSE/MAPE on a validation set (HC/glossary_pai/machine_learning_based_new_parts_forecasting.html; HC/functional/dashboard_new_part_introduction_forecasting.html).

## 7. Returns forecasting
Returned, Repaired and NFF rows appear only for repairable parts (HC/core/core_pid/pid_demand_detail_page.html):
- Returned = Fcst × (1 − Return Wash Rate) × (1 − NRTS).
- Repaired = Returned × (1 − NFF) × (1 − Repair Wash Rate).
- NFF row = Returned × NFF Rate.

Rates and flags:
- Return Wash Rate glossary gives Returned = Fcst × (1 − RWR); global settings may alter it (HC/glossary/return_wash_rate.html).
- Repair Wash Rate example: 10% means 11 bad units are needed for 10 good (HC/glossary/repair_wash_rate.html).
- NFF Rate: share of returns usable as good without repair (HC/glossary/no_fault_found_rate.html).
- `ENABLE_NRTS` models local condemnation at two points: return (RWR) and after local repair (RpWR). With NRTS off, Condemnation Rate appears only at the root location as a blended scrap rate (HC/glossary/not_repairable_this_station_2.html; HC/glossary/condemnation_rate.html).
- Repairable Interval Local vs Network Forecast (IO). Example: 10 demand with NRTS 40% gives 6 local and 4 at the parent (HC/glossary/repairable_interval_local_forecast.html, repairable_interval_network_forecast.html).
- **NFF for Consumables**: needs `APPLY_RETURN_WR_AND_NFF_TO_CONSUMABLES`=true (default false) plus `ENABLE_NRTS`=true. Set RWR=0 where no returns are expected. For non-repairable SKUs: RpWR = 100%, NRTS = 0, Consumable flag visible. The NFF rate is not applied to the internal rolled-up forecast. EOQ is affected (HC/glossary/no_fault_found_for_consumables.html, _2, _3).
- `APPLY_NFF_TO_INT_RETURN_FCST` (default true): NFF is also applied to the internal return forecast (HC/glossary/global_settings_fcst.html).
- `RETURN_WR_NON_REPAIR_LOC` (default false): use the non-repairable child's RWR when an ancestor part is repairable (HC/glossary/global_settings_general.html).

Supply Planning settings (HC/glossary/global_settings_sp.html):
- `RETURN_FORECAST_UNTIL_RETURN_LT` (default true): counts sales returns, not the return forecast, until return LT.
- `RETURNS_THROUGH_HORIZON` (default true).
- `RETURNS_STARTING_ON_DAY2` (default false).

Other:
- Time-phased ROP daily inventory includes good/bad from sales returns plus the return forecast (HC/glossary/time-phased_rop.html).
- The History Based Simulator "Create Sales Return Over Period" option is Auto / History / Forecast / None (HC/glossary/create_sales_return_over_period.html).

## 8. Other material facts
- Setup order: Demand Stream → Forecast Stream → import history (SKU-stream) → Stream Config + Details → AutoPilot Param assigns config to segments → Forecast Parameters → run Sync DB + Forecasting + Forecast Netting (HC/core/core_topics/forecasting_configuration.html).
- `DELETE_DO_NOT_FORECAST` (default false) deletes future forecasts for the Do Not Forecast method (HC/glossary/global_settings_fcst.html).
- Demand Detail aggregation settings: `DEMAND_DETAIL_AGGREGATION_SLICES/_BY_SLICE/_MODE` (autopilot_processes_8).
- Demand bins (Bin Type = d) are not forecast; their demand rolls to the parent location (HC/core/core_pid/pid_new_edit_location_page.html).
- History SD = sample SD formula. Scaled % = (HistSD/HistAvg) × FcstAvg. History % Error = HistSD/HistAvg × 100 (pid_demand_detail_page).
- Winters Additive exists as a flag but is unused. Initial/Re-Provisioning are legacy. Our design should not replicate either (**UNVERIFIED recommendation**).
