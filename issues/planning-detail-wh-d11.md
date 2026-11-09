TITLE: [Planning] WH-D11 · Add reviewed expected-version policy publication service
LABELS: task,planning
issue: TBD
---
<!-- planning-detail: WH-D11 -->
**Parent epic:** [WH-P04](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-support-04.md) · **Leaf ID:** `WH-D11` · **Phase:** Foundation.

This is one implementation increment. The parent is the aggregate product/release scope, not parallel work to implement a second time. All acceptance below is proposed and unexecuted.

## Goal
Add reviewed expected-version policy publication service.

## Scope
- Reuse existing item-site settings and approval services
- Accept calculated/approved/manual provenance, run ref, effective history and expiry
- Reject stale/direct cross module writes with per-pair atomic outcomes

## Input, output and functional contract

| Area | Required behavior |
|---|---|
| inputs | approved policy intent; authority/target revision; idempotency and grants |
| outputs | applied owner policy revision; per-pair conflict/provenance |
| states and guards | Operation belongs to a sealed run; proposed/validated/completed or typed rejected/failed with authorized retry |
| actors and permissions | Scoped planner; authorized reviewer for activation; current-grant service worker |
| timers and recovery | No independent timer; inherit the parent run clock and make cancellation/retry observable |
| cross-module effects | Warehouse/purchase/manufacturing remain the execution owners. Read/compute does not post stock or create an approved order; publication uses current-grant, expected-revision, idempotent owning-module commands. |
| UI/API entry points | Add reviewed expected-version policy publication service in the owning planner/admin workspace, with preview/detail, scoped reason diagnostics and explicit retry where supported; API and UI enforce the same permission/state guard. |

Adopt exact T1–T5 transitions, permissions, clocks and field bindings in the owning implementation contract before code. These rows do not assert existing database statuses or ratify a derived contract. Web/mobile scope follows current warehouse decisions: mobile is explicitly deferred unless a later adopted capability changes that boundary.

## Execution prerequisites
- [WH-D10](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-detail-wh-d10.md) — Extend existing external planner seam to scoped multiple producers.

## Real-world acceptance scenarios

### Scenario 1
**Given:** Human raises stock policy while old nightly run is ready

**When:** owner receives old expected version

**Then:** manual value is retained and publisher gets 409 stale conflict

## Acceptance
- [ ] Manual override survives nightly publish
- [ ] Same idempotency/payload returns original result; changed payload refuses
- [ ] Stale target or grant produces no partial pair setting writes
- [ ] Retain implementation evidence for the exact source clauses and primary/supporting cases below. Run two independent functional reviewers on the same closed implementation diff and adopted contract; resolve the verified union.
- [ ] Verify applicable negative, missing-data, scope/cost, numerical, concurrency and retry/restore cases through the owning UI/API/job/provider paths. Do not count this task specification or a capability flag as a runtime pass.

## Requirements closed
“Closed” here is a source-ownership heading, not completed work. The detailed case ledger supersedes inherited parent-wide AC ranges.

- `WH-P04:scope:3` — Add a scoped, reviewed policy-publication service with expected source revision, run reference, effective history and expiring manual overrides. No direct whb_item_site_settings writes by planning and no automatic overwrite of manufacturing parameters.
- `WH-P04:scope:4` — Reuse existing settings and approval services; no generic policy DSL or separate approval workflow. Add source/provenance only to the owning core/base objects that need it.
- `WH-P04:acceptance:3` — Publishing a stale target returns conflict with no partial settings changes; retry with same idempotency key returns original result.
- `WH-P04:scenarios:1` — Two engines claim the same raw material after an admin changes its planning method.
- `WH-P04:scenarios:3` — Future order-planning provider is absent or disabled while inventory planning remains active.

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
Implementation increment `WH-D11`; parent completion remains the aggregate gate for all its children. Existing original warehouse/purchase issues are untouched.

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
