TITLE: [Warehouse] [Finding] W71 · Closed receiving and access work contains unresolved smaller obligations
LABELS: task,warehouse,warehouse-base
issue: 265
---
Part of #1 · Audit **warehouse-only readiness, 2026-10-01** · Finding **W71** · Module **`warehouse-base`, `warehouse`** · Migrations **none allocated by this audit; reserve only if implementation requires one** · Screens **existing affected surfaces identified below; no new screen IDs allocated**

**Priority:** P2 (audit recommendation, not a programme phase). **Evidence class:** Reported closed-issue carry-forward. **Applies to:** Receiving documents and access model.

## Scope

### What happens / remaining gap

Receiving closure records GRN documents deferred without an owner. Access closure records access_level as inert for reads with write semantics undecided. Current advertised attachment and grant behavior requires reconciliation.

### Required work

Confirm whether these are still promised requirements; assign implementation or explicitly remove the unsupported promise.

### Boundary and ownership

This task tracks one finding from the warehouse-only audit. Complete the work or evidence needed for the affected existing workflow. Planning, forecasting, optimization and competitor feature work are excluded. Optional-module work applies only to the stated scope. Existing web-only/online-only decisions and removed-adapter decisions remain authoritative. An intentional limit is closed by enforcing/documenting the supported boundary unless a later explicit scope decision authorizes expansion.

## Evidence and affected code

[#113](https://github.com/neetub1508/warehouse-issues/issues/113); [#137](https://github.com/neetub1508/warehouse-issues/issues/137).

Audit code baseline: `neetub1508/classic@0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa`. Design baseline: `neetub1508/warehouse-issues@7b96725eb5850748cd94b2a784466cb16728a55d`.

Recheck the affected path at the implementation commit. “Reported” and “verification gap” do not mean a fresh runtime failure; “code-supported” does not mean a live reproduction. Preserve that distinction in the resolution.

## Requirements closed

The existing warehouse behavior described in Scope and Acceptance. This audit does not allocate new FR identifiers or claim any requirement already closed. Reuse the adopted requirements in related task sources; record exact applicable IDs when implementing instead of inventing them.

## Scenarios closed

No scenario is newly marked passed by creating this task. Execute the finding-specific acceptance below and affected refusal/retry paths. Record the current commit, supported module configuration, fixture, role, steps and actual results; reuse catalogue scenarios where they apply.

## Closes

Audit finding **W71** once its acceptance is met and evidence is linked. This issue does not automatically close or reopen earlier tasks.

### Related issues / existing implementation ownership

- #113 — [Warehouse] P1-13 · Receiving — sessions, GRNs, blind receipt, and receiving behaviour as configuration.
- #137 — [Warehouse] P1-18 · Warehouse-scoped user access in every management query's WHERE clause.

These links preserve earlier ownership/history. Coordinate overlapping implementation in one change and link both issues; do not build a second competing implementation. Closed duplicates remain closed.

## Traps

- Follow `docs/DECISIONS.md` and its adopted settings amendment; older task wording is historical where superseded.
- Preserve stock/valuation lineage, tenant/site/owner scope and existing service ownership on affected paths.
- Do not interpret a missing runtime test as proof that the feature is missing. Verify before replacing working code.

## Acceptance

- [ ] Receiving documents have a supported governed path; exposed access levels have clear enforced semantics rather than inert choices.
- [ ] Verify current behavior against the cited evidence; record which concern is reproduced, already resolved, accepted by an existing decision, or still awaiting applicable integration evidence.
- [ ] Relevant flow check — **Site/owner/item setup**: Create masters and required associations through UI; effective dates, invalid setups and per-site sourcing behave consistently. Limit this task to its finding; link adjacent tasks for the rest.
- [ ] Relevant flow check — **Purchase and receipt**: Partial/over/foreign-currency receipt, duplicate submission, lot/serial/UOM and receipt evidence. Limit this task to its finding; link adjacent tasks for the rest.
- [ ] Relevant flow check — **Permissions and evidence**: Cross-site/owner direct IDs, exports, attachments, public links, revoked grants and cost visibility. Limit this task to its finding; link adjacent tasks for the rest.
- [ ] Run the targeted automated/runtime checks needed for this change, plus required module gates; retain actual results. A skipped integration test or code read is not a runtime pass.
- [ ] Update affected contract/help/runbook text and the related issue evidence so the supported behavior agrees across code and documentation.
- [ ] List remaining conditional dependencies explicitly; do not close an enabled workflow with unverified stock integrity, access control or external-state recovery.

<!-- warehouse-readiness-finding: 2026-10-01/W71 -->
