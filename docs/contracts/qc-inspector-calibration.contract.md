# Functional Contract — QC inspector authorisation, segregation of duties, result approval, and measuring-instrument calibration

> **What this is.** The functional truth for **who** may inspect and approve, and **with what**: the inspector
> authorisation register (site × stage × item category, dated), the segregation rules (an inspector never
> inspects their own GRN, own production or own return), the QC Manager's approval of an inspection result
> before disposition, and the QC gauge register whose calibration status decides whether a reading is
> accepted. It **extends** [`incoming-inspection-sampling.contract.md`](incoming-inspection-sampling.contract.md)
> and [`receipt-qc-putaway.contract.md`](receipt-qc-putaway.contract.md) (`RQP-T1-16`…`-23`); `MRA-GRD-04`
> (MRN authoriser ≠ releasing inspector) is unchanged.
>
> **Status.** Derived 2026-10-25 (v0) from [`frd/FRD-STORES.md`](../frd/FRD-STORES.md) §6.9 (`FR-697`…`FR-701`),
> `DECISIONS.md` `D-20` item 3 (*inspector authorisation*, *QC instrument calibration*), PRD 2026-10-24 §6 / §10;
> ISO 9001:2015 §7.1.5 and IATF 16949 §7.1.5.2 (calibration), §7.2 (competence). Not ratified. **No code exists.**

---

## 0. Identity

| | |
|---|---|
| **Workflow** | Grant authorisation → inspector starts / records / completes (authorised, not the receiver / producer) → result approval (QC Manager) → disposition · Instrument registered → calibrated (certificate) → readings checked against status → failed calibration lists impact |
| **Module** | `warehouse`; code lists in `warehouse-base` (`V500502`) |
| **Owning tasks** | `issues/p8-19.md` (authorisation, segregation, result approval) · `issues/p8-20.md` (instruments, calibration) |
| **Primary tables** | `wh_qc_inspector_authorisations` (`V511502`); ALTER `wh_quality_inspections` + `result_approval_*` (`V511502`); `wh_qc_instruments`, `wh_qc_instrument_calibrations` (`V511503`); ALTER `wh_inspection_plan_criteria` + `instrument_required`, `instrument_type_*`; ALTER `wh_quality_inspection_results` + `instrument_id`, `instrument_due_on_at_reading` (`V511503`) |
| **Permission resources** | `wh_qc_inspector_authorisations:{view,view:all,view:branch,create,edit,export}` · verb `wh_quality_inspections:approve_result` · `wh_qc_instruments:{view,view:all,view:branch,create,edit,record_calibration,export}` |
| **Routes** | WS-694 `/warehouse/quality/inspector-authorisations` · WS-695 `/warehouse/quality/instruments` · WS-079, WS-080 (changed) · **mobile: none** |
| **Contract version** | `v0 — 2026-10-25` |

### Acceptance checks

| # | Expects | Delivered by |
|---|---|---|
| A1 | Only an authorised inspector inspects (`WH-SC-726`) | `QIC-GRD-01` |
| A2 | The GRN maker never inspects that GRN (`WH-SC-727`) | `QIC-GRD-02` |
| A3 | A result is approved by a QC Manager who did not record it, before disposition (`WH-SC-728`) | `QIC-T1-03`…`-05`, `QIC-GRD-04`, `-05` |
| A4 | A reading against an overdue instrument is refused; a failed calibration lists its impact (`WH-SC-729`) | `QIC-GRD-08`, `QIC-T4-01` |

---

## 1. T1 — State machine

### 1.1 Status inventory

| Entity | Status | Represented by | Kind |
|---|---|---|---|
| Inspector authorisation | current / ended | `[valid_from, valid_to)`, `is_active` | dated fact |
| Inspection result approval | `NOT_REQUIRED` · `PENDING` · `APPROVED` · `RETURNED` | `wh_quality_inspections.result_approval_status` | fact on the inspection |
| Instrument service status | `IN_SERVICE` · `OUT_FOR_CALIBRATION` · `OUT_OF_SERVICE` · `SCRAPPED` | `wh_qc_instruments.service_status` | registry |
| Instrument calibration status | `VALID` · `DUE_SOON` · `OVERDUE` · `FAILED` · `NEVER_CALIBRATED` | computed on read from the latest live calibration and the site-local today | derived |

### 1.2 Transitions

| ID | From | Event | To | Guard | Actor | Side effects | Source |
|---|---|---|---|---|---|---|---|
| QIC-T1-01 | — | Grant an authorisation (user, site?, stage?, category?, level, dates, qualification ref) | current | `QIC-GRD-06` | `wh_qc_inspector_authorisations:create` | audited | FR-697 |
| QIC-T1-02 | current | End / deactivate | ended | — | `:edit` | never deleted once used by an inspection | FR-697 |
| QIC-T1-03 | *in progress* | **Complete** under mode `ALL`, or `REJECT_ONLY` with a reject | *completed*, `PENDING` | `QIC-GRD-01`…`-03` | inspector | disposition blocked until approved | FR-699 |
| QIC-T1-04 | `PENDING` | **Approve result** | `APPROVED` | `QIC-GRD-04`, `-05` | `wh_quality_inspections:approve_result` + `APPROVER` grant | `result_approved_by/at`; disposition allowed | FR-699 |
| QIC-T1-05 | `PENDING` | **Return** (reason) | `RETURNED`, inspection *in progress* | `QIC-GRD-04` | same | `lot_verdict` cleared with an audit row; results editable again | FR-699 |
| QIC-T1-06 | — | **Complete** with mode `NONE`, or `REJECT_ONLY` without a reject | *completed*, `NOT_REQUIRED` | `QIC-GRD-01`…`-03` | inspector | as today | FR-699 |
| QIC-T1-07 | — | Read calibration status | derived | — | any `:view` | — | FR-700 |
| QIC-T1-08 | any | **Record calibration** (date, agency, certificate, result, as-found, next due) | `VALID` / `FAILED` | `QIC-GRD-10` | `wh_qc_instruments:record_calibration` | `last_calibrated_on`, `calibration_due_on` set; `FAIL` → `service_status = OUT_OF_SERVICE` | FR-700 |
| QIC-T1-09 | `IN_SERVICE` | Send out on an RGP of purpose `CALIBRATION` | `OUT_FOR_CALIBRATION` | gate pass approved (`FR-514`) | stores | `gate_pass_id` on the next calibration record | FR-700 |
| QIC-T1-10 | any | Scrap | `SCRAPPED` | no open RGP | `:edit` | readings with it refused | FR-700 |

### 1.3 Guards

| ID | Predicate | Refusal | Backstop | Source |
|---|---|---|---|---|
| QIC-GRD-01 | with `inspector_authorisation_required`, Start / Record / Complete need a current `INSPECTOR` or `APPROVER` grant matching site, stage and **any** category of the item, valid on the site-local today; Disposition needs `APPROVER` | `403 INSPECTOR_NOT_AUTHORISED` · `403 INSPECTION_APPROVER_NOT_AUTHORISED` (scope named) | the permission verb is checked first | FR-697 |
| QIC-GRD-02 | `GOODS_RECEIPT` source: the GRN's creator / poster does not record results or complete, unless `inspector_may_be_receiver` | `403 INSPECTOR_IS_RECEIVER` | audit row | FR-698 |
| QIC-GRD-03 | production sources: a user in the resolver's `producedByUserIds` does not inspect, unless `inspector_may_be_producer`; `STORE_RETURN`: the return's submitter does not inspect | `403 INSPECTOR_IS_PRODUCER` · `403 INSPECTOR_IS_RETURNER` | audit row | FR-698 |
| QIC-GRD-04 | result approver ≠ every user who recorded a result on the inspection | `403 RESULT_SELF_APPROVAL` | — | FR-699 |
| QIC-GRD-05 | Disposition while `PENDING` or `RETURNED` | `409 RESULT_APPROVAL_PENDING` | — | FR-699 |
| QIC-GRD-06 | no two overlapping identical grants | `409 INSPECTOR_AUTHORISATION_OVERLAP` | `EXCLUDE USING gist` on scope + daterange | FR-697 |
| QIC-GRD-07 | a criterion with `instrument_required` gets a result only with an instrument of its `instrument_type_code` | `422 INSTRUMENT_REQUIRED` · `422 INSTRUMENT_TYPE_MISMATCH` | — | FR-701 |
| QIC-GRD-08 | the instrument is `IN_SERVICE` and its calibration status is `VALID` / `DUE_SOON` (under `instrument_reading_policy = WARN`: saved with acknowledgement + audit) | `422 INSTRUMENT_NOT_CALIBRATED` naming the due date | `instrument_due_on_at_reading` frozen | FR-701 |
| QIC-GRD-09 | the reading lies inside the instrument's `range_min`…`range_max` | `422 READING_OUTSIDE_INSTRUMENT_RANGE` | — | FR-701 |
| QIC-GRD-10 | `next_due_on` > `calibrated_on` and ≤ `calibrated_on + calibration_interval_days`; calibration records are append-only (`supersedes_id` corrections) | `422 CALIBRATION_DUE_BEYOND_INTERVAL` | CHECK; trigger refuses `UPDATE`/`DELETE` | FR-700 |

### 1.4 Unreachable

| ID | Must never happen | Source |
|---|---|---|
| QIC-UNR-01 | `calibration_due_on` changed except by a calibration record | FR-700 |
| QIC-UNR-02 | a disposition posted on a `PENDING` result | FR-699 |
| QIC-UNR-03 | a failed calibration re-dispositioning or reversing posted inspections automatically | FR-701 |

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from | Extra | Source |
|---|---|---|---|---|---|
| QIC-T2-01 | Maintain authorisations | `wh_qc_inspector_authorisations:create/edit` | — | QA manager | FR-697 |
| QIC-T2-02 | Approve / return result | `wh_quality_inspections:approve_result` | `PENDING` | `APPROVER` grant | FR-699 |
| QIC-T2-03 | Maintain instruments; record calibration | `wh_qc_instruments:create/edit` · `:record_calibration` | — | metrology in-charge | FR-700 |

## 3. T3 — Time-driven rules

| ID | Rule | Trigger | Changes | Notified | Job | Once? | Source |
|---|---|---|---|---|---|---|---|
| QIC-T3-01 | Calibration due / overdue | status enters `DUE_SOON` (`calibration_due_warning_days`) or `OVERDUE` | nothing; event `qc_instrument.calibration_due` | custodian, holders of `:record_calibration` | daily per site | once per due date (`last_due_notified_on`) | FR-700 |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in | Source |
|---|---|---|---|---|
| QIC-T4-01 | a calibration recorded with `as_found_in_tolerance = false` | the *Impact* list = every result recorded with this instrument since its previous in-tolerance calibration; event `qc_instrument.calibration_failed`; an NCR of source `CALIBRATION_FAILURE` may be raised from it (`NCR-T1-02`) | instrument service (read model) | FR-701 |

## 5. T5 — Screen contract

| ID | Screen | Contract | Source |
|---|---|---|---|
| QIC-T5-01 | WS-694 Inspector Authorisations (reference **Department**) | grid `wh_qc_inspector_authorisations` · scope `WAREHOUSE_QC_INSPECTOR_AUTH` · sort `e.valid_from DESC`; columns `userName` (platform user-display helper), `siteName`, `inspectionStage`, `itemCategoryName`, `authorisationLevel`, `validFrom`, `validTo` (`formatDateSync`), `qualificationRef`, `isCurrent`, audit; filters `userId`, `warehouseId`, `inspectionStage`, `authorisationLevel`, `currentOnly` | FR-697 |
| QIC-T5-02 | WS-080 changes | column + filter `resultApprovalStatus`; row actions **Approve result** (success) / **Return** (warning) per `QIC-T2-02`; segregation and authorisation refusals inside the modal | FR-698 FR-699 |
| QIC-T5-03 | WS-695 QC Instruments (reference **Department**, tabs) | grid `wh_qc_instruments` · scope `WAREHOUSE_QC_INSTRUMENT` · sort `e.calibration_due_on ASC`; columns `code`, `name`, `instrumentType`, `serialNumber`, `siteName`, `custodianName`, `lastCalibratedOn`, `calibrationDueOn` (`formatDateSync`), `calibrationStatus`, `serviceStatus`, audit; filters `warehouseId`, `instrumentType`, `calibrationStatus`, `serviceStatus`; tiles Valid · Due soon · Overdue · Failed · Out of service; View tabs *Details*, *Calibrations*, *Impact* | FR-700 FR-701 |

## 6. Out of scope

MSA / gauge R&R studies, SPC, the legal-metrology weighing register (`FR-223`, `wh_weighing_instruments`, v2), training records beyond a qualification reference, mobile.

## 7. Amendments

| Date | Change |
|---|---|
| 2026-10-25 | v0 derived (R32, `D-20` item 3): `P8-19` authorisation / segregation / result approval, `P8-20` instruments and calibration |

## 8. Invariants and scenarios

`FR-408`; `RQP-UNR-04` (Return clears a verdict with an audit row; it never edits a completed verdict); scenarios `WH-SC-726`…`WH-SC-729`.
