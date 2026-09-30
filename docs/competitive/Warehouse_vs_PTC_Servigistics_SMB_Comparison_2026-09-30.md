# Warehouse and service parts management: comparison with PTC Servigistics

**Prepared:** 30 September 2026  
**Purpose:** Identify what we already have, what is missing, and what to build for small and midsize service-parts businesses. This is a product and source-code assessment, not a claim of enterprise feature parity.

## 1. Recommendation

**Keep the existing warehouse foundation and add a focused service-parts planning layer.** We already have substantial inventory execution: stock records, locations, reservations, procurement, transfers, receiving, fulfilment, returns, and reporting. The largest gap is deciding the right future stock level for each part and site, then measuring whether that decision improves availability without creating excess inventory.

The immediate opportunity is a product that helps a parts manager answer:

1. What needs replenishing today?
2. Can another branch supply it before we buy more?
3. What should this part's stocking level be, and why?
4. Which slow-moving parts are tying up cash?
5. Which service jobs or customer orders are at risk?

The first two have meaningful implementation today. The third is explicitly planned in open issue [neetub1508/warehouse-issues#99][i99]. The fourth has reporting foundations. The fifth needs stronger planning and service context.

**Recommended sequence:** verify the existing workflows → complete computed stocking levels → add demand forecasting and service-level stock policies → add selected service-parts workflows → consider advanced network optimization only after customer evidence justifies it.

Do not rebuild item masters, stock balances, purchase orders, transfers, or an independent replenishment engine inside the new planning layer.

## 2. Scope and evidence quality

### Repositories and documents reviewed

- [classic](https://github.com/neetub1508/classic), local and remote HEAD `ee98b80b1ba645b25f6cb8753bc820389656e72d`.
- [warehouse-issues](https://github.com/neetub1508/warehouse-issues), design repository HEAD `7b96725eb5850748cd94b2a784466cb16728a55d`.
- All **189 warehouse issue records**, including bodies: **144 closed, 45 open** at retrieval. Relevant issue discussions were also read, especially removal decisions and follow-ups.
- A warehouse search in the `classic` issue tracker returned no matching issues. The dedicated warehouse repository is the substantive backlog reviewed here.
- Warehouse design README, implementation plan, module integration document, and movement/adapter contract.
- Local `warehouse-base`, `warehouse`, `warehouse-3pl`, `warehouse-india`, and example fixture; targeted services, entities, migrations, contracts, frontend paths, and test inventory.
- Existing `docs/spi/ptc-servigistics.md`, `SPI_PRODUCT_DOCUMENT.md`, and `SPI_FUNCTIONAL_DOCUMENT.md`.
- Current official PTC product pages, documentation, and customer examples.

### How to read the findings

| Label | Meaning |
|---|---|
| Code present | Relevant implementation was found; this does not establish production readiness. |
| Partial | A useful foundation exists, but the complete business outcome is missing or unverified. |
| Planned | Backlog or design describes it; inspected code does not establish delivery. |
| Dropped | Issue discussion explicitly withdrew the feature or removed its module. |
| Not evidenced | No implementation was found in the inspected warehouse scope; this is not a claim about every other product module. |

This was a read-only product review. No application tests, database checks, or live business scenarios were run. Existing test files establish intended coverage only. Open defect reports are reported as backlog evidence, not freshly reproduced failures. Uncommitted local changes, including a warehouse valuation query edit, were left untouched; use the pinned commit for a reproducible baseline.

**A closed issue is not a completion certificate.** Some issues were closed as duplicates or because their target modules were removed. There are also stale open descriptions where the code has progressed.

## 3. What PTC Servigistics does

Servigistics plans service-parts inventory: it combines demand and supply information with service objectives to decide how much stock to hold and where. This addresses inventory investment and parts availability across a service network. PTC describes integration with ERP, maintenance systems, and ServiceMax. [PTC service parts management overview](https://www.ptc.com/en/technologies/service-lifecycle-management/service-parts-management)

Its published capabilities include intermittent-demand forecasting, multi-echelon optimization, asset-availability planning, network design, lifecycle planning, initial provisioning, last-time-buy analysis, dealer inventory management, and K-curve cycle-stock planning. Connected planning can use installed-equipment data through ThingWorx. [PTC capabilities](https://www.ptc.com/en/products/servigistics/capabilities)

In plain terms:

| Business question | Relevant PTC capability |
|---|---|
| How much might customers need? | Demand forecasting |
| How much should each network tier hold? | Multi-echelon inventory optimization |
| Where should inventory be located? | Network optimization |
| How do we support new and discontinued equipment? | Provisioning and lifecycle planning |
| How do stock decisions support equipment uptime? | Asset-availability optimization |

These names describe planning capabilities; they do not imply that every warehouse execution workflow is included in one SPM license. Source: [PTC capabilities](https://www.ptc.com/en/products/servigistics/capabilities).

PTC's current product page also describes simulation, AI-assisted planning, automation, and Spring 2026 improvements including explainability and service SIOP. These are vendor descriptions; entitlement and availability should be checked for a specific purchase. [PTC Servigistics](https://www.ptc.com/en/products/servigistics)

ServiceMax field-stock integration provides a concrete example: it supplies demand, part, replacement, inventory, and location data; Servigistics returns optimized stock levels. This is a useful reference for our own execution-to-planning contract. [PTC field stock documentation](https://support.ptc.com/help/servicemaxcore/en/articles/servigistics_integration/field-stock-optimization.html)

### Product boundaries matter

ServiceMax, Arbortext, and PTC Warranty cover other aspects of field service, service information, and warranty management. Do not assume all their functionality belongs to Servigistics SPM. Likewise, historical Servigistics naming includes separate pricing, returns/repair, and logistics products; it does not establish today's bundle. [PTC SLM portfolio](https://www.ptc.com/en/technologies/service-lifecycle-management), [PTC product-name reference](https://support.ptc.com/support/servigisticsProducts.htm)

Repairable-parts planning belongs in our gap assessment, but a complete PTC depot-repair execution entitlement was not verified. Pricing optimization is also a separate commercial question, not a prerequisite for our first release.

### Does PTC mainly serve large companies?

The enterprise emphasis is supported by PTC's positioning and named OEM customers. It does **not** prove that smaller businesses cannot buy the product or that PTC has no midmarket offering. [PTC Servigistics](https://www.ptc.com/en/products/servigistics)

Operational complexity is a better segmentation test than headcount. PTC's NedTrain example includes 26,500 stocked parts, 9 main locations, 35 service locations, and 65 warehouses. A business with a modest planning team can still have complex inventory needs. [PTC NedTrain case study](https://www.ptc.com/en/case-studies/nedtrain)

**No verified current price quote or universal implementation duration was found in the reviewed sources.** Treat our SMB/midmarket position as a strategy to validate, not proof of an uncontested market.

## 4. Similarities: foundations we already have

These are reusable business concepts, not claims of equal algorithmic sophistication.

| Area | What exists in our warehouse scope | Evidence and qualification |
|---|---|---|
| Part and location data | Item master, UOM, supplier sources, item/site settings, warehouses and location hierarchy | `WhbItem`, `WhbItemSiteSetting`, master controllers; [neetub1508/warehouse-issues#13][i13], [neetub1508/warehouse-issues#20][i20], [neetub1508/warehouse-issues#54][i54] |
| Inventory position | Stock ledger, availability, ownership, lots, serials and reservations | Base ledger/allocation code; [neetub1508/warehouse-issues#25][i25], [neetub1508/warehouse-issues#34][i34], [neetub1508/warehouse-issues#70][i70], [neetub1508/warehouse-issues#77][i77] |
| Demand history | Monthly hits and quantity from eligible issues, reversal handling, lost-sale recording and history import | [Demand recorder][c-demand], [neetub1508/warehouse-issues#106][i106], [neetub1508/warehouse-issues#90][i90] |
| Replenishment recommendations | Runs, proposed suggestions, explanation text, accept/reject and bulk acceptance | [Replenishment engine][c-replen], [acceptance service][c-accept], [neetub1508/warehouse-issues#106][i106] |
| Buy versus branch transfer | Prioritizes a sister branch's surplus before purchase; donor minimum retained | [Engine][c-replen], [neetub1508/warehouse-issues#96][i96] |
| Supply constraints | Supplier minimum quantity, order multiple and lead-time information | Engine and supplier-source queries |
| Substitutions | Effective-dated supersession chains, quantity ratios, alternates and rule-controlled substitution | [Resolver][c-super], [allocator][c-allocate]; demand roll-up remains incomplete |
| Buyer controls | Purchase orders and approval-controlled transfers | [neetub1508/warehouse-issues#105][i105], [neetub1508/warehouse-issues#24][i24]; acceptance delegates to existing document services |
| Returns and stock condition | Return receipts, RMA, supplier returns, quarantine, grading, recall and obsolescence workflows | [neetub1508/warehouse-issues#87][i87], [neetub1508/warehouse-issues#93][i93], [neetub1508/warehouse-issues#72][i72], [neetub1508/warehouse-issues#76][i76] |
| Parts performance | Fill rate, inventory turns, obsolescence percentage and days-supply report | [Parts KPI query][c-kpi], [neetub1508/warehouse-issues#141][i141]; service-job first-time-fix needs different inputs |
| Integration foundation | Movement port, outbox, subscriptions, imports and API clients | [neetub1508/warehouse-issues#71][i71], [neetub1508/warehouse-issues#89][i89], [neetub1508/warehouse-issues#92][i92], [neetub1508/warehouse-issues#111][i111], [neetub1508/warehouse-issues#119][i119] |
| Access and governance | Site/owner scoping, permissions, reason codes, audit and scheduled jobs | Base scope service and workflow contracts; verify each new planning surface |

### What today's replenishment engine actually calculates

The inspected code calculates:

```text
inventory position = on hand - allocated + on order

if position <= configured reorder point:
    target = configured maximum stock
             else reorder point + reorder quantity
             else reorder point
    need = target - position
    apply supplier MOQ and pack multiple when purchasing
```

It can first propose a transfer from the sister site with the largest eligible surplus. Open suggestions and converted supply documents are considered to reduce repeat proposals. Acceptance creates a purchase order or a requested transfer; source-site approval governs the latter. [Engine][c-replen], [acceptance service][c-accept]

This is valuable automation. **Its target levels are still configured inputs.** It does not establish a forecast-driven, service-level optimization model.

Another important boundary: the engine explicitly replenishes **HOUSE-owned stock**. Client-owned 3PL stock is not automatically eligible for the same buyer workflow. Offering planning to 3PL clients requires owner-specific policies and authority, not merely enabling the existing schedule.

## 5. Differences and the work needed

PTC planning references in this table are the capabilities and product sources in section 3, the [inventory optimization overview](https://www.ptc.com/en/solutions/reduce-costs/field-service-cost/inventory-optimization), and the [field stock integration documentation](https://support.ptc.com/help/servicemaxcore/en/articles/servigistics_integration/field-stock-optimization.html). Proposed work below is our assessment.

| Capability | Our present position | What to add | Priority |
|---|---|---|---|
| Automatically computed stocking targets | **Planned:** neetub1508/warehouse-issues#99; existing min/max and reorder inputs | Historical days-supply targets, phase-in/out, input history, protected overrides | Immediate |
| Intermittent-demand forecasting | **Not evidenced in runtime:** described in SPI plans | Baselines, sparse-demand models, backtesting and forecast versioning | First planning release |
| Service-level inventory policies | **Partial:** safety-stock fields and service metrics | Targets linked to demand uncertainty, lead-time variability and part criticality | First planning release |
| Multi-echelon optimization | **Not evidenced:** sister-transfer heuristic exists | Start with hub/branch visibility and constrained rebalancing; evaluate a solver later | Later |
| Supersession-aware planning | **Partial:** relations and allocation exist; neetub1508/warehouse-issues#168 open | Effective-date and ratio-aware demand roll-up, no double counting | Immediate data foundation |
| Installed-base and maintenance demand | **Not evidenced as warehouse planning integration** | Equipment/part applicability plus dated maintenance demand; reuse existing asset/service IDs after mapping | Customer-led extension |
| Lifecycle provisioning and last-time buys | **Partial:** item lifecycle/obsolescence foundations | Remaining-support horizon, replacement chains, retirement assumptions and scenarios | Later |
| Repairable supply planning | **Partial operational foundations; dropped core task** | Core lifecycle, repair turnaround/yield, dated repair supply, repair/buy comparison | Only for repair-heavy pilot |
| Technician-van planning | **Location foundation only; dedicated adapter dropped** | Job consumption/returns and custody integration through an approved existing-module/API design | Only for field-service pilot |
| Dealer network optimization | **Branch stock and transfer foundation** | Authorized dealer demand feeds, replenishment targets and cross-company constraints | Later |
| Planner workbench | **Partial:** suggestions and operational alerts | Combined stockout/excess/late-supply queue with explanations, owner and outcome tracking | First planning release |
| What-if scenarios and inventory budgets | **Not evidenced as planning feature** | Compare service target, lead-time and budget assumptions before approval | After baseline planning |
| Strategic facility-location optimization | **Not evidenced** | Defer until customers need network redesign | Defer |
| Asset-uptime/PBL optimization | **Not evidenced** | Requires reliability, equipment configuration and contract-risk models | Defer |
| AI assistant and autonomous planning | **Not evidenced as warehouse planning capability** | Deliver trustworthy data and bounded approval controls first | Defer |
| Ready-to-use ERP/service connections | **Ports and integration infrastructure present** | Specific mappings, reconciliation, retries and connector acceptance tests | Essential for chosen pilot |

### Warehouse features beyond the comparison's main planning scope

Our repository also contains receiving, putaway, RF/mobile execution, picking, packing, dispatch, cycle counting, label/print flows, 3PL billing and India-specific documents. These can make a combined product useful to customers who need both execution and planning. They are not substitutes for forecasting, and they do not prove superiority over PTC's wider portfolio.

`warehouse-india` and `warehouse-3pl` are real code modules, with frontend pages and tests. Regulatory correctness and operational readiness still require their own validation; this review does not certify compliance.

## 6. Important GitHub findings that change the assessment

| Issue | GitHub state | Interpretation after checking evidence |
|---|---|---|
| [neetub1508/warehouse-issues#99][i99] computed stocking levels | Open | Highest-value existing planning-related task. Uses demand history and days supply; explicitly excludes forecasting inside WMS. |
| [neetub1508/warehouse-issues#106][i106] replenishment and demand history | Closed | Engine, history recorder, acceptance service and targeted tests exist. Reuse them. |
| [neetub1508/warehouse-issues#96][i96] surplus transfers and replenishment extensions | Closed | Sister-transfer logic is present. It is a heuristic, not proof of global optimization. |
| [neetub1508/warehouse-issues#149][i149] supersession, interchange, fitment | Closed | Base supersession is present. Historical counter/fitment delivery notes refer to an adapter later removed; do not count those screens as current warehouse features. |
| [neetub1508/warehouse-issues#167][i167] requested item on reservation | Open | Description is partly stale: V500038, `WhbReservation.requestedItemId`, allocation creation and pick splitting already preserve this in the base path. Deleted counter-adapter acceptance remains unresolved. Re-scope and verify before adding anything. |
| [neetub1508/warehouse-issues#168][i168] MERGE_DEMAND | Open | Stored treatment has no consumer in inspected demand/replenishment services. Genuine planning-data gap; issue still names a removed adapter. |
| [neetub1508/warehouse-issues#156][i156] ABC recompute | Closed as duplicate | Folded into neetub1508/warehouse-issues#33. Site ABC fields exist, but this review found no automatic recompute implementation. Do not count closure as delivery; reconcile with neetub1508/warehouse-issues#33. |
| [neetub1508/warehouse-issues#81][i81] cores and warranty holds | Closed, explicitly void | Target adapters were removed; comments say no code/migration was applied. Re-scope if later needed. |
| [neetub1508/warehouse-issues#95][i95] OEM order interface | Closed, explicitly void | No current delivery; requires new ownership if revived. |
| [neetub1508/warehouse-issues#102][i102], [neetub1508/warehouse-issues#108][i108] field-service/assets adapters | Closed, not required | User decision ruled them out; they were not built. Base location support is not an end-to-end van-stock workflow. |
| [neetub1508/warehouse-issues#150][i150], [neetub1508/warehouse-issues#151][i151] dealer/services warehouse adapters | Closed after deletion | Removed in commit `64d1fe74d5`; existing dealer/services verticals are separate. Do not resurrect deleted adapter modules as an incidental roadmap step. |
| [neetub1508/warehouse-issues#174][i174], [neetub1508/warehouse-issues#175][i175] integrated accounting | Open | Warehouse handover interfaces do not establish working accounting integration. Ownership and end-to-end proof remain backlog items. |

### Readiness work before a customer pilot

Prioritize by the pilot's actual workflow:

- **Inventory/cost trust:** reconcile [neetub1508/warehouse-issues#169][i169]–[neetub1508/warehouse-issues#172][i172], [neetub1508/warehouse-issues#179][i179] as-at valuation, and [neetub1508/warehouse-issues#182][i182] ageing performance.
- **Receiving and integrations:** investigate [neetub1508/warehouse-issues#189][i189] putaway failure and [neetub1508/warehouse-issues#193][i193] omitted-UOM order import.
- **Execution consistency:** resolve ownership of [neetub1508/warehouse-issues#176][i176]/[neetub1508/warehouse-issues#177][i177] bin movements and emergency replenishment.
- **Acceptance evidence:** complete the unproven scenario set in [neetub1508/warehouse-issues#186][i186]; check the reported gate failure in [neetub1508/warehouse-issues#183][i183].
- **Safe reporting:** [neetub1508/warehouse-issues#185][i185] records a per-recipient scope limitation in scheduled reports. Reuse report data only through a design that preserves recipient access.
- **Demand correctness:** resolve neetub1508/warehouse-issues#168 and classify warranty, returns, internal transfers and lost sales before forecasting.

This is not a recommendation to fix every open issue before any planning experiment. Offline analysis can proceed while customer-critical execution defects are addressed.

## 7. A focused product for smaller and midsize clients

### Initial customer hypothesis

Start with **one** of these segments, selected through discovery:

1. Regional spare-parts distributors with several branches.
2. Equipment dealers and service businesses carrying replacement parts.
3. Smaller OEM aftermarket teams with a central store and a manageable branch network.

For a first pilot, a proposed scope is one company, one parts family or business line, a few sites, and a named parts manager who can review recommendations. These are scope choices, not measured market boundaries or scale claims.

A general 3PL warehouse is a different buyer: custody, billing and customer-owned inventory may matter more than service-parts planning. Keep that offering distinct.

### Product promise

> Help a parts manager improve stock availability and reduce avoidable purchases using existing inventory, demand and supply data, with recommendations they can explain and approve.

Offer:

- Warehouse execution as a standalone product.
- An optional parts-planning capability using that same inventory foundation.
- External inventory/ERP ingestion later where a customer already has a working execution system.

Simple onboarding, predictable packaging and clear recommendations are design goals. Do not claim faster deployment, lower total cost or better results than PTC until measured.

### What to defer

Global network solvers, aerospace readiness planning, PBL risk simulation, full IoT predictive maintenance, autonomous purchasing, pricing optimization, and broad industry coverage should not define the first release. They add requirements that a narrow distributor pilot may never need.

## 8. Proposed architecture: reuse execution, add planning

```text
Existing warehouse / external inventory and service sources
        |
        | stock + eligible demand + open supply + replacements
        v
Planning input validation and versioned snapshot
        |
        v
Demand estimates -> proposed stock policies -> exception review
        |
        | approved policy changes / recommendation references
        v
Existing item-site policy and replenishment workflow
        |
        v
Existing purchase / transfer / receipt / issue services
        |
        +---- observed results return to planning evaluation
```

### Reuse these owners

- `warehouse-base`: stock truth, items, locations, UOM, owners, reservations, availability and movement posting.
- `warehouse`: demand history, procurement, transfers, fulfilment, replenishment documents and reports.
- Existing platform: authorization, audit, jobs and import infrastructure, subject to its actual contracts.
- Proposed planning module/domain: forecast versions, planning policies, snapshots, explanations, scenario results and evaluation history.

A new planning module is a recommendation, not an implemented artifact. No active SPI runtime module was found in the inspected build; the existing SPI files are design documents.

### Contracts needed

1. **Planning input:** item/site/owner/company identity, base UOM, usable stock, commitments, dated open supply, demand stream and source event ID.
2. **Replay and reconciliation:** use durable outbox/event contracts and snapshots; deduplicate events, apply reversals, show source freshness, and reconcile to warehouse reports. In-process events alone do not guarantee delivery.
3. **Policy ownership:** manual, historical-policy or forecast-derived authority must be explicit. Preserve overrides, author, reason and expiry. neetub1508/warehouse-issues#99 and a later forecaster must not overwrite each other.
4. **Execution:** publish approved targets through a validated service contract. Continue to create orders through existing services, with idempotency and source approval. Do not write balances or bypass document state machines.
5. **Scope:** enforce site, owner and company access in reads, background jobs and exports. The current HOUSE-owned replenishment boundary must remain explicit.
6. **Data reuse:** add planning attributes/extensions to existing identity, rather than duplicating `whb_items` into a second independent part master. Keep immutable planning snapshots for reproducibility.

These boundaries also preserve the warehouse design's deliberate refusal to implement forecasting inside its execution core. The earlier prohibition on product adapter modules should be preserved; any new service connection needs explicit ownership in the future implementation design.

### Demand definitions need particular care

`WhDemandHistoryRecorder` excludes transfers and honors `affects_demand_history=false`; its documentation explicitly mentions warranty and internal-consumption exclusions. For physical service-parts availability, a warranty replacement may still be real demand. Preserve separate paid-service, warranty, maintenance and other streams, and choose which contribute to a planning policy. Do not assume the commercial-demand view is a complete physical-consumption forecast.

Likewise, do not count a transfer at both sending and consuming sites, or count a failed sale and its later fulfilled order twice. Record missing periods and history coverage; absence of data is not necessarily zero demand.

## 9. Prioritized roadmap and suggested backlog

These are proposed work packages, not new GitHub issues. No issues were created or modified.

| Order | Work package | Reuse/dependencies | Exit evidence |
|---|---|---|---|
| 0 | Establish an honest capability baseline | neetub1508/warehouse-issues#167, neetub1508/warehouse-issues#156/#33, dropped adapter decisions; pilot-critical defects | Demonstrated receive → hold → issue → transfer → return → count flow; reconciled stock/value; corrected feature inventory |
| 1 | Complete historical stocking policies | Existing neetub1508/warehouse-issues#99, neetub1508/warehouse-issues#106 and neetub1508/warehouse-issues#96 | Phase-in/out and provisional-history states; reproducible calculation; manager override survives rerun; existing replenishment consumes approved target |
| 2 | Correct and qualify planning data | neetub1508/warehouse-issues#168, existing recorder/import/outbox | Replays do not duplicate demand; reversals reconcile; supersession ratios/dates handled; warranty and lost-sale semantics documented |
| 3 | Add a small forecasting service | Versioned snapshots and data-quality gates | Compare simple baseline and selected sparse-demand methods using held-out periods; persist model/input versions and overrides |
| 4 | Add service-target stock recommendations | Forecast uncertainty, supplier lead times, criticality | Proposed buffers and order-up-to levels explain assumptions; MOQ/pack constraints shown; targets approved before activation |
| 5 | Add a planner workbench | Existing suggestions, PO/transfer services, KPI definitions | One queue for shortage, excess, late supply and missing-data exceptions; track accept/reject reasons and resulting documents |
| 6 | Add one service-specific workflow | Chosen customer's need; existing asset/service identity | Either maintenance-demand ingestion, core/repair tracking, or van consumption/returns demonstrated end to end |
| 7 | Evaluate broader optimization | Reliable multi-site history and a measurable network problem | Show incremental benefit over historical policies and transfer heuristics before funding a full optimizer |

### Suggested new issue titles after existing tasks are reconciled

- Planning input snapshot and demand-stream contract.
- Supersession-aware demand transformation and replay reconciliation — coordinate with neetub1508/warehouse-issues#168.
- Forecast runs, historical backtesting and model selection.
- Service-level stock targets with explicit policy authority and override retention.
- Planner exception queue and approved handoff to existing replenishment.
- Planning outcome dashboard with agreed KPI denominators.
- Selected pilot ERP/service connector with reconciliation and failure recovery.
- Conditional: core/repair lifecycle re-scoped from void neetub1508/warehouse-issues#81 onto an approved current owner.

Do not open a second issue for neetub1508/warehouse-issues#99, a second requested-item column for neetub1508/warehouse-issues#167, or a duplicate ABC job without settling neetub1508/warehouse-issues#33/#156.

### Pilot acceptance criteria

- A planner can explain every recommendation from its saved inputs and assumptions.
- Sparse or incomplete history produces an explicit provisional result or refusal.
- Re-running the same accepted recommendation cannot create duplicate supply.
- A donor branch retains its protected stock; approvals respect source authority.
- Planning uses correct owner/company scope and excludes unusable stock.
- Supersession, reversal, warranty and lost-sale cases reconcile to source facts.
- Overrides remain visible and survive automatic runs.
- Track fill rate, inventory investment, excess/obsolete stock, emergency purchases, and planner effort against an agreed baseline.
- Measure service-job first-time-fix only after job outcome data is integrated; it cannot be inferred from warehouse fill rate alone.

A narrow pilot should agree numerical success thresholds with its customer before activation. There is insufficient evidence here for a reliable calendar estimate, price or promised percentage improvement.

## 10. Corrections needed in the existing SPI documents

The files under `docs/spi/` contain useful ideas, but mix desired functionality with assertions about current capability and competitors. Before using them for sales or implementation:

| Existing claim/pattern | Recommended correction |
|---|---|
| PTC costs $500K–$5M annually; implementations always take 12–18 months | Remove as an established fact without a current attributable quote and scope. |
| Servigistics is a black box with only stale daily ERP data | Remove the blanket claim. PTC documents explainability developments and ServiceMax/connected integrations. Actual refresh and explanation quality require evaluation. |
| No competitor has native execution-to-planning integration | Unsupported exclusivity claim; describe our intended integration and measure its reliability. |
| SPI has six forecasting methods, optimization and repair management | Label as proposed. No active SPI runtime was established in this review. |
| New `wms_*` stock/item tables | Map to the actual `whb_*` / `wh_*` owners; avoid a parallel inventory model. |
| Warehouse has no planning-related functionality | Correct: demand history, explanatory replenishment and branch-transfer suggestions already exist. |
| Closed adapter issues prove dealer/van/core support | Correct using the subsequent removal/void decisions. |
| Enterprise-scale launch, many industries and a two-month build target | Replace with a narrow pilot and estimated packages after engineering decomposition. |
| All outbound movement is forecast demand | Use explicit stream definitions, reversal handling and transfer exclusion. |
| MAPE alone proves sparse-demand forecasting quality | Select an evaluation contract suited to zero-demand periods; also simulate service and inventory outcomes. |

PTC evidence for the second correction: [current product description](https://www.ptc.com/en/products/servigistics), [field-stock documentation](https://support.ptc.com/help/servicemaxcore/en/articles/servigistics_integration/field-stock-optimization.html). The remaining corrections follow from the code/backlog review or are proposed quality requirements.

## 11. Conclusion

**We have a substantial warehouse execution foundation and some useful replenishment logic. We do not yet have an evidenced Servigistics-like planning product.**

For smaller and midsize customers, the practical next step is to finish computed stocking levels, make planning data trustworthy, and add a focused forecasting and recommendation workflow over the existing warehouse. This produces a credible service-parts product path without making enterprise algorithm parity the initial goal.

The most valuable immediate engineering anchor is **neetub1508/warehouse-issues#99**, supported by **neetub1508/warehouse-issues#168**, backlog reconciliation, and a customer-specific readiness gate.

## Appendix A. Open warehouse issues at retrieval

This list preserves the scope of the open backlog. It includes epics, deferred choices, functional gaps and cosmetic defects; these are not 45 equivalent missing features.

| Issue | Title |
|---|---|
| [neetub1508/warehouse-issues#1](https://github.com/neetub1508/warehouse-issues/issues/1) | EPIC: Warehouse and inventory management — master |
| [neetub1508/warehouse-issues#8](https://github.com/neetub1508/warehouse-issues/issues/8) | EPIC: P4 — India statutory & compliance |
| [neetub1508/warehouse-issues#11](https://github.com/neetub1508/warehouse-issues/issues/11) | EPIC: P6 — Optimisation, planning and the logistics seam |
| [neetub1508/warehouse-issues#75](https://github.com/neetub1508/warehouse-issues/issues/75) | P4-11 · A second, tax-basis inventory value carried alongside the book value |
| [neetub1508/warehouse-issues#94](https://github.com/neetub1508/warehouse-issues/issues/94) | P6-01 · Archiving as a transaction — an `OPENING_BALANCE` movement at the cut-off before a single row moves |
| [neetub1508/warehouse-issues#99](https://github.com/neetub1508/warehouse-issues/issues/99) | P6-02 · The best stocking level is computed, not typed |
| [neetub1508/warehouse-issues#103](https://github.com/neetub1508/warehouse-issues/issues/103) | P6-03 · Measured labour, not engineered standards — and the refusal is the requirement |
| [neetub1508/warehouse-issues#109](https://github.com/neetub1508/warehouse-issues/issues/109) | P6-04 · Automation, AS/RS and robotics through a published task-event contract and the movement port — an interface, never a control layer |
| [neetub1508/warehouse-issues#112](https://github.com/neetub1508/warehouse-issues/issues/112) | P6-05 · Receipt facts emitted as evidence — and the supplier scorecard is deliberately not built here |
| [neetub1508/warehouse-issues#118](https://github.com/neetub1508/warehouse-issues/issues/118) | P6-06 · The `party-base` extraction trigger is recorded, not acted on |
| [neetub1508/warehouse-issues#122](https://github.com/neetub1508/warehouse-issues/issues/122) | P6-07 · 3PL v3 — rate escalation as a new version, the SLA credit as a negative billable event, and client profitability |
| [neetub1508/warehouse-issues#131](https://github.com/neetub1508/warehouse-issues/issues/131) | P6-08 · The `logistics` module — trips, ePOD and freight settlement, posting through the port, with zero commits to `warehouse-base` |
| [neetub1508/warehouse-issues#138](https://github.com/neetub1508/warehouse-issues/issues/138) | P6-10 · The real-time operations dashboard on the platform widget framework |
| [neetub1508/warehouse-issues#142](https://github.com/neetub1508/warehouse-issues/issues/142) | P6-11 · The accessories absorption path, stated in advance so it is a decision rather than a discovery |
| [neetub1508/warehouse-issues#144](https://github.com/neetub1508/warehouse-issues/issues/144) | P6-12 · Multi-level BOM with routings is not built — recorded so the refusal is a decision with a way back in |
| [neetub1508/warehouse-issues#165](https://github.com/neetub1508/warehouse-issues/issues/165) | P2-12 follow-up · RMA expiry job (RJ-012) — open RMAs expire on the site's date |
| [neetub1508/warehouse-issues#166](https://github.com/neetub1508/warehouse-issues/issues/166) | P2-11 follow-up · Pack evidence and item documents cannot be deleted out from under a sealed carton |
| [neetub1508/warehouse-issues#167](https://github.com/neetub1508/warehouse-issues/issues/167) | P2-24 follow-up · A reservation remembers the part the customer asked for when a substitute is held |
| [neetub1508/warehouse-issues#168](https://github.com/neetub1508/warehouse-issues/issues/168) | P2-24 follow-up · MERGE_DEMAND is read by the demand calculation |
| [neetub1508/warehouse-issues#169](https://github.com/neetub1508/warehouse-issues/issues/169) | P2-16 follow-up · Cost Layers and Valuation Policies screens |
| [neetub1508/warehouse-issues#170](https://github.com/neetub1508/warehouse-issues/issues/170) | P2-16 follow-up · Movement lines keep the approved cost, the source-currency amount and the cost source line |
| [neetub1508/warehouse-issues#171](https://github.com/neetub1508/warehouse-issues/issues/171) | P2-16 follow-up · Receipts, supplier returns, transfers and workshop returns give the costing engine what it needs |
| [neetub1508/warehouse-issues#172](https://github.com/neetub1508/warehouse-issues/issues/172) | P2-16 follow-up · Ratify costing defaults, contract codes and run the integration tests in the gate |
| [neetub1508/warehouse-issues#173](https://github.com/neetub1508/warehouse-issues/issues/173) | Follow-up · Accounting envelope v2 — duty status, lot, serial and exchange rate per line |
| [neetub1508/warehouse-issues#174](https://github.com/neetub1508/warehouse-issues/issues/174) | Follow-up · The accounting-facing adapter has no home — no module owns WhbAccountingHandoverSink or WhbGlBalanceProvider |
| [neetub1508/warehouse-issues#175](https://github.com/neetub1508/warehouse-issues/issues/175) | Follow-up · Prove INTEGRATED mode end to end — WH-SC-156, WH-SC-157, CONFIG-CASE-07/10 |
| [neetub1508/warehouse-issues#176](https://github.com/neetub1508/warehouse-issues/issues/176) | P2-02 follow-up · FR-150 / WH-SC-285 bin-to-bin movement has no owning task — the deferral, not a closure |
| [neetub1508/warehouse-issues#177](https://github.com/neetub1508/warehouse-issues/issues/177) | P2-02 follow-up · RA-006 — P2-09's emergency replenish is specified as a BIN_TO_BIN transfer, which V511246 makes unbuildable |
| [neetub1508/warehouse-issues#178](https://github.com/neetub1508/warehouse-issues/issues/178) | OD-20 · Does v1 ship a union valuation report across the two ownership domains? (gates P2-20, P2-27) |
| [neetub1508/warehouse-issues#179](https://github.com/neetub1508/warehouse-issues/issues/179) | P2-20 · WS-224's 365-day lower bound makes the as-at quantity a windowed net, not an all-time balance |
| [neetub1508/warehouse-issues#180](https://github.com/neetub1508/warehouse-issues/issues/180) | WhStockToGl search: an unescaped LIKE makes '_' and '%' live wildcards |
| [neetub1508/warehouse-issues#181](https://github.com/neetub1508/warehouse-issues/issues/181) | wh_opening_stock_lines.validationStatus: a seeded filter row nothing can consume |
| [neetub1508/warehouse-issues#182](https://github.com/neetub1508/warehouse-issues/issues/182) | WS-212 Ageing now scans the whole ledger: PP-7's bound was removed on purpose, and the cost is unmeasured |
| [neetub1508/warehouse-issues#183](https://github.com/neetub1508/warehouse-issues/issues/183) | V511248's header loses its § characters, so MigrationHeaderRule fails and blocks every warehouse ci-gate run |
| [neetub1508/warehouse-issues#184](https://github.com/neetub1508/warehouse-issues/issues/184) | P2-21: four product calls taken by default in report pack 2 |
| [neetub1508/warehouse-issues#185](https://github.com/neetub1508/warehouse-issues/issues/185) | RH-010 unmet: WS-215 cannot be scheduled without a platform commit |
| [neetub1508/warehouse-issues#186](https://github.com/neetub1508/warehouse-issues/issues/186) | W13-1 carry: WH-SC-044…WH-SC-059 not demonstrated (SCENARIO-CATALOGUE.md not available locally) |
| [neetub1508/warehouse-issues#187](https://github.com/neetub1508/warehouse-issues/issues/187) | Site-access 403s name the wrong permission (shared requirePermitted) |
| [neetub1508/warehouse-issues#188](https://github.com/neetub1508/warehouse-issues/issues/188) | P4-13 follow-up · Refuse an unlotted regulated item at the item screen; Schedule H1 prescriber/patient fields (adviser-gated) |
| [neetub1508/warehouse-issues#189](https://github.com/neetub1508/warehouse-issues/issues/189) | Putaway Rules: creating/editing a zone-less rule (FIXED_LOCATION or CONSOLIDATE_SAME_LOT) always 500s |
| [neetub1508/warehouse-issues#190](https://github.com/neetub1508/warehouse-issues/issues/190) | Receiving Sessions export labels the Site column "Warehouse" |
| [neetub1508/warehouse-issues#191](https://github.com/neetub1508/warehouse-issues/issues/191) | Style x Variant Matrix: no code path ever creates a "style" — page is permanently empty |
| [neetub1508/warehouse-issues#192](https://github.com/neetub1508/warehouse-issues/issues/192) | Stock Periods: "Site" column marked sortable but sort is silently ignored |
| [neetub1508/warehouse-issues#193](https://github.com/neetub1508/warehouse-issues/issues/193) | Channel order import rejects lines with no uomCode instead of defaulting to the item's base unit |
| [neetub1508/warehouse-issues#194](https://github.com/neetub1508/warehouse-issues/issues/194) | Handovers: shipment picker shows literal "TRACKING - null" when ship-to name is blank |

## Appendix B. Code and design evidence

The following links are pinned to the inspected source revisions. GitHub issue content remains mutable. Access to private repositories requires your GitHub account.

- [Replenishment calculation and sister transfer logic][c-replen] — `warehouse/backend/src/main/java/ai/warehouse/service/whreplenishment/WhReplenishmentEngine.java`
- [Recommendation acceptance into PO/transfer services][c-accept] — `warehouse/backend/src/main/java/ai/warehouse/service/WhReplenishmentSuggestionService.java`
- [Demand history and reversal semantics][c-demand] — `warehouse/backend/src/main/java/ai/warehouse/service/whdemandhistory/WhDemandHistoryRecorder.java`
- [Supersession resolution][c-super] — `warehouse-base/backend/src/main/java/ai/warehousebase/service/whbitemsupersession/WhbSupersessionChainResolver.java`
- [Allocation and requested-item preservation][c-allocate] — `warehouse-base/backend/src/main/java/ai/warehousebase/service/allocation/WhbAllocationService.java`
- [Parts KPI query and scope][c-kpi] — `warehouse/backend/src/main/java/ai/warehouse/service/whpartskpi/WhPartsKpiQueryService.java`
- [Requested-item migration V500038][c-migration] — `warehouse-base/backend/src/main/resources/db/migration/V500038__Add_whb_allocation_rules_allow_supersession_and_whb_reservations_requested_item.sql`
- [Replenishment functional contract, marked derived][c-contract] — `warehouse/docs/contracts/replenishment.contract.md`
- [Existing item-site policy entity][c-policy] — `warehouse-base/backend/src/main/java/ai/warehousebase/entity/WhbItemSiteSetting.java`
- [Replenishment arithmetic tests, present but not run here][c-tests] — `warehouse/backend/src/test/java/ai/warehouse/service/whreplenishment/WhReplenishmentEngineProposeTest.java`
- [Runtime module build profiles][c-pom] — `pom.xml`
- [Existing SPI product proposal][c-spi] — `docs/spi/SPI_PRODUCT_DOCUMENT.md`
- [Warehouse design: IMPLEMENTATION-PLAN.md](https://github.com/neetub1508/warehouse-issues/blob/7b96725eb5850748cd94b2a784466cb16728a55d/docs/IMPLEMENTATION-PLAN.md)
- [Warehouse design: MODULE-INTEGRATION.md](https://github.com/neetub1508/warehouse-issues/blob/7b96725eb5850748cd94b2a784466cb16728a55d/docs/MODULE-INTEGRATION.md)
- [Warehouse design: PORT-AND-ADAPTER-CONTRACT.md](https://github.com/neetub1508/warehouse-issues/blob/7b96725eb5850748cd94b2a784466cb16728a55d/docs/PORT-AND-ADAPTER-CONTRACT.md)

[c-replen]: https://github.com/neetub1508/classic/blob/ee98b80b1ba645b25f6cb8753bc820389656e72d/warehouse/backend/src/main/java/ai/warehouse/service/whreplenishment/WhReplenishmentEngine.java
[c-accept]: https://github.com/neetub1508/classic/blob/ee98b80b1ba645b25f6cb8753bc820389656e72d/warehouse/backend/src/main/java/ai/warehouse/service/WhReplenishmentSuggestionService.java
[c-demand]: https://github.com/neetub1508/classic/blob/ee98b80b1ba645b25f6cb8753bc820389656e72d/warehouse/backend/src/main/java/ai/warehouse/service/whdemandhistory/WhDemandHistoryRecorder.java
[c-super]: https://github.com/neetub1508/classic/blob/ee98b80b1ba645b25f6cb8753bc820389656e72d/warehouse-base/backend/src/main/java/ai/warehousebase/service/whbitemsupersession/WhbSupersessionChainResolver.java
[c-allocate]: https://github.com/neetub1508/classic/blob/ee98b80b1ba645b25f6cb8753bc820389656e72d/warehouse-base/backend/src/main/java/ai/warehousebase/service/allocation/WhbAllocationService.java
[c-kpi]: https://github.com/neetub1508/classic/blob/ee98b80b1ba645b25f6cb8753bc820389656e72d/warehouse/backend/src/main/java/ai/warehouse/service/whpartskpi/WhPartsKpiQueryService.java
[c-migration]: https://github.com/neetub1508/classic/blob/ee98b80b1ba645b25f6cb8753bc820389656e72d/warehouse-base/backend/src/main/resources/db/migration/V500038__Add_whb_allocation_rules_allow_supersession_and_whb_reservations_requested_item.sql
[c-contract]: https://github.com/neetub1508/classic/blob/ee98b80b1ba645b25f6cb8753bc820389656e72d/warehouse/docs/contracts/replenishment.contract.md
[c-policy]: https://github.com/neetub1508/classic/blob/ee98b80b1ba645b25f6cb8753bc820389656e72d/warehouse-base/backend/src/main/java/ai/warehousebase/entity/WhbItemSiteSetting.java
[c-tests]: https://github.com/neetub1508/classic/blob/ee98b80b1ba645b25f6cb8753bc820389656e72d/warehouse/backend/src/test/java/ai/warehouse/service/whreplenishment/WhReplenishmentEngineProposeTest.java
[c-pom]: https://github.com/neetub1508/classic/blob/ee98b80b1ba645b25f6cb8753bc820389656e72d/pom.xml
[c-spi]: https://github.com/neetub1508/classic/blob/ee98b80b1ba645b25f6cb8753bc820389656e72d/docs/spi/SPI_PRODUCT_DOCUMENT.md
[i193]: https://github.com/neetub1508/warehouse-issues/issues/193
[i189]: https://github.com/neetub1508/warehouse-issues/issues/189
[i186]: https://github.com/neetub1508/warehouse-issues/issues/186
[i185]: https://github.com/neetub1508/warehouse-issues/issues/185
[i183]: https://github.com/neetub1508/warehouse-issues/issues/183
[i182]: https://github.com/neetub1508/warehouse-issues/issues/182
[i179]: https://github.com/neetub1508/warehouse-issues/issues/179
[i177]: https://github.com/neetub1508/warehouse-issues/issues/177
[i176]: https://github.com/neetub1508/warehouse-issues/issues/176
[i175]: https://github.com/neetub1508/warehouse-issues/issues/175
[i174]: https://github.com/neetub1508/warehouse-issues/issues/174
[i172]: https://github.com/neetub1508/warehouse-issues/issues/172
[i169]: https://github.com/neetub1508/warehouse-issues/issues/169
[i168]: https://github.com/neetub1508/warehouse-issues/issues/168
[i167]: https://github.com/neetub1508/warehouse-issues/issues/167
[i156]: https://github.com/neetub1508/warehouse-issues/issues/156
[i151]: https://github.com/neetub1508/warehouse-issues/issues/151
[i150]: https://github.com/neetub1508/warehouse-issues/issues/150
[i149]: https://github.com/neetub1508/warehouse-issues/issues/149
[i141]: https://github.com/neetub1508/warehouse-issues/issues/141
[i119]: https://github.com/neetub1508/warehouse-issues/issues/119
[i111]: https://github.com/neetub1508/warehouse-issues/issues/111
[i108]: https://github.com/neetub1508/warehouse-issues/issues/108
[i106]: https://github.com/neetub1508/warehouse-issues/issues/106
[i105]: https://github.com/neetub1508/warehouse-issues/issues/105
[i102]: https://github.com/neetub1508/warehouse-issues/issues/102
[i99]: https://github.com/neetub1508/warehouse-issues/issues/99
[i96]: https://github.com/neetub1508/warehouse-issues/issues/96
[i95]: https://github.com/neetub1508/warehouse-issues/issues/95
[i93]: https://github.com/neetub1508/warehouse-issues/issues/93
[i92]: https://github.com/neetub1508/warehouse-issues/issues/92
[i90]: https://github.com/neetub1508/warehouse-issues/issues/90
[i89]: https://github.com/neetub1508/warehouse-issues/issues/89
[i87]: https://github.com/neetub1508/warehouse-issues/issues/87
[i81]: https://github.com/neetub1508/warehouse-issues/issues/81
[i77]: https://github.com/neetub1508/warehouse-issues/issues/77
[i76]: https://github.com/neetub1508/warehouse-issues/issues/76
[i72]: https://github.com/neetub1508/warehouse-issues/issues/72
[i71]: https://github.com/neetub1508/warehouse-issues/issues/71
[i70]: https://github.com/neetub1508/warehouse-issues/issues/70
[i54]: https://github.com/neetub1508/warehouse-issues/issues/54
[i34]: https://github.com/neetub1508/warehouse-issues/issues/34
[i25]: https://github.com/neetub1508/warehouse-issues/issues/25
[i24]: https://github.com/neetub1508/warehouse-issues/issues/24
[i20]: https://github.com/neetub1508/warehouse-issues/issues/20
[i13]: https://github.com/neetub1508/warehouse-issues/issues/13
