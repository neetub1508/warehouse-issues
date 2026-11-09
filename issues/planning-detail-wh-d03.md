TITLE: [Planning] WH-D03 · Publish master revisions and stable paged extraction behavior
LABELS: task,planning
issue: 926
---
<!-- planning-detail: WH-D03 -->
**Parent epic:** [WH-P01](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-support-01.md) · **Leaf ID:** `WH-D03` · **Phase:** Foundation.

This is one implementation increment. The parent is the aggregate product/release scope, not parallel work to implement a second time. All acceptance below is proposed and unexecuted.

## Goal
Publish master revisions and stable paged extraction behavior.

## Scope
- Return item/site/UOM/source/calendar/master version projections with capability/completeness
- Define paging cut validity and stale source cursor refusal
- Measure batch latency on representative workload

## Input, output and functional contract

| Area | Required behavior |
|---|---|
| inputs | public master/read APIs; revision/cursor and completeness contract |
| outputs | stable paged master projection; measured limits and stale-cut status |
| states and guards | Operation belongs to a sealed run; proposed/validated/completed or typed rejected/failed with authorized retry |
| actors and permissions | Scoped planner; authorized reviewer for activation; current-grant service worker |
| timers and recovery | No independent timer; inherit the parent run clock and make cancellation/retry observable |
| cross-module effects | Warehouse/purchase/manufacturing remain the execution owners. Read/compute does not post stock or create an approved order; publication uses current-grant, expected-revision, idempotent owning-module commands. |
| UI/API entry points | Publish master revisions and stable paged extraction behavior in the owning planner/admin workspace, with preview/detail, scoped reason diagnostics and explicit retry where supported; API and UI enforce the same permission/state guard. |

Adopt exact T1–T5 transitions, permissions, clocks and field bindings in the owning implementation contract before code. These rows do not assert existing database statuses or ratify a derived contract. Web/mobile scope follows current warehouse decisions: mobile is explicitly deferred unless a later adopted capability changes that boundary.

## Execution prerequisites
- [WH-D02](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-detail-wh-d02.md) — Expose serviceability and excluded stock reasons without changing allocation.

## Real-world acceptance scenarios

### Scenario 1
**Given:** Reservation revision changes between two extraction pages

**When:** consumer tries completing the old cut

**Then:** cut validity or reconciliation flags changed source before complete activation

## Acceptance
- [ ] Replayed page is stable source identity or safely invalidates the cut
- [ ] Reservation arriving during read is detectable via bootstrap reconciliation
- [ ] No extra second item master or cross module SQL is created
- [ ] Retain implementation evidence for the exact source clauses and primary/supporting cases below. Run two independent functional reviewers on the same closed implementation diff and adopted contract; resolve the verified union.
- [ ] Verify applicable negative, missing-data, scope/cost, numerical, concurrency and retry/restore cases through the owning UI/API/job/provider paths. Do not count this task specification or a capability flag as a runtime pass.

## Requirements closed
“Closed” here is a source-ownership heading, not completed work. The detailed case ledger supersedes inherited parent-wide AC ranges.

- `WH-P01:scope:2` — Provide item/site/UOM, source, calendar and master-version projections with deterministic pagination, source revision and completeness metadata; planning has no direct cross-module SQL.
- `WH-P01:acceptance:3` — Extraction respects site/owner/cost scope for paging, counts, filters and exports; live OLTP writes are not held in a long planning transaction.
- `WH-P01:acceptance:4` — Replayed page/watermark returns stable source identity or invalidates the cut explicitly; performance target is measured.

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
Implementation increment `WH-D03`; parent completion remains the aggregate gate for all its children. Existing original warehouse/purchase issues are untouched.

## Traps
- Unknown source coverage is not zero; model output is not operational approval.
- Current grants, source version, producer authority and receiving-owner idempotency apply at the effect boundary, not only when calculation started.
- Hierarchy membership is not an execution prerequisite; do not wait for the parent epic to close before implementing this child.

## Sources
- [Source](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-support-01.md)
- [Source](https://github.com/neetub1508/warehouse-issues/issues/34)
- [Source](https://github.com/neetub1508/warehouse-issues/issues/59)
- [Source](https://github.com/neetub1508/warehouse-issues/issues/106)
- [Source](https://github.com/neetub1508/warehouse-issues/blob/main/docs/contracts/reservation-allocation.contract.md)
- [Source](https://github.com/neetub1508/warehouse-issues/blob/main/docs/reference/downloads-2026-10-01/Warehouse_Service_Parts_Deep_Audit_2026-09-30/02-Warehouse-Gaps.md)
