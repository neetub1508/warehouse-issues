TITLE: [Planning] WH-D10 · Extend existing external planner seam to scoped multiple producers
LABELS: task,planning
issue: 933
---
<!-- planning-detail: WH-D10 -->
**Parent epic:** [WH-P04](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-support-04.md) · **Leaf ID:** `WH-D10` · **Phase:** Foundation.

This is one implementation increment. The parent is the aggregate product/release scope, not parallel work to implement a second time. All acceptance below is proposed and unexecuted.

## Goal
Extend existing external planner seam to scoped multiple producers.

## Scope
- Reuse [warehouse issue 577](https://github.com/neetub1508/warehouse-issues/issues/577) External Planning Owner and [warehouse issue 602](https://github.com/neetub1508/warehouse-issues/issues/602)/ [warehouse issue 603](https://github.com/neetub1508/warehouse-issues/issues/603) MRP method semantics
- Arbitrate producer by company/owner/pair/domain/effective period without global bean conflict
- Cache/batch scope checks while preserving expected authority revision

## Input, output and functional contract

| Area | Required behavior |
|---|---|
| inputs | producer registrations; planning-method/catalogue authority; effective revisions |
| outputs | resolved authority/provider; overlap conflict |
| states and guards | Requested registration → reviewed/effective → superseded/expired/revoked |
| actors and permissions | Scoped planner; authorized reviewer for activation; current-grant service worker |
| timers and recovery | Authority effective-time expiry plus per-commit fence |
| cross-module effects | Warehouse/purchase/manufacturing remain the execution owners. Read/compute does not post stock or create an approved order; publication uses current-grant, expected-revision, idempotent owning-module commands. |
| UI/API entry points | Extend existing external planner seam to scoped multiple producers in the owning planner/admin workspace, with preview/detail, scoped reason diagnostics and explicit retry where supported; API and UI enforce the same permission/state guard. |

Adopt exact T1–T5 transitions, permissions, clocks and field bindings in the owning implementation contract before code. These rows do not assert existing database statuses or ratify a derived contract. Web/mobile scope follows current warehouse decisions: mobile is explicitly deferred unless a later adopted capability changes that boundary.

## Execution prerequisites
- [PL-D303](https://github.com/neetub1508/warehouse-planning-issues/blob/main/issues/detail-pl-d303.md) — Adopt product ownership and installation acceptance contracts.

## Real-world acceptance scenarios

### Scenario 1
**Given:** Manufacturing claims raw A and planning claims spare B

**When:** application starts and resolves scopes

**Then:** both providers load without bean collision and neither plans other domain

## Acceptance
- [ ] Warehouse only reorder behavior is unchanged
- [ ] Manufacturing and inventory planning coexist with one current authority per scope
- [ ] Overlapping effective claims refuse explicitly
- [ ] Retain implementation evidence for the exact source clauses and primary/supporting cases below. Run two independent functional reviewers on the same closed implementation diff and adopted contract; resolve the verified union.
- [ ] Verify applicable negative, missing-data, scope/cost, numerical, concurrency and retry/restore cases through the owning UI/API/job/provider paths. Do not count this task specification or a capability flag as a runtime pass.

## Requirements closed
“Closed” here is a source-ownership heading, not completed work. The detailed case ledger supersedes inherited parent-wide AC ranges.

- `WH-P04:scope:1` — Extend the current optional single-bean ExternalPlanningOwner contract to compose manufacturing MRP, inventory planning and future order planning without bean collision or competing ownership.
- `WH-P04:acceptance:1` — Warehouse-only has unchanged reorder behavior; manufacturing-only still uses [warehouse issue 577](https://github.com/neetub1508/warehouse-issues/issues/577)/#602 behavior.
- `WH-P04:acceptance:3` — Publishing a stale target returns conflict with no partial settings changes; retry with same idempotency key returns original result.
- `WH-P04:scenarios:1` — Two engines claim the same raw material after an admin changes its planning method.
- `WH-P04:scenarios:2` — A planner manually raises safety stock while a nightly recommendation is pending.
- `WH-P04:scenarios:3` — Future order-planning provider is absent or disabled while inventory planning remains active.

Primary source-case integration owner:
- `G05` — One owner of policy calculation Primary: [WH-D10](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-detail-wh-d10.md). Supporting: [PL-D314](https://github.com/neetub1508/warehouse-planning-issues/blob/main/issues/detail-pl-d314.md), [PL-D634](https://github.com/neetub1508/warehouse-planning-issues/blob/main/issues/detail-pl-d634.md).

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
Implementation increment `WH-D10`; parent completion remains the aggregate gate for all its children. Existing original warehouse/purchase issues are untouched.

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
