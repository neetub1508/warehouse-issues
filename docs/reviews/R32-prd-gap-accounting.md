# Gap analysis — PRD §12A Accounting (lines 320–404) vs accounting + warehouse design sets

Slice: PRD §12A.0–12A.11 (every voucher type, field, status, match rule, statutory row, Tally export).
Date: 2026-10-25. Read-only analysis; no repo edited.

## Sources and how to read the evidence column

| Tag | Source |
|---|---|
| `acc#N` | GitHub issue N of **`neetub1508/accounting`** (184 issues: 103 closed, 81 open; dumped to `S/acc-issues.json`, `S/acc-issues-titles.tsv`, `S/acc-issues-full.md`). **`neetub1508/accounting-issues` does not resolve on GitHub** (`gh`: "Could not resolve to a Repository"). Its local clone `workspace/accounting-issues/` is the **superseded v1 design set** (memory `reference_accounting_prior_set_status`), so it is not used as evidence. The authoritative accounting design set is the local clone `workspace/accounting/` (`docs/`, `issues/`). |
| `aFR-nnn` | `workspace/accounting/docs/ACCOUNTING-FUNCTIONAL-REQUIREMENTS.md` |
| `wh#N` / `FR-nnn` | warehouse-issues GitHub issue / `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` + `frd/FRD-*.md` FR ids |
| `AHO-*`, `GBM-*` | warehouse `contracts/accounting-handover.contract.md`, `contracts/grn-bill-match.contract.md` |
| built | spot-check of `classic/accounting*/` (migrations `V6100xx`/`V6105xx`, controllers, `page.tsx`) and `classic/warehouse*/` |

**Status column.** Almost every row is `OTHER-MODULE` (owned by accounting, not warehouse), as the brief expected. The
useful information is **how accounting itself covers the row**, so `OTHER-MODULE` carries a second label:
`acc:BUILT` (a closed acc issue, code in `classic/accounting*`), `acc:PLANNED` (an open acc issue owns it),
`acc:DESIGN-ONLY` (an aFR row, no issue), `acc:PARTIAL`, `acc:DECLINED` (explicitly refused or deferred in the acc set), `acc:MISSING`.
A row needing a **warehouse ↔ accounting seam** is labelled `SEAM-…` because neither set owns both halves of it.

## Summary counts

160 atomic requirements (plus one cross-reference row, 12A.1-08 → 12A.7-05). The count script groups by the first label.

| Status | Count |
|---|---|
| OTHER-MODULE · acc:BUILT | 48 |
| OTHER-MODULE · acc:PLANNED | 57 |
| OTHER-MODULE · acc:PARTIAL | 26 |
| OTHER-MODULE · acc:DESIGN-ONLY | 2 |
| OTHER-MODULE · acc:DECLINED | 4 |
| OTHER-MODULE · acc:MISSING | 10 |
| SEAM — PARTIAL (warehouse half designed or built, accounting consumer missing) | 11 |
| SEAM — MISSING | 2 |
| **Total** | **160** |

Of the 160, **53 (PARTIAL + MISSING + DECLINED + DESIGN-ONLY + SEAM)** are real gaps against the PRD. Warehouse itself owns
nothing in this slice beyond the handover points (`RN-054`, `D-16`: *accounting deferred, warehouse never
generates a debit or credit note*).

## Answers to the three key questions

1. **Is a purchase invoice booked against MRN (three-way PO × MRN × invoice)?** **No — not anywhere end to end.**
   - Accounting books a **bill** against **its own** `acc_goods_receipts` (V610133: `DRAFT`/`POSTED`, `quantity` only — **no accepted/rejected qty, no QC, no MRN**), through bill-line × receipt-line allocations (`V610581`, ACR-006, acc#26/#29 closed, acc#118/#119/#123 open). A bill **may be booked without a PO or receipt**. The match is **two-way** (aFR-237, PO tolerance columns `quantity_tolerance_percent`/`price_tolerance_percent`/`value_tolerance_amount` in V610132), and **three-way match is explicitly out of scope for v1** (aFR §10).
   - Warehouse has a **built commercial three-way match** (`wh_three_way_matches` + allocations, V510201, wh#58 P5-10 closed): invoice line × GRN line × PO line with quantity, amount, price variance, tolerance and approval. It records a supplier invoice **reference only**. It books no payable, and the design says *"the value leg belongs to accounting"*. It allocates against **GRN** lines. Nothing states MRN accepted quantity as the comparand.
   - The MRN (FR-527, wh#569 P8-08 **open**) emits `material_receipt_note.authorised` *"with bill fields"* for *"GRNI accrual, bill matching"* (FRD-STORES §8). **No accounting task consumes it**, and the adapter has no home (wh#174).
2. **Item-wise debit/credit notes with stock effect?** **Item-wise yes, stock effect no.**
   - `acc_debit_note_lines` carry `bill_line_id, item_id, uom, quantity` and `acc_credit_note_lines` carry `invoice_line_id, item_id, quantity` (built, acc#29/#27 closed). But neither moves stock, because accounting has no stock engine yet (acc#54 P3-02 open).
   - The physical half is warehouse's: supplier return (FR-526, wh#93 closed, wh#568 open), the `SHORT_SHIPMENT`/`QUALITY_REJECT` supplier claim (FR-519, wh#123 closed), and the SRA `CREDIT` intent (FRD-TRADE R3). Each is recorded only as a *"debit-note candidate"* handover point. **No task turns a claim or return into a debit or credit note.**
3. **Does any task connect warehouse MRN / issue / production cost to accounting?** **No.**
   - Warehouse builds its half only in `STANDALONE` mode (wh#128 P2-18; `AHO` scope fence: *"the accounting-facing adapter, INTEGRATED mode and every accounting-side receiver belong to accounting P4-01 / #174"*).
   - The follow-ups are all **open with no owner**: wh#174 (*"adapter has no home"*), wh#175 (prove INTEGRATED), wh#173 (envelope v2: duty, lot, serial, FX).
   - The accounting side has the inbound port acc#36 P2-01 and posting rules acc#37 P2-02, both open. Its "second vertical" acc#62 P4-01 is open and **does not name warehouse**. The accounting README (`docs/README.md:76`) and acc#62 still say *"`warehouse` no longer exists in this codebase"*, which is stale: four warehouse modules are built in `classic`.
   - Warehouse D-6 / OD-1 (*accounting must stand down its own stock grain when warehouse is installed*) has **no reciprocal edit** in the accounting set.
   - Store issue with a cost object (FR-535, wh#571 open) and production settlement (wh#600 P10-09 open) emit envelopes that nobody receives.

## Matrix

### 12A.0 Preamble

| Id | PRD requirement (short) | Status | Evidence | Gap / note |
|---|---|---|---|---|
| 12A.0-01 | Complete double-entry module; every voucher posts to ledger | OTHER-MODULE · acc:BUILT | acc#14 P0-08 journals + invariant triggers (closed); L-1 balanced-or-nothing; subledger docs post journals (V610010/20/21/22) | — |
| 12A.0-02 | Operational vouchers built from the preceding document | SEAM — PARTIAL | inside accounting: quotation→SO→invoice, PO→GRN→bill flow links (V610130 `acc_document_flow_links`, acc#25/#26 closed) | Across modules (warehouse despatch → invoice, MRN → bill) **no consumer** (wh#174) |
| 12A.0-03 | Statutory returns prepared from the same books | OTHER-MODULE · acc:PLANNED | acc#61 P2-20, acc#79 P2-25 | — |
| 12A.0-04 | Every voucher: maker ≠ checker + value-based approval (§3) | OTHER-MODULE · acc:PARTIAL | acc#39 P2-04 approvals (open); acc#49 SoD matrix (open); aFR-137 | Bills/invoices/journals have `PENDING_APPROVAL`; **payments have no approval state** (`acc_payments.status` = DRAFT/POSTED/REVERSED); value bands not built |

### 12A.1 Sales Invoice

| Id | PRD requirement (short) | Status | Evidence | Gap / note |
|---|---|---|---|---|
| 12A.1-01 | Invoice created only from an approved dispatch | SEAM — MISSING | FRD-TRADE:55 warehouse-trade *"never raises an invoice"*; despatch emits handover (AHO A4); aFR-031 port materialises invoice | No adapter (wh#174); accounting invoices can be typed fresh or come from its own SO/delivery note (`acc_delivery_notes` V610141), so "never typed fresh" is not enforced |
| 12A.1-02 | Lines, rate and GST copied from SO | OTHER-MODULE · acc:BUILT (acc SO only) | aFR-233, acc#25 closed, `source` links V610130 | Only from **acc_sales_orders**, not from a warehouse-trade SO (two SO owners, see CONFLICTS C-2) |
| 12A.1-03 | Serials per line (chassis/motor/battery…) | OTHER-MODULE · acc:MISSING | `acc_invoice_lines` has no serial column; acc#116 batches schema-only; wh#173 envelope v2 (lot/serial) open | Serial identity lives only in warehouse; it cannot reach the invoice |
| 12A.1-04 | Type: Tax invoice | OTHER-MODULE · acc:BUILT | acc#27 closed | — |
| 12A.1-05 | Type: Export / SEZ | OTHER-MODULE · acc:PARTIAL | `supply_type` + registration type SEZ (INDIA-PACK:56, :115), acc#21 tax engine closed; seed acc#60 open | No LUT/bond fields, no shipping-bill/port fields, no export invoice declaration |
| 12A.1-06 | Type: Stock transfer (branch) invoice | OTHER-MODULE · acc:MISSING | zero hits in acc docs/issues; acc#34 inter-branch clearing is GL-only. Warehouse-india built `whin_transfer_irn_evidence` (V540112) | GST stock transfer between distinct GSTINs (a supply) has no accounting document; warehouse records only the IRN evidence |
| 12A.1-07 | Type: Proforma (advance, no stock effect) | OTHER-MODULE · acc:BUILT | aFR-234, acc#25 closed; retainer invoice kind V610151 (acc#72) | — |
| 12A.1-08 | Type: Debit note (sales side) | see 12A.7-05 | — | — |
| 12A.1-09 | Type: Credit note against invoice (return, rate diff, discount, with approval) | OTHER-MODULE · acc:BUILT | acc#27 closed; `applies_to_invoice_id`, `credit_note_reason_code_id` | Approval of credit notes: status set is DRAFT/POSTED/… with **no PENDING_APPROVAL** (V610011) |
| 12A.1-10 | GST CGST+SGST / IGST by place of supply | OTHER-MODULE · acc:BUILT | acc#21 P1-02 determination engine closed | — |
| 12A.1-11 | HSN summary on invoice | OTHER-MODULE · acc:PARTIAL | HSN as item tax classification (acc#23 closed); HSN summary in GSTR-1 (acc#61) | HSN-wise summary block on the printed invoice → acc#32 P1-13 templates (open), not stated |
| 12A.1-12 | TCS where applicable | OTHER-MODULE · acc:PLANNED | acc#46 P2-11 (TCS) open; warehouse-india `whin_tcs_sections` built (V540131) | Two TCS masters (C-4) |
| 12A.1-13 | Round-off | OTHER-MODULE · acc:BUILT | aFR-073; `round_off_total`/`rounding_total` on invoices | — |
| 12A.1-14 | E-invoice IRN/QR | OTHER-MODULE · acc:PLANNED | acc#61 P2-20; acc#47 doc lock (open); acc#97 F-005 GSP, F-007 30-day reporting window | — |
| 12A.1-15 | E-way bill | OTHER-MODULE · acc:PLANNED | acc#61; **warehouse-india built e-way bills** (wh#82 closed, V540030/V540100/V540101) | Two e-way owners (C-3) |
| 12A.1-16 | Status Draft → Approved → Posted → Partly paid → Paid / Cancelled | OTHER-MODULE · acc:PARTIAL | built: DRAFT, PENDING_APPROVAL, POSTED, PARTIALLY_PAID, PAID, WRITTEN_OFF, REVERSED (V610010) | "Cancelled" = REVERSED with reason; no explicit "Approved" state (C-6) |
| 12A.1-17 | Cancel only before IRN cancel window closes | OTHER-MODULE · acc:PLANNED | acc#47 (`locks_document`, authority-cancel rule L2-SC-92) | — |
| 12A.1-18 | Customer ledger: invoice-wise outstanding | OTHER-MODULE · acc:BUILT | acc#67 P1-18 open items (closed) | — |
| 12A.1-19 | Due date from payment terms | OTHER-MODULE · acc:BUILT | aFR-062, acc#113 payment terms closed | — |
| 12A.1-20 | Ageing 0–30/31–60/61–90/90+ | OTHER-MODULE · acc:PLANNED | aFR-074 configurable buckets, acc#31 P1-12 open | — |
| 12A.1-21 | Credit limit used | OTHER-MODULE · acc:PLANNED | acc#72 P1-20 open (V610152 credit_control + page already in code) | — |

### 12A.2 Purchase Invoice

| Id | PRD requirement (short) | Status | Evidence | Gap / note |
|---|---|---|---|---|
| 12A.2-01 | Booked against one or more approved **MRNs**, never PO alone | SEAM — PARTIAL | acc bill × **acc GRN** allocations V610581 (ACR-006); acc#123 P1-10a open. Warehouse MRN FR-527 / wh#569 open; outbox `material_receipt_note.authorised` (FRD-STORES §8) | Accounting's GRN is not the warehouse MRN and has no accepted qty. Bills without PO/GRN are allowed. **No rule forbids PO-only booking.** |
| 12A.2-02 | Only accepted qty is paid for | SEAM — MISSING | `acc_goods_receipt_lines` = `quantity`, `quantity_billed` only | Accepted vs rejected qty exists only in warehouse QC/MRN |
| 12A.2-03 | Three-way match PO rate × MRN accepted qty vs invoice | SEAM — PARTIAL | warehouse `wh_three_way_matches` BUILT (wh#58, V510201) against GRN lines; accounting two-way only (aFR-237); three-way **declined for v1** (aFR §10, COMPETITOR-BENCHMARK:144) | Warehouse match is a reference-only commercial check, against GRN not MRN, and posts nothing. Accounting refuses three-way in v1 (C-1). |
| 12A.2-04 | Difference above tolerance (₹ or %) holds invoice | OTHER-MODULE · acc:BUILT (two-way) | PO tolerance qty %/price %/value ₹ (V610132); bill → PENDING_APPROVAL naming variance (aFR-237, acc#26 closed); wh three-way `tolerance_percent` | Tolerance is on the PO, not per vendor or category |
| 12A.2-05 | Held invoice approved by **Purchase Manager** with reason | OTHER-MODULE · acc:PARTIAL | approver configuration acc#39 open | No named role routing; reason codes exist (acc#8) |
| 12A.2-06 | Vendor invoice no. + date; duplicate blocked per vendor | OTHER-MODULE · acc:BUILT | aFR-078, acc#29 closed; warehouse GRN duplicate-bill guard GBM-GRD-01..03 (wh#565 open) | aFR-078 default is **warn**, blocking is configurable (C-7); two duplicate guards |
| 12A.2-07 | GSTIN on invoice | OTHER-MODULE · acc:BUILT | V610024 `counterparty_tax_registration`/`own_tax_registration` (I-001) | — |
| 12A.2-08 | GST input CGST/SGST/IGST, ITC eligible Y/N | OTHER-MODULE · acc:BUILT | bill tax lines `recoverable_amount`/`non_recoverable_amount`, input/non-recoverable accounts | — |
| 12A.2-09 | TDS section and rate on invoice | OTHER-MODULE · acc:PARTIAL | aFR-080 withholding at bill or payment (acc#29 closed); sections master acc#46 open; IT Act 2025 re-key acc#97 open | Section master has no `effective_from` (acc#97 F-001) |
| 12A.2-10 | Freight / other charges | OTHER-MODULE · acc:PARTIAL | bill lines can carry charge items; landed cost aFR-104 acc#54 open; warehouse landed cost built (wh#125 P2-17) | Apportionment of a bill's freight into stock value has no cross-module path |
| 12A.2-11 | Due date | OTHER-MODULE · acc:BUILT | `acc_bills.due_date`, payment terms | — |
| 12A.2-12 | Debit note auto-proposed for rejected qty (IQC) | SEAM — PARTIAL | warehouse QUALITY_REJECT claim / supplier return as *"debit-note candidate"* (FRD-STORES §8, FR-526) | **No auto-proposal** on the accounting side; warehouse is forbidden to create it (RN-054) |
| 12A.2-13 | Debit note auto-proposed for short receipt | SEAM — PARTIAL | `SHORT_SHIPMENT` claim FR-519 (wh#123 closed, wh#565 open); WH-SC-438 *"no debit note"* | Same as above |
| 12A.2-14 | Expense/service bills without MRN (service PO or direct expense) | OTHER-MODULE · acc:BUILT | bills without GRN/PO allowed; service-line PO in warehouse-trade (FR-658) | — |
| 12A.2-15 | … with HOD approval | OTHER-MODULE · acc:PLANNED | acc#39 | No department/HOD resolver stated |
| 12A.2-16 | Status Draft → **Verified (Accounts)** → Approved → Posted → Partly paid → Paid | OTHER-MODULE · acc:PARTIAL | built DRAFT, PENDING_APPROVAL, POSTED, PARTIALLY_PAID, PAID, REVERSED (V610020) | **No "Verified" step** (C-6) |
| 12A.2-17 | Vendor ledger: invoice-wise payable, due date | OTHER-MODULE · acc:BUILT | acc#67 open items | — |
| 12A.2-18 | Vendor ageing | OTHER-MODULE · acc:PLANNED | acc#31 | — |
| 12A.2-19 | Advances paid shown on vendor ledger | OTHER-MODULE · acc:PARTIAL | payments `unallocated_amount`, tax on advances aFR-059 | No "advance against a PO" link (see 12A.3-02) |

### 12A.3 Payment and Receipt

| Id | PRD requirement (short) | Status | Evidence | Gap / note |
|---|---|---|---|---|
| 12A.3-01 | Payment against one or more purchase invoices | OTHER-MODULE · acc:BUILT | acc_payments allocations (acc#29 closed); payment batches V610139 | — |
| 12A.3-02 | … or as advance against a PO | OTHER-MODULE · acc:PARTIAL | unallocated payment = advance | **No PO reference on a payment** |
| 12A.3-03 | Mode NEFT/RTGS/cheque/UPI/cash | OTHER-MODULE · acc:BUILT | `payment_method` CASH/CHEQUE/BANK_TRANSFER/CARD/UPI/OTHER | NEFT vs RTGS not distinguished (cosmetic) |
| 12A.3-04 | Bank account, UTR/cheque no. | OTHER-MODULE · acc:BUILT | `bank_account_id`, `instrument_reference`; cheques register acc#43 open | — |
| 12A.3-05 | TDS deducted at payment | OTHER-MODULE · acc:BUILT | aFR-080, `section_id`, `is_withholding_catch_up` | — |
| 12A.3-06 | Payment maker–checker with value limits | OTHER-MODULE · acc:PARTIAL | acc#39 open | `acc_payments.status` has no approval state (built code) |
| 12A.3-07 | Payment advice emailed to vendor | OTHER-MODULE · acc:PLANNED | aFR-123, acc#32 P1-13 | — |
| 12A.3-08 | Receipt against invoices, bill-wise allocation | OTHER-MODULE · acc:PLANNED (code exists) | acc#28 P1-09 / acc#121 open; V610012/13 built; receipts page | — |
| 12A.3-09 | Receipt as advance against an SO | OTHER-MODULE · acc:PARTIAL | advance held as liability aFR-066 | No SO reference on a receipt |
| 12A.3-10 | Unallocated kept as on-account | OTHER-MODULE · acc:PLANNED | aFR-066/067, acc#28 | — |
| 12A.3-11 | TDS by customer recorded | OTHER-MODULE · acc:PLANNED | aFR-063 deduction lines (customer-deducted withholding), acc#28 | — |
| 12A.3-12 | Bank statement upload Excel/CSV | OTHER-MODULE · acc:PLANNED | aFR-087/088, acc#41 P2-06 | — |
| 12A.3-13 | Auto-match by UTR/amount/date; manual match | OTHER-MODULE · acc:PLANNED | aFR-090, acc#42 P2-07 | — |
| 12A.3-14 | Due list: vendor payments due this week | OTHER-MODULE · acc:PLANNED | acc#31 / acc#33 dashboard | No named "due this week" list |
| 12A.3-15 | Customer collections due/overdue | OTHER-MODULE · acc:PLANNED | acc#31 collections worklist | — |
| 12A.3-16 | Overdue visible to CRM sales owner before new SO | SEAM — PARTIAL | acc#72 credit control blocks an **acc** SO | The CRM (dealer) / warehouse-trade SO cannot read accounting exposure; no outbound read port (acc#38 outbox open) |
| 12A.3-17 | Cash payments above limit blocked (s.40A(3) / 269ST) | OTHER-MODULE · acc:MISSING | zero hits in acc docs/issues; acc#97 F-001 IT Act 2025 renumbering | — |

### 12A.4 Journal Voucher

| Id | PRD requirement (short) | Status | Evidence | Gap / note |
|---|---|---|---|---|
| 12A.4-01 | JV for provisions, accruals, depreciation, adjustments, rectifications, transfers, opening balances | OTHER-MODULE · acc:BUILT | acc#14 journals, acc#73 voucher entry, acc#30 opening balances (open, page built) | — |
| 12A.4-02 | Multi-line Dr/Cr, must balance | OTHER-MODULE · acc:BUILT | L-1 trigger, acc#14 | — |
| 12A.4-03 | Cost centre per line | OTHER-MODULE · acc:BUILT | dimensions acc#10/#64 closed; L-8 per-line guard acc#128 open | — |
| 12A.4-04 | Narration mandatory | OTHER-MODULE · acc:PARTIAL | narration template on voucher classes (acc#73) | Mandatory narration not stated (reason code is mandatory, aFR-140) |
| 12A.4-05 | Attachments | OTHER-MODULE · acc:BUILT | acc#16 document links, acc#149 attachments | — |
| 12A.4-06 | Recurring journals with schedule | OTHER-MODULE · acc:PLANNED | aFR-114/115, acc#56 P3-04 | — |
| 12A.4-07 | Reversing journals auto-reverse on the 1st | OTHER-MODULE · acc:PLANNED | aFR-116, acc#56 / acc#84 | — |
| 12A.4-08 | Contra cash↔bank, bank↔bank | OTHER-MODULE · acc:BUILT | V610140 contra transfers, acc#24/#150 closed | — |
| 12A.4-09 | Approval Accounts Manager; above limit Finance Head/MD | OTHER-MODULE · acc:PARTIAL | journal approval exists (acc#167 "approval bypass" fixed); value tiers acc#39 open | — |

### 12A.5 Expense

| Id | PRD requirement (short) | Status | Evidence | Gap / note |
|---|---|---|---|---|
| 12A.5-01 | Direct expense heads (freight inward, job-work, power, wages, packing, consumables) | OTHER-MODULE · acc:BUILT (as CoA) | CoA templates acc#9 / seed acc#60 | Head list is client data (Q-AC11) |
| 12A.5-02 | Direct expense linked to Production Order / batch → product cost | SEAM — PARTIAL | warehouse store issue cost object incl. production order (FR-535, wh#571 open); wh#600 P10-09 actual costing open; **aFR §10 / T-034 refuses manufacturing and WIP** | A **bill or journal expense** (power, wages, job-work charge) has no path into the production-order cost pool. Warehouse-manufacturing costs only material plus its own settlement. |
| 12A.5-03 | Indirect expense heads to P&L | OTHER-MODULE · acc:BUILT (CoA) | acc#9 | — |
| 12A.5-04 | Expense booking: vendor/employee, ledger, cost centre, GST input | OTHER-MODULE · acc:BUILT | bills + expense claims V610142 | — |
| 12A.5-05 | GST blocked under s.17(5) | OTHER-MODULE · acc:PARTIAL | non-recoverable tax split built; acc#110 open | s.17(5) blocked-credit categories not modelled by name |
| 12A.5-06 | TDS section on expense | OTHER-MODULE · acc:PLANNED | acc#46 | — |
| 12A.5-07 | RCM flag | OTHER-MODULE · acc:PLANNED | `is_reverse_charge` columns built; RCM posting both sides acc#47 open | — |
| 12A.5-08 | Bill upload | OTHER-MODULE · acc:BUILT | document links acc#16 | — |
| 12A.5-09 | Employee claim → HOD → Accounts → payment | OTHER-MODULE · acc:PARTIAL | expense claims built (V610142, page); acc#123 P1-10c | HOD approval leg depends on acc#39 |
| 12A.5-10 | Petty cash imprest with daily cash book | OTHER-MODULE · acc:DECLINED | aFR-094: cash count yes, *"deferred imprest workflow"*; cash count acc#42 | PRD needs imprest now |
| 12A.5-11 | Budget per head & cost centre; warn or block | OTHER-MODULE · acc:PLANNED | aFR-239/240, acc#56 | — |

### 12A.6 Income

| Id | PRD requirement (short) | Status | Evidence | Gap / note |
|---|---|---|---|---|
| 12A.6-01 | Direct income heads (vehicles, spares, services, job-work) | OTHER-MODULE · acc:BUILT (CoA) | acc#9 | — |
| 12A.6-02 | Scrap sales from Scrap store with GST/TCS | SEAM — PARTIAL | warehouse-india scrap = stock status + *"scrap sale is a supply"* (wh#32 P4-04 closed, V540131 + TCS sections) | No accounting invoice from a warehouse scrap despatch (wh#174) |
| 12A.6-03 | Indirect income heads | OTHER-MODULE · acc:BUILT (CoA) | — | — |
| 12A.6-04 | Booked via sales invoice or income voucher | OTHER-MODULE · acc:BUILT | invoices / journals | — |
| 12A.6-05 | TDS by payer recorded for 26AS/AIS | OTHER-MODULE · acc:PLANNED | aFR-063 deductions; 26AS/AIS recon acc#79 | — |

### 12A.7 Debit Note

| Id | PRD requirement (short) | Status | Evidence | Gap / note |
|---|---|---|---|---|
| 12A.7-01 | Vendor DN item-wise (rejection, short supply) | OTHER-MODULE · acc:BUILT | `acc_debit_note_lines.bill_line_id,item_id,quantity` (V610021, acc#29) | — |
| 12A.7-02 | … links to IQC/GRN, reduces stock via purchase return | SEAM — PARTIAL | warehouse supplier return (wh#93 closed, wh#568 open) moves stock; DN has no GRN/return link | Two halves never joined |
| 12A.7-03 | Vendor DN amount-only (rate diff, penalty, quality claim) | OTHER-MODULE · acc:BUILT | DN lines with account, no item | — |
| 12A.7-04 | GST reversal on DN | OTHER-MODULE · acc:BUILT | DN tax lines with recoverable/non-recoverable | — |
| 12A.7-05 | Customer DN / supplementary invoice (price increase, freight, interest, short-billing) | OTHER-MODULE · acc:PARTIAL | only interest debit note aFR-075 (acc#45 open) | No general customer debit note or supplementary invoice document |
| 12A.7-06 | DN against party with no invoice | OTHER-MODULE · acc:BUILT | `applies_to_bill_id` optional; leftover vendor credit acc#154 F2 fixed | Customer side: none |
| 12A.7-07 | Must reference original invoice no. + date | OTHER-MODULE · acc:PARTIAL | `applies_to_bill_id`, `vendor_reference` | Not mandatory |
| 12A.7-08 | Approval mandatory | OTHER-MODULE · acc:PARTIAL | acc#39 | DN status set has no approval state |
| 12A.7-09 | Reason code mandatory | OTHER-MODULE · acc:BUILT | `reason_code_id`, aFR-140 | — |

### 12A.8 Credit Note

| Id | PRD requirement (short) | Status | Evidence | Gap / note |
|---|---|---|---|---|
| 12A.8-01 | Customer CN item-wise (sales return) | OTHER-MODULE · acc:BUILT | `acc_credit_note_lines.invoice_line_id,item_id,quantity` (acc#27) | — |
| 12A.8-02 | … goods back via gate entry and IQC, stock to Rework/FG/Scrap | SEAM — PARTIAL | warehouse-trade SRA (`trade-sales-return-authorisation.contract`), QC polymorphic source wh#567 closed; SRA CREDIT intent is the hand-over point (FRD-TRADE R3) | No CN raised from the SRA |
| 12A.8-03 | Customer CN amount-only (discount, rate diff, warranty, scheme) | OTHER-MODULE · acc:BUILT | acc#27 | — |
| 12A.8-04 | GST reversal + e-invoice IRN for B2B CN | OTHER-MODULE · acc:PLANNED | acc#61 (e-invoice covers CN/DN) | — |
| 12A.8-05 | Record vendor's credit note (item-wise or amount) | OTHER-MODULE · acc:PARTIAL | modelled as an own debit note / bill reversal | No "vendor credit note" document with the vendor's number and date for GSTR-2B matching |
| 12A.8-06 | CN against party with no invoice | OTHER-MODULE · acc:BUILT | `applies_to_invoice_id` optional | — |
| 12A.8-07 | Original invoice ref, reason code, approval | OTHER-MODULE · acc:PARTIAL | reason code built; approval acc#39 | — |
| 12A.8-08 | GST time-limit check (30 Nov after FY end, s.34) | OTHER-MODULE · acc:MISSING | zero hits | — |

### 12A.9 Masters, books, statements

| Id | PRD requirement (short) | Status | Evidence | Gap / note |
|---|---|---|---|---|
| 12A.9-01 | CoA groups in Schedule III layout | OTHER-MODULE · acc:PLANNED | account types acc#9 closed; Schedule III layout acc#48/#60 open | — |
| 12A.9-02 | Party ledgers auto-created for customers/vendors | OTHER-MODULE · acc:PARTIAL | parties + control account + open items (acc#114, #67) | **Subledger model, not one ledger per party** (C-8); party match-then-create aFR-040 at the port |
| 12A.9-03 | Bank, cash, GST/TDS/TCS duty ledgers | OTHER-MODULE · acc:BUILT | acc#24 bank/cash; tax accounts on tax codes | — |
| 12A.9-04 | Cost / profit centres on every voucher line | OTHER-MODULE · acc:BUILT | dimensions acc#10/#64 | — |
| 12A.9-05 | FY and periods; lock after close | OTHER-MODULE · acc:BUILT | acc#11, acc#65 lock date, acc#164 | — |
| 12A.9-06 | Only Finance Head unlocks, with reason, audited | OTHER-MODULE · acc:BUILT | reopen + reason code (aFR-140), acc#164 | Role naming is config |
| 12A.9-07 | Opening balances import | OTHER-MODULE · acc:PLANNED | acc#30 P1-11 open (page built), acc#50 workbench | — |
| 12A.9-08 | Fixed asset register, capitalisation from purchase invoice | OTHER-MODULE · acc:PLANNED | acc#53 P3-01; `capitalise_to_asset` on bill lines (acc#123) | — |
| 12A.9-09 | Depreciation Companies Act WDV/SLM | OTHER-MODULE · acc:PLANNED | aFR-107 (straight line, reducing balance), acc#53 | — |
| 12A.9-10 | Income Tax block rates | OTHER-MODULE · acc:PLANNED | acc#87 P3-10 parallel tax depreciation board | — |
| 12A.9-11 | Inventory valuation weighted average / FIFO | SEAM — PARTIAL | warehouse AVCO/FIFO + specific id for serials (costing-valuation A3, wh#115 P2-16 open, follow-ups closed); accounting aFR-101 acc#54 open | D-6: warehouse authoritative when installed; OD-1 reciprocal edits absent in acc set |
| 12A.9-12 | Stock value in balance sheet from stock ledger | OTHER-MODULE · acc:DECLINED (integrated) / PLANNED (standalone) | wh WS-219 stock-to-GL (AHO A9, TO BUILD); `GlBalanceProvider` has no implementation (AHO-UNR-06) | With warehouse installed, nothing posts stock value to the GL (wh#174/#175) |
| 12A.9-13 | WIP and FG at standard or actual cost | OTHER-MODULE · acc:DECLINED | aFR-101 / §10 / T-034 *"Manufacturing and WIP … out of scope"*; warehouse-manufacturing actual costing wh#600 open; **no standard cost** in warehouse (AVCO/FIFO only) | Standard costing for FG/WIP missing everywhere (C-1) |
| 12A.9-14 | Day book, cash book, bank book, ledger, sub-ledger, TB | OTHER-MODULE · acc:PARTIAL | day book/GL/TB built (acc#99–#101); open items | Named **cash book / bank book** reports: zero hits |
| 12A.9-15 | P&L, balance sheet (Schedule III) | OTHER-MODULE · acc:PLANNED | acc#33, acc#48 | — |
| 12A.9-16 | Cash flow | OTHER-MODULE · acc:PLANNED | aFR-120, acc#56 | — |
| 12A.9-17 | Receivables/payables ageing, bill-wise outstanding | OTHER-MODULE · acc:PLANNED | acc#31, acc#67 built | — |
| 12A.9-18 | Cost-centre P&L | OTHER-MODULE · acc:PLANNED | dimension filters on P&L acc#33/#77 | — |
| 12A.9-19 | Budget vs actual | OTHER-MODULE · acc:PLANNED | acc#56 | — |
| 12A.9-20 | Interest calculation on overdue | OTHER-MODULE · acc:PLANNED | aFR-075, acc#45 | — |
| 12A.9-21 | Multi-currency with FX gain/loss | OTHER-MODULE · acc:PLANNED | rates acc#12 closed; realised FX acc#28; revaluation acc#40 | Warehouse FX costing has no rate source (wh OD-16) |

### 12A.10 Statutory compliance

| Id | PRD requirement (short) | Status | Evidence | Gap / note |
|---|---|---|---|---|
| 12A.10-01 | GST place-of-supply split, HSN/SAC | OTHER-MODULE · acc:BUILT | acc#21, acc#23 | Warehouse-india has a second GST engine (wh#16 closed) — C-4 |
| 12A.10-02 | RCM | OTHER-MODULE · acc:PLANNED | acc#47 | — |
| 12A.10-03 | ITC eligibility and blocked credits | OTHER-MODULE · acc:PARTIAL | recoverable split built | s.17(5) catalogue absent |
| 12A.10-04 | ITC reversal Rule 42/43 | OTHER-MODULE · acc:MISSING | acc#79 covers only non-payment reversal (I-009); warehouse-india `whin_itc_reversals` covers loss/scrap (wh#32) | Common-credit apportionment (exempt + taxable) and capital-goods reversal not designed |
| 12A.10-05 | GSTR-1 data + JSON | OTHER-MODULE · acc:PLANNED | acc#61; IMS/GSTR-1A acc#97 F-003/4 | — |
| 12A.10-06 | GSTR-3B summary | OTHER-MODULE · acc:PLANNED | acc#61, acc#79 tie-out | — |
| 12A.10-07 | GSTR-2B import + reconciliation, mismatch report | OTHER-MODULE · acc:PLANNED | acc#61, acc#79 supplier-not-filed flag | — |
| 12A.10-08 | GSTR-9 data | OTHER-MODULE · acc:PLANNED | acc#79 (9/9C working papers) | — |
| 12A.10-09 | E-invoice IRN/QR via GSP/IRP, cancel within 24h | OTHER-MODULE · acc:PLANNED | acc#61, acc#47, acc#97 F-005/F-007 | — |
| 12A.10-10 | E-way bill > ₹50k, Part-B, cancel, extend | OTHER-MODULE · acc:PLANNED / warehouse BUILT | acc#61, acc#79 consolidated; warehouse-india built all four (wh#82 closed, wh#147 open) | C-3 |
| 12A.10-11 | TDS section-wise (194C/J/H/I/Q…), threshold per party | OTHER-MODULE · acc:PLANNED | acc#46, aggregate built in acc#29; acc#97 F-001, F-010 | Section codes changed under IT Act 2025 (C-5) |
| 12A.10-12 | TDS challan (ITNS 281) entry | OTHER-MODULE · acc:PARTIAL | acc#79 *"GST challan reference"*; TDS challan not named | — |
| 12A.10-13 | 24Q/26Q return data | OTHER-MODULE · acc:PLANNED | acc#79 | 24Q is salary TDS; payroll out of scope (T-061), so only 26Q is meaningful |
| 12A.10-14 | Form 16A | OTHER-MODULE · acc:PLANNED | certificates acc#46 | — |
| 12A.10-15 | TCS 206C(1H), challan, 27EQ | OTHER-MODULE · acc:PLANNED | acc#46, acc#79; 194Q↔206C(1H) exclusion acc#97 F-010 | 206C(1H) was omitted from 1 Apr 2025 (Finance Act 2025) — C-5 |
| 12A.10-16 | MSME flag; 45-day rule s.43B(h) | OTHER-MODULE · acc:PLANNED | acc#97 F-002 (Udyam, statutory due date) | — |
| 12A.10-17 | MSME-1 half-yearly report data | OTHER-MODULE · acc:MISSING | zero hits | — |
| 12A.10-18 | Cash limits s.40A(3) / 269ST | OTHER-MODULE · acc:MISSING | zero hits | = 12A.3-17 |
| 12A.10-19 | 26AS/AIS reconciliation | OTHER-MODULE · acc:PLANNED | acc#79 | — |
| 12A.10-20 | Schedule III BS & P&L | OTHER-MODULE · acc:PLANNED | acc#48/#60 | — |
| 12A.10-21 | Depreciation schedule | OTHER-MODULE · acc:PLANNED | acc#53 | — |
| 12A.10-22 | Audit trail (edit log) that cannot be disabled, Rule 3(1) | OTHER-MODULE · acc:BUILT | acc#15 P0-09 hash chain (closed); acc#60 trap *"satisfied by P0-09"*; Rules 3(5)/3(6) acc#97 F-006 | — |
| 12A.10-23 | Payroll statutory out of scope v1 | OTHER-MODULE · acc:DECLINED (consistent) | T-061 | Agrees with PRD |
| 12A.10-24 | Compliance calendar (GSTR-1 11th, 3B 20th, TDS 7th, returns, advance tax, MSME-1) with owner/status | OTHER-MODULE · acc:MISSING | zero hits; tax periods acc#112 hold no due dates | — |
| 12A.10-25 | Every voucher create/edit/delete keeps before/after, append-only | OTHER-MODULE · acc:BUILT | acc#15, aFR-140; viewer acc#49 open | — |
| 12A.10-26 | Edits after period lock blocked | OTHER-MODULE · acc:BUILT | acc#11/#65 | — |
| 12A.10-27 | Prints carry GSTIN, CIN, PAN, statutory declarations | OTHER-MODULE · acc:PLANNED | company tax identifiers acc#65 closed; templates acc#32 | — |

### 12A.11 Tally and registers

| Id | PRD requirement (short) | Status | Evidence | Gap / note |
|---|---|---|---|---|
| 12A.11-01 | Every posted voucher exports to Tally (XML or API) | OTHER-MODULE · acc:PLANNED | acc#78 P2-24 *"Outbound Tally XML export"*; aFR-131; INDIA-PACK:199 | Planned as a **batch export for the CA**, not per voucher. No Tally API. |
| 12A.11-02 | CRM document no. as reference | OTHER-MODULE · acc:DESIGN-ONLY | aFR-131 batch acknowledgement | Not specified per voucher |
| 12A.11-03 | Posting status and errors shown per voucher | OTHER-MODULE · acc:DESIGN-ONLY | aFR-131 *"acknowledgement … re-runnable"* | No per-voucher status/error UI in any issue |
| 12A.11-04 | Masters mapped once (ledgers, customers, vendors, items, GST rates) | OTHER-MODULE · acc:PARTIAL | external refs on parties/items (acc#114/#115) and import mapping (acc#50/#98 F-014) | Mapping is for **import**. An outbound mapping to Tally ledger names is not designed. |
| 12A.11-05 | MRN exported to Tally for bill booking (PRD §6 line 180) | OTHER-MODULE · acc:MISSING | warehouse has zero Tally design (one incidental mention) | — |
| 12A.11-06 | Reports: sales register, purchase register | OTHER-MODULE · acc:PLANNED | acc#33 | — |
| 12A.11-07 | GSTR-1/3B summary data | OTHER-MODULE · acc:PLANNED | acc#61 | — |
| 12A.11-08 | TDS payable | OTHER-MODULE · acc:PLANNED | acc#46/#79 | — |
| 12A.11-09 | Receivables/payables ageing | OTHER-MODULE · acc:PLANNED | acc#31 | — |
| 12A.11-10 | Cash/bank book | OTHER-MODULE · acc:MISSING | see 12A.9-14 | — |

## CONFLICTS (design set vs PRD)

- **C-1 · Manufacturing, WIP and three-way match are refused in the accounting design.**
  - aFR §10 and T-034: *"Manufacturing, BOM and WIP … a different product."* *"three-way match in v1"* is out of scope.
  - The PRD requires three-way PO × MRN × invoice (12A.2-03), direct expenses landing in production-order cost (12A.5-02), and WIP/FG valued at standard or actual cost (12A.9-13).
  - The warehouse re-target (RN-050..054) now **is** a manufacturing product. The accounting refusal predates it, and its re-entry path ("post a stock-movement envelope through the port") is exactly the unbuilt adapter (wh#174).
  - **Standard costing exists in neither set**: warehouse has AVCO/FIFO and actual mfg costing.
- **C-2 · Two owners of PO, GRN, quotation, SO and delivery note.**
  - Accounting built `acc_purchase_orders`, `acc_goods_receipts`, `acc_quotations`, `acc_sales_orders` and `acc_delivery_notes` (acc#25/#26/#72).
  - Warehouse-trade designs PO, PR, RFQ, SO and SRA, and warehouse builds GRN, MRN and despatch.
  - On an install with both, no decision says which one is the system of record or how the duplicate is suppressed (the accounting README believes warehouse does not exist). The PRD assumes a single chain SO → dispatch → invoice and PO → GRN → IQC → MRN → bill.
- **C-3 · Two e-way bill and IRN owners.** Warehouse-india **built** e-way bills (single, consolidated, Part B, cancel, extend) and transfer IRN. Accounting plans e-invoice and e-way bills on the invoice (acc#61, acc#79). Nothing says which module generates the e-way bill for an invoice that travels with a warehouse challan.
- **C-4 · Two GST engines and two TCS masters.** Warehouse-india P4-01 *"relational tax engine"* (wh#16 closed) and `whin_tcs_sections` vs accounting-base tax determination (acc#21) and withholding sections (acc#46). Warehouse OD-9 (*does warehouse compute tax?*) is still listed open.
- **C-5 · The PRD cites superseded statute.**
  - The **Income-tax Act 2025 is in force from 1 Apr 2026** (acc#97 F-001), so 194C/194J/194H/194I/194Q, 206C(1H), 40A(3), 269ST, 43B(h), 26Q/27EQ, Form 16A and ITNS 281 have new section and form numbers.
  - 206C(1H) TCS on sale of goods was omitted from 1 Apr 2025.
  - The design set (acc#97) is ahead of the PRD here. Tell the client.
- **C-6 · Status ladders differ.**
  - Purchase invoice: PRD Draft → **Verified** → Approved → Posted. Built: DRAFT → PENDING_APPROVAL → POSTED, with no Verified step.
  - Sales invoice: PRD "Approved (Billing/Accounts)" and "Cancelled". Built: PENDING_APPROVAL and REVERSED with reason; WRITTEN_OFF exists but is not in the PRD.
  - Payments: PRD maker–checker. Built: no approval state.
- **C-7 · Duplicate vendor bill: PRD "blocked", aFR-078 default "warn"** (configurable). There are also two guards: the warehouse GRN bill guard GBM-GRD-01..03 and the accounting bill guard.
- **C-8 · Ledger model.** The PRD says *"party ledgers auto-created for customers and vendors"* (Tally model). Accounting uses control accounts plus a party subledger (open items) and forbids manual posting to AP/AR control (L-7). The functional outcome matches; the vocabulary does not. Explain to the client.
- **C-9 · Imprest.** PRD wants petty-cash imprest with a daily cash book. aFR-094 defers the imprest workflow and keeps only cash count.
- **C-10 · Tally direction.** The PRD wants every posted voucher exported per voucher with status and errors during transition. The accounting design centres on **import** from Tally (acc#50, acc#98) and a CA-facing batch XML export (acc#78).
- **C-11 · Warehouse handover status.** AHO says *"P2-18 builds STANDALONE only (OD-1)"* and defers INTEGRATED to accounting P4-01 / wh#174. Accounting acc#62 P4-01 says its intended vertical *"no longer exists"*. Each side waits on the other.

## BEYOND-PRD

**Industry gaps neither the PRD nor the design sets cover**
- **GRNI / provision for unbilled receipts across modules.** Accounting has GRNI for its own GRN (aFR-083, acc#123). Warehouse MRNs with no bill never accrue, so month-end liabilities are understated on an integrated install.
- **Purchase price variance (MRN at PO rate vs bill rate) back into stock or COGS.** aFR-084 states the rule only for accounting's own layers. For warehouse-costed stock, the bill-price difference has no route back into `wh` cost layers.
- **Job-work (ITC-04) charges and goods.** Warehouse-india built ITC-04 (V540120). The job-worker's charge bill and the 1-year / 3-year deemed-supply rule have no accounting tie.
- **Rule 86B** (1% cash payment of GST liability) and the **electronic credit ledger set-off order**. The latter is in acc#79; 86B is absent.
- **QRMP / IFF**, **GST on advances received** (aFR-059 present), **e-invoice reporting 30-day limit** (acc#97 F-007), and **GSP dependency** (acc#97 F-005). Add the last two to the PRD.
- **Vendor bank-detail change control** (fraud control on beneficiary edits). Payment-file generation exists (aFR-081). Maker–checker on beneficiary master changes is not stated anywhere.
- **Warranty provision** (Ind AS 37 / AS 29) for an EV OEM. The PRD mentions warranty claim settlement credit notes but not the provision accrual on each vehicle sale.

**In the accounting design but absent from the PRD (worth telling the client)**
- Hash-chained, tamper-evident audit trail and number-series gapless integrity report (acc#15, acc#102).
- Inter-branch clearing with per-branch balanced trial balance (acc#34).
- Source-module reconciliation as a blocking close condition (aFR-046/122), and the warehouse stock-to-GL reconciliation WS-219 (AHO A9).
- Deduction lines on receipts: bank charge, customer TDS, settlement discount, small write-off, retention (aFR-063).
- Cheque / PDC register with dishonour cascade (acc#43); undeposited funds (V610149).
- Customer-advance liability presentation, forfeiture and refund documents (aFR-066..068).
- Revenue recognition and deferral schedules (acc#84); percentage-of-completion (Q-042).
- Migration workbench with dry-run trial balance and parallel run (acc#50, acc#98).
- DPDP 2023 compliance by 13 May 2027 (acc#97 F-011).

## QUESTIONNAIRE

Pairing taken from PRD §14 (the extracted text shifts each answer cell by one row; the mapping below is by question text).

| Q | Topic | Depends rows | Answered by assumption in the design sets? |
|---|---|---|---|
| Q-INV / Q-AC1 | System is the entry point, Tally only receives vouchers? | 12A.0-02, 12A.1-01, 12A.11-* | **Accounting assumes YES** (standalone books of record, aFR §1, D-1; Tally as migration source). Warehouse assumes nothing (accounting deferred, RN-054). |
| Q-AC2 | Invoice types (tax, export/SEZ, stock transfer, proforma, DN, CN) | 12A.1-04..09 | Partly: tax, proforma, CN, vendor DN built. Export/SEZ only as supply_type. **Stock-transfer invoice not assumed.** |
| Q-AC3 | Purchase invoice always against MRN (three-way)? Tolerance? | 12A.2-01..05 | **Answered NO by assumption**: two-way in v1, three-way deferred (aFR §10); tolerance per PO (V610132). Warehouse three-way built as reference-only. |
| Q-AC4 | TDS/TCS sections | 12A.10-11..15 | Not answered; seed is acc#60; must be re-based on IT Act 2025 (acc#97) |
| Q-AC5 / Q-A1 | Payment approval levels, maker/checker | 12A.0-04, 12A.3-06, 12A.4-09 | Not answered; approval engine acc#39 is generic (aFR-137) |
| Q-AC6 | Bank statement format | 12A.3-12/13 | Mapping profiles are configurable (aFR-087), so no assumption needed |
| Q-AC7 / Q-D3 | Overdue blocks new SO / dispatch? | 12A.3-16, 12A.1-21 | Accounting assumes a credit check on **its own** SO (acc#72). Warehouse-trade *"never checks credit"* (FRD-TRADE:55). Cross-module block unanswered. |
| Q-AC8 | Reports needed | 12A.9-14..20, 12A.11-06..10 | Accounting ships a fixed report set (custom builder deferred, Q-034); cash/bank book not in it |
| Q-AC9 | Replace Tally? Cut-over date, opening balances | 12A.9-07, 12A.11-* | Assumed YES with migration workbench + parallel run (acc#50, acc#98) |
| Q-AC10 | Chart of accounts, cost centres | 12A.9-01..04 | CoA template + dimensions configurable; no assumption |
| Q-AC11 | Expense heads; which direct expenses to production cost | 12A.5-01/02 | **Blocked by C-1**: no path for expenses into production cost |
| Q-AC12 | Income heads (scrap, job-work, interest) | 12A.6-* | Scrap = warehouse-india stock status + supply (wh#32); no accounting invoice path |
| Q-AC13 | DN/CN reasons, item-wise or amount, approver | 12A.7-*, 12A.8-* | Both item-wise and amount-only supported; approver unassumed; stock effect unassumed |
| Q-AC14 | Valuation method | 12A.9-11..13 | Warehouse assumes AVCO default, FIFO optional, specific id for serials (CVL-GRD-03/04); **standard cost not offered**; accounting refuses WIP |
| Q-AC15 | Fixed assets (Companies Act + IT) | 12A.9-08..10 | Assumed YES (acc#53, acc#87), both P3 |
| Q-AC16 | GSTINs/states, e-invoice, GSP | 12A.10-09/10, 12A.1-06 | GSP intermediation flagged (acc#97 F-005); count unassumed |
| Q-AC17 | GSTR-2B recon, GSTR-1/3B files | 12A.10-05..07 | Assumed YES (acc#61) |
| Q-AC18 | TDS/TCS returns self or CA; 24Q/26Q/27EQ export | 12A.10-13/15 | Assumed: extracts only (acc#79); filing not in scope |
| Q-AC19 | MSME vendors, enforce 45-day alerts | 12A.10-16/17 | Reporting assumed (acc#97); enforcement and MSME-1 unassumed |
| Q-AC20 | Period-lock owner; budgets per head | 12A.9-05/06, 12A.5-11 | Lock + reopen with reason built; budget warn-vs-block **must be stated** (aFR-239), so it is unanswered |
| Q-AC21 | Foreign-currency imports/exports | 12A.9-21 | Accounting FX built/planned; **warehouse FX costing rate source open (wh OD-16)** |
| Q-I6 | Is MRN the bill-booking document; MRN to Tally automatically? | 12A.2-01, 12A.11-05 | Warehouse assumes MRN emits an outbox event for *"bill matching"* (FRD-STORES §8). No consumer; no Tally path. |
| Q-D1 / Q-D4 | E-invoice/e-way from system; Tally version and voucher sync | 12A.10-09/10, 12A.11-01/04 | E-way assumed and built in warehouse-india; Tally version unassumed (acc#78 trap: *"pin the release"*) |

## Top gaps (ranked)

1. **No warehouse → accounting adapter.** wh#174, #175 and #173 are open with no owner, and accounting acc#62 doesn't name warehouse. Its README says warehouse doesn't exist, so MRN, issue, production and despatch values never reach the GL (12A.0-02, 12A.9-12).
2. **Purchase invoice not bound to the MRN or accepted quantity.**
   - The accounting bill matches its own GRN, which has no QC quantities, and PO-only or no-PO bills are allowed.
   - Three-way match is declined for v1, and the warehouse's built three-way is reference-only (12A.2-01..03).
3. **Manufacturing, WIP and standard cost refused in accounting (T-034)** and absent in warehouse. Direct expenses can't reach production cost (12A.5-02, 12A.9-13).
4. **Debit/credit notes have no stock effect and no auto-proposal** from IQC reject, short receipt or sales return. The warehouse claims and SRA are "candidates" nobody consumes (12A.2-12/13, 12A.7-02, 12A.8-02).
5. **Two owners for PO/GRN/SO/delivery note, e-way bill/IRN and the GST engine/TCS** across accounting and warehouse(-india) (C-2, C-3, C-4).
6. **Maker–checker gaps.** Payments, debit notes and credit notes have no approval state, and value bands are not built (acc#39 open) (12A.0-04, 12A.3-06).
7. **Missing statutory items:** s.40A(3)/269ST cash limits, Rule 42/43 ITC reversal, MSME-1, CN/DN 30-Nov time limit, compliance calendar, and the stock-transfer tax invoice.
8. **The PRD cites pre-IT-Act-2025 sections and the omitted 206C(1H)** (C-5).
9. **Tally:** batch CA export only. Per-voucher export, posting status/errors, outbound master mapping and MRN → Tally are not designed (12A.11-01..05).
10. **Customer debit note / supplementary invoice, vendor credit note document, and petty-cash imprest are missing or deferred.** Cash book and bank book reports are not named (12A.7-05, 12A.8-05, 12A.5-10, 12A.9-14).
