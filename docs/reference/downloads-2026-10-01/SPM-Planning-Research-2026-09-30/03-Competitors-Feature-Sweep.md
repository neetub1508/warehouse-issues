# 03 — Service Parts Planning (SPP) Competitors to PTC Servigistics

Research date: 2026-09-30. Scope: vendor features, methods, differentiators and small details a mid-market service-parts product can learn from.

**Conventions**
- Every claim carries a source URL. Where a claim comes only from a third-party review, an aggregator, or my inference, it is tagged **UNVERIFIED**.
- Pricing figures from review aggregators (Capterra/GetApp/vendorbenchmark etc.) are always **UNVERIFIED**: they are often stale or estimated.
- Several third-party comparisons used below are written by **Lokad**, which is itself a competitor. Its rankings are opinion, not fact. I use them for architecture and acquisition facts and label their opinions.
- "Not found" means the research did not surface it. It does not mean the vendor lacks the feature.

---

## 0. Executive digest

| Theme | What the market does | Who does it best / most visibly |
|---|---|---|
| Forecasting intermittent demand | Croston / SBA / TSB is the baseline. Leaders produce a **full demand-over-lead-time distribution** (bootstrap, Monte Carlo, Poisson/compound) | Smart (patented bootstrap), ToolsGroup (probabilistic), Lokad (demand + lead-time distributions) |
| Inventory optimization | Service-level target → ROP/OUL/SS, or **total-cost / economic** optimization (stockout penalty vs carrying) | Baxter (TCO), Lokad (ranked economic purchase list), GAINS (cost/profit) |
| Multi-echelon | MEIO co-optimizes service targets across tiers; demand propagation must account for downstream MOQ "lumpiness" | Syncron, ToolsGroup, Servigistics, SAP IBP |
| Lifecycle | Supersession chains with demand inheritance, phase-in/phase-out, last-time-buy (LTB), EOL excess | Syncron, ToolsGroup, Baxter, SAP SPP |
| Repairables | Returns forecast, repair yield/scrap, repair lead time, repair vs buy | Oracle SPP, Baxter, GAINS, ToolsGroup, Smart |
| Automation | Auto-confirm orders unless a **blocking rule** fires; **policy-change approval** with auto-approve rules; **policy smoothing** | Syncron (most explicit), Slim4 (manage-by-exception), Intuiflow Autopilot |
| Dealer network | OEM-run dealer stocking (RIM): nightly DMS feed → OEM computes min/max → auto stock order; OEM-guaranteed returns for recommended parts | GM RIM, Syncron Dealer Parts Planning (RIM), CDK/Reynolds phase-in/out |
| Pricing | Cost-plus / value / competitor; kits; supersession pricing; harmonization vs grey market | Syncron Price, Servigistics pricing, ToolsGroup (Evo) |

---

## 1. Vendor profiles

### 1.1 Syncron (Sweden; OEM aftermarket specialist)

**Company and segment**
- Founded in 1990 in Stockholm. Summit Partners took a $67M minority stake in 2018. It merged with **Mize** (warranty and field service, Tampa) in 2021, taking revenue beyond $60M. New CEO Josh Weiss from April 2025. Source: https://en.wikipedia.org/wiki/Syncron_(company)
- Mize brought warranty, service contracts, field service, depot repair and knowledge management. Mize's founder became CPO. Sources: https://www.syncron.com/blog/mize-merges-with-syncron , https://www.summitpartners.com/news/syncron-and-mize-join-forces-to-deliver-the-industrys-first-connected-service-experience
- Target segment: OEMs in automotive, industrial machinery, construction/mining and agriculture. Source: https://en.wikipedia.org/wiki/Syncron_(company)
- Price tier: enterprise SaaS. The reported ~$144.5M revenue for 2024 and 821 staff are **UNVERIFIED** (https://getlatka.com/companies/syncron.com/funding). **Price IQ** is marketed as a mid-market pricing product (https://www.syncron.com/solutions/parts-pricing).
- Product families: Parts Planning (Inventory), Dealer Parts Planning (RIM), Price, Uptime (predictive maintenance), Warranty. Source: https://www.lokad.com/review-of-syncron-com/ (third-party).

**Parts Planning modules.** All from the official scope document (Feb 2025): https://www.syncron.com/hubfs/Syncron_2025/Document/Syncron_Parts_Planning_scope_Feb_7_V1.1.pdf

*Base package: forecasting, inventory optimization, replenishment, reporting, configuration*
- **Demand forecasting**
  - Automatic periodic time-series forecast per **location-unique item**, governed by a **forecasting parameter set**. Each item can use different settings.
  - Manual or imported **forecast adjustments**.
  - **Replacements and demand inheritance**: demand history from a replaced item propagates to its replacement (supersession).
  - **Market volume density profiles** that scale future periods.
  - Automatic **individual and group seasonal profiles**.
- **Inventory optimization**
  - Each item is assigned, by configurable rules, to exactly one **inventory policy**. The policy decides *whether to stock* and at *what target service level*.
  - **Target service level optimization** runs under constraints and an "optimization mode".
  - Outputs per item-location: stocking decision, target SL, **order level**, **buffer stock** and **optimal order quantity**.
  - **Delivery mode optimization** per supplier.
  - **Central and local item overrides**.
  - **Critical stock lists**: initial/critical items with minimum order levels.
  - **CO2 emission simulation** of transport.
- **Stock replenishment**. Order types are generated separately:
  - **Refill** orders (effective stock hits the order level)
  - **Rush** orders (reacting to a detected *risk of run-out*)
  - **On-demand** orders (for *non-stocked* items that have a backorder)
  - **Manual** orders
  - Full replenishment history is kept.
  - **Ordering calendars / schedules** apply.
  - Confirmed orders are exported to the ERP/OMS.
- **Reporting**: Summary, standard KPIs (service level, stock value), Item alerts, Item report with **mass update**, Demand transactions, **Excess stock**, **Stock Health**, and **Risk of Run-out** as an actionable list.
- **Configuration**
  - Forecasting and replenishment parameter sets.
  - **Dynamic parameter-set assignment rule framework**: rules assign parameter sets and policies to items.
  - Warehouse defaults, supplier defaults, inventory policy configuration.
  - **Demand stream configuration**.
  - Currencies and FX.

*Planner automation*
- **Auto-confirmation** of recommended order lines, configured **per warehouse × supplier**.
- **Order-blocking parameter sets**, assignable to warehouses, suppliers per warehouse, or policy "picks classes". Lines that match a blocking rule go to a human.
- **Replenishment Policy Approval (RPA)**: planners review *policy* changes (order level, order quantity, stocking decision) before they take effect.
  - Simple or advanced **auto-approval rules** decide which changes need review.
  - **Replenishment policy smoothing** phases in big changes so planners and suppliers are not flooded on go-live day.

*Supplier collaboration*
- **Delivery monitoring**: open POs at risk of run-out, ETA updates, expediting. Suppliers log in to respond.
- **Purchase-order forecasting**: an item order schedule. **Order fill-up** tops up orders to meet supplier order-value minimums, bonus targets or container sizes.
- **Return order management**: return lines for excess/obsolete stock are created automatically on a schedule or on demand. Returns can be **guaranteed or non-guaranteed** per supplier agreement.
- **Supplier load levelling**: caps order *lines per weekday* per supplier location. Order suggestions are prioritized by **service contribution**.

*Global parts planning*
- **Demand/forecast propagation**
  - Supplying warehouses aggregate POS demand from some customer warehouses and forecasts from others.
  - Demand propagates down BOMs (assembly → components).
  - Probabilistic forecasting **accounts for expected downstream order sizes (MOQ/EOQ)**, because propagated demand looks smoother than it really is.
- **MEIO**: co-optimizes service levels across tiers. Lower upstream SL raises downstream effective lead time. Vendor claim: up to 30% less inventory and +5 SL points.
- **Internal stock redistribution**: redistribution is proposed as an *alternative* line to a refill or rush order. It is governed by **redistribution regions, pairs** and settings.
- **Item locator (parts locator)**: finds stock at other *dealer* locations by **straight-line distance** and shows contact details.
- **Virtual planning**
  - A virtual location holds stock for a region. Demand and stock are aggregated before optimization.
  - Orders land at a predetermined or dynamically chosen physical site.
  - Used for slow movers that no single site would stock.
  - Requires redistribution.
- **Warehouse clustering**: similar warehouses are grouped. Items are classified by cluster-level demand into Fast/Medium/Slow **cluster movement types**, which drive parameter sets. The rationale: a local sale of a cluster slow-mover is more likely coincidence.
- **Planned events**: event lines link items to future events. Ordering runs **ALAP or ASAP** before the event. Events can be imported from file.

*Advanced prediction*
- **Causal forecasting** using running hours and **MTBF**.
- **Installed-base forecasting**: forecast scales with installed units, propagated through BOM.
- **Connected products**: the GPS position of machines maps them to the nearest warehouse. Forecasts update when a machine moves service area.

*Other modules*
- **Replay Simulator**: re-simulates history with a new configuration, mirroring production with auto-confirmation.
- **Insights BI**: override/compliance analytics (impact of user overrides), supplier performance, warehouse comparison, service level and backorder root cause.
- **CSX Data Central**: data products. The **AI Premium** tier adds Python notebooks and **Text-to-SQL**. **Managed Exports** is a service.
- **ML Forecasting**: an ML model trained on customer data to improve *point* forecast accuracy.

**Dealer Parts Planning / Retail Inventory Management (RIM).** Source: https://www.syncron.com/solutions/retail-inventory-management
- The OEM sets **stocking policies per dealer location**.
- Dealer **POS data extract** covers sales, stock and orders. Integrations are claimed with **100+ DMS**, including CDK Global and KARMAK.
- **One-click approval becomes an automated order**. The target is **~15 min/day** of dealer planning time.
- **Recommended "smart returns"** with policy enforcement to limit buy-backs.
- **Dealer-to-dealer transfer** of unsold stock.
- Stocking logic for initial and critical stocking, and return logic synced with replenishment. Source: https://www.syncron.com/solutions/retail-inventory-management (via search summary, **UNVERIFIED** wording).
- Claimed results: +20% availability, −20–30% dealer network inventory, −15–40% emergency orders (vendor claim).
- Ford extended its relationship with Syncron for RIM: https://www.syncron.com/press-releases/ford-extends-its-relationship-with-syncron-to-improve-spare-parts-availability-and-fill-rates-leveraging-retail-inventory-management

**Price.** Source: https://www.syncron.com/solutions/price
- Pricing methods: cost-plus, value-based and competitor-based.
- **Kit pricing**, **lifecycle pricing** and **supersession pricing**.
- **Price harmonization** rules to limit grey market and cannibalization.
- Price-volume mix analysis and pricing simulations.
- **Approval workflows**.
- AI segmentation of parts and customers.
- Uses stocking and warranty-claims data.
- **Elasticity charts** (https://www.syncron.com/blog/new-ai-machine-learning-capabilities-for-syncron-price).
- **Price IQ** is the mid-market offering.

**Uptime**
- ML on sensor data for anomaly detection and failure prediction, with prescriptive maintenance. Source: https://www.syncron.com/press-releases/syncron-uptime-accelerates-manufacturers-transition-from-after-sales-service-to-products-as-a-service-paas
- Ashok Leyland connected-vehicle deployment: https://www.dcvelocity.com/articles/53870-syncron-ashok-leyland-partner-to-propel-transformation-for-predictive-vehicle-maintenance-solution

**Architecture notes.** Lokad's review, **UNVERIFIED** and written by a competitor, claims:
- Inventory and Price use separate databases.
- The optimization engine is black-box.
- Rotable tracking is weaker out of the box.

Source: https://www.lokad.com/spare-parts-optimization-software/

**Acquisitions and consolidation**
- The only confirmed acquisition is **Mize (2021)**.
- An "M&A offer April 2025" signal exists but is **UNVERIFIED** (https://getlatka.com/companies/syncron.com/funding).
- I found no evidence of a "Syncron Supply Chain" acquisition.

**Small details to steal**
- Order types are split into refill, rush and on-demand.
- Blocking rules sit on top of auto-confirm.
- Policy approval and smoothing.
- MOQ-aware propagation upstream.
- Straight-line parts locator.
- Cluster movement classes.
- ALAP/ASAP event ordering.
- Replay simulator.
- Override-impact analytics.

---

### 1.2 Baxter Planning — BaxterPredict / BaxterProphet (US; high-tech & med-device service)

**Company and segment**
- Segment: high-tech, medical devices, industrial equipment, aerospace, energy. Customers include Avaya, Ciena, Extreme Networks, NetApp and Bio-Rad. Source: https://baxterplanning.com/who-we-serve/ (via search summary)
- Roche Diagnostics selected the platform: https://www.prnewswire.com/news-releases/baxter-plannings-predictive-service-supply-chain-platform-chosen-by-roche-diagnostics-corporation-for-service-supply-chain-optimization-301932163.html
- Acquired **Entercoms' Supply Chain Technology unit on 2021-11-02**, bringing predictive and patented visibility tech: https://www.prnewswire.com/news-releases/baxter-planning-acquires-business-unit-from-entercoms-and-extends-predictive-service-supply-chain-offerings-301414225.html
- Pricing is subscription, based on users, parts and modules (**UNVERIFIED**, https://www.peerspot.com/products/baxter-planning-reviews).
- **Planning-as-a-Service (PaaS)** combines outsourced planners with the software. Source: https://baxterplanning.com/platform/ (via search summary, **UNVERIFIED** wording)

**Modules.** Source: https://baxterplanning.com/platform/planning-prophet/
- **DC planning**
- **Repair planning**
  - Prefers repair over new buy.
  - Forecasts defective returns, **scrap rates** and throughput.
- **Field planning**
  - MEIO.
  - Replenishment plus **redeployment** of excess.
- **Technician stock planning**
  - Allocation by **installed base and skill mapping**.
  - Adapts to routes.
  - Reallocates on workforce change.
- **Budget planning**
  - Scenario modeling of service-level impact.
  - Plan vs actual spend by region.
- **Supplier web portal** covering orders, repairs, shipments and alerts.
- **Lifecycle**
  - NPI.
  - **Last-Time-Buy (LTB)**.
  - EOL.
- **Excess management**
  - Utilize, sell or dispose.

**Methods**
- **Total Cost Optimization (TCO)**. Target stock is computed by trading off:
  - stockout costs: **service penalties, expedited freight, lost sales**
  - against carrying cost, order cost, forecast and **outlier demand**, and lead time.
  - **Part, site and customer criticality attributes** feed the targets.

  Sources: https://baxterplanning.com/platform/planning-prophet/ , https://info.baxterplanning.com/smarter-service-parts-planning
- **Backlog Criticality Index (BCI)** drives deployment decisions.
- **Service-contract-aligned network rules** map demand to sites.
- Forecasting combines history with **service-contract projections**.
- Forecasting also supports failure-rate × installed base, per Lokad (**UNVERIFIED**): https://www.lokad.com/spare-parts-optimization-software/
- KPIs: fill rate, service level, **hit rate**.

**Integration and deployment**
- APIs plus batch.
- SAP, Oracle and **ServiceNow**.
- Cloud, SOC 2, ISO 27001, GDPR.

Source: https://baxterplanning.com/platform/planning-prophet/

**Small details to steal**
- Stockout cost is modeled as three named buckets (penalty, expedite, lost sale).
- Backlog-criticality index for deploying scarce stock.
- Technician-skill-aware van stock.
- Budget-planning module that ties inventory to finance.

---

### 1.3 ToolsGroup — Service Optimizer 99+ (SO99+) (Italy/US)

**Company and segment**
- Distribution-heavy verticals: automotive aftermarket, MRO, pharma, industrial wholesale. Source: https://techvendorindex.com/software/supply-chain-management/toolsgroup-so99/ (**UNVERIFIED**)
- Acquisitions:
  - Mi9 Retail demand management (formerly **JustEnough**), 2021
  - **Onera**, 2022
  - **Evo** (pricing/inventory prescriptive AI), 2023

  Sources: https://www.toolsgroup.com/news/toolsgroup-acquires-evo-for-industry-leading-responsive-ai/ , https://www.toolsgroup.com/news/toolsgroup-acquires-onera-to-extend-retail-platform-from-planning-to-execution/
- Price tier (**UNVERIFIED** benchmark): Demand Planning $100K–250K/yr; Demand + Inventory $250K–600K/yr; full suite $600K–2M+/yr. Priced by SKU-location count, planners and modules. Source: https://vendorbenchmark.com/vendors/toolsgroup-pricing

**Methods and features**
- **Probability forecasting** produces a range of outcomes with probabilities. It is designed for long-tail and intermittent demand.
- A **stock-to-service curve per SKU-location** optimizes the portfolio service mix.
- The user specifies the service level and the system meets it at lowest stock.

  Source: https://www.toolsgroup.com/wp-content/uploads/2019/06/ToolsGroup-Service-Optimizer-99.pdf
- Aftermarket page. Source: https://www.toolsgroup.com/industries/aftermarket/
  - Range-based probabilistic forecasting that "handles zero-demand periods without inflating safety stock".
  - Service-driven MEIO: central → regional → depot → local service point.
  - **Inventory-aware price optimization** through end of life.
  - **Lifecycle and LTB control**: phase-in, phase-out and supersession scenarios. **Optimal LTB quantity** from holding cost and projected demand.
  - **Repairables and returns**: return flows are forecast probabilistically, and refurbished stock is treated as planned supply aligned to repair lead time.
  - Automated replenishment across hundreds of thousands of SKU-locations.
  - What-if planning with financial impact.
  - Pre-built SAP, Oracle and Dynamics connectors.
- Uses Croston variants and Monte Carlo, per Lokad (**UNVERIFIED**): https://www.lokad.com/spare-parts-optimization-software/
- Demand Collaboration Hub, S&OP and promotion planning (brochure).

**Small details to steal**
- The stock-to-service curve as a *UI artifact*: show the planner the marginal inventory cost of each SL point.
- LTB quantity recommendation.
- Returns treated as planned supply.

---

### 1.4 GAINSystems — GAINS (US; cost/profit optimization, MRO-strong)

**Company and segment**
- Service parts and MRO: utilities, GE Power, aviation.
  - GE Power case study: https://gainsystems.com/case-study/ge-power/
  - Gartner "Notable Vendor" in the spare/service parts context of the 2022 SCP Magic Quadrant: https://www.globenewswire.com/news-release/2022/10/03/2527208/0/en/GAINSystems-Named-a-Notable-Vendor-in-the-2022-Gartner-Spare-Service-Parts-Context-Magic-Quadrant-for-Supply-Chain-Planning-Solutions.html
- Price tier: not found (**UNVERIFIED**, mid/upper enterprise).

**Features.** Source: https://gainsystems.com/solutions/service-parts-mro/
- Independent demand forecasting and lead-time prediction.
- MEIO and **store-level optimization**.
- **Dynamic redistribution for condition-based planning**.
- **Item supersession**.
- BOM planning.
- **Part/repair process optimization** and **repair capacity optimization**.
- **Rotables**.
- **Preventive/predictive maintenance planning**.
- **OEM vs PMA parts** preference and multi-source handling.
- Inventory classification.
- Item deployment and **service-level policy optimization**.
- Exception monitoring for stockouts, late deliveries and quality issues.
- **"DEO Agentic Agent"** for supply decision automation.
- **GAINS Connect API**. The platform is ERP-agnostic, **SAP- and Oracle-certified**.
- Blends time-series with **Weibull reliability** modeling. Total cost covers holding, ordering, backorder and capacity. Source: Lokad review (**UNVERIFIED**), https://www.lokad.com/spare-parts-optimization-software/

**Small details to steal**
- OEM vs PMA (approved alternate-source) part preference: in automotive terms, OEM vs aftermarket/OES alternate.
- Repair *capacity* as a constraint, not only repair lead time.

---

### 1.5 Smart Software — Smart IP&O (US; SMB/mid-market, ERP add-on)

**Company and segment**
- Mid-market companies on Epicor (Kinetic, P21), Sage, NetSuite, Dynamics, SAP, IBM Maximo and Hexagon EAM. Source: https://smartcorp.com/spare-parts-planning-software-aftermarket-service/
- Price (**UNVERIFIED**, aggregators):
  - "from $695/month"
  - Small $2K/mo, Medium $5K/mo, Large $10K/mo (annual billing)

  Sources: https://www.capterra.com/p/175581/Smart-IP-O/ , https://softwarefinder.com/project-management-software/smart-ip-o

**Methods**
- **Patented bootstrapping**: US Patent 6,205,431 B1, the Willemain–Smart–Schwarz (WSS) method.
  - It resamples history to create tens of thousands of **demand-over-lead-time scenarios** with *no distribution assumption*.
  - It also gives a new way to assess forecast accuracy.

  Sources: https://smartcorp.com/wp-content/uploads/2015/07/IJF_Bootstrap_paper_Smart_Software.pdf , https://www.sciencedirect.com/science/article/abs/pii/S016920700300013X
- The method is academically contested. There are published letters criticising the patented bootstrap: https://www.researchgate.net/publication/4960497_Comments_on_a_patented_bootstrapping_method_for_forecasting_intermittent_demand_multiple_letters
- Croston is available in SmartForecasts. Source: https://softwarefinder.com/project-management-software/smart-ip-o (**UNVERIFIED**)

**Features.** Source: https://smartcorp.com/spare-parts-planning-software-aftermarket-service/
- Min/Max and ROP recommendations.
- Safety stock.
- **Service level vs cost trade-off**.
- What-if **optimization workbench**.
- **Repair-and-return simulation**: wait for repair vs buy more.
- **Capital budgeting**: project-based planned plus unplanned demand.
- Network balancing.
- Extends Epicor Kinetic min/max with policy write-back: https://smartcorp.com/blog/extend-epicor-kinetic-forecasting-min-max-planning/

**Small details to steal**
- The **"ERP overlay" model**: compute the policies, then write min/max/ROP back into the ERP's native fields. Low integration cost is the key reason mid-market buyers pick it.
- Consumable vs repairable split: https://smartcorp.com/intermittent/planning-for-consumable-vs-repairable-parts-spare-aftermarket/

---

### 1.6 Lokad (France; "quantitative supply chain", programmable)

**Company and segment**
- Aviation MRO, aerospace, distribution and retail.
- Pricing: a **fixed monthly fee** made of a platform fee plus a support fee for dedicated **Supply Chain Scientists**. Premier plans start at **$2,500/month**. Sources: https://www.lokad.com/contractual-agreement/ , https://www.lokad.com/inventory-optimization-as-a-service

**Methods**
- **Probabilistic forecasting** of demand, **lead time** and **scrap**. It forecasts all futures with probabilities.
- **Differentiable programming** and **stochastic discrete descent**.
- Combines OEM reliability data (**MTBUR**) with operator removal history, weighting whichever predicts better per part.

  Sources: https://www.lokad.com/aviation-mro-optimization-software/ , https://www.lokad.com/stochastic-discrete-descent/
- **Prioritized inventory replenishment**: every *next unit* of every SKU is ranked in one list by expected $ reward, with purchases taken from the top down to the budget or constraint.
  - Reward = expected margin − expected carrying cost + **stockout cover**. The stockout cover is a "virtual" incentive expressing relative importance.
  - The ranking honours MOQs and volume discounts.

  Sources: https://www.lokad.com/prioritized-inventory-replenishment-in-excel-with-probabilistic-forecasts/ , https://www.lokad.com/inventory-optimization/
- **Rejects service-level targets and ABC classes**. It optimizes dollars of return per dollar of inventory.
- May decide *not* to stock and pay a premium when the need arises (AOG trade-off). Case: Air France Industries MRO, https://www.lokad.com/images/solutions/CASE%20STUDY-AF-MRO-final.pdf
- **Envision** DSL ("supply chain as code"). No acquisitions. Source: https://www.lokad.com/spare-parts-optimization-software/

**Small details to steal**
- A **single ranked purchase list with a cumulative-budget cursor**. It is easy to explain to finance and works with any budget cap.
- Lead-time *distributions*, not averages.

---

### 1.7 Blue Yonder (US; broad SCP suite)

- **Slow Mover Forecasting and Replenishment**. Source: https://info.blueyonder.com/retail-planning-category-management/what-is-blue-yonder-slow-mover-forecasting-and-replenishment
  - Croston / **SBA**.
  - Separates demand size from interval, so the forecast does not collapse to zero after zero periods.
  - **Automatic mode switching** when a SKU's velocity changes from fast to slow.
  - **Poisson-based SS** using an in-stock probability.
  - **Minimum presentation** quantities.
  - Risk-pooling at the DC with ship-on-demand to stores.
  - "Cash optimization" delays reorders to the latest feasible moment.
- **Distribution Planning for Aftermarket & Industrial Distributors**: multi-echelon positioning from central DC to regional DC to branch. Source: https://info.blueyonder.com/supply-chain-planning/what-is-blue-yonder-distribution-planning-for-aftermarket-and-industrial-distributors
- Classifies each SKU as **Smooth / Lumpy / Erratic / Intermittent** (Syntetos–Boylan quadrants) and picks the algorithm family per class (same source family; **UNVERIFIED** exact wording).
- Segment: large enterprise, retail and manufacturing heritage. Lokad calls it "not specialized" for spare parts (**UNVERIFIED** opinion): https://www.lokad.com/spare-parts-optimization-software/

**Small detail to steal**: the Smooth/Lumpy/Erratic/Intermittent demand-pattern classification (ADI × CV²) driving automatic method selection.

---

### 1.8 SAP — SPP (APO), S/4HANA eSPP, IBP

**SPP (SCM/APO) processes.** Source: https://help.sap.com/saphelp_SCM700_ehp01/helpdata/en/47/e12f019e014ac5e10000000a42189d/content.htm
- **Planning Service Manager (PSM)** is the batch orchestration of planning services.
- Forecast service covers the lifecycle **phase-in → phase-out**. It supports leading-indicator and historical methods.
- Inventory planning service computes EOQ and SS per location-product or via MEIO.
- **ABC classification**.
- **DRP**: planning horizons and stability, **pre-season SS**, supplier shutdown handling, virtual-order consolidation, **remanufactured product planning**, multi-sourcing with approval rules. Source: https://community.sap.com/t5/supply-chain-management-blog-posts-by-sap/sap-spare-parts-planning-spp-in-a-nutshell/ba-p/13235674 (via search summary)
- **Deployment**: distributes scarce incoming stock by **priority tiers, sequence rules and fair share**.
- **Inventory balancing**: generates *horizontal* (lateral) stock transfers within a **Bill of Distribution (BOD)**.
- **Surplus and obsolescence** evaluation criteria.
- **Product interchangeability** (supersession). Supersession only works where the BOD products use ROP planning (per community blog, **UNVERIFIED** constraint).
- Monitors: **SPP Alert Monitor**, Inbound Delivery Monitor, **Service Fill Monitor**, **Service Loss Analysis**, Supplier Delivery Performance Rating.

**S/4HANA extended SPP (eSPP).** Source: https://sapinsider.org/blogs/sap-s4hana-supply-chain-for-extended-service-parts-planning/
- Automatic best-fit model selection.
- Supersession-aware forecasting.
- **Stock / de-stock decisions** based on cost, demand regularity and customer requirements.
- DRP, deployment with priority and fair-share, inventory balancing.
- Network-wide SS optimization.

**IBP**
- 40+ algorithms, including **Croston**. Source: https://precisiontech.in/software/sap/sap-ibp/ (**UNVERIFIED**)
- **MRO sporadic-demand algorithms**.
- MEIO producing **time-phased safety stock** per node.
- Component SS derived from planned preventive and corrective maintenance and works programmes.

  Source: https://community.sap.com/t5/supply-chain-management-blog-posts-by-sap/integrated-business-planning-for-maintenance-repair-operations-mro-what-s/ba-p/13526371

**Critique**
- Lokad cites implementation struggles at Caterpillar, the US Navy and Ford (**UNVERIFIED**, competitor opinion): https://www.lokad.com/spare-parts-optimization-software/
- SAP learning describes aftersales SPP for automotive OEMs: https://learning.sap.com/courses/describing-sap-for-automotive-supply-chain-and-manufacturing/outlining-capabilities-of-aftersales-service-parts-planning

**Small details to steal**
- **Fair-share deployment** when supply is short.
- Explicit **stock/de-stock decision** as its own output.
- **Service Loss Analysis**: attribute each lost fill to a cause.

---

### 1.9 Oracle — EBS Service Parts Planning, Spares Management, Fusion Service Logistics, NetSuite

**Oracle SPP (EBS).** Source: https://docs.oracle.com/cd/E26401_01/doc.122/e48778/T515331T515335.htm
- Forecast basis: usage, shipment or returns history, or **installed base × average failure rate**.
  - *Traditional* mode uses an external demand planner.
  - *Inline* mode uses Demantra.
- **Forecasts defective returns**. Models **repair yield** and **repair lead time**.
- Depot repair flows: field-service flow and customer-return flow.
- **Supersession**: searches the supersession chain for on-hand and on-order supply. A **lower-revision defective can be repaired to satisfy higher-revision demand**.
- **Supply sourcing priority order**:
  1. on-hand at the demand org
  2. on-order at the demand org
  3. supersession parts
  4. then by sourcing rules: reallocation transfer of declared excess → supersession transfer → **repair defectives** → buy new
- Customizable exception and recommendation messages. Supplier capacity overload alerts.
- Network: external suppliers, external repair suppliers, internal depot repair, central warehouse (with optional central defective warehouse), regional warehouses and technician trunk stock.
- Inventory Optimization for SS is optional.
- Requires the MSO constraint engine licence.

**Oracle Spares Management.** Source: https://docs.oracle.com/cd/E18727_01/doc.121/e12789/T452145T453172.htm
- **Planner's Desktop**.
- Automated **min-max recommendations for technician trunk stock** and warehouses.
- **Usable vs defective sub-inventories** per technician. Service **debrief** auto-transacts usage and recovered defectives.
- Return of excess and defective parts to depots.
- Sharing inventory between technicians.

**Fusion Service Logistics.** Source: https://docs.oracle.com/en/cloud/saas/service-logistics/25c/fasgs/overview-of-service-logistics.html
- Technician **stocking locations**, each with a default sub-inventory.
- **Parts search sourcing sequence**: keeps searching until one location has *all* parts, whether from trunk stock or a site-dedicated location.
- Replenishment via the **Min-Max Planning Report**.

**NetSuite Demand Planning.** Sources: https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_N2290234.html , https://www.netatwork.com/blog/netsuite-erp-demand-and-supply-planning/
- Four projection methods: **linear regression, moving average, seasonal average (monthly only), sales forecast** (pipeline).
- Item demand plans feed the **Supply Planning Workbench**, which suggests PO/WO/TO.
- No intermittent-demand method, hence the overlays (Netstock, Smart, Slim4, Intuiflow) certified for NetSuite: https://www.netstock.com/blog/how-to-optimize-inventory-planning-with-netstock-and-netsuite/ , http://intuiflow.com/solutions/ddmrp-for-netsuite/

**Small details to steal**
- The **ordered supply-sourcing cascade** (on-hand → on-order → superseded → lateral excess → repair → buy).
- Usable/defective sub-locations per technician.
- "Find a location that has all parts" search.

---

### 1.10 Kinaxis — Maestro (formerly RapidResponse)

- **Concurrent planning**: always-on propagation and fast scenarios. Hosted on Google Cloud.
- Acquisitions: Rubikloud (2020), Prana (2020), MPO (2022).

  Source: https://www.lokad.com/review-of-kinaxis-com/
- **Spare parts management** solution: what-if scenarios, forecasting and inventory optimization, "track modifications and supersessions", order promising, logistics coordination. Source: https://www.kinaxis.com/en/solutions/spare-parts-management
- Primer articles: https://www.kinaxis.com/en/blog/service-parts-planning-101-part-1
- Depth of MEIO and intermittent methods: not found (**UNVERIFIED**).
- Segment: large enterprise (high-tech, aerospace, automotive).

### 1.11 o9 Solutions — Digital Brain

- **Enterprise Knowledge Graph**, a unified demand, supply, finance and commercial model, plus AI agents. Source: https://o9solutions.com/
- The aftermarket offer claims predictive maintenance plus inventory optimization, with telematics, weather and regional signals. Source: https://o9solutions.com/industries/automotive/automotive-oems ; search summary via https://www.lokad.com/automotive-aftermarket-optimization-software/ (**UNVERIFIED**)
- o9 is not a service-parts specialist; the aftermarket use is configured on the platform.
- Segment: large enterprise.

---

### 1.12 Slimstock — Slim4 (Netherlands; mid-market to enterprise distributors)

- **Management by exception**. Source: https://www.slimstock.com/faq/ (via search summary)
  - Continuously analyses all items, detects abnormal behaviour and surfaces only items needing attention.
  - Vendor claims up to 50% less planning workload. Source: https://www.slimstock.com/solutions/supply-planning-platform/ (via search)
- **Automatic demand classification**, with the forecasting method assigned per class.
- **Multidimensional ABC and XYZ**.
- **Differentiated service levels** by demand frequency, strategic importance and ABC.

  Source: https://www.slimstock.com/solutions/supply-planning-platform/
- Order advice. Source: https://www.slimstock.com/solutions/supply-planning-platform/
  - Honours MOQ, lead times and supplier conditions.
  - Fills orders to **real-time supplier constraints while prioritizing urgent items**.
  - Supplier profiles with rules and **closure types** (holidays).
  - Shipment consolidation.
  - Dynamic SS.
  - Multi-location balancing.
  - Promotions.
  - Allocation templates.
- Integration and deployment. Source: https://www.lokad.com/review-of-slimstock-com/
  - Certified D365 and NetSuite adapters.
  - ~700 API endpoints.
  - File and API exchange, with planned-order return to ERP staging.
  - Private multi-tenant SaaS or on-prem.
- Automotive case study: https://www.slimstock.com/blog/tackling-automotive-supply-chain-challenges-with-slim4-case-study-insights/
- Pricing: not found.

**Small details to steal**
- Supplier **closure types** (holiday calendars) feeding order timing.
- Order fill-up prioritized by urgency.

---

### 1.13 EazyStock (Sweden/UK, part of the Syncron lineage historically — **UNVERIFIED**; SMB/mid-market)

- **Classification matrix**
  - Multi-dimensional: demand value, sales frequency, **number of picks** and annual consumption value.
  - Gives **81 categories** instead of ABC's 3.
  - Service-level targets and SS are recommended *per matrix cell*, down to SKU.
  - **Reclassified daily**, with **alerts when an item moves between categories**.

  Sources: https://www.eazystock.com/blog/classifying-inventory-optimizing-stock-levels-business-central/ (via search summary), https://www.eazystock.com/blog/abc-xyz-analysis-for-inventory-and-how-can-it-add-value/
- **ABC–XYZ**: XYZ by coefficient of variation ((σ/μ)×100), with user-set boundaries; X/Y/Z map to low/medium/high SS. A **free ABC tool** is offered. Source: https://www.eazystock.com/blog/abc-xyz-analysis-for-inventory-and-how-can-it-add-value/
- Features. Source: https://www.capterra.com/p/135219/EazyStock/ (**UNVERIFIED**)
  - Lead-time forecasting.
  - Excess stock management.
  - Multi-location.
  - ML forecasting.
  - Automated ordering.
- Pricing (**UNVERIFIED**): Professional $640/mo, Premium $1,280/mo, Global Planner $1,984/mo. Source: https://www.capterra.com/p/135219/EazyStock/
- ERP overlay for Business Central and Prophet 21: https://www.eazystock.com/blog/improve-inventory-control-prophet-21/

**Small detail to steal**: reclassification alerts (item moved from B-frequent to C-rare, so the policy changed) are a cheap, high-trust exception type.

---

### 1.14 Netstock (South Africa/US; SMB ERP overlay)

- Segment: SMB. **ERP overlay**: pulls item, sales and lead-time data and pushes **one-click PO/WO/TO** back to the ERP. ERPs: Acumatica, NetSuite, Dynamics, SAP B1, Sage. Integration is live in under 45 days. Source: https://www.netstock.com/blog/how-to-optimize-inventory-planning-with-netstock-and-netsuite/ (via search summary)
- **Opportunities Engine**: an AI recommendation feed on stock-out risk, excess and supplier issues. It passed **1M recommendations by Aug 2025**. Source: https://www.lokad.com/review-of-netstock-com/
- "AI Pack".
- Acquired **Demand Works** (S&OP) on **2021-12-06**. Strattam Capital majority investment in Oct 2020. Sources: https://www.netstock.com/blog/news-netstock-acquires-demand-works/ , https://www.lokad.com/review-of-netstock-com/
- Pricing "from $900/month", otherwise by quote (**UNVERIFIED**): https://www.netstock.com/pricing/
- Methods: standard statistical forecasting with seasonality and trend (Lokad review, **UNVERIFIED**).

**Small detail to steal**: an **"opportunities" inbox** in $ terms is the SMB-friendly form of exception management.

---

### 1.15 Intuiflow (Demand Driven Technologies → acquired by Algo, Jan 2026)

- Algo acquired DD Tech on **2026-01-13**: https://www.algo.com/press/algo-acquires-demand-driven-technologies-intuiflow/
- **DDMRP**: decoupling-point buffers (red/yellow/green zones). The **red zone is a shock absorber, not safety stock**. Items are **prioritized by buffer penetration %**. Source: https://intuiflow.com/what-is-ddmrp/
- **Autopilot** self-tunes buffers against service-level targets with explainable ML. Source: https://demanddriventech.com/blog/intuiflow-auto-pilot-inventory-buffers-made-simple/
- **Pulse thresholds** map annual demand "pulses" (order occurrences) to policy:
  - fewer than 10 pulses/yr → make/buy-to-order (do not stock)
  - 10–20 → 85% SL
  - 20–40 → 90% SL
  - more than 40 → 100% SL

  Source: https://demanddriventech.com/blog/intuiflow-auto-pilot-inventory-buffers-made-simple/ (via search summary)
- ERPs: SAP, Oracle, JDE, Dynamics, NetSuite.

**Small detail to steal**: the **pulse (hit-count) threshold → stock / SL tier** table. It is the same idea as dealer "hits" rules and is very explainable.

---

### 1.16 Automotive dealer DMS parts modules and OEM programs (CDK, Reynolds, GM RIM, FCA ARO)

**CDK phase-in / phase-out**
- **Phase-In**: a part is added to the parts master and stock order when *N* **lost-sale or non-stock sales** occur within *M* months (fields "Phase In Sales" and "Phase In Months").
- **Phase-Out**: if a part has not sold for a set number of **weeks**, it is flagged **conditional delete**.
- Both functions offer a **preview report before changes**.

  Source: https://dash.cdk.com/1.008/Help/3.80/Parts/Maint/Inventory_Phase_InPhase_Out.htm (via search summary; page unreachable at fetch time)
- Practitioner detail (DealersEdge forums, **UNVERIFIED** practitioner claims):
  - ADP/CDK phase-in counts **months with a hit**, not raw hits. "2 of 3 months" means a lost sale posted in two *different* months within 3 months.
  - Typical settings:
    - aggressive: phase-in "2 hits in 3 months", phase-out "<2 hits in 3 months", **BSL = 10 days supply**
    - conservative: "3 separate monthly hits in 12 months" with ABC sourcing, lost-sale posting and aggressive OEM stock returns. This is claimed to give about **43 days supply, <2% 12-month no-sale, 94% off-the-shelf fill**.
  - Phase-out at 9 consecutive months with no sale, i.e. obsolete at month 10.
  - In **CDK Drive**, per-source phase criteria moved to function **IRO** (custom stocking parameters assigned to one or more **sources**).

  Sources: https://forums.dealersedge.com/viewtopic.php?t=1054&start=10 , https://forums.dealersedge.com/viewtopic.php?t=3262 , https://forums.dealersedge.com/viewtopic.php?f=3&t=11359
- Terms:
  - **BSL** (Best Stocking Level) = max.
  - **BRP** (Best Reorder Point) = min.
  - **Source codes** group parts by vendor or OEM line.
  - **Lost sale** posting is the demand signal for non-stocked parts.

  Source: https://forums.dealersedge.com/viewtopic.php?t=3708 (**UNVERIFIED**)

**Reynolds and Reynolds (ERA-IGNITE / POWER)**
- Its parts inventory, POs and suppliers are exposed via a certified Parts Inventory API. Source: https://github.com/api-evangelist/reynolds-reynolds
- KPIs used by dealers: fill rate, obsolescence %, days supply. Source: https://www.dealersalessolutions.com/ (**UNVERIFIED**)
- Specific phase-in parameter names: not found (**UNVERIFIED**).

**GM Retail Inventory Management (RIM)**
- Launched in 2005, derived from Saturn in the 1990s. Covers 5,200+ US dealers (85% of the network, 96% of volume) and 9,100+ worldwide. Source: https://www.fenderbender.com/news/article/55053336/inventory-management-evolves-at-dealerships-oems-are-taking-a-new-approach-to-the-service-parts-supply-chain
- At enrolment GM downloads **12 months of DMS order history**. Stocking levels come from the **dealer's own history plus national averages**.
  - The parts manager can override.
  - Polling detects drops below level, and the order goes to the regional DC.

  Sources: https://www.fenderbender.com/news/article/55053336/inventory-management-evolves-at-dealerships-oems-are-taking-a-new-approach-to-the-service-parts-supply-chain , https://www.wardsauto.com/general-motors/gm-to-order-dealerships-parts
- **100% obsolescence protection** on RIM-recommended parts. Parts ordered above the recommendation get **no protection**. Before RIM, protection covered only 5% of unsold inventory.
- A monthly **material return** is generated for parts with no movement for 12+ months.
- RIM parts: 95.6% availability and 5.7 turns. Non-RIM parts: 67% and 4.9.

  Source: https://www.fenderbender.com/news/article/55053336/inventory-management-evolves-at-dealerships-oems-are-taking-a-new-approach-to-the-service-parts-supply-chain
- **DMS integration mechanics**. Source: https://download.autosoft-asi.com/instructions/GM/ASIGMRIM.pdf
  - Each night the DMS sends a **daily sales and inventory file**. An initial **historical file** is sent once.
  - GM returns three files:
    - the **RIM State File**, which sets a per-part **RIM State code**. The code is not editable. State codes such as 02/04/05/06 **exclude the part from the dealer's own suggested order**.
    - the **Copy of Order File**
    - the **RIM Material Return File**
  - GM sends the **OEM Min** (best reorder point). The DMS defaults **OEM Max = Min + 1**.
  - The suggested return is based on the **last 9–12 months** of sales. It is approved on the GM site and gets a **7-character Application Number**, and the DMS then auto-creates the return document.
  - Reports: RIM State Report, **RIM Exception Report**.
- Compliance (**UNVERIFIED**, practitioner forums):
  - The dealer must stock **≥85% of RIM-recommended** parts to keep the parts discount.
  - **90% purchase loyalty** by $ is required under PASE.

  Sources: https://forums.dealersedge.com/viewtopic.php?t=1717 , https://dealersedge.substack.com/p/new-parts-manager-pay-plan-metrics
- **FCA/Stellantis ARO** (Automatic Replenishment Ordering) is a comparable program with "no-risk" returns on recommended parts: https://dealersedge.substack.com/p/new-parts-manager-pay-plan-metrics

**Returnability and order types**
- Statutory return floor, using a Nebraska dealer statute as an example:
  - The supplier must accept annual returns worth **≥6% of the prior 12 months' purchases**.
  - Credit must be **≥85% of the current list price**.

  Source: https://nebraskalegislature.gov/laws/statutes.php?statute=87-706&print=true
- **Emergency (rush) vs stock (daily/weekly) orders**. Emergency orders carry a 20–40% cost premium (**UNVERIFIED**, blog): https://www.cryotos.com/blog/spare-parts-inventory-management-car-dealerships
- OEM dealer-to-dealer (D2D) programs. Source: https://www.autodealertodaymagazine.com/370242/oem-parts-programs-help-dealerships-secure-needed-parts
  - **Kia D2D Express**: 15% bonus to the sharing dealer; Kia pays shipping.
  - **Honda D2D**: pays the source dealer 20% of part value plus expedited shipping.
  - **GM SPRINT**: special orders are filled from parts already in the pipeline.
- Obsolescence rule of thumb: 7–10% is acceptable (**UNVERIFIED**, forum): https://forums.dealersedge.com/viewtopic.php?t=2234

**Small details to steal (dealer)**
- Hits counted as *distinct months with demand*, not raw quantity.
- Lost-sale capture as a first-class transaction.
- Separate stock-order and emergency-order types with different cost and lead time.
- OEM-returnable flag per part.
- "Protected vs unprotected" stock.
- Min+1 max default.
- Conditional-delete status with preview before commit.
- Phase rules configured per source (vendor/OEM line).

---

### 1.17 IFS (Sweden; ERP + service + MRO)

- **IFS Service Parts Management**. Source: https://ifs-p-001.sitecorecontenthub.cloud/api/public/content/service_parts_management.pdf-3183cc?v=1ff3d704
  - Manages parts and **van stock** alongside scheduling and warehouse replenishment.
  - Special algorithms maintain field min/max, ROP and order quantities.
  - Parts are allocated when the technician appointment is scheduled.
  - Mobile logistics sync of usage.
  - Returns and repair flow back to depot repair vendors.
  - First-time-fix focus.
- **PSO** (Planning & Scheduling Optimization) does AI-based resource forecasting and scheduling. Source: https://www.ifs.com/en/products/fsm
- **IFS MRO (aviation)**: engine configuration, ownership and maintenance planning. Source: https://ifs-p-001.sitecorecontenthub.cloud/api/public/content/brochure-independent-mro.pdf-530d8f?v=f4ec2b1d
- Probabilistic or MEIO-grade optimization: not found. IFS appears **execution-centric**; best-of-breed planners get layered on top (**UNVERIFIED** inference).

### 1.18 Epicor and Infor

- **Epicor Kinetic**: per-item Min/Max On-Hand, SS, lead time, order modifiers (min/max/multiple). **Epicor Smart Demand Planner** is OEM'd from Smart Software and includes an intermittent model. Sources: https://smartcorp.com/epicorplanningforecasting/ , https://www.sixspartners.com/news/forecast-inventory-optimization-best-erp-features/
- **Epicor Prophet 21** has four replenishment methods: **Min/Max, OP/OQ, EOQ, Up-To**. Min/Max means ROP = Min, and the **PORG** report suggests orders up to Max. Source: https://smartcorp.com/epicor_p21_prophet_planning_forecasting/ (via search summary)
- **Infor**
  - CloudSuite Service / Service Management ties parts to work orders and installed assets. Source: https://gitnux.org/best/spare-parts-software/ (**UNVERIFIED**)
  - **Infor EAM part condition tracking** (new/used/refurbished conditions for repairables): https://campus2.infor.com/courses/SIMS/Academies/EAM-Power-Training_June2017/White%20Papers/Functional/Infor%20EAM%20Part%20Conditions.pdf (not opened; **UNVERIFIED** content)

### 1.19 PTC Servigistics (the reference incumbent, brief)

- Suite: Service Parts Management plus **Service Parts Pricing** on the same database.
- Built from the **Xelus + MCA Solutions** acquisitions.
- 200+ customers, including Boeing, Deere and the USAF.
- Poisson-based distributions.
- Multi-indenture.
- IoT causal forecasting via ThingWorx.
- **Demand streams**: separate demand streams for, e.g., maintenance vs recalls or campaigns.

Sources: https://www.ptc.com/en/products/servigistics , https://www.lokad.com/spare-parts-optimization-software/ (**UNVERIFIED** for the counts), https://www.ptc.com/en/blogs/service/servigistics-transformative-release

---

## 2. Cross-vendor feature matrix

Legend:
- **Y** = documented in a cited vendor or official source above.
- **C** = claimed by a third party or aggregator only (**UNVERIFIED**).
- **P** = partial or limited.
- **–** = not found in this research. This is not proof the vendor lacks it.

Columns:
- SYN = Syncron
- BAX = Baxter
- TG = ToolsGroup
- GNS = GAINS
- SMT = Smart
- LOK = Lokad
- BY = Blue Yonder
- SAP = SAP SPP/eSPP/IBP
- ORA = Oracle SPP/Spares/Fusion
- KNX = Kinaxis
- o9 = o9
- SLM = Slim4
- EZY = EazyStock
- NTS = Netstock
- IFW = Intuiflow
- DMS = CDK/Reynolds + GM RIM
- IFS = IFS
- EPI = Epicor/Infor ERP-native
- NSU = NetSuite native

| # | Feature | SYN | BAX | TG | GNS | SMT | LOK | BY | SAP | ORA | KNX | o9 | SLM | EZY | NTS | IFW | DMS | IFS | EPI | NSU |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Forecasting** |||||||||||||||||||||
| 1 | Croston/SBA/TSB intermittent methods | C | C | C | – | Y | – | Y | Y | – | – | – | C | – | – | – | – | – | Y | – |
| 2 | Full demand-over-lead-time distribution | Y | – | Y | C | Y | Y | Y | P | – | – | – | – | – | – | – | – | – | P | – |
| 3 | Bootstrap / Monte Carlo scenarios | – | – | C | – | Y | Y | – | – | – | – | – | – | – | – | – | – | – | P | – |
| 4 | Lead-time *distribution* forecast | – | – | – | Y | Y | Y | – | – | – | – | – | – | Y | – | – | – | – | – | – |
| 5 | Auto demand-pattern classification → method | – | – | – | – | – | – | Y | Y | – | – | – | Y | Y | – | – | – | – | Y | – |
| 6 | Automatic best-fit model selection | – | – | – | – | Y | – | Y | Y | – | – | – | Y | – | – | – | – | – | Y | – |
| 7 | Seasonal profiles (item + group) | Y | – | – | – | – | – | – | – | – | – | – | Y | Y | Y | – | – | – | – | Y |
| 8 | Manual forecast override / import | Y | – | – | – | – | – | – | – | – | – | – | – | – | – | – | – | – | – | Y |
| 9 | Override-impact analytics (FVA) | Y | – | – | – | – | – | – | – | – | – | – | – | – | – | – | – | – | – | – |
| 10 | Installed-base × failure-rate forecast | Y | C | – | – | – | – | – | – | Y | – | – | – | – | – | – | – | – | – | – |
| 11 | Causal (usage hours, MTBF/MTBUR, IoT) | Y | – | – | C | – | Y | – | Y | – | – | C | – | – | – | – | – | – | – | – |
| 12 | Planned events / campaigns / demand streams | Y | – | – | – | Y | – | – | – | – | – | – | Y | – | – | – | – | – | – | – |
| 13 | Service-contract-driven demand | – | Y | – | – | – | – | – | – | – | – | – | – | – | – | – | – | – | – | – |
| 14 | ML forecasting | Y | Y | Y | Y | – | Y | Y | – | – | C | C | Y | C | C | Y | – | – | – | – |
| 15 | Backtest / replay simulator | Y | – | – | – | – | – | – | – | – | Y | – | – | – | – | – | – | – | – | – |
| **Inventory optimization** |||||||||||||||||||||
| 16 | Service-level-target driven ROP/SS | Y | Y | Y | Y | Y | – | Y | Y | P | Y | – | Y | Y | Y | Y | – | – | P | P |
| 17 | Total-cost / economic optimization (stockout penalty) | – | Y | – | Y | Y | Y | – | Y | – | – | – | – | – | – | – | – | – | – | – |
| 18 | Ranked purchase list vs budget | – | – | – | – | – | Y | – | – | – | – | – | – | – | – | – | – | – | – | – |
| 19 | Stock-to-service / trade-off curve | – | – | Y | – | Y | – | – | – | – | – | – | – | – | – | – | – | – | – | – |
| 20 | Explicit stock / non-stock decision | Y | – | – | – | – | Y | – | Y | – | – | – | – | – | – | Y | Y | – | Y | – |
| 21 | Criticality attributes (part/site/customer) | Y | Y | – | – | – | Y | – | – | – | – | – | Y | – | – | – | – | – | – | – |
| 22 | Multi-criteria classification matrix (ABC/XYZ/hits) | Y | – | – | Y | – | – | Y | Y | – | – | – | Y | Y | Y | Y | Y | – | – | – |
| 23 | Daily reclassification + move alerts | – | – | – | – | – | – | – | – | – | – | – | – | Y | – | – | – | – | – | – |
| 24 | Rule-based policy/parameter-set assignment | Y | – | – | – | – | – | – | – | – | – | – | Y | Y | – | Y | Y | – | – | – |
| 25 | EOQ / optimal order quantity | Y | Y | – | – | – | – | – | Y | – | – | – | Y | Y | – | – | – | – | Y | – |
| 26 | Critical / initial stock lists | Y | – | – | – | – | – | – | – | – | – | – | – | – | – | – | – | – | – | – |
| 27 | Min/max write-back to ERP (overlay) | Y | Y | Y | Y | Y | Y | – | – | – | – | – | Y | Y | Y | Y | – | – | – | – |
| **Network / multi-echelon** |||||||||||||||||||||
| 28 | MEIO (co-optimized SL per tier) | Y | Y | Y | Y | – | C | Y | Y | P | Y | C | P | – | – | – | – | – | – | – |
| 29 | Demand propagation upstream (MOQ-aware) | Y | – | – | – | – | – | – | – | – | – | – | – | – | – | – | – | – | – | – |
| 30 | Lateral redistribution / balancing | Y | Y | Y | Y | Y | – | – | Y | Y | – | – | Y | – | – | – | P | – | – | – |
| 31 | Fair-share / priority deployment under shortage | – | Y | – | – | – | – | – | Y | – | – | – | – | – | – | – | – | – | – | – |
| 32 | Virtual/regional pooled stock | Y | – | – | – | – | – | Y | – | – | – | – | – | – | – | – | – | – | – | – |
| 33 | Parts locator across sites/dealers | Y | – | – | – | – | – | – | – | Y | – | – | – | – | – | – | Y | – | – | – |
| 34 | Warehouse clustering | Y | – | – | – | – | – | – | – | – | – | – | – | – | – | – | – | – | – | – |
| 35 | Technician / van stock planning | – | Y | – | – | – | – | – | – | Y | – | – | – | – | – | – | – | Y | – | – |
| 36 | Dealer network stocking (OEM-managed RIM) | Y | – | – | – | – | – | – | – | – | – | – | – | – | – | – | Y | – | – | – |
| **Lifecycle** |||||||||||||||||||||
| 37 | Supersession chain + demand inheritance | Y | – | Y | Y | – | – | – | Y | Y | Y | – | – | – | – | – | – | – | – | – |
| 38 | Supersession supply search (use old stock) | – | – | – | – | – | – | – | P | Y | – | – | – | – | – | – | – | – | – | – |
| 39 | Phase-in rules (new part / hits) | – | Y | Y | – | – | – | – | Y | – | – | – | – | – | – | Y | Y | – | – | – |
| 40 | Phase-out / conditional delete | – | Y | Y | – | – | – | – | Y | – | – | – | – | – | – | – | Y | – | – | – |
| 41 | Last-time-buy recommendation | – | Y | Y | – | – | – | – | – | – | – | – | – | – | – | – | – | – | – | – |
| 42 | Excess & obsolete identification | Y | Y | Y | – | – | – | – | Y | Y | – | – | Y | Y | Y | – | Y | – | – | – |
| 43 | Supplier/OEM returns (guaranteed vs not) | Y | – | – | – | – | – | – | – | Y | – | – | – | – | – | – | Y | Y | – | – |
| **Repairables** |||||||||||||||||||||
| 44 | Defective returns forecast | – | Y | Y | – | Y | – | – | – | Y | – | – | – | – | – | – | – | – | – | – |
| 45 | Repair yield / scrap (BER) rate | – | Y | – | – | – | Y | – | – | Y | – | – | – | – | – | – | – | – | – | – |
| 46 | Repair vs buy decision | – | Y | Y | Y | Y | Y | – | – | Y | – | – | – | – | – | – | – | – | – | – |
| 47 | Repair capacity constraint | – | – | – | Y | – | – | – | – | – | – | – | – | – | – | – | – | – | – | – |
| 48 | Remanufactured product planning | – | – | – | – | – | – | – | Y | – | – | – | – | – | – | – | – | – | – | – |
| 49 | Usable / defective sub-locations | – | – | – | – | – | – | – | – | Y | – | – | – | – | – | – | – | – | P | – |
| 50 | OEM vs alternate (PMA) source preference | – | – | – | Y | – | – | – | – | – | – | – | – | – | – | – | – | – | – | – |
| **Replenishment execution** |||||||||||||||||||||
| 51 | Distinct order types (stock/refill vs rush/emergency vs on-demand) | Y | – | – | – | – | – | – | – | – | – | – | – | – | – | – | Y | – | – | – |
| 52 | Auto-confirm orders + blocking rules | Y | – | Y | Y | – | Y | – | Y | – | – | – | Y | Y | Y | Y | Y | – | – | – |
| 53 | Policy-change approval + auto-approve rules | Y | – | – | – | – | – | – | – | – | – | – | – | – | – | – | – | – | – | – |
| 54 | Policy smoothing (phase big changes) | Y | – | – | – | – | – | – | – | – | – | – | – | – | – | – | – | – | – | – |
| 55 | Ordering calendars / supplier closures | Y | – | – | – | – | – | – | Y | – | – | – | Y | – | – | – | – | – | – | – |
| 56 | Order fill-up to MOQ / container / bonus | Y | – | – | – | – | Y | – | Y | – | – | – | Y | – | – | – | – | – | Y | – |
| 57 | Supplier load levelling | Y | – | – | – | – | – | – | – | Y | – | – | – | – | – | – | – | – | – | – |
| 58 | Supplier portal (ETA, expedite, PO forecast) | Y | Y | – | – | – | – | – | – | – | – | – | – | – | – | – | – | – | – | – |
| 59 | Exception / alert workbench | Y | Y | Y | Y | – | – | – | Y | Y | Y | – | Y | Y | Y | Y | Y | – | – | – |
| 60 | "Opportunities" $-ranked recommendation feed | – | – | – | – | – | Y | – | – | – | – | – | – | – | Y | – | – | – | – | – |
| **Analytics / other** |||||||||||||||||||||
| 61 | Risk-of-run-out report | Y | – | – | Y | – | – | – | Y | – | – | – | Y | Y | Y | Y | – | – | – | – |
| 62 | Service loss / backorder root cause | Y | – | – | – | – | – | – | Y | – | – | – | – | – | – | – | – | – | – | – |
| 63 | Supplier performance rating | Y | – | – | – | – | – | – | Y | – | – | – | – | – | – | – | – | – | – | – |
| 64 | What-if scenarios with $ impact | Y | Y | Y | Y | Y | Y | – | – | – | Y | Y | – | – | – | – | – | – | – | – |
| 65 | Budget planning (inventory ↔ finance) | – | Y | – | – | Y | Y | – | – | – | – | Y | – | – | – | – | – | – | – | – |
| 66 | Parts price optimization | Y | – | Y | – | – | – | – | – | – | – | Y | – | – | – | – | – | – | – | – |
| 67 | CO2 simulation | Y | – | – | – | – | – | – | – | – | – | – | – | – | – | – | – | – | – | – |
| 68 | Data science notebook / DSL | Y | – | – | – | – | Y | – | – | – | – | – | – | – | – | – | – | – | – | – |
| 69 | Planning-as-a-service (outsourced planners) | – | Y | – | – | – | Y | – | – | – | – | – | – | – | – | – | – | – | – | – |
| **Commercial** |||||||||||||||||||||
| 70 | Published / SMB-level pricing | – | – | – | – | C | Y | – | – | – | – | – | – | C | C | – | – | – | – | – |

---

## 3. Segmentation and price tiers (summary)

| Vendor | Primary segment | Price indication | Deployment |
|---|---|---|---|
| Servigistics | Large OEM, A&D, defence | Enterprise (not found) | SaaS / on-prem |
| Syncron | OEM aftermarket plus dealer networks | Enterprise; Price IQ for mid-market | SaaS |
| Baxter | High-tech, med-device, industrial service | Subscription by users, parts and modules (**UNVERIFIED**) | SaaS, plus PaaS service |
| ToolsGroup | Distribution, aftermarket, MRO | $100K–2M+/yr (**UNVERIFIED**) | SaaS (Azure marketplace) |
| GAINS | Service parts, MRO, utilities | Not found | SaaS |
| Smart | SMB/mid-market ERP overlay | ~$695–10K/mo (**UNVERIFIED**) | SaaS |
| Lokad | Mid to large, esp. aviation MRO | From $2.5K/mo, fixed monthly | SaaS plus scientists |
| Blue Yonder / SAP / Oracle / Kinaxis / o9 | Large enterprise | Enterprise | SaaS / on-prem |
| Slim4 | Mid-market to enterprise distribution | Not found | Private multi-tenant SaaS / on-prem |
| EazyStock | SMB/mid-market | $640–1,984/mo (**UNVERIFIED**) | SaaS |
| Netstock | SMB | From $900/mo (**UNVERIFIED**) | SaaS |
| Intuiflow (Algo) | Mid-market manufacturers | Not found | SaaS |
| CDK / Reynolds DMS | Franchised dealers | Bundled in DMS | Hosted DMS |
| IFS / Epicor / Infor / NetSuite | ERP customers | ERP licence | SaaS / on-prem |

---

## 4. Integration patterns observed

1. **ERP overlay with parameter write-back** (Smart, EazyStock, Netstock, Slim4, Intuiflow).
   - Nightly extract of item, stock, open POs, sales lines and lead times.
   - The overlay computes the policy.
   - It either writes min/max/ROP back to ERP item-location fields, or pushes suggested PO/TO/WO for one-click release.
   - This is the dominant mid-market pattern.
2. **Planning system of record with order export** (Syncron, Servigistics, Baxter, ToolsGroup).
   - Orders are confirmed in the planner and exported to the ERP/OMS (Syncron scope doc).
   - Suppliers log into the planner's portal.
3. **OEM–dealer file handshake** (GM RIM).
   - Nightly daily file from DMS to OEM.
   - The OEM returns a state/min file, an order copy and a return authorisation file.
   - The DMS enforces state codes on its own suggested order.
4. **Embedded ERP module** (SAP SPP/eSPP, Oracle SPP, NetSuite, IFS). No integration is needed, but methods are weaker and implementation is heavy.
5. **API/data-product layer** (Syncron CSX Data Central with Text-to-SQL, Slim4 with ~700 endpoints, GAINS Connect, Lokad Envision).

---

## 5. Table stakes vs differentiators for a mid-market product

### 5.1 Table stakes (buyers expect these; omission loses deals)

1. Intermittent-aware forecasting (Croston/SBA/TSB) with automatic demand-pattern classification (smooth/erratic/intermittent/lumpy) and best-fit selection.
2. Service-level-driven safety stock and ROP/min-max per item-location, including lead time and lead-time variability.
3. Multi-criteria classification: ABC by value, plus frequency/hits (XYZ or pulses), plus criticality. Different service-level targets per class, and rule-based assignment of policies to classes.
4. Supersession/replacement chains with **demand-history inheritance**, plus interchangeability.
5. Phase-in / phase-out rules (N hits in M months; no sale for N months → candidate obsolete). Always preview before commit.
6. Order suggestions honouring MOQ, pack size, order multiples, supplier lead time and **ordering calendars**. One-click release to PO/TO.
7. Order types: stock/refill vs emergency/rush vs special (non-stock backorder), each with different cost and lead time.
8. Exception workbench: risk of run-out, excess, dead stock, forecast outliers, late POs. Filterable, with mass update.
9. Manual overrides (forecast and parameters) with expiry and audit.
10. Excess and obsolete (E&O) reporting and return-to-vendor suggestions, respecting a returnable flag and allowance.
11. Multi-location visibility, parts locator, and lateral transfer suggestions.
12. KPI dashboard: fill rate (first-time fill), service level, turns, days supply, obsolescence %, lost sales, emergency order %.
13. ERP/DMS integration via file and API, including write-back of parameters.
14. Seasonality (item and group profiles).

### 5.2 Differentiators (where a mid-market product can win)

1. **Probabilistic demand-over-lead-time distribution**, via bootstrap or compound Poisson, instead of a normal-approximation safety stock. Smart and ToolsGroup show this sells. It is cheap to compute at mid-market scale.
2. **Economic mode alongside the SL mode.** Stockout cost is split into penalty, expedite and lost margin (Baxter), and each additional unit is ranked by $ in one **ranked purchase list under a budget** (Lokad). Few mid-market tools offer it.
3. **Trust-building automation** (Syncron's model):
   - auto-confirm orders unless a **blocking rule** matches
   - **policy-change approval** with auto-approve thresholds
   - **policy smoothing** after re-parameterisation
   - **replay/backtest simulator** before go-live
4. **Stock-to-service curve** and $ what-if per class. This makes the trade-off visible to finance.
5. **Dealer-network mode for OEMs/distributors** (Syncron RIM / GM RIM):
   - The OEM sets policy per dealer.
   - Nightly POS feed.
   - One-click dealer approval, with ~15 min/day as the benchmark.
   - **Protected (returnable) vs unprotected stock**.
   - Auto-generated returns for parts with no movement for 9–12 months.
   - Compliance % against the recommended stock.
   - Dealer-to-dealer transfer incentives.
6. **Hits-by-distinct-months counting**, **lost-sale capture** as demand, and **pulse-threshold → SL tier** tables (Intuiflow). Planners and dealers can explain these.
7. **Reclassification alerts** (EazyStock): tell the planner *why* a policy changed.
8. **Virtual / regional pooling** and **warehouse clustering** for slow movers (Syncron).
9. **Repairables-lite**:
   - defective-return forecast
   - repair yield/scrap
   - repair vs buy
   - usable/defective sub-locations (Oracle)
   - the sourcing cascade on-hand → on-order → superseded → lateral excess → repair → buy
10. **Installed-base / campaign demand streams**: recalls, service campaigns, and vehicle parc × failure rate (Syncron, Servigistics, Oracle).
11. **Last-time-buy recommendation** (Baxter, ToolsGroup).
12. **Override-impact analytics** (Syncron Insights): does planner judgement help or hurt?
13. **$-ranked "opportunities" inbox** (Netstock) as the SMB-friendly face of exception management.
14. Low-cost extras that are nice-to-have: supplier load levelling, CO2 simulation, Text-to-SQL analytics, supplier self-service ETA portal.

### 5.3 Anti-patterns and warnings from the market

- ERP-native SPP (SAP/Oracle) is powerful but hard to implement. Buyers layer best-of-breed tools on top (Lokad opinion, **UNVERIFIED**): https://www.lokad.com/spare-parts-optimization-software/
- AI-marketing without disclosed methods is a recurring criticism (Netstock, Slim4, Syncron, Kinaxis reviews). Publishing the method, even a simple one, is itself a trust differentiator.
- Pure economic optimization (Lokad) needs stockout costs that many planners cannot quantify. Offer SL targets as the default and economic mode as opt-in.
- OEM programs penalise over-ordering: stock above the recommendation loses return protection (GM RIM). A dealer tool must show *protected vs unprotected* quantity at order time.

---

## 6. Gaps in this research (not verified)

- Reynolds ERA parts stocking parameter names.
- The full CDK phase-in/out field list. The CDK help page was unreachable, so the content comes from the search snippet only.
- GM RIM State code meanings: only that 02/04/05/06 exclude the part from the dealer suggested order.
- Pricing for Syncron, Baxter, GAINS, Slim4, Kinaxis and o9.
- Kinaxis/o9 intermittent-demand method depth.
- IFS probabilistic capability.
- Infor EAM part-condition PDF content.
- Whether EazyStock shares lineage with Syncron (flagged **UNVERIFIED** in its heading).
