TITLE: [Planning] WH-D08 · Capture supplier confirmation revisions and lead-time milestones
LABELS: task,planning
issue: TBD
---
<!-- planning-detail: WH-D08 -->
**Parent epic:** [WH-P03](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-support-03.md) · **Leaf ID:** `WH-D08` · **Phase:** Foundation.

This is one implementation increment. The parent is the aggregate product/release scope, not parallel work to implement a second time. All acceptance below is proposed and unexecuted.

## Goal
Capture supplier confirmation revisions and lead-time milestones.

## Scope
- Retain old confirmed quantity/date before amendment with source/observed time
- Expose first/full/accepted/final usable receipt milestones and routine/emergency policy
- Optional upstream supplier integration does not imply confirmed data when absent

## Input, output and functional contract

| Area | Required behavior |
|---|---|
| inputs | supplier confirmed revision; original promised dates; receipt/QC events |
| outputs | versioned confirmation history; milestone facts |
| states and guards | Operation belongs to a sealed run; proposed/validated/completed or typed rejected/failed with authorized retry |
| actors and permissions | Scoped planner; authorized reviewer for activation; current-grant service worker |
| timers and recovery | No independent timer; inherit the parent run clock and make cancellation/retry observable |
| cross-module effects | Warehouse/purchase/manufacturing remain the execution owners. Read/compute does not post stock or create an approved order; publication uses current-grant, expected-revision, idempotent owning-module commands. |
| UI/API entry points | Capture supplier confirmation revisions and lead-time milestones in the owning planner/admin workspace, with preview/detail, scoped reason diagnostics and explicit retry where supported; API and UI enforce the same permission/state guard. |

Adopt exact T1–T5 transitions, permissions, clocks and field bindings in the owning implementation contract before code. These rows do not assert existing database statuses or ratify a derived contract. Web/mobile scope follows current warehouse decisions: mobile is explicitly deferred unless a later adopted capability changes that boundary.

## Execution prerequisites
- [WH-D07](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-detail-wh-d07.md) — Publish dated open supply lines and schedule conservation.

## Real-world acceptance scenarios

### Scenario 1
**Given:** Supplier moves delivery from tomorrow to one week later after run seal

**When:** confirmation revision is captured

**Then:** old run retain sold promise and new dated projection explains changed source

## Acceptance
- [ ] Supplier Monday→next week change can be reproduced by old known-at cut
- [ ] Historical run uses old confirmation and new run gets new revision
- [ ] Unknown supplier confidence is explicit not default 100 percent
- [ ] Retain implementation evidence for the exact source clauses and primary/supporting cases below. Run two independent functional reviewers on the same closed implementation diff and adopted contract; resolve the verified union.
- [ ] Verify applicable negative, missing-data, scope/cost, numerical, concurrency and retry/restore cases through the owning UI/API/job/provider paths. Do not count this task specification or a capability flag as a runtime pass.

## Requirements closed
“Closed” here is a source-ownership heading, not completed work. The detailed case ledger supersedes inherited parent-wide AC ranges.

- `WH-P03:scope:4` — Capture confirmation revisions before overwriting current values; upstream supplier integration is optional and unknown confidence is explicit, not assumed.
- `WH-P03:scope:5` — Keep first receipt, full receipt, accepted receipt and final usable receipt distinguishable for lead-time measures; exclude emergency/line-stop orders only under declared policy.
- `WH-P03:acceptance:2` — An unconfirmed/overdue PO cannot appear available today by silently shifting its date.
- `WH-P03:acceptance:4` — Supplier confirmed date change retains prior value/time/source so past run can reproduce its inputs.
- `WH-P03:scenarios:2` — Supplier delays tomorrow receipt by a week after a run: current plan is stale and old explanation remains reproducible.
- `WH-P03:scenarios:3` — Trade off has native core PO; trade on supplies same core references via its port.

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
Implementation increment `WH-D08`; parent completion remains the aggregate gate for all its children. Existing original warehouse/purchase issues are untouched.

## Traps
- Unknown source coverage is not zero; model output is not operational approval.
- Current grants, source version, producer authority and receiving-owner idempotency apply at the effect boundary, not only when calculation started.
- Hierarchy membership is not an execution prerequisite; do not wait for the parent epic to close before implementing this child.

## Sources
- [Source](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-support-03.md)
- [Source](https://github.com/neetub1508/warehouse-issues/issues/562)
- [Source](https://github.com/neetub1508/warehouse-issues/issues/112)
- [Source](https://github.com/neetub1508/warehouse-issues/issues/584)
- [Source](https://github.com/neetub1508/classic/blob/main/warehouse-base/backend/src/main/java/ai/warehousebase/service/allocation/WhbOnOrderSource.java)
- [Source](https://github.com/neetub1508/warehouse-issues/blob/main/docs/reference/downloads-2026-10-01/Warehouse_Service_Parts_Deep_Audit_2026-09-30/02-Warehouse-Gaps.md)
