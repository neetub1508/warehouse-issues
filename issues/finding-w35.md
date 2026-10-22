TITLE: [Warehouse] [Finding] W35 · The standalone acceptance sequence remains incompletely demonstrated
LABELS: task,warehouse,warehouse-base
issue: 229
---
Part of #1 · Audit **warehouse-only readiness, 2026-10-01** · Finding **W35** · Module **`warehouse-base`, `warehouse`** · Migrations **none allocated by this audit; reserve only if implementation requires one** · Screens **existing affected surfaces identified below; no new screen IDs allocated**

**Priority:** P1 (audit recommendation, not a programme phase). **Evidence class:** Reported verification gap. **Applies to:** Initial warehouse release.

## Scope

### What happens / remaining gap

The earlier run demonstrated 060–062 but not 044–059 in sequence. The catalogue is now available; lack of access is no longer a reason to leave the sequence undefined.

### Required work

Execute 044–062 in order on an isolated Mode-A install and preserve setup/data/results.

### Boundary and ownership

This task tracks one finding from the warehouse-only audit. Complete the work or evidence needed for the affected existing workflow. Planning, forecasting, optimization and competitor feature work are excluded. Optional-module work applies only to the stated scope. Existing web-only/online-only decisions and removed-adapter decisions remain authoritative. An intentional limit is closed by enforcing/documenting the supported boundary unless a later explicit scope decision authorizes expansion.

## Evidence and affected code

[#186](https://github.com/neetub1508/warehouse-issues/issues/186).

Audit code baseline: `neetub1508/classic@0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa`. Design baseline: `neetub1508/warehouse-issues@7b96725eb5850748cd94b2a784466cb16728a55d`.

Recheck the affected path at the implementation commit. “Reported” and “verification gap” do not mean a fresh runtime failure; “code-supported” does not mean a live reproduction. Preserve that distinction in the resolution.

## Requirements closed

The existing warehouse behavior described in Scope and Acceptance. This audit does not allocate new FR identifiers or claim any requirement already closed. Reuse the adopted requirements in related task sources; record exact applicable IDs when implementing instead of inventing them.

## Scenarios closed

No scenario is newly marked passed by creating this task. Execute the finding-specific acceptance below and affected refusal/retry paths. Record the current commit, supported module configuration, fixture, role, steps and actual results; reuse catalogue scenarios where they apply.

## Closes

Audit finding **W35** once its acceptance is met and evidence is linked. This issue does not automatically close or reopen earlier tasks.

### Related issues / existing implementation ownership

- #186 — [Warehouse] W13-1 carry: WH-SC-044…WH-SC-059 not demonstrated (SCENARIO-CATALOGUE.md not available locally).

These links preserve earlier ownership/history. Coordinate overlapping implementation in one change and link both issues; do not build a second competing implementation. Closed duplicates remain closed.

## Implementation order and dependencies

**Recommended wave:** 3 — Prove complete release workflows and enabled integrations. This is a scheduling recommendation, not a requirement to finish every lower-wave issue before starting independent work.

### Before dependent implementation

- No mandatory start dependency on another finding is identified. Begin current-code verification and this task’s scoped work immediately, subject to the setup/decision prerequisites below.

### Before final acceptance / closure

- Required upstream deliverables/evidence: [W01 / #195](https://github.com/neetub1508/warehouse-issues/issues/195), [W02 / #196](https://github.com/neetub1508/warehouse-issues/issues/196), [W03 / #197](https://github.com/neetub1508/warehouse-issues/issues/197), [W07 / #201](https://github.com/neetub1508/warehouse-issues/issues/201), [W08 / #202](https://github.com/neetub1508/warehouse-issues/issues/202), [W12 / #206](https://github.com/neetub1508/warehouse-issues/issues/206), [W13 / #207](https://github.com/neetub1508/warehouse-issues/issues/207), [W14 / #208](https://github.com/neetub1508/warehouse-issues/issues/208), [W19 / #213](https://github.com/neetub1508/warehouse-issues/issues/213), [W34 / #228](https://github.com/neetub1508/warehouse-issues/issues/228), [W39 / #233](https://github.com/neetub1508/warehouse-issues/issues/233), [W40 / #234](https://github.com/neetub1508/warehouse-issues/issues/234), [W49 / #243](https://github.com/neetub1508/warehouse-issues/issues/243), [W50 / #244](https://github.com/neetub1508/warehouse-issues/issues/244). Confirm the relevant deliverable is accepted; an issue’s CLOSED status alone is not proof.
- Preparatory analysis, fixtures and independent fixes can proceed while prerequisites are open. If a prerequisite is already satisfied in current code, link its commit/test evidence instead of waiting or rebuilding it.

### Setup, decisions and conditional dependencies

Prepare standalone acceptance data immediately. Complete the catalogue sequence on the supported Mode-A configuration; optional capabilities are required only if exercised. Record explicit exclusions rather than silently skipping steps.

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
- [ ] One install proves onboarding, receive/putaway, order/pick/ship, return, transfer, count and independent reconciliation without accounting/vertical modules.
- [ ] Verify current behavior against the cited evidence; record which concern is reproduced, already resolved, accepted by an existing decision, or still awaiting applicable integration evidence.
- [ ] Relevant flow check — **Purchase and receipt**: Partial/over/foreign-currency receipt, duplicate submission, lot/serial/UOM and receipt evidence. Limit this task to its finding; link adjacent tasks for the rest.
- [ ] Relevant flow check — **Release gates**: Backend plus actual database tests, repaired frontend gate, type/build checks and complete operator journeys. Limit this task to its finding; link adjacent tasks for the rest.
- [ ] Run the targeted automated/runtime checks needed for this change, plus required module gates; retain actual results. A skipped integration test or code read is not a runtime pass.
- [ ] Update affected contract/help/runbook text and the related issue evidence so the supported behavior agrees across code and documentation.
- [ ] List remaining conditional dependencies explicitly; do not close an enabled workflow with unverified stock integrity, access control or external-state recovery.

## Earlier report detail (reference, verify against current code)

The following preserves the original observations/reproduction details. It is historical context; the Scope and adopted decisions above govern implementation.

<details>
<summary>Source issue #186</summary>

## What is carried

`W13-1` (the warehouse v1 exit criterion) calls for **`WH-SC-044` … `WH-SC-062`, in order, on one
Mode-A install, in one sitting**. On 2026-09-21 only the **three the batch file itself calls decisive**
were demonstrated:

- **`WH-SC-060`** — register / position / valuation reconcile to the unit and the paisa — **PASS**
- **`WH-SC-061`** — full rebuild from `whb_stock_movements` reproduces the position report, diffed
  per item — **PASS**
- **`WH-SC-062`** — valuation produced with no accounting module installed — **PASS**

**`WH-SC-044` … `WH-SC-059` (16 scenarios) were NOT demonstrated.**

## Why

Their ratified texts live in `SCENARIO-CATALOGUE.md` §3.2, in the **design-set repo**, which is **not
cloned on this machine** (`~/work/git/workspace/warehouse-issues` is the *old* machine's path and does
not exist here). Only `WH-SC-060/061/062` are quoted in full inside
`.claude/tasks/BATCH-WAREHOUSE-P2.md`, so they were the only ones with an authoritative definition
available locally.

Reconstructing the 16 from `warehouse*/docs/contracts/` was explicitly rejected as an option: a
reconstructed scenario is not the ratified one, so a pass would be weaker evidence than it looks.

## To close this

1. Clone or point at the design-set repo holding `SCENARIO-CATALOGUE.md`.
2. Run `WH-SC-044` … `WH-SC-059` in order on a Mode-A install, in one sitting.
3. Note the standing **Mode-A deviation**: on this stack accounting is genuinely absent (0 `acc_*`
   tables, no `ai.accounting.*` beans, accounting routes unmapped/404), but the verticals
   (dealer, assets, accessories, services, insurance, attendance) are **installed-but-unwired** rather
   than absent. The user accepted this deviation for the three decisive scenarios; re-confirm it is
   acceptable for the remaining 16.

## Also carried from the same sitting

- `WhaeExampleDocumentPostingIntegrationTest` (the `W13-2` port-proof test) was **not executed** — it
  needs a Maven run and there is no usable local toolchain. `W13-2` rests on the ratchet
  (`git log --oneline -- warehouse-base/ | wc -l` = **831**, unchanged) plus the code path.
- `ci-gate.sh ratchets warehouse` has **not been re-run** since the two product adapters were removed
  in `64d1fe74d5`. That removal dropped 6 adapter ratchets — a permitted shrink; no baseline was
  extended.
- Not exercised in the W13-1 sitting: WS-208's by-location tab, exports / CSV streaming, and any
  pixel-level UI check.

## Fixtures left in place (reusable)

Warehouse `ZZQAWH1` (`25af4627-0160-40d1-8756-eccf9c265da3`), company `Default Company`
(`c57a1041-01ff-4f8f-ac0a-486ca8b5e62c`), branch `PASCO NEXA FARIDABAD (SALES)`, items
`ITM-00000001..3`, counterparty `ZZQASUP1`, locations `ZZQARCV1` / `ZZQABIN1`, GRN 000001-000006,
ADJ 000001-000003. Users `qa.tester@platform.test` / `QaTester@2026` and
`qa.approver@platform.test` / `QaApprover@2026` (a second ADMIN is required because
`WhStockAdjustmentController.approve` refuses an approver who is also the submitter — `FR-408`
maker-checker, not a bug).

</details>

<!-- warehouse-readiness-finding: 2026-10-01/W35 -->
