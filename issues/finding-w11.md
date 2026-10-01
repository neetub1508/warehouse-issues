TITLE: [Warehouse] [Finding] W11 · Versioned accounting-envelope extension
LABELS: task,warehouse,warehouse-base
issue: 205
---
Part of #1 · Audit **warehouse-only readiness, 2026-10-01** · Finding **W11** · Module **`warehouse-base`** · Migrations **none allocated by this audit; reserve only if implementation requires one** · Screens **existing affected surfaces identified below; no new screen IDs allocated**

**Priority:** P1 (audit recommendation, not a programme phase). **Evidence class:** Reported. **Applies to:** Only customers requiring the expanded accounting interface.

## Scope

### What happens / remaining gap

Required per-line details and version negotiation are not established by the frozen v1 contract.

### Required work

Define v2 with the receiving module and resolve account-reference ownership using adopted authority.

### Boundary and ownership

This task tracks one finding from the warehouse-only audit. Complete the work or evidence needed for the affected existing workflow. Planning, forecasting, optimization and competitor feature work are excluded. Optional-module work applies only to the stated scope. Existing web-only/online-only decisions and removed-adapter decisions remain authoritative. An intentional limit is closed by enforcing/documenting the supported boundary unless a later explicit scope decision authorizes expansion.

## Evidence and affected code

[#173](https://github.com/neetub1508/warehouse-issues/issues/173); [accounting-handover.contract.md:1](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-base/docs/contracts/accounting-handover.contract.md#L1).

Audit code baseline: `neetub1508/classic@0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa`. Design baseline: `neetub1508/warehouse-issues@7b96725eb5850748cd94b2a784466cb16728a55d`.

Recheck the affected path at the implementation commit. “Reported” and “verification gap” do not mean a fresh runtime failure; “code-supported” does not mean a live reproduction. Preserve that distinction in the resolution.

## Requirements closed

The existing warehouse behavior described in Scope and Acceptance. This audit does not allocate new FR identifiers or claim any requirement already closed. Reuse the adopted requirements in related task sources; record exact applicable IDs when implementing instead of inventing them.

## Scenarios closed

No scenario is newly marked passed by creating this task. Execute the finding-specific acceptance below and affected refusal/retry paths. Record the current commit, supported module configuration, fixture, role, steps and actual results; reuse catalogue scenarios where they apply.

## Closes

Audit finding **W11** once its acceptance is met and evidence is linked. This issue does not automatically close or reopen earlier tasks.

### Related issues / existing implementation ownership

- #173 — [Warehouse] Follow-up · Accounting envelope v2 — duty status, lot, serial and exchange rate per line.

These links preserve earlier ownership/history. Coordinate overlapping implementation in one change and link both issues; do not build a second competing implementation. Closed duplicates remain closed.

## Implementation order and dependencies

**Recommended wave:** 3 — Prove complete release workflows and enabled integrations. This is a scheduling recommendation, not a requirement to finish every lower-wave issue before starting independent work.

### Before dependent implementation

- [W07 / #201](https://github.com/neetub1508/warehouse-issues/issues/201) — Stable source-cost evidence fields.
- [W08 / #202](https://github.com/neetub1508/warehouse-issues/issues/202) — Producer lineage mapping.

### Before final acceptance / closure

- Required upstream deliverables/evidence: [W07 / #201](https://github.com/neetub1508/warehouse-issues/issues/201), [W08 / #202](https://github.com/neetub1508/warehouse-issues/issues/202). Confirm the relevant deliverable is accepted; an issue’s CLOSED status alone is not proof.
- Preparatory analysis, fixtures and independent fixes can proceed while prerequisites are open. If a prerequisite is already satisfied in current code, link its commit/test evidence instead of waiting or rebuilding it.

### Setup, decisions and conditional dependencies

External prerequisite: receiving-system agreement on required fields/version negotiation/account-reference ownership. Do not invent a receiver or recost downstream.

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
- [ ] Receiver accepts the negotiated version and preserves duty/lot/serial/rate evidence without recosting.
- [ ] Verify current behavior against the cited evidence; record which concern is reproduced, already resolved, accepted by an existing decision, or still awaiting applicable integration evidence.
- [ ] Run the targeted automated/runtime checks needed for this change, plus required module gates; retain actual results. A skipped integration test or code read is not a runtime pass.
- [ ] Update affected contract/help/runbook text and the related issue evidence so the supported behavior agrees across code and documentation.
- [ ] List remaining conditional dependencies explicitly; do not close an enabled workflow with unverified stock integrity, access control or external-state recovery.

## Earlier report detail (reference, verify against current code)

The following preserves the original observations/reproduction details. It is historical context; the Scope and adopted decisions above govern implementation.

<details>
<summary>Source issue #173</summary>

Raised 2026-09-20 from **P2-18 (#128)**, which shipped STANDALONE only on the user's ruling.

`WhbAccountingEnvelopeV1` is frozen by `RL-002`, so the per-line fields `FR-233` / `WH-SC-156` require — duty status, lot identity, serial identity — and `RF-005`'s exchange rate cannot be added to it. They need a v2 envelope, with a version negotiation the receiving side can accept.

Contract: `docs/contracts/accounting-handover.contract.md` row `AHO-OPEN-02` (still OPEN). That row also records the unresolved conflict about whether the envelope may carry `debitAccountRef`/`creditAccountRef`: BUILD-SPEC WS-051 and P0-12 DEC-01 say yes, p2-18's Traps and WH-SC-156 say no. Settle that before writing v2.

Blocked by nothing in warehouse; it needs a receiving side to negotiate with (see the adapter follow-up).

</details>

<!-- warehouse-readiness-finding: 2026-10-01/W11 -->
