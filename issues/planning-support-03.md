TITLE: [Planning] [Warehouse] Planning support WH-P03 · Publish detailed dated supply and supplier-confirmation facts for planning
LABELS: task,warehouse
issue: 918
---
<!-- planning-review: WH-P03 -->
Part of [planning product backlog](https://github.com/neetub1508/warehouse-planning-issues/blob/main/issues/00-EPIC-planning.md). **Task ID:** `WH-P03` · **Owner:** Warehouse-owned additive integration support · **Phase:** Foundation · **Priority:** essential.

**Authoritative source:** [issues/planning-support-03.md](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-support-03.md). This is a pre-build requirement, not a claim the capability is implemented or tested.

## Goal
Publish detailed dated supply and supplier-confirmation facts for planning.

## Scope
- Extend the existing PO/schedule and receipt evidence ports with per-source-line remaining firm supply, confirmed quantities/dates, promised/revised date history, ship/receive/QC-usable dates, cancellation and receipt allocations.
- Reuse [warehouse issue 562](https://github.com/neetub1508/warehouse-issues/issues/562) schedules and [warehouse issue 112](https://github.com/neetub1508/warehouse-issues/issues/112) receipt facts. Do not treat the existing aggregate WhbOnOrderSource as absent; add a distinct detailed read projection while preserving base availability behavior.
- Distinguish forecast schedule rows from firm commitments, overdue/undated supply from usable supply and PR suggestion from a purchase order. Include optional manufacturing/subcontract/transit providers behind scoped ports.
- Capture confirmation revisions before overwriting current values; upstream supplier integration is optional and unknown confidence is explicit, not assumed.
- Keep first receipt, full receipt, accepted receipt and final usable receipt distinguishable for lead-time measures; exclude emergency/line-stop orders only under declared policy.

## Dependencies and ownership
- Required task contracts: [PL-F01](https://github.com/neetub1508/warehouse-planning-issues/blob/main/issues/pl-001.md).
- Existing canonical work to reuse; inspect its current contract before changing an implementation:
  - [Warehouse issue 562](https://github.com/neetub1508/warehouse-issues/issues/562) (closed at review): Reuse completed ports; extend missing time/source facts only.
  - [Warehouse issue 584](https://github.com/neetub1508/warehouse-issues/issues/584) (open at review): Reuse open canonical warehouse-trade work, all dependencies not duplicate planning implementation.
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
100 units due Monday: 40 received, 10 rejected, 60 still inbound; usable supply remains correct.
**When:** execute this task’s named operation through its supported UI/API using a sealed input revision and the actor’s current grants. **Then:** satisfy the applicable acceptance criteria below; expose the reason for rejected/unsupported outcomes and produce no unauthorized or duplicate execution effect.

### Scenario 2
Supplier delays tomorrow receipt by a week after a run: current plan is stale and old explanation remains reproducible.
**When:** execute this task’s named operation through its supported UI/API using a sealed input revision and the actor’s current grants. **Then:** satisfy the applicable acceptance criteria below; expose the reason for rejected/unsupported outcomes and produce no unauthorized or duplicate execution effect.

### Scenario 3
Trade off has native core PO; trade on supplies same core references via its port.
**When:** execute this task’s named operation through its supported UI/API using a sealed input revision and the actor’s current grants. **Then:** satisfy the applicable acceptance criteria below; expose the reason for rejected/unsupported outcomes and produce no unauthorized or duplicate execution effect.

## Acceptance
- [ ] An open line with three dated receipts is time-phased and conserved after partial receipt, cancellation and rejection.
- [ ] An unconfirmed/overdue PO cannot appear available today by silently shifting its date.
- [ ] Firm schedule and parent PO quantity are counted once; PR converted to PO is not counted twice.
- [ ] Supplier confirmed date change retains prior value/time/source so past run can reproduce its inputs.
- [ ] Run two independent functional reviews against the same closed changed-file set and agreed contract; resolve their verified union and retain per-case implementation evidence. C1–C10 checks include UI reachability, actor/guard parity, timed obligations and cross-module effects.
- [ ] Negative, concurrency, timeout/retry and scope-isolation cases preserve prior approved state and return actionable errors; no direct cross-module table writes or implicit auto-approval.

## Requirements closed
This task contributes implementation coverage for the source requirements below. “Closed” means ownership within this backlog, not that tests have passed. No new warehouse FR or scenario namespace is allocated here.
- `G06`: Detailed time-phased supply projection
- `G07`: Unknown supply versus verified zero

## Scenarios closed
The real-world cases above and assigned source acceptance cases become executable implementation evidence. No research checklist is represented as executed.

## Closes
`WH-P03` in the [coverage ledger](https://github.com/neetub1508/warehouse-planning-issues/blob/main/docs/COVERAGE.md). Existing warehouse issues retain their current state.

## Implementation areas and migration policy
Extend owning warehouse/base/trade public providers, source entities/DTOs, query/export APIs and existing operational screens only where a missing field is proven. Exact implementation paths and T-row identifiers are resolved in the implementation PR from current code; paths are not invented by this design review. No production code lives in this issue repository.

No migration allocated at design stage. Use only the next free additive version within the owning installed warehouse module band after its data-model authority is amended. Never renumber applied migrations, reuse reserved deleted-adapter bands or assume a historical free-range observation remains current.

## Traps
- Historical September findings describe a past snapshot. Verify present code and canonical issue coverage before calling a source defect current.
- Unknown/missing input is not zero. Optional provider absence must be visible and must not silently enable an execution action.
- Baseline release is shadow/advisory; operational changes require reviewed acceptance by the authoritative owner. Automatic release is a separate capability gate, not implied by scheduling.
- Sealed history, owner/site scope and idempotency must survive reruns, upgrades, disable and restore.

## Sources
- [Warehouse design or issue](https://github.com/neetub1508/warehouse-issues/issues/562)
- [Warehouse design or issue](https://github.com/neetub1508/warehouse-issues/issues/112)
- [Warehouse design or issue](https://github.com/neetub1508/warehouse-issues/issues/584)
- [Warehouse design or issue](https://github.com/neetub1508/classic/blob/main/warehouse-base/backend/src/main/java/ai/warehousebase/service/allocation/WhbOnOrderSource.java)
- [Warehouse design or issue](https://github.com/neetub1508/warehouse-issues/blob/main/docs/reference/downloads-2026-10-01/Warehouse_Service_Parts_Deep_Audit_2026-09-30/02-Warehouse-Gaps.md)

Public competitor documentation establishes reference capabilities; the Scope and Acceptance here are proposed product behavior, not a guarantee of proprietary algorithm parity.
