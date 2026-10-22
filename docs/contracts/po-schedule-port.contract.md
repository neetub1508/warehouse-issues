# Functional Contract — PO type and schedule lines, the purchase-order port, and the demand-order port (sales mirror)

> **What this is.** The functional truth for the order **schema** core owns and the **ports** through
> which `warehouse-trade` creates and releases orders without writing `wh_` tables: PO type
> (`FIXED`/`OPEN`/`BLANKET_RELEASE`), schedule lines (firm/forecast), receipt allocation to schedule
> lines, the purchase-order port with idempotency and the change-guard seam, and the same for demand
> orders with a customer delivery schedule. It **extends** `RQP-T1-12`…`-15` (PO roll-up, close, cancel)
> and the demand ladder of `P2-08` — neither ladder changes.
>
> **What this is not.** Not the agreement, rate contract, RFQ, amendment approval or PO approval matrix —
> those are `warehouse-trade`'s (`FRD-TRADE`), which **calls** this port.
>
> **Status.** Derived 2026-10-22 (v0) from [`frd/FRD-STORES.md`](../frd/FRD-STORES.md) `FR-500`…`FR-506`,
> `STO-D1`, `STO-D2`. Not ratified.

---

## 0. Identity

| | |
|---|---|
| **Workflow** | PO create (manual or port) → schedule lines (firm/forecast) → release / firm → receipt allocated to firm lines → line/schedule roll-up → close; port amend / cancel schedule; demand order create (port) → customer schedule → firm-within-horizon allocation → despatch |
| **Module** | `warehouse` (core). Consumer: `warehouse-trade` (`ai.warehousetrade`) |
| **Domain baseline** | `FR-122`…`FR-124`, `FR-500`…`FR-506`, `RN-030`, `RN-053`, `D-16` item 5 (FKs down only) · the classic demand-order idempotency migration (W50 #244) (idempotency key + request fingerprint precedent on `wh_demand_orders`) · `PORT-AND-ADAPTER-CONTRACT.md` idempotency rules · outbox (`P0-11`) |
| **Owning tasks** | `issues/p8-01.md` (PO) · `issues/p8-02.md` (demand) · `issues/p8-15.md` (RMA port, supplier-return intent — §8a) · `issues/p8-16.md` (external replenishment suggestions — §8b) |
| **Primary tables** | ALTER `wh_purchase_orders` (`V510400`): `po_type`, `valid_from`, `valid_to`, `agreement_ref`, `source_module`, `source_document_type`, `source_document_id`, `source_document_ref`, `idempotency_key`, `request_fingerprint`, `revision_no`; ALTER `wh_purchase_order_lines`: `ordered_quantity` **nullable** (CHECK `ordered_quantity IS NULL OR ordered_quantity > 0`, replacing `chk_wh_purchase_order_lines_ordered`), `line_total` nullable, `rate_source`, `rate_source_ref`, `agreement_line_ref`, `scheduled_quantity` (Σ firm); new `wh_purchase_order_schedule_lines`, `wh_goods_receipt_line_schedule_allocations` (`V510400`). ALTER `wh_demand_orders` (`V510401`): `source_module`, `source_document_type`, `source_document_id`, `source_document_ref`, `sales_order_ref`, `customer_po_ref`, `customer_po_date`, `revision_no` (the the classic demand-order idempotency migration (W50 #244) `idempotency_key`/`request_fingerprint` are reused); new `wh_demand_order_schedule_lines` |
| **Status columns** | `wh_purchase_order_schedule_lines.status`, `wh_demand_order_schedule_lines.status` — no CHECK |
| **Permission resources** | existing `wh_purchase_orders:*`; the port runs as the calling user and requires `wh_purchase_orders:create`/`:edit` plus the module-to-module authority `warehouse:orders:port` (seed `V511400`) · `wh_demand_orders:*` likewise |
| **Routes** | WS-072/073 (changed), WS-275 PO Delivery Schedule, WS-276 Customer Delivery Schedule. Port: in-process Java interface **and** REST `/warehouse/ports/purchase-orders`, `/warehouse/ports/demand-orders` (same service) |
| **Contract version** | `v0 — 2026-10-22` |

### Acceptance checks

| # | Expects | Delivered by |
|---|---|---|
| A1 | Fixed, open (rate only) and blanket-release orders storable (`WH-SC-420`…`-422`) | `POS-T1-01`, `POS-GRD-01`…`-03` |
| A2 | Delivery schedule per line; only firm lines receivable; early delivery guarded (`WH-SC-421`…`-423`) | `POS-T1-03`, `POS-T4-02`, `POS-GRD-05`, `-06` |
| A3 | Trade creates/releases via an idempotent port and owns its POs (`WH-SC-424`, `-425`) | `POS-T1-05`…`-08`, `POS-GRD-07`, `-08` |
| A4 | Sales mirror: demand orders via port with a customer schedule; forecast never reserves (`WH-SC-426`) | `POS-T1-10`…`-12`, `POS-T4-05` |

---

## 1. T1 — State machine

### 1.1 Status inventory (additions)

| Entity | Status | Represented by | Reachable via | Exits via | Kind |
|---|---|---|---|---|---|
| PO schedule line | `OPEN` | `status`, `kind` (`FIRM`/`FORECAST`) | `POS-T1-02`, `-06` | `-03`, `-04`, `-09` | active (receivable only when `FIRM`) |
| PO schedule line | `PARTIALLY_RECEIVED` | `status` | `POS-T4-02` | `-03`, `-04` | active |
| PO schedule line | `RECEIVED` | `status` (received ≥ qty × (1 − short tol.)) | `POS-T4-02` | reversal regresses (`POS-T4-03`) | active |
| PO schedule line | `CLOSED` · `CANCELLED` | `status` | `-04`, `-09` / port cancel | none | **terminal** |
| PO header / line | unchanged ladders | `RQP` §1.1 | — | — | — |
| Demand schedule line | `OPEN` · `PARTIALLY_SHIPPED` · `SHIPPED` · `CANCELLED` | `status`, `kind` | `POS-T1-11`, effects | — | — |

Quantities on a PO schedule line: `scheduled_quantity`, `received_quantity`, `cancelled_quantity`
(`DECIMAL(18,4)`), `scheduled_date` (DATE), `kind`, `release_ref` (the buying module's release number).

### 1.2 Transitions

| ID | From | Event | To | Guard | Actor | Side effects | Reason? | UI |
|---|---|---|---|---|---|---|---|---|
| POS-T1-01 | — | Create PO with `po_type` | header `DRAFT` (manual) or the port's `initialStatus` `DRAFT`/`APPROVED` | `POS-GRD-01`…`-04` | `wh_purchase_orders:create` | `po_type` immutable thereafter | no | WS-072 **Add** (type select); port `createOrder` |
| POS-T1-02 | header `DRAFT` (manual) / any non-terminal (port) | Add schedule lines to a line | schedule `OPEN` | `POS-GRD-02`, `-03`, `-05` | `:edit` / port | line `scheduled_quantity` = Σ firm; `BLANKET_RELEASE` line `ordered_quantity` = Σ firm | no | WS-073 *Schedule* tab; port `releaseSchedule` |
| POS-T1-03 | schedule `OPEN` `FORECAST` | Firm it | `OPEN` `FIRM` | same | `:edit` / port | — | no | WS-073 / port |
| POS-T1-04 | schedule `OPEN`·`PARTIALLY_RECEIVED` | Close short | `CLOSED` | — | `:edit` / port | remainder → `cancelled_quantity`; the line's close rule (`RQP-T1-14`) re-evaluated | **yes** | WS-073 |
| POS-T1-05 | — | **Port create** with `(source_module, idempotency_key)` | as `-01` | `POS-GRD-07` | calling user + `warehouse:orders:port` | `source_*` recorded; when `initialStatus = APPROVED`, `approved_by` = `approvedByUserId` in the command (the trade approver), `submitted_at`/`approved_at` stamped; the `FR-408` check is the **source's** (trade approves) and core records `approval_source = SOURCE_MODULE` | no | none (port) |
| POS-T1-06 | non-terminal | **Port release** — add/firm schedule lines with `release_ref` | `OPEN` | `POS-GRD-05`, `-07` | port | outbox `WH_PO_SCHEDULE_RELEASED` | no | port |
| POS-T1-07 | non-terminal | **Port amend** — open lines' quantity / date / rate; add lines | unchanged; `revision_no` += 1 | `POS-GRD-09` | port | audit row with before/after per field | **yes** (`amendmentReason`) | port |
| POS-T1-08 | non-terminal | **Port close** (line or order) / **cancel** (order, `RQP-T1-15` cascade) | `CLOSED` / `CANCELLED` | `RQP-GRD-13`, `-14` | port | as `RQP-T1-14`/`-15` | **yes** | port |
| POS-T1-09 | schedule `OPEN` with 0 received | Port cancel schedule line | `CANCELLED` | — | port | — | **yes** | port |
| POS-T1-10 | — | **Demand port create** | demand `OPEN` | `POS-GRD-07`, `-10` | port | `source_*`, `sales_order_ref`, `customer_po_ref` recorded | no | port |
| POS-T1-11 | demand non-terminal | Demand release schedule (firm / forecast, requested date, qty) | schedule `OPEN` | `POS-GRD-10` | port | demand line `ordered_quantity` = Σ firm schedule | no | port; WS-276 read-only |
| POS-T1-12 | demand non-terminal | Demand amend / cancel line or schedule | per `P2-08` | `POS-GRD-09` (allocated/picked never reduced below) | port | reservations adjusted by `P2-07`'s release | **yes** | port |
| POS-T1-13 | any port-owned PO / demand | **Manual** edit / submit / approve / cancel / close from WS-072/073 or the outbound order screen | refused or allowed | every registered `PurchaseOrderChangeGuard` / `DemandOrderChangeGuard` is asked first | `:edit` etc. | — | — | the row shows a *Managed by warehouse-trade* banner; actions hidden when a guard would refuse |

### 1.3 Guards

| ID | Predicate | Refusal | Backstop | Source |
|---|---|---|---|---|
| POS-GRD-01 | `po_type ∈ {FIXED, OPEN, BLANKET_RELEASE}` | `422 PO_TYPE_INVALID` · `poType` | none (`D-10`) | FR-500 |
| POS-GRD-02 | `FIXED` line: `ordered_quantity > 0`; Σ schedule (any kind) = ordered when schedule lines exist. `OPEN` line: `ordered_quantity` null, `unit_price > 0`. `BLANKET_RELEASE`: `agreement_ref` on the header and `agreement_line_ref` on each line; ordered = Σ firm | `422 PO_LINE_QUANTITY_RULE` naming the rule | CHECK `ordered_quantity IS NULL OR ordered_quantity > 0` | FR-500, FR-502 |
| POS-GRD-03 | `valid_from ≤ valid_to`; `OPEN`/`BLANKET_RELEASE` need `valid_to` | `422 PO_VALIDITY_INVALID` | CHECK | FR-500 |
| POS-GRD-04 | `rate_source = AGREEMENT` ⇒ `rate_source_ref` set | `422 RATE_SOURCE_REF_REQUIRED` | CHECK | FR-501 |
| POS-GRD-05 | schedule date within `[valid_from, valid_to]` (when set) and ≥ order date | `422 SCHEDULE_DATE_OUT_OF_VALIDITY` | CHECK `scheduled_quantity > 0` | FR-502 |
| POS-GRD-06 | a receipt against a line that has schedule lines needs a `FIRM` `OPEN`/`PARTIALLY_RECEIVED` schedule line; earliest such line's `scheduled_date − early_delivery_days ≤ receipt date` when the setting is set; an `OPEN` PO with no firm line refuses; receipt after `valid_to` refuses | `409 NO_FIRM_SCHEDULE_OPEN` / `409 SCHEDULE_DELIVERY_TOO_EARLY` / `409 PO_VALIDITY_EXPIRED` · `lines[i].poLineId` | — | FR-503 |
| POS-GRD-07 | idempotency: `(source_module, idempotency_key)` unique where set; replay with the same SHA-256 fingerprint returns the original result; a different fingerprint refuses | `409 PORT_IDEMPOTENCY_CONFLICT` | partial uk + CHECK fingerprint `^[0-9a-f]{64}$` (the classic demand-order idempotency migration (W50 #244) shape) | FR-504 |
| POS-GRD-08 | manual change on a PO with `source_module` set is allowed only if every `PurchaseOrderChangeGuard` allows; with no guard registered (trade off) it is allowed | `409 PO_OWNED_BY_SOURCE_MODULE` (raised by trade's guard) | — | FR-504 |
| POS-GRD-09 | amend never sets a line/schedule quantity below received (PO) or allocated+picked+shipped (demand); never changes `po_type`, supplier, site, owner, currency | `422 AMEND_BELOW_RECEIVED` / `422 AMEND_FIELD_IMMUTABLE` | — | FR-504 |
| POS-GRD-10 | demand: `demand_type` in `DEMAND_TYPE`; customer counterparty for `SALES`; schedule dates ≥ order date | `422` field-named | composite FK | FR-505 |

### 1.4 Unreachable

| ID | Must never happen |
|---|---|
| POS-UNR-01 | a `wh_`/`whb_` FK to a `wht_` table, or core reading a `wht_` table |
| POS-UNR-02 | a receipt allocated to a `FORECAST` schedule line |
| POS-UNR-03 | a forecast demand schedule line reserving stock |
| POS-UNR-04 | `po_type` changed after create |
| POS-UNR-05 | a port call bypassing the PO/demand service (a direct repository write) |

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from | Extra |
|---|---|---|---|---|
| POS-T2-01 | Create PO with type | `wh_purchase_orders:create` | — | manual or port |
| POS-T2-02 | Edit schedule | `:edit` | header `DRAFT` (manual); non-terminal (port) | guards `POS-GRD-08` |
| POS-T2-03 | Close schedule line short | `:edit` | schedule open | reason |
| POS-T2-04 | Port calls | user perms + `warehouse:orders:port` | per row | trade only |
| POS-T2-05 | View schedules | `wh_purchase_orders:view` / `wh_demand_orders:view` | — | WS-275 / WS-276 |

## 3. T3 — Time-driven rules

| ID | Rule | Trigger | Changes | Notified | Job | Once? |
|---|---|---|---|---|---|---|
| POS-T3-01 | Schedule line **overdue** | `FIRM`, open qty > 0, `scheduled_date < today` (site TZ) | nothing — `overdueOnly` filter on WS-275, tile | buyer (PO `created_by`) | computed on read; weekly digest job `WhPoScheduleOverdueDigestJob` | once per line per week |
| POS-T3-02 | Agreement validity end | `valid_to < today` for an `OPEN`/`BLANKET_RELEASE` PO not terminal | receipts refused (`POS-GRD-06`); nothing else — close is explicit | buyer | computed | — |
| POS-T3-03 | Demand allocation horizon | firm demand schedule `requested_date ≤ today + warehouse.outbound.schedule_allocation_horizon_days` (default 7) | becomes allocatable (the allocator's candidate query) | — | `P2-07` allocation run | — |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in |
|---|---|---|---|
| POS-T4-01 | GRN line with `po_line_id` posts | quantity = `received − excess_refused` (`GBM-T4-01`) | GRN post |
| POS-T4-02 | same, line has schedule lines | allocate oldest `scheduled_date` first across `FIRM` open lines, each up to `scheduled − received − cancelled`, the remainder (excess) to the last allocated line; one `wh_goods_receipt_line_schedule_allocations` row per (GRN line, schedule line); schedule `received_quantity` and `status` recomputed (short-receipt tolerance applies per schedule line); then the PO line roll-up `RQP-T1-12` | GRN posting service, same transaction |
| POS-T4-03 | receipt reversal post | allocations of the GRN's lines reversed (rows kept, `reversed_at` stamped), schedule lines recomputed | reversal service |
| POS-T4-04 | any PO receipt, close, cancel, amend of a port-owned PO | outbox `WH_PO_LINE_RECEIVED` / `WH_PO_SCHEDULE_LINE_RECEIVED` / `WH_PO_CLOSED` / `WH_PO_CANCELLED` / `WH_PO_AMENDED` with `source_*` so trade updates drawn-down quantity | outbox |
| POS-T4-05 | demand despatch | demand schedule lines' shipped qty allocated oldest-first; outbox `WH_DEMAND_SHIPPED` with `sales_order_ref` | despatch service |
| POS-T4-06 | `RQP-T3-01` PO overdue | for a line with schedule lines, overdue reads the schedule lines, not `expected_delivery_date` | query |

## 5. T5 — Screen contract

### 5.1 WS-072 / WS-073 changes

- Grid gains `poType`, `validTo` (date-only), `agreementRef`, `sourceModule`, `nextScheduledDate`, `overdueScheduleCount`; filters `poType` (enum), `sourceModule`, `agreementRef` (text) — added to `COMMON_FILTER_CONFIGS.WAREHOUSE_PURCHASE_ORDER`.
- Add modal: **Type** first; `OPEN` hides line quantity; `BLANKET_RELEASE` requires agreement refs.
- WS-073 gains a **Schedule** tab per line: `scheduleNo`, `kind`, `scheduledDate`, `scheduledQuantity`, `receivedQuantity`, `cancelledQuantity`, `status`, `releaseRef`, overdue flag; actions Add · Firm · Close short (hidden when a change guard refuses).

### 5.2 WS-275 PO Delivery Schedule (reference: **Customer**)

Grid `wh_purchase_order_schedule_lines` · scope `WAREHOUSE_PO_SCHEDULE` · sort `e.scheduled_date ASC` · columns `poNumber`, `poType`, `supplierName`, `itemCode`, `itemName`, `scheduleNo`, `kind`, `scheduledDate`, `scheduledQuantity`, `receivedQuantity`, `openQuantity`, `status`, `releaseRef`, `daysOverdue`; filters site, supplier, item, `kind`, `status`, `scheduledFrom/To` (date), `overdueOnly`; export superset + audit names. A receiving clerk's *what is due this week* screen.

### 5.3 WS-276 Customer Delivery Schedule

Same shape over `wh_demand_order_schedule_lines`: `orderNumber`, `salesOrderRef`, `customerPoRef`, `customerName`, `item`, `requestedDate`, `kind`, `quantity`, `allocated`, `shipped`, `status`, `insideHorizon`.

## 6. Out of scope

Agreements, rate contracts, RFQ, amendment approval, PO approval matrix, vendor rating (`FRD-TRADE`); MRP-generated schedules (`FRD-MFG`); mobile.

## 7. Amendments

| Date | Change |
|---|---|
| 2026-10-22 | v0 derived |

## 8. Invariants and scenarios

`D-16` item 5; `L-1` untouched (no stock effect of a schedule); scenarios `WH-SC-420`…`-426`.

## 8a. RMA-creation port and supplier-return intent (`FR-506`, `P8-15`, TRADE `OD-33`)

| ID | From | Event | To | Guard | Actor | Side effects | Reason? | UI |
|---|---|---|---|---|---|---|---|---|
| POS-T1-20 | — | **Port `createRma`** | RMA `OPEN` (or `APPROVED` when `initialStatus = APPROVED`) | `POS-GRD-20`…`-22` | calling user + `warehouse:orders:port` + `wh_rmas:create` | `WhRmaService.create` (`:186`) then `approve` (`:234`) when asked; `source_*` recorded | no | none (port) |
| POS-T1-21 | RMA `OPEN`·`APPROVED` | **Port `cancelRma`** | `CANCELLED` | not `MATCHED` | port | `WhRmaService.cancel` (`:271`); outbox `WH_RMA_CANCELLED` | **yes** | port |
| POS-T1-22 | RMA any | *(effects)* match / expire | `MATCHED` / `EXPIRED` | — | core | outbox `WH_RMA_MATCHED` / `WH_RMA_EXPIRED` with `source_*` | — | none |
| POS-T1-23 | supplier return `DRAFT` | Set intent (`REPLACE`/`CREDIT`/`NO_ACTION`) | unchanged | active code-list row | `wh_supplier_returns:edit` | — | no | WS-084 |
| POS-T1-24 | supplier return `PICKED` | *(effect of despatch)* `DISPATCHED` | unchanged ladder | — | core | outbox `WH_SUPPLIER_RETURN_DISPATCHED` (intent, origin GRN/PO lines, PO `source_*`, item, lot, qty, movement id); **no PO change in core** | — | none |

| ID | Predicate | Refusal | Backstop |
|---|---|---|---|
| POS-GRD-20 | idempotency on `(source_module, idempotency_key)` with fingerprint | `409 PORT_IDEMPOTENCY_CONFLICT` | partial uk on `wh_rmas` |
| POS-GRD-21 | the original demand order is the same customer's, shipped; each line qty ≤ shipped − Σ live RMA lines for that demand line (lock) | `422 RMA_EXCEEDS_SHIPPED` · `lines[i].quantity` | — |
| POS-GRD-22 | manual change on a port-owned RMA allowed only if every `RmaChangeGuard` allows | `409 RMA_OWNED_BY_SOURCE_MODULE` | — |
| POS-GRD-23 | intent frozen once the return is `APPROVED` | `409 SUPPLIER_RETURN_INTENT_FROZEN` | — |

Unreachable: core reinstating PO quantity on a `REPLACE` dispatch (trade calls `amendOrder`/`releaseSchedule`); any financial document on `CREDIT` (`RN-054`). Scenarios `WH-SC-478`, `WH-SC-479`.

## 8b. External replenishment suggestions — the MRP supply seam (`FR-528`, SEAM-M3, `P8-16`; MFG `OD-41`, TRADE `OD-31`)

| ID | From | Event | To | Guard | Actor | Side effects | Reason? | UI |
|---|---|---|---|---|---|---|---|---|
| POS-T1-30 | — | **`publishExternal`** (origin `MRP`, origin run id, proposal id, item, site, qty, UoM, need date, preferred supplier?) | suggestion `PROPOSED` in a replenishment run of `run_type = EXTERNAL` (one run per publish call) | `POS-GRD-30`, `-31` | MFG port + `warehouse:orders:port` | `origin`, `origin_document_type = MRP_PROPOSAL`, `origin_document_id`, `need_date`; `on_hand`/`allocated`/`on_order` snapshotted from positions; `reorder_point` null; `basis_note` = *MRP run n, proposal m* | no | none (port) |
| POS-T1-31 | `PROPOSED` (origin `MRP`) | **`withdrawExternal`** (MRP re-run supersedes it) | `REJECTED` | not `ACCEPTED`/`CONVERTED` | port | reason `WITHDRAWN_BY_ORIGIN` | — | none |
| POS-T1-32 | `PROPOSED`/`ACCEPTED`, `suggested_source = PURCHASE`, **no `SuggestionConversionOwner` bean** (trade off) | Convert to draft PO (today's core path, `WhReplenishmentSuggestionService.java:287`) | `CONVERTED` | unchanged | `wh_replenishment_suggestions:edit` | `resulting_document_*` = the PO; outbox `WH_REPLENISHMENT_SUGGESTION_CONVERTED` | no | core replenishment screen |
| POS-T1-33 | same, **bean present** (trade on) | trade *Raise PR* (`FR-557`) calls `markConverted(suggestionId, PR ref)` | `CONVERTED` | not already converted | trade via port | `resulting_document_type = PURCHASE_REQUISITION`, ref; core's convert-to-PO not offered | no | trade screen |
| POS-T1-34 | any | `getSuggestionStatus(originDocumentId)` | — | — | port | returns status, accepted qty, resulting document (MFG `OD-44` cover rule) | — | — |

| ID | Predicate | Refusal |
|---|---|---|
| POS-GRD-30 | idempotent per `(origin, origin_document_id)`: a republish of the same proposal returns the existing suggestion; a changed qty on a `PROPOSED` one updates it, on a converted one refuses | `409 SUGGESTION_ALREADY_CONVERTED` |
| POS-GRD-31 | origin is an active `REPLENISHMENT_ORIGIN` row other than `REORDER`; item stocked at the site | `422` field-named |
| POS-GRD-32 | a suggestion is converted at most once (core PO **or** trade PR) | `409 SUGGESTION_ALREADY_CONVERTED` |

Schema (`P8-16`): `wh_replenishment_runs.run_type` CHECK widened with `EXTERNAL` (`run_by` = the publishing user); `wh_replenishment_suggestions` + `origin_list`/`origin` (default `REORDER`), `origin_document_type`, `origin_document_id`, `need_date`; `reorder_point` nullable with CHECK `origin <> 'REORDER' OR reorder_point IS NOT NULL`; partial uk `(origin, origin_document_id) WHERE origin <> 'REORDER' AND status <> 'REJECTED'`. `suggested_source` and its CHECK are untouched.

## 9. Open rows

| ID | Question | Default |
|---|---|---|
| POS-OPEN-01 | Should a manual (non-port) PO be allowed to be `BLANKET_RELEASE` when trade is off? | **No** — `BLANKET_RELEASE` requires `source_module`; without trade an install uses `FIXED`/`OPEN` |
| POS-OPEN-02 | Port transport: in-process only, or REST too? | both; trade in the same JVM uses the Java interface; REST exists for a remote buying system and requires `warehouse:orders:port` |
