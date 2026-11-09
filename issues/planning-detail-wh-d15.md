TITLE: [Planning] WH-D15 · Withdraw only unconverted remainder and reconcile cancellation feedback
LABELS: task,planning
issue: TBD
---
<!-- planning-detail: WH-D15 -->
**Parent epic:** [WH-P05](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-support-05.md) · **Leaf ID:** `WH-D15` · **Phase:** Reviewed execution.

This is one implementation increment. The parent is the aggregate product/release scope, not parallel work to implement a second time. All acceptance below is proposed and unexecuted.

## Goal
Withdraw only unconverted remainder and reconcile cancellation feedback.

## Scope
- Rerun supersedes unaccepted remainder while preserving firmed/converted supply
- Owner cancel/amend feedback releases only corresponding conversion quantity
- Post dispatch cancellation uses existing business lifecycle, never history rewrite

## Input, output and functional contract

| Area | Required behavior |
|---|---|
| inputs | conversion/withdraw revision; owner feedback/cancellation event |
| outputs | reconciled remainder and lineage; safe retry/refusal |
| states and guards | Operation belongs to a sealed run; proposed/validated/completed or typed rejected/failed with authorized retry |
| actors and permissions | Scoped planner; authorized reviewer for activation; current-grant service worker |
| timers and recovery | No independent timer; inherit the parent run clock and make cancellation/retry observable |
| cross-module effects | Warehouse/purchase/manufacturing remain the execution owners. Read/compute does not post stock or create an approved order; publication uses current-grant, expected-revision, idempotent owning-module commands. |
| UI/API entry points | Withdraw only unconverted remainder and reconcile cancellation feedback in the owning planner/admin workspace, with preview/detail, scoped reason diagnostics and explicit retry where supported; API and UI enforce the same permission/state guard. |

Adopt exact T1–T5 transitions, permissions, clocks and field bindings in the owning implementation contract before code. These rows do not assert existing database statuses or ratify a derived contract. Web/mobile scope follows current warehouse decisions: mobile is explicitly deferred unless a later adopted capability changes that boundary.

## Execution prerequisites
- [WH-D14](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-detail-wh-d14.md) — Conserve partial concurrent conversions through canonical purchase owner.

## Real-world acceptance scenarios

### Scenario 1
**Given:** New run withdraw sold proposal while buyer conversion is unknown

**When:** reconciler queries canonical owner outcome

**Then:** converted quantity remains firm and only provably unconverted remainder is withdrawn

## Acceptance
- [ ] Accept 40 then withdraw 100 leaves 40 converted and only 60 withdrawn
- [ ] Cancelled PR line feedback does not create another PO
- [ ] Stale price/source/stock/grants reject acceptance with reason
- [ ] Retain implementation evidence for the exact source clauses and primary/supporting cases below. Run two independent functional reviewers on the same closed implementation diff and adopted contract; resolve the verified union.
- [ ] Verify applicable negative, missing-data, scope/cost, numerical, concurrency and retry/restore cases through the owning UI/API/job/provider paths. Do not count this task specification or a capability flag as a runtime pass.

## Requirements closed
“Closed” here is a source-ownership heading, not completed work. The detailed case ledger supersedes inherited parent-wide AC ranges.

- `WH-P05:scope:4` — Withdrawal affects only unconverted proposed remainder; accepted documents are amended/canceled only through their existing lifecycle and explicit authority.
- `WH-P05:acceptance:3` — A rerun withdraws stale proposed remainder but retains firmed/converted supply once; cancellation feed releases only the correct quantity.

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
Implementation increment `WH-D15`; parent completion remains the aggregate gate for all its children. Existing original warehouse/purchase issues are untouched.

## Traps
- Unknown source coverage is not zero; model output is not operational approval.
- Current grants, source version, producer authority and receiving-owner idempotency apply at the effect boundary, not only when calculation started.
- Hierarchy membership is not an execution prerequisite; do not wait for the parent epic to close before implementing this child.

## Sources
- [Source](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-support-05.md)
- [Source](https://github.com/neetub1508/warehouse-issues/issues/577)
- [Source](https://github.com/neetub1508/warehouse-issues/issues/581)
- [Source](https://github.com/neetub1508/warehouse-issues/issues/562)
- [Source](https://github.com/neetub1508/warehouse-issues/blob/main/docs/contracts/po-schedule-port.contract.md)
