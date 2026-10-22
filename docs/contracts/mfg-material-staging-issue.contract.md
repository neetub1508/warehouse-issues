# Functional Contract — Material to production: request, staging to line-side, issue and return through core, substitution, consumption policy

> **What this is.** The functional truth for getting components to a production order: *Request
> materials* through core's `WhMaterialRequisitionPort`, manual issue and return through **core** store
> issue / store return with cost object `PRODUCTION_ORDER` (`RN-034`, `MD-04`), pick-to-line **staging
> lists** to a physical `LINE_SIDE` location and *Unstage*, component **substitution**, and the
> **consumption policy** applied to every issue. It also fixes the two WIP models (`MD-05`).
>
> **What this is not.** The store-issue / store-return documents themselves are
> [`store-issue-return.contract.md`](store-issue-return.contract.md) (`SIR-*`) and the requisition is
> [`material-requisition.contract.md`](material-requisition.contract.md) (`MRQ-*`); this contract adds
> only what MFG does through their seams. Backflush consumption at receipt is `PRC-*`. Movement
> mechanics are `MPR-*`.
>
> **Status.** Derived 2026-10-22 (v0) from [`frd/FRD-MFG.md`](../frd/FRD-MFG.md) `FR-638`…`FR-643`,
> `MD-04`, `MD-05`, §3.1, §3.2 (**SEAM-M1**, **SEAM-M2**), §4, scenarios `WH-SC-618`…`-624`; core
> seams per [`frd/FRD-STORES.md`](../frd/FRD-STORES.md) `FR-529`…`FR-533`. Not ratified.

---

## 0. Identity

| | |
|---|---|
| **Workflow** | Per component by supply method — `ISSUE`: *Request materials* → MRQ (core) → store issue (core) into `VIRT-PRODUCTION-<site>` → store return (core); `STAGE_BACKFLUSH`: staging list → release → stage (store bin → `LINE_SIDE`) → consumed by receipt backflush / *Unstage*; `BACKFLUSH`: nothing here (consumed at receipt from the supply location). Substitution and unplanned consumption under the order's consumption policy |
| **Module** | `warehouse-manufacturing`; calls core `WhMaterialRequisitionPort.create/cancel/close` (`p8-09`); implements core `CostObjectResolver` hooks for type `PRODUCTION_ORDER` (`p8-09`/`p8-10`/`p8-11`) |
| **Domain baseline** | `L-1`, `L-6`, `L-10`, `L-12`, `RN-034`, `STO-D11` (posted store issue is never reversed), `MD-04`, `MD-05` · movement types `PRODUCTION_STAGE`, `PRODUCTION_UNSTAGE` (+ `*_REVERSAL`, `MUST_BALANCE_PER_OWNER_ITEM`, `WEIGHTED_AVERAGE`), document type `STAGING_LIST`, location type `LINE_SIDE`, reason contexts `PRODUCTION_SUBSTITUTION`, `PRODUCTION_DEVIATION`, print kind `STAGING_PICK_LIST`, series `STG-` (`V560001`) · `VIRT-PRODUCTION-<site>` (`V500013:35-47`) |
| **Seams owed by others** | **SEAM-M1** (`ResolvedCostObject.counterLocationPurpose = PRODUCTION` used by the store-issue post and store return) and **SEAM-M2** (`assertIssuable`, `onIssuePosted`, `onReturnPosted` in the posting transaction), both written into STORES `FR-533` |
| **Owning tasks** | `issues/p10-06.md`. Depends on `p10-05`, `p8-09`, `p8-10`, `p8-11` |
| **Primary tables** | `whm_staging_lists`, `whm_staging_list_lines`, `whm_component_substitutions` (`V560040`); rollup columns on `whm_production_order_components` (`V560030`) |
| **Status columns** | `whm_staging_lists.status` (`DRAFT`/`RELEASED`/`PARTIALLY_STAGED`/`STAGED`/`CLOSED`/`CANCELLED`) — no `CHECK` |
| **Permission resources** | `whm_staging_lists:{view,create,edit,export,release,stage,unstage,cancel}` · `whm_production_orders:{request_materials,substitute}` · core `wh_store_issues:post`, `wh_store_returns:*`, `wh_material_requisitions:approve` |
| **Routes** | WS-325 `/warehouse/manufacturing/staging-lists` · WS-324 **Materials** tab · core WS-270…WS-274 · mobile: none |
| **Contract version** | `v0 — 2026-10-22` |

### Acceptance checks

| # | Expects | Delivered by |
|---|---|---|
| A1 | Staging is one `PRODUCTION_STAGE` movement per stage action and moves the reservation (`WH-SC-618`) | `MSI-T1-05`, `MSI-T4-06`, `MSI-T4-07` |
| A2 | Line-side stock is never offered to another pick (`WH-SC-619`) | `MSI-T4-07`, `MSI-UNR-03` |
| A3 | *Request materials* creates one MRQ with cost object `PRODUCTION_ORDER`; its store issue lands in `VIRT-PRODUCTION` (`WH-SC-620`) | `MSI-T1-01`, `MSI-T4-01`, `MSI-T4-02` |
| A4 | Under `STRICT` an item not on the order is refused at issue (`WH-SC-621`) | `MSI-GRD-06` |
| A5 | A store return reduces net issued and leaves the pool (`WH-SC-622`) | `MSI-T4-03` |
| A6 | Substitution reduces the original, adds a substitute line, and re-reserves (`WH-SC-623`) | `MSI-T1-09`, `MSI-T4-09` |
| A7 | A `WARN` deviation needs a reason and stays visible (`WH-SC-624`) | `MSI-GRD-07`, `MSI-T4-10` |

---

## 1. T1 — State machine

### 1.1 Status inventory

| Entity | Status | Represented by | Reachable via | Exits via | Kind |
|---|---|---|---|---|---|
| Staging list | `DRAFT` | `status` | `MSI-T1-02` | `-03`, `-04`, `-08` | initial |
| Staging list | `RELEASED` | `status`; `released_by/at` | `MSI-T1-04` | `-05`, `-08` | active |
| Staging list | `PARTIALLY_STAGED` | `status`; some `staged_quantity < requested_quantity` | `MSI-T1-05` | `-05`, `-07` | active |
| Staging list | `STAGED` | `status`; every line staged = requested | `MSI-T1-05` | `-07` | active |
| Staging list | `CLOSED` | `status`; `closed_at` | `MSI-T1-07` | none | **terminal** |
| Staging list | `CANCELLED` | `status` | `MSI-T1-08` | none | **terminal** |
| Substitution | *pending* / *effective* | `approved_by/at` null / set; `created_component_line_id` | `MSI-T1-09`, `-10` | — | record |
| Component line | `OPEN`/`PARTIAL`/`COMPLETE`/`CLOSED` | `line_status` derived on every rollup write | `MSI-T4-02`…`-04`, `PRC-T4-04` | — | derived |

### 1.2 Transitions

| ID | From | Event | To | Guard | Actor | Side effects | Reason? | UI |
|---|---|---|---|---|---|---|---|---|
| MSI-T1-01 | order `RELEASED`/`IN_PROGRESS` | **Request materials** (selected open components, default all `ISSUE` lines with open quantity) | MRQ `DRAFT`→ per core | `MSI-GRD-01`, `PRO-GRD-07` | `whm_production_orders:request_materials` | `WhMaterialRequisitionPort.create`: cost object `PRODUCTION_ORDER`/orderId/`order_number`, purpose `PRODUCTION`, department = work centre's department (else requester's), `source_module = warehouse-manufacturing`, idempotency key `PRD:<orderId>:<seq>`, lines = open quantity (required − issued + returned − open requested) with required date; MRQ then follows `MRQ-T1-02`…`-09` | no | WS-324 Materials **Request materials** |
| MSI-T1-02 | order `RELEASED`/`IN_PROGRESS` | **Generate staging list** from open `STAGE_BACKFLUSH` (option: `ISSUE`) requirements | `DRAFT` | `MSI-GRD-01`, `-02` | `whm_staging_lists:create` | `STG-` number; `to_location_id` = order line-side → work centre default line-side; lines with suggested `from_location`/lot by FEFO/FIFO; `requested_quantity` = required − staged + unstaged − consumed | no | WS-324 **Stage** · WS-325 **Add** |
| MSI-T1-03 | `DRAFT` | Edit lines (from location, lot, serial, requested quantity), remove lines | `DRAFT` | `MSI-GRD-02`, `-03` | `:edit` | — | no | WS-325 **Edit** |
| MSI-T1-04 | `DRAFT` | **Release** | `RELEASED` | `MSI-GRD-01`…`-03` | `:release` | `released_by/at`; pick list printable (`STAGING_PICK_LIST`, lots + bins) | no | WS-325 **Release** |
| MSI-T1-05 | `RELEASED` · `PARTIALLY_STAGED` | **Stage** selected lines / quantities | `PARTIALLY_STAGED` · `STAGED` | `MSI-GRD-01`, `-03`, `-04`; order not on hold | `:stage` | **one** `PRODUCTION_STAGE` movement for the action (`MSI-T4-06`); reservation moved (`MSI-T4-07`); line `staged_quantity` +=, component `staged_quantity` +=; first posting → order `IN_PROGRESS` (`PRO-T1-12`) | no | WS-325 **Stage** modal |
| MSI-T1-06 | order `RELEASED`/`IN_PROGRESS`/`COMPLETED`, line-side balance of the order > 0 | **Unstage** quantity of a component back to a store location | unchanged | `MSI-GRD-05` | `whm_staging_lists:unstage` | **one** `PRODUCTION_UNSTAGE` movement line-side → store location; component `unstaged_quantity` +=; reservation returned to the store position (or released when the order is `COMPLETED`) | no | WS-324 Materials **Unstage** |
| MSI-T1-07 | `PARTIALLY_STAGED` · `STAGED` | **Close** (from `PARTIALLY_STAGED` = close short, MD-22) | `CLOSED` | — | `:release` | unstaged requested remainder dropped; its reservations **stay with the order** (they are the order's, MD-16) and are released only at order close/cancel; also the effect of order close (`CST-T4-07`) | **yes** (note) when `PARTIALLY_STAGED`; no when `STAGED` | WS-325 **Close** |
| MSI-T1-08 | `DRAFT` · `RELEASED` (nothing staged) | **Cancel** | `CANCELLED` | Σ `staged_quantity` = 0 | `:cancel` | number stays issued | **yes** (note) | WS-325 **Cancel** |
| MSI-T1-09 | order `RELEASED`/`IN_PROGRESS` | **Substitute** from the BOM alternate group (priority order) | effective | `MSI-GRD-08` | `whm_production_orders:substitute` | `whm_component_substitutions` (`source = BOM_ALTERNATE`) and effects `MSI-T4-09` | **yes** (`PRODUCTION_SUBSTITUTION`) | WS-324 Components **Substitute** |
| MSI-T1-10 | same | **Substitute ad hoc** (any item) | `FLEXIBLE`/`WARN`: effective · `STRICT`: *pending* until a second `:substitute` holder approves | `MSI-GRD-08`, `-09` | `:substitute` (maker), second user (checker under `STRICT`) | as `-09` with `source = AD_HOC`; under `STRICT` effects apply at approval (`approved_by/at`) | **yes** + note | same |
| MSI-T1-11 | MRQ approved | (core) **store issue post** with cost object the order (`SIR-T1-03`) | — | `SIR-GRD-*` + `MSI-GRD-06`, `-07` via `assertIssuable` | core `wh_store_issues:post` (stores-issue clerk) | `MSI-T4-02` | — | core WS-271 |
| MSI-T1-12 | issue posted | (core) **store return post** linked to the issue line (`SIR-T1-07`) | — | `SIR-GRD-07`…`-10` (return ≤ net issued, by core) | core `wh_store_returns:post` | `MSI-T4-03` | — | core WS-272 |
| MSI-T1-13 | order `RELEASED`/`IN_PROGRESS`/`COMPLETED` (late issue, MD-14) | **Request extra material** (over-requirement or unplanned item) | MRQ as `-01` | `MSI-GRD-06`, `-07` evaluated **here**, with the deviation reason captured on the order | `:request_materials` | for an unplanned item: a component line `is_unplanned = true`, `deviation_reason_code_id`; then `WhMaterialRequisitionPort.create` | **yes** under `WARN` (`PRODUCTION_DEVIATION`) | WS-324 **Request extra** |
| MSI-T1-14 | order cancelled / closed | (effect) open MRQ of the order | MRQ `CANCELLED` / `CLOSED` | — | system | `WhMaterialRequisitionPort.cancel` (nothing issued) or `.close` (short-close remainder) (`FR-656`) | system reason | — |

### 1.3 Guards

| ID | Predicate | Refusal | Backstop | Source |
|---|---|---|---|---|
| MSI-GRD-01 | Order `RELEASED`/`IN_PROGRESS` for request, staging and substitution; **`COMPLETED` also for unstage, request extra, store issue and store return** (late issues and returns until `CLOSED`, MD-14); not on hold; no settlement `DRAFT`/`APPROVED`; same site | `409 ORDER_NOT_OPEN` / `409 ORDER_ON_HOLD` / `409 ORDER_SETTLEMENT_PENDING` | the `PRODUCTION_ORDER` resolver (STORES `FR-533`, `SIR-GRD-01a`, amended for MD-14) | FR-634, FR-640, FR-656 |
| MSI-GRD-02 | Staging `to_location` of type `LINE_SIDE`, stock-holding, same site; staging line's component line belongs to the order and has supply method `STAGE_BACKFLUSH` (or `ISSUE` when the option is on) | `422 STAGING_LOCATION_NOT_LINE_SIDE` · `422 STAGING_LINE_INVALID` | FK `whb_locations`; location type read | FR-639 |
| MSI-GRD-03 | `requested_quantity > 0`; Σ live staging requested for a component ≤ required − staged + unstaged − consumed (+ tolerance under `WARN`/`FLEXIBLE`) | `422 STAGING_EXCEEDS_REQUIREMENT` naming the open quantity | — | FR-639, FR-643 |
| MSI-GRD-04 | Stage: from-location stock-holding, status `AVAILABLE`, lot not expired / on hold, serial captured for serialised items, on hand ≥ quantity (or negative-stock policy) | `422 STOCK_STATUS_NOT_ISSUABLE` / `422 LOT_NOT_ISSUABLE` / `422 SERIAL_REQUIRED` / writer refusal | ledger (`MPR-T1-01`) | FR-639 |
| MSI-GRD-05 | Unstage: quantity ≤ the order's line-side balance of the item (staged − unstaged − consumed at the line-side location); target is a stock-holding non-`LINE_SIDE` location | `422 UNSTAGE_EXCEEDS_STAGED` | — | FR-641 |
| MSI-GRD-06 | `assertIssuable` (store issue post) / request extra under **`STRICT`**: item is on the order (incl. effective substitutes) and cumulative issued + staged + this ≤ required × (1 + `consumption_tolerance_percent`) | `422 ITEM_NOT_ON_ORDER` · `422 CONSUMPTION_DEVIATION_NOT_ALLOWED` | — | FR-640, FR-643, `WH-SC-621` |
| MSI-GRD-07 | Under **`WARN`**: a deviation (over tolerance or unplanned) needs a `PRODUCTION_DEVIATION` reason — captured by `MSI-T1-13`; a core issue line not covered by such a request (e.g. a direct issue) is refused by `assertIssuable`. Under **`FLEXIBLE`**: free | `422 DEVIATION_REASON_REQUIRED` | — | FR-643, `WH-SC-624` |
| MSI-GRD-08 | Substitution: substitute item active, stock-holding, UoM convertible to its base, ≠ original, not phantom; quantity > 0; original line open quantity ≥ the quantity it replaces; from alternate group: the item is an alternate of that BOM line (priority order offered first) | `422 SUBSTITUTE_INVALID` · `422 SUBSTITUTION_EXCEEDS_OPEN` | — | FR-642 |
| MSI-GRD-09 | `STRICT` ad-hoc substitution approver ≠ requester | `403 SUBSTITUTION_SELF_APPROVAL` (MD-21) | — | FR-642 |
| MSI-GRD-10 | Return above net issued | core `422 STORE_RETURN_EXCEEDS_ISSUED` (`SIR-GRD-07`) | CHECK on issue line | FR-641 |

### 1.4 Unreachable

| ID | Must never happen |
|---|---|
| MSI-UNR-01 | An MFG issue slip or MFG issue document (`MD-04`, `RM-022`) — manual issue is always the core store issue |
| MSI-UNR-02 | An issue to a production order landing in `VIRT-CONSUMED-<site>` (**SEAM-M1**) |
| MSI-UNR-03 | Staged line-side stock allocated to any holder other than its order (`L-6`, `WH-SC-619`) |
| MSI-UNR-04 | A rollup (`issued_quantity`, `returned_quantity`, `staged_quantity`, `unstaged_quantity`) updated outside the posting transaction (**SEAM-M2**) |
| MSI-UNR-05 | Reversal of a posted store issue (`STO-D11`); MFG relies on no `onIssueReversed` hook |
| MSI-UNR-06 | A cost-object column on the ledger (`RN-034`) |
| MSI-UNR-07 | A staging or unstage movement that changes owner, lot, serial or stock status |

## 2. T2 — Action × role × state (maker–checker)

| ID | Action | Permission | Allowed from | Persona / extra |
|---|---|---|---|---|
| MSI-T2-01 | Request materials / extra | `whm_production_orders:request_materials` | order `RELEASED`/`IN_PROGRESS` | production supervisor; MRQ approval is core's (approver ≠ requester, `MRQ-T1-03`) |
| MSI-T2-02 | Create / edit / release staging list | `whm_staging_lists:create`/`:edit`/`:release` | — / `DRAFT` | supervisor or stores-issue clerk |
| MSI-T2-03 | Stage | `:stage` | `RELEASED`/`PARTIALLY_STAGED` | stores-issue clerk |
| MSI-T2-04 | Unstage | `:unstage` | per `MSI-T1-06` | stores-issue clerk |
| MSI-T2-05 | Cancel staging list | `:cancel` | `DRAFT`/`RELEASED`, nothing staged | supervisor |
| MSI-T2-06 | Substitute | `whm_production_orders:substitute` | order open | supervisor; `STRICT` ad hoc needs a second holder |
| MSI-T2-07 | Store issue / return | core `wh_store_issues:post` / `wh_store_returns:post` | per `SIR-T2-*` | stores-issue clerk |
| MSI-T2-08 | Print pick list | `wh_print_jobs:create` | `RELEASED` onward | — |

## 3. T3 — Time-driven rules

| ID | Rule | Trigger | Changes | Notified | Job | Once? |
|---|---|---|---|---|---|---|
| MSI-T3-01 | Stale staging | an order's line-side balance > 0 and no stage / unstage / receipt for the order in `warehouse.manufacturing.staging_stale_days` (default 7) | nothing — tile + alert | supervisor, stores in-charge | daily (Scheduler) | once per episode |
| MSI-T3-02 | Released staging list not staged | `RELEASED` > `staging_stale_days` with Σ staged = 0 | nothing | stores in-charge | daily | once |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in |
|---|---|---|---|
| MSI-T4-01 | core store-issue post, line cost object `PRODUCTION_ORDER` | `CostObjectResolver.assertIssuable(orderId, itemId, baseQty)` runs `MSI-GRD-01`, `-06`, `-07` before the writer; the resolver's `counterLocationPurpose = PRODUCTION` makes the `ISSUE` movement's counter line `+qty` at **`VIRT-PRODUCTION-<site>`** (**SEAM-M1**, `WH-SC-620`) | core issue service → MFG resolver |
| MSI-T4-02 | same, inside the post transaction | `onIssuePosted(line)`: component `issued_quantity` += base qty (unplanned item → its `is_unplanned` line), `consumed_quantity` recomputed, `line_status` derived, first posting → `PRO-T1-15`; a hook failure rolls the issue back (**SEAM-M2**) | MFG resolver |
| MSI-T4-03 | core store-return post of an issue line with this cost object | `onReturnPosted(line)`: `returned_quantity` +=; core posts `ISSUE_RETURN` −qty at `VIRT-PRODUCTION-<site>` (same purpose, **SEAM-M1**) at the issue line's unit cost, so the value leaves the order's pool (`CST-T4-05`, `WH-SC-622`) | core return service → MFG resolver |
| MSI-T4-04 | order reservation and MRQ | **the order is the single owner** (MD-16): the MRQ created by `MSI-T1-01` reserves nothing because the resolver's `reservationsFor(orderId, itemId)` returns the order's component reservations (`MRQ-T4-01` as amended); the store issue's `consumedReservationIds` are those reservations (`SIR-T4-01` as amended); MRQ close/cancel release nothing — order close/cancel do (`PRO-T4-04`, `-05`) | core issue service + MFG resolver |
| MSI-T4-05 | genealogy | lots / serials of posted store-issue lines with this cost object since the order's previous receipt (net of returns) are attributed to the next receipt's transformation (`PRC-T4-06`, `FR-648`) — read at receipt, nothing stored here | receipt service |
| MSI-T4-06 | stage action | **one** `PRODUCTION_STAGE` movement (`WhbStockLedgerWriter.post`): `sourceSystem = WAREHOUSE_MANUFACTURING`, `sourceDocumentType = STAGING_LIST`, id, `sourceDocumentNo = STG-…`, idempotency `STAGING_LIST:<id>:<actionSeq>`; per line −qty at the from-location, +qty at the line-side location, same owner / item / lot / serial / status; balanced per `MUST_BALANCE_PER_OWNER_ITEM`; `movement_id` on the staging line (`MSI-OPEN-02`) | staging service → writer |
| MSI-T4-07 | stage | the order's reservation for the component is reduced at the source position and a reservation with the **same holder quad** is made at the line-side position for the staged quantity — **always**, even when `component_reservation = NONE` (staged stock is never allocatable to another holder, `FR-639`); `LINE_SIDE` is not pickable for outbound | staging service → `WhbReservationService` |
| MSI-T4-08 | unstage | **one** `PRODUCTION_UNSTAGE` movement line-side → store location; line-side reservation reduced; store-position reservation restored (order open) or released (order `COMPLETED`) | staging service |
| MSI-T4-09 | substitution effective | original line's `required_quantity` reduced by the replaced quantity (never below consumed); a new component line with `substitute_of_line_id`, `substitution_id`, required date and supply method of the original; UoM factor re-resolved and frozen; original reservation released for that quantity and a new one made for the substitute (`L-10`); genealogy and cost follow the substitute (`WH-SC-623`) | order service |
| MSI-T4-10 | deviation recorded (`WARN`) or free (`FLEXIBLE`) | the component line shows required vs consumed variance and `deviation_reason_code_id`; reported in WS-337 consumption variance (`FR-643`) | order service |
| MSI-T4-11 | order close / cancel | `MSI-T1-14`; staging lists closed / cancelled; any line-side balance blocks close (`CST-GRD-02`) | close service |

## 5. T5 — Screen contract

### 5.1 WS-325 Staging Lists (reference: **Service Vehicle**)

| | |
|---|---|
| **Grid** | `whm_staging_lists` · scope `WAREHOUSE_MFG_STAGING_LIST` · sort `e.created_at DESC` |
| **Tiles (5)** | `DRAFT` · `RELEASED` · `PARTIALLY_STAGED` · `STAGED` · *Stale* (`MSI-T3-01`) |
| **Columns** | `stagingNumber`, `warehouseName`, `orderNumber`, `orderItemCode`, `toLocationCode`, `lineCount`, `requestedQuantity`, `stagedQuantity`, `status`, `releasedByName`, `releasedAt`, `closedAt`, `createdByName`, `updatedByName` |
| **Filters** | `warehouseId`; `status`; `orderId` (typeahead); `toLocationId`; `itemId`; `createdFrom/To` (`date`) |
| **Row actions** | View · Edit (`DRAFT`) · Release · Stage · Close · Cancel · Print pick list |
| **Toolbar** | Add (pick an open order) · Export |
| **Stage modal** | per line: `itemCode`, `fromLocation`, `lot`, `serials`, `requestedQuantity`, `stagedQuantity`, `quantityToStage`; refusal shown in `AlertBox` inside the modal |
| **Export** | grid + **Lines** sheet (`itemCode`, `fromLocationCode`, `lotCode`, `requestedQuantity`, `stagedQuantity`, `movementNumber`) + `createdByName`, `updatedByName` |

### 5.2 WS-324 Materials tab (owned here)

Sections: **Requisitions** (MRQ number, status, lines requested / approved / issued — read from core), **Issues & returns** (core store-issue / return lines with this cost object, value), **Staging** (lists, line-side balance per component, *Unstage*), **Substitutions** (original, substitute, quantity, source, reason, approved by). Actions: Request materials · Request extra · Stage · Unstage · Substitute.

## 6. Error codes

| Code | HTTP | When | FR | WH-SC |
|---|---|---|---|---|
| `ITEM_NOT_ON_ORDER` | 422 | `STRICT`, issue of an item not on the order | FR-640, FR-643 | 621 |
| `CONSUMPTION_DEVIATION_NOT_ALLOWED` | 422 | `STRICT`, issue/stage beyond tolerance | FR-643 | — |
| `DEVIATION_REASON_REQUIRED` | 422 | `WARN`, deviation without reason | FR-643 | 624 |
| `ORDER_ON_HOLD` / `ORDER_NOT_OPEN` | 409 | resolver / staging on a held or non-open order | FR-634, FR-640 | 615, 643 |
| `STAGING_LOCATION_NOT_LINE_SIDE` | 422 | to-location not `LINE_SIDE` | FR-639 | 618 |
| `STAGING_LINE_INVALID` | 422 | line not an open stageable component | FR-639 | — |
| `STAGING_EXCEEDS_REQUIREMENT` | 422 | requested above open requirement | FR-639 | — |
| `UNSTAGE_EXCEEDS_STAGED` | 422 | unstage above line-side balance | FR-641 | — |
| `SUBSTITUTE_INVALID` / `SUBSTITUTION_EXCEEDS_OPEN` | 422 | bad substitute / over the open quantity | FR-642 | 623 |
| `SUBSTITUTION_SELF_APPROVAL` | 403 | `STRICT` ad hoc approved by the requester | FR-642 | — |
| `STORE_RETURN_EXCEEDS_ISSUED` | 422 | core, return above net issued | FR-641 | 622 |

All except `ITEM_NOT_ON_ORDER`, `ORDER_ON_HOLD`, `ORDER_NOT_OPEN` and core's codes are contract-defined.

## 7. Edge cases

| ID | Case | Behaviour | FR | WH-SC |
|---|---|---|---|---|
| MSI-EC-01 | `CASING-01` 105 staged from `PLT1-RM-B04` | one `PRODUCTION_STAGE` movement to `PLT1-LS-A`; reservation at line-side; staged 105 | FR-639 | 618 |
| MSI-EC-02 | Sales pick for `CASING-01` | line-side stock not offered | FR-639 | 619 |
| MSI-EC-03 | Store issue of 100 `SHAFT-03` | lands in `VIRT-PRODUCTION-PLT1`; issued 100 | FR-640 | 620 |
| MSI-EC-04 | 100 issued, 97 consumed, 3 returned after final receipt | returned 3, net 97; value leaves the pool — a residual for settlement (`CST-T1-01`) | FR-641, FR-656 | 622, 641 |
| MSI-EC-05 | Substitute 40 `IMPELLER-02B` for short `IMPELLER-02` | original required 60, substitute line 40, reservations re-made | FR-642 | 623 |
| MSI-EC-06 | Issue to a held order | resolver refuses; the MRQ stays approved | FR-640 | 615 |
| MSI-EC-07 | Direct issue (no requisition) to an order under `WARN` beyond tolerance | refused `DEVIATION_REASON_REQUIRED`; the supervisor uses *Request extra* | FR-643 | 624 |
| MSI-EC-08 | Partial stage, then stage the rest in a second action | two `PRODUCTION_STAGE` movements, each its own idempotency key | FR-639 | 618 |
| MSI-EC-09 | Unstage after order `COMPLETED` | allowed; reservation released, not restored | FR-641 | — |
| MSI-EC-10 | Substitution of a quantity already staged | refused `SUBSTITUTION_EXCEEDS_OPEN` until unstaged | FR-642 | — |

## 8. Out of scope

Tool-crib custody; kanban / pull replenishment of line-side; per-unit consumption capture (`MD-11`); an MFG issue document (`MD-04`); mobile (`R-13`).

## 9. Amendments

| Date | Change |
|---|---|
| 2026-10-22 | v0 derived from FRD-MFG FR-638…FR-643 and FRD-STORES FR-529…FR-533 |
| 2026-10-22 | Consistency pass: late issues/returns on `COMPLETED` (MD-14), single reservation owner via `reservationsFor` (MD-16), no `onIssueReversed` (MD-17), staging close short (MD-22), `CST-` cross-references, `MSI-EC-` edge-case ids |

## 10. Invariants and scenarios

`L-1`, `L-6`, `L-10`, `L-12`, `RN-034`, `STO-D11`; `MD-04`, `MD-05`; SEAM-M1, SEAM-M2; scenarios `WH-SC-618`…`-624`.

## 11. Open rows

| ID | Question | Default |
|---|---|---|
| MSI-OPEN-01 *(resolved — MD-16; STORES `FR-531`/`FR-533`, `MRQ-T4-01`/`-03` amended)* | Order reservations (HARD at release) and MRQ approval reservations (`MRQ-T4-01`) would double-reserve the same `ISSUE` component | **adopted:** the order is the only owner; the resolver's `reservationsFor(orderId, itemId)` names them, MRQ approval reserves nothing, the store issue consumes them, MRQ close/cancel releases none (the port signature carries no reservation ids) |
| MSI-OPEN-02 | `whm_staging_list_lines` has one `movement_id` but a line may be staged by several actions | add a child `whm_staging_list_line_postings` (movement id, quantity) or allow one stage action per line — P10-06 to settle |
| MSI-OPEN-03 | A core store-issue line carries no deviation reason, so `WARN` cannot be satisfied on the core screen | `MSI-T1-13` captures it on the order before the MRQ (adopted here) |
| MSI-OPEN-04 *(resolved — MD-17; FRD-MFG SEAM-M2 corrected)* | FRD-MFG SEAM-M2 lists an `onIssueReversed` hook; FRD-STORES `FR-533` says there is none (`STO-D11`) | follow STORES: no reversal hook; correction is a store return |
| MSI-OPEN-05 | `whm_component_substitutions` has no status for a `STRICT` pending substitution | pending = `approved_by` null (adopted); add a status column if a reject path is wanted |
