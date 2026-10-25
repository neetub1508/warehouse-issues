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
| **Permission resources** | `wh_status_store_locations:{view,view:all,view:branch,create,edit,export}` |
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
| SST-T1-01 | stock in status A at location L | a posting (GRN receipt into `QC_HOLD`, disposition `REJECT`/`SCRAP`, store-return condition, MRN authorise) sets status B with an active `move_on_status_change` row for (site, B) under `DEDICATED_LOCATIONS` | status B at the row's location | `SST-GRD-01`, `-02` | the posting's actor | **one** balanced movement carries the status change and the location leg (`L-1`); leaving a status store (B → allocatable) hands over to putaway (`P1-15`) | FR-703 |
| SST-T1-02 | as above | same posting under `STATUS_ONLY`, or no row for B | status B at L | — | — | today's behaviour exactly | FR-703 |
| SST-T1-03 | — | Create / edit / deactivate a status-store row | active / inactive | `SST-GRD-01`, `-02` | `wh_status_store_locations:create/edit` | — | FR-703 |
| SST-T1-04 | mode switched on | **Move existing** (lists stock already in a bound status elsewhere) | relocated by user-confirmed transfers | `SST-GRD-04` | stores | never automatic | FR-703 |

### 1.3 Guards

| ID | Predicate | Refusal | Backstop | Source |
|---|---|---|---|---|
| SST-GRD-01 | the bound status is non-allocatable (`whb_stock_statuses.is_allocatable = false`) | `422 STATUS_STORE_STATUS_ALLOCATABLE` | service | FR-703 |
| SST-GRD-02 | the location is on the same site and is a non-virtual storage location; one active row per (site, status) | `422 STATUS_STORE_LOCATION_OTHER_SITE` · `422 STATUS_STORE_LOCATION_VIRTUAL` · `409 STATUS_STORE_DUPLICATE` | partial uk `(warehouse_id, stock_status_code) WHERE is_active` | FR-703 |
| SST-GRD-03 | a manual transfer **into** a status store moves only stock already in that store's status | `409 STATUS_STORE_STATUS_MISMATCH` | writer check | FR-703 |
| SST-GRD-04 | a manual transfer **out of** a status store keeps the status only into another location bound to the same status; otherwise the status change document must move it | `409 STATUS_STORE_TRANSFER_REQUIRES_STATUS_CHANGE` | writer check | FR-703 |

### 1.4 Unreachable

| ID | Must never happen | Source |
|---|---|---|
| SST-UNR-01 | availability, reservation, MRN routing or issuability decided by a location rather than the status | FR-703 |
| SST-UNR-02 | a second movement document for the relocation of a status change | FR-703 |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in | Source |
|---|---|---|---|---|
| SST-T4-01 | a status-store row is active | putaway / move labels for stock at its location print `store_label` and the status (`P8-12`) | print data contract | FR-703 |

## 5. T5 — Screen contract

| ID | Screen | Contract | Source |
|---|---|---|---|
| SST-T5-01 | WS-697 Status Stores (reference **Department**) | grid `wh_status_store_locations` · scope `WAREHOUSE_STATUS_STORE` · sort `e.warehouse_id, e.stock_status_code`; columns `siteName`, `stockStatus`, `locationCode`, `storeLabel`, `moveOnStatusChange`, `isActive`, audit; filters `warehouseId`, `stockStatus`, `isActive` | FR-703 |
| SST-T5-02 | WS-208 Stock on hand; WS-277 / WS-696 registers | `storeLabel` column and `groupByStore` toggle: a status store's label for stock at its location, else the zone / store as today; *Quarantine stock* = `QC_HOLD` + `QUARANTINE` + `MRN_PENDING` rows | FR-703 |

## 6. Out of scope

Separate legal stores (godowns) per status, a status-specific owner, mobile.

## 7. Amendments

| Date | Change |
|---|---|
| 2026-10-25 | v0 derived (R32, `D-20` item 2 KEEP #16): status model kept; optional dedicated locations shown as stores (`P8-22`) |

## 8. Invariants and scenarios

`L-1`; scenario `WH-SC-732`.
