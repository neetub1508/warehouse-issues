# Gap analysis — slice "purchase-inward"

PRD (2026-10-24) lines 154-187 (§5 Purchase, §6 Inward) + §13.1 Purchase / Stores report rows (lines 409-412).
Compared against the warehouse design set (`warehouse-issues/docs`), all 630 GitHub issues of
`neetub1508/warehouse-issues`, and spot-checks of built code in `classic/{warehouse,warehouse-base,warehouse-india}`.

Ownership after the 2026-10-22 re-target (R28 `RN-053`/`RN-054`):
- **§5 (PR, RFQ, PO, rate contract, amendment, follow-up)** = new sibling `warehouse-trade` (V550000, `wht_`),
  epic **#547 P9** — every P9 issue is OPEN, **no trade code exists** (`classic/` has no `warehouse-trade/`).
  The core PO it hands off to (`WhPurchaseOrderPort`, #562 P8-01) is built.
- **§6 (gate, GRN, IQC, MRN, put-away, rejection)** = core `warehouse`, epic **#546 P8** (part built, part open)
  on top of P1/P2 inbound already built (#105 PO, #113 receiving/GRN, #120 QC, #126 putaway, #93 supplier returns).
- **Job work** = `warehouse-manufacturing` #601 P10-10 (open) + `warehouse-india` #22 P4-02 (built) + trade subcontract PO (#584).
- **Bill booking / debit notes / Tally** = accounting (refused in warehouse, FRD-TRADE §11 R2/R3, FRD-STORES §12 row 1).

## Summary counts

| Status | Count |
|---|---|
| COVERED-BUILT | 32 |
| COVERED-PLANNED | 58 |
| DESIGN-ONLY | 0 |
| PARTIAL | 12 |
| DECLINED | 5 |
| OTHER-MODULE | 2 |
| MISSING | 18 |
| **Total atomic requirements** | **127** |

(Every trade FR is owned by an open P9 issue, so there are no DESIGN-ONLY rows. Trade items are COVERED-PLANNED
even though no trade code exists yet. The 11 conflicts, C-01 to C-11, overlap the statuses above and have their own section.)

## Matrix

Abbreviations: TPR = `contracts/trade-purchase-requisition.contract.md`, TPO = `trade-purchase-order`, TRA = `trade-rfq-award`,
TOA = `trade-order-amendment`, TRC = `trade-rate-contract`, TAM = `trade-approval-matrix`, TRP = `trade-reports`,
GTE = `gate-entry`, RQP = `receipt-qc-putaway`, IIS = `incoming-inspection-sampling`, MRA = `mrn-authorisation`,
GBM = `grn-bill-match`. FR ids: FR-540…FR-689 in `frd/FRD-TRADE.md`, FR-504…FR-539 in `frd/FRD-STORES.md`.

### §5 preamble — PO with or without PR

| Id | PRD requirement (short) | Status | Evidence | Gap / note |
|---|---|---|---|---|
| 5.0-01 | PO raised against one or more approved PRs | COVERED-PLANNED | #581 P9-04, #584 P9-07; FR-559 (workbench creates one PO from N PR lines), TPR-T1-06 | — |
| 5.0-02 | PO directly without PR, only for holders of `po:create_without_pr` | PARTIAL | TPO-T1-01 (manual create allowed for any `wht_purchase_orders:create`) | A PO can be raised without a PR, but no separate permission controls it. Missing: the `create_without_pr` verb (FR-617 verb list has none) |
| 5.0-03 | Both paths go through the same PO approval | COVERED-PLANNED | #580 P9-03; FR-548 (one approval engine, doc type `PO`) | — |

### §5.1 Purchase Requisition

| Id | PRD requirement (short) | Status | Evidence | Gap / note |
|---|---|---|---|---|
| 5.1-01 | Source: manual, any department | COVERED-PLANNED | #581; FR-556, TPR-T1-01 | — |
| 5.1-02 | Source: **auto** from BOM shortage for a production order vs free stock | PARTIAL | MRP → `WhReplenishmentSuggestionPort` origin `MRP` (#577 P8-16 built; MRP #603 P10-12 open); TPR-T1-02 *Import shortages*; TPR §6 "Automatic PR from MRP without a user — not built"; FRD-STORES §12 row 6 | Design never auto-creates a PR: a buyer has to convert the MRP suggestion. PRD says "auto" (see CONFLICTS C-03) |
| 5.1-03 | Source: **auto** from reorder level | PARTIAL | Replenishment run + suggestions built (`WhReplenishmentRunController`, `replenishment.contract.md`); conversion via TPR-T1-02 (#581) | Same as 5.1-02: the suggestion is automatic, the PR needs a person |
| 5.1-04 | Source: from a Material Requisition the store cannot fulfil | COVERED-PLANNED | Core side built: #570 P8-09 closed, `classic/warehouse/.../port/purchase/PurchaseRequisitionHandoff.java`; trade side TPR-T1-02a (#581) | Trade bean not built yet, so *Send to purchasing* is hidden until P9-04 ships |
| 5.1-05 | Header: PR no., date, department, requested by, required-by date | COVERED-PLANNED | #581; FR-556; TPR §0 fields (`pr_number` at submit, `department_id`, `requested_by`, `required_by_date`) | — |
| 5.1-06 | Purpose: Production order / SO / Maintenance / Sample / Stock | PARTIAL | TPR fields `cost_object_type` (`p8-10`: DEPARTMENT / COST_CENTRE / PRODUCTION_ORDER) + `source_code` | No PR purpose code list. Missing: SO, Sample, Stock and Maintenance as purposes (the core MR has `REQUISITION_PURPOSE`, FR-529; the PR has nothing like it) |
| 5.1-07 | Reference: Prod. order no., SO no. | PARTIAL | Production order through cost object `PRODUCTION_ORDER` (TPR §0) | A PR cannot reference an SO: no SO field, and SO is not a cost object type |
| 5.1-08 | Lines: item, qty, UoM, required date | COVERED-PLANNED | #581; FR-556; TPR §0 line fields | — |
| 5.1-09 | Line: suggested vendor | COVERED-PLANNED | `suggested_supplier_id` (TPR §0), workbench grouping FR-559 | — |
| 5.1-10 | Line: last purchase rate | COVERED-PLANNED | FR-558 / TPR-T4-04 (estimate = rate contract, else last approved PO rate, with its source stored) | Shown as the *estimated rate* plus its source, not as a separate "last purchase rate" column |
| 5.1-11 | Line: current stock | MISSING | Not in TPR §0 fields or the WS-286/287 columns | Needs a read of core availability (`WhAvailableToPromiseQuery` exists) on the PR line / workbench |
| 5.1-12 | Line: remarks | COVERED-PLANNED | `notes` (TPR §0) | — |
| 5.1-13 | Flow Draft → Submitted → **HOD approved → Purchase approved** → Open | PARTIAL | TPR §1.1 `DRAFT → SUBMITTED → APPROVED`; TAM levels are fixed users or roles (TAM-GRD-06), with an optional department in the rule match (TAM-GRD-01) | You can set up two levels, but: (a) there are no separate HOD-approved and Purchase-approved statuses (the level shows on the approval request only); (b) the approver cannot be "the HOD of the requester's department" worked out at run time, so each department needs its own rule. The core MR has `DEPARTMENT_HEAD` (#570, open bug #623); the PR has nothing like it. See C-02 |
| 5.1-14 | → Partly ordered → Fully ordered / Short-closed (reason) | COVERED-PLANNED | TPR §1.1 `PARTIALLY_ORDERED`, `ORDERED`, `CLOSED`; close-short with reason TPR-T1-09 | Has an extra `IN_RFQ` line state |
| 5.1-15 | A PR line splits across several POs; balance = approved − ordered | COVERED-PLANNED | FR-560 partial conversion, TPR-GRD-04 (row lock) | — |

### §5.2 RFQ and comparison

| Id | PRD requirement (short) | Status | Evidence | Gap / note |
|---|---|---|---|---|
| 5.2-01 | RFQ to 1–n approved vendors from PR lines | COVERED-PLANNED | #582 P9-05; FR-562 (from PR lines or manual; AVL check per invitee; `rfq.min_suppliers` default 3, else a limited-source reason) | — |
| 5.2-02 | Enter quotes | COVERED-PLANNED | FR-564 vendor quotation with versions | — |
| 5.2-03 | Comparison: rate, freight, delivery days, payment terms, last price | COVERED-PLANNED | FR-566 comparative statement (net price, landed price with header charges, lead time, payment days, MOQ, grade, last PO rate, contract rate) | — |
| 5.2-04 | Comparison: GST | DECLINED | FR-566 "landed price … **excluding tax**"; FRD-TRADE §11 R5 / `TRD-06` (no tax computation in trade) | See C-05 |
| 5.2-05 | Select vendor with reason if not L1 | COVERED-PLANNED | FR-567 (`non_l1_award` condition, reason code + note) | — |

### §5.3 Purchase Order

| Id | PRD requirement (short) | Status | Evidence | Gap / note |
|---|---|---|---|---|
| 5.3-01 | With PR: pull approved PR lines from one or many PRs, same or different departments | COVERED-PLANNED | FR-559, TPR-GRD-03 (lines must share company and deliver-to site only) | — |
| 5.3-02 | PO qty cannot exceed PR balance unless the user holds `po:exceed_pr` (tolerance % configurable) | MISSING | TPR-GRD-04 always refuses `422 TRADE_ALLOCATION_EXCEEDS_OPEN` | No override permission and no tolerance %. See C-04 |
| 5.3-03 | Without PR: only permitted users | MISSING | — (see 5.0-02) | Needs a permission and a guard on TPO-T1-01/-02 |
| 5.3-04 | Without PR: optionally only for listed categories (consumables, urgent spares) | MISSING | — | The approval matrix can match on item category (FR-548), but that changes **who approves**, not **whether the PO is allowed** |
| 5.3-05 | Without PR: reason mandatory | MISSING | — | — |
| 5.3-06 | Flagged "Direct PO" in reports | MISSING | — (no flag on `wht_purchase_orders`; not among the 8 reports of FR-619) | — |
| 5.3-07 | Vendor approved for each item | COVERED-PLANNED | #579 P9-02; FR-544 AVL (default enforcement `REFUSE`), TPO-GRD-01 | — |
| 5.3-08 | PO type Standard | COVERED-PLANNED | #584; FR-575 `FIXED`; core PO type built (#562, `WhPurchaseOrderController`) | — |
| 5.3-09 | PO type Job-work | COVERED-PLANNED | #584 subcontract service PO (FR-682…689, TPO §1.5) + #601 P10-10 | Built as a `FIXED` PO with `po_purpose = SUBCONTRACT`, not a separate type |
| 5.3-10 | PO type Service | DECLINED | FRD-TRADE §11 R8 "Service POs, capex / asset POs → assets"; TPO-UNR-09 | Only the subcontract service line is allowed. See C-06 |
| 5.3-11 | PO type Sample | MISSING | Only a line-level `is_free_of_charge` flag (FR-576, TPO-GRD-03) | No Sample type. A paid sample is a plain FIXED PO; reporting cannot tell it apart |
| 5.3-12 | PO type Rate contract / Open | COVERED-PLANNED | FR-575 `OPEN` and `BLANKET`; #583 rate contracts | — |
| 5.3-13 | Delivery schedule per line, multiple dates | COVERED-PLANNED | FR-575/579 schedule lines; core schedule lines built (#562, `WhPurchaseOrderScheduleController`) | — |
| 5.3-14 | Rate, discount | COVERED-PLANNED | FR-576 (`unit_price`, `discount_percent`, backend `net_price`) | — |
| 5.3-15 | GST (CGST/SGST or IGST by place of supply) | DECLINED | FRD-TRADE §11 R5 / `TRD-06`; FR-576 `tax_classification_code` is recorded only | No tax on the PO or its print. See C-05 |
| 5.3-16 | Freight, P&F | COVERED-PLANNED | `wht_po_charges` (TPO §0, `V550060`); charge types code list (FR-546) | Amounts are recorded, not taxed |
| 5.3-17 | Terms, payment terms | COVERED-PLANNED | FR-576 payment / delivery / freight terms; FR-584 versioned T&C templates | Payment terms are recorded only (R4) |
| 5.3-18 | Delivery address | COVERED-PLANNED | `warehouse_id` + `deliver_to_location_id` (TPO §0) | Must be one of our sites; no free-text delivery address (for example a job worker's address) |
| 5.3-19 | Attachments (drawing, spec) | MISSING | Not on `wht_purchase_orders`; core PO says "PO document attachments — not in v1" (RQP §6 line 390) | Platform documents are used only for vendor quotations (FR-564) and customer approval documents (FR-545) |
| 5.3-20 | Approval by value-based matrix | COVERED-PLANNED | #580; FR-548…FR-555 (bands, levels, maker ≠ checker, delegation, escalation, My Approvals) | No rule means refusal, never auto-approval (FR-550). Rules must be set up |
| 5.3-21 | PO number assigned on approval | COVERED-PLANNED | FR-547 "`PO`/`PA` at **submit**" | Numbered at submit, not at approval. See C-07 |
| 5.3-22 | PO PDF on company letterhead | COVERED-PLANNED | FR-615 `PURCHASE_ORDER` template; minimal default template in #584, final layout in #591 P9-14 | Letterhead is template content; the client's format is needed (Q-P8) |
| 5.3-23 | Email / WhatsApp share to vendor | DECLINED | TRA-OPEN-01 settled "print + download only in v1; channel recorded manually"; FRD-TRADE §12b line 738 "v1 sends in-app only" | See C-01 |
| 5.3-24 | Amendment: revision no. increments | COVERED-PLANNED | #588 P9-11; FR-590, FR-592 (`version_no` + 1) | — |
| 5.3-25 | Amendment: re-approval | COVERED-PLANNED | FR-553 (band on new total and absolute delta), FR-590 `PO_AMENDMENT` | — |
| 5.3-26 | Amendment: old revision kept | COVERED-PLANNED | FR-592 snapshot rows; FR-593 compare and reprint any version | — |
| 5.3-27 | Amendment cannot reduce qty below received | COVERED-PLANNED | FR-591 (new qty ≥ received + in-flight); STO-D25 | — |
| 5.3-28 | Status Draft → Pending approval → Approved → Partly received → Fully received → Closed / Short-closed | COVERED-PLANNED | TPO §1.1 `DRAFT/SUBMITTED/APPROVED/ISSUED/ACKNOWLEDGED/CLOSED/SHORT_CLOSED/CANCELLED`; fulfilment `NOT_STARTED/PARTIAL/COMPLETE` derived (FR-581) | Partly / fully received is a derived column, not a status. Issued and Acknowledged are extra statuses |
| 5.3-29 | Over-receipt tolerance configurable % per item / category | PARTIAL | Core ladder PO line → header → item × site → site built (#105, #113; `V500050` item-site settings; FR-520); trade passes the line % (FR-582) | No **category** level in the ladder |
| 5.3-30 | Rate contract: price fixed for a period | COVERED-PLANNED | #583 P9-06; FR-570…574 (validity, slabs, ceiling, dated revisions, `EXCLUDE` overlap) | — |
| 5.3-31 | Release orders against the rate contract | COVERED-PLANNED | FR-578/580 OPEN/BLANKET releases priced from the RC (TRC-T4-02/03); #584 | The release is raised on an OPEN/BLANKET **PO** that cites the RC, not on the RC itself |
| 5.3-32 | Job-work PO: material sent out on a returnable challan | COVERED-PLANNED | #601 P10-10 (subcontract dispatch + RGP, `gate_pass_id`); India delivery challan built (#22 P4-02 closed, `WhinDeliveryChallanController`); RGP built (#564 P8-03) | — |
| 5.3-33 | Job-work: received back as processed goods | COVERED-PLANNED | #601 (processed-item receipt); TPO-T1-18 service confirmation lands the charge | — |
| 5.3-34 | Job-work: tracks material lying with the vendor | COVERED-PLANNED | #601 `whm_subcontract_reconciliations` (sent / consumed / open); India challan clock + ITC-04 built (#22, `WhinItc04ReturnController`) | — |

### §5.4 Vendor follow-up

| Id | PRD requirement (short) | Status | Evidence | Gap / note |
|---|---|---|---|---|
| 5.4-01 | Pending PO list by due date | COVERED-PLANNED | #587 P9-10; FR-587; TPO §5.4 WS-295 (sort `delivery_date ASC`) | — |
| 5.4-02 | Overdue highlighted | COVERED-PLANNED | TPO-T3-02 `overdue` filter and tile | — |
| 5.4-03 | Vendor-wise pending | COVERED-PLANNED | WS-295 `supplierId` filter; open PO register (TRP, #591) | — |
| 5.4-04 | Expected arrivals for the week | COVERED-PLANNED | WS-295 `dueSoon` = `warehouse.trade.expedite.days_before` (default 3) | Set it to 7 for a "week" view. There is no calendar-week bucket |

### §6 preamble

| Id | PRD requirement (short) | Status | Evidence | Gap / note |
|---|---|---|---|---|
| 6.0-01 | Material is usable only after IQC pass **and** an approved MRN; until then it sits in quarantine and cannot be issued | COVERED-PLANNED | QC_HOLD is non-allocatable (built, #120/#566/#567); `MRN_PENDING` + MRA-GRD-06/08 (#569 P8-08 open) | The MRN half is not built: there is no `wh_material_receipt_notes` in `classic/` migrations |

### §6 Gate Entry

| Id | PRD requirement (short) | Status | Evidence | Gap / note |
|---|---|---|---|---|
| 6.1-01 | Vehicle no., driver, transporter, LR no. | COVERED-BUILT | #564 P8-03 closed; FR-507; `WhGateEntry.java` | Driver mobile and security officer are captured too |
| 6.1-02 | Vendor, vendor invoice / challan no. + date | COVERED-BUILT | FR-508 bill type / no / date / amount / e-way bill no. (`wh_gate_entry_documents`) | — |
| 6.1-03 | PO no. (one or more) | COVERED-BUILT | FR-508, GTE-GRD-01/01a (matches core or trade PO number) | — |
| 6.1-04 | No. of packages | MISSING | Not in FR-507/508, GTE fields, or `WhGateEntry.java` | — |
| 6.1-05 | Gross weight | COVERED-BUILT | FR-510 weighment link (`wh_weighing_records`, #564 + P5-17) + bill weight; variance raises a case | Gross weight is a weighing record, not a plain field |
| 6.1-06 | In-time | COVERED-BUILT | `entered_at` server-stamped (IRR-23) | — |
| 6.1-07 | Photo of invoice and vehicle | MISSING | No attachment or photo on gate entry (GTE contract; entity) | See C-08 (attachments are declined throughout inbound) |
| 6.1-08 | Inward types: Against PO, Job-work return, Customer return, Returnable (our material back) | COVERED-BUILT | `GATE_PURPOSE` `PURCHASE_RECEIPT`, `JOB_WORK_IN`, `CUSTOMER_RETURN_IN`, `RETURNABLE_IN` (FR-507; seed `V501230`) | — |
| 6.1-09 | Inward type Non-PO (samples, free-of-cost) | PARTIAL | Purpose `OTHER` only; blind / non-PO GRN exists (RQP, `V510014`) | No `SAMPLE` / `FREE_OF_COST` purpose. The code list can be extended per install |
| 6.1-10 | Gate entry without PO only for non-PO types | COVERED-BUILT | GTE-GRD-03a (`warehouse.gate.purchase_documents_required`, default true) | Open follow-up #626 (validation / flag gaps from P8-03) |
| 6.1-11 | Gate pass number generated | COVERED-BUILT | Gapless `GE` series per site (GTE-T1-01) | The PRD's inward "gate pass number" is our gate-entry number; our "gate pass" is the outward RGP / NRGP |
| 6.1-12 | Out-time recorded when the vehicle leaves | COVERED-BUILT | GTE-T1-05 `exited_at` (+ boom-barrier EXIT proposal) | — |

### §6 Stock Inward / GRN

| Id | PRD requirement (short) | Status | Evidence | Gap / note |
|---|---|---|---|---|
| 6.2-01 | Against the gate entry, pick PO lines | COVERED-BUILT | GTE-T1-04 session from gate entry (#564); GRN against PO lines (#113 P1-13, `WhGoodsReceiptController`) | — |
| 6.2-02 | Invoice qty | COVERED-PLANNED | #565 P8-04 open; FR-517 `supplier_billed_quantity` | — |
| 6.2-03 | Received qty (counted) | COVERED-BUILT | #113; blind receipt supported | — |
| 6.2-04 | Short / excess | COVERED-PLANNED | Short / over vs PO built (#113); bill short → `SHORT_SHIPMENT` claim and excess approval / refusal planned in #565 (FR-519/520, GBM §1.5) | — |
| 6.2-05 | Damaged qty | COVERED-BUILT | Dock-rejected `rejected_quantity` + `condition_code` / `damage_notes` (RQP-T1-08) | — |
| 6.2-06 | Batch / lot no., mfg / expiry date | COVERED-BUILT | RQP-T1-08 (lot, expiry), lot control policy RQP-GRD-03; lot manufacture date (#573 label data) | — |
| 6.2-07 | Serial nos. by scan for serial-tracked items | COVERED-BUILT | `wh_goods_receipt_line_serials`, serial policy RQP-GRD-03/04; scan resolution (#311/#314 closed) | — |
| 6.2-08 | Serial nos. by **import** (vendor's Excel list) | MISSING | No GRN serial import (only opening-stock import, `WhOpeningStockImportHandler`) | Important for battery / motor / controller / charger lots of hundreds of serials (Q-I5) |
| 6.2-09 | Received qty goes to Quarantine (QC Hold) store | COVERED-BUILT | Received status resolved to `QC_HOLD` by plan assignment (RQP-GRD-07a, #566) | A stock **status** at the receiving location, not a separate store. See C-09 |
| 6.2-10 | QC required = No → straight to MRN | COVERED-PLANNED | `NO_INSPECTION` assignment built (#566 P8-05, FR-523); the routing to `MRN_PENDING` is MRA-T4-01 (#569) | — |

### §6 IQC

| Id | PRD requirement (short) | Status | Evidence | Gap / note |
|---|---|---|---|---|
| 6.3-01 | IQC auto-raised for every GRN line needing QC | PARTIAL | QC-held stock + ageing tile IIS-T3-01 (`inspection_due_hours`); inspection started by the inspector (RQP-T1-16) | No inspection document or worklist row is created at GRN post. The inspector finds the work from the QC-held tile |
| 6.3-02 | Sample size (AQL plan) | COVERED-BUILT | #566 P8-05 (band tables, FIXED / PERCENTAGE, Z1.4 `AQL_TABLE`), #120; `WhSamplingSchemeController` | Client band table seeded as `CLIENT-DEFAULT` (OD-25) |
| 6.3-03 | Each parameter's reading vs spec, pass / fail | COVERED-BUILT | #120 P1-14 typed criterion results (`WhQualityInspectionResult` text / number / boolean), RQP-GRD-15 | — |
| 6.3-04 | Photos | MISSING | No attachment on `wh_quality_inspections` / lines | — |
| 6.3-05 | Test certificate (COA) from vendor | MISSING | Not modelled (FRD-MFG R-10 refuses only CoA **generation**) | — |
| 6.3-06 | Result per line: accepted qty, rejected qty | COVERED-BUILT | Dispositions `RESTOCK_SELLABLE` / `REJECT` / `RTV` / `SCRAP` per line (RQP-T1-20…23), lot verdict (IIS-T1-08/09) | — |
| 6.3-07 | Accepted under deviation, approved by QC Manager / Plant Head with reason | PARTIAL | IIS-T1-09: releasing against a `REJECT_LOT` verdict ("MRB use-as-is") is allowed with a mandatory reason | No deviation outcome, no second-person approval, no approver level. Only scrap has an approval (RQP-GRD-19) |
| 6.3-08 | Serial-tracked items inspected per serial | MISSING | Inspection lines carry no serial (`WhQualityInspectionLine` / `Result`) | — |

### §6 MRN

| Id | PRD requirement (short) | Status | Evidence | Gap / note |
|---|---|---|---|---|
| 6.4-01 | MRN created from IQC result (or from GRN for non-QC items) | COVERED-PLANNED | #569 P8-08; MRA-T1-01 (prepared from a posted GRN, per line with pending qty) | — |
| 6.4-02 | Shows PO rate, accepted qty, value | COVERED-PLANNED | MRA-T1-01 (billed / received / accepted / rejected, PO rate and value); #573 MRN print | Value shown only to view-cost holders |
| 6.4-03 | Store Manager approves | COVERED-PLANNED | MRA-T1-03 `:authorise`, ≠ maker (MRA-GRD-03), ≠ releasing inspector by default (MRA-GRD-04) | Gated by permission, not by a named role |
| 6.4-04 | On approval accepted qty moves Quarantine → Main store, becomes free stock | COVERED-PLANNED | MRA-T4-02 `STATUS_CHANGE MRN_PENDING → AVAILABLE`, then the putaway task | A status change; the move to the bin follows by putaway. See C-09 |
| 6.4-05 | MRN is the document Purchase / Accounts use for bill booking | OTHER-MODULE | Accounting AP (`accounting-issues/issues/p1-06.md` B-06 bills / debit notes); warehouse adapter `p4-01.md` E-01; warehouse handover points FRD-STORES §8 / `whb_accounting_handovers` | Warehouse never books the bill (FRD-STORES §12 row 1, `RN-054`) |
| 6.4-06 | MRN export to Tally | OTHER-MODULE | Accounting `p2-06.md` C-06 export adapters (Tally named in accounting FRD line 87) | No warehouse-side Tally export of MRNs. Answer depends on Q-I6 / Q-INV |
| 6.4-07 | MRN on / off (implicit: PRD makes MRN mandatory) | COVERED-PLANNED | `warehouse.stores.mrn_required` per site; default on for `PRODUCTION_STORE` (OD-26 resolved) | Make sure the client's sites are `PRODUCTION_STORE` or switch it on |

### §6 Store Inward / Put-away

| Id | PRD requirement (short) | Status | Evidence | Gap / note |
|---|---|---|---|---|
| 6.5-01 | Store keeper assigns bin / rack | COVERED-BUILT | #126 P1-15 putaway rules + tasks (suggested location, override reason); `WhPutawayTaskController` | — |
| 6.5-02 | Labels with item, batch, serial, QR / barcode | COVERED-BUILT | #100 P2-14 printing, #41 P3-08 print server; TEP-GRD-06 item / LPN / location labels | Default symbology is Code-128 (OD-17); QR is a template choice |
| 6.5-03 | Label carries MRN no. | MISSING | Label data contracts (`WhPrintBuiltInDataProvider`, #573 scope) have no MRN binding | Small template / data-contract addition once #569 exists |
| 6.5-04 | Stock ledger updated | COVERED-BUILT | P0 single movement writer (#3 epic, `movement-post-reverse.contract.md`) | — |

### §6 Rejections / purchase return

| Id | PRD requirement (short) | Status | Evidence | Gap / note |
|---|---|---|---|---|
| 6.6-01 | Rejected qty moves to the Rejected store | COVERED-BUILT | `REJECT` disposition → status `REJECTED` (RQP-T1-21) | A status, not a store (C-09) |
| 6.6-02 | A Rejection Note is generated | MISSING | No rejection-note document or print (not in #573's kinds, not in FR-538) | The supplier return (DRAFT) and the claim stand in for it |
| 6.6-03 | Debit Note request generated against the vendor | DECLINED | FRD-TRADE §11 R3; FR-519/526 "no debit note is generated"; `RN-031`, `RN-054`. Handover: `QUALITY_REJECT` supplier claim (#123 P5-23 built) | See C-10 |
| 6.6-04 | Material goes back on a Returnable / Non-returnable gate pass (purchase return) | COVERED-BUILT | Supplier return built (#93 P2-13, `WhSupplierReturnController`); outward gate entry / gate pass link (`SUPPLIER_RETURN` resolver, #564); *Raise supplier return* from QC = #568 P8-07 (open) | The one-press action from QC is planned. Today the return is created by hand |
| 6.6-05 | Replacement received later as a new gate entry against the same PO | COVERED-PLANNED | Supplier return intent `REPLACE` (#576 P8-15); trade reinstates PO qty by system amendment (TPO-T4-07, FR-613, #590 P9-13) | Without trade (core-only install) nothing reinstates the quantity |

### §6 Controls

| Id | PRD requirement (short) | Status | Evidence | Gap / note |
|---|---|---|---|---|
| 6.7-01 | Cannot receive more than PO balance + tolerance | COVERED-BUILT | Core over-receipt guard (#113, RQP-GRD-06; CONFIG-CASE-14) | #565 adds "accept above tolerance with a second person's approval, else refuse" (FR-520) |
| 6.7-02 | Cannot receive against an unapproved or closed PO | COVERED-BUILT | RQP-GRD-28; GTE-GRD-01 | — |
| 6.7-03 | Duplicate vendor invoice no. for the same vendor blocked | COVERED-PLANNED | #565; FR-516 `409 SUPPLIER_BILL_DUPLICATE` (same supplier and financial year) | Not in code yet (grep `SUPPLIER_BILL_DUPLICATE` in `classic/` finds nothing). Blocked only per financial year, not for ever |
| 6.7-04 | IQC cannot be done by the person who made the GRN | MISSING | No such guard in RQP / IIS. The only segregation is MRN authoriser ≠ inspector (MRA-GRD-04) | — |
| 6.7-05 | Every movement writes the stock ledger with doc no., batch, serial, store, user, time | COVERED-BUILT | P0 ledger (`whb_stock_movements`, source_document_*, lot, serial, location, user, timestamps) | — |

### §13.1 Reports — Purchase

| Id | PRD requirement (short) | Status | Evidence | Gap / note |
|---|---|---|---|---|
| 13.1-P1 | PR pending | COVERED-PLANNED | #591 P9-14 PR ageing report (TRP); WS-286 tiles / WS-287 workbench (#581) | — |
| 13.1-P2 | PR-to-PO ageing | PARTIAL | TRP `wht_rpt_pr_ageing` (age of **open** approved lines) | No PR approval → PO lead time for lines already converted |
| 13.1-P3 | PO pending / overdue by vendor | COVERED-PLANNED | TRP open PO register (overdue tile, `supplierId`); WS-295 expediting (#587) | — |
| 13.1-P4 | Direct POs (without PR) | MISSING | — (FR-619 has 8 reports, none for this; no flag, see 5.3-06) | — |
| 13.1-P5 | Price history | PARTIAL | Rate-contract price history tab (TRC §5, #583); last PO rate on the CS (FR-566) | No price-history report per item / vendor across POs |
| 13.1-P6 | Vendor rating (delivery, rejection %) | COVERED-PLANNED | #589 P9-12 (FR-594 `DELIVERY_OTIF`, `QUALITY_ACCEPTANCE`, …); receipt facts #112 P6-05 | — |

### §13.1 Reports — Stores

| Id | PRD requirement (short) | Status | Evidence | Gap / note |
|---|---|---|---|---|
| 13.1-S1 | Stock ledger | COVERED-BUILT | `WhMovementRegisterController` | — |
| 13.1-S2 | Stock by store / bin / batch | COVERED-BUILT | `WhStockOnHandController` | — |
| 13.1-S3 | Ageing | COVERED-BUILT | `WhStockAgeingController` | — |
| 13.1-S4 | Quarantine stock | COVERED-BUILT | Stock on hand by status (QC_HOLD / QUARANTINE / REJECTED); QC-held ageing tile IIS-T3-01 | MRN_PENDING joins it with #569 |
| 13.1-S5 | Reorder alerts | COVERED-BUILT | `WhLowStockController`, replenishment run, `WhbAlertRule` | — |
| 13.1-S6 | MR pending | COVERED-BUILT | Requisition issue queue (#570, `WhRequisitionIssueQueueController`) | Register tab *requisitions pending issue* planned in #574 P8-13 |
| 13.1-S7 | Issue vs. BOM | COVERED-PLANNED | Production-order components tab required / issued / consumed (#596 P10-05, #597 P10-06); consumption register #604; cost sheet #600 | Exists only with `warehouse-manufacturing` |
| 13.1-S8 | Returns | COVERED-PLANNED | Supplier returns built (#93); store returns #572 P8-11 + register #574 | — |

## CONFLICTS (design says something different from the PRD)

| # | Topic | PRD | Design set | Source | Recommendation |
|---|---|---|---|---|---|
| C-01 | PO / RFQ to the vendor | Email / WhatsApp share from the system | v1 is print + download only; channel recorded by hand; notifications are in-app only | TRA-OPEN-01 (R31); FRD-TRADE §12b line 738 | Ask Q-P8. The platform has a functional Twilio WhatsApp provider (memory: `reference_twilio_whatsapp_provider_is_functional`), so the decision can be reversed cheaply |
| C-02 | PR approval ladder | HOD approved → Purchase approved as statuses; HOD of the requester's department | One `APPROVED`; levels are fixed users / roles per rule; department is only a rule-match key | TPR §1.1; TAM-GRD-01/06 | Add a "department head of the document's department" level member type to TAM (the MR already has `DEPARTMENT_HEAD`, #570) |
| C-03 | Auto PR | "Auto from shortage / reorder level" | Never automatic: a suggestion is converted by a buyer | TPR §6; FRD-STORES §12 row 6; `TRD-09` | Confirm with the client. A scheduled "auto-draft PR (DRAFT, maker = service principal)" keeps the buyer in the loop and closes the gap |
| C-04 | PO above PR balance | Allowed with `po:exceed_pr` up to a tolerance % | Hard refusal `TRADE_ALLOCATION_EXCEEDS_OPEN` | TPR-GRD-04 | Add a permission + setting `pr.over_allocation_pct` |
| C-05 | GST on PO / comparison | CGST/SGST or IGST by place of supply on the PO; GST in the comparison | Trade computes no tax (R5, `TRD-06`); landed price excludes tax | FRD-TRADE §11 R5; FR-566 | High impact for an Indian buyer. The print needs at least the tax head, rate and amount. Option: a `warehouse-india` tax-preview bean using `WhinHsnTaxMaster` + `WhinGstStateCode` (both built) |
| C-06 | PO types | Standard, Job-work, Service, Sample, Rate contract / Open | FIXED / OPEN / BLANKET + `SUBCONTRACT` purpose; Service refused (R8 → assets); no Sample | FR-575; FRD-TRADE §11 R8, R9 | Ask Q-P6; a non-stock service line (AMC, calibration, testing) is common in a plant |
| C-07 | PO numbering | Number on approval | Number at submit | FR-547 | Minor. Submit-time numbering leaves gaps (the series is non-gapless). Confirm with the client |
| C-08 | Attachments on gate / GRN / IQC / PO | Photo of invoice and vehicle, IQC photos, COA, PO drawing / spec | PO and GRN documents "not in v1"; nothing on gate or inspection | RQP §6 lines 390-391 | Re-open: platform document storage exists (FR-545 / FR-564 already use it) |
| C-09 | Quarantine / Rejected / Main as **stores** | Separate stores; MRN moves stock Quarantine → Main | Stock **statuses** (`QC_HOLD`, `MRN_PENDING`, `REJECTED`, `AVAILABLE`) at a location; putaway moves to the bin | FR-527; RQP-T1-20/21 | Same control, different model. Explain to the client; a status-filtered stock view gives the same "store" reports |
| C-10 | Debit note | Rejection Note / Debit Note request generated against the vendor | Never generated in warehouse; supplier claim `QUALITY_REJECT` and supplier return are the handover points | FRD-TRADE §11 R3; FR-519, FR-526; `RN-054` | Decide the debit-note owner: accounting B-06 (`accounting-issues/issues/p1-06.md`) consuming the claim through E-01 |
| C-11 | Direct-PO governance | Permission, category list, mandatory reason, "Direct PO" flag | Any `:create` holder may raise a PO with no PR, unflagged | TPO-T1-01 | Add all four (5.3-03…06, 13.1-P4) |

## BEYOND-PRD

### Industry gaps — neither the PRD nor the design covers them (Indian EV / auto-component manufacturer)

1. **Import purchases** (bill of entry, customs duty, IGST on import, landed cost from the BoE): refused (FRD-TRADE §11 R17). EV makers import cells, BMS and controllers, so this is likely material. Ask the client.
2. **GRN against the vendor's e-invoice**: IRN / QR validation of the supplier invoice and a GSTIN check against the PO supplier at the gate. Only the e-way bill number is captured (#147 P2-IN-04 handles the e-way bill lifecycle).
3. **New-part / new-vendor first-article inspection and PPAP on the purchase side**: FR-545 has PPAP for the **customer** side only. No supplier PPAP or FAI status that blocks a GRN.
4. **Shelf-life retest for cells** (periodic re-inspection before expiry): the `PERIODIC` inspection stage exists (FR-525), but nothing schedules it.
5. **Hazmat storage segregation for lithium batteries** (UN3480 class 9) at putaway: hazard labels are built (#311 follow-up); a putaway compatibility rule is not designed.
6. **Vendor-supplied serial list matched at GRN** (expected serials pre-loaded from the vendor's ASN / Excel and checked at scan): related to 6.2-08.
7. **RCM (reverse charge) and TDS on purchases**: accounting / India, not designed in this slice.
8. **Capex / asset POs**: refused here (R8 → assets). Confirm the assets module will raise them, since plants buy dies, moulds and fixtures.

### Covered by the design but not in the PRD (worth telling the client)

- MSME / Udyam on the supplier profile, with a 45-day payment-terms acknowledgement on the PO (FR-542, TPO-GRD-01).
- Approved vendor list with WARN / REFUSE enforcement and maker-checker on AVL changes (FR-544).
- Sealed-bid RFQ mode, minimum-supplier rule, limited-source reason (FR-562, FR-565).
- Supplier acknowledgement with changes → auto-drafted amendment (FR-586); BLANKET schedule release proposals and "release overdue" (TPO-T3-01/06).
- Receipt reversal as a document (#129); weighbridge vs bill-weight variance case (FR-510).
- Excess-over-bill and short-shipment claims as a decision centre (FR-519/520, #123); three-way quantity match (P5-10, `WhThreeWayMatchController`).
- Landed cost with apportionment basis on the receipt (#125 P2-17).
- Destructive-test quantity posted as QC consumption (FR-524); Ac/Re lot verdict (FR-524); per item × supplier `NO_INSPECTION` skip (FR-523).
- RGP / NRGP gate passes with overdue clock and partial returns (FR-512…515).
- Stores performance KPIs: gate → GRN, GRN → MRN, QC lead time, dock-to-stock (#574 P8-13).
- Concurrency / idempotency so a double-clicked approve creates one PO (FR-618).

## QUESTIONNAIRE (PRD §14) dependencies

| Q | Question (short) | Affects | Already answered by assumption in the design? |
|---|---|---|---|
| Q-P1 | Which departments raise PRs; who approves (HOD, Purchase, Plant Head) | 5.1-01, 5.1-13, 5.0-03 | **No.** Matrix is configurable; FR-550 refuses with no rule, so rules must be set up per install. No dynamic HOD level (C-02) |
| Q-P2 | When is a PO without PR allowed, which items / users | 5.0-02, 5.3-03…06 | **No.** Design assumes unrestricted manual PO (C-11) |
| Q-P3 | PO approval levels and ₹ limits | 5.3-20 | **No.** Value bands are data per install (FR-548); only zero-level system rules for `PO_CANCEL` / `PO_SHORT_CLOSE` / `PO_RELEASE` are seeded |
| Q-P4 | RFQ used? Minimum quotes | 5.2-* | **Yes, by default:** `warehouse.trade.rfq.min_suppliers = 3` with a limited-source override (FR-562); RFQ is optional (PO can be created directly) |
| Q-P5 | Over-receipt tolerance %, per item or one rule | 5.3-29, 6.7-01 | **Partly.** Ladder line → header → item × site → site, default 0 (CONFIG-CASE-14); category level missing |
| Q-P6 | Rate contracts / open POs, job-work POs, service POs | 5.3-09…12, 5.3-30…34 | **Partly.** RC, OPEN, BLANKET and subcontract PO designed; service PO refused (R8), sample PO absent (C-06) |
| Q-P7 | Approved vendor list per item; approved make | 5.3-07 | **AVL yes** (FR-544, default `REFUSE`). **Approved make: not designed** (only a manufacturer-part-number alias, `item-master` ITM-GRD-10) |
| Q-P8 | Email / WhatsApp PO; print format | 5.3-22, 5.3-23 | **Answered "no" by assumption** (TRA-OPEN-01: print + download only) — conflicts with the PRD (C-01). Print format pending (#591) |
| Q-I1 | What security records; photos | 6.1-* | **Partly.** FR-507/508 field set fixed; photos and package count not designed (6.1-04, 6.1-07) |
| Q-I2 | Which items need IQC | 6.2-09/10, 6.3-01 | **Config, not assumption:** plan assignments incl. `NO_INSPECTION` (FR-523), category default plan |
| Q-I3 | IQC checklists and AQL plans | 6.3-02/03 | **Yes, by assumption:** OD-25 — the client's band table read as contiguous, seeded `CLIENT-DEFAULT` with a third band `10001+ → 32` *to confirm* |
| Q-I4 | Who approves "accept under deviation" | 6.3-07 | **No.** Not designed (release against verdict needs only a reason) |
| Q-I5 | Batch / serial-tracked items; vendor serial lists in Excel | 6.2-06…08, 6.3-08 | **Partly.** Item control policy is data; Excel serial import and per-serial IQC not designed |
| Q-I6 | Is MRN the bill-booking document; MRN to Tally automatically | 6.4-05/06 | **Partly.** OD-26: MRN on by default for `PRODUCTION_STORE` sites (resolved 2026-10-23); bill booking deferred to accounting (`RN-054`); Tally path is accounting C-06 |
| Q-I7 | How rejections return to vendors (debit note, RGP) | 6.6-* | **Answered by decision:** supplier return + gate pass, no debit note ever generated (R3, `RN-031`, `RN-054`) — conflicts with the PRD (C-10) |
| Q-I8 | Bin / rack location needed or store-level enough | 6.5-01 | **Design supports both** (locations with bins, putaway rules); nothing to decide in code |
| Q-INV | Tally import / export (referenced from §6 MRN) | 6.4-06 | **No** — open in accounting |
