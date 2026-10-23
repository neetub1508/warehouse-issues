# FRD-TRADE — `warehouse-trade`: manufacturing purchase and sales, mirrored

**Date** 2026-10-22 · **Area** TRADE · **Phase** `P9` · **Status** derived v0, R29 dual-engine review
folded (§"R29 dispositions") · **ID ranges** `FR-540`–`FR-619`, `WS-280`–`WS-313` (allocated to 319), `WH-SC-480`–`WH-SC-599`,
`OD-30`–`OD-39` (`DECISIONS.md` D-16 allocation); lost-sale capture `FR-680` onward, ten ids (`D-17` item 4; `FR-680`, `FR-681` used); the subcontract service PO `FR-682`–`FR-689` (`D-18` item 3, R31) uses the rest, so the range is full. Unused numbers stay unused.

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

**What it never does.** It never writes a `wh_` or `whb_` row except seed rows carrying
`owning_module = 'warehouse-trade'` under the owning-module guard (`RL-003`): code lists, document types,
number series, print-template kinds, **reason codes** (`whb_reason_codes`, FR-546, FR-680), the **source
system** `WAREHOUSE_TRADE` (`whb_source_systems`, `p9-01`) and the **task type** `TRADE_AVL_REVIEW`
(`whb_task_types`, `TCE-OPEN-01`) (R31 F-TR-022). It never reads or writes a `whm_` row: a subcontract
order is reached only through core's `CostObjectResolver` (FR-682). It never posts a movement. It never computes tax, never converts
currency, never raises an invoice, debit note or credit note, and never checks credit (§11).

**How it reaches core.** Only through the ports and SPIs of FRD-STORES *"Port & seam registry
(authoritative)"*. Every method, command field, operation key, verb, event and refusal code this file and
the `trade-*` contracts name is that registry's; §12a states trade's side of each one (principal, grants,
idempotency keys, guards, events). Where a trade document and the registry differ, the registry wins.

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

Every row is covered by an FR here, assigned to another area by id, or refused in §11.

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
| C23 | Invoice verification, 3-way match | accounting / core `P5-10` | refused here §11 R2 | Billing / invoice | accounting | §11 R2 |
| C24 | Debit / credit note | accounting | §11 R3 | Debit / credit note | accounting | §11 R3 |
| C25 | Payment, MSME due date | accounting | §11 R4 | Credit limit / credit check | accounting | §11 R1 |

## 4. Requirement catalogue

Rows use the shape of `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` §2. **Module** `trade` = `warehouse-trade`;
`app` = core `warehouse`. **Ver** `v1`: D-16 sequences P7–P10 into the pre-launch build (no clients,
`RN-052`); if SPINE maps P9 to a later release unit the column changes in one place. **Ph** `P9`.

### 4.1 Module and masters *owner: trade*

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-540** | `warehouse-trade` is a **sibling module**: package `ai.warehousetrade`, band `V550000`–`V559999`, prefix `wht_`, switch `enable.warehouse.trade` read by `@ConditionalOnExpression`. It depends on platform + `warehouse-base` + `warehouse`. Every FK points **down** (`wht_` → `wh_`/`whb_`/platform); no `wh_`/`whb_` table, entity, service or route references `wht_`, enforced by `ArchitectureInvariantsTest`. A Mode-A install without it behaves exactly as before, and core PO / demand-order screens keep working for documents core creates itself. At start-up the module refuses to run unless the core port beans it calls unconditionally are present (`WhPurchaseOrderPort`, `WhDemandOrderPort`, `WhAvailableToPromiseQuery`); `WhReplenishmentSuggestionPort` absence only disables *Import shortages* and suggestion conversion (`503`, R31 F-TR-020, as `p9-01`), and `WhRmaPort` absence only the SRA screens (`TSR-GRD-04`) | trade | v1 | P9 | `RN-053` `RM-041` |
| **FR-541** | **One party identity.** Suppliers and customers are `whb_counterparties` with a `SUPPLIER` / `CUSTOMER` role link. Trade adds **profile extension** rows (one per counterparty × company × side); it never creates a second supplier or customer master. A profile for a counterparty without the matching role link is refused with `422 TRADE_COUNTERPARTY_ROLE_MISSING` | trade | v1 | P9 | `G-027` `FR-119` |
| **FR-542** | **Supplier trade profile**: `is_purchase_blocked` + block reason + blocked by/at (block and unblock are approval requests of type `PROFILE_BLOCK`, acted on with `wht_supplier_profiles:approve`), MSME category (code list: `MICRO`/`SMALL`/`MEDIUM`/`NOT_MSME`), Udyam registration number (format `UDYAM-XX-00-0000000`), classification date, default lead time days, min order value, default currency, payment terms (code + days, **recorded only**), delivery terms, freight terms. A `MICRO`/`SMALL` supplier whose payment-terms days exceed 45 shows a warning on the profile and on every PO, and the buyer must tick an acknowledgement that is stored; trade does not track payment (§11 R4) | trade | v1 | P9 | `RM-006` R28 A8 |
| **FR-543** | **Customer trade profile** (mirror of FR-542): `is_sales_blocked` + reason (approval request `PROFILE_BLOCK`, acted on with `wht_customer_profiles:approve`), customer category, default currency, payment terms (recorded only), delivery and freight terms, default ship-to address (`whb_counterparty_addresses`), default dispatch site, `customer_po_required`, `requires_part_approval`. **No credit limit** (§11 R1) | trade | v1 | P9 | R28 D |
| **FR-544** | **Approved vendor list (AVL)** per company × item (or item category) × supplier: status code (`APPROVED`, `PROVISIONAL`, `SUSPENDED`, `DISQUALIFIED`), valid from/to, sole-source flag, approver and reason. **Every AVL entry and status change is an approval request of type `AVL`** (maker ≠ checker, `403 TRADE_APPROVAL_SELF`; reject leaves the row `REJECTED` and without effect); the change takes effect only on approval. Setting `warehouse.trade.avl.enforcement` = `WARN` \| `REFUSE` (default `REFUSE`) applies when the item has any effective AVL row: inviting, awarding or ordering from a supplier not `APPROVED`/`PROVISIONAL` for the date. `SUSPENDED` and `DISQUALIFIED` are refused under either setting | trade | v1 | P9 | R28 A8 |
| **FR-545** | **Customer item reference** (the customer-material info record): customer × item → customer part number, drawing number + revision, customer approval status (`APPROVED`, `PENDING`, `REJECTED`, e.g. PPAP), valid from/to. The status **records the customer's own decision**; setting it to `APPROVED` requires the customer's approval document attached (platform documents) — no internal approval request (mirror refusal, §5 M2). When the customer profile has `requires_part_approval`, an SO or quotation line for an item without a current `APPROVED` reference is refused with `422 TRADE_CUSTOMER_PART_NOT_APPROVED` | trade | v1 | P9 | mirror of FR-544 |
| **FR-546** | Every extensible vocabulary (reasons, terms, statuses-as-codes for AVL, MSME category, charge types, enquiry sources) is a `whb_code_lists` row set with `owning_module = 'warehouse-trade'`, seeded with the owning-module guard; an install may add values. **Except the reasons a core port takes** (R31 F-TR-007): every port command and the core RMA take a `reasonCodeId` ↓ `whb_reason_codes`, so cancel, short-close, release cancel and auto-close reasons are `whb_reason_codes` rows of context **`TRADE_ORDER_CLOSE`** (seeded: `CUSTOMER_REQUEST`, `SUPPLIER_CANNOT_SUPPLY`, `NO_STOCK`, `LEAD_TIME_NOT_MET`, `AUTO_CLOSE`; they replace the code lists `trade_cancel_reason` and `trade_short_close_reason`), and return reasons (replacing `trade_return_reason`) rows of context **`RETURN`** (seeded `QUALITY_NC`, `DIMENSION_NC`, `EXCESS_SUPPLY`, `TRANSIT_DAMAGE`, `CUSTOMER_CHANGE`; base's `RETURN` / `WRONG_ITEM` row is reused, never re-seeded, since the key is `uk(context, code)`), all `owning_module = 'warehouse-trade'`; the picker value is the reason id, passed to the port unchanged. An SRA carries one header reason (the RMA's) and per-line reasons defaulted from it (`TSR` §0) **No `CHECK` on an extensible value; document status columns carry no `CHECK` (`D-10`)** — the service is the only enforcement point | trade | v1 | P9 | `D-10` `RL-003` |
| **FR-547** | **Numbering.** Each numbered trade document type has a `whb_document_types` row and draws non-gapless (`is_gapless = false`; these are not tax documents) numbers from `whb_number_series` per company (optionally per site) with `YEARLY` (financial-year) reset: `PR` at submit, `RFQ` at issue, `VQ` at capture, `CS` at submit, `PRC` / `SRC` / `PL` at submit, `PO` / `PA` / `SO` at submit, `ENQ` at save, `SQ` at submit, `SRA` at submit. **Releases and amendments take no series**: a release is `<order number>-Rnn` (purchase) / `-Dnn` (sales) and an amendment `<order number>-Ann`, from a per-order counter, at release submit / amendment submit. Drafts show `DRAFT` and are never numbered; a hand-off PR (FR-557) is numbered because it is created submitted. The PO's supplier-facing number is resolved by `OD-30` | trade | v1 | P9 | `RL-004` |

### 4.2 Approval matrix *owner: trade* — contract `trade-approval-matrix`

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-548** | **One approval engine** for every trade document type (`PR`, `CS`, `PRC`, `PRC_AMENDMENT`, `PO`, `PO_RELEASE`, `PO_AMENDMENT`, `PO_SHORT_CLOSE`, `PO_CANCEL`, `SQ`, `SRC`, `SRC_AMENDMENT`, `PRICE_LIST`, `PRICE_LIST_AMENDMENT`, `SO`, `SO_RELEASE`, `SO_AMENDMENT`, `SO_SHORT_CLOSE`, `SO_CANCEL`, `SRA`, `AVL`, `PROFILE_BLOCK`). A rule names document type × company × optional site × optional department × optional item category × **currency**, a value band and/or a quantity band, a condition set (`manual_rate`, `non_l1_award`, `below_floor_price`, `discount_over_pct`, `open_unbounded`, `release_price_manual`, `supplier_return_replacement`, `termination`) with a **match mode** — `EXACT` (default: the document's condition set equals the rule's, so an empty-set rule matches only a document with no condition) or `INCLUDES` (the rule's set ⊆ the document's) — and ordered levels; each level names a role or users and `ANY_ONE` / `ALL`. The most specific matching rule wins. Two active rules that could match one document with equal specificity are refused at save (`422 TRADE_APPROVAL_RULE_AMBIGUOUS`), and a tie found at submit is refused the same way | trade | v1 | P9 | R28 A6 |
| **FR-549** | **Maker ≠ checker at every level.** The document's maker, and anyone who has already acted on an earlier level of the same request — **in their own name or as a delegate** — cannot act on a level, and a delegate cannot act for a principal who is the maker or has already acted; refused with `403 TRADE_APPROVAL_SELF` even for a holder of `:approve` or `ADMIN`. For a system-drafted document the maker is the person whose action drafted it (the statement's preparer for award targets, the clicking buyer for acknowledgement changes, the stores user for a hand-off PR) | trade | v1 | P9 | `FR-408` |
| **FR-550** | **No rule ⇒ refusal, never auto-approval.** Submitting a document no rule covers is refused with `422 TRADE_NO_APPROVAL_RULE` naming the document type, value, currency and conditions. A rule may have **zero levels**: the document is approved at submit by `SYSTEM` with the rule id recorded. The non-monetary types `AVL` and `PROFILE_BLOCK` open their request with value 0 in the **company currency**, so a rule for them is written in that currency (`TAM-GRD-01`, R31 F-TR-013). Seeded zero-level rules (`EXACT`, empty condition set unless named): `PO_RELEASE`, `SO_RELEASE`, `PO_SHORT_CLOSE`, `SO_SHORT_CLOSE`, `PO_CANCEL`, `SO_CANCEL`, `SQ`, and `PO_AMENDMENT` with `{supplier_return_replacement}` | trade | v1 | P9 | — |
| **FR-551** | Approve, reject and return-for-changes; reject and return need a comment. On every trade document type reject → `REJECTED` (editable, resubmittable) and return → `DRAFT`; the request itself is terminal either way. A resubmission opens a **new** approval request; the old one is kept. Every action writes `whb_audit_events` | trade | v1 | P9 | — |
| **FR-552** | **Delegation**: an approver records a dated delegate for themselves; the delegate acts "on behalf of" and the record keeps both names. A delegation recorded **for another approver** (by a holder of `wht_approval_rules:edit`) is `PENDING_CONFIRMATION` until a second holder, who is neither the recorder nor the delegate, confirms it. A delegation whose delegate is the recording user (unless they are the principal — then refused as self), or the request's maker, is refused | trade | v1 | P9 | — |
| **FR-553** | An approved document changes **only by amendment** (FR-590), which takes its own approval; the amendment's band is evaluated on the **new total** and on the **absolute delta**, and the request uses the matched rule with more levels (a tie takes the new-total rule) — levels are never merged | trade | v1 | P9 | R28 A5 |
| **FR-554** | A step pending longer than `warehouse.approval.pending_alert_hours` (default 24) alerts the level's approvers once per episode (in-app, §12b); nothing is ever auto-approved by time | trade | v1 | P9 | `RQP-T3-03` pattern |
| **FR-555** | **My Approvals** (WS-285) lists the user's pending steps across all trade document types with a read-only preview and approve / reject / return; filters by document type, site, currency and value range | trade | v1 | P9 | — |

### 4.3 Purchase requisition *owner: trade* — contract `trade-purchase-requisition`

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-556** | **PR document**: company, requesting site, deliver-to location (optional), department (platform `departments`), cost object (the `p8-10` vocabulary: department / cost centre / production order), requested by, required-by date, priority, justification, source (`MANUAL`, `STORES_SHORTAGE`, `REPLENISHMENT`, `MRP`). Lines: item, quantity, UoM, required date, suggested supplier, estimated rate, source line reference, notes | trade | v1 | P9 | `RM-001` |
| **FR-557** | **PR from shortage.** Two entry points. (a) A stores user's *Send to purchasing* on a core material requisition (`p8-09`) calls trade's `PurchaseRequisitionHandoff.raise` (`ai.warehouse.port.purchase`): trade creates one PR line, source `STORES_SHORTAGE`, maker = the envelope's `actingUserId`, **submits it in the same call** (number issued, approval opened) and returns `HandoffRef('warehouse-trade', 'WHT_PURCHASE_REQUISITION', id, issued number)`; `status(ref)` answers the line's status, ordered and received quantity. (b) A buyer's *Import shortages* on WS-286 lists core shortfalls and replenishment suggestions (incl. origin `MRP`, `p8-16`, `OD-31`) and creates draft PR lines; a converted suggestion is reported through `WhReplenishmentSuggestionPort.markConverted`. One source line feeds **at most one** non-cancelled PR line (partial unique index). The quantity defaults to the shortfall; raising it needs a justification | trade | v1 | P9 | `RM-001` `RM-015` |
| **FR-558** | PR approval runs the matrix on Σ (qty × estimated rate) in the company currency; a PR with no estimates is matched on quantity bands. The estimated rate defaults from the active rate contract, else the last approved PO rate for the item, else blank | trade | v1 | P9 | — |
| **FR-559** | **Consolidation.** The requisition workbench (WS-287) lists approved open PR lines across PRs, groupable by item, site and suggested supplier. The buyer selects lines and creates **one** RFQ, **one** PO, or a release against an agreement. A junction records each PR line × target line × quantity | trade | v1 | P9 | — |
| **FR-560** | **Partial conversion.** A PR line converts in parts; Σ allocated ≤ approved − cancelled, checked under a row lock on the PR line. Line status `OPEN` → `IN_RFQ` (allocated only to RFQ lines) → `PARTIALLY_ORDERED` → `ORDERED`; header follows. The remainder can be closed short with a reason. The requester is notified (in-app, §12b) at each conversion and at close-short | trade | v1 | P9 | — |
| **FR-561** | A PR is cancellable before any allocation; after one, only its open remainder can be closed. A target line's cancellation releases its allocation back to the PR line (the PR line returns to open for that quantity). The PR header is `CLOSED` when every line is terminal (ordered with all targets terminal, closed short or cancelled), whatever its allocation. Cancelling a PR line, or closing short a line that never had an allocation, that converted a core suggestion returns it to `PROPOSED` through `WhReplenishmentSuggestionPort.releaseConversion` | trade | v1 | P9 | — |

### 4.4 RFQ, vendor quotation, comparative statement, award *owner: trade* — contract `trade-rfq-award`

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-562** | **RFQ**: lines from PR lines or manual (item, qty, UoM, required date, specification note), invited suppliers, response due date, deliver-to site, terms. At issue: at least `warehouse.trade.rfq.min_suppliers` (default 3) invited, or a limited-source reason code + note; every invitee passes FR-544 and is not purchase-blocked. An RFQ may be cancelled with a reason from `DRAFT`, `ISSUED`, `BIDS_CLOSED` or `EVALUATION` while no statement is `SUBMITTED` | trade | v1 | P9 | `RM-002` |
| **FR-563** | Issue prints one RFQ document **per supplier** (never showing another supplier) and records sent-at and channel per invitee. Invitee response status: `INVITED` → `RESPONDED` / `DECLINED` (reason) / `NO_RESPONSE` (set at close). A reminder goes to the buyer `warehouse.trade.rfq.reminder_days` before the due date for invitees still `INVITED` | trade | v1 | P9 | — |
| **FR-564** | **Vendor quotation** against an RFQ or unsolicited: supplier's ref and date, valid until, currency, payment / delivery / freight terms, per line offered qty, unit price, discount %, MOQ, lead time days, alternative item (flagged, never silently substituted), free-of-charge flag with reason; header charges (code list, recorded amounts, allocation basis, no tax). The supplier's document attaches through platform documents. A revision creates **version n+1**, also from `EXPIRED`; only the latest non-withdrawn version counts | trade | v1 | P9 | `RM-002` |
| **FR-565** | **Sealed mode** (setting `warehouse.trade.rfq.sealed_until_due`, default `false`, `OD-37`): while the RFQ is open and before its due date, captured prices are hidden from every user except the capturer and the comparative statement cannot be prepared | trade | v1 | P9 | — |
| **FR-566** | **Comparative statement**, **one per RFQ × currency**: a backend-computed matrix RFQ line × supplier — net price, landed price (net + allocated header charges, **excluding tax**), lead time, payment days, MOQ, vendor grade (FR-597), last PO rate, current contract rate — with L1/L2/L3 rank per line by landed price among that statement's currency. Quotations in another currency are shown unranked and can be awarded only on that currency's statement (`OD-34`) | trade | v1 | P9 | `RM-002` |
| **FR-567** | **Recommendation and award** per line; **split award** allowed with Σ awarded over every statement of the RFQ ≤ RFQ line qty. Awarding other than L1 needs an award reason code + note and sets the `non_l1_award` approval condition. The award is approved through the matrix on the awarded value in the statement's currency. A rejected statement returns the RFQ to `BIDS_CLOSED` so a new statement can be prepared; a returned one goes back to `DRAFT` | trade | v1 | P9 | — |
| **FR-568** | On award approval, per awarded supplier the buyer's chosen **award target** is drafted (maker = the statement's preparer): FIXED PO, OPEN PO, BLANKET agreement or purchase rate contract, prefilled from the quotation. PR allocations move from the RFQ lines to FIXED / BLANKET target lines; for OPEN PO and rate-contract targets, which hold no quantity, they return to the PR lines' open quantity (the buyer allocates them to releases later). Unawarded quotations become `NOT_AWARDED`; the RFQ becomes `AWARDED` or `PARTIALLY_AWARDED` | trade | v1 | P9 | — |
| **FR-569** | A quotation whose `valid_until` is before the award date cannot be awarded; the buyer records the supplier's validity extension as a new version. Revising a quotation that a `SUBMITTED` statement uses returns that statement's approval request (comment *quotation revised*), the statement goes back to `DRAFT` stale, and it is refreshed and resubmitted | trade | v1 | P9 | — |

### 4.5 Purchase rate contract *owner: trade* — contract `trade-rate-contract`

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-570** | **Purchase rate contract** per supplier: company, valid from/to, currency, terms, lines item × UoM × rate with optional **quantity slabs** (`from_qty` → rate, evaluated on the order line quantity, `OD-35`), optional ceiling quantity per line with consumed quantity tracked from approved FIXED / BLANKET PO lines and approved OPEN releases. Approval through the matrix; numbering FR-547 | trade | v1 | P9 | `RM-006` `RN-030` |
| **FR-571** | At most one approved rate per (company, supplier, item, UoM) at any date — a database `EXCLUDE` over the dated price rows. Different suppliers may each hold a contract for the same item | trade | v1 | P9 | — |
| **FR-572** | **Price revision** writes a new dated price row (`effective_from`) through a **contract amendment** document (`PRC_AMENDMENT` / `SRC_AMENDMENT` / `PRICE_LIST_AMENDMENT` approval); history is never overwritten. Approved POs keep their rate; an OPEN/BLANKET agreement whose `price_basis = AT_RELEASE` prices each release at the rate effective on the release date, and that price reaches core on the release's schedule lines (`unitPrice`), else the agreement rate | trade | v1 | P9 | R28 A4 |
| **FR-573** | **One price-resolution service** (backend): rate contract (date, slab) → valid awarded quotation → manual. The last PO rate is shown as reference only, never defaulted. A typed or overridden rate sets `price_source = MANUAL` and the `manual_rate` approval condition | trade | v1 | P9 | `RM-006` |
| **FR-574** | Contract expiry alerts `warehouse.trade.contract.expiry_alert_days` (default 30) before `valid_to`; an expired contract prices nothing. **Termination** is a contract amendment with change type `TERMINATE`, a termination date ≥ today and a reason, approved under condition `termination`; **supersession** is stamped when a successor marked *supersedes* is approved. Both take effect **on their date**, never at approval: price rows end on that date and `TradeContractJob` flips the status (`TERMINATED` / `SUPERSEDED`) when it arrives. After termination an `AT_RELEASE` release resolves no contract price and needs a manual one (condition `release_price_manual`) | trade | v1 | P9 | — |

### 4.6 Purchase order *owner: trade (commercial) → core (execution)* — contract `trade-purchase-order`

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-575** | **Three PO types**, immutable after submit: `FIXED` — quantity and rate fixed, one or more dated schedule lines, received without a release; `OPEN` — rate fixed, quantity open (optional ceiling qty per line, optional ceiling value per header), validity, call-off releases; `BLANKET` — agreement with a delivery schedule (item × qty × date) within validity, released schedule line by schedule line. An `OPEN` PO **without a ceiling value** carries the approval condition `open_unbounded` on the PO and on every release, so it never matches a zero-level rule | trade | v1 | P9 | `RM-003` `RM-004` `RM-005` |
| **FR-576** | Header: company, supplier, buyer, order date, deliver-to site and receiving location, currency, payment / delivery / freight terms (recorded), rate contract ref, award ref, validity (OPEN/BLANKET), `receipt_cutoff_date` (OPEN/BLANKET, optional, ≥ `valid_to`; null = released quantity receivable without cut-off), ceilings, `price_basis`, T&C template, notes, MSME acknowledgement (FR-542). Line: item, supplier part no (from `whb_item_supplier_sources`), UoM, qty (FIXED/BLANKET > 0; OPEN null), unit price, discount %, `price_source`, over/under delivery tolerance %, tax classification code (recorded), free-of-charge flag (FIXED / BLANKET only) | trade | v1 | P9 | — |
| **FR-577** | **One core PO per trade PO, created at approval.** Approval calls `WhPurchaseOrderPort.createOrder` (`p8-01`) **in the approval transaction** with `initialStatus = APPROVED`, `approvedByUserId` = the last trade approver (core records `approval_source = SOURCE_MODULE`), `sourceModule = 'warehouse-trade'`, `sourceDocumentType = WHT_PURCHASE_ORDER`, `sourceDocumentId`, `sourceDocumentRef` = the trade PO number, the operation key of §12a, and the lines, rates (`rateSource = AGREEMENT` + contract ref where priced from a contract) and schedule lines. FIXED schedule lines go as `FIRM`; OPEN and BLANKET lines go with `orderedQuantity` null. A port refusal rolls the approval back and shows the core reason on the trade screen | trade | v1 | P9 | `RN-053` |
| **FR-578** | **OPEN** approval creates a core PO of type `OPEN` (rates, no quantities). Each **release** (call-off) adds dated `FIRM` quantities through `releaseSchedule`. Σ released + Σ pending (submitted, not yet approved) ≤ ceiling; a release dated after `valid_to` is refused; after validity no release is accepted and firm released quantities continue to be received until `receipt_cutoff_date` (core `POS-GRD-06`) | trade | v1 | P9 | `RM-004` |
| **FR-579** | **BLANKET**: Σ schedule qty = line agreed qty and every date within validity, checked at submit. Approval creates **one** core PO of type `BLANKET_RELEASE` with `agreementRef` = the agreement number and the whole schedule as `FORECAST` lines (core receives only `FIRM` lines, `POS-UNR-02`; its line ordered quantity stays null until the first firm line, `POS-GRD-02`). Each **release** firms whole schedule lines (`releaseSchedule` `firm`), or adds a `FIRM` line and reduces the `FORECAST` one when it is split or priced differently, with `releaseRef` = the release number. Schedule lines carry zone `FIRM` / `TENTATIVE` (`warehouse.trade.firm_zone_days`, default 14). A job **proposes** releases for schedule lines entering `warehouse.trade.release_horizon_days`; it never releases | trade | v1 | P9 | `RM-005` |
| **FR-580** | **Release document**: number, release date, lines (schedule line or call-off item × qty × date × price), approval `PO_RELEASE` (seeded zero-level `EXACT` rule, so a release carrying `open_unbounded` or `release_price_manual` needs an install rule with levels), print *Schedule Release* to the supplier. A release can be cancelled before approval, and after it for the unreceived part — a line with nothing received is un-firmed or cancelled, a **partly received** line is reduced to its received quantity by `amendOrder` `scheduleChanges.quantity` (core's floor = received) with the unreceived BLANKET quantity restored as `FORECAST` (R31 F-TR-004); a rejected or cancelled release returns its quantity to the schedule and its PR allocation to the PR line (FR-561, R31 F-TR-014). A release is `CLOSED` when every core schedule line carrying its `releaseRef` is received, closed or cancelled | trade | v1 | P9 | — |
| **FR-581** | **Hand-off to stores.** Gate entry (`p8-03`) and GRN (`p8-04`) run against the core PO; trade's PO detail shows gate entries, GRNs with bill no/date/billed qty, QC results, supplier returns and claims **read-only from core**. Trade's fulfilment state (`NOT_STARTED` / `PARTIAL` / `COMPLETE`) is **derived from core quantities on read, never stored** (`FR-123` layered truth) | trade | v1 | P9 | `RM-007` `RM-008` |
| **FR-582** | Over/under delivery tolerance per line is passed to core (over-receipt guard is core's); under-tolerance marks a line *short-close suggested* when the received quantity is within it | trade | v1 | P9 | — |
| **FR-583** | **Cancel** a PO only while nothing is received or on an open gate entry (`getReceiptPosition`); after approval the cancel is an approval request `PO_CANCEL`, and on approval the port cancels the core PO (`cancelOrder`) in the same transaction. Otherwise the only exit is short-close (FR-588). Trade registers a `PurchaseOrderChangeGuard` / `DemandOrderChangeGuard` / `RmaChangeGuard` bean, so a trade-created core PO, demand order or RMA refuses manual edit, approve, cancel and close on core screens with `409 PO_OWNED_BY_SOURCE_MODULE` / `409 DEMAND_OWNED_BY_SOURCE_MODULE` / `409 RMA_OWNED_BY_SOURCE_MODULE`; receipts, allocation, dispatch and RMA expiry run normally | trade | v1 | P9 | R28 §6 guard seam |
| **FR-584** | **Terms & conditions templates** per company × document type (PO, SO, RFQ, quotation), versioned; the version used is frozen on the document and printed | trade | v1 | P9 | — |
| **FR-585** | A supplier blocked after approval: new releases and quantity-increasing amendments are refused with `422 TRADE_SUPPLIER_BLOCKED`; receipts against released quantities continue (core's decision) | trade | v1 | P9 | — |

### 4.6a Subcontract service PO *owner: trade (commercial); MFG (the order, dispatch, receipt); core (the value posting)* — contract `trade-purchase-order` §1.5

`D-18` item 3 (user decision 2026-10-23; R31 `F-MF-005`, `SUB-OPEN-06`): trade **lifts refusal R9** for one case — a
service-line PO linked to a `warehouse-manufacturing` subcontract order. It carries the job worker's processing
charge and lands that charge on the processed item's cost. R8 (general service and capex POs) stays refused.

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-682** | **Subcontract PO.** A `FIXED` PO with `po_purpose = SUBCONTRACT` (header, `STOCK` by default, immutable after submit) orders a job worker's processing for one or more MFG subcontract orders (FRD-MFG FR-658). Each of its lines is a **service line** (`line_kind = SUBCONTRACT_SERVICE`): `item_id` = the **processed item** (the subcontract BOM's main output), `quantity` = the quantity to process in that item's UoM, `unit_price` = the **processing charge** per unit (no material value), and the link `subcontract_order_id` (a bare UUID of `whm_production_orders.id` — **no FK**, trade never references `whm_`, `TRD-09`) + `subcontract_order_ref` (the order number, frozen at save). At most one non-cancelled service line per subcontract order (partial unique index) | trade | v1.1 | P9 | `D-18` `F-MF-005` |
| **FR-683** | **The link is resolved through core, never MFG.** Save and submit resolve `subcontract_order_id` through core's `CostObjectResolver` of type `PRODUCTION_ORDER` (FRD-STORES registry R.3; MFG implements it): the order must resolve (`RELEASED`), be of kind `SUBCONTRACT`, and name the PO's supplier as its job worker — else `422 TRADE_SUBCONTRACT_ORDER_INVALID`. The kind and job-worker fields of the resolved result are asked of STORES (§12c `CN-14` (a)) and filled by MFG from `whm_production_orders.order_type` and `.subcontractor_counterparty_id` | trade | v1.1 | P9 | `D-18` |
| **FR-684** | **No stock line, no core PO.** A subcontract PO holds only service lines and a stock PO none (`422 TRADE_PO_PURPOSE_MIXED`); it is `FIXED` only (OPEN / BLANKET refused, `422 TRADE_SUBCONTRACT_TYPE`) and in the **company currency** only, because the charge lands as a base-currency value and trade never converts (`TRD-06`; `422 TRADE_SUBCONTRACT_CURRENCY`). Its approval creates **no core PO** (FR-577 does not apply): nothing is received against it at the gate or the GRN — the components leave through MFG's subcontract dispatch (india's job-work challan where it applies) and the processed item returns through MFG's subcontract receipt against the order. It has no release, no tolerance push and no core amendment; approval (`PO`, value Σ qty × charge), print, supplier acknowledgement, expediting and trade-side amendment follow the PO rules | trade | v1.1 | P9 | `D-18` |
| **FR-685** | **Processed quantity read from core.** A service line's processed quantity is the processed item's base quantity received into stock by the order's receipts, read on demand through core (§12c `CN-14` (b): the received output of cost object `PRODUCTION_ORDER` × item, with its receiving lots and cost layers), never stored (`TRD-03`); the line's fulfilment (`NOT_STARTED` / `PARTIAL` / `COMPLETE`) is derived from it as FR-581 | trade | v1.1 | P9 | `D-18` |
| **FR-686** | **Service confirmation lands the charge.** The buyer records a **service confirmation** (`wht_po_service_confirmations`, number `<po_number>-Cnn`) on a service line: quantity ≤ processed − already confirmed, date, the job worker's bill no and date (recorded only, §11 R2). In the same transaction trade asks core to post the charge — confirmed quantity × the line's net price, company currency — as **one value-only `LANDED_COST_APPLY`** onto the processed item's lots that the order's receipts created (§12c `CN-14` (c); core posts it, trade never posts a movement, §1; a consumed share goes where core's landed cost sends it, `CVL-T4-07`). Idempotency key `WHT_PURCHASE_ORDER:<poId>:SUBCONTRACT_CHARGE_APPLY:<confirmation no>`; a core refusal rolls the confirmation back and is relayed (`TPO-T4-03`). Closes MFG `SUB-OPEN-06` | trade | v1.1 | P9 | `D-18` `SUB-OPEN-06` |
| **FR-687** | **Correction.** A posted confirmation is corrected only by **reversing** it (reason, `TRADE_ORDER_CLOSE` context), which reverses its core landed-cost posting in the same transaction (§12c `CN-14` (c), key `…:SUBCONTRACT_CHARGE_REVERSE:<confirmation no>`) and frees its quantity; a confirmation is never edited or deleted | trade | v1.1 | P9 | `D-18` |
| **FR-688** | **Close, cancel, amend.** Cancel only while no confirmation is posted (after approval through `PO_CANCEL`, no port call); short-close closes the unconfirmed remainder (`PO_SHORT_CLOSE`, no port call); auto-close when every line is confirmed ≥ qty × (1 − under tolerance) or short-closed (`TradePoCloseJob`). An amendment may change quantity (never below confirmed), charge (unconfirmed quantity only, the `OD-36` twin), dates and terms; the item, the link and the supplier are not amendable (`422 TRADE_FIELD_NOT_AMENDABLE`); it applies trade-side only | trade | v1.1 | P9 | `D-18` |
| **FR-689** | **What stays refused, and the screens.** A service line without a subcontract-order link is refused `422 TRADE_SERVICE_LINE_NEEDS_SUBCONTRACT_ORDER` (R8 stands); the job-work challan, ITC-04 and the bond stay `warehouse-india` / MFG's; tax on the charge, the job worker's invoice and its payment stay accounting's (§11 R2, R4). WS-292 gains a `poPurpose` column and filter and *Add → Subcontract PO*; WS-293 of a subcontract PO shows a *Service confirmations* tab (confirmed quantity, bill ref, the core landed-cost document, read-only) in place of *Releases* and *Receipts*; permission `wht_purchase_orders:confirm_service` (buyer bundle) | trade | v1.1 | P9 | `D-18` |

### 4.7 Acknowledgement, expediting, short-close *owner: trade* — contract `trade-purchase-order`, `trade-sales-order`

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-586** | **Supplier acknowledgement**: ack date, supplier ref, `ACCEPTED` / `ACCEPTED_WITH_CHANGES` / `REJECTED`, per schedule line confirmed date and qty. Differences are shown side by side; with changes, the buyer either accepts (an amendment is drafted from the differences, maker = that buyer) or disputes (follow-up logged). The agreed dates never change except by amendment. The acknowledgement lives in trade only; core's `acknowledged_at` stays null for trade POs | trade | v1 | P9 | — |
| **FR-587** | **Expediting** (WS-295): due and overdue schedule lines — FIXED schedule lines and released OPEN / BLANKET quantities (site timezone, `FR-439`), follow-up log (date, contact, mode, supplier promised date, remarks, next follow-up), reminders on next-follow-up date and `warehouse.trade.expedite.days_before` (default 3) before due. The supplier's promised date is stored apart from the agreed date. A BLANKET schedule line still unreleased when its date minus lead time has passed is shown as *release overdue* on WS-294 | trade | v1 | P9 | — |
| **FR-588** | **Short-close** at line or header with reason (`PO_SHORT_CLOSE` approval, seeded zero-level); the port closes the open quantity in core; OPEN/BLANKET short-close cancels unreleased schedule lines and closes open releases; a header short-close ends with `closeOrder` | trade | v1 | P9 | R28 A |
| **FR-589** | **Auto-close**: a PO becomes `CLOSED` when every line is complete or short-closed, no release is open, no GRN line of it is under QC hold and no supplier return of it is undispatched; an OPEN/BLANKET past validity with nothing open closes by the nightly job. Auto-close calls `closeOrder` in the same transaction | trade | v1 | P9 | — |

### 4.8 Amendments and versions *owner: trade* — contract `trade-order-amendment`

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-590** | **Amendment document** per PO or SO: quantity, rate, dates, schedule lines, add line, cancel line, terms, validity extension, ceilings, receiving location (PO) / ship-to address (SO) inside the same site; reason code; origin `MANUAL` / `ACK_CHANGES` / `CUSTOMER_SCHEDULE` / `SUPPLIER_RETURN`; approval `PO_AMENDMENT` / `SO_AMENDMENT` on new total and delta (FR-553). **One open amendment per order**; while it is open, releases on the **schedule lines it changes** and a header short-close or cancel are refused. A newer customer-schedule import replaces a `DRAFT` amendment of the same origin | trade | v1 | P9 | `RM-005` R28 A5 |
| **FR-591** | Guards: new qty ≥ received (dispatched) + in-flight (open gate entry / unposted GRN / released-not-received, or released-not-shipped); a rate change applies only to un-received quantity (`OD-36`); type, counterparty, company, **site** and currency are not amendable | trade | v1 | P9 | — |
| **FR-592** | On approval: `version_no` + 1, a header + line **snapshot** row set (no JSON), the port pushes the change to core (core PO / demand order), the print is marked *Amendment No. n dated …*, and the acknowledgement resets to pending (PO: supplier re-acknowledges; SO: *Re-send acknowledgement* is due) | trade | v1 | P9 | — |
| **FR-593** | Version history: list, compare any two versions field by field (backend diff), reprint any version | trade | v1 | P9 | — |

### 4.9 Vendor evaluation *owner: trade* — contract `trade-counterparty-evaluation`

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-594** | **Evaluation scheme** per company × side: criteria chosen from a fixed metric catalogue with weights summing to 100 — purchase: `DELIVERY_OTIF`, `QUALITY_ACCEPTANCE`, `PRICE_VARIANCE`, `RFQ_RESPONSE`, `ACK_TIMELINESS`; sales: FR-614 — and grade bands (code list, e.g. A ≥ 85, B ≥ 70, C ≥ 50, D) | trade | v1 | P9 | R28 A7 |
| **FR-595** | **Evaluation run** per period (`MONTHLY` / `QUARTERLY`) computes scores in the backend from core receipt facts (`p6-05`: on-time, short, damaged), core QC accepted vs inspected (`p8-06`), trade schedule dates and rates; a published run is immutable, recalculation creates a new run superseding it | trade | v1 | P9 | `FR-142` |
| **FR-596** | Grade at or below `warehouse.trade.evaluation.review_grade` raises an AVL review task to the trade administrator; the AVL is **never** suspended automatically | trade | v1 | P9 | — |
| **FR-597** | The latest published grade shows on the comparative statement, the PO (a WS-292 column), the AVL, and on the customer side on the customer profile and the SO | trade | v1 | P9 | — |

### 4.10 Sales enquiry, quotation, win/loss *owner: trade* — contract `trade-sales-enquiry-quotation`

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-598** | **Sales enquiry**: customer, customer enquiry ref + date, source (code list), quote-by date, sales executive, lines (item, customer part no via FR-545, qty, UoM, required date, target price, specification note) each with its own outcome (`OPEN`, `QUOTED`, `WON`, `LOST`, `REGRETTED`). Regret (decline to quote) — of the whole enquiry or of single lines, a not-catalogued line (no item yet) included (R31 F-TR-010) — needs a reason and prints a regret letter; a `QUOTED` enquiry may still be quoted or regretted for its remaining open lines, and may be closed as lost when the customer goes silent | trade | v1 | P9 | R28 D |
| **FR-599** | **Customer quotation**: dispatch site (`dispatch_warehouse_id`, required; defaulted from the enquiry, else the customer profile's default dispatch site — a quotation may have no enquiry, §5 M5; R31 F-TR-009), versions, valid until (default `warehouse.trade.quotation.validity_days` = 30), currency, terms, lines priced by FR-604 with discount %, lead time / promised date; header charges (code list, recorded amount, allocation basis — the vendor-quotation shape), carried to the won SO; quotation below floor price, or above `warehouse.trade.sales.discount_approval_pct`, carries the approval condition | trade | v1 | P9 | — |
| **FR-600** | Send/print marks the version `SENT`; a revision (from `SENT` or `EXPIRED`) supersedes it with version n+1; only the latest version can be won or lost; the expiry job marks `EXPIRED` past `valid_until`, and an `EXPIRED` version can still be won when the customer's PO is dated on or before `valid_until`, or lost | trade | v1 | P9 | — |
| **FR-601** | **Win/loss** per line: the win modal records an outcome for every line — `WON` lines draft an SO (FIXED/OPEN/BLANKET) or a sales rate contract from the quotation; `LOST` lines record loss reason, competitor name and competitor price (optional). The quotation is `WON` when any line is won, else `LOST`. The win/loss analysis (WS-300) shows hit rate and lost value by reason, customer, item and executive, per currency; competitor bids are never compared line by line (§11 R10) | trade | v1 | P9 | — |
| **FR-680** | **Lost sale from pre-sales** (`D-17` item 4). An enquiry line **regretted**, or an enquiry / quotation line closed **`LOST`**, with a **stock reason** — a code listed in the setting `warehouse.trade.sales.lost_sale_reason_codes` (default `NO_STOCK`, `LEAD_TIME_NOT_MET`, both seeded in the code lists `trade_regret_reason` and `trade_loss_reason` and as `TRADE_ORDER_CLOSE` reason codes for SO cancel / short-close, FR-546; matched by `code`; neither a code list value nor a reason row has an attribute for it, so the setting is the classification) — records **one** lost sale in core by calling the registered port **`WhLostSalePort.captureLostSale(PortEnvelope, …)`** (FRD-STORES R.2, op `LOST_SALE_CAPTURE`; R31 F-TR-011) in the same transaction: dispatch site, item (or the new-item description when the line has none — the *not catalogued* case), house owner, the line's quantity in base UoM, `sourceDocumentType = TRADE_ENQUIRY_LINE` / `TRADE_QUOTATION_LINE`, `sourceDocumentId` = the line id (core records them as the row's source type / id and the envelope's module as its source system, `POS-T1-40`), and core reason `TRADE_STOCK_NOT_AVAILABLE` (context `SHORT_PICK`, `affects_demand_history = true`, seeded by trade). The row reads `captured_manually = true` and `policy_applied = BLOCK` (core sets both: a person's regret or loss act refused the demand). The line keeps `lost_sale_log_id`, so a line captures once; a non-stock reason (price, capacity, competitor) captures nothing. Core keeps the log and the API; this is now the producer of `FR-257` and `WH-SC-283` | trade | v1 | P9 | `FR-257` `D-17` |

### 4.11 Sales pricing *owner: trade* — contract `trade-rate-contract`

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-602** | **Price list**: code, currency, validity, applicability (all customers or customer categories), **priority** (1 = highest), item × UoM dated prices with optional slabs, floor price per item; approval `PRICE_LIST`. Two approved price lists of equal priority whose applicability intersects may not price the same item × UoM × currency on the same date (`422 TRADE_PRICE_LIST_OVERLAP`) | trade | v1 | P9 | — |
| **FR-603** | **Sales rate contract** per customer: the mirror of FR-570–FR-574 — validity, slabs, ceiling with consumption (approved FIXED / BLANKET SO lines and approved OPEN dispatch releases), `EXCLUDE` against overlap, dated revisions, termination and supersession by amendment | trade | v1 | P9 | — |
| **FR-604** | **One sales price-resolution service**: customer rate contract → customer-category price list (lowest priority number) → general price list (lowest priority number) → manual (`price_source`). A price below the floor sets `below_floor_price` | trade | v1 | P9 | — |

### 4.12 Sales order and dispatch *owner: trade (commercial) → core (execution)* — contract `trade-sales-order`

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-605** | **Three SO types** (mirror of FR-575): `FIXED` (dispatched from its firm schedule without a release), `OPEN` (rate fixed, quantity by customer call-off, `open_unbounded` without a ceiling value), `BLANKET` with a **customer delivery schedule**. Header: customer, customer PO no + date (required by profile flag; a duplicate (customer, customer PO no) on a non-cancelled SO is refused), sales executive, ship-to, dispatch site, currency, terms, price refs, validity, ceilings, `price_basis`. Line: over/under delivery tolerance %. **One core demand order per SO** (`OD-45` option A: its header rolls up from the schedule and returns to `OPEN` after each despatch until trade calls `closeDemand`), created at approval through `WhDemandOrderPort.createDemand` (`p8-02`) with `salesOrderRef`, `customerPoRef/Date` and the schedule: FIXED as `FIRM`, BLANKET as `FORECAST`, OPEN with none until a call-off | trade | v1 | P9 | R28 D1 |
| **FR-606** | SO approval through the matrix; **order acknowledgement** printed and sent with committed dates per schedule line: SO status `ISSUED`, `ack_status` `SENT`. An approved amendment resets `ack_status` to `PENDING` and *Re-send acknowledgement* prints the new version. There is no customer-side acknowledgement status (§5 M22) | trade | v1 | P9 | — |
| **FR-607** | **Dispatch planning** (WS-305): due schedule lines by dispatch site and horizon, with backend-computed available-to-promise from `WhAvailableToPromiseQuery.atp` (FIXED lines shown for ATP only; they need no release); the planner releases whole or part OPEN / BLANKET lines into a **dispatch release**, approved as `SO_RELEASE` (seeded zero-level), which firms them on the SO's core demand order (`firmScheduleLine(…, releaseRef)`, whose optional `releaseRef` re-stamps the firmed line with the release number — R31 F-TR-003 — or `releaseSchedule` for a split or a call-off; `releaseRef` = release number); core allocates firm in-horizon quantity (`warehouse.outbound.schedule_allocation_horizon_days`) and picks / ships it. Release qty > open schedule qty (FIXED / BLANKET) or > ceiling open including pending releases (OPEN) is refused; a shortfall is shown, never blocked. A release can be cancelled before approval and, after it, while nothing of it is picked; a release is `CLOSED` when every core schedule line carrying its `releaseRef` is shipped or cancelled | trade | v1 | P9 | `RN-053` |
| **FR-608** | SO fulfilment (released, picked, shipped, delivered) is **derived from core** demand orders and shipments on read; outward gate pass is `p8-03`, challan / e-way bill is `warehouse-india` | trade | v1 | P9 | R28 D2 D3 |
| **FR-609** | SO cancel / short-close mirror FR-583 / FR-588: cancel after approval is an `SO_CANCEL` request whose approval calls `cancelDemand`; short-close (`SO_SHORT_CLOSE`) cancels unreleased and unpicked schedule lines one by one (`cancelScheduleLine`) and closes the unpicked remainder of a partly picked or shipped `FIRM` line (`closeScheduleLineShort`, R31 F-TR-005), and a header short-close ends with `closeDemand`. Auto-close mirrors FR-589: every line complete (shipped ≥ qty × (1 − under tolerance)) or short-closed, no release open, no SRA open; it closes each tolerated `FIRM` remainder with `closeScheduleLineShort` and then calls `closeDemand` in the same transaction, as trade's service principal (R31 F-TR-006, F-TR-012) | trade | v1 | P9 | — |
| **FR-610** | **Delivery commitment tracking** (twin of expediting): schedule lines due within `warehouse.trade.sales.at_risk_days` that are unreleased or short on ATP; internal follow-up log; customer-informed revised date stored apart from the committed date | trade | v1 | P9 | — |
| **FR-611** | **Customer schedule revision** for BLANKET: a revised schedule (screen or CSV import with dry-run) becomes an SO amendment; changes inside the sales firm zone (`warehouse.trade.sales.firm_zone_days`, default 14) are flagged and counted for FR-614. Unreleased schedule lines live on the core demand order as `FORECAST` lines, which MRP reads and which never reserve stock (`p8-02`, `POS-UNR-03`; closes `OD-32`) | trade | v1 | P9 | — |
| **FR-681** | **Lost sale from the sales order** (`D-17` item 4). An SO line or schedule-line quantity that is **cancelled** (`SO_CANCEL`) or **short-closed** (`SO_SHORT_CLOSE`) with a stock reason (the same setting) — including the remainder of a dispatch release the planner released short because ATP was short (`TSO-T4-12`) and the customer would not take later — records one lost sale for the unshipped quantity through `WhLostSalePort.captureLostSale` (`sourceDocumentType = TRADE_SO_SCHEDULE_LINE`, `sourceDocumentId` = the schedule line id, the same core reason, envelope key `WHT_SALES_ORDER:<soId>:LOST_SALE_CAPTURE:<scheduleLineId>-<approvalRequestId>`; an **OPEN** line has no schedule line, so its released call-off is captured per release line — `TRADE_SO_RELEASE_LINE`, the release line id, key `…:<releaseLineId>-<approvalRequestId>`, accumulated on `wht_so_dispatch_release_lines.lost_sale_quantity`), in the transaction that approves the cancel or short-close, under the `TRD-13` principal (the last approver; the submitter when the seeded zero-level rule approved it) — so once per line and request; `wht_so_schedule_lines.lost_sale_quantity` accumulates what was captured. A cancel for any other reason captures nothing; nothing is captured at release itself, since a release is never refused for ATP (`TSO-UNR-05`), nor when a dispatch release is cancelled, since its quantity returns to the schedule (R31 F-TR-008) | trade | v1 | P9 | `FR-257` `D-17` |

### 4.13 Returns and customer rating *owner: trade* — contracts `trade-sales-return-authorisation`, `trade-counterparty-evaluation`

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-612** | **Sales return authorisation (SRA)** against an SO and its shipped demand-order lines: qty ≤ shipped − already authorised, reason code, expected condition, return-by date, intent `REPLACE` / `CREDIT` / `REWORK` (recorded; `CREDIT` is an accounting hand-over point only), approval `SRA`; approval creates the core RMA `APPROVED` through `WhRmaPort.createRma` (`OD-33`). SRA status follows the RMA: `MATCHED` → `RECEIVED` (or `PARTIALLY_RECEIVED` when the matched quantity is short), `EXPIRED` → closed expired, `CANCELLED` → cancelled; the shipped allowance counts live authorisations and matched quantity only — an expired SRA or a lapsed remainder frees it (R31 F-TR-015). `REPLACE` drafts a replacement dispatch release on receipt, which the received quantity bounds and which is exempt from the schedule, ceiling, validity and FIXED-line gates (TS-F16, R31 F-TR-002); `REPLACE` needs the SO open (`APPROVED` / `ISSUED`) — for a `CLOSED` / `SHORT_CLOSED` SO a replacement is a new SO and the SRA is raised `CREDIT` or `REWORK` (`422 TRADE_REPLACE_NEEDS_OPEN_SO`, twin of FR-613) | trade | v1 | P9 | R28 D4 |
| **FR-613** | **Purchase twin**: the supplier return stays core (`p8-07`, `wh_supplier_returns`); trade shows it on the PO; a supplier return with intent `REPLACE`, once dispatched, drafts a system amendment (origin `SUPPLIER_RETURN`, condition `supplier_return_replacement`) that the buyer submits and that reinstates the quantity as a `FIRM` schedule line through `amendOrder` (`OD-33`). On a closed, short-closed or cancelled PO nothing is reinstated and the buyer is told a new PO is needed | trade | v1 | P9 | `RN-031` |
| **FR-614** | **Customer rating** on the FR-594 engine: `DELIVERY_OTIF` (shipped/delivered vs committed date and qty), `RETURN_RATE`, `SCHEDULE_VOLATILITY` (sales firm-zone changes), `ENQUIRY_CONVERSION`. Payment behaviour is not measured (§11 R4) | trade | v1 | P9 | — |

### 4.14 Print, grids, permissions, non-functional *owner: trade*

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-615** | **Print documents** through core's template renderer (`wh_print_templates`), template kinds seeded by trade: `PURCHASE_REQUISITION`, `RFQ`, `COMPARATIVE_STATEMENT`, `PURCHASE_ORDER` (+ amendment banner), `SCHEDULE_RELEASE`, `CUSTOMER_QUOTATION`, `REGRET_LETTER`, `SALES_ORDER_ACK`, `SALES_RETURN_AUTHORISATION`. **Each consuming task seeds a minimal default template for its kinds**; p9-14 adds the final layouts as new template versions. Every render is a print job; a reprint is flagged. A dispatch release has no print of its own (§5 M32) | trade | v1 | P9 | `FR-224` |
| **FR-616** | Every list screen follows the CLAUDE.md standards: `DynamicDataTable`, `grid_column_definitions` + `filter_definitions` + `grid_preferences` with both default arrays, a `filterUtils.ts` scope per grid, five-tile statistics strip, export as a superset of the grid incl. `createdByName` / `updatedByName`. **Money is never summed across currencies**: a value tile shows the company currency's total and a count of documents in other currencies, and every report or export that totals money groups by currency | trade | v1 | P9 | — |
| **FR-617** | Permissions `wht_<table>:<verb>` (`view`, `create`, `edit`, `export`, plus `submit`, `approve`, `cancel`, `issue`, `release`, `amend`, `short_close`, `acknowledge`, `block`, `publish`); `permission_dependencies` seeded; the auditor bundle gets `:view` only; record scope follows core's company / site grants. Every trade bundle whose actions call a core port is also granted core's **`warehouse:orders:port`** in the trade seed (core seeds its dependencies, §12a), and — because core checks **site scope** before it validates a port command (`WhPurchaseOrderService.java:244-245`) — the **`:view:branch`** scope verb on each core resource its calls touch (`wh_purchase_orders`, `wh_demand_orders`, `wh_rmas`, `wh_replenishment_suggestions`, `wh_material_requisitions`, and `wh_insufficient_stock_log` for the lost-sale port); trade's **service principal** gets **`:view:all`** on the same six (FRD-STORES R.1; R31 F-SR-004; seeded by `p9-01` and each task's bundle seed) | trade | v1 | P9 | — |
| **FR-618** | **Concurrency and idempotency**: optimistic `version` (stale write `409`); every port write carries a `PortEnvelope` whose idempotency key follows the registry shape `<SOURCE_DOCUMENT_TYPE>:<id>:<operation>:<sequence>` (§12a), so a double-clicked Approve creates one core PO; port call and trade transition commit together | trade | v1 | P9 | — |
| **FR-619** | **Reports** (eight): open PO register, PR ageing, schedule adherence (PO vs receipt), dispatch adherence (SO committed vs shipped), rate contract expiry, open SO register, dispatch backlog, quotation hit rate — backend queries, grid + export, money grouped by currency | trade | v1 | P9 | — |

## 5. Mirror table — every purchase capability and its sales twin

**Rule.** Each pair ships **in the same task**, on **separate tables of identical shape** (`TRD-02`),
so a gap on one side is visible in review. Where no twin makes sense the row says why.

| # | Purchase | Sales twin | Same engine? | Task | Note / refusal |
|---|---|---|---|---|---|
| M1 | Supplier trade profile (`wht_supplier_profiles`) — purchase block, MSME, lead time, terms | Customer trade profile (`wht_customer_profiles`) — sales block, category, terms, part-approval flag | no, mirrored tables | p9-02 | MSME fields have no sales twin: the MSMED Act protects the **supplier**; we are the supplier on the sales side and our own Udyam number is a platform company fact |
| M2 | Approved vendor list (`wht_approved_vendor_items`), changes through the approval engine (`AVL`) | Customer item reference + part approval (`wht_customer_item_refs`) | no | p9-02 | **Refused twin for the approval request**: the AVL is our decision and takes maker–checker; a part approval is the customer's decision, so we record it with the customer's document attached (FR-545) |
| M3 | Purchase requisition (internal need) | Sales enquiry (external need) | no | p9-04 / p9-08 | The PR **and** the RFQ together mirror the enquiry: we *send* an RFQ, a customer *sends* us one. There is no outgoing sales "RFQ" |
| M4 | PR from stores shortage / replenishment / MRP | Enquiry from customer; blanket schedule feeds MRP | — | p9-04 / p9-09 | MRP direction is opposite: purchase consumes MRP output (`OD-31`), sales feeds MRP input (`OD-32`) |
| M5 | PR consolidation (many PR lines → one RFQ/PO) | **Refused twin**: one quotation answers one enquiry | — | p9-04 | Customers do not consolidate our quotations; a quotation may be raised with no enquiry |
| M6 | PR partial conversion (line `OPEN` → `IN_RFQ` → `PARTIALLY_ORDERED` → `ORDERED`) | Enquiry partially quoted / partially won: per-line outcome `OPEN` → `QUOTED` → `WON` / `LOST` / `REGRETTED`; remaining lines quotable or regrettable from `QUOTED` | — | p9-04 / p9-08 | — |
| M7 | RFQ issue to N suppliers | — (received as M3) | — | p9-05 | see M3 |
| M8 | Vendor quotation, versions, validity, charges (`wht_vendor_quotation_charges`) | Customer quotation, versions, validity, charges (`wht_customer_quotation_charges`, carried to the SO) | shared version pattern | p9-05 / p9-08 | Revise from `EXPIRED` on both sides |
| M9 | Sealed quotation mode | **Refused twin** | — | p9-05 | Our own quotation cannot be sealed from us |
| M10 | Comparative statement, L1 rank | Quotation version comparison + win/loss analysis | backend diff | p9-05 / p9-08 | Competitor bids are invisible to us; only their reported price on a loss is recorded (§11 R10) |
| M11 | Award with reason (non-L1) | Won / lost with reason, competitor | — | p9-05 / p9-08 | — |
| M12 | Award target → PO / agreement / rate contract | Win → SO / agreement / sales rate contract | — | p9-05 / p9-08 | — |
| M13 | Purchase rate contract (slabs, ceiling, revision) | Sales rate contract (same) | mirrored tables | p9-06 | — |
| M14 | — (supplier sets prices) | Price list (general / category) with floor | — | p9-06 | **Refused purchase twin**: a generic purchase price list duplicates the supplier's quotation and contract; we hold the supplier's price only as M8/M13 |
| M15 | Purchase price resolution | Sales price resolution | two services, same order of precedence | p9-06 | — |
| M16 | PO FIXED / OPEN / BLANKET; FIXED received without a release | SO FIXED / OPEN / BLANKET; FIXED dispatched without a release | mirrored tables | p9-07 / p9-09 | `open_unbounded` on both sides; tolerances on both sides |
| M17 | Supplier delivery schedule (FIRM/TENTATIVE) | Customer delivery schedule (FIRM/TENTATIVE) | mirrored | p9-07 / p9-09 | — |
| M18 | Release (`PO_RELEASE` approval, ceiling consumption) → firms `FORECAST`/adds `FIRM` schedule lines on the one core PO (`releaseSchedule`); cancel, reject-revert, close by `releaseRef` | Dispatch release (`SO_RELEASE` approval, ceiling consumption) → firms schedule lines on the one core demand order (`firmScheduleLine` / `releaseSchedule`); cancel (`unfirmScheduleLine` / `cancelScheduleLine`), reject-revert, close by `releaseRef` | same ladder, same port shape | p9-07 / p9-09 | Symmetric: one core execution document per trade order on both sides; the demand header stays open across releases (`OD-45` option A) until `closeDemand`, as the core PO stays open until `closeOrder` |
| M19 | Release proposal job (horizon); release list WS-294 | Dispatch planning workbench (horizon, ATP); dispatch release list WS-313 | — | p9-07 / p9-09 | ATP (`WhAvailableToPromiseQuery`) shown on sales only; supplier capacity is not known to us |
| M20 | Approval matrix | Same engine | **shared** | p9-03 | — |
| M21 | PO amendment + versions + snapshot | SO amendment + versions + snapshot | shared engine, mirrored tables | p9-11 | — |
| M22 | Supplier acknowledgement captured (`ack_status` `PENDING` → `ACCEPTED` / `ACCEPTED_WITH_CHANGES` / `REJECTED`; reset by amendment; *ack overdue* alert) | Order acknowledgement issued (`ack_status` `PENDING` → `SENT`; reset by amendment; *Re-send acknowledgement*; *ack not sent* alert) | — | p9-10 | Direction is opposite: we **record** a supplier's, we **issue** ours, so the sales ladder has no customer-side states |
| M23 | Expediting + follow-up log | Delivery commitment tracking + follow-up log | mirrored tables | p9-10 | — |
| M24 | Short-close (`PO_SHORT_CLOSE`) / cancel (`PO_CANCEL`) / auto-close via `p8-01` (`closeLine`, `cancelScheduleLine`, `closeOrder`, `cancelOrder`) | Short-close (`SO_SHORT_CLOSE`) / cancel (`SO_CANCEL`) / auto-close via `p8-02` (`cancelScheduleLine`, `closeDemand`, `cancelDemand`) | — | p9-10 | — |
| M25 | Gate entry inward, GRN + bill (core) | Outward gate pass, shipment, challan (core / india) | — | core | read-only roll-up in trade |
| M26 | Supplier return from QC reject (core `p8-07`), `REPLACE` reinstates PO qty through a system amendment (origin `SUPPLIER_RETURN`) | Sales return authorisation → core RMA, `REPLACE` drafts a replacement dispatch release | — | p9-13 | **Purchase side has no trade return document**: core's supplier return already carries approval (`wh_supplier_returns` DRAFT→APPROVED). Both sides hold the order open while a return is unresolved |
| M27 | Vendor evaluation (OTIF, quality, price, response, ack) | Customer rating (OTIF, returns, schedule volatility, conversion) | **shared** engine | p9-12 | — |
| M28 | MSME payment-terms warning | — | — | p9-02 | see M1 |
| M29 | Debit note on short / reject | Credit note on return | — | — | **Both refused** (§11 R3), accounting deferred |
| M30 | Invoice / bill verification | Sales invoice | — | — | **Both refused** (§11 R2) |
| M31 | — | Credit limit / credit check | — | — | **Refused** (§11 R1) |
| M32 | Print: PR, RFQ, CS, PO, schedule release | Print: regret letter, quotation, SO acknowledgement, SRA | shared renderer | p9-14 | **Refused twin: no dispatch-release print.** A schedule release goes to the supplier, who must act on it; a dispatch release is internal, and the FG store works from core's pick list and despatch note, which the shipment already prints |
| M33 | Reports: open PO, PR ageing, schedule adherence, RC expiry | Reports: open SO, dispatch backlog, dispatch adherence, hit rate | — | p9-14 | RC expiry covers both sides |
| M34 | Subcontract service PO — a job worker's processing charge, landed on the processed item (`D-18` item 3, FR-682…FR-689) | **Refused twin** | — | p9-07 | We do not sell processing: job work done **for** a customer on its material is not in scope; the sales side has no service line |

## 6. Screens (WS)

Reference column: **D** = Department (simple CRUD), **C** = Customer (relations + cascading filters),
**SV** = Service Vehicle (stateful workflow + bulk import + transition modals). All routes are web only
(no mobile, user rule 2026-09-11). Menu: trade's own L1 `warehouse_purchase_sales` (*Purchase & Sales*; never `warehouse_trade`, the Trade Portal key P7 deletes — R30 `CP-SC-002`), L2
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
| WS-313 | Dispatch Releases | `/warehouse/trade/sales/dispatch-releases` | SV | Sales — Orders | p9-09 |
| WS-309 | Customer Ratings | `/warehouse/trade/sales/customer-ratings` | SV | Sales — Pre-sales | p9-12 |
| WS-310 | Evaluation Schemes | `/warehouse/trade/masters/evaluation-schemes` | C | Trade Masters | p9-12 |
| WS-311 | T&C Templates | `/warehouse/trade/masters/terms-templates` | D | Trade Masters | p9-02 |
| WS-312 | Trade Reports | `/warehouse/trade/reports/<report>` (8 reports) | D | Trade Reports | p9-14 |

Leaf counts: Trade Masters 8 · Purchasing — Sourcing 5 · Purchasing — Orders 6 · Sales — Pre-sales 5 ·
Sales — Orders 7 · Trade Reports 8. `WS-313` (R29 MA-08) is the sales twin of WS-294; the allocation's last six screen numbers (after `WS-313`, up to 319) are unused.

**Detail-page tabs.** WS-293: Lines · Schedule · Releases · Receipts (core gate entries, GRNs with bill,
QC, MRN — read-only) · Returns & claims (core) · Acknowledgement · Follow-ups · Amendments · Versions ·
Approvals · Audit. WS-304 mirrors it: Lines · Schedule · Dispatch releases · Shipments (core demand orders,
shipments, outward gate passes — read-only) · Returns (SRA + RMA) · Acknowledgement · Commitments ·
Amendments · Versions · Approvals · Audit. Per the view-popup rule, no tab carries more than two sections.
Both detail pages show the latest published counterparty grade in the header (FR-597).

## 7. Scenarios (WH-SC)

Actors: `req1` (department requester, Maintenance), `stores1`, `buyer1`, `pm1` / `pm2` (purchase
approvers), `sales1`, `sm1` (sales approver), `disp1` (dispatch planner), `adm1` (trade administrator),
`aud1` (auditor). Company `ACME`, sites `PLANT-1` (stores + FG store `FG-1`), currency INR. Kind:
happy / edge / error / guard. Scenario numbers `WH-SC-597`…`599` were added on 2026-10-23 for the `D-17` lost-sale rows; the range is now full. The subcontract service PO's scenarios use **`WH-SC-700`…`719`** (`D-18` item 3, allocated in `DECISIONS.md` §6; `700`…`707` used).

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
| **WH-SC-491** | Seeded zero-level `EXACT` rule (empty condition set) for `PO_RELEASE` | `buyer1` releases a BLANKET schedule line at the agreement rate | Release approved at submit by `SYSTEM`, rule id stored on the request; `releaseSchedule` called with `actingUserId = buyer1`, `approvedByUserId` null | FR-550 FR-580 | happy |
| **WH-SC-492** | `pm1` returns a PR with comment | `req1` edits and resubmits | First request `RETURNED` kept; PR back to `DRAFT`; resubmit opens a second request; audit has both | FR-551 | happy |
| **WH-SC-493** | `pm1` delegates to `pm2` 2026-11-01…05; `pm2` is the maker of PO-X | PO-X reaches `pm1`'s step on 11-02 | `pm2` cannot act (maker); `pm1` still can; a delegation from `pm1` to `buyer1` for buyer1's own documents is refused at save | FR-552 FR-549 | guard |
| **WH-SC-494** | A step pending 25 h; `pending_alert_hours=24` | Alert job runs twice | One alert per episode; step still pending; nothing auto-approved | FR-554 | edge |
| **WH-SC-495** | Two rules equally specific for `PR` INR 0–50,000 — the second scoped to site `PLANT-1`, the first to department `MAINT` | `adm1` saves the second | Refused `422 TRADE_APPROVAL_RULE_AMBIGUOUS` naming the first rule: both could match one PR with equal specificity | FR-548 | guard |

### 7.3 Purchase requisition

| ID | Given | When | Then | FR | Kind |
|---|---|---|---|---|---|
| **WH-SC-496** | `req1` (Maintenance) needs 40 `BRG-6205` by 2026-11-20, cost object department `MAINT` | Creates and submits a manual PR | Number issued; estimated rate ₹310 defaulted from active RC; approval on ₹12,400; `pm1` approves; PR `APPROVED`, line `OPEN` | FR-556 FR-558 | happy |
| **WH-SC-497** | Core material requisition MR-88 short 25 `GSK-12` (`p8-09`) | `stores1` clicks *Send to purchasing* on the core MR | Trade's `PurchaseRequisitionHandoff.raise` creates a PR (maker `stores1`, source `STORES_SHORTAGE`, qty 25) **submitted** in the same call; core shows the issued number `PR/2627/00043`; a replay with the same key returns the same PR; a second hand-off of the same line is refused `409 TRADE_SOURCE_LINE_ALREADY_REQUISITIONED` | FR-557 FR-547 | guard |
| **WH-SC-498** | Same, `stores1` raises qty to 40 | Saves without justification | `422` on `justification`; with it, saved | FR-557 | error |
| **WH-SC-499** | Core replenishment suggestion with origin `MRP` (published by MFG through `p8-16`, `OD-31`) for 500 `STL-ROD-20` | `buyer1` converts it | PR source `MRP` linked to the suggestion; trade calls `WhReplenishmentSuggestionPort.markConverted` with the PR number and core shows *Converted by purchasing* | FR-557 | happy |
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
| **WH-SC-514** | α's quotation valid to 11-30, now `EXPIRED`; the statement is `SUBMITTED`; approval on 12-02 | `pm1` approves; `buyer1` then revises α's quotation | Approve refused `422 TRADE_QUOTATION_EXPIRED`; revising the `EXPIRED` version 2 creates version 3 and returns the statement's request (*quotation revised*); the statement, back in `DRAFT`, is refreshed onto version 3, resubmitted and approved | FR-569 FR-564 | guard |

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
| **WH-SC-522** | RC line UoM `BOX` (= 10 `EA`), PO in `EA` | Resolve | Converted through `whb_item_uom_conversions`, factor frozen on the line; no conversion → refused `422 TRADE_UOM_NOT_CONVERTIBLE` | FR-573 | edge |
| **WH-SC-523** | RC currency USD, PO currency INR | Resolve | RC skipped (no FX, §11 R5); line falls to manual | FR-573 | edge |

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
| **WH-SC-531** | `buyer1` releases 60 of the 100 line | Release | On the agreement's single core `BLANKET_RELEASE` PO a `FIRM` line of 60 is added with `releaseRef` `…-R03` and the `FORECAST` line is reduced to 40, which cannot be received; schedule line `PARTIALLY_RELEASED`; print *Schedule Release R-03* | FR-579 FR-580 | happy |
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
| **WH-SC-540** | OPEN PO past validity, all releases received | Nightly job | PO `CLOSED`; `closeOrder` closes the core PO in the same transaction and it leaves the gate-entry PO picker | FR-589 | edge |

### 7.8 Amendments

| ID | Given | When | Then | FR | Kind |
|---|---|---|---|---|---|
| **WH-SC-541** | FIXED line 80: received 40, gate entry open for 30 | Amend qty to 60 | Refused `422 TRADE_AMEND_BELOW_COMMITTED` (40 received + 30 in-flight = 70) | FR-591 | guard |
| **WH-SC-542** | Same, amend qty to 100 and rate ₹298 → ₹295 | Approve | Rate applies to the 60 un-received; version 2 snapshot; port updates core PO; print *Amendment No. 1*; ack pending | FR-590 FR-591 FR-592 | happy |
| **WH-SC-543** | An amendment open on PO-A changing schedule line 2 | `buyer1` releases schedule line 2 / opens a second amendment / releases schedule line 5 | The first two refused (`409 TRADE_AMENDMENT_OPEN`); line 5, which the amendment does not change, releases | FR-590 | guard |
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
| **WH-SC-556** | SO approved | `sales1` sends the acknowledgement | Print *Order Acknowledgement* with committed dates; SO `ISSUED`, `ack_status` `SENT` | FR-606 | happy |
| **WH-SC-557** | BLANKET schedule line 500 due 12-10; FG-1 `availableNow` 320 (`WhAvailableToPromiseQuery`) | `disp1` releases 500 | Allowed; shortfall 180 shown; release approved by `SYSTEM` (seeded `SO_RELEASE` rule); `firmScheduleLine` firms the line on the SO's core demand order (`releaseRef` `…-D02`); core allocates 320 within the horizon and backorders the rest per its fulfilment policy | FR-607 | edge |
| **WH-SC-558** | Open schedule 200 | Release 250 | `422 TRADE_RELEASE_EXCEEDS_SCHEDULE` | FR-607 | guard |
| **WH-SC-559** | Demand order shipped 500 through core, outward gate pass, challan | Open SO detail | *Shipments* tab read-only from core; fulfilment derived; no trade write | FR-608 | happy |
| **WH-SC-560** | Customer revises January from 500 to 350 inside the firm zone | Import revised schedule CSV (dry-run then apply) | Amendment drafted; firm-zone change flagged and counted for `SCHEDULE_VOLATILITY` | FR-611 FR-614 | edge |
| **WH-SC-561** | Schedule line due in 3 days, unreleased; `at_risk_days=5` | Open WS-306 | Line at risk; follow-up with customer-informed date stored apart from committed | FR-610 | happy |
| **WH-SC-562** | Shipped 500, customer returns 20 for `DIMENSION_NC`, intent `REPLACE` | `sales1` raises SRA, `sm1` approves | Core RMA created `APPROVED` (`approvedByUserId = sm1`) through `WhRmaPort.createRma` (`OD-33`); on `WH_RMA_MATCHED` the SRA is `RECEIVED` and a replacement release of 20 is drafted; `CREDIT` would only mark an accounting hand-over point | FR-612 | happy |
| **WH-SC-563** | Shipped 500, authorised 20 | Raise SRA for 490 | `422 TRADE_RETURN_EXCEEDS_SHIPPED` (open 480) | FR-612 | guard |
| **WH-SC-564** | Core supplier return of 30 rejected `BRG-6205` with intent `REPLACE`, dispatched (`WH_SUPPLIER_RETURN_DISPATCHED`) | `buyer1` submits the drafted amendment | A system amendment (origin `SUPPLIER_RETURN`, maker `buyer1` on submit) is approved by the seeded rule; `amendOrder` adds a `FIRM` schedule line of 30; version + 1; shows on WS-293 *Returns & claims* as *replacement due* | FR-613 | happy |
| **WH-SC-565** | `aud1` opens every trade screen | Tries Export / Approve | Views succeed; no Export button and `403` on the API; no write action | FR-617 | guard |

### 7.11 Added by the R29 review (both sides, row for row)

| ID | Given | When | Then | FR | Kind |
|---|---|---|---|---|---|
| **WH-SC-566** | RFQ in `EVALUATION`; its statement is rejected by `pm1` | `buyer1` prepares a second statement, later cancels the RFQ | The RFQ returns to `BIDS_CLOSED` on rejection; the second statement can be prepared; cancel from `BIDS_CLOSED` with reason is allowed | FR-567 FR-562 | edge |
| **WH-SC-567** | OPEN PO γ ceiling 600, released 350; two releases of 150 and 120 submitted, neither approved | Approve both | Pending quantity counts against the ceiling at submit, so the second submit is refused `422 TRADE_CEILING_EXCEEDED` (open 100); a release rejected by `pm1` returns its quantity to the schedule; a `RELEASED` release with nothing received is cancelled through `cancelScheduleLine` | FR-578 FR-580 | guard |
| **WH-SC-568** | `pm1` holds `wht_purchase_orders:approve` but not `warehouse:orders:port` | `pm1` approves a PO | The port refuses `403 PORT_AUTHORITY_REQUIRED`; the approval rolls back and the reason is shown; with the trade approver bundle (which grants the port authority) it succeeds | FR-617 FR-577 | error |
| **WH-SC-569** | `adm1` holds `wht_approval_rules:edit` | `adm1` records *pm1 → adm1*; then *pm1 → pm2*; `pm1` approves L1 and then `pm2` tries L2 for pm1 | The first is refused (delegate = recorder); the second is `PENDING_CONFIRMATION` until `adm2` confirms; `pm2` acting for `pm1` on L2 is refused `403 TRADE_APPROVAL_SELF` (principal already acted) | FR-552 FR-549 | guard |
| **WH-SC-570** | `buyer1` holds AVL create and approve | `buyer1` adds `SUP-ALPHA` for `BRG-6205` and approves it | Approval request `AVL` opened; self-approval `403 TRADE_APPROVAL_SELF`; until `adm1` approves the row has no effect; a rejected entry stays `REJECTED` | FR-544 FR-549 | guard |
| **WH-SC-571** | BLANKET δ `AT_RELEASE`; δ's rate contract terminated on 2027-02-01 by an approved amendment dated 2026-12-15 | Releases on 2027-01-20 and 2027-02-05 | The first is priced from the contract and its `unitPrice` reaches core on the new `FIRM` line; the second resolves no contract price, needs a manual price (`release_price_manual`) and an install rule with a level | FR-572 FR-574 | edge |
| **WH-SC-572** | OPEN PO `valid_to` 2027-10-31, `receipt_cutoff_date` 2027-11-30, release of 50 firm and unreceived | GRN on 2027-11-05, then a release on 2027-11-05 | The GRN posts (core `POS-GRD-06`); the release is refused `422 TRADE_OUTSIDE_VALIDITY` | FR-578 FR-576 | guard |
| **WH-SC-573** | RFQ answered in INR by α and in USD by ε | `buyer1` awards α and ε on one statement | Refused: ε is shown unranked and can be awarded only on the RFQ's USD statement; Σ awarded across both statements ≤ the RFQ quantity | FR-566 FR-567 | guard |
| **WH-SC-574** | PR line 500 `STL-ROD-20` converted an `MRP` suggestion | `req1` cancels the PR | `releaseConversion` returns the suggestion to `PROPOSED` in core in the same transaction | FR-561 | edge |
| **WH-SC-575** | Purchase RC β approved; a termination amendment dated 2027-02-01 approved on 2026-12-15 | Price a PO line on 2027-01-10 and on 2027-02-02 | The first resolves β's price (contract still `APPROVED`); the second does not; `TradeContractJob` sets `TERMINATED` on 2027-02-01 | FR-574 | edge |
| **WH-SC-576** | FIXED PO approved and issued, nothing received | `buyer1` cancels | A `PO_CANCEL` request opens (seeded zero-level), approval calls `cancelOrder`; an install rule with a level makes `pm1` approve it | FR-583 | guard |
| **WH-SC-577** | FIXED PO fully received; a QC hold on 10 of its GRN lines | Nightly auto-close | Held until the QC disposition and any supplier return are resolved; then `CLOSED` with `closeOrder` | FR-589 FR-613 | edge |
| **WH-SC-578** | Supplier return `REPLACE` dispatched for a PO already `SHORT_CLOSED` | Event arrives | Nothing reinstated; `buyer1` is notified that a new PO is needed; WS-293 shows it | FR-613 | edge |
| **WH-SC-579** | BLANKET schedule line due 12-10, lead time 10 days, still `PLANNED` on 12-02 | Expedite job | WS-294 lists it *release overdue*; it does not count against the supplier's OTIF | FR-587 | edge |
| **WH-SC-580** | BLANKET SO, first release of 500 shipped in full | Core despatch | The core demand order returns to `OPEN` (`OD-45`), not `SHIPPED`; the next release firms on the same order; at SO auto-close trade calls `closeDemand` | FR-605 FR-609 | happy |
| **WH-SC-581** | SRA for 20 approved; core matches a return receipt of 15 | `WH_RMA_MATCHED` | SRA `PARTIALLY_RECEIVED` (15), remaining authorisation lapses; with intent `REPLACE` a replacement of 15 is drafted; the SRA closes once it is released or declined | FR-612 | edge |
| **WH-SC-582** | Quotation v2 `EXPIRED` on 12-01 (valid until 11-30); customer PO dated 11-28 arrives 12-03 | `sales1` marks won, then another expired quotation lost | Won accepted with the PO-date evidence; the other is marked lost from `EXPIRED` | FR-600 FR-601 | edge |
| **WH-SC-583** | Enquiry of 3 lines; quotation v1 covers lines 1–2 and is sent (enquiry `QUOTED`) | `sales1` quotes line 3 on a second quotation; the customer wins lines 1 and 3 and loses line 2 | The `QUOTED` enquiry accepts the second quotation for its open line; the win modal records WON / LOST per line; enquiry `PARTIALLY_WON` | FR-598 FR-601 | edge |
| **WH-SC-584** | SO issued; amendment applied | `sales1` opens the SO | `ack_status` `PENDING`; *Re-send acknowledgement* prints version 2 and sets `SENT` | FR-606 FR-592 | happy |
| **WH-SC-585** | Seeded zero-level `EXACT` `SQ` rule with no condition; no other `SQ` rule | `sales1` submits a below-floor quotation | Refused `422 TRADE_NO_APPROVAL_RULE` naming `below_floor_price`; a quotation with no condition is approved by `SYSTEM` | FR-548 FR-550 | guard |
| **WH-SC-586** | Dispatch release of 200 on a BLANKET line, allocated 0 | `disp1` cancels it | `unfirmScheduleLine` returns it to `FORECAST`; the trade schedule line reopens 200; an OPEN call-off release is cancelled through `cancelScheduleLine`; a release with picked quantity is refused `409 TRADE_EXECUTION_STARTED` | FR-607 | guard |
| **WH-SC-587** | BLANKET SO fully released and shipped; SRA `REPLACE` 20 received | `disp1` releases the replacement | Allowed beyond the schedule (bounded by the received 20); a `FIRM` line is added through `releaseSchedule`; the SO stays open until the SRA closes | FR-612 FR-609 | edge |
| **WH-SC-588** | Sales RC for `CUST-OEM1` ceiling 1,000; OPEN SO released 900 | Release 150 | Refused `422 TRADE_CEILING_EXCEEDED` (open 100); a cancelled release gives its quantity back to the contract | FR-603 FR-607 | guard |
| **WH-SC-589** | A `CUSTOMER_SCHEDULE` amendment `DRAFT` changing January | Next week's import; a release of February | The import replaces the draft (old one `CANCELLED`); the February release proceeds | FR-590 FR-611 | edge |
| **WH-SC-590** | Price lists `PL-OEM` (category `OEM`, priority 1) and `PL-OEM-PROMO` (category `OEM`, priority 1), both pricing `HSG-100` in INR in January | Approve the second | Refused `422 TRADE_PRICE_LIST_OVERLAP`; with priority 2 it approves and the priority-1 list prices first | FR-602 FR-604 | guard |
| **WH-SC-591** | Open SOs in INR (₹40,00,000) and USD ($20,000) | Open WS-303 | The *open value* tile shows ₹40,00,000 and *+1 in other currencies*; the open SO register export groups totals by currency | FR-616 FR-619 | guard |
| **WH-SC-592** | Customer scheme: OTIF 50, returns 20, volatility 20, conversion 10; October: 18/20 lines on time in full, 30 returned of 1,000 shipped, 2 firm-zone changes of 20 lines due, 3 of 4 enquiries won | Run and publish October | Score 0.5×90 + 0.2×97 + 0.2×90 + 0.1×75 = 89.9 → grade A on the customer profile and the SO | FR-614 FR-597 | happy |
| **WH-SC-593** | `sales1` holds `wht_sales_orders:approve` | `sales1` approves his own SO | `403 TRADE_APPROVAL_SELF` | FR-549 FR-605 | guard |
| **WH-SC-594** | SO approved on 12-01, acknowledgement not sent; `warehouse.trade.sales.ack_send_alert_days = 1` | Job on 12-02 | One *ack not sent* alert to the sales executive | FR-606 | edge |
| **WH-SC-595** | Supplier `SUP-BETA` block requested by `buyer1` | `pm1` (holds `wht_supplier_profiles:approve`) approves | Profile blocked; `WH-SC-484` completes; without the permission `pm1` cannot act | FR-542 FR-549 | guard |
| **WH-SC-596** | FIXED SO approved: schedule 300 on 12-05 | Open WS-305 | The line shows ATP and shortfall but offers no *Release*: core allocates it inside the horizon as a `FIRM` line | FR-605 FR-607 | edge |
| **WH-SC-597** | Enquiry line 400 `HSG-100` for `CUST-OEM1`; FG-1 holds 0; quotation v1 `SENT` | `sales1` records the line `LOST` with reason `NO_STOCK`; a second line is lost with `PRICE` | One `wh_insufficient_stock_log` row: FG-1, `HSG-100`, 400, `is_lost_sale = true`, reason `TRADE_STOCK_NOT_AVAILABLE`, source `WAREHOUSE_TRADE` / `TRADE_QUOTATION_LINE` / the line id, available 0 read by core; the `PRICE` line captures nothing; recording the outcome again captures nothing more | FR-680, FR-257 | happy |
| **WH-SC-598** | Enquiry line for a part the plant does not catalogue (no `item_id`, description *Cover 7-B*) | `sales1` regrets the line with `NO_STOCK` | A *not catalogued* lost sale: item description stored, available 0; the regret letter prints as usual (`WH-SC-552` with `NO_CAPACITY` captures nothing) | FR-680, FR-257 | edge |
| **WH-SC-599** | BLANKET SO line, schedule line 500 due 12-10; FG-1 ATP 320; customer will not wait | `disp1` releases 320 and requests short-close of the remaining 180 with reason `NO_STOCK`; `sm1` approves | Core schedule line cancelled for 180 (`TSO-T4-06`); one lost sale of 180 sourced `TRADE_SO_SCHEDULE_LINE`; a cancel with `CUSTOMER_REQUEST` captures nothing | FR-681, FR-257 | happy |

### 7.x Subcontract service PO (`D-18` item 3; scenario range `WH-SC-700`…`719`, `DECISIONS.md` §6)

| ID | Given | When | Then | FR | Kind |
|---|---|---|---|---|---|
| **WH-SC-700** | MFG subcontract order `SCO-0042` (`RELEASED`, kind `SUBCONTRACT`, job worker `JW-ANODE`) to process 500 `HSG-100`; core resolves `PRODUCTION_ORDER` | `buyer1` saves a `SUBCONTRACT` PO to `JW-ANODE`, one service line: `HSG-100`, 500, charge ₹12/unit, link `SCO-0042` | Saved `DRAFT`; `subcontract_order_ref = SCO-0042` frozen; no `whm_` read, no FK; value ₹6,000 | FR-682 FR-683 | happy |
| **WH-SC-701** | As `WH-SC-700`, but `SCO-0042`'s job worker is `JW-PLATE` | `buyer1` saves the PO to `JW-ANODE` | Refused `422 TRADE_SUBCONTRACT_ORDER_INVALID`; nothing saved | FR-683 | guard |
| **WH-SC-702** | A `SUBCONTRACT` PO in `DRAFT` | `buyer1` adds a stock line; separately, a `STOCK` PO adds a service line with no link; separately, the subcontract PO is set to USD | `422 TRADE_PO_PURPOSE_MIXED`; `422 TRADE_SERVICE_LINE_NEEDS_SUBCONTRACT_ORDER` (R8 stands); `422 TRADE_SUBCONTRACT_CURRENCY` | FR-684 FR-689 | error |
| **WH-SC-703** | The `WH-SC-700` PO submitted | `pm1` approves it (last level) | `APPROVED`; **no core PO** is created and no port call is made; the line is `OPEN`; WS-293 shows *Service confirmations*, not *Releases* / *Receipts* | FR-684 FR-689 | happy |
| **WH-SC-704** | `SCO-0042`'s subcontract receipt put 300 `HSG-100` into stock at `PLANT-1` on two lots | Open WS-293 | Processed 300 read from core's received output (`CN-14` (b)), never stored; line `PARTIAL` | FR-685 | happy |
| **WH-SC-705** | As `WH-SC-704` | `buyer1` confirms 300 with bill `JW/118` dated 12-04; then tries to confirm 1 more | Confirmation `<po_number>-C01` `POSTED`; core posts **one value-only `LANDED_COST_APPLY`** of ₹3,600 over the two lots by remaining quantity (`CN-14` (c)); the extra 1 is refused `422 TRADE_CONFIRMATION_EXCEEDS_PROCESSED` (open 0); a replay of the same key posts nothing | FR-686 | happy |
| **WH-SC-706** | `-C01` `POSTED`; 100 of the 300 already issued | `buyer1` reverses `-C01` with a `TRADE_ORDER_CLOSE` reason | `-C01` `REVERSED`; core reverses its posting exactly, the consumed share included (`CVL-T4-07`); 300 is confirmable again; the confirmation is never edited or deleted | FR-687 | edge |
| **WH-SC-707** | 300 confirmed, 200 never processed; under tolerance 0 | `buyer1` short-closes the PO; separately, an amendment changes the link to `SCO-0050` | Remainder 200 closed (`PO_SHORT_CLOSE`, no port call), PO `CLOSED`; the amendment is refused `422 TRADE_FIELD_NOT_AMENDABLE` | FR-688 | guard |

## 8. Data model summary (authority for the task files; `DATA-MODEL.md` gains it through SPINE)

Money `DECIMAL(19,4)`, unit price `DECIMAL(19,6)`, quantity `DECIMAL(18,4)`, percent `DECIMAL(9,6)` —
the convention core already uses (`V510011:99-101, 208-225`). Every table: `id UUID`, `version BIGINT`,
audit columns, `company_id` NOT NULL. Status columns `VARCHAR(30)` with **no `CHECK`**.

| Migration | Tables | Task |
|---|---|---|
| `V550000` | bootstrap: asserts platform, base (incl. the `btree_gist` extension base creates in `V500012`) and the core contract it consumes (`wh_purchase_orders.po_type`, `.source_module`, `.receipt_cutoff_date`, `wh_purchase_order_schedule_lines.unit_price`, `wh_port_operations`, `wh_demand_orders.sales_order_ref`, `wh_demand_order_schedule_lines` — `p8-01`/`p8-02`); the port beans are checked at start-up (FR-540) | p9-01 |
| `V550010` | `wht_supplier_profiles`, `wht_customer_profiles`, `wht_approved_vendor_items` (+ `approval_state` `PENDING`/`APPROVED`/`REJECTED`, `approval_request_id`), `wht_customer_item_refs`, `wht_terms_templates`, `wht_terms_template_versions` | p9-02 |
| `V550011` | seed: code lists, `whb_document_types` + series (FR-547 list — no release or amendment series), print template kinds — owning-module guard. `whb_source_systems` (`WAREHOUSE_TRADE`) is seeded once, by `V551000` | p9-02 |
| `V550020` | `wht_approval_rules` (+ `condition_match_mode` `EXACT`/`INCLUDES`), `wht_approval_rule_conditions`, `wht_approval_rule_levels`, `wht_approval_rule_level_users`, `wht_approval_requests`, `wht_approval_steps`, `wht_approval_delegations` (+ `recorded_by`, `status` `ACTIVE`/`PENDING_CONFIRMATION`, `confirmed_by`) | p9-03 |
| `V550030` | `wht_purchase_requisitions` (+ `handoff_idempotency_key`, uk), `wht_purchase_requisition_lines`, `wht_requisition_allocations` | p9-04 |
| `V550040` | `wht_rfqs`, `wht_rfq_lines`, `wht_rfq_suppliers`, `wht_vendor_quotations`, `wht_vendor_quotation_lines`, `wht_vendor_quotation_charges`, `wht_comparative_statements` (+ `currency_code`; uk `(rfq_id, currency_code)` among non-rejected), `wht_comparative_statement_awards` | p9-05 |
| `V550050` | `wht_purchase_rate_contracts`, `wht_purchase_rate_contract_lines`, `wht_purchase_rate_contract_prices` (dated, `EXCLUDE`), `wht_purchase_rate_contract_slabs`; `wht_price_lists` (+ `priority`), `wht_price_list_categories`, `wht_price_list_prices`, `wht_price_list_slabs`; `wht_sales_rate_contracts`, `_lines`, `_prices`, `_slabs`; contract headers + `terminates_on`, `superseded_on`, `superseded_by_id`; the shared amendment engine `wht_rate_contract_amendments` (`contract_kind` `PRC`/`SRC`/`PL`) + `wht_rate_contract_amendment_changes` | p9-06 |
| `V550060` | `wht_purchase_orders` (+ `deliver_to_location_id`, `receipt_cutoff_date`, `po_purpose` `STOCK`/`SUBCONTRACT`), `wht_purchase_order_lines` (+ `replacement_pending_quantity`, `line_kind` `STOCK`/`SUBCONTRACT_SERVICE`, `subcontract_order_id` bare UUID — no FK, `subcontract_order_ref`; FR-682), `wht_po_schedule_lines`, `wht_po_releases` (+ `approval_request_id`, `cancel_reason_code_id` ↓ `whb_reason_codes`), `wht_po_release_lines` (+ `unit_price`, `core_schedule_line_id`), `wht_po_charges`, `wht_po_service_confirmations` (`po_line_id`, `confirmation_number`, `quantity`, `confirmed_on`, `job_worker_bill_no`, `job_worker_bill_date`, `charge_value`, `core_landed_cost_ref`, `status` `POSTED`/`REVERSED`, `reversal_reason_code_id`; FR-686, FR-687) | p9-07 |
| `V550070` | `wht_sales_enquiries`, `wht_sales_enquiry_lines` (`line_outcome`, `lost_sale_log_id`), `wht_customer_quotations` (+ `dispatch_warehouse_id` NOT NULL ↓ `whb_warehouses`, FR-599), `wht_customer_quotation_lines` (`line_outcome`, loss fields per line, `lost_sale_log_id`), `wht_customer_quotation_charges` | p9-08 |
| `V550080` | `wht_sales_orders` (+ `price_basis`, `ack_status`, `ceiling_quantity`/`ceiling_value`), `wht_sales_order_lines` (+ `over_tolerance_pct`, `under_tolerance_pct`), `wht_so_schedule_lines` (+ `lost_sale_quantity`, FR-681), `wht_so_dispatch_releases` (+ `approval_request_id`, `is_replacement`, `source_sra_id`, `cancel_reason_code_id` ↓ `whb_reason_codes`), `wht_so_dispatch_release_lines` (+ `unit_price`, `core_schedule_line_id`, `lost_sale_quantity` for OPEN call-offs), `wht_so_charges` | p9-09 |
| `V550090` | `wht_po_acknowledgements`, `wht_po_ack_lines`, `wht_po_followups`, `wht_so_acknowledgements` (one per version sent), `wht_so_commitment_followups` | p9-10 |
| `V550100` | `wht_po_amendments` (origin + `SUPPLIER_RETURN`), `wht_po_amendment_changes`, `wht_purchase_order_versions`, `wht_purchase_order_line_versions`, `wht_po_schedule_line_versions`; the `wht_so_*` mirror set | p9-11 |
| `V550110` | `wht_evaluation_schemes`, `wht_evaluation_criteria`, `wht_evaluation_grade_bands`, `wht_evaluation_runs`, `wht_counterparty_evaluations`, `wht_counterparty_evaluation_scores` | p9-12 |
| `V550120` | `wht_sales_return_authorisations` (+ `return_by_date`, `received_short`, `reason_code_id` ↓ `whb_reason_codes`), `wht_sales_return_authorisation_lines` (+ `reason_code_id`) | p9-13 |
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
| `TRD-07` | Trade has its **own L1 menu** (`warehouse_purchase_sales`, *Purchase & Sales*) with six L2 sections ≤ 8 leaves. The key is **not** `warehouse_trade`: P7 removes that L1 (the Trade Portal, FR-491) and `WH-SC-662` asserts its absence; a reused key would also bring back favourites, visit history and grants stored against the portal (R30 `CP-SC-002`) | Keeps `warehouse_operations` under its 10-section cap; one toggle hides one tree |
| `TRD-08` | **Approval never times out into approval**; zero-level rules are explicit rows | `FR-408` maker–checker |
| `TRD-09` | **MRP and stores shortages reach trade by pull from core**, never by a sibling call: MFG publishes core replenishment suggestions with origin `MRP` (`p8-16`, `OD-31`), stores writes material requisitions (`p8-09`); trade converts them | FKs point down only; siblings never depend on each other |
| `TRD-10` | Price precedence: purchase — rate contract → valid awarded quotation → manual; sales — customer RC → category price list → general price list → manual. Last price is reference only | One resolution order per side, testable |
| `TRD-11` | Release proposals are **proposed, never auto-released** | A release is a commitment to a supplier |
| `TRD-12` | **A FIXED order needs no release on either side.** Its schedule goes to core `FIRM` at approval; core receives it (PO) or allocates it inside the horizon (SO). Releases exist only for OPEN call-offs and BLANKET schedule lines | R29 TS-F14 / MA-17: the sales side had FIXED firm lines that a release was also supposed to firm |
| `TRD-13` | **Port principal = the person whose act causes the call** (the last approver; the submitter of a `SYSTEM`-approved document); a **scheduled job** calls as trade's **service principal**, one non-interactive user seeded by `p9-01` (`V551000`: stable UUID, login disabled, account locked), never under the order's buyer / sales executive. Every trade bundle that acts so, and the service principal, is granted `warehouse:orders:port` in trade's seed, plus core **site scope** on the resources the calls touch — `:view:branch` for a bundle, `:view:all` for the service principal (FR-617) | FRD-STORES registry R.1, `STO-D20` (`CN-7`); R29 TP-F6; R31 F-SR-004 |
| `TRD-14` | **Approval conditions match exactly by default** (`EXACT`): a rule without conditions covers only a document without conditions, so a zero-level default can never approve a below-floor quotation or an unbounded open order | R29 TS-F8, TP-F7 |
| `TRD-15` | **Contract termination and supersession are dated, not immediate**: price rows end on the date; the status flips on the date | R29 TP-F20, TS-F23 |

## 10. Open decisions (OD-30…OD-39)

| # | Question | Recommended default (adopted unless overruled) | Blocks |
|---|---|---|---|
| **OD-30** | One number or two for a purchase order? | **The trade number is the supplier-facing number.** It is printed on the PO and stored as the core PO's `source_document_ref`; the core PO keeps its internal `po_number` (core's series, `p8-01` has no number parameter). Owed by STORES: the gate entry (`p8-03`) and GRN PO pickers match **either** number and **show both** (R31 decisions, `TPO-OPEN-02`), and WS-072 shows `source_document_ref` as *Supplier PO no.* | FR-547, FR-577 |
| **OD-31** | How does MRP output reach a PR without a sibling-to-sibling dependency? | MFG writes **core `wh_replenishment_suggestions` rows with origin `MRP`** (planned purchase) through STORES `p8-16`'s `WhReplenishmentSuggestionPort.publishExternal`; trade converts them (FR-557), calls `markConverted`, and registers the optional `SuggestionConversionOwner` bean so core's own *Convert to PO* is withdrawn while trade is on. Seam published by `p8-16`; MFG to confirm (`OD-40`…`44` range) | FR-556, FR-557 |
| **OD-32** | How does MRP see unreleased customer schedule lines? | **Closed by `p8-02`:** the SO's core demand order carries them as `FORECAST` schedule lines that never reserve; MRP reads core. Trade keeps them equal to the unreleased schedule on every approval, release and amendment. The header of that one order follows **STORES `OD-45` option (A)** (adopted): it rolls up from its schedule lines, returns to `OPEN` after each despatch and never goes `SHIPPED`/`DELIVERED` until trade calls `closeDemand` (`POS-T1-12a`, `-12b`) | FR-605, FR-611 |
| **OD-33** | Port for creating a core RMA from an SRA, and the supplier-return `REPLACE` intent | **Published by STORES `p8-15`** (`FR-506`): `WhRmaPort.createRma` (created `APPROVED` with `approvedByUserId`) / `cancelRma` / `getRmaPosition`, the `RmaChangeGuard` seam, `intent_code` on `wh_supplier_returns` and outbox `WH_SUPPLIER_RETURN_DISPATCHED`, `WH_RMA_MATCHED` / `_EXPIRED` / `_CANCELLED`. PO reinstatement needs no new op: a trade amendment of origin `SUPPLIER_RETURN` calls `amendOrder` to add a `FIRM` schedule line (FR-613) | FR-612, FR-613 |
| **OD-34** | Approval bands and ranking for foreign-currency documents | Rules are **per currency**; no rule → refusal; comparative statement ranks only same-currency quotations | FR-548, FR-566 |
| **OD-35** | Slab basis: per order line, or cumulative over the contract? | **Per order line** in v1; cumulative slabs need a retroactive price change, which is accounting | FR-570 |
| **OD-36** | Rate amendment after partial receipt | Applies to **un-received quantity only**; received units keep their GRN valuation; no revaluation (accounting deferred) | FR-591 |
| **OD-37** | Sealed bids default | Setting exists, **default off** | FR-565 |
| **OD-38** | Does a trade PO carry `qc_required` or do core inspection plans decide? | **Core inspection plans decide** (`p8-05`/`p8-06`); trade carries nothing | FR-576 |
| **OD-39** | May core screens edit a core PO / demand order / RMA that trade created? | **Closed by `p8-01`/`p8-02`/`p8-15`:** trade registers `PurchaseOrderChangeGuard` (refuses `EDIT`, `RELEASE_SCHEDULE`, `SUBMIT`, `APPROVE`, `RETURN`, `CANCEL`, `CLOSE`, `CLOSE_LINE` → `409 PO_OWNED_BY_SOURCE_MODULE`), `DemandOrderChangeGuard` (refuses `EDIT`, `RELEASE`, `CANCEL`, `CLOSE`; allows `ALLOCATE` → `409 DEMAND_OWNED_BY_SOURCE_MODULE`) and `RmaChangeGuard` (refuses `EDIT`, `APPROVE`, `CANCEL`; allows `EXPIRE` → `409 RMA_OWNED_BY_SOURCE_MODULE`); receipts, allocation and dispatch are not guarded | FR-583 |

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
| R9 | **Subcontract / job-work PO** — *lifted for one case by `D-18` item 3*: a service-line PO linked to an MFG subcontract order is built (§4.6a, FR-682…FR-689) | the job-work challan, ITC-04 and the bond stay `warehouse-india` + MFG | Job work runs through `warehouse-india` (`RN-053`); only its commercial charge is trade's | FR-682 |
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

Names are FRD-STORES *"Port & seam registry (authoritative)"* (R.2 ports, R.3 SPIs, R.4 events).

| Owed by | Item | Used by |
|---|---|---|
| STORES `p8-01` | `WhPurchaseOrderPort` (`ai.warehouse.port.purchase`): `createOrder`, `releaseSchedule` (`firm` / `add` entries with optional `unitPrice`), `amendOrder`, `cancelScheduleLine`, `closeLine`, `closeOrder`, `cancelOrder`, `getReceiptPosition`; `receiptCutoffDate`; `wh_port_operations` idempotency; `PurchaseOrderChangeGuard`; `warehouse:orders:port` seeded with its `permission_dependencies` (`V511400`); events `WH_PO_SCHEDULE_RELEASED`, `WH_PO_AMENDED`, `WH_PO_CLOSED`, `WH_PO_CANCELLED`, `WH_PO_LINE_RECEIVED`, `WH_PO_SCHEDULE_LINE_RECEIVED` | p9-07, p9-10, p9-11, p9-13 |
| STORES `p8-02` | `WhDemandOrderPort` (`ai.warehouse.port.demand`): `createDemand`, `releaseSchedule`, `firmScheduleLine`, `unfirmScheduleLine`, `cancelScheduleLine`, `amendDemand`, `cancelLine`, `cancelDemand`, `closeDemand` (`OD-45`), `getFulfilmentPosition`; `WhAvailableToPromiseQuery.atp`; `DemandOrderChangeGuard`; schedule-driven header ladder (`POS-T1-12a`, `-12b`); events `WH_DEMAND_SHIPPED`, `WH_DEMAND_AMENDED`, `WH_DEMAND_CANCELLED` | p9-09, p9-10, p9-11, p9-13 |
| STORES `p8-03` / `p8-04` | Gate entry and GRN PO pickers match `source_document_ref` as well as `po_number` (`OD-30`); bill no / date / billed qty readable | p9-07 (read-only tabs) |
| STORES `p8-06` / `p8-07` | QC accepted / inspected per GRN line by supplier, QC hold per GRN line; supplier return with intent | p9-10 (auto-close hold), p9-12, p9-13 |
| STORES `p8-09` / `p8-10` | Shortage line query; the optional `PurchaseRequisitionHandoff` SPI trade implements (`raise` returns the **issued** number, `status`; `FR-528`, `MRQ-T1-11`, `-13`); cost-object vocabulary | p9-04 |
| STORES `p8-15` | `WhRmaPort` (`ai.warehouse.port.returns`): `createRma` (`initialStatus` `APPROVED` + `approvedByUserId`), `cancelRma`, `getRmaPosition`; `RmaChangeGuard`; supplier-return `intent_code`; events `WH_RMA_MATCHED`, `WH_RMA_EXPIRED`, `WH_RMA_CANCELLED`, `WH_SUPPLIER_RETURN_DISPATCHED` (`OD-33`) | p9-13 |
| STORES `p8-16` | `WhReplenishmentSuggestionPort` (`ai.warehouse.port.replenishment`): `markConverted`, `releaseConversion`, `getSuggestionStatus` (and `publishExternal`, used by MFG); optional `SuggestionConversionOwner` SPI trade implements (`OD-31`) | p9-04 |
| STORES `p8-02` / `p8-15` / registry | The R31 agreed port changes (§12c `CN-9`…`CN-13`): `firmScheduleLine(…, releaseRef)`, `closeScheduleLineShort`, `WhLostSalePort.captureLostSale`, the `amendOrder` received floor, the port-principal site-scope rule | p9-07, p9-08, p9-09, p9-10, p9-01 |
| STORES (core landed cost, `CostObjectResolver`) | §12c `CN-14`: resolver kind + job worker, the received-output read, a value-only landed-cost apply onto non-GRN lots (FR-683, FR-685, FR-686) | p9-07 (subcontract) |
| MFG | MRP publishes core replenishment suggestions with origin `MRP` through `p8-16` (`OD-31`); reads `FORECAST` + `FIRM` demand schedule from core (`OD-32`); fills `CN-14` (a) and (b) for `PRODUCTION_ORDER` and never reads `wht_` (FR-682) | p9-04, p9-07, p9-09 |
| SPINE | `DATA-MODEL.md`, `BUILD-SPEC-SCREENS.md` (incl. `WS-313`), `SCENARIO-CATALOGUE.md` (incl. `WH-SC-566`…`-596`), `MODULE-INTEGRATION.md` rows for `warehouse-trade`; D-12 release unit for P9; confirm `OD-45` | all |

### 12a. Trade's side of every port call (aligned to the registry)

**Envelope.** Every write passes `PortEnvelope(sourceModule = 'warehouse-trade', idempotencyKey, actingUserId)`.
**Key shape** (registry R.1): `<SOURCE_DOCUMENT_TYPE>:<id>:<operation>:<sequence>`, where the source document
type is the trade document that owns the core one (`WHT_PURCHASE_ORDER`, `WHT_SALES_ORDER`, `WHT_SRA`,
`WHT_PURCHASE_REQUISITION`, and for a lost sale `WHT_SALES_ENQUIRY` / `WHT_CUSTOMER_QUOTATION`), the operation is the registry's operation key, and the sequence is the trade
sub-document that caused the call (release, amendment or approval-request number), so a replay returns the
recorded result and a changed body is refused `409 PORT_IDEMPOTENCY_CONFLICT`. **Principal** (`TRD-13`): the
last approver of the triggering request; for a `SYSTEM`-approved request its submitter (`approvedByUserId`
null); for a scheduled job trade's **service principal** (FRD-STORES `STO-D20`: the non-interactive user `p9-01`
`V551000` seeds, never the order's buyer or sales executive; a `403 PORT_AUTHORITY_REQUIRED` is recorded on
the job run and notified to the trade administrator). **Site scope** (R31 F-SR-004): core checks the caller's
site scope before it validates a command, so every principal also holds the scope verb on the core resources
it touches — a person's bundle `:view:branch`, the service principal `:view:all` (FR-617). A refusal rolls the trade transaction back and is relayed
(`TPO-T4-03`).

| Trade act | Port method | Operation | Idempotency key | Contract row |
|---|---|---|---|---|
| PO approved | `WhPurchaseOrderPort.createOrder` | `PO_CREATE` | `WHT_PURCHASE_ORDER:<poId>:PO_CREATE:1` | `TPO-T4-01` |
| Release approved — whole BLANKET line | `releaseSchedule` `firm(scheduleLineId, unitPrice?)` — `unitPrice` = the release price when `AT_RELEASE` (`STO-D19`) | `PO_RELEASE` | `…:PO_RELEASE:<release no>` | `TPO-T4-02` |
| Release approved — OPEN call-off or BLANKET split | `releaseSchedule` `add(poLineId, FIRM, date, qty, unitPrice)`; the BLANKET `FORECAST` line reduced by `amendOrder` `scheduleChanges` or ended by `cancelScheduleLine` | `PO_RELEASE` + `PO_AMEND` / `PO_CANCEL_SCHEDULE` | `…:PO_RELEASE:<release no>`, `…:PO_AMEND:<release no>`, `…:PO_CANCEL_SCHEDULE:<release no>-<schedule no>` | `TPO-T4-02` |
| Release cancelled after approval | `unfirmScheduleLine` (whole-firmed BLANKET lines, nothing received; `STO-D19`); `cancelScheduleLine` (added `FIRM` lines, nothing received) + `amendOrder` restoring a split BLANKET `FORECAST` (`scheduleChanges`, or `newScheduleLines` when it was ended); a **partly received** line → `amendOrder` `scheduleChanges.quantity` = received (core's floor) with the unreceived BLANKET quantity restored as `FORECAST` in the same command (`CN-12`, R31 F-TR-004) | `PO_UNFIRM_SCHEDULE`, `PO_CANCEL_SCHEDULE`, `PO_AMEND` | `…:<op>:<release no>-X<n>` | `TPO-T4-09` |
| Amendment applied (incl. origin `SUPPLIER_RETURN`) | `amendOrder`, added schedule lines as `newScheduleLines` in the same command (`CN-2`), a deliver-to change as `lineChanges.receivingLocationId`, a tolerance change as `lineChanges.overTolerancePct` / `underTolerancePct` (`CN-8`); `cancelScheduleLine` | `PO_AMEND`, `PO_CANCEL_SCHEDULE` | `…:PO_AMEND:<amendment no>` (+ `-<n>`) | `TOA-T4-02` |
| Short-close approved | `closeLine`; `cancelScheduleLine` for `FORECAST` / unreleased; header: `closeOrder` — every `reasonCodeId` a `TRADE_ORDER_CLOSE` reason (FR-546) | `PO_CLOSE_LINE`, `PO_CANCEL_SCHEDULE`, `PO_CLOSE` | `…:<op>:<request id>-<line / schedule no>` | `TPO-T4-06` |
| Cancel approved | `cancelOrder` | `PO_CANCEL` | `…:PO_CANCEL:<request id>` | `TPO-T4-06` |
| Auto-close (service principal) | `closeOrder` (`reasonCodeId` = `AUTO_CLOSE`) | `PO_CLOSE` | `…:PO_CLOSE:AUTO` | `TPO-T4-10` |
| Subcontract service confirmed / reversed (FR-686, FR-687) | the core landed-cost apply / its reversal (`CN-14` (c); `WhCostObjectChargePort.applyOutputCharge` / `reverseOutputCharge`, FRD-STORES registry R.2) | `SUBCONTRACT_CHARGE_APPLY` / `SUBCONTRACT_CHARGE_REVERSE` (registry R.2) | `…:SUBCONTRACT_CHARGE_APPLY:<confirmation no>` / `…:SUBCONTRACT_CHARGE_REVERSE:<confirmation no>` | `TPO-T4-14` |
| SO approved | `WhDemandOrderPort.createDemand` | `DEMAND_CREATE` | `WHT_SALES_ORDER:<soId>:DEMAND_CREATE:1` | `TSO-T4-01` |
| Dispatch release approved — whole BLANKET line | `firmScheduleLine(scheduleLineId, releaseRef = release no)` — the optional `releaseRef` re-stamps the firmed line (`CN-9`, R31 F-TR-003) | `DEMAND_FIRM` | `…:DEMAND_FIRM:<release no>-<schedule no>` | `TSO-T4-02` |
| Dispatch release approved — OPEN call-off, BLANKET split, replacement | `releaseSchedule` (`FIRM` entries); a split BLANKET `FORECAST` line reduced by `amendDemand` | `DEMAND_RELEASE` + `DEMAND_AMEND` | `…:DEMAND_RELEASE:<release no>`, `…:DEMAND_AMEND:<release no>` | `TSO-T4-02` |
| Dispatch release cancelled after approval | `unfirmScheduleLine` (whole-firmed lines, allocated 0); `cancelScheduleLine` (added `FIRM` lines) + `amendDemand` restoring a split `FORECAST` | `DEMAND_UNFIRM`, `DEMAND_CANCEL_SCHEDULE`, `DEMAND_AMEND` | `…:<op>:<release no>-X<n>` | `TSO-T4-09` |
| SO amendment applied | `amendDemand` (a ship-to change as `shipToAddressId`, `CN-3`); `cancelLine` / `cancelScheduleLine`; `releaseSchedule` for added schedule lines — `FIRM` entries on a FIXED SO, `FORECAST` on a BLANKET (R31 F-TR-001) | `DEMAND_AMEND`, `DEMAND_CANCEL_LINE`, `DEMAND_CANCEL_SCHEDULE`, `DEMAND_RELEASE` | `…:DEMAND_AMEND:<amendment no>` (+ `-<n>`) | `TOA-T4-02` |
| SO short-close approved | `cancelScheduleLine` per open schedule line with nothing picked; `closeScheduleLineShort` per partly picked / shipped `FIRM` line (`CN-10`, R31 F-TR-005); header: `closeDemand` | `DEMAND_CANCEL_SCHEDULE`, `DEMAND_CLOSE_SCHEDULE_SHORT`, `DEMAND_CLOSE` | `…:<op>:<request id>-<n>` | `TSO-T4-06` |
| SO cancel approved | `cancelDemand` | `DEMAND_CANCEL` | `…:DEMAND_CANCEL:<request id>` | `TSO-T4-06` |
| SO auto-close (service principal) | `closeScheduleLineShort` per tolerated `FIRM` remainder (R31 F-TR-006), then `closeDemand` (`reasonCodeId` = `AUTO_CLOSE`) | `DEMAND_CLOSE_SCHEDULE_SHORT`, `DEMAND_CLOSE` | `…:DEMAND_CLOSE_SCHEDULE_SHORT:AUTO-<schedule no>`, `…:DEMAND_CLOSE:AUTO` | `TSO-T4-10` |
| Lost sale — enquiry / quotation line (FR-680), SO cancel / short-close for stock (FR-681) | `WhLostSalePort.captureLostSale(CaptureLostSaleCommand{ envelope, sourceDocumentType/Id/Ref, warehouseId, ownerId, itemId or itemDescription, requestedQuantity, lostSaleReasonCodeId })` (`CN-11`, `POS-T1-40`, R31 F-TR-011) | `LOST_SALE_CAPTURE` | `WHT_SALES_ENQUIRY:<id>:LOST_SALE_CAPTURE:<line id>`, `WHT_CUSTOMER_QUOTATION:<id>:…:<line id>`, `WHT_SALES_ORDER:<id>:…:<schedule or release line id>-<request id>` | `TSQ-T4-05`, `TSO-T4-13` |
| SRA approved / cancelled | `WhRmaPort.createRma` (`APPROVED`) / `cancelRma` | `RMA_CREATE` / `RMA_CANCEL` | `WHT_SRA:<sraId>:RMA_CREATE:1` / `…:RMA_CANCEL:1` | `TSR-T4-03`, `TSR-T1-04` |
| PR line created from a suggestion / that line cancelled or deleted | `WhReplenishmentSuggestionPort.markConverted` / `releaseConversion` | `SUGGESTION_CONVERT` / `SUGGESTION_RELEASE` | `WHT_PURCHASE_REQUISITION:<prId>:<op>:<line id>` | `TPR-T4-02` |
| Reads | `getReceiptPosition`, `getFulfilmentPosition`, `WhAvailableToPromiseQuery.atp`, `getRmaPosition`, `getSuggestionStatus` | — (read) | — | per contract |

**SPIs trade implements:** `PurchaseOrderChangeGuard`, `DemandOrderChangeGuard`, `RmaChangeGuard` (refusals
per `OD-39`), `SuggestionConversionOwner` (`ownsConversion` true for every suggestion while trade is on) and
`PurchaseRequisitionHandoff` (FR-557). **Events trade consumes** (outbox, matched by `source_document_id`):
`WH_PO_SCHEDULE_LINE_RECEIVED`, `WH_PO_LINE_RECEIVED` (release close, fulfilment refresh), `WH_PO_AMENDED`,
`WH_PO_CLOSED`, `WH_PO_CANCELLED` (reconciliation), `WH_DEMAND_SHIPPED` (release close by `release_ref`),
`WH_DEMAND_AMENDED`, `WH_DEMAND_CANCELLED`, `WH_RMA_MATCHED`, `WH_RMA_EXPIRED`, `WH_RMA_CANCELLED`,
`WH_SUPPLIER_RETURN_DISPATCHED`.

**Grants seeded by trade** (`warehouse:orders:port`; core seeds the verbs it implies): requester and stores
requester bundles (`p9-04`: `markConverted` / `releaseConversion`), buyer and purchase approver (`p9-07`,
`p9-10`, `p9-11`), sales executive (also `p9-08`, the lost-sale port at regret / loss), sales approver and dispatch planner (`p9-09`, `p9-10`, `p9-11`), SRA
approver (`p9-13`). Each of these bundles also gets `:view:branch` on the core resources its calls touch, and the
service principal `warehouse:orders:port` + `:view:all` on `wh_purchase_orders`, `wh_demand_orders`, `wh_rmas`,
`wh_replenishment_suggestions`, `wh_material_requisitions`, `wh_insufficient_stock_log` (`p9-01`; R31 F-SR-004). The auditor and trade
administrator bundles get none.

### 12b. Notifications

Every *Notified* column in the `trade-*` contracts uses the platform notification service (`notifications`,
`NotificationDeliveryListener`, delivered after commit, so a rolled-back transition sends nothing) with **one
category `NotificationCategory.WAREHOUSE_TRADE`** (a platform enum value and its
`NotificationCategoryMenuMapping` row to WS-285 — the two platform commits, owned by `p9-03`, the first trade
notification). v1 sends **in-app only**: e-mail templates (`EmailTemplateDefaults`) are not registered, SMS is a
platform stub. Each kind is a code with an i18n message key, seeded by the task that owns its rule; recipients
are resolved at send time; a digest kind sends one message per recipient per run.

| Kind | Rule | Recipients |
|---|---|---|
| `TRADE_APPROVAL_PENDING` | `TAM-T3-01` | level members + their active delegates |
| `TRADE_APPROVAL_DECIDED` | `TAM-T1-05`/`-07`/`-08` | the document's maker |
| `TRADE_PR_CONVERTED`, `TRADE_PR_CLOSED_SHORT` | `TPR-T4-01`, `TPR-T1-09` | requester |
| `TRADE_PR_AGEING` (digest), `TRADE_PR_OVERDUE` | `TPR-T3-01`, `-02` | buyers of the site; requester |
| `TRADE_RFQ_REMINDER`, `TRADE_RFQ_DUE`, `TRADE_VQ_EXPIRED` | `TRA-T3-01`…`-03` | the RFQ's buyer |
| `TRADE_CONTRACT_EXPIRING`, `TRADE_CONTRACT_CEILING`, `TRADE_CONTRACT_ENDED` | `TRC-T3-01`, `-03`, `-04` | contract owner |
| `TRADE_RELEASE_PROPOSED`, `TRADE_RELEASE_OVERDUE` | `TPO-T3-01`, `-06` | the PO's buyer |
| `TRADE_EXPEDITE_DIGEST`, `TRADE_PO_ACK_OVERDUE`, `TRADE_VALIDITY_ENDING` | `TPO-T3-02`, `-04`, `-05` | the PO's buyer |
| `TRADE_DISPATCH_DUE` (digest), `TRADE_COMMITMENT_AT_RISK` | `TSO-T3-01`, `-02` | dispatch planners of the dispatch site (holders of `wht_so_dispatch_releases:create` scoped to it); the SO's sales executive |
| `TRADE_SO_ACK_NOT_SENT`, `TRADE_SO_VALIDITY_ENDING` | `TSO-T3-04`, `-05` | the SO's sales executive |
| `TRADE_ORDER_CLOSED` | `TPO-T3-03`, `TSO-T3-03` | buyer / sales executive |
| `TRADE_QUOTE_BY`, `TRADE_QUOTATION_EXPIRED`, `TRADE_QUOTATION_FOLLOWUP` | `TSQ-T3-01`…`-03` | sales executive |
| `TRADE_RETURN_OVERDUE` | `TSR-T3-01` | sales executive |
| `TRADE_REPLACEMENT_NEEDS_NEW_PO` | `TPO-T4-07` | the PO's buyer |
| `TRADE_EVALUATION_DRAFTED`, `TRADE_AVL_EXPIRING`, `TRADE_UDYAM_REVIEW`, `TRADE_PART_APPROVAL_EXPIRING` | `TCE-T3-01`…`-04` | trade administrator; sales executive for part approval |
| `TRADE_JOB_PORT_REFUSED` | any job's port refusal (§12a) | trade administrator |

### 12c. Core changes trade asked of STORES — `CN-1`…`CN-7` resolved 2026-10-22; `CN-8` resolved 2026-10-23; `CN-9`…`CN-13` agreed in R31 (2026-10-23); `CN-14` (b), (c) owed by STORES (carrier `p8-09`, `V511324`), (a) by MFG

STORES made `CN-1`…`CN-7` (FRD-STORES *R29 dispositions* → *FRD-TRADE §12c*); the trade rows now call
the registry as it stands. `CN-8` was found by R30 `CP-GB-002` and resolved by STORES (`STO-D25`, `p8-01`)
(R31 F-TR-017, F-SR-012). `CN-9`…`CN-13` are the port changes agreed in the R31 fix wave, defined by STORES in
registry R.2 / `po-schedule-port`; where an operation key below says *proposed*, the registry's name wins (`DEMAND_CLOSE_SCHEDULE_SHORT` and `LOST_SALE_CAPTURE` are the registry's).
`CN-14` is the seam the subcontract service PO (FR-682…FR-689, `D-18` item 3) needs: (b) and (c) are defined in FRD-STORES registry R.2 (`WhCostObjectChargePort`) and R.3 (`CostObjectResolver.receivedOutput`) as owed core changes carried by `p8-09` (`V511324`); (a) and the (b) implementation are MFG's.

| # | Need | Why | Registry row it extends | Resolved (FRD-STORES) |
|---|---|---|---|---|
| CN-1 | `CreatePurchaseOrderCommand.lines[]` gains `overTolerancePct`, `underTolerancePct` and `receivingLocationId` | FR-582 passes tolerances to core's over-receipt guard; FR-576 deliver-to location; today only `amendOrder` carries `receivingLocationId` | `WhPurchaseOrderPort.createOrder` | **Resolved** — FR-504; registry R.2 `createOrder`; `POS-T1-05`, `-14`, `POS-GRD-15`; p8-01 (`V511310`) |
| CN-2 | `AmendPurchaseOrderCommand` gains `newScheduleLines[]` (`poLineId`, `kind`, `scheduledDate`, `quantity`, `unitPrice?`, `releaseRef`) validated together with `lineChanges` | a FIXED line keeps Σ schedule = ordered (`POS-GRD-02`), so a quantity increase or a supplier-return reinstatement on a FIXED line cannot be made by two separate calls | `amendOrder` | **Resolved** — FR-504; registry R.2 `amendOrder`; `POS-T1-07`, `POS-GRD-02`; p8-01 |
| CN-3 | `CreateDemandCommand` and `AmendDemandCommand` carry `shipToAddressId` | the SO ship-to (FR-605) and its amendment (FR-590) must reach core shipping | `createDemand`, `amendDemand` | **Resolved** — FR-505; registry R.2; `POS-T1-10`, `-12`, `POS-GRD-16`; p8-02 (`V511311`) |
| CN-4 | State that a demand line created with no schedule (an `OPEN` SO line) is `is_schedule_driven` | `POS-T1-10` saves it with `ordered_quantity = 0`, which the `POS-GRD-10` CHECK admits only for a schedule-driven line | `POS-T1-10`, `POS-GRD-10` | **Resolved** — FR-505; registry R.2; `POS-T1-10`, `POS-GRD-10`; p8-02 |
| CN-5 | `POS-T3-01`'s weekly overdue digest skips POs whose `source_module` is set | trade's `TPO-T3-02` already tells the buyer; core would send a second digest to the port's acting user | `POS-T3-01` | **Resolved** — FR-504; `POS-T3-01`; p8-01 |
| CN-6 *(recommended → adopted)* | `WhPurchaseOrderPort.unfirmScheduleLine` and an optional `unitPrice` on the `firm` entry | mirror of the demand port: a cancelled BLANKET release could return its line to `FORECAST` instead of cancel + re-add, and an `AT_RELEASE` whole-line release could firm in place | `releaseSchedule` | **Resolved** — `STO-D19`; registry R.2 `unfirmScheduleLine`, `firm(…, unitPrice?)`; `POS-T1-03`, `-03a`; p8-01 |
| CN-7 *(recommended → adopted)* | a service principal for a sibling's scheduled jobs | `TRD-13` uses the order's buyer for auto-close; registry R.1 knows only acting users | R.1 *Principal* | **Resolved** — `STO-D20`; registry R.1 *Principal*; p8-01 |
| CN-8 | `AmendPurchaseOrderCommand.lineChanges[]` gains `overTolerancePct?`, `underTolerancePct?`, validated as on create (`POS-GRD-15`) | a trade amendment of change type `TOLERANCE` (`trade-order-amendment` §0) otherwise stays trade-side and core's over-receipt guard keeps the create-time value (FR-582, FR-590). The SO mirror needs nothing: a core demand line has no tolerance and trade reads its own (`TSO-T3-03`) | `amendOrder` | **Resolved 2026-10-23** — STORES `STO-D25`, port registry R.2 (`FRD-STORES.md`), `POS-T1-07` / `POS-GRD-15`; carrier `p8-01`; trade side `TOA-T4-02`, `TOA-GRD-11`, `p9-11` (R30 `CP-GB-002`). **Band (R31 F-SR-013):** the amended band is `effective × (1 + T_new) + Σ excess_approved`, so approved excess never reads as a breach; an amendment that would leave received quantity outside it is refused `409 TOLERANCE_BELOW_RECEIVED`, which trade pre-checks at submit and re-checks at apply (`TOA-GRD-11`) |
| CN-9 | `firmScheduleLine(…, releaseRef)`: an optional `releaseRef` re-stamps the firmed core demand line | a whole BLANKET dispatch release firms a line created with `<so>-S<n>`; without the re-stamp no core line carries the release number, so the release and the SO never close (R31 F-TR-003) | `WhDemandOrderPort.firmScheduleLine` | **Agreed R31** — registry R.2; trade side `TSO-T4-02`, `TSO-T1-12`, FR-607; `p9-09` |
| CN-10 | `closeScheduleLineShort(scheduleLineId, reasonCodeId)`: closes the unpicked remainder of a partly picked / shipped demand schedule line, releases its reservation, writes `cancelled_quantity`, emits an event | `cancelScheduleLine` refuses a line with picked > 0 (`POS-T1-11c`, `409 DEMAND_SCHEDULE_PICKED`), so a backordered `FIRM` line could not be short-closed, and auto-close left a tolerated remainder live (R31 F-TR-005, F-TR-006) | `WhDemandOrderPort` | **Agreed R31** — registry R.2 (STORES F-SR-003); trade side `TSO-T1-13a`, `TSO-T4-06`, `TSO-T4-10`, FR-609; `p9-10` |
| CN-11 | `WhLostSalePort.captureLostSale(PortEnvelope, …)`: the lost-sale capture as a registered port with an operation key | trade called the core service `WhInsufficientStockLogService.captureLostSale` (`:146`), which is outside the registry and takes no envelope or key (R31 F-TR-011) | new port | **Agreed R31** — registry R.2; trade side `TSQ-T4-05`, `TSO-T4-13`, FR-680, FR-681; `p9-08`, `p9-09`, `p9-10` |
| CN-12 | `amendOrder` `scheduleChanges.quantity` may reduce a partly received `FIRM` line down to (never below) its received quantity | `unfirmScheduleLine` and `cancelScheduleLine` both need 0 received, so the unreceived part of a partly received release had no path (R31 F-TR-004) | `amendOrder` | **Agreed R31** — registry R.2 (floor = received); trade side `TPO-T1-10c`, `TPO-T4-09`, FR-580; `p9-07` |
| CN-13 | Port principals need core site scope: service principals `:view:all`, user bundles `:view:branch`, on `wh_purchase_orders`, `wh_demand_orders`, `wh_rmas`, `wh_replenishment_suggestions`, `wh_material_requisitions`, `wh_insufficient_stock_log` | core checks site scope before validating (`WhPurchaseOrderService.java:244-245`); `warehouse:orders:port` alone resolves scope `NONE` (R31 F-SR-004) | registry R.1 *Principal* | **Agreed R31** — STORES states the rule (R.1); trade seeds it (`p9-01`, each bundle's task); FR-617, `TRD-13` |
| CN-14 | (a) `CostObjectResolver.resolve` for `PRODUCTION_ORDER` returns the order's **kind** and **job-worker counterparty**; (b) a read of the **received output** of a cost object × item — the receiving lots / cost layers and base quantity its receipts created (an MFG-implemented default method, like `reservationsFor`); (c) a **value-only landed-cost apply** (and its reversal) onto those lots, posted by core as one `LANDED_COST_APPLY`, from a source module with a `PortEnvelope` | the subcontract charge lands on the processed item (`D-18` item 3, MFG `SUB-OPEN-06`); core's landed cost allocates only to GRN lines (`wh_landed_cost_allocations.grn_line_id NOT NULL`, `V510080:151`) and the processed item arrives by MFG production receipt, not a GRN; trade may not read `whm_` | `CostObjectResolver` (R.3), core landed cost (`V510080`) | **Owed** — STORES (b), (c) defined in registry R.2 `WhCostObjectChargePort` / R.3, carrier `p8-09` (`V511324`); MFG (a), (b) implementation; trade side FR-683, FR-685…FR-687, `TPO-T1-17`…`-19`, `TPO-T4-13`, `-14`; `p9-07` |

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
| FR-615–619 | every contract §5; WS-312 reports `trade-reports` | p9-14 (print + reports); FR-616–618 in every task |
| FR-680 | `trade-sales-enquiry-quotation` `TSQ-T4-05` | p9-08 |
| FR-681 | `trade-sales-order` `TSO-T4-13` | p9-09 (short-close half p9-10) |
| FR-682–689 | `trade-purchase-order` §1.5 (`TPO-T1-17`…`-19`, `TPO-GRD-17`…`-20`, `TPO-T4-13`, `-14`) | p9-07 |

## R29 dispositions

R29 trade-purchase (`TP-`) and trade-sales (`TS-`) functional reviews, folded 2026-10-22. Trade references
are aligned to FRD-STORES *"R29 dispositions"* and *"Port & seam registry (authoritative)"*; the core halves
were fixed by STORES. The core changes trade asked for, §12c `CN-1`…`CN-7`, were made by STORES on 2026-10-22
(`STO-D19`, `STO-D20`); nothing is owed.

### Purchase review

| Finding | Change | Where |
|---|---|---|
| TP-F1 | BLANKET creates its core PO with all-`FORECAST` schedule lines (registry schedule-driven line); FIXED needs no release (`TRD-12`) | TPO-T4-01; §4 FR-575; p9-07 |
| TP-F2 | Rejected CS terminal with RFQ back to `BIDS_CLOSED`; returned CS → `DRAFT`; RFQ cancel from `BIDS_CLOSED`/`EVALUATION` | TRA-T1-13, -14; p9-05; WH-SC-566 |
| TP-F3 | Vendor quotation revisable from `EXPIRED` | TRA-T1-08, T3-03; p9-05 |
| TP-F4 | Release ladder: reject-revert, cancel before / after approval, close on core events | TPO-T1-10a…-10c, -12, T4-09, -11; p9-07 |
| TP-F5 | PR header closes when every line is closed short or cancelled, allocation or not | TPR-T1-09, -10; p9-04 |
| TP-F6 | Port principal = triggering person; a scheduled job calls as trade's service principal (`CN-7` → `STO-D20`); `warehouse:orders:port` granted per task bundle and to the service principal | TRD-13; §12a; every contract §0; p9-01/04/07/09/10/11/13; epic |
| TP-F7 | OPEN PO without ceiling value carries `open_unbounded`; release with it needs an install rule | FR-575, FR-580; TPO-T1-08 (the release carries `open_unbounded`; R30 `CP-FR-015` corrected the pointer from `TPO-GRD-07`); p9-07; WH-SC-567 |
| TP-F8 | Delegation for another approver needs a second administrator's confirmation | TAM-T1-10, -11, GRD-07; p9-03; WH-SC-569 |
| TP-F9 | Maker ≠ checker checked for actor and principal, own name or delegate | TAM-GRD-03; FR-549; p9-03 |
| TP-F10 | Every AVL entry / change is an `AVL` approval request held in `pending_change` | TCE-T1-04; FR-544; p9-02; WH-SC-570 |
| TP-F11 | `:approve` verb on both profile resources; approve-verb map | TCE §0; TAM §0.1; p9-02, p9-03; WH-SC-595 |
| TP-F12 | Ambiguity guard covers rules on different dimensions that could match one document; tie at open refused | TAM-GRD-05, -08; p9-03; WH-SC-495 |
| TP-F13 | Core hand-off row: PR created `SUBMITTED`, number issued and returned, key `MRQ_HANDOFF:<id>` | TPR-T1-02a; FR-557; p9-04 |
| TP-F14 | `AT_RELEASE` price reaches core on release: `firm(…, unitPrice)` for a whole BLANKET line, `add(…, unitPrice)` otherwise (`CN-6` → `STO-D19`, resolved) | TPO-T4-02; §12c CN-1, CN-6; p9-07; WH-SC-571 |
| TP-F15 | `receipt_cutoff_date` passed to core; core refuses receipts after it | TPO-GRD-16; FR-578; p9-07; WH-SC-572 |
| TP-F16 | One comparative statement per RFQ × currency | TRA §0, GRD-10; p9-05; WH-SC-573 |
| TP-F17 | Release guards complete at submit and re-checked under the header lock at approval | TPO-GRD-06…-08, -15; p9-07 |
| TP-F18 | Cancel / delete / close-short of a converted PR line calls `releaseConversion` | TPR-T4-02; p9-04; WH-SC-574 |
| TP-F19 | Free-of-charge never on an OPEN line | TPO-GRD-03; TSO-GRD-03 |
| TP-F20 | Shared amendment engine for PRC / SRC / PL incl. dated termination and supersession | TRC-T1-05…-09, T3-04; TRD-15; p9-06; WH-SC-575 |
| TP-F21 | Cancel after approval is a `PO_CANCEL` approval request (seeded zero-level) | TPO-T1-05, -05a; FR-583; p9-03, p9-07; WH-SC-576 |
| TP-F22 | Auto-close calls `closeOrder`; holds on QC, undispatched return and pending replacement | TPO-T3-03, T4-10; p9-10; WH-SC-577 |
| TP-F23 | Supplier-return reinstatement is a system amendment of origin `SUPPLIER_RETURN` | TOA-T1-01, -05, GRD-09; TPO-T4-07; p9-11, p9-13; WH-SC-578 |
| TP-F24 | Deliver-to / ship-to change reaches core: PO `DELIVER_TO` as `amendOrder` `lineChanges.receivingLocationId`, SO `SHIP_TO` as `amendDemand` `shipToAddressId` (`CN-3` resolved) | §12c CN-1, CN-3; TOA-T4-02; p9-11 |
| TP-F25 | OPEN-PO and rate-contract award targets release the PR allocation (they hold no quantity); the buyer allocates to releases later | TRA-T4-03, -04; p9-05 |
| TP-F26 | One notification category `WAREHOUSE_TRADE`, in-app; kinds per rule | §12b; every T3 row; p9-03 |
| TP-F27 | Expediting covers FIXED lines; unreleased past-due BLANKET → release overdue, excluded from OTIF | TPO-T3-02, -06; TCE metric catalogue; p9-07, p9-12; WH-SC-579 |
| TP-F28 | Screen contracts completed (grids, scopes, tiles, filters, actions) | every contract §5; p9-02…p9-14 |
| TP-F29 | PR line `IN_RFQ` in the state inventory | TPR §1.1; p9-04 |
| TP-F30 | Single `whb_source_systems` owner `V551000`; `btree_gist` and port beans asserted | §8; p9-01, p9-02 |

### Sales review

| Finding | Change | Where |
|---|---|---|
| TS-F1 | BLANKET / OPEN SO lines are schedule-driven; an OPEN line sent with no schedule and a null quantity is schedule-driven in core (`CN-4` resolved) | TSO-T4-01; §12c CN-4; p9-09 |
| TS-F2 | `OD-45` (A): one demand order per SO, header back to `OPEN` after each despatch, `closeDemand` ends it | OD-32; TSO-T4-10; p9-09, p9-10; WH-SC-580 |
| TS-F3 | SRA maps every core RMA status; received / partially received closable | TSR §1, T1-05, -07, -08, T4-01; p9-13; WH-SC-581 |
| TS-F4 | Expired latest quotation winnable (PO-date evidence), losable, revisable | TSQ-T1-08…-10, GRD-05; p9-08; WH-SC-582 |
| TS-F5 | Per-line outcomes on enquiry and quotation lines | TSQ §0, T1-09; p9-08; WH-SC-583 |
| TS-F6 | One ack target: `ISSUED` + `ack_status` | TSO-T1-06; FR-606; p9-10 |
| TS-F7 | Dispatch release `CLOSED` on core events; `DRAFT` release cancellable | TSO-T1-10b, -12, T4-11; p9-09 |
| TS-F8 | Zero-level seeds match `EXACT` (empty condition set) | TAM-GRD-01; TRD-14; FR-550; p9-03; WH-SC-585 |
| TS-F9 | As TP-F12 | TAM-GRD-05, -08; p9-03 |
| TS-F10 | Amendment resets `ack_status`; *Re-send acknowledgement* | TSO-T1-11; TOA-T4-03; p9-10; WH-SC-584 |
| TS-F11 | ATP from core `WhAvailableToPromiseQuery.atp` | TSO-T4-12; p9-09; WH-SC-586 |
| TS-F12 | Withdraw on every sales document screen | TSO / TSQ / TSR §5; p9-08, p9-09, p9-13 |
| TS-F13 | Each consuming task seeds a minimal template; p9-14 supersedes | FR-615; p9-02, -04, -05, -07, -08, -10, -13, -14 |
| TS-F14 | FIXED SO needs no release; schedule `FIRM` at approval | TRD-12; FR-605; TSO-T4-01; p9-09; WH-SC-596 |
| TS-F15 | `firmScheduleLine` / `unfirmScheduleLine` used per registry | TSO-T4-02, -09; p9-09 |
| TS-F16 | Replacement release exempt from block / validity guards; approved through `SO_RELEASE` | TSO-T1-16, GRD-08; TSR-T4-02; p9-13; WH-SC-587 |
| TS-F17 | `SO_RELEASE` approval; ceiling consumption on release | FR-548; TSO-T1-10, GRD-07; p9-09; WH-SC-588 |
| TS-F18 | TSO-GRD-05, -10, -11 written as twins | TSO §1.3 |
| TS-F19 | Amendment lock only on the schedule lines it changes; newer import replaces a draft | TOA-GRD-04, -10; p9-11; WH-SC-589 |
| TS-F20 | SO cancel / short-close port effects; `COMPLETE` within under-tolerance | TSO-T4-06, T3-03; p9-10 |
| TS-F21 | Core RMA created `APPROVED` with approver; `RmaChangeGuard` allows `EXPIRE` | TSR-T4-03, GRD-05; OD-39; p9-13 |
| TS-F22 | Price-list priority; equal-priority overlap refused | TRC-GRD-05, T4-04; p9-06; WH-SC-590 |
| TS-F23 | Termination / supersession dated; prices end on the date | TRD-15; TRC-T3-04; p9-06 |
| TS-F24 | No FX: money tiles and reports grouped by currency | FR-616, FR-619; p9-14; WH-SC-591 |
| TS-F25 | Demand and RMA port rows written to registry names | TSO-T4-01, -02, -06, -09, -10; TSR-T4-01, -03 (R30 `CP-FR-015`: the wildcards resolved); §12a |
| TS-F26 | Quotation charges specified (fields, screen, carried to SO) | TSQ §0, §5; p9-08 |
| TS-F27 | Refused: a dispatch release has no print (written refusal) | §5 M32; FR-615 |
| TS-F28 | Releases / amendments `<order>-Rnn` / `-Dnn` / `-Ann`; release and amendment series removed | FR-547; p9-02 |
| TS-F29 | Customer-rating scenario; `warehouse.trade.sales.firm_zone_days` named | TCE metric catalogue; p9-12; epic; WH-SC-592 |

### Mirror asymmetries

| Row | Change | Where |
|---|---|---|
| MA-01 | `SO_RELEASE` approval twin | TSO-T1-10; FR-548; p9-09 |
| MA-02 | PO release cancel rows | TPO-T1-10b, -10c |
| MA-03 | Sales ack ladder, `ack_status`, re-send | TSO-T1-06, -11; p9-10 |
| MA-04 | TSO T2 written row for row against TPO T2 | TSO §2 |
| MA-05 | TSO-GRD-05, -10, -11 | TSO §1.3 |
| MA-06 | Line tolerances; `COMPLETE` defined | TSO §0, T3-03; p9-10 |
| MA-07 | Ceiling consumption on SO release | TSO-GRD-07; p9-09 |
| MA-08 | WS-313 Dispatch Releases; WS-305 / WS-306 grid ids, scopes, exports | §6; TSO §5.3–5.5; p9-09 |
| MA-09 | SO cancel / short-close T4 | TSO-T4-06 |
| MA-10 | Ack-not-sent alert | TSO-T3-04; p9-10; WH-SC-594 |
| MA-11 | **Refused** — no dispatch-release print; the SO acknowledgement and core despatch documents serve | §5 M32 |
| MA-12 | Sales-rating and sales self-approval scenarios | WH-SC-592, WH-SC-593 |
| MA-13 | Dispatch adherence report | FR-619; p9-14 |
| MA-14 | Demand-port rows to PO-port depth | TSO-T4-01, -02, -06, -09…-12 |
| MA-15 | Withdraw on sales screens | TSO-T1-03; TSQ / TSR §5 |
| MA-16 | Quotation charges to vendor-quotation depth | TSQ §0 |
| MA-17 | FIXED needs no release on either side | TRD-12 |
| MA-18 | Partial conversion on sales via per-line outcomes | TSQ-T1-09; M6 |

## R31 dispositions

R31 second dual-engine functional review (`reviews/R31-functional-review-trade.md`, 23 findings) and the trade
rows of `reviews/R31-decisions.md`, folded 2026-10-23. Core port names are the ones agreed with STORES (§12c
`CN-9`…`CN-13`); user decisions are `D-18`.

| Finding | Change | Where |
|---|---|---|
| F-TR-001 | FIXED SO amendment adds schedule lines as `FIRM`, BLANKET as `FORECAST` | `TOA-T4-02`; §12a; p9-11 |
| F-TR-002 | Replacement release exempt from type, validity and schedule gates; `REPLACE` needs an open SO, else a new SO (`TRADE_REPLACE_NEEDS_OPEN_SO`) | FR-612; `TSO-GRD-06`, `-T1-16`, `-T2-06`; `TSR-GRD-03`; p9-09, p9-13 |
| F-TR-003 | `firmScheduleLine(…, releaseRef)` re-stamps the firmed line (`CN-9`) | FR-607; `TSO-T4-02`, `-T1-12`; §12a; p9-09 |
| F-TR-004 | Partly received release line reduced to received by `amendOrder` (`CN-12`); T1-10c aligned with T4-09 | FR-580; `TPO-T1-10c`, `-T4-09`; §12a; p9-07 |
| F-TR-005 | `closeScheduleLineShort` for a partly picked / shipped `FIRM` line (`CN-10`) | FR-609; `TSO-T1-13a`, `-T4-06`; §12a; p9-10 |
| F-TR-006 | Auto-close closes tolerated `FIRM` remainders before `closeDemand` | FR-609; `TSO-T3-03`, `-T4-10`; p9-10 |
| F-TR-007 | Port-bound reasons are `whb_reason_codes` (`TRADE_ORDER_CLOSE`, `RETURN`); SRA header reason | FR-546; §1; TPO / TSO / TSR rows; p9-02, p9-08, p9-13 |
| F-TR-008 | Lost-sale trigger without release cancel; OPEN call-offs on the release line; `TRD-13` principal | FR-681; `TSO-T4-13`, `-UNR-08`; p9-09, p9-10 |
| F-TR-009 | Quotation `dispatch_warehouse_id` | FR-599; §8; TSQ §0, `TSQ-T4-05`; p9-08 |
| F-TR-010 | A not-catalogued enquiry line can be regretted | FR-598; TSQ §0, `TSQ-GRD-04`; p9-08 |
| F-TR-011 | Lost sale through `WhLostSalePort.captureLostSale` (`CN-11`) | FR-680, FR-681; §12a; `TSQ-T4-05`, `TSO-T4-13`; p9-08, p9-09 |
| F-TR-012 | Auto-close jobs call as the service principal | `TPO-T3-03`, `-T4-10`; `TSO-T3-03`, `-T4-10`; p9-10 |
| F-TR-013 | `AVL` / `PROFILE_BLOCK` requests: value 0, company currency | FR-550; `TAM-GRD-01`; p9-03 |
| F-TR-014 | Rejected / cancelled release lines release their PR allocation | FR-580; `TPO-T1-10a`…`-10c`; `TPR-T4-03`; p9-04, p9-07 |
| F-TR-015 | SRA allowance counts live authorisations + matched only | FR-612; `TSR-GRD-01`; p9-13 |
| F-TR-016 | `TOLERANCE` amendment pre-checked at submit and apply | §12c `CN-8`; `TOA-GRD-11`; p9-11 |
| F-TR-017 | `CN-8` no longer reads as open | §12c heading; p9-11 |
| F-TR-018 | RFQ cancel permission states = transition states | `TRA-T2-03` |
| F-TR-019 | Every T2 row and the reports T2 table carry a Source FR; `TPO-T4-12`, `TPR-UNR-05` cite FRs | every `trade-*` contract §2 |
| F-TR-020 | `WhReplenishmentSuggestionPort` optional | FR-540; `TPR-GRD-07` |
| F-TR-021 | Epic lists 11 contracts and the lost-sale setting; §8 lists the lost-sale columns | `11-EPIC-p9`; §8 |
| F-TR-022 | §1 seed exception list complete | §1 |
| F-TR-023 | The due date never closes bids; `NO_RESPONSE` at close | TRA §1.1, `TRA-T3-02` |
| F-SR-004 | Port principals' site scope (`CN-13`) | FR-617; `TRD-13`; §12a; p9-01 |
| F-SR-012 | `CN-8` recorded as resolved | §12c; p9-11 |
| F-SR-013 | `CN-8` band with approved excess; `409 TOLERANCE_BELOW_RECEIVED` handled | §12c `CN-8`; `TOA-GRD-11`; p9-11 |
| `D-18` item 3 | R9 lifted for the subcontract service PO; R8 stays | §4.6a FR-682…FR-689; §11 R9; §12c `CN-14`; TPO §1.5; p9-07 |
| R31 decisions | `TCE-OPEN-01`, `TCE-OPEN-02`, `TPO-OPEN-02`, `TPR-OPEN-02`, `TPR-OPEN-03`, `TRA-OPEN-01` settled; `SUB-OPEN-06` owned by trade (FR-686) | the open rows of each contract; OD-30 |
