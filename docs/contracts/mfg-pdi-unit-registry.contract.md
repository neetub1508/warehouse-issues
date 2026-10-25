# Functional Contract — Manufacturing units: chassis / VIN series, as-built binding, PDI gate and certificate, unit registry, traceability, Form 22

> **What this is.** The functional truth for the R32 unit layer of `warehouse-manufacturing` (`D-20` items 3, 4): unit
> serial (chassis / VIN) series and assignment at the first stage, **as-built binding** of serial-controlled parts to the
> unit (MD-11 / MD-41 narrowed, MD-48), the **PDI gate** per vehicle with a per-model checklist and SO-specific points, the
> QC-Manager-signed **PDI certificate**, FG receipt only after PDI and PDI before dispatch from stock (MD-49), the
> **manufacturer unit registry** that warranty reads (never `services`), chassis traceability both ways, and the
> homologation / Form 22 / VAHAN data per unit. FRD-MFG §6.1 FR-811…FR-820.
>
> **What this is not.** The inspection engine, inspector segregation and result approval are core (`p8-06`, `p8-19`);
> the receipt movement is [`mfg-production-receipt.contract.md`](mfg-production-receipt.contract.md); job cards are
> [`mfg-shop-floor.contract.md`](mfg-shop-floor.contract.md). Warranty claims themselves are not built here.
>
> **Status.** Derived 2026-10-25 (v0) under `D-20`. Statutory content (VIN check digit, Form 22 fields, VAHAN layout)
> **RE-VERIFY**. Not ratified; run through `functional-reviewer` before `P10-21`, `P10-22`, `P10-23` are built.

---

## 0. Identity

| | |
|---|---|
| **Workflow** | series configured → first job card of a batch starts → unit serials assigned (`whm_unit_wip` rows, no core serial yet) → parts scanned and bound at consuming stages; each booking records every unit's outcome → last stage complete → units `AWAITING_PDI` → PDI (100 %, model plan + SO points, serials match; rework loops back to `AWAITING_PDI`) → QC Manager signs through the approval engine (`WHM_PDI`) → certificate PDF → FG receipt of signed units creates the core serial → registry `IN_STOCK` → dispatch (PDI still valid, type approval valid) → `DISPATCHED` → core `INVOICE_ACKNOWLEDGED` → `SOLD`, warranty start (registry is the warranty authority) → return → `RETURNED` → re-PDI → `IN_STOCK`; scrap before or after receipt; part replacements rebind through the port |
| **Module** | `warehouse-manufacturing`; core `whb_serials` for unit and part serials; core inspection (source `PDI_UNIT`, MFG-registered); `UnitRegistryPort` declared in core by `P10-23` (optional bean) |
| **Owning tasks** | `issues/p10-21.md` (series, binding) · `issues/p10-22.md` (PDI) · `issues/p10-23.md` (registry, traceability, Form 22) |
| **Primary tables** | `whm_unit_serial_series`, `whm_unit_serial_voids`, `whm_unit_wip`, `whm_unit_bindings` (`V562070`); `whm_pdi_order_points`, `whm_pdi_records`, `whm_pdi_certificates` (`V562080`); `whm_unit_registry`, `whm_unit_part_replacements`, `whm_type_approvals` (`V562090`) |
| **Status columns** | unit WIP `PLANNED`/`IN_PROCESS`/`AWAITING_PDI`/`REWORK`/`REJECTED`/`COMPLETED`/`RECEIVED`/`SCRAPPED`/`CANCELLED` (`whm_unit_wip.state`, the pre-receipt unit, `D-21` item 8); PDI record `OPEN`/`PASSED`/`REWORK`/`HELD`/`SIGNED`; certificate `VALID`/`SUSPENDED`/`SUPERSEDED`; registry `IN_STOCK`/`DISPATCHED`/`SOLD`/`RETURNED`/`SCRAPPED` — no `CHECK` (`D-10`) |

## 1. T1 — State machine

### 1.1 Transitions

| ID | From | Event | To | Guard | Actor | Side effects | Source |
|---|---|---|---|---|---|---|---|
| PUR-T1-01 | — | First job card of a unit-serial batch starts (or release, per `unit_serial.assign_at`) | unit WIP `IN_PROCESS` (first start) / `PLANNED` (release) | `PUR-GRD-01` | system | one `whm_unit_wip` row per unit with the next value of the series (or the pre-printed range), sequence advanced under row lock; **no `whb_serials` row** — the core serial is created by the FG receipt (`PRC-T4-20`), so core's stock-status model never holds a pre-receipt unit (`D-21` item 8) | FR-811 |
| PUR-T1-02 | unit `PLANNED` · `IN_PROCESS` | *Void* (spoiled plate) | serial value voided | reason | `whm_unit_serial_series:void` | `whm_unit_serial_voids` row; the same `whm_unit_wip` row takes the next serial value (bindings and events kept) | FR-811 |
| PUR-T1-03 | — | Scan a part serial at a consuming stage | binding live | `PUR-GRD-02` | `whm_unit_bindings:bind` | binding row on the `whm_unit_wip` unit; consumption of that serial by the stage backflush (`SFL-T4-02`) | FR-812 |
| PUR-T1-04 | binding live | *Replace* | old unbound, new bound | reason; new serial `PUR-GRD-02` | `whm_unit_bindings:replace` | both rows audited | FR-812 |
| PUR-T1-05 | unit `PLANNED` | First job card of its batch starts | `IN_PROCESS` | — | system | `current_operation_seq`, `current_job_card_id` set | FR-811 |
| PUR-T1-06 | unit `IN_PROCESS` · `REWORK` | A booking (`SFL-T1-16`) names the unit's outcome at the card | good → `IN_PROCESS` at the next operation · rework → `REWORK` · rejected → `REJECTED` · scrap → `SCRAPPED` (`PUR-T1-07`) | `SFL-GRD-14` | `whm_job_cards:book` | one `whm_job_card_events` row per unit (`UNIT_GOOD` / `UNIT_REWORK` / `UNIT_REJECTED` / `UNIT_SCRAPPED`, `confirmation_id`) — "which unit failed at stage n" is a backend read over these rows; rework → rework job card (`QRW-T1-22`); rejected → `SFL-T1-21` disposition | FR-810, FR-812 |
| PUR-T1-07 | unit `IN_PROCESS` · `REWORK` · `REJECTED` · `AWAITING_PDI` | Unit scrapped: booked scrap, `SFL-T1-21` disposition `SCRAP`, or *Scrap unit* (the exit after `409 REWORK_LIMIT_REACHED`) | `SCRAPPED` (terminal) | `PUR-GRD-09` | the booking / disposition verb; *Scrap unit* `whm_unit_wip:scrap` | live bindings unbound (`unbind_reason_code_id` `UNIT_SCRAPPED`); bound part serials stay consumed — a recovered part re-enters stock only through a store return against the order (`p8-11`); batch `scrapped_quantity` + 1 and the batch's receipt no longer waits for the unit; no registry row (never received) | FR-810, FR-812 |
| PUR-T1-08 | unit `PLANNED` | *(effect)* order unreleased or cancelled before any card started (`PRO-T1-12`, `-20`) | `CANCELLED` (terminal) | — | system | each serial value voided with the system reason `ORDER_CANCELLED` (never reused, `PUR-UNR-01`) | FR-811 |
| PUR-T1-10 | unit `IN_PROCESS` at the last operation | Last-stage good booked for the unit | `pdi_required` → `AWAITING_PDI` (`pdi_attempt_no` + 1); otherwise `COMPLETED` | `PUR-GRD-03` | system | `last_stage_completed_at` | FR-813 |
| PUR-T1-11 | unit `AWAITING_PDI` · registry `IN_STOCK` (stock PDI) | *Start PDI* | PDI record `OPEN` | `PUR-GRD-04` | `whm_pdi_records:start` | core inspection `PDI_UNIT` with the model plan + order points; serials-match criterion computed; **stock PDI: the unit's `VALID` certificate → `SUSPENDED`** (dispatch refused until a new one is signed, `PUR-GRD-05`) | FR-813, FR-816 |
| PUR-T1-12 | `OPEN` | Record outcome — acted on only at the inspection's **result-final** event (`QRW-T1-23`: completed with `result_approval_status` `NOT_REQUIRED`, or `APPROVED`, `p8-19`) | `PASSED` / `REWORK` / `HELD` | inspector ≠ producer (`403 INSPECTOR_IS_PRODUCER`, `p8-19`) | `whm_pdi_records:record` | `REWORK`: production PDI → unit `REWORK` + rework job card (`QRW-T1-22`); stock PDI → `PUR-T1-15`; a `REWORK` records core outcome `REJECT` on the failed checklist lines, so core raises one NCR with source type `PDI_INSPECTION` (`NCR-T1-01`, `p8-17`); `HELD` reason `PDI_HOLD`; a **returned** result (`RETURNED`) keeps the record `OPEN` for re-recording and changes nothing else | FR-813 |
| PUR-T1-13 | `HELD` | Release hold | `OPEN` | QC Manager | `whm_pdi_records:release_hold` | — | FR-813 |
| PUR-T1-14 | `PASSED` | *Submit for signature* opens one engine request of document type `WHM_PDI` (`p8-30`, approve verb `whm_pdi_records:sign`, default policy `SINGLE_LEVEL`, `excludedActorIds` frozen = the inspector, every result recorder and the unit's producers); the final approval **is** the Sign | `SIGNED` | result final (`QRW-T1-23`); `DAP-GRD-03` (maker / submitter / prior-level exclusion, `ADMIN` refused too), kept code `403 PDI_SELF_SIGN` | engine (`whm_pdi_records:sign`) | `PDC-` certificate `VALID`, PDF rendered (`PDI_CERTIFICATE`) and stored as a platform document; the unit's earlier certificate (`VALID` / `SUSPENDED`) → `SUPERSEDED`; production PDI: unit `COMPLETED`; engine reject or withdraw leaves the record `PASSED` unsigned and re-submittable | FR-814 |
| PUR-T1-15 | stock PDI `REWORK` (registry `IN_STOCK`) | *(effect)* | unit WIP `REWORK`; certificate stays `SUSPENDED` | the serial's position is allocatable and unreserved | system | `STATUS_CHANGE` `AVAILABLE → REJECTED` (`MPR-T1-10`) and a rework **order** (`QRW-T4-06`, `-07`: component = the unit serial in `REJECTED`, output = the same serial, `rework_of_inspection_id` = the PDI inspection) — never a rework job card (`QRW-UNR-20`); its receipt needs a fresh signed `PASS` from PDI attempt n + 1 against the rework order (`PUR-GRD-08`) | FR-810, FR-816 |
| PUR-T1-16 | unit `REWORK` | *(effect)* its rework job cards complete (`QRW-T1-22`) | PQC rework → `IN_PROCESS` at the next operation (or `AWAITING_PDI` after the last); PDI rework → `AWAITING_PDI` (`pdi_attempt_no` + 1) once the rework cards of the named operation **and every later operation** have completed | — | system | `rework_count` + 1 | FR-810 |
| PUR-T1-20 | unit `COMPLETED` | FG receipt posted for the unit | unit `RECEIVED`; registry `IN_STOCK` (the row is created in `IN_STOCK`; there is no stored `BUILT` state — build data is the unit WIP history) | `PRC-GRD-30` | system (`PRC-T4-20`) | core `whb_serials` row created at the receipt location in `AVAILABLE`; `whm_unit_wip.unit_serial_id` set; registry row with build data and bound parts | FR-817 |
| PUR-T1-21 | `IN_STOCK` | Shipment posted | `DISPATCHED` | `PUR-GRD-05`, `PUR-GRD-06` (via MD-35 guard) | system | customer, dispatch ref, date | FR-817 |
| PUR-T1-22 | `DISPATCHED` | Core event `INVOICE_ACKNOWLEDGED` (`D-21` item 3: shipment → invoice no. / date and serial list) | `SOLD` | `PUR-GRD-10` | system — MFG listener, idempotent on the event id (a replay writes nothing) | `invoice_ref`, `sale_date` = invoice date; `warranty_start_date` (= sale date, or dispatch date with `warranty_starts_at = DISPATCH`) and warranty end written to the registry **and** to the core serial's warranty fields (`PUR-T4-04`) | FR-817 |
| PUR-T1-23 | `DISPATCHED` · `SOLD` | Customer return receipt of the serial posted (core return, `p8-11`) | `RETURNED` | — | system | `last_returned_at` stamped; the certificate → `SUSPENDED`; the next dispatch needs a fresh PDI (`PUR-GRD-05`) | FR-816, FR-817 |
| PUR-T1-24 | any but `SCRAPPED` | `recordPartReplacement` | unchanged | `PUR-GRD-07` | port / `whm_unit_registry:record_part_replacement` | **one transaction:** the old serial's live binding unbound (`unbound_at`, reason `PART_REPLACED`, `replaced_by_binding_id`), a new live `whm_unit_bindings` row bound (`binding_source = FIELD_REPLACEMENT`; `component_serial_id` when the serial exists in core, else `external_serial_value`) and the `whm_unit_part_replacements` row; lookup returns the new serial; history kept | FR-818 |
| PUR-T1-25 | `RETURNED` | The returned serial moves into an allocatable FG status (core return disposition `RESTOCK_SELLABLE`) | `IN_STOCK` | — | system | resellable; the last sale's customer, invoice and warranty values stay on the row until the next dispatch / invoice overwrite them (history in the audit log) | FR-817 |
| PUR-T1-26 | `IN_STOCK` · `RETURNED` | A scrap movement of the serial posted (core scrap, `MPR-T1-04`…`-07`) | `SCRAPPED` (terminal) | — | system | live bindings unbound (`UNIT_SCRAPPED`) | FR-817 |
| PUR-T1-30 | — | Generate VAHAN export / print Form 22 | — | each unit's model has a valid type approval | `whm_type_approvals:generate_vahan` / print | CSV in the configured layout (**RE-VERIFY**); `form22_issued_on` stamped | FR-820 |

### 1.2 Guards

| ID | Predicate | Refusal | Source |
|---|---|---|---|
| PUR-GRD-01 | The item × site has an active series; a pre-printed range has a free value; with `ISO_3779_17` every generated or typed VIN has a valid check digit and 17 characters (**RE-VERIFY**) | `409 UNIT_SERIAL_SERIES_MISSING`; `409 UNIT_SERIAL_RANGE_EXHAUSTED`; `422 VIN_CHECK_DIGIT_INVALID` | FR-811 |
| PUR-GRD-02 | Part serial exists for the BOM line's item, is on hand at the consuming location, and is not bound to another live unit | `409 SERIAL_NOT_AVAILABLE`; `409 SERIAL_ALREADY_BOUND` | FR-812 |
| PUR-GRD-03 | Stage completion: every serial-controlled line of the stage bound for every unit | `422 UNIT_BINDING_INCOMPLETE` | FR-812 |
| PUR-GRD-04 | PDI only for a unit `AWAITING_PDI`, or a registry unit `IN_STOCK` (stock PDI); one `OPEN` record per unit | `409 PDI_NOT_ALLOWED`; `409 PDI_ALREADY_OPEN` | FR-813 |
| PUR-GRD-05 | Outbound shipment of a `pdi_required` serial needs a `VALID` certificate (a `SUSPENDED` one never qualifies) signed ≤ `pdi_revalidate_days` ago and after the registry's `last_returned_at` | `409 PDI_REQUIRED_BEFORE_DISPATCH` | FR-816 |
| PUR-GRD-06 | Dispatch to a customer needs the model's type approval valid on the dispatch date | `409 TYPE_APPROVAL_NOT_VALID` | FR-820 |
| PUR-GRD-07 | Part replacement: unit registered; old serial in a **live** binding of the unit (after a replacement, the new serial is the live one); new serial not live on another unit; idempotency key unseen (replay returns the original) | `404 UNIT_NOT_REGISTERED`; `409 PART_NOT_BOUND` | FR-818 |
| PUR-GRD-08 | FG receipt of a `pdi_required` unit only with a signed `PASS` certificate of its latest attempt (for a rework order, an attempt opened after the rework order's release) | `422 PDI_NOT_PASSED` | FR-815 |
| PUR-GRD-09 | Scrap unit: unit WIP not `RECEIVED` / `SCRAPPED` / `CANCELLED`; no `OPEN` PDI record; reason active in `PRODUCTION_SCRAP` | `409 UNIT_NOT_SCRAPPABLE` · `unitId`; `422 REASON_REQUIRED` · `reasonCodeId` | FR-810 |
| PUR-GRD-10 | `INVOICE_ACKNOWLEDGED`: a listed serial with a registry row must be `DISPATCHED` (a serial with no registry row is not a unit-serial item and is skipped) | `409 UNIT_NOT_DISPATCHED` — the listener fails and core's outbox redelivers | FR-817 |

### 1.3 Unreachable

| ID | Never happens | Why | Source |
|---|---|---|---|
| PUR-UNR-01 | A voided chassis number reused | `whm_unit_serial_voids` uk + series check | FR-811 |
| PUR-UNR-02 | One part serial live on two units | partial unique index on live bindings | FR-812 |
| PUR-UNR-03 | Warranty reading `services` tables | registry + port only (`D-20` item 4) | FR-817, FR-818 |
| PUR-UNR-04 | A certificate edited | re-PDI issues a new one, the old `SUPERSEDED` | FR-814 |
| PUR-UNR-05 | A pre-receipt unit held as a core serial or stock status | `whm_unit_wip` holds it; `whb_serials` is created by the receipt (`PUR-T1-20`) | FR-811, FR-828 |
| PUR-UNR-06 | Two warranty truths for a unit-serial item | the registry is the warranty authority and writes the core serial's warranty fields; core's despatch rule skips unit-serial items (`LSS-T4-01`, `D-21` item 3) | FR-817 |
| PUR-UNR-07 | A dispatch on a certificate whose stock re-PDI is open or failed | `SUSPENDED` on Start (`PUR-T1-11`); `PUR-GRD-05` | FR-816 |
| PUR-UNR-08 | A unit with no exit after the rework limit | *Scrap unit* (`PUR-T1-07`) | FR-810 |

## 2. T2 — Action × role × state

| ID | Action | Permission | Persona | Source |
|---|---|---|---|---|
| PUR-T2-01 | Maintain series, void | `whm_unit_serial_series:*` | production engineer | FR-811 |
| PUR-T2-02 | Bind / replace | `whm_unit_bindings:bind/replace` | operator, supervisor | FR-812 |
| PUR-T2-03 | PDI record / submit / sign | `whm_pdi_records:record` / `:submit` / `:sign` (the `WHM_PDI` engine level) | QC inspector / QC Manager | FR-813, FR-814 |
| PUR-T2-04 | Registry read, export; part replacement | `whm_unit_registry:view/export/record_part_replacement` | service / warranty desk | FR-817, FR-818 |
| PUR-T2-05 | Type approvals — add / edit / deactivate on the WS-391 *Type Approvals* tab, VAHAN export | `whm_type_approvals:view,create,edit,delete,export,generate_vahan` (delete only while unreferenced) | homologation engineer | FR-820 |
| PUR-T2-07 | Unit WIP view, scrap a unit | `whm_unit_wip:view`, `:export`, `:scrap` | production manager | FR-810, FR-811 |
| PUR-T2-06 | Traceability report | `whm_unit_registry:view`, `:export` | quality, recall team | FR-819 |

## 3. T3 — Time-driven rules

| ID | Trigger | Effect | Source |
|---|---|---|---|
| PUR-T3-01 | Type approval / COP `valid_to` within 30 days | one alert per approval | FR-820 |
| PUR-T3-02 | Stock unit's certificate passes `pdi_revalidate_days` | listed on WS-390 *Re-PDI due* (read-time) | FR-816 |

## 4. T4 — Cross-entity effects

| ID | Cause | Effect | Source |
|---|---|---|---|
| PUR-T4-01 | Binding live | the stage backflush consumes exactly the bound serial | FR-812 |
| PUR-T4-02 | Certificate signed | the unit becomes receivable (`PRC-GRD-30`) and its PDF is linked on the registry | FR-814, FR-815 |
| PUR-T4-03 | Traceability forward / backward | backend read over bindings, unit WIP, registry and `whb_transformations` (FR-648) — recall list exportable | FR-819 |
| PUR-T4-04 | Registry `SOLD` / `DISPATCHED` with `warranty_starts_at = DISPATCH` | the registry writes the core `whb_serials` warranty start / end and `sold_to_counterparty_id` for the unit serial (`LSS-T4-01` skips unit-serial items) | FR-817 |
| PUR-T4-05 | Core builds the `INVOICE_REQUEST` line of a unit serial (`p8-23`) | the chassis and its live bound part serials are read through `UnitRegistryPort.findByUnitSerial` (PRD §12) | FR-817, FR-818 |

## 5. T5 — Screen contract

| ID | Screen | Contents | Source |
|---|---|---|---|
| PUR-T5-01 | WS-389 Unit Serial Series | Department + voids tab; pattern preview computed by the backend | FR-811 |
| PUR-T5-02 | WS-390 PDI | Service Vehicle; record (checklist incl. SO points, serials-match), sign, certificate print; *Re-PDI due* filter | FR-813…FR-816 |
| PUR-T5-03 | WS-391 Unit Registry · WS-392 Chassis Traceability | Customer read grid (Parts · Replacements · Form 22 tabs) · report forward / backward with export; WS-392 columns `direction`, `level`, `unitVin`, `componentItem`, `componentSerial`, `lotCode`, `batchNo`, `mrnNumber`, `grnNumber`, `poNumber`, `supplierName`, `customerName`; filters `serialOrLot`, `direction`, `warehouseId` (plant), `itemId`, `counterpartyId` (vendor / customer), date range (`DateRangePicker`) | FR-817…FR-820 |
| PUR-T5-04 | WS-391 *Type Approvals* tab | Department reference: grid `whm_type_approvals` · scope `WAREHOUSE_MFG_TYPE_APPROVAL` (`itemCode`, `agency`, `tacNumber`, `copCertificateNumber`, `validFrom`, `validTo` `formatDateSync`, `isActive`, audit); Add / Edit modal (`DatePicker` validity, TAC / COP certificate attached as a platform document), View modal; deactivate once referenced | FR-820 |
| PUR-T5-05 | WS-388 *Units* tab | grid `whm_unit_wip` · scope `WAREHOUSE_MFG_UNIT_WIP` (`unitSerial`, `batchNo`, `currentOperationSeq`, `state`, `reworkCount`, `pdiAttemptNo`, audit); row action *Scrap unit* (reason modal, refusal in the modal) | FR-810, FR-811 |

## 6. Error codes

`UNIT_SERIAL_SERIES_MISSING`, `UNIT_SERIAL_RANGE_EXHAUSTED`, `VIN_CHECK_DIGIT_INVALID`, `SERIAL_NOT_AVAILABLE`,
`SERIAL_ALREADY_BOUND`, `UNIT_BINDING_INCOMPLETE`, `PDI_NOT_ALLOWED`, `PDI_ALREADY_OPEN`, `PDI_SELF_SIGN`, `PDI_NOT_PASSED`,
`PDI_REQUIRED_BEFORE_DISPATCH`, `TYPE_APPROVAL_NOT_VALID`, `UNIT_NOT_REGISTERED`, `PART_NOT_BOUND`, `UNIT_NOT_SCRAPPABLE`,
`UNIT_NOT_DISPATCHED`, `UNIT_OUTCOME_MISMATCH`, `TYPE_APPROVAL_REFERENCED` — all *(proposed)*.

## 7. Edge cases

| ID | Case | Expected | Source | Scenario |
|---|---|---|---|---|
| PUR-EC-01 | Unit scrapped after binding | before receipt: unit WIP `SCRAPPED` (`PUR-T1-07`, no registry row); after receipt: registry `SCRAPPED` (`PUR-T1-26`); bindings unbound with reason; parts free for re-use only after a return to stock | FR-812, FR-817 | 788 |
| PUR-EC-02 | `INVOICE_ACKNOWLEDGED` arrives before dispatch | the listener fails `409 UNIT_NOT_DISPATCHED` (`PUR-GRD-10`); core's outbox redelivers | FR-817 | 791 |

## 8. Out of scope

Warranty claims processing; Form 21 and dealer schemes (`D-20` item 4); battery EPR filing (the backward trace gives the
quantities; the filing is outside warehouse); mobile (`D-20` item 5).

## 9. Amendments

| Date | Change |
|---|---|
| 2026-10-25 | v0 derived from FRD-MFG §6.1 (R32, `D-20`; MD-11 / MD-41 narrowed by MD-48) |
| 2026-10-25 | R32-fix (`R32-functional-review-mfg-shop.md`, `D-21` items 3, 6, 8): unit WIP table and its states, no core serial before receipt (F-R32MS-001); `SOLD` from core `INVOICE_ACKNOWLEDGED`, registry is the warranty authority (F-R32MS-002, -020); `RETURNED → IN_STOCK`, scrap before and after receipt (F-R32MS-004); PDI rework return path and *Scrap unit* (F-R32MS-007); PDI signature through the engine, `WHM_PDI` (F-R32MS-008); acting only on the result-final event (F-R32MS-010); certificate `SUSPENDED`, stock rework through a rework order (F-R32MS-012); replacement rebinds (F-R32MS-014); PDI NCR source (F-R32MS-023); type-approval tab and traceability columns (F-R32MS-022, -025); no stored `BUILT`, `last_returned_at` (F-R32MS-029) — `PUR-T1-01`…`-26`, `PUR-GRD-04`, `-05`, `-07`…`-10`, `PUR-UNR-05`…`-08`, `PUR-T2-03`, `-05`, `-07`, `PUR-T4-03`…`-05`, `PUR-T5-03`…`-05`, `PUR-EC-01`, `-02` |

## 10. Invariants and scenarios

`L-12` (genealogy), MD-35, MD-48, MD-49; scenarios `WH-SC-787`…`-792`.

## 11. Open rows

| ID | Question | Default |
|---|---|---|
| PUR-OPEN-01 | When is the chassis assigned; which parts are bound (PRD Q-PR3)? | first stage; every serial-controlled BOM line |
| PUR-OPEN-02 | Current PDI checklist and certificate format (PRD Q-Q2) | model plan + SO points; certificate per FR-814 |
