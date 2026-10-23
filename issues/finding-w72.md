TITLE: [Warehouse] [Finding] W72 · Counterfeit control has no open owner after P3-24 was closed not planned
LABELS: task,warehouse,warehouse-base
issue: 606
---
Part of #1 · Audit **contract-divergence tracking, 2026-10-23** · Finding **W72** · Module **`warehouse-base`** · Migrations **none allocated by this audit; reserve only if implementation requires one** · Screens **existing affected surfaces identified below; no new screen IDs allocated**

**Priority:** P2 (audit recommendation, not a programme phase). **Evidence class:** Code-supported (grep). **Applies to:** Receiving and quality disposition (`FR-455`, v1.1).

## Scope

### What happens / remaining gap

`FR-455` (v1.1, active) asks for counterfeit control as two rows and a flag: `is_authorised_source` on item × supplier and a `SUSPECT` row in `whb_dispositions`, so a part from an unauthorised source is quarantined by the existing disposition path. Its owner `P3-24` (#121) was closed **not planned** on the product owner's `OD-17` ruling (2026-09-24), but that ruling defers only the GS1 identity work (SSCC allocation, the GS1-128 / Digital Link parser, EPC, the GS1 settings screen). Counterfeit control does not need a GS1 prefix, yet no open issue now owns it (`docs/contracts/counterparty-master.contract.md` §10 row 1).

### Required work

Build `FR-455` as `issues/p3-24.md` item 4 specifies — the `is_authorised_source` flag on `whb_item_supplier_sources`, the `SUSPECT` disposition row, and receipt of a serialised item from an unauthorised source raising the disposition without blocking the receipt — in a migration outside `P3-24`'s reserved `V500056`; **or** record a product decision that defers or withdraws `FR-455` as well, and amend the FRD and the contract row accordingly.

### Boundary and ownership

This task tracks one finding from the warehouse-only audit. Complete the work or evidence needed for the affected existing workflow. Planning, forecasting, optimization and competitor feature work are excluded. Optional-module work applies only to the stated scope. Existing web-only/online-only decisions and removed-adapter decisions remain authoritative. An intentional limit is closed by enforcing/documenting the supported boundary unless a later explicit scope decision authorizes expansion.

## Evidence and affected code

`docs/contracts/counterparty-master.contract.md` §10 row 1; `warehouse-base/backend/src/main/resources/db/migration/V500050__Create_whb_item_site_settings_supplier_sources_and_supersessions.sql:159` (`whb_item_supplier_sources`, no `is_authorised_source`); `V500010` (no `SUSPECT` disposition); #121 closing comment (`OD-17`).

Audit code baseline: `neetub1508/classic@74102d8d0481a90e84495d0462caf4e815fa977a`. Design baseline: `neetub1508/warehouse-issues@ba7f000119f665af7576519a6f96ab0d11175a0e`.

Recheck the affected path at the implementation commit. “Reported” and “verification gap” do not mean a fresh runtime failure; “code-supported” does not mean a live reproduction. Preserve that distinction in the resolution.

## Requirements closed

The existing warehouse behavior described in Scope and Acceptance. This audit does not allocate new FR identifiers or claim any requirement already closed. Reuse the adopted requirements in related task sources; record exact applicable IDs when implementing instead of inventing them.

## Scenarios closed

No scenario is newly marked passed by creating this task. Execute the finding-specific acceptance below and affected refusal/retry paths. Record the current commit, supported module configuration, fixture, role, steps and actual results; reuse catalogue scenarios where they apply.

## Closes

Audit finding **W72** once its acceptance is met and evidence is linked. This issue does not automatically close or reopen earlier tasks.

### Related issues / existing implementation ownership

- #121 — [Warehouse] P3-24 · GS1 identity — SSCC allocation, EPC on the serial and the LPN, Digital Link, and the authorised-source flag (closed not planned; GS1 part deferred by `OD-17`).

These links preserve earlier ownership/history. Coordinate overlapping implementation in one change and link both issues; do not build a second competing implementation. Closed duplicates remain closed.

## Implementation order and dependencies

**Recommended wave:** 2 — Complete task, import, reporting, setup and operational contracts. This is a scheduling recommendation, not a requirement to finish every lower-wave issue before starting independent work.

### Before dependent implementation

- No mandatory start dependency on another finding is identified. Begin current-code verification and this task’s scoped work immediately, subject to the setup/decision prerequisites below.

### Before final acceptance / closure

- No mandatory whole-issue completion dependency is identified. Meet this task’s acceptance and any applicable handoff/external prerequisites before closure.
- Preparatory analysis, fixtures and independent fixes can proceed while prerequisites are open. If a prerequisite is already satisfied in current code, link its commit/test evidence instead of waiting or rebuilding it.

### Setup, decisions and conditional dependencies

One scope decision first: does `OD-17`'s deferral extend to counterfeit control? If not, build it here; if so, record the decision and close this task with the FRD amendment.

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
- [ ] Counterfeit control is either built (flag, `SUSPECT` disposition, receipt raising the disposition, en/fr/hi strings, a refusal-free receipt test) or explicitly deferred/withdrawn by a recorded product decision with the FRD and contract amended.
- [ ] Verify current behavior against the cited evidence; record which concern is reproduced, already resolved, accepted by an existing decision, or still awaiting applicable integration evidence.
- [ ] Relevant flow check — **Purchase and receipt**: receipt of a serialised item from an unauthorised source records the goods and quarantines them; an authorised source receives normally. Limit this task to its finding; link adjacent tasks for the rest.
- [ ] Run the targeted automated/runtime checks needed for this change, plus required module gates; retain actual results. A skipped integration test or code read is not a runtime pass.
- [ ] Update affected contract/help/runbook text and the related issue evidence so the supported behavior agrees across code and documentation.
- [ ] List remaining conditional dependencies explicitly; do not close an enabled workflow with unverified stock integrity, access control or external-state recovery.

<!-- warehouse-readiness-finding: 2026-10-23/W72 -->
