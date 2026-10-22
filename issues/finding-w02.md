TITLE: [Warehouse] [Finding] W02 · Zone-less putaway rules can throw during response mapping
LABELS: task,warehouse
issue: 196
---
Part of #1 · Audit **warehouse-only readiness, 2026-10-01** · Finding **W02** · Module **`warehouse`** · Migrations **none allocated by this audit; reserve only if implementation requires one** · Screens **existing affected surfaces identified below; no new screen IDs allocated**

**Priority:** P1 (audit recommendation, not a programme phase). **Evidence class:** Code-supported. **Applies to:** Receiving/putaway.

## Scope

### What happens / remaining gap

An empty immutable map is used for absent zones and then queried with a nullable zone ID. This matches the reported Java null-key failure path. No new live create was performed.

### Required work

Handle the optional zone before lookup; cover create, edit, list and detail.

### Boundary and ownership

This task tracks one finding from the warehouse-only audit. Complete the work or evidence needed for the affected existing workflow. Planning, forecasting, optimization and competitor feature work are excluded. Optional-module work applies only to the stated scope. Existing web-only/online-only decisions and removed-adapter decisions remain authoritative. An intentional limit is closed by enforcing/documenting the supported boundary unless a later explicit scope decision authorizes expansion.

## Evidence and affected code

[#189](https://github.com/neetub1508/warehouse-issues/issues/189); [WhPutawayRuleQueryService.java:411](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse/backend/src/main/java/ai/warehouse/service/whputawayrule/WhPutawayRuleQueryService.java#L411); [WhPutawayRuleMapper.java:61](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse/backend/src/main/java/ai/warehouse/service/whputawayrule/WhPutawayRuleMapper.java#L61).

Audit code baseline: `neetub1508/classic@0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa`. Design baseline: `neetub1508/warehouse-issues@7b96725eb5850748cd94b2a784466cb16728a55d`.

Recheck the affected path at the implementation commit. “Reported” and “verification gap” do not mean a fresh runtime failure; “code-supported” does not mean a live reproduction. Preserve that distinction in the resolution.

## Requirements closed

The existing warehouse behavior described in Scope and Acceptance. This audit does not allocate new FR identifiers or claim any requirement already closed. Reuse the adopted requirements in related task sources; record exact applicable IDs when implementing instead of inventing them.

## Scenarios closed

No scenario is newly marked passed by creating this task. Execute the finding-specific acceptance below and affected refusal/retry paths. Record the current commit, supported module configuration, fixture, role, steps and actual results; reuse catalogue scenarios where they apply.

## Closes

Audit finding **W02** once its acceptance is met and evidence is linked. This issue does not automatically close or reopen earlier tasks.

### Related issues / existing implementation ownership

- #189 — [Warehouse] Putaway Rules: creating/editing a zone-less rule (FIXED_LOCATION or CONSOLIDATE_SAME_LOT) always 500s.

These links preserve earlier ownership/history. Coordinate overlapping implementation in one change and link both issues; do not build a second competing implementation. Closed duplicates remain closed.

## Implementation order and dependencies

**Recommended wave:** 1 — Protect stock, value and core operator flows. This is a scheduling recommendation, not a requirement to finish every lower-wave issue before starting independent work.

### Before dependent implementation

- No mandatory start dependency on another finding is identified. Begin current-code verification and this task’s scoped work immediately, subject to the setup/decision prerequisites below.

### Before final acceptance / closure

- No mandatory whole-issue completion dependency is identified. Meet this task’s acceptance and any applicable handoff/external prerequisites before closure.
- Preparatory analysis, fixtures and independent fixes can proceed while prerequisites are open. If a prerequisite is already satisfied in current code, link its commit/test evidence instead of waiting or rebuilding it.

### Setup, decisions and conditional dependencies

Use a zone-less fixture and check the entire create/edit/list/detail path; independent of planning and optional modules.

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
- [ ] FIXED_LOCATION and CONSOLIDATE_SAME_LOT rules work in an otherwise zone-less result page, without HTTP 500 or rollback.
- [ ] Verify current behavior against the cited evidence; record which concern is reproduced, already resolved, accepted by an existing decision, or still awaiting applicable integration evidence.
- [ ] Relevant flow check — **QC and putaway**: Accept/reject/quarantine, optional-zone rule, capacity, stock status and concurrent completion. Limit this task to its finding; link adjacent tasks for the rest.
- [ ] Run the targeted automated/runtime checks needed for this change, plus required module gates; retain actual results. A skipped integration test or code read is not a runtime pass.
- [ ] Update affected contract/help/runbook text and the related issue evidence so the supported behavior agrees across code and documentation.
- [ ] List remaining conditional dependencies explicitly; do not close an enabled workflow with unverified stock integrity, access control or external-state recovery.

## Earlier report detail (reference, verify against current code)

The following preserves the original observations/reproduction details. It is historical context; the Scope and adopted decisions above govern implementation.

<details>
<summary>Source issue #189</summary>

**What happens**
Creating (or editing) a putaway rule whose page-of-results contains no rule with a `targetZoneLocationId` throws an unhandled `NullPointerException`, returning HTTP 500. Because Create and Update both end by re-reading the row through the same code path, and that re-read is inside the `@Transactional` method, the whole operation rolls back — no data loss, but the user cannot create, view, or edit any rule using the `FIXED_LOCATION` or `CONSOLIDATE_SAME_LOT` strategies (2 of the 5 documented strategies, and the two that need no zone lookup, so the first rule most people would add is exactly the one that breaks).

**Reproduce**
```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login -H 'Content-Type: application/json' \
  -d '{"email":"<test-user-email>","password":"<test-user-password>"}' | jq -r .accessToken)

curl -s -X POST http://localhost:8000/api/v1/warehouse/inbound/putaway-rules \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"code":"ZZQATEST1","name":"QA Test Rule","warehouseId":"<any site id>","sequence":500,"strategy":"FIXED_LOCATION"}'
```
Actual:
```json
{"detail":"An unexpected error occurred","error":"Internal Server Error","code":"INTERNAL_ERROR","message":"An unexpected error occurred","status":500,"error_id":"SYS-ZSYPG9"}
```
Backend log for that request (`docker logs platform-backend`) confirms the row was inserted and then the in-transaction re-read failed:
```
[SERVICE] Method Exit: WhPutawayRuleRepositoryCustomImpl.findSupersededIds - Duration: 1ms
ERROR ... Failed SERVICE.WhPutawayRuleQueryService.getById after 24ms: null
ERROR ... a.p.exception.GlobalExceptionHandler - Unexpected error ... Type: java.lang.NullPointerException - Message: No message available - StackTrace: java.util.Objects.requireNonNull(null:-1)
```
Confirmed by contrast: the identical payload with a zone-requiring strategy and a real `targetZoneLocationId` succeeds with HTTP 201; re-running the zone-less payload afterwards (now that a zoned row exists on the same site) still 500s, and `GET /management` for the site afterwards shows the zone-less row was never persisted (transaction rolled back).

**Expected**
HTTP 201 with the created rule, `targetZoneLocationCode: null`, exactly like every other nullable display field on this response.

**Cause**
`warehouse/backend/src/main/java/ai/warehouse/service/whputawayrule/WhPutawayRuleQueryService.java:411` —
```java
Map<UUID, String> zoneCodes = zoneIds.isEmpty() ? Map.of()
        : locationRepository.findLocationCodes(zoneIds);
```
When the batch of rules being mapped has no rule with a zone, `zoneIds` is empty and `zoneCodes` becomes `Map.of()` — the JDK's immutable empty map, whose `get(Object)` calls `Objects.requireNonNull(key)` and throws on a `null` key. `WhPutawayRuleMapper.java:61` then calls `display.zoneLocationCodes().get(rule.getTargetZoneLocationId())`, and `getTargetZoneLocationId()` is legitimately `null` for `FIXED_LOCATION`/`CONSOLIDATE_SAME_LOT` rules — that null key hits the immutable map and throws. A `HashMap`/`Collections.emptyMap()` `get(null)` returns `null` safely; `Map.of()` does not accept `null` keys at all. The same `toResponses()` method backs `getById`, the grid (`/management`), `create` and `update` (both call `getById` at the end), so every one of those paths is affected whenever the rendered page contains no zoned rule.

</details>

<!-- warehouse-readiness-finding: 2026-10-01/W02 -->
