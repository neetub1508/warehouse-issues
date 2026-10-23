# Functional Contract — The three-leg stock transfer and in-transit ageing

> **What this is.** The functional truth for moving stock between sites: the transfer order, its depart leg
> into a **per-transfer `IN_TRANSIT` location that is a child of the source site**, its arrive leg into the
> destination, the explicit transit-loss leg, the return leg on a cancel in transit, the ownership and risk
> of in-transit stock, and the ageing of what was shipped and not received. Every rule row names its
> requirement in **Source** (`DECISIONS.md` `D-17` item 1).
>
> **What this is not.** The stock leaves the source through the one demand path (a transfer creates one demand
> order — [`outbound-despatch.contract.md`](outbound-despatch.contract.md) `ODS-T4-01`); this contract does not
> restate allocation, pick or despatch. Every leg posts through
> [`movement-post-reverse.contract.md`](movement-post-reverse.contract.md) `MPR-T1-01`.
>
> **Status.** Derived 2026-10-23 (v0) from `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` §6.9 (`FR-147`, `FR-148`,
> `FR-149`) and `FR-165`, checked against the built code in `classic` by name. Not ratified.

---

## 0. Identity

| | |
|---|---|
| **Workflow** | Create (source) or request (destination) → approve / reject → allocate → despatch (depart leg, first despatch provisions the transit location) → receive (arrive leg, partial or complete) → close, with transit loss or variance; cancel, with a return leg from `IN_TRANSIT` |
| **Module** | `warehouse` (`wh_transfer_orders`, `wh_transfer_order_lines`) over `warehouse-base` (locations, virtual-location provisioner, writer, jobs) |
| **Domain baseline** | `L-1`, `L-2`; `D-14` dated branch links (one `REGISTERED` link at every instant); `FR-177`, `FR-189` (transfer relief is into transit) |
| **Owning tasks** | `issues/p2-02.md` · `issues/p0-13.md` (dated-obligation rule) |
| **Code (as built)** | `WhTransferOrderService`, `WhTransferOrderValidationService`, `WhTransferOrderPostingService`, `WhTransferOrderDespatchEffects`, `WhbTransferOverdueArrivalJob`, `WhInTransitAgeingQueryService` |
| **Routes** | WS-090 Transfer Orders · WS-220 In-transit Ageing |
| **Contract version** | `v0 — 2026-10-23` |

---

## 1. T1 — State machine

### 1.1 Status inventory

| Entity | Status | Represented by | Reachable via | Exits via | Kind | Source |
|---|---|---|---|---|---|---|
| Transfer | `DRAFT` · `REQUESTED` | `status` | `STR-T1-01`, `-02` | `REQUESTED`: `-03`, `-04`, `-11`; `DRAFT`: `-03` (where `requires_approval`), `-05` (where not), `-11` | initial | `FR-147` |
| Transfer | `APPROVED` · `ALLOCATED` | `status` | `STR-T1-03` (`APPROVED` then `ALLOCATED` in the same request), `-05` | `-06`, `-11` | active — `APPROVED` is never left standing by a committed Approve; it is the step the demand order's allocation leaves (`V510031:52-54`) | `FR-147` |
| Transfer | `IN_TRANSIT` | `status`; `transit_location_id`, `dispatched_at` | `STR-T1-06` | `-07`, `-08`, `-11` | active — stock exists, owned by the sender | `FR-147`, `FR-148` |
| Transfer | `PARTIALLY_RECEIVED` | `status` | `STR-T1-07` | `-07`, `-08`, `-09`, `-10` | active | `FR-147` |
| Transfer | `RECEIVED` | `status`; `received_at` | `STR-T1-08` | `-09`, `-10` | active | `FR-147` |
| Transfer | `CLOSED` · `REJECTED` · `CANCELLED` | `status` | `STR-T1-09a`, `-10` / `-04` / `-11` | none | **terminal** | `FR-147` |

### 1.2 Transitions

| ID | From | Event / action | To | Guard | Actor (permission) | Side effects | Source |
|---|---|---|---|---|---|---|---|
| STR-T1-01 | — | Create at the source | `DRAFT` | `STR-GRD-01`, `-02` | `wh_transfer_orders:create` | number issued; `expected_arrival_date` held | `FR-147` |
| STR-T1-02 | — | Request at the destination | `REQUESTED` | `STR-GRD-01`, `-02` | `wh_transfer_orders:request` | as `-01` | `FR-147` |
| STR-T1-03 | `REQUESTED` · `DRAFT` (a `DRAFT` only where `requires_approval` is set — `WhTransferOrderValidationService.java:266-273`) | Approve (line quantities may be cut, never raised) | `APPROVED` → `ALLOCATED` **in the same request** | `STR-GRD-03`, `-04` | `wh_transfer_orders:approve` | approved quantities stored; the approval raises and allocates the **one demand order** for the transfer (`ODS-T4-01`, `WhTransferOrderService` `raiseDemandOrder`) | `FR-147`, `FR-177` |
| STR-T1-04 | `REQUESTED` | Reject | `REJECTED` | reason | `wh_transfer_orders:reject` | none | `FR-147` |
| STR-T1-05 | `DRAFT` where `requires_approval` is **false** | Allocate (a draft that needs no approval) | `ALLOCATED` | a `DRAFT` that requires approval is refused (`409 TRANSFER_INVALID_TRANSITION`, *"allocated by its approval"*); a transfer that already has a demand order is refused (`TRANSFER_INVALID_TRANSITION`) — `WhTransferOrderValidationService.java:197-206` | `wh_transfer_orders:allocate` | **one demand order** for the transfer (`ODS-T4-01`) | `FR-147`, `FR-177` |
| STR-T1-06 | `ALLOCATED` | First despatch of the transfer's demand order | `IN_TRANSIT` | `STR-GRD-05` | system (despatch, `wh_shipments:dispatch`) | `STR-T4-01`, `-02` | `FR-147`, `FR-148`, `FR-189` |
| STR-T1-07 | `IN_TRANSIT` · `PARTIALLY_RECEIVED` | Receive less than in transit | `PARTIALLY_RECEIVED` | `STR-GRD-06`, `-07` | `wh_transfer_orders:receive` | `STR-T4-03` | `FR-147`, `FR-148` |
| STR-T1-08 | `IN_TRANSIT` · `PARTIALLY_RECEIVED` | Receive the remainder | `RECEIVED` | `STR-GRD-06`, `-07` | `wh_transfer_orders:receive` | `STR-T4-03`; `received_at` | `FR-147` |
| STR-T1-09 | `IN_TRANSIT` · `PARTIALLY_RECEIVED` · `RECEIVED` | Write off the transit residue (shipped ≠ received) | status unchanged — the write-off is not a ladder step (`WhTransferOrderValidationService.java:214-224`); something must stand at the transit location | `STR-GRD-08` | `wh_transfer_orders:write_off_transit` | `STR-T4-04`; then `STR-T1-09a` when the residue reaches zero | `FR-147`, `FR-148` |
| STR-T1-09a | `IN_TRANSIT` · `PARTIALLY_RECEIVED` · `RECEIVED` | Transit location reaches zero residue (after a write-off) | `CLOSED` | `STR-GRD-09` | system (no verb, no permission — `validateCanCloseAtZeroResidue`) | none | `FR-147` |
| STR-T1-10 | `PARTIALLY_RECEIVED` · `RECEIVED` | Report variance and close | `CLOSED` | `STR-GRD-08`, `-09` | `wh_transfer_orders:report_variance` | `STR-T4-04` for a non-zero residue | `FR-147` |
| STR-T1-11 | `DRAFT` · `REQUESTED` · `APPROVED` · `ALLOCATED` · `IN_TRANSIT` | Cancel | `CANCELLED` | `STR-GRD-10` | `wh_transfer_orders:cancel` | demand order de-allocated; from `IN_TRANSIT`, `STR-T4-05` | `FR-147` |

### 1.3 Guards

| ID | Predicate (must hold to proceed) | Refusal: code · field | Message shape | Source |
|---|---|---|---|---|
| STR-GRD-01 | Lines are present, quantities positive, one owner per transfer | `TRANSFER_NO_LINES`, `TRANSFER_LINE_QUANTITY_INVALID`, `TRANSFER_MIXED_OWNERS` | names the line | `FR-147` |
| STR-GRD-02 | Source and destination each resolve to a `REGISTERED` branch link at the transfer date; the source branch is frozen on the transfer | `TRANSFER_SITE_UNREGISTERED`, `TRANSFER_DESTINATION_LINK_INVALID` | names the site and date | `FR-148` |
| STR-GRD-03 | The approver is not the maker | `403 TRANSFER_SELF_APPROVAL` | *"the maker may not approve their own transfer"* | `FR-147` |
| STR-GRD-04 | An approved line quantity never exceeds the requested quantity | `TRANSFER_LINE_APPROVED_ABOVE_REQUESTED` · `lines[n]` | names both quantities | `FR-147` |
| STR-GRD-05 | Despatch only of a transfer whose demand order is allocated | `DESPATCH_TRANSFER_NOT_ALLOCATED`, `DESPATCH_TRANSFER_MISSING` | names the transfer | `FR-147`, `FR-189` |
| STR-GRD-06 | Receive and transit loss are authorised **on that transfer's own transit location** — type `IN_TRANSIT`, `transit_reference_id` = this transfer — and on no other location at the source site; the receiver is scoped to the destination | `409 TRANSFER_NOT_RECEIVABLE`; `TRANSFER_NOT_AT_DESTINATION` | names the transfer and the location | `FR-148` |
| STR-GRD-07 | A receipt never exceeds what is in transit | `TRANSFER_RECEIVE_ABOVE_TRANSIT` · `lines[n].quantity`; `TRANSFER_RECEIVE_NOTHING` | names in-transit and offered | `FR-147` |
| STR-GRD-08 | A transit-loss leg carries a reason code | `TRANSFER_TRANSIT_LOSS_REASON_REQUIRED` · `reasonCodeId` | *"a transit loss names why the stock never arrived"* | `FR-147` |
| STR-GRD-09 | A transfer closes only when its transit location is empty | `409 TRANSFER_TRANSIT_NOT_EMPTY`; `TRANSFER_NOT_CLOSEABLE` | names the residue | `FR-147` |
| STR-GRD-10 | Cancel is refused while picked stock sits in staging, and a cancel from `IN_TRANSIT` names a return reason | `409 STAGED_STOCK`; `TRANSFER_RETURN_REASON_REQUIRED`; `TRANSFER_NOT_CANCELLABLE` | names the staged quantity | `FR-147` |
| STR-GRD-11 | A **bin-to-bin move** within a site is an ordinary two-line `BIN_MOVE` movement — one negative and one positive line of loose stock, two different real locations at the same site — with the same owner, item, lot, serial, stock status and duty status at both ends; no transfer document, no adjustment, no reason code | `422 BIN_MOVE_SHAPE_INVALID` · `lines` (`WhbMovementPostValidationService.java:1392`) | names what differs (line count, sign, virtual location, same location, LPN) | `FR-150` |

### 1.4 Transitions that must be unreachable

| ID | Forbidden | What makes it unreachable | Source |
|---|---|---|---|
| STR-UNR-01 | A transit **site** (a separate warehouse holding everyone's in-transit stock) | the transit location is provisioned per transfer under the source site (`IN_TRANSIT-<transfer number>`) | `FR-147` |
| STR-UNR-02 | In-transit stock resolving to a transit pool's branch, or to the destination's, before receipt | lines carry the source site; the sender holds the stock until receipt | `FR-148` |
| STR-UNR-03 | A transfer with a pick of its own, outside the demand path | `STR-T1-05` creates one demand order; despatch is `ODS-T1-*` | `FR-147`, `FR-177` |
| STR-UNR-04 | Shipped-not-received stock disappearing without a transit-loss movement | close requires an empty transit location (`STR-GRD-09`) | `FR-147` |
| STR-UNR-05 | A bin move filed as a transfer order, or changing owner or status on the way | `BIN_TO_BIN` is not a transfer type (`V501123` comment, `V511246`); the shape guard refuses a differing owner or status (`STR-GRD-11`) | `FR-150` |

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from | Extra | Source |
|---|---|---|---|---|---|
| STR-T2-01 | Create / request / edit | `wh_transfer_orders:{create,request,edit}` | — / `DRAFT` | `TRANSFER_NOT_EDITABLE` past `DRAFT` | `FR-147` |
| STR-T2-02 | Approve / reject / allocate | `wh_transfer_orders:{approve,reject,allocate}` | approve: `REQUESTED`, or `DRAFT` where `requires_approval`; reject: `REQUESTED`; allocate: `DRAFT` where not `requires_approval` | approver ≠ maker | `FR-147` |
| STR-T2-03 | Receive / write off / report variance / cancel | `wh_transfer_orders:{receive,write_off_transit,report_variance,cancel}` | as §1.2 | receiver scoped to the destination | `FR-148` |
| STR-T2-04 | In-transit ageing report | `wh_rpt_in_transit_ageing:{view,export}` | — | — | `FR-149` |

## 3. T3 — Time-driven rules

| ID | Rule | Trigger (clock) | Changes | Notified | Job | Source |
|---|---|---|---|---|---|---|
| STR-T3-01 | A transfer still in transit past its expected arrival is flagged | `expected_arrival_date` < today (injected `Clock`) | nothing — notification `WAREHOUSE_TRANSFER_ARRIVAL_OVERDUE` | source and destination stock controllers | `WhbTransferOverdueArrivalJob` | `FR-149`, `FR-165` |
| STR-T3-02 | The in-transit ageing report lists shipped-not-received quantity per transfer older than N days, so the residue is found | report run with an over-days parameter | nothing | — | WS-220 (`WhInTransitAgeingQueryService`; `IN_TRANSIT_OVER_DAYS_INVALID`) | `FR-149` |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in | Source |
|---|---|---|---|---|
| STR-T4-01 | First despatch | the transfer's own `IN_TRANSIT` location is provisioned, child of the source site, idempotently; `transit_location_id` stored | `WhTransferOrderDespatchEffects` | `FR-147` |
| STR-T4-02 | Every despatch | depart leg `TRANSFER_DEPART`: − source location, + the transfer's transit location, both at the source site, `occurred_at` = despatch | despatch → writer | `FR-147`, `FR-148`, `FR-189` |
| STR-T4-03 | Receive | arrive leg `TRANSFER_ARRIVE`: − transit location, + destination location | `WhTransferOrderPostingService` | `FR-147` |
| STR-T4-04 | Write off / variance | `TRANSIT_LOSS` from the transit location with the reason code | `WhTransferOrderPostingService` | `FR-147` |
| STR-T4-05 | Cancel from `IN_TRANSIT` | return leg `TRANSFER_RETURN`: − transit location, + source | `WhTransferOrderService.cancel` | `FR-147` |

## 5. T5 — Screen contract (web only, `D-17` item 2)

| ID | Screen | Rule | Source |
|---|---|---|---|
| STR-T5-01 | WS-090 Transfer Orders | tiles by status; row actions per §1.2 gated by §2; the view shows the transit location, quantities shipped / received / lost per line, and the frozen source branch | `FR-147`, `FR-148` |
| STR-T5-02 | WS-220 In-transit Ageing | rows per transfer and line: shipped, received, residue, days in transit, expected arrival; over-days filter | `FR-149` |

## 6. Amendments

| Date | Change |
|---|---|
| 2026-10-23 | v0 derived for `D-17` item 1 (R30 `CP-FR-007` row 8, the transfer half) |
| 2026-10-23 | R31 `F-CA-001`: `STR-T1-03`, `-05`, `-09` restated to the built ladder, `STR-T1-09a` added, §8 rows `STR-DIV-01`/`-02` replace "none found"; `F-CA-015`: WS-090 amended. `STR-OPEN-01` decided (R31 decisions) |

## 7. Invariants and scenarios

`L-1`, `L-2`, `D-14`; scenarios `WH-SC-058`, `WH-SC-121`.

## 8. Code divergences (FRD rule kept)

| ID | File:line | FR | Difference |
|---|---|---|---|
| STR-DIV-01 | `docs/BUILD-SPEC-SCREENS.md` WS-090 (amended R31) | `FR-147`, `FR-150` | WS-090 listed `transferType (BIN_TO_BIN/INTRA_SITE/INTER_SITE)` and said Receive is authorised *"regardless of site scope"*. The build has two types (`V511246__Narrow_wh_transfer_orders_type_check_to_two_values.sql`, `STR-UNR-05`) and requires destination scope (`TRANSFER_NOT_AT_DESTINATION`, `WhTransferOrderValidationService.java:600`, `STR-GRD-06`). WS-090 was amended to the contract (R31 `F-CA-015`) — **Triage 2026-10-23: AMEND-SPEC** — applied R31 (WS-090 amended to the build); stands as the rule `STR-UNR-05` / `STR-GRD-06` |
| STR-DIV-02 | `V510031:52-54`; `WhTransferOrderValidationService.java:197-224` | `FR-147` | the v0 ladder had Approve from `REQUESTED` only, a separate Allocate from `APPROVED`, and write-off as a closing step. The build approves a `DRAFT` too (where `requires_approval`), allocates inside the approval, allocates a no-approval `DRAFT` directly, and closes automatically at zero residue. The contract was corrected to the build (R31 `F-CA-001`); the FRD rule is unchanged — **Triage 2026-10-23: AMEND-SPEC** — applied R31 (contract corrected to the build, `F-CA-001`); `FR-147` defines the three legs, not the status ladder, so no FRD edit is owed |

## 9. Open rows

| ID | Question | Missing decision | Default until decided | Source |
|---|---|---|---|---|
| STR-OPEN-01 | The default N (days) of the in-transit ageing residue | **DECIDED R31 (2026-10-23): default stands** — no setting key | the report's over-days parameter, entered per run | `FR-149` |

<!-- v0 2026-10-23. Amend with /functional-contract: every change references a row id and adds a §7 row. -->
