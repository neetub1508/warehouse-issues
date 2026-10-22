# Functional Contract — Trade approval matrix (maker–checker for every trade document)

> **What this is.** The functional truth for how any `warehouse-trade` document is approved: rule
> matching, levels, maker ≠ checker, delegation, escalation, and the hand-back to the document's own
> ladder. Every other trade contract cites a `TAM-*` row instead of restating approval.
>
> **What this is not.** It does not own any document's states; each document contract says which of
> its transitions *opens* an approval request and what *approved* / *rejected* / *returned* does to it.
>
> **Status.** Derived 2026-10-22 (v0) from `docs/frd/FRD-TRADE.md`; not yet run through the
> `functional-reviewer`. **No code exists yet.**

---

## 0. Identity

| | |
|---|---|
| **Workflow** | Rule administration → submit opens request → level-by-level steps → approved / rejected / returned → document ladder continues; delegation; escalation alert |
| **Module** | `warehouse-trade` (`ai.warehousetrade`, `wht_`) |
| **Domain baseline** | `DECISIONS.md` D-16, `FR-408` (maker–checker), `GLOBAL-SETTINGS-DECISIONS.md` `warehouse.approval.pending_alert_hours` · FRD-TRADE FR-548…FR-555, `TRD-08`, `OD-34` |
| **Owning task body** | `issues/p9-03.md` |
| **Primary tables** | `wht_approval_rules`, `wht_approval_rule_levels`, `wht_approval_rule_level_users`, `wht_approval_requests`, `wht_approval_steps`, `wht_approval_delegations` (`V550020`) |
| **Status columns** | `wht_approval_requests.status`, `wht_approval_steps.status` — no `CHECK` (`D-10`) |
| **Permission resources** | `wht_approval_rules:view/create/edit/export` · `wht_approval_requests:view` (inbox) · document-specific `wht_<doc>:approve` is the authority to act on a step |
| **Routes** | `/warehouse/trade/masters/approval-rules` (WS-284), `/warehouse/trade/approvals` (WS-285) · mobile: none |
| **Contract status / version** | `derived` · `v0 — 2026-10-22` |

### Acceptance checks

| # | The requester expects… | Delivered by |
|---|---|---|
| A1 | Every trade document type is approved by one engine with value / quantity bands per currency (`WH-SC-489`) | `TAM-T1-03`, `TAM-GRD-01` |
| A2 | Nobody approves what they made, or two levels of one request (`WH-SC-489`, `WH-SC-493`) | `TAM-GRD-03` |
| A3 | No rule ⇒ refusal; nothing is approved by time (`WH-SC-490`, `WH-SC-494`) | `TAM-GRD-02`, `TAM-T3-01` |
| A4 | Reject / return carry a comment; resubmit is a new request (`WH-SC-492`) | `TAM-T1-07`, `TAM-T1-08` |
| A5 | Ambiguous rules cannot be saved (`WH-SC-495`) | `TAM-GRD-05` |

## 1. T1 — State machine

### 1.1 Status inventory

| Entity | Status | Represented by | Reachable via | Exits via | Kind |
|---|---|---|---|---|---|
| Rule | `ACTIVE` | `wht_approval_rules.is_active = true` | `TAM-T1-01` | `-02` | active |
| Rule | `INACTIVE` | `is_active = false` | `TAM-T1-02` | `-01` | active |
| Request | `PENDING` | `wht_approval_requests.status` | `TAM-T1-03` | `-05`…`-09` | initial |
| Request | `APPROVED` | status; `decided_at` | `TAM-T1-05`, `-04` (zero level) | none | terminal |
| Request | `REJECTED` | status | `TAM-T1-07` | none | terminal |
| Request | `RETURNED` | status | `TAM-T1-08` | none | terminal |
| Request | `WITHDRAWN` | status | `TAM-T1-09` | none | terminal |
| Step | `WAITING` → `PENDING` → `APPROVED` / `REJECTED` / `RETURNED` / `SKIPPED` | `wht_approval_steps.status` | with the request | — | — |

### 1.2 Transitions

| ID | From | Event / action | To | Guard | Actor (permission) | Side effects | Comment | UI |
|---|---|---|---|---|---|---|---|---|
| TAM-T1-01 | — / `INACTIVE` | Save / activate a rule | Rule `ACTIVE` | `TAM-GRD-05`, `-06` | `wht_approval_rules:create`/`edit` | audit | no | WS-284 Add / Activate |
| TAM-T1-02 | `ACTIVE` | Deactivate | `INACTIVE` | open requests keep the rule snapshot they started with | `wht_approval_rules:edit` | audit | no | WS-284 row action |
| TAM-T1-03 | — | Document submit calls `ApprovalService.open(docType, docId, version, value, qty, currency, conditions)` | Request `PENDING`, first step `PENDING`, rest `WAITING` | `TAM-GRD-01`, `-02` | the document's `:submit` | rule id, level snapshot, value, currency frozen on the request | no | the document's Submit |
| TAM-T1-04 | — | Matched rule has zero levels | Request `APPROVED` by `SYSTEM` | — | system | callback `onApproved` in the submit transaction | no | — |
| TAM-T1-05 | step `PENDING` | Approve | step `APPROVED`; next step `PENDING`, or request `APPROVED` after the last | `TAM-GRD-03`, `-04` | `wht_<doc>:approve` and member of the level | `onApproved` callback when last; audit | optional | WS-285, document Approve |
| TAM-T1-06 | level `ALL` | Each member approves | level done when all members approved | `TAM-GRD-03` | same | — | optional | same |
| TAM-T1-07 | step `PENDING` | Reject | request `REJECTED`, remaining steps `SKIPPED` | `TAM-GRD-03` | same | `onRejected` → document `REJECTED` | **yes** | same |
| TAM-T1-08 | step `PENDING` | Return for changes | request `RETURNED` | `TAM-GRD-03` | same | `onReturned` → document `DRAFT` | **yes** | same |
| TAM-T1-09 | `PENDING` | Maker withdraws before any step acted | `WITHDRAWN` | no step `APPROVED` | document `:submit` holder who is the maker | document → `DRAFT` | no | document Withdraw |
| TAM-T1-10 | — | Record delegation | delegation row | `TAM-GRD-07` | any approver for themselves; `wht_approval_rules:edit` for others | audit | no | WS-285 *Delegate* |

### 1.3 Guards

| ID | Predicate | Refusal | Lands on |
|---|---|---|---|
| TAM-GRD-01 | Rule match: doc type = rule type ∧ company ∧ (site null or =) ∧ (department null or =) ∧ (category null or item category ∈) ∧ currency = ∧ value ∈ [from, to) ∧ qty ∈ [from, to) when set ∧ rule conditions ⊆ document conditions; **most specific wins** (count of non-null dimensions, conditions count as dimensions) | — | — |
| TAM-GRD-02 | At least one rule matches | `422 TRADE_NO_APPROVAL_RULE` `{documentType, value, currency}` | Submit modal |
| TAM-GRD-03 | Actor ≠ document maker (`created_by` and the submitter) ∧ actor has not acted on another step of this request ∧ actor (or the principal they act for) is a member of the level | `403 TRADE_APPROVAL_SELF` / `403 TRADE_APPROVAL_NOT_MEMBER` | Approve modal |
| TAM-GRD-04 | Document version = request's frozen version (no edit after submit) | `409 TRADE_APPROVAL_STALE` | Approve modal |
| TAM-GRD-05 | No other active rule with identical dimension set and overlapping bands | `422 TRADE_APPROVAL_RULE_AMBIGUOUS` naming the other rule | WS-284 modal |
| TAM-GRD-06 | Bands `from < to`; ≥ 0 levels; each level ≥ 1 member or a role | field `422` | WS-284 modal |
| TAM-GRD-07 | Delegate ≠ self; date range valid; a delegate never acts on a request whose maker is the delegate (`TAM-GRD-03` applies to the delegate in their own name) | field `422` | Delegate modal |

### 1.4 Transitions that must be unreachable

| ID | Forbidden | What makes it unreachable |
|---|---|---|
| TAM-UNR-01 | Approval by time, job or bulk script | no job writes a step; `TAM-T3-01` only alerts |
| TAM-UNR-02 | A terminal request moving | terminal in the ladder; resubmit opens a new request |
| TAM-UNR-03 | Editing a document while its request is `PENDING` | every document service refuses edit when an open request exists (`409 TRADE_APPROVAL_PENDING`) |
| TAM-UNR-04 | `ADMIN` bypassing `TAM-GRD-03` | the check is not permission-based |

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from |
|---|---|---|---|
| TAM-T2-01 | Add / edit / (de)activate rule | `wht_approval_rules:create`/`edit` | any |
| TAM-T2-02 | Open inbox | `wht_approval_requests:view` | — (own pending steps only) |
| TAM-T2-03 | Approve / reject / return | `wht_<doc>:approve` + level member | step `PENDING` |
| TAM-T2-04 | Withdraw | maker | request `PENDING`, nothing approved |
| TAM-T2-05 | Export rules | `wht_approval_rules:export` | — (auditor: none) |

## 3. T3 — Time-driven rules

| ID | Rule | Trigger | Changes | Notified | Job | Once? |
|---|---|---|---|---|---|---|
| TAM-T3-01 | Pending escalation | step `PENDING` older than `warehouse.approval.pending_alert_hours` (default 24) | `alert_episode_started_at` on the step | level members + their delegates | `TradeApprovalAlertJob` (hourly, `whb_job_runs`) | once per episode |
| TAM-T3-02 | Delegation expiry | `valid_to` passed | delegation inactive (derived) | — | computed on read | — |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in |
|---|---|---|---|
| TAM-T4-01 | Request `APPROVED` | document callback `onApproved` runs **in the same transaction** (e.g. PO → `p8-01` port) | `ApprovalService` → `TradeApprovable` bean per doc type |
| TAM-T4-02 | Request `REJECTED` / `RETURNED` | document `REJECTED` / `DRAFT` | same |
| TAM-T4-03 | Every action | `whb_audit_events` row (actor, on-behalf-of, comment) | same |

## 5. T5 — Screen contract

### 5.1 WS-284 Approval Rules (reference **Customer**)
Grid `wht_approval_rules`, filter scope `WAREHOUSE_TRADE_APPROVAL_RULE`. Columns: `documentType`,
`companyName`, `warehouseName`, `departmentName`, `itemCategoryName`, `currencyCode`, `valueFrom`,
`valueTo`, `qtyFrom`, `qtyTo`, `conditions`, `levelCount`, `isActive`, audit. Filters: `documentType`,
`warehouseId`, `currencyCode`, `isActive`. Tiles: active, inactive, zero-level, document types covered,
rules with conditions. Modal tabs: Scope · Bands & conditions · Levels. Export: grid + audit.

### 5.2 WS-285 My Approvals (reference **Service Vehicle**)
Grid `wht_approval_requests_inbox` (own pending steps). Columns: `documentType`, `documentNumber`,
`counterpartyName`, `value`, `currencyCode`, `level`, `submittedByName`, `submittedAt`, `pendingHours`.
Filters: `documentType`, `warehouseId`, `overdueOnly`. Row actions: View (read-only document preview) ·
Approve · Reject · Return. Toolbar: Delegate. No export.

## 6. Out of scope

| Item | Decision | Reason |
|---|---|---|
| Bulk approve | not built | each approval is a deliberate act on a previewed document |
| Approval by e-mail link | not built | needs signed tokens; re-entry with a notification module |
| FX conversion of bands | not built | `OD-34` |

## 7. Amendments

| Date | Rows | Change | Found by |
|---|---|---|---|
| 2026-10-22 | all | v0 derived | TRADE author |

## 8. Invariants and scenarios

`FR-408` maker–checker · `WH-SC-489`…`WH-SC-495`.

## 9. Open rows

| ID | Question | Status |
|---|---|---|
| TAM-OPEN-01 | Does a role-level member list resolve at submit (frozen) or at action time? | **Proposed: at action time**, so a joiner can act; the frozen part is the rule and levels. DEFERRED-TO-p9-03 |
