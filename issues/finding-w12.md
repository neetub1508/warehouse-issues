TITLE: [Warehouse] [Finding] W12 · RMA expiry has no scheduled transition found
LABELS: task,warehouse,warehouse-base
issue: 206
---
Part of #1 · Audit **warehouse-only readiness, 2026-10-01** · Finding **W12** · Module **`warehouse-base`** · Migrations **none allocated by this audit; reserve only if implementation requires one** · Screens **existing affected surfaces identified below; no new screen IDs allocated**

**Priority:** P1 (audit recommendation, not a programme phase). **Evidence class:** Code-supported. **Applies to:** Returns/RMA.

## Scope

### What happens / remaining gap

Expiry is enforced when matching a return, but the scheduled status transition remains marked owed and no RMA expiry job was found.

### Required work

Implement the site-date job using existing job infrastructure and idempotent transitions.

### Boundary and ownership

This task tracks one finding from the warehouse-only audit. Complete the work or evidence needed for the affected existing workflow. Planning, forecasting, optimization and competitor feature work are excluded. Optional-module work applies only to the stated scope. Existing web-only/online-only decisions and removed-adapter decisions remain authoritative. An intentional limit is closed by enforcing/documenting the supported boundary unless a later explicit scope decision authorizes expansion.

## Evidence and affected code

[#165](https://github.com/neetub1508/warehouse-issues/issues/165); [warehouse-base/docs/DATED-OBLIGATION-REGISTER.md](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-base/docs/DATED-OBLIGATION-REGISTER.md).

Audit code baseline: `neetub1508/classic@0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa`. Design baseline: `neetub1508/warehouse-issues@7b96725eb5850748cd94b2a784466cb16728a55d`.

Recheck the affected path at the implementation commit. “Reported” and “verification gap” do not mean a fresh runtime failure; “code-supported” does not mean a live reproduction. Preserve that distinction in the resolution.

## Requirements closed

The existing warehouse behavior described in Scope and Acceptance. This audit does not allocate new FR identifiers or claim any requirement already closed. Reuse the adopted requirements in related task sources; record exact applicable IDs when implementing instead of inventing them.

## Scenarios closed

No scenario is newly marked passed by creating this task. Execute the finding-specific acceptance below and affected refusal/retry paths. Record the current commit, supported module configuration, fixture, role, steps and actual results; reuse catalogue scenarios where they apply.

## Closes

Audit finding **W12** once its acceptance is met and evidence is linked. This issue does not automatically close or reopen earlier tasks.

### Related issues / existing implementation ownership

- #165 — [Warehouse] P2-12 follow-up · RMA expiry job (RJ-012) — open RMAs expire on the site's date.

These links preserve earlier ownership/history. Coordinate overlapping implementation in one change and link both issues; do not build a second competing implementation. Closed duplicates remain closed.

## Implementation order and dependencies

**Recommended wave:** 1 — Protect stock, value and core operator flows. This is a scheduling recommendation, not a requirement to finish every lower-wave issue before starting independent work.

### Before dependent implementation

- No mandatory start dependency on another finding is identified. Begin current-code verification and this task’s scoped work immediately, subject to the setup/decision prerequisites below.

### Before final acceptance / closure

- Required upstream deliverables/evidence: [W34 / #228](https://github.com/neetub1508/warehouse-issues/issues/228). Confirm the relevant deliverable is accepted; an issue’s CLOSED status alone is not proof.
- Preparatory analysis, fixtures and independent fixes can proceed while prerequisites are open. If a prerequisite is already satisfied in current code, link its commit/test evidence instead of waiting or rebuilding it.

### Setup, decisions and conditional dependencies

Use existing site-date/job infrastructure; agree expiry boundary and idempotent transition. Coordinate the recovery drill with W52.

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
- [ ] Expired OPEN/APPROVED RMAs become EXPIRED once; the list and receipt validation agree across timezones.
- [ ] Verify current behavior against the cited evidence; record which concern is reproduced, already resolved, accepted by an existing decision, or still awaiting applicable integration evidence.
- [ ] Relevant flow check — **Returns and RMA**: Expired RMA, matching origin, partial return, QC outcome, cost lineage and weighing behavior. Limit this task to its finding; link adjacent tasks for the rest.
- [ ] Run the targeted automated/runtime checks needed for this change, plus required module gates; retain actual results. A skipped integration test or code read is not a runtime pass.
- [ ] Update affected contract/help/runbook text and the related issue evidence so the supported behavior agrees across code and documentation.
- [ ] List remaining conditional dependencies explicitly; do not close an enabled workflow with unverified stock integrity, access control or external-state recovery.

## Earlier report detail (reference, verify against current code)

The following preserves the original observations/reproduction details. It is historical context; the Scope and adopted decisions above govern implementation.

<details>
<summary>Source issue #165</summary>

Follow-up from #87 (P2-12 Returns v1) · Module **`warehouse-base`** (job catalogue) + **`warehouse`** · Migrations: none expected (reuse the existing job-run tables)

## Scope
An RMA past its `expiry_date` is already refused when a return is matched to it (`RETURN_RMA_EXPIRED`, site date). What is missing is the **scheduled job (RJ-012)** that moves an open RMA to **EXPIRED** on the site's date and stamps `wh_rmas.expired_at`, so the RMA list shows the true status without anyone pressing Expire.

- Register an `RMA_EXPIRY` entry in `WhbJobCatalogue` (warehouse-base) — a draft descriptor was prepared during #87.
- The warehouse job implementation expires every OPEN/APPROVED RMA whose `expiry_date` < site today, idempotently, one job-run row per site.
- `DATED-OBLIGATION-REGISTER.md`: `wh_rmas.expiry_date` moves from `owed` to enforced by this job.

## Acceptance
1. An RMA whose expiry date has passed shows EXPIRED after the job runs, with the expiry stamp set; running the job twice changes nothing more.
2. An RMA expiring today (site time) is not expired until tomorrow.

</details>

<!-- warehouse-readiness-finding: 2026-10-01/W12 -->
