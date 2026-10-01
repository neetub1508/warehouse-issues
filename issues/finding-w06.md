TITLE: [Warehouse] [Finding] W06 · Cost-layer and valuation-policy maintenance surfaces remain unbuilt/unproven
LABELS: task,warehouse,warehouse-base
issue: 200
---
Part of #1 · Audit **warehouse-only readiness, 2026-10-01** · Finding **W06** · Module **`warehouse-base`** · Migrations **none allocated by this audit; reserve only if implementation requires one** · Screens **existing affected surfaces identified below; no new screen IDs allocated**

**Priority:** P1 (audit recommendation, not a programme phase). **Evidence class:** Code-supported. **Applies to:** Valued stock.

## Scope

### What happens / remaining gap

The follow-up identifies missing screens/seeds; controller search did not find CostLayer or ValuationPolicy controllers. Existing costing engine is not a substitute for supported policy maintenance.

### Required work

Deliver or identify the supported configuration, inspection and export surfaces; reconcile seeds and permissions.

### Boundary and ownership

This task tracks one finding from the warehouse-only audit. Complete the work or evidence needed for the affected existing workflow. Planning, forecasting, optimization and competitor feature work are excluded. Optional-module work applies only to the stated scope. Existing web-only/online-only decisions and removed-adapter decisions remain authoritative. An intentional limit is closed by enforcing/documenting the supported boundary unless a later explicit scope decision authorizes expansion.

## Evidence and affected code

[#169](https://github.com/neetub1508/warehouse-issues/issues/169); [warehouse-base/backend/src/main/java/ai/warehousebase/controller](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-base/backend/src/main/java/ai/warehousebase/controller).

Audit code baseline: `neetub1508/classic@0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa`. Design baseline: `neetub1508/warehouse-issues@7b96725eb5850748cd94b2a784466cb16728a55d`.

Recheck the affected path at the implementation commit. “Reported” and “verification gap” do not mean a fresh runtime failure; “code-supported” does not mean a live reproduction. Preserve that distinction in the resolution.

## Requirements closed

The existing warehouse behavior described in Scope and Acceptance. This audit does not allocate new FR identifiers or claim any requirement already closed. Reuse the adopted requirements in related task sources; record exact applicable IDs when implementing instead of inventing them.

## Scenarios closed

No scenario is newly marked passed by creating this task. Execute the finding-specific acceptance below and affected refusal/retry paths. Record the current commit, supported module configuration, fixture, role, steps and actual results; reuse catalogue scenarios where they apply.

## Closes

Audit finding **W06** once its acceptance is met and evidence is linked. This issue does not automatically close or reopen earlier tasks.

### Related issues / existing implementation ownership

- #169 — [Warehouse] P2-16 follow-up · Cost Layers and Valuation Policies screens.

These links preserve earlier ownership/history. Coordinate overlapping implementation in one change and link both issues; do not build a second competing implementation. Closed duplicates remain closed.

## Implementation order and dependencies

**Recommended wave:** 2 — Complete workflow contracts and operational safeguards. This is a scheduling recommendation, not a requirement to finish every lower-wave issue before starting independent work.

### Before dependent implementation

- [W09 / #203](https://github.com/neetub1508/warehouse-issues/issues/203) — Adopted costing policy/field contract identified; full W09 runtime closure is not required to start.

### Before final acceptance / closure

- No mandatory whole-issue completion dependency is identified. Meet this task’s acceptance and any applicable handoff/external prerequisites before closure.
- Preparatory analysis, fixtures and independent fixes can proceed while prerequisites are open. If a prerequisite is already satisfied in current code, link its commit/test evidence instead of waiting or rebuilding it.

### Setup, decisions and conditional dependencies

Reserve any menu/grid/filter/permission migration through the existing allocation process. Coordinate displays with W07/W08 cost fields.

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
- [ ] A stock controller can inspect layers and an authorized user can maintain effective policies through supported UI/API.
- [ ] Verify current behavior against the cited evidence; record which concern is reproduced, already resolved, accepted by an existing decision, or still awaiting applicable integration evidence.
- [ ] Relevant flow check — **Valuation and period close**: Old surviving stock, backdated events, FIFO/average, rounding, policy changes and period refusal. Limit this task to its finding; link adjacent tasks for the rest.
- [ ] Run the targeted automated/runtime checks needed for this change, plus required module gates; retain actual results. A skipped integration test or code read is not a runtime pass.
- [ ] Update affected contract/help/runbook text and the related issue evidence so the supported behavior agrees across code and documentation.
- [ ] List remaining conditional dependencies explicitly; do not close an enabled workflow with unverified stock integrity, access control or external-state recovery.

## Earlier report detail (reference, verify against current code)

The following preserves the original observations/reproduction details. It is historical context; the Scope and adopted decisions above govern implementation.

<details>
<summary>Source issue #169</summary>

Follow-up from #115 (P2-16 costing engine) · Module **`warehouse-base`** · Migration: one base migration (grid/filter/menu/permission seeds) — **number to be reserved in this task's header** (#115 declared "Migrations none" while listing the screens)

## Scope
The costing engine shipped in #115, but its two screens need seed data the task had no migration for:
- **WS-049 Cost Layers** (`whb_cost_layers`, read-only; filter scope `WAREHOUSE_COST_LAYER`: boolean `hasRemaining` default true, dateOnly `layerDateFrom`/`layerDateTo`; lists `RETURN_UNMATCHED` and `ESTIMATED` layers by basis).
- **WS-050 Valuation Policies** (`whb_valuation_policies`; filter scope `WAREHOUSE_VALUATION_POLICY`: dateOnly `effectiveFromFrom`/`effectiveFromTo`; FIFO/AVCO only — LIFO and STANDARD are refused by the engine).

## Acceptance
1. A stock controller can list the open cost layers of an item at a site, with quantity remaining, value and basis, and export exactly the grid.
2. A finance user can set FIFO or weighted average for an item category at a site from a date; LIFO and standard cost cannot be chosen.

</details>

<!-- warehouse-readiness-finding: 2026-10-01/W06 -->
