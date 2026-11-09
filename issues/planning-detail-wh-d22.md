TITLE: [Planning] WH-D22 · Expose approved site-specific purchasing constraints to planning
LABELS: task,planning
issue: TBD
---
<!-- planning-detail: WH-D22 -->
**Parent epic:** [WH-P08](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-support-08.md) · **Leaf ID:** `WH-D22` · **Phase:** Optional purchase integration.

This is one implementation increment. The parent is the aggregate product/release scope, not parallel work to implement a second time. All acceptance below is proposed and unexecuted.

## Goal
Expose approved site-specific purchasing constraints to planning.

## Scope
- Reuse supplier-site master [warehouse issue 33](https://github.com/neetub1508/warehouse-issues/issues/33)/ [warehouse issue 199](https://github.com/neetub1508/warehouse-issues/issues/199) and trade AVL/agreement owners [warehouse issue 579](https://github.com/neetub1508/warehouse-issues/issues/579)/ [warehouse issue 583](https://github.com/neetub1508/warehouse-issues/issues/583)/ [warehouse issue 584](https://github.com/neetub1508/warehouse-issues/issues/584)
- Project effective source priority/MOQ/pack/UOM/calendar/capacity with scope and confidence
- Trade absence permits labelled planning estimates not fake agreements

## Input, output and functional contract

| Area | Required behavior |
|---|---|
| inputs | canonical supplier/site/agreement revisions; provider capability |
| outputs | scoped purchase constraint projection; unsupported/estimate labels |
| states and guards | Operation belongs to a sealed run; proposed/validated/completed or typed rejected/failed with authorized retry |
| actors and permissions | Scoped planner; authorized reviewer for activation; current-grant service worker |
| timers and recovery | No independent timer; inherit the parent run clock and make cancellation/retry observable |
| cross-module effects | Warehouse/purchase/manufacturing remain the execution owners. Read/compute does not post stock or create an approved order; publication uses current-grant, expected-revision, idempotent owning-module commands. |
| UI/API entry points | Expose approved site-specific purchasing constraints to planning in the owning planner/admin workspace, with preview/detail, scoped reason diagnostics and explicit retry where supported; API and UI enforce the same permission/state guard. |

Adopt exact T1–T5 transitions, permissions, clocks and field bindings in the owning implementation contract before code. These rows do not assert existing database statuses or ratify a derived contract. Web/mobile scope follows current warehouse decisions: mobile is explicitly deferred unless a later adopted capability changes that boundary.

## Execution prerequisites
- [WH-D09](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-detail-wh-d09.md) — Compose optional transit, manufacturing and subcontract supply providers.

## Real-world acceptance scenarios

### Scenario 1
**Given:** Supplier A preferred at plant 1 and Bat plant 2 with different packs

**When:** planner requests constraints

**Then:** each site gets current valid source/pack and foreign source is not defaulted

## Acceptance
- [ ] Site preference overrides global only for its valid interval
- [ ] Revoked AVL/source blocks new execution action with stale explanation
- [ ] No duplicate supplier/source master or price field on base sources
- [ ] Retain implementation evidence for the exact source clauses and primary/supporting cases below. Run two independent functional reviewers on the same closed implementation diff and adopted contract; resolve the verified union.
- [ ] Verify applicable negative, missing-data, scope/cost, numerical, concurrency and retry/restore cases through the owning UI/API/job/provider paths. Do not count this task specification or a capability flag as a runtime pass.

## Requirements closed
“Closed” here is a source-ownership heading, not completed work. The detailed case ledger supersedes inherited parent-wide AC ranges.

- `WH-P08:scope:1` — Create bounded planning-consumer projections/adapters for effective approved suppliers, item-site supply attributes, MOQ/multiples, purchase UOM, price/FX provenance, capacity/calendar/confidence and receipt performance.
- `WH-P08:scope:2` — Reuse already implemented item-site supplier source ([warehouse issue 33](https://github.com/neetub1508/warehouse-issues/issues/33)/#199) and existing trade owners [warehouse issue 579](https://github.com/neetub1508/warehouse-issues/issues/579)/#583/#584 for AVL, commercial pricing and orders; do not place prices on warehouse-base supplier sources.
- `WH-P08:acceptance:1` — Site-specific source overrides global only for that site and effective interval; source disabled/AVL revoked causes stale recommendation refusal.
- `WH-P08:acceptance:3` — Closed issue [warehouse issue 199](https://github.com/neetub1508/warehouse-issues/issues/199) is not reopened and existing supplier-site functionality is not rebuilt.
- `WH-P08:acceptance:4` — Optional commercial module absent does not block quantity-only advisory forecasts; unsupported optimization inputs are explained.
- `WH-P08:scenarios:1` — Supplier A is preferred at one plant, B at another, with different packs.
- `WH-P08:scenarios:3` — A freight-excluded estimate is used for advisory budget, clearly labeled and not posted to costing.

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
Implementation increment `WH-D22`; parent completion remains the aggregate gate for all its children. Existing original warehouse/purchase issues are untouched.

## Traps
- Unknown source coverage is not zero; model output is not operational approval.
- Current grants, source version, producer authority and receiving-owner idempotency apply at the effect boundary, not only when calculation started.
- Hierarchy membership is not an execution prerequisite; do not wait for the parent epic to close before implementing this child.

## Sources
- [Source](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-support-08.md)
- [Source](https://github.com/neetub1508/warehouse-issues/issues/33)
- [Source](https://github.com/neetub1508/warehouse-issues/issues/199)
- [Source](https://github.com/neetub1508/warehouse-issues/issues/579)
- [Source](https://github.com/neetub1508/warehouse-issues/issues/580)
- [Source](https://github.com/neetub1508/warehouse-issues/issues/583)
- [Source](https://github.com/neetub1508/warehouse-issues/issues/584)
- [Source](https://github.com/neetub1508/warehouse-issues/issues/112)
- [Source](https://github.com/neetub1508/warehouse-issues/blob/main/docs/reference/downloads-2026-10-01/Warehouse_Service_Parts_Deep_Audit_2026-09-30/02-Warehouse-Gaps.md)
