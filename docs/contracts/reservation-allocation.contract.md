# Functional Contract — Reservations as an open-item ledger, and allocation by configured strategy

> **What this is.** The functional truth for holding stock against demand: the reservation row with its
> holder quad, `SOFT` and `HARD` types, the Release that turns soft into hard, expiry of `SOFT` rows by a
> job, deterministic reason-coded de-allocation, allocation strategies and rules as configured rows that are
> recorded on the reservation they chose, the locking discipline, and the supersession fallback. Every rule
> row names its requirement in **Source** (`DECISIONS.md` `D-17` item 1).
>
> **What this is not.** Picking and despatch consume reservations — [`outbound-despatch.contract.md`](outbound-despatch.contract.md).
> The writer's availability check is [`movement-post-reverse.contract.md`](movement-post-reverse.contract.md).
>
> **Status.** Derived 2026-10-23 (v0) from `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` §6.10 (`FR-166`, `FR-167`,
> `FR-169`…`FR-173`, `FR-175`, `FR-176`), checked against the built code in `classic` by name and against the
> as-built `warehouse-base/docs/contracts/reservation.contract.md` (`RSV-*`). Not ratified.

---

## 0. Identity

| | |
|---|---|
| **Workflow** | Take (soft or hard, by allocation or directly) → extend (soft) → release (by row, by holder, by status change) · soft → hard at Release · expire (soft, by job) · consume (pick / despatch) · de-allocate on cancel |
| **Module** | `warehouse-base` (`whb_reservations`, `whb_allocation_strategies`, `whb_allocation_strategy_rules`, `whb_allocation_rules`) |
| **Domain baseline** | `L-10` (allocation is an open-item ledger, never a counter); `FR-436`; `FR-174` availability API |
| **Owning tasks** | `issues/p0-03.md` (locking) · `issues/p0-09.md` (reservation ledger) · `issues/p2-07.md` (allocation, expiry, strategy) |
| **Code (as built)** | `WhbReservationService`, `WhbReservationValidationService`, `WhbReservationReleaseGuard`, `WhbReservationExpiryJob`, `WhbReservationHolderNotifier`, `WhbAllocationService`, `WhbAllocationStrategyResolver`, `WhbAllocationCandidateOrdering`, `WhbAllocationVocabulary` |
| **Routes** | WS-047 Reservations (`/warehouse/ledger/reservations`) · WS-048 Allocation Strategies · REST `/warehouse/allocation` (`/allocate`, `/deallocate`, `/release`, `/availability`, `/availability/bulk`, `/reservation-ageing`) |
| **Contract version** | `v0 — 2026-10-23` |

---

## 1. T1 — State machine

### 1.1 Status inventory

| Entity | Status | Represented by | Reachable via | Exits via | Kind | Source |
|---|---|---|---|---|---|---|
| Reservation | `OPEN` (type `SOFT` or `HARD`) | **derived, not stored** (`V500033:44`, *"status is NOT stored"*): `released_at` null and `consumed_by_movement_line_id` null; `reservation_type`, `expires_at` (soft only) | `RSA-T1-01`, `-02` | `-03`…`-08` | active | `FR-166`, `FR-169` |
| Reservation | `RELEASED` | derived: `released_at` set; release reason | `RSA-T1-05`, `-06`, `-07` | none | **terminal** | `FR-166`, `FR-170`, `FR-171` |
| Reservation | `CONSUMED` | derived: `consumed_by_movement_line_id` set | `RSA-T1-08` | none | **terminal** | `FR-166` |
| Allocation strategy / rule | active · superseded | `version_no`, `supersedes_id`, `is_active` | `RSA-T1-09` | — | master (copy-on-write) | `FR-172`, `FR-173` |

### 1.2 Transitions

| ID | From | Event / action | To | Guard | Actor (permission) | Side effects | Source |
|---|---|---|---|---|---|---|---|
| RSA-T1-01 | — | Allocate demand lines by the resolved strategy | `OPEN` (`SOFT`, or `HARD` where the holder asks) | `RSA-GRD-01`…`-07` | `whb_reservations:create` (`/allocate`) | `RSA-T4-01` | `FR-166`, `FR-172`, `FR-175` |
| RSA-T1-02 | — | Take a reservation directly (a specific lot, serial or LPN) | `OPEN` | `RSA-GRD-01`, `-02`, `-08` | `whb_reservations:create` | holder quad stored | `FR-166`, `FR-167` |
| RSA-T1-03 | `OPEN` · `SOFT` | Extend | `OPEN` (later `expires_at`) | `RSA-GRD-09` | `whb_reservations:extend` | `WHB_RESERVATION_EXTENDED` | `FR-170` |
| RSA-T1-04 | `OPEN` · `SOFT` | **Release** (demand header Release) | `OPEN` · `HARD` | — | `wh_demand_orders:release` → `/release` | soft becomes hard; tasks are created (`ODS-T1-04`); `WHB_ALLOCATION_RELEASED_TO_HARD` | `FR-169` |
| RSA-T1-05 | `OPEN` | Release one row, reason-coded | `RELEASED` | `RSA-GRD-10` | `whb_reservations:release` | reason, `released_at` | `FR-166`, `FR-171` |
| RSA-T1-06 | `OPEN` (every row of a holder or holder line) | Release by holder — `DELETE /warehouse/ledger/reservations?holderSystem…` | `RELEASED` | every row permitted, else nothing changes | `whb_reservations:release` | default reason `HOLDER_CANCELLED` | `FR-167`, `FR-171` |
| RSA-T1-07 | `OPEN` · `SOFT`, `expires_at` passed | Expire | `RELEASED` (reason `EXPIRED`) | `RSA-T3-01` | scheduled job | `RSA-T4-03` | `FR-170` |
| RSA-T1-08 | `OPEN` · `HARD` | Consume at pick / despatch | `CONSUMED` | pick writer | system | reservation re-attached at pick where the picked grain differs | `FR-166` |
| RSA-T1-09 | a strategy or rule a reservation or task references | Edit | a new version; the old one superseded | copy-on-write | `whb_allocation_strategies:edit` | the referencing reservation still resolves to the row that ran | `FR-173` |

### 1.3 Guards

| ID | Predicate (must hold to proceed) | Refusal: code · field | Message shape | Source |
|---|---|---|---|---|
| RSA-GRD-01 | Every reservation carries the holder quad `(holder_system, holder_document_type, holder_document_id, holder_line_no ≥ 1)` from the registered vocabularies | `RESERVATION_HOLDER_SYSTEM_UNKNOWN`, `RESERVATION_HOLDER_DOCUMENT_TYPE_UNKNOWN`, `RESERVATION_HOLDER_LINE_NO_INVALID`, `RESERVATION_FIELD_REQUIRED` | names the field | `FR-167` |
| RSA-GRD-02 | A `SOFT` row carries `expires_at`; a `HARD` row carries none | `RESERVATION_EXPIRY_REQUIRED`; `RESERVATION_HARD_HAS_NO_EXPIRY` | names the type | `FR-167`, `FR-170` |
| RSA-GRD-03 | The strategy resolves most-specific-first by site, item, owner, customer and demand type to an ACTIVE, non-empty strategy | `ALLOCATION_NO_RULE`, `ALLOCATION_STRATEGY_NOT_ACTIVE`, `ALLOCATION_STRATEGY_EMPTY`, `ALLOCATION_STRATEGY_SUPERSEDED` | names the demand line | `FR-172` |
| RSA-GRD-04 | Candidates are ordered by the strategy's whitelisted keys only (FIFO, FEFO, LIFO, lot-specified, nearest location, fewest locations, single-LPN, highest-quantity bin, fixed location); an unlisted key is refused | `VALUE_NOT_WHITELISTED` | names the key | `FR-172` |
| RSA-GRD-05 | **No oversell**: every candidate grain is locked in ascending key order, re-read under the locks, and each take admitted by the writer's availability rule, so two takers of one unit cannot both succeed | the loser gets the short quantity, never a negative available | — | `FR-175` |
| RSA-GRD-06 | A held subject is not allocated; a status not permitted for the demand is not allocated; a lot-required item names its lot | `ALLOCATION_HELD`, `ALLOCATION_STATUS_NOT_PERMITTED`, `ALLOCATION_LOT_REQUIRED` | names the hold / status / item | `FR-172` |
| RSA-GRD-07 | Where the requested item is short, a superseding item is consulted **only** under the rule's `allow_supersession = true`, at its cumulative ratio; the reservation records `requested_item_id` | — (no substitution without the flag) | — | `FR-176` |
| RSA-GRD-08 | A serial is held by at most one open reservation | `RESERVATION_SERIAL_ALREADY_HELD` | names the serial | `FR-166` |
| RSA-GRD-09 | Extend only an `OPEN` `SOFT` row, to a time later than now and than its current expiry | `RESERVATION_ALREADY_CLOSED`; `RESERVATION_NOT_EXTENDABLE`; `RESERVATION_EXPIRY_NOT_LATER` | names the reservation | `FR-170` |
| RSA-GRD-10 | A manual release names an ACTIVE reason of the `RESERVATION_RELEASE` context, not `EXPIRED` / `PICKED` | `RESERVATION_RELEASE_REASON_REQUIRED`, `RESERVATION_RELEASE_REASON_INVALID` | names the reason | `FR-171` |
| RSA-GRD-11 | **Availability API**, single (`GET /availability`) and bulk (`POST /availability/bulk`), returns per item × site on-hand, hard-allocated, soft-allocated, available, in-transit, on-order and earliest expiry, scoped by item, site, owner and an as-of instant; the caller holds `whb_stock_positions:view` | `403` without the permission; `400` on a bulk request with no items or more than 200 (`WhbAvailabilityBulkRequest`) | — | `FR-174` |

### 1.4 Transitions that must be unreachable

| ID | Forbidden | What makes it unreachable | Source |
|---|---|---|---|
| RSA-UNR-01 | An allocated-quantity counter column as the source of truth, or a "zero all allocations" repair | allocation is the sum of `OPEN` rows; no counter column exists | `FR-166` |
| RSA-UNR-02 | The expiry job releasing a `HARD` row (a released order mid-pick) | the job selects `SOFT` rows past `expires_at` only | `FR-170` |
| RSA-UNR-03 | Hard-allocating every order at creation | allocation is `SOFT` until `RSA-T1-04` | `FR-169` |
| RSA-UNR-04 | Allocation order hard-coded in an `if` | ordering is `WhbAllocationCandidateOrdering` over strategy rows | `FR-172` |
| RSA-UNR-05 | An in-place `UPDATE` of a rule a reservation references | `RSA-T1-09` copy-on-write | `FR-173` |
| RSA-UNR-06 | A cancel that leaves an orphaned reservation reducing availability | `RSA-T4-02` | `FR-167`, `FR-171` |

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from | Extra | Source |
|---|---|---|---|---|---|
| RSA-T2-01 | Take / extend / release / release by holder | `whb_reservations:{create,extend,release}` | `OPEN` | owner and site permitted | `FR-166`, `FR-167` |
| RSA-T2-02 | Allocate / de-allocate / release to hard | `whb_reservations:{create,edit,release}` on `/warehouse/allocation` | — | — | `FR-169`, `FR-171` |
| RSA-T2-03 | Strategies and rules | `whb_allocation_strategies:*` | — | admin | `FR-172` |
| RSA-T2-04 | Ask availability (single / bulk) | `whb_stock_positions:view` | — | read only; reserves nothing | `FR-174` |

## 3. T3 — Time-driven rules

| ID | Rule | Trigger (clock) | Changes | Notified | Job | Source |
|---|---|---|---|---|---|---|
| RSA-T3-01 | `SOFT` reservations past `expires_at` are released; the release commits first, the holder is told afterwards | `expires_at` < now (`warehouse.reservations.expiry.cron`; default TTL `warehouse.reservation.default_ttl_minutes`) | `RELEASED`, reason `EXPIRED`; a movement-free audit row `WHB_RESERVATION_EXPIRED` | the holder (`WAREHOUSE_RESERVATION_EXPIRED`) | `WhbReservationExpiryJob` | `FR-170`, `FR-165` |
| RSA-T3-02 | The ageing report shows open reservations by age, and stale `HARD` rows separately | `warehouse.reservation.hard_stale_after_minutes` | nothing | — | `/warehouse/allocation/reservation-ageing` | `FR-170` |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in | Source |
|---|---|---|---|---|
| RSA-T4-01 | A reservation is created by allocation | the row records `allocation_strategy_id` and `allocation_rule_id`; the reservation detail shows the rule and strategy that chose the stock | `WhbAllocationService` | `FR-173` |
| RSA-T4-02 | A demand order or line is cancelled | de-allocation is deterministic and reason-coded: every `OPEN` row of the holder released, un-started tasks cancelled; allocate ten, cancel, and availability returns exactly to its pre-allocation value | `WhbAllocationService.deallocate` | `FR-171` |
| RSA-T4-03 | Expiry, release or consume | available = on-hand − open reservations recomputes from rows only | availability API | `FR-166`, `FR-170` |
| RSA-T4-04 | A superseding item is allocated | reporting distinguishes *stock of A* from *stock of A including superseded equivalents*. **Chain**: forward successors only (the allocator's: `REPLACES`/`PARTIAL` steps from `WhbSupersessionChainResolver.resolveAll`, never `INTERCHANGE` alternates, no `stock_treatment` filter); a step with no successor, no cumulative ratio, or a successor already on the chain is skipped; a cycle or truncation keeps the steps before the break and is flagged `equivalentsIncomplete`. **Date basis**: availability — the `asOf` instant's UTC date (the allocator's); WS-208 — today. **Unit and rounding**: an equivalent contributes its own available (and on hand) ÷ cumulative ratio, scale 4, `RoundingMode.DOWN`, in A's base unit. **Surface**: availability `includeEquivalents` (opt-in, default answer unchanged) and WS-208 `includeSupersededEquivalents` (`RSA-T5-03`); rows are never summed across A and B | `WhbAvailabilityService` (`P2-07` #53 G1a), `WhStockOnHandQueryService` (G1b); §8 `RSA-DIV-02` closes at S5 | `FR-176` |
| RSA-T4-05 | A demand line for a PHANTOM kit is allocated (P3-11 #57 G2, `VWO-T4-06`) | one allocation PER COMPONENT under the line's holder quad, each reservation stamped with `explosion_parent_item_id`, `explosion_parent_line_id`, `explosion_source`, `explosion_definition_id`, `explosion_version_no`, `explosion_quantity_per` (all or none, `chk_whb_reservations_explosion_attribution`, V501243); the duplicate-allocation guard (`RSV-P207-T1-01`) refuses a component only for that component's own open holds on the line; the stamp is set in-process only (never from POST /allocate JSON) and carried to the staged hold at pick; `requested_item_id` keeps meaning substitution only | `WhbAllocationService`, `WhbPickReservationService.reattach` | `FR-261` |

## 5. T5 — Screen contract (web only, `D-17` item 2)

| ID | Screen | Rule | Source |
|---|---|---|---|
| RSA-T5-01 | WS-047 Reservations | grid of rows with holder quad, type, expiry, status; the view shows the strategy and rule that chose the stock and the requested item when substituted; Release and Extend (soft only) actions | `FR-167`, `FR-173`, `FR-176` |
| RSA-T5-02 | WS-048 Allocation Strategies | rows and their ordered keys; Edit creates a new version; v1 seeds `FIFO_BY_RECEIPT` and `FIXED_LOCATION_FIRST` | `FR-172`, `FR-173` |
| RSA-T5-03 | WS-208 Stock on Hand (both tabs) | boolean filter `includeSupersededEquivalents` (default off) acts only with Item set: rows of A's forward successors are added, physical (own code, quantities, unit), under the same owner/site scope and sandbox exclusion; hidden unsortable columns `equivalentOfItemCode` (A's code on B rows) and `availableAsRequested` (available ÷ cumulative ratio, scale 4, DOWN); export = grid; the statistics strip stays on A alone | `FR-176`, `FR-400` |

## 6. Amendments

| Date | Change |
|---|---|
| 2026-10-23 | v0 derived for `D-17` item 1 (R30 `CP-FR-007` row 9) |
| 2026-10-26 | `P2-07` #53 S2: `RSA-T4-04` made checkable (chain direction, date basis, unit, rounding, surface); `RSA-T5-03` added for WS-208's inclusive view |
| 2026-10-23 | R31 `F-CA-018`: §1.1 — `RSA-T1-04` (soft → hard, still `OPEN`) removed from `RELEASED`'s inbound list; the status is derived from `released_at` / `consumed_by_movement_line_id`, not stored |
| 2026-10-26 | `P3-11` #57 G2: `RSA-T4-05` added — phantom-kit component reservations, their explosion stamp (V501243) and the per-component duplicate guard |
| 2026-10-26 | `P3-11` #57 S4e F4 (classic 0b21f1a642) — overlay on **`RSA-GRD-07`** / **`RSA-T4-05`**: a substitute's reservation also records the cumulative ratio it was taken at (`substitution_ratio`, V501247, carried to the staged hold); every reader that counts a hold for the requested item (Release's held-by-line and held-by-component, a kit pick, the trim, the per-component withdraw and amendment release, the despatch kit check) counts `base_quantity / ratio`, DOWN at scale 4; a pre-V501247 substitution counts at 1. |

## 7. Invariants and scenarios

`L-10`, `FR-436`; scenarios `WH-SC-025`, `WH-SC-053`, `WH-SC-099`, `WH-SC-101`, `WH-SC-184`, `WH-SC-190`.

## 8. Code divergences (FRD rule kept)

| ID | File:line | FR | Difference |
|---|---|---|---|
| RSA-DIV-01 | `warehouse-base/…/service/allocation/WhbAllocationVocabulary.java:37` | `FR-172` | the FRD's ordering key *"fewest locations"* is coded `FEWEST_PICKS` — **Triage 2026-10-23: AMEND-SPEC** — rule: the FRD's *fewest locations* key is the code value `FEWEST_PICKS` (`WhbAllocationVocabulary`). `FR-172` amended |
| RSA-DIV-02 | — (grep of `warehouse-base` / `warehouse` `src/main` for a supersession-inclusive availability or report finds none) | `FR-176` | the allocator substitutes and records `requested_item_id` (`WhbReservation.java:161`), but no report or availability answer separates *including superseded equivalents* — **Triage 2026-10-23: FIX-CODE** — owner `P2-07` #53 (`FR-176`), reopened |

## 9. Open rows

| ID | Question | Missing decision | Default until decided | Source |
|---|---|---|---|---|
| RSA-OPEN-01 | — | none: every FR in scope states a checkable rule | — | — |

<!-- v0 2026-10-23. Amend with /functional-contract: every change references a row id and adds a §7 row. -->
