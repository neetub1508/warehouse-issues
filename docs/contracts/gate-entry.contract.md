# Functional Contract — Gate entry register and gate passes (returnable / non-returnable)

> **What this is.** The functional truth for every crossing of the site gate: the inward and outward
> **gate entry**, its link to POs, ASNs, supplier bills and a weighment, the turn-back, the gate-out, and
> the **gate pass** (RGP / NRGP) with its approval, gate-out, line-wise return and overdue clock. Every
> row cites its source id.
>
> **What this is not.** It does not restate the receiving session, the GRN or the movement writer
> ([`receipt-qc-putaway.contract.md`](receipt-qc-putaway.contract.md), [`movement-post-reverse.contract.md`](movement-post-reverse.contract.md)).
> **A gate pass never posts a movement** (`STO-D4`); the stock leaves on its own document.
>
> **Status.** Derived 2026-10-22 (v0) from [`frd/FRD-STORES.md`](../frd/FRD-STORES.md) §6.3. Not ratified;
> run through `functional-reviewer` before `P8-03` is built.

---

## 0. Identity

| | |
|---|---|
| **Workflow** | Gate-in (inward/outward) → link documents → turn back *or* hand to receiving / loading → gate-out; gate pass create → approve → gate-out → return(s) → returned / closed-short |
| **Module** | `warehouse` (`wh_`); seeds in `warehouse-base` code lists (`V500300`) |
| **Domain baseline** | `DECISIONS.md` `D-10`, `D-16`, `L-1` · `FRD-STORES.md` `FR-507`…`FR-515`, `STO-D3`, `STO-D4` · `IRR-23` (arrival clock) · `FR-408` (maker ≠ checker) · `P5-17` weighing records · `P2-IN-04` (`FR-195`, e-way-bill-conditional dispatch gate pass) |
| **Owning task bodies** | `issues/p8-03.md`. Depends on `p7-*` (cleaned schema), `p1-09` (series), `p1-13` (sessions), `p5-17` (weighing), `p2-14` (print), `p2-23` (approval) |
| **Primary tables** | `wh_gate_entries`, `wh_gate_entry_documents`, `wh_gate_passes`, `wh_gate_pass_lines`, `wh_gate_pass_returns` (`V510402`); `wh_receiving_sessions.gate_entry_id` (ALTER, `V510402`); `wh_weighing_records.subject_type` CHECK widened with `GATE_ENTRY` (`V510402`) |
| **Status columns** | `wh_gate_entries.status`, `wh_gate_passes.status` — **no CHECK** (`D-10`), service-enforced |
| **Permission resources** | `wh_gate_entries:{view,create,edit,turn_back,gate_out,cancel,export}` · `wh_gate_passes:{view,create,edit,approve,gate_out,record_return,close_short,extend,cancel,export}` (seed `V511402`, each verb `→ :view` dependency) |
| **Routes** | `/warehouse/gate/entries` (WS-260) + `/[id]` (WS-261) · `/warehouse/gate/passes` (WS-262) + `/[id]` (WS-263) · **mobile: none** |
| **Contract version** | `v0 — 2026-10-22` |

### Acceptance checks

| # | The requester expects… | Delivered by |
|---|---|---|
| A1 | The PO, bill no and bill date are captured **on arrival**, at the gate (`WH-SC-427`) | `GTE-T1-01`, `GTE-GRD-01`…`-04` |
| A2 | A vehicle can be turned back and nothing downstream follows (`WH-SC-429`) | `GTE-T1-03`, `GTE-UNR-02` |
| A3 | A PO receipt can be forced to start at the gate (`WH-SC-430`) | `GTE-GRD-06` |
| A4 | The weighbridge net sits beside the bill weight and a variance is flagged, not blocked (`WH-SC-431`) | `GTE-T4-03` |
| A5 | An RGP is approved by a second person, leaves, comes back in parts and goes overdue (`WH-SC-432`…`-436`) | `GTE-T1-10`…`-17`, `GTE-T3-01` |
| A6 | No gate pass moves stock (`WH-SC-433`) | `GTE-GRD-10`, `GTE-UNR-01` |

---

## 1. T1 — State machine

### 1.1 Status inventory

| Entity | Status | Represented by | Reachable via | Exits via | Kind |
|---|---|---|---|---|---|
| Gate entry | `OPEN` | `status`; `entered_at` stamped by the server | `GTE-T1-01` | `-03`, `-05`, `-06` | initial, active |
| Gate entry | `TURNED_BACK` | `status`; `turned_back_at`, reason | `GTE-T1-03` | none | **terminal** |
| Gate entry | `CLOSED` | `status`; `exited_at` | `GTE-T1-05` | none | **terminal** |
| Gate entry | `CANCELLED` | `status`; reason | `GTE-T1-06` | none | **terminal** |
| Gate pass | `DRAFT` | `wh_gate_passes.status` | `GTE-T1-10` | `-11`, `-18` | initial |
| Gate pass | `APPROVED` | `status`; `approved_by`, `approved_at` | `GTE-T1-11` | `-12`, `-18` | active |
| Gate pass | `OUT` | `status`; `out_gate_entry_id`, `gated_out_at` | `GTE-T1-12` | RGP: `-13`, `-14`, `-16`; NRGP: none | RGP active · **NRGP terminal** |
| Gate pass | `PARTIALLY_RETURNED` | `status` | `GTE-T1-13` | `-13`, `-14`, `-16` | active |
| Gate pass | `RETURNED` | `status`; `returned_at` | `GTE-T1-14` | none | **terminal** |
| Gate pass | `CLOSED_SHORT` | `status`; reason, `closed_by` | `GTE-T1-16` | none | **terminal** |
| Gate pass | `CANCELLED` | `status`; reason | `GTE-T1-18` | none | **terminal** |

Not statuses: **overdue** is computed on read (`GTE-T3-01`); the expected-return revision is a dated child
row (`wh_gate_pass_revisions` is **not** created — the revision is an audit row plus the new date, `GTE-T1-15`).

### 1.2 Transitions

| ID | From | Event / action | To | Guard | Actor (permission) | Side effects | Reason? | UI entry point |
|---|---|---|---|---|---|---|---|---|
| GTE-T1-01 | — | Gate-in: direction, purpose, party, vehicle, driver, mobile, transporter, LR no.; for an inward `PURCHASE_RECEIPT`: supplier, **PO(s)**, ASN(s), primary bill (type, no, date, amount, e-way bill no.) | `OPEN` | `GTE-GRD-01`…`-04` | `wh_gate_entries:create` | gapless `GE` number issued at create; `entered_at = now()` (server clock, `IRR-23`); `wh_gate_entry_documents` rows | no | WS-260 toolbar **Gate in** |
| GTE-T1-02 | `OPEN` | Edit / link more documents | unchanged | same guards; vehicle and direction frozen | `wh_gate_entries:edit` | audit row per changed field | no | WS-261 **Edit** |
| GTE-T1-03 | `OPEN` | Turn back | `TURNED_BACK` | `GTE-GRD-05` | `wh_gate_entries:turn_back` | `turned_back_at`; documents kept; nothing else | **yes** (reason code, context `GATE_TURN_BACK`) | WS-260 row **Turn back** |
| GTE-T1-04 | `OPEN` (inward purchase) | Create receiving session | unchanged | `GTE-GRD-07` | `wh_receiving_sessions:create` | a session `ARRIVED` with `gate_entry_id`, supplier, vehicle, driver and the PO/ASN documents copied (`RQP-T1-01` with a pre-fill) | no | WS-261 **Create receiving session** |
| GTE-T1-05 | `OPEN` | Gate-out | `CLOSED` | `GTE-GRD-08`, `GTE-GRD-09` | `wh_gate_entries:gate_out` | `exited_at`; linked session's `departed_at` stamped; any gate pass named on the entry moves by `GTE-T1-12` in the same transaction | no | WS-260 row **Gate out** |
| GTE-T1-06 | `OPEN` | Cancel (entered in error) | `CANCELLED` | no session, GRN or gate pass references it | `wh_gate_entries:cancel` | number stays issued | **yes** | WS-261 **Cancel** |
| GTE-T1-07 | `OPEN` | Gate event `ENTRY` from the barrier | `OPEN` (new or matched) | vehicle number normalised; an `OPEN` entry for that vehicle at that site in the last `warehouse.gate.event_match_minutes` (default 240) is matched, else a skeleton entry is created with purpose `OTHER` | system (`WarehouseGateEventHandler`, outcome `CLAIMED`) | `entered_at` = event `occurredAt` | no | none (event) |
| GTE-T1-08 | `OPEN` | Gate event `EXIT` | unchanged | — | system | sets `exit_proposed_at`; **does not close** — the guard set of `GTE-T1-05` may not hold | no | WS-260 tile *Exit proposed* |
| GTE-T1-10 | — | Create gate pass: kind, purpose, party, expected return date (RGP), lines (item **or** description, qty, UoM, approx. value, source document) | `DRAFT` | `GTE-GRD-10`…`-12` | `wh_gate_passes:create` | gapless `GP` number | no | WS-262 **Add** |
| GTE-T1-11 | `DRAFT` | Approve | `APPROVED` | approver ≠ creator (`FR-408`, `403 APPROVER_IS_ACTOR`) | `wh_gate_passes:approve` | `approved_by/at` | no | WS-262 row **Approve** |
| GTE-T1-12 | `APPROVED` | Gate-out against an **outward** gate entry | `OUT` | `GTE-GRD-13` | `wh_gate_passes:gate_out` | `out_gate_entry_id`, `gated_out_at`, `quantity_out` = line quantity | no | WS-263 **Gate out** / WS-260 **Gate out** of the entry |
| GTE-T1-13 | `OUT` · `PARTIALLY_RETURNED` (RGP) | Record return of some lines against an **inward** gate entry | `PARTIALLY_RETURNED` | `GTE-GRD-14` | `wh_gate_passes:record_return` | `wh_gate_pass_returns` row (line, qty, condition `RETURN_CONDITION`, in-gate entry, remarks); line `returned_quantity` += | no | WS-263 **Record return** |
| GTE-T1-14 | `OUT` · `PARTIALLY_RETURNED` | the return that makes every line returned = out | `RETURNED` | — | same | `returned_at` | — | effect of `-13` |
| GTE-T1-15 | `APPROVED` · `OUT` · `PARTIALLY_RETURNED` (RGP) | Extend expected return date | unchanged | new date > old date; extender ≠ creator | `wh_gate_passes:extend` | audit row (old, new, reason); overdue episode reset (`GTE-T3-01`) | **yes** | WS-263 **Extend** |
| GTE-T1-16 | `OUT` · `PARTIALLY_RETURNED` (RGP) | Close short (lost, scrapped by the party, sold) | `CLOSED_SHORT` | closer ≠ creator | `wh_gate_passes:close_short` | unreturned quantity → `closed_quantity` per line | **yes** | WS-263 **Close short** |
| GTE-T1-18 | `DRAFT` · `APPROVED` | Cancel | `CANCELLED` | — | `wh_gate_passes:cancel` | number stays issued | **yes** | WS-262 row **Cancel** |

### 1.3 Guards

| ID | Predicate | Refusal: HTTP · code · field | DB backstop | Source |
|---|---|---|---|---|
| GTE-GRD-01 | each linked PO is `APPROVED`/`PARTIALLY_RECEIVED`, same site, same supplier as the entry | `422 GATE_ENTRY_PO_NOT_RECEIVABLE` · `documents[i].poId` / `422 GATE_ENTRY_PO_SUPPLIER_MISMATCH` | FK `wh_gate_entry_documents.po_id → wh_purchase_orders` | FR-508 |
| GTE-GRD-01a | the PO picker / search resolves a PO by `po_number` **or** `source_document_ref` (supplier-facing trade number, TRADE `OD-30`), same supplier and site; an ambiguous match (two POs share a ref) lists both, never picks one | — (picker contract) | — | FR-508 |
| GTE-GRD-02 | each linked ASN is `EXPECTED`, same site and supplier | `422 GATE_ENTRY_ASN_NOT_RECEIVABLE` | FK | FR-508 |
| GTE-GRD-03 | inward `PURCHASE_RECEIPT` has a supplier; bill date ≤ today (site TZ) | `422 GATE_ENTRY_SUPPLIER_REQUIRED` · `supplierCounterpartyId`; `422 SUPPLIER_BILL_DATE_IN_FUTURE` · `bill.billDate` | — | FR-508 |
| GTE-GRD-04 | vehicle number matches `warehouse.gate.vehicle_number_pattern` when set (default none); normalised upper-case, spaces removed | `422 VEHICLE_NUMBER_INVALID` · `vehicleNumber` | — | FR-507 |
| GTE-GRD-05 | no receiving session exists on the entry | `409 GATE_ENTRY_HAS_SESSION` | — | FR-509 |
| GTE-GRD-06 | when `warehouse.gate.entry_required_for_receipt = true`, a GRN with any `po_line_id` must sit on a session with a non-null `gate_entry_id` | `409 GATE_ENTRY_REQUIRED` · `sessionId` (raised by the GRN create, `RQP-T1-07`) | — | FR-509 |
| GTE-GRD-07 | entry is inward, `OPEN`, purpose `PURCHASE_RECEIPT`/`RETURNABLE_IN`/`CUSTOMER_RETURN_IN`/`JOB_WORK_IN`; at most one live session per entry | `409 GATE_ENTRY_SESSION_EXISTS` | partial uk `wh_receiving_sessions(gate_entry_id) WHERE status <> 'CANCELLED'` | FR-509 |
| GTE-GRD-08 | inward: the linked session is `COMPLETED` or `CANCELLED` (unloading over) | `409 GATE_OUT_SESSION_OPEN` naming the session | — | FR-511 |
| GTE-GRD-09 | outward: every linked outward document is dispatched — supplier return `DISPATCHED`, shipment despatched, challan issued, store issue `POSTED`, gate pass `APPROVED` (moves to `OUT` in the same request) | `409 GATE_OUT_DOCUMENT_NOT_DISPATCHED` naming each | — | FR-511 |
| GTE-GRD-10 | RGP: `expected_return_date` ≥ today; NRGP: none | `422 GATE_PASS_RETURN_DATE_REQUIRED` · `expectedReturnDate` | — | FR-512 |
| GTE-GRD-11 | a line with `item_id` of a stock-holding item type names `(source_document_type, source_document_id)` that a registered `GatePassSourceResolver` resolves, at the same site and party; a line without `item_id` has a description | `422 GATE_PASS_STOCK_LINE_UNSOURCED` · `lines[i].sourceDocumentId` · `422 GATE_PASS_SOURCE_TYPE_UNSUPPORTED` | — | FR-513 |
| GTE-GRD-12 | line quantity > 0; for a sourced line, ≤ the source line's quantity not already on another live gate pass | `422 GATE_PASS_QUANTITY_EXCEEDS_SOURCE` | — | FR-513 |
| GTE-GRD-13 | the out entry is outward, `OPEN`, same site; each sourced line's document is dispatched | `409 GATE_OUT_DOCUMENT_NOT_DISPATCHED` | — | FR-514 |
| GTE-GRD-14 | returned quantity per line ≤ quantity out − returned − closed; the in entry is inward, `OPEN`, same site | `422 GATE_PASS_RETURN_EXCEEDS_OUT` · `returns[i].quantity` | CHECK `returned_quantity + closed_quantity <= quantity_out` | FR-514 |

### 1.4 Unreachable

| ID | Must never happen | Why |
|---|---|---|
| GTE-UNR-01 | any gate-pass transition writes `whb_stock_movements` | `STO-D4`; the stock left on its source document |
| GTE-UNR-02 | a session, GRN or gate-out from a `TURNED_BACK`/`CANCELLED` entry | FR-509 |
| GTE-UNR-03 | an edit of a `CLOSED` entry or of `entered_at`/`exited_at` | `IRR-23` |
| GTE-UNR-04 | an NRGP leaving `OUT`, or an RGP return above quantity out | FR-514 |
| GTE-UNR-05 | an approver approving their own gate pass | FR-408 |

---

## 2. T2 — Action × role × state

Every query and action is limited to the user's allowed warehouses (`p1-18`); an auditor is read-only.

| ID | Action | Permission | Allowed from | Extra condition |
|---|---|---|---|---|
| GTE-T2-01 | Gate in | `wh_gate_entries:create` | — | gate security |
| GTE-T2-02 | Edit / link | `wh_gate_entries:edit` | `OPEN` | — |
| GTE-T2-03 | Turn back | `wh_gate_entries:turn_back` | `OPEN` | no session |
| GTE-T2-04 | Create receiving session | `wh_receiving_sessions:create` | `OPEN` inward | receiving clerk |
| GTE-T2-05 | Gate out | `wh_gate_entries:gate_out` | `OPEN` | `GTE-GRD-08/09` |
| GTE-T2-06 | Cancel entry | `wh_gate_entries:cancel` | `OPEN` | nothing references it |
| GTE-T2-07 | Create / edit gate pass | `wh_gate_passes:create` / `:edit` | — / `DRAFT` | — |
| GTE-T2-08 | Approve gate pass | `wh_gate_passes:approve` | `DRAFT` | ≠ creator |
| GTE-T2-09 | Gate out pass | `wh_gate_passes:gate_out` | `APPROVED` | outward entry open |
| GTE-T2-10 | Record return | `wh_gate_passes:record_return` | `OUT`, `PARTIALLY_RETURNED` (RGP) | inward entry open |
| GTE-T2-11 | Extend | `wh_gate_passes:extend` | `APPROVED`, `OUT`, `PARTIALLY_RETURNED` (RGP) | ≠ creator |
| GTE-T2-12 | Close short | `wh_gate_passes:close_short` | `OUT`, `PARTIALLY_RETURNED` (RGP) | ≠ creator |
| GTE-T2-13 | Cancel pass | `wh_gate_passes:cancel` | `DRAFT`, `APPROVED` | — |
| GTE-T2-14 | Print gate entry slip / gate pass | `wh_print_jobs:create` + `:view` on the subject | entry any; pass `APPROVED` onward | `SYS-GATE-ENTRY`, `SYS-GATE-PASS` (`P8-12`) |
| GTE-T2-15 | Export | `:export` or ADMIN | — | superset of grid columns |

## 3. T3 — Time-driven rules

| ID | Rule | Trigger | What it changes | Who is notified | Channel | Job | Notify-once? |
|---|---|---|---|---|---|---|---|
| GTE-T3-01 | RGP **overdue** | `expected_return_date < today` (site TZ), status `OUT`/`PARTIALLY_RETURNED` | nothing — backend filter `overdueOnly`, tile | approver + stores in-charge (role setting) | platform notification | `WhGatePassOverdueJob` daily 08:00 site time | once per pass per `warehouse.gate.rgp_overdue_reminder_days` (default 7; 0 = once only); an extend resets the episode |
| GTE-T3-02 | Vehicle **dwell** | `OPEN` inward entry older than `warehouse.gate.max_dwell_hours` (default 12) | nothing — tile *Long dwell* | none | — | computed on read | — |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in |
|---|---|---|---|
| GTE-T4-01 | `GTE-T1-04` | session created with `gate_entry_id` and copied PO/ASN junction rows; the GRN created on it copies the entry's **primary bill** into `wh_goods_receipt_bills` (`GBM-T4-01`) | gate-entry service → session service, one transaction |
| GTE-T4-02 | `GTE-T1-05` inward | session `departed_at` = `exited_at` (only if null) | same transaction |
| GTE-T4-03 | a weighing record with `subject_type = GATE_ENTRY` and `subject_id` = the GE number is saved (`P5-17`) | entry shows net kg; when a GRN of the entry is posted and `|net − Σ bill weight| / bill weight > warehouse.gate.weight_variance_percent` (default null = off), a `QUANTITY` reconciliation case opens on the GRN — never a refusal | GRN post (`WhReconciliationCaseRecorder.open`) |
| GTE-T4-04 | `GTE-T1-12` | pass `OUT`; the source documents are untouched | gate-pass service |
| GTE-T4-05 | `GTE-T1-13` for a sourced line | the source document is **not** touched: a stock item coming back is received on its own document (job-work receipt in `warehouse-india`, supplier replacement GRN, store return) | — (no effect, stated) |
| GTE-T4-06 | GRN posting refuses excess (`GBM-T1-06`) | the refused quantity is listed on the inward entry's gate-out view as *leaving with the vehicle* | read model |

## 5. T5 — Screen contract (web only)

### 5.1 `/warehouse/gate/entries` — WS-260 Gate Entries

| | |
|---|---|
| **Type** | list + transition modals (reference: **Service Vehicle**) |
| **Grid identifier** | `wh_gate_entries` · filter scope `WAREHOUSE_GATE_ENTRY` (add to `COMMON_FILTER_CONFIGS`) |
| **Default sort** | `e.entered_at DESC` (index `idx(warehouse_id, entered_at DESC)`) |
| **Statistics tiles** | `OPEN` · `CLOSED` today · `TURNED_BACK` today · *Exit proposed* · *Long dwell* (filter-aware, no cache name) |
| **Columns** | `gateEntryNumber`, `warehouseName`, `direction`, `purpose`, `partyName`, `vehicleNumber`, `driverName`, `driverMobile`, `transporterName`, `lrNumber`, `poNumbers`, `supplierPoNumbers`, `billNumber`, `billDate`, `ewayBillNumber`, `netWeightKg`, `enteredAt`, `exitedAt`, `status`, `sessionNumber`, `securityOfficerName`, audit |
| **Filters** | `warehouseId`; `direction` (enum); `purpose` (enum); `status` (multi); `partyCounterpartyId` typeahead; `vehicleNumber` (text); `poNumber` (text — matches `po_number` **or** `source_document_ref`); `billNumber` (text); `enteredFrom`/`enteredTo` (`date`, `DateRangePicker`); `openOnly` (boolean) |
| **Row actions** | View · Edit · Create receiving session · Turn back · Gate out · Print slip · Cancel |
| **Toolbar** | **Gate in** · Export |
| **Add modal** | tabs: *Vehicle* (direction, purpose, vehicle, driver, mobile, transporter, LR) · *Party & documents* (party, POs multi-select from `/gate/entries/receivable-pos?supplierId`, ASNs) · *Bill* (type, no, `DatePicker` date, amount, e-way bill) — `size="lg"`, refusal shown in-modal (`AlertBox`) |
| **Export columns** | all grid columns + `createdByName`, `updatedByName` |

### 5.2 `/warehouse/gate/passes` — WS-262 Gate Passes, WS-263 detail

| | |
|---|---|
| **Grid identifier** | `wh_gate_passes` · filter scope `WAREHOUSE_GATE_PASS` |
| **Default sort** | `e.created_at DESC` |
| **Tiles** | `DRAFT` · `APPROVED` · `OUT` · **Overdue** · `RETURNED` (filter-aware) |
| **Columns** | `gatePassNumber`, `warehouseName`, `kind` (RGP/NRGP), `purpose`, `partyName`, `lineCount`, `quantityOut`, `quantityReturned`, `approxValue`, `expectedReturnDate` (`formatDateSync`, date-only), `daysOverdue`, `status`, `approvedByName`, `gatedOutAt`, `returnedAt`, audit |
| **Filters** | `warehouseId`; `kind`; `purpose`; `status` (multi); `partyCounterpartyId`; `expectedReturnFrom/To` (`date`); `overdueOnly` (boolean) |
| **Row actions** | View · Edit (`DRAFT`) · Approve · Gate out · Record return · Extend · Close short · Print · Cancel |
| **Detail (WS-263)** | tabs: *Header* · *Lines* (item/description, qty out, returned, closed, source doc link) · *Returns* (date, in-gate entry, qty, condition) · *History* |
| **Export** | grid columns + lines in a second sheet + `createdByName`, `updatedByName` |

## 6. Out of scope

Visitor management; employee attendance; yard scheduling (`P3-05` dock appointments); weighbridge device
drivers (`P5-17`); a gate pass that posts stock (`STO-D4`); mobile.

## 7. Amendments

| Date | Change |
|---|---|
| 2026-10-22 | v0 derived |

## 8. Invariants and scenarios

`L-1` (no stock path here) · `IRR-23` (server-stamped clocks) · `FR-408`. Scenarios `WH-SC-427`…`-436`, `-441`, `-476`.

## 9. Open rows

| ID | Question | Default |
|---|---|---|
| GTE-OPEN-01 | Should a gate pass for a stock item without a source document be allowed under a manager override (emergency repair)? | **No** (`STO-D4`); raise a store issue to cost object `MACHINE` first |
| GTE-OPEN-02 | Gate-entry series per site or per gate? | per site (`GE`); multiple gates share it, `gate_code` is a column |
