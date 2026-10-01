TITLE: [Warehouse] [Finding] W07 · Approval cost and original-currency evidence require persistence reconciliation
LABELS: task,warehouse,warehouse-base
issue: 201
---
Part of #1 · Audit **warehouse-only readiness, 2026-10-01** · Finding **W07** · Module **`warehouse-base`** · Migrations **none allocated by this audit; reserve only if implementation requires one** · Screens **existing affected surfaces identified below; no new screen IDs allocated**

**Priority:** P1 (audit recommendation, not a programme phase). **Evidence class:** Reported / partial code check. **Applies to:** Approval-gated valued movements.

## Scope

### What happens / remaining gap

The issue reports differences between submitted line cost and approval-time valuation, and missing persisted source amount/rate/source-line identity. Command fields alone do not prove reload after approval preserves them.

### Required work

Trace submitted → pending → approved → line/layer/envelope; choose the adopted immutable persistence approach and migrate accordingly.

### Boundary and ownership

This task tracks one finding from the warehouse-only audit. Complete the work or evidence needed for the affected existing workflow. Planning, forecasting, optimization and competitor feature work are excluded. Optional-module work applies only to the stated scope. Existing web-only/online-only decisions and removed-adapter decisions remain authoritative. An intentional limit is closed by enforcing/documenting the supported boundary unless a later explicit scope decision authorizes expansion.

## Evidence and affected code

[#170](https://github.com/neetub1508/warehouse-issues/issues/170); [WhbStockLedgerWriter.java:879](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-base/backend/src/main/java/ai/warehousebase/service/ledger/writer/WhbStockLedgerWriter.java#L879).

Audit code baseline: `neetub1508/classic@0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa`. Design baseline: `neetub1508/warehouse-issues@7b96725eb5850748cd94b2a784466cb16728a55d`.

Recheck the affected path at the implementation commit. “Reported” and “verification gap” do not mean a fresh runtime failure; “code-supported” does not mean a live reproduction. Preserve that distinction in the resolution.

## Requirements closed

The existing warehouse behavior described in Scope and Acceptance. This audit does not allocate new FR identifiers or claim any requirement already closed. Reuse the adopted requirements in related task sources; record exact applicable IDs when implementing instead of inventing them.

## Scenarios closed

No scenario is newly marked passed by creating this task. Execute the finding-specific acceptance below and affected refusal/retry paths. Record the current commit, supported module configuration, fixture, role, steps and actual results; reuse catalogue scenarios where they apply.

## Closes

Audit finding **W07** once its acceptance is met and evidence is linked. This issue does not automatically close or reopen earlier tasks.

### Related issues / existing implementation ownership

- #170 — [Warehouse] P2-16 follow-up · Movement lines keep the approved cost, the source-currency amount and the cost source line.

These links preserve earlier ownership/history. Coordinate overlapping implementation in one change and link both issues; do not build a second competing implementation. Closed duplicates remain closed.

## Traps

- Follow `docs/DECISIONS.md` and its adopted settings amendment; older task wording is historical where superseded.
- Preserve stock/valuation lineage, tenant/site/owner scope and existing service ownership on affected paths.
- Do not interpret a missing runtime test as proof that the feature is missing. Verify before replacing working code.

## Acceptance

- [ ] After restart and approval, reports, layers and handover values agree; source currency and originating cost line remain recoverable.
- [ ] Verify current behavior against the cited evidence; record which concern is reproduced, already resolved, accepted by an existing decision, or still awaiting applicable integration evidence.
- [ ] Relevant flow check — **Valuation and period close**: Old surviving stock, backdated events, FIFO/average, rounding, policy changes and period refusal. Limit this task to its finding; link adjacent tasks for the rest.
- [ ] Run the targeted automated/runtime checks needed for this change, plus required module gates; retain actual results. A skipped integration test or code read is not a runtime pass.
- [ ] Update affected contract/help/runbook text and the related issue evidence so the supported behavior agrees across code and documentation.
- [ ] List remaining conditional dependencies explicitly; do not close an enabled workflow with unverified stock integrity, access control or external-state recovery.

## Earlier report detail (reference, verify against current code)

The following preserves the original observations/reproduction details. It is historical context; the Scope and adopted decisions above govern implementation.

<details>
<summary>Source issue #170</summary>

Follow-up from #115 (P2-16 costing engine) · Module **`warehouse-base`** · Migration: one base migration — number to be reserved here

## Scope
Three gaps the costing engine leaves because each needs a column on `whb_stock_movement_lines` (the I-2 trigger forbids updating a posted line):
1. **Approval-gated movements** (ADJUST_*, SCRAP, COUNT_ADJUST, OWNER_CHANGE, TRANSIT_LOSS) get their layers and hand accounting the engine's value at approval, but the line itself keeps its submitted cost and has no `moving_average_after`. Decide with the P0-02 owner: extend the I-2 allowlist for these two columns at approval, or a side table.
2. **Source-currency evidence (OD-16):** the line stores base-currency cost; the original amount and rate ("USD 42 at 88.415") are only on the layer. Add the source amount and rate to the line.
3. **`cost_source_line_id`** is not stored, so a matched return that goes to approval loses its link to the issue line and is costed as unmatched on approval.

## Acceptance
1. An approved scrap shows the same unit cost on its movement line, on the layer consumption and in the accounting hand-over.
2. A USD receipt shows USD 42 and 88.415 on its movement line.
3. A matched customer return that needs approval restores the original issue's layers once approved.

</details>

<!-- warehouse-readiness-finding: 2026-10-01/W07 -->
