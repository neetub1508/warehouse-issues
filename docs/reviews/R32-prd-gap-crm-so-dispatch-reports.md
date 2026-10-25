# Gap analysis — slice `crm-so-dispatch-reports`

PRD lines 139-153 (§4A CRM before the SO), 309-319 (§12 Dispatch and Sales Invoice), 405-421 (§13.1 Sales/CRM + Traceability report rows, export rule).
Sources: warehouse-issues `docs/frd/FRD-TRADE.md` (FR-540…619, 680-681, §5 mirror table, §6 WS, §9 TRD, §10 OD, §11 refusals), contracts `trade-sales-order`, `trade-sales-enquiry-quotation`, `trade-order-amendment`, `trade-reports`, `trade-approval-matrix`, `FRD-MFG.md`, `INDIA-LOCALISATION-PACK.md`, R28 RN-050..054; issue dump (630); classic code spot-checks (warehouse, warehouse-base, warehouse-india, dealer, leads, leads-base, services, accounting, accounting-base, platform).

## Key context discovered (read first)

1. **The design's sales side lives in `warehouse-trade` (P9, #578-#591, all OPEN, no code).** SO = commercial doc in trade; execution = core demand order via `WhDemandOrderPort` (P8-02 #563, **built**: `warehouse/.../port/demand/WhDemandOrderPort.java`, `WhAvailableToPromiseQueryService`, customer PO columns in V511311).
2. **Trade deliberately refuses** credit check (§11 R1), sales invoice (R2), debit/credit notes (R3), payment/advance tracking (R4), tax computation (R5/`TRD-06`), CRM leads/opportunities (R11). Contract rows `TSO-UNR-03` ("a credit check blocking release — no such guard exists") and `TSO-UNR-04` ("an SO invoice — refused"). Justification: "accounting is deferred" (`RN-054`).
3. **But classic already has a built accounting sales chain** the warehouse design never mentions: `accounting/…/entity/AccQuotation`, `AccSalesOrder` (customer_po_number/date, source_quotation_id, invoiced_amount, close reasons), `AccDeliveryNote`, `AccInvoice` (place_of_supply, tax lines, source_document_id, amount_due), `AccCreditNote`, `AccReceipt`/advance consumption, and `AccCreditCheckService` (credit_check_mode WARN / BLOCK / APPROVE with `CREDIT_LIMIT_OVERRIDE` approval, credit hold, exposure calculator) on `AccParty.creditLimit`. Grep of warehouse-issues docs for `acc_sales_order|AccSalesOrder|AccInvoice` = 0 hits. So "accounting deferred" is stale relative to the code.
4. **Classic also has a dealer-CRM quotation** (`dealer/…/entity/Quotation`, `QuotationRevision` with valid_until, approved_by, sent_to_customer_at; statuses DRAFT, PENDING_APPROVAL, APPROVED, SENT, VIEWED, UNDER_NEGOTIATION, REVISED, ACCEPTED, CONVERTED, REJECTED, EXPIRED, CANCELLED; lead_id link; `Lead`, `LeadSource`, `WalkInEnquiry` with model/variant), and dealer customer UI with GSTIN, creditLimit, paymentTerms. `RN-054` fences dealer/services/automotive from edits.
   → There are now **three quotation implementations and three SO-like documents** (dealer quotation; accounting quotation/SO; planned trade SQ/SO + core demand order). The PRD assumes one CRM → SO → dispatch → invoice chain. Nobody owns the seam.
5. **"Tally Item Wise Sales Report import into the service registry" was not found in classic.** `services/…/ServiceVehicleBulkImportService` imports job cards (bill no/date, chassis, model/variant/colour), not Tally item-wise sales; `ServiceVehicle` has chassis/engine number but no sale date and no part serials (motor/controller/battery/charger). Watermarked quotation PDF also not found in classic dealer. The PRD's "existing CRM" may be a client-specific build outside this repo — **confirm with the client/owner**.

## Summary counts

| Status | Count |
|---|---|
| COVERED-BUILT | 8 |
| COVERED-PLANNED | 22 |
| DESIGN-ONLY | 1 |
| PARTIAL | 28 |
| DECLINED (PRD contradicts each one) | 5 |
| OTHER-MODULE | 4 |
| MISSING | 20 |
| **Total atomic requirements** | **88** |

Combined labels (12-09 "PARTIAL / OTHER-MODULE", 4A-24 "MISSING / OTHER-MODULE", 12-16 "MISSING (in classic)") are counted under the first label.

## Matrix

### §4A CRM before the Sales Order

| Id | PRD requirement (short) | Status | Evidence | Gap / note |
|---|---|---|---|---|
| 4A-01 | No SO without CRM trail (lead/customer + enquiry + approved quotation + customer PO) | PARTIAL | FR-605 (SO draft manual / from won quotation / from sales RC, `trade-sales-order` §0 Workflow); FR-599 "a quotation may have no enquiry" (§5 M5) | Design explicitly allows a manual SO and a quotation without enquiry. No mandatory-trail guard. Customer PO mandatory only via profile flag `customer_po_required` (FR-543) |
| 4A-02 | Lead sources Meta / manual / dealer (existing) | OTHER-MODULE | dealer `Lead`, `LeadSource`, `WalkInEnquiry`; leads-base `LdbLead`, leads `LdHostedFormConnector`; FRD-TRADE §11 R11 | No Meta (Facebook lead-ads) connector found in classic leads/dealer — only hosted-form connector. Confirm whether "existing CRM" is classic dealer |
| 4A-03 | Customer master: GSTIN, billing + shipping addresses | COVERED-BUILT | warehouse-base `WhbCounterparty`, `WhbCounterpartyAddress`, `WhbCounterpartyTaxRegistration` (built); FR-541 one party identity; dealer customer GSTIN | Three customer masters exist (dealer/automotive `Customer`, accounting `AccParty`, `whb_counterparties`); no sync design |
| 4A-04 | Customer master: credit limit, payment terms | PARTIAL | FR-543 payment terms "recorded only", **"No credit limit" (§11 R1)**; accounting `AccParty.creditLimit` built | Credit limit exists only on accounting party; trade profile refuses it |
| 4A-05 | Lead converts to customer account when first SO booked | MISSING | FRD-TRADE §11 R11 "Enquiry may later link a lead id"; dealer `Quotation.convertLeadToCustomer` converts at quotation, not SO | No lead → counterparty conversion anywhere in warehouse design |
| 4A-06 | Enquiry against lead OR customer | PARTIAL | FR-598 enquiry requires `customer` (counterparty) | No lead reference on enquiry; prospect without counterparty cannot raise enquiry |
| 4A-07 | Enquiry fields: product/model, variant, colour, qty, required delivery date | PARTIAL | FR-598 lines: item, customer part no, qty, UoM, required date, target price; style × variant matrix P5-20 #107 (built, warehouse-base) | Variant/colour only if modelled as separate SKUs; no model/variant/colour attributes on the enquiry line |
| 4A-08 | Special requirements + customer drawing/spec attachments | PARTIAL | FR-598 "specification note"; FR-545 drawing no + revision on customer item reference | Attachments on enquiry not specified (platform documents not wired in FR-598) |
| 4A-09 | Standard vs custom product flag | MISSING | — | Drives feasibility/costing routing; not in FR-598/599 |
| 4A-10 | Sample needed (Y/N) on enquiry | MISSING | grep "sample" in FRD-TRADE = QC sampling only | — |
| 4A-11 | Technical feasibility (feasibility, BOM availability, new drawing, tooling, lead time) for custom items | MISSING | "feasib" 0 hits in issues; only R2/R28 review prose | No `feasibility_reviews` table (PRD §13.2 lists it) |
| 4A-12 | Feasibility approved by Design Head before costing | MISSING | — | Approval engine (FR-548) has no FEASIBILITY doc type |
| 4A-13 | Costing: BOM × last purchase rate + labour/routing + overhead + margin | MISSING | MFG costing (`mfg-costing-close`) is production-order actual/standard cost, not pre-sale estimate; TRD-10 "last price is reference only" | No quotation cost sheet / margin computation. (Dealer `costsheet` service exists but is vehicle-dealer pricing, fenced by RN-054) |
| 4A-14 | Below-floor price needs Sales Manager / MD approval | COVERED-PLANNED | FR-599, FR-602 floor price, FR-604 `below_floor_price`, FR-548 condition sets; #583, #585, #580 | Approver identity is configuration (rule levels), not seeded |
| 4A-15 | Quotation Draft → Pending approval → Approved → Sent, revisions kept | COVERED-PLANNED | trade SQ FR-599/600 versions, SENT, EXPIRED (#585); existing dealer quotation built with same statuses | Duplicate implementations (dealer vs trade vs accounting `AccQuotation`) — CONFLICT C-01 |
| 4A-16 | Watermark and PDF as today | PARTIAL | FR-615 `CUSTOMER_QUOTATION` print template (#591); dealer `QuotationPdfService` | No watermark spec in trade print; watermark not found in classic dealer either |
| 4A-17 | Quotation gains validity date | COVERED-PLANNED | FR-599 `valid_until` default 30 days, FR-600 expiry job (#585) | Dealer quotation already has `valid_until` |
| 4A-18 | Quotation gains delivery period | COVERED-PLANNED | FR-599 line lead time / promised date (#585) | — |
| 4A-19 | Quotation gains payment terms | COVERED-PLANNED | FR-599 terms; T&C templates WS-311 (#579) | Terms recorded only |
| 4A-20 | Quotation links to enquiry | COVERED-PLANNED | FR-599 dispatch site defaulted from enquiry; FR-598 line outcomes (#585) | — |
| 4A-21 | Sample request → §11 before order confirmed | MISSING | no sample document in trade/MFG design | Belongs to §11 slice; here only the hook from enquiry/SO line is missing |
| 4A-22 | Customer PO no. + date | COVERED-PLANNED | FR-605 header customer PO no + date, duplicate refused (`TSO-GRD-17`) (#586); core demand order `customer_po` columns built (V511311, #563 CLOSED) | — |
| 4A-23 | Customer PO copy upload | PARTIAL | FR-545 uses platform documents for part approval; FR-605 silent on PO copy | Attachment on SO header not specified |
| 4A-24 | Advance received (amount, UTR) | MISSING (warehouse) / OTHER-MODULE | FRD-TRADE §11 R4 refuses payment tracking; accounting `AccReceipt`, `AccAdvanceTaxInvoiceConsumption` built | No link from SO to accounting advance receipt |
| 4A-25 | Acceptance check: price = approved quotation | PARTIAL | FR-601 won lines draft SO from quotation; FR-604 price resolution; amendment rules FR-590 | No guard that an SO line price differs from the won quotation (manual SO priced by FR-604 instead) |
| 4A-26 | Acceptance check: credit limit | DECLINED | FRD-TRADE §11 R1; `TSO-UNR-03` | **PRD contradicts R1.** Accounting `AccCreditCheckService` is built but only for accounting documents |
| 4A-27 | Acceptance check: overdue outstanding (from Tally) | MISSING | — | No Tally receivables import; accounting has open items (`AccOpenItem*`) if accounting becomes the ledger |
| 4A-28 | Acceptance check: stock / production availability | PARTIAL | ATP `WhAvailableToPromiseQuery` (built) shown at dispatch planning FR-607; MFG capacity infinite (#604) | ATP not evaluated at SO submit/approval; no production capacity promise |
| 4A-29 | SO created from approved quotation, lines copied | COVERED-PLANNED | FR-601 win modal drafts SO FIXED/OPEN/BLANKET with charges (#585, #586) | — |
| 4A-30 | SO header: SO no, customer, billing/shipping address, PO ref | PARTIAL | FR-547 SO number at submit (FY reset); FR-605 ship-to, customer PO | **Billing address** not on trade SO (only ship-to) |
| 4A-31 | SO line: item/model, variant, colour, qty, rate | COVERED-PLANNED | FR-605 lines (#586) | Variant/colour only as SKU (see 4A-07) |
| 4A-32 | SO line GST | DECLINED | `TRD-06` "No tax… lines carry the item's tax classification code (recorded); prints say Taxes extra as applicable" | **PRD contradicts** — PRD SO shows GST per line |
| 4A-33 | Delivery schedule per line | COVERED-PLANNED | FR-605 schedule lines FIRM/FORECAST, FR-611 customer schedule revision (#586) | — |
| 4A-34 | Dispatch mode, freight terms, special instructions | PARTIAL | FR-543/605 delivery + freight terms, notes | No dispatch-mode field (road/rail/self-pickup/transporter) |
| 4A-35 | Drawing revision for custom items on SO | PARTIAL | FR-545 customer item reference holds drawing no + revision per customer × item | Revision not frozen on the SO line; a later reference change silently re-points |
| 4A-36 | SO approval: Sales Manager | COVERED-PLANNED | FR-548 `SO` doc type, FR-549 maker ≠ checker (#580) | Who = config |
| 4A-37 | Credit-limit or price exception → Accounts / MD | PARTIAL | price exception via `below_floor_price` / `discount_over_pct` conditions (FR-548) | Credit-limit exception route absent (R1) |
| 4A-38 | On approval: stock check per line → reserve FG if available | PARTIAL | FR-605 FIXED → FIRM at approval; core allocates FIRM qty **inside horizon** `warehouse.outbound.schedule_allocation_horizon_days` (P8-02 #563 built); FORECAST (BLANKET) never reserves (FR-611); reservations P2-07 #53 REOPENED | Not "reserve at approval": far-dated FIRM lines and BLANKET lines reserve nothing. CONFLICT C-06 |
| 4A-39 | Balance → Production Order suggested (§9) | COVERED-PLANNED | MRP reads demand incl. FORECAST (MD-08, P10-12 #603); FR-637 MTO order from demand line with reserve-output (P10-05 #596); FRD-MFG R-11 no automatic creation | Suggestion is via MRP run, not an immediate per-SO suggestion at approval |
| 4A-40 | BOM shortages raise PRs (§5) | COVERED-PLANNED | MRP → `WhReplenishmentSuggestionPort.publishExternal` (P8-16 #577 CLOSED, built) → PR conversion FR-557 (P9-04 #581) | — |
| 4A-41 | Status Draft → Approved | COVERED-PLANNED | `trade-sales-order` states DRAFT, SUBMITTED, REJECTED, APPROVED, ISSUED (#586) | Extra SUBMITTED/ISSUED states |
| 4A-42 | Status In production | MISSING | no SO state or derived flag from MFG | Trade may not read `whm_`; MFG→SO progress must come via core demand line (not specified) |
| 4A-43 | Status Partly dispatched / Fully dispatched | COVERED-PLANNED | derived fulfilment NOT_STARTED / PARTIAL / COMPLETE (`TSO-T4-04`, FR-608) | Derived, not stored status |
| 4A-44 | Status Invoiced | DECLINED | §11 R2, `TSO-UNR-04` | No invoice in warehouse; no accounting feedback |
| 4A-45 | Status Closed | PARTIAL | FR-609 auto-close on shipped ≥ qty × (1 − tolerance) | Closes on shipment, PRD closes on invoice (12-21) |
| 4A-46 | Cancel / short-close with reason | COVERED-PLANNED | FR-609, `SO_CANCEL`/`SO_SHORT_CLOSE`, reason codes `TRADE_ORDER_CLOSE` (FR-546); lost-sale FR-681 (#587) | — |
| 4A-47 | Amendment (qty, date, spec) = new revision + re-approval | COVERED-PLANNED | FR-590…593 snapshot, version compare, re-ack (#588) | "Spec" change: item/type not amendable (FR-591) — only cancel line + add line |
| 4A-48 | Amendment impact shown on linked production orders | MISSING | `trade-order-amendment` has no MFG reference; MFG listens to `demand_order.amended`? not specified | No impact view; MTO order freezes SO reference (FR-637) |
| 4A-49 | Screen: Enquiry list | COVERED-PLANNED | WS-298 (#585) | — |
| 4A-50 | Screen: Feasibility queue | MISSING | — | — |
| 4A-51 | Screen: Order book (SO-wise pending vs produced vs dispatched) | PARTIAL | open SO register + dispatch backlog reports FR-619 (#591); SO detail WS-304 | "Produced" column absent (no SO↔production quantity read) |
| 4A-52 | Screen: Customer 360 (leads, quotations, SOs, samples, invoices, service claims) | MISSING | — | Spans dealer/leads/trade/accounting/services; RN-054 fence blocks reading/editing dealer & services |

### §12 Dispatch and Sales Invoice

| Id | PRD requirement (short) | Status | Evidence | Gap / note |
|---|---|---|---|---|
| 12-01 | Only PDI-passed FG units reserved to an approved SO can be dispatched | PARTIAL | core allocates only allocatable status; MTO output reserved at QC release (FR-637, MD F15); final QC P10-08 #599; demand orders from approved SO only (FR-605) | No "PDI" concept (term only in removed dealer-era docs); core ships un-reserved stock for non-trade demand |
| 12-02 | Each invoice line carries unit's chassis + part serials into warranty registry | MISSING | — | No invoice, no unit↔part serial binding (see 13.1-06) |
| 12-03 | Dispatch plan: ready SO lines, customer, transporter, vehicle, planned date | PARTIAL | FR-607 dispatch planning WS-305 + dispatch release WS-313 (#586); transporter/carrier on core shipment P2-10 #73 (built); e-way vehicle update P4-12 #82 (built) | Transporter/vehicle are not on the plan/release; "ready" = ATP not "PDI passed" |
| 12-04 | Dispatch plan approved by Dispatch In-charge | PARTIAL | `SO_RELEASE` approval through matrix, **seeded zero-level** (FR-550) | Needs a configured level; default is auto-approval by SYSTEM |
| 12-05 | Packing/loading list: units picked by chassis-no scan | PARTIAL | serial scan resolution P1-02 #20 (REOPENED); pack session as operator flow P3-07 #36 (REOPENED); picking P2-09 #65 (REOPENED); cartons/pack evidence P2-11 #79 (built) | No "loading list" document for vehicles; scan verification is config per task type |
| 12-06 | Checklist: accessories, tool kit, manuals, PDI certificate, warranty card | MISSING | pack evidence (#79) is photo/evidence, not a checklist | — |
| 12-07 | Dispatch blocked over credit limit unless Accounts/MD override with reason | DECLINED | §11 R1; `TSO-UNR-03`; #586 body "No credit check exists; do not add a placeholder guard" | **PRD contradicts.** Accounting override mechanism exists (`AccCreditCheckService` APPROVE → `CREDIT_LIMIT_OVERRIDE`) but not callable from warehouse |
| 12-08 | Dispatch blocked if advance terms unpaid | MISSING | §11 R4 | — |
| 12-09 | Sales invoice created from dispatch, never typed fresh | PARTIAL / OTHER-MODULE | warehouse §11 R2 refuses; accounting `AccInvoice` + `AccInvoiceSourceFulfilmentService` (QUOTATION→INVOICE, DELIVERY_NOTE→INVOICE, SO→INVOICE hops) built; accounting design E-01 warehouse adapter (`accounting-issues/issues/p4-01.md`) | No warehouse shipment → accounting invoice hop; `whb_accounting_handovers` envelope is stock-value only |
| 12-10 | Invoice: SO rate, GST by place of supply, HSN | OTHER-MODULE | `AccInvoice.place_of_supply`, `AccInvoiceTaxLine`; warehouse-india GST masters P4-01 #16 (built) | Rate inheritance from trade SO impossible while trade SO ≠ accounting SO |
| 12-11 | Invoice line serials: chassis, motor, controller, battery, charger | MISSING | — | — |
| 12-12 | E-way bill no. | COVERED-BUILT | `WhinEwayBill` (warehouse-india), P4-12 #82 CLOSED; lifecycle P2-IN-04 #147 REOPENED | Generated on warehouse shipment/challan, not against an accounting invoice |
| 12-13 | E-invoice IRN / QR (via GSP or Tally) | PARTIAL | warehouse-india IRN only for stock-transfer tax invoices (`WhinTransferIrnRequest`); `whin_compliance_providers` vendor-agnostic (INDIA-LOCALISATION-PACK §4.3, P-044) | No IRN for sales invoices anywhere built; accounting FR-118 says filing is an outbound adapter (design) |
| 12-14 | Invoice number series per FY | OTHER-MODULE | accounting invoice numbering; `whb_number_series` YEARLY (FR-547) is non-gapless, not for tax documents | Must be gapless per GST Rule 46 — accounting's job |
| 12-15 | Tally: export invoice (XML/Excel) or import Tally invoice back (Q-INV) | DESIGN-ONLY | accounting FRD FR-207 Tally Prime XML adapter, SC-28; accounting issue C-06 (`p2-06.md`) | No Tally code in classic; warehouse design has nothing |
| 12-16 | Existing CRM imports Tally Item Wise Sales Report into service registry | MISSING (in classic) | `ServiceVehicleBulkImportService` is a job-card import; `ServiceVehicle` lacks sale date & part serials | Not found in this repo — confirm where it lives |
| 12-17 | Gate out: gate pass against invoice | PARTIAL | outward gate entry / gate pass P8-03 #564 CLOSED (built `WhGatePass`, document types PO/ASN/SUPPLIER_BILL/OUTWARD_DOCUMENT); print P8-12 #573 OPEN | Linked to shipment/outward document, not to an invoice (invoice not a warehouse doc) |
| 12-18 | Vehicle out-time | COVERED-BUILT | `wh_gate_entries.exited_at` server-stamped (V511312, IRR-23) | — |
| 12-19 | Warranty registry: on invoice, register each vehicle in Service with sale date + part serials | MISSING | RN-054 fences `services` from edits | CONFLICT C-08; no port/event to services |
| 12-20 | Service claims trace back to PO, MRN, IQC, production batch, PDI | PARTIAL | lot genealogy built (`warehouse-base/.../ledger/genealogy/page.tsx`, `WhbTransformation*`); FR-648 production genealogy (P10-07 #598); MRN P8-08 #569 OPEN | No serial-level unit genealogy; no link from services claim to warehouse lot |
| 12-21 | SO line closes when invoiced qty = ordered qty | DECLINED | FR-609 close on shipped within tolerance; R2 | **PRD contradicts** design close rule |
| 12-22 | Order book updates on closure | COVERED-PLANNED | fulfilment derived on read (`TRD-03`), open SO register (#591) | — |
| 12-23 | Customer returns via gate entry (Customer return) | COVERED-BUILT | gate purpose `CUSTOMER_RETURN_IN` (warehouse-base V501230), gate entry #564; return receipt P2-12 #87 CLOSED | SRA → RMA authorisation planned (P9-13 #590, P8-15 #576 OPEN) |
| 12-24 | Customer return → IQC | COVERED-BUILT | QC polymorphic source P8-06 #567 CLOSED; `RETURN_RECEIPT` subject type in migrations; returns never land AVAILABLE (P2-12) | — |
| 12-25 | Customer return → credit note | OTHER-MODULE | warehouse §11 R3 refuses; SRA `CREDIT` intent = hand-over point (FR-612); accounting `AccCreditNote` built | No SRA/return → accounting credit-note hop |
| 12-26 | Return stock to Rework / FG / Scrap | COVERED-BUILT | return disposition P2-12 #87, quarantine disposition P2-13 #93 (CLOSED); SRA intent REWORK (FR-612, #590) | Rework order is MFG (`mfg-qc-rework`) |

### §13.1 Reports (Sales/CRM + Traceability rows, export rule)

| Id | PRD requirement (short) | Status | Evidence | Gap / note |
|---|---|---|---|---|
| 13.1-01 | Report: Order book | PARTIAL | `wht_rpt_open_so` open SO register (FR-619, `trade-reports`, #591) | No produced quantity |
| 13.1-02 | Report: SO pending to produce | PARTIAL | MFG registers P10-13 #604 (production/WIP by order; FR-637 SO reference frozen on MTO orders) | No SO-wise "ordered − produced" report |
| 13.1-03 | Report: SO pending to dispatch | COVERED-PLANNED | `wht_rpt_dispatch_backlog`, `wht_rpt_dispatch_adherence` (#591) | — |
| 13.1-04 | Report: Sample status | MISSING | — | §11 slice |
| 13.1-05 | Report: Enquiry-to-SO conversion | COVERED-PLANNED | `wht_rpt_quotation_hit_rate`, WS-300 win/loss (FR-601), `ENQUIRY_CONVERSION` customer-rating criterion (FR-614, #589) | Hit rate is quotation-level; enquiry→SO funnel by lead source absent (lead not linked) |
| 13.1-06 | Traceability: chassis → every part serial → batch → MRN → PO → vendor | PARTIAL | lot genealogy built; MRN #569 OPEN; FRD-MFG MD-11/MD-41 genealogy at order-receipt grain, cumulative attribution | **MD-11 rejects per-unit consumption capture** — a chassis cannot be bound to its motor/battery/controller serials. CONFLICT C-07 |
| 13.1-07 | Traceability backward: vendor batch → chassis/customers | PARTIAL | recall lists every consignee P5-14 #76 (built); genealogy forward trace | Over-inclusive at lot grain, no unit grain |
| 13.1-08 | All reports filter by date, plant, item, vendor/customer | COVERED-PLANNED | `trade-reports` §5 filters, `TRP-GRD-04` date rule (#591); core report packs P2-20 #136 (built) / P2-21 #141 (REOPENED) | Verify every PRD dimension per report when #591 is built |
| 13.1-09 | Export to Excel | COVERED-BUILT | platform `BaseExportService` (CSV/Excel), FR-616 export superset | — |
| 13.1-10 | Exports are audited | COVERED-BUILT | `BaseExportService` "tracks all exports in the export_history table for audit purposes" (line 34); platform P2-29 #154 | Auditor role never exports (design) |

## CONFLICTS (design set vs PRD)

| # | Topic | PRD says | Design set says | Evidence |
|---|---|---|---|---|
| C-01 | Who owns quotation & SO | One CRM chain: existing CRM quotation → new manufacturing SO | Trade builds its own enquiry/quotation/SO (#585/#586); classic already has dealer `Quotation` and accounting `AccQuotation`/`AccSalesOrder`/`AccInvoice` (built) — never referenced by warehouse docs | FRD-TRADE §4.10-4.12; accounting entities; RN-054 |
| C-02 | Credit-limit check at SO approval and dispatch, with Accounts/MD override | Required (4A-26, 4A-37, 12-07) | Refused (§11 R1, `TSO-UNR-03`, #586 "do not add a placeholder guard") because "accounting deferred" — yet accounting's `AccCreditCheckService` is built | RN-054 |
| C-03 | Sales invoice, credit note, invoiced status, SO closure on invoice | Invoice from dispatch; SO closes at invoiced = ordered | Refused (R2, R3, `TSO-UNR-04`); SO closes on shipment within tolerance (FR-609) | — |
| C-04 | GST on SO lines | GST per line, by place of supply | `TRD-06`: no tax on trade documents, "Taxes extra as applicable" | — |
| C-05 | SO status ladder | Draft → Approved → In production → Partly dispatched → Fully dispatched → Invoiced → Closed | DRAFT → SUBMITTED → APPROVED → ISSUED → CLOSED / SHORT_CLOSED / CANCELLED; fulfilment derived NOT_STARTED/PARTIAL/COMPLETE; no In production / Invoiced | `trade-sales-order` §1 |
| C-06 | Reservation timing | Reserve FG stock at SO approval | Allocate FIRM lines only inside `schedule_allocation_horizon_days`; FORECAST (BLANKET) never reserves | FR-605, FR-611, P8-02 |
| C-07 | Unit-level traceability | Chassis → every part serial (unit_serial_bindings in §13.2) | MD-11: per-unit consumption capture refused ("operator burden SMEs refuse"); genealogy at lot/receipt grain, cumulative (MD-41) | FRD-MFG MD-11, MD-41 |
| C-08 | Warranty registry in Service | On invoice, register vehicle + serials in Service | RN-054 scope fence: `services` not edited; no port to services | R28 RN-054 |
| C-09 | Mandatory CRM trail | No SO without lead/enquiry/approved quotation/PO | Manual SO allowed; quotation may skip enquiry; lead link refused (R11) | FR-605, §5 M5, §11 R11 |
| C-10 | Dispatch approval | Approved by Dispatch In-charge | `SO_RELEASE` seeded zero-level (auto) | FR-550 |
| C-11 | Mobile | (PRD silent; classic CLAUDE.md requires web↔mobile parity) | FRD-TRADE §11 R16: no mobile screens (user rule 2026-09-11) — not a PRD conflict, but dispatch/packing by chassis scan is a handheld task | — |

## BEYOND-PRD

**Industry gaps (neither PRD nor design covers) — Indian vehicle (EV) manufacturer selling through dealers:**
1. **Form 21 (sale certificate) / Form 22 (roadworthiness) and VAHAN manufacturer upload** of chassis/motor numbers at dispatch — mandatory for dealer registration of motor vehicles; nothing in design or PRD.
2. **Government subsidy / scheme claims** (e.g. PM E-DRIVE for EVs) need chassis-level sale + battery data per invoice — depends on 12-02/12-11.
3. **Gapless GST invoice numbering (Rule 46), IRN 24-hour cancellation window, credit-note time limit (Sec 34)** — accounting must own; no warehouse↔accounting invoice seam designed.
4. **Dealer as customer**: dealer-wise price lists/schemes/discounts, dealer credit limit, dealer stock (secondary sales) — PRD mentions dealers as lead source only.
5. **Proof of delivery / transit insurance / LR (lorry receipt) number** on dispatch and invoice.
6. **Battery EPR** (Battery Waste Management Rules 2022): warehouse-india P4-08 #55 built EPR reporting — the client PRD omits it; worth telling the client.
7. **Order-acceptance credit exposure including open SOs + un-invoiced dispatches** (exposure calc) — needs one SO owner.
8. **Customer return within warranty vs commercial return** split (warranty replacement vs credit note) — PRD treats all returns one way.

**Design covers but PRD omits (tell the client):**
- FIXED / OPEN / BLANKET SOs with customer delivery schedules, call-off dispatch releases, firm zone, CSV schedule import (FR-605, FR-607, FR-611).
- Sales rate contracts and price lists with priority + floor price, one price-resolution order (FR-602-604).
- Customer item reference / PPAP-style customer part approval with `requires_part_approval` block (FR-545).
- Regret letters, per-line win/loss with competitor + price, lost-sale capture into demand history (FR-598, FR-601, FR-680/681).
- SO acknowledgement print and re-send after amendment (FR-606).
- Delivery commitment tracking + follow-up log (FR-610); customer rating / OTIF (FR-614).
- Sales return authorisation → RMA with REPLACE / CREDIT / REWORK intent (FR-612).
- Maker ≠ checker at every level, delegation with confirmation, pending-approval alerts, My Approvals (FR-549-555).
- Duplicate customer-PO guard (`TSO-GRD-17`).

## QUESTIONNAIRE dependencies

| Q | Question (short) | Slice items | Answered by design assumption? |
|---|---|---|---|
| Q-C1 | Which products standard vs made-to-spec | 4A-09, 4A-11..13, 4A-35 | No — design has no standard/custom flag |
| Q-C2 | Feasibility + costing approval for custom; who approves | 4A-11..14, 4A-50 | Partly — below-floor approval condition exists (FR-604/548); feasibility not designed |
| Q-C3 | Customer PO mandatory? advance mandatory, how much | 4A-01, 4A-22..24 | PO: yes, per-customer flag `customer_po_required` (FR-543). Advance: refused (§11 R4) |
| Q-C4 | Credit limit + overdue check at SO approval; outstanding source (Tally) | 4A-26, 4A-27, 4A-37 | **Answered "no" by assumption** (§11 R1, accounting deferred) — PRD implies yes; also contradicts built accounting credit control |
| Q-C5 | Who approves SO; who approves price below quotation | 4A-14, 4A-36, 4A-37 | Mechanism yes (configurable matrix, `below_floor_price`, `discount_over_pct`); persons not decided |
| Q-C6 | Several delivery dates per line; amend after approval, by whom | 4A-33, 4A-47, 4A-48 | Yes by assumption: schedule lines per line (FR-605); amendment document with approval, `:amend` permission (FR-590) |
| Q-INV | Invoices made here and pushed to Tally, or in Tally and imported | 12-09..12-16, 4A-44, 12-21 | Warehouse: invoice refused (R2) → accounting. Accounting design: Tally Prime XML **export** (FR-207). Direction not decided with the client |
| Q-D1 | E-invoice IRN + e-way bill from this system; which GSP | 12-12, 12-13 | E-way: built (warehouse-india). IRN: only for transfers; provider-agnostic layer (P-044); GSP not chosen |
| Q-D2 | Dispatch documents: challan, packing list, PDI cert, warranty card, gate pass | 12-05, 12-06, 12-17 | Challan (`WhinDeliveryChallan`, built), gate pass (#564 built, print #573 open), pack/carton docs (#79). PDI certificate, warranty card: not designed |
| Q-D3 | Block dispatch on credit / unpaid advance; who overrides | 12-07, 12-08 | **Answered "no" by assumption** (`TSO-UNR-03`) — PRD says yes |
| Q-D4 | Tally version; which masters/vouchers sync | 12-15, 12-16, 4A-27 | Accounting design assumes Tally Prime XML export; masters/vouchers list not decided |
