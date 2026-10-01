PTC SERVIGISTICS 13.x HELP: RESEARCH NOTES (from the local text crawl; read-only, no files written)

About URLs: every source URL starts with https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/ and is shortened to "B/" below. A crawl file is named after its URL path with "/" replaced by "__" and ".txt" added: B/pricing/pricing_topics/rounding_rules.html is pricing__pricing_topics__rounding_rules.html.txt.

Longer versions of two sections are saved as files:
- Release notes 13.0.1.0 to 13.1.0.5, with a 90-row settings table: see appendix PTC-D-Release-Notes-13x.md
- PAI / AI-ML: see appendix PTC-E-PAI-AI-ML.md

Section 4 below condenses the first file. Section 3 is close to the full PAI file. The PAI and release-notes-after-13.0.0.0 facts come from research agents. I read the 13.0.0.0 release notes and the global-settings glossary pages myself.

==========================================================================
GAPS: things the corpus does not contain (read this first)
==========================================================================
- **ServiceMax:** 0 hits in the whole corpus. The only related items are the global setting OP_ENABLE_TRIGGER_NEED_TO_SMAX, which is "SMAX = Stock Maximum" and has nothing to do with ServiceMax, and the 13.0.0.0 "updated" setting of the same name.
- **Consignment / customer-owned inventory:** no concept of either anywhere in core, inv_opt or parts.
- **"Dealer returns" as a named feature:** none. The closest things are the Inventory Studio "Excess Return Recommendations" tab and the Excess Recall order type.
- **Technician van / trunk stock:** no dedicated feature. The only mention is marketing-style text in the Servigistics glossary entry.
- **Pricing terms:** "cost-plus", "competitive" and "value-based" are never used. The equivalents are four Pricing Methodology labels: Margin Plus, Price Plus, Price Alignment and Price Elasticity.
- **"Price gateway" and "price change trigger":** no pages under these names. The closest are the Price Actions gateway import, Demote Action for Price Update Events, and Event Rules.
- **Supersession / interchangeability in pricing:** covered only through part-chain reference points.
- **"Explainability" and "AI":** neither word appears. Explanation is delivered through Feature Importance widgets and the Forecast Accuracy Intelligence (FAI) Profiles.
- **Service Impact Score:** no formula beyond the analytical-object (AO) measure "Sum of Systemimpact".
- **AutoPilot cadence:** no fixed schedule per process. Cadence is configured per Job (minutes / daily / weekly / monthly). Host data is "normally processed … once per day".

==========================================================================
1. PRICING MODULE
==========================================================================
1.1 Overview
- Why service parts pricing differs: "Pricing service parts is very different than pricing other items… if the part is critical to product uptime… more urgency and less opportunity to price shop." Factors are lifecycle stage, pull-through revenue, location/market and competitive substitutes. [B/pricing/pricing_topics/module_pricing.html]
- Menus:
  - Price Simulation: Standard Pricing and Special Pricing. [B/pricing/pricing_topics/module_pricing_price_simulation.html]
  - Price Optimization: Price Alignment, Market Data, Market Data Configuration, Price Feedback Management. [B/pricing/pricing_topics/module_pricing_price_optimization.html]
  - Price Analysis: Analyze and Advanced Analysis. [B/pricing/pricing_topics/module_pricing_advanced_analysis.html]
  - Review. [B/pricing/pricing_topics/module_pricing_review.html]
  - Pricing Part Relationship. [B/pricing/pricing_topics/module_pricing_pricing_part_relationship.html]
  - Manage System. [B/pricing/pricing_topics/module_pricing_manage_system.html]
- Price-active test: only price-active parts are priced. SKU Price Active is checked first. If it is null, part Price Active is used (Yes = active; No or null = not). [B/pricing/pricing_topics/price_active_parts.html]
- Pricing user rights are split across three tabs: Price Optimization, Price Analysis and Price Simulation. There is also a Price Approval Roles tab. Role Name "Pricing" has the database name PricingRole. [B/core/core_smart_help/sh_user_rights_setup_page.html; B/glossary/role_name.html]

1.2 Price streams, price buckets, offsets (price lists)
- Price streams:
  - A SKU can have up to 20 price stream values, representing "price sheet prices (or sales channel prices)".
  - Example: Standard (MSRP) $100, Dealer Net $80, Distributor Net $70.
  - A price stream = price stream value + cost value + demand stream.
  - Market streams hold competitor prices.
  - [B/pricing/pricing_topics/overview_of_price_streams_and_price_stream_values.html]
- Offsets: "each is separated by a set percentage difference, called an offset".
  - Example: Retail $100; Retail Exchange −10% = $90; Wholesale −25% = $75; Wholesale Exchange −40% = $60.
  - The "Price Streams and Offsets" AutoPilot process updates the stream values. [same URL]
- Stream columns:
  - Prices: Standard, Volume, Expedite, Refurbished, Damaged, Custom Price 1–20 (tables IPCS_PRICE / IPCS_PRC_ACTION).
  - Costs: Current, Custom Cost 1–5, Damaged, Expedite, Refurbished (table IPCS_COST).
  - [B/glossary/pricing_reference_points.html]
- Price bucket: the table IPCS_PRICING_BUCKET, where PricingBucketType = p marks price buckets. PRC_OFFSET_REF_PRICE names the reference bucket (default StandardPrice). [B/glossary/global_settings_pricing.html]
- Configurable Margins: 10 margin definitions, each a price field vs a cost field. "The Price and the Cost cannot be set to the same selection." [B/pricing/pricing_smart_help/sh_configurable_margins.html]

Propagation Mode (policy setting) [B/glossary/propagation_mode.html]
- Ripple: "exactly one reference price stream that serves as the anchor". The rule sets the target stream and ripples it to the other streams. With rounding rules, it ripples first and then rounds each stream.
- Independent: sets only the target stream; no ripple.
- Custom Offset: the other streams use the offsets defined in the Configurable Price Offset Code. Shown only when PRC_USE_CUSTOM_OFFSETS = true.

Price Offset Management / Configurable Price Offset Codes (custom offsets)
- "Each SKU is associated with a unique offset code, and each offset code can have multiple offsets with different effective dates." [B/glossary/price_offset_management.html]
- Enabled by ENABLE_CONFIGURABLE_PRICE_OFFSET_CODES (default false). This was renamed from ENABLE_PRC_OFFSET_MANAGEMENT in 13.0.1.0. [B/glossary/global_settings_pricing.html; B/release_notes/release_13_0_1_0/rn_enhancements_pricing_5.html]
- Codes are listed in priority order. The Run button offers:
  - Assign Offset Codes: assigned by segment; a SKU in several codes' segments gets the highest-priority code.
  - Apply Offset Codes: populates prices and splits price records by effective date.
  - Both.
  - [B/pricing/pricing_smart_help/sh_configurable_price_offset_codes.html]
- Detail fields: Effective Date, End Date; Standard / Volume / Expedite / Refurbished / Damaged Price Adjustment %; Custom Price Adjustment 1–20. [B/pricing/pricing_pid/pid_price_offset_code_details.html]
- Each code has a Data Set of Included and Excluded segments. [B/pricing/pricing_topics/price_offset_managment_data_set_assignment.html]
- 13.0.0.0 changes: [B/release_notes/release_13_0_0_0/rn_enhancements_pricing_2.html]
  - A code named "Default" was added. It always has the Default segment, is always sequenced last, and cannot be deleted.
  - Reference Price was added to the page.
  - New settings PRC_APPLY_CUST_PRICE_OFFSETS and USE_SKU_PRICING_BUCKET_CUSTOM_OFFSETS.
  - The Run right was replaced by two rights: "Assign Price Offset Codes" and "Apply Price Offset Codes".
- The "System Defined Price Offsets %" field sits on the Pricing Worksheet, Stream Prices section. [B/glossary/system_defined_price_offsets.html]

1.3 Pricing policies: structure, parameters, precedence
- Build order: Pricing Policy page, then name, Settings, Data Set, price setting rules, rule order, event rules, run. [B/pricing/pricing_topics/overview_of_creating_modifying_pricing_policies.html]
- Settings tab [B/pricing/pricing_smart_help/sh_pricing_policy_page_definition_tab_settings_tab.html]:
  - Process Group: needs ENABLE_PROCESS_GROUP_UI.
  - Policy Folder.
  - Policy Status: must be "Complete for the results in the policy to roll up into the Price Book results".
  - Currency; Propagation Mode.
  - Price Change Reason (needs PRC_PRICE_CHG_REASON); Price Action Comment (needs PRC_PRICE_ACTION_COMMENT).
  - Action lock on Apply Results.
  - Force Elasticity Data Calibration: when a price is not in Data Stage 4, the system "will automatically calibrate elasticity by forcing a price change to test the market".
  - Include parts with no price change (checked by default).
  - Effective Date (a past date is allowed with a warning, added in 13.0.1.0) and Policy Expiration Date (informational only).
  - Detail Step Analysis.
  - Diagnostic Reporting: produces Part Loc Pair Counts, Data Flow, Null Reference Point Exceptions, Multi-Currency Stats and Process Metrics.
  - Prevent Small Price Changes: Minimum Change Amount and Minimum Change %, each for Increase and Decrease. Below the minimum, "the SKU's new recommended price will be set to current standard price". If both are populated, the one with the smaller resolved amount wins.
- Data Set: Part Lists or Included/Excluded Segments. "If you assign both … the segments are ignored." [B/pricing/pricing_topics/changing_pricing_policy_data_set.html]
- Precedence:
  - Across policies: a SKU "is processed within the pricing policy that is listed topmost". Order only matters in folders with Run as AutoPilot = Yes, which is also when the Change Sequence button appears. [B/pricing/pricing_topics/ordering_pricing_policies.html]
  - Within a policy: "the new recommended price resulting from one rule is the beginning price for the next rule." [B/pricing/pricing_topics/overview_of_price_setting_rules_for_pricing_policies.html; B/pricing/pricing_topics/ordering_price_setting_rules_for_pricing_policies.html]
  - Strategy codes: "rules only test parts with the same assigned strategy code". Every rule also has an optional Filters section. [B/pricing/pricing_topics/assignment_rules.html]
  - Part chains and kits: members affect results "whether they are in the included pricing policy or not". [B/pricing/pricing_topics/how_part_chains_and_part_kits_affect_pricing_policies.html]
- Policy Folders: name, description, Run As AutoPilot; User Permissions tab and Data Set tab. [B/pricing/pricing_topics/creating_modifying_policy_folders.html]
- Diagnostic definitions (added 13.1.0.0): Total Input/Output Pairs; New Price = 0, = Current, < Current; fallout categories Outside Folder Coverage, Price Active = No, Undefined Strategy Code, Missing Price Offsets. [B/release_notes/release_13_1_0_0/rn_enhancements_pricing_6.html]

1.4 Price setting rule types (the policy catalogue)
- The list: Assignment, Threshold, Survey Data rules (Market Statistics, Key Competitor), Group Alignment rules (Tier Group, Leader-Follower, Simple Group, Group Step Level, Multi-Attribute Group), Rounding, Price Curve. [B/pricing/pricing_topics/overview_of_price_setting_rules_for_pricing_policies.html]
- Common Adjustment: Final = rule price + (Percent × rule price) + Amount. Example: $9 + 5% + $3 = $12.45. [B/pricing/pricing_topics/adjusting_the_rule_output_price.html] "Adjustments cannot be made when using Direct Pricing reference points." [B/pricing/pricing_topics/assignment_rules.html]
- Assignment rule: fields are Target Pricing Stream, Reference Group/Point, Adjustment, Strategy Codes, Filters. [B/pricing/pricing_topics/assignment_rules.html]
- Threshold rule (floors, ceilings, guardrails): "'guardrails' to keep pricing recommendations within boundaries". Threshold Type = Floor or Ceiling. Example: cap any increase at 25%. [B/pricing/pricing_topics/threshold_rules.html]
- Market Statistics rule (competitive):
  - Fields: Location, Pricing Market, Market Stream, Conditional Test (<, >, =), Statistic Type (Minimum, Average…), Market Relationship Type, Use Extrapolated Data, Adjustment.
  - Example: if price equals the market minimum, "lowered to 97% of the market prices."
  - [B/pricing/pricing_topics/market_statistics_rules.html]
- Key Competitor rule: Location, Pricing Market, Market Stream, Conditional Test, Key Competitor, Adjustment. [B/pricing/pricing_topics/key_competitor_rules.html]
- Rounding rule [B/pricing/pricing_topics/rounding_rules.html]:
  - Rule Type: Price Ending or Nearest Multiple.
  - Direction: Up Only / Up or Down / Down Only.
  - Price Range: Between or Not Between, with Minimum and Maximum. A price outside the range is not rounded.
  - Round To Target: e.g. 0.01, 0.50, 0.99. A value ≥ 1 means "ends in".
  - Directional Up/Down Threshold.
  - "The bottom has highest priority." Best practice is the widest range at the top.
  - Example: 224.7355 with target 0.001 and threshold 0.0004 becomes 224.736.
- Price Curve rule: Baseline Adjustment % and Amount (e.g. $50 + 5% + $10 = $62.50), Lower/Upper Limit, Active. [B/pricing/pricing_topics/price_curve_rules.html; B/pricing/pricing_smart_help/sh_price_curves.html]
- Price banding (group and curve rules) [B/pricing/pricing_topics/price_banding_for_pricing_policy_rules.html]:
  - Upper = Theoretical × (1 + Upper%); Lower = Theoretical × (1 + Lower%).
  - A price inside the band is kept. Above the band it is set to Upper; below, to Lower.
  - If both limits are null, the price is set to the theoretical price.

1.5 Price alignment (groups, chains, kits)
- Leader/Follower [B/pricing/pricing_topics/overview_of_leader_follower_pricing.html; B/pricing/pricing_topics/leader_follower_rules.html]:
  - A part is either a leader or a follower, never both.
  - One L-F rule per policy. Baseline is always the Leader Part Price.
  - Leader Part Output checkbox: whether leader prices also change.
  - Location-Specific Processing off averages the leader prices across locations.
- Simple Group: "All parts … have an equal influence". One rule per policy. Baselines: Weighted Average, Average, Maximum, Minimum, Range. [B/pricing/pricing_topics/overview_of_simple_group_pricing.html]
- Group Step Level: a baseline group plus step groups, e.g. leather priced 10% above cloth. Unlimited rules. Fields: Baseline Level, Baseline Calculation Method, Step Level, Step Offset % and Amount, Lower/Upper Limit. [B/pricing/pricing_topics/group_step_level_rules.html]
- Tier Group (attribute-based) [B/pricing/pricing_topics/overview_of_tier_group_pricing.html; B/pricing/pricing_topics/tier_group_pricing_approximation_methods.html]:
  - Quantitative attributes use a ramp (Linear or Power approximation).
  - Qualitative attributes use steps, e.g. "Remanufactured Parts are priced at a -60% offset from New Parts".
- Multi-Attribute Group (MAG): Attribute-Value-Based Adjustments (anchor part), Attribute Weighting and Price Offsets, or Hybrid. The number of auto-generated adjustments is capped by PRC_MAG_ADJUSTMENTS_AUTOGENERATION_LIMIT. [B/glossary/multi_attribute_group_pricing_strategy.html; B/pricing/pricing_smart_help/sh_multi_attribute_group_page_definition_tab_adjustments_adjustment_settings.html]
- Part chain (supersession) pricing:
  - A part chain is "a series of revised part numbers, each superceding the previous revision". [B/glossary/part_chain.html]
  - Reference points: Part Chain Max Price and Max Markup; Top Most Part Price and Markup; Max Inventory Price; Replaced Part Total / Min / Max / Avg Price and Markup; each also in an "Eff" version. "Markup … = Price / Cost." [B/glossary/pricing_reference_points.html]
  - Pair Dashboard, Price Chain Data Summary tab: helps "manage part burnoff". [B/pricing/pricing_smart_help/sh_pair_dash_pricing_rel_tab_price_cds_tab.html]
- Part kit pricing:
  - Reference points: Part Kit Current Prices, Eff Current Prices, and New Rec Prices (the latter uses component new recommended prices from Price Actions). The kit price is the sum over the kit BOM × quantities. If no component prices are available, the reference point is null. [B/glossary/pricing_reference_points.html]
  - 13.1.0.0: all price buckets can price kits; Review Reason 351 "Component Part Priced Later than Part Kit". [B/release_notes/release_13_1_0_0/rn_enhancements_pricing_3.html]
  - Pair Dashboard, Price Kit Data Summary tab. [B/pricing/pricing_smart_help/sh_pair_dash_pricing_rel_tab_price_kds_tab.html]

1.6 Reference points (cost-based, market and elasticity inputs) [B/glossary/pricing_reference_points.html]
- Groups:
  - Current Costs / Margin / Prices, plus Eff versions.
  - Direct Pricing.
  - Dynamic Targets.
  - Eff Part Chain Relationship.
  - Maintain Current Margin.
  - Max Profit Price.
  - New Margin.
  - Part Group Relationships (Family / Type / Class / Line: Avg Price, Wtd Avg Price, Avg Margin, Wtd Avg Margin, Max Inventory Price).
  - Part Kit Relationships.
  - Price Adjustment Factors.
  - Ref Loc Current / Eff Costs, Margins and Prices; Ref Loc New Rec Margins; Ref Loc New Prices (the approved-for-upload price at the reference location).
- Methodology labels: Price Alignment (the most common), Margin Plus (cost-plus style), Price Plus (dynamic targets and adjustment factors), Price Elasticity (Max Profit).
- Formulas:
  - Margin = (Price − Cost) / Price.
  - New Margin price = X / (1 − Adjustment).
  - Current Margin price = X / (1 − [((Selected Price − X) / Selected Price) + Adjustment]).
  - Maintain Current Margin = [X / (1 − [((Selected Price − Y) / Selected Price) + Adj %])] + Adj Amount.
  - Distance to Max Profit (Local / Consolidated): 0–100% of the way from the current price toward the max-profit price, "or even exceed it (>100%)". The values come from IPCS_PRICE_REFOPT.MPPLocal / MPPCosolidated.
- Location-to-location harmonization: the Reference location supplies prices; the Applied To location receives them. [B/pricing/pricing_topics/overview_of_loc_to_loc_configuration_parameters.html]

1.7 Elasticity and price-volume
- PV curves [B/pricing/pricing_topics/price_volume_curves.html]:
  - Two or more points: linear V(p) = m·p + b, with m negative.
  - Three or more points and PRC_TRY_EXPONENTIAL: V(p) = a·exp(−b·p).
  - Max Profit Price (Local): exponential PmaxGP = c + 1/b; linear PmaxGP = ((c·m) − b) / (2·m).
- Data stages [B/glossary/elasticity_data_stage.html]:
  - Stages 1, 2 and 3 = 1, 2 and 3 valid price points. At stage 3, "max profit can now be roughly calculated". Stages 1–3 are labelled "Insufficient/Unit Data for Elasticity".
  - Stage 4 = 4 points, labelled "Elastic SKU".
  - A mid-month price change counts as the higher price. Zero-demand months do not count. Inelastic parts go to Stage 1. "A part can be elastic and not be in Data Stage 4."
- Elasticity global settings (defaults) [B/glossary/global_settings_pricing.html]:

  | Setting | Default | Meaning |
  |---|---|---|
  | PRC_DATA_STAGE_DAYS | 90 | Days a price must stay constant to advance a stage (3 = 3 months if demand is aggregated monthly) |
  | PRC_DATA_STAGE_MIN_CHANGE | 0.08 | Minimum price change to advance a stage |
  | PRC_MAX_OPT_HIST | 12 | Months of demand/price history used |
  | PRC_MIN_DEMAND_THRESH | 0 | Pairs with average monthly volume below this are set to 0 |
  | PRC_NEW_DEMAND_AVG_WEIGHT | 0.2 | Exponential smoothing weight for the average |
  | PRC_NEW_DEMAND_TREND_WEIGHT | 0.8 | Smoothing weight for the trend |
  | PRC_NEW_MAD_WEIGHT | 0.3 | Weight for MAD |
  | PRC_DEF_FMU | 1 | Default factory markup, used for the consolidated max profit price |
  | PRC_DEF_LCMU | 1 | Fallback when Standard Cost / Supplier Cost is 0 or null |
  | PRC_OPT_GOVERN_PRICE | true | Apply Price Limiters |
  | PRC_OPT_PRICE_LB_PCT / _UB_PCT | 0.05 / 1 | Bounds on the max profit price |
  | PRC_OPT_VOL_LB_PCT / _UB_PCT | 1 / 1 | Bounds on expected volume |
  | PRC_TRY_POWER | true | Fit a power curve; false fits a line (needs more than 2 price points) |

- 13.1.0.0 added Recommended Price (Pricing Worksheet Elasticity tab and Group Price Analysis) and Average Elasticity, and refined the definitions of Group Elasticity Data Stage, Recommended Action and PV Curve Equation. [B/release_notes/release_13_1_0_0/rn_enhancements_pricing_5.html]
- The Home page Elasticity Calibration chart is fed by the Pricing Elasticity AutoPilot process. [B/pricing/pricing_smart_help/sh_home_page_for_pricing.html]

1.8 Market and competitor data
- Market: "a geographic segment where a price for a part behaves similarly and with a similar currency". [B/pricing/pricing_topics/overview_of_markets.html]
- Market Group: groups markets so AutoPilot can run them in parallel. Each market is in one group and needs a currency. [B/pricing/pricing_topics/overview_of_market_groups.html]
- Survey Companies, Survey Sources, Survey Parts ("competitive parts"), and Market Relationship Types (with a configurable order). [B/pricing/pricing_topics/overview_of_survey_companies.html; …overview_of_survey_sources.html; …overview_of_survey_parts.html; …defining_market_relationship_type_order.html]
- Survey expiry: Global Expiration Date = today − PRC_MARKET_SURVEY_AGE_FILTER. [B/glossary/autopilot_processes_6.html]
- The Market Analysis filter has two modes, Key Competitor and Market Statistics. [B/pricing/pricing_topics/market_analysis_filter.html]

1.9 Dealer price feedback: Price Feedback Management (new in 13.1.0.0)
- Enabled by ENABLE_PRC_FEEDBACK_MANAGEMENT (default false). User right "Price Feedback" (View / Modify / Modify 'Use for Market Stats').
- Pages: Price Feedback Types (Default), Price Feedback Status (Open / In Progress / Closed), Price Feedback Resolution Types (Price Increased / Price Decreased / No Change; custom types allowed), and Price Feedback. There is also a Price Feedback tab on the Pricing Worksheet.
- [B/release_notes/release_13_1_0_0/rn_enhancements_pricing_4.html; B/glossary/price_feedback_management_2.html; B/glossary/feedback_resolution_type.html]
- Benefits: "More market data input; Executive view of potential pricing issues; … quicker response time." [B/glossary/price_feedback_management.html]
- Record variants: plain; with Reference SKU; with Competitor. [B/pricing/pricing_smart_help/sh_price_feedback.html]
- Fields [B/pricing/pricing_pid/pid_price_feedback_new_edit.html]:
  - Feedback Number, Description, Feedback Type, Part Number.
  - Suggested Price ("suggested by the dealer").
  - Custom String 1–3 and Custom Numeric 1–3.
  - Customer, Location, Host ID, Owner, Status, Resolution Type, Resolution Notes.
  - Reference SKU variant adds Reference Part and Reference Location.
  - Competitor variant adds Create New Survey Part, Competitor Part Number, Survey Company, Competitor Part Description, Market Relationship Type, Part Number in Catalog, Model.
- 13.1.0.1: segment rights now come from the Pricing Worksheet right; feedback added to Data Manager and Import; Feedback Number added on the Survey Parts pop-up. [B/release_notes/release_13_1_0_1/rn_enhancements_pricing_2.html]
- 13.1.0.2: Home page containers for feedback Type, Status and Resolution Type, with drill-down counts. [B/release_notes/release_13_1_0_2/rn_enhancements_pricing_2.html]

1.10 Event rules: Review and Auto Upload
- Event rules "test the final output price". There are two types. [B/pricing/pricing_topics/overview_of_event_rules_for_pricing_policies.html]
- Review rule [B/pricing/pricing_topics/review_rules.html]:
  - Fields: Target Pricing Stream, Test (<, >, =…), Reference Group/Point, Adjustment, Strategy Codes.
  - Creates Review Board records. They appear in Review Count, the Details grid, the Pricing Worksheet "Price Review Reasons" tab and Price Actions.
- Auto Upload rule [B/pricing/pricing_topics/auto_upload_rules.html]:
  - Qualifying price changes go straight to the Price Book, bypassing Price Actions.
  - "Upload Notify" creates Review Board type 90.
  - "The lower listed rule takes precedence". Rules cannot be reordered; you delete and re-add.
- Pricing exceptions appear on the Review Board Pricing tab. [B/pricing/pricing_topics/pricing_exceptions.html]

1.11 Simulation and apply
- Run (honors Step Analysis), Run Fast (without it), Run Detailed (with it); Run All or Run Selected; Set Price Effective Date. "Simulation results reflect only changes since last price change." [B/pricing/pricing_topics/simulating_a_pricing_policy_autopilot_run.html]
- Apply Results posts to Price Actions and/or the Price Book (per Auto Upload rules). A comment/reason pop-up appears if PRC_PRICE_ACTION_COMMENT / PRC_PRICE_CHG_REASON are set. [B/pricing/pricing_topics/applying_pricing_policy_simulation_results.html]
- Price Step Analysis shows each rule's step. The target stream is green and the reference is blue. [B/pricing/pricing_topics/price_step_analysis.html]
- Locks [B/pricing/pricing_topics/locking_pricing_results.html]:
  - SKU Price Locked = Yes blocks AutoPilot changes.
  - A Price Action lock blocks record updates but still lets the simulation recommend.
- Part List Work Queue: quick re-run for a part list plus locations. [B/pricing/pricing_topics/part_list_work_queue.html]
- Promotions: require PRC_PROMOTIONS. Flow is datasets, then folders, then policies, then simulation and approval. [B/pricing/pricing_topics/promotional_pricing_overview.html] PRC_PROMO_BYPASS_VALIDATION_RULES auto-validates SKUs. [B/pricing/pricing_pid/pid_promotion_policy_list_page.html]
- PRC_POL_ENGINE_LOG_KEEP_DAYS (new in 13.0.0.0, default 0 = never purge; 90 purges records 91 or more days old) sets retention of Pricing Engine output. [B/release_notes/release_13_0_0_0/rn_enhancements_pricing_3.html]

1.12 Price review and approval workflow
- Setup [B/pricing/pricing_topics/overview_of_price_approval.html]:
  1. Ruleset folders.
  2. Pricing business rules.
  3. Price approval roles, assigned to users.
  4. Workflows and their order.
  5. Approve and upload, at aggregate or SKU level.
  - "Up to 20 approval levels." Only records that are locked, not on hold and without blockings move up.
- Roles: each workflow needs at least one role, and the default role cannot be deleted. Approval Limit Rules are assigned per role. [B/pricing/pricing_topics/overview_of_price_approval_roles.html; B/pricing/pricing_smart_help/sh_assign_approval_limit_rules_page.html]
- User fields: "Promotions Revenue Impact Approval Limit Amount" and "Maximum records visible on price actions". [B/core/core_pid/pid_new_edit_user_page.html]
- Workflow General tab [B/pricing/pricing_pid/pid_price_approval_wf_page_general_tab.html]:
  - Name; Required Number of Approval Levels (1–20; changing it resets the workflow).
  - Demote Action for Price Update Events: the "number of price approval levels a SKU will be demoted when the price is updated".
  - Process Group; Included/Excluded Segments. After a coverage change, run Synchronize Database.
- Per-level permissions: View, Add, Edit, Delete, Approve, Reject, Hold, Release, Lock/Unlock, Override, Upload. [B/pricing/pricing_topics/creating_modifying_price_approval_workflows.html]
- Business Rule Sets: Rule Type is "Warning" (notify when the test fails) or "Blocking" (prevent approval). [B/pricing/pricing_pid/pid_price_approval_wf_page_assign_bus_rule_sets_tab.html]
- Skipping rules: only for workflows with 3 or more levels. Fields: Skip From level, Skip To level, and one or more business rules. Example: skip "when absolute margin change is less than or equal to 5%". [B/pricing/pricing_smart_help/sh_price_approval_wf_page_assign_skipping_rules_tab.html; B/glossary/pricing_business_rules.html]
- Business rules use a Criteria Builder with and/or groups. Editing a rule resets the records of the workflows that use it. [B/pricing/pricing_topics/managing_pricing_business_rule_criteria.html]
- Workflow precedence: the "first (top) workflow … to which a SKU is included will be used". The default workflow is always last. [B/pricing/pricing_topics/ordering_price_approval_workflows.html]
- Price Actions page [B/pricing/pricing_topics/price_approval_on_the_aggregate_level.html; …price_approval_on_the_pair_level.html]:
  - Tabs: Multi Level, Single Level, Financial Impact, Action Reports.
  - Actions:
    - Approve: up one level, or to the skip target.
    - Reject: demote to a chosen level.
    - Lock / Unlock: "only locked records can be approved or uploaded".
    - Hold / Release.
  - The Approve window has "Ignore Warnings" and "Ignore Blockings". PRC_APPROVAL_LOCK_AUTOMATIC auto-locks records.
  - Effective date must be today or later; it defaults to today on upload.
- 13.0.1.0 changes:
  - The Reject summary pop-up shows the user, level and reason. [B/release_notes/release_13_0_1_0/rn_enhancements_pricing_4.html]
  - Price Action Comment and Price Change Reason were added to the Price Book and to IPCSDU_PRICE_BOOK, IPCS_PRICE and IPCSDD_PRICE. [B/release_notes/release_13_0_1_0/rn_enhancements_pricing_3.html]
- Price Actions gateway import:
  - PRC_PRICE_ACTION_GATEWAY_APPLY_PRICE_OFFSETS (default false): true applies offsets during import. [B/glossary/global_settings_pricing.html]
  - In 13.1.0.0 it was replaced by PRC_PRICE_ACTION_GATEWAY_PROPAGATION_MODE (1 Ripple / 2 Independent / 3 Custom Offset). The source lists its default as "true", which is inconsistent. [B/release_notes/release_13_1_0_0/rn_enhancements_pricing_2.html]

1.13 Pricing KPIs and screens
- Policy Result tab sections: Financial Impact, Price Change Analysis, Margin vs Cost, Price vs Volume, Market Cone, Market Price Difference, Market Statistics Position, Key Competitor Price Comparison, Review Count, Workflow, Details, Data Flow, and the Diagnostics sections. [B/pricing/pricing_smart_help/sh_pricing_policy_page_result_tab.html]
- Financial Impact [B/pricing/pricing_topics/pricing_policy_page_result_tab_financial_impact_section.html; B/pricing/pricing_topics/understanding_financial_impact.html]:
  - OEM Revenue, Profit and Margin %.
  - Relative view (New vs Effective Current) and Absolute view (New vs Current).
  - "Net Change % = (Projected − Effective Current)/Effective Current × 100%".
- Market Position bands: Maximum; 4th Quartile; 2nd–3rd Quartile; 1st Quartile; < Minimum; No Market Data. Market Cone = competitor Q1–Q3 range. [B/pricing/pricing_topics/pricing_policy_page_result_tab_market_statistics_position_section.html]
- Home page: Market Position, Elasticity Calibration, Strategy Code Mix, Actions Required, Pricing Location Hierarchy, Price Feedback containers. [B/pricing/pricing_smart_help/sh_home_page_for_pricing.html]
- Price Book Projects: target revenue and profit, with color coding white / yellow / green. [B/pricing/pricing_smart_help/sh_price_book_projects_page.html]
- Group Price Analysis: "Create Policy" auto-creates a segment and a policy. PRC_GPA_WTAVGMARGIN_BY_REVENUE switches the weighted-average margin from volume to revenue. [B/pricing/pricing_topics/automatically_creating_segments_and_pricing_policies_from_gpa.html; B/pricing/pricing_pid/pid_group_price_analysis_dashboard_details_tab.html]
- Scoring Analysis (needs ENABLE_SCORING). [B/pricing/pricing_topics/overview_of_scoring_analysis.html]
- Price Transactions: ENABLE_PRC_TRANSACTIONS (default true; added 13.1.0.1). [B/release_notes/release_13_1_0_1/rn_enhancements_pricing_3.html]
- Other pricing settings [B/glossary/global_settings_pricing.html]:
  - DISPLAY_AUTOPILOT_MENU_RUN_CUSTOM_PROCESS (false): Run Custom Process tab.
  - PRC_PROCESS_PRICE_ACTIVE_SKUS (true): the Monthly Financial process uses only price-active SKUs.
  - USE_SKU_PRICING_BUCKET_CUSTOM_OFFSETS (false):
    - true: System Defined Price Offsets % comes from the currently effective offset-code adjustments, as (1 + %).
    - false: it comes from the reference offset of the current stream prices.
  - PRC_APPLY_CUST_PRICE_OFFSETS (false): enables the Apply Price Offset Codes process and the AutoPilot process.
  - PRC_MARGIN_INTEL: Price & Margin Intelligence dashboard. [B/functional/dashboard_price_margin_intelligence_2.html]

==========================================================================
2. DEALER NETWORK, FIELD STOCK, LOCATIONS
==========================================================================
2.1 Dealer role
- "A predefined Role Name." The Role Name options are Customer, Dealer (DealerRole), Planner (ARRole) and Pricing (PricingRole). [B/glossary/dealer.html; B/glossary/role_name.html]
- Rights are auto-assigned and shown on the Dealer tab of User Rights Setup. These rights "are defined at the time of installation and cannot be modified". Action, Admin and Base Setup rights do not apply, and changes on other tabs have no effect. Some rights can be assigned per segment. [B/core/core_smart_help/sh_urs_page_dealer_tab.html] The Dealer tab was added in 13.1.0.0. [B/release_notes/release_13_1_0_0/rn_enhancements_16.html]
- Home page = Inventory Collaboration.
- Restrictions:
  - No Part Properties and no currency fields.
  - Fill Rate Exchange Curve shows units only.
  - Configurable Filter fields are limited to the SKU Levels container fields.
  - Location Summary: no Run button and no scenario comparison.
  - Part selector: no Advanced Find.
  - Segment Summary: no comparison.
  - SKU Overrides: no Import.
  - Scenario and Location selectors show only granted items; Production is always selectable.
  - [B/glossary/dealer.html; B/release_notes/release_13_0_0_0/rn_enhancements_io_8.html]
- DEALER_APP_RESTRICTIONS (new in 13.0.0.0, default false). When true:
  - SKU Override Minimum/Maximum are hidden.
  - Pre-Optimization override fields are unavailable.
  - Configurable filters cannot be shared.
  - [B/release_notes/release_13_0_0_0/rn_enhancements_io_8.html; B/glossary/global_settings_io.html]
- Inventory Collaboration right "Approve" (13.0.0.0): a Dealer can update Production Status on the SKU Levels container. [same; B/glossary/base_setup_rights.html]
- In 13.0.0.0 "Inventory Collaboration" was renamed "Dealer Planning" (the process, which uses the Inventory Collaboration page). [B/release_notes/release_13_0_0_0/rn_enhancements_io_8.html]

2.2 Dealer Planning: setup and workflow
- Definition: "review and collaboration of target stock level information from a single page". [B/glossary/dealer_planning.html]
- Setup [B/glossary/dealer_planning_2.html]:
  1. Users: set Role = Dealer.
  2. Dealer rights:
     - Inventory Collaboration: View + Modify (+ Approve).
     - Location Summary: View.
     - Optimization Set Assignments: View + Modify ("only … administrators").
     - Segment Summary: View.
     - SKU Overrides: View + Modify.
     - User Can Configure Grids.
     - View All Optimization Results: Allowed or Not.
  3. Optional: DEALER_APP_RESTRICTIONS = true.
  4. Override Security role: Allow Recommend = Yes, Allow Review = Yes, Allow Deletion of others' overrides = Yes.
  5. Override Assignment: role + user + segments.
  6. Optimization Set Assignment per dealer user. This populates the "scenario that is in collaboration".
  7. Scenarios page: Run, then "Start Collaboration".
- Workflow [B/glossary/dealer_planning_3.html]:
  1. Analyze SKUs on Inventory Collaboration.
  2. Compare Optimized levels with Min/Max.
  3. Enter Fixed overrides (Fixed EOQ, ROP, Safety Stock, Stock Maximum).
  4. Set Production Status to Approved, or Disapproved together with overrides.
- Inventory Collaboration containers: Constraint and Override Details, Daily Demands, Demand/Forecast Graph, Fill Rate by Stock Level, Fill Rate Exchange Curve, Forecast vs ROP Value, Journal, Part Chain Details, SKU Demand Details, SKU Exception, SKU Levels (default), SKU Overrides, Time Series. [B/inv_opt/inv_opt_smart_help/sh_inventory_collaboration_page.html; …_page_3.html]
- 13.0.0.0 changes:
  - Min/Max ROP, Safety Stock and Stock Max fields added to SKU Levels, pre- and post-optimization.
  - Demand-detail fields added to SKU Demand Details.
  - SKU Exception selections persist through the session.
  - Overrides can be created and deleted on the page.
  - Part Cost removed from SKU Levels.
  - [B/release_notes/release_13_0_0_0/rn_enhancements_io_10.html; …io_13.html; …io_21.html]
- 13.1.0.0: Segment Summary Run options "Approve All Pending SKU" and "Start Collaboration", also schedulable in AutoPilot. "In Collaboration" field on Segment Summary. [B/release_notes/release_13_1_0_0/rn_enhancements_io_18.html; …io_10.html]

2.3 Inventory Studio: dealer, distributor and parts-manager UI (new in 13.0.1.0)
- "A single page for dealers, distributors and customers to manage inventory at one or all of their locations": approve, alter or reject OEM buy/return/transfer recommendations; order parts; locate parts at other locations. [B/release_notes/release_13_0_1_0/rn_enhancements_5.html]
- Menu: Supply Planning > Workflow > Action > Inventory Studio. It is "intended for users that do not require the full capabilities of a parts planner, such as a parts manager at a dealership". [B/parts/parts_smart_help/sh_inventory_studio_page.html]
- Tabs [same URL]:
  - Purchase Recommendations.
  - Excess Return Recommendations.
  - Transfer Recommendations.
  - Stocking Policy Recommendations ("future release").
  - Requests Received and Requests Sent.
  - Order Status.
  - Parts: Part Catalog for non-stocked parts, plus Part Locator.
- Rights [B/core/core_smart_help/sh_urs_page_inventory_studio_tab.html]:
  - Inventory Studio: View, Order Part, Configure, Approve Limit.
  - Recommendation tabs: View, Approve & Reject, Override.
  - Part Locator: View or Request Part.
  - Requests Received: View or Approve & Reject.
  - Requests Sent: View or Delete.
- Later changes:
  - 13.0.1.2: expandable rows. [B/release_notes/release_13_0_1_2/rn_enhancements_5.html]
  - 13.0.1.3: Bing-map Part Locator (pin shows available quantity, distance and an Order button). Needs INVENTORY_STUDIO_MAP_DISPLAY (default true) and servigistics.bingmap.licensekey. [B/release_notes/release_13_0_1_3/rn_enhancements_sp_3.html]
  - 13.0.1.0: Next Generation View enabled on Inventory Studio. [B/release_notes/release_13_0_1_0/rn_enhancements_7.html]

2.4 Location flags and types
- Pricing section of a location: Dealer = Yes marks a dealer location. Dealer = No and Sub Location = No means a regular pricing location. Price Active is also here. [B/core/core_pid/pid_new_edit_location_page.html; B/core/core_pid/pid_loc_prop_page_general_tab.html]
- Planning fields [B/core/core_pid/pid_new_edit_location_page.html]:
  - Critical; Active.
  - Procurement Allowed ("normally … only at central locations"); Repair Allowed.
  - Parent (a central location has Parent = Self).
  - Like Location and Demand Increment Factor.
  - Replenishment Source Location Override.
  - Region.
  - Bin Type: Demand "d" rolls demand up; Forecast "f".
  - Location Type.
  - Network: limits balancing.
  - Process Group.
  - Put Away Length / Std Dev.
  - Fair Share Priority / Reserve.
  - Disconnected Replenishment: orders are seen upstream only once approved.
  - Geo fields; Host Location ID; Enable Alternate Transport Mode.
- Location Types ("central, field, etc."): Fair Share Priority (up to 99, "advisory"), Miles Per Hour, Calendar, Buffer Days for Future Chain Parts. [B/core/core_pid/pid_new_edit_location_types_page.html; B/glossary/location_type.html]
- Echelon = "hierarchy level of the supply chain". [B/glossary/echelon.html]
- Location Hierarchies are replenishment trees per part group, enabled by ENABLE_LOCATION_HIERARCHY (false). [B/glossary/location_hierarchies.html; B/glossary/global_settings_io.html]
- Emergency Backup Location Optimization: uses Service Metric "Fill Rate with Emergency Backup". [B/glossary/emergency_backup_location_optimization.html]
  - 13.0.0.0 added IO_EMERGENCY_NETWORK_SOLVES_COMMON_GROUPS (true = also load groups that share SKUs). [B/release_notes/release_13_0_0_0/rn_enhancements_io_14.html]
  - 13.0.1.0 lets local-repair and NFF sources participate and uses the scenario's fill rate method. [B/release_notes/release_13_0_1_0/rn_enhancements_io_3.html]
- Excess = Stock Level > Stock Maximum × Excess Threshold, plus any non-ASL inventory. [B/glossary/excess.html] Excess Recall is an order type. [B/glossary/excess_recall.html]
- Field stock: Servigistics covers locations "from central locations all the way to the smallest field stock locations such as technician trunks and parts kiosks". [B/glossary/servigistics.html] The time-phased service group target is "the percentage of time that the parts … are available to the technicians". [B/inv_opt/inv_opt_pid/pid_time_phased_service_groups.html]

==========================================================================
3. PERFORMANCE ANALYTICS & INTELLIGENCE (PAI) AND AI/ML
==========================================================================
3.1 Platform
- PAI is "a reporting platform for Data Historicization, Performance Measurement, Root Cause Analysis, and Intelligence for the Service Supply Chain". It is built on Intellicus. [B/glossary_pai/performance_analytics_intelligence.html]
- Tiers:
  - Foundation: low volume, runs on production.
  - Advanced: large volume, exported to a separate server; covers performance, analytics and intelligence.
  - Machine Learning.
  - [same; B/functional/dashboards_section.html]
- Advanced storage [B/functional/how_is_data_stored.html]:
  - Historicized: demand, forecast, inventory, stocking decisions, supply chain data, review reasons.
  - Copied (last value only): segments, planners, base data.
- Analytical Objects are pre-aggregated cubes that must be rebuilt periodically. [B/glossary_pai/analytical_object.html]
- Refresh methods: build the AO, publish the Report, or run the Performance 360 Jobs. [B/admin/admin_update_data_on_dashboards.html]
- The Planning Analytics Generator AutoPilot process loads Order Planning and IO data into the PAI database. [B/glossary/autopilot_processes_9.html]
- ADVANCED_REPORTS (default true) enables Run Advanced Reports and the PAI links in Go to. [B/glossary/global_settings_general.html]
- In 13.0.0.0 the PAI Help Center was embedded under the Analytics menu. [B/release_notes/release_13_0_0_0/rn_new_features_5.html]

3.2 Dashboard catalogue [B/functional/dashboards_section.html]
- Foundation, Service Parts Management (11): Backorder Categorization; Excess Analysis; Forecast Analysis; Forecast Error Analysis; Performance 360; Review Reason Summary; Spend Inventory and Projection; Vendor Detail; Vendor Forecast; Vendor Prioritization and Performance; Vendor Performance Management.
- Foundation, Pricing (8): Financial Bridge Analysis; Global Group Price Analysis; Global Pricing Financial Analysis; Key Competitor Analysis; Market Statistics Analysis; Price Book Analysis; Pricing Policy Duplicate SKUs; Pricing Review Reason Summary.
- Advanced, Service Parts Management (15): Backorder Days; Demand Miss Analysis; Fill Rate Analysis; Forecast Analysis–Adv; Forecast Error Analysis–Adv; Forecast Override Analysis–Adv; Inventory Detail; Location / Part / SKU Forecast Analysis–Adv; Performance 360 Advanced; Planner Workload; Review Reason Trend; Service Group Fill Rate Detail; SKU Supply Chain History.
- Machine Learning, Service Parts Management (14): Correlated Part Details; Correlated Parts Intelligence; Forecasting Time Series Analysis; Forecast Accuracy Intelligence; MTBF Cluster; Multivariate SKU Forecast Analysis; NPI Forecasting (+ Detail); New Part MTBF Prediction; Region MTBF (+ Detail); Remaining Useful Life (+ Detail); SKU Forecast Analysis.
- Machine Learning, Pricing (3): New SKU Margin Intelligence; Price Margin Cluster Details; Price Margin Intelligence ("raise prices, and therefore margins, without reducing revenue"). [B/functional/dashboard_price_margin_intelligence.html]
- Business menus: Performance 360; Forecast Performance; Pricing Intelligence; Service Performance ("fill rates and backorders"); Supply Network Performance; Forecast Intelligence ("Machine Learning-based use cases"). [B/functional/menu_*.html, e.g. B/functional/menu_forecast_intelligence.html]
- Key dashboards:
  - Demand Miss Analysis: "unfulfilled demand (missed quantity) due to the unavailability of stock". Active pairs only; external demand only; day-by-day with no carry-forward; smallest line filled first. [B/functional/dashboard_demand_miss_analysis.html]
  - Fill Rate Analysis: Planned / Actual / Delta Unit and Line FR, Missed, Unplanned Missed. [B/functional/dashboard_fill_rate_analysis.html]
  - Backorder Days: how many days backorders stayed open. [B/functional/dashboard_backorder_days.html]
  - Inventory Detail: Critically Short (OH < SS), In Range, In Excess (OH > Stock Max). [B/functional/dashboard_inventory_detail.html]
  - Vendor Performance Management: on-time, early and late delivery; needs 10 or more closed orders (PO_SPM_VendorMinOrders). [B/functional/dashboard_vendor_perf_mgmt.html]
  - Vendor Prioritization and Performance: vendors ranked "based on a Service Impact score"; widgets include Shortage and Top 5 by Service Impact. [B/functional/dashboard_vendor_prioritization_and_performance.html]
  - Service Impact Score = "Sum of Systemimpact" in the AO. The AO also defines Shortage = Sum of Exceptionqty and Total Spend = Procure + Repair Projection. [B/glossary_pai/AO_SPM_VendorPrioritizationAndProjection.html]

3.3 KPI definitions
- Actual Unit FR (SKU) = Min(Qty Requested, Day's On Hand) / Qty Requested × 100. Day's On Hand = OnhandNew + OnhandFixed − Backorder − Allocated + today's incoming Plan Qty. [B/glossary_pai/actual_unit_fill_rate.html]
- Actual Line FR = Lines Filled / Lines Requested × 100. [B/glossary_pai/actual_line_fill_rate.html]
- Planned FR = the historicized IO Fill Rate from Stocking Policy. [B/glossary_pai/planned_fill_rate.html] Planned Unit FR = Σ(SKU planned FR × qty) / Σ qty. [B/glossary_pai/planned_unit_fill_rate.html]
- Delta Unit / Line FR = Actual − Planned. [B/glossary_pai/delta_unit_fill_rate.html] Aggregation uses a weighted average of SKU fill rates. [B/glossary_pai/fill_rate_aggregation.html]
- Missed = Σ Requested − Σ Filled. It is not calculated for Replaced parts. Example: inventory 7, two lines of 5 gives Missed = 3. [B/glossary_pai/missed.html]
- Unplanned Missed = Delta Unit FR × Total Qty Requested, and 0 if Actual > Planned. Example: planned 97%, actual 95%, so 2% is unplanned. [B/glossary_pai/unplanned_missed.html] Unplanned Line Missed follows the same logic. [B/glossary_pai/unplanned_line_missed.html]
- Bias = Σ Forecast − Σ Demand. [B/glossary_pai/bias.html]
- Forecast Accuracy = 100 − (MAD / Avg Demand) × 100. X = 1 slice (Foundation), or 3, 6 or Lead Time (Advanced). [B/glossary_pai/forecast_accuracy.html]
- Tracking Signal = Σ(D − F) / Σ|D − F|, range −1 to 1. [B/glossary_pai/tracking_signal.html]
- MAPE = Σ|D − F| / Σ((D + F)/2), range 0–2. [B/glossary_pai/mape.html]
- MAD = (Σ|D − F|/N)/X. [B/glossary_pai/mad.html]
- RMSE = √((Σ(D − F)²/N)/X). [B/glossary_pai/rmse.html]
- COV = SD / Avg. [B/glossary_pai/cov.html]
- Days of Excess Supply = Excess / Daily Demand Rate. [B/glossary_pai/days_of_excess_supply.html]

Root-cause categorization (backorder cause / demand-miss cause) [B/glossary_pai/root_cause_categorization.html]

| Priority | Category | Condition |
|---|---|---|
| 1 | Forced Non-Stock | Override forces no stock |
| 2 | No Supply Source | Not procurable, replenishable or repairable |
| 3 | On ASL with On Order | See sub-categories below |
| 3.1 | Vendor Delays | RR 327 "Overdue host order(s) exist" at the procuring location |
| 3.2 | Vendor Delays at Procuring Location | RR 327 upstream |
| 3.3 | Under Forecast | e.g. RR 138 |
| 3.4 | Not Categorized | None of 3.1–3.3 |
| 4 | On ASL without On Order | On Order + In Repair = 0 |
| 5 | System Chose Not to Stock, Forecast Exists | |
| 6 | First Time Demand | |
| 7 | System Chose Not to Stock, No Forecast | |
| 8 | Not Categorized | |

- servigistics.analytics.demandmiss.pastlookupdays = 30. [same URL]
- 13.0.0.0 core change: "On ASL with/without On Order" now uses On Order + In Repair. [B/release_notes/release_13_0_0_0/rn_enhancements_sp_2.html]
- 13.1.0.0 split category 3 in core SP as well. [B/release_notes/release_13_1_0_0/rn_enhancements_sp_5.html]

3.4 AI/ML capabilities
- Data Science Workbench (13.0.0.0) [B/release_notes/release_13_0_0_0/rn_new_features_3.html; B/core/core_smart_help/sh_data_science_workbench.html]:
  - The admin page starts and stops the SFTP and Zeppelin containers and sets credentials (Zeppelin must be restarted to apply them).
  - Needs ADVANCED_REPORTS, FUTURE1 or FUTURE19 = true, plus the "Data Science Workbench Administration" admin right.
  - ML runs in Zeppelin notebooks, with Intellicus ETLs (QO_ETL_PAI_ML_*) passing data in and out. [B/glossary_pai/etl.html]
  - PAI 5.0 allows on-prem ML without the workbench. [B/release_notes_pai/5000/rn_enhancements_13.html]
- AutoPilot processes added for PAI in 13.0.0.0 [B/release_notes/release_13_0_0_0/rn_enhancements_8.html]:
  - AWS Zeppelin Start / Stop ("containers incur hourly charges").
  - Correlated Parts Intelligence.
  - Forecast Accuracy Intelligence.
  - Machine Learning Forecasting: "run on a few exceptionally high error SKUs"; the forecast can be exported and imported back.
  - Mean Time Between Failure (MTBF of new parts).
  - New Part Introduction Forecasting.
- ML time-series forecasting:
  - SARIMA, BATS, Auto ETS, Prophet and XGBoost are trained and validated on past data, and the best is selected. [B/glossary_pai/machine_learning_based_time_series_forecasting.html]
  - PAI 5.0 added XGBoost, with hyper-parameters xgb_n_trees, xgb_depth and xgb_learning_rate. [B/release_notes_pai/5000/rn_enhancements_7.html]
  - PAI 5.0.0.1 flags excessively trending ML forecasts as high-risk and removes them from best-fit selection. [B/release_notes_pai/5001/rn_enhancements_3.html]
- ML Best Fit Integration (core 13.1.0.0) [B/release_notes/release_13_1_0_0/rn_enhancements_fcst_2.html; B/glossary/servigistics_ml_composite_forecast_method.html]:
  - New methods: "Servigistics ML" and "Servigistics ML Composite" (a blend of best statistical and best ML, weighted by Best Fit).
  - Run order: ML Forecasting, then Best Fit, then Forecasting.
  - "Force Servigistics ML Composite" setting.
  - Links to the SKU Forecast Analysis dashboard.
- Multivariate forecasting: demand plus external factors "like weather data and economic factors". The dashboard shows ML vs Servigistics error metrics and Features Detail (feature importance). [B/functional/dashboard_multivariate_sku_forecast_analysis.html; B/release_notes_pai/5000/rn_enhancements_8.html]
- RUL: "Predicts the remaining useful life or expected time until the next failure" of serialized items, from utilization, operational or sensor data. Beta in PAI 5.0.
  - Dashboards: RUL (statistics by Model, range, Feature Importance, Serial Number Distribution, Predicted Failure Date) and RUL Detail.
  - [B/glossary_pai/remaining_useful_life_prediction.html; B/functional/dashboard_remaining_useful_life.html; B/release_notes_pai/5000/rn_enhancements_9.html]
- Forecast Override Intelligence / Recommendations: ML "that advise[s] against potentially detrimental forecast overrides". Beta in PAI 5.0.
  - Parameters: train_split_size 0.75, feature_threshold 0.8, col_missing_value_threshold 0.5, override_recomm_threshold 0.8.
  - Core 13.1.0.2 added the AutoPilot process and the Plan Intelligence message "A forecast override is not recommended" (Stream, Confidence Level).
  - [B/glossary_pai/forecast_override_recommendations.html; B/release_notes/release_13_1_0_2/rn_enhancements_fcst_3.html; B/release_notes_pai/5000/rn_enhancements_10.html]
- Forecast Accuracy Intelligence: predicts tracking signal from attributes and recommends "the combination of attributes that cause SKUs to over forecast or under forecast".
  - Widgets: Data Overview, Feature Importance, Profiles.
  - Parameters: prediction_ts_threshold, sampling (W or MS), slice_date. Slice_date was automated in 5.0.0.1.
  - [B/glossary_pai/forecast_accuracy_intelligence.html; B/functional/dashboard_forecast_accuracy_intelligence.html; B/release_notes_pai/5001/rn_enhancements_4.html]
- Plan Intelligence (IPWS, core 13.1.0.0) [B/glossary/plan_intelligence.html; …_2.html; …_3.html; B/release_notes/release_13_1_0_0/rn_enhancements_sp_3.html]:
  - A flashing toolbar button opens messages in four categories:
    - Balancing Recommendations ("Create balance order from <location>").
    - Forecast Override Recommendations.
    - Unplanned Demand Missed ("Excessive unplanned demand misses"; needs PAI Advanced).
    - Vendor Performance ("Excessive order delay by <vendor>").
  - A Plan Intelligence Map shows excess and shortage locations and can create balance orders.
  - Settings: ENABLE_PLAN_INTELLIGENCE_IPWS (false), PI_VENDOR_PERF_CALCULATE_PERIOD_MONTHS (12), PI_VENDOR_PERF_MIN_ORDERS (10), PI_VENDOR_PERF_RETAIN_SLICES_MONTHS (6), servigistics.analytics.pi.demandmiss.calc.horizonslices (12), servigistics.analytics.pi.demandmiss.retainslices (6).
  - AutoPilot: Plan Intelligence and Planning Analytics Generator.
- MTBF, NPI, correlated parts:
  - Region-Based MTBF: blends regional and global attributes; compared with Servigistics on MAPE, MAD, RMSE and $Bias. [B/glossary_pai/region_based_mtbf_prediction.html]
  - New Part MTBF. [B/glossary_pai/new_part_mtbf_prediction.html]
  - NPI forecasting matches similar parts on numeric and text characteristics, then uses an ensemble. [B/glossary_pai/machine_learning_based_new_parts_forecasting.html]
  - Correlated Parts: items bought together, probable kits, order-level fill rate. [B/glossary_pai/correlated_parts_intelligence.html]
- Explainability is delivered through Feature Importance widgets on Multivariate, RUL, Region MTBF Detail, MTBF Cluster and FAI. [URLs above]
- Causal: core "Causal Forecast" pages cover install-base and failure-rate forecasting, which is not ML. [B/core/core_pid/pid_causal_forecast_scenario_page.html]

3.5 PAI 5.0.0.0 release notes: every enhancement [index B/release_notes_pai/5000/rn_enhancements.html]
1. New dashboards Vendor Forecast (vendor collaboration: capacity, order projection, Service Impact Score) and Vendor Prioritization and Performance. "IO Stockable" renamed "Stockable". [B/release_notes_pai/5000/rn_enhancements_2.html]
2. Demand Miss Analysis: category 3 split into 3.1–3.4; pastlookupdays = 30. Historical data is not recalculated, so old misses show as 3.4. [B/release_notes_pai/5000/rn_enhancements_3.html]
3. Fill Rate Analysis and Service Group FR Detail: "Highest…" widgets renamed "…Summary"; Top 5 service group widgets; filters moved to the top; Service Group filter added; new red Unplanned Missed and Unplanned Line Missed columns; "Demand Missed" renamed "Missed". [B/release_notes_pai/5000/rn_enhancements_4.html]
4. SKU Supply Chain History: "Unmet Demand" renamed "Demand Missed"; Net On Hand Good and Planned Qty added; new Demand Missed and Inventory Projection graph tabs. [B/release_notes_pai/5000/rn_enhancements_5.html]
5. Forecasting dashboards workflow: SKU-level dashboards show the inherited Part/Location filters. [B/release_notes_pai/5000/rn_enhancements_6.html]
6. XGBoost ML time-series algorithm. [B/release_notes_pai/5000/rn_enhancements_7.html]
7. ML-based Multivariate forecasting and its dashboard. [B/release_notes_pai/5000/rn_enhancements_8.html]
8. RUL Prediction (beta), under Analytics > Forecast Intelligence. [B/release_notes_pai/5000/rn_enhancements_9.html]
9. Forecast Override Intelligence (beta). [B/release_notes_pai/5000/rn_enhancements_10.html]
10. Regional MTBF: RMSE-improvement report; MTBF and Failure Rate both shown; Detail widget tabs. [B/release_notes_pai/5000/rn_enhancements_11.html]
11. Service Group FR Detail: separate Demand and Lines tiles; renames. [B/release_notes_pai/5000/rn_enhancements_12.html]
12. Technical [B/release_notes_pai/5000/rn_enhancements_13.html]:
    - On-prem ML without the Data Science Workbench.
    - ML uses the Servigistics system date.
    - Connections renamed: Reportdb is now PAIFoundationDefault; Repositorydb is now RepositoryDB.
    - PAI Advanced on Oracle can use a separate database.
    - Single Report Objects can be published by command.
    - ReportEngine log purge.
    - Obsolete AOs removed.
    - servigistics.analytics.demandmiss.pastlookupdays property.

3.6 PAI 5.0.0.1 release notes [index B/release_notes_pai/5001/rn_enhancements.html]
1. Disable Archiving Tables: servigistics.analytics.archive.tables.mode = STANDARD / CUSTOM (tables listed in IPCS_ANALYTICS_CUSTOM_TABLE_INFO) / ALL (default). [B/release_notes_pai/5001/rn_enhancements_2.html]
2. Eliminate Excessively Trending Forecasts: high-risk ML methods are dropped from best fit. [B/release_notes_pai/5001/rn_enhancements_3.html]
3. Automatic system date for FAI: PO_PAI_ML_FAI_SliceDate removed. [B/release_notes_pai/5001/rn_enhancements_4.html]
4. Help: new RUL topics. [B/release_notes_pai/5001/rn_enhancements_5.html]
- Resolved: PAI-9799, 9944, 9996, 10129. [B/release_notes_pai/new_in_r5001.html]

==========================================================================
4. RELEASE NOTES 13.0.0.0 THROUGH 13.1.0.5
==========================================================================
Series structure:
- 13.0.1.x patches were folded into 13.1.0.0. Many 13.1.0.0 notes repeat them: Network Optimization Rules, Disaggregation Type, Sustainability, Stockout Costs, Order Sizing, Calendar Adjustments, Geo Locate.
- Resolved-issue counts: 13.0.0.0 ≈ 190 case rows; 13.0.1.0 29; 13.0.1.1 11; 13.0.1.2 22; 13.0.1.3 16; 13.0.1.4 4; 13.0.1.5 6; 13.1.0.0 87; 13.1.0.1 17; 13.1.0.2 13; 13.1.0.3 12; 13.1.0.4 18; 13.1.0.5 13.

---- 13.0.0.0 ---- [overview B/release_notes/new_in_13_0_0_0.html]
- New global settings: BESTFIT_RUN_HIST_ANALYTICS, DEALER_APP_RESTRICTIONS, DELETE_DO_NOT_FORECAST, DEPLOYMENT_LOADGAP_LOC_LIMIT, ENABLE_ADVANCED_GRID, ENABLE_PINNING_ALL_LOCATIONS, FCST_RUN_HIST_ANALYTICS, HIST_ANALYTICS_AVG_DMD_INTERVAL_THRESH, HIST_ANALYTICS_COV_SQUARED_THRESH, INTERMITTENCY_TEST_USE_ADI, IO_EMERGENCY_NETWORK_SOLVES_COMMON_GROUPS, IO_PROD_SKU_TRACKING, IO_PRODUCTION_SCENARIO_SKU_SQL_METHOD, OP_TIME_PHASED_ROP_OUTPUT_ZERO_QTY_RECS, OP_OVERDUE_ORDERS_AVAILABLE_TOMORROW, ORACLE_PARALLELISM, PRC_POL_ENGINE_LOG_KEEP_DAYS, USE_SKU_PRICING_BUCKET_CUSTOM_OFFSETS.
- Updated: IO_EVALUATE_EMERGENCY_BACKUP_VALUES, IO_FISCAL_YR_STARTING_MONTH (renamed FISCAL_YR_STARTING_MONTH), OP_ENABLE_TRIGGER_NEED_TO_SMAX, OP_IGNORE_ORDER_DATE_IN_TRIGGERPT, RESTRICT_MANUAL_ORDER_CREATION.

Common: new features
- Comparative Analytics of Modeling Instances: compare two SPM instances, e.g. base vs modeling, for what-ifs, tuning and upgrade previews.
  - New AutoPilot "Dataset Comparison Processes": Forecast Comparison – Data Backup / Build Report; Order Plan Comparison – Data Backup / Build Report.
  - Pages: Forecast Comparison Summary and Detail (Forecast, Forecast Value, BIAS); Order Plan Comparison Summary and Detail (units and value by order type).
  - [B/release_notes/release_13_0_0_0/rn_new_features_2.html]
- Data Science Workbench Administration page (see 3.4). [B/release_notes/release_13_0_0_0/rn_new_features_3.html]
- Location description on the Location select button: user preference, length 1–1000, 50 recommended. [B/release_notes/release_13_0_0_0/rn_new_features_4.html]
- PAI Help Center embedded under Analytics. [B/release_notes/release_13_0_0_0/rn_new_features_5.html]
- New page display (beta "advanced grid", later called Next Generation View) on Location Summary and the IPWS Deployments container: column resize, pin, filter, group collapse. Controlled by ENABLE_ADVANCED_GRID (default true). [B/release_notes/release_13_0_0_0/rn_new_features_6.html]

Common: usability
- Audit Trail process list sorted alphanumerically. [B/release_notes/release_13_0_0_0/rn_usability_improvements_2.html]
- Enhanced User Rights Setup page with module tabs: Forecasting, Inventory Optimization, Price Optimization, Price Analysis, Price Simulation, Supply Planning, Processing, Analytics, Settings. Unchanged tabs: OTF Rights, Review Subscriptions, Column Security, Import, Products, Custom Tables, Segment Folders. The classic page is still available. [B/release_notes/release_13_0_0_0/rn_usability_improvements_3.html]
- Text filter on the Configure page's Available Columns. [B/release_notes/release_13_0_0_0/rn_usability_improvements_4.html]
- Page help gains "View Access Settings", which lists the rights and settings that control each page (phased rollout). [B/release_notes/release_13_0_0_0/rn_usability_improvements_5.html]
- Copy Configurations on the Users page now includes Layout-Manager pages (IPWS Plan/Forecast, Inventory Collaboration, Location Summary, Visual Analytics, Part Summary, Planner 360°, Scenario Summary, Scenarios, Segment Summary, Service Group Results, Stocking Policy). [B/release_notes/release_13_0_0_0/rn_usability_improvements_6.html]

Common: enhancements [index B/release_notes/release_13_0_0_0/rn_enhancements.html]
- Additional Review Types on a Review Parameter: a new Add Review Reason to Parameter page. [B/release_notes/release_13_0_0_0/rn_enhancements_2.html]
- Fiscal year view on the IPWS Time Series Grid: Calendar Year / Fiscal Year selector driven by FISCAL_YR_STARTING_MONTH (e.g. 2 gives Q1 Feb–Apr). Not available on weekly systems. [B/release_notes/release_13_0_0_0/rn_enhancements_3.html]
- History Based Simulator [B/release_notes/release_13_0_0_0/rn_enhancements_4.html]:
  - Forecast tables are no longer wiped at start.
  - No initial orders for non-ASL SKUs or SKUs with Stock Max = 0.
  - New "Enable Inventory Reconciliation" parameter.
  - New Fill Rate by Part page.
  - Order Plan Synchronize DB added as a selectable process.
- ABC Class Sets: "Include zero demand slices" checkbox (when Slice Grouping = Count). [B/release_notes/release_13_0_0_0/rn_enhancements_5.html]
- Journal entries can be part-level (blank Location) or SKU-level, on six pages. [B/release_notes/release_13_0_0_0/rn_enhancements_6.html]
- New Audit Trail processes: Replenishment/Balance SKU Lead Time; Replenishment/Balancing SKU; Replenishment Lead Times; Vendor Location SKU Lead Time (tracks Procurement LT, Procurement MOQ, Repair LT on the IPWS Order/SKU Parameters). Go To includes Audit Trail. [B/release_notes/release_13_0_0_0/rn_enhancements_7.html]
- New AutoPilot processes for PAI (see 3.4). [B/release_notes/release_13_0_0_0/rn_enhancements_8.html]
- ESCM property servigistics.escm.dbparalleldegree: parallel workers for Create Snapshot Export / Create Modeling Instance Import. Set to cores − 2 on Oracle; 1 on MSSQL. [B/release_notes/release_13_0_0_0/rn_enhancements_9.html]
- Part autocomplete properties [B/release_notes/release_13_0_0_0/rn_enhancements_10.html]:
  - servigistics.part.autocomplete.min.chars.
  - servigistics.part.autocomplete.on.partnumber: true searches Part Number only; false also searches Part Name 1–5.
  - servigistics.part.autocomplete.compare.lower: needs a lower(PartNumber) index on case-sensitive databases.
- runICP scripts can now publish Intellicus reports as well as build AOs. [B/release_notes/release_13_0_0_0/rn_enhancements_11.html]
- Set Default Layout: a new right, plus Layout menu options "Set Default Layout" and "Restore Original Default Layout" on Layout-Manager pages. New Planner 360° user right. [B/release_notes/release_13_0_0_0/rn_enhancements_12.html]
- The order-plan.ws export filter supports custom attributes. [B/release_notes/release_13_0_0_0/rn_enhancements_13.html]
- AutoPilot job names prefixed "Inventory Optimization - " (Exception Criteria; Apply SKU Overrides Locally To Production). [B/release_notes/release_13_0_0_0/rn_enhancements_14.html]

Forecasting [index B/release_notes/release_13_0_0_0/rn_enhancements_fcst.html]
- Clear Future Forecast: DELETE_DO_NOT_FORECAST (false). True deletes future forecast records when the method is Do Not Forecast (in the Forecasting AutoPilot or Interactive Plan). [B/release_notes/release_13_0_0_0/rn_enhancements_fcst_2.html]
- Demand Categorization [B/release_notes/release_13_0_0_0/rn_enhancements_fcst_3.html]:
  - Categories: Smooth (ADI < 1.32 and CoV² < 0.49), Erratic (ADI < 1.32 and CoV² ≥ 0.49), Intermittent (ADI ≥ 1.32).
    - ADI = total slices / non-zero slices.
    - CoV = SD / Mean.
  - Applied at SKU and SKU-Stream levels. Thresholds come from Forecast Parameters (stream level) or the global settings HIST_ANALYTICS_AVG_DMD_INTERVAL_THRESH (1.32) and HIST_ANALYTICS_COV_SQUARED_THRESH (0.49) (SKU level).
  - INTERMITTENCY_TEST_USE_ADI (true new / false upgrade): Best Fit uses the categorization intermittency check.
  - FCST_RUN_HIST_ANALYTICS and BESTFIT_RUN_HIST_ANALYTICS (false new / true upgrade): run Demand History Management inside the Forecasting / Best Fit AutoPilot.
  - Synchronize Database and Update Segmentation refresh the segment membership.
  - New Segment Coverage "Forecasting Fields": Avg Historical Forecast, Bias, Bias Value, Demand Category, History Avg / COV / SD, Periods Between Demand, Slices of Non-Zero Demand, Slices Since First Non-Zero Demand.
  - Demand Category added to Forecast Review and the IPWS Forecast Metrics.
- Stream Configuration Details: "Used in Replacement Rate Forecasting" field. [B/release_notes/release_13_0_0_0/rn_enhancements_fcst_4.html]
- Work Queue Magnitude and Magnitude Value populated for review types 1–3 ("Actual vs Forecast outside of calculated Demand Standard Deviation 1/2/3"). [B/release_notes/release_13_0_0_0/rn_enhancements_fcst_5.html]
- "Run Post Forecast Process": listed in the index but the page body is empty in the crawl. Related setting RUN_POST_FORECAST (true) includes Post Forecast in the Forecasting process and page Run buttons. [B/release_notes/release_13_0_0_0/rn_enhancements_fcst_6.html; B/glossary/global_settings_fcst.html]

Inventory Optimization [index B/release_notes/release_13_0_0_0/rn_enhancements_io.html]
- SKU Summary and Part Supply Chain gain Additional Data containers: Part Chain Details, Service Group, SKU Overrides. [B/release_notes/release_13_0_0_0/rn_enhancements_io_2.html]
- Apply Overrides To Production logs a warning when the parent SKU is missing or the echelon is wrong, and sets backorders from above to 0. [B/release_notes/release_13_0_0_0/rn_enhancements_io_3.html]
- Audit Trail for IO transactions: Exception Criteria, Optimization Sets, Service Group Parameters, SKU Overrides, Time Phased Service Groups. Audit Purge is recommended. [B/release_notes/release_13_0_0_0/rn_enhancements_io_4.html]
- Time Phased Service Group Begin Period now uses a calendar picker. [B/release_notes/release_13_0_0_0/rn_enhancements_io_5.html]
- Category filter on Scenario Summary. [B/release_notes/release_13_0_0_0/rn_enhancements_io_6.html]
- Customer Order Size: replenishment locations compute COS mean and SD weighted by own and child forecasts. [B/release_notes/release_13_0_0_0/rn_enhancements_io_7.html]
- Dealer Role enhancements (see 2.1). [B/release_notes/release_13_0_0_0/rn_enhancements_io_8.html]
- Default Override Reason flag on Override Reasons; it pre-fills Reason (general) on new SKU Overrides. [B/release_notes/release_13_0_0_0/rn_enhancements_io_9.html]
- Fields added:
  - Stocking Policy attributes: Part Critical, Part Family, Part Type.
  - Location Custom 3–10.
  - No Fault Found Rate.
  - Host SKU Override ID and Network Region.
  - Demand detail fields.
  - Min/Max ROP, SS and Stock Max on Inventory Collaboration.
  - [B/release_notes/release_13_0_0_0/rn_enhancements_io_10.html]
- Exports include group headers, e.g. "Fixed Fill Rate (Pre-Optimization)". [B/release_notes/release_13_0_0_0/rn_enhancements_io_11.html]
- Stocking Policy links to Service Group Budget Summary and Results. [B/release_notes/release_13_0_0_0/rn_enhancements_io_12.html]
- Inventory Collaboration improvements (see 2.2). [B/release_notes/release_13_0_0_0/rn_enhancements_io_13.html]
- IO_EMERGENCY_NETWORK_SOLVES_COMMON_GROUPS (true). [B/release_notes/release_13_0_0_0/rn_enhancements_io_14.html]
- Label changes [B/release_notes/release_13_0_0_0/rn_enhancements_io_15.html]:
  - Held SKUs became Rejected SKU.
  - MEO Approve Holds became MEO Approve All Pending SKU.
  - Location / Part / Scenario / Service Group Hold became MEO Approve/Reject SKU by Location / Part / Scenario / Service Group.
- Minimize Stockout Cost [B/release_notes/release_13_0_0_0/rn_enhancements_io_16.html]:
  - Service Group flag.
  - Stockout Unit Cost for Fill Rate and for Wait Time (plus Reference and Currency fields), resolved SKU, then Part, then IO Planning Parameter, then Service Group default (1).
  - Stockout Cost (FR) = (1 − FR) × Interval Customer Forecast × unit cost.
  - Stockout Cost (Wait Time) = (Expected Backorder / Total Daily Forecast) × Interval Customer Forecast × unit cost.
- No Fault Found for Consumables now applies in IO. [B/release_notes/release_13_0_0_0/rn_enhancements_io_17.html]
- Help global-setting references fixed on the COV and VMR Cap pages. [B/release_notes/release_13_0_0_0/rn_enhancements_io_18.html]
- Import of Optimization Set Assignments: gateway IPCSDD_MEO_PLANNER_OPTSET. [B/release_notes/release_13_0_0_0/rn_enhancements_io_19.html]
- IPCS_OVR_USER_LOCATIONS table speeds security and segment checks. [B/release_notes/release_13_0_0_0/rn_enhancements_io_20.html]
- Part Cost removed from SKU Levels. [B/release_notes/release_13_0_0_0/rn_enhancements_io_21.html]
- ASL Generation and Stock Level Generation OTF rights off by default on new installs. [B/release_notes/release_13_0_0_0/rn_enhancements_io_22.html]

IO performance [index B/release_notes/release_13_0_0_0/rn_inv_opt_calc_improvements.html]
- servigistics.meo.max.concurrent.index.creation: 10 concurrent index builds by default. [B/release_notes/release_13_0_0_0/rn_inv_opt_calc_improvements_2.html]
- Exception Criteria results go to a per-scenario table EC<scenarioId>. [B/release_notes/release_13_0_0_0/rn_inv_opt_calc_improvements_3.html]
- Concurrency and loading changes [B/release_notes/release_13_0_0_0/rn_inv_opt_calc_improvements_4.html]:
  - Inputs and results loaded concurrently per servigistics.meo.max.concurrent.parts.
  - Membership derivation runs once per scenario.
  - Concurrent model queries; revert with servigistics.submit.part.model.queries.sequentially = true.
  - Forecasts staged in a temp table.
  - Make Production can rebuild ipcs_order_plan_netfcst_sl with servigistics.io.make.production.create.table.update = true.
- IO_EVALUATE_EMERGENCY_BACKUP_VALUES default changed to false (recommended). [B/release_notes/release_13_0_0_0/rn_inv_opt_calc_improvements_5.html]
- IO_PROD_SKU_TRACKING [B/release_notes/release_13_0_0_0/rn_inv_opt_calc_improvements_6.html]:
  - 0: no IPCS_MEO_PROD_SKU rows.
  - 1: current period only (recommended for large configurations).
  - 2: all periods (the glossary default).
- IO_PRODUCTION_SCENARIO_SKU_SQL_METHOD: 1 = create then append (default); 2 = union. [same URL]
- The Synchronize Database client argument "-param buildLocNode true|false" overrides servigistics.meo.update.locnode (false). [B/release_notes/release_13_0_0_0/rn_inv_opt_calc_improvements_7.html]

Supply Planning [index B/release_notes/release_13_0_0_0/rn_enhancements_sp.html]
- Backorder categorization now counts In Repair (see 3.3). [B/release_notes/release_13_0_0_0/rn_enhancements_sp_2.html]
- Enable Receiving Balancing values: No / Balance only for own need (the former "Yes") / Balance also for downstream need (the new-install default, recommended). [B/release_notes/release_13_0_0_0/rn_enhancements_sp_3.html]
- Host Part Chain ID on Part Chains. [B/release_notes/release_13_0_0_0/rn_enhancements_sp_4.html]
- IPWS improvements [B/release_notes/release_13_0_0_0/rn_enhancements_sp_5.html]:
  - Right-click and left-click on the Orders container.
  - Multi-select order types.
  - Pin All locations (ENABLE_PINNING_ALL_LOCATIONS, false).
  - Change the destination location.
  - Excess and Critical Shortage show today's values only.
  - Column security on 9 containers.
  - Go To adds Forecast Review and Part Health.
  - Custom attributes editable on Order/SKU Parameters.
- Last Time Buy Profile Assignment [B/release_notes/release_13_0_0_0/rn_enhancements_sp_6.html]:
  - Profiling Segments and new Forecasting Segments tabs auto-assign profiles.
  - Page renamed from Last Time Buy Profile Select.
  - New Manually Assigned and Segment Assigned fields.
- Help: "Balancing" glossary rework; Deployments help. [B/release_notes/release_13_0_0_0/rn_enhancements_sp_7.html]
- Alerts To = All. [B/release_notes/release_13_0_0_0/rn_enhancements_sp_8.html]
- Planner Home Page renamed Planner 360° (tabs Planner 360° and Part 360°). [B/release_notes/release_13_0_0_0/rn_enhancements_sp_9.html]
- New Part Health tab: Current Details, Graph (inventory vs orders vs ROP), Summary. [B/release_notes/release_13_0_0_0/rn_enhancements_sp_10.html] Populated when OP_GENERATE_ORDER_PLAN_PART_HEALTH_DATA = true. [B/glossary/global_settings_sp.html]
- RESTRICT_MANUAL_ORDER_CREATION also locks the Location on IPWS orders. [B/release_notes/release_13_0_0_0/rn_enhancements_sp_11.html]
- OP_OVERDUE_ORDERS_AVAILABLE_TOMORROW (true new / false upgrade): overdue orders with Effective Available Date = today move to tomorrow. [B/release_notes/release_13_0_0_0/rn_enhancements_sp_12.html]
- Time-Phased ROP [B/release_notes/release_13_0_0_0/rn_enhancements_sp_13.html]:
  - OP_TIME_PHASED_ROP_OUTPUT_ZERO_QTY_RECS (true).
  - Replenishment and Chain Deficit shown over the horizon.
  - "Material Flow" renamed "Inventory Reconciliation".
  - Daily Detail IP date ranges: None / 7 / 30 (default) / 60 / 90 / 365 / Custom.
  - New-install defaults: OP_ENABLE_TRIGGER_NEED_TO_SMAX = true (lets Trigger and TP-ROP preorder for large EOQ); OP_IGNORE_ORDER_DATE_IN_TRIGGERPT = false.
  - Fill Rate added to IP Summary.
  - Balancing "Primary Source First" fix.
  - EOQ-then-sizing ordering. Example: ROP 10, Smax 18, EOQ 8, IP 9, lot 8 now orders 8 (previously 16).
  - New fields Perform Substitution / Upchain Excess Transfer (Before or After Balancing and Excess Recall), gated by OP_TIME_PHASED_ROP_ENABLE.
- Host orders outside the calendar are placed at the calendar end. OP_ADD_DAYS_TO_LT_TO_CALC_TRIGGER_INVENTORY_POSITION = −1 counts them as on order. [B/release_notes/release_13_0_0_0/rn_enhancements_sp_14.html]
- Generate Order Plan multi-thread writes table updates in 4 staggered orders. [B/release_notes/release_13_0_0_0/rn_enhancements_sp_15.html]
- Transport Cost visibility with waterfall: Replenishment/Balancing SKU LT, then LT; Vendor Location SKU LT, then Vendor Location Parts, then Vendor Location LT.
  - Total Procurement Cost = (Part Cost × Qty) + Order Cost + Transport Cost.
  - Total Repair Cost likewise with Repair Cost and Repair Order Cost.
  - [B/release_notes/release_13_0_0_0/rn_enhancements_sp_16.html]
- SP performance:
  - Order Plan global-setting evaluation is back to 12.2.1.0 speed. [B/release_notes/release_13_0_0_0/rn_peformance_improvements_sp_2.html]
  - A TP-SS non-ASL source case dropped from hours to minutes. […sp_3.html]
  - DEPLOYMENT_LOADGAP_LOC_LIMIT (500) for the Deployments tab. […sp_4.html]

Pricing (13.0.0.0)
- Price Offset Management enhancements. [B/release_notes/release_13_0_0_0/rn_enhancements_pricing_2.html]
- PRC_POL_ENGINE_LOG_KEEP_DAYS. [B/release_notes/release_13_0_0_0/rn_enhancements_pricing_3.html]

Resolved issue: ORACLE_PARALLELISM controls parallel hints: DEFAULT (recommended) / AUTO / an integer ≥ 1. [B/release_notes/release_13_0_0_0/resolved_issues_13_0_0_0.html]

---- 13.0.1.0 ---- [B/release_notes/new_in_13_0_1_0.html]
Common
- Refresh Planner/Part 360° documentation. [B/release_notes/release_13_0_1_0/rn_enhancements_2.html]
- Geo Locate accepts inexact matches. [B/release_notes/release_13_0_1_0/rn_enhancements_3.html]
- Data Manager: new entities Causal Type and Disaggregation Weight Overrides; Export All Rows (MAX_EXPORT_ROWS); custom attribute labels in export headers. [B/release_notes/release_13_0_1_0/rn_enhancements_4.html]
- Inventory Studio (new). [B/release_notes/release_13_0_1_0/rn_enhancements_5.html]
- ENABLE_EXPORT_NUMBER_FORMAT. [B/release_notes/release_13_0_1_0/rn_enhancements_6.html]
- Next Generation View on Deployments, Inventory Studio, Location Summary, What-If. [B/release_notes/release_13_0_1_0/rn_enhancements_7.html]
- Review subscription default priority reordered (325, 332, 320; 345 removed). [B/release_notes/release_13_0_1_0/rn_enhancements_8.html]

Forecasting
- Best Fit allows negative Trend % for Same As Last Year. [B/release_notes/release_13_0_1_0/rn_enhancements_fcst_2.html]
- Life Limited Parts Maintenance Forecasting [B/release_notes/release_13_0_1_0/rn_enhancements_fcst_3.html]:
  - Serial-level forecasting from flight hours/cycles and life limits.
  - Methods LLP Maintenance – Raw and LLP Maintenance – Smooth (capacity-smoothed).
  - AutoPilot process Maintenance Forecast Detail; LLP Forecast Details page.
- Servigistics TSB (Teunter-Syntetos-Babai) intermittent method: "Select Forecast Method for Intermittent Demand", TSB Alpha/Beta, Allow Servigistics TSB. [B/release_notes/release_13_0_1_0/rn_enhancements_fcst_4.html]
- Replacement Rate Details row links. [B/release_notes/release_13_0_1_0/rn_enhancements_fcst_5.html]
- Forecast Review count query falls back to MAX_ROW_ERROR_LIMIT after 10 s. [B/release_notes/release_13_0_1_0/rn_performance_fcst_2.html]

Inventory Optimization
- Demand Weighted Composite Lead Time: MEO_REPAIR_TYPE = 3 (1 Serial, 2 Aggregate). [B/release_notes/release_13_0_1_0/rn_enhancements_io_2.html]
- Emergency Backup changes. [B/release_notes/release_13_0_1_0/rn_enhancements_io_3.html]
- Pass Up Rate and Condemnation Rate removed. [B/release_notes/release_13_0_1_0/rn_enhancements_io_4.html]
- Prioritized Buy List: network exchange-curve steps (mandatory, then minimums/overrides, then discretionary); new right, scenario checkbox and page. [B/release_notes/release_13_0_1_0/rn_enhancements_io_5.html]
- Scenario window reorganized. [B/release_notes/release_13_0_1_0/rn_enhancements_io_6.html]
- What-If Modeling (beta): What-If Model page and right; fields What-If SKU and Modified by What-If. [B/release_notes/release_13_0_1_0/rn_enhancements_io_7.html]

Pricing
- "Rule Sets Folder" naming. [B/release_notes/release_13_0_1_0/rn_enhancements_pricing_2.html]
- Comment and Reason fields in the Price Book. [B/release_notes/release_13_0_1_0/rn_enhancements_pricing_3.html]
- Reject summary details. [B/release_notes/release_13_0_1_0/rn_enhancements_pricing_4.html]
- Offset Management renamed Configurable Price Offset Codes; AutoPilot process renamed Apply Configurable Price Offsets. [B/release_notes/release_13_0_1_0/rn_enhancements_pricing_5.html]
- Part Lists tab on the Pricing Worksheet. [B/release_notes/release_13_0_1_0/rn_enhancements_pricing_6.html]
- Policy Name in Stream Prices. [B/release_notes/release_13_0_1_0/rn_enhancements_pricing_7.html]
- Warning for a past Effective Date. [B/release_notes/release_13_0_1_0/rn_enhancements_pricing_8.html]

Supply Planning
- Nine Order Plan Comparison Detail pages (By Part / For Part / By SKU × Full Horizon / Today / 13 Week). [B/release_notes/release_13_0_1_0/rn_enhancements_sp_2.html]
- Balancing uses the order date for excess. [B/release_notes/release_13_0_1_0/rn_enhancements_sp_3.html]
- ENABLE_PINNING_ALL_LOCATIONS renamed ENABLE_LOCATION_PINNING. [B/release_notes/release_13_0_1_0/rn_enhancements_sp_4.html]
- Fair Share sort defaults q / f. [B/release_notes/release_13_0_1_0/rn_enhancements_sp_5.html]
- PromisedShipDate import. [B/release_notes/release_13_0_1_0/rn_enhancements_sp_6.html]
- IPWS: Part 360° and Part Health tabs; PAI links. [B/release_notes/release_13_0_1_0/rn_enhancements_sp_7.html]
- Trigger Point order sizing. [B/release_notes/release_13_0_1_0/rn_enhancements_sp_8.html]
- Outside-horizon shading. [B/release_notes/release_13_0_1_0/rn_enhancements_sp_9.html]
- Trigger Point uses Stock Max as the excess limit. [B/release_notes/release_13_0_1_0/rn_enhancements_sp_10.html]
- TP-ROP improvements [B/release_notes/release_13_0_1_0/rn_enhancements_sp_11.html]:
  - Repair ROP in balancing.
  - OP_TIME_PHASED_ROP_USES_TIME_PHASED_ROP_FAIRSHARE (true).
  - "Output Generated Orders" option.
  - SCS for TP-ROP.
  - Unadjusted SS and SCS rows.

---- 13.0.1.1 ---- [B/release_notes/new_in_13_0_1_1.html]
- Demand History Management job in OTF rights. [B/release_notes/release_13_0_1_1/rn_enhancements_2.html]
- Simulator starts at On Hand Good = Smax. [B/release_notes/release_13_0_1_1/rn_enhancements_3.html]
- Network Optimization Rules page (overrides install-base coverage). [B/release_notes/release_13_0_1_1/rn_enhancements_io_2.html]
- Global LTB Quantity. [B/release_notes/release_13_0_1_1/rn_enhancements_sp_2.html]
- Comparison-page hyperlinks. [B/release_notes/release_13_0_1_1/rn_enhancements_sp_3.html]
- Order Spreading for TP-SS and TP-ROP, with an "Order Spreading Need" row. [B/release_notes/release_13_0_1_1/rn_enhancements_sp_4.html]

---- 13.0.1.2 ---- [B/release_notes/new_in_13_0_1_2.html]
- Configurable Go To Menu (needs ADVANCED_REPORTS and FUTURE36). [B/release_notes/release_13_0_1_2/rn_enhancements_2.html]
- "Review Reason" naming. [B/release_notes/release_13_0_1_2/rn_enhancements_3.html]
- Sample workflows. [B/release_notes/release_13_0_1_2/rn_enhancements_4.html]
- Inventory Studio expandable rows. [B/release_notes/release_13_0_1_2/rn_enhancements_5.html]
- Disaggregation Type Even / Proportional. [B/release_notes/release_13_0_1_2/rn_enhancements_fcst_2.html]
- Average Inventory renamed Expected On Hand. [B/release_notes/release_13_0_1_2/rn_enhancements_io_2.html]
- Network Optimization Hours to Cross (country borders). [B/release_notes/release_13_0_1_2/rn_enhancements_io_3.html]
- "Full" approve option (ALLOW_MASS_APPROVAL_TO_CO_ORDERS, MAX_ROWS_FOR_FULL_OPERATION, RS_MAX_PAGES). [B/release_notes/release_13_0_1_2/rn_enhancements_sp_2.html]
- LTB approve/disapprove behavior. [B/release_notes/release_13_0_1_2/rn_enhancements_sp_3.html]
- Order sizing never exceeds Smax; Review Reasons 346–348. [B/release_notes/release_13_0_1_2/rn_enhancements_sp_4.html]
- OP_COUNT_SALES_RETURNS_THROUGH_HORIZON (true). [B/release_notes/release_13_0_1_2/rn_enhancements_sp_5.html]

---- 13.0.1.3 ---- [B/release_notes/new_in_13_0_1_3.html]
- ABC help chart. [B/release_notes/release_13_0_1_3/rn_enhancements_2.html]
- Geo Locate properties servitistics.map.location.fail.multiple (typo as in the source) and servigistics.map.location.verify.country. [B/release_notes/release_13_0_1_3/rn_enhancements_3.html]
- servigistics.intellicus.automated.comparison.categoryid = Modeling. [B/release_notes/release_13_0_1_3/rn_enhancements_fcst_2.html]
- Next Generation View on Budget Summary. [B/release_notes/release_13_0_1_3/rn_enhancements_io_2.html]
- Sustainability: embodied and transport carbon inputs and outputs; CARBON_MEASURE_TYPE ("kg of CO2e"); IO_CALCULATE_SUSTAINABILITY (false). [B/release_notes/release_13_0_1_3/rn_enhancements_io_3.html]
- Stockout cost visibility. [B/release_notes/release_13_0_1_3/rn_enhancements_io_4.html]
- ENABLE_PROPERTYGRID_GRIDLINES. [B/release_notes/release_13_0_1_3/rn_enhancements_sp_2.html]
- Inventory Studio map. [B/release_notes/release_13_0_1_3/rn_enhancements_sp_3.html]

---- 13.0.1.4 ----
- TP-ROP calendar adjustment rewrite: NUNAD; new settings OP_TIME_PHASED_ROP_CALENDAR_ADJUSTMENTS_AT_TOP_MOST_LOC_ONLY (true) and OP_TIME_PHASED_ROP_CALENDAR_ADJUSTMENT_IO_LEAD_TIME_INCREASE (7). [B/release_notes/release_13_0_1_4/rn_enhancements_sp_2.html]

---- 13.0.1.5 ----
- Manual balancing orders use the replenishment transport mode. [B/release_notes/release_13_0_1_5/rn_enhancements_sp_2.html]
- Oracle parallel_degree_policy=ADAPTIVE and parallel_min_time_threshold=2. [B/release_notes/release_13_0_1_5/technical_notes_13_0_1_5.html]

---- 13.1.0.0 ---- [B/release_notes/new_in_13_1_0_0.html]
Common (release_13_1_0_0/rn_enhancements_2 … _16)
- Toolbar redesign.
- Configurable Go To.
- Best-practice workflows; FAQs.
- Ad hoc Intellicus reports shown in Analytics.
- APPLY_RETURN_WR_NON_REPAIR_LOC (false).
- Circular Reference Finder AutoPilot process (CIRCULAR_REFERENCE_RETENTION_DAYS, 90 per glossary).
- Data Manager entity Vendor Location SKU LT.
- Simulator can include DHM, Demand Aggregation and ML Forecasting.
- Next Generation View on SKU Summary.
- Dealer User Rights tab.
- [B/release_notes/release_13_1_0_0/rn_enhancements.html and siblings]

Forecasting (rn_enhancements_fcst_2 … _10)
- ML Best Fit Integration.
- Error Improvement % (default 10) to reduce method churn.
- Annual Forecast Override at SKU-stream level, with Replace / Increase / Decrease operations.
- Aggregated Forecast Review.
- Outlier Notify/Ignore clear old adjustments.
- Replacement Rate variability from the parent.
- Worksheet sorting.
- Disaggregation Type.
- FORECAST_REVIEW_MAX_GRID_ROWS up to 100,000 (65,000 default).
- [B/release_notes/release_13_1_0_0/rn_enhancements_fcst.html]

Inventory Optimization (rn_enhancements_io_2 … _20)
- Scenario Budget reporting: Turns, Planned Revenue, Cash Outflow; compare up to 12 scenarios (MAXIMUM_ADDITIONAL_SCENARIOS_DISPLAY_COUNT = 5).
- What-If Modeling generally available (GA).
- Carbon Tax, resolved Location, then Region, then CARBON_TAX_RATE (0).
- Objective Cost Criteria (Part Cost / Optimization Cost / Carbon Tax + Part Cost). Bang for Buck = ΔObjective Benefit / ΔObjective Cost.
- Customer Order Size Calculator AutoPilot process: CUST_ORDER_SIZE_* settings; IO_CALC_RESUPPLY_CUST_ORDER_SIZE = CUSTOMER / EFFOQ / NONE.
- Rotable pooling: Maximum Pool Wait Time.
- Default filters.
- EXCEL_EXPORT_ESCAPE_CHARACTER.
- Emergency FR fields.
- Global Settings at Runtime container.
- SIOP fields: Expected Gross Profit, Planned COGS / Revenue / Revenue at Risk, Resale Price.
- Process Group on Optimization Sets.
- Segment Summary Run options.
- TP-ROP safety stock formula.
- [B/release_notes/release_13_1_0_0/rn_enhancements_io.html]

Pricing (rn_enhancements_pricing_2 … _6)
- Configurable Price Offsets: Custom Offset mode; PRC_USE_CUSTOM_OFFSETS; PRC_PRICE_ACTION_GATEWAY_PROPAGATION_MODE.
- Part Kit Pricing (Review Reason 351).
- Price Feedback Management.
- Elasticity Estimation (Recommended Price, Average Elasticity).
- Policy diagnostic definitions.
- [B/release_notes/release_13_1_0_0/rn_enhancements_pricing.html]

Supply Planning (rn_enhancements_sp_2 … _21)
- Vendor Capacity and Multi-Vendor [B/release_notes/release_13_1_0_0/rn_enhancements_sp_2.html]:
  - Capacity and priority pages.
  - Review Reasons 349, 350, 352, 353.
  - Enable Vendor Capacity.
  - OP_VENDOR_CAPACITY_DATE_INDEX (0 Order / 1 Ship / 2 Receive / 3 Available).
- Plan Intelligence.
- Order Spreading.
- Backorder categorization 3.1–3.4.
- IPWS: Show Total/Subtotal; Remaining / Replenishment / Chain Transfer Requested (OP_INHOUSE_UPTO_SMAX).
- Order Sizing (Review Reasons 346–348; "Order Sizing Rules" label).
- Calendar Adjustments.
- TP-ROP rows; ROP SCS.
- Chain Deficit shown at the first capable parent.
- Overdue orders use the primary vendor lead time.
- Full option; Global LTB; comparison links.
- Inventory Studio.
- LTB behavior.
- IPWS launch URL: Pws.mvc?hostPart_toSelect=…&hostLocation_toSelect=….
- Non-ASL label.
- Sales returns through the horizon.
- Transport calendars longer than 1 year.
- [B/release_notes/release_13_1_0_0/rn_enhancements_sp.html]

Technical [B/release_notes/release_13_1_0_0/technical_notes_13_1_0_0.html]
- SQL Server driver 12.2 (servigistics.dburl.encrypt).
- Tomcat 9.0.83 (maxParameterCount 10000).
- Debug log rotation (log4j_debug.properties).
- servigistics.recordsetfetchsize = 500.
- New web services import-csv-file.ws and import-csv-data.ws; run-job.ws gains a process group.
- Encrypted LDAP credentials (servigistics.credentials.encrypted).
- Forecast multithread deadlock fix.

---- 13.1.0.1 ----
- "Change Sequence" naming. [B/release_notes/release_13_1_0_1/rn_enhancements_2.html]
- servigistics.histanalysis.clear.outlier. [B/release_notes/release_13_1_0_1/rn_enhancements_fcst_2.html]
- Streamlined Best Fit graph. [B/release_notes/release_13_1_0_1/rn_enhancements_fcst_3.html]
- Forecast Comparison Under/Over-forecast bias. [B/release_notes/release_13_1_0_1/rn_enhancements_fcst_4.html]
- Price Feedback in Data Manager and Import. [B/release_notes/release_13_1_0_1/rn_enhancements_pricing_2.html]
- Price Transactions (ENABLE_PRC_TRANSACTIONS). [B/release_notes/release_13_1_0_1/rn_enhancements_pricing_3.html]
- Alternate Transport Mode with TP-ROP. [B/release_notes/release_13_1_0_1/rn_enhancements_sp_2.html]
- Order Explanation Report. [B/release_notes/release_13_1_0_1/rn_enhancements_sp_3.html]
- Balancing transport mode. [B/release_notes/release_13_1_0_1/rn_enhancements_sp_4.html]
- TP-ROP deficit rows always shown; Set SCS Min to 0. [B/release_notes/release_13_1_0_1/rn_enhancements_sp_5.html]
- Deployments "Total Daily/Period Forecast" rename. [B/release_notes/release_13_1_0_1/rn_enhancements_sp_6.html]

---- 13.1.0.2 ----
- Forecast Comparison Composite Detail. [B/release_notes/release_13_1_0_2/rn_enhancements_2.html]
- FCST_REP_RATE_USE_PARENT_SD. [B/release_notes/release_13_1_0_2/rn_enhancements_fcst_2.html]
- Forecast Override Intelligence AutoPilot process and message. [B/release_notes/release_13_1_0_2/rn_enhancements_fcst_3.html]
- ADI and Periods Between Demand definitions (PERIODS_BETWEEN_DEMAND). [B/release_notes/release_13_1_0_2/rn_enhancements_fcst_4.html]
- Pricing Home page feedback containers. [B/release_notes/release_13_1_0_2/rn_enhancements_pricing_2.html]
- PRC_PROCESS_PRICE_ACTIVE_SKUS. [B/release_notes/release_13_1_0_2/rn_enhancements_pricing_3.html]
- Ending IP data source. [B/release_notes/release_13_1_0_2/rn_enhancements_sp_2.html]
- Weekly IP Summary dates; Restart Number. [B/release_notes/release_13_1_0_2/rn_enhancements_sp_3.html]
- Last Planned Date without time. [B/release_notes/release_13_1_0_2/rn_enhancements_sp_4.html]

---- 13.1.0.3 ----
- OUTLIER_USE_VARIABILITY_CAP. [B/release_notes/release_13_1_0_3/rn_enhancements_fcst_2.html]
- IPLAN_DONOTRUN_BESTFIT. [B/release_notes/release_13_1_0_3/rn_enhancements_fcst_3.html]
- BUY_LIST_ROUNDING_RULE (−1). [B/release_notes/release_13_1_0_3/rn_enhancements_io_2.html]
- servigistics.enable.poa.view (PO Agreements / Requisitions pages). [B/release_notes/release_13_1_0_3/rn_technical_2.html]

---- 13.1.0.4 ----
- Forecast Worksheet links. [B/release_notes/release_13_1_0_4/rn_enhancements_fcst_2.html]
- TP-ROP: review reasons ignore future need (Review Reasons 18, 52, 53, 93, 94, 112, 134, 135, 137, 333, 334). [B/release_notes/release_13_1_0_4/rn_enhancements_sp_2.html]
- LTB Custom 11–20. [B/release_notes/release_13_1_0_4/rn_enhancements_sp_3.html]
- Part Health user right. [B/release_notes/release_13_1_0_4/rn_enhancements_sp_4.html]

---- 13.1.0.5 ----
- Forecasting Database Cleanup AutoPilot process (removes stale Best Fit overrides; run after Synchronize DB). [B/release_notes/release_13_1_0_5/rn_enhancements_fcst.html]
- Planned Revenue at Risk = (1 − FR) × Resale Price × Interval Forecast. [B/release_notes/release_13_1_0_5/rn_enhancements_io.html]
- Order Plan Synchronize DB cleans SKUs no longer in a GAP. [B/release_notes/release_13_1_0_5/rn_enhancements_sp.html]
- IO_TPROP_ROUND_SS (false). [B/release_notes/release_13_1_0_5/rn_enhancements_sp.html]

4.1 Global settings not already covered in sections 1–4 (from the glossary pages)
Source pages: B/glossary/global_settings_general.html, …_fcst.html, …_io.html, …_sp.html, …_modeling.html. Defaults in brackets.

General
- ADVANCED_REPORTS [true]: PAI and the Run Advanced Reports option.
- AUDIT_TRAIL_KEEP_DAYS [90], AUDIT_TRAIL_LOAD_BLANK [false], AUDIT_TRAIL_MAX_RECORD [1,000,000].
- DISPLAY_CF_CONTRACT_AS_PICKER [false]: use it when there are more than 500 contracts.
- ENABLE_FROZEN_COLUMNS [false], ENABLE_MULTI_MRU [false].
- ENABLE_PROCESS_GROUP_UI [false], ENABLE_SEGMENT_GROUPS [false].
- MANUAL_AP_PROCESS_GROUP: definition shown as "TBD" in the source.
- MAX_POST_CONTENT_SIZE [256mb].
- OUTLIER_MIN_NON_ZERO_DEMAND_SLICES [1], OUTLIER_USE_NON_OUTLIER_SLICES [true].
- OVERRIDE_INTELLICUS_RIGHTS [true].
- SL_HIGH_VOL_VARIABILITY_CAP [30], SL_LOW_VOL_THRESH [25; average period demand below it = slow mover], SL_LOW_VOL_VARIABILITY_CAP [9].
- SL_LOW_VOL_VMR_THRESH [1.1; VMR above it = Negative Binomial, else Poisson].
- SL_VARIABILITY_TYPE [COV or VMR].

Modeling
- ENABLE_ESCM [false]: enables the Modeling menu.

Forecasting
- APPLY_NFF_TO_INT_RETURN_FCST [true], APPLY_RETURN_WR_AND_NFF_TO_CONSUMABLES [false].
- DEMAND_DETAIL_AGGREGATION_BY_SLICE [false], DEMAND_DETAIL_AGGREGATION_MODE [P = Partial; F = Full; W also valid], DEMAND_DETAIL_AGGREGATION_SLICES [12].
- EXP_SMOOTHING_USE_HIST_AVG_BASE [true new / false upgrade].
- MF_SKU_FORECAST_ALLOC_METHOD [0; LLP forecast allocation].
- RUN_POST_FORECAST [true].
- WINTERS_VERSION [3: consider Alpha, Beta, Gamma and full-year history].

Inventory Optimization
- ALLOW_NEGATIVE_SAFETY_STOCK [false].
- ENABLE_NRTS [true; Not Repairable This Station].
- INVENTORY_OPTIMIZATION_MODE [MEO; options SIO / MIO / MEO / MIME].
- IO_FULL_COMPARE_MODE [false].
- IO_NEW_BUY_PROC_EFFOQ_THRESHOLD [false].
- IO_OVERRIDE_CLEANUP_EXPIRED_RECORDS_DAYS [180].
- LEVELS_DAYS_CONSTANT [false].
- MEO_OVERRIDE_CODE_REQUIRED [false], MEO_OVERRIDE_DEFAULT_PERIODS_TO_EXPIRE [0], MEO_OVERRIDE_MAX_QTY [0], MEO_SKU_OVERRIDE_TYPE [ROP].
- NOPT_CROSS_BORDERS [true].
- SPACE_CONSTRAINT_TYPE [Cubic Meter].

Supply Planning
- APPROVE_FOR_UPLOAD [false; two-stage order approval].
- ENABLE_ADVANCED_LAYOUT_IPWS [false].
- ENABLE_DASHBOARD_CACHE [true; Refresh Planner 360° process].
- OP_BALANCE_UPTO_SMAX [false], OP_BALANCE_USE_ONHANDEXCESS [false].
- OP_FORECASTED_RETURNS_STARTING_ON_DAY2 [false], OP_IGNORE_RETURN_FORECAST_UNTIL_RETURN_LT [true].
- OP_INCLUDE_SALES_ORDERS_TO_CALC_TRIGGER_INVENTORY_POSITION [true].
- OP_REDUCE_PARENT_NEED_BY_IP_EXCESS [false].
- OP_SCS_MOVE_TG_TO_AVAIL [a], OP_SCS_TG_RESPECT_CAL [true].
- OP_SHORTAGE_SORT_CRITERIA_1 / _2 [q / s].
- OP_TIME_PHASED_ROP_INCLUDE_CALENDAR_NEED [true], OP_TIME_PHASED_ROP_IP_DAYS_TO_OUTPUT [true].
- PWS_EDIT_CO_ORDERS [true], PWS_UPLOAD [false; upload approved orders to host].
- USE_TIME_PHASED_LEVELS [true].

==========================================================================
5. SECURITY, USERS, SEGMENTS, CLASSIFICATION, AUTOPILOT, KPIs
==========================================================================
5.1 Users and rights
- User fields [B/core/core_pid/pid_new_edit_user_page.html]:
  - Sign In Name (case-sensitive). The password is hidden when servigistics.authenticationtype = REMOTE_USER.
  - Template Name; Role Name; Preferred location; Customer.
  - Account active, change on next login, can change password, never expires.
  - The two pricing approval-limit fields.
  - Report Role (Intellicus); Host Planner ID.
- User Templates with template overrides. [B/glossary/user_template.html]
- Temporarily Assign User Rights: covering user plus start and end dates. [B/core/core_pid/pid_temporarily_assign_user_rights_page.html]
- Column Security. [B/glossary/column_security.html]
- Rights tabs: Forecasting, Price Simulation, Price Analysis, Price Optimization, Inventory Optimization, Supply Planning, Inventory Studio, Processing, Analytics, Modeling, Settings, OTF Rights, Review Subscriptions, Column Security, Price Approval Roles, Import, Products, Custom Tables, Custom Pages, Segment Folders, Dealer, Action/Admin/Base Setup Rights. [B/core/core_smart_help/sh_user_rights_setup_page.html]
- Right values [B/core/core_pid/pid_urs_page_tabs.html]:
  - Allowed / Not Allowed; View / Modify / Modify All; Create; Run.
  - Approve / Approve & Reject; Approve Limit ("Planned Quantity × Price per Unit").
  - Configure / Configure Default; Set Default Layout.
  - Modify Production / Scenario; View Production / Scenario; Save.
  - Upload; Order Part; Request Part; Create Policy and Segment; Edit Table / Settings; Modify Attach Rate.
- Segment Folders tab: segment-node access. [B/core/core_smart_help/sh_urs_page_segment_folders_tab.html]
- Override Security (Allow Recommend / Review / Delete others') and Override Assignment (user + segments). [B/inv_opt/inv_opt_pid/pid_override_security_page.html; B/inv_opt/inv_opt_pid/pid_override_assignment_page.html]
- IPCS_OVR_USER_LOCATIONS caches location security (13.0.0.0). [B/release_notes/release_13_0_0_0/rn_enhancements_io_20.html]

5.2 Segments
- Menu: Settings > Configuration > Part Classification, which holds ABC Class Sets, ABC Parameters, Custom Attributes and Segments. [B/core/core_topics/module_settings_part_classification.html]
- Segment: "A group of SKUs that have attributes in common…". Parameters are applied via segment coverages. [B/glossary/segment.html]
  - Strategies: Matrix (e.g. 2 price bands × 4 part types = 8 segments) and Pyramid (most specific first, ending with Default).
  - Example: critical parts with Demand Accommodation 100% are all on the ASL.
- Coverages: and/or equations, e.g. "Part Type is equal to Manufactured And Standard Cost is greater than $1000 And Region starts with North". "Best to always use upper-case letters." [B/glossary/segment_coverages.html]
- Segment Group: one segment per SKU within the group. [B/glossary/segment_group.html]
- Segment Tree: hierarchical nodes; node coverage acts as an extra AND and as a security layer. [B/glossary/segment_tree.html]
- Segment fields [B/core/core_pid/pid_new_edit_segment_page.html]:
  - Dimension: anything other than Part/Location is used only in IO service groups, for "different target fill rates by customer/service contract".
  - Only If Install Base Exists.
  - Classification.
- Classification values: All, None, AutoPilot, Security ("assigned to users"), Parameter ("assigned to schemes"), Copy Demand, Filter, Business Intelligence. [B/core/core_pid/pid_segments_page.html]
- Segments page columns [same URL]:
  - Derived Values in Criteria: must be Yes to use ABC results.
  - Total SKU Count: needs servigistics.show.segment.sku.count.
  - Exclude Replaced Part.
- Refresh: the Update Segmentation AutoPilot process. Demand categories (13.0.0.0) are refreshed by Synchronize Database and Update Segmentation. [B/glossary/segment.html; B/release_notes/release_13_0_0_0/rn_enhancements_fcst_3.html]

5.3 Part classification
- ABC: "categorizing SKUs into different classes based on demand volume, demand value, cost, or custom characteristics". Bases are percentage rank, absolute rank, tier values or percent values. Results go to IPCSCUST_STOCK_AMOUNT (example columns ABC_UNITS_PCT_RANK, XYZ_COST_TIER_VALUE). [B/glossary/abc_classification.html]
- Class Set types: Demand (units or hits), Demand Value (History × Price), Cost, Custom, Forecast, Forecast Value. Also: Part/SKU level, SKU Grouping, Slice Grouping, number of slices, streams, and the 13.0.0.0 zero-slice option. [B/core/core_pid/pid_new_edit_abc_class_set_page.html]
- ABC Parameter: Promote Ties; Tier Type; rules, e.g. A = 80%, B = 15%, C = 5%. Assigned to segments with Derived Values = No. [B/core/core_pid/pid_new_edit_abc_parameter_page.html; B/core/core_smart_help/sh_assign_segments_page.html]
- Workflow: create the Class Set, restart the server, create the Parameter, run Synchronize Database, then use the results in segments. [B/glossary/abc_classification_2.html]
- ABC Code on the SKU. [B/glossary/abc_code.html]
- Part Criticality: user-defined codes, "numeric (1–10), alphanumeric (A, B, C, D), or even descriptive titles"; page under Settings > Data Management > Part. [B/glossary/part_criticality.html; B/core/core_smart_help/sh_part_criticality_page.html]
- Criticality Multiplier: influences optimization selection and availability. [B/glossary/criticality_multiplier.html]
- Location Critical flag; Part Critical field (13.0.0.0 Stocking Policy).
- No named velocity-class feature. Velocity is handled with a Demand ABC class set (units or hits). XYZ is just another class set.

5.4 AutoPilot
- "An agent that runs selected processes … collectively or individually at desired frequencies against one or more segments." [B/glossary/autopilot.html]
- Data flow: the gateway loads host data "(typically on a nightly basis)", then AutoPilot processes it, then upload tables go back to the host. [same URL]
- Pages: Job, Process Log, Process Status (instances Active / Idle failover / Inactive), Run Manual Process (segments + threads), Run Custom Process (pricing). [B/core/core_topics/module_processing_autopilot.html; B/core/core_pid/pid_autopilot_page_status_tab.html; B/core/core_smart_help/sh_autopilot_page_manual_tab.html]
- Scheduling (New/Edit Job) [B/core/core_pid/pid_new_edit_job_page.html]:
  - Fields: Active, Frequency, Frequency Units ("minutes, daily, weekly, or monthly"; "3 … Weekly … once every 3 weeks"), Scheduled Run Date/Time, Pricing Market Group.
  - Assign Segments / Processes / Reports / What-If Scenarios / Network Optimization Scenarios.
- Cadence as documented:
  - Host data is processed daily.
  - Process Groups and the Frequent Data Load process allow intraday loads (needs ENABLE_PROCESS_GROUP_UI and MANUAL_AP_PROCESS_GROUP). [B/glossary/process_group.html; B/glossary/process_group_2.html]
  - Pricing Monthly Financial is monthly.
  - Frequent Data Load blocks the gateway and Synchronize Database while it runs.
- Process list by category [B/glossary/autopilot_processes.html]:
  - Core: Attachment Storage Synchronizer; Circular Reference Finder; Database Maintenance; Gateway Consistency Check; Get Host Data; Review Process ("Refreshes the Review Board"); Synchronize Database ("Determines the parameters … and calculates stock amounts"); Update Segmentation. [B/glossary/autopilot_processes_2.html]
  - Network Optimization: Geo Locate; Location Matcher; Network Optimization. [B/glossary/autopilot_processes_3.html]
  - Lifecycle: Lifecycle Analytics; Calculate Decay Rate; Last Time Buy Recommendation; Last Time Buy Forecast. [B/glossary/autopilot_processes_4.html]
  - Pricing (includes Pricing Elasticity, Price Streams and Offsets, Apply Configurable Price Offsets, Pricing Monthly Financial, Pricing Engine). [B/glossary/autopilot_processes_6.html]
  - Report: Run Advanced Reports. [B/glossary/autopilot_processes_7.html]
  - Planning [B/glossary/autopilot_processes_8.html]:
    - ASL Generation (supports Mid-Slice ASL Adjustment).
    - BestFit Forecasting.
    - Causal Forecast Detail; Causal Equipment Loader and Rollup.
    - Copy Demand.
    - Customer Order Size Calculator.
    - Delete Orphan IO Scenarios.
    - Demand Aggregation; Demand Detail Aggregation; Demand History Management.
    - Disassembly.
    - Forecast Netting; Forecasting; Forecasting-Calculate Metrics; Forecasting Database Cleanup.
    - Frequent Data Load.
    - Generate Order Plan (includes Post Review and Post Auto Approval Review).
    - High Margin Analysis.
    - Maintenance Forecast Detail.
    - Make Forecast Production.
    - IO – Run Supersession Changes.
    - Merge SKU Overrides.
    - Plan Intelligence.
    - Multi-level BOM Synchronize Database.
    - Post Forecast.
    - Refresh Planner/Part 360°.
    - Scheduled Event Detail.
    - Stock Level Generation ("Calculates the optimal levels for each SKU").
    - Vendor Group MOQ; Vendor Split.
  - PAI [B/glossary/autopilot_processes_9.html]: Analytics Database Maintenance; Analytics Purge (servigistics.analytics.purge.retain.days / .retain.slices); AWS Zeppelin Start and Stop; Correlated Parts Intelligence; General Analytics Data Loader; Forecast Accuracy Intelligence; Forecast Analytics Generator; Forecast Override Intelligence; Machine Learning Forecasting; Mean Time Between Failure; New Part Introduction Forecasting; Planning Analytics Generator; Region MTBF.
  - Dataset Comparison: Forecast and Order Plan Comparison – Data Backup and Build Report. [B/glossary/autopilot_processes_10.html]
  - IO scenario jobs [B/glossary/autopilot_process_dependencies.html]:
    - Calculate: depends on Database Maintenance, Get Host Data, Synchronize Database, Order Plan Sync DB, Forecasting, Forecast Netting, ASL Generation.
    - Also: Make Production, Apply Overrides / To Production, Start Collaboration, Evaluate Exception Criteria, Delete Expired Production Scenarios, Calculate Visual Analytics, Generate Multi-Period Budget Report.
    - "Run in parallel unless there is a dependency."

5.5 KPI definitions (core / IO)
- Fill Rate: "fraction of demand that is met through immediate stock availability, without being backordered". [B/glossary/fill_rate.html]
- Fill Rate Methods [B/glossary/fill_rate_method.html]:
  - Fill Rate / Probability In Stock (PIS).
  - PIS with Reorder Quantity Benefit.
  - 1 − EBO(ROP+1)/Reorder Qty.
  - 1 − EBO(ROP+1)/Pipeline Forecast.
- Availability: "expected percentage of time that equipment is operational". Network and Location Availability are MIME only. [B/glossary/availability.html; B/glossary/network_availability.html; B/glossary/location_availability.html]
- EBO: "average units of demands that are waiting to be filled". [B/glossary/ebo.html]
- Network Fill Rate: weighted by external and internal forecasts. Customer Network Fill Rate: external only. [B/glossary/network_fill_rate.html; B/glossary/customer_network_fill_rate.html]
- Location Wait Time. [B/glossary/location_wait_time.html]
- Incremental Fill Rate. [B/glossary/incremental_fill_rate.html]
- Inventory Turns = (Daily Demand Rate × 365) / Average Inventory. [B/glossary/inventory_turns.html]
- Days on Hand = (On Hand New + On Hand Fixed) / Avg Daily Demand. [B/glossary/days_on_hand.html]
- Service Group Parameters [B/inv_opt/inv_opt_pid/pid_service_group_parameters_create_edit.html]:
  - Service Metric: Fill Rate; Availability and Fill Rate (MIME); Fill Rate with Emergency Backup. It cannot be changed after saving.
  - Parent Membership: Direct / Derived-Reporting / Derived-Targets and Constraints.
  - Targets: Customer Network FR, Customer Location FR, Total Location FR, Primary / Secondary Emergency FR, Network / Location Wait Time, Network / Location Availability, Contract Wait Time / Availability.
  - Capacity constraints (SPACE_CONSTRAINT_TYPE).
  - Minimize Stockout Cost.
- Stockout Cost formulas: see the 13.0.0.0 IO section.
- Planned Revenue at Risk: see 13.1.0.5.
- PAI fill-rate, missed and forecast KPIs: see 3.3.
- Pricing KPIs (Net Change %, Margin, Market Position): see 1.13.

Source issues to keep in mind:
- PRC_USE_CUSTOM_OFFSETS: the text says true hides the option, which contradicts its purpose.
- PRC_PRICE_ACTION_GATEWAY_PROPAGATION_MODE: the default is listed as "true" although the values are 1/2/3.
- The Geo Locate property is misspelled "servitistics" in the source.
- The rn_enhancements_fcst_6 page (Run Post Forecast Process) is empty in the crawl.
- IO_PROD_SKU_TRACKING: the glossary default is 2, while the release notes recommend 1 for large configurations.