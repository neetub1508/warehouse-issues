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
| **Workflow** | series configured → first job card of a batch starts → unit serials assigned (`PLANNED` serials) → parts scanned and bound at consuming stages → last stage complete → units `AWAITING_PDI` → PDI (100 %, model plan + SO points, serials match) → QC Manager signs → certificate PDF → FG receipt of signed units → registry `IN_STOCK` → dispatch (PDI still valid, type approval valid) → `DISPATCHED` → invoice hand-off → `SOLD`, warranty start; part replacements recorded through the port |
| **Module** | `warehouse-manufacturing`; core `whb_serials` for unit and part serials; core inspection (source `PDI_UNIT`, MFG-registered); `UnitRegistryPort` declared in core by `P10-23` (optional bean) |
| **Owning tasks** | `issues/p10-21.md` (series, binding) · `issues/p10-22.md` (PDI) · `issues/p10-23.md` (registry, traceability, Form 22) |
| **Primary tables** | `whm_unit_serial_series`, `whm_unit_serial_voids`, `whm_unit_bindings` (`V562070`); `whm_pdi_order_points`, `whm_pdi_records`, `whm_pdi_certificates` (`V562080`); `whm_unit_registry`, `whm_unit_part_replacements`, `whm_type_approvals` (`V562090`) |

## 1. T1 — State machine

### 1.1 Transitions

| ID | From | Event | To | Guard | Actor | Side effects | Source |
|---|---|---|---|---|---|---|---|
| PUR-T1-01 | — | First job card of a unit-serial batch starts (or release, per `unit_serial.assign_at`) | unit serials `PLANNED` | `PUR-GRD-01` | system | one `whb_serials` row per unit from the series (or the pre-printed range), sequence advanced under row lock | FR-811 |
| PUR-T1-02 | serial `PLANNED` | *Void* (spoiled plate) | voided | reason | `whm_unit_serial_series:void` | `whm_unit_serial_voids` row; a replacement serial assigned to the unit | FR-811 |
| PUR-T1-03 | — | Scan a part serial at a consuming stage | binding live | `PUR-GRD-02` | `whm_unit_bindings:bind` | binding row; consumption of that serial by the stage backflush (`SFL-T4-02`) | FR-812 |
| PUR-T1-04 | binding live | *Replace* | old unbound, new bound | reason; new serial `PUR-GRD-02` | `whm_unit_bindings:replace` | both rows audited | FR-812 |
| PUR-T1-10 | unit last stage complete (`pdi_required`) | — | `AWAITING_PDI` | — | system | — | FR-813 |
| PUR-T1-11 | `AWAITING_PDI` · stock unit | *Start PDI* | PDI record `OPEN` | `PUR-GRD-04` | `whm_pdi_records:start` | core inspection `PDI_UNIT` with the model plan + order points; serials-match criterion computed | FR-813, FR-816 |
| PUR-T1-12 | `OPEN` | Record outcome | `PASSED` / `REWORK` / `HELD` | inspector ≠ producer (`403 INSPECTOR_IS_PRODUCER`, `p8-19`) | `whm_pdi_records:record` | `REWORK` → rework job card (`QRW-T1-22`); `HELD` reason `PDI_HOLD` | FR-813 |
| PUR-T1-13 | `HELD` | Release hold | `OPEN` | QC Manager | `whm_pdi_records:release_hold` | — | FR-813 |
| PUR-T1-14 | `PASSED` | *Sign* | `SIGNED` | signer ≠ inspector (`403 PDI_SELF_SIGN`) | `whm_pdi_records:sign` | `PDC-` certificate `VALID`, PDF rendered (`PDI_CERTIFICATE`) and stored as a platform document; earlier certificate of the unit → `SUPERSEDED` | FR-814 |
| PUR-T1-20 | — | FG receipt posted for the unit | registry `IN_STOCK` (row created `BUILT` → `IN_STOCK`) | — | system (`PRC-T4-20`) | registry row with build data and bound parts | FR-817 |
| PUR-T1-21 | `IN_STOCK` | Shipment posted | `DISPATCHED` | `PUR-GRD-05`, `PUR-GRD-06` (via MD-35 guard) | system | customer, dispatch ref, date | FR-817 |
| PUR-T1-22 | `DISPATCHED` | Invoice hand-off received | `SOLD` | hand-off names the unit | system (hand-off port — trade / accounting fold) | invoice ref, sale date, warranty start | FR-817 |
| PUR-T1-23 | `DISPATCHED` · `SOLD` | Customer return received | `RETURNED` | — | system | the next dispatch needs a fresh PDI (`PUR-GRD-05`) | FR-816, FR-817 |
| PUR-T1-24 | any | `recordPartReplacement` | unchanged | `PUR-GRD-07` | port / `whm_unit_registry:record_part_replacement` | `whm_unit_part_replacements` row; binding history kept | FR-818 |
| PUR-T1-30 | — | Generate VAHAN export / print Form 22 | — | each unit's model has a valid type approval | `whm_type_approvals:generate_vahan` / print | CSV in the configured layout (**RE-VERIFY**); `form22_issued_on` stamped | FR-820 |

### 1.2 Guards

| ID | Predicate | Refusal | Source |
|---|---|---|---|
| PUR-GRD-01 | The item × site has an active series; a pre-printed range has a free value; with `ISO_3779_17` every generated or typed VIN has a valid check digit and 17 characters (**RE-VERIFY**) | `409 UNIT_SERIAL_SERIES_MISSING`; `409 UNIT_SERIAL_RANGE_EXHAUSTED`; `422 VIN_CHECK_DIGIT_INVALID` | FR-811 |
| PUR-GRD-02 | Part serial exists for the BOM line's item, is on hand at the consuming location, and is not bound to another live unit | `409 SERIAL_NOT_AVAILABLE`; `409 SERIAL_ALREADY_BOUND` | FR-812 |
| PUR-GRD-03 | Stage completion: every serial-controlled line of the stage bound for every unit | `422 UNIT_BINDING_INCOMPLETE` | FR-812 |
| PUR-GRD-04 | PDI only for a unit `AWAITING_PDI` or in stock (stock PDI); one `OPEN` record per unit | `409 PDI_NOT_ALLOWED`; `409 PDI_ALREADY_OPEN` | FR-813 |
| PUR-GRD-05 | Outbound shipment of a `pdi_required` serial needs a `VALID` certificate signed ≤ `pdi_revalidate_days` ago and after the unit's last return | `409 PDI_REQUIRED_BEFORE_DISPATCH` | FR-816 |
| PUR-GRD-06 | Dispatch to a customer needs the model's type approval valid on the dispatch date | `409 TYPE_APPROVAL_NOT_VALID` | FR-820 |
| PUR-GRD-07 | Part replacement: unit registered; old serial currently bound; idempotency key unseen (replay returns the original) | `404 UNIT_NOT_REGISTERED`; `409 PART_NOT_BOUND` | FR-818 |
| PUR-GRD-08 | FG receipt of a `pdi_required` unit only with a signed `PASS` certificate | `422 PDI_NOT_PASSED` | FR-815 |

### 1.3 Unreachable

| ID | Never happens | Why | Source |
|---|---|---|---|
| PUR-UNR-01 | A voided chassis number reused | `whm_unit_serial_voids` uk + series check | FR-811 |
| PUR-UNR-02 | One part serial live on two units | partial unique index on live bindings | FR-812 |
| PUR-UNR-03 | Warranty reading `services` tables | registry + port only (`D-20` item 4) | FR-817, FR-818 |
| PUR-UNR-04 | A certificate edited | re-PDI issues a new one, the old `SUPERSEDED` | FR-814 |

## 2. T2 — Action × role × state

| ID | Action | Permission | Persona | Source |
|---|---|---|---|---|
| PUR-T2-01 | Maintain series, void | `whm_unit_serial_series:*` | production engineer | FR-811 |
| PUR-T2-02 | Bind / replace | `whm_unit_bindings:bind/replace` | operator, supervisor | FR-812 |
| PUR-T2-03 | PDI record / sign | `whm_pdi_records:record` / `:sign` | QC inspector / QC Manager | FR-813, FR-814 |
| PUR-T2-04 | Registry read, export; part replacement | `whm_unit_registry:view/export/record_part_replacement` | service / warranty desk | FR-817, FR-818 |
| PUR-T2-05 | Type approvals, VAHAN export | `whm_type_approvals:*` | homologation engineer | FR-820 |
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
| PUR-T4-03 | Traceability forward / backward | backend read over bindings, registry and `whb_transformations` (FR-648) — recall list exportable | FR-819 |

## 5. T5 — Screen contract

| ID | Screen | Contents | Source |
|---|---|---|---|
| PUR-T5-01 | WS-389 Unit Serial Series | Department + voids tab; pattern preview computed by the backend | FR-811 |
| PUR-T5-02 | WS-390 PDI | Service Vehicle; record (checklist incl. SO points, serials-match), sign, certificate print; *Re-PDI due* filter | FR-813…FR-816 |
| PUR-T5-03 | WS-391 Unit Registry · WS-392 Chassis Traceability | Customer read grid (Parts · Replacements · Form 22 tabs) · report forward / backward with export | FR-817…FR-820 |

## 6. Error codes

`UNIT_SERIAL_SERIES_MISSING`, `UNIT_SERIAL_RANGE_EXHAUSTED`, `VIN_CHECK_DIGIT_INVALID`, `SERIAL_NOT_AVAILABLE`,
`SERIAL_ALREADY_BOUND`, `UNIT_BINDING_INCOMPLETE`, `PDI_NOT_ALLOWED`, `PDI_ALREADY_OPEN`, `PDI_SELF_SIGN`, `PDI_NOT_PASSED`,
`PDI_REQUIRED_BEFORE_DISPATCH`, `TYPE_APPROVAL_NOT_VALID`, `UNIT_NOT_REGISTERED`, `PART_NOT_BOUND` — all *(proposed)*.

## 7. Edge cases

| ID | Case | Expected | Source | Scenario |
|---|---|---|---|---|
| PUR-EC-01 | Unit scrapped after binding | registry `SCRAPPED`; bindings unbound with reason; parts free for re-use only after a return to stock | FR-812, FR-817 | 788 |
| PUR-EC-02 | Invoice hand-off arrives before dispatch | refused by the port (`409 UNIT_NOT_DISPATCHED`), retried by the sender | FR-817 | 791 |

## 8. Out of scope

Warranty claims processing; Form 21 and dealer schemes (`D-20` item 4); battery EPR filing (the backward trace gives the
quantities; the filing is outside warehouse); mobile (`D-20` item 5).

## 9. Amendments

| Date | Change |
|---|---|
| 2026-10-25 | v0 derived from FRD-MFG §6.1 (R32, `D-20`; MD-11 / MD-41 narrowed by MD-48) |

## 10. Invariants and scenarios

`L-12` (genealogy), MD-35, MD-48, MD-49; scenarios `WH-SC-787`…`-792`.

## 11. Open rows

| ID | Question | Default |
|---|---|---|
| PUR-OPEN-01 | When is the chassis assigned; which parts are bound (PRD Q-PR3)? | first stage; every serial-controlled BOM line |
| PUR-OPEN-02 | Current PDI checklist and certificate format (PRD Q-Q2) | model plan + SO points; certificate per FR-814 |
