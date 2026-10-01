PTC SERVIGISTICS 13.x HELP: RESEARCH NOTES (Topics A and B)

Scope: I searched the text crawl for dealer, field stock, ServiceMax, consignment, security, segments, part classification, AutoPilot and KPI topics. I skipped the Pricing and release-notes files except where noted. Every fact below ends with the URL from the first line of its source file. All URLs start with https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/, and I write that prefix out in full each time.

======================================================================
PART A: DEALER NETWORK, FIELD STOCK, LOCATION TYPES
======================================================================

A0. Coverage gaps: the corpus has none of these
- "ServiceMax": 0 hits anywhere in the corpus (grep -il servicemax found nothing).
- "consign", "customer owned" / "customer-owned": 0 hits outside release notes. The only hits for "consign|customer.owned|technician" are in glossary files about technicians (see A6). There is no consignment or customer-owned inventory concept in core, inv_opt or parts.
- "Dealer returns" as a named feature: not found. The closest features are the Inventory Studio "Excess Return Recommendations" tab (A3) and the "Excess Recall" order type (A5).
- "Trunk stock" / "van stock": no dedicated feature. Technician trunks appear only in marketing-style glossary text (A6).
- "Dealer-managed inventory" / "dealer stocking": the documented features are "Dealer Planning" (a Role plus the Inventory Collaboration page) and the location flag "Dealer = Yes" (A4).

A1. The Dealer role
- "Dealer" is "A predefined Role Name that can be assigned to a user on the Users page." https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/dealer.html
- Valid Role Name options: Customer; Dealer ("the database name is DealerRole"); Planner ("ARRole"); Pricing ("PricingRole"). "Roles are defined during implementation." https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/role_name.html
- Rights are assigned automatically: "User rights are automatically assigned to a user that has a Role Name of Dealer. The listing of user rights is visible on the Dealer tab of the User Rights Setup page." https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/dealer.html
- Home page: "The home page is configured to the Inventory Collaboration page when the Role Name is set to Dealer." https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/dealer.html
- Page restrictions applied by the Dealer role (same URL):
  - All pages: the user cannot view Part Properties or currency fields.
  - Inventory Collaboration: the Units button on the Fill Rate Exchange Curve container is not available, so data is shown in units. Configurable Filter fields are limited to the fields configured for the user on the SKU Levels container.
  - Location Summary: the Run button is not available. Scenario comparison is removed, so the Scenario(B), Period and Show Delta For buttons are not available.
  - Part single-select button: no Advanced Find and no Part Properties option.
  - Segment Summary: scenario comparison is removed.
  - SKU Overrides: the Import button is not available.
  Source: https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/dealer.html

A2. User Rights Setup Page, Dealer tab
- "This tab contains the user rights for users that have the Role of Dealer assigned, or have a User Template that has a Role of Dealer assigned." https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/core/core_smart_help/sh_urs_page_dealer_tab.html
- "The rights that are listed on this page are defined at the time of installation and cannot be modified. Contact PTC Technical Support if any changes need to be made…" (same URL)
- "The user right settings on the Action Setup, Admin Setup, and Base Setup tabs are not applicable." Also: "Changing a user right assignment on any tab other than the Dealer tab for users has no effect." (same URL)
- Some rights can be assigned by segment ("Assign or revoke rights by segment"). (same URL)
- Inventory Collaboration right: "When Approve access is selected and the Role Name assigned to the user is Dealer, then the user has access to update the Production Status field on the SKU Levels container of the Inventory Collaboration page." https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/core/core_smart_help/sh_urs_page_inventory_optimization_tab.html (also https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/base_setup_rights.html)

A3. Dealer Planning: definition, setup and workflow
- Definition: "This feature enables the review and collaboration of target stock level information from a single page." Related page: Inventory Collaboration. https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/dealer_planning.html
- Setup ("Enable the Dealer Planning Process"). Source for all steps: https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/dealer_planning_2.html
  1. On the Users page, set Role Name = Dealer.
  2. On the Dealer User Rights Setup page, validate these rights:

     | Process                           | Rights |
     |-----------------------------------|--------|
     | Inventory Collaboration           | View + Modify. Approve is optional and lets the user change Production Status |
     | Location Summary                  | View |
     | Optimization Set Assignments      | View + Modify. "This should only be set for administrators." |
     | Segment Summary                   | View |
     | SKU Overrides                     | View + Modify |
     | User Can Configure Grids (optional) | Not Allowed restricts field display configuration |
     | View All Optimization Results     | Not Allowed if the user should not see all SKUs; Allowed if they should |

  3. Optional: set the global setting DEALER_APP_RESTRICTIONS = true.
  4. On the Override Security page, create a role with Allow Recommend = Yes, Allow Review = Yes, and "Allow Deletion of overrides set by other planners" = Yes.
  5. On the Override Assignment page, create one assignment per user: Override Security = the role from step 4, Planner = the user, Segments = move the appropriate segments from Available to Selected.
  6. On the Optimization Set Assignment page, assign an optimization set to each Dealer user. This "will populate the scenario on the Location Summary page and Inventory Collaboration page with the scenario that is in collaboration and associated with the user."
  7. Open the Scenarios page, select a scenario, click Run and choose the "Start Collaboration" job.
- The DEALER_APP_RESTRICTIONS global setting (default false; Usage: Dealer Planning). When true, Dealer users are restricted as follows:
  - "The Minimum and Maximum field entries are not visible when creating or modifying a SKU Override."
  - "The Pre-Optimization fields on the Create/Edit SKU Override page are not available."
  - "Filters created on the Configurable Filters page cannot be shared."
  Source: https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/global_settings_io.html
- The SKU Overrides page describes the same setting as restricting "access to scenarios, locations, configurable filters and minimum and maximum SKU Overrides." https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/inv_opt/inv_opt_smart_help/sh_sku_overrides_page_2.html
- Pre-Optimization is where Pre-Optimization SKU Overrides and SKU Constraints are applied. Those fields are hidden when DEALER_APP_RESTRICTIONS = true. https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/pre_optimization.html
- Dealer Planning Workflow. Source for all steps: https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/dealer_planning_3.html
  1. Open Inventory Collaboration and analyse each SKU.
  2. Select a row on the SKU Levels container to populate the other containers.
  3. Compare Optimized levels with the Minimum/Maximum levels.
  4. Enter Fixed override levels if needed.
  5. Set Production Status: "If values are acceptable, select Approved". "If values are not acceptable, enter overrides in the SKU Levels container and click Disapproved". This needs the Approve option on the Inventory Collaboration right.
- A Location Summary feature is marked "only available when the Dealer Planning process is enabled". https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/inv_opt/inv_opt_smart_help/sh_location_summary_page.html

A3b. Inventory Collaboration page (Dealer home page)
- "Use this page to view and approve level recommendations resulting from the Inventory Optimization calculation process and enter SKU overrides." https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/inv_opt/inv_opt_smart_help/sh_inventory_collaboration_page.html
- Containers: Constraint and Override Details, Daily Demands, Demand/Forecast Graph, Fill Rate by Stock Level, Fill Rate Exchange Curve, Forecast vs ROP Value, Journal, Part Chain Details, SKU Demand Details, SKU Exception, SKU Levels (the default), SKU Overrides, Time Series. (same URL)
- Fixed override fields in the SKU Levels container: Fixed EOQ, Fixed ROP, Fixed Safety Stock, Fixed Stock Maximum. When an override exists, Comment, End Date and Override Reason become editable. https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/inv_opt/inv_opt_smart_help/sh_inventory_collaboration_page_3.html

A3c. Inventory Studio (lightweight dealer and parts-manager UI in Supply Planning)
- Menu path: Supply Planning > Workflow > Action > Inventory Studio. "This page is intended for users that do not require the full capabilities of a parts planner, such as a parts manager at a dealership." https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/parts/parts_smart_help/sh_inventory_studio_page.html
- Tabs (same URL):
  - Purchase Recommendations: review and approve PO recommendations.
  - Excess Return Recommendations: "recommendations for returning excess inventory".
  - Transfer Recommendations.
  - Stocking Policy Recommendations: "scheduled to be delivered in a future release".
  - Requests Received: requests from other locations.
  - Requests Sent.
  - Order Status: approved orders that are open or in process.
  - Parts: search the Part Catalog to order non-stocked parts, and search for and request parts from another location.
- Rights on the Inventory Studio tab of User Rights Setup. Source: https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/core/core_smart_help/sh_urs_page_inventory_studio_tab.html
  - Inventory Studio (Order Status and Parts tabs): View, Order Part, Configure, Approve Limit.
  - Excess Return Recommendations, Purchase Recommendations, Stocking Policy Recommendations, Transfer Recommendations: View, Approve & Reject, or Override.
  - Part Locator: View or Request Part.
  - Requests Received: View or Approve & Reject.
  - Requests Sent: View or Delete.

A4. Location flags and location types
- Pricing section of the New/Edit Location page: Dealer = "Yes indicates that this location is a dealer location. When Dealer and Sub Location are both set to No, the location is a pricing location (or regular location)." Price Active = the location is included in pricing. https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/core/core_pid/pid_new_edit_location_page.html
- On the Location Properties General tab, Dealer is "A yes/no flag to indicate if the pricing location type = Dealer" and Sub Location is "A yes/no flag to indicate if the pricing location type = Sub Location." https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/core/core_pid/pid_loc_prop_page_general_tab.html
- Other planning fields on the New/Edit Location page. Source for all: https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/core/core_pid/pid_new_edit_location_page.html
  - Critical.
  - Active.
  - Procurement Allowed: "Normally, procurement is done only at central locations… procurement actions may be permitted at certain field locations."
  - Repair Allowed: same pattern as Procurement Allowed.
  - Parent: replenishment hierarchy parent; a central location has Parent = Self.
  - Like Location and Demand Increment Factor: borrow demand history for a new location.
  - Replenishment Source Location Override.
  - Region.
  - Bin Type:
    - Demand ("d"): no forecasting; demand rolls up to the parent.
    - Forecast ("f"): forecast at the bin, rolled up to the parent.
  - Location Type.
  - Network: limits balancing of excess On Hand to locations within the network.
  - Process Group.
  - Put Away Length and Put Away Standard Deviation.
  - Fair Share Priority, Fair Share Reserve and Fair Share Reserve Quantity.
  - Disconnected Replenishment: "replenishment orders generated from the destination location will only be recognized at the upstream location when orders are approved".
  - Replenishment Source Internal Stream.
  - Geo fields, including Geo Quality of Match codes 8/5/4/2/1 and Geo Source u = user, g = Google.
  - Host Location ID.
  - Enable Alternate Transport Mode.
- Location Type: "The type of this location in the procurement and replenishment hierarchy. Location Types are defined in the Location Types page and assigned to locations via the Locations page." https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/location_type.html
- New/Edit Location Types page fields. Source for all: https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/core/core_pid/pid_new_edit_location_types_page.html
  - Name: "The name of the location type (like central, field, etc.)".
  - Fair Share Priority: replenishes field locations to Safety Stock in priority order (up to 99), then to ROP, then by Days On Hand. "This feature is only an advisory tool - it is not enforced."
  - Miles Per Hour: used in "Time To Location = Distance … / Miles Per Hour".
  - Calendar Name.
  - Buffer Days for Future Chain Parts: waterfalled location, then location type.
- Echelon: "The hierarchy level of the supply chain." https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/echelon.html
- Location Hierarchies: "define replenishment trees for a specific part… You can define different replenishment hierarchies by part group." https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/location_hierarchies.html
- Global setting ENABLE_LOCATION_HIERARCHY: default false. https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/global_settings_io.html
- Emergency Backup Location Optimization: "When a part from the field location is needed and it is not available, the emergency backup location is considered for replenishment." https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/emergency_backup_location_optimization.html
  - Setup: a location hierarchy of backup locations, then a service group with Service Metric = "Fill Rate with Emergency Backup", then add it to an Optimization Set.
  - The fill rate method is always "Lost Sales for a Covered SKU". (same URL)

A5. Returns and excess
- Excess: "Excess = Stock Level > Stock Maximum * Excess Threshold". Excesses are also posted for any inventory of a part not on that location's Authorized Stock List. The Excess Threshold is set via AutoPilot parameters. https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/excess.html
- Excess Recall is "One of the Order Types". It shows on the Planner 360° Supply Chain View and links to the Replenishment page. https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/excess_recall.html

A6. Field stock and technicians
- Servigistics "is specifically designed for implementation across the entire hierarchy of service parts locations, from central locations all the way to the smallest field stock locations such as technician trunks and parts kiosks." https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/servigistics.html
- Time-phased service group fill-rate target: "The lowest acceptable percentage of time that the parts to perform the service are available to the technicians." https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/inv_opt/inv_opt_pid/pid_time_phased_service_groups.html

======================================================================
PART B: SECURITY, SEGMENTS, CLASSIFICATION, AUTOPILOT, KPIs
======================================================================

B1. Users (Settings > Configuration > Users)
- New/Edit User page fields. Source for all: https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/core/core_pid/pid_new_edit_user_page.html
  - Sign In Name (case-sensitive).
  - Password and Confirm password: hidden "When the servigistics.authenticationtype WebUI parameter is set to REMOTE_USER".
  - First name, Last name, Description.
  - Password last modified, Last Login.
  - Template Name.
  - Role Name.
  - Preferred location.
  - Customer.
  - Account active.
  - Change on next login.
  - User Can Change Password.
  - Password Never Expires.
  - Promotions Revenue Impact Approval Limit Amount (Pricing).
  - Maximum records visible on price actions (Pricing).
  - Report Role (Intellicus).
  - Host Planner ID.
- Fields populated from a selected User Template: Role Name, Preferred Location, Customer, Account Active, Change on next login, User Can Change Password, Password Never Expires, the two pricing fields, and Report Role. "These settings can be overridden." (same URL)
- User Template: "A set of user settings and rights, defined on the User Templates page, that can be applied to multiple users." Per-user changes are made through "template overrides". https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/user_template.html
- Temporarily Assign User Rights page: Assign Rights Of (the absent user), Assign Rights To (the covering user), Effective Start Date, Effective End Date, Current Assignments. https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/core/core_pid/pid_temporarily_assign_user_rights_page.html
- Column Security: "A method used to restrict the display of columns on a page", assigned per user on the Column Security tab. https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/column_security.html

B2. User Rights Setup page (rights grouped by module as tabs)
- Tabs: Forecasting, Price Simulation, Price Analysis, Price Optimization, Inventory Optimization, Supply Planning, Inventory Studio, Processing, Analytics, Modeling, Settings, OTF Rights, Review Subscriptions, Column Security, Price Approval Roles, Import, Products, Custom Tables, Custom Pages, Segment Folders, Dealer, Action Setup Rights, Admin Setup Rights, Base Setup Rights. https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/core/core_smart_help/sh_user_rights_setup_page.html
- Page columns: Menu Path, Process / Page, Override Template (shown when a template is applied), Rights. https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/core/core_pid/pid_urs_page_tabs.html
- Right values (same URL):
  - Allowed.
  - Approve.
  - Approve & Reject.
  - Approve Limit: "validated against the Planned Quantity * Price per Unit".
  - Configure (own IPW layout) and Configure Default.
  - Create.
  - Create Policy and Segment.
  - Edit Table and Edit Settings (Custom Tables).
  - Modify and Modify All (Journal).
  - Modify Attach Rate.
  - Modify Production.
  - Modify Scenario.
  - Not Allowed.
  - Order Part and Request Part.
  - Run.
  - Save (what-if results to production).
  - Set Default Layout.
  - Upload (orders to host).
  - View, View Production, View Scenario.
- OTF Rights tab: "defines the OTF processes that a user can configure for display on a page." https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/core/core_smart_help/sh_urs_page_otf_rights_tab.html
- Segment Folders tab: "Allows users to access segments within segment nodes". You move nodes from Available to Selected. https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/core/core_smart_help/sh_urs_page_segment_folders_tab.html
- Override Security page fields: Role Name, Description, Allow Recommend, Allow Review (approve or reject recommended overrides), Allow Deletion of overrides set by other planners. https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/inv_opt/inv_opt_pid/pid_override_security_page.html
- Override Assignment page fields: Override Security, Planner (user), plus Segments (see A3). https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/inv_opt/inv_opt_pid/pid_override_assignment_page.html
- Optimization Set Assignments page: Optimization Set ("A collection of service groups that are assigned to a scenario") and Planner Name. https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/inv_opt/inv_opt_pid/pid_optimization_set_assignments.html

B3. Segments and segmentation (Settings > Configuration > Part Classification)
- The Part Classification menu contains ABC Class Sets, ABC Parameters, Custom Attributes and Segments. https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/core/core_topics/module_settings_part_classification.html
- Segment: "A group of SKUs that have attributes in common, such as lead times, geographic areas, forecasting methods, high or low value… You can apply processing parameters to all records in a segment at one time using segment coverages." https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/segment.html
  - Example: a critical-parts segment whose Demand Accommodation is set to 100% puts every critical part on the ASL. (same URL)
  - Strategies (same URL):
    - Matrix Segmentation Strategy: cross-reference the categories; for example price high/low × 4 part types = an 8-segment matrix.
    - Pyramid Segmentation Strategy: plan the most specific groups first, then more general ones, "finally ending with Default".
- Segment Coverages: "the conditions that define which parts are to be included in the segment". Coverages are equations joined with And/Or, for example "Part Type is equal to Manufactured And Standard Cost is greater than $1000 And Region starts with North". They may be case-sensitive, so "it is best to always use upper-case letters." https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/segment_coverages.html
- Segment Group: "Each SKU can only be assigned to one segment within the segment group. Each segment can only be assigned to one segment group." A SKU can otherwise belong to more than one segment. https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/segment_group.html
- Segment Tree: "groups segments within segment nodes that are arranged in a hierarchy. It provides another layer of segmentation as well as security enhancement." Node coverage acts as an "And" criterion for all segments in the node. https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/segment_tree.html
- New/Edit Segment page fields. Source for all: https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/core/core_pid/pid_new_edit_segment_page.html
  - Segment Name and Segment Description.
  - Dimension: dimensions other than Part and Location "are ONLY used within Inventory Optimization… Service Group Parameters and the SKU Parameters". This allows "different target fill rates by customer/service contract".
  - Only If Install Base Exists.
  - Classification.
- Classification values, which scope where a segment can be used. Source: https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/core/core_pid/pid_segments_page.html
  - All.
  - None.
  - AutoPilot.
  - Security: "available to be assigned to users".
  - Parameter: "available to be assigned to schemes".
  - Copy Demand.
  - Filter.
  - Business Intelligence.
- Other Segments page columns (same URL):
  - Node Name.
  - View/Edit Coverages.
  - Derived Values in Criteria: must be Yes for ABC results to be usable in coverages.
  - Total SKU Count: shown only if the property servigistics.show.segment.sku.count = True.
  - Exclude Replaced Part.
- Segment membership is refreshed by the Update Segmentation AutoPilot process (B5). Pricing fields such as IsASLItem and Current Revenue need Synchronize Database to run before they work on new parts. https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/segment.html

B4. Part classification
- ABC Classification: "categorizing SKUs into different classes based on demand volume, demand value, cost, or custom characteristics". https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/abc_classification.html
  - Bases: Percentage rank, Absolute rank, Tier values, Percent values.
  - Results are stored in the custom Stock Amount table (IPCSCUST_STOCK_AMOUNT) "and are available for segmentation".
  - The example class-set DB columns are ABC_UNITS_PCT_RANK, ABC_UNITS_ABS_RANK, ABC_UNITS_PTC_VALUE and XYZ_COST_TIER_VALUE, which shows that XYZ-style cost classes are just another class set.
- ABC Class Set Classification Types. Source: https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/core/core_pid/pid_new_edit_abc_class_set_page.html
  - Demand: units or hits, from IPCS_DEMAND_HISTORY / IPCS_DEMAND_DETAIL.
  - Demand Value: HistoryAmount × Price.
  - Cost: IPCS_SKU.Price or IPCS_PART_MASTER.Price.
  - Custom: any custom attribute.
  - Forecast Value.
  - Forecast.
- Other ABC Class Set properties (same URL):
  - Units/Volume (Units vs Hits).
  - Part/SKU.
  - SKU Grouping: Sum, Average, Minimum, Maximum, No Grouping.
  - Slice Grouping: Sum, Average, Count, Minimum, and more.
  - Number of Slices.
  - Demand Streams.
- ABC Parameter page fields. Source: https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/core/core_pid/pid_new_edit_abc_parameter_page.html
  - Name, Description, Enabled, Insert Class Set.
  - Promote Ties: Yes promotes all tied SKUs; No promotes only the top Part ID.
  - Tier Type: Percentage Rank, Absolute Rank, Tier Values, Percentage Value.
  - Rules.
  - Worked example: A = 80%, B = 15%, C = remaining 5%.
- ABC Parameters are assigned to segments on the Assign Segments page. Only segments with "Derived Values in Criteria" = No appear there. https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/core/core_smart_help/sh_assign_segments_page.html
- ABC workflow. Source: https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/abc_classification_2.html
  1. Create an ABC Class Set.
  2. "Restart the server" to add the custom columns to IPCSCUST_STOCK_AMOUNT.
  3. Define an ABC Parameter.
  4. Run the Synchronize Database AutoPilot process.
  5. Use the results in segmentation, with Derived Values in Criteria = Yes.
- ABC Code: "The ABC classification code assigned to the SKU". It appears on IPW containers and the Inventory Collaboration SKU Levels container. https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/abc_code.html
- Part Criticality: "A user-defined way of describing the importance of a part, typically used to segment parts of like criticality… codes could be numeric (1–10), alphanumeric (A, B, C, D), or even descriptive titles". Managed on the Part Criticality page (Settings > Data Management > Part). https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/part_criticality.html and https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/core/core_smart_help/sh_part_criticality_page.html
- Criticality Multiplier: "The criticality factor of the SKU that can be used to influence the optimization selection. For the availability model, this also impacts the availability calculation." https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/criticality_multiplier.html
- Location "Critical" flag: see A4.
- Velocity classes: there is no named "velocity class" feature. Velocity is handled with an ABC class set of type Demand (units or hits). Pricing "Part Classes" pages exist but I did not cover them.

B5. AutoPilot
- "AutoPilot is an agent that runs selected processes… The individual AutoPilot tasks can be run collectively or individually at desired frequencies against one or more segments." https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/autopilot.html
- Data flow (same URL):
  1. The gateway pulls host data "(typically on a nightly basis)" into the download transfer tables.
  2. AutoPilot loads the main tables.
  3. AutoPilot processes the data and writes to the upload transfer tables.
  4. The gateway integrates the results back to the host.
- AutoPilot pages: Job, Process Log, Process Status, Run Manual Process, Run Custom Process (Pricing only). https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/core/core_topics/module_processing_autopilot.html
- Status tab: AutoPilot instances are Active, Idle (failover) or Inactive. Filters: Processes, User, What-If, Status, Segment, Job, Report, Task ID. Sections: Current, Scheduled, Completed. https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/core/core_pid/pid_autopilot_page_status_tab.html
- Scheduling on the New/Edit Job page:
  - Fields: Name, Description, Active, Frequency, Frequency Units, Scheduled Run Date, Scheduled Run Time, Pricing Market Group Name.
  - Frequency Units: "Indicates whether the AutoPilot job will run in minutes, daily, weekly, or monthly." "A frequency of '3' for a Weekly type means the AutoPilot job will run once every 3 weeks."
  - Details section buttons: Assign Segments, Assign Processes, Assign Reports, Assign What-If Scenarios, Assign Network Optimization Scenarios.
  - Source: https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/core/core_pid/pid_new_edit_job_page.html
- The Job tab also shows Planner Name, and the counts of Processes and Segments per job. https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/core/core_pid/pid_autopilot_page_job_tab.html
- The Manual tab runs processes "on an as-needed basis", with Segments and Threads selectors. https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/core/core_smart_help/sh_autopilot_page_manual_tab.html
- Documented cadence: the docs do not give a fixed schedule for each process; cadence is configured per job. The only explicit cadence statements are:
  - Host data "is normally processed in Servigistics once per day". Process Groups (groups of locations) enable "more frequent processing of host data without disrupting the daily AutoPilot processing". https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/process_group.html
  - To enable Process Groups: set ENABLE_PROCESS_GROUP_UI and MANUAL_AP_PROCESS_GROUP to true, define groups on the Process Groups page, assign them on Locations, "Run the normal daily AutoPilot processes", then run or schedule Frequent Data Load. https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/process_group_2.html
  - The gateway runs "typically on a nightly basis". https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/autopilot.html
  - Pricing Monthly Financial is monthly by nature (pricing, out of scope). https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/autopilot_processes_6.html
- Process categories: Core, Network Optimization, Lifecycle, Custom, Pricing, Report, Planning, Performance Analytics & Intelligence, Dataset Comparison. "If a process is not displayed… it belongs to a module that is not enabled." https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/autopilot_processes.html

Process lists by category:

Core Processes. Source: https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/autopilot_processes_2.html
- Attachment Storage Synchronizer.
- Circular Reference Finder: uses the CIRCULAR_REFERENCE_RETENTION_DAYS setting.
- Database Maintenance: cannot run by segment.
- Gateway Consistency Check: uses the IPCSDD_FK_CHECK and IPCSDD_BAD_REFERENCE tables.
- Get Host Data: cannot run by segment.
- Review Process: "Refreshes the Review Board".
- Synchronize Database: "Determines the parameters to be assigned to each SKU and calculates stock amounts, taking part chains into account".
- Update Segmentation: "Updates the list of SKUs in a segment".

Network Optimization Processes. Source: https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/autopilot_processes_3.html
- Geo Locate, Location Matcher, Network Optimization.

Lifecycle Processes. Source: https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/autopilot_processes_4.html
- Lifecycle Analytics, Calculate Decay Rate, Last Time Buy Recommendation, Last Time Buy Forecast.

Report Processes. Source: https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/autopilot_processes_7.html
- Run Advanced Reports (Intellicus).

Planning Processes. Source: https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/autopilot_processes_8.html
- ASL Generation: "Calculates, for each location, which parts should be on the Authorized Stocking List"; supports Mid-Slice ASL Adjustment.
- BestFit Forecasting.
- Causal Forecast Detail.
- Causal Forecasting Equipment Loader and Causal Forecasting Equipment Rollup.
- Copy Demand.
- Customer Order Size Calculator.
- Delete Orphan Inventory Optimization Scenarios.
- Demand Aggregation: cannot run by segment.
- Demand Detail Aggregation.
- Demand History Management.
- Disassembly.
- Forecast Netting.
- Forecasting.
- Forecasting-Calculate Metrics: bias metrics.
- Forecasting Database Cleanup.
- Frequent Data Load: stock amounts, sales orders, Order Plan and shipments "frequently throughout the day for SKUs in a process group". Gateway and Synchronize Database cannot start while it runs.
- Generate Order Plan: populates the Planner Worksheet; includes Post Review and Post Auto Approval Review.
- High Margin Analysis.
- Maintenance Forecast Detail.
- Make Forecast Production.
- Inventory Optimization - Run Supercession Changes: moves overrides to the TMR part.
- Merge SKU Overrides: part of Synchronize Database.
- Plan Intelligence.
- Multi-level BOM Synchronize Database.
- Post Forecast: Annual Demand and Forecast Standard Deviation.
- Refresh Planner/Part 360°.
- Scheduled Event Detail.
- Stock Level Generation: "Calculates the optimal levels for each SKU".
- Vendor Group Min Order Quantity (VendorGroupMoqTask).
- Vendor Split (VendorSplitTask).

Performance Analytics & Intelligence Processes. Source: https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/autopilot_processes_9.html
- Analytics Database Maintenance.
- Analytics Purge: uses servigistics.analytics.purge.retain.days and .retain.slices.
- AWS Zeppelin Start and Stop.
- Correlated Parts Intelligence.
- General Analytics Data Loader.
- Forecast Accuracy Intelligence.
- Forecast Analytics Generator.
- Forecast Override Intelligence.
- Machine Learning Forecasting.
- Mean Time Between Failure.
- New Part Introduction Forecasting.
- Planning Analytics Generator.
- Region MTBF.

Dataset Comparison Processes. Source: https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/autopilot_processes_10.html
- Forecast Comparison – Data Backup and Build Report.
- Order Plan Comparison – Data Backup and Build Report.

Inventory Optimization (scenario) job dependencies. Source: https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/autopilot_process_dependencies.html
- Rule: jobs run in parallel unless there is a dependency.
- Jobs listed include:
  - Calculate Visual Analytics.
  - Gather System Info.
  - Delete Orphan Scenarios.
  - Calculate: depends on Database Maintenance, Get Host Data, Synchronize Database, Order Plan Sync Database, Forecasting, Forecast Netting, ASL Generation, and other IO jobs in the same scenario series.
  - Make Production.
  - Clear Optimized Production Values.
  - Delete.
  - Evaluate Exception Criteria.
  - Delete Expired Production Scenarios.
- Other IO jobs named: Apply Overrides, Generate Multi-Period Budget Report, Start Collaboration (A3), Apply Overrides To Production.

B6. KPI definitions (glossary and inv_opt)
- Fill Rate: "The fraction of demand that is met through immediate stock availability, without being backordered. It is calculated based on the Fill Rate Method selected on the scenario." https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/fill_rate.html
- Fill Rate Method options. Source: https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/fill_rate_method.html
  - Fill Rate/Probability In Stock.
  - Fill Rate/Probability In Stock, with Reorder Quantity Benefit.
  - Approximate Fill Rate: 1 – Expected Backorder (ROP+1) / Reorder Quantity ("from a supply perspective").
  - Approximate Fill Rate: 1 – Expected Backorder (ROP+1) / Pipeline Forecast ("from a demand perspective").
- Availability: "The expected percentage of time that equipment is operational." https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/availability.html
- Network Availability: aggregated across a network. It is only available when INVENTORY_OPTIMIZATION_MODE = MIME. https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/network_availability.html
- Location Availability: population-weighted; MIME only. https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/location_availability.html
- EBO (Expected Backorder): "The average units of demands that are waiting to be filled at any point of time in an optimization interval", a function of pipeline forecast, pipeline forecast variance and stock level. https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/ebo.html
- Network Fill Rate: "weighted by both external customer and internal forecasts across network of locations". https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/network_fill_rate.html
- Customer Network Fill Rate: weighted by external customer forecast only. https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/customer_network_fill_rate.html
- Customer Fill Rate: "The average total customer fill rate." https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/customer_fill_rate.html
- Location Wait Time (days): average wait weighted by customer forecast. https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/location_wait_time.html
- Incremental Fill Rate: the change in Fill Rate when the budget increases. https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/incremental_fill_rate.html
- Inventory Turns: "(Daily Demand Rate * 365) / Average Inventory", where Daily Demand Rate = Customer + Resupply Demand. https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/inventory_turns.html
- Days on Hand: "(On Hand New + On Hand Fixed)/ Average Daily Demand Rate". The calculation depends on the GENERATE_OP_SL_OUTSTOCK_DAYS setting. https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/days_on_hand.html
- Service Group Parameters: "A set of service targets and constraints that are applied to SKUs belonging to segments". Targets are Service, Location and Contract Targets. https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/glossary/service_group_parameter.html
- Create/Edit Service Group Parameters page. Source for all: https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/inv_opt/inv_opt_pid/pid_service_group_parameters_create_edit.html
  - Service Metric options: Fill Rate; Availability and Fill Rate (MIME only); Fill Rate with Emergency Backup. "Once the service metric selection is saved, it cannot be changed."
  - Parent Membership options: Direct; Derived - Reporting; Derived - Targets and Constraints.
  - Minimize Stockout Cost, with Stockout Unit Cost (Fill Rate) and Stockout Unit Cost (Wait Time).
  - Service Target fields:
    - Customer Network Fill Rate.
    - Customer Location Fill Rate: "weighted by external demand only".
    - Total Location Fill Rate: "both external and internal demand".
    - Primary Emergency Fill Rate: customer-facing plus first-level emergency.
    - Secondary Emergency Fill Rate.
    - Network Wait Time and Location Wait Time.
    - Network Availability and Location Availability.
    - Contract Wait Time and Contract Availability.
  - Contract Targets: Min Contract Availability and Max Contract Wait Time.
  - Capacity Constraints, for example Cubic Meter.