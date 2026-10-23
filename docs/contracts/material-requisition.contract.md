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
| **Module** | `warehouse`; code lists in `warehouse-base` (`V501233`) |
| **Domain baseline** | `FR-408`, `FR-174`, `P0-09` reservations (open-item ledger, holder quad), `P1-18` record-level scope, `FR-528`…`FR-533`, `STO-D9`, `OD-29` |
| **Owning task** | `issues/p8-09.md`; owns the cost-object seam (`COST_OBJECT_TYPE` list, `CostObjectResolver`, `wh_cost_centres`) that `p8-10` applies to issue lines; depends on `p0-09`, `p1-18` |
| **Primary tables** | `wh_material_requisitions`, `wh_material_requisition_lines`, `wh_material_requisition_line_handoffs`, `wh_cost_centres` (`V511318`); code lists `REQUISITION_PURPOSE`, `COST_OBJECT_TYPE` (`V501233`); `whb_document_types` `MATERIAL_REQUISITION`; reservation holder type `MATERIAL_REQUISITION` |
| **Status columns** | header `status`, line `line_status` — no CHECK; line status recomputed from quantities by the service |
| **Permission resources** | `wh_material_requisitions:{view,view:all,view:branch,view_all_departments,create,edit,submit,approve,close,cancel,export,handoff}` (`V511408`). **Two axes, two verbs (R29 F1):** `:view:all` / `:view:branch` is the warehouse **site** scope pair (`V511000:60-71`, `WhbWarehouseScopeService.java:133-141` — without it a non-admin resolves `NONE`), exactly as on every warehouse resource; **`:view_all_departments`** is the **department** axis — without it a user sees only requisitions of departments they belong to (`MRQ-GRD-04`). Granting department-wide visibility never opens another site |
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
| MRQ-T1-03 | `SUBMITTED`, and **either** the estimated value ≤ `requisition_second_approval_value` (or the setting is null) **or** `first_approved_by` is set (R29 F16) | **Approve** (final) with `approved_quantity` per line (0 = reject the line) | `APPROVED` (≥ 1 line > 0) / `REJECTED` (all 0) | `MRQ-GRD-05`, `-06`, `-11` | `:approve` | line `approved_quantity`; lines at 0 → `REJECTED`; `MRQ-T4-01` reservation | **yes** when any line approved < requested | WS-269 **Approve** modal |
| MRQ-T1-04 | `SUBMITTED` | Recall | `DRAFT` | actor is the requester | `:edit` | **`first_approved_by/at` cleared** — a resubmission needs both approvals again (R29 F16) | no | WS-269 **Recall** |
| MRQ-T1-05 | `SUBMITTED` | Reject (whole) | `REJECTED` | `MRQ-GRD-05` | `:approve` | — | **yes** | WS-269 **Reject** |
| MRQ-T1-06 | `SUBMITTED`, value > `requisition_second_approval_value` **and** `first_approved_by` null — the only state in which `-03` is refused (R29 F16) | First approval | stays `SUBMITTED`, `first_approved_by/at` set | `MRQ-GRD-05`, `-11` | `:approve` | second approver notified | no | same modal — *awaiting second approval* (`OD-29`) |
| MRQ-T1-07 | `APPROVED` · `PARTIALLY_ISSUED` | *(effect of a store-issue post, `SIR-T1-03`)* | `PARTIALLY_ISSUED` | — | `wh_store_issues:post` | line `issued_quantity` += | — | none (effect) |
| MRQ-T1-08 | `PARTIALLY_ISSUED` · `APPROVED` | *(effect)* every approved line fully issued (issued = approved, closed = 0) | `ISSUED` | — | same | reservations fully consumed | — | none |
| MRQ-T1-09 | `APPROVED` · `PARTIALLY_ISSUED` | **Close short** (header or one line) | header `CLOSED` once every line is terminal **and any line was closed short** — closing the last open line short always gives `CLOSED`, never `ISSUED` (R29 F33) | — | `:close` (stores in-charge, or the requester for own requisitions) | open-to-issue → `closed_quantity`; reservation released; open hand-offs listed (not cancelled — the buyer decides) | **yes** | WS-269 **Close short**; WS-274 row action |
| MRQ-T1-10 | `DRAFT` · `SUBMITTED` · `APPROVED` with nothing issued | Cancel | `CANCELLED` | `MRQ-GRD-09` | `:cancel` | reservation released | **yes** | WS-269 **Cancel** |
| MRQ-T1-11 | line `APPROVED`/`PARTIALLY_ISSUED`, short > 0 | **Raise purchase requisition** for ≤ the short quantity | unchanged | `MRQ-GRD-10` | `:handoff` | `PurchaseRequisitionHandoff.raise(HandoffCommand)` returns `HandoffRef {module, documentType, documentId, documentRef}` (the buying document's **issued** number — the bean raises it before it returns); a `wh_material_requisition_line_handoffs` row (line, quantity, refs, `raised_by/at`) | no | WS-269 line action / WS-274 **Raise PR** |
| MRQ-T1-13 | any line with a hand-off | **Read hand-off status** (R29 F14) | — | — | `:view` | `PurchaseRequisitionHandoff.status(HandoffRef)` → `HandoffStatus {status, statusLabel, orderedQuantity, receivedQuantity, closed}`, read on WS-269 open; bean absent → the stored refs shown with *status unavailable* | — | WS-269 hand-off column |
| MRQ-T1-14 | `APPROVED` · `PARTIALLY_ISSUED`, a line with reserved < open-to-issue | **Top up reservations** (R29 F32) | unchanged | `MRQ-GRD-08` | `:approve` or `wh_store_issues:create` | reserves min(open-to-issue − reserved, available) per grain (`MRQ-T4-01`); also run by the daily `WhRequisitionReservationTopUpJob` oldest `required_by_date` first, so hand-off stock that arrives is protected | no | WS-269 / WS-274 **Top up** |
| MRQ-T1-12 | — | Edit header/lines | unchanged | `DRAFT` only (approved quantities are never edited — re-approval means recall) | `:edit` | — | no | WS-269 **Edit** |

### 1.3 Guards

| ID | Predicate | Refusal | Backstop | Source |
|---|---|---|---|---|
| MRQ-GRD-01 | department active; the requester belongs to it (platform user department / `department_head_id`) or holds `:view_all_departments` | `422 REQUISITION_DEPARTMENT_NOT_ALLOWED` · `departmentId` | FK `departments(id)` | FR-529 |
| MRQ-GRD-02 | cost object type is an active `COST_OBJECT_TYPE` row with a registered `CostObjectResolver`, which validates the id: active; **same company only where the target has a company** — `wh_cost_centres.company_id`, MFG orders; platform `departments` has no company column (`platform` `V13`), so `DEPARTMENT` checks active only (R29 F33) | `422 COST_OBJECT_TYPE_UNSUPPORTED` / `422 COST_OBJECT_INVALID` · `costObjectId` | composite FK to the code list | FR-533 |
| MRQ-GRD-03 | each item is active, stock-holding (`STOCK`, `CONSUMABLE`, `PACKAGING`, … not `SERVICE`/`NON_STOCK`) and stocked at the issuing site's item-site row; qty > 0; required date ≥ today | `422 REQUISITION_ITEM_NOT_STOCKED` · `lines[i].itemId` | CHECK `requested_quantity > 0` | FR-529 |
| MRQ-GRD-04 | record-level scope, two axes: the site tier from the scope pair (`WhbWarehouseScopeService`), then the department tier — a user without `:view_all_departments` sees and acts only on requisitions whose department is one of theirs; other ids answer `404` | `404` | `WHERE` clause in every query (`P1-18`) | FR-529 |
| MRQ-GRD-05 | approver ≠ requester and ≠ `created_by` (`FR-408`); when `requisition_approver_scope = DEPARTMENT_HEAD`, approver is the department's `department_head_id` or `deputy_head_id`; a second approver ≠ the first | `403 REQUISITION_SELF_APPROVAL` (core `<DOCUMENT>_SELF_APPROVAL` convention, R29 F26) / `403 REQUISITION_APPROVER_NOT_HEAD` | — | FR-530 |
| MRQ-GRD-06 | `0 ≤ approved_quantity ≤ requested_quantity` | `422 APPROVED_EXCEEDS_REQUESTED` · `lines[i].approvedQuantity` | CHECK | FR-530 |
| MRQ-GRD-07 | an issue line references a requisition line of a requisition `APPROVED`/`PARTIALLY_ISSUED`, same site, and quantity ≤ open-to-issue | `422 ISSUE_EXCEEDS_APPROVED` (raised by `SIR-GRD-02`) | CHECK `issued_quantity + closed_quantity <= approved_quantity` | FR-535 |
| MRQ-GRD-08 | stock is reserved only from allocatable statuses (`MRN_PENDING`/`QC_HOLD` excluded) | short shown, not refused | `P0-09` | FR-531 |
| MRQ-GRD-09 | cancel only when Σ issued = 0 | `409 REQUISITION_TRANSITION_INVALID` naming *close short* | — | FR-530 |
| MRQ-GRD-10 | a `PurchaseRequisitionHandoff` bean is registered; Σ live hand-offs on the line + new ≤ short (= approved − issued − closed − available-reserved) | `409 PURCHASE_HANDOFF_UNAVAILABLE` / `422 HANDOFF_EXCEEDS_SHORT` | — | FR-528 |
| MRQ-GRD-11 | the two approval transitions are mutually exclusive (`-03` needs value ≤ threshold or a first approval; `-06` needs value > threshold and no first approval) | `409 REQUISITION_SECOND_APPROVAL_REQUIRED` / `409 REQUISITION_ALREADY_FIRST_APPROVED` | — | FR-530 |

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
| MRQ-T4-01 | approval (and `MRQ-T1-14` top-up) with `requisition_reservation = SOFT`/`HARD` | **reservations per grain** (R29 F4): a `whb_reservations` row needs a location and a status (`WhbReservationService.java:136-139`), so the approved quantity is reserved as one row per (location, lot, status `AVAILABLE`) picked FEFO for expiry-managed items, else FIFO by lot receipt date, until min(approved, available-to-reserve) is held — every row with holder `(WAREHOUSE, MATERIAL_REQUISITION, requisition id, line_no)`; the shortfall is a computed field. **`SOFT`** = `TYPE_SOFT` with `expires_at = approved_at + warehouse.stores.requisition_soft_hold_days` (default 7; the expiry job releases it, `WhbReservation.java:55`); **`HARD`** = `TYPE_HARD`, ended only by consume, close, cancel or explicit release (`:58`) (R29 F32). *Amended for MFG MD-16, sharpened by R29 MFG-F12:* **no reservation whenever the line's resolver declares `ownsReservations() = true`** (MFG's `PRODUCTION_ORDER`) — decided by the cost-object **type**, never by whether `reservationsFor` happens to return rows, so an order released short, with a `NONE` policy or with an expired `SOFT` hold never gets requisition-owned holds; the line's `reserved` reads `reservationsFor(costObjectId, itemId)` | requisition service → reservation service, one transaction · `STO-D18` (R30 `CP-FR-014`) |
| MRQ-T4-02 | store-issue post | **consume-and-split inside the issue transaction** (R29 F4): per issue line, the line's open holds at the issued grain are locked (`WhbReservationStore.lockForRelease`) and consumed up to the issued base quantity with `WhbReservationStore.consume(hold, movementLineId, …)` (`:232`, closes the whole hold); when a hold is larger than what was issued, a residual hold for the remainder is inserted at once (`WhbReservationStore.insert`, same holder quad, grain, type and expiry — the shape of `WhbPickReservationService.reattach` `:137`). Then holds of the line at other grains are trimmed (released and re-inserted smaller) until Σ open holds ≤ open-to-issue. The same call is also passed as `consumedReservationIds` so the writer's availability check does not count them (`WhbMovementPostCommand.java:23-25`). **Owner-held holds (MFG):** core consumes them in the same way, by the ids `reservationsFor` returns, and passes the consumed and residual ids to `onIssuePosted` — MFG never consumes them itself. Line `issued_quantity`, header ladder | issue service, same transaction |
| MRQ-T4-03 | close short / cancel | the line's own holds released (reason context `RESERVATION_RELEASE`, `releaseByHolder`); an owner-held reservation (`ownsReservations()`, MFG MD-16) is **not** released — the owner releases it | requisition service |
| MRQ-T4-04 | store-return post (`SIR-T1-07`) | line `returned_quantity` += ; status unchanged | return service |
| MRQ-T4-05 | hand-off | outbox `WH_REQUISITION_SHORTFALL_HANDED_OFF`; the buying module's later receipt is issued against the same line | handoff port |

## 5. T5 — Screen contract

### 5.1 WS-268 Material Requisitions (reference: **Service Vehicle**)

| | |
|---|---|
| **Grid** | `wh_material_requisitions` · scope `WAREHOUSE_MATERIAL_REQUISITION` · sort `e.created_at DESC` |
| **Tiles** | `SUBMITTED` · `APPROVED` · `PARTIALLY_ISSUED` · *Overdue to issue* · `ISSUED` this month |
| **Columns** | `requisitionNumber`, `warehouseName`, `departmentName`, `costObjectType`, `costObjectRef`, `purpose`, `requestedByName` (user display helper), `requiredByDate` (`formatDateSync`), `priority`, `lineCount`, `requestedQuantity`, `approvedQuantity`, `issuedQuantity`, `status`, `approvedByName`, `approvedAt`, audit |
| **Filters** | `warehouseId`; `departmentId` (own departments unless `:view_all_departments`); `costObjectType` → `costObjectId` (cascade, resolver-backed dropdown); `purpose`; `status` (multi); `requestedById`; `requiredFrom/To` (date); `overdueOnly`; `itemId` |
| **Row actions** | View · Edit · Submit · Recall · Approve · Reject · Issue (→ WS-271 pre-filled) · Close short · Cancel · Print |
| **Detail WS-269** | header; lines (`item`, `requested`, `approved`, `issued`, `returned`, `closed`, `available`, `reserved`, `short`, `status`, hand-off refs); issues tab; returns tab; history |
| **Export** | grid + lines sheet + `createdByName`, `updatedByName` |

### 5.2 WS-274 Issue queue (reference: **Customer**)

Grid `wh_material_requisition_issue_queue` (one row per open line): `requisitionNumber`, `departmentName`, `itemCode`, `itemName`, `openToIssue`, `available`, `reserved`, `short`, `requiredByDate`, `ageDays`, `priority`; filters site, department, item, `shortOnly`, `overdueOnly`; actions **Issue selected** (one store issue for the selected lines of one requisition), **Raise PR**, **Close short**. Backend-computed; no `.filter()` in the page. **R30 `CP-SC-006`:** scope `WAREHOUSE_REQUISITION_ISSUE_QUEUE`; `default_columns` = the columns above, `default_filters` = site, department, `shortOnly`, `overdueOnly` (`STO-D22`); export = the visible columns (a read-only queue — no audit columns on the grid, so none in the export).

## 6. Out of scope

Requisition of services; a multi-level approval matrix beyond `OD-29`'s optional second level; auto-PR; mobile.

## 7. Amendments

| Date | Change |
|---|---|
| 2026-10-22 | v0 derived |
| 2026-10-22 | Amended for MFG MD-16: owner-held reservations (`MRQ-T4-01`, `-03`); `WhMaterialRequisitionPort` named (`MRQ-OPEN-02`) |
| 2026-10-22 | R29 dispositions: site scope pair + `:view_all_departments`; mutually exclusive approvals, recall clears the first approval; per-grain reservations, SOFT/HARD, top-up, consume-and-split, core consumes owner-held holds; `ownsReservations()` by type; close-short header outcome; department company rule; hand-off status row; §8a port rows; self-approval code |

## 8. Invariants and scenarios

`FR-408`; `P0-09` reservation balance; scenarios `WH-SC-455`, `-458`…`-462`, `-466`, `-473`, `-474`.

## 8a. `WhMaterialRequisitionPort` — requisitions raised by a sibling (R29 F14, MFG-F4)

`ai.warehouse.port.stores.WhMaterialRequisitionPort`, a façade over `WhMaterialRequisitionService` (no
second write path). Used by `warehouse-manufacturing` for production-order requisitions.

| ID | From | Event | To | Guard | Actor | Side effects | Reason? |
|---|---|---|---|---|---|---|---|
| MRQ-T1-20 | — | **`create(CreateRequisitionCommand)`** — site, department, cost object (type, id), purpose, required-by, lines; `sourceModule`, `sourceDocumentType/Id/Ref`, `idempotencyKey`, `actingUserId`, `initialStatus` (`DRAFT` / `APPROVED`), `approvedByUserId` | `DRAFT`, or `APPROVED` with `approved_quantity = requested_quantity` per line | `MRQ-GRD-01`…`-03`, `-20`, `-21`; `APPROVED` needs `approvedByUserId` (`422 PORT_APPROVER_REQUIRED`) and skips `MRQ-GRD-05` — the maker ≠ checker check is the source's (its order release), recorded `approval_source = SOURCE_MODULE` | acting user + `warehouse:orders:port` + `wh_material_requisitions:create` | `source_*` recorded; gapless `MRQ` number; `MRQ-T4-01` (no reservation for an `ownsReservations()` type) | no |
| MRQ-T1-21 | `DRAFT` · `SUBMITTED` · `APPROVED` with Σ issued = 0 | **`cancel(requisitionId, reason, sourceModule, idempotencyKey)`** | `CANCELLED` | Σ issued = 0 else `409 REQUISITION_TRANSITION_INVALID`. On an already terminal requisition with nothing issued (`REJECTED`, `CLOSED`, `CANCELLED`) the call **succeeds as a no-op** and returns the current status — so a sibling's order cancel/unrelease is never blocked by a rejected or short-closed requisition (MFG-F4: the sibling blocks only on Σ issued > 0, read from `-23`) | acting user + port authority + `wh_material_requisitions:cancel` | `MRQ-T4-03` | **yes** |
| MRQ-T1-22 | `APPROVED` · `PARTIALLY_ISSUED` | **`close(requisitionId, reason, sourceModule, idempotencyKey)`** — close short every open line | `CLOSED` (`MRQ-T1-09`) | — ; a replay on `CLOSED` returns it | acting user + port authority + `wh_material_requisitions:close` | `MRQ-T4-03` | **yes** |
| MRQ-T1-23 | any | **`getRequisitionPosition(requisitionId)`** | — | — | port + `:view` | status and per line requested, approved, issued, returned, closed, cancelled, reserved, open-to-issue | — |
| MRQ-T1-24 | port-owned requisition | **Manual** edit / submit / approve / reject / cancel / close on WS-268/269 | refused or allowed | every `MaterialRequisitionChangeGuard` bean is asked first; none registered → allowed | `:edit` etc. | WS-269 shows *Managed by <module>* | — |

| ID | Predicate | Refusal |
|---|---|---|
| MRQ-GRD-20 | idempotency per `POS-GRD-07` (operation registry; the create's key also on the header, partial uk `(source_module, idempotency_key)`) | `409 PORT_IDEMPOTENCY_CONFLICT` |
| MRQ-GRD-21 | manual change on a port-owned requisition allowed only if every `MaterialRequisitionChangeGuard` allows | `409 REQUISITION_OWNED_BY_SOURCE_MODULE` (raised by the guard) |

## 9. Open rows

| ID | Question | Default |
|---|---|---|
| MRQ-OPEN-01 | OD-29 | single level + optional value threshold |
| MRQ-OPEN-02 | Should a requisition for `PRODUCTION_ORDER` be created by MFG through a port rather than the screen? | yes — §8a (`WhMaterialRequisitionPort`); the screen also allows it when the resolver is present, and the requisition is then not port-owned |
