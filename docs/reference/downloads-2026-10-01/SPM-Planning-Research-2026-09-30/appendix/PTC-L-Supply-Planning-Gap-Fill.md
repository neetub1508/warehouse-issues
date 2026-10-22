# Gap notes: Supply / Order Planning, Repair, LTB, Planner workflow (Servigistics 13.x)

Prefix `HC/` = `https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/`.
Excluded as already known: TR/TPSS/TPROP basics, order sizing steps, SCS basics/time gates, auto-approval horizon/MOV, global_settings_sp list, review reason catalogue, balancing/fair share basics, ATM basics, order spreading.
"—" in Default = the help does not state one. **UNVERIFIED** = my inference.

## 0. Supply search sequence (core algorithm)
Order Plan satisfies each day's need by searching supply in this order: **1 Upchain Excess → 2 Substitution → 3 Repair → 4 Balancing → 5 Excess Recall → 6 Procurement or Replenishment → 7 Remaining Need Chain Transfer → 8 Expensive Repair**. Priorities inside a method come from setup data (substitution priority, repair option priority). All SKUs in a GAP (group of associated parts) are planned together. — HC/glossary/supply_planning.html
- `Balancing and Excess Recall Before Repair` (Ordering Param) can swap 3 with 4/5; expensive repair is always last. — HC/parts/parts_pid/pid_new_edit_ordering_parameters_page_general_tab.html
- Generate Order Plan (Interactive Plan, Plan tab) sub-steps: OP Preproc → BestFit → Forecasting → Forecast Rollup → Forecast Netting → Levels → Review Process → Mid-review → OP Levels → OrderPlan → OP Part Kit → Post-review → Review Post Auto Approve. Results are in memory until Save. — HC/glossary/interactive_plan.html
- After Post Review, Post Auto Approval Review runs (review reasons 323 repair / 324 repl / 325 balancing / 326 procurement / 332 excess recall "new recommended orders"). — HC/glossary/autopilot_processes_8.html

## 1. Ordering Parameters — General tab
Source for all rows unless noted: HC/parts/parts_pid/pid_new_edit_ordering_parameters_page_general_tab.html (list page: HC/parts/parts_pid/pid_ordering_parameters_page.html; SKU-level view: HC/parts/parts_pid/pid_ps_page_ordering_tab.html). A scheme has a Priority Sequence and is assigned to segments.

| Name | Meaning | Default / range |
|---|---|---|
| Run Order Plan | No = no orders of any type for the SKU; Yes = plan posted to the Planner Worksheet (proc/repl/repair/balancing per other flags) | Yes/No |
| Plan Non-ASL Pairs for Backorder | Use stock at non-ASL SKUs as sources (balancing out, repl out, repair option, chain transfer, substitution). Must be Yes to procure non-ASL parts that have backorder/sales order | Yes/No |
| Ignore Forecast | Levels still use the forecast, but time-phased OP consumes only actual demand (sales orders/backorder). For slow, expensive parts. Trigger point is unaffected. Part/SKU value overrides | Yes/No |
| Use Aggregate Balance Amounts | Trigger Point only. No = Sync DB derives BO from Sales Orders, In Return from Sales Returns, In Repair/On Order from Order Plan. Yes = detail records are created from the aggregates. **SCS is disabled when Yes** | Yes/No |
| Order Policy | Trigger Point / Time-Phased Safety Stock / Time-Phased ROP (TPROP needs OP_TIME_PHASED_ROP_ENABLE) | — |
| Forecast Horizon Days | Last possible Available Date for planning, extended to the end of the slice. Also sets the slices shown in the Weekly/Monthly views | days; becomes −1 when Use Max LT is on |
| Use Max LT | Per-SKU horizon = longest pipeline LT | checkbox |
| Max Auto Horizon | Horizon cap used when Forecast Horizon Days is 0 or null. −1 (recommended) = Days to Generate Orders + longest LT in the GAP, capped. 0 = no time-series output but orders are still planned. >0 = days of output | **730** (system default) |
| Order Period Display | Weekly or monthly worksheet display | — |
| Include Backorder in Order Plan | TP policies. Yes (recommended) includes BO. No = an unmet SO/BO/forecast is not carried forward; unmet replenishment requirements still are | Yes recommended |
| Start Display / End Display | Worksheet lines keyed by Order vs Ship date / Receive vs Available date | — |
| Only Run Order Plan When Triggered | Plan only when IPWS `Need To Plan`=Yes, or when a Review Board record whose review type has `Trigger Order Plan` checked fires | Yes/No |
| Plan Date | Order Date (almost always for procurable SKUs) vs Ship Date (shortens effective LT to transport + putaway). For repl SKUs: when source stock is consumed. Also drives the **commitment level** (see §1a) | Order Date / Ship Date |
| Days to Generate Orders | Last possible Order Date, e.g. 14 = orders only within 14 days. Blank = no effect | days |
| Enable Vendor Capacity | Monthly vendor capacity (TPROP only). Reveals `When Repair Capacity Is Fully Consumed`: "Procure only for need above future repair" vs "Procure immediately for full remaining need" | No/Yes |
| Output Generated Orders | All orders all locs / all for repair+procure locs and today's for others / today's only (TPROP) | — |
| Enable Procurement / Enable Repair / Enable Replenishment | Order-type master switches | Yes/No |
| Enable Push Repair | Shown only if Repair=Yes. Builds on Repair All: Yes = repair all bad units immediately with no requirement needed; No = Repair All triggered by need. Self-part repair only, not Repair Options/Rework | Yes/No |
| Respect Order Sizing in Push Repair | Push repair obeys order sizing | Yes/No |
| Ignore Repair Wash Rate on Day 1 | Repair wash rate is applied only after Day 1 | Yes/No |
| Avoid Procurement within Repair LT | Blocks new procurement inside max(Proc LT, Repair LT) when defective goods inventory can cover need at repair LT. May cause shortages, which raise Critical Shortage review reasons. Active only until repair LT | Yes/No |
| Avoid Chain Transfer within Repair LT | Repairable alternate down-chain parts use their own On Hand Bad (what they can repair today) before asking the up-chain parent | **Yes** (doc: "This is the default") |
| Allow Upchain Excess Transfer | Start-of-day excess chain transfer first, vs the down-chain SKU ordering first | No / Yes all locs / Yes only non-repl-source locs; **default Yes, only non-replenishment locations** |
| Perform Upchain Excess Transfer | TPROP: when the transfer runs | Before / After Balancing & Excess Recall |
| Allow Remaining Need Chain Transfer | Pass down-chain remaining need to the parent | Never / Only if not procurable and not replenishable |
| Enable Part Substitution → Allow Substitution Excess Transfer → Perform Substitution Excess Transfer | Same pattern as upchain, applied to substitutes | default Yes, only non-repl locs |
| Allow Substitution From Replenishment | Substitution inside replenishment ordering | Yes/No |
| Disconnected Replenishment (+ Replenishment Source Internal Stream) | Destination repl orders are seen upstream only once approved; the stream is used to net them against the source forecast | Yes/No |
| Enable Receiving Balancing | No / Balance only for own need / Balance also for downstream need | **"also for downstream" = default & recommended** |
| Balancing and Excess Recall Before Repair | Prefer balancing/recall over repair | Yes/No |
| Enable Sending Excess Recall | Recall Day-1 on-hand excess from allowed sources whatever the destination's need, which reduces central procurement | Yes/No |
| Enable Cost Based Repair | Consider procurement before "expensive" repairs | Yes/No |
| Enable Schedule Change Suppression | Needs a separate SCS scheme | Yes/No |
| Orders Count In Order Plan | Whether this scheme's orders are seen by OP. Order-level override on IPWS. Clear it when Aggregate Balance=Yes and host orders are uploaded (avoids double count) | Yes/No |
| Respect Order Sizing In Repair Options | — | Yes/No |
| Enable Alternate Transport Mode | Also on the proc/repl tabs | Yes/No |
| Consider Need Until Lead Time | Adds known need within LT (netted forecast + confirmed SO − incoming supply) on top of SS or SCS Min, so shortages are flagged and acted on earlier ("like a frozen period") | checkbox |
| Backorder Threshold Days / BO Threshold LT Multiplier | Allowed BO days, e.g. 0, 1, 10 / fraction of LT, e.g. .2 (also per proc/repl tab) | — |
| Enable Already Ordered | Consider future host orders before creating new ones (not for Trigger Point). No / Until Last Host Order / Until Specific Days (= Constant Days past LT × Multiplier) | **No (default)** — HC/glossary/already_ordered.html |
| Excess Burnout Days | Adds `DemandRatePerDay × days` to the Excess Limit (preferred over SCS/balancing multipliers). DemandRatePerDay = OptDailyDmdRate (MEO) or SLDemandPerDay (Stock Levels) | days |

- Already Ordered guidance: a narrow window such as 1 LT + 7 days is reasonable. "Until Last Host Order" is not recommended when soft commitments extend to the horizon, because of processing cost. — HC/glossary/already_ordered.html
- Excess Limit = Stock Max (TP) or SS + EOQ − 1 (time phased), raised by order sizing / burnout. — HC/glossary/excess_limit.html

### 1a. Order Limit Periods, commitment levels, frozen period
- **Order Limit Period 1–3** (SKU page, Vendor Location SKU Lead Time): "the number of days out for which order quantity changes will be allowed". Used by Review Board, Auto Approvals and Order Plan. When Order Limit Periods are used, auto-approval applies them only up to the Auto Approval Horizon. — HC/core/core_pid/pid_sku_page_general_tab.html; HC/parts/parts_pid/pid_new_edit_vendor_location_sku_lead_time_page.html; HC/glossary/auto_approval_horizon.html
- **Commitment Level** from Plan Date: L1 < Today+P1; L2 in [P1, P1+P2); L3 in [P1+P2, P1+P2+P3); **L4 beyond = most flexible, fully recalculated**. Levels 1–3 "impose restrictions definable in the Ordering parameters" (the help does not detail them — **UNVERIFIED** what exactly each level blocks). Field `Order Commitment Level` is on the order. — ordering general tab; HC/parts/parts_pid/pid_new_edit_order_page.html
- Review reasons: **24** Qty Change Outside Commit Level, **25** Date Change Outside Commit Level (both "boundaries set using specific Ordering Parameters"), **29** Order is to Be Frozen ("Order Plan will not change an order if it is within the frozen period"), **130** Expedites ("Order Expedited Orders cannot be auto approved"), **131** Deferrals, **23** Maximum Order Value Exceeded. — HC/glossary/review_reason_2.html. **UNVERIFIED**: frozen period = Order Limit Period 1 / commitment level 1. No separate "frozen days" field was found.
- Expedite/defer amounts are governed by SCS (Expedite Days / Defer Days per time gate, plus Expedite/Deferral thresholds = constant + LT multiplier). OP marks orders `Supply Shipment Expedited` / `Deferred` in Recommended Actions. — HC/parts/parts_pid/pid_new_edit_scs_parameter_page_procurement_tab.html; HC/parts/parts_pid/pid_ipws_orders_section.html
- Expedite Report page: weekly forecast vs open purchases/repairs/sales vs On Hand (OHG − BO) vs SS, plus substitute stock. — HC/parts/parts_pid/pid_expedite_report.html

### 1b. Procurement / Repair / Replenishment / Balancing / Excess Recall tabs
HC/parts/parts_pid/pid_new_edit_ordering_parameters_page_proc_repair_repl_bal_tabs.html
| Name | Meaning | Default |
|---|---|---|
| Ordering Calendar Name | Used when the vendor has no calendar | blank → default calendar **24×7** |
| Break Order Into Multiple Orders Using | No / EOQ (proc, repl) / Repair EOQ (repair) / Order Size. N/A for excess recall | — |
| Respect (Repair) EOQ Multiplier in Ordering | Yes = round need to EOQ multiples, then apply order sizing (soft). No = use the raw need when remainder/EOQ < (Repair) EOQ Threshold | — |
| Allow Auto Approval / Auto Approval Horizon / Max Order Value w/o Approval | per order type (known) | — |
| Requires Purchase Agreement | Proc & repair only: no order without a valid PO agreement (review reason 30 "No Valid Purchase Agreement") | Yes/No |
| Enable ATM, Backorder Threshold Days/LT Mult | per tab | — |

## 2. AutoPilot Parameters (segment scheme)
HC/parts/parts_pid/pid_new_edit_autopilot_parameter_page.html. **The help gives no numeric defaults for any field.**
| Name | Meaning | Default |
|---|---|---|
| Review Slices 1–3 / Review Limit 1–3 / Demand Minimum 1–3 | Actual vs forecast test (review types 1–3): variance > Limit σ over Slice periods and actual demand > Demand Min | — |
| Forecast Monitor Slice 1–3 / Forecast % Change 1–3 / Forecast Minimum 1–3 | Forecast-change test (review types 4–6) | — |
| Stream Configuration | Forecast stream config for the segment | — |
| Critical Shortage Threshold | % of SS that (OH − BO − allocated) must fall to for a Critical Shortage (Critical Shortages page, red on Part/Location props). Order `Shortage Date` = when stock < SS × threshold | % |
| Excess Threshold | % over Stock Max (e.g. 150%) before excess review reasons/exceptions fire. **Does not change the Excess Limit** | % |
| Fair Share Reserve (%) / Fair Share Reserve Quantity / Fair Share Priority | Source SS share protected from downstream repl; the qty form covers SS=0. Priority is advisory only (overridable at loc type/loc/SKU) | — |
| Automatically Add to ASLs / Automatically Delete From ASLs | Checked = AutoPilot changes the ASL until the planning scheme's Demand Accommodation is met; unchecked = recommend only | checkbox (default state not stated) |
| Minimum ROP / Minimum Stock Max | Floors on the levels | — |
| Round-Up Thresholds: SS, ROP, EOQ, RROP, REOQ, Days | Fraction needed to round up by 1. Days = SS Override (Days) → units, shared by Stock Levels and IO | — |

## 3. Other supply parameter schemes
**Balancing** (TPSS & TPROP share one page) — HC/parts/parts_pid/pid_new_edit_balancing_parameter_page.html; also pid_balancing_parameters_page_tpss/_tprop
| Name | Meaning / options |
|---|---|
| Allow Partial | Fill a multi-unit need from several sources (expensive/critical parts); off = one source must cover the whole need |
| Primary Source First / Primary Amount / Primary Threshold | Use the repl source's excess first. Amount options: **Excess Limit (recommended)**, Safety Stock, Days of Supply = (OHG − BO − Alloc) − Spread − Need Until Threshold, Zero or Safety Stock, SS/ROP (mixed TP+TP-phased). Threshold multiplier ≥1.00 recommended; blank = 1.00 |
| Min Order Value (+ reference currency) | = qty × unit cost + order cost |
| Source Segment / Type / Region / Amount / Threshold / Additional Retention Days (rules 1–7) | Hierarchy of up to 7 source rules. Region = Same / Parent / Parent or Below / Any; Type = location type or Any. Retention days add a buffer to NuNAD at the source, e.g. 14. For TP sources: days × demand/day, plus SOs if OP_INCLUDE_SALES_ORDERS_TO_CALC_TRIGGER_INVENTORY_POSITION |

**Excess Recall** — HC/parts/parts_pid/pid_new_edit_excess_recall_parameters_page.html: Excess Limit Threshold Multiplier (1.0=100%), Min Order Value Threshold, Priority Sequence (params applied ascending), Recall to Location, **Recall to Replenishment Source Location (default NO)**, Additional Retention Days, Source Segments.

**Action Parameters** — HC/parts/parts_pid/pid_new_edit_action_parameter_page.html: Procurement Allowed, Repair Allowed (normally central only; lets field locations procure or repair), Source Location Name (override repl source; part/loc/SKU overrides beat this).

**Transport Mode Parameters** — HC/parts/parts_pid/pid_new_edit_transport_mode_parameters_page.html: only name/segments plus the Selected Transport Modes lists on the Procurement tab (vendor→dest) and Replenishment tab (source→dest).

**SCS parameter tabs** — HC/parts/parts_pid/pid_new_edit_scs_parameter_page_procurement_tab.html (repair tab identical with REOQ Multiplier; _tprop variants exist)
- Enable Procurement/Repair SCS; Exclude Non ASL (the doc wording is inverted). Min/Max Calculation Type = **ISL** or **Excess Limit/Safety Stock**.
- ISL = Constant + SS×SS Mult + EOQ×EOQ Mult. Without SCS the default ISL is **SS + ½ EOQ**.
- Per time gate: Constant days + LT multiplier or Horizon. Limits: Min = const + mult×(ISL or SS); Max = const + mult×(ISL or Excess Limit).
- Strategies: If above Max → decrease/defer, Bring down to ISL or SCS Max. If below Min → increase/expedite, Bring up to SCS Min or SS.
- Per gate: Allow create, Allow cancel, Consider Already Ordered, Increase %, Decrease %, Expedite Days, Defer Days.
- Strategy Thresholds: Increase and Decrease/Cancel use a 2-tier condition (qty and/or value; SKU condition overrides the scheme per tier). Expedite and Deferral thresholds = const + LT multiplier. Changes below the threshold are dropped.
- Notifications: 134 Below Min, 135 Below ISL, 136 Order cancellation, 137 Above Max per the SCS page (same text on both tabs). But the review catalogue lists 95 = "Orders cancelled due to Procurement SCS", 136 = "cancelled due to Repair SCS", 137 = "On Hand Over the Repair SCS Maximum". So 134–137 are probably the *repair* codes and procurement uses other codes (**UNVERIFIED**; the docs are inconsistent).
- Release note: in 13.1.0.3 the last time gate no longer has to be Horizon. — HC/release_notes/release_13_1_0_3/resolved_issues_13_1_0_3.html

**Review Parameters** — HC/core/core_pid/pid_new_edit_review_parameter_page.html. Per review reason:
- Parameter 1/2
- Block Auto Approval
- Trigger Order Plan (works only with Only Run OP When Triggered)
- Active
- Delay Days (blank → REVIEWED_ACTION_DELAY_DAYS global; that default was not found)
- Retention: Retained / Use Retention Period (**30 days default**, configurable at install) / Delete
- Type: Exceptions (auto-cleared when the condition ends) vs Notifications (kept until manually removed)

## 4. Repair, returns, rotables
- **Repairable / Generate Repair Orders** is a part flag (Parts page). Order types: Balance, Excess Recall, Procurement, Repair, Replenishment. — HC/glossary/generate_repair_orders.html; HC/glossary/order_type.html
- **Repair Options** (Part Props → Repair Options tab): SKU; Type = **Repair** (bad → a different fixed part) or **Is Rework** (good → a different good part); From Part/From Location; Auto Repair (used by Generate OP); Priority (lower number first); Lock status (blocks host overwrite). — HC/parts/parts_pid/pid_new_edit_repair_options_page.html
- Wash and NFF:
  - Repair Wash Rate: need 10 good at 10% gives a recommended 11 bad; Recommended Bad Qty = Rec Qty / (1 − RWR). — HC/glossary/repair_wash_rate.html; ipws orders
  - Return Wash Rate: forecast returns = Forecast × (1 − RtnWR), used to project On Hand Bad. — HC/glossary/return_wash_rate.html
  - NFF Rate: share of returns usable as good without repair. IPWS "Bad Available In Future" = In Return × (1 − NFF). Part Health "Good from Returns" uses NFF. — HC/glossary/no_fault_found_rate.html; HC/parts/parts_pid/pid_ipws_order_sku_parameters_section.html; HC/core/core_pid/pid_part_health_page_summary.html
  - Not Repairable This Station % is also defined. — HC/glossary/not_repairable_this_station.html
- Stock buckets: On Hand Good/New/Fixed/Bad, In Return (Good/Bad; client-driven, RMA), In Repair (Good/Bad, = repair WIP), each with an *Original* copy. — glossary in_return*, in_repair*, on_hand_bad
- Repair sizing: Repair EOQ/REOQ, Repair Fixed Order Size, Repair Order Period (min days between repair orders, 0 = none), Repair ROP, Repair LT, Return LT (+ overrides/std dev). — glossary repair_*
- Returns global settings (HC/glossary/global_settings_sp.html):

| Setting | Meaning | Default |
|---|---|---|
| OP_FORECASTED_RETURNS_STARTING_ON_DAY2 | true = forecast returns available at end of day; false = not pickable today (offsite repair). Since 13.1.0.3 applies to TPSS only | false |
| OP_IGNORE_RETURN_FORECAST_UNTIL_RETURN_LT | true = count actual sales returns (not return forecast) within return LT, avoiding a double count | true |
| OP_COUNT_SALES_RETURNS_THROUGH_HORIZON | TPROP IP counts all actual returns through the horizon (true) or only up to return LT (false) | true |
| OP_OVERDUE_ORDERS_AVAILABLE_TOMORROW | Overdue order effective available date moved to tomorrow | false (upgrade) / true (new install) |
| OP_USE_REPAIR_COST_FOR_REPAIR_AUTOAPPR | Repair orders valued at Repair Cost for auto-approval (repl/bal use Repl Order Cost) — HC/glossary/order_cost.html | — |

- **Roll Up Demand As Repairable**: demand rolls to the parent location and is inducted into repair there. — HC/glossary/roll_up_demand_as_repairable.html
- **Disassembly**: products scheduled for teardown feed parts into projected on hand.
  - Setup fields: Location, Product, Quantity, Available Start/End Date, Include In Analysis, Priority (higher number evaluated first).
  - Plan fields: Plan Disassembly End Date, Plan Quantity (gross recoverable).
  - Run by the Disassembly AutoPilot process.
  - Sources: HC/parts/parts_pid/pid_disassembly_setup.html; pid_new_edit_disassembly_page.html
- **Part Kits / Kitting**:
  - A Part Kit is a part with Is Part Kit=Yes. Kit demand (procurement order) becomes dependent demand on components via dummy internal sales orders.
  - Kits cannot be on the ASL.
  - Kitting types: Global (1, not overridable), Default (1, overridable), Location Specific (many).
  - OP runs an "OP Part Kit" step; depth is capped by OP_MAX_PARTKIT_DEPTH.
  - Sources: HC/glossary/part_kit.html; HC/glossary/kitting.html; HC/parts/parts_smart_help/sh_ipws_part_kit_details.html
- Cost-based repair: Effective Repair Need Unit Cost = weighted average of repair sources. Expensive repair is the last supply step. — HC/glossary/effective_repair_need_unit_cost.html

## 5. Supersession / substitution in ordering
- Part chain relation types (HC/glossary/part_chain.html; HC/core/core_pid/pid_part_chain_details_page_parts_tab.html):
  - **Replace**: the old part stops being planned and is burned off every ASL at the next AutoPilot run. Future demand is redirected up-chain.
  - **Alternate**: one-way. The newer part may serve the older part's need once the older part's stock/forecast is burned off. The older part may borrow the newer part's SS in an emergency. Has Part Procurable/Repairable flags plus ASL Retention Min Inventory/Forecast (below either → ASL removal recommended).
- Roll-up flags (Replace only):
  - Roll Up Good: down-chain good stock counts toward the up-chain part.
  - Roll Up Bad: down-chain bad stock / in repair counts.
  - Roll Up Good As Bad: down-chain good stock counts as up-chain bad (rework/upgrade needed).
  - Roll Up Demand Percent: for Replace, the non-rolled remainder is dropped; for Alternate, it stays with the down-chain part.
- Future Part Chains (FUTURE_PART_CHAINS=true): Effective Date = Available Date − LT − Buffer Days for Future Chain Parts. Sync DB adds the chain on that date. — HC/glossary/part_chain_2.html
- A part belongs to one chain per location.
- IO process "Run Supercession Changes" merges child SKU overrides into the TMR (top-most revision) part: max of Min overrides, min of Max/Fixed overrides. The child's override end-dates are set to yesterday. — HC/glossary/autopilot_processes_8.html
- **Part Substitution** (non-chain): substitute part, Global or per-location, Priority (lower = first, negatives allowed, null last). Needs Enable Part Substitution. — HC/parts/parts_pid/pid_new_edit_part_substitution_page.html
- Part Health reports Acquired/Relinquished Chain Transfer and Substitution quantities. — HC/core/core_pid/pid_part_health_page_summary.html

## 6. Order lifecycle
- **Order Status**:
  - Planned (OP recommended)
  - Ordered (uploaded, then re-downloaded from host as approved)
  - Planned (On Hold)
  - Ordered (On Hold)
  - Closed: OP ignores it; it can't be cancelled; host-owned, deletable only in the host.
  - Planned and Ordered both count as open.
  - Source: HC/glossary/order_status.html
- **Order Planned** code: **Current** (host-updated, read-only), **Planned** (Servigistics recommended), **User** (planner-added or edited). Global settings: PWS_EDIT_CO_ORDERS (edit "c/o" = Order Planned c + Status o host orders; default true); ALLOW_MASS_APPROVAL_TO_CO_ORDERS (default false on upgrade / true on new install). — HC/parts/parts_pid/pid_new_edit_order_page.html; HC/glossary/global_settings_sp.html
- **Approval Status**: Not Approved (a.k.a. Needs approval), Auto Approved, Manually Approved, No change from current order, Reviewed and no change to be made. — HC/glossary/approval_status.html
- **APPROVE_FOR_UPLOAD** (default **false**): two-stage approval, planner then a second planner. **PWS_UPLOAD** enables "Upload Data to Internal System" on IPWS / Procurement / Repair / Replenishment. User **Approve Limit** caps planned qty × price per order. Approve rights depend on location modify rights. — gs_sp; HC/glossary/approve_limit.html; HC/glossary/orders_7.html
- Upload flags:
  - Need to Upload: informational, cleared on upload.
  - Upload Action: Changed / Uploaded / Not Uploaded.
  - Uploaded Since Last Change: Yes/No.
  - After the host download, approved orders become Ordered and cancelled orders become Closed.
  - Sources: glossary need_to_upload, upload_action, orders_8
- Order date sets: Planned, Recommended, Effective (from the generated plan), Original (baseline), Actual (from host), On Hold. Action "Order Change" copies planned dates to original; "Status Update" does not. — pid_new_edit_order_page
- **Recommended Actions** (can combine): Alternate Transport Mode, Cancelled, Constrained (repl limited by source), Deferred, Supply Shipment Expedited, Group MOQ Order, Increased, Newly Created, Overdue, Reduced, Unchanged, Vendor Split, Within Lead Time. — HC/parts/parts_pid/pid_ipws_orders_section.html
- **Locks and holds**:
  - Order Plan Locked: AutoPilot won't modify the order.
  - Lock Until Date + Locked By Planner: no change before that date.
  - On Hold Until Date: on expiry the order becomes regular if it has planned values, else it is deleted. Hold Quantity is editable except on repair orders.
  - SKU-level Hold Plan Until: no OP at all; existing orders untouched; unapproved orders must be deleted manually; auto-approval still runs; don't use on replaced parts.
  - SKU-level Hold New Orders Until: plan is visible but no new orders.
  - Hide Until: hides the SKU from IPWS.
  - Sources: glossary order_plan_locked, lock_until_date, on_hold_until_date, hold_plan_until, hold_new_orders_until; orders_2..6
- Other order flags: Count in Order Plan, Count In Netting, Life Cycle Order (constrained by lifecycle params), Purchase Agreements / Purchase Requisitions counts. — ipws orders
- **Purchase Order Agreements**: Host PO number, Effective/End Date, Min Order Qty, Pallet Qty, PO Quantity (max units), PO Type (Limited / Unlimited / One Time), Reference Unit Cost, order type, vendor location. Percent of Business is unused. Review reasons: 30 No Valid Purchase Agreement, 85 cancellation requisitions need approval. — HC/parts/parts_pid/pid_purchase_order_agreements_page.html
- **Vendors**:
  - Hierarchy: Vendor → Vendor Location(s) → Vendor Location SKU Lead Time.
  - Lead time record fields: Processing Length/SD, Transport Length/SD, Ordering/Transport Calendar, Block Auto Approvals, Fixed Order Size, Min Days Closed To Spread / Spread Length, Transport Cost, Order Limit Period 1–3, Packaging/Pallet Size (+ round 0–1), Min Order Value, Lock Status, Percentage Split, Min/Max Order Qty.
  - Source: HC/parts/parts_pid/pid_new_edit_vendor_location_sku_lead_time_page.html
- **Price breaks**: Vendor Location Part/SKU Price Break by order type (Procure/Repair/Replenish), Lower/Upper Bound, Unit Cost. — pid_new_edit_vendor_location_part_price_break_page.html
- **Vendor Split** (AutoPilot proc 1198, hidden by default, runs after Generate OP; today's orders only):
  - Splits by Percentage Split (must sum to 100) and Max Order Qty, and respects Min Order Qty (blank = 0).
  - Leftover goes to the primary vendor even above its max.
  - Source: HC/parts/parts_topics/splitting_orders_by_vendor.html
- **Vendor Group Min Order Quantity**: one segment per group; trigger-point SKUs only (time-phased ignored); segments should be mutually exclusive (overlap → highest ID wins plus a review record).
  - If any SKU has a procurement order today, all SKUs in the group are ordered to reach the group MinOQ. Group Auto-Approved overrides Allow Auto Approval.
  - Source: HC/glossary/vendor_group_min_order_quantity.html
- **Vendor Capacity** (TPROP only): monthly capacity per vendor location SKU, a priority list of vendors, uses OP_VENDOR_CAPACITY_DATE_INDEX. — HC/glossary/vendor_capacity*.html
- **Vendor Programs**: program → vendor location, Global Part List, minimum Cost/Weight/Point/Lot limits ("Absolute", Minimum 2–5 in Procurement by Vendor). — pid_new_edit_vendor_programs_page / _program_limits_page

## 7. Last Time Buy (LTB)
- Trigger: product EOP or vendor discontinuation. Modes: **Top-down** (global LTB at one location, then allocated to regions) or **Bottom-up** (each region independently). Forecasting uses profiles, so no install base is needed. — HC/glossary/last_time_buy.html
- 8 workflows (HC/glossary/last_time_buy_2.html):
  1. Profile mgmt: parameter sets → profiles (system-generated, user-created or imported) → approve
  2. Optional Shipment Service Factor profiles (SBLI forecast)
  3. Identify via the LTB Work Queue
  4. LTB Forecast, EOP → End of Service
  5. Decay-rate schemes
  6. Recommendation
  7. Monitoring through Review Board Lifecycle tab records
  8. Re-enable LTB for SKUs
- **Profile Parameters** (cluster analysis of parts that completed their life cycle): Horizon Begin (−slices before EOP), Horizon End (+slices), Iterations, Max Distance Criteria %, Min SKU per Profile, LTB Date Setting (LTB Date / First Demand Slice), Approval All, Profiling vs Forecasting segments. — HC/parts/parts_pid/pid_new_edit_ltb_profile_parameters.html
- **LTB Parameter Set** (HC/parts/parts_pid/pid_new_edit_ltb_parameters_set_page.html):
  - Significance Level: profile significance in regression.
  - Allow Negative Coefficient: only if LTB_REGRESSION_FORCE_NO_INTERCEPT.
  - Shipment Based Forecast Weight; Regress on SBLI (Exclude / Include / Enforce); Failure Rate Calculation Window.
  - Auto-approve LTB Forecast / Order.
  - Regression Demand History Method: **Full History (default)** / Fixed Length (+ Demand History To Use slices).
  - Regression Alignment: Best Search / End of Production.
- Forecast = regression of pre-EOP demand against the selected approved profiles. The planner adjusts per slice by % or amount. — HC/glossary/last_time_buy_3.html
- **Decay Rate Parameters** (HC/parts/parts_pid/pid_new_edit_ltb_decay_rate_parameter_page.html):
  - Override Decay Rate.
  - Decay Start Slice: fixed slices from Support-To; overrides Decay Start Date.
  - Slice Number: history slices for the Slice Decay Rate.
  - Calculation Type: Slice (per part) / Actual (don't use pre-LTB) / Group (segment average, with Group Type Slice or Actual).
- **LTB Recommendation page — General tab** (HC/parts/parts_pid/pid_ltb_reco_page_general_tab.html):
  - Dates: LTB Date (last procurement date), Decay Start Date, Field Support-To Date, Support To Date.
  - Rates and inputs: Return/Repair Wash Rate, Salvage Rate, Slice Forecast Decay Rate; LTB Slice Decay Rate (history window ending at min(today, Support-To) − Slice Number); LTB Actual Decay Rate (Decay Start → min(Support-To, today); only once status is Done); Decay SD.
  - Notification limits: Monitor To Date, High/Low Limit %, Early Used Up Limit (days before end of service → review), Excess at End (units).
  - **Total Forecast** = cumulative LTB forecast from LTB Date to End of Support. After Decay Start, each period = previous × (1 − Slice Forecast Decay Rate).
  - **Need = Total Forecast − Total Repair Forecast − Current Inventory Balance − Roll Up Inventory** (child locations).
  - Excess Used (±, borrowed from or given to chain parts); Recommended Quantity (overridable); Excess Not Used.
  - LTB Method: Global LTB (no other location can plan) + Allocate To Locations (Allocation tab, replenishment distribution); Global LTB Quantity.
  - **LTB Status**: Not Approved → Approved (not complete) → Done.
  - Other tabs: Allocation, Decay Rate, Part Chain, Part Shipment, Product, Total LTB.
- AutoPilot Lifecycle processes: Calculate Decay Rate, LTB Forecast, LTB Recommendation (for Approved records; also generates LTB review records), Lifecycle Analytics. — HC/glossary/autopilot_processes_4.html
- Review reasons (Lifecycle): 65 LTB usage rate > alert, **80** actual inventory > projected max, **81** < projected min, **118** Earlier Used-up Date (projected 0 before Support-To), **119** Significant Excess at Support-To, **120** LTB Follow Up (approve plan or procurement). — HC/glossary/review_reason_2.html
- LTB Work Queue fields: Allocation %, Inventory Difference Limit (end-of-support difference → notification), Monitor High/Low, Current Month Number, decay rates. — HC/parts/parts_pid/pid_ltb_work_queue_page.html
- Life Cycle Management covers New Product Introduction and leading-indicator data, not LTB. — HC/glossary/life_cycle_management.html

## 8. Planner workflow and tools
- **Planning by Exception (Daily Planner)** — HC/process/workflow_daily_planner.html. Premise: most recommendations are auto-approved; the planner works exceptions. Work Queue and Review Board configuration is a one-time, per-user setup.
  1. Start on **Planner 360°**.
  2. Preferred path: the Top Work Queue Items container → IPWS for the top SKU. Alternate path: the Part Based WQ Summary (top 5 review reasons) → Work Queue → IPWS.
  3. On IPWS:
     - a. Review the Part Health tab.
     - b. Review the Review Board container.
     - c. Deployments: top location, Display Planned Locations, Show Total, date range. Compare OHG vs levels for 7 days; check Proc Order vs Repl Sent/Received; check excess.
     - d. Orders container: sort by Available Date. Check Rec Qty / Avail Date / Order Date against the Time Series Graph/Grid (OH vs ROP). Adjust, repeat for balancing / excess / repl / repair orders, then approve.
     - e. Review Board: optional custom delay; **Part Reviewed** (preferred, all locations) or **SKU Reviewed**, which sets Delay Until = today + Delay Days.
     - f. Journal note.
     - g. Save.
     - h. Next SKU.
- **Detailed SP Ordering Workflow** (a supplement to that step) — HC/process/workflow_detailed_supply_planning_ordering.html: Orders with Date Range = None. Check in order:
  1. Repl/Balance/Excess types: can network excess cover the need?
  2. Procurement.
  3. Repair: is there enough repairable material?
  Then adjust and set the date range around the order date.
- **Planner 360°** containers: Backorder, Order Summary, Spend History, Supply Chain View (counts of repair etc. per location), Top 10 BO, Top 10 Review Reasons, Top WQ Items, WQ Summary. Date Type filter (Ordered / Shipped / Received / Avail) evaluates recommended, actual, effective, on-hold and planned dates in turn. Right: "Planner 360°/Part 360°/Part Health". Global setting ENABLE_DASHBOARD_CACHE. — HC/core/core_smart_help/sh_planner_360_page*.html
- **Part 360°** (part KPIs) and **Part Health** (only via tabs): part-level supply over time, network need, procurements and repairs, excess/shortage/imbalance vs min/max.
  - Summary fields: Net Requirement = (External Forecast + SO) − Good from Returns (NFF); Supply Chain Imbalance = Excess + Below SS; Inventory = OHG + On Order (proc/repair/repl/bal/recall); ordered qty by type; acquired/relinquished chain and substitution.
  - Global setting OP_GENERATE_ORDER_PLAN_PART_HEALTH_DATA.
  - Sources: HC/core/core_smart_help/sh_part_health_page.html; HC/core/core_pid/pid_part_health_page_summary.html
- **IPWS** tabs: Part 360°, Part Health, Plan, Forecast.
  - Plan containers: Alerts, Daily Detail IP Report, Demand/Forecast (Detail/Summary/Graph), Deployments, Forecast Parameters/Metrics, Inventory Position (+Summary), Journal, Order/SKU Parameters, Orders, Part Chain Details, Part Kit Details, Review Board, Time Series Graph/Grid, Used In Part Kit.
  - Deep link: `/WebUI/Pws.mvc?hostPart_toSelect=..&hostLocation_toSelect=..`.
  - Order/SKU Parameters include Need To Plan, Hold Plan/New Orders Until, Hide Until, Last Planned Date, Order Last Reviewed By/Date, Planner Code/Name, Primary (Repair) Vendor Location.
  - Sources: HC/glossary/interactive_planner_worksheet.html; HC/parts/parts_pid/pid_ipws_order_sku_parameters_section.html
- **Work Queue** fields: Priority (per review type, from Review Subscriptions), Delay Until Date, Magnitude Value = Part Cost × Magnitude, Total Forecast Cost ranking, Planner Code/Name. — HC/parts/parts_pid/pid_work_queue_page.html
- **Planner Code**: defined on the Planner Code page, assigned to parts, then to planners; drives responsibility and coverage. — HC/glossary/planner_code.html
- Rush/emergency orders: **no dispatch/rush order type exists** in SP. Emergency handling = expedite recommendations (SCS), ATM (alternate transport mode), Alternate chain borrowing of SS, and IO emergency locations/fill rates (IO module). Grep of "rush order"/"emergency order" found only IO/scenario pages. **UNVERIFIED** that nothing else exists.
- The FAQ lists SP how-tos: vendor capacity, hold, lock, ATM, ASL check, and configuring/sorting the work queue and review board. — HC/process/faqs.html
