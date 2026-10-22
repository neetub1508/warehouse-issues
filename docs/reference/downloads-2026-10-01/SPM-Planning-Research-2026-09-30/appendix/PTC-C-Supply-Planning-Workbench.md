PTC SERVIGISTICS 13.x: SUPPLY / ORDER PLANNING AND PLANNER WORKBENCH, RESEARCH NOTES

URL convention: every source is https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/ followed by the path in brackets. Example: [glossary/global_settings_sp.html]. I read these from the local crawl in scratchpad/spm/ptc/txt/, where the first line of each file is its URL. I wrote no files into the repo; compact extracts are in scratchpad/spm/ptc/out/o1..o17.txt.

====================================================================
1. CORE CONCEPTS AND ORDER POLICIES
====================================================================

1.1 Three Order Policies
- There are three Order Policy types: Time-Phased Safety Stock, Trigger Point and Time-Phased ROP. [glossary/order_policy_type.html]
- The policy is "assigned to an Ordering Parameter, which is assigned to a part or SKU." [glossary/order_policy_type.html]
- PTC's advice: "It is almost always best to use Trigger Point until you need to use Time-Phased Safety Stock". Trigger Point is less process-intensive, simpler and easier to explain. [glossary/order_policy_type.html]

Comparison table from the same page [glossary/order_policy_type.html]:

| | Trigger Point | Time-Phased Safety Stock |
|---|---|---|
| When need is evaluated | Order Date | Available Date |
| What is evaluated | Inventory Balance <= ROP | Projected On Hand Inventory < SL |
| How far out | Through Horizon | Through Horizon |
| Quantity ordered | "Up to Stock Max, then order sized" | "Multiples of EOQ to cover need, then order sized" |

Trigger Point (TR) [glossary/trigger_point.html]
- A reactive policy: "orders are made when inventory position drops to a trigger point."
- Typical for high-tech and automotive. Suits low-volume, cheap, less critical, short-lead-time parts.
- When stock is at or below ROP, it recommends a quantity back up to Stock Maximum.
- Stock reaching Safety Stock posts a critical-shortage Review Board record. Stock above Stock Max posts an excess record.
- Limitation: it does not consider sales orders, month-by-month forecast variation, or calendars.

Time-Phased Safety Stock (TP) [glossary/time-phased_safety_stock.html]
- A proactive policy: orders are made "when projected inventory is expected to fall below Safety Stock."
- It "automatically identifies expedites and deferrals".
- Typical for aerospace and defense. Suits higher-volume, expensive, critical, long-lead-time parts.
- Inputs: daily forecast, procurement/repair orders, replenishment/balancing orders, sales orders, forecasted returns or sales returns, lead-time elements, calendars.
- "should not be used as the Order Policy for replenished locations unless it is absolutely necessary."

Time-Phased ROP (TPROP) [glossary/time-phased_rop.html]
- "places orders over the horizon when projected inventory is expected to fall at or below ROP."
- Each day's inventory is updated by incoming and outgoing orders, daily forecast need, sales-order need, and incoming good and bad parts from sales returns and the return forecast.

Enabling TPROP [glossary/time-phased_rop_2.html]
1. Set OP_TIME_PHASED_ROP_ENABLE=true.
2. Set every Ordering Parameter's Order Policy to Trigger Point, so no calculation falls back to Time-Phased Safety Stock behaviour.
3. Set Days to Generate Orders plus Forecast Horizon Days, or Use Max LT plus Max Auto Horizon.
4. Tick Count In Order Plan on all internal forecast streams.
5. Configure the recommended global settings (see section 12).
- All SKUs in a GAP must generate orders for the same number of days; the longest value is used. The default is 1 day (today).

Effects of OP_TIME_PHASED_ROP_ENABLE=true [glossary/global_settings_sp.html]
- Trigger Point and Time-Phased Safety Stock policies are disregarded.
- Perform Upchain Excess Transfer and Perform Substitution Excess Transfer are enabled.
- The TPROP Schedule Change Suppression (SCS) pages and tabs are enabled.
- The Purchase Order Agreements and Purchase Order Requisitions pages are NOT available.

1.2 GAP (Group of Associated Parts)
GAPs are "SKUs that need to be order-planned together." A SKU is included if any of these is true [glossary/group_of_associated_parts.html]:
- It is on the ASL or has a positive stock amount.
- Run Order Plan = Yes.
- It has a supply (order plan) record.
- It has a sales order or sales return.
- It is the Top Most Revision (TMR) of a chain.
- It is a replenishment source of a planned SKU.
- It is a non-ASL SKU with forecast only, when OP_ROLLUP_NONASL_FCST or OP_NONASL_FUTURE_PROCURE is true.

The GAP is built by the Order Plan Synchronize Database AutoPilot process. [glossary/group_of_associated_parts.html]

1.3 Supply pipelines
There are four pipelines [glossary/service_parts_supply_chain_pipelines.html]:
- Procurement: new parts from suppliers.
- Replenishment: transfers between locations.
- Return: removed parts sent to repair.
- Repair: repaired parts back into stock.
- "The Return pipeline is separate and distinct from the Repair pipeline because not all bad parts need to be or can be fixed."
- AutoPilot runs "usually nightly" and produces forecasts, ASLs, optimal levels, exceptions and recommendations.

1.4 Key planner terms and formulas
- Stock Maximum = ROP + Effective Order Quantity. 0 means not stocked. [parts/parts_pid/pid_ipws_orders_section.html]
- ROP of -1 means the SKU is not stocked. [parts/parts_pid/pid_ipws_orders_section.html]
- Safety Stock = Round((ROP - Pipeline Forecast)/Customer Order Size) * Customer Order Size, with minimum -1. Under TPROP it is unrounded, 2 decimals, no floor. [parts/parts_pid/pid_ipws_orders_section.html]
- Unadjusted Safety Stock = ROP - OnOrderMean; can be negative or fractional; TPROP only. [parts/parts_pid/pid_ipws_time_series_grid_section.html]
- Excess Limit = Stock Maximum (Trigger Point) or Safety Stock + EOQ - 1 (Time Phased). It is raised by order sizing or Excess Burnout Days. [glossary/excess_limit.html]
- On Hand Good: "Generally a healthy amount of On Hand Good is between Safety Stock and Safety Stock + EOQ." [parts/parts_pid/pid_ipws_orders_section.html]
- Need By Date = Today + 30*(On Order + In Repair + In Return - Backorder + On Hand Good - Allocated + Proc Req Amount + On Hand Bad)/Forecast. [parts/parts_pid/pid_ipws_orders_section.html]
- Out of Stock Date = Today + 30*(On Hand Good)/Forecast. [parts/parts_pid/pid_ipws_orders_section.html]
- Cushion Time = Need By Date - Expected Date; negative means stock is needed before it arrives. [parts/parts_pid/pid_ipws_orders_section.html]
- System Impact (ASL) = (EBO with current IP - EBO with IP including this order) * Lead Time. Non-ASL = Recommended Qty * Lead Time. Use it to rank orders for review. [parts/parts_pid/pid_ipws_orders_section.html]
- Days on Hand is governed by GENERATE_OP_SL_OUTSTOCK_DAYS.
  - Time Phased SKUs: based on when planned On Hand Good goes below zero.
  - Otherwise: (On Hand New + On Hand Fixed)/Average Daily Demand Rate.
  - [parts/parts_pid/pid_ipws_orders_section.html]
- "Effective On Hand Good" does not appear verbatim in the corpus. The closest terms are:
  - Effective Ending On Hand Planned = Ending On Hand Planned - Ending TP Replenishment Deficit - Ending TP Chain Deficit (minus Ending Replenishment Need to Stock Max under TPROP).
  - Effective Ending On Hand Recommended = the same formula on the Recommended values.
  - Both are visible when OP_ENABLE_TIMEPHASED_REPL_CHAIN_DEFICIT=true.
  - [glossary/effective_ending_on_hand_planned.html], [glossary/effective_ending_on_hand_recommended.html]

====================================================================
2. INTERACTIVE PLANNER WORKSHEET (IPWS)
====================================================================

2.1 Tabs and purpose
- The IPWS has four tabs [glossary/interactive_planner_worksheet.html]:
  - Part 360°: part KPIs.
  - Part Health: inventory health of a part.
  - Plan: "focal point for reviewing and planning orders".
  - Forecast.
- It can be opened by URL: http://<server>:<port>/WebUI/Pws.mvc?hostPart_toSelect=<Parthostid>&hostLocation_toSelect=<locHostID> [glossary/interactive_planner_worksheet.html]
- Plan tab containers: Alerts, AutoPilot Process Status, Daily Detail IP Report, Demand/Forecast Graph, Demand/Forecast Summary, Demand/Forecast Summary Graph, Deployments, Forecast Parameters/Metrics, Inventory Position, Inventory Position Summary, Journal, Order/SKU Parameters, Orders, Part Chain Details, Part Kit Details, Review Board, Time Series Graph, Time Series Grid, Used In Part Kit. [parts/parts_smart_help/sh_ipws.html]
- Forecast tab containers: Demand/Forecast, Demand/Forecast Detail Graph, Forecast Metrics, Forecast Parameters, Review Board, SKU Parameters. [glossary/interactive_planner_worksheet.html]

2.2 Toolbar actions [parts/parts_smart_help/sh_ipws.html]
- Run configured OTF AutoPilot processes, which come from the OTF Rights tab of User Rights Setup.
- Run Interactive Plan.
- Discard unsaved changes. Save, which persists Interactive Plan results after you are satisfied.
- Plan Intelligence button. It flashes yellow when there are messages.
- Chain Detail button (up/down arrow for up-chain/down-chain part). Only shown when the part is in a chain.
- View menu (pop-ups):
  - Dashboard, which is the SKU page.
  - Purchase Requisitions, Purchase Agreements.
  - Sales Orders, Sales Returns, Backorder, Order Plan - Order History (each with a count).
  - Daily Balance Summary Report, Daily Balance Detail Report.
  - Generate Excel Report, Export Gap Data.
- Go To menu:
  - Audit Trail, Forecast Review, Part Supply Chain, Stocking Policy.
  - PAI dashboards: Forecast Analysis, Spend and Inventory Projection, Vendor Performance Management, Backorder Days, Demand Miss Analysis, Fill Rate Analysis, Inventory Detail, Part/SKU Forecast Analysis - Advanced, SKU Supply Chain History.
- Review-reason filter options: Go To Advanced Filters, Go To Work Queue, Not Filtered, My Review Reasons, or a specific Review Reason.
  - Only review types with "Use for Filters" set appear in the list.
  - With Location = All plus a review filter, a checkbox orders results by priority (lower value is higher priority), then highest magnitude across locations, then minimum LocID.
- Configure options:
  - Run Iplan On Page Load: runs Generate Order Plan when the page opens.
  - Layout: Advanced (Layout Manager, requires ENABLE_ADVANCED_LAYOUT_IPWS), Classic (Review / Time Series / Details sections), Single Column, or Adjustable Panel.
  - Pin the Menu.
  - Status Badge in Order/SKU Parameters. Status Badge in Time Series Grid.
  - Order Plan AutoPilot Logging Enabled.
  - Order Plan Output Order Explanation Enabled.
- Manage Containers: only with Advanced layout.
- Email.

2.3 IPWS access settings [parts/parts_smart_help/sh_ipws_2.html]
- Global settings: ALLOW_EDIT_IPWS_ON_DASHBOARD, APPROVE_FOR_UPLOAD, ALLOW_MASS_APPROVAL_TO_CO_ORDERS, DEPLOYMENT_LOADGAP_LOC_LIMIT, ENABLE_ADVANCED_LAYOUT_IPWS, ENABLE_PLAN_INTELLIGENCE_IPWS, PWS_DISPLAY_PROC_REPL_REPA_FIELDS, PWS_IPLAN_ON_LOAD, PWS_SHOW_ONLY_POSTITIVE_OHBAD, PWS_TIME_SERIES_VIEW_MODE, PWS_UPLOAD, OP_TIME_PHASED_ROP_ENABLE, UPLOAD_ALL_ORDER_DETAIL, USE_OPTIMAL_LEVEL_PERMISSION_FOR_IPWS.
- User rights: "Interactive Planner Worksheet" and "Configure Interactive Planner Worksheet" on the Supply Planning tab of User Rights Setup.
- Audit Trail processes: Optimal Levels, Replenishment/Balance SKU Lead Time, Replenishment/Balancing SKU, Replenishment Lead Times, SKU, Vendor Location SKU Lead Time.

2.4 Orders container
Purpose: lists all recommended and approved orders for the SKU. It is Step 3d of the Daily Planner Workflow. Export includes all rows and ignores MAX_EXPORT_ROWS. [parts/parts_smart_help/sh_ipws_orders_section.html]

Filters [parts/parts_smart_help/sh_ipws_orders_section.html]
- Location: All (the whole GAP for the part) or the selected location.
- Order Type: All, Procure, Repair, Replenishment, Balance, Excess Recall.
- Approval Status: All, Approved, Not Approved, Planned.
- Inbound / Outbound / Inbound-Outbound.
- Date Type: Ordered, Shipped, Received or Avail. Each falls back through Recommended, Actual, Effective, On Hold, then Planned date.
- Date Range: None, Today, Last 365, Next 7/30/60/90/365 days, Custom. The choice persists.
- Show part-chain orders.
- On Hold State: Show All, Show On Hold, Hide On Hold, Show Expired On Hold.
- Pin/reset filter. ENABLE_LOCATION_PINNING controls pinning "All" locations.

Actions [parts/parts_smart_help/sh_ipws_orders_section.html]
- Selected / All scope.
- Approve. Disapprove.
- Manage menu: Cancel, Lock Selected Orders, Unlock Selected Orders, Set Selected orders On Hold Until Date of, Remove On Hold Until Date, Upload Data to Internal System (requires PWS_UPLOAD=true).
- Row menu: Journal.
- Right-click links on Part, Location, From Part and Source Location open Part/Location Properties or SKU.

Key Orders fields [parts/parts_pid/pid_ipws_orders_section.html]
- Order Type: Balance, Excess Recall, Procurement, Repair, Replenishment.
  - The Inventory Position section also references Disassembly/Reduce-to-Produce orders (order type 7 = good, 8 = defective). [parts/parts_pid/pid_ipws_inventory_position_section.html]
- Order Status:
  - Planned: recommended by Order Plan.
  - Ordered: "uploaded to the host system and was downloaded again ... as an approved order".
  - Planned (On Hold). Ordered (On Hold).
  - Closed: ignored by Order Plan; cannot be cancelled; host-owned.
  - "Order Plan considers both Planned and Ordered orders as being open."
- Planned (origin flag):
  - Planned (p): generated by Order Plan.
  - User (u): created manually on the IPWS or Procurement page.
  - Host updated (c): downloaded from procurement; "cannot be updated in Servigistics". PWS_EDIT_CO_ORDERS and ALLOW_MASS_APPROVAL_TO_CO_ORDERS relax this.
- Approval Status: Not Approved, Auto Approved, Manually Approved, No change from current order, Reviewed and no change to be made.
- Recommended Actions (can hold several values):

| Value | Meaning |
|---|---|
| Alternate Transport Mode | Recommended mode differs from planned/primary |
| Cancelled | Newly recommended quantity is 0 |
| Constrained | Replenishment is below the requested amount because of source availability |
| Deferred | Later Available Date recommended |
| Supply Shipment Expedited | Earlier Available Date recommended |
| Group MOQ Order | Result of Vendor Group Min Order Quantity |
| Increased | Quantity raised |
| Newly Created | New order |
| Overdue | Effective date updated because the order is overdue |
| Reduced | Quantity lowered |
| Unchanged | No change |
| Vendor Split | Result of splitting by vendor |
| Within Lead Time | Available date falls within lead time |

- Date families:
  - Actual (Order/Ship/Receive/Avail): from the host, editable.
  - Planned: approved, editable.
  - Recommended: calculated.
  - Effective: recalculated when a Planned date is past and no Actual exists. It accounts for Processing, Shipping, Put Away Lead Time and Calendar. It is not calculated for Manual/Auto-Approved planned orders whose Planned Available Date is today or later.
  - Orig: at placement.
  - Hold (Order/Ship/Receive/Avail/Quantity/Bad Qty/Transport Mode): used while the order is on hold.
- Quantities:
  - Planned Quantity is not editable for Repair.
  - Planned Bad Quantity = Planned Qty/(1 - Repair Wash Rate).
  - Recommended Bad Quantity = Recommended Qty/(1 - Repair Wash Rate).
  - Amount Requested vs Order Quantity. Example: field needs 10, central has 7, so Order Qty = 7 and Amount Requested = 10.
  - Spread Amount comes from order spreading.
  - Also: Remaining Due in Quantity, Received Qty, Shipped Qty, Available Quantity.
- Control fields:
  - Freezing: Yes means "committed and cannot be changed".
  - Lock Until Date and Locked By Planner ID. Order Plan Locked.
  - On Hold Until Date. When it expires, an order with planned values becomes a regular order; an order without planned values is deleted.
  - Count in Order Plan: order-level override of the parameter "Orders Count In Order Plan".
  - Count In Netting.
  - Need To Upload: a notification flag only; it "does not actually upload the record".
  - Upload Action: Changed, Uploaded, Not Uploaded. Uploaded Since Last Change. Last Uploaded Date. Last Planned.
  - Approved/Disapproved By: sign-in name.
  - LTB Status: Not Approved, Approved, Done.
  - Life Cycle Order.
  - SCS Time Gate Period: TG0, TG0-1, TG1 ... TG4, or Null.
- Trigger Point day-level fields ("only applicable when using Trigger Point"):
  - Approved Balance / Approved Repair Balance: inventory position at the beginning of the day.
  - Recommended Balance / Recommended Repair Balance.
  - Calculated Need = Stock Max - Recommended Balance. Calculated Repair Need.
  - Recommended In/Out counts for Balancing, Procurement, Repair, Replenishment, Substitution and Up-Chain.
- Costs:
  - Transport Cost waterfall for Replenishment/Balance/Excess Recall: Repl/Balancing SKU Lead Time, then Repl/Balancing Lead Time.
  - Transport Cost waterfall for Procurement/Repair: Vendor Location SKU Lead Time, then Vendor Location Parts, then Vendor Location Lead Time.
  - Planned Line Value = Planned Qty*Part Cost. Recommended Line Value = Rec Qty*Part Cost.
- Order Details hyperlinks appear only when OP_WRITE_PART_DETAIL=true. [glossary/order_details.html]

2.5 Order/SKU Parameters container [parts/parts_pid/pid_ipws_order_sku_parameters_section.html]
Category headers: General, Order Sizing, Vendors and Lead Times, Production Amounts, Custom.

Controls
- Hide Until: hides the SKU from filtered navigation until the date.
- Hold New Orders Until: no new orders until the date. [glossary/hold_new_orders_until.html]
- Hold Plan Until: Order Plan does not run for the SKU at all.
  - "Existing orders will not be modified."
  - "Unapproved orders will have to be manually deleted."
  - It does not stop auto-approval of already qualifying orders.
- Need To Plan: set to Yes to trigger planning of "Only Run Order Plan When Triggered" SKUs. It cannot be set back to No.
- Aggregate Balance Amounts (Trigger Point only):
  - Yes: On Order / Backorder / In Repair / In Return are taken from Stock Amounts.
  - No: they are summed from order plan, sales return and sales order detail within lead time.
- Disconnected Replenishment. Replenishment Source Internal Stream.

Sizing fields
- Procurement / Repair / Replenishment: Fixed Order Size, Lot Size, Lot Size Round, Minimum Order Quantity, Order Period ("minimum number of days between orders ... 0 means not to use"), Packaging Size (+Round), Pallet Size (+Round). The "Round" value is "the number of parts in excess of ... above which Servigistics recommends ordering another package/pallet".
- Sales Size: the smallest quantity to order when need is at least one unit. Otherwise Lot Size and Lot Size Round are used.
- EOQ controls:
  - Min EOQ (slices), Max EOQ (slices), Min EOQ Qty, Max EOQ Qty.
  - Set EOQ (slices), e.g. 1.25 slices of a 20/slice forecast gives EOQ 25. Set EOQ Quantity.
  - Overrides carry end dates and Reason Codes. For conflicting maxima, "the minimum of the maximum values take priority".
  - The EOQ edit dialog: Min/Max/Set EOQ (slices), Slices Override end date + reason, EOQ Override end date + reason. [parts/parts_pid/pid_ipws_order_sku_parameters_section_edit_eoq.html]
  - The REOQ dialog: Max REOQ, Set REOQ. [parts/parts_pid/pid_ipws_order_sku_parameters_edit_repair_eoq.html]

Pipeline and status fields
- Lengths: Procurement Length, Repair Length ("repair or scrap a part and return it"), Replenishment Length, Return Length.
- Due Dates: Procurement, Repair, Replenishment, Return.
- Late in Availability, Late in Shipping, Due to be Received, In Transport.
- Primary Vendor Location. Primary Repair Vendor Location.
- NFF Rate, NRTS, Repair Wash Rate, Return Wash Rate. Consumable (only with NFF for Consumables).
- Deficits: Time Phased Day 1 Chain/Replenishment Deficit, Trigger Point Chain/Replenishment Deficit.
- Cost totals:
  - Total Procurement Cost = (Part Cost*Qty) + Order Cost + Transport Cost.
  - Total Repair Cost = (Repair Cost*Qty) + Repair Order Cost + Transport Cost.
- Order Last Reviewed By / Date.
- EBO: "Total EBO ... is Wait Time * Total Daily Forecast".
- ENABLE_PROPERTYGRID_GRIDLINES toggles grid lines. [glossary/global_settings_sp.html]

2.6 Time Series Grid [parts/parts_pid/pid_ipws_time_series_grid_section.html]
Display
- Weekly or monthly slices per Order Period Display. Monthly systems can switch to Quarterly/Yearly.
- Calendar Year or Fiscal Year (FISCAL_YR_STARTING_MONTH).
- Plan/Rec filter: All, Recommended, Planned. View Mode: Report or Default.
- IO/SCS rows show averages; others show sums.
- Slices beyond Days To Generate Orders are shaded gray.
- Cell hyperlinks drive the Orders container filter.
- [parts/parts_smart_help/sh_ipws_time_series_grid_section.html]
- OP_USE_ACTUALS=true (default): effective dates are used and "Actual" rows are hidden. false: planned dates only, with extra "...Actual" rows displayed.
- USE_TIME_PHASED_LEVELS=true (default): per-slice IO stock levels are used. false: current-slice levels are used for all slices. [glossary/global_settings_sp.html]

Rows
- Available/Orders rows:
  - Planned Available (expands to No Fault Found, Repairs, Disassembly, Procurements, Replenishments). Planned Available Bad (Disassembly).
  - Planned Orders (Repairs/Procurements/Replenishments).
  - Planned Sent (Replenishment/Balancing/Excess Recall).
  - Recommended Planned, Recommended Available, Recommended Available Bad, Recommended Orders, Recommended Sent.
- On Hand rows:
  - Beginning On Hand Good / Good Planned / Bad / Bad Planned.
  - Ending On Hand Planned = (OnHandNew + OnHandFixed - Allocated) - Forecast - Sales Orders - Part Kits - Sales Backorder + Planned Available.
  - Ending On Hand Bad Planned = OnHandBad + InReturn + Forecasted Returned Qty + Sales Returns - Repair Orders.
  - Ending On Hand Recommended = Beginning On Hand Good - Total Requirements + Recommended Available.
  - Ending On Hand Bad Recommended.
  - Effective Ending On Hand Planned / Recommended.
- Deficit rows:
  - Ending Replenishment Need to Stock Maximum (TPROP).
  - Ending Chain Deficit / Ending Time Phased Chain Deficit.
  - Ending Replenishment Deficit / Ending Time Phased Replenishment Deficit.
- Vendor capacity rows (TPROP, expandable by Vendor Location Priority): Original / Beginning / Ending Capacity for Procurement and for Repair.
  - "Blank" means no limit for the Primary Vendor.
  - For a Secondary Vendor, blank means capacity is not used.
- Level rows:
  - Unadjusted Safety Stock. EOQ (with EOQ Override). Repair EOQ. Fill Rate.
  - Demand Satisfaction Used (hidden when IO calculates levels).
  - ROP (Trigger Point only). It expands to ROP Override and Min/Max ROP in qty and days.
  - Repair ROP. Repair Stock Maximum.
  - Safety Stock. It expands to SS Override qty/days (qty wins) and Min/Max SS qty/days; editable per slice.
  - Stock Maximum (Trigger Point), with Stock Max Override.
  - Procurement / Repair / Replenishment Lead Time.
  - Values in parentheses are calculated values that differ from the effective value.
- SCS rows:
  - Trigger Point / Time-Phased Safety Stock SCS: Ideal Stock Level (Procurement/Repair) = Safety Stock + EOQ/2. Min/Max (Procurement/Repair), the "cone".
  - TPROP SCS: SCS Safety Stock Minimum, SCS ROP Minimum, SCS Stock Maximum, each for Procurement and Repair.
- Acquired/Relinquished: On Hand Good/Bad Acquired and Relinquished, for chain/substitution.
- Total Requirement expands to:
  - Net Forecast.
  - Forecast - External (Forecast, Demand).
  - Forecast - Internal (Forecast, Demand).
  - Net Forecast - Downstream Non-ASL.
  - Sales Orders. Open Kit Orders.
  - Chain Relinquished (PWS_TOT_REQ_INCLUDE_CHAINS).
  - Recommended Sent (PWS_TOT_REQ_INCLUDE_REPL).
  - Downstream Sales Orders. Trigger Point Replenishment Deficit.
  - Worked example: three streams of 100 each, two netted to 50, give Total Forecast 300 and Net 200.

2.7 Inventory Position container (row-by-row IP build) [parts/parts_pid/pid_ipws_inventory_position_section.html]
Requirements rows
- Backorder Original. Allocated.
- Replenishment / Balancing / Excess Recall / Repair (rework) Orders Sent.
- Sales Orders: due up to the max of procurement, repair and repl/balance lead times plus OP_ADD_DAYS_TO_LT_TO_CALC_TOROP_BALANCE; "-1" means the whole horizon.
- Downstream Sales Orders. Trigger Point Replenishment Deficit (integrated mode). Stock Maximum. Trigger Point Chain Deficit.

Supply = OH Good + Approved Orders + On Order + In Repair + In Return * NFF
- On Hand Good: if in a chain, OH Orig - Outgoing + Incoming.
- Outgoing Chain & Substitutes: transfer down-chain, roll up to superseding part, rolled up good as defective.
- Incoming: roll-up, transfer, substitute, Reduce to Produce.
- Planned Orders (Proc/Repair/Repl/Bal/ExRecall). On Order. In Repair. Good Available in Future.

Inventory Position = Supply - Requirements.

Supply (Defective), repairable only
- On Hand Bad Orig + Incoming (Defective Sales Returns = In Return Orig*(1 - NFF); Reduce to Produce defective) - Outgoing (repair defectives, roll-up defective).
- Bad Available in Future.

Other rows
- Targets: Stock Max, ROP, EOQ.
- Supply (Recommended) by order type.
- Excess Limit.

2.8 Inventory Position Summary container (TPROP only) [parts/parts_pid/pid_ipws_inventory_position_summary.html], [parts/parts_smart_help/sh_ipws_inventory_position_summary.html]
Purpose
- A view-only daily IP audit. Daily columns count = OP_TIME_PHASED_ROP_IP_DAYS_TO_OUTPUT (recommended 14); after that, first and last day of each period through the horizon.
- A line separates yesterday from today. Hover shows formulas and calculations.
- Row prefixes: E = equation, L = by location, P = by part. A red disc marks a subtracted row.
- Toggle Maximum Precision. Buttons for Daily Detail IP Report and Order Explanation Report.
- Questions it answers: "Is my Ending Inventory Position within ROP and Stock Maximum?"; "Is there a configuration issue that is causing the Order Plan process to not recommend an order?"

Dates
- IP Lead Time Date = max(Procurement, Replenishment, Repair LT).
- IP Lead Time Adjusted Date: adjusted by Already Ordered and OP_ADD_DAYS_TO_LT_TO_CALC_TRIGGER_INVENTORY_POSITION.

Inventory Position rows (blue)
- Repair IP Before Creating Orders: excludes Future Potential to Repair.
- Ending Inventory Position = Ending Net On Hand Good - Requirements + Surplus & Future Supply + Existing On Order + Recommended Orders (Today) + Remaining Requested (Today).
  - "does not consider today's forecast and sales returns. Today's forecast and sales returns are considered during overnight."
- Ending Net On Hand Good = On Hand Good - Backorder.
- Requirements = Future Sales Order + Downstream Future Sales Order + Replenishment Deficit + Replenishment Need to Stock Maximum + Chain Deficit + Need Until Next Available Date + Calendar Lead Time Adjustment + Order Spreading Need.
  - Replenishment Deficit: whole number, when the child's IP is at or below ROP.
  - Replenishment Need to Stock Max: fractional, when the child's IP is above ROP; only if OP_ENABLE_TRIGGER_NEED_TO_SMAX=true.
  - Chain Deficit: down-chain Chain Transfer Requested at the first up-chain part able to self-supply.
  - NUNAD: "extra amount to order today to cover the forecast from the available date of today's order until the next possible available date", e.g. closed periods or once-a-week ordering.
  - Calendar Lead Time Adjustment. Example: 5-day LT with weekends closed takes 8 days, so +3 days.
- Surplus & Future Supply = IP Excess Used (Child) (needs OP_REDUCE_PARENT_NEED_BY_IP_EXCESS) + Future Potential to Repair + Future Returns (sales returns + return forecast over Return LT, no wash rate).
- Existing On Order: Planned orders with order date on or before today, and Recommended orders with order date before today, available by the IP LT Date.
- Recommended Orders (Today).
- Remaining Requested (Today): Replenishment Requested + Chain Transfer Requested (to ROP+1 or Stock Max per OP_INHOUSE_UPTO_SMAX).

Other row groups
- Stock Levels (orange): Unadjusted SS, ROP, Repair ROP, Stock Max, SCS SS Min/ROP Min/Stock Max for Procurement and Repair, EOQ, Fill Rate.
- Inventory Reconciliation (green):
  - OH Good Reconciliation Today: Acquired (Substitution, Roll Up Good, Chain Transfer), Sales Orders, Part Kit SOs, Good Sent, Relinquished, Good Received.
  - OH Good Reconciliation Next Day: Good from Returns, Net Forecast External/Internal/Downstream Non-ASL.
  - OH Bad Reconciliation Today and Next Day.
  - Ending On Hand Bad. Total Ordered / Good Received / Good Used / Bad Used.
- Additional Information:
  - Flags: Order Date, Closed Date, Available Date, Unconstrained ("the first unconstrained date is essentially the calendar adjusted pipeline length from today").
  - Future Bad from Returns. Sales Returns (NFF Applicable / Not Applicable).
  - Need To Stock Maximum (Self) = Stock Max - IP.
  - Forecast Unmet Need. Non-ASL Forecast Unmet Need. Sales Order & Host Order Unmet Need.
  - IP Excess (Self / Child). NFF Rate.

2.9 Daily Detail IP Report container [parts/parts_pid/pid_ipws_daily_detail_ip_report.html]
- Material Flow rows:
  - Ending On Hand Good / Backorder (Previous Day). Overnight On Hand Good Net Usage. Good from Returns. Net Forecasts.
  - Net Beginning On Hand Good (Today). Consumption (Today). Existing Incoming/Outgoing Orders.
  - Acquired Roll Up Good. Sales Orders. Part Kit SOs. Relinquished.
  - Roll Up Good: down-chain good counts toward the up-chain part; Replace parts only.
  - Roll Up Good as Bad: down-chain good must be reworked.
  - Beginning OHG / Backorder for IP. Existing On Order. IP Before Requirements.
- IP rows:
  - Outgoing Order Recommendation (Today). Repair Good Sent.
  - Repair Order Recommendation. Future Potential to Repair. IP Before Creating Orders.
  - Acquired. Incoming Order Recommendation (Today).
  - Ending Inventory Position. Ending On Hand Good / Backorder (Today). Remaining Requested.

2.10 Deployments container
- Shows stock amounts, stock levels and today's excess, critical shortage, days on hand, balancing, and replenishment sent/received for all locations. It is Step 3c of the daily workflow. [parts/parts_smart_help/sh_ipws_deployments_section.html]
- Controls:
  - Display Planned Locations: GAP locations, from IPCS_ORDER_PLAN_GAP.
  - Display All Locations: hierarchy (IPCS_NS_LOC_TREE) within IPCS_ORDER_PLAN_EXTRA_PAIRS.
  - Show Total. Show Subtotal (Next Generation View only).
  - Date Type / Date Range.
  - Hyperlinks (Excess Recall Sent/Received, Balancing Order Received/Sent, Procurement Order, Repair Order, Replenishment Received/Sent) filter the Orders container.
  - DEPLOYMENT_LOADGAP_LOC_LIMIT (default 500) tunes load order. [glossary/global_settings_sp.html]
- Key fields [parts/parts_pid/pid_ipws_deployments_section.html]:
  - Critical Shortage Amount = ceil(Critically Short SS Threshold - Projected Net On Hand Good).
    - TPROP threshold: Unadjusted SS*(CST/100) if Unadjusted SS >= 0, else Unadjusted SS*(1 + (1 - CST/100)).
    - TPSS threshold: SS*(CST/100).
    - Projected Net OHG under TPROP = OHG - Backorder - Replenishment Deficit - Chain Deficit.
    - Projected Net OHG under TPSS = OHG - BO - Rec Outgoing + Rec Incoming - Ending Deficit.
  - Shortage Date / Shortage End Date. Excess Date / Excess End Date. On Hand Excess.
  - Pipeline Forecast: demand over effective LT including parent wait time.
  - Repair Max: "Stock Maximum cannot exceed the Repair Stock Maximum"; = Safety Stock + Repair Pipeline Forecast + Repair EOQ.
  - Is Pooled. Pooling Location Name.
  - Total Period Forecast = Daily*7 (weekly) or *30 (monthly, when LEVELS_DAYS_CONSTANT=true).

2.11 Other IPWS containers
- Review Board container [parts/parts_smart_help/sh_ipws_review_board_section_review_board.html]:
  - Covers GAP and non-GAP records.
  - Show For: None, Part, Location, SKU. Part Reviewed. SKU Reviewed. Delay.
  - Show All / Show Delayed-Reviewed / Hide Delayed-Reviewed. Review Note.
  - Steps 3b and 3e of the workflow.
- Alerts container [parts/parts_smart_help/sh_ipws_review_section_alerts.html]:
  - Review Alerts tab and Future Alerts tab. Part/SKU Reviewed. Delay with an alert date.
  - Filter By All, Part, Location, Pair.

2.12 Plan Intelligence
- Enabled by ENABLE_PLAN_INTELLIGENCE_IPWS (default false). [glossary/global_settings_sp.html]
- Guides planners on vendor delay (from closed-order history), unplanned demand missed (from demand detail history), and excess sources for balancing. [glossary/plan_intelligence.html]
- Setup [glossary/plan_intelligence_2.html]:
  - Set PI_VENDOR_PERF_CALCULATE_PERIOD_MONTHS (default 12), PI_VENDOR_PERF_MIN_ORDERS (default 10 closed orders), PI_VENDOR_PERF_RETAIN_SLICES_MONTHS (default 6). [glossary/global_settings_sp.html]
  - Run the Plan Intelligence AutoPilot process.
  - Unplanned Demand Missed needs PAI Advanced + Planning Analytics Generator.
  - Forecast Override Recommendations needs PAI Advanced + Forecast Override Intelligence.
  - Optional Bing Maps. Run Geo Locate.
- Messages [glossary/plan_intelligence_3.html]:
  - Balancing Recommendations: "Create balance order from <location> (Nearest Location)", showing Lead Time and Balancing LT; "Show excess and shortage locations"; "Review Balancing Parameters and configure/redefine balancing".
  - Forecast Override Recommendations: "A forecast override is not recommended" (Stream, Confidence Level).
  - Unplanned Demand Missed: "Excessive unplanned demand misses" (Actual/Planned/Delta Fill Rate, Unplanned Missed, Demand Missed, Review Age); secondary "There is a backorder", linked to review reason 331.
  - Vendor Performance: "Excessive order delay by <vendor> (Primary vendor)"; secondary "There is an overdue host order", linked to review reason 327.
- Pop-up layout: the left column holds tips with links; the right column holds key metrics. [parts/parts_smart_help/sh_plan_intelligence.html]
- Map views: Excess and Shortage Locations (pink = shortage, aqua = excess; create a balance order from the map; On Hand = OHN + OHF - BO - Allocated), Existing Balance Orders, Supply Chain Network. [parts/parts_smart_help/sh_plan_intelligence_map.html]

2.13 Order Explanation Report
- "lists simplified explanations of the decisions the Generate Order Plan AutoPilot process made about order generation for each day." [core/core_smart_help/sh_order_explanation_report.html]
- TPROP only. To enable: IPWS Plan tab > Configure > "Order Plan Output Order Explanation Enabled", then run Generate Order Plan. It opens from Daily Detail IP Report, Inventory Position Summary or Time Series Grid. [core/core_smart_help/sh_order_explanation_report_2.html]
- Fields [core/core_pid/pid_order_explanation_report.html]:
  - Part, Location.
  - Restart Number: "Every time an order is moved or created to become available inside of Lead Time, the Order Plan process must restart from the first day", e.g. SCS.
  - Explanation Date: Process Date to Process Date + Days to Generate Orders.
  - Process Name: e.g. Procurement, Repair, ATM, SCS, Substitution, Configuration.
  - Detail, Process Date, Sequence Number.
  - Sort order: Restart Number, Explanation Date, Sequence.

====================================================================
3. DAILY PLANNER WORKFLOW (PLANNING BY EXCEPTION)
====================================================================
- Premise: "Most of the order recommendations ... should be automatically approved using the Auto Approval process. However, there are always exceptions ... This is referred to as planning by exception." [process/workflow_daily_planner.html]

Steps [process/workflow_daily_planner.html]
1. Open Planner 360°.
2. Choose a path:
   - Preferred: Top Work Queue Items goes straight to the IPWS.
   - Alternate: Part Based Work Queue Summary goes to the Work Queue, then the IPWS.
3. On the IPWS:
   - a. Part Health tab.
   - b. Review Board.
   - c. Deployments: top location, Display Planned Locations, Show Total, Date Range, expand all, show Procurement Order; compare OHG vs levels for the next 7 days.
   - d. Orders: Date Range, sort by Available Date, check Rec Qty / Rec Avail Date / Order Date, adjust using the Time Series Graph/Grid, repeat for Balancing, Excess, Replenishment, Repair; approve.
   - e. Review Board: optional custom delay; Part Reviewed (preferred) or SKU Reviewed (alternate).
   - f. Journal note.
   - g. Save.
   - h. Next SKU.

Detailed ordering sub-workflow [process/workflow_detailed_supply_planning_ordering.html]
- Set Date Range to None.
- Review Replenishment/Balance/Excess first ("Is there excess in the network that can be moved?").
- Then Procurement, then Repair.
- Adjust, then set a Date Range before placing orders.

Configuration recommendations
- Sort by Priority ascending, then Magnitude descending. Show For = Parts. Hide Delayed/Reviewed. Put ROW_GROUP_NAME / ROW_GROUP_COUNT first. [glossary/review_board_2.html]
- Magnitude Value = Part Cost * Magnitude. A part appears once for its highest-priority reason. [glossary/work_queue_2.html]
- Work queue pages: Work Queue, Last Time Buy Work Queue, Part List Work Queue (Pricing). [glossary/work_queue.html]
- Planner 360° cache: ENABLE_DASHBOARD_CACHE (default true) plus the "Refresh Planner/Part 360°" process. It affects Part Based WQ Summary, Order Summary, Top Work Queue Items and Supply Chain View. [glossary/global_settings_sp.html]

====================================================================
4. GENERATE ORDER PLAN AUTOPILOT AND RUN CADENCE
====================================================================
- AutoPilot "runs selected processes" against segments "at desired frequencies" [glossary/autopilot.html]:
  1. The gateway pulls host data, "typically on a nightly basis".
  2. AutoPilot loads the transfer tables.
  3. AutoPilot processes and writes upload tables.
  4. The host gateway integrates the results.
- Job fields: Active, Frequency, Frequency Units (minutes/daily/weekly/monthly), Scheduled Run Date/Time, Segments, Processes, Planner Name. [core/core_pid/pid_autopilot_page_job_tab.html]
- Manual run: page "Run Manual Process"; pick a Segment or Default; optional AutoPilot Base Date (Parts module); select processes; check the Status tab. [core/core_topics/running_the_autopilot_manually.html]
- Related pages: Job, Process Log, Process Status, Run Manual Process. [core/core_topics/module_processing_autopilot.html]
- Process categories: Core, Network Optimization, Lifecycle, Custom, Pricing, Report, Planning, PAI, Dataset Comparison. [glossary/autopilot_processes.html]

Core processes [glossary/autopilot_processes_2.html]
- Attachment Storage Synchronizer. Circular Reference Finder. Database Maintenance. Gateway Consistency Check. Get Host Data.
- Review Process ("Refreshes the Review Board").
- Synchronize Database ("Determines the parameters to be assigned to each SKU and calculates stock amounts, taking part chains into account").
- Update Segmentation.

Forecasting / Supply Planning / IO processes [glossary/autopilot_processes_8.html]
- ASL Generation, including Mid-Slice ASL Adjustment via MID_SLICE_ASL_DA_THRESHOLD.
- BestFit, Causal Forecast Detail, Copy Demand, Customer Order Size Calculator, Demand Aggregation, Demand Detail Aggregation, Demand History Management.
- Disassembly: populates Product Disassembly.
- Forecast Netting. Forecasting. Forecasting-Calculate Metrics. Forecasting Database Cleanup.
- Frequent Data Load: intraday stock amounts, SOs, Order Plan and shipment data for a process group.
- Generate Order Plan:
  - "Runs the Order Plan process which populates the Planner Worksheet. This process is comprised of multiple processes that run in succession."
  - After Post Review, a Post Auto Approval Review runs (Run Time Order 5) and creates review types 323, 324, 325, 326 and 332 (new recommended repair, replenishment, balancing, procurement and excess recall orders).
  - Logging: servigistics.OP_LOGSS / OP_LOGBAL = true, plus IPWS Configure "Order Plan AutoPilot Logging Enabled", produce <ts>OPSS.csv and <ts>OPBAL.csv for PTC support.
- Make Forecast Production. MEO Make Production. Run Supercession Changes. Merge SKU Overrides.
- Plan Intelligence. Post Forecast. Refresh Planner/Part 360°. Stock Level Generation.
- Vendor Group Min Order Quantity (hidden; PROCID 1200 VendorGroupMoqTask).
- Vendor Split (hidden; PROCID 1198 VendorSplitTask).

Lifecycle processes [glossary/autopilot_processes_4.html]
- Lifecycle Analytics.
- Calculate Decay Rate.
- Last Time Buy Recommendation: approved LTB records; creates Review Board records.
- Last Time Buy Forecast.

Comparison processes [glossary/autopilot_processes_10.html]
- Order Plan Comparison - Data Backup, and Build Report (Order Plan Comparison Summary/Detail).

Dependencies and parameters
- Jobs can run in parallel unless they are dependent. For example, Calculate depends on Database Maintenance, Get Host Data, Synchronize Database, "Order Plan Sync Database", Forecasting, Forecast Netting and ASL Generation. [glossary/autopilot_process_dependencies.html]
- OP_GENERATE_ORDER_PLAN_PART_HEALTH_DATA=true makes Generate Order Plan populate the Part Health page. [glossary/global_settings_sp.html]

Planning horizon and time buckets
- Planning horizon comes from Forecast Horizon Days, or Max Auto Horizon when Use Max LT is set. [glossary/planning_horizon.html]
- Slice = "Summarized data over a period a time" (week, month). [glossary/slice.html]
- Forecast Horizon Days sets the last possible Available Date, extended to the end of the slice. [parts/parts_pid/pid_new_edit_ordering_parameters_page_general_tab.html]
- Use Max LT sets the horizon field to -1. Max Auto Horizon defaults to 730:
  - -1 (recommended) = GAP days-to-generate + longest LT, capped.
  - 0 disables the Time Series Grid output.
  - >0 = days to output.
  - [parts/parts_pid/pid_new_edit_ordering_parameters_page_general_tab.html]
- Days to Generate Orders sets the last possible Order Date (e.g. 14). [parts/parts_pid/pid_new_edit_ordering_parameters_page_general_tab.html]
- Under TPSS, Days to Generate Orders differs from the planning horizon; the last order date is roughly horizon minus LT. [glossary/time-phased_rop_2.html]

====================================================================
5. ORDERING PARAMETERS (ORDER TYPES, SIZING, APPROVAL)
====================================================================

5.1 General tab [parts/parts_pid/pid_new_edit_ordering_parameters_page_general_tab.html]
Core switches
- Run Order Plan.
- Plan Non-ASL Pairs for Backorder: needed to procure for non-ASL parts with backorders or sales orders.
- Ignore Forecast: only actual demand consumes inventory in time-phased planning; intended for slow, expensive parts.
- Use Aggregate Balance Amounts: Trigger Point only; "SCS is disabled when ... Yes".
- Order Policy. Forecast Horizon Days / Use Max LT / Max Auto Horizon. Order Period Display.
- Include Backorder in Order Plan: recommended Yes. With No, unmet SO/BO/forecast is not carried forward, but unmet replenishment is.
- Start Display: Order vs Ship date. End Display: Receive vs Available date.
- Only Run Order Plan When Triggered: triggered by Need To Plan, or by a Review Board record whose review type has Trigger Order Plan.
- Plan Date: Order or Ship. It drives Commitment Levels 1-4 via Order Periods 1-3:
  - Level 1: Plan Date < Today + OP1.
  - Level 2: next band after OP1 (through OP2).
  - Level 3: next band (through OP3).
  - Level 4: after OP1 + OP2 + OP3.
- Days to Generate Orders.

Vendor capacity
- Enable Vendor Capacity.
- When Repair Capacity Is Fully Consumed: "Procure only for need above future repair" or "Procure immediately for full remaining need".

Output
- Output Generated Orders (TPROP): All Orders For All Locations; All Orders for Repair & Procure Locations with Today's Orders for others; or Today's Orders For All Locations.

Order-type enables
- Enable Procurement. Enable Repair.
- Enable Push Repair: built on Repair All; repairs all bad parts immediately without needing a requirement; self-part repair only.
- Respect Order Sizing in Push Repair.
- Ignore Repair Wash Rate on Day 1.
- Avoid Procurement within Repair LT: blocks new procurement within max(Proc, Repair) LT when defective goods inventory (DGI) is sufficient; may cause Critical Shortage review reasons.
- Avoid Chain Transfer within Repair LT.
- Allow Upchain Excess Transfer: No / Yes all locations / Yes only at non-replenishment-source locations (default). Perform Upchain Excess Transfer: Before or After Balancing and Excess Recall (TPROP).
- Allow Remaining Need Chain Transfer: Never, or Only if not procurable and not replenishable.
- Enable Part Substitution. Allow Substitution Excess Transfer. Perform Substitution Excess Transfer.
- Enable Replenishment. Disconnected Replenishment. Replenishment Source Internal Stream.
- Enable Receiving Balancing: No / Balance only for own need / Balance also for downstream need (default, recommended).
- Balancing and Excess Recall Before Repair: "Expensive repair is always the last option".
- Enable Sending Excess Recall: recalls Day-1 on-hand excess regardless of destination need, to reduce central procurement.
- Enable Cost Based Repair: considers procurement before expensive repair.
- Allow Substitution From Replenishment.
- Enable Schedule Change Suppression.
- Orders Count In Order Plan.
- Respect Order Sizing In Repair Options.
- Enable Alternate Transport Mode.
- Consider Need Until Lead Time: adds the need until LT on top of Safety Stock or SCS Min, so shortages are flagged earlier and ATM/SCS act proactively.
- Backorder Threshold Days / Lead Time Multiplier.
- Enable Already Ordered: No / Until Last Host Order / Until Specific Days, with Constant Days and LT Multiplier.
- Excess Burnout Days: adds Burnout Days*Demand Rate/Day to the Excess Limit; preferred over multipliers.

5.2 Procurement / Repair / Replenishment / Balancing / Excess Recall tabs [parts/parts_pid/pid_new_edit_ordering_parameters_page_proc_repair_repl_bal_tabs.html]
- Ordering Calendar Name: used when the vendor has no ordering calendar; the default is 24*7.
- Break Order Into Multiple Orders Using: No / EOQ / Repair EOQ / Order Size. Not applicable to Excess Recall.
- Respect (Repair) EOQ Multiplier in Ordering:
  - Yes: need is rounded to EOQ multiples, then order sizing applies. This is "not a hard constraint".
  - No: raw need is used when (remainder need after initial EOQs)/EOQ < EOQ Threshold.
- Allow Auto Approval: for Procurement, Repair, Replenishment, Balancing and Excess Recall. Orders auto-approve "if the auto approval requirements (horizon, value, limits) are met."
- Auto Approval Horizon (Horizon Days + Horizon LT Multiplier), applied to the Order Date:

| Horizon Days | Horizon LT Multiplier | Pipeline Length | Auto Approval Horizon |
|---|---|---|---|
| NULL | NULL | 30 | NULL: all orders auto-approve |
| 0 | 0 or NULL | 30 | 0: only Order Date = today |
| 10 | 1 | 30 | 40: orders up to 40 days out |

  - Order Limit Periods apply only up to this horizon. [glossary/auto_approval_horizon.html]
- Maximum Order Value Without Approval = Reference Amount * Reference Currency.
- Requires Purchase Agreement: Procurement and Repair only.
- Enable Alternate Transport Mode. Backorder Threshold Days / LT Multiplier (Procurement and Replenishment).

5.3 Other approval controls
- Block Auto Approval on a review type blocks auto-approval for SKUs with that Review Board record. [core/core_pid/pid_new_edit_review_parameter_page.html]
- Review Run Time Order 3 is created "before attempting to auto approve orders so that these Review Reasons can block auto approval." [core/core_pid/pid_review_type_page_view_new_edit.html]
- Review type 130: "Expedites - Order Expedited Orders cannot be auto approved." [glossary/review_reason_2.html]
- Block Auto Approvals on a Vendor Location SKU Lead Time blocks that vendor/SKU. [parts/parts_pid/pid_new_edit_vendor_location_sku_lead_time_page.html]
- Approve Limit (user rights): a user cannot approve an order whose Planned Qty * Price per Unit exceeds it. [glossary/approve_limit.html]
- APPROVE_FOR_UPLOAD=true gives two-stage approval (initial planner approval, then final approval by another planner). Default false. [glossary/global_settings_sp.html]
- OP_USE_REPAIR_COST_FOR_REPAIR_AUTOAPPR=true selects the cost basis: Repair uses Repair Cost, Procurement uses Order Cost, Replenishment/Balancing use Replenishment Order Cost. [glossary/order_cost.html]
- Hold Plan Until does not stop auto-approval. [parts/parts_pid/pid_ipws_order_sku_parameters_section.html]
- Group MinOQ Auto-Approved overrides Allow Auto Approval. [glossary/vendor_group_min_order_quantity.html]
- LTB parameter sets have Auto-approve LTB Forecast and Auto-approve LTB Order. [parts/parts_pid/pid_new_edit_ltb_parameters_set_page.html]

5.4 Release to ERP, requisitions and agreements
- PWS_UPLOAD=true adds "Upload Data to Internal System" to Manage on the IPWS Orders, Procurement, Repair and Replenishment pages. Default false. [glossary/global_settings_sp.html]
- Purchase requisition fields: Location, Part, Order Type (procure/repair), Action (Create Requisition / Cancel Requisition), Vendor Location, Reference Unit Cost/Currency, Request First Ship Date/Quantity, Annual Estimated Demand, Custom 1-4. [parts/parts_pid/pid_new_edit_purchase_requisition_page.html]
- The list page adds Host PO Number, Create Date, Upload Date and Status. [parts/parts_pid/pid_purchase_order_requisitions_page.html]
- Approving marks requisitions "to be executed by Servigistics" (View > Purchase Requisitions on the IPWS). [parts/parts_topics/proc_approving_a_purchase_order_requisition.html]
- Purchase Order Agreements fields: Effective/End Date, Host PO Number, MOQ, Pallet Quantity, Purchase Order Quantity (max units), PO Type (Limited/Unlimited/One Time), Reference Unit Cost (max), Vendor Part Number. [parts/parts_pid/pid_purchase_order_agreements_page.html]
- Related review types: 22, 30, 36 ("older than n days"), 37, 38, 39, 84, 85. [glossary/review_reason_2.html]
- These pages are unavailable under TPROP. [glossary/global_settings_sp.html]
- RESTRICT_MANUAL_ORDER_CREATION=true makes manual IPWS order types follow the SKU's ordering properties and locks the location. Default false. [glossary/global_settings_sp.html]
- MAX_ROWS_FOR_FULL_OPERATION (2000) and RS_MAX_PAGES (25) govern "Full" approve on Procurement, Repair and Replenishment. [glossary/global_settings_sp.html]

5.5 Order sizing sources
- Vendor Location SKU Lead Time fields: Fixed Order Size, Packaging/Pallet Size (+Round, 0-1), Minimum Order Value = Qty*Unit Cost + Order Cost, Order Limit Period 1-3 ("number of days out that changes will be allowed for order quantities. Used by Review Reasons, Auto Approvals and Order Plan"), Percentage Split, Min/Max Order Quantity (for vendor split). [parts/parts_pid/pid_new_edit_vendor_location_sku_lead_time_page.html]
- Replenishment/Balance SKU Lead Time: MOQ, Lot Size, Lot Size Round, Minimum Order Value. [parts/parts_pid/pid_new_edit_replenishment_balance_sku_lead_time_page.html]
- EOQ is the ordering-plus-carrying cost trade-off. Carrying cost is an annual percentage of part value. [parts/parts_pid/pid_ipws_orders_section.html]
- The Order Cost vs Repair Cost basis is per order (see 5.3). [glossary/order_cost.html]
- Review reasons 346/347/348 fire when Stock Max is too small for the procurement/repair/replenishment sizing rule; "Order sizing rules are not used." Types 12/14 fire when Max EOQ or Set EOQ is exceeded. [glossary/review_reason_2.html]

5.6 Vendor capacity, multi-vendor priority and vendor split
- Vendor Capacity limits monthly procure/repair per vendor, with multiple vendors in priority order; "Once the capacity of the highest priority vendor is consumed, the next highest priority vendor is used." TPROP only. [glossary/vendor_capacity.html], [glossary/vendor_capacity_2.html]
- Setup: user rights View/Modify on the Vendor Location SKU Capacity and Priority pages; OP_VENDOR_CAPACITY_DATE_INDEX (0 Order Date, the default, not to be used with SCS; 1 Ship; 2 Receive; 3 Available); Ordering Parameter flags; import or manual load; run Generate Order Plan. [glossary/vendor_capacity_2.html], [glossary/vendor_capacity_3.html], [glossary/global_settings_sp.html]
- Capacity record: Vendor Location, Part, Location, Order Type, Start/End Date, "Capacity: The number of orders that are allowed per month". [parts/parts_pid/pid_vendor_location_sku_capacity_page_create_edit.html]
- Priority record: Location, Order Type (Procurement/Repair), Part, Vendor Location, Priority (lower number is higher priority). [parts/parts_pid/pid_vendor_location_sku_priority_page.html]
- Review types 349/350 (capacity preventing orders) and 352/353 (primary vendor reached limit). [glossary/review_reason_2.html]
- Vendor Split:
  - Splits today's order by Percentage Split (must sum to 100) and per-vendor Min/Max Qty.
  - Unallocated remainder goes to the primary vendor, ignoring its max.
  - Split orders are for the current day only.
  - Runs after Generate Order Plan.
  - [parts/parts_topics/splitting_orders_by_vendor.html]
- Vendor Group Min Order Quantity:
  - Trigger SKUs only; mutually exclusive segments (conflicts raise review 317).
  - When the group total is below MinOQ, each SKU is raised to Stock Max; any remaining gap is distributed by forecast pipeline "ensuring that all items reach Safety Stock around the same time".
  - [glossary/vendor_group_min_order_quantity.html]
- Procurement By Vendor / vendor programs: planners review orders against discount-program minimums, which are not enforced. Requires SHOW_PRICE_BREAKS_IN_MENU=1. [parts/parts_topics/overview_of_procurement_by_vendor.html]

5.7 Alternate Transport Mode (ATM)
- Four types: Replenishment Transport Mode, Replenishment SKU Transport Mode, Vendor Location Transport Mode, Vendor Location SKU Transport Mode. [glossary/alternate_transport_mode.html]
- Selection under TPSS / Trigger Point [glossary/alternate_transport_mode.html]:
  - Applies if the backorder begins within LT.
  - Modes are sorted by pipeline length, descending.
  - Use the first mode whose backorder days are below the Backorder Threshold.
  - Otherwise use the earliest-arriving mode.
- Selection under TPROP: the first mode where Backorder Days Reduced >= threshold; otherwise no ATM. [glossary/alternate_transport_mode.html]
- Restrictions [glossary/alternate_transport_mode.html]:
  - Not for Repair, Balancing or Excess Recall.
  - Not with SCS.
  - Not when SS < 0.
  - Not for projected backorders inside LT (use SCS Inside Lead Time instead).
  - Does not respect order sizing.
  - Usable with ABR.
- Enable precedence: SKU > Part > Location > Ordering Parameter. Thresholds: Replenishment/Procurement Backorder Threshold Days and LT Multiplier. [glossary/alternate_transport_mode_2.html]
- Transport Mode Parameter schemes list allowed modes on Procurement and Replenishment tabs. [parts/parts_pid/pid_new_edit_transport_mode_parameters_page.html]

5.8 Schedule Change Suppression (expedite, de-expedite, cancel, reschedule)
TPROP SCS tab [parts/parts_pid/pid_ps_page_schedule_change_suppression_tab_tprop.html]
- Enable Safety Stock SCS (Inside Lead Time Only). Exclude Non ASL.
- Time Gates = Constants (Days) + Lead Time Multiplier, or Horizon.
- Limits:
  - SCS SS Min = SS - Constant - Multiplier*LT Forecast. Option "Set SCS Min to 0" when SS >= 0.
  - SCS ROP Min = ROP - Constant - Multiplier*LT Forecast.
  - SCS Stock Max = SMax + Constant + Multiplier*LT Forecast.
- Strategies:
  - Allow Create.
  - Shortage Strategy: Expedite / Increase / None.
  - Bring Up To: SCS Min SS or SS.
  - Excess Strategy: Defer / None.
  - Increase %, Maximum Expedite Days, Maximum Defer Days, Allow Defer From (Constant days + LT multiplier).
- Thresholds:
  - Increase Quantity % and/or Price (And/Or).
  - Expedite Minimum Days. Deferral Minimum Days.
  - Waterfall between SKU override and parameter conditions.
- SCS global settings: OP_SCS_TG_RESPECT_CAL (default true) and OP_SCS_MOVE_TG_TO_AVAIL (a = after, b = before, n = none; default a). [glossary/global_settings_sp.html]
- Validate MEO_OVERRIDE_MAX_QTY. [glossary/schedule_change_suppression_2.html]
- Related review types: 93-95, 112, 134-137 (SCS), 130 Expedites, 131 Deferrals, 140 Increases, 141 Decreases, 48/49 date earlier/later, 40/47 quantity more/less, 24/25 quantity/date change outside commit level, 29 order to be frozen. [glossary/review_reason_2.html]

5.9 Order spreading
- "spreads the receiving orders over a number of days ... avoid receiving orders all at once at the beginning of a shut-down period." [glossary/order_spreading.html]
- Under TPSS the need is spread across existing orders within the spread length, or a new order is made right before the closure. Under TPROP the spread need can be met by any order type. [glossary/order_spreading.html]
- Configured by Min Days Closed To Spread and Spread Length on the Vendor Location or Vendor Location SKU Lead Time (the SKU overrides). [glossary/order_spreading_2.html]
- Procurement only; primary vendor only. SCS, ATM and other constraints are not applied. ABR and order sizing may conflict. [glossary/order_spreading.html]

5.10 Already Ordered
- Future host orders covering the need suppress new orders. Not for Trigger Point. The already-ordered date is the last host order date, or Today + Constant Days + LT*Multiplier. [glossary/already_ordered.html]
- Warning: this "can add significant complexity"; "1 lead time + 7 days is reasonable". [glossary/already_ordered.html]

====================================================================
6. DEPLOYMENT, ALLOCATION, FAIR SHARE, ABR, BALANCING, EXCESS RECALL
====================================================================

6.1 Fair Share
- Fair Share Priority is used when requests exceed source stock [glossary/fair_share_priority.html]:
  1. Every requesting location is brought to Safety Stock in priority order (1 first, up to 99).
  2. Remaining stock brings locations to ROP in priority order.
  3. The rest goes by lowest Days On Hand.
  - "an advisory tool. It is not enforced". It can be overridden at location type, location and SKU level. [parts/parts_pid/pid_new_edit_autopilot_parameter_page.html]
- Fair Share Reserve: a percentage of SS held at the source for its own external demand. Fair Share Reserve Quantity is an absolute quantity, for when SS = 0. [parts/parts_pid/pid_new_edit_autopilot_parameter_page.html]
- OP_TIME_PHASED_ROP_USES_TIME_PHASED_ROP_FAIRSHARE (default true) prioritizes locations not expecting a backorder (ROP >= LT demand). [glossary/global_settings_sp.html]
- OP_FAIRSHARE_SORT_CRITERIA_1..4: new-install defaults q, f, Null, Null (previously all Null). Ties are allocated "in proportion of the total need quantity. The final break point is LocIDs." [release_notes/release_13_0_1_0/rn_enhancements_sp_5.html]

6.2 Availability Based Replenishment (ABR)
- OP_ENABLE_ABR (default true) constrains downstream replenishment to what the source actually has. [glossary/availability_based_replenishment.html]
  - Trigger Point: quantity is constrained; the unmet part shows as Amount Requested and Replenishment Deficit.
  - Time Phased: the order is moved out until stock is available.
  - Example: under TP with ABR, the field order moves to Jan 5; under Trigger Point with ABR, a 0 quantity is recommended while 5 is requested.
- Retry limits: OP_MAX_ABR_RETRIES and OP_ABR_RETRY_STOP_PERCENTAGE. Exceeding them raises review 336 "Order Plan processing stopped early". [glossary/availability_based_replenishment.html]
- ABR cannot be combined with Alternate Transport Mode or Disconnected replenishment. [glossary/availability_based_replenishment.html]
- Without ABR, the source can go negative and cause backorders at the top-most location. [glossary/availability_based_replenishment.html]
- OP_MAX_CONSTRAINED_DAYS sets the ABR enforcement horizon (not recommended). Do not enable OP_WRITE_PART_DETAIL without ABR. [glossary/availability_based_replenishment.html]
- OP_ENABLE_TRIGGER_NEED_TO_SMAX (default true) lets sources pre-order for children's need up to Stock Max. [glossary/trigger_point_2.html]

6.3 Balancing (redeployment of excess)
- Purpose: move excess to shortage locations to reduce procurement and repair. Reverse balancing (field to central) is also supported. [glossary/balancing.html]
- Prioritization: greatest-need shortage locations first; sources by excess or distance. [glossary/balancing.html]
- Need logic:
  - Uses the maximum need over max(balance LT, procurement/replenishment/repair LT).
  - With Excess Limit, over balance LT + Procurement/Replenishment/Repair LT, so a balance order cannot trigger an incoming order before it arrives.
  - Projected inventory must never drop below the threshold during that window.
  - [glossary/balancing.html]
- Level priority: lower processing levels lock balance orders first.
  - TPSS: the lowest balance LT wins regardless of hierarchy.
  - TPROP: strict bottom-to-top hierarchy.
  - With OP_BALANCE_BONEED_IN_TIMEPHASED and ..._IN_TRIGGER both true: backorders first, then SS/ROP.
  - [glossary/balancing.html]
- Within a level, OP_SHORTAGE_SORT_CRITERIA_1/2 apply: q = quantity (default 1st), s = stockout date (default 2nd). [glossary/global_settings_sp.html]
- Setup: sort settings plus Enable Receiving Balancing plus Balancing Parameters. [glossary/balancing_2.html]
- OP_BALANCE_UPTO_SMAX (default false) raises to ROP+1; true raises to Stock Max. [glossary/global_settings_sp.html]
- Balancing Parameter fields [parts/parts_pid/pid_new_edit_balancing_parameter_page.html]:
  - Allow Partial: multi-source for expensive parts; single source otherwise.
  - Primary Source First. Primary Amount. Primary Threshold.
  - Minimum Order Value.
  - Source Segment 1-7, Type 1-7 (location-type hierarchy; Any), Region 1-7 (Same / Parent / Parent or Below / Any), Amount 1-7, Threshold 1-7, Additional Retention Days 1-7.
  - Amount options: Excess Limit (recommended); Safety Stock; Days of Supply = (OHG - BO - Allocated) - Spread Amount - Need Until Threshold; Zero or Safety Stock (can drain the source to zero for backorders); Safety Stock/Reorder Point (mixed TP/Trigger Point segments).
  - Threshold under TPROP: a multiplier on Stock Max, >= 1.00 recommended. Under Days of Supply: days.
- Additional Retention Days: an extra buffer, e.g. 14 days before a field replenishment order. [glossary/additional_retention_days.html]
- Networks restrict balancing to locations within the Network. OP_OON_COUNTS_RECOMMENDED_ALSO lets out-of-network sources count recommended quantities. [glossary/network.html]
- OP_REDUCE_PARENT_NEED_BY_IP_EXCESS rolls child excess into the parent IP; "If you anticipate a lot of excess, change this setting to true." [glossary/time-phased_rop_2.html]

6.4 Excess Recall
- Parameter fields: Additional Retention Days, Excess Limit Threshold Multiplier, Minimum Order Value Threshold, Priority Sequence (applied ascending), Recall to Location, Recall to Replenishment Source Location, Source Segments. [parts/parts_pid/pid_new_edit_excess_recall_parameters_page.html]

6.5 Excess and obsolescence
- Excess = Stock Level > Stock Maximum * Excess Threshold. Any inventory not on the ASL is also excess. [glossary/excess.html]
- Excess Threshold is an AutoPilot parameter (e.g. 150%). It affects only review reasons and exceptions, not the Excess Limit. [glossary/excess_threshold.html]
- Excess Report: "all ASL and non ASL items that are in excess ... ranks them by days supply"; includes on-order stock; used to spot falling demand or stock with little demand. [core/core_topics/excess_report.html]
- Excess page fields: Excess Amount (Trigger Point only; includes on order, in repair, in return), Excess Value, Excess Date / End Date, On Hand Excess and Value, ASL Source (Manually / AutoPilot). [parts/parts_pid/pid_excess_page.html]
- Disposal/scrap: I found no explicit disposal workflow in the Supply Planning pages. The disposal-related levers are the Excess Report/page, Excess Recall, Balancing, and LTB "Excess at the End"/"Excess Not Used".

6.6 Critical shortage
- Critical Shortage Threshold is the percentage of SS below which the SKU is listed on the Critical Shortages page. [parts/parts_pid/pid_new_edit_autopilot_parameter_page.html]
- The Critical Shortages page filters by Start/End date and can include children. [parts/parts_smart_help/sh_critical_shortages_page.html]
- The Expedite report graph shows Forecast, Purchases, Repairs, Sales, On Hand (OHG - BO) and Safety Stock. [parts/parts_pid/pid_expedite_report.html]
- The Expected Backorders page lists sales orders flagged backorder or past their ship date. [parts/parts_smart_help/sh_expected_backorders_page.html]

====================================================================
7. RETURNS, REPAIR, ROTABLES, NFF, WASH RATES, CONDEMNATION
====================================================================
- Repair Wash Rate: units in repair that cannot be repaired. At 10%, 10 good units need 11 On Hand Bad. [parts/parts_pid/pid_ipws_orders_section.html]
- Return Wash Rate: removed parts that never reach repair. Returns forecast = Forecast*(1 - RWR). [parts/parts_pid/pid_ipws_orders_section.html]
- NFF Rate: returned material that needs no repair. Good Available in Future = In Return*NFF; Bad = In Return*(1 - NFF). [parts/parts_pid/pid_ipws_orders_section.html]
- NRTS: not repairable at this station. [parts/parts_pid/pid_ipws_order_sku_parameters_section.html]
- Condemnation Rate: "not repairable at any location"; blended at the root when ENABLE_NRTS=false. [glossary/condemnation_rate.html]
- NFF for Consumables: enable with APPLY_RETURN_WR_AND_NFF_TO_CONSUMABLES=true and ENABLE_NRTS=true, then run Sync DB + Forecasting. [glossary/no_fault_found_for_consumables_2.html]
- Returns global settings [glossary/global_settings_sp.html]:
  - OP_COUNT_SALES_RETURNS_THROUGH_HORIZON (default true).
  - OP_IGNORE_RETURN_FORECAST_UNTIL_RETURN_LT (default true; avoids double counting).
  - OP_FORECASTED_RETURNS_STARTING_ON_DAY2 (default false).
- Repair Options: repair a part from other "repair from" parts by priority. Example: need 50, gives 20 of B, 20 of C, 10 of D. Types are Repair and Is Rework (good to different good). Auto Repair. Priority. Lock. [parts/parts_topics/overview_of_repair_options.html], [parts/parts_pid/pid_new_edit_repair_options_page.html]
- Rotables [parts/parts_topics/overview_of_rotable_parts_planning.html]:
  - Rotable Bank: a virtual pool; a core/customer return replaces the removed part.
  - Planned across a group of locations.
  - Steps: define rotable, set planning params, run Stock Level Generation, review.
  - Review types 142, 143, 144, 248, 249. [parts/parts_topics/review_types_for_rotable_parts_planning.html]
- Rotable Pooling (IO): pooled demand (Houston 5 + Chicago 13 = 18), Pool Max Stock Max constraints. [glossary/rotable_pooling.html]
- Disassembly (Reduce to Produce):
  - Fields: Disassembly Capacity (per slice), Cost, Time, Plan/Rec Start and End Dates, Rec Disassembly Qty, Value.
  - Setup: Include In Analysis; Priority, where the highest number is evaluated first.
  - [parts/parts_pid/pid_disassembly_page.html], [parts/parts_pid/pid_disassembly_setup.html]

====================================================================
8. REVIEW REASONS, ALERTS, REVIEW BOARD, DELAY, MY REVIEW REASONS
====================================================================

8.1 Structure
- Review Board: "A list of SKUs that are exceptional", e.g. type 18 Critically Short. Tabs appear only for subscribed categories. [glossary/review_board.html]
- Review Categories: Forecasting, ASL, Procurement, Location Analysis, Alerts, Lifecycle, Install Base, Order Plan, Pricing, SCS, Dispatch. [glossary/review_category.html]
- Order Plan review types use On Hand Recommended "unless the word Approved appears". [glossary/review_type.html]
- Review Type definition fields: Review Reason, Active, Short Name, Host Review Type ID, Category, Grid ID (-1), Score, Use For Filters, Sort Order, Use Parameters 1/2, Email Template, Review SQL or Review Object. [core/core_pid/pid_review_type_page_view_new_edit.html]
- Run Time Order [core/core_pid/pid_review_type_page_view_new_edit.html]:
  - 0: set by the application during AutoPilot.
  - 1: Review process.
  - 2: during Generate Order Plan, before planning.
  - 3: after planning, before auto-approval; can block it.
  - 4: set by the application during Order Plan.
  - 5: after auto-approval.
- Review Parameter per review type: Parameter 1/2, Block Auto Approval, Trigger Order Plan, Active, Delay Days (falls back to REVIEWED_ACTION_DELAY_DAYS), Retention (Retained / Use Retention Period, default 30 days / Delete), Type (Exceptions or Notifications). [core/core_pid/pid_new_edit_review_parameter_page.html]
- Review Age = System Date - First Create Date (Manual System Date if set). [glossary/review_age.html]

8.2 Delay and review actions
- Delay Until Date can be set on the Work Queue, Review Board and IPWS Review Board. It cannot be set on the Alerts tab. [core/core_topics/manually_delay_review.html]
- IPWS Delay options: Set Default Delay Date (needs RB_DEF_DELAY_FROM_TODAY=true plus Delay Days), Set Delay Date, Remove Delay Date. [parts/parts_topics/delaying_rb_records_on_ipws_review_board_review_board_tab.html]
- Part Reviewed / SKU Reviewed set the Delay Until Date for that review type. They do not delay user alert messages. [core/core_topics/review_part_pair.html]
- My Review Reasons filters by review subscriptions. It is available on Demand, Demand Summary, IPWS, Optimal Levels, Rotable Levels and Work Queue. [core/core_topics/filtering_with_my_review_reasons.html]
- Priority comes from the Review Subscriptions tab of User Rights Setup. [glossary/review_board_2.html]

8.3 AutoPilot-parameter thresholds [parts/parts_pid/pid_new_edit_autopilot_parameter_page.html]
- Forecasted vs Actual (types 1-3): Review Slices, Review Limit (sigma), Demand Minimum.
- Forecast Monitor (types 4-6): Monitor Slice, Percentage Change, Forecast Minimum.
- Actions: Critical Shortage Threshold, Excess Threshold, Fair Share Reserve / Qty / Priority.
- Automatically Add/Delete ASLs. Minimum ROP. Minimum Stock Max.
- Round-Up Thresholds: SS, ROP, EOQ, RROP, REOQ, Days.

8.4 Standard review types relevant to supply planning [glossary/review_reason_2.html]
- ASL: 7 auto add/remove, 20 field ASL not on source ASL, 60/61 pooling, 91 ASL lock expired, 132 Mid-Slice ASL.
- Procurement: 8/10 repair LT change, 12 qty > MaxEOQ/SetEOQ, 13 same source and destination, 14 repair qty > max REOQ.
- Order Plan:
  - 15 Out of Plan Range, 16 in supercession chain, 17 change to primary vendor.
  - 18 Critically Short. 19 In Excess (Parameter 1 threshold).
  - 22 multiple purchase agreements, 23 Maximum Order Value Exceeded, 24/25 qty/date change outside commit level.
  - 26 new sales order, 27 new chain info, 28 OHG below ROP (not recommended), 29 Order is to be Frozen, 30 no valid PO agreement.
  - 36-39 PO requisition/agreement, 40/47 recommended qty more/less than original, 48/49 date earlier/later.
  - 51 Future Backorder exists, 52 Recommended OHG below 0 (P1), 53 OHG below SS, 55 OHG above Repair SMAX, 56 processing exception.
  - 84/85 requisition approvals.
  - 115 Pair Forced To Timephase, 116 No Unconstrained Date, 117 Future Balance below ROP.
  - 130 Expedites, 131 Deferrals, 140 Increases, 141 Decreases, 142-144 rotable bank.
  - 215 On Hold Order Date close to expiry, 248/249 Set Allotment.
  - 259 GAP Processing Exception.
  - 318 Trigger Point used because the time-phased solution exceeded time/attempt limits.
  - 320 Planned OHG below 0.
  - 323-326, 332 new recommended repair / replenishment / balancing / procurement / excess recall orders.
  - 327 Overdue host orders (P1 days, P2 days*qty).
  - 328 Shortage with host orders outside LT; 329 Excess with host orders within LT (both non-SCS).
  - 331 Critically Short: Zero On Hand with Backorder (OHN + OHF - Allocated <= 0 and BO > 0).
  - 333 Recommended OHG below 0 today, 334 Critically Short Today, 335 new zero-quantity recommendation.
  - 336 processing stopped early (ABR), 337/338 potential configuration error (TP / Trigger Point).
  - 345 today's IP at or below ROP (TPROP).
  - 346-348 ROP/SMax conflict with sizing, 349/350/352/353 vendor capacity.
- SCS: 93, 94, 95, 112, 134-137.
- Stock Levels: 207-214 override expired, 222-227 SS/ROP/RROP min/max violations.
- Lifecycle/LTB: 41-46 usage rate, 65, 80, 81, 118, 119, 120.
- Forecasting examples: 1-6, 50, 62-64, 83, 86, 92/111 over/under-consumed forecast, 138/139 tracking signal.
- Vendor Group MinOQ: 317.
- Alerts: 9 User Alert Messages.

====================================================================
9. BACKORDER CATEGORIZATION (ROOT CAUSE)
====================================================================
Categories in priority order, used by the Backorder Categorization, Backorder Days, Demand Miss Analysis and Performance 360 dashboards [glossary_pai/root_cause_categorization.html]:

| # | Category | Condition |
|---|---|---|
| 1 | Forced Non-Stock | An override/constraint forces no stock, e.g. SMax Fixed Override = 0 |
| 2 | No Supply Source | Procurable = Replenishable = Repairable = N |
| 3 | On ASL with On Order | ASL = Y, shortage at parent, On Order + In Repair > 0 (Original values for BO dashboards) |
| 3.1 | Vendor Delays with On ASL with OnOrder | Miss at a procuring location plus review 327 there |
| 3.2 | Vendor Delays at Procuring Location with On ASL with OnOrder | Miss at a replenishment location plus 327 at its procurement location |
| 3.3 | Under Forecast with On ASL with OnOrder | Miss plus an under-forecast reason, e.g. 138 |
| 3.4 | On ASL with On Order Not Categorized | Other |
| 4 | On ASL without On Order | ASL = Y, On Order + In Repair = 0 |
| 5 | System Chose Not to Stock and Forecast Exists | ASL = N, no forcing override, forecast not 0 |
| 6 | First Time Demand | No prior demand history (Demand Detail ignored) |
| 7 | System Chose Not to Stock and No Forecast Exists | ASL = N, forecast 0 |
| 8 | Not Categorized | No condition met |

- The 327 look-back comes from servigistics.analytics.demandmiss.pastlookupdays (e.g. 30). [glossary_pai/root_cause_categorization.html]
- The Backorder Categorization dashboard is reachable from the menu, Planner Home or Performance 360. Query object BackorderCategorization; tables include IPCS_STOCK_AMOUNT, IPCS_REVIEW_BOARD, IPCS_ORDER_PLAN_SCALARS. [functional/dashboard_backorder_categorization.html], [functional/dashboard_backorder_categorization_2.html]
- No dedicated "backorder priority" field was found. Backorder handling uses Include Backorder in Order Plan, Fair Share, OP_BALANCE_BONEED_*, ATM Backorder Threshold, and review types 51, 331 and 327.

====================================================================
10. LEAD TIMES AND CALENDARS
====================================================================
Lead times
- Vendor Location SKU Lead Time: Order Type, Transport Mode, Ordering and Transport Calendars, Processing Length + SD, Transport Length + SD, Block Auto Approvals, spreading, Order Limit Periods, sizing, split. [parts/parts_pid/pid_new_edit_vendor_location_sku_lead_time_page.html]
- Vendor Location Lead Time: Transport Mode/Calendar/Length/SD/Cost, Program Indicator. [parts/parts_pid/pid_new_edit_vendor_location_lead_time_page.html]
- Replenishment/Balancing Lead Time and SKU Lead Time: From/To location, Processing Length/SD, Transport Mode/Length/SD, Variable Transportation Cost, MOQ, Lot Size, Minimum Order Value. [parts/parts_pid/pid_new_edit_replenishment_balancing_lead_time_page.html], [parts/parts_pid/pid_new_edit_replenishment_balance_sku_lead_time_page.html]
- Transport Modes carry Transport Length + SD. [parts/parts_pid/pid_new_edit_transport_modes_page.html]
- Procurement Lead Time (Orders container) "includes the wait time due to shortages from the replenishment parent and from components"; the same definition as Effective Lead Time. [parts/parts_pid/pid_ipws_orders_section.html], [glossary/effective_lead_time.html]
- Put-away: Effective dates include Put Away Lead Time. "Set the Put Away Length to 1 to force ... Effective Available Date from today to tomorrow", or use OP_OVERDUE_ORDERS_AVAILABLE_TOMORROW (default false on upgrade, true on new installs). [glossary/effective_available_date.html], [glossary/global_settings_sp.html]
- Plan Date = Ship Date "reduces the effective lead time by planning as if orders can be placed and shipped at Transport + Putaway lead time". [parts/parts_pid/pid_new_edit_ordering_parameters_page_general_tab.html]
- Buffer Days for Future Chain Parts, waterfalled location then location type. [parts/parts_pid/pid_ipws_order_sku_parameters_section.html]

Calendars
- Types [glossary/calendars.html]:
  - Working: holidays and closed days.
  - Ordering: valid order dates.
  - Transportation.
  - Parent calendars: only Working calendars can be parents; parent closures become "block out days" for ordering/transport children.
- An Execution calendar controls on which days Order Plan sub-processes execute. [parts/parts_pid/pid_new_edit_execution_calendar_page.html]
- Ordering calendar fields: Ordering Days of Week plus special Order Dates (e.g. 1st/15th). [parts/parts_pid/pid_new_edit_ordering_calendar_page.html]
- Calendar adjustments in TPROP [glossary/global_settings_sp.html]:
  - OP_TIME_PHASED_ROP_INCLUDE_CALENDAR_NEED (default true) orders for gaps to the next available date.
  - OP_TIME_PHASED_ROP_CALENDAR_ADJUSTMENTS_AT_TOP_MOST_LOC_ONLY (default true).
  - OP_TIME_PHASED_ROP_CALENDAR_ADJUSTMENT_IO_LEAD_TIME_INCREASE (default 7): 7 for weekly ordering, 14 for fortnightly, 0 to let Order Plan handle it.
- OP_IGNORE_ORDER_DATE_IN_TRIGGERPT (default false). [glossary/global_settings_sp.html]

====================================================================
11. LAST TIME BUY, PROVISIONING, END OF LIFE
====================================================================
Overview
- LTB is triggered by end of production (EOP) or a vendor discontinuing the part. [glossary/last_time_buy.html]
- Modes: Top-down (global buy, then allocate to regions) and Bottom-up (each region independently). [glossary/last_time_buy.html]
- Profile-based forecasting removes the need for install-base data. [glossary/last_time_buy.html]

Eight workflows [glossary/last_time_buy_2.html]
1. Profile Management: parameter sets, then profiles (system-generated / user / imported), then approve.
2. Shipment Service Factor Profile (optional; SBLI forecast).
3. LTB Identification via the LTB Work Queue.
4. LTB Forecast: EOP to End of Service.
5. Decay Rate Parameter schemes.
6. Recommendation.
7. Inventory Monitoring: Lifecycle tab review types.
8. Re-enable LTB processes.

Forecast and profiles
- The forecast is a regression of pre-EOP demand on the selected profiles. Adjust by percent or amount per slice; approve the Reviewed Forecast. [glossary/last_time_buy_3.html]
- Profiles come from cluster analysis of parts with a complete life cycle. [glossary/last_time_buy_profile.html]
- Profile Parameters: Approval All, Horizon Begin (negative slices before EOP), Horizon End, Iterations, LTB Date Setting (LTB Date / First Demand Slice), Max Distance Criteria, Min SKU per Profile, Profiling vs Forecasting Segments. [parts/parts_pid/pid_new_edit_ltb_profile_parameters.html]
- Profile approval happens on the Last Time Buy Profile Review page (Approve / Disapprove). [parts/parts_topics/approving_rejecting_last_time_buy_profiles.html]
- LTB Parameter Set: Significance Level, Allow Negative Coefficient (LTB_REGRESSION_FORCE_NO_INTERCEPT), Shipment Based Forecast Weight, Regress on SBLI (Exclude/Include/Enforce), Failure Rate Window, Auto-approve LTB Forecast / Order, Regression Demand History Method (Full / Fixed Length), Regression Alignment (Best Search / EOP). [parts/parts_pid/pid_new_edit_ltb_parameters_set_page.html]

Recommendation General tab [parts/parts_pid/pid_ltb_reco_page_general_tab.html]
- Dates: Last Time Buy Date, Decay Start Date, Field Support-To Date, Support To Date.
- Rates and quantities: Return / Repair Wash Rate, Salvage Rate, Slice Forecast Decay Rate, LTB Slice/Actual Decay Rate + SD, current OH / On-Order / In-Repair.
- Notification Limits: Monitor To Date, High/Low Limit, Early Used Up Limit (Days), Excess at the End.
- Recommendations: Recommended Qty (override allowed), Excess Not Used, Total Forecast (decay applied after the Decay Start Date), Total Repair Forecast, Current Inventory Balance, Roll Up Inventory.
  - Need = Total Forecast - Total Repair Forecast - Current Inventory - Roll Up Inventory.
  - Excess Used. LTB Method: Global LTB / Allocate To Locations. Global LTB Quantity.
- LTB Status: Not Approved / Approved / Done.

Actions
- Tabs: Allocation (Allocation %, Push All), Product, Part Shipment (SBLI), Decay Rate (up to 3 like parts), Total LTB. Process Changes runs it; alternatively run Calculate Decay Rate then Last Time Buy in AutoPilot. [parts/parts_topics/generating_last_time_buy_recommendations.html]
- On Approve + Save, "a Last Time Buy procurement order will be generated the next time the AutoPilot runs"; allocations generate replenishment orders. [parts/parts_topics/generating_last_time_buy_recommendations.html]
- Decay-rate scheme: Override Decay Rate, Decay Start Slice, Slice Number, Calculation Type (Slice / Actual / Group). [parts/parts_pid/pid_new_edit_ltb_decay_rate_parameter_page.html]
- Monitoring uses review types 65, 80, 81, 118, 119, 120. [parts/parts_topics/monitoring_last_time_buy_inventory_levels.html]
- Re-enable: LTB Work Queue > Run > "Re-enable Last Time Buy for location(s)" or "for selected SKUs". [parts/parts_topics/reenabling_last_time_buy_processes_for_multiple_pairs.html]
- A recommendation with allocations cannot be deleted. [parts/parts_topics/clearing_last_time_buy_recommendations.html]

Provisioning
- Initial Provisioning and Re-Provisioning are "no longer supported as of the 12.0.0.0 release" but still exist for current users. [core/core_topics/initial_provisioning_forecast_method.html], [core/core_topics/re_provisioning_forecast_method.html]
- Provision Forecasting is replaced by Causal Forecasting. [parts/parts_topics/overview_of_provision_forecasting.html]

====================================================================
12. OP_* AND RELATED GLOBAL SETTINGS (CONSOLIDATED)
====================================================================
Default values are from [glossary/global_settings_sp.html] unless another source is noted.

| Setting | Default | Effect |
|---|---|---|
| OP_TIME_PHASED_ROP_ENABLE | false | Enables TPROP |
| OP_ADD_DAYS_TO_LT_TO_CALC_TRIGGER_INVENTORY_POSITION | 0 | Days added to LT for child sales orders |
| OP_ADD_DAYS_TO_LT_TO_CALC_TOROP_BALANCE | not documented | Sales-order buffer days; -1 = whole horizon [parts/parts_pid/pid_ipws_inventory_position_section.html] |
| OP_BALANCE_UPTO_SMAX | false | Balance to ROP+1 vs Stock Max |
| OP_BALANCE_USE_ONHANDEXCESS | false | Compare today's OHG to ROP/SMax for excess |
| OP_BALANCE_BONEED_IN_TIMEPHASED / _IN_TRIGGER | not documented | Balance backorders first [glossary/balancing.html] |
| OP_COUNT_SALES_RETURNS_THROUGH_HORIZON | true | Returns counted through horizon vs only to return LT |
| OP_ENABLE_TIMEPHASED_REPL_CHAIN_DEFICIT | false | Plan child deficits at parent |
| OP_ENABLE_TRIGGER_NEED_TO_SMAX | true | Pre-order for children up to SMax |
| OP_FORECASTED_RETURNS_STARTING_ON_DAY2 | false | See wording note below |
| OP_GENERATE_ORDER_PLAN_PART_HEALTH_DATA | false | Populates Part Health |
| OP_IGNORE_ORDER_DATE_IN_TRIGGERPT | false | Ignore the order-date calendar |
| OP_IGNORE_RETURN_FORECAST_UNTIL_RETURN_LT | true | Avoid return double count |
| OP_INCLUDE_SALES_ORDERS_TO_CALC_TRIGGER_INVENTORY_POSITION | true | Include sales orders |
| OP_OVERDUE_ORDERS_AVAILABLE_TOMORROW | false upgrade / true new | Overdue EAD becomes tomorrow |
| OP_REDUCE_PARENT_NEED_BY_IP_EXCESS | false | Roll child excess to parent IP |
| OP_SCS_MOVE_TG_TO_AVAIL | a | Time-gate move a / b / n |
| OP_SCS_TG_RESPECT_CAL | true | SCS respects calendar |
| OP_SHORTAGE_SORT_CRITERIA_1 / _2 | q / s | Balancing sort |
| OP_TIME_PHASED_ROP_CALENDAR_ADJUSTMENTS_AT_TOP_MOST_LOC_ONLY | true | Calendar adjustment only at top-most locations |
| OP_TIME_PHASED_ROP_CALENDAR_ADJUSTMENT_IO_LEAD_TIME_INCREASE | 7 | Days handled by IO |
| OP_TIME_PHASED_ROP_INCLUDE_CALENDAR_NEED | true | Order for closed-period gaps |
| OP_TIME_PHASED_ROP_IP_DAYS_TO_OUTPUT | listed as "true"; recommended 14 | Daily IP columns |
| OP_TIME_PHASED_ROP_OUTPUT_ZERO_QTY_RECS | true | Output today's zero-quantity replenishment recommendations |
| OP_TIME_PHASED_ROP_USES_TIME_PHASED_ROP_FAIRSHARE | true | Fair Share backorder prioritization |
| OP_TIME_PHASED_ROP_TOP_MOST_LOC_ONLY | not documented | Top-most future balance orders (release note SPM-103400) [release_notes/release_13_1_0_0/resolved_issues_13_1_0_0.html] |
| OP_VENDOR_CAPACITY_DATE_INDEX | 0 | 0 Order / 1 Ship / 2 Receive / 3 Available |
| OP_USE_ACTUALS | true | Use actual/effective dates [parts/parts_pid/pid_ipws_time_series_grid_section.html] |
| OP_WRITE_PART_DETAIL | not documented | Order Details hyperlinks [glossary/order_details.html] |
| OP_ENABLE_ABR | true | ABR [glossary/availability_based_replenishment.html] |
| OP_MAX_ABR_RETRIES / OP_ABR_RETRY_STOP_PERCENTAGE | not documented | ABR retry limits [glossary/availability_based_replenishment.html] |
| OP_MAX_CONSTRAINED_DAYS | not documented | ABR horizon, not recommended [glossary/availability_based_replenishment.html] |
| OP_INHOUSE_UPTO_SMAX | not documented | Chain transfer to ROP+1 vs SMax [parts/parts_pid/pid_ipws_inventory_position_summary.html] |
| OP_NONASL_FUTURE_PROCURE / OP_ROLLUP_NONASL_FCST | not documented | Non-ASL forecast in GAP [glossary/group_of_associated_parts.html] |
| OP_FAIRSHARE_SORT_CRITERIA_1..4 | new installs: q, f, Null, Null | Fair Share sort [release_notes/release_13_0_1_0/rn_enhancements_sp_5.html] |
| OP_USE_REPAIR_COST_FOR_REPAIR_AUTOAPPR | not documented | Auto-approval cost basis [glossary/order_cost.html] |
| OP_OON_COUNTS_RECOMMENDED_ALSO | not documented | Out-of-network recommended quantities [glossary/network.html] |
| OP_MAX_PARTKIT_DEPTH | not documented | Kit display depth [parts/parts_smart_help/sh_ipws_part_kit_details.html] |
| OP_LOGSS / OP_LOGBAL | not documented | Order Plan trace properties [glossary/autopilot_processes_8.html] |
| OP_PROCESSING_WARNING | not documented | Only appears in the audit-trail glossary [glossary/audit_trail_fields_user_setup.html] |

OP_FORECASTED_RETURNS_STARTING_ON_DAY2 wording: true makes returns "considered available at the end of the day"; false means they are "not available for picking today" (the page suits false to offsite repair). Both states describe the same timing, so the page is unclear.

Two pages give conflicting descriptions:
- OP_TIME_PHASED_ROP_IP_DAYS_TO_OUTPUT is listed with default "true", but it is a day count; 14 is recommended.
- OP_TIME_PHASED_ROP_OUTPUT_ZERO_QTY_RECS describes both true and false as "are created".

Non-OP settings from the same page
- ALLOW_MASS_APPROVAL_TO_CO_ORDERS: false upgrade / true new.
- APPROVE_FOR_UPLOAD: false.
- DEPLOYMENT_LOADGAP_LOC_LIMIT: 500.
- ENABLE_ADVANCED_LAYOUT_IPWS: false.
- ENABLE_DASHBOARD_CACHE: true.
- ENABLE_PLAN_INTELLIGENCE_IPWS: false.
- ENABLE_PROPERTYGRID_GRIDLINES: false.
- ENABLE_LOCATION_PINNING: false.
- MAX_ROWS_FOR_FULL_OPERATION: 2000.
- PI_VENDOR_PERF_CALCULATE_PERIOD_MONTHS: 12. PI_VENDOR_PERF_MIN_ORDERS: 10. PI_VENDOR_PERF_RETAIN_SLICES_MONTHS: 6.
- PWS_EDIT_CO_ORDERS: true.
- PWS_UPLOAD: false.
- RESTRICT_MANUAL_ORDER_CREATION: false.
- RS_MAX_PAGES: 25.
- USE_TIME_PHASED_LEVELS: true.
- Others referenced elsewhere: RB_DEF_DELAY_FROM_TODAY, REVIEWED_ACTION_DELAY_DAYS, GENERATE_OP_SL_OUTSTOCK_DAYS, PWS_TOT_REQ_INCLUDE_CHAINS, PWS_TOT_REQ_INCLUDE_REPL, MEO_OVERRIDE_MAX_QTY, FISCAL_YR_STARTING_MONTH, LEVELS_DAYS_CONSTANT, MID_SLICE_ASL_DA_THRESHOLD, IO_TPROP_ROUND_SS.

====================================================================
13. OTHER PARAMETER SCHEMES AND PAGES
====================================================================
- Action Parameters: Procurement Allowed, Repair Allowed (normally central only), Source Location Name override, Priority Sequence. Part / location / SKU overrides take precedence. [parts/parts_pid/pid_new_edit_action_parameter_page.html]
- Parameter Settings page tabs: Action, AutoPilot, Balancing, Excess Recall, Forecast Netting, Forecasting, LTB Decay Rate, Ordering, Planning, Pooling, Schedule Change Suppression, Transport Mode. These are the ps_page_* files in parts/parts_pid/.
- Other Supply Planning pages found in the crawl (file names under parts/parts_pid/): Procurement, Repair and Replenishment (prr_pages), Open Orders, Order Plan - Order History, Sales Orders, Sales Returns, Expected Backorders, Critical Shortages, Excess, Expedite Report, Daily Balance Summary/Detail Report, Work Queue, LTB Work Queue, Procurement by Vendor, Vendor Programs, Vendor Group Min Order Quantity, Disassembly, Repair Options, Rotable Levels, Calendars (Working / Ordering / Transportation / Process Execution tabs), Transport Modes, Vendor Location SKU Capacity/Priority, Purchase Order Agreements/Requisitions, Part Substitution, Order Frequency Set, Inventory Studio (Order Status, Purchase/Transfer/Excess Return Recommendations tabs).