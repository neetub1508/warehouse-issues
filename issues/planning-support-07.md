TITLE: [Planning] [Warehouse] Planning support WH-P07 · Preserve source versions and archive-safe planning extraction without promising full ledger time travel
LABELS: task,warehouse
issue: TBD
---
<!-- planning-review: WH-P07 -->
Part of [planning product backlog](https://github.com/neetub1508/warehouse-planning-issues/blob/main/issues/00-EPIC-planning.md). **Task ID:** `WH-P07` · **Owner:** Warehouse-owned additive integration support · **Phase:** Foundation · **Priority:** essential.

**Authoritative source:** [issues/planning-support-07.md](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-support-07.md). This is a pre-build requirement, not a claim the capability is implemented or tested.

## Goal
Preserve source versions and archive-safe planning extraction without promising full ledger time travel.

## Scope
- Define which warehouse source facts, master versions, calendar/source terms and corrections are retained/exported for reproducible planning manifests; distinguish current-state as-of report, historical stock snapshot and as-known source state.
- Integrate existing [warehouse issue 94](https://github.com/neetub1508/warehouse-issues/issues/94) archive/opening-balance and snapshot recovery capability; archive must retain source references or explicitly mark unavailable history rather than synthesize detailed demand from balances.
- Expose additive source versions/effective histories only where missing and needed by planning, respecting existing immutable ledger, lawful deletion and configurable retention; no rewrite of archived stock.
- Provide bounded historical export/read windows and a compatibility contract for immutable planning run packages.

## Dependencies and ownership
- Required task contracts: [PL-F01](https://github.com/neetub1508/warehouse-planning-issues/blob/main/issues/pl-001.md), [WH-P06](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-support-06.md).
- Existing canonical work to reuse; inspect its current contract before changing an implementation:
  - [Warehouse issue 94](https://github.com/neetub1508/warehouse-issues/issues/94) (closed at review): Reuse existing infrastructure and canonical open snapshot-recovery task; new planning bootstrap/reproducibility contracts incremental.
  - [Warehouse issue 179](https://github.com/neetub1508/warehouse-issues/issues/179) (closed at review): Reuse existing infrastructure and canonical open snapshot-recovery task; new planning bootstrap/reproducibility contracts incremental.
  - [Warehouse issue 688](https://github.com/neetub1508/warehouse-issues/issues/688) (open at review): Reuse existing infrastructure and canonical open snapshot-recovery task; new planning bootstrap/reproducibility contracts incremental.
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
Warehouse archives a year between planning run and historical replay.
**When:** execute this task’s named operation through its supported UI/API using a sealed input revision and the actor’s current grants. **Then:** satisfy the applicable acceptance criteria below; expose the reason for rejected/unsupported outcomes and produce no unauthorized or duplicate execution effect.

### Scenario 2
Supplier terms change next month, then a prior run is explained.
**When:** execute this task’s named operation through its supported UI/API using a sealed input revision and the actor’s current grants. **Then:** satisfy the applicable acceptance criteria below; expose the reason for rejected/unsupported outcomes and produce no unauthorized or duplicate execution effect.

### Scenario 3
An authorized retention purge removes sensitive customer fields while preserving permitted aggregates.
**When:** execute this task’s named operation through its supported UI/API using a sealed input revision and the actor’s current grants. **Then:** satisfy the applicable acceptance criteria below; expose the reason for rejected/unsupported outcomes and produce no unauthorized or duplicate execution effect.

## Acceptance
- [ ] A historical run retains the original supplier lead time/calendar/policy/confirmation version even after today values change.
- [ ] Archive does not silently turn dormant balances into zero demand or erase provenance promised to an existing run.
- [ ] Purged source data produces an explicit non-reproducible/unavailable state and documented reason.
- [ ] Extraction reproduces records from a declared source revision, with permissions rechecked; no universal bitemporal claim without evidence.
- [ ] Run two independent functional reviews against the same closed changed-file set and agreed contract; resolve their verified union and retain per-case implementation evidence. C1–C10 checks include UI reachability, actor/guard parity, timed obligations and cross-module effects.
- [ ] Negative, concurrency, timeout/retry and scope-isolation cases preserve prior approved state and return actionable errors; no direct cross-module table writes or implicit auto-approval.

## Requirements closed
This task contributes implementation coverage for the source requirements below. “Closed” means ownership within this backlog, not that tests have passed. No new warehouse FR or scenario namespace is allocated here.
- `G16`: Snapshot boundary and event replay
- `G17`: Complete planning run snapshot
- `G18`: Historical as-known state
- `G45`: Retention, reproducibility and export

## Scenarios closed
The real-world cases above and assigned source acceptance cases become executable implementation evidence. No research checklist is represented as executed.

## Closes
`WH-P07` in the [coverage ledger](https://github.com/neetub1508/warehouse-planning-issues/blob/main/docs/COVERAGE.md). Existing warehouse issues retain their current state.

## Implementation areas and migration policy
Extend owning warehouse/base/trade public providers, source entities/DTOs, query/export APIs and existing operational screens only where a missing field is proven. Exact implementation paths and T-row identifiers are resolved in the implementation PR from current code; paths are not invented by this design review. No production code lives in this issue repository.

No migration allocated at design stage. Use only the next free additive version within the owning installed warehouse module band after its data-model authority is amended. Never renumber applied migrations, reuse reserved deleted-adapter bands or assume a historical free-range observation remains current.

## Traps
- Historical September findings describe a past snapshot. Verify present code and canonical issue coverage before calling a source defect current.
- Unknown/missing input is not zero. Optional provider absence must be visible and must not silently enable an execution action.
- Baseline release is shadow/advisory; operational changes require reviewed acceptance by the authoritative owner. Automatic release is a separate capability gate, not implied by scheduling.
- Sealed history, owner/site scope and idempotency must survive reruns, upgrades, disable and restore.

## Sources
- [Warehouse design or issue](https://github.com/neetub1508/warehouse-issues/issues/94)
- [Warehouse design or issue](https://github.com/neetub1508/warehouse-issues/issues/179)
- [Warehouse design or issue](https://github.com/neetub1508/warehouse-issues/issues/688)
- [Warehouse design or issue](https://github.com/neetub1508/warehouse-issues/blob/main/docs/reference/downloads-2026-10-01/Warehouse_Service_Parts_Deep_Audit_2026-09-30/03-Planning-Architecture-and-Contracts.md)

Public competitor documentation establishes reference capabilities; the Scope and Acceptance here are proposed product behavior, not a guarantee of proprietary algorithm parity.
