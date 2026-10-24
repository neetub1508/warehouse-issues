# Functional Contract — Material Receipt Note (MRN): authorisation into stores, stock availability, print

> **What this is.** The functional truth for the stores' **authorisation** of received and inspected
> material: the `MRN_PENDING` status that keeps it unissuable, the MRN document (prepare → submit →
> authorise / reject → cancel), the status change and putaway that authorisation triggers, the
> separation of the authoriser from the inspector, and the MRN and GRN prints. It sits between
> `RQP-T1-09`/`RQP-T1-20` (GRN post, QC release) and `RQP-T1-24` (putaway creation) and **moves the
> putaway trigger** when the site setting is on.
>
> **Status.** Derived 2026-10-22 (v0) from [`frd/FRD-STORES.md`](../frd/FRD-STORES.md) `FR-527`, `FR-538`,
> `STO-D8`. Not ratified.

---

## 0. Identity

| | |
|---|---|
| **Workflow** | GRN post / QC release → stock lands `MRN_PENDING` → MRN prepared (from one GRN) → submitted → authorised (status change to `AVAILABLE` + putaway) or rejected back to draft → printed |
| **Module** | `warehouse`; status seed in `warehouse-base` (`V501232`) |
| **Domain baseline** | `FR-127`, `FR-129` (allocatable flag), `FR-174` (availability), `FR-408`, `FR-527`, `STO-D8` · `RQP-T1-20`, `RQP-T1-24`, `RQP-T4-05` · `P2-14` printing (`wh_print_templates`, `WarehousePrintDataProvider`) |
| **Owning task** | `issues/p8-08.md`; depends on `p8-04` (billed qty for the MRN), `p8-06`, `p2-14` |
| **Primary tables** | new `wh_material_receipt_notes`, `wh_material_receipt_note_lines` (`V511317`); `whb_stock_statuses` row `MRN_PENDING` (`is_on_hand = true`, `is_available_to_promise = false`, `is_allocatable = false`, `is_pickable = false`, `is_shippable = false`, `is_countable = true`, `requires_reason_to_enter = false`, `requires_reason_to_leave = false`; `V500005` columns) (`V501232`); `whb_document_types` row `MATERIAL_RECEIPT_NOTE`; settings `warehouse.stores.mrn_required` (per site), `warehouse.stores.mrn_authoriser_may_be_inspector` |
| **Status column** | `wh_material_receipt_notes.status` — no CHECK (`D-10`) |
| **Permission resources** | `wh_material_receipt_notes:{view,view:all,view:branch,create,edit,submit,authorise,cancel,export}` (`V511407`; the scope pair per `V511000:60-71`, R29 F1) |
| **Routes** | WS-266 `/warehouse/stores/mrns`, WS-267 `/[id]`; WS-077 gains **Prepare MRN** and **Print** |
| **Contract version** | `v0 — 2026-10-22` |

### Acceptance checks

| # | Expects | Delivered by |
|---|---|---|
| A1 | Received material is not usable until the MRN is authorised (`WH-SC-454`, `-455`) | `MRA-T4-01`, `MRA-GRD-06` |
| A2 | The authoriser is a different person from the preparer and (by default) the inspector (`WH-SC-454`) | `MRA-GRD-03`, `-04` |
| A3 | Authorise is what creates the putaway and makes stock `AVAILABLE` | `MRA-T4-02` |
| A4 | The MRN prints with authoriser and time; GRN prints too (`WH-SC-456`) | `MRA-T2-07` |
| A5 | Setting off = today's behaviour exactly (`WH-SC-457`) | `MRA-T4-04` |

---

## 1. T1 — State machine

### 1.1 Status inventory

| Entity | Status | Represented by | Reachable via | Exits via | Kind |
|---|---|---|---|---|---|
| MRN | `DRAFT` | `status` | `MRA-T1-01`, `-04` | `-02`, `-05` | initial |
| MRN | `SUBMITTED` | `status`; `submitted_by/at` | `MRA-T1-02` | `-03`, `-04` | active |
| MRN | `AUTHORISED` | `status`; `authorised_by/at` | `MRA-T1-03` | none | **terminal** |
| MRN | `CANCELLED` | `status`; reason | `MRA-T1-05` | none | **terminal** |
| Stock | `MRN_PENDING` | `whb_stock_statuses` row, position grain | `MRA-T4-01` | `MRA-T4-02` | non-allocatable |

### 1.2 Transitions

| ID | From | Event | To | Guard | Actor | Side effects | Reason? | UI |
|---|---|---|---|---|---|---|---|---|
| MRA-T1-01 | — | **Prepare** from a `POSTED` GRN | `DRAFT` | `MRA-GRD-01`, `-02` | `wh_material_receipt_notes:create` | gapless `MRN` number at create; one line per GRN line with `MRN_PENDING` quantity not on another live MRN: `quantity_authorisable` (frozen at prepare, re-read at authorise), `billed`, `received`, `accepted`, `rejected` (copied facts), PO rate and value (display), lot, serials count, current location(s), inspection number | no | WS-077 **Prepare MRN**; WS-266 **Add** (pick a GRN) |
| MRA-T1-02 | `DRAFT` | Submit | `SUBMITTED` | ≥ 1 line; remarks optional | `wh_material_receipt_notes:submit` | `submitted_by/at` | no | WS-267 **Submit** |
| MRA-T1-03 | `SUBMITTED` | **Authorise** | `AUTHORISED` | `MRA-GRD-03`…`-05` | `wh_material_receipt_notes:authorise` | `MRA-T4-02` in **one transaction**; `authorised_by/at` | no | WS-266 row / WS-267 **Authorise** |
| MRA-T1-04 | `SUBMITTED` | Reject | `DRAFT` | rejecter ≠ `created_by` and ≠ `submitted_by`, else `403 MRN_SELF_APPROVAL` (R29 F26) | `wh_material_receipt_notes:authorise` | `rejected_by/at`, `rejection_note`; nothing moves; the maker may cancel and raise a receipt reversal or re-inspection | **yes** | WS-267 **Reject** |
| MRA-T1-05 | `DRAFT` | Cancel | `CANCELLED` | — | `wh_material_receipt_notes:cancel` | lines released (their quantity may go on a new MRN); number stays issued | **yes** | WS-267 **Cancel** |

### 1.3 Guards

| ID | Predicate | Refusal | Backstop | Source |
|---|---|---|---|---|
| MRA-GRD-01 | GRN `POSTED` and at least one of its lines holds `MRN_PENDING` stock — **the MRN flow is keyed on the pending stock, not on the setting**: turning `mrn_required` off for a site stops *new* receipts routing to `MRN_PENDING` but never strands stock already there, which is still prepared, submitted and authorised as before (grandfathered, R29 F10). With the setting off and nothing pending the action is not offered | `409 MRN_NOTHING_PENDING` / `409 MRN_GRN_NOT_POSTED` | — | FR-527 |
| MRA-GRD-02 | at least one GRN line has `MRN_PENDING` quantity not on a live MRN line | `409 MRN_NOTHING_PENDING` | partial uk on lines `(grn_line_id, mrn_id)`; service sum check | FR-527 |
| MRA-GRD-03 | authoriser ≠ `created_by` and ≠ `submitted_by` | `403 MRN_SELF_APPROVAL` (the core `<DOCUMENT>_SELF_APPROVAL` convention, `WhSupplierReturnValidationService.java:40`, R29 F26) | — | FR-408 |
| MRA-GRD-04 | authoriser ≠ any user who dispositioned a line of the GRN to release, unless `mrn_authoriser_may_be_inspector = true` | `403 MRN_AUTHORISER_IS_INSPECTOR` | — | FR-527 |
| MRA-GRD-05 | for each line, the `MRN_PENDING` on-hand traceable to the GRN line (receipt and release movements' `source_document_*`, at lot/LPN/serial grain — the QC release movement is `source_document_type = 'QCINSP'` (`WhQualityInspectionRepository.DOCUMENT_TYPE`, `:36`) with `source_document_id` = the inspection, joined to the GRN line through `wh_quality_inspection_lines.grn_line_id` (`WhQualityInspectionLine.java:70`); the GRN posting is `GRN` (`WhGoodsReceiptPostingService.java:121`); R31 F-SR-005) ≥ `quantity_authorisable`; else the line authorises the lower figure and the response names the difference | `409 MRN_PENDING_QUANTITY_CHANGED` only when every line is zero | — | FR-527 |
| MRA-GRD-06 | nothing in `MRN_PENDING` is reservable, allocatable, issuable or transferable | refused by the existing allocatable/issuable checks (`FR-129`) — no new code path | `whb_stock_statuses.is_allocatable = false` | FR-527 |
| MRA-GRD-07 | a receipt reversal of the GRN is refused while a `SUBMITTED` MRN exists (`RQP-GRD-24` extended) | `409 RECEIPT_MRN_SUBMITTED` | — | FR-527 |
| MRA-GRD-08 | **the only path from `MRN_PENDING` into an allocatable status is MRN authorisation**: a `STATUS_CHANGE` out of `MRN_PENDING` into a status with `is_allocatable = true` is refused unless its `source_document_type = MATERIAL_RECEIPT_NOTE`; moves into non-allocatable statuses (`QUARANTINE` by a recall, `REJECTED`, `DAMAGED`) stay allowed | `409 MRN_PENDING_RELEASE_REQUIRES_MRN` | a core `WhbMovementPostGuard` bean on `STATUS_CHANGE` | FR-527 |

### 1.4 Unreachable

| ID | Must never happen |
|---|---|
| MRA-UNR-01 | a putaway task for `MRN_PENDING` stock before authorisation (when the setting is on) |
| MRA-UNR-02 | an `AUTHORISED` MRN edited, rejected or cancelled |
| MRA-UNR-03 | the same GRN line quantity authorised twice |
| MRA-UNR-04 | an MRN from a store return, a production receipt or a transfer. **MRN covers every goods receipt** — PO, blind and non-PO GRNs alike (`V510014:201-203` allows all three; all are supplier inward receipts), and nothing else (`IIS-T4-04`; MFG has its own FG receipt) (R29 F27) |

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from | Extra | Source |
|---|---|---|---|---|---|
| MRA-T2-01 | Prepare | `:create` | GRN `POSTED` with pending qty | receiving clerk | — |
| MRA-T2-02 | Edit remarks / storage location hint | `:edit` | `DRAFT` | quantities are not editable | — |
| MRA-T2-03 | Submit | `:submit` | `DRAFT` | — | — |
| MRA-T2-04 | Authorise | `:authorise` | `SUBMITTED` | `MRA-GRD-03`, `-04` | — |
| MRA-T2-05 | Reject | `:authorise` | `SUBMITTED` | reason | — |
| MRA-T2-06 | Cancel | `:cancel` | `DRAFT` | reason | — |
| MRA-T2-07 | Print MRN | `wh_print_jobs:create` | `SUBMITTED` (watermark *NOT AUTHORISED*) and `AUTHORISED` | `SYS-MRN`; reprint marked duplicate | FR-538, FR-518 |
| MRA-T2-08 | Print GRN | `wh_print_jobs:create` | GRN `DRAFT` (*provisional*) / `POSTED` / `REVERSED` (*reversed*) | `SYS-GRN` with the bill block | FR-538 |

## 3. T3 — Time-driven rules

| ID | Rule | Trigger | Changes | Notified | Job | Once? |
|---|---|---|---|---|---|---|
| MRA-T3-01 | Pending authorisation | `SUBMITTED` > `warehouse.approval.pending_alert_hours` | nothing; never auto-authorises | holders of `:authorise` at the site | `p2-23` pending-approval alert | one per episode |
| MRA-T3-02 | Stock waiting for an MRN | `MRN_PENDING` on-hand with no live MRN > `warehouse.stores.mrn_pending_alert_hours` (default 24) | nothing — tile | stores in-charge | daily | once per GRN |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in |
|---|---|---|---|
| MRA-T4-01 | setting on, and (a) GRN post (PO, blind or non-PO, `MRA-UNR-04`) of a line whose resolved received status is allocatable, or (b) QC disposition `RESTOCK_SELLABLE` of a GOODS_RECEIPT source | (a) the line is received into **`MRN_PENDING`** instead, **no putaway task** (`RQP-T1-24` suppressed); (b) the release `STATUS_CHANGE` targets `MRN_PENDING` instead of `AVAILABLE`, no putaway task | GRN posting service; disposition service |
| MRA-T4-02 | `MRA-T1-03` | per line one balanced **`STATUS_CHANGE` `MRN_PENDING → AVAILABLE`** at the location(s) holding it (`MPR-T1-10`, reason code `MRN_AUTHORISED` context `RELEASE`), `source_document_type = MATERIAL_RECEIPT_NOTE`; **then** one putaway task per line for the authorised quantity (the `RQP-T1-24` rule, now triggered here); line `status_change_movement_id` stored; outbox `material_receipt_note.authorised` | MRN service → writer → putaway service, one transaction |
| MRA-T4-03 | receipt reversal of a GRN with an `AUTHORISED` MRN | allowed per `RQP-GRD-26` (stock moved on is refused there); the MRN stays `AUTHORISED` and shows *GRN reversed* | reversal service |
| MRA-T4-04 | setting off | no new receipt routes to `MRN_PENDING`; behaviour equals `RQP` v1 for them. Stock already in `MRN_PENDING` keeps its MRN path (`MRA-GRD-01`) | — |

## 5. T5 — Screen contract

### 5.1 WS-266 Material Receipt Notes (reference: **Service Vehicle**)

| | |
|---|---|
| **Grid** | `wh_material_receipt_notes` · scope `WAREHOUSE_MRN` · sort `e.created_at DESC` |
| **Tiles** | `DRAFT` · `SUBMITTED` · `AUTHORISED` today · *GRNs awaiting MRN* |
| **Columns** | `mrnNumber`, `warehouseName`, `grnNumber`, `supplierName`, `poNumber`, `billNumber`, `billDate`, `lineCount`, `authorisableQuantity`, `value` (PO rate × qty, view-cost permission), `status`, `submittedByName`, `submittedAt`, `authorisedByName`, `authorisedAt`, audit |
| **Filters** | `warehouseId`; `status` (multi); `supplierCounterpartyId`; `grnNumber`, `poNumber`, `billNumber` (text); `authorisedFrom/To` (date); `pendingOnly` |
| **Row actions** | View · Submit · Authorise · Reject · Print · Cancel |
| **Detail WS-267** | header + lines grid (`item`, `lot`, `billed`, `received`, `accepted`, `rejected`, `authorisable`, `uom`, `rate`, `value`, `inspectionNumber`, `location`) + history |
| **Export** | grid + `createdByName`, `updatedByName` |

## 6. Out of scope

MRN for non-purchase receipts; value-based authorisation limits (`OD-29`-style matrix refused here); accounting posting at authorise (deferred); mobile.

## 7. Amendments

| Date | Change |
|---|---|
| 2026-10-22 | v0 derived. Amends `RQP-T1-24` (putaway trigger) and `RQP-T1-20` (release target) under the setting |
| 2026-10-22 | R29 dispositions: scope pair; MRN keyed on pending stock (setting change never strands it); MRN scope = every GRN; self-approval code on authorise and reject; `MRA-GRD-08` single exit; recall quarantine path stated |
| 2026-10-23 | R31: QC lineage names `QCINSP` and the inspection-line → GRN-line join (`MRA-GRD-05`, F-SR-005); `OD-26` keyed to `PRODUCTION_STORE` (`MRA-OPEN-01`, F-SR-016); `MRA-OPEN-01`…`-03` resolved (`R31-decisions`) |
| 2026-10-24 | P8 decision record `EV-1` (DECISIONS `D-19`): every outbox event code renamed to the dotted `whb_event_types` vocabulary of registry R.4 (PC-42) — e.g. `purchase_order.amended`, `demand_order.shipped`, `rma.matched`, `supplier_return.dispatched`; no behaviour change |

## 8. Invariants and scenarios

`L-1` (status change balanced); `FR-408`; scenarios `WH-SC-454`…`-457`.

## 9. Open rows

| ID | Question | Default |
|---|---|---|
| MRA-OPEN-01 | OD-26 default of `mrn_required` | on for a new site of `WAREHOUSE_TYPE` **`PRODUCTION_STORE`** (the `P7-11` rename of `WORKSHOP`; no raw-material type is seeded), off otherwise; per-site override (R31 F-SR-016). **RESOLVED (DEFAULT), 2026-10-23** (`R31-decisions`). The type only seeds the new site's setting row — a recorded exception to *"a label, not a behaviour"* (`V500012:191`): nothing at runtime reads the type |
| MRA-OPEN-02 | Should putaway be allowed **before** authorisation (stock in the bin but still `MRN_PENDING`)? | **No** in v1.1 — the stock stays at receiving/QC staging; a site that wants bin-first runs with the setting off **RESOLVED (DEFAULT), 2026-10-23** (`R31-decisions`). |
| MRA-OPEN-03 | A recall (`WhRecallService`) moves `MRN_PENDING` stock to `QUARANTINE` (allowed, `MRA-GRD-08`); does the recall's release later restore it to `MRN_PENDING` or to the status it had before? | `P8-08` verifies the recall release target in code; it must restore the **prior** status (`MRN_PENDING`), never `AVAILABLE` — `MRA-GRD-08` refuses the latter **RESOLVED (DEFAULT), 2026-10-23** (`R31-decisions`). Restore the prior status; `P8-08` verifies. |
