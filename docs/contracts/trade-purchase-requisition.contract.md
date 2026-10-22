# Functional Contract — Purchase requisition (manual, stores shortage, replenishment, MRP) → consolidation → conversion

> **What this is.** The functional truth for raising, approving, consolidating, partially converting and
> closing a purchase requisition in `warehouse-trade`. Approval mechanics cite `TAM-*`
> ([trade-approval-matrix](trade-approval-matrix.contract.md)).
>
> **Sales twin.** The sales enquiry ([trade-sales-enquiry-quotation](trade-sales-enquiry-quotation.contract.md)),
> FRD-TRADE §5 rows M3–M6. Consolidation has no twin (M5).
>
> **Status.** Derived 2026-10-22 (v0). No code exists yet.

---

## 0. Identity

| | |
|---|---|
| **Workflow** | Create (manual or from a core shortage / suggestion) → submit → approve → allocate lines to RFQ / PO / release (consolidated, partial) → ordered → closed; cancel; close-short remainder |
| **Module** | `warehouse-trade`; reads core `wh_material_requisition_lines` (`p8-09`) and `wh_replenishment_suggestions` (`V510070`, origin `MRP` per `OD-31`, published by STORES `p8-16` through `WhReplenishmentSuggestionPort`) |
| **Domain baseline** | FRD-TRADE FR-556…FR-561, `TRD-09`, `OD-31` · R27 `RM-001`, `RM-015` · `p8-10` cost-object vocabulary |
| **Owning task body** | `issues/p9-04.md` |
| **Primary tables** | `wht_purchase_requisitions`, `wht_purchase_requisition_lines`, `wht_requisition_allocations` (`V550030`) |
| **Permission resources** | `wht_purchase_requisitions:view/create/edit/export/submit/approve/cancel` · `wht_requisition_allocations:create` (workbench, buyer) |
| **Routes** | `/warehouse/trade/purchase/requisitions` (WS-286), `/warehouse/trade/purchase/requisition-workbench` (WS-287) · mobile: none |
| **Contract status / version** | `derived` · `v0 — 2026-10-22` |

**Fields.** Header: `pr_number` (issued at submit, series `PR`), `company_id`, `warehouse_id` (requesting
site), `deliver_to_location_id` (nullable), `department_id` ↓ platform `departments`, `cost_object_type` +
`cost_object_id` / `cost_object_code` (`p8-10`), `requested_by` ↓ users, `required_by_date` (DATE),
`priority_code` (code list `trade_priority`), `source_code` (`MANUAL`/`STORES_SHORTAGE`/`REPLENISHMENT`/`MRP`),
`justification` (TEXT), `status`, `approval_request_id`. Line: `line_no`, `item_id` ↓ `whb_items`,
`quantity` > 0, `uom_code`, `required_date`, `suggested_supplier_id` (nullable), `estimated_rate`
(nullable), `estimated_rate_source`, `source_material_requisition_line_id` ↓ core (nullable),
`source_replenishment_suggestion_id` ↓ core (nullable), `allocated_quantity` (maintained from the
junction), `closed_short_quantity`, `close_reason_code`, `line_status`, `notes`. Junction:
`pr_line_id`, `target_type` (`RFQ_LINE` / `PO_LINE` / `PO_RELEASE_LINE`), `target_line_id`, `quantity`,
`is_active`.

### Acceptance checks

| # | Expects | Delivered by |
|---|---|---|
| A1 | Manual PR with department and cost object, approved through the matrix (`WH-SC-496`) | `TPR-T1-01`…`-04` |
| A2 | PR from a stores shortage or MRP suggestion, one source line → one PR line (`WH-SC-497`, `-499`) | `TPR-T1-02`, `TPR-GRD-02` |
| A3 | Consolidation of many PR lines into one RFQ / PO (`WH-SC-500`) | `TPR-T1-06` |
| A4 | Partial conversion never over-allocates, even concurrently (`WH-SC-501`, `-502`) | `TPR-GRD-04` |
| A5 | Cancel only before allocation; remainder close-short after (`WH-SC-503`, `-504`) | `TPR-T1-08`, `-09`, `TPR-T4-03` |

## 1. T1 — State machine

### 1.1 Status inventory

| Entity | Status | Represented by | Reachable via | Exits via | Kind |
|---|---|---|---|---|---|
| PR | `DRAFT` | `status` | `-01`, `-02`, return | `-03`, `-08` | initial |
| PR | `SUBMITTED` | status; number issued | `-03` | approval outcome | active |
| PR | `APPROVED` | status | `TAM` approved | `-06`, `-08`, `-09` | active |
| PR | `REJECTED` | status | `TAM` rejected | edit → `DRAFT` | active |
| PR | `PARTIALLY_ORDERED` | derived & stored from lines | `TPR-T4-01` | `-06`, `-09` | active |
| PR | `ORDERED` | every line `ORDERED` / `CLOSED_SHORT` with ≥ 1 allocation | `TPR-T4-01` | `-10` | active |
| PR | `CLOSED` | all target lines terminal | `-10` | none | terminal |
| PR | `CANCELLED` | status | `-08` | none | terminal |
| Line | `OPEN` → `PARTIALLY_ORDERED` → `ORDERED`; `CLOSED_SHORT`; `CANCELLED` | `line_status` | allocations | — | — |

### 1.2 Transitions

| ID | From | Action | To | Guard | Actor | Side effects | Comment | UI |
|---|---|---|---|---|---|---|---|---|
| TPR-T1-01 | — | Create manual | `DRAFT` | `TPR-GRD-01` | `:create` | estimated rate defaulted (`TPR-T4-04`) | no | WS-286 Add |
| TPR-T1-02 | — | *Raise PR* from shortage / suggestion | `DRAFT`, lines linked | `TPR-GRD-02` | `:create` | qty defaulted to shortfall | justification if qty raised | WS-287 *Import shortages* (no core screen edit, `TPR-OPEN-01`) |
| TPR-T1-03 | `DRAFT`, `REJECTED` | Submit | `SUBMITTED` | `TPR-GRD-01`, `TAM-GRD-02` | `:submit` | number at first submit; `TAM-T1-03` with value Σ qty × est. rate or qty | no | WS-286 Submit |
| TPR-T1-04 | `SUBMITTED` | Approved | `APPROVED` | `TAM` | approver | requester notified | — | WS-285 |
| TPR-T1-05 | `SUBMITTED` | Rejected / returned | `REJECTED` / `DRAFT` | `TAM` | approver | requester notified | yes | WS-285 |
| TPR-T1-06 | `APPROVED`, `PARTIALLY_ORDERED` | Allocate lines → RFQ / PO / release (one target from N PR lines) | allocation rows; line statuses | `TPR-GRD-03`, `-04` | `wht_requisition_allocations:create` + target's `:create` | `TPR-T4-01` | no | WS-287 *Create RFQ* / *Create PO* / *Add to release* |
| TPR-T1-07 | target line cancelled / reduced | Release allocation | allocation inactive or reduced | — | system (target service) | `TPR-T4-03` | — | — |
| TPR-T1-08 | `DRAFT`, `SUBMITTED`(withdraw first), `APPROVED` with zero allocations | Cancel | `CANCELLED` | `TPR-GRD-05` | `:cancel` | source line freed (`TPR-T4-02`) | **yes** | WS-286 |
| TPR-T1-09 | line with open qty, header `APPROVED`/`PARTIALLY_ORDERED` | Close short remainder | line `CLOSED_SHORT` (or `ORDERED` if partially allocated) | open qty > 0 | `:cancel` | requester notified | **yes**, reason code | WS-286 detail |
| TPR-T1-10 | `ORDERED` | All target documents terminal | `CLOSED` | — | system (event from PO/RFQ service) | — | — | — |

### 1.3 Guards

| ID | Predicate | Refusal |
|---|---|---|
| TPR-GRD-01 | ≥ 1 line; qty > 0; item active and purchasable (`whb_items` purchase status); `required_by_date ≥ today` (site tz) at submit; department active; cost object valid per `p8-10` | field `422` |
| TPR-GRD-02 | Source line not linked to another non-cancelled PR line (partial unique index on each source column `WHERE line_status <> 'CANCELLED'`); qty > shortfall needs `justification` | `409 TRADE_SOURCE_LINE_ALREADY_REQUISITIONED`; field `422` |
| TPR-GRD-03 | Selected PR lines share company, and for a PO also deliver-to site; items match the target line (UoM convertible) | `422 TRADE_ALLOCATION_INCOMPATIBLE` |
| TPR-GRD-04 | Under `SELECT … FOR UPDATE` on each PR line: Σ active allocations + new ≤ quantity − closed_short | `422 TRADE_ALLOCATION_EXCEEDS_OPEN {open}` |
| TPR-GRD-05 | No active allocation | `409 TRADE_PR_HAS_ALLOCATIONS` (offer close-short) |
| TPR-GRD-06 | Requester cannot approve own PR | `TAM-GRD-03` |

### 1.4 Unreachable

| ID | Forbidden | Why |
|---|---|---|
| TPR-UNR-01 | Editing an approved PR's quantities | no edit after approval; close-short or a new PR |
| TPR-UNR-02 | Allocation from a `DRAFT` / `SUBMITTED` / `REJECTED` PR | workbench lists approved open lines only, `TPR-GRD-04` re-checks status |
| TPR-UNR-03 | Writing core MR / suggestion rows | trade reads them; a converted suggestion is recorded by core through `WhReplenishmentSuggestionPort.markConverted` (`p8-16`), a stores hand-off through `PurchaseRequisitionHandoff` (`p8-09`) — never a trade repository write (`TRD-09`) |

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from |
|---|---|---|---|
| TPR-T2-01 | Add / edit | `:create` / `:edit` (own or department scope) | `DRAFT`, `REJECTED` |
| TPR-T2-02 | Submit / withdraw | `:submit` | `DRAFT`, `REJECTED` / `SUBMITTED` |
| TPR-T2-03 | Approve | `:approve` via `TAM` | `SUBMITTED` |
| TPR-T2-04 | Allocate | `wht_requisition_allocations:create` | `APPROVED`, `PARTIALLY_ORDERED` |
| TPR-T2-05 | Cancel / close short | `:cancel` | per `-08`, `-09` |
| TPR-T2-06 | Print PR | `:view` | any numbered |
| TPR-T2-07 | Export | `:export` | — |

## 3. T3 — Time-driven rules

| ID | Rule | Trigger | Changes | Notified | Job |
|---|---|---|---|---|---|
| TPR-T3-01 | PR ageing | approved line open > `warehouse.trade.pr.ageing_days` (default 7) | none (computed filter `ageingOnly`, report FR-619) | buyer group daily digest | `TradePrAgeingJob` |
| TPR-T3-02 | Required date passed while open | `required_date < today` | `overdue` computed | requester + buyer | same |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in |
|---|---|---|---|
| TPR-T4-01 | Allocation created / released | line `allocated_quantity`, `line_status`, header status recomputed in the same transaction | `RequisitionAllocationService` |
| TPR-T4-02 | PR line created / cancelled from a source | core shortage / suggestion shows *requisitioned by PR-x* (read through the FK down); on cancel it is free again | read-side join; no core write |
| TPR-T4-03 | Target RFQ line not awarded / PO line cancelled / reduced | allocation released back (`TPR-T1-07`) | target service calls `RequisitionAllocationService.release` |
| TPR-T4-04 | Line saved without estimate | estimate = rate-contract price (`trade-rate-contract` `TRC-T4-02`) else last approved PO rate, source stored | `PurchasePriceResolutionService` (reference mode) |

## 5. T5 — Screen contract

### 5.1 WS-286 Purchase Requisitions (reference **Service Vehicle**)
Grid `wht_purchase_requisitions`, scope `WAREHOUSE_TRADE_PURCHASE_REQUISITION`. Default sort
`e.created_at DESC`. Tiles: `DRAFT`+`REJECTED`, `SUBMITTED`, `APPROVED` (open), `PARTIALLY_ORDERED`,
overdue. Columns: `prNumber`, `warehouseName`, `departmentName`, `costObjectLabel`, `requestedByName`
(user display helper), `requiredByDate` (date-only → `formatDateSync`), `priority`, `source`, `lineCount`,
`estimatedValue`, `status`, audit. Filters: `warehouseId` → `departmentId`; `status`; `source`;
`requestedBy` typeahead; `requiredFrom`/`requiredTo` (`DateRangePicker`); `overdueOnly`. Row actions:
View · Edit · Submit · Withdraw · Cancel · Close short · Print. Toolbar: Add · Import shortages · Export.
Modal tabs: Header · Lines · Approvals.

### 5.2 WS-287 Requisition Workbench
Grid of approved open PR lines `wht_requisition_open_lines`. Columns: `prNumber`, `lineNo`, `itemCode`,
`itemName`, `openQuantity`, `uom`, `requiredDate`, `warehouseName`, `suggestedSupplierName`,
`rateContractSupplierName`, `estimatedRate`, `ageDays`. Filters: `warehouseId`, `itemCategoryId`,
`itemId`, `suggestedSupplierId`, `requiredFrom`/`To`. Multi-select actions: Create RFQ · Create PO (type
picker) · Add to release (agreement picker) — each opens a modal showing per-line quantity to allocate
(defaults to open). No export of selection; grid export allowed.

## 6. Out of scope

| Item | Decision |
|---|---|
| Budget check | refused FRD §11 R13 |
| Service / capex requisition | refused R8 |
| Automatic PR from MRP without a user | not built: MRP output is a core suggestion; a user converts it (`TRD-09`) |

## 7. Amendments

| Date | Rows | Change | Found by |
|---|---|---|---|
| 2026-10-22 | all | v0 derived | TRADE author |

## 8. Invariants and scenarios

`WH-SC-496`…`WH-SC-504`, `WH-SC-488`.

## 9. Open rows

| ID | Question | Status |
|---|---|---|
| TPR-OPEN-01 | Does core render a *Raise PR* action on its MR / suggestion screens when trade is enabled? A core screen cannot import trade code | **Settled by STORES:** core needs no trade import — `p8-09` offers *Send to purchasing* only when trade registers the optional `PurchaseRequisitionHandoff` bean (`FR-528`), and `p8-16` withdraws core's *Convert to PO* when trade registers `SuggestionConversionOwner`; trade's WS-287 *Import shortages* also lists core shortages (read down). DEFERRED-TO-p9-04 |
| TPR-OPEN-02 | `OD-31` MRP path | seam published by `p8-16` (origin `MRP`, `markConverted`); MFG to confirm |
