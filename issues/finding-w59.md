TITLE: [Warehouse] [Finding] W59 · Advanced operational features must remain explicitly outside the basic offer
LABELS: task,warehouse,warehouse-base
issue: 253
---
Part of #1 · Audit **warehouse-only readiness, 2026-10-01** · Finding **W59** · Module **`warehouse-base`, `warehouse`** · Migrations **none allocated by this audit; reserve only if implementation requires one** · Screens **existing affected surfaces identified below; no new screen IDs allocated**

**Priority:** P2 (audit recommendation, not a programme phase). **Evidence class:** Intentional scope limit. **Applies to:** Customer/package selection.

## Scope

### What happens / remaining gap

Engineered labor/incentive pay, robotics control, supplier scorecard, logistics, dashboard expansion, accessories absorption and manufacturing routings are deferred or deliberately outside scope. They are not universal release blockers.

### Required work

Publish the supported warehouse-only package and extension boundaries; do not quietly rebuild removed adapters or promise future work as shipped.

### Boundary and ownership

This task tracks one finding from the warehouse-only audit. Complete the work or evidence needed for the affected existing workflow. Planning, forecasting, optimization and competitor feature work are excluded. Optional-module work applies only to the stated scope. Existing web-only/online-only decisions and removed-adapter decisions remain authoritative. An intentional limit is closed by enforcing/documenting the supported boundary unless a later explicit scope decision authorizes expansion.

## Evidence and affected code

[#103](https://github.com/neetub1508/warehouse-issues/issues/103); [#109](https://github.com/neetub1508/warehouse-issues/issues/109); [#112](https://github.com/neetub1508/warehouse-issues/issues/112); [#131](https://github.com/neetub1508/warehouse-issues/issues/131); [#138](https://github.com/neetub1508/warehouse-issues/issues/138); [#142](https://github.com/neetub1508/warehouse-issues/issues/142); [#144](https://github.com/neetub1508/warehouse-issues/issues/144).

Audit code baseline: `neetub1508/classic@0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa`. Design baseline: `neetub1508/warehouse-issues@7b96725eb5850748cd94b2a784466cb16728a55d`.

Recheck the affected path at the implementation commit. “Reported” and “verification gap” do not mean a fresh runtime failure; “code-supported” does not mean a live reproduction. Preserve that distinction in the resolution.

## Requirements closed

The existing warehouse behavior described in Scope and Acceptance. This audit does not allocate new FR identifiers or claim any requirement already closed. Reuse the adopted requirements in related task sources; record exact applicable IDs when implementing instead of inventing them.

## Scenarios closed

No scenario is newly marked passed by creating this task. Execute the finding-specific acceptance below and affected refusal/retry paths. Record the current commit, supported module configuration, fixture, role, steps and actual results; reuse catalogue scenarios where they apply.

## Closes

Audit finding **W59** once its acceptance is met and evidence is linked. This issue does not automatically close or reopen earlier tasks.

### Related issues / existing implementation ownership

- #103 — [Warehouse] P6-03 · Measured labour, not engineered standards — and the refusal is the requirement.
- #109 — [Warehouse] P6-04 · Automation, AS/RS and robotics through a published task-event contract and the movement port — an interface, never a control layer.
- #112 — [Warehouse] P6-05 · Receipt facts emitted as evidence — and the supplier scorecard is deliberately not built here.
- #131 — [Warehouse] P6-08 · The `logistics` module — trips, ePOD and freight settlement, posting through the port, with zero commits to `warehouse-base`.
- #138 — [Warehouse] P6-10 · The real-time operations dashboard on the platform widget framework.
- #142 — [Warehouse] P6-11 · The accessories absorption path, stated in advance so it is a decision rather than a discovery.
- #144 — [Warehouse] P6-12 · Multi-level BOM with routings is not built — recorded so the refusal is a decision with a way back in.

These links preserve earlier ownership/history. Coordinate overlapping implementation in one change and link both issues; do not build a second competing implementation. Closed duplicates remain closed.

## Implementation order and dependencies

**Recommended wave:** 0 — Establish scope/contracts and repair verification infrastructure. This is a scheduling recommendation, not a requirement to finish every lower-wave issue before starting independent work.

### Before dependent implementation

- No mandatory start dependency on another finding is identified. Begin current-code verification and this task’s scoped work immediately, subject to the setup/decision prerequisites below.

### Before final acceptance / closure

- No mandatory whole-issue completion dependency is identified. Meet this task’s acceptance and any applicable handoff/external prerequisites before closure.
- Preparatory analysis, fixtures and independent fixes can proceed while prerequisites are open. If a prerequisite is already satisfied in current code, link its commit/test evidence instead of waiting or rebuilding it.

### Setup, decisions and conditional dependencies

Confirm the existing warehouse offer and excluded advanced/removed vertical capabilities; no reinstatement of excluded adapters or future modules.

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
- [ ] Customer requirements are mapped to supported workflows or explicit exclusions before go-live.
- [ ] Verify current behavior against the cited evidence; record which concern is reproduced, already resolved, accepted by an existing decision, or still awaiting applicable integration evidence.
- [ ] Run the targeted automated/runtime checks needed for this change, plus required module gates; retain actual results. A skipped integration test or code read is not a runtime pass.
- [ ] Update affected contract/help/runbook text and the related issue evidence so the supported behavior agrees across code and documentation.
- [ ] List remaining conditional dependencies explicitly; do not close an enabled workflow with unverified stock integrity, access control or external-state recovery.

<!-- warehouse-readiness-finding: 2026-10-01/W59 -->
