# Functional Contract — Store issue to consumption with a cost object, and store return

> **What this is.** The functional truth for taking stock out of a store into consumption — a store
> issue posting `ISSUE` to `VIRT-CONSUMED-<site>` with a **cost object on every line** — and for bringing
> unused material back — a store return linked to the issue line, partial, with condition and QC. It
> also owns the **cost-object resolver** seam and the thin **cost-centre master**. It resolves `S-052`
> per `RN-034`.
>
> **Status.** Derived 2026-10-22 (v0) from [`frd/FRD-STORES.md`](../frd/FRD-STORES.md) `FR-533`…`FR-537`,
> `STO-D10`, `STO-D11`. Not ratified.

---

## 0. Identity

| | |
|---|---|
| **Workflow** | Issue: create (from requisition lines or direct) → pick lines (location, lot, serial) → post → acknowledged. Return: create from an issue line → submit (department) → post (stores) / reject; condition decides status and QC |
| **Module** | `warehouse`; base seeds: `COST_OBJECT_TYPE` (`V501233`, `P8-09`), `RETURN_CONDITION` (`V501230`, `P8-03`), document type `STORE_ISSUE` (`V501234`, `P8-10`), movement type `ISSUE_RETURN` + reason context `STORE_RETURN` + document type `STORE_RETURN` (`V501235`, `P8-11`) |
| **Domain baseline** | `L-1`, `L-2`, `FR-436` (single writer), `P0-17` cost layers, `S-052` / `RN-034`, `FR-533`…`FR-537`, `STO-D10`, `STO-D11` · `movement-post-reverse.contract.md` `MPR-T1-01` · `whb_movement_types` `ISSUE` (`V500003:212`) · `VIRT-CONSUMED-<site>` (`V500013:37`, provisioned by `WhbVirtualLocationProvisioner`) |
| **Owning tasks** | `issues/p8-09.md` (cost-object seam, cost centres — shared with requisitions) · `issues/p8-10.md` (store issue) · `issues/p8-11.md` (store return) |
| **Primary tables** | `wh_cost_centres` (`V511318`); `wh_store_issues`, `wh_store_issue_lines`, `wh_store_issue_line_serials` (`V511319`); `wh_store_returns`, `wh_store_return_lines`, `wh_store_return_line_serials` (`V511320`) |
| **Permission resources** | `wh_cost_centres:{view,view:all,view:branch,create,edit,export}` · `wh_store_issues:{view,view:all,view:branch,view_all_departments,create,edit,post,cancel,export,issue_without_requisition}` · `wh_store_returns:{view,view:all,view:branch,view_all_departments,create,edit,submit,post,reject,cancel,export}` (`V511408`, `V511409`, `V511410`). `:view:all`/`:view:branch` = the warehouse **site** scope pair (`V511000:60-71`); `:view_all_departments` = the **department** axis (own departments without it, `MRQ-GRD-04` shape) — R29 F1 |
| **Routes** | WS-270 `/warehouse/stores/issues` + WS-271 `/[id]` · WS-272 `/warehouse/stores/returns` · WS-273 `/warehouse/stores/cost-centres` · WS-277 registers |
| **Contract version** | `v0 — 2026-10-22` |

### Acceptance checks

| # | Expects | Delivered by |
|---|---|---|
| A1 | An issue posts to `VIRT-CONSUMED` and carries the cost object on its lines, not on the ledger (`WH-SC-463`) | `SIR-T4-01`, `SIR-UNR-01` |
| A2 | An issue never exceeds what was approved (`WH-SC-465`) | `SIR-GRD-02` |
| A3 | Cost-object types are pluggable; MFG's `PRODUCTION_ORDER` only when MFG is on (`WH-SC-464`) | `SIR-GRD-01` |
| A4 | A posted issue is immutable (`WH-SC-472`) | `SIR-UNR-02` |
| A5 | A return names the issue line, is partial, is valued at the issue cost, and its condition decides status/QC (`WH-SC-467`…`-470`) | `SIR-T1-05`…`-09`, `SIR-T4-03` |
| A6 | Consumption by cost object is reportable (`WH-SC-471`) | §5.4 |

---

## 1. T1 — State machine

### 1.1 Status inventory

| Entity | Status | Represented by | Reachable via | Exits via | Kind |
|---|---|---|---|---|---|
| Store issue | `DRAFT` | `status` | `SIR-T1-01` | `-03`, `-04` | initial |
| Store issue | `POSTED` | `status`; `issue_movement_id`, `posted_by/at` | `SIR-T1-03` | none | **terminal** |
| Store issue | `CANCELLED` | `status`; reason | `SIR-T1-04` | none | **terminal** |
| Store return | `DRAFT` | `status` | `SIR-T1-05` | `-06`, `-09` | initial |
| Store return | `SUBMITTED` | `status`; `submitted_by/at` | `SIR-T1-06` | `-07`, `-08`, `-09` | active |
| Store return | `POSTED` | `status`; `return_movement_id`, `received_by/at` | `SIR-T1-07` | none | **terminal** |
| Store return | `REJECTED` | `status`; reason | `SIR-T1-08` | none | **terminal** |
| Store return | `CANCELLED` | `status`; reason | `SIR-T1-09` | none | **terminal** |
| Cost centre | active / inactive | registry convention | — | — | master |

### 1.2 Transitions

| ID | From | Event | To | Guard | Actor | Side effects | Reason? | UI |
|---|---|---|---|---|---|---|---|---|
| SIR-T1-01 | — | Create issue: site, requisition (optional), department, issued-to user / name, lines (requisition line, item, quantity, UoM, location, lot, serials, status `AVAILABLE`, cost object — defaulted from the requisition line → header) | `DRAFT` | `SIR-GRD-01`…`-05` | `wh_store_issues:create` (+ `:issue_without_requisition` when no requisition) | gapless `SIS` number at create; **suggested pick** per line (FEFO for expiry-managed, else FIFO by lot receipt date) from `GET /stores/issues/pick-suggestion` — a proposal | no | WS-274 **Issue selected**; WS-268 **Issue**; WS-270 **Add** |
| SIR-T1-02 | `DRAFT` | Edit lines | unchanged | same | `:edit` | — | no | WS-271 |
| SIR-T1-03 | `DRAFT` | **Post** | `POSTED` | `SIR-GRD-01`…`-06` re-checked under lock, then `MPR-T1-01`'s guards | `wh_store_issues:post` | `SIR-T4-01`, `-02` in one transaction; `acknowledged_by_name` / `acknowledged_at` captured in the post modal | no | WS-271 **Post** |
| SIR-T1-04 | `DRAFT` | Cancel | `CANCELLED` | — | `:cancel` | number stays issued | **yes** | WS-271 **Cancel** |
| SIR-T1-05 | — | Create return: issue line(s), quantity, condition, reason, return location (default the site's `RETURNS` staging or the issue location) | `DRAFT` | `SIR-GRD-07`…`-09` | `wh_store_returns:create` | gapless `SRN`; cost object, unit cost and lot **copied from the issue line** (read-only) | no | WS-271 **Return**; WS-272 **Add** (pick a posted issue) |
| SIR-T1-06 | `DRAFT` | Submit (department hands over) | `SUBMITTED` | — | `:submit` | — | no | WS-272 **Submit** |
| SIR-T1-07 | `SUBMITTED` | **Post** (stores has the material) | `POSTED` | `SIR-GRD-07`…`-10` re-checked; receiver ≠ submitter, else `403 STORE_RETURN_SELF_APPROVAL` (R29 F26) | `:post` | `SIR-T4-03`…`-06` in one transaction | no | WS-272 **Post** |
| SIR-T1-08 | `SUBMITTED` | Reject (not received / not as declared) | `REJECTED` | — | `:reject` | nothing posted | **yes** | WS-272 **Reject** |
| SIR-T1-09 | `DRAFT` · `SUBMITTED` | Cancel | `CANCELLED` | actor is the creator or holds `:reject` | `:cancel` | — | **yes** | WS-272 **Cancel** |

### 1.3 Guards

| ID | Predicate | Refusal | Backstop | Source |
|---|---|---|---|---|
| SIR-GRD-01 | each line's cost object: type active in `COST_OBJECT_TYPE` **and** a `CostObjectResolver` registered **and** the id valid (core: `DEPARTMENT` → `departments` active (no company column on `departments`, so no company check, R29 F33); `COST_CENTRE` → `wh_cost_centres` active, same company; `WORK_ORDER` → `wh_work_orders` `RELEASED`/`IN_PROGRESS`; `MACHINE`/`PROJECT` → `wh_cost_centres` rows of that kind until an owner exists (core registers all five resolvers, `FR-533`, R29 F34); MFG: `PRODUCTION_ORDER` released) ; never null | `422 COST_OBJECT_TYPE_UNSUPPORTED` / `422 COST_OBJECT_INVALID` / `422 COST_OBJECT_REQUIRED` · `lines[i].costObjectId` | `cost_object_type`, `cost_object_id`, `cost_object_ref` NOT NULL; composite FK to the code list | FR-533 |
| SIR-GRD-01a | the resolver's `assertIssuable(costObjectId, itemId, baseQty)` holds (MFG: order `RELEASED`/`IN_PROGRESS`/`COMPLETED`-not-settled, not on hold, no settlement awaiting approval, item on the order under `STRICT` — *amended for MFG MD-14*) | the resolver's own `422`/`409` code, field `lines[i]` | — | FR-533 (SEAM-M2) |
| SIR-GRD-02 | with a requisition line (R29 F17): the line belongs to **the requisition named on the issue header**; requisition `APPROVED`/`PARTIALLY_ISSUED`, same site; **the issue line's item equals the requisition line's item**; the UoM may differ only through the item's conversion, and quantities are compared in **base units** (`conversion_factor_used` on both lines): Σ this issue's lines for it ≤ approved − issued − closed | `422 ISSUE_LINE_NOT_ON_REQUISITION` / `422 ISSUE_ITEM_MISMATCH` · `lines[i].itemId` / `422 ISSUE_EXCEEDS_APPROVED` · `lines[i].quantity` | CHECK on the requisition line (`MRQ-GRD-07`) | FR-535 |
| SIR-GRD-03 | without a requisition: `warehouse.stores.direct_issue_allowed = true` and the actor holds `:issue_without_requisition` | `403 DIRECT_ISSUE_NOT_ALLOWED` | — | FR-535 |
| SIR-GRD-04 | the location is stock-holding at the site; status is allocatable; lot not expired / on hold (`P2-05`); serial captured when the item is serialised | `422 ISSUE_LOCATION_INVALID` / `422 STOCK_STATUS_NOT_ISSUABLE` / `422 LOT_NOT_ISSUABLE` / `422 SERIAL_REQUIRED` | ledger guards | FR-535 |
| SIR-GRD-05 | the item is stock-holding (not `SERVICE`/`NON_STOCK`) | `422 ITEM_NOT_ISSUABLE` | — | FR-535 |
| SIR-GRD-06 | on-hand at the grain ≥ quantity unless the negative-stock policy allows (`V500031`) | the writer's refusal (`MPR`) | ledger | L-1 |
| SIR-GRD-07 | the issue is `POSTED`; Σ live return lines (not `REJECTED`/`CANCELLED`) for the issue line + this ≤ issued | `422 STORE_RETURN_EXCEEDS_ISSUED` · `lines[i].quantity` naming the remaining quantity | CHECK `returned_quantity <= quantity` on `wh_store_issue_lines` | FR-536 |
| SIR-GRD-08 | return lot/serial ⊆ the issue line's | `422 STORE_RETURN_LOT_MISMATCH` | — | FR-536 |
| SIR-GRD-09 | condition active in `RETURN_CONDITION`; reason in context `STORE_RETURN` | `422` field-named | composite FK; FK `whb_reason_codes` | FR-536 |
| SIR-GRD-10 | `warehouse.stores.return_window_days` > 0 ⇒ issue `posted_at` within the window | `409 STORE_RETURN_WINDOW_EXPIRED` | — | FR-536 |

### 1.4 Unreachable

| ID | Must never happen |
|---|---|
| SIR-UNR-01 | a cost-object column on `whb_stock_movements` / `_lines` (`RN-034`) |
| SIR-UNR-02 | an edit, delete or reversal of a `POSTED` store issue (`STO-D11`) — `PUT` answers `409 STORE_ISSUE_POSTED_IMMUTABLE` |
| SIR-UNR-03 | a store return changing its cost object or unit cost |
| SIR-UNR-04 | a store issue routed through `wh_demand_orders` (the despatch path relieves `SCRAP`/`SAMPLE`/`WORK_ORDER` demand to `VIRT-CUSTOMER`, `WhDespatchService.reliefPurpose` `:312-319` — wrong for consumption) |
| SIR-UNR-06 | an `onIssueReversed` hook firing — no issue-reversal path exists (`STO-D11`, `STO-D13`; MFG's proposed hook is rejected) |
| SIR-UNR-05 | a store return booking against `VIRT-CUSTOMER` (`WhReturnReceiptPostingService` is customer-only) |

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from | Extra | Source |
|---|---|---|---|---|---|
| SIR-T2-01 | Create / edit issue | `wh_store_issues:create`/`:edit` | — / `DRAFT` | stores issue clerk | — |
| SIR-T2-02 | Post issue | `:post` | `DRAFT` | — | — |
| SIR-T2-03 | Cancel issue | `:cancel` | `DRAFT` | reason | — |
| SIR-T2-04 | Create / submit return | `wh_store_returns:create`/`:submit` | — / `DRAFT` | department requester (own departments) | — |
| SIR-T2-05 | Post / reject return | `:post` / `:reject` | `SUBMITTED` | stores; ≠ submitter | — |
| SIR-T2-06 | Cost centres | `wh_cost_centres:*` | — | admin | — |
| SIR-T2-07 | Print issue slip / return note | `wh_print_jobs:create` | `POSTED` (issue), `SUBMITTED`/`POSTED` (return) | `SYS-STORE-ISSUE`, `SYS-STORE-RETURN` | FR-538 |

## 3. T3 — Time-driven rules

| ID | Rule | Trigger | Changes | Notified | Job | Once? |
|---|---|---|---|---|---|---|
| SIR-T3-01 | Draft issue ageing | `DRAFT` > 24 h | nothing — tile; the draft holds no stock (reservation stays on the requisition) | creator | daily | once |
| SIR-T3-02 | Submitted return not received | `SUBMITTED` > `warehouse.stores.return_receive_alert_hours` (default 24) | nothing | stores in-charge | daily | once |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in | Source |
|---|---|---|---|---|
| SIR-T4-01 | issue post | **one** `ISSUE` movement (`WhbStockLedgerWriter.post`, `WhbMovementPostCommand`: `sourceSystem = WAREHOUSE`, `sourceDocumentType = STORE_ISSUE`, `sourceDocumentId` = issue id, `sourceDocumentNo` = `SIS` number, `idempotencyKey = STORE_ISSUE:<id>`, `consumedReservationIds` = the line's requisition holds at the issued grain, or — when the line's resolver `ownsReservations()` — the cost object's own holds from `reservationsFor(costObjectId, itemId)`, *amended for MFG MD-16*; the holds are then **consumed and split in the same transaction** by `MRQ-T4-02` — passing the ids alone only exempts them from the availability check, R29 F4) with, per issue line, −qty at the location (status `AVAILABLE`, lot, serial) and +qty at `VIRT-<counterLocationPurpose>-<site>` (the resolver's purpose: `CONSUMED` by default, `PRODUCTION` for MFG's `PRODUCTION_ORDER` — SEAM-M1); the purpose used is stored on the issue line (`counter_location_purpose`); before the post each line's resolver `assertIssuable` runs, and after the writer call `onIssuePosted(line)` runs in the same transaction (SEAM-M2); valued by the item's cost method; `issue_movement_id` on the header, `unit_cost` per line read back from the movement line | issue service → writer · `STO-D18` (R30 `CP-FR-014`) | STO-D18 |
| SIR-T4-02 | issue post | requisition `MRQ-T4-02`; outbox `store_issue.posted` carrying each line's cost object and value (accounting handover) | issue service | — |
| SIR-T4-03 | return post | one **`ISSUE_RETURN`** movement (new type: direction `IN`, `cost_basis_default = ACTUAL`, `requires_reason = true`, **`reversal_type_code = NULL`** — a posted store return is never reversed, mirroring `STO-D11`: a return posted in error is corrected by a new store issue against the same requisition line. Pointing it at `ISSUE` would make its reversal a bare, itself-reversible `ISSUE` with no store issue behind it, against L-3 and the `V500003:71-73` convention (R31 F-SR-008)): −qty at the issue line's stored `counter_location_purpose` location (`VIRT-CONSUMED` or `VIRT-PRODUCTION`), +qty at the return location, **unit cost = the issue line's `unit_cost`**; then the resolver's `onReturnPosted(line)` in the same transaction (SEAM-M2), status by condition (`GOOD` → `AVAILABLE`, `NEEDS_INSPECTION` → `QC_HOLD`, `DAMAGED`/`SCRAP` → `DAMAGED`), `sourceDocumentType = STORE_RETURN` | return service → writer | FR-537 |
| SIR-T4-04 | return post, `GOOD` | a putaway task per line (`RQP-T1-24` rule) | putaway service | — |
| SIR-T4-05 | return post, `NEEDS_INSPECTION` | an inspection of `source_type = STORE_RETURN` is started (`IIS-T1-07`), stage `RETURN` | inspection service | — |
| SIR-T4-06 | return post | issue line `returned_quantity` +=; requisition line `returned_quantity` += (`MRQ-T4-04`); outbox `store_return.posted` with the inherited cost object | return service, same transaction | — |
| SIR-T4-07 | return post, `SCRAP` | stock lands `DAMAGED`; a `SCRAP` disposition is then an ordinary scrap movement (`requires_approval`) — not automatic | — (stated) | — |

## 5. T5 — Screen contract

### 5.1 WS-270 Store Issues / WS-271 detail (reference: **Service Vehicle**)

| | |
|---|---|
| **Grid** | `wh_store_issues` · scope `WAREHOUSE_STORE_ISSUE` · sort `e.created_at DESC` |
| **Tiles** | `DRAFT` · `POSTED` today · value issued today (view-cost) · *Direct issues* |
| **Columns** | `issueNumber`, `warehouseName`, `requisitionNumber`, `departmentName`, `costObjectSummary` (one type/ref, or *mixed*), `issuedToName`, `lineCount`, `quantity`, `value`, `status`, `postedByName`, `postedAt`, `acknowledgedByName`, audit |
| **Filters** | `warehouseId`; `departmentId`; `costObjectType` → `costObjectId`; `status`; `requisitionNumber` (text); `itemId`; `postedFrom/To` (date); `directOnly` |
| **Row actions** | View · Edit · Post · Cancel · Return · Print |
| **Detail** | lines (`item`, `lot`, `serials`, `location`, `quantity`, `uom`, `unitCost`, `value`, `costObjectType`, `costObjectRef`, `returnedQuantity`); returns tab |
| **Export** | grid + lines sheet + `createdByName`, `updatedByName` |

### 5.2 WS-272 Store Returns

Grid `wh_store_returns` · scope `WAREHOUSE_STORE_RETURN` · columns `returnNumber`, `warehouseName`, `issueNumber`, `departmentName`, `costObjectRef`, `lineCount`, `quantity`, `value`, `condition` (or *mixed*), `status`, `submittedByName`, `receivedByName`, `postedAt`, audit; filters site, department, status, condition, issue number, date range; actions View · Submit · Post · Reject · Cancel · Print; export superset + audit names.

### 5.3 WS-273 Cost Centres (reference: **Department**)

Grid `wh_cost_centres` · scope `WAREHOUSE_COST_CENTRE` · sort `e.code ASC` · columns `code`, `name`, `kind` (`COST_CENTRE`/`MACHINE`/`PROJECT`), `departmentName`, `parentName`, `externalRef`, `isActive`, audit; filters `search`, `kind`, `departmentId`, `isActive`; uniqueness validation on code (`/validate/code`, upper-cased); deactivate refused while a `DRAFT` issue or an open requisition references it (`409 COST_CENTRE_IN_USE`). **R30 `CP-SC-006`:** row actions View (gray) · Edit (primary, only when `canEdit && isActive`) · Deactivate (warning) / Activate (success); Add + Export (superset + audit names) + Import none in v1.1; `default_columns` = the columns above less audit, `default_filters` = `search`, `kind`, `isActive` (`STO-D22`); statistics tiles: total, active, by kind (3), as on Department.

### 5.4 WS-277 Stores Registers

Tabs, each a backend-paginated grid with export and filter-aware tiles (no cache name): **RGP pending/overdue** (from `GTE`), **Requisitions pending issue** (WS-274 data), **Issue register by cost object** (date range, site, cost-object type/id, item, department → item, qty, value, issue no.), **Gate register** (inward/outward by date, from `GTE`, R29 F31), **Issue register by cost object** also lists QC destructive-test issues (inspection lines under `QCINSP`, `IIS-T4-02`, R29 F11), **Consumption by department** (store issues + QC destructive issues − store returns at value, by department × month; **only `VIRT-CONSUMED` lines** — `VIRT-PRODUCTION` issues are WIP, not consumption), **Stores performance** (`FR-534`: gate-to-GRN, GRN-to-MRN, QC lead time, issue turnaround, fill rate, return cycle, dock-to-stock; median / P90 / % inside target). All SQL-aggregated; the page does no arithmetic.

| ID | Rule (WS-277 tab) | Proved by | Source |
|---|---|---|---|
| SIR-T5-01 | Every register tab is a backend-paginated, backend-filtered grid with an export whose columns ⊇ the grid's; the statistics tiles follow the active filters and read **no cache name** (`FR-395`) | each tab's `/management` + `/export` honour the same filter set; no `@Cacheable` on the register query service | FR-539 |
| SIR-T5-02 | **Gate register**: gate entries inward and outward by date (from `GTE`, R29 F31) | rows = `wh_gate_entries` in the date range, by `direction` | FR-539 |
| SIR-T5-03 | **RGP pending / overdue**: RGPs `OUT`/`PARTIALLY_RETURNED`; overdue is computed on read exactly as `GTE-T3-01` | the tab and WS-263's `overdueOnly` return the same RGPs for the same day | FR-539, FR-515 |
| SIR-T5-04 | **Requisitions pending issue**: approved − issued per line, aged by required-by date | open-to-issue equals the WS-274 figure for the same line | FR-539 |
| SIR-T5-05 | **Issue register by cost object**: item, quantity, value by department / cost centre / production order for a date range; also lists QC destructive-test issues (`QCINSP`, `IIS-T4-02`) and issues to `VIRT-PRODUCTION` | value = Σ posted line value; `VIRT-PRODUCTION` lines are listed here | FR-539 |
| SIR-T5-06 | **Consumption by department**: store issues + QC destructive issues − store returns, at value, by department × month, **only lines to `VIRT-CONSUMED`**; an issue to `VIRT-PRODUCTION` (WIP) is never consumption | a production-order issue appears in SIR-T5-05 and not here | FR-539 |
| SIR-T5-07 | **Stores performance**: gate-to-GRN, GRN-to-MRN, QC lead time, issue turnaround (+ fill rate issued ÷ approved at closure), store-return cycle, issue → return elapsed (`ISSUE_TO_RETURN`), dock-to-stock, each from **stored timestamps** (never typed), per site × period, median / P90 / share inside the site target `warehouse.stores.kpi_target_*`, drill-down to the documents | definitions are frozen KPI rows (**nine**, version 1, seeded by `P8-13` in `V511412`, each with a site target setting; R31 F-SR-017); a changed definition is a new KPI version | FR-534 |

## 6. Out of scope

Production issue / backflush / WIP (MFG); tool-crib custody (FRD §12 row 13); editing a posted issue; mobile.

## 7. Amendments

| Date | Change |
|---|---|
| 2026-10-22 | v0 derived. Resolves `S-052` (`GAP-REGISTER.md:614`) per `RN-034` |
| 2026-10-22 | Amended for MFG MD-14 (`SIR-GRD-01a` admits a `COMPLETED` production order; a throwing `onReturnPosted` — MFG on a `CLOSED` order, `409 ORDER_NOT_OPEN` — rolls the return post back) and MD-17 (`SIR-UNR-06`) |
| 2026-10-22 | R29 dispositions: site scope pair + `:view_all_departments`; issue-line item / requisition / base-unit guard; consume-and-split reservation call; department company rule; register reads QC destructive lines; gate register tab; self-approval code |
| 2026-10-23 | R31: `ISSUE_RETURN` seeded irreversible (`SIR-T4-03`, F-SR-008); ninth KPI row `ISSUE_TO_RETURN` and a target per measure (`SIR-T5-07`, F-SR-017); `SIR-OPEN-01`…`-03` resolved (`R31-decisions`; `P8-13` names each tab's grid id and scope) |
| 2026-10-24 | P8 decision record `EV-1` (DECISIONS `D-19`): every outbox event code renamed to the dotted `whb_event_types` vocabulary of registry R.4 (PC-42) — e.g. `purchase_order.amended`, `demand_order.shipped`, `rma.matched`, `supplier_return.dispatched`; no behaviour change |

## 8. Invariants and scenarios

`L-1`, `L-2`, `FR-436`; `RN-034`; scenarios `WH-SC-450`, `-463`…`-472`.

## 9. Open rows

| ID | Question | Default |
|---|---|---|
| SIR-OPEN-01 | OD-27 cost centre source | thin `wh_cost_centres` **RESOLVED (DEFAULT), 2026-10-23** (`R31-decisions`). |
| SIR-OPEN-02 | Should an issue post require the receiver's acknowledgement (PIN / signature) before `POSTED`? | captured as name + time in the post modal; a signature image is an optional platform document id **RESOLVED (DEFAULT), 2026-10-23** (`R31-decisions`). Name + time; optional signature document. |
| SIR-OPEN-03 | `FR-539` names five register tabs but no grid identifier or filter scope for any of them (WS-277 has `G = Y` in `FRD-STORES.md` §7) | one grid id and one `filterUtils` scope per tab, named by `P8-13` before build; until then SIR-T5-01…-06 are checked on behaviour only **RESOLVED (DEFAULT), 2026-10-23** (`R31-decisions`). `P8-13` names the grid id and filter scope of every tab (its *Scope* table). |
