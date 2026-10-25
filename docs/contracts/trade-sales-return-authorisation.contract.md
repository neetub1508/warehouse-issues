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
`return_to_warehouse_id`, `intent_code` (`REPLACE`/`CREDIT`/`REWORK`), `reason_code_id` ↓ `whb_reason_codes` (context `RETURN`, required — the one header reason core's RMA takes, R31 F-TR-007), `status`, `core_rma_id` ↓ `wh_rmas`,
`received_short` (matched below the authorised quantity), `replacement_release_id`,
`replacement_declined_reason_code`, `accounting_handover_marked_at`. Line: `so_line_id`,
`core_demand_order_line_id` (the shipped line; sent as `originalDemandOrderLineId`), item, `quantity`,
`uom_code`, `reason_code_id` ↓ `whb_reason_codes` (context `RETURN`; trade seeds `QUALITY_NC`, `DIMENSION_NC`,
`EXCESS_SUPPLY`, `TRANSIT_DAMAGE`, `CUSTOMER_CHANGE` and reuses base's `RETURN` / `WRONG_ITEM` row, FRD-TRADE FR-546; defaulted from the header reason, may differ per line and stays trade-side — the RMA carries the header reason only), `expected_condition_code`, lot / serial refs (optional,
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
| `RECEIVED` | `TSR-T4-01` (core `rma.matched`, matched = authorised) | `-05` | active |
| `PARTIALLY_RECEIVED` | `TSR-T4-01` (core `rma.matched`, matched < authorised — final, core takes no further receipt on a `MATCHED` RMA) | `-05` | active |
| `CLOSED` | `-05`, `-07` | none | terminal |
| `CANCELLED` | `-04`, `-06`, `-08` | none | terminal |

Core RMA status → SRA (`POS-T1-22`; core statuses are exactly `OPEN`, `APPROVED`, `MATCHED`, `EXPIRED`,
`CANCELLED`): `APPROVED` → `APPROVED`; `MATCHED` → `RECEIVED` / `PARTIALLY_RECEIVED`; `EXPIRED` → `CLOSED`
(outcome *expired*, `-07`); `CANCELLED` → `CANCELLED` (`-04` or `-08`). `OPEN` is never used by trade.

| ID | From | Action | To | Guard | Actor | Side effects | Comment | UI | Source |
|---|---|---|---|---|---|---|---|---|---|
| TSR-T1-01 | — | Create from SO / shipment | `DRAFT` | — | `:create` | lines prefilled from shipped lines; `return_by_date` defaulted | no | WS-308 Add, WS-304 *Raise return* | FR-612 |
| TSR-T1-02 | `DRAFT`, `REJECTED` | Submit | `SUBMITTED` | `TSR-GRD-01`…`-03` | `:submit` | number at first submit; `TAM` doc `SRA` (value = Σ qty × SO net price, SO currency) | no | Submit | FR-612 |
| TSR-T1-02a | `SUBMITTED` | Withdraw (`TAM-T1-09`) | `DRAFT` | no step acted | maker | — | no | *Withdraw* | FR-551 |
| TSR-T1-03 | `SUBMITTED` | Approved | `APPROVED` | `TSR-GRD-04` | approver (holds `warehouse:orders:port`) | **`WhRmaPort.createRma`** (`TSR-T4-03`) in the same transaction; print `SALES_RETURN_AUTHORISATION` | — | WS-285 | FR-612 |
| TSR-T1-03a | `SUBMITTED` | Rejected / returned | `REJECTED` / `DRAFT` | `TAM` | approver | maker notified | **yes** | WS-285 | FR-551 |
| TSR-T1-04 | `APPROVED` | Cancel (customer withdrew) | `CANCELLED` | core RMA not `MATCHED` (`getRmaPosition`) | `:cancel` | **`WhRmaPort.cancelRma(CancelRmaCommand{ rmaId, reasonCodeId (a `TRADE_ORDER_CLOSE`-context `whb_reason_codes` id, FR-546), note })`**, key `WHT_SRA:<id>:RMA_CANCEL:1` | **yes** | row action | FR-612 |
| TSR-T1-05 | `RECEIVED`, `PARTIALLY_RECEIVED` | Close | `CLOSED` | `REPLACE`: the replacement release is `RELEASED`/`CLOSED`, or declined with a reason (also when the SO is `SHORT_CLOSED` / `CANCELLED`, `TSO-T4-07`); `CREDIT`: `accounting_handover_marked_at` stamped; `REWORK`: none | system (after the replacement release is released or declined), or `:edit` for *Decline replacement* | — | reason on decline | *Decline replacement* | FR-612 |
| TSR-T1-06 | `DRAFT`, `REJECTED` | Cancel | `CANCELLED` | — | maker | — | no | row action | FR-612 |
| TSR-T1-07 | `APPROVED` | Core RMA expired (`rma.expired`) | `CLOSED`, outcome *expired*, received 0 | — | system | none sent to core; the customer may raise a new SRA | — | — | FR-612 |
| TSR-T1-08 | `APPROVED` | Core RMA cancelled outside trade's call (`rma.cancelled` not caused by `-04` — only possible if a guard is removed) | `CANCELLED` | — | system | logged for the sales executive | — | — | FR-612 |

### 1.3 Guards

| ID | Predicate | Refusal | Source |
|---|---|---|---|
| TSR-GRD-01 | Per shipped demand-order line: Σ **live** authorised qty (SRAs `SUBMITTED` or `APPROVED`, not yet matched or expired) + Σ **matched** qty (SRAs `RECEIVED`, `PARTIALLY_RECEIVED`, or `CLOSED` after a match) + this ≤ shipped qty — an expired SRA and the lapsed remainder of a `PARTIALLY_RECEIVED` one count nothing, as core counts only live RMAs (R31 F-TR-015); core re-checks under its own lock (`POS-GRD-21`) | `422 TRADE_RETURN_EXCEEDS_SHIPPED {open}` | FR-612 |
| TSR-GRD-02 | Header reason (`RETURN` context) and expected condition set; intent set; `return_by_date ≥ today`; return-to site in user scope and holds a return location (core) | field `422` | FR-612 |
| TSR-GRD-03 | SO not `CANCELLED`; customer exists (a blocked customer may still return goods — no block check). Intent **`REPLACE`** also needs the SO open (`APPROVED` / `ISSUED`): on a `CLOSED` or `SHORT_CLOSED` SO its core demand order is closed and takes no release, so a replacement is a **new SO** and the SRA is raised `CREDIT` or `REWORK` (twin of FR-613's *a new PO is needed*; R31 F-TR-002). An SO open at approval stays open until the SRA closes (`TSO-T3-03`) | field `422` / `422 TRADE_REPLACE_NEEDS_OPEN_SO` | FR-612 |
| TSR-GRD-04 | `WhRmaPort` bean present (`OD-33`) | `503 TRADE_RMA_PORT_ABSENT` — the screen states the dependency | FR-612 |
| TSR-GRD-05 | Trade's `RmaChangeGuard` refuses core-screen `EDIT`, `APPROVE`, `CANCEL` of a trade-created RMA; `EXPIRE` is allowed (`OD-39`) | `409 RMA_OWNED_BY_SOURCE_MODULE` (raised by the guard, `POS-GRD-22`) | FR-612 |
| TSR-GRD-06 | **Concurrency**: every edit, submit, transition and approval of a `wht_` document checks its optimistic `version`; a stale write changes nothing; every write through `WhRmaPort` (`TSR-T4-03`) carries a `PortEnvelope` whose idempotency key has the FRD-TRADE §12a shape `<SOURCE_DOCUMENT_TYPE>:<id>:<operation>:<sequence>`, and the port call commits with the trade transition, so a double-clicked action changes core once | `409 CONCURRENT_MODIFICATION` stale write (`TPR-OPEN-03`); `409 PORT_IDEMPOTENCY_CONFLICT` relayed | FR-618 |

### 1.4 Unreachable

| ID | Forbidden | Why | Source |
|---|---|---|---|
| TSR-UNR-01 | A credit note, debit note or invoice reversal | FRD §11 R3 — `CREDIT` only stamps `accounting_handover_marked_at` | FR-612 |
| TSR-UNR-02 | Trade receiving or dispositioning returned stock | core RMA → return receipt → QC → disposition | FR-612 |
| TSR-UNR-03 | A trade purchase-return document | M26: core supplier return already carries approval | FR-613 |
| TSR-UNR-04 | An SRA stuck after its RMA ends | every core end state maps to an SRA exit (§1) | FR-612 |

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from | Source |
|---|---|---|---|---|
| TSR-T2-01 | Add / edit | `:create` / `:edit` | `DRAFT`, `REJECTED` | FR-612 |
| TSR-T2-02 | Submit / withdraw / approve | `:submit` / `:submit` (maker) / `:approve` + `warehouse:orders:port` | per T1 | FR-612 |
| TSR-T2-03 | Cancel | `:cancel` (+ `warehouse:orders:port` after approval) | `DRAFT`, `REJECTED`, `APPROVED` (not matched) | FR-612 |
| TSR-T2-04 | Decline replacement | `:edit` | `RECEIVED`, `PARTIALLY_RECEIVED` with intent `REPLACE` | FR-612 |
| TSR-T2-05 | Print / export | `:view` / `:export` (auditor: none) | numbered | FR-615 |
| TSR-T2-06 | Every action in this table, and the auditor | `wht_<table>:<verb>` per FRD-TRADE FR-617 (`view`, `create`, `edit`, `export` + the workflow verbs above); `permission_dependencies` seeded; the auditor bundle holds `:view` only; record scope follows core's company / site grants; a bundle whose action calls a core port is also granted `warehouse:orders:port` in the trade seed | — | FR-617 |

## 3. T3 — Time-driven rules

| ID | Rule | Trigger | Changes | Notified | Job | Source |
|---|---|---|---|---|---|---|
| TSR-T3-01 | Return overdue | `APPROVED` and `return_by_date` passed with no match | none (core expires the RMA, `TSR-T1-07`) | sales exec, `TRADE_RETURN_OVERDUE` | daily `TradeSalesJob`, once | FR-612 |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in | Source |
|---|---|---|---|---|
| TSR-T4-01 | `rma.matched` for the SRA's RMA (`source_document_id`) | `received_quantity` per line from the event (reconciled through `getRmaPosition`); SRA `RECEIVED` when Σ matched = authorised, else `PARTIALLY_RECEIVED` with `received_short = true` (the rest of the authorisation lapses); `rma.expired` → `TSR-T1-07`; `rma.cancelled` → `-04` / `-08`; projection reconciled nightly | outbox subscriber | FR-612 |
| TSR-T4-02 | `REPLACE` and matched quantity > 0 | replacement dispatch release `DRAFT` on the SO for the matched qty at the original net price, `is_replacement`, `source_sra_id` (`TSO-T1-16`); the planner submits it and `SO_RELEASE` approves it; the SO stays open until the SRA closes (`TSO-T3-03`) | same handler | FR-612 |
| TSR-T4-03 | Approved | `WhRmaPort.createRma(CreateRmaCommand{ envelope(sourceModule 'warehouse-trade', idempotencyKey 'WHT_SRA:<id>:RMA_CREATE:1', actingUserId = last approver), sourceDocumentType 'WHT_SRA', sourceDocumentId, sourceDocumentRef <sra_number>, customerCounterpartyId, ownerId, warehouseId = return-to site, originalDemandOrderId = the SO's core demand order, reasonCodeId = the header `reason_code_id` (a `RETURN`-context `whb_reason_codes` id, as `WhRmaValidationService.validateHeader` requires), expectedConditionCode, expiryDate = return_by_date, initialStatus 'APPROVED', approvedByUserId = last approver, lines[ originalDemandOrderLineId, itemId, quantity, uomCode, lotCode?, serialNumber? ] })` → core `wh_rmas` `APPROVED` (`POS-T1-20`); `core_rma_id` stored | approval transaction | FR-612 |
| TSR-T4-04 | `supplier_return.dispatched` with intent `REPLACE` for a trade-created PO | `TPO-T4-07`: a system amendment of origin `SUPPLIER_RETURN` is drafted for the buyer (version + 1 on apply, `amendOrder` adds the `FIRM` schedule quantity); on a `SHORT_CLOSED` / `CANCELLED` PO nothing is reinstated and the buyer is told | outbox subscriber (`OD-33`) | FR-613 |
| TSR-T4-05 | Any | `RETURN_RATE` metric reads SRA quantities (`TCE`) | evaluation run | FR-614 |

## 5. T5 — Screen contract

WS-308 (reference **Service Vehicle**): grid `wht_sales_return_authorisations`, scope
`WAREHOUSE_TRADE_SALES_RETURN_AUTHORISATION`, sort `e.requested_date DESC`. Tiles: draft, awaiting approval,
approved awaiting receipt, received (period), replacements pending — counts. Columns: `sraNumber`,
`customerName`, `soNumber`, `customerReturnRef`, `requestedDate`, `returnByDate` (date-only), `intent`,
`lineCount`, `quantity`, `receivedQuantity`, `receivedShort`, `coreRmaNumber`, `status`, audit. Filters:
`customerId`, `soId`, `status`, `intent`, `reasonCode`, `requestedFrom`/`To`, `overdueOnly`. Actions: View ·
Edit · Submit · Withdraw · Cancel · Decline replacement · Print · Open RMA (core route, read). Export ⊇ grid.
Empty state: *No return authorisations.*

## R32 additions (PRD 2026-10-24, `D-20`)

Rows added by the R32 fold (FRD-TRADE §4.15). Numbers continue each kind's sequence; where a number exists on one side of the purchase / sales mirror only, the asymmetry is stated in FRD-TRADE §5 rows M35…M40.

| ID | Kind | Rule | Refusal / effect | Source |
|---|---|---|---|---|
| TSR-GRD-07 | guard | Intent `WARRANTY_REPLACEMENT`: the shipped unit's serial named; within the item's warranty days from the core shipment date; never proposes a credit note | `422 TRADE_RETURN_OUT_OF_WARRANTY` | FR-758 |
| TSR-T4-06 | effect | Intent `CREDIT`, RMA `RECEIVED` and core QC disposition posted → one `SALES_RETURN` proposal (accepted qty × SO price, tax reversal, original invoice no) handed over (`CN-18`) | — | FR-775 |

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
| 2026-10-23 | every T1, guard, unreachable, T3 and T4 row | `Source` column added, filled from FRD-TRADE §4, so every rule traces to the FR it proves | R30 `CP-FR-008` |
| 2026-10-23 | §0 fields, `TSR-GRD-01`…`-03`, `-T1-04`, `-T4-03`, `-GRD-06`, every T2 row | R31: header `reason_code_id` and line reasons as `whb_reason_codes` (F-TR-007); allowance counts live + matched only (F-TR-015); `REPLACE` needs an open SO (F-TR-002); stale-write code `409 CONCURRENT_MODIFICATION` (`TPR-OPEN-03`); T2 Source FRs (F-TR-019) | R31 |
| 2026-10-24 | every row citing a core event | P8 decision record `EV-1` (DECISIONS `D-19`): every outbox event code renamed to the dotted `whb_event_types` vocabulary of registry R.4 (PC-42) — e.g. `purchase_order.amended`, `demand_order.shipped`, `rma.matched`, `supplier_return.dispatched`; no behaviour change | decision record P8 wave 1/2 |
| 2026-10-25 | `TSR-GRD-07`, `TSR-T4-06` (new, *R32 additions*) | R32 fold of the client PRD (`D-20`): warranty-replacement intent, credit-note proposal | R32 / `D-20` |

## 8. Invariants and scenarios

`WH-SC-562`…`WH-SC-564`, `WH-SC-578`, `WH-SC-581`, `WH-SC-587`.

## 9. Open rows

`OD-33` (blocking until `p8-15` lands).
