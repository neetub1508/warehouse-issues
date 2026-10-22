# Functional Contract — Sales return authorisation (SRA) → core RMA, and the purchase-side replacement twin

> **What this is.** The functional truth for authorising a customer's return in `warehouse-trade`
> against a sales order and its shipments, handing it to the core RMA (receipt, QC, disposition are
> core's), and acting on the outcome (replacement release, or an accounting hand-over point for credit).
> The purchase twin — supplier return — stays core (`p8-07`); trade only reinstates PO quantity on a
> `REPLACE` intent, through a system amendment (FRD-TRADE §5 M26, `TPO-T4-07`).
>
> **Port names.** `WhRmaPort`, `RmaChangeGuard`, the commands, operation keys and events below are FRD-STORES
> *"Port & seam registry (authoritative)"*'s (R.2, R.3, R.4); trade's keys and principal are FRD-TRADE §12a.
>
> **Status.** Derived 2026-10-22 (v0), R29 folded (v1). **Not buildable until STORES `p8-15`** (`OD-33`) has landed.

---

## 0. Identity

| | |
|---|---|
| **Workflow** | Draft SRA (from SO / shipment) → submit → approve → core RMA created `APPROVED` → core matches a return receipt (`MATCHED`) or the RMA expires / is cancelled → SRA received / closed; `REPLACE` → replacement dispatch release drafted; `CREDIT` → hand-over marker; reject / cancel |
| **Module** | `warehouse-trade`; core RMA (`wh_rmas`, `V510050`) through `ai.warehouse.port.returns.WhRmaPort` (`OD-33` — published by STORES `p8-15`, `FR-506`; `POS-T1-20`…`-25`) |
| **Domain baseline** | FRD-TRADE FR-612, FR-613, FR-614 (`RETURN_RATE`) · R28 §4 D4 · `RN-031` |
| **Owning task body** | `issues/p9-13.md` |
| **Primary tables** | `wht_sales_return_authorisations`, `wht_sales_return_authorisation_lines` (`V550120`) |
| **Permission resources** | `wht_sales_return_authorisations:view/create/edit/export/submit/approve/cancel`. The SRA approver and sales-executive bundles hold core **`warehouse:orders:port`** (`TRD-13`, seeded in `V551130`) |
| **Routes** | WS-308 `/warehouse/trade/sales/return-authorisations`; *Returns* tab on WS-304, *Returns & claims* on WS-293 · mobile: none |
| **Contract status / version** | `derived` · `v1 — 2026-10-22` |

**Fields.** Header: `sra_number` (series `SRA`, at submit), company, customer, `sales_order_id`,
`customer_return_ref`, `requested_date`, `return_by_date` (DATE, default `requested_date` +
`warehouse.trade.sales.return_validity_days`, default 30; sent to core as the RMA `expiryDate`),
`return_to_warehouse_id`, `intent_code` (`REPLACE`/`CREDIT`/`REWORK`), `status`, `core_rma_id` ↓ `wh_rmas`,
`received_short` (matched below the authorised quantity), `replacement_release_id`,
`replacement_declined_reason_code`, `accounting_handover_marked_at`. Line: `so_line_id`,
`core_demand_order_line_id` (the shipped line; sent as `originalDemandOrderLineId`), item, `quantity`,
`uom_code`, `reason_code` (code list `trade_return_reason`: `QUALITY_NC`, `DIMENSION_NC`, `WRONG_ITEM`,
`EXCESS_SUPPLY`, `TRANSIT_DAMAGE`, `CUSTOMER_CHANGE`), `expected_condition_code`, lot / serial refs (optional,
from the shipment), `received_quantity` (projection of core, `getRmaPosition`).

### Acceptance checks

| # | Expects | Delivered by |
|---|---|---|
| A1 | SRA against shipped qty; core RMA created `APPROVED` on approval; `REPLACE` drafts a replacement on receipt (`WH-SC-562`) | `TSR-T1-03`, `TSR-T4-01`, `-02`, `-03` |
| A2 | Qty ≤ shipped − already authorised (`WH-SC-563`) | `TSR-GRD-01` |
| A3 | Supplier return `REPLACE` reinstates PO qty through an amendment (`WH-SC-564`, `-578`) | `TSR-T4-04` |
| A4 | `CREDIT` produces no credit note (FRD §11 R3) | `TSR-UNR-01` |
| A5 | Every core RMA end state has an SRA exit; a short match closes (`WH-SC-581`) | `TSR-T1-05`, `-07`, `-08`, `TSR-T4-01` |

## 1. T1 — State machine

| Status | Reachable via | Exits via | Kind |
|---|---|---|---|
| `DRAFT` | `-01`, return | `-02`, `-06` | initial |
| `SUBMITTED` | `-02` | `TAM`, `-02a` | active |
| `REJECTED` | `TAM` | edit → `DRAFT`, `-06` | active |
| `APPROVED` | `-03` (core RMA `APPROVED`) | `-04`, `-07`, `-08`, `TSR-T4-01` | active |
| `RECEIVED` | `TSR-T4-01` (core `WH_RMA_MATCHED`, matched = authorised) | `-05` | active |
| `PARTIALLY_RECEIVED` | `TSR-T4-01` (core `WH_RMA_MATCHED`, matched < authorised — final, core takes no further receipt on a `MATCHED` RMA) | `-05` | active |
| `CLOSED` | `-05`, `-07` | none | terminal |
| `CANCELLED` | `-04`, `-06`, `-08` | none | terminal |

Core RMA status → SRA (`POS-T1-22`; core statuses are exactly `OPEN`, `APPROVED`, `MATCHED`, `EXPIRED`,
`CANCELLED`): `APPROVED` → `APPROVED`; `MATCHED` → `RECEIVED` / `PARTIALLY_RECEIVED`; `EXPIRED` → `CLOSED`
(outcome *expired*, `-07`); `CANCELLED` → `CANCELLED` (`-04` or `-08`). `OPEN` is never used by trade.

| ID | From | Action | To | Guard | Actor | Side effects | Comment | UI |
|---|---|---|---|---|---|---|---|---|
| TSR-T1-01 | — | Create from SO / shipment | `DRAFT` | — | `:create` | lines prefilled from shipped lines; `return_by_date` defaulted | no | WS-308 Add, WS-304 *Raise return* |
| TSR-T1-02 | `DRAFT`, `REJECTED` | Submit | `SUBMITTED` | `TSR-GRD-01`…`-03` | `:submit` | number at first submit; `TAM` doc `SRA` (value = Σ qty × SO net price, SO currency) | no | Submit |
| TSR-T1-02a | `SUBMITTED` | Withdraw (`TAM-T1-09`) | `DRAFT` | no step acted | maker | — | no | *Withdraw* |
| TSR-T1-03 | `SUBMITTED` | Approved | `APPROVED` | `TSR-GRD-04` | approver (holds `warehouse:orders:port`) | **`WhRmaPort.createRma`** (`TSR-T4-03`) in the same transaction; print `SALES_RETURN_AUTHORISATION` | — | WS-285 |
| TSR-T1-03a | `SUBMITTED` | Rejected / returned | `REJECTED` / `DRAFT` | `TAM` | approver | maker notified | **yes** | WS-285 |
| TSR-T1-04 | `APPROVED` | Cancel (customer withdrew) | `CANCELLED` | core RMA not `MATCHED` (`getRmaPosition`) | `:cancel` | **`WhRmaPort.cancelRma(CancelRmaCommand{ rmaId, reasonCodeId, note })`**, key `WHT_SRA:<id>:RMA_CANCEL:1` | **yes** | row action |
| TSR-T1-05 | `RECEIVED`, `PARTIALLY_RECEIVED` | Close | `CLOSED` | `REPLACE`: the replacement release is `RELEASED`/`CLOSED`, or declined with a reason (also when the SO is `SHORT_CLOSED` / `CANCELLED`, `TSO-T4-07`); `CREDIT`: `accounting_handover_marked_at` stamped; `REWORK`: none | system (after the replacement release is released or declined), or `:edit` for *Decline replacement* | — | reason on decline | *Decline replacement* |
| TSR-T1-06 | `DRAFT`, `REJECTED` | Cancel | `CANCELLED` | — | maker | — | no | row action |
| TSR-T1-07 | `APPROVED` | Core RMA expired (`WH_RMA_EXPIRED`) | `CLOSED`, outcome *expired*, received 0 | — | system | none sent to core; the customer may raise a new SRA | — | — |
| TSR-T1-08 | `APPROVED` | Core RMA cancelled outside trade's call (`WH_RMA_CANCELLED` not caused by `-04` — only possible if a guard is removed) | `CANCELLED` | — | system | logged for the sales executive | — | — |

### 1.3 Guards

| ID | Predicate | Refusal |
|---|---|---|
| TSR-GRD-01 | Per shipped demand-order line: Σ non-cancelled SRA qty + this ≤ shipped qty (core; core re-checks under its own lock, `POS-GRD-21`) | `422 TRADE_RETURN_EXCEEDS_SHIPPED {open}` |
| TSR-GRD-02 | Reason and expected condition set; intent set; `return_by_date ≥ today`; return-to site in user scope and holds a return location (core) | field `422` |
| TSR-GRD-03 | SO not `CANCELLED`; customer exists (a blocked customer may still return goods — no block check) | field `422` |
| TSR-GRD-04 | `WhRmaPort` bean present (`OD-33`) | `503 TRADE_RMA_PORT_ABSENT` — the screen states the dependency |
| TSR-GRD-05 | Trade's `RmaChangeGuard` refuses core-screen `EDIT`, `APPROVE`, `CANCEL` of a trade-created RMA; `EXPIRE` is allowed (`OD-39`) | `409 RMA_OWNED_BY_SOURCE_MODULE` (raised by the guard, `POS-GRD-22`) |

### 1.4 Unreachable

| ID | Forbidden | Why |
|---|---|---|
| TSR-UNR-01 | A credit note, debit note or invoice reversal | FRD §11 R3 — `CREDIT` only stamps `accounting_handover_marked_at` |
| TSR-UNR-02 | Trade receiving or dispositioning returned stock | core RMA → return receipt → QC → disposition |
| TSR-UNR-03 | A trade purchase-return document | M26: core supplier return already carries approval |
| TSR-UNR-04 | An SRA stuck after its RMA ends | every core end state maps to an SRA exit (§1) |

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from |
|---|---|---|---|
| TSR-T2-01 | Add / edit | `:create` / `:edit` | `DRAFT`, `REJECTED` |
| TSR-T2-02 | Submit / withdraw / approve | `:submit` / `:submit` (maker) / `:approve` + `warehouse:orders:port` | per T1 |
| TSR-T2-03 | Cancel | `:cancel` (+ `warehouse:orders:port` after approval) | `DRAFT`, `REJECTED`, `APPROVED` (not matched) |
| TSR-T2-04 | Decline replacement | `:edit` | `RECEIVED`, `PARTIALLY_RECEIVED` with intent `REPLACE` |
| TSR-T2-05 | Print / export | `:view` / `:export` (auditor: none) | numbered |

## 3. T3 — Time-driven rules

| ID | Rule | Trigger | Changes | Notified | Job |
|---|---|---|---|---|---|
| TSR-T3-01 | Return overdue | `APPROVED` and `return_by_date` passed with no match | none (core expires the RMA, `TSR-T1-07`) | sales exec, `TRADE_RETURN_OVERDUE` | daily `TradeSalesJob`, once |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in |
|---|---|---|---|
| TSR-T4-01 | `WH_RMA_MATCHED` for the SRA's RMA (`source_document_id`) | `received_quantity` per line from the event (reconciled through `getRmaPosition`); SRA `RECEIVED` when Σ matched = authorised, else `PARTIALLY_RECEIVED` with `received_short = true` (the rest of the authorisation lapses); `WH_RMA_EXPIRED` → `TSR-T1-07`; `WH_RMA_CANCELLED` → `-04` / `-08`; projection reconciled nightly | outbox subscriber |
| TSR-T4-02 | `REPLACE` and matched quantity > 0 | replacement dispatch release `DRAFT` on the SO for the matched qty at the original net price, `is_replacement`, `source_sra_id` (`TSO-T1-16`); the planner submits it and `SO_RELEASE` approves it; the SO stays open until the SRA closes (`TSO-T3-03`) | same handler |
| TSR-T4-03 | Approved | `WhRmaPort.createRma(CreateRmaCommand{ envelope(sourceModule 'warehouse-trade', idempotencyKey 'WHT_SRA:<id>:RMA_CREATE:1', actingUserId = last approver), sourceDocumentType 'WHT_SRA', sourceDocumentId, sourceDocumentRef <sra_number>, customerCounterpartyId, ownerId, warehouseId = return-to site, originalDemandOrderId = the SO's core demand order, reasonCodeId, expectedConditionCode, expiryDate = return_by_date, initialStatus 'APPROVED', approvedByUserId = last approver, lines[ originalDemandOrderLineId, itemId, quantity, uomCode, lotCode?, serialNumber? ] })` → core `wh_rmas` `APPROVED` (`POS-T1-20`); `core_rma_id` stored | approval transaction |
| TSR-T4-04 | `WH_SUPPLIER_RETURN_DISPATCHED` with intent `REPLACE` for a trade-created PO | `TPO-T4-07`: a system amendment of origin `SUPPLIER_RETURN` is drafted for the buyer (version + 1 on apply, `amendOrder` adds the `FIRM` schedule quantity); on a `SHORT_CLOSED` / `CANCELLED` PO nothing is reinstated and the buyer is told | outbox subscriber (`OD-33`) |
| TSR-T4-05 | Any | `RETURN_RATE` metric reads SRA quantities (`TCE`) | evaluation run |

## 5. T5 — Screen contract

WS-308 (reference **Service Vehicle**): grid `wht_sales_return_authorisations`, scope
`WAREHOUSE_TRADE_SALES_RETURN_AUTHORISATION`, sort `e.requested_date DESC`. Tiles: draft, awaiting approval,
approved awaiting receipt, received (period), replacements pending — counts. Columns: `sraNumber`,
`customerName`, `soNumber`, `customerReturnRef`, `requestedDate`, `returnByDate` (date-only), `intent`,
`lineCount`, `quantity`, `receivedQuantity`, `receivedShort`, `coreRmaNumber`, `status`, audit. Filters:
`customerId`, `soId`, `status`, `intent`, `reasonCode`, `requestedFrom`/`To`, `overdueOnly`. Actions: View ·
Edit · Submit · Withdraw · Cancel · Decline replacement · Print · Open RMA (core route, read). Export ⊇ grid.
Empty state: *No return authorisations.*

## 6. Out of scope

| Item | Decision |
|---|---|
| Credit note | refused (R3) |
| Return receipt, grading, disposition | core |

## 7. Amendments

| Date | Rows | Change | Found by |
|---|---|---|---|
| 2026-10-22 | all | v0 derived | TRADE author |
| 2026-10-22 | all | R29 TS-F3, F12, F16, F21 and contract quality: core RMA statuses mapped exactly (`MATCHED` / `EXPIRED` / `CANCELLED`), `PARTIALLY_RECEIVED` closable, RMA created `APPROVED` with the approver, `return_by_date` field for `expiryDate`, registry-exact command and keys, `RmaChangeGuard` row, withdraw, replacement through `TSO-T1-16`, supplier-return reinstatement through the amendment engine | R29 |

## 8. Invariants and scenarios

`WH-SC-562`…`WH-SC-564`, `WH-SC-578`, `WH-SC-581`, `WH-SC-587`.

## 9. Open rows

`OD-33` (blocking until `p8-15` lands).
