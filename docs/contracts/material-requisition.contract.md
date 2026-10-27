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
| **Primary tables** | `wh_material_requisitions`, `wh_material_requisition_lines`, `wh_material_requisition_line_handoffs`, `wh_cost_centres` (`V511318`) — the header also carries `owner_id UUID NOT NULL → whb_owners` (house owner types only: DB trigger in the `V510212` shape plus a service guard, `L-14`; P8 decision `G2`), `approval_source`, `reject_reason_code_id`, `reject_note`, `estimated_value DECIMAL(19,4)` (`MRQ-GRD-11`) and the once-only latches `overdue_alert_raised_at` (`MRQ-T3-02`) and `stale_alert_raised_at` (`MRQ-T3-03`); each line carries `soft_hold_until TIMESTAMPTZ` (`MRQ-T4-01`, P8 decision `G12`) and a CHECK that a line cost-object override is all-or-none; numbering through `WhbDocumentNumberIssuer.issue` (`MANDATORY` transaction) with an `MRQ` series seeded per site like `WO`; code lists `REQUISITION_PURPOSE`, `COST_OBJECT_TYPE`, the requisition close / cancel / reject reason contexts and codes, and the event type `material_requisition.shortfall_handed_off` (`V501233`); `whb_document_types` `MATERIAL_REQUISITION`; reservation holder type `MATERIAL_REQUISITION` |
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

| ID | From | Event | To | Guard | Actor | Side effects | Reason? | UI | Source |
|---|---|---|---|---|---|---|---|---|---|
| MRQ-T1-01 | — | Create: issuing site, department, stock owner (defaults when exactly one eligible house owner is linked to the site's company, else required — `422 OWNER_REQUIRED · ownerId`, validated by `validateOwner`, P8 `G2`), cost object (type, id), purpose, required-by, priority, notes, lines (item, qty, UoM, required date, remarks, optional line cost object) | `DRAFT` | `MRQ-GRD-01`…`-04` | `wh_material_requisitions:create` | gapless `MRQ` number at create; `cost_object_ref` frozen | no | WS-268 **Add** | — |
| MRQ-T1-02 | `DRAFT` | Submit | `SUBMITTED` | ≥ 1 line; enough eligible approvers (`MRQ-GRD-05`, `422 REQUISITION_NO_ELIGIBLE_APPROVER · departmentId`, P8 `G4`) | `:submit`, and the actor is the requester **or the creator** (as Recall, `MRQ-T2-02`; `403 REQUISITION_SUBMIT_NOT_REQUESTER`, P8-09 S5) | `submitted_by/at`; `estimated_value` frozen (`MRQ-GRD-11`; recomputed on resubmit after Recall); notify approvers (`MRQ-T3-01`) | no | WS-269 **Submit** | — |
| MRQ-T1-03 | `SUBMITTED`, and **either** the estimated value ≤ `requisition_second_approval_value` (or the setting is null) **or** `first_approved_by` is set (R29 F16) | **Approve** (final) with `approved_quantity` per line (0 = reject the line) | `APPROVED` (≥ 1 line > 0) / `REJECTED` (all 0) | `MRQ-GRD-05`, `-06`, `-11` | `:approve` | line `approved_quantity`; lines at 0 → `REJECTED`; `MRQ-T4-01` reservation | **yes** when any line approved < requested — a free-text `approval_note`, not a reason code (`422 REQUISITION_APPROVAL_NOTE_REQUIRED · approvalNote`, P8-09 S4) | WS-269 **Approve** modal | — |
| MRQ-T1-04 | `SUBMITTED` | Recall | `DRAFT` | actor is the requester **or the creator** (P8-09 S4 F4); every change guard asked (`MRQ-T1-24`) | `:edit` (endpoint and both UI gates) | **`first_approved_by/at` cleared** — a resubmission needs both approvals again (R29 F16) | no | WS-269 **Recall** | — |
| MRQ-T1-05 | `SUBMITTED` | Reject (whole) | `REJECTED` | `MRQ-GRD-05` | `:approve` | `reject_reason_code_id` (requisition reject context, `V501233`) and `reject_note` stored | **yes** | WS-269 **Reject** | — |
| MRQ-T1-06 | `SUBMITTED`, value > `requisition_second_approval_value` **and** `first_approved_by` null — the only state in which `-03` is refused (R29 F16) | First approval | stays `SUBMITTED`, `first_approved_by/at` set | `MRQ-GRD-05`, `-11` | `:approve` | second approver notified | no | same modal — *awaiting second approval* (`OD-29`) | — |
| MRQ-T1-07 | `APPROVED` · `PARTIALLY_ISSUED` | *(effect of a store-issue post, `SIR-T1-03`)* | `PARTIALLY_ISSUED` | — | `wh_store_issues:post` | line `issued_quantity` += | — | none (effect) | FR-532 |
| MRQ-T1-08 | `PARTIALLY_ISSUED` · `APPROVED` | *(effect)* every approved line fully issued (issued = approved, closed = 0) **and no line's `excess_approval_status` is `PENDING`** — a line whose standard part is fully issued while its excess waits keeps the header `PARTIALLY_ISSUED` (R32-fix F-R32CQ-006) | `ISSUED` | — | same | reservations fully consumed | — | none | — |
| MRQ-T1-09 | `APPROVED` · `PARTIALLY_ISSUED` | **Close short** (header or one line) | header `CLOSED` once every line is terminal **and any line was closed short** — closing the last open line short always gives `CLOSED`, never `ISSUED` (R29 F33) | — | `:close` — its holders only (S4b; the requester closes only when they also hold `:close`) | open-to-issue → `closed_quantity`; reservation released; open hand-offs listed (not cancelled — the buyer decides) | **yes** | WS-269 **Close short**; WS-274 row action | — |
| MRQ-T1-10 | `DRAFT` · `SUBMITTED` · `APPROVED` with nothing issued | Cancel | `CANCELLED` | `MRQ-GRD-09` | `:cancel` | reservation released | **yes** | WS-269 **Cancel** | — |
| MRQ-T1-11 | line `APPROVED`/`PARTIALLY_ISSUED`, short > 0 | **Raise purchase requisition** for ≤ the short quantity | unchanged | `MRQ-GRD-10` | `:handoff` | `PurchaseRequisitionHandoff.raise(HandoffCommand)` returns `HandoffRef {module, documentType, documentId, documentRef}` (the buying document's **issued** number — the bean raises it before it returns); a `wh_material_requisition_line_handoffs` row (line, quantity, refs, `raised_by/at`) | no | WS-269 line action / WS-274 **Raise PR** | FR-532 |
| MRQ-T1-13 | any line with a hand-off | **Read hand-off status** (R29 F14) | — | — | `:view` | `PurchaseRequisitionHandoff.status(HandoffRef)` → `HandoffStatus {status, statusLabel, orderedQuantity, receivedQuantity, closed}`, read on WS-269 open; bean absent → the stored refs shown with *status unavailable* | — | WS-269 hand-off column | — |
| MRQ-T1-14 | `APPROVED` · `PARTIALLY_ISSUED`, a line with reserved < open-to-issue | **Top up reservations** (R29 F32) | unchanged | `MRQ-GRD-08` | `:approve` (as `MRQ-T2-09`; S4b R6) | reserves min(open-to-issue − reserved, available) per grain (`MRQ-T4-01`); also run by the daily `WhRequisitionReservationTopUpJob` oldest `required_by_date` first, so hand-off stock that arrives is protected. The job tops up only HARD lines and SOFT lines whose window is open (`soft_hold_until` > now); a manual **Top up** after expiry renews `soft_hold_until = now + soft_hold_days` (audited) — no silent auto-renewal of a lapsed claim (P8 decision `G12`). **A NULL window** (policy changed from `HARD`/`NONE` to `SOFT` after approval) is stamped `now + soft_hold_days` on the first SOFT top-up, by the job or by hand, before any hold is inserted — a SOFT hold is never inserted with a NULL `expires_at` (P8-09 S4). The job reads only lines still short of their own live holds (a SOFT hold past `expires_at` does not count), oldest need first (`COALESCE(line required_date, required_by_date)`), keyset-paged past the first batch; a reservation-owning cost object is never a candidate (P8-09 S4 F12). The reservation sweep closes the grain's expired SOFT holds first, as the allocator does. Every change guard is asked (`MRQ-T1-24`) | no | WS-269 / WS-274 **Top up** | — |
| MRQ-T1-12 | — | Edit header/lines | unchanged | `DRAFT` only (approved quantities are never edited — re-approval means recall) | `:edit` | — | no | WS-269 **Edit** | — |
| MRQ-T1-25 | — / `DRAFT` | Create / edit with cost object `DEMAND_ORDER` (SO sample) or a `REPLACEMENT` line, an SO / job-card / operation reference (R32) | `DRAFT` | `MRQ-GRD-22` | requester | `sales_order_ref`, `customer_ref`, line `operation_seq`, `operation_ref`, `job_card_ref`, `replacement_of_*` frozen | no | WS-269 | FR-713 |
| MRQ-T1-26 | `APPROVED` | **Reserve** honouring `preferred_lot_id` / `lot_preference_mode` | reservation held | `MRQ-GRD-25` | system | `PREFERRED` → that lot first, then FEFO / FIFO; `ONLY` → that lot alone, shortfall shown | no | WS-269 / WS-274 | FR-713 |
| MRQ-T1-27 | header `APPROVED` · `PARTIALLY_ISSUED` (issue progress does not matter, R32-fix F-R32CQ-006), a line with `excess_approval_status = PENDING` | **Approve / reject excess** per line (higher level) | line `excess_approval_status` `APPROVED` (the excess becomes issuable; `MRQ-T1-14` top-up reserves it in the same transaction) / `REJECTED` (`approved_quantity` −= the excess; only the standard part stays issuable) | `MRQ-GRD-23` | `wh_material_requisitions:approve_excess` | **its own engine request**, tracked apart from issue progress: when the standard request is approved (`onApproved`) and any line has excess > 0, a second `MATERIAL_REQUISITION` request is opened for the requisition with the frozen condition `excess_over_standard` (`DAP` §0.1) — one `PERMISSION_HOLDER` level of `:approve_excess`, `requiresDocumentScreen` (per-line decision), `excludedActorIds` = requester, creator and every approver of the standard request; lines go `NOT_REQUIRED` → `PENDING` at open. **Close short** of a line with a pending excess sets it `WITHDRAWN`; header close-short or cancel withdraws the request (`WITHDRAWN`); a reject needs a reason (`APPROVAL_REJECT`). **R33 (#570 S4):** a matching `MATERIAL_REQUISITION` rule routes the excess request, but every rule level demands `:approve_excess` (a rule never lowers it to `:approve`), and a zero-level rule outcome is replaced by the document-defined `:approve_excess` level — an excess is never decided without a human holder of it (F4); `excludedActorIds` also names the source approver of a port `APPROVED` create (`MRQ-T1-20`), who has no standard request in the history (F3); **Close Line** is allowed on a line whose only remainder is its pending excess and withdraws it (F6); a decision with nothing pending (a replay) is `409 APPROVAL_STEP_NOT_PENDING` and writes nothing (F9) | yes | WS-269 *Excess* tab; WS-285 | FR-713 |
| MRQ-T1-28 | — | **Create post-facto requisition** from an emergency store issue (`SIR-T1-10`) | `SUBMITTED`, `requisition_kind = EMERGENCY_POST_FACTO`, `ratification_status = PENDING` | `MRQ-GRD-24`; ratifier check **before** the issue posts (R32-fix F-R32CQ-031): the `MRQ-GRD-05` department head / deputy when one is eligible (≠ issuer, ≠ requester); otherwise the ratification level falls back to the site's `wh_material_requisitions:approve` holders (stores-manager bundle) ≠ issuer ≠ requester; none at all → the emergency post is refused `422 REQUISITION_NO_ELIGIBLE_APPROVER` · `departmentId` and nothing posts | system, in the issue's posting transaction | lines = issued lines, approved = issued, no reservation; the Submit-time eligibility refusal of `MRQ-T1-02` is replaced by this pre-post check, so the requisition never waits with no ratifier; a pending ratification escalates by `DAP-T3-02`. **MANDATORY (#570 S4):** `SIR-T1-10` (P8-10) creates it only through `WhMaterialRequisitionPostFactoService.createPostFacto` (`@Transactional(propagation = MANDATORY)`), never by injecting `WhMaterialRequisitionService` — the facade is what guarantees the requisition joins the posting transaction and rolls back with it **#571 S4:** one requisition line per ITEM of the emergency issue (its lines of one item share unit and cost object, `EMERGENCY_LINE_ITEM_MISMATCH`), quantities summed. | no | WS-268 *Awaiting ratification* filter | FR-713 |
| MRQ-T1-29 | `SUBMITTED` post-facto | **Ratify** / **Refuse** (reason) | `ISSUED` + `RATIFIED` / `CLOSED` + `REFUSED` | `MRQ-GRD-05`, `MRQ-GRD-24` | the ratifier `MRQ-T1-28` resolved: the department's head or deputy holding `:approve` (site and department in scope) when one is eligible, else the site's `wh_material_requisitions:approve` holders — never the issuer or the requester (OD-8; #570 S4c) | refused: the site's `:approve` holders and the department's head and deputy are notified in-app, minus the refuser; the issue shows *Refused on ratification*; no stock effect (`STO-D11`) **#571 S4 P5:** the issue shows the outcome beside its post-facto number on WS-270, WS-271, the View modal and the export. | refuse only | WS-269 | FR-713 |

### 1.3 Guards

| ID | Predicate | Refusal | Backstop | Source |
|---|---|---|---|---|
| MRQ-GRD-01 | department active; the requester belongs to it (platform user department / `department_head_id`) or holds `:view_all_departments` | `422 REQUISITION_DEPARTMENT_NOT_ALLOWED` · `departmentId` | FK `departments(id)` | FR-529 |
| MRQ-GRD-02 | cost object type is an active `COST_OBJECT_TYPE` row with a registered `CostObjectResolver`, which validates the id: active; **same company only where the target has a company** — `wh_cost_centres.company_id`, MFG orders; platform `departments` has no company column (`platform` `V13`), so `DEPARTMENT` checks active only (R29 F33) | `422 COST_OBJECT_TYPE_UNSUPPORTED` / `422 COST_OBJECT_INVALID` · `costObjectId` | composite FK to the code list | FR-533 |
| MRQ-GRD-03 | each item is active, stock-holding (`STOCK`, `CONSUMABLE`, `PACKAGING`, … not `SERVICE`/`NON_STOCK`) (the item type's `whb_item_types.is_stocked` flag — the registry flag, not a code list); **no item-site row is required** (`whb_item_site_settings` is an optional override with no stocked flag; P8-09 S1 `G16`); qty > 0; required date ≥ the site-local today (`whb_warehouses.timezone`) | `422 REQUISITION_ITEM_NOT_STOCKED` · `lines[i].itemId` | CHECK `requested_quantity > 0` | FR-529 |
| MRQ-GRD-04 | record-level scope, two axes: the site tier from the scope pair (`WhbWarehouseScopeService`), then the department tier — a user without `:view_all_departments` sees and acts only on requisitions whose department is one of theirs; other ids answer `404`. **Secondary surfaces (P8-09 S4 F1):** the same department tier binds the cost-objects picker and the `DEPARTMENT` cost-object resolver (a `DEPARTMENT` cost object outside the caller's department scope answers *does not exist*), the item master-merge preview, and the `MRQ-T3-02`/`-03` recipients | `404` | `WHERE` clause in every query (`P1-18`) | FR-529 |
| MRQ-GRD-05 | approver ≠ requester and ≠ `created_by` (`FR-408`); when `requisition_approver_scope = DEPARTMENT_HEAD`, approver is the department's `department_head_id` or `deputy_head_id`; a second approver ≠ the first. **No eligible approver (P8 decision `G4`):** Submit refuses when the eligible approvers (active, `:approve`, in scope, ≠ requester, ≠ creator; under `DEPARTMENT_HEAD`, only the head and deputy) number fewer than one, or fewer than two distinct people when `estimated_value` is above `requisition_second_approval_value` (`MRQ-T1-06` → `-03`); the approver is never silently widened to `ANY_APPROVER`; approvers are re-checked at approve; Recall and Cancel stay available | `403 REQUISITION_SELF_APPROVAL` (core `<DOCUMENT>_SELF_APPROVAL` convention, R29 F26) / `403 REQUISITION_APPROVER_NOT_HEAD` / `422 REQUISITION_NO_ELIGIBLE_APPROVER` · `departmentId` | — | FR-530 |
| MRQ-GRD-06 | `0 ≤ approved_quantity ≤ requested_quantity` | `422 APPROVED_EXCEEDS_REQUESTED` · `lines[i].approvedQuantity` | CHECK | FR-530 |
| MRQ-GRD-07 | an issue line references a requisition line of a requisition `APPROVED`/`PARTIALLY_ISSUED`, same site, and quantity ≤ open-to-issue | `422 ISSUE_EXCEEDS_APPROVED` (raised by `SIR-GRD-02`) | CHECK `issued_quantity + closed_quantity <= approved_quantity` | FR-535 |
| MRQ-GRD-08 | stock is reserved only from allocatable statuses (`MRN_PENDING`/`QC_HOLD` excluded) | short shown, not refused | `P0-09` | FR-531 |
| MRQ-GRD-09 | cancel only when Σ issued = 0 | `409 REQUISITION_TRANSITION_INVALID`; once anything is issued the message names *Close short* ("has stock issued against it and cannot be cancelled - use Close short to end it", P8-09 S5) | — | FR-530 |
| MRQ-GRD-10 | a `PurchaseRequisitionHandoff` bean is registered (else the action is absent and the endpoint answers `409`); Σ live hand-offs on the line + new ≤ short. **Definitions (P8-09 S1 `G20`):** short = max(0, open-to-issue − reserved), and under policy `NONE` the free available quantity stands in for reserved — **available** is the allocator's own candidate rule (`WhbAllocationRepository.ALLOCATABLE`, the hard-expiry guard on the site-local date) with expired SOFT holds not counted as reserved, and under `NONE` one free pool of the site, owner and item is shared across the open lines, oldest required-by date first (then requisition number, line), in SQL, so one free unit is never offered to two lines (P8-09 S4 F10); for a reservation-owning cost object reserved is the holds its `reservationsFor` names (S4 F8); a hand-off is **live** until its `status().closed` is true — an unavailable status is never treated as closed or as zero. Checked with the requisition line locked (`FOR UPDATE`) and short and Σ hand-offs recomputed under the lock, so of two concurrent *Raise PR* one is refused; the hand-off row id is generated before `raise()` (key `MRQ_HANDOFF:<id>`). Close and cancel list the open hand-offs and do not cancel them | `409 PURCHASE_HANDOFF_UNAVAILABLE` / `422 HANDOFF_EXCEEDS_SHORT` | — | FR-528 |
| MRQ-GRD-11 | the two approval transitions are mutually exclusive (`-03` needs value ≤ threshold or a first approval; `-06` needs value > threshold and no first approval). **The value (P8 decision `G17`, `OD-29`):** `estimated_value` = Σ requested base quantity × the latest positive, non-reversed receipt-layer unit cost for (company, owner, item, site), in company currency, frozen at Submit and recomputed on resubmit after Recall; NULL when no layer exists, and **0** (not NULL) when the latest layers carry a zero unit cost — a zero estimate counts as **below** the threshold, one approval (P8-09 S5, recorded from the code); with `requisition_second_approval_value` set, NULL is treated as above it (two approvals; the hand-off path for never-stocked items stays open). The reader is written once beside `WhbOpenCostLayerSql` | `409 REQUISITION_SECOND_APPROVAL_REQUIRED` / `409 REQUISITION_ALREADY_FIRST_APPROVED` | — | FR-530 |
| MRQ-GRD-12 | one line per item on a requisition (P8-09 S4: recorded from the code) | `422 REQUISITION_LINE_DUPLICATE_ITEM` · `lines[i].itemId` | — | FR-529 |
| MRQ-GRD-22 | a `DEMAND_ORDER` cost object resolves to a core demand order of the same company that is not cancelled; a `REPLACEMENT` line names what it replaces | `422 COST_OBJECT_NOT_FOUND` · `422 REPLACEMENT_SOURCE_REQUIRED` · `lines[i].replacementOfId` | — | FR-713 |
| MRQ-GRD-23 | a line with excess over the resolver's standard balance needs an excess reason, and only its standard part is issuable — open-to-issue = approved − issued − closed − (excess only while `excess_approval_status` = `PENDING`; a rejected excess has already left `approved_quantity` once, and a withdrawn one closes with the line — S1 G5, #570 S4c), and reservations cover only the standard part — until a person who has not approved this requisition approves the excess on its own request (`MRQ-T1-27`, R32-fix F-R32CQ-006) | `422 EXCESS_REASON_REQUIRED` · `403 REQUISITION_SELF_APPROVAL` · `422 ISSUE_EXCEEDS_APPROVED` | — | FR-713 |
| MRQ-GRD-24 | a post-facto requisition is created only by an emergency issue and is never edited, recalled or cancelled | `409 REQUISITION_TRANSITION_INVALID` | `origin_store_issue_id NOT NULL` when `requisition_kind = EMERGENCY_POST_FACTO` (CHECK) | FR-713 |
| MRQ-GRD-25 | a preferred lot is of the line's item and allocatable at the issuing site | `422 PREFERRED_LOT_INVALID` · `lines[i].preferredLotId` | — | FR-713 |

### 1.4 Unreachable

| ID | Must never happen |
|---|---|
| MRQ-UNR-01 | a requisition creating or changing a `wh_demand_orders` row (`STO-D9`) |
| MRQ-UNR-02 | a store return reopening an `ISSUED`/`CLOSED` requisition |
| MRQ-UNR-03 | an approved quantity edited without recall |
| MRQ-UNR-04 | the requisition writing the ledger (only `SIR` posts) |
| MRQ-UNR-05 | an FK from `wh_material_requisition_line_handoffs` to a `wht_` table |

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from | Extra | Source |
|---|---|---|---|---|---|
| MRQ-T2-01 | Create / edit | `:create` / `:edit` | — / `DRAFT` | own department | — |
| MRQ-T2-02 | Submit · Recall | `:submit` · `:edit` | `DRAFT` · `SUBMITTED` | requester (Recall: requester or creator, `MRQ-T1-04`) | — |
| MRQ-T2-03 | Approve · Reject | `:approve` | `SUBMITTED` | `MRQ-GRD-05` | — |
| MRQ-T2-04 | Issue | `wh_store_issues:create/post` | `APPROVED`, `PARTIALLY_ISSUED` | `SIR` | — |
| MRQ-T2-05 | Close short | `:close` | `APPROVED`, `PARTIALLY_ISSUED` | reason | — |
| MRQ-T2-06 | Cancel | `:cancel` | nothing issued | reason | — |
| MRQ-T2-07 | Raise PR | `:handoff` | line short | trade on | — |
| MRQ-T2-09 | Top up | `:approve` (P8 `G8`) | `APPROVED`, `PARTIALLY_ISSUED` | a line short of its holds (`MRQ-T1-14`) | — |
| MRQ-T2-08 | Print | `wh_print_jobs:create` | any but `DRAFT` | `SYS-MATERIAL-REQUISITION` | FR-538 |

**Seeded bundles (P8-09 S4 F5, `V511408` §3):** ADMIN / ADMIN_GROUP hold every verb; AUDITOR `:view`, `:view:all`, `:view_all_departments`; the stores and department bundles **Warehouse Storekeeper**, **Warehouse Supervisor** and **Branch Admin** (`BRANCH_ADMIN`) raise — `:create`, `:edit`, `:submit` (with `:view` + `:view:branch`); the approver bundle **Warehouse Manager** holds `:approve`, `:close`, `:cancel` and `:handoff`; **Warehouse Supervisor** also holds `:handoff` (S4b). Stock Controller and Finance Controller keep `:view` + `:view:branch`. `MRQ-GRD-05` still narrows who may approve; a grant never widens it.

## 3. T3 — Time-driven rules

| ID | Rule | Trigger | Changes | Notified | Job | Once? |
|---|---|---|---|---|---|---|
| MRQ-T3-01 | Pending approval | `SUBMITTED` > `warehouse.approval.pending_alert_hours` | nothing | approvers — the eligible approvers under `MRQ-GRD-05` (`eligibleApproverIds`; once first-approved, less the first approver), through a `WhMaterialRequisitionPendingApprovalProvider` on the `WhbPendingApprovalSource` SPI, which names each document's recipients (`recipientsFor`) instead of every site `:approve` holder (P8-09 S4 F1) | `p2-23` alert | per episode (`alert_raised_at`; it never suppresses `-02` / `-03`) |
| MRQ-T3-02 | **Overdue to issue** | `APPROVED`/`PARTIALLY_ISSUED`, a line with open-to-issue > 0 and `required_by_date < today` (site TZ) (P8-09 S4 F13) | nothing — `overdueOnly` filter, WS-274 ageing | stores in-charge — the `:view` holders whose site **and** department scope include the requisition | daily job, site-local date | once per requisition (`overdue_alert_raised_at` latch) |
| MRQ-T3-03 | Stale approved | `APPROVED`/`PARTIALLY_ISSUED` with no issue for `warehouse.stores.requisition_stale_days` (default 30), on the site-local date. **Proxy until P8-10** records issues: measured from `approved_at` (P8-09 S4 F13) | nothing — tile; **never auto-closes** | requester + stores — the `:view` holders whose site and department scope include it | daily job, site-local date; no auto-close, no auto-PR. `-02` and `-03` run as **one job with two latches** (`WH_MATERIAL_REQUISITION_REMINDER`, P8 `G24` amended, S4 F17) | once (`stale_alert_raised_at` latch) |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in | Source |
|---|---|---|---|---|
| MRQ-T4-01 | approval (and `MRQ-T1-14` top-up) with `requisition_reservation = SOFT`/`HARD` | **reservations per grain** (R29 F4): a `whb_reservations` row needs a location and a status (`WhbReservationService.java:136-139`), so the approved quantity is reserved as one row per (location, lot, status `AVAILABLE`) picked FEFO for expiry-managed items, else FIFO by lot receipt date, until min(approved, available-to-reserve) is held — every row with holder `(WAREHOUSE, MATERIAL_REQUISITION, requisition id, line_no)`; the shortfall is a computed field. **`SOFT`** = `TYPE_SOFT` with `expires_at = soft_hold_until` (initially `approved_at + warehouse.stores.requisition_soft_hold_days`, default 7; every hold created inside the window, at approval or by a top-up, gets the same `expires_at`; the expiry job releases it, `WhbReservation.java:55`; P8 decision `G12`). Holds carry the default priority 100; a SOFT hold yields only to a strictly higher-priority allocation (WH-SC-189), reason `YIELDED`, shown on the line's reserved / short — no yield notification (a base-wide change in its own task if ever wanted; P8 decision `G11`); **`HARD`** = `TYPE_HARD`, ended only by consume, close, cancel or explicit release (`:58`) (R29 F32). *Amended for MFG MD-16, sharpened by R29 MFG-F12:* **no reservation whenever the line's resolver declares `ownsReservations() = true`** (MFG's `PRODUCTION_ORDER`) — decided by the cost-object **type**, never by whether `reservationsFor` happens to return rows, so an order released short, with a `NONE` policy or with an expired `SOFT` hold never gets requisition-owned holds; the line's `reserved` reads `reservationsFor(costObjectId, itemId)` | requisition service → reservation service, one transaction · `STO-D18` (R30 `CP-FR-014`) | STO-D18 |
| MRQ-T4-02 | store-issue post | **consume-and-split inside the issue transaction** (R29 F4): per issue line, the line's open holds at the issued grain are locked (`WhbReservationStore.lockForRelease`) and consumed up to the issued base quantity with `WhbReservationStore.consume(hold, movementLineId, …)` (`:232`, closes the whole hold); when a hold is larger than what was issued, a residual hold for the remainder is inserted at once (`WhbReservationStore.insert`, same holder quad, grain, type and expiry — the shape of `WhbPickReservationService.reattach` `:137`). Then holds of the line at other grains are trimmed (released and re-inserted smaller) until Σ open holds ≤ open-to-issue. The same call is also passed as `consumedReservationIds` so the writer's availability check does not count them (`WhbMovementPostCommand.java:23-25`). **Owner-held holds (MFG):** core consumes them in the same way, by the ids `reservationsFor` returns, and passes the consumed and residual ids to `onIssuePosted` — MFG never consumes them itself. Line `issued_quantity`, header ladder | issue service, same transaction | — |
| MRQ-T4-03 | close short / cancel | the line's own holds released (reason context `RESERVATION_RELEASE`, `releaseByHolder`); an owner-held reservation (`ownsReservations()`, MFG MD-16) is **not** released — the owner releases it | requisition service | — |
| MRQ-T4-04 | store-return post (`SIR-T1-07`) | line `returned_quantity` += ; status unchanged | return service | — |
| MRQ-T4-05 | hand-off | outbox `material_requisition.shortfall_handed_off`; the buying module's later receipt is issued against the same line | handoff port | FR-532 |

## 5. T5 — Screen contract

### 5.1 WS-268 Material Requisitions (reference: **Service Vehicle**)

| | |
|---|---|
| **Grid** | `wh_material_requisitions` · scope `WAREHOUSE_MATERIAL_REQUISITION` · sort `e.created_at DESC` |
| **Tiles** | `SUBMITTED` · `APPROVED` · `PARTIALLY_ISSUED` · *Overdue to issue* · `ISSUED` this month |
| **Columns** | `requisitionNumber`, `warehouseName`, `departmentName`, `costObjectType`, `costObjectRef`, `purpose`, `requestedByName` (user display helper), `requiredByDate` (`formatDateSync`), `priority`, `lineCount`, `requestedQuantity`, `approvedQuantity`, `issuedQuantity`, `status`, `approvedByName`, `approvedAt`, audit |
| **Requester picker** | `/requesters` lists every active user (the canonical user display), as every warehouse ledger user picker does (`WhbLedgerOptionsService.users`) — not narrowed by department or site (P8-09 S5) |
| **Filters** | `search` (requisition number, cost-object reference, source reference); `warehouseId`; `departmentId` (own departments unless `:view_all_departments`); `costObjectType` → `costObjectId` (cascade, resolver-backed dropdown — `GET /warehouse/stores/cost-objects` takes `type`, `search`, `limit` and an optional `warehouseId`, which picks the site's operator company and its work orders; P8-09 S4 recorded from the code); `purpose`; `status` (multi); `requestedById`; `requiredFrom/To` (date); `overdueOnly`; `itemId` |
| **Row actions** | View · Edit · Submit · Recall · Approve · Reject · Issue (→ WS-271 pre-filled) · Close short · Cancel · Print |
| **Detail WS-269** | header; lines (`item`, `requested`, `approved`, `issued`, `returned`, `closed`, `available`, `reserved`, `short`, `status`, hand-off refs); issues tab; returns tab; history |
| **Export** | grid + lines sheet + `createdByName`, `updatedByName` |
| **Line UoM picker** | `GET /warehouse/stores/requisitions/items/{itemId}/uoms` (`:view`) — the units convertible to the item's base unit; the line modal's UoM Select reads it (P8-09 S4 L2) |
| **Preferred-lot picker** | `GET /warehouse/stores/requisitions/lots` (`:view`; `search`, `itemId`, `includeId`, `limit`) — the item's lots a line may prefer (`MRQ-T1-26`); the line modal's lot `SearchableSelect` reads it (#570 S4, recorded from the code) |
| **R32 grid columns** | `operationRefs`, `jobCardRefs` — the distinct line operation / job-card refs of the requisition, aggregated per header (plural; the lines grid and WS-274 carry the per-line `operationRef` / `jobCardRef`); both exported (#570 S4, recorded from the code) |
| **Excess summary** | the header summary SQL counts `excess_pending` (lines with `excess_approval_status = PENDING`); it drives the detail response's `canDecideExcess` and the WS-269 *Decide excess* action (#570 S4, recorded from the code) |
| **Lines grid** | `wh_material_requisition_lines` (ledger-style, no audit columns): the WS-269 lines table and the extended lines export; its filters are the WS-268 set (P8-09 S4: recorded from the code) |

### 5.2 WS-274 Issue queue (reference: **Customer**)

Grid `wh_material_requisition_issue_queue` (one row per open line): `requisitionNumber`, `departmentName`, `itemCode`, `itemName`, `openToIssue`, `available`, `reserved`, `short`, `requiredByDate`, `ageDays`, `priority`; filters site, department, item, `shortOnly`, `overdueOnly`; actions **Issue selected** (one store issue for the selected lines of one requisition), **Raise PR**, **Close short**, **Top up** — each gated by the row's `can*` flag and reusing the WS-269 modals and API (P8-09 S4 F6). `available` and `short` follow `MRQ-GRD-10` (allocator candidate rule; the `NONE` shared pool). Backend-computed; no `.filter()` in the page. **R30 `CP-SC-006`:** scope `WAREHOUSE_REQUISITION_ISSUE_QUEUE`; `default_columns` = the columns above, `default_filters` = site, department, `shortOnly`, `overdueOnly` (`STO-D22`); export = the visible columns (a read-only queue — no audit columns on the grid, so none in the export).

## 6. Out of scope

Requisition of services; a multi-level approval matrix beyond `OD-29`'s optional second level; auto-PR; mobile.

## 7. Amendments

| Date | Change |
|---|---|
| 2026-10-22 | v0 derived |
| 2026-10-22 | Amended for MFG MD-16: owner-held reservations (`MRQ-T4-01`, `-03`); `WhMaterialRequisitionPort` named (`MRQ-OPEN-02`) |
| 2026-10-22 | R29 dispositions: site scope pair + `:view_all_departments`; mutually exclusive approvals, recall clears the first approval; per-grain reservations, SOFT/HARD, top-up, consume-and-split, core consumes owner-held holds; `ownsReservations()` by type; close-short header outcome; department company rule; hand-off status row; §8a port rows; self-approval code |
| 2026-10-23 | R31: the port caller also holds `wh_material_requisitions:view:all` (sibling service principal) or `:view:branch` (sibling bundles) — core checks site scope first (registry R.1, F-SR-004); the `warehouse:orders:port → wh_material_requisitions:{view,create,cancel,close}` dependency rows are seeded by `V511408` (F-SR-006); `MRQ-OPEN-01`/`-02` resolved (`R31-decisions`) |
| 2026-10-24 | P8 decision record `EV-1` (DECISIONS `D-19`): every outbox event code renamed to the dotted `whb_event_types` vocabulary of registry R.4 (PC-42) — e.g. `purchase_order.amended`, `demand_order.shipped`, `rma.matched`, `supplier_return.dispatched`; no behaviour change |
| 2026-10-24 | P8 decision record (DECISIONS `D-19`): `owner_id` (house owner) on the requisition and the port command (`G2`); department-axis verb seeded by the sibling (`G3`, §8a); `422 REQUISITION_NO_ELIGIBLE_APPROVER` (`G4`, `MRQ-T1-02`, `-GRD-05`); SOFT holds priority 100, strict yield, no notification (`G11`, `MRQ-T4-01`); `soft_hold_until` window and job/top-up rule (`G12`, `MRQ-T4-01`, `-T1-14`); `estimated_value` = last receipt-layer cost, NULL counts above the threshold (`G17`, `MRQ-GRD-11`); port `APPROVED` create adds `:approve` (`OD-1`, `MRQ-T1-20`). P8-09 S1: reject reason columns and seeds (`G14`); `MRQ-GRD-03` predicate on `is_stocked`, no item-site row (`G16`); short and live hand-off defined, lock and retry (`G20`, `MRQ-GRD-10`); T3 provider, jobs and latches (`G24`) |
| 2026-10-24 | P8-09 S4 (S3 review fix round): Recall under `:edit` for requester or creator (`-T1-04`, `-T2-02`); department tier on secondary surfaces (`-GRD-04`); `NONE` shared pool and allocator candidate rule (`-GRD-10`); `-GRD-12` one line per item; `-T2-09` Top up; seeded bundles; T3 recipients, predicates, `approved_at` proxy, one job two latches (`G24` amended); `-T1-20` skips `-GRD-11`; `-T1-24` widened; SOFT NULL window stamped on first top-up; §5.1 `search`, cost-objects `warehouseId`, lines grid; §5.2 actions |
| 2026-10-24 | P8-09 S4b: `-T1-14` actor aligned to `-T2-09` (`:approve`); top-up job walks LINES in need-date order (S4b R4); `-T1-09` close by `:close` holders only; Warehouse Manager `:cancel` / `:handoff`, Warehouse Supervisor `:handoff`; §5.1 line UoM endpoint; `ownedReservationKeys` fan-out noted |
| 2026-10-24 | P8-09 S5 (tester round): `-T1-02` Submit by requester or creator; `-GRD-09` message names Close short; `-GRD-11` zero estimate (0, below the threshold); `/requesters` lists all active users; the `can*` flags follow the caller (self-approval, requester/creator) and Top up only when a line is short of its holds |
| 2026-10-25 | **R32 (PRD 2026-10-24 §7.1 / §7.2, `D-20` #10).** `P8-09` reopened: SO sample via cost object `DEMAND_ORDER`, `REPLACEMENT` purpose, SO / job-card / operation refs `MRQ-T1-25`/`-GRD-22`; lot preference `MRQ-T1-26`/`-GRD-25`; over-standard higher approval `MRQ-T1-27`/`-GRD-23` (`C6`); post-facto requisition for an emergency issue `MRQ-T1-28`/`-29`/`-GRD-24` (`C2`). Production requisitions approved by the department head by default (`warehouse.stores.production_requisition_approver`, `C4`; FRD-MFG:165 amended). Contract stays v0 |
| 2026-10-25 | **R32-fix** (`R32-functional-review-core-quality.md`). Excess over standard approved on its own `MATERIAL_REQUISITION` request (condition `excess_over_standard`) tracked apart from issue progress, allowed from `APPROVED` / `PARTIALLY_ISSUED`, per-line `excess_approval_status`, withdrawn on close-short / cancel, header stays `PARTIALLY_ISSUED` while an excess waits (`MRQ-T1-08`, `-27`, `MRQ-GRD-23`; F-R32CQ-006); post-facto requisition ratifier checked before the emergency post, falling back to the site's stores approvers (`MRQ-T1-28`; F-031) |
| 2026-10-27 | **P8-09 #570 S4 (R33).** `MRQ-T1-27`: rule levels in the EXCESS phase demand `:approve_excess`, a zero-level rule never auto-decides the excess; a port create's source approver excluded; Close Line withdraws a line's only-pending excess; a replayed decision is `409 APPROVAL_STEP_NOT_PENDING`. `MRQ-T1-28`: P8-10 goes through `WhMaterialRequisitionPostFactoService` (MANDATORY). §5.1 adds the `/lots` picker, the `operationRefs` / `jobCardRefs` columns and the `excess_pending` summary (in code, not in contract) |
| 2026-10-27 | **P8-09 #570 S4c.** `MRQ-GRD-23` open-to-issue deducts the excess only while `PENDING` (as built); `MRQ-T1-29` actor is the `MRQ-T1-28` ratifier (head / deputy, else site `:approve` holders) and the refusal audience as built; `MRQ-T1-27` replay after the header ended is still `409 APPROVAL_STEP_NOT_PENDING`; policy-`NONE` short pool caps earlier `ONLY` lines at their lot's free stock (`MRQ-GRD-10`, `-25`) |
| 2026-10-27 | **P8-10 #571 S4.** `MRQ-T1-28` one line per item; `MRQ-T1-29` the outcome on the issue screens and export; a `DEPARTMENT` cost object resolves under the CALLING resource's department verb — requisition callers keep `wh_material_requisitions:view_all_departments` (`SIR-GRD-01`); WS-268 gains the **Issue** row action |

## 8. Invariants and scenarios

`FR-408`; `P0-09` reservation balance; scenarios `WH-SC-455`, `-458`…`-462`, `-466`, `-473`, `-474`.

## 8a. `WhMaterialRequisitionPort` — requisitions raised by a sibling (R29 F14, MFG-F4)

`ai.warehouse.port.stores.WhMaterialRequisitionPort`, a façade over `WhMaterialRequisitionService` (no
second write path). Used by `warehouse-manufacturing` for production-order requisitions. The sibling also seeds, for `wh_material_requisitions`, the department-axis verb `:view_all_departments` on its service principal (MFG `p10-01`); core never grants it through dependencies (P8 decision `G3`).

| ID | From | Event | To | Guard | Actor | Side effects | Reason? |
|---|---|---|---|---|---|---|---|
| MRQ-T1-20 | — | **`create(CreateRequisitionCommand)`** — site, department, cost object (type, id), purpose, required-by, lines; `sourceModule`, `sourceDocumentType/Id/Ref`, `idempotencyKey`, `actingUserId`, `initialStatus` (`DRAFT` / `APPROVED`), `approvedByUserId` | `DRAFT`, or `APPROVED` with `approved_quantity = requested_quantity` per line | `MRQ-GRD-01`…`-03`, `-20`, `-21`; `ownerId` optional (defaults when one eligible house owner exists, else `422 OWNER_REQUIRED · ownerId`, P8 `G2`); `APPROVED` needs `approvedByUserId` (`422 PORT_APPROVER_REQUIRED`) and skips `MRQ-GRD-05` — the maker ≠ checker check is the source's (its order release), recorded `approval_source = SOURCE_MODULE`; **`MRQ-GRD-11` is skipped** too (no second-approval threshold for a source-approved create, P8-09 S4) | acting user + `warehouse:orders:port` + `wh_material_requisitions:create` (with `initialStatus = APPROVED` additionally `:approve`, P8 `OD-1`) + the site scope verb (`:view:all` service principal / `:view:branch` bundle, registry R.1, R31 F-SR-004) | `source_*` recorded; gapless `MRQ` number; `MRQ-T4-01` (no reservation for an `ownsReservations()` type) | no |
| MRQ-T1-21 | `DRAFT` · `SUBMITTED` · `APPROVED` with Σ issued = 0 | **`cancel(requisitionId, reason, sourceModule, idempotencyKey)`** | `CANCELLED` | Σ issued = 0 else `409 REQUISITION_TRANSITION_INVALID`. On an already terminal requisition with nothing issued (`REJECTED`, `CLOSED`, `CANCELLED`) the call **succeeds as a no-op** and returns the current status — so a sibling's order cancel/unrelease is never blocked by a rejected or short-closed requisition (MFG-F4: the sibling blocks only on Σ issued > 0, read from `-23`) | acting user + port authority + `wh_material_requisitions:cancel` | `MRQ-T4-03` | **yes** |
| MRQ-T1-22 | `APPROVED` · `PARTIALLY_ISSUED` | **`close(requisitionId, reason, sourceModule, idempotencyKey)`** — close short every open line | `CLOSED` (`MRQ-T1-09`) | — ; a replay on `CLOSED` returns it | acting user + port authority + `wh_material_requisitions:close` | `MRQ-T4-03` | **yes** |
| MRQ-T1-23 | any | **`getRequisitionPosition(requisitionId)`** | — | — | port + `:view` | status and per line requested, approved, issued, returned, closed, cancelled, reserved, open-to-issue | — |
| MRQ-T1-24 | port-owned requisition | **Manual** edit / submit / **recall** / approve / reject / cancel / close / **top up** / **raise PR** on WS-268/269/274 (`RequisitionChange` `RECALL`, `TOP_UP`, `HANDOFF` added, P8-09 S4 F11) | refused or allowed | every `MaterialRequisitionChangeGuard` bean is asked first, after the row lock; none registered → allowed; the `can*` flags ask the same guards; the daily top-up job skips a guarded line | `:edit` etc. | WS-269 shows *Managed by <module>* | — |

| ID | Predicate | Refusal |
|---|---|---|
| MRQ-GRD-20 | idempotency per `POS-GRD-07` (operation registry; the create's key also on the header, partial uk `(source_module, idempotency_key)`) | `409 PORT_IDEMPOTENCY_CONFLICT` |
| MRQ-GRD-21 | manual change on a port-owned requisition allowed only if every `MaterialRequisitionChangeGuard` allows | `409 REQUISITION_OWNED_BY_SOURCE_MODULE` (raised by the guard) |

### Contract quality (P8-09 S4b)

- The issue-queue `reserved` figure for a reservation-owning cost object binds every hold id its resolver's `reservationsFor` returned, one `costObjectId:reservationId` key per hold (`ownedReservationKeys`), as one `IN` list. It has no upper bound: a resolver naming thousands of holds produces an equally long bind list. Nothing changes now; a bound, or a resolver read that sums the figures itself, is for P10 when MFG registers.

## 9. Open rows

| ID | Question | Default |
|---|---|---|
| MRQ-OPEN-01 | OD-29 | single level + optional value threshold **RESOLVED (DEFAULT), 2026-10-23** (`R31-decisions`). One level, plus a second level above `warehouse.stores.requisition_second_approval_value` (null = off). |
| MRQ-OPEN-02 | Should a requisition for `PRODUCTION_ORDER` be created by MFG through a port rather than the screen? | yes — §8a (`WhMaterialRequisitionPort`); the screen also allows it when the resolver is present, and the requisition is then not port-owned **RESOLVED (DEFAULT), 2026-10-23** (`R31-decisions`). |
