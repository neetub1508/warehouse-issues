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
>
> **R32 (2026-10-25, `D-20` item 18).** The engine itself — tables, `ApprovalService`, WS-284 / WS-285, the
> alert job and the notification category — is **re-homed to core** as
> [`document-approval.contract.md`](document-approval.contract.md) (`DAP-*`, `issues/p8-30.md`, `wh_approval_*`),
> so one engine approves every core, trade and manufacturing document. The `TAM-*` rows below stay the
> **trade consumer's** truth: the trade document types and approve verbs (§0.1), trade's `REFUSE` default
> (`TAM-GRD-02`), trade conditions, and the trade callbacks. Where a `TAM` row names a `wht_approval_*` table,
> read the `wh_approval_*` table of the same role; `TRADE_APPROVAL_*` refusal codes are `APPROVAL_*`;
> `TradeApprovalAlertJob` is `WhApprovalAlertJob`; the in-app-only rule of `TAM-T3-01` is superseded by
> `DAP-T4-04` (e-mail / WhatsApp per `warehouse.approval.channels`) and same-level re-alerting is joined by
> upward escalation (`DAP-T3-02`).

---

## 0. Identity

| | |
|---|---|
| **Workflow** | Rule administration → submit opens request → level-by-level steps → approved / rejected / returned → document ladder continues; delegation; escalation alert |
| **Module** | `warehouse-trade` (`ai.warehousetrade`, `wht_`) |
| **Domain baseline** | `DECISIONS.md` D-16, `FR-408` (maker–checker), `GLOBAL-SETTINGS-DECISIONS.md` `warehouse.approval.pending_alert_hours` · FRD-TRADE FR-548…FR-555, `TRD-08`, `TRD-14` (exact condition match), `OD-34` |
| **Owning task body** | `issues/p9-03.md` |
| **Primary tables** | `wht_approval_rules` (+ `condition_match_mode`), `wht_approval_rule_conditions`, `wht_approval_rule_levels`, `wht_approval_rule_level_users`, `wht_approval_requests`, `wht_approval_steps`, `wht_approval_delegations` (+ `recorded_by`, `status`, `confirmed_by`) (`V550020`) |
| **Status columns** | `wht_approval_requests.status`, `wht_approval_steps.status` — no `CHECK` (`D-10`) |
| **Permission resources** | `wht_approval_rules:view/create/edit/export` · `wht_approval_requests:view` (inbox) · the document type's approve verb (§0.1) is the authority to act on a step |
| **Routes** | `/warehouse/trade/masters/approval-rules` (WS-284), `/warehouse/trade/approvals` (WS-285) · mobile: none |
| **Contract status / version** | `derived` · `v1 — 2026-10-22` (R29 folded) |

### 0.1 Document type → approve verb

| Document type | Verb that acts on its steps | Document type | Verb |
|---|---|---|---|
| `PR` | `wht_purchase_requisitions:approve` | `SQ` | `wht_customer_quotations:approve` |
| `CS` | `wht_comparative_statements:approve` | `SRC`, `SRC_AMENDMENT` | `wht_sales_rate_contracts:approve` |
| `PRC`, `PRC_AMENDMENT` | `wht_purchase_rate_contracts:approve` | `PRICE_LIST`, `PRICE_LIST_AMENDMENT` | `wht_price_lists:approve` |
| `PO`, `PO_SHORT_CLOSE`, `PO_CANCEL` | `wht_purchase_orders:approve` | `SO`, `SO_SHORT_CLOSE`, `SO_CANCEL` | `wht_sales_orders:approve` |
| `PO_RELEASE` | `wht_po_releases:approve` | `SO_RELEASE` | `wht_so_dispatch_releases:approve` |
| `PO_AMENDMENT` | `wht_po_amendments:approve` | `SO_AMENDMENT` | `wht_so_amendments:approve` |
| `AVL` | `wht_approved_vendor_items:approve` | `SRA` | `wht_sales_return_authorisations:approve` |
| `PROFILE_BLOCK` (supplier) | `wht_supplier_profiles:approve` | `PROFILE_BLOCK` (customer) | `wht_customer_profiles:approve` |
| — | — | `SO_CREDIT_OVERRIDE` *(R32)* | `wht_sales_orders:approve_credit_override` |
| — | — | `FEASIBILITY` *(R32)* | `wht_feasibility_reviews:approve` |

Each `:approve` depends on the resource's `:view` (`permission_dependencies`, seeded by the task owning the resource).

### Acceptance checks

| # | The requester expects… | Delivered by |
|---|---|---|
| A1 | Every trade document type is approved by one engine with value / quantity bands per currency (`WH-SC-489`) | `TAM-T1-03`, `TAM-GRD-01` |
| A2 | Nobody approves what they made, or two levels of one request (`WH-SC-489`, `WH-SC-493`) | `TAM-GRD-03` |
| A3 | No rule ⇒ refusal; nothing is approved by time (`WH-SC-490`, `WH-SC-494`) | `TAM-GRD-02`, `TAM-T3-01` |
| A4 | Reject / return carry a comment; resubmit is a new request (`WH-SC-492`) | `TAM-T1-07`, `TAM-T1-08` |
| A5 | Ambiguous rules cannot be saved, and a tie at submit is refused (`WH-SC-495`) | `TAM-GRD-05`, `-08` |
| A6 | A zero-level default never approves a document carrying a condition (`WH-SC-585`) | `TAM-GRD-01` |
| A7 | A delegation cannot be used to approve twice or for oneself (`WH-SC-569`) | `TAM-GRD-03`, `-07`, `TAM-T1-11` |

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
| Delegation | `PENDING_CONFIRMATION` → `ACTIVE`; *expired* derived from `valid_to` | `wht_approval_delegations.status` | `TAM-T1-10`, `-11` | `valid_to` | — |

### 1.2 Transitions

| ID | From | Event / action | To | Guard | Actor (permission) | Side effects | Comment | UI | Source |
|---|---|---|---|---|---|---|---|---|---|
| TAM-T1-01 | — / `INACTIVE` | Save / activate a rule | Rule `ACTIVE` | `TAM-GRD-05`, `-06` | `wht_approval_rules:create`/`edit` | audit | no | WS-284 Add / Activate | FR-548 |
| TAM-T1-02 | `ACTIVE` | Deactivate | `INACTIVE` | open requests keep the rule snapshot they started with | `wht_approval_rules:edit` | audit | no | WS-284 row action | FR-548 |
| TAM-T1-03 | — | Document submit calls `ApprovalService.open(docType, docId, version, value, qty, currency, conditions)` | Request `PENDING`, first step `PENDING`, rest `WAITING` | `TAM-GRD-01`, `-02`, `-08`, `-09` | the document's `:submit` | rule id, level snapshot, value, currency, condition set and maker frozen on the request (maker per FR-549 for system-drafted documents) | no | the document's Submit | FR-548, FR-549 |
| TAM-T1-04 | — | Matched rule has zero levels | Request `APPROVED` by `SYSTEM` | — | system | callback `onApproved` in the submit transaction; a port call it makes uses the submitter as `actingUserId` (`FRD-TRADE §12a`) | no | — | FR-550 |
| TAM-T1-04a | — | `open(type, id)` for a company × currency with no system zero-level seed yet for a type whose bean declares `zeroLevelDefaults()` (a company created after `V551030`, or a new company currency) | the seed rows written, then matching proceeds | idempotent: uk(`company_id`, `document_type_code`, `currency_code`, `condition_set`) WHERE `is_system_seed` | system (`WhApprovalDefaultRuleSeeder`, in the opening transaction) | audit `APPROVAL_RULE_SEEDED`; the same rows `V551030` writes for companies existing at migration time | no | — | FR-550 (R32-fix F-R32CA-014) |
| TAM-T1-05 | step `PENDING` | Approve | step `APPROVED`; next step `PENDING`, or request `APPROVED` after the last | `TAM-GRD-03`, `-04` | `wht_<doc>:approve` and member of the level | `onApproved` callback when last; audit | optional | WS-285, document Approve | FR-551 |
| TAM-T1-06 | level `ALL` | Each member approves | level done when all members approved | `TAM-GRD-03` | same | — | optional | same | FR-548 |
| TAM-T1-07 | step `PENDING` | Reject | request `REJECTED`, remaining steps `SKIPPED` | `TAM-GRD-03` | same | `onRejected` → document `REJECTED` | **yes** | same | FR-551 |
| TAM-T1-08 | step `PENDING` | Return for changes | request `RETURNED` | `TAM-GRD-03` | same | `onReturned` → document `DRAFT` | **yes** | same | FR-551 |
| TAM-T1-08a | `PENDING` | **Input changed** — a document the request depends on changed under it (a quotation revised under a `SUBMITTED` statement, `TRA-T1-08`) | request `RETURNED` by `SYSTEM`, comment *source changed: <ref>* | — | system | `onReturned` → document `DRAFT`, flagged stale | auto | — | FR-551 |
| TAM-T1-09 | `PENDING` | Maker withdraws before any step acted | `WITHDRAWN` | no step `APPROVED` | document `:submit` holder who is the maker | document → `DRAFT` | no | document *Withdraw* on every trade document screen | FR-551 |
| TAM-T1-10 | — | Record delegation | own: `ACTIVE`; for another approver: `PENDING_CONFIRMATION` | `TAM-GRD-07` | any approver for themselves; `wht_approval_rules:edit` for others | `recorded_by`; audit | no | WS-285 *Delegate* | FR-552 |
| TAM-T1-11 | delegation `PENDING_CONFIRMATION` | Confirm | `ACTIVE` | confirmer ≠ recorder ∧ ≠ delegate | `wht_approval_rules:edit` | `confirmed_by`; audit | no | WS-284 *Delegations* tab | FR-552 |

### 1.3 Guards

| ID | Predicate | Refusal | Lands on | Source |
|---|---|---|---|---|
| TAM-GRD-01 | Rule match: doc type = rule type ∧ company ∧ (site null or =) ∧ (department null or =) ∧ (category null or item category ∈) ∧ currency = ∧ value ∈ [from, to) ∧ qty ∈ [from, to) when set ∧ conditions: **`EXACT`** (default) — rule condition set = document condition set; **`INCLUDES`** — rule set ⊆ document set. **Most specific wins**: specificity = non-null scope dimensions + rule conditions + 1 when `EXACT`. **Non-monetary types** (`AVL`, `PROFILE_BLOCK`) carry no money: the request is opened with value 0 and the **company currency**, so their rules are written in the company currency with a value band that includes 0 (R31 F-TR-013) | — | — | FR-548, TRD-14 |
| TAM-GRD-02 | At least one rule matches | `422 TRADE_NO_APPROVAL_RULE` `{documentType, value, currency}` | Submit modal | FR-550 |
| TAM-GRD-03 | For **both** the actor and, when acting as a delegate, the principal: ≠ document maker (`created_by` and the submitter) ∧ has not acted on another step of this request (in own name or as / through a delegate); and the actor or the principal is a member of the level | `403 TRADE_APPROVAL_SELF` / `403 TRADE_APPROVAL_NOT_MEMBER` | Approve modal | FR-549 |
| TAM-GRD-04 | Document version = request's frozen version (no edit after submit) | `409 TRADE_APPROVAL_STALE` | Approve modal | FR-553 |
| TAM-GRD-05 | No other active rule of the same document type, company and currency that **could match the same document** — every scope dimension equal or null on one side, value and quantity bands overlapping, condition sets compatible under both rules' match modes — **with equal specificity** | `422 TRADE_APPROVAL_RULE_AMBIGUOUS` naming the other rule | WS-284 modal | FR-550 |
| TAM-GRD-06 | Bands `from < to`; ≥ 0 levels; each level ≥ 1 member or a role | field `422` | WS-284 modal | FR-548 |
| TAM-GRD-07 | Delegate ≠ principal; delegate ≠ recording user unless the recorder is the principal; date range valid; a delegate never acts on a request whose maker is the delegate or the principal (`TAM-GRD-03`) | field `422` | Delegate modal | FR-552 |
| TAM-GRD-08 | At open: exactly one rule has the highest specificity among the matches (a tie the save guard missed — e.g. after a rule edit — is refused, never broken arbitrarily) | `422 TRADE_APPROVAL_RULE_AMBIGUOUS {ruleIds}` | Submit modal | FR-550 |
| TAM-GRD-09 | Amendment documents (`*_AMENDMENT`): matched twice, on the new total and on the absolute delta; the request uses the match with more levels, a tie takes the new-total match; levels are never merged | — | — | FR-553 |
| TAM-GRD-10 | **Concurrency**: every edit, submit, transition and approval of a `wht_` document checks its optimistic `version`; a stale write changes nothing | `409 CONCURRENT_MODIFICATION` stale write (`TPR-OPEN-03`) | — | FR-618 |

### 1.4 Transitions that must be unreachable

| ID | Forbidden | What makes it unreachable | Source |
|---|---|---|---|
| TAM-UNR-01 | Approval by time, job or bulk script | no job writes a step; `TAM-T3-01` only alerts; the one system write, `TAM-T1-08a`, only **returns** | FR-554 |
| TAM-UNR-02 | A terminal request moving | terminal in the ladder; resubmit opens a new request | FR-551 |
| TAM-UNR-03 | Editing a document while its request is `PENDING` | every document service refuses edit when an open request exists (`409 TRADE_APPROVAL_PENDING`) | FR-553 |
| TAM-UNR-04 | `ADMIN` bypassing `TAM-GRD-03` | the check is not permission-based | FR-549 |

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from | Source |
|---|---|---|---|---|
| TAM-T2-01 | Add / edit / (de)activate rule | `wht_approval_rules:create`/`edit` | any | FR-548 |
| TAM-T2-02 | Open inbox | `wht_approval_requests:view` | — (own pending steps only) | FR-555 |
| TAM-T2-03 | Approve / reject / return | `wht_<doc>:approve` + level member | step `PENDING` | FR-555 |
| TAM-T2-04 | Withdraw | maker | request `PENDING`, nothing approved | FR-551 |
| TAM-T2-05 | Export rules | `wht_approval_rules:export` | — (auditor: none) | FR-616 |
| TAM-T2-06 | Record delegation for self / for another / confirm | approver / `wht_approval_rules:edit` / `wht_approval_rules:edit` (≠ recorder, ≠ delegate) | — | FR-552 |
| TAM-T2-07 | Every action in this table, and the auditor | `wht_<table>:<verb>` per FRD-TRADE FR-617 (`view`, `create`, `edit`, `export` + the workflow verbs above); `permission_dependencies` seeded; the auditor bundle holds `:view` only; record scope follows core's company / site grants; a bundle whose action calls a core port is also granted `warehouse:orders:port` in the trade seed | — | FR-617 |

## 3. T3 — Time-driven rules

| ID | Rule | Trigger | Changes | Notified | Job | Once? | Source |
|---|---|---|---|---|---|---|---|
| TAM-T3-01 | Pending escalation | step `PENDING` older than `warehouse.approval.pending_alert_hours` (default 24) | `alert_episode_started_at` on the step | level members + their active delegates — `TRADE_APPROVAL_PENDING` (FRD-TRADE §12b) | `TradeApprovalAlertJob` (hourly, `whb_job_runs`) | once per episode | FR-554 |
| TAM-T3-02 | Delegation expiry | `valid_to` passed | delegation inactive (derived) | — | computed on read | — | FR-552 |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in | Source |
|---|---|---|---|---|
| TAM-T4-01 | Request `APPROVED` | document callback `onApproved` runs **in the same transaction** (e.g. PO → `p8-01` port) | `ApprovalService` → `TradeApprovable` bean per doc type | FR-548 |
| TAM-T4-02 | Request `REJECTED` / `RETURNED` | document `REJECTED` / `DRAFT` | same | FR-551 |
| TAM-T4-03 | Every action | `whb_audit_events` row (actor, on-behalf-of, comment); the maker is notified `TRADE_APPROVAL_DECIDED` on approve / reject / return | same | FR-549, FR-552 |

## 5. T5 — Screen contract

### 5.1 WS-284 Approval Rules (reference **Customer**)
Grid `wht_approval_rules`, filter scope `WAREHOUSE_TRADE_APPROVAL_RULE`. Columns: `documentType`,
`companyName`, `warehouseName`, `departmentName`, `itemCategoryName`, `currencyCode`, `valueFrom`,
`valueTo`, `qtyFrom`, `qtyTo`, `conditions`, `levelCount`, `isActive`, audit. Filters: `documentType`,
`warehouseId`, `currencyCode`, `conditionMatchMode`, `isActive`. Tiles: active, inactive, zero-level, document
types covered, rules with conditions. Modal tabs: Scope · Bands & conditions (match mode) · Levels. Tab
*Delegations* (all delegations, confirm action). Empty state: *No approval rules — every submit is refused
until one exists.* Export: grid + audit.

### 5.2 WS-285 My Approvals (reference **Service Vehicle**)
Grid `wht_approval_requests_inbox` (own pending steps, and those of principals the user is an active delegate
for), scope `WAREHOUSE_TRADE_APPROVAL_INBOX`. Columns: `documentType`, `documentNumber`, `counterpartyName`,
`value`, `currencyCode`, `level`, `submittedByName` (user display helper), `submittedAt`, `pendingHours`,
`onBehalfOfName`. Filters: `documentType`, `warehouseId`, `currencyCode`, `valueFrom`/`valueTo` (applied
within the chosen currency), `overdueOnly`, `asDelegateOnly`. Tiles: my pending, overdue, as delegate,
decided by me today, returned by me (period) — counts, never summed values. Row actions: View (read-only
document preview) · Approve · Reject · Return. Toolbar: Delegate. No export.

## R32 additions (PRD 2026-10-24, `D-20`)

Rows added by the R32 fold (FRD-TRADE §4.15). Numbers continue each kind's sequence; where a number exists on one side of the purchase / sales mirror only, the asymmetry is stated in FRD-TRADE §5 rows M35…M40.

| ID | Kind | Rule | Refusal / effect | Source |
|---|---|---|---|---|
| TAM-GRD-11 | guard | PR HOD level = core resolver `DEPARTMENT_HEAD` (core `FR-722`); trade supplies the PR's `department_id` in `snapshot()`; nothing trade-local resolves approvers | core's resolver refusal | FR-740 |
| TAM-GRD-12 | guard | Trade registers `WhApprovable` for `SO_CREDIT_OVERRIDE` (`REFUSE`, no seed) and `FEASIBILITY` (`REFUSE` + seeded one-level `ROLE` rule `trade_design_head`) | `422 APPROVAL_NO_RULE` | FR-740, FR-766, FR-771 |
| TAM-T1-12 | transition | PR derived status `HOD_APPROVED` while a `DEPARTMENT_HEAD` level is approved and a later level pending (read from core steps, not stored); MR-origin PRs carry `from_approved_mr` | — | FR-743 |
| TAM-GRD-13 | guard | Band value = net of tax unless `warehouse.trade.approval.value_basis` = `GROSS` (default `NET`, client Q-P3); the basis is frozen on the request | — | FR-762 |
| TAM-GRD-14 | guard | New condition codes from trade's `WhApprovalConditionProvider`: `exceeds_pr`, `direct_po`, `sample_from_unlisted_vendor`, `price_differs_from_quotation`, `below_target_margin`, `affects_production`, `from_approved_mr` — none is matched by a zero-level seed (`EXACT`, empty set, `TRD-14`); install rules for `PR` / `PO` / `SO` / `SQ` default to `INCLUDES` on WS-284 so a condition-free rule also covers them and a rule naming the condition is more specific; seed `PR` × {`from_approved_mr`} `INCLUDES`, one `ROLE` level (purchase-manager bundle) in `V551030` | — | FR-745, FR-746, FR-747, FR-752, FR-757, FR-772 |

## 6. Out of scope

| Item | Decision | Reason |
|---|---|---|
| Bulk approve | not built | each approval is a deliberate act on a previewed document |
| Approval by e-mail link | not built | needs signed tokens; re-entry with a notification module. *(R32: e-mail / WhatsApp **notification** is now built by `DAP-T4-04`; approving by link stays out)* |
| FX conversion of bands | not built | `OD-34` |

## 7. Amendments

| Date | Rows | Change | Found by |
|---|---|---|---|
| 2026-10-22 | all | v0 derived | TRADE author |
| 2026-10-22 | §0.1, `TAM-T1-03`, `-04`, `-08a`, `-10`, `-11`, `TAM-GRD-01`, `-03`, `-05`, `-07`…`-09`, T2-06, T3, T4-03, §5 | R29 TP-F8, F9, F12, F26, F28, TS-F8, F9, F12 and contract quality: exact condition match, both-party maker check, intersecting-scope ambiguity, delegation confirmation, approve-verb map, inbox filters and tiles, notifications | R29 |
| 2026-10-23 | every T1, guard, unreachable, T3 and T4 row | `Source` column added, filled from FRD-TRADE §4, so every rule traces to the FR it proves | R30 `CP-FR-008` |
| 2026-10-23 | `TAM-GRD-01`, `-GRD-10`, every T2 row | R31: `AVL` / `PROFILE_BLOCK` match with value 0 in the company currency (F-TR-013); stale-write code (`TPR-OPEN-03`); T2 Source FRs (F-TR-019) | R31 |
| 2026-10-25 | header, §0, `TAM-T3-01`, `TAM-T4-03`, §6 e-mail row | R32: engine re-homed to core `document-approval` (`DAP-*`); this contract becomes the trade consumer; e-mail / WhatsApp and upward escalation added by `DAP-T3-02` / `DAP-T4-04` (supersedes the in-app-only rule) | R32 (`D-20` items 2-18, 2-19) |
| 2026-10-25 | `TAM-GRD-14` | R32-fix: `INCLUDES` default for install rules of condition-bearing trade types and a seeded `from_approved_mr` rule, so MR hand-off PRs, direct POs, PO-over-PR and quotation-price-changed SOs are approvable by default | R32 review F-R32TR-004 |
| 2026-10-25 | `TAM-GRD-11`, `TAM-GRD-12`, `TAM-T1-12`, `TAM-GRD-13`, `TAM-GRD-14` (new, *R32 additions*) | R32 fold of the client PRD (`D-20`): trade consumer of core `document-approval`: HOD level via core `DEPARTMENT_HEAD`, `SO_CREDIT_OVERRIDE` / `FEASIBILITY` types, value basis, new condition codes | R32 / `D-20` |
| 2026-10-25 | `TAM-T1-04a` (new) | **R32-fix (`F-R32CA-014`, `-015`).** Zero-level seeds are written for a company created after `V551030` at its first `open()` (idempotent seeder), so trade types are not refused `APPROVAL_NO_RULE` on a new company. The separate amendment types of §0.1 (`PO_AMENDMENT`, …) are the one amendment model `DAP-T1-12` now states for every type that declares one | R32 review |

## 8. Invariants and scenarios

`FR-408` maker–checker · `WH-SC-489`…`WH-SC-495`, `WH-SC-569`, `WH-SC-585`, `WH-SC-593`.

## 9. Open rows

| ID | Question | Status |
|---|---|---|
| TAM-OPEN-01 | Does a role-level member list resolve at submit (frozen) or at action time? | **Settled (R29): at action time**, so a joiner can act; the frozen part is the rule, levels and maker. `TAM-GRD-03` is evaluated at action time too |
