TITLE: [Warehouse] [Finding] W49 · Permissions need adversarial workflow tests, not only annotations
LABELS: task,warehouse
issue: 243
---
Part of #1 · Audit **warehouse-only readiness, 2026-10-01** · Finding **W49** · Module **`warehouse`** · Migrations **none allocated by this audit; reserve only if implementation requires one** · Screens **existing affected surfaces identified below; no new screen IDs allocated**

**Priority:** P1 (audit recommendation, not a programme phase). **Evidence class:** Verification gap. **Applies to:** Every deployment.

## Scope

### What happens / remaining gap

Scope architecture tests pass, but complete cross-site/owner access and indirect export/attachment/public-link behavior were not exercised against deployed roles.

### Required work

Test ordinary operator, supervisor, finance and external-user roles across reads/writes/exports/links.

### Boundary and ownership

This task tracks one finding from the warehouse-only audit. Complete the work or evidence needed for the affected existing workflow. Planning, forecasting, optimization and competitor feature work are excluded. Optional-module work applies only to the stated scope. Existing web-only/online-only decisions and removed-adapter decisions remain authoritative. An intentional limit is closed by enforcing/documenting the supported boundary unless a later explicit scope decision authorizes expansion.

## Evidence and affected code

[warehouse/backend/src/test/java/ai/warehouse/architecture/WhWarehouseScopeContractTest.java](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse/backend/src/test/java/ai/warehouse/architecture/WhWarehouseScopeContractTest.java); [warehouse/backend/src/test/java/ai/warehouse/architecture/WhOwnerScopeContractTest.java](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse/backend/src/test/java/ai/warehouse/architecture/WhOwnerScopeContractTest.java).

Audit code baseline: `neetub1508/classic@0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa`. Design baseline: `neetub1508/warehouse-issues@7b96725eb5850748cd94b2a784466cb16728a55d`.

Recheck the affected path at the implementation commit. “Reported” and “verification gap” do not mean a fresh runtime failure; “code-supported” does not mean a live reproduction. Preserve that distinction in the resolution.

## Requirements closed

The existing warehouse behavior described in Scope and Acceptance. This audit does not allocate new FR identifiers or claim any requirement already closed. Reuse the adopted requirements in related task sources; record exact applicable IDs when implementing instead of inventing them.

## Scenarios closed

No scenario is newly marked passed by creating this task. Execute the finding-specific acceptance below and affected refusal/retry paths. Record the current commit, supported module configuration, fixture, role, steps and actual results; reuse catalogue scenarios where they apply.

## Closes

Audit finding **W49** once its acceptance is met and evidence is linked. This issue does not automatically close or reopen earlier tasks.

## Implementation order and dependencies

**Recommended wave:** 2 — Complete workflow contracts and operational safeguards. This is a scheduling recommendation, not a requirement to finish every lower-wave issue before starting independent work.

### Before dependent implementation

- No mandatory start dependency on another finding is identified. Begin current-code verification and this task’s scoped work immediately, subject to the setup/decision prerequisites below.

### Before final acceptance / closure

- Required upstream deliverables/evidence: [W13 / #207](https://github.com/neetub1508/warehouse-issues/issues/207), [W24 / #218](https://github.com/neetub1508/warehouse-issues/issues/218), [W30 / #224](https://github.com/neetub1508/warehouse-issues/issues/224), [W65 / #259](https://github.com/neetub1508/warehouse-issues/issues/259), [W71 / #265](https://github.com/neetub1508/warehouse-issues/issues/265). Confirm the relevant deliverable is accepted; an issue’s CLOSED status alone is not proof.
- Preparatory analysis, fixtures and independent fixes can proceed while prerequisites are open. If a prerequisite is already satisfied in current code, link its commit/test evidence instead of waiting or rebuilding it.

### Setup, decisions and conditional dependencies

Create adversarial role/site/owner fixtures now. Each optional endpoint/connector is included only when enabled; record N/A explicitly. Final acceptance includes repaired delete, reporting, grant and assignment paths.

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
- [ ] Foreign IDs, changed filters, stale grants and bulk actions do not widen scope; legitimate transfer receipt exceptions remain narrow.
- [ ] Verify current behavior against the cited evidence; record which concern is reproduced, already resolved, accepted by an existing decision, or still awaiting applicable integration evidence.
- [ ] Relevant flow check — **Reservation and allocation**: Concurrent orders cannot over-allocate; expiry, hold, cancellation and supersession preserve requested/fulfilled lineage. Limit this task to its finding; link adjacent tasks for the rest.
- [ ] Relevant flow check — **Inter-site transfers**: Dispatch/in-transit/partial receipt/loss/reversal, narrow receiving permissions and source valuation preserved. Limit this task to its finding; link adjacent tasks for the rest.
- [ ] Relevant flow check — **Permissions and evidence**: Cross-site/owner direct IDs, exports, attachments, public links, revoked grants and cost visibility. Limit this task to its finding; link adjacent tasks for the rest.
- [ ] Run the targeted automated/runtime checks needed for this change, plus required module gates; retain actual results. A skipped integration test or code read is not a runtime pass.
- [ ] Update affected contract/help/runbook text and the related issue evidence so the supported behavior agrees across code and documentation.
- [ ] List remaining conditional dependencies explicitly; do not close an enabled workflow with unverified stock integrity, access control or external-state recovery.

<!-- warehouse-readiness-finding: 2026-10-01/W49 -->
