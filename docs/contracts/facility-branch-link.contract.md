# Functional Contract — Facility and branch links: site identity, dated branch links, locations, custody, the serving-branch rule, the transfer request ladder

> **What this is.** The functional truth for a warehouse site's identity and its **dated links to platform
> branches** (`D-14`: link, never mirror; at most one `REGISTERED` link at every instant), the location
> hierarchy and its registry-driven behaviour, dated location custody, the location generator, the
> **serving-branch rule** for stock-consuming documents, the **transfer request** a branch raises, and
> movement between two companies of one install.
>
> **Status.** Derived 2026-10-23 (v0) for R30 `CP-FR-007` row 3 (`D-17` item a) from
> `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` §6.4 and §6.28, checked against the built code. Not ratified.
> Code disagreements are in §10.

---

## 0. Identity

| | |
|---|---|
| **Workflow** | Site create (no link) → add `REGISTERED` link → add `SERVING` / `FULFILMENT` / `RETURNS` links → change registration (maker–checker) → end links; location create / generate / block / custody; transfer request `REQUESTED` → approve (part) / reject → `TRANSFER` demand order |
| **Module** | `warehouse-base` (site, links, locations, custody); `warehouse` (docks, transfer orders, serving-branch rule, inter-company) |
| **Domain baseline** | `D-14` (`RG-001` canonical), `OD-19` safe default, `I-22`, `I-23`, `FR-408` (maker–checker) · `movement-post-reverse.contract.md` `MPR-GRD-07`, `-08` |
| **Owning tasks** | `issues/p1-05.md` (sites, links, locations, custody, external refs) · `issues/p1-06.md` (generator, docks) · `issues/p2-02.md` (transfer request ladder) · `issues/p1-17.md` (inter-company, v2) · `issues/p8-10.md` (`FR-461`, re-homed by `D-17` item 5) |
| **Primary tables** | `whb_warehouses`, `whb_warehouse_branch_roles`, `whb_warehouse_branches` (`V500012`); `whb_locations`, `whb_location_user_assignments`, `whb_location_external_refs` (`V500013`); `whb_location_owner_dedications` (`V500070`, `RG-014`); `whb_location_types` (`V500006`); `wh_dock_doors`, `wh_dock_appointments` (`V510010`); `wh_transfer_orders`, `wh_transfer_order_lines` (`V510031`) |
| **Permission resources** | `whb_warehouses:{view,create,edit,delete,export}` · `warehouse:warehouses:change_registration` · `whb_locations:{view,create,edit,delete,export,block}` · `wh_transfer_orders:{request,create,edit,approve,reject,cancel,allocate,receive,report_variance,write_off_transit,export}` |
| **Routes** | WS-016 Warehouses · WS-017 Locations · WS-018 Location Generator · WS-005 Location Types · WS-085 Dock Doors · WS-086 Dock Appointments · WS-090 Transfer Orders |
| **Contract version** | `v0 — 2026-10-23` |

### Acceptance checks

| # | Expects | Delivered by |
|---|---|---|
| A1 | A site has at most one `REGISTERED` link at every instant; a site with none is refused when used (`WH-SC-045`) | `FBL-GRD-01`, `-02` |
| A2 | Classification reads the link at `occurred_at`; access reads today's links | `FBL-T4-01`, `-02` |
| A3 | A registration change is maker–checker and refused while stock sits under a different GSTIN | `FBL-T1-04`, `FBL-GRD-04` |
| A4 | A branch raises a transfer request; the source approves / part-approves / rejects; approval creates the demand order (`WH-SC-314`) | `FBL-T1-08`…`-11` |

---

## 1. T1 — State machine

### 1.1 Status inventory

| Entity | Status | Represented by | Kind |
|---|---|---|---|
| Branch link | current / ended | `effective_from`, `effective_to` (`[from, to)`), role code | dated history |
| Location | `AVAILABLE` · `BLOCKED` · `DAMAGED` (Block / Unblock, `FBL-T1-06`, `-06a`) · `COUNTING` · `FROZEN` (set and cleared only by the count freeze, `cycle-count` `CCT-T4-04`) | `whb_locations.status` | operational |
| Custody assignment | current / released | `effective_from`, `effective_to` | dated history, retained forever |
| Transfer request | `REQUESTED` → `APPROVED` (lines carry `approved_quantity`) / `REJECTED` | `wh_transfer_orders.status` | the request half of the transfer lifecycle |

### 1.2 Transitions

| ID | From | Event | To | Guard | Actor | Side effects | UI | Source |
|---|---|---|---|---|---|---|---|---|
| FBL-T1-01 | — | Create site: code, name, company, structured address (`line1/2`, city, `state_code`, pincode, country, latitude, longitude), `gln`, `is_physical` | site with **no** link | `FBL-GRD-06` | `whb_warehouses:create` | — | WS-016 **Add** | FR-079, FR-080, FR-081 |
| FBL-T1-02 | no current `REGISTERED` | Add the first `REGISTERED` link | link current | `FBL-GRD-01`, `-03` | `warehouse:warehouses:change_registration` | — | WS-016 **Change registration** | FR-460 |
| FBL-T1-03 | — | Add / end a `SERVING`, `FULFILMENT` or `RETURNS` link | link current / ended | `FBL-GRD-03` | `whb_warehouses:edit` | changes access from now (`FBL-T4-02`), classification of nothing | WS-016 links tab | FR-079, FR-460 |
| FBL-T1-04 | `REGISTERED` link current | **Change registration**: closes the current row and opens the next **at the same instant**, maker–checker | old ended, new current | `FBL-GRD-01`, `-04`, `-05` | `warehouse:warehouses:change_registration`; approver ≠ requester | — | WS-016 **Change registration** | FR-079, FR-460 |
| FBL-T1-05 | — | Create / generate locations: zone, aisle / rack / level / position ranges, format mask, location type, default capacities — **preview** count, first and last code, then commit | locations `AVAILABLE` | `FBL-GRD-08`, `-09` | `whb_locations:create` | CSV import is the fallback (import batch) | WS-018 | FR-089 |
| FBL-T1-06 | `AVAILABLE` | Block (with reason) as `BLOCKED` or `DAMAGED` | that status | reason required | `whb_locations:block` (`WhbLocationController.java:320-321`) | stock stays where it is | WS-017 **Block** | FR-091 |
| FBL-T1-06a | `BLOCKED` · `DAMAGED` | Unblock | `AVAILABLE` | only `BLOCKED` / `DAMAGED`; `COUNTING` / `FROZEN` are never cleared here (`WhbLocationService.java:399`) — they belong to the count (`cycle-count` `CCT-T4-04`) | `whb_locations:block` (`WhbLocationController.java:330-331`) | none | WS-017 **Unblock** | FR-091 |
| FBL-T1-07 | — | Assign custody (`CUSTODIAN`, `DRIVER`, `HELPER`) | assignment current | `FBL-GRD-10` | `whb_locations:edit` | the previous custodian's row is ended, never overwritten | WS-017 custody tab | FR-088 |
| FBL-T1-08 | — | **Raise transfer request** against another site (created only by a user scoped to the **destination**) | `REQUESTED` | destination in caller's scope | `wh_transfer_orders:request` | — | WS-090 **Raise request** | FR-462 |
| FBL-T1-09 | `REQUESTED` | Approve, or part-approve by line `approved_quantity` (never a separate state) | `APPROVED` | `FBL-GRD-11`, `-12` | `wh_transfer_orders:approve`, scoped to the **source** site; approver ≠ requester (`FR-408`) | `FBL-T4-04`, `-05` | WS-090 **Approve** | FR-462 |
| FBL-T1-10 | `REQUESTED` | Reject with a reason | `REJECTED` | source in caller's scope | `wh_transfer_orders:reject` — its own verb, not `:approve` (`WhTransferOrderController.java:337`; `STR-T1-04`) | `FBL-T4-05` for the whole quantity | WS-090 **Reject** | FR-462 |
| FBL-T1-11 | — | Move goods between two companies of one install (v2): one action creates a demand order in the source company **and** a purchase order in the other, cross-referenced in the source quad, priced from `FR-244`'s transfer-price columns | both documents created | `FBL-UNR-04` | demand-order and PO create permissions | — | not built (v2, `P1-17`) | FR-465 |
| FBL-T1-12 | — | **Dedicate** a location to one or more owners from one instant (`effectiveFrom` defaults to now; never in the future) | dedication current | `FBL-GRD-16` | `whb_locations:edit` | the v1 scalar `dedicated_owner_id` is re-mirrored: the one current owner outside `OWNER_SET`, else `NULL` | WS-017 **Dedicated owners** row action, Add tab | FR-087, FR-468, `RG-014` |
| FBL-T1-13 | dedication current | **End** one dedication (`effectiveTo` defaults to now; never in the future, after its start). There is no delete — history is kept | dedication ended | `FBL-GRD-16`; End is permitted on a **retired** location (it opens nothing, so `LOCATION_INACTIVE` is not asked) | `whb_locations:edit` | scalar re-mirrored | WS-017 **Dedicated owners** → **End** link | FR-087, `RG-014` |
| FBL-T1-14 | — | Add / Edit **Dedicated Owner** field, written through in the same transaction ("the field is the truth" outside `OWNER_SET`): a current dedication to another owner is **ended now**, the field's owner is dedicated from now when not already; an empty field ends the current dedication — including when the policy is switched away from `OWNER_SET` with the field empty. Under `OWNER_SET` the field is disabled, sent empty, and the rows are the Dedicated owners action's alone | dedications as the field says | `FBL-GRD-16` (the new row is opened only where `FBL-T1-12` could open it — a PUT on a retired location is refused `LOCATION_INACTIVE`) | `whb_locations:edit` | — | WS-017 Add / Edit modal | FR-087, `RG-014` |

### 1.3 Guards

| ID | Predicate | Refusal: HTTP · code · field | Backstop | Source |
|---|---|---|---|---|
| FBL-GRD-01 | At most one `REGISTERED` link per site at every instant, over the whole history | `WAREHOUSE_REGISTRATION_OVERLAP` · `effectiveFrom` | `uk_whb_warehouse_branch_roles_single_registration` (`V500012:120`); exclusion `uk_whb_warehouse_branches_registered_history` (`V500012:330-332`) | FR-460 |
| FBL-GRD-02 | A site used by a movement or a numbered document has a `REGISTERED` link covering the instant; a site with none is refused **when used, not at create** | `422 UNREGISTERED_INSTANT` · `occurredAt` (ledger); `WAREHOUSE_NOT_REGISTERED` (document numbering) | `I-22` | FR-079, FR-460, FR-081 |
| FBL-GRD-03 | The linked branch is active and of the site's company; links of one role do not overlap for one branch | `WAREHOUSE_BRANCH_INACTIVE` / `WAREHOUSE_BRANCH_COMPANY_MISMATCH` / `WAREHOUSE_BRANCH_LINK_OVERLAP` · `branchId` | — | FR-460 |
| FBL-GRD-04 | Registration change across two different GSTINs is refused while the site holds on-hand, open reservations, inbound transit or open receipts / orders (`OD-19` safe default); same GSTIN: no stock rule | `409 WAREHOUSE_REGISTRATION_CHANGE_BLOCKED` · header, listing the blockers | — | FR-079, FR-460 |
| FBL-GRD-05 | The checker is not the maker; the change is not dated before the site's last movement, nor into a closed period | `422 WAREHOUSE_REGISTRATION_SELF_APPROVAL`; `WAREHOUSE_REGISTRATION_BEFORE_LAST_MOVEMENT` / `WAREHOUSE_REGISTRATION_PERIOD_CLOSED` · `effectiveFrom` | `I-23` (history append-only once a movement stands in its range) | FR-460, FR-079 |
| FBL-GRD-06 | `whb_warehouses.code` never derives from, copies or validates against `branch_code`; the site carries no `branch_id`, `legal_entity_id` or `tax_registration_id` — the GSTIN is read through the link | — (columns absent) | `V500012:36` | FR-079, FR-080 |
| FBL-GRD-07 | A location's type is a `whb_location_types` row whose flags (`is_physical`, `is_stock_holding`, `is_virtual_counterparty`, `is_mobile`, `is_transit`, `allows_mixed_owner`, `requires_assigned_user`, `is_pickable`, `is_receivable`, `counts_as_on_hand`, `is_staging`, `is_dock`) drive behaviour; `IN_TRANSIT`, `MOBILE`, `VEHICLE`, `TRAILER` are admitted | `422` `LOCATION_*` on `locationTypeCode` | FK by code, no `CHECK` (`D-10`) | FR-083 |
| FBL-GRD-08 | Locations form one self-referencing hierarchy (`SITE` → `BUILDING` → `ZONE` → `AISLE` → `RACK` → `LEVEL` → `POSITION`) with `location_level` and a materialised `path`; no cycle | `LOCATION_HIERARCHY_CYCLE` · `parentLocationId` | `chk_whb_locations_location_level`, `chk_whb_locations_not_own_parent` (`V500013:129-140`) | FR-082 |
| FBL-GRD-09 | Location codes are unique **within the site** | `LOCATION_CODE_EXISTS` · `code`; generator `LOCATION_GENERATE_TOO_MANY` / `_RANGE_INVALID` | `uk_whb_locations_warehouse_code` (`V500013:128`) | FR-089 |
| FBL-GRD-10 | One current custodian per location; custody ranges of one user do not overlap; the user is active | `LOCATION_CUSTODY_OVERLAP` / `LOCATION_CUSTODY_USER_INACTIVE` · `userId` | `uk_whb_location_user_assignments_one_custodian` (`V500013:299`); exclusion on custodian ranges | FR-088, FR-093 |
| FBL-GRD-11 | `approved_quantity` per line is 0 … requested quantity, and at least one line approves something | `TRANSFER_LINE_APPROVED_ABOVE_REQUESTED` / `TRANSFER_APPROVES_NOTHING` · `lines[i].approvedQuantity` | `CHECK (approved_quantity <= quantity)` (`V510031:351`) | FR-462 |
| FBL-GRD-12 | Approve / reject only a `REQUESTED` transfer; the approver is not the requester | `409 TRANSFER_NOT_REQUESTED`; `403 TRANSFER_SELF_APPROVAL` | — | FR-462 |
| FBL-GRD-13 | **Serving-branch rule.** A stock-consuming document handed over at a requesting branch (a store issue, a despatch from a shared site) posts directly from a site only when that branch holds a current `REGISTERED` or `SERVING` link to it **and** its GSTIN (`branches.gst_number`) equals the site's `REGISTERED` GSTIN at the document date; across GSTINs it is refused and offers *Raise request* | `422 CROSS_GSTIN_DIRECT_ISSUE` · `warehouseId` (the withdrawn dealer counter-sale code `CROSS_GSTIN_COUNTER_SALE` is not used — `D-16`, FR-359 withdrawn; no `warehouse*` code carries it, so no wire depends on it — R31 `F-CA-020`) | — | FR-461 — §10 row 1 |
| FBL-GRD-15 | Every site has its virtual locations — `SUPPLIER`, `CUSTOMER`, `ADJUSTMENT`, `SCRAP`, `PRODUCTION`, `IN_TRANSIT`, `COUNT_VARIANCE`, `OPENING_BALANCE`, `CONSUMED`, `JOB_WORKER`, `VALUE_OFFSET`, `COST_OF_SALES` — provisioned as `VIRT-<purpose>-<site>` with `counts_as_on_hand = false`, so they never appear in a stock report and always balance the ledger; every movement has a real from- and to-location, one of which may be virtual | the writer's `MPR-GRD-01` refusal for a one-sided movement | `WhbVirtualLocationProvisioner` (`ADJUSTMENT` → type `ADJUSTMENT_OFFSET`); location types `V500006` | FR-084 |
| FBL-GRD-14 | Capacity and constraint columns (weight, volume, height, LPN count, unit count, mixed-item, mixed-lot, mixed-owner, temperature zone, pick sequence, barcode, check digit) are on the location from v1 and **enforced at putaway Complete** from v1.1 (`D-18` item 5) for the five capacity columns `max_units`, `max_weight_kg`, `max_volume_cc`, `max_lpns`, `height_cm`: a NULL column is unconstrained, `0` is a real limit, reaching a limit exactly passes. **Measurement basis:** standing stock is every owner's and every status's `quantity_on_hand` at the location (physical); open tasks reserve nothing (RQP §5.5). Units Σ on-hand + incoming; weight / volume Σ(on-hand × the item's per-base-unit `weight_gross_kg` / `volume_cc`) + incoming × the item's measure; LPNs = distinct `lpn_id` with on-hand > 0, +1 only when the incoming LPN is non-null and not already there (loose stock adds none); height = the item's `height_cm` against the location's (per-unit clearance). A column the putaway adds nothing to is still judged on its resulting total, so a location already over a limit refuses further putaway. **Missing measure:** an item with no measure contributes nothing to it; when the incoming item has none for a limited column, that column is skipped and the skip is named in the audit line — a refusal is never made from a guessed value. `width_cm` / `depth_cm` and `allows_mixed_*` stay unenforced. **Mode:** `warehouse.putaway.capacity_enforcement` = `BLOCK` (default) or `WARN`, overridden per site by `whb_warehouses.putaway_capacity_enforcement` (NULL = inherit); read once per Complete and **stored** on `wh_putaway_tasks.capacity_enforcement`; an unreadable value is `BLOCK`. `WARN` lets the putaway proceed only with an acknowledgement reason (`capacityOverrideReasonCodeId`, stored with the task); a supplied reason never lets `BLOCK` through. Temperature and owner rules (`receipt-qc-putaway` `RQP-GRD-22`) run first and stay hard under either value. **Concurrency:** Complete takes `pg_advisory_xact_lock(hashtext('wh_putaway_capacity:' || locationId))` before the capacity read, so two Completes into one location serialise; bin moves and other inbound posts into the same bin are not serialised against it (accepted, as `BM-OPEN-01`) | `409 LOCATION_CAPACITY_EXCEEDED` · `actualLocationId`, naming the location and, per breached column, limit, standing, incoming and resulting; under `WARN`: `422 OVERRIDE_REASON_REQUIRED` · `capacityOverrideReasonCodeId` (same breach text), unknown reason `422 PUTAWAY_REASON_INVALID` | columns (`V500013:91-112`); enforced in `WhPutawayTaskService.complete` → `judgeCapacity` / `guardCapacity`, facts `WhPutawayTaskRepositoryCustomImpl.findLocationCapacity`, lock `lockLocationCapacity`, mode `WhPutawaySettings`; `V501238` (site column), `V511423` (setting, task columns) — §10 row 3 (P3-02 #14, 2026-10-25) | FR-086 |
| FBL-GRD-16 | **Owner dedications** (`FBL-T1-12`…`-14`): the location is active (`422 LOCATION_INACTIVE` · `locationId`) and not a provisioned virtual location (`422 LOCATION_PROVISIONED` · `locationId`) — asked by Add **and** by the Add / Edit write-through before it opens a row; at least one owner (`LOCATION_DEDICATION_OWNER_REQUIRED` · `ownerIds`); each owner exists, is active and shares a current company with the site (`LOCATION_OWNER_NOT_FOUND` / `LOCATION_OWNER_INACTIVE` / `LOCATION_OWNER_OTHER_COMPANY`); more than one current owner only under `OWNER_SET` (`422 LOCATION_DEDICATION_NEEDS_OWNER_SET` · `ownerIds`, or · `comminglePolicy` when leaving `OWNER_SET` with several current); the Add / Edit field empty under `OWNER_SET` (`LOCATION_DEDICATION_SCALAR_UNDER_OWNER_SET` · `dedicatedOwnerId`); no overlap with the owner's own history on the location (`LOCATION_DEDICATION_OVERLAP` · `ownerIds`, naming the owner by code); outside `OWNER_SET`, a start not before the latest `effective_to` of **any** owner's dedication on the location (`422 LOCATION_DEDICATION_OVERLAP` · `effectiveFrom`) — one owner at every instant, so a backdated movement is never judged against two. Under `OWNER_SET` several owners may be current; "one owner at every instant" holds from a switch away from `OWNER_SET` onwards, not over the `OWNER_SET` period before it; a start or an end **not in the future** (`422 LOCATION_DEDICATION_IN_FUTURE` · `effectiveFrom` / `effectiveTo`) — so "current" (an open row) and "in force now" are the same rows; End only an open row (`LOCATION_DEDICATION_NOT_CURRENT`), after its start (`LOCATION_DEDICATION_RANGE_INVALID` · `effectiveTo`). **Serialised on the location:** Add, End, the Add / Edit PUT, Retire / Reactivate, Block, Unblock and a count's hold / release (`cycle-count` `CCT-T4-04`, `WhbLocationCountStatusService`: the rows locked in id order so two counts never deadlock, then saved as entities — a column-scoped bulk `UPDATE` was not chosen because it would bypass the per-row audit, FR-427) take the `whb_locations` row `FOR UPDATE` before they read it (every writer of the row, so none saves a stale policy or scalar over another), so two concurrent writes cannot both pass the one-owner rule. A location with dedication history cannot be deleted (`409 REGISTRY_ROW_IN_USE`, through the reference counter); retire it instead | the `EXCLUDE` on `(location_id, owner_id, [from, to))` and the range `CHECK` (`V500070`); FK `RESTRICT` to `whb_locations` and `whb_owners` | FR-087, FR-468, `RG-014` |

### 1.4 Unreachable

| ID | Must never happen | Source |
|---|---|---|
| FBL-UNR-01 | A site visible to a branch-scoped user through no current link (accessories' *unlinked is shared* arm), or a `REGISTERED` link inferred from `is_primary` | FR-079 |
| FBL-UNR-02 | A `WAREHOUSE`- or `DISTRIBUTION_CENTER`-type branch created for a site that is not itself a GST place of business no existing branch carries (`RH-003`) | FR-079 |
| FBL-UNR-03 | An FK from base into a logistics module: a vehicle is a location joined to its asset by `whb_location_external_refs (location_id, source_module, external_id)` | FR-090 |
| FBL-UNR-04 | A cross-company movement posted as a transfer (`FR-305` refuses it from v1) | FR-465 |
| FBL-UNR-05 | An occupancy counter maintained by update; occupancy is derived at read time from active assignments, exclusivity is a partial unique index, released assignments are kept forever | FR-093 |

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from | Source |
|---|---|---|---|---|
| FBL-T2-01 | Change registration | `warehouse:warehouses:change_registration` | any; checker ≠ maker | FR-460 |
| FBL-T2-02 | Block / unblock a location | `whb_locations:block` | Block: `AVAILABLE`; Unblock: `BLOCKED` · `DAMAGED` | FR-091 |
| FBL-T2-03 | Raise / approve / reject a transfer request | `wh_transfer_orders:request` (destination scope) / `:approve` / `:reject` (source scope) | — / `REQUESTED` | FR-462 |
| FBL-T2-04 | Read a location's dedications (`GET /{id}/dedicated-owners`, `GET /{id}/available-dedicated-owners`) | `whb_locations:view`, inside the caller's site tier (`403` outside) | any | FR-087, `RG-014` |
| FBL-T2-05 | Dedicate / end (`POST /{id}/dedicated-owners`, `PATCH /{id}/dedicated-owners/{dedicationId}/end`) and the Add / Edit write-through (`PUT /{id}`) | `whb_locations:edit`, inside the caller's site tier. **Decided 2026-10-24:** dedication maintenance is owner-**master** administration under `whb_locations:edit` alone — the acting user's owner grants (`WhbOwnerScopeResolver`, which scopes stock and grants, `p0-06`) are not consulted, as the v1 Dedicated Owner field never consulted them; owner **eligibility** (`FBL-GRD-16`) is checked on the server | Dedicate and the write-through opening a row: an active location that is not a provisioned virtual one. **End:** any location with an open row, a retired one included | FR-087, `RG-014` |

## 3. T3 — Time-driven rules

| ID | Rule | Clock | Changes | Source |
|---|---|---|---|---|
| FBL-T3-01 | **Classification reads the `REGISTERED` link at the movement's `occurred_at`** (or the document date); **access reads today's links** | `occurred_at` / document date vs `[effective_from, effective_to)`; now | nothing — a read rule | FR-079, FR-460 |
| FBL-T3-02 | Dock appointment times `arrived_at`, `docked_at`, `departed_at`, `no_show` and `detention_minutes` are captured from v1 (schema), screens in v1.1; detention is metered from `arrived_at` | appointment clock | `wh_dock_appointments` (`V510010`) | FR-092 |
| FBL-T3-03 | **Owner dedications are read at the instant being judged:** the port at the movement's `occurred_at`; putaway Complete at its own movement time (the `now` it posts with, `receipt-qc-putaway` `RQP-GRD-22`); the putaway suggestion engine, the hold reach and the WS-017 grid, filter and export at now. **Clock source:** the maintenance bounds (`LOCATION_DEDICATION_IN_FUTURE`, the defaulted `effectiveFrom` / `effectiveTo`) and Complete use the application clock, while the suggestion engine, hold reach, grid, filter and export read the database's `CURRENT_TIMESTAMP`; with app / DB clock skew a just-added row is not yet current to those database reads for the length of the skew — the two agree only under synchronised clocks. Across application nodes the same applies: a defaulted `effectiveFrom = now` on one node can fall before an `effective_to` written by a node whose clock is ahead, so for the length of that skew a legitimate Add with the default start is refused, and the Add / Edit write-through (which does not ask the latest-end rule) can open a row overlapping the last end — node clocks are assumed synchronised | `[effective_from, effective_to)` | nothing — a read rule | FR-087, `RG-014` |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in | Source |
|---|---|---|---|---|
| FBL-T4-01 | A movement or statutory document is classified (GSTIN, branch-scoped series, tax attribution) | it reads the `REGISTERED` branch at `occurred_at`; a non-physical site (`is_physical = false`) still has one, administrative only; in-transit stock sits at a per-transfer location of the source site held by the transfer's frozen source branch | writer (`I-22`), number issuer | FR-079, FR-081, FR-460 |
| FBL-T4-02 | A branch-scoped user reads a warehouse grid | the visible sites are those with a current link whose role grants visibility (`SERVING` links grant visibility and let the branch draw stock; they classify nothing) | `WhbWarehouseScopeService` | FR-079 |
| FBL-T4-03 | A historical transfer is reclassified for a filed period | the site's `state_code` is its own address fact; supply vs non-supply reads the `REGISTERED` link at `occurred_at`, never a scalar on the warehouse | — (no scalar tax identity, `FBL-GRD-06`) | FR-080 |
| FBL-T4-04 | A transfer request is approved | the `TRANSFER` demand order is created; the **demand order reserves** — there is exactly one reservation path | transfer-order service | FR-462 |
| FBL-T4-05 | A request is part-approved or rejected | the refused remainder is recorded as insufficient-stock demand with source `TRANSFER_REQUEST` | transfer-order service → insufficient-stock log | FR-462 |
| FBL-T4-06 | A draw across GSTINs | it is a transfer that is a **taxable supply** (`is_taxable_supply = true`, a challan or invoice, and an e-way bill above the threshold); a same-GSTIN `SERVING` issue is a non-supply challan; a demand order despatched to a third party bills from the site's `REGISTERED` GSTIN at despatch | transfer / despatch services | FR-461 |
| FBL-T4-07 | Custody changes | the old row is ended and a new one opened; "who held the van's stock last Tuesday" is answerable — van stock is a `MOBILE` / `VEHICLE` location, the same object as a delivery vehicle's load | custody service | FR-088 |

## 5. T5 — Screen contract

| ID | Screen | Contract | Source |
|---|---|---|---|
| FBL-T5-01 | WS-016 Warehouses | grid shows the current `REGISTERED` branch and its GSTIN (read through the link), `isPhysical`, `gln`, `stateCode`; a links tab lists the dated history by role; **Change registration** opens a maker–checker modal that shows `WAREHOUSE_REGISTRATION_CHANGE_BLOCKED`'s blocker list inside the modal | FR-079, FR-080, FR-460 |
| FBL-T5-02 | WS-017 Locations | tree by `path` with `locationLevel`, type, status, capacities; Block with reason; custody tab with history | FR-082, FR-086, FR-088, FR-091 |
| FBL-T5-03 | WS-018 Location Generator | preview (count, first, last code) before commit; refusal names the mask token or range | FR-089 |
| FBL-T5-04 | WS-085 / WS-086 Docks | dock doors are locations; appointments show arrived / docked / departed / no-show / detention | FR-092 |
| FBL-T5-05 | WS-090 Transfer Orders | **Raise request** for destination-scoped users; Approve (line `approvedQuantity`) and Reject (reason) for source-scoped users | FR-462 |
| FBL-T5-06 | WS-017 Locations — Dedicated owners | row action **Dedicated owners** shown on `canEdit` — on a retired row too, so an open dedication left by Retire can be ended there; the modal lists the current owners, each with an **End** link, and an Add tab offering only owners eligible for the site and not already current — the Add tab is **disabled** on a retired location (`TabNavigation` `disabled`), so there the modal is End only; a refusal shows inside the modal. The grid column `dedicatedOwnerName`, the `dedicatedOwnerId` filter and the export all read the junction's **current** owners (one grouped query, so grid and export agree), never the scalar. The Add / Edit **Dedicated Owner** field is disabled and sent empty under `OWNER_SET` | FR-087, `RG-014` |

## 6. Out of scope

Transfer legs after approval (depart / in-transit / arrive, `stock-transfer` contract, R30 row 8); e-way bill
lifecycle (India contract); 3PL client GST registrations (WS-169).

## 7. Amendments

| Date | Change |
|---|---|
| 2026-10-23 | v0 derived for R30 `CP-FR-007` row 3; `FR-461` re-homed to `P8-10` per `D-17` item 5 |
| 2026-10-23 | R31: `F-CA-002` (`FBL-T1-06` narrowed, `FBL-T1-06a` Unblock added, `COUNTING`/`FROZEN` pointed at `CCT-T4-04`); `F-CA-005` (Reject is `:reject`; §0 resource list completed); `F-CA-020` (`FBL-GRD-13` code `CROSS_GSTIN_DIRECT_ISSUE`); `FBL-OPEN-01` decided; `FBL-OPEN-02` decided by `D-18` item 5 (`FBL-GRD-14`, §10 row 3) |
| 2026-10-24 | R31 `P1-05` #54 S4 (`RG-014`): `FBL-T1-12`…`-14` (dedicate, End, Add / Edit write-through incl. the end on a switch away from `OWNER_SET`), `FBL-GRD-16` (dedication guards, no future dates, the location row lock, history blocks delete), `FBL-T2-04`, `-05` (`:view` / `:edit`; owner-scope decision: `whb_locations:edit` alone), `FBL-T3-03` (read times), `FBL-T5-06`; §0 primary tables gain `whb_location_owner_dedications` |
| 2026-10-24 | R31 `P1-05` #54 S4b: `FBL-GRD-16` (backdated start outside `OWNER_SET` refused against any owner's latest end; the row lock covers Retire / Reactivate, Block, Unblock); `FBL-T1-13` (End permitted on a retired location); `FBL-T2-05` state column split; `FBL-T3-03` clock-source line |
| 2026-10-24 | R31 `P1-05` #54 S4c: `FBL-T5-06` (row action on retired rows, Add disabled there; the modal lists current owners, no history list); `FBL-GRD-16` (count hold / release take the row lock in id order — the lock, not a bulk UPDATE, for the per-row audit; one owner at every instant from a switch away from `OWNER_SET` onwards); `FBL-T3-03` (app-node clock skew) |
| 2026-10-25 | P3-02 #14 S2 (`D-18` item 5): `FBL-GRD-14` amended — the code is bound to `actualLocationId` (not `toLocationId`), the measurement basis, the missing-measure rule, LPN dedup, the stored mode and the per-location lock stated; §10 row 3 resolved (its evidence was stale) |

## 8. Invariants and scenarios

`D-14`, `I-22`, `I-23`, `FR-408`. Scenarios `WH-SC-045`, `-046`, `-075`, `-185`, `-192`, `-271`…`-274`,
`-312`, `-314`, `-322`.

## 9. Open rows

| ID | Question | Default until decided | Source |
|---|---|---|---|
| FBL-OPEN-01 | `OD-19`: may a registration change move a site between GSTINs while it holds stock, given an adviser ruling? | **DECIDED R31 (2026-10-23): default stands** — refused while the site holds stock, reservations, transfers, counts or open documents; no adviser bypass (`FBL-GRD-04`) | FR-079, FR-460 |
| FBL-OPEN-02 | `FR-086`'s hard-block-vs-warn setting: its key and default are not named in the FRD | **DECIDED `D-18` item 5 (2026-10-23):** key `warehouse.putaway.capacity_enforcement`, default `BLOCK` wherever a capacity is set, per-site `WARN` with an acknowledgement reason (`FBL-GRD-14`); the reviewer default, stated to the user | FR-086 |

## 10. Code divergences (for the build to fix)

| # | File:line | FR | What differs |
|---|---|---|---|
| 1 | `warehouse/backend` (no `CROSS_GSTIN_DIRECT_ISSUE` anywhere; no store-issue service yet) | FR-461 | The serving-branch refusal is not built; `P8-10` (store issue, the first stock-consuming document) owns it, under the neutral code `CROSS_GSTIN_DIRECT_ISSUE` — **Triage 2026-10-23: CARRIED** — `P8-10` #571 (store issue) |
| 2 | `warehouse/backend/.../db/migration/` (no inter-company action) | FR-465 | Inter-company demand order + PO in one action is not built (v2, `P1-17`) — **Triage 2026-10-23: FIX-CODE** — owner `P1-17` #133 (v2), reopened |
| 3 | `warehouse/backend/src/main/java/ai/warehouse/service/whputawayrule/WhPutawayRuleEngine.java:126` (capacity advisory, suggestion only); no `warehouse.putaway.capacity_enforcement` key | FR-086 | Capacity enforcement at putaway completion (`D-18` item 5: `BLOCK` default, per-site `WARN`) is not built; `P3-02` owns it (plan §8.2) — **Triage 2026-10-23: FIX-CODE** — owner `P3-02` #14, reopened — **Evidence was stale:** Complete already hard-blocked `max_units` (`WhPutawayTaskService.guardCapacity`, refusal code `LOCATION_POLICY_VIOLATED`); line 126 is the suggestion engine's advisory comment. **RESOLVED 2026-10-25 (P3-02 #14 S2):** all five FBL-GRD-14 columns judged at Complete, BLOCK/WARN with per-site override, `LOCATION_CAPACITY_EXCEEDED`, per-location advisory lock. The suggestion engine still accounts for `max_units` only (RQP §5.5 follow-up) |
