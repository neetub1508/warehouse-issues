TITLE: [Planning] WH-D02 · Expose serviceability and excluded stock reasons without changing allocation
LABELS: task,planning
issue: TBD
---
<!-- planning-detail: WH-D02 -->
**Parent epic:** [WH-P01](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-support-01.md) · **Leaf ID:** `WH-D02` · **Phase:** Foundation.

This is one implementation increment. The parent is the aggregate product/release scope, not parallel work to implement a second time. All acceptance below is proposed and unexecuted.

## Goal
Expose serviceability and excluded stock reasons without changing allocation.

## Scope
- Adopt documented projection of existing hold/expiry/duty/custody/location rules
- Return physical/available/restricted/expected/usable components and why excluded
- Distinguish source and destination transit without double onhand

## Input, output and functional contract

| Area | Required behavior |
|---|---|
| inputs | canonical eligibility/expiry rules; requested need date |
| outputs | serviceable projection components; exclusions with source lineage |
| states and guards | Operation belongs to a sealed run; proposed/validated/completed or typed rejected/failed with authorized retry |
| actors and permissions | Scoped planner; authorized reviewer for activation; current-grant service worker |
| timers and recovery | No independent timer; inherit the parent run clock and make cancellation/retry observable |
| cross-module effects | Warehouse/purchase/manufacturing remain the execution owners. Read/compute does not post stock or create an approved order; publication uses current-grant, expected-revision, idempotent owning-module commands. |
| UI/API entry points | Expose serviceability and excluded stock reasons without changing allocation in the owning planner/admin workspace, with preview/detail, scoped reason diagnostics and explicit retry where supported; API and UI enforce the same permission/state guard. |

Adopt exact T1–T5 transitions, permissions, clocks and field bindings in the owning implementation contract before code. These rows do not assert existing database statuses or ratify a derived contract. Web/mobile scope follows current warehouse decisions: mobile is explicitly deferred unless a later adopted capability changes that boundary.

## Execution prerequisites
- [WH-D01](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-detail-wh-d01.md) — Expose batched full-grain stock and reservation read contract.

## Real-world acceptance scenarios

### Scenario 1
**Given:** Lot 20 expired and QC30 accompany usable 50

**When:** read projection evaluates needdate

**Then:** physical 100 and usable 50 with 20/30 exclusion reasons are reported

## Acceptance
- [ ] Expired lot physically present contributes 0 serviceable
- [ ] QC/damaged/custody exclusions are explicit and match owning contract
- [ ] Transit is sourced once and future expected at destination, not double usable
- [ ] Retain implementation evidence for the exact source clauses and primary/supporting cases below. Run two independent functional reviewers on the same closed implementation diff and adopted contract; resolve the verified union.
- [ ] Verify applicable negative, missing-data, scope/cost, numerical, concurrency and retry/restore cases through the owning UI/API/job/provider paths. Do not count this task specification or a capability flag as a runtime pass.

## Requirements closed
“Closed” here is a source-ownership heading, not completed work. The detailed case ledger supersedes inherited parent-wide AC ranges.

- `WH-P01:scope:3` — Usable-for-planning is a documented projection of current availability/hold rules; distinguish physical on-hand, allocated, restricted, expected and immediately usable. Preserve status catalogs and never alter existing allocation meaning.
- `WH-P01:acceptance:1` — One scoped batch reconciles to warehouse position/availability by owner/item/site and identifies every excluded QC, damaged, expired, reserved or custody quantity.
- `WH-P01:acceptance:2` — On-hand at transit source and expected transit destination are not double counted.

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
Implementation increment `WH-D02`; parent completion remains the aggregate gate for all its children. Existing original warehouse/purchase issues are untouched.

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
