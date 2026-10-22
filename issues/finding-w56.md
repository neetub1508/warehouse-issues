TITLE: [Warehouse] [Finding] W56 · Product promises exceed the evidence in some help text
LABELS: task,warehouse,warehouse-base
issue: 250
---
Part of #1 · Audit **warehouse-only readiness, 2026-10-01** · Finding **W56** · Module **`warehouse-base`** · Migrations **none allocated by this audit; reserve only if implementation requires one** · Screens **existing affected surfaces identified below; no new screen IDs allocated**

**Priority:** P2 (audit recommendation, not a programme phase). **Evidence class:** Documentation / commercial readiness. **Applies to:** Sales/help/training.

## Scope

### What happens / remaining gap

Help text includes numerical scan-accuracy claims and handheld references while warehouse mobile is explicitly absent. These are not measured product outcomes from this audit.

### Required work

Remove unsupported percentages and stale workflows; publish actual supported configuration and limitations.

### Boundary and ownership

This task tracks one finding from the warehouse-only audit. Complete the work or evidence needed for the affected existing workflow. Planning, forecasting, optimization and competitor feature work are excluded. Optional-module work applies only to the stated scope. Existing web-only/online-only decisions and removed-adapter decisions remain authoritative. An intentional limit is closed by enforcing/documenting the supported boundary unless a later explicit scope decision authorizes expansion.

## Evidence and affected code

[warehouse-base/frontend/src/components/warehouseCatalogues/WhbTaskTypeModal.tsx](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-base/frontend/src/components/warehouseCatalogues/WhbTaskTypeModal.tsx); [warehouse-base/INSTALL.md](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-base/INSTALL.md).

Audit code baseline: `neetub1508/classic@0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa`. Design baseline: `neetub1508/warehouse-issues@7b96725eb5850748cd94b2a784466cb16728a55d`.

Recheck the affected path at the implementation commit. “Reported” and “verification gap” do not mean a fresh runtime failure; “code-supported” does not mean a live reproduction. Preserve that distinction in the resolution.

## Requirements closed

The existing warehouse behavior described in Scope and Acceptance. This audit does not allocate new FR identifiers or claim any requirement already closed. Reuse the adopted requirements in related task sources; record exact applicable IDs when implementing instead of inventing them.

## Scenarios closed

No scenario is newly marked passed by creating this task. Execute the finding-specific acceptance below and affected refusal/retry paths. Record the current commit, supported module configuration, fixture, role, steps and actual results; reuse catalogue scenarios where they apply.

## Closes

Audit finding **W56** once its acceptance is met and evidence is linked. This issue does not automatically close or reopen earlier tasks.

## Implementation order and dependencies

**Recommended wave:** 3 — Prove complete release workflows and enabled integrations. This is a scheduling recommendation, not a requirement to finish every lower-wave issue before starting independent work.

### Before dependent implementation

- [W37 / #231](https://github.com/neetub1508/warehouse-issues/issues/231) — Supported web/online scope.
- [W38 / #232](https://github.com/neetub1508/warehouse-issues/issues/232) — Actual hardware evidence or explicit unverified claims.
- [W59 / #253](https://github.com/neetub1508/warehouse-issues/issues/253) — Optional feature boundaries.
- [W67 / #261](https://github.com/neetub1508/warehouse-issues/issues/261) — GS1 support boundary.
- [W68 / #262](https://github.com/neetub1508/warehouse-issues/issues/262) — Actual labour/weighing interfaces.

### Before final acceptance / closure

- No mandatory whole-issue completion dependency is identified. Meet this task’s acceptance and any applicable handoff/external prerequisites before closure.
- Preparatory analysis, fixtures and independent fixes can proceed while prerequisites are open. If a prerequisite is already satisfied in current code, link its commit/test evidence instead of waiting or rebuilding it.

### Setup, decisions and conditional dependencies

Remove unsupported claims immediately. Publish final measured figures only if W53 or specific device evidence supports them; waiting for a benchmark is not a reason to keep an unsupported percentage.

### Coordination and change control

- Earlier issues in “Related issues / existing implementation ownership” are ownership/history links, not automatic blockers. Preserve their accepted decisions and coordinate overlapping changes.
- A start dependency above can be a contract or test-environment handoff; it does not require closing the whole upstream issue. This avoids circular waits between implementation and acceptance tasks.
- Before implementation, confirm the applicable package, owner, schema/API/event contracts and required external fixtures. If a new blocker is discovered, add its issue link, exact deliverable, reason and applicability here and update the batch dependency index before dependent work proceeds.
- Record each prerequisite as satisfied with evidence, blocked with an owner, or not applicable with a scope reason. Do not silently bypass prerequisites or turn conditional features into universal blockers.

## Traps

- Follow `docs/DECISIONS.md` and its adopted settings amendment; older task wording is historical where superseded.
- Preserve stock/valuation lineage, tenant/site/owner scope and existing service ownership on affected paths.
- Do not interpret a missing runtime test as proof that the feature is missing. Verify before replacing working code.
- This includes a scope or documentation decision. Closure can be a verified correction or supported-boundary decision; it must not silently expand the product.

## Acceptance

- [ ] Dependency review completed: all applicable prerequisites above have linked evidence or explicit scope disposition; newly discovered blockers are recorded in this task and the batch index.
- [ ] Demo, help, proposals and install guide describe the same shipped workflow and measured claims.
- [ ] Verify current behavior against the cited evidence; record which concern is reproduced, already resolved, accepted by an existing decision, or still awaiting applicable integration evidence.
- [ ] Relevant flow check — **Barcode and supported web UX**: Real browser/scanner/printer network, keyboard use, error recovery, readable labels and truthful GS1 limits. Limit this task to its finding; link adjacent tasks for the rest.
- [ ] Run the targeted automated/runtime checks needed for this change, plus required module gates; retain actual results. A skipped integration test or code read is not a runtime pass.
- [ ] Update affected contract/help/runbook text and the related issue evidence so the supported behavior agrees across code and documentation.
- [ ] List remaining conditional dependencies explicitly; do not close an enabled workflow with unverified stock integrity, access control or external-state recovery.

<!-- warehouse-readiness-finding: 2026-10-01/W56 -->
