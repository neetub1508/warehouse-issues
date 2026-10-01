TITLE: [Warehouse] [Finding] W04 · Style/variant matrix has no supported style-creation path found
LABELS: task,warehouse,warehouse-base
issue: 198
---
Part of #1 · Audit **warehouse-only readiness, 2026-10-01** · Finding **W04** · Module **`warehouse-base`** · Migrations **none allocated by this audit; reserve only if implementation requires one** · Screens **existing affected surfaces identified below; no new screen IDs allocated**

**Priority:** P1 (audit recommendation, not a programme phase). **Evidence class:** Code-supported. **Applies to:** Variant/style feature.

## Scope

### What happens / remaining gap

Style reads require style-axis associations. Searches found readers and a migration self-test, but no production association writer.

### Required work

Provide a supported association setup flow, or disable the advertised matrix capability until it exists.

### Boundary and ownership

This task tracks one finding from the warehouse-only audit. Complete the work or evidence needed for the affected existing workflow. Planning, forecasting, optimization and competitor feature work are excluded. Optional-module work applies only to the stated scope. Existing web-only/online-only decisions and removed-adapter decisions remain authoritative. An intentional limit is closed by enforcing/documenting the supported boundary unless a later explicit scope decision authorizes expansion.

## Evidence and affected code

[#191](https://github.com/neetub1508/warehouse-issues/issues/191); [WhbStyleVariantAxisRepository.java:1](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-base/backend/src/main/java/ai/warehousebase/repository/WhbStyleVariantAxisRepository.java#L1); [WhbVariantMatrixRepository.java:1](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-base/backend/src/main/java/ai/warehousebase/repository/WhbVariantMatrixRepository.java#L1).

Audit code baseline: `neetub1508/classic@0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa`. Design baseline: `neetub1508/warehouse-issues@7b96725eb5850748cd94b2a784466cb16728a55d`.

Recheck the affected path at the implementation commit. “Reported” and “verification gap” do not mean a fresh runtime failure; “code-supported” does not mean a live reproduction. Preserve that distinction in the resolution.

## Requirements closed

The existing warehouse behavior described in Scope and Acceptance. This audit does not allocate new FR identifiers or claim any requirement already closed. Reuse the adopted requirements in related task sources; record exact applicable IDs when implementing instead of inventing them.

## Scenarios closed

No scenario is newly marked passed by creating this task. Execute the finding-specific acceptance below and affected refusal/retry paths. Record the current commit, supported module configuration, fixture, role, steps and actual results; reuse catalogue scenarios where they apply.

## Closes

Audit finding **W04** once its acceptance is met and evidence is linked. This issue does not automatically close or reopen earlier tasks.

### Related issues / existing implementation ownership

- #191 — [Warehouse Base] Style x Variant Matrix: no code path ever creates a "style" — page is permanently empty.

These links preserve earlier ownership/history. Coordinate overlapping implementation in one change and link both issues; do not build a second competing implementation. Closed duplicates remain closed.

## Traps

- Follow `docs/DECISIONS.md` and its adopted settings amendment; older task wording is historical where superseded.
- Preserve stock/valuation lineage, tenant/site/owner scope and existing service ownership on affected paths.
- Do not interpret a missing runtime test as proof that the feature is missing. Verify before replacing working code.

## Acceptance

- [ ] A fresh install can create a style, assign axes, create variants and use a ratio-pack template without direct SQL.
- [ ] Verify current behavior against the cited evidence; record which concern is reproduced, already resolved, accepted by an existing decision, or still awaiting applicable integration evidence.
- [ ] Relevant flow check — **Site/owner/item setup**: Create masters and required associations through UI; effective dates, invalid setups and per-site sourcing behave consistently. Limit this task to its finding; link adjacent tasks for the rest.
- [ ] Run the targeted automated/runtime checks needed for this change, plus required module gates; retain actual results. A skipped integration test or code read is not a runtime pass.
- [ ] Update affected contract/help/runbook text and the related issue evidence so the supported behavior agrees across code and documentation.
- [ ] List remaining conditional dependencies explicitly; do not close an enabled workflow with unverified stock integrity, access control or external-state recovery.

## Earlier report detail (reference, verify against current code)

The following preserves the original observations/reproduction details. It is historical context; the Scope and adopted decisions above govern implementation.

<details>
<summary>Source issue #191</summary>

**What happens**
An item counts as a "style" only via a row in `whb_style_variant_axes` (see `WhbVariantMatrixRepository.findItemAsStyle`'s `EXISTS (SELECT 1 FROM whb_style_variant_axes ...)` check). `WhbStyleVariantAxisRepository` is referenced only from read-only code (`WhbItemValidationService`, `WhbItemQueryService`, `WhbVariantMatrixQueryService`) across the entire warehouse-base backend — nothing ever calls `.save()` on it. On the running stack `SELECT count(*) FROM whb_style_variant_axes` = 0, even though items, owners and variant axes all exist. The sole `INSERT INTO whb_style_variant_axes` in the codebase is inside migration `V500090`'s self-test `DO $$` block, which deliberately rolls back via sentinel SQLSTATE `WB090` and leaves no row behind. Result: `GET /styles` always returns `[]`, `GET /styles/{id}` 404s for every item, and `POST /templates` 422s for every `styleItemId` — permanently, on every install.

**Reproduce**
```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  'http://localhost:8000/api/v1/warehouse/masters/variant-matrix/styles?limit=20'
# -> [] HTTP 200

curl -s -H "Authorization: Bearer $TOKEN" \
  'http://localhost:8000/api/v1/warehouse/masters/variant-matrix/styles/08d91a21-da78-4f7f-be7b-af1ff9933b43'
# -> HTTP 404 {"error":"RESOURCE_NOT_FOUND","message":"Item ZZQA0928223458-SKU is not a style - it is a variant, or it varies along no axis."}

curl -s -X POST -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"code":"ZZQAMTX1","name":"QA Pack","styleItemId":"08d91a21-da78-4f7f-be7b-af1ff9933b43","packQuantity":10,"lines":[]}' \
  'http://localhost:8000/api/v1/warehouse/masters/variant-matrix/templates'
# -> HTTP 422 {"error":"RATIO_PACK_STYLE_NOT_A_STYLE","validation_errors":{"styleItemId":"Item ZZQA0928223458-SKU varies along no axis, so it has no variants to pack."}}
```
`SELECT count(*) FROM whb_style_variant_axes;` on the platform-postgres container returns `0`.

**Expected**
Some application-reachable path (item-master create/edit, a dedicated "mark as style + choose axes" action, or an import handler) must insert into `whb_style_variant_axes` so an item can actually become a style, matching the read side that already exists (`WhbVariantMatrixQueryService.getMatrix`, `WhbRatioPackTemplateService`).

**Cause**
`warehouse-base/backend/src/main/java/ai/warehousebase/repository/WhbStyleVariantAxisRepository.java` — no application writer anywhere in the codebase. `warehouse-base/backend/src/main/resources/db/migration/V500090__Create_whb_ratio_pack_templates_and_lines_with_variant_screens.sql:662` is the only INSERT and it lives inside a rolled-back migration self-test. `WhbItemRequest` (`warehouse-base/backend/src/main/java/ai/warehousebase/dto/request/WhbItemRequest.java`) has no field to declare an item's own axis set — its `styleItemId` is only the variant→style pointer.

**User impact**
The "Style x Variant Matrix" page (`masters/variant-matrix`) can never show a matrix — the style picker is permanently empty for every installation. "Add Ratio Pack" can never succeed against any real item, since every `styleItemId` is refused as "varies along no axis". The entire WS-033 feature is dead on arrival unless a DBA hand-writes rows directly into `whb_style_variant_axes`.

</details>

<!-- warehouse-readiness-finding: 2026-10-01/W04 -->
