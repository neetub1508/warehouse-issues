TITLE: [Warehouse] [Finding] W27 · Opening-stock row validation filter has no operator surface
LABELS: task,warehouse
issue: 221
---
Part of #1 · Audit **warehouse-only readiness, 2026-10-01** · Finding **W27** · Module **`warehouse`** · Migrations **none allocated by this audit; reserve only if implementation requires one** · Screens **existing affected surfaces identified below; no new screen IDs allocated**

**Priority:** P2 (audit recommendation, not a programme phase). **Evidence class:** Reported / UI check. **Applies to:** Opening-stock onboarding.

## Scope

### What happens / remaining gap

A seeded child-grid filter has no matching filter strip; the reported consequence is difficulty isolating invalid rows.

### Required work

Add a supported filter or align metadata and error-download workflow.

### Boundary and ownership

This task tracks one finding from the warehouse-only audit. Complete the work or evidence needed for the affected existing workflow. Planning, forecasting, optimization and competitor feature work are excluded. Optional-module work applies only to the stated scope. Existing web-only/online-only decisions and removed-adapter decisions remain authoritative. An intentional limit is closed by enforcing/documenting the supported boundary unless a later explicit scope decision authorizes expansion.

## Evidence and affected code

[#181](https://github.com/neetub1508/warehouse-issues/issues/181); [warehouse/frontend/src/components/whOpeningStock/WhOpeningStockViewModal.tsx](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse/frontend/src/components/whOpeningStock/WhOpeningStockViewModal.tsx).

Audit code baseline: `neetub1508/classic@0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa`. Design baseline: `neetub1508/warehouse-issues@7b96725eb5850748cd94b2a784466cb16728a55d`.

Recheck the affected path at the implementation commit. “Reported” and “verification gap” do not mean a fresh runtime failure; “code-supported” does not mean a live reproduction. Preserve that distinction in the resolution.

## Requirements closed

The existing warehouse behavior described in Scope and Acceptance. This audit does not allocate new FR identifiers or claim any requirement already closed. Reuse the adopted requirements in related task sources; record exact applicable IDs when implementing instead of inventing them.

## Scenarios closed

No scenario is newly marked passed by creating this task. Execute the finding-specific acceptance below and affected refusal/retry paths. Record the current commit, supported module configuration, fixture, role, steps and actual results; reuse catalogue scenarios where they apply.

## Closes

Audit finding **W27** once its acceptance is met and evidence is linked. This issue does not automatically close or reopen earlier tasks.

### Related issues / existing implementation ownership

- #181 — wh_opening_stock_lines.validationStatus: a seeded filter row nothing can consume.

These links preserve earlier ownership/history. Coordinate overlapping implementation in one change and link both issues; do not build a second competing implementation. Closed duplicates remain closed.

## Traps

- Follow `docs/DECISIONS.md` and its adopted settings amendment; older task wording is historical where superseded.
- Preserve stock/valuation lineage, tenant/site/owner scope and existing service ownership on affected paths.
- Do not interpret a missing runtime test as proof that the feature is missing. Verify before replacing working code.

## Acceptance

- [ ] An operator can isolate invalid rows in a large staged batch and export/fix them without scanning all rows.
- [ ] Verify current behavior against the cited evidence; record which concern is reproduced, already resolved, accepted by an existing decision, or still awaiting applicable integration evidence.
- [ ] Relevant flow check — **Reports/export/search**: UI/filter/export parity, literal wildcard input, timezone dates, cost masking and scoped scheduled delivery. Limit this task to its finding; link adjacent tasks for the rest.
- [ ] Run the targeted automated/runtime checks needed for this change, plus required module gates; retain actual results. A skipped integration test or code read is not a runtime pass.
- [ ] Update affected contract/help/runbook text and the related issue evidence so the supported behavior agrees across code and documentation.
- [ ] List remaining conditional dependencies explicitly; do not close an enabled workflow with unverified stock integrity, access control or external-state recovery.

## Earlier report detail (reference, verify against current code)

The following preserves the original observations/reproduction details. It is historical context; the Scope and adopted decisions above govern implementation.

<details>
<summary>Source issue #181</summary>

Found while closing P2-20 (#136): the `whGridFilterParity` "binds every configured grid to a page" assertion had been red since the day it was written, on this one grid.

**The state.** `V510090:676` seeds one `filter_definitions` row — `wh_opening_stock_lines.validationStatus`, `select`, `default_visible = true`. There is no page for that grid identifier. The rows render as a CHILD table inside `warehouse/frontend/src/components/whOpeningStock/WhOpeningStockViewModal.tsx` (batch detail, javadoc `:44`) through `ViewModalBase`'s `DataTable` at `:290`, which passes no `gridIdentifier` and names no `COMMON_FILTER_CONFIGS` scope. So there is no filter strip, and nothing reads the seeded row — the operator cannot narrow a long staged batch to just its failed rows, which is the one thing that row was seeded to let them do.

P2-20 recorded the fact rather than papering over it: `wh_opening_stock_lines` is now named in `GRIDS_WITHOUT_A_PAGE` in `warehouse/frontend/src/__tests__/whGridFilterParity.test.ts`, whose javadoc no longer claims every `wh_` grid has a page. That makes the gate honest; it does not decide what should happen.

**The product call, which P2-20 did not make.** Either

- **give the child grid its filter** — a `validationStatus` select on the modal's staged-rows table, reading the seeded row, with a `COMMON_FILTER_CONFIGS` scope of its own; then remove the entry from `GRIDS_WITHOUT_A_PAGE`; or
- **declare the row dead** and leave it. `V510090` is APPLIED and must never be edited, not even its comments (`db-migrate` is the Flyway CLI with validate-on-migrate and no repair — a checksum change stops the whole stack starting), so retiring it means a new migration deleting that one row, not a change to `V510090`.

Recommendation: the first. A staged opening-stock batch is exactly the place an operator wants to see only the rows that failed validation, and the seed shows that was the intent.

</details>

<!-- warehouse-readiness-finding: 2026-10-01/W27 -->
