TITLE: [Planning] WH-D12 · Make classification authority explicit and preserve existing ABC writer
LABELS: task,planning
issue: 935
---
<!-- planning-detail: WH-D12 -->
**Parent epic:** [WH-P04](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-support-04.md) · **Leaf ID:** `WH-D12` · **Phase:** Foundation.

This is one implementation increment. The parent is the aggregate product/release scope, not parallel work to implement a second time. All acceptance below is proposed and unexecuted.

## Goal
Make classification authority explicit and preserve existing ABC writer.

## Scope
- Retain [warehouse issue 33](https://github.com/neetub1508/warehouse-issues/issues/33) monthly ABC job and conditional [warehouse issue 673](https://github.com/neetub1508/warehouse-issues/issues/673) STANDARD cost followup
- Introduce field/domain authority only for optional approved planning class publication
- Existing job checks revision and handover; unaffected scope keeps original behavior

## Input, output and functional contract

| Area | Required behavior |
|---|---|
| inputs | classification field scope; producer revision; existing ABC job result |
| outputs | authorized classification revision; handover/stale-writer evidence |
| states and guards | Operation belongs to a sealed run; proposed/validated/completed or typed rejected/failed with authorized retry |
| actors and permissions | Scoped planner; authorized reviewer for activation; current-grant service worker |
| timers and recovery | Existing monthly ABC job plus authority-expiry worker; no duplicate ABC scheduler |
| cross-module effects | Warehouse/purchase/manufacturing remain the execution owners. Read/compute does not post stock or create an approved order; publication uses current-grant, expected-revision, idempotent owning-module commands. |
| UI/API entry points | Make classification authority explicit and preserve existing ABC writer in the owning planner/admin workspace, with preview/detail, scoped reason diagnostics and explicit retry where supported; API and UI enforce the same permission/state guard. |

Adopt exact T1–T5 transitions, permissions, clocks and field bindings in the owning implementation contract before code. These rows do not assert existing database statuses or ratify a derived contract. Web/mobile scope follows current warehouse decisions: mobile is explicitly deferred unless a later adopted capability changes that boundary.

## Execution prerequisites
- [WH-D11](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-detail-wh-d11.md) — Add reviewed expected-version policy publication service.

## Real-world acceptance scenarios

### Scenario 1
**Given:** Approved planning class A races legacy job class B and authority revocation

**When:** both attempt write with expected authority revision

**Then:** only current classification producer commits and history is not lost

## Acceptance
- [ ] Stocking policy claim does not claim abc_class
- [ ] Monthly job cannot overwrite planning-owned class; stale producer fails
- [ ] Revoke/expiry/disable/enable have approved fallback and retain class history
- [ ] Retain implementation evidence for the exact source clauses and primary/supporting cases below. Run two independent functional reviewers on the same closed implementation diff and adopted contract; resolve the verified union.
- [ ] Verify applicable negative, missing-data, scope/cost, numerical, concurrency and retry/restore cases through the owning UI/API/job/provider paths. Do not count this task specification or a capability flag as a runtime pass.

## Requirements closed
“Closed” here is a source-ownership heading, not completed work. The detailed case ledger supersedes inherited parent-wide AC ranges.

- `WH-P04:scope:2` — Define effective item-site planning authority, precedence/conflict refusal and bulk/cached ownership resolution; preserve existing manufacturing [warehouse issue 602](https://github.com/neetub1508/warehouse-issues/issues/602) MRP and REORDER_POINT/NONE semantics.
- `WH-P04:scope:5` — Extend authority arbitration to explicit output domains and fields, including optional execution classification abc_class separately from stocking-policy quantities. The existing monthly per-site ABC recompute remains owned by [warehouse issue 33](https://github.com/neetub1508/warehouse-issues/issues/33); do not replace or duplicate it.
- `WH-P04:scope:6` — When a reviewed planning classification publisher takes authority for a scope/field, the legacy monthly ABC job must honor that active producer and avoid overwriting it. Revoke/expiry/disable/re-enable restores the declared producer through approved effective revisions; preserve prior class/provenance/history and unaffected execution-owned recomputes.
- `WH-P04:acceptance:2` — Manufacturing plus inventory planning starts successfully and exactly one authority plans each item-site; conflicting claims fail explicitly.
- `WH-P04:acceptance:3` — Publishing a stale target returns conflict with no partial settings changes; retry with same idempotency key returns original result.
- `WH-P04:acceptance:4` — Manual override with reason and expiry survives nightly planning, and expiry resumes the declared authority with audit.
- `WH-P04:acceptance:7` — Authority is domain/field-specific: taking stocking-policy authority cannot implicitly claim execution ABC, and a derived planning XYZ/VED output cannot mutate execution abc_class.
- `WH-P04:acceptance:8` — Run the existing monthly ABC recompute after a scoped planning classification publication; only the current authorized classification producer may write each field, while unaffected scopes keep original behavior.
- `WH-P04:acceptance:9` — Test revoke/expiry/disable/re-enable plus concurrent/stale worker and next monthly run: one current classification writer, approved handover and retained historical classes. Reuse existing warehouse issue 33 and conditional cost follow-up 673 rather than filing another baseline ABC computation.
- `WH-P04:scenarios:1` — Two engines claim the same raw material after an admin changes its planning method.
- `WH-P04:scenarios:3` — Future order-planning provider is absent or disabled while inventory planning remains active.
- `WH-P04:scenarios:4` — **Given** an active planning class publication and a legacy monthly ABC job racing with an authority revocation, **when** each checks the expected authority revision, **then** only the current field/domain producer commits; the failed actor receives a stale-authority refusal and no approved class history is overwritten.

## Scenarios closed
The concrete scenarios above and assigned source cases need real implementation evidence before this child closes. No research fixture is represented as executed product behavior.

## Reuse, limits and migration policy
Do not rebuild existing execution masters, approval engines, scheduler/authentication infrastructure or another parent capability; consume the declared sibling-child interface. Original warehouse issues remain canonical.
Warehouse owns stock, reservations and movements; trade/purchase owns commercial documents; manufacturing owns BOM/MRP. Reuse canonical existing work, including warehouse issues [33](https://github.com/neetub1508/warehouse-issues/issues/33), [577](https://github.com/neetub1508/warehouse-issues/issues/577), [602](https://github.com/neetub1508/warehouse-issues/issues/602), [603](https://github.com/neetub1508/warehouse-issues/issues/603) and the conditional STANDARD-cost follow-up [673](https://github.com/neetub1508/warehouse-issues/issues/673) when relevant. Do not reopen/refile their scope.
No migration is allocated here. Use the next free additive version in the owning adopted module band after a current collision check; planning V57/prefix whp_ are proposals, not applied-schema changes. Never renumber applied migrations.

## Numerical and evidence basis
Original proposed workflow/numerical fixture; implementation tests have not run. No proprietary numerical-equivalence assertion.
Missing vendor formulas, inconsistent history defaults and private solver behavior require the named evidence-resolution prerequisites before activation. An unsupported method/profile remains visibly blocked; do not substitute a vendor name on an unvalidated approximation.

## Closes
Implementation increment `WH-D12`; parent completion remains the aggregate gate for all its children. Existing original warehouse/purchase issues are untouched.

## Traps
- Unknown source coverage is not zero; model output is not operational approval.
- Current grants, source version, producer authority and receiving-owner idempotency apply at the effect boundary, not only when calculation started.
- Hierarchy membership is not an execution prerequisite; do not wait for the parent epic to close before implementing this child.

## Sources
- [Source](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-support-04.md)
- [Source](https://github.com/neetub1508/warehouse-issues/issues/577)
- [Source](https://github.com/neetub1508/warehouse-issues/issues/602)
- [Source](https://github.com/neetub1508/warehouse-issues/issues/603)
- [Source](https://github.com/neetub1508/classic/blob/main/warehouse/backend/src/main/java/ai/warehouse/port/replenishment/ExternalPlanningOwner.java)
- [Source](https://github.com/neetub1508/warehouse-issues/blob/main/docs/reference/downloads-2026-10-01/SPM-Planning-Research-2026-09-30/06-Warehouse-Design-Decision-Gaps.md)
- [Source](https://github.com/neetub1508/warehouse-issues/issues/33)
- [Source](https://github.com/neetub1508/warehouse-issues/issues/673)
- [Source](https://github.com/neetub1508/warehouse-issues/blob/main/issues/p1-03.md#L276)
