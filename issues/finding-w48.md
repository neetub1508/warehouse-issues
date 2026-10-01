TITLE: [Warehouse] [Finding] W48 · 3PL billing needs an independent cycle-level reconciliation
LABELS: task,warehouse,warehouse-3pl
issue: 242
---
Part of #1 · Audit **warehouse-only readiness, 2026-10-01** · Finding **W48** · Module **`warehouse-3pl`** · Migrations **none allocated by this audit; reserve only if implementation requires one** · Screens **existing affected surfaces identified below; no new screen IDs allocated**

**Priority:** P1 (audit recommendation, not a programme phase). **Evidence class:** Verification gap. **Applies to:** 3PL customers.

## Scope

### What happens / remaining gap

Unit/contract tests passed in the current backend gate, but database storage billing and a complete client billing cycle were not demonstrated in this audit. Rate escalation/SLA credits/profitability are separate deferred capabilities.

### Required work

Run occupancy/handling/VAS/rate-version/dispute/credit scenarios against independently calculated results.

### Boundary and ownership

This task tracks one finding from the warehouse-only audit. Complete the work or evidence needed for the affected existing workflow. Planning, forecasting, optimization and competitor feature work are excluded. Optional-module work applies only to the stated scope. Existing web-only/online-only decisions and removed-adapter decisions remain authoritative. An intentional limit is closed by enforcing/documenting the supported boundary unless a later explicit scope decision authorizes expansion.

## Evidence and affected code

[warehouse-3pl/backend/src/test/java/ai/warehouse3pl/service/wh3plstoragebilling/Wh3plStorageBillingSnapshotDayIntegrationTest.java](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-3pl/backend/src/test/java/ai/warehouse3pl/service/wh3plstoragebilling/Wh3plStorageBillingSnapshotDayIntegrationTest.java); [#122](https://github.com/neetub1508/warehouse-issues/issues/122).

Audit code baseline: `neetub1508/classic@0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa`. Design baseline: `neetub1508/warehouse-issues@7b96725eb5850748cd94b2a784466cb16728a55d`.

Recheck the affected path at the implementation commit. “Reported” and “verification gap” do not mean a fresh runtime failure; “code-supported” does not mean a live reproduction. Preserve that distinction in the resolution.

## Requirements closed

The existing warehouse behavior described in Scope and Acceptance. This audit does not allocate new FR identifiers or claim any requirement already closed. Reuse the adopted requirements in related task sources; record exact applicable IDs when implementing instead of inventing them.

## Scenarios closed

No scenario is newly marked passed by creating this task. Execute the finding-specific acceptance below and affected refusal/retry paths. Record the current commit, supported module configuration, fixture, role, steps and actual results; reuse catalogue scenarios where they apply.

## Closes

Audit finding **W48** once its acceptance is met and evidence is linked. This issue does not automatically close or reopen earlier tasks.

### Related issues / existing implementation ownership

- #122 — [Warehouse] P6-07 · 3PL v3 — rate escalation as a new version, the SLA credit as a negative billable event, and client profitability.

These links preserve earlier ownership/history. Coordinate overlapping implementation in one change and link both issues; do not build a second competing implementation. Closed duplicates remain closed.

## Traps

- Follow `docs/DECISIONS.md` and its adopted settings amendment; older task wording is historical where superseded.
- Preserve stock/valuation lineage, tenant/site/owner scope and existing service ownership on affected paths.
- Do not interpret a missing runtime test as proof that the feature is missing. Verify before replacing working code.

## Acceptance

- [ ] One full bill reconciles to stock snapshots and events, with owner isolation and no duplicate charges after retry.
- [ ] Verify current behavior against the cited evidence; record which concern is reproduced, already resolved, accepted by an existing decision, or still awaiting applicable integration evidence.
- [ ] Relevant flow check — **3PL billing/client lifecycle**: Full independent bill, rates/storage days, retries, credits, offboarding and client isolation. Limit this task to its finding; link adjacent tasks for the rest.
- [ ] Run the targeted automated/runtime checks needed for this change, plus required module gates; retain actual results. A skipped integration test or code read is not a runtime pass.
- [ ] Update affected contract/help/runbook text and the related issue evidence so the supported behavior agrees across code and documentation.
- [ ] List remaining conditional dependencies explicitly; do not close an enabled workflow with unverified stock integrity, access control or external-state recovery.

<!-- warehouse-readiness-finding: 2026-10-01/W48 -->
