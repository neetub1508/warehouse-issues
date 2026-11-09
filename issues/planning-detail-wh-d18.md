TITLE: [Planning] WH-D18 · Fence old cursors on restore and expose scoped replay recovery
LABELS: task,planning
issue: 941
---
<!-- planning-detail: WH-D18 -->
**Parent epic:** [WH-P06](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-support-06.md) · **Leaf ID:** `WH-D18` · **Phase:** Foundation.

This is one implementation increment. The parent is the aggregate product/release scope, not parallel work to implement a second time. All acceptance below is proposed and unexecuted.

## Goal
Fence old cursors on restore and expose scoped replay recovery.

## Scope
- Detect source restore epoch changes and expired retention
- Reject old consumer checkpoints before new write activation
- Expose pause/retry/dead-letter/rebootstrap using existing controls

## Input, output and functional contract

| Area | Required behavior |
|---|---|
| inputs | source epoch/retention; consumer checkpoint; current subscription grants |
| outputs | invalidated cursor; scoped recovery action and journal |
| states and guards | Operation belongs to a sealed run; proposed/validated/completed or typed rejected/failed with authorized retry |
| actors and permissions | Scoped planner; authorized reviewer for activation; current-grant service worker |
| timers and recovery | Restore detection and subscription retry/dead letter recovery workers |
| cross-module effects | Warehouse/purchase/manufacturing remain the execution owners. Read/compute does not post stock or create an approved order; publication uses current-grant, expected-revision, idempotent owning-module commands. |
| UI/API entry points | Fence old cursors on restore and expose scoped replay recovery in the owning planner/admin workspace, with preview/detail, scoped reason diagnostics and explicit retry where supported; API and UI enforce the same permission/state guard. |

Adopt exact T1–T5 transitions, permissions, clocks and field bindings in the owning implementation contract before code. These rows do not assert existing database statuses or ratify a derived contract. Web/mobile scope follows current warehouse decisions: mobile is explicitly deferred unless a later adopted capability changes that boundary.

## Execution prerequisites
- [WH-D17](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-detail-wh-d17.md) — Define reconciled snapshot/high-water bootstrap boundary.

## Real-world acceptance scenarios

### Scenario 1
**Given:** Backup restore creates epoch 2 while planning holds acknowledged epoch 3 cursor

**When:** consumer tries resume

**Then:** it receives epoch conflict and must rebootstrap before planning release

## Acceptance
- [ ] Old cursor cannot resume past restored data as if current
- [ ] Missing retained events demand explicit rebootstrap
- [ ] Delayed tombstone/cancellation cannot be resurrected by older revision
- [ ] Retain implementation evidence for the exact source clauses and primary/supporting cases below. Run two independent functional reviewers on the same closed implementation diff and adopted contract; resolve the verified union.
- [ ] Verify applicable negative, missing-data, scope/cost, numerical, concurrency and retry/restore cases through the owning UI/API/job/provider paths. Do not count this task specification or a capability flag as a runtime pass.

## Requirements closed
“Closed” here is a source-ownership heading, not completed work. The detailed case ledger supersedes inherited parent-wide AC ranges.

- `WH-P06:acceptance:3` — Restore to older database invalidates old planning cursors before new writes; missing retained events require explicit rebootstrap.
- `WH-P06:acceptance:4` — Consumer pause/retry/dead-letter is observable and scoped, reusing existing subscription controls.
- `WH-P06:scenarios:2` — Planning retries a batch after receiving its acknowledgment but before committing its local watermark.
- `WH-P06:scenarios:3` — Backup restore has an epoch older than already acknowledged external events.

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
Implementation increment `WH-D18`; parent completion remains the aggregate gate for all its children. Existing original warehouse/purchase issues are untouched.

## Traps
- Unknown source coverage is not zero; model output is not operational approval.
- Current grants, source version, producer authority and receiving-owner idempotency apply at the effect boundary, not only when calculation started.
- Hierarchy membership is not an execution prerequisite; do not wait for the parent epic to close before implementing this child.

## Sources
- [Source](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-support-06.md)
- [Source](https://github.com/neetub1508/warehouse-issues/issues/89)
- [Source](https://github.com/neetub1508/warehouse-issues/issues/119)
- [Source](https://github.com/neetub1508/warehouse-issues/issues/315)
- [Source](https://github.com/neetub1508/warehouse-issues/blob/main/docs/contracts/outbox-events.contract.md)
- [Source](https://github.com/neetub1508/warehouse-issues/blob/main/docs/reference/downloads-2026-10-01/Warehouse_Service_Parts_Deep_Audit_2026-09-30/02-Warehouse-Gaps.md)
