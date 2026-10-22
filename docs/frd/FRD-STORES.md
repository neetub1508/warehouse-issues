# FRD-STORES — manufacturing stores capability in core `warehouse`

**Area** STORES · **Phase** `P8` · **Modules** `warehouse` (documents, `wh_`) with seed rows in `warehouse-base`
(`whb_`) · **Ids** `FR-500`…`FR-539`, `WS-260`…`WS-277`, `WH-SC-420`…`WH-SC-479`, `OD-25`…`OD-29` ·
**Decision record** `DECISIONS.md` `D-16` (`RN-050`…`RN-054`) · **Status** v0, derived 2026-10-22, not ratified

> **Source requirement.** The client's purchase-to-stores flow ([`reviews/R27`](../reviews/R27-client-p2p-stores-gap.md)
> §1, steps 1–12) and the core stores placement of [`reviews/R28`](../reviews/R28-manufacturing-storage-retarget-impact.md)
> §8b `RN-053`. R28 §4 group B (`B1`…`B8`) and the procurement schema rows of group A (`A3`) and group D
> (`D1`, `D3`) are owned here; everything else in group A goes to `FRD-TRADE.md`, group C to `FRD-MFG.md`.
>
> **Precedence.** `DECISIONS.md` wins on module names, bands and prefixes; `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md`
> (the main FRD) wins on every requirement this file does not amend. This file **amends** `FR-139` (§6.4) and
> **resolves** `S-052` per `RN-034` (§6.7). It runs **after `P7`**: every table named below is the post-`P7`
> schema (dealer/retail columns gone, `WORKSHOP` renamed to production store, `VOR` renamed to line-stop).
>
> **v0 renumbering note (2026-10-22, before any external citation).** The first draft's `FR-506` (customer
> delivery schedule) is folded into `FR-505` and its `FR-534` (cost-centre master) into `FR-533`; the two
> freed ids now carry the RMA port (`FR-506`, TRADE `OD-33`) and stores performance (`FR-534`, replacing the
> withdrawn `FR-422`). The range `FR-500`…`FR-539` stays contiguous and full.
>
> **Accounting is deferred (`RN-054`).** No row here creates a debit note, a credit note, a journal or a
> valuation posting. Where the client flow says *"debit note"* or *"credit note"*, this file stops at a
> **handover point**: a claim, a reconciliation case or an outbox event carrying the quantity and value an
> accounting module will later read. The handover points are listed in §8.

---

## 1. What this area builds

A manufacturing plant's stores run one loop every day, and this area closes every gap R27 found in it:

```
              ┌──────────── warehouse-trade (P9): PR → RFQ → award → rate contract → PO create/release ─┐
              │                                                                                          ▼
 GATE ENTRY ──► RECEIVING SESSION ──► GRN (bill no/date, billed vs received) ──► INCOMING QC (sampling) ──► MRN (authorised) ──► STORE
 (inward,        (unload, seals)       short → claim · excess → accept/refuse       accept · reject → supplier    putaway, AVAILABLE
  PO/ASN/bill,                                                                     return (manual)
  weighment)
                                                                                                                     │
 DEPARTMENT / PRODUCTION ──► MATERIAL REQUISITION ──approve──► STORE ISSUE (to VIRT-CONSUMED, cost object on lines) ◄┘
                              │ shortfall → back-to-back PR hand-off (warehouse-trade)     │
                              ▼                                                            ▼
                                                                     STORE RETURN (linked to the issue line, partial, condition/QC)
 GATE PASS (outward): returnable / non-returnable, return tracking, overdue
```

Plus the two **schema ports** that the siblings consume and that only core may own, because the tables are
core's: the **purchase-order type and schedule-line schema with its creation/release port** (consumed by
`warehouse-trade` purchasing) and the **demand-order creation/release port with a customer delivery schedule**
(consumed by `warehouse-trade` sales), and the **polymorphic QC source** consumed by `warehouse-manufacturing`
for in-process and final inspection.

## 2. Reference process catalogue (RM-040) — stores rows

Scored against standard manufacturing-stores practice (Indian plant stores; SAP MM/QM, Oracle Receiving,
Tally Prime, Odoo; sources in §11). Every row is **covered here**, **assigned** to a named owner that exists or
is scheduled, or **refused** in §10 (`RM-043`).

| # | Catalogue row (standard practice) | R27 | Disposition | Where |
|---|---|---|---|---|
| CAT-01 | Purchase requisition / indent from a department | `RM-001` | assigned | `FRD-TRADE` (P9); core supplies the requisition hand-off `FR-528` |
| CAT-02 | RFQ, quotation, comparison, award | `RM-002` | assigned | `FRD-TRADE` |
| CAT-03 | PO types — fixed, open (rate only), blanket release with delivery schedule | `RM-003`–`005` | **here** | `FR-500`–`FR-504` |
| CAT-04 | Agreed / contract rate | `RM-006` | assigned | `FRD-TRADE` (rate contract, `RN-030`); core line carries the rate and its source ref `FR-501` |
| CAT-05 | Inward gate entry with party, PO, bill no/date, vehicle, weighment | `RM-007` | **here** | `FR-507`–`FR-511` |
| CAT-06 | Outward gate pass — returnable (RGP) / non-returnable (NRGP), return tracking, overdue | — | **here** | `FR-512`–`FR-515` |
| CAT-07 | Goods receipt against the supplier bill: billed vs received vs accepted | `RM-008` | **here** | `FR-516`–`FR-518` |
| CAT-08 | Short receipt → supplier claim (debit note deferred) | `RM-009` | **here** | `FR-519` |
| CAT-09 | Excess receipt → accept within approved excess, or refuse | `RM-010` | **here** | `FR-520` |
| CAT-10 | Incoming inspection with lot-size sampling (IS 2500-1 / ISO 2859-1 / ANSI Z1.4; user band table; fixed; percentage) | `RM-011` | **here** | `FR-521`–`FR-524` |
| CAT-11 | QC on production receipts, in-process and final (inspection-lot origin other than PO) | — | **here** (source) / MFG (documents) | `FR-525` |
| CAT-12 | QC reject → return to supplier (manual) | `RM-012` | **here** | `FR-526` (amends `FR-139`) |
| CAT-13 | MRN — material receipt note authorised into stores, printed | `RM-013` | **here** | `FR-527`, `FR-538` |
| CAT-14 | Store / location / custodian | `RM-014` | covered | `FR-079`…`FR-088` (main FRD) |
| CAT-15 | Material requisition from department / cost centre / production order with approval, partial issue, closure | `RM-015` | **here** | `FR-529`–`FR-532` |
| CAT-16 | Back-to-back purchase requisition for a shortfall | — | **here** (hand-off) / TRADE (PR) | `FR-532` |
| CAT-17 | Store issue to consumption with a cost object | `RM-016`, `S-052` | **here** | `FR-533`–`FR-535` |
| CAT-18 | Store return of unused material, partial, condition / QC | `RM-017` | **here** | `FR-536`–`FR-537` |
| CAT-19 | Issue to production / backflush / FG receipt | — | assigned | `FRD-MFG` (P10) through the store-issue cost object `PRODUCTION_ORDER` and the QC source |
| CAT-20 | Job work out/in (ITC-04 challan) | — | covered | `warehouse-india` `P4-02`; the gate pass links the challan `FR-513` |
| CAT-21 | Sales order → demand → dispatch, customer delivery schedule | — | **here** (port) / TRADE (SO) | `FR-505` |
| CAT-21a | Sales return authorisation → RMA; supplier return for replacement | — | **here** (port, intent) / TRADE (SRA, reinstatement) | `FR-506` |
| CAT-22 | Supplier rating from receipt and QC facts | — | assigned | `FRD-TRADE` (vendor rating `A7`) reading `P6-05`'s receipt facts |
| CAT-23 | Printed stores documents (gate entry slip, gate pass, GRN, MRN, requisition, issue slip, return note) | `RM-013` | **here** | `FR-538` |
| CAT-24 | Stores registers: gate register, RGP pending, requisition pending, issue register by cost object, consumption by department | — | **here** | `FR-539` |
| CAT-26 | Stores performance: gate-to-GRN, GRN-to-MRN, QC lead time, issue turnaround, return cycle, dock-to-stock | — | **here** | `FR-534` |
| CAT-25 | Debit / credit note, GRNI, supplier bill booking | `RM-030`–`032` | refused here (deferred) | §10 row 1 |

## 3. Personas (adds to main FRD §4, `RN-036`)

| Actor | Is | Notes |
|---|---|---|
| **Gate security** | a person | Records gate entries and gate-outs; never receives, never inspects. Permission `wh_gate_entries:create` / `:close`, `wh_gate_passes:gate_out` / `:record_return` only |
| **Stores receiving clerk** | a person | Gate-in to receiving session, GRN with bill fields, prepares the MRN (maker) |
| **QC inspector** | a person | Incoming inspection, sampling results, disposition; raises the supplier return (maker) |
| **Stores in-charge / MRN authoriser** | a person | Authorises the MRN (checker), approves gate passes, approves accept-excess |
| **Department requester** | a person | Raises material requisitions and store returns for a department or cost centre; sees only own department's documents |
| **Department head / requisition approver** | a person | Approves requisitions of the departments they head; may not approve their own |
| **Stores issue clerk** | a person | Picks and posts store issues against approved requisitions; posts store returns |
| **Production planner** | a person (MFG) | Raises requisitions against a production order through MFG; reads requisition and issue status |
| **Buyer** | a person (TRADE) | Owns POs created through the port; receives the back-to-back PR hand-off |

Maker ≠ checker everywhere a row says *approve* or *authorise*: a **service check against the stored actor**
(`FR-408`, `P2-23`), refused `403 APPROVER_IS_ACTOR`, never a UI gate.

## 4. Deployment rules

- Every row is `module = app` (core `warehouse`) unless marked `base`. No row needs `warehouse-trade` or
  `warehouse-manufacturing` to be installed; where a sibling extends a flow it does so through a port or a
  bean collection that is **empty when the sibling is off** (`D-16` item 5, the `WarehouseBranchLinkValidator`
  pattern in `classic/warehouse-base/.../whbwarehouse/WarehouseBranchLinkValidator.java`).
- No `wh_`/`whb_` table gains an FK to a `wht_`/`whm_` table. A reference upward is `(source_module,
  source_document_type, source_document_id, source_document_ref)` with no FK, validated by a resolver bean.
- Every new vocabulary is a `whb_code_list_values` row (`V500010` pattern, composite FK `(…_list, code)`), never
  a CHECK (`D-10`). Closed lifecycle columns carry no CHECK either (BUILD-SPEC §0.11); the service is the gate.
- Every new document that posts a movement registers its `whb_document_types` row (the FK behind
  `whb_stock_movements.source_document_type`, `V500030:213-217`; `source_document_id` is `VARCHAR(100)`).
  The owning-module guard copies the `RL-003` pattern now living at
  `warehouse-adapter-example/.../V525000__…sql:99-122` (the `V521000:117` original was deleted with the
  services adapter in `64d1fe74d5`).
- Every new document number is a gapless site series seeded per OPERATOR site in the `CLM`/`SR` shape
  (`'<CODE>-'`, pad 6, `YEARLY`): `GE`, `GP`, `MRN`, `MRQ`, `SIS`, `SRN`. (The `PO`, `GRN`, `RCV`, `QCINSP`
  series are configured on the number-series screen, not seeded — unchanged.)
- No mobile (`D-16` item 7).

## 5. Ver / phase

Every row below is **`v1.1 · P8`** unless the row says otherwise. `P8` depends on `P7` (removal and the one
rebuild, `RN-052`); `P9` and `P10` depend on `P8-01`, `P8-02`, `P8-06`, `P8-09`, `P8-10`.

## 6. Requirement catalogue

### 6.1 Purchase-order type, schedule lines and the creation/release port (`A3`; `RM-003`…`RM-005`)

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-500** | A purchase order has a **type**: `FIXED` (quantity and rate fixed per line — today's PO), `OPEN` (rate fixed per line, **no ordered quantity**; quantity exists only on released schedule lines) or `BLANKET_RELEASE` (a release against a blanket agreement held by the buying module; every line carries an agreement reference and its quantity is the sum of its schedule lines). The type is fixed at create and never changes. Stored `wh_purchase_orders.po_type`, closed set, service-whitelisted, no CHECK | app | v1.1 | P8 | `RM-003` `RM-004` `RM-005` `RN-053` |
| **FR-501** | A PO line carries a **rate source**: `MANUAL` (typed) or `AGREEMENT` (copied from a rate contract or blanket agreement, with `rate_source_ref`). Core never stores the agreement and never prices a line itself (`FR-119` stands for counterparties, `RN-030`) | app | v1.1 | P8 | `RM-006` `RN-030` |
| **FR-502** | A PO line may carry **schedule lines** (`wh_purchase_order_schedule_lines`): schedule number, delivery date, quantity, kind `FIRM` or `FORECAST`, received / cancelled quantity, status. **Only a `FIRM` schedule line is receivable.** A `FIXED` line's schedule lines must sum to its ordered quantity; a `BLANKET_RELEASE` line's ordered quantity *is* the sum of its firm lines; an `OPEN` line's received quantity is bounded by the sum of its firm lines | app | v1.1 | P8 | `RM-005` |
| **FR-503** | A receipt against a scheduled line is **allocated to schedule lines oldest-date-first** inside the PO line's tolerance, recorded on a junction (`wh_goods_receipt_line_schedule_allocations`), so one GRN line can satisfy two schedule lines and a schedule line can be satisfied by two GRNs. A delivery earlier than `scheduled_date − warehouse.receiving.early_delivery_days` is refused `409 SCHEDULE_DELIVERY_TOO_EARLY` when the setting is set | app | v1.1 | P8 | `RM-005` |
| **FR-504** | Core publishes the **purchase-order port** (`ai.warehouse.port.purchase.WhPurchaseOrderPort`): create an order of any type, release (add or firm) schedule lines, amend open lines (never below received), cancel a schedule line, close a line or the order. Calls are idempotent on `(source_module, idempotency_key)` with a request fingerprint; a replay with a different body is refused `409 PORT_IDEMPOTENCY_CONFLICT`. A PO created through the port records `source_module` / `source_document_*`, and a **`PurchaseOrderChangeGuard` bean collection** lets the source module refuse manual edits, approval or cancel on its own POs. Receipt and closure events go out through the outbox (`FR-436`-shaped) so the buying module updates its drawn-down quantity. No `wh_` table references the buying module | app | v1.1 | P8 | `RN-053` R28 §6 "a published PO-creation port, plus a PO contributor/guard seam" |

### 6.2 Demand-order port for sales (`D1`)

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-505** | Core publishes the **demand-order port** (`ai.warehouse.port.demand.WhDemandOrderPort`), the sales mirror of `FR-504`: create a demand order (`demand_type` from the `DEMAND_TYPE` list, default `SALES`), release schedule lines, amend, cancel. Each order records `source_module`, `source_document_*`, the **sales-order reference** and the **customer PO reference**; idempotent exactly as `FR-504`; a `DemandOrderChangeGuard` bean collection refuses manual edits on port-owned orders A demand line may also carry a **customer delivery schedule** (`wh_demand_order_schedule_lines`): requested date, quantity, `FIRM`/`FORECAST`, shipped / cancelled quantity; **only firm quantity due within `warehouse.outbound.schedule_allocation_horizon_days` is allocatable**, a forecast line never reserves stock, and the line's `ordered_quantity` equals the sum of its firm schedule lines when it has any | app | v1.1 | P8 | `RN-053` `D1` |
| **FR-506** | Core publishes the **RMA-creation port** (`ai.warehouse.port.returns.WhRmaPort`: `createRma`, `cancelRma`, `getRmaPosition`) so a sales-return authorisation in the selling module creates the core RMA (`wh_rmas` / `wh_rma_lines`, `V510050`) through `WhRmaService.create` (`:186`) — idempotent on `(source_module, idempotency_key)` with a fingerprint, recording `source_module` / `source_document_*`, and guarded by an `RmaChangeGuard` bean collection against manual edits of port-owned RMAs. A **supplier return** carries an **intent** (code list `SUPPLIER_RETURN_INTENT`: `REPLACE`, `CREDIT`, `NO_ACTION`; default `NO_ACTION`) set at create and frozen at approval; dispatch emits outbox `WH_SUPPLIER_RETURN_DISPATCHED` with intent, PO/GRN origin, item, lot and quantity, so the buying module reinstates open PO quantity for `REPLACE` through `WhPurchaseOrderPort.amendOrder` / `releaseSchedule` — core never reinstates quantity itself, and `CREDIT` is an accounting handover point only | app | v1.1 | P8 | TRADE `OD-33` (`FR-612`, `FR-613`) |

### 6.3 Gate entry and gate pass (`B1`, `D3`; `RM-007`, `RM-024`)

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-507** | A **gate entry register** (`wh_gate_entries`) records every vehicle or hand-carried consignment crossing the site gate, **inward or outward**, with a gapless gate-entry number (`GE` series, per site), timestamp in, timestamp out, direction, purpose (code list `GATE_PURPOSE`: `PURCHASE_RECEIPT`, `RETURNABLE_IN`, `SUPPLIER_RETURN_OUT`, `SALES_DISPATCH`, `JOB_WORK_OUT`, `JOB_WORK_IN`, `RGP_OUT`, `NRGP_OUT`, `CUSTOMER_RETURN_IN`, `OTHER`), party, vehicle number, driver name and mobile, transporter, LR/docket number, and security officer. `arrived_at` is stamped by the server and cannot be backfilled (`IRR-23`) | app | v1.1 | P8 | `RM-007` `RM-024` |
| **FR-508** | An **inward** gate entry for a purchase receipt carries the **supplier bill number, bill date, bill type** (`TAX_INVOICE`, `DELIVERY_CHALLAN`, `BILL_OF_SUPPLY`, `OTHER` — code list `SUPPLIER_DOCUMENT_TYPE`), optional bill amount and e-way bill number, and links **one or more POs and ASNs** at creation (`wh_gate_entry_documents`) — the PO is on the arrival form, not attached afterwards. A PO that is not `APPROVED`/`PARTIALLY_RECEIVED`, belongs to another supplier or another site is refused at the link. The PO picker and every PO search on the gate entry and the GRN match **either** the core `po_number` **or** the supplier-facing number held in `wh_purchase_orders.source_document_ref` (the `warehouse-trade` PO number, TRADE `OD-30`), and both are shown (`poNumber`, `supplierPoNumber`) | app | v1.1 | P8 | `RM-007` |
| **FR-509** | A gate entry may be **turned back** at the gate (no PO, wrong material, documents missing) with a reason; nothing downstream can be created from it. A receiving session for a purchase is created **from** an inward gate entry and copies vehicle, driver, supplier and documents; when `warehouse.gate.entry_required_for_receipt` is true, a GRN against a PO is refused `409 GATE_ENTRY_REQUIRED` unless its session has a gate entry | app | v1.1 | P8 | `RM-007` |
| **FR-510** | A gate entry links a **weighment** — a `wh_weighing_records` row (`P5-17`, `V510213`) with `subject_type = GATE_ENTRY` (the closed `subject_type` CHECK at `V510213:155` is widened) and `subject_id` = the gate-entry number — and shows the net weight beside the bill weight; a difference above `warehouse.gate.weight_variance_percent` raises a `QUANTITY` reconciliation case on the GRN, never a block | app | v1.1 | P8 | R28 brief "weighment link" |
| **FR-511** | A gate entry is **closed by gate-out**: an inward entry closes when the vehicle leaves (stamps `departed_at` on the receiving session too); an outward entry closes only when every linked outward document (shipment, supplier return, job-work challan, gate pass) is in a dispatched state. A gate entry is never edited after close; a correction is a note with an audit row. A boom-barrier **gate event** (`WarehouseGateEvent`, `POST /warehouse/gate-events`) is claimed by a core `WarehouseGateEventHandler` that matches an `ENTRY` to a new or pre-registered gate entry by vehicle number and stamps an `EXIT` as a **gate-out proposal** — the close still runs every guard above | app | v1.1 | P8 | `RM-007` |
| **FR-512** | A **gate pass** (`wh_gate_passes`) authorises material to leave the site: kind `RETURNABLE` (RGP) or `NON_RETURNABLE` (NRGP), party, purpose (code list `GATE_PASS_PURPOSE`: `REPAIR`, `CALIBRATION`, `JOB_WORK`, `TRIAL`, `LOAN`, `SAMPLE`, `SCRAP_SALE`, `SUPPLIER_RETURN`, `OTHER`), expected return date (mandatory for returnable), lines with item **or** free-text description (tools, dies, moulds, gauges, equipment), quantity, UoM, approximate value, and remarks. Gapless `GP` number per site | app | v1.1 | P8 | `B1` `D3` |
| **FR-513** | **A gate pass never moves stock.** A line naming a stock item must reference the document that moves it — a supplier return, a shipment, a store issue, or a `warehouse-india` delivery challan (`whin_delivery_challans`, purposes `REPAIR`/`JOB_WORK`/`APPROVAL`/…) — by `(source_document_type, source_document_id)`, resolved by a **`GatePassSourceResolver` bean** (core registers `SUPPLIER_RETURN`, `SHIPMENT`, `STORE_ISSUE`; `warehouse-india` registers `DELIVERY_CHALLAN`), and that document must be posted/dispatched before gate-out; otherwise the line must be non-inventory (free text). A gate pass for a stock item with no resolvable source document is refused `422 GATE_PASS_STOCK_LINE_UNSOURCED` | app | v1.1 | P8 | `L-1` `D3` |
| **FR-514** | Gate pass lifecycle: `DRAFT` → `APPROVED` (checker, `wh_gate_passes:approve`, ≠ maker) → `OUT` (gate security records gate-out against an outward gate entry) → for RGP `PARTIALLY_RETURNED` → `RETURNED`; `CLOSED_SHORT` with a reason and approval; `CANCELLED` before gate-out. An NRGP is terminal at `OUT`. Returns are recorded line by line against an **inward gate entry** (`wh_gate_pass_returns`) with quantity and condition; returned quantity never exceeds the quantity out | app | v1.1 | P8 | `D3` |
| **FR-515** | An RGP is **overdue** when it is `OUT`/`PARTIALLY_RETURNED` and `expected_return_date` < today in the site's timezone; overdue is computed on read (grid tile, `overdueOnly` filter), and a daily job notifies the approver and the stores in-charge once per pass per `warehouse.gate.rgp_overdue_reminder_days`. An expected return date may be extended (revision with reason, approval) — never silently | app | v1.1 | P8 | `D3` |

### 6.4 GRN against the supplier bill; short and excess (`B2`; `RM-008`…`RM-010`)

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-516** | A GRN carries its **supplier bills** as child rows (`wh_goods_receipt_bills`: bill type, bill number, bill date, amount, e-way bill no., `is_primary`, `is_supplementary`), the primary bill copied from the gate entry and editable only in `DRAFT`; a **supplementary bill** may be appended after post (append-only, audited) and is how an excess is billed (`FR-520`). A bill number already on a **posted** GRN of the same supplier in the same financial year (normalised: trimmed, upper-cased, internal spaces removed) is refused `409 SUPPLIER_BILL_DUPLICATE` naming the first GRN. When `warehouse.receiving.bill_required_for_po_receipt` is true, a PO receipt posts only with a primary bill. A bill date after the receipt date is refused `422 SUPPLIER_BILL_DATE_AFTER_RECEIPT`. `wh_goods_receipts.invoice_matched` (today written by nothing) is set by `P5-10`'s three-way match only | app | v1.1 | P8 | `RM-008` |
| **FR-517** | Each GRN line carries **billed quantity** (stored, nullable for a blind receipt), **received quantity** (counted), **accepted** and **rejected** quantity (QC), plus **short quantity** = max(billed − received, 0) and **excess quantity** = max(received − billed, 0), the excess split into **excess accepted** and **excess refused**. `WhGoodsReceiptLine.billedQuantity()` returns the stored column; it no longer returns `receivedQuantity` | app | v1.1 | P8 | `RM-008` |
| **FR-518** | The **layered-truth chain** gains the bill: *Ordered 100 → Billed 100 → Gate weight ≈ → Received 92 → Accepted 89 → Authorised (MRN) 89*. Every number is stored and shown side by side on WS-077 and on the GRN and MRN prints; none is derived from another (`FR-123` extended) | app | v1.1 | P8 | `RM-008` `FR-123` |
| **FR-519** | **Short receipt** (billed > received at post) opens a `SHORT_SHIPMENT` **supplier claim** in `DRAFT` (`P5-23`, `wh_supplier_claims`) with one line per short GRN line, quantity = short quantity, value at the PO line rate, traced to the GRN line; the clerk submits it. **No debit note is generated** — the claim is the accounting handover point (§8). Short against the PO (not the bill) keeps today's `QUANTITY` reconciliation case. A short receipt never blocks the post | app | v1.1 | P8 | `RM-009` `RN-054` |
| **FR-520** | **Excess receipt** (received > billed, or received > open PO/schedule quantity) is resolved per line at post: **accepted** without approval when inside the resolved over-receipt tolerance (PO line → header → item → site, today's ladder); **accepted with approval** above tolerance only when a second user holding `wh_goods_receipts:approve_excess` approves that line's excess (maker ≠ checker); otherwise **refused** — the refused quantity is never received into stock, is recorded as `excess_refused_quantity` with a reason, and leaves with the vehicle (it appears on the gate-out). Accepted excess over the **bill** opens an **`EXCESS_OVER_BILL`** reconciliation case (new `RECON_CASE_TYPE` row) that stays `OPEN` until resolved `RECORD_SUPPLEMENTARY_BILL` (a supplementary bill row is appended to the GRN; resulting document = the GRN) or `ACCEPT_FREE_OF_CHARGE` (manager; resulting document = the GRN) — the credit-side handover point; no credit note is generated | app | v1.1 | P8 | `RM-010` `RN-054` |

### 6.5 Incoming inspection with configurable sampling (`B3`; `RM-011`)

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-521** | A **sampling scheme** (`wh_sampling_schemes`) is a named, versioned **band table** (`wh_sampling_scheme_bands`): lot-size from, lot-size to (open-ended last band), sample size **or** sample percent, optional acceptance number Ac and rejection number Re. Bands must be **contiguous from 1 with no gap or overlap**, the last band open-ended; a save that leaves any lot size uncovered is refused `422 SAMPLING_BANDS_NOT_CONTIGUOUS` naming the first uncovered size. The client's table (1–1000 → 5; 1001–10000 → 20) is one scheme (`OD-25`). A scheme referenced by a completed inspection is copy-on-write: an edit creates a new version and the inspection keeps the version it used | app | v1.1 | P8 | `RM-011` |
| **FR-522** | An inspection plan's `sample_size_formula` gains `BAND_TABLE` (reads the plan's scheme) and the two formulas that today fall back to the whole lot are **fixed**: `FIXED_QUANTITY` reads `wh_inspection_plans.fixed_sample_quantity`, `PERCENTAGE` reads `sample_percent` with an optional `min_sample_quantity`; both are required by the formula they serve (`422 SAMPLE_PARAMETER_REQUIRED`). The hard-coded **ANSI/ASQ Z1.4 general level II** table (`WhQualityInspectionSampleSize.java`) stays as the `AQL_TABLE` option, unchanged, and is equivalent to IS 2500 (Part 1) / ISO 2859-1 normal single sampling at level II. Every size rounds up to whole units and is capped at the lot (`RQP-GRD-20` unchanged) | app | v1.1 | P8 | `RM-011` `RQP-T1-16` open note |
| **FR-523** | A plan is chosen by an **assignment** (`wh_inspection_plan_assignments`) at the most specific matching scope, in this precedence: item + supplier → item → category + supplier → supplier → category → `whb_item_categories.default_inspection_plan_id` (today's rule) → none. Assignments carry effective-from/to and are dated, never overwritten. An assignment may say **`NO_INSPECTION`** (skip QC for a trusted item × supplier) — recorded, so a skipped inspection is a decision and not an absence | app | v1.1 | P8 | `RM-011` |
| **FR-524** | When the plan carries Ac/Re (band table or AQL with an AQL value), Complete **proposes a lot verdict**: defectives ≤ Ac → `ACCEPT_LOT`, ≥ Re → `REJECT_LOT`; the inspector confirms or overrides with a reason, and the verdict drives a **whole-lot disposition** of the QC-held quantity (sample destroyed in testing excluded). **Destructive-test quantity** is recorded per line and posted as an `ISSUE` to `VIRT-CONSUMED-<site>` with cost object `DEPARTMENT` = the site's QC department (`FR-533`), so the lot balances (`L-1`) | app | v1.1 | P8 | `RM-011` |
| **FR-525** | A quality inspection has a **polymorphic source**: `source_type` (code list `QC_SOURCE_TYPE`: `GOODS_RECEIPT`, `STORE_RETURN`, `PRODUCTION_RECEIPT`, `IN_PROCESS`, `STOCK`, `OTHER`), `source_document_id`, `source_line_id`, `source_document_ref`, and an **inspection stage** (code list `INSPECTION_STAGE`: `INCOMING`, `IN_PROCESS`, `FINAL`, `RETURN`, `PERIODIC`). `grn_id` / `grn_line_id` become nullable and are required only when `source_type = GOODS_RECEIPT`. A source type is honoured only when a **`QualityInspectionSourceResolver` bean** for it is registered; core registers `GOODS_RECEIPT`, `STORE_RETURN` and `STOCK`, `warehouse-manufacturing` registers its own. An unregistered source is refused `422 QC_SOURCE_TYPE_UNSUPPORTED`. One inspection series per source document (`FR-133` generalised) **Non-stock-bearing sources (SEAM-M4):** a resolver may declare `stockBearing = false` (MFG `IN_PROCESS`: inspection of a production operation with no stock subject); such an inspection has no held quantity or location, its lines record an **outcome** (code list `INSPECTION_OUTCOME`: `ACCEPT`, `REJECT`, `REWORK`) instead of a disposition, **posts no movement**, never routes to `MRN_PENDING`, and hands the outcome to the resolver's `onDisposition` hook | app | v1.1 | P8 | R28 §6 "QC with a polymorphic source"; SAP QM inspection-lot origin |

### 6.6 QC reject → supplier return; MRN (`B4`, `B5`; `RM-012`, `RM-013`)

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-526** | **Amends `FR-139`.** A completed GOODS_RECEIPT inspection with quantity dispositioned `REJECT` or `RTV` and not yet on a live supplier return offers an explicit **"Raise supplier return"** action. It creates a supplier return in **`DRAFT`** (maker = the user who pressed it), pre-filled with supplier, origin GRN, origin inspection, reason `QUALITY_REJECTED`, and one line per rejected inspection line at its rejected quantity and lot. It never approves, never dispatches and never posts; the ladder `DRAFT → APPROVED → PICKED → DISPATCHED → CLOSED` and its maker/checker are unchanged. **Nothing raises a supplier return automatically** — the refusal in `FR-139` survives as *"no silent auto-return"*. `debit_note_ref` stays a free-text reference; no debit note is generated (`RN-031`, `RN-054`) | app | v1.1 | P8 | `RM-012` `RN-031` |
| **FR-527** | A **material receipt note** (MRN, `wh_material_receipt_notes`) is the stores' authorisation that received and inspected material is taken on charge. When `warehouse.stores.mrn_required` is true for the site: a GRN line received into an allocatable status, and any QC-released quantity, lands in stock status **`MRN_PENDING`** (non-allocatable, non-issuable) with **no putaway task**; the MRN lists, per GRN line, billed / received / accepted / rejected quantity, rate and value from the PO; `DRAFT` → `SUBMITTED` (maker) → `AUTHORISED` (checker holding `wh_material_receipt_notes:authorise`, ≠ maker, ≠ the releasing inspector unless `warehouse.stores.mrn_authoriser_may_be_inspector`) or back to `DRAFT` on reject with reason; `CANCELLED` from `DRAFT`. **Authorise posts one `STATUS_CHANGE` `MRN_PENDING → AVAILABLE` per line and only then creates the putaway task.** Gapless `MRN` series per site. With the setting false, today's behaviour holds exactly. **Stock-availability rule:** material is issuable only from an allocatable status, so nothing in `MRN_PENDING`, `QC_HOLD` or `REJECTED` can be requisitioned, reserved, issued or transferred; availability (`FR-174`) excludes it | app | v1.1 | P8 | `RM-013` |
| **FR-528** | Core exposes the **purchase-requisition hand-off port** (`ai.warehouse.port.purchase.PurchaseRequisitionHandoff`, optional bean): a stores user may send a requisition shortfall to the buying module, which returns its document reference; core records the link (`wh_material_requisition_line_handoffs`) and shows the buying document's status by asking the port. With no bean registered (`warehouse-trade` off) the action is not offered — there is no stub that pretends **Supply-request seam for MRP (SEAM-M3):** core also publishes `WhReplenishmentSuggestionPort` (`publishExternal`, `withdrawExternal`, `getSuggestionStatus`) so `warehouse-manufacturing` MRP can post BUY proposals as core replenishment suggestions with origin `MRP` (code list `REPLENISHMENT_ORIGIN`: `REORDER`, `MRP`; `origin_document_type/id`, `need_date`), idempotent per origin proposal. With no `SuggestionConversionOwner` bean (trade off) the core replenishment screen converts them to a **draft core PO** exactly as reorder suggestions (MFG `OD-41`); with trade on, trade's *Raise PR* converts them (TRADE `OD-31`, `FR-557`) and core's convert-to-PO is not offered. Either conversion marks the suggestion `CONVERTED` with its resulting document, so it is never converted twice | app | v1.1 | P8 | `RM-001` hand-off, R28 §4 `A1` seam |

### 6.7 Material requisition, store issue, store return (`B6`, `B7`, `B8`; `RM-015`…`RM-017`, `S-052`)

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-529** | A **material requisition** (indent; `wh_material_requisitions` + lines) asks a store for material: issuing site, requesting **department** (platform `departments`), **cost object** (`FR-533`), purpose (code list `REQUISITION_PURPOSE`: `CONSUMPTION`, `MAINTENANCE`, `PRODUCTION`, `PROJECT`, `CAPITAL`, `SAMPLE`, `OTHER`), requested-by, required-by date, priority, and lines with item, quantity, UoM, required date, remarks. Gapless `MRQ` series per site. A department requester sees and acts only on requisitions of departments they belong to (record-level guard, `P1-18` shape) | app | v1.1 | P8 | `RM-015` |
| **FR-530** | Requisition lifecycle: `DRAFT` → `SUBMITTED` → `APPROVED` / `REJECTED`; `SUBMITTED` → `DRAFT` (recall by the requester); `APPROVED` → `PARTIALLY_ISSUED` → `ISSUED` (effects of issue posts); `APPROVED`/`PARTIALLY_ISSUED` → `CLOSED` (short-close, reason mandatory, the unissued remainder → `closed_quantity`); `DRAFT`/`SUBMITTED`/`APPROVED`-with-nothing-issued → `CANCELLED`. **Approval is per line**: the approver sets `approved_quantity` ≤ requested (zero rejects the line); the approver holds `wh_material_requisitions:approve`, is not the requester, and — when `warehouse.stores.requisition_approver_scope = DEPARTMENT_HEAD` — is the head of the requesting department | app | v1.1 | P8 | `RM-015` |
| **FR-531** | On approval, per `warehouse.stores.requisition_reservation` (`NONE` / `SOFT` / `HARD`, default `SOFT`) the approved quantity is reserved in the open-item reservation ledger (`P0-09`) with holder `MATERIAL_REQUISITION`/line; issue consumes the reservation, closure and cancel release it. Reservation never exceeds available; a shortfall is shown per line (`available`, `reserved`, `short`) and computed by the backend. *Amended for MFG MD-16:* when the line's cost-object resolver reports reservations it already holds for the item (`CostObjectResolver.reservationsFor`, `FR-533` — MFG's `PRODUCTION_ORDER` holds its component reservations from release), approval **creates no reservation**: the line shows the owner's reserved quantity, the store issue consumes the owner's reservations, and close/cancel release nothing (the owner releases its own). A requisition for a production order is created by MFG through **`WhMaterialRequisitionPort`** (`create`/`cancel`/`close`, `p8-09`) | app | v1.1 | P8 | `RM-015` |
| **FR-532** | **Partial issue** is normal: a line is issued over any number of store issues until issued = approved or it is closed. A requisition line short of stock may be **handed off as a back-to-back purchase requisition** (`FR-528`) for the short quantity; the hand-off does not change the requisition's status, and the received material is issued against the same requisition when it arrives | app | v1.1 | P8 | `RM-015` `RM-001` |
| **FR-533** | Every **store-issue line carries a cost object** — `cost_object_type` (code list `COST_OBJECT_TYPE`: `DEPARTMENT`, `COST_CENTRE`, `PRODUCTION_ORDER`, `WORK_ORDER`, `MACHINE`, `PROJECT`), `cost_object_id`, `cost_object_ref` (frozen display code) — defaulted from the requisition line, else the header, never null. A type is accepted only when a **`CostObjectResolver` bean** for it validates the id (core: `DEPARTMENT` → platform `departments`, `COST_CENTRE` → `wh_cost_centres`, `WORK_ORDER` → `wh_work_orders`; `warehouse-manufacturing`: `PRODUCTION_ORDER`). **The cost object lives on the issue document's lines, referenced from the movement by `source_document_type`/`source_document_id`; the ledger gains no column** (`RN-034` resolves `S-052`). The `COST_CENTRE` resolver reads a thin **cost-centre master** (`wh_cost_centres`: code, name, kind `COST_CENTRE`/`MACHINE`/`PROJECT`, department, parent, is_active, `external_ref` for a future accounting dimension) — a warehouse master, not an accounting dimension, until accounting is built (`OD-27`) **Resolver contract (SEAM-M1, SEAM-M2):** `ResolvedCostObject` carries `counterLocationPurpose` (default `CONSUMED`; MFG's `PRODUCTION_ORDER` resolver returns `PRODUCTION`, so the issue lands in WIP `VIRT-PRODUCTION-<site>`, not expense); and the resolver exposes default hooks `assertIssuable(costObjectId, itemId, baseQty)` (before post, may refuse), `onIssuePosted(line)` and `onReturnPosted(line)` called **inside** the posting transaction (a hook failure rolls the post back). There is **no `onIssueReversed`** hook: a posted store issue is never reversed (`STO-D11`); its correction is a store return, which fires `onReturnPosted`. *Amended for MFG MD-16:* a default `reservationsFor(costObjectId, itemId)` (empty by default) names reservations the cost object already holds, consumed by the issue instead of a requisition reservation (`FR-531`). *Amended for MFG MD-14:* MFG's `PRODUCTION_ORDER` resolver accepts an order `RELEASED`, `IN_PROGRESS` or `COMPLETED` (technically complete, not yet settled — late issues and returns flow into the settlement), and refuses one `PLANNED`, `CANCELLED`, `CLOSED`, on hold, or with a settlement awaiting approval | app | v1.1 | P8 | `S-052` `RN-034` `RM-016` |
| **FR-535** | A **store issue** (`wh_store_issues` + lines + serials) issues stock against an approved requisition (or, with `wh_store_issues:issue_without_requisition` and `warehouse.stores.direct_issue_allowed`, directly) from a named location, lot, serial and status `AVAILABLE`; issued quantity per line ≤ approved − issued − closed on the requisition line. **Post** writes one balanced **`ISSUE`** movement per document through the single writer: −quantity at the store location, +quantity at **`VIRT-<counterLocationPurpose>-<site>`** (`VIRT-CONSUMED` by default, `VIRT-PRODUCTION` for a production order — `FR-533`), `source_document_type = STORE_ISSUE`, `source_document_id` = the issue; valued at the movement's cost (weighted average / FIFO per item, `P0-17`). The receiver (user or name) and acknowledgement time are recorded. Gapless `SIS` series. A posted issue is never edited or reversed; a correction is a store return plus a new issue | app | v1.1 | P8 | `RM-016` |
| **FR-536** | A **store return** (`wh_store_returns` + lines) brings unused material back from a department: every line names the **store-issue line** it returns, quantity ≤ issued − already returned on that line (`422 STORE_RETURN_EXCEEDS_ISSUED`), condition (code list `RETURN_CONDITION`: `GOOD`, `NEEDS_INSPECTION`, `DAMAGED`, `SCRAP`), reason (reason context `STORE_RETURN`). The cost object is **inherited** from the issue line and cannot be changed. Lifecycle `DRAFT` → `SUBMITTED` (department) → `POSTED` (stores, after physical receipt) or `REJECTED` (stores refuses, reason); `CANCELLED` from `DRAFT`/`SUBMITTED`. Gapless `SRN` series | app | v1.1 | P8 | `RM-017` |
| **FR-537** | Posting a store return writes one balanced **`ISSUE_RETURN`** movement (new seeded type, `IN`, mirror of `ISSUE`): −quantity at the **same virtual location the issue line posted to** (`VIRT-CONSUMED` or `VIRT-PRODUCTION`), +quantity at the return location, **valued at the original issue line's unit cost**, in status by condition: `GOOD` → `AVAILABLE` (putaway task created), `NEEDS_INSPECTION` → `QC_HOLD` with an inspection of source `STORE_RETURN` opened, `DAMAGED` → `DAMAGED`, `SCRAP` → `DAMAGED` then the normal scrap approval. The issue line's `returned_quantity` and the requisition line's `returned_quantity` move in the same transaction; a requisition never reopens | app | v1.1 | P8 | `RM-017` |

### 6.8 Prints and registers

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-534** | **Plant-stores performance benchmarks** (replaces the withdrawn dealer `FR-422` for this segment), each measured from stored timestamps — never typed — per site × period with median, P90 and the share inside a target set per site (`warehouse.stores.kpi_target_*`): **gate-to-GRN time** (`wh_gate_entries.entered_at` → GRN `received_at`/post), **GRN-to-MRN time** (GRN post → MRN `authorised_at`), **QC lead time** (GRN post / QC-hold entry → inspection `completed_at` → disposition), **issue turnaround** (requisition `approved_at` → first and last store-issue `posted_at`; plus fill rate = issued ÷ approved at closure), **store-return cycle** (return `submitted_at` → `posted_at`, and issue → return elapsed), and **dock-to-stock** (GRN post → putaway completion, `dock_to_stock_completed_at`). Shown on a *Stores performance* tab of WS-277 with drill-down to the documents; definitions are frozen as KPI rows (`FR-395`-style, the `P2-21` frozen-definition rule) so a definition change is a new KPI version | app | v1.1 | P8 | `FR-422` (withdrawn, SPINE) · CAT-26 |
| **FR-538** | Seven **system print templates** (`PRINT_TEMPLATE_KIND` rows and `SYS-` templates through `P2-14`'s framework): `GATE_ENTRY` slip, `GATE_PASS` (RGP/NRGP, with signatures of maker, approver, security and receiver), `GRN`, `MRN` (with authoriser and time), `MATERIAL_REQUISITION`, `STORE_ISSUE` slip (with receiver acknowledgement), `STORE_RETURN` note. The GRN detail (WS-077) and the MRN detail (WS-267) gain a **Print** action — today the GRN page has none although `SYS-GRN` exists (`V510060:323`). A print is allowed from the states the contract names; a reprint is marked *duplicate* (`wh_print_jobs.is_reprint`) | app | v1.1 | P8 | `RM-013` CAT-23 |
| **FR-539** | Five **stores registers**, backend-filtered and exportable: gate register (inward/outward by date), **RGP pending / overdue**, **requisitions pending issue** (approved − issued, ageing by required-by date), **issue register by cost object** (item, quantity, value by department / cost centre / production order for a date range) and **consumption by department** (issues − returns, net). Statistics tiles are filter-aware with no cache name (`FR-395`) **Consumption** counts only issues/returns to `VIRT-CONSUMED`; issues to `VIRT-PRODUCTION` (WIP) are listed in the issue register but are not consumption — MFG reports them against the order | app | v1.1 | P8 | CAT-24 `S-052` |

## 7. Screens (WS-260…WS-277)

| WS | Name | Module | Route | Ref | Grid | Ver · Ph |
|---|---|---|---|---|---|---|
| WS-260 | Gate Entries | app | `/warehouse/gate/entries` | SV | Y | v1.1 · P8 |
| WS-261 | Gate Entry detail | app | `/warehouse/gate/entries/[id]` | SV | N | v1.1 · P8 |
| WS-262 | Gate Passes | app | `/warehouse/gate/passes` | SV | Y | v1.1 · P8 |
| WS-263 | Gate Pass detail (lines, returns) | app | `/warehouse/gate/passes/[id]` | SV | N | v1.1 · P8 |
| WS-264 | Sampling Schemes | app | `/warehouse/quality/sampling-schemes` | D | Y | v1.1 · P8 |
| WS-265 | Inspection Plan Assignments | app | `/warehouse/quality/plan-assignments` | C | Y | v1.1 · P8 |
| WS-266 | Material Receipt Notes | app | `/warehouse/stores/mrns` | SV | Y | v1.1 · P8 |
| WS-267 | MRN detail (+ print) | app | `/warehouse/stores/mrns/[id]` | SV | N | v1.1 · P8 |
| WS-268 | Material Requisitions | app | `/warehouse/stores/requisitions` | SV | Y | v1.1 · P8 |
| WS-269 | Material Requisition detail | app | `/warehouse/stores/requisitions/[id]` | SV | N | v1.1 · P8 |
| WS-270 | Store Issues | app | `/warehouse/stores/issues` | SV | Y | v1.1 · P8 |
| WS-271 | Store Issue detail | app | `/warehouse/stores/issues/[id]` | SV | N | v1.1 · P8 |
| WS-272 | Store Returns | app | `/warehouse/stores/returns` | SV | Y | v1.1 · P8 |
| WS-273 | Cost Centres | app | `/warehouse/stores/cost-centres` | D | Y | v1.1 · P8 |
| WS-274 | Issue queue (approved requisitions awaiting issue) | app | `/warehouse/stores/issue-queue` | C | Y | v1.1 · P8 |
| WS-275 | PO Delivery Schedule | app | `/warehouse/inbound/purchase-orders/schedule` | C | Y | v1.1 · P8 |
| WS-276 | Customer Delivery Schedule | app | `/warehouse/outbound/demand-schedule` | C | Y | v1.1 · P8 |
| WS-277 | Stores Registers (RGP pending, requisitions pending, issue register by cost object, consumption by department, stores performance) | app | `/warehouse/stores/registers` | C | Y | v1.1 · P8 |

Ref: `D` = Department, `C` = Customer, `SV` = Service Vehicle (CLAUDE.md canonical references). **Changed existing screens:** WS-072/073 (PO type, schedule tab, port-owned banner), WS-075 (create
from gate entry), WS-076/077 (bill fields, billed/short/excess columns, approve-excess, Print), WS-079 (plan
parameters, scheme), WS-080 (source/stage columns, lot verdict, destructive qty, **Raise supplier return**), WS-084
supplier returns (origin inspection column). Screen detail is in each contract's §5.

## 8. Accounting handover points (deferred — recorded, never generated)

| Event | Handover carrier | What accounting will read |
|---|---|---|
| Short against bill (`FR-519`) | `wh_supplier_claims` `SHORT_SHIPMENT` | debit-note candidate: supplier, bill no/date, item, qty, value |
| QC reject returned (`FR-526`) | `wh_supplier_returns` `DISPATCHED` + optional `QUALITY_REJECT` claim | purchase-return goods document and debit-note candidate |
| Excess accepted over bill (`FR-520`) | `wh_reconciliation_cases` `EXCESS_OVER_BILL` (open until a supplementary bill or free-of-charge resolution) | supplementary bill expected |
| GRN post / MRN authorise (`FR-527`) | outbox `WH_GRN_POSTED`, `WH_MRN_AUTHORISED` with bill fields | GRNI accrual, bill matching (`P5-10` three-way match reads `supplier_bill_no`) |
| Store issue / return (`FR-535`, `FR-537`) | movements + issue lines' cost object | consumption by cost object |

## 9. Scenarios (WH-SC-420…WH-SC-479)

| ID | Given | When | Then | FRs | Inv | Module | Ver·Ph | Kind |
|---|---|---|---|---|---|---|---|---|
| **WH-SC-420** | `buyer1` needs 1,000 kg resin at a fixed rate over three months | an `OPEN` PO is created with rate ₹120/kg and no quantity | the PO saves with `ordered_quantity` null; a GRN against it is refused `409 NO_FIRM_SCHEDULE_OPEN` until a firm schedule line exists | FR-500 FR-502 | — | app | v1.1·P8 | edge |
| **WH-SC-421** | the open PO above | trade releases a firm schedule line of 300 kg for 5 Nov through the port | the line is receivable; a receipt of 310 kg inside a 5% tolerance allocates 300 to the line and 10 as excess accepted | FR-502 FR-503 FR-504 FR-520 | — | app | v1.1·P8 | happy |
| **WH-SC-422** | a `BLANKET_RELEASE` PO with firm lines 5 Nov 200, 12 Nov 200 | a GRN of 350 posts on 6 Nov | allocation oldest-first: 200 to 5 Nov (`RECEIVED`), 150 to 12 Nov (`PARTIALLY_RECEIVED`) on the junction | FR-503 | — | app | v1.1·P8 | happy |
| **WH-SC-423** | `warehouse.receiving.early_delivery_days = 3`, firm line 20 Nov | a receipt is attempted on 10 Nov | refused `409 SCHEDULE_DELIVERY_TOO_EARLY` naming the line and the earliest date 17 Nov | FR-503 | — | app | v1.1·P8 | negative |
| **WH-SC-424** | trade replays a create call with the same idempotency key and a changed quantity | the port receives it | refused `409 PORT_IDEMPOTENCY_CONFLICT`; the original PO is unchanged; a same-body replay returns the original PO id | FR-504 | — | app | v1.1·P8 | negative |
| **WH-SC-425** | a PO created by `warehouse-trade` | `stores1` edits a line quantity on WS-073 | refused `409 PO_OWNED_BY_SOURCE_MODULE` by trade's guard bean; with trade disabled the guard is absent and the edit is allowed | FR-504 | — | app | v1.1·P8 | negative |
| **WH-SC-426** | a sales order with a customer schedule: 100 firm on 5 Nov, 100 forecast on 5 Dec, horizon 14 days | allocation runs on 1 Nov | only the 5 Nov firm 100 is allocatable; the forecast line reserves nothing | FR-505 | — | app | v1.1·P8 | happy |
| **WH-SC-427** | a truck from supplier S with bill INV-77 dated 1 Nov against PO-12 | `sec1` records an inward gate entry | GE number issued; PO-12, bill no/date, vehicle, driver captured on arrival; a receiving session is created from it with the same documents | FR-507 FR-508 FR-509 | IRR-23 | app | v1.1·P8 | happy |
| **WH-SC-428** | the gate entry links PO-15 of a different supplier | save | refused `422 GATE_ENTRY_PO_SUPPLIER_MISMATCH` on `documents[0].poId` | FR-508 | — | app | v1.1·P8 | negative |
| **WH-SC-429** | a vehicle with no PO and no challan | `sec1` turns it back | entry `TURNED_BACK` with reason; "Create receiving session" is not offered | FR-509 | — | app | v1.1·P8 | edge |
| **WH-SC-430** | `entry_required_for_receipt = true` | a PO GRN is created on a session with no gate entry | refused `409 GATE_ENTRY_REQUIRED` | FR-509 | — | app | v1.1·P8 | negative |
| **WH-SC-431** | bill weight 10,000 kg, weighbridge net 9,650 kg, variance setting 2% | the weighment links | net and variance shown; a `QUANTITY` reconciliation case opens on the GRN; nothing is blocked | FR-510 | — | app | v1.1·P8 | edge |
| **WH-SC-432** | a die sent for repair | `stores1` raises an RGP, `mgr1` approves, `sec1` gates it out | GP number; status `OUT`; no movement posted | FR-512 FR-513 FR-514 | L-1 | app | v1.1·P8 | happy |
| **WH-SC-433** | an RGP line names a stock item with no posted source document | save | refused `422 GATE_PASS_STOCK_LINE_UNSOURCED` | FR-513 | L-1 | app | v1.1·P8 | negative |
| **WH-SC-434** | the RGP's expected return date was yesterday | the grid loads | the pass shows overdue; the daily job notifies once | FR-515 | — | app | v1.1·P8 | time |
| **WH-SC-435** | RGP for 3 gauges; 2 come back | `sec1` records the return against an inward gate entry | `PARTIALLY_RETURNED`; a return of 2 more is refused `422 GATE_PASS_RETURN_EXCEEDS_OUT` | FR-514 | — | app | v1.1·P8 | negative |
| **WH-SC-436** | `stores1` raised the RGP | `stores1` approves it | refused `403 APPROVER_IS_ACTOR` | FR-514 | — | app | v1.1·P8 | negative |
| **WH-SC-437** | bill INV-77 already on a posted GRN of supplier S this year | a second GRN with `inv-77 ` posts | refused `409 SUPPLIER_BILL_DUPLICATE` naming the first GRN (normalised: trimmed, upper-cased) | FR-516 | — | app | v1.1·P8 | negative |
| **WH-SC-438** | bill 100, received 92 | the GRN posts | short 8; a `SHORT_SHIPMENT` claim in `DRAFT` with one line of 8 at the PO rate, traced to the GRN line; no debit note | FR-517 FR-519 | — | app | v1.1·P8 | happy |
| **WH-SC-439** | bill 100, received 104, tolerance 2% | post | 2 accepted inside tolerance; 2 above need approval; without approval the post is refused `409 EXCESS_APPROVAL_REQUIRED` | FR-520 | — | app | v1.1·P8 | negative |
| **WH-SC-440** | the same line, `mgr1` approves excess 2 | post | 104 received; an `EXCESS_OVER_BILL` case for 4 stays open; appending supplementary bill INV-77A for 4 resolves it; no credit note | FR-520 | — | app | v1.1·P8 | happy |
| **WH-SC-441** | the same line, the clerk refuses the 2 above tolerance | post | 102 received; `excess_refused_quantity` 2 with reason; the gate-out lists 2 units leaving with the vehicle | FR-520 FR-511 | L-1 | app | v1.1·P8 | edge |
| **WH-SC-442** | a scheme with bands 1–1000 → 5 and 1001–10000 → 20 and no open band | save | refused `422 SAMPLING_BANDS_NOT_CONTIGUOUS` (first uncovered 10001) | FR-521 | — | app | v1.1·P8 | negative |
| **WH-SC-443** | scheme bands 1–1000 → 5, 1001–10000 → 20, 10001+ → 32 | inspection starts on a lot of 2,400 | proposed sample 20 | FR-521 FR-522 | — | app | v1.1·P8 | happy |
| **WH-SC-444** | plan `FIXED_QUANTITY` 10, lot 6 | start | proposed 6 (capped at the lot) | FR-522 | — | app | v1.1·P8 | edge |
| **WH-SC-445** | plan `PERCENTAGE` 2.5% with minimum 3, lot 80 | start | proposed 3 (2 rounded up to 2, raised to the minimum) | FR-522 | — | app | v1.1·P8 | edge |
| **WH-SC-446** | a plan saved `PERCENTAGE` with no percent | save | refused `422 SAMPLE_PARAMETER_REQUIRED` on `samplePercent` | FR-522 | — | app | v1.1·P8 | negative |
| **WH-SC-447** | assignments: category RM → plan A; item X × supplier S → plan B | a GRN of item X from S | plan B is used; the same item from supplier T uses plan A | FR-523 | — | app | v1.1·P8 | happy |
| **WH-SC-448** | item X × supplier S assigned `NO_INSPECTION` | the GRN posts | stock lands per receiving status with no QC hold; the assignment is named in the GRN line's audit | FR-523 | — | app | v1.1·P8 | edge |
| **WH-SC-449** | band Ac 1 / Re 2, sample 20, 2 defectives | complete | verdict proposed `REJECT_LOT`; confirm rejects the whole QC-held quantity | FR-524 | — | app | v1.1·P8 | happy |
| **WH-SC-450** | 3 units destroyed in testing out of 500 | disposition | 3 posted as `ISSUE` to `VIRT-CONSUMED` with cost object = the QC department; 497 dispositioned | FR-524 FR-533 | L-1 | app | v1.1·P8 | edge |
| **WH-SC-451** | manufacturing registers a `PRODUCTION_RECEIPT` resolver | an inspection starts from an FG receipt | it starts with `grn_id` null; with manufacturing off the same call is refused `422 QC_SOURCE_TYPE_UNSUPPORTED` | FR-525 | — | app | v1.1·P8 | happy |
| **WH-SC-452** | an inspection with 12 rejected units | `qc1` presses Raise supplier return | a `DRAFT` return with 12 units, origin GRN + inspection, reason `QUALITY_REJECTED`; nothing posted; a second press is refused `409 SUPPLIER_RETURN_ALREADY_RAISED` | FR-526 | — | app | v1.1·P8 | happy |
| **WH-SC-453** | an inspection completes with rejects | no one acts | no supplier return exists (no auto-return) | FR-526 FR-139 | — | app | v1.1·P8 | negative |
| **WH-SC-454** | `mrn_required = true`, GRN released by `qc1` | stores prepares and submits the MRN; `qc1` tries to authorise | refused `403 MRN_AUTHORISER_IS_INSPECTOR`; `mgr1` authorises; status change to `AVAILABLE` posts and putaway tasks are created | FR-527 | L-1 | app | v1.1·P8 | happy |
| **WH-SC-455** | stock in `MRN_PENDING` | a requisition approval tries to reserve it | not counted as available; reservation short | FR-527 FR-531 | — | app | v1.1·P8 | negative |
| **WH-SC-456** | an authorised MRN | Print twice | `SYS-MRN` rendered; second print marked duplicate | FR-538 | — | app | v1.1·P8 | happy |
| **WH-SC-457** | `mrn_required = false` | a GRN posts | today's behaviour: received into the resolved status, putaway created at post / release | FR-527 | — | app | v1.1·P8 | regression |
| **WH-SC-458** | `req1` of Maintenance raises MRQ for 10 bearings, cost centre CC-MNT | submit, `head1` approves 8 | line approved 8; SOFT reservation of 8 | FR-529 FR-530 FR-531 | — | app | v1.1·P8 | happy |
| **WH-SC-459** | `req1` approves own requisition | — | refused `403 APPROVER_IS_ACTOR` | FR-530 | — | app | v1.1·P8 | negative |
| **WH-SC-460** | `req2` of Production views a Maintenance requisition by id | — | `404` (record-level guard) | FR-529 | — | app | v1.1·P8 | negative |
| **WH-SC-461** | approved 8, available 5 | stores issues 5 and hands off 3 as a back-to-back PR | issue posts 5 (`PARTIALLY_ISSUED`); a hand-off link shows trade's PR number; status unchanged | FR-532 FR-528 | — | app | v1.1·P8 | happy |
| **WH-SC-462** | trade disabled | the requisition line is short | "Raise purchase requisition" is not offered | FR-528 | — | app | v1.1·P8 | edge |
| **WH-SC-463** | issue of 5 posts | — | one `ISSUE` movement −5 at the bin, +5 at `VIRT-CONSUMED-<site>`, `source_document_type = STORE_ISSUE`; the issue line carries `COST_CENTRE` CC-MNT; the movement line carries no cost-object column | FR-533 FR-535 | L-1 RN-034 | app | v1.1·P8 | happy |
| **WH-SC-464** | an issue line with cost object `PRODUCTION_ORDER` and manufacturing off | save | refused `422 COST_OBJECT_TYPE_UNSUPPORTED` | FR-533 | — | app | v1.1·P8 | negative |
| **WH-SC-465** | an issue of 9 against approved 8 | post | refused `422 ISSUE_EXCEEDS_APPROVED` on `lines[0].quantity` | FR-535 | — | app | v1.1·P8 | negative |
| **WH-SC-466** | requisition line approved 8, issued 5 | stores closes it short | `CLOSED`, remainder 3 → `closed_quantity`, reservation released, reason recorded | FR-530 FR-531 | — | app | v1.1·P8 | happy |
| **WH-SC-467** | 5 bearings issued, 2 unused | the department returns 2 as `GOOD` | `ISSUE_RETURN` +2 at the return location at the issue's unit cost, `AVAILABLE`, putaway created; issue line returned 2 | FR-536 FR-537 | L-1 | app | v1.1·P8 | happy |
| **WH-SC-468** | the same issue line | a return of 4 more | refused `422 STORE_RETURN_EXCEEDS_ISSUED` (3 remain) | FR-536 | — | app | v1.1·P8 | negative |
| **WH-SC-469** | a return marked `NEEDS_INSPECTION` | post | stock in `QC_HOLD`; an inspection of source `STORE_RETURN` opened | FR-537 FR-525 | — | app | v1.1·P8 | happy |
| **WH-SC-470** | a submitted return whose material never arrived | stores rejects | `REJECTED` with reason; nothing posted | FR-536 | — | app | v1.1·P8 | edge |
| **WH-SC-471** | issues and returns for CC-MNT in October | consumption by department is opened | net = issues − returns at value; export matches grid | FR-539 | — | app | v1.1·P8 | happy |
| **WH-SC-472** | a posted store issue | a user tries PUT on it | refused `409 STORE_ISSUE_POSTED_IMMUTABLE` | FR-535 | — | app | v1.1·P8 | negative |
| **WH-SC-473** | an approved requisition, nothing issued | the requester cancels | `CANCELLED`, reservation released | FR-530 | — | app | v1.1·P8 | happy |
| **WH-SC-474** | a requisition `PARTIALLY_ISSUED` | the requester cancels | refused `409 REQUISITION_TRANSITION_INVALID`; close-short is offered instead | FR-530 | — | app | v1.1·P8 | negative |
| **WH-SC-475** | a sampling scheme used by a completed inspection | the band is edited | a new version is created; the inspection still shows the old version's band | FR-521 | — | app | v1.1·P8 | edge |
| **WH-SC-476** | gate-out of an outward entry whose supplier return is still `PICKED` | security closes | refused `409 GATE_OUT_DOCUMENT_NOT_DISPATCHED` naming it | FR-511 | — | app | v1.1·P8 | negative |
| **WH-SC-477** | a GRN with bill date 5 Nov received 3 Nov | post | refused `422 SUPPLIER_BILL_DATE_AFTER_RECEIPT` | FR-516 | — | app | v1.1·P8 | negative |

| **WH-SC-478** | trade approves an SRA for 20 units of a shipped SO | trade calls `WhRmaPort.createRma` twice with the same key | one RMA `OPEN` with `source_module = warehouse-trade`; the replay returns it; a manual edit on WS-RMA is refused by trade's guard | FR-506 | — | app | v1.1·P8 | happy |
| **WH-SC-479** | a supplier return with intent `REPLACE` for 12 rejected units | it is dispatched | outbox `WH_SUPPLIER_RETURN_DISPATCHED` carries intent `REPLACE`, origin PO line and 12; the core PO is untouched until trade's port amend | FR-506 | — | app | v1.1·P8 | happy |

## 10. Decisions (taken in this file)

| ID | Decision | Why |
|---|---|---|
| **STO-D1** | PO type is a closed set (`FIXED`/`OPEN`/`BLANKET_RELEASE`) on `wh_purchase_orders.po_type`, service-whitelisted, no CHECK; the **agreement** (blanket, rate contract) is a `warehouse-trade` document referenced by text, never a core table | `RN-053` puts agreements in trade; behaviour branches on the type, so it is not an extensible vocabulary |
| **STO-D2** | Open quantity lives **only** on schedule lines (`ordered_quantity` nullable only for `OPEN`); receipt allocates oldest-first through a junction | R28 §6 "open quantity on release lines only"; one GRN line ↔ many schedule lines without splitting the GRN line |
| **STO-D3** | Gate entry is its **own register**, upstream of the receiving session; the session keeps unloading, seals and dock. `wh_receiving_sessions.gate_pass_ref` stays as the *supplier's* document reference | the session is the unload; the gate sees outward traffic and turned-back vehicles that never unload |
| **STO-D4** | **A gate pass never posts stock.** Stock leaves through its own posting document; the gate pass references it | one writer per stock event (`FR-436`); a second stock path would double-count |
| **STO-D5** | Short against bill → `SHORT_SHIPMENT` claim in `DRAFT` automatically (a claim is a record, not a financial document); excess over tolerance → approve or refuse, never silent; accepted excess over bill → reconciliation case | `RN-054`: handover, never a note; R27 `RM-009`/`RM-010` |
| **STO-D6** | Sampling: a band table (user) **plus** the existing hard-coded Z1.4 level II table kept as `AQL_TABLE` — no switching rules (tightened/reduced) and no skip-lot dynamics in P8 | the client asked for bands; switching rules need lot history and are refused with a re-entry path (§11 row 4) |
| **STO-D7** | QC source is polymorphic by `(source_type, source_document_id, source_line_id)` plus resolver beans; no FK to a sibling; `grn_id` kept for GRN sources | `D-16` FKs point down only; SAP QM inspection-lot origins (01 GR for PO, 04 GR from production, 05 other) are the model |
| **STO-D8** | MRN is a **separate document and a separate actor** from inspection, gated by a site setting, and it is the point where stock becomes `AVAILABLE` (status `MRN_PENDING` before it) | `RM-013`; availability by status reuses the allocatable flag instead of a second availability rule |
| **STO-D9** | Material requisition is **its own document**, not a demand order; the demand order keeps the shipping ladder | `RM-015`: the demand ladder (`OPEN→…→SHIPPED`) has no department, approver or closure semantics |
| **STO-D10** | Store issue posts the existing `ISSUE` type to `VIRT-CONSUMED`; store return posts a new `ISSUE_RETURN` type (`ISSUE_REVERSAL` stays the whole-movement mirror); the cost object is on **issue lines**, never on the ledger (`RN-034`) | `ISSUE_REVERSAL` cancels a whole movement (R27 `RM-017`); partial return needs its own type and the original cost |
| **STO-D11** | A posted store issue is immutable; correction = store return + new issue | the ledger is append-only (`L-2`); an "edit issue" would be a hidden reversal |
| **STO-D13** | The four MFG seams are amendments, not new documents: counter-location purpose and posting hooks on the cost-object resolver (`FR-533`), a non-stock-bearing QC source (`FR-525`), and an external replenishment-suggestion port (`FR-528`). **Rejected part:** MFG's proposed `onIssueReversed` hook, because no issue-reversal path exists (`STO-D11`); MFG adopts `onReturnPosted` (MFG MD-17). *Amended for MFG MD-14 / MD-16:* the resolver also admits `COMPLETED` orders and exposes `reservationsFor` so a production-order requisition never double-reserves | keeps one writer per stock event; WIP is not expense; MRP output reaches purchasing through the one suggestion table both modules already read |
| **STO-D12** | New P8 schema lands as **new migrations** (`V510400`+ app, `V500300`+ base, `V511400`+ seeds) after `P7`'s one rebuild — never as edits of the rebuilt files | `RN-052` allows one rebuild; P8 lands on a rebuilt DB that must not be rebuilt again |

## 11. Open decisions (OD-25…OD-29)

| # | Question | Safe default (built unless the user decides otherwise) | Requirements blocked |
|---|---|---|---|
| **OD-25** | The client's bands read *"1–1000 → 5, 1–10000 → 20"*: overlapping as written. Read as contiguous `1–1000 → 5`, `1001–10000 → 20`? And what sample above 10,000? | contiguous reading; the seeded `CLIENT-DEFAULT` scheme carries a third open band `10001+ → 32` marked *to confirm*; the save rule (`FR-521`) forces every install to state one | FR-521 (seed only) |
| **OD-26** | Is the MRN step on by default for a new manufacturing site? | `warehouse.stores.mrn_required = true` for new sites of type production store/raw-material store, `false` otherwise; per-site override | FR-527 |
| **OD-27** | Cost centres: a thin warehouse master now, or wait for accounting dimensions? | thin `wh_cost_centres` with `external_ref`; when accounting arrives, an adapter maps `external_ref` to its dimension — no migration of issue lines | FR-534 |
| **OD-28** | Accepted excess over the bill: await a supplementary bill, or treat as free goods? | await bill (`EXCESS_OVER_BILL` case open); a manager may resolve it `ACCEPT_FREE_OF_CHARGE`, recorded on the case only — the posted GRN line is never edited (`RQP-UNR-01`) | FR-520 |
| **OD-29** | Requisition approval: one level, or a value-based multi-level matrix? | one level (department head or any holder of `:approve`), plus an optional second level when the requisition's estimated value exceeds `warehouse.stores.requisition_second_approval_value` (null = off) | FR-530 |

## 12. What this area deliberately does not do (refusals, `RM-043`)

| # | Not building | Who has it | Why not | Re-entry path |
|---|---|---|---|---|
| 1 | **Debit notes, credit notes, supplier bill booking, GRNI** | accounting | deferred by the user (`RN-054`) | §8 handover points; an accounting adapter reads them |
| 2 | **PR, RFQ, quotation comparison, award, rate contract, PO amendment workflow, approval matrix for POs** | `warehouse-trade` (`FRD-TRADE`) | `RN-053` | the `FR-504` port |
| 3 | **Production-order issue, backflush, WIP, FG receipt, MRP** | `warehouse-manufacturing` (`FRD-MFG`) | `RN-053` | cost object `PRODUCTION_ORDER` (`FR-533`) and QC source (`FR-525`) |
| 4 | **Switching rules (normal/tightened/reduced), dynamic skip-lot, variables sampling (IS 2500-2 / ISO 3951), SPC charts** | SAP QM (dynamic modification rules), dedicated QMS | need lot history per item × supplier and a statistics engine; the client asked only for bands | an `inspection_level_history` table fed by completed inspections; `SKIP_LOT` stays as a plan type with today's meaning |
| 5 | **Automatic supplier return on QC reject** | — | `FR-139` (amended): a return is a commercial act needing a person | the manual action `FR-526` |
| 6 | **Automatic purchase requisition from a requisition shortfall or reorder point** | `warehouse-trade` may | an automatic PR from stores would bypass the buyer | the hand-off `FR-528`, invoked by a person |
| 7 | **A gate pass that posts stock** | — | `STO-D4` | link the posting document |
| 8 | **Visitor management, employee gate attendance, vehicle yard scheduling** | HR / security products; dock appointments are `P3-05` | not stores | `P3-05` for dock slots |
| 9 | **Weighbridge device integration** | `P5-17` owns the instrument | P8 only links a weighing record | `P5-17` |
| 10 | **Editing or reversing a posted store issue** | — | `STO-D11` | store return + new issue |
| 11 | **Requisition of non-stock services** | `warehouse-trade` (service PR) | stores issue only stock items | trade |
| 12 | **Mobile screens** | — | `D-16` item 7 | none |
| 13 | **Returnable tracking of stock lent inside the company (tool crib custody per person)** | `assets` consumable issuance | a tool crib is custody, not consumption | a later `TOOL_CRIB` cost object with a custody location |

## 13. Sources (web research, 2026-10-22)

- IS 2500 (Part 1) adoption of ISO 2859-1, code letters by lot size and level: [InfraLens IS 2500-1:2017](https://infralens.in/code/IS-2500-Part-1-2017), [qualityinspection.org — inspection levels](https://qualityinspection.org/inspection-level/), [Global Sources — AQL table](https://www.globalsources.com/knowledge/aql-table/).
- SAP has no standard gate pass; RGP/NRGP built over material documents and custom transactions: [SAP Community thread](https://archive.sap.com/discussions/thread/1165497), [BSPTCL NRGP manual](https://bsptcl.in/ERP/MM/Gate_pass_Non_Returnable.pdf), [Deendayal Port gate pass](https://www.deendayalport.gov.in/wp-content/uploads/2022/11/23Aug2021050643PM.pdf).
- SAP QM dynamic modification (skip-lot, normal/reduced stages): [SAP Learning — Setting up Dynamic Modification](https://learning.sap.com/learning-journeys/configuring-sap-s-4hana-quality-management/setting-up-dynamic-modification), [SAPinsider — DMR](https://sapinsider.org/dmr-leads-to-more-efficient-procurement-and-production-processes/).
- Odoo quality control points (all / percentage / periodic; per quantity): [Odoo 13 control points](https://www.odoo.com/documentation/13.0/applications/inventory_and_mrp/quality/control/control_points.html), [Cybrosys — Odoo 18 QC](https://www.cybrosys.com/blog/overview-of-manufacturing-quality-check-in-odoo-18).
- Tally Prime material in/out and job-work registers: [Tally — Job Work](https://help.tallysolutions.com/tally-prime/inventory/job-work/).
