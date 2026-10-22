# PTC Servigistics release notes, 13.0.1.0 to 13.1.0.5: enhancements and settings

I read every in-scope file: the 12 `new_in_*` overview pages, all `release_13_0_1_*` and `release_13_1_0_*` enhancement, performance, technical and technical-notes pages, and the 16 `rn_*_features_13_0_1_*` pages. The `rn_*_features` pages are only index stubs that list "Enhancements" and carry no content of their own.

**How URLs are written below.** Every source URL starts with this base, which is left out:
`https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/release_notes/`
So `release_13_0_1_0/rn_enhancements_3.html` means `<BASE>release_13_0_1_0/rn_enhancements_3.html`, and `new_in_13_0_1_0.html` means `<BASE>new_in_13_0_1_0.html`.

**Resolved issues (counted only, not read).** The number is the count of JIRA rows in each `resolved_issues_*` page:

| Release | Resolved issues |
|---|---|
| 13.0.1.0 | 29 |
| 13.0.1.1 | 11 |
| 13.0.1.2 | 22 |
| 13.0.1.3 | 16 |
| 13.0.1.4 | 4 |
| 13.0.1.5 | 6 |
| 13.1.0.0 | 87 |
| 13.1.0.1 | 17 |
| 13.1.0.2 | 13 |
| 13.1.0.3 | 12 |
| 13.1.0.4 | 18 |
| 13.1.0.5 | 13 |

**How 13.1.0.0 relates to 13.0.1.x.** Many 13.1.0.0 notes repeat features first shipped in 13.0.1.1 to 13.0.1.4. These include:
- Network Optimization Rules
- Disaggregation Type
- Sustainability
- Stockout Costs
- Order Sizing
- Calendar Adjustments
- `ENABLE_PROPERTYGRID_GRIDLINES`
- `INVENTORY_STUDIO_MAP_DISPLAY`
- `OP_COUNT_SALES_RETURNS_THROUGH_HORIZON`
- the Geo Locate properties

13.1.0.0 is the 13.1 line absorbing the 13.0.1.x patches. Those items are listed under both releases below and marked "(also in 13.0.1.x)".

---

## 13.0.1.0

Overview page: `new_in_13_0_1_0.html`
- New global settings: `ENABLE_EXPORT_NUMBER_FORMAT`, `OP_TIME_PHASED_ROP_USES_TIME_PHASED_ROP_FAIRSHARE`.
- Updated global settings: `ENABLE_PRC_OFFSET_MANAGEMENT`, `ENABLE_PINNING_ALL_LOCATIONS`, `OP_FAIRSHARE_SORT_CRITERIA_1` to `_4`.

### Common / General
- **Documentation Updates.** The help for the Refresh Planner/Part 360° AutoPilot process now says when the process should be run. `release_13_0_1_0/rn_enhancements_2.html`
- **Geo Locate Improvements** (case 16804620). Geo Locate now accepts an inexact match at a level (address, then postal code, city, state, country) if its quality beats the next level; before, it discarded it and dropped to postal code. It also fixed Geo Locate running before Get Host Data. `release_13_0_1_0/rn_enhancements_3.html`
- **Improvements to the Data Manager Page.**
  - New entities: Causal Forecasting Causal Type and Forecast Disaggregation Weight Overrides.
  - New Export All Rows to CSV / Excel. Exports use label names and respect `MAX_EXPORT_ROWS`; very large exports need a bigger WebUI heap.
  - Custom Attribute label names now appear in export headers (cases 14123017, 16016223, 16282878).
  - `release_13_0_1_0/rn_enhancements_4.html`
- **Inventory Studio Page (new).** A single page for dealers, distributors and customers to manage inventory at one or all of their locations. They can approve, alter or reject OEM buy/return/transfer recommendations, order parts, and locate parts at other locations. Access is controlled by User Rights. `release_13_0_1_0/rn_enhancements_5.html`
- **New Global Setting to Control the Export of Numeric Fields** (cases 16282852, 16350484, 16368557). `ENABLE_EXPORT_NUMBER_FORMAT`: true exports numbers as numeric fields (usable in formulas); false exports them as text. Default false; applies system-wide. `release_13_0_1_0/rn_enhancements_6.html`
- **Next Generation View Display.** Now fully functional on the IPWS Deployments tab, Inventory Studio, Location Summary and What-If Model. `release_13_0_1_0/rn_enhancements_7.html`
- **Priority List Updated for Review Reason Subscriptions.**
  - The default Review Subscriptions list was reordered: 325 New recommended balancing orders, 332 New recommended excess recall orders, 320 Planned On Hand Good below 0.
  - 345 (Today's IP at or below ROP) was removed from the default list.
  - `release_13_0_1_0/rn_enhancements_8.html`

### Forecasting
- **Best Fit Process Run Improvement** (case 16366816). The Best Fit run now allows a negative Trend % for the Same As Last Year method. `release_13_0_1_0/rn_enhancements_fcst_2.html`
- **Life Limited Parts (LLP) Maintenance Forecasting.** Forecasts service events for life-limited parts at serial-number level. It uses host causal history (flight hours/cycles) and the maximum life limits.
  - New forecast methods: *LLP Maintenance – Raw* (the need from scheduled maintenance) and *LLP Maintenance – Smooth* (the raw amount smoothed to maintenance-center capacity; excess is pulled to earlier slices, and any remainder goes in the earliest slice).
  - New AutoPilot process: Maintenance Forecast Detail (serial, SKU and Part levels). The Forecasting process copies the SKU-level forecast into `IPCS_FORECAST_DETAIL`.
  - New page: Life Limited Parts Forecast Details. The methods also appear on the Forecast Worksheet and in stream configuration.
  - `release_13_0_1_0/rn_enhancements_fcst_3.html`
- **New Forecast Method — Servigistics TSB.** A Teunter-Syntetos-Babai method for intermittent demand: it replaces Croston's demand interval with a demand probability updated every period.
  - On Forecast Parameters, the "Use Intermittence Smoothing Instead of Crostons" setting was replaced by *Select Forecast Method for Intermittent Demand* (Intermittent Smoothing / Croston / Servigistics TSB).
  - New TSB Alpha/Beta fields, plus an *Allow Servigistics TSB* option in Best Fit Methods.
  - TSB is also selectable on Parameter Settings, the Forecast Worksheet and Best Fit pop-up, Forecast Review filters, and Stream Configuration Detail.
  - `release_13_0_1_0/rn_enhancements_fcst_4.html`
- **Row Links Added to Replacement Rate Details Page.** New row links "Forecast Worksheet for Part" and "Forecast Worksheet for Included Part" open the IPWS Forecast tab for that part and location. `release_13_0_1_0/rn_enhancements_fcst_5.html`
- **Improved Response Time of Forecast Review Page** (performance). The record-count query falls back to `MAX_ROW_ERROR_LIMIT` when it runs longer than 10 seconds. `release_13_0_1_0/rn_performance_fcst_2.html`
- **Navigation to PAI dashboards** (overview page only). The IPWS Go to menu gains PAI Advanced Part, Location and SKU dashboards. Details are under SP "Interactive Planner Worksheet Improvements" below. `new_in_13_0_1_0.html`

### Inventory Optimization
- **Demand Weighted Composite Lead Time.** Adds `MEO_REPAIR_TYPE` = 3 (Demand Weighted Mode), which weights the composite lead time by demand conditions (Return and Repair Wash Rates, NRTS, NFF, hierarchy). The other values are 1 = Serial (not recommended, kept for backward compatibility with Levels) and 2 = Aggregate (wash-rate weighted, ignores demand). 3 is the default for new installs; 2 remains for existing customers, and PTC recommends upgrading sites switch to 3 manually. `release_13_0_1_0/rn_enhancements_io_2.html`
- **Emergency Backup Location Optimization Changes.**
  - SKUs whose resupply location is the emergency backup, with local repair or NFF supply sources, can now take part.
  - Hierarchy-navigation techniques were changed, and the scenario's Fill Rate method replaces the Lost Sales Fill Rate method (more conservative).
  - Summarization is faster.
  - `release_13_0_1_0/rn_enhancements_io_3.html`
- **Fields Removed from Lead Time Inputs** (Stocking Policy, SKU Summary tab). Pass Up Rate and Condemnation Rate were removed. `release_13_0_1_0/rn_enhancements_io_4.html`
- **Prioritized Buy List** (case 16657158). Shows the network exchange curve (new buy cost vs availability, backorders, fill rate and wait time) as steps: mandatory new buy, then SKU minimums and overrides, then discretionary increments up to the final mix. A per-part buy list shows the incremental investment at each step. Adds a Prioritized Buy List user right, a *Generate Prioritized Buy List* scenario checkbox, and a Prioritized Buy List page. To see the full path, leave budget constraints off the scenario. `release_13_0_1_0/rn_enhancements_io_5.html`
- **Reorganized Field Groupings on the Create/Edit Scenario Window.** Fields regrouped for ease of use. `release_13_0_1_0/rn_enhancements_io_6.html`
- **What-If Modeling {Beta}.** New What-If Model page (containers: What-If Model, Details, Assigned Segments, Assigned SKUs) and a What-If Model user right (View / View and Modify).
  - A scenario can reference a model; changing it flags the scenario for recalculation.
  - New fields: What-If Model, What-If SKU (count of impacted SKUs), and Modified by What-If (Y/N).
  - `release_13_0_1_0/rn_enhancements_io_7.html`

### Pricing
- **Consistent Naming of Rule Sets Folder.** "Rule Folder Name" and "Business Rule Sets Folder" became "Rule Sets Folder" on Find Business Rules and Pricing Business Rules. `release_13_0_1_0/rn_enhancements_pricing_2.html`
- **Fields Added to Price Book.** Price Action Comment and Price Change Reason were added to the Pricing Worksheet Price History pop-up and to `IPCSDU_PRICE_BOOK`, `IPCS_PRICE` and `IPCSDD_PRICE`. `release_13_0_1_0/rn_enhancements_pricing_3.html`
- **More Information in Reject Process Summary Pop-up.** The Approval/Upload/Reject summary (opened from the Price Actions Action Reports tab) now shows the user name, the rejection level and the approval/rejection reason text. `release_13_0_1_0/rn_enhancements_pricing_4.html`
- **Name Changes for Price Offset Management.**
  - Pages: Price Offset Management became Configurable Price Offset Codes; Price Offset Code became Configurable Price Offset Code; Price Offset Details became Configurable Price Offset Details.
  - AutoPilot process: Price Offset Management became Apply Configurable Price Offsets.
  - Global setting: `ENABLE_PRC_OFFSET_MANAGEMENT` became `ENABLE_CONFIGURABLE_PRICE_OFFSET_CODES`.
  - The user right was renamed the same way.
  - `release_13_0_1_0/rn_enhancements_pricing_5.html`
- **Part List Visibility on Pricing Worksheet** (case 16721341). New Part Lists tab, with links to Part List Details. `release_13_0_1_0/rn_enhancements_pricing_6.html`
- **Policy Name in Stream Prices section** of the Pricing Worksheet. `release_13_0_1_0/rn_enhancements_pricing_7.html`
- **Warning Message for Policy Effective Date.** The Pricing Policy Definition tab warns when the Effective Date is earlier than today. `release_13_0_1_0/rn_enhancements_pricing_8.html`

### Supply Planning / Order Planning
- **Additional Comparative Analytics Pages.** Nine new Order Plan Comparison Detail pages: By Part, For Part (one part across locations) and By SKU, each for Full Horizon, Today and 13 Week. `release_13_0_1_0/rn_enhancements_sp_2.html`
- **Balancing Uses Order Date for Excess.** Time-Phased Safety Stock and Time-Phased ROP balancing now compute source excess from stock levels on the order date, not the available date. `release_13_0_1_0/rn_enhancements_sp_3.html`
- **Enable Pinning Location on IPWS Orders Container** (case 16665493). `ENABLE_PINNING_ALL_LOCATIONS` was renamed `ENABLE_LOCATION_PINNING`.
  - true: "All" keeps orders for all locations shown even when the toolbar location changes; choosing a single location makes the container follow the toolbar location.
  - false: the pin-all option is removed.
  - `release_13_0_1_0/rn_enhancements_sp_4.html`
- **Fair Share Default Sort Criteria.** New-install defaults: `OP_FAIRSHARE_SORT_CRITERIA_1` = q and `_2` = f (previously null); `_3` and `_4` stay null. Upgrades must set these manually. Ties are allocated in proportion to need, with LocID as the final tie-break. `release_13_0_1_0/rn_enhancements_sp_5.html`
- **Import of Promised Ship Date** (case 16637054). `PromisedShipDate` was added to `IPCSDD_ORDER_PLAN`. `release_13_0_1_0/rn_enhancements_sp_6.html`
- **Interactive Planner Worksheet Improvements.** New toolbar tabs for Part 360° and Part Health. The Go to menu adds PAI Forecast Analysis plus Part, Location and SKU Forecast Analysis – Advanced. `release_13_0_1_0/rn_enhancements_sp_7.html`
- **Order Sizing for Trigger Point Order Policy** (cases 16588570, 16717165). Uses the Time-Phased ROP technique: with an order sizing rule, order up to ROP+1 and then apply the rule; without one, order up to Stock Maximum. MOQ does not count as a sizing rule here. `release_13_0_1_0/rn_enhancements_sp_8.html`
- **Outside Horizon Indicator on Time Series Grid** (case 16601524). Slices beyond Days To Generate Orders are shaded gray. `release_13_0_1_0/rn_enhancements_sp_9.html`
- **Stock Maximum as Excess Limit for Trigger Point.** Trigger Point uses Stock Maximum as the excess limit instead of computing Stock Max For Excess. `release_13_0_1_0/rn_enhancements_sp_10.html`
- **Time-Phased ROP Improvements.** `release_13_0_1_0/rn_enhancements_sp_11.html`
  - Balancing uses Repair ROP when Balance Before Repair = Yes and the SKU is repairable.
  - Improved Fair Share backorder pass, controlled by `OP_TIME_PHASED_ROP_USES_TIME_PHASED_ROP_FAIRSHARE` (default true).
  - New *Output Generated Orders* option on the Ordering Parameters General tab (shown when `OP_TIME_PHASED_ROP_ENABLE` = true). Values: All Orders For All Locations; All Orders For Repair and Procure Locations with Today's Orders for all others; Today's Orders For All Locations. Each SKU can have its own DaysToGenOrders, with forecast rolled up after that day.
  - Schedule Change Suppression (SCS) now works with TP-ROP, with TP-ROP-specific tabs on the SCS page, Parameter Settings and the SKU page.
  - New rows on the Time Series Grid, IP Summary and Daily Detail IP Report: Unadjusted Safety Stock (ROP − OnOrderMean), and SCS Safety Stock Minimum, SCS ROP Minimum and SCS Stock Maximum for both Procurement and Repair.

---

## 13.0.1.1

Overview page: `new_in_13_0_1_1.html`. New and updated global settings: none.

### Common
- **Demand History Management Job Added to OTF Rights.** Added for Demand Dashboard and PWS, so the job can run from the IPWS Forecast tab and the Demand Detail page when `FCST_RUN_HIST_ANALYTICS` = false. Selected by default on new installs, not selected on upgrades. `release_13_0_1_1/rn_enhancements_2.html`
- **History Based Simulator Enhancement.** Initial stock is now On Hand Good = Stock Maximum and On Hand Bad = 0. `release_13_0_1_1/rn_enhancements_3.html`

### Inventory Optimization
- **Network Optimization Rules.** New Network Optimization Rules page for defining overrides to install base coverage assignments. A Rule field on the Network Optimization Scenario Coverage tab shows the rule that was applied, and the workflow was updated. `release_13_0_1_1/rn_enhancements_io_2.html`

### Supply Planning
- **Global Last Time Buy Quantity on the LTB Recommendation page.** Shows the network-total LTB quantity on the General and Allocation tabs, taken from the global location. `release_13_0_1_1/rn_enhancements_sp_2.html`
- **Hyperlinks on Order Plan Comparison pages.** On the By SKU Full Horizon, 13 Week and Today pages, Current Quantity and Backup Quantity link to the IPWS for that SKU. `release_13_0_1_1/rn_enhancements_sp_3.html`
- **Time-Phased ROP Enhancements.** `release_13_0_1_1/rn_enhancements_sp_4.html`
  - Order Spreading now supports TP Safety Stock: closure-period need is spread across existing orders within the spread length, or a new order is created just before the closure.
  - It also supports TP-ROP: need is spread back over the spread length and can be met by any order type.
  - New "Order Spreading Need" row on the IP Summary and Daily Detail IP Report.
  - The six SCS rows were added to the Time Series Graph.

---

## 13.0.1.2

Overview page: `new_in_13_0_1_2.html`. New global setting: `OP_COUNT_SALES_RETURNS_THROUGH_HORIZON`.

### Common
- **Configurable Go To Menu** (cases 16922120, 16922178, 16923058). Configurable on the IPWS Forecast and Plan tabs, Forecast Review and the Pricing Worksheet.
  - The dropdown has four sections. PAI Foundation and PAI Advanced links show or are accessible depending on which is configured.
  - Requires `ADVANCED_REPORTS` = true and `FUTURE36` = true. An administrator reorders or adds items.
  - `release_13_0_1_2/rn_enhancements_2.html`
- **Consistent Naming of Review Reasons.** "Review Name" / "Name" became "Review Reason" on Review Types, the Review Board (Plan and Forecast tabs), Planner/Part 360° containers, Work Queue and the Pricing Dashboard. `release_13_0_1_2/rn_enhancements_3.html`
- **Introduction of Sample Workflows** (help). Adds Planning by Exception (Daily Planner) and Detailed SP Ordering Workflow; help pages link to workflow steps. `release_13_0_1_2/rn_enhancements_4.html`
- **View Additional Information on Inventory Studio.** List rows can be expanded to show more detail. `release_13_0_1_2/rn_enhancements_5.html`

### Forecasting
- **Disaggregation Type on Forecast Disaggregation Parameters** (case 16700297). Even (the Demand Aggregation process splits weights evenly across child locations) or Proportional. `release_13_0_1_2/rn_enhancements_fcst_2.html`

### Inventory Optimization
- **Field Name Changes.**
  - Average Inventory became Expected On Hand.
  - Average Inventory Value became Expected On Hand Value.
  - Average Inventory Value (Optimized) became Expected On Hand Value (Optimized).
  - Expected On Hand and Expected On Hand Value were added to Performance Summary on the Stocking Policy SKU Summary tab.
  - `release_13_0_1_2/rn_enhancements_io_2.html`
- **Network Optimization Enhancements.** Rules that override install base coverage (as in 13.0.1.1). Cross-border wait times: a new *Hours to Cross* field on Country Borders, added to the response time; include every crossing on the route (case 16852029). `release_13_0_1_2/rn_enhancements_io_3.html`

### Supply Planning
- **Full Option on Procurement / Repair / Replenishment pages documented** (case 17008087). Approve/disapprove scope is Selected / All loaded / Full (includes rows not displayed). Availability is governed by `ALLOW_MASS_APPROVAL_TO_CO_ORDERS`, `MAX_ROWS_FOR_FULL_OPERATION` and `RS_MAX_PAGES`. `release_13_0_1_2/rn_enhancements_sp_2.html`
- **Last Time Buy Improvements.** Approving an already-approved recommendation now shows a warning. Disapproving deletes the orders and sets the status to "In Progress – Recommendation". `release_13_0_1_2/rn_enhancements_sp_3.html`
- **Order Sizing Enhancements** (Trigger and TP-ROP). Order Plan no longer orders above Stock Maximum: it picks the largest valid rule-sized quantity ≤ the need up to Stock Maximum. If none exists, the sizing rules are skipped and it orders up to Stock Maximum. New Review Reasons for ROP/Stock Max conflicts with sizing rules: 346 (procurement), 347 (repair), 348 (replenishment). `release_13_0_1_2/rn_enhancements_sp_4.html`
- **Sales Return Outside Return Lead Time considered in Order Plan** (case 16986583). New `OP_COUNT_SALES_RETURNS_THROUGH_HORIZON` (default true): true counts all actual sales returns through the horizon in IP; false counts only up to the return lead time (exclusive). `release_13_0_1_2/rn_enhancements_sp_5.html`

---

## 13.0.1.3

Overview page: `new_in_13_0_1_3.html`. New global settings: `CARBON_MEASURE_TYPE`, `ENABLE_PROPERTYGRID_GRIDLINES`, `INVENTORY_STUDIO_MAP_DISPLAY`, `IO_CALCULATE_SUSTAINABILITY`.

### Common
- **Documentation Updates** (case 17014604). The ABC Classification final results chart was updated. `release_13_0_1_3/rn_enhancements_2.html`
- **Geo Locate Improvements** (case 17116260). Two WebUI properties to catch bad Bing geolocation results:
  - `servitistics.map.location.fail.multiple` (typo as in the source; default true) treats multiple results as a failure.
  - `servigistics.map.location.verify.country` (default true) checks that the returned country matches the requested one.
  - `release_13_0_1_3/rn_enhancements_3.html`

### Forecasting
- **Property to Enable/Disable Automated Dataset Comparison Pages.** Setting WebUI property `servigistics.intellicus.automated.comparison.categoryid` = Modeling shows the Automated Dataset Comparison pages under the Modeling menu. `release_13_0_1_3/rn_enhancements_fcst_2.html`

### Inventory Optimization
- **Next Generation View** enabled on Scenario Budget Summary. `release_13_0_1_3/rn_enhancements_io_2.html`
- **Sustainability.** Carbon reporting across IO. `release_13_0_1_3/rn_enhancements_io_3.html`
  - Input fields on IO Planning Parameters, Parts, SKU and elsewhere: Embodied Carbon Per New Buy / Per Repair, and Transportation Carbon Per Standard Order / Per Expedited Order / Per Repair.
  - Output fields on the summary pages: Embodied Carbon (New Buy / Repair), Transportation Carbon (Standard / Expedited / Repair), and Supply Shipment Regular / Expedited (units and lines).
  - New global settings: `CARBON_MEASURE_TYPE` (label, default "kg of CO2e") and `IO_CALCULATE_SUSTAINABILITY` (shows the Carbon Footprint row, default false).
  - The IO Planning Parameters window gains Optimization Costs and Sustainability tabs; "Reorder Quantity and Stockout Cost Settings" was renamed "Reorder Quantity".
  - New Sustainability container on Stocking Policy.
  - Budget Summary pages gain Stockout, Resupply Quantity and Carbon Footprint rows plus a Carbon Footprint chart; the "Over Time" suffix was removed.
- **Visibility Enhancements to Stockout Costs.** New fields Customer Backorder Days (Wait Time) and Customer Demands (Fill Rate) across the summary pages. New Stockout Costs container on Stocking Policy showing Stockout Cost and Stockout Unit Cost for both Fill Rate and Wait Time. `release_13_0_1_3/rn_enhancements_io_4.html`

### Supply Planning
- **Grid Lines on the IPWS Order/SKU Parameters container** (case 17134765). Controlled by `ENABLE_PROPERTYGRID_GRIDLINES` (default false). `release_13_0_1_3/rn_enhancements_sp_2.html`
- **Inventory Studio Part Locator Map.** A Bing map on the Parts → Part Locator subtab shows locations holding the part. A pin pop-up shows available quantity, distance and an Order button. Requires `INVENTORY_STUDIO_MAP_DISPLAY` = true (default true) and the WebUI property `servigistics.bingmap.licensekey`. `release_13_0_1_3/rn_enhancements_sp_3.html`

---

## 13.0.1.4

Overview page: `new_in_13_0_1_4.html`. New global settings: `OP_TIME_PHASED_ROP_CALENDAR_ADJUSTMENTS_AT_TOP_MOST_LOC_ONLY`, `OP_TIME_PHASED_ROP_CALENDAR_ADJUSTMENT_IO_LEAD_TIME_INCREASE`.

### Supply Planning
- **Time-Phased ROP Calendar Adjustments** (case 17228061). The calendar adjustment algorithm was rewritten to fix over-ordering. It now combines process, transport and put-away time with all applicable calendars. `release_13_0_1_4/rn_enhancements_sp_2.html`
  - Renamed fields:
    - Calendar Need became Need Until Next Available Date (NUNAD).
    - Previous Calendar Need Adjustment became Calendar Lead Time Adjustment.
    - Downstream Calendar Need became Downstream Need Until Next Available Date (not in use).
  - New global settings:
    - `..._AT_TOP_MOST_LOC_ONLY` (default true): Order Plan adjusts for calendars only at top-most locations.
    - `..._IO_LEAD_TIME_INCREASE` (default 7 days): the closure gap that IO already covers. Use 14 for bi-weekly ordering, or 0 to let Order Plan handle all restrictions.

---

## 13.0.1.5

Overview page: `new_in_13_0_1_5.html`. New and updated global settings: none.

### Supply Planning
- **Ordering Enhancements: Transportation Mode for manual orders** (case 17249240). Manual Balancing orders now use the same transport mode as manual Replenishment orders instead of the default mode. `release_13_0_1_5/rn_enhancements_sp_2.html`

### Technical / Performance
- **Oracle parameters** (SPM-110851). `parallel_degree_policy=ADAPTIVE` and `parallel_min_time_threshold=2` improve performance on well-resourced systems. `release_13_0_1_5/technical_notes_13_0_1_5.html`

---

## 13.1.0.0

Overview page: `new_in_13_1_0_0.html`. This overview has no global-settings list; settings are given on each feature page.

### Common / General
Index: `release_13_1_0_0/rn_enhancements.html`
- **Toolbar Improvements.** Industry-standard icons, functional grouping, labels and spacing. IPWS buttons were consolidated (e.g., Reports and Export Gap Data moved under grouped buttons). `rn_enhancements_2.html`
- **Configurable Go To Menu** (also in 13.0.1.2). `rn_enhancements_3.html`
- **Best Practice Workflows** ("Process Workflows" help section). Planning by Exception and the Detailed SP Ordering workflow. `rn_enhancements_4.html`
- **FAQs.** New help section. `rn_enhancements_5.html`
- **All Ad Hoc Reports Displayed in Analytics Menu** (case 16877235). Intellicus reports with Design Mode = Ad Hoc now appear in the Analytics menu. `rn_enhancements_6.html`
- **Apply Return Wash Rate and Return Lead Time to Non-Repairable SKUs of a Repairable Part.** New `APPLY_RETURN_WR_NON_REPAIR_LOC` (default false). When true, the Return Wash Rate is used for a non-repairable child that has a repairable ancestor, giving more accurate pipelines. Used by Forecasting, IO and SP. `rn_enhancements_7.html`
- **Circular Reference Finder** (case 16738825). New AutoPilot process that finds parent/child loops in any hierarchical table and writes them to an output table. Purge age is set by `CIRCULAR_REFERENCE_RETENTION_DAYS`. Table setup requires Technical Support. `rn_enhancements_8.html`
- **Consistent Naming of Review Reasons** (also in 13.0.1.2; adds Rotable Levels). `rn_enhancements_9.html`
- **Demand History Management Job in OTF Rights** (also in 13.0.1.1). `rn_enhancements_10.html`
- **Documentation Updates.** Order Plan – Order History field definitions (case 16883633); ABC chart; Cities became Cities/Regions and State became States. `rn_enhancements_11.html`
- **Entities Added to Data Manager** (case 14969214). Vendor Location SKU LT. `rn_enhancements_12.html`
- **Geo Locate** (also in 13.0.1.3; same two WebUI properties). `rn_enhancements_13.html`
- **History Based Simulator.** On Hand Good = Stock Maximum and On Hand Bad = 0. The processes Demand History Management, Demand Aggregation and Machine Learning Forecasting are now configurable. `rn_enhancements_14.html`
- **Next Generation View.** Collapse/expand of detail columns (Scenario Budget Summary only). Enabled on Scenario Budget Summary and SKU Summary. The toolbar toggle appears when `ENABLE_ADVANCED_GRID` = true and replaces Additional Data / Exception Criteria with a Layout button. `rn_enhancements_15.html`
- **User Rights Setup Tab for Dealers** (case 16600474). A Dealer tab applies automatically to users with the Dealer role or template; the other tabs have no effect for dealers. `rn_enhancements_16.html`

### Forecasting
Index: `release_13_1_0_0/rn_enhancements_fcst.html`
- **Machine Learning Best Fit Integration.** New methods: *Servigistics ML* (the best of SARIMA, BATS, Auto ETS, Prophet and XGBoost, chosen by the Machine Learning Forecasting process) and *Servigistics ML Composite* (a blend of the best statistical and best ML forecast, weighted by Best Fit). Requires PAI Machine Learning. Add the methods to the Best Fit Methods list, then run ML Forecasting, Best Fit Forecasting and Forecasting. A *Force Servigistics ML Composite* setting (Yes) always uses the Composite method. `rn_enhancements_fcst_2.html`
- **Reduced Forecast Method Churn In Best Fit.** New *Error Improvement %* on Forecast Parameters (default 10; 0 on upgrades, where 0 means no threshold). Best Fit switches methods only if the new metric is at least x% better. `rn_enhancements_fcst_3.html`
- **Enhanced SKU Overrides** (cases 14514462, 16954727). Annual Forecast Override at SKU-Stream level, spread over the next 12 months in proportion to the raw forecast; user period adjustments are kept, and it overrides Adjustment Profiles. New Adjustment Operation options: Replace, Increase/Decrease By Value (Increase By Value is the default), Increase/Decrease By Percent. Priority: period adjustment, then annual override, then segment Adjustment Profile. `rn_enhancements_fcst_4.html`
- **Aggregated Forecast Review** (case 16369769). Toggleable aggregate rows (Aggregate Forecast, Raw Forecast, Adjustment, Adjustment %) and per-SKU Adjustment / Raw Forecast rows. `rn_enhancements_fcst_5.html`
- **Enhanced Outlier Management** (cases 15373144, 16313930, 16971151). Notify and Ignore now remove existing outlier adjustments for the analyzed slices; Change still auto-adjusts and notifies. `rn_enhancements_fcst_6.html`
- **Replacement Rate Forecast Variability** (case 13861085). For the Replacement Rate method, the History, Forecast and Forecast Error Standard Deviations are now derived from the parent part's SD and the replacement rate. `rn_enhancements_fcst_7.html`
- **Improved Forecast Worksheet Usability** (case 15913665). Child locations and bins are sorted by descending total demand or forecast, then by name. `rn_enhancements_fcst_8.html`
- **Disaggregation Type** (Even / Proportional; also in 13.0.1.2). `rn_enhancements_fcst_9.html`
- **Export of Records on Forecast Review** (case 16282952). `FORECAST_REVIEW_MAX_GRID_ROWS` now allows 1 to 100,000 (default 65,000). `rn_enhancements_fcst_10.html`

### Inventory Optimization
Index: `release_13_1_0_0/rn_enhancements_io.html`
- **Enhanced Scenario Budget Reporting.** New graphs: Inventory Turns with Fill Rate, Planned Revenue, Total Cash Outflow, Total Forecast Quantity/Value with Fill Rate. New containers: Budget Detail and Carbon Summary. Compare up to 12 additional scenarios, with the count set by `MAXIMUM_ADDITIONAL_SCENARIOS_DISPLAY_COUNT` (default 5), a user preference page "Set Additional Scenarios Selection Size", and a Configure: Additional Scenario Display pop-up. `rn_enhancements_io_2.html`
- **Expanding Scenario What-If Modeling** (the What-If page, rights and fields from 13.0.1.0, now GA). `rn_enhancements_io_3.html`
- **Sustainability Modeling and Optimization.** Everything from 13.0.1.3, plus Carbon Tax:
  - New fields: Carbon Tax (Embodied / Transportation / Total), Carbon Tax Rate, and Reference Carbon Tax Rate / Currency on Locations and Regions.
  - The rate resolves Location, then Region, then the `CARBON_TAX_RATE` global setting (default 0).
  - The rate is editable in What-If Model; you can optimize to minimize carbon tax plus ROP value.
  - `rn_enhancements_io_4.html`
- **Inventory Optimization (Objective) Cost.** New Optimization Cost field on Parts and SKU (Gateway-loadable). New scenario setting *Objective Cost Criteria*: Part Cost (default); Optimization Cost (falls back SKU, then Part, then Part Cost); or Carbon Tax (Embodied) + Part Cost. New Objective Cost output field. Renamed: Benefit Criteria became Objective Benefit Criteria (Fill Rate Increment / EBO Reduction), and Fill Rate became Fill Rate Method (4 methods). Bang for Buck is redefined as ΔObjective Benefit / ΔObjective Cost. `rn_enhancements_io_5.html`
- **Customer Order Size Calculation.** New Customer Order Size Calculator AutoPilot process (runs by segment, from external demand) and a *Use In Customer Order Size* flag on Demand Streams. New global settings `CUST_ORDER_SIZE_DMD_HIST_HORIZON`, `_MIN_DMD_RECS`, `_OUTLIER_HANDLING`, `_OUTLIER_STD` and `_VARIABILITY_CAP`. `IO_CALC_CUST_ORDER_SIZE` was renamed `IO_CALC_RESUPPLY_CUST_ORDER_SIZE` with values CUSTOMER / EFFOQ / NONE. Order Size fields were renamed to Customer Order Size. Steps: Synchronize DB, then the Calculator, then Calculate Scenarios. `rn_enhancements_io_6.html`
- **Enhanced Rotable Pooling Optimization** (case 15044247). Adds Maximum Pool Wait Time (days) as a constraint (overridable) and Expected Pool Wait Time. Pool Fill Rate was renamed Minimum Pool Fill Rate on constraints and Expected Pool Fill Rate on the report. `rn_enhancements_io_7.html`
- **Improved User Experience.** Default configurable filters on Service Group Results and SKU Summary; Exception Criteria container on Location Summary. `rn_enhancements_io_8.html`
- **Excel Escape Character on SKU Summary export** (case 16962610). `EXCEL_EXPORT_ESCAPE_CHARACTER`: "=" (default) outputs ="0…"; "t" prefixes a tab. Applies only to values that start with 0. `rn_enhancements_io_9.html`
- **Fields Added to IO Pages.**
  - Part Supply Chain and SKU Summary: Customer Period Forecast In Line and Pipeline Forecast In Line.
  - Part Summary and Segment Summary: Primary and Secondary Emergency Fill Rate, plus their Optimized variants.
  - Segment Summary: In Collaboration.
  - `rn_enhancements_io_10.html`
- **Field Name Changes.** The Expected On Hand renames from 13.0.1.2, plus Summarize Excluded Pairs became Summarize Excluded SKUs. `rn_enhancements_io_11.html`
- **Global Settings at Runtime container** on the Scenarios page. Shows the global setting values in effect when the scenario ran; needs the Global Parameters right. `rn_enhancements_io_12.html`
- **Integrated Support for SIOP.**
  - New fields: Expected Gross Profit, Expected Inbound/Outbound Orders, Inventory Turns, Planned COGS, Planned Revenue, Planned Revenue at Risk, Resale Price and Resale Value.
  - New read-only "Sales, Inventory and Operations Planning" container on Stocking Policy.
  - `rn_enhancements_io_13.html`, `_14.html`, `_15.html`
- **Network Optimization.** Rules and Hours to Cross (also in 13.0.1.1/13.0.1.2). `rn_enhancements_io_16.html`
- **Process Group Added to Optimization Sets.** The process group is applied to the task when the scenario is run from the Run menu. `rn_enhancements_io_17.html`
- **Run Options on Segment Summary.** Approve All Pending SKU and Start Collaboration (also schedulable in AutoPilot). `rn_enhancements_io_18.html`
- **Safety Stock Calculation Change for TP-ROP.** SS = ((ROP − Pipeline Forecast) / COS) × COS, shown to 2 decimals with no floor. `rn_enhancements_io_19.html`
- **Stockout Costs** (also in 13.0.1.3). `rn_enhancements_io_20.html`

### Pricing
Index: `release_13_1_0_0/rn_enhancements_pricing.html`
- **Configurable Price Offsets.** New Custom Offset propagation mode, allowing a custom offset for any future date.
  - New `PRC_USE_CUSTOM_OFFSETS` (default true). The source text for this setting is garbled; read it as "true = the option is available".
  - `PRC_PRICE_ACTION_GATEWAY_APPLY_PRICE_OFFSETS` was replaced by `PRC_PRICE_ACTION_GATEWAY_PROPAGATION_MODE` (1 Ripple, 2 Independent, 3 Custom Offset). The source lists its default as "true", which is inconsistent with those values.
  - `rn_enhancements_pricing_2.html`
- **Part Kit Pricing** (cases 13471826, 14667494). All price buckets can price kits, and price-action recommended prices of components can be used. New Review Reason 351, Component Part Priced Later than Part Kit. `rn_enhancements_pricing_3.html`
- **Price Feedback Management.** New `ENABLE_PRC_FEEDBACK_MANAGEMENT` (default false). New Price Feedback user right (View / Modify / Modify 'Use for Market Stats').
  - New pages: Price Feedback Types (Default), Price Feedback Status (Open / In Progress / Closed), Price Feedback Resolution Types (Price Increased / Decreased / No Change), and Price Feedback (records can be plain, with a Reference SKU, or with a Competitor).
  - New Price Feedback tab on the Pricing Worksheet.
  - `rn_enhancements_pricing_4.html`
- **Elasticity Estimation.** New Recommended Price (Pricing Worksheet Elasticity tab, Group Price Analysis) and Average Elasticity (Group Price Analysis). Definitions were refined for Elasticity Data Stage, Group Elasticity Data Stage, Recommended Action and Price Volume Curve Equation. `rn_enhancements_pricing_5.html`
- **Pricing Policy Documentation** (case 17005984). Diagnostic Reporting definitions for: Total Input/Output Pairs; New Price = 0, = Current, < Current; and the fallout categories (Outside Folder Coverage, Price Active = No, Undefined Strategy Code, Missing Price Offsets). `rn_enhancements_pricing_6.html`

### Supply Planning
Index: `release_13_1_0_0/rn_enhancements_sp.html`
- **Vendor Capacity and Multi-Vendor Support** (requires TP-ROP). `rn_enhancements_sp_2.html`
  - Monthly procurement and repair capacity per vendor-location-SKU, with vendor priority. When the top vendor's capacity is used up, the next is used.
  - New pages and user rights: Vendor Location SKU Capacity and Vendor Location SKU Priority.
  - New Review Reasons: 349 and 350 (capacity blocks procurement / repair), 352 and 353 (primary vendor at procurement / repair limit).
  - New ordering parameter *Enable Vendor Capacity*, with *When Repair Capacity Is Fully Consumed*: Procure only for need above future repair, or Procure immediately for full remaining need.
  - `OP_VENDOR_CAPACITY_DATE_INDEX` (0 Order, the default and not for use with SCS; 1 Ship; 2 Receive; 3 Available date).
  - New Original / Beginning / Ending Capacity rows (Procurement and Repair) on the Time Series Grid and IP Summary.
- **Plan Intelligence.** A flashing IPWS toolbar button opens guidance messages in three categories: Balancing Recommendations (nearest excess location), Unplanned Demand Missed (needs PAI Advanced), and Vendor Performance (average delay from closed orders). A Plan Intelligence Map shows excess/shortage locations, existing balance orders and the supply network, and can create balance orders. `rn_enhancements_sp_3.html`
  - Global settings: `ENABLE_PLAN_INTELLIGENCE_IPWS` (default false), `PI_VENDOR_PERF_CALCULATE_PERIOD_MONTHS` (12), `PI_VENDOR_PERF_MIN_ORDERS` (10), `PI_VENDOR_PERF_RETAIN_SLICES_MONTHS` (6).
  - WebUI/AutoPilot properties: `servigistics.analytics.pi.demandmiss.calc.horizonslices` = 12 and `servigistics.analytics.pi.demandmiss.retainslices` = 6.
  - New AutoPilot process: Plan Intelligence. Also run the Planning Analytics Generator. Bing maps are optional via `servigistics.bingmap.licensekey`.
- **Order Spreading** (also in 13.0.1.1). `rn_enhancements_sp_4.html`
- **Backorder Categorization.** "On ASL with OnOrder" was split into 3.1 Vendor Delays (procuring location; Review Reason 327 present), 3.2 Vendor Delays at the upstream procuring location, 3.3 Under Forecast (e.g., Review Reason 138), and 3.4 Not Categorized. `rn_enhancements_sp_5.html`
- **Interactive Planner Worksheet.** `rn_enhancements_sp_6.html`
  - Deployments container: Show Total / Show Subtotal (Next Generation View; case 17031316).
  - New IP fields Remaining Requested, Replenishment Requested and Chain Transfer Requested (Today), which roll child needs into the parent IP. Chain Transfer Requested orders up to ROP+1 or Stock Max depending on `OP_INHOUSE_UPTO_SMAX`.
  - SCS rows on the Time Series Graph.
  - IP Summary fields renamed (e.g., Acquired Chain Transfer became Chain Transfer), with drill-down.
  - Faster page loads for large GAPs and hierarchies (cases 16119686, 16726440).
- **Order Sizing** (also in 13.0.1.2). Review Reasons 346–348. "Lot Sizing Rules" heading renamed "Order Sizing Rules" on Parts and Part Properties. `rn_enhancements_sp_7.html`
- **Calendar Adjustments** (also in 13.0.1.4). `rn_enhancements_sp_8.html`
- **Time-Phased ROP Enhancements.** New Time Series Grid rows: Ending Chain Deficit, Ending Replenishment Deficit, Ending Replenishment Need to Stock Maximum. SCS Parameters labels with TP-ROP on: Enable Procurement/Repair Safety Stock SCS. New fields Enable Procurement ROP SCS and Enable Repair ROP SCS. `rn_enhancements_sp_9.html`
- **Chain Deficit.** Down-chain deficit no longer bypasses chain parents that can balance. The deficit is shown only at the first parent able to procure, repair, replenish, balance or substitute. `rn_enhancements_sp_10.html`
- **Display Grid Lines** (`ENABLE_PROPERTYGRID_GRIDLINES`; also in 13.0.1.3). `rn_enhancements_sp_11.html`
- **Effective Date Calculation for Overdue Orders.** Overdue Procurement and Repair host orders with no vendor, or a non-primary vendor, use the primary vendor's lead time. `rn_enhancements_sp_12.html`
- **Full Option documented** (also in 13.0.1.2). `rn_enhancements_sp_13.html`
- **Global LTB Quantity** (also in 13.0.1.1). `rn_enhancements_sp_14.html`
- **Order Plan Comparison hyperlinks** (also in 13.0.1.1). `rn_enhancements_sp_15.html`
- **Inventory Studio.** Expandable rows and the Part Locator map (`INVENTORY_STUDIO_MAP_DISPLAY`). `rn_enhancements_sp_16.html`
- **Last Time Buy** approve/disapprove behavior (also in 13.0.1.2). `rn_enhancements_sp_17.html`
- **Launch IPWS with URL and SKU parameters** (case 16923315). `http://<server>:<port>/WebUI/Pws.mvc?hostPart_toSelect=<Parthostid>&hostLocation_toSelect=<locHostID>` `rn_enhancements_sp_18.html`
- **Non-ASL label** on the Daily Detail IP Report, IP Summary and Time Series Grid when a non-ASL SKU is loaded (TP-ROP). `rn_enhancements_sp_19.html`
- **Sales Return Outside Return Lead Time** (`OP_COUNT_SALES_RETURNS_THROUGH_HORIZON`; also in 13.0.1.2). `rn_enhancements_sp_20.html`
- **Transport Calendar More than One Year** (case 15532113). Ordering and Transport calendars can span more than one year. `rn_enhancements_sp_21.html`

### Technical / Performance
Source: `release_13_1_0_0/technical_notes_13_1_0_0.html`
- **SQL Server driver** upgraded to 12.2.0.jre8. Encryption is off by default; enable with `servigistics.dburl.encrypt=true` in WebUI, AutoPilotServer, AutoPilotClient and DBUpgrader properties (BID-8190).
- **Tomcat 9.0.83** certified; `maxParameterCount` must go from 1000 to 10000 in `server.xml`. Windows needs "Upgrade with New Settings" (BID-8542).
- **Debug logs** rotate at 500MB or at date change and are compressed; a new `log4j_debug.properties` is installed (BID-8722, case 16404087).
- **`servigistics.recordsetfetchsize` = 500** now also set in WebUI properties (Oracle) (BID-87996).
- **Apache session-termination configuration** added to the docs (SPM-102368).
- **IPWS initial load time** reduced (SPM-104702 / SPM-109737).
- **SQL Server Fill Factor 0 or 100** recommended (SPM-107608).
- **New web services:** `import-csv-file.ws` (SPM-107639) and `import-csv-data.ws` with process group support (SPM-108052). `run-job.ws` gains an optional process group for Get Host Data (SPM-108526).
- **Forecasting multithread** performance improved and deadlock risk reduced (SPM-107727).
- **LDAP credentials** can be stored encrypted: `servigistics.credentials.encrypted` replaces `servigistics.credentials`, and `<ldapsecondary>.credentials.encrypted` is supported (SPM-108086).
- **Oracle parallel parameters** (SPM-110851).
- **Get Host Data via `run-job.ws`** no longer raises a primary-key-violated error for a multi-SKU data group (SPM-110918).

---

## 13.1.0.1

Overview page: `new_in_13_1_0_1.html`

### Common
- **Usability.** Parameter-priority toolbar buttons now have the tooltip "Change Sequence", and the page they open was retitled from "Order Schemes" to "Change Sequence". `release_13_1_0_1/rn_enhancements_2.html`

### Forecasting
- **Demand History Management Performance.** New AutoPilot property `servigistics.histanalysis.clear.outlier = true`. `release_13_1_0_1/rn_enhancements_fcst_2.html`
- **Streamline Best Fit Graph.** Shows only Total Demand, Total Forecast, Applied, Recommended and Second Best by default; other series can be toggled on. `release_13_1_0_1/rn_enhancements_fcst_3.html`
- **Usability.** Forecast Worksheet link added to Go to and row links on Production/Scenario Causal Forecast Detail. Forecast Comparison Summary adds "Under Forecasted SKUs Bias" and "Over Forecasted SKUs Bias". `release_13_1_0_1/rn_enhancements_fcst_4.html`

### Pricing
- **Price Feedback Management.** Segment rights now come from the Pricing Worksheet right. Price Feedback added to Data Manager and Import. New Feedback Number field on the Survey Parts pop-up. `release_13_1_0_1/rn_enhancements_pricing_2.html`
- **Price Transactions.** New `ENABLE_PRC_TRANSACTIONS` (default true), a Price Transactions user right (Price Analysis tab), and a Price Transactions page to view and delete transactions. `release_13_1_0_1/rn_enhancements_pricing_3.html`

### Supply Planning
- **Alternate Transport Mode with TP-ROP** (procurement and replenishment, ABR on or off). Modes are ranked by descending pipeline length. The first mode whose Backorder Days Reduced ≥ Backorder Threshold is used; if none qualifies, no alternate mode is used. TP Safety Stock and Trigger logic is unchanged. `release_13_1_0_1/rn_enhancements_sp_2.html`
- **Order Explanation Report** (TP-ROP only). Explains day-by-day Generate Order Plan decisions. Enable "Order Plan Output Order Explanation Enabled" in the IPWS Configure window; a report button appears on the Daily Detail IP, IP Summary and Time Series Grid containers. `release_13_1_0_1/rn_enhancements_sp_3.html`
- **Transportation Mode for manually created Balancing orders** (case 17249240; same as 13.0.1.5). `release_13_1_0_1/rn_enhancements_sp_4.html`
- **Time-Phased ROP Enhancements.**
  - Ending Deficit, Ending Replenishment Deficit and Ending Chain Deficit rows are always shown. `OP_ENABLE_TIMEPHASED_REPL_CHAIN_DEFICIT` now applies only to TP Safety Stock.
  - New *Set SCS Min to 0* checkbox (SCS Procurement/Repair tabs): when SS ≥ 0 the SCS SS Minimum becomes 0, so orders are only expedited or created inside lead time when a backorder is predicted.
  - `release_13_1_0_1/rn_enhancements_sp_5.html`
- **Field Name Changes.** On Deployments, Average Daily Forecast became Total Daily Forecast and Average Period Forecast became Total Period Forecast. `release_13_1_0_1/rn_enhancements_sp_6.html`

---

## 13.1.0.2

Overview page: `new_in_13_1_0_2.html`

### Common / Modeling
- **Comparative Analytics.** New Forecast Comparison Composite Detail page (Automated Dataset Comparison) showing the methods used in Composite streams. `release_13_1_0_2/rn_enhancements_2.html`

### Forecasting
- **Replacement Rate Forecast Variability Derived from Parent** (case 17478964). New `FCST_REP_RATE_USE_PARENT_SD` (true on new installs, false on upgrades): true derives the SDs from the parent; false uses the SKU/stream's own data. `release_13_1_0_2/rn_enhancements_fcst_2.html`
- **Forecast Override Recommendations.** New Forecast Override Intelligence AutoPilot process (ML). A Plan Intelligence message, "A forecast override is not recommended", shows Stream and Confidence Level. `release_13_1_0_2/rn_enhancements_fcst_3.html`
- **Improved Definitions** (case 17420317).
  - Average Demand Interval = total periods / non-zero periods.
  - Periods Between Demand = zero periods / (non-zero periods − 1).
  - The `PERIODS_BETWEEN_DEMAND` global setting is the default for new or blank parameters.
  - `release_13_1_0_2/rn_enhancements_fcst_4.html`

### Pricing
- **Home Page.** New containers Price Feedback Type, Status and Resolution Type, with counts that drill into Price Feedback. `release_13_1_0_2/rn_enhancements_pricing_2.html`
- **Monthly Financial Process** (case 17271277). New `PRC_PROCESS_PRICE_ACTIVE_SKUS` (default true): true processes only Price Active SKUs; false processes active and inactive. `release_13_1_0_2/rn_enhancements_pricing_3.html`

### Supply Planning
- **Ending Inventory Position** data source on the Time Series Graph, to validate IP between ROP and Stock Max. `release_13_1_0_2/rn_enhancements_sp_2.html`
- **Time-Phased ROP.** IP Summary reports the first and last day of each week when Order Period Display = Weekly. New Restart Number field on the Order Explanation report: the count of Order Plan restarts, used for sorting. `release_13_1_0_2/rn_enhancements_sp_3.html`
- **Field Changes.** Timestamp removed from Last Planned Date on the IPWS Order/SKU Parameters container. `release_13_1_0_2/rn_enhancements_sp_4.html`

---

## 13.1.0.3

Overview page: `new_in_13_1_0_3.html`

### Forecasting
- **Demand Outlier Analysis** (case 17451759). New `OUTLIER_USE_VARIABILITY_CAP` (true on upgrades, false on new installs; false is recommended). Controls whether the COV/VMR cap is used for the Upper Control Limit; the cap can create false-positive outliers. `release_13_1_0_3/rn_enhancements_fcst_2.html`
- **Enable/Disable Best Fit with Interactive Plan** (case 17193421). Via `IPLAN_DONOTRUN_BESTFIT`: true skips Best Fit in Interactive Plan on the IPWS Forecast tab. `release_13_1_0_3/rn_enhancements_fcst_3.html`

### Inventory Optimization
- **Priority Buy List rounding** (case 17523922). New `BUY_LIST_ROUNDING_RULE` (default −1, no rounding). A value between 0 and 1 rounds as Truncate(qty + (1 − value)); for example, 10.35 becomes 11 at .35 and 10 at .5. `release_13_1_0_3/rn_enhancements_io_2.html`

### Technical
- **WebUI property `servigistics.enable.poa.view`** (true/false). Enables the Purchase Order Agreements and Purchase Order Requisitions pages when the Order Policy is not TP-ROP. `release_13_1_0_3/rn_technical_2.html`

---

## 13.1.0.4

Overview page: `new_in_13_1_0_4.html`

### Forecasting
- **Forecast Worksheet Link.** Row link added on Causal Forecast SKU Summary, Part Supply Chain, and Production/Scenario Causal Forecast Detail. `release_13_1_0_4/rn_enhancements_fcst_2.html`

### Supply Planning
- **Time-Phased ROP.** `release_13_1_0_4/rn_enhancements_sp_2.html`
  - Remove Future Need When Creating Review Reasons (case 17660422). Review Reasons that compare On Hand Good with Safety Stock no longer count future needs (future sales orders, Calendar LT Adjustment, NUNAD, Order Spreading Need, Replenishment Need to Stock Max). Affected Review Reasons: 18, 52, 53, 93, 94, 112, 134, 135, 137, 333, 334. SCS Inside Lead Time now expedites or creates orders to arrive on the day of need.
  - IP Summary: Repair IP Before Creating Orders no longer subtracts today's approved orders.
- **Last Time Buy.** Custom 11–20 fields added to the LTB Work Queue (case 17463403). `release_13_1_0_4/rn_enhancements_sp_3.html`
- **Part Health User Right** (case 17588086). A new Supply Planning tab right controls the Part Health tab on Planner 360° and the IPWS. Without the Work Queue right, the tab shows no data. `release_13_1_0_4/rn_enhancements_sp_4.html`

---

## 13.1.0.5

Overview page: `new_in_13_1_0_5.html`

### Forecasting
- **Forecasting Database Cleanup** (case 17787763). New AutoPilot process that removes stale Best Fit overrides when Run Best Fit changes from Auto-Approved to No or Null. It then applies the User Override Method, or the Stream Configuration default. Run it after Synchronize DB and before other forecasting processes. Do not run it directly on databases upgraded from before 12.2. `release_13_1_0_5/rn_enhancements_fcst.html`

### Inventory Optimization
- **Documentation.** Planned Revenue at Risk = (1 − Fill Rate) × Resale Price × Interval Forecast. `release_13_1_0_5/rn_enhancements_io.html`

### Supply Planning (TP-ROP)
- **Remove SKU Info for SKUs no longer in a GAP** (case 17720927). The Order Plan Synchronize DB process now cleans the IP Summary, Daily Detail IP Report and Order Explanation. `release_13_1_0_5/rn_enhancements_sp.html`
- **Safety Stock Rounding.** New `IO_TPROP_ROUND_SS` (default false; evaluated only when TP-ROP is on): true rounds SS with the SS rounding rule, matching TP-SS behavior; false (recommended) is consistent with IO. `release_13_1_0_5/rn_enhancements_sp.html`

---

## Consolidated settings table

GS = global setting; WebUI / AP = properties-file setting; UI = page-level setting or field. The Release column gives the first release that introduced or changed the item, with any later re-listing in parentheses. URLs are relative to BASE.

| Name | Type | Meaning / values (default) | Release | URL |
|---|---|---|---|---|
| ENABLE_EXPORT_NUMBER_FORMAT | GS | true exports numerics as numbers; false as text (false) | 13.0.1.0 | release_13_0_1_0/rn_enhancements_6.html |
| MAX_EXPORT_ROWS | GS (existing) | Respected by Data Manager Export All Rows | 13.0.1.0 | release_13_0_1_0/rn_enhancements_4.html |
| MAX_ROW_ERROR_LIMIT | GS (existing) | Used by the Forecast Review count query when it runs over 10 s | 13.0.1.0 | release_13_0_1_0/rn_performance_fcst_2.html |
| MEO_REPAIR_TYPE | GS (updated) | Composite LT: 1 Serial, 2 Aggregate, 3 Demand Weighted (3 new installs; 2 existing, with 3 recommended) | 13.0.1.0 | release_13_0_1_0/rn_enhancements_io_2.html |
| ENABLE_PRC_OFFSET_MANAGEMENT → ENABLE_CONFIGURABLE_PRICE_OFFSET_CODES | GS (renamed) | Enables Configurable Price Offset Codes | 13.0.1.0 | release_13_0_1_0/rn_enhancements_pricing_5.html |
| ENABLE_PINNING_ALL_LOCATIONS → ENABLE_LOCATION_PINNING | GS (renamed) | true: pin All/location on the IPWS Orders container; false: pin-all option removed | 13.0.1.0 | release_13_0_1_0/rn_enhancements_sp_4.html |
| OP_FAIRSHARE_SORT_CRITERIA_1 / _2 / _3 / _4 | GS (updated) | New-install defaults q / f / null / null (previously all null); upgrades set manually | 13.0.1.0 | release_13_0_1_0/rn_enhancements_sp_5.html |
| OP_TIME_PHASED_ROP_USES_TIME_PHASED_ROP_FAIRSHARE | GS | true uses the improved TP-ROP Fair Share; false the legacy logic (true) | 13.0.1.0 | release_13_0_1_0/rn_enhancements_sp_11.html |
| OP_TIME_PHASED_ROP_ENABLE | GS (existing) | Enables the TP-ROP order policy; shows Output Generated Orders and the TP-ROP SCS tabs | 13.0.1.0 | release_13_0_1_0/rn_enhancements_sp_11.html |
| Output Generated Orders | UI (Ordering Parameters) | All Orders All Locs; All for Repair/Procure Locs + Today for others; Today's Orders All Locs | 13.0.1.0 | release_13_0_1_0/rn_enhancements_sp_11.html |
| Select Forecast Method for Intermittent Demand | UI (Forecast Parameters) | Intermittent Smoothing / Croston / Servigistics TSB; replaces "Use Intermittence Smoothing Instead of Crostons" | 13.0.1.0 | release_13_0_1_0/rn_enhancements_fcst_4.html |
| Allow Servigistics TSB; TSB Alpha / Beta | UI (Forecast Parameters) | Includes TSB in Best Fit; smoothing constants | 13.0.1.0 | release_13_0_1_0/rn_enhancements_fcst_4.html |
| Generate Prioritized Buy List | UI (Scenario) | Checkbox to build a PBL for the scenario | 13.0.1.0 | release_13_0_1_0/rn_enhancements_io_5.html |
| What-If Model | UI (Scenario) | Selects the model used in the IO calc; changing it flags a recalculation | 13.0.1.0 | release_13_0_1_0/rn_enhancements_io_7.html |
| FCST_RUN_HIST_ANALYTICS | GS (existing) | When false, the DHM job can be run from IPWS / Demand Detail through OTF rights | 13.0.1.1 (13.1.0.0) | release_13_0_1_1/rn_enhancements_2.html |
| ADVANCED_REPORTS, FUTURE36 | GS (existing) | Must be true for PAI links in the configurable Go to menu | 13.0.1.2 (13.1.0.0) | release_13_0_1_2/rn_enhancements_2.html |
| Disaggregation Type | UI (Fcst Disaggregation Params) | Even / Proportional | 13.0.1.2 (13.1.0.0) | release_13_0_1_2/rn_enhancements_fcst_2.html |
| Hours to Cross | UI (Country Borders) | Border wait time added to the response time | 13.0.1.2 (13.1.0.0) | release_13_0_1_2/rn_enhancements_io_3.html |
| ALLOW_MASS_APPROVAL_TO_CO_ORDERS, MAX_ROWS_FOR_FULL_OPERATION, RS_MAX_PAGES | GS (existing) | Govern availability of the "Full" approve option | 13.0.1.2 (13.1.0.0) | release_13_0_1_2/rn_enhancements_sp_2.html |
| OP_COUNT_SALES_RETURNS_THROUGH_HORIZON | GS | true counts all sales returns through the horizon in IP; false only up to return LT (true) | 13.0.1.2 (13.1.0.0) | release_13_0_1_2/rn_enhancements_sp_5.html |
| servitistics.map.location.fail.multiple (typo as in source) | WebUI | Treat multiple Bing results as a failure (true) | 13.0.1.3 (13.1.0.0) | release_13_0_1_3/rn_enhancements_3.html |
| servigistics.map.location.verify.country | WebUI | Verify the returned country matches the request (true) | 13.0.1.3 (13.1.0.0) | release_13_0_1_3/rn_enhancements_3.html |
| servigistics.intellicus.automated.comparison.categoryid | WebUI | Set to Modeling to show the Automated Dataset Comparison pages | 13.0.1.3 | release_13_0_1_3/rn_enhancements_fcst_2.html |
| CARBON_MEASURE_TYPE | GS | Label for Sustainability headings ("kg of CO2e") | 13.0.1.3 (13.1.0.0) | release_13_0_1_3/rn_enhancements_io_3.html |
| IO_CALCULATE_SUSTAINABILITY | GS | Show the Carbon Footprint row on Budget Summary pages (false) | 13.0.1.3 | release_13_0_1_3/rn_enhancements_io_3.html |
| ENABLE_PROPERTYGRID_GRIDLINES | GS | Grid lines on the IPWS Order/SKU Parameters container (false) | 13.0.1.3 (13.1.0.0) | release_13_0_1_3/rn_enhancements_sp_2.html |
| INVENTORY_STUDIO_MAP_DISPLAY | GS | Show the Bing map in the Inventory Studio Part Locator (true) | 13.0.1.3 (13.1.0.0) | release_13_0_1_3/rn_enhancements_sp_3.html |
| servigistics.bingmap.licensekey | WebUI | Bing Maps key; required for Inventory Studio and Plan Intelligence maps | 13.0.1.3 (13.1.0.0) | release_13_0_1_3/rn_enhancements_sp_3.html |
| OP_TIME_PHASED_ROP_CALENDAR_ADJUSTMENTS_AT_TOP_MOST_LOC_ONLY | GS | Order Plan does calendar adjustment only at top-most locations (true) | 13.0.1.4 (13.1.0.0) | release_13_0_1_4/rn_enhancements_sp_2.html |
| OP_TIME_PHASED_ROP_CALENDAR_ADJUSTMENT_IO_LEAD_TIME_INCREASE | GS | Days of closure gap covered by IO; 7 weekly, 14 bi-weekly, 0 Order Plan handles (7) | 13.0.1.4 (13.1.0.0) | release_13_0_1_4/rn_enhancements_sp_2.html |
| parallel_degree_policy=ADAPTIVE; parallel_min_time_threshold=2 | Oracle DB | Recommended performance parameters | 13.0.1.5 (13.1.0.0) | release_13_0_1_5/technical_notes_13_0_1_5.html |
| APPLY_RETURN_WR_NON_REPAIR_LOC | GS | Apply Return Wash Rate to non-repairable children of repairable ancestors (false) | 13.1.0.0 | release_13_1_0_0/rn_enhancements_7.html |
| CIRCULAR_REFERENCE_RETENTION_DAYS | GS | Days before purging Circular Reference Finder output (default not stated) | 13.1.0.0 | release_13_1_0_0/rn_enhancements_8.html |
| ENABLE_ADVANCED_GRID | GS (existing) | Shows the Next Generation View toggle on the toolbar | 13.1.0.0 | release_13_1_0_0/rn_enhancements_15.html |
| Error Improvement % | UI (Forecast Parameters) | Minimum % metric gain before Best Fit switches method (10; 0 on upgrade = off) | 13.1.0.0 | release_13_1_0_0/rn_enhancements_fcst_3.html |
| Force Servigistics ML Composite | UI (Best Fit) | Yes always uses ML Composite | 13.1.0.0 | release_13_1_0_0/rn_enhancements_fcst_2.html |
| Adjustment — Operation / Value | UI (Forecast Worksheet) | Replace / Increase-Decrease By Value / Increase-Decrease By Percent (default Increase By Value) | 13.1.0.0 | release_13_1_0_0/rn_enhancements_fcst_4.html |
| FORECAST_REVIEW_MAX_GRID_ROWS | GS (updated) | Max Forecast Review export rows, 1 to 100,000 (65,000) | 13.1.0.0 | release_13_1_0_0/rn_enhancements_fcst_10.html |
| MAXIMUM_ADDITIONAL_SCENARIOS_DISPLAY_COUNT | GS | Additional scenarios on Scenario Budget Summary (5; up to 12; user preference can override) | 13.1.0.0 | release_13_1_0_0/rn_enhancements_io_2.html |
| CARBON_TAX_RATE | GS | Fallback carbon tax rate after Location, then Region (0) | 13.1.0.0 | release_13_1_0_0/rn_enhancements_io_4.html |
| Objective Cost Criteria | UI (Scenario) | Part Cost (default) / Optimization Cost / Carbon Tax (Embodied) + Part Cost | 13.1.0.0 | release_13_1_0_0/rn_enhancements_io_5.html |
| Objective Benefit Criteria (was Benefit Criteria) | UI (Scenario) | Fill Rate Increment / EBO Reduction | 13.1.0.0 | release_13_1_0_0/rn_enhancements_io_5.html |
| Fill Rate Method (was Fill Rate) | UI (Scenario) | 4 methods: PIS; PIS with ROQ benefit; 1−EBO(ROP+1)/ROQ; 1−EBO(ROP+1)/Pipeline Fcst | 13.1.0.0 | release_13_1_0_0/rn_enhancements_io_5.html |
| Optimization Cost | UI (Parts/SKU) | Custom unit cost for Bang for Buck | 13.1.0.0 | release_13_1_0_0/rn_enhancements_io_5.html |
| CUST_ORDER_SIZE_DMD_HIST_HORIZON | GS | Months of demand used for Customer Order Size (24) | 13.1.0.0 | release_13_1_0_0/rn_enhancements_io_6.html |
| CUST_ORDER_SIZE_MIN_DMD_RECS | GS | Minimum records, else COS=1 and SD=0 (5) | 13.1.0.0 | release_13_1_0_0/rn_enhancements_io_6.html |
| CUST_ORDER_SIZE_OUTLIER_HANDLING | GS | REMOVE or REPLACE (with mean ± SD) (REMOVE) | 13.1.0.0 | release_13_1_0_0/rn_enhancements_io_6.html |
| CUST_ORDER_SIZE_OUTLIER_STD | GS | Outlier threshold in SDs; −1 = none (3.0) | 13.1.0.0 | release_13_1_0_0/rn_enhancements_io_6.html |
| CUST_ORDER_SIZE_VARIABILITY_CAP | GS | Cap as a COV or VMR multiple per SL_VARIABILITY_TYPE; −1 = none (−1) | 13.1.0.0 | release_13_1_0_0/rn_enhancements_io_6.html |
| SL_VARIABILITY_TYPE | GS (existing) | COV or VMR; sets how the variability cap is interpreted | 13.1.0.0 | release_13_1_0_0/rn_enhancements_io_6.html |
| IO_CALC_CUST_ORDER_SIZE → IO_CALC_RESUPPLY_CUST_ORDER_SIZE | GS (renamed) | CUSTOMER (default) / EFFOQ / NONE; upgrade maps true→CUSTOMER, false→NONE | 13.1.0.0 | release_13_1_0_0/rn_enhancements_io_6.html |
| Use In Customer Order Size | UI (Demand Streams) | Includes the stream's transactions in the COS calculation | 13.1.0.0 | release_13_1_0_0/rn_enhancements_io_6.html |
| Maximum Pool Wait Time (days) / Minimum Pool Fill Rate | UI (Rotable Pool Constraints) | Pooled wait-time and fill-rate targets | 13.1.0.0 | release_13_1_0_0/rn_enhancements_io_7.html |
| EXCEL_EXPORT_ESCAPE_CHARACTER | GS | "=" (default) or "t" (tab) prefix for values starting with 0 | 13.1.0.0 | release_13_1_0_0/rn_enhancements_io_9.html |
| PRC_USE_CUSTOM_OFFSETS | GS | Makes the Custom Offset propagation mode available (true; source wording garbled) | 13.1.0.0 | release_13_1_0_0/rn_enhancements_pricing_2.html |
| PRC_PRICE_ACTION_GATEWAY_APPLY_PRICE_OFFSETS | GS (replaced) | Replaced by the next row | 13.1.0.0 | release_13_1_0_0/rn_enhancements_pricing_2.html |
| PRC_PRICE_ACTION_GATEWAY_PROPAGATION_MODE | GS | Gateway propagation mode: 1 Ripple, 2 Independent, 3 Custom Offset (source says "true") | 13.1.0.0 | release_13_1_0_0/rn_enhancements_pricing_2.html |
| ENABLE_PRC_FEEDBACK_MANAGEMENT | GS | Enables Price Feedback Management (false) | 13.1.0.0 | release_13_1_0_0/rn_enhancements_pricing_4.html |
| Enable Vendor Capacity; When Repair Capacity Is Fully Consumed | UI (Ordering / Planning Params) | Yes/No; Procure only for need above future repair / Procure immediately for full remaining need | 13.1.0.0 | release_13_1_0_0/rn_enhancements_sp_2.html |
| OP_VENDOR_CAPACITY_DATE_INDEX | GS | Date for vendor capacity: 0 Order (not with SCS), 1 Ship, 2 Receive, 3 Available (0) | 13.1.0.0 | release_13_1_0_0/rn_enhancements_sp_2.html |
| ENABLE_PLAN_INTELLIGENCE_IPWS | GS | Enables Plan Intelligence on the IPWS (false) | 13.1.0.0 | release_13_1_0_0/rn_enhancements_sp_3.html |
| PI_VENDOR_PERF_CALCULATE_PERIOD_MONTHS | GS | Order-history horizon for vendor performance (12) | 13.1.0.0 | release_13_1_0_0/rn_enhancements_sp_3.html |
| PI_VENDOR_PERF_MIN_ORDERS | GS | Minimum closed orders per vendor location (10) | 13.1.0.0 | release_13_1_0_0/rn_enhancements_sp_3.html |
| PI_VENDOR_PERF_RETAIN_SLICES_MONTHS | GS | Months of vendor performance to retain (6) | 13.1.0.0 | release_13_1_0_0/rn_enhancements_sp_3.html |
| servigistics.analytics.pi.demandmiss.calc.horizonslices | WebUI + AP | Past horizon for the Unplanned Missed calculation (12) | 13.1.0.0 | release_13_1_0_0/rn_enhancements_sp_3.html |
| servigistics.analytics.pi.demandmiss.retainslices | WebUI + AP | Months retained for Unplanned Missed (6) | 13.1.0.0 | release_13_1_0_0/rn_enhancements_sp_3.html |
| OP_INHOUSE_UPTO_SMAX | GS (existing) | Chain Transfer Requested orders up to ROP+1 vs Stock Max | 13.1.0.0 | release_13_1_0_0/rn_enhancements_sp_6.html |
| Enable Procurement / Repair ROP SCS; (Procurement / Repair) Safety Stock SCS | UI (SCS Parameters) | ROP-based SCS on/off; labels change when TP-ROP is on | 13.1.0.0 | release_13_1_0_0/rn_enhancements_sp_9.html |
| servigistics.dburl.encrypt | Properties (WebUI / AP / DBUpgrader) | true enables SQL Server driver encryption (off by default) | 13.1.0.0 | release_13_1_0_0/technical_notes_13_1_0_0.html |
| maxParameterCount (Tomcat server.xml) | Server | Raise from 1000 to 10000 for Tomcat 9 | 13.1.0.0 | release_13_1_0_0/technical_notes_13_1_0_0.html |
| log4j_debug.properties | Server | Rotation at 500MB or daily, compressed | 13.1.0.0 | release_13_1_0_0/technical_notes_13_1_0_0.html |
| servigistics.recordsetfetchsize | WebUI + AP | 500 (Oracle fetch size) | 13.1.0.0 | release_13_1_0_0/technical_notes_13_1_0_0.html |
| SQL Server Fill Factor | DB | 0 or 100 recommended | 13.1.0.0 | release_13_1_0_0/technical_notes_13_1_0_0.html |
| servigistics.credentials.encrypted (and <ldapsecondary>.credentials.encrypted) | WebUI | Encrypted LDAP credentials; replaces servigistics.credentials | 13.1.0.0 | release_13_1_0_0/technical_notes_13_1_0_0.html |
| servigistics.histanalysis.clear.outlier | AP property | true, for Demand History Management performance | 13.1.0.1 | release_13_1_0_1/rn_enhancements_fcst_2.html |
| ENABLE_PRC_TRANSACTIONS | GS | Enables Price Transactions (true) | 13.1.0.1 | release_13_1_0_1/rn_enhancements_pricing_3.html |
| Order Plan Output Order Explanation Enabled | UI (IPWS Configure) | Generates Order Explanation data (TP-ROP) | 13.1.0.1 | release_13_1_0_1/rn_enhancements_sp_3.html |
| OP_ENABLE_TIMEPHASED_REPL_CHAIN_DEFICIT | GS (scope changed) | Now used only for TP Safety Stock; TP-ROP deficit rows always shown | 13.1.0.1 | release_13_1_0_1/rn_enhancements_sp_5.html |
| Set SCS Min to 0 | UI (SCS Proc/Repair tabs) | SCS SS Minimum = 0 when SS ≥ 0 | 13.1.0.1 | release_13_1_0_1/rn_enhancements_sp_5.html |
| FCST_REP_RATE_USE_PARENT_SD | GS | Replacement Rate SDs from the parent (true) or the SKU's own data (false) (true new / false upgrade) | 13.1.0.2 | release_13_1_0_2/rn_enhancements_fcst_2.html |
| PERIODS_BETWEEN_DEMAND | GS (existing) | Default Periods Between Demand for new or blank parameters | 13.1.0.2 | release_13_1_0_2/rn_enhancements_fcst_4.html |
| PRC_PROCESS_PRICE_ACTIVE_SKUS | GS | Monthly Financial processes only Price Active SKUs (true) or all (false) (true) | 13.1.0.2 | release_13_1_0_2/rn_enhancements_pricing_3.html |
| OUTLIER_USE_VARIABILITY_CAP | GS | Use the COV/VMR cap for the Upper Control Limit (true upgrades / false new; false recommended) | 13.1.0.3 | release_13_1_0_3/rn_enhancements_fcst_2.html |
| IPLAN_DONOTRUN_BESTFIT | GS (existing) | true skips Best Fit in Interactive Plan | 13.1.0.3 | release_13_1_0_3/rn_enhancements_fcst_3.html |
| BUY_LIST_ROUNDING_RULE | GS | Prioritized Buy List rounding; −1 none, 0–1 threshold (−1) | 13.1.0.3 | release_13_1_0_3/rn_enhancements_io_2.html |
| servigistics.enable.poa.view | WebUI | Enables PO Agreements / Requisitions pages for non-TP-ROP policies (true/false) | 13.1.0.3 | release_13_1_0_3/rn_technical_2.html |
| IO_TPROP_ROUND_SS | GS | Round TP-ROP Safety Stock (false; recommended false) | 13.1.0.5 | release_13_1_0_5/rn_enhancements_sp.html |

**Problems in the source to keep in mind:**
- The `PRC_USE_CUSTOM_OFFSETS` description says true hides the option, which contradicts its purpose.
- `PRC_PRICE_ACTION_GATEWAY_PROPAGATION_MODE` has numeric values but a stated default of "true".
- The Geo Locate property is spelled `servitistics…` in the source.
- `FCST_REP_RATE_USE_PARENT_SD` says "Replenishment Rate Forecast" where it means Replacement Rate.
- No default is given for `CIRCULAR_REFERENCE_RETENTION_DAYS`.
- Some pages mention icons whose glyphs were lost in the text crawl.