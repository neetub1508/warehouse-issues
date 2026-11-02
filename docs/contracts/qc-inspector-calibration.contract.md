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
| Inspector authorisation | current / ended | `[valid_from, valid_to]` (both inclusive; null `valid_to` = open), `is_active` | dated fact |
| Inspection result approval | `NOT_REQUIRED` · `PENDING` · `APPROVED` · `RETURNED` | `wh_quality_inspections.result_approval_status` | fact on the inspection |
| Instrument service status | `IN_SERVICE` · `OUT_FOR_CALIBRATION` · `OUT_OF_SERVICE` · `SCRAPPED` | `wh_qc_instruments.service_status` | registry |
| Instrument calibration status | `VALID` · `DUE_SOON` · `OVERDUE` · `FAILED` · `NEVER_CALIBRATED` | computed on read from the latest live calibration and the site-local today; `FAILED` = the latest live record's result is `FAIL` (an `ADJUSTED_PASS` with as-found false is not `FAILED`, R32-fix F-R32CQ-015) | derived |

### 1.2 Transitions

| ID | From | Event | To | Guard | Actor | Side effects | Source |
|---|---|---|---|---|---|---|---|
| QIC-T1-01 | — | Grant an authorisation (user, site?, stage?, category?, level, dates, qualification ref) | current | `QIC-GRD-06`, `QIC-GRD-11` | `wh_qc_inspector_authorisations:create` | audited; company and user are the grant's identity and cannot change on edit (`422 INSPECTOR_AUTHORISATION_IDENTITY_IMMUTABLE` — deactivate and grant anew; R33 #638 S4) | FR-697 |
| QIC-T1-02 | current | End / deactivate | ended | — | `:edit` | never deleted (no delete endpoint — R33 #638 accepted builder choice); **reactivation** re-checks `QIC-GRD-06` overlap and `QIC-GRD-11` (R33 #638 S4) | FR-697 |
| QIC-T1-03 | *in progress* | **Complete** under mode `ALL`, or `REJECT_ONLY` with a reject (default mode `NONE`, `D-21` item 7) | *completed*, `PENDING` | `QIC-GRD-01`…`-03` | inspector | opens an `INSPECTION_RESULT` request (`DAP` §0.1, `SINGLE_LEVEL`, `D-21` item 6; `excludedActorIds` = every result recorder — R32-fix F-R32CQ-028); disposition and the non-stock `onDisposition` held until approved (`QIC-T4-02`) | FR-699 |
| QIC-T1-04 | `PENDING` | **Approve result** (the engine step) | `APPROVED` | `QIC-GRD-04`, `-05` | `wh_quality_inspections:approve_result`; + `APPROVER` grant **only while** `inspector_authorisation_required` (R33 #638 accepted builder choice) | `result_approved_by/at`; disposition allowed; non-stock `onDisposition` called once (`QIC-T4-02`) | FR-699 |
| QIC-T1-05 | `PENDING` | **Return** (reason from `APPROVAL_RETURN`; the engine step) | `RETURNED`, inspection *in progress* | `QIC-GRD-04` | same | `lot_verdict` cleared with an audit row; results editable again; a re-complete opens a new request | FR-699 |
| QIC-T1-06 | — | **Complete** with mode `NONE`, or `REJECT_ONLY` without a reject | *completed*, `NOT_REQUIRED` | `QIC-GRD-01`…`-03` | inspector | as today (a non-stock source's `onDisposition` is called here, once — `QIC-T4-02`) | FR-699 |
| QIC-T1-07 | — | Read calibration status | derived | — | any `:view` | — | FR-700 |
| QIC-T1-08 | any | **Record calibration** (date, agency, certificate, result, as-found, next due) | `VALID` / `FAILED` | `QIC-GRD-10` | `wh_qc_instruments:record_calibration` | `last_calibrated_on`, `calibration_due_on` set; `FAIL` → `service_status = OUT_OF_SERVICE`. D9: the certificate arrives in the same multipart request and is linked in the same transaction (a failed link rolls the record back); a certificate that arrives later is attached by `POST /{id}/calibrations/{cid}/attachments` (`:record_calibration`; the record must belong to the instrument) (R33 #639 S4) | FR-700 |
| QIC-T1-09 | `IN_SERVICE` | Send out on an RGP of purpose `CALIBRATION` | `OUT_FOR_CALIBRATION` | gate pass approved (`FR-514`); **returnable `CALIBRATION` passes only** — a `QC_INSTRUMENT` line on any other kind or purpose is refused `422 GATE_PASS_SOURCE_PASS_INVALID` (`GatePassSourceResolver.acceptsPass`); **repeatable, one open trip at a time** — the resolver's line quantity is 1 + what is already returned or closed on the instrument's earlier non-cancelled pass lines, so the `GTE-GRD-12` cap (`422 GATE_PASS_QUANTITY_EXCEEDS_SOURCE`) refuses a second open trip and a finished trip frees the next (R33 #639 S4 F1, F3) | stores | `gate_pass_id` on the next calibration record — the one the user names, else (on a correction) the superseded record's, else the latest pass with no live `PASS` / `ADJUSTED_PASS` record citing it | FR-700 |
| QIC-T1-10 | any | Scrap | `SCRAPPED` | no open RGP (`409 QC_INSTRUMENT_OUT_ON_GATE_PASS`) | `:edit` | readings with it refused; terminal — a scrapped instrument may be deactivated but not reactivated (`409 QC_INSTRUMENT_SCRAPPED`), edited or calibrated (R33 #639 S4) | FR-700 |
| QIC-T1-11 | `OUT_OF_SERVICE` | **Record calibration** with result `PASS` / `ADJUSTED_PASS` (R32-fix F-R32CQ-004) | `IN_SERVICE` | `QIC-GRD-10` | `wh_qc_instruments:record_calibration` | `calibration_due_on` set; readings allowed again. While `OUT_FOR_CALIBRATION` (derived from an open `CALIBRATION` RGP line, new `QC_INSTRUMENT` `GatePassSourceResolver`; `WhGatePassService` create/update only pass the pass kind and purpose to the resolver's `acceptsPass` hook, R33 #639 S4 F3) the record is stored and the status stays `OUT_FOR_CALIBRATION` until `QIC-T1-12` (R33 #639 D3). D8: a correction (`supersedes_id`) naming no gate pass carries over the `gate_pass_id` of the record it supersedes, so correcting a passing record never drops its citation (R33 #639 S4 F2) | FR-700 |
| QIC-T1-12 | `OUT_FOR_CALIBRATION` | the `CALIBRATION` RGP is returned (`FR-512`) | `IN_SERVICE` when a `PASS` / `ADJUSTED_PASS` record citing that `gate_pass_id` exists; else `OUT_OF_SERVICE` (*awaiting certificate*) until `QIC-T1-11` | — | stores (RGP return) | — | FR-700 |

### 1.3 Guards

| ID | Predicate | Refusal | Backstop | Source |
|---|---|---|---|---|
| QIC-GRD-01 | with `inspector_authorisation_required` (default **`false`** — upgrade-safe, `D-21` item 7, R32-fix F-R32CQ-001; global key, no per-site override — switching it on while any site has no current `INSPECTOR`/`APPROVER` grant **or no current `APPROVER` grant** is refused `409 INSPECTOR_AUTHORISATION_NONE_GRANTED` naming every such site as "no inspector at …" / "no approver at …", via `WarehouseSettingsGuard.valueProblem` (R33 #638 D10, S4 F2)), Start / Record / Complete need a current `INSPECTOR` or `APPROVER` grant matching site, stage and **any** category of the item, valid on the site-local today; Disposition needs `APPROVER` | `403 INSPECTOR_NOT_AUTHORISED` · `403 INSPECTION_APPROVER_NOT_AUTHORISED` (scope named) | the permission verb is checked first | FR-697 |
| QIC-GRD-02 | `GOODS_RECEIPT` source: the GRN's creator / poster does not record results or complete, unless `inspector_may_be_receiver` | `403 INSPECTOR_IS_RECEIVER` | audit row | FR-698 |
| QIC-GRD-03 | production sources: a user in the resolver's `producedByUserIds` does not inspect, unless `inspector_may_be_producer`; `STORE_RETURN`: the return's submitter does not inspect | `403 INSPECTOR_IS_PRODUCER` · `403 INSPECTOR_IS_RETURNER` | audit row | FR-698 |
| QIC-GRD-04 | result approver ≠ every user who recorded a result on the inspection | `403 RESULT_SELF_APPROVAL` | — | FR-699 |
| QIC-GRD-05 | Disposition while `PENDING` or `RETURNED` | `409 RESULT_APPROVAL_PENDING` | — | FR-699 |
| QIC-GRD-06 | no two overlapping identical active grants; a null scope column ("every site / stage / category") is one value for this test | `409 INSPECTOR_AUTHORISATION_OVERLAP` | `btree_gist`; `EXCLUDE USING gist` on `user_id`, `COALESCE(scope, sentinel)` per scope column, level, `daterange(valid_from, valid_to, '[]')` `WHERE is_active` (R32-fix F-R32CQ-030) | FR-697 |
| QIC-GRD-07 | a criterion with `instrument_required` gets a result (criterion result **or per-serial result**, R32-fix F-R32CQ-026) only with an instrument of its `instrument_type_code`, **at the inspection's site**. Applies to the readings a save submits — a criterion (or serial cell) left blank needs no instrument (R33 #639 S4 F3). An instrument named on a criterion without `instrument_required` is still judged by `QIC-GRD-08` / `-09` | `422 INSTRUMENT_REQUIRED` · `422 INSTRUMENT_TYPE_MISMATCH` · `422 INSTRUMENT_NOT_AT_SITE` (another site's instrument **or an unknown id**) · `422 INSTRUMENT_TYPE_NOT_APPLICABLE` (a type set on a criterion without `instrument_required`, WS-079) | — | FR-701 |
| QIC-GRD-08 | the instrument is active, `IN_SERVICE` and its calibration status is `VALID` / `DUE_SOON`; inactive, not in service and `FAILED` are refused under every policy. `OVERDUE` / `NEVER_CALIBRATED`: refused under `BLOCK`; under `instrument_reading_policy = WARN` saved only with `acknowledgeInstrumentNotCalibrated = true` + a non-blank `instrumentAcknowledgementNote` (≤ 2000) in the same request (line and serial results alike). The acknowledgement is held **in the audit log only** (`WH_QUALITY_INSPECTION_INSTRUMENT_NOT_CALIBRATED_ACKNOWLEDGED`, actor + note + readings) — no row column; accepted risk: not queryable from the screen, level-gated log (R33 #639 S4 F4). **D6 carry-forward**: a reading unchanged since the last save (same typed value, same instrument) keeps its recorded row — instrument, frozen due date, and the reading's time and author (`created_at` / `created_by`, which `QIC-T4-01`'s window is keyed on) — and is not re-judged; `updated_by` moves to the saver. A changed reading is a new row, judged afresh and audited `WH_QUALITY_INSPECTION_READING_CHANGED` | `422 INSTRUMENT_NOT_CALIBRATED` naming the due date (field `…instrumentId`, or `acknowledgeInstrumentNotCalibrated` / `instrumentAcknowledgementNote` under WARN) | `instrument_due_on_at_reading` frozen on `wh_quality_inspection_results` and `wh_quality_inspection_serial_results` | FR-701 |
| QIC-GRD-09 | the reading lies inside the instrument's `range_min`…`range_max` | `422 READING_OUTSIDE_INSTRUMENT_RANGE` | — | FR-701 |
| QIC-GRD-10 | `next_due_on` > `calibrated_on` and ≤ `calibrated_on + calibration_interval_days`; calibration records are append-only (`supersedes_id` corrections) | `422 CALIBRATION_DUE_BEYOND_INTERVAL` · D8: `422 CALIBRATION_DATE_IN_FUTURE` (after the site's today) · `409 CALIBRATION_CORRECTION_NOT_LATEST` · D9: `422 CALIBRATION_CERTIFICATE_REQUIRED` (`EXTERNAL_LAB` without file, certificate no. or agency) · `422 CALIBRATION_GATE_PASS_INVALID` (a named pass that is not a `CALIBRATION` pass carrying the instrument) | CHECK; trigger refuses `UPDATE`/`DELETE` | FR-700 |
| QIC-GRD-11 | an authorisation's grantor ≠ its grantee — create, edit and reactivation of one's own grant (ADMIN included); deactivating one's own grant is allowed (R33 #638 S4 driver decision — SoD, ISO 9001 §7.2 / §8.6) | `422 QC_AUTHORISATION_SELF_GRANT` on `userId` | — | FR-697 |

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
| QIC-T2-03 | Maintain instruments; record calibration | `wh_qc_instruments:create/edit` · `:record_calibration` | `422 QC_INSTRUMENT_CODE_IMMUTABLE` · `422 QC_INSTRUMENT_SITE_IMMUTABLE` · edit refused on a scrapped instrument (R33 #639 S4) | metrology in-charge | FR-700 |

## 3. T3 — Time-driven rules

| ID | Rule | Trigger | Changes | Notified | Job | Once? | Source |
|---|---|---|---|---|---|---|---|
| QIC-T3-01 | Calibration due / overdue | status enters `DUE_SOON` (`calibration_due_warning_days`) or `OVERDUE` | nothing; event `qc_instrument.calibration_due` | custodian (in-app notification) + the ROLE recipients of rule `QC_INSTRUMENT_CALIBRATION_DUE` (seed: Warehouse QA, ADMIN; a custom role holding `:record_calibration` is alerted only once an admin adds it on WS-069) (R33 #639 S4) | daily per site | once per due date (`last_due_notified_on`) | FR-700 |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in | Source |
|---|---|---|---|---|
| QIC-T4-01 | a calibration recorded with `as_found_in_tolerance = false` | the *Impact* list = every result and per-serial result recorded with this instrument since its previous in-tolerance calibration (R32-fix F-R32CQ-026); event `qc_instrument.calibration_failed`; an NCR of source `CALIBRATION_FAILURE` may be raised from it (`NCR-T1-02`). The Impact tab shows the latest live out-of-tolerance record; each live out-of-tolerance row on the Calibrations tab has an *Impact* action that opens that record's list (R33 #639 S4 F5). `422 QC_INSTRUMENT_STOCK_OWNER_UNRESOLVED` when the company has no house owner to carry the event | instrument service (read model) | FR-701 |
| QIC-T4-02 | a non-stock-bearing source's inspection completes (SEAM-M4, `IIS-GRD-07a`) | the resolver's `onDisposition` runs at Complete when the result is `NOT_REQUIRED`, else in the `INSPECTION_RESULT` `onApproved` transaction — never while `PENDING` / `RETURNED`; **no manual Raise NCR while `PENDING` / `RETURNED`** (`409 RESULT_APPROVAL_PENDING` under the inspection lock; `canRaiseNcr` false — the approval raises it through the hook, a Return clears the verdict; R33 #638 S4 F1); exactly once per inspection (`outcome_dispatched_at` latch) across Return and re-complete (R32-fix F-R32CQ-010; built `WhQualityInspectionService.java:609-620` amended) | inspection service | FR-699 |

## 5. T5 — Screen contract

| ID | Screen | Contract | Source |
|---|---|---|---|
| QIC-T5-01 | WS-694 Inspector Authorisations (reference **Department**) | grid `wh_qc_inspector_authorisations` · scope `WAREHOUSE_QC_INSPECTOR_AUTH` · sort `e.valid_from DESC`; columns `userName` (platform user-display helper), `siteName`, `inspectionStage`, `itemCategoryName`, `authorisationLevel`, `validFrom`, `validTo` (`formatDateSync`), `qualificationRef`, `isCurrent`, audit; filters `userId`, `warehouseId`, `inspectionStage`, `authorisationLevel`, `currentOnly`. `isCurrent` / `currentOnly` read the site-local day for a site grant and the **UTC day** for an every-site grant (the guard always reads the inspection site's local day — R33 #638 S4) | FR-697 |
| QIC-T5-02 | WS-080 changes | column + filter `resultApprovalStatus`; row actions **Approve result** (success) / **Return** (warning) per `QIC-T2-02`; segregation and authorisation refusals inside the modal; `resultApprovalStatus` filter options served by `/vocabularies` (`resultApprovalStatuses`, like `states`); View gains a **Result Approval History** tab — the shared `ApprovalHistoryPanel` on `GET /{id}/result-approval-history`, beside the scrap one; the statistics strip keeps its **five** tiles — no pending-approval tile, approvers work from My Approvals (R33 #638 S4, accepted builder choice); the `/inspectors` feed is the **history filter** and lists every inspector — the only grant-restricted pick is the Start guard on the named inspector (D6 amended). **Instrument picker** (R33 #639): `GET /{id}/instruments?instrumentType=` with `wh_quality_inspections:view` (+ the inspection's site scope) — the site's active, unscrapped instruments of the criterion's type (any when absent), filtered in SQL **before** the 500-row cap, `truncated` when capped; each option carries calibration / service status, due date, range and `requiresAcknowledgement` (the server's D5 rule), plus `readingPolicy`. Per criterion on a line; on a per-serial line each recorded cell keeps its own instrument and the criterion's picker fills only new or edited cells; the WARN acknowledgement is asked only for new or changed readings. View results (line and serial) gain **Instrument** and **Due at Reading** columns | FR-698 FR-699 FR-701 |
| QIC-T5-03 | WS-695 QC Instruments (reference **Department**, tabs) | grid `wh_qc_instruments` · scope `WAREHOUSE_QC_INSTRUMENT` · sort `e.calibration_due_on ASC`; columns `code`, `name`, `instrumentType`, `serialNumber`, `siteName`, `custodianName`, `lastCalibratedOn`, `calibrationDueOn` (`formatDateSync`), `calibrationStatus`, `serviceStatus`, audit; filters `warehouseId`, `instrumentType`, `calibrationStatus`, `serviceStatus`; tiles Valid · Due soon · Overdue · Failed · Out of service (the four calibration-status tiles count active, unscrapped instruments only — R33 #639 S4 F4); export writes the grid's English status labels; View tabs *Details*, *Calibrations*, *Impact* | FR-700 FR-701 |

## 6. Out of scope

MSA / gauge R&R studies, SPC, the legal-metrology weighing register (`FR-223`, `wh_weighing_instruments`, v2), training records beyond a qualification reference, mobile.

## 7. Amendments

| Date | Change |
|---|---|
| 2026-10-25 | v0 derived (R32, `D-20` item 3): `P8-19` authorisation / segregation / result approval, `P8-20` instruments and calibration |
| 2026-10-25 | **R32-fix** (`R32-functional-review-core-quality.md`, `D-21` items 6, 7). Upgrade-safe defaults `inspector_authorisation_required = false`, `result_approval_mode = NONE` (`QIC-GRD-01`, `QIC-T1-03`; F-R32CQ-001); result approval on the engine as `INSPECTION_RESULT` (`QIC-T1-03`…`-05`; F-028); non-stock outcome held until approval, exactly once (`QIC-T4-02`; F-010); back into service after a passing calibration or RGP return (`QIC-T1-11`, `-12`; F-004); `FAILED` = latest result `FAIL` (§1.1; F-015); per-serial readings under the same guards and impact list (`QIC-GRD-07`, `-08`, `QIC-T4-01`; F-026); overlap constraint with sentinels, inclusive range, `btree_gist` (`QIC-GRD-06`; F-030) |
| 2026-11-01 | **R33 #638 S4** (`R33-run-decisions.md`). `QIC-T4-02`: no manual NCR while result approval is `PENDING` / `RETURNED` (F1). `QIC-GRD-01` / D10: switch-on also needs a current `APPROVER` per site (F2). D6: "picker" means the Start check on the named inspector only; the `/inspectors` feed is the WS-080 history filter, unrestricted (F3). D11: a re-inspection while the source's result is `PENDING` is `409 RESULT_APPROVAL_PENDING`; while `RETURNED` it is refused `409 INSPECTION_IN_PROGRESS` (a returned inspection is in progress again) (F4). `QIC-T1-04` actor: `APPROVER` grant only while authorisation is required. `QIC-T5`: five WS-080 tiles kept, Result Approval History tab, UTC-day *current* for every-site grants, `validFrom DESC` sort (F6). `QIC-T1-01` / `-02`: company and user immutable, no delete, reactivation re-checks overlap. New `QIC-GRD-11`: grantor ≠ grantee (`422 QC_AUTHORISATION_SELF_GRANT`) |
| 2026-11-01 | **R33 #639 S4** (`R33-run-decisions.md`). `QIC-T1-09`: returnable `CALIBRATION` passes only, repeatable with one open trip at a time (F1, F3). `QIC-T1-11` / D8: a correction carries the superseded record's gate pass; auto-cite skips only a pass with a live passing citation (F2). `QIC-T5-03`: calibration tiles exclude scrapped / inactive (F4). `QIC-T4-01`: per-record Impact action (F5). `QIC-T1-08` / D9: multipart, same transaction, plus the later attach endpoint. `QIC-T3-01`: recipients are the rule's ROLE recipients + custodian. Refusal codes found in code added to `QIC-GRD-07`, `-10`, `QIC-T1-10`, `QIC-T2-03`, `QIC-T4-01` |
| 2026-11-02 | **R33 #639 S4 inc2** (S3 functional + standards review). `QIC-GRD-07`: `INSTRUMENT_NOT_AT_SITE` (incl. unknown id); only submitted readings need an instrument (F3, F8). `QIC-GRD-08`: acknowledgement fields, held in the audit log only — accepted (F4); D6 carry-forward keeps the reading's row, time and author, so the `QIC-T4-01` impact window survives a re-save (F2); per-serial cells keep their own instrument (F1). `QIC-T5-02`: `GET /{id}/instruments` per instrument type, server-side type filter before the cap, `truncated`, per-option `requiresAcknowledgement`; per-cell serial instruments; WARN prompt only for new / changed readings; View *Instrument* / *Due at Reading* columns (F1, F5–F8) |

## 8. Invariants and scenarios

`FR-408`; `RQP-UNR-04` (Return clears a verdict with an audit row; it never edits a completed verdict); scenarios `WH-SC-726`…`WH-SC-729`.
