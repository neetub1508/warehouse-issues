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
| **Primary tables** | ALTER `wh_purchase_orders` (`V511310`): `po_type`, `valid_from`, `valid_to`, `agreement_ref`, `source_module`, `source_document_type`, `source_document_id`, `source_document_ref`, `idempotency_key`, `request_fingerprint`, `revision_no`; ALTER `wh_purchase_order_lines`: `ordered_quantity` **nullable** (CHECK `ordered_quantity IS NULL OR ordered_quantity > 0`, replacing `chk_wh_purchase_order_lines_ordered`), `line_total` nullable, `rate_source`, `rate_source_ref`, `agreement_line_ref`, `scheduled_quantity` (Σ firm); ALTER `wh_purchase_orders` + `receipt_cutoff_date` (DATE, null = no cut-off; R29 TP-F15); new `wh_purchase_order_schedule_lines` (with `unit_price` DECIMAL(19,6) nullable — the release price, null = the line rate; `price_source_ref`; R29 TP-F14), `wh_goods_receipt_line_schedule_allocations` (+ `unit_price` frozen at allocation), and the port operation registry `wh_port_operations` (R29 F21) (`V511310`). ALTER `wh_demand_orders` (`V511311`): `source_module`, `source_document_type`, `source_document_id`, `source_document_ref`, `sales_order_ref`, `customer_po_ref`, `customer_po_date`, `revision_no` (the classic demand-order idempotency migration (W50 #244) `idempotency_key`/`request_fingerprint` are reused; its global partial uk `uk_wh_demand_orders_idempotency_key` (`V511303:51-52`, applied before every P8 file — R29 F2) is dropped and recreated on `(COALESCE(source_module, ''), idempotency_key)`); ALTER `wh_demand_order_lines` (`V511311`): + `is_schedule_driven BOOLEAN NOT NULL DEFAULT false`, `chk_wh_demand_order_lines_ordered` (`V510040:319`) replaced by `CHECK (ordered_quantity > 0 OR (is_schedule_driven AND ordered_quantity >= 0))` (R29 F3, TS-F1); `wh_demand_orders` + `is_schedule_driven`, `release_closed_at` (`OD-45`); new `wh_demand_order_schedule_lines` |
| **Status columns** | `wh_purchase_order_schedule_lines.status`, `wh_demand_order_schedule_lines.status` — no CHECK |
| **Permission resources** | existing `wh_purchase_orders:*` + new verb `wh_purchase_orders:release_schedule` (manual release / firm / close-short on an approved `OPEN` PO, R29 F6) · `wh_demand_orders:*` · `wh_rmas:*` · `wh_replenishment_suggestions:*`. **Port principal (R29 TP-F6):** every port call names `actingUserId`; core authorises that user — it must hold `warehouse:orders:port` **and** the operation's core verb (table in FRD-STORES *Port & seam registry*). Core seeds `warehouse:orders:port` (`V511400`) with `permission_dependencies` rows `warehouse:orders:port → wh_purchase_orders:{view,create,edit}`, `→ wh_demand_orders:{view,create,edit}`, `→ wh_rmas:{view,create,edit}`, `→ wh_replenishment_suggestions:{view,edit}`, `→ wh_material_requisitions:{view,create}` (granting the port authority grants the verbs it needs). The **sibling** grants `warehouse:orders:port` to its approver bundles in its own seed. A SYSTEM-approved trade document (zero-level release) calls the port with `actingUserId` = the trade document's submitter and `approvedByUserId` = null; core records `approval_source = SOURCE_MODULE`. A caller lacking the authority is refused `403 PORT_AUTHORITY_REQUIRED` and the sibling's transaction rolls back |
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
| POS-T1-02 | header `DRAFT` (manual, `:edit`); header `APPROVED`/`PARTIALLY_RECEIVED` of an `OPEN` PO (manual, `:release_schedule`, R29 F6); any non-terminal (port) | Add schedule lines to a line (optional `unitPrice` per schedule line, R29 TP-F14) | schedule `OPEN` | `POS-GRD-02`, `-03`, `-05`, `-08` (every `PurchaseOrderChangeGuard` asked for a manual call), `-12` | `:edit` / `:release_schedule` / port | line `scheduled_quantity` = Σ firm; `BLANKET_RELEASE` line `ordered_quantity` = Σ firm, **NULL while Σ firm = 0** (R29 TP-F1); audit row; outbox `WH_PO_SCHEDULE_RELEASED` | no | WS-073 *Schedule* tab; port `releaseSchedule` |
| POS-T1-03 | schedule `OPEN` `FORECAST` | Firm it | `OPEN` `FIRM` | same as `-02` | same as `-02` | as `-02` | no | WS-073 / port `releaseSchedule` (`firm` entry) |
| POS-T1-04 | schedule `OPEN`·`PARTIALLY_RECEIVED` | Close short | `CLOSED` | `-08` for a manual call | `:edit` (DRAFT) / `:release_schedule` (approved `OPEN`) / port | remainder → `cancelled_quantity`; the line's close rule (`RQP-T1-14`) re-evaluated | **yes** | WS-073 |
| POS-T1-05 | — | **Port create** with `(source_module, idempotency_key)` | as `-01` | `POS-GRD-07`, `-13` | calling user + `warehouse:orders:port` + `wh_purchase_orders:create` | `source_*` recorded; when `initialStatus = APPROVED`, `approved_by` = `approvedByUserId` in the command (the trade approver), `submitted_at`/`approved_at` stamped; the `FR-408` check is the **source's** (trade approves) and core records `approval_source = SOURCE_MODULE` | no | none (port) |
| POS-T1-06 | non-terminal | **Port release** — add/firm schedule lines with `release_ref`, optional `unitPrice` | `OPEN` | `POS-GRD-05`, `-07`, `-12` | port + `wh_purchase_orders:edit` | outbox `WH_PO_SCHEDULE_RELEASED`; operation row in `wh_port_operations` | no | port |
| POS-T1-07 | non-terminal | **Port amend** — open lines' quantity / date / rate; add lines | unchanged; `revision_no` += 1 | `POS-GRD-09` | port | audit row with before/after per field | **yes** (`amendmentReason`) | port |
| POS-T1-08 | non-terminal | **Port close** (`closeLine` / `closeOrder`) / **cancel** (`cancelOrder`, `RQP-T1-15` cascade) | `CLOSED` / `CANCELLED` | `RQP-GRD-13`, `-14`; `closeOrder` refuses `409 PO_HAS_DRAFT_RECEIPT` while a `DRAFT` GRN line references the PO | port + `:edit` | `closeOrder` (R29 TP-F22): every open schedule line → `CLOSED` with its remainder in `cancelled_quantity`, every open line closed (`RQP-T1-14`), header `CLOSED`, outbox `WH_PO_CLOSED`; a replay on a `CLOSED` order returns it (idempotent); the PO leaves the gate-entry PO picker (`GTE-GRD-01`) | **yes** | port |
| POS-T1-09 | schedule `OPEN` with 0 received | Port cancel schedule line | `CANCELLED` | — | port + `:edit` | line `scheduled_quantity` recomputed; outbox `WH_PO_AMENDED` | **yes** | port |
| POS-T1-10 | — | **Demand port create** (`createDemand`) | demand `OPEN` | `POS-GRD-07`, `-10` | port + `wh_demand_orders:create` | `source_*`, `sales_order_ref`, `customer_po_ref` recorded; a line sent with schedule lines is `is_schedule_driven = true` (and so is its order); a line with only `FORECAST` lines, or none (an `OPEN` SO), saves with `ordered_quantity = 0` (R29 F3, TS-F1) | no | port |
| POS-T1-11 | demand non-terminal (`OD-45`: a schedule-driven order is non-terminal until `release_closed_at` is set) | Demand release schedule (`releaseSchedule`: firm / forecast, requested date, qty, `release_ref`) | schedule `OPEN` | `POS-GRD-07`, `-10` | port + `wh_demand_orders:edit` | demand line `ordered_quantity` = Σ `FIRM` schedule `quantity` (cancelled firm quantity included, mirrored in the line's `cancelled_quantity`, so the partition CHECK `V510040:328-329` holds); a release onto a schedule-driven order resting in `OPEN` makes it allocatable; outbox `WH_DEMAND_AMENDED` | no | port; WS-276 read-only |
| POS-T1-11a | schedule `OPEN` `FORECAST` | **Firm** (`firmScheduleLine`, by `scheduleLineId` or `(demandLineId, releaseRef)`, R29 TS-F15) | `OPEN` `FIRM` | `POS-GRD-10` | port + `:edit` | line `ordered_quantity` += qty | no | port |
| POS-T1-11b | schedule `OPEN` `FIRM` with `allocated_quantity = 0` | **Un-firm** (`unfirmScheduleLine`) | `OPEN` `FORECAST` | allocated = 0, else `409 DEMAND_SCHEDULE_ALLOCATED` | port + `:edit` | line `ordered_quantity` −= qty (may reach 0 on a schedule-driven line) | **yes** | port |
| POS-T1-11c | schedule `OPEN` with nothing picked | **Cancel one schedule line** (`cancelScheduleLine`) | `CANCELLED` | picked = 0, else `409 DEMAND_SCHEDULE_PICKED`; a `FIRM` line's allocation is released first through `P2-07`'s release path | port + `:edit` | `FIRM`: schedule and line `cancelled_quantity` += qty; `FORECAST`: nothing else; the other schedule lines of the item line are untouched | **yes** | port |
| POS-T1-12 | demand non-terminal | Demand amend (`amendDemand`) / cancel item line (`cancelLine`) / cancel order (`cancelDemand`) | per `P2-08`; `cancelDemand` → `CANCELLED` (`P2-08` cascade) | `POS-GRD-09`, `-14` | port + `:edit` | reservations adjusted by `P2-07`'s release; outbox `WH_DEMAND_AMENDED` / `WH_DEMAND_CANCELLED` with `sales_order_ref` | **yes** | port |
| POS-T1-12a | schedule-driven order | **Close for release** (`closeDemand`, `OD-45`) | `release_closed_at` stamped; header follows the ordinary ladder from now on | — | port + `:edit` | every open `FORECAST` schedule line `CANCELLED`; an order with nothing left unshipped goes `SHIPPED` at once; outbox `WH_DEMAND_AMENDED` | **yes** | port |
| POS-T1-12b | schedule-driven order `PICKING`/`PACKED` | *(effect of despatch, `OD-45`)* every line fully accounted **but** `release_closed_at` is null | **`OPEN`** (not `SHIPPED`) | — | core | `last_shipped_at` stamped; outbox `WH_DEMAND_SHIPPED`; the order is never `SHIPPED`/`DELIVERED` while it can still take releases | — | none |
| POS-T1-13 | any port-owned PO / demand | **Manual** edit / release / submit / approve / cancel / close from WS-072/073 or the outbound order screen | refused or allowed | every registered `PurchaseOrderChangeGuard` / `DemandOrderChangeGuard` is asked first (`POS-GRD-08`, `-14`) | `:edit` etc. | — | — | the row shows a *Managed by warehouse-trade* banner; actions hidden when a guard would refuse |
| POS-T1-14 | any | **Line roll-up** (R29 F7) | line / header status recomputed | — | core | every reader uses `WhPurchaseOrderLine.effectiveOrderedQuantity()` = `ordered_quantity` for `FIXED`, `scheduled_quantity` (Σ firm) for `OPEN`/`BLANKET_RELEASE`; the line is `RECEIVED` when received ≥ effective × (1 − short tolerance) **and** it has no `OPEN` `FORECAST` schedule line; a later release re-opens it to `PARTIALLY_RECEIVED`; an `OPEN`/`BLANKET_RELEASE` header never rolls up to `RECEIVED` before `closeOrder` / manual close — it rests in `PARTIALLY_RECEIVED` | — | none |

### 1.3 Guards

| ID | Predicate | Refusal | Backstop | Source |
|---|---|---|---|---|
| POS-GRD-01 | `po_type ∈ {FIXED, OPEN, BLANKET_RELEASE}` | `422 PO_TYPE_INVALID` · `poType` | none (`D-10`) | FR-500 |
| POS-GRD-02 | `FIXED` line: `ordered_quantity > 0`; Σ schedule (any kind) = ordered when schedule lines exist. `OPEN` line: `ordered_quantity` null, `unit_price > 0` (a free-of-charge `OPEN` line is refused — `STO-D14`; trade refuses it at submit, R29 TP-F19). `BLANKET_RELEASE`: `agreement_ref` on the header and `agreement_line_ref` on each line; ordered = Σ firm, **NULL while Σ firm = 0**, so a blanket sent with only `FORECAST` lines saves (R29 TP-F1) | `422 PO_LINE_QUANTITY_RULE` naming the rule | CHECK `ordered_quantity IS NULL OR ordered_quantity > 0` | FR-500, FR-502 |
| POS-GRD-03 | `valid_from ≤ valid_to`; `OPEN`/`BLANKET_RELEASE` need `valid_to` | `422 PO_VALIDITY_INVALID` | CHECK | FR-500 |
| POS-GRD-04 | `rate_source = AGREEMENT` ⇒ `rate_source_ref` set | `422 RATE_SOURCE_REF_REQUIRED` | CHECK | FR-501 |
| POS-GRD-05 | schedule date within `[valid_from, valid_to]` (when set) and ≥ order date — `valid_to` is the **last release date**: no schedule line may be added or firmed for a date after it | `422 SCHEDULE_DATE_OUT_OF_VALIDITY` | CHECK `scheduled_quantity > 0` | FR-502 |
| POS-GRD-06 | a receipt against a line that has schedule lines needs a `FIRM` `OPEN`/`PARTIALLY_RECEIVED` schedule line; earliest such line's `scheduled_date − early_delivery_days ≤ receipt date` when the setting is set; an `OPEN` PO with no firm line refuses. **Firm released quantity stays receivable after `valid_to`** (R29 TP-F15): a receipt is refused only after `receipt_cutoff_date` when it is set (null = no cut-off; the port and WS-072 may set it ≥ `valid_to`) | `409 NO_FIRM_SCHEDULE_OPEN` / `409 SCHEDULE_DELIVERY_TOO_EARLY` / `409 PO_RECEIPT_CUTOFF_PASSED` · `lines[i].poLineId` | CHECK `receipt_cutoff_date IS NULL OR valid_to IS NULL OR receipt_cutoff_date >= valid_to` | FR-503 |
| POS-GRD-07 | idempotency (R29 F21): every port **write** carries `(sourceModule, idempotencyKey)`; core records one `wh_port_operations` row per call — `source_module`, `operation` (`PO_CREATE`, `PO_RELEASE`, `PO_AMEND`, `PO_CANCEL_SCHEDULE`, `PO_CLOSE_LINE`, `PO_CLOSE`, `PO_CANCEL`, `DEMAND_*`, `RMA_*`, `MRQ_*`, `SUGGESTION_*`), `idempotency_key`, `request_fingerprint` (SHA-256 of the canonical JSON body), `target_type`, `target_id`, `result_revision_no`, `result_code`, `created_at`, `created_by`; uk `(source_module, operation, idempotency_key)`. A replay with the same fingerprint returns the **recorded** result (target id, revision, code) without re-executing; a different fingerprint refuses. The create's key also stays on the header (`idempotency_key`, `request_fingerprint`, the W50 #244 shape) | `409 PORT_IDEMPOTENCY_CONFLICT` | uk on `wh_port_operations`; CHECK fingerprint `^[0-9a-f]{64}$` | FR-504 |
| POS-GRD-08 | manual change on a PO with `source_module` set is allowed only if every `PurchaseOrderChangeGuard` allows; with no guard registered (trade off) it is allowed | `409 PO_OWNED_BY_SOURCE_MODULE` (raised by trade's guard) | — | FR-504 |
| POS-GRD-09 | amend never sets a PO line/schedule quantity below received; never sets a demand line's `ordered_quantity` below `allocated_quantity + cancelled_quantity + backordered_quantity` (the quantities are cumulative — picked ⊆ allocated, shipped ⊆ picked — so adding them would double-count; this is the partition CHECK `V510040:328-329`, R29 F18); never changes `po_type`, supplier, **site**, owner, currency (`STO-D15`: a deliver-to change is a receiving location inside the same site; another site is cancel + new order, R29 TP-F24) | `422 AMEND_BELOW_RECEIVED` / `422 AMEND_BELOW_ALLOCATED` / `422 AMEND_FIELD_IMMUTABLE` | partition CHECK | FR-504 |
| POS-GRD-10 | demand: `demand_type` in `DEMAND_TYPE`; customer counterparty for `SALES`; schedule dates ≥ order date | `422` field-named | composite FK; CHECK `ordered_quantity > 0 OR (is_schedule_driven AND ordered_quantity >= 0)` | FR-505 |
| POS-GRD-11 | every `ordered_quantity` reader goes through `effectiveOrderedQuantity()` (`POS-T1-14`): `WhPurchaseOrderLineStatusService` (`:148-162`), `WhGoodsReceiptPostingService` tolerance (`:451-509`), `WhPurchaseOrderValidationService`, `WhPurchaseOrderMapper`, `WhPurchaseOrderExportService`, `WhOrderAmendmentRecorder`, `WhPurchaseOrderLine.outstandingQuantity()` | — (no null arithmetic) | — | FR-502 |
| POS-GRD-12 | a schedule line's `unit_price`, when set, is > 0 and in the PO currency; the GRN values each allocation at its schedule line's price (else the line rate) and the GRN line's unit cost is the allocation-weighted price (R29 TP-F14) | `422 SCHEDULE_PRICE_INVALID` · `scheduleLines[i].unitPrice` | CHECK `unit_price IS NULL OR unit_price > 0` | FR-501 |
| POS-GRD-13 | the acting user holds `warehouse:orders:port` and the operation's core verb (`POS` §0 principal row) | `403 PORT_AUTHORITY_REQUIRED` | `@PreAuthorize` on the REST mirror; service check in-process | FR-504 |
| POS-GRD-14 | manual change on a demand order with `source_module` set is allowed only if every `DemandOrderChangeGuard` allows; none registered → allowed (R29 TS-F25) | `409 DEMAND_OWNED_BY_SOURCE_MODULE` (raised by the guard) | — | FR-505 |

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
| POS-T2-02 | Edit schedule | `:edit` (`DRAFT`) · `:release_schedule` (approved `OPEN` PO, R29 F6) | header `DRAFT` or approved `OPEN` (manual); non-terminal (port) | guards `POS-GRD-08`; works with trade off (no guard registered) |
| POS-T2-03 | Close schedule line short | `:edit` | schedule open | reason |
| POS-T2-04 | Port calls | `warehouse:orders:port` + the operation's verb (`POS-GRD-13`) | per row | sibling modules only |
| POS-T2-05 | View schedules | `wh_purchase_orders:view` / `wh_demand_orders:view` | — | WS-275 / WS-276 |

## 3. T3 — Time-driven rules

| ID | Rule | Trigger | Changes | Notified | Job | Once? |
|---|---|---|---|---|---|---|
| POS-T3-01 | Schedule line **overdue** | `FIRM`, open qty > 0, `scheduled_date < today` (site TZ) | nothing — `overdueOnly` filter on WS-275, tile | buyer (PO `created_by`) | computed on read; weekly digest job `WhPoScheduleOverdueDigestJob` | once per line per week |
| POS-T3-02 | Agreement validity end | `valid_to < today` for an `OPEN`/`BLANKET_RELEASE` PO not terminal | **releases** stop (`POS-GRD-05`); firm released quantity stays receivable until `receipt_cutoff_date` (`POS-GRD-06`); close is explicit (`closeOrder`, which the buying module's auto-close job calls, R29 TP-F22) | buyer | computed | — |
| POS-T3-03 | Demand allocation horizon | firm demand schedule `requested_date ≤ today + warehouse.outbound.schedule_allocation_horizon_days` (default 7) | becomes allocatable (the allocator's candidate query) | — | `P2-07` allocation run | — |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in |
|---|---|---|---|
| POS-T4-01 | GRN line with `po_line_id` posts | quantity = `received − excess_refused` (free quantity excluded, as today; `GBM-T4-01`) | GRN post |
| POS-T4-02 | same, line has schedule lines | allocate oldest `scheduled_date` first across `FIRM` open lines, each up to `scheduled − received − cancelled`, the remainder (excess) to the last allocated line; one `wh_goods_receipt_line_schedule_allocations` row per (GRN line, schedule line) with the schedule line's `unit_price` frozen on it (`POS-GRD-12`); schedule `received_quantity` and `status` recomputed (short-receipt tolerance applies per schedule line); then the PO line roll-up `RQP-T1-12` | GRN posting service, same transaction |
| POS-T4-03 | receipt reversal post | allocations of the GRN's lines reversed (rows kept, `reversed_at` stamped), schedule lines recomputed | reversal service |
| POS-T4-04 | any PO receipt, close, cancel, amend of a port-owned PO | outbox `WH_PO_LINE_RECEIVED` / `WH_PO_SCHEDULE_LINE_RECEIVED` / `WH_PO_CLOSED` / `WH_PO_CANCELLED` / `WH_PO_AMENDED` with `source_*` so trade updates drawn-down quantity | outbox |
| POS-T4-05 | demand despatch | demand schedule lines' shipped qty allocated oldest-first; outbox `WH_DEMAND_SHIPPED` with `sales_order_ref`, per schedule line `release_ref` and shipped qty; a schedule-driven order follows `POS-T1-12b` | despatch service |
| POS-T4-07 | `getFulfilmentPosition(demandOrderId)` (R29 TS-F25, TRADE `TSO-OPEN-02`) | returns per line and per schedule line: `kind`, `quantity`, `allocated`, `picked`, `shipped`, `cancelled`, `backordered`, picked-not-shipped, status, `release_ref`; header status, `is_schedule_driven`, `release_closed_at` | read, no lock |
| POS-T4-08 | `WhAvailableToPromiseQuery.atp(...)` (R29 TS-F11) | per item × site × owner: allocatable on-hand, open reservations, `availableNow` = on-hand allocatable − open reservations, and firm scheduled receipts by date (open firm PO schedule quantity) up to the horizon — backend-computed, read only, never a reservation | query bean (core) |
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
| 2026-10-22 | R29 dispositions (FRD-STORES §"R29 dispositions"): port principal and authority (`POS-GRD-13`); operation registry (`POS-GRD-07`); BLANKET all-forecast create; manual release on an approved `OPEN` PO; `effectiveOrderedQuantity` roll-up (`POS-T1-14`); per-schedule-line price; last release vs last receipt date; `closeOrder`; site immutable; demand schedule-driven lines and header (`OD-45`), firm / un-firm / cancel one schedule line, cumulative amend floor, demand change guard, fulfilment position, ATP query; RMA statuses, initial status, demand-line link, `getRmaPosition`; EXTERNAL run CHECK; accept-path owner check; withdraw outcomes; `releaseConversion` |

## 8. Invariants and scenarios

`D-16` item 5; `L-1` untouched (no stock effect of a schedule); scenarios `WH-SC-420`…`-426`.

## 8a. RMA-creation port and supplier-return intent (`FR-506`, `P8-15`, TRADE `OD-33`)

| ID | From | Event | To | Guard | Actor | Side effects | Reason? | UI |
|---|---|---|---|---|---|---|---|---|
| POS-T1-20 | — | **Port `createRma`** | RMA `APPROVED` (default for a port call, R29 TS-F21) or `OPEN` | `POS-GRD-20`…`-22`; `initialStatus = APPROVED` requires `approvedByUserId` (the source's approver), else `422 PORT_APPROVER_REQUIRED` | calling user + `warehouse:orders:port` + `wh_rmas:create` | `WhRmaService.create` (`:186`) then `approve` (`:234`) in the same transaction when `APPROVED` (the `wh_rmas_assert_ladder` trigger allows only `OPEN → APPROVED`, `V510050:204`); `approved_by` = `approvedByUserId`, audit note `approval_source = SOURCE_MODULE`; `source_*` recorded; each line's `original_demand_order_line_id` stored (R29 F13) | no | none (port) |
| POS-T1-21 | RMA `OPEN`·`APPROVED` | **Port `cancelRma`** | `CANCELLED` | not `MATCHED`/`EXPIRED` (terminal, `V510050:200`); a replay on a `CANCELLED` RMA returns it | port + `wh_rmas:edit` | `WhRmaService.cancel` (`:271`); outbox `WH_RMA_CANCELLED` | **yes** | port |
| POS-T1-22 | RMA `OPEN`·`APPROVED` | *(effects)* a posted return receipt is matched (`WhRmaService.match` `:249`) / the RMA expires (`expire` `:259`) | `MATCHED` / `EXPIRED` | — | core | outbox `WH_RMA_MATCHED` (with the matching return receipt id and received quantity per RMA line) / `WH_RMA_EXPIRED`, each with `source_*`. **Core RMA statuses are exactly `OPEN`, `APPROVED`, `MATCHED`, `EXPIRED`, `CANCELLED`** (`WhRma.java:53-64`); there is no `PARTIALLY_RECEIVED` in core — a partial receipt is a `MATCHED` RMA whose received quantity is below the RMA quantity, and the selling module maps it (R29 TS-F3) | — | none |
| POS-T1-25 | any | **`getRmaPosition(rmaId)`** (R29 F14) | — | — | port + `wh_rmas:view` | returns status, `approved_by/at`, expiry date, matched return receipt ids, and per line: RMA quantity, received quantity, `original_demand_order_line_id` | — | — |
| POS-T1-23 | supplier return `DRAFT` | Set intent (`REPLACE`/`CREDIT`/`NO_ACTION`) | unchanged | active code-list row | `wh_supplier_returns:edit` | — | no | WS-084 |
| POS-T1-24 | supplier return `PICKED` | *(effect of despatch)* `DISPATCHED` | unchanged ladder | — | core | outbox `WH_SUPPLIER_RETURN_DISPATCHED` (intent, origin GRN/PO lines, PO `source_*`, item, lot, qty, movement id); **no PO change in core** | — | none |

| ID | Predicate | Refusal | Backstop |
|---|---|---|---|
| POS-GRD-20 | idempotency on `(source_module, idempotency_key)` with fingerprint | `409 PORT_IDEMPOTENCY_CONFLICT` | partial uk on `wh_rmas` |
| POS-GRD-21 | the original demand order is the same customer's, shipped; each port line names `originalDemandOrderLineId` (stored in the new `wh_rma_lines.original_demand_order_line_id → wh_demand_order_lines`, R29 F13; nullable for manual RMAs, required for port-created ones) of that order and the same item; qty ≤ shipped − Σ live (`OPEN`/`APPROVED`/`MATCHED`) RMA lines for that demand line, under a lock on the demand line | `422 RMA_EXCEEDS_SHIPPED` · `lines[i].quantity` / `422 RMA_DEMAND_LINE_INVALID` · `lines[i].originalDemandOrderLineId` | FK |
| POS-GRD-22 | manual change on a port-owned RMA allowed only if every `RmaChangeGuard` allows | `409 RMA_OWNED_BY_SOURCE_MODULE` | — |
| POS-GRD-23 | intent frozen once the return is `APPROVED` | `409 SUPPLIER_RETURN_INTENT_FROZEN` | — |

Unreachable: core reinstating PO quantity on a `REPLACE` dispatch (trade calls `amendOrder`/`releaseSchedule`); any financial document on `CREDIT` (`RN-054`). Scenarios `WH-SC-478`, `WH-SC-479`.

## 8b. External replenishment suggestions — the MRP supply seam (`FR-528`, SEAM-M3, `P8-16`; MFG `OD-41`, TRADE `OD-31`)

| ID | From | Event | To | Guard | Actor | Side effects | Reason? | UI |
|---|---|---|---|---|---|---|---|---|
| POS-T1-30 | — | **`publishExternal`** (origin `MRP`, origin run id, proposal id, item, site, qty, UoM, need date, preferred supplier?) | suggestion `PROPOSED` in a replenishment run of `run_type = EXTERNAL` (one run per publish call **per site**, inserted directly `COMPLETED` with `run_by` = the acting user — never `RUNNING`, so the one-running-run index `V510070:147` is never taken, R29 F12) | `POS-GRD-30`, `-31` | MFG port + `warehouse:orders:port` | `origin`, `origin_document_type = MRP_PROPOSAL`, `origin_document_id`, `need_date`; `on_hand`/`allocated`/`on_order` snapshotted from positions; `reorder_point` null; `basis_note` = *MRP run n, proposal m* | no | none (port) |
| POS-T1-31 | `PROPOSED` (origin `MRP`) | **`withdrawExternal`** (MRP re-run supersedes it) | `REJECTED` | only `PROPOSED` is withdrawn; an `ACCEPTED`/`CONVERTED` one is **not** an error — the call returns, per proposal, `WITHDRAWN` / `ALREADY_CONVERTED` (with the resulting document) / `NOT_FOUND`, and MRP re-plans only the `WITHDRAWN` ones, counting the others as supply (R29 MFG-F13) | port + `wh_replenishment_suggestions:edit` | reason `WITHDRAWN_BY_ORIGIN` | — | none |
| POS-T1-32 | `PROPOSED`, `suggested_source = PURCHASE` | **Accept** (today's core path: `accept` → `acceptLocked` → convert to a draft PO, `WhReplenishmentSuggestionService.java:186`, `:197`, `:287`) | `CONVERTED` | **inside `acceptLocked`**: when a `SuggestionConversionOwner` bean claims the suggestion (`ownsConversion(suggestion)`, trade on) the accept is refused `409 SUGGESTION_CONVERSION_OWNED`; no bean (trade off) → unchanged (R29 F20) | `wh_replenishment_suggestions:accept` (the controller's existing authority, `WhReplenishmentSuggestionController.java:198`, `:209`) | `resulting_document_*` = the PO; outbox `WH_REPLENISHMENT_SUGGESTION_CONVERTED` | no | core replenishment screen (Accept hidden when the owner claims it) |
| POS-T1-33 | `PROPOSED`/`ACCEPTED`, **bean present** (trade on) | trade *Raise PR* (`FR-557`) calls **`markConverted(suggestionId, resultingDocumentType, resultingDocumentId, resultingDocumentRef)`** | `CONVERTED` | `POS-GRD-32` | port + `wh_replenishment_suggestions:edit` | `resulting_document_type = PURCHASE_REQUISITION`, id, ref; outbox `WH_REPLENISHMENT_SUGGESTION_CONVERTED` | no | trade screen |
| POS-T1-34 | any | `getSuggestionStatus(origin, originDocumentId)` | — | — | port + `wh_replenishment_suggestions:view` | returns status, suggested qty, resulting document type/id/ref, `conversionLive` (MFG `OD-44` cover rule: a `CONVERTED`-to-PR suggestion is supply until the PR line is cancelled or a PO line references it) | — | — |
| POS-T1-35 | `CONVERTED` with `resulting_document_type = PURCHASE_REQUISITION` | **`releaseConversion(suggestionId, resultingDocumentId, reason)`** — the PR line was cancelled (R29 TP-F18) | `PROPOSED` (resulting document cleared, `conversion_released_at` stamped; a deliberate amendment of the `CONVERTED`-is-terminal comment, `V510070:263`, service-owned ladder) | only the module that converted it, only for a PR result; a PO result is never released | port + `wh_replenishment_suggestions:edit` | outbox `WH_REPLENISHMENT_SUGGESTION_RELEASED`; MRP may now withdraw or re-plan it | **yes** | none |

| ID | Predicate | Refusal |
|---|---|---|
| POS-GRD-30 | idempotent per `(origin, origin_document_id)`: a republish of the same proposal returns the existing suggestion; a changed qty on a `PROPOSED` one updates it, on a converted one refuses | `409 SUGGESTION_ALREADY_CONVERTED` |
| POS-GRD-31 | origin is an active `REPLENISHMENT_ORIGIN` row other than `REORDER`; item stocked at the site | `422` field-named |
| POS-GRD-32 | a suggestion is converted at most once (core PO **or** trade PR) | `409 SUGGESTION_ALREADY_CONVERTED` |

Schema (`P8-16`): `wh_replenishment_runs.run_type` CHECK widened with `EXTERNAL`, and the pairing CHECK `V510070:120` **replaced** by `(run_type IN ('MANUAL','EXTERNAL') AND run_by IS NOT NULL) OR (run_type = 'SCHEDULED' AND run_by IS NULL)` (R29 F12); `wh_replenishment_suggestions` + `conversion_released_at`; `wh_replenishment_suggestions` + `origin_list`/`origin` (default `REORDER`), `origin_document_type`, `origin_document_id`, `need_date`; `reorder_point` nullable with CHECK `origin <> 'REORDER' OR reorder_point IS NOT NULL`; partial uk `(origin, origin_document_id) WHERE origin <> 'REORDER' AND status <> 'REJECTED'`. `suggested_source` and its CHECK are untouched.

## 9. Open rows

| ID | Question | Default |
|---|---|---|
| POS-OPEN-01 | Should a manual (non-port) PO be allowed to be `BLANKET_RELEASE` when trade is off? | **No** — `BLANKET_RELEASE` requires `source_module`; without trade an install uses `FIXED`/`OPEN` |
| POS-OPEN-02 | Port transport: in-process only, or REST too? | both; trade in the same JVM uses the Java interface; REST exists for a remote buying system and requires `warehouse:orders:port` |
| POS-OPEN-03 | `OD-45` — header ladder for a schedule-driven demand order | the header returns to `OPEN` after each despatch until `closeDemand` (`POS-T1-12a`, `-12b`) |
