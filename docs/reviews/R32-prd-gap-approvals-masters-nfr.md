# Gap analysis — slice "approvals-masters-nfr"

PRD (`prd.txt`) lines 1–134 (§1 overview / goals / users / fit, §2 flow, §3 approvals + approval table, §4 masters) and 422–435 (§13.2 data model, §13.3 non-functional, §13.4 phasing). Questionnaire Q-G1…G6, Q-A1…A4.
Compared against `warehouse-issues/docs` (FR, FRD-STORES/TRADE/MFG/REM, contracts, DECISIONS D-16/D-17/D-18, DATA-MODEL) and the 630-issue corpus. Built-code spot checks in `classic/warehouse-base|warehouse`.

Key context: D-16 (2026-10-22) re-targets warehouse to manufacturing + storage, splits **warehouse-trade** (P9, `wht_`) and **warehouse-manufacturing** (P10, `whm_`) — neither has code yet. D-16 item 6 fences dealer/services/automotive (not edited) and **defers accounting**; D-16 item 7 + D-17 (b) = **no mobile app in v1**.

## Summary counts

| Status | Count |
|---|---|
| COVERED-BUILT | 42 |
| COVERED-PLANNED | 37 |
| DESIGN-ONLY | 0 |
| PARTIAL | 60 |
| DECLINED | 7 |
| OTHER-MODULE | 4 |
| MISSING | 18 |
| **Total atomic requirements** | **168** (§1 30, §2 8, §3 39, §4 49, §13.2 26, §13.3 12, §13.4 4) |

DECLINED counts 1-11 (PRD declines MRP, design builds it), so it is also a CONFLICT.

CONFLICT flags (design says something different from PRD) are marked **[C]** in the Gap column and listed in §CONFLICTS (19).

## Matrix

### §1 Overview, goals, users, fit

| Id | PRD requirement (short) | Status | Evidence | Gap / note |
|---|---|---|---|---|
| 1-01 | One system carries a vehicle from material requirement to the sales invoice | PARTIAL | D-16 items 5–6; FRD-TRADE §11 R2 (`frd/FRD-TRADE.md:640`) | Invoice / payment refused to accounting, which is deferred (D-16 item 6). **[C]** |
| 1-02 | Every document moves only when an approved user acts on it | COVERED-PLANNED | FR-408; maker-checker in every contract (MRA-GRD-03, MRQ-GRD-05, GTE-T1-11, BOM-GRD-07, PRO-GRD-09, TAM-GRD-03); #146 (P2-23, open/reopened) | Built for gate pass, MR, adjustments, counts, reversals; planned for MRN #569, issue #571, trade #580, MFG #594/#596 |
| 1-03 | Goal chain PR→PO→Gate→IQC→MRN→Store→MR→Issue→Production→PQC→PDI→Invoice→Payment | PARTIAL | PR #581, PO #584, Gate #564 (built), IQC #566/#567 (built), MRN #569, MR #570 (built), Issue #571, Prod #596–#598, PQC #599 | PDI = generic final QC only (no PDI doc); Invoice + Payment refused (FRD-TRADE R2) **[C]** |
| 1-04 | Production driven by SO, built against approved BOM + routing, batch-wise and stage-wise | PARTIAL | FR-637 MTO link, FR-626 approved BOM selection, FR-631 optional operations, FR-651 confirmations; #596, #599 | Routing optional and not separately released; no "batch" entity (lot per receipt); SO does not auto-raise a production order (manual or MRP convert) **[C]** |
| 1-05 | No stock movement without a document | COVERED-BUILT | D-4, L-1/L-2 single ledger writer; `whb_document_types` registry (P0 epic #3) | — |
| 1-06 | No document without an approved user | COVERED-PLANNED | same as 1-02 | — |
| 1-07 | Samples and drawings handled against the SO, drawing approval before any sample is built | MISSING | only `wht_customer_item_refs` drawing no. + revision (FR-545, #579) | No drawing master, drawing revision approval, sample order, sample iteration, sample store or sample dispatch anywhere in design or issues |
| 1-08 | Serial and batch traceability feeds the existing Warranty & Service registry | PARTIAL | lots/serials #13, #70 (P1-07 genealogy, open/reopened); `whm_production_receipt_output_serials` (#598) | Feed to the services product registry is MISSING: D-16 item 6 fences `services` from edits **[C]** |
| 1-09 | Out of scope v1: direct filing on government portals (system prepares data/upload files) | PARTIAL | warehouse-india e-way bill + compliance API logs (#328, #437) | Design already calls the e-way-bill API directly — beyond PRD's "prepare files" line. GST returns themselves are accounting **[C]** |
| 1-10 | Out of scope v1: payroll | DECLINED | not in any warehouse doc | Consistent |
| 1-11 | Out of scope v1: MRP auto-planning across many SOs | DECLINED (PRD) | design builds it: FR-662…FR-668, #602, #603 (P10-11/12) | Design goes beyond PRD — tell the client MRP is planned; or descope **[C]** |
| 1-12 | Out of scope v1: vendor portal logins | DECLINED | `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md:1133` (out-of-scope row 22) | Consistent |
| 1-13 | Role: Purchase Executive / Manager — PR review, RFQ, PO, vendor follow-up | COVERED-PLANNED | FRD-TRADE actors; #581, #582, #584, #587 | — |
| 1-14 | Role: Security / Gate — gate entry in and out | COVERED-BUILT | #564 (P8-03, closed), gate-entry contract | — |
| 1-15 | Role: Store Keeper / Manager — inward, MRN, issue, returns, store inward | PARTIAL | #570 built; #569, #571, #572 open | MRN / issue / return still planned |
| 1-16 | Role: QC Inspector / Manager — IQC, PQC, PDI, rejection notes | PARTIAL | `FRD-STORES.md:96`, `FRD-MFG.md:83`; #567 built, #568, #599 open | No separate QC-Manager approval of results; no PDI; no "rejection note" document (supplier return #568 instead) |
| 1-17 | Role: Production Planner / Supervisor — PO, job cards, stage booking | COVERED-PLANNED | `FRD-MFG.md:81`; #596, #599 | "Job card" = traveller (FR-636) + operation confirmation (FR-651) |
| 1-18 | Role: Design / R&D Engineer — BOM, routing, drawings, samples | PARTIAL | BOM #594, operations #595 | Drawings + samples MISSING |
| 1-19 | Role: Plant Head — approvals above limits, BOM and drawing release | PARTIAL | trade matrix levels #580 (WH-SC-489 L2 `PLANT_HEAD`) | BOM approval is single-level (BOM-GRD-07); drawing release MISSING |
| 1-20 | Role: Sales / Dispatch / Billing — SO, sample request, dispatch, sales invoice | PARTIAL | SO #586, despatch (outbound-despatch contract, built P2) | Sample request MISSING; sales invoice refused (accounting) |
| 1-21 | Role: Management Viewer — reports only | COVERED-BUILT | auditor bundle `:view` only (TAM-T2-07; AUDITOR role) | Trade auditor bundle planned with #578 |
| 1-22 | Fit: reuse the existing item master (categories, units, GST) | PARTIAL | `whb_items` (DATA-MODEL:802) built #13 | Warehouse owns its own item master; HSN only (`tax_classification_code`), no GST rate **[C]** |
| 1-23 | Fit: reuse company profile | OTHER-MODULE | platform `companies` | — |
| 1-24 | Fit: reuse multi-tenant RLS | PARTIAL | access-scope contract; #137 (P1-18 site scope in WHERE) | No PostgreSQL RLS anywhere in the codebase (grep: 0); isolation is app-level company/site scope **[C]** |
| 1-25 | Fit: reuse roles and data scope | COVERED-BUILT | platform roles + `wh_*:view:all/branch` scopes (#137, #145) | — |
| 1-26 | Fit: reuse `audit_log` | PARTIAL | `whb_audit_events` own, hash-chained (DATA-MODEL:1254) | Separate trail from platform audit_log **[C]** |
| 1-27 | Fit: reuse the approval pattern quotations use | PARTIAL | trade approval matrix engine (TAM, #580) | New engine, not the CRM quotation pattern; core docs use per-document approve verbs **[C]** |
| 1-28 | Fit: reuse PDF printing | COVERED-BUILT | P2-14 #100, P3-08 #41 print framework; stores prints #573 (open) | Warehouse uses its own template renderer |
| 1-29 | Fit: reuse service product registry for serials | MISSING | D-16 item 6 scope fence | See 1-08 |
| 1-30 | New tables carry `org_id` like every tenant table | PARTIAL | `company_id` + `warehouse_id` convention | Naming / mechanism differ (no org_id, no RLS) **[C]** |

### §2 End-to-end flow

| Id | PRD requirement (short) | Status | Evidence | Gap / note |
|---|---|---|---|---|
| 2-01 | Approved SO is the trigger; it raises the Production Order | PARTIAL | FR-637, FR-632 demand link; MRP convert FR-666 (#603) | No automatic SO-approval → production order; order created manually from demand line or via MRP **[C]** |
| 2-02 | Production Order's BOM drives the material requisition | COVERED-PLANNED | #597 (P10-06 staging / issue through core MR), MR cost object = production order (#570 built) | — |
| 2-03 | Free stock goes straight to issue | COVERED-PLANNED | MRQ reservation + store issue #571 | — |
| 2-04 | Shortage runs through purchase and inward | COVERED-PLANNED | FR-557 "Send to purchasing" handoff (#581); P8-16 #577 (built) | Trade side open |
| 2-05 | MRN puts accepted stock in the Main store | COVERED-PLANNED | FR-527, mrn-authorisation contract, #569 | MRN optional per site (`warehouse.stores.mrn_required`, OD-26) |
| 2-06 | IQC rejects go back to the vendor (§6) | COVERED-PLANNED | #568 (manual "Raise supplier return"), FR-139 amended | Manual, never automatic |
| 2-07 | PQC and PDI failures go to rework | PARTIAL | FR-653 REWORK disposition (#599) | PDI not a distinct stage |
| 2-08 | Every box (20 documents) is a document only an approved user can approve | PARTIAL | see §3 table rows | Drawings, samples, PDI, enquiry feasibility have no document |

### §3 Approved users and approvals

| Id | PRD requirement (short) | Status | Evidence | Gap / note |
|---|---|---|---|---|
| 3-01 | Permission per action, not per screen (`pr:create`, `po:approve`, `iqc:inspect`, `mrn:approve`, `issue:post`, `bom:release`, `drawing:approve`, `prodorder:release`, `pdi:approve`…) | PARTIAL | `resource:verb` per action: `wht_purchase_requisitions:approve`, `wh_material_receipt_notes:authorise`, `whm_boms:approve`, `whm_production_orders:approve_release`, `wh_quality_inspections:*` (TAM §0.1, contracts T2) | `drawing:approve`, `pdi:approve` have no resource; names differ from PRD's |
| 3-02 | Roles bundle permissions; Admin → Roles edits them | COVERED-BUILT | platform roles; seeds via `permission_dependencies` (#145) | — |
| 3-03 | Maker ≠ checker, enforced in the service, not UI | COVERED-PLANNED | FR-408; `<DOC>_SELF_APPROVAL` 403 (MD-21); TAM-UNR-04 (even ADMIN) | Built on gate pass, MR, counts, adjustments; rest planned |
| 3-04 | Value limits per approver per document type; above limit routes to next level (PM → PH → MD) | PARTIAL | TAM-GRD-01 bands per rule; WH-SC-489 | Trade docs only; limit is on the **rule band**, not per approver **[C]** |
| 3-05 | Limit used is recorded on the approval | PARTIAL | request freezes rule id, value, level snapshot (TAM-T1-03) | No per-approver "limit used" column |
| 3-06 | Multi-level matrix configurable per doc type, value band, item category, plant/store | PARTIAL | FR-548 (doc type × site × department × category × currency × value/qty band), #580 | Trade documents only. Core docs (MRN, MR, issue, return, gate pass, BOM, production order, QC) are single-step; core value-banded `wh_approval_levels` (FR-466, v2) never built — #160 closed DUPLICATE **[C]** |
| 3-07 | Approved status locks the document | COVERED-PLANNED | TAM-UNR-03, FR-553; BOM immutable FR-625 | — |
| 3-08 | Change after approval = amendment (new revision + re-approval), never edit in place | COVERED-PLANNED | FR-590…FR-593, #588 (PO/SO); BOM new version FR-625 | Only PO/SO/rate contracts/BOM; MR / MRN / production order have cancel, not amend |
| 3-09 | Revision history kept | COVERED-PLANNED | `wht_*_versions` tables, FR-593 compare + reprint | — |
| 3-10 | Reason mandatory on reject | COVERED-PLANNED | FR-551, TAM-T1-07; MRA-T1-04 `rejection_note` | — |
| 3-11 | Reason mandatory on cancel | COVERED-PLANNED | `TRADE_ORDER_CLOSE` reason codes (FR-546); PRO `cancel_reason_code_id` | — |
| 3-12 | Reason mandatory on short-close | COVERED-PLANNED | FR-546; GTE-T1-16 close short | — |
| 3-13 | Reason mandatory on amendment | COVERED-PLANNED | #588 | — |
| 3-14 | Reason mandatory on deviation | PARTIAL | `PRODUCTION_DEVIATION` reason (WH-SC-624, #593) | Only consumption deviation; no IQC deviation / concession |
| 3-15 | Reason mandatory on override | COVERED-BUILT | lot-verdict override reason FR-524 (#566); period override reason MPR-GRD-10 | — |
| 3-16 | PO only to an approved vendor for that item (AVL) | PARTIAL | FR-544, `warehouse.trade.avl.enforcement` default REFUSE, #579 | Enforced **only when the item has any AVL row**; an item with no AVL row can be ordered from anyone **[C]** |
| 3-17 | Production only on released BOM + routing | COVERED-PLANNED | FR-626, MD-19 `409 BOM_NOT_EFFECTIVE`, #596 | Routing has no own release |
| 3-18 | Sample built only from an approved drawing revision | MISSING | — | — |
| 3-19 | Authorised operators per routing stage (skill/operator master) | MISSING | FR-651 records `operator` only | No authorisation list; any holder of the confirm permission books any operation |
| 3-20 | QC stages list authorised inspectors | MISSING | `inspector_id` on inspection; MRN_AUTHORISER_IS_INSPECTOR is separation only | — |
| 3-21 | Audit every create/approve/reject/post/amend/print with before/after, user, time | PARTIAL | `whb_audit_events` (actor, on-behalf-of, summary, hash) | No structured before/after columns; print events not stated as audited |
| 3-22 | Approvals are append-only | PARTIAL | audit events append-only + hash chain (L-2, DATA-MODEL:147) | `wht_approval_steps` rows are updated in place (status) — not append-only at DB level **[C]** |
| 3-23 | In-app notification to next approver | COVERED-PLANNED | TAM-T4-03, FRD-TRADE §12b | — |
| 3-24 | Email notification where configured | DECLINED | `FRD-TRADE.md:738` "v1 sends in-app only"; TAM §6 approval by e-mail link not built | **[C]** vs PRD |
| 3-25 | Overdue approvals escalate after configurable hours | PARTIAL | TAM-T3-01 `warehouse.approval.pending_alert_hours` (24) alerts the **same** level; P2-23 alerts (#146) | Alert, no escalation to a higher level; #620 open (notifier swallows failures) **[C]** |
| 3-26 | Common statuses Draft → Submitted → Approved (L1…Ln) → Released/Posted → Closed | PARTIAL | per-document ladders in each contract | Each document has its own ladder; no common status vocabulary |
| 3-27 | Rejected goes back to Draft for revision | PARTIAL | FR-551: reject → `REJECTED` (editable, resubmittable); *return* → `DRAFT` | Design adds Return + Withdraw; Rejected is its own state **[C]** |
| 3-28 | Cancelled with reason | COVERED-PLANNED | see 3-11 | — |
| 3-29 | Table: PR — any dept user creates; HOD, then Purchase; optional value | PARTIAL | FR-556, FR-558 (matrix on Σ qty × est. rate), #581 | No dynamic "HOD of the PR's department" level (MR has `DEPARTMENT_HEAD`, PR has none) |
| 3-30 | Table: PO — Purchase Exec; PM → Plant Head → MD; value-based | COVERED-PLANNED | FR-548, WH-SC-489, #580, #584 | — |
| 3-31 | Table: IQC result / deviation — QC Inspector; QC Manager (deviation: Plant Head) | PARTIAL | #567 built; MPR-GRD-27 approval only for a PENDING disposition movement (scrap) | No QC-Manager approval of a result; no deviation/concession document; lot-verdict override is by the inspector himself (FR-524) **[C]** |
| 3-32 | Table: MRN — Store Keeper; Store Manager | COVERED-PLANNED | MRA-GRD-03, #569 | — |
| 3-33 | Table: Material Requisition — production/department; HOD / Production Manager | COVERED-BUILT | MRQ-GRD-05 `DEPARTMENT_HEAD` policy, second approver; #570 closed | Follow-ups open #623, #624, #634 |
| 3-34 | Table: Material Return — Production; Production Manager + Store Manager | PARTIAL | SIR-T1-07 store posts, receiver ≠ submitter; #572 | No Production-Manager approval step |
| 3-35 | Table: BOM / Routing release — Design Engineer; Design Head + Plant Head | PARTIAL | FR-625 single approver, #594 | Two-level release not supported **[C]** |
| 3-36 | Table: Drawing release — Design Engineer; Design Head (customer approval for SO samples) | MISSING | FR-545 records customer part approval only | — |
| 3-37 | Table: Production Order — Planner; Production Manager | COVERED-PLANNED | PRO-GRD-09 release approval (when configured), #596 | — |
| 3-38 | Table: PDI clearance — QC Inspector; QC Manager | PARTIAL | final QC FR-652 (#599) | No PDI checklist per model, no QC-Manager clearance step |
| 3-39 | Table: Sample dispatch — Sales / R&D; Sales Manager | MISSING | — | — |

### §4 Masters

| Id | PRD requirement (short) | Status | Evidence | Gap / note |
|---|---|---|---|---|
| 4-01 | Masters retired, never deleted; changes audited | COVERED-BUILT | `is_active`, `lifecycle_status`; `whb_audit_events`; P1-21 merge #148 | — |
| 4-02 | Item: code, name | COVERED-BUILT | `whb_items.code` (system surrogate) + `sku`, `name` (#13) | Code is system-generated, user key is SKU |
| 4-03 | Item: category | COVERED-BUILT | `whb_item_category_assignments` (#13) | — |
| 4-04 | Item: item type RM / Bought-out / Sub-assembly / FG / Consumable / Sample | PARTIAL | FR-049 registry `whb_item_types` | Seeds are STOCK/NON_STOCK/SERVICE/KIT/CONSUMABLE/PACKAGING…; no RM/BO/SA/FG/SAMPLE seeds |
| 4-05 | Item type drives which flows apply | PARTIAL | type flags `is_stocked`, `is_serial_default`… (DATA-MODEL:487); make/buy FR-662 | No rule "type X ⇒ flow Y" |
| 4-06 | Item: UoM + purchase UoM + conversion | COVERED-BUILT | `base_uom_code`, `purchase_uom_code`, `whb_item_uom_conversions` (#13, #20) | — |
| 4-07 | Item: HSN | COVERED-BUILT | `tax_classification_code` | — |
| 4-08 | Item: GST rate | OTHER-MODULE | `INDIA-LOCALISATION-PACK.md:1365` (GST-rate engine is an open decision; accounting owns tax) | No GST rate on the warehouse item **[C]** |
| 4-09 | Item: make/buy | COVERED-PLANNED | FR-662 `WHM_PROCUREMENT_TYPE` per item × site, #602 | Per site, not on the item |
| 4-10 | Item: batch-tracked | COVERED-BUILT | `lot_control_mode` | — |
| 4-11 | Item: serial-tracked | COVERED-BUILT | `serial_control_mode` | — |
| 4-12 | Item: shelf life | COVERED-BUILT | `shelf_life_days` + receipt/ship % (FR-069) | — |
| 4-13 | Item: QC required (Y/N) | COVERED-BUILT | inspection plan assignments with `no_inspection` (FR-521, #566); OD-38 | Resolved per item / category / supplier, not a flag |
| 4-14 | Item: reorder level, min/max | COVERED-BUILT | `whb_item_site_settings` reorder_point / min / max (P1-03 #33 reopened) | Per item × site |
| 4-15 | Item: lead time | COVERED-BUILT | `whb_item_site_settings.lead_time_days`; supplier lead time FR-542 | — |
| 4-16 | Item: default store | PARTIAL | putaway rules (#126), BOM line default supply location (FR-623), `default_receipt_status_code` | No "default store" field on the item |
| 4-17 | Vendor: code, name | COVERED-BUILT | `whb_counterparties` (#78) + SUPPLIER role link | — |
| 4-18 | Vendor: GSTIN | COVERED-BUILT | `whb_counterparty_tax_registrations` per state | — |
| 4-19 | Vendor: PAN | COVERED-BUILT | `national_tax_id` | — |
| 4-20 | Vendor: address | COVERED-BUILT | `whb_counterparty_addresses` | — |
| 4-21 | Vendor: contacts | MISSING | P1-08 #78 states "no contacts"; `wht_supplier_profiles` "no contact" (DATA-MODEL:1843) | No contact person / phone / email anywhere |
| 4-22 | Vendor: payment terms | COVERED-PLANNED | FR-542 (recorded only), #579 | MSME 45-day warning included |
| 4-23 | Vendor: approved items | COVERED-PLANNED | AVL FR-544, #579 | — |
| 4-24 | Vendor: approved make | MISSING | AVL is item × supplier only; manufacturer part no. alias FR-059 | No make/manufacturer dimension on AVL |
| 4-25 | Vendor: rating | COVERED-PLANNED | #589 (P9-12) | — |
| 4-26 | Only approved vendor-item pairs can be ordered | PARTIAL | see 3-16 | — |
| 4-27 | Plant | PARTIAL | site = `whb_warehouses`, branch link (facility-branch-link contract) | No separate "plant" over several stores; a plant is a site (zones inside) or several sites on one branch |
| 4-28 | Store types Main, Quarantine/QC Hold, Rejected, WIP, FG, Scrap, Sample | PARTIAL | stock statuses QC_HOLD/QUARANTINE/REJECTED; VIRT-PRODUCTION, VIRT-SCRAP; line-side locations | Modelled as status/virtual locations, not stores; no Sample store **[C]** |
| 4-29 | Quarantine and Rejected are separate, non-issuable stores | COVERED-BUILT | statuses non-allocatable (`is_allocatable=false`), P1-14 `V500058` REJECTED | Status, not store — equivalent behaviour |
| 4-30 | Bin / rack | COVERED-BUILT | `whb_locations` hierarchy, generator (#54, #60) | — |
| 4-31 | Work centre: code, name | COVERED-PLANNED | FR-630, WS-322, #595 | — |
| 4-32 | Work centre: capacity per shift | PARTIAL | FR-630 available minutes/day, efficiency, parallel units | No shift calendar; infinite capacity (FR-668) |
| 4-33 | Work centre: cost per hour | PARTIAL | FR-630 rate "recorded for reporting only" (OD-43) | Not used in costing |
| 4-34 | Machine master (used by routing) | MISSING | work centre `parallel units` only | — |
| 4-35 | Operation / Stage master: code, name (welding, painting, wiring, assembly, testing) | PARTIAL | `whm_bom_operations` per BOM (description, seq) #595 | No reusable operation master with code |
| 4-36 | Operation: QC checkpoint Y/N | COVERED-PLANNED | `is_qc_checkpoint` FR-631 | — |
| 4-37 | Operator / Skill master: user, stages authorised, shift | MISSING | — | — |
| 4-38 | Only authorised operators book a stage | MISSING | see 3-19 | — |
| 4-39 | QC parameter: parameter, spec min/max | COVERED-BUILT | `wh_inspection_plan_criteria` (criterion, value_type, min, max, expected_text) #120 | — |
| 4-40 | QC parameter: target value; pass/fail | PARTIAL | pass/fail via `value_boolean`/`is_pass` | No target column |
| 4-41 | QC parameter: method, instrument | MISSING | `wh_weighing_instruments` is legal-metrology only (FR-223, v2) | No method / gauge fields on criteria |
| 4-42 | QC sampling plan (AQL) | COVERED-BUILT | FR-521…524, #566; Z1.4 seed #610 open | — |
| 4-43 | Checklist linked per item (IQC) | COVERED-BUILT | plan assignments item/category/supplier (#566) | — |
| 4-44 | Checklist linked per stage (PQC) | PARTIAL | in-process QC at checkpoint ops (FR-652, #599) | Assignment scopes are item/category/supplier — no per-operation plan |
| 4-45 | Checklist linked per FG model (PDI) | PARTIAL | final QC plan per FG item | No PDI checklist concept |
| 4-46 | Reason codes: rejection, return, scrap | COVERED-BUILT | `whb_reason_codes` contexts; STO-D24 | #621 open (label collisions) |
| 4-47 | Reason codes: deviation, cancellation, short-close | COVERED-PLANNED | `PRODUCTION_DEVIATION` (#593), `TRADE_ORDER_CLOSE` (#579) | — |
| 4-48 | Approval matrix master: doc type, value band, category, levels, approver roles | PARTIAL | WS-284, `wht_approval_rules/levels` (#580) | Trade only (see 3-06) |
| 4-49 | Number series per doc type, per plant, per FY (PO/26-27/00001) | COVERED-BUILT | `whb_number_series` `{FY}` token, YEARLY reset on 1 April (`WhbNumberSeries.java:60`, `WhbNumberSeriesValidationService.java:38`), #84 | Trade numbers are non-gapless (FR-547) |

### §13.2 Data model (table list vs design set)

| Id | PRD table(s) | Status | Design equivalent | Gap / note |
|---|---|---|---|---|
| 13.2-01 | vendors, vendor_items | COVERED-PLANNED | `whb_counterparties` (+roles, addresses, tax regs) built; `wht_supplier_profiles`, `wht_approved_vendor_items`, `whb_item_supplier_sources` | — |
| 13.2-02 | stores, bins | COVERED-BUILT | `whb_warehouses`, `whb_locations` | — |
| 13.2-03 | purchase_requisitions(+_lines), rfqs | COVERED-PLANNED | `wht_purchase_requisitions`, `wht_rfqs` (#581, #582) | — |
| 13.2-04 | purchase_orders(+_lines, +_schedules, +_revisions) | COVERED-PLANNED | core `wh_purchase_orders` + schedule lines (#562 built) + `wht_purchase_order_versions`, `wht_po_amendments` (#584, #588) | — |
| 13.2-05 | gate_entries, grns(+_lines) | COVERED-BUILT | `wh_gate_entries` (#564), `wh_goods_receipts` (#113); bill block #565 open | — |
| 13.2-06 | qc_checklists, qc_parameters, qc_inspections(+_results) | COVERED-BUILT | `wh_inspection_plans`, `_criteria`, `wh_quality_inspections`, `_results` | — |
| 13.2-07 | ncrs | MISSING | supplier claims / supplier returns exist, no NCR record | — |
| 13.2-08 | deviations | MISSING | — | — |
| 13.2-09 | mrns(+_lines) | COVERED-PLANNED | `wh_material_receipt_notes` (#569) | — |
| 13.2-10 | stock_ledger (append-only), stock_balances, stock_serials | COVERED-BUILT | `whb_stock_movements/_lines`, `whb_stock_positions`, `whb_serials` | — |
| 13.2-11 | material_requisitions, material_issues, material_returns (+_lines) | PARTIAL | `wh_material_requisitions` built #570; `wh_store_issues` #571, `wh_store_returns` #572 open | — |
| 13.2-12 | boms(+_lines, +_variants) | COVERED-PLANNED | `whm_boms`, `_lines`, `_line_alternates`, `_outputs` (#594) | "variants" = alternatives |
| 13.2-13 | routings(+_stages) | PARTIAL | `whm_bom_operations` (#595) | Routing-lite inside the BOM |
| 13.2-14 | ecns | DECLINED | FRD-MFG R-08 (`FRD-MFG.md:571`): versioning + effectivity + change reason instead | PRD Phase 4 lists ECN **[C]** |
| 13.2-15 | drawings(+_revisions) | MISSING | — | — |
| 13.2-16 | enquiries, feasibility_reviews | PARTIAL | `wht_sales_enquiries` (#585) | No feasibility review |
| 13.2-17 | sales_orders(+_lines, +_revisions) | COVERED-PLANNED | `wht_sales_orders`, `_versions`, `wht_so_amendments` (#586, #588) | — |
| 13.2-18 | production_orders, production_batches | PARTIAL | `whm_production_orders` (#596), receipts `whm_production_receipts` (#598) | No batch entity |
| 13.2-19 | job_cards, stage_bookings | PARTIAL | traveller FR-636, `whm_production_order_operations`, `whm_operation_confirmations` (#599) | No job card document |
| 13.2-20 | unit_serial_bindings | PARTIAL | genealogy `whb_transformations` (#70 open), `whm_production_receipt_output_serials` | Chassis ↔ part-serial binding at assembly not specified |
| 13.2-21 | samples(+_iterations) | MISSING | — | — |
| 13.2-22 | dispatches | COVERED-BUILT | core shipments / outbound-despatch contract; SO dispatch planning #586 | — |
| 13.2-23 | sales_invoices(+_lines) | DECLINED | FRD-TRADE §11 R2 → accounting | — |
| 13.2-24 | approvals (append-only) | PARTIAL | `wht_approval_requests/_steps` (#580) | Trade only; not append-only (3-22) |
| 13.2-25 | document_number_series | COVERED-BUILT | `whb_number_series` + `_issued` (#84) | — |
| 13.2-26 | accounts tables (account_groups, ledgers, cost_centres, periods, vouchers by type, bill_allocations, bank_statements, tds/tcs/gst entries, statutory_challans, fixed_assets, depreciation_runs, budgets, compliance_calendar) | OTHER-MODULE | `accounting-issues` design (chart, ledgers, bank reco, fixed assets, depreciation, budgets present) | Light check: TCS and compliance calendar return 0 hits in `ACCOUNTING-FUNCTIONAL-REQUIREMENTS.md` — flag to the accounting slice |

### §13.3 Non-functional

| Id | PRD requirement (short) | Status | Evidence | Gap / note |
|---|---|---|---|---|
| 13.3-01 | Multi-tenant, multi-plant | COVERED-BUILT | company + site scope (#137); multi-site everywhere | No RLS (1-24) |
| 13.3-02 | Every document number per plant per FY | COVERED-BUILT | #84 (`{FY}`, per warehouse) | Trade numbering per company, optionally per site (FR-547) |
| 13.3-03 | Stock ledger append-only at DB level | COVERED-BUILT | L-2 three layers incl. trigger (`DECISIONS.md:807`) | — |
| 13.3-04 | Approvals append-only at DB level | PARTIAL | see 3-22 | **[C]** |
| 13.3-05 | Stock never negative (DB check) | PARTIAL | `chk_whb_stock_positions_available_nonneg` (I-6) | `negative_stock_mode` BLOCK/WARN/**ALLOW** per item × site (`whb_negative_stock_policies`) lets an install allow negative on-hand **[C]** |
| 13.3-06 | Android app: gate entry, GRN scan, IQC, issue scan, shop-floor booking, PDI | DECLINED | D-16 item 7, D-17 (b): 12 mobile FRs DEFERRED post-v1 | **[C]** direct contradiction |
| 13.3-07 | Barcode/QR labels for items, batches, serials, job cards | PARTIAL | `ITEM_LABEL`, `LOCATION_LABEL`, `LPN_LABEL`, `QR_CODE` seeded (P2-14 #100, #310–#313); traveller barcode FR-636 | No lot/batch or serial label kind |
| 13.3-08 | Response < 2 s for lists of 1,000 rows | COVERED-BUILT | `NonFunctionalFoundationsTest` PerformanceTargets: ledger/position grids p95 < 2,000 ms (measured 111–1,403 ms) | Proven for ledger/position grids only; first page, not 1,000 rows |
| 13.3-09 | IST time zone | COVERED-BUILT | FR-439 per-site timezone (validated vs platform) | Supports IST and others |
| 13.3-10 | INR | COVERED-BUILT | base-currency costing (OD-16), currency on trade docs | Multi-currency beyond PRD |
| 13.3-11 | Tally integration for masters (items, vendors, customers) | MISSING | none in warehouse; accounting OD-1 mentions a Tally export adapter | — |
| 13.3-12 | Tally integration for vouchers (purchase, sales, credit/debit notes) | OTHER-MODULE | accounting (`ACCOUNTING-FUNCTIONAL-REQUIREMENTS.md:1884` OD-1) | Not designed; warehouse never raises vouchers/notes (D-16 item 6) |

### §13.4 Phasing vs batch / phase plan

| Id | PRD requirement (short) | Status | Evidence | Gap / note |
|---|---|---|---|---|
| 13.4-01 | Phase 1: Masters, CRM → SO, PR/PO, Gate, GRN, IQC, MRN, stock ledger | PARTIAL | Masters P1 (built), Gate/GRN/IQC P8 (#564/#566/#567 built, #565 open), MRN #569 open; PR/PO/SO in P9 (all open, no code) | Design order is P7 REM → P8 → P9 ∥ P10 (D-16 item 8). PRD Phase 1 needs P9 (trade) before P10 — fine if P9 is prioritised; "CRM → SO" link to the dealer CRM is fenced (D-16) **[C]** |
| 13.4-02 | Phase 2: BOM, routing, Production Order, MR against BOM, issue, return, job cards, PQC | COVERED-PLANNED | P10-03…P10-08 (#594–#599), P8-10/11 (#571, #572) | MFG FRs are v1.1 (FRD-MFG) |
| 13.4-03 | Phase 3: PDI, dispatch, sales invoice, purchase invoice, payments/receipts, warranty link, traceability | PARTIAL | dispatch built; traceability #70 | PDI missing; invoices/payments → accounting (deferred); warranty link fenced **[C]** |
| 13.4-04 | Phase 4: samples + drawings, ECN, costing, dashboards, complete accounts, statutory compliance, Tally sync | PARTIAL | costing #600; reports-kpis contract; warehouse-india e-way/ITC-04 | Samples/drawings missing; ECN declined (R-08); accounts deferred; Tally missing **[C]** |

## CONFLICTS (design set vs PRD)

1. **No mobile app** (13.3-06): D-16 item 7 + D-17 (b) defer every mobile FR post-v1; PRD wants Android for gate, GRN scan, IQC, issue scan, shop-floor booking, PDI. Q-G4 would settle scope.
2. **Accounting deferred / invoice refused** (1-01, 1-03, 13.2-23, 13.4-03/04): FRD-TRADE §11 R2 refuses sales invoice and 3-way match; D-16 item 6 says warehouse never raises debit/credit notes. PRD chain ends at Invoice → Payment, and Phase 3/4 include the full accounts module.
3. **Approval matrix covers trade documents only** (3-06, 4-48): core documents (MRN, MR, issue, return, gate pass, QC, BOM, production order) are single-step permission-gated; FR-466 `wh_approval_levels` (v2) was never built (#160 closed DUPLICATE). PRD: matrix "applies to every module".
4. **Per-approver limits vs per-rule bands** (3-04/3-05): design attaches the band to a rule and its levels; PRD attaches a limit to each approver and records the limit used.
5. **Escalation = alert, not re-route** (3-25): TAM-T3-01 re-alerts the same level; nothing moves to a higher approver.
6. **E-mail notifications not built** (3-24): in-app only in v1.
7. **Approvals not append-only at DB** (3-22, 13.3-04): step rows are updated in place; only the audit trail is append-only.
8. **Rejected ≠ Draft** (3-27): design has REJECTED (editable) + RETURNED → DRAFT + WITHDRAWN; PRD has reject → Draft.
9. **BOM/routing release is single-level** (3-35): PRD Design Head + Plant Head.
10. **IQC deviation / QC Manager approval** (3-31): design lets the inspector override the lot verdict with a reason, no second approver and no deviation document; PRD wants QC Manager (deviation: Plant Head).
11. **AVL enforcement is opt-in per item** (3-16, 4-26): ordering from any supplier is allowed for an item with no AVL rows; PRD "only approved vendor-item pairs can be ordered".
12. **Negative stock can be allowed** (13.3-05): `negative_stock_mode = ALLOW` exists; PRD "stock never negative (DB check)".
13. **Item master is warehouse-owned, not the CRM item master extended** (1-22, 4-08): no GST rate on the item; HSN only.
14. **No RLS / org_id** (1-24, 1-30): app-level company/site scoping.
15. **Own audit trail and approval engine** (1-26, 1-27) instead of the CRM `audit_log` and quotation approval pattern.
16. **Warranty & Service registry feed and "CRM → SO" fenced** (1-08, 1-29, 13.4-01): D-16 item 6 forbids edits to services/dealer.
17. **MRP is designed although PRD scopes it out** (1-11): P10-11/12 (#602, #603).
18. **ECN declined** (13.2-14): FRD-MFG R-08; PRD Phase 4 lists ECN.
19. **Stores modelled as stock status / virtual locations** (4-28): no Sample store; Quarantine/Rejected are statuses on a bin, not separate stores. Behaviour matches; reports/labels will read differently to the client.

## BEYOND-PRD

Industry gaps neither PRD nor design covers (substantive, Indian vehicle-manufacturing ERP):
- **Calibration / gauge master** for QC instruments (IATF 16949 / ISO 9001 7.1.5) — PRD lists "instrument" on QC parameters, design has none outside legal-metrology weighing (v2).
- **PPAP / first-article inspection for new vendor parts** — design records the *customer's* part approval (FR-545), not our approval of a supplier part before AVL `APPROVED`.
- **Shift calendar + holiday calendar** for work centres and operator authorisation (PRD's "capacity per shift" needs it).
- **Vendor contacts and bank details** (needed for PO e-mail and payment) — #78 explicitly excludes them.
- **Segregation-of-duties matrix report** (who holds both maker and checker rights) — natural audit companion to maker ≠ checker.
- **Delegation expiry/out-of-office for core documents** — delegation exists for trade only.
- **VIN / chassis-number rules** (WMI/VDS, check digit, Form 21/22 data) for an automotive OEM — not in either.
- **CMVR homologation / type-approval and COP sample tracking** for vehicle manufacturers — samples requirement hints at it.

Design covers but PRD omits (tell the client):
- Delegation with second-person confirmation (FR-552), withdraw before action, return-for-changes, stale-version guard (TAM-GRD-04/10), ambiguous-rule refusal at save (TAM-GRD-05).
- Configurable sampling band tables + ISO 2859-1 / IS 2500 (FR-521…524).
- MSME 45-day payment-terms warning and Udyam fields on suppliers (FR-542).
- Customer item reference with drawing no./revision and customer PPAP status (FR-545).
- Gapless numbering with FY token, branch-scoped series for tax documents (#84, FR-426).
- MRP, subcontracting / job work + ITC-04, bonded/MOOWR, e-way bill, Rule 56 stock account (warehouse-india).
- Multi-currency, multi-site timezone, hash-chained audit trail, cycle counting and valuation.
- Vendor rating and customer OTIF on one engine (#589); rate contracts and price lists (#583).

## QUESTIONNAIRE dependencies

| Q | Depends here | Already answered in the design set by assumption? |
|---|---|---|
| Q-G1 plants / stores per plant | 4-27, 4-28, 13.3-01 | Partly: multi-site model; stores = statuses/zones. No count assumed |
| Q-G2 users per department | 1-13…1-21, 3-29…3-39 | Actor tables in FRD-STORES/TRADE/MFG; no head-count |
| Q-G3 FY + numbering format, series per plant | 4-49, 13.3-02 | **Yes**: `{FY}` reset on 1 April, per warehouse series (#84); trade per company, optionally per site (FR-547) |
| Q-G4 which flows on mobile | 13.3-06 | **Yes, opposite**: no mobile in v1 (D-16 item 7, D-17 b). Needs client confirmation |
| Q-G5 barcode/QR, printer make, label size | 13.3-07 | Partly: ZPL first, Code-128, QR kind seeded (#100, #310); no printer make assumed |
| Q-G6 go-live date / urgent phase | 13.4-01…04 | Program order P7 → P8 → P9 ∥ P10 (D-16 item 8); no date |
| Q-A1 approval matrix per doc / level / value | 3-04, 3-06, 3-29…3-39, 4-48 | Partly: trade examples only (WH-SC-489: PO ≤ ₹1,00,000 PM; above PM → PH); core docs single-step |
| Q-A2 e-mail / WhatsApp / in-app; escalation hours | 3-23…3-25 | **Yes**: in-app only, alert after 24 h (`warehouse.approval.pending_alert_hours`), no e-mail/WhatsApp, no escalation |
| Q-A3 self-approval in exceptional cases | 3-03 | **Yes**: never, not even ADMIN (TAM-UNR-04, MD-21) — matches PRD recommendation |
| Q-A4 daily management reports | 1-21 | Partly: stores registers #574, trade reports #591, MFG registers #604, reports-kpis contract; no daily digest assumed |
