# Functional Contract — Manufacturing shop floor: operators, shifts, operations, routings, batches, job cards, board, tools and maintenance

> **What this is.** The functional truth for the R32 shop-floor layer of `warehouse-manufacturing` (`D-20` items 3, 10,
> 11, 17, 20): the operator / skill and shift masters, the operation master and the **routing master** (mandatory for
> make items with job cards), **production batches** and **job cards per batch per stage** with sequencing, start / pause /
> complete, crew booking, stage consumption and the job-work stage, the production board and daily plan, the tooling /
> die master and preventive maintenance. FRD-MFG §6.1 FR-787…FR-791, FR-802…FR-807, FR-821, FR-822, FR-832…FR-835.
>
> **What this is not.** PQC on a job card and the rework loop are [`mfg-qc-rework.contract.md`](mfg-qc-rework.contract.md)
> (R32 rows `QRW-T1-20`…); the order's release and snapshot are [`mfg-production-order.contract.md`](mfg-production-order.contract.md);
> unit serials, binding and PDI are [`mfg-pdi-unit-registry.contract.md`](mfg-pdi-unit-registry.contract.md); conversion
> costing is [`mfg-costing-close.contract.md`](mfg-costing-close.contract.md). The movement writer is
> `movement-post-reverse.contract.md`.
>
> **Status.** Derived 2026-10-25 (v0) from FRD-MFG §6.1 under `D-20` (R32 fold of the client PRD 2026-10-24). Not
> ratified; run through `functional-reviewer` before `P10-15`, `P10-16`, `P10-20`, `P10-24`, `P10-26` are built.

---

## 0. Identity

| | |
|---|---|
| **Workflow** | Masters (shifts → operators + authorisations → operations → routings, maker–checker) → release of a `uses_job_cards` order creates batches and job cards → stage by stage: ready → start ⇄ pause → book (crew, machine, shift, tool; good / rework / rejected / scrap) → stage consumption → complete → transfer to the next stage; job-work stage via a child subcontract order; board, daily plan; tools consume life; PM orders take machines / tools out of service |
| **Module** | `warehouse-manufacturing`; registries `V562001` (`P10-02`), menus / settings `V563000` (`P10-01`) |
| **Owning tasks** | `issues/p10-15.md` (operators, skills, shifts) · `issues/p10-16.md` (operations, routings) · `issues/p10-20.md` (batches, job cards) · `issues/p10-24.md` (board, daily plans) · `issues/p10-26.md` (tools, maintenance) · `issues/p10-01.md`, `issues/p10-02.md` (menus, settings, registries) |
| **Primary tables** | `whm_shifts`, `whm_operators`, `whm_operator_authorisations` (`V562010`); `whm_operations`, `whm_routings`, `whm_routing_operations` (`V562020`); `whm_production_batches`, `whm_job_cards`, `whm_job_card_events`, `whm_operation_confirmation_operators` (`V562060`); `whm_daily_plans`, `whm_daily_plan_lines` (`V562100`); `whm_tools`, `whm_routing_operation_tools`, `whm_tool_life_entries`, `whm_maintenance_plans`, `whm_maintenance_orders` (`V562120`) |
| **Status columns** | routing `DRAFT`/`SUBMITTED`/`APPROVED`/`OBSOLETE`; batch `OPEN`/`IN_PROGRESS`/`COMPLETED`/`CANCELLED`; job card `PENDING`/`READY`/`STARTED`/`PAUSED`/`HELD_QC`/`COMPLETED`/`CANCELLED`; daily plan `DRAFT`/`PUBLISHED`; tool `AVAILABLE`/`IN_USE`/`AT_JOB_WORKER`/`UNDER_MAINTENANCE`/`SCRAPPED`; maintenance order `OPEN`/`IN_PROGRESS`/`COMPLETED`/`CANCELLED` — no `CHECK` (`D-10`) |
| **Permission resources** | `whm_shifts`, `whm_operators`, `whm_operations`, `whm_routings`, `whm_job_cards`, `whm_production_batches` (via `whm_job_cards:view`), `whm_daily_plans`, `whm_tools`, `whm_maintenance_plans`, `whm_maintenance_orders` (FRD-MFG §7 R32 list); every verb → `:view` |

## 1. T1 — State machine

### 1.1 Transitions

| ID | From | Event | To | Guard | Actor | Side effects | Source |
|---|---|---|---|---|---|---|---|
| SFL-T1-01 | — | Create / edit a shift | active | `SFL-GRD-01` | `whm_shifts:create` / `:edit` | — | FR-787 |
| SFL-T1-02 | — | Create an operator; add an authorisation | active | `SFL-GRD-02` | `whm_operators:create` / `:authorise` | `authorised_by/at` stamped | FR-788 |
| SFL-T1-03 | — | Create / edit an operation | active | code upper, unique per company; required skill in `WHM_SKILL`; `operators_required ≥ 1` | `whm_operations:create` / `:edit` | — | FR-789 |
| SFL-T1-04 | — | Create a routing (blank or *Copy from BOM operations*) | `DRAFT` | `SFL-GRD-03` | `whm_routings:create` | `version_no` = 1, operations default from the operation master | FR-790 |
| SFL-T1-05 | `DRAFT` | Submit | `SUBMITTED` | `SFL-GRD-03`, ≥ 1 operation | `whm_routings:submit` | approval request in the engine (`p8-30`, doc type `WHM_ROUTING`, levels per FR-782) | FR-790 |
| SFL-T1-06 | `SUBMITTED` | Last level approves | `APPROVED` | no overlapping approved effectivity (`SFL-GRD-04`); not governed by an ECN (`409 VERSION_GOVERNED_BY_ECN`, FR-794) | engine | predecessor end-dated / obsoleted as `BOM-T1-06` | FR-790, FR-782 |
| SFL-T1-07 | `APPROVED` | *New version* | new `DRAFT` | an ECN when the setting requires it (`409 ECN_REQUIRED`) | `whm_routings:new_version` | deep copy, `supersedes_routing_id` | FR-790, FR-794 |
| SFL-T1-10 | order `RELEASED` (job-card item) | release creates batches | batches `OPEN` | `SFL-GRD-05` | system, in the release transaction | `whm_production_batches` of `standard_batch_size`, `batch_no` = order no. + `-B<nn>` | FR-802 |
| SFL-T1-11 | batch `OPEN` | release creates job cards | job cards `PENDING`; first operation `READY` | routing snapshot exists (FR-791) | system | one card per batch × operation, `JCB-` numbers in routing sequence | FR-803 |
| SFL-T1-12 | batch `OPEN` (no booking) | *Re-split* | batches re-created | Σ = order quantity; no job card started | `whm_job_cards:resplit_batch` | job cards regenerated | FR-802 |
| SFL-T1-13 | `PENDING` | predecessor transfers output | `READY` | available input > 0 | system | — | FR-804 |
| SFL-T1-14 | `READY` · `PAUSED` | *Start* / *Resume* | `STARTED` | `SFL-GRD-06`; machine and tool available (`SFL-GRD-09`, `-10`) | `whm_job_cards:start` | event row; first card of a unit-serial batch triggers serial assignment (`PUR-T1-01`) | FR-804, FR-805 |
| SFL-T1-15 | `STARTED` | *Pause* (reason `JOB_CARD_PAUSE`) | `PAUSED` | reason given | `whm_job_cards:pause` | event row | FR-805 |
| SFL-T1-16 | `STARTED` | *Book* | `STARTED` or `HELD_QC` | `SFL-GRD-07`, `-08`, `-09`, `-10` | `whm_job_cards:book` | one `OPC-` confirmation with crew, machine, shift, tool; conversion cost rows (`CST-T4-20`); tool life entry; stage consumption (`SFL-T4-02`); → `HELD_QC` when the checkpoint blocks (`QRW-T1-20`) | FR-805, FR-806 |
| SFL-T1-17 | `STARTED` | *Complete* | `COMPLETED` | `SFL-GRD-11`; no open blocking PQC | `whm_job_cards:complete` | good transfers to the next card (`SFL-T4-01`); batch rollups | FR-804, FR-805 |
| SFL-T1-18 | any booking `RECORDED` | *Cancel booking* | booking `CANCELLED` | the transferred quantity has not been started on downstream (`409 DOWNSTREAM_STARTED`) | `whm_job_cards:cancel_booking` | rollups, consumption, conversion rows and tool life reversed | FR-805 |
| SFL-T1-19 | `READY` (job-work operation) | *Start* | `STARTED` | job worker set | `whm_job_cards:start` | child `SUBCONTRACT` order created and linked (`SUB-T1-20`) | FR-807 |
| SFL-T1-20 | `STARTED` (job-work) | child order completes | `COMPLETED` | — | system | good = processed quantity received; transfers | FR-807 |
| SFL-T1-30 | `DRAFT` | Publish daily plan | `PUBLISHED` | ≥ 1 line; one plan per site × date | `whm_daily_plans:publish` | board shows plan vs actual | FR-822 |
| SFL-T1-40 | — | Create a tool | `AVAILABLE` | `SFL-GRD-12` | `whm_tools:create` | — | FR-832 |
| SFL-T1-41 | `AVAILABLE` · `IN_USE` | *Scrap* | `SCRAPPED` | no open maintenance order | `whm_tools:scrap` | reason required | FR-832 |
| SFL-T1-42 | — | Create PM / breakdown order | `OPEN` | machine or tool, not both | `whm_maintenance_orders:create` | `MNT-` number | FR-833 |
| SFL-T1-43 | `OPEN` | *Start* | `IN_PROGRESS` | — | `whm_maintenance_orders:start` | machine → `UNDER_MAINTENANCE` (`BREAKDOWN` for a breakdown order), tool → `UNDER_MAINTENANCE` | FR-833 |
| SFL-T1-44 | `IN_PROGRESS` | *Complete* | `COMPLETED` | downtime reason (`DOWNTIME`) | `whm_maintenance_orders:complete` | machine / tool back to `ACTIVE` / `AVAILABLE`; plan `next_due_*` re-dated; tool life reset when the plan says so | FR-833 |

### 1.2 Guards

| ID | Predicate | Refusal | Source |
|---|---|---|---|
| SFL-GRD-01 | Shift times set; no overlap with another active shift of the site (midnight-crossing handled) | `422 SHIFT_OVERLAP` · `startTime` | FR-787 |
| SFL-GRD-02 | Authorisation names an operation **or** a skill; `valid_from ≤ valid_to`; authoriser ≠ the operator's user | `422 AUTHORISATION_SCOPE_REQUIRED`; `403 AUTHORISATION_SELF_GRANT` | FR-788 |
| SFL-GRD-03 | Routing: item active and make; operation seqs unique and ascending; each work centre of the routing's site; a machine belongs to its operation's work centre; job-work operations name input, output item and job worker | `422 ROUTING_INVALID` · `operations[i]` | FR-790 |
| SFL-GRD-04 | One approved routing per `(item, site scope)` per date (gist EXCLUDE + pre-check with `flush()`) | `409 ROUTING_EFFECTIVITY_OVERLAP` | FR-790 |
| SFL-GRD-05 | A job-card item × site has an approved routing effective on the planned start date; batch-produced items have `standard_batch_size > 0` | `409 ROUTING_NOT_EFFECTIVE`; `422 STANDARD_BATCH_SIZE_REQUIRED` | FR-791, FR-802 |
| SFL-GRD-06 | Available input > 0 (previous card's transferred good, or the batch quantity for the first operation) | `409 PREVIOUS_STAGE_NOT_COMPLETE` | FR-804 |
| SFL-GRD-07 | good + rejected + scrap (cumulative on the card) ≤ available input; rejected and scrap carry reasons | `422 STAGE_QUANTITY_EXCEEDS_INPUT`; `422 REASON_REQUIRED` | FR-804, FR-805 |
| SFL-GRD-08 | Crew size ≥ `operators_required`; every member an active operator of the site authorised on the booking date for the operation (or its skill at ≥ level) | `422 CREW_TOO_SMALL`; `403 OPERATOR_NOT_AUTHORISED` (names user, operation) | FR-788, FR-805 |
| SFL-GRD-09 | Machine of the operation's work centre and `ACTIVE`; with `maintenance.overdue_mode = BLOCK` no overdue plan | `422 MACHINE_NOT_OF_WORK_CENTRE`; `409 MACHINE_UNAVAILABLE`; `409 MAINTENANCE_OVERDUE` | FR-786, FR-833 |
| SFL-GRD-10 | Each required tool `AVAILABLE`/`IN_USE` with `life_used + booked × life_per_unit ≤ life_total` | `409 TOOL_UNAVAILABLE` (names tool and remaining life) | FR-832 |
| SFL-GRD-11 | Complete: every unit of a unit-serial batch has its required bindings (`PUR-GRD-03`); stage consumption posted without shortage | `422 UNIT_BINDING_INCOMPLETE`; `422 BACKFLUSH_SHORTAGE` | FR-806, FR-812 |
| SFL-GRD-12 | Tool code unique per company; `life_total > 0`; `warn_at_percent` in (0, 100] | `422 TOOL_INVALID` | FR-832 |
| SFL-GRD-13 | Registry rows (`V562001`) inserted under the owning-module guard; menu sections ≤ 8 leaves | migration `RAISE` (`RL-003`) | FR-835, FR-834 |

### 1.3 Unreachable

| ID | Never happens | Why | Source |
|---|---|---|---|
| SFL-UNR-01 | A job card started before its predecessor transferred output | `SFL-GRD-06` | FR-804 |
| SFL-UNR-02 | A booking edited | cancel + re-book only (`SFL-T1-18`) | FR-805 |
| SFL-UNR-03 | A job-card order released without an approved routing | `SFL-GRD-05` | FR-791 |
| SFL-UNR-04 | A mobile shop-floor screen | `D-20` item 5; web screens accept a scanner as keyboard | FR-834 |

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from | Persona | Source |
|---|---|---|---|---|---|
| SFL-T2-01 | Maintain shifts, operators | `whm_shifts:*`, `whm_operators:create/edit` | — | production manager | FR-787, FR-788 |
| SFL-T2-02 | Authorise an operator | `whm_operators:authorise` | — | production manager (≠ operator) | FR-788 |
| SFL-T2-03 | Maintain operations / routings | `whm_operations:*`, `whm_routings:create/edit/submit` | `DRAFT` | design / production engineer | FR-789, FR-790 |
| SFL-T2-04 | Approve a routing level | engine level role | `SUBMITTED` | Design Head, Plant Head | FR-782, FR-790 |
| SFL-T2-05 | Start / pause / book / complete | `whm_job_cards:start/pause/book/complete` | per T1 | supervisor or operator | FR-805 |
| SFL-T2-06 | Board, daily plan | `whm_reports:view`, `whm_daily_plans:*` | — | planner, supervisor | FR-821, FR-822 |
| SFL-T2-07 | Tools, maintenance | `whm_tools:*`, `whm_maintenance_*:*` | per T1 | maintenance planner | FR-832, FR-833 |
| SFL-T2-08 | AUDITOR | `:view` only, never `:export` | any | auditor | FR-834 |

## 3. T3 — Time-driven rules

| ID | Trigger | Effect | Source |
|---|---|---|---|
| SFL-T3-01 | Nightly maintenance job (scheduler principal) | plans past `next_due_*` raise one alert per plan; tools at `warn_at_percent` raise one alert | FR-832, FR-833 |
| SFL-T3-02 | Authorisation `valid_to` passes | the operator is no longer authorised (read-time rule, no job) | FR-788 |

## 4. T4 — Cross-entity effects

| ID | Cause | Effect | Source |
|---|---|---|---|
| SFL-T4-01 | Job card completes (or books with `allow_partial_transfer`) | good quantity becomes the next card's available input; WIP by stage moves | FR-804 |
| SFL-T4-02 | Booking on an operation that consumes `BACKFLUSH`/`STAGE_BACKFLUSH` lines | one `PRODUCTION_STAGE_CONSUMPTION` movement (lines → `VIRT-PRODUCTION`), idempotency `JOB_CARD:<id>:CONSUME:<seq>`; lot / serial items never negative (`D-20` item 13a) | FR-806 |
| SFL-T4-03 | Job-work job card starts | child `SUBCONTRACT` order `PLANNED` → released with the batch quantity; dispatch, challan, receipt as `mfg-subcontracting` | FR-807 |
| SFL-T4-04 | Maintenance order `IN_PROGRESS` | capacity load deducts its planned minutes; bookings refused on the machine / tool | FR-833 |
| SFL-T4-05 | Booking with a tool | `whm_tool_life_entries` row; status `IN_USE` while a card using it is `STARTED` | FR-832 |

## 5. T5 — Screen contract

| ID | Screen | Reference / contents | Source |
|---|---|---|---|
| SFL-T5-01 | WS-380 Operators & Skills · WS-381 Shifts | Customer (authorisations child editor) · Department; operator name through the platform user-display helper; validity dates `formatDateSync` | FR-787, FR-788 |
| SFL-T5-02 | WS-382 Operations · WS-383 Routings | Department · Customer multi-tab (Header · Operations · Tools · Approval · Compare); compare is a backend diff | FR-789, FR-790 |
| SFL-T5-03 | WS-387 Job Cards · WS-388 Production Batches | Service Vehicle with Start / Pause / Book / Complete modals (refusals inside the modal `AlertBox`); a scan field accepts the job-card QR and serials; Batches read grid + re-split | FR-803…FR-805 |
| SFL-T5-04 | WS-393 Production Board · WS-394 Daily Plans | report board (status columns, batch Kanban, WIP by stage) — backend aggregates; Daily Plans Customer with plan-vs-actual tab | FR-821, FR-822 |
| SFL-T5-05 | WS-396 Tools & Dies · WS-397 Maintenance | Department + life history · Service Vehicle (plans tab, orders ladder) | FR-832, FR-833 |
| SFL-T5-06 | Menus | L2 *Engineering* (5), *Shop Floor* (7), *Quality & Units* (6) under *Manufacturing* (`V563000`) | FR-834 |

## 6. Error codes

`SHIFT_OVERLAP`, `AUTHORISATION_SCOPE_REQUIRED`, `AUTHORISATION_SELF_GRANT`, `ROUTING_INVALID`, `ROUTING_EFFECTIVITY_OVERLAP`,
`ROUTING_NOT_EFFECTIVE`, `STANDARD_BATCH_SIZE_REQUIRED`, `PREVIOUS_STAGE_NOT_COMPLETE`, `STAGE_QUANTITY_EXCEEDS_INPUT`,
`CREW_TOO_SMALL`, `OPERATOR_NOT_AUTHORISED`, `MACHINE_NOT_OF_WORK_CENTRE`, `MACHINE_UNAVAILABLE`, `MAINTENANCE_OVERDUE`,
`TOOL_UNAVAILABLE`, `TOOL_INVALID`, `DOWNSTREAM_STARTED`, `UNIT_BINDING_INCOMPLETE`, `BACKFLUSH_SHORTAGE` — all *(proposed)*.

## 7. Edge cases

| ID | Case | Expected | Source | Scenario |
|---|---|---|---|---|
| SFL-EC-01 | Shift 22:00–06:00 | crosses midnight; a booking at 02:00 defaults to it | FR-787 | 774 |
| SFL-EC-02 | Last batch smaller than the standard size | remainder batch | FR-802 | 781 |
| SFL-EC-03 | Partial transfer off, 9 of 10 good booked | nothing transfers until complete | FR-804 | 783 |

## 8. Out of scope

Finite scheduling (R-01); attendance, payroll, IoT, OEE (R-02 narrowed); mobile (`D-20` item 5); measuring-instrument
calibration (core `p8-20`).

## 9. Amendments

| Date | Change |
|---|---|
| 2026-10-25 | v0 derived from FRD-MFG §6.1 (R32, `D-20`) |

## 10. Invariants and scenarios

`D-10`, `L-1`, `RL-003`, MD-45, MD-47; scenarios `WH-SC-773`, `-774`, `-775`, `-781`, `-783`, `-784`, `-793`, `-799`.

## 11. Open rows

| ID | Question | Default |
|---|---|---|
| SFL-OPEN-01 | Partial transfer default per operation (PRD Q-PR2) | `false` |
| SFL-OPEN-02 | Do operators book their own output (tablet, web) or the supervisor (PRD Q-PR4)? | both, by permission; no mobile |
