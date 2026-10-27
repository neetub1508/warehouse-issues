# Functional Contract — Non-conformance (NCR), CAPA, defect codes, quality deviation (concession), and the quality registers

> **What this is.** The functional truth for what happens **after** an inspection finds a defect, on one
> engine for every inspection stage (IQC, PQC, PDI, store return, stock): the non-conformance report raised
> for every reject, its containment, root cause and CAPA actions, the defect-code master that classifies it,
> the bounded and expiring **deviation** that lets non-conforming material be used with a second (and third)
> person's approval, and the five quality registers the plant reads. It **extends** the inspection
> workflow of [`incoming-inspection-sampling.contract.md`](incoming-inspection-sampling.contract.md) and
> [`receipt-qc-putaway.contract.md`](receipt-qc-putaway.contract.md); approval itself is the one engine of
> [`document-approval.contract.md`](document-approval.contract.md).
>
> **Status.** Derived 2026-10-25 (v0) from [`frd/FRD-STORES.md`](../frd/FRD-STORES.md) §6.9 (`FR-690`…`FR-696`,
> `FR-702`), `DECISIONS.md` `D-20` item 3, PRD 2026-10-24 §6 / §10 / §13.1. Amended 2026-10-27 (v1) from the
> `P8-17` S3 functional review (`#636`): the NCR / CAPA / defect-code part is **implemented** (classic `V511500`,
> `V511550`, `V511612`) and reviewed; the deviation (`P8-18`) and register (`P8-21`) parts are not yet built.

---

## 0. Identity

| | |
|---|---|
| **Workflow** | Inspection reject → NCR raised (auto or manual) → investigation (containment, root cause) → CAPA actions (complete → verify) → closure approval · Deviation request → level approvals → active → consumed / expired / revoked · Registers read both |
| **Module** | `warehouse`; code lists and document types in `warehouse-base` (`V500500`, `V500501`) |
| **Domain baseline** | ISO 9001:2015 §8.7 (control of nonconforming outputs), §10.2 (nonconformity and corrective action); IATF 16949 §8.7.1.1 (customer authorisation for concession), §10.2.3 (problem solving); `FR-383` (no JSONB); `FR-408` (maker ≠ checker); `D-16` item 5 (no upward FK); `RN-054` (no accounting document) |
| **Owning tasks** | `issues/p8-17.md` (NCR, CAPA, defect codes) · `issues/p8-18.md` (deviation) · `issues/p8-21.md` (registers) |
| **Primary tables** | `wh_nonconformances`, `wh_capa_actions`, `wh_defect_codes` (`V511500`); `wh_quality_deviations`, `wh_quality_deviation_usages` (`V511501`); ALTER `wh_quality_inspection_lines` + `defect_code_id` (`V511500`), + `deviation_id` (`V511501`); evidence in `wh_document_attachments` (`V511505`, `P8-06`) |
| **Permission resources** | `wh_nonconformances:{view,view:all,view:branch,create,edit,investigate,submit_closure,approve_closure,cancel,export}` · `wh_capa_actions:{view,create,edit,complete,verify,cancel,export}` · `wh_defect_codes:{view,create,edit,export}` · `wh_quality_deviations:{view,view:all,view:branch,create,edit,submit,approve,approve_final,revoke,consume,export}` (`:consume` — the mutating verb of the port's consume / reverse, R32-fix F-R32CQ-007) · `wh_rpt_quality_registers:{view,view:all,view:branch,export}` |
| **Routes** | WS-690 `/warehouse/quality/nonconformances` · WS-691 `/warehouse/quality/nonconformances/[id]` · WS-692 `/warehouse/quality/defect-codes` · WS-693 `/warehouse/quality/deviations` · WS-696 `/warehouse/quality/registers` · **mobile: none** (`D-20` item 5) |
| **Contract version** | `v1 — 2026-10-27` (`P8-17` S4 amendments, §7) |

### Acceptance checks

| # | Expects | Delivered by |
|---|---|---|
| A1 | Every reject raises exactly one NCR, attributed to the supplier when the material came from one (`WH-SC-720`) | `NCR-T1-01`, `NCR-GRD-01`, `NCR-T4-01` |
| A2 | An NCR cannot close with an unverified CAPA action; the completer cannot verify (`WH-SC-721`) | `NCR-GRD-02`, `NCR-GRD-04` |
| A3 | A deviation is always bounded, approved in levels by different people, and consumed under a lock (`WH-SC-723`, `-725`) | `DEV-GRD-01`…`-04` |
| A4 | An expired deviation is never applied (`WH-SC-724`) | `DEV-T3-01`, `DEV-GRD-05` |
| A5 | The registers compute rejection % on inspected and ppm on received (`WH-SC-731`) | `QRG-T5-01`, `-02` |

---

## 1. T1 — State machine

### 1.1 Status inventory

| Entity | Status | Represented by | Kind |
|---|---|---|---|
| NCR | `OPEN` · `UNDER_INVESTIGATION` · `ACTION_PENDING` · `PENDING_CLOSURE` · `CLOSED` · `CANCELLED` | `wh_nonconformances.status` (no CHECK, service-whitelisted) | document ladder |
| CAPA action | `OPEN` · `IN_PROGRESS` · `COMPLETED` · `VERIFIED` · `CANCELLED` | `wh_capa_actions.status` | task ladder |
| Deviation | `DRAFT` · `SUBMITTED` · `LEVEL1_APPROVED` · `APPROVED` · `REJECTED` · `EXHAUSTED` · `EXPIRED` · `REVOKED` · `CANCELLED` | `wh_quality_deviations.status` | document ladder |
| Defect code | active / inactive | `is_active` | registry |

### 1.2 Transitions

| ID | From | Event | To | Guard | Actor | Side effects | Source |
|---|---|---|---|---|---|---|---|
| NCR-T1-01 | — | Disposition `REJECT`/`RTV`/`SCRAP` (stock-bearing) or outcome `REJECT` (non-stock-bearing) with `warehouse.quality.ncr_auto_raise = ON_REJECT` | `OPEN` | `NCR-GRD-01` | system, inside the disposition transaction | NCR numbered `NCR`, quantity = rejected, defect = line's code, owner = disposing user, `raised_automatically = true`; outbox `nonconformance.raised` | FR-690 |
| NCR-T1-02 | — | **Raise NCR** manually (any `NCR_SOURCE_TYPE`; from WS-690 or a rejected WS-080 line under `MANUAL`) | `OPEN` | `NCR-GRD-01`, `NCR-GRD-05` | `wh_nonconformances:create` | as T1-01, `raised_automatically = false` | FR-690 |
| NCR-T1-03 | `OPEN` | **Start investigation** (containment action, root cause category / text, 5-why) | `UNDER_INVESTIGATION` | — | `:investigate` | `investigation_started_at` | FR-691 |
| NCR-T1-04 | `UNDER_INVESTIGATION` | first CAPA action added | `ACTION_PENDING` | — | `wh_capa_actions:create` | — | FR-692 |
| NCR-T1-05 | `ACTION_PENDING`; or `UNDER_INVESTIGATION` when the severity is not in `ncr_capa_required_severities` (R32-fix F-R32CQ-020) | **Submit for closure** | `PENDING_CLOSURE` | `NCR-GRD-02` | `:submit_closure` | opens an `NCR_CLOSURE` approval request (`DAP` §0.1, `D-21` item 6) with `excludedActorIds` = owner, submitter, `raised_by` | FR-691 |
| NCR-T1-06 | `PENDING_CLOSURE` | request approved | `CLOSED` | `NCR-GRD-03` | the engine (`:approve_closure`) | `closed_by/at`; outbox `nonconformance.closed` | FR-691 |
| NCR-T1-07 | `PENDING_CLOSURE` | request rejected / returned | `ACTION_PENDING` (or `UNDER_INVESTIGATION` with no action) | — | the engine | reason recorded | FR-691 |
| NCR-T1-08 | `OPEN` / `UNDER_INVESTIGATION` / `ACTION_PENDING` (R32-fix F-R32CQ-039) | **Cancel** | `CANCELLED` | reason in `NCR_CANCEL` | `:cancel` | the partial uk frees the inspection line; from `ACTION_PENDING` every `OPEN` / `IN_PROGRESS` / `COMPLETED` CAPA action → `CANCELLED` with the note *NCR cancelled* | FR-690 |
| NCR-T1-09 | `OPEN` → `IN_PROGRESS` → `COMPLETED` | CAPA **Start** / **Complete** (completion note) | as named | owner or `:complete` | `wh_capa_actions:edit` / `:complete` | `completed_by/at` | FR-692 |
| NCR-T1-10 | `COMPLETED` | CAPA **Verify** `EFFECTIVE` | `VERIFIED` | `NCR-GRD-04` | `:verify` | `verified_by/at`, `effectiveness_result` | FR-692 |
| NCR-T1-11 | `COMPLETED` | CAPA **Verify** `NOT_EFFECTIVE` | `OPEN` | new `due_date` required (`422 CAPA_DUE_DATE_REQUIRED`) | `:verify` | note kept | FR-692 |
| NCR-T1-12 | `OPEN` / `IN_PROGRESS` | CAPA **Cancel** | `CANCELLED` | note mandatory | `:cancel` | — | FR-692 |
| NCR-T1-13 | — / active | Create / edit / deactivate a defect code | active / inactive | `NCR-GRD-06` | `wh_defect_codes:create/edit` | — | FR-693 |
| NCR-T1-14 | `PENDING_CLOSURE` | **Withdraw closure** (`PATCH /{id}/withdraw-closure`, the submitter's own request) | `ACTION_PENDING` (or `UNDER_INVESTIGATION` with no live action) | open `NCR_CLOSURE` request; the caller is the request's **maker or submitter** and no level has approved it (the engine's withdraw rule; WS-691 offers it per caller, `canWithdrawClosure`) | `:submit_closure` | the request is `WITHDRAWN` (S2 decision) | FR-691 |
| NCR-T1-15 | `PENDING_CLOSURE` | WS-691 **Approve / Return / Reject closure** (`PATCH /{id}/approve-closure`, `/return-closure`, `/reject-closure`) — the engine's decision taken from the document screen, offered only while the caller can act on the step (`canActOnClosure`) | as `NCR-T1-06` / `-07` | `NCR-GRD-03`; Return / Reject need a reason from the type's `APPROVAL_RETURN` / `APPROVAL_REJECT` codes, read under `wh_approval_requests:view` — which every approve verb now requires (`V511612`, R33 decision) | `:approve_closure` | as `NCR-T1-06` / `-07` | FR-691 |
| DEV-T1-01 | — | Create | `DRAFT` | `DEV-GRD-01`, `-02` | `wh_quality_deviations:create` | numbered `DEV` at submit | FR-694 |
| DEV-T1-02 | `DRAFT` | **Submit** | `SUBMITTED` | `DEV-GRD-01`, `-02` | `:submit` | opens a `QUALITY_DEVIATION` approval request (`DAP` §0.1) | FR-694 |
| DEV-T1-03 | `SUBMITTED` | level 1 approved, two levels configured | `LEVEL1_APPROVED` | `DEV-GRD-03`, `-07` | `:approve` | `level1_approved_by/at` | FR-694 |
| DEV-T1-04 | `SUBMITTED` (one level) / `LEVEL1_APPROVED` | final approval | `APPROVED` | `DEV-GRD-03`, `-07` | `:approve` (one level) / `:approve_final` | event `quality_deviation.approved` | FR-694 |
| DEV-T1-05 | `SUBMITTED` / `LEVEL1_APPROVED` | **Reject** (reason) | `REJECTED` | — | the level's verb | — | FR-694 |
| DEV-T1-06 | `APPROVED` | **Consume** (IQC `ACCEPT_UNDER_DEVIATION`, or `WhQualityDeviationPort.consume`) | `APPROVED` / `EXHAUSTED` at the limit | `DEV-GRD-04`, `-05` | inspector with `wh_quality_inspections:disposition` / port: `warehouse:orders:port` **and** `wh_quality_deviations:consume` on `actingUserId`, re-checked on a replay (R32-fix F-R32CQ-007) | usage row in base UoM (entered quantity, UoM and factor frozen, `DEV-GRD-04`); `consumed_quantity` += base qty | FR-695 FR-696 |
| DEV-T1-07 | `APPROVED` / `EXHAUSTED` / `EXPIRED` / `REVOKED` | **Reverse a usage** (disposition reversed; port `reverse`) | `EXHAUSTED` → `APPROVED` while site-local today ≤ `valid_to` (else `EXPIRED`); `APPROVED`, `EXPIRED`, `REVOKED` unchanged (R32-fix F-R32CQ-036) | — | system / port (as `DEV-T1-06`, `:consume`) | `REVERSAL` usage; `consumed_quantity` −= qty | FR-695 |
| DEV-T1-08 | `APPROVED` | **Revoke** (reason) | `REVOKED` | — | `:revoke` | future consumption refused | FR-695 |
| DEV-T1-09 | `DRAFT` | **Cancel** | `CANCELLED` | — | maker | — | FR-694 |

### 1.3 Guards

| ID | Predicate | Refusal | Backstop | Source |
|---|---|---|---|---|
| NCR-GRD-01 | one live (not `CANCELLED` / `CLOSED`) NCR per rejected inspection line — a further reject of the line adds to it (`NCR-T4-04`); a reject carries an active defect code applicable to the stage when `defect_code_required` (with the setting off the NCR is raised with a null code, R32-fix F-R32CQ-018) | `409 NCR_ALREADY_RAISED` (manual raise only) · `422 DEFECT_CODE_REQUIRED` · `422 DEFECT_CODE_NOT_APPLICABLE` | partial uk `(inspection_line_id) WHERE status NOT IN ('CANCELLED','CLOSED')` | FR-690 FR-693 |
| NCR-GRD-02 | closure needs every CAPA action `VERIFIED`/`CANCELLED`; ≥ 1 `VERIFIED` action when the severity is in `ncr_capa_required_severities` (default `CRITICAL,MAJOR`, R32-fix F-R32CQ-020); containment recorded; root cause for a severity in `ncr_root_cause_required_severities`; a defect code set | `409 NCR_CLOSURE_BLOCKED` listing each blocker | — | FR-691 FR-692 |
| NCR-GRD-03 | the closure approver is not the NCR owner, the submitter, nor the immutable `raised_by` (R32-fix F-R32CQ-005) | `403 NCR_SELF_CLOSURE` | `DAP-GRD-03` over the request's frozen `excludedActorIds` | FR-691 FR-692 |
| NCR-GRD-04 | the CAPA verifier is not the completer | `403 CAPA_SELF_VERIFICATION` | — | FR-692 |
| NCR-GRD-05 | manual raise names an item, a quantity > 0 and a source document or a free description for `CUSTOMER_COMPLAINT` / `AUDIT` / `OTHER` | `422 NCR_SUBJECT_REQUIRED` | CHECK `nonconforming_quantity > 0` | FR-690 |
| NCR-GRD-06 | defect code unique per company; a code used by an NCR or inspection line is deactivated, never deleted | `409 DEFECT_CODE_DUPLICATE` · `409 DEFECT_CODE_IN_USE` | uk `(company_id, code)` | FR-693 |
| NCR-GRD-07 | a manual **Raise NCR** from WS-080 only while `ncr_auto_raise = MANUAL` (S2 decision) | `409 NCR_MANUAL_RAISE_OFF` | — | FR-690 |
| NCR-GRD-08 | a raise or accumulation carries a quantity > 0: the rejected quantity of a disposition, the failed quantity of a non-stock `REJECT` outcome (D4) (S2 decision) | `422 NCR_QUANTITY_INVALID` (on `lines[i].outcomeCode` for an outcome) | CHECK `nonconforming_quantity > 0` | FR-690 |
| NCR-GRD-09 | a write carries the `version` the screen read (S2 decision) | `409 NCR_VERSION_CONFLICT` · `409 CAPA_VERSION_CONFLICT` | `version` column | FR-691 FR-692 |
| NCR-GRD-10 | an owner is an active user holding the verb in the record's site: NCR owner `wh_nonconformances:investigate` in the `wh_nonconformances` site scope, CAPA owner `wh_capa_actions:complete` in the `wh_capa_actions` site scope (D17; scope per resource, S4 F4) | `422 NCR_OWNER_NOT_ELIGIBLE` · `422 CAPA_OWNER_NOT_ELIGIBLE` | — | FR-691 FR-692 |
| NCR-GRD-11 | a CAPA action has a description, a due date **on or after the site-local today** at create, on an edit that changes it, and at `NOT_EFFECTIVE` (an unchanged past due date is kept on edit; S4 F10), a note on Complete and Cancel, an effectiveness result on Verify, and is moved only from the status its verb names (S2 decision) | `422 CAPA_DESCRIPTION_REQUIRED` · `422 CAPA_DUE_DATE_REQUIRED` · `422 CAPA_NOTE_REQUIRED` · `422 CAPA_EFFECTIVENESS_REQUIRED` · `409 CAPA_STATUS_INVALID` | — | FR-692 |
| DEV-GRD-01 | bounded: at least one of `quantity_limit`, `valid_to`; `valid_to ≥ valid_from`; validity ≤ `deviation_max_validity_days` | `422 DEVIATION_BOUND_REQUIRED` · `422 DEVIATION_VALIDITY_TOO_LONG` | CHECK `num_nonnulls(quantity_limit, valid_to) >= 1` | FR-694 |
| DEV-GRD-02 | specification, deviation, reason and risk texts present; item active; after `SUBMITTED` only notes change | `422` field errors · `409 DEVIATION_NOT_EDITABLE` | NOT NULL columns | FR-694 |
| DEV-GRD-03 | each approver ≠ requester and ≠ the other level's approver | `403 DEVIATION_SELF_APPROVAL` | `DAP-GRD-03` | FR-694 |
| DEV-GRD-04 | consumption under a row lock: consumed + qty ≤ limit, **both in the item's base UoM** — `quantity_limit`, `consumed_quantity` and every usage are base-UoM; a usage freezes the entered quantity, UoM and `conversion_factor_used` (an IQC quantity in receipt-line units, a port quantity with its `uomCode`), a UoM with no conversion to base is refused (R32-fix F-R32CQ-017) | `409 DEVIATION_QUANTITY_EXCEEDED` naming the remainder · `422 UOM_CONVERSION_MISSING` | CHECK `consumed_quantity <= quantity_limit` | FR-695 |
| DEV-GRD-05 | applicable: `APPROVED`, site-local today in `[valid_from, valid_to]`, **same company as the consuming document and `warehouse_id` null or = the consuming site** (R32-fix F-R32CQ-012), same item, supplier / lot / stage / source document when set — re-checked under the row lock at consume | `409 DEVIATION_NOT_APPLICABLE` naming the failing condition (incl. `SITE`, `COMPANY`) | — | FR-695 FR-696 |
| DEV-GRD-06 | usages are append-only | — | trigger refuses `UPDATE` / `DELETE` on `wh_quality_deviation_usages` | FR-695 |
| DEV-GRD-07 | an approval level is acted only while site-local today ≤ `valid_to` (when set) (R32-fix F-R32CQ-036) | `409 DEVIATION_VALIDITY_ENDED` | `DEV-T3-01` expires the pending request | FR-694 FR-695 |

### 1.4 Unreachable

| ID | Must never happen | Source |
|---|---|---|
| NCR-UNR-01 | an NCR creating a supplier claim, supplier return, debit note or any movement (`RN-054`, `IIS-UNR-01`) | FR-690 |
| NCR-UNR-02 | a CLOSED NCR edited or reopened in place (a recurrence is a new NCR citing the old) | FR-691 |
| DEV-UNR-01 | an unbounded or self-approved deviation reaching `APPROVED` | FR-694 |
| DEV-UNR-02 | a usage written against a deviation that was not applicable at that instant | FR-695 |
| DEV-UNR-03 | a lot whose verdict is `REJECT_LOT` released to an allocatable status (or `MRN_PENDING`) by any disposition other than `ACCEPT_UNDER_DEVIATION` (R32-fix F-R32CQ-002; `IIS-T1-09` amended) | FR-696 |

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from | Extra | Source |
|---|---|---|---|---|---|
| NCR-T2-01 | Raise / edit / investigate | `wh_nonconformances:create` / `:edit` / `:investigate` | `OPEN`, `UNDER_INVESTIGATION`, `ACTION_PENDING` (D13; never `PENDING_CLOSURE` — withdraw or have it returned first) | record scope by site (`P1-18`) | FR-690 FR-691 |
| NCR-T2-02 | Submit / approve closure | `:submit_closure` / `:approve_closure` | `ACTION_PENDING` (or `UNDER_INVESTIGATION` per `NCR-T1-05`) / `PENDING_CLOSURE` | QA manager | FR-691 |
| NCR-T2-03 | CAPA complete / verify | `wh_capa_actions:complete` / `:verify` | `IN_PROGRESS` / `COMPLETED` | verifier ≠ completer | FR-692 |
| NCR-T2-04 | Print NCR | `wh_nonconformances:view` | any but `CANCELLED` | `SYS-NCR`; reprint duplicate | FR-691 |
| DEV-T2-01 | Request / submit | `wh_quality_deviations:create` / `:submit` | `DRAFT` | QC engineer, production, purchase | FR-694 |
| DEV-T2-02 | Approve level 1 / final | `:approve` / `:approve_final` | `SUBMITTED` / `LEVEL1_APPROVED` | QC Manager / Plant Head bundles | FR-694 |
| DEV-T2-03 | Accept under deviation | `wh_quality_inspections:disposition` | inspection *completed* | applicable deviation only | FR-696 |

## 3. T3 — Time-driven rules

| ID | Rule | Trigger | Changes | Notified | Job | Once? | Source |
|---|---|---|---|---|---|---|---|
| NCR-T3-01 | CAPA overdue | action `OPEN`/`IN_PROGRESS`, `due_date` < site-local today | nothing; outbox `capa_action.overdue` | action owner, NCR owner | daily alert job (`p2-23` family) | once per `capa_overdue_reminder_days` per action | FR-692 |
| DEV-T3-01 | Deviation expiry | `APPROVED`, `SUBMITTED` or `LEVEL1_APPROVED` with `valid_to` < site-local today (R32-fix F-R32CQ-036) | → `EXPIRED`, event `quality_deviation.expired`; a pending `QUALITY_DEVIATION` request is withdrawn by the system (`WITHDRAWN`, reason *validity ended*) | requester, approvers | daily per site | once | FR-695 |
| DEV-T3-02 | Expiry warning | `valid_to` − today = `deviation_expiry_alert_days` | nothing | requester | same job | once (`expiry_alerted_on`) | FR-695 |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in | Source |
|---|---|---|---|---|
| NCR-T4-01 | NCR raised from a `GOODS_RECEIPT` source | `supplier_counterparty_id`, `origin_grn_*`, `origin_mrn_id`, `origin_po_ref` copied from the GRN / MRN; responsibility defaults `SUPPLIER` | NCR service | FR-690 |
| NCR-T4-02 | NCR raised from a `STORE_RETURN` source | the `P8-07` supplier-origin trace fills the same columns when the lot has a supplier receipt (`IIS-T4-06`): one candidate → used; several → the GRN line the user picked **at disposition** (`origin_grn_line_id` on the inspection line, `IIS-GRD-16`, R32-fix F-R32CQ-019); none → supplier columns null, responsibility `UNDETERMINED` (D8, adopted; every non-GRN source) | NCR service | FR-690 |
| NCR-T4-03 | NCR raised from MFG `IN_PROCESS` / `PRODUCTION_RECEIPT` | source columns name the MFG document by bare id + frozen ref; no FK (`D-16` item 5) | NCR service via resolver | FR-690 |
| NCR-T4-04 | a further rejecting disposition / outcome on a line that already has an NCR (R32-fix F-R32CQ-011) | live NCR: `nonconforming_quantity +=` the rejected quantity, `disposition_count +=`, history row naming the disposition movement — in the disposition transaction, so exactly once; `PENDING_CLOSURE`: when the reject adds quantity (after the D6 give-back credit) the closure request is `SYSTEM_RETURNED` (*quantity changed*) and the NCR returns to `ACTION_PENDING` (or `UNDER_INVESTIGATION` with no action) — a reject the credit absorbs whole adds nothing and leaves the request pending (S4 F11); `CLOSED`: a new `OPEN` NCR with `recurrence_of_ncr_id` (`NCR-UNR-02`); `CANCELLED`: a new NCR as `NCR-T1-01`. A reversed disposition never lowers the quantity | NCR service | FR-690 |
| DEV-T4-01 | `ACCEPT_UNDER_DEVIATION` disposition | posts exactly as `RESTOCK_SELLABLE` (incl. `MRA-T4-01` `MRN_PENDING` routing); line `deviation_id` set; usage row | inspection service, same transaction | FR-696 |
| DEV-T4-02 | deviation reaches its limit | `EXHAUSTED`, event `quality_deviation.exhausted` | deviation service, same transaction | FR-695 |

## 5. T5 — Screen contract

| ID | Screen | Contract | Source |
|---|---|---|---|
| NCR-T5-01 | WS-690 Non-conformances (reference **Service Vehicle**) | grid `wh_nonconformances` · scope `WAREHOUSE_NCR` · sort `e.raised_at DESC`; columns `ncrNumber`, `raisedAt` (timestamp, `formatDateWithTimezoneSync`), `sourceType`, `sourceDocumentRef`, `itemCode`, `itemName`, `lotCode`, `supplierName`, `defectCode`, `severity`, `nonconformingQuantity`, `ownerName` (platform user-display helper), `targetCloseDate` (`formatDateSync`), `openCapaCount`, `status`, `createdByName`, `updatedByName`; filters `warehouseId`, `status`, `sourceType`, `severity`, `defectCodeId`, `supplierCounterpartyId`, `itemId`, `ownerUserId`, `overdueOnly`, `raisedFrom` / `raisedTo` (two linked BaseFilter `date` fields, each a `DatePicker`); the search box also matches a scanned lot or serial — a serial through the NCR's own serial or the inspection line's serial results (S4 F8); tiles Open · Under investigation · Action pending · Overdue CAPA · Closed this month; export ⊇ grid columns | FR-690 FR-691 |
| NCR-T5-02 | WS-691 NCR detail | tabs *Details*, *Investigation*, *CAPA* (inline grid of `wh_capa_actions` with a read-only **View** — the action and its evidence, on every row whatever the NCR's state — and Start / Complete / Verify / Cancel; the tab is shown only with `wh_capa_actions:view`), *Attachments*, *History*, *Approval History* — Department-weight tabs, no vertical scroll, the open tab in `?tab=`; each verb offered on its permission AND the server's flag — Submit for closure per `NCR-T1-05` (`canSubmitClosure`), Withdraw per caller (maker or submitter, `NCR-T1-14`), approve / return / reject per caller (`canActOnClosure`), CAPA Verify never to the completer (`NCR-GRD-04`); refusals in the modal (`AlertBox`) | FR-691 FR-692 |
| NCR-T5-03 | WS-692 Defect Codes (reference **Department**) | grid `wh_defect_codes` · scope `WAREHOUSE_DEFECT_CODE` · sort `e.code ASC`; columns `code`, `name`, `defectCategory`, `inspectionStage`, `usedCount`, `isActive`, audit; filters `search`, `defectCategory`, `inspectionStage`, `isActive` | FR-693 |
| DEV-T5-01 | WS-693 Quality Deviations (reference **Service Vehicle**) | grid `wh_quality_deviations` · scope `WAREHOUSE_DEVIATION` · sort `e.valid_from DESC`; columns `deviationNumber`, `deviationType`, `itemCode`, `itemName`, `supplierName`, `lotCode`, `inspectionStage`, `quantityLimit`, `consumedQuantity`, `remainingQuantity`, `validFrom`, `validTo` (`formatDateSync`), `status`, `requestedByName`, audit; filters `warehouseId`, `status`, `deviationType`, `itemId`, `supplierCounterpartyId`, `activeOn` (`DatePicker`); tiles Pending approval · Active · Expiring · Exhausted · Expired; detail tabs *Details*, *Usage*, *Approvals*, *Attachments* | FR-694 FR-695 |
| DEV-T5-02 | WS-080 disposition modal | `ACCEPT_UNDER_DEVIATION` with a picker of applicable deviations (server-listed, remaining quantity shown) | FR-696 |
| QRG-T5-01 | WS-696 *Vendor rejection* tab (reference **Customer**) | grid `wh_rpt_vendor_rejection`; per supplier × item × month: received, inspected, accepted, accepted under deviation, rejected, IQC rejection % (÷ inspected), line-rejected, line-rejection ppm (÷ received × 10⁶); filters `warehouseId`, `supplierCounterpartyId`, `itemCategoryId` → `itemId`, `dateFrom`/`dateTo` (GRN posting date, named on screen); drill to WS-080 / WS-690 | FR-702 |
| QRG-T5-02 | WS-696 *Defect Pareto* tab | grid `wh_rpt_defect_pareto`; per defect code: NCR count, Σ quantity, share %, cumulative %, *vital few* flag up to `pareto_cutoff_percent`; bar + cumulative line chart; filters stage, source type, supplier, item category, date range | FR-702 |
| QRG-T5-03 | WS-696 *Open NCR / CAPA* tab | grid `wh_rpt_open_ncr_capa`; NCRs not closed / cancelled with site-local age bucket (0–7, 8–30, 31–60, > 60), owner, severity, open and overdue CAPA counts; overdue actions with days overdue | FR-702 |
| QRG-T5-04 | WS-696 *Deviations* tab | grid `wh_rpt_deviations`; every deviation with limit, consumed, remaining, validity, status; tiles Active · Expiring · Exhausted · Expired | FR-702 |
| QRG-T5-05 | WS-696 *Pass rate by stage* tab | grid `wh_rpt_inspection_pass_rate`; per stage (the `INSPECTION_STAGE` code list — `INCOMING`, `FIRST_ARTICLE`, `IN_PROCESS`, `FINAL`, `RETURN`, `PERIODIC`; no `STOCK` stage, `STOCK` is a source type, R32-fix F-R32CQ-033) × item × month: completed inspections, accepted first time (no `REWORK`, no re-inspection of the source line), first-pass % — core inspections only (MFG operation yield stays `P10-13`) | FR-702 |

## 6. Out of scope

The 8D report format and customer-complaint handling beyond raising an NCR; SPC charts (FRD-STORES §12 row 4); automatic supplier return, claim or debit note from an NCR (`RN-054`); mobile (`D-20` item 5).

## 7. Amendments

| Date | Change |
|---|---|
| 2026-10-25 | v0 derived (R32, `D-20` item 3): NCR / CAPA / defect codes (`P8-17`), deviation (`P8-18`), quality registers (`P8-21`); approvals on the one engine (`P8-30`, `DAP` §0.1 types `NONCONFORMANCE`, `QUALITY_DEVIATION`) |
| 2026-10-25 | **R32-fix** (`R32-functional-review-core-quality.md`, `D-21` items 6, 8). Engine type renamed `NCR_CLOSURE` with frozen `excludedActorIds` = owner, submitter, `raised_by` (`NCR-T1-05`, `NCR-GRD-03`; F-R32CQ-005); NCR quantity accumulates per further reject, recurrence NCR after `CLOSED`, partial uk excludes `CLOSED` (`NCR-T4-04`, `NCR-GRD-01`; F-011); defect code nullable on the NCR, required at closure (F-018); `ncr_capa_required_severities` and Submit-from reconciled (`NCR-T1-05`, `NCR-T2-02`, `NCR-GRD-02`; F-020); cancel from `ACTION_PENDING` (`NCR-T1-08`; F-039); deviation `:consume` verb on the port (`DEV-T1-06`/`-07`; F-007), company + site applicability (`DEV-GRD-05`; F-012), base-UoM limits and usages (`DEV-GRD-04`; F-017), pending expiry, no approval after `valid_to`, reversal on `EXPIRED` / `REVOKED` (`DEV-GRD-07`, `DEV-T3-01`, `DEV-T1-07`; F-036); a `REJECT_LOT` lot released only under deviation (`DEV-UNR-03`; F-002); NCR supplier attribution at the disposition's origin pick (`NCR-T4-02`; F-019); registers' stage vocabulary (`QRG-T5-05`; F-033) |
| 2026-10-27 | **v1 — P8-17 S4** (`#636` S3 functional review). Edit / investigate also from `ACTION_PENDING` (`NCR-T2-01`, D13); withdraw closure and the WS-691 approve / return / reject buttons as rows (`NCR-T1-14`, `-15`); the S2 refusal codes as guards (`NCR-GRD-07` … `-11`); CAPA due date ≥ site-local today at create and on a changed edit (`NCR-GRD-11`, F10); owner scope per resource (`NCR-GRD-10`, F4); non-GRN attribution `UNDETERMINED` (`NCR-T4-02`, D8); no system return on a zero accumulation (`NCR-T4-04`, F11); WS-690 filter and serial search wording (`NCR-T5-01`, F8); read-only CAPA view, tab permission and `?tab=` (`NCR-T5-02`, F2); approve verbs require `wh_approval_requests:view` (`V511612`, R33 decision, F7); `NCR-OPEN-01` setting dormant until G16 (F5) |

## 8. Invariants and scenarios

`L-1` (an accepted-under-deviation release posts through the single writer); `FR-383`; `FR-408`; scenarios `WH-SC-720`, `WH-SC-721`, `WH-SC-723`…`WH-SC-725`, `WH-SC-731`.

## 9. Open rows

| ID | Question | Default |
|---|---|---|
| NCR-OPEN-01 | Should a `CRITICAL` NCR on a supplier lot automatically block further receipts from that supplier × item until closed? | **No** in v0 — the NCR is visible on WS-077 as a warning chip; a hard block is a client decision (`Q-Q4`) and would need a release path. **Dormant until G16:** `warehouse.quality.critical_ncr_receipt_policy` (`WARN` / `BLOCK`) is seeded and shown by `V511550`, but nothing reads it yet — neither the chip nor the block exists until the G16 lane lands, and G16 must land before release (S4 F5) |
| DEV-OPEN-01 | IATF 16949 §8.7.1.1 requires **customer** authorisation for a concession on customer-supplied or customer-specified product — record it? | `customer_authorisation_ref` is free text in `deviation_text` in v0; a structured field waits for the client's customer-specific requirements |
