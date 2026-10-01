TITLE: [Warehouse] [Finding] W01 · Historical stock report can omit older surviving stock
LABELS: task,warehouse
issue: 195
---
Part of #1 · Audit **warehouse-only readiness, 2026-10-01** · Finding **W01** · Module **`warehouse`** · Migrations **none allocated by this audit; reserve only if implementation requires one** · Screens **existing affected surfaces identified below; no new screen IDs allocated**

**Priority:** P0 (audit recommendation, not a programme phase). **Evidence class:** Code-supported. **Applies to:** Stock As-At reporting.

## Scope

### What happens / remaining gap

The current query sums movements only in the preceding 365 days. It is not an all-time balance if stock predates that window. A footer stating the window does not make it a correct balance.

### Required work

Use a valid opening snapshot plus deltas, or a complete balance computation with measured performance.

### Boundary and ownership

This task tracks one finding from the warehouse-only audit. Complete the work or evidence needed for the affected existing workflow. Planning, forecasting, optimization and competitor feature work are excluded. Optional-module work applies only to the stated scope. Existing web-only/online-only decisions and removed-adapter decisions remain authoritative. An intentional limit is closed by enforcing/documenting the supported boundary unless a later explicit scope decision authorizes expansion.

## Evidence and affected code

[#179](https://github.com/neetub1508/warehouse-issues/issues/179); [WhStockAsAtQueryService.java:129](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse/backend/src/main/java/ai/warehouse/service/whstockasat/WhStockAsAtQueryService.java#L129); [WhStockAsAtRepositoryCustomImpl.java:105](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse/backend/src/main/java/ai/warehouse/repository/WhStockAsAtRepositoryCustomImpl.java#L105).

Audit code baseline: `neetub1508/classic@0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa`. Design baseline: `neetub1508/warehouse-issues@7b96725eb5850748cd94b2a784466cb16728a55d`.

Recheck the affected path at the implementation commit. “Reported” and “verification gap” do not mean a fresh runtime failure; “code-supported” does not mean a live reproduction. Preserve that distinction in the resolution.

## Requirements closed

The existing warehouse behavior described in Scope and Acceptance. This audit does not allocate new FR identifiers or claim any requirement already closed. Reuse the adopted requirements in related task sources; record exact applicable IDs when implementing instead of inventing them.

## Scenarios closed

No scenario is newly marked passed by creating this task. Execute the finding-specific acceptance below and affected refusal/retry paths. Record the current commit, supported module configuration, fixture, role, steps and actual results; reuse catalogue scenarios where they apply.

## Closes

Audit finding **W01** once its acceptance is met and evidence is linked. This issue does not automatically close or reopen earlier tasks.

### Related issues / existing implementation ownership

- #179 — [Warehouse] P2-20 · WS-224's 365-day lower bound makes the as-at quantity a windowed net, not an all-time balance.

These links preserve earlier ownership/history. Coordinate overlapping implementation in one change and link both issues; do not build a second competing implementation. Closed duplicates remain closed.

## Traps

- Follow `docs/DECISIONS.md` and its adopted settings amendment; older task wording is historical where superseded.
- Preserve stock/valuation lineage, tenant/site/owner scope and existing service ownership on affected paths.
- Do not interpret a missing runtime test as proof that the feature is missing. Verify before replacing working code.

## Acceptance

- [ ] Stock received more than 365 days earlier, with no later movement, appears correctly; compare report with independent ledger reconstruction.
- [ ] Verify current behavior against the cited evidence; record which concern is reproduced, already resolved, accepted by an existing decision, or still awaiting applicable integration evidence.
- [ ] Relevant flow check — **Valuation and period close**: Old surviving stock, backdated events, FIFO/average, rounding, policy changes and period refusal. Limit this task to its finding; link adjacent tasks for the rest.
- [ ] Run the targeted automated/runtime checks needed for this change, plus required module gates; retain actual results. A skipped integration test or code read is not a runtime pass.
- [ ] Update affected contract/help/runbook text and the related issue evidence so the supported behavior agrees across code and documentation.
- [ ] List remaining conditional dependencies explicitly; do not close an enabled workflow with unverified stock integrity, access control or external-state recovery.

## Earlier report detail (reference, verify against current code)

The following preserves the original observations/reproduction details. It is historical context; the Scope and adopted decisions above govern implementation.

<details>
<summary>Source issue #179</summary>

Raised by the WS-224 build, flagged for a ruling rather than decided.

## What was built
PP-7 says a ledger-scale report must not open on "all time", and the module's shipped answer (`WhInTransitAgeingQueryService`) defaults a lower bound of **365 days**. WS-224 Stock As-At follows it: `WhStockAsAtQueryService.criteria(...)` sets `movedFrom = asAtDateTime.minusDays(DEFAULT_WINDOW_DAYS)`, and the SQL sums `whb_stock_movement_lines` over `[movedFrom, asAtDateTime]`.

## The concern
Because the bound restricts **which movements are summed**, the reported quantity is the net over that window, **not an all-time on-hand balance**. That is only correct when the window reaches back to the ledger's `OPENING_BALANCE` movements.

It happens to hold for the common readings — 365 days back from a 31-March or 30-September date does reach an FY-start opening balance — which is why the build kept it. But WS-224 is exactly the screen someone uses for a **statutory 44AB, bank or year-end stock statement**, and a grain that has not moved in over a year is silently netted to whatever happened inside the window.

## Why it was not resolved in the task
The alternative reading — bound only row *discovery* and sum all-time — omits dormant grains entirely, which is worse because it is invisible rather than merely narrow. Neither reading is obviously right, and `V511066` seeds no `movedFrom` filter key, so the window is not something the user can widen from the screen.

## Mitigation already in place
The applied window is echoed from `/management` as `movedFrom` + `asAtDateTime`, stated in the page footer in plain words, and repeated in the View modal beside the quantity. The figure does not pass itself off as all-time.

## Options
1. **Keep 365 days** (current). Cheapest; correct for FY-boundary readings; documented on screen.
2. **Make the window reach the last `OPENING_BALANCE` movement per grain**, so the balance is true whatever the date. Correct, more expensive, and needs an index to stay sane.
3. **Expose `movedFrom` as a real filter** so the reader chooses, with the default staying 365 days. Needs a `filter_definitions` row, so a migration.

The single constant is `WhStockAsAtQueryService.DEFAULT_WINDOW_DAYS`.

Related: **#178** (OD-20). P2-20 is otherwise unblocked by this — it is a correctness question about the default, not a build blocker.

</details>

<!-- warehouse-readiness-finding: 2026-10-01/W01 -->
