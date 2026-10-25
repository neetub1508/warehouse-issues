# Gap analysis — slice `mr-issue-return-bom` (PRD lines 188–229, §7 + §8)

Sources: PRD `prd.txt:188-229`; questionnaire `prd.txt:540-582` (Q-M1…Q-M6, Q-B1…Q-B6).
Design set (`warehouse-issues/docs`): `contracts/material-requisition.contract.md` (MRQ), `contracts/store-issue-return.contract.md` (SIR), `contracts/mfg-bom.contract.md` (BOM), `contracts/mfg-material-staging-issue.contract.md` (MSI), `contracts/mfg-production-order.contract.md` (PRO), `contracts/mfg-costing-close.contract.md` (CST), `contracts/incoming-inspection-sampling.contract.md` (IIS), `frd/FRD-STORES.md` (FR-528…539, STO-D*), `frd/FRD-MFG.md` (FR-620…669, MD-*, R-01…R-14), `DATA-MODEL.md` §2.7, `DECISIONS.md` D-13.
Issues: #570 P8-09 requisition (CLOSED, built), #571 P8-10 store issue, #572 P8-11 store return, #573 P8-12 print docs, #574 P8-13 registers, #567 P8-06 polymorphic QC (CLOSED), #581 P9-04 purchase requisition (trade), #592…#604 P10-01…P10-13 (manufacturing), #144 P6-12 (NOT_PLANNED, VOID — superseded by P10-03), follow-ups #621 #623 #624 #625 #634 (requisition).
Code spot-check (`classic/`): `warehouse/…/WhMaterialRequisitionService.java`, `WhRequisitionReservationCoordinator.java` (FEFO→FIFO hold), `port/purchase/PurchaseRequisitionHandoff.java`, `V511318` (MRQ tables), `warehouse-base/…/V501233` (code lists), frontend `dashboard/warehouse/stores/requisitions` + `requisition-issue-queue`. **No** `wh_store_issues` / `wh_store_returns` tables or services exist yet; **no** `warehouse-manufacturing` module exists; **no** mobile requisition screen.

## Summary counts

| Status | Count |
|---|---|
| COVERED-BUILT | 9 |
| COVERED-PLANNED | 52 |
| DESIGN-ONLY | 0 |
| PARTIAL | 25 |
| DECLINED | 1 |
| OTHER-MODULE | 0 |
| MISSING | 16 |
| **Total atomic requirements** | **103** |

(Everything in the design set for this slice has an owning issue, so DESIGN-ONLY is 0. Most MFG-side rows are COVERED-PLANNED against open P10 issues whose module does not yet exist.)

## Matrix

### §7 intro

| Id | PRD requirement (short) | Status | Evidence | Gap / note |
|---|---|---|---|---|
| 7-01 | Store issues **only** against an approved MR | PARTIAL | FR-535; SIR-GRD-02/-03; #571 | Direct issue is allowed behind `warehouse.stores.direct_issue_allowed` + `:issue_without_requisition`. Also MFG `STAGE_BACKFLUSH` components move by **staging list** and `BACKFLUSH` components are consumed at receipt, both with **no MR** (MSI §0 workflow; FR-638/639/645) — see CONFLICT C1 |
| 7-02 | Material coming back needs an **approved** Material Return before stock | COVERED-PLANNED | FR-536/537; SIR-T1-05…-07; #572 | Approval = stores post ≠ submitter; chain differs (C3) |

### §7.1 Material Requisition

| Id | PRD requirement (short) | Status | Evidence | Gap / note |
|---|---|---|---|---|
| 7.1-01 | Type: against Production Order (from BOM) | COVERED-PLANNED | `COST_OBJECT_TYPE.PRODUCTION_ORDER` seeded (`V501233:66`); `WhMaterialRequisitionPort` built (#570, MRQ §8a); MFG *Request materials* MSI-T1-01 (#597) | Resolver arrives with MFG (#592/#596); until then the type is not usable |
| 7.1-02 | Type: against SO sample | PARTIAL | `REQUISITION_PURPOSE.SAMPLE` (`V501233:75`), built #570 | No `SALES_ORDER` cost object / SO reference on the MR; sample cannot be tied to a customer SO |
| 7.1-03 | Type: Maintenance / General | COVERED-BUILT | `REQUISITION_PURPOSE.MAINTENANCE`, cost objects `MACHINE`/`DEPARTMENT`/`COST_CENTRE` (`V501233`); #570 | — |
| 7.1-04 | Type: Consumables | COVERED-BUILT | `REQUISITION_PURPOSE.CONSUMPTION`; item type `CONSUMABLE` stock-holding (MRQ-GRD-03); #570 | Label "Consumption" not "Consumables" |
| 7.1-05 | Type: Replacement (extra issue for rejection/scrap at a stage) | PARTIAL | MSI-T1-13 *Request extra* with `PRODUCTION_DEVIATION` reason (#597) | No `REPLACEMENT` purpose; not linked to the rejection/scrap record or to the stage that scrapped it |
| 7.1-06 | Field: MR no., date | COVERED-BUILT | gapless `MRQ` series, MRQ-T1-01; #570 | — |
| 7.1-07 | Field: department, requested by | COVERED-BUILT | MRQ-T1-01, MRQ-GRD-01 (requester ∈ department) | — |
| 7.1-08 | Field: production order / SO / job card ref | PARTIAL | cost object (type, id, frozen `cost_object_ref`); port `sourceDocumentType/Id/Ref` | Production order yes (via MFG); **SO** and **job card / operation** refs absent |
| 7.1-09 | Field: stage | MISSING | — (no `operation_seq` on `wh_material_requisition_lines`, V511318) | Needed for stage-wise MR (8.4-08) |
| 7.1-10 | Field: required date | COVERED-BUILT | header required-by + line required date (MRQ-T1-01, GRD-03) | — |
| 7.1-11 | Lines: item, required qty, UoM | COVERED-BUILT | MRQ-T1-01; line UoM endpoint (§5.1) | One line per item (MRQ-GRD-12) |
| 7.1-12 | Lines: batch preference | MISSING | — | Reservation picks FEFO/FIFO automatically (MRQ-T4-01); requester cannot express a lot preference |
| 7.1-13 | Lines: remarks | COVERED-BUILT | MRQ-T1-01 | — |
| 7.1-14 | Flow Draft→Submitted→Approved→Partly issued→Fully issued / Short-closed | COVERED-BUILT | MRQ §1.1 (`DRAFT`/`SUBMITTED`/`APPROVED`/`PARTIALLY_ISSUED`/`ISSUED`/`CLOSED`) + `REJECTED`, `CANCELLED`, Recall; #570 | Partly/Fully issued transitions fire only once store issue (#571) is built — today approved MRs cannot progress |
| 7.1-15 | Approved by HOD / Production Manager | COVERED-BUILT | MRQ-GRD-05 (`requisition_approver_scope = DEPARTMENT_HEAD` → head/deputy; maker≠checker); optional 2nd level by value (OD-29) | For MFG-sourced MRs the approver is the **stores** approver (FRD-MFG:165) — CONFLICT C4; #623 open bug (Approve shown to non-head) |
| 7.1-16 | Extra issue beyond BOM needs a reason code | COVERED-PLANNED | FR-643; MSI-GRD-07 (`WARN` → `PRODUCTION_DEVIATION`); #597 | Under `FLEXIBLE` no reason; under `STRICT` refused |
| 7.1-17 | …and a higher approval | PARTIAL | MRQ approval is a normal approval; value threshold 2nd approval is by **value**, not by excess (MRQ-GRD-11) | No escalation for over-BOM quantity — CONFLICT C6 |
| 7.1-18 | Short free stock → one-click PR from MR (§5.1) | COVERED-PLANNED | MRQ-T1-11 / WS-274 *Raise PR*, `PurchaseRequisitionHandoff` port **built** (#570); trade bean P9-04 #581 open | Action absent until warehouse-trade ships the bean (#625 test debt) |

### §7.2 Material Issue

| Id | PRD requirement (short) | Status | Evidence | Gap / note |
|---|---|---|---|---|
| 7.2-01 | Store picks approved MR lines | COVERED-PLANNED | WS-274 issue queue **built** (#570); *Issue selected* → store issue SIR-T1-01 (#571) | Issue document itself not built |
| 7.2-02 | System suggests batches FIFO/FEFO | COVERED-PLANNED | SIR-T1-01 pick-suggestion (FEFO expiry-managed else FIFO); MRQ reservation FEFO/FIFO built (`WhRequisitionReservationCoordinator`) | — |
| 7.2-03 | Shows bin location | COVERED-PLANNED | SIR-T1-01 (location per line), SIR-GRD-04 | — |
| 7.2-04 | Issued qty ≤ approved balance | COVERED-PLANNED | SIR-GRD-02; DB CHECK `issued+closed ≤ approved` built (MRQ-GRD-07, V511318) | — |
| 7.2-05 | Issued qty ≤ free stock | COVERED-PLANNED | SIR-GRD-06 (writer, `L-1`), SIR-GRD-04 allocatable status | Negative-stock policy (`V500031`) can allow below zero — confirm BLOCK for stores |
| 7.2-06 | Serial-tracked items: each serial scanned | COVERED-PLANNED | SIR-GRD-04 `SERIAL_REQUIRED`; `wh_store_issue_line_serials`; #571 | Capture yes; "scan" only via web barcode field — no handheld (C9) |
| 7.2-07 | Stock moves Main store → WIP against production order | COVERED-PLANNED | SIR-T4-01 → `VIRT-PRODUCTION-<site>` (SEAM-M1, FR-638/640); #571, #597 | WIP is a **virtual** location (not countable); physical line-side only for `STAGE_BACKFLUSH` |
| 7.2-08 | …or to the consuming department | COVERED-PLANNED | SIR-T4-01 → `VIRT-CONSUMED`, cost object `DEPARTMENT` | — |
| 7.2-09 | Issue slip printed | COVERED-PLANNED | FR-538 `SYS-STORE-ISSUE`; SIR-T2-07; #573 | — |
| 7.2-10 | Receiver acknowledges (name / sign) | PARTIAL | SIR-T1-03 `acknowledged_by_name/at`; SIR-OPEN-02 (signature = optional platform document) | No in-app signature capture; ack is typed by the store clerk, not by the receiver |
| 7.2-11 | …or OTP on app | MISSING | — (SIR §6 "mobile" out of scope) | No OTP, no mobile — CONFLICT C9 |
| 7.2-12 | No direct issue without MR | COVERED-PLANNED | SIR-GRD-03 (setting off + permission) | Setting default must be `false` |
| 7.2-13 | Emergency issue by a permitted user | COVERED-PLANNED | `wh_store_issues:issue_without_requisition` + `direct_issue_allowed` (FR-535); WS-270 tile *Direct issues* | — |
| 7.2-14 | Emergency issue auto-creates the MR for post-approval | MISSING | — | Direct issue creates **no** MR and has no post-facto approval — CONFLICT C2 |

### §7.3 Material Return

| Id | PRD requirement (short) | Status | Evidence | Gap / note |
|---|---|---|---|---|
| 7.3-01 | Reasons: Excess/unused, Wrong issue, Defective in process (line rejection), Scrap, PO closed with balance | PARTIAL | reason context `STORE_RETURN` (FR-536, SIR-GRD-09, `issues/p8-11.md`) | Code list rows not enumerated anywhere; seed these five in #572 |
| 7.3-02 | Fields: return no., production order / MR / issue ref | COVERED-PLANNED | gapless `SRN`; `store_issue_id NOT NULL`, line → issue line; cost object inherited (SIR-T1-05) | MR reached via the issue |
| 7.3-03 | Fields: item, batch, serial, qty | COVERED-PLANNED | `wh_store_return_lines` lot, qty; `wh_store_return_line_serials`; SIR-GRD-07/-08 | — |
| 7.3-04 | Fields: reason, condition (Good / Defective / Scrap) | COVERED-PLANNED | `RETURN_CONDITION` `GOOD`/`NEEDS_INSPECTION`/`DAMAGED`/`SCRAP` (FR-536) | PRD "Defective" = `NEEDS_INSPECTION` or `DAMAGED` — pick one mapping |
| 7.3-05 | Fields: photos | MISSING | — | No attachment on store return |
| 7.3-06 | Flow: raised by production | COVERED-PLANNED | SIR-T1-05/-06 (department create + submit) | — |
| 7.3-07 | → approved by Production Manager | MISSING | — | No department-side approval; Submit is the handover — CONFLICT C3 |
| 7.3-08 | → Store verifies physical qty | PARTIAL | SIR-T1-07 post "after physical receipt" | No verify step and no "received ≠ declared" quantity capture; only post or reject |
| 7.3-09 | → Store Manager approves | PARTIAL | SIR-T1-07 `:post`, receiver ≠ submitter (`STORE_RETURN_SELF_APPROVAL`) | Verify + approve collapsed into one stores action |
| 7.3-10 | → Material inward in store | COVERED-PLANNED | SIR-T4-03 `ISSUE_RETURN` movement at issue unit cost | Irreversible (R31 F-SR-008) |
| 7.3-11 | Good → Main store (free stock) | COVERED-PLANNED | SIR-T4-03/-04 `GOOD` → `AVAILABLE` + putaway | Lands at `RETURNS` staging or issue location then putaway |
| 7.3-12 | Defective → Quarantine for QC decision | COVERED-PLANNED | `NEEDS_INSPECTION` → `QC_HOLD` + `STORE_RETURN` inspection (SIR-T4-05; QC source built #567) | `DAMAGED` condition bypasses QC |
| 7.3-13 | QC decision: use / return to vendor / scrap | PARTIAL | IIS-T4-04 release; scrap disposition | *Raise supplier return* is only for `GOODS_RECEIPT` source (IIS-T1-10) — no RTV from a store-return inspection |
| 7.3-14 | Scrap → Scrap store | PARTIAL | SIR-T4-07: `SCRAP` → status `DAMAGED`, then ordinary scrap movement (approval) | Status-based, no dedicated scrap store/location default |
| 7.3-15 | Defective bought-out part raises vendor rejection linked to original MRN + PO | MISSING | — | No back-link store return → issue lot → GRN/MRN/PO, no vendor rejection document from line rejection |
| 7.3-16 | …feeds vendor rating | PARTIAL | `trade-counterparty-evaluation.contract.md` vendor rating reads receipt + QC facts (FRD-STORES CAT-22) | Line-rejection facts not fed |
| 7.3-17 | Production order consumption reduced by returned qty | COVERED-PLANNED | `onReturnPosted` (SEAM-M2), FR-641, SIR-T4-06; #572, #597 | — |
| 7.3-18 | Actual-vs-BOM variance stays correct | COVERED-PLANNED | FR-643 net (issued − returned); WS-337 consumption variance (#604) | — |

### §8 intro

| Id | PRD requirement (short) | Status | Evidence | Gap / note |
|---|---|---|---|---|
| 8-01 | Every producible item has **one** released component BOM | PARTIAL | BOM-GRD-13 one approved per (item, usage, alternative, site) per date; FR-626 | Design allows several alternatives + site-specific versions (selection rule BOM-T1-13) |
| 8-02 | …and **one** released routing | PARTIAL | FR-631 operation list is **optional** ("routing never mandatory") | CONFLICT C7 |
| 8-03 | Production uses only released revisions | COVERED-PLANNED | PRO-GRD-07 / FR-635 release requires APPROVED + effective BOM; snapshot FR-633; #596 | — |

### §8.1 Component BOM

| Id | PRD requirement (short) | Status | Evidence | Gap / note |
|---|---|---|---|---|
| 8.1-01 | Header: BOM no. | COVERED-PLANNED | `bom_code` (BOM-T1-01); #594 | — |
| 8.1-02 | Header: parent item (FG or sub-assembly) | COVERED-PLANNED | BOM-GRD-01 | — |
| 8.1-03 | Header: revision | COVERED-PLANNED | `version_no`, *New version* BOM-T1-08 | — |
| 8.1-04 | Header: base qty | COVERED-PLANNED | `base_quantity` + UoM | — |
| 8.1-05 | Header: effective from/to | COVERED-PLANNED | `[effective_from, effective_to)` DATE, BOM-GRD-13 | — |
| 8.1-06 | Header: drawing no. + drawing revision | MISSING | not on `whm_boms` (FRD-MFG:195-203); drawing only on trade `wht_customer_item_refs` (DATA-MODEL:1846) | Add to BOM header (and/or item) |
| 8.1-07 | Status Draft→Under review→Released→Obsolete | COVERED-PLANNED | `DRAFT`/`SUBMITTED`/`APPROVED`/`OBSOLETE` (BOM §1.1), Return to DRAFT | Labels differ; map in i18n |
| 8.1-08 | Line: component, qty per base, UoM | COVERED-PLANNED | BOM-GRD-02 | — |
| 8.1-09 | Line: scrap / wastage % | COVERED-PLANNED | `component_scrap_percent` + header `process_loss_percent` | — |
| 8.1-10 | Line: item type (RM / bought-out / sub-assembly) | PARTIAL | derived — item type, procurement `MAKE`/`BUY` (FR-662, #602), presence of a child BOM | No RM vs bought-out classification on the line or item |
| 8.1-11 | Line: issue stage (routing stage that consumes it) | COVERED-PLANNED | `operation_seq` (BOM-GRD-08); #594/#595 | — |
| 8.1-12 | Line: alternate items with priority | COVERED-PLANNED | `whm_bom_line_alternates.priority`, alternate group (BOM-GRD-03/-11) | — |
| 8.1-13 | Line: serial-tracked flag (battery, motor, controller, charger, chassis) | PARTIAL | serial control is an **item** attribute (P1-07 #70 reopened); genealogy FR-648 | Not a BOM-line flag; acceptable if item master is set — confirm with client |
| 8.1-14 | Multi-level: a line can be a sub-assembly with its own BOM | COVERED-PLANNED | FR-627 (depth ≤ 20, cycle check), phantoms; supersedes P6-12 #144 | — |
| 8.1-15 | Exploded and indented views | COVERED-PLANNED | WS-321 explosion tree + table (BOM-T1-14) | — |
| 8.1-16 | Variants: one base BOM + variant overrides (31 configurations) | DECLINED | FRD-MFG **R-09** (`:572`): "variants are separate items with their own BOMs"; BOM §8 | PRD contradicts the decision — CONFLICT C5 |
| 8.1-17 | Change to released BOM ⇒ new revision | COVERED-PLANNED | BOM-UNR-01 immutable; BOM-T1-08 New version; BOM-T4-01 end-dating | — |
| 8.1-18 | ECN document with reason | PARTIAL | `BOM_CHANGE` reason required on new version; FRD-MFG **R-08** declines ECO/change-number master | No ECN entity/number — CONFLICT C5 |
| 8.1-19 | ECN impact: open production orders, stock of old part | MISSING | — (orders keep snapshot, BOM-UNR-03; where-used exists) | No impact analysis / disposition of old-part stock |
| 8.1-20 | ECN approval by Design Head **+** Plant Head | PARTIAL | single checker ≠ submitter (BOM-GRD-07) | Two named approvers not supported |
| 8.1-21 | Where-used report for any component | COVERED-PLANNED | BOM-T1-15 single/recursive; WS-321; #594 | — |

### §8.2 Routing BOM

| Id | PRD requirement (short) | Status | Evidence | Gap / note |
|---|---|---|---|---|
| 8.2-01 | Ordered stages: stage no., operation | COVERED-PLANNED | `whm_bom_operations.operation_seq`, `description` (FR-631); #595 | — |
| 8.2-02 | Work centre | COVERED-PLANNED | `work_centre_id`; WS-322 work centres (FR-630) | — |
| 8.2-03 | Standard time (setup + run per unit) | COVERED-PLANNED | `setup_minutes`, `run_minutes_per_unit` | — |
| 8.2-04 | Operators required | MISSING | — | Not on operation or work centre (`parallel_units` is machines) |
| 8.2-05 | Authorised operator skill | MISSING | — (FRD-MFG R-02: labour/HR out of scope) | Needs skill master + check at confirmation |
| 8.2-06 | QC checkpoint Y/N | COVERED-PLANNED | `is_qc_checkpoint`; in-process QC FR-652 (#599) | — |
| 8.2-07 | …+ checklist | PARTIAL | in-process inspection via `IN_PROCESS` source (FR-652, IIS-GRD-07a) | No per-operation checklist/template link on `whm_bom_operations` |
| 8.2-08 | In-house or job-work (vendor) per stage | PARTIAL | subcontract = whole **order** type `SUBCONTRACT` with own BOM (FR-658, #601) | No external **operation** inside an in-house order (e.g. painting at a vendor mid-route) — CONFLICT C8 |
| 8.2-09 | Materials tagged to stage ⇒ stage-wise issue | PARTIAL | tag = `operation_seq` (8.1-11); *Request materials* takes "selected open components" (MSI-T1-01) | No "issue for stage N" action or MR stage field (7.1-09) |
| 8.2-10 | Routing released/revised like the BOM | COVERED-PLANNED | operations are children of the BOM version (BOM-T1-03/-06) | — |
| 8.2-11 | Routing revision tied to a BOM revision | COVERED-PLANNED | same `whm_boms` row | A routing-only change forces a new BOM version (no independent routing revision) |

### §8.3 Batch-wise production setup

| Id | PRD requirement (short) | Status | Evidence | Gap / note |
|---|---|---|---|---|
| 8.3-01 | Item marked batch-produced | MISSING | — | — |
| 8.3-02 | Standard batch size (e.g. 10 vehicles) | PARTIAL | MRP lot sizing `FIXED` multiples (FR-665, #602/#603) | Planning only; not a production-batch attribute |
| 8.3-03 | Production order split into batches | MISSING | — (`whm_production_orders` has one `planned_lot_code`) | Multiple receipts allowed (FR-644) but no batch entity |
| 8.3-04 | Batch no. follows MR, issue, stages, QC, PDI, FG label | PARTIAL | `planned_lot_code` → FG lot (PRC-GRD-08); genealogy FR-648 | Per-order only; not on MR, issue lines or operation confirmations |

### §8.4 MR against BOM

| Id | PRD requirement (short) | Status | Evidence | Gap / note |
|---|---|---|---|---|
| 8.4-01 | Requirement = BOM qty × order qty × (1 + scrap %) | COVERED-PLANNED | FR-633 snapshot (also process loss, fixed qty); BOM-EC-05; #596 | — |
| 8.4-02 | …× **batch** qty | MISSING | — | No batches (8.3) |
| 8.4-03 | Exploded to the level the store issues at | COVERED-PLANNED | phantoms exploded (FR-633); sub-assemblies via child orders (FR-666) | — |
| 8.4-04 | Per line: required, already issued, returned, balance | COVERED-PLANNED | order component rollups (FR-641); MRQ-T1-23 position; WS-324 | — |
| 8.4-05 | Per line: free stock, shortage | COVERED-PLANNED | release shortage list FR-635; WS-274 `available`/`short` built (#570) | — |
| 8.4-06 | MR for whole order | COVERED-PLANNED | MSI-T1-01 (default all open `ISSUE` lines) | Only `ISSUE` supply-method lines; staged/backflushed lines never get an MR (C1) |
| 8.4-07 | MR per batch | MISSING | — | — |
| 8.4-08 | MR per stage (only that stage's materials) | PARTIAL | component selection in MSI-T1-01 | No stage filter / stage on the MR |
| 8.4-09 | Shortage lines → one-click PR | COVERED-PLANNED | MRQ-T1-11 (built, needs #581 bean); MRP BUY convert FR-666 (#603) | — |
| 8.4-10 | Alternate issued only if on BOM or approved deviation | PARTIAL | FR-642 / MSI-T1-09/-10; second approver only under `STRICT` (MSI-GRD-09) | Under `WARN`/`FLEXIBLE` an ad-hoc substitute is effective without approval |
| 8.4-11 | Variance: actual issue − returns vs BOM standard, per order | COVERED-PLANNED | WS-337 *Consumption variance* (`whm_register_consumption_variance`, #604); MSI-T4-10 | Quantity variance; value residual at close (CST) |
| 8.4-12 | Variance per batch | MISSING | — | No batches |

## CONFLICTS (PRD vs design set)

| # | Topic | PRD | Design set | Evidence |
|---|---|---|---|---|
| C1 | **Everything issued via MR** | "Store issues material only against an approved MR" | Only `ISSUE` supply-method components go through MRQ; `STAGE_BACKFLUSH` moves by staging list (no MR, no approval), `BACKFLUSH` consumed at receipt | MSI §0; FR-638/639/645 |
| C2 | Emergency issue | Permitted user issues; MR **auto-created** for post-approval | Direct issue with setting + permission; no MR, no after-the-fact approval | FR-535; SIR-GRD-03 |
| C3 | Return approval chain | Production raises → **Production Manager approves** → store verifies qty → **Store Manager approves** → inward | Department Submit → stores Post (≠ submitter) or Reject; 2 steps | FR-536; SIR-T1-06/-07 |
| C4 | Who approves a production MR | HOD / Production Manager | MFG-sourced MRQ is submitted/approved by the **stores approver** (`wh_material_requisitions:approve`, Warehouse Manager bundle); manual edit/cancel blocked by MFG guard | FRD-MFG:165; MRQ §2 seeded bundles |
| C5 | Variants and ECN | Base BOM + variant overrides; formal ECN with impact and Design Head + Plant Head approval | **R-09** variants = separate items; **R-08** no ECO; versioning + change reason + one checker | FRD-MFG:571-572; BOM §8 |
| C6 | Over-BOM issue | Reason code **and higher approval** | Policy `STRICT` refuse / `WARN` reason only / `FLEXIBLE` free; no escalation | FR-643; MSI-GRD-06/-07 |
| C7 | Routing mandatory | One released routing per producible item | Operation list optional; "routing never mandatory" | FR-631; MD-09 |
| C8 | Job-work per stage | Each stage in-house or job-work | Subcontract is a whole order of type `SUBCONTRACT` | FR-658; #601 |
| C9 | Mobile / OTP | Receiver ack by OTP on app; serial scan | MRQ/SIR §6 "mobile" out of scope; MFG **R-13** no shop-floor mobile — while **D-13** says "Mobile is not optional" (internal design-set contradiction too) | DECISIONS.md:295; FRD-MFG:576; SIR §6 |
| C10 | Where returns land | Separate Quarantine store and Scrap store | Status-based (`QC_HOLD`, `DAMAGED`) at the return location; `DAMAGED` condition skips QC | FR-537; SIR-T4-03/-07 |
| C11 | Alternate needs approved deviation | Always | Approval only under `STRICT` | MSI-T1-10 |
| C12 | One BOM per item | One released | Alternatives by lot size + site-specific versions | FR-626 |

## BEYOND-PRD

**Design covers, PRD omits (worth telling the client):**
- Stock reservation at MR approval (`NONE`/`SOFT`/`HARD`, top-up job), value-threshold second approval, department-scoped visibility, recall, stale/overdue alerts (MRQ-T3-*).
- Cost object on every issue line (department / cost centre / machine / project / production order) + cost-centre master; consumption by department register; stores KPIs (SIR §5.4, #574).
- Posted issue immutable; correction = return + new issue (STO-D11); return window; return valued at issue cost.
- Pick-to-line staging and backflush (three supply methods), line-side locations, consumption policy with tolerance %.
- Phantom BOMs, co-/by-products with cost share, fixed (setup) quantities, process loss, lot-size-based alternatives, BOM cost roll-up, *Copy from kit*.
- Rework orders from QC disposition, actual costing with settlement at close, bonded/MOOWR issue to production (india).

**Industry gaps (neither PRD nor design set):**
- **BOM bulk import** (Excel/CAD/PLM) — no import on WS-320; 31 configurations × multi-level makes manual entry impractical.
- **BOM revision compare** (diff v1 vs v2) and **mass replace** of a component via where-used.
- **ECN impact workflow** (open orders, WIP, stock of old part — use-up / scrap / rework decision, effectivity by serial/VIN).
- **Domestic value addition (DVA) / localisation by BOM** for EV incentive schemes (PM E-DRIVE / PLI phased manufacturing) — needs BOM lines tagged imported vs domestic with value.
- **EV battery traceability**: battery/motor/controller serials married to chassis/VIN, needed for warranty, recall and Battery Waste Management Rules EPR; genealogy exists (FR-648) but no VIN-level report.
- Tool/jig issue on returnable basis (tool crib — explicitly out, SIR §6), MR budget control per cost centre, WIP physical verification, scrap sale/disposal with GST invoicing.

## QUESTIONNAIRE

| Q | Question | Answered by design assumption? | Where |
|---|---|---|---|
| Q-M1 | Who raises / approves MRs | **Yes** — requester in own department; approver any `:approve` holder or department head/deputy (setting), maker≠checker; optional 2nd level above a value (OD-29 DEFAULT, R31). MFG MRs approved by stores approver | MRQ-GRD-01/-05, MRQ-OPEN-01, FRD-MFG:165 |
| Q-M2 | Emergency issue without MR | **Yes** — setting + permission, no auto MR | FR-535, SIR-GRD-03 |
| Q-M3 | FIFO / FEFO / store chooses | **Yes** — FEFO for expiry-managed, else FIFO, as a suggestion the clerk may override | SIR-T1-01, MRQ-T4-01 |
| Q-M4 | Issue per order / batch / stage | **Partly** — whole order or selected components; per-batch not modelled | MSI-T1-01 |
| Q-M5 | Who approves a return; where defective goes | **Yes** — stores posts (≠ submitter); `NEEDS_INSPECTION` → `QC_HOLD` + inspection, `DAMAGED`/`SCRAP` → `DAMAGED` | SIR-T1-07, FR-537 |
| Q-M6 | Excess issue over BOM allowed / approval | **Yes** — consumption policy `STRICT`/`WARN`/`FLEXIBLE` + tolerance %; no higher approval | FR-643 |
| Q-B1 | Models/variants; sample BOM | **Yes (contradicted)** — R-09: each variant a separate item + BOM | FRD-MFG:572 |
| Q-B2 | BOM levels; in-house sub-assemblies | **Partly** — depth ≤ 20; MAKE/BUY per item × site | FR-627, FR-662 |
| Q-B3 | Stages, work centres, std time | **No** (data) — structure exists, optional | FR-630/631 |
| Q-B4 | Which stages are job-work | **Partly** — only whole-order subcontract | FR-658 |
| Q-B5 | Scrap/wastage % known | **No** (data) — fields exist (component scrap %, process loss %) | FR-622/623 |
| Q-B6 | Who creates/releases BOM; ECN needed | **Yes (contradicted)** — production engineer makes, engineering approver checks; R-08 no ECN | BOM §2, FRD-MFG:571 |
