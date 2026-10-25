# Functional conformance — R32 manufacturing engineering (`r32-mfg-eng`)
Contract: `docs/contracts/mfg-engineering-change.contract.md` (v0), `mfg-shop-floor` (v0), `mfg-bom` §12, `mfg-material-staging-issue` §12, `mfg-mrp` §12 | Mode: audit (pre-build, design set `warehouse-issues` @ a244ff6)
Files reviewed: 30 (p10-01…06 R32 sections, p10-15…19, p10-25, p10-26; FRD-MFG §6.1/§8/§9; DATA-MODEL §2.7.10; DECISIONS D-20; the 5 contracts plus `document-approval`, `store-issue-return`; p8-03/09/18/30; PRD; MRB/AMN gap reports; mfg, approvals and core ledgers) | File set: derived from workflow
Engines: Claude + GPT (gpt-6.1-sol, medium) — 10 both · 15 Claude only · 8 GPT only · 0 dropped

All paths are relative to `/Users/bbhushan/work/git/workspace/warehouse-issues` unless they start with `/`.

## Verdict
33 findings (18 High, 11 Medium, 4 Low). This is not ready to build. Three areas break: the sample lifecycle and its gate, the ECN implement/impact model, and variant ↔ routing selection.

## Status reachability
| Status set | In contract T1 | Inbound | Outbound | Verdict |
|---|---|---|---|---|
| ECN DRAFT/SUBMITTED/APPROVED/IMPLEMENTED/REJECTED/CANCELLED | yes | ECH-T1-01…07 | APPROVED → IMPLEMENTED only if effectivity ≥ today | APPROVED is a dead end once its date passes (F-004) |
| Drawing rev DRAFT…RELEASED_FOR_PRODUCTION/SUPERSEDED/REJECTED | yes | ECH-T1-10…14 | manual supersede has no row | `:supersede` permission orphaned (F-028) |
| Sample DRAFT…AWAITING_FEEDBACK | yes | T1-20…24 | ok | — |
| Sample IN_DEVELOPMENT (after changes / check FAIL), REJECTED (reopen) | partial | T1-25 | no next-order path | dead end (F-003) |
| Routing DRAFT/SUBMITTED/APPROVED/OBSOLETE | partial | SFL-T1-04…07 | no OBSOLETE / return / reject rows | F-028 |
| Maintenance CANCELLED | no | none | — | unreachable (F-023) |
| Tool AT_JOB_WORKER | no T1 row | — | — | F-028 |
| Machine BREAKDOWN | only on order *Start* | SFL-T1-43 | — | F-022 |

## Findings

### F-R32ME-001 — High: a rejected or cancelled sample lifts the production gate
- **Contract row:** ECH-GRD-10, ECH-T4-05, ECH-T1-26 · **Source:** Both
- **Evidence:**
  - `docs/contracts/mfg-engineering-change.contract.md:69`: the gate tests for an *open* blocking request.
  - `:105` and `:54`: CANCELLED explicitly lifts the gate.
  - `docs/frd/FRD-MFG.md:470`: REJECTED closes the request, so it is no longer "open".
  - PRD `docs/reference/PRD-…txt:308`: production is allowed only once the sample is customer-approved.
- **What a user experiences:** Sales cancels the request, or the customer rejects the sample, and the STANDARD order releases on an unapproved part.
- **Fix:** Lift the gate only on `APPROVED`. Make anything else an explicit waiver (permission + reason + approver). Rejection and cancellation keep the block.

### F-R32ME-002 — High: no request means no block, and orders without a demand link bypass the gate
- **Contract row:** ECH-GRD-10, ECH-OPEN-02 · **Source:** Claude
- **Evidence:**
  - `issues/p10-19.md:9`: `requires_part_approval` is moved off the SO line.
  - `docs/frd/FRD-MFG.md:468`: `blocks_production` lives only on the request.
  - `docs/frd/FRD-MFG.md:471`: the gate applies only to orders created from, or covering, the SO line.
- **What a user experiences:**
  - An SO line that needs a sample, but has no request raised yet, can get a production order.
  - A make-to-stock order for the same item builds stock that is then allocated to that line.
- **Fix:**
  - Keep the "sample approval required" mark (on the SO line or an item × customer flag) and test the mark, not the request.
  - Extend the gate to allocating MTS output to a marked line.
  - Specify what `create_order_from_demand_line` (FR-826) does when refused.

### F-R32ME-003 — High: sample iterations dead-end
- **Contract row:** ECH-T1-22, -24, -25, EC-02 · **Source:** Both
- **Evidence:**
  - `mfg-engineering-change.contract.md:50`: the next order can only be created from SUBMITTED or AWAITING_FEEDBACK.
  - `:53`: feedback "with changes" goes to IN_DEVELOPMENT, and rejection goes to REJECTED.
  - `:128`: a rejected request must still be able to reopen.
  - `:52`: when the internal check FAILs there is no outbound path.
- **What a user experiences:** The iteration n+1 sample order can't be created after changes, a failed check or a rejection.
- **Fix:**
  - Add a "Next iteration" transition from IN_DEVELOPMENT (changes / check FAIL) and from REJECTED, guarded by ECH-GRD-09.
  - Reconcile with FR-800 at `docs/frd/FRD-MFG.md:470`.

### F-R32ME-004 — High: an APPROVED ECN can be neither implemented nor cancelled once its date passes
- **Contract row:** ECH-T1-06, -07 · **Source:** Claude
- **Evidence:** `mfg-engineering-change.contract.md:40` requires effectivity ≥ today; `:41` allows cancel only from DRAFT/SUBMITTED.
- **What a user experiences:** Approval takes longer than the planned effective date and the ECN is stuck forever.
- **Fix:** Allow re-dating with re-approval, or implement with effectivity = today, or cancel from APPROVED with a reason.

### F-R32ME-005 — High: ECN implement sets drawings to `APPROVED` and bypasses drawing release control
- **Contract row:** ECH-T1-02, ECH-T1-06 · **Source:** Both
- **Evidence:**
  - `mfg-engineering-change.contract.md:40`: "every new version `APPROVED`".
  - `:27`: drawing revisions have no `APPROVED` status.
  - `:36`: the submit guard validates only BOM/routing structure.
  - `:46`: drawing release otherwise runs through ECH-GRD-05 and copy recall.
  - PRD `:299`: only `drawing:approve` releases, never the uploader.
- **What a user experiences:** A DRAFT drawing revision, never internally reviewed, reaches production through an implementer who may be the uploader.
- **Fix:**
  - Give each object type its own implement target: drawing → `RELEASED_FOR_PRODUCTION`, with supersession and recall.
  - Require the ECN's drawing revision to have passed INTERNAL_REVIEW by someone other than the uploader before submit.

### F-R32ME-006 — High (approval weaker than contract): the single-checker fallback silently cuts two levels to one
- **Contract row:** SFL-T1-06, ECH-T1-04, BOM-T1-21 · **Source:** Both
- **Evidence:**
  - `issues/p10-16.md:66` and `issues/p10-17.md:62`: a single checker applies until p8-30 ships.
  - `docs/frd/FRD-MFG.md:596,599`: the default is 2 levels.
- **What a user experiences:** Plant Head approval disappears, depending on build order.
- **Fix:** Make p8-30 a hard blocker for p10-03, p10-16 and p10-17, or refuse `approval_levels > 1` until the engine is present.

### F-R32ME-007 — High: drawing release, sample dispatch, order approval and shortage release bypass the one approval engine
- **Contract row:** ECH-T1-12/-14, ECH-GRD-08, PRO-T1-40, FR-825 · **Source:** Claude
- **Evidence:**
  - `issues/p8-30.md:34`: P10 is expected to wire "production order release, PDI clearance, drawing release, sample dispatch, deviation" as engine document types.
  - FRD-MFG wires only `WHM_BOM`, `WHM_ROUTING` and `WHM_ECN` (`:452`, `:462`).
  - `:495`, `:470` and `:494` use bespoke permission checks instead.
  - D-20 item 18 (`docs/DECISIONS.md:705`) says one engine for every document type.
  - The approvals ledger rows 3-36 and 3-39 say "mfg slice", so neither side delivers this.
- **What a user experiences:** These approvals have no configurable levels, no append-only steps and no escalation.
- **Fix:** Register `WHM_DRAWING_RELEASE`, `WHM_SAMPLE_DISPATCH`, `WHM_PRODUCTION_ORDER` and `WHM_SHORTAGE_RELEASE` types with matching approve verbs.

### F-R32ME-008 — High: the `SAMPLE` order type has no owner, and trial versions contradict the release guards
- **Contract row:** ECH-GRD-07/-10, FR-799, FR-791 · **Source:** Both
- **Evidence:**
  - `issues/p10-19.md:9,21,23` assigns the order type, the create/release gate and `is_trial` to p10-05 and p10-03.
  - A grep of p10-05, p10-03, p10-06, p10-08, p10-09 and `mfg-production-order.contract.md` finds no `SAMPLE`, trial or `SAMPLE_APPROVAL_PENDING` row.
  - `FRD-MFG.md:461` refuses release without an approved routing, while `:469` allows a trial routing.
  - The general release guards at `mfg-production-order.contract.md:112` and `mfg-shop-floor.contract.md:70` say the same.
- **What a user experiences:** Sample orders on trial versions are refused at release. The gate, receipt into `SAMPLE` status and the separate sample cost pool are not built anywhere.
- **Fix:**
  - Add R32 rows to p10-05: order type, trial exception at release, ECH-GRD-10.
  - p10-03: the `is_trial` column.
  - p10-08: receipt into `SAMPLE` status and the sample-store location.
  - p10-09: the sample cost pool.
  - Give `WhmRoutingSelectionService` a trial-routing path.

### F-R32ME-009 — High (missing UI entry point): no screen for variant mapping, applicability or the BOM engineering tools
- **Contract row:** BOM-GRD-31, BOM-T1-22…24 · **Source:** GPT
- **Evidence:**
  - `issues/p10-03.md:77,79` add the variant tables and import/compare/mass-replace.
  - `issues/p10-03.md:72` and `docs/contracts/mfg-bom.contract.md:172-173`: the actions, toolbar and Components editor include none of them.
- **What a user experiences:** Base-BOM selection depends on data no user can enter.
- **Fix:** Add a variants tab (model ↔ variant), per-line applicability in the Components editor, and Import / Compare / Mass replace actions with permission gates to T5.

### F-R32ME-010 — High: dispatching a sample moves no stock, and chargeable samples are never billed
- **Contract row:** ECH-T1-24 · **Source:** Claude
- **Evidence:**
  - `mfg-engineering-change.contract.md:52`: dispatch goes out on a gate pass.
  - `issues/p8-03.md:49`: "a gate pass never posts a movement".
  - `FRD-MFG.md:469`: sample stock is held in `SAMPLE` status.
  - `FRD-MFG.md:468`: `is_chargeable`, with no dispatch → invoice hand-off.
- **What a user experiences:** A dispatched non-returnable sample stays on hand for ever. A chargeable sample never reaches invoicing.
- **Fix:**
  - Post an issue out of `SAMPLE` at dispatch (and a receipt on return through gate entry).
  - Route chargeable samples through the dispatch → invoice hand-off.

### F-R32ME-011 — High: unit-serial effectivity is selected before the serial exists
- **Contract row:** ECH-EC-01, FR-792 · **Source:** Both
- **Evidence:**
  - `FRD-MFG.md:462`: effective_from = "date the named unit is assigned".
  - `:608` and `:481`: serials are assigned at the first stage by default.
  - BOM/routing snapshots are taken at release (`mfg-production-order.contract.md:309`).
  - `mfg-engineering-change.contract.md:127`.
- **What a user experiences:**
  - Implement can't set a date.
  - Release can't evaluate the serial.
  - An order whose batches straddle the cut-over has no rule.
- **Fix:**
  - Require `assign_at = RELEASE`, or reserve the serial range at release, for items with UNIT_SERIAL ECNs.
  - Define serial ordering.
  - Split or refuse orders that span the cut-over.

### F-R32ME-012 — High: ECN impact decisions are recorded while the approval engine locks the document
- **Contract row:** ECH-T1-02…04 vs DAP-GRD-07 · **Source:** GPT
- **Evidence:**
  - `mfg-engineering-change.contract.md:36`: submit opens the approval request.
  - `:37`: decisions are edited in SUBMITTED.
  - `docs/contracts/document-approval.contract.md:103`: `409 APPROVAL_PENDING` while a request is pending.
- **What a user experiences:** The decisions needed for approval can't be saved.
- **Fix:** Compute impacts, take the decisions, then open the approval request (or define a decision phase before the engine request). Any later change re-opens approval.

### F-R32ME-013 — High: ECN impacts are frozen at submit and miss orders, variants, drawings and stock
- **Contract row:** ECH-T4-01, FR-793 · **Source:** Both
- **Evidence:**
  - `mfg-engineering-change.contract.md:101`: impacts are computed at submit only.
  - `:40`: implement re-checks validity only (plus `ORDER_HAS_POSTINGS`, `issues/p10-17.md:50`).
  - `FRD-MFG.md:463`: states PLANNED/RELEASED/IN_PROGRESS only, but `mfg-production-order.contract.md:301` adds APPROVED. MRP capacity load (`mfg-mrp.contract.md:209`) also omits APPROVED.
  - Variant orders link through `base_bom_id` (`FRD-MFG.md:451`), and no matching rule is given.
  - A DRAWING item has no orders or stock to match, so a drawing-only ECN computes no impacts at all.
  - Stock covers "allocatable + QC_HOLD" only, not stock at job workers, issued WIP or `SAMPLE`.
  - Open POs carrying the old drawing revision are not listed.
- **What a user experiences:** Orders created during approval, and every variant order, build the old design without being flagged.
- **Fix:**
  - Recompute impacts at implement, or block new orders on an old version that is under a live ECN.
  - Add APPROVED orders, `base_bom_id` matching, a drawing where-used impact (BOMs, routings, open POs) and the missing stock locations.
  - Add APPROVED to the capacity load.

### F-R32ME-014 — High: `USE_UP` has no mechanism behind it
- **Contract row:** ECH-T4-02 · **Source:** GPT
- **Evidence:**
  - `FRD-MFG.md:463`: "consume first; new version effective after".
  - `mfg-engineering-change.contract.md:40`: versions are approved immediately.
  - `:102`: no USE_UP effect is defined.
  - `DATA-MODEL.md` `whm_ecn_impacts`: no depletion field.
- **What a user experiences:** Choosing USE_UP changes nothing.
- **Fix:** Define deferred activation on depletion (a T3 job or a trigger on consumption) and track the remaining old-part quantity.

### F-R32ME-015 — High: routing selection has no fallback from variant to model
- **Contract row:** SFL-GRD-04/-05, FR-790/791 · **Source:** Claude
- **Evidence:**
  - `FRD-MFG.md:451`: variant BOM falls back to the model's BASE BOM.
  - `:460-461` and `issues/p10-16.md:24`: routing is selected strictly by `item_id`.
  - `mfg-shop-floor.contract.md` mentions no model or variant.
- **What a user experiences:** All 31 variants each need their own routing, or release fails with `409 ROUTING_NOT_EFFECTIVE`. That defeats the point of D-20 item 2 together with item 17.
- **Fix:** Fall back from the variant item to the model's routing, and let ECNs and the cost estimate use the same fallback.

### F-R32ME-016 — High: the routing ↔ BOM revision tie is display-only
- **Contract row:** SFL-GRD-03/05, BOM-GRD-30 · **Source:** Both
- **Evidence:**
  - PRD `:221`: "a routing revision is tied to a BOM revision".
  - `FRD-MFG.md:460`: `bom_id` is nullable and display-only.
  - `:461`: `BOM_OPERATION_NOT_IN_ROUTING` is checked only at release.
- **What a user experiences:** Incompatible BOM and routing versions are both approved, and every order then fails at release.
- **Fix:** Validate the combination at BOM/routing approval and at ECN implement, not only at release.

### F-R32ME-017 — High: BOM-GRD-08 contradicts separate routings
- **Contract row:** BOM-GRD-08 vs FR-791 · **Source:** GPT
- **Evidence:** `mfg-bom.contract.md:96` requires a line's `operation_seq` to name an operation of the same BOM, while `FRD-MFG.md:461` checks it against the routing.
- **What a user experiences:** Engineers must duplicate routing stages inside the BOM.
- **Fix:** Split the guard: BOM operations for BOM-only shops, the effective routing for items with job cards.

### F-R32ME-018 — High: the stage-backflush posting trigger is specified two ways
- **Contract row:** SFL-T4-02 · **Source:** GPT
- **Evidence:** `issues/p10-20.md:25` and `mfg-shop-floor.contract.md:114` post on booking. `FRD-MFG.md:476` posts on completion, or on booking only with partial transfer.
- **What a user experiences:** Stock is consumed twice or at the wrong time, and the cancel/reversal logic diverges.
- **Fix:** Choose one trigger and align the FRD, the contract and the task.

### F-R32ME-019 — Medium: the MFG half of the over-BOM issue escalation has no owner
- **Contract row:** none (MRB C6, 7.1-17) · **Source:** Claude
- **Evidence:**
  - `issues/p8-09.md:92`: escalation depends on MFG returning required − issued + returned from `standardBalanceFor`.
  - The hook appears in no MFG file (grep hits only `FRD-STORES.md` and `p8-09.md`).
  - MRB C6 is in no ledger.
- **What a user experiences:** The default is empty, so a production MR over the BOM never needs the higher approval the PRD requires (`PRD:194`).
- **Fix:** Add the hook implementation to p10-06 R32 and to `mfg-material-staging-issue` §12.

### F-R32ME-020 — Medium: a customer drawing can reach production without customer approval
- **Contract row:** ECH-T1-14 · **Source:** Claude
- **Evidence:** `mfg-engineering-change.contract.md:46` allows INTERNAL_REVIEW → RELEASED_FOR_PRODUCTION directly. PRD `:87` and `:298` put customer approval in the path for SO samples.
- **What a user experiences:** A `drawing_type = CUSTOMER` revision skips `CUSTOMER_APPROVED`.
- **Fix:** Require CUSTOMER_APPROVED before production release when the drawing type is CUSTOMER or a blocking sample request exists.

### F-R32ME-021 — Medium: variant resolution is unguarded and MRP has no variant row
- **Contract row:** BOM-T1-20, MRP §12 · **Source:** Claude
- **Evidence:** `FRD-MFG.md:451` ("no row = all") has no completeness or exclusivity check. `mfg-mrp.contract.md:270` has batch rounding only.
- **What a user experiences:**
  - A variant can get both battery lines, or neither.
  - Whether MRP explodes variant demand through the BASE BOM is unverified.
- **Fix:**
  - Add an exclusive-group guard (and a validation report) for each variant.
  - Add an MRP §12 row for selecting the BASE BOM for variant demand.

### F-R32ME-022 — Medium: a broken machine stays bookable until its repair starts
- **Contract row:** SFL-T1-42/43 · **Source:** Claude
- **Evidence:** `mfg-shop-floor.contract.md:58-59` sets BREAKDOWN only on *Start*.
- **What a user experiences:** Jobs keep being booked on a broken machine while its breakdown order is OPEN.
- **Fix:** Set machine → BREAKDOWN when a breakdown order is created.

### F-R32ME-023 — Medium: maintenance CANCELLED is unreachable
- **Contract row:** SFL-T1-42…44 · **Source:** Both
- **Evidence:** `mfg-shop-floor.contract.md:28` lists the status and `issues/p10-26.md:33` grants `:cancel`, but the T1 rows at `:58-60` never reach it.
- **What a user experiences:** Cancel is offered with no defined effect.
- **Fix:** Add the cancel row: allowed states, a reason, and restoring the machine/tool status and the plan.

### F-R32ME-024 — Medium: planned PM minutes are not modelled
- **Contract row:** SFL-T4-04 · **Source:** GPT
- **Evidence:** `issues/p10-26.md:21` promises the deduction, but `DATA-MODEL.md:2227-2228` has no planned duration or window.
- **What a user experiences:** Future PM does not reduce capacity.
- **Fix:** Add a planned start and duration to orders/plans, and define the deduction so it does not count twice.

### F-R32ME-025 — Medium: a booking records only one tool
- **Contract row:** SFL-GRD-10, SFL-T4-05 · **Source:** GPT
- **Evidence:** `issues/p10-26.md:17` adds a scalar `tool_id`, while `mfg-shop-floor.contract.md:75` checks "each required tool".
- **What a user experiences:** An operation that needs a die and a fixture can't record both.
- **Fix:** Add booking ↔ tool child rows.

### F-R32ME-026 — Medium: the frozen estimate stores only totals
- **Contract row:** CST-T1-20 · **Source:** GPT
- **Evidence:** `issues/p10-25.md:22,29` promise a frozen breakdown, but `DATA-MODEL.md` `whm_cost_estimates` holds totals only.
- **What a user experiences:** The breakdown view can't be reproduced later.
- **Fix:** Add detail rows: line, revision ids, rate, cost source, missing flag.

### F-R32ME-027 — Medium: the cost estimate can't cost custom items
- **Contract row:** FR-831 · **Source:** Claude
- **Evidence:** `issues/p10-25.md:52` returns `422 BOM_NOT_FOUND` without an approved BOM. PRD `:143-144` asks for costing of custom/non-standard enquiries, using BOM × last purchase rate.
- **What a user experiences:** The enquiries that most need pre-sale costing get no estimate.
- **Fix:** Allow a DRAFT/trial BOM and routing, flagged on the estimate. Add a `LAST_PURCHASE` cost-basis option (D-20 rule 1).

### F-R32ME-028 — Medium: permissions and statuses with no transition
- **Contract row:** ECH-T1, SFL-T1 · **Source:** Claude
- **Evidence:**
  - `whm_sample_requests:approve_dispatch` and `:close` (`issues/p10-19.md:34`) have no T1 row; there is also no golden-sample or return row.
  - `whm_drawings:supersede` (`issues/p10-18.md:34`) has no row.
  - `whm_routings:obsolete` and the routing return/reject from FR-782 (`issues/p10-16.md:38`) have no row.
  - Tool `AT_JOB_WORKER` (`FRD-MFG.md:502`) has no row.
- **What a user experiences:** Buttons with no defined behaviour.
- **Fix:** Add a T1 row for each, or remove the verb.

### F-R32ME-029 — Medium: the ledger claims holiday-aware shifts the owning task excludes
- **Contract row:** ledger AMN BEYOND shift calendar; approvals ledger `BP-shift-calendar` (NO-CHANGE, "mfg slice") · **Source:** Both
- **Evidence:** `r32-ledger-mfg.tsv:179` vs `issues/p10-15.md:54` and `FRD-MFG.md:457`.
- **What a user experiences:** Holidays fall into neither slice.
- **Fix:** Use the platform holiday calendar in FR-785/787, or record an authorised v2 deferral in both ledgers.

### F-R32ME-030 — Low: ledger and Closes tracking drift (D-20 item 6, "exactly one open issue")
- **Source:** Claude
- **Evidence:**
  - AMN 1-18 (ledger → p10-19) and AMN 13.4-04 (ledger → p10-17) are in neither task's Closes (`p10-19.md:45`, `p10-17.md:46`).
  - MRB 8.2-05, 8.2-08 and 8.2-09 are claimed by both p10-16 ("8.2-01…8.2-11", `p10-16.md:48`) and p10-15/p10-20.
  - AMN 4-32 is ledgered to p10-15 but closed by FR-785 / p10-04.
  - Approvals-ledger row 4-44 cites P10-08, but the work lives in p10-16 / FR-808.
- **Fix:** Correct the Closes lines and the ledger rows.

### F-R32ME-031 — Low: error codes and actors drift between documents
- **Source:** Claude
- **Evidence:**
  - p10-06 `:70` uses `DEVIATION_NOT_APPLICABLE` where FR-827 and MSI-GRD-21 use `DEVIATION_REQUIRED`.
  - FR-795 has `:approve` releasing, while ECH-T1-14 uses `:release`.
  - FR-832 refuses "exhausted" tools, while SFL-GRD-10 refuses bookings that "would exceed" life.
- **Fix:** Align the documents.

### F-R32ME-032 — Low: ECN/SMR numbers are assigned at create
- **Source:** Claude
- **Evidence:** ECH-T1-01 `:35` and FR-798 assign numbers at create. PRD `:135` says "assigned on approval/posting, never on draft", and no D-20 justification is recorded.
- **Fix:** Record the deviation, or assign the number at submit.

### F-R32ME-033 — Low: masters have `:delete` despite "retired, never deleted"
- **Source:** Claude
- **Evidence:** PRD `:102` vs the `:delete` verb on operators, shifts, operations, tools and plans (`p10-15:38`, `p10-16:38`, `p10-26:33`).
- **Fix:** State delete-only-if-unreferenced, otherwise deactivate.

## Dropped after verification
- None. The GPT leg's "dropped" notes were non-findings (no scoped NO-CHANGE rows; the gate is correctly on production, not the SO line).

## Remediation backlog
All targets are design-set files. No migration is authored now; the affected specs are the V5620xx/V5622xx rows named.

| Finding | Files to touch | Migration | Shared registries | Parity apply-to | Contract |
|---|---|---|---|---|---|
| 001, 002 | FRD-MFG FR-798/801 → `mfg-engineering-change` → `p10-19`, `p10-05`; trade fold (SO-line mark) | V562050 spec | waiver verb | warehouse-trade SO/enquiry | ECH-GRD-10, T4-05, T1-26 |
| 003, 028 | `mfg-engineering-change`, `mfg-shop-floor` → p10-19, p10-18, p10-16, p10-26 | none | permissions dependencies | — | ECH-T1-22/25, SFL rows |
| 004, 012, 013, 014 | FRD FR-792/793 → `mfg-engineering-change` → DATA-MODEL `whm_ecn_impacts` → `p10-17`; `mfg-mrp` capacity | V562030 spec | `document-approval` lifecycle | p10-05, p10-13 | ECH-T1-06/07, T4-01/02 |
| 005 | `mfg-engineering-change` → `p10-17`, `p10-18` | none | none | — | ECH-T1-02/06 |
| 006, 007 | `p10-03`, `p10-05`, `p10-16`, `p10-17`; `p8-30` dependency; document types | V563xxx seed spec | `p8-30` type registry | core approval | BOM-T1-21, SFL-T1-06, new DAP rows |
| 008 | `p10-05`, `p10-03`, `p10-08`, `p10-09` R32 sections; `mfg-production-order`, `mfg-shop-floor` | V562200/V562220 spec | none | — | PRO rows, SFL-GRD-05 |
| 009, 021 | `mfg-bom` T5 → `p10-03`; `mfg-mrp` §12 → `p10-12` | V562200 spec | `WAREHOUSE_MFG_BOM` scope | p10-25 | BOM-T5, new MRP row |
| 010 | `mfg-engineering-change` → `p10-19`; core gate pass / despatch seam | none | none | warehouse-trade invoicing hand-off | ECH-T1-24, T4 |
| 011 | FRD FR-792/811 → `p10-16`, `p10-17`, `p10-21` | none | none | — | ECH-EC-01 |
| 015, 016, 017 | FRD FR-790/791 → `mfg-shop-floor`, `mfg-bom` → `p10-16`, `p10-03` | V562010 spec | none | p10-25 | SFL-GRD-05, BOM-GRD-08 |
| 018 | FRD FR-806 → `mfg-shop-floor` → `p10-20` | none | none | — | SFL-T4-02 |
| 019 | `p10-06` R32, `mfg-material-staging-issue` §12 | none | none | core p8-09 | new MSI row |
| 020 | `mfg-engineering-change` → `p10-18` | none | none | — | ECH-T1-14 |
| 022–025 | `mfg-shop-floor` → DATA-MODEL → `p10-26`, `p10-20` | V562120 spec | none | p10-13 | SFL-T1-42/43, T4-04/05 |
| 026, 027 | DATA-MODEL → `mfg-costing-close` → `p10-25` | V562110 spec | none | trade quotation | CST-T1-20 |
| 029, 030 | `p10-15`, the ledgers, task Closes lines | none | none | approvals ledger | — |
| 031–033 | `p10-06`, FRD FR-795/832, `p10-17` | none | none | — | — |

## Parity (C10)
- **Mobile:** out of scope per the caller and D-20 item 5 (`docs/DECISIONS.md:728`). Every screen says Mobile N/A.
- **Siblings sharing these patterns:** core warehouse (`p8-30` approvals, `p8-09` MR escalation, `p8-03` gate pass, `p8-18` deviation) and warehouse-trade (SampleRequestPort and DrawingRevisionPort callers, CostEstimatePort). The dealer vertical is fenced (D-20 item 4).

## In code, not in contract
- Not applicable: this is a pre-build design set. Design-to-contract undocumented behaviour is captured in F-008, F-019 and F-028.

## Contract quality
- All five contracts are v0 and unratified.
- No scoped MRB, AMN or BRIEF row in `r32-ledger-mfg.tsv` is NO-CHANGE (55 NEW, 28 AMEND, 1 ACCOUNTING). The NO-CHANGE reasons that fail are in the approvals ledger: `BP-shift-calendar` (F-029) and 3-36 / 3-39 (F-007).
- Checked and clean:
  - D-20 item 10 emergency issue (auto-MR) is covered by core `store-issue-return` SIR-T1-10.
  - The deviation usages `ALTERNATE_ISSUE` and `PRODUCTION_CONSUMPTION` exist in `p8-18.md:20`.
- Could not verify:
  - Grid, filter and export supersets (pre-build).
  - That the T3 jobs (ECH-T3-01/02, SFL-T3-01) exist; recipients for SFL-T3-01 are unnamed.
  - The DVA rules (RE-VERIFY, `FRD-MFG.md:501`).

## Referred to standards reviewer
- None.

## Fix record (2026-10-25)

Contracts carry a 2026-10-25 R32-fix amendment row (`mfg-engineering-change` §9, `mfg-shop-floor` §9, `mfg-bom` §9, `mfg-mrp` §7, `mfg-material-staging-issue` §9, `mfg-production-order`, `mfg-costing-close`). FRD-MFG closes with an *R32 fix wave — engineering* disposition paragraph. No new migration version: every change lands in a migration its task already claims.

| Finding | Files changed | State |
|---|---|---|
| F-R32ME-001 | `mfg-engineering-change` (ECH-T1-25, -26, -29, -30, ECH-GRD-10, -17, ECH-T4-05, ECH-UNR-04, ECH-EC-05); FRD-MFG FR-801; `p10-19`; `p10-05`; `mfg-production-order` PRO-GRD-50 | done (`D-21` item 8) |
| F-R32ME-002 | `mfg-engineering-change` ECH-GRD-10, ECH-T4-10, ECH-OPEN-02; FRD-MFG FR-798, FR-801; FRD-TRADE FR-545 (trade half: the mark); `p8-26` CN-20 (`sampleApprovalRequired`); DATA-MODEL `wh_demand_order_lines.sample_approval_required`; `p10-19`, `p10-05` | done (`D-21` item 8) |
| F-R32ME-003 | `mfg-engineering-change` ECH-T1-22, -27, ECH-GRD-09, ECH-EC-02; FRD-MFG FR-800; `p10-19` | done |
| F-R32ME-004 | `mfg-engineering-change` ECH-T1-06 (`effective_from_actual`), -07 (cancel from `APPROVED`), ECH-EC-03; FRD-MFG FR-792; DATA-MODEL `whm_ecns`; `p10-17` | done |
| F-R32ME-005 | `mfg-engineering-change` ECH-T1-06, ECH-GRD-12, ECH-T4-02; FRD-MFG FR-792; `p10-17`, `p10-18` | done |
| F-R32ME-006 | `p10-03`, `p10-16`, `p10-17`, `p10-18`, `p10-19` (Depends / Blocked on); FRD-MFG FR-782; `mfg-bom` BOM-T1-21; `mfg-shop-floor` SFL-T1-05; IMPLEMENTATION-PLAN deps | done (`D-21` item 6) |
| F-R32ME-007 | `WHM_DRAWING_RELEASE` (ECH-T1-14, ECH-T2-04), `WHM_SAMPLE_DISPATCH` (ECH-T1-24, -28, ECH-GRD-08); FRD-MFG FR-795, FR-800, FR-835; `p10-18`, `p10-19`. `WHM_PRODUCTION_ORDER` / `WHM_SHORTAGE_RELEASE` are carried by F-R32MS-008 in `p10-05`; the DAP §0.1 listing is core-approvals' (`D-21` item 6) | done (`D-21` item 6) |
| F-R32ME-008 | `mfg-production-order` PRO-T1-50; `mfg-shop-floor` SFL-GRD-05 (trial path); `mfg-costing-close` CST-T4-30; FRD-MFG FR-791, FR-799; `p10-05`, `p10-03` (`is_trial`), `p10-08` (receipt into `SAMPLE`), `p10-09` (sample cost pool), `p10-16` (selection trial path) | done |
| F-R32ME-009 | `mfg-bom` §5.1 (tabs, editor columns, Import / Compare / Mass replace); FRD-MFG FR-781, FR-783; `p10-03` | done |
| F-R32ME-010 | `mfg-engineering-change` ECH-T1-28, -31, ECH-T4-09; FRD-MFG FR-798 (`charge_amount`), FR-800, FR-835 (`SAMPLE_REQUEST` cost object); DATA-MODEL `whm_sample_requests`, `whm_sample_iterations`; `p10-19` | done (`D-21` item 2 invoice producer) |
| F-R32ME-011 | `mfg-engineering-change` ECH-GRD-15, ECH-EC-01; FRD-MFG FR-792, FR-811; DATA-MODEL `whm_routings` EXCLUDE predicate, `whm_ecn_items.activation_status`; `p10-17`, `p10-21`, `p10-05` | done |
| F-R32ME-012 | `mfg-engineering-change` ECH-T1-02, -03, -05; FRD-MFG FR-793; `p10-17` | done |
| F-R32ME-013 | `mfg-engineering-change` ECH-T4-01, -07, ECH-EC-04; FRD-MFG FR-793; DATA-MODEL `whm_ecn_impacts`; `mfg-mrp` §5.1 capacity (`APPROVED`); `p10-17`, `p10-13` | done |
| F-R32ME-014 | `mfg-engineering-change` ECH-T1-08, ECH-GRD-16, ECH-T3-03, ECH-T4-08; FRD-MFG FR-793, WH-SC-776; DATA-MODEL `whm_ecn_impacts.use_up_until/use_up_remaining_quantity`; `p10-17` | done |
| F-R32ME-015 | FRD-MFG FR-791; `mfg-shop-floor` SFL-GRD-05; `p10-16`, `p10-25` | done |
| F-R32ME-016 | FRD-MFG FR-790, FR-791; `mfg-shop-floor` SFL-GRD-30, SFL-T1-06; `mfg-bom` BOM-T1-21; `mfg-engineering-change` ECH-GRD-14; DATA-MODEL `whm_routings.bom_id`; `p10-03`, `p10-16` | done |
| F-R32ME-017 | `mfg-bom` BOM-GRD-08; FRD-MFG FR-791; `p10-03` | done |
| F-R32ME-018 | FRD-MFG FR-806 aligned to the booking trigger (`SFL-T4-02`, `p10-20` already say booking) | done |
| F-R32ME-019 | `mfg-material-staging-issue` MSI-T4-20; `p10-06`; `r32-ledger-mfg.tsv` MRB 7.1-17 | done |
| F-R32ME-020 | `mfg-engineering-change` ECH-GRD-13, -12; FRD-MFG FR-795; `p10-18` | done |
| F-R32ME-021 | `mfg-bom` BOM-GRD-35; `mfg-mrp` MRP-N-21; FRD-MFG FR-781; DATA-MODEL `whm_bom_lines.variant_option_group`; `p10-03`, `p10-12` | done |
| F-R32ME-022 | `mfg-shop-floor` SFL-T1-42; FRD-MFG FR-833; `p10-26` | done |
| F-R32ME-023 | `mfg-shop-floor` SFL-T1-50; FRD-MFG FR-833; DATA-MODEL `whm_maintenance_orders.cancel_reason`; `p10-26` | done |
| F-R32ME-024 | `mfg-shop-floor` SFL-T1-42, SFL-T4-04; FRD-MFG FR-833; DATA-MODEL `whm_maintenance_plans`, `whm_maintenance_orders` (planned window); `p10-26`, `p10-13` | done |
| F-R32ME-025 | `mfg-shop-floor` SFL-GRD-10, SFL-T4-05; FRD-MFG FR-832; DATA-MODEL `whm_tool_life_entries` (booking × tool uk; scalar `tool_id` dropped); `p10-26` | done |
| F-R32ME-026 | DATA-MODEL `whm_cost_estimate_lines` (new, `V562110`; §7, §8.1 inventory and count); `mfg-costing-close` CST-T1-21; FRD-MFG FR-831; `p10-25` | done |
| F-R32ME-027 | `mfg-costing-close` CST-T1-21; FRD-MFG FR-831; DATA-MODEL `whm_cost_estimates` (`cost_basis`, `bom_id`, `routing_id`, `is_unapproved_structure`); `p10-25` | done |
| F-R32ME-028 | `mfg-engineering-change` ECH-T1-24, -28, -31, -32 (`:close` and `whm_drawings:supersede` removed); `mfg-shop-floor` SFL-T1-08, -09, -51, -52; FRD-MFG §7 permissions, FR-795, FR-832; `p10-18`, `p10-19`, `p10-16`, `p10-26` | done |
| F-R32ME-029 | FRD-MFG FR-785, FR-787 (platform holiday calendar, `RH-011`); `p10-15`, `p10-13`; `r32-ledger-mfg.tsv` AMN BEYOND shift calendar; `r32-ledger-approvals.tsv` BP-shift-calendar → AMEND `p10-15` | done |
| F-R32ME-030 | `p10-19` Closes + AMN 1-18, 13.4-04; `p10-17` Closes + AMN 13.4-04; `p10-16` Closes and FRD-MFG FR-790 Closes (8.2-05/-08/-09 removed); `p10-04` Closes + AMN 4-32; `r32-ledger-mfg.tsv` AMN 4-32 → `p10-04`; `r32-ledger-approvals.tsv` 4-44 → `p10-16` + `p10-08` (3-36 / 3-39 already AMEND by the core-approvals fix) | done |
| F-R32ME-031 | `p10-06` (`DEVIATION_REQUIRED` vs core's `DEVIATION_NOT_APPLICABLE`); FRD-MFG FR-795 (`:approve` review vs `:release` production) and FR-832 (*would exceed*); `mfg-material-staging-issue` amendment | done |
| F-R32ME-032 | `ECN-` and `SMR-` assigned at submit: `mfg-engineering-change` ECH-T1-01, -02, -20, -21; FRD-MFG FR-792, FR-798; DATA-MODEL partial uks; `p10-17`, `p10-19` | done |
| F-R32ME-033 | `mfg-shop-floor` SFL-GRD-31, SFL-T2-07; FRD-MFG FR-833; `p10-15`, `p10-16`, `p10-26`, `p10-04` | done (`D-21` item 8) |
