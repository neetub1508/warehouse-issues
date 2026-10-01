TITLE: [Warehouse] [Finding] W29 · Handover shipment picker renders a null name
LABELS: task,warehouse
issue: 223
---
Part of #1 · Audit **warehouse-only readiness, 2026-10-01** · Finding **W29** · Module **`warehouse`** · Migrations **none allocated by this audit; reserve only if implementation requires one** · Screens **existing affected surfaces identified below; no new screen IDs allocated**

**Priority:** P3 (audit recommendation, not a programme phase). **Evidence class:** Code-supported. **Applies to:** Carrier handovers.

## Scope

### What happens / remaining gap

Description concatenates tracking with nullable ship-to text.

### Required work

Join only present display fields.

### Boundary and ownership

This task tracks one finding from the warehouse-only audit. Complete the work or evidence needed for the affected existing workflow. Planning, forecasting, optimization and competitor feature work are excluded. Optional-module work applies only to the stated scope. Existing web-only/online-only decisions and removed-adapter decisions remain authoritative. An intentional limit is closed by enforcing/documenting the supported boundary unless a later explicit scope decision authorizes expansion.

## Evidence and affected code

[#194](https://github.com/neetub1508/warehouse-issues/issues/194); [WhHandoverQueryService.java:219](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse/backend/src/main/java/ai/warehouse/service/whhandover/WhHandoverQueryService.java#L219).

Audit code baseline: `neetub1508/classic@0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa`. Design baseline: `neetub1508/warehouse-issues@7b96725eb5850748cd94b2a784466cb16728a55d`.

Recheck the affected path at the implementation commit. “Reported” and “verification gap” do not mean a fresh runtime failure; “code-supported” does not mean a live reproduction. Preserve that distinction in the resolution.

## Requirements closed

The existing warehouse behavior described in Scope and Acceptance. This audit does not allocate new FR identifiers or claim any requirement already closed. Reuse the adopted requirements in related task sources; record exact applicable IDs when implementing instead of inventing them.

## Scenarios closed

No scenario is newly marked passed by creating this task. Execute the finding-specific acceptance below and affected refusal/retry paths. Record the current commit, supported module configuration, fixture, role, steps and actual results; reuse catalogue scenarios where they apply.

## Closes

Audit finding **W29** once its acceptance is met and evidence is linked. This issue does not automatically close or reopen earlier tasks.

### Related issues / existing implementation ownership

- #194 — [Warehouse] Handovers: shipment picker shows literal "TRACKING - null" when ship-to name is blank.

These links preserve earlier ownership/history. Coordinate overlapping implementation in one change and link both issues; do not build a second competing implementation. Closed duplicates remain closed.

## Traps

- Follow `docs/DECISIONS.md` and its adopted settings amendment; older task wording is historical where superseded.
- Preserve stock/valuation lineage, tenant/site/owner scope and existing service ownership on affected paths.
- Do not interpret a missing runtime test as proof that the feature is missing. Verify before replacing working code.

## Acceptance

- [ ] Tracking-only and name-only shipments have clean labels with no literal null.
- [ ] Verify current behavior against the cited evidence; record which concern is reproduced, already resolved, accepted by an existing decision, or still awaiting applicable integration evidence.
- [ ] Relevant flow check — **Reports/export/search**: UI/filter/export parity, literal wildcard input, timezone dates, cost masking and scoped scheduled delivery. Limit this task to its finding; link adjacent tasks for the rest.
- [ ] Run the targeted automated/runtime checks needed for this change, plus required module gates; retain actual results. A skipped integration test or code read is not a runtime pass.
- [ ] Update affected contract/help/runbook text and the related issue evidence so the supported behavior agrees across code and documentation.
- [ ] List remaining conditional dependencies explicitly; do not close an enabled workflow with unverified stock integrity, access control or external-state recovery.

## Earlier report detail (reference, verify against current code)

The following preserves the original observations/reproduction details. It is historical context; the Scope and adopted decisions above govern implementation.

<details>
<summary>Source issue #194</summary>

**What happens**
The Add/Edit Handover modal's shipment picker (`GET /warehouse/outbound/handovers/shipment-options`) builds each option's subtitle as `trackingNumber + " - " + shipToName`. The null guard only checks `trackingNumber == null`; it does not check `shipToName == null`. Any DISPATCHED shipment that has a tracking number but no ship-to name (routine — `shipToName` is optional on `WhShipmentRequest` and is often left blank) renders the literal string `"null"` in the dropdown, e.g. `"000004 — ZZQATRACK4 - null"`.

**Reproduce**
```bash
# Fixture: shipment a4476f11-4b4c-48f0-adf4-5e62d483bdc1 (site ZZQADOCK59376, carrier ZZQAWHCARR1), DISPATCHED with trackingNumber=ZZQATRACK4 and no shipToName set.
curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/warehouse/outbound/handovers/shipment-options?warehouseId=e32c957b-7b8c-4435-b1f9-77d78a867187&carrierId=24a04be8-ce83-4249-a42e-7559e840dc6e"
```
→ `[{"id":"a4476f11-4b4c-48f0-adf4-5e62d483bdc1","code":"000004","name":"000004","description":"ZZQATRACK4 - null","isActive":true}]`

Frontend renders this directly: `warehouse/frontend/src/components/whHandover/WhHandoverModal.tsx:308` (`option.description ? \`${option.name} — ${option.description}\` : option.name`), so the picker shows `000004 — ZZQATRACK4 - null`.

**Expected**
When `shipToName` is null, the description should be just the tracking number (or blank if neither is present) — never the literal string `"null"`.

**Cause**
`warehouse/backend/src/main/java/ai/warehouse/service/whhandover/WhHandoverQueryService.java:219` — `.description(row[2] == null ? (String) row[3] : row[2] + " - " + row[3])` only null-checks `row[2]` (trackingNumber); when `row[2]` is present and `row[3]` (shipToName) is null, the concatenation includes the literal string `"null"`.

**User impact**
Anyone preparing a handover sees a shipment option labelled with a garbage `"- null"` suffix in the picker — looks broken/untrustworthy even though the shipment itself is fine.

</details>

<!-- warehouse-readiness-finding: 2026-10-01/W29 -->
