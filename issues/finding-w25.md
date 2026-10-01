TITLE: [Warehouse] [Finding] W25 · Stock-to-GL search treats literal wildcards as patterns
LABELS: task,warehouse,warehouse-base
issue: 219
---
Part of #1 · Audit **warehouse-only readiness, 2026-10-01** · Finding **W25** · Module **`warehouse-base`, `warehouse`** · Migrations **none allocated by this audit; reserve only if implementation requires one** · Screens **existing affected surfaces identified below; no new screen IDs allocated**

**Priority:** P2 (audit recommendation, not a programme phase). **Evidence class:** Reported. **Applies to:** Stock-to-GL reporting.

## Scope

### What happens / remaining gap

The issue records unescaped percent/underscore matching in a bound LIKE parameter. This is search semantics, not SQL injection.

### Required work

Verify current query and escape literal search consistently.

### Boundary and ownership

This task tracks one finding from the warehouse-only audit. Complete the work or evidence needed for the affected existing workflow. Planning, forecasting, optimization and competitor feature work are excluded. Optional-module work applies only to the stated scope. Existing web-only/online-only decisions and removed-adapter decisions remain authoritative. An intentional limit is closed by enforcing/documenting the supported boundary unless a later explicit scope decision authorizes expansion.

## Evidence and affected code

[#180](https://github.com/neetub1508/warehouse-issues/issues/180).

Audit code baseline: `neetub1508/classic@0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa`. Design baseline: `neetub1508/warehouse-issues@7b96725eb5850748cd94b2a784466cb16728a55d`.

Recheck the affected path at the implementation commit. “Reported” and “verification gap” do not mean a fresh runtime failure; “code-supported” does not mean a live reproduction. Preserve that distinction in the resolution.

## Requirements closed

The existing warehouse behavior described in Scope and Acceptance. This audit does not allocate new FR identifiers or claim any requirement already closed. Reuse the adopted requirements in related task sources; record exact applicable IDs when implementing instead of inventing them.

## Scenarios closed

No scenario is newly marked passed by creating this task. Execute the finding-specific acceptance below and affected refusal/retry paths. Record the current commit, supported module configuration, fixture, role, steps and actual results; reuse catalogue scenarios where they apply.

## Closes

Audit finding **W25** once its acceptance is met and evidence is linked. This issue does not automatically close or reopen earlier tasks.

### Related issues / existing implementation ownership

- #180 — WhStockToGl search: an unescaped LIKE makes '_' and '%' live wildcards.

These links preserve earlier ownership/history. Coordinate overlapping implementation in one change and link both issues; do not build a second competing implementation. Closed duplicates remain closed.

## Traps

- Follow `docs/DECISIONS.md` and its adopted settings amendment; older task wording is historical where superseded.
- Preserve stock/valuation lineage, tenant/site/owner scope and existing service ownership on affected paths.
- Do not interpret a missing runtime test as proof that the feature is missing. Verify before replacing working code.

## Acceptance

- [ ] Searching ITEM_1 does not also match ITEMX1 unless wildcard search is explicitly requested.
- [ ] Verify current behavior against the cited evidence; record which concern is reproduced, already resolved, accepted by an existing decision, or still awaiting applicable integration evidence.
- [ ] Relevant flow check — **Reports/export/search**: UI/filter/export parity, literal wildcard input, timezone dates, cost masking and scoped scheduled delivery. Limit this task to its finding; link adjacent tasks for the rest.
- [ ] Run the targeted automated/runtime checks needed for this change, plus required module gates; retain actual results. A skipped integration test or code read is not a runtime pass.
- [ ] Update affected contract/help/runbook text and the related issue evidence so the supported behavior agrees across code and documentation.
- [ ] List remaining conditional dependencies explicitly; do not close an enabled workflow with unverified stock integrity, access control or external-state recovery.

## Earlier report detail (reference, verify against current code)

The following preserves the original observations/reproduction details. It is historical context; the Scope and adopted decisions above govern implementation.

<details>
<summary>Source issue #180</summary>

Raised while closing P2-20 (#136), which escaped every `LIKE`-bound input in the six report-pack repositories. The canonical reference this pack was mirrored from does not escape, and it is out of scope for #136 — a reference page is read, never edited.

**Where.** `warehouse/backend/src/main/java/ai/warehouse/repository/WhStockToGlRepositoryCustomImpl.java:194-199` binds `:search` into six `LIKE '%…%'` predicates with no `StringUtils.escapeLikePattern(...)`.

**Effect today.** A `_` typed into the WS-040 search box matches any single character and a `%` matches anything. So `ITEM_1` also returns `ITEM-1` and `ITEMX1`, and a bare `%` returns the whole table — a reader searching a code that legitimately contains an underscore (most item and account codes do) gets silently wrong rows, with no error to tell them so. It is not an injection into SQL structure: the value is a bound parameter. It is a wildcard the reader never typed.

**Fix.** One call, at the single bind site, exactly as the report pack now does it:

```java
query.setParameter("search", StringUtils.escapeLikePattern(criteria.search()));
```

`escapeLikePattern` escapes `\\`, `%` and `_` with a backslash (PostgreSQL's default `LIKE` escape, so no `ESCAPE` clause is needed), returns `""` for `""` so the existing `CAST(:search AS TEXT) = ''` short-circuit still fires, and returns `null` for `null`. Escape once per path: verify no caller escapes upstream before adding it.

**Check for siblings while you are there.** `grep -rl escapeLikePattern warehouse/backend` returned exactly one file before P2-20; other pre-existing warehouse repositories may have the same gap.

</details>

<!-- warehouse-readiness-finding: 2026-10-01/W25 -->
