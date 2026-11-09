TITLE: [Planning] WH-D17 · Define reconciled snapshot/high-water bootstrap boundary
LABELS: task,planning
issue: TBD
---
<!-- planning-detail: WH-D17 -->
**Parent epic:** [WH-P06](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-support-06.md) · **Leaf ID:** `WH-D17` · **Phase:** Foundation.

This is one implementation increment. The parent is the aggregate product/release scope, not parallel work to implement a second time. All acceptance below is proposed and unexecuted.

## Goal
Define reconciled snapshot/high-water bootstrap boundary.

## Scope
- Specify lower/upper cursor bounds and position-snapshot semantics without assuming atomic cut
- Replay snapshot overlap and reconcile scoped totals before consumer activation
- Provider reports coverage/epoch and blocked gaps explicitly

## Input, output and functional contract

| Area | Required behavior |
|---|---|
| inputs | snapshot and source watermark/epoch; overlapping outbox events; totals |
| outputs | reconciled bootstrap manifest or explicit gap status |
| states and guards | Operation belongs to a sealed run; proposed/validated/completed or typed rejected/failed with authorized retry |
| actors and permissions | Scoped planner; authorized reviewer for activation; current-grant service worker |
| timers and recovery | No independent timer; inherit the parent run clock and make cancellation/retry observable |
| cross-module effects | Warehouse/purchase/manufacturing remain the execution owners. Read/compute does not post stock or create an approved order; publication uses current-grant, expected-revision, idempotent owning-module commands. |
| UI/API entry points | Define reconciled snapshot/high-water bootstrap boundary in the owning planner/admin workspace, with preview/detail, scoped reason diagnostics and explicit retry where supported; API and UI enforce the same permission/state guard. |

Adopt exact T1–T5 transitions, permissions, clocks and field bindings in the owning implementation contract before code. These rows do not assert existing database statuses or ratify a derived contract. Web/mobile scope follows current warehouse decisions: mobile is explicitly deferred unless a later adopted capability changes that boundary.

## Execution prerequisites
- [WH-D16](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-detail-wh-d16.md) — Add missing planning event payloads transactionally to existing outbox.

## Real-world acceptance scenarios

### Scenario 1
**Given:** Receipt 20 commits between snapshot start and completion

**When:** snapshot+event bootstrap reconciles

**Then:** final stock conserves 120 from opening 100 and one 20 receipt

## Acceptance
- [ ] Receipt at each start/middle/end boundary appears exactly once
- [ ] Snapshot cursor lower bound alone cannot claim complete input
- [ ] Detected unexplained gap requires repair/rebootstrap
- [ ] Retain implementation evidence for the exact source clauses and primary/supporting cases below. Run two independent functional reviewers on the same closed implementation diff and adopted contract; resolve the verified union.
- [ ] Verify applicable negative, missing-data, scope/cost, numerical, concurrency and retry/restore cases through the owning UI/API/job/provider paths. Do not count this task specification or a capability flag as a runtime pass.

## Requirements closed
“Closed” here is a source-ownership heading, not completed work. The detailed case ledger supersedes inherited parent-wide AC ranges.

- `WH-P06:scope:2` — Define snapshot-plus-event bootstrap with a consistent high-water mark and reconciliation barrier: a position snapshot cursor lower bound is not proof of an atomic exact cut.
- `WH-P06:acceptance:1` — A posting at every bootstrap boundary is represented exactly once after snapshot+replay reconciliation.
- `WH-P06:scenarios:1` — Warehouse commits a receipt between extraction start and snapshot completion.
- `WH-P06:scenarios:2` — Planning retries a batch after receiving its acknowledgment but before committing its local watermark.

Primary source-case integration owner:
- `G16` — Snapshot boundary and event replay Primary: [WH-D17](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-detail-wh-d17.md).

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
Implementation increment `WH-D17`; parent completion remains the aggregate gate for all its children. Existing original warehouse/purchase issues are untouched.

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
