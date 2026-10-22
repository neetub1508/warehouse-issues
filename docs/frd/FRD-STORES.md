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
| **Gate security** | a person | Records gate entries and gate-outs; never receives, never inspects. Permission `wh_gate_entries:create` / `:gate_out`, `wh_gate_passes:gate_out` / `:record_return` only (plus the `:view:branch` scope verb, §4) |
| **Stores receiving clerk** | a person | Gate-in to receiving session, GRN with bill fields, prepares the MRN (maker) |
| **QC inspector** | a person | Incoming inspection, sampling results, disposition; raises the supplier return (maker) |
| **Stores in-charge / MRN authoriser** | a person | Authorises the MRN (checker), approves gate passes, approves accept-excess |
| **Department requester** | a person | Raises material requisitions and store returns for a department or cost centre; sees only own department's documents |
| **Department head / requisition approver** | a person | Approves requisitions of the departments they head; may not approve their own |
| **Stores issue clerk** | a person | Picks and posts store issues against approved requisitions; posts store returns |
| **Production planner** | a person (MFG) | Raises requisitions against a production order through MFG; reads requisition and issue status |
| **Buyer** | a person (TRADE) | Owns POs created through the port; receives the back-to-back PR hand-off |

Maker ≠ checker everywhere a row says *approve* or *authorise*: a **service check against the stored actor**
(`FR-408`, `P2-23`), never a UI gate, refused **`403 <DOCUMENT>_SELF_APPROVAL`** — the convention core already
uses (`SUPPLIER_RETURN_SELF_APPROVAL`, `WhSupplierReturnValidationService.java:40`, and nine siblings):
`GATE_PASS_SELF_APPROVAL` (approve, extend, close short), `GRN_EXCESS_SELF_APPROVAL`, `EXCESS_CASE_SELF_RESOLUTION`,
`MRN_SELF_APPROVAL` (authorise, reject), `REQUISITION_SELF_APPROVAL`, `STORE_RETURN_SELF_APPROVAL` (post by the
submitter); `MRN_AUTHORISER_IS_INSPECTOR` stays a separate rule (R29 F26). The existing PO code
`PO_APPROVER_IS_SUBMITTER` (409, `WhPurchaseOrderValidationService.java:56`) is untouched.

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
- **Every new resource carries the warehouse scope pair `:view:all` / `:view:branch`** (`V511000:60-71`) in its
  seed: without it `WhbWarehouseScopeService.java:133-141` resolves `NONE` and a non-admin sees nothing.
  ADMIN and AUDITOR hold `:view:all`, Branch Admin and the operational bundles `:view:branch`, Branch Admin never
  `:view:all`. Department visibility on requisitions, issues and returns is a **separate verb**,
  `:view_all_departments` — never `:view:all`, which means *every site* (R29 F1).
- **Migration order (R29 F2).** Every P8 **schema** migration sorts above the live high-water mark of its band in
  `classic` (2026-10-22: `warehouse` `V511308`, `warehouse-base` `V501227`): app schema `V511310`…`V511323`, base seeds
  `V501230`…`V501235`, app seeds `V511400`…`V511416`. A rebuilt database and an upgraded one therefore apply P8 in
  the same order (base first, then app schema, then app seeds; out-of-order is `true`, `shared/docker/docker-compose.yml:99`),
  and `V511311` meets the demand-order idempotency index of `V511303` already created. `V511309` and
  `V501228`…`V501229` are left unused as a buffer for `P7` fixes.
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
| **FR-502** | A PO line may carry **schedule lines** (`wh_purchase_order_schedule_lines`): schedule number, delivery date, quantity, kind `FIRM` or `FORECAST`, received / cancelled quantity, status. **Only a `FIRM` schedule line is receivable.** A `FIXED` line's schedule lines must sum to its ordered quantity; a `BLANKET_RELEASE` line's ordered quantity *is* the sum of its firm lines and is **NULL while no line is firm** (a blanket created with only forecast lines saves — R29 TP-F1); an `OPEN` line's received quantity is bounded by the sum of its firm lines. A schedule line may carry its own **release price** (`unit_price`, null = the line rate); the GRN values each allocation at it (R29 TP-F14). Every reader of ordered quantity goes through `effectiveOrderedQuantity()` (ordered for `FIXED`, Σ firm otherwise) and an `OPEN`/`BLANKET_RELEASE` header never rolls up to `RECEIVED` before it is closed (R29 F7). On an **approved** `OPEN` PO, a stores user holding `wh_purchase_orders:release_schedule` may add, firm and close-short schedule lines when no `PurchaseOrderChangeGuard` refuses — so a core-only install can call off (R29 F6). `valid_to` is the **last release date**; firm released quantity stays receivable after it until the optional `receipt_cutoff_date` (R29 TP-F15) | app | v1.1 | P8 | `RM-005` |
| **FR-503** | A receipt against a scheduled line is **allocated to schedule lines oldest-date-first** inside the PO line's tolerance, recorded on a junction (`wh_goods_receipt_line_schedule_allocations`), so one GRN line can satisfy two schedule lines and a schedule line can be satisfied by two GRNs. A delivery earlier than `scheduled_date − warehouse.receiving.early_delivery_days` is refused `409 SCHEDULE_DELIVERY_TOO_EARLY` when the setting is set | app | v1.1 | P8 | `RM-005` |
| **FR-504** | Core publishes the **purchase-order port** (`ai.warehouse.port.purchase.WhPurchaseOrderPort`): create an order of any type, release (add or firm) schedule lines, amend open lines (never below received), cancel a schedule line, close a line or the order. Calls are idempotent on `(source_module, idempotency_key)` with a request fingerprint, **per operation** — every write is recorded in the port operation registry `wh_port_operations` so a replayed release, amend, cancel or close returns its original result (R29 F21); a replay with a different body is refused `409 PORT_IDEMPOTENCY_CONFLICT`. The port authorises the **acting user**, who must hold `warehouse:orders:port` and the operation's core verb (R29 TP-F6; §"Port & seam registry"). `closeOrder` closes every open schedule line and line and takes the PO out of the gate picker (R29 TP-F22); amend never changes the site (`STO-D15`). A PO created through the port records `source_module` / `source_document_*`, and a **`PurchaseOrderChangeGuard` bean collection** lets the source module refuse manual edits, approval or cancel on its own POs. Receipt and closure events go out through the outbox (`FR-436`-shaped) so the buying module updates its drawn-down quantity. No `wh_` table references the buying module | app | v1.1 | P8 | `RN-053` R28 §6 "a published PO-creation port, plus a PO contributor/guard seam" |

### 6.2 Demand-order port for sales (`D1`)

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-505** | Core publishes the **demand-order port** (`ai.warehouse.port.demand.WhDemandOrderPort`), the sales mirror of `FR-504`: create a demand order (`demand_type` from the `DEMAND_TYPE` list, default `SALES`), release schedule lines, amend, cancel. Each order records `source_module`, `source_document_*`, the **sales-order reference** and the **customer PO reference**; idempotent exactly as `FR-504`; a `DemandOrderChangeGuard` bean collection refuses manual edits on port-owned orders A demand line may also carry a **customer delivery schedule** (`wh_demand_order_schedule_lines`): requested date, quantity, `FIRM`/`FORECAST`, shipped / cancelled quantity; **only firm quantity due within `warehouse.outbound.schedule_allocation_horizon_days` is allocatable**, a forecast line never reserves stock, and a **schedule-driven** line's `ordered_quantity` equals the sum of its firm schedule lines — **0 is allowed for a schedule-driven line** (forecast only, or an `OPEN` SO with no call-off yet), replacing the `ordered_quantity > 0` CHECK `V510040:319` with `ordered_quantity > 0 OR (is_schedule_driven AND ordered_quantity >= 0)` (R29 F3, TS-F1). The port firms, un-firms and cancels **one** schedule line (R29 TS-F15); an amend never takes ordered below allocated + cancelled + backordered (cumulative, R29 F18); a schedule-driven order's header returns to `OPEN` after each despatch until the source closes it for release (`OD-45`, R29 TS-F2). Core publishes the **ATP query** `WhAvailableToPromiseQuery` the selling module reads for dispatch planning (R29 TS-F11) | app | v1.1 | P8 | `RN-053` `D1` |
| **FR-506** | Core publishes the **RMA-creation port** (`ai.warehouse.port.returns.WhRmaPort`: `createRma`, `cancelRma`, `getRmaPosition`) so a sales-return authorisation in the selling module creates the core RMA (`wh_rmas` / `wh_rma_lines`, `V510050`) through `WhRmaService.create` (`:186`) — idempotent on `(source_module, idempotency_key)` with a fingerprint, recording `source_module` / `source_document_*`, and guarded by an `RmaChangeGuard` bean collection against manual edits of port-owned RMAs. A port RMA is created **`APPROVED`** by default with the source's approver (R29 TS-F21); every port line names its original demand-order line (`wh_rma_lines.original_demand_order_line_id`, R29 F13) for the shipped-quantity ceiling; core's RMA statuses are exactly `OPEN`, `APPROVED`, `MATCHED`, `EXPIRED`, `CANCELLED` and are published as outbox events for the selling module to map (R29 TS-F3). A **supplier return** carries an **intent** (code list `SUPPLIER_RETURN_INTENT`: `REPLACE`, `CREDIT`, `NO_ACTION`; default `NO_ACTION`) set at create and frozen at approval; dispatch emits outbox `WH_SUPPLIER_RETURN_DISPATCHED` with intent, PO/GRN origin, item, lot and quantity, so the buying module reinstates open PO quantity for `REPLACE` through `WhPurchaseOrderPort.amendOrder` / `releaseSchedule` — core never reinstates quantity itself, and `CREDIT` is an accounting handover point only | app | v1.1 | P8 | TRADE `OD-33` (`FR-612`, `FR-613`) |

### 6.3 Gate entry and gate pass (`B1`, `D3`; `RM-007`, `RM-024`)

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-507** | A **gate entry register** (`wh_gate_entries`) records every vehicle or hand-carried consignment crossing the site gate, **inward or outward**, with a gapless gate-entry number (`GE` series, per site), timestamp in, timestamp out, direction, purpose (code list `GATE_PURPOSE`: `PURCHASE_RECEIPT`, `RETURNABLE_IN`, `SUPPLIER_RETURN_OUT`, `SALES_DISPATCH`, `JOB_WORK_OUT`, `JOB_WORK_IN`, `RGP_OUT`, `NRGP_OUT`, `CUSTOMER_RETURN_IN`, `OTHER`), party, vehicle number, driver name and mobile, transporter, LR/docket number, and security officer. `entered_at` is stamped by the server and cannot be backfilled (`IRR-23`) — also for a barrier event, whose device time is kept only as `barrier_occurred_at` (R29 F28) | app | v1.1 | P8 | `RM-007` `RM-024` |
| **FR-508** | An **inward** gate entry for a purchase receipt carries the **supplier bill number, bill date, bill type** (`TAX_INVOICE`, `DELIVERY_CHALLAN`, `BILL_OF_SUPPLY`, `OTHER` — code list `SUPPLIER_DOCUMENT_TYPE`), optional bill amount and e-way bill number, and links **one or more POs and ASNs** at creation (`wh_gate_entry_documents`) — the PO is on the arrival form, not attached afterwards. A PO that is not `APPROVED`/`PARTIALLY_RECEIVED`, belongs to another supplier or another site is refused at the link. The PO picker and every PO search on the gate entry and the GRN match **either** the core `po_number` **or** the supplier-facing number held in `wh_purchase_orders.source_document_ref` (the `warehouse-trade` PO number, TRADE `OD-30`), and both are shown (`poNumber`, `supplierPoNumber`) | app | v1.1 | P8 | `RM-007` |
| **FR-509** | A gate entry may be **turned back** at the gate (no PO, wrong material, documents missing) with a reason; nothing downstream can be created from it. A receiving session for a purchase is created **from** an inward gate entry and copies vehicle, driver, supplier and documents; when `warehouse.gate.entry_required_for_receipt` is true, a GRN against a PO is refused `409 GATE_ENTRY_REQUIRED` unless its session has a gate entry | app | v1.1 | P8 | `RM-007` |
| **FR-510** | A gate entry links a **weighment** — a `wh_weighing_records` row (`P5-17`, `V510213`) with `subject_type = GATE_ENTRY` (the closed `subject_type` CHECK at `V510213:155` is widened) and `subject_id` = the gate-entry number — and shows the net weight beside the **bill weight** (`bill_weight` + UoM captured on the gate entry's bill row, R29 F9); the variance is evaluated once per entry when both the net (gross and tare weighed) and a posted GRN exist, and a difference above `warehouse.gate.weight_variance_percent` raises a `QUANTITY` reconciliation case on that GRN, never a block | app | v1.1 | P8 | R28 brief "weighment link" |
| **FR-511** | A gate entry is **closed by gate-out**: an inward entry closes when the vehicle leaves (stamps `departed_at` on the receiving session too); an outward entry closes only when every linked outward document (shipment, supplier return, job-work challan, gate pass) is in a dispatched state. A gate entry is never edited after close; a correction is a note with an audit row. A boom-barrier **gate event** (`WarehouseGateEvent`, `POST /warehouse/gate-events`) is claimed by a core `WarehouseGateEventHandler` that matches an `ENTRY` to a new or pre-registered gate entry by vehicle number and stamps an `EXIT` as a **gate-out proposal** — the close still runs every guard above | app | v1.1 | P8 | `RM-007` |
| **FR-512** | A **gate pass** (`wh_gate_passes`) authorises material to leave the site: kind `RETURNABLE` (RGP) or `NON_RETURNABLE` (NRGP), party, purpose (code list `GATE_PASS_PURPOSE`: `REPAIR`, `CALIBRATION`, `JOB_WORK`, `TRIAL`, `LOAN`, `SAMPLE`, `SCRAP_SALE`, `SUPPLIER_RETURN`, `OTHER`), expected return date (mandatory for returnable), lines with item **or** free-text description (tools, dies, moulds, gauges, equipment), quantity, UoM, approximate value, and remarks. Gapless `GP` number per site | app | v1.1 | P8 | `B1` `D3` |
| **FR-513** | **A gate pass never moves stock.** A line naming a stock item must reference the document that moves it — a supplier return, a shipment, a store issue, or a `warehouse-india` delivery challan (`whin_delivery_challans`, purposes `REPAIR`/`JOB_WORK`/`APPROVAL`/…) — by `(source_document_type, source_document_id, source_line_id)` (the line identity, R29 F23), resolved by a **`GatePassSourceResolver` bean** (core registers `SUPPLIER_RETURN`, `SHIPMENT`, `STORE_ISSUE`; `warehouse-india` registers `DELIVERY_CHALLAN`; *amended for MFG MD-29:* `warehouse-manufacturing` registers `SUBCONTRACT_DISPATCH` for the generic-path job-work RGP), and that document must be posted/dispatched before gate-out; otherwise the line must be non-inventory (free text). A gate pass for a stock item with no resolvable source document is refused `422 GATE_PASS_STOCK_LINE_UNSOURCED` | app | v1.1 | P8 | `L-1` `D3` |
| **FR-514** | Gate pass lifecycle: `DRAFT` → `APPROVED` (checker, `wh_gate_passes:approve`, ≠ maker) → `OUT` (gate security records gate-out against an outward gate entry) → for RGP `PARTIALLY_RETURNED` → `RETURNED`; `CLOSED_SHORT` with a reason and approval; `CANCELLED` before gate-out. An NRGP is terminal at `OUT`. Returns are recorded line by line against an **inward gate entry** (`wh_gate_pass_returns`) with quantity and condition; returned quantity never exceeds the quantity out | app | v1.1 | P8 | `D3` |
| **FR-515** | An RGP is **overdue** when it is `OUT`/`PARTIALLY_RETURNED` and `expected_return_date` < today in the site's timezone; overdue is computed on read (grid tile, `overdueOnly` filter), and a daily job notifies the approver and the stores in-charge once per pass per `warehouse.gate.rgp_overdue_reminder_days`. An expected return date may be extended (revision with reason, approval) — never silently | app | v1.1 | P8 | `D3` |

### 6.4 GRN against the supplier bill; short and excess (`B2`; `RM-008`…`RM-010`)

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-516** | A GRN carries its **supplier bills** as child rows (`wh_goods_receipt_bills`: bill type, bill number, bill date, amount, e-way bill no., `is_primary`, `is_supplementary`), the primary bill copied from the gate entry and editable only in `DRAFT`; a **supplementary bill** may be appended after post (append-only, audited) and is how an excess is billed (`FR-520`). A bill number already on a **posted** GRN of the same supplier in the same financial year (normalised: trimmed, upper-cased, internal spaces removed) **of another bill group** is refused `409 SUPPLIER_BILL_DUPLICATE` naming the first GRN — every GRN of one gate entry shares the entry's bill and is one group (R29 F24). When `warehouse.receiving.bill_required_for_po_receipt` is true, a PO receipt posts only with a primary bill. A bill date after the receipt date is refused `422 SUPPLIER_BILL_DATE_AFTER_RECEIPT`. `wh_goods_receipts.invoice_matched` (today written by nothing) is set by `P5-10`'s three-way match only | app | v1.1 | P8 | `RM-008` |
| **FR-517** | Each GRN line carries **supplier billed quantity** (new column `supplier_billed_quantity`, accessor `supplierBilledQuantity()`, nullable for a blind receipt), **received quantity** (counted), the existing **free (scheme) quantity**, the existing **dock-rejected quantity** (`rejected_quantity`, landed in `REJECTED` at post), plus **bill short** = max(billed − received, 0) and the excess figures of `grn-bill-match` §1.5, the excess split into **auto-accepted**, **approved** and **refused**. The existing `billedQuantity()`, `overReceivedQuantity()` and `shortQuantity()` (`WhGoodsReceiptLine.java:207-228`, compared to *expected* quantity) are **left unchanged** (R29 F5). QC accept/reject quantities are the inspection's, not the GRN line's | app | v1.1 | P8 | `RM-008` |
| **FR-518** | The **layered-truth chain** gains the bill: *Ordered 100 → Billed 100 → Gate weight ≈ → Received 92 → Accepted 89 → Authorised (MRN) 89*. Every number is stored and shown side by side on WS-077 and on the GRN and MRN prints; none is derived from another (`FR-123` extended) | app | v1.1 | P8 | `RM-008` `FR-123` |
| **FR-519** | **Short receipt** (billed > received at post) opens a `SHORT_SHIPMENT` **supplier claim** in `DRAFT` (`P5-23`, `wh_supplier_claims`) with one line per short GRN line, quantity = short quantity, value at the PO line rate, traced to the GRN line; the clerk submits it. **No debit note is generated** — the claim is the accounting handover point (§8). The claim's suggested quantity and its validation ceiling read billed − received for a line with a bill, expected − received otherwise (R29 F19). Short against the PO (not the bill) keeps today's `QUANTITY` reconciliation case. A short receipt never blocks the post | app | v1.1 | P8 | `RM-009` `RN-054` |
| **FR-520** | **Excess receipt** (received > billed, or received > open PO/schedule quantity; free quantity excluded from both) is resolved per line at post by the frozen arithmetic of `grn-bill-match` §1.5 — excess over the bill and excess over the PO are computed separately and only the part above PO + tolerance needs a decision (R29 F8): **accepted** without approval when inside the resolved over-receipt tolerance (PO line → header → item → site, today's ladder); **accepted with approval** above tolerance only when a second user holding `wh_goods_receipts:approve_excess` approves that line's excess (maker ≠ checker); otherwise **refused** — the refused quantity is never received into stock, is recorded as `excess_refused_quantity` with a reason, and leaves with the vehicle (it appears on the gate-out). Accepted excess over the **bill** opens an **`EXCESS_OVER_BILL`** reconciliation case (new `RECON_CASE_TYPE` row) that stays `OPEN` until resolved `RECORD_SUPPLEMENTARY_BILL` (a supplementary bill row is appended to the GRN; resulting document = the GRN) or `ACCEPT_FREE_OF_CHARGE` (manager; resulting document = the GRN) — the credit-side handover point; no credit note is generated | app | v1.1 | P8 | `RM-010` `RN-054` |

### 6.5 Incoming inspection with configurable sampling (`B3`; `RM-011`)

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-521** | A **sampling scheme** (`wh_sampling_schemes`) is a named, versioned **band table** (`wh_sampling_scheme_bands`): lot-size from, lot-size to (open-ended last band), sample size **or** sample percent, optional acceptance number Ac and rejection number Re. Bands must be **contiguous from 1 with no gap or overlap**, the last band open-ended; a save that leaves any lot size uncovered is refused `422 SAMPLING_BANDS_NOT_CONTIGUOUS` naming the first uncovered size. The client's table (1–1000 → 5; 1001–10000 → 20) is one scheme (`OD-25`). A band with Ac and Re has **`Re = Ac + 1`** so every defective count yields a verdict (R29 F22). A scheme referenced by a completed inspection is copy-on-write: an edit creates a new version row, plans are re-pointed to it in the same transaction, and the inspection keeps the `sampling_scheme_id` (version row) it used; a scheme no active plan uses may be deactivated (R29 F30) | app | v1.1 | P8 | `RM-011` |
| **FR-522** | An inspection plan's `sample_size_formula` gains `BAND_TABLE` (reads the plan's scheme) and the two formulas that today fall back to the whole lot are **fixed**: `FIXED_QUANTITY` reads `wh_inspection_plans.fixed_sample_quantity`, `PERCENTAGE` reads `sample_percent` with an optional `min_sample_quantity`; both are required by the formula they serve (`422 SAMPLE_PARAMETER_REQUIRED`). The hard-coded **ANSI/ASQ Z1.4 general level II** table (`WhQualityInspectionSampleSize.java`) stays as the `AQL_TABLE` option, unchanged, and is equivalent to IS 2500 (Part 1) / ISO 2859-1 normal single sampling at level II. Every size rounds up to whole units and is capped at the lot (`RQP-GRD-20` unchanged) | app | v1.1 | P8 | `RM-011` `RQP-T1-16` open note |
| **FR-523** | A plan is chosen by an **assignment** (`wh_inspection_plan_assignments`) at the most specific matching scope, in this precedence: item + supplier → item → category + supplier → supplier → category → `whb_item_categories.default_inspection_plan_id` (today's rule) → none. Assignments carry effective-from/to and are dated, never overwritten. An assignment may say **`NO_INSPECTION`** (skip QC for a trusted item × supplier) — recorded, so a skipped inspection is a decision and not an absence | app | v1.1 | P8 | `RM-011` |
| **FR-524** | When the plan carries Ac/Re (band table or AQL with an AQL value), Complete **proposes a lot verdict**: defectives ≤ Ac → `ACCEPT_LOT`, ≥ Re → `REJECT_LOT`; the inspector confirms or overrides with a reason, and the verdict drives a **whole-lot disposition** of the QC-held quantity (sample destroyed in testing excluded). **Destructive-test quantity** is recorded per line and posted as an `ISSUE` to `VIRT-CONSUMED-<site>` under the existing QC document type **`QCINSP`**, with cost object `DEPARTMENT` = the site's QC department stored on the inspection line (`FR-533`), so the lot balances (`L-1`) and the consumption register counts it (R29 F11) | app | v1.1 | P8 | `RM-011` |
| **FR-525** | A quality inspection has a **polymorphic source**: `source_type` (code list `QC_SOURCE_TYPE`: `GOODS_RECEIPT`, `STORE_RETURN`, `PRODUCTION_RECEIPT`, `IN_PROCESS`, `STOCK`, `OTHER`), `source_document_id`, `source_line_id`, `source_document_ref`, and an **inspection stage** (code list `INSPECTION_STAGE`: `INCOMING`, `IN_PROCESS`, `FINAL`, `RETURN`, `PERIODIC`). `grn_id` / `grn_line_id` become nullable and are required only when `source_type = GOODS_RECEIPT`. A source type is honoured only when a **`QualityInspectionSourceResolver` bean** for it is registered; core registers `GOODS_RECEIPT`, `STORE_RETURN` and `STOCK`, `warehouse-manufacturing` registers its own. An unregistered source is refused `422 QC_SOURCE_TYPE_UNSUPPORTED`. One inspection series per source document (`FR-133` generalised) **Non-stock-bearing sources (SEAM-M4):** a resolver may declare `stockBearing = false` (MFG `IN_PROCESS`: inspection of a production operation with no stock subject); such an inspection has no held quantity or location, its lines record an **outcome** (code list `INSPECTION_OUTCOME`: `ACCEPT`, `REJECT`, `REWORK`) instead of a disposition, **posts no movement**, never routes to `MRN_PENDING`, and hands the outcome to the resolver's `onDisposition` hook. For a **stock-bearing** sibling source (`PRODUCTION_RECEIPT`) **core posts** the disposition movements and `onDisposition` only reacts (R29 F25) | app | v1.1 | P8 | R28 §6 "QC with a polymorphic source"; SAP QM inspection-lot origin |

### 6.6 QC reject → supplier return; MRN (`B4`, `B5`; `RM-012`, `RM-013`)

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-526** | **Amends `FR-139`.** A completed GOODS_RECEIPT inspection with quantity dispositioned `REJECT` or `RTV` and not yet on a live supplier return offers an explicit **"Raise supplier return"** action. It creates a supplier return in **`DRAFT`** (maker = the user who pressed it), pre-filled with supplier, origin GRN, origin inspection, reason `QUALITY_REJECTED`, and one line per rejected inspection line at its rejected quantity and lot. It never approves, never dispatches and never posts; the ladder `DRAFT → APPROVED → PICKED → DISPATCHED → CLOSED` and its maker/checker are unchanged. **Nothing raises a supplier return automatically** — the refusal in `FR-139` survives as *"no silent auto-return"*. `debit_note_ref` stays a free-text reference; no debit note is generated (`RN-031`, `RN-054`) | app | v1.1 | P8 | `RM-012` `RN-031` |
| **FR-527** | A **material receipt note** (MRN, `wh_material_receipt_notes`) is the stores' authorisation that received and inspected material is taken on charge. When `warehouse.stores.mrn_required` is true for the site: a GRN line received into an allocatable status, and any QC-released quantity, lands in stock status **`MRN_PENDING`** (non-allocatable, non-issuable) with **no putaway task**; the MRN lists, per GRN line, billed / received / accepted / rejected quantity, rate and value from the PO; `DRAFT` → `SUBMITTED` (maker) → `AUTHORISED` (checker holding `wh_material_receipt_notes:authorise`, ≠ maker, ≠ the releasing inspector unless `warehouse.stores.mrn_authoriser_may_be_inspector`) or back to `DRAFT` on reject with reason; `CANCELLED` from `DRAFT`. **Authorise posts one `STATUS_CHANGE` `MRN_PENDING → AVAILABLE` per line and only then creates the putaway task.** Gapless `MRN` series per site. MRN covers every goods receipt — PO, blind and non-PO (R29 F27). With the setting false, today's behaviour holds exactly for new receipts; stock already in `MRN_PENDING` keeps its MRN path, so switching the setting off never strands it (R29 F10), and only an MRN lifts `MRN_PENDING` stock into an allocatable status. **Stock-availability rule:** material is issuable only from an allocatable status, so nothing in `MRN_PENDING`, `QC_HOLD` or `REJECTED` can be requisitioned, reserved, issued or transferred; availability (`FR-174`) excludes it | app | v1.1 | P8 | `RM-013` |
| **FR-528** | Core exposes the **purchase-requisition hand-off port** (`ai.warehouse.port.purchase.PurchaseRequisitionHandoff`, optional bean): a stores user may send a requisition shortfall to the buying module, which returns its document reference; core records the link (`wh_material_requisition_line_handoffs`) and shows the buying document's status by asking the port. With no bean registered (`warehouse-trade` off) the action is not offered — there is no stub that pretends **Supply-request seam for MRP (SEAM-M3):** core also publishes `WhReplenishmentSuggestionPort` (`publishExternal`, `withdrawExternal`, `getSuggestionStatus`, `markConverted`, `releaseConversion` — R29 F14, TP-F18; `withdrawExternal` reports per proposal `WITHDRAWN` / `ALREADY_CONVERTED` / `NOT_FOUND`, and MRP counts converted ones as supply, R29 MFG-F13) so `warehouse-manufacturing` MRP can post BUY proposals as core replenishment suggestions (in `EXTERNAL` runs created directly `COMPLETED`, R29 F12) with origin `MRP` (code list `REPLENISHMENT_ORIGIN`: `REORDER`, `MRP`; `origin_document_type/id`, `need_date`), idempotent per origin proposal. With no `SuggestionConversionOwner` bean (trade off) the core replenishment screen converts them to a **draft core PO** exactly as reorder suggestions (MFG `OD-41`); with trade on, trade's *Raise PR* converts them (TRADE `OD-31`, `FR-557`) and core's convert-to-PO is not offered. Either conversion marks the suggestion `CONVERTED` with its resulting document, so it is never converted twice | app | v1.1 | P8 | `RM-001` hand-off, R28 §4 `A1` seam |

### 6.7 Material requisition, store issue, store return (`B6`, `B7`, `B8`; `RM-015`…`RM-017`, `S-052`)

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-529** | A **material requisition** (indent; `wh_material_requisitions` + lines) asks a store for material: issuing site, requesting **department** (platform `departments`), **cost object** (`FR-533`), purpose (code list `REQUISITION_PURPOSE`: `CONSUMPTION`, `MAINTENANCE`, `PRODUCTION`, `PROJECT`, `CAPITAL`, `SAMPLE`, `OTHER`), requested-by, required-by date, priority, and lines with item, quantity, UoM, required date, remarks. Gapless `MRQ` series per site. A department requester sees and acts only on requisitions of departments they belong to (record-level guard, `P1-18` shape) | app | v1.1 | P8 | `RM-015` |
| **FR-530** | Requisition lifecycle: `DRAFT` → `SUBMITTED` → `APPROVED` / `REJECTED`; `SUBMITTED` → `DRAFT` (recall by the requester); `APPROVED` → `PARTIALLY_ISSUED` → `ISSUED` (effects of issue posts); `APPROVED`/`PARTIALLY_ISSUED` → `CLOSED` (short-close, reason mandatory, the unissued remainder → `closed_quantity`); `DRAFT`/`SUBMITTED`/`APPROVED`-with-nothing-issued → `CANCELLED`. **Approval is per line**: the approver sets `approved_quantity` ≤ requested (zero rejects the line); the approver holds `wh_material_requisitions:approve`, is not the requester, and — when `warehouse.stores.requisition_approver_scope = DEPARTMENT_HEAD` — is the head of the requesting department. Above the `OD-29` value threshold the first and the final approval are two mutually exclusive transitions and a recall clears the first (R29 F16); closing the last open line short ends the header `CLOSED` (R29 F33) | app | v1.1 | P8 | `RM-015` |
| **FR-531** | On approval, per `warehouse.stores.requisition_reservation` (`NONE` / `SOFT` / `HARD`, default `SOFT`) the approved quantity is reserved in the open-item reservation ledger (`P0-09`) with holder `MATERIAL_REQUISITION`/line, **one hold per grain** (location, lot, status); `SOFT` expires after `warehouse.stores.requisition_soft_hold_days`, `HARD` never; a shortfall is topped up by an action and a daily job when stock arrives (R29 F32); issue **consumes and splits** the holds inside its transaction, closure and cancel release them (R29 F4). Reservation never exceeds available; a shortfall is shown per line (`available`, `reserved`, `short`) and computed by the backend. *Amended for MFG MD-16:* when the line's cost-object resolver reports reservations it already holds for the item (`CostObjectResolver.reservationsFor`, `FR-533` — MFG's `PRODUCTION_ORDER` holds its component reservations from release), approval **creates no reservation** — decided by the type's `ownsReservations()` (R29 MFG-F12), never by whether holds happen to exist: the line shows the owner's reserved quantity, the store issue consumes the owner's reservations, and close/cancel release nothing (the owner releases its own). A requisition for a production order is created by MFG through **`WhMaterialRequisitionPort`** (`create`/`cancel`/`close`, `p8-09`) | app | v1.1 | P8 | `RM-015` |
| **FR-532** | **Partial issue** is normal: a line is issued over any number of store issues until issued = approved or it is closed. A requisition line short of stock may be **handed off as a back-to-back purchase requisition** (`FR-528`) for the short quantity; the hand-off does not change the requisition's status, and the received material is issued against the same requisition when it arrives | app | v1.1 | P8 | `RM-015` `RM-001` |
| **FR-533** | Every **store-issue line carries a cost object** — `cost_object_type` (code list `COST_OBJECT_TYPE`: `DEPARTMENT`, `COST_CENTRE`, `PRODUCTION_ORDER`, `WORK_ORDER`, `MACHINE`, `PROJECT`), `cost_object_id`, `cost_object_ref` (frozen display code) — defaulted from the requisition line, else the header, never null. A type is accepted only when a **`CostObjectResolver` bean** for it validates the id (core: `DEPARTMENT` → platform `departments`, `COST_CENTRE` / `MACHINE` / `PROJECT` → `wh_cost_centres` of that kind, `WORK_ORDER` → `wh_work_orders` — five core resolvers, R29 F34; `warehouse-manufacturing`: `PRODUCTION_ORDER`). **The cost object lives on the issue document's lines, referenced from the movement by `source_document_type`/`source_document_id`; the ledger gains no column** (`RN-034` resolves `S-052`). The `COST_CENTRE` resolver reads a thin **cost-centre master** (`wh_cost_centres`: code, name, kind `COST_CENTRE`/`MACHINE`/`PROJECT`, department, parent, is_active, `external_ref` for a future accounting dimension) — a warehouse master, not an accounting dimension, until accounting is built (`OD-27`) **Resolver contract (SEAM-M1, SEAM-M2):** `ResolvedCostObject` carries `counterLocationPurpose` (default `CONSUMED`; MFG's `PRODUCTION_ORDER` resolver returns `PRODUCTION`, so the issue lands in WIP `VIRT-PRODUCTION-<site>`, not expense); and the resolver exposes default hooks `assertIssuable(costObjectId, itemId, baseQty)` (before post, may refuse), `onIssuePosted(line)` and `onReturnPosted(line)` called **inside** the posting transaction (a hook failure rolls the post back). There is **no `onIssueReversed`** hook: a posted store issue is never reversed (`STO-D11`); its correction is a store return, which fires `onReturnPosted`. *Amended for MFG MD-16:* a default `reservationsFor(costObjectId, itemId)` (empty by default) names reservations the cost object already holds, consumed by the issue instead of a requisition reservation (`FR-531`). *Amended for MFG MD-14:* MFG's `PRODUCTION_ORDER` resolver accepts an order `RELEASED`, `IN_PROGRESS` or `COMPLETED` (technically complete, not yet settled — late issues and returns flow into the settlement), and refuses one `PLANNED`, `CANCELLED`, `CLOSED`, on hold, or with a settlement awaiting approval | app | v1.1 | P8 | `S-052` `RN-034` `RM-016` |
| **FR-535** | A **store issue** (`wh_store_issues` + lines + serials) issues stock against an approved requisition (or, with `wh_store_issues:issue_without_requisition` and `warehouse.stores.direct_issue_allowed`, directly) from a named location, lot, serial and status `AVAILABLE`; issued quantity per line ≤ approved − issued − closed on the requisition line. **Post** writes one balanced **`ISSUE`** movement per document through the single writer: −quantity at the store location, +quantity at **`VIRT-<counterLocationPurpose>-<site>`** (`VIRT-CONSUMED` by default, `VIRT-PRODUCTION` for a production order — `FR-533`), `source_document_type = STORE_ISSUE`, `source_document_id` = the issue; valued at the movement's cost (weighted average / FIFO per item, `P0-17`). The receiver (user or name) and acknowledgement time are recorded. Gapless `SIS` series. A posted issue is never edited or reversed; a correction is a store return plus a new issue | app | v1.1 | P8 | `RM-016` |
| **FR-536** | A **store return** (`wh_store_returns` + lines) brings unused material back from a department: every line names the **store-issue line** it returns, quantity ≤ issued − already returned on that line (`422 STORE_RETURN_EXCEEDS_ISSUED`), condition (code list `RETURN_CONDITION`: `GOOD`, `NEEDS_INSPECTION`, `DAMAGED`, `SCRAP`), reason (reason context `STORE_RETURN`). The cost object is **inherited** from the issue line and cannot be changed. Lifecycle `DRAFT` → `SUBMITTED` (department) → `POSTED` (stores, after physical receipt) or `REJECTED` (stores refuses, reason); `CANCELLED` from `DRAFT`/`SUBMITTED`. Gapless `SRN` series | app | v1.1 | P8 | `RM-017` |
| **FR-537** | Posting a store return writes one balanced **`ISSUE_RETURN`** movement (new seeded type, `IN`, mirror of `ISSUE`): −quantity at the **same virtual location the issue line posted to** (`VIRT-CONSUMED` or `VIRT-PRODUCTION`), +quantity at the return location, **valued at the original issue line's unit cost**, in status by condition: `GOOD` → `AVAILABLE` (putaway task created), `NEEDS_INSPECTION` → `QC_HOLD` with an inspection of source `STORE_RETURN` opened, `DAMAGED` → `DAMAGED`, `SCRAP` → `DAMAGED` then the normal scrap approval. The issue line's `returned_quantity` and the requisition line's `returned_quantity` move in the same transaction; a requisition never reopens | app | v1.1 | P8 | `RM-017` |

### 6.8 Prints and registers

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-534** | **Plant-stores performance benchmarks** (replaces the withdrawn dealer `FR-422` for this segment), each measured from stored timestamps — never typed — per site × period with median, P90 and the share inside a target set per site (`warehouse.stores.kpi_target_*`): **gate-to-GRN time** (`wh_gate_entries.entered_at` → GRN `received_at`/post), **GRN-to-MRN time** (GRN post → MRN `authorised_at`), **QC lead time** (GRN post / QC-hold entry → inspection `completed_at` → disposition), **issue turnaround** (requisition `approved_at` → first and last store-issue `posted_at`; plus fill rate = issued ÷ approved at closure), **store-return cycle** (return `submitted_at` → `posted_at`, and issue → return elapsed), and **dock-to-stock** (GRN post → putaway completion, `dock_to_stock_completed_at`). Shown on a *Stores performance* tab of WS-277 with drill-down to the documents; definitions are frozen as KPI rows (`FR-395`-style, the `P2-21` frozen-definition rule) — eight rows, version 1, seeded by `P8-13` in `V511412` — so a definition change is a new KPI version (R29 F31) | app | v1.1 | P8 | `FR-422` (withdrawn, SPINE) · CAT-26 |
| **FR-538** | Seven **system print templates** (`PRINT_TEMPLATE_KIND` rows and `SYS-` templates through `P2-14`'s framework): `GATE_ENTRY` slip, `GATE_PASS` (RGP/NRGP, with signatures of maker, approver, security and receiver), `GRN`, `MRN` (with authoriser and time), `MATERIAL_REQUISITION`, `STORE_ISSUE` slip (with receiver acknowledgement), `STORE_RETURN` note. The GRN detail (WS-077) and the MRN detail (WS-267) gain a **Print** action — today the GRN page has none although `SYS-GRN` exists (`V510060:323`). A print is allowed from the states the contract names; a reprint is marked *duplicate* (`wh_print_jobs.is_reprint`) | app | v1.1 | P8 | `RM-013` CAT-23 |
| **FR-539** | Five **stores registers**, backend-filtered and exportable, each a tab of WS-277 (R29 F31): gate register (inward/outward by date), **RGP pending / overdue**, **requisitions pending issue** (approved − issued, ageing by required-by date), **issue register by cost object** (item, quantity, value by department / cost centre / production order for a date range) and **consumption by department** (issues − returns, net). Statistics tiles are filter-aware with no cache name (`FR-395`) **Consumption** counts store issues, QC destructive-test issues (`QCINSP`) and store returns to `VIRT-CONSUMED`; issues to `VIRT-PRODUCTION` (WIP) are listed in the issue register but are not consumption — MFG reports them against the order | app | v1.1 | P8 | CAT-24 `S-052` |

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
| **WH-SC-436** | `stores1` raised the RGP | `stores1` approves it | refused `403 GATE_PASS_SELF_APPROVAL` | FR-514 | — | app | v1.1·P8 | negative |
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
| **WH-SC-459** | `req1` approves own requisition | — | refused `403 REQUISITION_SELF_APPROVAL` | FR-530 | — | app | v1.1·P8 | negative |
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
| **STO-D12** | New P8 schema lands as **new migrations** (`V511310`…`V511323` app, `V501230`…`V501235` base, `V511400`…`V511416` seeds) after `P7`'s one rebuild — never as edits of the rebuilt files — and every one sorts above its band's live high-water mark (§4, R29 F2) | `RN-052` allows one rebuild; P8 lands on a rebuilt DB that must not be rebuilt again; a fresh and an upgraded database must apply P8 in one order |
| **STO-D14** | An `OPEN` PO line keeps `unit_price > 0`; a free-of-charge `OPEN` line is refused by core and by trade at submit (R29 TP-F19) | an `OPEN` PO is a rate agreement with no quantity; a zero rate has no meaning there — free goods are a `FIXED` line or scheme free quantity |
| **STO-D15** | A port amend never changes a PO's or demand order's **site**; a *deliver-to* change is a receiving location inside the same site; another site is cancel + new order (R29 TP-F24) | stock, series, scope and tolerance are all per site; moving an order across sites would re-key every one |
| **STO-D16** | Two visibility axes, two verbs: `:view:all`/`:view:branch` is the **site** pair on every new resource; `:view_all_departments` is the **department** axis on requisitions, issues and returns (R29 F1) | reusing `:view:all` for departments opened every site to whoever needed department-wide sight |
| **STO-D17** | One port **operation registry** (`wh_port_operations`) for every port write of every core port, keyed `(source_module, operation, idempotency_key)` (R29 F21) | header idempotency columns can replay only the create; a replayed release, amend or cancel must return its original result |
| **STO-D18** | **Core consumes every reservation a store issue uses**, including owner-held (MFG) ones, with consume-and-split in the issue transaction; whether a requisition reserves is decided by the cost-object type's `ownsReservations()` (R29 F4, MFG-F12) | a reservation row closes whole (`WhbReservationStore.java:232`); one owner of the consume call keeps partial issues balanced |

## 11. Open decisions (OD-25…OD-29, OD-45)

| # | Question | Safe default (built unless the user decides otherwise) | Requirements blocked |
|---|---|---|---|
| **OD-25** | The client's bands read *"1–1000 → 5, 1–10000 → 20"*: overlapping as written. Read as contiguous `1–1000 → 5`, `1001–10000 → 20`? And what sample above 10,000? | contiguous reading; the seeded `CLIENT-DEFAULT` scheme carries a third open band `10001+ → 32` marked *to confirm*; the save rule (`FR-521`) forces every install to state one | FR-521 (seed only) |
| **OD-26** | Is the MRN step on by default for a new manufacturing site? | `warehouse.stores.mrn_required = true` for new sites of type production store/raw-material store, `false` otherwise; per-site override | FR-527 |
| **OD-27** | Cost centres: a thin warehouse master now, or wait for accounting dimensions? | thin `wh_cost_centres` with `external_ref`; when accounting arrives, an adapter maps `external_ref` to its dimension — no migration of issue lines | FR-533 |
| **OD-28** | Accepted excess over the bill: await a supplementary bill, or treat as free goods? | await bill (`EXCESS_OVER_BILL` case open); a manager may resolve it `ACCEPT_FREE_OF_CHARGE`, recorded on the case only — the posted GRN line is never edited (`RQP-UNR-01`) | FR-520 |
| **OD-29** | Requisition approval: one level, or a value-based multi-level matrix? | one level (department head or any holder of `:approve`), plus an optional second level when the requisition's estimated value exceeds `warehouse.stores.requisition_second_approval_value` (null = off) | FR-530 |
| **OD-45** | *(raised by R29 TS-F2; the STORES range `OD-25`…`OD-29` is full, so the next unallocated id is used — SPINE to confirm.)* A blanket or open sales order runs for months, but the core demand-order header ships the whole order and then goes terminal (`WhDemandOrderService.java:892-905` ships only when every line is fully accounted; `DELIVERED` is terminal, `WhDemandOrder.java:101`). **(A)** one core demand order per sales order whose header **rolls up from its schedule lines**: a schedule-driven order returns to `OPEN` after each despatch and is never `SHIPPED`/`DELIVERED` while the source can still release, until the port's `closeDemand`; or **(B)** one core demand order **per firm release**, the forecast staying in the selling module (then MRP's forecast source and TRADE's one-order symmetry change) | **(A), recommended and built**: TRADE (`TSO-T4-01`, `p9-09`) and MFG (`MRP-N-03`, TRADE `OD-32` confirmed) already rely on one core order per SO carrying `FORECAST` lines; (A) changes only the header rule for `is_schedule_driven` orders (`POS-T1-12a`, `-12b`) and leaves every other order's ladder untouched; (B) would move the forecast out of core and break both siblings' reads. Per-shipment proof of delivery keeps working, because POD is recorded on the shipment | FR-505 |

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

## Port & seam registry (authoritative)

This section is the **one source of truth** for every port (core-implemented, sibling-called) and SPI
(sibling-implemented, core-called) that P8 publishes. `FRD-TRADE`, `FRD-MFG` and their contracts align to it;
where any other document names a method, a signature or an event differently, **this table wins** and the
other document is corrected. Rows cite the contract row that specifies the behaviour.

### R.1 Rules that apply to every port

| Rule | Statement |
|---|---|
| **Envelope** | every port **write** takes a command that carries `PortEnvelope(String sourceModule, String idempotencyKey, UUID actingUserId)`; reads take ids only |
| **Principal** | core authorises `actingUserId`: it must hold **`warehouse:orders:port`** and the operation's core verb (column *Verb* below), else `403 PORT_AUTHORITY_REQUIRED` (`POS-GRD-13`). Core seeds `warehouse:orders:port` (`V511400`) with `permission_dependencies` granting the verbs below; each sibling grants `warehouse:orders:port` to its own approver / planner bundles in its own seed. A SYSTEM-approved sibling document calls with `actingUserId` = its submitter and `approvedByUserId` = null |
| **Idempotency** | one `wh_port_operations` row per write, uk `(source_module, operation, idempotency_key)`, with the SHA-256 `request_fingerprint` of the canonical JSON body and the recorded result (`target_type`, `target_id`, `result_revision_no`, `result_code`). Same key + same fingerprint → the recorded result, nothing re-executed, `replayed = true`; same key + other fingerprint → `409 PORT_IDEMPOTENCY_CONFLICT` (`POS-GRD-07`, `STO-D17`). Recommended key shape: `<SOURCE_DOCUMENT_TYPE>:<id>:<operation>:<sequence>` |
| **Transport** | in-process Java interface **and** a REST mirror under `/warehouse/ports/...` (`@PreAuthorize("hasAuthority('warehouse:orders:port') and hasAuthority('<verb>')")`); one service, no second write path (`POS-UNR-05`) |
| **Transaction** | a port write joins the caller's transaction (`Propagation.REQUIRED`); a refusal is a runtime exception that rolls the caller back |
| **Guards** | a change guard SPI is a bean collection, empty when the sibling is off; core asks every bean before a **manual** change of a document whose `source_module` is set: `Optional<GuardRefusal> check(<DocumentRef> ref, <ChangeKind> change)` with `GuardRefusal(String code, String message)`; core raises `409 <code>` and hides the action when a bean would refuse |
| **Events** | outbox (`P0-11`, `FR-436`-shaped), each carrying `source_module`, `source_document_type`, `source_document_id`, `source_document_ref` of the core document so the sibling matches its own record |
| **FKs** | none upward (`D-16` item 5); sibling ids are bare UUIDs |

### R.2 Ports core implements

| Port · package | Method (signature) | Verb | Operation key | Events | Contract |
|---|---|---|---|---|---|
| **`WhPurchaseOrderPort`** · `ai.warehouse.port.purchase` | `PurchaseOrderResult createOrder(CreatePurchaseOrderCommand c)` — `c`: envelope, `sourceDocumentType/Id/Ref`, `poType`, `supplierCounterpartyId`, `warehouseId`, `ownerId`, `currencyCode`, `validFrom`, `validTo`, `receiptCutoffDate`, `agreementRef`, `initialStatus` (`DRAFT`/`APPROVED`), `approvedByUserId`, `lines[]` (`lineRef`, `itemId`, `uomCode`, `orderedQuantity` (null for `OPEN`/`BLANKET_RELEASE`), `unitPrice`, `rateSource`, `rateSourceRef`, `agreementLineRef`, `expectedDeliveryDate`, `schedule[]` (`kind`, `scheduledDate`, `quantity`, `unitPrice`?, `releaseRef`)) | `wh_purchase_orders:create` | `PO_CREATE` | — | `POS-T1-01`, `-05` |
| | `PurchaseOrderResult releaseSchedule(ReleaseScheduleCommand c)` — `poId`, `releaseRef`, `entries[]`: either `firm(scheduleLineId)` or `add(poLineId, kind, scheduledDate, quantity, unitPrice?)` | `:edit` | `PO_RELEASE` | `WH_PO_SCHEDULE_RELEASED` | `POS-T1-02`, `-03`, `-06` |
| | `PurchaseOrderResult amendOrder(AmendPurchaseOrderCommand c)` — `poId`, `expectedRevisionNo`, `amendmentReason`, `lineChanges[]` (`poLineId`, `orderedQuantity`?, `unitPrice`?, `expectedDeliveryDate`?, `receivingLocationId`?), `scheduleChanges[]` (`scheduleLineId`, `quantity`?, `scheduledDate`?, `unitPrice`?), `newLines[]`, `validTo`?, `receiptCutoffDate`? | `:edit` | `PO_AMEND` | `WH_PO_AMENDED` | `POS-T1-07`, `POS-GRD-09` |
| | `PurchaseOrderResult cancelScheduleLine(CancelScheduleLineCommand c)` — `scheduleLineId`, `reasonCodeId`, `note` | `:edit` | `PO_CANCEL_SCHEDULE` | `WH_PO_AMENDED` | `POS-T1-09` |
| | `PurchaseOrderResult closeLine(ClosePurchaseOrderLineCommand c)` — `poLineId`, `reasonCodeId`, `note` | `:edit` | `PO_CLOSE_LINE` | `WH_PO_AMENDED` | `POS-T1-08` |
| | `PurchaseOrderResult closeOrder(ClosePurchaseOrderCommand c)` — `poId`, `reasonCodeId`, `note` | `:edit` | `PO_CLOSE` | `WH_PO_CLOSED` | `POS-T1-08` |
| | `PurchaseOrderResult cancelOrder(CancelPurchaseOrderCommand c)` — `poId`, `reasonCodeId`, `note` | `:edit` | `PO_CANCEL` | `WH_PO_CANCELLED` | `POS-T1-08` |
| | `PurchaseOrderReceiptPosition getReceiptPosition(UUID poId)` — header status, revision, per line effective ordered / received / remaining, per schedule line kind / date / qty / received / cancelled / status / price | `:view` | — (read) | — | `POS-T4-02` |
| | *result* `PurchaseOrderResult(UUID poId, String poNumber, String status, int revisionNo, boolean replayed)` | | | receipt-side: `WH_PO_LINE_RECEIVED`, `WH_PO_SCHEDULE_LINE_RECEIVED` | `POS-T4-04` |
| **`WhDemandOrderPort`** · `ai.warehouse.port.demand` | `DemandOrderResult createDemand(CreateDemandCommand c)` — envelope, `sourceDocumentType/Id/Ref`, `demandType` (default `SALES`), `customerCounterpartyId`, `warehouseId`, `ownerId`, `salesOrderRef`, `customerPoRef`, `customerPoDate`, `fulfilmentPolicy`, `lines[]` (`lineRef`, `itemId`, `uomCode`, `orderedQuantity` (ignored for a schedule-driven line), `unitPrice`, `requiredDate`, `schedule[]` (`kind`, `requestedDate`, `quantity`, `releaseRef`)) | `wh_demand_orders:create` | `DEMAND_CREATE` | — | `POS-T1-10` |
| | `DemandOrderResult releaseSchedule(ReleaseDemandScheduleCommand c)` — `demandOrderId`, `releaseRef`, `entries[]` (`demandLineId` or `lineRef`, `kind`, `requestedDate`, `quantity`) | `:edit` | `DEMAND_RELEASE` | `WH_DEMAND_AMENDED` | `POS-T1-11` |
| | `DemandOrderResult firmScheduleLine(DemandScheduleLineCommand c)` · `unfirmScheduleLine(…)` · `cancelScheduleLine(…)` — `scheduleLineId` **or** `(demandLineId, releaseRef)`, `reasonCodeId`? (un-firm, cancel) | `:edit` | `DEMAND_FIRM` / `DEMAND_UNFIRM` / `DEMAND_CANCEL_SCHEDULE` | `WH_DEMAND_AMENDED` | `POS-T1-11a`…`-11c` |
| | `DemandOrderResult amendDemand(AmendDemandCommand c)` — `demandOrderId`, `expectedRevisionNo`, `amendmentReason`, line / schedule changes | `:edit` | `DEMAND_AMEND` | `WH_DEMAND_AMENDED` | `POS-T1-12`, `POS-GRD-09` |
| | `DemandOrderResult cancelLine(CancelDemandLineCommand c)` · `cancelDemand(CancelDemandCommand c)` | `:edit` | `DEMAND_CANCEL_LINE` / `DEMAND_CANCEL` | `WH_DEMAND_AMENDED` / `WH_DEMAND_CANCELLED` | `POS-T1-12` |
| | `DemandOrderResult closeDemand(CloseDemandCommand c)` — close a schedule-driven order for release (`OD-45`) | `:edit` | `DEMAND_CLOSE` | `WH_DEMAND_AMENDED` | `POS-T1-12a` |
| | `DemandFulfilmentPosition getFulfilmentPosition(UUID demandOrderId)` | `:view` | — | despatch: `WH_DEMAND_SHIPPED` (per schedule line `release_ref`, shipped qty) | `POS-T4-05`, `-07` |
| | *result* `DemandOrderResult(UUID demandOrderId, String orderNumber, String status, int revisionNo, boolean replayed)` | | | | |
| **`WhAvailableToPromiseQuery`** · `ai.warehouse.port.demand` | `List<AtpRow> atp(AtpQuery q)` — `q`: `warehouseId`, `ownerId`, `itemIds`, `horizonEnd`; `AtpRow(itemId, onHandAllocatable, openReserved, availableNow, firmScheduledReceipts[] (date, quantity))` | `warehouse:orders:port` (read) | — | — | `POS-T4-08` |
| **`WhRmaPort`** · `ai.warehouse.port.returns` | `RmaResult createRma(CreateRmaCommand c)` — envelope, `sourceDocumentType/Id/Ref`, `customerCounterpartyId`, `ownerId`, `warehouseId`, `originalDemandOrderId`, `reasonCodeId`, `expectedConditionCode`, `expiryDate`, `initialStatus` (`APPROVED` default / `OPEN`), `approvedByUserId`, `lines[]` (`originalDemandOrderLineId`, `itemId`, `quantity`, `uomCode`, `lotCode`?, `serialNumber`?) | `wh_rmas:create` | `RMA_CREATE` | — | `POS-T1-20`, `POS-GRD-20`, `-21` |
| | `RmaResult cancelRma(CancelRmaCommand c)` — `rmaId`, `reasonCodeId`, `note` | `wh_rmas:edit` | `RMA_CANCEL` | `WH_RMA_CANCELLED` | `POS-T1-21` |
| | `RmaPosition getRmaPosition(UUID rmaId)` | `wh_rmas:view` | — | effects: `WH_RMA_MATCHED`, `WH_RMA_EXPIRED` | `POS-T1-22`, `-25` |
| *(event only)* supplier-return dispatch | — | — | — | `WH_SUPPLIER_RETURN_DISPATCHED` (intent, origin GRN/PO lines, PO `source_*`, item, lot, qty, movement id) | `POS-T1-24` |
| **`WhReplenishmentSuggestionPort`** · `ai.warehouse.port.replenishment` | `List<SuggestionResult> publishExternal(PublishExternalCommand c)` — envelope, `origin` (`MRP`), `originRunId`, `suggestions[]` (`originDocumentId`, `itemId`, `warehouseId`, `quantity`, `uomCode`, `needDate`, `preferredSupplierId`?) | `wh_replenishment_suggestions:edit` | `SUGGESTION_PUBLISH` | — | `POS-T1-30`, `POS-GRD-30`, `-31` |
| | `List<WithdrawOutcome> withdrawExternal(WithdrawExternalCommand c)` — `origin`, `originDocumentIds`; outcome per id `WITHDRAWN` / `ALREADY_CONVERTED` (+ resulting document) / `NOT_FOUND` | `:edit` | `SUGGESTION_WITHDRAW` | — | `POS-T1-31` |
| | `SuggestionStatus getSuggestionStatus(String origin, UUID originDocumentId)` — status, quantity, resulting document type / id / ref, `conversionLive` | `:view` | — | — | `POS-T1-34` |
| | `SuggestionResult markConverted(MarkConvertedCommand c)` — `suggestionId`, `resultingDocumentType`, `resultingDocumentId`, `resultingDocumentRef` | `:edit` | `SUGGESTION_CONVERT` | `WH_REPLENISHMENT_SUGGESTION_CONVERTED` | `POS-T1-33`, `POS-GRD-32` |
| | `SuggestionResult releaseConversion(ReleaseConversionCommand c)` — `suggestionId`, `resultingDocumentId`, `reasonCodeId` | `:edit` | `SUGGESTION_RELEASE` | `WH_REPLENISHMENT_SUGGESTION_RELEASED` | `POS-T1-35` |
| **`WhMaterialRequisitionPort`** · `ai.warehouse.port.stores` | `RequisitionResult create(CreateRequisitionCommand c)` — envelope, `sourceDocumentType/Id/Ref`, `warehouseId`, `departmentId`, `costObjectType`, `costObjectId`, `purposeCode`, `requiredByDate`, `initialStatus` (`DRAFT`/`APPROVED`), `approvedByUserId`, `lines[]` (`itemId`, `quantity`, `uomCode`, `requiredDate`, line cost object?) | `wh_material_requisitions:create` | `MRQ_CREATE` | — | `MRQ-T1-20`, `MRQ-GRD-20` |
| | `RequisitionResult cancel(CancelRequisitionCommand c)` — `requisitionId`, `reasonCodeId`, `note`; no-op success on a terminal requisition with nothing issued | `:cancel` | `MRQ_CANCEL` | — | `MRQ-T1-21` |
| | `RequisitionResult close(CloseRequisitionCommand c)` — `requisitionId`, `reasonCodeId`, `note` | `:close` | `MRQ_CLOSE` | — | `MRQ-T1-22` |
| | `RequisitionPosition getRequisitionPosition(UUID requisitionId)` — status; per line requested / approved / issued / returned / closed / cancelled / reserved / open-to-issue | `:view` | — | `WH_STORE_ISSUE_POSTED`, `WH_STORE_RETURN_POSTED` (cost object + value per line) | `MRQ-T1-23`, `SIR-T4-02`, `-06` |

### R.3 SPIs a sibling implements (core calls them)

| SPI · package | Methods (signature) | Cardinality / absent | Who implements | Contract |
|---|---|---|---|---|
| **`PurchaseOrderChangeGuard`** · `ai.warehouse.port.purchase` | `Optional<GuardRefusal> check(PurchaseOrderRef po, PurchaseOrderChange change)` — `change` ∈ `EDIT`, `RELEASE_SCHEDULE`, `SUBMIT`, `APPROVE`, `RETURN`, `CANCEL`, `CLOSE`, `CLOSE_LINE` | collection; empty → every manual change allowed | `warehouse-trade` | `POS-GRD-08`, `POS-T1-13` |
| **`DemandOrderChangeGuard`** · `ai.warehouse.port.demand` | `Optional<GuardRefusal> check(DemandOrderRef order, DemandOrderChange change)` — `EDIT`, `RELEASE`, `ALLOCATE`, `CANCEL`, `CLOSE` | collection; empty → allowed | `warehouse-trade` | `POS-GRD-14` |
| **`RmaChangeGuard`** · `ai.warehouse.port.returns` | `Optional<GuardRefusal> check(RmaRef rma, RmaChange change)` — `EDIT`, `APPROVE`, `CANCEL`, `EXPIRE` | collection; empty → allowed | `warehouse-trade` | `POS-GRD-22` |
| **`MaterialRequisitionChangeGuard`** · `ai.warehouse.port.stores` | `Optional<GuardRefusal> check(RequisitionRef r, RequisitionChange change)` — `EDIT`, `SUBMIT`, `APPROVE`, `REJECT`, `CANCEL`, `CLOSE` | collection; empty → allowed | `warehouse-manufacturing` | `MRQ-GRD-21` |
| **`SuggestionConversionOwner`** · `ai.warehouse.port.replenishment` | `boolean ownsConversion(SuggestionRef s)` | optional single bean; absent → core converts on Accept | `warehouse-trade` | `POS-T1-32` |
| **`PurchaseRequisitionHandoff`** · `ai.warehouse.port.purchase` | `HandoffRef raise(HandoffCommand c)` — `c`: `PortEnvelope` (core is the caller: `sourceModule = warehouse`, `idempotencyKey = MRQ_HANDOFF:<handoff row id>`, `actingUserId` = the stores user), `requisitionId`, `requisitionLineId`, `requisitionNumber`, `warehouseId`, `departmentId`, cost object, `itemId`, `quantity`, `uomCode`, `requiredDate`; returns `HandoffRef(module, documentType, documentId, documentRef)` with the **issued** number · `HandoffStatus status(HandoffRef ref)` → `(status, statusLabel, orderedQuantity, receivedQuantity, closed)` | optional single bean; absent → action not offered, endpoint `409 PURCHASE_HANDOFF_UNAVAILABLE` | `warehouse-trade` | `MRQ-T1-11`, `-13`; event `WH_REQUISITION_SHORTFALL_HANDED_OFF` |
| **`CostObjectResolver`** · `ai.warehouse.port.stores` | `String type()` · `ResolvedCostObject resolve(UUID id, UUID companyId)` → `(ref, name, departmentId, counterLocationPurpose)` (purpose default `CONSUMED`) · `default void assertIssuable(UUID costObjectId, UUID itemId, BigDecimal baseQty)` · `default boolean ownsReservations()` (false) · `default List<UUID> reservationsFor(UUID costObjectId, UUID itemId)` (empty) · `default void onIssuePosted(IssueLineFact l)` — `l` carries issue / line ids, cost object, item, lot, base qty, unit cost, movement line id, **consumed and residual reservation ids** · `default void onReturnPosted(ReturnLineFact l)`. **No `onIssueReversed`** (`STO-D11`) | collection keyed by `type()`; an unregistered type → `422 COST_OBJECT_TYPE_UNSUPPORTED` | core: `DEPARTMENT`, `COST_CENTRE`, `MACHINE`, `PROJECT`, `WORK_ORDER`; MFG: `PRODUCTION_ORDER` | `SIR-GRD-01`, `-01a`, `SIR-T4-01`, `-03`, `MRQ-T4-01`, `-02` |
| **`QualityInspectionSourceResolver`** · `ai.warehouse.port.quality` | `String sourceType()` · `InspectableSource resolve(UUID sourceDocumentId, UUID warehouseId)` (lines: `sourceLineId`, `itemId`, `lotId`, `heldQuantity`, `locationId`, `statusCode`, `ownerId`, serials) · `void assertInspectable(InspectableSource s)` · `default boolean stockBearing()` (true) · `default void onDisposition(UUID inspectionId, DispositionOutcome o)` — reacts only; core posts every movement of a stock-bearing disposition | collection; unregistered → `422 QC_SOURCE_TYPE_UNSUPPORTED` | core: `GOODS_RECEIPT`, `STORE_RETURN`, `STOCK`; MFG: `PRODUCTION_RECEIPT`, `IN_PROCESS` | `IIS-GRD-07`, `-07a`, `IIS-T4-05` |
| **`GatePassSourceResolver`** · `ai.warehouse.port.gate` | `String sourceType()` · `ResolvedGateDocument resolve(UUID documentId, UUID warehouseId)` (party, lines: `sourceLineId`, `itemId`, `quantity`, `uomCode`) · `boolean isDispatched(UUID documentId)` — answers both gate-pass lines and outward gate-entry links | collection; unregistered → `422 GATE_PASS_SOURCE_TYPE_UNSUPPORTED` / `422 GATE_ENTRY_DOCUMENT_UNSUPPORTED` | core: `SUPPLIER_RETURN`, `SHIPMENT`, `STORE_ISSUE`; india: `DELIVERY_CHALLAN`; MFG: `SUBCONTRACT_DISPATCH` | `GTE-GRD-11`, `-12`, `-15` |
| `WarehouseGateEventHandler` (existing, `POST /warehouse/gate-events`) | core registers `WhGateEntryGateEventHandler` | — | core | `GTE-T1-07`, `-08` |

### R.4 Events (outbox) published by P8

`WH_PO_SCHEDULE_RELEASED` · `WH_PO_AMENDED` · `WH_PO_CLOSED` · `WH_PO_CANCELLED` · `WH_PO_LINE_RECEIVED` ·
`WH_PO_SCHEDULE_LINE_RECEIVED` · `WH_DEMAND_AMENDED` · `WH_DEMAND_CANCELLED` · `WH_DEMAND_SHIPPED` · `WH_RMA_MATCHED` ·
`WH_RMA_EXPIRED` · `WH_RMA_CANCELLED` · `WH_SUPPLIER_RETURN_DISPATCHED` · `WH_REPLENISHMENT_SUGGESTION_CONVERTED` ·
`WH_REPLENISHMENT_SUGGESTION_RELEASED` · `WH_REQUISITION_SHORTFALL_HANDED_OFF` · `WH_STORE_ISSUE_POSTED` ·
`WH_STORE_RETURN_POSTED` · `WH_GRN_POSTED` (bill fields added) · `WH_MRN_AUTHORISED`.

## R29 dispositions

Review: `docs/reviews/R29-functional-review-stores.md` (F-ids below) and the core-side items of
`R29-functional-review-trade-purchase.md` (`TP-`), `-trade-sales.md` (`TS-`) and `-mfg.md` (`MFG-`).
*Contracts:* GTE = gate-entry, GBM = grn-bill-match, IIS = incoming-inspection-sampling, MRA = mrn-authorisation,
MRQ = material-requisition, SIR = store-issue-return, POS = po-schedule-port.

| Finding | What changed | Where |
|---|---|---|
| F1 | scope pair `:view:all`/`:view:branch` seeded on every new resource; department axis is its own verb `:view_all_departments` | §4, `STO-D16`; GTE/MRA/MRQ/SIR/IIS §0, `GTE-T2-00`, `MRQ-GRD-01`, `-04`; p8-03…p8-11, p8-13 seeds |
| F2 | every P8 schema migration renumbered above the live high-water mark: app `V511310`…`V511323`, base `V501230`…`V501235`; seeds `V511400`+ unchanged; demand idempotency index rebuilt after `V511303` | §4, `STO-D12`; all seven contracts; every p8 header; epic migration table |
| F3 | demand line may hold `ordered_quantity = 0` when schedule-driven (CHECK replaced); cancelled firm quantity stays in ordered and in cancelled | FR-505; `POS-T1-10`, `-11`, `POS-GRD-10`; p8-02 |
| F4 | reservations per grain; consume-and-split inside the issue transaction; core consumes owner-held holds | FR-531, `STO-D18`; `MRQ-T4-01`, `-02`, `SIR-T4-01`; p8-09, p8-10 |
| F5 | new `supplier_billed_quantity` + accessor, existing helpers untouched; posting = received + free − excess refused; dock rejection named | FR-517; GBM §0, `GBM-GRD-07`, `-UNR-04`, `-T4-01`; p8-04; epic invariant |
| F6 | approved `OPEN` PO takes manual release / firm / close-short with `:release_schedule` when no guard refuses | FR-502; `POS-T1-02`…`-04`, `POS-T2-02`; p8-01 |
| F7 | `effectiveOrderedQuantity()` roll-up row; every reader listed; `OPEN`/`BLANKET` header never `RECEIVED` before close | FR-502; `POS-T1-14`, `POS-GRD-11`; p8-01 |
| F8 | excess over bill and over PO computed separately; decision quantity = above PO + tolerance; six frozen worked examples | FR-520; GBM §1.5, `GBM-GRD-06`, `-08`; p8-04 |
| F9 | bill weight + UoM on the gate bill row; variance once per entry at the later of net-known and first GRN post | FR-510; `GTE-T4-03`; p8-03 |
| F10 | MRN flow keyed on pending stock (grandfathered); setting change never strands `MRN_PENDING` | FR-527; `MRA-GRD-01`, `-T4-04`; p8-08 |
| F11 | destructive issue under `QCINSP`; cost-object columns on the inspection line; registers read them | FR-524, FR-539; `IIS-T4-02`, SIR §5.4; p8-05, p8-13 |
| F12 | EXTERNAL runs inserted `COMPLETED`; run_type/run_by pairing CHECK replaced | FR-528; POS §8b schema, `POS-T1-30`; p8-16 |
| F13 | `wh_rma_lines.original_demand_order_line_id` added; ceiling guard uses it | FR-506; `POS-GRD-21`, `-T1-20`; p8-15 |
| F14 | rows for `getRmaPosition`, `markConverted`, `PurchaseRequisitionHandoff.status`, `WhMaterialRequisitionPort` (idempotency, initial status, approver, guard) | FR-506, FR-528, FR-531; `POS-T1-25`, `-33`; `MRQ-T1-13`, §8a; registry R.2/R.3; p8-09, p8-15, p8-16 |
| F15 | entry gate-out moving a pass also needs `wh_gate_passes:gate_out` | `GTE-T1-05`, `-T2-05`; p8-03 |
| F16 | first and final approval mutually exclusive; recall clears the first approval | FR-530; `MRQ-T1-03`, `-04`, `-06`, `MRQ-GRD-11`; p8-09 |
| F17 | issue line: same requisition, same item, base-unit comparison | `SIR-GRD-02`; p8-10 |
| F18 | demand amend floor = allocated + cancelled + backordered (cumulative) | FR-505; `POS-GRD-09`; p8-02 |
| F19 | `SHORT_SHIPMENT` prefill and ceiling on billed − received | FR-519; `GBM-T4-02`; p8-04 |
| F20 | owner check inside `acceptLocked`, authority `:accept` | `POS-T1-32`; p8-16 |
| F21 | one operation registry `wh_port_operations` for every port write | FR-504, `STO-D17`; `POS-GRD-07`; registry R.1; p8-01 |
| F22 | single sampling `Re = Ac + 1` (CHECK) | FR-521; `IIS-GRD-03`, `-T1-08`; p8-05 |
| F23 | gate-pass line `source_line_id` resolved by the resolver | FR-513; `GTE-GRD-12`; p8-03 |
| F24 | bill group per gate entry; exclusion constraint instead of a plain unique index | FR-516; `GBM-GRD-01`, `GTE-T4-01`; p8-04 |
| F25 | core posts `PRODUCTION_RECEIPT` dispositions; `onDisposition` only reacts | FR-525; `IIS-T4-05`; registry R.3; p8-06 |
| F26 | one `<DOCUMENT>_SELF_APPROVAL` 403 convention, a code on every maker ≠ checker guard | §3; GTE/GBM/MRA/MRQ/SIR guard rows; scenarios `WH-SC-436`, `-459` |
| F27 | MRN covers every GRN (PO, blind, non-PO) | FR-527; `MRA-UNR-04`, `-T4-01` |
| F28 | `entered_at` server-stamped for barrier events too; device time in `barrier_occurred_at`; one field name | FR-507; `GTE-T1-07`; p8-03 |
| F29 | reversal resolves `EXCESS_OVER_BILL` and weighment cases `RECEIPT_REVERSED` | `GBM-T4-05`; p8-04 |
| F30 | one column name `sampling_scheme_id` (version row); plans re-pointed; deactivation row | FR-521; `IIS-T1-03`, `-03a`; p8-05; epic table |
| F31 | gate register is a WS-277 tab; KPI rows seeded by p8-13; `OD-27` now cites FR-533 | FR-534, FR-539, §11; SIR §5.4; p8-13 |
| F32 | SOFT = expiring hold, HARD = until consumed; top-up action and daily job | FR-531; `MRQ-T4-01`, `-T1-14`; p8-09 |
| F33 | close-short of the last line ends `CLOSED`; department resolver checks active only | FR-530; `MRQ-T1-08`, `-09`, `MRQ-GRD-02`, `SIR-GRD-01` |
| F34 | five core resolvers listed (`MACHINE`, `PROJECT` added) | FR-533; `SIR-GRD-01`; registry R.3 |
| F35 | outward-document link row and guard | `GTE-T1-02a`, `GTE-GRD-15`; p8-03 |
| F36 | gate-security persona permission is `:gate_out` | §3 |
| TP-F1 | `BLANKET_RELEASE` ordered NULL while Σ firm = 0 | FR-502; `POS-GRD-02`, `-T1-02` |
| TP-F6 | port principal = acting user with `warehouse:orders:port` + verb; core seeds dependencies, sibling seeds grants; SYSTEM approvals | FR-504; POS §0, `POS-GRD-13`; registry R.1; p8-01 |
| TP-F14 | schedule-line `unit_price`; allocation-weighted GRN valuation | FR-502; `POS-GRD-12`, `-T4-02`; p8-01 |
| TP-F15 | `valid_to` = last release date; `receipt_cutoff_date` = last receipt date | FR-502; `POS-GRD-05`, `-06`, `-T3-02`; p8-01 |
| TP-F18 | `releaseConversion` port operation returns a PR-converted suggestion to `PROPOSED` | FR-528; `POS-T1-35`; p8-16 |
| TP-F19 | core keeps `OPEN` `unit_price > 0`; trade refuses free-of-charge `OPEN` at submit | `STO-D14`; `POS-GRD-02` |
| TP-F22 | `closeOrder` semantics stated (idempotent, closes schedules and lines, leaves the gate picker) | FR-504; `POS-T1-08`, `-T3-02` |
| TP-F24 | site immutable; deliver-to = location inside the site | `STO-D15`; `POS-GRD-09` |
| TS-F1 | demand-line CHECK replaced for schedule-driven lines | as F3 |
| TS-F2 | header ladder for schedule-driven orders — **`OD-45`**, recommendation (A) built | §11 `OD-45`; `POS-T1-12a`, `-12b`, `POS-OPEN-03`; p8-02 |
| TS-F3 | core RMA statuses stated exactly, events per status, partial receipt mapping left to trade | FR-506; `POS-T1-22` |
| TS-F11 | `WhAvailableToPromiseQuery` added to p8-02 and the port contract | FR-505; `POS-T4-08`; registry R.2; p8-02 |
| TS-F15 | firm, un-firm, cancel one demand schedule line | FR-505; `POS-T1-11a`…`-11c`; p8-02 |
| TS-F21 | port RMA created `APPROVED` with the source approver | FR-506; `POS-T1-20`; p8-15 |
| TS-F25 | rows for `cancelDemand`, `getFulfilmentPosition`, demand guard, demand idempotency, `WH_DEMAND_CANCELLED`/`_AMENDED` | `POS-T1-12`, `POS-GRD-14`, `POS-T4-07`; registry R.2 |
| MFG-F4 | port `cancel` is a no-op success on a terminal requisition with nothing issued; position read gives Σ issued so MFG blocks only on issued > 0 | `MRQ-T1-21`, `-23`; registry R.2 |
| MFG-F12 | MRQ reservations suppressed by the type's `ownsReservations()`, not by `reservationsFor` returning rows | FR-531, `STO-D18`; `MRQ-T4-01`; p8-09 |
| MFG-F13 | `withdrawExternal` returns per-proposal outcomes; converted ones stay supply; `getSuggestionStatus.conversionLive` | FR-528; `POS-T1-31`, `-34`; p8-16 |

## 13. Sources (web research, 2026-10-22)

- IS 2500 (Part 1) adoption of ISO 2859-1, code letters by lot size and level: [InfraLens IS 2500-1:2017](https://infralens.in/code/IS-2500-Part-1-2017), [qualityinspection.org — inspection levels](https://qualityinspection.org/inspection-level/), [Global Sources — AQL table](https://www.globalsources.com/knowledge/aql-table/).
- SAP has no standard gate pass; RGP/NRGP built over material documents and custom transactions: [SAP Community thread](https://archive.sap.com/discussions/thread/1165497), [BSPTCL NRGP manual](https://bsptcl.in/ERP/MM/Gate_pass_Non_Returnable.pdf), [Deendayal Port gate pass](https://www.deendayalport.gov.in/wp-content/uploads/2022/11/23Aug2021050643PM.pdf).
- SAP QM dynamic modification (skip-lot, normal/reduced stages): [SAP Learning — Setting up Dynamic Modification](https://learning.sap.com/learning-journeys/configuring-sap-s-4hana-quality-management/setting-up-dynamic-modification), [SAPinsider — DMR](https://sapinsider.org/dmr-leads-to-more-efficient-procurement-and-production-processes/).
- Odoo quality control points (all / percentage / periodic; per quantity): [Odoo 13 control points](https://www.odoo.com/documentation/13.0/applications/inventory_and_mrp/quality/control/control_points.html), [Cybrosys — Odoo 18 QC](https://www.cybrosys.com/blog/overview-of-manufacturing-quality-check-in-odoo-18).
- Tally Prime material in/out and job-work registers: [Tally — Job Work](https://help.tallysolutions.com/tally-prime/inventory/job-work/).
