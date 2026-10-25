# Gap analysis — slice "production-quality-samples"

PRD (client, 2026-10-24) lines 230-308 (§9 Production, §10 Quality, §11 Samples & drawings) + §13.1 Quality / Production report rows (lines 413-416), questionnaire Q-PR1..7, Q-Q1..4, Q-S1..5.
Compared against: `warehouse-issues/docs/frd/FRD-MFG.md` (FR-620..678, MD-01..43, R-01..14, OD-40..44), `FRD-STORES.md` (FR-512, FR-521..527, FR-529), `FRD-TRADE.md` (FR-545), contracts `mfg-*`, `receipt-qc-putaway`, `trade-counterparty-evaluation`, `mrn-authorisation`, DECISIONS, R27..R31, the 630-issue corpus, and the built code in `classic/warehouse` (spot checks).

Key context: **all of §9 lands in `warehouse-manufacturing` (P10, epic #548, tasks #592..#605 — every one OPEN; no code exists).** The shared QC engine (polymorphic source, plans, criteria with min/max, sampling) is **built** in core `warehouse` (P1-14 #120, P8-05 #566, P8-06 #567 closed; `WhQualityInspection.java`, `V510015`/`V510016`). Nothing in the design set or issue corpus covers **samples, drawings, PDI as a distinct gate, NCR/CAPA, deviations, batches, per-batch job cards, chassis/part-serial binding, the production board or shop-floor mobile**.

## Summary counts

| Status | Count |
|---|---|
| COVERED-BUILT | 10 |
| COVERED-PLANNED | 33 |
| DESIGN-ONLY | 0 |
| PARTIAL | 49 |
| DECLINED | 2 |
| OTHER-MODULE | 0 |
| MISSING | 59 |
| CONFLICT (also tagged in matrix) | 13 (listed in §CONFLICTS; each also carries a PARTIAL/MISSING/DECLINED/COVERED status) |
| **Total atomic requirements** | **153** |

DESIGN-ONLY is 0 because every MFG FR in FRD-MFG §13 traceability is owned by an open P10 task (#592..#605); every core QC FR is owned by a closed or open P8 task.

## Matrix

Legend: `#n` = warehouse-issues GitHub issue. "P10-xx" tasks: #592 P10-01 … #605 P10-14 (all OPEN). FR ids are FRD-MFG unless prefixed.

### §9 intro / §9.1 Production Order

| Id | PRD requirement (short) | Status | Evidence | Gap / note |
|---|---|---|---|---|
| 9.0-01 | PO-P raised from an approved SO line | COVERED-PLANNED | FR-633 source "demand-order line", FR-637 MTO link; #596 P10-05; demand-order port P8-02 #563 (built); trade SO #586 | "Approved" SO gate is trade's SO status (P9-09); MFG reads core demand order, not SO approval |
| 9.0-02 | Released only on released BOM + routing | COVERED-PLANNED | FR-635 (`409 BOM_NOT_EFFECTIVE`), FR-625 maker-checker BOM; #594, #596 | Routing = the BOM's optional operation list (FR-631) — not a separate released object |
| 9.0-03 | Progresses stage by stage, batch by batch until PDI | PARTIAL | FR-651 optional operation confirmations; FR-652 final QC | No batch grain at all; stages are optional and not sequenced (see 9.2) |
| 9.1-01 | Source: SO line (default) | COVERED-PLANNED | FR-632/633 `demand_source_type = DEMAND_ORDER`; #596 | Default is MANUAL/MRP in design (R-11: no automatic order from SO; planner converts) |
| 9.1-02 | Source: multiple SO lines of same item consolidated | PARTIAL | `whm_production_orders.demand_source_line_id` is a single line (FRD-MFG §4); multi-demand only through MRP pegging (FR-666, `whm_mrp_pegging`, #603) | Manual consolidation of N SO lines into one order and per-SO output reservation split missing |
| 9.1-03 | Source: make-to-stock by planner, with approval | PARTIAL | Manual order FR-633; `release_requires_approval` (FR-635, default false, global) | No "MTS needs approval" rule distinct from release approval |
| 9.1-04 | Source: Sample (§11) | MISSING | `WHM_ORDER_TYPE` = STANDARD/REWORK/SUBCONTRACT only (FRD-MFG §3.1) | Code list is extensible, but no sample semantics (draft BOM, separate cost, sample store) |
| 9.1-05 | Source: Rework | COVERED-PLANNED | FR-653, `demand_source_type = QC_REWORK`; #599 | |
| 9.1-06 | Field: order no. | COVERED-PLANNED | FR-636 gapless `PRD-` per site; #596 | |
| 9.1-07 | Field: item / variant | PARTIAL | FR-632 item; R-09 refuses variant-rule BOMs ("variants are separate items") | Variant must be modelled as its own item + BOM — tell client |
| 9.1-08 | Field: qty | COVERED-PLANNED | `planned_quantity`, UoM (FR-632) | |
| 9.1-09 | Field: SO ref(s) + customer | PARTIAL | `demand_source_ref` (frozen SO/customer number) — one ref | Plural SO refs missing (follows 9.1-02) |
| 9.1-10 | Field: BOM revision | COVERED-PLANNED | `bom_id` = frozen version (FR-632/633) | |
| 9.1-11 | Field: routing revision | PARTIAL | Operations live inside the BOM version (FR-631, `whm_bom_operations`) | No independent routing revision; a routing change = new BOM version (CONFLICT C-03) |
| 9.1-12 | Field: planned start / end | COVERED-PLANNED | `planned_start_date`/`planned_end_date` DATE | |
| 9.1-13 | Field: priority | COVERED-PLANNED | `priority SMALLINT 1..5` | |
| 9.1-14 | Field: batch size → no. of batches | MISSING | no batch column/table anywhere in FRD-MFG §4; grep "batch size" = 0 hits in MFG files | Core of PRD's "batch-wise" model. Q-PR2 |
| 9.1-15 | Field: plant / line | PARTIAL | `warehouse_id` (site) + header `work_centre_id` | No production-line master distinct from work centre; plant = site |
| 9.1-16 | Release check: BOM and routing released | COVERED-PLANNED | FR-635, MD-19 | |
| 9.1-17 | Release check: material availability (available / shortage) | COVERED-PLANNED | FR-635 shortage list per component | |
| 9.1-18 | Release check: "on order with ETA" per short component | MISSING | Release check reads allocatable stock only (FR-635); PO schedule-line supply used only by MRP (FR-664) | Add open-PO quantity + earliest ETA to the shortage list |
| 9.1-19 | Release check: capacity per work centre shown | PARTIAL | Capacity load report WS-336, FR-668, #604 | Not shown in the release dialog; infinite capacity only (R-01) |
| 9.1-20 | Release with shortage only with Production Manager approval | PARTIAL | `release_with_shortage` BLOCK/WARN(default)/ALLOW; `release_requires_approval` separate global flag (FR-635, MD-12) | No "approval required only when short" mode; default WARN lets planner release short with no approver (CONFLICT C-02). Q-PR5 |
| 9.1-21 | Flow: Draft → Approved → Released | PARTIAL | Ladder `PLANNED → RELEASED` (FR-634); approval only as optional release maker-checker | No `APPROVED` state (CONFLICT C-01) |
| 9.1-22 | Flow: In progress → Completed | COVERED-PLANNED | FR-634; MD-14 (COMPLETED = technically complete) | |
| 9.1-23 | Flow: Closed after FG receipt and variance review | COVERED-PLANNED | FR-656 settlement; variance > `close_variance_approval_percent` (5%) needs approver; #600 | |
| 9.1-24 | Flow: Short-closed (reason) | PARTIAL | Complete with `PRODUCTION_CLOSE_SHORT` reason, then Close (FR-647, MD-15) | No distinct `SHORT_CLOSED` status — closed-short orders indistinguishable by status (CONFLICT C-01) |
| 9.1-25 | On release: batches generated | MISSING | — | Follows 9.1-14 |
| 9.1-26 | On release: job cards generated | PARTIAL | Operations snapshotted at **create** (FR-633); traveller print `PRODUCTION_ORDER_TRAVELLER` (FR-636) | No job-card document per batch × stage |
| 9.1-27 | On release: MR against BOM can be raised | COVERED-PLANNED | FR-640 "Request materials" → `WhMaterialRequisitionPort` (P8-09 #570 built); #597 | |

### §9.2 Job cards and stage-wise booking

| Id | PRD requirement (short) | Status | Evidence | Gap / note |
|---|---|---|---|---|
| 9.2-01 | One job card per batch per routing stage, in routing sequence | MISSING | `whm_production_order_operations` is per order (FRD-MFG §4); confirmations FR-651 | No batch × stage document |
| 9.2-02 | Stage starts only when previous stage has output (or partial, if allowed) | MISSING | QRW-GRD-01..06 have no predecessor check; milestone confirms *earlier* ops (FR-651) | No sequence gate, no "partial output allowed" flag |
| 9.2-03 | Start / pause / complete with timestamps | PARTIAL | Confirmation `started_at`/`finished_at` recorded after the fact (QRW-T1-01) | No live start event, no pause/resume; confirmation is one record per booking |
| 9.2-04 | Operators only those authorised for that stage | MISSING | QRW-GRD-06: any active company user | Need operator ↔ work-centre/operation skill authorisation |
| 9.2-05 | Operator(s) — more than one | PARTIAL | single `operator_user_id` | Crew booking missing |
| 9.2-06 | Machine | MISSING | work centre only; tool/mould refused to assets (R-12) | Machine within a work centre not modelled |
| 9.2-07 | Shift | MISSING | no shift column/master in MFG (only persona "shift in-charge") | Platform has no shift master either |
| 9.2-08 | Output: good qty | COVERED-PLANNED | `good_quantity` FR-651; #599 | |
| 9.2-09 | Output: rework qty | COVERED-PLANNED | `rework_quantity` | |
| 9.2-10 | Output: rejected qty with reason | PARTIAL | Confirmation has scrap + reason only; "reject" exists only as an in-process QC outcome (QRW-T1-05) | No rejected-qty field at the stage |
| 9.2-11 | Output: scrap | COVERED-PLANNED | `scrap_quantity`, `PRODUCTION_SCRAP` reason (QRW-GRD-04) | |
| 9.2-12 | Good qty moves to the next stage | MISSING | Confirmations post no movement and no inter-stage quantity (QRW-UNR-02) | No WIP-per-stage quantity; next stage not capped by previous good |
| 9.2-13 | Material consumption recorded at the consuming stage | PARTIAL | BOM line `operation_seq` link (FR-623); consumption posts at issue or at receipt backflush (FR-645), never at a stage | Stage-level backflush missing |
| 9.2-14 | Serial-tracked parts scanned and bound to the unit (chassis ↔ motor, controller, battery, charger) | MISSING | MD-11/MD-41: genealogy at order-receipt grain, per-unit consumption capture **rejected** ("operator burden SMEs refuse"); consumption lines carry `serial_id` but link all inputs to all outputs (FR-648) | Unit-level as-built record absent; CONFLICT C-04. Q-PR3 |
| 9.2-15 | Unit serial / chassis no. assigned at first stage (or pre-printed series) | MISSING | Serials captured only at production receipt (PRC-GRD-09) | No serial pre-allocation series for MFG output; no VIN/chassis format |
| 9.2-16 | Serial carried through all stages | MISSING | — | Follows 9.2-15 |
| 9.2-17 | Job-work stage: stage sent to vendor on JW challan, received back, continues | PARTIAL | Subcontracting is a whole order of type `SUBCONTRACT` (FR-658..661, #601); india challan + ITC-04 via SEAM-M5, P4-02 #22 (built) | A mid-routing operation sent out needs a child subcontract order (sub-assembly, `parent_order_id`); no "JW operation" on the routing (CONFLICT C-05) |
| 9.2-18 | PQC hold: output waits for PQC result before next stage | PARTIAL | FR-652 in-process inspection at `is_qc_checkpoint` op (record-only, SEAM-M4); only gate = `block_receipt_on_open_inprocess_qc` (default **false**) on the **receipt** (QRW-GRD-09) | No next-stage gate (CONFLICT C-06). Q-Q3 |
| 9.2-19 | Rework loop: rejected units → rework job card → back to the same stage | PARTIAL | In-process `REWORK` outcome only records qty (QRW-OPEN-05: no rework order); final-QC `REWORK` creates a separate rework order (FR-653) | No return to the originating stage |
| 9.2-20 | Rework repeat counts tracked | MISSING | rework-of-rework allowed (QRW-T1-10), not counted | Per-unit count needs unit serial (9.2-15). Q-PR6 |

### §9.3 Completion and FG receipt

| Id | PRD requirement (short) | Status | Evidence | Gap / note |
|---|---|---|---|---|
| 9.3-01 | Last stage output → PDI | PARTIAL | Final QC on production-receipt `QC_HOLD` output (FR-644, FR-652; #598, #599) | PDI is generic final QC; no PDI type, no per-vehicle record |
| 9.3-02 | PDI-passed units received into FG store against the order | COVERED-PLANNED | Receipt into `QC_HOLD` → release → `AVAILABLE` + putaway (QRW-T1-06) | Order of events differs: stock is *received* first, then inspected (CONFLICT C-07, cosmetic) |
| 9.3-03 | …and reserved for the SO | COVERED-PLANNED | FR-637 `reserve_output_for_demand`, reserved at QC release (R29 F15) | |
| 9.3-04 | Closure: planned vs actual qty | COVERED-PLANNED | Cost sheet FR-656; production register WS-337 #604 | |
| 9.3-05 | Closure: material variance (BOM vs issued − returned) | COVERED-PLANNED | Consumption-variance register (#604), cost sheet planned vs actual by component (FR-656) | |
| 9.3-06 | Closure: time variance (standard vs actual hours) | PARTIAL | `planned_setup/run_minutes` vs `actual_minutes` on order operations; cost sheet "recorded, not absorbed" (CST-T4-10) | No time-variance figure/report stated |
| 9.3-07 | Closure: rejection % | COVERED-PLANNED | Yield register good ÷ (good+rejected+scrapped) (#604); order rollups | |
| 9.3-08 | Closure: cost per unit | PARTIAL | Actual material cost per unit (FR-654); labour/overhead recorded only (OD-43, R-05) | Q-PR7 — full cost per unit needs OD-43 reversed |

### §9.4 Shop-floor screens

| Id | PRD requirement (short) | Status | Evidence | Gap / note |
|---|---|---|---|---|
| 9.4-01 | Production board: orders by status | PARTIAL | WS-323 grid + status filters (#596) | No board view |
| 9.4-02 | Batch progress across stages (Kanban) | MISSING | grep kanban/board in MFG = 0 | |
| 9.4-03 | WIP by stage | MISSING | WS-337 "WIP by order" is value per order (#604) | |
| 9.4-04 | Today's plan vs actual | MISSING | — | No daily plan object |
| 9.4-05 | Delayed orders | COVERED-PLANNED | PRO-T3-01 late order (`lateOnly` filter + tile), PRO-T3-02 late start (`WhmLateOrderAlertJob`) | |
| 9.4-06 | Mobile/tablet: operator scans job-card QR → start/complete → qty → scan serials | DECLINED | FRD-MFG R-13 + FR-669 "No mobile" (user rule 2026-09-11); FR-218 DEFERRED by D-17 | **PRD contradicts** the no-warehouse-mobile rule (and DECISIONS D-13 still says mobile is not optional — internal inconsistency). Q-PR4 |
| 9.4-07 | Job card carries a QR | PARTIAL | Traveller prints barcode (FR-636) | Per order, not per job card |

### §10 Quality — inspection matrix (every cell)

| Id | PRD requirement (short) | Status | Evidence | Gap / note |
|---|---|---|---|---|
| 10-01 | Three gates share one engine (checklists, parameters, sampling, results, approvals) | COVERED-BUILT | FRD-STORES FR-525 polymorphic source; P8-06 #567 closed; `WhQualityInspection.java` `source_type`/`inspection_stage` | MFG resolvers (`PRODUCTION_RECEIPT`, `IN_PROCESS`) planned #599 |
| 10-02 | IQC trigger: GRN line for item with QC = Yes | COVERED-BUILT | Plan assignment precedence + `NO_INSPECTION` (FR-523, FR-129); P8-05 #566, P8-06 #567 | |
| 10-03 | PQC trigger: completion of routing stage marked QC checkpoint | COVERED-PLANNED | `is_qc_checkpoint`, `inspection_required` (FR-631, FR-652, QRW-GRD-10); #595, #599 | |
| 10-04 | PDI trigger: last production stage complete | PARTIAL | Final QC when item × site requires final inspection (FR-644) | Triggered by receipt, not by last-stage completion |
| 10-05 | PDI also before dispatch of FG from stock | PARTIAL | Core `STOCK`-source inspection exists (FR-525, built) | No rule forcing PDI before dispatch of stock FG |
| 10-06 | IQC checklist from item / item category | COVERED-BUILT | `wh_inspection_plan_assignments` item → category precedence (FR-523); `V510015` criteria rows | |
| 10-07 | PQC checklist from routing stage | MISSING | `whm_bom_operations` has no plan reference; mfg-qc-rework silent on plan resolution | Need operation → inspection plan link |
| 10-08 | PDI checklist from FG model/variant | COVERED-PLANNED | Item-level plan assignment (built) applied to `PRODUCTION_RECEIPT` source (#599) | Variant = item (R-09) |
| 10-09 | + customer-specific PDI points from SO | MISSING | — | SO-line inspection points not modelled |
| 10-10 | IQC sampling: AQL plan or 100 % | COVERED-BUILT | `AQL_TABLE`, `FULL`, `BAND_TABLE` (FR-521/522; P8-05 #566); Z1.4 table seed #610 OPEN | |
| 10-11 | IQC sampling: per serial for serial items | PARTIAL | Inspection line per GRN line with qty (`V510016`) | No per-serial result rows |
| 10-12 | PQC sampling: per-batch first-piece + patrol | MISSING | grep first-piece/patrol = 0 | |
| 10-13 | PQC sampling: or 100 % | PARTIAL | `FULL` plan type exists; in-process inspection = one line per confirmation (QRW-T1-04) | No per-unit result |
| 10-14 | PDI sampling: 100 % — every vehicle | PARTIAL | `FULL` possible on receipt output line | No per-vehicle inspection record (needs unit serial) |
| 10-15 | IQC typical checks (dimensions, visual, COA, battery V/AH, motor rating, controller spec) | COVERED-BUILT | Criteria TEXT/NUMBER/BOOLEAN with min/max (`V510015` `wh_inspection_plan_criteria`) | Content is client data (Q-Q1); COA attachment not supported (see 10-35) |
| 10-16 | PQC typical checks (weld, paint DFT, torque, harness continuity) | COVERED-PLANNED | Same criteria engine via `IN_PROCESS` source (#599) | Depends on 10-07 for per-stage checklist |
| 10-17 | PDI typical checks (road test, braking, lights, horn, battery charge, range, serials match, accessories, documents, finish) | PARTIAL | Generic criteria cover the manual checks | "Serials match" auto-check needs as-built binding (9.2-14) |
| 10-18 | IQC outcome: Accept / Reject | COVERED-BUILT | Dispositions release / REJECT / RTV / SCRAP (FR-134, `V510016`) | |
| 10-19 | IQC outcome: Accept under deviation | MISSING | no deviation/concession concept in design or code (grep 0) | |
| 10-20 | PQC outcome: Pass / Rework / Reject | COVERED-PLANNED | `INSPECTION_OUTCOME` ACCEPT/REJECT/REWORK (FR-525, SEAM-M4); #599 | |
| 10-21 | PQC outcome: Pass under deviation | MISSING | — | |
| 10-22 | PDI outcome: Pass | COVERED-PLANNED | release disposition (QRW-T1-06) | |
| 10-23 | PDI outcome: Rework (back to stage) | PARTIAL | `REWORK` disposition → new rework order (FR-653) | Not "back to stage" |
| 10-24 | PDI outcome: Hold | PARTIAL | Stock stays `QC_HOLD` until dispositioned; core holds (P1/P5 holds, built) | No explicit Hold outcome with reason |
| 10-25 | IQC moves: Quarantine → Main via MRN | COVERED-PLANNED | FR-527 MRN, `MRN_PENDING`; P8-08 #569 OPEN; `QC_HOLD` built | |
| 10-26 | IQC moves: → Rejected | COVERED-BUILT | REJECT → `REJECTED` status (`V510016`); "Raise supplier return" P8-07 #568 OPEN | |
| 10-27 | PQC moves: next stage, rework job card, or scrap | PARTIAL | In-process is record-only, posts no movement (QRW-UNR-03); reject pre-fills next receipt's rejected qty | No stage movement, no rework job card |
| 10-28 | PDI moves: FG store (reserved to SO) | COVERED-PLANNED | FR-637/652 | |
| 10-29 | PDI moves: or rework | PARTIAL | rework order (FR-653) | as 10-23 |
| 10-30 | IQC approver: QC Manager | PARTIAL | Completion/disposition by `wh_quality_inspections:disposition`; second-person approval only for scrap (`:approve`) and MRN authorise (FR-527) | No QC-manager approval of accept/reject |
| 10-31 | IQC/PQC deviation approver: Plant Head | MISSING | — | |
| 10-32 | PQC approver: QC Manager | PARTIAL | as 10-30 | |
| 10-33 | PDI: QC Manager signs PDI certificate | MISSING | — | |

### §10 Common requirements

| Id | PRD requirement (short) | Status | Evidence | Gap / note |
|---|---|---|---|---|
| 10-34 | Readings entered against spec; out-of-spec auto-fails the parameter | COVERED-BUILT | `min_value`/`max_value`/`expected_text` (`V510015:151-154`); `validationService.computeVerdict` → `is_pass` (`WhQualityInspectionService.java:472-481`) | |
| 10-35 | Photos and files per parameter | MISSING | `wh_quality_inspection_results` has no attachment; no document link on inspection entities | Platform documents exist — needs a link per result |
| 10-36 | Inspector cannot inspect their own production | MISSING | no guard in mfg-qc-rework | Needs operator (confirmation/receipt poster) ≠ inspector |
| 10-37 | Inspector cannot inspect their own GRN | MISSING | Only MRN authoriser ≠ inspector (FR-527, `mrn_authoriser_may_be_inspector`) | Receiver ≠ inspector not enforced |
| 10-38 | NCR for every reject: defect, root cause | MISSING | grep NCR/non-conformance in design = 0 (one reference-download hit); reason code on line only | Supplier claim P5-23 #123 is commercial; reconciliation case FR-138 is inbound variance |
| 10-39 | CAPA: corrective/preventive action, owner, due date, closure | MISSING | — | Q-Q4 |
| 10-40 | Deviation time- or qty-bound and expires | MISSING | — | Also needed by PRD §8.4 alternate-item rule (other slice) |
| 10-41 | PDI certificate PDF per vehicle (chassis no., part serials, checklist result, inspector, date), printed for dispatch, stored for warranty | MISSING | Print framework P2-14 exists; FRD-MFG R-10 "print templates can render a CoA" (re-entry only) | Needs unit serial + bound parts (9.2-14/15); warranty registry is PRD §12 (other slice) |
| 10-42 | QC dashboard: vendor-wise rejection % | PARTIAL | P9-12 #589 vendor rating metric `QUALITY_ACCEPTANCE` (trade-counterparty-evaluation:52); inspection grid statistics (built) | No QC dashboard; needs trade module |
| 10-43 | QC dashboard: stage-wise first-pass yield | MISSING | Yield register (#604) is final output by item/work centre, not first-pass by stage | |
| 10-44 | QC dashboard: top defects (Pareto) | MISSING | — | Reason codes exist; no defect taxonomy or Pareto |
| 10-45 | QC dashboard: open NCRs | MISSING | — | Follows 10-38 |

### §11 Samples and drawings

| Id | PRD requirement (short) | Status | Evidence | Gap / note |
|---|---|---|---|---|
| 11-01 | Sample built only from approved drawing revision, by authorised users, on a Sample PO-P linked to enquiry/SO | MISSING | grep "sample order/request/store" = 0 | Whole §11 has no owner in any FRD or issue |
| 11-02 | Customer's sample approval releases the bulk SO to production | MISSING | — | |
| 11-03 | Sample request raised from enquiry or SO (Sales) | MISSING | Trade enquiry/quotation P9-08 #585 has no sample request | |
| 11-04 | Sample request fields: item/spec, qty, required date, customer drawing/spec upload, chargeable or free | MISSING | — | Q-S4 |
| 11-05 | Drawing master: drawing no., revision A/B/C…, file PDF/DWG/image, linked item and BOM | PARTIAL | FRD-TRADE FR-545 customer item reference holds `drawing_number` + `drawing_revision` as text (P9-02 #579); FR-038: drawing no. is not an item identifier | No drawing entity, no file, no BOM link. Q-S2 |
| 11-06 | Drawing status Draft → Internal review → Released for sample → Customer approved → Released for production / Superseded | MISSING | — | |
| 11-07 | Only `drawing:create` uploads; only `drawing:approve` releases, never the uploader | MISSING | Maker-checker precedent: BOM FR-625 `403 BOM_SELF_APPROVAL` | Q-S3 |
| 11-08 | Every revision kept | MISSING | — | |
| 11-09 | Production and purchase screens always show current released revision | MISSING | — | |
| 11-10 | PO for a drawing-based part carries drawing no. + revision | MISSING | Trade PO line (trade-purchase-order contract) has no drawing fields | |
| 11-11 | Watermark "UNCONTROLLED COPY" on prints of non-released revisions | MISSING | Precedent: MRN print watermark "NOT AUTHORISED" (mrn-authorisation A-T2-07) | |
| 11-12 | Sample BOM/routing may be a draft (trial) BOM flagged "Sample" | MISSING | Orders select only `APPROVED` effective BOMs (FR-626, FR-635); usage `ENGINEERING` exists but is not orderable | CONFLICT C-08 |
| 11-13 | Trial BOM allowed only on a Sample PO-P | MISSING | — | |
| 11-14 | Sample PO-P: MR → issue → stages → QC exactly as normal | MISSING | Would reuse the ordinary ladder once an order type exists | |
| 11-15 | Sample costs captured separately | PARTIAL | Each order has its own pool (FR-654) | No sample-cost classification/report |
| 11-16 | Sample QC / internal approval: QC + Design check vs drawing, report attached | MISSING | — | |
| 11-17 | Sample dispatch: delivery challan returnable or non-returnable | PARTIAL | Gate pass RGP/NRGP purpose `SAMPLE` (FRD-STORES FR-512; P8-03 #564 built); india DC (built) | Not linked to a sample document |
| 11-18 | Sample dispatch: courier / AWB, date | MISSING | gate pass has no AWB field | |
| 11-19 | Sample dispatch approved by Sales Manager | PARTIAL | Gate pass `DRAFT → APPROVED` checker ≠ maker (FR-514) | Generic approver, not sales-manager role |
| 11-20 | Customer feedback: Approved / Approved with changes / Rejected, remarks, files | MISSING | — | |
| 11-21 | Changes → new drawing revision → new sample cycle; iteration no. tracked | MISSING | — | |
| 11-22 | On approval: drawing and BOM released for production | MISSING | — | |
| 11-23 | ECN if a released version existed | DECLINED | FRD-MFG R-08 (ECO workflow / change-number master refused; versioning + effectivity + change reason + maker-checker instead); mfg-bom §refusals | **PRD contradicts** (also Q-B6). CONFLICT C-09 |
| 11-24 | SO lines referencing the sample become eligible for PO-P | MISSING | — | |
| 11-25 | Control: SO lines "sample approval required" cannot raise a PO-P until customer-approved | PARTIAL | FR-545 `requires_part_approval` refuses the **SO/quotation line itself** (`422 TRADE_CUSTOMER_PART_NOT_APPROVED`) | Wrong gate: PRD lets the SO exist and blocks production (CONFLICT C-10) |
| 11-26 | Sample stock sits in a separate Sample store | PARTIAL | Stores/locations configurable (built); MRQ purpose `SAMPLE` (FR-529) | No sample-store designation or enforcement |
| 11-27 | Samples returned by customer come back via gate entry (Returnable) | PARTIAL | Inward gate entry + RGP return tracking (FR-507/514; P8-03 #564 closed, built) | Not linked to the sample; customer return receipt path is RMA, not RGP |

### §13.1 Reports — Quality and Production rows

| Id | PRD requirement (short) | Status | Evidence | Gap / note |
|---|---|---|---|---|
| 13.1-Q1 | IQC rejection by vendor / item | PARTIAL | P9-12 #589 `QUALITY_ACCEPTANCE`; inspection grid/export filters (built) | No dedicated report |
| 13.1-Q2 | PQC first-pass yield by stage | MISSING | as 10-43 | |
| 13.1-Q3 | PDI pass % | PARTIAL | Inspection statistics `passCount` by stage (WhQualityInspectionQueryService:213) | No PDI-specific % |
| 13.1-Q4 | Defect Pareto | MISSING | | |
| 13.1-Q5 | Open NCR / CAPA | MISSING | | |
| 13.1-Q6 | Deviations | MISSING | | |
| 13.1-P1 | Order status | COVERED-PLANNED | WS-323 #596 | |
| 13.1-P2 | Batch progress by stage | MISSING | | |
| 13.1-P3 | WIP | COVERED-PLANNED | WS-337 WIP by order (#604) | By order value, not by stage |
| 13.1-P4 | Plan vs actual | PARTIAL | Production register, cost sheet | No daily/period plan baseline |
| 13.1-P5 | Operator output | MISSING | Confirmations carry operator (FR-651); no report | |
| 13.1-P6 | Material variance | COVERED-PLANNED | Consumption-variance register #604 | |
| 13.1-P7 | Time variance | PARTIAL | as 9.3-06 | |
| 13.1-P8 | Cost per unit | PARTIAL | as 9.3-08 (material only, OD-43) | |
| 13.1-P9 | Production orders consume components via MR/issue with cost object (supporting §9.1 MR) | COVERED-BUILT | P8-09 #570 closed (requisition with `PRODUCTION_ORDER` cost object) | Store issue P8-10 #571 still OPEN |
| 13.1-P10 | FG reserved to SO feeds "SO pending to produce" | COVERED-BUILT | Demand-order port P8-02 #563 closed (fulfilment position read by MFG FR-637) | Sales/CRM row itself is another slice |

## CONFLICTS (design set vs PRD)

| # | Topic | PRD | Design set | Where |
|---|---|---|---|---|
| C-01 | Production-order states | Draft → **Approved** → Released → In progress → Completed → Closed / **Short-closed** | `PLANNED → RELEASED → IN_PROGRESS → COMPLETED → CLOSED`, `CANCELLED`; no APPROVED, no SHORT_CLOSED (close-short is a reason on Complete) | FR-634, mfg-production-order §ladder |
| C-02 | Release with shortage | Allowed **only with Production Manager approval** | `release_with_shortage` default **WARN** (no approver); release approval is a separate global flag default **off** (MD-12: "SME planners release dozens a day") | FR-635, §8 settings |
| C-03 | Routing | Separate routing with its own revision, released with the BOM | Routing is an **optional** operation list inside the BOM version; "routing is never mandatory" | FR-631, MD-09 |
| C-04 | Unit serial binding | Each part serial scanned and bound to the vehicle chassis at the consuming stage | Genealogy at **order-receipt grain**; per-unit consumption capture explicitly rejected | MD-11, MD-41, FR-648 |
| C-05 | Job work | A **stage** of the production order goes to a vendor and returns | Subcontracting is a **whole order** of type SUBCONTRACT producing a different processed item | FR-658, mfg-subcontracting |
| C-06 | PQC | Failing/pending PQC holds the **next stage** | In-process QC is record-only; optional gate (default off) blocks only the **FG receipt** | FR-652, QRW-GRD-09, `block_receipt_on_open_inprocess_qc=false` |
| C-07 | FG receipt vs PDI order | PDI first, then receive PDI-passed units into FG | Receive into `QC_HOLD` first, then final QC releases | FR-644, QRW-T1-06 (cosmetic: outcome equivalent, ledger sequence differs) |
| C-08 | Sample / trial BOM | Draft (trial) BOM usable on a Sample order | Only `APPROVED`, effective BOMs can be put on an order | FR-626, FR-635 |
| C-09 | ECN | ECN when a released drawing/BOM is changed | ECO workflow **refused** (R-08) | FRD-MFG R-08; mfg-bom refusals |
| C-10 | Sample-approval control | SO allowed; **production** blocked until sample approved | `requires_part_approval` blocks the **SO/quotation line** until a customer item reference is APPROVED | FRD-TRADE FR-545 |
| C-11 | Shop-floor mobile | Operator mobile/tablet with QR scan | **No warehouse mobile** (R-13, FR-669, FR-218 deferred by D-17) — while DECISIONS **D-13 "Mobile is not optional"** still stands unamended | FRD-MFG R-13; DECISIONS D-13 — internal design-set inconsistency to resolve |
| C-12 | Make-to-order automation | Default source is the SO line (order raised from SO) | R-11: no automatic production order from SO; MRP proposes, planner converts | FRD-MFG R-11 |
| C-13 | Cost per unit | Cost per unit at closure (implies full cost) | Material-only actual cost; labour/overhead recorded, not absorbed | OD-43, R-05 |

## BEYOND-PRD

### Industry gaps — neither PRD nor design set (Indian EV / discrete manufacturer)
1. **Homologation / Conformity of Production** — CMVR type approval (ARAI/ICAT), COP sampling, AIS-156 / AIS-038 Rev 2 battery-safety checks as PDI/PQC content; vehicle data for **Form 22** (initial certificate of compliance) and Vahan dealer-point upload per chassis. **RE-VERIFY**.
2. **VIN / chassis-number structure** — 17-char VIN with WMI (SIAM/ARAI allocation), model-year and plant codes, check digit; pre-printed series control and void/scrapped-chassis register.
3. **Battery traceability & EPR** — battery-pack serial ↔ cell lot ↔ BMS id; Battery Waste Management Rules 2022 EPR registration and quantity reporting; battery passport readiness. **RE-VERIFY**.
4. **PM E-DRIVE / PMP localisation (DVA)** — domestic-value-addition evidence per component per vehicle for subsidy claims; needs supplier/origin on bound serials. **RE-VERIFY**.
5. **Measuring-instrument calibration** (ISO 9001 §7.1.5 / IATF) — gauge/torque-tool master with due dates; a reading against an out-of-calibration instrument should be refused.
6. **SPC on PQC readings** — X-bar/R, Cp/Cpk for torque, DFT, voltage.
7. **First-article / PPAP for new parts** — supplier first-article inspection before AVL "APPROVED" (links FR-544 AVL).
8. **Customer complaint / 8D** linked to NCR/CAPA and to warranty claims (PRD §12 warranty registry).
9. **ECN impact handling** — where-used, disposition of old-revision stock and WIP (use-up / rework / scrap), effective-from by serial or date.
10. **Drawing access control / IP protection** — vendor-facing drawing issue log (which revision was sent to which job worker/vendor), retrieval of superseded copies.
11. **Golden-sample retention** — approved sample kept as reference with location and retention date.
12. **Operator skill matrix and shift master** — needed by PRD 9.2 ("only authorised operators") but absent platform-wide.
13. **Downtime / breakdown capture per work centre** — refused as OEE (R-02); minimal downtime reason logging is common SME practice.
14. **Line-rejection feedback to vendor** — PQC reject attributable to a purchased part should feed vendor rejection % (PRD only counts IQC).

### Design set covers, PRD omits (worth telling the client)
- MRP: planning parameters, demand plans/forecast, regenerative MRP with pegging, firm/convert, exception messages (FR-662..667, #602, #603).
- Line-side staging with pick lists, three supply methods incl. backflush (FR-638, FR-639, FR-645, #597).
- Co-products / by-products, phantom assemblies, alternates with priority, process-loss % (FR-623, FR-624, FR-627).
- Consumption policy STRICT/WARN/FLEXIBLE with deviation reasons (FR-643).
- Receipt reversal maker-checker; scrap-value approval threshold (FR-646, FR-649).
- Actual costing with exact co-product split, settlement capitalising residual, WIP valuation (FR-654..656).
- Subcontract reconciliation (recall / write-off), ITC-04 processed-form returns, bonded/MOOWR/SEZ production and job work (FR-658..661, FR-670..677).
- Lot genealogy forward/backward for recall (FR-648).
- Legal Metrology declarations on FG labels (FR-678).
- Capacity load per work centre (FR-668).
- Gapless numbering, concurrency/idempotency guarantees (FR-620).

## QUESTIONNAIRE dependencies

| Q | Question (short) | Slice items | Answered by design assumption? |
|---|---|---|---|
| Q-PR1 | Every order against SO, or MTS too? | 9.1-01..03 | Yes — both supported (manual / MRP / demand line, FR-633); MTS has no approval rule; R-11 refuses auto-creation from SO |
| Q-PR2 | Standard batch size; batch no. printed on vehicle/label? | 9.1-14, 9.1-25, 9.2-01 | **No** — design has no batch concept; `planned_lot_code` on output lot is the nearest |
| Q-PR3 | When is chassis assigned; which part serials bound? | 9.2-14..16, 10-41 | **No** — and MD-11 assumes the opposite (no per-unit capture) |
| Q-PR4 | Operators book own output (tablet) or supervisor? | 9.2-03..05, 9.4-06 | Assumed supervisor on web (persona "Production supervisor / shift in-charge" holds `whm_operation_confirmations:create`; R-13 no mobile) |
| Q-PR5 | Release with shortage allowed? Who approves? | 9.1-20 | Assumed: allowed with warning, no approver (`release_with_shortage=WARN`, `release_requires_approval=false`) — contradicts PRD text |
| Q-PR6 | Rework handling; per-unit rework count? | 9.2-19, 9.2-20, 10-23 | Partly — rework = separate rework order per lot (FR-653); per-unit count not assumed |
| Q-PR7 | Production costing material + labour + overhead? | 9.3-08, 13.1-P8 | Assumed material-only actual (OD-40); labour/overhead recorded, not absorbed (OD-43) |
| Q-Q1 | Which stages have PQC; share checklists | 10-03, 10-07, 10-16 | Mechanism assumed (`is_qc_checkpoint` per operation); per-stage checklist link missing |
| Q-Q2 | Current PDI checklist and certificate format | 10-14, 10-17, 10-33, 10-41 | No — no PDI certificate in design |
| Q-Q3 | Failed PQC blocks next stage or flags? | 9.2-18 | Assumed **flag** (record-only; optional receipt gate default off) — PRD text says block |
| Q-Q4 | Need NCR/CAPA? Who closes? | 10-38, 10-39, 10-45 | No — not in design |
| Q-S1 | Sample frequency and for whom | §11 all | No |
| Q-S2 | Drawing file types, numbering/revision scheme | 11-05, 11-08 | No (FR-545 stores number + revision as free text) |
| Q-S3 | Who creates/approves drawings; customer approval before sample? | 11-06, 11-07 | No |
| Q-S4 | Samples chargeable? Returned? | 11-04, 11-17, 11-27 | No (gate-pass RGP/NRGP `SAMPLE` purpose exists generically) |
| Q-S5 | Must bulk production always wait for sample approval? | 11-02, 11-25 | Partly — FR-545 `requires_part_approval` per customer profile, but gates the SO, not production |
| Q-B6 (adjacent) | BOM creator/releaser; ECN process? | 11-23 | Answered: maker-checker BOM (FR-625), ECN **refused** (R-08) — PRD now asks for ECN |

## Suggested ownership for MISSING clusters (for planning)
- **Batches + job cards + stage sequencing + WIP per stage + production board** → new P10 task(s) extending `whm_production_order_operations` to batch × operation job cards (touches FR-631/651, MD-09, QRW contract).
- **As-built serial binding + chassis series + PDI certificate** → new P10 task + base serial series; requires reversing MD-11 for serial-tracked components only.
- **NCR / CAPA / deviation (concession)** → core `warehouse` QC (P8 follow-up), since IQC, PQC and PDI share the engine.
- **Inspector segregation, photos per parameter, per-operation checklist, customer-specific PDI points, first-piece/patrol** → core QC + P10-08 #599 amendments.
- **Samples + drawings (document control) + sample order type + feedback iterations** → no module owns it; candidate: `warehouse-manufacturing` (sample order, trial BOM) + `warehouse-trade` (sample request from enquiry/SO, feedback, SO-line production gate) + a document-control capability (drawings, revisions, watermark) — decision needed (ECN refusal R-08 must be revisited).
