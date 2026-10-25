# Functional Contract — Status stores: quarantine, rejected, scrap and sample as stock statuses with optional dedicated locations shown as stores

> **What this is.** The functional truth for `D-20` item 2 **KEEP #16**: non-allocatable stock statuses
> (`QC_HOLD`, `QUARANTINE`, `MRN_PENDING`, `REJECTED`, `DAMAGED`, a sibling's sample status) stay the control
> for availability, and a site may additionally bind each status to a dedicated location so that every
> status change also **moves** the stock there, and reports show those locations as the plant's *Quarantine
> Store*, *Rejected Store*, *Scrap Store*, *Sample Store*. It touches the posting paths of
> [`receipt-qc-putaway.contract.md`](receipt-qc-putaway.contract.md), [`mrn-authorisation.contract.md`](mrn-authorisation.contract.md)
> and [`store-issue-return.contract.md`](store-issue-return.contract.md) without changing their status rules.
>
> **Status.** Derived 2026-10-25 (v0) from [`frd/FRD-STORES.md`](../frd/FRD-STORES.md) §6.9 (`FR-703`). Not ratified. **No code exists.**

---

## 0. Identity

| | |
|---|---|
| **Workflow** | Configure status → location per site → any posting that sets a bound status relocates in the same movement → reports group by store |
| **Module** | `warehouse` |
| **Owning task** | `issues/p8-22.md` |
| **Primary table** | `wh_status_store_locations` (`V511504`) |
| **Permission resources** | `wh_status_store_locations:{view,view:all,view:branch,create,edit,move_existing,export}` (`:move_existing` → `:view`, R32-fix F-R32CQ-034) |
| **Settings** | `warehouse.stores.status_store_mode` per site — `STATUS_ONLY` (default, today's behaviour) · `DEDICATED_LOCATIONS` |
| **Routes** | WS-697 `/warehouse/stores/status-stores` · WS-208 (store grouping) · **mobile: none** |
| **Contract version** | `v0 — 2026-10-25` |

### Acceptance checks

| # | Expects | Delivered by |
|---|---|---|
| A1 | A reject lands in the Rejected Store in one movement and the report shows it as a store (`WH-SC-732`) | `SST-T1-01`, `SST-T5-02` |
| A2 | Stock cannot be moved into or out of a status store without the matching status (`WH-SC-732`) | `SST-GRD-03`, `-04` |
| A3 | `STATUS_ONLY` changes nothing | `SST-T1-02` |

---

## 1. T1 — State machine

| ID | From | Event | To | Guard | Actor | Side effects | Source |
|---|---|---|---|---|---|---|---|
| SST-T1-01 | stock in status A at location L | a posting (GRN receipt into `QC_HOLD` / `QUARANTINE` / `MRN_PENDING`, disposition `REJECT` / `RTV` into a bound status, store-return condition `NEEDS_INSPECTION` / `DAMAGED` / `SCRAP`, a QC release into `MRN_PENDING`) sets a non-allocatable status B with an active `move_on_status_change` row for (site, B, the item's DG class or none) under `DEDICATED_LOCATIONS` | status B at the row's location | `SST-GRD-01`, `-02`, `-05` | the posting's actor | **one** balanced movement carries the status change and the location leg (`L-1`). A QC `SCRAP` disposition is **not** a trigger: it is a write-off to the virtual `SCRAP` location (`WhQualityInspectionDispositionService.java:225-251`); the *Scrap Store* is the `DAMAGED` row (R32-fix F-R32CQ-014) | FR-703 |
| SST-T1-02 | as above | same posting under `STATUS_ONLY`, or no row for B | status B at L | — | — | today's behaviour exactly | FR-703 |
| SST-T1-03 | — | Create / edit / deactivate a status-store row | active / inactive | `SST-GRD-01`, `-02` | `wh_status_store_locations:create/edit` | — | FR-703 |
| SST-T1-04 | mode switched on | **Move existing** — `GET /warehouse/stores/status-stores/misplaced?warehouseId` lists stock already in a bound status outside its store; `POST /warehouse/stores/status-stores/move-existing` (selected rows) posts one user-confirmed transfer per row into the bound location (R32-fix F-R32CQ-034) | relocated | `SST-GRD-03`, `-04`, `-05` | `wh_status_store_locations:move_existing` | never automatic; WS-697 toolbar action *Move existing stock* (shown only under `DEDICATED_LOCATIONS`) | FR-703 |
| SST-T1-05 | stock in bound status B at its status-store location | a posting changes it to a status C that has no row (MRN authorise `MRN_PENDING → AVAILABLE`, QC release `QC_HOLD → AVAILABLE` / `MRN_PENDING` without a row, a re-test accept) | status C at the **receiving staging location** of the line (the GRN line's receiving location, else the site's default receiving location) | — | the posting's actor | the leaving `STATUS_CHANGE` carries its own location leg out of the store in the same movement (`L-1`, no second document); the putaway task (`RQP-T1-24`) then starts from staging, so allocatable stock never sits in a status store (R32-fix F-R32CQ-009; `MRA-T4-02` amended); into another bound status → that row's location (`SST-T1-01`) | FR-703 |

### 1.3 Guards

| ID | Predicate | Refusal | Backstop | Source |
|---|---|---|---|---|
| SST-GRD-01 | the bound status is non-allocatable (`whb_stock_statuses.is_allocatable = false`) | `422 STATUS_STORE_STATUS_ALLOCATABLE` | service | FR-703 |
| SST-GRD-02 | the location is on the same site and is a non-virtual storage location; one active row per (site, status, DG class or none); **a location is bound to at most one status** — a plant's single "Quarantine Store" holding `QC_HOLD` and `MRN_PENDING` is modelled as one zone with a child bin per status (R32-fix F-R32CQ-021); a row with `dg_class_code` needs an `is_dg_store` location permitting that class (`RQP-GRD-46`) | `422 STATUS_STORE_LOCATION_OTHER_SITE` · `422 STATUS_STORE_LOCATION_VIRTUAL` · `409 STATUS_STORE_DUPLICATE` · `409 STATUS_STORE_LOCATION_TAKEN` · `422 PUTAWAY_DG_LOCATION_NOT_APPROVED` | partial uk `(warehouse_id, stock_status_code, COALESCE(dg_class_code, '')) WHERE is_active`; partial uk `(location_id) WHERE is_active` | FR-703 |
| SST-GRD-03 | **every movement** into a status-store location (transfer, putaway, replenishment, pick return, `SST-T1-04`) carries stock already in that store's status; putaway and replenishment **suggestions** never propose a status-store location for stock in another status (R32-fix F-R32CQ-021) | `409 STATUS_STORE_STATUS_MISMATCH` | `WhbMovementPostGuard` writer check (all movement types) | FR-703 |
| SST-GRD-04 | stock **still in the store's bound status** leaves a status store by a movement that keeps the status only into another location bound to the same status; otherwise the status change document must move it (`SST-T1-05`). Stock at a status-store location in another status (pre-mode stock, an edge case) moves freely (R32-fix F-R32CQ-009) | `409 STATUS_STORE_TRANSFER_REQUIRES_STATUS_CHANGE` | writer check | FR-703 |
| SST-GRD-05 | a dangerous-goods item relocates only into a status store whose location permits its class: the (site, status, item's DG class) row is used, else the class-less row if its location permits the class (`RQP-GRD-46`); when neither does, the status changes **in place** (`SST-T1-02` path) and the posting returns the warning `STATUS_STORE_DG_NOT_PERMITTED` — a reject is never refused for segregation (R32-fix F-R32CQ-022) | warning only | writer check | FR-703 FR-711 |

### 1.4 Unreachable

| ID | Must never happen | Source |
|---|---|---|
| SST-UNR-01 | availability, reservation, MRN routing or issuability decided by a location rather than the status | FR-703 |
| SST-UNR-02 | a second movement document for the relocation of a status change | FR-703 |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in | Source |
|---|---|---|---|---|
| SST-T4-01 | a status-store row is active | putaway / move labels for stock at its location print `store_label` and the status (`P8-12`) | print data contract | FR-703 |
| SST-T4-02 | a `SAMPLE_IN` receipt (`GTE-T4-07`) on a core-only install | core seeds **no** sample status: the line takes the resolved receiving status (`QC_HOLD` when a plan resolves, else `AVAILABLE`/`MRN_PENDING` as today) and its store is the one bound to that status. A sibling that seeds a non-allocatable sample status (MFG `P10`) also owns its exit — a `STATUS_CHANGE` with its own reason, which `SST-T1-05` relocates (R32-fix F-R32CQ-035) | receiving service | FR-703 FR-712 |

## 5. T5 — Screen contract

| ID | Screen | Contract | Source |
|---|---|---|---|
| SST-T5-01 | WS-697 Status Stores (reference **Department**) | grid `wh_status_store_locations` · scope `WAREHOUSE_STATUS_STORE` · sort `e.warehouse_id, e.stock_status_code`; columns `siteName`, `stockStatus`, `dgClass`, `locationCode`, `storeLabel`, `moveOnStatusChange`, `isActive`, audit; filters `warehouseId`, `stockStatus`, `isActive`; toolbar *Move existing stock* (`SST-T1-04`, `:move_existing`) | FR-703 |
| SST-T5-02 | WS-208 Stock on hand; WS-277 / WS-696 registers | `storeLabel` column and `groupByStore` toggle: a status store's label for stock at its location, else the zone / store as today; *Quarantine stock* = `QC_HOLD` + `QUARANTINE` + `MRN_PENDING` rows; *Scrap Store* = the `DAMAGED` row's label (QC-scrapped stock is written off, never stored) | FR-703 |

## 6. Out of scope

Separate legal stores (godowns) per status, a status-specific owner, mobile.

## 7. Amendments

| Date | Change |
|---|---|
| 2026-10-25 | v0 derived (R32, `D-20` item 2 KEEP #16): status model kept; optional dedicated locations shown as stores (`P8-22`) |
| 2026-10-25 | **R32-fix** (`R32-functional-review-core-quality.md`). Leaving a status store carries its own location leg to receiving staging, `SST-GRD-04` scoped to bound-status stock (`SST-T1-05`; F-R32CQ-009; `MRA-T4-02` amended); QC `SCRAP` removed from the triggers, Scrap Store = `DAMAGED` (`SST-T1-01`, `SST-T5-02`; F-014); the guard covers every movement and suggestion, one status per location (`SST-GRD-02`, `-03`; F-021); DG items use a per-class row or change in place (`SST-GRD-05`; F-022); *Move existing* verb, endpoints, action (`SST-T1-04`; F-034); sample status on a core-only install (`SST-T4-02`; F-035) |

## 8. Invariants and scenarios

`L-1`; scenario `WH-SC-732`.
