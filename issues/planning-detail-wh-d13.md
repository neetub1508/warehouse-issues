TITLE: [Planning] WH-D13 · Extend existing suggestion port with typed planning origin and lineage
LABELS: task,planning
issue: 936
---
<!-- planning-detail: WH-D13 -->
**Parent epic:** [WH-P05](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-support-05.md) · **Leaf ID:** `WH-D13` · **Phase:** Reviewed execution.

This is one implementation increment. The parent is the aggregate product/release scope, not parallel work to implement a second time. All acceptance below is proposed and unexecuted.

## Goal
Extend existing suggestion port with typed planning origin and lineage.

## Scope
- Reuse [warehouse issue 577](https://github.com/neetub1508/warehouse-issues/issues/577) publish/withdraw/status/mark Converted/release Conversion
- Add catalogued PLANNING producer/origin and immutable run/recommendation/source-line/version refs
- Keep recommendation distinct from reservation or approved purchase

## Input, output and functional contract

| Area | Required behavior |
|---|---|
| inputs | producer/origin catalogue; immutable recommendation envelope |
| outputs | versioned suggestion with planning provenance |
| states and guards | Operation belongs to a sealed run; proposed/validated/completed or typed rejected/failed with authorized retry |
| actors and permissions | Scoped planner; authorized reviewer for activation; current-grant service worker |
| timers and recovery | No independent timer; inherit the parent run clock and make cancellation/retry observable |
| cross-module effects | Warehouse/purchase/manufacturing remain the execution owners. Read/compute does not post stock or create an approved order; publication uses current-grant, expected-revision, idempotent owning-module commands. |
| UI/API entry points | Extend existing suggestion port with typed planning origin and lineage in the owning planner/admin workspace, with preview/detail, scoped reason diagnostics and explicit retry where supported; API and UI enforce the same permission/state guard. |

Adopt exact T1–T5 transitions, permissions, clocks and field bindings in the owning implementation contract before code. These rows do not assert existing database statuses or ratify a derived contract. Web/mobile scope follows current warehouse decisions: mobile is explicitly deferred unless a later adopted capability changes that boundary.

## Execution prerequisites
- [WH-D10](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-detail-wh-d10.md) — Extend existing external planner seam to scoped multiple producers.

## Real-world acceptance scenarios

### Scenario 1
**Given:** Planning publishes 100 units with run Rrecommendationv 2

**When:** existing suggestion port stores it

**Then:** one proposed suggestion and its run/version lineage exist without an approved order

## Acceptance
- [ ] No second order creator or approval engine is added
- [ ] Provider/origin and requestedquantity/date survive partial conversion
- [ ] Unknown origin or unauthorized producer is refused
- [ ] Retain implementation evidence for the exact source clauses and primary/supporting cases below. Run two independent functional reviewers on the same closed implementation diff and adopted contract; resolve the verified union.
- [ ] Verify applicable negative, missing-data, scope/cost, numerical, concurrency and retry/restore cases through the owning UI/API/job/provider paths. Do not count this task specification or a capability flag as a runtime pass.

## Requirements closed
“Closed” here is a source-ownership heading, not completed work. The detailed case ledger supersedes inherited parent-wide AC ranges.

- `WH-P05:scope:1` — Extend [warehouse issue 577](https://github.com/neetub1508/warehouse-issues/issues/577) external suggestion port with a catalogued PLANNING origin/provider contract, reusing existing publish/withdraw/status/markConverted/releaseConversion behavior and authority checks.
- `WH-P05:scope:2` — Retain run, recommendation/revision, source line, quantity, requested need date and resulting PR/PO/transfer references across partial conversions; never add a second order creator.
- `WH-P05:acceptance:2` — Trade off uses supported draft core purchase; trade on uses [warehouse issue 581](https://github.com/neetub1508/warehouse-issues/issues/581) PR lifecycle and release rules, with lineage preserved through PO and receipt.
- `WH-P05:scenarios:2` — A newer run replaces an unaccepted suggestion while a buyer converts the old recommendation.
- `WH-P05:scenarios:3` — Trade cancels a PR line after conversion; recommendation lineage reconciles rather than creating a second PO.

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
Implementation increment `WH-D13`; parent completion remains the aggregate gate for all its children. Existing original warehouse/purchase issues are untouched.

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
