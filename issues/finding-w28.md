TITLE: [Warehouse] [Finding] W28 · Receiving-session export label differs from grid
LABELS: task,warehouse
issue: 222
---
Part of #1 · Audit **warehouse-only readiness, 2026-10-01** · Finding **W28** · Module **`warehouse`** · Migrations **none allocated by this audit; reserve only if implementation requires one** · Screens **existing affected surfaces identified below; no new screen IDs allocated**

**Priority:** P3 (audit recommendation, not a programme phase). **Evidence class:** Code-supported. **Applies to:** Receiving exports.

## Scope

### What happens / remaining gap

Export still labels the site column Warehouse instead of the grid’s Site.

### Required work

Align the label and translations across formats.

### Boundary and ownership

This task tracks one finding from the warehouse-only audit. Complete the work or evidence needed for the affected existing workflow. Planning, forecasting, optimization and competitor feature work are excluded. Optional-module work applies only to the stated scope. Existing web-only/online-only decisions and removed-adapter decisions remain authoritative. An intentional limit is closed by enforcing/documenting the supported boundary unless a later explicit scope decision authorizes expansion.

## Evidence and affected code

[#190](https://github.com/neetub1508/warehouse-issues/issues/190); [WhReceivingSessionExportService.java:77](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse/backend/src/main/java/ai/warehouse/service/WhReceivingSessionExportService.java#L77).

Audit code baseline: `neetub1508/classic@0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa`. Design baseline: `neetub1508/warehouse-issues@7b96725eb5850748cd94b2a784466cb16728a55d`.

Recheck the affected path at the implementation commit. “Reported” and “verification gap” do not mean a fresh runtime failure; “code-supported” does not mean a live reproduction. Preserve that distinction in the resolution.

## Requirements closed

The existing warehouse behavior described in Scope and Acceptance. This audit does not allocate new FR identifiers or claim any requirement already closed. Reuse the adopted requirements in related task sources; record exact applicable IDs when implementing instead of inventing them.

## Scenarios closed

No scenario is newly marked passed by creating this task. Execute the finding-specific acceptance below and affected refusal/retry paths. Record the current commit, supported module configuration, fixture, role, steps and actual results; reuse catalogue scenarios where they apply.

## Closes

Audit finding **W28** once its acceptance is met and evidence is linked. This issue does not automatically close or reopen earlier tasks.

### Related issues / existing implementation ownership

- #190 — [Warehouse] Receiving Sessions export labels the Site column "Warehouse".

These links preserve earlier ownership/history. Coordinate overlapping implementation in one change and link both issues; do not build a second competing implementation. Closed duplicates remain closed.

## Traps

- Follow `docs/DECISIONS.md` and its adopted settings amendment; older task wording is historical where superseded.
- Preserve stock/valuation lineage, tenant/site/owner scope and existing service ownership on affected paths.
- Do not interpret a missing runtime test as proof that the feature is missing. Verify before replacing working code.

## Acceptance

- [ ] Grid, CSV and spreadsheet use the agreed same label.
- [ ] Verify current behavior against the cited evidence; record which concern is reproduced, already resolved, accepted by an existing decision, or still awaiting applicable integration evidence.
- [ ] Relevant flow check — **Reports/export/search**: UI/filter/export parity, literal wildcard input, timezone dates, cost masking and scoped scheduled delivery. Limit this task to its finding; link adjacent tasks for the rest.
- [ ] Run the targeted automated/runtime checks needed for this change, plus required module gates; retain actual results. A skipped integration test or code read is not a runtime pass.
- [ ] Update affected contract/help/runbook text and the related issue evidence so the supported behavior agrees across code and documentation.
- [ ] List remaining conditional dependencies explicitly; do not close an enabled workflow with unverified stock integrity, access control or external-state recovery.

## Earlier report detail (reference, verify against current code)

The following preserves the original observations/reproduction details. It is historical context; the Scope and adopted decisions above govern implementation.

<details>
<summary>Source issue #190</summary>

**What happens**
The Receiving Sessions grid's `warehouseName` column is seeded with display name `Site` (`grid_column_definitions.display_name`), and every other Warehouse export service (`WhAdjustmentRegisterExportService`, `WhWaveExportService`, `WhWorkOrderExportService`, `WhLowStockExportService`, and 15+ more) headers the same concept `Site`. `WhReceivingSessionExportService` is the one outlier that hard-codes `Warehouse`.

**Reproduce**
```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/warehouse/inbound/receiving-sessions/export?format=csv" | head -1
```
Actual header:
```
Session Number,Warehouse,Dock Door,Supplier,Carrier,Vehicle Number,Driver,Seal In,Seal Out,Gate Pass,Arrived At,Started At,Completed At,Status,Documents,GRNs,Created By,Updated By,Created At,Updated At
```
vs. `grid_column_definitions.display_name` for `warehouseName` on `wh_receiving_sessions` = `Site`.

**Expected**
The export header for the `warehouseName` column should read `Site`, matching the grid column label and every other Warehouse export service's convention.

**Cause**
`warehouse/backend/src/main/java/ai/warehouse/service/WhReceivingSessionExportService.java:77` — `getExportHeaders()` uses the literal `"Warehouse"` instead of `"Site"`.

**User impact**
A user who enables the "Site" column in the grid and exports has to guess that the CSV's "Warehouse" column is the same field. Cosmetic — no data loss, filters and row counts are correct — but a real, reproducible naming inconsistency against the module's own convention.

</details>

<!-- warehouse-readiness-finding: 2026-10-01/W28 -->
