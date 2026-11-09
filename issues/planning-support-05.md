TITLE: [Planning] EPIC [Warehouse] WH-P05 · Extend external recommendations with planning origin and end-to-end conversion lineage
LABELS: epic,planning
issue: 920
---
<!-- planning-review: WH-P05 -->

> **Parent epic — aggregate scope.** Implement the detailed children below as the executable work units. This issue retains the product scope and aggregate acceptance; it is not an additional duplicate implementation task. The source-case mapping below corrects earlier broad AC-range inheritance. All work remains open until implementation evidence exists.

Part of [planning product backlog](https://github.com/neetub1508/warehouse-planning-issues/blob/main/issues/00-EPIC-planning.md). **Task ID:** `WH-P05` · **Owner:** Warehouse-owned additive integration support · **Phase:** Reviewed execution · **Priority:** essential.

**Authoritative source:** [issues/planning-support-05.md](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-support-05.md). This is a pre-build requirement, not a claim the capability is implemented or tested.

## Goal
Extend external recommendations with planning origin and end-to-end conversion lineage.

## Scope
- Extend [warehouse issue 577](https://github.com/neetub1508/warehouse-issues/issues/577) external suggestion port with a catalogued PLANNING origin/provider contract, reusing existing publish/withdraw/status/markConverted/releaseConversion behavior and authority checks.
- Retain run, recommendation/revision, source line, quantity, requested need date and resulting PR/PO/transfer references across partial conversions; never add a second order creator.
- Define current-state validation under existing document locks, source grants, period locks, item flow/AVL rules and approval guards. A recommendation is not a stock reservation or automatic approved purchase.
- Withdrawal affects only unconverted proposed remainder; accepted documents are amended/canceled only through their existing lifecycle and explicit authority.

## Dependencies and ownership
- Required task contracts: [PL-F01](https://github.com/neetub1508/warehouse-planning-issues/blob/main/issues/pl-001.md), [WH-P04](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-support-04.md).
- Existing canonical work to reuse; inspect its current contract before changing an implementation:
  - [Warehouse issue 577](https://github.com/neetub1508/warehouse-issues/issues/577) (closed at review): Existing completed seam; WH-P04/05 describe incremental multi-engine and PLANNING-origin contracts only.
  - [Warehouse issue 562](https://github.com/neetub1508/warehouse-issues/issues/562) (closed at review): Reuse completed ports; extend missing time/source facts only.
  - [Warehouse issue 581](https://github.com/neetub1508/warehouse-issues/issues/581) (open at review): Reuse open canonical warehouse-trade work, all dependencies not duplicate planning implementation.
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
Planner accepts 40 of 100 units, another actor accepts remaining 60 concurrently.
**When:** execute this task’s named operation through its supported UI/API using a sealed input revision and the actor’s current grants. **Then:** satisfy the applicable acceptance criteria below; expose the reason for rejected/unsupported outcomes and produce no unauthorized or duplicate execution effect.

### Scenario 2
A newer run replaces an unaccepted suggestion while a buyer converts the old recommendation.
**When:** execute this task’s named operation through its supported UI/API using a sealed input revision and the actor’s current grants. **Then:** satisfy the applicable acceptance criteria below; expose the reason for rejected/unsupported outcomes and produce no unauthorized or duplicate execution effect.

### Scenario 3
Trade cancels a PR line after conversion; recommendation lineage reconciles rather than creating a second PO.
**When:** execute this task’s named operation through its supported UI/API using a sealed input revision and the actor’s current grants. **Then:** satisfy the applicable acceptance criteria below; expose the reason for rejected/unsupported outcomes and produce no unauthorized or duplicate execution effect.

## Acceptance
- [ ] Concurrent double acceptance produces exactly one live conversion per accepted quantity; duplicate key with different payload conflicts.
- [ ] Trade off uses supported draft core purchase; trade on uses [warehouse issue 581](https://github.com/neetub1508/warehouse-issues/issues/581) PR lifecycle and release rules, with lineage preserved through PO and receipt.
- [ ] A rerun withdraws stale proposed remainder but retains firmed/converted supply once; cancellation feed releases only the correct quantity.
- [ ] Stale price/source/stock or lost grant blocks acceptance with actionable reason, not silent partial publication.
- [ ] Run two independent functional reviews against the same closed changed-file set and agreed contract; resolve their verified union and retain per-case implementation evidence. C1–C10 checks include UI reachability, actor/guard parity, timed obligations and cross-module effects.
- [ ] Negative, concurrency, timeout/retry and scope-isolation cases preserve prior approved state and return actionable errors; no direct cross-module table writes or implicit auto-approval.

## Requirements closed
This epic owns the aggregate behavior of its named child increments. Source cases are assigned to actual primary leaves and supporting contracts, not inherited as an entire AC range. “Closed” means specified ownership, never a runtime test pass.

### Primary case integration
No named global source case has its primary integration owner here; the exact preserved parent clauses are still fully allocated to its children in the detailed ledger.

### Corrected prior range assignments
These cases remain globally owned by the following leaves; they are not claimed as implementation of this epic:
- `G22` → [PL-D327](https://github.com/neetub1508/warehouse-planning-issues/blob/main/issues/detail-pl-d327.md)
- `G23` → [PL-D328](https://github.com/neetub1508/warehouse-planning-issues/blob/main/issues/detail-pl-d328.md)

## Scenarios closed
The real-world cases above and assigned source acceptance cases become executable implementation evidence. No research checklist is represented as executed.

## Closes
`WH-P05` in the [coverage ledger](https://github.com/neetub1508/warehouse-planning-issues/blob/main/docs/COVERAGE.md). Existing warehouse issues retain their current state.

## Implementation areas and migration policy
Extend owning warehouse/base/trade public providers, source entities/DTOs, query/export APIs and existing operational screens only where a missing field is proven. Exact implementation paths and T-row identifiers are resolved in the implementation PR from current code; paths are not invented by this design review. No production code lives in this issue repository.

No migration allocated at design stage. Use only the next free additive version within the owning installed warehouse module band after its data-model authority is amended. Never renumber applied migrations, reuse reserved deleted-adapter bands or assume a historical free-range observation remains current.

## Traps
- Historical September findings describe a past snapshot. Verify present code and canonical issue coverage before calling a source defect current.
- Unknown/missing input is not zero. Optional provider absence must be visible and must not silently enable an execution action.
- Baseline release is shadow/advisory; operational changes require reviewed acceptance by the authoritative owner. Automatic release is a separate capability gate, not implied by scheduling.
- Sealed history, owner/site scope and idempotency must survive reruns, upgrades, disable and restore.

## Sources
- [Warehouse design or issue](https://github.com/neetub1508/warehouse-issues/issues/577)
- [Warehouse design or issue](https://github.com/neetub1508/warehouse-issues/issues/581)
- [Warehouse design or issue](https://github.com/neetub1508/warehouse-issues/issues/562)
- [Warehouse design or issue](https://github.com/neetub1508/warehouse-issues/blob/main/docs/contracts/po-schedule-port.contract.md)

Public competitor documentation establishes reference capabilities; the Scope and Acceptance here are proposed product behavior, not a guarantee of proprietary algorithm parity.

## Detailed implementation children

[Detailed ownership ledger](https://github.com/neetub1508/warehouse-planning-issues/blob/main/docs/DETAILED-COVERAGE.md) · [Created issue registry](https://github.com/neetub1508/warehouse-issues/blob/main/issues/DETAILED-IMPLEMENTATION-CREATED.md). Native GitHub sub-issues provide progress; source links below remain stable before issue-number stamping.

| Child | Implementation increment | Phase |
|---|---|---|
| [WH-D13](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-detail-wh-d13.md) | Extend existing suggestion port with typed planning origin and lineage. | Reviewed execution |
| [WH-D14](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-detail-wh-d14.md) | Conserve partial concurrent conversions through canonical purchase owner. | Reviewed execution |
| [WH-D15](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-detail-wh-d15.md) | Withdraw only unconverted remainder and reconcile cancellation feedback. | Reviewed execution |

Close this parent only after every in-scope child is complete with evidence and the aggregate acceptance remains satisfied. Explicitly gated advanced increments retain their gate status; they are not silently counted as delivered.
