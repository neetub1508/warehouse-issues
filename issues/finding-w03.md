TITLE: [Warehouse] [Finding] W03 · Blank unit on imported/direct demand order is not defaulted
LABELS: task,warehouse
issue: 197
---
Part of #1 · Audit **warehouse-only readiness, 2026-10-01** · Finding **W03** · Module **`warehouse`** · Migrations **none allocated by this audit; reserve only if implementation requires one** · Screens **existing affected surfaces identified below; no new screen IDs allocated**

**Priority:** P1 (audit recommendation, not a programme phase). **Evidence class:** Code-supported. **Applies to:** Demand orders and channel imports.

## Scope

### What happens / remaining gap

Validation passes the nullable request unit to the conversion guard despite the request contract promising the item base unit as default.

### Required work

Normalize omitted/blank unit once before validation and persistence; return line-specific errors for invalid supplied units.

### Boundary and ownership

This task tracks one finding from the warehouse-only audit. Complete the work or evidence needed for the affected existing workflow. Planning, forecasting, optimization and competitor feature work are excluded. Optional-module work applies only to the stated scope. Existing web-only/online-only decisions and removed-adapter decisions remain authoritative. An intentional limit is closed by enforcing/documenting the supported boundary unless a later explicit scope decision authorizes expansion.

## Evidence and affected code

[#193](https://github.com/neetub1508/warehouse-issues/issues/193); [WhDemandOrderValidationService.java:214](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse/backend/src/main/java/ai/warehouse/service/whdemandorder/WhDemandOrderValidationService.java#L214).

Audit code baseline: `neetub1508/classic@0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa`. Design baseline: `neetub1508/warehouse-issues@7b96725eb5850748cd94b2a784466cb16728a55d`.

Recheck the affected path at the implementation commit. “Reported” and “verification gap” do not mean a fresh runtime failure; “code-supported” does not mean a live reproduction. Preserve that distinction in the resolution.

## Requirements closed

The existing warehouse behavior described in Scope and Acceptance. This audit does not allocate new FR identifiers or claim any requirement already closed. Reuse the adopted requirements in related task sources; record exact applicable IDs when implementing instead of inventing them.

## Scenarios closed

No scenario is newly marked passed by creating this task. Execute the finding-specific acceptance below and affected refusal/retry paths. Record the current commit, supported module configuration, fixture, role, steps and actual results; reuse catalogue scenarios where they apply.

## Closes

Audit finding **W03** once its acceptance is met and evidence is linked. This issue does not automatically close or reopen earlier tasks.

### Related issues / existing implementation ownership

- #193 — [Warehouse] Channel order import rejects lines with no uomCode instead of defaulting to the item's base unit.

These links preserve earlier ownership/history. Coordinate overlapping implementation in one change and link both issues; do not build a second competing implementation. Closed duplicates remain closed.

## Implementation order and dependencies

**Recommended wave:** 1 — Protect stock, value and core operator flows. This is a scheduling recommendation, not a requirement to finish every lower-wave issue before starting independent work.

### Before dependent implementation

- No mandatory start dependency on another finding is identified. Begin current-code verification and this task’s scoped work immediately, subject to the setup/decision prerequisites below.

### Before final acceptance / closure

- No mandatory whole-issue completion dependency is identified. Meet this task’s acceptance and any applicable handoff/external prerequisites before closure.
- Preparatory analysis, fixtures and independent fixes can proceed while prerequisites are open. If a prerequisite is already satisfied in current code, link its commit/test evidence instead of waiting or rebuilding it.

### Setup, decisions and conditional dependencies

Confirm item base UOM and conversion rules; cover direct demand order and current channel-import callers.

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
- [ ] Direct API and channel import with omitted UOM use the item base unit; explicit incompatible UOM is refused atomically.
- [ ] Verify current behavior against the cited evidence; record which concern is reproduced, already resolved, accepted by an existing decision, or still awaiting applicable integration evidence.
- [ ] Relevant flow check — **Purchase and receipt**: Partial/over/foreign-currency receipt, duplicate submission, lot/serial/UOM and receipt evidence. Limit this task to its finding; link adjacent tasks for the rest.
- [ ] Run the targeted automated/runtime checks needed for this change, plus required module gates; retain actual results. A skipped integration test or code read is not a runtime pass.
- [ ] Update affected contract/help/runbook text and the related issue evidence so the supported behavior agrees across code and documentation.
- [ ] List remaining conditional dependencies explicitly; do not close an enabled workflow with unverified stock integrity, access control or external-state recovery.

## Earlier report detail (reference, verify against current code)

The following preserves the original observations/reproduction details. It is historical context; the Scope and adopted decisions above govern implementation.

<details>
<summary>Source issue #193</summary>

**What happens**
`WhChannelOrderImportRequest.Line.uomCode`'s own javadoc says "Blank means the item's base unit." In practice, omitting `uomCode` on a line does NOT default to the item's base unit — the import is REJECTED with `reason: "Both units are required"` and `failedField: "order"` (not even the specific line). Most external marketplace/storefront payloads never carry the warehouse's internal UOM codes, so this is the common case, not an edge case — it defeats the "the order never came through" design the controller's own javadoc describes.

**Reproduce**
```bash
curl -s -X POST http://localhost:8000/api/v1/warehouse/outbound/channel-order-imports/import \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"channelAccountId":"40379db9-7ecd-4681-b2ad-9750bb99ba51","externalOrderId":"ZZQAIMPORT002152","externalVersion":1,
       "order":{"shipToName":"QA Ship To","shipToAddressLine1":"1 QA St","shipToCity":"QA City","shipToCountryCode":"IN",
                "paymentMode":"PREPAID","lines":[{"itemCode":"ITM-00000002","quantity":1}]}}'
```
Response: `201 {"outcome":"REJECTED","reason":"Both units are required","failedField":"order", ...}`

The identical payload with `"uomCode":"EA"` added to the line (the item's own `baseUomCode`) returns `201 {"outcome":"CREATED","demandOrderNumber":"000003", ...}`. Re-running the REJECTED row (`PATCH /{id}/rerun`) reproduces the identical rejection deterministically, confirming it is not transient.

**Expected**
A line with no `uomCode` should resolve to the item's base unit (factor 1, same-unit) and the order should import normally, per the field's own documented contract.

**Cause**
`warehouse/backend/src/main/java/ai/warehouse/service/whchannelorderimport/WhChannelOrderImportValidationService.java:158` passes a `null` `uomCode` straight through with no base-unit fallback. It reaches `warehouse/backend/src/main/java/ai/warehouse/service/whdemandorder/WhDemandOrderValidationService.java:214-215`, which calls `WhUomConvertibilityGuard.requireConvertible(...)` in `warehouse/backend/src/main/java/ai/warehouse/service/uom/WhUomConvertibilityGuard.java:53`, which unconditionally calls `WhbUomConversionResolver.resolve(itemId, uomCode, baseUomCode, at)` (`warehouse-base/backend/src/main/java/ai/warehousebase/service/whbitemuomconversion/WhbUomConversionResolver.java:43`). That method throws a generic `BusinessException("Both units are required","UOM_REQUIRED",422)` whenever either side is blank — there is no same-as-base-unit special case. `requireConvertible`'s catch block only translates `CONVERSION_NOT_FOUND` into a field-specific error; `UOM_REQUIRED` propagates as a bare `BusinessException` and lands in `WhChannelOrderImportService.fieldOf(BusinessException)` (`WhChannelOrderImportService.java:184-192`), which falls through to the generic `"order"` field — losing the more useful `order.lines[0].uomCode` pointer too.

**User impact**
A marketplace/storefront order with no UOM code on any line — the ordinary case — is silently rejected, and the support agent working the "order never came through" ticket sees only a top-level "order" field with the message "Both units are required," not "the missing unit on line 1."

</details>

<!-- warehouse-readiness-finding: 2026-10-01/W03 -->
