# Functional Contract — Document approval engine (one engine for every document type)

> **What this is.** The functional truth for how **any** warehouse document — core, trade or manufacturing —
> is approved: rule matching, levels, maker ≠ checker, the append-only decision record with the band and
> limit used, escalation, notification channels, delegation, the lock after approval and re-approval of an
> amendment. Every document contract cites a `DAP-*` row instead of restating approval.
>
> **What this is not.** It owns no document's states. Each document contract says which of its transitions
> *opens* a request and what *approved* / *rejected* / *returned* does to it. The trade-specific rows (the
> trade document types, their conditions and approve verbs, trade's `REFUSE` default) stay in
> [`trade-approval-matrix.contract.md`](trade-approval-matrix.contract.md), which since `D-20` item 18 is a
> **consumer** of this engine.
>
> **Status.** Derived 2026-10-25 (v0) from `D-20` items 2-13b, 2-18, 2-19 and PRD 2026-10-24 §3 / §13.2 /
> §13.3, re-homing `TAM`'s engine rows into core; not yet run through the `functional-reviewer`. **No code
> exists yet.**

---

## 0. Identity

| | |
|---|---|
| **Workflow** | Rule administration → document submit opens a request → level-by-level steps (alert, escalation) → approved / rejected / returned / withdrawn → document ladder continues; amendment re-opens at the next revision |
| **Module** | `warehouse` (`ai.warehouse`, `wh_`); port `ai.warehouse.port.approval` for `warehouse-trade` / `warehouse-manufacturing` |
| **Domain baseline** | `DECISIONS.md` D-20 items 2-13b, 2-18, 2-19; `FR-408` (maker–checker); FRD-STORES `FR-720`…`FR-729`; trade `FR-548`…`FR-555` (now the trade consumer's rules); `OD-34` (no FX on bands) |
| **Owning task body** | `issues/p8-30.md`; trade consumer `issues/p9-03.md` |
| **Primary tables** | `wh_approval_rules`, `wh_approval_rule_conditions`, `wh_approval_rule_levels`, `wh_approval_rule_level_users`, `wh_approval_requests`, `wh_approval_steps`, `wh_approval_actions` (append-only), `wh_approval_delegations`, `wh_approval_notifications` (`V511600`) |
| **Status columns** | `wh_approval_requests.status`, `wh_approval_steps.status` — projections of `wh_approval_actions`, no `CHECK` (`D-10`) |
| **Permission resources** | `wh_approval_rules:view/create/edit/export` · `wh_approval_requests:view` (own inbox) / `:view:all` / `:view:branch` (register, SoD) / `:export` · the document type's approve verb (§0.1) is the authority to act on a step |
| **Routes** | `/warehouse/approvals/rules` (WS-284), `/warehouse/approvals` (WS-285) · mobile: none (`D-20` item 5) |
| **Contract status / version** | `derived` · `v0 — 2026-10-25` |

### 0.1 Core document type → approve verb → default policy

| Document type | Verb | Default policy | Refusal code kept |
|---|---|---|---|
| `MATERIAL_REQUISITION` | `wh_material_requisitions:approve` | `DOCUMENT_DEFINED` (1 level ≤ threshold, 2 above, `MRQ-GRD-05`/`-11`) | `REQUISITION_SELF_APPROVAL` |
| `GATE_PASS` | `wh_gate_passes:approve` | `SINGLE_LEVEL` | `GATE_PASS_SELF_APPROVAL` |
| `STOCK_ADJUSTMENT`, `COUNT_ADJUSTMENT` | the adjustment / count approve verbs (`CCT-GRD-03`, `-07`) | `SINGLE_LEVEL` | `ADJUSTMENT_SELF_APPROVAL`, `COUNT_SELF_APPROVAL` |
| `REVALUATION`, `NRV_ASSESSMENT` | `CVL-T1-06`, `-10` verbs | `SINGLE_LEVEL` | `REVALUATION_SELF_APPROVAL`, `NRV_SELF_APPROVAL` |
| `SITE_BRANCH_TRANSFER` | `FBL-GRD-12` verb | `SINGLE_LEVEL` | the `FBL` code |
| `GRN_EXCESS` | `GBM-T1-05` verb | `SINGLE_LEVEL` | the `GBM` code |
| `MATERIAL_RECEIPT_NOTE` | `wh_material_receipt_notes:authorise` | `SINGLE_LEVEL` (wired by `p8-08`) | `MRN_SELF_APPROVAL` |
| `NONCONFORMANCE` (closure) | `wh_nonconformances:approve_closure` | `SINGLE_LEVEL` (wired by `p8-17`, R32) | `NCR_SELF_CLOSURE` |
| `QUALITY_DEVIATION` | `wh_quality_deviations:approve` → `:approve_final` | `DOCUMENT_DEFINED` (2 levels by default, `warehouse.quality.deviation_approval_levels`; wired by `p8-18`, R32) | `DEVIATION_SELF_APPROVAL` |
| `STORE_RETURN` (department step) | `wh_store_returns:approve_department` | `SINGLE_LEVEL` when a rule exists, else the head / deputy check (`p8-11`, R32) | `STORE_RETURN_SELF_APPROVAL` |
| trade types | `TAM` §0.1 | `REFUSE` | `APPROVAL_SELF_APPROVAL` |
| manufacturing types (BOM / routing release, production order release, PDI, drawing, sample dispatch, deviation) | their task's `:approve` / `:release` verb | declared by the owning `P10` task | the type's own |

### Acceptance checks

| # | The requester expects… | Delivered by |
|---|---|---|
| A1 | One engine approves every document type, configurable per type × site × department × item category × value / qty band (`WH-SC-740`) | `DAP-T1-03`, `DAP-GRD-01` |
| A2 | Nobody approves what they made, or two levels of one request — not even `ADMIN` (`WH-SC-741`) | `DAP-GRD-03`, `DAP-UNR-04` |
| A3 | The decision record cannot be changed, and it says which band and limit were used (`WH-SC-742`) | `DAP-T4-02`, `DAP-UNR-05` |
| A4 | An overdue step moves up, and nothing is approved by time (`WH-SC-743`) | `DAP-T3-02`, `DAP-UNR-01` |
| A5 | Approvers hear about it in-app, by e-mail and by WhatsApp where configured, and a failed channel loses nothing (`WH-SC-744`) | `DAP-T4-04` |
| A6 | An approved document changes only by amendment, which is approved again (`WH-SC-745`) | `DAP-GRD-07`, `DAP-T1-12` |

## 1. T1 — State machine

### 1.1 Status inventory

| Entity | Status | Represented by | Reachable via | Exits via | Kind |
|---|---|---|---|---|---|
| Rule | `ACTIVE` / `INACTIVE` | `wh_approval_rules.is_active` | `DAP-T1-01`, `-02` | each other | active |
| Request | `PENDING` | projection | `DAP-T1-03` | `-05`…`-09` | initial |
| Request | `APPROVED` | projection; `decided_at` | `DAP-T1-05`, `-04` | none (an amendment is a new request) | terminal |
| Request | `REJECTED` / `RETURNED` / `WITHDRAWN` | projection | `DAP-T1-07`, `-08`, `-09` | none | terminal |
| Step | `WAITING` → `PENDING` → `APPROVED` / `REJECTED` / `RETURNED` / `SKIPPED` | projection | with the request | — | — |
| Action | written once | `wh_approval_actions` row | every transition | never | append-only |

### 1.2 Transitions

| ID | From | Event / action | To | Guard | Actor (permission) | Side effects | Comment | UI | Source |
|---|---|---|---|---|---|---|---|---|---|
| DAP-T1-01 | — / `INACTIVE` | Save / activate a rule | Rule `ACTIVE` | `DAP-GRD-05`, `-06` | `wh_approval_rules:create`/`edit` | audit; copy-on-write when the rule was ever matched | no | WS-284 | FR-721 |
| DAP-T1-02 | `ACTIVE` | Deactivate | `INACTIVE` | open requests keep their frozen rule version | `wh_approval_rules:edit` | audit | no | WS-284 | FR-721 |
| DAP-T1-03 | — | Document submit calls `open(type, id)` | Request `PENDING`, step 1 `PENDING`, rest `WAITING` | `DAP-GRD-01`, `-02`, `-08` | the document's `:submit` | `OPENED` action; rule version, bands, limits, value, currency, conditions, revision and maker frozen | no | document *Submit* | FR-720 |
| DAP-T1-04 | — | Matched rule has zero levels | Request `APPROVED` by `SYSTEM` | — | system | `SYSTEM_APPROVED` action; `onApproved` in the submit transaction | no | — | FR-721 |
| DAP-T1-05 | step `PENDING` | Approve | step `APPROVED`; next `PENDING`, or request `APPROVED` | `DAP-GRD-03`, `-04` | approve verb + level member (or escalation target, or delegate) | `APPROVED` action with band / limit; `onApproved` when last | optional | WS-285 or document *Approve* | FR-722 |
| DAP-T1-06 | level `ALL` | Each member approves | level done when all have | `DAP-GRD-03` | same | one action per member | optional | same | FR-722 |
| DAP-T1-07 | step `PENDING` | Reject | request `REJECTED`, rest `SKIPPED` | `DAP-GRD-03`, `-10` | same | `onRejected` → document `REJECTED`, or `DRAFT` when `reject_returns_to_draft` | **reason** | same | FR-725 |
| DAP-T1-08 | step `PENDING` | Return for changes | request `RETURNED` | `DAP-GRD-03`, `-10` | same | `onReturned` → document `DRAFT` | **reason** | same | FR-725 |
| DAP-T1-08a | `PENDING` | An input the request depends on changed | request `RETURNED` by `SYSTEM` | — | system | `SYSTEM_RETURNED` action, comment *source changed: ref* | auto | — | FR-725 |
| DAP-T1-09 | `PENDING` | Maker withdraws before any step acted | `WITHDRAWN` | no `APPROVED` action yet | maker with the document `:submit` | document → `DRAFT` | no | document *Withdraw* | FR-725 |
| DAP-T1-10 | — | Record a delegation for another approver | delegation `PENDING_CONFIRMATION` | `DAP-GRD-11` | `wh_approval_rules:edit` | audit | no | WS-284 *Delegations* | FR-722 |
| DAP-T1-11 | `PENDING_CONFIRMATION` | Confirm | `ACTIVE` | confirmer ≠ recorder, ≠ delegate | `wh_approval_rules:edit` | audit | no | same | FR-722 |
| DAP-T1-12 | Request `APPROVED` | Document amendment at revision n+1 | new Request `PENDING` | `DAP-GRD-07` | the document's amend verb | `OPENED` with `document_revision` n+1 and a `DOCUMENT_AMENDMENT` reason; the band of the **new** value decides the levels | **reason** | document *Amend* | FR-728 |

### 1.3 Guards

| ID | Predicate | Refusal | Source |
|---|---|---|---|
| DAP-GRD-01 | The most specific active rule for type × company × currency whose site, department, item category (every line in the subtree), value band, qty band and condition set (`EXACT` / `INCLUDES`) match; none ⇒ the type's default policy | — | FR-721 |
| DAP-GRD-02 | `REFUSE` default and no rule | `422 APPROVAL_NO_RULE` | FR-721 |
| DAP-GRD-03 | The actor ≠ maker, ≠ submitter, has acted on no other level of the request; a delegate does not act for the maker; evaluated in the service | `403 APPROVAL_SELF_APPROVAL` (or the type's kept code, §0.1) / `403 APPROVAL_SAME_PERSON_TWO_LEVELS` | FR-723 |
| DAP-GRD-04 | The actor is a current member of the step's level (resolved at action time), an active delegate of one, or an escalation target of the step | `403 APPROVAL_NOT_MEMBER` | FR-722 |
| DAP-GRD-05 | A saved rule cannot tie with another active rule on any document | `409 APPROVAL_RULE_AMBIGUOUS` naming the other rule | FR-721 |
| DAP-GRD-06 | Levels contiguous from 1; `ROLE` needs `role_id`; `USERS` needs ≥ 1 user; value / qty from ≤ to | `422` field errors | FR-722 |
| DAP-GRD-07 | Edit while a request is `PENDING` / after `APPROVED` is refused; only the document's amend action changes an approved document | `409 APPROVAL_PENDING` / `409 DOCUMENT_APPROVED_LOCKED` | FR-728 |
| DAP-GRD-08 | Submit needs at least one eligible approver per level other than the maker | `422 APPROVAL_NO_ELIGIBLE_APPROVER · level` | FR-723 |
| DAP-GRD-09 | Reject / return / cancel / short-close / amend / deviation / override carry a reason code of the right context (cancel and short-close: every core and trade document's cancel / close-short endpoint) | `422 APPROVAL_REASON_REQUIRED` / `422 REASON_REQUIRED` | FR-725 |
| DAP-GRD-10 | A reason code whose `requires_note` is set needs a note | `422 REASON_NOTE_REQUIRED` | FR-725 |
| DAP-GRD-11 | A delegation is dated, `valid_to` ≥ `valid_from`, delegate ≠ principal | `422` field errors | FR-722 |
| DAP-GRD-12 | The step's request version equals the document's current revision when acting | `409 APPROVAL_STALE_VERSION` | FR-728 |
| DAP-GRD-13 | A reason code offered on a reject, return, amendment, deviation, override, cancel or short-close picker is an active code of that action's context (`APPROVAL_REJECT`, `APPROVAL_RETURN`, `DOCUMENT_AMENDMENT`, `DEVIATION`, `APPROVAL_OVERRIDE`, or the document's own cancel / close context); labels resolve per context, never from another context's code | `422 REASON_CODE_CONTEXT_MISMATCH · reasonCodeId` | FR-737 |

### 1.4 Transitions that must be unreachable

| ID | Forbidden | What makes it unreachable | Source |
|---|---|---|---|
| DAP-UNR-01 | Approval by time, job or bulk script | the alert and escalation job write only `ALERTED` / `ESCALATED`; no bulk endpoint | FR-726 |
| DAP-UNR-02 | A terminal request moving | terminal in the ladder; resubmit / amend opens a new request | FR-725 |
| DAP-UNR-03 | A document approving itself outside the engine | `ApprovalRegistryVerifier`: each adopted Approve endpoint calls `act`; no `WhbMakerChecker` call beside it | FR-720 |
| DAP-UNR-04 | `ADMIN` bypassing `DAP-GRD-03` | the check is not permission-based | FR-723 |
| DAP-UNR-05 | Changing or deleting a decision | `trg_wh_approval_actions_append_only` (`APPROVAL_ACTION_IMMUTABLE`), no update path, no `updated_*` columns | FR-724 |

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from | Source |
|---|---|---|---|---|
| DAP-T2-01 | Add / edit / (de)activate rule | `wh_approval_rules:create`/`edit` | any | FR-721 |
| DAP-T2-02 | Open My Approvals | `wh_approval_requests:view` | own pending, delegated and escalated steps | FR-729 |
| DAP-T2-03 | Approve / reject / return | approve verb + `DAP-GRD-04` | step `PENDING` | FR-722 |
| DAP-T2-04 | Register / SoD report / export | `wh_approval_requests:view:all` / `:view:branch` / `:export` | — | FR-729 |
| DAP-T2-05 | Export rules | `wh_approval_rules:export` | — | FR-721 |

## 3. T3 — Time-driven rules

| ID | Rule | Trigger | Changes | Notified | Job | Once? | Source |
|---|---|---|---|---|---|---|---|
| DAP-T3-01 | Pending alert | step `PENDING` older than `warehouse.approval.pending_alert_hours` (24) | `ALERTED` action; `alert_episode_started_at` | level members + active delegates — `APPROVAL_PENDING` | `WhApprovalAlertJob` (hourly) | once per episode | FR-726 |
| DAP-T3-02 | Upward escalation | step `PENDING` older than the rule's `escalation_hours`, else `warehouse.approval.escalation_hours` (48; `0` = never) | `ESCALATED` action; `escalation_level + 1`; next level's members (last level: the final escalation role) become eligible | them — `APPROVAL_ESCALATED` | same | once per level | FR-726 |
| DAP-T3-03 | Delegation expiry | `valid_to` passed | inactive (derived) | — | on read | — | FR-722 |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in | Source |
|---|---|---|---|---|
| DAP-T4-01 | Request `APPROVED` / `REJECTED` / `RETURNED` / `WITHDRAWN` | the type's callback runs **in the same transaction** | `WhApprovalService` → `WhApprovable` | FR-720 |
| DAP-T4-02 | Every transition | one `wh_approval_actions` row with rule version, level, band, approver limit, value, currency, revision, actor, on-behalf-of, via-escalation, reason, comment | same | FR-724 |
| DAP-T4-03 | Every action | `whb_audit_events` row (actor, on-behalf-of, summary) | same | FR-724 |
| DAP-T4-04 | After commit of an action that notifies | one `wh_approval_notifications` row per recipient × channel in `warehouse.approval.channels`; a failure is `FAILED`, never rolls back, never stamps the episode as delivered | `WhApprovalNotifier` (platform `NotificationService`, `EmailNotificationService`, `WhatsAppService`) | FR-727 |
| DAP-T4-05 | The document grid / detail is read | `approvalStatus` (`NOT_SUBMITTED` / `PENDING_L{n}` / `APPROVED` / `REJECTED` / `RETURNED` / `WITHDRAWN`) and the history panel come from the engine | `WhApprovalQueryService` | FR-729 |

## 5. T5 — Screen contract

### 5.1 WS-284 Approval Rules (reference **Customer**)
Per `issues/p8-30.md` §Screens: grid `wh_approval_rules`, scope `WAREHOUSE_APPROVAL_RULE`, tabs Scope · Bands & conditions · Levels · Escalation, *Delegations* tab, export.

### 5.2 WS-285 My Approvals (reference **Service Vehicle**)
Per `issues/p8-30.md` §Screens: inbox across modules, scope `WAREHOUSE_APPROVAL_INBOX`, tabs Register and Segregation of duties; inline approve only when `requiresDocumentScreen()` is false.

## 6. Out of scope

| Item | Decision | Reason |
|---|---|---|
| Approval by e-mail / WhatsApp reply or link | not built | needs signed one-time tokens; the message links to the web page |
| Bulk approve | not built | each approval is a deliberate act on a previewed document |
| FX conversion of bands | not built | `OD-34` |
| Mobile approval | not built | `D-20` item 5 |

## 7. Amendments

| Date | Rows | Change | Found by |
|---|---|---|---|
| 2026-10-25 | all | v0 derived — R32: engine re-homed from `TAM` to core, append-only actions, band / limit recorded, upward escalation, e-mail / WhatsApp, amendment re-approval, default policies, adoption of the built single-step approvals | R32 (`D-20` items 2-13b, 2-18, 2-19) |
| 2026-10-25 | §0.1 | three document types added by the R32 core fold: `NONCONFORMANCE` closure (`p8-17`), `QUALITY_DEVIATION` (`p8-18`), `STORE_RETURN` department step (`p8-11`); `MATERIAL_REQUISITION` gains an excess level over standard (`MRQ-T1-27`, `p8-09`) | R32 core fold |

## 8. Invariants and scenarios

`FR-408` maker–checker · `WH-SC-740`…`WH-SC-745` · trade `WH-SC-489`…`WH-SC-495` through `TAM`.

## 9. Open rows

| ID | Question | Status |
|---|---|---|
| DAP-OPEN-01 | Escalation default 48 h and channel default `IN_APP` | **default — client Q-A2**; both are settings, changeable on the settings page |
