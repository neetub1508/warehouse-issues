# Our Warehouse Suite vs PTC Servigistics — Gap Analysis for the SMB / Mid-Market Service-Parts Opportunity

*Prepared 2026-09-30. Sources: the `classic` codebase (`warehouse-base`, `warehouse`, `warehouse-3pl`, `warehouse-india`, `accessories`, `services`), the `neetub1508/warehouse-issues` design set (FRD FR-001…469, DECISIONS, COMPETITOR-BENCHMARK, 144 tasks) and its live GitHub issue state, plus public material on PTC Servigistics and its competitors (links at the end).*

---

## 1. Executive summary

- **PTC Servigistics and our warehouse suite are different kinds of product.** Servigistics is a **planning and optimisation layer**. It forecasts demand, sets stocking levels across a network, prices parts, and hands purchase requisitions back to SAP. It does **no** receiving, bins, picking, shipping or stock ledger. Our suite is the opposite: a deep **execution system** (a WMS with an inventory ledger) that has almost no planning intelligence.
- **The overlap is small**, but it sits exactly where service parts differ from generic inventory. We already have supersession chains, kits, item × site reorder point / min-max / safety stock, RMA and returns grading, obsolescence returns, recall, a fill-rate KPI, and sister-branch transfer suggestions.
- **The biggest gap is the planning layer.** We have no demand forecasting, no computed stocking levels, no service-level-driven safety stock, no multi-echelon balancing, no core/warranty/repair loop, and no parts pricing. Our own FRD **refuses** most of this on purpose (§10 refusals #8, #9, #16, #22) and "relocates" it to a *future planning module*. That module does not exist yet.
- **The mid-market opportunity is real.** Servigistics, Syncron, Baxter, ToolsGroup and GAINS start at roughly $100k+/year and take multi-quarter implementations. Cheap SMB tools (Netstock, Zoho, Odoo, Fishbowl, Inventory Planner) have no service-parts logic. Smart Software IP&O is the only mid-tier specialist, and it has no execution and no repair/pricing depth.
- **Our edge:** a *"Servigistics-lite" planning module embedded in an execution WMS* that we already own. Servigistics deliberately does not offer that combination, and SMB customers cannot afford to integrate two enterprise products.

**Recommendation:** build a new **`warehouse-planning`** module (v3, on top of P6-02) with 12 capabilities in 3 phases (Section 6). This means formally reversing FRD refusals #8 and #9, which is a decision for you (Section 8).

---

## 2. What PTC Servigistics is

| Aspect | Detail |
|---|---|
| Owner / history | PTC. It acquired Servigistics in 2012 and markets it as "39 years" of pedigree and 200+ customers. |
| Where it fits | Part of PTC's Service Lifecycle Management suite: **Servigistics** (parts planning) + **ServiceMax** (field-service execution) + **Arbortext** (service manuals and illustrated parts catalogs) + **ThingWorx** (IoT). |
| Deployment | Historically on-premises, now cloud SaaS (Azure Marketplace listing, "FedRAMP-ready"). |
| Customers | Boeing, Airbus, Lockheed Martin, Pratt & Whitney, Rolls-Royce, Honeywell, US Air Force (up to $95M / 5 yrs), US Navy / Army / Coast Guard, John Deere, Komatsu, Kubota, Bobcat, Metso, Kone, Daikin, HPE, Xerox, Philips Healthcare, GM, SAIC-GM, VW of America, JLG, FedEx. |
| Industries | Aerospace and defence, airline MRO, heavy equipment and agriculture, automotive OEMs, high-tech and semiconductor, medical devices, elevators and HVAC. |
| Price | Not published. Quote-based, module × users + services. Realistically six to seven figures per year. |
| Time to value | PTC claims 3–12 months after go-live. Rollouts are multi-quarter (GM's pricing rollout extracted data from 120 source systems). |

### 2.1 Servigistics modules and capabilities

| # | Capability | What it does |
|---|---|---|
| S1 | **Forecasting & Demand Planning** | Statistical forecasting for intermittent, sporadic and low-volume demand; new-product introduction; end-of-life; lifecycle-stage forecasts. |
| S2 | **Supersession-aware forecasting** | A new part inherits the demand history of the part it replaces. |
| S3 | **Connected / causal forecasting** | ThingWorx IoT usage and installed-base data drives failure-based forecasts (PTC claims about 30% better accuracy). |
| S4 | **Multi-Echelon Optimisation (MEO)** | Sets optimal stock levels across central DC → regional → branch → van, against service-level targets. |
| S5 | **Asset Sustainability Optimisation (ASO)** | Plans stock to hit equipment **uptime / availability** targets, not just fill rate. Used for performance-based logistics. |
| S6 | **Network Optimisation / balancing** | Redeploys excess stock between locations instead of buying new. |
| S7 | **K-Curve Cycle Stock** | Trades order quantity and frequency against planner workload and ABC class. |
| S8 | **Initial Provisioning** | Stocks parts for a product that has just been launched, with no demand history. |
| S9 | **Last Time Buy** | Sizes the final order before a supplier discontinues a part. |
| S10 | **Repair / rotables planning** | Repair-vs-buy decisions, depot repair, return/repair forecasting, multi-source procurement. |
| S11 | **Field-stock optimisation** | Technician van / trunk / backpack stock, integrated with ServiceMax since 2024. |
| S12 | **Dealer Inventory Management** | Manages stock at dealers across the OEM's dealer network. |
| S13 | **Service Parts Pricing** | Value- and competition-based price optimisation; auto-prices the long tail. |
| S14 | **Performance Analytics & Intelligence** | KPIs (fill rate, availability, inventory investment, planner workload) and AI/ML root-cause analysis. |
| S15 | **What-if / budget-constrained scenarios** | "What service level can I buy for ₹X of inventory?" |
| S16 | **ERP integration** | Reads masters and transactions from SAP; writes purchase requisitions back to SAP. |

**What Servigistics does not do:** receiving, putaway, bins, picking, packing, shipping, stock ledger, valuation, invoicing, tax/e-way bill, or 3PL billing. It needs an ERP or WMS underneath it.

---

## 3. What we have built

### 3.1 Size of the build (from the `classic` codebase)

| Module | Controllers | Entities | Migrations | Frontend pages | Scope |
|---|---|---|---|---|---|
| `warehouse-base` | 79 | ~104 | 179 | 73 | Masters, stock ledger, movement port, reservations, supersession, kits, outbox |
| `warehouse` | 106 | ~139 | 159 | 108 | Inbound, inventory control, outbound, returns, replenishment, valuation, reports |
| `warehouse-3pl` | 18 | 27 | 30 | 18 | 3PL clients, rate cards, billing runs, SLAs, client portal |
| `warehouse-india` | 32 | 55 | 61 | 26 | GSTIN, HSN, e-way bill, challans, ITC-04, job work, bonded, EPR |
| `accessories` (older, simpler) | 28 | 53 | 335 | 36 | Products, stock, transfers, counts, **sales price lists**, quotations and sales orders |

### 3.2 Design set status (`warehouse-issues`)

| Phase | Theme | Status |
|---|---|---|
| P0 | Ledger foundation | 18 closed / 0 open: **built** |
| P1 | Masters, identity, inbound | 23 / 0: **built** |
| P2 | Outbound, counting, valuation, returns, reports | 30 / 12 open follow-ups and bugs: **built** |
| P2-IN | India movement documents | 5 / 0: **built** |
| P3 | RF / mobile execution, waves, kits, VAS, reorder policy | 26 / 0: **built** (some tasks cancelled, listed below) |
| P4 | India statutory (GST engine, e-invoice, job work, bonded) | 12 / 3: **mostly built** |
| P5 | 3PL, channels, reverse logistics | 29 / 0: **built** (cores/warranty cancelled) |
| P6 | Optimisation, computed stocking level, supplier scorecard, logistics | 1 / 12: **not started** |

**Cancelled or removed, and relevant to service parts:**
- P5-15 **cores and warranty scrap-and-hold** (#81) — not planned
- P3-20 **field-service van adapter** (#102) — not planned
- P3-24 **GS1 SSCC / EPC / RFID** (#121) — not planned
- P3-19 **OEM order interface** (#95) — not planned
- P2-25 / P2-26 **dealer and services adapters** — built, then deleted 2026-09-21. Decision on 2026-09-23: "no dealer/vehicle-management scope".

### 3.3 Positioning stated in our own design (COMPETITOR-BENCHMARK.md)

- **Target:** multi-branch Indian SME / mid-market. Examples used are the "ten-branch dealer" and the "400–5,000 SKU parts store". Other segments named: workshop parts, field-service van stock, auto-parts distribution, and general multi-godown SMEs (against Tally, Busy and Marg). 3PL and D2C come in v2.
- **Explicitly not entered:** tier-1 enterprise WMS deals, TMS, OMS, and multi-tenant SaaS.
- **Planning boundary (FRD §6.14):** a WMS holds ROP, min/max and safety stock. *"Forecasting, multi-echelon optimisation and purchase planning belong to a planning product."*

> ⚠ The design still names "vehicle-dealership parts department" as the primary target. The 2026-09-23 decision removed dealer scope, and the docs have not been updated to match. Pick one positioning before building the planning module.

---

## 4. Similarities: what we already cover

| Servigistics capability | Our equivalent | Status | Where |
|---|---|---|---|
| S2 Supersession | Supersession chains (REPLACES / INTERCHANGE / PARTIAL), ratio, effective dates, cycle detection, stock treatment KEEP_SEPARATE / MERGE_DEMAND / MERGE_STOCK, bidirectional interchange; allocation consults the chain | **Built** (execution side) | `WhbItemSupersession`, `WhbSupersessionChainResolver`, FR-071…073, FR-176 |
| S7 (partly) Stocking parameters | Item × site: reorder point, safety stock, min/max, reorder qty, lead time, ABC / XYZ / VED / FSN / HML / velocity class | **Partial**: typed in by hand, never computed | `WhbItemSiteSetting`, FR-053, FR-252 |
| S6 (partly) Network balancing | Replenishment engine prefers a **sister-branch transfer** before a PO when the sister holds stock above its minimum | **Partial**: single-level, rule-based | `WhReplenishmentEngine`, FR-254, P5-18 |
| S1 (inputs only) Demand history | Monthly hits, quantity and **lost sales** per item × site; 12-month history import | **Data only**: nothing reads it to forecast | `WhDemandHistory`, FR-256/257/415 |
| S14 KPIs | Parts KPIs: fill rate against target, turns, obsolescence %; metric targets; stock ageing; low stock; expiry | **Built** (reporting only) | `WhPartsKpiResponse`, `WhMetricTarget`, FR-393 |
| S9 / lifecycle (partly) | OEM **obsolescence returns**, NRV assessment, recall, holds | **Built** | P5 reverse logistics, FR-276/279/280 |
| S10 (partly) Returns | RMA, return receipts, **return grading** / disposition, supplier returns and claims | **Built** | FR-269…275, FR-459 |
| Kitting | Stocked and phantom kits; assembly / disassembly work orders; genealogy | **Built** (single-level only) | `WhbKitDefinition`, P3-10/11, FR-261…267 |
| S11 (schema only) | Location custody with MOBILE / VEHICLE location types | **Schema only**: van adapter cancelled | FR-088 |
| S16 ERP integration | Movement port, outbox, API clients, import framework, accounting handover | **Built**, and deeper than Servigistics because we *are* the system of record | warehouse-base |

---

## 5. Differences

### 5.1 What Servigistics has and we don't (the gaps)

| # | Servigistics capability | Our status | Mid-market importance | Notes |
|---|---|---|---|---|
| G1 | **Intermittent-demand forecasting** (S1) | ❌ Absent (FRD refusal #8) | **Must-have**: 70–90% of service parts have lumpy demand | Data exists (`WhDemandHistory`); the engine does not |
| G2 | **Supersession-aware demand** (S2) | ⚠ Configured but unused: `MERGE_DEMAND` is never read (open bug **#168**) | **Must-have**, and cheap | Fix #168 when G1 lands |
| G3 | **Computed stocking levels / service-level safety stock** (S4 single-echelon, S7) | ❌ Deferred (P6-02 #99 open); ROP and SS are typed in | **Must-have**: the core value proposition | Should target fill rate per ABC/XYZ class |
| G4 | **Auto ABC / XYZ / FSN classification** | ⚠ Fields exist, values hand-entered; ABC recompute FR-463 (v1.1), XYZ deferred (FR-070) | **Must-have**, cheap | Drives G3 and cycle-count frequency |
| G5 | **Multi-echelon optimisation** (S4) | ❌ Absent (refusal #8) | Nice-to-have for SMB; a 2-echelon DC → branch model covers 90% of cases | Full MEO is enterprise territory |
| G6 | **Network rebalancing / excess redeployment** (S6) | ⚠ Sister transfer at reorder time only; no proactive excess sweep | **Should-have** | Extend `WhReplenishmentEngine` |
| G7 | **New-part / initial provisioning** (S8) | ❌ Absent | Should-have | Use the predecessor's history via supersession, or like-item analogues |
| G8 | **Last-time buy / end-of-life** (S9) | ❌ Absent (obsolescence returns only) | Should-have for distributors | Simple lifetime-demand × survival estimate |
| G9 | **Repair / rotables / core returns** (S10) | ❌ Cancelled (#81, FR-277/278) | **Should-have** for auto, heavy equipment and electronics service | Core deposit, core-due tracking, repair-vs-buy |
| G10 | **Warranty claims** | ⚠ Serial warranty dates and `WARRANTY_RETURN` code only; no claim entity | Should-have | Claim → supplier recovery |
| G11 | **Field / van stock planning** (S11) | ❌ Van adapter cancelled (#102); schema only | **Should-have** for field-service SMBs | Mobile location + min/max per van + replenish from branch |
| G12 | **Dealer / channel inventory** (S12) | ❌ Out of scope since 2026-09-23 | Depends on positioning | Conflicts with the "no dealer scope" decision |
| G13 | **Parts pricing** (S13) | ⚠ Price lists exist only in `accessories`; warehouse has costs only | Should-have: rules-based markup and class pricing is enough for SMB | Value-based optimisation is enterprise-only |
| G14 | **Causal / installed-base / IoT forecasting** (S3) | ❌ Absent (refusal #9) | Low for SMB | Later: `services` job-card history as a causal signal |
| G15 | **Availability / uptime optimisation, PBL** (S5) | ❌ Absent | Low for SMB (defence / aviation niche) | Skip |
| G16 | **What-if / budget scenarios** (S15) | ❌ Absent (refusal #16) | Should-have (lite) | "Service level vs inventory ₹" curve per class |
| G17 | **AI/ML root-cause analytics** (S14) | ❌ Absent | Nice-to-have | Explain forecast error or stock-outs later |
| G18 | **Supplier collaboration / scorecard** | ❌ Refusal #22; scorecard P6-05 open | Should-have (scorecard only) | Lead-time variability feeds G3 |
| G19 | **Planner workbench / exception-based planning** | ❌ Absent (there is a replenishment suggestions page) | **Must-have**: how planners actually work | Exceptions: stock-out risk, excess, forecast error |

### 5.2 What we have and Servigistics doesn't (our advantages)

| Area | Our capability |
|---|---|
| Execution | Full WMS: PO, ASN, dock, GRN, QC, putaway, waves, pick, pack, ship, cartons, manifests, carriers, NDR/COD, RF/mobile screens |
| Inventory system of record | Immutable double-entry stock ledger, lots / serials / LPN, genealogy, reservations, allocation strategies, counts, holds |
| Costing | Weighted-average and FIFO valuation, landed cost, NRV, stock-to-GL, COGS, accounting handover |
| India compliance | GSTIN, HSN, e-way bill, e-invoice, delivery challan, ITC-04, job work, bonded / MOOWR, EPR, Schedule H1 |
| 3PL | Client onboarding, rate cards, billing runs, SLAs, client portal |
| Commercial fit | Single-tenant, one database per customer, INR pricing, Indian SME workflows |

> **Positioning:** Servigistics = *"what should I stock?"*. We = *"what do I have, where is it, and how does it move?"*. SMBs need both in one box.

---

## 6. What to build to close the gap: `warehouse-planning` (proposed)

A **new module**, consistent with the FRD's "relocated, not refused" note. It reads `WhDemandHistory`, `WhbItemSiteSetting`, supersession and the ledger, and **writes back** computed ROP / SS / min-max into `WhbItemSiteSetting`. The existing `WhReplenishmentEngine` keeps doing execution-side suggestions, so there is no rework.

### Phase A: "Smart reorder" (MVP, the must-haves)

| # | Capability | Closes | Approach |
|---|---|---|---|
| A1 | Demand classification (ABC by value/hits, XYZ by CV, FSN, smooth / intermittent / lumpy / erratic by ADI-CV²) | G4 | Nightly job; replaces hand-entered classes |
| A2 | Intermittent forecasting: Croston, SBA, TSB, plus simple exponential smoothing and moving average for fast movers; auto-select by class; forecast-error tracking (MAD, bias) | G1 | Method per class, overridable per item |
| A3 | Supersession-aware history (fix #168 `MERGE_DEMAND`) | G2 | Roll predecessor history into successor |
| A4 | Service-level safety stock and computed ROP / min-max (target fill rate per ABC × XYZ cell, lead-time variability) | G3 | This **is** P6-02 (#99), widened. Planner approves before write-back |
| A5 | Planner workbench: exception queue (stock-out risk, excess, dead stock, forecast-error outliers, pending approvals) | G19 | Standard management page + bulk approve |

### Phase B: Service-parts specifics (should-haves)

| # | Capability | Closes |
|---|---|---|
| B1 | Proactive excess redeployment across branches (2-echelon DC ↔ branch) | G5 (lite), G6 |
| B2 | New-part provisioning (inherit from predecessor or analogue item) and last-time-buy calculator | G7, G8 |
| B3 | Core returns and warranty claims: core deposit, core-due ageing, claim → supplier recovery (**reopen #81**) | G9, G10 |
| B4 | Van / technician stock: mobile locations with min/max, replenish from branch, consumption as demand (**revisit #102**, without a vertical adapter) | G11 |
| B5 | Parts price lists: cost-plus / class-based markup, customer price levels (reuse the `accessories` pricing model, not a new engine) | G13 |
| B6 | Supplier scorecard: lead-time mean and variance, OTIF, feeding A4 (P6-05) | G18 |

### Phase C: Differentiators (nice-to-haves)

| # | Capability | Closes |
|---|---|---|
| C1 | Budget what-if: service level vs inventory ₹ curve, "buy this service level for ₹X" | G16 |
| C2 | Causal signal from our own `services` job cards (repairs per model → part usage) | G14 (lite) |
| C3 | ML forecast (bootstrapping, or gradient boosting on history) with explainability | G17 |
| C4 | Repair-vs-buy for repairable parts | G9 (full) |

**Deliberately skip:** full multi-echelon MEO, ASO / PBL uptime optimisation, IoT/ThingWorx-style telemetry forecasting, and value-based price optimisation. These are enterprise and defence features that SMBs neither need nor pay for.

---

## 7. Target positioning for the SMB / mid-market segment

| Dimension | PTC Servigistics | Proposed us |
|---|---|---|
| Customer size | Global OEMs, A&D, Fortune 500 | 1–50 branches, 2k–100k SKUs, ₹20 Cr–₹1,000 Cr revenue |
| Price | $100k–$1M+ per year | Indicative ₹25k–₹2L per month (comparable to Netstock and Smart IP&O at $1k–$5k/month) |
| Implementation | 6–18 months, SI-led | Weeks: 12-month history import (already built, FR-415), templates |
| Architecture | Planning layer on SAP | **Planning + execution in one product**, with no integration project |
| Geography | Global, USD | India-first (GST / e-way bill built), INR |
| Forecasting | Advanced, IoT-connected | Intermittent-demand methods, supersession-aware, service-level driven |

### Competitive map

| Vendor | Tier | Service-parts logic | Execution | Our angle |
|---|---|---|---|---|
| PTC Servigistics | Enterprise | Deepest | None | Too costly and complex for SMB |
| Syncron | Enterprise (~$150k/yr min) | Deep, aftermarket | None | Same |
| Baxter Planning, GAINS, ToolsGroup | Upper mid / enterprise | Deep | None | Same |
| Smart Software IP&O | Mid ($2–10k/month) | Intermittent demand only | None | We add execution, supersession, cores, India compliance |
| Netstock | SMB (~$900/month) | Generic replenishment | Relies on ERP | We add service-parts logic and execution |
| Zoho Inventory, Odoo, Fishbowl, Tally | SMB | None (reorder rules) | Basic | We are far deeper on both axes |

---

## 8. Decisions needed before building

1. **Reverse FRD §10 refusals #8 (forecasting / multi-echelon) and #9 (service-parts planning)?** They were "relocated to a planning module". Confirming `warehouse-planning` as that module fulfils the design's intent, but it is a formal DECISIONS.md change. *Recommended: yes.*
2. **Positioning.** Dealership parts departments were the stated primary target, but dealer scope was removed on 2026-09-23. Is the planning module aimed at **independent parts distributors, workshops and field-service SMBs** (general), or does dealer come back? *Recommended: general service-parts SMB, vertical-neutral.*
3. **Reopen cancelled tasks:** #81 (cores and warranty) and #102 (van stock, vertical-neutral). *Recommended: reopen as Phase B.*
4. **Pricing:** reuse the `accessories` price-list model inside warehouse, or keep pricing out of scope? *Recommended: reuse, Phase B.*
5. **Module and Flyway band:** `warehouse-planning` needs a band. `V550000–V559999` is free in the V130000–V599999 gap. Confirm before any migration is written.
6. **Mobile:** warehouse has a standing "no mobile changes" rule. The planner workbench is desktop-only. Van-stock counting (B4) would be the exception. Confirm.

---

## 9. Quick wins available now (no new module)

| Item | Effort | Value |
|---|---|---|
| Fix **#168**: make `MERGE_DEMAND` actually merge demand history across a supersession chain | Small | Correct history for every future forecast |
| Implement **FR-463**: nightly ABC recompute (by value and hits) into `WhbItemSiteSetting` | Small | Replaces hand-entered classes |
| Add an **XYZ / demand-pattern** (ADI-CV²) computation next to ABC | Small | Prerequisite for the choice of forecast method |
| Add **forecast-ready views** on `WhDemandHistory` (rolling 12-month hits, average demand interval) to the parts KPI page | Small | Planners see demand shape today |
| Start **P6-02** (#99, computed stocking level) as Phase A's A4 | Medium | The single biggest value item |

---

## 10. Sources

- PTC Servigistics product page: https://www.ptc.com/en/products/servigistics
- INAS (PTC reseller) module list: https://www.inas.ro/en/ptc/slm-software/servigistics
- Lokad review of PTC: https://www.lokad.com/review-of-ptc-com/ and https://www.lokad.com/spare-parts-optimization-software/
- PTC news, Connected Forecasting (2018): https://www.ptc.com/en/news/2018/ptc-adds-connected-forecasting-to-servigistics-service-parts-management-solution
- PTC news, US Air Force expansion (2022): https://www.ptc.com/en/news/2022/ptc-announces-servigistics-expansion-with-us-air-force
- PTC case studies: GM, SAIC-GM, JLG (pricing); Pratt & Whitney (SAP integration); Metso; Hitachi Vantara
- Microsoft Marketplace SaaS listing: https://marketplace.microsoft.com/en-us/product/saas/ptc.service_parts_management
- Gartner Peer Insights: https://www.gartner.com/reviews/product/servigistics
- Competitor pricing: GetApp (Syncron), vendorbenchmark (ToolsGroup), SoftwareAdvice (GAINS), SelectHub (Smart IP&O), netstock.com/pricing, inventory-planner.com/pricing, G2 (Fishbowl), zoho.com/inventory/pricing, erpresearch.com (Odoo)

**Unverified claims** (not confirmed in any source): Caterpillar as a Servigistics customer; Croston named as a Servigistics method; a Servigistics supplier portal; native Oracle integration. The indicative INR price band in Section 7 is a suggestion, not market data.
