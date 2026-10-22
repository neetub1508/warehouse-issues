# Functional Contract — Sales return authorisation (SRA) → core RMA, and the purchase-side replacement twin

> **What this is.** The functional truth for authorising a customer's return in `warehouse-trade`
> against a sales order and its shipments, handing it to the core RMA (receipt, QC, disposition are
> core's), and acting on the outcome (replacement release, or an accounting hand-over point for credit).
> The purchase twin — supplier return — stays core (`p8-07`); trade only reinstates PO quantity on a
> `REPLACE` intent (FRD-TRADE §5 M26).
>
> **Status.** Derived 2026-10-22 (v0). **Not buildable until STORES `p8-15`** (`OD-33`: the RMA creation port `WhRmaPort` and the supplier-return intent) has landed.

---

## 0. Identity

| | |
|---|---|
| **Workflow** | Draft SRA (from SO / shipment) → submit → approve → core RMA created → RMA received / closed → SRA closed; `REPLACE` → replacement dispatch release drafted; `CREDIT` → hand-over marker; reject / cancel |
| **Module** | `warehouse-trade`; core RMA (`wh_rmas`, `V510050`) through `ai.warehouse.port.returns.WhRmaPort` (`OD-33` — published by STORES `p8-15`, `FR-506`) |
| **Domain baseline** | FRD-TRADE FR-612, FR-613, FR-614 (`RETURN_RATE`) · R28 §4 D4 · `RN-031` |
| **Owning task body** | `issues/p9-13.md` |
| **Primary tables** | `wht_sales_return_authorisations`, `wht_sales_return_authorisation_lines` (`V550120`) |
| **Permission resources** | `wht_sales_return_authorisations:view/create/edit/export/submit/approve/cancel` |
| **Routes** | WS-308 `/warehouse/trade/sales/return-authorisations`; *Returns* tab on WS-304, *Returns & claims* on WS-293 · mobile: none |
| **Contract status / version** | `derived` · `v0 — 2026-10-22` |

**Fields.** Header: `sra_number` (series `SRA`, at submit), company, customer, `sales_order_id`,
`customer_return_ref`, `requested_date`, `return_to_warehouse_id`, `intent_code` (`REPLACE`/`CREDIT`/
`REWORK`), `status`, `core_rma_id` ↓ `wh_rmas`, `replacement_release_id`, `accounting_handover_marked_at`.
Line: `so_line_id`, `core_demand_order_line_id` (the shipped line), item, `quantity`, `uom_code`,
`reason_code` (code list `trade_return_reason`: `QUALITY_NC`, `DIMENSION_NC`, `WRONG_ITEM`,
`EXCESS_SUPPLY`, `TRANSIT_DAMAGE`, `CUSTOMER_CHANGE`), `expected_condition_code`, lot / serial refs
(optional, from the shipment), `received_quantity` (read from core).

### Acceptance checks

| # | Expects | Delivered by |
|---|---|---|
| A1 | SRA against shipped qty; core RMA created on approval; `REPLACE` drafts a replacement on receipt (`WH-SC-562`) | `TSR-T1-03`, `TSR-T4-01`, `-02` |
| A2 | Qty ≤ shipped − already authorised (`WH-SC-563`) | `TSR-GRD-01` |
| A3 | Supplier return `REPLACE` reinstates PO qty (`WH-SC-564`) | `TSR-T4-04` |
| A4 | `CREDIT` produces no credit note (FRD §11 R3) | `TSR-UNR-01` |

## 1. T1 — State machine

| Status | Reachable via | Exits via | Kind |
|---|---|---|---|
| `DRAFT` | `-01`, return | `-02`, `-06` | initial |
| `SUBMITTED` | `-02` | `TAM` | active |
| `APPROVED` | `-03` (core RMA `OPEN`) | `-04`, `-05` | active |
| `PARTIALLY_RECEIVED` / `RECEIVED` | `TSR-T4-01` (from core RMA / return receipt) | `-05` | active |
| `CLOSED` | `-05` | none | terminal |
| `REJECTED` / `CANCELLED` | `TAM` / `-06`, `-04` | none | terminal |

| ID | From | Action | To | Guard | Actor | Side effects | Comment | UI |
|---|---|---|---|---|---|---|---|---|
| TSR-T1-01 | — | Create from SO / shipment | `DRAFT` | — | `:create` | lines prefilled from shipped lines | no | WS-308 Add, WS-304 *Raise return* |
| TSR-T1-02 | `DRAFT`, return | Submit | `SUBMITTED` | `TSR-GRD-01`…`-03` | `:submit` | number; `TAM` doc `SRA` (value = Σ qty × SO net price) | no | Submit |
| TSR-T1-03 | `SUBMITTED` | Approved | `APPROVED` | `TSR-GRD-04` | approver | **`WhRmaPort.createRma`** (`TSR-T4-03`) in the same transaction; print `SALES_RETURN_AUTHORISATION` | — | WS-285 |
| TSR-T1-04 | `APPROVED` | Cancel (customer withdrew) | `CANCELLED` | core RMA has no receipt | `:cancel` | `WhRmaPort.cancelRma` | **yes** | row action |
| TSR-T1-05 | `RECEIVED` (or `APPROVED` with RMA expired / closed by core) | Close | `CLOSED` | core RMA `CLOSED` / `EXPIRED` | system | `REPLACE`: replacement release must exist or be explicitly declined (reason) | — | — |
| TSR-T1-06 | `DRAFT` | Cancel | `CANCELLED` | — | maker | — | no | — |

### 1.3 Guards

| ID | Predicate | Refusal |
|---|---|---|
| TSR-GRD-01 | Per shipped demand-order line: Σ non-cancelled SRA qty + this ≤ shipped qty (core) | `422 TRADE_RETURN_EXCEEDS_SHIPPED {open}` |
| TSR-GRD-02 | Reason and expected condition set; intent set; return-to site in user scope and holds a return location (core) | field `422` |
| TSR-GRD-03 | SO not `CANCELLED`; customer exists (a blocked customer may still return goods — no block check) | field `422` |
| TSR-GRD-04 | `WhRmaPort` bean present (`OD-33`) | `503 TRADE_RMA_PORT_ABSENT` — the screen states the dependency |

### 1.4 Unreachable

| ID | Forbidden | Why |
|---|---|---|
| TSR-UNR-01 | A credit note, debit note or invoice reversal | FRD §11 R3 — `CREDIT` only stamps `accounting_handover_marked_at` |
| TSR-UNR-02 | Trade receiving or dispositioning returned stock | core RMA → return receipt → QC → disposition |
| TSR-UNR-03 | A trade purchase-return document | M26: core supplier return already carries approval |

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from |
|---|---|---|---|
| TSR-T2-01 | Add / edit | `:create` / `:edit` | `DRAFT` |
| TSR-T2-02 | Submit / approve | `:submit` / `:approve` | per T1 |
| TSR-T2-03 | Cancel | `:cancel` | `DRAFT`, `APPROVED` (no receipt) |
| TSR-T2-04 | Print / export | `:view` / `:export` | numbered |

## 3. T3 — Time-driven rules

| ID | Rule | Trigger | Changes | Notified | Job |
|---|---|---|---|---|---|
| TSR-T3-01 | Return overdue | `APPROVED` and core RMA `expiry_date` passed with no receipt | none (core expires the RMA; trade reflects it) | sales exec | read on core event / daily `TradeSalesJob` |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in |
|---|---|---|---|
| TSR-T4-01 | Core return receipt posted against the RMA | SRA `PARTIALLY_RECEIVED` / `RECEIVED` from core received quantities (read through `WhRmaPort.getRmaPosition`; status stored only as a projection refreshed by the core event and the `p8-15` outbox `WH_RMA_MATCHED` / `WH_RMA_CANCELLED` / `WH_RMA_EXPIRED`, reconciled nightly) | event handler on core `return.receipt.posted` and the `WH_RMA_*` outbox |
| TSR-T4-02 | `REPLACE` and received | replacement dispatch release `DRAFT` on the SO for the received qty at the original net price, flagged `is_replacement` (no new commercial value); planner releases it (`TSO-T1-08`) | same handler |
| TSR-T4-03 | Approved | `WhRmaPort.createRma(idempotencyKey:'WHT_SRA:<id>', {sourceModule:'warehouse-trade', sourceDocumentType:'WHT_SRA', sourceDocumentId, sourceDocumentRef:<sra_number>, initialStatus:'OPEN', owner, warehouse, customer, originalDemandOrderId, reasonCodeId, expectedCondition, expiryDate, lines[item, qty, uom, lot/serial]})` → core `wh_rmas` `OPEN`; `core_rma_id` stored | approval transaction |
| TSR-T4-04 | Core supplier return with intent `REPLACE` reaches `DISPATCHED` for a trade-created PO | `WhPurchaseOrderPort.amendOrder` adds a `FIRM` schedule line for the returned qty on the original PO line (no new port op), which re-opens that quantity; trade PO line shows *replacement due*; expediting lists it | outbox subscriber on `WH_SUPPLIER_RETURN_DISPATCHED` carrying `intent_code` (`OD-33`) |
| TSR-T4-05 | Any | `RETURN_RATE` metric reads SRA quantities (`TCE`) | evaluation run |

## 5. T5 — Screen contract

WS-308 (reference **Service Vehicle**): grid `wht_sales_return_authorisations`, scope
`WAREHOUSE_TRADE_SALES_RETURN_AUTHORISATION`. Tiles: draft, awaiting approval, approved awaiting
receipt, received (period), replacements pending. Columns: `sraNumber`, `customerName`, `soNumber`,
`customerReturnRef`, `requestedDate`, `intent`, `lineCount`, `quantity`, `receivedQuantity`,
`coreRmaNumber`, `status`, audit. Filters: `customerId`, `soId`, `status`, `intent`, `reasonCode`,
`requestedFrom`/`To`. Actions: View · Edit · Submit · Cancel · Print · Open RMA (core route, read).

## 6. Out of scope

| Item | Decision |
|---|---|
| Credit note | refused (R3) |
| Return receipt, grading, disposition | core |

## 7. Amendments

| Date | Rows | Change | Found by |
|---|---|---|---|
| 2026-10-22 | all | v0 derived | TRADE author |

## 8. Invariants and scenarios

`WH-SC-562`…`WH-SC-564`.

## 9. Open rows

`OD-33` (blocking until `p8-15` lands).
