TITLE: [Warehouse] [Finding] W10 · Accounting-integrated mode lacks an installed implementation
LABELS: task,warehouse,warehouse-base
issue: 204
---
Part of #1 · Audit **warehouse-only readiness, 2026-10-01** · Finding **W10** · Module **`warehouse-base`** · Migrations **none allocated by this audit; reserve only if implementation requires one** · Screens **existing affected surfaces identified below; no new screen IDs allocated**

**Priority:** P1 (audit recommendation, not a programme phase). **Evidence class:** Code-supported. **Applies to:** Only accounting-integrated customers.

## Scope

### What happens / remaining gap

No production implementations were found for these interfaces. Standalone valuation remains supported; an integrated accounting promise is not established.

### Required work

Assign the adapter owner and prove handover/reconciliation before enabling integrated mode.

### Boundary and ownership

This task tracks one finding from the warehouse-only audit. Complete the work or evidence needed for the affected existing workflow. Planning, forecasting, optimization and competitor feature work are excluded. Optional-module work applies only to the stated scope. Existing web-only/online-only decisions and removed-adapter decisions remain authoritative. An intentional limit is closed by enforcing/documenting the supported boundary unless a later explicit scope decision authorizes expansion.

## Evidence and affected code

[#174](https://github.com/neetub1508/warehouse-issues/issues/174); [#175](https://github.com/neetub1508/warehouse-issues/issues/175); [WhbAccountingHandoverSink.java:1](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-base/backend/src/main/java/ai/warehousebase/service/accounting/WhbAccountingHandoverSink.java#L1); [WhbGlBalanceProvider.java:1](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-base/backend/src/main/java/ai/warehousebase/service/accounting/WhbGlBalanceProvider.java#L1).

Audit code baseline: `neetub1508/classic@0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa`. Design baseline: `neetub1508/warehouse-issues@7b96725eb5850748cd94b2a784466cb16728a55d`.

Recheck the affected path at the implementation commit. “Reported” and “verification gap” do not mean a fresh runtime failure; “code-supported” does not mean a live reproduction. Preserve that distinction in the resolution.

## Requirements closed

The existing warehouse behavior described in Scope and Acceptance. This audit does not allocate new FR identifiers or claim any requirement already closed. Reuse the adopted requirements in related task sources; record exact applicable IDs when implementing instead of inventing them.

## Scenarios closed

No scenario is newly marked passed by creating this task. Execute the finding-specific acceptance below and affected refusal/retry paths. Record the current commit, supported module configuration, fixture, role, steps and actual results; reuse catalogue scenarios where they apply.

## Closes

Audit finding **W10** once its acceptance is met and evidence is linked. This issue does not automatically close or reopen earlier tasks.

### Related issues / existing implementation ownership

- #174 — [Warehouse] Follow-up · The accounting-facing adapter has no home — no module owns WhbAccountingHandoverSink or WhbGlBalanceProvider.
- #175 — [Warehouse] Follow-up · Prove INTEGRATED mode end to end — WH-SC-156, WH-SC-157, CONFIG-CASE-07/10.

These links preserve earlier ownership/history. Coordinate overlapping implementation in one change and link both issues; do not build a second competing implementation. Closed duplicates remain closed.

## Implementation order and dependencies

**Recommended wave:** 3 — Prove complete release workflows and enabled integrations. This is a scheduling recommendation, not a requirement to finish every lower-wave issue before starting independent work.

### Before dependent implementation

- [W07 / #201](https://github.com/neetub1508/warehouse-issues/issues/201) — Stable valued movement output.
- [W08 / #202](https://github.com/neetub1508/warehouse-issues/issues/202) — Native producer cost lineage.

### Before final acceptance / closure

- Required upstream deliverables/evidence: [W07 / #201](https://github.com/neetub1508/warehouse-issues/issues/201), [W08 / #202](https://github.com/neetub1508/warehouse-issues/issues/202), [W34 / #228](https://github.com/neetub1508/warehouse-issues/issues/228). Confirm the relevant deliverable is accepted; an issue’s CLOSED status alone is not proof.
- Preparatory analysis, fixtures and independent fixes can proceed while prerequisites are open. If a prerequisite is already satisfied in current code, link its commit/test evidence instead of waiting or rebuilding it.

### Setup, decisions and conditional dependencies

External prerequisite: named receiving accounting owner, installed production sink/GL provider and an isolated receiver fixture. W11 is required only if this customer requires envelope v2; v1 standalone must not wait for v2.

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
- [ ] One dispatch yields one correctly valued accounting result; retries do not duplicate it; unavailable GL is never shown as zero.
- [ ] Verify current behavior against the cited evidence; record which concern is reproduced, already resolved, accepted by an existing decision, or still awaiting applicable integration evidence.
- [ ] Run the targeted automated/runtime checks needed for this change, plus required module gates; retain actual results. A skipped integration test or code read is not a runtime pass.
- [ ] Update affected contract/help/runbook text and the related issue evidence so the supported behavior agrees across code and documentation.
- [ ] List remaining conditional dependencies explicitly; do not close an enabled workflow with unverified stock integrity, access control or external-state recovery.

## Earlier report detail (reference, verify against current code)

The following preserves the original observations/reproduction details. It is historical context; the Scope and adopted decisions above govern implementation.

<details>
<summary>Source issue #174</summary>

Raised 2026-09-20 from **P2-18 (#128)**.

P2-18 declared `WhbGlBalanceProvider` in `warehouse-base` with **no implementation** (`AHO-UNR-06`, enforced by a test), and `WhbAccountingHandoverSink` is likewise unimplemented. An adapter must implement both, declare `enable.warehouse.accounting_sink=true`, and import both sides — so it cannot live under `ai.warehouse*`. **No module in CLAUDE.md's table owns it and no task builds it.**

Until it exists, INTEGRATED mode is unreachable: every movement stays `NOT_APPLICABLE`, the three handover columns on WS-219 are permanently zero, and the GL balance column states 'not connected'.

Contract: `AHO-OPEN-01` (OPEN). OD-1 is RESOLVED — the reciprocal accounting-side work is an **external integration dependency**, not an unanswered warehouse decision — so this issue is about naming the owning module and scheduling it, not about re-deciding OD-1.

</details>

<details>
<summary>Source issue #175</summary>

Raised 2026-09-20 from **P2-18 (#128)**, whose scope was ruled STANDALONE only.

These acceptance rows could not be demonstrated and are **not** covered by P2-18's close:
- `WH-SC-156` / `WH-SC-157` — one despatch produces one valued envelope through accounting's own source-document port, with the classification quad.
- Retry idempotency: a replay with the same key posts nothing and returns the original (`AHO-GRD-03`, `AHO-T1-06`).
- `REJECTED → VOIDED` needing `:void`, approver ≠ requester, only for a reversed or `NOT_APPLICABLE` movement (`AHO-T1-08`).
- `CONFIG-CASE-07` / `CONFIG-CASE-10` and the `enable.warehouse.accounting_sink` boot reconciliation (`A3`).

All of them need an installed, tested adapter — see the adapter follow-up. Schedule this immediately after it.

</details>

<!-- warehouse-readiness-finding: 2026-10-01/W10 -->
