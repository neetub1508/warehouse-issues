# Functional Contract — Task execution, exception console, printing, labour and weighing (web)

> **What this is.** The functional truth for the execution layer FRD §6.12 asks for, on the **web** surface
> v1 ships: the task as the execution object behind every receipt and pick line, its timing columns, pull and
> push assignment from one table, resource and qualification fit, the supervisor exception console, the print
> templates, renderer, print-job log and print server, timed labour tasks, legal weighing instruments, the
> refusal to compute engineered labour standards, and automation through a task-event contract. Every rule row
> names its requirement in **Source** (`DECISIONS.md` `D-17` item 1).
>
> **What this is not.** The mobile and RF half of §6.12 — `FR-217`, `FR-219`, `FR-220`, `FR-221`, `FR-222` — is
> **DEFERRED by `D-17` item 2** (warehouse ships no mobile app in v1) and is not covered; the web screens are
> the v1 execution surface. Pick and putaway effects are in [`outbound-despatch.contract.md`](outbound-despatch.contract.md)
> and [`receipt-qc-putaway.contract.md`](receipt-qc-putaway.contract.md); the as-built task ladder detail is
> classic `warehouse-base/docs/contracts/task.contract.md` (`TSK-*`).
>
> **Status.** Derived 2026-10-23 (v0) from `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` §6.12 (`FR-212`…`FR-216`,
> `FR-223`…`FR-229`), checked against the built code in `classic` by name. Not ratified.

---

## 0. Identity

| | |
|---|---|
| **Workflow** | Task: created by its document → assigned (push) or claimed (pull) → completed / completed with exception / cancelled; stale → exception · Print: template authored and published → resolved by kind, owner and site → rendered → job logged (reprint flagged) → routed to a printer · Labour timer: run ⇄ pause → end · Weighing: instrument with certificate → weighing record on a receipt / shipment / carton |
| **Module** | `warehouse-base` (`whb_tasks`, `whb_task_types`, claim service, devices) · `warehouse` (exception console, printing, labour, weighing) |
| **Domain baseline** | `FR-436`; `OD-17` (v1 LPN label is internal Code-128; GS1-128 optional from v1.1); `D-13` read subject to `D-17` item 2 |
| **Owning tasks** | `issues/p0-10.md` (tasks) · `issues/p2-14.md` (printing) · `issues/p3-02.md` (pull / push, console) · `issues/p3-08.md` (print server) · `issues/p5-17.md` (weighing, labour) · `issues/p5-21.md` (per-owner templates) · `issues/p6-03.md` (measured labour) · `issues/p6-04.md` (automation) |
| **Code (as built)** | `WhbTaskService`, `WhbTaskValidationService`, `WhbTaskClaimService`, `WhbTaskAgeingJob`, `WhbTaskBlockedAlertService`, `WhbTaskCompletedEvents`; `WhExceptionConsoleService`; print services under `service/whprinttemplate`, `whprintjob`, `whprinter`, `whprintroutingrule`; `WhLabourTaskService`; `WhWeighingInstrumentService`, `WhWeighingRecordService`, `WhbWeighingCertificateExpiryJob` |
| **Routes** | WS-059 Tasks · WS-154 Task Assignment Board · WS-153 Supervisor Exception Console · WS-131 Print Templates · WS-132 Print Jobs · WS-133 Printers · WS-134 Print Routing Rules · WS-146 Labour Tasks · WS-129 Weighing Instruments · WS-130 Weighing Records |
| **Contract version** | `v0 — 2026-10-23` |

---

## 1. T1 — State machine

### 1.1 Status inventory

| Entity | Status | Represented by | Reachable via | Exits via | Kind | Source |
|---|---|---|---|---|---|---|
| Task | `CREATED` · `ASSIGNED` | `whb_tasks.status` | `TEP-T1-01`, `-02`, `-03` | `-04`, `-05`, `-06`, `-07` | active | `FR-212`, `FR-214` |
| Task | `STARTED` · `PAUSED` | `status`; `started_at`, `paused_seconds` | not reachable from a v1 web screen | — | columns from v1, behaviour later | `FR-213`, `FR-215` |
| Task | `EXCEPTION` | `status`; `exception_code`, `exception_at` | `TEP-T1-07` | `-04`, `-05`, `-06` | active | `FR-216` |
| Task | `COMPLETED` · `CANCELLED` | `status`; `completed_at`, `completion_movement_id` / cancel reason | `TEP-T1-04`, `-05` / `-06` | none | **terminal** | `FR-212` |
| Print job | `PRINTED` → `VOIDED` | `status`; `is_reprint`, `reprint_of_job_id` | `TEP-T1-10`, `-11` | none | record | `FR-224` |
| Labour task | `RUNNING` ⇄ `PAUSED` → `ENDED` | `status` | `TEP-T1-12`…`-14` | none after `ENDED` | record | `FR-227` |
| Weighing certificate | `VALID` · `EXPIRING` · `EXPIRED` · `NOT_YET_VALID` · `UNVERIFIED` | derived from the certificate window | `TEP-T3-03` | — | derived | `FR-223` |

### 1.2 Transitions

| ID | From | Event / action | To | Guard | Actor (permission) | Side effects | Source |
|---|---|---|---|---|---|---|---|
| TEP-T1-01 | — | A receipt line or a pick line is created / released | `CREATED` | `TEP-GRD-01` | system (the document's service) | one task per line, `source_document_type` / `_id` | `FR-212` |
| TEP-T1-02 | `CREATED` · `EXCEPTION` | **Push** — a supervisor assigns a queue | `ASSIGNED` | `TEP-GRD-02` | `whb_tasks:assign` / `:reassign` | `assigned_to`, `assigned_at` | `FR-214`, `FR-215` |
| TEP-T1-03 | `CREATED` | **Pull** — an operator asks for the next task | `ASSIGNED` | `TEP-GRD-02`, `-03` | `whb_tasks:claim` | the claimed task, `assigned_at` | `FR-214` |
| TEP-T1-04 | `CREATED` · `ASSIGNED` · `EXCEPTION` | Complete (in the same web request; v1 has no RF gun) | `COMPLETED` | the document's completion guards | the document's `:complete` | `TEP-T4-01` | `FR-212`, `FR-213` |
| TEP-T1-05 | `CREATED` · `ASSIGNED` · `EXCEPTION` | Complete with exception | `COMPLETED` | `TEP-GRD-04` | `whb_tasks:edit` | exception code kept | `FR-216` |
| TEP-T1-06 | `CREATED` · `ASSIGNED` · `EXCEPTION` | Cancel | `CANCELLED` | `TEP-GRD-04` | `whb_tasks:edit` | cancel reason | `FR-212` |
| TEP-T1-07 | `ASSIGNED` | Ages past the task type's stale threshold | `EXCEPTION` | `TEP-T3-01` | scheduled job | supervisor notified | `FR-216` |
| TEP-T1-08 | — | Author / publish a print template | active, published | `TEP-GRD-05`, `-06`, `-07` | `wh_print_templates:{create,edit,publish}` | a template version | `FR-224`, `FR-225`, `FR-226` |
| TEP-T1-09 | — | Register a printer; add a routing rule | active | `TEP-GRD-08`, `-09` | `wh_printers:*` · `wh_print_routing_rules:*` | — | `FR-224` |
| TEP-T1-10 | — | Print a document kind for a subject | job `PRINTED` | `TEP-GRD-05`, `-08`, `-09` | `wh_print_jobs:create` | `TEP-T4-02`, `-03` | `FR-224`, `FR-225` |
| TEP-T1-11 | `PRINTED` | Void a print job | `VOIDED` | reason code | `wh_print_jobs:void` | job kept | `FR-224` |
| TEP-T1-12 | — | Start a labour timer against a task / work order | `RUNNING` | `TEP-GRD-10` | `wh_labour_tasks:record` | who, from, reference, device | `FR-227` |
| TEP-T1-13 | `RUNNING` ⇄ `PAUSED` | Pause / resume | `PAUSED` / `RUNNING` | `TEP-GRD-10` | `wh_labour_tasks:record` | paused seconds accrue | `FR-227` |
| TEP-T1-14 | `RUNNING` · `PAUSED` | End | `ENDED` | `TEP-GRD-10` | `wh_labour_tasks:record` | `TEP-T4-04` | `FR-227` |
| TEP-T1-15 | — | Record a weighing on a receipt, return receipt, shipment or carton | a weighing record | `TEP-GRD-11` | `wh_weighing_records:create`; the out-of-verification acknowledgement `wh_weighing_records:acknowledge` | out-of-verification flag on the receipt | `FR-223` |

### 1.3 Guards

| ID | Predicate (must hold to proceed) | Refusal: code · field | Message shape | Source |
|---|---|---|---|---|
| TEP-GRD-01 | A task names a registered task type, its source document, its site, its zone and a priority; `required_resource_type` comes from the task type | `TASK_TYPE_INVALID`, `TASK_SOURCE_DOCUMENT_INVALID`, `TASK_SITE_INVALID`, `TASK_ZONE_INVALID`, `TASK_PRIORITY_REQUIRED` | names the field | `FR-212`, `FR-215` |
| TEP-GRD-02 | The assignee is active, permitted at the site and qualified for the task's required resource type | `TASK_ASSIGNEE_INACTIVE`, `TASK_ASSIGNEE_SITE_NOT_PERMITTED`, `TASK_ASSIGNEE_NOT_QUALIFIED`, `TASK_ASSIGNEE_REQUIRED` | names the assignee and the resource | `FR-215` |
| TEP-GRD-03 | Pull honours zone, task type and equipment capability, highest priority first, from the same `whb_tasks` table push assigns from | — (no task returned when none fits) | — | `FR-214` |
| TEP-GRD-04 | Cancel names a valid cancel reason; complete-with-exception names a valid `TASK_EXCEPTION` code; illegal moves are refused | `TASK_CANCEL_REASON_REQUIRED`, `TASK_CANCEL_REASON_INVALID`, `TASK_EXCEPTION_CODE_REQUIRED`, `TASK_EXCEPTION_CODE_INVALID`, `TASK_TRANSITION_INVALID` | names the task | `FR-212`, `FR-216` |
| TEP-GRD-05 | A template has a document kind, a format (`ZPL` first; `PDF` for laser; `EPL`, `TSPL`, `HTML`), a body and its dimensions; its syntax parses and every variable is declared; only a published, active template prints | `PRINT_KIND_UNSUPPORTED`, `PRINT_TEMPLATE_SYNTAX`, `PRINT_TEMPLATE_UNDECLARED_VARIABLE`, `PRINT_TEMPLATE_NOT_PUBLISHED`, `PRINT_TEMPLATE_INACTIVE`, `PRINT_TEMPLATE_NOT_RESOLVED` | names the template | `FR-224` |
| TEP-GRD-06 | The eleven kinds ship in v1 — item / shelf label, LPN / pallet label, carton label, shipping label, location label, goods-receipt note, pick list, packing slip, delivery document, movement-document print, hazard class label; the v1 LPN label encodes internal Code-128; GS1-128 is refused until the allocator and parser capability is on | `PRINT_TEMPLATE_GS1_NOT_AVAILABLE` | names the capability | `FR-225` |
| TEP-GRD-07 | A template may carry an `owner_id`; owner and site scopes of one kind do not overlap | `PRINT_TEMPLATE_SCOPE_OVERLAP`, `PRINT_TEMPLATE_SCOPE_OWNER_NOT_FOUND`, `PRINT_TEMPLATE_TIER_TAKEN` | names the scope | `FR-226` |
| TEP-GRD-08 | A printer belongs to a site, optionally a zone or dock, with a DPI, a default label size and media; a job prints only on a usable printer whose DPI and format match the template | `PRINTER_DPI_INVALID`, `PRINTER_LABEL_SIZE_INVALID`, `PRINTER_ZONE_INVALID`, `PRINTER_DOCK_DOOR_INVALID`, `PRINTER_ADDRESS_NOT_ALLOWED`, `PRINT_PRINTER_DPI_MISMATCH`, `PRINTER_FORMAT_MISMATCH`, `PRINT_PRINTER_NOT_USABLE` | names the printer and the mismatch | `FR-224` |
| TEP-GRD-09 | A routing rule resolves kind × scope to a printer in sequence; no rule → the browser path | `NO_RULE_MATCHED`; `PRINT_ROUTING_RULE_SEQUENCE_DUPLICATE`, `PRINT_ROUTING_RULE_PRINTER_INVALID` | names the kind | `FR-224` |
| TEP-GRD-10 | One open labour timer per user; only its owner pauses, resumes or ends it; it times an open task | `LABOUR_TIMER_ALREADY_OPEN`, `LABOUR_TIMER_NOT_OWN`, `LABOUR_TIMER_NOT_RUNNING`, `LABOUR_TIMER_NOT_PAUSED`, `LABOUR_TIMER_ENDED`, `TASK_NOT_OPEN`, `LABOUR_TASK_ALREADY_TIMED` | names the timer | `FR-227` |
| TEP-GRD-11 | An instrument carries a verification certificate number and validity window; a weighing on an instrument out of verification needs an explicit acknowledgement and is flagged on the receipt; tare ≤ gross; not in the future | `CERTIFICATE_INCOMPLETE`, `CERTIFICATE_WINDOW_INVALID`, `OUT_OF_VERIFICATION_NOT_ACKNOWLEDGED`, `TARE_EXCEEDS_GROSS`, `WEIGHED_AT_IN_FUTURE`, `INSTRUMENT_INACTIVE` | names the instrument and its certificate | `FR-223` |

### 1.4 Transitions that must be unreachable

| ID | Forbidden | What makes it unreachable | Source |
|---|---|---|---|
| TEP-UNR-01 | A receiving or pick screen writing the ledger without a task | the task's completion is the posting path (`TEP-T4-01`) | `FR-212` |
| TEP-UNR-02 | A task duration backfilled after the fact | the timing columns exist from v1 and are stamped by the completing request | `FR-213` |
| TEP-UNR-03 | Two assignment lifecycles (one for pull, one for push) | one `whb_tasks` ladder for both | `FR-214` |
| TEP-UNR-04 | A reprint not flagged, or a print job deleted | the service sets `is_reprint`; void keeps the row | `FR-224` |
| TEP-UNR-05 | An engineered labour standard computed, or incentive pay computed from a warehouse metric | measured durations are reported only | `FR-228` |
| TEP-UNR-06 | Protocol-level control of conveyors, sorters, AS/RS or robots in this codebase | automation integrates through the task-event contract and the movement port only | `FR-229` |

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from | Extra | Source |
|---|---|---|---|---|---|
| TEP-T2-01 | Assign / reassign / claim / cancel / complete with exception | `whb_tasks:{assign,reassign,claim,edit}` | as §1.2 | assignee qualified | `FR-214`, `FR-215` |
| TEP-T2-02 | Exception console | no permission of its own — the union of its sources' view permissions | — | — | `FR-216` |
| TEP-T2-03 | Templates / jobs / printers / routing | `wh_print_templates:{create,edit,publish}` · `wh_print_jobs:{create,void}` · `wh_printers:{create,edit,delete,test_print}` · `wh_print_routing_rules:{create,edit,delete,test_routing}` | — | — | `FR-224` |
| TEP-T2-04 | Labour; weighing instruments | `wh_labour_tasks:record` · `wh_weighing_instruments:{create,edit}` · `wh_weighing_records:{create,acknowledge}` | — | — | `FR-223`, `FR-227` |

## 3. T3 — Time-driven rules

| ID | Rule | Trigger (clock) | Changes | Notified | Job | Source |
|---|---|---|---|---|---|---|
| TEP-T3-01 | An `ASSIGNED` task older than its type's stale threshold moves to `EXCEPTION` | `assigned_at` + threshold (`warehouse.tasks.ageing.cron`) | `EXCEPTION`, `WAREHOUSE_TASK_STALE` | supervisor | `WhbTaskAgeingJob` | `FR-216`, `FR-165` |
| TEP-T3-02 | A task blocked longer than `warehouse.tasks.blocked_alert_minutes` alerts | the same clock | nothing | supervisor | `WhbTaskBlockedAlertService` | `FR-216` |
| TEP-T3-03 | A verification certificate nearing or past its end is flagged | the certificate's validity end | `EXPIRING` / `EXPIRED`; `WAREHOUSE_WEIGHING_CERTIFICATE_EXPIRY` | instrument owner | `WhbWeighingCertificateExpiryJob` | `FR-223`, `FR-165` |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in | Source |
|---|---|---|---|---|
| TEP-T4-01 | A task completes | in one request: `assigned_at` (when null), `started_at`, `completed_at` stamped; `paused_seconds`, `device_id`, `travel_distance_m`, `units_processed` kept; `completion_movement_id`; outbox `task.completed` | `WhbTaskService`, `WhbTaskCompletedEvents` | `FR-212`, `FR-213` |
| TEP-T4-02 | A print job is created | one job-log row: template and version, kind, subject, copies, printer, DPI, format; `is_reprint` / `reprint_of_job_id` set when the subject and kind were printed before | print-job service | `FR-224` |
| TEP-T4-03 | Rendering | the body renders to the template's format and is stored as a platform document (`rendered_document_id`); routed to the printer or downloaded | renderer | `FR-224` |
| TEP-T4-04 | A labour timer ends | who, from–to, paused seconds, units processed, reference and device recorded — the input to VAS-by-the-minute billing and cost-to-serve | `WhLabourTaskService` | `FR-227` |
| TEP-T4-05 | An automation device acts | it posts through the movement port with `actor_type = DEVICE` and reads the published task events | port + outbox | `FR-229` |
| TEP-T4-06 | A task, reconciliation exception, failed inbound message or blocked movement is raised | it appears as one row in the supervisor console with its source's actions | `WhExceptionConsoleService` | `FR-216` |

## 5. T5 — Screen contract (web only, `D-17` item 2)

| ID | Screen | Rule | Source |
|---|---|---|---|
| TEP-T5-01 | WS-059 Tasks | grid with priority, zone, required resource, assignee and the timing columns; Assign / Reassign / Cancel / Complete-with-exception | `FR-212`, `FR-213`, `FR-215` |
| TEP-T5-02 | WS-154 Task Assignment Board | push assignment of a queue; pull shows the next fitting task | `FR-214` |
| TEP-T5-03 | WS-153 Supervisor Exception Console | one grid over exception-coded tasks, reconciliation exceptions, failed inbound messages and blocked movements, each with its actions | `FR-216` |
| TEP-T5-04 | WS-131 / WS-132 / WS-133 / WS-134 | templates per kind, format and owner; the job log with a reprint marker and Void; printers with zone / dock, DPI, label size, media and Test print; routing rules with Test routing | `FR-224`, `FR-225`, `FR-226` |
| TEP-T5-05 | WS-146 Labour Tasks | timers listed with durations; no standard or incentive column | `FR-227`, `FR-228` |
| TEP-T5-06 | WS-129 / WS-130 Weighing | instruments with certificate and validity state; records flag out-of-verification weighings | `FR-223` |

## 6. Amendments

| Date | Change |
|---|---|
| 2026-10-23 | v0 derived for `D-17` item 1 (R30 `CP-FR-007` row 11); mobile FRs deferred by `D-17` item 2 |

## 7. Invariants and scenarios

`FR-436`; scenarios `WH-SC-052`, `WH-SC-055`, `WH-SC-228`, `WH-SC-230`, `WH-SC-249`, `WH-SC-349`, `WH-SC-352`, `WH-SC-361`.

## 8. Code divergences (FRD rule kept)

| ID | File:line | FR | Difference |
|---|---|---|---|
| TEP-DIV-01 | `warehouse-base/…/entity/WhbTaskType.java:79`; `V500010__Create_whb_code_lists_task_types_dispositions_attribute_keys.sql:250` | `FR-228` | a `labour_standard_minutes` column is stored per task type; the FRD forbids claiming an engineered standard before a year of actual data — the column must stay a manually entered reference that nothing computes or pays from |
| TEP-DIV-02 | `warehouse-base/…/service/whbtask/WhbTaskCompletedEvents.java` (`EVENT_TASK_COMPLETED`, `ACTOR_TYPE_USER`) | `FR-229` | the only task event emitted is `task.completed` with a `USER` actor; the published task-event contract an automation vendor integrates against does not exist yet (v3, `P6-04`) |

## 9. Open rows

| ID | Question | Missing decision | Default until decided | Source |
|---|---|---|---|---|
| TEP-OPEN-01 | The published task-event contract: which events (created, assigned, started, completed, exception), their payload and version | `FR-229` names the contract, not its content | `task.completed` only | `FR-229` |

<!-- v0 2026-10-23. Amend with /functional-contract: every change references a row id and adds a §7 row. -->
