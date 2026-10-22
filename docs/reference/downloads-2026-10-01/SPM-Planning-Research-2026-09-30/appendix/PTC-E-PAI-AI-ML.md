PTC SERVIGISTICS 13.x: PAI, AI/ML, AND PAI 5.0.0.0 / 5.0.0.1 RELEASE NOTES (research notes)
Every fact below is followed by its source URL (the first line of the crawled file). All sources are under https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/

======================================================================
1. WHAT PAI IS, AND ITS DATA MODEL AND REFRESH
======================================================================
- PAI is "a reporting platform for Data Historicization, Performance Measurement, Root Cause Analysis, and Intelligence for the Service Supply Chain." Its dashboards are built in Intellicus and opened from the Servigistics main menu. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary_pai/performance_analytics_intelligence.html]
- PAI processes reports that need large data volumes on a separate server, so they do not slow down the production system. [same URL]
- There are two dashboard tiers:
  - PAI Foundation: low data volume, fast enough not to affect production. [same URL]
  - PAI Advanced: large data volume. Data is exported to a separate server and processed there. Advanced covers "Performance — forecast accuracy performance, planner productivity and workload analysis, supplier performance, service level and financial performance; Analytics — time phased Dashboards...; Intelligence — root causes of service loss, factors driving over-forecasting and under-forecasting, effectiveness of overrides." It supports tera/petabyte-scale big data. [same URL]
- A third category, PAI Machine Learning, appears in the dashboard catalogue (section 2). [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboards_section.html]
- Storage in PAI Advanced uses two methods: [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/how_is_data_stored.html]
  - Historicized (kept as a time series): demand streams and stream config; forecast streams and parameters; inventory (on hand, on order, in return); stocking decisions (stock max, ROP, SL, EOQ); supply chain data (orders, sales orders, returns); review reasons.
  - Copied (last value only): segments; planners and planner coverage; base data (parts, locations, part types, part chains).
- Presentation: stored data is "sorted, filtered, and aggregated into cubes in the Intellicus system". Building an analytical object creates the data shown on a dashboard, and rebuilding it updates the data. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/how_data_is_presented.html]
- Analytical Object = a "set of multi-dimensional, pre-aggregated data ... stored in the Intellicus system". It "need[s] to be rebuilt periodically" to reflect the latest planning data. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary_pai/analytical_object.html]
- There are three ways to refresh dashboard data: (1) build the corresponding Analytical Object, (2) publish the corresponding Report, (3) run the Performance 360 Jobs in Intellicus. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/admin/admin_update_data_on_dashboards.html]
- Planning Analytics Generator AutoPilot process (cannot be run by segment): "Loads the Order Planning and Inventory Optimization related data from the Servigistics database into the Performance Analytics and Intelligence database... to create tables for Intellicus." [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/autopilot_processes_9.html]
- DB connections: ReportDB is "A Servigistics database connection where data is fetched to generate reports" [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary_pai/reportdb.html]. RepositoryDB is where the Intellicus cab files are stored [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary_pai/repositorydb.html].
- ETL (ML context): fetches Zeppelin Notebook output into Intellicus, transforms it, and loads it into the Servigistics schema. Input ETLs send Servigistics data to Zeppelin; Output ETLs save Zeppelin results. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary_pai/etl.html]
- Table archiving is controlled by the AutoPilot property servigistics.analytics.archive.tables.mode:
  - STANDARD = out-of-the-box tables only
  - CUSTOM = only the tables listed in IPCS_ANALYTICS_CUSTOM_TABLE_INFO
  - ALL = both (default)
  [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/admin/admin_disable_archive.html]
- Dashboard anatomy: made of Dimensions (qualitative, e.g. Location, Part Family, Part Type) and Measures (numeric, e.g. Backorders, On Order, Profit). Each dashboard has three sections: Toolbar, Filters, Widgets. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/understanding_using_dashboards.html]
- Access: type "Advanced Reports Dashboard" in the Go to box, or select Analytics from the Servigistics main menu. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/how_to_access_dashboards.html]

======================================================================
2. FULL DASHBOARD CATALOGUE (by tier)
======================================================================
Source for all tier lists: [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboards_section.html]

PAI FOUNDATION, Service Parts Management (11): Backorder Categorization; Excess Analysis; Forecast Analysis; Forecast Error Analysis; Performance 360; Review Reason Summary; Spend Inventory and Projection; Vendor Detail; Vendor Forecast; Vendor Prioritization and Performance; Vendor Performance Management.

PAI FOUNDATION, Service Parts Pricing (8): Financial Bridge Analysis; Global Group Price Analysis; Global Pricing Financial Analysis; Key Competitor Analysis; Market Statistics Analysis; Price Book Analysis; Pricing Policy Duplicate SKUs; Pricing Review Reason Summary.

PAI ADVANCED, Service Parts Management (15): Backorder Days; Demand Miss Analysis; Fill Rate Analysis; Forecast Analysis–Advanced; Forecast Error Analysis–Advanced; Forecast Override Analysis–Advanced; Inventory Detail; Location Forecast Analysis–Advanced; Part Forecast Analysis–Advanced; Performance 360 Advanced; Planner Workload; Review Reason Trend; SKU Forecast Analysis–Advanced; Service Group Fill Rate Detail; SKU Supply Chain History. (Pricing: N/A.)

PAI MACHINE LEARNING, Service Parts Management (14): Correlated Part Details; Correlated Parts Intelligence; Forecasting Time Series Analysis; Forecast Accuracy Intelligence; MTBF Cluster; Multivariate SKU Forecast Analysis; New Part Introduction Forecasting; New Part Introduction Forecasting Detail; New Part MTBF Prediction; Region MTBF; Region MTBF Detail; Remaining Useful Life; Remaining Useful Life Detail; SKU Forecast Analysis.

PAI MACHINE LEARNING, Service Parts Pricing (3): New SKU Margin Intelligence; Price Margin Cluster Details; Price Margin Intelligence.

Business-category menus (same source), with the menu page descriptions:
- Performance 360 (executive, system-level: service, forecasting, operational performance, planner workload, supply chain health, review reasons) [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/menu_performance_360.html]. Contains: Inventory Detail, Performance 360, Performance 360 Advanced, Planner Workload, Review Reason Summary, Review Reason Trend, and the pricing Foundation dashboards.
- Forecast Performance: Forecast Analysis (+Advanced), Forecast Error Analysis (+Advanced), Forecast Override Analysis-Advanced, Location/Part/SKU Forecast Analysis-Advanced, SKU Forecast Override Analysis-Advanced. Metrics use N = "# of Slices for Forecast Error Calculation" on the Forecast Parameter. X (forward-looking periods) = 1 for Foundation, and 3 slices, 6 slices, or Lead Time for Advanced. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/menu_forecast_performance.html]
- Pricing Intelligence: New SKU Margin Intelligence, Price Margin Cluster Details, Price Margin Intelligence. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/menu_pricing_intelligence.html]
- Service Performance ("fill rates and backorders"): Backorder Categorization, Backorder Days, Demand Miss Analysis, Fill Rate Analysis, SKU Supply Chain History, Service Group Fill Rate Detail. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/menu_service_performance.html]
- Supply Network Performance (excess, spend history and projection, supplier performance): Excess Analysis, Spend Inventory and Projection, Vendor Detail, Vendor Forecast, Vendor Prioritization and Performance, Vendor Performance Management. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/menu_supply_network_performance.html]
- Forecast Intelligence: "Machine Learning-based use cases that help predict the accurate forecast and provide insights on features that are important for root cause analysis". Business scenarios: Correlated Parts Intelligence, Forecast Accuracy Intelligence, Forecast Override Recommendations, ML-Based Time Series Forecasting, ML-Based New Parts Forecasting, Multivariate SKU Forecast Analysis, New Part MTBF Prediction, Region-Based MTBF Prediction, Remaining Useful Life Prediction. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/menu_forecast_intelligence.html]

======================================================================
3. WHAT EACH DASHBOARD SHOWS (one-liners)
======================================================================
Service / backorders
- Backorder Categorization: backorder detail at SKU level. Opened from the menu, from the Planner Home Page Backorder Categorization container, or from the Performance 360 Backorder Categorization widget. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboard_backorder_categorization.html]
- Backorder Days: "how many days a backorder was in the system" (carried over daily until filled). Shows trends, frequency, time-phased backorder days by root-cause category, by SKU, and by Planner Code. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboard_backorder_days.html]
- Demand Miss Analysis: "analyze the unfulfilled demand (missed quantity) due to the unavailability of stock". Covers time-phased trend by root cause, top-contributing SKUs, categorical distribution, and Planner Codes with the most misses. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboard_demand_miss_analysis.html]
  - Rules: only Active Pairs are counted. External demand only (identified via External Forecast streams whose demand streams have Use In Total = Y). The calculation is day-by-day with no carry-forward. Past-due unfulfilled demand is excluded. Backorder qty is subtracted from On Hand. The smallest Demand Detail qty is filled first when computing Lines Filled. Filters: Stockable, TMR. [same URL]
- Fill Rate Analysis: "percentage of customer demand that is met immediately from stocks without placing backorders". Planned/Actual/Delta Unit and Line Fill Rate, Missed, and Unplanned Missed at Service Group/SKU/Location/Part levels. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboard_fill_rate_analysis.html]
- Service Group Fill Rate Detail: fill rate performance at service-group level, with the same measures. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboard_service_group_fill_rate_detail.html]
- SKU Supply Chain History: "in-depth analysis of any demand miss, fill rates, and backorder days". Daily inventory, stock levels, on order, and demand-miss root cause, across three tabs. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboard_supply_chain_history.html]

Executive / workload
- Performance 360: "current, high-level view of service, forecasting, and operational performance", with links into Servigistics. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboard_performance360.html]
- Performance 360 Advanced: historical plus current view. Examples: Planned vs Actual unit fill rate trend, and Demand Miss trend with Root Cause Category. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboard_performance_360_advanced.html]
- Inventory Detail: daily average inventory trend in three bands: Critically Short (On Hand < Safety Stock), In Range, and In Excess (On Hand > Stock Max). [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboard_inventory_detail.html]
- Planner Workload: system-level planner daily performance based on review reasons reviewed (average generated per day; reviewed vs pending per planner). [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboard_planner_workload.html]
- Review Reason Summary: review reasons at global, location, and part level, filterable by planner, including not-reviewed counts. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboard_review_reason_summary.html]
- Review Reason Trend: historical time-phased daily trend by review reason (Forecast and Supply Planning). [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboard_review_reason_trend.html]

Forecast performance
- Forecast Analysis: total demand vs forecast by demand category (Smooth, Intermittent, Erratic), Bias/Bias Value, accuracy, and method-count and adjustment trends. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboard_forecast_analysis.html]
- Forecast Analysis–Advanced: the same, calculated on lead-time data, and adds the Composite Forecast Method count. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboard_forecast_analysis_advanced.html]
- Forecast Error Analysis: SKU-streams "consistently under or over forecasted", via Tracking Signal, Bias, and Bias Value, broken down by location, part type, method, parameter, and so on. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboard_forecast_error_analysis.html]
- Forecast Error Analysis–Advanced: over- and under-forecast and accuracy by location, part type, and method. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboard_forecast_error_analysis_advanced.html]
- Forecast Override Analysis–Advanced: compares KPIs "with and without forecast adjustments" by Segment, Location, Part Type, and Method. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboard_forecast_override_analysis_advanced.html]
- SKU Forecast Override Analysis–Advanced: Tracking Signal trend for adjusted SKU streams. Uses Total Demand, Total Raw Forecast, and Total Forecast. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboard_sku_forecast_override_analysis_advanced.html]
- Location / Part / SKU Forecast Analysis–Advanced: accuracy, bias, and method trends at each level, and child items below the accuracy threshold. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboard_location_forecast_analysis_advanced.html] [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboard_part_forecast_analysis_advanced.html] [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboard_sku_forecast_analysis_advanced.html]

Supply network / vendor
- Excess Analysis: system excess as of today for SKUs with review reason In Excess (19), by Planner Code, Part Family, Location Type, and Region. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboard_excess_analysis.html]
- Spend and Inventory Projection: monthly procurement and repair spend projection, forecasted demand value, and inventory and stock-level projection. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboard_spend_and_inventory_projection.html]
- Vendor Performance Management: delivery lead-time performance of procurement orders (on-time, early, late, top spend). Requires at least 10 closed orders per vendor-location/part (configurable via PO_SPM_VendorMinOrders). Closed orders need an Actual Available Date. The Primary Vendor Location lead time is used as the Servigistics lead time. Widgets: Vendors by Late Delivery, Delivery Status Classification, Vendors by Early Delivery, Top Vendors by Spend, Details. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboard_vendor_perf_mgmt.html]
- Vendor Detail: spend to date, order delivery status, top late parts and locations, spend by part and location, activity. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboard_vendor_detail.html]
- Vendor Forecast: vendor capacity, procurement and repair order projection, Service Impact Score, spend history and projection. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboard_vendor_forecast.html]
- Vendor Prioritization and Performance: prioritizes vendors "based on a Service Impact score". Widgets: Service Impact Score, Total Spend History, Total Spend (projection), Procurement, Repair, Shortage (total shortage qty), Vendor By Service Impact (top 5), Vendor Details (drill to Vendor Forecast / Procurement / Repair pages), Vendor By Late Delivery. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboard_vendor_prioritization_and_performance.html]

Pricing (Foundation)
- Financial Bridge Analysis: impact of price, cost, demand, and mix changes on revenue, profit, and margin. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboard_financial_bridge_analysis.html]
- Global Pricing Financial: financials by Pricing Market and Stream. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboard_global_pricing_financial.html]
- Group Price Analysis: part groupings. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboard_global_group_price_analysis.html]
- Key Competitor Analysis: OEM prices vs each competitor. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboard_key_competitor_analysis.html]
- Market Statistics Analysis: OEM prices vs aggregated competitor prices. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboard_market_statistics_analysis.html]
- Price Book Analysis: uploaded vs pending SKUs and target revenue/profit. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboard_price_book_analysis.html]
- Pricing Policy Duplicate SKUs. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboard_pricing_policy_duplicate_skus.html]
- Pricing Review Reason Summary. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboard_pricing_review_reason_summary.html]

Pricing (ML)
- Price Margin Intelligence: finds opportunities "to raise prices, and therefore margins, without reducing revenue", plus price outliers. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboard_price_margin_intelligence.html]
- Price Margin Cluster Details: cluster drill-down. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboard_price_margin_cluster_details.html]
- New SKU Margin Intelligence: recommends margins and prices for new SKUs (outlier thresholds, margin range, based on similar SKUs). [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboard_new_sku_margin_intelligence.html]

ML service-parts dashboards: see section 5.

======================================================================
4. KPI DEFINITIONS
======================================================================
Fill rate
- Actual Fill Rate: "The fraction of demand that is met through immediate stock availability which includes incoming host orders expected to be available today". Calculated when the Planning Analytics Generator AutoPilot runs. Measured as Line and Unit. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary_pai/actual_fill_rate.html]
- Actual Unit Fill Rate (SKU) = [Min(Quantity Requested, Day's On Hand) / Quantity Requested] * 100.
  - Quantity Requested = HistoryAmount from IPCS_DEMAND_DETAIL.
  - Day's On Hand = OnhandNew + OnhandFixed – Backorder – Allocated + Plan Quantity (today's incoming host orders, by Effective Available Date / Plan Available Date).
  [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary_pai/actual_unit_fill_rate.html]
- Actual Line Fill Rate (SKU) = (Lines Filled / Lines Requested) * 100, where Lines Requested = number of lines in IPCS_DEMAND_DETAIL. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary_pai/actual_line_fill_rate.html]
- Planned Fill Rate: "The historicized Fill Rate from the Stocking Policy page ... calculated by the Inventory Optimization calculation". It is historicized by Planning Analytics Generator. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary_pai/planned_fill_rate.html]
- Planned Unit Fill Rate = Σ(SKU Planned FR * SKU Qty Requested) / Σ(SKU Qty Requested). [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary_pai/planned_unit_fill_rate.html]
- Planned Line Fill Rate = Σ(SKU Planned FR * SKU Lines Requested) / Σ(SKU Lines Requested). [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary_pai/planned_line_fill_rate.html]
- Delta Unit Fill Rate = Actual Unit FR – Planned Unit FR. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary_pai/delta_unit_fill_rate.html]
- Delta Line Fill Rate = Actual Line FR – Planned Line FR. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary_pai/delta_line_fill_rate.html]
- Aggregation: System, Service Group, Location, and Part levels use the "Weighted Average of the SKU level Fill Rates". Period shows the trend over time. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary_pai/fill_rate_aggregation.html]

Missed and unplanned missed
- Missed (= Demand Missed) = Σ Qty Requested – Σ Qty Filled. Calculated for parts not in a chain, alternates, and top-most chain parts. Not calculated for Replaced parts, whose demand rolls up to the parent regardless of Roll up Demand Percent. Example: inventory 7, two lines of 5, so Missed = 3. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary_pai/missed.html] [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary_pai/demand_missed.html]
- Unplanned Missed: "The demand misses which are not expected as per Planned Unit Fill Rate".
  - Formula: Unplanned Missed = Delta Unit FR * Total (Qty Requested). It is 0 if Actual > Planned.
  - Example: Planned 97%, Actual 95%, so the extra 2% is unplanned.
  [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary_pai/unplanned_missed.html]
- Line Missed = Σ Lines Requested – Σ Lines Filled. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary_pai/line_missed.html]
- Unplanned Line Missed = Delta Line FR * Total Line. It is 0 if Actual > Planned. Example: Planned 98%, Actual 94%. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary_pai/unplanned_line_missed.html]

Forecast metrics
- Bias = Σ Total Forecasts – Σ Actual Demands. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary_pai/bias.html]
- Forecast Accuracy = 100 – Forecast Error %, where Forecast Error = (MAD / Average Demand) * 100%. Range 0–100%. X = 1 slice for Foundation; Lead Time, 3, or 6 for Advanced. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary_pai/forecast_accuracy.html]
- Tracking Signal = Σ(Demand – Forecast) / Σ|Demand – Forecast| over N observations. Range [-1, 1]; closer to 0 is better. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary_pai/tracking_signal.html]
- MAPE = Σ|D – F| / Σ((D + F) / 2). Range [0, 2]. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary_pai/mape.html]
- MAD = (Σ|D – F| / N) / X. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary_pai/mad.html]
- RMSE = SQRT((Σ(D – F)^2 / N) / X). [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary_pai/rmse.html]
- COV = History Std Dev / History Average. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary_pai/cov.html]

Other metrics and filters
- Days of Excess Supply (Excess Analysis filter) = Excess Supply / Daily Demand Rate, where the rate comes from the Annual Forecast. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary_pai/days_of_excess_supply.html]
- Active Pair: Part and Location both Active. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary_pai/active_pair.html]
- Stockable filter (renamed from "IO Stockable" in 5.0): used on Backorder Days, Demand Miss Analysis, Fill Rate Analysis, and Performance 360 Adv. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary_pai/stockable.html]
- TMR filter = Top Most Revision parts. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary_pai/tmr.html]

Service Impact Score (vendor)
- Shown on Vendor Prioritization and Performance ("overall service impact score for all Vendors") and on Vendor Forecast (score for the selected vendor). [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboard_vendor_prioritization_and_performance.html] [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboard_vendor_forecast.html]
- In the Analytical Object it is defined as "Service Impact Score = Sum of Systemimpact". Also in that AO: Shortage = Sum of Exceptionqty; Total Spend = Sum of Procure Projection and Repair Projection. No further formula is documented in the crawl. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary_pai/AO_SPM_VendorPrioritizationAndProjection.html]

Root Cause Categorization (Backorder / Demand Miss cause analysis)
Used by Backorder Categorization, Backorder Days, Demand Miss Analysis, and the Performance 360 Backorder Categorization widget. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary_pai/root_cause_categorization.html]

| Pri | Category | Condition (abridged) |
|---|---|---|
| 1 | Forced Non-Stock | An override or constraint forces no stock (e.g. Stock Max Fixed Override = 0) |
| 2 | No Supply Source | Procurable = Replenishable = Repairable = N |
| 3 | On ASL with On Order | ASL = Y, shortage at parent. DMA uses On Order + In Repair > 0; BO dashboards use the "Original" values |
| 3.1 | Vendor Delays with On ASL with OnOrder | Miss at procurement location (ProcAllowed = y) and Review Reason 327 "Overdue host order(s) exist" at that location |
| 3.2 | Vendor Delays at Procuring Location with On ASL with OnOrder | Miss at replenishment location (ProcAllowed = n) and RR 327 at its procurement location |
| 3.3 | Under Forecast with On ASL with OnOrder | Miss plus under-forecast RR, e.g. 138 "Tracking Signal - Actuals Greater than Forecast" |
| 3.4 | On ASL with On Order Not Categorized | None of 3.1–3.3 applies |
| 4 | On ASL without On Order | ASL = Y, On Order + In Repair = 0 |
| 5 | System Chose Not to Stock and Forecast Exists | ASL = N, no forcing override, forecast ≠ 0 |
| 6 | First Time Demand | No prior Demand History record |
| 7 | System Chose Not to Stock and No Forecast Exists | ASL = N, forecast = 0 |
| 8 | Not Categorized | No conditions met |

Notes on the table (same URL):
- The RR 327 lookback is set by servigistics.analytics.demandmiss.pastlookupdays = 30.
- Categories 3.1–3.4 are "planned ... in a future release for the Backorder Days dashboard".

======================================================================
5. AI / ML IN SERVIGISTICS
======================================================================
Infrastructure
- Data Science Workbench Administration page (new in 13.0.0.0): start and stop the SFTP and Zeppelin containers, and set credentials (Zeppelin must be restarted to apply them). [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/core/core_smart_help/sh_data_science_workbench.html]
- Page access requires one of the global settings ADVANCED_REPORTS, FUTURE1, or FUTURE19 = true, plus the user right "Data Science Workbench Administration". [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/core/core_smart_help/sh_data_science_workbench_2.html] [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/release_notes/release_13_0_0_0/rn_new_features_3.html]
- 13.0 AutoPilot processes for PAI [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/release_notes/release_13_0_0_0/rn_enhancements_8.html]:
  - AWS Zeppelin Start and AWS Zeppelin Stop (containers incur hourly AWS charges)
  - Correlated Parts Intelligence
  - Forecast Accuracy Intelligence
  - Machine Learning Forecasting ("Normally ... run on a few exceptionally high error SKUs"; the improved forecast can be exported and imported back)
  - Mean Time Between Failure
  - New Part Introduction Forecasting
- ML models run in Zeppelin Notebooks. Results flow back through Intellicus ETL Query Objects (QO_ETL_PAI_ML_*) into the Servigistics schema. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary_pai/etl.html]
- PAI 5.0 lets on-premises customers use ML without the Data Science Workbench (simplified deployment). [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/release_notes_pai/5000/rn_enhancements_13.html]

ML time-series forecasting
- Business scenario: trains and validates in the past over multiple iterations for SARIMA, BATS, Auto ETS, Prophet, and XGBoost, and selects the most accurate method. Dashboards: Forecasting Time Series Analysis and SKU Forecast Analysis. ETLs: QO_ETL_PAI_ML_FTS_TmpSKUS_* (input) and QO_ETL_PAI_ML_FTS_FcstDetailAndSKUStreamMetrics_* (output). [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary_pai/machine_learning_based_time_series_forecasting.html]
- Forecasting Time Series Analysis dashboard: the best-performing ML method system-wide and per SKU stream, with its metrics. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboard_forecasting_time_series_analysis.html]
- SKU Forecast Analysis dashboard: demand vs forecast for all evaluated methods, plus error types (mini-dashboards SKU Forecast Details and SKU Error Details). [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboard_sku_forecast_analysis.html]
- Core 13.1.0.0 "Machine Learning Best Fit Integration" [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/release_notes/release_13_1_0_0/rn_enhancements_fcst_2.html]:
  - Best Fit Analysis now compares the best ML method against the statistical methods.
  - New methods: "Servigistics ML" (the ML/deep-learning time series, whose method is chosen by the Machine Learning Forecasting AutoPilot) and "Servigistics ML Composite" (a blend of best statistical and best ML, weighted by Best Fit).
  - Setup: add both to Best Fit Methods on the Forecast Parameter, then run ML Forecasting, then Best Fit Forecasting, then Forecasting.
  - Optional "Force Servigistics ML Composite" = Yes.
  - Links from the Forecast Worksheet and Forecast Review page open the SKU Forecast Analysis dashboard.
- Servigistics ML Composite definition. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/servigistics_ml_composite_forecast_method.html]
- The History Based Simulator can include the Machine Learning Forecasting process (13.1). [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/release_notes/release_13_1_0_0/rn_enhancements_14.html]

Multivariate forecasting
- Predicts SKU-stream demand "using demand and multiple attributes or factors", including external factors "like weather data and economic factors". [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboard_multivariate_sku_forecast_analysis.html]
- Multivariate SKU Forecast Analysis widgets: Multivariate Error Metrics; Servigistics Error Metrics (comparison); Features Detail (feature importance in descending order, with a value plot and red/green dots for global min/max); Forecast. [same URL]

Explainability (feature importance and profiles)
- The docs contain no "explainability" term. Explanation is delivered through Feature Importance widgets on these dashboards:
  - Multivariate SKU Forecast Analysis [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboard_multivariate_sku_forecast_analysis.html]
  - Remaining Useful Life [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboard_remaining_useful_life.html]
  - Region MTBF Detail [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboard_region_mtbf_detail.html]
  - MTBF Cluster [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboard_mtbf_clusters.html]
  - Forecast Accuracy Intelligence [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboard_forecast_accuracy_intelligence.html]
- Forecast Accuracy Intelligence learns historical tracking signals from part, location, and demand attributes. It predicts future tracking signal and recommends "the combination of attributes that cause SKUs to over forecast or under forecast". [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary_pai/forecast_accuracy_intelligence.html]
- FAI mini-dashboards: Forecast Data Overview (tracking-signal spread), Forecast Feature Importance, and Profiles ("SKUs ... predicted to be highly, and consistently, over or under forecasted, with very high confidence"). [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboard_forecast_accuracy_intelligence.html]
- FAI parameters:
  - prediction_ts_threshold: change it and rerun if no profiles appear. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary_pai/prediction_ts_threshold.html]
  - sampling: W or MS. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary_pai/sampling.html]
  - slice_date. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary_pai/slice_date.html]

Forecast Override Intelligence / Recommendations
- An ML application "that advise[s] against potentially detrimental forecast overrides". It has no dashboard; it powers the Plan Intelligence messages. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary_pai/forecast_override_recommendations.html]
- Zeppelin parameters (same URL):
  - train_split_size = 0.75
  - feature_threshold = 0.8 (cumulative feature-importance cap)
  - col_missing_value_threshold = 0.5
  - override_recomm_threshold = 0.8 (minimum confidence)
- Output ETLs: QO_ETL_PAI_ML_FOI_*FcstDetailAndFeatureImportance_*. [same URL]
- Core 13.1.0.2 added the Forecast Override Intelligence AutoPilot and the message "A forecast override is not recommended" (fields: Stream, Confidence Level). [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/release_notes/release_13_1_0_2/rn_enhancements_fcst_3.html]
- PAI 5.0 describes it as beta. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/release_notes_pai/5000/rn_enhancements_10.html]

Plan Intelligence (IPWS)
- A tool on the Interactive Planner Worksheet. It highlights vendor average delay (closed-order history), unplanned average demand missed (demand detail history), and excess source locations for balancing orders. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/plan_intelligence.html]
- Enabling it [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/plan_intelligence_2.html]:
  - Set ENABLE_PLAN_INTELLIGENCE_IPWS = true.
  - Vendor Performance messages: PI_VENDOR_PERF_CALCULATE_PERIOD_MONTHS, PI_VENDOR_PERF_MIN_ORDERS, PI_VENDOR_PERF_RETAIN_SLICES_MONTHS, then run the Plan Intelligence AutoPilot.
  - Unplanned Demand Missed messages: PAI Advanced, plus servigistics.analytics.pi.demandmiss.calc.horizonslices and servigistics.analytics.pi.demandmiss.retainslices, then run Planning Analytics Generator.
  - Forecast Override Recommendations messages: PAI Advanced, then run Forecast Override Intelligence.
  - Optional Bing Maps, plus the Geo Locate AutoPilot.
  - Message thresholds can be set via PTC Technical Support.
- Message categories [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/plan_intelligence_3.html]:
  - Balancing Recommendations: "Create balance order from <location>".
  - Forecast Override Recommendations.
  - Unplanned Demand Missed: "Excessive unplanned demand misses", linking to Demand Miss Analysis. Fields: Actual FR, Planned FR, Delta FR, Unplanned Missed, Demand Missed, Review Age. Secondary message: backorder with RR 331.
  - Vendor Performance: "Excessive order delay by <vendor>", linking to the vendor dashboard. Secondary message: overdue host order RR 327.

RUL (Remaining Useful Life)
- "Predicts the remaining useful life or expected time until the next failure in the current repair cycle". Example: RUL of 5 days means the part will most likely fail in 5 days. Dashboards: Remaining Useful Life and RUL Detail. ETLs: QO_ETL_PAI_ML_RUL_*. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary_pai/remaining_useful_life_prediction.html]
- RUL dashboard: predicts failure dates of serialized items. Widgets: Predicted RUL Statistics (min/max/avg per Model), Predicted RUL Range, Feature Importance, Serial Number Distribution (trained/validated/predicted), Predicted RUL Summary (RUL, Predicted Failure Date, Serial). [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboard_remaining_useful_life.html]
- RUL Detail: graph plus Prediction Details per serial number. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboard_remaining_useful_life_detail.html]

MTBF, NPI, and correlated parts
- Region-Based MTBF Prediction: optimal failure rate per part per region, blending regional and global attributes. Compared with the Servigistics rate via MAPE, MAD, RMSE, and Accuracy, plus $Bias ML / $Bias SPM / Delta Bias. Includes Feature Importance. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary_pai/region_based_mtbf_prediction.html]
- Region MTBF dashboard. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboard_region_mtbf.html]
- New Part MTBF Prediction: ML-predicted MTBF for new parts. Dashboards: MTBF Cluster and New Part MTBF Prediction. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary_pai/new_part_mtbf_prediction.html]
- ML-based NPI forecasting: short-term forecasts for parts with no history. It matches similar parts on numerical and textual characteristics, then uses an ensemble of algorithms. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary_pai/machine_learning_based_new_parts_forecasting.html]
- New Part Introduction Forecasting dashboard. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboard_new_part_introduction_forecasting.html]
- Correlated Parts Intelligence: items frequently bought together, parts demanded together, probable kits, order-level fill rate. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary_pai/correlated_parts_intelligence.html]
- Correlated Parts Intelligence dashboard: associations, confidence, and attributes of Part A and Part B. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/functional/dashboard_correlated_parts_intelligence.html]

Causal factors
- "Causal" in the core product refers to the Causal Forecast pages (Causal Forecast Scenario, Product BOM, Failure Rate, Causal Value, Product Rollout). This is causal (install-base/failure-rate) forecasting, not ML. I only identified the files and did not read them in depth; example: [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/core/core_pid/pid_causal_forecast_scenario_page.html]
- The ML equivalent of external factors is Multivariate forecasting (above).

======================================================================
6. PAI 5.0.0.0 RELEASE NOTES: EVERY ENHANCEMENT
======================================================================
Overview: "performance improvements, usability improvements, and bug fixes for PAI Foundation, PAI Advanced, and Machine Learning dashboards." [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/release_notes_pai/new_in_r5000.html]

Enhancement index: New Dashboards; Demand Miss Analysis Dashboard Improvements; Fill Rate Analysis and Service Group Fill Rate Detail Dashboard; SKU Supply Chain History Dashboard; Improved Forecasting Dashboards Workflow; New ML Time Series Forecasting Algorithm; ML Based Multivariate; RUL Prediction; Forecast Override Intelligence; Regional MTBF Improvement; Service Group Fill Rate Detail Dashboard; Technical. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/release_notes_pai/5000/rn_enhancements.html]

1. New Dashboards [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/release_notes_pai/5000/rn_enhancements_2.html]
   - Vendor Forecast: a vendor-collaboration dashboard sharing vendor capacity and procurement/repair order projection, plus Service Impact Score and spend history.
   - Vendor Prioritization and Performance: prioritizes vendors by Service Impact score, with spend history and projection.
   - Usability: the "IO Stockable" filter was renamed "Stockable".

2. Demand Miss Analysis Improvements [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/release_notes_pai/5000/rn_enhancements_3.html]
   - Root cause 3 (On ASL with On Order) is split into 3.1 Vendor Delays, 3.2 Vendor Delays at Procuring Location, 3.3 Under Forecast, and 3.4 Not Categorized.
   - Applies to Demand Miss Analysis, SKU Supply Chain History, Performance 360 Backorder Categories, and the Backorder Categorization report.
   - Setting: servigistics.analytics.demandmiss.pastlookupdays = 30 (RR 327 lookback).
   - Upgrade note: historical data is not recalculated, so past misses appear under 3.4.

3. Fill Rate Analysis and Service Group Fill Rate Detail [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/release_notes_pai/5000/rn_enhancements_4.html]
   - Widgets renamed from "Highest ..." to "... Summary". Examples: "SKU with Highest Demand Missed" became "System Level – SKU with Demand Missed Summary"; "Service Group Delta Fill Rate Trend" became "Top 5 Service Groups by Highest Delta Fill Rate"; "Service Group Demand Missed Trend" became "Top 5 Service Groups by Highest Missed".
   - Filters moved to the top of the dashboard, and a Service Group filter was added.
   - New columns: Total, Unplanned Missed (red), Total Line, Unplanned Line Missed (red).
   - "Demand Missed" renamed to "Missed".

4. SKU Supply Chain History [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/release_notes_pai/5000/rn_enhancements_5.html]
   - "Unmet Demand" renamed to "Demand Missed".
   - Data tab adds Net On Hand Good and Planned Quantity.
   - New graph tab Demand Missed (Demand Missed, Net On Hand Good, Total Demand, Vendor Delays with OnOrder).
   - New graph tab Inventory Projection (Net On Hand Good, On Order, Chain Acquired/Relinquished, Order Sent, Safety Stock, ROP, Stock Max, Inventory Position).

5. Improved Forecasting Dashboards Workflow: SKU-level dashboards now clearly show the selected Part/Location filters when you navigate down from System or Part level. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/release_notes_pai/5000/rn_enhancements_6.html]

6. New ML Time Series Algorithm: a univariate "Xg-Boost" method was added to the ensemble. Hyper-parameters xgb_n_trees, xgb_depth, and xgb_learning_rate are set in the Zeppelin Notebook. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/release_notes_pai/5000/rn_enhancements_7.html]

7. ML Based Multivariate: forecasts from demand plus external factors (weather, economic). New dashboard: Multivariate SKU Forecast Analysis. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/release_notes_pai/5000/rn_enhancements_8.html]

8. RUL Prediction: ML-based RUL of serialized items from utilization, operational, and/or sensor data. Released as beta for evaluation; found under Analytics > Forecast Intelligence. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/release_notes_pai/5000/rn_enhancements_9.html]

9. Forecast Override Intelligence: "Machine learning based recommendation against potentially detrimental forecast overrides", released as beta. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/release_notes_pai/5000/rn_enhancements_10.html]

10. Regional MTBF Improvement [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/release_notes_pai/5000/rn_enhancements_11.html]
    - Region MTBF: new report of RMSE improvement when ML MTBF/Failure Rate is used instead of global. The Part Summary shows both MTBF and Failure Rate (configurable).
    - Region MTBF Detail: new MTBF/Failure Rate widget with tabs. MTBF, Failure Rate, and error metrics added to the Detail Prediction report (ML vs Global).

11. Service Group Fill Rate Detail: separate tiles for Demand and Lines, "...Summary" widget renames, Unplanned Missed and Unplanned Line Missed columns (red), and "Demand Missed" renamed to "Missed". [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/release_notes_pai/5000/rn_enhancements_12.html]

12. Technical [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/release_notes_pai/5000/rn_enhancements_13.html]
    - On-prem ML without the Data Science Workbench.
    - PAI ML now uses the Servigistics system date.
    - Intellicus connection names: Reportdb is now PAIFoundationDefault; Repositorydb is now RepositoryDB.
    - PAI Advanced on Oracle can run on a separate database.
    - Single Report Objects can be published by command.
    - Log purge size and backup index for ReportEngine (case 17184183).
    - Removing obsolete AOs (case 17090903).
    - New property servigistics.analytics.demandmiss.pastlookupdays (set to 30) in the WebUI and AutoPilot property files.

Resolved issues listed in the 5.0.0.0 notes include PAI-8241, 8270, 8264, 8402, 8819, 8351, and 8880, among others. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/release_notes_pai/new_in_r5000.html]

======================================================================
7. PAI 5.0.0.1 RELEASE NOTES: EVERY ENHANCEMENT
======================================================================
Index: Disable Archiving Tables; Eliminate Excessively Trending Forecasts; Automatic System Date Configuration for Forecast Accuracy Intelligence; Online Help Updates. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/release_notes_pai/5001/rn_enhancements.html]

1. Disable Archiving Tables: new system property servigistics.analytics.archive.tables.mode with values STANDARD, CUSTOM (IPCS_ANALYTICS_CUSTOM_TABLE_INFO), or ALL (default). [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/release_notes_pai/5001/rn_enhancements_2.html]

2. Eliminate Excessively Trending Forecasts [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/release_notes_pai/5001/rn_enhancements_3.html]
   - An excessive upward trend in an ML time-series forecast is "flagged as high-risk in the SKU Forecast Analysis dashboard".
   - Any high-risk ML method "is automatically removed from the best-fit selection process" for that SKU.

3. Automatic System Date for FAI (case 17518634): QO_PAI_ML_FAI_UnderFcstByTS and QO_PAI_ML_FAI_OverFcstByTS now take the system date from Servigistics tables. Parameter Object PO_PAI_ML_FAI_SliceDate was removed. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/release_notes_pai/5001/rn_enhancements_4.html]

4. Online Help Updates: added the topics Remaining Useful Life Prediction, Remaining Useful Life, and Remaining Useful Life Detail. [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/release_notes_pai/5001/rn_enhancements_5.html]

Resolved issues in 5.0.0.1: PAI-9799 (17315522), PAI-9944 (17438365), PAI-9996 (17482491), PAI-10129 (17518634). [https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/release_notes_pai/new_in_r5001.html]

======================================================================
GAPS
======================================================================
- No formula for Service Impact Score beyond the AO measure "Sum of Systemimpact".
- No "explainability" or "artificial intelligence" wording anywhere in the corpus. Explanation is only through Feature Importance widgets and FAI Profiles.
- The Causal Forecast pages were identified by filename but not read in depth.
- Widget-level `_2` pages (e.g. functional__dashboard_*_2.html.txt) were not read.