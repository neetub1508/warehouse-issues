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
| **Permission resources** | `wht_purchase_requisitions:view/create/edit/export/submit/approve/cancel` · `wht_requisition_allocations:create` (workbench, buyer). Bundles: requester, **stores requester** (create + submit, used by the core hand-off) and buyer also hold core `warehouse:orders:port` (FRD-TRADE §12a), because their acts call `markConverted` / `releaseConversion` |
| **Routes** | `/warehouse/trade/purchase/requisitions` (WS-286), `/warehouse/trade/purchase/requisition-workbench` (WS-287) · mobile: none |
| **Contract status / version** | `derived` · `v1 — 2026-10-22` (R29 folded) |

**Fields.** Header: `pr_number` (issued at submit, series `PR`), `handoff_idempotency_key` (unique, set only by `TPR-T1-02a`), `company_id`, `warehouse_id` (requesting
site), `deliver_to_location_id` (nullable), `department_id` ↓ platform `departments`, `cost_object_type` +
`cost_object_id` / `cost_object_code` (`p8-10`), `requested_by` ↓ users, `required_by_date` (DATE),
`priority_code` (code list `trade_priority`), `source_code` (`MANUAL`/`STORES_SHORTAGE`/`REPLENISHMENT`/`MRP`),
`justification` (TEXT), `status`, `approval_request_id`. Line: `line_no`, `item_id` ↓ `whb_items`,
`quantity` > 0, `uom_code`, `required_date`, `suggested_supplier_id` (nullable), `estimated_rate`
(nullable), `estimated_rate_source`, `source_material_requisition_line_id` ↓ core (nullable),
`source_replenishment_suggestion_id` ↓ core (nullable), `allocated_quantity` (maintained from the
junction), `closed_short_quantity`, `close_reason_code`, `line_status` (`OPEN`, `IN_RFQ`, `PARTIALLY_ORDERED`,
`ORDERED`, `CLOSED_SHORT`, `CANCELLED`), `notes`. Junction:
`pr_line_id`, `target_type` (`RFQ_LINE` / `PO_LINE` / `PO_RELEASE_LINE`), `target_line_id`, `quantity`,
`is_active`.

### Acceptance checks

| # | Expects | Delivered by |
|---|---|---|
| A1 | Manual PR with department and cost object, approved through the matrix (`WH-SC-496`) | `TPR-T1-01`…`-04` |
| A2 | PR from a stores shortage or MRP suggestion, one source line → one PR line (`WH-SC-497`, `-499`) | `TPR-T1-02`, `-02a`, `TPR-GRD-02` |
| A3 | Consolidation of many PR lines into one RFQ / PO (`WH-SC-500`) | `TPR-T1-06` |
| A4 | Partial conversion never over-allocates, even concurrently (`WH-SC-501`, `-502`) | `TPR-GRD-04` |
| A5 | Cancel only before allocation; remainder close-short after (`WH-SC-503`, `-504`) | `TPR-T1-08`, `-09`, `TPR-T4-03` |
| A6 | A PR whose lines all end, however they end, closes; a cancelled converted line frees its suggestion (`WH-SC-574`) | `TPR-T1-10`, `TPR-T4-02` |

## 1. T1 — State machine

### 1.1 Status inventory

| Entity | Status | Represented by | Reachable via | Exits via | Kind |
|---|---|---|---|---|---|
| PR | `DRAFT` | `status` | `-01`, `-02`, return | `-03`, `-08` | initial |
| PR | `SUBMITTED` | status; number issued | `-03` | approval outcome | active |
| PR | `APPROVED` | status | `TAM` approved | `-06`, `-08`, `-09` | active |
| PR | `REJECTED` | status | `TAM` rejected | edit → `DRAFT` | active |
| PR | `PARTIALLY_ORDERED` | derived & stored from lines | `TPR-T4-01` | `-06`, `-09`, `-10` | active |
| PR | `ORDERED` | every line `ORDERED` / `CLOSED_SHORT` / `CANCELLED`, at least one `ORDERED` | `TPR-T4-01` | `-10` | active |
| PR | `CLOSED` | every line terminal: `ORDERED` with all its targets terminal, `CLOSED_SHORT` or `CANCELLED` — whatever the allocation | `-10` | none | terminal |
| PR | `CANCELLED` | status | `-08` | none | terminal |
| Line | `OPEN` → `IN_RFQ` (allocated to RFQ lines only) → `PARTIALLY_ORDERED` → `ORDERED` (Σ PO / release allocation = qty − closed short); `CLOSED_SHORT`; `CANCELLED` | `line_status` | allocations | — | — |

### 1.2 Transitions

| ID | From | Action | To | Guard | Actor | Side effects | Comment | UI | Source |
|---|---|---|---|---|---|---|---|---|---|
| TPR-T1-01 | — | Create manual | `DRAFT` | `TPR-GRD-01` | `:create` | estimated rate defaulted (`TPR-T4-04`) | no | WS-286 Add | FR-556 |
| TPR-T1-02 | — | *Import shortages* (buyer) from core shortfalls / suggestions | `DRAFT`, lines linked | `TPR-GRD-02` | `:create` | qty defaulted to shortfall; each suggestion line → `markConverted` (`TPR-T4-02`) | justification if qty raised | WS-286 toolbar *Import shortages* | FR-557 |
| TPR-T1-02a | — | **Core hand-off**: core calls `PurchaseRequisitionHandoff.raise(HandoffCommand)` (`ai.warehouse.port.purchase`; envelope `sourceModule = warehouse`, key `MRQ_HANDOFF:<row id>`, `actingUserId` = the stores user) from *Send to purchasing* on a core MR (`MRQ-T1-11`) | PR `SUBMITTED` with one line (source `STORES_SHORTAGE`, linked to the MR line) — created **and submitted** in the call | `TPR-GRD-01`, `-02`, `TAM-GRD-02`; a replayed key returns the same `HandoffRef` | the acting stores user, who must hold `:create` + `:submit` (stores requester bundle); maker = that user | number issued (FR-547); `TAM-T1-03`; returns `HandoffRef('warehouse-trade', 'WHT_PURCHASE_REQUISITION', id, pr_number)`; `status(ref)` → `(line_status, label, Σ allocated to PO lines, received from core, closed)`; a refusal (e.g. `422 TRADE_NO_APPROVAL_RULE`) is thrown to core, which shows it | no | core MR screen (`p8-09`) | FR-557 |
| TPR-T1-03 | `DRAFT`, `REJECTED` | Submit | `SUBMITTED` | `TPR-GRD-01`, `TAM-GRD-02` | `:submit` | number at first submit; `TAM-T1-03` with value Σ qty × est. rate or qty | no | WS-286 Submit | FR-558 |
| TPR-T1-04 | `SUBMITTED` | Approved | `APPROVED` | `TAM` | approver | requester notified (`TRADE_APPROVAL_DECIDED`) | — | WS-285 | FR-558 |
| TPR-T1-05 | `SUBMITTED` | Rejected / returned | `REJECTED` / `DRAFT` | `TAM` | approver | requester notified (`TRADE_APPROVAL_DECIDED`) | yes | WS-285 | FR-551 |
| TPR-T1-06 | `APPROVED`, `PARTIALLY_ORDERED` | Allocate lines → RFQ / PO / release (one target from N PR lines) | allocation rows; line statuses | `TPR-GRD-03`, `-04` | `wht_requisition_allocations:create` + target's `:create` | `TPR-T4-01` | no | WS-287 *Create RFQ* / *Create PO* / *Add to release* | FR-559, FR-560 |
| TPR-T1-07 | target line cancelled / reduced | Release allocation | allocation inactive or reduced | — | system (target service) | `TPR-T4-03` | — | — | FR-561 |
| TPR-T1-08 | `DRAFT`, `SUBMITTED`(withdraw first), `APPROVED` with zero allocations | Cancel | `CANCELLED` | `TPR-GRD-05` | `:cancel` | source line freed; a converted suggestion is returned by `releaseConversion` (`TPR-T4-02`) | **yes** | WS-286 | FR-561 |
| TPR-T1-09 | line with open qty, header `APPROVED`/`PARTIALLY_ORDERED` | Close short remainder | line `CLOSED_SHORT` (or `ORDERED` if partially allocated) | open qty > 0 | `:cancel` | requester notified (`TRADE_PR_CLOSED_SHORT`); a line closed short **with no allocation** that converted a suggestion → `releaseConversion` | **yes**, reason code | WS-286 detail | FR-561 |
| TPR-T1-10 | `APPROVED`, `PARTIALLY_ORDERED`, `ORDERED` | Every line terminal (`ORDERED` with all targets terminal, `CLOSED_SHORT`, `CANCELLED`) | `CLOSED` | — | system (after `-09`, and on target-terminal events from the RFQ / PO services) | — | — | — | FR-560 |

### 1.3 Guards

| ID | Predicate | Refusal | Source |
|---|---|---|---|
| TPR-GRD-01 | ≥ 1 line; qty > 0; item active and purchasable (`whb_items` purchase status); `required_by_date ≥ today` (site tz) at submit; department active; cost object valid per `p8-10` | field `422` | FR-556 |
| TPR-GRD-02 | Source line not linked to another non-cancelled PR line (partial unique index on each source column `WHERE line_status <> 'CANCELLED'`); qty > shortfall needs `justification` | `409 TRADE_SOURCE_LINE_ALREADY_REQUISITIONED`; field `422` | FR-557 |
| TPR-GRD-03 | Selected PR lines share company, and for a PO also deliver-to site; items match the target line (UoM convertible) | `422 TRADE_ALLOCATION_INCOMPATIBLE` | FR-559 |
| TPR-GRD-04 | Under `SELECT … FOR UPDATE` on each PR line: Σ active allocations + new ≤ quantity − closed_short | `422 TRADE_ALLOCATION_EXCEEDS_OPEN {open}` · **R32: the bound is widened by `TPR-GRD-10` (tolerance + `exceed_pr`, default 0 = this row unchanged)** | FR-560 |
| TPR-GRD-05 | No active allocation | `409 TRADE_PR_HAS_ALLOCATIONS` (offer close-short) | FR-561 |
| TPR-GRD-06 | Requester cannot approve own PR | `TAM-GRD-03` | FR-549 |
| TPR-GRD-07 | **Module start-up** (`warehouse-trade`, package `ai.warehousetrade`, band `V550000`–`V559999`, prefix `wht_`, switch `enable.warehouse.trade` read by `@ConditionalOnExpression`): the core port beans it calls unconditionally — `WhPurchaseOrderPort`, `WhDemandOrderPort`, `WhAvailableToPromiseQuery` — are present. `WhReplenishmentSuggestionPort` is **optional** (R31 F-TR-020, as `p9-01`): absent, *Import shortages* and suggestion conversion refuse `503` and are hidden; `WhRmaPort` absent disables only the SRA screens (`TSR-GRD-04`) | the module refuses to start, naming the missing bean | FR-540 |
| TPR-GRD-08 | **Concurrency**: every edit, submit, transition and approval of a `wht_` document checks its optimistic `version`; a stale write changes nothing; every write through `WhReplenishmentSuggestionPort` (`TPR-T4-02`) carries a `PortEnvelope` whose idempotency key has the FRD-TRADE §12a shape `<SOURCE_DOCUMENT_TYPE>:<id>:<operation>:<sequence>`, and the port call commits with the trade transition, so a double-clicked action changes core once | `409 CONCURRENT_MODIFICATION` stale write (`TPR-OPEN-03`); `409 PORT_IDEMPOTENCY_CONFLICT` relayed | FR-618 |

### 1.4 Unreachable

| ID | Forbidden | Why | Source |
|---|---|---|---|
| TPR-UNR-01 | Editing an approved PR's quantities | no edit after approval; close-short or a new PR | FR-553 |
| TPR-UNR-02 | Allocation from a `DRAFT` / `SUBMITTED` / `REJECTED` PR | workbench lists approved open lines only, `TPR-GRD-04` re-checks status | FR-560 |
| TPR-UNR-03 | Writing core MR / suggestion rows | trade reads them; a converted suggestion is recorded by core through `WhReplenishmentSuggestionPort.markConverted` / `releaseConversion` (`p8-16`), a stores hand-off through core's call of trade's `PurchaseRequisitionHandoff` (`p8-09`) — never a trade repository write (`TRD-09`) | FR-557 |
| TPR-UNR-04 | A `wh_` / `whb_` table, entity, service or route that references `wht_` (an FK or a call pointing **up**); a Mode-A install without trade behaving differently, or core PO / demand-order screens failing for documents core creates itself | every FK points down (`wht_` → `wh_` / `whb_` / platform); enforced by `ArchitectureInvariantsTest` (`warehouse/backend/src/test/java/ai/warehouse/architecture/ArchitectureInvariantsTest.java`) | FR-540 |
| TPR-UNR-05 | Trade menus under the L1 key `warehouse_trade`, or a trade L2 with more than 8 leaves | `warehouse_trade` is retired with the Trade Portal (`REM-D21`, `WH-SC-662`); trade owns its own L1 `warehouse_purchase_sales` (*Purchase & Sales*) with six L2 sections of ≤ 8 leaves, so `warehouse_operations` keeps its 10-section cap | FR-540 (`TRD-07`) |

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from | Source |
|---|---|---|---|---|
| TPR-T2-01 | Add / edit | `:create` / `:edit` (own or department scope) | `DRAFT`, `REJECTED` | FR-556 |
| TPR-T2-02 | Submit / withdraw | `:submit` | `DRAFT`, `REJECTED` / `SUBMITTED` | FR-551 |
| TPR-T2-03 | Approve | `:approve` via `TAM` | `SUBMITTED` | FR-558 |
| TPR-T2-04 | Allocate | `wht_requisition_allocations:create` | `APPROVED`, `PARTIALLY_ORDERED` | FR-559, FR-560 |
| TPR-T2-05 | Cancel / close short | `:cancel` | per `-08`, `-09` | FR-561 |
| TPR-T2-06 | Print PR | `:view` | any numbered | FR-615 |
| TPR-T2-07 | Export | `:export` | — | FR-616 |
| TPR-T2-08 | Every action in this table, and the auditor | `wht_<table>:<verb>` per FRD-TRADE FR-617 (`view`, `create`, `edit`, `export` + the workflow verbs above); `permission_dependencies` seeded; the auditor bundle holds `:view` only; record scope follows core's company / site grants; a bundle whose action calls a core port is also granted `warehouse:orders:port` in the trade seed | — | FR-617 |

## 3. T3 — Time-driven rules

| ID | Rule | Trigger | Changes | Notified | Job | Source |
|---|---|---|---|---|---|---|
| TPR-T3-01 | PR ageing | approved line open > `warehouse.trade.pr.ageing_days` (default 7) | none (computed filter `ageingOnly`, report FR-619) | buyers of the site, daily digest `TRADE_PR_AGEING` | `TradePrAgeingJob` | FR-619 |
| TPR-T3-02 | Required date passed while open | `required_date < today` | `overdue` computed | requester + buyers, `TRADE_PR_OVERDUE`, once per line | same | FR-556 |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in | Source |
|---|---|---|---|---|
| TPR-T4-01 | Allocation created / released | line `allocated_quantity`, `line_status`, header status recomputed in the same transaction; the requester is notified `TRADE_PR_CONVERTED` on each allocation to a PO / release line (FR-560) | `RequisitionAllocationService` | FR-560 |
| TPR-T4-02 | PR line created from a suggestion / that line cancelled, deleted with its draft, or closed short unallocated | `WhReplenishmentSuggestionPort.markConverted(suggestionId, 'PURCHASE_REQUISITION', prId, pr_number or DRAFT ref)` / `releaseConversion(suggestionId, prId, reasonCodeId)` (`POS-T1-33`, `-35`) in the same transaction, keys `WHT_PURCHASE_REQUISITION:<prId>:SUGGESTION_CONVERT\|SUGGESTION_RELEASE:<line id>`; a material-requisition shortfall shows *requisitioned by PR-x* through core's `PurchaseRequisitionHandoff.status` read | `PurchaseRequisitionService` (port adapter) | FR-557 |
| TPR-T4-03 | Target RFQ line not awarded / PO line cancelled / reduced / **PO release line** rejected or returned (`TPO-T1-10a`), cancelled before approval (`TPO-T1-10b`) or cancelled for its unreceived part after it (`TPO-T1-10c`) — the release-line allocation (`target_type PO_RELEASE_LINE`) is released for the quantity that leaves the release (R31 F-TR-014) | allocation released back (`TPR-T1-07`) | target service calls `RequisitionAllocationService.release` | FR-561 |
| TPR-T4-04 | Line saved without estimate | estimate = rate-contract price (`trade-rate-contract` `TRC-T4-02`) else last approved PO rate, source stored | `PurchasePriceResolutionService` (reference mode) | FR-558 |

## 5. T5 — Screen contract

### 5.1 WS-286 Purchase Requisitions (reference **Service Vehicle**)
Grid `wht_purchase_requisitions`, scope `WAREHOUSE_TRADE_PURCHASE_REQUISITION`. Default sort
`e.created_at DESC`. Tiles: `DRAFT`+`REJECTED`, `SUBMITTED`, `APPROVED` (open), `PARTIALLY_ORDERED`,
overdue. Columns: `prNumber`, `warehouseName`, `departmentName`, `costObjectLabel`, `requestedByName`
(user display helper), `requiredByDate` (date-only → `formatDateSync`), `priority`, `source`, `lineCount`,
`estimatedValue`, `status`, audit. Filters: `warehouseId` → `departmentId`; `status`; `source`;
`requestedBy` typeahead; `requiredFrom`/`requiredTo` (`DateRangePicker`); `overdueOnly`. Row actions:
View · Edit · Submit · Withdraw · Cancel · Close short · Print. Toolbar: Add · Import shortages (`TPR-T1-02`) ·
Export. Modal tabs: Header · Lines · Approvals. `estimatedValue` is in the company currency (FR-558), so the
tiles are counts.

### 5.2 WS-287 Requisition Workbench
Grid `wht_requisition_open_lines` (approved PR lines with open quantity), scope
`WAREHOUSE_TRADE_REQUISITION_WORKBENCH`, default sort `e.required_date ASC`; `grid_preferences` default
columns = all below except `itemName`, default filters `warehouseId`, `itemId`, `requiredFrom`/`To`. Columns:
`prNumber`, `lineNo`, `itemCode`, `itemName`, `openQuantity`, `uom`, `requiredDate` (date-only),
`warehouseName`, `lineStatus` (`OPEN` / `IN_RFQ` / `PARTIALLY_ORDERED`), `suggestedSupplierName`,
`rateContractSupplierName`, `estimatedRate`, `ageDays`, audit. Filters: `warehouseId`, `itemCategoryId`,
`itemId`, `suggestedSupplierId`, `lineStatus`, `requiredFrom`/`To`, `ageingOnly`. Tiles: open lines, overdue
lines, in RFQ, ageing beyond `pr.ageing_days`, lines with a rate-contract supplier. Multi-select actions:
Create RFQ · Create PO (type picker) · Add to release (agreement picker) — each opens a modal showing per-line
quantity to allocate (defaults to open). Empty state: *No approved requisition lines are waiting.* No export of
selection; grid export allowed (⊇ grid, incl. `createdByName` / `updatedByName`).

## R32 additions (PRD 2026-10-24, `D-20`)

Rows added by the R32 fold (FRD-TRADE §4.15). Numbers continue each kind's sequence; where a number exists on one side of the purchase / sales mirror only, the asymmetry is stated in FRD-TRADE §5 rows M35…M40.

| ID | Kind | Rule | Refusal / effect | Source |
|---|---|---|---|---|
| TPR-GRD-09 | guard | Submit: `purpose_code` (`trade_pr_purpose`) set; `PRODUCTION_ORDER` → cost object `PRODUCTION_ORDER`; `SALES_ORDER` → `sales_order_id` of an `APPROVED`/`ISSUED` SO of the same company (`sales_order_ref` frozen); MR hand-off maps the MR purpose one-to-one | `422 TRADE_PR_PURPOSE_REFERENCE_REQUIRED {purpose}` | FR-741 |
| TPR-T4-05 | effect | PR line and WS-287 rows read on hand and free stock (`WhAvailableToPromiseQuery.atp(site, item)`) and the last approved PO rate (PO no, date) at query time; never stored; blank without the core site scope | — | FR-742 |
| TPR-T1-11 | transition | Rule level 1 `DEPARTMENT_HEAD` approved, later level pending → derived **`HOD_APPROVED`**; final → `APPROVED` (*Purchase approved*); MR hand-off PRs carry condition `from_approved_mr` | rejection shows the rejecting level | FR-743 |
| TPR-T3-03 | time | `TradeAutoPrDraftJob` every `warehouse.trade.pr.auto_draft_interval_minutes` (60), service principal: open core suggestions of origin in `warehouse.trade.pr.auto_draft_sources` (`REORDER,MRP`) → `DRAFT` PRs per site × required week, department `warehouse.trade.pr.auto_draft_department_code` (`STORES`), `auto_drafted = true`, each suggestion `markConverted`; never submits; notifies `TRADE_PR_AUTO_DRAFTED` | a suggestion already linked is skipped (`TPR-GRD-02`) | FR-744 |
| TPR-T1-02b | transition | MR hand-off one press: `TPR-T1-02a` also submits the PR when `warehouse.trade.pr.mr_handoff_auto_submit` = true (default), maker = the stores user | submit guards as `TPR-T1-03` | FR-744 |
| TPR-GRD-10 | guard | Replaces `TPR-GRD-04`'s bound: Σ active allocations + new ≤ (quantity − closed_short) × (1 + `warehouse.trade.pr.over_allocation_pct` ÷ 100) (default 0); any excess over the balance needs `wht_purchase_orders:exceed_pr`, is stored as `excess_quantity` and sets PO condition `exceeds_pr`; audited `TRADE_PR_EXCEEDED` | `422 TRADE_ALLOCATION_EXCEEDS_OPEN {open, tolerancePct}`; `403 TRADE_EXCEED_PR_NOT_PERMITTED` | FR-745 |

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
| 2026-10-22 | §0, §1.1, `TPR-T1-02`, `-02a`, `-04`, `-05`, `-08`…`-10`, `TPR-UNR-03`, T3, `TPR-T4-01`, `-02`, §5 | R29 TP-F5, F13, F18, F26, F28, F29: header close whatever the allocation, core hand-off row (created submitted, issued number), `releaseConversion`, `IN_RFQ`, conversion notification, workbench grid contract, *Import shortages* on WS-286 | R29 |
| 2026-10-23 | every T1, guard, unreachable, T3 and T4 row | `Source` column added, filled from FRD-TRADE §4, so every rule traces to the FR it proves | R30 `CP-FR-008` |
| 2026-10-23 | `TPR-GRD-07`, `-GRD-08`, `-UNR-05`, `-T4-03`, `TPR-OPEN-02`, `-03`, every T2 row | R31: `WhReplenishmentSuggestionPort` optional (F-TR-020); release-line allocations released (F-TR-014); `TPR-UNR-05` cites FR-540 (F-TR-019); `TPR-OPEN-02`, `-03` settled (`409 CONCURRENT_MODIFICATION`) | R31 |
| 2026-10-25 | `TPR-GRD-09`, `TPR-T4-05`, `TPR-T1-11`, `TPR-T3-03`, `TPR-T1-02b`, `TPR-GRD-10` (new, *R32 additions*) | R32 fold of the client PRD (`D-20`): PR purpose + SO reference, current stock, HOD → Purchase statuses, auto-drafted PRs, one-press MR hand-off, PO over PR balance with `exceed_pr` and tolerance (default 0; `TPR-GRD-04` bound replaced by `TPR-GRD-10`) | R32 / `D-20` |

## 8. Invariants and scenarios

`WH-SC-496`…`WH-SC-504`, `WH-SC-488`, `WH-SC-574`.

## 9. Open rows

| ID | Question | Status |
|---|---|---|
| TPR-OPEN-01 | Does core render a *Raise PR* action on its MR / suggestion screens when trade is enabled? A core screen cannot import trade code | **Settled by STORES:** core needs no trade import — `p8-09` offers *Send to purchasing* only when trade registers the optional `PurchaseRequisitionHandoff` bean (`FR-528`; trade's side is `TPR-T1-02a`), and `p8-16` withdraws core's *Convert to PO* when trade registers `SuggestionConversionOwner`; trade's WS-286 *Import shortages* also lists core shortages (read down) |
| TPR-OPEN-02 | `OD-31` MRP path | **Settled (R31 decisions):** default stands — seam published by `p8-16` (origin `MRP`, `markConverted`); MFG has confirmed it (FRD-MFG `OD-41`, `OD-44`) |
| TPR-OPEN-03 | `FR-618` says a stale `version` write is refused `409` but names no code, and the trade contracts need one exact code for the reviewer to check (`TAM-GRD-10`, `TCE-GRD-08`, `TPR-GRD-08`, `TRA-GRD-11`, `TRC-GRD-06`, `TSQ-GRD-08`, `TSR-GRD-06`) | **Settled (R31 decisions):** `409 CONCURRENT_MODIFICATION`, the code the MFG contracts already use (`PRO-GRD-21`, `PRC-GRD-18`) |
