TITLE: [Planning] [Warehouse] Planning support WH-P08 · Expose optional purchase source, price and receipt-performance inputs without duplicating commercial masters
LABELS: task,warehouse
issue: 923
---
<!-- planning-review: WH-P08 -->
Part of [planning product backlog](https://github.com/neetub1508/warehouse-planning-issues/blob/main/issues/00-EPIC-planning.md). **Task ID:** `WH-P08` · **Owner:** Warehouse-owned additive integration support · **Phase:** Optional purchase integration · **Priority:** essential.

**Authoritative source:** [issues/planning-support-08.md](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-support-08.md). This is a pre-build requirement, not a claim the capability is implemented or tested.

## Goal
Expose optional purchase source, price and receipt-performance inputs without duplicating commercial masters.

## Scope
- Create bounded planning-consumer projections/adapters for effective approved suppliers, item-site supply attributes, MOQ/multiples, purchase UOM, price/FX provenance, capacity/calendar/confidence and receipt performance.
- Reuse already implemented item-site supplier source ([warehouse issue 33](https://github.com/neetub1508/warehouse-issues/issues/33)/#199) and existing trade owners [warehouse issue 579](https://github.com/neetub1508/warehouse-issues/issues/579)/#583/#584 for AVL, commercial pricing and orders; do not place prices on warehouse-base supplier sources.
- When trade is absent, permit explicitly versioned planning estimate inputs with provenance and freshness, never pretend they are executable commercial agreements.
- Supplier scorecards in trade ([warehouse issue 580](https://github.com/neetub1508/warehouse-issues/issues/580)) remain owned there; planning consumes evidence/statistics needed for uncertainty rather than builds a duplicate evaluation product.

## Dependencies and ownership
- Required task contracts: [PL-F01](https://github.com/neetub1508/warehouse-planning-issues/blob/main/issues/pl-001.md), [WH-P03](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-support-03.md).
- Existing canonical work to reuse; inspect its current contract before changing an implementation:
  - [Warehouse issue 579](https://github.com/neetub1508/warehouse-issues/issues/579) (open at review): Reuse open canonical warehouse-trade work, all dependencies not duplicate planning implementation.
  - [Warehouse issue 580](https://github.com/neetub1508/warehouse-issues/issues/580) (open at review): Reuse open canonical warehouse-trade work, all dependencies not duplicate planning implementation.
  - [Warehouse issue 583](https://github.com/neetub1508/warehouse-issues/issues/583) (open at review): Reuse open canonical warehouse-trade work, all dependencies not duplicate planning implementation.
  - [Warehouse issue 584](https://github.com/neetub1508/warehouse-issues/issues/584) (open at review): Reuse open canonical warehouse-trade work, all dependencies not duplicate planning implementation.
  - [Warehouse issue 33](https://github.com/neetub1508/warehouse-issues/issues/33) (closed at review): Reuse completed source and current entity evidence; old gap reports are stale.
  - [Warehouse issue 199](https://github.com/neetub1508/warehouse-issues/issues/199) (closed at review): Reuse completed source and current entity evidence; old gap reports are stale.
- Warehouse owns stock, reservations, movements and execution; trade/purchase owns commercial documents and supplier masters; manufacturing owns BOM/MRP. Existing open/closed/VOID issues are not reopened or mirrored by this task. Purchase-repository copy state is not implementation evidence.

## Functional contract requirements
Write or amend T1–T5 in the owning implementation contract before code. Proposed behavior below requires normal product ratification; this backlog does not ratify a derived implementation contract.

| Contract area | Required behavior |
|---|---|
| T1 states and guards | Reuse the authoritative warehouse document and immutable posting lifecycles. The new read/feed adapter cannot create a bypass transition. Define source revision, unavailable/quarantined/ready projection states and current-scope acceptance guards before build. |
| T2 actors | Warehouse owns source writes; planning workers receive only company/owner/site-scoped consumer rights. Existing approval and cost masks remain enforced. Define exact endpoint and job permissions in the owning contract. |
| T3 timers and recovery | Scheduled extraction, stale-feed warnings, replay expiry and retry need named jobs/owners. Timed absence must be represented as unavailable, never zero. Reuse existing job/outbox foundations. |
| T4 cross-module effects | Public downward interfaces only. Read adapters have no stock effects; conversion/policy commands delegate to their existing authoritative service with idempotency and expected-version checks. |
| T5 entry points and parity | Extend the existing owning warehouse screen only where new source fields are necessary; provider readiness/error and reconciliation are visible to authorized operators. No duplicate order, stock or approval UI. API/consumer-only operations must explicitly state why no user action is needed. Mobile: none in this increment, matching current warehouse web-only scope. |

## Real-world scenarios
### Scenario 1
Supplier A is preferred at one plant, B at another, with different packs.
**When:** execute this task’s named operation through its supported UI/API using a sealed input revision and the actor’s current grants. **Then:** satisfy the applicable acceptance criteria below; expose the reason for rejected/unsupported outcomes and produce no unauthorized or duplicate execution effect.

### Scenario 2
Price slab changes between run and acceptance.
**When:** execute this task’s named operation through its supported UI/API using a sealed input revision and the actor’s current grants. **Then:** satisfy the applicable acceptance criteria below; expose the reason for rejected/unsupported outcomes and produce no unauthorized or duplicate execution effect.

### Scenario 3
A freight-excluded estimate is used for advisory budget, clearly labeled and not posted to costing.
**When:** execute this task’s named operation through its supported UI/API using a sealed input revision and the actor’s current grants. **Then:** satisfy the applicable acceptance criteria below; expose the reason for rejected/unsupported outcomes and produce no unauthorized or duplicate execution effect.

## Acceptance
- [ ] Site-specific source overrides global only for that site and effective interval; source disabled/AVL revoked causes stale recommendation refusal.
- [ ] Price source, effective date, currency/FX, UOM and tax/landed-cost basis are visible; missing cost blocks cost-dependent release or uses disclosed advisory fallback.
- [ ] Closed issue [warehouse issue 199](https://github.com/neetub1508/warehouse-issues/issues/199) is not reopened and existing supplier-site functionality is not rebuilt.
- [ ] Optional commercial module absent does not block quantity-only advisory forecasts; unsupported optimization inputs are explained.
- [ ] Run two independent functional reviews against the same closed changed-file set and agreed contract; resolve their verified union and retain per-case implementation evidence. C1–C10 checks include UI reachability, actor/guard parity, timed obligations and cross-module effects.
- [ ] Negative, concurrency, timeout/retry and scope-isolation cases preserve prior approved state and return actionable errors; no direct cross-module table writes or implicit auto-approval.

## Requirements closed
This task contributes implementation coverage for the source requirements below. “Closed” means ownership within this backlog, not that tests have passed. No new warehouse FR or scenario namespace is allocated here.
- `G08`: Lead-time measurement
- `G09`: Supplier site preference

## Scenarios closed
The real-world cases above and assigned source acceptance cases become executable implementation evidence. No research checklist is represented as executed.

## Closes
`WH-P08` in the [coverage ledger](https://github.com/neetub1508/warehouse-planning-issues/blob/main/docs/COVERAGE.md). Existing warehouse issues retain their current state.

## Implementation areas and migration policy
Extend owning warehouse/base/trade public providers, source entities/DTOs, query/export APIs and existing operational screens only where a missing field is proven. Exact implementation paths and T-row identifiers are resolved in the implementation PR from current code; paths are not invented by this design review. No production code lives in this issue repository.

No migration allocated at design stage. Use only the next free additive version within the owning installed warehouse module band after its data-model authority is amended. Never renumber applied migrations, reuse reserved deleted-adapter bands or assume a historical free-range observation remains current.

## Traps
- Historical September findings describe a past snapshot. Verify present code and canonical issue coverage before calling a source defect current.
- Unknown/missing input is not zero. Optional provider absence must be visible and must not silently enable an execution action.
- Baseline release is shadow/advisory; operational changes require reviewed acceptance by the authoritative owner. Automatic release is a separate capability gate, not implied by scheduling.
- Sealed history, owner/site scope and idempotency must survive reruns, upgrades, disable and restore.

## Sources
- [Warehouse design or issue](https://github.com/neetub1508/warehouse-issues/issues/33)
- [Warehouse design or issue](https://github.com/neetub1508/warehouse-issues/issues/199)
- [Warehouse design or issue](https://github.com/neetub1508/warehouse-issues/issues/579)
- [Warehouse design or issue](https://github.com/neetub1508/warehouse-issues/issues/580)
- [Warehouse design or issue](https://github.com/neetub1508/warehouse-issues/issues/583)
- [Warehouse design or issue](https://github.com/neetub1508/warehouse-issues/issues/584)
- [Warehouse design or issue](https://github.com/neetub1508/warehouse-issues/issues/112)
- [Warehouse design or issue](https://github.com/neetub1508/warehouse-issues/blob/main/docs/reference/downloads-2026-10-01/Warehouse_Service_Parts_Deep_Audit_2026-09-30/02-Warehouse-Gaps.md)

Public competitor documentation establishes reference capabilities; the Scope and Acceptance here are proposed product behavior, not a guarantee of proprietary algorithm parity.
