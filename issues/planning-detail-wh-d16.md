TITLE: [Planning] WH-D16 · Add missing planning event payloads transactionally to existing outbox
LABELS: task,planning
issue: TBD
---
<!-- planning-detail: WH-D16 -->
**Parent epic:** [WH-P06](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-support-06.md) · **Leaf ID:** `WH-D16` · **Phase:** Foundation.

This is one implementation increment. The parent is the aggregate product/release scope, not parallel work to implement a second time. All acceptance below is proposed and unexecuted.

## Goal
Add missing planning event payloads transactionally to existing outbox.

## Scope
- Reuse outbox subscriptions/cursors/retry/restore epoch
- Inventory required demand/supply/master/policy/lineage payload fields and extend only missing catalogues
- Emits table business identity/source version with transactional commit

## Input, output and functional contract

| Area | Required behavior |
|---|---|
| inputs | canonical source transaction; versioned event catalogue/schema |
| outputs | durable scoped planning event; schema compatibility evidence |
| states and guards | Operation belongs to a sealed run; proposed/validated/completed or typed rejected/failed with authorized retry |
| actors and permissions | Scoped planner; authorized reviewer for activation; current-grant service worker |
| timers and recovery | No independent timer; inherit the parent run clock and make cancellation/retry observable |
| cross-module effects | Warehouse/purchase/manufacturing remain the execution owners. Read/compute does not post stock or create an approved order; publication uses current-grant, expected-revision, idempotent owning-module commands. |
| UI/API entry points | Add missing planning event payloads transactionally to existing outbox in the owning planner/admin workspace, with preview/detail, scoped reason diagnostics and explicit retry where supported; API and UI enforce the same permission/state guard. |

Adopt exact T1–T5 transitions, permissions, clocks and field bindings in the owning implementation contract before code. These rows do not assert existing database statuses or ratify a derived contract. Web/mobile scope follows current warehouse decisions: mobile is explicitly deferred unless a later adopted capability changes that boundary.

## Execution prerequisites
- [WH-D03](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-detail-wh-d03.md) — Publish master revisions and stable paged extraction behavior.
- [WH-D06](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-detail-wh-d06.md) — Make demand imports and live postings overlap-safe.
- [WH-D09](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-detail-wh-d09.md) — Compose optional transit, manufacturing and subcontract supply providers.

## Real-world acceptance scenarios

### Scenario 1
**Given:** Demand line commits successfully but consumer is offline

**When:** outbox delivery resumes

**Then:** one current fact revision is delivered and replay is idempotent

## Acceptance
- [ ] Fact commit and event publication reconcile
- [ ] Duplicate/out-of-order delivery never overwrites newer sourcerevision
- [ ] Existing consumer payload compatibility is versioned/tested
- [ ] Retain implementation evidence for the exact source clauses and primary/supporting cases below. Run two independent functional reviewers on the same closed implementation diff and adopted contract; resolve the verified union.
- [ ] Verify applicable negative, missing-data, scope/cost, numerical, concurrency and retry/restore cases through the owning UI/API/job/provider paths. Do not count this task specification or a capability flag as a runtime pass.

## Requirements closed
“Closed” here is a source-ownership heading, not completed work. The detailed case ledger supersedes inherited parent-wide AC ranges.

- `WH-P06:scope:1` — Reuse existing outbox, cursors, subscription, restore-epoch and retry infrastructure. Define planning-specific schema/event catalogs and batched scoped read endpoints only where current payloads are insufficient.
- `WH-P06:scope:3` — Handle duplicate delivery, gaps, out-of-order source revisions, tombstones, restore epochs and expired retention explicitly; event cursor is transport order, not business effective time.
- `WH-P06:scope:4` — Publish demand-line, supply confirmation, master/policy and lineage changes with source identity transactionally; source commit and event publication must reconcile.
- `WH-P06:acceptance:2` — Repeated or delayed event cannot resurrect a canceled document or overwrite newer source revision.
- `WH-P06:scenarios:2` — Planning retries a batch after receiving its acknowledgment but before committing its local watermark.

Primary source-case integration owner:
- `G15` — Reusable transactional event foundation Primary: [WH-D16](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-detail-wh-d16.md).

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
Implementation increment `WH-D16`; parent completion remains the aggregate gate for all its children. Existing original warehouse/purchase issues are untouched.

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
