TITLE: [Planning] [Warehouse] Planning support WH-P04 · Arbitrate multiple planning engines and publish versioned stocking policy through one authority
LABELS: task,warehouse
issue: TBD
---
<!-- planning-review: WH-P04 -->
Part of [planning product backlog](https://github.com/neetub1508/warehouse-planning-issues/blob/main/issues/00-EPIC-planning.md). **Task ID:** `WH-P04` · **Owner:** Warehouse-owned additive integration support · **Phase:** Foundation · **Priority:** essential.

**Authoritative source:** [issues/planning-support-04.md](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-support-04.md). This is a pre-build requirement, not a claim the capability is implemented or tested.

## Goal
Arbitrate multiple planning engines and publish versioned stocking policy through one authority.

## Scope
- Extend the current optional single-bean ExternalPlanningOwner contract to compose manufacturing MRP, inventory planning and future order planning without bean collision or competing ownership.
- Define effective item-site planning authority, precedence/conflict refusal and bulk/cached ownership resolution; preserve existing manufacturing [warehouse issue 602](https://github.com/neetub1508/warehouse-issues/issues/602) MRP and REORDER_POINT/NONE semantics.
- Add a scoped, reviewed policy-publication service with expected source revision, run reference, effective history and expiring manual overrides. No direct whb_item_site_settings writes by planning and no automatic overwrite of manufacturing parameters.
- Reuse existing settings and approval services; no generic policy DSL or separate approval workflow. Add source/provenance only to the owning core/base objects that need it.

- Extend authority arbitration to explicit output domains and fields, including optional execution classification abc_class separately from stocking-policy quantities. The existing monthly per-site ABC recompute remains owned by [warehouse issue 33](https://github.com/neetub1508/warehouse-issues/issues/33); do not replace or duplicate it.
- When a reviewed planning classification publisher takes authority for a scope/field, the legacy monthly ABC job must honor that active producer and avoid overwriting it. Revoke/expiry/disable/re-enable restores the declared producer through approved effective revisions; preserve prior class/provenance/history and unaffected execution-owned recomputes.

## Dependencies and ownership
- Required task contracts: [PL-F01](https://github.com/neetub1508/warehouse-planning-issues/blob/main/issues/pl-001.md).
- Existing canonical work to reuse; inspect its current contract before changing an implementation:
  - [Warehouse issue 602](https://github.com/neetub1508/warehouse-issues/issues/602) (open at review): Reuse open canonical work. Planning owns advanced statistical forecast and adapter, not duplicate masters.
  - [Warehouse issue 603](https://github.com/neetub1508/warehouse-issues/issues/603) (open at review): Reuse open canonical work; future planning orchestration must not be second MRP.
  - [Warehouse issue 577](https://github.com/neetub1508/warehouse-issues/issues/577) (closed at review): Existing completed seam; WH-P04/05 describe incremental multi-engine and PLANNING-origin contracts only.
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
Two engines claim the same raw material after an admin changes its planning method.
**When:** execute this task’s named operation through its supported UI/API using a sealed input revision and the actor’s current grants. **Then:** satisfy the applicable acceptance criteria below; expose the reason for rejected/unsupported outcomes and produce no unauthorized or duplicate execution effect.

### Scenario 2
A planner manually raises safety stock while a nightly recommendation is pending.
**When:** execute this task’s named operation through its supported UI/API using a sealed input revision and the actor’s current grants. **Then:** satisfy the applicable acceptance criteria below; expose the reason for rejected/unsupported outcomes and produce no unauthorized or duplicate execution effect.

### Scenario 3
Future order-planning provider is absent or disabled while inventory planning remains active.
**When:** execute this task’s named operation through its supported UI/API using a sealed input revision and the actor’s current grants. **Then:** satisfy the applicable acceptance criteria below; expose the reason for rejected/unsupported outcomes and produce no unauthorized or duplicate execution effect.

### Correction scenario 1
**Given** an active planning class publication and a legacy monthly ABC job racing with an authority revocation, **when** each checks the expected authority revision, **then** only the current field/domain producer commits; the failed actor receives a stale-authority refusal and no approved class history is overwritten.

## Acceptance
- [ ] Warehouse-only has unchanged reorder behavior; manufacturing-only still uses [warehouse issue 577](https://github.com/neetub1508/warehouse-issues/issues/577)/#602 behavior.
- [ ] Manufacturing plus inventory planning starts successfully and exactly one authority plans each item-site; conflicting claims fail explicitly.
- [ ] Publishing a stale target returns conflict with no partial settings changes; retry with same idempotency key returns original result.
- [ ] Manual override with reason and expiry survives nightly planning, and expiry resumes the declared authority with audit.
- [ ] Run two independent functional reviews against the same closed changed-file set and agreed contract; resolve their verified union and retain per-case implementation evidence. C1–C10 checks include UI reachability, actor/guard parity, timed obligations and cross-module effects.
- [ ] Negative, concurrency, timeout/retry and scope-isolation cases preserve prior approved state and return actionable errors; no direct cross-module table writes or implicit auto-approval.

- [ ] Authority is domain/field-specific: taking stocking-policy authority cannot implicitly claim execution ABC, and a derived planning XYZ/VED output cannot mutate execution abc_class.
- [ ] Run the existing monthly ABC recompute after a scoped planning classification publication; only the current authorized classification producer may write each field, while unaffected scopes keep original behavior.
- [ ] Test revoke/expiry/disable/re-enable plus concurrent/stale worker and next monthly run: one current classification writer, approved handover and retained historical classes. Reuse existing warehouse issue 33 and conditional cost follow-up 673 rather than filing another baseline ABC computation.

## Requirements closed
This task contributes implementation coverage for the source requirements below. “Closed” means ownership within this backlog, not that tests have passed. No new warehouse FR or scenario namespace is allocated here.
- `G04`: Policy history and override authority
- `G05`: One owner of policy calculation

## Scenarios closed
The real-world cases above and assigned source acceptance cases become executable implementation evidence. No research checklist is represented as executed.

## Closes
`WH-P04` in the [coverage ledger](https://github.com/neetub1508/warehouse-planning-issues/blob/main/docs/COVERAGE.md). Existing warehouse issues retain their current state.

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
- [Warehouse design or issue](https://github.com/neetub1508/warehouse-issues/issues/602)
- [Warehouse design or issue](https://github.com/neetub1508/warehouse-issues/issues/603)
- [Warehouse design or issue](https://github.com/neetub1508/classic/blob/main/warehouse/backend/src/main/java/ai/warehouse/port/replenishment/ExternalPlanningOwner.java)
- [Warehouse design or issue](https://github.com/neetub1508/warehouse-issues/blob/main/docs/reference/downloads-2026-10-01/SPM-Planning-Research-2026-09-30/06-Warehouse-Design-Decision-Gaps.md)

Public competitor documentation establishes reference capabilities; the Scope and Acceptance here are proposed product behavior, not a guarantee of proprietary algorithm parity.

- [Canonical source evidence](https://github.com/neetub1508/warehouse-issues/issues/33)

- [Canonical source evidence](https://github.com/neetub1508/warehouse-issues/issues/673)

- [Canonical source evidence](https://github.com/neetub1508/warehouse-issues/blob/main/issues/p1-03.md#L276)
