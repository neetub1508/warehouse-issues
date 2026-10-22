# FRD-TRADE — `warehouse-trade`: manufacturing purchase and sales, mirrored

**Date** 2026-10-22 · **Area** TRADE · **Phase** `P9` · **Status** derived v0, not yet through the
`functional-reviewer` · **ID ranges** `FR-540`–`FR-619`, `WS-280`–`WS-319`, `WH-SC-480`–`WH-SC-599`,
`OD-30`–`OD-39` (`DECISIONS.md` D-16 allocation). Unused numbers stay unused.

**Sources.** `reviews/R27-client-p2p-stores-gap.md` (`RM-001`…`RM-006`, `RM-030`, `RM-040`…`RM-045`) ·
`reviews/R28-manufacturing-storage-retarget-impact.md` §4 groups A + D, §5 (`RN-030`, `RN-035`), §6,
§8b (`RN-053`, `RN-054`, authoritative) · `reviews/R7-logistics-supply-chain-seam.md` §418-424 (rows 9–15:
PR, RFQ, PO, amendment, price agreement, agreed lead time were owned by a supply-chain module that does
not exist — `RM-025`; **this module is that owner now**) · `issues/p6-05.md` (receipt facts are emitted
as evidence; the scorecard belongs to the supply-chain owner) · `issues/p1-08.md` (counterparties are a
thin identity; commercial terms live elsewhere — here).

**Reference practice consulted** (the R27 `RM-027` gap: no lens walked a standard process): SAP MM
outline agreements — quantity/value contracts with release orders vs scheduling agreements with
delivery schedules, release (approval) strategy; SAP SD inquiry → quotation → order, customer
scheduling agreements, customer-material info record; Oracle Purchasing standard / blanket / contract
/ planned POs with releases; Odoo purchase agreements (blanket order, call for tender); ERPNext RFQ,
supplier quotation, supplier scorecard (weighted criteria, standings); Tally/Indian practice — indent,
comparative statement, L1 award, rate contract, PO amendment number, regret letter, MSMED Act §15
(payment within 15 days, or the agreed period capped at 45 days, of acceptance; Udyam registration;
Income-tax §43B(h)).

---

## 1. What this module is

`warehouse-trade` holds the **commercial commitment** with a supplier or a customer. Core `warehouse`
holds the **execution** of that commitment: gate entry, GRN, QC, MRN, stores, pick/pack/ship. The rule
from R7 §3.1 (`G-026`) decides every split in this file:

> *Commitment ⇒ trade. Quantity ⇒ warehouse. Obligation (money) ⇒ accounting (deferred).*

```
warehouse-base   (ledger, items, counterparties, code lists, number series, outbox)
   └─ warehouse  (core) — PO execution document (FIXED / OPEN / BLANKET_RELEASE + schedule lines, p8-01),
   │                      demand order with SO ref + customer schedule (p8-02), gate entry (p8-03),
   │                      GRN + bill (p8-04), QC (p8-05/06/07), MRN (p8-08), material requisition (p8-09),
   │                      store issue/return (p8-10/11), RMA, supplier return, shipping
   └─ warehouse-trade (this) — PR · RFQ · vendor quotation · comparative statement · award · rate contract ·
                         purchase order (commercial) · releases · amendments · acknowledgement · expediting ·
                         vendor rating — and the sales mirror: enquiry · customer quotation · win/loss ·
                         price list · sales rate contract · sales order (commercial) · dispatch releases ·
                         amendments · acknowledgement · commitment tracking · return authorisation ·
                         customer rating
```

**What it never does.** It never writes a `wh_` or `whb_` row except code-list, document-type,
number-series and print-template-kind seed rows carrying `owning_module = 'warehouse-trade'` under the
owning-module guard (`RL-003`). It never posts a movement. It never computes tax, never converts
currency, never raises an invoice, debit note or credit note, and never checks credit (§10).

## 2. Personas

| Persona | Is | Does in this module |
|---|---|---|
| **Department requester** | a person in a production, maintenance or utility department | Raises a manual PR; sees its conversion; cannot approve their own PR |
| **Stores clerk** | a person | Raises a PR from a material-requisition shortage (`p8-09`); never edits a PO |
| **Buyer** | a person in purchase | Consolidates PR lines, issues RFQs, captures vendor quotations, prepares the comparative statement, raises POs and releases, expedites, records acknowledgements, drafts amendments |
| **Purchase manager / approver** | a person | Approves PR, award, rate contract, PO, release, amendment within the approval matrix; never approves what they made |
| **Sales executive** | a person | Records enquiries, prepares quotations, records win/loss, raises SOs |
| **Sales manager / approver** | a person | Approves quotations below floor, SOs, amendments, return authorisations |
| **Dispatch planner** | a person in sales/logistics | Releases due customer schedule lines to the FG store (`p8-02`), tracks commitments |
| **Quality inspector** | a person (core) | Produces the QC facts vendor rating reads; no trade action |
| **Trade administrator** | a person | Approval rules, evaluation schemes, AVL, profiles, code lists, T&C templates |
| **Auditor** | a person | Read-only across every trade screen, **no `:export`** (user decision 2026-09-15) |
| **System (job)** | a principal | Expiry, reminder, evaluation and close jobs; never approves |

## 3. Reference process catalogue (`RM-040`, `RM-043`)

Every row is covered by an FR here, assigned to another area by id, or refused in §10.

| # | Purchase step (SAP / Oracle / Odoo / ERPNext / Indian name) | Owner | FR | Sales twin | Owner | FR |
|---|---|---|---|---|---|---|
| C1 | Purchase requisition / indent | trade | FR-556–561 | Sales enquiry (inquiry) | trade | FR-598 |
| C2 | Requisition from stores shortage | trade ← core `p8-09` | FR-557 | Enquiry from customer RFQ | trade | FR-598 |
| C3 | Requisition from MRP / reorder | trade ← core suggestion (`OD-31`) | FR-556 | Forecast / blanket schedule to MRP | core `p8-02` (`OD-32`) | FR-611 |
| C4 | RFQ to N vendors (call for tender) | trade | FR-562–563 | — (we receive the RFQ: C1) | — | mirror row M3 |
| C5 | Vendor quotation capture | trade | FR-564–565 | Customer quotation (we issue) | trade | FR-599–600 |
| C6 | Comparative statement, L1 | trade | FR-566 | Quotation version comparison + win/loss | trade | FR-601 |
| C7 | Award with reason | trade | FR-567–569 | Won / lost with reason | trade | FR-601 |
| C8 | Rate contract / outline agreement (value/qty contract) | trade | FR-570–574 | Customer rate contract / price list | trade | FR-602–604 |
| C9 | Standard (fixed) PO | trade → core `p8-01` | FR-575–577 | Standard SO | trade → core `p8-02` | FR-605–606 |
| C10 | Open PO / contract release order | trade → `p8-01` | FR-578 | Open SO / call-off | trade → `p8-02` | FR-605, FR-607 |
| C11 | Blanket / scheduling agreement + delivery schedule | trade → `p8-01` | FR-579–580 | Customer scheduling agreement + delivery schedule | trade → `p8-02` | FR-605, FR-607, FR-611 |
| C12 | Release (approval) strategy / matrix | trade | FR-548–555 | Same engine | trade | FR-548–555 |
| C13 | PO amendment + version | trade | FR-590–593 | SO amendment + version | trade | FR-590–593 |
| C14 | PO acknowledgement / order confirmation from supplier | trade | FR-586 | Order acknowledgement to customer | trade | FR-606 |
| C15 | Expediting / follow-up | trade | FR-587 | Delivery commitment tracking | trade | FR-610 |
| C16 | Short-close | trade → core | FR-588–589 | Short-close | trade → core | FR-609 |
| C17 | Gate entry against PO | core `p8-03` | FR-581 | Outward gate pass | core `p8-03` | FR-608 |
| C18 | GRN with bill no/date/billed qty | core `p8-04` | FR-581 | Dispatch / shipment, challan / e-way bill | core + `warehouse-india` | FR-608 |
| C19 | QC, reject → supplier return | core `p8-05`…`p8-07` | FR-613 | Customer return authorisation → RMA | trade → core RMA (`OD-33`) | FR-612 |
| C20 | Vendor evaluation / scorecard | trade | FR-594–597 | Customer rating / OTIF | trade | FR-614 |
| C21 | Approved vendor list / source list | trade | FR-544 | Customer part approval (customer-material info) | trade | FR-545 |
| C22 | Supplier master commercial extension (block, MSME, lead time, terms) | trade | FR-542 | Customer master extension | trade | FR-543 |
| C23 | Invoice verification, 3-way match | accounting / core `P5-10` | refused here §10 R2 | Billing / invoice | accounting | §10 R2 |
| C24 | Debit / credit note | accounting | §10 R3 | Debit / credit note | accounting | §10 R3 |
| C25 | Payment, MSME due date | accounting | §10 R4 | Credit limit / credit check | accounting | §10 R1 |

## 4. Requirement catalogue

Rows use the shape of `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` §2. **Module** `trade` = `warehouse-trade`;
`app` = core `warehouse`. **Ver** `v1`: D-16 sequences P7–P10 into the pre-launch build (no clients,
`RN-052`); if SPINE maps P9 to a later release unit the column changes in one place. **Ph** `P9`.

### 4.1 Module and masters *owner: trade*

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-540** | `warehouse-trade` is a **sibling module**: package `ai.warehousetrade`, band `V550000`–`V559999`, prefix `wht_`, switch `enable.warehouse.trade` read by `@ConditionalOnExpression`. It depends on platform + `warehouse-base` + `warehouse`. Every FK points **down** (`wht_` → `wh_`/`whb_`/platform); no `wh_`/`whb_` table, entity, service or route references `wht_`, enforced by `ArchitectureInvariantsTest`. A Mode-A install without it behaves exactly as before, and core PO / demand-order screens keep working for documents core creates itself | trade | v1 | P9 | `RN-053` `RM-041` |
| **FR-541** | **One party identity.** Suppliers and customers are `whb_counterparties` with a `SUPPLIER` / `CUSTOMER` role link. Trade adds **profile extension** rows (one per counterparty × company × side); it never creates a second supplier or customer master. A profile for a counterparty without the matching role link is refused with `422 TRADE_COUNTERPARTY_ROLE_MISSING` | trade | v1 | P9 | `G-027` `FR-119` |
| **FR-542** | **Supplier trade profile**: `is_purchase_blocked` + block reason + blocked by/at (block and unblock are maker–checker), MSME category (code list: `MICRO`/`SMALL`/`MEDIUM`/`NOT_MSME`), Udyam registration number (format `UDYAM-XX-00-0000000`), classification date, default lead time days, min order value, default currency, payment terms (code + days, **recorded only**), delivery terms, freight terms. A `MICRO`/`SMALL` supplier whose payment-terms days exceed 45 shows a warning on the profile and on every PO, and the buyer must tick an acknowledgement that is stored; trade does not track payment (§10 R4) | trade | v1 | P9 | `RM-006` R28 A8 |
| **FR-543** | **Customer trade profile** (mirror of FR-542): `is_sales_blocked` + reason (maker–checker), customer category, default currency, payment terms (recorded only), delivery and freight terms, default ship-to address (`whb_counterparty_addresses`), default dispatch site, `customer_po_required`, `requires_part_approval`. **No credit limit** (§10 R1) | trade | v1 | P9 | R28 D |
| **FR-544** | **Approved vendor list (AVL)** per company × item (or item category) × supplier: status code (`APPROVED`, `PROVISIONAL`, `SUSPENDED`, `DISQUALIFIED`), valid from/to, sole-source flag, approver and reason; changes are maker–checker. Setting `warehouse.trade.avl.enforcement` = `WARN` \| `REFUSE` (default `REFUSE`) applies when the item has any AVL row: inviting, awarding or ordering from a supplier not `APPROVED`/`PROVISIONAL` for the date. `SUSPENDED` and `DISQUALIFIED` are refused under either setting | trade | v1 | P9 | R28 A8 |
| **FR-545** | **Customer item reference** (the customer-material info record): customer × item → customer part number, drawing number + revision, customer approval status (`APPROVED`, `PENDING`, `REJECTED`, e.g. PPAP), valid from/to. When the customer profile has `requires_part_approval`, an SO or quotation line for an item without a current `APPROVED` reference is refused with `422 TRADE_CUSTOMER_PART_NOT_APPROVED` | trade | v1 | P9 | mirror of FR-544 |
| **FR-546** | Every extensible vocabulary (reasons, terms, statuses-as-codes for AVL, MSME category, charge types, enquiry sources) is a `whb_code_lists` row set with `owning_module = 'warehouse-trade'`, seeded with the owning-module guard; an install may add values. **No `CHECK` on an extensible value; document status columns carry no `CHECK` (`D-10`)** — the service is the only enforcement point | trade | v1 | P9 | `D-10` `RL-003` |
| **FR-547** | **Numbering.** Each trade document type has a `whb_document_types` row and draws non-gapless (`is_gapless = false`; these are not tax documents) numbers from `whb_number_series` per company (optionally per site) with `YEARLY` (financial-year) reset. A number is issued at the transition named per document in its contract (PR at submit, RFQ at issue, vendor quotation at capture, comparative statement at submit, rate contract / price list at submit, PO and SO at submit, release at release, amendment at submit, return authorisation at submit). Drafts show `DRAFT` and are never numbered. The PO's supplier-facing number is resolved by `OD-30` | trade | v1 | P9 | `RL-004` |

### 4.2 Approval matrix *owner: trade* — contract `trade-approval-matrix`

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-548** | **One approval engine** for every trade document type (`PR`, `CS`, `PRC`, `PO`, `PO_RELEASE`, `PO_AMENDMENT`, `PO_SHORT_CLOSE`, `SQ`, `SRC`, `PRICE_LIST`, `SO`, `SO_AMENDMENT`, `SO_SHORT_CLOSE`, `SRA`, `AVL`, `PROFILE_BLOCK`). A rule names document type × company × optional site × optional department × optional item category × **currency**, a value band and/or a quantity band, optional conditions (`manual_rate`, `non_l1_award`, `below_floor_price`, `discount_over_pct`), and ordered levels; each level names a role or users and `ANY_ONE` / `ALL`. The most specific matching rule wins; ties are refused at rule save | trade | v1 | P9 | R28 A6 |
| **FR-549** | **Maker ≠ checker at every level.** The document's maker, and anyone who has already acted on an earlier level of the same request, cannot act on a level — refused with `403 TRADE_APPROVAL_SELF` even for a holder of `:approve` or `ADMIN` | trade | v1 | P9 | `FR-408` |
| **FR-550** | **No rule ⇒ refusal, never auto-approval.** Submitting a document no rule covers is refused with `422 TRADE_NO_APPROVAL_RULE` naming the document type, value and currency. A rule may have **zero levels**: the document is approved at submit by `SYSTEM` with the rule id recorded (the seeded default for `PO_RELEASE` within an approved agreement) | trade | v1 | P9 | — |
| **FR-551** | Approve, reject and return-for-changes; reject and return need a comment. Reject → `REJECTED`; return → `DRAFT`. A resubmission opens a **new** approval request; the old one is kept. Every action writes `whb_audit_events` | trade | v1 | P9 | — |
| **FR-552** | **Delegation**: an approver records a dated delegate; the delegate acts "on behalf of" and the record keeps both names. A delegation to the request's maker is refused | trade | v1 | P9 | — |
| **FR-553** | An approved document changes **only by amendment** (FR-590), which takes its own approval; the amendment's band is evaluated on the **new total** and on the **delta**, and the stricter applies | trade | v1 | P9 | R28 A5 |
| **FR-554** | A step pending longer than `warehouse.approval.pending_alert_hours` (default 24) alerts the level's approvers once per episode; nothing is ever auto-approved by time | trade | v1 | P9 | `RQP-T3-03` pattern |
| **FR-555** | **My Approvals** (WS-285) lists the user's pending steps across all trade document types with a read-only preview and approve / reject / return; filters by document type, site, value | trade | v1 | P9 | — |

### 4.3 Purchase requisition *owner: trade* — contract `trade-purchase-requisition`

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-556** | **PR document**: company, requesting site, deliver-to location (optional), department (platform `departments`), cost object (the `p8-10` vocabulary: department / cost centre / production order), requested by, required-by date, priority, justification, source (`MANUAL`, `STORES_SHORTAGE`, `REPLENISHMENT`, `MRP`). Lines: item, quantity, UoM, required date, suggested supplier, estimated rate, source line reference, notes | trade | v1 | P9 | `RM-001` |
| **FR-557** | **PR from shortage.** From the core material-requisition shortfall (`p8-09`) or a core replenishment suggestion (incl. `MRP` source, `OD-31`), "Raise PR" creates PR lines linked to the source line. One source line feeds **at most one** non-cancelled PR line (partial unique index). The quantity defaults to the shortfall; raising it needs a justification | trade | v1 | P9 | `RM-001` `RM-015` |
| **FR-558** | PR approval runs the matrix on Σ (qty × estimated rate) in the company currency; a PR with no estimates is matched on quantity bands. The estimated rate defaults from the active rate contract, else the last approved PO rate for the item, else blank | trade | v1 | P9 | — |
| **FR-559** | **Consolidation.** The requisition workbench (WS-287) lists approved open PR lines across PRs, groupable by item, site and suggested supplier. The buyer selects lines and creates **one** RFQ, **one** PO, or a release against an agreement. A junction records each PR line × target line × quantity | trade | v1 | P9 | — |
| **FR-560** | **Partial conversion.** A PR line converts in parts; Σ allocated ≤ approved − cancelled, checked under a row lock on the PR line. Line status `OPEN` → `PARTIALLY_ORDERED` → `ORDERED`; header follows. The remainder can be closed short with a reason. The requester is notified at each conversion and at close-short | trade | v1 | P9 | — |
| **FR-561** | A PR is cancellable before any allocation; after one, only its open remainder can be closed. A target line's cancellation releases its allocation back to the PR line (the PR line returns to open for that quantity) | trade | v1 | P9 | — |

### 4.4 RFQ, vendor quotation, comparative statement, award *owner: trade* — contract `trade-rfq-award`

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-562** | **RFQ**: lines from PR lines or manual (item, qty, UoM, required date, specification note), invited suppliers, response due date, deliver-to site, terms. At issue: at least `warehouse.trade.rfq.min_suppliers` (default 3) invited, or a limited-source reason code + note; every invitee passes FR-544 and is not purchase-blocked | trade | v1 | P9 | `RM-002` |
| **FR-563** | Issue prints one RFQ document **per supplier** (never showing another supplier) and records sent-at and channel per invitee. Invitee response status: `INVITED` → `RESPONDED` / `DECLINED` (reason) / `NO_RESPONSE` (set at close). A reminder goes to the buyer `warehouse.trade.rfq.reminder_days` before the due date for invitees still `INVITED` | trade | v1 | P9 | — |
| **FR-564** | **Vendor quotation** against an RFQ or unsolicited: supplier's ref and date, valid until, currency, payment / delivery / freight terms, per line offered qty, unit price, discount %, MOQ, lead time days, alternative item (flagged, never silently substituted), free-of-charge flag with reason; header charges (code list, recorded amounts, no tax). The supplier's document attaches through platform documents. A revision creates **version n+1**; only the latest non-withdrawn version counts | trade | v1 | P9 | `RM-002` |
| **FR-565** | **Sealed mode** (setting `warehouse.trade.rfq.sealed_until_due`, default `false`, `OD-37`): while the RFQ is open and before its due date, captured prices are hidden from every user except the capturer and the comparative statement cannot be prepared | trade | v1 | P9 | — |
| **FR-566** | **Comparative statement**: a backend-computed matrix RFQ line × supplier — net price, landed price (net + allocated header charges, **excluding tax**), lead time, payment days, MOQ, vendor grade (FR-597), last PO rate, current contract rate — with L1/L2/L3 rank per line by landed price. Only same-currency quotations are ranked together; a foreign-currency quotation is shown unranked (`OD-34`) | trade | v1 | P9 | `RM-002` |
| **FR-567** | **Recommendation and award** per line; **split award** allowed with Σ awarded ≤ RFQ line qty. Awarding other than L1 needs an award reason code + note and sets the `non_l1_award` approval condition. The award is approved through the matrix on the awarded value | trade | v1 | P9 | — |
| **FR-568** | On award approval, per awarded supplier the buyer's chosen **award target** is drafted: FIXED PO, OPEN PO, BLANKET agreement or purchase rate contract, prefilled from the quotation. PR allocations move from the RFQ lines to the new lines. Unawarded quotations become `NOT_AWARDED`; the RFQ becomes `AWARDED` or `PARTIALLY_AWARDED` | trade | v1 | P9 | — |
| **FR-569** | A quotation whose `valid_until` is before the award date cannot be awarded; the buyer records the supplier's validity extension as a new version | trade | v1 | P9 | — |

### 4.5 Purchase rate contract *owner: trade* — contract `trade-rate-contract`

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-570** | **Purchase rate contract** per supplier: company, valid from/to, currency, terms, lines item × UoM × rate with optional **quantity slabs** (`from_qty` → rate, evaluated on the order line quantity, `OD-35`), optional ceiling quantity per line with consumed quantity tracked from approved PO lines and releases. Approval through the matrix; numbering FR-547 | trade | v1 | P9 | `RM-006` `RN-030` |
| **FR-571** | At most one approved rate per (company, supplier, item, UoM) at any date — a database `EXCLUDE` over the dated price rows. Different suppliers may each hold a contract for the same item | trade | v1 | P9 | — |
| **FR-572** | **Price revision** writes a new dated price row (`effective_from`) through a contract amendment with approval; history is never overwritten. Approved POs keep their rate; an OPEN/BLANKET agreement whose `price_basis = AT_RELEASE` prices each release at the rate effective on the release date, else at the agreement rate | trade | v1 | P9 | R28 A4 |
| **FR-573** | **One price-resolution service** (backend): rate contract (date, slab) → valid awarded quotation → manual. The last PO rate is shown as reference only, never defaulted. A typed or overridden rate sets `price_source = MANUAL` and the `manual_rate` approval condition | trade | v1 | P9 | `RM-006` |
| **FR-574** | Contract expiry alerts `warehouse.trade.contract.expiry_alert_days` (default 30) before `valid_to`; an expired contract prices nothing; termination is dated with a reason and needs approval | trade | v1 | P9 | — |

### 4.6 Purchase order *owner: trade (commercial) → core (execution)* — contract `trade-purchase-order`

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-575** | **Three PO types**, immutable after submit: `FIXED` — quantity and rate fixed, one or more dated schedule lines; `OPEN` — rate fixed, quantity open (optional ceiling qty / value), validity, call-off releases; `BLANKET` — agreement with a delivery schedule (item × qty × date) within validity, released schedule line by schedule line | trade | v1 | P9 | `RM-003` `RM-004` `RM-005` |
| **FR-576** | Header: company, supplier, buyer, order date, deliver-to site, currency, payment / delivery / freight terms (recorded), rate contract ref, award ref, validity (OPEN/BLANKET), ceilings, `price_basis`, T&C template, notes, MSME acknowledgement (FR-542). Line: item, supplier part no (from `whb_item_supplier_sources`), UoM, qty (FIXED/BLANKET > 0; OPEN null), unit price, discount %, `price_source`, over/under delivery tolerance %, tax classification code (recorded), free-of-charge flag | trade | v1 | P9 | — |
| **FR-577** | **One core PO per trade PO, created at approval.** Approval calls `WhPurchaseOrderPort.createOrder` (`p8-01`) **in the approval transaction** with `initialStatus = APPROVED`, `approvedByUserId` = the last trade approver (core records `approval_source = SOURCE_MODULE`), `source_module = 'warehouse-trade'`, `source_document_type/id`, `source_document_ref` = the trade PO number, an idempotency key and the lines, rates (`rate_source = AGREEMENT` + contract ref where priced from a contract), tolerances and schedule lines. FIXED schedule lines go as `FIRM`. A port refusal rolls the approval back and shows the core reason on the trade screen | trade | v1 | P9 | `RN-053` |
| **FR-578** | **OPEN** approval creates a core PO of type `OPEN` (rates, no quantities). Each **release** (call-off) adds dated quantities through the port. Σ released ≤ ceiling; a release dated after `valid_to` is refused; after validity no release is accepted and open released quantities continue to be received | trade | v1 | P9 | `RM-004` |
| **FR-579** | **BLANKET**: Σ schedule qty = line agreed qty and every date within validity, checked at submit. Approval creates **one** core PO of type `BLANKET_RELEASE` with `agreement_ref` = the agreement number and the whole schedule as `FORECAST` lines (core receives only `FIRM` lines, `POS-UNR-02`). Each **release** firms whole or split schedule lines through `releaseSchedule` with `release_ref` = the release number. Schedule lines carry zone `FIRM` / `TENTATIVE` (`warehouse.trade.firm_zone_days`, default 14). A job **proposes** releases for schedule lines entering `warehouse.trade.release_horizon_days`; it never releases | trade | v1 | P9 | `RM-005` |
| **FR-580** | **Release document**: number, release date, lines (schedule line or call-off item × qty × date), approval (`PO_RELEASE`; seeded zero-level rule within an approved agreement), print *Schedule Release* to the supplier | trade | v1 | P9 | — |
| **FR-581** | **Hand-off to stores.** Gate entry (`p8-03`) and GRN (`p8-04`) run against the core PO; trade's PO detail shows gate entries, GRNs with bill no/date/billed qty, QC results, supplier returns and claims **read-only from core**. Trade's fulfilment state (`NOT_STARTED` / `PARTIAL` / `COMPLETE`) is **derived from core quantities on read, never stored** (`FR-123` layered truth) | trade | v1 | P9 | `RM-007` `RM-008` |
| **FR-582** | Over/under delivery tolerance per line is passed to core (over-receipt guard is core's); under-tolerance marks a line *short-close suggested* when the received quantity is within it | trade | v1 | P9 | — |
| **FR-583** | **Cancel** a PO only while nothing is received or on an open gate entry (`getReceiptPosition`); the port cancels the core PO in the same transaction. Otherwise the only exit is short-close (FR-588). Trade registers a `PurchaseOrderChangeGuard` / `DemandOrderChangeGuard` bean (`p8-01` `POS-GRD-08`, `p8-02`), so a trade-created core PO or demand order refuses manual edit, approve, cancel and close on core screens with `409 PO_OWNED_BY_SOURCE_MODULE`; receipts and dispatches run normally | trade | v1 | P9 | R28 §6 guard seam |
| **FR-584** | **Terms & conditions templates** per company × document type (PO, SO, RFQ, quotation), versioned; the version used is frozen on the document and printed | trade | v1 | P9 | — |
| **FR-585** | A supplier blocked after approval: new releases and quantity-increasing amendments are refused with `422 TRADE_SUPPLIER_BLOCKED`; receipts against released quantities continue (core's decision) | trade | v1 | P9 | — |

### 4.7 Acknowledgement, expediting, short-close *owner: trade* — contract `trade-purchase-order`, `trade-sales-order`

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-586** | **Supplier acknowledgement**: ack date, supplier ref, `ACCEPTED` / `ACCEPTED_WITH_CHANGES` / `REJECTED`, per schedule line confirmed date and qty. Differences are shown side by side; with changes, the buyer either accepts (an amendment is drafted from the differences) or disputes (follow-up logged). The agreed dates never change except by amendment | trade | v1 | P9 | — |
| **FR-587** | **Expediting** (WS-295): due and overdue schedule lines (site timezone, `FR-439`), follow-up log (date, contact, mode, supplier promised date, remarks, next follow-up), reminders on next-follow-up date and `warehouse.trade.expedite.days_before` (default 3) before due. The supplier's promised date is stored apart from the agreed date | trade | v1 | P9 | — |
| **FR-588** | **Short-close** at line or header with reason (`PO_SHORT_CLOSE` approval, seeded zero-level); the port closes the open quantity in core; OPEN/BLANKET short-close cancels unreleased schedule lines and closes open releases | trade | v1 | P9 | R28 A |
| **FR-589** | **Auto-close**: a PO becomes `CLOSED` when every line is complete or short-closed and no release is open; an OPEN/BLANKET past validity with nothing open closes by the nightly job | trade | v1 | P9 | — |

### 4.8 Amendments and versions *owner: trade* — contract `trade-order-amendment`

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-590** | **Amendment document** per PO or SO: quantity, rate, dates, schedule lines, add line, cancel line, terms, validity extension, ceilings; reason code; approval `PO_AMENDMENT` / `SO_AMENDMENT` on new total and delta (FR-553). **One open amendment per order**; while it is open, releases on the affected lines are refused | trade | v1 | P9 | `RM-005` R28 A5 |
| **FR-591** | Guards: new qty ≥ received (dispatched) + in-flight (open gate entry / unposted GRN / released-not-received, or released-not-shipped); a rate change applies only to un-received quantity (`OD-36`); type, counterparty, company and currency are not amendable | trade | v1 | P9 | — |
| **FR-592** | On approval: `version_no` + 1, a header + line **snapshot** row set (no JSON), the port pushes the change to core (core PO / demand order), the print is marked *Amendment No. n dated …*, and the counterparty acknowledgement resets to pending | trade | v1 | P9 | — |
| **FR-593** | Version history: list, compare any two versions field by field (backend diff), reprint any version | trade | v1 | P9 | — |

### 4.9 Vendor evaluation *owner: trade* — contract `trade-counterparty-evaluation`

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-594** | **Evaluation scheme** per company × side: criteria chosen from a fixed metric catalogue with weights summing to 100 — purchase: `DELIVERY_OTIF`, `QUALITY_ACCEPTANCE`, `PRICE_VARIANCE`, `RFQ_RESPONSE`, `ACK_TIMELINESS`; sales: FR-614 — and grade bands (code list, e.g. A ≥ 85, B ≥ 70, C ≥ 50, D) | trade | v1 | P9 | R28 A7 |
| **FR-595** | **Evaluation run** per period (`MONTHLY` / `QUARTERLY`) computes scores in the backend from core receipt facts (`p6-05`: on-time, short, damaged), core QC accepted vs inspected (`p8-06`), trade schedule dates and rates; a published run is immutable, recalculation creates a new run superseding it | trade | v1 | P9 | `FR-142` |
| **FR-596** | Grade at or below `warehouse.trade.evaluation.review_grade` raises an AVL review task to the trade administrator; the AVL is **never** suspended automatically | trade | v1 | P9 | — |
| **FR-597** | The latest published grade shows on the comparative statement, the PO and the AVL | trade | v1 | P9 | — |

### 4.10 Sales enquiry, quotation, win/loss *owner: trade* — contract `trade-sales-enquiry-quotation`

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-598** | **Sales enquiry**: customer, customer enquiry ref + date, source (code list), quote-by date, sales executive, lines (item, customer part no via FR-545, qty, UoM, required date, target price, specification note). `REGRETTED` (decline to quote) needs a reason and prints a regret letter | trade | v1 | P9 | R28 D |
| **FR-599** | **Customer quotation**: versions, valid until (default `warehouse.trade.quotation.validity_days` = 30), currency, terms, lines priced by FR-604 with discount %, lead time / promised date; quotation below floor price, or above `warehouse.trade.sales.discount_approval_pct`, carries the approval condition | trade | v1 | P9 | — |
| **FR-600** | Send/print marks the version `SENT`; a revision supersedes it with version n+1; only the latest `SENT` version can be won; the expiry job marks `EXPIRED` past `valid_until` | trade | v1 | P9 | — |
| **FR-601** | **Win/loss**: `WON` drafts an SO (FIXED/OPEN/BLANKET) or a sales rate contract from the quotation; `LOST` records loss reason, competitor name and competitor price (optional). The win/loss analysis (WS-300) shows hit rate and lost value by reason, customer, item and executive; competitor bids are never compared line by line (§10 R10) | trade | v1 | P9 | — |

### 4.11 Sales pricing *owner: trade* — contract `trade-rate-contract`

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-602** | **Price list**: code, currency, validity, applicability (all customers or customer categories), item × UoM dated prices with optional slabs, floor price per item; approval `PRICE_LIST` | trade | v1 | P9 | — |
| **FR-603** | **Sales rate contract** per customer: the mirror of FR-570–FR-572 — validity, slabs, ceiling with consumption, `EXCLUDE` against overlap, dated revisions by amendment | trade | v1 | P9 | — |
| **FR-604** | **One sales price-resolution service**: customer rate contract → customer-category price list → general price list → manual (`price_source`). A price below the floor sets `below_floor_price` | trade | v1 | P9 | — |

### 4.12 Sales order and dispatch *owner: trade (commercial) → core (execution)* — contract `trade-sales-order`

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-605** | **Three SO types** (mirror of FR-575): `FIXED`, `OPEN` (rate fixed, quantity by customer call-off), `BLANKET` with a **customer delivery schedule**. Header: customer, customer PO no + date (required by profile flag; a duplicate (customer, customer PO no) on a non-cancelled SO is refused), sales executive, ship-to, dispatch site, currency, terms, price refs, validity, ceilings. **One core demand order per SO**, created at approval through `WhDemandOrderPort.createDemand` (`p8-02`) with `sales_order_ref`, `customer_po_ref/date` and the schedule: FIXED as `FIRM`, BLANKET as `FORECAST`, OPEN with none until a call-off | trade | v1 | P9 | R28 D1 |
| **FR-606** | SO approval through the matrix; **order acknowledgement** printed and sent with committed dates per schedule line, status `ACKNOWLEDGED` | trade | v1 | P9 | — |
| **FR-607** | **Dispatch planning** (WS-305): due schedule lines by dispatch site and horizon, with backend-computed available-to-promise from core positions; the planner releases whole or part lines into a **dispatch release**, which firms them on the SO's core demand order through `releaseSchedule` (`release_ref` = release number); core allocates firm in-horizon quantity (`warehouse.outbound.schedule_allocation_horizon_days`) and picks / ships it. Release qty > open schedule qty is refused; a shortfall is shown, never blocked | trade | v1 | P9 | `RN-053` |
| **FR-608** | SO fulfilment (released, picked, shipped, delivered) is **derived from core** demand orders and shipments on read; outward gate pass is `p8-03`, challan / e-way bill is `warehouse-india` | trade | v1 | P9 | R28 D2 D3 |
| **FR-609** | SO cancel / short-close mirror FR-583 / FR-588 through the `p8-02` port (cancels unreleased schedule and open demand remaining) | trade | v1 | P9 | — |
| **FR-610** | **Delivery commitment tracking** (twin of expediting): schedule lines due within `warehouse.trade.sales.at_risk_days` that are unreleased or short on ATP; internal follow-up log; customer-informed revised date stored apart from the committed date | trade | v1 | P9 | — |
| **FR-611** | **Customer schedule revision** for BLANKET: a revised schedule (screen or CSV import with dry-run) becomes an SO amendment; changes inside the firm zone are flagged and counted for FR-614. Unreleased schedule lines live on the core demand order as `FORECAST` lines, which MRP reads and which never reserve stock (`p8-02`, `POS-UNR-03`; closes `OD-32`) | trade | v1 | P9 | — |

### 4.13 Returns and customer rating *owner: trade* — contracts `trade-sales-return-authorisation`, `trade-counterparty-evaluation`

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-612** | **Sales return authorisation (SRA)** against an SO and its shipped demand-order lines: qty ≤ shipped − already authorised, reason code, expected condition, intent `REPLACE` / `CREDIT` / `REWORK` (recorded; `CREDIT` is an accounting hand-over point only), approval `SRA`; approval creates the core RMA through a port (`OD-33`). SRA status follows the RMA; `REPLACE` drafts a replacement dispatch release on receipt | trade | v1 | P9 | R28 D4 |
| **FR-613** | **Purchase twin**: the supplier return stays core (`p8-07`, `wh_supplier_returns`); trade shows it on the PO; a supplier return with intent `REPLACE` reinstates open quantity on the PO line through the port when dispatched (`OD-33`) | trade | v1 | P9 | `RN-031` |
| **FR-614** | **Customer rating** on the FR-594 engine: `DELIVERY_OTIF` (shipped/delivered vs committed date and qty), `RETURN_RATE`, `SCHEDULE_VOLATILITY` (firm-zone changes), `ENQUIRY_CONVERSION`. Payment behaviour is not measured (§10 R4) | trade | v1 | P9 | — |

### 4.14 Print, grids, permissions, non-functional *owner: trade*

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-615** | **Print documents** through core's template renderer (`wh_print_templates`), template kinds seeded by trade: `PURCHASE_REQUISITION`, `RFQ`, `COMPARATIVE_STATEMENT`, `PURCHASE_ORDER` (+ amendment banner), `SCHEDULE_RELEASE`, `CUSTOMER_QUOTATION`, `REGRET_LETTER`, `SALES_ORDER_ACK`, `SALES_RETURN_AUTHORISATION`. Every render is a print job; a reprint is flagged | trade | v1 | P9 | `FR-224` |
| **FR-616** | Every list screen follows the CLAUDE.md standards: `DynamicDataTable`, `grid_column_definitions` + `filter_definitions` + `grid_preferences` with both default arrays, a `filterUtils.ts` scope per grid, five-tile statistics strip, export as a superset of the grid incl. `createdByName` / `updatedByName` | trade | v1 | P9 | — |
| **FR-617** | Permissions `wht_<table>:<verb>` (`view`, `create`, `edit`, `export`, plus `submit`, `approve`, `cancel`, `issue`, `award`, `release`, `amend`, `short_close`, `acknowledge`, `block`, `publish`); `permission_dependencies` seeded; the auditor bundle gets `:view` only; record scope follows core's company / site grants | trade | v1 | P9 | — |
| **FR-618** | **Concurrency and idempotency**: optimistic `version` (stale write `409`); every port call is idempotent on (source document type, id, version or release no), so a double-clicked Approve creates one core PO; port call and trade transition commit together | trade | v1 | P9 | — |
| **FR-619** | **Reports**: open PO register, PR ageing, schedule adherence (PO vs receipt), rate contract expiry, open SO register, dispatch backlog, quotation hit rate — backend queries, grid + export | trade | v1 | P9 | — |

## 5. Mirror table — every purchase capability and its sales twin

**Rule.** Each pair ships **in the same task**, on **separate tables of identical shape** (`TRD-02`),
so a gap on one side is visible in review. Where no twin makes sense the row says why.

| # | Purchase | Sales twin | Same engine? | Task | Note / refusal |
|---|---|---|---|---|---|
| M1 | Supplier trade profile (`wht_supplier_profiles`) — purchase block, MSME, lead time, terms | Customer trade profile (`wht_customer_profiles`) — sales block, category, terms, part-approval flag | no, mirrored tables | p9-02 | MSME fields have no sales twin: the MSMED Act protects the **supplier**; we are the supplier on the sales side and our own Udyam number is a platform company fact |
| M2 | Approved vendor list (`wht_approved_vendor_items`) | Customer item reference + part approval (`wht_customer_item_refs`) | no | p9-02 | — |
| M3 | Purchase requisition (internal need) | Sales enquiry (external need) | no | p9-04 / p9-08 | The PR **and** the RFQ together mirror the enquiry: we *send* an RFQ, a customer *sends* us one. There is no outgoing sales "RFQ" |
| M4 | PR from stores shortage / replenishment / MRP | Enquiry from customer; blanket schedule feeds MRP | — | p9-04 / p9-09 | MRP direction is opposite: purchase consumes MRP output (`OD-31`), sales feeds MRP input (`OD-32`) |
| M5 | PR consolidation (many PR lines → one RFQ/PO) | **Refused twin**: one quotation answers one enquiry | — | p9-04 | Customers do not consolidate our quotations; a quotation may be raised with no enquiry |
| M6 | PR partial conversion | Enquiry partially quoted / partially won (per line) | — | p9-04 / p9-08 | — |
| M7 | RFQ issue to N suppliers | — (received as M3) | — | p9-05 | see M3 |
| M8 | Vendor quotation, versions, validity | Customer quotation, versions, validity | shared version pattern | p9-05 / p9-08 | — |
| M9 | Sealed quotation mode | **Refused twin** | — | p9-05 | Our own quotation cannot be sealed from us |
| M10 | Comparative statement, L1 rank | Quotation version comparison + win/loss analysis | backend diff | p9-05 / p9-08 | Competitor bids are invisible to us; only their reported price on a loss is recorded (§10 R10) |
| M11 | Award with reason (non-L1) | Won / lost with reason, competitor | — | p9-05 / p9-08 | — |
| M12 | Award target → PO / agreement / rate contract | Win → SO / agreement / sales rate contract | — | p9-05 / p9-08 | — |
| M13 | Purchase rate contract (slabs, ceiling, revision) | Sales rate contract (same) | mirrored tables | p9-06 | — |
| M14 | — (supplier sets prices) | Price list (general / category) with floor | — | p9-06 | **Refused purchase twin**: a generic purchase price list duplicates the supplier's quotation and contract; we hold the supplier's price only as M8/M13 |
| M15 | Purchase price resolution | Sales price resolution | two services, same order of precedence | p9-06 | — |
| M16 | PO FIXED / OPEN / BLANKET | SO FIXED / OPEN / BLANKET | mirrored tables | p9-07 / p9-09 | — |
| M17 | Supplier delivery schedule (FIRM/TENTATIVE) | Customer delivery schedule (FIRM/TENTATIVE) | mirrored | p9-07 / p9-09 | — |
| M18 | Release → firms `FORECAST`/adds `FIRM` schedule lines on the one core PO (`p8-01` `releaseSchedule`) | Dispatch release → firms schedule lines on the one core demand order (`p8-02` `releaseSchedule`) | same port shape | p9-07 / p9-09 | Symmetric: one core execution document per trade order on both sides |
| M19 | Release proposal job (horizon) | Dispatch planning workbench (horizon, ATP) | — | p9-07 / p9-09 | ATP shown on sales only; supplier capacity is not known to us |
| M20 | Approval matrix | Same engine | **shared** | p9-03 | — |
| M21 | PO amendment + versions + snapshot | SO amendment + versions + snapshot | shared engine, mirrored tables | p9-11 | — |
| M22 | Supplier acknowledgement captured | Order acknowledgement issued | — | p9-10 | Direction is opposite: we **record** a supplier's, we **issue** ours |
| M23 | Expediting + follow-up log | Delivery commitment tracking + follow-up log | mirrored tables | p9-10 | — |
| M24 | Short-close / cancel via `p8-01` | Short-close / cancel via `p8-02` | — | p9-10 | — |
| M25 | Gate entry inward, GRN + bill (core) | Outward gate pass, shipment, challan (core / india) | — | core | read-only roll-up in trade |
| M26 | Supplier return from QC reject (core `p8-07`), `REPLACE` reinstates PO qty | Sales return authorisation → core RMA, `REPLACE` drafts replacement release | — | p9-13 | **Purchase side has no trade return document**: core's supplier return already carries approval (`wh_supplier_returns` DRAFT→APPROVED) |
| M27 | Vendor evaluation (OTIF, quality, price, response, ack) | Customer rating (OTIF, returns, schedule volatility, conversion) | **shared** engine | p9-12 | — |
| M28 | MSME payment-terms warning | — | — | p9-02 | see M1 |
| M29 | Debit note on short / reject | Credit note on return | — | — | **Both refused** (§10 R3), accounting deferred |
| M30 | Invoice / bill verification | Sales invoice | — | — | **Both refused** (§10 R2) |
| M31 | — | Credit limit / credit check | — | — | **Refused** (§10 R1) |
| M32 | Print: PR, RFQ, CS, PO, schedule release | Print: regret letter, quotation, SO acknowledgement, SRA | shared renderer | p9-14 | — |
| M33 | Reports: open PO, PR ageing, schedule adherence, RC expiry | Reports: open SO, dispatch backlog, hit rate | — | p9-14 | — |

## 6. Screens (WS)

Reference column: **D** = Department (simple CRUD), **C** = Customer (relations + cascading filters),
**SV** = Service Vehicle (stateful workflow + bulk import + transition modals). All routes are web only
(no mobile, user rule 2026-09-11). Menu: trade's own L1 `warehouse_trade` (*Purchase & Sales*), L2
sections ≤ 8 leaves each (`TRD-07`).

| WS | Screen | Route | Ref | L2 section | Task |
|---|---|---|---|---|---|
| WS-280 | Supplier Trade Profiles | `/warehouse/trade/masters/supplier-profiles` | C | Trade Masters | p9-02 |
| WS-281 | Customer Trade Profiles | `/warehouse/trade/masters/customer-profiles` | C | Trade Masters | p9-02 |
| WS-282 | Approved Vendor List | `/warehouse/trade/masters/approved-vendors` | C | Trade Masters | p9-02 |
| WS-283 | Customer Item References | `/warehouse/trade/masters/customer-items` | C | Trade Masters | p9-02 |
| WS-284 | Approval Rules | `/warehouse/trade/masters/approval-rules` | C | Trade Masters | p9-03 |
| WS-285 | My Approvals | `/warehouse/trade/approvals` | SV | Trade Masters | p9-03 |
| WS-286 | Purchase Requisitions | `/warehouse/trade/purchase/requisitions` | SV | Purchasing — Sourcing | p9-04 |
| WS-287 | Requisition Workbench | `/warehouse/trade/purchase/requisition-workbench` | SV | Purchasing — Sourcing | p9-04 |
| WS-288 | RFQs | `/warehouse/trade/purchase/rfqs` | SV | Purchasing — Sourcing | p9-05 |
| WS-289 | Vendor Quotations | `/warehouse/trade/purchase/vendor-quotations` | SV | Purchasing — Sourcing | p9-05 |
| WS-290 | Comparative Statements | `/warehouse/trade/purchase/comparative-statements` (+ `/[id]`) | SV | Purchasing — Sourcing | p9-05 |
| WS-291 | Purchase Rate Contracts | `/warehouse/trade/purchase/rate-contracts` | SV | Purchasing — Orders | p9-06 |
| WS-292 | Purchase Orders | `/warehouse/trade/purchase/orders` | SV | Purchasing — Orders | p9-07 |
| WS-293 | Purchase Order Detail | `/warehouse/trade/purchase/orders/[id]` | SV | (detail) | p9-07 |
| WS-294 | Schedule Releases | `/warehouse/trade/purchase/releases` | SV | Purchasing — Orders | p9-07 |
| WS-295 | Purchase Expediting | `/warehouse/trade/purchase/expediting` | SV | Purchasing — Orders | p9-10 |
| WS-296 | PO Amendments | `/warehouse/trade/purchase/amendments` | SV | Purchasing — Orders | p9-11 |
| WS-297 | Vendor Evaluations | `/warehouse/trade/purchase/vendor-evaluations` | SV | Purchasing — Orders | p9-12 |
| WS-298 | Sales Enquiries | `/warehouse/trade/sales/enquiries` | SV | Sales — Pre-sales | p9-08 |
| WS-299 | Customer Quotations | `/warehouse/trade/sales/quotations` | SV | Sales — Pre-sales | p9-08 |
| WS-300 | Quotation Win/Loss | `/warehouse/trade/sales/win-loss` | D | Sales — Pre-sales | p9-08 |
| WS-301 | Price Lists | `/warehouse/trade/sales/price-lists` | SV | Sales — Pre-sales | p9-06 |
| WS-302 | Sales Rate Contracts | `/warehouse/trade/sales/rate-contracts` | SV | Sales — Orders | p9-06 |
| WS-303 | Sales Orders | `/warehouse/trade/sales/orders` | SV | Sales — Orders | p9-09 |
| WS-304 | Sales Order Detail | `/warehouse/trade/sales/orders/[id]` | SV | (detail) | p9-09 |
| WS-305 | Dispatch Planning | `/warehouse/trade/sales/dispatch-planning` | SV | Sales — Orders | p9-09 |
| WS-306 | Delivery Commitments | `/warehouse/trade/sales/commitments` | SV | Sales — Orders | p9-10 |
| WS-307 | SO Amendments | `/warehouse/trade/sales/amendments` | SV | Sales — Orders | p9-11 |
| WS-308 | Sales Return Authorisations | `/warehouse/trade/sales/return-authorisations` | SV | Sales — Orders | p9-13 |
| WS-309 | Customer Ratings | `/warehouse/trade/sales/customer-ratings` | SV | Sales — Pre-sales | p9-12 |
| WS-310 | Evaluation Schemes | `/warehouse/trade/masters/evaluation-schemes` | C | Trade Masters | p9-12 |
| WS-311 | T&C Templates | `/warehouse/trade/masters/terms-templates` | D | Trade Masters | p9-02 |
| WS-312 | Trade Reports | `/warehouse/trade/reports/<report>` (7 reports) | D | Trade Reports | p9-14 |

Leaf counts: Trade Masters 8 · Purchasing — Sourcing 5 · Purchasing — Orders 6 · Sales — Pre-sales 5 ·
Sales — Orders 6 · Trade Reports 7. `WS-313`…`WS-319` are unused.

**Detail-page tabs.** WS-293: Lines · Schedule · Releases · Receipts (core gate entries, GRNs with bill,
QC, MRN — read-only) · Returns & claims (core) · Acknowledgement · Follow-ups · Amendments · Versions ·
Approvals · Audit. WS-304 mirrors it: Lines · Schedule · Dispatch releases · Shipments (core demand orders,
shipments, outward gate passes — read-only) · Returns (SRA + RMA) · Acknowledgement · Commitments ·
Amendments · Versions · Approvals · Audit. Per the view-popup rule, no tab carries more than two sections.

## 7. Scenarios (WH-SC)

Actors: `req1` (department requester, Maintenance), `stores1`, `buyer1`, `pm1` / `pm2` (purchase
approvers), `sales1`, `sm1` (sales approver), `disp1` (dispatch planner), `adm1` (trade administrator),
`aud1` (auditor). Company `ACME`, sites `PLANT-1` (stores + FG store `FG-1`), currency INR. Kind:
happy / edge / error / guard. Unused ids `WH-SC-566`…`599` stay unused.

### 7.1 Module and masters

| ID | Given | When | Then | FR | Kind |
|---|---|---|---|---|---|
| **WH-SC-480** | A Mode-A install (platform + base + core), `enable.warehouse.trade=false` | Start, open Warehouse menu, receive a core PO end to end | Starts and migrates; no `wht_` table exists; no *Purchase & Sales* menu; core PO, gate entry, GRN work unchanged; `ArchitectureInvariantsTest` finds no `wht_` reference in base or core | FR-540 | happy |
| **WH-SC-481** | Same install with trade enabled | Start | `docker logs platform-backend` shows trade's module configuration; V550000 asserts base + core contract (p8-01 `po_type`, p8-02 SO ref columns) and raises naming the missing object when absent | FR-540 | guard |
| **WH-SC-482** | Counterparty `SUP-ALPHA` with only the `CUSTOMER` role | `adm1` creates a supplier profile for it | `422 TRADE_COUNTERPARTY_ROLE_MISSING` on `counterpartyId`; no row | FR-541 | error |
| **WH-SC-483** | `SUP-ALPHA` supplier profile, MSME `SMALL`, Udyam `UDYAM-MH-26-0012345`, payment terms 60 days | `adm1` saves | Saved with a visible warning *MSME supplier: agreed terms exceed 45 days (MSMED Act §15)*; a PO for it requires `msmeAcknowledged = true`, which is stored with user and time | FR-542 | edge |
| **WH-SC-484** | `buyer1` blocks `SUP-ALPHA` with reason `QUALITY_ESCALATION` | `buyer1` tries to approve the unblock request himself | Block is `PENDING` until `pm1` approves; self-approval `403 TRADE_APPROVAL_SELF`; after approval RFQ invite of `SUP-ALPHA` is refused `422 TRADE_SUPPLIER_BLOCKED` | FR-542 FR-549 | guard |
| **WH-SC-485** | Item `BRG-6205` has AVL rows: `SUP-ALPHA` APPROVED, `SUP-BETA` SUSPENDED; enforcement `REFUSE` | `buyer1` invites `SUP-BETA` and `SUP-GAMMA` (no row) | `SUP-BETA` refused (SUSPENDED, always); `SUP-GAMMA` refused (not on AVL under REFUSE); with `WARN` `SUP-GAMMA` is accepted with a stored warning, `SUP-BETA` still refused | FR-544 | guard |
| **WH-SC-486** | Customer `CUST-OEM1` with `requires_part_approval`; item `HSG-100` reference status `PENDING` | `sales1` adds `HSG-100` to a quotation | `422 TRADE_CUSTOMER_PART_NOT_APPROVED`; after the reference becomes `APPROVED` (rev C), the line saves showing customer part `OEM-77812-C` | FR-545 | guard |
| **WH-SC-487** | Code list `trade_award_reason` seeded by trade | An install adds `TOOLING_OWNED_BY_SUPPLIER`; a later trade migration re-seeds | The install value survives; re-seed is idempotent; a seed row whose `owning_module` is not `warehouse-trade` aborts the migration (owning-module guard) | FR-546 | guard |
| **WH-SC-488** | PR series `PR` for `ACME`, FY 2026-27, current value 41 | `req1` saves a draft, then submits | Draft shows `DRAFT`; submit issues `PR/2627/00042`; a second draft deleted before submit consumes no number | FR-547 | happy |

### 7.2 Approval matrix

| ID | Given | When | Then | FR | Kind |
|---|---|---|---|---|---|
| **WH-SC-489** | Rules for `PO` INR: ≤ 1,00,000 → L1 `PURCHASE_MANAGER` any-one; > 1,00,000 → L1 `PURCHASE_MANAGER`, L2 `PLANT_HEAD` | `buyer1` submits a PO of ₹2,40,000 | Request with two steps; `pm1` approves L1; `pm1` cannot act on L2 (`403 TRADE_APPROVAL_SELF`, already acted); `ph1` approves L2; PO `APPROVED` | FR-548 FR-549 | happy |
| **WH-SC-490** | No rule covers `PO` in `USD` | `buyer1` submits a USD PO | `422 TRADE_NO_APPROVAL_RULE` naming `PO`, `USD 12,000.00`; PO stays `DRAFT` | FR-550 FR-566 | error |
| **WH-SC-491** | Seeded zero-level rule for `PO_RELEASE` within an approved agreement | `buyer1` releases a schedule line | Release approved at submit by `SYSTEM`, rule id stored on the request; port called | FR-550 FR-580 | happy |
| **WH-SC-492** | `pm1` returns a PR with comment | `req1` edits and resubmits | First request `RETURNED` kept; PR back to `DRAFT`; resubmit opens request #2; audit has both | FR-551 | happy |
| **WH-SC-493** | `pm1` delegates to `pm2` 2026-11-01…05; `pm2` is the maker of PO-X | PO-X reaches `pm1`'s step on 11-02 | `pm2` cannot act (maker); `pm1` still can; a delegation from `pm1` to `buyer1` for buyer1's own documents is refused at save | FR-552 FR-549 | guard |
| **WH-SC-494** | A step pending 25 h; `pending_alert_hours=24` | Alert job runs twice | One alert per episode; step still pending; nothing auto-approved | FR-554 | edge |
| **WH-SC-495** | Two rules equally specific for `PR` INR 0–50,000 | `adm1` saves the second | Refused `422 TRADE_APPROVAL_RULE_AMBIGUOUS` naming the first rule | FR-548 | guard |

### 7.3 Purchase requisition

| ID | Given | When | Then | FR | Kind |
|---|---|---|---|---|---|
| **WH-SC-496** | `req1` (Maintenance) needs 40 `BRG-6205` by 2026-11-20, cost object department `MAINT` | Creates and submits a manual PR | Number issued; estimated rate ₹310 defaulted from active RC; approval on ₹12,400; `pm1` approves; PR `APPROVED`, line `OPEN` | FR-556 FR-558 | happy |
| **WH-SC-497** | Core material requisition MR-88 short 25 `GSK-12` (`p8-09`) | `stores1` clicks *Raise PR* | PR line linked to MR-88 line, qty 25, source `STORES_SHORTAGE`; a second *Raise PR* on the same line is refused `409 TRADE_SOURCE_LINE_ALREADY_REQUISITIONED` | FR-557 | guard |
| **WH-SC-498** | Same, `stores1` raises qty to 40 | Saves without justification | `422` on `justification`; with it, saved | FR-557 | error |
| **WH-SC-499** | Core replenishment suggestion source `MRP` (written by MFG, `OD-31`) for 500 `STL-ROD-20` | `buyer1` converts it | PR source `MRP` linked to the suggestion; suggestion marked consumed by core | FR-557 | happy |
| **WH-SC-500** | Three approved PRs each with `BRG-6205` (40, 25, 60) | `buyer1` selects all three on the workbench → *Create RFQ* | One RFQ line qty 125; three allocation rows 40/25/60; PR lines `IN_RFQ`-allocated | FR-559 | happy |
| **WH-SC-501** | PR line 100 `GSK-12` | `buyer1` orders 60 on PO-A, later 30 on PO-B, then tries 20 on PO-C | 60 and 30 succeed (line `PARTIALLY_ORDERED`, open 10); 20 refused `422 TRADE_ALLOCATION_EXCEEDS_OPEN` (open 10) | FR-560 | guard |
| **WH-SC-502** | Two buyers allocate the last 10 of a PR line concurrently | Both submit | One succeeds; the other is refused (row lock), not over-allocated | FR-560 FR-618 | edge |
| **WH-SC-503** | PR line 100 with 60 allocated | `req1` cancels the PR | Refused; *close short remainder 40* with reason allowed; line `ORDERED` (60) closed short 40; requester notified | FR-561 | guard |
| **WH-SC-504** | PO-A line (allocated 60 from the PR) is cancelled before release | Cancel | The 60 return to the PR line's open quantity | FR-561 | edge |

### 7.4 RFQ, quotation, comparative statement, award

| ID | Given | When | Then | FR | Kind |
|---|---|---|---|---|---|
| **WH-SC-505** | RFQ for 125 `BRG-6205` with two invitees; `min_suppliers=3` | `buyer1` issues | Refused `422` on `limitedSourceReasonCode`; with `SOLE_OEM_APPROVED` + note it issues; two RFQ prints, each naming only its supplier | FR-562 FR-563 | guard |
| **WH-SC-506** | RFQ issued to α, β, γ, due 2026-11-10 | γ declines (reason `CAPACITY`); β silent past due; buyer closes bids | γ `DECLINED`, β `NO_RESPONSE`, α `RESPONDED` | FR-563 | happy |
| **WH-SC-507** | α quotes ₹305, valid to 11-30; then revises to ₹298 | Capture revision | Version 2 current; version 1 `REVISED` kept; CS uses ₹298 | FR-564 | happy |
| **WH-SC-508** | α offers alternative item `BRG-6205-ZZ` | Captured | Line flagged alternative; CS shows it in a separate row, never ranked as the RFQ item | FR-564 FR-566 | edge |
| **WH-SC-509** | Sealed mode on, due 11-10, today 11-08 | `buyer2` opens the quotation list | Prices masked for all but the capturer; *Prepare CS* refused until due or bids closed | FR-565 | guard |
| **WH-SC-510** | α ₹298 + freight ₹1,250, β ₹290 + freight ₹3,000 for 125 units | Prepare CS | Landed per unit α 308.00, β 314.00; α L1, β L2 — computed in the backend, tax excluded | FR-566 | happy |
| **WH-SC-511** | CS: buyer recommends β (L2) | Submit without reason | `422` on `awardReasonCode`; with `BETTER_LEAD_TIME` + note it submits with condition `non_l1_award`, routed to the rule requiring `PLANT_HEAD` | FR-567 FR-548 | guard |
| **WH-SC-512** | Split award α 80, β 60 on a 125 line | Submit | `422 TRADE_AWARD_EXCEEDS_RFQ_QTY` (140 > 125); α 80 + β 45 accepted | FR-567 | guard |
| **WH-SC-513** | Award approved; target α = FIXED PO, β = rate contract | Approve | Draft PO for α (80 @ 298), draft RC for β; 80 of the PR allocations move to α's PO line; β's 45 return to the PR lines' open quantity, because a rate contract holds no quantity; RFQ `AWARDED` | FR-568 | happy |
| **WH-SC-514** | α's quotation valid to 11-30; award approval on 12-02 | Approve | Refused `422 TRADE_QUOTATION_EXPIRED`; after capturing α's extension as version 3, award proceeds | FR-569 | guard |

### 7.5 Rate contracts and pricing

| ID | Given | When | Then | FR | Kind |
|---|---|---|---|---|---|
| **WH-SC-515** | RC β for `BRG-6205`: 1–499 @ ₹292, ≥ 500 @ ₹285, 2026-11-01…2027-03-31, ceiling 3,000 | PO line 600 dated 11-15 | Price ₹285, `price_source=RATE_CONTRACT`; consumed 600 / 3,000 | FR-570 FR-573 | happy |
| **WH-SC-516** | Another RC for β, `BRG-6205`, 2027-03-01…2027-09-30 | Approve | Refused by the `EXCLUDE` (overlap in March); a contract starting 04-01 approves | FR-571 | guard |
| **WH-SC-517** | Price revision ₹285 → ₹280 effective 2027-01-01 | Approve amendment | New dated price row; PO-A approved in Dec keeps ₹285; a BLANKET with `price_basis=AT_RELEASE` releases on 01-05 at ₹280 | FR-572 | happy |
| **WH-SC-518** | `buyer1` types ₹300 over the resolved ₹285 | Submit | `price_source=MANUAL`; condition `manual_rate` routes to the stricter rule | FR-573 | guard |
| **WH-SC-519** | RC ending 2026-12-31, alert days 30 | Job on 12-01 | One expiry alert to the RC owner; on 2027-01-01 a new line cannot resolve to it | FR-574 | edge |
| **WH-SC-520** | Price list `PL-DOM-2026` category `OEM`: `HSG-100` ₹1,150, floor ₹1,050; customer RC for `CUST-OEM1` ₹1,120 | Quote `CUST-OEM1` | ₹1,120 (customer RC wins); for a category-OEM customer without an RC, ₹1,150 | FR-602 FR-604 | happy |
| **WH-SC-521** | `sales1` quotes ₹1,000 | Submit | Condition `below_floor_price`; routed to `SALES_MANAGER` | FR-604 FR-599 | guard |
| **WH-SC-522** | RC line UoM `BOX` (= 10 `EA`), PO in `EA` | Resolve | Converted through `whb_uom_conversions`, factor frozen on the line; no conversion → refused `422 TRADE_UOM_NOT_CONVERTIBLE` | FR-573 | edge |
| **WH-SC-523** | RC currency USD, PO currency INR | Resolve | RC skipped (no FX, §10 R5); line falls to manual | FR-573 | edge |

### 7.6 Purchase orders, releases and hand-off

| ID | Given | When | Then | FR | Kind |
|---|---|---|---|---|---|
| **WH-SC-524** | FIXED PO α: 80 `BRG-6205` @ ₹298, schedule 40 on 11-20, 40 on 12-05 | `pm1` approves | One core PO type `FIXED` (`initialStatus = APPROVED`, `approval_source = SOURCE_MODULE`) with two `FIRM` schedule lines created in the same transaction through `p8-01`; trade PO `APPROVED`; the trade number is the core PO's `source_document_ref` and the number printed to the supplier (`OD-30`) | FR-575 FR-577 | happy |
| **WH-SC-525** | The port refuses (item blocked for purchase in core) | Approve | Approval rolled back; PO stays `SUBMITTED`; the core reason shows on the trade screen | FR-577 | error |
| **WH-SC-526** | `pm1` double-clicks Approve | Two requests | One core PO (idempotent on doc id + version); second request returns the same result | FR-618 | edge |
| **WH-SC-527** | OPEN PO γ for `CUT-OIL-20L` @ ₹4,200, validity 2026-11-01…2027-10-31, ceiling 600 | Three call-offs of 50, 100, 200; then one of 300 | First three accepted (350); fourth refused `422 TRADE_CEILING_EXCEEDED` (open 250) | FR-578 | guard |
| **WH-SC-528** | Same OPEN PO, release dated 2027-11-03 | Submit | Refused `422 TRADE_OUTSIDE_VALIDITY` | FR-578 | guard |
| **WH-SC-529** | BLANKET δ `CASTING-A` 1,200 total, schedule 100 × 12 monthly | Submit with schedule totalling 1,150 | `422 TRADE_SCHEDULE_TOTAL_MISMATCH` (1,150 ≠ 1,200) | FR-579 | guard |
| **WH-SC-530** | BLANKET approved; horizon 7 days; schedule line due 12-01 | Job on 11-24 | A release **proposal** appears on WS-294; nothing sent to core until `buyer1` releases | FR-579 | happy |
| **WH-SC-531** | `buyer1` releases 60 of the 100 line | Release | 60 firmed on the agreement's single core `BLANKET_RELEASE` PO with `release_ref` `…-R03`; 40 stay `FORECAST` and cannot be received; schedule line `PARTIALLY_RELEASED`; print *Schedule Release R-03* | FR-579 FR-580 | happy |
| **WH-SC-532** | Released 60; truck arrives with bill no `INV-7781` dated 11-29, billed 60 | Gate entry and GRN in core (`p8-03`, `p8-04`) | Trade PO detail *Receipts* tab shows gate entry, GRN, bill no/date/billed qty read from core; fulfilment `PARTIAL` derived; no trade row written | FR-581 | happy |
| **WH-SC-533** | FIXED line 80, tolerance under 5 %; received 77 | Read PO | Line shows *short-close suggested*; not closed automatically | FR-582 | edge |
| **WH-SC-534** | FIXED PO approved, a core gate entry open against it | `buyer1` cancels | Refused `409 TRADE_EXECUTION_STARTED` naming the gate entry; short-close offered | FR-583 | guard |
| **WH-SC-535** | Trade-created core PO | `stores1` opens it on core WS-072 and clicks Edit / Cancel | Banner *Managed by warehouse-trade*; actions hidden; the API refuses `409 PO_OWNED_BY_SOURCE_MODULE` through trade's registered guard; receipts work | FR-583 | guard |
| **WH-SC-536** | `SUP-ALPHA` purchase-blocked after PO approval | Release / increase qty | Refused `422 TRADE_SUPPLIER_BLOCKED`; the open released 40 still receives | FR-585 | guard |

### 7.7 Acknowledgement, expediting, short-close

| ID | Given | When | Then | FR | Kind |
|---|---|---|---|---|---|
| **WH-SC-537** | PO issued; supplier confirms line 2 for 12-12 instead of 12-05 | `buyer1` records ack `ACCEPTED_WITH_CHANGES` | Diff shown; *Accept changes* drafts an amendment with the date change; agreed date stays 12-05 until it is approved | FR-586 FR-590 | happy |
| **WH-SC-538** | Schedule line due 12-05 open; `days_before=3`; site timezone Asia/Kolkata | Job on 12-02 IST | Line appears on WS-295 *due soon*; on 12-06 *overdue*; follow-up with promised 12-09 stored apart from agreed | FR-587 | happy |
| **WH-SC-539** | FIXED line 80, received 77 | `buyer1` short-closes the line with `SUPPLIER_CANNOT_SUPPLY` | Port closes 3 in core; line `SHORT_CLOSED`; header `CLOSED` when no open line | FR-588 FR-589 | happy |
| **WH-SC-540** | OPEN PO past validity, all releases received | Nightly job | PO `CLOSED` | FR-589 | edge |

### 7.8 Amendments

| ID | Given | When | Then | FR | Kind |
|---|---|---|---|---|---|
| **WH-SC-541** | FIXED line 80: received 40, gate entry open for 30 | Amend qty to 60 | Refused `422 TRADE_AMEND_BELOW_COMMITTED` (40 received + 30 in-flight = 70) | FR-591 | guard |
| **WH-SC-542** | Same, amend qty to 100 and rate ₹298 → ₹295 | Approve | Rate applies to the 60 un-received; version 2 snapshot; port updates core PO; print *Amendment No. 1*; ack pending | FR-590 FR-591 FR-592 | happy |
| **WH-SC-543** | An amendment open on PO-A | `buyer1` releases a line of PO-A / opens a second amendment | Both refused (`409 TRADE_AMENDMENT_OPEN`) | FR-590 | guard |
| **WH-SC-544** | ₹90,000 PO amended to ₹1,30,000 | Submit | Evaluated on new total (band > 1,00,000) → two levels | FR-553 | guard |
| **WH-SC-545** | Versions 1, 2, 3 | Compare 1 ↔ 3, reprint 1 | Field-level diff from the backend; reprint of v1 marked *Reprint, superseded* | FR-593 FR-615 | happy |
| **WH-SC-546** | `buyer1` tries to change supplier on an amendment | Save | Field not editable; API refuses `422 TRADE_FIELD_NOT_AMENDABLE` | FR-591 | guard |

### 7.9 Evaluation

| ID | Given | When | Then | FR | Kind |
|---|---|---|---|---|---|
| **WH-SC-547** | Scheme: OTIF 40, quality 40, price 10, response 10; October: 18 of 20 lines on time in full, 9,700 of 10,000 accepted, price at contract, 4 of 5 RFQs answered | Run October | Score 0.4×90 + 0.4×97 + 0.1×100 + 0.1×80 = 92.8 → grade A; published run immutable | FR-594 FR-595 | happy |
| **WH-SC-548** | Weights summing to 95 | Save scheme | `422 TRADE_WEIGHTS_NOT_100` | FR-594 | guard |
| **WH-SC-549** | `SUP-BETA` grade D, review grade D | Publish | AVL review task for `adm1`; AVL unchanged | FR-596 | guard |

### 7.10 Sales

| ID | Given | When | Then | FR | Kind |
|---|---|---|---|---|---|
| **WH-SC-550** | Enquiry from `CUST-OEM1` ref `RFQ/OEM/991` for 2,000 `HSG-100` | `sales1` records and quotes ₹1,120, validity 30 days | Quotation v1 `SENT`, enquiry `QUOTED` | FR-598 FR-599 FR-600 | happy |
| **WH-SC-551** | Customer negotiates; `sales1` revises to ₹1,090 | Revise | v2 `SENT`, v1 `REVISED`; *Won* offered on v2 only | FR-600 | guard |
| **WH-SC-552** | Enquiry for an item the plant cannot make | `sales1` regrets with `NO_CAPACITY` | Enquiry `REGRETTED`, regret letter printable | FR-598 | happy |
| **WH-SC-553** | v2 lost to a competitor at ₹1,040 | Record loss `PRICE` | Quotation `LOST`; WS-300 shows lost value ₹21,80,000 under `PRICE` | FR-601 | happy |
| **WH-SC-554** | Quotation won as BLANKET | Mark won | Draft BLANKET SO prefilled; enquiry `WON` | FR-601 | happy |
| **WH-SC-555** | BLANKET SO `CUST-OEM1` 2,000 `HSG-100`, monthly schedule 500 × 4, customer PO `4500012345` | Submit a second SO with the same customer PO | Refused `409 TRADE_DUPLICATE_CUSTOMER_PO` | FR-605 | guard |
| **WH-SC-556** | SO approved | `sales1` sends the acknowledgement | Print *Order Acknowledgement* with committed dates; SO `ACKNOWLEDGED` | FR-606 | happy |
| **WH-SC-557** | Schedule line 500 due 12-10; FG-1 available 320 | `disp1` releases 500 | Allowed; shortfall 180 shown; the schedule line is firmed on the SO's core demand order (`release_ref` `…-D02`); core allocates 320 within the horizon and backorders the rest per its fulfilment policy | FR-607 | edge |
| **WH-SC-558** | Open schedule 200 | Release 250 | `422 TRADE_RELEASE_EXCEEDS_SCHEDULE` | FR-607 | guard |
| **WH-SC-559** | Demand order shipped 500 through core, outward gate pass, challan | Open SO detail | *Shipments* tab read-only from core; fulfilment derived; no trade write | FR-608 | happy |
| **WH-SC-560** | Customer revises January from 500 to 350 inside the firm zone | Import revised schedule CSV (dry-run then apply) | Amendment drafted; firm-zone change flagged and counted for `SCHEDULE_VOLATILITY` | FR-611 FR-614 | edge |
| **WH-SC-561** | Schedule line due in 3 days, unreleased; `at_risk_days=5` | Open WS-306 | Line at risk; follow-up with customer-informed date stored apart from committed | FR-610 | happy |
| **WH-SC-562** | Shipped 500, customer returns 20 for `DIMENSION_NC`, intent `REPLACE` | `sales1` raises SRA, `sm1` approves | Core RMA created through the port (`OD-33`); on RMA receipt a replacement release of 20 is drafted; `CREDIT` would only mark an accounting hand-over point | FR-612 | happy |
| **WH-SC-563** | Shipped 500, authorised 20 | Raise SRA for 490 | `422 TRADE_RETURN_EXCEEDS_SHIPPED` (open 480) | FR-612 | guard |
| **WH-SC-564** | Core supplier return of 30 rejected `BRG-6205` with intent `REPLACE`, dispatched | — | PO line open quantity reinstated by 30 through the port; shows on WS-293 *Returns & claims* | FR-613 | happy |
| **WH-SC-565** | `aud1` opens every trade screen | Tries Export / Approve | Views succeed; no Export button and `403` on the API; no write action | FR-617 | guard |

## 8. Data model summary (authority for the task files; `DATA-MODEL.md` gains it through SPINE)

Money `DECIMAL(19,4)`, unit price `DECIMAL(19,6)`, quantity `DECIMAL(18,4)`, percent `DECIMAL(9,6)` —
the convention core already uses (`V510011:99-101, 208-225`). Every table: `id UUID`, `version BIGINT`,
audit columns, `company_id` NOT NULL. Status columns `VARCHAR(30)` with **no `CHECK`**.

| Migration | Tables | Task |
|---|---|---|
| `V550000` | bootstrap: asserts platform, base and the core contract it consumes (`wh_purchase_orders.po_type`, `.source_module`, `wh_purchase_order_schedule_lines`, `wh_demand_orders.sales_order_ref`, `wh_demand_order_schedule_lines` — `p8-01`/`p8-02`; the port beans are checked at start-up) | p9-01 |
| `V550010` | `wht_supplier_profiles`, `wht_customer_profiles`, `wht_approved_vendor_items`, `wht_customer_item_refs`, `wht_terms_templates`, `wht_terms_template_versions` | p9-02 |
| `V550011` | seed: code lists, `whb_document_types`, `whb_source_systems` (`WAREHOUSE_TRADE`), print template kinds — owning-module guard | p9-02 |
| `V550020` | `wht_approval_rules`, `wht_approval_rule_levels`, `wht_approval_rule_level_users`, `wht_approval_requests`, `wht_approval_steps`, `wht_approval_delegations` | p9-03 |
| `V550030` | `wht_purchase_requisitions`, `wht_purchase_requisition_lines`, `wht_requisition_allocations` | p9-04 |
| `V550040` | `wht_rfqs`, `wht_rfq_lines`, `wht_rfq_suppliers`, `wht_vendor_quotations`, `wht_vendor_quotation_lines`, `wht_vendor_quotation_charges`, `wht_comparative_statements`, `wht_comparative_statement_awards` | p9-05 |
| `V550050` | `wht_purchase_rate_contracts`, `wht_purchase_rate_contract_lines`, `wht_purchase_rate_contract_prices` (dated, `EXCLUDE`), `wht_purchase_rate_contract_slabs`; `wht_price_lists`, `wht_price_list_prices`, `wht_price_list_slabs`; `wht_sales_rate_contracts`, `_lines`, `_prices`, `_slabs` | p9-06 |
| `V550060` | `wht_purchase_orders`, `wht_purchase_order_lines`, `wht_po_schedule_lines`, `wht_po_releases`, `wht_po_release_lines`, `wht_po_charges` | p9-07 |
| `V550070` | `wht_sales_enquiries`, `wht_sales_enquiry_lines`, `wht_customer_quotations`, `wht_customer_quotation_lines`, `wht_customer_quotation_charges` | p9-08 |
| `V550080` | `wht_sales_orders`, `wht_sales_order_lines`, `wht_so_schedule_lines`, `wht_so_dispatch_releases`, `wht_so_dispatch_release_lines`, `wht_so_charges` | p9-09 |
| `V550090` | `wht_po_acknowledgements`, `wht_po_ack_lines`, `wht_po_followups`, `wht_so_acknowledgements`, `wht_so_commitment_followups` | p9-10 |
| `V550100` | `wht_po_amendments`, `wht_po_amendment_changes`, `wht_purchase_order_versions`, `wht_purchase_order_line_versions`, `wht_po_schedule_line_versions`; the `wht_so_*` mirror set | p9-11 |
| `V550110` | `wht_evaluation_schemes`, `wht_evaluation_criteria`, `wht_evaluation_grade_bands`, `wht_evaluation_runs`, `wht_counterparty_evaluations`, `wht_counterparty_evaluation_scores` | p9-12 |
| `V550120` | `wht_sales_return_authorisations`, `wht_sales_return_authorisation_lines` | p9-13 |
| `V551000`–`V551199` | permissions, `permission_dependencies`, menus (`WHERE NOT EXISTS`), grid / filter definitions, `grid_preferences`, admin settings — one pair per task, numbered `V5510n0` / `V5510n1` for task `p9-0n` and `V5511n0` / `V5511n1` for `p9-1n` | each task |

## 9. Decisions (TRADE-local; `D-16` is the program record)

| ID | Decision | Why |
|---|---|---|
| `TRD-01` | **Commercial document in trade, execution document in core.** The trade PO / SO is what is approved, versioned, printed, acknowledged and amended. The core PO / demand order is what is received or dispatched. Trade creates and changes core documents only through the `p8-01` / `p8-02` ports | `RN-053`; `RM-030` (three POs already exist — this makes the roles explicit rather than adding a fourth undefined one) |
| `TRD-02` | **Separate tables per side, identical shape, delivered in the same task**; the approval engine, evaluation engine, renderer and version pattern are shared | Separate permissions, grids and ports per side; the mirror is enforced by review, not by a `side` column every query must remember |
| `TRD-03` | Fulfilment (received / shipped) is **derived from core on read**, never cached in `wht_` | `FR-123` layered truth: one quantity truth |
| `TRD-04` | Versions are **snapshot row sets**, not JSON | CLAUDE.md: no JSONB |
| `TRD-05` | **Trade is the supply-chain owner that `p6-05` / `FR-142` defer to**; it stores scorecards in `wht_`. The core still stores none | `RN-035`; `p6-05` refuses a scorecard **in warehouse core**, and core stays that way |
| `TRD-06` | **No tax, no FX.** Lines carry the item's tax classification code (recorded); prints say *Taxes extra as applicable*; documents of different currencies are never ranked or summed together | `OD-9` answer (warehouse never computes tax); accounting deferred |
| `TRD-07` | Trade has its **own L1 menu** (`warehouse_trade`, *Purchase & Sales*) with six L2 sections ≤ 8 leaves | Keeps `warehouse_operations` under its 10-section cap; one toggle hides one tree |
| `TRD-08` | **Approval never times out into approval**; zero-level rules are explicit rows | `FR-408` maker–checker |
| `TRD-09` | **MRP and stores shortages reach trade by pull from core**, never by a sibling call: MFG writes core replenishment suggestions (`OD-31`), stores writes material requisitions (`p8-09`); trade converts them | FKs point down only; siblings never depend on each other |
| `TRD-10` | Price precedence: purchase — rate contract → valid awarded quotation → manual; sales — customer RC → category price list → general price list → manual. Last price is reference only | One resolution order per side, testable |
| `TRD-11` | Release proposals are **proposed, never auto-released** | A release is a commitment to a supplier |

## 10. Open decisions (OD-30…OD-39)

| # | Question | Recommended default (adopted unless overruled) | Blocks |
|---|---|---|---|
| **OD-30** | One number or two for a purchase order? | **The trade number is the supplier-facing number.** It is printed on the PO and stored as the core PO's `source_document_ref`; the core PO keeps its internal `po_number` (core's series, `p8-01` has no number parameter). Owed by STORES: the gate entry (`p8-03`) and GRN PO pickers match **either** number, and WS-072 shows `source_document_ref` as *Supplier PO no.* | FR-547, FR-577 |
| **OD-31** | How does MRP output reach a PR without a sibling-to-sibling dependency? | MFG writes **core `wh_replenishment_suggestions` rows with source `MRP`** (planned purchase); trade converts them (FR-557). Confirm with MFG (`OD-40`…`44` range) and STORES | FR-556, FR-557 |
| **OD-32** | How does MRP see unreleased customer schedule lines? | **Closed by `p8-02`:** the SO's core demand order carries them as `FORECAST` schedule lines that never reserve; MRP reads core. Trade keeps them equal to the unreleased schedule on every approval, release and amendment. Confirm MRP reads `FORECAST` (MFG) | FR-611 |
| **OD-33** | Port for creating a core RMA from an SRA, and the supplier-return `REPLACE` intent | **Owed by STORES as a new task (not in `p8-01`…`p8-14`)**: `WhRmaPort.createRma / cancelRma` with `source_*` and idempotency, plus an `intent_code` on `wh_supplier_returns` and outbox `WH_SUPPLIER_RETURN_DISPATCHED`. PO reinstatement itself needs no new op: trade calls `amendOrder` to add a `FIRM` schedule line. Until then FR-612/FR-613 are not buildable | FR-612, FR-613 |
| **OD-34** | Approval bands and ranking for foreign-currency documents | Rules are **per currency**; no rule → refusal; comparative statement ranks only same-currency quotations | FR-548, FR-566 |
| **OD-35** | Slab basis: per order line, or cumulative over the contract? | **Per order line** in v1; cumulative slabs need a retroactive price change, which is accounting | FR-570 |
| **OD-36** | Rate amendment after partial receipt | Applies to **un-received quantity only**; received units keep their GRN valuation; no revaluation (accounting deferred) | FR-591 |
| **OD-37** | Sealed bids default | Setting exists, **default off** | FR-565 |
| **OD-38** | Does a trade PO carry `qc_required` or do core inspection plans decide? | **Core inspection plans decide** (`p8-05`/`p8-06`); trade carries nothing | FR-576 |
| **OD-39** | May core screens edit a core PO / demand order that trade created? | **Closed by `p8-01`/`p8-02`:** the `PurchaseOrderChangeGuard` / `DemandOrderChangeGuard` seams exist; trade registers guards refusing manual edit / approve / cancel / close with `409 PO_OWNED_BY_SOURCE_MODULE` (receipts and dispatch are not guarded) | FR-583 |

## 11. What this module deliberately does not do (`RM-043`)

| # | Not building | Who has it | Why not | Re-entry path |
|---|---|---|---|---|
| R1 | **Credit limit / credit check** on SO | accounting | Needs receivables; accounting is deferred (`RN-054`) | An accounting-owned `CreditCheckPort` called at SO submit |
| R2 | **Supplier bill / sales invoice**, three-way match | accounting; core `P5-10` keeps its quantity match | Obligation ⇒ accounting | `whb_accounting_handovers` envelope |
| R3 | **Debit note / credit note** (short, reject, return, price difference) | accounting | User rule: never generate them | SRA `CREDIT` intent and core claims are the recorded hand-over points |
| R4 | **Payment tracking, MSME due dates, §43B(h) reports** | accounting | Needs payments | Profile carries Udyam + terms already |
| R5 | **Tax computation, FX conversion** | accounting / `warehouse-india` facts | `TRD-06` | — |
| R6 | **Supplier portal, e-auction, reverse auction** | e-procurement products | External user surface + security | A portal module over trade's RFQ |
| R7 | **EDI** (ORDERS, DELFOR, DESADV) | integration | v1 CSV import of customer schedules (FR-611) | Base inbound messages |
| R8 | **Service POs, capex / asset POs** | `assets` | Stock items only; the scope fence forbids editing `assets` | — |
| R9 | **Subcontract / job-work PO** | `warehouse-india` + MFG | Job work runs through `warehouse-india` (`RN-053`) | — |
| R10 | **Competitor bid comparison** | — | We never see competitors' bids; only a reported price on loss | — |
| R11 | **CRM pipeline, leads, opportunities** | `leads-base` / `leads` | Different module | Enquiry may later link a lead id |
| R12 | **Sales commissions, incentives** | HR/accounting | — | — |
| R13 | **Budget check against department / cost centre** | accounting | No budget master | — |
| R14 | **Generic purchase price list** | — | Mirror row M14 | — |
| R15 | **Enquiry consolidation into one quotation** | — | Mirror row M5 | — |
| R16 | **Mobile screens** | — | User rule 2026-09-11 | — |
| R17 | **Import purchase (customs, bill of entry), landed cost** | core landed cost (`V510080`) / india | Landed cost is core's; customs is out | — |
| R18 | **Auto-suspension of a supplier by grade** | — | `FR-596` advisory only | — |

## 12. Owed by other areas (TRADE cannot build these rows without them)

| Owed by | Item | Used by |
|---|---|---|
| STORES `p8-01` | `WhPurchaseOrderPort` (`createOrder` with `initialStatus = APPROVED`, `releaseSchedule`, `amendOrder`, `cancelScheduleLine`, `closeLine`, `closeOrder`, `cancelOrder`, `getReceiptPosition`), `source_*`, idempotency per `(source_module, key)`, `PurchaseOrderChangeGuard` — **as written in `p8-01` / `po-schedule-port.contract.md`** | p9-07, p9-10, p9-11 |
| STORES `p8-02` | `WhDemandOrderPort` (`createDemand`, `releaseSchedule`, `amendDemand`, `cancelLine`, `cancelDemand`, `getFulfilmentPosition`), `FORECAST`/`FIRM` schedule, `DemandOrderChangeGuard`, outbox `WH_DEMAND_SHIPPED` / `_CANCELLED` / `_AMENDED`; an ATP query bean for WS-305 | p9-09, p9-10, p9-11 |
| STORES `p8-03` / `p8-04` | Gate entry and GRN PO pickers match `source_document_ref` as well as `po_number` (`OD-30`); bill no / date / billed qty readable | p9-07 (read-only tabs) |
| STORES `p8-06` / `p8-07` | QC accepted / inspected per GRN line by supplier; supplier return with intent | p9-12, p9-13 |
| STORES `p8-09` / `p8-10` | Shortage line query; cost-object vocabulary | p9-04 |
| STORES (new task) | `WhRmaPort`; supplier-return `intent_code` + dispatched event (`OD-33`) | p9-13 |
| MFG | MRP writes core replenishment suggestions with source `MRP` (`OD-31`); reads `FORECAST` + `FIRM` demand schedule from core (`OD-32`) | p9-04, p9-09 |
| SPINE | `DATA-MODEL.md`, `BUILD-SPEC-SCREENS.md`, `SCENARIO-CATALOGUE.md`, `MODULE-INTEGRATION.md` rows for `warehouse-trade`; D-12 release unit for P9 | all |

## 13. Traceability

| FR | Contract | Task |
|---|---|---|
| FR-540 | — | p9-01 |
| FR-541–547, FR-584 | `trade-counterparty-evaluation` (profiles, AVL); T&C templates | p9-02 |
| FR-548–555 | `trade-approval-matrix` | p9-03 |
| FR-556–561 | `trade-purchase-requisition` | p9-04 |
| FR-562–569 | `trade-rfq-award` | p9-05 |
| FR-570–574, FR-602–604 | `trade-rate-contract` | p9-06 |
| FR-575–583, FR-585 | `trade-purchase-order` | p9-07 |
| FR-598–601 | `trade-sales-enquiry-quotation` | p9-08 |
| FR-605–609, FR-611 | `trade-sales-order` | p9-09 |
| FR-586–589, FR-606 (ack), FR-610 | `trade-purchase-order` §ack, `trade-sales-order` §ack | p9-10 |
| FR-590–593 | `trade-order-amendment` | p9-11 |
| FR-594–597, FR-614 | `trade-counterparty-evaluation` | p9-12 |
| FR-612–613 | `trade-sales-return-authorisation` | p9-13 |
| FR-615–619 | every contract §5 | p9-14 (print + reports); FR-616–618 in every task |
