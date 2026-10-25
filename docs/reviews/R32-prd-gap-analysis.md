# PRD (Manufacturing, Purchase, Stores & Quality, 2026-10-24) vs warehouse design set + GitHub issues — MASTER GAP LIST

Sources checked: PRD (every bullet, table cell, questionnaire item); warehouse-issues docs (FR, 4 FRDs, 51 contracts, DECISIONS, DATA-MODEL, GAP-REGISTERs, reviews); all 630 warehouse-issues GitHub issues (499 closed / 131 open); `neetub1508/accounting` (184 issues) + accounting docs; built code under classic/warehouse*, classic/accounting*, classic/dealer, classic/services.

## Totals (799 atomic PRD requirements)

| Slice | Rows | Built | Planned (open issue) | Partial | Missing | Declined (PRD contradicts) | Other module |
|---|---|---|---|---|---|---|---|
| Approvals, masters, NFR (§1–4, 13.2–13.4) | 168 | 42 | 37 | 60 | 18 | 7 | 4 |
| Purchase + inward (§5–6) | 127 | 32 | 58 | 12 | 18 | 5 | 2 |
| MR / issue / return + BOM (§7–8) | 103 | 9 | 52 | 25 | 16 | 1 | 0 |
| Production, QC, samples (§9–11) | 153 | 10 | 33 | 49 | 59 | 2 | 0 |
| CRM→SO, dispatch, reports (§4A, 12, 13.1) | 88 | 8 | 22 | 28 | 20 | 5 | 4 (+1 design-only) |
| Accounting + compliance (§12A) | 160 | — | — | 11 seam | 2 seam | — | 147 (acc: 48 built, 57 planned, 26 partial, 10 missing, 4 declined, 2 design-only) |

Not built yet even where "planned": all of warehouse-trade (P9 #578–#591) and warehouse-manufacturing (P10 #592–#605); store issue/return #571/#572; MRN #569.

## A. Whole areas with NO owner anywhere (new tasks needed)
1. Samples + drawings (§11): drawing master, revisions A/B/C, status flow, create≠approve, "UNCONTROLLED COPY" watermark, drawing no.+rev on PO/BOM, sample request, Sample production order, sample store, sample dispatch challan, customer feedback iterations, sample QC report.
2. Batch-wise production (§8.3/9.1/9.2): batch-produced flag, standard batch size, order → batches, batch no. through MR/issue/stage/QC/PDI/FG label, job card per batch per stage, stage sequencing gate, per-batch MR and variance.
3. Unit serial binding (chassis ↔ motor/controller/battery/charger) at stage level, chassis no. at first stage — design explicitly rejects per-unit capture (MD-11, MD-41). Breaks traceability report + invoice serials + warranty.
4. PDI as its own gate: per-vehicle record, per-model/variant checklist + SO-specific points, QC-Manager-signed PDI certificate PDF, PDI before dispatch from stock.
5. NCR / CAPA / Deviation documents with expiry (qty/time bound), Plant Head approval; reports: open NCR, Pareto, deviations.
6. Operator/skill master + work centre/machine master (capacity/shift/cost per hour); authorised operator per stage; authorised inspector per QC stage.
7. Feasibility review + pre-sale costing (BOM × last rate + routing labour + overhead + margin, floor price approval); Order book "produced" column; Customer 360.
8. Warehouse → accounting adapter: MRN/issue/production cost never reach GL (wh#173/#174/#175 open, unowned; accounting README still says warehouse doesn't exist). Purchase invoice against MRN accepted qty (three-way) not designed.
9. Manufacturer-side unit/serial registry (chassis ↔ part serials, sale date, invoice) for warranty, in warehouse-manufacturing — NOT a feed into classic `services` (dealer vertical, fenced). The PRD's "existing CRM" (leads, quotations, Tally import) is the client's Voyager CRM, not classic `dealer`.
10. Tally integration (masters + per-voucher export with status/errors) — only a CA batch XML export planned (acc#78).
11. Mobile app (gate, GRN scan, IQC, issue scan + OTP ack, shop-floor QR booking, PDI) — design says no mobile (D-16/D-17/R-13/FR-669) while D-13 says mobile mandatory: design set contradicts itself.

## B. Decisions in the design set that the PRD now CONTRADICTS (need client/user ruling)
| PRD wants | Design set decided | Ref |
|---|---|---|
| ECN with impact on open orders + old stock, Design Head + Plant Head | No ECN, versioning + one checker | FRD-MFG R-08 |
| One base BOM + variant overrides (31 configs) | Each variant = separate item + BOM | FRD-MFG R-09 |
| Credit-limit / overdue check at SO approval + dispatch, Accounts/MD override | Refused, "no placeholder guard" | FRD-TRADE §11 R1, TSO-UNR-03, #586 |
| Sales invoice, credit note, SO "Invoiced" status, close on invoiced qty | Refused → accounting; SO closes on shipment | FRD-TRADE R2/R3 |
| GST (CGST/SGST/IGST) on PO, RFQ comparison, SO lines | Trade docs carry no tax | TRD-06, FRD-TRADE §11 R5 |
| Debit note / Rejection Note from IQC reject + short | Supplier claim/return only, no DN | R3, RN-054 |
| PO email/WhatsApp to vendor | Print/download only v1 | TRA-OPEN-01 |
| Service PO, Sample PO types | Service PO → assets; no sample PO | R8 |
| PO may exceed PR balance with `po:exceed_pr` + tolerance | Hard refuse | TPR-GRD-04 |
| Issue only against approved MR (+ emergency issue auto-creates MR) | Backflush/staging consume without MR; direct issue without auto-MR | MSI §0, FR-638/639/645 |
| Failed PQC blocks next stage; rework back to same stage with count | Records only; gate (off by default) blocks FG receipt; rework = new order | Q-Q3 |
| Release with shortage only with Production Manager approval | WARN, no approver | Q-PR5 |
| Stock never negative (DB check); approvals append-only at DB | `negative_stock_mode=ALLOW` configurable; approval rows updated in place | 3-22, 13.3-05 |
| AVL hard rule: PO only to approved vendor-item | AVL only enforced if item has AVL rows | 3-16 / 4-26 |
| Material return: 4 steps (prod raises → PM approves → store verifies qty → SM approves) | 2 steps, no verified-qty | C3 |
| Quarantine/Rejected/Scrap/Sample as separate stores | Stock statuses, not stores (same controls) | C-09 |
| Routing mandatory | Routing optional inside BOM | FR-631, #595 |
| Multi-level value-banded approval on every document type | Matrix only for trade docs (#580); core FR-466 never built (#160 closed DUPLICATE) | 3-06 |
| Approver value limit per user + limit recorded + upward escalation, email/WhatsApp | Limits on bands, re-alert same level after 24h, in-app only | 3-04/05/24/25 |
| Production costing material+labour+overhead | Material-only, labour recorded not absorbed | OD-43 |
| Import purchases (cells) | Bill of entry refused | R17 |

## C. Notable PARTIAL gaps inside otherwise-planned tasks (amend the open issue)
- Direct-PO governance: `po:create_without_pr`, category allow-list, mandatory reason, "Direct PO" flag + report.
- PR: HOD-approved / Purchase-approved statuses, approver = requester's HOD, purpose SO/Sample/Stock, SO ref, current-stock column, auto-PR from reorder level / MRP shortage / unfulfillable MR (one-click).
- Gate entry: package count, invoice + vehicle photos. GRN: serial import from vendor Excel; per-serial IQC; COA + photo attachments.
- Segregation: IQC ≠ GRN maker; inspector ≠ own production.
- MR: stage field, batch preference, SO + job-card refs, REPLACEMENT type, over-BOM issue needs higher approval, HOD/Production Manager approver (not stores).
- Material return: photos, defective → vendor rejection linked to MRN/PO + vendor rating.
- Job card booking: operator authorisation, machine, shift, pause, rejected qty separate from rework/scrap, stage consumption, Kanban production board, WIP by stage, plan vs actual.
- BOM: drawing no.+rev, where-used, alternates priority (check), comparison of revisions.
- Labels: MRN no. on put-away label; over-receipt tolerance per item category; approved-make master; vendor contacts; GST rate on item.
- Reports: PR-to-PO ageing, PO price history, direct-PO report, enquiry-to-SO conversion, chassis traceability both ways, audited exports.
- Trial/sample BOM only on Sample production order; FR-545 part-approval blocks the SO line instead of the production order.

## D. Accounting (§12A) — owned by `accounting`, gaps found there
Purchase invoice not bound to MRN; two-way match only (three-way declined v1); DN/CN no stock effect / no auto-proposal; payments + DN/CN lack approval state, value bands unbuilt (acc#39); no manufacturing/WIP/standard cost (T-034); missing s.40A(3)/269ST, Rule 42/43, MSME-1, 30-Nov CN/DN limit, compliance calendar, stock-transfer invoice, petty-cash imprest, cash/bank book named reports, "Verified" step on purchase invoice. Duplicate owners: PO/GRN/quotation/SO/delivery note (accounting built its own vs warehouse-trade), e-way bill + IRN (warehouse-india built vs acc#61), GST engine + TCS (warehouse-india vs accounting-base). PRD cites old Income-tax section numbers and 206C(1H) (omitted 1-Apr-2025) — PRD needs correcting.

## E. Beyond the PRD — not in PRD or design set (industry gaps to raise)
BOM bulk import; BOM revision compare; EV domestic value addition / PMP localisation by BOM; battery serial→VIN traceability + battery EPR (EPR is built in warehouse-india #55); manufacturer Form 22 + VAHAN homologation upload (Form 21 / dealer schemes are dealer-side — out of scope); FAME/PM E-DRIVE subsidy claims needing chassis data; import purchase/bill of entry; tooling/die master; preventive maintenance of machines (PR "Maintenance" purpose has no maintenance module); calibration of QC instruments (QC parameter has "instrument" but no calibration due-date); scrap sale with GST/TCS from Scrap store.

## F. Design set has it, PRD doesn't mention (tell the client)
MRP (#602/#603 — PRD says out of scope v1), blanket orders + call-offs, price lists with floor price, customer part approval, regret letters / lost-sale capture, sales return authorisation, cycle counting, stock transfer, 3PL billing, MOOWR bonded issue, subcontracting order, VAS work order.

## G. Questionnaire (§14) status
- Already answered by design assumption (confirm with client): Q-G3, Q-A3, Q-P4 (≥3 quotes), Q-I3 (CLIENT-DEFAULT AQL), Q-I6, Q-M1/M2/M3/M5/M6, Q-AC1/AC3/AC9.
- Assumed OPPOSITE to the PRD (client must rule): Q-G4 (mobile), Q-A2 (notifications/escalation), Q-P8 (email/WA), Q-I7 (debit note), Q-C4/Q-D3 (credit block), Q-B1 (variants), Q-B6 (ECN), Q-PR5, Q-Q3, Q-PR7, Q-AC11/AC14.
- Unanswered and blocking design: Q-P1/P2/P3, Q-I4, Q-PR2, Q-PR3, Q-Q2, Q-Q4, Q-S1–S4, Q-B3, Q-B5, Q-G1/G2/G5/G6, Q-A1 (partly), Q-A4.

Full requirement-by-requirement matrices with evidence (issue #, FR id, file:line) follow, one slice per section.


## 21 conflicts — industry ruling

Rule applied (user): if the real world requires it, keep it — never remove or weaken it. If the PRD is silent but industry requires it, add it. The PRD wins over a design decision only when the PRD side is also the industry norm.

Outcome codes: **ADD** = the PRD (industry) wins; reverse the design decision. **KEEP+ADD** = keep the design capability and add the PRD behaviour as a configurable option. **KEEP** = the design is the industry norm; keep it and explain to the client.

| # | Topic | PRD says | Design says | Industry norm | Outcome |
|---|---|---|---|---|---|
| 1 | ECN | ECN with impact, Design Head + Plant Head | No ECN (R-08) | IATF 16949 8.5.6.1 / ISO 9001 8.5.6 require controlled engineering change; SAP ECM, Oracle ECO | **ADD** (reverse R-08) |
| 2 | BOM variants | Base BOM + variant overrides | Separate item + BOM per variant (R-09) | Both are used: SAP variant config / super-BOM; Odoo "apply on variant" lines. Variant SKUs still needed for stock/serial | **KEEP+ADD**: keep variant items, add one base BOM with variant-applicable lines |
| 3 | Credit limit at SO + dispatch | Block, Accounts/MD override | Refused (FRD-TRADE R1) | Standard (SAP credit management, Tally credit limit). Accounting already has `AccCreditCheckService` | **ADD**: reuse the accounting credit check, do not rebuild it |
| 4 | Sales invoice / CN / "Invoiced" SO status | Invoice from dispatch, SO closes on invoiced qty | Invoice → accounting; SO closes on shipment | Billing is its own module in every ERP (SAP SD billing ≠ WM); the SO carries delivery status AND billing status | **KEEP+ADD**: invoice stays in accounting; add the dispatch→invoice link plus a billing status on the SO line; close only when both are complete |
| 5 | GST on PO / RFQ / SO lines | CGST/SGST/IGST by place of supply | No tax on trade documents (TRD-06) | Every Indian ERP shows tax on PO/SO (commitment value, approval value, vendor comparison landed cost) | **ADD**: reuse the existing GST engine (warehouse-india / accounting-base), not a third one |
| 6 | Debit note from IQC reject / short | Rejection note + DN request | Supplier return / claim only | The supplier return delivery is the stores document (keep); the DN is required under GST s.34 and is an accounting document | **KEEP+ADD**: keep supplier return; auto-propose the DN into accounting |
| 7 | PO email / WhatsApp | Share from system | Print/download only (TRA-OPEN-01) | Email is standard; WhatsApp is common in India; platform Twilio WhatsApp works | **ADD** (keep print/download) |
| 8 | Service PO, Sample PO | Both types | Service → assets (R8); no sample | Service PO + service entry is standard (SAP item category D): freight, calibration, job charges | **ADD** service PO in trade; sample = PO purpose flag |
| 9 | PO over PR balance | Allowed with `po:exceed_pr` + tolerance % | Hard refuse | SAP/Oracle: configurable tolerance, default 0 | **KEEP+ADD**: default stays refuse (tolerance 0); add permission + tolerance |
| 10 | Issue only against MR | Every issue against approved MR; emergency issue auto-creates MR | Backflush / staging consume without MR | Backflush is industry standard for low-value, high-volume parts (SAP REM, Oracle). MR-only for everything is not | **KEEP+ADD**: keep backflush for BOM lines flagged backflush; MR mandatory for all others; add emergency issue → auto-MR → post-approval |
| 11 | PQC failure | Blocks next stage; rework to same stage, count tracked | Records only; optional gate at FG receipt; rework = new order | IATF 8.7 (nonconforming product segregated); SAP inspection points block the next operation; rework operation on the same order | **KEEP+ADD**: block the next stage per QC-checkpoint setting (default block); add the in-order rework loop + count; keep the rework order for major rework |
| 12 | Release with shortage | Only with Production Manager approval | WARN, no approver | SAP availability check + release authorisation | **KEEP+ADD**: modes WARN / APPROVE / BLOCK, default APPROVE |
| 13a | Negative stock | Never (DB check) | `ALLOW` configurable | Negative stock is a known config (SAP per plant), but auditors and Ind AS 2 valuation dislike it; never for batch/serial | **ADD**: default BLOCK; ALLOW only for non-batch, non-serial backflush consumables, with audit |
| 13b | Approvals append-only | Append-only at DB | Step rows updated in place | Companies (Accounts) Rules 3(1) audit trail; standard workflow history | **ADD** |
| 14 | Approved vendor list | PO only to approved vendor-item | Enforced only if item has AVL rows | IATF 8.4 supplier approval; SAP source list "required" per material | **ADD**: enforce for RM / bought-out / QC-required items; open for consumables (configurable) |
| 15 | Material return chain | Prod raises → PM approves → store verifies qty → SM approves | 2 steps, no verified qty | Store physical verification of received qty is universal; PM approval is common in Indian plants | **ADD** (verified qty + configurable approval steps) |
| 16 | Quarantine / Rejected / Scrap / Sample | Separate non-issuable stores | Stock statuses | SAP stock types (unrestricted / QI / blocked) = status model, plus physical locations | **KEEP**: status model; also allow dedicated locations, and show them to users as "stores". Same controls |
| 17 | Routing | Mandatory released routing | Optional, inside the BOM | SAP/Oracle: routing is a separate reusable master; mandatory for discrete production orders, optional for kitting | **KEEP+ADD**: separate routing master with operation master; mandatory for make items with job cards; optional for kits |
| 18 | Approval matrix on all documents | Configurable per doc type / value / category / plant | Trade docs only; core FR-466 never built | One generic workflow engine for every document type (SAP release strategy, Oracle AME) | **ADD**: one engine for all documents; default single level as in PRD §3 table |
| 19 | Approver limits, escalation, channels | Per-user limit, limit recorded, upward escalation, email | Bands, 24 h same-level re-alert, in-app | Value bands are the norm (SAP release codes); upward escalation + email are norm | **KEEP+ADD**: keep bands; record band/limit used; add upward escalation + email/WhatsApp |
| 20 | Production costing | Material + labour + overhead, cost per unit | Material only, labour not absorbed (OD-43) | **Ind AS 2 / AS 2 require conversion costs (labour + production overhead) in WIP/FG inventory value**; CAS-4 for cost audit | **ADD** (compliance, not optional) |
| 21 | Import purchases | PRD silent (only "multi-currency imports") | Bill of entry refused (R17) | EV makers import cells/motors: bill of entry, BCD, IGST on import, landed cost — standard | **ADD** (industry-required, PRD silent) |

Result: 13 ADD · 7 KEEP+ADD · 1 KEEP. No existing design capability is removed.

## Also applied by the same rule
- Design-set features the PRD never mentions (MRP, blanket orders + call-offs, price lists + floor price, customer part approval, regret / lost sale, sales return authorisation, cycle count, stock transfer, subcontracting, MOOWR bonded, VAS, 3PL billing, battery EPR): **KEEP all**; tell the client they exist. MRP stays, but PRD v1 wants manual planning, so ship it off by default.
- Industry gaps neither side covers. **Required** (add): import / bill of entry (#21), QC instrument calibration due-date, Ind AS 2 conversion costing (#20), battery serial → VIN traceability, manufacturer-side vehicle compliance data (Form 22 initial certificate of compliance + VAHAN homologation upload — the OEM's obligation, not the dealer's), scrap sale with GST. **Recommended** (add, lower priority): BOM bulk import, BOM revision compare, tooling/die master, machine preventive maintenance, domestic-value-addition (PMP) by BOM, subsidy-claim chassis data.

## Dealer-module fence (user, 2026-10-25)
The dealer vertical (dealer, automotive, services, accessories, insurance) is NOT part of this scope: it is not reused, not edited, and not a source of "existing CRM". Warehouse stays a generic manufacturing + storage ERP that can also serve an automotive manufacturing unit.
- "Variant" here always means a **manufacturing product configuration** (colour, battery type, MS/SS frame, with/without charger) on the item/BOM in warehouse-manufacturing — never the dealer/automotive vehicle-model variant master.
- PRD §4A "existing CRM" (leads, quotations) = the client's Voyager CRM, not classic `dealer`. The pre-SO chain is owned by warehouse-trade (#585 enquiry/quotation, #586 SO); leads may link via `leads-base` only.
- Warranty registry feed (PRD §12): do NOT feed classic `services` (`ServiceVehicle` is a dealer-workshop record). Instead the manufacturer keeps a unit/serial registry (chassis ↔ part serials, sale date, invoice) in warehouse-manufacturing that a warranty function can read.
- Dropped as dealer-side: Form 21 (dealer sale certificate), dealer pricing schemes, dealer secondary stock. A dealer is just a customer (counterparty) here.
- Item #3 credit check reuses the **accounting** credit check, not anything in dealer.
- PRD tax references: use Income-tax Act 2025 section numbers; drop TCS 206C(1H) (omitted 1 Apr 2025).


## Fit scorecard

Warehouse scope 629: built 101 (16%), designed 202, partial 174, missing 131, declined 20, design-only 1 -> 326 gaps; fit 62%. Accounting 160 -> 55 gaps. Total 381.
