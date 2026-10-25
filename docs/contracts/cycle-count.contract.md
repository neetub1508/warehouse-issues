# Functional Contract — Count, adjustment, holds and stock control

> **What this is.** The functional truth for the inventory-control half of FRD §6.9: the stock adjustment
> with its value-and-quantity approval threshold, the count (cycle, stocktake, empty-bin) that proposes an
> adjustment and never writes on-hand, the count programme as a policy object, holds as records, the
> expiry state and the four shelf-life enforcement points, the aged-stock measure, the reconciliation-exception
> grid and the ABC recompute. The three-leg transfer is [`stock-transfer.contract.md`](stock-transfer.contract.md).
> Every rule row names its requirement in **Source** (`DECISIONS.md` `D-17` item 1).
>
> **What this is not.** It does not restate the single writer: every movement here goes through
> [`movement-post-reverse.contract.md`](movement-post-reverse.contract.md) and a row cites its `MPR-*` id.
> Allocation is [`reservation-allocation.contract.md`](reservation-allocation.contract.md).
>
> **Status.** Derived 2026-10-23 (v0) from `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` §6.9 (`FR-145`…`FR-163`,
> `FR-165`, `FR-463`) and checked against the built code in `classic` (`warehouse`, `warehouse-base`) by name.
> Where the FRD and the code differ the FRD rule is kept and §9 records the difference. Not ratified.

---

## 0. Identity

| | |
|---|---|
| **Workflow** | Adjustment: create → submit → (auto-post inside thresholds, or approve / reject) → post · Count: generate → freeze → enter counts → submit → (post, or pending approval → recount / approve → post) · cancel · Hold: place → release · Reconciliation exception: raised → assigned → resolved · Lot expiry by job |
| **Module** | `warehouse` (documents, `wh_`) over `warehouse-base` (ledger, reason codes, lots, shelf-life policy, jobs) |
| **Domain baseline** | `L-1`, `L-2`, `L-10`; `FR-436` single writer; `movement-post-reverse.contract.md` `MPR-T1-01` (post), `MPR-T1-10` (status change); classic `warehouse/docs/contracts/count.contract.md` (`CNT-*`, the as-built count rows this contract adopts) |
| **Owning tasks** | `issues/p2-01.md` (adjustments) · `issues/p2-03.md` (holds) · `issues/p2-04.md` (counts) · `issues/p2-05.md` (expiry, shelf life) · `issues/p2-06.md` (reconciliation exceptions) · `issues/p3-14.md` (empty-bin) · `issues/p0-13.md` (dated-obligation rule) · `issues/p1-03.md` (ABC classes) |
| **Primary tables** | `wh_stock_adjustments`, `wh_stock_adjustment_lines`, `wh_adjustment_approval_policies`; `wh_counts`, `wh_count_lines`, `wh_count_zone_assignments`, `wh_count_tasks`, `wh_count_programs`, `wh_count_program_scopes`; `wh_hold_types`, `wh_holds`; `wh_reconciliation_exceptions`; base `whb_reason_codes`, `whb_lots`, `whb_item_site_settings` |
| **Code (as built)** | `WhStockAdjustmentService`, `WhAdjustmentApprovalPolicyResolver`, `WhStockAdjustmentAutoPostGuard`; `WhCountService`, `WhCountPostingService`, `WhCountAutoPostGuard`, `WhCountProgramService`, `WhbCycleCountSchedulingJob`; `WhHoldService`, `WhHoldAllocationGate`; `WhbShelfLifePolicyService`, `WhbLotExpiryJob`, `WhbNearExpiryResolver`; `WhStockAgeingService`; `WhReconciliationExceptionService`, `WhReconciliationExceptionRecorder` |
| **Routes** | WS-089 Stock Adjustments · WS-093 Count Programs · WS-094 Counts · WS-095 Count Entry & Variance · WS-091 Hold Types · WS-092 Holds · WS-098 Reconciliation Exceptions · WS-212 Stock Ageing · WS-213 Adjustment Register · WS-214 Count History & Variance · WS-221 Expiry & Shelf-life Register |
| **Contract version** | `v0 — 2026-10-23` |

---

## 1. T1 — State machine

### 1.1 Status inventory

| Entity | Status | Represented by | Reachable via | Exits via | Kind | Source |
|---|---|---|---|---|---|---|
| Adjustment | `DRAFT` | `status` | `CCT-T1-01` | `-02`, `-06` | initial | `FR-145` |
| Adjustment | `SUBMITTED` | `status`; `submitted_at`, `requires_approval` | `CCT-T1-02` | `-04`, `-05`, `-06` | active | `FR-145` |
| Adjustment | `APPROVED` | `status`; `approved_at` | `CCT-T1-04` | `-07` | active | `FR-145` |
| Adjustment | `POSTED` | `status`; `posted_movement_id` | `CCT-T1-03`, `-07` | none | **terminal** | `FR-145` |
| Adjustment | `REJECTED` / `CANCELLED` | `status`; reason code + note | `CCT-T1-05` / `-06` | none | **terminal** | `FR-145` |
| Count | `GENERATED` · `FROZEN` · `COUNTING` · `PENDING_APPROVAL` · `APPROVED` | `wh_counts.status` | `CCT-T1-10`…`-16` | as §1.2 | active | `FR-153`, `FR-155` |
| Count | `POSTED` · `CANCELLED` | `status`; `posted_at` / cancel reason | `CCT-T1-13`, `-17`, `-18` | none | **terminal** | `FR-153`, `FR-159` |
| Hold | open · released | `wh_holds.placed_at` / `released_at` (no status column) | `CCT-T1-20` / `-21` | none after release | record | `FR-151` |
| Reconciliation exception | `OPEN` · `ASSIGNED` · `RESOLVED` | `status` | `CCT-T3-04`, `CCT-T1-23`, `-24` | `RESOLVED` is terminal | active | `FR-163` |
| Lot | `AVAILABLE` → `EXPIRED` | stock status of the lot's positions | `CCT-T3-02` | none (a disposition) | effect | `FR-160` |
| Count programme | active / inactive | registry convention | — | — | master | `FR-156` |

### 1.2 Transitions

| ID | From | Event / action | To | Guard | Actor (permission) | Side effects | Source |
|---|---|---|---|---|---|---|---|
| CCT-T1-01 | — | Create adjustment, lines with signed variance | `DRAFT` | `CCT-GRD-01` | `wh_stock_adjustments:create` | number issued | `FR-145` |
| CCT-T1-02 | `DRAFT` | Submit | `SUBMITTED` | `CCT-GRD-01`, `-02`; at least one line, no zero-variance line | `wh_stock_adjustments:submit` | the resolved policy and the applied thresholds are stored (`resolved_policy_id`, `threshold_quantity_applied`, `threshold_value_applied`) | `FR-145` |
| CCT-T1-03 | `DRAFT` | Submit, every line inside **both** thresholds and `warehouse.adjustment.auto_post_below_thresholds` on | `POSTED` | `CCT-GRD-02`; `WhStockAdjustmentAutoPostGuard` admits the auto type only — once `p8-30` adopts the type, it admits a request with `rule_source = ZERO_LEVEL` (`DAP-T1-04`: `DOCUMENT_DEFINED` zero levels, `acting_user_id` = submitter) instead of testing `approved_by = submitted_by`; the count's `isApprovedOnSubmission` likewise (R32-fix) | `wh_stock_adjustments:submit` | `CCT-T4-02` in the same transaction | `FR-145` |
| CCT-T1-04 | `SUBMITTED` | Approve | `APPROVED` | `CCT-GRD-03` | `wh_stock_adjustments:approve` | `approved_at`, note | `FR-145` |
| CCT-T1-05 | `SUBMITTED` | Reject | `REJECTED` | reason code required | `wh_stock_adjustments:approve` | none | `FR-145` |
| CCT-T1-06 | `DRAFT` · `SUBMITTED` | Cancel | `CANCELLED` | reason code required | `wh_stock_adjustments:cancel` | none | `FR-145` |
| CCT-T1-07 | `APPROVED` | Post | `POSTED` | every `MPR-T1-01` guard | `wh_stock_adjustments:post` | `CCT-T4-02` | `FR-145` |
| CCT-T1-10 | — | Generate (programme scope or ad hoc) | `GENERATED` | `CCT-GRD-10` | `wh_counts:generate` | tolerances and `recount_pct` copied onto the count | `FR-156`, `FR-157` |
| CCT-T1-11 | `GENERATED` | Freeze | `FROZEN` | — | `wh_counts:freeze` | book quantity and unit cost stored on every line, blind or not; `book_snapshot_taken_at`; `CCT-T4-04` | `FR-153`, `FR-157` |
| CCT-T1-12 | `FROZEN` | Enter counts (first counted line) | `COUNTING` | `CCT-GRD-05`, `-08` | `wh_counts:edit` | `counted_by`, `counted_at` per line | `FR-154` |
| CCT-T1-13 | `COUNTING` | Submit, every current line inside both tolerances | `POSTED` | `CCT-GRD-06` | `wh_counts:edit` | approved by the submitter; `CCT-T4-01` | `FR-155`, `FR-159` |
| CCT-T1-14 | `COUNTING` | Submit, a line outside either tolerance | `PENDING_APPROVAL` | `CCT-GRD-06` | `wh_counts:edit` | the whole count routes; nothing posts | `FR-155` |
| CCT-T1-15 | `COUNTING` · `PENDING_APPROVAL` | Recount (a first-attempt line beyond `recount_pct` on Submit, or named lines) | `COUNTING` | `COUNT_NOTHING_TO_RECOUNT` when none qualifies | `wh_counts:recount` | each original line superseded, never overwritten; a recount attempt number | `FR-154`, `FR-155` |
| CCT-T1-16 | `PENDING_APPROVAL` | Approve | `APPROVED` | `CCT-GRD-07` | `wh_counts:approve` | `approved_at`, note | `FR-155` |
| CCT-T1-17 | `APPROVED` | Post | `POSTED` | every `MPR-T1-01` guard | `wh_counts:post` | `CCT-T4-01` | `FR-159` |
| CCT-T1-18 | `GENERATED` · `FROZEN` · `COUNTING` · `PENDING_APPROVAL` | Cancel | `CANCELLED` | reason required (`COUNT_CANCEL_REASON_REQUIRED`) | `wh_counts:cancel` | posts nothing; frozen locations released; open count tasks cancelled | `FR-153` |
| CCT-T1-19 | — | Last pick leaves a storage location at exactly zero | `ZERO_STOCK` count, `FROZEN` | `CCT-T4-05` | system (pick transaction) | one `EMPTY_BIN` task | `FR-158` |
| CCT-T1-20 | — | Place a hold on an order, lot, item or location | open | `CCT-GRD-12` | `wh_holds:place` | hold number, `placed_by_actor_type` | `FR-151` |
| CCT-T1-21 | open | Release | released | `CCT-GRD-13` | `wh_holds:release` (and the hold type's release permission) | `released_at`, release reason; other holds on the subject untouched | `FR-151` |
| CCT-T1-22 | — | Mass place / release over a subject list. **#29 (D1–D4):** for a LOT or ITEM hold type the list may be filled by a **Find** — `GET /holds/mass/subjects` resolves supplier and / or receipt-date window inside the caller's subject reach (`subjectScope()`), RELEASE only subjects with an open hold of the type, over 500 refused with the real count (never truncated); the operator reviews the list and the unchanged `POST /mass` submits it, re-checking every guard. Preview fixes which subjects, not the hold records — RELEASE re-reads open holds at execution | one hold row per subject | `CCT-GRD-12`, `-13`; `TOO_MANY_SUBJECTS`; `HOLD_SELECTOR_SCOPE_UNSUPPORTED`, `HOLD_SELECTOR_RANGE_INVERTED` (Find only); reason required per the hold type's `requires_reason` | `wh_holds:mass` (Find + supplier picker too); RELEASE also `wh_holds:release` and the type's own `release_permission` | `CCT-T4-07` | `FR-152` |
| CCT-T1-23 | `OPEN` | Assign an owner | `ASSIGNED` | owner user active (`EXCEPTION_OWNER_USER_INACTIVE`) | `wh_reconciliation_exceptions:edit` | owner stamped | `FR-163` |
| CCT-T1-24 | `OPEN` · `ASSIGNED` | Resolve | `RESOLVED` | `CCT-GRD-19` | `wh_reconciliation_exceptions:edit` | resolution note; nothing moves | `FR-163` |

### 1.3 Guards

| ID | Predicate (must hold to proceed) | Refusal: code · field | Message shape | Source |
|---|---|---|---|---|
| CCT-GRD-01 | Every adjustment carries an ACTIVE catalogue reason code of the adjustment context, and a note where the reason `requires_note` | `ADJUSTMENT_REASON_INVALID` · `reasonCodeId`; `ADJUSTMENT_REASON_NOTE_REQUIRED` · `note` | names the reason | `FR-145` |
| CCT-GRD-02 | The approval threshold is resolved most-specific-first (site × owner × category × reason, effective-dated) and gates by **value and by quantity**: a line beyond either `threshold_quantity` or `threshold_value` makes `requires_approval = true` | a policy with neither threshold is refused `POLICY_NO_THRESHOLD`; an inverted window `POLICY_WINDOW_INVALID` | names the policy and the threshold that fired | `FR-145` |
| CCT-GRD-03 | The adjustment approver is not its maker | `403 ADJUSTMENT_SELF_APPROVAL` · `approvedBy` | *"the maker may not approve their own adjustment"* | `FR-145` |
| CCT-GRD-04 | The book quantity is the one frozen at `CCT-T1-11` and stored on the line; the variance is `counted − (book + movement at the line's grain after the snapshot and up to counted_at)`, excluding the count's own movements — never live on-hand | — (computed; asserted by test) | — | `FR-153` |
| CCT-GRD-05 | While blind and not submitted, book, window movement and every variance figure are absent from the API and the export | — (never on the wire) | — | `FR-154` |
| CCT-GRD-06 | Tolerance gates posting by quantity percentage (`tolerance_pct`) **and** value (`tolerance_value`), defaulted from `warehouse.count.default_tolerance_pct` / `_value` | — (routes to `PENDING_APPROVAL`, `CCT-T1-14`) | — | `FR-155` |
| CCT-GRD-07 | The approver differs from every maker of the count — every submitter, every `counted_by` (superseded lines included), every zone assignee | `403 COUNT_SELF_APPROVAL` · `approvedBy` — under the engine these makers are the request's frozen `excludedActorIds` (`DAP-GRD-03`, R32-fix) | *"a counter may not approve the count"* | `FR-155` |
| CCT-GRD-08 | A keyed-back sheet's `countedAt` lies in `[book_snapshot_taken_at, now]` | `422 COUNT_COUNTED_AT_INVALID` · `countedAt` | names the window | `FR-154`, `FR-153` |
| CCT-GRD-09 | A line's variance reason, when given, is an ACTIVE `COUNT_VARIANCE` reason; none → `COUNT_OVER` / `COUNT_SHORT` by sign | `422 COUNT_REASON_INVALID` · `lines[n].reasonCodeId` | names the reason | `FR-159` |
| CCT-GRD-10 | A count programme names a type (`ABC` · random · full · zone · item · discrepancy-triggered), a scope, a cadence and the policy fields (blind flag, recount threshold, approval threshold, `freeze_locations`, per-run task cap) | `COUNT_PROGRAM_TYPE_INVALID`, `COUNT_PROGRAM_SCOPE_REQUIRED`, `COUNT_PROGRAM_CADENCE_REQUIRED`, `COUNT_PROGRAM_CRON_INVALID` | names the missing field | `FR-156` |
| CCT-GRD-11 | Until the ABC recompute ships, the `ABC` programme type reads *uses manually maintained classes* and scopes by the class held on the item × site, never a computed class | — (label; `warehouse.json` `ABC`) | — | `FR-156`, `FR-463` |
| CCT-GRD-12 | A hold type carries `blocks_allocation` and `blocks_pick`; a subject may carry two holds of different types at once; the allocator and the pick both ask "is there an open hold that blocks me" by query | `HOLD_TYPE_INACTIVE`, `SUBJECT_TYPE_MISMATCH`, `SUBJECT_NOT_FOUND`, `REASON_REQUIRED`, `REASON_WRONG_CONTEXT`; allocation refused `ALLOCATION_HELD` | names the hold type and subject | `FR-151` |
| CCT-GRD-13 | A release names a reason and is made by a holder of the hold type's release permission; a released hold is not released again | `RELEASE_PERMISSION_REQUIRED`, `HOLD_ALREADY_RELEASED` | names the hold number | `FR-151` |
| CCT-GRD-14 | A single-object status change is a balanced `STATUS_CHANGE` movement with a reason through `MPR-T1-10` | as `MPR-T1-10` | as cited | `FR-152` |
| CCT-GRD-15 | An `EXPIRED` lot is neither allocated nor issued | `EXPIRED_LOT_NOT_ISSUABLE` | names the lot and its expiry | `FR-160`, `FR-161` |
| CCT-GRD-16 | Point 1 — a received lot with less than the item's minimum remaining shelf life is refused at the dock | `SHELF_LIFE_RULE_VIOLATED` · `lines[i].lot_id` | names the lot, the days left and the minimum | `FR-161` |
| CCT-GRD-17 | Point 2 — allocation orders earliest expiry first where the strategy is FEFO (`orderEarliestExpiryFirst`) | — (ordering) | — | `FR-161` |
| CCT-GRD-18 | Point 3 — despatch refuses a lot below the minimum remaining resolved **counterparty (customer / ship-to) → B2B channel → item**, most specific first; the FRD measure is **days remaining** (§9 `CCT-DIV-02`) | `SHELF_LIFE_RULE_VIOLATED` | names the lot, the remaining, the minimum and the level that supplied it | `FR-161` |
| CCT-GRD-19 | Resolving an exception needs a note; a resolved exception is not resolved again | `EXCEPTION_RESOLUTION_NOTE_REQUIRED` · `note`; `EXCEPTION_ALREADY_RESOLVED` | names the exception | `FR-163` |
| CCT-GRD-20 | A location a stocktake (`FULL_PHYSICAL`) holds `FROZEN` takes no stock in or out until that stocktake is posted or cancelled, with the `CCT-T4-04` exemptions (own count adjustments; receipts into receiving, dock or staging; in-place status change; zero quantity). Checked on post and on Approve of a `PENDING` movement, reading the location rows `FOR SHARE` in id order so a Freeze committed while the post waits is seen | `409 LOCATION_FROZEN_FOR_STOCKTAKE` · `lines[i].location_id` | *"Location … is frozen by stocktake …, so nothing moves into or out of it until the stocktake is posted or cancelled … Post this after the stocktake ends."* | `FR-157` |

### 1.4 Transitions that must be unreachable

| ID | Forbidden | What makes it unreachable | Source |
|---|---|---|---|
| CCT-UNR-01 | A count writing `whb_stock_positions` itself, or posting its variance as anything but writer movements | `CCT-T4-01` is the only effect; architecture test on the writer | `FR-153` |
| CCT-UNR-02 | A variance measured against live on-hand, so a movement made during the count is reversed | `CCT-GRD-04` | `FR-153` |
| CCT-UNR-03 | A hold as a status value (`ON_HOLD`), or one release clearing another hold on the same subject | holds are rows (`wh_holds`); release touches one row | `FR-151` |
| CCT-UNR-04 | An adjustment, or a count variance line, posting without a reason | `CCT-GRD-01`, `CCT-GRD-09` | `FR-145`, `FR-159` |
| CCT-UNR-05 | A counter, submitter or zone assignee approving the count | `CCT-GRD-07` | `FR-155` |
| CCT-UNR-06 | An `ABC` programme implying a computed class before the recompute exists | `CCT-GRD-11` | `FR-156`, `FR-463` |
| CCT-UNR-07 | A threshold or date column merged with no job that reads it | each column in §3 names its job | `FR-165` |
| CCT-UNR-08 | A scheduled rule reading a bare `now()` | jobs take the injected UTC `Clock` | `FR-165` |
| CCT-UNR-09 | An `EXPIRED` lot allocated, picked or issued | `CCT-GRD-15` | `FR-160` |

---

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from | Extra | Source |
|---|---|---|---|---|---|
| CCT-T2-01 | Adjustment create / edit / submit / approve / post / cancel | `wh_stock_adjustments:{create,edit,submit,approve,post,cancel}` | as §1.2 | approver ≠ maker | `FR-145` |
| CCT-T2-02 | Approval policies | `wh_adjustment_approval_policies:{view,manage}` | — | admin | `FR-145` |
| CCT-T2-03 | Count generate / freeze / edit / recount / approve / post / cancel | `wh_counts:{generate,freeze,edit,recount,approve,post,cancel}` | as §1.2 | approve is a distinct permission | `FR-155` |
| CCT-T2-04 | Count programmes | `wh_count_programs:{create,edit,delete,view,export}` | — | — | `FR-156` |
| CCT-T2-05 | Holds place / release / mass; hold types | `wh_holds:{place,release,mass}` · `wh_hold_types:*` | open / — | mass is the v2 action | `FR-151`, `FR-152` |
| CCT-T2-06 | Reconciliation exceptions assign / resolve | `wh_reconciliation_exceptions:edit` | `OPEN` · `ASSIGNED` | — | `FR-163` |

## 3. T3 — Time-driven rules

| ID | Rule | Trigger (clock) | Changes | Notified | Job | Source |
|---|---|---|---|---|---|---|
| CCT-T3-01 | A count programme generates its counts on its cadence, within the per-run task cap | the programme's next scheduled date | a `GENERATED` count per due scope | count supervisor | `WhbCycleCountSchedulingJob` | `FR-156`, `FR-165` |
| CCT-T3-02 | A lot past its hard date (`LEAST(expiry_date, use_by_date)`, the one rule in `lot-serial-status` `LSS-GRD-02a`) moves to `EXPIRED` | hard date < site day | `CCT-T4-08` | stock controller | `WhbLotExpiryJob` (`WHB_LOT_EXPIRY`) | `FR-160`, `FR-161`, `FR-165` |
| CCT-T3-03 | Near-expiry notification at `expiry − near_expiry_days`, resolved item × site → item → `warehouse.expiry.near_expiry_days`; the register buckets by `warehouse.expiry.register_bucket_days` | the same clock | nothing — alert `LOT_NEAR_EXPIRY` + WS-221 | stock controller | `WhbNearExpiryResolver` with the expiry job | `FR-160` |
| CCT-T3-04 | Ledger-versus-position drift, position-versus-allocation drift, orphaned reservations and a ledger chain break each raise an exception row with an owner and an action; its age is reported | the recorder's run | `POSITION_DRIFT`, `RESERVATION_DRIFT`, `ORPHANED_RESERVATION`, `LEDGER_CHAIN_BREAK` rows `OPEN` | assigned owner | `WhReconciliationExceptionRecorder` | `FR-163`, `FR-165` |
| CCT-T3-05 | Aged-stock and no-movement buckets are measured from the **last outward movement**, valued per bucket, split by warehouse and by each site's `REGISTERED` branch as at the report date; a linked-branches view is a separate, non-additive grouping | the report date | nothing (projection) | — | `WhbStockAgeingProjectionScheduler`; WS-212 | `FR-162` |
| CCT-T3-06 | ABC recompute, per site (S-1…S-9 of #33, as amended): twelve whole site months of `wh_demand_history.quantity` before the run month (migrated rows count) per item, valued at the site's current method unit cost (`WhbCostLayerMath.methodCost` — AVCO average or FIFO oldest positive open layer), else the latest layer's unit cost, else 0 (uncosted); every demanded item counts in the site total, only items with a `whb_item_site_settings` row are classed; ranked by value, ties by item code; **an item is A while the cumulative share of the items ranked above it (excluding itself) is below the A cut-off, B while below the B cut-off, else C** (S-4 amended 2026-10-26 to the built exclusive rule — the top item is always A); a zero-value item is C; the class replaced moves to `previous_abc_class` only when a new site month is computed; one `whb_job_runs` row per site whose outcome note names the cost basis and counts the uncosted and row-less items | monthly, 02:30 on the 1st (`warehouse.abc.recompute.cron`) | the item × site class, `previous_abc_class`, `abc_computed_at` | — (ratified 2026-10-26, #33 S3 F6: no notification; the outcome is the `whb_job_runs` row on WS-064 and the computed date on WS-093) | `WhAbcRecomputeJob` (`WH_ABC_RECOMPUTE`) | `FR-463`, `FR-165` |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in | Source |
|---|---|---|---|---|
| CCT-T4-01 | Count post | **one movement per non-zero variance line**, carrying the line's reason, balanced against the site's `COUNT_VARIANCE` virtual location, `source_document_type = COUNT`; routed counts post the approval-gated type, auto-posted counts the auto type; the count never writes positions | `WhCountPostingService` → writer | `FR-153`, `FR-159` |
| CCT-T4-02 | Adjustment post | one writer movement (`ADJUST_UP` / `ADJUST_DOWN`, or the `_AUTO` pair on `CCT-T1-03`) carrying the reason; `posted_movement_id` stored | `WhStockAdjustmentPostingService` | `FR-145` |
| CCT-T4-03 | A movement posts with a reason whose `affects_demand_history = false` | the movement is excluded from demand history, so a write-off does not inflate the reorder point | demand-history reader over `whb_reason_codes` | `FR-146` |
| CCT-T4-04 | Freeze with `freeze_locations` | the scoped locations become `COUNTING` (cycle) or `FROZEN` (stocktake); the allocator admits only `AVAILABLE` locations; post and cancel release them. Hold and release lock the location rows `FOR UPDATE` in id order before reading them and save them as entities (`facility-branch-link` `FBL-GRD-16`), so a count never writes back a commingle policy or dedicated owner changed meanwhile. **While a stocktake holds a location `FROZEN`, the movement writer refuses every move into or out of it** (`CCT-GRD-20`), on the post and on the Approve of a `PENDING` movement, `409 LOCATION_FROZEN_FOR_STOCKTAKE` · `lines[i].location_id`. Admitted: the holding stocktake's own `COUNT_ADJUST` / `COUNT_ADJUST_AUTO`; a receipt-class movement (`RECEIPT`, `RETURN_RECEIPT`, `TRANSFER_ARRIVE`, `TRANSFER_RETURN`, `RETURN_FROM_ASSET`) adding stock to a `RECEIVING` / `DOCK` / `STAGING` location, which the GRN and return-receipt resolvers still offer while `FROZEN`; an in-place `STATUS_CHANGE` whose stock lines all sit at one location; a zero-quantity line. A cycle count's variance at a stocktake-`FROZEN` location is refused until the stocktake ends; reversals get no exemption. Putaway confirm already refuses a non-`AVAILABLE` destination | `WhCountService`, `WhbLocationCountStatusService`, `WhCountFrozenLocationGuard` (`WhbMovementPostGuard` + `WhbMovementApprovalGuard`) | `FR-156`, `FR-157` |
| CCT-T4-05 | A pick leaves its source storage location with every position row exactly zero | a `ZERO_STOCK` count over that one location is raised and frozen inside the pick transaction, with an `EMPTY_BIN` task; none when an open `EMPTY_BIN` task exists or the location is not storage | `WhEmptyBinVerificationService` (called by `WhPickTaskWriter.pick`) | `FR-158` |
| CCT-T4-06 | A hold is placed or released | allocation (`WhHoldAllocationGate`) and pick read open blocking holds by query at the moment of the action | hold gate | `FR-151` |
| CCT-T4-07 | Mass action | one hold row (or release) per subject, all in one transaction, with the same reason; **no movement is posted and nothing is written to `whb_lots`** (`WhHoldService.java:220-225`, `FR-096`); a subject already holding an open hold of the type is skipped. **#29:** a Find matches a subject when EITHER a `POSTED` goods receipt (`DRAFT`, `CANCELLED`, `REVERSED` excluded) of the supplier names it with `received_at` in the half-open window `[start of from-day, start of day after to-day)` in the user's zone **on that same receipt**, OR a current `SUPPLIER` lot party (`effective_to IS NULL`) names the supplier — unconditionally on a supplier-only Find; with a window, the lot's `receipt_date` (plain DATE) is the fallback **only for a lot with no `POSTED` receipt line** (a received lot is dated by its receipts, never by its first receipt's date, D2); a date-only Find reads receipts alone. The Find fetches one row past the cap and refuses rather than truncate. The Find writes nothing; the mass audit line appends the Find criteria the caller sends (supplier, window, timezone validated as a `ZoneId` — refused otherwise, as Find refuses it) and which source matched, **computed by the server over the submitted list** (receipt / lot party / neither) — never a caller-asserted count | `WhHoldService`, `WhHoldRepositoryCustomImpl.findSelectorMatches`, `.findSelectorMatchesAmong` | `FR-152`, `FR-096` |
| CCT-T4-08 | Lot expiry job | a `STATUS_CHANGE` to `EXPIRED` through `MPR-T1-10`, reason `EXPIRED`, `actor_type = SCHEDULED_JOB`, `source_document_type = LOT_EXPIRY`; then `whb_lots.status_code = EXPIRED` once none of the lot's stock is still issuable — the same two effects as `LSS-T3-01` | `WhbShelfLifePolicyService` | `FR-160`, `FR-161` |

## 5. T5 — Screen contract (web only, `D-17` item 2)

| ID | Screen | Rule | Source |
|---|---|---|---|
| CCT-T5-01 | WS-089 Stock Adjustments | tiles by status; row actions follow §1.2 and §2; the view shows the resolved policy and which threshold fired | `FR-145` |
| CCT-T5-02 | WS-093 Count Programs | the type picker labels `ABC` *uses manually maintained classes*; the form carries every `CCT-GRD-10` field | `FR-156`, `FR-463` |
| CCT-T5-03 | WS-094 Counts · WS-095 Count Entry | blind counts hide book and variance (`CCT-GRD-05`); zone assignment of counters; a printable count sheet (`COUNT_SHEET` print kind, identity without book) that can be keyed back with `countedAt`; Approve shown only when `canApprove` | `FR-154`, `FR-155`, `FR-157` |
| CCT-T5-04 | WS-094 stocktake | a full physical count shows the freeze window (`freeze_started_at`, `freeze_ended_at`) and the variance **value** before Approve | `FR-157` |
| CCT-T5-05 | WS-092 Holds · WS-091 Hold Types | a subject lists every open hold with its type and flags; Release per hold; Mass place/release from a selection. **#29:** the Mass modal (LOT / ITEM hold types) carries a Find section — supplier `SearchableSelect` (supply-side counterparties), receipt-date `DateRangePicker`, Find button that fills the subject list and lists each found subject with the source that matched it; an ITEM warning that the hold blocks the whole item for the owner; refusals shown in the modal's `AlertBox`; typing or pasting subject ids works as before | `FR-151`, `FR-152` |
| CCT-T5-06 | WS-221 Expiry & Shelf-life Register | near-expiry buckets and expired stock | `FR-160` |
| CCT-T5-07 | WS-212 Stock Ageing | buckets from last outward movement with value; branch split by `REGISTERED` branch; linked-branches view labelled non-additive | `FR-162` |
| CCT-T5-08 | WS-098 Reconciliation Exceptions | one grid: type, age, owner, action (assign, resolve) | `FR-163` |

## 6. Error codes (as built)

`ADJUSTMENT_REASON_INVALID` · `ADJUSTMENT_REASON_NOTE_REQUIRED` · `ADJUSTMENT_SELF_APPROVAL` (403) ·
`ADJUSTMENT_NO_LINES` · `ADJUSTMENT_LINE_ZERO_VARIANCE` · `ADJUSTMENT_NOT_CANCELLABLE` · `POLICY_NO_THRESHOLD` ·
`POLICY_WINDOW_INVALID` · `COUNT_SELF_APPROVAL` (403) · `COUNT_COUNTED_AT_INVALID` (422) · `COUNT_REASON_INVALID`
(422) · `COUNT_CANCEL_REASON_REQUIRED` · `COUNT_NOTHING_TO_RECOUNT` · `COUNT_LINES_UNCOUNTED` · `COUNT_INVALID_STATE` ·
`COUNT_PROGRAM_TYPE_INVALID` · `COUNT_PROGRAM_SCOPE_REQUIRED` · `COUNT_PROGRAM_CADENCE_REQUIRED` ·
`COUNT_PROGRAM_CRON_INVALID` · `HOLD_ALREADY_RELEASED` · `RELEASE_PERMISSION_REQUIRED` · `TOO_MANY_SUBJECTS` (422) ·
`HOLD_SELECTOR_SCOPE_UNSUPPORTED` (422 · `subjectType`) · `HOLD_SELECTOR_RANGE_INVERTED` (422 · `receivedTo`) ·
`EXPIRED_LOT_NOT_ISSUABLE` · `SHELF_LIFE_RULE_VIOLATED` · `EXCEPTION_RESOLUTION_NOTE_REQUIRED` ·
`EXCEPTION_ALREADY_RESOLVED` · `EXCEPTION_OWNER_USER_INACTIVE` · `LOCATION_FROZEN_FOR_STOCKTAKE` (409). An HTTP status is given only where it was read from
the code or the as-built count contract; the rest are fixed by their owning task.

## 7. Amendments

| Date | Change |
|---|---|
| 2026-10-23 | v0 derived for `D-17` item 1 (R30 `CP-FR-007` row 8, the count / adjust half) |
| 2026-10-23 | R31: `F-CA-006` (`CCT-T2-02`); `F-CA-009` (`CCT-T3-02`, `-T4-08` cite `LSS-GRD-02a`); `F-CA-010` (`CCT-T4-07`, `CCT-DIV-04`, FR-152 amended); `F-CA-011` (this contract owns holds; `lot-serial-status` cites it); `CCT-OPEN-01`…`-03` decided, `CCT-DIV-05` added |
| 2026-10-24 | R31 `P1-05` #54 S4c: `CCT-T4-04` — hold / release take the location row lock in id order (`facility-branch-link` `FBL-GRD-16`) |
| 2026-10-25 | `CCT-T1-03`, `CCT-GRD-07` | **R32-fix (`F-R32CA-002`, `-010`).** Below-threshold auto-post under the engine is a `DOCUMENT_DEFINED` zero-level request with the submitter as acting user, so the auto-post guard and `isApprovedOnSubmission` test `rule_source = ZERO_LEVEL`; the count's makers become frozen excluded actors. No behaviour change | R32 review |
| 2026-10-25 | R31 `P2-03` #29 S2 (R32 D1–D4): `CCT-T1-22` (Find + preview, release floor in the actor cell, reason per type), `CCT-T4-07` (union of sources, same-receipt window), `CCT-T5-05` (modal Find section), §6 `HOLD_SELECTOR_SCOPE_UNSUPPORTED`, `HOLD_SELECTOR_RANGE_INVERTED`; `CCT-DIV-04` stays open until S3 |
| 2026-10-26 | R31 `P2-03` #29 S4 (S3 standards P1/P2, functional F1–F4): `CCT-T4-07` lot-party date fallback limited to lots with no `POSTED` receipt line (D2), Find fetches cap+1 and refuses, audit source counts server-computed over the submitted list and the echoed timezone validated as a `ZoneId` |
| 2026-10-25 | R31 `P2-04` #37 S4 (S3 F2): `CCT-T4-04` amended with the writer refusal and its exemptions; `CCT-GRD-20` added (`LOCATION_FROZEN_FOR_STOCKTAKE` 409 · `lines[i].location_id`); `CCT-DIV-05` closed and its text corrected; `CCT-OPEN-01` built |
| 2026-10-26 | R31 `P1-03` #33 S4 (S3 F1, F6, F8): `CCT-T3-06` built — method-cost basis, S-5 population, item-code tie-break, S-4 amended to the exclusive cut-off rule, previous class rotated once per site month, no notified recipient (ratified); `CCT-DIV-03` closed; `CCT-OPEN-02` enforcement named |

## 8. Invariants and scenarios

`L-1`, `L-2`, `L-10`, `FR-436`; scenarios `WH-SC-059`, `WH-SC-098`, `WH-SC-108`, `WH-SC-111`, `WH-SC-112`,
`WH-SC-132`, `WH-SC-137`, `WH-SC-282`, `WH-SC-286`, `WH-SC-320`.

## 9. Code divergences (FRD rule kept)

| ID | File:line | FR | Difference |
|---|---|---|---|
| CCT-DIV-01 | `warehouse/…/service/whcount/WhCountPostingService.java:68` | `FR-153` | the FRD names the variance movement `COUNT_ADJ`; the code posts `COUNT_ADJUST` / `COUNT_ADJUST_AUTO` (both keyed `source_document_type = COUNT`). Same behaviour, different type code — **Triage 2026-10-23: AMEND-SPEC** — rule: the count variance posts as `COUNT_ADJUST` (manual) / `COUNT_ADJUST_AUTO` (auto-post), both `source_document_type = COUNT`. Evidence: `V500003` seed, `WhCountPostingService.java:68`. `FR-153` amended |
| CCT-DIV-02 | `warehouse-base/…/service/shelflife/WhbShelfLifePolicyService.java:170-177`; `warehouse-base/…/entity/WhbCounterparty.java:89` | `FR-161` | the FRD's despatch point is *"below Y days remaining"*; the code resolves `min_shelf_life_ship_pct`, a **percentage** of shelf life, on counterparty → channel → item — **Triage 2026-10-23: AMEND-SPEC** — rule: the despatch point refuses below a minimum **percentage** of shelf life remaining (`min_shelf_life_ship_pct`), resolved counterparty → channel → item — the same unit as the receipt point. Evidence: `WhbShelfLifePolicyService.java:170-177` javadoc cites `FR-161`. `FR-161` amended. reviewer-confirm |
| CCT-DIV-03 | `warehouse/…/service/whabc/WhAbcRecomputeJob.java` | `FR-463` | **CLOSED 2026-10-26 (#33 S4):** the monthly ABC recompute is built (`CCT-T3-06`); classes are computed from the first run (RK-003) and stay hand-editable until the next run |
| CCT-DIV-04 | `warehouse/…/dto/request/WhHoldMassActionRequest.java:22` | `FR-152` | the FRD's mass hold selects by lot, LPN, location, supplier, item **or date range**; the code takes one subject type and a list of subject ids — no supplier or date-range selector. **Effect (R31 `F-CA-010`):** the code posts no movement on a mass hold (`WhHoldService.java:220-225`) — the FRD's FR-152 said each mass hold posts a balanced status-change movement, contradicting `FR-096`; FR-152 was amended 2026-10-23 to the movement-free hold, so only the selector difference remains — **Triage 2026-10-23: FIX-CODE** — owner `P2-03` #29 (v2 mass action), reopened |
| CCT-DIV-05 | `warehouse/…/service/whcount/WhCountFrozenLocationGuard.java` (the writer fence) | `FR-157` | **CLOSED 2026-10-25 (`P2-04` #37, built `b7de0227ea`)** — the movement writer now refuses moves into and out of a stocktake-`FROZEN` location (`CCT-T4-04`, `CCT-GRD-20`). Text corrected: before the fix the allocator (`AVAILABLE` only) **and** putaway confirm (`WhPutawayTaskService`) already refused, not "only allocation". Residual, outside this row and recorded on #37 as a follow-up: a manual reservation (`WhbReservationService.create`) still does not refuse a `FROZEN` location — **Triage 2026-10-23: FIX-CODE** — owner `P2-04` #37 |

## 10. Open rows

| ID | Question | Missing decision | Default until decided | Source |
|---|---|---|---|---|
| CCT-OPEN-01 | Which movements a `FROZEN` stocktake location refuses during the freeze window (receipts, putaway, moves, or allocation only) | **DECIDED R31 (2026-10-23), default replaced:** a `FROZEN` stocktake location refuses putaway into it, moves in or out and allocation; only the stocktake's own count adjustments post; receipts to dock or staging go ahead — **built 2026-10-25** (`P2-04` #37; `CCT-T4-04`, `CCT-GRD-20`; `CCT-DIV-05` closed) | none — built | `FR-157` |
| CCT-OPEN-02 | The two Pareto cut-offs' default values for the ABC recompute | **DECIDED R31 (2026-10-23):** A = up to 80 % of cumulative 12-month issue value, B = up to 95 %, C = the rest; editable per site; zero-value items are C | `WhAbcRecomputeJob.classify`; cut-offs `whb_warehouses.abc_a_cutoff_pct` / `abc_b_cutoff_pct` (`V500069`); "up to" read as the exclusive rule of `CCT-T3-06` (S-4 amended 2026-10-26) | `FR-463` |
| CCT-OPEN-03 | The aged-stock bucket boundaries | **DECIDED R31 (2026-10-23): default stands** — 0–30, 31–60, 61–90, 91–180, 181–365, > 365 days from the last outward movement; stock with no outward movement goes in the oldest bucket | the as-built projection's buckets (WS-212) | `FR-162` |

<!-- v0 2026-10-23. Amend with /functional-contract: every change references a row id and adds a §7 row. -->
