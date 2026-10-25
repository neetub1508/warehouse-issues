# Functional conformance — R32 core approvals (`r32-core-approvals`)
Contract: `warehouse-issues/docs/contracts/document-approval.contract.md` (v0, derived 2026-10-25) + `accounting-handover.contract.md` (R32 rows) | Mode: **audit (pre-build design)**
Files reviewed: Claude ≈ 60 (design repo at a244ff6: issues p8-30, p8-23/24/25, p8-08/09/11/17/18/19, p9-02/03/17, p10-01…26 (scanned for approval wiring), p1-03, p0-13, p1-09, p1-14, p8-12; contracts DAP, AHO, TAM extracts; FRD-STORES R32; GLOBAL-SETTINGS; DECISIONS D-20; PRD §1–4, §13; both ledgers. Classic code: WhbMakerChecker and its 29 callers, WhbPendingApprovalSource/AlertService, the approve/cancel controllers, V500042, V501011, WhbAccountingHandoverRepository, WhbAccountingEnvelopeV1, WhbGlBalanceProvider). GPT: 76 files. | File set: derived from workflow.
Engines: Claude + GPT (gpt-6.1-sol, medium) — 7 both · 16 Claude only · 9 GPT only · 1 dropped

Path convention: `issues/…` and `docs/…` are in `/Users/bbhushan/work/git/workspace/warehouse-issues`. `classic/…` is `/Users/bbhushan/work/git/workspace/classic`. Ledgers are in `/private/tmp/claude-501/-Users-bbhushan-work-git-workspace-classic/d8d47f73-78d6-4e9a-ba94-3c5238790e76/scratchpad/`.

## Verdict
**32 findings — not ready to build.** The engine design holds together internally, but it does not fit the code that is already built (auto-post paths, multi-maker counts, an existing alert pipeline, the audit change table, the handover status rule). It also misses most of the approving document types that the PRD and D-20 item 18 say must go through it.

## Status reachability
| Status | In CHECK | In contract T1 | Inbound | Outbound | UI reachable | Verdict |
|---|---|---|---|---|---|---|
| request `PENDING` | no (D-10, projection) | DAP-T1-03 | open on Submit | T1-05/07/08/08a/09 | WS-285 | Adopted types open at Approve, not Submit (F-008); gate pass has no Submit |
| request `APPROVED` | no | T1-04/05 | final approve / zero-level | terminal; amend opens a new request | yes | Escalation can strand the request before it gets here (F-003) |
| request `REJECTED`/`RETURNED`/`WITHDRAWN` | no | T1-07/08/09 | as named | terminal | yes | OK on paper |
| `RETURNED` via `SYSTEM_RETURNED` | no | T1-08a | "an input changed" | terminal | — | No trigger and no job defined (F-020) |
| step `WAITING`→`PENDING`→… | no | T1-05/06 | open / previous level | next level | WS-285 | Choosing distinct people across levels is not guaranteed (F-003) |
| handover `BLOCKED` (version) | CHECK forbids it without a predecessor | AHO-GRD-17 only | R32 refusal | **none** | WS-052 | Cannot be written, and could not leave if it were (F-001) |

## Findings

### F-R32CA-001 — Critical · Rank 1: a "version unsupported" envelope breaks the built status rule and has no release path
- Contract row: AHO-GRD-17, AHO status inventory row `BLOCKED` (`docs/contracts/accounting-handover.contract.md:86`, `:138`)
- Source: Both
- Evidence: `issues/p8-25.md:22`, `:35` write a document-kind envelope `BLOCKED` with `ENVELOPE_VERSION_UNSUPPORTED`. `classic/warehouse-base/src/main/resources/db/migration/V500042__…sql:197` has `CHECK (status <> 'BLOCKED' OR predecessor_handover_id IS NOT NULL)`. Envelopes are emitted in the source transaction (`issues/p8-23.md` Traps; AHO-GRD-15). The only sweep that releases `BLOCKED` rows joins on the predecessor (`classic/…/WhbAccountingHandoverRepository.java:185-190`), and Retry exists only from `REJECTED`.
- What a user experiences: With a v1-only receiver, authorising an MRN fails at flush and the authorisation rolls back. If the rule were relaxed instead, the rows would stay `BLOCKED` for good after the receiver is upgraded.
- Fix: Give version blocking its own status or reason, separate from the predecessor meaning. Change the CHECK through a new migration in `warehouse-base`. Add a capability re-check transition back to `PENDING`. Update the AHO status inventory row.

### F-R32CA-002 — High · Rank 1: built below-threshold self-approval cannot be taken over as `SINGLE_LEVEL`
- Contract row: DAP §0.1 rows `STOCK_ADJUSTMENT`, `COUNT_ADJUSTMENT` (`document-approval.contract.md:40`); `issues/p8-30.md:33`, `:83`
- Source: Claude
- Evidence: `classic/warehouse/…/WhStockAdjustmentAutoPostGuard.java` (javadoc): the `_AUTO` movement is admitted only when the adjustment "was approved by its own submitter" with `warehouse.adjustment.auto_post_below_thresholds` on. `classic/warehouse/…/WhCountPostingService.java:112-114` `isApprovedOnSubmission` checks approved_by = submitted_by. DAP-GRD-03 (`:99`) forbids exactly that, and `SINGLE_LEVEL` always creates a level.
- What a user experiences: After the engine takes over, below-threshold adjustments and counts either need a second person (a behaviour change), or post through `SYSTEM_APPROVED`. In the second case the actor is null and the auto-post guard refuses `ADJUSTMENT_AUTO_POST_TYPE_RESTRICTED`.
- Fix: Make both types `DOCUMENT_DEFINED`, with zero levels below the threshold. Define who acts for the `_AUTO` post (the submitter as `actingUserId`, as TAM-T1-04 does). Amend the auto-post guard contracts (CCT and the adjustment contract).

### F-R32CA-003 — High · Rank 1: escalation can deadlock a request
- Contract row: DAP-GRD-03, DAP-GRD-08, DAP-T3-02 (`:99`, `:104`, `:136`)
- Source: Both
- Evidence: `issues/p8-30.md:44` makes next-level members eligible on the overdue step. GRD-03 then bars them from acting on their own level. GRD-08 checks only that each level is non-empty, at submit.
- What a user experiences: L1 = A and L2 = only B. B approves the escalated L1 step and can never approve L2. With `final_escalation_role` blank, nothing can complete the request.
- Fix: Check that distinct people can cover the whole request, at submit and after every escalated act. Either refuse an escalated act that would leave a later level with no one eligible, or define a reassignment transition. Add this two-person case to WH-SC-743.

### F-R32CA-004 — High · Rank 2: approver value limits are recorded but not enforced
- Contract row: DAP-GRD-04, DAP-T4-02
- Source: GPT (verified)
- Evidence: `issues/p8-30.md:18` says "`approver_limit` … informative". `docs/frd/FRD-STORES.md:643` says the same. PRD `:44`: "Above it, the document routes to the next level". GRD-04 (`:100`) has no amount test.
- What a user experiences: A delegate or escalation target with a 1 lakh limit can approve a 10 lakh PO.
- Fix: Add a limit guard (refuse, or require the next level) that also applies to delegates and escalation targets. Add an over-limit acceptance case.

### F-R32CA-005 — High · Rank 2: the engine cannot hold a different approve permission per level
- Contract row: DAP §0.1 `QUALITY_DEVIATION` (`:46`), DAP-T2-03 (`:127`)
- Source: Both
- Evidence: `WhApprovable.approveVerb()` is one verb per type (`issues/p8-30.md:30`; FRD-STORES R.3 `:462`). `issues/p8-18.md:24` needs `:approve` at L1 and `:approve_final` at L2. Levels have no verb column (`p8-30.md:18`).
- What a user experiences: Either an ordinary deviation approver can give the Plant-Head final approval, or a Plant Head who holds only `:approve_final` is refused.
- Fix: Add a per-level `required_authority`, frozen onto the step, and check it for delegates and escalation targets too.

### F-R32CA-006 — High · Rank 3: the list of approvals to take over is wrong in both directions
- Contract row: DAP §0.1, DAP-UNR-03 (`:117`), `issues/p8-30.md:33`, `:83`
- Source: Claude
- Evidence:
  - GRN excess (GBM-T1-05) is listed as a built single-step approval. No code exists for it (`approve_excess` is absent from classic), and its owner P8-04 #565 is OPEN with no engine wiring (`issues/p8-04.md` has zero engine references).
  - Built Approve endpoints that call `WhbMakerChecker` but are **not** in §0.1: `WhPurchaseOrderController /{id}/approve` (`wh_purchase_orders:approve`, `PO_APPROVER_IS_SUBMITTER`), `WhReceiptReversalController`, `WhSupplierReturnController`, `WhRmaController`, `WhThreeWayMatchController`, `WhQualityInspectionController …/scrap/approve`, `WhReturnReceiptController …/approve-scrap`, `WhbStockMovementController /{id}/approve`, `WhbPeriodOverrideRecorder` (`PERIOD_OVERRIDE_SELF_APPROVED`), `WhbWarehouseValidationService` (`WAREHOUSE_REGISTRATION_SELF_APPROVAL`) and `WhBlockedMovementValidationService`.
  - The `SITE_BRANCH_TRANSFER` verb and code are left unnamed ("the FBL code"). The built code is `wh_transfer_orders:approve` / `TRANSFER_SELF_APPROVAL`.
- What a user experiences: These documents keep a second approval mechanism beside the engine: no bands, no escalation, no inbox, no append-only record. `ApprovalRegistryVerifier` only checks beans that are registered, so nothing fails.
- Fix: Write a complete type list: type code, verb, opening event, policy, kept code, owning task. Each built path is either taken over or excluded with a reason. Move GRN excess into P8-04's scope.

### F-R32CA-007 — High · Rank 3: consumer tasks keep their own approval ladders
- Contract row: DAP §0.1 (`:44`, `:49`, `:171`), DAP-UNR-03; D-20 item 18
- Source: Both
- Evidence:
  - `issues/p8-08.md` (MRN authorise, 0 engine references, own `MRN_SELF_APPROVAL` at `:50`).
  - `issues/p8-17.md:30` (NCR closure "by a second person"; no `WhApprovable`).
  - `issues/p8-11.md:27` (the permission list lacks `approve_department`, which `:73` uses; the `STORE_VERIFY`/`STORE_APPROVAL` steps are outside the engine).
  - `issues/p8-19.md:25` (QC result approval stamps inspection columns directly).
  - `issues/p10-05.md:56` (`RELEASE_SELF_APPROVAL`), `p10-18.md:20` (`DRAWING_SELF_RELEASE`), `p10-19.md:22` (sample dispatch), `p10-22.md:23` (`PDI_SELF_SIGN`), plus `p10-07`/`-09`/`-10`.
  - Only p10-03/16/17 name p8-30, and p10-16:66 / p10-17:62 keep a "single checker until it ships" fallback.
- What a user experiences: The PRD §3 approver table (PR, PO, IQC/deviation, MRN, MR, return, BOM, drawing, PO release, PDI, sample dispatch) is only partly configurable. Approvals skip escalation, delegation, history and WS-285.
- Fix: Add an engine-wiring section to each task: type, verb, policy, opening event, callbacks. Remove the interim fallbacks, since p8-30 is a declared dependency.

### F-R32CA-008 — High · Rank 3: adopted types open their request at Approve, not at Submit
- Contract row: DAP-T1-03 (`:81`), DAP-T4-05
- Source: GPT (verified)
- Evidence: `issues/p8-30.md:33` ("open an engine request and act its step inside their existing Approve endpoint"). `classic/warehouse/…/WhGatePassService.java:299-300` goes from DRAFT straight to APPROVED; there is no Submit.
- What a user experiences: Nothing appears in My Approvals, no pending alert fires, escalation never starts, and the lock does not apply until someone has already found and approved the document.
- Fix: Name the opening event per type: a Submit for the gate pass, MRQ's existing submit, and so on. Also define what happens to documents already pending at upgrade.

### F-R32CA-009 — High · Rank 3: document-only handovers drop out of branch-scoped queues
- Contract row: AHO-T5 / WS-052; `issues/p8-23.md` §2 (`movement_id` nullable)
- Source: GPT (verified)
- Evidence: `classic/warehouse-base/…/WhbAccountingHandoverRepository.java:40-47`: the site clause works only through `whb_stock_movements` via `e.movement_id`.
- What a user experiences: Branch users never see MRN, debit-note or credit-note proposal rows that have no movement. Only unscoped admins do.
- Fix: Store the source document's company and site on the handover, and use them in grid, count, statistics, export and alert predicates.

### F-R32CA-010 — High · Rank 4: one frozen maker loses the built exclusions for several makers
- Contract row: DAP-GRD-03 (`:99`)
- Source: Both
- Evidence: `classic/warehouse/…/WhCountValidationService.java:95-113` excludes every submitter of every attempt, every counter and every zone assignee. MRN also excludes the inspector (`issues/p8-08.md:50`). GRN excess excludes the last line editor and the GRN creator. The MRQ excludes both requester and creator (`WhMaterialRequisitionValidationService.java:465-466`). Yet the snapshot and request carry one `maker` (`p8-30.md:20`, `:30`), and `:65` forbids keeping `WhbMakerChecker` beside the engine.
- What a user experiences: After the engine takes over, a counter can approve their own count.
- Fix: Have `snapshot()` return `excludedActorIds` with a reason per actor, freeze them on the request, and check them in GRD-03.

### F-R32CA-011 — High · Rank 4: editing an approved production order breaks the approved-document lock
- Contract row: DAP-GRD-07, DAP-T1-12
- Source: GPT (verified)
- Evidence: `docs/contracts/mfg-production-order.contract.md:301` (PRO-T1-40: "an edit of an `APPROVED` order returns it to `PLANNED`").
- Fix: Use either an amendment with a revision, or cancel and re-raise. State which in DAP §0.1.

### F-R32CA-012 — High · Rank 4: the adapter implements a different credit interface from the one trade uses
- Contract row: AHO-GRD-14; trade CN-17
- Source: GPT (verified)
- Evidence: `issues/p8-23.md:34` `WhbCustomerCreditExposureProvider.exposure(companyId, customerId)` vs `issues/p9-17.md:12` `WhCustomerCreditCheckProvider` (check plus advanceReceived).
- What a user experiences: Trade stays `NOT_AVAILABLE` even with the adapter installed.
- Fix: Pick one interface and align p8-23, p9-17, FRD-TRADE §12c and AHO-GRD-14.

### F-R32CA-013 — High · Rank 4: envelope v2 cannot carry what the document kinds need
- Contract row: AHO-ENV-11/12, AHO-T1-12…16
- Source: GPT (verified), with Claude evidence added
- Evidence: `issues/p8-23.md:25`, `:28` need the supplier, bills (number, date, amount) and customer/ship-to. The v2 header in `issues/p8-25.md:20` adds none of these, and v1 (`classic/…/WhbAccountingEnvelopeV1.java:25-47`) has none. Claude: the v2 header also re-adds `sourceDocumentType/Id/Ref`, which v1 already has (`:43-45`), as an ambiguous duplicate.
- Fix: Define a typed payload per envelope kind. Reuse v1's source-document fields.

### F-R32CA-014 — Medium · Rank 4: zero-level seeds exist only for companies that existed at migration time
- Contract row: TAM-T1-04; `issues/p9-03.md:32-36`, `:76`
- Source: Claude
- Evidence: Seeds go "in each company currency" in V551030. `wh_approval_rules.company_id` and `currency_code` are NOT NULL (`p8-30.md:16`). Trade types are `REFUSE`.
- What a user experiences: On a company created later, `PO_RELEASE`, `SO_RELEASE`, cancel and short-close are all refused `422 APPROVAL_NO_RULE`.
- Fix: Seed when a company is created (listener), or allow a company-less default rule.

### F-R32CA-015 — Medium · Rank 4: two contradictory amendment models
- Contract row: DAP-T1-12 (`:91`) vs TAM §0.1 `PO_AMENDMENT`/`SO_AMENDMENT`/`PRC_AMENDMENT`/`SRC_AMENDMENT`/`PRICE_LIST_AMENDMENT` (`issues/p9-03.md:69-72`)
- Source: Claude
- Evidence: DAP re-opens the **same** type at revision n+1, approved by the band of the new value. TAM uses separate amendment types with their own zero-level seed (`PO_AMENDMENT {supplier_return_replacement}`).
- What a user experiences: The type and band an amendment uses depend on which contract the builder reads.
- Fix: Pick one model and amend the other contract.

### F-R32CA-016 — Medium · Rank 4: "one despatch, one envelope" no longer holds
- Contract row: AHO A4 (`accounting-handover.contract.md:51`), WH-SC-156; AHO-T1-15
- Source: Claude
- Evidence: Posting a despatch already emits a `STOCK_MOVEMENT` envelope (AHO-T1-01). R32 adds an `INVOICE_REQUEST` for the same despatch (`issues/p8-23.md:28`), while `issues/p8-24.md` still proves "one despatch produces one valued envelope".
- Fix: Restate A4 as one movement envelope plus one document envelope, linked to each other, and say which one carries the value so COGS is not counted twice.

### F-R32CA-017 — Medium · Rank 4: numbering at approval does not fit the engine
- Contract row: FR-735; `issues/p1-09.md:156-163`
- Source: Claude
- Evidence: `wh_approval_requests.document_ref` is "frozen number or draft ref" (`p8-30.md:20`), so with `APPROVAL` numbering the register shows `DRAFT-…` forever. An amendment's second `onApproved` has no rule against drawing a second number.
- Fix: Refresh `document_ref` from the document when read. Make number assignment idempotent per document.

### F-R32CA-018 — Medium · Rank 4: the TRUNCATE protection differs from the built pattern
- Contract row: DAP-UNR-05 (`:119`); `issues/p8-30.md:22`
- Source: Claude
- Evidence: p8-30 says "TRUNCATE is revoked from the application role". The application role runs Flyway and owns the table. Built tables use `BEFORE TRUNCATE` statement triggers (`classic/…/V501011__…sql:335-343`).
- Fix: Use the trigger idiom.

### F-R32CA-019 — Medium · Rank 5: the built pending-approval alert job is not retired
- Contract row: DAP-T3-01
- Source: Both (GPT raised it under contract quality)
- Evidence: `classic/warehouse-base/…/jobs/WhbPendingApprovalAlertService.java:37`, `:44` already alerts on `warehouse.approval.pending_alert_hours` for 5 sources (stock adjustment, count, PO, MRQ, receipt reversal `…PendingApprovalProvider`). p8-30:43 adds `WhApprovalAlertJob` without mentioning it.
- What a user experiences: The same pending document raises two alerts.
- Fix: Retire the built sources (or turn them into adapters) as each type moves to the engine. List this in p8-30.

### F-R32CA-020 — Medium · Rank 5: `SYSTEM_RETURNED` has no trigger
- Contract row: DAP-T1-08a (`:87`)
- Source: Claude
- Evidence: The trigger is "an input the request depends on changed", with no job, event or input list. GRD-07 already refuses edits while pending.
- Fix: List the inputs (for example the PR quantity, or a price-list change) and the event that detects each, or drop the row.

### F-R32CA-021 — Medium · Rank 4: the reopened P0-13 re-specifies the built audit change table
- Contract row: FR-736, DAP-T4-03; ledger 3-21 REOPEN
- Source: Both
- Evidence: `issues/p0-13.md:353` creates `whb_audit_event_changes` keyed by (`event_sequence_no`, `occurred_at`) with an FK and VARCHAR(4000). The table already exists keyed by `audit_event_id`, deliberately without an FK, with TEXT values and a changes digest (`classic/…/V501011__…sql:216-228`, `:265`). It is written by `WhbAuditEntityListener` (15 services use `WhbAuditFieldChange`), and the original p0-13 already scoped it (`:14`).
- Fix: Reduce the R32 scope to what is actually missing: print/reprint events, secret masking, export of one row per change, and the masters not yet covered.

### F-R32CA-022 — Medium · Rank 6: the cancel/short-close reason rule has no endpoint list
- Contract row: DAP-GRD-09 (`:105`); `issues/p8-30.md:27`, `:84`
- Source: Claude
- Evidence: p8-30 calls GRD-09 "the coverage list", but GRD-09 lists nothing. 38 built cancel/close endpoints exist (pick task, pack session, wave and replenishment-task cancel among them).
- What a user experiences: Applied as a blanket rule, operational cancels that work today start returning `422 REASON_REQUIRED`.
- Fix: Enumerate document cancel/close endpoints and exclude operational tasks.

### F-R32CA-023 — Medium · Rank 6: QC defaults disagree between task and FRD
- Contract row: FR-697/699
- Source: GPT (verified)
- Evidence: `issues/p8-19.md:20` (`inspector_authorisation_required` true, `result_approval_mode` ALL) vs `docs/frd/FRD-STORES.md:686`, `:688` (false, NONE).
- Fix: Settle the defaults once and update the task, FRD, settings and acceptance fixtures.

### F-R32CA-024 — Medium · Rank 6: settings registry gaps and a wrong key name
- Contract row: GLOBAL-SETTINGS
- Source: Claude
- Evidence:
  - Missing from `docs/GLOBAL-SETTINGS-DECISIONS.md`: `warehouse.quality.deviation_approval_levels` (p8-18), `warehouse.stores.return_approval_steps` (p8-11), `bom.approval_levels` / `ecn.approval_levels` (no `warehouse.` prefix; p10-03/16/17), `warehouse.trade.approval.value_basis` (p9-03), `warehouse.accounting.envelope_max_version` (p8-25), `warehouse.quality.result_approval_mode` (p8-19), `release_requires_approval` (p10-05).
  - p8-30:33 names `warehouse.stores.requisition_second_approval_threshold`; the built key is `warehouse.stores.requisition_second_approval_value`.
  - The settings row at `:44` logs a blank WhatsApp template as `SKIPPED_NO_ADDRESS`, which is the wrong outcome.
- Fix: Register the keys and correct the names.

### F-R32CA-025 — Medium · Rank 6: `hsn_must_resolve` changes behaviour for existing items
- Contract row: ITM R32 / FR-731; `issues/p1-03.md:229`
- Source: Claude
- Evidence: Default `true` refuses **any** save of a purchasable or saleable item whose HSN is not in the master. This applies to existing items edited for unrelated fields, against "no behaviour change".
- Fix: Apply the check on create or when the HSN changes, or default it to false with a release note.

### F-R32CA-026 — Medium · Rank 7: ledger rows marked NO-CHANGE whose reason does not hold
- Contract row: `r32-ledger-approvals.tsv`
- Source: Claude
- Evidence:
  - 1-15 "MRN … already planned": p8-08 does not wire the engine.
  - 1-16 and 3-31 "QC-Manager result approval = P8-19": P8-19 is outside the engine, against D-20 item 18.
  - 3-34 "Material return = P8-11": only the department step is in DAP §0.1.
  - 3-36, 3-38, 3-39 "drawing / PDI / sample dispatch — mfg slice": p10-18, p10-22 and p10-19 do not register types.
  - 1-26: the reason holds, but its 3-21 follow-up is mis-scoped (F-021).
- Fix: Change these rows to AMEND against the owning tasks.

### F-R32CA-027 — Medium · Rank 7: the PPAP-before-AVL NO-CHANGE does not hold
- Contract row: `TCE-T1-04a`; ledger `BP-ppap`
- Source: GPT (verified)
- Evidence: Ledger row `BP-ppap` says the quality slice owns it. `issues/p8-06.md:79` puts first-article inspection at the GRN. `docs/contracts/trade-counterparty-evaluation.contract.md:87` approves an AVL row with no FAI/PPAP prerequisite.
- Fix: Own a quality→AVL gate, or record the row as deferred.

### F-R32CA-028 — Medium · Rank 7: the GL provider signature does not match its task
- Contract row: AHO-RPT; `issues/p8-23.md:18`
- Source: GPT (verified)
- Evidence: The built `controlAccountBalance(companyId, warehouseId, asOfDate)` (`classic/…/WhbGlBalanceProvider.java:47`) vs "per site × owner × item group" in the task.
- Fix: Keep the built signature, or design a v2 port.

### F-R32CA-029 — Low · Rank 7: MRQ refusal code changes for the two-level case
- Source: Claude
- Evidence: Built code returns `REQUISITION_SELF_APPROVAL` for "same person, first and final" (`WhMaterialRequisitionValidationService.java:471-474`). DAP-GRD-03 returns `APPROVAL_SAME_PERSON_TWO_LEVELS`, against "no client breaks" (`p8-30.md:33`).
- Fix: Keep the type's code for both cases.

### F-R32CA-030 — Low · Rank 7: P9-03's old acceptance and definition of done are stale
- Source: Claude
- Evidence: `issues/p9-03.md:128` (`WAREHOUSE_TRADE` category delivers), `:135` ("consumes `ApprovalService`", "clean against `trade-approval-matrix`") contradict its R32 section (`:59-93`).
- Fix: Strike those lines, or mark them superseded.

### F-R32CA-031 — Low · Rank 7: the new adapter module has no migration band or module registration
- Source: Claude
- Evidence: `issues/p8-23.md:5`, `:16` (`accounting-adapter-warehouse`, DDL "in the accounting repository's adapter band"). The CLAUDE.md MODULES table has no row for it; the dealer adapter has V620000–V620999.
- Fix: Reserve a band and list the module integration points.

### F-R32CA-032 — Low · Rank 7: P8-12 has two R32 blocks split by its definition of done
- Source: Claude
- Evidence: `issues/p8-12.md:49`, `:66`, `:68`.
- Fix: Merge the two blocks above the definition of done.

## Dropped after verification
- Claude: "V500505 / V500600 / V500601 sort below the built V501236 and will crash-loop Flyway" → `classic/platform/backend/src/main/resources/application.yml:113` (`out-of-order: true`) and `shared/docker/.env:34` (`FLYWAY_OUT_OF_ORDER=true`). Out-of-order migrations are allowed, and none of the numbers collide with an existing file.

## Remediation backlog
| Finding | Files to touch | Migration | Shared registries | Parity apply-to | Contract |
|---|---|---|---|---|---|
| F-001 | issues/p8-25.md → p8-23.md → AHO contract | next free in V500000–V509999 (CHECK change) | none | every document kind | AHO status inventory, GRD-17, new T1 release |
| F-002 | issues/p8-30.md → adjustment/count contracts | none | none | stock adjustment, count | DAP §0.1 policy; CCT auto-post rows |
| F-003 | issues/p8-30.md → DAP | V511600 (unbuilt) | none | trade, mfg consumers | DAP-GRD-08, T3-02 |
| F-004 | issues/p8-30.md → FRD-STORES FR-722 → DAP | V511600 | none | all banded types | new DAP-GRD |
| F-005 | issues/p8-30.md → p8-18.md → DAP | V511600 | permission_dependencies | deviation, BOM/ECN levels | DAP T2-03, §0.1 |
| F-006 | issues/p8-30.md, p8-04.md → DAP §0.1 | none | none | 11 built approve paths | DAP §0.1 |
| F-007 | p8-08, p8-11, p8-17, p8-19, p10-05/07/09/10/18/19/22 | owners' unbuilt numbers | type registry, permissions | quality, mfg | DAP §0.1 + each consumer T1 |
| F-008 | issues/p8-30.md → gate-pass/MRQ contracts | owners' numbers (gate pass submit) | none | 8 adopted types | DAP-T1-03 |
| F-009 | issues/p8-23.md → AHO T5 | V500505 (unbuilt) | none | 5 document kinds | AHO T5 |
| F-010 | issues/p8-30.md → DAP | V511600 | none | count, MRN, GRN excess, MRQ | DAP-GRD-03 |
| F-011 | mfg-production-order contract, p10-05 | V562220 (unbuilt) if revision is stored | none | none | PRO-T1-40 |
| F-012 | p8-23, p9-17, FRD-TRADE §12c | none | none | SO approval, dispatch | AHO-GRD-14, CN-17 |
| F-013 | p8-25, p8-23, AHO | V500506 (unbuilt) | none | 5 kinds | AHO-ENV-11/12 |
| F-014 | p9-03 | V551030 (unbuilt) | none | trade types | TAM-T1-04 |
| F-015 | DAP or TAM | none | none | trade amendments | DAP-T1-12 / TAM §0.1 |
| F-016 | AHO, p8-24 | none | none | despatch | AHO A4 |
| F-017 | p1-09, p8-30 | V500603 (unbuilt) | none | all APPROVAL-numbered types | FR-735 |
| F-018 | p8-30 | V511600 | none | none | DAP-UNR-05 |
| F-019 | p8-30 | none | none | 5 built sources | DAP-T3-01 |
| F-020 | DAP, p8-30 | none | none | trade | DAP-T1-08a |
| F-021 | p0-13, FRD-STORES FR-736 | drop V500604, or ALTER only | none | all audited masters | FR-736 |
| F-022 | DAP, p8-30 | none | none | 38 built endpoints | DAP-GRD-09 list |
| F-023 | p8-19, FRD-STORES | V511552 (unbuilt) | admin_settings | IQC/PQC | QIC settings |
| F-024 | GLOBAL-SETTINGS, p8-30 | owners' numbers | admin_settings | — | — |
| F-025 | p1-03 | V500601 (unbuilt) | none | trade lines | ITM R32 |
| F-026 | r32-ledger-approvals.tsv | none | none | — | — |
| F-027 | ledger, p9-02, p8-06, TCE | none | none | AVL | TCE-T1-04a |
| F-028 | p8-23 | none | none | WS-219 | AHO-RPT |
| F-029 | DAP | none | none | MRQ | DAP-GRD-03 |
| F-030 | p9-03 | none | none | — | — |
| F-031 | p8-23, CLAUDE.md MODULES | next free band (ask) | CacheConfiguration / SafeTranslation if any UI | — | AHO-OPEN-01 |
| F-032 | p8-12 | none | none | — | — |

## Parity (C10)
- Mobile: none. Out of scope by the user's rule and D-20 item 5 (`docs/DECISIONS.md:728`); DAP §6 says the same.
- Modules that share this pattern: warehouse-base, warehouse, warehouse-trade (P9), warehouse-manufacturing (P10), and warehouse-india for envelope fields and scrap sale. warehouse-3pl has its own approve endpoints (`Wh3plAccessorialController`, `Wh3plBillingRunController`, `Wh3plStorageBillingPeriodController`) and no decision on the engine. The dealer vertical is fenced off by D-20 item 4.

## In code, not in contract
- `WhbPendingApprovalSource` and its 5 providers (`classic/warehouse-base/…/jobs/WhbPendingApprovalSource.java:23`) → add to DAP T3 as superseded, or remove them (F-019).
- The 11 built approve paths listed in F-006 → add to DAP §0.1, or exclude them with a reason.
- `whb_audit_event_changes` plus `WhbAuditEntityListener` (`V501011:216`) → FR-736 should cite them as built (F-021).
- `WhbGlBalanceProvider(companyId, warehouseId, asOfDate)` (`:47`) → AHO-RPT row (F-028).

## Contract quality
- DAP §0.1 leaves verbs and codes unnamed for STOCK/COUNT adjustment, REVALUATION/NRV, SITE_BRANCH_TRANSFER and GRN_EXCESS. The built verbs are `wh_stock_adjustments:approve`, `wh_counts:approve`, `wh_revaluations:approve`, `wh_nrv_assessments:approve` and `wh_transfer_orders:approve`.
- The `approvalStatus` value `PENDING_L{n}` is not a fixed enum, so an allowlisted enum filter cannot express it.
- Could not verify: whether exports are already audited (PRD §13.1, "exports are audited"). This is outside this slice.
- No code exists yet for the engine, so the C3 four-link chains and C8 grid/filter/export checks are not assessable.

## Referred to standards reviewer
- None.
## Fix record (2026-10-25)

| Finding | Files changed | Status |
|---|---|---|
| F-R32CA-001 | `issues/p8-25.md` (V500506 `blocked_reason`, CHECK replaced, release), `issues/p8-24.md`, `docs/contracts/accounting-handover.contract.md` (status inventory, `AHO-GRD-17`, new `AHO-T1-18`), `docs/DATA-MODEL.md`, `docs/BUILD-SPEC-SCREENS.md` WS-052, `issues/10-EPIC-p8.md` | done |
| F-R32CA-002 | `docs/contracts/document-approval.contract.md` §0.1 (a), `DAP-T1-04`; `issues/p8-30.md`; `docs/contracts/cycle-count.contract.md` `CCT-T1-03`; `docs/frd/FRD-STORES.md` R.3 | done |
| F-R32CA-003 | DAP `DAP-GRD-08`, new `-16`, `DAP-T3-02`; `issues/p8-30.md`; `docs/SCENARIO-CATALOGUE.md` WH-SC-743 | done |
| F-R32CA-004 | DAP new `DAP-GRD-15`, `-04`, `T2-03`; `issues/p8-30.md`; FRD-STORES FR-722; DATA-MODEL | done |
| F-R32CA-005 | DAP new `DAP-GRD-14`, §0.1; `issues/p8-30.md` (`required_authority`); FRD-STORES R.3 / FR-722; DATA-MODEL | done |
| F-R32CA-006 | DAP §0.1 (a)–(c), `DAP-UNR-03`; `issues/p8-30.md`; `issues/p8-04.md` (GRN excess wiring); `docs/contracts/grn-bill-match.contract.md` §7 | done (D-21 item 6) |
| F-R32CA-007 | DAP §0.1 (c)–(e) (every type, owner, no fallback); `issues/p8-08.md` (MRN wiring); `issues/p8-30.md`. `p8-11`/`p8-17`/`p8-18`/`p8-19` and `p10-*` wiring is in their files by their area fixers (D-21 item 6); §0.1 aligned to their codes and excluded actors | done (D-21 item 6) |
| F-R32CA-008 | DAP `DAP-T1-03`, §0.1 opening events + upgrade backfill; `issues/p8-30.md`; `docs/contracts/gate-entry.contract.md` (`GTE-T1-10a`, `-11`) | done |
| F-R32CA-009 | `issues/p8-23.md` (V500505 `warehouse_id`); AHO §5.1 site scope; DATA-MODEL; BUILD-SPEC WS-052 | done |
| F-R32CA-010 | DAP `DAP-GRD-03`, §0.1 excluded actors; `issues/p8-30.md` (`excluded_actor_ids`); CCT `CCT-GRD-07`; DATA-MODEL | done (D-21 item 6) |
| F-R32CA-011 | DAP §0.1 amendment model (`WHM_PRODUCTION_ORDER` = amend by revision, `PRO-T1-46` as written by the MFG fixer) | done |
| F-R32CA-012 | `issues/p8-23.md` §3, AHO `AHO-GRD-14`, FRD-STORES SPI row, `issues/p8-26.md` (`p9-17` / FRD-TRADE §12c already aligned by the trade fixer) | done (D-21 item 4) |
| F-R32CA-013 | `issues/p8-25.md` (header reuses v1 source fields, typed `documentPayload`); AHO `AHO-ENV-11`, new `-15` | done |
| F-R32CA-014 | `issues/p9-03.md`, `issues/p8-30.md` (`zeroLevelDefaults()`, `is_system_seed`); `docs/contracts/trade-approval-matrix.contract.md` new `TAM-T1-04a`; DATA-MODEL | done |
| F-R32CA-015 | DAP `DAP-T1-12` + §0.1 amendment model; `issues/p8-30.md`; TAM §7 | done |
| F-R32CA-016 | AHO A4, `AHO-T1-15`, new `AHO-GRD-18`; `issues/p8-23.md`; `issues/p8-24.md` | done (D-21 item 2) |
| F-R32CA-017 | `issues/p8-30.md` (`document_ref` live, idempotent number); `issues/p1-09.md`; FRD-STORES FR-735 | done (D-21 item 8) |
| F-R32CA-018 | `issues/p8-30.md`; DAP `DAP-UNR-05`; DATA-MODEL | done |
| F-R32CA-019 | DAP `DAP-T3-01` + §T3 note; `issues/p8-30.md` | done |
| F-R32CA-020 | DAP `DAP-T1-08a` (registered input watchers) | done |
| F-R32CA-021 | `issues/p0-13.md` (reuse built table, `V500604` released); FRD-STORES FR-736; DATA-MODEL; ledger 1-26, 3-21 | done |
| F-R32CA-022 | DAP `DAP-GRD-09` (endpoint list + exclusions); `issues/p8-30.md` | done |
| F-R32CA-023 | `docs/GLOBAL-SETTINGS-DECISIONS.md` (both QC keys registered at `false` / `NONE`); `p8-19` and FRD-STORES already aligned by the core-quality fixer | done (D-21 item 7) |
| F-R32CA-024 | `docs/GLOBAL-SETTINGS-DECISIONS.md` (10 keys registered, MFG keys prefixed, WhatsApp `SKIPPED_NO_TEMPLATE`); `issues/p8-30.md` (built key `requisition_second_approval_value`, outcome enum) | done |
| F-R32CA-025 | `issues/p1-03.md`; `docs/contracts/item-master.contract.md` `ITM-GRD-R32A-02`; FRD-STORES FR-731; GLOBAL-SETTINGS | done |
| F-R32CA-026 | `r32-ledger-approvals.tsv` rows 1-15, 1-16, 3-31, 3-34, 3-36, 3-38, 3-39 → AMEND; 1-26 reason corrected | done |
| F-R32CA-027 | `docs/contracts/trade-counterparty-evaluation.contract.md` new `TCE-OPEN-03` (deferred, owner named); ledger `BP-ppap` | done |
| F-R32CA-028 | `issues/p8-23.md` (built signature kept); AHO `AHO-RPT-03`, `AHO-GRD-14` | done |
| F-R32CA-029 | DAP `DAP-GRD-03` (kept code for every case); `issues/p8-30.md` | done |
| F-R32CA-030 | `issues/p9-03.md` (acceptance line and DoD marked superseded) | done |
| F-R32CA-031 | `docs/MODULE-INTEGRATION.md` §0 (band V621000–V621999 + 10 integration points); `issues/p8-23.md`; `docs/reviews/RETARGET-PROGRAM-STATUS.md` *Pending user items* (classic `CLAUDE.md` not edited) | done |
| F-R32CA-032 | `issues/p8-12.md` (the two R32 blocks merged above the definition of done) | done |

**Also delivered with this wave (`D-21` item 5):** new task `issues/p8-26.md` (issue TBD) — carrier of `CN-15`…`CN-22` incl. the gate-out and pre-ship guard SPIs, with implementers and acceptance; added to `issues/10-EPIC-p8.md` and `docs/IMPLEMENTATION-PLAN.md` §2.8.2 (P8 = 27 tasks; plan total 231 = 144 in P0–P6 + 87 in P7–P10, recounted from `issues/`); `docs/README.md`, `issues/README.md`, `issues/00-EPIC-master.md` counts brought to 231.
