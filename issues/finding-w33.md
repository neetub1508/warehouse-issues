TITLE: [Warehouse] [Finding] W33 · Warehouse-only disaster recovery is not demonstrated
LABELS: task,warehouse,platform
issue: 227
---
Part of #1 · Audit **warehouse-only readiness, 2026-10-01** · Finding **W33** · Module **`platform`, `shared`** · Migrations **none allocated by this audit; reserve only if implementation requires one** · Screens **existing affected surfaces identified below; no new screen IDs allocated**

**Priority:** P0 (audit recommendation, not a programme phase). **Evidence class:** Verification / integration gap. **Applies to:** Every production deployment.

## Scope

### What happens / remaining gap

Backup and scratch restore exist; the scheduled verification found is accounting-owned. No warehouse-only restore/rebuild/value/hash-chain recovery evidence was established. PITR and achieved recovery objectives remain unproven.

### Required work

Run an isolated recovery drill for the actual deployment, including object attachments and replay state; agree measured recovery objectives.

### Boundary and ownership

This task tracks one finding from the warehouse-only audit. Complete the work or evidence needed for the affected existing workflow. Planning, forecasting, optimization and competitor feature work are excluded. Optional-module work applies only to the stated scope. Existing web-only/online-only decisions and removed-adapter decisions remain authoritative. An intentional limit is closed by enforcing/documenting the supported boundary unless a later explicit scope decision authorizes expansion.

## Evidence and affected code

[DatabaseBackupService.java:390](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/platform/backend/src/main/java/ai/platform/service/DatabaseBackupService.java#L390); [accounting-base/backend/src/main/java/ai/accountingbase/service/jobs/AccRestoreVerifyJob.java](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/accounting-base/backend/src/main/java/ai/accountingbase/service/jobs/AccRestoreVerifyJob.java); [shared/scripts/start.sh](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/shared/scripts/start.sh).

Audit code baseline: `neetub1508/classic@0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa`. Design baseline: `neetub1508/warehouse-issues@7b96725eb5850748cd94b2a784466cb16728a55d`.

Recheck the affected path at the implementation commit. “Reported” and “verification gap” do not mean a fresh runtime failure; “code-supported” does not mean a live reproduction. Preserve that distinction in the resolution.

## Requirements closed

The existing warehouse behavior described in Scope and Acceptance. This audit does not allocate new FR identifiers or claim any requirement already closed. Reuse the adopted requirements in related task sources; record exact applicable IDs when implementing instead of inventing them.

## Scenarios closed

No scenario is newly marked passed by creating this task. Execute the finding-specific acceptance below and affected refusal/retry paths. Record the current commit, supported module configuration, fixture, role, steps and actual results; reuse catalogue scenarios where they apply.

## Closes

Audit finding **W33** once its acceptance is met and evidence is linked. This issue does not automatically close or reopen earlier tasks.

## Implementation order and dependencies

**Recommended wave:** 3 — Prove complete release workflows and enabled integrations. This is a scheduling recommendation, not a requirement to finish every lower-wave issue before starting independent work.

### Before dependent implementation

- [W54 / #248](https://github.com/neetub1508/warehouse-issues/issues/248) — Coordinated recovery procedure, retention and external replay policy.
- [W40 / #234](https://github.com/neetub1508/warehouse-issues/issues/234) — Known reproducible standalone install/upgrade configuration.

### Before final acceptance / closure

- Required upstream deliverables/evidence: [W34 / #228](https://github.com/neetub1508/warehouse-issues/issues/228), [W40 / #234](https://github.com/neetub1508/warehouse-issues/issues/234), [W54 / #248](https://github.com/neetub1508/warehouse-issues/issues/248). Confirm the relevant deliverable is accepted; an issue’s CLOSED status alone is not proof.
- Preparatory analysis, fixtures and independent fixes can proceed while prerequisites are open. If a prerequisite is already satisfied in current code, link its commit/test evidence instead of waiting or rebuilding it.

### Setup, decisions and conditional dependencies

External prerequisite: isolated restore target, sanitized representative backup, object copies/keys and agreed recovery objectives. No restore into a live customer database.

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
- [ ] Recovered stock, valuation and hash chain reconcile to known checkpoints; no duplicate external execution; recovery duration/data loss recorded.
- [ ] Verify current behavior against the cited evidence; record which concern is reproduced, already resolved, accepted by an existing decision, or still awaiting applicable integration evidence.
- [ ] Relevant flow check — **Backup and incident recovery**: Isolated restore of DB and objects, ledger/hash/value tie-out, outbox reconciliation and measured recovery time. Limit this task to its finding; link adjacent tasks for the rest.
- [ ] Run the targeted automated/runtime checks needed for this change, plus required module gates; retain actual results. A skipped integration test or code read is not a runtime pass.
- [ ] Update affected contract/help/runbook text and the related issue evidence so the supported behavior agrees across code and documentation.
- [ ] List remaining conditional dependencies explicitly; do not close an enabled workflow with unverified stock integrity, access control or external-state recovery.

<!-- warehouse-readiness-finding: 2026-10-01/W33 -->
