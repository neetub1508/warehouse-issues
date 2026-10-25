# Functional Contract — Manufacturing engineering change: ECN, drawings and revisions, samples and customer feedback

> **What this is.** The functional truth for the R32 engineering layer of `warehouse-manufacturing` (`D-20` items 1, 3):
> the **engineering change notice** with impact analysis on open orders and old-part stock and Design Head + Plant Head
> approval (`R-08` reversed), the **drawing master** with controlled revisions, release by a checker, watermarking and the
> copy-issue log, and the **sample** flow — request from enquiry / SO, sample production order on a trial BOM, internal
> check, dispatch, customer feedback iterations, and the production gate that the customer's approval lifts. FRD-MFG
> §6.1 FR-792…FR-801.
>
> **What this is not.** BOM / routing versioning itself is [`mfg-bom.contract.md`](mfg-bom.contract.md) and
> [`mfg-shop-floor.contract.md`](mfg-shop-floor.contract.md); the approval engine is core `p8-30`
> (`document-approval.contract.md`); the gate pass is `p8-03`; trade's enquiry / SO buttons are the trade fold's half.
>
> **Status.** Derived 2026-10-25 (v0) under `D-20`. Not ratified; run through `functional-reviewer` before `P10-17`,
> `P10-18`, `P10-19` are built.

---

## 0. Identity

| | |
|---|---|
| **Workflow** | ECN: draft → items (old → new `DRAFT` versions) → submit (impact computed) → decisions → two-level approval → implement (versions approved, impacts executed). Drawing: upload revision → internal review → released for sample → customer approved → released for production → superseded. Sample: request → submit → sample order (trial BOM) → check → dispatch (approval) → feedback → next iteration or approved → production released |
| **Module** | `warehouse-manufacturing`; ports declared in core by `P10-18` (`DrawingRevisionPort`) and `P10-19` (`SampleRequestPort`), optional beans (MD-51) |
| **Owning tasks** | `issues/p10-17.md` (ECN) · `issues/p10-18.md` (drawings) · `issues/p10-19.md` (samples) |
| **Primary tables** | `whm_ecns`, `whm_ecn_items`, `whm_ecn_impacts` (`V562030`); `whm_drawings`, `whm_drawing_revisions`, `whm_drawing_issues` (`V562040`); `whm_sample_requests`, `whm_sample_iterations` (`V562050`) |
| **Status columns** | ECN `DRAFT`/`SUBMITTED`/`APPROVED`/`IMPLEMENTED`/`REJECTED`/`CANCELLED`; drawing revision `DRAFT`/`INTERNAL_REVIEW`/`RELEASED_FOR_SAMPLE`/`CUSTOMER_APPROVED`/`RELEASED_FOR_PRODUCTION`/`SUPERSEDED`/`REJECTED`; sample request `DRAFT`/`SUBMITTED`/`IN_DEVELOPMENT`/`AWAITING_FEEDBACK`/`APPROVED`/`REJECTED`/`CANCELLED` — no `CHECK` (`D-10`) |

## 1. T1 — State machine

### 1.1 Transitions

| ID | From | Event | To | Guard | Actor | Side effects | Source |
|---|---|---|---|---|---|---|---|
| ECH-T1-01 | — | Create ECN; add items (link or create new `DRAFT` versions of `APPROVED` BOMs / routings / released drawings) | `DRAFT` | `ECH-GRD-01` | `whm_ecns:create` / `:edit` | `ECN-` number at create | FR-792 |
| ECH-T1-02 | `DRAFT` | Submit | `SUBMITTED` | ≥ 1 item; every new version structurally valid (`BOM-GRD-01`…, `SFL-GRD-03`) | `whm_ecns:submit` | impact rows computed (`ECH-T4-01`); approval request (`p8-30`, `WHM_ECN`) | FR-792, FR-793 |
| ECH-T1-03 | `SUBMITTED` | Record impact decisions | `SUBMITTED` | decision allowed for the impact type and order state (`ECH-GRD-02`) | `whm_ecns:edit` | `decided_by/at` | FR-793 |
| ECH-T1-04 | `SUBMITTED` | Last level approves | `APPROVED` | `ECH-GRD-03` (all decided); no user on two levels; submitter never approves | engine | — | FR-792 |
| ECH-T1-05 | `SUBMITTED` | Return / Reject | `DRAFT` / `REJECTED` | note required | engine | new versions stay `DRAFT` (reject: they are deleted if never referenced) | FR-792 |
| ECH-T1-06 | `APPROVED` | **Implement** | `IMPLEMENTED` | effectivity date ≥ today (or unit serial named); new versions still valid | `whm_ecns:implement` | every new version `APPROVED` with the ECN's effectivity, predecessors end-dated (`BOM-T4-01`); impact decisions executed (`ECH-T4-02`) in one transaction | FR-792, FR-793 |
| ECH-T1-07 | `DRAFT` · `SUBMITTED` | Cancel | `CANCELLED` | — | `whm_ecns:cancel` | approval request withdrawn | FR-792 |
| ECH-T1-10 | — | Upload a drawing revision | `DRAFT` | `ECH-GRD-04` | `whm_drawings:create` | file(s) linked as platform documents | FR-795 |
| ECH-T1-11 | `DRAFT` | Submit for review | `INTERNAL_REVIEW` | — | `whm_drawings:submit` | — | FR-795 |
| ECH-T1-12 | `INTERNAL_REVIEW` | Release for sample / Return / Reject | `RELEASED_FOR_SAMPLE` / `DRAFT` / `REJECTED` | actor ≠ uploader (`ECH-GRD-05`) | `whm_drawings:approve` | — | FR-795 |
| ECH-T1-13 | `RELEASED_FOR_SAMPLE` | Customer approval (sample feedback `APPROVED`, or manual with the customer's document) | `CUSTOMER_APPROVED` | document attached when manual | system / `whm_drawings:approve` | — | FR-795, FR-801 |
| ECH-T1-14 | `INTERNAL_REVIEW` · `CUSTOMER_APPROVED` | Release for production | `RELEASED_FOR_PRODUCTION` | `ECH-GRD-05`; when a released revision exists, only through an ECN (`FR-794`) | `whm_drawings:release` | the prior released revision → `SUPERSEDED`, its open copies listed for recall (`ECH-T4-04`) | FR-795, FR-797 |
| ECH-T1-15 | any released revision | Issue a copy | — | controlled copy needs `:print_controlled`; non-released prints watermarked | `whm_drawings:issue` | `whm_drawing_issues` row | FR-797 |
| ECH-T1-20 | — | Create a sample request (manual, or through `SampleRequestPort.open` from trade) | `DRAFT` | `ECH-GRD-06` | `whm_sample_requests:create` / port | `SMR-` number; source frozen | FR-798 |
| ECH-T1-21 | `DRAFT` | Submit | `SUBMITTED` | — | `whm_sample_requests:submit` | — | FR-798 |
| ECH-T1-22 | `SUBMITTED` · `AWAITING_FEEDBACK` | Create sample order (iteration n) | `IN_DEVELOPMENT` | `ECH-GRD-07` | `whm_sample_requests:create_order` | `SAMPLE` production order on the trial BOM / routing; iteration row | FR-799 |
| ECH-T1-23 | `IN_DEVELOPMENT` | Record internal check | `IN_DEVELOPMENT` | checker ≠ the order's supervisor; report attached | `whm_sample_requests:record_check` | `check_result` | FR-800 |
| ECH-T1-24 | `IN_DEVELOPMENT` | Dispatch | `AWAITING_FEEDBACK` | check `PASS`; dispatch approved (`ECH-GRD-08`); courier / AWB / date | `whm_sample_requests:dispatch` | gate pass `SAMPLE` (returnable / non) or india challan sourced on the iteration | FR-800 |
| ECH-T1-25 | `AWAITING_FEEDBACK` | Record feedback | `APPROVED` / `IN_DEVELOPMENT` (with changes) / `REJECTED` | `ECH-GRD-09` | `whm_sample_requests:record_feedback` | `APPROVED` → drawing `CUSTOMER_APPROVED` (`ECH-T1-13`), production gate lifted (`ECH-T4-05`) | FR-800, FR-801 |
| ECH-T1-26 | any open | Cancel | `CANCELLED` | open sample order cancelled first | `whm_sample_requests:cancel` | gate lifted | FR-798 |

### 1.2 Guards

| ID | Predicate | Refusal | Source |
|---|---|---|---|
| ECH-GRD-01 | An item's old version is `APPROVED` (BOM / routing) or `RELEASED_FOR_PRODUCTION` (drawing); one ECN item per old version among live ECNs | `422 ECN_ITEM_INVALID`; `409 ECN_ITEM_IN_OTHER_ECN` | FR-792 |
| ECH-GRD-02 | `RE_EXPLODE_UNSTARTED` only on an order with nothing posted; stock decisions only on stock impacts | `422 ECN_DECISION_NOT_ALLOWED` | FR-793 |
| ECH-GRD-03 | Every impact row has a decision | `422 ECN_IMPACT_UNDECIDED` | FR-793 |
| ECH-GRD-04 | Drawing number unique per company; revision code follows the scheme and is new for the drawing; ≥ 1 file | `422 DRAWING_REVISION_INVALID`; `422 DRAWING_FILE_REQUIRED` | FR-795 |
| ECH-GRD-05 | Reviewer / releaser ≠ uploader of the revision | `403 DRAWING_SELF_RELEASE` | FR-795 |
| ECH-GRD-06 | Request has item or specification; quantity > 0; customer set for enquiry / SO sources | `422 SAMPLE_REQUEST_INVALID` | FR-798 |
| ECH-GRD-07 | Drawing revision ≥ `RELEASED_FOR_SAMPLE`; trial BOM / routing only on a `SAMPLE` order | `409 SAMPLE_DRAWING_NOT_RELEASED`; `422 TRIAL_BOM_ONLY_ON_SAMPLE_ORDER` | FR-799 |
| ECH-GRD-08 | Dispatch approver ≠ requester when approval is required | `403 SAMPLE_DISPATCH_SELF_APPROVAL` | FR-800 |
| ECH-GRD-09 | `APPROVED_WITH_CHANGES` needs a newer drawing revision before the next iteration's order | `409 NEW_DRAWING_REVISION_REQUIRED` | FR-800 |
| ECH-GRD-10 | A `STANDARD` order whose source / covered SO line has an open blocking sample request is refused at create and release | `409 SAMPLE_APPROVAL_PENDING` | FR-801 |
| ECH-GRD-11 | *New version* of a released object outside an ECN while `ecn_required_for_released_change` | `409 ECN_REQUIRED`; approving it directly `409 VERSION_GOVERNED_BY_ECN` | FR-794 |

### 1.3 Unreachable

| ID | Never happens | Why | Source |
|---|---|---|---|
| ECH-UNR-01 | A released drawing revision edited | revisions are immutable; a change is a new revision | FR-795 |
| ECH-UNR-02 | An SO line refused for want of sample approval | the gate is on production (`ECH-GRD-10`), never the SO | FR-801 |
| ECH-UNR-03 | Two `RELEASED_FOR_PRODUCTION` revisions of one drawing | partial unique index | FR-795 |

## 2. T2 — Action × role × state

| ID | Action | Permission | Persona | Source |
|---|---|---|---|---|
| ECH-T2-01 | Create / submit ECN | `whm_ecns:create/edit/submit` | design engineer | FR-792 |
| ECH-T2-02 | Approve ECN levels | engine roles | Design Head, Plant Head | FR-792 |
| ECH-T2-03 | Implement ECN | `whm_ecns:implement` | production engineer / planner | FR-792 |
| ECH-T2-04 | Upload / review / release drawings | `whm_drawings:create` / `:approve` / `:release` | design engineer / Design Head | FR-795 |
| ECH-T2-05 | Sample request, order, check, dispatch, feedback | `whm_sample_requests:*` | sales, R&D, QC; `:approve_dispatch` Sales Manager | FR-798…FR-800 |

## 3. T3 — Time-driven rules

| ID | Trigger | Effect | Source |
|---|---|---|---|
| ECH-T3-01 | Golden sample `retain_until` passes | alert to the sample owner; nothing auto-disposed | FR-800 |
| ECH-T3-02 | Returnable sample past the gate pass expected return | core gate-pass overdue alert, sourced on the iteration | FR-800 |

## 4. T4 — Cross-entity effects

| ID | Cause | Effect | Source |
|---|---|---|---|
| ECH-T4-01 | ECN submitted | impact rows: open orders on old versions (with state), open purchase demand for removed components, old-part stock per site | FR-793 |
| ECH-T4-02 | ECN implemented | `RE_EXPLODE` / `RE_EXPLODE_UNSTARTED` re-snapshot orders (the `PRO-T1-07` re-explode path, allowed by the ECN for a `RELEASED` order with nothing posted — `PRO-T1-45`); `HOLD` sets the hold with `ENGINEERING_CHANGE`; `REWORK` creates a `PLANNED` rework order; `SCRAP` a core scrap adjustment request; `RETURN_TO_VENDOR` a core supplier-return draft; result ids recorded | FR-793 |
| ECH-T4-03 | Mass replace from where-used (`BOM-T1-20`) | one `DRAFT` ECN with a new `DRAFT` version per selected BOM | FR-783, FR-792 |
| ECH-T4-04 | Drawing revision superseded | open copies in `whm_drawing_issues` listed for recall; frozen BOM / order references flagged superseded on WS-320 / WS-324 | FR-796, FR-797 |
| ECH-T4-05 | Sample request `APPROVED` / `CANCELLED` | `ECH-GRD-10` no longer refuses for its SO line | FR-801 |
| ECH-T4-06 | `DrawingRevisionPort.currentReleased(itemId)` called by trade / core | returns drawing no., revision, document id of the current released revision | FR-796 |

## 5. T5 — Screen contract

| ID | Screen | Contents | Source |
|---|---|---|---|
| ECH-T5-01 | WS-384 ECNs | Service Vehicle; tabs Items · Impact (decisions inline) · Approval (engine steps, append-only) · Implement log | FR-792, FR-793 |
| ECH-T5-02 | WS-385 Drawings | Service Vehicle; tabs Revisions · Files (platform document viewer) · Issue log · Where used; print shows the watermark on non-released revisions | FR-795…FR-797 |
| ECH-T5-03 | WS-386 Sample Requests | Service Vehicle; tabs Iterations · Orders · Dispatch · Feedback; dates `formatDateSync` | FR-798…FR-801 |

## 6. Error codes

`ECN_ITEM_INVALID`, `ECN_ITEM_IN_OTHER_ECN`, `ECN_DECISION_NOT_ALLOWED`, `ECN_IMPACT_UNDECIDED`, `ECN_SELF_APPROVAL`,
`ECN_REQUIRED`, `VERSION_GOVERNED_BY_ECN`, `DRAWING_REVISION_INVALID`, `DRAWING_FILE_REQUIRED`, `DRAWING_SELF_RELEASE`,
`SAMPLE_REQUEST_INVALID`, `SAMPLE_DRAWING_NOT_RELEASED`, `TRIAL_BOM_ONLY_ON_SAMPLE_ORDER`, `SAMPLE_DISPATCH_SELF_APPROVAL`,
`NEW_DRAWING_REVISION_REQUIRED`, `SAMPLE_APPROVAL_PENDING` — all *(proposed)*.

## 7. Edge cases

| ID | Case | Expected | Source | Scenario |
|---|---|---|---|---|
| ECH-EC-01 | ECN effective by unit serial | the new version applies from the order that builds the named unit; selection honours `effective_from_unit_serial` | FR-792 | 776 |
| ECH-EC-02 | Sample rejected, then a new iteration opened | request returns to `IN_DEVELOPMENT` with iteration n+1 | FR-800 | 779 |

## 8. Out of scope

PLM / CAD integration (the import of FR-783 is Excel); drawing viewer markup; dealer-side Form 21 and schemes (`D-20` item 4).

## 9. Amendments

| Date | Change |
|---|---|
| 2026-10-25 | v0 derived from FRD-MFG §6.1 (R32, `D-20`; `R-08` reversed) |

## 10. Invariants and scenarios

`D-10`, MD-46, MD-51; scenarios `WH-SC-772`, `-776`, `-777`, `-778`, `-779`, `-780`.

## 11. Open rows

| ID | Question | Default |
|---|---|---|
| ECH-OPEN-01 | Drawing numbering / revision scheme (PRD Q-S2) | `ALPHA` revisions, user-entered drawing number |
| ECH-OPEN-02 | Must bulk production always wait for sample approval (PRD Q-S5)? | per request `blocks_production`, default `true` from an SO line marked *sample approval required* |
