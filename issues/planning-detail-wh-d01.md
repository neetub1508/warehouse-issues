TITLE: [Planning] WH-D01 · Expose batched full-grain stock and reservation read contract
LABELS: task,planning
issue: TBD
---
<!-- planning-detail: WH-D01 -->
**Parent epic:** [WH-P01](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-support-01.md) · **Leaf ID:** `WH-D01` · **Phase:** Foundation.

This is one implementation increment. The parent is the aggregate product/release scope, not parallel work to implement a second time. All acceptance below is proposed and unexecuted.

## Goal
Expose batched full-grain stock and reservation read contract.

## Scope
- Inspect existing stock/allocation API sandextendonlymissingplanninggrain
- Return owner/item/site/location/lot/serial/LPN/status/duty and holder reservations with source versions
- Preserve current allocation meaning and cost mask

## Input, output and functional contract

| Area | Required behavior |
|---|---|
| inputs | current stock/reservation providers; scope filters/cursor |
| outputs | versioned full-grain read page; conservation and masking evidence |
| states and guards | Operation belongs to a sealed run; proposed/validated/completed or typed rejected/failed with authorized retry |
| actors and permissions | Warehouse API maintainer and scoped planning read service |
| timers and recovery | No independent timer; inherit the parent run clock and make cancellation/retry observable |
| cross-module effects | Warehouse/purchase/manufacturing remain the execution owners. Read/compute does not post stock or create an approved order; publication uses current-grant, expected-revision, idempotent owning-module commands. |
| UI/API entry points | Existing stock detail and planning extraction diagnostics; no duplicate stock-maintenance screen |

Adopt exact T1–T5 transitions, permissions, clocks and field bindings in the owning implementation contract before code. These rows do not assert existing database statuses or ratify a derived contract. Web/mobile scope follows current warehouse decisions: mobile is explicitly deferred unless a later adopted capability changes that boundary.

## Execution prerequisites
- [PL-D303](https://github.com/neetub1508/warehouse-planning-issues/blob/main/issues/detail-pl-d303.md) — Adopt product ownership and installation acceptance contracts.

## Real-world acceptance scenarios

### Scenario 1
**Given:** HOUSE and client stock share one 3PL site

**When:** scoped planning reader extracts HOUSE stock

**Then:** client rows are excluded and HOUSE totals reconcile without changing positions

## Acceptance
- [ ] Scoped batch reconciles to canonical positions by full grain
- [ ] Foreign owner/site and cost mask hold for paging/count/filter/export
- [ ] Long planning read uses bounded pages not long OLTP write-lock transaction
- [ ] Retain implementation evidence for the exact source clauses and primary/supporting cases below. Run two independent functional reviewers on the same closed implementation diff and adopted contract; resolve the verified union.
- [ ] Verify applicable negative, missing-data, scope/cost, numerical, concurrency and retry/restore cases through the owning UI/API/job/provider paths. Do not count this task specification or a capability flag as a runtime pass.

## Requirements closed
“Closed” here is a source-ownership heading, not completed work. The detailed case ledger supersedes inherited parent-wide AC ranges.

- `WH-P01:scope:1` — Extend existing warehouse read providers with batched planning extraction of stock by full grain, reservations/holders, status, duty, ownership, expiry and location, including in-transit and serviceability dates without mutating execution positions.
- `WH-P01:scope:4` — Assess existing APIs first and extend only missing fields/contract; this is a new consumer projection, not a claim existing stock logic is defective.
- `WH-P01:scenarios:1` — A 3PL site has HOUSE and client stock plus QC hold: only opted-in serviceable stock is planned.
- `WH-P01:scenarios:2` — A late reservation arrives during extraction: cut/reconciliation contract detects it.
- `WH-P01:scenarios:3` — Expired lot still physically present contributes zero serviceable stock.

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
Implementation increment `WH-D01`; parent completion remains the aggregate gate for all its children. Existing original warehouse/purchase issues are untouched.

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
