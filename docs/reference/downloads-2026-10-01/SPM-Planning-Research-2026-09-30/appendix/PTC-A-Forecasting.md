PTC SERVIGISTICS 13.x: DEMAND PLANNING / FORECASTING NOTES
(from the local crawl at scratchpad/spm/ptc/txt)

URL CONVENTION: B = https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/
Every fact below is followed by [B + path]. Formulas that the help renders as images (the MAD, RMSE and Composite Error formulas for Best Fit and Demand) were NOT captured in the text crawl. Where only a textual definition exists, that is noted.

======================================================================
0. MENU STRUCTURE AND UI PAGE NAMES PLANNERS USE
======================================================================
Menus
- Forecasting > Analysis > Actions: Best Fit, Copy Demand, Forecast Adjustment Profiles, Forecast Analysis [B core/core_topics/module_forecast_analysis_actions.html]
- Forecasting > Analysis > Review: Demand Detail, Demand Summary, Forecast Review, Interactive Planner Worksheet (Forecast tab = "Forecast Worksheet") [B core/core_pid/pid_demand_detail_page.html; B parts/parts_pid/pid_forecast_review_fields.html; B parts/parts_pid/pid_ipws_forecast_forecast_metrics.html]
- Forecasting > Forecasting Configuration > Streams: Composite Weight Factor Profiles, Demand Streams, Forecast Streams, Seasonal Profiles, Stream Configuration [B core/core_topics/module_forecast_configure_streams.html]
- Forecasting > Forecasting Configuration > Parameters: AutoPilot Parameters, Forecast Netting Parameters, Forecast Parameters, Forecast Disaggregation [B core/core_topics/module_forecast_configure_parameters.html]
- Forecasting > Forecasting Configuration > Products: Products, Product BOMS, Product Groups, Product Lines, Product Types [B core/core_topics/module_forecast_configure_products.html]
- Forecasting > Forecasting Configuration > Install Bases: Contract Types, Install Bases, Install Sites, Stocking Coverages [B core/core_topics/module_forecast_configuration_install_base.html]
- Forecasting > Causal:
  - Production pages: Causal Forecast Product BOM
  - Scenario pages: Causal Forecast Scenario, Causal Forecast SKU Summary
  - Pages for either Production or Scenario: Causal Forecast Detail, Failure Rate Detail, Failure Rate Summary, Product Rollout and Causal Value, Product Rollout and Causal Value Detail
  [B core/core_topics/module_forecast_causal.html]
- Forecasting > Events: Event Coverage, Event Product BOM, Event Schedules, Events [B core/core_topics/module_forecast_events.html]
- Forecasting > Life Limited Parts (includes the Life Limited Parts Forecast Details page) [B core/core_topics/module_forecast_life_limited_parts.html; B release_notes/release_13_0_1_0/rn_enhancements_fcst_3.html]
- Forecasting > Replacement Rate: Replacement Rate, Replacement Rate Details [B core/core_topics/replacement_rate.html]
- Other pages:
  - Best Fit Management (pop-up), Best Fit Detail [B core/core_pid/pid_best_fit_management_page.html]
  - Adjust Demand History, Adjust Scheduled Forecast, Adjust Non-Recurring Forecast [B core/core_topics/adjusting_demand_or_forecasts_from_the_demand_page.html]
  - Forecast page (filter/results) [B parts/parts_pid/pid_forecast_page.html]
  - Part Properties (Part Forecast / Part Demand tabs) and Location Properties (Location Forecast tab) [B core/core_topics/overview_of_forecast_review.html]
  - Review Board [B glossary/review_board.html]
  - Parameter Settings (Forecasting and Forecast Netting tabs) [B parts/parts_pid/pid_ps_page_forecast_netting_tab.html]
  - LI Forecast Details [B parts/parts_pid/pid_li_forecast_details_page.html]
  - Lifecycle Forecast (tabs: Seed Stock, Normal, Adjustment, Total) [B parts/parts_topics/calculating_initial_demand_forecast.html]
  - Last Time Buy Forecast [B parts/parts_pid/pid_last_time_buy_forecast.html]
- PAI dashboards:
  - Forecast Performance: Forecast Analysis, Forecast Error Analysis, SKU/Part/Location Forecast Analysis, Forecast Override Analysis
  - Forecast Intelligence: Forecast Accuracy Intelligence, Forecast Override Recommendations, ML Time Series Forecasting, ML New Parts Forecasting, Multivariate SKU Forecast Analysis, New Part MTBF Prediction, Region MTBF, Remaining Useful Life, Correlated Parts
  [B functional/menu_forecast_intelligence.html; B functional/menu_forecast_performance.html]

Configuration workflow
1. Create a Demand Stream.
2. Create a Forecast Stream.
3. Import demand history at the SKU-stream level (Data Manager/Import).
4. Create a Stream Configuration and its Details.
5. Assign the Stream Configuration to segments through AutoPilot Parameters.
6. Create or edit Forecast Parameters and assign segments.
7. Run AutoPilot: Synchronize Database, then Forecasting, then Forecast Netting.
8. View the results on Demand, Demand Summary and Interactive Planner Worksheet (IPWS) Demand/Forecast.
[B core/core_topics/forecasting_configuration.html]

Planner process when Forecast Review is enabled
1. Run Best Fit
2. Run Forecasting
3. Review and adjust
4. Run IO Calculation
5. Run Forecast Make Production
6. Run Forecast Netting
7. Run IO Make Production
[B core/core_topics/overview_of_forecast_review.html]

======================================================================
1. FORECAST METHODS (FULL LIST)
======================================================================
Official list: Average, Causal, Composite, Croston, Do Not Forecast, Double Exponential Smoothing, Forecast Disaggregation, Intermittence Smoothing, Leading Indicators, Life Limited Parts, Linear Regression, LLP Maintenance – Raw, LLP Maintenance – Smooth, Manual Forecast, Moving Average, Replacement Rate, Same As Last Year, Scheduled Event Maintenance, Single Exponential Smoothing, Servigistics ML, Servigistics ML Composite, Servigistics TSB, Weighted Average, Winters Multiplicative [B glossary/forecast_method.html]
- "Each forecast method has constraints, called best fit rules that may make it ineligible for forecasting." [B glossary/forecast_method.html]

Time-series grouping [B glossary/time_series_forecasting.html]
- Constant profile: Average, Weighted Average, Moving Average, SES
- Trend: DES, Same As Last Year, Linear Regression
- Seasonal: Winters Multiplicative
- Intermittent: Intermittence Smoothing, Croston, Servigistics TSB
- Other: Manual Forecast, Do Not Forecast

Minimum history and fallback summary
| Method | Min history | Fallback / notes |
|---|---|---|
| Average | 1 month | best with no trend; averaging "dampens trends" [B glossary/average_forecast_method.html] |
| Weighted Average | 1 month | flat forecast [B glossary/weighted_average_forecast_method.html] |
| Moving Average | 1 month | [B glossary/moving_average_forecast_method.html] |
| Linear Regression | 1 month | y = mx + b [B glossary/linear_regression_forecast_method.html] |
| SES | at least 1 month | flat-line forecast [B glossary/single_exponential_smoothing_forecast_method.html] |
| DES | INIT_EXPSMOOTHING_MONTHS (the "Double Exponential Smoothing global setting") + 3 months | below that, uses SES and posts a Review Board record [B glossary/double_exponential_smoothing_forecast_method.html; B glossary/best_fit_analysis_2.html] |
| Croston | 12 months | below that, uses SES and posts a Review Board record [B glossary/croston_forecast_method.html] |
| Same As Last Year | 12 months | below that, uses Average and posts a Review Board record [B glossary/same_as_last_year_forecast_method.html] |
| Winters Multiplicative | 12 months | below that, uses Average and posts a Review Board reason [B glossary/winters_multiplicative_forecast_method.html] |
| Leading Indicators usage rate | one full month of non-zero install base and non-zero central demand | [B glossary/leading_indicators_forecast_method.html] |

- Conflicting statement: the Demand Detail page says "Winters and double exponential forecast methods require at least 2 years of history slices. Same as Last Year… at least one year." [B core/core_pid/pid_demand_detail_page.html]
- The Best Fit page says: "Winters Multiplicative, Croston, and Same As Last Year… require at least one year of history slices." [B core/core_pid/pid_best_fit_detail_page.html]
- Related Review Board reasons: 62 "Insufficient data for Winters Multiplicative Method", 63 "Insufficient data for Double Exponential Smoothing", 64 "Insufficient data for Croston Forecast Method" ("…create Croston forecast using single exponential smoothing") [B glossary/review_reason_2.html]

1.1 Average
- "uses the average of a number of historical periods… best used when there is no trend." Forecasting more than one period ahead "is suspect if there is any upward or downward trend." [B glossary/average_forecast_method.html]
- Parameters: "# of History Slices Average"; "Maximum # of History Slices [For Average Forecast Method]" [B parts/parts_pid/pid_forecast_parameters_page.html]

1.2 Weighted Average
- "assigns more importance (weight) to the most recent periods… weight is assigned depending upon the number of historical slices." It "responds to trends more quickly than a Moving Average forecast, but the result is still a flat forecast." [B glossary/weighted_average_forecast_method.html]

1.3 Moving Average
- "weighted average of the last n slices." Example with n = 3: (H1×3 + H2×2 + H3×1) ÷ (1+2+3). [B glossary/moving_average_forecast_method.html]
- Hybrid behaviour: weight factor 0 behaves like Average; weight factor 1 behaves like Weighted Average. [B glossary/moving_average_forecast_method.html]
- Parameters: "# of Slices" and "Weight" (a value between 0 and 1 inclusive) [B core/core_pid/pid_best_fit_detail_page.html]
- Parameter "Weight factor to apply to moving average" [B parts/parts_pid/pid_new_edit_forecast_parameter_page_forecasting_tab.html]

1.4 Linear Regression
- "simplest forecast method for recognizing trends… slope… intercept… y = mx + b." [B glossary/linear_regression_forecast_method.html]

1.5 Single Exponential Smoothing (SES)
- F(t+1) = α·D(t) + (1–α)·F(t), with F(2) = D(1) and t = [2, # History Slices] [B glossary/single_exponential_smoothing_forecast_method.html]
- α is in [0,1]. A higher α gives more weight to recent slices but more month-to-month variation. Use when trend and seasonality are not significant. [same URL]
- Default α = 0.1000 (Exponential Smoothing section) [B parts/parts_pid/pid_new_edit_forecast_parameter_page_forecasting_tab.html]
- Base initialization is controlled by EXP_SMOOTHING_USE_HIST_AVG_BASE:
  - true: the history average initializes the base ("more consistent forecasts over time")
  - false: the first slice initializes the base
  - Default: true for new installs, false for upgrades
  [B glossary/global_settings_fcst.html]

1.6 Double Exponential Smoothing (DES)
- "smooths the old average and the new average together… computes the base trend using α and β." Use when seasonality is not significant. [B glossary/double_exponential_smoothing_forecast_method.html]
- Accepts the trend-dampening constant φ (phi): "The smaller phi is, the more the trend value will be dampened. If phi = 1, then no trend dampening occurs." [same URL; B core/core_pid/pid_best_fit_detail_page.html]
- Defaults: α = 0.1000, β = 0.0500, φ = 0.7000 [B parts/parts_pid/pid_new_edit_forecast_parameter_page_forecasting_tab.html]
- Best Fit also requires TotalDemandSlices ≥ 5 (soft rule) [B glossary/best_fit_analysis_2.html]

1.7 Winters Multiplicative
- Handles "level, trend, and seasonality." A seasonal index is "updated monthly" per slice, and each index is smoothed. There are three smoothing equations (level, trend, seasonality), and an initialization method generates the initial values. [B glossary/winters_multiplicative_forecast_method.html]
- Defaults: α = 0.1900, β = 0.0530, γ = 0.5 [B parts/parts_pid/pid_new_edit_forecast_parameter_page_forecasting_tab.html; B glossary/gamma.html]
- WINTERS_VERSION global setting (default 3) [B glossary/global_settings_fcst.html]:
  - 1 = do not consider α, β, γ
  - 2 = consider α, β, γ
  - 3 = consider α, β, γ and "use the full year in the # of History Slices"
- Each Winters SKU "uses a private seasonal profile on an ongoing basis." [B glossary/seasonal_profile.html]
- Best Fit elimination (hard rules): LastYearAverage < 2; stream-config history < 12; history < 12; history < minWintersHist; "Not seasonal – Auto correlation test failed." [B glossary/best_fit_analysis_2.html]

1.8 Same As Last Year
- "uses the demand value for the same slice from the previous year. A trending parameter can be applied."
- Needs 12 months; otherwise falls back to Average with a Review Board record.
[B glossary/same_as_last_year_forecast_method.html]
- Parameter "Trend % to apply to last year demand", default 0.0000 [B parts/parts_pid/pid_new_edit_forecast_parameter_page_forecasting_tab.html]

1.9 Croston
- Designed for "intermittent and erratic demand." It forecasts (a) the interval between events and (b) the size of each event. The two are assumed independent and "generally forecasted using exponential smoothing." No seasonality is assumed. [B glossary/croston_forecast_method.html]
- Initialization uses the whole initial dataset to produce forecast size, interval and SD. After that, "the intermediate values for demand size (set by the crostons_alpha global setting), interval standard deviation, and demand size standard deviation are updated… after each non-zero demand period." [same URL]
- Parameters, section "Croston (Intermittence)":
  - Alpha "smooth the level or the base and Periods Between Demand", default 0.1000
  - Omega "smoothing equation for updating history standard deviation", default 0.1000
  [B parts/parts_pid/pid_new_edit_forecast_parameter_page_forecasting_tab.html]
- Outlier adjustment is not applied to SKUs using the Croston (or Leading Indicator) method [B glossary/outlier_adjustment.html]

1.10 Intermittence Smoothing
- "combination of the Croston and Single Exponential Smoothing": when demand is intermittent it produces "a modified Croston forecast"; otherwise it behaves "much like Single Exponential Smoothing." [B glossary/intermittence_smoothing_forecast_method.html]
- "Use this method as the default forecast method for those streams where a lack of data does not allow for the use of Best Fit." [same URL]
- Parameter: Alpha only [B core/core_pid/pid_best_fit_detail_page.html]

1.11 Servigistics TSB (Teunter-Syntetos-Babai), new in 13.0.1.0
- Designed for intermittent items. It "replaces the demand interval in the Croston forecast method with demand probability, which is updated every period." [B glossary/servigistics_tsb_forecast_method.html]
- Parameters: Alpha "smoothing parameter for demand level" (default 0.3000); Beta "smoothing parameter for demand occurrence" (default 0.1000) [B parts/parts_pid/pid_new_edit_forecast_parameter_page_forecasting_tab.html]
- The old setting "Use Intermittence Smoothing Instead of Crostons" was removed and replaced by "Select Forecast Method for Intermittent Demand" (Intermittent Smoothing / Croston / Servigistics TSB). "Allow Servigistics TSB" was added to the Best Fit methods. [B release_notes/release_13_0_1_0/rn_enhancements_fcst_4.html]

1.12 Manual Forecast
- "does not perform any forecast calculations. It adopts and displays the forecast provided by the host system."
- "does not calculate standard deviation. All other forecast methods do."
[B glossary/manual_forecast_forecast_method.html]

1.13 Do Not Forecast
- Creates no forecast detail records, and no history average or SD. "Select this method for streams that have been created for the purpose of displaying demand to planners." [B glossary/do_not_forecast_forecast_method.html]
- DELETE_DO_NOT_FORECAST (default false) controls whether future forecast records are deleted during Forecasting or Interactive Plan [B glossary/global_settings_fcst.html; B release_notes/release_13_0_0_0/rn_enhancements_fcst_2.html]
- When first assigned, it can leave residual records that must be cleaned up [B glossary/do_not_forecast_forecast_method.html]

1.14 Causal (BOM / install-base; recommended over Leading Indicators and LLP)
- "BOM based forecasting of parts at all levels in the BOM… forecasts failure rates… using historic demand and installed base. Global failure rate is calculated based on installed base and causal factors, while higher weight is given to recent installed base and failures using exponential smoothing." [B glossary/causal_forecast_method.html]
- Formulas:
  - Current Effective Total Population × Σ(Causal Value × Failure Rate × Weight Factor)
  - (Product Rollout Amount × BOM Quantity × Attach Rate) × Σ(Causal Value × Failure Rate × Weight Factor)
  - With no part_causal_type record: (Rollout × BOM Qty × Attach Rate) × Failure Rate
  - Causal Value and Weight Factor are optional.
  [same URL]
- Forecasts the top-most part only. "Population and/or causal values of replaced parts are rolled over to the top most part. Alternates are treated as standalone parts." [same URL]
- All start/end dates (rollouts, failure rates, contracts, causal values) must fall on the first day of a slice. [same URL]
- Total Causal Value = Product Rollout Amount × BOM Qty × Attach Rate × Primary Causal Value. The primary causal type is the one with the highest weight factor. MTBF = 1 / Failure Rate. [B core/core_pid/pid_causal_forecast_detail_page.html]
- Host vs calculated failure rate:
  - UseHostFailureRate = 'y' in IPCS_PART_MASTER forces the host rate.
  - Otherwise a rule-based cut-over to the calculated rate happens when all of these thresholds are met:
    - FAILURE_RATE_MIN_CUM_CAUSAL (default 1,000; can be overridden per CAUSAL_TYPE)
    - FAILURE_RATE_MIN_CUM_POPULATION (default 30)
    - FAILURE_RATE_MIN_DEMAND_PERIODS (default 0)
  [B glossary/causal_forecast.html]
- Effective Failure Rate = Host + Override (operations: Replace, Increase/Decrease by Value, Increase/Decrease by Percent) or the Calculated rate. CF_USE_MTBF_FOR_FAILURE_RATE switches the logic to MTBF. If both Host Failure Rate and Host MTBF exist, the Host Failure Rate is used. [B core/core_pid/pid_failure_rate_page.html]
- Workflow:
  1. Set product rollouts and causal values.
  2. Set part causal types (weights).
  3. Set failure rates/MTBF.
  4. Set product BOMs (qty, attach rate).
  5. Run Multi-level BOM Synchronize Database (if BOMs changed), then Causal Forecast Detail, then Forecasting.
  6. Review on Demand Summary, Demand Detail and Causal Forecast Detail.
  [B glossary/causal_forecast_2.html]
- Product BOM Causal fields: Weight Factor, MTBF, MTBR, MTBUR, MTBx Used, Causal Coefficient (overrides the others when not null), Quantity, Attach Rate, Line Scrap Rate, Replacement Repair Rate, Line Repair Rate [B parts/parts_pid/pid_product_bom_causal_page.html]
- Part Causal Type: associates a part with a forecast stream, a causal type and a weight, e.g. flight hours or landings [B glossary/part_causal_type.html]
- Causal scenarios: Forecast Type options are Production / Recommended / Causal Forecast Scenario (Recommended exists only when ENABLE_FORECAST_APPROVAL is true) [B glossary/forecast_type.html]
- Review types (enabled by ENABLE_CF_FR_REVIEW):
  - 342 Failure rate calculated for first time
  - 343 Failure rate change exceeds limit (FR_CHANGE_ALERT, default 20%)
  - 344 Failure rate zero
  [B glossary/review_reason_2.html]

1.15 Leading Indicators (legacy; "recommended that you use Causal Forecasting")
- Forecast = installed part quantity × usage/failure rate. Can estimate from a similar part. Needs the install site/base, product BOM and usage/failure rate. [B glossary/leading_indicators_forecast_method.html]
- Usage rate smoothing: previous rate 80%, current slice 20% by default [same URL]. Part flag "Smooth Usage Rate - 80/20(%)" [B core/core_pid/pid_parts_page.html]
- Formulas:
  - Forecast Amount = (FPP/30 × #Days in Slice) × (Usage Rate/100) × Avg(Attach Rate/100) × Percent Coverage
  - FPP = Σ(Future Install Base by Slice/30 × #Days) × BOM × P Factor × Avg(Attach Rate/100) × Percent Coverage
  - EPP = Σ per product (Install Base/30 × #Days) × BOM × P Factor
  - Usage Rate 50 means 1 in 50 parts fails per slice
  [B parts/parts_pid/pid_li_forecast_details_page.html]
- Slice MTBF = Usage Hours Per Month (default 720) / (demand / EPP) [B core/core_pid/pid_demand_detail_page.html]
- Review types: 41–46 (cannot auto-calc usage rate; last month rate too high/low; first auto-calc; change exceeds limit; accumulated EPP too high; no usage rate for an LI SKU) [B glossary/review_reason_2.html]

1.16 Replacement Rate
- Forecasts a component from repairs of its parent assembly: Forecast = Replacement Rate × Repair Rate × Parent Total Forecast (internal + external) [B glossary/replacement_rate_forecast_method.html]
- Repair Rate = ((1–ReturnWashRate)(1–RepairWashRate)(1–NffRate)) + ((1–ReturnWashRate)·NffRate) [same URL]
- For Multi-Indenture Optimization SKUs, SDs are NULL. Otherwise ForecastErrorSD = Sqrt(Σ(Demand(i)–Forecast(i))² / (N–1)). [same URL]
- FCST_REP_RATE_USE_PARENT_SD: when true, History/Forecast/Forecast-Error SD are derived from the parent's SD and the replacement rate. Default true for new installs, false for upgrades. [B glossary/global_settings_fcst.html; B release_notes/release_13_1_0_2/rn_enhancements_fcst_2.html]
- Stream config flag "Used in Replacement Rate Forecasting" [B core/core_pid/pid_new_edit_stream_configuration_details_page.html]

1.17 Scheduled Event Maintenance
- "uses a schedule of events with known part usage rates to create a dependent demand forecast" (A&D). Upstream rollup is done through Related Stream ID; the rollup stream uses External Indicator = n and the SEM stream uses External Indicator = y. [B glossary/scheduled_event_maintenance_forecast_method.html]
- The Scheduled Event Detail process (ProcID 1208) must run before Forecasting [B glossary/autopilot_processes.html]
- Event schedule: one per install site [B glossary/event_schedule.html]

1.18 Life Limited Parts / LLP Maintenance – Raw / LLP Maintenance – Smooth
- LLP (legacy): uses historical flight hours/cycles and the maximum hours/cycles before a service event is required. Forecast types are lost or stub life (Stream Config "Life Limited Parts Forecast Type"). [B glossary/life_limited_parts_forecast_method.html; B core/core_pid/pid_new_edit_stream_configuration_details_page.html]
- MF_SKU_FORECAST_ALLOC_METHOD controls how the serial-number forecast is allocated to SKUs:
  - 0 = the part/location on the serial record
  - 1 = allocation percentages in IPCS_MF_SKU_FCST_ALLOC
  [B glossary/global_settings_fcst.html]
- LLP Maintenance – Raw: need based on scheduled maintenance.
- LLP Maintenance – Smooth: smooths the raw need to maintenance-center capacity. Excess is pulled back to earlier slices, and any remainder goes into the earliest forecast slice.
- New in 13.0.1.0: the Maintenance Forecast Detail AutoPilot process (forecast at serial, SKU and part level, copied into IPCS_FORECAST_DETAIL).
[B glossary/llp_maintenance_smooth_forecast_method.html; B release_notes/release_13_0_1_0/rn_enhancements_fcst_3.html]

1.19 Composite
- Blends forecast streams: Σ weightfactor(i) × (forecastamount + forecastschamount + forecastnramount), where i ranges over streams with UsedInComposite = y and the weight "can vary by time". [B glossary/composite_forecast_method.html]
- MAD, MAPE, RMSE and Tracking Signal are computed for it. Netting rolls composite streams into forecasted_data if UseInTotal is set. "Users cannot make forecast adjustments to composite forecast streams" (no mass adjustment either). [same URL]
- Configuration:
  - The composite stream has Forecast Stream Type = Composite; feeder streams are Non-Composite.
  - In the detail: Forecast Method blank, Run Best Fit = No, Use in Composite Forecasting = Yes, Weight Factor Profile set.
  [B glossary/composite_forecast_stream_2.html]

1.20 Forecast Disaggregation
- Aggregates child-location demand to an Aggregation Location, forecasts there statistically (Best Fit allowed), then distributes the result by system-calculated or user weights. [B glossary/forecast_disaggregation_forecast_method.html; B glossary/demand_aggregation_and_forecast_disaggregation.html]
- Parameter page fields:
  - Aggregate to Location
  - Aggregation History Slices (blank = all slices)
  - Disaggregate Slices (blank = 3)
  - Disaggregation Type: Even or Proportional
  - Demand Stream, Forecast Stream, Is Active, Priority Sequence
  - Segments (must exclude the aggregation location)
  [B core/core_pid/pid_forecast_disaggregation_page.html]
- Run order: Synchronize Database, then Demand Aggregation (not by segment), then Forecasting. Child locations use the "Forecast Disaggregation" method; the aggregation location uses a statistical method or Best Fit. [B glossary/demand_aggregation_and_forecast_disaggregation_2.html]

1.21 Servigistics ML and ML Composite (13.1)
- ML: the Machine Learning Forecasting AutoPilot process chooses among BATS, Auto ETS, Prophet, XGBoost and SARIMA. [B glossary/servigistics_ml_forecast_method.html]
- ML Composite: a blend of the best statistical method and the best ML method, using weights from Best Fit. Fields: Best Non-ML Method, Best ML Method, and their weights. [B glossary/servigistics_ml_composite_forecast_method.html; B core/core_pid/pid_demand_detail_page.html]
- Setup: move both methods to the Best Fit Methods list, then run Machine Learning Forecasting, then Best Fit Forecasting, then Forecasting. PAI ML must be configured. [B release_notes/release_13_1_0_0/rn_enhancements_fcst_2.html]
- "Force Servigistics ML Composite" recommends ML Composite "regardless of any errors". [B parts/parts_pid/pid_edit_forecast_parameter_page_best_fit_tab.html]
- The ML model is trained and validated "in the past for multiple iterations… the best forecast method that has the highest accuracy is selected." [B glossary_pai/machine_learning_based_time_series_forecasting.html]

1.22 Initial Provisioning / Re-Provisioning
- "no longer supported as of the 12.0.0.0 release," but still usable by existing customers. [B core/core_topics/initial_provisioning_forecast_method.html; B core/core_topics/re_provisioning_forecast_method.html]

======================================================================
2. BEST FIT ANALYSIS
======================================================================
Concept
- "The forecast method that results in the smallest forecast error over the specified time period is designated… the Best Fit forecast method." [B glossary/best_fit_analysis.html]
- "leaving typical SKUs under the control of Best Fit forecasting is strongly discouraged. Use Best Fit Analysis periodically to confirm the assigned forecasting method." [same URL]
- Recommended data: "three years of demand history (36 slices…) and a one year forecast window (12 slices)". [same URL]

Modes
- Auto-Approved: assigns the method automatically. If set at the stream configuration level, it runs once and then assigns the method at the SKU level, which prevents Best Fit from rerunning on those SKUs.
- Recommended: results are posted to the Best Fit page for review and approval.
[B glossary/best_fit_analysis.html]
- Set in Stream Configuration Details "Run Best Fit" [B core/core_pid/pid_new_edit_stream_configuration_details_page.html], or ad hoc from Demand Detail (Manage > Run Best Fit) [B core/core_topics/proc_demand_detail_run_best_fit.html]

Approval
- On the Best Fit page, select the row and click Approve; the Approved column updates. [B core/core_topics/approving_best_fit_analysis_recommendations.html]
- On Best Fit Management, choose a different method with the radio button and click Apply. The chosen method is used at the next Forecasting run. [B core/core_pid/pid_best_fit_management_page.html; B core/core_topics/proc_best_fit_change_forecast_method.html]
- Forecasting Database Cleanup removes out-of-date Best Fit Overrides when Run Best Fit changes from Auto-Approved to No/Null (a User Override Method is applied if one exists). [B glossary/autopilot_processes_*; seen in B glossary/autopilot_processes.html set]
- IPLAN_DONOTRUN_BESTFIT (default false): when true, Best Fit is skipped during Interactive Plan [B glossary/global_settings_fcst.html]

Best Fit tab parameters [B parts/parts_pid/pid_edit_forecast_parameter_page_best_fit_tab.html]
- Maximum # of History Slices: the maximum of this value and the stream configuration history horizon. Winters and Croston need ≥12 slices, so with a 12-slice window you need ≥2 years.
- Minimum # of History Slices: blank = 12. If fewer are available, all are used and the error "Slides<1" is raised.
- Holdout Window: "sub-window in the forecast window… across which demand will be compared to forecast values to calculate forecast error (MAPE, MAD, RMSE)."
- Holdout Window equals lead time: overrides the holdout to each SKU's lead time.
- Best Fit Selection Criteria: Composite Error, Best 2 Out Of 3, MAPE, MAD, RMSE.
- Tie-breaker Error Type: used with Best 2 of 3.
- Error Improvement % (churn control; default 10):
  - Recommend switching only if the latest metric of the best-found method is at least x% better than the current method.
  - If the same method is recommended with new values, the new values are applied.
  - 0 disables the threshold. Upgrades are set to 0.
  [also B release_notes/release_13_1_0_0/rn_enhancements_fcst_3.html "Reduced Forecast Method Churn"]
- Best Fit Methods: the Selected list order is used as the tiebreaker.
- Advanced settings:
  - Check for Intermittency
  - Intermittency Test - Periods Between Demand (default 1.25)
  - Intermittency Test - Average Demand Interval Threshold (default 1.32)
  - Intermittency Test - Minimum Demand Interval MVR
  - Select Forecast Method for Intermittent Demand
  - Apply personal seasonal profile to forecast
  - Maximum number of rolling forecasts ("6 and 12 may significantly reduce processing time")
  - Use Autocorrelation Analysis to consider Winters (if seasonal, Winters is chosen regardless of errors when only statistical methods are configured; if ML methods are configured they are evaluated alongside Winters; if not seasonal, Winters is dropped)
  - Use Autocorrelation Analysis to detect trend (if a trend is detected, all flat-line methods are dropped)
  - Min # History Slices to Consider Croston / Winters / DES
  - Force Servigistics ML Composite
- Parameter Values Evaluated (grid search): each parameter is run at primary, primary − delta and primary + delta; the lowest-error values are recorded and used by Forecasting. Delta fields include Alpha, Beta, Gamma, Phi, Omega and "# of History Slices to consider" (±). [same URL; B parts/parts_pid/pid_forecast_parameters_page.html]

Sliding / holdout mechanics
- Best Fit History Slices:
  - If max rolling forecasts is null: = Minimum # of History Slices
  - Otherwise: = Max # History Slices − Max # Rolling Forecasts − Holdout Window + 1
  [B core/core_pid/pid_best_fit_detail_page.html]
- # of Slides: the holdout is first aligned with the first slice of the forecast window, then slid one slice at a time; errors are averaged over the slides. [same URL]
- Worked example: Min = 12, Total = 30, Holdout = 4 gives slides = 30 − (12 + 4) = 15. MAPE/MAD/RMSE shown on Best Fit Management are the averages over the 15 slides. [B glossary/best_fit_analysis_2.html]

Rules (Status column) [B glossary/best_fit_analysis_2.html]
- A hard rule produces no forecast and no errors.
- A soft rule still produces a forecast and MAPE/MAD/RMSE, but no Composite Error.
- Soft rules:
  - Trend detected: eliminates Average, Weighted Average, Moving Average, Same As Last Year and SES
  - LastYearAvg < BEST_FIT_MOVING_AVG_MIN_DEMAND: eliminates Moving Average
  - #HistSlices < minCrostonsHist: eliminates Croston and Intermittence Smoothing
  - Not intermittent: eliminates Croston and Intermittence Smoothing
  - #HistSlices < minDoubleExpHistory: eliminates DES
  - TotalDemandSlices < 5: eliminates DES
  - Horizon forecast < BESTFIT_MIN_FCST
- Hard rules:
  - Any zero in the last 5 demand slices: eliminates Linear Regression
  - NumHistDemands < 2: eliminates Croston and Intermittence Smoothing
  - Stream-config history < 12 or history < 12: eliminates Croston, Intermittence Smoothing, Same As Last Year and Winters
  - History < INIT_EXPSMOOTHING_MONTHS + 3: eliminates DES
  - LastYearAverage < 2, < minWintersHist, or Not seasonal (autocorrelation): eliminates Winters
  - #Slides < 1: eliminates all methods
  - LastForwardStartDate = Null: eliminates all methods
- BESTFIT_MIN_FCST: negative forecasts are floored to 0 before this check (13.0.1.3 fix) [B release_notes/release_13_0_1_3/resolved_issues_13_0_1_3.html]

Error metrics on Best Fit, Best Fit Management and Demand
- RMSE, MAPE, MAD: "only calculated with new period."
- Composite Error: "the result of MAD, MAPE, and RMSE values or the combination of the three," where M = number of candidate methods and j = candidate index (the formula image was not captured). [B parts/parts_topics/composite_error_formula_best_fit.html]
- MAPE:
  - Best Fit: N = slices in the holdout window
  - Demand: N = "# of Slices for Forecast Error Calculation"
  - "In case of negative demand, MAPE can be greater then 2"
  [B glossary/mape.html]
- Best Fit page fields include Status, Approved, Effective Composite Error, and "Forecast Method/ID – Forecast method identified as best fit candidate". [B core/core_pid/pid_best_fit_page.html]
- Best Fit workflow:
  1. In Stream Configuration Details, map demand to forecast streams and set Run Best Fit.
  2. Select methods on the Best Fit tab of Forecast Parameters.
  3. Run Best Fit.
  4. Review.
  5. Approve.
  [B glossary/best_fit_analysis_3.html]
- Demand History Management must run before Best Fit or Causal. It covers categorization and outliers. [B glossary/autopilot_processes.html]

======================================================================
3. STREAMS, STREAM CONFIGURATION, NETTING, AGGREGATION
======================================================================
Demand stream fields [B core/core_pid/pid_demand_streams_page.html; B core/core_pid/pid_demand_stream_page_view_new_edit.html]
- Name, Host ID
- Related Stream ("distinguish between internal and external streams")
- Accumulate (include in total demand)
- Display on Planner Worksheet
- Pricing Demand (SPP)
- Use in Customer Order Size
- Use in Decay Rate (LTB)
- Use In Usage Rate
- Warranty Demand ("used in warranty demand calculations")
- Stream configuration detail sets can separate warranty from non-warranty demand [B glossary/stream_configurations.html]

Forecast stream fields [B core/core_pid/pid_forecast_streams_page.html; B core/core_pid/pid_forecast_stream_page_view_new_edit.html]
- External Indicator ("netting will occur… against sales or replenishment orders")
- Forecast Stream Type (Composite / Non-Composite)
- Related Stream
- Count In Order Plan (not for internal streams of downstream time-phased SKUs or kit components; yes for internal streams under Time-Phased ROP)
- Count Internal Return Forecast in Order Plan
- Display on Planner Worksheet
- Include SD (demand variation included in levels; only if Use in Total = Yes)
- Use in Equipment (IO)
- Non Recurring (NR adjustments loaded through the DD tables)

Stream Configuration [B core/core_pid/pid_new_edit_stream_configurations_page.html]
- Header: Name, Description, "# of History Slices" (demand history horizon), "# of Forecast Horizon Slices"
- Detail fields [B core/core_pid/pid_new_edit_stream_configuration_details_page.html]:
  - Demand Stream and Forecast Stream mapping
  - Forecast Method (not for internal streams)
  - Life Limited Parts Forecast Type (lost / stub)
  - Run Best Fit (Recommended / Auto-Approved)
  - Used In Total Forecast
  - Demand Display, Forecast Display
  - Used in Composite Forecasting
  - Used in Replacement Rate Forecasting
  - Weight Factor Profile
- Assigned to SKUs through AutoPilot Parameters [B glossary/stream_configurations.html]

Totals
- Total external demand = historyamount + historyschamount + historycopyamount
- External forecast = forecastamount + forecastschamount + forecastnramount
- Internal demand/forecast = Σ over child locations (0 or null at leaf level)
- Aggregated demand is stored as stream "NormalInternal"
[B core/core_topics/demand_and_forecast_aggregation.html]
- Enabling aggregation: demand aggregation happens when the internal stream's related ID equals the external demand stream ID. Forecast aggregation requires ExternalIndicator = n and related ID = the external forecast stream ID. IGNORE_REPLALLOWED_IN_ROLLUPS controls whether only ReplAllowed = Y SKUs roll up. Down-chain parts are not forecast; their demand rolls to the TMP. [same URL]

Forecast netting (consumption)
- Netted Forecast = max[(Forecast − Demand), 0] [B glossary/forecast_netting.html]
- Parameters, External and Internal [B parts/parts_pid/pid_new_edit_forecast_netting_parameters_external_page.html; B parts/parts_pid/pid_new_edit_forecast_netting_parameters_internal_page.html]:
  - Enable Forecast Netting (default No)
  - Enable Network Consumption (consume at other locations of the replenishment hierarchy, in ascending level order; the procurement location is level 1)
  - Consume Orders
  - Use Demand History or Order Data (Demand History / Closed Orders / Both)
  - Consume From Future Slices and Forward Consumption Slices
  - Use Remaining Forecast (example: forecast 30, demand 5, half-way through the slice gives 25 if Yes, ((30−5)/30)×15 = 12.5 if No)
  - Rollover Unconsumed Forecast
  - Enable Backward Consumption
  - Forecast Netting Start/End Date (overridable at segment and SKU level)
  - Consumption Date (order vs ship date; internal only)
  - Priority Sequence
  - Net by single stream or stream group
- Default internal and external netting schemes cover all streams not otherwise assigned. Demand Summary rows: Net Forecast / Total Forecast / Total Demand for Internal and External. [B core/core_pid/pid_demand_summary_page.html]
- With forecast aggregation (10.7 note), netting must be disabled on internal streams [B core/core_topics/demand_and_forecast_aggregation.html]
- Review types: 92 Over Consumed Forecast (Parameter 1 = min % consumed), 111 Under Consumed Forecast (Parameter 1 = min cost); Parameter 2 = HostForecastStreamID [B glossary/review_reason_2.html]

Forecast pooling
- One field location stores parts for a regional group, and the forecasts are consolidated. Fields: Maximum Slice forecast; Candidate Locations (All / Non-ASL / ASL); criteria rows (e.g. Annual Forecast > 50); Primary Location. [B glossary/forecast_pooling_parameter.html; B parts/parts_pid/pid_forecast_pooling_parameters_page.html]

Scheduled vs non-recurring demand [B core/core_topics/overview_of_demand_forecasting.html]
- Scheduled adjustments (positive or negative) are added to the forecast.
- Non-recurring adjustments are for one-time events (recall, FCO). They are backed out of demand history so that forecasts are not inflated.
- Three rules for the automatic NR demand adjustment:
  | Calculated forecast | NR adjustment | Actual demand | NR demand adjustment |
  |---|---|---|---|
  | 10 | 50 | 75 | 50 |
  | 10 | 50 | 45 | 35 |
  | 10 | 50 | 6 | 0 |
- The Scheduled row "will not have an effect on demand history once the date is in the past." Profile adjustments are stored here, and user adjustments take priority. [B core/core_pid/pid_demand_detail_page.html]

Copy demand (history transfer)
- Fields: Source (part/location/stream, dates) with action Copy or Move; Destination with action Add or Replace; Demand Percentage (%); Refresh Type (Full / Partial). [B parts/parts_pid/pid_new_copy_demand_history_page.html]
- Status values: New, Failed, Done, Refresh, Delete, Active. Active profiles update each slice until the Destination End Date. [B parts/parts_pid/pid_copy_demand_history_page.html]

Demand Detail aggregation (transactions to slices)
- DEMAND_DETAIL_AGGREGATION_BY_SLICE (default false = one record per day)
- DEMAND_DETAIL_AGGREGATION_MODE: P (Partial, default), F (Full), T (Truncate), W (Time window)
- DEMAND_DETAIL_AGGREGATION_SLICES (default 12; 0 = no rollup)
[B glossary/global_settings_fcst.html]

======================================================================
4. DEMAND CLEANSING: OUTLIERS, ZEROS, HISTORY HORIZON, SEASONALITY
======================================================================
Outlier parameters (Forecasting tab) [B parts/parts_pid/pid_new_edit_forecast_parameter_page_forecasting_tab.html; B glossary/outlier_management.html]
- Outlier - Management:
  - Change: adjust and post to the Review Board
  - Notify: post only, and remove existing adjustments
  - Ignore: no processing, and remove existing adjustments
  - The removal behaviour was added in 13.1 [B release_notes/release_13_1_0_0/rn_enhancements_fcst_6.html]
- Outlier - Definition: 1.0–5.0 standard deviations
- Outlier - Correction: 0–5.0. 0 corrects to the mean; 2.0 corrects to ±2 SD. It must be ≤ Definition.
- Outlier - Maximum Consecutive Occurrences Allowed: null = no limit, 0 not allowed. Example: 3 means that on the 4th consecutive outlier the prior three adjustments are removed.
- Adjust if history less than LCL, where LCL = History Avg − (Outlier Detection Limit × SD)
- Use Confidence Level for Outlier Adjustments: All (recommended) / Slow or Intermittent / None (SD multiplier)
- Upper Control Limit Confidence Level and Correction Confidence Level (defaults 99.73%)

Outlier rules [B glossary/outlier_adjustment.html]
- Only top-most parts are adjusted; replaced parts have their adjustments removed.
- Calculations use raw history, or de-seasonalized/de-trended history if that option is Yes.
- The SD option "must be set to No if you are using Outlier Detection". [B parts/parts_pid/pid_new_edit_forecast_parameter_page_forecasting_tab.html]
- Slow/intermittent SKUs use a lower control limit of 0 with a probability distribution.
- Skipped when:
  - annual demand < OUTLIER_LOWER_TRIP (default 3)
  - history < OUTLIER_MIN_HISTORY_SLICES (default 3)
  - OUTLIER_IGNORE_RECENTYEARCOUNT = false (default) and the first demand is less than 12 months / 52 weeks old
  - the method is Leading Indicator or Croston
- OUTLIER_IGNORE_INTERMITTENCY_CHECK × confidence setting matrix:
  - True + None: older logic
  - True or False + All / Slow-or-Intermittent: PDF (probability distribution) method
  - False + None: intermittent SKUs are not adjusted
- OUTLIER_USE_NON_OUTLIER_SLICES (default true) excludes outlier slices from the history average and SD
- Other settings: OUTLIER_MIN_NON_ZERO_DEMAND_SLICES (default 1); SL_VARIABILITY_TYPE (COV / VMR, default COV); SL_LOW_VOL_THRESH (default 25); SL_LOW_VOL_VMR_THRESH; SL_LOW_VOL_VARIABILITY_CAP (9); SL_HIGH_VOL_VARIABILITY_CAP (30)
  [B glossary/global_settings_general.html; B glossary/levels_calculations.html]
- OUTLIER_USE_VARIABILITY_CAP: recommended false ("can generate false positive outliers"); default false for new installs, true for upgrades [B glossary/global_settings_fcst.html; B release_notes/release_13_1_0_3/rn_enhancements_fcst_2.html]
- Review types: 83 Outlier Detected, 86 Outlier Adjustment applied. The Forecast Review page shows an "Outliers Adjusted" count. [B glossary/review_reason_2.html; B parts/parts_pid/pid_forecast_review_fields.html]
- Performance tip: property servigistics.histanalysis.clear.outlier = true [B glossary/autopilot_processes.html]

Zero-demand and history horizon
- Ignore demand before first non-zero slice: Yes uses history only from the first non-zero slice. Example: horizon 36, first demand 3 slices ago gives 3 slices. [B parts/parts_pid/pid_new_edit_forecast_parameter_page_forecasting_tab.html]
- Related global settings: DMDHIST_USE_FIRST_FOUND, DMDHIST_USE_FIRST_ROUND, DMDHIST_USE_FIRST_FOUND_MIN_SLICES. "global settings… control whether the system uses the first non-null value or assumes null values are zeros". [same URL; B parts/parts_pid/pid_ipws_forecast_forecast_metrics.html]
- History Analysis Slices waterfall:
  1. IPWS/Demand override
  2. Forecast Parameter "# of History Slices for History Analysis"
  3. Stream Configuration "# of History Slices"
  - If Run Best Fit is on, the greater of this and Best Fit Max # History Slices is used.
  [B parts/parts_pid/pid_ipws_forecast_forecast_metrics.html]
- Per-method "# of History Slices …" fields. The value cannot exceed the demand history horizon. [B parts/parts_pid/pid_new_edit_forecast_parameter_page_forecasting_tab.html]
- Use Phase In Date / Use Phase Out Date: when Yes, forecasting respects the part's dates, and there is no forecast for EOL parts with a valid Phase Out Date. [same URL]
- Part Phase In Date = "start date in the past from where demand is used"; Phase Out Date = "future date when the forecasts stops". [B core/core_pid/pid_parts_page.html]

Demand categorization (13.0)
- Categories: Smooth (ADI < 1.32 and CoV² < 0.49), Erratic (ADI < 1.32 and CoV² ≥ 0.49), Intermittent (ADI ≥ 1.32)
- ADI = total slices / non-zero slices
- Evaluated at SKU-Stream level (thresholds from Forecast Parameters) and SKU level (HIST_ANALYTICS_AVG_DMD_INTERVAL_THRESH = 1.32, HIST_ANALYTICS_COV_SQUARED_THRESH = 0.49)
- Categories can be used to build segments
- FCST_RUN_HIST_ANALYTICS and BESTFIT_RUN_HIST_ANALYTICS: false for new installs, true for upgrades
- INTERMITTENCY_TEST_USE_ADI: true for new installs, false for upgrades
[B release_notes/release_13_0_0_0/rn_enhancements_fcst_3.html; B glossary/demand_category.html]
- Periods Between Demand = zeros / (non-zeros − 1). Examples give 5.25 and 1.5. The PERIODS_BETWEEN_DEMAND global setting is the default. [B glossary/periods_between_demand.html]

Seasonal profiles
- Monthly profile = 12 indices summing to 12; weekly = 52 indices summing to 52.
- Deseasonalized history is used by all demand-based methods; the forecast is then multiplied by the index.
- Total Demand = Demand + Adjustment (Outlier or User) + Copy Demand
[B glossary/seasonal_profile.html]
- Indices ≤ 0.3 are ignored (threshold changeable by support), with special rules for the deseasonalized value. [B glossary/seasonal_profile_2.html; B glossary/seasonal_profile_4.html]
- Index = slice demand / initial historical average. Uses 1–3 years of history with year weights 1; 0.6/0.4; 0.5/0.3/0.2. [B glossary/seasonal_profile_3.html]
- The TMR's profile applies to the whole chain's demand [B glossary/seasonal_profile_4.html]
- History Analysis tab: Determine Seasonality, Consider as Group?, Output Seasonal Profile?, # of History Slices for History Analysis, Output Adjusted History?, YoY Trend threshold / Starting Weight / Weight Decrement, Seasonal Indices Starting Weight (default 5) / Weight Decrement (default 2) [B parts/parts_pid/pid_edit_forecast_parameter_page_history_analysis_tab.html]

Time buckets and calendar
- A slice is summarized data over a period (week, month). [B glossary/slice.html]
- The databases are "monthly" or "weekly". [B glossary/causal_forecast_method.html; B glossary/seasonal_profile.html]
- Calendars: Working, Ordering and Transportation (with parent/child merging). They are used by ordering and forecasting processes to adjust dates. [B glossary/calendars.html]
- Forecast horizon = "# of Forecast Horizon Slices" (stream config). "a forecast is best when only viewed a few months out." [B core/core_pid/pid_best_fit_detail_page.html]

======================================================================
5. SUPERSESSION / PART CHAINS / ALTERNATES
======================================================================
- A part chain is a series of revisions, each superseding the previous one; "down-chain" is older and "up-chain" is newer. [B glossary/part_chain.html]
- Relation types:
  - Alternate: the up-chain part can substitute for the down-chain part, but not the reverse; used to burn off old stock.
  - Replace: the old part is no longer planned and is removed from ASLs. "Future demand for replaced parts is redirected to the next up-chain planned part (Top Most Part or Alternates)."
  - Roll Up Good / Roll Up Bad / Roll up good as bad flags control inventory.
  - A part belongs to one chain per location.
  [B glossary/part_chain.html]
- Down-chain demand rolls into the TMP. Forecasts are not generated for down-chain replacement parts. [B core/core_topics/demand_and_forecast_aggregation.html; B core/core_pid/pid_demand_detail_page.html]
- Future Part Chains (FUTURE_PART_CHAINS):
  - Effective Date = Available Date − Lead Time (max of procurement, repair and replenishment) − Buffer Days for Future Chain Parts
  - The Active flag controls recalculation
  - FX Part Procurable / FX Part Repairable set future behaviour
  [B glossary/part_chain_2.html]
- Review types: 16 In Supercession Chain; 27 New Part Chain Information; 50 Part in Transition (Forecasting). [B glossary/review_reason_2.html]

======================================================================
6. INSTALLED BASE, ROLLOUT, NPI, EOL
======================================================================
- Install Base fields: Amount, Begin/End Date (End Date is system-managed; the latest record must have a null End Date), Contract Type, EOL Date ("demand for service parts will be ended"), Install Site, Model, Serial, Usage Factor, Include in Network Optimization [B core/core_pid/pid_install_bases_page.html]
- Product Rollout: how a product is installed at a site over time; used as causal input. [B glossary/product_rollout.html]
- Average Population = average rollout × qty per unit [B glossary/average_population.html]
- Lifecycle Management – NPI steps:
  1. Product setup
  2. Service shipment plan (install-base growth)
  3. Calculate initial demand (seed forward locations, corrective maintenance, installation, PM)
  4. View results
  5. Review Board Lifecycle tab
  [B glossary/life_cycle_management.html]
- Seed Stock: Strategic Locations ÷ Deployment Cycle per slice (e.g. 101 / 4 gives 25, 25, 25, 26). [B parts/parts_topics/calculating_initial_demand_forecast.html]
- ML NPI forecasting uses similar parts' history for parts without history; there is also ML MTBF prediction for new parts. [B glossary_pai/machine_learning_based_new_parts_forecasting.html; B glossary_pai/new_part_mtbf_prediction.html]
- EOL / Last Time Buy:
  - Triggered by EOP or vendor discontinuation; top-down and bottom-up modes; profile-based decay forecasts.
  - Forecast lines: LTB Forecast, SBLI Forecast, Selected Forecast.
  - Decay Rate Parameters: Calculation Type Slice / Actual / Group, Decay Start Slice, Override Decay Rate.
  [B glossary/last_time_buy.html; B parts/parts_pid/pid_last_time_buy_forecast.html; B parts/parts_pid/pid_ltb_decay_rate_parameters_page.html]

======================================================================
7. ACCURACY METRICS
======================================================================
Core application (Demand / Best Fit / Forecast Review / IPWS)
- MAPE, MAD, RMSE: the window is "# of Slices for Forecast Error Calculation" (Demand) or the holdout (Best Fit). Demand-page errors are "for display only and have no effect on Best Fit." [B parts/parts_pid/pid_new_edit_forecast_parameter_page_forecasting_tab.html]
- Tracking Signal = (RSFE / count) / MAD, where RSFE is the running sum of forecast errors and count is the error-calc slices or the holdout. Enabled by "Enable Tracking Signal". [B glossary/tracking_signal.html]
- TRACKING_SIGNAL_NORMALIZED (default true): review thresholds are ±0.5 when normalized, ±4 when not (review types 138 and 139). [B glossary/review_reason_2.html]
- Bias = (Total Forecast − Total Demand) / #error slices. Bias Value = Bias × Part Cost. These are calculated only for External streams with Used In Total = Yes. At location level, over- and under-forecast are kept separate. [B glossary/bias.html; B glossary/bias_value.html]
- Average Demand and Average Historical Forecast = totals / #error slices [B parts/parts_pid/pid_forecast_review_fields.html]
- Forecasting-Calculate Metrics process (auto-runs if RUN_CALCULATE_METRICS_WITH_FORECAST is set) [B glossary/autopilot_processes_8.html]

PAI definitions
- MAPE = Σ|D−F| / Σ((D+F)/2), range [0, 2] [B glossary_pai/mape.html]
- MAD = (Σ|D−F| / N) / X [B glossary_pai/mad.html]
- RMSE = SQRT((Σ(D−F)² / N) / X) [B glossary_pai/rmse.html]
- Tracking Signal = Σ(D−F) / Σ|D−F|, range [−1, 1] [B glossary_pai/tracking_signal.html]
- Bias = ΣF − ΣD [B glossary_pai/bias.html]
- Forecast Accuracy = 100 − (MAD / Average Demand) × 100% [B glossary_pai/forecast_accuracy.html]
- N = error-calc slices; X = forward periods (1 for Foundation; 3, 6 or Lead Time for Advanced) [B functional/menu_forecast_performance.html]
- Dashboard bands: FA Low ≤ 25%, Medium 26–75%, High > 75%; TS Under > 0.5, Over < −0.5 [B functional/dashboard_forecast_analysis.html]
- Aggregate TS = Σ(TS × History Avg) / Σ History Avg [B functional/dashboard_forecast_error_analysis.html]
- Analytics properties: servigistics.analytics.forecast.calc.three.months / six.months / horizon / leadtime (leadtime default true) [B glossary/autopilot_processes_9.html]

======================================================================
8. VARIABILITY MEASURES USED DOWNSTREAM (levels / safety stock)
======================================================================
- HistorySD = SQRT((SUMSQ − SUM²/COUNT) / (COUNT − 1)). It uses de-seasonalized/de-trended history if that option is Yes. [B core/core_pid/pid_demand_detail_page.html]
- Forecast Error SD: used in safety stock when "Std Deviation - Use forecast error" = Yes. With fewer than 3 archived forecast slices it is null and HistorySD is used instead. [same URL]
- ForecastSD = (HistorySD / HistoryAvg) × ForecastAvg, used when "Use Scaled Percentage" = Yes. Decision matrix: forecast error = Yes and scaled = No uses FESD; forecast error = Yes and scaled = Yes uses ForecastSD in levels and the Optimizer. [B parts/parts_pid/pid_new_edit_forecast_parameter_page_forecasting_tab.html]
- History Percent Error = SD / Avg × 100 [B core/core_pid/pid_demand_detail_page.html]
- The Post Forecast process updates Annual Demand and Forecast SD (RUN_POST_FORECAST, default true) [B glossary/global_settings_fcst.html]
- Low-volume logic: Poisson vs negative binomial, based on VMR vs SL_LOW_VOL_VMR_THRESH [B glossary/levels_calculations.html]
- Stream "Include SD" flag [B core/core_pid/pid_forecast_streams_page.html]

======================================================================
9. REVIEW, OVERRIDES, ADJUSTMENTS
======================================================================
Forecast Review / approval
- Requires ENABLE_FORECAST_APPROVAL = true and user rights Approve / Make Production.
- The forecast splits into Total Production and Total Recommended; overrides apply to Recommended.
- SKU status: None, then Recommended, then Approved, then Production.
- The Make Forecast Production process moves the approved forecast to production.
[B core/core_topics/overview_of_forecast_review.html; B parts/parts_pid/pid_forecast_review_fields.html]
- FORECAST_REVIEW_MAX_GRID_ROWS (default 65,000) [B glossary/global_settings_fcst.html]
- Forecast Review columns: Approved By, Bias, Bias Value, Demand Category, FESD, HistorySD, MAD, MAPE, RMSE, TS, Outliers Adjusted, SKU Forecast Status, Row Types (Aggregate / Raw / Adjustment) [B parts/parts_pid/pid_forecast_review_fields.html]

Forecast Analysis mass adjustment
- Methods: Set, Relative, Percent, Extended Percent (compounding, e.g. 110 / 121 / 132.1).
- Aggregate adjustments are spread proportionally; Units display is required; a note is auto-added.
[B parts/parts_topics/adjusting_forecast_on_the_forecast_analysis_page.html]

Forecast Adjustment Profiles
- Operations: Replace, Increase/Decrease by Value, Increase/Decrease by Percent, applied through ForecastSchAmount.
- Not applied to composite streams or Replacement Rate streams.
- Priority Sequence; "User adjustments have precedence over profile adjustments."
[B parts/parts_pid/pid_additional_data_forecast_adjustment_profile_details.html; B parts/parts_topics/workflow_for_applying_forecast_adjustment_profiles.html]

SKU overrides (13.1)
- Annual Forecast Override is spread over 12 months in proportion to the raw forecast.
- Priority order: period adjustment, then annual override, then segment profile.
[B release_notes/release_13_1_0_0/rn_enhancements_fcst_4.html]
- Forecast Override Intelligence (ML): message "A forecast override is not recommended" [B release_notes/release_13_1_0_2/rn_enhancements_fcst_3.html]

Review Board forecasting types [B glossary/review_reason_2.html]
- 1–3 Actual vs Forecast outside Demand SD (AutoPilot Parameters Review Slices / Review Limit / Demand Minimum)
- 4–6 Forecast % change (Forecast Monitor Slice, Percentage Change, Forecast Minimum)
- 50 Part in Transition
- 62–64 insufficient data (Winters, DES, Croston)
- 80 Forecast Custom Item 1
- 83 Outlier Detected; 86 Outlier Adjustment applied
- 92 Over Consumed Forecast; 111 Under Consumed Forecast
- 138 TS Actuals > Forecast; 139 TS Forecast > Actuals
- 343 and 344 failure rate (342 is also causal)
- Tabs appear only for subscribed types [B glossary/review_board.html]

======================================================================
10. OTHER FORECAST GLOBAL SETTINGS (not listed above)
======================================================================
- APPLY_NFF_TO_INT_RETURN_FCST (default true)
- APPLY_RETURN_WR_AND_NFF_TO_CONSUMABLES (default false)
[B glossary/global_settings_fcst.html]
- CUST_ORDER_SIZE_OUTLIER_STD / _HANDLING (REMOVE or REPLACE) / _MIN_DMD_RECS / _DMD_HIST_HORIZON [B glossary/global_settings_io.html]
- MID_SLICE_ASL_DA_THRESHOLD (mid-slice first-demand stocking) [B glossary/autopilot_processes*.html]

A note on history length: one page (Parameter Settings AutoPilot tab) says "Since Servigistics works on a day-by-day method, it is important that the history data is recorded daily… Using history periods longer than daily will result in high standard deviations." [B parts/parts_pid/pid_ps_page_autopilot_tab.html]

Gaps and uncertainties
- The formula images for MAD, RMSE and Composite Error (Best Fit and Demand variants) are missing from the crawl.
- The exact Croston, TSB and Winters equations are not in the text.
- The SIOP section contains only a generic intro [B process/siop_workflows.html].
- The pages disagree on minimum history for Winters/DES: 12 months vs 2 years.
- No files were written.