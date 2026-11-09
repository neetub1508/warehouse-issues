TITLE: [Planning] WH-D04 · Capture append-only requested-line demand event facts
LABELS: task,planning
issue: TBD
---
<!-- planning-detail: WH-D04 -->
**Parent epic:** [WH-P02](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-support-02.md) · **Leaf ID:** `WH-D04` · **Phase:** Foundation.

This is one implementation increment. The parent is the aggregate product/release scope, not parallel work to implement a second time. All acceptance below is proposed and unexecuted.

## Goal
Capture append-only requested-line demand event facts.

## Scope
- Reuse existing request/issue/sales demand contracts and extend only missing line facts
- Store original requested and supplied item/source/owner/company/stream/times/UOM and revision
- Preserve frozen warehouse KPI history as a separate projection

## Input, output and functional contract

| Area | Required behavior |
|---|---|
| inputs | canonical request and posting events; source line ID; base UOM conversion |
| outputs | immutable line-event facts; request/fulfillment lineage |
| states and guards | Operation belongs to a sealed run; proposed/validated/completed or typed rejected/failed with authorized retry |
| actors and permissions | Owning warehouse/trade transaction services; scoped planning fact reader |
| timers and recovery | No independent timer; inherit the parent run clock and make cancellation/retry observable |
| cross-module effects | Warehouse/purchase/manufacturing remain the execution owners. Read/compute does not post stock or create an approved order; publication uses current-grant, expected-revision, idempotent owning-module commands. |
| UI/API entry points | Capture append-only requested-line demand event facts in the owning planner/admin workspace, with preview/detail, scoped reason diagnostics and explicit retry where supported; API and UI enforce the same permission/state guard. |

Adopt exact T1–T5 transitions, permissions, clocks and field bindings in the owning implementation contract before code. These rows do not assert existing database statuses or ratify a derived contract. Web/mobile scope follows current warehouse decisions: mobile is explicitly deferred unless a later adopted capability changes that boundary.

## Execution prerequisites
- [PL-D303](https://github.com/neetub1508/warehouse-planning-issues/blob/main/issues/detail-pl-d303.md) — Adopt product ownership and installation acceptance contracts.

## Real-world acceptance scenarios

### Scenario 1
**Given:** Request A10 is fulfilled B4 then A3 and cancelled 3

**When:** source events are captured

**Then:** original request 10 and fulfilled 7/cancelled 3 and supplied identities are conserved

## Acceptance
- [ ] Three partial shipments of 1 request remain 1 demand occurrence
- [ ] Supplierreturn/internal transfer does not become customer consumption
- [ ] Historical owner cannot be reassigned from current item owner
- [ ] Retain implementation evidence for the exact source clauses and primary/supporting cases below. Run two independent functional reviewers on the same closed implementation diff and adopted contract; resolve the verified union.
- [ ] Verify applicable negative, missing-data, scope/cost, numerical, concurrency and retry/restore cases through the owning UI/API/job/provider paths. Do not count this task specification or a capability flag as a runtime pass.

## Requirements closed
“Closed” here is a source-ownership heading, not completed work. The detailed case ledger supersedes inherited parent-wide AC ranges.

- `WH-P02:scope:1` — Add an append-only planning-consumer fact/projection seam for demand creation/amendment/cancel/backorder/shipment/return/lost outcome and manufacturing stores consumption, retaining company/owner/source line, requested/supplied item, stream, quantities, UOM and both effective/observed clocks.
- `WH-P02:scope:2` — Keep existing monthly wh_demand_history and its frozen KPI semantics intact. Capture source granularity not infer customer demand from every outbound movement; internal transfers/vendor returns and repairs have explicit types.
- `WH-P02:scope:4` — Reconstruct historical fields only when authoritative source evidence exists; mark unavailable provenance rather than invent lost sales. Reuse trade lost-sale capture and source [warehouse issue 106](https://github.com/neetub1508/warehouse-issues/issues/106)/#563, not restore removed manual/dealer routes.
- `WH-P02:acceptance:1` — One requested line split into three shipments remains one demand occurrence; canceled/lost remainder is separated from fulfilled demand.
- `WH-P02:acceptance:2` — Supplier return/internal transfer does not become customer consumption; manufacturing demand is a separately named stream.
- `WH-P02:scenarios:1` — A request for A is partly fulfilled with successor B and later canceled: requested and supplied identities reconcile.
- `WH-P02:scenarios:2` — A customer return in the following month nets only according to the declared demand policy.
- `WH-P02:scenarios:3` — An owner changes after old consumption: historical owner remains the source fact.

Primary source-case integration owner:
- `AC013` — Partial fill with a substitute retains requested quantity/item and actual fulfilled quantity/item. Primary: [WH-D04](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-detail-wh-d04.md). Supporting: [PL-D103](https://github.com/neetub1508/warehouse-planning-issues/blob/main/issues/detail-pl-d103.md).
- `G01` — Source-level demand facts Primary: [WH-D04](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-detail-wh-d04.md). Supporting: [PL-D101](https://github.com/neetub1508/warehouse-planning-issues/blob/main/issues/detail-pl-d101.md), [PL-D102](https://github.com/neetub1508/warehouse-planning-issues/blob/main/issues/detail-pl-d102.md).
- `G11` — Requested versus fulfilled item across all paths Primary: [WH-D04](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-detail-wh-d04.md). Supporting: [PL-D103](https://github.com/neetub1508/warehouse-planning-issues/blob/main/issues/detail-pl-d103.md), [PL-D111](https://github.com/neetub1508/warehouse-planning-issues/blob/main/issues/detail-pl-d111.md).

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
Implementation increment `WH-D04`; parent completion remains the aggregate gate for all its children. Existing original warehouse/purchase issues are untouched.

## Traps
- Unknown source coverage is not zero; model output is not operational approval.
- Current grants, source version, producer authority and receiving-owner idempotency apply at the effect boundary, not only when calculation started.
- Hierarchy membership is not an execution prerequisite; do not wait for the parent epic to close before implementing this child.

## Sources
- [Source](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-support-02.md)
- [Source](https://github.com/neetub1508/warehouse-issues/issues/106)
- [Source](https://github.com/neetub1508/warehouse-issues/issues/563)
- [Source](https://github.com/neetub1508/warehouse-issues/issues/167)
- [Source](https://github.com/neetub1508/warehouse-issues/blob/main/docs/reference/downloads-2026-10-01/Warehouse_Service_Parts_Deep_Audit_2026-09-30/02-Warehouse-Gaps.md)
- [Source](https://github.com/neetub1508/warehouse-issues/blob/main/docs/reference/downloads-2026-10-01/SPM-Planning-Research-2026-09-30/05-Warehouse-Code-Gaps.md)
