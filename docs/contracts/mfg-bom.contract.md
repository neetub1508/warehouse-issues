# Functional Contract — Manufacturing BOM: versions, alternatives, phantoms, outputs, operations, explosion

> **What this is.** The functional truth for the multi-level, versioned manufacturing bill of materials
> (`whm_boms` and children), its maker–checker lifecycle, effectivity and alternative selection, the
> structure guards (recursion, depth, UoM, phantom), co-/by-product outputs, the optional operation list
> and work-centre master, and the read-only explosion / where-used / cost roll-up services. It replaces
> the multi-level-BOM refusal of `FR-268` / `issues/p6-12.md` (`RN-032`); `FR-268` is withdrawn under `D-16` (`D-17` item 5)
> and superseded by FR-622…FR-631, and `p6-12` is VOID (R30 `CP-FR-002`).
>
> **What this is not.** It does not restate the movement writer ([`movement-post-reverse.contract.md`](movement-post-reverse.contract.md),
> cited by `MPR-*` id). A BOM posts **no movement**. Order creation from a BOM (snapshot, re-explode) is
> [`mfg-production-order.contract.md`](mfg-production-order.contract.md) `PRO-T1-01`; this contract owns
> only the **selection** rule it calls.
>
> **Status.** Derived 2026-10-22 (v0) from [`frd/FRD-MFG.md`](../frd/FRD-MFG.md) `FR-622`…`FR-631`,
> `MD-01`, `MD-09`, §3.1, §4, §7, scenarios `WH-SC-600`…`-609`. Not ratified; run through
> `functional-reviewer` before `P10-03` / `P10-04` are built.

---

## 0. Identity

| | |
|---|---|
| **Workflow** | Create (blank or *Copy from kit*) → edit header, components, alternates, outputs, operations → submit → approve (≠ submitter) or return → effective by date → *New version* → predecessor end-dated / obsoleted; explosion, where-used and cost roll-up as read services; work-centre master |
| **Module** | `warehouse-manufacturing` (`ai.warehousemanufacturing`, `whm_`); registries from `V560001` (`WHM_BOM_USAGE`, `WHM_BOM_TYPE`, `WHM_SUPPLY_METHOD`, `WHM_OUTPUT_TYPE`, `WHM_CONSUMPTION_POLICY`, reason context `BOM_CHANGE`) under the `RL-003` owning-module guard (`FR-621`) |
| **Domain baseline** | `D-1` (layering), `D-10` (no status `CHECK`), `RL-003`, `FR-143` (UoM convertibility guard, reused), `V500060` kits (`whb_kit_definitions`, unchanged), `V500089` phantom-kit guard (precedent), `WhbCostLayerMath` (AVCO/FIFO read), `MD-01`, `MD-09` |
| **Owning tasks** | `issues/p10-03.md` (BOM, explorer) · `issues/p10-04.md` (work centres, operations). Depends on `p10-01` (bootstrap), `p10-02` (registries) |
| **Primary tables** | `whm_boms`, `whm_bom_lines`, `whm_bom_line_alternates`, `whm_bom_outputs` (`V560010`); `whm_work_centres`, `whm_bom_operations` (`V560020`); permissions `V561010`, `V561020` |
| **Status columns** | `whm_boms.status` (`DRAFT`/`SUBMITTED`/`APPROVED`/`OBSOLETE`) — **no `CHECK`** (`D-10`); service-enforced. Work centre: `is_active` + `status` (Department convention) |
| **Permission resources** | `whm_boms:{view,create,edit,delete,export,submit,approve,new_version,obsolete}` · `whm_work_centres:{view,create,edit,delete,export}`; every verb → `:view` in `permission_dependencies` (`FR-669`) |
| **Routes** | WS-320 `/warehouse/manufacturing/boms` · WS-321 `/warehouse/manufacturing/bom-explorer` · WS-322 `/warehouse/manufacturing/work-centres` · **mobile: none** (`R-13`) |
| **Contract version** | `v0 — 2026-10-22` |

### Acceptance checks

| # | Expects | Delivered by |
|---|---|---|
| A1 | A BOM is approved by a second person and is immutable once approved (`WH-SC-600`, `-601`) | `BOM-T1-06`, `BOM-GRD-07`, `BOM-UNR-01` |
| A2 | A new version end-dates its predecessor; orders pick the version effective on their date (`WH-SC-602`) | `BOM-T1-06`, `BOM-T4-01`, `BOM-T1-13` |
| A3 | The alternative is chosen by lot size, then default (`WH-SC-603`) | `BOM-T1-13` |
| A4 | A cycle at any depth is refused with its path (`WH-SC-604`) | `BOM-GRD-05` |
| A5 | A phantom item never holds stock (`WH-SC-605`) | `BOM-GRD-12`, `BOM-T4-03` |
| A6 | Explosion, where-used and cost roll-up are backend services with phantoms, scrap and fixed quantities applied (`WH-SC-606`, `-607`, `-609`) | `BOM-T1-14`…`-16` |
| A7 | *Copy from kit* leaves the kit untouched (`WH-SC-608`) | `BOM-T1-02`, `BOM-UNR-06` |

---

## 1. T1 — State machine

### 1.1 Status inventory

| Entity | Status | Represented by | Reachable via | Exits via | Kind |
|---|---|---|---|---|---|
| BOM version | `DRAFT` | `status` | `BOM-T1-01`, `-02`, `-05`, `-08` | `-04`, `-10` | initial |
| BOM version | `SUBMITTED` | `status`; `submitted_by/at` | `BOM-T1-04` | `-05`, `-06` | active |
| BOM version | `APPROVED` | `status`; `approved_by/at`; `effective_from/to` | `BOM-T1-06` | `-07`, `-09` | active (effective by date) |
| BOM version | `OBSOLETE` | `status`; `obsoleted_by/at` | `BOM-T1-07`, `-09` | none | **terminal** |
| BOM version | *deleted* | row gone (with children, `ON DELETE CASCADE`) | `BOM-T1-10` | none | **terminal** (only a never-referenced `DRAFT`) |
| Work centre | active / inactive | `is_active`, `status` | `BOM-T1-17`, `-18` | `-18` | master |

### 1.2 Transitions

| ID | From | Event | To | Guard | Actor | Side effects | Reason? | UI | Source |
|---|---|---|---|---|---|---|---|---|---|
| BOM-T1-01 | — | Create: item, usage, type, alternative no, site scope (null = all sites), base quantity + UoM, lot-size range, default-alternative flag, process-loss %, consumption policy (null = setting), `effective_from`, change reason | `DRAFT` | `BOM-GRD-01` | `whm_boms:create` | `version_no` = 1 for a new `(item, usage, alternative, site)`; `bom_code` built for display (`FR-622`) | `BOM_CHANGE` reason optional on v1 | WS-320 **Add** | FR-622 |
| BOM-T1-02 | — | **Copy from kit**: pick a kit version (`whb_kit_definitions`) | `DRAFT` | kit version exists; every kit line item active | `whm_boms:create` | lines copied 1:1, `base_quantity = 1`, `copied_from_kit_id` set (provenance only); **the kit is not touched** (`FR-629`, `WH-SC-608`) | no | WS-320 **Copy from kit** | FR-629 |
| BOM-T1-03 | `DRAFT` | Edit header, lines, alternates, outputs, operations | `DRAFT` | `BOM-GRD-01`…`-04`, `-08`…`-11` per field | `whm_boms:edit` | children replaced in one transaction; optimistic `version` | no | WS-320 **Edit** (multi-tab modal) | FR-622, FR-623, FR-624, FR-631 |
| BOM-T1-04 | `DRAFT` | **Submit** | `SUBMITTED` | `BOM-GRD-01`…`-11`, `-19` (full structure check, incl. `-05` recursion, `-06` depth); ≥ 1 line | `whm_boms:submit` | `submitted_by/at`; notification to holders of `:approve` at the site | no | WS-320 **Submit** | FR-625 |
| BOM-T1-05 | `SUBMITTED` | **Return** for correction | `DRAFT` | actor ≠ submitter (`BOM-GRD-07`) | `whm_boms:approve` | `returned_by/at`, `return_note` (required) | **yes** (note) | Approval tab **Return** | FR-625 |
| BOM-T1-06 | `SUBMITTED` | **Approve** | `APPROVED` | `BOM-GRD-01`…`-12` re-run under lock; `BOM-GRD-07` (≠ submitter); `BOM-GRD-13` (effectivity); `BOM-GRD-14` (default alternative) | `whm_boms:approve` | `approved_by/at`; `BOM-T4-01` predecessor end-dated; `BOM-T4-02` wholly superseded predecessor → `OBSOLETE` | no | Approval tab **Approve** | FR-625 |
| BOM-T1-07 | `APPROVED` | **Obsolete** manually | `OBSOLETE` | — (existing orders keep their frozen snapshot, `FR-633`) | `whm_boms:obsolete` | `obsoleted_by/at`; `PLANNED` orders on this version now fail release `PRO-GRD-07` (edge `BOM-EC-06`) | **yes** (`BOM_CHANGE`) | WS-320 **Obsolete** | FR-625 |
| BOM-T1-08 | `APPROVED` · `OBSOLETE` | **New version** | new row `DRAFT` | no other `DRAFT`/`SUBMITTED` version of the same `(item, usage, alternative, site)` (`BOM-GRD-15`) | `whm_boms:new_version` | deep copy of header + children; `version_no` = max + 1; `supersedes_bom_id` = source; `effective_from` proposed = today | `BOM_CHANGE` reason **required** | WS-320 **New version** | FR-625 |
| BOM-T1-09 | `APPROVED` | (effect of approving a successor whose `effective_from` ≤ this one's `effective_from`) | `OBSOLETE` | — | system, in `BOM-T1-06`'s transaction | `obsoleted_by` = approver | — | — | FR-625 |
| BOM-T1-10 | `DRAFT` | **Delete** | *deleted* | never referenced (`BOM-GRD-16`) | `whm_boms:delete` | children cascade | no | WS-320 **Delete** | FR-625 |
| BOM-T1-11 | `APPROVED` · `SUBMITTED` · `OBSOLETE` | Edit / delete | refused | — | any | none | — | `BOM-UNR-01`, `-02` | FR-625 |
| BOM-T1-12 | — | Set default alternative | via `BOM-T1-03` on a `DRAFT` | effective on approval (`BOM-GRD-14`) | `:edit` | — | no | Header tab | FR-622 |
| BOM-T1-13 | — | **Select BOM** (service, called by `PRO-T1-01`/`-02`, `MRP-T1-13`; R31 F-MF-023) for `(item, usage, site, date, quantity)` — **the date is always the order's (or proposal's) planned start date**, at creation and again at release (MD-19) | — (read) | — | system | order of precedence (`FR-626`): explicit BOM id → site-specific before all-sites → `APPROVED` and effective on the date (`[from, to)`) → alternative whose `[lot_size_from, lot_size_to]` contains the quantity → `is_default_alternative` → lowest `alternative_no` among ties (`BOM-OPEN-01`); `is_rework_alternative` rows only for a `REWORK` order and preferred there (MD-26) → `422 BOM_NOT_FOUND` naming item, site, date, usage | — | — | FR-626 |
| BOM-T1-14 | — | **Explode** item × quantity × date × site × usage | — (read) | an approved BOM selectable by `BOM-T1-13` at each level | `whm_boms:view` | indented tree: quantity scaled by `qty ÷ base_quantity ÷ (1 − process_loss_percent ÷ 100)` (R29 F29; fixed lines excepted, the `PRO-T4-01` factor), line scrap applied (`required = qty × (1 + scrap%)`), `is_fixed_quantity` unscaled, phantom components replaced by their own components multiplied through with `phantom_path`, low-level code shown (`FR-628`, `WH-SC-606`, `WH-SC-609`) | — | WS-321 **Explosion** | FR-628 |
| BOM-T1-15 | — | **Where-used** single-level / recursive for a component | — (read) | — | `whm_boms:view` | parents with quantity per parent; recursive walks up through phantoms and sub-assemblies (`WH-SC-607`) | — | WS-321 **Where-used** | FR-628 |
| BOM-T1-16 | — | **Cost roll-up** for an explosion | — (read) | — | `whm_boms:view` (+ platform view-cost) | per level: unit cost from current cost layers via `WhbCostLayerMath` (AVCO/FIFO per the item's method), extended cost, `missingCost = true` where no layer exists (`WH-SC-606`); never computed on the frontend (rule 8) | — | WS-321 **Cost roll-up** | FR-628 |
| BOM-T1-17 | — | Create / edit work centre | active | `BOM-GRD-17` | `whm_work_centres:create`/`:edit` | — | no | WS-322 | FR-630 |
| BOM-T1-18 | active ↔ inactive | Toggle status | inactive / active | deactivate: `BOM-GRD-18` | `whm_work_centres:edit` | — | no | WS-322 row toggle | FR-630 |

### 1.3 Guards

| ID | Predicate | Refusal | Backstop | Source |
|---|---|---|---|---|
| BOM-GRD-01 | Header: parent item active and stock-holding; usage, type, policy in their code lists; `alternative_no ≥ 1`; `base_quantity > 0`; `base_uom_code` convertible to the item base UoM; `effective_from` set, `effective_to` null or > `effective_from`; `lot_size_from ≤ lot_size_to` when both set; `process_loss_percent` in [0, 100) | `422` field-named (`effectiveTo`, `baseQuantity`, …) · `422 BOM_UOM_NOT_CONVERTIBLE` | composite FKs to `whb_code_list_values`; `CHECK base_quantity > 0` | FR-622 |
| BOM-GRD-02 | Line: component active, ≠ parent; `quantity > 0`; `uom_code` convertible to the component base (`FR-143` guard reused); `component_scrap_percent` in [0, 100); `supply_method` in `WHM_SUPPLY_METHOD`; default supply location stock-holding at the BOM's site (if site-scoped); `line_no` unique | `422 BOM_UOM_NOT_CONVERTIBLE` · `lines[i].uomCode`; `422 BOM_COMPONENT_IS_PARENT`; `422` field-named | uk `(bom_id, line_no)`; `CHECK quantity > 0` | FR-623 |
| BOM-GRD-03 | Alternate: `alternate_item_id` ≠ primary component, ≠ parent; UoM convertible; one row per `(bom_line_id, alternate_item_id)`; `usage_percent` in (0, 100] or null | `422 BOM_ALTERNATE_INVALID` · `lines[i].alternates[j]` | uk `(bom_line_id, alternate_item_id)` | FR-623 |
| BOM-GRD-04 | Outputs: `output_type` ∈ {`CO_PRODUCT`, `BY_PRODUCT`} (main = header item, no row); output item ≠ parent and **not a component of the same BOM**; Σ `cost_share_percent` of `CO_PRODUCT` ≤ 100; `cost_share_percent` only on `CO_PRODUCT`, `by_product_unit_value` only on `BY_PRODUCT` | `422 BOM_OUTPUT_IS_COMPONENT` · `422 BOM_COST_SHARE_EXCEEDS_100` · `422` field-named | uk `(bom_id, sequence)`, `(bom_id, output_item_id)` | FR-624 |
| BOM-GRD-05 | **No cycle at any depth**: DFS over the approved-and-candidate graph of every usage-`PRODUCTION`/`SUBCONTRACT` BOM effective on any overlapping date | `422 BOM_RECURSIVE` naming the path (`PUMP-100 > MOTOR-ASSY > PUMP-100`) | — (service) | FR-627, `WH-SC-604` |
| BOM-GRD-06 | Depth ≤ 20 levels after phantom expansion; a `PHANTOM` BOM is never its own parent | `422 BOM_DEPTH_EXCEEDED` / `422 BOM_RECURSIVE` | — | FR-627 |
| BOM-GRD-07 | **Maker–checker**: approver / returner ≠ `submitted_by` | `403 BOM_SELF_APPROVAL` (MD-21) | — | FR-625, `WH-SC-601` |
| BOM-GRD-08 | `operation_seq` on a line or output names an operation of the **same** BOM | `422 BOM_OPERATION_NOT_FOUND` · `lines[i].operationSeq` | — | FR-631 |
| BOM-GRD-09 | Operation: work centre active, same site when the BOM is site-scoped; `setup_minutes ≥ 0`, `run_minutes_per_unit ≥ 0`; `operation_seq` unique | `422` field-named | uk `(bom_id, operation_seq)` | FR-631 |
| BOM-GRD-10 | Line effectivity `[line_effective_from, line_effective_to)` lies inside the version's effectivity | `422 BOM_LINE_EFFECTIVITY_OUTSIDE_VERSION` | — | FR-623 |
| BOM-GRD-11 | `lead_time_offset_days` ≥ 0; `alternate_group_code` + `alternate_priority` both set or both null; priorities unique in a group | `422` field-named | — | FR-623 |
| BOM-GRD-12 | Approving a `PHANTOM` BOM that would become the item's default `PRODUCTION` BOM: the item has **zero on-hand** at every site in scope (contract rule, edge `BOM-EC-04`) | `409 PHANTOM_ITEM_HAS_STOCK` naming site, location, quantity | movement-line validator `BOM-T4-03` | FR-627 |
| BOM-GRD-13 | **One approved BOM per `(item, usage, alternative, coalesce(site))` on any date**: after setting the predecessor's `effective_to` (`BOM-T4-01`), no other `APPROVED` row overlaps `daterange(from, to, '[)')`; service pre-check followed by an explicit `flush()` | `409 BOM_EFFECTIVITY_OVERLAP` naming the overlapping version | gist `EXCLUDE` (FRD §4) | FR-626 |
| BOM-GRD-14 | At most one `is_default_alternative` per `(item, usage, COALESCE(site, nil-uuid))` among `APPROVED` current non-rework rows; approving a default when another alternative is default refuses unless that other is this version's predecessor | `409 BOM_DEFAULT_ALTERNATIVE_EXISTS` | partial uk | FR-622, FR-626 |
| BOM-GRD-15 | One open (`DRAFT`/`SUBMITTED`) successor per `(item, usage, alternative, site)` | `409 BOM_VERSION_IN_PROGRESS` naming it | — | FR-625 |
| BOM-GRD-16 | Delete: `DRAFT` **and** no `whm_production_orders.bom_id`, no `whm_mrp_proposals.bom_id`, no `supersedes_bom_id` points at it | `409 BOM_REFERENCED` naming the first referrer | FK `bom_id` from orders (no cascade) | FR-625 |
| BOM-GRD-17 | Work centre: `code` upper-cased, unique per company + site; `available_minutes_per_day` in [0, 1440]; `working_days` matches `^[MTWTFSS-]{7}$`; `efficiency_percent` > 0; `parallel_units ≥ 1`; default line-side location of type `LINE_SIDE` at the same site | `422` field-named; `409` duplicate code (`/validate/code`) | uk `(company_id, warehouse_id, code)` | FR-630 |
| BOM-GRD-19 | A `PHANTOM` BOM carries **no** co- or by-product output rows (they would be lost when it is exploded into its parent); its operations are allowed and are appended to the parent's operation list at explosion, keeping their component and output links (R31 `BOM-OPEN-02`) | `422 PHANTOM_OUTPUTS_NOT_ALLOWED` · `outputs` | — | FR-624, FR-627 |
| BOM-GRD-18 | Deactivate work centre: no `OPEN`/`STARTED` order operation and no `DRAFT`/`SUBMITTED`/current `APPROVED` BOM operation references it | `409 WORK_CENTRE_IN_USE` naming one referrer | — | FR-630 |

### 1.4 Unreachable

| ID | Must never happen | Source |
|---|---|---|
| BOM-UNR-01 | An edit of an `APPROVED`, `SUBMITTED` or `OBSOLETE` version — `PUT` answers `409 BOM_APPROVED_IMMUTABLE` (`FR-625`) | FR-625 |
| BOM-UNR-02 | A delete of anything but a never-referenced `DRAFT` | FR-625 |
| BOM-UNR-03 | A BOM change altering an existing order's components, outputs or operations (`FR-633`, `WH-SC-612`) | FR-633 |
| BOM-UNR-04 | Two `APPROVED` versions of one `(item, usage, alternative, site)` overlapping on a date | FR-626 |
| BOM-UNR-05 | An approved structure containing a cycle; a stock-bearing movement line for a phantom item | FR-627 |
| BOM-UNR-06 | Any write to `whb_kit_definitions` from MFG, or a `whb_`/`wh_` table gaining an FK to `whm_boms` (`D-1`, `FR-620`) | FR-620 |
| BOM-UNR-07 | A BOM posting a movement or creating a reservation | FR-628 |
| BOM-UNR-08 | Explosion, where-used or roll-up arithmetic in a page component (rule 8) | FR-628 |
| BOM-UNR-09 | An MFG registry row (movement, document or location type, code list, reason context, the `REWORK` disposition, print kind, number series) inserted without the `RL-003` owning-module guard (the `V525000` step-4 pattern, `warehouse-adapter-example`), or a re-seed of core's `COST_OBJECT_TYPE.PRODUCTION_ORDER` or `QC_SOURCE_TYPE.PRODUCTION_RECEIPT` / `IN_PROCESS` | FR-621 |
| BOM-UNR-10 | An MFG grid without `grid_column_definitions` + `filter_definitions` + a `grid_preferences` row carrying both default filters and default columns in its table migration, or without its `COMMON_FILTER_CONFIGS` scope; an export narrower than its grid; an MFG verb that is not a `resource:action` permission with `permission_dependencies` on `:view`; an AUDITOR export grant; an MFG mobile screen; an L2 under L1 *Manufacturing* with more than 8 leaves | FR-669 |

## 2. T2 — Action × role × state (maker–checker)

| ID | Action | Permission | Allowed from | Persona / extra | Source |
|---|---|---|---|---|---|
| BOM-T2-01 | Create / Copy from kit / Edit | `whm_boms:create` / `:edit` | — / `DRAFT` | production engineer | FR-622, FR-625 |
| BOM-T2-02 | Submit | `:submit` | `DRAFT` | production engineer (maker) | FR-625 |
| BOM-T2-03 | Approve / Return | `:approve` | `SUBMITTED` | engineering approver (checker, ≠ submitter, `BOM-GRD-07`) | FR-625 |
| BOM-T2-04 | New version | `:new_version` | `APPROVED` · `OBSOLETE` | production engineer | FR-625 |
| BOM-T2-05 | Obsolete | `:obsolete` | `APPROVED` | engineering approver | FR-625 |
| BOM-T2-06 | Delete | `:delete` | never-referenced `DRAFT` | creator or `:approve` holder | FR-625 |
| BOM-T2-07 | Explorer (explode, where-used, roll-up) | `whm_boms:view` (roll-up values need platform view-cost) | — | any MFG persona; cost accountant | FR-628 |
| BOM-T2-08 | Export BOMs / explosion | `whm_boms:export` | — | **not AUDITOR** (`V698`) | FR-669 |
| BOM-T2-09 | Work centres | `whm_work_centres:*` | — | production planner / admin | FR-630 |

## 3. T3 — Time-driven rules

| ID | Rule | Trigger | Changes | Notified | Job | Once? | Source |
|---|---|---|---|---|---|---|---|
| BOM-T3-01 | Pending BOM approval | `SUBMITTED` > `warehouse.approval.pending_alert_hours` | nothing; never auto-approves | holders of `whm_boms:approve` at the site | hourly (core approval alert job) | once per episode | FR-625 |
| BOM-T3-02 | Effectivity roll-over | calendar date passes `effective_to` / `effective_from` | **nothing is written** — effectivity is evaluated at query time by `BOM-T1-13` (half-open range); the status stays `APPROVED` | — | none | — | FR-626 |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in | Source |
|---|---|---|---|---|
| BOM-T4-01 | approve a version with `supersedes_bom_id` (or any `APPROVED` sibling of the same key covering its `effective_from`) | that predecessor's `effective_to` := new `effective_from`, same transaction, before the overlap check (`FR-625`, `WH-SC-602`) | BOM approval service | FR-625 |
| BOM-T4-02 | approve, predecessor `effective_from` ≥ new `effective_from` | predecessor → `OBSOLETE` (`BOM-T1-09`) | same | FR-625 |
| BOM-T4-03 | always (module on) | a **movement-line validator** registered with the writer refuses any line for an item whose current default `PRODUCTION` BOM is `PHANTOM` (`422 PHANTOM_ITEM_NOT_STOCKABLE`, `V500089` precedent; `WH-SC-605`) | MFG validator bean, called by `WhbStockLedgerWriter.post` | FR-627 |
| BOM-T4-04 | approve / return / obsolete / new version / delete | platform audit `BOM_APPROVED` / `BOM_RETURNED` / `BOM_OBSOLETED` / `BOM_VERSION_CREATED` / `BOM_DELETED` with `bom_code` | service | FR-625 |
| BOM-T4-05 | order creation | `BOM-T1-13` selects; the order snapshots (owned by `PRO-T4-01`) — the BOM row is not changed and gains no counter | production-order service | FR-626, FR-633 |
| BOM-T4-06 | none | no ledger movement, no reservation, no cost layer, no genealogy, no QC from any BOM action | — (stated) | FR-628 |

## 5. T5 — Screen contract

Defaults: newest first unless stated; tiles filter-aware, no cache name; export = grid superset +
`createdByName`, `updatedByName`; dates that are SQL `DATE` render with `formatDateSync`, timestamps with
`formatDateWithTimezoneSync`; every date input is `<DatePicker>`; modals `lazyModal()` + `Suspense`,
refusals shown inside the modal (`AlertBox`).

### 5.1 WS-320 BOMs (reference: **Customer** — relations + child editors)

| | |
|---|---|
| **Grid** | `whm_boms` · scope `WAREHOUSE_MFG_BOM` · sort `e.updated_at DESC` |
| **Tiles (5)** | `DRAFT` · `SUBMITTED` · `APPROVED` (effective today) · `OBSOLETE` · *Phantom* |
| **Columns** | `bomCode`, `itemCode`, `itemName`, `bomUsage`, `bomType`, `alternativeNo`, `versionNo`, `warehouseName` (*All sites* when null), `baseQuantity`, `baseUomCode`, `isDefaultAlternative`, `effectiveFrom`, `effectiveTo`, `status`, `lineCount`, `outputCount`, `operationCount`, `submittedByName`, `approvedByName`, `approvedAt`, `createdByName`, `updatedByName`, `updatedAt` |
| **Filters** | `search` (code / item); `itemId`; `componentItemId` (BOMs containing it); `bomUsage`; `bomType`; `warehouseId`; `status`; `effectiveOn` (`date`, `dateOnly`); `isDefaultAlternative` (boolean) — all in `COMMON_FILTER_CONFIGS.WAREHOUSE_MFG_BOM` |
| **Row actions** | View · Edit (`DRAFT` && `:edit`) · Submit · Approve · Return · New version · Obsolete · Delete · Explode (→ WS-321) |
| **Toolbar** | Add · Copy from kit · Export |
| **Modal** | `size="lg"`, `minWidth={500}`, resizable; tabs **Header · Components · Alternates · Outputs · Operations · Approval** (`useModalTabState`); Components grid editor: `lineNo`, `componentItem`, `quantity`, `uomCode`, `componentScrapPercent`, `isFixedQuantity`, `supplyMethod`, `defaultSupplyLocation`, `operationSeq`, `leadTimeOffsetDays`, `alternateGroupCode`, `alternatePriority`, `limitsOutputExpiry`, `lineEffectiveFrom/To`, `referenceText` |
| **View** | `ViewModalBase`, tabs ≤ 2 sections each; Approval tab shows submitted/approved/returned/obsoleted by-at and `returnNote` |
| **Export** | grid columns + **Lines** sheet + **Outputs** sheet + **Operations** sheet + `createdByName`, `updatedByName` |

### 5.2 WS-321 BOM Explorer (report)

Inputs: `itemId` (required), `quantity` (default base quantity), `date` (`DatePicker`, default today), `warehouseId`, `bomUsage`, mode **Explosion · Where-used (single) · Where-used (recursive) · Cost roll-up**. Grid `whm_bom_explosion` · scope `WAREHOUSE_MFG_BOM_EXPLOSION`; columns `level`, `path`, `itemCode`, `itemName`, `bomCode`, `quantity`, `uomCode`, `componentScrapPercent`, `isFixedQuantity`, `supplyMethod`, `isPhantom`, `phantomPath`, `lowLevelCode`, `unitCost`, `extendedCost`, `missingCost`. Tree + table views of the same backend result; export superset. No write action.

### 5.3 WS-322 Work Centres (reference: **Department**)

Grid `whm_work_centres` · scope `WAREHOUSE_MFG_WORK_CENTRE` · sort `e.code ASC`; tiles active / inactive / total / with line-side / without department; columns `code`, `name`, `warehouseName`, `departmentName`, `availableMinutesPerDay`, `workingDays`, `efficiencyPercent`, `parallelUnits`, `costRatePerHour` (view-cost; recorded only, `OD-43`), `defaultLineSideLocationCode`, `isActive`, `createdByName`, `updatedByName`; filters `search`, `warehouseId`, `departmentId`, `isActive`; `/validate/code` + `/validate/name`; actions View · Edit (active) · Toggle · Delete (never referenced); export superset.

## 6. Error codes

| Code | HTTP | When | FR | WH-SC |
|---|---|---|---|---|
| `BOM_SELF_APPROVAL` | 403 | approver/returner is the submitter | FR-625 | 601 |
| `BOM_APPROVED_IMMUTABLE` | 409 | edit/delete of a non-`DRAFT` version | FR-625 | 600 |
| `BOM_RECURSIVE` | 422 | cycle; message carries the path | FR-627 | 604 |
| `BOM_DEPTH_EXCEEDED` | 422 | > 20 levels | FR-627 | — |
| `BOM_NOT_FOUND` | 422 | selection found no approved, effective BOM (item, site, date, usage named) | FR-626 | 602, 603 |
| `BOM_EFFECTIVITY_OVERLAP` | 409 | two approved versions would overlap | FR-626 | 602 |
| `BOM_DEFAULT_ALTERNATIVE_EXISTS` | 409 | a second default alternative | FR-622 | 603 |
| `BOM_VERSION_IN_PROGRESS` | 409 | a second open successor | FR-625 | — |
| `BOM_REFERENCED` | 409 | delete of a referenced draft | FR-625 | — |
| `BOM_UOM_NOT_CONVERTIBLE` | 422 | header/line/alternate UoM not convertible | FR-622, FR-623 | — |
| `BOM_COMPONENT_IS_PARENT` | 422 | line component = parent | FR-627 | — |
| `BOM_ALTERNATE_INVALID` | 422 | alternate = primary/parent or bad UoM | FR-623 | 623 |
| `BOM_OUTPUT_IS_COMPONENT` | 422 | output item also a component | FR-624 | — |
| `BOM_COST_SHARE_EXCEEDS_100` | 422 | Σ co-product shares > 100 | FR-624 | 640 |
| `BOM_OPERATION_NOT_FOUND` | 422 | line/output names a missing operation | FR-631 | — |
| `BOM_LINE_EFFECTIVITY_OUTSIDE_VERSION` | 422 | line effectivity outside version | FR-623 | — |
| `PHANTOM_ITEM_HAS_STOCK` | 409 | approving a default phantom for an item with stock | FR-627 | 605 |
| `PHANTOM_ITEM_NOT_STOCKABLE` | 422 | movement line for a phantom item | FR-627 | 605 |
| `WORK_CENTRE_IN_USE` | 409 | deactivate a referenced work centre | FR-630 | — |
| `PHANTOM_OUTPUTS_NOT_ALLOWED` | 422 | output rows on a `PHANTOM` BOM | FR-624, FR-627 | — |

Codes not named in the FRD (`BOM_EFFECTIVITY_OVERLAP`, `BOM_DEFAULT_ALTERNATIVE_EXISTS`, `BOM_VERSION_IN_PROGRESS`, `BOM_REFERENCED`, `PHANTOM_ITEM_HAS_STOCK`, `PHANTOM_ITEM_NOT_STOCKABLE`, `WORK_CENTRE_IN_USE`, `PHANTOM_OUTPUTS_NOT_ALLOWED` and the field-level ones) are **contract-defined** here. `BOM_NOT_EFFECTIVE` (`BOM-EC-06`) is `PRO-GRD-07`'s *(proposed)* code, fixed by `p10-05`'s ratification item.

## 7. Edge cases

| ID | Case | Behaviour | FR | WH-SC |
|---|---|---|---|---|
| BOM-EC-01 | v2 approved effective 2026-11-01 while v1 is current | v1 `effective_to` = 2026-11-01; an order with planned start 2026-10-30 selects v1, planned start 2026-11-02 selects v2 (creation day irrelevant, MD-19) | FR-625, FR-626 | 602 |
| BOM-EC-02 | v2 approved with `effective_from` ≤ v1's | v1 → `OBSOLETE` in the same transaction | FR-625 | — |
| BOM-EC-03 | Two alternatives, lot sizes 1–49 and 50+, order for 60 | alternative 2 | FR-626 | 603 |
| BOM-EC-04 | Item made phantom while it still holds stock | approval refused `PHANTOM_ITEM_HAS_STOCK`; the stock must be consumed or reclassified first | FR-627 | 605 |
| BOM-EC-05 | Scrap 5 % on `CASING-01`, `BOLT-M8` fixed 2 + 8/unit, quantity 100 | explosion shows 105 and 802; the order snapshot reproduces them (`PRO-T4-01`) | FR-623, FR-633 | 609 |
| BOM-EC-06 | BOM obsoleted while a `PLANNED` order references it | the order keeps its snapshot; release refused `BOM_NOT_EFFECTIVE` *(proposed)* (`PRO-GRD-07`); planner may *Re-explode* in `PLANNED` | FR-633, FR-635 | 612 |
| BOM-EC-07 | Phantom nested in phantom | multiplied through; `phantom_path` `PARENT>P1>P2`; depth counted after expansion | FR-627, FR-628 | 606 |
| BOM-EC-08 | Component with no cost layer in roll-up | `missingCost = true`, extended cost excluded from the level total and the total flagged incomplete | FR-628 | 606 |
| BOM-EC-09 | Site-specific and all-sites BOMs both effective | site-specific wins | FR-626 | — |
| BOM-EC-10 | Cycle only through a version effective in the future | refused: the cycle check spans every overlapping effectivity, not just today | FR-627 | 604 |
| BOM-EC-11 | *Copy from kit* of a kit whose item is not stock-holding | refused `BOM-GRD-01` | FR-629 | 608 |

## 8. Out of scope

Engineering change orders / change-number master (`R-08`); configurable / variant BOMs (`R-09`); recipes with potency, catch weight (`R-10`); unbuild (`R-07`); routing alternatives and finite capacity (`R-01`); labour/overhead absorption from work-centre rates (`OD-43`); editing kits; mobile (`R-13`).

## 9. Amendments

| Date | Change |
|---|---|
| 2026-10-22 | v0 derived from FRD-MFG FR-622…FR-631 |
| 2026-10-22 | Consistency pass: selection date = planned start (MD-19), `403` self-approval (MD-21), `is_rework_alternative` (MD-26), COALESCE unique index (MD-27) |
| 2026-10-22 | Edge-case ids renamed `BOM-E-nn` → `BOM-EC-nn` (the design-set checker reads `E-nn` as a review finding) |
| 2026-10-23 | R31: phantom outputs refused, `BOM-GRD-19` (`BOM-OPEN-02` DECIDE); `BOM-OPEN-01`, `-03`, `-04` ratified; `BOM-T1-13` cross-reference `MRP-T1-13` (F-MF-023); `BOM_NOT_EFFECTIVE` marked proposed (F-MF-019); Source FR on every rule row (F-MF-018) |
| 2026-10-22 | R29: `BOM-T1-07` and `BOM-EC-06` cite `PRO-GRD-07` (the release BOM-effective guard), not `PRO-GRD-03` (F31); explosion applies `process_loss_percent` (F29) |

## 10. Invariants and scenarios

`D-1`, `D-10`, `RL-003`, `FR-143`; `MD-01`, `MD-09`; scenarios `WH-SC-600`…`-609`, `-612`.

## 11. Open rows

| ID | Question | Default |
|---|---|---|
| BOM-OPEN-01 *(resolved — R31-decisions DECIDE: default stands; `BOM-T1-13`)* | Two approved alternatives whose lot-size ranges both contain the quantity (FRD silent) | default alternative if among them, else lowest `alternative_no`; approval does not refuse overlapping ranges |
| BOM-OPEN-02 *(resolved — R31-decisions DECIDE: default stands; `BOM-GRD-19`)* | May a `PHANTOM` BOM carry co-/by-product outputs or operations? (they would be lost on explosion) | refuse outputs on a phantom (`422 BOM_OUTPUT_IS_COMPONENT` family → new `422 PHANTOM_OUTPUTS_NOT_ALLOWED`); operations allowed and appended to the parent's list at explosion, keeping their links — **adopted** |
| BOM-OPEN-03 *(resolved — MD-27)* | uk `(item_id, bom_usage, alternative_no, version_no, warehouse_id)` with a nullable `warehouse_id` treats NULLs as distinct (PostgreSQL), so two all-sites v1 rows are allowed | **adopted:** unique index on `(item_id, bom_usage, alternative_no, version_no, COALESCE(warehouse_id, '00000000-0000-0000-0000-000000000000'::uuid))`; the default-alternative partial index uses the same expression |
| BOM-OPEN-04 *(resolved — R31-decisions DECIDE: default stands)* | Should an `APPROVED` version whose `effective_to` has passed be auto-`OBSOLETE`? | no (`BOM-T3-02`); `OBSOLETE` only by `BOM-T1-07`/`-09` |
