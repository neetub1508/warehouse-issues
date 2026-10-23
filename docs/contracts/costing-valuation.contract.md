# Functional Contract — Costing and valuation: cost layers, methods, landed cost, revaluation, NRV, COGS point

> **What this is.** The functional truth for how warehouse **computes and holds cost**: cost layers with a
> consumption table, the valuation methods and the declared grain, the moving-average snapshot, the
> currency on the layer, landed cost, revaluation, the NRV register, the COGS recognition point and the
> second (tax) basis. It is the cost half of `D-6`. The handover of the computed value to accounting — the
> envelope, the queue, WS-219 — is [`accounting-handover`](accounting-handover.contract.md) and is **not
> restated here**; a row that meets the seam points at an `AHO-*` row.
>
> **Status.** Derived 2026-10-23 (v0) from `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` §6.13 (`FR-230`,
> `FR-234`…`FR-241`, `FR-243`, `FR-245`, `FR-250`) and verified against the built code in `classic`
> (`warehouse-base`, `warehouse`). Not ratified. Written for R30 `CP-FR-007` row 12 / `D-17` item 1.

---

## 0. Identity

| | |
|---|---|
| **Workflow** | A stock-moving post → the costing engine (inside the single writer's transaction) creates or consumes layers and returns each line's unit and extended cost → the value rides the movement. Value-only documents (landed cost, revaluation, NRV write-down) post a zero-quantity, non-zero-value movement and restate an open layer's value. COGS is recognised at the configured point |
| **Module** | `warehouse-base` (`ai.warehousebase.service.costing.WhbCostingEngine`, `WhbCostLayerMath`; WS-049, WS-050) + `warehouse` (WS-147, WS-148, WS-149, the COGS recognition rows, WS-211) + `warehouse-india` (the tax basis, `FR-250`, not built) |
| **Domain baseline** | `D-6`, `D-7`, `OD-1`, `OD-6`, `OD-16`, `L-2`, `L-14` · `RF-001`, `RF-002`, `RF-004`, `RF-006`, `RG-005`, `RG-019`, `RJ-010` · [`accounting-handover`](accounting-handover.contract.md) `AHO-UNR-01`…`-03`, `AHO-UNR-07`, `AHO-X-09` · [`movement-post-reverse`](movement-post-reverse.contract.md) (the single writer) |
| **Owning tasks** | `issues/p0-12.md` (authority rule, seam) · `issues/p2-16.md` (engine, layers, methods) · `issues/p2-17.md` (landed cost, revaluation) · `issues/p5-16.md` (NRV, COGS point) · `issues/p4-11.md` (tax basis) |
| **Primary tables** | `whb_valuation_policies`, `whb_cost_layers`, `whb_cost_layer_consumptions` (`V500021`, currency corrected `V500023`), `whb_cost_layer_value_restatements`; `whb_stock_movement_lines.moving_average_after` (`V501122`); `wh_landed_cost_documents`, `wh_landed_cost_allocations`, `wh_revaluations`, `wh_revaluation_lines` (`V510080`); `wh_nrv_assessments`, `wh_nrv_assessment_lines`, `wh_cogs_recognition_policies`, `wh_cogs_recognitions` (`V510212`) |
| **Status columns** | `wh_landed_cost_documents.status` `DRAFT`/`APPLIED`/`REVERSED`/`CANCELLED` · `wh_revaluations.status` `DRAFT`/`APPROVED`/`REJECTED`/`POSTED`/`CANCELLED` · `wh_nrv_assessments.status` `DRAFT`/`POSTED`/`REJECTED` · `wh_cogs_recognitions.status` `IN_TRANSIT`/`RECOGNISED` — no value `CHECK` on the status columns (`D-10`) |
| **Permission resources** | `whb_cost_layers:{view,export}` · `whb_valuation_policies:{view,create,edit,export}` · `wh_landed_cost_documents:{view,create,edit,apply,export}` · `wh_revaluations:{view,create,edit,approve,export}` · `wh_nrv_assessments:{view,create,approve,reverse,export}` · `wh_cogs_recognitions:{view,recognise,export}` · `wh_rpt_valuation:{view,export}` (all read off the controllers' `@PreAuthorize`) |
| **Routes** | WS-049 `/warehouse/ledger/cost-layers` · WS-050 `/warehouse/masters/valuation-policies` · WS-147 `/warehouse/inventory/landed-costs` · WS-148 `/warehouse/inventory/revaluations` · WS-149 `/warehouse/inventory/nrv-assessments` · `/warehouse/inventory/cogs-recognitions` · WS-211 `/warehouse/reports/stock-valuation` · mobile: none (finance desk; `D-16` item 7) |
| **Contract version** | `v0 — 2026-10-23` |

### Acceptance checks

| # | Expects | Delivered by |
|---|---|---|
| A1 | Warehouse computes cost; accounting posts what it is handed and never re-costs (`WH-SC-032`, `WH-SC-062`, `WH-SC-157`) | `CVL-GRD-01`, `CVL-UNR-01` |
| A2 | Layers + consumption; a matched return restores the original layers (`WH-SC-149`, `WH-SC-152`) | `CVL-T4-01`, `-03` |
| A3 | AVCO and FIFO per category × site; specific identification for serial-controlled items; LIFO never (`WH-SC-150`, `WH-SC-161`) | `CVL-GRD-03`…`-05`, `CVL-UNR-02` |
| A4 | Moving average snapshotted, never restated by a backdated receipt (`WH-SC-148`, `WH-SC-151`) | `CVL-T4-05`, `CVL-UNR-03` |
| A5 | Landed cost splits layer / COGS; revaluation is a movement (`WH-SC-153`…`WH-SC-155`) | `CVL-T1-01`…`-08`, `CVL-T4-07`, `-08` |
| A6 | NRV is a register with a linked reversal; COGS point is a policy (`WH-SC-345`, `WH-SC-348`) | `CVL-T1-09`…`-12`, `CVL-T4-10` |

---

## 1. T1 — State machine

### 1.1 Status inventory

| Entity | Status | Reachable via | Exits via | Kind | Source |
|---|---|---|---|---|---|
| Cost layer | `is_open = true` | `CVL-T4-01` | `CVL-T4-02` (fully consumed) | active | FR-234 |
| Cost layer | `is_open = false` | `CVL-T4-02` | `CVL-T4-03` (a return re-opens it) | settled | FR-234 |
| Landed cost document | `DRAFT` | `CVL-T1-01` | `-02`, `-04` | initial | FR-238 |
| Landed cost document | `APPLIED` | `CVL-T1-02` | `-03` | active | FR-238 |
| Landed cost document | `REVERSED` / `CANCELLED` | `CVL-T1-03` / `-04` | none | **terminal** | FR-238 |
| Revaluation | `DRAFT` | `CVL-T1-05` | `-06`, `-07`, `-08` | initial | FR-240 |
| Revaluation | `APPROVED` | `CVL-T1-06` | `-08`, `-08a` | active | FR-240 |
| Revaluation | `POSTED` / `REJECTED` / `CANCELLED` | `-08a` / `-07` / `-08` | none | **terminal** | FR-240 |
| NRV assessment | `DRAFT` | `CVL-T1-09`, `-11` | `-10`, `-10a` | initial | FR-241 |
| NRV assessment | `POSTED` / `REJECTED` | `-10` / `-10a` | none (a `POSTED` write-down is reversed by a **new** linked row, `-11`) | **terminal** | FR-241 |
| COGS recognition row | `IN_TRANSIT` | `CVL-T1-12` | `-13` | active | FR-243 |
| COGS recognition row | `RECOGNISED` | `CVL-T1-12` (`DISPATCH`) / `-13` | none | **terminal** | FR-243 |

### 1.2 Transitions

| ID | From | Event | To | Guard | Actor | Side effects | Reason? | Source |
|---|---|---|---|---|---|---|---|---|
| CVL-T1-01 | — | Create landed cost document: charge kind, counterparty, amount, currency, **apportionment basis** (`VALUE`/`QUANTITY`/`WEIGHT`/`VOLUME`/`MANUAL`), receipt lines it loads | `DRAFT` | `CVL-GRD-08`, `-09` | `wh_landed_cost_documents:create` | number `LCD-…`; `grn_id` set only when exactly one GRN is loaded (`RG-019`) | no | FR-238, FR-239 |
| CVL-T1-02 | `DRAFT` | **Apply** | `APPLIED` | `CVL-GRD-08`…`-10` under the grain lock | `:apply` | `CVL-T4-07`; allocation rows stored with `quantity_remaining_at_apply`, `amount_to_layer`, `amount_to_cogs` | no | FR-238 |
| CVL-T1-03 | `APPLIED` | Reverse | `REVERSED` | `CVL-GRD-09a` | `:apply` | a mirror value-only movement; the allocation rows are kept | **yes** | FR-238 |
| CVL-T1-04 | `DRAFT` | Cancel | `CANCELLED` | — | `:edit` | nothing posted | **yes** | FR-238 |
| CVL-T1-05 | — | Create revaluation: site, owner, reason, lines (open cost layer, new unit cost) | `DRAFT` | `CVL-GRD-11` | `wh_revaluations:create` / `:edit` (maker only, `403 REVALUATION_NOT_MAKER`) | — | no | FR-240 |
| CVL-T1-06 | `DRAFT` | Approve | `APPROVED` | approver ≠ maker (`WhbMakerChecker`), else `403 REVALUATION_SELF_APPROVAL` | `:approve` | — | no | FR-240 — **see §10 row 2** |
| CVL-T1-07 | `DRAFT` | Reject | `REJECTED` | same | `:approve` | nothing posted | **yes** | FR-240 |
| CVL-T1-08 | `DRAFT` · `APPROVED` | Cancel | `CANCELLED` | — | `:edit` | nothing posted | **yes** | FR-240 |
| CVL-T1-08a | `APPROVED` | **Post** | `POSTED` | layer unchanged since approval, else `409 REVALUATION_LAYER_CHANGED` | `:edit` | `CVL-T4-08` | no | FR-240 |
| CVL-T1-09 | — | Create NRV write-down: item or lot, site, owner, assessed NRV, basis, note | `DRAFT` | `CVL-GRD-12`, `-13` | `wh_nrv_assessments:create` | — | no | FR-241 |
| CVL-T1-10 | `DRAFT` | Approve | `POSTED` | approver ≠ assessor, else `403 NRV_SELF_APPROVAL`; layers unchanged, else `409 NRV_LAYER_CHANGED` | `:approve` | `CVL-T4-09` | no | FR-241 — **see §10 row 3** |
| CVL-T1-10a | `DRAFT` | Reject | `REJECTED` | same | `:approve` | nothing posted | **yes** | FR-241 |
| CVL-T1-11 | — (original `POSTED`) | **Reverse** a write-down (the cause ceased) | new reversal row `DRAFT`, linked to the original | `CVL-GRD-14` | `:reverse` | approved through `-10`; posts the reversing movement | **yes** | FR-241 |
| CVL-T1-12 | — | A despatch posts | `RECOGNISED` (point `DISPATCH`) or `IN_TRANSIT` (point `DELIVERY`/`INVOICE`) | — | system (despatch post) | the point in force is **snapshotted** on the row; dispatch stock state `SOLD` / `IN_TRANSIT`, in-transit role `GOODS_IN_TRANSIT` | no | FR-243 |
| CVL-T1-13 | `IN_TRANSIT` | Delivery confirmed (row snapshotted `DELIVERY`) · invoice event (row snapshotted `INVOICE`, `PATCH /invoiced`) | `RECOGNISED` | invoice date not in the future and not before the dispatch, else `422 COGS_INVOICE_DATE_INVALID`; a `DELIVERY` row is never recognised by an invoice | system / `wh_cogs_recognitions:recognise` | — | no | FR-243 |

### 1.3 Guards

| ID | Predicate | Refusal | Backstop | Source |
|---|---|---|---|---|
| CVL-GRD-01 | **Authority rule.** The system authoritative for quantity is authoritative for cost: warehouse runs the costing engine and holds the layers; accounting receives valued movements and posts them; where warehouse is installed accounting's own costing and quantity balance stand down | — (architecture) | `WhbAccountingSeamContractTest` (`AHO-UNR-01`) | FR-230 |
| CVL-GRD-02 | Non-own stock is never valued: an owner whose type does not `posts_to_our_gl` carries `cost_basis = ZERO_BAILMENT` and no value; WS-211 values `HOUSE` stock only | — (no value computed) | `AHO-UNR-07` | FR-230 (`L-14`) |
| CVL-GRD-03 | Method resolution: the `whb_valuation_policies` row in force at `occurred_at` for the item's `STOCKING` category **at that instant**, most specific (category × site) first; no policy = AVCO; v1 costs `AVCO` and `FIFO` | `VALUATION_METHOD_NOT_SUPPORTED` for any other method (`WhbCostingEngine.java:773`) | `uk(company_id, category_id, warehouse_id, effective_from) NULLS NOT DISTINCT`; `409 VALUATION_POLICY_OVERLAP` | FR-235 (`RG-005`) |
| CVL-GRD-04 | Specific identification is **implied by serial control**, not a policy value: an item whose `serial_control_mode` is `RECEIPT`/`FULL` relieves from its own serial's layer; lot-tracked non-serial stock follows the category's method (a FIFO line naming a lot relieves in receipt order across the grain) | — | `SERIAL_LAYERED_MODES` | FR-235 (`RF-006`) |
| CVL-GRD-05 | Standard cost with purchase-price and usage variances is a v1.1 method | — | — | FR-235 — **see §10 row 1** |
| CVL-GRD-06 | The valuation grain is declared: `(company, owner, item, site)`; an inter-site transfer is valued at the **sending site's** cost | — | `chk_whb_valuation_policies_grain` (one legal value, `V500021:194`) | FR-236 |
| CVL-GRD-07 | A foreign-currency cost carries a positive `exchange_rate` (base units per one source unit); a base-currency cost carries rate 1 only; `unit_cost`/`layer_value` are stored in the company's base currency; a movement waiting for approval takes base-currency cost only; a company with no base currency and no platform default stores no cost | `422 EXCHANGE_RATE_REQUIRED` · `lines[i].exchange_rate` / `422 BASE_CURRENCY_REQUIRED` · `company_id` | `exchange_rate DECIMAL(19,8)` | FR-245 (`OD-16`, `RF-004`) |
| CVL-GRD-08 | Landed cost: the basis is one of the five and is read from the receipt side; lines are posted receipt lines, unique; basis quantities non-zero | `422 LANDED_COST_BASIS_INVALID` / `_BASIS_MISSING` / `_BASIS_ZERO` / `_LINE_INVALID` / `_LINE_DUPLICATE` / `_NOT_WHOLE`; the charge kind is an active code and the counterparty valid (`LANDED_COST_CHARGE_KIND_INVALID`, `LANDED_COST_COUNTERPARTY_INVALID`, `WhLandedCostValidationService.java:54`, `:69`); the receiving location resolves (`LANDED_COST_LOCATION_MISSING`, `WhLandedCostPostingService.java:380`) | `CHECK (apportionment_basis IN (…))` `V510080:104` | FR-238, FR-239 |
| CVL-GRD-09 | Apply and edit only from `DRAFT`; the receipt movement is posted and its layer exists | `409 LANDED_COST_STATUS` / `422 LANDED_COST_MOVEMENT_NOT_POSTED` / `LANDED_COST_LAYER_MISSING` | — | FR-238 |
| CVL-GRD-09a | **Reverse** only from `APPLIED`, and only while **no loaded layer has been issued since apply** — a layer consumed after apply is corrected with a revaluation instead; Apply refuses a consumed layer the same way | `409 LANDED_COST_STATUS` (`WhLandedCostValidationService.java:147`); `409 LANDED_COST_LAYER_CONSUMED` (`WhLandedCostPostingService.java:320-339`, *"Correct it with a revaluation instead"*) | — | FR-238 |
| CVL-GRD-10 | A consumed share goes to cost of sales only when the consumption was a sale; a non-sale consumption (transfer, receipt reversal) is refused | `422 LANDED_COST_NON_SALE_CONSUMPTION` | `NON_SALE_MOVEMENT_TYPES` | FR-238 |
| CVL-GRD-11 | Revaluation line: the layer exists, is open with stock, belongs to the document's site and owner, is on the document once, and the new unit cost changes its value | `422 REVALUATION_LAYER_INVALID` / `REVALUATION_LINE_DUPLICATE` / `REVALUATION_NO_CHANGE` · `lines[i]` | — | FR-240 |
| CVL-GRD-12 | NRV: owner type is own; assessed NRV is below carrying value; basis active; note when the basis requires it; caller holds the cost view and the site | `422 NRV_OWNER_NOT_OWN` / `NRV_NOTHING_TO_WRITE_DOWN` / `NRV_BASIS_INVALID` / `NRV_NOTE_REQUIRED` · `403 NRV_COST_VIEW_REQUIRED` / `NRV_SITE_NOT_PERMITTED` | — | FR-241 |
| CVL-GRD-13 | NRV lot scope: a FIFO pool and a lot on one assessment never overlap; the lot scope did not change between create and approve | `422 NRV_POOL_LOT_OVERLAP` / `409 NRV_LOT_SCOPE_CHANGED` | — | FR-241 |
| CVL-GRD-14 | Reversal: only a `POSTED` write-down, once, and the new NRV is above the written-down value | `409 NRV_NOT_REVERSIBLE` / `NRV_ALREADY_REVERSED` · `422 NRV_REVERSAL_NRV_NOT_ABOVE` | — | FR-241 |
| CVL-GRD-15 | COGS point: `warehouse.cogs.recognition_point` (`DISPATCH`/`DELIVERY`/`INVOICE`), a site override in `wh_cogs_recognition_policies` beating it; missing or unknown = `DISPATCH` (logged) | — | `chk_wh_cogs_recognition_policies_point` | FR-243 |
| CVL-GRD-16 | The tax basis is a **second basis** over the configured book method, never a third method; the two are never summed; non-own stock carries neither | — | — | FR-250 — **not built, §10 row 4** |
| CVL-GRD-17 | Every movement carries `handover_id` and `posting_status` (`NOT_APPLICABLE` default, `PENDING`, `POSTED`, `REJECTED`); the **rejected-handover queue** (WS-052) shows each row's owner (the requester) and age, and raises `WHB_ACCOUNTING_HANDOVER_QUEUE_ALERT` once per breach of `warehouse.accounting.handover.rejected_queue_threshold` (default 10) to the WS-069 recipients | — | `V500030:242-244`, partial index `:306-307`; `V501071`; `WhbAccountingHandoverQueueAlertService` | FR-232 |
| CVL-GRD-18 | **Cut-off** is answered by three columns and the owner: `invoice_matched` on the receipt (goods received not invoiced), `ownership_transfer_point` on the **purchase order**, the receipt and the transfer (goods in transit under the Incoterm), and `owner_id` (consignment) | — | `V510011` (`WhPurchaseOrder.java:178`); `V510014:155-156`; `V510031:117` | FR-242 |
| CVL-GRD-19 | An inter-branch transfer carries **two numbers**: `transfer_price` under `transfer_price_basis` (the tax document) and `cost_value` (what follows the goods); `transfer_price − cost_value` inside one company is the unrealised profit to eliminate | `chk_wh_transfer_orders_transfer_price`, `_cost_value` (≥ 0); a price needs a basis | `V510031:111-145` | FR-244 |
| CVL-GRD-20 | **Stock periods are separate from accounting periods and close earlier**; a stock period cannot be reopened under a closed accounting period | `409 PERIOD_ACCOUNTING_CLOSED` (`WhbStockPeriodValidationService.java:253`) | `WhbAccountingPeriodLockProvider` | FR-251 — **see §10 row 7** |

### 1.4 Unreachable

| ID | Must never happen | Why it cannot | Source |
|---|---|---|---|
| CVL-UNR-01 | A re-costing step on the receiving side, or accounting computing value | `AHO-UNR-03`; the envelope carries the stored decimal | FR-230 |
| CVL-UNR-02 | `LIFO` as a method value, in the dropdown, the schema or the mobile schema | method refused (`CVL-GRD-03`); the screen states why (Ind AS 2 / IAS 2, ICDS II) | FR-235 |
| CVL-UNR-03 | An `UPDATE` of a written `moving_average_after`, or a backdated FIFO layer re-drawing an existing consumption | `I-2` refuses every `UPDATE` to `whb_stock_movement_lines`; consumptions are append-only | FR-237 |
| CVL-UNR-04 | A write to `whb_cost_layers.unit_cost` after insert | `restateLayerValue` changes `layer_value` only and records a dated `whb_cost_layer_value_restatements` row (`WhbCostingEngine.java` §restateLayerValue) | FR-240 |
| CVL-UNR-05 | A cost column on a balance as the source of value | value is read from layers / consumptions only | FR-234 |
| CVL-UNR-06 | An apportionment basis column on a freight, carrier or charge object other than `wh_landed_cost_documents` | `V510080:662` asserts none exists | FR-239 |
| CVL-UNR-07 | An NRV reversal that edits its original | the reversal is a new linked row; neither edits the other | FR-241 |
| CVL-UNR-08 | A report total across the book and tax bases | `CVL-GRD-16` | FR-250 |

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from | Source |
|---|---|---|---|---|
| CVL-T2-01 | View / export cost layers (read-only; a layer is never edited) | `whb_cost_layers:view` / `:export` | — | FR-234 |
| CVL-T2-02 | Add / edit / end-date a valuation policy | `whb_valuation_policies:create` / `:edit` | — | FR-235 |
| CVL-T2-03 | Landed cost create / edit / apply / reverse / cancel | `wh_landed_cost_documents:create` / `:edit` / `:apply` / `:apply` / `:edit` | `DRAFT` / `DRAFT` / `DRAFT` / `APPLIED` / `DRAFT` | FR-238 |
| CVL-T2-04 | Revaluation create / edit / approve / reject / post / cancel | `wh_revaluations:create` / `:edit` / `:approve` / `:approve` / `:edit` / `:edit` | see §1.2 | FR-240 |
| CVL-T2-05 | NRV create / approve / reject / reverse | `wh_nrv_assessments:create` / `:approve` / `:approve` / `:reverse` | see §1.2 | FR-241 |
| CVL-T2-06 | Record an invoice event for COGS | `wh_cogs_recognitions:recognise` | `IN_TRANSIT` | FR-243 |
| CVL-T2-07 | Run / export WS-211 | `wh_rpt_valuation:view` / `:export` | — | FR-230 |

## 3. T3 — Time-driven rules

| ID | Rule | Trigger | Changes | Source |
|---|---|---|---|---|
| CVL-T3-01 | Method in force is the policy effective at `occurred_at`; re-categorising an item changes the method for later movements and re-costs nothing posted | each post | the method used | FR-235 (`RG-005`) |
| CVL-T3-02 | A backdated receipt inserts a layer dated at its `occurred_at`; it is drawn only by issues posted after it | each post | — | FR-237 |
| CVL-T3-03 | The COGS point is read **live** at each despatch and snapshotted; changing the setting never restates a closed period | each despatch | — | FR-243 |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in | Source |
|---|---|---|---|---|
| CVL-T4-01 | An inbound line posts | a `whb_cost_layers` row: grain `(company, owner, item, site)` + lot, serial, `duty_status` (FK `whb_duty_statuses`), `quantity_in`, `quantity_remaining`, `unit_cost`, `layer_value`, `currency_code`, `exchange_rate`, `cost_basis` | `WhbCostingEngine.cost` in the writer's transaction | FR-234, FR-245 |
| CVL-T4-02 | An outbound line posts | consumption rows link the issue line to each layer drawn (FIFO: receipt order; AVCO: the open-layer average; serial: its own layer); a fully drawn layer closes | same | FR-234, FR-235 |
| CVL-T4-03 | A return posts | **matched**: its consumptions are reversed (`reversal_of_consumption_id`) and the original layers restored at their original cost; **unmatched**: a layer at the site's current method cost, `cost_basis = RETURN_UNMATCHED`, listed on WS-049; **return to vendor citing an origin GRN**: relieves that receipt's layer | same | FR-234 (`RJ-010`) |
| CVL-T4-04 | An issue finds no open layer (negative-stock policy `ALLOW`) | a negative layer `cost_basis = ESTIMATED`, unit cost from last receipt, else zero, source recorded; the covering receipt consumes it first and posts the difference as a value-only cost-variance movement | same | FR-234 (`RF-002`) |
| CVL-T4-05 | Any stock line posts | `moving_average_after` is written on the movement line; the current average is `Σ open layer_value / Σ open quantity_remaining`, computed on read | same | FR-237 (`RF-001`) |
| CVL-T4-06 | An inter-site transfer posts | the receiving site's layer carries the sending site's cost | same | FR-236 |
| CVL-T4-07 | Landed cost applied | one `LANDED_COST_APPLY` movement, zero quantity: two lines on an unconsumed layer, three on a partly consumed one; the consumed share posts at `VIRT-COST_OF_SALES-<site>`; the open layer's value is restated (`CVL-UNR-04`); split by largest remainder, ties by `line_no` | `WhLandedCostPostingService` → writer | FR-238 |
| CVL-T4-08 | Revaluation posted | one `REVALUATION` movement, zero quantity, non-zero value; the layer value restated; handed over per `AHO-X-09` | `WhRevaluationPostingService` → writer | FR-240 |
| CVL-T4-09 | NRV write-down / reversal posted | one `WRITE_DOWN` movement (reversal: the opposite value) linked to the assessment; the candidates (ageing, slow-moving, obsolete, damaged, expired) are supplied by warehouse as evidence | `WhNrvAssessmentPostingService` → writer | FR-241 |
| CVL-T4-10 | COGS recognised | the cost of goods sold is computed from warehouse's own consumptions and handed over valued (`AHO-X-09` shape); under `DELIVERY`/`INVOICE` the value sits in the in-transit role until the event | `WhCogsRecognitionService` | FR-243 |
| CVL-T4-11 | A valued movement is handed over | the envelope carries the value warehouse computed (`AHO-ENV-07`) | `WhbAccountingHandoverEmitter` | FR-230 |

## 5. T5 — Screen contract

| ID | Screen · grid · scope | Contract | Source |
|---|---|---|---|
| CVL-T5-01 | WS-049 Cost Layers (Customer ref.) · `whb_cost_layers` · `WAREHOUSE_COST_LAYER` | read-only; View drills into the consumptions (`whb_cost_layer_consumptions`) — which layer fed which issue; filter `hasRemaining` default **true**; `costBasis` filter lists `RETURN_UNMATCHED` and `ESTIMATED` — **not built** (§10 row 8); `layerDateFrom`/`To` `dateOnly` | FR-234 |
| CVL-T5-02 | WS-050 Valuation Policies (Department ref.) · `whb_valuation_policies` · `WAREHOUSE_VALUATION_POLICY` | Add / Edit / End-date; method select offers `AVCO`, `FIFO` only and states why LIFO is absent; footer names the grain | FR-235, FR-236 |
| CVL-T5-03 | WS-147 Landed Cost Documents · `wh_landed_cost_documents` · `WAREHOUSE_LANDED_COST_DOCUMENT` | the basis is chosen on the document from the receipt side; detail shows the stored allocation rows with the layer / COGS split | FR-238, FR-239 |
| CVL-T5-04 | WS-148 Revaluations · `wh_revaluations` · `WAREHOUSE_REVALUATION` | lines pick an open layer (`/layers`); actions Approve · Reject · Post · Cancel by state | FR-240 |
| CVL-T5-05 | WS-149 NRV Assessments · `wh_nrv_assessments` · `WAREHOUSE_NRV_ASSESSMENT` | the register shows a write-down and its reversal as two linked rows with assessor and date; **Candidates** tab (`/candidates`) drills to the producing position | FR-241 |
| CVL-T5-06 | WS-211 Stock Valuation (as-at) · `wh_rpt_valuation` · `WAREHOUSE_RPT_VALUATION` | totals in base currency, layer currency shown; `method` column; values own (`HOUSE`) stock only; `asAtDate` reproduces the same answer next year | FR-230, FR-245 |

## 6. Out of scope

The handover envelope, queue, period-close pre-check and WS-219 (`accounting-handover`); accounting's GL,
provisioning and the signed NRV judgement (the accounting set, deferred by `D-16` item 6); the WS-211 report
columns and filters as a report (`reports-kpis` §5).

## 7. Amendments

| Date | Change |
|---|---|
| 2026-10-23 | v0 derived (R30 `CP-FR-007` row 12) |
| 2026-10-23 | R31: `F-CB-007` (`CVL-GRD-09a` reverse guard; missing landed-cost codes on `CVL-GRD-08`); `F-CB-018` (§10 row 6 deleted as false, `CVL-GRD-18` corrected); `F-CB-012` (§10 row 8, `P2-16` acceptance item); `CVL-OPEN-01` decided, `-02`, `-03` deferred |

## 8. Invariants and scenarios

`L-2`, `L-14`, `D-6`; `WH-SC-032`, `WH-SC-062`, `WH-SC-127`, `WH-SC-148`…`WH-SC-155`, `WH-SC-157`,
`WH-SC-160`, `WH-SC-161`, `WH-SC-345`, `WH-SC-348`. `FR-250` has no scenario.

## 9. Open rows

| ID | Question | Default |
|---|---|---|
| CVL-OPEN-01 | `FR-240`/`FR-241` place revaluation approval and the NRV judgement with accounting; accounting is deferred (`D-16` item 6) and the built screens approve inside warehouse. Does warehouse approval stand as the standalone (`D-7`) stand-in, or must an accounting approval gate the post when accounting is installed? | **DECIDED R31 (2026-10-23): default stands for standalone** — warehouse maker-checker approval (`D-7`); whether an accounting gate applies when accounting is installed goes to accounting `P4-01` |
| CVL-OPEN-02 | `FR-250` asks a jurisdiction-specific tax basis; `p4-11.md` first asks whether it is derivable from v1 columns. Unanswered | **DEFERRED R31 (2026-10-23)**: carrier accounting-india / the accounting integration, with warehouse `P4-11`; the tax basis is a statutory valuation (India s.145A) — not built, not withdrawn |
| CVL-OPEN-03 | `FR-251` says the two period locks are synchronised; with accounting deferred (`D-16` item 6), who refuses an accounting close while the stock period is still open (§10 row 7)? | **DEFERRED R31 (2026-10-23)**: carrier accounting `P4-01`; the stock-side lock stands as built |

## 10. Code divergences

The FRD rule is kept; the code is what differs.

| # | File:line | FR | Difference |
|---|---|---|---|
| 1 | `warehouse-base/…/service/costing/WhbCostingEngine.java:773` | FR-235 | `STANDARD` is refused `VALUATION_METHOD_NOT_SUPPORTED`; standard cost with PPV / usage variance (v1.1) is not built, and the `ESTIMATED` chain skips standard cost |
| 2 | `warehouse/…/controller/WhRevaluationController.java:227` | FR-240 | approval is a warehouse verb (`wh_revaluations:approve`), not an accounting act |
| 3 | `warehouse/…/controller/WhNrvAssessmentController.java:252` | FR-241 | the write-down is approved and posted in warehouse (`wh_nrv_assessments:approve`); accounting owns NRV per the FRD |
| 4 | — (no `tax_basis` anywhere under `warehouse-base`, `warehouse`, `warehouse-india`) | FR-250 | the second, tax-basis value is not built |
| 5 | `warehouse-base/…/db/migration/V500042__Create_whb_accounting_handovers_and_gl_posting_rules.sql:49-54` | FR-232 | `posting_status` has no CHECK and also stores `BLOCKED` and `DISCARDED`, two values beyond the FR's four |
| 6 | *(deleted R31 `F-CB-018`: false divergence — `wh_purchase_orders.ownership_transfer_point` exists, `V510011`, `WhPurchaseOrder.java:178`)* | FR-242 | — |
| 7 | `warehouse-base/…/service/whbstockperiod/WhbStockPeriodValidationService.java:253` | FR-251 | only the stock side of the lock sync is enforced (reopen refused under a closed accounting period); nothing stops an accounting close while the stock period is open, because accounting is deferred (`D-16` item 6) |
| 8 | `warehouse-base/frontend/src/components/warehouseCatalogues/WhbCostLayerFilter.tsx`; `platform/frontend/src/utils/filterUtils.ts:1416-1421` (`WAREHOUSE_COST_LAYER`); `V501119` (`costBasis` seeded as a grid column only, `:254`) | FR-234 | the WS-049 `costBasis` filter (`CVL-T5-01`) is not built: no `filter_definitions` row, no allowlist key, no query binding, no filter control. `P2-16` owns it (acceptance item added) |
