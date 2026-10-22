TITLE: [Warehouse] [Finding] W57 · Operational KPI semantics and coexistence defaults require sign-off
LABELS: task,warehouse,warehouse-base
issue: 251
---
Part of #1 · Audit **warehouse-only readiness, 2026-10-01** · Finding **W57** · Module **`warehouse-base`, `warehouse`** · Migrations **none allocated by this audit; reserve only if implementation requires one** · Screens **existing affected surfaces identified below; no new screen IDs allocated**

**Priority:** P2 (audit recommendation, not a programme phase). **Evidence class:** Reported / verification. **Applies to:** Management reports and legacy coexistence.

## Scope

### What happens / remaining gap

Open issues record reversible report decisions, including side-by-side valuations without a combined grand total. They are product choices, not automatically defects.

### Required work

Confirm adopted defaults, explain them in reports, and independently reconcile KPI denominators and cost bases.

### Boundary and ownership

This task tracks one finding from the warehouse-only audit. Complete the work or evidence needed for the affected existing workflow. Planning, forecasting, optimization and competitor feature work are excluded. Optional-module work applies only to the stated scope. Existing web-only/online-only decisions and removed-adapter decisions remain authoritative. An intentional limit is closed by enforcing/documenting the supported boundary unless a later explicit scope decision authorizes expansion.

## Evidence and affected code

[#184](https://github.com/neetub1508/warehouse-issues/issues/184); [#178](https://github.com/neetub1508/warehouse-issues/issues/178).

Audit code baseline: `neetub1508/classic@0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa`. Design baseline: `neetub1508/warehouse-issues@7b96725eb5850748cd94b2a784466cb16728a55d`.

Recheck the affected path at the implementation commit. “Reported” and “verification gap” do not mean a fresh runtime failure; “code-supported” does not mean a live reproduction. Preserve that distinction in the resolution.

## Requirements closed

The existing warehouse behavior described in Scope and Acceptance. This audit does not allocate new FR identifiers or claim any requirement already closed. Reuse the adopted requirements in related task sources; record exact applicable IDs when implementing instead of inventing them.

## Scenarios closed

No scenario is newly marked passed by creating this task. Execute the finding-specific acceptance below and affected refusal/retry paths. Record the current commit, supported module configuration, fixture, role, steps and actual results; reuse catalogue scenarios where they apply.

## Closes

Audit finding **W57** once its acceptance is met and evidence is linked. This issue does not automatically close or reopen earlier tasks.

### Related issues / existing implementation ownership

- #178 — [Warehouse] OD-20 · Does v1 ship a union valuation report across the two ownership domains? (gates P2-20, P2-27).
- #184 — P2-21: four product calls taken by default in report pack 2.

These links preserve earlier ownership/history. Coordinate overlapping implementation in one change and link both issues; do not build a second competing implementation. Closed duplicates remain closed.

## Implementation order and dependencies

**Recommended wave:** 2 — Complete workflow contracts and operational safeguards. This is a scheduling recommendation, not a requirement to finish every lower-wave issue before starting independent work.

### Before dependent implementation

- [W09 / #203](https://github.com/neetub1508/warehouse-issues/issues/203) — Adopted valuation and basis semantics.

### Before final acceptance / closure

- No mandatory whole-issue completion dependency is identified. Meet this task’s acceptance and any applicable handoff/external prerequisites before closure.
- Preparatory analysis, fixtures and independent fixes can proceed while prerequisites are open. If a prerequisite is already satisfied in current code, link its commit/test evidence instead of waiting or rebuilding it.

### Setup, decisions and conditional dependencies

Confirm existing coexistence/KPI definitions and independent reconciliation fixture. W10 is conditional when a live GL comparison is promised; unavailable GL must not be represented as zero.

### Coordination and change control

- Earlier issues in “Related issues / existing implementation ownership” are ownership/history links, not automatic blockers. Preserve their accepted decisions and coordinate overlapping changes.
- A start dependency above can be a contract or test-environment handoff; it does not require closing the whole upstream issue. This avoids circular waits between implementation and acceptance tasks.
- Before implementation, confirm the applicable package, owner, schema/API/event contracts and required external fixtures. If a new blocker is discovered, add its issue link, exact deliverable, reason and applicability here and update the batch dependency index before dependent work proceeds.
- Record each prerequisite as satisfied with evidence, blocked with an owner, or not applicable with a scope reason. Do not silently bypass prerequisites or turn conditional features into universal blockers.

## Traps

- Follow `docs/DECISIONS.md` and its adopted settings amendment; older task wording is historical where superseded.
- Preserve stock/valuation lineage, tenant/site/owner scope and existing service ownership on affected paths.
- Do not interpret a missing runtime test as proof that the feature is missing. Verify before replacing working code.
- This includes a scope or documentation decision. Closure can be a verified correction or supported-boundary decision; it must not silently expand the product.

## Acceptance

- [ ] Dependency review completed: all applicable prerequisites above have linked evidence or explicit scope disposition; newly discovered blockers are recorded in this task and the batch index.
- [ ] Users can reproduce key metrics and distinguish native/external stock values; no misleading combined valuation.
- [ ] Verify current behavior against the cited evidence; record which concern is reproduced, already resolved, accepted by an existing decision, or still awaiting applicable integration evidence.
- [ ] Relevant flow check — **Reports/export/search**: UI/filter/export parity, literal wildcard input, timezone dates, cost masking and scoped scheduled delivery. Limit this task to its finding; link adjacent tasks for the rest.
- [ ] Run the targeted automated/runtime checks needed for this change, plus required module gates; retain actual results. A skipped integration test or code read is not a runtime pass.
- [ ] Update affected contract/help/runbook text and the related issue evidence so the supported behavior agrees across code and documentation.
- [ ] List remaining conditional dependencies explicitly; do not close an enabled workflow with unverified stock integrity, access control or external-state recovery.

## Earlier report detail (reference, verify against current code)

The following preserves the original observations/reproduction details. It is historical context; the Scope and adopted decisions above govern implementation.

<details>
<summary>Source issue #178</summary>

`COEXISTENCE.md` §8.2 flagged this conflict as needing an `OD-` row and could not allocate the id itself, because `DECISIONS.md` §OD owns the namespace. Its stated deadline — *"before the `P2` reports task is written"* — arrived with **P2-20**, so the driver allocated **OD-20** and took a default rather than blocking the batch.

## The conflict
- **R3 `M3`/`E-084`** — build a union valuation report across the warehouse-owned and legacy-owned domains.
- **R7 §4.6 item 4** — do not; document the separation in the UI instead.
- `DECISIONS.md` settled neither.

## Default taken (driver ruling, 2026-09-20 — open to reversal)
`COEXISTENCE.md` §5 `M3`'s own reconciling shape: **side-by-side columns, and no grand total anywhere, including the export.**

Reasoning:
1. Both domains appear together, which is what R3 wanted from a union report.
2. No arithmetic unions two different costing bases, which is what R7 objected to.
3. It is the reversible direction. A grand total can be added later once both domains share one of `L-13`'s clocks; a number finance has started quoting cannot be withdrawn.
4. **`RC-001` reinforces it** — P2-20 requires every report to declare which of `L-13`'s three clocks it reads, and a cross-domain union can declare none.

The category-ownership reconciliation itself remains **P2-27**'s work (`D-9`), not P2-20's.

## What a reversal would cost
Cheap while P2-20's reports are unbuilt or freshly built: adding a grand total is additive. It gets expensive once an install's finance users have quoted the figure. If you want the union total in v1, say so before P2-27 ships and it can be added to the same grids.

Recorded as `OD-20` in `docs/DECISIONS.md`.

</details>

<details>
<summary>Source issue #184</summary>

Tracking the calls taken by default while building P2-21 (#141), per the standing rule that a default call is recorded rather than left implicit. None of these is blocking; each is cheap to reverse.

**1. WS-218 Traceability refuses an unknown `direction` (added API behaviour).**
`direction` is the pack's one `is_required` row, so `WhbReportParameterGuard` already refuses it when absent. A *present but unrecognised* value satisfied the guard, matched neither arm of the SQL and returned an empty trace — which on a recall reads as "this lot never moved". The controller now returns a field-level 400 on the same key instead. This is one `if` beyond what the seed declares.

**2. WS-216 Operational KPIs no longer cross-joins the whole catalogue unconditionally.**
The grid is driven by `whb_metric_definitions` so that a metric registered by an adapter appears without a code change. Unconditionally, that also rendered the four FR-393 parts metrics as rows the screen's six fact arms will never fill — and `wh_rpt_parts_kpis` (WS-217) is a *pivoted* grid, so those four are columns there and will never have a fact source here. They were blank forever, not blank pending WS-217. A metric now gets a row when it has a fact for the grain **or** the reader named it in `metricCode`; catalogue-driven discovery is unchanged.

**3. WS-217 Parts KPIs: `metricCode` narrows the row set rather than blanking cells.**
On a pivoted grid the filter could either blank unselected cells or narrow the row set. Blanking would make a dash mean two things ("no figure" and "not selected"), and the whole pack rests on a dash meaning one. Selected metrics narrow the row set to site-periods where at least one has a figure; cells stay real.

**4. WS-217's metric picker offers only this grid's four column-metrics.**
Read from `whb_metric_definitions` rather than hard-coded, but scoped to the four. Offering a tenth catalogue metric would offer a filter that can never match a column this grid has. The D-10 openness argument governs WS-216's *long* grid; it does not transfer to a pivoted one.

Related: #176, #177, #178, #179, #180, #181, #182, #183.

</details>

<!-- warehouse-readiness-finding: 2026-10-01/W57 -->
