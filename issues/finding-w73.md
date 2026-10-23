TITLE: [Warehouse] [Finding] W73 · Nine non-functional rules are verified only by the reviewer gate
LABELS: task,warehouse,warehouse-base
issue: 607
---
Part of #1 · Audit **contract-divergence tracking, 2026-10-23** · Finding **W73** · Module **`warehouse-base`, `warehouse`, `warehouse-india`, `warehouse-3pl`** · Migrations **none allocated by this audit; reserve only if implementation requires one** · Screens **existing affected surfaces identified below; no new screen IDs allocated**

**Priority:** P3 (audit recommendation, not a programme phase). **Evidence class:** Verification gap. **Applies to:** Build gates (`ci-gate.sh` ratchets).

## Scope

### What happens / remaining gap

`docs/contracts/non-functional.contract.md` `NFR-DIV-07` lists nine rule rows — `NFR-04` (the auditor artefact list), `NFR-10`, `NFR-13`, `NFR-15` (in-product help), `NFR-16`…`NFR-18`, `NFR-23`, `NFR-24` — that no automated check enforces; only the reviewer gate reads them. `NFR-DIV-08` shows the cost: 47 warehouse pages shipped without the platform `HelpButton` (18 in `warehouse-3pl`, 27 in `warehouse-india`, 2 in `warehouse-base`) because no scanner fails the build.

### Required work

Mechanise each of the nine rows as a ratchet or architecture test in the warehouse gate (`shared/scripts/ci-gate.sh ratchets <module>`, new test classes registered in its `.def`), starting with a page scanner that fails when a warehouse `page.tsx` lacks `HelpButton` (`NFR-15`). Where a row cannot be mechanised, record why in the contract row. The missing `HelpButton`s themselves are fixed by the reopened `P5-01` (#17), `P2-IN-01` (#130) and `P0-08` (#71); this task adds the check that keeps them fixed.

### Boundary and ownership

This task tracks one finding from the warehouse-only audit. Complete the work or evidence needed for the affected existing workflow. Planning, forecasting, optimization and competitor feature work are excluded. Optional-module work applies only to the stated scope. Existing web-only/online-only decisions and removed-adapter decisions remain authoritative. An intentional limit is closed by enforcing/documenting the supported boundary unless a later explicit scope decision authorizes expansion.

## Evidence and affected code

`docs/contracts/non-functional.contract.md` §2 rows `NFR-DIV-07`, `NFR-DIV-08` and the nine rule rows they cite (`FR-427`, `FR-430`, `FR-431`, `FR-435`, `FR-440`, `FR-442`…`FR-445`).

Audit code baseline: `neetub1508/classic@74102d8d0481a90e84495d0462caf4e815fa977a`. Design baseline: `neetub1508/warehouse-issues@ba7f000119f665af7576519a6f96ab0d11175a0e`.

Recheck the affected path at the implementation commit. “Reported” and “verification gap” do not mean a fresh runtime failure; “code-supported” does not mean a live reproduction. Preserve that distinction in the resolution.

## Requirements closed

The existing warehouse behavior described in Scope and Acceptance. This audit does not allocate new FR identifiers or claim any requirement already closed. Reuse the adopted requirements in related task sources; record exact applicable IDs when implementing instead of inventing them.

## Scenarios closed

No scenario is newly marked passed by creating this task. Execute the finding-specific acceptance below and affected refusal/retry paths. Record the current commit, supported module configuration, fixture, role, steps and actual results; reuse catalogue scenarios where they apply.

## Closes

Audit finding **W73** once its acceptance is met and evidence is linked. This issue does not automatically close or reopen earlier tasks.

### Related issues / existing implementation ownership

- #17 — [Warehouse] P5-01 (reopened: 3PL page `HelpButton`).
- #130 — [Warehouse] P2-IN-01 (reopened: India page `HelpButton`).
- #71 — [Warehouse] P0-08 (reopened: port pages `HelpButton`).

These links preserve earlier ownership/history. Coordinate overlapping implementation in one change and link both issues; do not build a second competing implementation. Closed duplicates remain closed.

## Implementation order and dependencies

**Recommended wave:** 0 — Confirm adopted contracts/package boundaries and repair test/runtime infrastructure. This is a scheduling recommendation, not a requirement to finish every lower-wave issue before starting independent work.

### Before dependent implementation

- No mandatory start dependency on another finding is identified. Begin current-code verification and this task’s scoped work immediately, subject to the setup/decision prerequisites below.

### Before final acceptance / closure

- No mandatory whole-issue completion dependency is identified. Meet this task’s acceptance and any applicable handoff/external prerequisites before closure.
- Preparatory analysis, fixtures and independent fixes can proceed while prerequisites are open. If a prerequisite is already satisfied in current code, link its commit/test evidence instead of waiting or rebuilding it.

### Setup, decisions and conditional dependencies

Coordinate the page scanner with the three reopened `HelpButton` items so the ratchet baseline is set after they land, or set it at today's count and ratchet down. The scanners touch files `P7` removes or renames; run after `P7`.

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
- [ ] Each of the nine rule rows has an automated check in the warehouse gate, or its contract row records why it stays reviewer-only; the `HelpButton` page scanner fails on a page without it.
- [ ] Verify current behavior against the cited evidence; record which concern is reproduced, already resolved, accepted by an existing decision, or still awaiting applicable integration evidence.
- [ ] Relevant flow check — **Permissions and evidence**: the gate fails on a planted page without `HelpButton` and passes on the fixed tree. Limit this task to its finding; link adjacent tasks for the rest.
- [ ] Run the targeted automated/runtime checks needed for this change, plus required module gates; retain actual results. A skipped integration test or code read is not a runtime pass.
- [ ] Update affected contract/help/runbook text and the related issue evidence so the supported behavior agrees across code and documentation.
- [ ] List remaining conditional dependencies explicitly; do not close an enabled workflow with unverified stock integrity, access control or external-state recovery.

<!-- warehouse-readiness-finding: 2026-10-23/W73 -->
