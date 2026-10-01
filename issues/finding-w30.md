TITLE: [Warehouse] [Finding] W30 · Site-access denial reports misleading permission
LABELS: task,warehouse,platform
issue: 224
---
Part of #1 · Audit **warehouse-only readiness, 2026-10-01** · Finding **W30** · Module **`platform`** · Migrations **none allocated by this audit; reserve only if implementation requires one** · Screens **existing affected surfaces identified below; no new screen IDs allocated**

**Priority:** P2 (audit recommendation, not a programme phase). **Evidence class:** Reported. **Applies to:** All scoped operations.

## Scope

### What happens / remaining gap

The recorded platform handler substitutes endpoint permissions for site-scope failure detail. This is misleading diagnostics, not proof of unauthorized access.

### Required work

Preserve safe structured scope-denial codes and messages.

### Boundary and ownership

This task tracks one finding from the warehouse-only audit. Complete the work or evidence needed for the affected existing workflow. Planning, forecasting, optimization and competitor feature work are excluded. Optional-module work applies only to the stated scope. Existing web-only/online-only decisions and removed-adapter decisions remain authoritative. An intentional limit is closed by enforcing/documenting the supported boundary unless a later explicit scope decision authorizes expansion.

## Evidence and affected code

[#187](https://github.com/neetub1508/warehouse-issues/issues/187); [GlobalExceptionHandler.java:187](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/platform/backend/src/main/java/ai/platform/exception/GlobalExceptionHandler.java#L187).

Audit code baseline: `neetub1508/classic@0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa`. Design baseline: `neetub1508/warehouse-issues@7b96725eb5850748cd94b2a784466cb16728a55d`.

Recheck the affected path at the implementation commit. “Reported” and “verification gap” do not mean a fresh runtime failure; “code-supported” does not mean a live reproduction. Preserve that distinction in the resolution.

## Requirements closed

The existing warehouse behavior described in Scope and Acceptance. This audit does not allocate new FR identifiers or claim any requirement already closed. Reuse the adopted requirements in related task sources; record exact applicable IDs when implementing instead of inventing them.

## Scenarios closed

No scenario is newly marked passed by creating this task. Execute the finding-specific acceptance below and affected refusal/retry paths. Record the current commit, supported module configuration, fixture, role, steps and actual results; reuse catalogue scenarios where they apply.

## Closes

Audit finding **W30** once its acceptance is met and evidence is linked. This issue does not automatically close or reopen earlier tasks.

### Related issues / existing implementation ownership

- #187 — [Warehouse] Site-access 403s name the wrong permission (shared requirePermitted).

These links preserve earlier ownership/history. Coordinate overlapping implementation in one change and link both issues; do not build a second competing implementation. Closed duplicates remain closed.

## Implementation order and dependencies

**Recommended wave:** 1 — Protect stock, value and core operator flows. This is a scheduling recommendation, not a requirement to finish every lower-wave issue before starting independent work.

### Before dependent implementation

- No mandatory start dependency on another finding is identified. Begin current-code verification and this task’s scoped work immediately, subject to the setup/decision prerequisites below.

### Before final acceptance / closure

- No mandatory whole-issue completion dependency is identified. Meet this task’s acceptance and any applicable handoff/external prerequisites before closure.
- Preparatory analysis, fixtures and independent fixes can proceed while prerequisites are open. If a prerequisite is already satisfied in current code, link its commit/test evidence instead of waiting or rebuilding it.

### Setup, decisions and conditional dependencies

Shared exception-mapping owner must distinguish access-scope denial from missing permission without leaking foreign resource details.

### Coordination and change control

- Earlier issues in “Related issues / existing implementation ownership” are ownership/history links, not automatic blockers. Preserve their accepted decisions and coordinate overlapping changes.
- A start dependency above can be a contract or test-environment handoff; it does not require closing the whole upstream issue. This avoids circular waits between implementation and acceptance tasks.
- Before implementation, confirm the applicable package, owner, schema/API/event contracts and required external fixtures. If a new blocker is discovered, add its issue link, exact deliverable, reason and applicability here and update the batch dependency index before dependent work proceeds.
- Record each prerequisite as satisfied with evidence, blocked with an owner, or not applicable with a scope reason. Do not silently bypass prerequisites or turn conditional features into universal blockers.

## Traps

- Follow `docs/DECISIONS.md` and its adopted settings amendment; older task wording is historical where superseded.
- Preserve stock/valuation lineage, tenant/site/owner scope and existing service ownership on affected paths.
- Do not interpret a missing runtime test as proof that the feature is missing. Verify before replacing working code.

## Acceptance

- [ ] Dependency review completed: all applicable prerequisites above have linked evidence or explicit scope disposition; newly discovered blockers are recorded in this task and the batch index.
- [ ] User can distinguish lacking endpoint permission from lacking access to the selected site.
- [ ] Verify current behavior against the cited evidence; record which concern is reproduced, already resolved, accepted by an existing decision, or still awaiting applicable integration evidence.
- [ ] Run the targeted automated/runtime checks needed for this change, plus required module gates; retain actual results. A skipped integration test or code read is not a runtime pass.
- [ ] Update affected contract/help/runbook text and the related issue evidence so the supported behavior agrees across code and documentation.
- [ ] List remaining conditional dependencies explicitly; do not close an enabled workflow with unverified stock integrity, access control or external-state recovery.

## Earlier report detail (reference, verify against current code)

The following preserves the original observations/reproduction details. It is historical context; the Scope and adopted decisions above govern implementation.

<details>
<summary>Source issue #187</summary>

**What's wrong**
When a warehouse user is refused because of site access, the 403 response names the wrong permission. The platform `GlobalExceptionHandler.handleAccessDenied` throws away the real message of every `AccessDeniedException` and reports the endpoint's `@PreAuthorize` list instead — usually a permission the user already holds.

**Where it happens**
Every site check that goes through `WhbWarehouseScopeService.requirePermitted` (warehouse-base), e.g. labour-task start, weighing instruments/records, return gradings, marketplace claims, obsolescence returns, return receipts and COGS recognitions, plus WhbJobRunService, WhbNumberSeriesQueryService, WhbChainVerificationService, WhbMovementPortService and WhPrintTemplateQueryService.

**Already fixed**
The three wave-2 R2 business-rule refusals now return coded 403s (commit 0805cb321b): WEIGHING_DEVICE_AUTHORITY_REQUIRED, LABOUR_TIMER_NOT_OWN and NRV_SITE_NOT_PERMITTED.

**Suggested fix**
Make `requirePermitted` throw the module's coded 403 `BusinessException`, as the NRV self-approval refusal does. It's one change and covers every caller. Leave the platform handler alone: it's shared with every module.

Found by the R2 tester (warehouse P5 wave 2). Repro: classic `.claude/tasks/reports/warehouse-p5-R2/tester.md`.

</details>

<!-- warehouse-readiness-finding: 2026-10-01/W30 -->
