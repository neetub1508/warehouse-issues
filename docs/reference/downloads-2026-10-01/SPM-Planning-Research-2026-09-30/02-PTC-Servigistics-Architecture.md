# PTC Servigistics — Technical Architecture & Implementation Decisions

Research date: 2026-09-30. Primary sources: the public Servigistics 13.1 Help Center (`trne-prod.ptcmanaged.com/servigistics_help/...`, abbreviated **HC** below), the *Servigistics SaaS Service Description* (1 Aug 2025, abbreviated **SSD**), PTC product pages and press releases, a PTC lecture at Stanford (Apr 2023), and job postings.
Legend: **VERIFIED** = stated in a primary source. **UNVERIFIED** = my inference from indirect evidence. Where ptc.com returned 403 to the fetch tool, the page was read with curl or through search snippets, as noted.

HC base URL: `https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/`
SSD URL: https://ptc-p-001.sitecorecontenthub.cloud/api/public/content/312715bc95994beb94cb013a4906dbe8?v=9c7c8608

---

## 0. TL;DR — the four beliefs, checked

| Belief | Verdict | What it really is |
|---|---|---|
| "Snowflake in the middle" | **Partly true, but it sits at the edge, not in the middle.** | The planning system of record is an **Oracle or SQL Server RDBMS**. Snowflake is the warehouse for **PAI Advanced** (Performance Analytics & Intelligence). The AutoPilot server extracts from the RDBMS, writes CSV, PUTs it to a Snowflake stage and COPYs it into tables. Intellicus then builds cubes from Snowflake for dashboards. Data flows **one way, downstream of planning**. Snowflake credits come bundled with the Advanced and Premium SaaS tiers. |
| "Location model" | **True.** | Location → Location Type → **Location Hierarchies** (per-part replenishment trees) → Echelon. SKU = part × location (a "PLP"). Process Groups (sets of locations). Emergency-backup locations. Network Optimization. The PLP count is the sizing and licensing unit. |
| "Planners can go back in time" | **True, through four separate mechanisms. None of them is Snowflake Time Travel.** | (1) **Enhanced Supply Chain Modeling (ESCM)**: a *Snapshot* is a **database backup as of a point in time**, restored into a *Sandbox* schema to form a *Modeling Instance*. (2) The **History Based Simulator** replays planning day by day over a past date range. (3) **Automated Dataset Comparison** diffs a "backup" dataset against the "current" one. (4) The **SKU Supply Chain History** dashboard, plus the Audit Trail and Journal. |
| "Autopilot" | **True, but it is the batch job engine, not an AI.** | "**AutoPilot** is an agent that runs selected processes": the scheduled, dependency-aware batch runner, typically nightly. The *autonomy* features are separate: **Auto Approval** of orders with horizon, value and per-user limit guardrails; the **Order Explanation Report**; the **AI Assistant** (GA Oct 2025); and **agentic AI** for order approval, work queues and exceptions (Spring 2026). |

---

## 1. Deployment & SaaS architecture

### 1.1 Tiers and runtime (VERIFIED unless noted)

| Layer | Technology | Source |
|---|---|---|
| Web tier | **WebUI Server**: Java web app on **Apache Tomcat 9.0.83** (certification moved from 8.5). Needs `maxParameterCount` raised to 10000 in `server.xml`. | HC `release_notes/release_13_1_0_0/technical_notes_13_1_0_0.html` |
| Batch/compute tier | **AutoPilot Server**, separate from the WebUI server. Install docs have steps for "Stop/Start AutoPilot Server and WebUI Server" on Linux and Windows. | HC `install/` section (e.g. "Installing PAI Advanced on the AutoPilot Server", `install/install_instructions_pai_advanced_oracle_3.html`) |
| System-of-record DB | **Oracle or Microsoft SQL Server** (JDBC driver `mssql 12.2.0.jre8`; Oracle parallel-processing tuning guidance). | HC install_planning_advanced_snowflake.html; technical_notes_13_1_0_0 |
| ETL / "gateway" | **Pentaho PDI** is listed in the hosted-ops job skills. Import web services: `import-csv-file.ws`, `import-csv-data.ws`, `run-job.ws`. | Job posting https://zapply.jobs/jobs/54c5da72-5a15-472a-8095-75742be1dd71/ ; HC technical notes |
| Analytics | **PAI Foundation** (Intellicus reports on the RDBMS). **PAI Advanced** (Snowflake or Oracle platform + Intellicus cubes). **PAI Machine Learning** (Apache **Zeppelin** notebooks, "Data Science Workbench", XGBoost in the ML forecasting ensemble). | HC PAI 5.0 release notes `release_notes_pai/...` |
| Auth | LDAP; `servigistics.credentials.encrypted` property. Log4j 2.17. | HC technical notes; install "Update to log4j 2.17.0" |
| OS | Linux and Windows are both supported (log rotation .gz vs .zip). | HC technical notes |

Stack signal from hosting-ops hiring: "Linux… Apache, Java, and Tomcat… AWS and Azure… Oracle… Pentaho PDI" (Servigistics Cloud Service Engineer posting, URL above).

**Engine language: UNVERIFIED.** No public source names C++ or Java for the optimizer. The web and batch tiers are Java/Tomcat. Because of the product's lineage (Xelus + MCA Solutions + Servigistics, per the PTC product page FAQ), the MEO kernel may be native code. Lokad's review states that PTC's public material "does not expose much about solver families": https://www.lokad.com/review-of-ptc-com/

### 1.2 Hosting, tenancy, cloud

- **Delivery**: SaaS under the PTC Master SaaS Agreement, plus managed services and on-prem (the HC keeps separate on-prem instructions, e.g. "On-premises customers can utilize Servigistics ML functionality without the Data Science Workbench"). VERIFIED (SSD; HC PAI 5.0 notes).
- **Cloud provider**: PTC standardised its cloud operations on **Azure**. For example, ThingWorx moved to Azure Database for PostgreSQL (Mar 2025): https://www.microsoft.com/en/customers/story/22856-ptc-azure-database-for-postgresql. Servigistics can be bought on Azure Marketplace through PTC's Digital Thread bundle (search snippet of https://marketplace.microsoft.com/en-us/product/ptc.service_parts_management). That Servigistics SaaS runs on Azure specifically is **UNVERIFIED**: the ops posting says "AWS and Azure", and the story does not name Servigistics.
- **Tenancy**: The evidence points to **single-tenant, per-customer environments**. Each customer has its own storage entitlement (900 GB–7.5 TB). At exit you receive a "Database schema export". PTC hosts your code customisations under "Extended SaaS Support" (ESS) and can refuse them. PTC forces you onto supported releases. (SSD, all.) A dedicated DB per customer is therefore **UNVERIFIED but strongly implied**. Snowflake is similarly a per-customer PAI database, schema and stage (HC Snowflake resources page).
- **FedRAMP / DoD**: "PTC SaaS Services is… **FedRAMP Authorized at the Moderate Baseline**". It also covers NIST 800-171 / DFARS 252.204-7012 / CMMC, and offers **IL2/IL4/IL5** under DISA SRG. Data stays in the US. Staff are US citizens with background checks. (SSD Exhibit B.) PTC's Spring 2026 page says "FedRAMP-ready security" (https://www.ptc.com/en/products/servigistics, fetched via curl).
- **DR/backup**: daily full backups, geo-redundant. Production backups kept 30 days, non-prod 7 days. **RPO 24 h, RTO 5 days**. VERIFIED (SSD).
- **Data export**: two exports at exit. "Export and snapshot of Data (e.g., for Customer's long-term retention needs) are not offered as part of the standard PTC offering." VERIFIED (SSD). Customer-facing history retention is therefore limited to what the product itself keeps.

### 1.3 Packaging, licensing, sizing (VERIFIED, SSD)

- Packages: Commercial Foundation / Foundation+ / Advanced; Commercial Aviation Foundation; Defense Foundation; FA&D Advanced; Premium; plus add-ons (PAI Advanced, Data Science/ML hours, "PAI Snowflake Usage (200 credits)").
- License metrics: **PMI** (inventory value under management, sold in $1M blocks), **PXL** (parts × locations), and **DAL** (dealer-assigned locations, for OEM Retail Inventory Management). **PLP** (part/location pairs) is a cap on all of them: "The total number of PLPs is a factor in system processing and environment sizing."

| PMI tier | $24–49M | $50–99M | $100–199M | $200–499M | $500M+ |
|---|---|---|---|---|---|
| PLP limit | 100K | 500K | 4M | 8M | **25M** |
| Storage | 900 GB | 1.5 TB | 1.5 TB | 4.5 TB | 7.5 TB |
| Snowflake credits/yr | 200 | 200 | 400 | 400 | 600 |
| ML hours (std/high) | 1200/600 | 1200/600 | 1200/600 | 1200/600 | 2400/1200 |

Scale claims: "billions of part locations every day" (PTC marketing, search snippet of ptc.com/en/products/servigistics). "Millions of decisions every day without user intervention" (Stanford EE392B lecture, 18 Apr 2023: https://web.stanford.edu/class/archive/ee/ee392b/ee392b.1236/lecture/apr18/PTC.pdf). Contractual reality: at most **25M PLPs** per environment.

### 1.4 Release cadence

- Core line: **13.1** (13.1.0.5 is the current public HC), then **14.0** in July 2025 ("40+ enhancements", agentic AI Assistant, multivariate/MTBF forecasting, SIOP consensus, reimagined LTB). Blog: https://www.ptc.com/en/blogs/service/servigistics-transformative-release (403 to the tool; content from search snippets).
- **AI Assistant GA October 2025** (press release, 30 Sep 2025): https://www.prnewswire.com/news-releases/ptc-delivers-new-service-lifecycle-management-ai-solutions-to-modernize-field-service-and-the-service-supply-chain-302570030.html
- **Spring 2026** (PTC product page FAQ, fetched via curl):
  - "Self-Healing, Autonomous Planning — Agentic AI capabilities for order approval, work queue management, exception handling, and closed-loop optimization"
  - "AI Assistant — context-aware conversational AI trained on Servigistics documentation, configuration, and operational data"
  - "SaaS & Platform Modernization — expanded cloud-native SaaS… FedRAMP-ready security"
  - SIOP & consensus planning
  - expanded stochastic MEO
- PAI runs its own version line: PAI 5.0.0.0 / 5.0.0.1 (HC `release_notes_pai/`).
- SaaS customers are upgraded when PTC chooses. Customers must re-certify their own customisations. Falling off a supported release can cost "up to 30% of the annual contracted value" per month (SSD).

---

## 2. AutoPilot — the batch engine (the real meaning of "autopilot")

### 2.1 Definition and the integration loop (VERIFIED, HC `glossary/autopilot.html`)

> "AutoPilot is an agent that runs selected processes to calculate data in accordance with the rules set in Servigistics… The individual AutoPilot tasks can be run collectively or individually at desired frequencies against one or more segments."

The four-step data loop is quoted directly:
1. "The **gateway** pulls information from the host system(s) (**typically on a nightly basis**), does any needed transformation and scrubbing, and writes the results to the Servigistics **download transfer tables**."
2. "AutoPilot picks up the data from the download transfer tables and stores the information in the main Servigistics tables."
3. "The AutoPilot processes the updated data in the main Servigistics tables… then writes its results into the **upload transfer tables**."
4. "The host gateway picks up the data in the upload transfer tables and integrates it with the host system."

```
 ERP/EAM/FSM ──(Pentaho/ETL, SFTP, import-csv-*.ws)──► DOWNLOAD transfer tables
                                                        │  AutoPilot: Get Host Data, Synchronize Database
                                                        ▼
                                              main Servigistics tables (Oracle / SQL Server)
                                                        │  AutoPilot: Forecast → IO scenarios → Generate Order Plan → …
                                                        ▼
 ERP (POs, repair orders, transfers) ◄── gateway ── UPLOAD transfer tables
                                                        │  AutoPilot: PAI processes (extract → CSV → Snowflake stage → COPY)
                                                        ▼
                                             Snowflake (PAI Advanced) ──► Intellicus cubes/dashboards, Zeppelin ML
```

### 2.2 Process catalogue, dependencies, partitioning (VERIFIED)

- Process categories: Core, Network Optimization, Lifecycle, Custom, Pricing, Report, Planning, **Performance Analytics & Intelligence**, **Dataset Comparison** (HC `glossary/autopilot_processes.html`).
- Named jobs seen in the HC: Get Host Data, Synchronize Database, Inventory Optimization – Calculate Scenarios, Apply Overrides, Generate Visual Analytics Report Data, Generate Multi-Period Budget Report, Clear Optimized Production Values, Database Maintenance, Gather System Info, Generate Order Plan, Generate Repair Orders, Customer Order Size (13.1), Region MTBF (PAI).
- **Dependency DAG**: "AutoPilot processes can be run in parallel as long as there are no dependencies… the job with the dependency will wait". Several dependencies are conditional: "if the scenario series is the same for both jobs" (HC `glossary/autopilot_process_dependencies.html`).
- **Partitioning**:
  - **Segments**: groups of SKUs sharing attributes. Parameters are applied through "segment coverages" (HC `glossary/segment.html`).
  - **Process Groups**: "A group of locations that can be processed together… Since data from the host system is normally processed in Servigistics **once per day**, using a Process Group enables more frequent processing of host data without disrupting the daily AutoPilot processing" (HC `glossary/process_group.html`). The 13.1 web services `import-csv-data.ws` and `run-job.ws` accept a process group name.
- **Batch vs real time**: the design is **daily batch**, with intra-day micro-batches per process group. There is no evidence of event-driven, real-time replanning. VERIFIED for batch; real-time absence UNVERIFIED.

### 2.3 Autonomy guardrails on top of AutoPilot (VERIFIED)

| Guardrail | Semantics | Source |
|---|---|---|
| **Auto Approval** (per order type: Procurement, Repair, Replenishment) | "order recommendations are automatically approved if the auto approval requirements (horizon, value, limits) are met" | HC `glossary/auto_approval.html` |
| **Auto Approval Horizon** | Horizon Days, or Horizon Lead-Time Multiplier × pipeline length. Example: NULL means all orders are auto-approved; 0 means only orders dated today. | HC `glossary/auto_approval_horizon.html` |
| **Maximum Order Value Without Approval** | Reference amount × currency cap for auto-approval | HC `glossary/maximum_order_value_without_approval.html` |
| **Approve Limit** (per user, in User Rights) | Validated against Planned Qty × Price per Unit. The user cannot approve above it. | HC `glossary/approve_limit.html` |
| **Order Plan Locked** | Per-order lock flag | HC `glossary/order_plan_locked.html` |
| **Review Board / Work Queue** | Exception records typed by review reason (e.g. Review Type 18 "Critically Short"). Users subscribe to review types. The Work Queue is a prioritised list, most severe first. | HC `glossary/review_board.html`, `glossary/work_queue.html` |
| **Order Explanation Report** (13.1.0.1) | "explanation of the sequence of decisions made during the Generate Order Plan AutoPilot process for each day", keyed by Process Date and Explanation Date | HC 13.1 release notes; `glossary/explanation_date.html`, `glossary/process_date.html` |

"Agentic" layer (marketing claims, not documented in the HC): the AI Assistant (Oct 2025) and Spring 2026 "agentic AI capabilities for order approval, work queue management, exception handling, and closed-loop optimization" (PTC product page). How these agents interact with the guardrails above is **UNVERIFIED**. They most plausibly act *within* the existing Auto Approval and Approve Limit rules.

---

## 3. Data model

### 3.1 Core entities (VERIFIED from HC glossary unless noted)

| Concept | Definition / notes | Source (HC glossary/…) |
|---|---|---|
| **Location** | "A physical or virtual place that stocks parts. A location can also be a geographic area where prices are set…" | `location.html` |
| **Location Type** | "The type of this location in the procurement and replenishment hierarchy" | `location_type.html` |
| **Location Hierarchies** | "define **replenishment trees for a specific part**… assigned to a part and considered an attribute of that part. You can define different replenishment hierarchies by part group" | `location_hierarchies.html` |
| **Echelon** | "The hierarchy level of the supply chain" | `echelon.html` |
| **Replenishment source** | Separate fields for "Location Replenishment Source" (named by the destination) and "Part Replenishment Source Location" (defined by the part). Part-level override of network links. | `location_replenishment_source_loc_name.html`, `part_replenishment_source_location_name.html` |
| **Emergency Backup Location** | An alternate emergency source used when the primary stocking location is short | `emergency_backup_location_optimization.html` |
| **SKU / PLP** | Part × location. "forecasting and planning are done for each part at each location where it has been used… or is anticipated to be used" | SSD |
| **Part Chain** | Supersession: "series of revised part numbers, each superceding the previous revision". "Up-chain" means newer, "down-chain" means older. Supports alternate relation types, including higher-level assemblies that satisfy the need. Local vs Global Part Chains are separate package features. | `part_chain.html`; SSD |
| **Indenture** | LRU (1st indenture) vs SRU (lower levels): the BOM depth used for repairables | `indenture.html` |
| **Segment** / **Multi-Attribute Group** | SKU grouping used for parameters and pricing | `segment.html`, `multi_attribute_group.html` |
| **Service Group / SLA** | Service metric (Fill Rate, Availability) attached to a location hierarchy. Network Optimization analyses SLA coverage per product and install site as "a stand-alone… strategic process". | `location_hierarchy.html`, `network_optimization.html` |
| **Inventory states** | on-hand new / fixed / bad, on order, in return, in repair (in-repair good/bad) | SSD; glossary `in_repair_*` |
| **Scenario** | "a set of rules that govern the Inventory Optimization calculations… The system generated scenario, named **Production**, is read-only… jobs cannot be run against it" | `scenario.html` |
| **What-If Model** | Attached to a scenario. Changing it flags the scenario "as needing to be recalculated". Simulates forecast, price and carbon-tax changes (13.1 GA). | `what_if_model.html`; 13.1 RN |
| **Journal** | Per-SKU notes shown across planner pages | `journal.html` |
| **Slice** | Time-bucketed summary (week, month) | `slice.html` |

### 3.2 Inbound feeds (reference: the ServiceMax → Servigistics connector)

ServiceMax/Asset360 integration uses **AWS AppFlow → S3 CSV**. "Eight flows… seven flows to get data from ServiceMax Org… one flow to insert and/or update the parts planning engine output back". The flows are DemandDetail, LocMaster, PartChainDetail, PartMaster, Product, StockAmount, and one more; the outbound flow is `stocklevel`. File name = execution ID. (https://support.ptc.com/help/servicemax_asset360/en/articles/servigistics_integration/creating-flows.html ; https://support.ptc.com/help/servicemaxcore/en/articles/servigistics_integration/field-stock-optimization.html). This is a good minimal canonical feed set: **demand history, location master, part master, part chains, installed product, stock on hand → stock levels out**.

Other integrations:
- **ThingWorx IoT** (2018): asset utilisation feeds connected forecasting, with a claimed +30% accuracy. https://www.ptc.com/en/news/2018/thingworx-supercharges-servigistics-service-parts-management
- **Connected SPM** is a package feature (SSD).
- SAP/Oracle ERP connectors: VERIFIED only generically ("host system", "gateway"). There is no public evidence of certified SAP adapters. Integrations are typically custom ETL, charged under ESS (SSD).
- Outbound: procurement, repair and replenishment (transfer) orders, stock levels and pricing are written to upload tables for the host (HC autopilot).

### 3.3 Data quality

The gateway does "transformation and scrubbing" (HC autopilot). There are Review Board exception types, and "Excluded SKU" counts for SKUs outside scenario coverage (`excluded_pairs.html`). A dedicated DQ rules engine: **UNVERIFIED / not found**.

---

## 4. "Going back in time": four mechanisms

### 4.1 Enhanced Supply Chain Modeling (ESCM): snapshot + sandbox = modeling instance (VERIFIED)

- **Snapshot**: "A database backup as of a distinct point in time. The database backup can be of a production instance or of an already existing modeling instance." Fields: Snapshot Date, **Snapshot Dump File Name** ("system-generated name of the output file that contains the records"), Snapshot Source (Production | existing modeling instance), and Status (Pending, Running, Success, Failed). The maximum count is set by the global `ESCM_MAX_SNAPSHOTS` (e.g. 10). (HC `glossary/snapshot.html`, `core/core_pid/pid_snapshot_management.html`)
- **Sandbox**: a server or schema slot in a **Sandbox Pool**. `ESCM_MAX_SANDBOXES` (e.g. 5). The "Production sandbox is created by default." (HC `core/core_smart_help/sh_sandbox_pool.html`)
- **Modeling Instance**: "The association between a snapshot and a sandbox… Modeling activity such as making data changes and running process can be performed… without having an impact on the production data". **Snapshot Schema** = "The database name of the modeling instance". (HC `glossary/modeling_instance.html`, `snapshot_schema.html`)
- Access is gated by the global setting `ENABLE_ESCM` and by Modeling-tab user rights.
- **Implementation**: this is **physical copy isolation** (dump and restore a whole DB or schema into a pooled slot). It is not copy-on-write branching. The hard caps (5 sandboxes, 10 snapshots) show the cost. Snapshots can chain (a snapshot of a modeling instance), which gives a tree of what-if branches.

### 4.2 History Based Simulator (HBS): day-by-day replay (VERIFIED, HC `glossary/history_based_simulator.html`, `core/core_pid/pid_history_based_simulator.html`)

- The simulator steps a **Current Simulation Date** from a Start date to an End date. Each simulated day it runs the planning processes plus "daily execution tasks… sales order fulfillment, inventory reconciliation and fill rate". It can "automate the advancing of the date on a daily basis". It records Iteration and **Last Run Process**, so a run can pause and resume. Parameters include "Pause after Every Simulation", "Look Ahead Days for Sales Orders" and the IO scenario and causal-forecast scenario.
- It is tunable: lead times, add or remove locations, enable features such as Schedule Change Suppression. Its stated purpose is to generate history for PAI when real history is missing, and to back-test policy changes.
- **The architectural key**: the engine accepts an injectable **system/process date** ("The System date from Servigistics is now used by PAI Machine Learning", PAI 5.0 notes; "Process Date… In a normal production environment this is the current date"). Replay only works because nothing reads the wall clock directly.

### 4.3 Automated Dataset Comparison (VERIFIED, HC `core/core_topics/module_modeling_automated_dataset_comparison.html`)

- "Standard out of the box metrics are provided for comparison between **backup and current** version. Data is stored for base instance using autopilot process." Uses include upgrade regression, parameter tuning during implementation, and feature impact.
- Dashboards: Forecast Comparison Summary/Detail, and Order Plan Comparison by horizon (Full / Today / 13-week). Built as Intellicus analytical objects (`AO_SPM_*`).

### 4.4 Analytical history & audit (VERIFIED)

- **SKU Supply Chain History** dashboard (PAI 5.0): demand missed, net on-hand good, planned qty, vendor delays, inventory projection.
- **Audit Trail**: opt-in per "Audit Trail Process" on the Audit Configuration page. It tracks field changes such as NFF rate, lead times and order periods on the Interactive Planner Worksheet (HC `glossary/audit_trail.html`, `audit_trail_process.html`). The **Journal** holds per-SKU notes. **Order History** is a count per order.
- Snowflake Time Travel: **no evidence** that PAI relies on it. UNVERIFIED either way.

---

## 5. Analytics: PAI on Snowflake (VERIFIED, HC `install/install_planning_advanced_snowflake.html`, `install/install_instructions_pai_advanced_snowflake_2.html`)

Components: "Servigistics RDBMS Database as the data source, **Servigistics Autopilot Server as the Advanced Analytics Engine**, and Snowflake Database as the data destination and source for Intellicus Dashboards".

Flow:
1. AutoPilot queries the RDBMS (Oracle or SQL Server).
2. It writes temporary CSVs.
3. It stages them into a Snowflake-managed stage.
4. It loads the stage into tables and processes them.
5. Intellicus extracts from Snowflake and builds cubes.
6. Dashboards read both.

Snowflake objects per customer:

| Object | Details |
|---|---|
| PAI Database, Schema | one of each per customer |
| PAI Stage | Snowflake-managed |
| Warehouses | two: *AutoPilot* and *Intellicus*. Sample config: `WAREHOUSE_SIZE='XSMALL' AUTO_SUSPEND=60 AUTO_RESUME=TRUE MIN/MAX_CLUSTER_COUNT=1` |
| Service users and roles | two of each: AutoPilot and Intellicus |

The sizing is tiny and cost-controlled, which matches the 200–600 credits per year bundled in the SSD.

PAI Advanced can alternatively run on an **Oracle platform** (HC `install/install_pai_advanced_on_oracle.html`). **Snowflake is therefore an optional analytics backend, not a planning dependency.**

ML runs in **Zeppelin notebooks** (e.g. XGBoost hyper-parameters `xgb_n_trees`, `xgb_depth`, `xgb_learning_rate`). Features include multivariate forecasting, Remaining Useful Life (beta) and Forecast Override Intelligence (beta). "Data Science/ML usage hours" are metered (SSD; PAI 5.0 RN).

"Snowflake data sharing" to customers: **UNVERIFIED**. There is no public evidence that PTC offers Secure Data Sharing of PAI data. Syncron announced exactly that capability in June 2026 (see §8).

---

## 6. UI, security, explainability

- **UI**: web application. Pages include the **Interactive Planner Worksheet** ("complete overview of a SKU on a single page… Review the results of parameter changes before saving"), Review Board, Work Queue (orders, LTB, pricing), Inventory Studio, Scenarios and What-If Model (HC glossary). The tech stack beyond Java/Tomcat/Apache is UNVERIFIED.
- **Security**:
  - **User Rights Setup** with per-page and per-action rights ("Enhanced User Rights") and monetary **Approve Limit** per user. Review-type subscriptions control what each planner sees.
  - LDAP/SSO; encrypted credentials.
  - For federal customers: the FedRAMP Moderate / IL controls above.
- **Explainability**:
  - The Order Explanation Report (the decision sequence per day).
  - What-If and scenario comparison (A / B / Delta fields on many pages, e.g. `echelon.html`).
  - PAI "Demand Miss Analysis".
  - Marketing adds "explainable AI" for Spring 2026 (PTC product page).
- **Plan approval**: order-level approval workflow (manual or auto, within guardrails). Scenario "Workflow Status" exists (glossary index "Scenario Workflow Status"). A formal plan-version sign-off beyond this is UNVERIFIED.

---

## 7. Implementation methodology, timelines, roles

- Evidence is thin publicly.
  - Juniper Networks reported ROI in under 3 months after go-live (https://www.supplychainbrain.com/articles/3534-juniper-networks-achieves-rapid-results-with-servigistics-implementation).
  - PTC claims "100–900% ROI within 12 months" (Stanford lecture).
  - **SPM Essentials** is a mid-market SaaS-only package with a "pre-defined configuration" for "rapid implementation" (search snippet of the Azure Marketplace listing / SSD family).
- The HC explicitly positions Automated Dataset Comparison and the History Based Simulator as **implementation tuning** tools: "During implementations, tuning is very important…".
- Typical roles (**UNVERIFIED**, inferred from HC artefacts):

| Role | Work |
|---|---|
| Integration/ETL engineer | gateway, Pentaho, transfer tables |
| Solution architect | segments, location hierarchies, part chains |
| Data scientist | PAI ML / Zeppelin |
| Planner super-users | Review Board subscriptions, parameters |
| PTC Cloud Ops | patching, upgrades |
| Customer customisation owner | under ESS |

- Timelines of 6–12 months for enterprise multi-module rollouts are **UNVERIFIED**. They come only from generic SPM-implementation sources, not PTC.

---

## 8. Comparable vendor patterns (architecture only)

| Vendor | Pattern | Relevance | Source |
|---|---|---|---|
| **Kinaxis Maestro** | Its own in-memory DB, "like **Git, but for data**". Scenarios are instant branches that pin historical views, compare, sandbox private changes, and resolve conflicts on commit. Records are stored as objects with versions linked to their parent. | Scenario isolation by **copy-on-write versioning** rather than dump and restore (Servigistics ESCM) | https://www.kinaxis.com/en/blog/we-built-database |
| **o9** | Enterprise Knowledge Graph. Its "Value-Chain Graph" versions plans (draft, approved baseline, frozen window). Its "Decision-Context Graph" records each decision with owner, timestamp, plan version and the assumptions used. | Plan versioning plus **decision ledger** for explainability and audit | https://o9solutions.com/articles/the-four-layers-of-the-o9-enterprise-knowledge-graph (via search snippet) |
| **Lokad** | **Event sourcing** for all user inputs, plus a content-addressable store for data, plus versioned Envision scripts. "Complete reproducibility of past behaviors." | **Time travel by construction**: inputs + code version = reproducible run | https://www.lokad.com/architecture-of-lokad/ |
| **Syncron** | Cloud-native on AWS. June 2026: bidirectional connection to **Snowflake, Databricks** and customer-hosted platforms "without duplicating or moving" data. | Warehouse as an *integration surface* (data sharing), not the planning store | https://www.globenewswire.com/news-release/2026/06/30/3319399/0/en/Syncron-Expands-Integration-Capabilities-to-Connect-Aftermarket-Intelligence-with-Enterprise-Data-Platforms.html |
| **ToolsGroup SO99+** | SaaS on Azure. Single model end to end ("eliminating… passing data from one module to the next"). Probabilistic, Monte Carlo MEIO. | Single-model vs Servigistics' transfer-table staging | https://www.toolsgroup.com/wp-content/uploads/2019/06/ToolsGroup-Service-Optimizer-99.pdf ; PR https://www.prnewswire.com/news-releases/toolsgroup-announces-a-major-new-ai-supply-chain-planning-software-release-optimized-for-the-cloud-300518768.html |

What these show:

| Decision | Servigistics | Others |
|---|---|---|
| Planning store | Classic enterprise RDBMS + batch jobs | Kinaxis: proprietary in-memory versioned store; Lokad: ES + CAS; ToolsGroup: single model |
| Analytics | Separate warehouse (Snowflake/Intellicus) fed by CSV export | Syncron: data sharing |
| Time travel | Coarse physical snapshots + a replay simulator driven by an injected process date | Kinaxis: fine-grained versioning; Lokad: fine-grained event log |

---

## 9. Architecture decisions we must make

Context: a planning module on **Java 21 / Spring Boot + PostgreSQL**, single-tenant, attached to our WMS (warehouse / warehouse-base modules, Docker-only builds, no JSONB, accounting-grade decimals in the accounting modules only).

### D1. Snapshot / time travel / reproducibility

| Option | How | Pros | Cons |
|---|---|---|---|
| A. Servigistics-style physical snapshots | `pg_dump` / `CREATE DATABASE … TEMPLATE` into a pooled sandbox DB | Simple, full isolation | Heavy (GBs per copy), slow, needs caps like `ESCM_MAX_*`, ops burden inside Docker |
| B. **Plan-run ledger**: immutable, append-only run tables keyed by `plan_run_id` | Every batch run writes its inputs-as-used (parameter set version, demand-history cut-off, `as_of_date`) and outputs (`plan_run_sku_result`, `plan_run_order_line`) with `created_at`. Master data changes go to SCD-2 history tables (`valid_from`/`valid_to`). | Cheap. Queryable in SQL. Answers "what did we recommend on 3 Sep and why". Diffs between runs (Automated Dataset Comparison) are plain SQL. | Storage growth → needs partitioning by run month + retention policy |
| C. Full event sourcing (Lokad) | All inputs as events | Perfect replay | Big paradigm shift from our CRUD + Flyway codebase |
| D. Temporal DB extensions (`temporal_tables`, periods) | — | Less code | Extension availability/maintenance in our image; not portable |

**Recommendation: B.** Add:
- one **injectable `PlanningClock` / `asOfDate`** used by every calculation (never `now()`), which is what makes a History-Based-Simulator-style replay possible;
- SCD-2 history on the planning-relevant masters: part-location params, lead times, supersession;
- monthly range partitioning on run tables.

Defer A (whole-DB sandboxes) until a customer needs structural what-ifs, such as adding a location.

### D2. Analytics store: Postgres vs Snowflake / DuckDB / ClickHouse

| Option | Fit |
|---|---|
| **Postgres only** (materialised views / summary tables refreshed after each run, partitioned run tables) | Handles 10^5–10^7 PLPs × a few runs retained. Zero new infra. Matches Docker-only ops. |
| DuckDB (embedded, reading Parquet exported per run) | Excellent for heavy ad-hoc and back-test analytics in-process. No server. Adds an export step and a JVM↔native dependency. |
| ClickHouse | Fast at 10^9 rows, but a new stateful service to operate |
| Snowflake | Only sensible as a *customer-facing* data-share or export target, as Syncron does. Servigistics itself keeps it optional (PAI can run on Oracle). Adds cost and credentials to a single-tenant install. |

**Recommendation: Postgres now**, with summary tables written by the batch job (the same pattern as PAI's "Generate Visual Analytics Report Data" step). Design the run-output tables so they can be exported to **Parquet** later. Add DuckDB for back-testing and simulation analytics when run-history volume demands it. Offer Snowflake/Databricks only as an **outbound export/share** integration, never on the planning path.

### D3. Batch engine

| Option | Notes |
|---|---|
| Spring Batch with job repository in Postgres | Chunking, restart, and step metadata give a "Last Run Process"-style pause and resume. Heavier API. |
| Our existing scheduler pattern (`@Scheduled` + job table + advisory lock), as in `WhbKpiSnapshotScheduler` / `WhbKpiSnapshotJob` | Consistent with the codebase. Must add the DAG and partitioning ourselves. |
| External orchestrator (Airflow/Temporal) | Overkill for single-tenant |

**Recommendation:** a small **DAG-aware job runner on the existing scheduler pattern**:
- job + step tables, declared dependencies, parallel where independent (mirrors AutoPilot Process Dependencies);
- **partition by "process group"** (sets of warehouses/locations) so one group can re-run intra-day without a full nightly run;
- set-based SQL for aggregation and Java for the optimiser kernel;
- idempotent steps keyed by (`plan_run_id`, `step`, `partition`).

Adopt Spring Batch only if chunk/restart semantics become painful. Keep an inbound staging layer ("download transfer tables") and outbound staging ("upload transfer tables") so that ERP and WMS integration is decoupled from the engine. That is Servigistics' gateway pattern, and it maps well onto our Flyway-managed tables.

### D4. Scenario isolation

| Option | Notes |
|---|---|
| Physical copy (ESCM) | Strong isolation, heavy, capped |
| **Scenario-keyed overlay (copy-on-write rows)** | A `scenario_id` column on parameter and override tables; resolve as `COALESCE(scenario override, production)`. Runs write to run tables tagged with `scenario_id`. The Production scenario is read-only (as in Servigistics). |
| Schema-per-scenario | Middle ground, but awkward with Flyway and JPA |

**Recommendation: overlay/copy-on-write** (Kinaxis-like semantics at row level):
- Production is immutable except through approved changes;
- scenarios hold only deltas: parameters, what-if demand multipliers, lead-time changes, added or removed network links;
- "promote scenario" is an audited, permissioned action;
- comparison is SQL across run tables (A / B / Delta, as Servigistics shows);
- cap concurrent scenario runs through the job runner, not by copying the DB.

### D5. Autopilot guardrails (auto-release of recommendations to WMS/ERP)

Copy Servigistics' proven controls and add a decision ledger:
1. **Per-order-type auto-approve switch**: procurement, transfer/replenishment, repair.
2. **Horizon guard**: auto-release only orders due within N days, or within lead time × multiplier.
3. **Value guards**: a max order value without approval (currency-aware, using our existing `DECIMAL(19,4)` accounting convention if it posts to the ledger), plus a **per-user Approve Limit** on manual approval.
4. **Exception gates**: never auto-release a SKU with an open severe exception (Review Board equivalent), a large delta against the previous run (e.g. more than X% or more than Y value), a supersession change, or a data-quality failure in this run's inbound batch.
5. **Lock flag** per order and per SKU, so planners can pin a line.
6. **Decision explanation record** per recommended order: which rule and which inputs; an Order Explanation Report equivalent written into the run ledger (D1).
7. **Kill switch plus shadow mode**: run "autopilot" in recommend-only mode for K cycles and compare with planner decisions before enabling release. Stage it first per process group or warehouse.
8. Any LLM or agentic assistant is **read-and-propose only**. It acts through the same approval API and the same guardrails and never writes directly. Its every action is audited under our existing `@PreAuthorize` and audit conventions.
