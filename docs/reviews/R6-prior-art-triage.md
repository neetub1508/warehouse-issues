# LENS R6 — Prior-Art Triage

**Target:** a new Warehouse / Inventory design set for the Classic platform
(`warehouse-base` · `warehouse` · `warehouse-adapter-<vertical>` · `warehouse-3pl` · `warehouse-india`)
**Prior art triaged:** `/Users/bbhushan/work/git/workspace/classic-issues/` — `warehouse-base/docs/`, `warehouse-core/docs/`, `supply-chain-core/docs/` (+ the `logistics/docs/TMS/` folder, see §0.1)
**Truth source for every premise challenge:** `/Users/bbhushan/work/git/workspace/classic` — branch `main`, working tree clean
**Siblings read first:** `R1-codebase-reality.md` (`C-`), `R2-tier1-wms-audit.md` (`T-`), `R3-erp-midmarket-audit.md` (`E-`), `R4-fulfilment-3pl-audit.md` (`F-`), `R5-standards-industry-ops.md` (`S-`)
**Date:** 2026-09-01
**Method:** reading + `grep` only. No `mvn`/`npm`/`tsc`/`psql` was run (Docker-only build). Every count below was
computed with a command shown in-line or in the method note beside it. Anything not computed is marked `UNVERIFIED`.

---

## 0. Executive summary — the load-bearing conclusions

1. **The prior art is a post-implementation review set, not a design set.** This is the single most important
   fact about it and it changes how every row must be read. `warehouse-core`, `supply-chain-core` and
   `warehouse-base` were **built** — 46 + ~17 + ~130 tables, ~65 web screens, migrations `V190001–V190045`,
   `V200001–V200042`, `V210000–V210131` — and then audited. Roughly 60% of the corpus (the whole `WMS/` folder,
   `WAREHOUSE_CORE_ISSUES.md`, `SCC_MODULE_ISSUES_ANALYSIS.md`, `WMS_Competitive_Gap_Analysis_And_Roadmap.md`)
   is written in the present tense about code that **does not exist in this checkout**. Every `EXISTS` / `reuse` /
   `already built` verdict in those documents is void here. Every *decision* in them is still gold. (P-005)

2. **The most dangerous inherited premise is a methodology, not a fact.** Fourteen prior-art documents assert
   *"warehouse modules are pre-production — per the CLAUDE.md rule the DB is rebuilt from scratch on every
   Docker build, so schema fixes go into the ORIGINAL migration in place, never as new ALTER migrations."*
   **`CLAUDE.md` in this checkout contains zero occurrences of "pre-produc"** (`grep -c -i "pre-produc" CLAUDE.md`
   → `0`) and no in-place-edit rule anywhere. The two newest modules here do the exact opposite: `acc_companies`
   is created in `V600001` and altered in `V600142`; `dococr_jobs` is created in `V700000` and altered in
   `V700003`/`V700006`. **Forward-only additive migration is the house style.** An author who inherits the
   in-place rule will edit a shipped migration, break the Flyway checksum on every existing install, and
   `FlywayConfiguration.java:246-264`'s blind `repair()` will paper over it. **BLOCKER. (P-001)**

3. **The schema is the prize, and it is complete and exact.** `WMS_DATABASE_DESIGN.md` is 4,655 lines of full
   DDL for **72 tables** (`grep -cE "^\s*CREATE TABLE" WMS_DATABASE_DESIGN.md` → `72`), each with columns,
   types, CHECK constraints, FKs, indexes and `COMMENT ON`. Eight further tables carry real DDL in the `WMS/`
   folder (packaging + invoice-orders). This is the single most reusable artefact in the corpus and §2 maps
   every one of the 80 onto the new five-module split. It is also **thin exactly where R5 said it was**: `owner_id`
   appears **0 times** in the entire 4,655-line file, and there is no cost-layer, landed-cost, duty-status,
   period-lock, GLN or device-registry table.

4. **One line in that DDL will not run.** `WMS_DATABASE_DESIGN.md:1898` —
   `CONSTRAINT uk_wms_soh_item_loc_lot UNIQUE (item_id, location_id, COALESCE(lot_id, '000…'))`. PostgreSQL
   table-level `UNIQUE` constraints accept a **column list only**; an expression requires
   `CREATE UNIQUE INDEX`. It is the uniqueness guarantee on the central stock-position table, and it is the
   only expression-in-`UNIQUE` in the file (`grep -nE "UNIQUE \(.*\("` → 1 hit). **BLOCKER. (P-008)**

5. **The ledger design is the accessories mistake in better clothes.** `wms_stock_transactions` is declared
   "immutable transaction log" but is **single-sided**: one row carries `quantity` *and* both
   `from_location_id` and `to_location_id` (`:1930-2005`). A transfer is one row, so
   `SUM(quantity) GROUP BY location` is undefined and the per-location balance in `wms_inventory` is **not
   reconstructible from the log**. There is no DB-level UPDATE/DELETE guard despite the "immutable" comment.
   This is precisely R2 `T-001` and R1 `C-021`. The *later* built version fixed part of it (before/after
   balances on the ledger row, `@Version` + a no-oversell CHECK on the balance, a single writer gateway) —
   adopt the built version's shape, not the design document's. (P-009, P-024)

6. **Three module boundaries in the prior art are already void, and one of them is a warning.**
   `supply-chain-core` (46 `scc_*` tables) and `warehouse-core` (~17 `wms_*` tables) do not exist here
   (`ls` → `No such file or directory`; `grep -rln "scc_units_of_measure|scc_suppliers|scc_carriers|scc_customers|scc_hsn_tax_master|sac_master|tax_rules"` over the whole tree → **0 files**). The warning is *why*
   they were split: SCC owned the masters (`scc_units_of_measure` 26 downstream FK refs, `scc_carriers` 18,
   `scc_suppliers` 13) and warehouse owned the operations, and the seam produced a designated-owner entity that
   was **never built** (`SccCompany`), four dangling cross-module table references, `scc*`-named files inside
   `warehouse-core`, and a bulk-import feature whose table was in one module and whose page was in the other —
   a menu that 404s if the module deploys alone. **Fold the masters into `warehouse-base`; do not recreate a
   fifth master-owning module.** (P-003, P-004, P-042)

7. **The live platform still carries hardcoded warehouse exclusions, and nobody has noticed.**
   `platform/.../V528__Create_auditor_role_with_view_permissions.sql:37,59,67` excludes `p.name NOT LIKE 'wms_%'`
   and menus named `warehouse`, `warehouse-setup`, `warehouse-catalog`, `warehouse-config`, plus `logistics_%`;
   `V663__Grant_branch_admin_branch_safe_permissions.sql:17-19` excludes "*pages with NO branch filtering
   (warehouse `wms_*`, product-lift `pl_*`, assets, `scc_*` …)*". These are one-shot `INSERT … SELECT`
   migrations that have already run, so they will **not** retro-grant anything to the new module — which means
   the recorded product decisions ("AUDITOR excludes warehouse", "Branch Admin must not hold warehouse
   view:all") are **not enforced for the new build and must be re-taken deliberately**. Also
   `assets/.../V60158__Asset_depreciation_ledger.sql:291` cites "*the two-tab precedent set by `wms_inventory` /
   `wms_inventory_by_item`*" — a live module quoting a warehouse screen that no longer exists. (P-014)

8. **The prior art contains five capability areas that none of the five sibling lenses touched at all.**
   Verified by grepping all five sibling reports: *pack session* / *cartonisation flow*, *receiving session*
   (multi-PO/multi-ASN inbound shipment), *PO command center*, *gate pass* / *bilty–LR*, *reconciliation case*,
   *keyboard-wedge scan engine*, and the whole service-parts **planning** vocabulary (*last time buy*,
   *rotable pool*, *installed base*, *initial provisioning*, *performance-based logistics*, *K-curve*) return
   **zero hits across R1–R5**. These are §5 and they are the strongest reason to read the prior art at all.

9. **The India pack already exists as 26 built-and-audited tables.** `supply-chain-core` shipped a relational
   tax engine (`tax_components`, `tax_entity_types`, `tax_rules`, `tax_rule_components`, `tax_rule_conditions`,
   `tax_resolution_audit`, `sac_master`, `scc_hsn_tax_master`, `scc_gst_state_codes`) and an 18-table
   e-invoice/e-way-bill compliance stack with a vendor-agnostic provider/credential/session model. R5 §2
   specified what India needs; **this is a prior implementation of most of it, with its own defect list already
   written**. It is the highest-leverage single carry-forward into `warehouse-india`. (P-043 … P-046)

10. **Reusability, computed:** of 37 prior-art `.md` files (28,928 lines), **9 are directly reusable as
    source material**, **19 are reusable as decisions with the "as-built" framing stripped**, **5 are
    obsolete**, and **4 are superseded by sibling reports**. Of the **80 tables with real DDL**, **68 map
    cleanly onto the new five-module split**, 4 are dropped by the prior art's own review, and 8 are
    contested. Of the **205 unique implementation task IDs**, roughly the P0/P1 bootstrap block (15 tasks) is
    void and the rest is a work-breakdown template. Method for each count is stated in §6.

---

## 0.1 A correction to the brief before anything else

The brief states *"`classic-issues/` contains 33,175 lines of earlier warehouse/supply-chain design work"* and
*"`warehouse-base/docs/` — 37 files"*. Computed:

| Set | Files | Lines |
|---|---|---|
| `warehouse-base/docs/` (3 top-level + 7 `spi/` + 25 `WMS/`) | **35** `.md` (+1 `.DS_Store`) | 27,396 |
| `warehouse-core/docs/` | 1 | 215 |
| `supply-chain-core/docs/` | 1 | 317 |
| **Warehouse prior art total** | **37 `.md`** | **28,928** |
| `logistics/docs/TMS/` (13 files) | 13 | 4,247 |
| **28,928 + 4,247** | | **33,175** |

So the 33,175 figure **includes the `logistics/docs/TMS/` folder** — 13 files of transport-management
competitor intelligence (Shipsy, Fleetable, LogiNext, NaaviQ, Delhivery OS, Sagar, FarEye, Fretron,
SuperProcure, Oracle OTM, Rose Rocket) plus a 2,266-line `TMS_Functional_Document.md`. That is **not**
warehouse prior art; it is a TMS design set. It matters because the built warehouse module's outbound flow
terminates in a Shipment → Consignment → Freight Bill → LR → POD chain that is unmistakably drawn from it, and
because R4 §2.4 (carriers, manifests, NDR, RTO, COD) overlaps it heavily. **It is triaged here only as
P-060**; a full TMS triage is a different lens. `37` is the right file count for *all three* warehouse dirs,
not for `warehouse-base/docs/` alone.

---

# §1 — Inventory of the prior art

Kind: **SPEC** = defines what to build · **REVIEW** = audits what was built · **TASKS** = a work breakdown ·
**NOTES** = explanatory / competitor intelligence. `Lines` from `wc -l`.

## 1.1 `warehouse-base/docs/spi/` — the original design set (7 files, 18,507 lines)

| # | File | Lines | Kind | What it decided |
|---|---|---|---|---|
| 1 | `WMS_DATABASE_DESIGN.md` | 4,655 | **SPEC** | **The 72-table schema**, in full DDL, across 15 functional modules. Conventions: UUID PKs, `created_by`/`updated_by` on every table, soft delete on 5 masters only, `is_active`+`status` dual columns on masters, `DECIMAL(18,4)` quantities / `DECIMAL(15,2)` money, `JSONB` for "flexible metadata". Declares migrations **start at V200001** (`:126-130`). Also carries a permissions matrix, ER diagrams and SPI integration points (`:4529-4561`). |
| 2 | `WMS_IMPLEMENTATION_TASKS.md` | 3,875 | **TASKS** | Modules 1–2 (warehouse setup + item master): **107 unique task IDs** (`P0-01…P0-07`, `M1-*`, `M2-*`), each with backend/frontend/DB layer, dependency graph and a mandatory implementation order. Names the platform utilities to reuse and forbids recreating them. |
| 3 | `WMS_IMPLEMENTATION_TASKS_PART2.md` | 3,441 | **TASKS** | Modules 3–15: **98 unique task IDs** (`P1-01…P1-08`, `M3-*`…`M15-*`). Declares Part 1's 180 tasks "COMPLETED". Adds the 4-level warehouse hierarchy and the module-placement rules (what goes in core vs base). |
| 4 | `SPI_PRODUCT_DOCUMENT.md` | 1,814 | **SPEC** | The Service Parts Intelligence product/architecture strategy. **The key architectural claim: "WMS is the execution foundation; SPI is the intelligence layer built on top" — sell WMS standalone to distributors, or WMS+SPI to OEMs.** 6-week deployment vs Servigistics' 18 months. |
| 5 | `WAREHOUSE_EXPLAINED.md` | 1,719 | **NOTES** | Every warehouse menu explained with a concrete Indian automotive-spare-parts example ("AutoParts Central" — brake pads, oil filters for Honda/Maruti/Tata dealers), in a fixed 4-part shape: what it is · real-world example · depends on · used by. |
| 6 | `SPI_FUNCTIONAL_DOCUMENT.md` | 1,601 | **SPEC** | SPI functional scope — features, workflows, roles, screens, KPIs, phasing. Explicitly excludes schema. States SPI **always requires WMS** and reads live inventory from it. |
| 7 | `ptc-servigistics.md` | 1,402 | **NOTES** | Competitor intelligence on PTC Servigistics: **16 modules** of service-parts planning — parts master, demand forecasting, multi-echelon optimisation (MEO), network management, asset-availability (MIME/ASO), initial provisioning, lifecycle/last-time-buy, order planning, dealer inventory, repair & return, pricing, PBL, strategic network optimisation, SIOP, analytics, planner workbench. |

## 1.2 `warehouse-base/docs/` top level (3 files, 1,562 lines)

| # | File | Lines | Kind | What it decided |
|---|---|---|---|---|
| 8 | `WAREHOUSE_END_TO_END_FLOWS.md` | 769 | **SPEC** | The three document flows (PO / SO / TO) end-to-end, plus an auto-event trigger summary, role responsibilities, a global-settings reference, status flows and an ER quick reference. |
| 9 | `WAREHOUSE_ARCHITECTURE_REVIEW.md` | 664 | **REVIEW→SPEC** | **The single best decision document in the corpus.** Rejects making Transfer Order a polymorphic "God Document"; locks PO = supplier→our WH, SO = our WH→customer, TO = our WH→our WH, with drop-ship as an SO+PO pair and no warehouse activity. Quantifies the saving (17→8 entity changes, 8→2 NOT NULL drops, 16→13 migrations, 7→5 sprints). Ends with a 14-row locked migration list and a decision table. |
| 10 | `ERP_FEATURE_GAPS.md` | 129 | **NOTES** | 12 categories of ERP capability the warehouse stack lacks (financials, procurement planning, manufacturing, CRM, HR/labour, EAM, advanced WMS, TMS, QMS, compliance, BI, cross-cutting). Headline level only — no columns, no schema. |

## 1.3 `warehouse-base/docs/WMS/` — the post-build correction set (25 files, 7,327 lines)

Every file here is written against a **built** system with `V21xxxx` migrations and named Java classes.

| # | File | Lines | Kind | What it decided |
|---|---|---|---|---|
| 11 | `WMS_Outbound_Flow_Implementation_Task.md` | 742 | **TASKS** | The build breakdown derived from `WMS_Outbound_Flow_FINAL.md`, with P0/P1/P2 gap IDs and per-layer verify cells. |
| 12 | `WMS_Outbound_Flow_FINAL.md` | 594 | **SPEC (FROZEN)** | The frozen outbound chain: SO → Invoice(DRAFT) → Allocation → Wave → Pick → Pack Session → Shipment → Carrier Assignment ⇒ Freight Bill + Consignment → E-Invoice → E-Way Bill → Gate Pass → Dispatch → POD → Delivered → freight reconciliation. **Revision R7 locks 11 UX decisions**, including Add-Truck-on-shipment-only, a 10-state consignment lifecycle, mandatory carton loading before dispatch, and EWB-conditional gate pass. |
| 13 | `WMS_Packaging_Architecture_Design.md` | 594 | **SPEC** | The packaging hierarchy vision: `wms_packaging_classes`/`_types`/`_levels`/`_rules`/`_templates`, `wms_product_packaging_profiles`, `wms_package_events`. **6 `CREATE TABLE`.** Partially superseded by #16. |
| 14 | `WMS_Competitive_Gap_Analysis_And_Roadmap.md` | 525 | **REVIEW** | **The best as-built truth in the corpus.** 8-pillar maturity scorecard with file references and engineer-week estimates. Verdict: *"a competent web-based, single-tenant, India-GST-focused WMS with excellent transactional depth; not yet mobile-first, multi-channel, analytics-driven or multi-tenant."* Mobile scored ●○○○○ — **~65 web ops screens, 0 warehouse-base mobile screens**. |
| 15 | `WMS_Packaging_Implementation_And_Validation_Plan.md` | 461 | **TASKS** | The authoritative packaging-master build plan (`wms_packaging_types` + extend `wms_product_packaging`). **3 `CREATE TABLE`.** Wins over #13 on conflict. |
| 16 | `WMS_Inbound_Flow_And_PO_Command_Center_Workflow.md` | 436 | **SPEC** | **The PO-as-command-centre design.** Governing principle: *a document owns only the information that legally belongs to it*. Four owners — Receiving Session owns the physical arrival, GRN owns the legal receipt, Invoice owns the finance, **PO owns the lifecycle and gets the consolidation dashboard**. Adds a per-warehouse Receiving Config (receiving mode, GRN timing, QC policy, putaway automation) instead of two parallel workflows. Reframes the scanner as an "Inventory Capture Engine". |
| 17 | `WMS_PO_To_Inventory_And_Scanning_Flow.md` | 426 | **SPEC** | PO→inventory walkthrough with the scan path. **1 `CREATE TABLE`.** |
| 18 | `WMS_Inventory_Identity_And_Scanning_Architecture.md` | 418 | **SPEC** | **The identity model, reconciled against what was built.** Four authoritative layers: container-type catalog (`wms_packaging_types`), item packaging config (`wms_product_packaging` + `container_type_id`/`supplier_id`/`priority`), **single scannable barcode registry** (`wms_item_barcodes`, with `packaging_id` — and **quantity derived from packaging, never stored on the barcode**), UOM rate authority (`wms_item_variant_uom_conversions`, order math only). Net new tables: **0**. Adds a named 4-step identity-resolution contract and a deterministic packaging-resolution order (supplier-specific → supplier-agnostic default → loose). |
| 19 | `WMS_Goods_Receipt_Add_Redesign_And_Consolidation_Plan.md` | 404 | **SPEC** | GRN page redesign + the 5-section consolidation view (later re-homed onto the PO by #16). |
| 20 | `WMS_Gap_Closure_Implementation_Plan.md` | 386 | **TASKS** | Cross-cutting gap closure with a **zero-gap definition of done** per feature (backend + frontend + migration + i18n + mobile + Docker-green). **3 `CREATE TABLE`.** |
| 21 | `WMS_Outbound_Flow_Master_Workflow_Matrix.md` | 361 | **SPEC** | The full outbound state × actor × document matrix. |
| 22 | `WMS_Outbound_Flow_UI_Screens.md` | 351 | **SPEC** | Screen-by-screen outbound UI spec. |
| 23 | `WMS_Scanner_Feature_Design.md` | 329 | **SPEC** | **The scan engine.** Hardware-agnostic pipeline: barcode string → scan capture layer → resolution engine → workflow validation (scan mode declares the expected entity type) → immutable `wms_scan_events` → business logic. **Explicitly rejects scanner-SDK coupling.** Keyboard-wedge first; certify on one device (Zebra DS2208) and every wedge scanner works. Mobile camera deferred but the engine is mobile-ready. Also carries a "schema gotchas confirmed" note (`:75`) that correctly names `filter_definitions` — see P-006. |
| 24 | `WMS_Bulk_Import_Wizard_And_Packaging_Import_Design.md` | 299 | **SPEC** | Reuse the platform 6-stage Import Wizard (`ImportButton` → `ImportModal` → `useImport`) rather than build one; keep the job/audit tables **in the vertical**, not promoted to platform. Explicitly rejects a platform `bulk_import_jobs` table, a generic `ImportJobService` and a platform-wide import history page. |
| 25 | `WMS_Packaging_Implementation_Task.md` | 249 | **TASKS** | Packaging-types build tasks. **1 `CREATE TABLE`.** |
| 26 | `WMS_Pack_Session_Frictionless_Carton_Flow_Design.md` | 233 | **SPEC** | **Ten locked decisions (D1–D10) on the pack-session operator flow.** Carton-based loading stays (6 named downstream dependencies: truck loading, LR/bilty package count, EWB package count, multi-truck split, damage claims, 3PL handover). Auto-create the first carton, track an active carton on the session, auto-create the next on seal (only while units remain), quantity-on-scan, merge repeat scans, remove the "no carton" trap. **No new tables, no new menus.** |
| 27 | `WMS_Outbound_Flow_Gap_Review.md` | 232 | **REVIEW** | Outbound gap audit. |
| 28 | `WMS_Goods_Receipt_View_Popup_Functional_Spec.md` | 230 | **SPEC** | GRN view-modal functional spec. |
| 29 | `WMS_Supplier_Invoice_AP_3WayMatch_Change_Plan.md` | 199 | **SPEC** | **The 3-way-match allocation model.** Rejects a parallel `ap_*` domain; reuses `wms_invoices` with `invoice_type='PURCHASE_INVOICE'`. Adds `po_line_id` to the invoice line and a new `wms_invoice_grn_allocations` junction — the one structure that makes partial invoicing, multiple invoices per PO, one invoice spanning several GRNs, and one GRN line split across invoices all possible without drift. Ships with a signed-off decision list D1–D8 and a P0/P1/P2 status. |
| 30 | `WMS_Outbound_Flow_Cancellation_Spec.md` | 190 | **SPEC** | Outbound cancellation semantics and de-allocation. |
| 31 | `WMS_Inbound_Corrections_Build_Contract.md` | 182 | **SPEC** | **The densest and most rigorous document in the corpus.** Locks the layered-truth model (PO=commitment · ASN=shipment declaration · Receiving Session=inbound shipment, N POs × N ASNs × N GRNs · GRN=single receipt truth · Invoice=billed · Inventory=on-hand, written only by the gateway), with a worked number example. Twelve sections A–L, each traced through six layers (Menu/Access → UI → FE API → endpoint+permission → service → DB) tagged EXISTS/ADD/FIX, and a **7-layer Definition of Done** where a tick requires all seven. Introduces `wms_reconciliation_cases`, `wms_receipt_reversal_requests`, `wms_supplier_returns`, multi-PO/multi-ASN session junctions, and the `owner_id`/`owner_type` grain (`:109`). |
| 32 | `WMS_Inbound_Flow_Implementation_Task.md` | 139 | **TASKS** | Phase-wise execution of #31 with a 7-layer verification gate. |
| 33 | `WMS_Quality_Inspection_Header_Line_Redesign.md` | 130 | **SPEC** | **QC header/line.** Keeps `wms_quality_inspections` as the LINE table (all downstream orchestration is per-line and correct) and adds a thin `wms_quality_inspection_headers` grouping table with a `UNIQUE(grn_id)`, rollup status/result/counters, and a `complete-all` endpoint. One QC number per GRN instead of N. States explicitly that no mobile QC screen exists. |
| 34 | `WMS_Outbound_Flow_Traceability_Audit.md` | 119 | **REVIEW** | Outbound traceability gaps. |
| 35 | `WMS_Outbound_Flow_Accounts_And_WorkQueues.md` | 98 | **SPEC** | Accounts/work-queue screens hanging off outbound. |

## 1.4 The two module audits (2 files, 532 lines)

| # | File | Lines | Kind | What it decided |
|---|---|---|---|---|
| 36 | `warehouse-core/docs/WAREHOUSE_CORE_ISSUES.md` | 215 | **REVIEW** | Audit of `warehouse-core` (migrations `V200001–V200042`, 15 JPA entities, 11 admin pages). 13 findings DB-1…DB-9 / WF-1…WF-5 with a resolution log. Names 6 tables absent from the 72-table design: `wms_equipment_types`, `wms_equipment`, `wms_warehouse_staff`, `wms_distance_cache`, `wms_bulk_import_jobs`/`_rows`, `wms_location_zones`. |
| 37 | `supply-chain-core/docs/SCC_MODULE_ISSUES_ANALYSIS.md` | 317 | **REVIEW** | Audit of `supply-chain-core` (13 migrations `V190001–V190045`, **46 tables**, 46 entities, 22 controllers, 68 services, 17 pages). Full table inventory, 4 orphan tables, 5 UI-orphaned backends, a security finding on a demo controller that triggers live statutory filings, and a §7 Remediation Log that **revises six of its own findings** on closer inspection. |

---

# §2 — The schema, complete and mapped

## 2.1 How I counted

- **72 tables** = `grep -cE "^\s*CREATE TABLE" warehouse-base/docs/spi/WMS_DATABASE_DESIGN.md`. Each was
  mapped to its owning functional module by an `awk` pass that carries the nearest preceding `# Module N:`
  heading and `## N.M <table>` sub-heading down to the `CREATE TABLE` line, so the module assignment is the
  document's own, not mine.
- **Key columns** were extracted by a second `awk` pass over each DDL body, dropping comment lines, table
  constraints, and the eight universal audit columns (`id`, `created_at`, `updated_at`, `created_by`,
  `updated_by`, `deleted_at`, `deleted_by`, `is_active`). Where a CHECK constraint's value list wrapped onto
  its own line the extractor picked up a stray enum literal; those are excluded from the tables below by hand.
- **8 further tables with real DDL** elsewhere in the corpus =
  `grep -rhoE "CREATE TABLE (IF NOT EXISTS )?[a-z_]+"` over `WMS/`, the top-level docs, the task docs and the
  two audits, minus the 72: `wms_packaging_types`, `wms_packaging_classes`, `wms_packaging_rules`,
  `wms_packaging_templates`, `wms_packaging_assets`, `wms_product_packaging_profiles`, `wms_package_events`,
  `wms_invoice_orders`. **80 tables with DDL in total.**
- A further **~45 table names are referenced but never defined** — they belong to the *built* system and are
  known only by name (§2.8). `grep -rhoE "\bwms_[a-z_]+\b"` over the whole warehouse corpus returns **257
  distinct tokens**, but that set is polluted by singular forms, abbreviations and column names, so it is not
  a table count and I do not present it as one.

**New-module legend:** `B` = `warehouse-base` · `W` = `warehouse` · `A` = `warehouse-adapter-<vertical>` ·
`3PL` = `warehouse-3pl` · `IN` = `warehouse-india` · `P` = planning module (out of the five, see P-052).

## 2.2 Module 1 — Warehouse setup & configuration (7 tables)

| # | Table | Purpose | Key columns | New module |
|---|---|---|---|---|
| 1 | `wms_warehouses` | Warehouse master; M:N to platform branches | `warehouse_code`, `warehouse_name`, `warehouse_type`, manager contact, full address + `latitude`/`longitude`/`geocoding_status`, `total_area_sqm`, `total_locations`, `total_pallet_positions`, `operating_hours` (JSONB), `default_putaway_strategy`, `default_pick_method`, `order_cutoff_time`, `timezone`, `status`, `metadata` (JSONB) | **B** |
| 2 | `wms_warehouse_branches` | Warehouse ↔ platform branch junction | `warehouse_id`, `branch_id`, `is_primary` | **B** |
| 3 | `wms_warehouse_locations` | Building / floor level between warehouse and zone | `location_code`, `warehouse_id`, `location_type`, `floor_level`, `building`, `area_sqm`, `total_zones`, address, `is_temperature_controlled`, `is_hazmat_certified`, temp min/max | **B** — but *dropped by the prior art's own review* (`WAREHOUSE_CORE_ISSUES.md` DB-2) |
| 4 | `wms_zones` | Zone within a warehouse | `zone_code`, `warehouse_location_id`, `warehouse_id`, `zone_type` (RECEIVING/COLD_STORAGE/QUARANTINE/…), temp + humidity min/max, `hazmat_classes_allowed`, `max_capacity_pallets/units/weight_kg`, `pick_priority` | **B** |
| 5 | `wms_locations` | The bin. Flat `aisle`/`rack`/`level`/`bin` under a zone | `location_code`, `warehouse_id`, `zone_id`, `aisle`, `rack`, `level`, `bin`, `location_type` (RACK_BIN/CAROUSEL_SLOT/…), `width/depth/height_cm`, `weight_capacity_kg`, `volume_capacity_cc`, `max_units`, `storage_rule` (SINGLE_SKU/…), `is_fixed_location`, `fixed_item_id`, `pick_sequence`, `putaway_priority`, `abc_velocity_class`, hazmat + temp flags | **B** |
| 6 | `wms_dock_doors` | Dock door master with current assignment | `door_code`, `warehouse_id`, `door_type`, `has_leveler`, `has_shelter`, `has_temperature_control`, `compatible_vehicles` (JSONB), `current_assignment_type`, `current_assignment_id` | **W** |
| 7 | `wms_dock_appointments` | Booked dock slots, inbound and outbound | `dock_door_id`, `appointment_type`, `scheduled_start`/`_end`, `slot_duration_minutes`, `reference_type`/`reference_id`, `supplier_id`, `carrier_name`, `vehicle_number`, `driver_name`/`_phone`, `actual_arrival`/`_departure` | **W** |

## 2.3 Module 2 — Item master & catalogue (17 tables)

| # | Table | Purpose | Key columns | New module |
|---|---|---|---|---|
| 8 | `wms_item_categories` | Category master with inspection/putaway defaults | `category_code`, `category_name`, `default_inspection_type`, `default_putaway_strategy` | **B** |
| 9 | `wms_item_subcategories` | Subcategory under a category | `category_id`, `subcategory_code`, same defaults | **B** |
| 10 | `wms_units_of_measure` | UoM master | `uom_code`, `uom_name`, `uom_type` | **B** |
| 11 | `wms_uom_conversions` | **Per-item** conversion between two UoMs | `item_id`, `from_uom_id`, `to_uom_id`, `conversion_factor` | **B** — correct grain; satisfies R2 `T-011` |
| 12 | `wms_items` | The SKU. Thin header; six side tables carry the rest | `sku_code`, `item_name`, `category_id`, `subcategory_id`, `product_family`, `commodity_code`, **`tracking_mode`**, `base_uom_id`, `purchase_uom_id`, `sale_uom_id`, `sku_auto_generated`, `status`, `metadata` (JSONB) | **B** |
| 13 | `wms_item_physical` | Weight / dimensions / handling | `weight_gross_kg`, `weight_net_kg`, `length/width/height_cm`, `volume_cc`, `is_oversized`, `is_stackable`, `is_fragile` | **B** |
| 14 | `wms_item_storage` | Storage conditions and hazmat | `storage_type`, temp + humidity min/max, `shelf_life_days`, `is_hazmat`, `hazmat_un_number`, `hazmat_class`, `hazmat_packing_group`, `hazmat_proper_shipping_name`, `hazmat_subsidiary_classes` | **B** |
| 15 | `wms_item_procurement` | Buying attributes | `default_supplier_id`, `lead_time_days`, `min_order_qty`, `economic_order_qty`, `standard_cost`, `last_purchase_price`, `retail_price` | **B** |
| 16 | `wms_item_stocking` | Reorder policy | `reorder_point`, `safety_stock`, `min_stock`, `max_stock`, `low_stock_alert_level` | **B** — grain contested, see P-030 |
| 17 | `wms_item_analysis` | Five classification axes | `abc_class`, `xyz_class`, **`ved_class`**, **`fsn_class`**, **`hml_class`** | **B** |
| 18 | `wms_item_service_parts` | Service-parts attributes | `part_type`, `criticality_level`, **`is_vor_eligible`**, `warranty_months`, **`is_core_exchange`**, `core_deposit_amount` | **A** |
| 19 | `wms_item_barcodes` | Many barcodes per item | `item_id`, `barcode` (UNIQUE), `barcode_format` (CODE_128/EAN-13/…), `is_primary` | **B** |
| 20 | `wms_item_images` | Images, via the **platform** documents table | `item_id`, **`platform_document_id`**, `image_type`, `sort_order`, `is_primary` | **B** |
| 21 | `wms_item_supersessions` | Predecessor → successor chains | `predecessor_item_id`, `successor_item_id`, `effective_date`, **`chain_sequence`** | **B** (adapter tension, P-031) |
| 22 | `wms_interchangeability_groups` | "Any of these fits" groups | `group_code`, `group_name` | **B** (same tension) |
| 23 | `wms_interchangeability_group_items` | Group membership, ranked and dated | `group_id`, `item_id`, `priority_order`, `effective_from`, `effective_to` | **B** |
| 24 | `wms_item_classification_history` | Audited ABC/XYZ/VED/FSN/HML reclassification | `classification_type`, `old_class`, `new_class`, `classification_date`, `period_start`/`_end`, `calculation_basis`, `is_auto_calculated`, `is_approved`, `approved_by`, `approved_at` | **B** |

## 2.4 Module 3 — Inbound (8 tables) · all **W**

| # | Table | Purpose | Key columns |
|---|---|---|---|
| 25 | `wms_purchase_orders` | PO header | `po_number`, `supplier_id`, `warehouse_id`, `order_date`, `expected_delivery_date`, `currency`, `payment_terms`, `subtotal`/`tax_amount`/`total_amount`, `priority`, `approved_by`, `approval_date`, `approval_threshold`, **`spi_recommendation_id`**, **`over_receipt_tolerance_pct`**, status `DRAFT…PARTIALLY_RECEIVED…` |
| 26 | `wms_purchase_order_lines` | PO line with a receiving counter | `line_number`, `item_id`, `ordered_quantity`, `uom_id`, `unit_price`, `line_total`, `expected_delivery_date`, `received_quantity`, `accepted_quantity`, `rejected_quantity`, `remaining_quantity`, `line_status` |
| 27 | `wms_advanced_shipping_notices` | Supplier's shipment declaration | `asn_number`, `supplier_id`, `carrier_name`, `tracking_number`, `vehicle_number`, `expected_arrival`, `total_pallets`/`_cases`/`_loose_items`, `total_weight_kg`, `total_volume_cc` |
| 28 | `wms_asn_lines` | Declared line with lot/serial | `asn_id`, `purchase_order_id`, `po_line_id`, `item_id`, `expected_quantity`, `lot_number`, `serial_numbers` (JSONB) |
| 29 | `wms_goods_receipts` | GRN header | `grn_number`, `purchase_order_id`, `asn_id`, `supplier_id`, `dock_door_id`, `received_by`, `received_date`, `vehicle_number`, `tracking_number`, **`is_blind_receipt`** |
| 30 | `wms_goods_receipt_lines` | GRN line — the receipt truth | `po_line_id`, `item_id`, `expected_quantity`, `received_quantity`, `accepted_quantity`, `rejected_quantity`, `lot_number`, `expiry_date`, `condition`, `rejection_reason`, `damage_notes` |
| 31 | `wms_quality_inspections` | Inspection at **GRN-line** grain | `grn_id`, `grn_line_id`, `inspector_id`, `inspection_type` (FULL/SAMPLING/…), `sampling_plan`, `sample_size`, `inspected_quantity`, `inspection_criteria` (JSONB checklist), `result`, `rejection_reason_code`, `disposition` (…/`RETURN_TO_SUPPLIER`), started/completed timestamps |
| 32 | `wms_putaway_tasks` | Directed / zone-based putaway | `grn_line_id`, `quantity`, `lot_number`, `serial_number_id`, `putaway_strategy`, `suggested_location_id`, `actual_location_id`, `assigned_to`, `priority`, `staging_location_id`, `is_staged` |

## 2.5 Module 4 — Inventory (8 tables)

| # | Table | Purpose | Key columns | New module |
|---|---|---|---|---|
| 33 | `wms_inventory` | **The balance.** Grain = item × location × warehouse × lot | `quantity_on_hand`, `quantity_allocated`, `quantity_picked`, `quantity_packed`, `quantity_quality_hold`, `quantity_damaged`, `quantity_blocked`, **`quantity_available` GENERATED ALWAYS … STORED**, `stock_status`, `average_cost`, `last_receipt_cost`, `last_movement_date`, `last_count_date`, `receipt_date`. Carries `CHECK (quantity_on_hand >= 0)`. **No `owner_id`. No `@Version`. Invalid UNIQUE at `:1898`.** | **B** |
| 34 | `wms_stock_transactions` | **The movement log.** Declared immutable | `item_id`, `lot_id`, `serial_number_id`, `transaction_type` (18 values), `quantity` (signed), `uom_id`, `from_location_id`, `to_location_id`, `from_status`, `to_status`, `reference_type`/`_id`/`_number`, `unit_cost`, `total_cost`, `reason_code`, `performed_by`, `transaction_date`. **Single-sided; no `location_id`; no DB immutability guard.** | **B** |
| 35 | `wms_lots` | Lot as a real entity with a hold workflow | `lot_number`, `item_id`, `supplier_lot_number`, `supplier_id`, `manufacture_date`, `expiry_date`, `receipt_date`, `status`, `hold_reason`, `held_by`, `held_at`, `grn_id` | **B** |
| 36 | `wms_serial_numbers` | Serial as an entity with current state | `serial_number`, `item_id`, `lot_id`, `current_location_id`, `current_warehouse_id`, `status` (IN_STOCK…SCRAPPED), `grn_id`, `shipment_id`, `ship_date`, `customer_reference`, `warranty_start`/`_end_date`, **`linked_core_serial_id`** | **B** |
| 37 | `wms_stock_adjustments` | Adjustment header with approval | `adjustment_number`, `adjustment_type` (POSITIVE/NEGATIVE), `reason_code` (CYCLE_COUNT_VARIANCE/FOUND_STOCK/CUSTOMER_RETURN_ADJ/…), `total_lines`, `total_value_impact`, `requires_approval`, `approved_by`/`_at` | **W** |
| 38 | `wms_stock_adjustment_lines` | Adjustment line with variance | `item_id`, `location_id`, `lot_id`, `serial_number_id`, `system_quantity`, `actual_quantity`, `variance_quantity`, `from_status`/`to_status`, `from_location_id`/`to_location_id`, `unit_cost`, `variance_value` | **W** |
| 39 | `wms_transfer_orders` | Warehouse→warehouse and zone→zone | `transfer_number`, **`transfer_type`** (BIN_TO_BIN / INTRA / INTER), `source_warehouse_id`, `destination_warehouse_id`, `source_zone_id`, `destination_zone_id`, `requested_date`, `expected_arrival_date`, `requires_approval` | **W** |
| 40 | `wms_transfer_order_lines` | Transfer line | `item_id`, `quantity`, `lot_id`, `source_location_id`, `destination_location_id`, `picked_quantity`, `received_quantity` | **W** |

## 2.6 Module 5 — Outbound (11 tables)

| # | Table | Purpose | Key columns | New module |
|---|---|---|---|---|
| 41 | `wms_carriers` | Carrier master | `carrier_code`, `carrier_type` (GROUND/…), contacts, `website`, `service_levels` (JSONB), **`tracking_url_template`**, `api_enabled` | **B** |
| 42 | `wms_sales_orders` | SO header | `order_number`, `external_reference`, `customer_name`/`_code`, **`dealer_id`**, full ship-to block, `order_type`, `priority`, order/requested/promised dates, `carrier_id`, `service_level`, `shipping_method`, money block, **`allow_partial_ship`**, **`allow_backorder`**, `is_credit_hold`, **`spi_order_id`** | **W** |
| 43 | `wms_sales_order_lines` | SO line with the full fulfilment ladder | `ordered_quantity`, `unit_price`, `allocated_quantity`, `picked_quantity`, `packed_quantity`, `shipped_quantity`, `backordered_quantity`, **`original_item_id`**, **`substitution_reason`** | **W** |
| 44 | `wms_stock_allocations` | **Open-item allocation ledger** | `sales_order_line_id`, `item_id`, `location_id`, `lot_id`, `serial_number_id`, `allocated_quantity`, **`allocation_method`**, `status` | **B** (ledger dimension) |
| 45 | `wms_waves` | Wave as a real object | `wave_number`, `wave_type`, `grouping_criteria` (JSONB), `total_orders`/`_pick_lines`/`_units`, `ship_by_time`, `pick_progress_pct`, `pack_progress_pct`, released/pick-started/pick-completed/pack-completed/shipped timestamps | **W** |
| 46 | `wms_wave_orders` | Wave ↔ SO junction | `wave_id`, `sales_order_id`, `sequence_number` | **W** |
| 47 | `wms_pick_tasks` | The pick task | `wave_id`, `sales_order_line_id`, `allocation_id`, **`pick_method`** (DISCRETE/…), `requested_quantity`, `picked_quantity`, `source_location_id`, `lot_id`, `serial_number_id`, `pick_sequence`, `assigned_to`, **`is_short_pick`**, **`short_pick_quantity`**, **`short_pick_action`** | **W** |
| 48 | `wms_shipments` | Shipment header | `shipment_number`, `carrier_id`, `service_level`, `tracking_number`, `dock_door_id`, ship-to block, `total_cartons`/`_pallets`/`_weight_kg`/`_volume_cc`, `shipping_cost`, **`bol_number`**, **`manifest_number`**, packed/shipped/delivered timestamps, **`pod_signature`**, `pod_photo_url` | **W** |
| 49 | `wms_shipment_orders` | Shipment ↔ SO junction (many orders per shipment) | `shipment_id`, `sales_order_id` | **W** |
| 50 | `wms_shipment_cartons` | **The handling unit** | `carton_number`, `carton_type`, `weight_kg`, **`expected_weight_kg`**, dims, `tracking_number`, `label_printed`, **`contains_hazmat`**, `packed_by`/`_at`, `verified_by`/`_at`, status OPEN→SEALED | **W** |
| 51 | `wms_carton_items` | Carton contents, to the serial | `carton_id`, `item_id`, `sales_order_line_id`, `quantity`, `lot_number`, `serial_number` | **W** |

## 2.7 Modules 6–15 (21 tables)

| # | Table | Module | Purpose | Key columns | New |
|---|---|---|---|---|---|
| 52 | `wms_return_authorizations` | 6 Returns | RMA header | `rma_number`, `customer_name`/`_code`, `dealer_id`, `original_order_id`/`_number`, `return_reason_code` (WRONG_PART_SHIPPED / WRONG_PART_ORDERED / WARRANTY_CLAIM / …), `expected_condition`, `approved_credit_type` (FULL_REFUND/…), `credit_amount`, `rma_date`, **`expiry_date`** | **W** |
| 53 | `wms_return_authorization_lines` | 6 | RMA line with grading | `item_id`, `quantity`, `original_serial_number`, `original_lot_number`, **`inspected_grade`**, **`disposition`** (RETURN_TO_STOCK / REPAIR / …) | **W** |
| 54 | `wms_core_exchanges` | 6 | **Core deposit / core return** | `sales_order_line_id`, `new_item_id`, `new_serial_number`, `core_item_id`, `core_deposit_amount`, **`core_return_deadline`**, `core_received_date`, `core_serial_number`, `core_condition_grade`, `credit_issued`, `credit_amount`, `credit_issued_date` | **A** |
| 55 | `wms_cycle_count_programs` | 7 Counting | The counting **policy** object | `program_type` (ABC_BASED / DISCREPANCY_TRIGGERED / …), `frequency_days`, **`schedule_cron`**, `next_scheduled_date`, `scope_zone_ids`/`scope_abc_classes`/`scope_item_ids` (JSONB), **`is_blind_count`**, **`recount_threshold_pct`**, **`approval_threshold_pct`**, **`freeze_locations`**, `max_tasks_per_run` | **W** |
| 56 | `wms_cycle_count_tasks` | 7 | Generated count task | `program_id`, `count_type`, `location_id`, `item_id`, `assigned_to`, **`count_attempt`**, **`is_frozen`**, status …RECOUNT_REQUIRED | **W** |
| 57 | `wms_cycle_count_results` | 7 | Counted result → adjustment | `system_quantity`, `counted_quantity`, `variance_quantity`, `variance_pct`, `unit_cost`, `variance_value`, **`is_within_tolerance`**, `approved_by`/`_at`, **`adjustment_id`**, `counted_by`/`_at` | **W** |
| 58 | `wms_label_templates` | 8 Labels | Label template master | `template_code`, `label_type` (ITEM/BIN/…), **`template_format`**, **`template_content`**, `width_mm`, `height_mm`, `default_barcode_format`, **`default_printer_name`**, `is_default` | **B** |
| 59 | `wms_alert_rules` | 9 Alerts | Rule engine for operational alerts | `alert_type` (LOW_STOCK / VOR_ORDER / GRN_PENDING_INSPECTION / DOCK_APPOINTMENT_MISSED / EQUIPMENT_MAINTENANCE_DUE / HIGH_QUARANTINE_VOLUME / CUSTOM), `trigger_conditions` (JSONB), `urgency`, `notify_in_app`/`_email`/`_sms`/`_push`, `recipient_roles`/`recipient_user_ids`, **`escalation_minutes`**, **`escalation_to_roles`** | **B** |
| 60 | `wms_alert_history` | 9 | Fired alerts with an ack/resolve trail | `alert_rule_id`, `reference_type`/`_id`, `title`, `message`, `triggered_at`, `acknowledged_at`/`_by`, `resolved_at`/`_by`, `is_escalated`, `escalated_at` | **B** |
| 61 | `wms_kpi_snapshots` | 10 Analytics | Daily/period KPI roll-up, 29 metrics | `snapshot_date`, `snapshot_period`, `total_sku_count`, `total_stock_units`, `total_stock_value_cost`/`_retail`, `location_utilization_pct`, `inventory_accuracy_pct`, `shrinkage_value`, `dead_stock_pct`, `dock_to_stock_hours_avg`, `receiving_accuracy_pct`, `putaway_cycle_time_hours`, `order_fill_rate_pct`, `perfect_order_rate_pct`, `pick_accuracy_pct`, **`vor_fill_rate_pct`**, **`vor_response_time_hours`**, `backorder_rate_pct`, `same_day_ship_rate_pct`, `return_processing_hours`, `return_to_stock_rate_pct`, **`core_return_rate_pct`** | **W** |
| 62 | `wms_dashboard_tasks` | 10 | Operator to-do list | `task_date`, `priority`, `due_time`, `assigned_to`, `is_system_generated`, `source_type`, `is_completed` | **W** |
| 63 | `wms_cross_dock_plans` | 11 | Inbound line → outbound line, no putaway | `grn_id`, `grn_line_id`, `asn_id`, `sales_order_id`, `sales_order_line_id`, `item_id`, `quantity`, **`cross_dock_type`** | **W** |
| 64 | `wms_kit_definitions` | 12 Kitting | Versioned, effective-dated kit | `kit_item_id`, **`kit_type`**, **`version`**, `effective_from`/`_to`, `assembly_instructions`, `estimated_assembly_minutes` | **B** |
| 65 | `wms_kit_components` | 12 | BOM line | `kit_definition_id`, `component_item_id`, `quantity`, `uom_id`, `sort_order`, **`is_optional`** | **B** |
| 66 | `wms_kit_work_orders` | 12 | Assemble / disassemble order | `work_order_number`, `kit_definition_id`, **`work_order_type`**, `quantity`, `assigned_to`, `scheduled_date` | **W** |
| 67 | `wms_vas_service_types` | 13 VAS | Priced VAS catalogue | `service_code`, `service_category` (RELABELING / DOCUMENT_INSERTION / …), **`billing_unit`**, **`unit_rate`**, **`estimated_minutes_per_unit`** | **W** (rate → **3PL**, P-047) |
| 68 | `wms_vas_work_orders` | 13 | VAS execution record | `service_type_id`, `sales_order_id`, `item_id`, `quantity`, `instructions`, `qc_required`/`qc_passed`/`qc_by`, **`labor_minutes`**, **`materials_cost`**, `total_cost` | **W** |
| 69 | `wms_suppliers` | 14 Supplier | Supplier master | `supplier_code`, `supplier_type` (MANUFACTURER/…), contacts, address, `lead_time_days`, `min_order_quantity`, `payment_terms`, `currency`, **`is_asn_capable`**, `preferred_carrier`, `certifications` (JSONB), **`inspection_strategy`** | **B** |
| 70 | `wms_supplier_items` | 14 | Supplier's catalogue for our SKU | **`supplier_part_number`**, **`supplier_barcode`**, `unit_price`, `currency`, **`price_effective_from`/`_to`**, `lead_time_days`, `min_order_quantity`, `is_preferred`, `priority_rank` | **B** |
| 71 | `wms_supplier_performance` | 14 | Scorecard per period | `period_start`/`_end`, on-time delivery counts + pct, quality accept rate, **`asn_compliance_pct`**, order accuracy, `avg_lead_time_days` vs `promised_lead_time_days`, `avg_response_time_hours`, **`overall_score`**, **`traffic_light`** | **B** |
| 72 | `wms_documents` | 15 Docs | Polymorphic document link **with its own `file_url`** | `entity_type`, `entity_id`, `document_type` (PURCHASE_ORDER_PDF / SHIPPING_LABEL / DAMAGE_PHOTO / CYCLE_COUNT_SHEET / CERTIFICATE_OF_ORIGIN / …), `document_name`, **`file_url`**, `file_type`, `file_size_bytes`, `is_system_generated` | **B** — but see P-036 |

## 2.7a The 8 further tables with DDL, defined outside `WMS_DATABASE_DESIGN.md`

| Table | Source | Purpose | New module |
|---|---|---|---|
| `wms_packaging_types` | `WMS_Packaging_Implementation_And_Validation_Plan.md` | **The container-type catalogue** — `type_code`, `packaging_class` (CARTON/PALLET/CRATE/BAG/CUSTOM), L×W×H, `tare_weight_kg`, `max_weight_kg`, `volumetric_divisor`, `is_default` | **B** |
| `wms_packaging_classes` | `WMS_Packaging_Architecture_Design.md` | Class above type | **B** (contested — P-035) |
| `wms_packaging_rules` | same | Rules selecting a packaging | **W** |
| `wms_packaging_templates` | same | Reusable packing plans | **W** |
| `wms_packaging_assets` | same | Physical packing materials as stock | **W** (F-060) |
| `wms_product_packaging_profiles` | same | Per-item packaging profile | **B** — superseded by `wms_product_packaging` per #18 |
| `wms_package_events` | same | Package lifecycle events | **W** |
| `wms_invoice_orders` | `WAREHOUSE_ARCHITECTURE_REVIEW.md` (V200075) | **Invoice ↔ order junction** replacing polymorphic columns — `invoice_id`, `order_type` (PURCHASE_ORDER/SALES_ORDER/TRANSFER_ORDER), `order_id`, `UNIQUE(invoice_id, order_type, order_id)` | **W** |

## 2.8 Tables named by the prior art but never given DDL (the built system)

These are known only by name, from the review documents. They are **not** a schema — they are a checklist of
objects the built system had that the 72-table design lacked, and each is a question the new set must answer.

**`warehouse-core` extras** (`WAREHOUSE_CORE_ISSUES.md` table inventory): `wms_equipment_types`,
`wms_equipment`, `wms_warehouse_staff`, `wms_distance_cache` *(deleted — no callers)*, `wms_location_zones`
*(deleted — dead junction)*, `wms_bulk_import_jobs`, `wms_bulk_import_job_rows`.

**`warehouse-base` extras** (from `WMS/`): `wms_item_variants`, `wms_item_variant_uom_conversions`,
`wms_item_references`, `wms_product_packaging`, `wms_packaging_levels`, `wms_receiving_sessions`,
`wms_receiving_session_pos`, `wms_receiving_session_asns`, `wms_receiving_scan_logs`, `wms_scan_events`,
`wms_scan_mode_rules`, `wms_quality_inspection_headers`, `wms_reconciliation_cases`,
`wms_receipt_reversal_requests`, `wms_receipt_reversal_lines`, `wms_supplier_returns`,
`wms_supplier_return_lines`, `wms_pack_sessions`, `wms_pack_session_items`, `wms_consignments`,
`wms_consignment_cartons`, `wms_consignment_lines`, `wms_freight_orders`, `wms_freight_order_lines`,
`wms_freight_charge_adjustments`, `wms_carrier_bills`, `wms_shipping_documents`, `wms_gate_pass`,
`wms_delivery_challan`, `wms_invoices`, `wms_invoice_lines`, `wms_invoice_tax_lines`,
`wms_invoice_additional_charges`, `wms_invoice_grn_allocations`, `wms_payment_records`,
`wms_three_way_matches`, `wms_three_way_match_lines`, `wms_approvals`, `wms_document_attachments`,
`wms_po_supplier_notifications`, `wms_activity_log`, `wms_replenishment_rules`, `wms_replenishment_tasks`,
`wms_slotting_rules`, `wms_slotting_tasks`, `wms_pick_strategies`, `wms_customer_tracking_tokens`,
`wms_webhook_subscriptions`, `wms_webhook_delivery_log`, `wms_partner_api_keys`, `wms_ecommerce_channels`,
`wms_ecommerce_order_sync_log`, `wms_gl_postings`, `wms_inventory_valuations`, `wms_valuation_methods`,
`wms_accounting_connectors`, `wms_barcode_symbologies`, `wms_container_instances` *(deferred)*.

> **Honesty note.** I did not verify that every one of these was built; I verified only that the prior art
> names them. Several (`wms_gl_postings`, `wms_inventory_valuations`, `wms_valuation_methods`,
> `wms_ecommerce_*`, `wms_webhook_*`, `wms_slotting_*`, `wms_replenishment_*`) appear in *gap* sections and
> are almost certainly **proposed, not built** — `WMS_Competitive_Gap_Analysis_And_Roadmap.md` §2 lists
> valuation, reorder automation and e-commerce connectors under **❌ Missing**. Treat the list as a naming
> vocabulary, not an inventory.

## 2.9 The `supply-chain-core` 46 tables — the India pack and the shared masters

Inventory taken verbatim from `SCC_MODULE_ISSUES_ANALYSIS.md` §2 (which states its own method: full read of
every migration cross-checked against entities, repositories, controllers and frontend).

| Group | Tables | New module |
|---|---|---|
| **Shared masters** | `scc_units_of_measure`, `scc_uom_conversions`, `scc_carriers`, `scc_suppliers`, `scc_brands`, `scc_customers`, `scc_customer_addresses`, `scc_document_sequences` | **B** — fold in, do not recreate a master module (P-042) |
| **Fleet / driver** | `scc_vehicle_type_lookup`, `scc_vehicles`, `scc_vehicle_transfers`, `scc_vehicle_documents`, `scc_vehicle_maintenance_logs`, `scc_vehicle_trip_logs`, `scc_vehicle_fuel_logs`, `scc_driver_licenses`, `scc_driver_employment`, `scc_driver_documents` | **out of scope** — this is TMS (P-060) |
| **GST reference** | `scc_hsn_tax_master`, `scc_gst_state_codes`, `sac_master` | **IN** |
| **Relational tax engine** | `tax_components`, `tax_entity_types`, `tax_rules`, `tax_rule_components`, `tax_rule_conditions`, `tax_resolution_audit` | **IN** |
| **E-invoice / e-way-bill compliance** | `scc_compliance_providers`, `scc_compliance_provider_environments`, `scc_compliance_credential_specs`, `scc_gstin_profiles`, `scc_compliance_registrations`, `scc_compliance_credentials`, `scc_compliance_auth_sessions`, `scc_compliance_documents`, `scc_compliance_tasks`, `scc_compliance_api_logs`*, `scc_irn_cancellations`*, `scc_ewb_vehicle_updates`, `scc_ewb_cancellations`, `scc_ewb_extensions`*, `scc_ewb_consolidated`, `scc_ewb_consolidated_items`, `scc_compliance_rules`, `scc_compliance_rule_conditions` | **IN** |
| **Wrongly created** | `permission_dependencies` (defensive `CREATE TABLE IF NOT EXISTS` inside a tax migration) | **delete** — R1 `C-017` |

`*` = deleted by the prior art's own remediation as orphans (no repository, no service).

---

# §3 — Triage

**Verdict key:** KEEP · ADAPT · CONTRADICTED · OBSOLETE · DUPLICATE.
**Severity:** BLOCKER / MAJOR / MINOR. **Version:** v1 / v1.1 / v2 / v3.

## 3.1 False premises — the section that pays for the whole review

### `P-001` · CONTRADICTED · **BLOCKER** · `all` · **v1**
**The "pre-production, edit migrations in place" methodology.** Fourteen prior-art documents instruct the
builder to edit already-shipped Flyway files rather than write a new one, and attribute the rule to CLAUDE.md.
- *Prior art:* `WAREHOUSE_CORE_ISSUES.md:7` — "*the CLAUDE.md rule is that the DB is rebuilt from scratch on
  every Docker build, so all schema changes must be made in-place in the original `CREATE TABLE` migration,
  never as new `ALTER TABLE` / restructure migrations*"; `WMS_Inbound_Corrections_Build_Contract.md:6`;
  `WMS_Quality_Inspection_Header_Line_Redesign.md:3`; `SCC_MODULE_ISSUES_ANALYSIS.md:247`;
  `WMS_Inventory_Identity_And_Scanning_Architecture.md:30`; and 9 more
  (`grep -rli "edit.*migration.*in place|migrations in place|in-place|edit the original"` → 14 files).
- *Live codebase:* `grep -c -i "pre-produc" CLAUDE.md` → **0**. No in-place rule exists in `CLAUDE.md`.
  The house style is the opposite and is provable: `acc_companies` created in
  `accounting-base/.../V600001__Create_acc_companies_and_external_refs.sql`, altered in
  `V600142__Alter_acc_companies_entry_lock_and_national_tax_id.sql`; `acc_audit_events` created in
  `V600111`, altered in `V600121`; `dococr_jobs` created in `doc-ocr-ai/.../V700000__Create_doc_ocr_ai_tables.sql`,
  altered in `V700003` and `V700006`; `dococr_field_definitions` altered in `V700012` and `V700013`.
  And `FlywayConfiguration.java:246-264` runs a blind `repair()` + one retry on any failure, so a checksum
  break caused by an in-place edit does **not** fail loudly.
- **Do:** state forward-only additive migration as a rule in the new set's build spec, in the same paragraph
  that gives the band. Delete every in-place instruction inherited from the prior art. If a "rebuild from
  scratch in dev" convenience is genuinely wanted, it must be a documented dev-only script, never a rule that
  licenses editing a released file.

### `P-002` · CONTRADICTED · **BLOCKER** · `all` · **v1**
**Every migration version in the prior art is void.** The corpus cites three bands: `V190001–V190045`
(supply-chain-core), `V200001–V200042`+ (warehouse-core; `WMS_DATABASE_DESIGN.md:126-130` — "*WMS migrations
start at **V200001** … the current highest migration is V200001 (`V200001__Create_warehouse_menus.sql`)*"),
and `V210000–V210131` (warehouse-base; **60 distinct `V21xxxx` versions** referenced across `warehouse-base/docs`).
- *Live codebase:* all three bands are empty here (`find . -name "V19[0-9][0-9][0-9][0-9]__*.sql" -not -path "*/target/*"` → 0;
  same for `V20xxxx` and `V21xxxx`), so there is no collision — but the decided allocation is
  **V500000–V549999** (R1 `C-003`). Every "edit V210007 in place", "fold V200042 into V200005", "add to
  V210055's CHECK", "extend V950056" instruction is unexecutable.
- **Do:** treat every `V1900xx` / `V200xxx` / `V210xxx` / `V950xxx` reference as a *label for a logical
  change*, never as a file. Re-key them onto `V500000+` in the new set. **DUPLICATE of `C-001`/`C-003` for the
  band itself; recorded here because the prior art carries ~115 concrete version numbers that a copy-paste
  would import wholesale.**

### `P-003` · CONTRADICTED · **BLOCKER** · `warehouse-base` · **v1**
**`supply-chain-core` and its 46 `scc_*` tables do not exist.** The prior art treats SCC as a live upstream
module owning the UoM, carrier, supplier, customer, brand, vehicle, HSN and tax masters, with counted
downstream FK usage (`SCC_MODULE_ISSUES_ANALYSIS.md` §4.4: `scc_units_of_measure` **26** refs,
`scc_carriers` **18**, `scc_suppliers` **13**, `scc_vehicles` 8, `scc_customers` 5, `scc_brands` 5,
`scc_customer_addresses` 4, `scc_hsn_tax_master` 3).
- *Live codebase:* `ls supply-chain-core` → `No such file or directory`;
  `grep -rln "scc_units_of_measure\|scc_suppliers\|scc_carriers\|scc_customers\|scc_hsn_tax_master\|sac_master\|tax_rules" --include=*.sql --include=*.java .` (whole tree, targets excluded) → **0 files**.
  The only surviving trace is a comment: `platform/.../V663__Grant_branch_admin_branch_safe_permissions.sql:18`
  lists "`scc_*`" among pages with no branch filtering.
- **Do:** every `scc_*` FK in the prior art becomes a `wh_*` table owned by `warehouse-base`. §2.9 gives the
  fold-in list. **This is also the single largest source of silent breakage** if a prior-art DDL block is
  pasted into a new migration — the FK target will not exist and Flyway will fail at boot.
  Partly DUPLICATE of R1 `AF-1`; the table-level consequence is new.

### `P-004` · CONTRADICTED · **MAJOR** · `warehouse-base` · **v1**
**`warehouse-core` and its ~17 `wms_*` tables, 15 entities and 11 admin pages do not exist.**
- *Prior art:* `WAREHOUSE_CORE_ISSUES.md` "Tables in scope" table; §"Confirmed not problems" asserts all 11
  cache names are registered in platform `CacheConfiguration.java`.
- *Live codebase:* `ls warehouse-core` → `No such file or directory`. `CacheConfiguration.java` registers 202
  names (R1 `C-042`) and **none** is `statistics.wms_*`.
- **Do:** discard the module boundary; keep the *finding classes* (§3.5, P-055).

### `P-005` · CONTRADICTED · **MAJOR** · `all` · **v1**
**`warehouse-base` as built — ~65 web operations screens, `InventoryOrchestrationService`,
`ScannerService`, `ShipmentWorkflowService`, `ReceivingWorkflowService`, `WmsUomConvertibilityService`,
`TaxResolutionService`, the R2-backed document stack — does not exist.** Every `EXISTS`, `already built`,
`reuse`, `FIX` and `zero callers` verdict in the 25-file `WMS/` folder is a statement about a different
checkout.
- *Live codebase:* `ls warehouse-base warehouse` → `No such file or directory`. Root module dirs are
  `accessories accounting accounting-adapter-dealer accounting-base accounting-india assets automotive
  business-models dealer doc-ocr-ai field-service healthapp insurance insurance-360 lead-sharing mobile
  platform product-lift services shared submittals website` (+ `docs`, `node_modules`).
- **Do:** read the `WMS/` folder with a global find-and-replace of *"exists"* → *"was decided"*. The
  **decisions** survive intact and are the best material in the corpus; the **status** does not. Every
  three-column EXISTS/ADD/FIX table becomes a single-column build list. Note this is *not* the same as R1's
  `AF-1`, which observed the directories were absent; the consequence here is that ~7,300 lines of
  present-tense text must be re-tensed before it can be used.

### `P-006` · CONTRADICTED · **MAJOR** · `all` · **v1**
**`grid_filter_definitions` — a table that has never existed — is named in 6 prior-art documents, 14 times.**
`WMS_Outbound_Flow_Implementation_Task.md:77,163,257`; `WMS_Gap_Closure_Implementation_Plan.md:37,138,354`;
`WMS_Outbound_Flow_UI_Screens.md:51,99`; `WMS_Packaging_Implementation_And_Validation_Plan.md:255`;
`WMS_Packaging_Implementation_Task.md:201`; `WMS_Outbound_Flow_Accounts_And_WorkQueues.md:85`;
`WMS_Outbound_Flow_Gap_Review.md:184`; `spi/WMS_IMPLEMENTATION_TASKS.md:733`.
- *Live codebase:* `grep -rl "grid_filter_definitions" --include=*.sql --include=*.java .` (targets excluded)
  → **0 files**. The real table is `filter_definitions` (CLAUDE.md; created in V229).
- *The corpus knows this and did not propagate the fix:* `WMS_Scanner_Feature_Design.md:75` — "*the real
  grid-filter table is **`filter_definitions`** (not `grid_filter_definitions`)*". One document out of seven
  is right.
- **Do:** a single global correction in the new set. Inserting into `grid_filter_definitions` fails at Flyway
  and crash-loops the backend. DUPLICATE of R1 `CM-4` at the rule level; the six specific carriers are new.

### `P-007` · CONTRADICTED · **MAJOR** · `warehouse-base` · **v1**
**JSONB on eleven business tables.** `WMS_DATABASE_DESIGN.md:99` makes it a convention —
"*Flexible metadata | `JSONB DEFAULT '{}'::jsonb`*" — and then uses it on `wms_warehouses`
(`operating_hours`, `metadata`), `wms_warehouse_locations`, `wms_zones`, `wms_dock_doors`
(`compatible_vehicles`), `wms_items` (`metadata`), `wms_asn_lines` (`serial_numbers`),
`wms_quality_inspections` (`inspection_criteria`), `wms_carriers` (`service_levels`), `wms_suppliers`
(`certifications`), `wms_waves` (`grouping_criteria`), `wms_cycle_count_programs`
(`scope_zone_ids`/`scope_abc_classes`/`scope_item_ids`), `wms_alert_rules` (`trigger_conditions`).
Method: an `awk` pass emitting the enclosing table name for every `JSONB` line → **11 distinct tables**.
- *Live codebase:* CLAUDE.md "**NO JSONB** — standard SQL types only in PostgreSQL", nuanced by R1 `CM-3`
  (the `ArchitectureInvariantsTest.java:225-239` ratchet freezes a baseline rather than banning it, and
  grid-config columns are legitimately jsonb).
- *Sibling:* R2 `T-013` — "No JSONB anywhere in the stock model".
- **Do:** normalise all eleven. `serial_numbers` on `wms_asn_lines` and `inspection_criteria` on
  `wms_quality_inspections` are the two that most obviously want child tables — the first is a list of
  identities that must later be matched against `wms_serial_numbers`, the second is a checklist whose results
  a supplier scorecard will want to aggregate. `scope_*_ids` on the count program is a scoping rule that
  belongs in a `wh_count_program_scopes` child. `'[…]'::jsonb` stays legal **only** in
  `grid_preferences.default_columns`/`default_filters`, which every warehouse grid migration must emit.

### `P-008` · CONTRADICTED · **BLOCKER** · `warehouse-base` · **v1**
**The uniqueness constraint on the central stock table is not valid PostgreSQL.**
`WMS_DATABASE_DESIGN.md:1898`:
```sql
CONSTRAINT uk_wms_soh_item_loc_lot UNIQUE (item_id, location_id, COALESCE(lot_id, '00000000-0000-0000-0000-000000000000')),
```
PostgreSQL table-level `UNIQUE` constraints take a **column list**; an expression requires
`CREATE UNIQUE INDEX … ON wms_inventory (item_id, location_id, COALESCE(lot_id, …))`. It is the only
expression-inside-`UNIQUE` in the file (`grep -nE "UNIQUE \(.*\("` → one hit, line 1898) and it sits on
`wms_inventory` — the table every other module joins to. *(Not executed: Docker-only build. This is a
PostgreSQL grammar rule, not a runtime observation.)*
- **Do:** `CREATE UNIQUE INDEX`. And note the deeper point: the `COALESCE`-to-nil-UUID idiom is being used
  because the grain is nullable, which is exactly the trap R2 `T-003` warns about. Under `T-003` the on-hand
  key is the **full dimension tuple** — item, location, lot, serial, LPN, status **and `owner_id`** (R4
  `F-001`) — and every one of those columns should be `NOT NULL` with a sentinel row, not nullable with a
  `COALESCE`. Use the repo's own precedent for "one active X": partial unique indexes, as in
  `dealer/V20735:43-52` (R1 `C-033`).

### `P-009` · CONTRADICTED · **BLOCKER** · `warehouse-base` · **v1**
**The stock ledger is single-sided and the balance is not reconstructible from it.**
`WMS_DATABASE_DESIGN.md:1930-2005` — `wms_stock_transactions` carries one signed `quantity` together with
**both** `from_location_id` and `to_location_id` and **no** `location_id`. A `TRANSFER_OUT`/`TRANSFER_IN`
pair is described, but a `PUTAWAY` or `CROSS_DOCK` row has both locations and one quantity, so
`SUM(quantity) GROUP BY location` has no defined answer. The table comment says "*immutable transaction log*"
(`:2003`) and the DDL has `created_at` but no `updated_at` — yet there is **no** `REVOKE`, no rule, no
trigger and no `CHECK` preventing `UPDATE` or `DELETE`.
- *Siblings:* R2 `T-001` (double-sided, append-only), `T-017` (UPDATE/DELETE-proof at the database level),
  `T-019` (declare and test reconstructibility), `T-018` (three timestamps); R1 `C-021` (the accessories
  single-sided log is exactly this mistake), `C-038` (`accounting-base/V600111` is the three-layer
  append-only template that already exists in this repo), `C-037` (the deferred constraint trigger that makes
  a movement balance at COMMIT).
- **Do:** two rows per movement, each with a single `location_id` and a signed quantity, sharing a
  `movement_id`; `occurred_at` / `posted_at` / `created_at`; DB-level immutability; a reconstructibility test.
  **The prior art's own later work already moved this way** — the built ledger carries before/after balances
  per row and a single-writer gateway (P-024) — so adopt the built shape, not the designed one.

### `P-010` · CONTRADICTED · **MINOR** · `warehouse-base` · **v1**
**`SccCompany` — the designated owner of the shared company master — was never built.** `SCC_MODULE_ISSUES_ANALYSIS.md`
§4.4: "*no `SccCompany` entity and no `scc_companies` table were ever built. The only artefact is the
unconstrained `scc_company_id UUID` column on `scc_gstin_profiles` (V190045:71) — a pointer with no owning
table in any module (the real company master lives in **automotive** `companies`, which warehouse must not
depend on).*"
- *Live codebase:* R1 `C-035` — no shared supplier/party master exists; `automotive` owns `companies` and
  `customers`; `assets` owns `asset_vendors`.
- **Do:** `warehouse-base` owns `wh_counterparties` + an external-refs table from day one, copying
  `accounting-base/V600001`. A GSTIN profile must FK to a table that exists. **This is the second time this
  exact mistake would be made** — record it as a named trap.

### `P-011` · KEEP · **MINOR** · `all` · **v1**
**The platform-reuse premises still hold — all of them.** Verified individually because the prior art builds
substantial design on each:

| Prior-art premise | Live codebase | Verdict |
|---|---|---|
| Platform 6-stage Import Wizard | `platform/frontend/src/components/common/{ImportButton,ImportModal}.tsx`, `src/hooks/useImport.ts`, `src/types/import.ts` all present | **HOLDS** |
| Admin-configurable row cap `bulk_import_max_rows` | `platform/frontend/src/hooks/useBulkImportMaxRows.ts:5`; `AdminSettingsMiscellaneousTab.tsx:28` | **HOLDS** |
| `xlsx-js-style` for template/XLSX | `platform/frontend/package.json:81` | **HOLDS** |
| Dry-run validate then real import | `useImport.ts:755` (`dryRun: true`) and `:925` (`dryRun: false`) | **HOLDS** — but see P-041 |
| OpenPDF for document generation | `platform/backend/pom.xml:180` | **HOLDS** |
| `ObjectStorageService` → Cloudflare R2 | `platform/.../service/ObjectStorageService.java:57`, `:129`; `AdminSettingsService.java:441` | **HOLDS** |
| Platform `documents` table | `platform/.../V81__Add_document_management_system.sql:39` | **HOLDS** |
| `permission_dependencies` is a platform table | R1 `C-017` (`V248:17-30`) | **HOLDS** — and SCC's defensive re-create is the anti-pattern |
| `global_settings` allows `module='WAREHOUSE'` | R1 `C-015` (`platform/V553:14-15`) | **HOLDS** |
| `branches.branch_type` allows `'WAREHOUSE'`/`'DISTRIBUTION_CENTER'` | R1 `C-016` (`V149:61,63`) | **HOLDS** |

**Do:** carry these forward as *verified* reuse, not as assumptions to re-check. This is the cheapest
inheritance in the corpus.

### `P-012` · OBSOLETE · **MINOR** · `warehouse` · **v1**
**`DocumentAttachmentsPanel` / `wms_document_attachments` are warehouse-base's own, not platform's.**
`WMS_Inbound_Corrections_Build_Contract.md` §E instructs "reuse `wms_document_attachments` (V210055,
polymorphic) + `WmsDocumentAttachmentService/Controller` + `DocumentAttachmentsPanel`".
- *Live codebase:* `grep -rln "DocumentAttachmentsPanel" --include=*.tsx .` → **0 files**.
- **Do:** the *pattern* is right and R1 `C-018` already prescribes it (`wh_document_links` with
  `ON DELETE NO ACTION`, following `acc_document_links` at `V600110` and the warning at `V600111:52-58`).
  Build it; do not expect it. DUPLICATE of `C-018` for the design; recorded here because §E of the inbound
  contract reads as "no new table/endpoint/component" and that budget is wrong by one table and one panel.

### `P-013` · OBSOLETE · **MINOR** · `warehouse` · **v1**
**Three smaller artefacts the prior art expects and this checkout lacks:** the `WMS_DRIVER` platform role
(`grep -rn "WMS_DRIVER"` → 0 files; SCC modelled drivers as platform `users` holding it); the seed migrations
`V950055`/`V950056` that the inbound contract's build order step 7 says to extend (the `V950000+` test band
holds 32 files, all under `dealer/.../db/test/`); and `WMS_PRODUCT_DOCUMENT.md`, cited as a companion by 3
files in the corpus and **absent from it** (`find classic-issues -name WMS_PRODUCT_DOCUMENT.md` → nothing).
**Do:** the new set needs its own seed strategy and its own product document; neither is inheritable. The
missing product document also means the 205 implementation tasks reference requirements that cannot be read.

### `P-014` · KEEP (as a live-code fact) · **MAJOR** · `warehouse-base` + `platform` · **v1**
**The live platform still carries hardcoded warehouse exclusions from the deleted module, and they encode
product decisions that will not carry themselves forward.**
- `platform/.../V528__Create_auditor_role_with_view_permissions.sql:5` — "*Creates a new system role
  'AUDITOR' that has all view permissions from all modules EXCEPT warehouse (`wms_*`, `logistics_*`)*";
  `:37` `AND p.name NOT LIKE 'wms_%'`; `:59` `AND m.name NOT LIKE 'wms_%'`; `:57`
  `AND m.name NOT IN ('warehouse', 'warehouse-setup', 'warehouse-catalog', 'warehouse-config')`; `:67`
  and `:71` extend the exclusion to L3 children and grandchildren.
- `platform/.../V663__Grant_branch_admin_branch_safe_permissions.sql:17-19` — Branch Admin is deliberately
  **not** granted "*pages with NO branch filtering (warehouse `wms_*`, product-lift `pl_*`, assets, `scc_*`,
  oems, ins_360 policies/renewals/tasks, etc.) — granting these would leak all-branch data*".
- `assets/.../V60158__Asset_depreciation_ledger.sql:291` — "*the two-tab precedent set by `wms_inventory` /
  `wms_inventory_by_item`*" — a shipped module citing a warehouse screen that no longer exists.
- **Why it matters.** Both migrations are one-shot `INSERT … SELECT` and have already run. New warehouse
  permissions created by a `V5xxxxx` migration are therefore granted to **neither** AUDITOR **nor** Branch
  Admin, whatever they are named. So the recorded decisions are not enforced — they are simply absent. Given
  the AUDITOR = ADMIN-read-only intent, "warehouse is the one module AUDITOR cannot see" is a real product
  position that the new set must **re-take explicitly**, and if it is reversed, the warehouse migration must
  grant the rows itself. The same applies to Branch Admin and the `view:branch` vs `view:all` split.
- **Do:** one paragraph in the new set's permissions chapter, naming both migrations. And **do not name the
  new permission resources `wms_*`** — `V528`'s pattern would silently exclude them from any future
  AUDITOR-style bulk grant that copies its shape. Use `wh_*`.

### `P-015` · OBSOLETE · **MINOR** · `warehouse` · —
**"The module uses `useAuthGuard` instead of the `usePageAccess` convention" is not a defect.**
`SCC_MODULE_ISSUES_ANALYSIS.md` §5.3 flags this across all 17 pages.
- *Live codebase:* `platform/frontend/src/hooks/useAuthGuard.ts:6` — `import { usePageAccess } from '@/hooks/useMenuAccess';`.
  `useAuthGuard` is a platform hook that **delegates to** `usePageAccess` (defined at
  `platform/frontend/src/hooks/useMenuAccess.ts:152`, not at `hooks/usePageAccess.ts`).
- **Do:** drop the finding. Recorded so it is not re-raised.

### `P-016` · CONTRADICTED · **MINOR** · `warehouse-base` · **v1**
**`widget_definitions.chk_module` does not allow a warehouse value.** The prior art assumes warehouse
dashboards/widgets are available (`wms_kpi_snapshots`, `wms_dashboard_tasks`, the Pillar-4 analytics gap).
- *Live codebase:* `platform/.../V557__Extend_widget_definitions_module_constraint.sql:17-19` —
  `CHECK (module IN ('platform','dealer','shared','accessories','assets','insurance','services'))`.
- **Do:** a widening migration using the **merge** idiom of `accounting-base/V600200:56-99`, before the first
  warehouse widget. **DUPLICATE of R1 `C-014`** — recorded only to attach the prior art's widget ambition to it.

### `P-017` · ADAPT · **MINOR** · `warehouse-base` · **v1**
**`wms_documents` carries its own `file_url` while `wms_item_images` FKs to `platform_document_id`.** Two
document strategies inside one 72-table schema (`WMS_DATABASE_DESIGN.md:4213+` vs `:1173+`). The same split
recurs in SCC (`SCC_MODULE_ISSUES_ANALYSIS.md` T-L7: driver docs store a `document_url VARCHAR(500)` while
vehicle docs FK to platform `documents(id)`).
- **Do:** one strategy — a `wh_document_links` join to the platform `documents` table (R1 `C-018`), with
  `ON DELETE NO ACTION`. A raw URL column on an evidence table means a damage photo can be orphaned by a
  storage migration with no referential trace, which is exactly what an insurance claim needs not to happen.

## 3.2 Architecture and document-model decisions

### `P-018` · KEEP · **MAJOR** · `warehouse` · **v1**
**Each document has exactly one job: PO = supplier→our warehouse · SO = our warehouse→customer ·
TO = our warehouse→our warehouse. No polymorphic source/destination.**
`WAREHOUSE_ARCHITECTURE_REVIEW.md` — the entire document, with six user scenarios each mapped to the correct
document (including drop-ship = an SO+PO pair with **no warehouse floor activity and no GRN**, and
"we arrange pickup" = PO with `pickup_method = WE_PICKUP` plus a consignment). The rejected alternative
("Transfer Order as a God Document") is costed: 17 vs 8 entity modifications, 8 vs 2 NOT NULL drops, 14 vs 4
new polymorphic FKs, 16 vs 8–10 migrations, 10 vs 5 new services, 13 vs 5 updated services, 7 vs 1 CHECK
constraints, 7 vs 4–5 sprints, HIGH vs LOW risk of breaking existing flows.
- **Do:** adopt verbatim into the new FRD's document chapter. It is the only place in the corpus where an
  architectural choice is *quantified* rather than asserted, and it directly answers R2 `T-016`
  (inter-site transfer must be three legs with in-transit ownership) and `T-042` (one demand model for all
  demand types) by giving the document taxonomy those findings assume.
- **One amendment:** the review's own `transfer_type` split (`INTRA_WAREHOUSE` = instant zone-to-zone move;
  `INTER_WAREHOUSE` = pick → ship → GRN → putaway, with `completeTransfer()` rejecting the inter case) is
  correct and must be kept, but R2 `T-016` requires the inter-warehouse leg to post to an **in-transit virtual
  location** (R2 `T-009`) rather than leaving stock nowhere between ship and receipt. The prior art does not
  name that location. Add it.

### `P-019` · KEEP · **MAJOR** · `warehouse` · **v1**
**The layered-truth inbound model, with a worked number.**
`WMS_Inbound_Corrections_Build_Contract.md:13-15`: PO = commitment (`received_qty` is a counter) · ASN =
shipment declaration (shipped qty, lot, expiry, serial) · **Receiving Session = the inbound shipment**
(truck/dock/carrier; N POs × N ASNs × N GRNs) · GRN = the single receipt truth (received/accepted/rejected/
damaged) · Invoice = billed · Inventory = on-hand, written only by the gateway.
*"Number example: Ordered 100 → Shipped 95 → Received 92 → Billed 100 → On-hand 89."*
- **Do:** put that one-line example in the FRD. It settles a dozen arguments before they start, and it is the
  clearest statement anywhere in either corpus of why five different quantities on one PO line are all correct.

### `P-020` · KEEP · **MAJOR** · `warehouse` · **v1**
**The PO is the lifecycle command centre.** `WMS_Inbound_Flow_And_PO_Command_Center_Workflow.md` §1 —
governing principle "*a document should own only the information that legally belongs to it*", then four
owners: Receiving Session owns physical arrival (truck, dock, gate pass, seal, driver, photos, scan logs,
e-way/e-invoice reference); GRN owns the legal receipt (challan, final accepted/rejected/hold quantities, QC
result, putaway link); Invoice owns finance (supplier invoice number, freight, GST, payment status); **PO owns
the lifecycle** and carries the consolidation dashboard where all GRNs, invoices, returns, QC, putaway and
exceptions roll up. The document notes SAP/Oracle/Dynamics converge on this.
- **Do:** adopt. It is the answer to "which screen does the buyer live on", and no sibling report asks that
  question (`grep -ril "command cent" R1..R5` → none). It also implies a concrete screen — a PO detail page
  with sub-tabs — which is a v1 deliverable, not a v2 nicety.

### `P-021` · KEEP · **MAJOR** · `warehouse` · **v1**
**Multi-PO / multi-ASN receiving session — one truck, many suppliers.**
`WMS_Inbound_Corrections_Build_Contract.md` §H: junctions `wms_receiving_session_pos(session_id, po_id,
UNIQUE(session,po))` and `wms_receiving_session_asns(session_id, asn_id, UNIQUE(asn_id))` — an ASN is
assigned once; **relax `receiving_sessions.supplier_id` to NULLABLE** for a multi-supplier truck; demote the
single `purchase_order_id`/`asn_id` to nullable "primary" hints; aggregate expected items across N POs; and
**rework the rollup to iterate GRNs by `receiving_session_id`**, which also fixes the single-PO-keyed
three-way-match rollup. Frontend: an "Inbound Shipment console" with Documents / Progress / Timeline, and a
"Start Inbound" button on the PO page.
- **Do:** adopt. `grep -ril "receiving session" R1..R5` → **none**. This is a genuine gap in the sibling
  coverage and a real operational shape: a consolidator's truck carrying three suppliers' goods against five
  POs is normal in Indian distribution, and a one-PO-per-receipt model forces the operator to lie.

### `P-022` · KEEP · **MAJOR** · `warehouse-base` · **v1**
**A single inventory-writer gateway, enforced by an architecture test.**
`WMS_Inbound_Corrections_Build_Contract.md:13` — "*single-gateway (`InventoryOrchestrationService` is the
only writer)*"; `:76` C10 — "*ArchUnit/reflection test: only `InventoryOrchestrationService` calls
`WmsInventoryRepository.save` / `WmsStockTransactionRepository.save`* — invariant locked for 2 yrs".
- *Live codebase:* the enforcement mechanism exists and is house style — R1 `C-041`, each accounting module
  ships a ~660-line `ArchitectureInvariantsTest` including self-tests that the scanners are not passing
  vacuously.
- **Do:** adopt both halves. The gateway alone is a convention; the test is what makes it survive contact
  with the next feature. Pair with R2 `T-017` (the DB rejects UPDATE/DELETE) so the invariant is defended at
  two layers, and with R1 `C-025` (a ledger port must never return quietly — every refusal is an exception,
  every success returns a movement id).

### `P-023` · KEEP · **MAJOR** · `all` · **v1**
**The 7-layer Definition of Done.** `WMS_Inbound_Corrections_Build_Contract.md` — DB seed/column ✓ · service
method ✓ · endpoint with `@PreAuthorize` ✓ · frontend API ✓ · UI control rendered, `useMemo` permission-gated
and status-gated on a **menu-reachable** page ✓ · **access path clickable from a top menu** ✓ · **runtime
effect observable after rebuild** (a ledger row / a status change / a stat card) ✓.
*"A tick requires ALL 7. No aggregate 'all done.'"*
The same document's six-layer trace table (Menu/Access → UI → FE API → endpoint+permission → service →
DB, each tagged EXISTS/ADD/FIX) is the instrument that produces those ticks.
- **Do:** adopt as the acceptance format for every warehouse issue. It is strictly stronger than
  "backend + frontend + migration + i18n", it is the thing that catches the built-but-unreachable defect
  class, and `WMS_Gap_Closure_Implementation_Plan.md:37` already extends it with "**mobile counterpart where
  user-facing**" — which is CLAUDE.md Principle 3 written as a gate.

### `P-024` · ADAPT · **MAJOR** · `warehouse-base` · **v1**
**The seven quantity buckets and the generated `available`.** `wms_inventory` carries `on_hand`,
`allocated`, `picked`, `packed`, `quality_hold`, `damaged`, `blocked` and a
`GENERATED ALWAYS AS (on_hand − allocated − picked − packed − quality_hold − damaged − blocked) STORED`
column (`WMS_DATABASE_DESIGN.md:1867-1878`). The built version added `@Version` optimistic locking and a
no-oversell CHECK (`WMS_Competitive_Gap_Analysis_And_Roadmap.md` §2 — "*7 quantity buckets … optimistic
version lock prevents oversell*").
- *Tension with siblings.* R2 `T-004` says inventory **status** must be a master table with behaviour flags,
  not an enum and not a bucket; R2 `T-014` says allocation must be an **open-item ledger**, not a
  `quantity_reserved` column. The prior art does both: it has the buckets *and* `wms_stock_allocations` as a
  real open-item table (table 44).
- **Do:** keep `wms_stock_allocations` as the truth and treat the bucket columns as a **derived, indexed
  projection** maintained by the gateway — never as an independently writable number. Keep `@Version`, keep
  the CHECK, keep the generated column, and add the reconciliation test that the projection equals the
  ledger. R1 `C-024` is emphatic that all three of `@Version`, a DB CHECK and a lock ordering discipline are
  needed; the prior art supplies two of the three.

### `P-025` · ADAPT · **MAJOR** · `warehouse-base` · **v1**
**Ownership grain.** `WMS_Inbound_Corrections_Build_Contract.md:109` (§F.4, marked "LOCKED (D1)") — add
**nullable** `owner_id` + `owner_type` (OWN / CONSIGNMENT / CUSTOMER / 3PL, default OWN) to `wms_inventory`,
include `owner_id` in the unique key, key `findOrCreateInventory` on owner, add an `owner_id` filter to
availability queries, and add **no ownership logic beyond the grain**. The rationale given is exactly right:
"*Pre-prod = cheap now; brutal retrofit later.*" The built system shipped it
(`WMS_Competitive_Gap_Analysis_And_Roadmap.md` §2 — "*`owner_id` + `owner_type` part of the inventory unique
key, so consigned/customer stock never merges with own stock*").
- *Sibling:* R4 `F-001` requires `owner_id` **`NOT NULL`** in `warehouse-base` v1, on the balance **and the
  ledger**, arguing the same retrofit impossibility more strongly and adding that historical rows cannot be
  backfilled.
- **Do:** **`F-001` wins on nullability** — `NOT NULL` with a default owner row, not nullable-with-default.
  The prior art wins on scope discipline: the *grain* is base, the ownership *behaviour* (bailment,
  title transfer, per-owner billing) is `warehouse-3pl`. Take the column shape from `F-001` and the
  scope sentence from §F.4. Note the design DDL has neither — `grep -c "owner_id" WMS_DATABASE_DESIGN.md`
  → **0** across 4,655 lines.

### `P-026` · KEEP · **MAJOR** · `warehouse` · **v1**
**Cancellation is a cascade with a stock gate, not a status flip.**
`WMS_Inbound_Corrections_Build_Contract.md` §C4 — a PO is cancellable only **before stock is posted**; refuse
if any GRN line has `stockReceived` **or an ARRIVED ASN exists**; otherwise cascade-cancel the receiving
session and every non-completed GRN. Partial receipt stays OPEN and resolves to FULLY_RECEIVED or a manual
SHORT_CLOSE, with **no auto-backorder**. Over-receipt is governed by `over_receipt_tolerance_pct` on the PO
plus a warehouse-level default, with `match_status` set to MATCHED / QTY_OVER / QTY_UNDER (§C5).
`WMS_Outbound_Flow_Cancellation_Spec.md` (190 lines) is the outbound counterpart, and `WMS_Outbound_Flow_FINAL.md`
R7 item 6 adds that cancelling a consignment must cascade its DRAFT/APPROVED Freight Bill to CANCELLED
"*(today it orphans it — must fix)*".
- *Siblings:* R2 `T-036` (over/short-receipt policy or the PO line never closes), `T-049` (de-allocation on
  cancel must be deterministic and reason-coded), `T-047` (backorder policy per demand type).
- **Do:** adopt. The "refuse if an ARRIVED ASN exists" rule is subtler than anything in the sibling reports
  and is the kind of clause that only comes from having watched a real cancellation go wrong.

### `P-027` · KEEP · **MAJOR** · `warehouse` · **v1**
**Provenance on every ledger row.** `WMS_Inbound_Corrections_Build_Contract.md` §C8 — parameterise
`adjustStock(referenceType, referenceId, reason)` so an opening-stock import writes `OPENING_BALANCE` + the
batch id (today `null`), a cycle count writes `CYCLE_COUNT`, a kit consumption writes `KIT_WORK_ORDER`.
- *Siblings:* R2 `T-010` (reason codes are a master with a GL mapping, seeded in v1), `T-015` (movement type
  is a master because it is the join point for everything), `T-048` (record *why* this stock was chosen).
- **Do:** adopt, and go one step further than the prior art: make `reference_type` and `reason_code` FKs to
  masters rather than the `VARCHAR(30)`/`VARCHAR(50)` the DDL uses (`WMS_DATABASE_DESIGN.md:1961,1971`).
  An unparameterised `null` provenance is how a stock report becomes unauditable, and it is the specific
  failure the prior art caught in its own code.

### `P-028` · KEEP · **MAJOR** · `warehouse` · **v1.1**
**Inbound Reconciliation as a decision centre that never moves stock itself.**
`WMS_Inbound_Corrections_Build_Contract.md` §G — "*Principle (LOCKED): decision centre; **never moves
inventory directly** — creates business documents.*" `wms_reconciliation_cases` carries `case_number`,
`case_type` (QUANTITY / OVER_RECEIPT / INVOICE / ASN / INVENTORY_VARIANCE / RECEIPT_REVERSAL /
SUPPLIER_RETURN), `severity`, `status` (OPEN / IN_REVIEW / RESOLVED / CANCELLED), nullable PO/ASN/session/
GRN/invoice FKs, `root_cause`, and `resolution_document_type` + `resolution_document_id`. Cases are
**auto-created at variance points**. Five resolution actions, each of which creates a document: Accept
Variance → short-close · Receipt Reversal → `wms_receipt_reversal_requests`
(OPEN→APPROVED→EXECUTING→COMPLETED, pre-validating that the stock is still available, not allocated and not
shipped, then reversing storage→QC→GRN) · Supplier Return → `wms_supplier_returns` (DRAFT→APPROVED→PICKING→
STAGED→DISPATCHED, **inventory reduced only at dispatch**) · Invoice Resolution → three-way match ·
Inventory Adjustment → stock adjustment.
- *Siblings:* R2 `T-038` (receipt reversal must be an action, not a data fix), `T-045` (short pick is a
  first-class outcome with an exception code); R4 `F-056` (return to vendor). None of them proposes an
  exception **object** with a resolution-document pointer.
- **Do:** adopt at v1.1 (the prior art's own build order puts it after the core chain, correctly). Two
  details are worth preserving verbatim: **a supplier return is not an RMA** (`wms_supplier_returns` is
  distinct because RMA stays customer-scoped — the built system's bug was a QC-fail auto-RMA stuffing the
  supplier name into `customerName`), and **the resolution pointer**, which is what turns an exception log
  into an auditable trail. `grep -ril "reconciliation case" R1..R5` → **none**.

### `P-029` · KEEP · **MAJOR** · `warehouse` · **v1**
**Quality inspection is a header over lines, not N documents.**
`WMS_Quality_Inspection_Header_Line_Redesign.md` — the existing table is already at GRN-line grain and the
heavy per-line orchestration (QC-hold release, damage routing, auto putaway, auto supplier return, PO
rollup, session recompute) is correct, **so keep it as the LINE table and add a thin header** with
`UNIQUE(grn_id)`, one user-facing `inspection_number` per GRN, rollup `status` and `result`, and counters
(`total_lines`, `completed_lines`, `accepted_lines`, `rejected_lines`, `partial_lines`). Rollup rules are
stated exactly: all PASS → PASS, all FAIL → FAIL, anything mixed or PARTIAL → **CONDITIONAL**; started =
MIN(line.started), completed = MAX(line.completed) when all lines complete. One `POST /headers/{id}/complete-all`
takes per-line results in a single submit; per-line endpoints stay for incremental capture.
- **Do:** adopt. This is the highest ratio of operator-pain-removed to schema-added in the whole corpus — one
  table, one FK, one recompute method — and no sibling report distinguishes header from line for inspection
  (`grep -in "inspection header\|header/line"` across R1–R5 → nothing). Note the document also states
  plainly that **no mobile QC screen exists**, which is the right way to record a parity decision (P-054).

### `P-030` · ADAPT · **MINOR** · `warehouse-base` · **v1**
**The item master is split into six 1:1 side tables** — `wms_item_physical`, `_storage`, `_procurement`,
`_stocking`, `_analysis`, `_service_parts` — hanging off a thin `wms_items`.
- *Assessment.* The split is defensible for `_service_parts` (vertical-specific → adapter) and `_analysis`
  (recomputed by a job, audited by `wms_item_classification_history`). It is questionable for `_physical`
  and `_storage`, which are read on every putaway and every cartonisation decision and will be joined
  100% of the time.
- *Sibling:* R2 `T-027` — reorder point / min / max belong on item **×** site **×** location, **not on the
  item**. `wms_item_stocking` is keyed on `item_id` alone, which is the wrong grain and is exactly the
  mistake `T-027` names. R2 `T-026` similarly says unit cost does not belong on the item master, yet
  `wms_item_procurement` carries `standard_cost`, `last_purchase_price` and `retail_price`.
- **Do:** collapse `_physical` + `_storage` into `wh_items`; re-grain `_stocking` to item × site (v1) and
  item × site × location (v1.1) per `T-027`; move `_procurement`'s prices out of the item per `T-026` and
  keep only the true procurement attributes (`lead_time_days`, `min_order_qty`, `economic_order_qty`);
  move `_service_parts` to the adapter.

### `P-031` · ADAPT · **MAJOR** · `warehouse-base` + adapter · **v1**
**Supersession chains and interchangeability groups.** Three tables — `wms_item_supersessions`
(`predecessor_item_id`, `successor_item_id`, `effective_date`, **`chain_sequence`**),
`wms_interchangeability_groups`, `wms_interchangeability_group_items` (`priority_order`, `effective_from`,
`effective_to`). `chain_sequence` is the detail that matters: it makes a multi-hop chain (A→B→C→D)
traversable and terminable, which a bare predecessor/successor pair does not.
- *Siblings:* R2 `T-021` — "*Supersession chains: absent from every tier-1, mandatory for our vertical*";
  R2 `T-023` — vehicle fitment belongs in the **adapter**, not in `warehouse-base`; R3 §1.2 and §4.1 treat
  catalogue depth as the DMS-parts differentiator; R5 Register A touches interchangeability.
- **Do:** supersession and interchangeability are **item-identity**, not fitment, so they stay in
  `warehouse-base` (a superseded part number is a fact about the SKU, whatever vehicle it fits); **fitment**
  goes to the adapter per `T-023`. Carry `chain_sequence` and the effective-dated group membership verbatim
  — they are the concrete columns `T-021` asks for and the prior art already has them.

### `P-032` · ADAPT · **MINOR** · adapter · **v1.1**
**Core exchange as a first-class object.** `wms_core_exchanges` (table 54) tracks the old unit a customer must
return against a new one: `core_deposit_amount`, `core_return_deadline`, `core_received_date`,
`core_serial_number`, `core_condition_grade`, `credit_issued`/`credit_amount`/`credit_issued_date`, with
`wms_serial_numbers.linked_core_serial_id` closing the loop, `wms_item_service_parts.is_core_exchange` +
`core_deposit_amount` marking eligibility, and `wms_kpi_snapshots.core_return_rate_pct` measuring it.
- *Sibling:* R5 mentions core exchange; R3 §4.5 says "*returns are four different products*". Neither
  supplies the deadline-and-deposit schema.
- **Do:** move to `warehouse-adapter-<automotive>`. It is a dated obligation with money attached — a
  `core_return_deadline` that nothing watches is R2 `C6`-class debt — so it needs a scheduled job and a
  notification, not just a table.

### `P-033` · KEEP · **MAJOR** · `warehouse` · **v1**
**Cycle counting as a policy object, not a task list.** `wms_cycle_count_programs` (table 55) carries
`program_type` (ABC_BASED / RANDOM / FULL / ZONE / ITEM / **DISCREPANCY_TRIGGERED**), `frequency_days`,
`schedule_cron`, `next_scheduled_date`, scoping by zone / ABC class / item, **`is_blind_count`**,
**`recount_threshold_pct`**, **`approval_threshold_pct`**, **`freeze_locations`** and `max_tasks_per_run`;
tasks carry `count_attempt` and `is_frozen`; results carry `is_within_tolerance` and an `adjustment_id`.
- *Live codebase:* R1 `C-023` — accessories' physical count **never posts**; `generateAdjustments()` sets
  `status='POSTED'` and creates nothing. So this is net-new work, and the prior art has already designed it.
- **Do:** adopt whole. `freeze_locations` and `count_attempt`/recount-threshold are the two columns that
  distinguish a real counting program from a spreadsheet, and both are here.

### `P-034` · KEEP · **MAJOR** · `warehouse-base` · **v1**
**The single scannable barcode registry, with quantity derived — never stored.**
`WMS_Inventory_Identity_And_Scanning_Architecture.md` §3 Layer 3, marked LOCKED. One table
(`wms_item_barcodes`) resolves every code — product, supplier, internal, GS1 GTIN, customer, legacy — with
`packaging_id` pointing at the pack configuration it represents, `barcode_type` labelling the code's
*purpose*, `barcode_format` staying the *symbology*, and `status` retiring codes without deleting scan
history. **Quantity is not on the barcode**: a barcode with `packaging_id = null` is one base unit, and one
with `packaging_id` set resolves to that packaging row's `quantity`. The rationale is stated exactly: "*when a
supplier repacks 24 → 36, you edit the packaging row only; every barcode pointing at it instantly resolves to
the new quantity, and no barcode says 24 while packaging says 36.*"
- *The problem it solves is real and was measured:* the built system had a carton barcode in **three** places
  (`wms_item_barcodes.barcode`, `wms_product_packaging.barcode`, `wms_item_variant_uom_conversions.barcode`)
  with pack multipliers that could disagree (§2 GAP #3).
- *Sibling:* R2 `T-022` — "*Multiple barcodes per item, each with its own UoM*". The prior art is **more
  correct** than `T-022`: a barcode should not carry a UoM either, because that is the same dual-truth in a
  different column. Both point at packaging.
- **Do:** adopt as the identity chapter of the new set, and record the amendment to `T-022` explicitly.

### `P-035` · KEEP · **MAJOR** · `warehouse-base` · **v1**
**Supplier-specific packaging.** Same document, §2 GAP #1 and §3 Layer 2: extend the item-packaging
configuration with `container_type_id` (→ the container-type catalogue), **`supplier_id`** (nullable) and
`priority`, and relax uniqueness to `UNIQUE(variant_id, supplier_id, container_type_id)` where a null supplier
is the default. The worked example is the argument: *Maggi from ABC = 24/carton (barcode 111111), 48 (111112),
96 (111113); from XYZ = 20 (222221), 100 (222222); loose EACH = 1 (890102301)*.
Plus the **deterministic packaging resolution order** (§4.2): supplier-specific → supplier-agnostic default
→ loose/EACH, with `priority` breaking ties inside a tier, and a warehouse tier designed but explicitly not
built ("*slots in later as a nullable column without disturbing this order*").
- **Do:** adopt. The pack quantity a supplier ships in is not a property of your SKU, and every warehouse that
  buys the same part from two vendors hits this on day one. The resolution order is what makes it usable
  rather than ambiguous. **Contested detail:** the earlier `WMS_Packaging_Architecture_Design.md` proposes
  seven packaging tables (`_classes`, `_types`, `_levels`, `_rules`, `_templates`, `_assets`,
  `_profiles`); the later plan collapses this to two (`wms_packaging_types` + an extended
  `wms_product_packaging`) and **the later document wins by its own declaration**. Take two, not seven.

### `P-036` · KEEP · **MAJOR** · `warehouse` · **v1**
**The scan engine: one hardware-agnostic resolver, workflow-aware, fully audited.**
`WMS_Scanner_Feature_Design.md` §1 — pipeline `barcode (wedge | camera | manual) → scan capture layer →
scan resolution engine → workflow validation → immutable scan event → business logic`, with the anti-pattern
named and rejected: "*binding workflows to vendor SDKs → every deployment becomes a customization project*".
Concretely: the engine consumes a plain string so **no scanner SDK ever enters the codebase**; scan **modes**
(RECEIVE / PUTAWAY / PICK / PACK / DISPATCH / CYCLE_COUNT) declare the expected entity type so a wrong scan is
rejected with a clear message ("expected LOCATION, got CARTON"); **every** scan, resolved or not, is logged;
certification is on **one** device (Zebra DS2208) via the keyboard-wedge standard, so every wedge scanner
works. The four-step identity-resolution contract (`WMS_Inventory_Identity_And_Scanning_Architecture.md` §4.1)
is named so modules cannot each reinvent it: exact barcode-registry match → PO-line supplier barcode
(receiving context only) → item reference, supplier-scoped then global, returning candidates when ambiguous →
unresolved, logged.
- **Do:** adopt entirely. `grep -ril "keyboard wedge" R1..R5` → **none**; R5 §5.8 raises devices and §5.7
  raises printing, but no sibling states the SDK-independence rule, and it is the decision that determines
  whether the product can be sold to a customer who already owns scanners. **Location barcode first** (the
  design ranks it above carton barcode) is also correct and cheap.
- *Live-codebase note:* the mobile deferral is now cheaper than the prior art assumed — R1 `C-044`,
  `mobile/src/components/common/ListHeader.tsx:210-218` now supports text filters — but a mobile *scanning*
  screen still does not exist, so the deferral itself stands. See P-054.

### `P-037` · KEEP · **MAJOR** · `warehouse` · **v1**
**Pack session: the ten locked decisions.** `WMS_Pack_Session_Frictionless_Carton_Flow_Design.md` §0 and §3.
The decision that cartons stay is argued from six downstream dependencies, each of which is independently
true: you load and scan **cartons**, not 1,000 items; the LR/bilty has a mandatory "No. of packages" field;
the NIC e-way bill requires package count and description; a carton rides exactly one truck in a multi-truck
split; damage and loss claims are per handling unit; 3PL handover manifests are carton-based.
Then D1–D10: loading consumes only SEALED cartons · the container master's `is_default` **is** the global
default (no new settings key) · auto-create the first carton when the session starts · track an
`active_carton_id` on the session · auto-create the next carton on seal, **but only while units remain** ·
a "Change Package" control directly above the scanner · a quantity field on scan · **merge repeat scans into
the existing pack line** instead of creating N qty-1 rows · remove the "— no carton —" option that let items
be packed loose and stranded the session · no new tables and no new menus.
The stated result: "*scan × N, Seal × (#cartons), Complete × 1*".
- **Do:** adopt. `grep -ril "pack session" R1..R5` → **none**. R4 `F-038` covers cartonisation as
  dimensional-weight computation; this is the *operator flow*, which is a different and more immediately
  valuable problem — and the four friction points it diagnoses (F1–F4) are the ones that make a packing
  screen unusable. Also note D2's discipline: an existing master flag beats a new global setting.

### `P-038` · KEEP · **MAJOR** · `warehouse` + `IN` · **v1**
**The frozen outbound chain and the shipment→consignment multi-truck model.**
`WMS_Outbound_Flow_FINAL.md` §0 gives the chain with a parallel inventory track:
SO Draft → SO Approved → Invoice (DRAFT) → **Allocation (Available→Allocated)** → Wave → Pick Task →
Pick Confirm (**Allocated→Picked**) → Pack Session open/pack/seal/complete (**Picked→Packed**), where
completing packing **finalises the invoice and locks quantity** → Shipment READY_FOR_TRANSPORT →
Carrier Assignment ⇒ Freight Bill + Consignment (auto, together) → E-Invoice (IRN) → E-Way Bill (one per
consignment/truck) → Gate Pass → **Dispatch (Packed→Shipped — only here)** → POD → Delivered → carrier
invoice → freight reconciliation → close.
Revision R7 locks eleven UX decisions, of which four are structural: **Add Truck lives on the shipment
only** (a child consignment must not create siblings); the consignment lifecycle is
`DRAFT → CARRIER_ASSIGNED → READY_FOR_LOADING → LOADED → READY_FOR_DISPATCH → DISPATCHED → IN_TRANSIT →
DELIVERED → POD_PENDING → CLOSED` with `POD_PENDING` moved to **after** DELIVERED (deliver physically, then
await signed proof); **loading cartons is required before dispatch**, with a one-click "load all remaining"
so single-truck stays fast; and **gate pass stays EWB-conditional** — it issues freely when no e-way bill is
required and blocks only when one is legally required and not yet generated, because full decoupling would
let EWB-mandatory goods leave without one.
- *Siblings:* R4 §2.4 covers carriers, manifests, NDR, RTO, COD; R5 §2.1 covers the e-way bill. Neither
  models **one shipment → many consignments (trucks)**, and `grep -ril "gate pass\|bilty" R1..R5` → **none**.
- **Do:** adopt the chain and R7. The single most valuable line in it is *"Dispatch is the inventory-relief
  event and it is the only one"* — which is R2 `T-046` (ship confirm must be atomic with the allocation
  close) expressed as a workflow rule the whole team can hold.

### `P-039` · KEEP · **MAJOR** · `warehouse` · **v1.1**
**Three-way match built on an allocation junction, not a 1:1:1 assumption.**
`WMS_Supplier_Invoice_AP_3WayMatch_Change_Plan.md` §1 states the problem with a worked example (one PO, two
GRNs, two invoices, rates differing from the PO and each invoice billing across GRNs) and §4 gives the
answer: add `po_line_id` to the invoice line, and create
```
wms_invoice_grn_allocations (invoice_line_id, grn_line_id, po_line_id, allocated_qty,
                             allocated_amount, UNIQUE(invoice_line_id, grn_line_id))
```
"*This single table delivers: partial invoicing, multiple invoices per PO, one invoice spanning multiple
GRNs, and one GRN line split across invoices — all without data corruption.*" §3 explicitly **rejects** a
parallel `ap_supplier_invoice` domain in favour of reusing the unified invoice tables, on the project's own
"never create a parallel version" rule. The document also names what the built 1:1:1 match got wrong: the
header was one row per PO with a *single* `goods_receipt_id` and a *single* `supplier_invoice_id`, and the
line matcher paired invoice to PO lines by variant **plus closest price** — a heuristic, not a link.
- *Sibling:* R3 `E-028` places three-way match at v1.1 with the value leg in `accounting`. Consistent.
- **Do:** adopt the allocation table verbatim; keep `E-028`'s split of the value leg. The "closest price
  heuristic" is worth recording as a named anti-pattern — it is the kind of shortcut that produces a match
  report nobody can defend in an audit.

### `P-040` · KEEP · **MINOR** · `warehouse` · **v1**
**Invoice ↔ order is a junction, not polymorphic columns.** `WAREHOUSE_ARCHITECTURE_REVIEW.md` Addendum 2 —
replace `WmsInvoice.purchase_order_id` + `order_type` + `order_id` with
`wms_invoice_orders(invoice_id, order_type, order_id, UNIQUE(invoice_id, order_type, order_id))`.
- **Do:** adopt. Same reasoning as `P-018` — a polymorphic pair of columns on a header is a join nobody can
  index and a constraint nobody can write.

### `P-041` · KEEP · **MAJOR** · `warehouse` · **v1**
**Reuse the platform import wizard; keep the job/audit tables in the vertical.**
`WMS_Bulk_Import_Wizard_And_Packaging_Import_Design.md` §0 — reuse `ImportButton` → `ImportModal` →
`useImport` (Download-Template → Upload → Validate dry-run → Preview with per-cell errors → Import →
Result), extend the existing warehouse job table with a new job type, and **explicitly reject** a platform
`bulk_import_jobs` table, a generic platform `ImportJobService` and a platform-wide import-history page:
"*an import job is business infrastructure (it carries `warehouse_id`, SKU, supplier, location) — not
platform infrastructure; forcing a generic platform job table trends toward a God-table.*"
- *Live codebase:* every component named is present (P-011), and the dry-run/real split is real
  (`useImport.ts:755`, `:925`).
- **Two amendments, both from live-codebase facts the prior art could not know.**
  (a) R1 `C-020` — the best backend shape in this checkout is now
  `AccImportHandlerRegistry` (`:36-44`) + `acc_import_batches`/`_rows` + **a reversal path**
  (`AccImportBatchReverseModal.tsx`). An opening-stock import that cannot be reversed is a ledger you cannot
  correct, so the reversal path is not optional for warehouse.
  (b) A known trap in this repo is that a `validateApi` endpoint can *persist* while claiming to be a
  dry-run, producing duplicate rows on the subsequent real import. The frontend passes `dryRun: true`
  faithfully; the obligation is on the backend handler to honour it. Name it in the build spec.
- **Do:** adopt the decision, upgrade the backend shape to `C-020`, and add the reversal path and the
  dry-run obligation.

## 3.3 Module-boundary decisions

### `P-042` · ADAPT · **BLOCKER** · `warehouse-base` · **v1**
**Do not recreate a separate master-owning module.** The prior art's three-module chain
(`supply-chain-core` → `warehouse-core` → `warehouse-base`) split *masters* from *setup* from *operations*,
and every documented cost of that seam is a boundary cost, not a domain cost:
- `SccCompany`, the designated owner of the company master, was **never built** — only an orphan
  `scc_company_id` column with no FK (`SCC_MODULE_ISSUES_ANALYSIS.md` §4.4).
- Warehouse migrations referenced SCC tables that do not exist: `scc_items` (4 refs), `scc_drivers` (1),
  `scc_alert_rules` (1), `scc_alert_history` (1). The §7 remediation log later found two of these were
  false alarms (`scc_items` is a warehouse-base table misleadingly `scc_`-prefixed; `scc_drivers` is a
  permission code, not a table) — **which is itself the finding**: nobody could tell which module owned a
  name.
- `scc*`-named files, classes, components and an i18n namespace sat **inside** `warehouse-core`
  (`WAREHOUSE_CORE_ISSUES.md` WF-3, ~50 `Scc*` interfaces across ~60 files), deferred because renaming
  needed a Docker build to verify.
- The bulk-import feature had its table, entities and **menu** in `warehouse-core` and its controller,
  service and **page** in `warehouse-base`, so core deployed alone renders a menu entry that 404s
  (WF-1). It only worked because the Docker frontend `cp`-merges both trees into one Next.js app.
- `wmsPermissions.ts` in core defined ~70 permission prefixes, most for entities core does not implement
  (WF-5).
- Consumption was lopsided anyway: `scc_units_of_measure` 26 downstream refs, `scc_carriers` 18,
  `scc_suppliers` 13 — and **nothing** downstream consumed the entire `tax_*` set, `sac_master`,
  `scc_document_sequences`, the vehicle sub-logs or the driver sub-tables.
- **Do:** `warehouse-base` owns the masters (UoM, counterparty/supplier, carrier, customer-reference, brand,
  item, location, lot, serial, ledger). `warehouse` owns operations. That is the decided split and the prior
  art is the evidence for it, not against it. Fold §2.9's "shared masters" row into base and delete the
  concept of an upstream core.

### `P-043` · ADAPT · **MAJOR** · `warehouse-india` · **v1.1**
**The relational tax engine is prior art, and it has a known-defect list attached.** Six tables —
`tax_components`, `tax_entity_types`, `tax_rules`, `tax_rule_components`, `tax_rule_conditions`,
`tax_resolution_audit` — plus `scc_hsn_tax_master`, `sac_master`, `scc_gst_state_codes`.
Its own audit found the defects that matter, and they are design defects, not typos:
- **T-H1 (unresolved, deferred to a tax-domain owner):** five seeded intrastate slab rules (0/5/12/18/28%)
  all carry `hsn_id=NULL`, `source=dest=DTA`, `interstate=false`, `priority_order=50` — indistinguishable by
  any matchable column, so a resolver matches all five simultaneously and nothing forces a deterministic
  winner. **Tax resolution can silently pick the wrong slab.**
- **T-H2 (fixed):** no `UNIQUE(tax_rule_id, tax_component_id)` → two CGST rows on one rule → **silent double
  taxation**.
- **T-H3 (deferred):** overlapping effective-date ranges on `scc_hsn_tax_master`, `sac_master` and
  `tax_rules` — "rate for HSN X on date D" can return two rows. Needs `btree_gist` + an `EXCLUDE` constraint.
- **T-M11:** the slab seeds carry `rule_code = NULL`, and NULLs never collide, so `ON CONFLICT DO NOTHING`
  can never fire — re-running duplicates every rule.
- **T-M13:** `version` exists for immutable versioning with no `UNIQUE(rule_code, version)` to enforce it.
- *Sibling:* R5 §2.1 specifies what India requires of stock movement. This is a prior implementation of the
  rate-resolution half.
- **Do:** carry the six-table shape into `warehouse-india`, and carry **T-H1 and T-H3 as v1 blockers**, not
  as deferred items. A tax engine with a nondeterministic resolver is worse than no tax engine, because it
  is confidently wrong. The discriminator model needs designing before the first seed row.

### `P-044` · ADAPT · **MAJOR** · `warehouse-india` · **v1.1**
**The e-invoice / e-way-bill compliance stack, vendor-agnostic by design.** Eighteen tables modelling
providers, per-provider environments, credential *specs*, GSTIN profiles, registrations, encrypted
credentials, auth sessions, compliance documents, a task queue, IRN cancellations, EWB vehicle updates /
cancellations / extensions / consolidation (+items), and a compliance rule engine with conditions.
`WMS_Competitive_Gap_Analysis_And_Roadmap.md` §1 rates this the strongest thing in the built system:
"*Indian GST e-Invoice / e-Way Bill compliance is production-grade with a vendor-agnostic adapter layer.*"
Three of the eighteen were deleted as orphans with no repository or service
(`scc_compliance_api_logs`, `scc_irn_cancellations`, `scc_ewb_extensions`) — i.e. IRN cancellation and EWB
extension were **schema-only stubs**.
- **Two security findings to carry as constraints, not features.** `scc_compliance_api_logs` was *designed*
  to store raw request/response bodies of compliance API calls — including auth calls carrying client
  secrets and NIC passwords — **unencrypted**, undermining an otherwise correctly encrypted credential
  design; and it had no index on `created_at`, so any retention purge is a full scan.
  `ComplianceDemoController` — a test harness that could trigger **real** IRN and EWB filings from a minimal
  demo body with random source-document IDs — shipped in production code.
- **Do:** carry the provider/environment/credential-spec/session shape forward; it is the right abstraction
  and it is rare. Carry the two security findings as explicit non-goals. Build IRN cancellation and EWB
  extension properly or leave the tables out — a schema-only statutory flow is a compliance claim you cannot
  honour.

### `P-045` · ADAPT · **MINOR** · `warehouse-india` · **v1.1**
**Date-typed statutory fields.** `SCC_MODULE_ISSUES_ANALYSIS.md` T-M4 and its §7.2 remediation:
licence/employment/document `issue_date`, `expiry_date`, `joining_date`, `contract_start/end_date` were
`TIMESTAMP WITH TIME ZONE` mapped to `OffsetDateTime`, so "expired today" could shift across a day boundary;
the fix converted them to `DATE`/`LocalDate` with `DateUtils.todayUTC()` and `CURRENT_DATE`.
- *Live codebase:* the same trap is on record here — `LocalDate` must render date-only, and CLAUDE.md's
  "`formatUTCDate(value, true, true)`" guidance is wrong for `LocalDate`; and R1 `C-042` notes `dateOnly`
  is a distinct filter type from `date` in `filterUtils.ts` and matters for `DATE` columns.
- **Do:** every statutory/expiry/manufacture date in the warehouse set is `DATE` + `LocalDate` + a
  `dateOnly` filter. Lot expiry is the one that bites: FEFO allocation and an expiry sweep both branch on it.

### `P-046` · KEEP · **MINOR** · `warehouse-base` · **v1**
**A document-sequence table.** SCC shipped `scc_document_sequences` for gapless document numbering.
- *Live codebase:* R1 `C-019` — there is **no** platform number-series table, and `SequentialCodeGenerator`
  is scan-based and explicitly not gapless; the gapless precedent is `assets/V60014:2-9` +
  `AssetTagSequenceRepository.java:19-27` (a `PESSIMISTIC_WRITE` counter row).
- *Prior-art defect to fix:* T-L10 — `scc_document_sequences` has no `updated_at` even though `next_value`
  mutates on every allocation.
- **Do:** `warehouse-base` owns `wh_number_series` with a locked counter row, per `C-019`. GRN, pick, ship,
  adjustment, QC and gate-pass numbers must be gapless — a missing GRN number is an audit question.

## 3.4 Superseded, duplicated, and out of scope

### `P-047` · ADAPT · **MINOR** · `warehouse-3pl` · **v2**
**`wms_vas_service_types` carries `billing_unit` + `unit_rate` on the catalogue row.** That is a rate card
with one version and no effective date, sitting in the operations module.
- *Sibling:* R4 `F-013` (charge codes are a master with tax and revenue mapping), `F-014` (rate cards are
  versioned and effective-dated; a billing run rates against the version live on the event date), `F-023`
  (VAS priced by labour minute needs a timed task, and cost-to-serve needs it too).
- **Do:** keep `wms_vas_service_types` as the **service catalogue** in `warehouse`, keep
  `wms_vas_work_orders.labor_minutes` (which is exactly the timed task `F-023` needs, and the prior art
  already has it), and move `billing_unit`/`unit_rate` into a versioned rate card in `warehouse-3pl`.

### `P-048` · OBSOLETE · **MINOR** · `all` · —
**`ERP_FEATURE_GAPS.md` is superseded in full.** Its 12 categories are headline-level with no columns, no
schema and no verdicts. R2 (tier-1 WMS), R3 (ERP/mid-market), R4 (fulfilment/3PL) and R5 (standards, statute,
valuation, ops) cover the same ground at column granularity with per-capability v1/v1.1/v2/v3 placements.
R5 §"Fact 4" already reads it and turns its headlines into columns.
- **Do:** cite it once as provenance for the gap list; do not carry any of its rows.
  The one line still worth quoting is its own summary: *"the current system is essentially a solid
  execution-layer WMS"* — which is the honest positioning statement the new set inherits.

### `P-049` · DUPLICATE · **MINOR** · `warehouse` · **v1**
**Blind receipt, cross-dock flags, over/short-receipt tolerance, putaway strategies, allocation strategy,
short pick, receipt reversal, wave, dock appointments, interchangeability, VED/FSN/HML classification.**
Each appears in the prior art *and* in a sibling finding that supersedes it with an explicit version
placement: R2 `T-034` (blind receipt is a first-class v1 flow), `T-039` (cross-dock flag on the receipt line
in v1 even though cross-dock is v2), `T-036` (over/short-receipt policy), `T-037` (putaway rules must be
data, not code), `T-043` (allocation strategy is a configured value, not an if-statement), `T-045` (short
pick), `T-038` (receipt reversal is an action), `T-044` (wave is a real object and its absence must be a
stated deferral); R5 and R4 on dock appointments; R2 `T-021`/R5 on interchangeability; R1/R2/R3/R4/R5 on the
classification axes.
- **Do:** take the sibling's version placement; take the prior art's **column list** where the sibling gives
  a rule without one. The prior art's contribution here is DDL, not judgement.

### `P-050` · DUPLICATE · **MAJOR** · `warehouse` · **v1**
**No inventory valuation engine.** `WMS_Competitive_Gap_Analysis_And_Roadmap.md` §2 ❌ Missing —
"*weighted-average cost is tracked per receipt, but no FIFO/LIFO valuation, no periodic revaluation, no GL
posting, no reserve/variance reporting*". The 72-table design has no cost-layer table
(`grep -ci "cost_layer\|landed_cost\|fifo"` over the DDL → 4 hits, all prose).
- *Siblings:* R5 §4.2 (costing methods and what each forces into the schema), §4.3 (landed cost), §4.4 (NRV
  and write-down), §4.5 (cut-off), §4.8 (exactly what crosses to `accounting-base`); R1 `C-027` (accessories'
  valuation is one moving-average number, and its reversal recomputes the average by subtracting the
  reversed receipt's own cost, while the valuation report uses `last_cost` not `average_cost`); R3 §1.14.
- **Do:** follow R5 §4 and `C-027`. The prior art contributes only the confirmation that a WMS built without
  cost layers reaches production and *then* discovers it cannot answer an as-at-date valuation question.

### `P-051` · DUPLICATE · **MAJOR** · `warehouse` · **v1.1**
**No reorder-point automation and no alerting, despite the columns existing.**
Same source, §2 ❌ Missing — "*fields exist on `WmsItemStocking` (`reorder_point`, `safety_stock`,
`min_stock`, `max_stock`, `low_stock_alert_level`) but **nothing watches them**. No auto-PO, no
replenishment suggestion*"; and "*no notifications of any kind when stock drops or lots near expiry*". Also:
`wms_item_analysis` (ABC/XYZ/VED/FSN/HML) "*is stored but **not consumed** by any logic*", and the expiry
sweep "*flags lot status but does not auto-quarantine to a hold bucket or alert managers; stock stays in
`on_hand` until a manual adjustment*".
- *Siblings:* R2 `T-030` (shelf-life enforcement points must be named, not assumed), §1.15 rows 300–309;
  R3 §1.11 rows 94–99.
- **Do:** this is R2 `C6`-class — a dated obligation nobody executes. The lesson to carry is procedural, not
  functional: **a threshold column with no scheduled job that reads it is a defect at the moment it is
  merged**, and `wms_alert_rules`/`wms_alert_history` (tables 59–60, with `escalation_minutes` and
  `escalation_to_roles`) are the right home for the execution half. The prior art designed the alert engine
  and never wired it; the new set must ship the two together or neither.

### `P-052` · ADAPT · **MAJOR** · planning module (not one of the five) · **v3**
**Service-parts planning is a different product, and `ptc-servigistics.md` is the map of it.**
Sixteen modules: parts master with K-curve/ABC classification and part-equipment (BOM) mapping · demand
forecasting with separate demand streams and pattern-matched methods, consensus overrides and accuracy
measurement · **multi-echelon inventory optimisation (MEO)** with an exchange curve, a stochastic digital
twin, time-phased and multi-period planning · network topology and lateral transfers with bullwhip
mitigation · **asset-availability optimisation (MIME/ASO)** — multi-indenture, multi-echelon, uptime-target
→ stocking plan, **rotable pool optimisation** · **initial provisioning** for a newly launched product with
no demand history · lifecycle management and **last-time-buy** with life-limited parts and engineering-change
management · order planning with ABC-based order frequency, emergency/expedite orders and supplier order
scheduling · **dealer inventory management** with stocking recommendations pushed to dealers · repair &
return · pricing · **performance-based logistics (PBL)** · strategic network optimisation · SIOP · analytics ·
a planner workbench with exception management.
`SPI_PRODUCT_DOCUMENT.md` states the commercial architecture: "*WMS is the execution foundation. SPI is the
intelligence layer built on top. Sell standalone WMS to distributors, or the full SPI Suite to OEMs*", with
a 6-week vs 18-month deployment claim as the wedge. `SPI_FUNCTIONAL_DOCUMENT.md` adds that **SPI always
requires WMS** and reads live inventory from it. The seam is already designed in the schema:
`wms_purchase_orders.spi_recommendation_id`, `wms_sales_orders.spi_order_id`, shared
`wms_item_analysis.abc_class/xyz_class/ved_class`, SPI writing `wms_item_stocking.reorder_point`/
`safety_stock`/`min_stock`/`max_stock`, and SPI reading `wms_inventory` and `wms_stock_transactions`
(`WMS_DATABASE_DESIGN.md:4529-4561`).
- *Siblings:* R2 §1.15 and R3 §1.11 draw the boundary correctly and place forecasting, MEO, seasonality and
  fair-share at **NO / v2 / v3**. This finding does not move that line.
  But `grep -ril "last time buy\|rotable\|installed base\|initial provisioning\|performance-based logistics\|K-curve"`
  across R1–R5 → **zero hits for every one of those six terms**. The siblings drew the boundary; **nobody
  described what is on the far side of it.**
- **Do:** three things. (1) State in the new FRD that a planning product is a **separate module** with its own
  Flyway band, not a phase of `warehouse`. (2) Keep the four seam columns
  (`spi_recommendation_id`, `spi_order_id`, and SPI-writable stocking + classification fields) as **v1
  nullable columns** — they are free now and a retrofit later, exactly the argument the prior art makes for
  `owner_id`. (3) Carry the module list as the v3 roadmap so the boundary is a *decision* with a named other
  side rather than a silence. Last-time-buy in particular is the capability that sells to an OEM and it
  appears nowhere else in either corpus.

### `P-053` · KEEP · **MINOR** · `all` · **v1**
**`WAREHOUSE_EXPLAINED.md` is the onboarding document the new set will otherwise have to write.**
1,719 lines explaining every menu against one running example — "AutoParts Central", storing and shipping
brake pads, oil filters, headlamp assemblies and clutch plates for Honda, Maruti and Tata dealers across
India — in a fixed four-part shape: *what it is · real-world example (what you would actually type) ·
depends on · used by*. The "depends on / used by" pair is a dependency graph in prose, which is exactly what
a new joiner needs and what a schema diagram does not give.
- **Do:** keep as the model for the new set's explanatory document. Re-key the table names; the structure
  and the worked example survive unchanged, and the vertical it assumes (Indian automotive spare parts) is
  the vertical R3 §4 identifies as the differentiator.

### `P-054` · DUPLICATE (parity) · **MAJOR** · `mobile` · **v1.1**
**Zero mobile screens for the whole warehouse module.** `WMS_Competitive_Gap_Analysis_And_Roadmap.md` Pillar 7
scores mobile **●○○○○ Critical**: "*~65 web ops screens, **0** warehouse-base mobile screens; no scanning;
no offline*", and §2 ❌ lists "*no stock lookup, count, or adjustment for warehouse-base on mobile*".
`WMS_Quality_Inspection_Header_Line_Redesign.md` records the same for QC explicitly and correctly:
"*No mobile QC screen exists (`mobile/` has no QualityInspection screen) — state explicitly; no parity
change.*" `WMS_Scanner_Feature_Design.md` §0 defers mobile scanning by an explicit scope decision and argues
it costs nothing architecturally because the engine is mobile-ready.
- *Live codebase:* CLAUDE.md Principle 3 makes web↔mobile mirroring mandatory in the **same task**. R1
  `C-044` — `mobile/src/components/common/ListHeader.tsx:210-218` now supports text filters as well as
  dropdowns, so the mobile constraint is looser than the prior art assumed; **date filters still are not
  supported**.
- **Do:** the prior art's *method* is right and should be adopted as a rule — **a mobile decision is stated
  per screen, with a reason, and silence is a defect**. Its *outcome* (zero screens) is a parity failure the
  new set must not repeat. A warehouse whose floor operations are web-only is, by Pillar 7's own scoring,
  not a warehouse product. Put stock lookup, cycle count and receiving scan on mobile in v1.1 at the latest,
  and record every deliberate omission in the contract.

### `P-055` · KEEP (as a ratchet) · **MAJOR** · `all` · **v1**
**The two module audits are a pre-written defect checklist for the new build.** The *findings* are obsolete
(the modules are gone) but every one names a failure mode that this codebase's conventions permit and that a
new warehouse module will reproduce unless a test forbids it:

| From | Failure mode to ratchet |
|---|---|
| `WAREHOUSE_CORE_ISSUES.md` DB-3 | A grid with `grid_column_definitions` but **no `grid_preferences` row** and no `filter_definitions` → no default column strip, no default filter strip. *(CLAUDE.md's own migration rule; the prior art broke it anyway.)* |
| DB-4 | A grid column and filter bound to a `status` field the table and the response DTO do not have → a blank column and a silently dead filter. |
| DB-5 | A hardcoded `CHECK` **and** a catalogue FK for the same concept → the catalogue becomes a lie the moment it holds a sixth value. |
| DB-6 | Entity `nullable=false` vs a nullable DB column. |
| DB-7 | A grid column with no backing response field → renders blank when a user adds it. |
| DB-8 | `WHERE a LIKE x OR b LIKE y AND NOT EXISTS(...)` — `AND` binds tighter, so the guard covers one branch only. |
| DB-9 | A table named `wms_*` whose `grid_identifier` and permissions drop the prefix, and whose permission rows leave `resource_type` NULL. |
| WF-1 | A feature whose table and **menu** live in one module and whose controller and **page** live in another → a menu that 404s when deployed alone. |
| WF-2 | A frontend union type declaring values the DB `CHECK` rejects and omitting valid ones. |
| `SCC_MODULE_ISSUES_ANALYSIS.md` T-M9 | `DELETE FROM grid_column_definitions/filter_definitions/grid_preferences WHERE grid_identifier=…` in a migration → wipes every user's grid customisation on deploy. |
| T-M11 | `ON CONFLICT DO NOTHING` on a column that is NULL in the seed (NULLs never collide) or on a table with no unique constraint at all → the guard can never fire; bare menu `ON CONFLICT` with no target → duplicate menus on retry. |
| T-M3 / T-M2 | `*_id` columns with no FK and no index; a free-text `preferred_carrier VARCHAR(200)` when the carrier master is in the same module. |
| T-M6 / T-M7 | Inconsistent business-key uniqueness across sibling masters (PAN unique on one, plain index on another; a GSTIN partial-unique missing the `AND gstin != ''` guard); no partial unique enforcing a single default address. |
| T-M12 | Unbounded audit/log tables with no retention, no partitioning and no index on `created_at`. |
| T-L11 | JSON-in-`TEXT` blobs dodging the no-JSONB rule while remaining unqueryable. |
| W-3 | An i18n namespace whose JSON files exist but which is **not registered** → 172 keys silently fall back to English, and hi/fr are fully broken. |
| W-5 | A frontend API service calling a base path the controller does not expose → latent 404s, invisible because nothing calls the method yet. |
| W-6 | Direct `queryClient.invalidateQueries` instead of `useQueryInvalidation` — and the remediation found this was masking a **real** bug: the local key factory roots did not match the list query's `entityName`, so the invalidations refreshed nothing. |
| §4.2 | Fully built backends with **zero UI** (HSN master, tax-rule admin, vehicle trips, UOM conversions) — built, secured, maintained, unreachable. |
| §4.3 | A demo/test controller shipping in production that triggers **real** statutory filings. |

- **Do:** turn this table into the warehouse `ArchitectureInvariantsTest` (R1 `C-041`) and the functional
  contract's screen obligations. Several are already mechanically checkable — grid/preferences pairing,
  namespace registration, FK-less `*_id` columns, `ON CONFLICT` targets, `invalidateQueries` call sites.
  **This is the highest-value thing in the two audit documents**, and it is worth more than any individual
  finding in them.

### `P-056` · KEEP · **MINOR** · `all` · **v1**
**The SCC remediation log's honesty about its own false positives is itself a method to copy.**
`SCC_MODULE_ISSUES_ANALYSIS.md` §7.1 revises **six** of its own findings after closer inspection:
`is_active` + `status` is the platform convention (both canonical references carry it, synced by
`activate()`/`deactivate()`) not a defect · `deleted_at` on suppliers is a real soft-delete used in ~8
repository queries · the driver availability "quadruple" is wired through DTO/mapper/export and not safely
1:1 redundant · "`sac-master` is unreachable" was false for the real deployment because another module
created the menu, and adding one produced a **duplicate** · the "dangling `scc_items`/`scc_drivers`" were a
misleadingly-prefixed local table and a permission code · `scc_uom_conversions` was not dead — an earlier
word-boundary grep had missed the `Repository` suffix.
- **Do:** copy the practice. A review document with a revision log is trustworthy; one without is a list of
  assertions. Two of those six were **grep artefacts**, which is a standing hazard for this kind of work.

### `P-057` · KEEP · **MINOR** · `warehouse` · **v1**
**Per-warehouse receiving configuration instead of two parallel workflows.**
`WMS_Inbound_Flow_And_PO_Command_Center_Workflow.md` §2 — "*A single product must serve a large dock-managed
DC and a tiny direct-receipt store without two confusing parallel paths. Solve it with per-warehouse config,
not two always-visible workflows.*" The config carries the receiving mode, GRN timing (**configurable** —
when the legal receipt is cut relative to the physical count), the QC policy and the putaway automation
level, with defaults chosen to preserve current behaviour. The same document splits **Receiving Verification**
(always) from **Quality Inspection** (optional) — a distinction the 72-table design does not make.
- *Live codebase:* the built system had only **global** `GlobalSettings` and no per-warehouse config, which
  is what forced the finding.
- **Do:** adopt. It is the difference between one product and one product per customer size. Note it also
  resolves a tension the sibling reports leave open: R2 `T-035` (receipt must be able to land in a
  non-available status) and `T-034` (blind receipt is first-class) are both *policies*, and this is where
  they are configured.

### `P-058` · ADAPT · **MINOR** · `warehouse` · **v1.1**
**The KPI snapshot table is a 29-metric daily roll-up.** `wms_kpi_snapshots` (table 61) names the metrics a
warehouse is actually judged on: `dock_to_stock_hours_avg`, `receiving_accuracy_pct`,
`putaway_cycle_time_hours`, `order_fill_rate_pct`, `perfect_order_rate_pct`, `pick_accuracy_pct`,
`inventory_accuracy_pct`, `location_utilization_pct`, `dead_stock_pct`, `shrinkage_value`,
`same_day_ship_rate_pct`, `backorder_rate_pct`, `return_processing_hours`, `return_to_stock_rate_pct`, plus
three service-parts-specific ones — `vor_fill_rate_pct`, `vor_response_time_hours`, `core_return_rate_pct`.
- *Siblings:* R2 §1.19 (analytics, KPI and compliance); R5 §5.4 — "*performance targets, because none are
  stated anywhere*". This is the metric **list** those findings ask for.
- **Do:** keep the metric list; **re-home the mechanism**. A pre-aggregated snapshot table is the wrong first
  move here — R1 `C-043` records that filter-aware statistics must not be given a `statistics.*` cache name,
  and R1 `C-033` shows the repo's own best precedent is a **derived-at-read-time** occupancy model that
  deliberately does not cache. Compute these from the ledger for v1; snapshot only what is provably too slow,
  and only after measuring. The three service-parts metrics move to the adapter with `wms_item_service_parts`.

### `P-059` · ADAPT · **MINOR** · `all` · **v1**
**The 205 implementation tasks are a work-breakdown template, not a plan.**
107 unique IDs in Part 1 (`P0-01`…`P0-07`, `M1-*`, `M2-*`) and 98 in Part 2 (`P1-01`…`P1-08`, `M3-*`…`M15-*`),
each typed (Migration / Backend / Frontend / Config / Constants / i18n / Verification) with dependencies and
a mandatory implementation order. Method: `grep -ohE "^#{2,3} Task [A-Z0-9.-]+" | sort -u | wc -l`.
- *What is void:* the ~15 `P0-*`/`P1-*` bootstrap tasks (package structure, module config, SafeTranslation
  registration, menu migration, CacheConfiguration, permission constants) are superseded by R1 §2's
  **18-row, 16-file** touchpoint list, which is verified against the accounting four-module landing and
  includes the gate the prior art misses entirely — `ModuleImportSelector.java`, where a missing entry means
  the JAR ships and loads nothing.
- *What survives:* the **shape** of a per-entity task set — `DB` (table + grid config + permissions +
  menu) → `BE` (entity, DTOs, 3-file repository, services, `SqlSortBuilder` mappings, controller) →
  `FE` (types, api service, filter config, table, filter, page, modal, view modal, i18n) — which is 20 tasks
  per master entity and is a usable estimating unit.
- **Do:** discard the bootstrap block, replace it with R1 §2, and keep the per-entity task shape as the
  issue template.

### `P-060` · OBSOLETE (out of scope) · **MINOR** · — · —
**The 13-file, 4,247-line `logistics/docs/TMS/` set is transport management, not warehouse.**
Ten competitor briefs (Shipsy, Fleetable, LogiNext, NaaviQ, Delhivery OS, Sagar Informatics, FarEye, Fretron,
SuperProcure, Oracle OTM), a 592-line Rose Rocket functional document, a 2,266-line `TMS_Functional_Document.md`
and a sales feature overview. It is inside the caller's 33,175-line figure (§0.1) but it is a different
product. It matters here only because the built warehouse module's outbound tail — consignment, freight bill,
LR, carrier bill, POD, freight reconciliation (§2.8) — is drawn from it, and because R4 §2.4 already covers
the carrier/label/manifest/tracking/NDR/RTO/COD surface from a fulfilment angle.
- **Do:** exclude from the warehouse set. Record the overlap so the shipment→consignment boundary
  (`P-038`) is drawn deliberately: warehouse owns the handling unit and the dispatch event; a TMS owns the
  trip, the rate and the freight settlement. If `warehouse` grows a freight bill, that is the seam to name.

---

# §4 — The premise ledger

Every assumption the prior art makes about *something outside itself*, with the command that settled it.
`classic` = `/Users/bbhushan/work/git/workspace/classic`, `main`, clean tree. Targets (`*/target/*`) and
`node_modules` excluded from every grep. **HOLDS** = safe to inherit. **FALSE** = must be corrected before
the premise is used. **GONE** = the thing existed in the authoring checkout and does not exist here.

## 4.1 Module and code premises

| # | Premise in the prior art | Command | Result | Verdict | Finding |
|---|---|---|---|---|---|
| 1 | `supply-chain-core` is a live upstream module | `ls supply-chain-core` | `No such file or directory` | **GONE** | P-003 |
| 2 | `warehouse-core` is a live module (V200001–V200042, 15 entities, 11 pages) | `ls warehouse-core` | `No such file or directory` | **GONE** | P-004 |
| 3 | `warehouse-base` is a live module (~65 screens, V210000–V210131) | `ls warehouse-base` / `ls warehouse` | `No such file or directory` (both) | **GONE** | P-005 |
| 4 | 46 `scc_*` tables exist and are FK targets | `grep -rln "scc_units_of_measure\|scc_suppliers\|scc_carriers\|scc_customers\|scc_hsn_tax_master\|sac_master\|tax_rules" --include=*.sql --include=*.java .` | **0 files** | **FALSE** | P-003 |
| 5 | `wms_*` tables exist | `grep -rl "wms_" --include=*.sql --include=*.java .` | 3 files, **all comments** — `platform/V528:37,59,67`, `platform/V663:17`, `assets/V60158:291`. No DDL. | **FALSE** | P-005, P-014 |
| 6 | `SccCompany` / `scc_companies` owns the shared company master | (per prior art's own §4.4) + R1 `C-035` | never built; company master is `automotive` | **FALSE** | P-010 |
| 7 | 11 `statistics.wms_*` cache names are registered in platform `CacheConfiguration.java` | R1 `C-042` — 202 names registered | none is `wms_*` | **GONE** | P-004 |
| 8 | `WMS_DRIVER` platform role exists | `grep -rn "WMS_DRIVER" --include=*.sql --include=*.java .` | **0 files** | **GONE** | P-013 |
| 9 | `DocumentAttachmentsPanel` is available to reuse | `grep -rln "DocumentAttachmentsPanel" --include=*.tsx .` | **0 files** | **GONE** | P-012 |
| 10 | `V950055` / `V950056` warehouse seed migrations exist to extend | `find . -name "V9500*__*.sql" -not -path "*/target/*"` | 32 files, all under `dealer/.../db/test/` | **GONE** | P-013 |
| 11 | `WMS_PRODUCT_DOCUMENT.md` is a companion of the task docs | `find classic-issues -name WMS_PRODUCT_DOCUMENT.md` | not in the corpus; cited by 3 files | **FALSE** | P-013 |
| 12 | `useAuthGuard` is a module-local divergence from `usePageAccess` | `platform/frontend/src/hooks/useAuthGuard.ts:6` | it is a **platform** hook importing `usePageAccess` from `useMenuAccess.ts:152` | **FALSE (non-defect)** | P-015 |

## 4.2 Convention and constraint premises

| # | Premise | Command | Result | Verdict | Finding |
|---|---|---|---|---|---|
| 13 | "CLAUDE.md says warehouse modules are pre-production; edit migrations in place" (14 docs) | `grep -c -i "pre-produc" CLAUDE.md` | **0** | **FALSE — BLOCKER** | P-001 |
| 14 | …and the house style permits it | `acc_companies` `V600001`→altered `V600142`; `acc_audit_events` `V600111`→`V600121`; `dococr_jobs` `V700000`→`V700003`,`V700006`; `dococr_field_definitions`→`V700012`,`V700013` | forward-only ALTER is the house style | **FALSE** | P-001 |
| 15 | `grid_filter_definitions` is the filter table (14 uses across 6 docs) | `grep -rl "grid_filter_definitions" --include=*.sql --include=*.java .` | **0 files**; the table is `filter_definitions` | **FALSE** | P-006 |
| 16 | JSONB is an acceptable column type for business tables | CLAUDE.md "NO JSONB"; R1 `CM-3`; R2 `T-013`. Prior art uses it on **11 of 72** tables | permitted only for grid-config columns | **FALSE** | P-007 |
| 17 | `UNIQUE (item_id, location_id, COALESCE(lot_id, …))` is a valid table constraint | PostgreSQL grammar — `UNIQUE` takes a column list; an expression needs `CREATE UNIQUE INDEX`. `grep -nE "UNIQUE \(.*\("` → 1 hit, `:1898` | will not run | **FALSE — BLOCKER** *(not executed; Docker-only)* | P-008 |
| 18 | A single-sided movement row reconstructs a per-location balance | `wms_stock_transactions:1930-2005` has `from_location_id` + `to_location_id` and no `location_id` | it cannot | **FALSE — BLOCKER** | P-009 |
| 19 | Migration bands V190xxx / V200xxx / V210xxx are ours | `find . -name "V19[0-9][0-9][0-9][0-9]__*.sql"` etc. → 0 each; decided band is V500000–V549999 (R1 `C-003`) | free but wrong | **FALSE** | P-002 |
| 20 | `widget_definitions.chk_module` admits a warehouse value | `platform/V557:17-19` | `('platform','dealer','shared','accessories','assets','insurance','services')` | **FALSE** | P-016 |
| 21 | `permission_dependencies` may be `CREATE TABLE IF NOT EXISTS`-d by a module | R1 `C-017` — platform table, `V248:17-30` | insert rows only | **FALSE** | P-003 |
| 22 | `global_settings` accepts `module='WAREHOUSE'` | R1 `C-015` — `platform/V553:14-15` | yes | **HOLDS** | P-011 |
| 23 | `branches` accepts `branch_type='WAREHOUSE'` / `'DISTRIBUTION_CENTER'` | R1 `C-016` — `V149:61,63` | yes | **HOLDS** | P-011 |

## 4.3 Reusable-platform premises — all confirmed

| # | Premise | Evidence in `classic` | Verdict |
|---|---|---|---|
| 24 | 6-stage Import Wizard exists and is generic | `platform/frontend/src/components/common/ImportButton.tsx`, `ImportModal.tsx`, `src/hooks/useImport.ts`, `src/types/import.ts` | **HOLDS** |
| 25 | Validate is a dry-run, import is not | `useImport.ts:755` `dryRun: true` · `:925` `dryRun: false` | **HOLDS** — with the backend obligation noted in P-041 |
| 26 | Import row cap is an admin setting | `useBulkImportMaxRows.ts:5`; `AdminSettingsMiscellaneousTab.tsx:28` | **HOLDS** |
| 27 | XLSX generation is available client-side | `platform/frontend/package.json:81` — `xlsx-js-style` | **HOLDS** |
| 28 | PDF generation is available | `platform/backend/pom.xml:180` — `openpdf` | **HOLDS** |
| 29 | Object storage → Cloudflare R2 | `ObjectStorageService.java:57`, `:129`; `AdminSettingsService.java:441` | **HOLDS** |
| 30 | A platform `documents` table exists | `platform/V81__Add_document_management_system.sql:39` | **HOLDS** |

## 4.4 The three live-code artefacts the prior module left behind

Not premises — facts about `classic` that only surfaced because the prior art was read.

| Artefact | Evidence | Consequence |
|---|---|---|
| AUDITOR role excludes warehouse | `platform/V528:5,37,57,59,67,71` — `NOT LIKE 'wms_%'`, `NOT LIKE 'logistics_%'`, menu names `warehouse`/`warehouse-setup`/`warehouse-catalog`/`warehouse-config` + their L3 children and grandchildren | already ran; grants nothing to a new module. The product decision must be **re-taken**, and new permissions must not be named `wms_*` (P-014) |
| Branch Admin excludes warehouse | `platform/V663:17-19` — warehouse `wms_*`, product-lift `pl_*`, assets, `scc_*` … "*granting these would leak all-branch data*"; `:28-33` — Branch Admin must never hold `{resource}:view:all`, only `:view:branch` | the `view:all` / `view:branch` three-mode pattern is the one warehouse controllers must implement (P-014) |
| A live module cites a dead warehouse screen | `assets/V60158__Asset_depreciation_ledger.sql:291` — "*the two-tab precedent set by `wms_inventory` / `wms_inventory_by_item`*" | the by-location / by-item two-tab inventory screen is an established house pattern with a live citation, and it is **not** in the 72-table design (`wms_inventory_by_item` has no DDL anywhere). Build both tabs (P-014) |

---

# §5 — What the prior art has that the five sibling lenses missed

Method: every concept below was grepped case-insensitively across all five sibling reports
(`grep -ril "<term>" R1*.md R2*.md R3*.md R4*.md R5*.md`). A term is listed here only if the result was
**zero files**, or if the siblings named the capability without supplying the mechanism. This is the section
that justifies reading 28,928 lines of prior art rather than starting clean.

## 5.1 Zero-hit concepts — no sibling mentions them at all

| Concept | Grep result across R1–R5 | Prior-art source | Finding |
|---|---|---|---|
| **pack session** | 0 files | `WMS_Pack_Session_Frictionless_Carton_Flow_Design.md` | P-037 |
| **receiving session** | 0 files | `WMS_Inbound_Corrections_Build_Contract.md` §H | P-021 |
| **command cent**re | 0 files | `WMS_Inbound_Flow_And_PO_Command_Center_Workflow.md` | P-020 |
| **gate pass** | 0 files | `WMS_Outbound_Flow_FINAL.md` R7-7; inbound contract §I.3 | P-038 |
| **bilty** (LR / consignment note) | 0 files | `WMS_Pack_Session…` §0; `WMS_Outbound_Flow_FINAL.md` | P-038 |
| **reconciliation case** | 0 files | `WMS_Inbound_Corrections_Build_Contract.md` §G | P-028 |
| **keyboard wedge** | 0 files | `WMS_Scanner_Feature_Design.md` §0 ✔2, §8 | P-036 |
| **cartoniz**ation *(siblings use "cartonis-" only, and only for dim-weight)* | 0 files | `WMS_Pack_Session…` D1–D10 | P-037 |
| **inspection header / header-line** | 0 files | `WMS_Quality_Inspection_Header_Line_Redesign.md` | P-029 |
| **last time buy** | 0 files | `ptc-servigistics.md` §10.2 | P-052 |
| **rotable** (pool) | 0 files | `ptc-servigistics.md` §8.4 | P-052 |
| **installed base** | 0 files | `ptc-servigistics.md` §7.3 | P-052 |
| **initial provisioning** | 0 files | `ptc-servigistics.md` §9 | P-052 |
| **performance-based logistics** | 0 files | `ptc-servigistics.md` §15 | P-052 |
| **K-curve** | 0 files | `ptc-servigistics.md` §4 | P-052 |

## 5.2 The seven capabilities in detail

### 5.2.1 Inbound corrections and the six-layer trace
`WMS_Inbound_Corrections_Build_Contract.md` is 182 lines that do something no sibling report does: it takes
every gap and walks it through **Menu/Access → UI → Frontend API → Backend endpoint (+ permission) →
Backend service → DB/migration**, tagging each layer EXISTS / ADD / FIX, and then refuses to call anything
done until all **seven** layers of its Definition of Done tick — the seventh being *"runtime effect
observable after rebuild"*. The sibling reports are capability audits; this is a completeness instrument.
Its concrete contributions:
- The **layered-truth model with a number** (P-019) — five different quantities on one PO line, all correct.
- **Multi-PO / multi-ASN receiving** (P-021) — a truck is not a purchase order.
- **Cancel-cascade with an ARRIVED-ASN gate** (P-026).
- **Ledger provenance parameterisation** (P-027) — the specific `null` that made an opening-stock import
  untraceable.
- **The reconciliation decision centre** (P-028) — an exception object with a resolution-document pointer,
  which never moves stock itself.
- **UOM convertibility on the receiving path** (§F.2 F1, rated HIGH): PO and SO had a convertibility guard;
  the GRN modal used the full UoM master list, so a receipt could post the wrong base quantity. That is a
  silent data-corruption path that no sibling names.
- **Tracking decided by a string while booleans are ignored** (§F.2 F2, HIGH): `tracking_mode` was read but
  `is_lot_tracked` / `is_serial_tracked` were not, so an item could be silently received untracked.

### 5.2.2 The PO command centre and per-warehouse receiving config
Two decisions no sibling makes (P-020, P-057): *which document owns the lifecycle view* (the PO, following
SAP/Oracle/Dynamics), and *how one product serves a dock-managed DC and a two-person store without two
workflows* (a per-warehouse receiving config with defaults that preserve current behaviour). It also splits
**Receiving Verification** (always) from **Quality Inspection** (optional), and makes **GRN timing**
configurable — when the legal receipt is cut relative to the physical count. R2 `T-035` says a receipt must
be able to land in a non-available status; this is the configuration surface that decision needs.

### 5.2.3 Pack sessions and the carton argument
P-037. The six reasons cartons cannot be optional — truck loading and scanning, the mandatory package count
on an LR/bilty, the NIC e-way-bill package count, one-carton-one-truck in a split dispatch, per-handling-unit
damage claims, and 3PL handover manifests — are each independently true and together they close the question.
Then ten locked decisions reduce a session to *scan × N, seal × cartons, complete × 1*. R4 `F-038` treats
cartonisation as dimensional-weight arithmetic. This is the operator's screen, and it is the one that decides
whether the warehouse can actually ship.

### 5.2.4 Scanner and identity architecture
P-034, P-036. Three things no sibling states: **no scanner SDK may enter the codebase** (the engine consumes
a plain string, so any keyboard-wedge device works and no deployment becomes a customisation project);
**a scan is validated against what the current workflow step expects**, so a carton scanned where a location
is due is rejected with a clear message rather than silently mis-posted; and **quantity is derived from
packaging, never stored on the barcode**, which is the fix for a measured three-places-one-truth problem.
Add the named four-step identity-resolution contract and the deterministic packaging-resolution order, and
this is a complete identity chapter that R2 `T-022` and R5 §1.1/§1.3 gesture at but do not write.

### 5.2.5 Quality inspection header/line
P-029. One table, one FK, one recompute method, and a GRN with fourteen lines stops producing fourteen QC
documents. The rollup rules are specified to the value (`CONDITIONAL` for any mixed outcome) and the
downstream contract is explicitly unchanged, which is why it is safe. No sibling distinguishes the grain.

### 5.2.6 Three-way match as an allocation problem
P-039. R3 `E-028` places three-way match at v1.1 and splits the value leg to `accounting`. The prior art
supplies the structure that makes it possible at all: `wms_invoice_grn_allocations`, plus `po_line_id` on the
invoice line. It also documents the failure it replaced — a 1:1:1 match header carrying a *single*
`goods_receipt_id` and a *single* `supplier_invoice_id`, with lines paired by variant plus **closest price**.
That heuristic is worth carrying forward as a named anti-pattern.

### 5.2.7 Service-parts planning — the far side of the boundary
P-052. R2 §1.15 and R3 §1.11 draw the planning boundary correctly and place forecasting, MEO and
seasonality at NO/v2/v3. But six planning concepts return **zero hits** across all five sibling reports, and
they are precisely the capabilities that sell a service-parts product to an OEM rather than a distributor:
**initial provisioning** (stocking a part with no demand history because a new product just launched),
**last-time-buy** (the one-shot purchase decision when a supplier discontinues a part still under warranty
obligation), **rotable pool optimisation** (units that cycle through repair rather than being consumed),
**multi-indenture/multi-echelon** optimisation, **installed-base visibility**, and **performance-based
logistics** (contracting on uptime, not on parts sold). The prior art also already designed the seam — four
nullable columns and two shared classification fields — which costs nothing now and is a rebuild later.

## 5.3 Two things the prior art contributes that are not capabilities

- **A defect ratchet, pre-written** (P-055): nineteen named failure modes with the mechanism of each, drawn
  from auditing two real modules built against these exact conventions. Several are mechanically checkable
  and belong in the warehouse `ArchitectureInvariantsTest` on day one.
- **A worked onboarding narrative** (P-053): 1,719 lines explaining every screen against one Indian
  automotive-parts warehouse, with a *depends on / used by* pair per menu that is a dependency graph in prose.

---

# §6 — Reusability verdict

## 6.1 Files — how I counted

`wc -l` on every `.md` under the three warehouse directories (37 files, 28,928 lines), then each file
assigned exactly one disposition by reading it or, for the six long documents I sampled rather than read
end-to-end, by reading their headings, executive summary, decision tables and every section a finding cites.

**Sampling disclosure.** Read in full: `WAREHOUSE_ARCHITECTURE_REVIEW.md`, `ERP_FEATURE_GAPS.md`,
`WAREHOUSE_CORE_ISSUES.md`, `SCC_MODULE_ISSUES_ANALYSIS.md`, `WMS_Inbound_Corrections_Build_Contract.md`,
`WMS_Quality_Inspection_Header_Line_Redesign.md`, `WMS_Pack_Session_Frictionless_Carton_Flow_Design.md`,
`WMS_Inventory_Identity_And_Scanning_Architecture.md`.
Read in substantial part (headings + summary + decision tables + all cited sections):
`WMS_DATABASE_DESIGN.md` (the 72 DDL blocks were machine-extracted in full; the prose, ER diagrams,
permissions matrix and SPI integration section were read at heading level plus `:126-130`, `:1845-2010`,
`:4529-4561`), `WMS_Supplier_Invoice_AP_3WayMatch_Change_Plan.md` (§1–§4),
`WMS_Inbound_Flow_And_PO_Command_Center_Workflow.md` (§0–§2), `WMS_Scanner_Feature_Design.md` (§0–§2),
`WMS_Bulk_Import_Wizard_And_Packaging_Import_Design.md` (§0–§1),
`WMS_Outbound_Flow_FINAL.md` (R7 + §0), `WMS_Competitive_Gap_Analysis_And_Roadmap.md` (§0–§2),
`ptc-servigistics.md` (TOC + §1 + all 26 section headings), `spi/*` (headers + companion tables + heading trees),
`WMS_IMPLEMENTATION_TASKS*.md` (headings, dependency graphs, the complete task index; task IDs
machine-counted). **Read at heading level only:** the remaining 13 `WMS/` outbound and GRN documents
(`WMS_Outbound_Flow_{Implementation_Task,Master_Workflow_Matrix,UI_Screens,Gap_Review,Cancellation_Spec,
Traceability_Audit,Accounts_And_WorkQueues}.md`, `WMS_Goods_Receipt_{Add_Redesign_And_Consolidation_Plan,
View_Popup_Functional_Spec}.md`, `WMS_Gap_Closure_Implementation_Plan.md`,
`WMS_PO_To_Inventory_And_Scanning_Flow.md`, `WMS_Packaging_{Architecture_Design,Implementation_And_Validation_Plan,
Implementation_Task}.md`) plus targeted greps into each. Their dispositions below are correspondingly
lower-confidence and are marked `†`.

| Disposition | Files | Lines | Which |
|---|---|---|---|
| **Directly reusable as source material** | **9** | 9,214 | `WMS_DATABASE_DESIGN.md`, `WAREHOUSE_ARCHITECTURE_REVIEW.md`, `WMS_Inbound_Corrections_Build_Contract.md`, `WMS_Inventory_Identity_And_Scanning_Architecture.md`, `WMS_Pack_Session_Frictionless_Carton_Flow_Design.md`, `WMS_Quality_Inspection_Header_Line_Redesign.md`, `WMS_Supplier_Invoice_AP_3WayMatch_Change_Plan.md`, `WMS_Scanner_Feature_Design.md`, `WAREHOUSE_EXPLAINED.md` |
| **Reusable once the "as-built" framing is stripped** | **19** | 13,455 | `WMS_Inbound_Flow_And_PO_Command_Center_Workflow.md`, `WMS_Outbound_Flow_FINAL.md`, `WAREHOUSE_END_TO_END_FLOWS.md`, `WMS_Bulk_Import_Wizard_And_Packaging_Import_Design.md`, `WMS_Competitive_Gap_Analysis_And_Roadmap.md`, both `WMS_IMPLEMENTATION_TASKS*.md`, the 3 packaging documents†, `WMS_Gap_Closure_Implementation_Plan.md`†, `WMS_PO_To_Inventory_And_Scanning_Flow.md`†, and the 7 outbound/GRN documents† |
| **Obsolete** | **5** | 3,342 | `ERP_FEATURE_GAPS.md` (P-048), `WAREHOUSE_CORE_ISSUES.md` and `SCC_MODULE_ISSUES_ANALYSIS.md` **as findings** (their ratchets survive as P-055/P-056), `SPI_PRODUCT_DOCUMENT.md` and `SPI_FUNCTIONAL_DOCUMENT.md` **as plans** (their module map survives as P-052) |
| **Superseded by a sibling report** | **4** | 2,917 | `ptc-servigistics.md` at capability level (R2 §1.15, R3 §1.11 — but see P-052 for the six zero-hit concepts), plus the three outbound-review documents whose findings R4 §2.4 and R5 §2.1 restate at column granularity† |

Reading the two rightmost dispositions as "carry forward in some form": **28 of 37 files, 22,669 of 28,928
lines — 78% by line count.** The 22% that is genuinely dead is concentrated in the two module audits' finding
bodies and the ERP gap list.

## 6.2 Tables

| Disposition | Count | Notes |
|---|---|---|
| **Tables with real DDL in the corpus** | **80** | 72 in `WMS_DATABASE_DESIGN.md` + 8 elsewhere (§2.7a) |
| **Map cleanly onto the new five-module split** | **68** | §2.2–§2.7a; assignments given per table |
| **Dropped by the prior art's own review** | **4** | `wms_warehouse_locations`, `wms_location_zones` (dead junctions, `WAREHOUSE_CORE_ISSUES.md` DB-2), `wms_distance_cache` (no callers), `wms_product_packaging_profiles` (superseded) |
| **Contested — the later document wins** | **8** | the 6 surplus packaging tables (P-035), `wms_item_stocking` at the wrong grain (P-030), `wms_documents` with its own `file_url` (P-017) |
| **Require a structural rewrite before use** | **2** | `wms_inventory` (P-008 invalid constraint, P-024 buckets, P-025 owner grain), `wms_stock_transactions` (P-009 single-sided, no immutability guard) |
| **Named but never defined (the built system's vocabulary)** | **~58** | §2.8 — a naming checklist and a set of questions, **not** a schema |
| **`supply-chain-core` tables carried into `warehouse-india` / `warehouse-base`** | **29 of 46** | 3 GST reference + 6 tax engine + 18 compliance (3 of which were orphan stubs) → `warehouse-india`; 8 shared masters → `warehouse-base`. **17 excluded**: 10 fleet/driver (TMS, P-060), `permission_dependencies` (platform, P-003), and the 6 vehicle sub-log tables |

**Net: 68 + 29 = 97 tables of prior-art schema map onto the new set**, against 80 + 46 = 126 defined in the
corpus. The 29 that do not are either TMS, platform, or dropped by their own authors.

## 6.3 Requirements

| Unit | Count | Method | Disposition |
|---|---|---|---|
| Implementation task IDs | **205** | `grep -ohE "^#{2,3} Task [A-Z0-9.-]+" WMS_IMPLEMENTATION_TASKS.md WMS_IMPLEMENTATION_TASKS_PART2.md \| sed 's/^#* Task //' \| sort -u \| wc -l` → 205 (107 + 98) | ~15 bootstrap tasks **void** (replaced by R1 §2's 18-row touchpoint list); ~190 survive as a per-entity task template (P-059) |
| Locked architecture decisions | **~34** | counted from the decision tables that state them: `WAREHOUSE_ARCHITECTURE_REVIEW.md` "STATUS: READY" table (12) + Addendum 2 (2), `WMS_Pack_Session…` D1–D10 (10), `WMS_Outbound_Flow_FINAL.md` R7 (11 — 1 overlapping) | **KEEP or ADAPT, all of them.** These are the corpus's highest-value output |
| Signed-off 3-way-match decisions | **8** | `WMS_Supplier_Invoice_AP_3WayMatch_Change_Plan.md` D1–D8 | KEEP (P-039) |
| Inbound corrections | **~40** | §A (6) + §B (4) + §C (10) + §F (5) + §G (5 actions) + §I (3) + §K (3) + §L items 1–8 (8) | KEEP / ADAPT (P-019…P-029) |
| Module-audit findings | **13 + ~50** | `WAREHOUSE_CORE_ISSUES.md` DB-1…DB-9 + WF-1…WF-5; `SCC_MODULE_ISSUES_ANALYSIS.md` T-H1–4, T-M1–16, T-L1–17, W-1–7 | findings **OBSOLETE**; **19 distilled into the P-055 ratchet**; 5 tax/compliance defects carried as v1 blockers (P-043, P-044) |
| Competitor capability rows | ~200 | `ptc-servigistics.md` 16 modules | **superseded** by R2/R3 at capability level; **6 concepts survive** as the v3 planning roadmap (P-052) |

## 6.4 The five most valuable artefacts to carry forward

1. **`WMS_DATABASE_DESIGN.md` — the 72-table DDL.** Nothing else in either corpus gives 4,655 lines of
   columns, types, CHECK vocabularies, FKs, indexes and table comments for a complete WMS. §2 has already
   re-homed all 72 onto the new five-module split; the work remaining is to fix `:1898`, normalise the 11
   JSONB tables, re-shape the two ledger tables, add `owner_id`, and re-band every version. **That is
   perhaps two days of correction against several weeks of authoring.** Use it as the skeleton for the new
   schema chapter, not as a copy source.

2. **`WMS_Inbound_Corrections_Build_Contract.md` — the method as much as the content.** The six-layer
   EXISTS/ADD/FIX trace and the 7-layer Definition of Done are a completeness instrument that catches the
   built-but-unreachable defect class, which is the one this repo keeps producing. Adopt the format for
   every warehouse issue. Its substantive contributions — layered truth with a worked number, multi-PO
   receiving sessions, the reconciliation decision centre, cancel-cascade with a stock gate, ledger
   provenance — are each independently worth a finding.

3. **`WAREHOUSE_ARCHITECTURE_REVIEW.md` — the document-responsibility model, with the alternative costed.**
   PO / SO / TO each with exactly one job, drop-ship as an SO+PO pair, no polymorphic transfer order, and a
   before/after table quantifying what the rejected design would have cost (17→8 entity changes, 8→2 NOT
   NULL drops, 7→5 sprints). It is the only place in either corpus where an architectural decision is
   argued numerically, and it settles the question every warehouse design eventually gets wrong.

4. **`WMS_Inventory_Identity_And_Scanning_Architecture.md` + `WMS_Scanner_Feature_Design.md` — identity and
   capture as one chapter.** One scannable barcode registry with quantity derived from packaging and never
   stored; supplier-specific packaging with a deterministic resolution order; a named four-step
   identity-resolution contract; and a hardware-agnostic, workflow-aware, fully audited scan engine with a
   single certified device and no vendor SDK anywhere. Together these are more precise than R2 `T-022` and
   R5 §1, and they are the difference between a product a customer can deploy on their existing scanners and
   one that needs an integration project per site.

5. **The `supply-chain-core` India stack — 29 tables with a defect list attached (P-043, P-044).** A
   relational tax engine (components, entity types, rules, rule components, rule conditions, resolution
   audit) over HSN/SAC/state-code masters, plus an 18-table vendor-agnostic e-invoice/e-way-bill compliance
   layer with provider environments, credential specs, encrypted credentials and auth sessions. R5 §2
   specified what India demands; this is a prior implementation of the hardest half of it, already reviewed,
   with its own blockers named — nondeterministic slab resolution, overlapping effective-date ranges,
   never-firing `ON CONFLICT` seed guards, plaintext secrets in an API log, and a demo controller that could
   fire real statutory filings. Carrying the shape **and** the defect list into `warehouse-india` is the
   single largest head start available to the new set.

**Runner-up, and the one to read first if only one is read:**
`WMS_Competitive_Gap_Analysis_And_Roadmap.md`. It is the only honest as-built assessment in the corpus — an
8-pillar scorecard with file references, engineer-week estimates, and a one-line positioning statement
(*"a competent web-based, single-tenant, India-GST-focused WMS with excellent transactional depth; not yet
mobile-first, multi-channel, analytics-driven or multi-tenant"*). Its Pillar 7 finding — **~65 web
operations screens and 0 mobile screens** — is the clearest available warning about what happens when
CLAUDE.md Principle 3 is deferred one screen at a time (P-054).

---

## Appendix — what this lens did not do

- **I did not re-audit `logistics/docs/TMS/`** (13 files, 4,247 lines). It is inside the caller's line total
  but outside the warehouse product. P-060 records the overlap and the seam; a TMS triage is a separate lens.
- **I did not verify that every table named in §2.8 was actually built.** The prior art names them; several
  appear only in gap sections and are almost certainly proposals. §2.8 says so explicitly.
- **I did not execute any SQL.** P-008's invalidity is asserted from the PostgreSQL grammar rule that a
  table-level `UNIQUE` constraint takes a column list, not an expression. It should be confirmed on the first
  Docker build, and it costs nothing to write it as `CREATE UNIQUE INDEX` regardless.
- **I did not read 13 of the 25 `WMS/` documents end-to-end** — the outbound, GRN and packaging set. Their
  dispositions in §6.1 are marked `†` and are heading-level plus targeted greps. If the new set intends to
  specify outbound in depth, `WMS_Outbound_Flow_Master_Workflow_Matrix.md` (361 lines) and
  `WMS_Outbound_Flow_UI_Screens.md` (351 lines) should be read in full before the outbound chapter is
  written; nothing in this report depends on their contents beyond what is cited.
- **I did not re-derive any sibling finding.** Where a prior-art item duplicates one, I cite the sibling id
  and take its version placement. Where I disagree with a sibling — only twice, at P-025 (owner nullability,
  where R4 `F-001` wins) and P-034 (barcode UoM, where the prior art is more correct than R2 `T-022`) — I say
  so explicitly rather than silently diverging.
- **I wrote no contract and no issue.** This is a triage. The `KEEP` rows are candidates for the new FRD and
  build spec; the `CONTRADICTED` rows are corrections that must land before any of them are used.
