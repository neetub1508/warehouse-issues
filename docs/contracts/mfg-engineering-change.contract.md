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
| **Workflow** | ECN: draft → items (old → new `DRAFT` versions) → *Compute impacts* → decisions (still `DRAFT`) → submit (impacts recomputed, every row decided, `ECN-` number; approval request `WHM_ECN`) → two-level approval → implement (impacts recomputed under lock; BOM / routing → `APPROVED`, drawing → `RELEASED_FOR_PRODUCTION`; `USE_UP` items activate on depletion). Drawing: upload revision → internal review → released for sample → customer approved → production release (approval request `WHM_DRAWING_RELEASE`) → superseded. Sample: request → submit (`SMR-` number) → sample order (trial BOM) → check → dispatch request (`WHM_SAMPLE_DISPATCH`) → dispatch (stock out of `SAMPLE`) → feedback → next iteration, approved or rejected; the production gate tests the *sample approval required* mark and lifts only on `APPROVED` or an approved waiver |
| **Module** | `warehouse-manufacturing`; ports declared in core by `P10-18` (`DrawingRevisionPort`) and `P10-19` (`SampleRequestPort`), optional beans (MD-51) |
| **Owning tasks** | `issues/p10-17.md` (ECN) · `issues/p10-18.md` (drawings) · `issues/p10-19.md` (samples) |
| **Primary tables** | `whm_ecns`, `whm_ecn_items`, `whm_ecn_impacts` (`V562030`); `whm_drawings`, `whm_drawing_revisions`, `whm_drawing_issues` (`V562040`); `whm_sample_requests`, `whm_sample_iterations` (`V562050`) |
| **Status columns** | ECN `DRAFT`/`SUBMITTED`/`APPROVED`/`IMPLEMENTED`/`REJECTED`/`CANCELLED`; ECN item `activation_status` `PENDING`/`ACTIVE`/`AWAITING_DEPLETION`/`AWAITING_UNIT`; drawing revision `DRAFT`/`INTERNAL_REVIEW`/`RELEASED_FOR_SAMPLE`/`CUSTOMER_APPROVED`/`RELEASED_FOR_PRODUCTION`/`SUPERSEDED`/`REJECTED`; sample request `DRAFT`/`SUBMITTED`/`IN_DEVELOPMENT`/`AWAITING_FEEDBACK`/`APPROVED`/`REJECTED`/`CANCELLED`/`WAIVED` — no `CHECK` (`D-10`) |

## 1. T1 — State machine

### 1.1 Transitions

| ID | From | Event | To | Guard | Actor | Side effects | Source |
|---|---|---|---|---|---|---|---|
| ECH-T1-01 | — | Create ECN; add items (link or create new `DRAFT` versions of `APPROVED` BOMs / routings / released drawings) | `DRAFT` | `ECH-GRD-01` | `whm_ecns:create` / `:edit` | no number yet — the draft shows its id; `ECN-` is assigned at submit (PRD §5 *numbers on approval / posting, never on draft*) | FR-792 |
| ECH-T1-02 | `DRAFT` | Submit | `SUBMITTED` | ≥ 1 item; every new version structurally valid (`BOM-GRD-01`…, `SFL-GRD-03`); impacts recomputed and none new since the last *Compute impacts* (`409 ECN_IMPACTS_CHANGED`); every impact decided (`ECH-GRD-03`); drawing items reviewed (`ECH-GRD-12`) | `whm_ecns:submit` | `ECN-` number assigned (gapless per company, yearly; idempotent on retry); approval request opened (`p8-30`, `WHM_ECN`) — the document is then locked (`DAP-GRD-07`) | FR-792, FR-793 |
| ECH-T1-03 | `DRAFT` | *Compute impacts* (repeatable); record impact decisions | `DRAFT` | decision allowed for the impact type and order state (`ECH-GRD-02`); `USE_UP` names `use_up_until` (`ECH-GRD-16`) | `whm_ecns:edit` | impact rows (re)computed (`ECH-T4-01`), earlier decisions kept on rows that still match; `decided_by/at` | FR-793 |
| ECH-T1-04 | `SUBMITTED` | Last level approves | `APPROVED` | no user on two levels; submitter never approves (`403 ECN_SELF_APPROVAL`); the approver's limit and `excludedActorIds` per the engine (`D-21` item 6) | engine (`whm_ecns:approve`) | — | FR-792 |
| ECH-T1-05 | `SUBMITTED` | Return / Reject | `DRAFT` / `REJECTED` | note required | engine | return: decisions kept, *Compute impacts* required before re-submit; reject: new versions stay `DRAFT` (deleted if never referenced) | FR-792 |
| ECH-T1-06 | `APPROVED` | **Implement** | `IMPLEMENTED` | new versions still valid; the BOM ↔ routing pairing after implement holds (`SFL-GRD-14`); implementer ≠ uploader of any drawing revision in the ECN (`403 DRAWING_SELF_RELEASE`); `UNIT_SERIAL` cut-over per `ECH-GRD-15` | `whm_ecns:implement` | impacts recomputed under lock (`ECH-T4-07`); per object type (`ECH-T4-02`): BOM / routing version → `APPROVED`, drawing revision → `RELEASED_FOR_PRODUCTION` with the prior revision `SUPERSEDED` and its copies listed for recall (`ECH-T4-04`); `DATE` mode: `effective_from_actual` = max(planned `effective_from`, today) — a past planned date never strands the ECN; predecessors end-dated (`BOM-T4-01`); items with a `USE_UP` decision → `AWAITING_DEPLETION` (`ECH-T4-08`), `UNIT_SERIAL` items → `AWAITING_UNIT` (`ECH-EC-01`); impact decisions executed (`ECH-T4-02`) — one transaction | FR-792, FR-793 |
| ECH-T1-07 | `DRAFT` · `SUBMITTED` · `APPROVED` | Cancel | `CANCELLED` | from `APPROVED` a reason is required (`422 REASON_REQUIRED`) | `whm_ecns:cancel` | approval request withdrawn; new versions stay `DRAFT` (deleted if never referenced) | FR-792 |
| ECH-T1-08 | ECN item `AWAITING_DEPLETION` | Old-part quantity of every `USE_UP` impact of the item reaches 0, `use_up_until` passes (`ECH-T3-03`), or *Activate now* | item `ACTIVE` | the new version still valid | scheduler principal / `whm_ecns:implement` | the new version `APPROVED` effective the next day (`DATE`), predecessor end-dated; impacts recomputed for that object and executed with the defaults of `ECH-T4-07` | FR-793 |
| ECH-T1-10 | — | Upload a drawing revision | `DRAFT` | `ECH-GRD-04` | `whm_drawings:create` | file(s) linked as platform documents | FR-795 |
| ECH-T1-11 | `DRAFT` | Submit for review | `INTERNAL_REVIEW` | — | `whm_drawings:submit` | — | FR-795 |
| ECH-T1-12 | `INTERNAL_REVIEW` | Release for sample / Return / Reject | `RELEASED_FOR_SAMPLE` / `DRAFT` / `REJECTED` | actor ≠ uploader (`ECH-GRD-05`) | `whm_drawings:approve` (internal review verb) | `reviewed_by/at` | FR-795 |
| ECH-T1-13 | `RELEASED_FOR_SAMPLE` | Customer approval (sample feedback `APPROVED`, or manual with the customer's document) | `CUSTOMER_APPROVED` | document attached when manual | system / `whm_drawings:approve` | — | FR-795, FR-801 |
| ECH-T1-14 | `INTERNAL_REVIEW` · `CUSTOMER_APPROVED` | *Request production release* → last level approves | `RELEASED_FOR_PRODUCTION` | `ECH-GRD-05`, `ECH-GRD-13`; when a released revision exists, only through an ECN (`FR-794`, implement `ECH-T1-06`) | `whm_drawings:release` opens the request; engine (`WHM_DRAWING_RELEASE`, `SINGLE_LEVEL` default, verb `whm_drawings:release`) approves | the prior released revision → `SUPERSEDED`, its open copies listed for recall (`ECH-T4-04`); `released_by/at` | FR-795, FR-797 |
| ECH-T1-15 | any released revision | Issue a copy | — | controlled copy needs `:print_controlled`; non-released prints watermarked | `whm_drawings:issue` | `whm_drawing_issues` row | FR-797 |
| ECH-T1-20 | — | Create a sample request (manual, or through `SampleRequestPort.open` from trade) | `DRAFT` | `ECH-GRD-06` | `whm_sample_requests:create` / port | source frozen; no number yet | FR-798 |
| ECH-T1-21 | `DRAFT` | Submit | `SUBMITTED` | — | `whm_sample_requests:submit` (the port submits in the same call) | `SMR-` number assigned (gapless per site, idempotent on retry) | FR-798 |
| ECH-T1-22 | `SUBMITTED` | Create sample order (iteration 1) | `IN_DEVELOPMENT` | `ECH-GRD-07` | `whm_sample_requests:create_order` | `SAMPLE` production order on the trial BOM / routing (`PRO-T1-50`); iteration row | FR-799 |
| ECH-T1-23 | `IN_DEVELOPMENT` | Record internal check | `IN_DEVELOPMENT` | checker ≠ the order's supervisor; report attached | `whm_sample_requests:record_check` | `check_result` | FR-800 |
| ECH-T1-24 | `IN_DEVELOPMENT` | *Request dispatch* | `IN_DEVELOPMENT` | latest iteration check `PASS`; sample output received in `SAMPLE` | `whm_sample_requests:dispatch` | approval request `WHM_SAMPLE_DISPATCH` (verb `whm_sample_requests:approve_dispatch`, `SINGLE_LEVEL` — role Sales Manager; with `sample.dispatch_approval_required` = `false` the type resolves zero levels, `DOCUMENT_DEFINED`, the requester as acting user); approver ≠ requester (`ECH-GRD-08`) | FR-800 |
| ECH-T1-25 | `AWAITING_FEEDBACK` | Record feedback | `APPROVED` / `IN_DEVELOPMENT` (with changes) / `REJECTED` | `ECH-GRD-09` | `whm_sample_requests:record_feedback` | `APPROVED` → drawing `CUSTOMER_APPROVED` (`ECH-T1-13`), production gate lifted (`ECH-T4-05`); `REJECTED` keeps the gate closed | FR-800, FR-801 |
| ECH-T1-26 | any open | Cancel | `CANCELLED` | open sample order cancelled first | `whm_sample_requests:cancel` | the gate is **not** lifted — a marked line stays blocked until another request is `APPROVED` or a waiver is approved (`ECH-T4-05`) | FR-798, FR-801 |
| ECH-T1-27 | `IN_DEVELOPMENT` (latest iteration check `FAIL` or feedback `APPROVED_WITH_CHANGES`) · `REJECTED` | *Next iteration* | `IN_DEVELOPMENT` | `ECH-GRD-07`, `ECH-GRD-09`; no open sample order on the request (`409 SAMPLE_ORDER_OPEN`) | `whm_sample_requests:create_order` | iteration n+1 with a new `SAMPLE` order; a `REJECTED` request reopens | FR-799, FR-800 |
| ECH-T1-28 | `IN_DEVELOPMENT` | **Dispatch** | `AWAITING_FEEDBACK` | the `WHM_SAMPLE_DISPATCH` request `APPROVED` (`409 SAMPLE_DISPATCH_NOT_APPROVED`); courier / AWB / date | `whm_sample_requests:dispatch` | gate pass purpose `SAMPLE` (returnable / non) or india challan sourced on the iteration; stock leaves `SAMPLE` (`ECH-T4-09`) | FR-800 |
| ECH-T1-29 | any but `APPROVED` · `WAIVED` | *Request waiver* | unchanged | reason required (`422 REASON_REQUIRED`); no open sample order | `whm_sample_requests:request_waiver` | `waiver_reason`, `waiver_requested_by/at` | FR-801 |
| ECH-T1-30 | waiver requested | *Approve waiver* / *Refuse waiver* | `WAIVED` / unchanged | approver ≠ requester of the waiver (`ECH-GRD-17`) | `whm_sample_requests:approve_waiver` | `WAIVED` lifts the gate for the request's line (`ECH-T4-05`); refusal clears the waiver fields with a note | FR-801 |
| ECH-T1-31 | `AWAITING_FEEDBACK` · `APPROVED` · `REJECTED` (returnable sample) | Sample returned | unchanged | gate entry purpose `SAMPLE_IN` linked to the iteration (`p8-03`) | gate entry / `whm_sample_requests:record_feedback` | non-PO receipt into stock status `SAMPLE`; `returned_on` | FR-800 |
| ECH-T1-32 | `APPROVED` | Retain as golden sample | `APPROVED` | location set; `retain_until` ≥ today | `whm_sample_requests:record_feedback` | `is_golden_sample`, `retain_location_id`, `retain_until` (`ECH-T3-01`) | FR-800 |

### 1.2 Guards

| ID | Predicate | Refusal | Source |
|---|---|---|---|
| ECH-GRD-01 | An item's old version is `APPROVED` (BOM / routing) or `RELEASED_FOR_PRODUCTION` (drawing); one ECN item per old version among live ECNs | `422 ECN_ITEM_INVALID`; `409 ECN_ITEM_IN_OTHER_ECN` | FR-792 |
| ECH-GRD-02 | `RE_EXPLODE` on `PLANNED` / `APPROVED` orders; `RE_EXPLODE_UNSTARTED` only on a `RELEASED` order with nothing posted; `KEEP` / `HOLD` on `RELEASED` / `IN_PROGRESS`; stock decisions only on stock impacts; `KEEP` / `NOTIFY` only on reference impacts (`BOM_REFERENCE`, `ROUTING_REFERENCE`, `OPEN_PO_LINE`) | `422 ECN_DECISION_NOT_ALLOWED` | FR-793 |
| ECH-GRD-03 | Every impact row has a decision | `422 ECN_IMPACT_UNDECIDED` | FR-793 |
| ECH-GRD-04 | Drawing number unique per company; revision code follows the scheme and is new for the drawing; ≥ 1 file | `422 DRAWING_REVISION_INVALID`; `422 DRAWING_FILE_REQUIRED` | FR-795 |
| ECH-GRD-05 | Reviewer / releaser ≠ uploader of the revision | `403 DRAWING_SELF_RELEASE` | FR-795 |
| ECH-GRD-06 | Request has item or specification; quantity > 0; customer set for enquiry / SO sources | `422 SAMPLE_REQUEST_INVALID` | FR-798 |
| ECH-GRD-07 | Drawing revision ≥ `RELEASED_FOR_SAMPLE`; trial BOM / routing only on a `SAMPLE` order | `409 SAMPLE_DRAWING_NOT_RELEASED`; `422 TRIAL_BOM_ONLY_ON_SAMPLE_ORDER` | FR-799 |
| ECH-GRD-08 | Dispatch approver ≠ requester of the dispatch (`WHM_SAMPLE_DISPATCH` request; the engine's `excludedActorIds`) | `403 SAMPLE_DISPATCH_SELF_APPROVAL` | FR-800 |
| ECH-GRD-09 | *Next iteration* after `APPROVED_WITH_CHANGES` needs a drawing revision newer than the last iteration's | `409 NEW_DRAWING_REVISION_REQUIRED` | FR-800 |
| ECH-GRD-10 | **Sample gate.** A demand line is *marked* when `wh_demand_order_lines.sample_approval_required` is `true` (set by trade from the SO line's *sample approval required* tick, defaulted from the customer item reference — item × customer, FR-545; trade fold's half). For a marked line the gate is open only when a sample request with `status IN (APPROVED, WAIVED)` exists whose `source_line_id` is the line — or, raised from an enquiry before the SO, whose item and customer match the line's and whose approved drawing revision is still the item's current production revision. The gate tests the **mark**, not the request: a marked line with no request, or only `REJECTED` / `CANCELLED` / open requests, is closed. Refused while closed: create and release of a `STANDARD` order created from or covering the line (FR-826), output reservation of any order (incl. make-to-stock) to the line (`ECH-T4-10`), and an outbound shipment post of the line (`WhmMovementPostGuard`, MD-35) | `409 SAMPLE_APPROVAL_PENDING` naming the line and the request (or *no sample request raised*) | FR-801 |
| ECH-GRD-11 | *New version* of a released object outside an ECN while `ecn_required_for_released_change` | `409 ECN_REQUIRED`; approving it directly `409 VERSION_GOVERNED_BY_ECN` | FR-794 |
| ECH-GRD-12 | Submit of an ECN with a `DRAWING` item: the new revision has passed internal review by someone other than its uploader (`RELEASED_FOR_SAMPLE` or `CUSTOMER_APPROVED`), and `CUSTOMER_APPROVED` when `ECH-GRD-13` applies | `422 ECN_DRAWING_NOT_REVIEWED`; `409 DRAWING_CUSTOMER_APPROVAL_REQUIRED` | FR-794, FR-795 |
| ECH-GRD-13 | Production release of a revision of a `CUSTOMER` drawing, or of a drawing whose item has a marked demand line or a `blocks_production` sample request that is not `APPROVED` / `WAIVED`, needs `CUSTOMER_APPROVED` first | `409 DRAWING_CUSTOMER_APPROVAL_REQUIRED` | FR-795, FR-801 |
| ECH-GRD-14 | ECN items' new BOM and routing versions keep the pairing rule after implement (`SFL-GRD-14`) | `422 BOM_OPERATION_NOT_IN_ROUTING` naming BOM, line, seq | FR-791 |
| ECH-GRD-15 | `UNIT_SERIAL` effectivity: the item has a unit-serial series (FR-811) and the cut-over serial belongs to it; an order whose reserved serial range (reserved at release, FR-811) contains the cut-over serial anywhere but at its first unit is refused at release with a split proposal | `422 ECN_UNIT_SERIAL_INVALID`; `409 ORDER_SPANS_ECN_CUTOVER` (names the split quantity) | FR-792, FR-811 |
| ECH-GRD-16 | `USE_UP` names `use_up_until` (DATE, ≥ the ECN's effective date) — the latest date the old version may stay effective | `422 USE_UP_UNTIL_REQUIRED` | FR-793 |
| ECH-GRD-17 | Waiver approver ≠ waiver requester | `403 SAMPLE_WAIVER_SELF_APPROVAL` | FR-801 |

### 1.3 Unreachable

| ID | Never happens | Why | Source |
|---|---|---|---|
| ECH-UNR-01 | A released drawing revision edited | revisions are immutable; a change is a new revision | FR-795 |
| ECH-UNR-02 | An SO line refused for want of sample approval | the gate is on production, reservation and shipment (`ECH-GRD-10`), never the SO line | FR-801 |
| ECH-UNR-03 | Two `RELEASED_FOR_PRODUCTION` revisions of one drawing | partial unique index | FR-795 |
| ECH-UNR-04 | The gate lifted by a `REJECTED` or `CANCELLED` request | only `APPROVED` or an approved waiver lifts it (`ECH-T4-05`, `D-21` item 8) | FR-801 |
| ECH-UNR-05 | A new version of an ECN approved by its own approval request outside implement | `ECH-GRD-11`; implement is the only path (`ECH-T1-06`, `-08`) | FR-794 |

## 2. T2 — Action × role × state

| ID | Action | Permission | Persona | Source |
|---|---|---|---|---|
| ECH-T2-01 | Create / submit ECN | `whm_ecns:create/edit/submit` | design engineer | FR-792 |
| ECH-T2-02 | Approve ECN levels | engine levels, verb `whm_ecns:approve` | Design Head, Plant Head | FR-792 |
| ECH-T2-03 | Implement ECN | `whm_ecns:implement` | production engineer / planner | FR-792 |
| ECH-T2-04 | Upload / internal review / production release of drawings | `whm_drawings:create` / `:approve` (internal review) / `:release` (request + engine level of `WHM_DRAWING_RELEASE`) | design engineer / Design Head | FR-795 |
| ECH-T2-05 | Sample request, order, check, dispatch, feedback, waiver | `whm_sample_requests:*`; `:approve_dispatch` (engine level of `WHM_SAMPLE_DISPATCH`) Sales Manager; `:approve_waiver` Sales Manager / Plant Head | sales, R&D, QC | FR-798…FR-801 |

## 3. T3 — Time-driven rules

| ID | Trigger | Effect | Source |
|---|---|---|---|
| ECH-T3-01 | Golden sample `retain_until` passes | alert to the sample owner; nothing auto-disposed | FR-800 |
| ECH-T3-02 | Returnable sample past the gate pass expected return | core gate-pass overdue alert, sourced on the iteration | FR-800 |
| ECH-T3-03 | Nightly ECN depletion job (scheduler principal) | for each item `AWAITING_DEPLETION`: recompute the old-part quantity of its `USE_UP` impacts (on hand in every bucket of `ECH-T4-01`) into `use_up_remaining_quantity`; at 0, or once `use_up_until` passes, activate (`ECH-T1-08`); one alert to the ECN owner per activation | FR-793 |

## 4. T4 — Cross-entity effects

| ID | Cause | Effect | Source |
|---|---|---|---|
| ECH-T4-01 | *Compute impacts* / submit / implement | impact rows: open production orders (`PLANNED`, `APPROVED`, `RELEASED`, `IN_PROGRESS`) whose frozen `bom_id`, `base_bom_id` (a variant order exploded from a `BASE` BOM, FR-781), `routing_id` or drawing revision is an old version; open purchase demand for removed components; **reference impacts** for a `DRAWING` item — every BOM and routing whose drawing link is the old revision (`BOM_REFERENCE`, `ROUTING_REFERENCE`) and every open PO / RFQ line carrying the old revision (`OPEN_PO_LINE`, read through the core purchase demand port); old-part **stock** per site and bucket — allocatable, `QC_HOLD`, `SAMPLE`, at job workers (subcontract stock) and issued-to-order WIP (`stock_bucket`) | FR-793 |
| ECH-T4-02 | ECN implemented | per object type: BOM / routing → `APPROVED`; drawing → `RELEASED_FOR_PRODUCTION` + supersession (`ECH-T4-04`); decisions: `RE_EXPLODE` / `RE_EXPLODE_UNSTARTED` re-snapshot orders (the `PRO-T1-07` re-explode path, allowed by the ECN for a `RELEASED` order with nothing posted — `PRO-T1-45`); `HOLD` sets the hold with `ENGINEERING_CHANGE`; `REWORK` creates a `PLANNED` rework order; `SCRAP` a core scrap adjustment request; `RETURN_TO_VENDOR` a core supplier-return draft; `USE_UP` defers the item (`ECH-T4-08`); `NOTIFY` lists the reference for its owner (buyer / engineer); result ids recorded | FR-793 |
| ECH-T4-03 | Mass replace from where-used (`BOM-T1-20`) | one `DRAFT` ECN with a new `DRAFT` version per selected BOM | FR-783, FR-792 |
| ECH-T4-04 | Drawing revision superseded | open copies in `whm_drawing_issues` listed for recall; frozen BOM / order references flagged superseded on WS-320 / WS-324 | FR-796, FR-797 |
| ECH-T4-05 | Sample request `APPROVED`, or waiver approved (`WAIVED`) | `ECH-GRD-10` opens for the request's line (or the matching item × customer); a request `REJECTED` or `CANCELLED` changes nothing | FR-801 |
| ECH-T4-06 | `DrawingRevisionPort.currentReleased(itemId)` called by trade / core | returns drawing no., revision, document id of the current released revision | FR-796 |
| ECH-T4-07 | Implement (and `ECH-T1-08` activation) | impacts recomputed under the ECN row lock; a row that did not exist at submit (an order created or released during approval) is added with the default for its state — `PLANNED` / `APPROVED` → `RE_EXPLODE`, `RELEASED` / `IN_PROGRESS` → `HOLD`, stock → `NONE`, reference → `NOTIFY` — `decision_source = IMPLEMENT_DEFAULT`, `decided_by` = the implementer, listed in the implement log; while an ECN is `SUBMITTED` / `APPROVED`, order create / release on its old version shows *version under ECN-…* (warning, not a refusal) | FR-793 |
| ECH-T4-08 | Item with a `USE_UP` impact implemented | the old version stays effective, the new version stays `DRAFT` governed by the ECN, item `AWAITING_DEPLETION`, `use_up_remaining_quantity` tracked; activation by `ECH-T3-03` / `ECH-T1-08` | FR-793 |
| ECH-T4-09 | Sample dispatched (`ECH-T1-28`) | non-chargeable: a core store issue out of stock status `SAMPLE` at the sample store (cost object `SAMPLE_REQUEST`, ref = iteration) in the dispatch transaction — its value lands in the sample cost register (FR-799); chargeable: a core outbound shipment of the iteration from `SAMPLE` (the only pick ever allowed from `SAMPLE`), so core emits the one shipment-level `INVOICE_REQUEST` (`D-21` item 2) priced by trade's enrichment SPI for an SO-sourced request, else at the request's `charge_amount`; a return (`ECH-T1-31`) receives back into `SAMPLE` | FR-800 |
| ECH-T4-10 | Output reservation of any order to a demand line (FR-637, FR-826), and `create_order_from_demand_line` for a marked line | refused while `ECH-GRD-10` is closed (`409 SAMPLE_APPROVAL_PENDING`); auto-create creates no order, raises one alert to the planner naming the line, and retries when `ECH-T4-05` opens the gate | FR-801, FR-826 |

## 5. T5 — Screen contract

| ID | Screen | Contents | Source |
|---|---|---|---|
| ECH-T5-01 | WS-384 ECNs | Service Vehicle; row actions Compute impacts · Submit · Implement · Activate now · Cancel; tabs Items (with `activation_status`) · Impact (decisions inline while `DRAFT`) · Approval (engine steps, append-only) · Implement log (incl. `IMPLEMENT_DEFAULT` rows) | FR-792, FR-793 |
| ECH-T5-02 | WS-385 Drawings | Service Vehicle; tabs Revisions · Files (platform document viewer) · Issue log · Where used; print shows the watermark on non-released revisions | FR-795…FR-797 |
| ECH-T5-03 | WS-386 Sample Requests | Service Vehicle; tabs Iterations · Orders · Dispatch (engine steps of `WHM_SAMPLE_DISPATCH`) · Feedback · Waiver; row actions Submit · Create order · Next iteration · Record check · Request dispatch · Dispatch · Record feedback · Request / Approve waiver · Cancel; dates `formatDateSync` | FR-798…FR-801 |

## 6. Error codes

`ECN_ITEM_INVALID`, `ECN_ITEM_IN_OTHER_ECN`, `ECN_DECISION_NOT_ALLOWED`, `ECN_IMPACT_UNDECIDED`, `ECN_SELF_APPROVAL`,
`ECN_REQUIRED`, `VERSION_GOVERNED_BY_ECN`, `DRAWING_REVISION_INVALID`, `DRAWING_FILE_REQUIRED`, `DRAWING_SELF_RELEASE`,
`SAMPLE_REQUEST_INVALID`, `SAMPLE_DRAWING_NOT_RELEASED`, `TRIAL_BOM_ONLY_ON_SAMPLE_ORDER`, `SAMPLE_DISPATCH_SELF_APPROVAL`,
`NEW_DRAWING_REVISION_REQUIRED`, `SAMPLE_APPROVAL_PENDING`, `ECN_IMPACTS_CHANGED`, `ECN_DRAWING_NOT_REVIEWED`,
`DRAWING_CUSTOMER_APPROVAL_REQUIRED`, `ECN_UNIT_SERIAL_INVALID`, `ORDER_SPANS_ECN_CUTOVER`, `USE_UP_UNTIL_REQUIRED`,
`SAMPLE_ORDER_OPEN`, `SAMPLE_DISPATCH_NOT_APPROVED`, `SAMPLE_WAIVER_SELF_APPROVAL` — all *(proposed)*.

## 7. Edge cases

| ID | Case | Expected | Source | Scenario |
|---|---|---|---|---|
| ECH-EC-01 | ECN effective by unit serial | the cut-over serial's order is identified at release: serials are reserved at release in series order (FR-811); an order whose range starts at or after the cut-over serial gets the new version, which is then approved effective that day and the predecessor end-dated (item `AWAITING_UNIT` → `ACTIVE`); an order straddling the cut-over is refused `409 ORDER_SPANS_ECN_CUTOVER` with the split quantity | FR-792, FR-811 | 776 |
| ECH-EC-02 | Sample rejected, then a new iteration opened | *Next iteration* (`ECH-T1-27`) returns the request to `IN_DEVELOPMENT` with iteration n+1; the gate stayed closed while `REJECTED` | FR-800 | 779 |
| ECH-EC-03 | ECN approved after its planned effective date | implement uses today (`effective_from_actual`); or cancel from `APPROVED` with a reason | FR-792 | 776 |
| ECH-EC-04 | Order created on the old BOM while the ECN awaits approval | warning at create; at implement the order gets an `IMPLEMENT_DEFAULT` impact row (`RE_EXPLODE` while `PLANNED`) | FR-793 | 777 |
| ECH-EC-05 | Customer cancels the sample request on a marked SO line | the line stays blocked; production needs another approved request or an approved waiver | FR-801 | 780 |

## 8. Out of scope

PLM / CAD integration (the import of FR-783 is Excel); drawing viewer markup; dealer-side Form 21 and schemes (`D-20` item 4).

## 9. Amendments

| Date | Change |
|---|---|
| 2026-10-25 | v0 derived from FRD-MFG §6.1 (R32, `D-20`; `R-08` reversed) |
| 2026-10-25 | R32 fix wave (`R32-functional-review-mfg-eng.md`, `D-21` items 6, 8): sample gate tests the mark and lifts only on `APPROVED` / approved waiver (`WAIVED`), extended to reservation, auto-create and shipment (F-R32ME-001, -002); *Next iteration*, dispatch request, return, golden sample rows (F-003, -028); ECN decisions before submit, impacts recomputed at implement with defaults, wider impact scope, `USE_UP` deferred activation, past-date implement and cancel from `APPROVED` (F-004, -012, -013, -014); per-object implement targets and reviewed drawings (F-005, -020); engine types `WHM_ECN`, `WHM_DRAWING_RELEASE`, `WHM_SAMPLE_DISPATCH`, no single-checker fallback (F-006, -007); unit-serial cut-over at release (F-011); numbers at submit (F-032) |

## 10. Invariants and scenarios

`D-10`, MD-46, MD-51; scenarios `WH-SC-772`, `-776`, `-777`, `-778`, `-779`, `-780`.

## 11. Open rows

| ID | Question | Default |
|---|---|---|
| ECH-OPEN-01 | Drawing numbering / revision scheme (PRD Q-S2) | `ALPHA` revisions, user-entered drawing number |
| ECH-OPEN-02 | Must bulk production always wait for sample approval (PRD Q-S5)? | the gate tests the line's *sample approval required* mark (default from the customer item reference); lifted only by `APPROVED` or an approved waiver (`D-21` item 8); `blocks_production` on the request defaults from the mark |
