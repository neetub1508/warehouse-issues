# Functional Contract — Material requisition (indent): department / cost centre / production order, approval, reservation, partial issue, closure, back-to-back PR hand-off

> **What this is.** The functional truth for a department's or production's request for material from
> a store: its header and lines, the per-line approval by a second person, the reservation the approval
> takes, the partial issue it allows, the short-close and cancel, and the hand-off of a shortfall to the
> buying module. The issue itself is [`store-issue-return.contract.md`](store-issue-return.contract.md)
> (`SIR-*`); this contract cites it.
>
> **Status.** Derived 2026-10-22 (v0) from [`frd/FRD-STORES.md`](../frd/FRD-STORES.md) `FR-528`…`FR-532`,
> `STO-D9`. Not ratified.

---

## 0. Identity

| | |
|---|---|
| **Workflow** | Draft → submit → approve per line (or reject) → reserve → issue in parts (`SIR`) → issued / short-closed; recall; cancel; shortfall → purchase-requisition hand-off |
| **Module** | `warehouse`; code lists in `warehouse-base` (`V500303`) |
| **Domain baseline** | `FR-408`, `FR-174`, `P0-09` reservations (open-item ledger, holder quad), `P1-18` record-level scope, `FR-528`…`FR-533`, `STO-D9`, `OD-29` |
| **Owning task** | `issues/p8-09.md`; owns the cost-object seam (`COST_OBJECT_TYPE` list, `CostObjectResolver`, `wh_cost_centres`) that `p8-10` applies to issue lines; depends on `p0-09`, `p1-18` |
| **Primary tables** | `wh_material_requisitions`, `wh_material_requisition_lines`, `wh_material_requisition_line_handoffs`, `wh_cost_centres` (`V510408`); code lists `REQUISITION_PURPOSE`, `COST_OBJECT_TYPE` (`V500303`); `whb_document_types` `MATERIAL_REQUISITION`; reservation holder type `MATERIAL_REQUISITION` |
| **Status columns** | header `status`, line `line_status` — no CHECK; line status recomputed from quantities by the service |
| **Permission resources** | `wh_material_requisitions:{view,view:all,create,edit,submit,approve,close,cancel,export,handoff}` (`V511408`). `view` alone = own departments; `view:all` = every department of the allowed sites |
| **Routes** | WS-268 `/warehouse/stores/requisitions`, WS-269 `/[id]`, WS-274 issue queue |
| **Contract version** | `v0 — 2026-10-22` |

### Acceptance checks

| # | Expects | Delivered by |
|---|---|---|
| A1 | A requisition names department, cost object, purpose and required-by (`WH-SC-458`) | `MRQ-T1-01`, `MRQ-GRD-01`…`-03` |
| A2 | Approval by someone else, per line, may approve less (`WH-SC-458`, `-459`) | `MRQ-T1-03`, `MRQ-GRD-05`, `-06` |
| A3 | Approved stock is reserved; shortage visible (`WH-SC-455`, `-458`) | `MRQ-T4-01` |
| A4 | Partial issue, then short-close or full issue (`WH-SC-461`, `-466`) | `MRQ-T1-07`…`-09` |
| A5 | Shortfall handed to purchasing; absent when trade is off (`WH-SC-461`, `-462`) | `MRQ-T1-11` |
| A6 | Requesters see only their departments (`WH-SC-460`) | `MRQ-GRD-04` |
| A7 | Cancel only before anything is issued (`WH-SC-473`, `-474`) | `MRQ-T1-10`, `MRQ-GRD-09` |

---

## 1. T1 — State machine

### 1.1 Status inventory

| Entity | Status | Represented by | Reachable via | Exits via | Kind |
|---|---|---|---|---|---|
| Header | `DRAFT` | `status` | `-01`, `-04` | `-02`, `-10` | initial |
| Header | `SUBMITTED` | `status`; `submitted_by/at` | `-02` | `-03`, `-04`, `-05`, `-10` | active |
| Header | `APPROVED` | `status`; `approved_by/at` | `-03` | `-07`, `-09`, `-10` | active |
| Header | `PARTIALLY_ISSUED` | `status` | `-07` | `-07`, `-08`, `-09` | active |
| Header | `ISSUED` | `status`; `completed_at` | `-08` | none | **terminal** |
| Header | `CLOSED` | `status`; `closed_by/at`, reason | `-09` | none | **terminal** |
| Header | `REJECTED` | `status`; reason | `-05` | none | **terminal** |
| Header | `CANCELLED` | `status`; reason | `-10` | none | **terminal** |
| Line | `OPEN` · `APPROVED` · `PARTIALLY_ISSUED` · `ISSUED` · `CLOSED` · `REJECTED` · `CANCELLED` | `line_status` from `requested`, `approved`, `issued`, `returned`, `closed`, `cancelled` quantities | effects | — | derived |

Quantities per line (all stored, `DECIMAL(18,4)`, line UoM): `requested_quantity`, `approved_quantity`
(null until approval), `issued_quantity`, `returned_quantity` (fact only — never reopens), `closed_quantity`,
`cancelled_quantity`. Open-to-issue = `approved − issued − closed`.

### 1.2 Transitions

| ID | From | Event | To | Guard | Actor | Side effects | Reason? | UI |
|---|---|---|---|---|---|---|---|---|
| MRQ-T1-01 | — | Create: issuing site, department, cost object (type, id), purpose, required-by, priority, notes, lines (item, qty, UoM, required date, remarks, optional line cost object) | `DRAFT` | `MRQ-GRD-01`…`-04` | `wh_material_requisitions:create` | gapless `MRQ` number at create; `cost_object_ref` frozen | no | WS-268 **Add** |
| MRQ-T1-02 | `DRAFT` | Submit | `SUBMITTED` | ≥ 1 line | `:submit` | `submitted_by/at`; notify approvers (`MRQ-T3-01`) | no | WS-269 **Submit** |
| MRQ-T1-03 | `SUBMITTED` | **Approve** with `approved_quantity` per line (0 = reject the line) | `APPROVED` (≥ 1 line > 0) / `REJECTED` (all 0) | `MRQ-GRD-05`, `-06` | `:approve` | line `approved_quantity`; lines at 0 → `REJECTED`; `MRQ-T4-01` reservation | **yes** when any line approved < requested | WS-269 **Approve** modal |
| MRQ-T1-04 | `SUBMITTED` | Recall | `DRAFT` | actor is the requester | `:edit` | — | no | WS-269 **Recall** |
| MRQ-T1-05 | `SUBMITTED` | Reject (whole) | `REJECTED` | `MRQ-GRD-05` | `:approve` | — | **yes** | WS-269 **Reject** |
| MRQ-T1-06 | `SUBMITTED` (value > `requisition_second_approval_value`) | First approval | stays `SUBMITTED`, `first_approved_by/at` set | `MRQ-GRD-05` | `:approve` | second approver notified | no | same modal — *awaiting second approval* (`OD-29`) |
| MRQ-T1-07 | `APPROVED` · `PARTIALLY_ISSUED` | *(effect of a store-issue post, `SIR-T1-03`)* | `PARTIALLY_ISSUED` | — | `wh_store_issues:post` | line `issued_quantity` += | — | none (effect) |
| MRQ-T1-08 | `PARTIALLY_ISSUED` · `APPROVED` | *(effect)* every line issued + closed = approved | `ISSUED` | — | same | reservations fully consumed | — | none |
| MRQ-T1-09 | `APPROVED` · `PARTIALLY_ISSUED` | **Close short** (header or one line) | `CLOSED` (header when every line terminal) | — | `:close` (stores in-charge, or the requester for own requisitions) | open-to-issue → `closed_quantity`; reservation released; open hand-offs listed (not cancelled — the buyer decides) | **yes** | WS-269 **Close short**; WS-274 row action |
| MRQ-T1-10 | `DRAFT` · `SUBMITTED` · `APPROVED` with nothing issued | Cancel | `CANCELLED` | `MRQ-GRD-09` | `:cancel` | reservation released | **yes** | WS-269 **Cancel** |
| MRQ-T1-11 | line `APPROVED`/`PARTIALLY_ISSUED`, short > 0 | **Raise purchase requisition** for ≤ the short quantity | unchanged | `MRQ-GRD-10` | `:handoff` | `PurchaseRequisitionHandoff.raise(cmd)` returns `{module, documentType, documentId, documentRef}`; a `wh_material_requisition_line_handoffs` row (line, quantity, refs, `raised_by/at`) | no | WS-269 line action / WS-274 **Raise PR** |
| MRQ-T1-12 | — | Edit header/lines | unchanged | `DRAFT` only (approved quantities are never edited — re-approval means recall) | `:edit` | — | no | WS-269 **Edit** |

### 1.3 Guards

| ID | Predicate | Refusal | Backstop | Source |
|---|---|---|---|---|
| MRQ-GRD-01 | department active; the requester belongs to it (platform user department / `department_head_id`) or holds `view:all` | `422 REQUISITION_DEPARTMENT_NOT_ALLOWED` · `departmentId` | FK `departments(id)` | FR-529 |
| MRQ-GRD-02 | cost object type is an active `COST_OBJECT_TYPE` row with a registered `CostObjectResolver`, which validates the id (active, same company) | `422 COST_OBJECT_TYPE_UNSUPPORTED` / `422 COST_OBJECT_INVALID` · `costObjectId` | composite FK to the code list | FR-533 |
| MRQ-GRD-03 | each item is active, stock-holding (`STOCK`, `CONSUMABLE`, `PACKAGING`, … not `SERVICE`/`NON_STOCK`) and stocked at the issuing site's item-site row; qty > 0; required date ≥ today | `422 REQUISITION_ITEM_NOT_STOCKED` · `lines[i].itemId` | CHECK `requested_quantity > 0` | FR-529 |
| MRQ-GRD-04 | record-level scope: a user with `view` (not `view:all`) sees and acts only on requisitions whose department is one of theirs; other ids answer `404` | `404` | `WHERE` clause in every query (`P1-18`) | FR-529 |
| MRQ-GRD-05 | approver ≠ requester and ≠ `created_by` (`FR-408`); when `requisition_approver_scope = DEPARTMENT_HEAD`, approver is the department's `department_head_id` or `deputy_head_id`; a second approver ≠ the first | `403 APPROVER_IS_ACTOR` / `403 REQUISITION_APPROVER_NOT_HEAD` | — | FR-530 |
| MRQ-GRD-06 | `0 ≤ approved_quantity ≤ requested_quantity` | `422 APPROVED_EXCEEDS_REQUESTED` · `lines[i].approvedQuantity` | CHECK | FR-530 |
| MRQ-GRD-07 | an issue line references a requisition line of a requisition `APPROVED`/`PARTIALLY_ISSUED`, same site, and quantity ≤ open-to-issue | `422 ISSUE_EXCEEDS_APPROVED` (raised by `SIR-GRD-02`) | CHECK `issued_quantity + closed_quantity <= approved_quantity` | FR-535 |
| MRQ-GRD-08 | stock is reserved only from allocatable statuses (`MRN_PENDING`/`QC_HOLD` excluded) | short shown, not refused | `P0-09` | FR-531 |
| MRQ-GRD-09 | cancel only when Σ issued = 0 | `409 REQUISITION_TRANSITION_INVALID` naming *close short* | — | FR-530 |
| MRQ-GRD-10 | a `PurchaseRequisitionHandoff` bean is registered; Σ live hand-offs on the line + new ≤ short (= approved − issued − closed − available-reserved) | `409 PURCHASE_HANDOFF_UNAVAILABLE` / `422 HANDOFF_EXCEEDS_SHORT` | — | FR-528 |

### 1.4 Unreachable

| ID | Must never happen |
|---|---|
| MRQ-UNR-01 | a requisition creating or changing a `wh_demand_orders` row (`STO-D9`) |
| MRQ-UNR-02 | a store return reopening an `ISSUED`/`CLOSED` requisition |
| MRQ-UNR-03 | an approved quantity edited without recall |
| MRQ-UNR-04 | the requisition writing the ledger (only `SIR` posts) |
| MRQ-UNR-05 | an FK from `wh_material_requisition_line_handoffs` to a `wht_` table |

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from | Extra |
|---|---|---|---|---|
| MRQ-T2-01 | Create / edit | `:create` / `:edit` | — / `DRAFT` | own department |
| MRQ-T2-02 | Submit · Recall | `:submit` · `:edit` | `DRAFT` · `SUBMITTED` | requester |
| MRQ-T2-03 | Approve · Reject | `:approve` | `SUBMITTED` | `MRQ-GRD-05` |
| MRQ-T2-04 | Issue | `wh_store_issues:create/post` | `APPROVED`, `PARTIALLY_ISSUED` | `SIR` |
| MRQ-T2-05 | Close short | `:close` | `APPROVED`, `PARTIALLY_ISSUED` | reason |
| MRQ-T2-06 | Cancel | `:cancel` | nothing issued | reason |
| MRQ-T2-07 | Raise PR | `:handoff` | line short | trade on |
| MRQ-T2-08 | Print | `wh_print_jobs:create` | any but `DRAFT` | `SYS-MATERIAL-REQUISITION` |

## 3. T3 — Time-driven rules

| ID | Rule | Trigger | Changes | Notified | Job | Once? |
|---|---|---|---|---|---|---|
| MRQ-T3-01 | Pending approval | `SUBMITTED` > `warehouse.approval.pending_alert_hours` | nothing | approvers | `p2-23` alert | per episode |
| MRQ-T3-02 | **Overdue to issue** | open-to-issue > 0 and `required_by_date < today` (site TZ) | nothing — `overdueOnly` filter, WS-274 ageing | stores in-charge | daily | once per requisition |
| MRQ-T3-03 | Stale approved | `APPROVED`/`PARTIALLY_ISSUED` with no issue for `warehouse.stores.requisition_stale_days` (default 30) | nothing — tile; **never auto-closes** | requester + stores | daily | once |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in |
|---|---|---|---|
| MRQ-T4-01 | approval with `requisition_reservation = SOFT`/`HARD` | one reservation per line in `whb_reservations`, holder `(WAREHOUSE, MATERIAL_REQUISITION, id, line_no)`, quantity = min(approved, available-to-reserve); the shortfall is a computed field. *Amended for MFG MD-16:* **no reservation** when the line's cost-object resolver returns `reservationsFor(costObjectId, itemId)` non-empty (a `PRODUCTION_ORDER` already holds its component reservations from release); the line's `reserved` reads the owner's reservations | requisition service → reservation service, one transaction |
| MRQ-T4-02 | store-issue post | reservation consumed by the issue's `consumedReservationIds` (`WhbMovementPostCommand`), line `issued_quantity`, header ladder | issue service, same transaction |
| MRQ-T4-03 | close short / cancel | reservation released (reason context `RESERVATION_RELEASE`); an owner-held reservation (`MRQ-T4-01` amendment, MFG MD-16) is **not** released — the owner releases it | requisition service |
| MRQ-T4-04 | store-return post (`SIR-T1-07`) | line `returned_quantity` += ; status unchanged | return service |
| MRQ-T4-05 | hand-off | outbox `WH_REQUISITION_SHORTFALL_HANDED_OFF`; the buying module's later receipt is issued against the same line | handoff port |

## 5. T5 — Screen contract

### 5.1 WS-268 Material Requisitions (reference: **Service Vehicle**)

| | |
|---|---|
| **Grid** | `wh_material_requisitions` · scope `WAREHOUSE_MATERIAL_REQUISITION` · sort `e.created_at DESC` |
| **Tiles** | `SUBMITTED` · `APPROVED` · `PARTIALLY_ISSUED` · *Overdue to issue* · `ISSUED` this month |
| **Columns** | `requisitionNumber`, `warehouseName`, `departmentName`, `costObjectType`, `costObjectRef`, `purpose`, `requestedByName` (user display helper), `requiredByDate` (`formatDateSync`), `priority`, `lineCount`, `requestedQuantity`, `approvedQuantity`, `issuedQuantity`, `status`, `approvedByName`, `approvedAt`, audit |
| **Filters** | `warehouseId`; `departmentId` (own departments unless `view:all`); `costObjectType` → `costObjectId` (cascade, resolver-backed dropdown); `purpose`; `status` (multi); `requestedById`; `requiredFrom/To` (date); `overdueOnly`; `itemId` |
| **Row actions** | View · Edit · Submit · Recall · Approve · Reject · Issue (→ WS-271 pre-filled) · Close short · Cancel · Print |
| **Detail WS-269** | header; lines (`item`, `requested`, `approved`, `issued`, `returned`, `closed`, `available`, `reserved`, `short`, `status`, hand-off refs); issues tab; returns tab; history |
| **Export** | grid + lines sheet + `createdByName`, `updatedByName` |

### 5.2 WS-274 Issue queue (reference: **Customer**)

Grid `wh_material_requisition_issue_queue` (one row per open line): `requisitionNumber`, `departmentName`, `itemCode`, `itemName`, `openToIssue`, `available`, `reserved`, `short`, `requiredByDate`, `ageDays`, `priority`; filters site, department, item, `shortOnly`, `overdueOnly`; actions **Issue selected** (one store issue for the selected lines of one requisition), **Raise PR**, **Close short**. Backend-computed; no `.filter()` in the page.

## 6. Out of scope

Requisition of services; a multi-level approval matrix beyond `OD-29`'s optional second level; auto-PR; mobile.

## 7. Amendments

| Date | Change |
|---|---|
| 2026-10-22 | v0 derived |

## 8. Invariants and scenarios

`FR-408`; `P0-09` reservation balance; scenarios `WH-SC-455`, `-458`…`-462`, `-466`, `-473`, `-474`.

## 9. Open rows

| ID | Question | Default |
|---|---|---|
| MRQ-OPEN-01 | OD-29 | single level + optional value threshold |
| MRQ-OPEN-02 | Should a requisition for `PRODUCTION_ORDER` be created by MFG through a port rather than the screen? | yes — `warehouse-manufacturing` calls `WhMaterialRequisitionPort.create` (same service, `source_module` recorded); the screen also allows it when the resolver is present |
