TITLE: [Warehouse] [Finding] W26 · Stock-period Site sort is advertised but unsupported
LABELS: task,warehouse,warehouse-base
issue: 220
---
Part of #1 · Audit **warehouse-only readiness, 2026-10-01** · Finding **W26** · Module **`warehouse-base`** · Migrations **none allocated by this audit; reserve only if implementation requires one** · Screens **existing affected surfaces identified below; no new screen IDs allocated**

**Priority:** P2 (audit recommendation, not a programme phase). **Evidence class:** Code-supported. **Applies to:** Stock period administration.

## Scope

### What happens / remaining gap

The query map excludes warehouseName while the issue records it as a sortable grid field.

### Required work

Align saved preferences, grid metadata and SQL sort support.

### Boundary and ownership

This task tracks one finding from the warehouse-only audit. Complete the work or evidence needed for the affected existing workflow. Planning, forecasting, optimization and competitor feature work are excluded. Optional-module work applies only to the stated scope. Existing web-only/online-only decisions and removed-adapter decisions remain authoritative. An intentional limit is closed by enforcing/documenting the supported boundary unless a later explicit scope decision authorizes expansion.

## Evidence and affected code

[#192](https://github.com/neetub1508/warehouse-issues/issues/192); [WhbStockPeriodQueryService.java:54](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-base/backend/src/main/java/ai/warehousebase/service/whbstockperiod/WhbStockPeriodQueryService.java#L54).

Audit code baseline: `neetub1508/classic@0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa`. Design baseline: `neetub1508/warehouse-issues@7b96725eb5850748cd94b2a784466cb16728a55d`.

Recheck the affected path at the implementation commit. “Reported” and “verification gap” do not mean a fresh runtime failure; “code-supported” does not mean a live reproduction. Preserve that distinction in the resolution.

## Requirements closed

The existing warehouse behavior described in Scope and Acceptance. This audit does not allocate new FR identifiers or claim any requirement already closed. Reuse the adopted requirements in related task sources; record exact applicable IDs when implementing instead of inventing them.

## Scenarios closed

No scenario is newly marked passed by creating this task. Execute the finding-specific acceptance below and affected refusal/retry paths. Record the current commit, supported module configuration, fixture, role, steps and actual results; reuse catalogue scenarios where they apply.

## Closes

Audit finding **W26** once its acceptance is met and evidence is linked. This issue does not automatically close or reopen earlier tasks.

### Related issues / existing implementation ownership

- #192 — [Warehouse Base] Stock Periods: "Site" column marked sortable but sort is silently ignored.

These links preserve earlier ownership/history. Coordinate overlapping implementation in one change and link both issues; do not build a second competing implementation. Closed duplicates remain closed.

## Traps

- Follow `docs/DECISIONS.md` and its adopted settings amendment; older task wording is historical where superseded.
- Preserve stock/valuation lineage, tenant/site/owner scope and existing service ownership on affected paths.
- Do not interpret a missing runtime test as proof that the feature is missing. Verify before replacing working code.

## Acceptance

- [ ] Selecting Site sort produces correct order or the UI no longer offers an unsupported choice.
- [ ] Verify current behavior against the cited evidence; record which concern is reproduced, already resolved, accepted by an existing decision, or still awaiting applicable integration evidence.
- [ ] Relevant flow check — **Reports/export/search**: UI/filter/export parity, literal wildcard input, timezone dates, cost masking and scoped scheduled delivery. Limit this task to its finding; link adjacent tasks for the rest.
- [ ] Run the targeted automated/runtime checks needed for this change, plus required module gates; retain actual results. A skipped integration test or code read is not a runtime pass.
- [ ] Update affected contract/help/runbook text and the related issue evidence so the supported behavior agrees across code and documentation.
- [ ] List remaining conditional dependencies explicitly; do not close an enabled workflow with unverified stock integrity, access control or external-state recovery.

## Earlier report detail (reference, verify against current code)

The following preserves the original observations/reproduction details. It is historical context; the Scope and adopted decisions above govern implementation.

<details>
<summary>Source issue #192</summary>

**What happens**
`grid_column_definitions` marks the `warehouseName` ("Site") column of the `whb_stock_periods` grid as `is_sortable = true`. That flag is read by `GridConfigModal`'s "Default Sort Column" dropdown (`sortableColumns = columnConfigs.filter(c => c.definition.isSortable && c.visible)`), so a user can pick "Site" as their saved default sort and save it. The choice is then silently never honoured, in two independent places:

1. Backend: `WhbStockPeriodQueryService.FIELD_MAPPINGS` deliberately excludes `warehouseName` (it is resolved via a separate batch lookup, not a column on `whb_stock_periods`), so `SqlSortBuilder` falls back to the default sort (`startDate DESC`) whenever `sortBy=warehouseName` is sent — with no error, no warning.
2. Frontend: `page.tsx`'s `VALID_SORT_FIELDS` also excludes `warehouseName`, so even the saved grid preference (`gridOrderBy = 'warehouseName'`) is silently swapped back to `'startDate'` via `safeSortBy = VALID_SORT_FIELDS.includes(sortBy) ? sortBy : 'startDate'`.

The grid's own bespoke table component (`WhbStockPeriodManagementTable.tsx`) hardcodes `sortable: false` on the rendered Site column, so there is no clickable header arrow for it in the live grid — the only user-reachable path to the bug is via Grid Settings' "Default Sort Column" picker, which does list "Site" as a legitimate option because it trusts the DB flag.

**Reproduce**
```bash
TOKEN=$(curl -s -X POST "$API_BASE/auth/login" -H 'Content-Type: application/json' \
  -d '{"email":"<test-user-email>","password":"..."}' | jq -r .accessToken)

# direct sortBy=warehouseName: asc and desc return the identical order
curl -s "$API_BASE/warehouse/ledger/stock-periods/management?page=0&limit=5&sortBy=warehouseName&sortDirection=asc" \
  -H "Authorization: Bearer $TOKEN" | jq -c '.stockPeriods[].periodCode'
curl -s "$API_BASE/warehouse/ledger/stock-periods/management?page=0&limit=5&sortBy=warehouseName&sortDirection=desc" \
  -H "Authorization: Bearer $TOKEN" | jq -c '.stockPeriods[].periodCode'
# both -> ["2026-12","2026-12","2026-11","2026-11","2026-10"] — identical, i.e. silently fell back to the default sort

# Grid Settings will let a user save orderBy=warehouseName as their default sort
curl -s -X POST "$API_BASE/grid-preferences/whb_stock_periods/user-preferences" \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"gridIdentifier":"whb_stock_periods","visibleColumns":["periodCode","warehouseName","startDate"],"columnOrder":["periodCode","warehouseName","startDate"],"orderBy":"warehouseName","orderDirection":"asc","pageSize":20}'
# -> 200, persists orderBy="warehouseName" with no server-side rejection, even though it can never take effect
```

**Expected**
Either the column is truly sortable end to end (add `warehouseName`/a resolvable equivalent to `SqlSortBuilder`'s field map and to `VALID_SORT_FIELDS`), or `grid_column_definitions.is_sortable` for `whb_stock_periods.warehouseName` is `false` so it is never offered as a "Default Sort Column" choice and the saved-preference round trip cannot silently discard the user's selection.

**Cause**
`warehouse-base/backend/src/main/resources/db/migration/V500019__Create_whb_stock_periods_and_overrides.sql:404` seeds `is_sortable = true` for `warehouseName`, contradicting the deliberate exclusion documented at `warehouse-base/backend/src/main/java/ai/warehousebase/service/whbstockperiod/WhbStockPeriodQueryService.java:54` and `warehouse-base/frontend/src/app/dashboard/warehouse/ledger/periods/page.tsx:44-45`.

**User impact**
A user opens Grid Settings, sets "Default Sort Column" to "Site", saves it, and the grid keeps sorting by Start Date on every subsequent load with no indication the preference was not applied.

</details>

<!-- warehouse-readiness-finding: 2026-10-01/W26 -->
