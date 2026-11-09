TITLE: [Planning] WH-D23 · Publish dated price, currency and landed-cost provenance safely
LABELS: task,planning
issue: TBD
---
<!-- planning-detail: WH-D23 -->
**Parent epic:** [WH-P08](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-support-08.md) · **Leaf ID:** `WH-D23` · **Phase:** Optional purchase integration.

This is one implementation increment. The parent is the aggregate product/release scope, not parallel work to implement a second time. All acceptance below is proposed and unexecuted.

## Goal
Publish dated price, currency and landed-cost provenance safely.

## Scope
- Consume commercial price/slab/FX/UOM/tax/freight basis without duplicating price master
- Version estimate inputs when commercial module absent
- Expose missing/expired price as release block or labelled advisory fallback

## Input, output and functional contract

| Area | Required behavior |
|---|---|
| inputs | price/slab/FX/UOM/tax basis revisions; advisory estimate provenance |
| outputs | versioned cost projection; fresh-execution-price conflict |
| states and guards | Operation belongs to a sealed run; proposed/validated/completed or typed rejected/failed with authorized retry |
| actors and permissions | Scoped planner; authorized reviewer for activation; current-grant service worker |
| timers and recovery | No independent timer; inherit the parent run clock and make cancellation/retry observable |
| cross-module effects | Warehouse/purchase/manufacturing remain the execution owners. Read/compute does not post stock or create an approved order; publication uses current-grant, expected-revision, idempotent owning-module commands. |
| UI/API entry points | Publish dated price, currency and landed-cost provenance safely in the owning planner/admin workspace, with preview/detail, scoped reason diagnostics and explicit retry where supported; API and UI enforce the same permission/state guard. |

Adopt exact T1–T5 transitions, permissions, clocks and field bindings in the owning implementation contract before code. These rows do not assert existing database statuses or ratify a derived contract. Web/mobile scope follows current warehouse decisions: mobile is explicitly deferred unless a later adopted capability changes that boundary.

## Execution prerequisites
- [WH-D22](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-detail-wh-d22.md) — Expose approved site-specific purchasing constraints to planning.

## Real-world acceptance scenarios

### Scenario 1
**Given:** Advisory freight-excluded estimate 10 is replaced by approved slab 12

**When:** planner reviews budget and owner accepts

**Then:** old 10 remainslabelledestimateandacceptancerevalidates 12 without posting planning cost as valuation

## Acceptance
- [ ] Price slab change between seal and acceptance requires revalidation
- [ ] Missing currency/FX cannot produce approved cost-dependent purchase
- [ ] Quantity only forecast remains usable without commercial provider
- [ ] Retain implementation evidence for the exact source clauses and primary/supporting cases below. Run two independent functional reviewers on the same closed implementation diff and adopted contract; resolve the verified union.
- [ ] Verify applicable negative, missing-data, scope/cost, numerical, concurrency and retry/restore cases through the owning UI/API/job/provider paths. Do not count this task specification or a capability flag as a runtime pass.

## Requirements closed
“Closed” here is a source-ownership heading, not completed work. The detailed case ledger supersedes inherited parent-wide AC ranges.

- `WH-P08:scope:3` — When trade is absent, permit explicitly versioned planning estimate inputs with provenance and freshness, never pretend they are executable commercial agreements.
- `WH-P08:acceptance:2` — Price source, effective date, currency/FX, UOM and tax/landed-cost basis are visible; missing cost blocks cost-dependent release or uses disclosed advisory fallback.
- `WH-P08:acceptance:4` — Optional commercial module absent does not block quantity-only advisory forecasts; unsupported optimization inputs are explained.
- `WH-P08:scenarios:2` — Price slab changes between run and acceptance.
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
Implementation increment `WH-D23`; parent completion remains the aggregate gate for all its children. Existing original warehouse/purchase issues are untouched.

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
