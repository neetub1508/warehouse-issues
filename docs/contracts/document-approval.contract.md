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

### 0.1 Document type → verb → opening event → policy → kept code → owner (complete, `D-21` item 6)

Every approving document type in `warehouse`, `warehouse-trade` and `warehouse-manufacturing` is a row here. **Verb** is the type's approve verb and the default `required_authority` of every level (`DAP-GRD-14`); a level may name a stronger verb. **Opening event** is the act that calls `open(type, id)` — always a Submit-like act, never the Approve click (`DAP-T1-03`). **Excluded actors** are the people `snapshot()` returns in `excludedActorIds` beside the maker (`DAP-GRD-03`). **Kept code** is the `403` the type returns for every `DAP-GRD-03` refusal (self-approval *and* same person on two levels), so no client breaks. No type keeps a `WhbMakerChecker` call beside the engine (`DAP-UNR-03`); `P8-30` is a hard dependency of every owner below — there is no interim single-checker fallback.

**(a) Built core approvals adopted by `P8-30`** (no behaviour change on upgrade unless stated)

| Document type | Verb | Opening event | Default policy | Excluded actors | Kept code | Owner |
|---|---|---|---|---|---|---|
| `MATERIAL_REQUISITION` | `wh_material_requisitions:approve` | built Submit (`MRQ-T1-02`) | `DOCUMENT_DEFINED`: 1 level ≤ `warehouse.stores.requisition_second_approval_value`, 2 above; L1 `DEPARTMENT_HEAD` when the policy says so (`MRQ-GRD-05`/`-11`). **Excess over standard** is a **second** `MATERIAL_REQUISITION` request opened at the standard request's `onApproved` with frozen condition `excess_over_standard` — one `PERMISSION_HOLDER` level of `wh_material_requisitions:approve_excess`, per-line decision (`MRQ-T1-27`) | requester, creator (excess request: + every approver of the standard request) | `REQUISITION_SELF_APPROVAL` | `p8-30` (adopt), `p8-09` (excess level) |
| `GATE_PASS` | `wh_gate_passes:approve` | **new** Submit `DRAFT → SUBMITTED` (`GTE-T1-10a`, added by `p8-30`; Approve then acts from `SUBMITTED`) | `SINGLE_LEVEL` | creator | `GATE_PASS_SELF_APPROVAL` | `p8-30` |
| `STOCK_ADJUSTMENT` | `wh_stock_adjustments:approve` | built Submit (`CCT-T1-03`/`-04`) | `DOCUMENT_DEFINED`: **zero levels** when every line is inside both thresholds and `warehouse.adjustment.auto_post_below_thresholds` is on (`SYSTEM_APPROVED`, `acting_user_id` = submitter, so the `_AUTO` post keeps its actor — `DAP-T1-04`); else one `PERMISSION_HOLDER` level | submitter | `ADJUSTMENT_SELF_APPROVAL` | `p8-30` |
| `COUNT_ADJUSTMENT` | `wh_counts:approve` | built Submit | `DOCUMENT_DEFINED`, same zero-level rule as the adjustment (`isApprovedOnSubmission` becomes `rule_source = ZERO_LEVEL`) | every attempt's submitter, every counter, every zone assignee (`WhCountValidationService`) | `COUNT_SELF_APPROVAL` | `p8-30` |
| `REVALUATION` | `wh_revaluations:approve` | Create (the saved revaluation is the proposal; `open` in the create transaction) | `SINGLE_LEVEL` | creator | `REVALUATION_SELF_APPROVAL` | `p8-30` |
| `NRV_ASSESSMENT` | `wh_nrv_assessments:approve` | Create | `SINGLE_LEVEL` | creator | `NRV_SELF_APPROVAL` | `p8-30` |
| `SITE_BRANCH_TRANSFER` | `wh_transfer_orders:approve` | Create of a transfer that needs approval (`FBL-GRD-12`) | `SINGLE_LEVEL` | creator | `TRANSFER_SELF_APPROVAL` | `p8-30` |
| `PURCHASE_ORDER` (core `wh_purchase_orders`; trade's `PO` is `TAM`'s) | `wh_purchase_orders:approve` | built Submit | `SINGLE_LEVEL` | submitter | `PO_APPROVER_IS_SUBMITTER` | `p8-30` |
| `RECEIPT_REVERSAL` | `wh_receipt_reversals:approve` | Create (the reversal request) | `SINGLE_LEVEL` | requester | `REVERSAL_SELF_APPROVAL` | `p8-30` |
| `SUPPLIER_RETURN` | `wh_supplier_returns:approve` | Create | `SINGLE_LEVEL` | creator | `SUPPLIER_RETURN_SELF_APPROVAL` | `p8-30` |
| `RMA` | `wh_rmas:approve` | Create | `SINGLE_LEVEL` | creator | `APPROVAL_SELF_APPROVAL` — **new** maker ≠ checker for this type (none is built; PRD §3, `FR-408`; release note) | `p8-30` |
| `THREE_WAY_MATCH` (exception) | `wh_three_way_matches:approve` | Match raising an exception (`/{id}/match`) | `SINGLE_LEVEL` | the matcher | `APPROVAL_SELF_APPROVAL` — **new**, as `RMA` | `p8-30` |
| `QI_SCRAP_DISPOSITION` | `wh_quality_inspections:approve` | scrap disposition recorded on an inspection line | `SINGLE_LEVEL` | the disposition's recorder | `MOVEMENT_SELF_APPROVED` | `p8-30` |
| `RETURN_SCRAP_DISPOSITION` | `wh_return_receipts:approve` | scrap disposition recorded on a return-receipt line | `SINGLE_LEVEL` | the disposition's recorder | `SCRAP_SELF_APPROVAL` | `p8-30` |

**(b) Built two-person checks that stay outside the engine** (each is a co-sign on one posting or repair act, not a document with a Submit; `DAP-UNR-03` names them as the only `WhbMakerChecker` callers left)

| Path | Verb | Kept code | Reason it is not a document approval |
|---|---|---|---|
| Stock movement approve (`WhbStockLedgerWriter`) | `whb_stock_movements:approve` | `MOVEMENT_SELF_APPROVED` | the ledger primitive the engine's own callbacks post through; routing it through the engine would recurse |
| Period override (`WhbPeriodOverrideRecorder`) | `whb_stock_period_overrides` co-sign | `PERIOD_OVERRIDE_SELF_APPROVED` | a named co-signer at post time on a closed period (`L-13` control), not a document |
| Warehouse registration (`WhbWarehouseValidationService`) | named approver on the site master | `WAREHOUSE_REGISTRATION_SELF_APPROVAL` | master-data onboarding with a named approver |
| Blocked-movement resolve (`WhBlockedMovementValidationService`) | `wh_blocked_movements:resolve` | `BLOCKED_MOVEMENT_SELF_APPROVED` | exception-console override co-sign |
| Handover void (`WhbAccountingHandoverValidationService`) | `whb_accounting_handovers:void` | `HANDOVER_VOID_BY_REQUESTER` | queue repair act (`AHO-T1-07`) |

**(c) Core documents still to build — each wires its own type** (the owner's task file carries the engine-wiring section: type, verb, policy, opening event, callbacks)

| Document type | Verb | Opening event | Default policy | Excluded actors | Kept code | Owner |
|---|---|---|---|---|---|---|
| `GRN_EXCESS` | `wh_goods_receipts:approve_excess` | Receive line recording an undecided excess (`GBM-T1-05`) | `SINGLE_LEVEL` | the line's last editor, the GRN creator | `GRN_EXCESS_SELF_APPROVAL` | `p8-04` (moved from `p8-30`'s adoption list — no code exists) |
| `MRN` | `wh_material_receipt_notes:authorise` | MRN Submit (`MRA-T1-02`) | `SINGLE_LEVEL` | preparer, submitter, the inspector (default, `MRA-GRD-04`) | `MRN_SELF_APPROVAL` | `p8-08` |
| `STORE_RETURN` (department step) | `wh_store_returns:approve_department` | Return Submit, when `DEPARTMENT_APPROVAL` is in `warehouse.stores.return_approval_steps` | `DOCUMENT_DEFINED`: one `DEPARTMENT_HEAD` level (deputy when the head is the maker); an install may add levels / bands on WS-284. Store *Verify* (quantity entry) and *Post* stay the return's own steps (`SIR-T1-14`/`-15`), not engine levels | submitter, creator | `STORE_RETURN_SELF_APPROVAL` | `p8-11` |
| `NCR_CLOSURE` | `wh_nonconformances:approve_closure` | Request closure | `SINGLE_LEVEL` | the NCR owner, the closure submitter, the raiser (`NCR-GRD-03`) | `NCR_SELF_CLOSURE` | `p8-17` |
| `QUALITY_DEVIATION` | L1 `wh_quality_deviations:approve`, L2 `required_authority = wh_quality_deviations:approve_final` | Deviation Submit | `DOCUMENT_DEFINED`: levels from `warehouse.quality.deviation_approval_levels` (default 2) — the bean returns them, no seed row | requester, creator | `DEVIATION_SELF_APPROVAL` | `p8-18` (the one deviation type; MFG consumes it, no MFG deviation type) |
| `INSPECTION_RESULT` | `wh_quality_inspections:approve_result` | Inspection Complete when `warehouse.quality.result_approval_mode` ≠ `NONE` (default `NONE` ⇒ no request, `D-21` item 7) | `SINGLE_LEVEL` (the bean adds the `APPROVER`-grant scope check, `QIC-GRD-01`) | every user who recorded a result | `RESULT_SELF_APPROVAL` | `p8-19` |

**(d) Trade types** — verbs per `TAM` §0.1; opening event = the document's Submit; policy `REFUSE` (zero-level seeds per `TAM-T1-04`, created per company, `TAM-T1-04a`); kept code `APPROVAL_SELF_APPROVAL`; owner `p9-03` + the document's task: `PR`, `CS`, `PRC`, `PRC_AMENDMENT`, `PO`, `PO_SHORT_CLOSE`, `PO_CANCEL`, `PO_RELEASE`, `PO_AMENDMENT`, `AVL`, `PROFILE_BLOCK` (supplier, customer), `SQ`, `SRC`, `SRC_AMENDMENT`, `PRICE_LIST`, `PRICE_LIST_AMENDMENT`, `SO`, `SO_SHORT_CLOSE`, `SO_CANCEL`, `SO_RELEASE`, `SO_AMENDMENT`, `SRA`, `SO_CREDIT_OVERRIDE` (the one credit override, `D-21` item 4), `FEASIBILITY`.

**(e) Manufacturing types** (`warehouse-manufacturing`, through `WhApprovalPort`)

| Document type | Verb | Opening event | Default policy | Kept code | Owner |
|---|---|---|---|---|---|
| `WHM_BOM` | `whm_boms:approve` | BOM version Submit | `DOCUMENT_DEFINED`: levels from `warehouse.manufacturing.bom.approval_levels` (default 2 — *Design Head + Plant Head*) | `BOM_SELF_APPROVAL` | `p10-03`, `p10-16` |
| `WHM_ROUTING` | `whm_routings:approve` | Routing version Submit | `DOCUMENT_DEFINED`, as `WHM_BOM` | `ROUTING_SELF_APPROVAL` | `p10-16` |
| `WHM_ECN` | `whm_ecns:approve` | ECN Submit | `DOCUMENT_DEFINED`: levels from `warehouse.manufacturing.ecn.approval_levels` (default 2) | `ECN_SELF_APPROVAL` | `p10-17` |
| `WHM_PRODUCTION_ORDER` | `whm_production_orders:approve` | Submit for approval when `order_approval_mode` applies (`PRO-T1-40`) | `SINGLE_LEVEL` | `ORDER_SELF_APPROVAL` | `p10-05` |
| `WHM_SHORTAGE_RELEASE` | `whm_production_orders:approve_release` | Release request (`PRO-T1-09`) when `release_requires_approval = true` **or** a shortage under mode `APPROVE` (`PRO-T1-42`) — one request per order, the R22 release approval included (F-R32MS-017) | `DOCUMENT_DEFINED`: one level, `required_authority` `:approve_shortage_release` when the snapshot's `has_shortage`, else `:approve_release` | `RELEASE_SELF_APPROVAL` | `p10-05` |
| `WHM_PDI` | `whm_pdi_records:sign` | PDI *Submit for signature* of a `PASSED` record whose result is final (`PUR-T1-14`) | `SINGLE_LEVEL` (excluded: the inspector, every result recorder and the unit's producers) | `PDI_SELF_SIGN` | `p10-22` |
| `WHM_DRAWING_RELEASE` | `whm_drawings:release` | Drawing revision Submit | `SINGLE_LEVEL` | `DRAWING_SELF_RELEASE` | `p10-18` |
| `WHM_SAMPLE_DISPATCH` | `whm_sample_requests:approve_dispatch` | Sample dispatch Submit | `SINGLE_LEVEL` | `SAMPLE_DISPATCH_SELF_APPROVAL` | `p10-19` |

**Amendment model (one, `DAP-T1-12`).** A document whose owner declares an amendment type (`PO_AMENDMENT`, `SO_AMENDMENT`, `PRC_AMENDMENT`, `SRC_AMENDMENT`, `PRICE_LIST_AMENDMENT`) is re-approved as **that type**, keyed to the parent document id at `document_revision` n+1; every other amendable type re-opens **its own type** at revision n+1 (`WHM_BOM` / `WHM_ROUTING` as a new version; `WHM_PRODUCTION_ORDER`: an edit of an `APPROVED` order is an amendment — reason from `DOCUMENT_AMENDMENT`, `revision_no + 1`, back to `PLANNED`, a new request; `PRO-T1-40`). Either way the band of the **new** value decides the levels. Core internal documents (requisition, MRN, store issue / return, gate pass, adjustment, count) are not amendable: cancel with a reason and re-raise.

**Upgrade (documents already pending).** On first start after `V511600`, `WhApprovalAdoptionBackfill` (idempotent, `whb_job_runs`) opens one request per adopted-type document already awaiting approval — `rule_source = DEFAULT_POLICY`, maker and excluded actors from the document's stored actors, `submitted_at` = the document's submit / create time — so it shows in My Approvals and the alert job; a document already decided gets no request.

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
| DAP-T1-03 | — | The type's **opening event** (§0.1 — a Submit-like act, never the Approve click) calls `open(type, id)` in its own transaction | Request `PENDING`, step 1 `PENDING`, rest `WAITING` | `DAP-GRD-01`, `-02`, `-08` | the document's `:submit` (or the §0.1 opening act's verb) | `OPENED` action; rule version, bands, limits, each level's `required_authority`, value, currency, conditions, revision, maker and `excludedActorIds` (with a reason per actor) frozen | no | document *Submit* | FR-720 |
| DAP-T1-04 | — | Matched rule has zero levels, or a `DOCUMENT_DEFINED` bean returns zero levels (below-threshold adjustment / count, §0.1) | Request `APPROVED` by `SYSTEM` | — | system | `SYSTEM_APPROVED` action with `acting_user_id` = the submitter (`actor_user_id` stays NULL); `onApproved(actingUserId)` in the submit transaction, so a `_AUTO` post keeps the submitter as its actor (`TAM-T1-04` pattern) | no | — | FR-721 |
| DAP-T1-05 | step `PENDING` | Approve | step `APPROVED`; next `PENDING`, or request `APPROVED` | `DAP-GRD-03`, `-04`, `-14`, `-15`, `-16` | approve verb + level member (or escalation target, or delegate) | `APPROVED` action with band / limit; `onApproved` when last | optional | WS-285 or document *Approve* | FR-722 |
| DAP-T1-06 | level `ALL` | Each member approves | level done when all have | `DAP-GRD-03` | same | one action per member | optional | same | FR-722 |
| DAP-T1-07 | step `PENDING` | Reject | request `REJECTED`, rest `SKIPPED` | `DAP-GRD-03`, `-10` | same | `onRejected` → document `REJECTED`, or `DRAFT` when `reject_returns_to_draft` | **reason** | same | FR-725 |
| DAP-T1-08 | step `PENDING` | Return for changes | request `RETURNED` | `DAP-GRD-03`, `-10` | same | `onReturned` → document `DRAFT` | **reason** | same | FR-725 |
| DAP-T1-08a | `PENDING` | A registered input of the request changed: a `WhApprovalInputWatcher` bean (type, outbox event code) fires — `PO` / `PO_RELEASE` pending: a source PR line cancelled or short-closed (`wht.purchase_requisition.line_closed`); `MATERIAL_REQUISITION` pending: the production order it serves cancelled (`whm.production_order.cancelled`). A type with no watcher never reaches this row | request `RETURNED` by `SYSTEM` | the request is still `PENDING` when the event is consumed (re-checked in the one `UPDATE`) | system, in the event consumer's transaction | `SYSTEM_RETURNED` action, comment *source changed: ref*; `onReturned` → document `DRAFT` | auto | — | FR-725 |
| DAP-T1-09 | `PENDING` | Maker withdraws before any step acted | `WITHDRAWN` | no `APPROVED` action yet | maker with the document `:submit` | document → `DRAFT` | no | document *Withdraw* | FR-725 |
| DAP-T1-10 | — | Record a delegation for another approver | delegation `PENDING_CONFIRMATION` | `DAP-GRD-11` | `wh_approval_rules:edit` | audit | no | WS-284 *Delegations* | FR-722 |
| DAP-T1-11 | `PENDING_CONFIRMATION` | Confirm | `ACTIVE` | confirmer ≠ recorder, ≠ delegate | `wh_approval_rules:edit` | audit | no | same | FR-722 |
| DAP-T1-12 | Request `APPROVED` | Document amendment at revision n+1 | new Request `PENDING` | `DAP-GRD-07` | the document's amend verb | **One model (§0.1 *Amendment model*):** the owner's declared amendment type (`PO_AMENDMENT`, `SO_AMENDMENT`, `PRC_AMENDMENT`, `SRC_AMENDMENT`, `PRICE_LIST_AMENDMENT`) keyed to the parent document id, else the document's own type; `OPENED` with `document_revision` n+1 and a `DOCUMENT_AMENDMENT` reason; the band of the **new** value decides the levels | **reason** | document *Amend* | FR-728 |

### 1.3 Guards

| ID | Predicate | Refusal | Source |
|---|---|---|---|
| DAP-GRD-01 | The most specific active rule for type × company × currency whose site, department, item category (every line in the subtree), value band, qty band and condition set (`EXACT` / `INCLUDES`) match; none ⇒ the type's default policy | — | FR-721 |
| DAP-GRD-02 | `REFUSE` default and no rule | `422 APPROVAL_NO_RULE` | FR-721 |
| DAP-GRD-03 | The actor ≠ maker, ≠ submitter, ∉ the request's frozen `excludedActorIds` (§0.1 *Excluded actors*), has acted on no other level of the request; a delegate does not act for the maker or an excluded actor; evaluated in the service | `403` the type's kept code (§0.1) for **every** case — self, excluded actor and same person on two levels (so `MATERIAL_REQUISITION` keeps `REQUISITION_SELF_APPROVAL` for first-and-final); `403 APPROVAL_SELF_APPROVAL` / `403 APPROVAL_SAME_PERSON_TWO_LEVELS` only for a type that keeps no code | FR-723 |
| DAP-GRD-04 | The actor is a current member of the step's level (resolved at action time), an active delegate of one, or an escalation target of the step — each also passing `DAP-GRD-14` and `-15` | `403 APPROVAL_NOT_MEMBER` | FR-722 |
| DAP-GRD-05 | A saved rule cannot tie with another active rule on any document | `409 APPROVAL_RULE_AMBIGUOUS` naming the other rule | FR-721 |
| DAP-GRD-06 | Levels contiguous from 1; `ROLE` needs `role_id`; `USERS` needs ≥ 1 user; value / qty from ≤ to | `422` field errors | FR-722 |
| DAP-GRD-07 | Edit while a request is `PENDING` / after `APPROVED` is refused; only the document's amend action changes an approved document | `409 APPROVAL_PENDING` / `409 DOCUMENT_APPROVED_LOCKED` | FR-728 |
| DAP-GRD-08 | Submit needs a **distinct-person cover** of the whole request: an assignment of one different eligible person (member holding the level's `required_authority`, within its limit, not maker / submitter / excluded) to every level, checked as a bipartite match, not level by level | `422 APPROVAL_NO_ELIGIBLE_APPROVER · level` | FR-723 |
| DAP-GRD-09 | Reject / return / cancel / short-close / amend / deviation / override carry a reason code of the right context. **Cancel / close coverage (documents only):** ASN cancel; count cancel; demand order cancel and schedule-line close-short; gate entry cancel; gate pass cancel and close-short; goods receipt cancel; landed-cost document cancel; material requisition cancel, close and line close; purchase order cancel, close, line close and schedule-line close; recall close; revaluation cancel; RMA cancel; shipment cancel; stock adjustment cancel; supplier return cancel and close; three-way match cancel; transfer order cancel; work order cancel; the `WhDemandOrderPort`, `WhPurchaseOrderPort` and `WhMaterialRequisitionPort` cancel / close commands (the sibling passes its document's reason); every trade and manufacturing document cancel / short-close. **Excluded (operational tasks, no reason):** pick / putaway / replenishment / generic task cancel, pack session, wave, cross-dock plan, dock appointment, pickup request, receiving session, shift handover, manifest cancel, LPN close, stock-period close (its own close check). An endpoint that already refuses without a reason keeps its code | `422 APPROVAL_REASON_REQUIRED` / `422 REASON_REQUIRED` | FR-725 |
| DAP-GRD-10 | A reason code whose `requires_note` is set needs a note | `422 REASON_NOTE_REQUIRED` | FR-725 |
| DAP-GRD-11 | A delegation is dated, `valid_to` ≥ `valid_from`, delegate ≠ principal | `422` field errors | FR-722 |
| DAP-GRD-12 | The step's request version equals the document's current revision when acting | `409 APPROVAL_STALE_VERSION` | FR-728 |
| DAP-GRD-14 | The actor (member, delegate or escalation target) holds the step's frozen `required_authority` (the level's verb, default the type's §0.1 verb) in the document's scope — e.g. `QUALITY_DEVIATION` L2 needs `wh_quality_deviations:approve_final`; a delegate needs it too (delegation never lends authority) | `403 APPROVAL_AUTHORITY_MISSING · requiredAuthority` | FR-722 |
| DAP-GRD-15 | The document value ≤ the step's frozen `approver_limit` (null = no limit) for whoever acts — member, delegate or escalation target; above it the actor cannot approve this level and the step waits for someone within limit (the next level's members become eligible only through `DAP-T3-02`); reject and return are not limited | `403 APPROVAL_LIMIT_EXCEEDED · limit · value` | FR-722, PRD §3 |
| DAP-GRD-16 | After every escalated act (and at `DAP-T3-02` before widening), a distinct-person cover (`DAP-GRD-08`) must still exist for every remaining level; an escalated approve that would leave a later level with no eligible distinct person is refused, so the original members or the final escalation role act instead | `409 APPROVAL_COVER_LOST · level` | FR-726 |
| DAP-GRD-13 | A reason code offered on a reject, return, amendment, deviation, override, cancel or short-close picker is an active code of that action's context (`APPROVAL_REJECT`, `APPROVAL_RETURN`, `DOCUMENT_AMENDMENT`, `DEVIATION`, `APPROVAL_OVERRIDE`, or the document's own cancel / close context); labels resolve per context, never from another context's code | `422 REASON_CODE_CONTEXT_MISMATCH · reasonCodeId` | FR-737 |

### 1.4 Transitions that must be unreachable

| ID | Forbidden | What makes it unreachable | Source |
|---|---|---|---|
| DAP-UNR-01 | Approval by time, job or bulk script | the alert and escalation job write only `ALERTED` / `ESCALATED`; no bulk endpoint | FR-726 |
| DAP-UNR-02 | A terminal request moving | terminal in the ladder; resubmit / amend opens a new request | FR-725 |
| DAP-UNR-03 | A document approving itself outside the engine | `ApprovalRegistryVerifier`: every §0.1 (a) / (c) / (d) / (e) type has a registered `WhApprovable` and its Approve endpoint calls `act`; an architecture test fails on any `WhbMakerChecker` caller other than the five §0.1 (b) co-sign paths | FR-720 |
| DAP-UNR-04 | `ADMIN` bypassing `DAP-GRD-03` | the check is not permission-based | FR-723 |
| DAP-UNR-05 | Changing or deleting a decision | `trg_wh_approval_actions_append_only` (`APPROVAL_ACTION_IMMUTABLE`) on `UPDATE` / `DELETE`, and a `BEFORE TRUNCATE` statement trigger `trg_wh_approval_actions_no_truncate` (the built `V501011` idiom — the application role owns the table, so a revoke would not hold); no update path, no `updated_*` columns | FR-724 |

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from | Source |
|---|---|---|---|---|
| DAP-T2-01 | Add / edit / (de)activate rule | `wh_approval_rules:create`/`edit` | any | FR-721 |
| DAP-T2-02 | Open My Approvals | `wh_approval_requests:view` | own pending, delegated and escalated steps | FR-729 |
| DAP-T2-03 | Approve / reject / return | the step's `required_authority` (`DAP-GRD-14`) + `DAP-GRD-04`; approve also `DAP-GRD-15` | step `PENDING` | FR-722 |
| DAP-T2-04 | Register / SoD report / export | `wh_approval_requests:view:all` / `:view:branch` / `:export` | — | FR-729 |
| DAP-T2-05 | Export rules | `wh_approval_rules:export` | — | FR-721 |

## 3. T3 — Time-driven rules

| ID | Rule | Trigger | Changes | Notified | Job | Once? | Source |
|---|---|---|---|---|---|---|---|
| DAP-T3-01 | Pending alert | step `PENDING` older than `warehouse.approval.pending_alert_hours` (24) | `ALERTED` action; `alert_episode_started_at` | level members + active delegates — `APPROVAL_PENDING` | `WhApprovalAlertJob` (hourly) — the built `WhbPendingApprovalAlertService` sources retire as their type adopts (§T3 note) | once per episode | FR-726 |
| DAP-T3-02 | Upward escalation | step `PENDING` older than the rule's `escalation_hours`, else `warehouse.approval.escalation_hours` (48; `0` = never) | `ESCALATED` action; `escalation_level + 1`; next level's members (last level: the final escalation role) become eligible — only those who keep `DAP-GRD-16`'s cover; when none would, the step records `ESCALATED` with no new target and re-alerts | them — `APPROVAL_ESCALATED` | same | once per level | FR-726 |
| DAP-T3-03 | Delegation expiry | `valid_to` passed | inactive (derived) | — | on read | — | FR-722 |

**Built pending-alert sources (`D-21` item 6).** `WhbPendingApprovalAlertService` (`warehouse.approval.pending_alert_hours`) already alerts for five `WhbPendingApprovalSource` providers — stock adjustment, count, core PO, material requisition, receipt reversal. As each type adopts the engine (`p8-30`), its provider is **deleted in the same change** and `WhApprovalAlertJob` alerts for it; when the last provider goes, `WhbPendingApprovalAlertService` is retired. A type is never alerted by both (one alert per pending document).

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
| 2026-10-25 | §0.1 (rewritten), `DAP-T1-03`, `-04`, `-05`, `-08a`, `-12`, `DAP-GRD-03`, `-04`, `-08`, `-09`, `-14`…`-16` (new), `DAP-UNR-03`, `-05`, `DAP-T2-03`, `DAP-T3-01`, `-02`, §T3 note | **R32-fix (`F-R32CA-002`…`-008`, `-010`, `-011`, `-015`, `-018`…`-020`, `-022`, `-029`; `D-21` item 6).** §0.1 is the complete type table — verb, opening event, policy, excluded actors, kept code, owner — for the 14 adopted built paths, the 5 co-sign paths kept outside the engine, the 6 core types still to build (`GRN_EXCESS` moved to `p8-04`), every trade type and the 8 `WHM_*` types; one amendment model; upgrade backfill. Requests freeze `excludedActorIds` and per-level `required_authority`; approver limits are enforced; Submit and every escalated act check a distinct-person cover; below-threshold adjustment / count is `DOCUMENT_DEFINED` zero-level with the submitter as acting user; `SYSTEM_RETURNED` fires only from registered input watchers; the type's kept code covers the two-level case; TRUNCATE is blocked by trigger; the built alert sources retire as types adopt; GRD-09 names its cancel / close endpoints and excludes operational tasks | R32 review (`R32-functional-review-core-approvals.md`) |

## 8. Invariants and scenarios

`FR-408` maker–checker · `WH-SC-740`…`WH-SC-745` · trade `WH-SC-489`…`WH-SC-495` through `TAM`.

## 9. Open rows

| ID | Question | Status |
|---|---|---|
| DAP-OPEN-01 | Escalation default 48 h and channel default `IN_APP` | **default — client Q-A2**; both are settings, changeable on the settings page |
